# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:02 +0400 — B1-PREREG §3.1 for arm D (the non-torch leg): the first 2,000
# events of a tape run TWICE in separate processes (answers.jsonl byte-identical; state_sha identical at 500 /
# 1,000 / 1,500 / 2,000); a PLANTED copy whose first TEACH row at or after event 1,234 points to a different
# cache row (its sha recomputed — a legitimate tape) must be CAUGHT (identical at 500 and 1,000, different at
# 1,500 and 2,000; the first differing answer, if any, at or after the planted row); a snapshot at 1,000 loaded
# in a NEW process and continued must reach event 2,000's state_sha. And, as a FINDING only, the same run with
# 8 BLAS threads. The tape here is a toy tape on the creature's own front (toy_world.py's real renderings) —
# the real tape of seed 20261001 does not exist yet; the driver (brain/arms/library/identity.py) takes any tape.
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

from brain.protocol import canonical_json, make_row, op_row

from .toy_world import PLANT_CHARS, PLANT_NAMES, TOY_DIR, load_rows, row

HAVE_TOYS = (TOY_DIR / "rows.json").exists()
PLANT_AT = 1234
BUDGET = 1500
RESULTS = TOY_DIR / "results"


def build_tape(rows: Dict[str, int], n_rows: int = 2000) -> List[dict]:
    """Blocks of TEACH, NAME asks and PLUS1 asks (each ask followed by its FEEDBACK), a SLEEP after every 500th
    row, and one frozen TEST sitting near the end — TEACH rows continue past event 1,234 (so the plant lands)."""
    tape: List[dict] = []
    seq = 1
    b = 0

    def add(kind, payload, item="x"):
        nonlocal seq
        tape.append(make_row(seq, kind, "id", item, payload))
        seq += 1
        if kind != "SLEEP" and len(tape) % 500 == 499:      # every 500th row is a SLEEP
            tape.append(make_row(seq, "SLEEP", "id", "-", {"steps": 0}))
            seq += 1

    while len(tape) < n_rows:
        for j in range(8):
            i = (b * 8 + j) % 16
            add("TEACH", {"glance_row": row(rows, PLANT_CHARS[i], b + j, b % 6), "name": PLANT_NAMES[i]})
        for j in range(8):
            i = (b * 5 + j) % 16
            s = seq
            add("ASK", {"cues": ["NAME"], "operands": [op_row(row(rows, PLANT_CHARS[i], b + j + 1, (b + 1) % 6))],
                        "candidate_rows": None, "answer_kind": "NAME"})
            add("FEEDBACK", {"ask_seq": s, "right": PLANT_NAMES[i]})
        for j in range(4):
            i = (b * 3 + 2 * j) % 15
            s = seq
            add("ASK", {"cues": ["PLUS1"], "operands": [op_row(row(rows, PLANT_CHARS[i], b + j + 2, (b + 2) % 6))],
                        "candidate_rows": None, "answer_kind": "NAME"})
            add("FEEDBACK", {"ask_seq": s, "right": PLANT_NAMES[i + 1]})
        if b == 30:
            add("TEST_BEGIN", {"sitting": "T_toy"})
            for i in range(0, 15, 3):
                add("ASK", {"cues": ["PLUS1"], "operands": [op_row(row(rows, PLANT_CHARS[i], i, 5))],
                            "candidate_rows": None, "answer_kind": "NAME"})
            add("TEST_END", {"sitting": "T_toy"})
        b += 1
    return tape[:n_rows]


def plant(tape: List[dict], rows_total: int) -> (List[dict], int):
    out = [dict(r) for r in tape]
    for i in range(PLANT_AT - 1, len(out)):
        r = out[i]
        if r["kind"] == "TEACH":
            p = dict(r["payload"])
            p["glance_row"] = (int(p["glance_row"]) + 7) % rows_total
            out[i] = make_row(r["seq"], "TEACH", r["phase"], r["item"], p)   # its sha recomputed
            return out, int(r["seq"])
    raise AssertionError("no TEACH row at or after event 1,234 — the plant cannot land (report §4 R3)")


def run_leg(tape_path: Path, out: Path, extra: List[str], env_extra: Dict[str, str] = None) -> Dict[str, str]:
    env = dict(os.environ)
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    env.update(env_extra or {})
    cmd = [sys.executable, "-m", "brain.arms.library.identity", "--tape", str(tape_path), "--cache",
           str(TOY_DIR / "cache"), "--out", str(out), "--rows", "2000", "--budget", str(BUDGET), "--max-size", "16"] + extra
    subprocess.run(cmd, check=True, env=env, cwd=str(Path(__file__).resolve().parents[3]),
                   stdout=subprocess.DEVNULL)
    return json.loads((out / "state_sha.json").read_text())


@unittest.skipUnless(HAVE_TOYS, "the toy cache is absent — build it: python3 -m tests.brain.arms_library.toy_world")
class TestIdentity(unittest.TestCase):
    def test_twice_planted_resume(self):
        rows = load_rows()
        tape = build_tape(rows)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            tp = td / "tape.jsonl"
            tp.write_text("".join(canonical_json(r) + "\n" for r in tape))
            planted, planted_seq = plant(tape, len(rows))
            pp = td / "planted.jsonl"
            pp.write_text("".join(canonical_json(r) + "\n" for r in planted))
            A = run_leg(tp, td / "A", ["--snapshot-at", "1000"])
            B = run_leg(tp, td / "B", [])
            P = run_leg(pp, td / "P", [])
            R = run_leg(tp, td / "R", ["--resume-from", str(td / "A" / "snap")])
            T8 = run_leg(tp, td / "T8", [], {"OPENBLAS_NUM_THREADS": "8", "OMP_NUM_THREADS": "8"})
            a_ans = (td / "A" / "answers.jsonl").read_bytes()
            b_ans = (td / "B" / "answers.jsonl").read_bytes()
            p_lines = (td / "P" / "answers.jsonl").read_text().splitlines()
            a_lines = a_ans.decode().splitlines()
            first_diff = next((json.loads(x)["seq"] for x, y in zip(a_lines, p_lines) if x != y), None)
            r_lines = (td / "R" / "answers.jsonl").read_text().splitlines()
            rec = {"A": A, "B": B, "P": P, "R": R, "threads8": T8, "planted_seq": planted_seq,
                   "first_differing_answer_seq": first_diff, "answers": len(a_lines),
                   "answers_identical_AB": a_ans == b_ans,
                   "threads8_identical": T8 == A and (td / "T8" / "answers.jsonl").read_bytes() == a_ans,
                   "resume_answers_match_A_tail": a_lines[len(a_lines) - len(r_lines):] == r_lines,
                   "budget": BUDGET, "tape_rows": len(tape),
                   "sleeps": sum(1 for r in tape if r["kind"] == "SLEEP")}
            RESULTS.mkdir(parents=True, exist_ok=True)
            (RESULTS / "identity.json").write_text(json.dumps(rec, sort_keys=True, indent=1))
            self.assertTrue(rec["answers_identical_AB"], "answers.jsonl byte-identical across two processes")
            self.assertEqual(A, B)
            self.assertEqual(sorted(A), ["1000", "1500", "2000", "500"])
            self.assertEqual((P["500"], P["1000"]), (A["500"], A["1000"]))
            self.assertNotEqual(P["1500"], A["1500"])
            self.assertNotEqual(P["2000"], A["2000"])
            if first_diff is not None:
                self.assertGreaterEqual(first_diff, planted_seq)
            self.assertEqual(R["2000"], A["2000"], "resume from the snapshot at 1,000 reaches the same state")
            self.assertTrue(rec["resume_answers_match_A_tail"])


if __name__ == "__main__":
    unittest.main()
