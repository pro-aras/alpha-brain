"""test_think.py — B11 (docs/G4-PREREG.md §11.2): genome/think.py — believe/clash/induce/deduce.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new file, Wave 2 B11.

The three required toys (§11.2): "a planted rule found and a planted counter-example blocks it"
(induce); "a planted contradiction opens a clash row with both beliefs still readable" (clash); "an
unroutable deduction is REFUSED by name (FILE's law)" (deduce).
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import world
from genome.fast import Episodes
from genome.machinery import Organism
from genome.think import believe, clash, deduce, induce, read_beliefs

from ._toy import SIGHT_DIM, WORDS_DIM, mini_genome, unit


def _jitter(rng: np.random.Generator, v: np.ndarray, scale: float = 0.02) -> np.ndarray:
    j = v + rng.normal(scale=scale, size=v.shape)
    return j / np.linalg.norm(j)


class TestBelieve(unittest.TestCase):
    def test_append_only_line_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            r0 = believe("zog", [1, 2], [10], 5, path)
            r1 = believe("bar", [3], [11], 6, path)
            self.assertEqual(r0["line"], 0)
            self.assertEqual(r1["line"], 1)
            rows = read_beliefs(path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["word"], "zog")
            self.assertEqual(rows[0]["cells"], [1, 2])
            self.assertEqual(rows[1]["word"], "bar")

    def test_cells_and_episodes_deduplicated_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            r = believe("zog", [3, 1, 1, 2], [5, 5, 4], 0, path)
            self.assertEqual(r["cells"], [1, 2, 3])
            self.assertEqual(r["episodes"], [4, 5])


class TestClash(unittest.TestCase):
    def test_disjoint_same_word_opens_a_clash_row_both_beliefs_still_readable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            old = believe("zog", [1, 2], [10], 5, path)
            new = believe("zog", [7, 8], [20], 9, path)  # disjoint cells — a planted contradiction
            row = clash(new, [old], path)
            self.assertIsNotNone(row)
            self.assertEqual(row["kind"], "clash")
            self.assertEqual(row["word"], "zog")
            self.assertEqual(sorted(row["clashes"]), [0, 1])
            # both beliefs still readable, unchanged, in the file (clash never overwrites — B11/PREREG
            # row 4b: BELIEF clash opens never overwrites)
            rows = read_beliefs(path)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0], old)
            self.assertEqual(rows[1], new)
            self.assertEqual(rows[2]["kind"], "clash")

    def test_overlapping_cells_same_word_is_not_a_clash(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            old = believe("zog", [1, 2, 3], [10], 5, path)
            new = believe("zog", [3, 4], [20], 9, path)  # shares cell 3 — same underlying belief
            row = clash(new, [old], path)
            self.assertIsNone(row)

    def test_different_words_never_clash(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            old = believe("zog", [1, 2], [10], 5, path)
            new = believe("bar", [7, 8], [20], 9, path)
            row = clash(new, [old], path)
            self.assertIsNone(row)


class TestInduce(unittest.TestCase):
    def test_planted_rule_found_and_counterexample_blocks_it(self) -> None:
        rng = np.random.default_rng(21)
        org = Organism(mini_genome())
        v_zog = unit(rng)
        v_bar = unit(rng)
        x_w_zog = world.encode_word("zog", org.g.ear_blank_zero)
        x_w_bar = world.encode_word("bar", org.g.ear_blank_zero)
        for _ in range(8):
            org.moment(_jitter(rng, v_zog), x_w_zog)
        for _ in range(8):
            org.moment(_jitter(rng, v_bar), x_w_bar)

        episodes = Episodes(cap=50, dim_s=SIGHT_DIM, dim_w=WORDS_DIM)
        for i in range(4):
            episodes.write(moment=i, x_s=_jitter(rng, v_zog), x_w=x_w_zog, word="zog", surprise=0.1)

        rules = induce(episodes, k=3, org=org)
        zog_rules = [r for r in rules if r.get("word") == "zog"]
        self.assertTrue(zog_rules, f"expected an induced rule for 'zog', got {rules}")
        self.assertTrue(zog_rules[0]["accepted"], zog_rules[0])
        self.assertGreaterEqual(zog_rules[0]["agree"], 3)
        self.assertEqual(zog_rules[0]["disagree"], 0)

        # a planted counter-example: an episode LABELLED "zog" whose sight feature is actually drawn
        # from "bar"'s trained cluster — the organism's own nearest-cell geometry now disagrees with
        # the label, and the rule must be blocked (disagree > 0 refuses induction, no counter allowed).
        episodes.write(moment=100, x_s=_jitter(rng, v_bar), x_w=x_w_zog, word="zog", surprise=0.9)
        rules2 = induce(episodes, k=3, org=org)
        zog_rules2 = [r for r in rules2 if r.get("word") == "zog"]
        self.assertFalse(zog_rules2, f"the counter-example should have blocked the rule, got {zog_rules2}")

    def test_no_episodes_no_rules(self) -> None:
        org = Organism(mini_genome())
        episodes = Episodes(cap=10, dim_s=SIGHT_DIM, dim_w=WORDS_DIM)
        self.assertEqual(induce(episodes, k=3, org=org), [])
        self.assertEqual(induce(None, k=3, org=org), [])


class TestDeduce(unittest.TestCase):
    def test_shared_cell_different_words_predicts_co_resonance(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            a = believe("zog", [1, 2], [10], 5, path)
            b = believe("bar", [2, 3], [11], 6, path)  # shares cell 2 with "zog"
            claims = deduce([a, b])
            self.assertEqual(len(claims), 1)
            self.assertTrue(claims[0]["accepted"], claims[0])
            self.assertEqual(claims[0]["row"]["route"], "recall(sight) at cell 2")
            self.assertEqual(sorted(claims[0]["words"]), ["bar", "zog"])

    def test_disjoint_same_word_deduction_is_unroutable_refused_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            a = believe("zog", [1, 2], [10], 5, path)
            b = believe("zog", [7, 8], [20], 9, path)  # disjoint — same word (also a clash() pair)
            claims = deduce([a, b])
            self.assertEqual(len(claims), 1)
            row = claims[0]
            self.assertFalse(row["accepted"], row)
            self.assertIn("route", row["refused"])
            self.assertEqual(row["row"]["route"], "")

    def test_no_shared_cells_different_words_no_claim(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            a = believe("zog", [1, 2], [10], 5, path)
            b = believe("bar", [3, 4], [11], 6, path)
            self.assertEqual(deduce([a, b]), [])

    def test_overlapping_same_word_no_claim(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            a = believe("zog", [1, 2], [10], 5, path)
            b = believe("zog", [2, 3], [11], 6, path)
            self.assertEqual(deduce([a, b]), [])


if __name__ == "__main__":
    unittest.main()
