#!/usr/bin/env python3
# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE): the worker.
"""tools/evolve.py — EVOLVE: the worker (ALPHA4-PREREG.md §6, brief ALPHA4-J.md item 2).

Launched by `creature/body.py:main` as a SUBPROCESS (the model is `creature/senses/game.py`'s
`start_worker`/`stop_worker` + `tools/game_worker_babyai.py`) when `EVOLVE` is declared. Keeps a SHADOW
organism: a `Mind` that consumes the LIVE tape continuously (the same road `creature/replay.py` walks, but
INCREMENTAL and never closed — it just keeps polling for new rows), checkpointed under
`$ROOT/evolve/checkpoints/<n>/` every 2 h of TAPE time (the moment + the full snapshot; read from the
tape's own "at" fields — PREREG's own law: `creature/tape.py:Tape.publish` is the ONLY place in the
creature that reads the wall clock, and this worker follows the same discipline: it derives "now" from the
LATEST tape row it has consumed, never from `datetime.now()` directly).

The shadow is JUST a `Mind` — it consumes the SAME "proposal" tape rows the live mind does, so it adopts
the SAME sequence of epochs via the SAME `Mind._consume_proposal`/`_maybe_adopt_evolve_proposal` mechanism,
automatically, with no separate bookkeeping: `shadow.genome_text`/`shadow.evolve_epoch` at any moment ARE
the incumbent this worker mutates from (the advisor's blind spot #2 — mutating from a static `--genome`
argument would silently REVERT every earlier adoption on the second and later rounds).

Every `EVOLVE.every_h` hours (read off the shadow's OWN genome — the EVOLVE gene is a RATE/THRESHOLD-style
gene but is not itself in BOUNDS, since mutating "how often to propose" changes nothing about the mutant's
merit and the brief's own table never names it): find the checkpoint nearest (at or before)
`now - judge_h` hours, copy it + the tape slice [checkpoint, now] into fresh scratch roots
(`$ROOT/evolve/run-<n>/incumbent/` and `/mutant/`, #212: a copy, never the live root), replay the INCUMBENT
(the checkpoint's own genome, unmutated) and ONE MUTANT (`creature.genes.mutate_genome_text`, seeded on
(SEED, epoch, proposal_no)) over the slice ONE AT A TIME (never in parallel — each twin is a full
organism), grade both with `tools/verdict_life.py`'s own functions (never re-implemented — Q1 seen calls
`tools/self_exam.py`'s own `load_snapshot`/`genome.questions.ask_glances` verbatim, the same sequence
`self_exam.main()` itself runs), apply the regression bar (`regression_bar`, below), and write
`$ROOT/evolve/PROPOSAL-<n>.json`. `creature/senses/evolve.py`'s sense thread republishes that file onto the
tape as a "proposal" row — this worker NEVER touches the tape directly (a subprocess cannot safely share
the Body's own Tape lock/sequence counter; PUBLISH is the sense thread's job, matching the game worker's
own split).

RETENTION (brief item 2/5, PREREG §6): both twins start from the SAME checkpoint, so Q1-at-start is
IDENTICAL for both — a "retention = Q1(start) − Q1(end)" reading would be a pure re-statement of Q1(end)
alone on a shared-start slice (the advisor's blind-spot #1). Q1-at-start is measured ONCE (on the
checkpoint itself, before either twin runs) and printed on the proposal record; "retention" is marked
"not independently gradable on a shared-start 2 h slice (equals Q1 seen at the end)" rather than a second,
redundant formula being invented.

A pure worker (never a SENSE, per the writer law's own scope — see the module docstring difference from
`creature/senses/evolve.py`): it reads/writes ONLY under `$ROOT/evolve/` (its own scratch), its own shadow
root, and its own fresh `run-<n>/` twins; it NEVER writes under the LIVE `$ROOT/state`, `$ROOT/journal` or
`$ROOT/tape` (checked structurally by `tools/gate_g4.py`'s writer sweep would apply if this file were under
`creature/senses/` — it is not, exactly like `tools/game_worker_babyai.py` is not, since BOTH are
subprocesses, never in-process sense threads).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from creature.genes import BOUNDS, MUTABLE_KEYS, apply_mutation, mutate_genome_text          # noqa: E402
from creature.mind import Mind                                 # noqa: E402
from creature.tape import read_tape                            # noqa: E402
from genome.machinery import GenomeError, parse_genome         # noqa: E402
from tools.verdict_life import act_mark, sentence_mark, surprise_mark   # noqa: E402

# ALPHA4-PREREG.md §6 / brief item 2: the declared margins a numeric reading must clear for the mutant to
# count as an "improvement" — named here so the regression bar's own code and its report agree by
# construction. `frames_filed` is an INTEGER reading (a count of DISTINCT frames the mutant filed beyond
# the incumbent's own count on the SAME paired rows) so its margin is a whole frame, never a fraction.
MARGINS: Dict[str, float] = {
    "q1_seen": 0.01,
    "confirmed_share": 0.02,
    "reward_mean": 0.02,
    "frames_filed": 1,
}
COST_RATIO_BAR = 1.2


# ============================================================================ the proposer's redraw (PREREG-EVOLVE-CAL D8 + A8)
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:56 +0400 — D8: `creature.genes.draw_mutation(seed, epoch, proposal_no)` cannot see the
# incumbent, so on brain-long-2 proposal #3 drew `BIRTH.misfires 3` — the incumbent's own value — and cost ≈ 2 × 3,950 s to refuse a mutant identical to
# its incumbent. The redraw lives HERE (the worker), not in creature/ (organism code stays untouched): when the drawn value equals the number the
# incumbent text already carries, the SAME generator's next gene draw and value draw are taken, and so on until they differ. `draw_stream` repeats
# `draw_mutation`'s body to continue ONE generator; tests/tools/test_evolve_cal_gate.py pins its first element to `draw_mutation`'s over a grid
# that reaches both kinds of gene, so the two cannot drift apart.
def bounds_spec(key: str) -> dict:
    spec = BOUNDS.get(key)
    if spec is None or spec.get("excluded"):
        raise ValueError(f"evolve: {key!r} is not a mutable BOUNDS entry ({(spec or {}).get('reason', 'unknown key')})")
    return spec


def gene_text(text: str, key: str) -> str:
    """The number text the genome currently carries for `key`, read with BOUNDS' own pattern (group 1 = the fixed text up to the number, group 2 =
    everything after it). Exactly one match, or ValueError."""
    ms = list(bounds_spec(key)["pattern"].finditer(text))
    if len(ms) != 1:
        raise ValueError(f"evolve: BOUNDS[{key!r}]'s pattern matched {len(ms)} times in the genome text (need exactly 1)")
    m = ms[0]
    return text[m.end(1):m.start(2)]


def draw_stream(seed: int, epoch: int, proposal_no: int):
    """`creature.genes.draw_mutation`'s draws, CONTINUED: (gene, value) pairs from ONE generator seeded on (seed, epoch, proposal_no)."""
    rng = np.random.default_rng([int(seed), int(epoch), int(proposal_no)])
    while True:
        key = MUTABLE_KEYS[int(rng.integers(0, len(MUTABLE_KEYS)))]
        spec = BOUNDS[key]
        if spec["kind"] == "int":
            value: object = int(rng.integers(int(spec["lo"]), int(spec["hi"]) + 1))
        else:
            value = round(float(rng.uniform(spec["lo"], spec["hi"])), int(spec["decimals"]))
        yield key, value


def _printed_value(key: str, value: object) -> str:
    spec = BOUNDS[key]
    return str(int(round(value))) if spec["kind"] == "int" else f"{float(value):.{int(spec['decimals'])}f}"


def mutate_distinct(text: str, seed: int, epoch: int, proposal_no: int, max_draws: int = 1000):
    """(mutant_text, gene, value, draws): the first draw of the stream whose printed value differs from the incumbent text's own number.
    `draws` is 1 when nothing collided. Bounded: a text that no draw can differ from raises instead of looping."""
    for n, (key, value) in enumerate(draw_stream(seed, epoch, proposal_no), start=1):
        if float(_printed_value(key, value)) != float(gene_text(text, key)):
            return apply_mutation(text, key, value), key, value, n
        if n >= max_draws:
            raise RuntimeError(f"evolve: {max_draws} draws on (seed {seed}, epoch {epoch}, proposal {proposal_no}) all equal the incumbent's own values")
    raise RuntimeError("evolve: the draw stream ended")      # unreachable: the stream is infinite


# ============================================================================ grading (never re-implemented)
def _twin_status(mind: Mind) -> dict:
    """The subset of `creature/body.py:Body._build_status()`'s own fields the 2 h-gradable marks read —
    built from the twin `Mind`'s own attributes, since a twin never runs a `Body` and so never has a real
    STATUS.json (brief blind-spot #3: `sentence_mark`/`act_mark` read a `status` dict, and the twins'
    marks must come from the SAME fields `_build_status` exports, computed the SAME way, or the reading
    would silently mean something else)."""
    tc = mind.think_counters
    return {
        "frames_filed": int(tc.get("frames_filed", 0)), "frames_scored": int(tc.get("frames_scored", 0)),
        "frames_true": int(tc.get("frames_true", 0)), "said": int(tc.get("said", 0)),
        "heard_yes": int(tc.get("heard_yes", 0)), "heard_no": int(tc.get("heard_no", 0)),
        "acts_chosen": dict(getattr(mind, "acts_chosen", {}) or {}),
        "act_mismatches": int(getattr(mind, "act_mismatches", 0)),
        "glances_confirmed": int(getattr(mind, "glances_confirmed", 0)),
        "glances_surprised": int(getattr(mind, "glances_surprised", 0)),
    }


def _read_journal_rows(twin_root: Path) -> List[dict]:
    rows: List[dict] = []
    jdir = Path(twin_root) / "journal"
    if jdir.exists():
        for f in sorted(jdir.glob("*.jsonl")):
            for line in f.read_text().splitlines():
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def q1_seen(root: Path, genome_path: Path) -> Optional[float]:
    """Q1 on the held-out seen-words exam — calls `tools/self_exam.py`'s OWN functions verbatim (the same
    sequence `self_exam.main()` itself runs: `load_snapshot` -> `world.holdout_canvas` ->
    `run_g1.glance_held`/`feats_only` -> `genome.questions.ask_glances`), never a re-implementation of the
    grade (brief's own rule, item 2/5: "call tools/verdict_life.py's functions, never re-implement a
    mark" — Q1 itself is not in verdict_life.py; this is the SAME discipline applied to self_exam.py, the
    one file that actually owns the Q1 computation)."""
    from tools import self_exam
    from genome import world, run_g1
    from genome.questions import ask_glances
    try:
        g, org, ledgers, _L = self_exam.load_snapshot(Path(root), Path(genome_path))
    except (FileNotFoundError, OSError, ValueError) as e:
        return None
    things = list(world.THINGS_11)
    arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], 10, np.random.default_rng(2))
    held_g = run_g1.glance_held(held, g, "surprise")
    feats = run_g1.feats_only(held_g)
    never = {world.THING_NEVER: feats[world.THING_NEVER]}
    words_seen = sorted({w for s in ledgers["words"].values() for w in s})
    seen_things = [t for t in things if t in words_seen]
    fallback = len(seen_things) < 2
    ask = ask_glances(org, ledgers, things if fallback else seen_things, feats, never, g.ear_blank_zero)
    acc = (ask.get("Q1") or {}).get("acc")
    return float(acc) if isinstance(acc, (int, float)) else None


def machine_snapshot() -> dict:
    """The box's own state at this instant: the 1/5/15-minute load average and the CPU / memory pressure (PSI `some avg10`) — recorded at each
    twin's start and end (PREREG-EVOLVE-CAL A3: contention inflates a CPU-second as it inflates wall time, #242 addendum)."""
    load: Optional[List[float]]
    try:
        load = [float(x) for x in Path("/proc/loadavg").read_text().split()[:3]]
    except (OSError, ValueError):
        load = None
    psi: Dict[str, Optional[float]] = {}
    for name in ("cpu", "memory"):
        try:
            for line in Path(f"/proc/pressure/{name}").read_text().splitlines():
                kind, *kv = line.split()
                psi[f"{name}_{kind}_avg10"] = float(dict(x.split("=") for x in kv)["avg10"])
        except (OSError, ValueError, KeyError):
            psi.setdefault(f"{name}_some_avg10", None)
    return {"load": load, "psi": psi}


def _machine_pair(m0: dict, m1: dict) -> dict:
    return {"load0": m0["load"], "load1": m1["load"], "psi0": m0["psi"], "psi1": m1["psi"]}


def grade_twin(mind: Mind, twin_root: Path, genome_path: Path, tape_slice: List[dict], wall_s: float,
               cpu_s: Optional[float] = None, machine: Optional[dict] = None) -> dict:
    """One twin's paired readings — every mark computed by `tools/verdict_life.py`'s own functions over
    THIS twin's own journal/tape/status, never re-implemented. `q1_seen` is the ONE reading measured at
    the END of the slice only (see the module docstring's RETENTION note: the start reading is identical
    for both twins by construction, so it is measured once by the caller, not per twin).
    edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:59 +0400 (corrected from a typed 21:00 by `date`) — PREREG-EVOLVE-CAL §1 D6 + A3: `cpu_s` is the twin's PROCESS CPU-seconds
    (`time.process_time()` around the twin, not wall; None when the caller did not measure it — a missing reading, never a zero) and `machine` the
    load / pressure at the twin's start and end; both ride on the reading beside `wall_s`."""
    journal_rows = _read_journal_rows(twin_root)
    status = _twin_status(mind)
    declared = mind.genome.declared
    # edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:40 +0400 — PREREG-EVOLVE-CAL §1 D3 (the E3 call-site shift): the call read
    # `surprise_mark(tape_slice, journal_rows, status, declared)` against the signature `surprise_mark(journal, status, surprise_declared, ...)`,
    # every argument one place off, so `confirmed_share` read «not gradable» on 13 of 13 rounds (the twin journals carry `confirmed` on every
    # moment row). Pinned by tests/tools/test_evolve_cal_d3.py (RED on the shifted line, GREEN here).
    sm = surprise_mark(journal_rows, status, "SURPRISE" in declared)
    sen = sentence_mark(tape_slice, status, "SENTENCE" in declared)
    am = (act_mark(tape_slice, journal_rows, status) if "ACT" in declared
          else {"graded": False, "pass": None, "reason": "not gradable: ACT not declared"})
    out = {
        "q1_seen": q1_seen(twin_root, genome_path),
        "confirmed_share": sm.get("overall_share"), "confirmed_graded": sm.get("graded"),
        "reward_mean": am.get("reward_mean"), "act_pass": am.get("pass"), "act_graded": am.get("graded"),
        "frames_filed": sen.get("frames_filed"), "sentence_pass": sen.get("pass"), "sentence_graded": sen.get("graded"),
        "wall_s": round(wall_s, 3), "cpu_s": (round(cpu_s, 3) if cpu_s is not None else None),
        "tape_rows": len(tape_slice), "journal_rows": len(journal_rows),
        "detail": {"surprise": sm, "sentence": sen, "act": am},
    }
    if machine:
        out.update(machine)
    return out


def regression_bar(incumbent: dict, mutant: dict) -> Tuple[str, str]:
    """ALPHA4-PREREG.md §6: "the mutant passes every mark the incumbent passed AND improves at least one
    by its declared margin AND its cost <= 1.2x." Two kinds of "mark" are read here: (a) a GRADED pass/fail
    (act_pass, sentence_pass) — never allowed to regress from True to anything else; (b) a NUMERIC reading
    (MARGINS' own keys) — never allowed to go DOWN, and at least one must clear its margin. A reading
    missing (None) on either side is neither a regression nor an improvement — it is simply not compared
    (the mark's own "not gradable" already says why, carried in the proposal's "detail")."""
    regressions: List[str] = []
    for key in ("act_pass", "sentence_pass"):
        iv, mv = incumbent.get(key), mutant.get(key)
        if iv is True and mv is not True:
            regressions.append(f"{key}: incumbent PASS, mutant {mv!r}")
    improved: List[str] = []
    for key, margin in MARGINS.items():
        iv, mv = incumbent.get(key), mutant.get(key)
        if iv is None or mv is None:
            continue
        if mv < iv:
            regressions.append(f"{key}: incumbent {iv}, mutant {mv} (regressed)")
        elif mv >= iv + margin:
            improved.append(f"{key} {iv}->{mv} (+{margin})")
    iw, mw = incumbent.get("wall_s"), mutant.get("wall_s")
    cost_ratio = (mw / iw) if (iw is not None and iw > 0 and mw is not None) else None
    if cost_ratio is not None and cost_ratio > COST_RATIO_BAR:
        regressions.append(f"cost: {cost_ratio:.3f}x > {COST_RATIO_BAR}x ({mw:.1f}s vs {iw:.1f}s)")
    if regressions:
        return "REFUSED", "; ".join(regressions)
    if not improved:
        return "REFUSED", "no reading cleared its declared margin (no regressions either — a null mutant)"
    return "PASS", f"improved: {', '.join(improved)}; no regressions; cost_ratio={cost_ratio}"


# ============================================================================ the shadow
def _link_tape_payload(work_root: Path, source_root: Path, declared_tape_path: Optional[str]) -> None:
    """Mirrors `creature/replay.py:run_replay`'s own symlink exactly: a `Mind` resolves an eye/ear/body
    payload path under ITS OWN `run_root` (`_resolve_tape_dir(self.run_root, ...) / row["payload"]`), so a
    shadow or twin fed rows from a DIFFERENT root's tape needs that root's payload directory symlinked in —
    never copied (the payload files can be large and are never written by the shadow/twin)."""
    import os
    from creature.tape import _resolve_tape_dir
    work_tape = _resolve_tape_dir(Path(work_root), declared_tape_path)
    work_tape.mkdir(parents=True, exist_ok=True)
    link = work_tape / "payload"
    if link.exists() or link.is_symlink():
        return
    src = _resolve_tape_dir(Path(source_root), declared_tape_path) / "payload"
    if src.exists():
        os.symlink(src.resolve(), link)


def build_or_resume_shadow(shadow_root: Path, birth_genome_path: Path, live_root: Path) -> Mind:
    """The shadow `Mind` — `Mind.resume` if a prior shadow snapshot exists (epoch-aware: it will pick up
    ANY `GENOME.v<n>.genome` already written under `shadow_root` by this shadow's own earlier adoptions,
    exactly like the live mind's own restart does), else a fresh `Mind` from the birth genome. Either way,
    the shadow's own tape/payload directory is symlinked to the LIVE root's (`_link_tape_payload`) BEFORE
    the Mind is built, since `Mind.__init__`/`resume` never read the tape themselves but `advance_shadow`
    immediately will."""
    declared_tape_path = parse_genome(Path(birth_genome_path).read_text()).declared.get("TAPE", {}).get("path")
    shadow_root = Path(shadow_root)
    shadow_root.mkdir(parents=True, exist_ok=True)
    _link_tape_payload(shadow_root, live_root, declared_tape_path)
    if (shadow_root / "state" / "organism.npz").exists():
        mind, _last_seq = Mind.resume(birth_genome_path, shadow_root)
        return mind
    return Mind(birth_genome_path, shadow_root)


def advance_shadow(mind: Mind, live_root: Path, up_to_seq: Optional[int] = None) -> int:
    """Feed the shadow every LIVE tape row past its own `last_seq` (and, when given, at or before
    `up_to_seq`) — the same backlog-replay shape `creature/body.py:Body.start()` uses. Returns the count
    of rows consumed this call. `up_to_seq` is used by the negative control (brief item 4) to build "a
    shadow state at T−2h" without also consuming the 2 h window the judging round is about to grade."""
    n = 0
    for row in read_tape(Path(live_root)):
        seq = int(row["seq"])
        if seq > mind.last_seq and (up_to_seq is None or seq <= up_to_seq):
            mind.consume(row)
            n += 1
    if n:
        mind.snapshot()
    return n


def _iso_to_epoch_s(at: str) -> float:
    from datetime import datetime
    return datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp()


def hours_between(a_iso: str, b_iso: str) -> float:
    return (_iso_to_epoch_s(b_iso) - _iso_to_epoch_s(a_iso)) / 3600.0


# ============================================================================ checkpoints (#212: copies)
def checkpoint_shadow(mind: Mind, checkpoints_dir: Path, at_iso: str) -> Path:
    """Copy the shadow's CURRENT state + its CURRENT genome text into a new, numbered checkpoint directory
    under `checkpoints_dir` — never a reference to the shadow's own live root (#212: a measurement/judging
    round works from a COPY). Returns the checkpoint's own directory."""
    checkpoints_dir = Path(checkpoints_dir)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(int(p.name) for p in checkpoints_dir.iterdir() if p.is_dir() and p.name.isdigit())
    n = (existing[-1] + 1) if existing else 1
    cp_dir = checkpoints_dir / str(n)
    mind.snapshot()
    shutil.copytree(mind.run_root / "state", cp_dir / "state")
    (cp_dir / "GENOME.genome").write_text(mind.genome_text)
    (cp_dir / "META.json").write_text(json.dumps({
        "n": n, "at": at_iso, "last_seq": mind.last_seq, "moment": mind.org.t, "evolve_epoch": mind.evolve_epoch,
    }))
    return cp_dir


def latest_checkpoint(checkpoints_dir: Path) -> Optional[dict]:
    checkpoints_dir = Path(checkpoints_dir)
    if not checkpoints_dir.exists():
        return None
    dirs = sorted((p for p in checkpoints_dir.iterdir() if p.is_dir() and p.name.isdigit()), key=lambda p: int(p.name))
    if not dirs:
        return None
    meta = json.loads((dirs[-1] / "META.json").read_text())
    meta["dir"] = dirs[-1]
    return meta


def checkpoint_near(checkpoints_dir: Path, target_iso: str) -> Optional[dict]:
    """The checkpoint whose own "at" is the LATEST one at or before `target_iso` — the "shadow state at
    T-2h" brief item 2 names. None if every checkpoint is AFTER `target_iso` (too young a shadow) or none
    exist yet."""
    checkpoints_dir = Path(checkpoints_dir)
    if not checkpoints_dir.exists():
        return None
    best = None
    for p in checkpoints_dir.iterdir():
        if not (p.is_dir() and p.name.isdigit()):
            continue
        meta_path = p / "META.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        if meta["at"] <= target_iso and (best is None or meta["at"] > best["at"]):
            meta["dir"] = p
            best = meta
    return best


# ============================================================================ twins (#212: fresh scratch roots)
def build_twin(checkpoint: dict, genome_text: str, scratch_root: Path, live_root: Path) -> Mind:
    """A fresh `Mind` resumed from `checkpoint`'s own copied state, under `genome_text` (the incumbent's
    own text for the incumbent twin, or a mutant text for the mutant twin) — a COPY of the checkpoint's
    state, never the checkpoint directory itself (a second twin built from the SAME checkpoint must not
    see the first twin's writes). `live_root`'s tape/payload is symlinked in (`_link_tape_payload`) so the
    twin can decode the slice's own eye rows — the checkpoint carries no payloads of its own."""
    scratch_root = Path(scratch_root)
    scratch_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(checkpoint["dir"] / "state", scratch_root / "state")
    genome_path = scratch_root / "GENOME.genome"
    genome_path.write_text(genome_text)
    declared_tape_path = parse_genome(genome_text).declared.get("TAPE", {}).get("path")
    _link_tape_payload(scratch_root, live_root, declared_tape_path)
    mind, _last_seq = Mind.resume(genome_path, scratch_root)
    return mind


def tape_slice(live_root: Path, from_seq: int, to_seq: int) -> List[dict]:
    """Every LIVE tape row with `from_seq < seq <= to_seq`, in seq order — the judging round's own input
    slice (never mutated, never written back)."""
    return [r for r in read_tape(Path(live_root)) if from_seq < int(r["seq"]) <= to_seq]


# ============================================================================ one judging round
def run_judging_round(live_root: Path, shadow: Mind, checkpoints_dir: Path, now_iso: str, judge_h: float,
                       seed: int, proposal_no: int, runs_dir: Path,
                       forced_mutation: Optional[Tuple[str, object]] = None,
                       tape_head_seq: Optional[int] = None, bands: Optional[dict] = None) -> dict:
    """ALPHA4-PREREG.md §6: one round. `forced_mutation` (gene_key, value) bypasses the rng draw — used
    ONLY by the negative control (brief item 4), which must plant a SPECIFIC gene/value, never a random
    one. `tape_head_seq`: the LIVE tape's own latest seq at the moment `now_iso` was read (the caller
    already has it — `main()`'s own `rows[-1]["seq"]` — a second `read_tape` scan here would be wasted
    work); defaults to `shadow.last_seq` when not given (the advance-and-judge CLI always advances the
    shadow to the tape's own end first, so the two coincide there by construction). The GAP between this
    and `shadow.last_seq` — `shadow_lag_rows` on the returned dict — is the box-under-load failure mode
    #236 names: if the shadow has fallen behind the live tape (the box loaded with five builders' lives
    and readers), the slice this round grades is silently SHORTER than `judge_h` while the record still
    says 2 h. Never refused on — recorded, so a reader can judge whether to trust a given round's numbers.
    Returns the proposal dict (also written to `$ROOT/evolve/PROPOSAL-<proposal_no>.json` by the caller).

    edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:00 +0400 (corrected from a typed 21:01 by `date`) — PREREG-EVOLVE-CAL §1: `bands=None` is the LEGACY round (the two-verdict
    `regression_bar`, byte for byte what it was, now with each twin's process CPU-seconds and the box's load / pressure on the reading). With a
    BANDS dict (tools/evolve_bands.py) the round adds `gate` (REGRESSED / IMPROVED / NO EVIDENCE from the twins' paired readings, incumbent first,
    Δ = mutant − incumbent) and `not_gradable` (reward_mean / act_pass / sentence_pass, D4 / D5), and its `verdict` is ALWAYS REFUSED: an IMPROVED
    mutant is adopted only by `finalize_calibrated_round` after it is IMPROVED again on the next disjoint slice. An unforced draw goes through
    `mutate_distinct` (D8): the proposal records `draws` (1 = nothing collided with the incumbent's own value)."""
    from datetime import datetime, timedelta
    target_iso = (datetime.fromisoformat(now_iso.replace("Z", "+00:00")) - timedelta(hours=judge_h)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    head_seq = int(tape_head_seq) if tape_head_seq is not None else shadow.last_seq
    shadow_lag_rows = head_seq - shadow.last_seq
    cp = checkpoint_near(checkpoints_dir, target_iso)
    if cp is None:
        return {"no": proposal_no, "epoch": shadow.evolve_epoch, "verdict": "REFUSED",
                "reason": f"not gradable: no shadow checkpoint at or before {target_iso} yet",
                "shadow_lag_rows": shadow_lag_rows}
    to_seq = shadow.last_seq
    slice_rows = tape_slice(live_root, cp["last_seq"], to_seq)
    incumbent_text = cp["dir"].joinpath("GENOME.genome").read_text()
    draws: Optional[int] = None
    if forced_mutation is not None:
        gene_key, value = forced_mutation
        mutant_text = apply_mutation(incumbent_text, gene_key, value)
    else:
        mutant_text, gene_key, value, draws = mutate_distinct(incumbent_text, seed, shadow.evolve_epoch + 1, proposal_no)

    q1_start = q1_seen(cp["dir"], cp["dir"] / "GENOME.genome")   # cp["dir"] has its own state/ subdir (checkpoint_shadow's own layout)

    runs_dir = Path(runs_dir)
    inc_root = runs_dir / f"round-{proposal_no}" / "incumbent"
    mut_root = runs_dir / f"round-{proposal_no}" / "mutant"
    m0 = machine_snapshot()
    t0, c0 = time.perf_counter(), time.process_time()
    inc_mind = build_twin(cp, incumbent_text, inc_root, live_root)
    for row in slice_rows:
        inc_mind.consume(row)
    inc_mind.close()
    inc_wall, inc_cpu = time.perf_counter() - t0, time.process_time() - c0
    incumbent_readings = grade_twin(inc_mind, inc_root, inc_root / "GENOME.genome", slice_rows, inc_wall,
                                    cpu_s=inc_cpu, machine=_machine_pair(m0, machine_snapshot()))
    del inc_mind    # ONE AT A TIME (brief item 2): the incumbent twin's memory is released before the mutant twin is built

    m0 = machine_snapshot()
    t1, c1 = time.perf_counter(), time.process_time()
    mut_mind = build_twin(cp, mutant_text, mut_root, live_root)
    for row in slice_rows:
        mut_mind.consume(row)
    mut_mind.close()
    mut_wall, mut_cpu = time.perf_counter() - t1, time.process_time() - c1
    mutant_readings = grade_twin(mut_mind, mut_root, mut_root / "GENOME.genome", slice_rows, mut_wall,
                                 cpu_s=mut_cpu, machine=_machine_pair(m0, machine_snapshot()))
    del mut_mind

    extra: Dict[str, object] = {}
    if bands is None:
        verdict, reason = regression_bar(incumbent_readings, mutant_readings)
    else:
        from tools import evolve_bands
        gate = evolve_bands.calibrated_verdict(incumbent_readings, mutant_readings, bands)
        verdict, reason = "REFUSED", gate["reason"]          # a calibrated round never PASSes by itself (finalize_calibrated_round)
        extra = {"gate": gate, "not_gradable": evolve_bands.not_gradable_block(incumbent_readings, mutant_readings),
                 "bands_scope": {k: bands.get(k) for k in ("slice", "n", "df", "alpha_side", "scope")}}
    return {
        "no": proposal_no, "epoch": shadow.evolve_epoch, "gene": gene_key, "value": value, "draws": draws,
        "mutant_genome_text": mutant_text, "checkpoint": cp["n"], "checkpoint_at": cp["at"],
        "slice_from_seq": cp["last_seq"], "slice_to_seq": to_seq, "slice_rows": len(slice_rows),
        "shadow_lag_rows": shadow_lag_rows,
        "q1_seen_start": q1_start,
        "incumbent": incumbent_readings, "mutant": mutant_readings,
        "verdict": verdict, "reason": reason, **extra,
        "retention_note": "not independently gradable on a shared-start slice (equals q1_seen at the end); q1_seen_start is printed once, identical for both twins by construction",
    }


def write_proposal(evolve_dir: Path, proposal: dict) -> Path:
    evolve_dir = Path(evolve_dir)
    evolve_dir.mkdir(parents=True, exist_ok=True)
    path = evolve_dir / f"PROPOSAL-{proposal['no']}.json"
    tmp = evolve_dir / f"PROPOSAL-{proposal['no']}.json.tmp"
    tmp.write_text(json.dumps(proposal, default=str))
    tmp.replace(path)
    return path


def _next_proposal_no(evolve_dir: Path) -> int:
    evolve_dir = Path(evolve_dir)
    if not evolve_dir.exists():
        return 1
    ns = [int(p.stem.split("-")[1]) for p in evolve_dir.glob("PROPOSAL-*.json") if p.stem.split("-")[1].isdigit()]
    return (max(ns) + 1) if ns else 1


# ============================================================================ the confirmation round (PREREG-EVOLVE-CAL §1, D7)
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:00 +0400 — an IMPROVED mutant is ADOPTED only after it is IMPROVED again on the NEXT
# disjoint 2 h slice (its own twins, the same bands). The first IMPROVED round writes `evolve/PENDING-CONFIRM.json` and a proposal whose `verdict`
# stays REFUSED (the mind adopts only `verdict == "PASS"`); the next round re-judges THE SAME mutation (forced) and `tools/evolve_bands.
# confirm_decision` decides; PASS is written only there. A pending from an older epoch (an adoption happened since) is dropped with a note.
PENDING_NAME = "PENDING-CONFIRM.json"


def load_pending(evolve_dir: Path) -> Optional[dict]:
    p = Path(evolve_dir) / PENDING_NAME
    return json.loads(p.read_text()) if p.exists() else None


def _save_pending(evolve_dir: Path, record: dict) -> None:
    evolve_dir = Path(evolve_dir)
    evolve_dir.mkdir(parents=True, exist_ok=True)
    tmp = evolve_dir / (PENDING_NAME + ".tmp")
    tmp.write_text(json.dumps(record, sort_keys=True))
    tmp.replace(evolve_dir / PENDING_NAME)


def _clear_pending(evolve_dir: Path) -> None:
    p = Path(evolve_dir) / PENDING_NAME
    if p.exists():
        p.unlink()


def pending_forced_mutation(evolve_dir: Path, shadow_epoch: int) -> Tuple[Optional[Tuple[str, object]], Optional[str]]:
    """((gene, value), None) when a confirmation is pending for THIS epoch; (None, a note) when a pending was dropped as stale; (None, None) otherwise."""
    p = load_pending(evolve_dir)
    if p is None:
        return None, None
    if int(p["epoch"]) != int(shadow_epoch):
        _clear_pending(evolve_dir)
        return None, f"a pending confirmation of {p['proposal'].get('gene')}={p['proposal'].get('value')} (proposal {p['proposal'].get('no')}) was dropped: " \
                     f"it was drawn at epoch {p['epoch']} and the shadow is at epoch {shadow_epoch} (an adoption happened since)"
    return (p["proposal"]["gene"], p["proposal"]["value"]), None


def finalize_calibrated_round(proposal: dict, evolve_dir: Path, shadow_epoch: int) -> dict:
    """Apply the confirmation rule to a CALIBRATED proposal (one carrying `gate`); anything else is returned untouched."""
    if proposal.get("gate") is None:
        return proposal
    from tools import evolve_bands
    gate_verdict = proposal["gate"]["verdict"]
    pending = load_pending(evolve_dir)
    slim = {k: proposal.get(k) for k in ("no", "gene", "value", "slice_from_seq", "slice_to_seq")}
    slim["gate"] = {"verdict": gate_verdict, "reason": proposal["gate"].get("reason")}
    if pending is not None:
        d = evolve_bands.confirm_decision(pending["proposal"], proposal)
        proposal["confirmation"] = {"of": pending["proposal"].get("no"), **d}
        if d["keep_pending"]:
            proposal["verdict"], proposal["state"] = "REFUSED", f"not a confirmation round ({d['reason']}); the pending of proposal {pending['proposal'].get('no')} is kept"
        else:
            _clear_pending(evolve_dir)
            proposal["verdict"] = "PASS" if d["adopt"] else "REFUSED"
            proposal["state"] = ("ADOPTED: " if d["adopt"] else "NOT ADOPTED: ") + d["reason"]
        return proposal
    if gate_verdict == "IMPROVED":
        _save_pending(evolve_dir, {"epoch": int(shadow_epoch), "proposal": slim})
        proposal["verdict"] = "REFUSED"
        proposal["state"] = "IMPROVED — awaiting confirmation on the next disjoint 2 h slice (its own twins, the same bands)"
    else:
        proposal["verdict"] = "REFUSED"
        proposal["state"] = gate_verdict
    return proposal


# ============================================================================ the negative control (brief item 4)
def run_negative_control(root: Path, genome_path: Path, out_dir: Path, judge_h: float = 2.0) -> Dict[str, dict]:
    """ALPHA4-PREREG.md §6 / brief item 4: "must exist before the life". `root` is a COPY of a closed
    life's tape (#212 — never the live root or a life under /data/dev/genome-lives/*; the caller copies it
    with `cp -r` first). Builds "a shadow state at T−2h" by replaying from birth up to the seq at
    (last tape timestamp − 2 h) (`advance_shadow(..., up_to_seq=...)`), checkpoints there, then runs TWO
    judging rounds over the real last-2h slice with FORCED (never drawn) mutations: (a) the PLANTED BAD
    mutant, `BIRTH.theta_n` -> 0.5 (deliberately outside BOUNDS' own [0.85, 0.99] band); (b) a NULL mutant,
    a value moved by ONE STEP inside the noise (`DELTA.lr` 0.05 -> 0.051 by construction, never drawn by
    the rng — the brief's own words: "constructed directly", advisor's point 7). Both readings are printed
    on the returned dict regardless of verdict — a PASS here is a RESULT about the bar, reported, never
    silently loosened (advisor's point 7)."""
    root, genome_path, out_dir = Path(root), Path(genome_path), Path(out_dir)
    rows = list(read_tape(root))
    if not rows:
        raise RuntimeError(f"negative control: no tape rows under {root}")
    last_at = rows[-1]["at"]
    from datetime import datetime, timedelta
    target_iso = (datetime.fromisoformat(last_at.replace("Z", "+00:00")) - timedelta(hours=judge_h)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    checkpoint_seq = max((int(r["seq"]) for r in rows if r["at"] <= target_iso), default=0)

    shadow_root = out_dir / "shadow"
    shadow = build_or_resume_shadow(shadow_root, genome_path, root)
    n1 = advance_shadow(shadow, root, up_to_seq=checkpoint_seq)
    print(f"[evolve/negctl] shadow consumed {n1} rows up to seq {checkpoint_seq} (T-{judge_h}h checkpoint)")
    checkpoints_dir = out_dir / "checkpoints"
    checkpoint_shadow(shadow, checkpoints_dir, target_iso)
    n2 = advance_shadow(shadow, root)   # catch the shadow up to the tape's true end (needed for `to_seq` below)
    print(f"[evolve/negctl] shadow consumed {n2} more rows to the tape's end (seq {shadow.last_seq})")

    results: Dict[str, dict] = {}
    for label, forced in (("planted_bad", ("BIRTH.theta_n", 0.5)), ("null", ("DELTA.lr", 0.051))):
        proposal = run_judging_round(root, shadow, checkpoints_dir, last_at, judge_h, int(shadow.genome.seed),
                                      proposal_no=(901 if label == "planted_bad" else 902),
                                      runs_dir=out_dir / "runs", forced_mutation=forced,
                                      tape_head_seq=int(rows[-1]["seq"]))
        results[label] = proposal
        print(f"[evolve/negctl] {label} ({forced[0]}={forced[1]}): verdict={proposal.get('verdict')} reason={proposal.get('reason')}")
        print(f"[evolve/negctl] {label} incumbent q1_seen={proposal.get('incumbent', {}).get('q1_seen')} "
              f"mutant q1_seen={proposal.get('mutant', {}).get('q1_seen')} q1_seen_start={proposal.get('q1_seen_start')}")
        (out_dir / f"NEGATIVE-CONTROL-{label}.json").write_text(json.dumps(proposal, default=str))
    return results


# ============================================================================ CLI
def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="the LIVE life's root (read-only: tape, never written)")
    ap.add_argument("--genome", required=True, help="the BIRTH genome (used only when no shadow snapshot exists yet)")
    ap.add_argument("--stop-file", default=None)
    ap.add_argument("--poll-period", type=float, default=30.0)
    ap.add_argument("--negative-control", action="store_true", help="brief item 4: run the planted-bad + null mutant checks and exit")
    ap.add_argument("--out", default=None, help="--negative-control's own scratch dir")
    # edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:01 +0400 — PREREG-EVOLVE-CAL: `--bands` switches the worker to the CALIBRATED gate; absent (the default),
    # the worker is the legacy one. Nothing enters a life until a later law adopts the calibrated gate (the seat's signature line on the law).
    ap.add_argument("--bands", default=None, help="a BANDS.json (tools/evolve_bands.py) — the calibrated gate; default: the legacy two-verdict bar")
    a = ap.parse_args(argv)

    if a.negative_control:
        out_dir = Path(a.out) if a.out else (Path(a.root) / "_negative_control")
        results = run_negative_control(Path(a.root), Path(a.genome), out_dir)
        bad_ok = results["planted_bad"]["verdict"] == "REFUSED"
        null_ok = results["null"]["verdict"] == "REFUSED"
        print(f"[evolve/negctl] planted_bad REFUSED: {bad_ok}; null REFUSED: {null_ok}")
        return 0 if (bad_ok and null_ok) else 1
    root = Path(a.root)
    genome_path = Path(a.genome)
    evolve_dir = root / "evolve"
    shadow_root = evolve_dir / "shadow"
    checkpoints_dir = evolve_dir / "checkpoints"
    runs_dir = evolve_dir
    stop_file = Path(a.stop_file) if a.stop_file else (evolve_dir / "STOP")
    bands = None
    if a.bands:
        from tools import evolve_bands
        bands = evolve_bands.load_bands(a.bands)             # a malformed file stops the worker here, by name, before any shadow is built

    shadow = build_or_resume_shadow(shadow_root, genome_path, root)
    declared = shadow.genome.declared.get("EVOLVE")
    if declared is None:
        print("[evolve] EVOLVE not declared on this genome -- the worker has nothing to do, exiting")
        return 0
    every_h, judge_h = float(declared["every_h"]), float(declared["judge_h"])
    seed = int(shadow.genome.seed)

    last_cp = latest_checkpoint(checkpoints_dir)
    last_checkpoint_at = last_cp["at"] if last_cp else None
    proposal_no = _next_proposal_no(evolve_dir)
    last_proposal_at: Optional[str] = None

    print(f"[evolve] worker started: every_h={every_h} judge_h={judge_h} seed={seed} shadow_epoch={shadow.evolve_epoch}")
    if bands is not None:
        print(f"[evolve] calibrated gate: bands from {a.bands} (slice {bands.get('slice')}, n {bands.get('n')}, alpha_side {bands.get('alpha_side')}, "
              f"scope {bands.get('scope')}); an IMPROVED mutant waits for its confirmation round on the next disjoint slice")
    # steady-state cost note (report-only, not fixed here): this loop reads the WHOLE live tape twice per
    # poll (once inside advance_shadow, once here for now_iso/tape_head_seq) -- at ~100K rows that is
    # roughly a couple of seconds of pure parsing against a `poll_period` of tens of seconds, acceptable
    # at this life's scale (mirrors genome/predict.py's own "acceptable at this life's scale" note for a
    # different O(N) read); an incremental tail-read would remove it if a much longer life ever needs to.
    while not stop_file.exists():
        advance_shadow(shadow, root)
        rows = list(read_tape(root))
        now_iso = rows[-1]["at"] if rows else None
        if now_iso is not None:
            if last_checkpoint_at is None or hours_between(last_checkpoint_at, now_iso) >= 2.0:
                cp = checkpoint_shadow(shadow, checkpoints_dir, now_iso)
                last_checkpoint_at = now_iso
                print(f"[evolve] checkpoint {cp.name} at {now_iso} (epoch {shadow.evolve_epoch})")
            if last_proposal_at is None or hours_between(last_proposal_at, now_iso) >= every_h:
                forced, note = pending_forced_mutation(evolve_dir, shadow.evolve_epoch) if bands is not None else (None, None)
                proposal = run_judging_round(root, shadow, checkpoints_dir, now_iso, judge_h, seed, proposal_no, runs_dir,
                                              forced_mutation=forced, tape_head_seq=int(rows[-1]["seq"]), bands=bands)
                if note:
                    proposal["pending_note"] = note
                if bands is not None:
                    proposal = finalize_calibrated_round(proposal, evolve_dir, shadow.evolve_epoch)
                write_proposal(evolve_dir, proposal)
                print(f"[evolve] proposal {proposal_no}: {proposal.get('verdict')} — {proposal.get('reason')}")
                proposal_no += 1
                last_proposal_at = now_iso
        stop_file_parent_exists = stop_file.parent.exists()
        if not stop_file_parent_exists:
            stop_file.parent.mkdir(parents=True, exist_ok=True)
        time.sleep(a.poll_period)
    shadow.close()
    print("[evolve] worker stopped (stop file present)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
