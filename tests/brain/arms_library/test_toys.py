# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 17:01 +0400 — B1-PREREG §5.5 (0b) for arm D: its learning machinery on its
# own toys, outside the tape, on the creature's OWN front (real glyphs through brain/world/build.py; toy_world.py),
# each toy with a planted control (#228): XOR at 100 % (its control: labels that are no function of the pattern
# cannot reach 100 %), and a PLANTED RELATION induced from 3 examples, exact on 10 held-out (its twin: the same 3
# examples with their answers shuffled must NOT be induced — at most 2 of 10). Every row goes through
# brain.protocol.HarnessContract; every test ask is frozen (state_sha unchanged).
#
# The toys' cue marks are toy labels (XOR, PLUS1, PLUS3), outside B1's 14-mark vocabulary on purpose: D is
# mark-agnostic — a mark means only the program D learned for it — and no B1 relation is taught here.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

from brain.protocol import Answer, AnswerKind, HarnessContract, make_arm, make_row, op_row

from brain.arms.library import LibraryArm

from .toy_world import PLANT_CHARS, PLANT_NAMES, TOY_DIR, XOR_CHARS, load_rows, row

HAVE_TOYS = (TOY_DIR / "rows.json").exists()
BUILD_CMD = ("OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -m "
             "tests.brain.arms_library.toy_world /data/dev/brain-runs/tmp/b1-library-toys")
RESULTS = TOY_DIR / "results"
BUDGET = 5000


class Toy:
    def __init__(self, tmp: Path, name: str):
        self.cfg = {"cache_dir": str(TOY_DIR / "cache"), "run_dir": str(tmp / name), "seed": 20260930,
                    "interpreter": "venv", "candidates_per_sleep": BUDGET, "max_size": 16}
        self.arm = make_arm(LibraryArm, 20260930, self.cfg)
        self.seq = 1

    def teach(self, glance_row: int, name: str):
        HarnessContract.teach(self.arm, make_row(self.seq, "TEACH", "toy", name, {"glance_row": glance_row, "name": name}))
        self.seq += 1

    def train(self, cues, operands, kind, right, cands=None):
        a = make_row(self.seq, "ASK", "toy", "x", {"cues": cues, "operands": operands, "candidate_rows": cands,
                                                    "answer_kind": kind})
        ans = HarnessContract.training_ask(self.arm, a)
        fb = make_row(self.seq + 1, "FEEDBACK", "toy", "x", {"ask_seq": self.seq, "right": right})
        HarnessContract.feedback(self.arm, fb, ans, kind)
        self.seq += 2

    def sleep(self):
        HarnessContract.sleep(self.arm, make_row(self.seq, "SLEEP", "toy", "-", {"steps": 0}))
        self.seq += 1

    def test(self, cues, operands, kind, cands=None) -> Answer:
        a = make_row(self.seq, "ASK", "toy", "t", {"cues": cues, "operands": operands, "candidate_rows": cands,
                                                    "answer_kind": kind})
        self.seq += 1
        return HarnessContract.test_ask(self.arm, a)   # raises if state_sha moved


def _save(name: str, rec: Dict[str, Any]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{name}.json").write_text(json.dumps(rec, sort_keys=True, indent=1))


@unittest.skipUnless(HAVE_TOYS, f"the toy cache is absent — build it: {BUILD_CMD}")
class TestToys(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.rows = load_rows()

    def tearDown(self):
        self._tmp.cleanup()

    # -------------------------------------------------------------------------------------------- XOR
    def _xor(self, label_fn) -> Tuple[int, int, Dict[str, Any]]:
        t = Toy(self.tmp, "xor")
        chars = list(XOR_CHARS)
        for k in range(2):
            for f in range(4):
                for ch in chars:
                    t.teach(row(self.rows, ch, f, k), XOR_CHARS[ch])
        for f in range(4):
            for ch in chars:
                t.train(["NAME"], [op_row(row(self.rows, ch, f, 2))], "NAME", XOR_CHARS[ch])
        t.sleep()
        i = 0
        for f in range(4):
            for a in chars:
                for b in chars:
                    t.train(["XOR"], [op_row(row(self.rows, a, f, 3)), op_row(row(self.rows, b, f + 1, 4))], "YESNO",
                            label_fn(a, b, i))
                    i += 1
        t.sleep()
        t.sleep()
        right, total = 0, 0
        for f in range(4):
            for a in chars:
                for b in chars:
                    ans = t.test(["XOR"], [op_row(row(self.rows, a, f, 5)), op_row(row(self.rows, b, f + 1, 5))], "YESNO")
                    want = AnswerKind.YES if a != b else AnswerKind.NO
                    right += int(ans.kind == want)
                    total += 1
        rule = t.arm.rule(["XOR"])["text"]
        return right, total, {"rule": rule, "state_sha": t.arm.state_sha()}

    def test_xor_at_100(self):
        right, total, info = self._xor(lambda a, b, i: "YES" if a != b else "NO")
        _save("xor", {"right": right, "total": total, **info})
        self.assertEqual((right, total), (16, 16), info["rule"])

    def test_xor_control_labels_no_function_of_the_pattern(self):
        """The control: each pattern is shown with BOTH answers (alternating) — no program can reproduce them,
        so D cannot reach 100 % on the fresh renderings."""
        right, total, info = self._xor(lambda a, b, i: "YES" if (i // 4) % 2 == 0 else "NO")
        _save("xor_control", {"right": right, "total": total, **info})
        self.assertLess(right, total, info["rule"])

    # -------------------------------------------------------------------------------------------- the planted relation
    def _plant(self, shuffled: bool) -> Tuple[int, int, Dict[str, Any]]:
        t = Toy(self.tmp, "plant")
        n = len(PLANT_CHARS)
        for r in range(3):
            for i, ch in enumerate(PLANT_CHARS):
                t.teach(row(self.rows, ch, i + r, r), PLANT_NAMES[i])
        for i, ch in enumerate(PLANT_CHARS):
            for f in (i, i + 1):
                t.train(["NAME"], [op_row(row(self.rows, ch, f, 3))], "NAME", PLANT_NAMES[i])
        for i in range(0, n - 1, 2):
            for f in (i, i + 2):
                t.train(["PLUS1"], [op_row(row(self.rows, PLANT_CHARS[i], f, 4))], "NAME", PLANT_NAMES[i + 1])
        t.sleep()
        t.sleep()
        three = [1, 6, 11]
        answers = [PLANT_NAMES[i + 3] for i in three]
        if shuffled:
            answers = answers[1:] + answers[:1]          # a derangement of the three shown answers
        for i, ans in zip(three, answers):
            t.train(["PLUS3"], [op_row(row(self.rows, PLANT_CHARS[i], i, 4))], "NAME", ans)
        t.sleep()
        held = [i for i in range(n - 3) if i not in three]
        right = 0
        got = []
        for i in held:
            a = t.test(["PLUS3"], [op_row(row(self.rows, PLANT_CHARS[i], i + 1, 5))], "NAME")
            got.append(a.value if a.kind == AnswerKind.NAME else a.kind)
            right += int(a.kind == AnswerKind.NAME and a.value == PLANT_NAMES[i + 3])
        info = {"held": len(held), "answers": got, "rule": t.arm.rule(["PLUS3"])["text"],
                "plus1_rule": t.arm.rule(["PLUS1"])["text"], "state_sha": t.arm.state_sha()}
        return right, len(held), info

    def test_planted_relation_from_three_examples(self):
        right, total, info = self._plant(shuffled=False)
        _save("plant", {"right": right, "total": total, **info})
        self.assertEqual(total, 10)
        self.assertEqual(right, 10, info["rule"])

    def test_planted_relation_shuffled_twin_is_not_induced(self):
        right, total, info = self._plant(shuffled=True)
        _save("plant_shuffled", {"right": right, "total": total, **info})
        self.assertLessEqual(right, 2, info["rule"])


if __name__ == "__main__":
    unittest.main()
