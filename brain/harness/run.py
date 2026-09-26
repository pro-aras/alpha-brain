"""run.py — THE ONE RUNNER (B1-PREREG.md §8; docs/brain/b1/SEAT-DECISIONS.md R27, R28).

edit: Claude (Fable 5.1), 2026-09-24 18:31 +0400 — the seat, alone (Ahmad's 17:42 word).

`python -m brain.harness.run --seed <s> --arms <names> --out <run-dir> [--tape-dir …] [--cache-dir …]` under
the venv. The runner never renders and never writes the tape: it READS `tape.jsonl` (every row verified
against its own sha, the file against `tape.sha256`), `truth.jsonl` (the harness may; arms never), `mlc.jsonl`
and the glance cache, and drives every named arm through `brain.protocol.HarnessContract` in tape order —
the identical dispatch `brain/harness/identity_worker.py` uses for the §3.1 identity test, extended with the
sittings, the U4a/U4b collections and the MLC interleave. Per arm it writes the record R27 names:

  answers.jsonl · state_sha.jsonl · cost.jsonl · feedback.jsonl · why.jsonl · rules.jsonl · sittings.json ·
  summary.json (canonical) · run-facts.json (clocks, pid, load, RSS, interpreter — never hashed) · snapshot/

The graders (`brain/harness/graders.py`) are pure functions over (tape, truth, these files); nothing is graded
here beyond the inline `correct` flag every answer carries (the U4a road needs it, and a reader needs it
without recomputation — the graders recompute regardless).

The registry (`spec_for`) names every arm and twin of §4 that exists in the tree today; a name it does not
know is REFUSED with the list of the names it knows. A twin made FROM a base arm is written `TWIN:BASE`
(`SHUFFLED-NAME:A1`, `SHUFFLED-RELATION:A5`, `FORCED:A0`).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import resource
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from brain.protocol import (  # noqa: E402
    Answer, AnswerKind, HarnessContract, ProtocolError, canonical_json, has_rule, has_why, make_arm, right_matches, verify_row,
)
from brain.world import mlc as mlc_mod  # noqa: E402

OUT_ROOT = Path("/data/dev/brain-runs/b1")
_OVERRIDES: Dict[str, Dict[str, Any]] = {}
REFUSE = "REFUSE"
STATE_EVERY_ROWS = 500
U3_FAMILY_CUES: Dict[str, List[str]] = {
    "AFTER": ["AFTER"], "BEFORE": ["BEFORE"], "BETWEEN": ["BETWEEN"], "TWO_AFTER": ["TWO_AFTER"],
    "OTHER_CASE": ["OTHER_CASE"], "CHAIN": ["AFTER", "OTHER_CASE"], "MIRROR": ["MIRROR"], "LOOP": ["LOOP"], "VOWEL": ["VOWEL"],
}


class RunError(Exception):
    pass


# ================================================================================================ the registry
@dataclass
class ArmSpec:
    name: str
    module: str = ""
    cls: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    mlc: bool = False                      # R28: sees the MLC side rows
    transform: Optional[str] = None        # "shuffled_name" | "shuffled_relation"
    wrapper: Optional[str] = None          # "forced"
    needs_truth: bool = False              # the harness arms only
    config_from: Dict[str, Tuple[str, str]] = field(default_factory=dict)   # key -> (base arm name, summary field)


_BASE: Dict[str, ArmSpec] = {
    "DUMMY": ArmSpec("DUMMY", "brain.harness.dummy_arm", "DummyArm"),
    "A0": ArmSpec("A0", "brain.arms.cells.a0", "A0Arm"),
    "A1": ArmSpec("A1", "brain.arms.soft.arm", "ArmA1", {"variant": "A1"}),
    "A1-MLC": ArmSpec("A1-MLC", "brain.arms.soft.arm", "ArmA1", {"variant": "A1"}, mlc=True),
    "A1-NO-SLEEP": ArmSpec("A1-NO-SLEEP", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-NO-SLEEP"}),
    "A1-LOCAL": ArmSpec("A1-LOCAL", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-LOCAL"}),
    "A1-BPTT-AWAKE": ArmSpec("A1-BPTT-AWAKE", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-BPTT-AWAKE"}),
    "A1-FIXED": ArmSpec("A1-FIXED", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-FIXED"}, config_from={"fixed_h": ("A1", "final_h")}),
    # edit: Claude (Opus 5.5), 2026-09-26 11:58 +0400 — the attention twins are SOLVED to A1's final COUNT (§4.1), never given
    # A1's width: `fixed_h` = A1's final H put the readout and the wider heads on top of A1's parameters.
    "A1-ATT": ArmSpec("A1-ATT", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-ATT"},
                      config_from={"match_params": ("A1", "size.n_params_active"), "match_n_names": ("A1", "size.n_names")}),
    "A1-MA": ArmSpec("A1-MA", "brain.arms.soft.arm", "ArmA1", {"variant": "A1-MA", "ma_n_tokens": 63},
                     config_from={"match_params": ("A1", "size.n_params_active"), "match_n_names": ("A1", "size.n_names")}),
    "A4": ArmSpec("A4", "brain.arms.transformer.a4", "ArmA4", config_from={"match_params": ("A1", "size.n_params_active")}),
    # edit: Claude (Opus 5.5), 2026-09-26 12:59 +0400 — A2 at the PREREG §4 row's size (L 4 × G 2,048, a 256-bit state), not the
    # arm's toy defaults (2 layers, 38 gates, 16 bits, 16 names) that the first graded run used because no config was passed —
    # the builder RAISED this to the seat and it was never set. G is 2,077 = 67 × 31, the nearest multiple ≥ 2,048 of the
    # n_groups = name_cap + 3 the group readout needs; name_cap 64 holds the world's 63 names (SEAT-DECISIONS R35).
    "A2": ArmSpec("A2", "brain.arms.logic.arm", "ArmA2", {"name_cap": 64, "n_gates": 2077, "n_layers": 4, "recurrent_bits": 256}),
    "A3": ArmSpec("A3", "brain.arms.clauses.arm", "ArmA3", {"C": 200, "T": 50, "s": 5.0}),
    "D": ArmSpec("D", "brain.arms.library.arm", "LibraryArm"),
    # the hybrids (brain/hybrids/router.py): D inside E′ / F loads D's OWN snapshots (R9) — the dependency is named
    "A5": ArmSpec("A5", "brain.hybrids.router", "ArmA5"),
    "A6": ArmSpec("A6", "brain.hybrids.router", "ArmA6", {"partner": "A3"}),
    "E′": ArmSpec("E′", "brain.hybrids.router", "ArmEPrime", config_from={"part_config.lib.library_load_from": ("D", "arm_dir")}),
    "F": ArmSpec("F", "brain.hybrids.router", "ArmF", config_from={"part_config.lib.library_load_from": ("D", "arm_dir")}),
    "KEY": ArmSpec("KEY", "brain.twins.harness_arms", "KeyArm", {"shift": 0}, needs_truth=True),
    "SHIFTED-KEY": ArmSpec("SHIFTED-KEY", "brain.twins.harness_arms", "KeyArm", {"shift": 1}, needs_truth=True),
    "RING-READ": ArmSpec("RING-READ", "brain.twins.harness_arms", "RingReadArm", needs_truth=True),
}
_TWIN_PREFIX = {"SHUFFLED-NAME": ("transform", "shuffled_name"), "SHUFFLED-RELATION": ("transform", "shuffled_relation"),
                "FORCED": ("wrapper", "forced")}


def known_arm_names() -> List[str]:
    return sorted(_BASE) + [f"{p}:<base>" for p in sorted(_TWIN_PREFIX)]


def spec_for(name: str) -> ArmSpec:
    if name in _BASE:
        b = _BASE[name]
        return ArmSpec(b.name, b.module, b.cls, dict(b.config), b.mlc, b.transform, b.wrapper, b.needs_truth, dict(b.config_from))
    if ":" in name:
        prefix, base = name.split(":", 1)
        if prefix in _TWIN_PREFIX and base in _BASE:
            s = spec_for(base)
            s.name = name
            field_, value = _TWIN_PREFIX[prefix]
            setattr(s, field_, value)
            return s
    raise RunError(f"unknown arm {name!r}; the runner knows: {known_arm_names()}")


# ================================================================================================ the inputs
def load_tape(tape_dir: Path) -> Tuple[List[Dict[str, Any]], str]:
    tape_path = tape_dir / "tape.jsonl"
    data = tape_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    want = (tape_dir / "tape.sha256").read_text().strip()
    if sha != want:
        raise RunError(f"{tape_path}: sha256 {sha} != tape.sha256 {want}")
    rows = [json.loads(l) for l in data.decode("utf-8").splitlines() if l.strip()]
    for r in rows:
        if not verify_row(r):
            raise RunError(f"tape row seq={r.get('seq')} fails its own sha (#191's class: a row that looks parsed is not one that was verified)")
    if [r["seq"] for r in rows] != list(range(1, len(rows) + 1)):
        raise RunError("tape seqs are not 1..N in order")
    return rows, sha


def load_truth(tape_dir: Path) -> Dict[str, Dict[int, Dict[str, Any]]]:
    asks: Dict[int, Dict[str, Any]] = {}
    renders: Dict[int, Dict[str, Any]] = {}
    with (tape_dir / "truth.jsonl").open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["type"] == "ask":
                asks[int(rec["seq"])] = rec
            elif rec["type"] == "rendering":
                renders[int(rec["cache_row"])] = rec
    return {"asks": asks, "renderings": renders}


def load_mlc(tape_dir: Path) -> Dict[int, List[Dict[str, Any]]]:
    p = tape_dir / "mlc.jsonl"
    by_anchor: Dict[int, List[Dict[str, Any]]] = {}
    if not p.exists():
        return by_anchor
    with p.open() as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                mlc_mod.validate_mlc_row(r)
                by_anchor.setdefault(int(r["after_seq"]), []).append(r)
    return by_anchor


# ================================================================================================ grading inline (R27)
def grade(ask_row: Mapping[str, Any], ans: Answer, truth: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if truth is None:
        return {"truth": None, "correct": None}
    t = truth["answer"]
    if t == REFUSE:
        return {"truth": t, "correct": ans.kind in (AnswerKind.UNKNOWN, AnswerKind.NOTHING)}
    return {"truth": t, "correct": right_matches(ask_row["payload"]["answer_kind"], ans, t)}


# ================================================================================================ one arm's run
class _Writer:
    def __init__(self, path: Path) -> None:
        self.f = path.open("w", encoding="utf-8")

    def write(self, rec: Mapping[str, Any]) -> None:
        self.f.write(canonical_json(rec) + "\n")

    def close(self) -> None:
        self.f.close()


def _rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _resolve_config_from(spec: ArmSpec, out_root: Path) -> None:
    for key, (base, field_) in spec.config_from.items():
        summ = out_root / base / "summary.json"
        if not summ.exists():
            raise RunError(f"{spec.name} needs {key} from {base}'s run ({summ} missing) — run {base} first on this seed")
        d = json.loads(summ.read_text())
        v: Any = d
        for part in field_.split("."):          # a dotted SOURCE field reads a nested summary value (size.n_params_active)
            v = v.get(part) if isinstance(v, dict) else None
        if v is None:
            raise RunError(f"{spec.name}: {base}'s summary carries no {field_!r}")
        # a dotted key sets a NESTED config value (the routers' part_config.<role>.<key>)
        parts = key.split(".")
        target = spec.config
        for k in parts[:-1]:
            target = target.setdefault(k, {})
        target[parts[-1]] = v


def _arm_size(arm) -> Dict[str, Any]:
    """Whatever size the arm exposes — `size()` if it has one, else a few well-known attributes. Never graded
    here; recorded for COST-as-a-function-of-size and for A1-FIXED/ATT/MA's parameter match (§4.1)."""
    if hasattr(arm, "size") and callable(getattr(arm, "size")):
        try:
            return dict(arm.size())
        except Exception as e:  # pragma: no cover
            return {"error": repr(e)}
    out: Dict[str, Any] = {}
    for attr in ("h_alive", "hidden", "H", "n_alive", "n_params"):
        v = getattr(arm, attr, None)
        if isinstance(v, (int, float)):
            out[attr] = v
    return out


def run_arm(name: str, seed: int, tape_rows: Sequence[Mapping[str, Any]], tape_sha: str, truth: Mapping[str, Dict[int, Any]],
            mlc_by_anchor: Mapping[int, Sequence[Mapping[str, Any]]], cache_dir: Path, out_root: Path, tape_dir: Path,
            log: Callable[[str], None] = print, max_rows: Optional[int] = None) -> Dict[str, Any]:
    spec = spec_for(name)
    if _OVERRIDES.get(name):
        spec.config.update(_OVERRIDES[name])
        for k in list(spec.config_from):
            if k in _OVERRIDES[name]:
                del spec.config_from[k]          # an explicit value replaces the dependency on another arm's run
    _resolve_config_from(spec, out_root)
    out_dir = out_root / name.replace(":", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = out_dir / "arm"
    run_dir.mkdir(exist_ok=True)
    config: Dict[str, Any] = {"cache_dir": str(cache_dir), "run_dir": str(run_dir), "seed": int(seed), "interpreter": sys.executable}
    config.update(spec.config)
    if spec.needs_truth:
        config["truth_path"] = str(tape_dir / "truth.jsonl")

    rows: List[Dict[str, Any]] = list(tape_rows)
    twin_facts: Dict[str, Any] = {}
    if spec.transform:
        from brain.twins import transforms
        fn = getattr(transforms, spec.transform)
        rows, mp = fn(rows, seed)
        twin_sha = hashlib.sha256("".join(canonical_json(r) + "\n" for r in rows).encode()).hexdigest()
        twin_facts = {"transform": spec.transform, "twin_tape_sha256": twin_sha, "map": mp if len(json.dumps(mp)) < 20000 else "(large; omitted)"}
    if max_rows is not None:
        rows = rows[:max_rows]

    t_start = time.time()
    mod = importlib.import_module(spec.module)
    cls = getattr(mod, spec.cls)
    arm = make_arm(cls, seed, config)
    if spec.wrapper == "forced":
        from brain.twins.forced import ForcedAnswer
        arm = ForcedAnswer(arm)

    truth_asks = truth["asks"]
    ask_kind_by_seq: Dict[int, str] = {r["seq"]: r["payload"]["answer_kind"] for r in rows if r["kind"] == "ASK"}
    w_ans, w_state, w_cost, w_fb = (_Writer(out_dir / "answers.jsonl"), _Writer(out_dir / "state_sha.jsonl"),
                                    _Writer(out_dir / "cost.jsonl"), _Writer(out_dir / "feedback.jsonl"))
    sittings: Dict[str, Dict[str, Any]] = {}
    pending: Dict[int, Answer] = {}
    in_sitting: Optional[str] = None
    sitting_before: Optional[str] = None
    tl_answers: List[Dict[str, Any]] = []     # T_L's answer records (for U4a / U4b after TEST_END)
    tl_rows: Dict[int, Dict[str, Any]] = {}
    n_mlc_rows = 0
    counts = {"asks": 0, "test_asks": 0, "train_asks": 0, "correct_test": 0, "void_sittings": 0, "mlc_rows": 0}

    def record_state(where: str, seq: int) -> None:
        w_state.write({"where": where, "seq": seq, "state_sha": arm.state_sha()})
        c = arm.cost()
        w_cost.write({"where": where, "seq": seq, "arm_events": c["events"], "arm_ms": c["ms"],
                      "wall_s": round(time.time() - t_start, 3), "rss_mb": round(_rss_mb(), 1)})

    def write_answer(row: Mapping[str, Any], ans: Answer, sitting: Optional[str], ms: float, mlc: bool = False) -> Dict[str, Any]:
        tr = truth_asks.get(int(row["seq"]))
        g = grade(row, ans, tr)
        rec = {"seq": row["seq"], "phase": row["phase"], "sitting": sitting, "item": row["item"], "cues": row["payload"]["cues"],
               "answer_kind": row["payload"]["answer_kind"], "answer": ans.to_dict(), "truth": g["truth"], "correct": g["correct"],
               "family": (tr or {}).get("family"), "class": (tr or {}).get("class"), "split": (tr or {}).get("split"),
               "ms": round(ms, 3), "mlc": mlc}
        w_ans.write(rec)
        return rec

    def run_mlc_episode(anchor_seq: int) -> None:
        nonlocal n_mlc_rows
        for mrow in mlc_by_anchor.get(anchor_seq, []):
            n_mlc_rows += 1
            if mrow["kind"] == "ASK":
                t0 = time.perf_counter()
                ans = HarnessContract.training_ask(arm, mrow)
                pending[mrow["seq"]] = ans
                ask_kind_by_seq[mrow["seq"]] = "NAME"
                write_answer(mrow, ans, "MLC", (time.perf_counter() - t0) * 1000.0, mlc=True)
            else:
                a = pending.pop(mrow["payload"]["ask_seq"], None)
                if a is not None:
                    v = HarnessContract.feedback(arm, mrow, a, "NAME")
                    w_fb.write({"seq": mrow["seq"], "ask_seq": mrow["payload"]["ask_seq"], "valence": v, "mlc": True})

    record_state("start", 0)
    last_state_row = 0
    for row in rows:
        kind = row["kind"]
        seq = int(row["seq"])
        if kind == "TEACH":
            HarnessContract.teach(arm, row)
        elif kind == "ARRIVAL":
            HarnessContract.arrival(arm, row)
        elif kind == "SLEEP":
            HarnessContract.sleep(arm, row)
            record_state("sleep", seq)
        elif kind == "TEST_BEGIN":
            in_sitting = row["payload"]["sitting"]
            if hasattr(arm, "offline_train") and in_sitting in ("T_L", "T_D"):
                arm.offline_train([r for r in rows if int(r["seq"]) < seq])
            sitting_before = arm.state_sha()
            sittings[in_sitting] = {"begin_seq": seq, "state_before": sitting_before, "void": False, "reasons": [], "asks": 0}
            record_state(f"begin:{in_sitting}", seq)
        elif kind == "TEST_END":
            after = arm.state_sha()
            s = sittings[in_sitting]
            s.update({"end_seq": seq, "state_after": after})
            if after != sitting_before:
                s["void"] = True
                s["reasons"].append(f"state_sha moved across the sitting ({sitting_before[:12]}… -> {after[:12]}…)")
            if s["void"]:
                counts["void_sittings"] += 1
            record_state(f"end:{in_sitting}", seq)
            if in_sitting == "T_L":
                _collect_why(arm, tl_answers, tl_rows, out_dir, log)
                _collect_rules(arm, tl_answers, tl_rows, truth_asks, out_dir, log)
                s["state_after_u4"] = arm.state_sha()
                if s["state_after_u4"] != after:
                    s["void"] = True
                    s["reasons"].append("state_sha moved during why()/rule() collection")
            in_sitting = None
        elif kind == "ASK":
            counts["asks"] += 1
            t0 = time.perf_counter()
            if in_sitting is not None:
                counts["test_asks"] += 1
                sittings[in_sitting]["asks"] += 1
                try:
                    ans = HarnessContract.test_ask(arm, row)
                except ProtocolError as e:
                    s = sittings[in_sitting]
                    if not s["void"]:
                        s["reasons"].append(str(e)[:300])
                    s["void"] = True
                    ans = arm.answer(row, learn=False)
                rec = write_answer(row, ans, in_sitting, (time.perf_counter() - t0) * 1000.0)
                if rec["correct"]:
                    counts["correct_test"] += 1
                if in_sitting == "T_L":
                    tl_answers.append(rec)
                    tl_rows[seq] = row
            else:
                counts["train_asks"] += 1
                ans = HarnessContract.training_ask(arm, row)
                pending[seq] = ans
                write_answer(row, ans, None, (time.perf_counter() - t0) * 1000.0)
        elif kind == "FEEDBACK":
            a = pending.pop(int(row["payload"]["ask_seq"]), None)
            if a is not None:
                v = HarnessContract.feedback(arm, row, a, ask_kind_by_seq[int(row["payload"]["ask_seq"])])
                w_fb.write({"seq": seq, "ask_seq": row["payload"]["ask_seq"], "valence": v})
            if spec.mlc and seq in mlc_by_anchor:
                run_mlc_episode(seq)
        if seq - last_state_row >= STATE_EVERY_ROWS:
            record_state("periodic", seq)
            last_state_row = seq
    record_state("end", int(rows[-1]["seq"]) if rows else 0)
    counts["mlc_rows"] = n_mlc_rows
    for w in (w_ans, w_state, w_cost, w_fb):
        w.close()

    snap_dir = out_dir / "snapshot"
    snap_dir.mkdir(exist_ok=True)
    try:
        arm.snapshot(snap_dir / "final")
        snapshot_ok = True
    except Exception as e:
        snapshot_ok = f"snapshot failed: {e!r}"
    (out_dir / "sittings.json").write_text(json.dumps(sittings, sort_keys=True, indent=2) + "\n")
    size = _arm_size(arm)
    cost = arm.cost()
    wall = time.time() - t_start
    summary = {
        "arm": name, "seed": seed, "tape_sha256": tape_sha, "rows_run": len(rows), "counts": counts,
        "sittings": {k: {"void": v["void"], "asks": v["asks"], "reasons": v["reasons"]} for k, v in sittings.items()},
        "final_state_sha": arm.state_sha(), "cost": {"arm_events": cost["events"], "arm_ms": cost["ms"], "ms_per_event": (cost["ms"] / cost["events"] if cost["events"] else None)},
        "size": size, "final_h": size.get("h_alive", size.get("h")), "has_why": has_why(arm), "has_rule": has_rule(arm),
        "twin": twin_facts, "forced": (arm.counters() if spec.wrapper == "forced" else None), "snapshot_ok": snapshot_ok,
        "arm_dir": str(run_dir), "config": {k: v for k, v in config.items() if k not in ("run_dir",)},
    }
    (out_dir / "summary.json").write_text(canonical_json(summary) + "\n")
    facts = {"started_at": time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(t_start)), "wall_seconds": round(wall, 1),
             "pid": os.getpid(), "interpreter": sys.executable, "load1_at_end": os.getloadavg()[0], "rss_mb": round(_rss_mb(), 1),
             "threads_env": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}}
    (out_dir / "run-facts.json").write_text(json.dumps(facts, sort_keys=True, indent=2) + "\n")
    log(f"[run] {name}: {len(rows)} rows · asks {counts['asks']} (test {counts['test_asks']}, correct {counts['correct_test']}) · "
        f"void sittings {counts['void_sittings']} · mlc rows {n_mlc_rows} · {cost['ms']:.0f} ms in the arm over {cost['events']} events · wall {wall:.0f}s")
    return summary


def _collect_why(arm, tl_answers: List[Dict[str, Any]], tl_rows: Dict[int, Dict[str, Any]], out_dir: Path, log) -> None:
    """U4a (§5.3): «why?» once per upper-case letter the arm named right at T_L, on its FIRST right U1a item."""
    with (out_dir / "why.jsonl").open("w", encoding="utf-8") as f:
        if not has_why(arm):
            f.write(canonical_json({"no_road": True}) + "\n")
            return
        seen = set()
        for rec in tl_answers:
            if rec["family"] == "U1a_NAME" and rec["class"] == "latin-upper" and rec["correct"] and rec["truth"] not in seen:
                seen.add(rec["truth"])
                try:
                    cited = [int(s) for s in arm.why(tl_rows[rec["seq"]])]
                    err = None
                except Exception as e:
                    cited, err = [], repr(e)
                f.write(canonical_json({"letter": rec["truth"], "seq": rec["seq"], "cited": cited, "n_cited": len(cited), "error": err}) + "\n")
        log(f"[run]   why(): {len(seen)} letters asked")


def _collect_rules(arm, tl_answers: List[Dict[str, Any]], tl_rows: Dict[int, Dict[str, Any]], truth_asks, out_dir: Path, log) -> None:
    """U4b (§5.3): `rule(cue)` per U3 family, executed over that family's T_L items."""
    with (out_dir / "rules.jsonl").open("w", encoding="utf-8") as f:
        if not has_rule(arm):
            f.write(canonical_json({"no_road": True}) + "\n")
            return
        for fam, cue in U3_FAMILY_CUES.items():
            items = [r for r in tl_answers if r["family"] == fam]
            try:
                r = arm.rule(list(cue))
                text = r.get("text") if isinstance(r, dict) else None
                ex = r.get("executable") if isinstance(r, dict) else None
            except Exception as e:
                f.write(canonical_json({"family": fam, "cue": cue, "error": repr(e), "n_items": len(items)}) + "\n")
                continue
            if ex is None:
                f.write(canonical_json({"family": fam, "cue": cue, "text": text, "no_rule": True, "n_items": len(items)}) + "\n")
                continue
            answers = []
            for rec in items:
                try:
                    a = ex(tl_rows[rec["seq"]])
                    answers.append({"seq": rec["seq"], **(a.to_dict() if isinstance(a, Answer) else {"kind": "SILENT", "value": None, "raw": {"bad_return": repr(a)}})})
                except Exception as e:
                    answers.append({"seq": rec["seq"], "kind": "SILENT", "value": None, "raw": {"error": repr(e)}})
            f.write(canonical_json({"family": fam, "cue": cue, "text": text, "n_items": len(items), "answers": answers}) + "\n")
        log(f"[run]   rule(): {len(U3_FAMILY_CUES)} families executed")


# ================================================================================================ main
def run(seed: int, arms: Sequence[str], out_root: Path, tape_dir: Path, cache_dir: Path, log=print, max_rows: Optional[int] = None,
        config_overrides: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
    for nm in arms:
        spec_for(nm)   # refuse unknown names before any work
    global _OVERRIDES
    _OVERRIDES = {k: dict(v) for k, v in (config_overrides or {}).items()}   # per-arm config overrides (A6's partner, a match by hand); recorded in each summary's config
    out_root.mkdir(parents=True, exist_ok=True)
    rows, tape_sha = load_tape(tape_dir)
    truth = load_truth(tape_dir)
    mlc = load_mlc(tape_dir)
    (out_root / "inputs.json").write_text(json.dumps({"seed": seed, "tape_dir": str(tape_dir), "tape_sha256": tape_sha, "rows": len(rows),
                                                      "cache_dir": str(cache_dir), "mlc_episodes": len(mlc), "arms": list(arms)}, indent=2, sort_keys=True) + "\n")
    log(f"[run] seed {seed}: tape {len(rows)} rows (sha {tape_sha[:16]}…), {len(truth['asks'])} truth asks, {len(mlc)} MLC anchors; arms {list(arms)}")
    summaries = {}
    for nm in arms:
        summaries[nm] = run_arm(nm, seed, rows, tape_sha, truth, mlc, cache_dir, out_root, tape_dir, log=log, max_rows=max_rows)
    return summaries


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="B1 runner (B1-PREREG.md §8)")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--arms", required=True, help="comma-separated arm names (see known_arm_names)")
    p.add_argument("--out", required=True)
    p.add_argument("--tape-dir", default=None, help="default /data/dev/brain-runs/b1/<seed>")
    p.add_argument("--cache-dir", default=None, help="default /data/dev/brain-runs/b1/cache/<seed>")
    p.add_argument("--max-rows", type=int, default=None, help="run only the first N rows (a smoke; never a graded run)")
    p.add_argument("--prereg", default=str(REPO_ROOT / "docs" / "brain" / "B1-PREREG.md"))
    p.add_argument("--config-json", default=None, help='per-arm config overrides, e.g. \'{"A6": {"partner": "A2"}, "A4": {"match_params": 68020}}\'')
    ns = p.parse_args(argv)
    overrides = json.loads(ns.config_json) if ns.config_json else None
    tape_dir = Path(ns.tape_dir) if ns.tape_dir else OUT_ROOT / str(ns.seed)
    cache_dir = Path(ns.cache_dir) if ns.cache_dir else OUT_ROOT / "cache" / str(ns.seed)
    run(ns.seed, [a.strip() for a in ns.arms.split(",") if a.strip()], Path(ns.out), tape_dir, cache_dir, max_rows=ns.max_rows, config_overrides=overrides)
    return 0


if __name__ == "__main__":
    sys.exit(main())
