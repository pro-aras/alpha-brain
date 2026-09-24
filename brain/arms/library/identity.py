"""identity.py — B1-PREREG §3.1's twice-and-planted test for arm D, as a driver the seat can point at any tape.

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:00 +0400 — one process = one run of D over the first N rows of a tape,
through brain.protocol.HarnessContract exactly as the runner calls it (TEACH/ARRIVAL -> fit_event; training ASK ->
answer(learn=True) then fit_event; FEEDBACK -> fit_event with the valence the harness derives from D's own prior
answer; SLEEP -> sleep; a TEST-sitting ASK -> answer(learn=False), frozen). It writes answers.jsonl (every ASK's
answer, in tape order) and state_sha.json (the state_sha after rows 500, 1,000, 1,500, 2,000 — or the rows named),
and can snapshot at a row and RESUME from such a snapshot in a new process.

  python -m brain.arms.library.identity --tape T.jsonl --cache C --out DIR [--rows 2000] [--checkpoints 500,1000,1500,2000]
         [--snapshot-at 1000] [--resume-from DIR_OF_A_SNAPSHOT] [--budget 3000] [--max-size 20]

«Event» = a tape row, counted from 1 in file order; the checkpoint after event k is taken after row k is processed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from brain.protocol import Answer, HarnessContract, canonical_json, make_arm

from .arm import LibraryArm


def read_tape(path: Path, rows: int) -> List[Dict[str, Any]]:
    out = []
    with path.open() as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
            if len(out) >= rows:
                break
    return out


def run(tape: List[Dict[str, Any]], cache: str, out: Path, checkpoints: List[int], snapshot_at: Optional[int],
        resume_from: Optional[Path], budget: int, max_size: int, seed: int) -> Dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    cfg = {"cache_dir": cache, "run_dir": str(out / "run"), "seed": seed, "interpreter": sys.executable,
           "candidates_per_sleep": budget, "max_size": max_size}
    arm = make_arm(LibraryArm, seed, cfg)
    start = 0
    pending: Dict[int, Dict[str, Any]] = {}
    in_test = False
    shas: Dict[str, str] = {}
    answers_path = out / "answers.jsonl"
    if resume_from is not None:
        ck = json.loads((resume_from / "checkpoint.json").read_text())
        arm.load(resume_from / "snapshot.json")
        start = int(ck["event"])
        pending = {int(k): v for k, v in ck["pending"].items()}
        in_test = bool(ck["in_test"])
        if arm.state_sha() != ck["state_sha"]:
            raise SystemExit(f"resume: the loaded snapshot hashes {arm.state_sha()} != {ck['state_sha']}")
    with answers_path.open("w") as af:
        for i in range(start, len(tape)):
            row = tape[i]
            kind = row["kind"]
            if kind == "TEACH":
                HarnessContract.teach(arm, row)
            elif kind == "ARRIVAL":
                HarnessContract.arrival(arm, row)
            elif kind == "SLEEP":
                HarnessContract.sleep(arm, row)
            elif kind == "TEST_BEGIN":
                in_test = True
            elif kind == "TEST_END":
                in_test = False
            elif kind == "ASK":
                if in_test:
                    ans = HarnessContract.test_ask(arm, row)
                else:
                    ans = HarnessContract.training_ask(arm, row)
                    pending[int(row["seq"])] = {"answer": ans.to_dict(), "kind": row["payload"]["answer_kind"]}
                af.write(canonical_json({"seq": row["seq"], "answer": ans.to_dict()}) + "\n")
            elif kind == "FEEDBACK":
                p = pending.pop(int(row["payload"]["ask_seq"]), None)
                prior = Answer.from_dict(p["answer"]) if p else Answer(kind="SILENT")
                HarnessContract.feedback(arm, row, prior, p["kind"] if p else "NAME")
            ev = i + 1
            if ev in checkpoints:
                shas[str(ev)] = arm.state_sha()
            if snapshot_at is not None and ev == snapshot_at:
                snap = out / "snap"
                snap.mkdir(exist_ok=True)
                arm.snapshot(snap / "snapshot.json")
                (snap / "checkpoint.json").write_text(canonical_json({
                    "event": ev, "pending": {str(k): v for k, v in pending.items()}, "in_test": in_test,
                    "state_sha": arm.state_sha()}))
    (out / "state_sha.json").write_text(json.dumps(shas, sort_keys=True, indent=1))
    return shas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tape", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=2000)
    ap.add_argument("--checkpoints", default="500,1000,1500,2000")
    ap.add_argument("--snapshot-at", type=int, default=None)
    ap.add_argument("--resume-from", default=None)
    ap.add_argument("--budget", type=int, default=3000)
    ap.add_argument("--max-size", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261001)
    a = ap.parse_args(argv)
    tape = read_tape(Path(a.tape), a.rows)
    cks = [int(x) for x in a.checkpoints.split(",") if x]
    shas = run(tape, a.cache, Path(a.out), cks, a.snapshot_at, Path(a.resume_from) if a.resume_from else None,
               a.budget, a.max_size, a.seed)
    print(json.dumps(shas, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
