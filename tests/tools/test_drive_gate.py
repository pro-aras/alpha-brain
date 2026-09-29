# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:47 +0400 — PREREG-BRAIN-DRIVES §4: the gate's reader, each mark with a planted offender.
"""tests/tools/test_drive_gate.py — tools/brain/drive_gate.py reads what the law says, and a planted defect fails its mark."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.brain import drive_gate as G


def turn(scene: int, say=None, ask=None, surprise=0.0):
    return {"kind": "brain", "act": "turn", "seq": 10 * scene + 3, "moment": f"m{scene}", "at": "t", "scene": scene, "n_hyp": 2,
            "order": [0, 1], "members": [[0, 1], [2]], "held": [["star"], []], "expected": [["star", "red"], ["cross", "blue"]],
            "say": say, "ask": ask, "reason": None, "surprise": surprise, "heard": ["star"]}


def learn(scene: int):
    return {"kind": "brain", "act": "learn", "seq": 10 * scene + 3, "moment": f"m{scene}", "at": "t", "words": ["star"]}


def life(n: int = 6):
    off, on, bench = [], [], []
    for i in range(n):
        off += [{"seq": 10 * i + 1, "word": "star", "hash": f"h{i}"}, learn(i)]
        t = turn(i, say={"hyp": 0, "fix": [[1, 1]], "pos": [1.0, 1.0], "words": ["star"], "readback": 0, "margin": 0.5},
                 ask={"hyp": 1, "fix": [[9, 9]], "pos": [9.0, 9.0]})
        on += [{"seq": 10 * i + 1, "word": "star", "hash": f"h{i}"}, t, learn(i)]
        bench.append({k: t[k] for k in G.TURN_KEYS})
    return off, on, bench


class I2(unittest.TestCase):
    def test_the_journal_without_its_turn_rows_is_the_other_journal(self) -> None:
        off, on, _b = life()
        r = G.mark_i2(on, off)
        self.assertTrue(r["pass"])
        self.assertEqual((r["turn_rows"], r["rows_off"]), (6, 12))

    def test_one_moved_row_fails_it_and_is_named(self) -> None:
        off, on, _b = life()
        on = copy.deepcopy(on)
        on[5]["words"] = ["cross"]
        r = G.mark_i2(on, off)
        self.assertFalse(r["pass"])
        self.assertEqual(r["first_difference"]["seq"], on[5]["seq"])

    def test_a_missing_row_fails_it(self) -> None:
        off, on, _b = life()
        self.assertFalse(G.mark_i2(on[:-1], off)["pass"])
        self.assertFalse(G.mark_i2([], [])["pass"], "two empty journals are no identity")


class JB(unittest.TestCase):
    def test_every_turn_equal(self) -> None:
        _off, on, bench = life()
        r = G.mark_jb(on, bench)
        self.assertTrue(r["pass"])
        self.assertEqual(r["equal"], 6)

    def test_one_other_word_fails_it_and_names_the_key(self) -> None:
        _off, on, bench = life()
        bench = copy.deepcopy(bench)
        bench[2]["say"]["words"] = ["cross"]
        r = G.mark_jb(on, bench)
        self.assertFalse(r["pass"])
        self.assertEqual((r["first_difference"]["scene"], r["first_difference"]["key"]), (2, "say"))

    def test_a_canvas_without_its_turn_row_fails_it(self) -> None:
        _off, on, bench = life()
        on = [r for r in on if not (G.is_turn(r) and r["scene"] == 4)]
        r = G.mark_jb(on, bench)
        self.assertFalse(r["pass"])
        self.assertEqual(r["differing_by_key"], {"no turn row": 1})

    def test_a_turn_the_bench_never_took_fails_it(self) -> None:
        _off, on, bench = life()
        self.assertFalse(G.mark_jb(on, bench[:-1])["pass"])
        self.assertFalse(G.mark_jb([], [])["pass"])


def bench_json(true=0.97, unique=0.94, low=0.92, diff=0.12, p=1e-9, mean=0.13, null_true=0.21, null_sur=0.68, planted=0.0):
    return {"says": {"true": true, "unique_true": unique, "graded": 9000, "no_thing_under_the_target": 0, "rate": 0.95},
            "says_series": [{"from": 0, "to": 1000, "rate": low, "canvases": 750}, {"from": 1000, "to": 2000, "rate": 0.95, "canvases": 1000},
                            {"from": 2000, "to": 3000, "rate": None, "canvases": 0}],
            "null": {"says_true": [0.19, null_true], "surprise_believed": [null_sur, 0.69]},
            "D": {"difference": diff, "p_exact_one_sided": p},
            "doubt": {"doubted": {"believed_names": 3000, "right": 0.80}, "undoubted": {"believed_names": 41000, "right": 0.92}},
            "surprise_believed": {"mean": mean, "n": 9750}, "control_planted_say": {"n": 9000, "true": planted}}


class TheBenchsMarks(unittest.TestCase):
    def test_stage_minus_1s_figures_pass_every_bar(self) -> None:
        m = G.bench_marks(bench_json())
        self.assertTrue(all(m[k]["pass"] for k in ("S", "U", "R", "D", "E")), m)
        self.assertTrue(m["control_planted_say"]["caught"])
        self.assertEqual(m["R"]["lowest_window"]["rate"], 0.92)
        self.assertEqual(m["R"]["windows"], 2, "a window with no canvas is no window")

    def test_each_bar_fails_alone(self) -> None:
        for mark, kw in (("S", {"true": 0.94}), ("S", {"null_true": 0.98}), ("U", {"unique": 0.89}), ("R", {"low": 0.84}),
                         ("D", {"diff": 0.04}), ("D", {"p": 0.01}), ("E", {"mean": 0.21}), ("E", {"null_sur": 0.10})):
            with self.subTest(mark=mark, kw=kw):
                m = G.bench_marks(bench_json(**kw))
                self.assertFalse(m[mark]["pass"])
                self.assertTrue(all(m[k]["pass"] for k in ("S", "U", "R", "D", "E") if k != mark))

    def test_a_grader_that_cannot_fail_a_lying_mouth_is_named(self) -> None:
        self.assertFalse(G.bench_marks(bench_json(planted=0.30))["control_planted_say"]["caught"])


class J(unittest.TestCase):
    def test_the_same_table_and_one_moved_figure(self) -> None:
        a = {k: {"x": 1} for k in G.J_KEYS}
        self.assertTrue(G.mark_j(a, copy.deepcopy(a))["pass"])
        b = copy.deepcopy(a)
        b["doubt"] = {"x": 2}
        self.assertEqual(G.mark_j(b, a)["differing"], ["doubt"])


class C(unittest.TestCase):
    def test_the_cpu_of_a_canvas_is_the_cpu_of_its_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "timings.jsonl"
            p.write_text("\n".join(json.dumps({"seq": s, "ms": 2.0, "cpu_ms": 1.0 + s}) for s in range(1, 7)) + "\n")
            r = G.canvas_cpu(p, {"m0": [1, 2], "m1": [3, 4], "m2": [5, 6]})
            self.assertEqual((r["n"], r["missing"]), (3, 0))
            self.assertAlmostEqual(r["mean_cpu_ms"], (5.0 + 9.0 + 13.0) / 3)
            self.assertEqual(G.canvas_cpu(p, {"m0": [1, 99]})["missing"], 1)


if __name__ == "__main__":
    unittest.main()
