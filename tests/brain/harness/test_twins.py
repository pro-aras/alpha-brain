# edit: Claude (Fable 5.1), 2026-09-24 19:06 +0400 — the harness-side twins as units: the tape transforms (R22/R23) touch exactly the
# rows they name and keep every sha legitimate; KEY answers the truth, SHIFTED-KEY the next ask's, RING-READ by index
# arithmetic over the TEACH order it heard; FORCED-ANSWER forces only a carried would-be answer.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from brain.protocol import Answer, AnswerKind, make_row, op_name, op_row, verify_row
from brain.twins import transforms as TR
from brain.twins.forced import ForcedAnswer
from brain.twins.harness_arms import KeyArm, RingReadArm


def _tape():
    rows = [
        make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}),
        make_row(2, "TEACH", "L1", "b", {"glance_row": 1, "name": "b"}),
        make_row(3, "TEACH", "L1", "c", {"glance_row": 2, "name": "c"}),
        make_row(4, "ASK", "L4", "NAME:a", {"cues": ["NAME"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"}),
        make_row(5, "FEEDBACK", "L4", "NAME:a", {"ask_seq": 4, "right": "a"}),
        make_row(6, "ASK", "L4", "AFTER:a>b", {"cues": ["AFTER"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"}),
        make_row(7, "FEEDBACK", "L4", "AFTER:a>b", {"ask_seq": 6, "right": "b"}),
        make_row(8, "ASK", "L4", "MIRROR", {"cues": ["MIRROR"], "operands": [op_row(1)], "candidate_rows": None, "answer_kind": "YESNO"}),
        make_row(9, "FEEDBACK", "L4", "MIRROR", {"ask_seq": 8, "right": "YES"}),
        make_row(10, "ASK", "L4", "POINT:c", {"cues": ["POINT"], "operands": [op_name("c")], "candidate_rows": [0, 1, 2], "answer_kind": "PICK"}),
        make_row(11, "FEEDBACK", "L4", "POINT:c", {"ask_seq": 10, "right": 2}),
        make_row(12, "TEST_BEGIN", "T_L", "-", {"sitting": "T_L"}),
        make_row(13, "ASK", "T_L", "NAME:b", {"cues": ["NAME"], "operands": [op_row(1)], "candidate_rows": None, "answer_kind": "NAME"}),
        make_row(14, "ASK", "T_L", "AFTER:b>c", {"cues": ["AFTER"], "operands": [op_row(1)], "candidate_rows": None, "answer_kind": "NAME"}),
        make_row(15, "ASK", "T_L", "BETWEEN:a,c", {"cues": ["BETWEEN"], "operands": [op_row(0), op_row(2)], "candidate_rows": None, "answer_kind": "NAME"}),
        make_row(16, "ASK", "T_L", "POINT:a", {"cues": ["POINT"], "operands": [op_name("a")], "candidate_rows": [2, 0], "answer_kind": "PICK"}),
        make_row(17, "TEST_END", "T_L", "-", {"sitting": "T_L"}),
    ]
    return rows


def _truth(tmp: Path):
    recs = [{"type": "rendering", "item_id": f"r{i}", "cache_row": i, "script": "latin-lower", "char": "abc"[i], "font": "f", "variant": "b", "seed": 1,
             "top": 0, "left": 0, "cell": [0, 0], "canvas_png_sha256": f"{i:064x}"} for i in range(3)]
    recs += [{"type": "ask", "seq": 13, "item": "NAME:b", "family": "U1a_NAME", "class": "latin-lower", "answer": "b", "pair": None, "rendering": ["r1"], "font": "f", "split": "test", "sitting": "T_L", "answer_kind": "NAME"},
             {"type": "ask", "seq": 14, "item": "AFTER:b>c", "family": "AFTER", "class": "latin-lower", "answer": "c", "pair": ["b", "c"], "rendering": ["r1"], "font": "f", "split": "held_out", "sitting": "T_L", "answer_kind": "NAME"},
             {"type": "ask", "seq": 15, "item": "BETWEEN:a,c", "family": "BETWEEN", "class": "latin-lower", "answer": "b", "pair": ["a", "b", "c"], "rendering": ["r0", "r2"], "font": "f", "split": "held_out", "sitting": "T_L", "answer_kind": "NAME"},
             {"type": "ask", "seq": 16, "item": "POINT:a", "family": "U1b_PICK", "class": "latin-lower", "answer": 1, "pair": None, "rendering": ["r2", "r0"], "font": "f", "split": "test", "sitting": "T_L", "answer_kind": "PICK"}]
    p = tmp / "truth.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    return p


class TestTransforms(unittest.TestCase):
    def test_shuffled_name_touches_training_names_only(self) -> None:
        rows = _tape()
        out, m = TR.shuffled_name(rows, 20261001)
        self.assertEqual(len(out), len(rows))
        self.assertTrue(all(verify_row(r) for r in out))
        self.assertTrue(all(m[k] in TR.ALL_NAMES for k in m) and len(set(m.values())) == len(m))   # a bijection
        self.assertEqual(out[0]["payload"]["name"], m["a"])                                          # TEACH mapped
        self.assertEqual(out[4]["payload"]["right"], m["a"])                                         # NAME feedback mapped
        self.assertEqual(out[6]["payload"]["right"], m["b"])                                         # a relation NAME answer is a name too
        self.assertEqual(out[9]["payload"]["operands"][0]["value"], m["c"])                          # heard-name operand mapped
        self.assertEqual(out[10]["payload"]["right"], 2)                                             # a PICK index is not a name
        for i in (12, 13, 14, 15, 16):
            self.assertEqual(out[i], rows[i])                                                        # the sitting untouched
        self.assertNotEqual(out[0]["sha"], rows[0]["sha"]) if m["a"] != "a" else None

    def test_shuffled_relation_touches_relation_feedback_only(self) -> None:
        rows = _tape()
        out, maps = TR.shuffled_relation(rows, 20261001)
        self.assertTrue(all(verify_row(r) for r in out))
        self.assertEqual(out[4], rows[4])                          # NAME feedback untouched (a naming cue)
        self.assertEqual(out[10], rows[10])                        # POINT feedback untouched
        self.assertEqual(out[6]["payload"]["right"], maps["AFTER"]["b"])
        self.assertIn(out[8]["payload"]["right"], ("YES", "NO"))
        self.assertIn("MIRROR:yesno", maps)
        for i in range(12, 17):
            self.assertEqual(out[i], rows[i])


class TestHarnessArms(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.truth = _truth(Path(self.tmp.name))
        self.rows = _tape()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_key_and_shifted_key(self) -> None:
        key = KeyArm(1, {"truth_path": str(self.truth), "shift": 0})
        self.assertEqual(key.answer(self.rows[12]).value, "b")
        self.assertEqual(key.answer(self.rows[15]).to_dict()["value"], 1)
        s0 = key.state_sha(); key.fit_event(self.rows[0]); self.assertEqual(key.state_sha(), s0)
        shifted = KeyArm(1, {"truth_path": str(self.truth), "shift": 1})
        self.assertEqual(shifted.answer(self.rows[12]).value, "c")             # ask 13 answered with ask 14's truth
        a = shifted.answer(self.rows[14])                                        # ask 15 (NAME) gets ask 16's PICK index → coerced: not a str → NOTHING
        self.assertEqual(a.kind, AnswerKind.NOTHING)
        b = shifted.answer(self.rows[15])                                        # ask 16 (PICK) gets ask 13's "b" → not an index → NOTHING
        self.assertEqual(b.kind, AnswerKind.NOTHING)

    def test_ring_read(self) -> None:
        rr = RingReadArm(1, {"truth_path": str(self.truth)})
        for r in self.rows[:3]:
            rr.fit_event(r)
        self.assertEqual(rr.answer(self.rows[13]).value, "c")                  # AFTER b → c
        self.assertEqual(rr.answer(self.rows[14]).value, "b")                  # BETWEEN a, c → b
        self.assertEqual(rr.answer(self.rows[12]).kind, AnswerKind.NOTHING)    # NAME: no road
        self.assertEqual(rr.answer(self.rows[5]).value, "b")                   # AFTER a → b
        after_c = make_row(99, "ASK", "T_L", "AFTER:c", {"cues": ["AFTER"], "operands": [op_row(2)], "candidate_rows": None, "answer_kind": "NAME"})
        self.assertEqual(rr.answer(after_c).kind, AnswerKind.NOTHING)          # off the end of the order → refused (U5's shape)

    def test_forced_wrapper(self) -> None:
        class Inner:
            def __init__(self): self.n = 0
            def answer(self, row, learn=False):
                if row["seq"] == 13:
                    return Answer(kind=AnswerKind.UNKNOWN, raw={"forced": {"kind": "NAME", "value": "b"}})
                return Answer(kind=AnswerKind.NOTHING, raw={})
            def state_sha(self): return "x"
            def fit_event(self, row, valence=None): self.n += 1
            def sleep(self, steps): pass
            def snapshot(self, p): pass
            def load(self, p): pass
            def cost(self): return {"events": self.n, "ms": 0.0}
        f = ForcedAnswer(Inner())
        a = f.answer(self.rows[12]); self.assertEqual((a.kind, a.value, a.raw["forced_from"]), ("NAME", "b", "UNKNOWN"))
        b = f.answer(self.rows[13]); self.assertEqual(b.kind, AnswerKind.NOTHING); self.assertTrue(b.raw["forced_no_road"])
        self.assertEqual(f.counters(), {"forced": 1, "no_road": 1})


if __name__ == "__main__":
    unittest.main()
