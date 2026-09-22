#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-20 12:35 +0400 — THE VERDICT READER for G4 (docs/G4-PREREG.md §5 as amended by §10, §12, §14, §15, §16).
# Written BEFORE the verdict exists (#158/#214: the reader is pre-registered; its rules are §16), dry-run on life 1's CLOSED
# root as its control (life 1's known defects must show: (iv) refused 435, (vi) unreadable). Read-only on every root (#212):
# the tape is concatenated into --out, the state is COPIED, every twin lives in its own fresh root under --out.
"""usage: python3 tools/verdict_g4.py --root <run root> --genome genome/G4.genome --out runs/g4-verdict-<stamp>
          [--hours 24] [--random 20] [--slice-hours 6] [--regime-step 100] [--workers 8] [--nrestarts N] [--cpu-ns N] [--unit creature.service]
          [--skip-twins] [--skip-random]
       python3 tools/verdict_g4.py --worker <spec.json>            (one twin: replay -> snapshot -> self-exam -> summary.json)
"""
from __future__ import annotations
import argparse, json, os, shutil, statistics, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np

# edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400 — L-4/L-7 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
# §4): "coarse" (drops the fifth, whole-canvas glance from the mind's own learning road — Mind._consume_eye
# strips it from org_feats and writes no coarse journal row) and "surprise" (floor -1: residual/confirmed are
# STILL computed and journaled — a twin to compare the CONFIRM mechanism's effect against, never a twin blind
# to the computation itself) beside the six existing blinds. Neither gene needs to be declared for its blind
# to be harmless (Mind gates every use of self.blind on the gene's OWN presence first).
BLINDS = ["gaze", "sleep", "predict", "curiosity", "park", "frozen", "coarse", "surprise"]
REUSE = False   # --reuse: read existing twin summaries under --out instead of replaying them
WINDOW_SECONDS = 6 * 3600


# edit: Claude (Fable 5.1), 2026-09-22 18:29 +0400 — v3.2 (PREREG §19 / the plan's L-1, Appendix A «what is owed»): the version string names the reader that
# read a record (v3.1 never bumped it — every verdict-8h-v31/results.json said v3); `hash` is a DECLARED volatile field of the vs-live
# comparison only when the reader's commit is not the life's (a live journal is a record of the code it loaded — #234; life 3b's REPLAY
# FAIL at 16:49 was a cross-version hash); the two-replays comparison never masks anything.
READER_VERSION = "tools/verdict_g4.py v3.2 (2026-09-22: v3.1's rules + the version string on the record + `hash` volatile across commits, declared)"


def _git_head(tree) -> "str | None":
    try:
        import subprocess
        return subprocess.check_output(["git", "-C", str(tree), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip() or None
    except Exception:
        return None


def _life_commit(root) -> "str | None":
    """The commit a life LIVED on: its root's CODE-COMMIT (the seam lives, written by tools/lives/launch.sh) or its own checkout's HEAD;
    None when neither exists (the G4 lives under /data/dev/genome ran on master at a commit the register names, not the root)."""
    root = Path(root)
    f = root / "CODE-COMMIT"
    if f.exists():
        v = f.read_text().strip()
        return _git_head(root / "code") or v if (root / "code").exists() else v
    if (root / "code").exists():
        return _git_head(root / "code")
    return None


def replay_ignore_fields(reader_commit, life_commit) -> set:
    """PURE: the fields the vs-live comparison masks. Same commit (both known, equal, or one a prefix of the other) → none; else {"hash"}."""
    if reader_commit and life_commit and (reader_commit == life_commit or reader_commit.startswith(life_commit) or life_commit.startswith(reader_commit)):
        return set()
    return {"hash"}


def _iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read_jsonl(p: Path) -> List[dict]:
    """A journal/tape file the body may still be APPENDING to (tomorrow's live root): tolerate exactly ONE trailing partial line
    (dropped, named on stderr); a torn line anywhere else is corruption and raises. (edit: Claude (Fable 5.1), 2026-09-20 13:21 +0400 — robustness, not a bar.)"""
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    out: List[dict] = []
    for i, l in enumerate(lines):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                print(f"read_jsonl: dropped a trailing partial line in {p} ({len(l)} bytes, being written)", file=sys.stderr)
                break
            raise
    return out


# ----------------------------------------------------------------------------- the tape and the journal, cut at --hours
def _relink(link: Path, target: Path) -> None:
    """A payload symlink under the reader's own --out points at the CURRENT root's payload dir. Life 2's out dir was
    written while its root was `run/`; after the close (`mv run run-g4-life2-…`) the old link pointed into LIFE 3's
    `run/tape/payload` — a silent cross-life read for the solo probe and the plant (found 2026-09-21 14:0x, the v2
    control). A link is re-pointed when its target differs; a real directory is left alone."""
    if link.is_symlink():
        if os.readlink(link) != str(target):
            link.unlink(); os.symlink(target, link)
    elif not link.exists():
        os.symlink(target, link)


def closed_whole(events: Sequence[dict], last_seq: int, tape_last_seq: int) -> bool:
    """edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — plan L-1 × L-5: True iff the record is a CLOSED life read WHOLE (a `stop` event in its
    journal and the cut reaching the tape's last row). Then every whole-tape twin ends its mind the way the body did
    (creature/replay.py:run_replay(close=) — the think in flight lands at the last eye row's seq) or the closed journal carries one
    think row no replay can. A live life, or a cut short of the tape's end, never closes: the live mind lands that think later."""
    return bool(last_seq) and int(last_seq) == int(tape_last_seq) and any(e.get("event") == "stop" for e in events)


def gather(root: Path, out: Path, hours: float) -> dict:
    """Concatenates the root's tape files in seq order into out/tape/ALL.jsonl (payload symlinked, never copied), cut at
    start + hours; copies the state (a snapshot COPY); reads the journal's mind rows and event rows up to the cut."""
    tape_rows = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        tape_rows += read_jsonl(f)
    tape_rows.sort(key=lambda r: r["seq"])
    assert [r["seq"] for r in tape_rows] == list(range(1, len(tape_rows) + 1)), "tape seqs are not 1..N"
    journal = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        journal += read_jsonl(f)
    events = [r for r in journal if "event" in r]
    starts = [e for e in events if e["event"] == "start"]
    assert starts, "no start event in the journal"
    t0 = _iso(starts[0]["at"])
    t_cut = t0 + timedelta(hours=hours)
    tape_cut = [r for r in tape_rows if _iso(r["at"]) <= t_cut]
    last_seq = tape_cut[-1]["seq"] if tape_cut else 0
    mind_rows = [r for r in journal if "event" not in r and int(r["seq"]) <= last_seq]
    events_cut = [e for e in events if _iso(e["at"]) <= t_cut or e["event"] == "stop"]
    (out / "tape").mkdir(parents=True, exist_ok=True)
    pl = out / "tape" / "payload"
    _relink(pl, (root / "tape" / "payload").resolve())   # §18: a --reuse after the root MOVED must not read another life's payloads
    (out / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in tape_cut))
    (out / "live-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    st = out / "live-state"; st.mkdir(exist_ok=True)
    for f in ("organism.npz", "organism.json", "ledger.json"):
        shutil.copy2(root / "state" / f, st / f)
    status = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
    exams = []
    for f in sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit()):
        d = json.loads(f.read_text())
        if _iso(d["at"]) <= t_cut:
            d["_file"] = f.name; exams.append(d)
    return {"t0": t0, "t_cut": t_cut, "tape": tape_cut, "mind": mind_rows, "events": events_cut, "status": status, "exams": exams,
            "closed_whole": closed_whole(events, last_seq, tape_rows[-1]["seq"] if tape_rows else 0),
            "last_seq": last_seq, "hours_on_tape": (_iso(tape_cut[-1]["at"]) - t0).total_seconds() / 3600 if tape_cut else 0.0}


# ----------------------------------------------------------------------------- ALIVE
def alive(G: dict, hours: float, nrestarts: Optional[int]) -> dict:
    t0 = G["t0"]; at = {r["seq"]: _iso(r["at"]) for r in G["tape"]}
    n_hours = int(np.ceil(G["hours_on_tape"])) or 1
    per = {h: {"canvases": 0, "thinks": 0, "sleeps": 0, "snapshots": 0, "exams": 0} for h in range(n_hours)}
    for r in G["mind"]:
        h = int((at[int(r["seq"])] - t0).total_seconds() // 3600)
        if h not in per: continue
        if "moment" in r: per[h]["canvases"] += 1
        elif "think" in r: per[h]["thinks"] += 1
        elif "sleep" in r: per[h]["sleeps"] += 1
    for e in G["events"]:
        h = int((_iso(e["at"]) - t0).total_seconds() // 3600)
        if h in per and e["event"] in ("snapshot", "exam"): per[h][e["event"] + "s"] += 1
    gaps = []
    for sense in ("eye", "ear"):
        ts = [at[r["seq"]] for r in G["tape"] if r["sense"] == sense]
        gaps.append(max((b - a).total_seconds() for a, b in zip(ts, ts[1:])) if len(ts) > 1 else 0.0)
    restarts = [e for e in G["events"] if e["event"] == "sense_restart"]
    crashes = [e for e in G["events"] if e["event"] == "crash"] + ([G["status"]] if G["status"].get("crash") else [])
    stops = [e for e in G["events"] if e["event"] == "stop" and _iso(e["at"]) < G["t_cut"]]
    hours_full = [h for h in per if h < int(hours)]
    moved = all(all(per[h][k] > 0 for k in ("canvases", "thinks", "snapshots", "sleeps")) for h in hours_full) if hours_full else False
    ok = (G["hours_on_tape"] >= hours - 1 / 60) and moved and (max(gaps) <= 60.0) and not crashes and not stops and (nrestarts in (0, None))
    return {"pass": bool(ok), "hours_on_tape": round(G["hours_on_tape"], 3), "bar_hours": hours, "per_hour": per, "every_counter_moved_every_hour": moved,
            "max_gap_s_eye_ear": [round(g, 1) for g in gaps], "sense_restarts": len(restarts), "crashes": len(crashes), "stops_before_cut": len(stops),
            "nrestarts": nrestarts, "note": "NRestarts read from systemd (--nrestarts / --unit); None = not read"}


# ----------------------------------------------------------------------------- twins (one worker per twin, a fresh root each)
# edit: Claude (Fable 5.1), 2026-09-21 22:12 +0400 — two twin defects found at J's landing (G5): (1) the one-glance wrapper's lambda DROPPED every
# keyword the mind now passes (`colour=`, Builder J's block) → TypeError in the T-one-glance worker → (xi) unreadable on every
# G5 verdict; it forwards **kw now. (2) the nowire twin rebuilt Predictor() WITHOUT the genome's declared error arm (E's
# `; error comparator`) → the twin ran the novelty arm while the life ran the comparator; it keeps the arm now. Both factored
# out of worker() so tests/creature/test_verdict_twins_g5.py can call them without a worker process.
# (Builder J found the same dropped-keyword defect independently at 22:20 on its branch — its lambda variant with `colour=None` was dropped at the merge in favour of this **kw helper, which its test pins.)
def _plant_eye_row(rows: List[dict], root: Path) -> dict:
    """REPLAY's planted divergence: the maker eye row WITH a truth file at index 300 among the first 1,000 tape rows when more
    than 300 exist (a G4-shaped tape: exactly the row always picked), else the middle one (a G5 tape shares the seq space with
    the game and folder doors: ~241 maker rows in 1,000). Raises IndexError, named, when no such row exists."""
    mk = [r for r in rows if r["sense"] == "eye" and (r.get("meta") or {}).get("source", "maker") == "maker"
          and (root / "truth" / (Path(r["payload"]).stem + ".json")).exists()]   # §18: a folder/game picture has no truth file
    if not mk:
        raise IndexError("no maker eye row with a truth file in the first 1,000 tape rows")
    return mk[300] if len(mk) > 300 else mk[len(mk) // 2]


def _force_one_glance() -> None:
    """T-one-glance: gaze mode "one" on every glances() call of THIS process (PREREG §16 addendum), every other argument forwarded."""
    from genome import gaze as _gaze
    _orig = _gaze.glances
    _gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="", **kw: _orig(rgb, spec_, g, "one", pic_id, **kw)


def _force_no_coarse() -> None:
    """The blind-coarse twin ASKS with the four located glances it LEARNED on (builder B's clause 9, docs/briefs/LIFE-B-REPORT.md §6:
    a `--blind coarse` twin learned without the fifth glance and was asked with it — «learned without, asked with»). The sibling of
    `_force_one_glance()`: every glances() call of THIS process sees a gaze dict without `coarse`, every other argument forwarded.
    edit: Claude (Fable 5.1), 2026-09-22 20:39 +0400 — written RED first (tests/creature/test_verdict_blind_coarse.py)."""
    from genome import gaze as _gaze
    _orig = _gaze.glances
    _gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="", **kw: _orig(rgb, spec_, {k: v for k, v in dict(g).items() if k != "coarse"}, mode, pic_id, **kw)


def _nowire(mind: "Mind") -> None:
    """The no-wire twin: a fresh unwired Organism; the Predictor rebuilt on it with the SAME declared arm the life runs."""
    from genome.machinery import Organism
    from genome.predict import Predictor
    mind.org = Organism(mind.genome, wire=False)
    if mind.predictor is not None:
        mind.predictor = Predictor(mind.org, arm=mind.predictor.arm)


def worker(spec_path: Path) -> int:
    spec = json.loads(Path(spec_path).read_text())
    from creature.mind import Mind
    from genome.machinery import Organism, parse_genome
    from genome.predict import Predictor
    from genome.questions import build_ledgers
    root = Path(spec["root"]); (root / "tape").mkdir(parents=True, exist_ok=True)
    src_tape = Path(spec["tape"])
    _relink(root / "tape" / "payload", (src_tape.parent / "payload").resolve())
    rows = read_jsonl(src_tape)
    if spec.get("until_seq"):
        rows = [r for r in rows if r["seq"] <= spec["until_seq"]]
    if spec.get("shuffle_words"):
        # T-shuffle: the ear's words permuted across canvases by a fixed rng (the sight stream untouched)
        ears = [i for i, r in enumerate(rows) if r["sense"] == "ear"]
        words = [rows[i]["meta"]["word"] for i in ears]
        perm = np.random.default_rng(5).permutation(len(words))
        for i, j in zip(ears, perm):
            rows[i] = dict(rows[i]); rows[i]["meta"] = dict(rows[i]["meta"]); rows[i]["meta"]["word"] = words[j]
    (root / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))   # self_exam's disjointness control reads it
    genome_path = Path(spec["genome"])
    if spec.get("one_glance"):
        # edit: Claude (Fable 5.1), 2026-09-20 13:03 +0400 — PREREG §16 addendum: G1's T-one-glance = gaze mode "one" (the whole canvas at
        # glance×glance, one feature vector), forced on every glances() call of THIS worker process — the mind's learning road and
        # the exam's held-out alike — without touching creature code (the mind hardcodes surprise/random).
        _force_one_glance()
    if "coarse" in spec.get("blind", []):
        _force_no_coarse()      # edit: Claude (Fable 5.1), 2026-09-22 20:39 +0400 — B's clause 9: the twin asks with the glances it learned on
    mind = Mind(genome_path, root, blind=frozenset(spec.get("blind", [])))
    if spec.get("nowire"):
        _nowire(mind)
    t0 = time.perf_counter(); n_canvas = 0; errs = []
    for r in rows:
        mind.consume(r)
    secs = time.perf_counter() - t0
    if spec.get("close"):
        mind.close()        # edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — a CLOSED life's whole tape: the tail think lands as the body's stop() landed it (close() snapshots)
    else:
        mind.snapshot()
    org = mind.org
    L = build_ledgers(org, mind.moment_word)
    def _cross(log):
        return sum(1 for _m, sc, wc in log if L["sight"].get(sc, set()) != L["words"].get(wc, set()))
    mind_rows = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        mind_rows += [r for r in read_jsonl(f) if "event" not in r]
    (root / "mind-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    n_canvas = sum(1 for r in mind_rows if "moment" in r)
    summary = {"label": spec["label"], "arrivals": org.arrivals, "budget_left": org.budget_left, "births": len(org.births), "c": org.c,
               "glances_confirmed": getattr(mind, "glances_confirmed", None), "glances_surprised": getattr(mind, "glances_surprised", None),   # edit: Claude (Fable 5.1), 2026-09-22 22:33 +0400 — §19.1's twin clause reads the blind-surprise twin's own count
               "closed": bool(spec.get("close")),
               "cells": [int(org.sight.alive.sum()), int(org.words.alive.sum())], "cells_born": org.sight.n + org.words.n,
               "edges_cross": {"born": _cross(org.edges_log), "pruned": _cross(org.prunes_log), "born_total": len(org.edges_log), "pruned_total": len(org.prunes_log)},
               "sleeps": sum(1 for r in mind_rows if "sleep" in r), "thinks": sum(1 for r in mind_rows if "think" in r),
               "parked": sum(1 for r in mind_rows if "think" in r and r["think"].get("parked")),
               "canvases": n_canvas, "seconds": round(secs, 1), "ms_per_canvas": round(1000 * secs / max(1, n_canvas), 2), "hash": org.state_hash()}
    if spec.get("one_glance") or "coarse" in spec.get("blind", []):
        from tools import self_exam as _se           # in-process, so the forced mode "one" (or the forced no-coarse) applies to the held-out glances too
        old_argv = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"]
            _se.main()
        finally:
            sys.argv = old_argv
        summary["exam_stderr"] = ""
    else:
        ex = subprocess.run([sys.executable, str(ROOT / "tools" / "self_exam.py"), "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"],
                            capture_output=True, text=True, cwd=ROOT)
        summary["exam_stderr"] = ex.stderr[-500:] if ex.returncode else ""
    exams = sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit())
    summary["exam"] = json.loads(exams[-1].read_text()) if exams else None
    (root / "summary.json").write_text(json.dumps(summary, default=str))
    return 0


def run_workers(specs: List[dict], workers: int, out: Path) -> Dict[str, dict]:
    procs = []; pending = list(specs); done: Dict[str, dict] = {}
    while pending or procs:
        while pending and len(procs) < workers:
            s = pending.pop(0); sp = out / "specs" / (s["label"] + ".json"); sp.parent.mkdir(exist_ok=True)
            sf0 = Path(s["root"]) / "summary.json"
            if REUSE and sf0.exists():
                done[s["label"]] = json.loads(sf0.read_text()); print(f"  twin {s['label']}: reused", flush=True); continue
            sp.write_text(json.dumps(s)); log = open(out / "specs" / (s["label"] + ".log"), "w")
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker", str(sp)], stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            procs.append((s, p, log))
        time.sleep(2.0)
        still = []
        for s, p, log in procs:
            if p.poll() is None: still.append((s, p, log)); continue
            log.close(); sf = Path(s["root"]) / "summary.json"
            done[s["label"]] = json.loads(sf.read_text()) if sf.exists() else {"label": s["label"], "error": f"worker exit {p.returncode}"}
            print(f"  twin {s['label']}: exit {p.returncode}" + ("" if sf.exists() else " (no summary)"), flush=True)
        procs = still
    return done


def genome_twin_text(base_text: str, label: str, numbers: Optional[dict] = None, fixations: Optional[int] = None, frozen_after: Optional[int] = None) -> str:
    """A genome-TEXT twin: the same file with its numbers replaced (random genomes, (ix)) or GAZE fixations 1 ((xi))."""
    import re
    lines = base_text.splitlines()
    out = []
    for line in lines:
        s = line.split("#")[0].rstrip(); head = s.split()
        if numbers:
            n = numbers
            if head[:2] == ["BIRTH", "novelty"]: line = f"BIRTH    novelty  cos<{n['theta_n']:.4f}"
            elif head[:2] == ["BIRTH", "error"]: line = f"BIRTH    error    misfires {n['misfires']}"
            elif head[:1] == ["BUDGET"]: line = f"BUDGET   {n['budget']} per arrival"
            elif head[:1] == ["KWTA"]: line = f"KWTA     {n['kwta']}"
            elif head[:1] == ["DELTA"]: line = f"DELTA    lr {n['lr']:.4f}"
            elif head[:1] == ["PRUNE"]: line = re.sub(r"w<[0-9.]+", f"w<{n['prune_floor']:.4f}", line.split("#")[0]).rstrip()
            elif head[:1] == ["MERGE"]: line = f"MERGE    cos>{n['theta_m']:.4f} same-answer"
            elif head[:1] == ["SCALE"]: line = f"SCALE    every {n['scale_every']} moments"
            elif head[:2] == ["STAGE", "1"]: line = f"STAGE    1 senses   moments 0..{n['stage1']}"
            elif head[:2] == ["STAGE", "2"]: line = f"STAGE    2 meet     moments {n['stage1']}.."
            elif head[:1] == ["ABSTAIN"]: line = f"ABSTAIN  second/best > {n['abstain_ratio']:.3f}"
        if fixations is not None and head[:1] == ["GAZE"]:
            line = re.sub(r"fixations \d+", f"fixations {fixations}", line.split("#")[0]).rstrip()
        if frozen_after is not None and head[:1] == ["FROZEN"]:
            line = f"FROZEN   after {frozen_after} cells"
        out.append(line)
    return f"# {label} — a genome-text twin written by tools/verdict_g4.py (PREREG §16)\n" + "\n".join(out) + "\n"


# ----------------------------------------------------------------------------- the reader's own asks on an organism
def own_asks(root: Path, genome_path: Path) -> dict:
    """The plant (zog), the null plant (vex), random landing and the ceiling numbers — self_exam does not ask the plant."""
    from tools import self_exam
    from genome import world, run_g1
    from genome.questions import ask_plant_glances
    g, org, ledgers, L = self_exam.load_snapshot(root, genome_path)
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], 10, np.random.default_rng(2))
    held_g = run_g1.glance_held(held, g, "surprise"); feats = run_g1.feats_only(held_g)
    h0 = org.state_hash()
    plant = ask_plant_glances(org, ledgers, world.THING_PLANT, feats[world.THING_PLANT])
    null = ask_plant_glances(org, ledgers, world.THING_NULL, feats[world.THING_NULL])
    rnd = run_g1.landing(run_g1.glance_held(held, g, "random"), things, first=2)
    assert org.state_hash() == h0
    return {"plant": plant, "null": null, "random_landing": rnd}


# ----------------------------------------------------------------------------- MODULATION (§10 verbatim, on the life's own err series)
def _regime_calibration(mind: List[dict], step: int = 100, prev_window: int = 50, first_n: int = 3, settle_skip: int = 3) -> dict:
    """edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3 (G5-H-MODULATION-BARS-W32B.md): the
    null band and the settle bar DERIVED FROM DATA at read time (#158's argument for adaptivity — never a typed
    ratio), from the life's OWN pre-window (window-0) canvases. §16 addendum's ratio bars (3x spike / 1.25x settle /
    1.5x null) were calibrated on the pre-W3-2b ~0.23 steady-state error; W3-2b's memory-relative error collapses the
    steady state to ~0.016 (E's report §0/§3), which makes a ratio bar on a near-floor baseline report on the
    instrument, not the mechanism (SOLUTIONS #162, #228 b) — the same shape as the toy-front repair §16 addendum
    already made once, now needed again for the new regime.

    NULL BAND: at every `step`-th canvas inside window 0, treat it as a FAKE boundary and compute — for every thing
    with >= `first_n` showings after it — the SAME statistic the real spike rule computes: median(its first
    `first_n` errs after the boundary) / median(the `prev_window` errs immediately before it). Doing this at MANY
    boundaries (not just the one midpoint the original null used) over EVERY continuing thing yields a sample of
    "what ratio does pure noise produce on this life's own tape"; its 95th percentile is the null band. A real spike
    must clear this band AND the fixed 3x bar (both, §18 addendum 3 step 1).

    SETTLE BAR: window 0's own per-showing errors, for each thing's showings AFTER its own first `settle_skip`
    (excluding each thing's own bootstrap transient at the very start of the life — the only place on the tape a
    window-0 thing is itself new) — a continuing thing's own steady per-canvas noise. Its 95th percentile is the
    settle bar: an ABSOLUTE error ceiling, not a ratio on a baseline that can collapse to near-zero (1.25x of a
    ~0.016 median is ~0.02 — a bar a single glance's rounding can trip).

    Both derivations read ONLY window-0 rows (pre-window canvases — the only stretch with no real arrival to
    confound the calibration); if window 0 is too short for a given knob, the corresponding reading is None and
    every caller checks for it before grading — never a divide-by-zero, never a silent 0.
    """
    w0 = [r for r in mind if int(r["moment"][1:5]) == 0]
    n = len(w0)
    ratios: List[float] = []
    samples: List[dict] = []
    for m in range(step, max(step, n - first_n), step):
        prev = w0[max(0, m - prev_window):m]
        if not prev:
            continue
        last50 = float(np.median([p["err"] for p in prev]))
        if last50 <= 0:
            continue
        by_thing: Dict[str, list] = {}
        for q in w0[m:]:
            by_thing.setdefault(q["word"], []).append(q["err"])
        for t, errs in by_thing.items():
            if len(errs) >= first_n:
                ratio = float(np.median(errs[:first_n])) / last50
                ratios.append(ratio)
                samples.append({"thing": t, "boundary_idx": m, "last50_med": round(last50, 4), "ratio": round(ratio, 4)})
    null_band_95 = float(np.percentile(ratios, 95)) if ratios else None
    share_within = (sum(1 for r in ratios if r < null_band_95) / len(ratios)) if (ratios and null_band_95 is not None) else None
    seen_count: Dict[str, int] = {}
    noise_errs: List[float] = []
    for r in w0:
        t = r["word"]
        seen_count[t] = seen_count.get(t, 0) + 1
        if seen_count[t] > settle_skip:
            noise_errs.append(r["err"])
    settle_bar_err = float(np.percentile(noise_errs, 95)) if noise_errs else None
    return {"source": "window-0 (pre-window) canvases, this life's own tape — the fake-boundary sample and the settle noise are both derived here, never typed",
            "n_w0_rows": n, "step": step, "prev_window": prev_window, "first_n": first_n,
            "null_ratio_samples": len(ratios), "null_band_95": round(null_band_95, 4) if null_band_95 is not None else None,
            "null_share_within_band": round(share_within, 4) if share_within is not None else None,
            "settle_noise_n": len(noise_errs), "settle_skip_first": settle_skip,
            "settle_bar_err_95": round(settle_bar_err, 6) if settle_bar_err is not None else None,
            "sample_head": samples[:5]}


def modulation(G: dict, F: float, regime_step: int = 100) -> dict:
    # edit: Claude (Fable 5.1), 2026-09-21 20:57 +0400 — `regime_step` (CLI --regime-step): the fake-boundary sampling step of _regime_calibration; 100 = the recorded default; a 2 h window 0 (8 h seam lives) has ~14 boundaries × ~11 things ≈ 150 samples at 100 — enough; 25 is a convenience there (docs/G5-SEAM-LIFE-PLAN.md §1)
    # edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400 — §18: MODULATION reads the DRAWN world only (maker moments "w…"); a folder row's moment is "f<sha>" and its word is a folder name
    # edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3: BOTH the §16 fixed-bar reading (the
    # record — "pass_fixed_bars_record") and the regime-derived reading (_regime_calibration — "pass") are computed
    # and printed; grading (M["MODULATION"]["pass"], what the top-level verdict reads) uses the regime-derived one.
    mind = [r for r in G["mind"] if "moment" in r and r.get("word") and str(r["moment"]).startswith("w")]
    win = lambda r: int(r["moment"][1:5])
    by_seq = {int(r["seq"]): r for r in mind}
    reg = _regime_calibration(mind, step=int(regime_step))
    out = {"F": F,
           "settle_bar": ("record (§16 addendum): err at the 10th showing ≤ 1.25 × the pre-window last-50 median; the toy's F+.05 = %.4f printed per thing. "
                          "§18 addendum 3: the regime-derived bar is an ABSOLUTE ceiling — the life's own pre-window 95th percentile, see 'regime.settle_bar_err_95'.") % (F + 0.05),
           "regime": reg, "windows": {}}
    seen_before: set = set()
    cur = None; idx = 0
    for i, r in enumerate(mind):
        w = win(r)
        if cur is None: cur = w
        if w != cur:
            prev = mind[max(0, i - 50):i]
            last50 = float(np.median([p["err"] for p in prev])) if prev else 0.0
            words_here = []
            for q in mind[i:]:
                if win(q) != w: break
                words_here.append(q)
            new = sorted({q["word"] for q in words_here} - seen_before)
            returning = sorted({q["word"] for q in words_here} & seen_before - {q["word"] for q in prev})
            rec = {"at_seq": int(r["seq"]), "last50_med": round(last50, 4), "new_things": new, "returning_things": returning, "per_thing": {}}
            for t in new + returning:
                errs = [q["err"] for q in words_here if q["word"] == t]
                if len(errs) < 3: continue
                first3 = float(np.median(errs[:3])); tenth = errs[9] if len(errs) >= 10 else None
                spike_fixed = bool(last50 > 0 and first3 >= 3 * last50)
                spike_regime = bool(last50 > 0 and first3 >= 3 * last50 and (reg["null_band_95"] is None or (first3 / last50) >= reg["null_band_95"]))
                settled_fixed = bool(tenth is not None and last50 > 0 and tenth <= 1.25 * last50)
                settled_regime = bool(tenth is not None and reg["settle_bar_err_95"] is not None and tenth <= reg["settle_bar_err_95"])
                first_settle_regime = next((j + 1 for j, e in enumerate(errs) if reg["settle_bar_err_95"] is not None and e <= reg["settle_bar_err_95"]), None)
                rec["per_thing"][t] = {"kind": "new" if t in new else "returning", "first3_med": round(first3, 4),
                                       "spike_ratio": round(first3 / last50, 2) if last50 > 0 else None,
                                       "spike": spike_fixed, "spike_regime": spike_regime,
                                       "err_10th": round(tenth, 4) if tenth is not None else None,
                                       "settled": settled_fixed, "settled_regime": settled_regime,
                                       "settled_toy_bar_F_plus_05": bool(tenth is not None and tenth < F + 0.05),
                                       "first_settle_showing_regime": first_settle_regime, "n_showings": len(errs)}
            out["windows"][str(w)] = rec
            cur = w
        seen_before.add(r["word"])
    # the null: a FAKE boundary at the middle of window 0 — things continuing; the same statistic must show no spike
    w0 = [r for r in mind if win(r) == 0]
    if len(w0) > 200:
        m = len(w0) // 2; prev = w0[m - 50:m]; last50 = float(np.median([p["err"] for p in prev]))
        per = {}
        for t in sorted({q["word"] for q in w0[m:]}):
            errs = [q["err"] for q in w0[m:] if q["word"] == t][:3]
            if len(errs) == 3: per[t] = round(float(np.median(errs)) / last50, 2) if last50 > 0 else None
        out["null_fake_boundary_w0"] = {"at_seq": int(w0[m]["seq"]), "last50_med": round(last50, 4), "spike_ratio_per_thing": per,
                                        "no_spike": all(v is not None and v < 1.5 for v in per.values()) if per else None,   # the §16 record, kept as recorded
                                        # §18 addendum 4 (b2): the graded null clears by MAJORITY under the p95 band (all() failed by construction ~43 % of the time)
                                        "no_spike_regime": null_clears(per, reg["null_band_95"])[0],
                                        "share_under_band_regime": null_clears(per, reg["null_band_95"])[1]}
    # grading: at every window that brings NEW things — majority of the new things spike AND settle (B13's reading, §12)
    # §16 fixed-bar reading — the record; §18 addendum 3 — the regime-derived reading (the top-level verdict grades on it); §18 addendum 4
    # (2026-09-22) — a window whose new things never reached 10 showings (the plant's window) is NOT GRADABLE, never FAIL
    graded, graded_regime, skipped = grade_modulation_windows(out["windows"])
    out["graded_windows"] = graded
    out["graded_windows_regime"] = graded_regime
    out["not_gradable_windows"] = skipped
    nb = out.get("null_fake_boundary_w0", {}) or {}
    out["pass_fixed_bars_record"] = bool(graded) and all(x["pass"] for x in graded) and bool(nb.get("no_spike"))
    out["pass"] = bool(graded_regime) and all(x["pass"] for x in graded_regime) and bool(nb.get("no_spike_regime"))
    if not out["windows"]:
        out["reason"] = "no window change on this tape yet (e.g. a smoke shorter than the maker's window) — not gradable; the regime band is still derived and printed under 'regime'"
    return out


# ----------------------------------------------------------------------------- main
def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker"); ap.add_argument("--root"); ap.add_argument("--genome", default=str(ROOT / "genome" / "G4.genome"))
    ap.add_argument("--out"); ap.add_argument("--hours", type=float, default=24.0); ap.add_argument("--random", type=int, default=20)
    ap.add_argument("--slice-hours", type=float, default=6.0); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--regime-step", type=int, default=100, help="MODULATION: the fake-boundary sampling step over window 0 (100 = the recorded default; 25 for a 2 h window)")
    ap.add_argument("--nrestarts", type=int); ap.add_argument("--cpu-ns", type=int); ap.add_argument("--unit")
    ap.add_argument("--skip-twins", action="store_true"); ap.add_argument("--skip-random", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="re-grade: read twin summaries already under --out instead of replaying")
    ap.add_argument("--sizing-prediction", type=float, default=None, help="PREREG §19.11: the pre-flight's predicted sight births by 24 h (absent = SIZING not gradable)")
    a = ap.parse_args(argv)
    global REUSE; REUSE = bool(a.reuse)
    if a.worker:
        return worker(Path(a.worker))
    T0 = time.perf_counter()
    root = Path(a.root).resolve(); genome_path = Path(a.genome).resolve(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    from genome.machinery import parse_genome
    from genome import run_g0, world
    g = parse_genome(genome_path.read_text())
    R: Dict[str, object] = {"root": str(root), "genome": str(genome_path), "genome_sha": __import__("hashlib").sha256(genome_path.read_bytes()).hexdigest()[:16],
                            "reader": READER_VERSION, "reader_commit": _git_head(Path(__file__).resolve().parent.parent), "life_commit": _life_commit(root), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hours": a.hours}
    nrestarts, cpu_ns = a.nrestarts, a.cpu_ns
    if a.unit:
        try:
            sh = subprocess.run(["systemctl", "--user", "show", a.unit, "-p", "NRestarts", "-p", "CPUUsageNSec"], capture_output=True, text=True).stdout
            kv = dict(l.split("=", 1) for l in sh.strip().splitlines())
            nrestarts = int(kv.get("NRestarts", nrestarts or 0)); cpu_ns = int(kv.get("CPUUsageNSec", cpu_ns or 0))
        except Exception as e:
            R["unit_read_error"] = str(e)
    print(f"[gather] root {root} cut at {a.hours} h", flush=True)
    G = gather(root, out, a.hours)
    R["tape_rows"] = len(G["tape"]); R["mind_rows_live"] = len(G["mind"]); R["exams_in_window"] = [e["_file"] for e in G["exams"]]
    R["ALIVE"] = alive(G, a.hours, nrestarts)
    print(f"[ALIVE] {R['ALIVE']['pass']} hours {R['ALIVE']['hours_on_tape']} moved {R['ALIVE']['every_counter_moved_every_hour']} gaps {R['ALIVE']['max_gap_s_eye_ear']}", flush=True)

    tape_all = out / "tape" / "ALL.jsonl"
    twins_dir = out / "twins"; twins_dir.mkdir(exist_ok=True)
    base_text = genome_path.read_text()
    first_fix = twins_dir / "first-fixation.genome"; first_fix.write_text(genome_twin_text(base_text, "T-first-fixation", fixations=1))
    frozen10 = twins_dir / "frozen-10.genome"; frozen10.write_text(genome_twin_text(base_text, "T-frozen-10", frozen_after=10))
    specs = [{"label": "unblinded-1", "root": str(twins_dir / "unblinded-1"), "tape": str(tape_all), "genome": str(genome_path)},
             {"label": "unblinded-2", "root": str(twins_dir / "unblinded-2"), "tape": str(tape_all), "genome": str(genome_path)}]
    if not a.skip_twins:
        specs += [{"label": f"blind-{b}", "root": str(twins_dir / f"blind-{b}"), "tape": str(tape_all), "genome": str(genome_path), "blind": [b]} for b in BLINDS]
        specs += [{"label": "T-shuffle", "root": str(twins_dir / "T-shuffle"), "tape": str(tape_all), "genome": str(genome_path), "shuffle_words": True},
                  {"label": "T-nowire", "root": str(twins_dir / "T-nowire"), "tape": str(tape_all), "genome": str(genome_path), "nowire": True},
                  {"label": "T-one-glance", "root": str(twins_dir / "T-one-glance"), "tape": str(tape_all), "genome": str(genome_path), "one_glance": True},
                  {"label": "T-first-fixation", "root": str(twins_dir / "T-first-fixation"), "tape": str(tape_all), "genome": str(first_fix)},
                  {"label": "T-frozen-10", "root": str(twins_dir / "T-frozen-10"), "tape": str(tape_all), "genome": str(frozen10), "blind": ["frozen"]}]
    # edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — a CLOSED life read WHOLE (gather's `closed_whole`) ends every whole-tape twin's mind the way the
    # body did; the slice/random twins below cut the tape short and never close (the live mind lands that think at a later boundary).
    for _s in specs:
        if not _s.get("until_seq"):
            _s["close"] = bool(G.get("closed_whole"))
    # (ix): the first --slice-hours of the tape under 20 random genomes (numbers only, structure fixed) and under the creature's own
    slice_seq = 0
    for r in G["tape"]:
        if (_iso(r["at"]) - G["t0"]).total_seconds() <= a.slice_hours * 3600: slice_seq = r["seq"]
    if not a.skip_random:
        specs.append({"label": "slice-own", "root": str(twins_dir / "slice-own"), "tape": str(tape_all), "genome": str(genome_path), "until_seq": slice_seq})
        for seed in range(1, a.random + 1):
            rg = run_g0.random_genome(g, seed); nums = run_g0.genome_numbers(rg)
            gp = twins_dir / f"random-{seed}.genome"; gp.write_text(genome_twin_text(base_text, f"random genome seed {seed}", numbers=nums))
            parse_genome(gp.read_text())   # it must parse before it is spent on
            specs.append({"label": f"random-{seed}", "root": str(twins_dir / f"random-{seed}"), "tape": str(tape_all), "genome": str(gp), "until_seq": slice_seq, "numbers": nums})
    # G4-7's solo: the first 1,000 rows replayed ALONE before any worker starts (a replay under 8 workers is not solo)
    solo_ms = None
    try:
        from creature.mind import Mind
        sroot = out / "solo-probe"; (sroot / "tape").mkdir(parents=True, exist_ok=True)
        _relink(sroot / "tape" / "payload", (root / "tape" / "payload").resolve())
        sm = Mind(genome_path, sroot); srows = [r for r in G["tape"] if r["seq"] <= 1000]
        ts = time.perf_counter()
        for r in srows: sm.consume(r)
        solo_ms = round(1000 * (time.perf_counter() - ts) / max(1, sum(1 for r in srows if r["sense"] == "eye")), 2)
    except Exception as e:
        R["solo_probe_error"] = repr(e)
    R["solo_ms_per_canvas_probe"] = solo_ms
    print(f"[solo] {solo_ms} ms a canvas over the first 1,000 rows, alone", flush=True)
    print(f"[twins] {len(specs)} replays, {a.workers} workers, slice_seq {slice_seq}", flush=True)
    TW = run_workers(specs, a.workers, out)
    R["twins"] = TW

    # REPLAY + (vii): the unblinded replay vs the live journal, and the second unblinded replay vs the first; the planted divergence
    from creature import replay as replay_mod
    live = replay_mod.read_mind_journal(out / "live-journal.jsonl")
    u1 = replay_mod.read_mind_journal(twins_dir / "unblinded-1" / "mind-journal.jsonl")
    u2 = replay_mod.read_mind_journal(twins_dir / "unblinded-2" / "mind-journal.jsonl")
    _ign = replay_ignore_fields(R.get("reader_commit"), R.get("life_commit"))
    d_live = replay_mod.compare(u1, live, ignore=_ign); d_two = replay_mod.compare(u1, u2)   # v3.2: the two-replays comparison masks nothing
    # the plant: the first 1,000 rows with one eye payload's thing inverted (its cell from the root's truth file) must DIVERGE
    plant_ok = None; plant_seq = None
    try:
        from PIL import Image
        rows = [r for r in G["tape"] if r["seq"] <= 1000]
        # edit: Claude (Fable 5.1), 2026-09-21 22:40 +0400 — G5 dry-run (0.1 h of a tape with the game door ON): the first 1,000 rows hold only ~241 MAKER
        # eye rows (the game and folder rows share the seq space), so a fixed index 300 raised IndexError and the plant read as an error.
        # The plant is now the maker eye row WITH a truth file at index 300 when there are more than 300, else the middle one; a G4-shaped
        # tape (maker only, ~500 eye rows in 1,000) picks exactly the row it always picked. The chosen seq is on the record (plant_seq).
        eye = _plant_eye_row(rows, root)
        proot = out / "plant-root"; (proot / "tape").mkdir(parents=True, exist_ok=True); (proot / "tape" / "payload").mkdir(exist_ok=True)
        for r in rows:
            src = root / "tape" / r["payload"]; dst = proot / "tape" / r["payload"]
            if dst.is_symlink() or not dst.exists():
                _relink(dst, src.resolve())
        pp = proot / "tape" / eye["payload"]; pp.unlink()
        arr = np.array(Image.open(root / "tape" / eye["payload"]).convert("RGB"))
        truth = json.loads((root / "truth" / (Path(eye["payload"]).stem + ".json")).read_text())
        cy, cx = truth["cell"]; y0, x0 = max(0, min(int((cy + 0.5) * 8) - 12, 104)), max(0, min(int((cx + 0.5) * 8) - 12, 104))
        arr[y0:y0 + 24, x0:x0 + 24] = 255 - arr[y0:y0 + 24, x0:x0 + 24]; Image.fromarray(arr).save(pp, format="PNG")
        (proot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        if (proot / "replay").exists(): shutil.rmtree(proot / "replay")   # §18: a --reuse re-grade recomputes the plant in the reader's own scratch (FileExistsError otherwise)
        pj = replay_mod.run_replay(genome_path, proot / "tape" / "ALL.jsonl", proot / "replay")
        dp = replay_mod.compare(replay_mod.read_mind_journal(pj), [r for r in live if int(r["seq"]) <= 1000])
        plant_ok = dp is not None; plant_seq = eye["seq"]; R["replay_plant_diverged_at"] = dp
    except Exception as e:
        R["replay_plant_error"] = repr(e)
    R["REPLAY"] = {"pass": d_live is None and d_two is None and plant_ok is True, "vs_live": d_live, "two_replays": d_two, "mind_rows": len(u1), "hash_masked": sorted(_ign), "closed_whole": bool(G.get("closed_whole")),
                   "plant_seq": plant_seq, "plant_caught": plant_ok}
    print(f"[REPLAY] {R['REPLAY']}", flush=True)

    # the organism at the cut = the unblinded replay's snapshot (byte-identical to the live one when REPLAY passes)
    own = own_asks(twins_dir / "unblinded-1", genome_path)
    R["own_asks"] = own
    U = TW["unblinded-1"]; E = U["exam"]; seen = E["ask_seen_words"]; allw = E["ask_all_words"]
    last_live_exam = G["exams"][-1] if G["exams"] else None
    def q(twin, key="Q1"):
        # §16 addendum 2: every TWIN is read on ask_all_words (the same 160-question denominator as the creature's all-words Q1) —
        # a twin that met only 2 words scored .75 on its own 20 questions and .094 on the 160 (the control run, 13:2x)
        t = TW.get(twin, {}); ex = t.get("exam") or {}; return (ex.get("ask_all_words") or {}).get(key, {}).get("acc")
    Q1_ALL = allw["Q1"]["acc"]
    M: Dict[str, dict] = {}
    M["i_knows"] = {"pass": seen["Q1"]["acc"] >= .80 and seen["Q2"]["acc"] >= .80 and seen["Q3"]["acc"] >= .85 and seen["Q4"]["acc"] >= .90,
                    "Q1": seen["Q1"]["acc"], "Q2": seen["Q2"]["acc"], "Q3": seen["Q3"]["acc"], "Q4": seen["Q4"]["acc"], "chance_Q1": E["chance_q1"],
                    "all_words": {k: allw[k]["acc"] for k in ("Q1", "Q2", "Q3", "Q4")}, "per_thing_Q1": seen["Q1"]["per_thing"],
                    "live_exam_last": {k: (last_live_exam["ask_seen_words"][k]["acc"] if last_live_exam else None) for k in ("Q1", "Q2", "Q3", "Q4")},
                    "bar": "Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90"}
    M["ii_meeting_real"] = {"pass": (q("T-shuffle") is not None and q("T-shuffle") <= .20) and (q("T-nowire") is not None and q("T-nowire") <= .20),
                            "T_shuffle_Q1": q("T-shuffle"), "T_nowire_Q1": q("T-nowire"), "bar": "≤ .20"}
    M["iii_growth_matters"] = {"pass": q("T-frozen-10") is not None and q("T-frozen-10") <= Q1_ALL - .30, "T_frozen_10_Q1": q("T-frozen-10"), "T_frozen_50_Q1": q("blind-frozen"),
                               "T_frozen_10_cells": TW.get("T-frozen-10", {}).get("cells"), "Q1": Q1_ALL, "bar": "≥ 30 pp under on all 16 words (the twin FROZEN after 10 cells, G0b's; the 50-cell twin printed — §16 addenda)"}
    c = U["c"]; pruned_share = c["edges_pruned"] / c["edges_born"] if c["edges_born"] else 0.0
    refused = iv_refusals(c)   # §18 addendum 4 (2026-09-22): every CAP refusal counts — budget, nmax, frozen; redundant printed only
    M["iv_grows_alone"] = {"pass": U["cells_born"] >= 50 and refused["caps_total"] == 0 and pruned_share >= .05 and c["removed_for_disuse"] == 0,
                           "cells_born": U["cells_born"], "births_refused_budget": c["births_refused_budget"], "refused": refused, "arrivals": U["arrivals"], "budget_left": U["budget_left"],
                           "pruned_share": round(pruned_share, 4), "edges_born": c["edges_born"], "edges_pruned": c["edges_pruned"], "edges_cross": U["edges_cross"],
                           "removed_for_disuse": c["removed_for_disuse"], "bar": "≥ 50 born · 0 refused at ANY cap (budget · nmax · frozen; §18 add. 4) · ≥ 5 % pruned · 0 by disuse"}
    # (v) §15's pair: per odd window, the LAST exam inside it vs the LAST exam of the preceding even window, Q1 on the seen eleven
    seq_at = {r["seq"]: r for r in G["tape"]}
    def window_of(ex):
        s = ex.get("snapshot_last_seq") or 0
        # §18 hardening: walk back to the nearest MAKER row (a folder row's moment is "f<sha>", not a window)
        while s > 0 and (s not in seq_at or not str((seq_at[s].get("meta") or {}).get("moment", "")).startswith("w")): s -= 1
        return int(seq_at[s]["meta"]["moment"][1:5]) if s in seq_at else None
    by_w: Dict[int, List[dict]] = {}
    for ex in G["exams"]:
        w = window_of(ex)
        if w is not None: by_w.setdefault(w, []).append(ex)
    pairs = []
    for w in sorted(by_w):
        if w % 2 == 1 and (w - 1) in by_w:
            before = by_w[w - 1][-1]; first_after = by_w[w][0]; last_in = by_w[w][-1]
            q1 = lambda ex: ex["ask_seen_words"]["Q1"]["acc"]
            pairs.append({"window": w, "before": q1(before), "first_after": q1(first_after), "last_in_window": q1(last_in), "drop_pp": round(100 * (q1(before) - q1(last_in)), 1),
                          "files": [before["_file"], first_after["_file"], last_in["_file"]]})
    M["v_retention"] = {"pass": bool(pairs) and all(p["drop_pp"] <= 5.0 for p in pairs), "pairs": pairs, "bar": "≤ 5 pp on the last-of-window pair (§15)", "note": "no odd window with exams on both sides → not readable" if not pairs else ""}
    p, n = own["plant"], own["null"]
    M["vi_knows_unknown"] = {"pass": p["answered_rate"] > .5 and n["abstain_rate"] > .5 and (seen["Q5"][world.THING_NEVER]["abstain_rate"] >= .80) and seen["Q1"]["false_abstention"] <= .20,
                             "plant_zog": p, "null_vex": n, "Q5_spiral_abstain": seen["Q5"][world.THING_NEVER]["abstain_rate"], "false_abstention": seen["Q1"]["false_abstention"],
                             "bar": "plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20"}
    M["vii_replay"] = {"pass": R["REPLAY"]["pass"], **{k: v for k, v in R["REPLAY"].items() if k != "pass"}, "bar": "two replays byte-identical; the plant caught"}
    st = G["status"]
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — (viii) in ONE unit (#162): the per-row median it read until today is not the probe's ms per canvas
    M["viii_cost"] = viii_cost(st, R.get("solo_ms_per_canvas_probe") or U["ms_per_canvas"], U["ms_per_canvas"], cpu_ns)
    if not a.skip_random:
        comps = []
        for k, t in TW.items():
            if k == "slice-own" or k.startswith("random-"):
                ex = t.get("exam") or {}; comp = (ex.get("ask_seen_words") or {}).get("composite")
                comps.append({"label": k, "composite": comp, "cells": t.get("cells"), "numbers": t.get("numbers")})
        ranked = sorted([x for x in comps if x["composite"] is not None], key=lambda x: -x["composite"])
        rank = next((i + 1 for i, x in enumerate(ranked) if x["label"] == "slice-own"), None)
        M["ix_not_luck"] = {"pass": rank is not None and rank <= max(1, len(ranked) // 4) + (1 if len(ranked) % 4 else 0) and rank <= 5,
                            "rank_of_own": rank, "of": len(ranked), "own_composite": next((x["composite"] for x in comps if x["label"] == "slice-own"), None),
                            "best_random": next((x for x in ranked if x["label"] != "slice-own"), None), "slice_seq": slice_seq, "bar": "top quartile of 20 random genomes (rank ≤ 5 of 21), numbers only, on the first slice"}
    lx = E["gaze_landing"]; lr = own["random_landing"]
    M["x_gaze_finds_thing"] = {"pass": lx["rate"] >= .90 and lx["rate"] >= 1.5 * lr["rate"], "gaze_rate": lx["rate"], "random_rate": lr["rate"], "random_ceiling_expected": 0.069,
                               "ratio": round(lx["rate"] / lr["rate"], 2) if lr["rate"] else None, "bar": "≥ .90 in the first 2 fixations · ≥ 1.5× random"}
    M["xi_gaze_earns_place"] = {"pass": q("T-one-glance") is not None and Q1_ALL - q("T-one-glance") >= .10, "Q1_gaze": Q1_ALL, "Q1_one_glance": q("T-one-glance"),
                                "Q1_first_fixation_only": q("T-first-fixation"), "Q1_random_gaze": q("blind-gaze"),
                                "bar": "≥ .10 over G1's one-glance twin (gaze mode 'one': the whole canvas at glance×glance); the first-fixation-only twin printed — §16 addendum"}
    F = 1.0 - g.theta_n
    # edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3: the bar text now names both readings; M["MODULATION"]["pass"] grades on the regime-derived one (modulation()'s own doc)
    M["MODULATION"] = modulation(G, F, regime_step=a.regime_step)
    M["MODULATION"]["bar"] = ("§18 addendum 3: at every window bringing NEW things, a majority spike (≥ 3× the last-50 median AND ≥ the life's own regime null-band) and settle "
                              "(≤ the life's own regime settle-bar) by the 10th showing; the fake-boundary null clears the same band. "
                              "The §16 record (3× spike / 1.25× settle / 1.5× null, calibrated pre-W3-2b) is printed as 'pass_fixed_bars_record'.")
    np_err = None
    if "blind-predict" in TW and (twins_dir / "blind-predict" / "mind-journal.jsonl").exists():
        errs = [r["err"] for r in read_jsonl(twins_dir / "blind-predict" / "mind-journal.jsonl") if "moment" in r and "err" in r]
        np_err = {"max_err": max(errs) if errs else None, "n": len(errs)}
    M["MODULATION"]["no_predict_twin_err"] = np_err
    parked = U["parked"]
    M["PLANTS"] = {"vi": M["vi_knows_unknown"]["pass"], "predict_file_pair": "cannot fire on the maker's ear-then-eye stream (§14); predictions_filed " + str(st.get("predictions_filed")),
                   "park_unanswerable_want": "the folder door is OFF (§6)", "sleep_replay": {"sleeps": U["sleeps"], "no_sleep_twin_sleeps": TW.get("blind-sleep", {}).get("sleeps")},
                   "belief_contradiction": "clash unwired (§14)"}
    M["TWINS"] = {b: {"Q1": q(f"blind-{b}"), "Q1_seen": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_seen_words") or {}).get("Q1", {}).get("acc"),
                      "composite": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_all_words") or {}).get("composite"), "cells": TW.get(f"blind-{b}", {}).get("cells")} for b in BLINDS}
    M["TWINS"]["random_gaze_loses_xi"] = {"pass": q("blind-gaze") is not None and Q1_ALL - q("blind-gaze") >= .10, "margin": None if q("blind-gaze") is None else round(Q1_ALL - q("blind-gaze"), 3)}
    M["TWINS"]["no_sleep_v"] = {"graded": False, "reason": "SLEEP's retention is not gradable on drawn worlds (§10)", "no_sleep_Q1": q("blind-sleep")}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door mark needs the folder/web door (OFF)"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "PARK unreadable (folder OFF)"}
    # ------------------------------------------------------------------ §18 (edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400): W3-2, DOOR, W3-1, PARK graded
    decl = g.declared
    def _pred_rows(twin_root: Path) -> List[dict]:
        pth = twin_root / "state" / "predictions.jsonl"
        return read_jsonl(pth) if pth.exists() else []
    def _rule_stats(rows: List[dict]) -> dict:
        rules = [r for r in rows if ("cluster" in r or "shared" in r)]
        filed = [r for r in rules if r.get("accepted") and r.get("outcome") is None]
        refused = [r for r in rules if not r.get("accepted")]
        scored = [r for r in rules if r.get("outcome") in (True, False)]
        acc = (sum(1 for r in scored if r["outcome"] is True) / len(scored)) if scored else None
        words = sorted(set(str(r.get("word") or (r.get("words") or ["?"])[0]) for r in rules))
        sight_road = [r for r in rows if not ("cluster" in r or "shared" in r)]
        return {"filed": len(filed), "refused": len(refused), "scored": len(scored), "accuracy": None if acc is None else round(acc, 3), "words": words,
                "induce": sum(1 for r in rules if "cluster" in r), "deduce": sum(1 for r in rules if "shared" in r), "sight_road_rows": len(sight_road)}
    live_pred = _rule_stats(_pred_rows(twins_dir / "unblinded-1")); shuf_pred = _rule_stats(_pred_rows(twins_dir / "T-shuffle"))
    # edit: Claude (Fable 5.1), 2026-09-21 15:21 +0400 — §18 addendum 2 (the #162 control on W3-2): a rule's CLUSTER must be the word's OWN cells.
    # Life 3a's INDUCE compared a sight cell id to a words index (genome/think.py:411, fixed at the life-3b boundary), so its rules were
    # induced from ANOTHER word's cells and scored 6/6 by accident. Read from the ROOT's OWN predictions and END snapshot (never the replay,
    # which runs the current code): per induce rule, the share of its cluster that answers its word at the end; the eligible-word count
    # (words with ≥ 1 own cell) is the denominator printed beside the accuracy. Refuses to grade PASS when any scored/filed rule's cluster
    # share < .5 (wrong cells) or fewer than 5 words are eligible.
    def _cluster_control(root: Path) -> dict:
        try:
            from genome.machinery import Organism as _Org
            from genome import world as _world
            org = _Org.load(root / "state" / "organism", g)
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}", "ok": False}
        L = json.loads((root / "state" / "ledger.json").read_text())
        words = sorted({w for s in L["words"].values() for w in s if w})
        own: Dict[str, List[int]] = {}
        for w in words:
            r = org.recall("words", _world.encode_word(w, g.ear_blank_zero))
            lit = r.get("lit")
            own[w] = [] if lit is None else sorted(int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == lit)
        eligible = sorted(w for w in words if own[w])
        rows = read_jsonl(root / "state" / "predictions.jsonl") if (root / "state" / "predictions.jsonl").exists() else []
        per_rule = []
        for r in rows:
            if "cluster" not in r or not r.get("accepted"):
                continue
            w = str(r.get("word")); cl = [int(c) for c in (r.get("cluster") or [])]
            share = (sum(1 for c in cl if c in set(own.get(w, []))) / len(cl)) if cl else 0.0
            per_rule.append({"word": w, "cluster": len(cl), "own_share": round(share, 3), "outcome": r.get("outcome")})
        wrong = [x for x in per_rule if x["own_share"] < .5]
        reached = sorted({x["word"] for x in per_rule})          # the words the mechanism actually REACHED (life 3a: 1 of 21 — «bar», by a coincidence of ids)
        ok = (len(eligible) >= 5) and not wrong and (len(reached) >= 5)
        return {"eligible_words": len(eligible), "words": len(words), "own_cells": {w: len(own[w]) for w in words}, "rules": per_rule,
                "wrong_cell_rules": len(wrong), "words_with_rules": len(reached), "reached": reached, "ok": ok,
                "reason": "" if ok else w3_2_reason(len(eligible), len(reached), wrong)}   # §18 add. 4: the reason names the clause that failed
    cluster_ctl = _cluster_control(root)
    think_rows = [r for r in G["mind"] if "think" in r]
    parked_rules = sum(1 for r in think_rows if (r["think"] or {}).get("kind") == "rule" and (r["think"] or {}).get("parked"))
    rules_declared = ("INDUCE" in decl) or ("DEDUCE" in decl)
    chance = 1.0 / 11 + .10
    shuffle_ok = (shuf_pred["scored"] == 0) or (shuf_pred["accuracy"] is not None and shuf_pred["accuracy"] <= chance)
    M["W3_2_rules"] = {"graded": rules_declared,
                       "pass": rules_declared and live_pred["filed"] + live_pred["scored"] > 0 and live_pred["scored"] > 0 and (live_pred["accuracy"] or 0.0) >= .80 and shuffle_ok and bool(cluster_ctl.get("ok")),
                       "cluster_control": cluster_ctl,
                       "live": live_pred, "T_shuffle": shuf_pred, "parked_rules": parked_rules, "shuffle_bar": "≤ 1/11 + .10 when any rule is scored; 0 scored = the shuffle destroyed the meeting (D's toy)",
                       "bar": "filed > 0 · scored > 0 · accuracy ≥ .80 (W3-2c's decider) · the shuffled-words twin at chance · every rule's cluster ≥ .5 the word's OWN cells · rules reach ≥ 5 of ≥ 5 eligible words (§18 add. 2)",
                       "reason": ("" if rules_declared else "INDUCE/DEDUCE not declared in this life's genome — not graded") + (cluster_ctl.get("reason") or "")}
    tape = G["tape"]
    folder_rows = [r for r in tape if (r.get("meta") or {}).get("source") == "folder"]
    f_ear_moments = {(r.get("meta") or {}).get("moment") for r in folder_rows if r["sense"] == "ear"}
    f_pics = [r for r in folder_rows if r["sense"] == "eye"]
    sight_only = [r for r in f_pics if (r.get("meta") or {}).get("moment") not in f_ear_moments]
    folder_words = sorted({(r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"} - {None})
    recog = {}
    try:
        from tools import self_exam as _se2
        from genome import ask as _gask
        _g2, _org2, _led2, _L2 = _se2.load_snapshot(twins_dir / "unblinded-1", genome_path)
        _Lw2 = _led2["words"]; _h2 = _org2.state_hash()
        by_word: Dict[str, list] = {}
        for r in folder_rows:
            if r["sense"] == "ear": by_word.setdefault((r.get("meta") or {}).get("word"), [])
        moment_word = {(r.get("meta") or {}).get("moment"): (r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"}
        for r in f_pics:
            w = moment_word.get((r.get("meta") or {}).get("moment"))
            if w and len(by_word.get(w, [])) < 3: by_word.setdefault(w, []).append(r)
        for w, pics in by_word.items():
            hits = 0
            for r in pics:
                res = _org2.recall_many("sight", _gask.glance_picture(root / "tape" / r["payload"], _g2))
                ans = "/".join(sorted(_Lw2.get(res["cell"], set()))) if res.get("cell") is not None else None
                hits += int(ans == w)
            recog[w] = {"asked": len(pics), "own_word": hits}
        assert _org2.state_hash() == _h2
    except Exception as e:
        recog = {"error": repr(e)}
    door_graded = bool(decl.get("WORLD", {}).get("folder"))
    M["DOOR"] = {"graded": door_graded, "pass": door_graded and len(f_pics) >= 300 and len(folder_words) >= 11,
                 "folder_rows": len(folder_rows), "pictures": len(f_pics), "sight_only_rows": len(sight_only), "sight_only_first_seq": sight_only[0]["seq"] if sight_only else None,
                 "folder_words": folder_words, "recognition_of_seen_pictures": recog,
                 "bar": "≥ 300 pictures on the tape · ≥ 11 folder words heard (§18); sight-only rows and recognition REPORTED (§8)",
                 "reason": "" if door_graded else "no `folder <dir>` in the WORLD line — the door is OFF"}
    bel_path = twins_dir / "unblinded-1" / "state" / "beliefs.jsonl"
    bel_rows = read_jsonl(bel_path) if bel_path.exists() else []
    heard = sorted({(r.get("meta") or {}).get("word") for r in tape if r["sense"] == "ear"} - {None})
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — the bar accounts for the clash law's own fresh belief row (found on the six 2 h smokes)
    M["W3_1_beliefs"] = w3_1_beliefs(bel_rows, decl, heard)
    kinds = M["W3_1_beliefs"]["kinds"]
    M["PARK"] = {"graded": True, "pass": parked >= 1 and (parked / U["thinks"] <= .05 if U["thinks"] else False), "parked": parked, "thinks": U["thinks"],
                 "parked_share": round(parked / U["thinks"], 4) if U["thinks"] else None, "parked_rules": parked_rules,
                 "no_park_twin_parked": TW.get("blind-park", {}).get("parked"),
                 "reason": "graded in this life (§18): a dead end can arrive from a rule failed 3× or a wordless sight; sight-only rows on this tape: %d" % len(sight_only),
                 "bar": "≥ 1 parked · share ≤ 5 %"}
    # edit: Claude (Fable 5.1), 2026-09-22 19:3x +0400 — THE ONE LIFE's marks (PREREG §19.5/§19.10/§19.11; plan L-1): pure functions in
    # tools/verdict_life.py; each reads «not gradable» on a record whose life did not declare the line (the closed records are the control).
    from tools import verdict_life as _vl
    M["ACT"] = _vl.act_mark(tape, live, st)
    if M["ACT"].get("graded"):
        # the shuffled-act PLANT (§19.5's control): the first rows up to the 20th mind-chosen game outcome, every such outcome's act moved
        # to the next one; the replay must journal an act_mismatch on the first of them, or the check does not check.
        try:
            _mind_out = [r for r in tape if r["sense"] == "outcome" and (r.get("meta") or {}).get("chosen_by") == "mind"]
            _cut = int(_mind_out[min(19, len(_mind_out) - 1)]["seq"])
            _rows = _vl.shift_acts([r for r in tape if int(r["seq"]) <= _cut])
            aroot = out / "act-plant-root"; (aroot / "tape" / "payload").mkdir(parents=True, exist_ok=True)
            for r in _rows:
                src = root / "tape" / r["payload"]; dst = aroot / "tape" / r["payload"]
                if r["sense"] == "outcome" and (r.get("meta") or {}).get("chosen_by") == "mind":
                    if dst.is_symlink() or dst.exists(): dst.unlink()
                    _m = r["meta"]; dst.write_text(json.dumps({"act": _m.get("act"), "expected": None, "got": _m.get("got"), "residual": None, "source": "game"}))
                elif dst.is_symlink() or not dst.exists():
                    _relink(dst, src.resolve())
            (aroot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in _rows))
            if (aroot / "replay").exists(): shutil.rmtree(aroot / "replay")
            _pj = replay_mod.run_replay(genome_path, aroot / "tape" / "ALL.jsonl", aroot / "replay")
            _mis = [j for j in replay_mod.read_mind_journal(_pj) if isinstance(j.get("outcome"), dict) and j["outcome"].get("act_mismatch")]
            M["ACT"]["shuffled_twin_diverged"] = bool(_mis); M["ACT"]["shuffled_twin_first_mismatch_seq"] = (int(_mis[0]["seq"]) if _mis else None)
            M["ACT"]["pass"] = bool(M["ACT"]["pass"]) and bool(_mis)
        except Exception as e:
            M["ACT"]["shuffled_twin_diverged"] = None; M["ACT"]["shuffled_twin_error"] = repr(e); M["ACT"]["pass"] = False
    else:
        M["ACT"]["shuffled_twin_diverged"] = "not run (not gradable)"
    M["SOUND"] = _vl.sound_mark(tape, live, st)
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:52 +0400 — ALPHA4-G.md task 5: `grow=` from
    # the life's OWN genome (`decl`, already parsed above for "SELF"/"ANSWER") — never guessed from STATUS
    # shape, so a genome that happens to have a small sight_nmax under NMAX is never mistaken for GROW.
    M["SIZING"] = _vl.sizing_mark(st, live, a.sizing_prediction, grow=("GROW" in decl))
    M["GRADE"] = _vl.grade_mark(own["plant"], own["null"], seen, "ANSWER" in decl)      # §19.3 (builder A's graded answer)
    M["SELF"] = _vl.self_mark(tape, bel_rows, live, st, "SELF" in decl)                 # §19.6 (builder A's SELF)
    # edit: Claude (Fable 5.1), 2026-09-22 22:33 +0400 — §19.1 as re-specified: per thing by SOURCE (the eye row's `meta.source` on the tape), the blind-surprise twin's own count
    _src = {int(r["seq"]): ((r.get("meta") or {}).get("source")) for r in tape if r.get("sense") == "eye"}
    M["SURPRISE"] = _vl.surprise_mark(live, st, "SURPRISE" in decl, source_of=_src, twin_status=TW.get("blind-surprise"))   # §19.1 (builder B's confirmed glances)
    M["COARSE"] = _vl.coarse_mark(allw, (TW.get("blind-coarse", {}).get("exam") or {}).get("ask_all_words"), bool((getattr(g, "gaze", None) or {}).get("coarse")))   # §19.4
    M["QUESTION"] = _vl.question_mark(live, tape, st, float(a.hours), "QUESTION" in decl)   # §19.7 (builder C's question rows; the world's `answering` rows)
    M["SENTENCE"] = _vl.sentence_mark(tape, st, "SENTENCE" in decl)                        # §19.8 + the ceiling clause (the world's own pair skew)
    # §19.9 HANDS (builder F): the reader ASKS the hands' rendered canvases (up to 50) through the unblinded twin's organism and grades
    # the program's own shape; the shuffled-shelf twin = the same asks with the shapes permuted by a fixed rng.
    _hrows = _vl.hands_rows(tape)[:50]; _hrecog = None
    if "HANDS" in decl and _hrows:
        try:
            from tools import self_exam as _se3
            from genome import ask as _gask3
            _g3, _org3, _led3, _L3 = _se3.load_snapshot(twins_dir / "unblinded-1", genome_path)
            _Lw3 = _led3["words"]; _h3 = _org3.state_hash()
            _answers = []
            for r in _hrows:
                res = _org3.recall_many("sight", _gask3.glance_picture(root / "tape" / r["payload"], _g3))
                _answers.append("/".join(sorted(_Lw3.get(res["cell"], set()))) if res.get("cell") is not None else None)
            assert _org3.state_hash() == _h3
            _shapes = [(r.get("meta") or {}).get("shape") for r in _hrows]
            _perm = np.random.default_rng(7).permutation(len(_shapes))
            _hrecog = {"asked": len(_hrows), "hits": sum(1 for a, s_ in zip(_answers, _shapes) if a == s_),
                       "shuffled_hits": sum(1 for a, k in zip(_answers, _perm) if a == _shapes[int(k)])}
        except Exception as e:
            _hrecog = {"asked": 0, "error": repr(e)}
    M["HANDS"] = _vl.hands_mark(st, _hrows, _hrecog, "HANDS" in decl)
    M["THREAD"] = _vl.thread_mark(R["ALIVE"], st, bool((decl.get("THINK") or {}).get("threaded")))   # §19.2 (builder E's thinking thread)
    M["PLANTS"]["predict_file_pair"] = {"sight_road_rows": live_pred["sight_road_rows"], "rule_rows_filed": live_pred["filed"], "rule_rows_scored": live_pred["scored"], "status_predictions_filed": st.get("predictions_filed")}
    M["PLANTS"]["park_unanswerable_want"] = {"sight_only_rows": len(sight_only), "first_seq": sight_only[0]["seq"] if sight_only else None, "parked_total": parked}
    M["PLANTS"]["belief_contradiction"] = {"clash_rows": kinds.get("clash", 0), "extension_rows": kinds.get("extension", 0)}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "reported: no-park twin parked %s vs live %d" % (TW.get("blind-park", {}).get("parked"), parked)}
    # BANDS (reported): the drawn bands from gate G-a's line in the genome; photographs from the recorded runs if present
    bands = {"drawn_gate_Ga_line": next((l for l in base_text.splitlines() if "gate G-a wrote" in l), None)}
    for name, pth in (("eye_photo_g1_gate", ROOT / "runs" / "eye-photo-g1" / "gate.json"),):
        bands[name] = json.loads(pth.read_text()) if pth.exists() else "not on disk"
    M["BANDS"] = bands
    graded = ["i_knows", "ii_meeting_real", "iii_growth_matters", "iv_grows_alone", "v_retention", "vi_knows_unknown", "vii_replay", "x_gaze_finds_thing", "xi_gaze_earns_place", "MODULATION"] + (["ix_not_luck"] if "ix_not_luck" in M else [])
    graded += [k for k in ("viii_cost", "W3_2_rules", "W3_1_beliefs", "DOOR", "PARK", "ACT", "SOUND", "SIZING", "GRADE", "SELF", "SURPRISE", "COARSE", "QUESTION", "SENTENCE", "HANDS", "THREAD") if k in M and M[k].get("graded")]   # §18: graded only when the life declares them; (viii) only when STATUS carries the per-canvas unit
    failed = [k for k in graded if not M[k].get("pass")] + ([] if R["ALIVE"]["pass"] else ["ALIVE"]) + ([] if M["TWINS"]["random_gaze_loses_xi"]["pass"] else ["TWINS.random_gaze"])
    R["marks"] = M; R["marks_failed"] = failed; R["verdict"] = "PASS" if not failed else "FAIL"
    R["seconds_total"] = round(time.perf_counter() - T0, 1)
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str))
    write_verdict(out, R)
    print(f"VERDICT {R['verdict']} — failed: {failed or 'none'} — {out} ({R['seconds_total']} s)", flush=True)
    return 0


def w3_1_beliefs(bel_rows: List[dict], decl: dict, heard: Sequence[str]) -> dict:
    """W3-1 (PREREG §18) as amended 2026-09-22: a word carries ONE raw `belief` row, plus one more for every clash — genome/think.py's
    clash law (decision 5) FIRST writes the new observation as its own fresh `belief` row and then a `clash` row naming
    [standing_line, new_line], so the extra row is the clash's second side by design. Every belief row beyond a word's first must
    be NAMED as `clashes[1]` of a clash row of that word; an unnamed extra row is life 2's dedupe defect (1,473 rows, all kind
    belief, no clash) and still fails. Revisits > 0 as before. Found on the 2 h smokes of the six 8 h lives (L4 max 2, L5/seam-1
    max 4 — all 24 extra rows named by a clash, measured on the live files 2026-09-22 10:1x +04)."""
    kinds: Dict[str, int] = {}
    per_word_beliefs: Dict[str, List[int]] = {}
    named: Dict[str, set] = {}
    for r in bel_rows:
        k = str(r.get("kind", "belief")); kinds[k] = kinds.get(k, 0) + 1
        w = str(r.get("word"))
        if k == "belief":
            per_word_beliefs.setdefault(w, []).append(int(r.get("line", -1)))
        elif k == "clash":
            c = r.get("clashes")
            if isinstance(c, list) and len(c) == 2:
                named.setdefault(w, set()).add(int(c[1]))
    unaccounted = [[w, ln] for w, lines in per_word_beliefs.items() for ln in lines[1:] if ln not in named.get(w, set())]
    max_per_word = max((len(v) for v in per_word_beliefs.values()), default=0)
    extra = sum(len(v) - 1 for v in per_word_beliefs.values())
    graded = "BELIEF" in decl
    return {"graded": graded, "pass": graded and bool(bel_rows) and not unaccounted and kinds.get("revisit", 0) > 0,
            "rows": len(bel_rows), "kinds": kinds, "standing_words": len(per_word_beliefs), "words_heard": len(heard),
            "max_belief_rows_per_word": max_per_word, "extra_belief_rows": extra, "clash_rows": kinds.get("clash", 0), "unaccounted": unaccounted,
            "bar": "every raw `belief` row beyond a word's first is the named second side of a `clash` row of that word (the clash law writes it; "
                   "life 2's 1,473 unnamed rows fail) · revisits > 0 · clashes reported"}


def grade_modulation_windows(windows: dict, min_showings: int = 10):
    """PREREG §18 addendum 4 (2026-09-22): a window is graded over the NEW things that reached `min_showings` showings — «settled by
    the 10th showing» cannot be read on a thing shown fewer times (the PLANT is shown 5 times by design; on every rung of the ladder
    window 3's only new thing was the plant and the mark read FAIL on a bar above its ceiling, #228 (b)). A window whose new things
    ALL fall under the floor is reported NOT GRADABLE (skipped), never FAIL. Returns (graded_fixed, graded_regime, skipped)."""
    graded, graded_regime, skipped = [], [], []
    for w, rec in windows.items():
        news_all = {t: v for t, v in rec["per_thing"].items() if v["kind"] == "new"}
        if not news_all:
            continue
        news = [v for v in news_all.values() if v.get("n_showings", 0) >= min_showings]
        if not news:
            skipped.append({"window": w, "new": len(news_all), "new_under_min": sorted(news_all), "gradable": False,
                            "reason": f"no new thing reached {min_showings} showings (the plant is shown 5 times by design) — settle cannot be read; not gradable"})
            continue
        sp = sum(v["spike"] for v in news); st = sum(v["settled"] for v in news)
        graded.append({"window": w, "new": len(news), "spike": sp, "settled": st, "pass": sp * 2 > len(news) and st * 2 > len(news)})
        spr = sum(v["spike_regime"] for v in news); str_ = sum(v["settled_regime"] for v in news)
        graded_regime.append({"window": w, "new": len(news), "spike": spr, "settled": str_, "pass": spr * 2 > len(news) and str_ * 2 > len(news)})
    return graded, graded_regime, skipped


def null_clears(per: dict, band):
    """§18 addendum 4 (b2): the fake-boundary NULL clears when the MAJORITY of continuing things' spike ratios sit under the regime band
    (the spike rule's own majority). The band is the 95th percentile of exactly these ratios, so `all()` over eleven things failed by
    construction ~43 % of the time (L1: ten of eleven under 2.27, «wave» 3.73). Returns (pass, share_under_band); (None, None) when
    there is no band or nothing to read."""
    vals = [v for v in per.values() if v is not None] if per else []
    if band is None or not vals:
        return None, None
    share = sum(1 for v in vals if v < band) / len(vals)
    return share > 0.5, share


def iv_refusals(c: dict) -> dict:
    """(iv)'s refusals, §18 addendum 4: every CAP refusal counts (budget · nmax · frozen); `redundant` is the ordinary no-birth path and is
    printed only. g5-seam-1 refused 1,988 births at NMAX (its 2,000 sight ids spent by hour ~6) while the old bar read `births_refused_budget`
    alone and PASSED — the plant could not be learned and no surface said so."""
    b = int(c.get("births_refused_budget", 0)); n = int(c.get("births_refused_nmax", 0)); f = int(c.get("births_refused_frozen", 0))
    return {"budget": b, "nmax": n, "frozen": f, "redundant": int(c.get("births_refused_redundant", 0)), "caps_total": b + n + f}


def w3_2_reason(eligible_n: int, reached_n: int, wrong: list) -> str:
    """The W3-2 cluster control's reason names the clause that failed (§18 addendum 4): «VOID by the wiring» is the REACH floor only
    (life 3a's shape — one word of 21 by a coincidence of ids); a cluster under .5 own share is a real reading of the rules."""
    fails = []
    if eligible_n < 5:
        fails.append(f"fewer than 5 eligible words ({eligible_n})")
    if reached_n < 5:
        return f" VOID by the wiring: rules reached {reached_n} of {eligible_n} eligible words (floor 5)" + (f"; {len(wrong)} rule(s) under .5 own share" if wrong else "")
    if wrong:
        fails.append("own-cells clause: " + ", ".join(f"{x['word']} {x['own_share']:.3f}" for x in wrong) + " (bar .5 of the word's own cells)")
    return (" FAIL on the " + "; ".join(fails)) if fails else ""


def viii_cost(status: dict, solo_ms: float, unblinded_ms: float, cpu_ns) -> dict:
    """(viii) COST, G4-7, in ONE unit (#162 — found 2026-09-22 on the six 2 h smokes: STATUS.mind_ms_median_1min is the median of
    `mind.consume(row)` over EVERY tape row — ear, outcome, body rows included — while the probe is all rows' time ÷ CANVASES; 0.168 ms
    «vs» 13 ms passed in every life to date). The live number is STATUS.mind_ms_per_canvas_1min (creature/body.py writes it from
    2026-09-22); a status that carries only the per-row median is NOT GRADED — never PASS."""
    rss = status.get("rss_mb"); per_canvas = status.get("mind_ms_per_canvas_1min"); per_row = status.get("mind_ms_median_1min")
    graded = per_canvas is not None
    m = {"graded": graded, "pass": None, "rss_mb_last_status": rss, "live_ms_per_canvas": per_canvas, "live_mind_ms_median_per_row": per_row,
         "solo_ms_per_canvas_replay": solo_ms, "unblinded_replay_ms_under_workers": unblinded_ms,
         "cpu_hours": round(cpu_ns / 3.6e12, 3) if cpu_ns else None,
         "bar": "G4-7: live ms per CANVAS (STATUS.mind_ms_per_canvas_1min) ≤ 2× the solo probe's · RSS < 2 GB (the 24 h CPU bill printed)",
         "reason": ""}
    if not graded:
        m["reason"] = ("STATUS carries only the per-row median (mind_ms_median_1min), which is not the probe's unit (ms per canvas, #162): "
                       "not graded — every (viii) PASS before 2026-09-22 was a reading of this instrument")
        return m
    m["pass"] = (rss is not None and rss < 2048) and (solo_ms is None or solo_ms <= 0 or per_canvas <= 2 * solo_ms)
    return m


def write_verdict(out: Path, R: dict) -> None:
    M = R["marks"]; A = R["ALIVE"]
    def pf(x): return "PASS" if x else "FAIL"
    def gv(m): return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"   # hoisted 2026-09-22: (viii) renders through it before its old definition below
    L = [f"# G4 VERDICT — {R['verdict']}", "", f"root `{R['root']}` · genome `{R['genome']}` (sha {R['genome_sha']}) · read {R['at']} by `{R['reader']}` (PREREG §5 as amended; the reader's rules §16) · {R['hours']} h",
         "", "| mark | bar | reading | verdict |", "|---|---|---|---|",
         f"| ALIVE | {A['bar_hours']} h under the unit, NRestarts 0, every counter moved every hour, no sense dead > 60 s | {A['hours_on_tape']} h on tape · moved every hour {A['every_counter_moved_every_hour']} · max gap eye/ear {A['max_gap_s_eye_ear']} s · sense restarts {A['sense_restarts']} · crashes {A['crashes']} · NRestarts {A['nrestarts']} | {pf(A['pass'])} |",
         # edit: Claude (Fable 5.1), 2026-09-22 11:0x +0400 — compare() returns None when EVERY row matches; the old rendering printed "vs live None", which reads as unmeasured (the advisor's read, 2026-09-22 10:5x)
         f"| REPLAY / (vii) | byte-identical mind rows; the plant caught | vs live {'identical' if M['vii_replay']['vs_live'] is None else 'DIVERGED at ' + str(M['vii_replay']['vs_live'])} · two replays {'identical' if M['vii_replay']['two_replays'] is None else 'DIVERGED at ' + str(M['vii_replay']['two_replays'])} · {M['vii_replay']['mind_rows']} rows · plant at seq {M['vii_replay']['plant_seq']} caught {M['vii_replay']['plant_caught']}{(' · masked ' + ','.join(M['vii_replay']['hash_masked']) + ' (reader ' + str(R.get('reader_commit'))[:7] + ' ≠ life ' + str(R.get('life_commit'))[:7] + ')') if M['vii_replay'].get('hash_masked') else ''} | {pf(M['vii_replay']['pass'])} |"]
    i = M["i_knows"]; L.append(f"| (i) | {i['bar']} | Q1 {i['Q1']:.3f} Q2 {i['Q2']:.3f} Q3 {i['Q3']:.3f} Q4 {i['Q4']:.3f} (chance {i['chance_Q1']}; all words Q1 {i['all_words']['Q1']:.3f}) | {pf(i['pass'])} |")
    m = M["ii_meeting_real"]; L.append(f"| (ii) | {m['bar']} (all 16 words) | T-shuffle Q1 {m['T_shuffle_Q1']} · T-nowire Q1 {m['T_nowire_Q1']} | {pf(m['pass'])} |")
    m = M["iii_growth_matters"]; L.append(f"| (iii) | {m['bar']} | T-frozen-10 Q1 {m['T_frozen_10_Q1']} (cells {m['T_frozen_10_cells']}) vs Q1 {m['Q1']:.3f}; the 50-cell twin {m['T_frozen_50_Q1']} | {pf(m['pass'])} |")
    m = M["iv_grows_alone"]; L.append(f"| (iv) | {m['bar']} | born {m['cells_born']} · refused at caps {m['refused']['caps_total']} (budget {m['refused']['budget']} · nmax {m['refused']['nmax']} · frozen {m['refused']['frozen']}; redundant {m['refused']['redundant']}, not a refusal) (arrivals {m['arrivals']}, budget left {m['budget_left']}) · pruned {m['edges_pruned']}/{m['edges_born']} = {100*m['pruned_share']:.1f} % (cross-thing born {m['edges_cross']['born']} / pruned {m['edges_cross']['pruned']}) · disuse {m['removed_for_disuse']} | {pf(m['pass'])} |")
    m = M["v_retention"]; L.append(f"| (v) | {m['bar']} | " + ("; ".join(f"w{p['window']}: {p['before']:.3f} → first {p['first_after']:.3f} → last {p['last_in_window']:.3f} ({p['drop_pp']:+.1f} pp drop)" for p in m['pairs']) or m['note']) + f" | {pf(m['pass'])} |")
    m = M["vi_knows_unknown"]; L.append(f"| (vi) | {m['bar']} | plant zog answered {m['plant_zog']['answered_rate']:.2f} (as {m['plant_zog']['answered_as']}, abstain {m['plant_zog']['abstain']}) · null vex abstains {m['null_vex']['abstain_rate']:.2f} (answered as {m['null_vex']['answered_as']}) · Q5 {m['Q5_spiral_abstain']:.2f} · false {m['false_abstention']:.3f} | {pf(m['pass'])} |")
    m = M["viii_cost"]; L.append(f"| (viii) COST | {m['bar']} | live {m['live_ms_per_canvas']} ms a canvas (per-row median {m['live_mind_ms_median_per_row']} ms) vs solo {m['solo_ms_per_canvas_replay']} ms a canvas · RSS {m['rss_mb_last_status']} MB · CPU {m['cpu_hours']} h{(' · ' + m['reason']) if m.get('reason') else ''} | {gv(m)} |")
    if "ix_not_luck" in M:
        m = M["ix_not_luck"]; L.append(f"| (ix) | {m['bar']} | rank {m['rank_of_own']} of {m['of']} (own {m['own_composite']}; best random {m['best_random']}) | {pf(m['pass'])} |")
    m = M["x_gaze_finds_thing"]; L.append(f"| (x) | {m['bar']} | gaze {m['gaze_rate']:.3f} vs random {m['random_rate']:.3f} (×{m['ratio']}) | {pf(m['pass'])} |")
    m = M["xi_gaze_earns_place"]; L.append(f"| (xi) | {m['bar']} | Q1 gaze {m['Q1_gaze']:.3f} − one-glance {m['Q1_one_glance']} (first-fixation-only {m['Q1_first_fixation_only']}; random-gaze {m['Q1_random_gaze']}) | {pf(m['pass'])} |")
    m = M["MODULATION"]; reg = m.get("regime", {}) or {}; nb = m.get("null_fake_boundary_w0", {}) or {}
    L.append(f"| MODULATION | {m['bar']} | windows(regime) {m.get('graded_windows_regime')} · windows(fixed) {m['graded_windows']} · null(regime) {nb.get('no_spike_regime')} · null(fixed) {nb.get('no_spike')} "
             f"· regime band {reg.get('null_band_95')} (n={reg.get('null_ratio_samples')}, share {reg.get('null_share_within_band')}) · regime settle bar {reg.get('settle_bar_err_95')} "
             f"· not gradable (§18 add. 4: no new thing reached 10 showings) {m.get('not_gradable_windows')} "
             f"· no-predict twin max err {m['no_predict_twin_err']} · fixed-bar record {pf(m.get('pass_fixed_bars_record'))} · {m.get('reason','')} | {pf(m['pass'])} |")
    L.append(f"| TWINS random-gaze | loses (xi) | margin {M['TWINS']['random_gaze_loses_xi']['margin']} | {pf(M['TWINS']['random_gaze_loses_xi']['pass'])} |")
    def gv(m): return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"
    m = M["W3_2_rules"]; L.append(f"| W3-2 rules | {m['bar']} | filed {m['live']['filed']} (induce {m['live']['induce']}, deduce {m['live']['deduce']}, refused {m['live']['refused']}) · scored {m['live']['scored']} · accuracy {m['live']['accuracy']} · words {m['live']['words']} · T-shuffle scored {m['T_shuffle']['scored']} acc {m['T_shuffle']['accuracy']} · parked rules {m['parked_rules']} · clusters: rules reached {m['cluster_control'].get('words_with_rules')} of {m['cluster_control'].get('eligible_words')} eligible words (of {m['cluster_control'].get('words')}), wrong-cell rules {m['cluster_control'].get('wrong_cell_rules')} {m['reason']} | {gv(m)} |")
    m = M["DOOR"]; L.append(f"| DOOR | {m['bar']} | pictures {m['pictures']} (rows {m['folder_rows']}) · words {len(m['folder_words'])} · sight-only {m['sight_only_rows']} (first seq {m['sight_only_first_seq']}) · recognition {m['recognition_of_seen_pictures']} {m['reason']} | {gv(m)} |")
    m = M["W3_1_beliefs"]; L.append(f"| W3-1 beliefs | {m['bar']} | rows {m['rows']} · kinds {m['kinds']} · standing words {m['standing_words']} of {m['words_heard']} heard · max belief rows per word {m['max_belief_rows_per_word']} · extra belief rows {m['extra_belief_rows']} vs clash rows {m['clash_rows']} · unaccounted {m['unaccounted']} | {gv(m)} |")
    m = M["PARK"]; L.append(f"| PARK | {m['bar']} | parked {m['parked']} of {m['thinks']} thinks (rules {m['parked_rules']}) — {m['reason']} | {gv(m)} |")
    # edit: Claude (Fable 5.1), 2026-09-22 19:3x +0400 — THE ONE LIFE's marks (PREREG §19)
    for _k in ("ACT", "SOUND", "SIZING", "GRADE", "SELF", "SURPRISE", "COARSE", "QUESTION", "SENTENCE", "HANDS", "THREAD"):
        if _k in M:
            m = M[_k]
            if _k == "THREAD":
                body = f"max sense gap {m.get('max_gap_s')} s (per hour {m.get('gaps_per_hour')}) · thinks {m.get('thinks')} waits {m.get('think_waits')} (share {m.get('waits_share')}, {m.get('think_wait_ms')} ms) · think ms last {m.get('think_ms_last')} median {m.get('think_ms_median')} — {m['reason']}"
            elif _k == "HANDS":
                body = f"runs {m.get('runs')} (by program {m.get('runs_by_program')}; no road {m.get('hands_no_road')}) · asked {m.get('asked')} recognised {m.get('recognised_share')} vs shuffled shelf {m.get('shuffled_share')} · touch {m.get('touch_events')} smell {m.get('smell_events')} — {m['reason']}"
            elif _k == "QUESTION":
                body = f"questions {m.get('questions')} (forms {m.get('forms')}; needed {m.get('needed')}) · answered by the world {m.get('answered_rows')} (share {m.get('answered_share')}) · STATUS written {m.get('status_written')} answered {m.get('status_answered')} — {m['reason']}"
            elif _k == "SENTENCE":
                body = f"missions {m.get('missions')} · the world's max pair lift {m.get('max_lift')} on «{m.get('max_pair')}» · frames filed {m.get('frames_filed')} scored {m.get('frames_scored')} true {m.get('frames_true')} (precision {m.get('precision')}) · said {m.get('said')} heard yes {m.get('heard_yes')} no {m.get('heard_no')} — {m['reason']}"
            elif _k == "SURPRISE":
                body = (f"overall confirmed share {m.get('overall_share')} over {m.get('canvases')} canvases · maker things rising {m.get('things_rising')} of {m.get('things_graded')} (null mean {m.get('null_mean')} p95 {m.get('null_p95')}) · first 500 {m.get('first_500')} → last 500 {m.get('last_500')} (rise {m.get('rise_first_to_last_500')}) · by source {m.get('by_source')} · printed not graded {len(m.get('printed_not_graded') or {})} things · blind-surprise twin confirmed {m.get('twin_confirmed')} · STATUS confirmed {m.get('status_confirmed')} surprised {m.get('status_surprised')} — {m['reason']}")
            elif _k == "COARSE":
                body = f"Q1 all words {m.get('q1_live')} vs blind-coarse {m.get('q1_blind_coarse')} · house {m.get('house_live')} vs {m.get('house_blind_coarse')} (prediction held {m.get('house_prediction_held')}) · cup {m.get('cup_live')} vs {m.get('cup_blind_coarse')} — {m['reason']}"
            elif _k == "GRADE":
                body = f"null graded {m['null_graded']} · plant answered {m.get('plant_answered_rate')} graded {m['plant_graded']} · hedge rate on seen words {m['hedge_rate']} — {m['reason']}"
            elif _k == "SELF":
                body = f"self beliefs {m['self_beliefs']} (citing two body rows {m['self_beliefs_citing_two_body_rows']}; words {m['self_words']}) · self thinks {m['self_thinks']} · body rows {m['body_rows']} · skipped for backlog {m['think_skipped_for_backlog']} — {m['reason']}"
            elif _k == "ACT":
                body = f"mind-chosen {m['mind_chosen']} of {m['game_outcomes']} (share {m['mind_share']}) · mismatches journal {m['mismatches_journal']} status {m['mismatches_status']} · census {m['census']} max {m['max_share']} zero {m['zero_acts']} · shuffled twin diverged {m.get('shuffled_twin_diverged')} · reward mean {m['reward_mean']} success/episode {m['success_per_episode']} (random null {m['random_null_success']}) — {m['reason']}"
            elif _k == "SOUND":
                body = f"ear-sound rows {m['ear_sound_rows']} · consumed {m['consumed']} · errors {m['errors']} · STATUS sound_events {m['status_sound_events']} — {m['reason']}"
            else:
                body = f"born {m['sight_born']} of {m['sight_nmax']} · prediction {m['prediction']} · refused at NMAX {m['births_refused_nmax']} · series/h {m['series_sight_births_per_hour']} · plant shown {m['plant_shown_moments']} birthed {m['plant_sight_births']} — {m['reason']}"
            L.append(f"| {_k} | {m['bar']} | {body} | {gv(m)} |")
    L.append(f"| TWINS no-sleep / no-curiosity / no-park | (v) / door / PARK | {M['TWINS']['no_sleep_v']} · {M['TWINS']['no_curiosity']['reason']} · {M['TWINS']['no_park']['reason']} | not graded |")
    L += ["", "## Twins (each a replay of the same tape blind to one gene; Q1 on all 16 words, the seen-words Q1 beside it)", "", "| twin | Q1 (all) | Q1 (seen) | composite (all) | cells |", "|---|---|---|---|---|"]
    for b in BLINDS:
        t = M["TWINS"][b]; L.append(f"| {b} | {t['Q1']} | {t['Q1_seen']} | {t['composite']} | {t['cells']} |")
    L += ["", "## Plants", "", json.dumps(M["PLANTS"], indent=1, default=str), "", "## BANDS (reported, never gating)", "", json.dumps(M["BANDS"], indent=1, default=str)[:3000],
          "", "## ALIVE per hour", "", json.dumps(A["per_hour"]), "", f"failed: {R['marks_failed'] or 'none'} · {R['seconds_total']} s"]
    (out / "VERDICT.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
