"""run.py — TOY C's runner: the five conditions of the law, their records, the SCENE ceiling block, the grade and readings, the gates (docs/research/toys/PREREG-TOY-FRAMES.md §3, §7; AMENDMENT-1).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:06 +0400 — new module, red-first against tests/tools/test_toys_frames_run.py (stage 5a: the unit).

  PYTHONPATH=. python3 -m tools.toys.frames.run gates  [--out DIR]                 G1-G6 on the real copies (a failure STOPS; the unit refuses without a passed GATES.json)
  PYTHONPATH=. python3 -m tools.toys.frames.run unit   [--out DIR] [--only A,B]    the five conditions -> DIR/<name>.json, then DIR/RESULTS.json (resumable)
  PYTHONPATH=. python3 -m tools.toys.frames.run status [--out DIR]

THE FIVE CONDITIONS (law §3): ALPHA4 (alpha4-1's ear rows, every source, seq order), ALPHA4+PLANT (a plant after every 100th moment, then the 60/40 split), ALPHA4+SHUFFLE (words permuted among their own part's
positions, seed 1), SCENE (brain-full's 10,000 scene moments), SCENE+PLANT (every 10th). Every record carries both signed texts' sha256 (the run REFUSES a text that differs: tools/toys/common/prereg.py), the code's git
sha and whether the toy's files differed from it, and the PLANT-gate mode (amend1: AMENDMENT-1 §1). Heavy work goes through /data/dev/swarm/bin/slot (the unit is ONE job; peak RSS and CPU seconds are recorded a condition).
"""
from __future__ import annotations

import argparse
import json
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from tools.toys.common import prereg as PR

from . import compress as CO
from . import evaluate as EV
from . import plants as PL
from . import scene as SC
from . import streams as ST
from . import verdicts as VD

REPO = ST.REPO
ROOT = ST.ROOT
RUNS = ROOT / "runs"
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:20 +0400 — AMENDMENT-2 is a third pinned text (the unit and the gates REFUSE a text that differs from any of the three).
LAW_KEYS = ["frames", "frames_amend1", "frames_amend2"]
GATE_MODE = "amend1"
CONDITIONS: Tuple[Tuple[str, str, Optional[int], str], ...] = (
    ("ALPHA4", "plain", None, "alpha4"),
    ("ALPHA4+PLANT", "plant", PL.PLANT_EVERY["ALPHA4"], "alpha4"),
    ("ALPHA4+SHUFFLE", "shuffle", None, "alpha4"),
    ("SCENE", "plain", None, "scene"),
    ("SCENE+PLANT", "plant", PL.PLANT_EVERY["SCENE"], "scene"),
)


class RunError(Exception):
    pass


def load_streams(copies: Path) -> Dict[str, List[ST.Moment]]:
    a4 = ST.load_moments(sorted((Path(copies) / "alpha4-1" / "tape").glob("*.jsonl")))
    bf = ST.scene_moments(ST.load_moments(sorted((Path(copies) / "brain-full-20261102" / "tape").glob("*.jsonl"))))
    return {"alpha4": a4, "scene": bf}


def code_header() -> Dict[str, object]:
    """Which commit of the toy produced a record, and whether the toy's own files differed from it (a dirty tree is recorded, not hidden)."""
    def git(*a: str) -> str:
        return subprocess.check_output(["git", *a], cwd=REPO, text=True).strip()
    try:
        dirty = git("status", "--porcelain", "--", "tools/toys", "tests/tools", "docs/research/toys")
        return {"toys_git_sha": git("rev-parse", "HEAD"), "toys_tree_dirty": bool(dirty)}
    except (subprocess.CalledProcessError, OSError):
        return {"toys_git_sha": None, "toys_tree_dirty": None}


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True))
    tmp.rename(path)


def peak_rss_kb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def run_condition(name: str, kind: str, every: Optional[int], moments: Sequence[ST.Moment], draws: int, seeds: Sequence[int], header: Dict[str, object]) -> Dict[str, object]:
    t0 = time.process_time()
    train, held = PL.condition_parts(moments, kind, every)
    cond = EV.evaluate_condition(train, held, name=name, draws=draws, web_seeds=seeds, kind=kind)
    cond["header"] = dict(header)
    cond["every"] = every
    cond["cpu_seconds"] = time.process_time() - t0
    cond["peak_rss_kb"] = peak_rss_kb()
    return cond


# ------------------------------------------------------------------------------------------------------------------ SCENE: the ceiling block (law §3 THE CEILING, G1's χ²)
def scene_block(scene_moments: Sequence[ST.Moment], cond: Dict[str, object]) -> Dict[str, object]:
    """G_max from the generator's own code over the held-out part, every rule's G and G(F_oracle) against G_max + 20 (GATE-CEIL: a violation is an INSTRUMENT ERROR, the run STOPS) — gated only when
    G1's χ² fit holds (else G_max is printed as a reading) —, the oracle's G and each rule's recall of it. An utterance the four templates cannot produce in the held-out part is a STOP too."""
    chi = SC.chi2_checks(scene_moments)
    train, held = ST.split(scene_moments)
    sc = CO.Scorer([m.words for m in train], [m.words for m in held])
    bits0 = cond["records"][0]["gain"]["bits0"]
    gm = SC.g_max([m.words for m in held], bits0)
    oracle_all = SC.oracle_frames()
    F_or = frozenset(f for f in oracle_all if sc.train_adjacent(f) > 0)
    g_or = sc.gain(F_or)
    rows = []
    violations = []
    for r in cond["records"]:
        v = SC.ceiling_violation(r["gain"]["G"], gm)
        rows.append({"rule": r["rule"], "seed": r["seed"], "G": r["gain"]["G"], "margin": gm - r["gain"]["G"], "violation": v})
        if v:
            violations.append((r["rule"], r["seed"], r["gain"]["G"]))
    or_violation = SC.ceiling_violation(g_or.G, gm)
    gated = bool(chi["gated"])
    stop = bool(gated and (violations or or_violation))
    if stop:
        raise SC.CeilingStop(f"GATE-CEIL: a G above G_max + 20 on plain SCENE (G_max {gm:.3f}): rules {violations}, oracle {g_or.G:.3f} {'ABOVE' if or_violation else 'ok'} — an instrument error, the run is void")
    return {"chi2": chi, "gmax_gated": gated, "G_max": gm, "bits0": bits0, "expected_form": bits0 - SC.entropy() * len(held), "h_given_length": SC.h_given_length(),
            "entropy": SC.entropy(), "rows": rows, "stop": False,
            "oracle": {"n_frames": len(F_or), "G": g_or.G, "margin": gm - g_or.G, "violation": or_violation, "recall": VD.oracle_recall(cond, oracle_all)}}


# ------------------------------------------------------------------------------------------------------------------ the unit
def build_results(conds: Dict[str, Dict[str, object]], streams: Dict[str, List[ST.Moment]], copies: Path, mode: str) -> Dict[str, object]:
    says = ST.load_says(sorted((Path(copies) / "alpha4-1" / "journal").glob("*.jsonl")))
    return {
        "mode": mode,
        "grade": VD.grade(conds, mode),
        "grade_law": VD.grade(conds, "law"),                                     # what the base text's clause would have graded: a READING (AMENDMENT-1 §6)
        "eye": VD.eye_reading(conds["ALPHA4"], says),
        "overlaps": {name: VD.overlaps(c) for name, c in conds.items()},
        "scene": scene_block(streams["scene"], conds["SCENE"]),
        "plant_tokens": {"ALPHA4": PL.plant_token_occurrences(streams["alpha4"]), "SCENE": PL.plant_token_occurrences(streams["scene"])},
        "section0": ST.section0_counts(streams["alpha4"]),
    }


def run_unit(copies: Path, out: Path, draws: int = 100, seeds: Sequence[int] = EV.SEEDS, only: Optional[Sequence[str]] = None, require_gates: bool = True,
             prereg_root: Optional[Path] = None, mode: str = GATE_MODE, log=print) -> int:
    PR.check(LAW_KEYS, root=prereg_root)                                        # raises PreregError on a text that differs from the co-signed one: nothing is written
    out = Path(out)
    if require_gates:
        g = out / "GATES.json"
        if not g.exists() or not json.loads(g.read_text()).get("passed"):
            raise RunError(f"{g}: no passed gates record — run `gates` first (a gate that fails STOPS the unit)")
    out.mkdir(parents=True, exist_ok=True)
    streams = load_streams(copies)
    header = {**PR.header(LAW_KEYS), **code_header(), "gate_mode": mode}
    conds: Dict[str, Dict[str, object]] = {}
    for name, kind, every, key in CONDITIONS:
        if only and name not in only:
            continue
        path = out / f"{name}.json"
        if path.exists():
            conds[name] = json.loads(path.read_text())
            log(f"[unit] {name}: record on disk, skipped")
            continue
        t0 = time.time()
        cond = run_condition(name, kind, every, streams[key], draws, seeds, header)
        write_json(path, cond)
        conds[name] = cond
        log(f"[unit] {name}: {cond['n_train_moments']} train / {cond['n_held_moments']} held moments, V {cond['V']}, {time.time() - t0:.0f} s wall, {cond['cpu_seconds']:.0f} CPU-s, peak RSS {cond['peak_rss_kb'] / 1024:.0f} MB")
    if len(conds) < len(CONDITIONS):
        log(f"[unit] {len(conds)} of {len(CONDITIONS)} conditions on disk: no RESULTS.json yet")
        return 0
    try:
        res = build_results(conds, streams, copies, mode)
    except SC.CeilingStop as e:
        write_json(out / "STOP.json", {"reason": str(e), "header": header})
        log(f"[unit] STOP: {e}")
        return 2
    res["header"] = header
    write_json(out / "RESULTS.json", res)
    log(f"[unit] RESULTS.json written ({mode}); grade: " + ", ".join(f"{r} {v['gain_verdict']}" for r, v in res["grade"]["alpha4"].items()))
    return 0


def _main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["unit", "gates", "status"])
    ap.add_argument("--copies", default=str(ST.COPIES))
    ap.add_argument("--out", default=str(RUNS))
    ap.add_argument("--only", default="")
    ap.add_argument("--draws", type=int, default=100)
    a = ap.parse_args(list(argv))
    out = Path(a.out)
    if a.cmd == "status":
        for name, *_ in CONDITIONS:
            print(f"{name}: {'on disk' if (out / f'{name}.json').exists() else 'missing'}")
        print(f"RESULTS.json: {'on disk' if (out / 'RESULTS.json').exists() else 'missing'}; GATES.json: {'on disk' if (out / 'GATES.json').exists() else 'missing'}")
        return 0
    if a.cmd == "unit":
        only = [x for x in a.only.split(",") if x] or None
        return run_unit(Path(a.copies), out, draws=a.draws, only=only)
    print("gates: see tools/toys/frames/gates.py", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
