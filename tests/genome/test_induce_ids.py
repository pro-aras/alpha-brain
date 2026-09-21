"""test_induce_ids.py — the INDUCE cluster is the WORD's OWN cells, pinned on an organism whose sight
cell ids and words indices are DISJOINT.

edit: Claude (Fable 5.1), 2026-09-21 15:16 +0400 — after the 2026-09-21 finding (docs/organs/MIND-THINKING-LANGUAGE.md
§0): genome/think.py:411 compared recall("words", …)["cell"] (the SIGHT cell the word recalls) with
_answer_of(sight, c) (a WORDS index). test_think.py's toy could not see it: zog was sight cell 0 AND word 0,
bar sight 1 AND word 1 — the two id spaces coincided, so the wrong key returned the right cluster.
Here zog owns TWO sight cells (0, 1) so every later word's sight id ≠ its word index; the old key must
then cluster ANOTHER word's cells or nothing (the planted twin), and the fixed key the word's own.
Verified on life 3's own snapshot 15:1x +04: as coded 2/21 words clustered, both the wrong cells; with
r["lit"] 21/21."""
from __future__ import annotations

import unittest

import numpy as np

from genome import world
from genome.fast import Episodes
from genome.machinery import Organism
from genome.think import induce

from ._toy import SIGHT_DIM, WORDS_DIM, mini_genome, unit


def _jitter(rng, v, scale=0.02):
    j = v + rng.normal(scale=scale, size=v.shape)
    return j / np.linalg.norm(j)


def _cluster(org, word, key):
    """think.py's own two lines, with the key as a parameter: key='lit' is the fix, key='cell' the old code."""
    r = org.recall("words", world.encode_word(word, org.g.ear_blank_zero))
    wc = r[key]
    if wc is None:
        return None
    return sorted(int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == wc)


class TestInduceIds(unittest.TestCase):
    def _org(self):
        rng = np.random.default_rng(7)
        org = Organism(mini_genome())
        v = {"zogA": unit(rng), "zogB": unit(rng), "bar": unit(rng), "cat": unit(rng)}
        xw = {w: world.encode_word(w, org.g.ear_blank_zero) for w in ("zog", "bar", "cat")}
        for _ in range(6):
            org.moment(_jitter(rng, v["zogA"]), xw["zog"])
            org.moment(_jitter(rng, v["zogB"]), xw["zog"])      # zog: two sight cells, one word cell
        for _ in range(6):
            org.moment(_jitter(rng, v["bar"]), xw["bar"])
        for _ in range(6):
            org.moment(_jitter(rng, v["cat"]), xw["cat"])
        return rng, org, v, xw

    def test_id_spaces_are_disjoint_for_bar_and_cat(self):
        _, org, _, _ = self._org()
        for w in ("bar", "cat"):
            r = org.recall("words", world.encode_word(w, org.g.ear_blank_zero))
            self.assertIsNotNone(r["lit"]); self.assertIsNotNone(r["cell"])
            self.assertNotEqual(r["cell"], r["lit"], f"{w}: sight id {r['cell']} == word index {r['lit']} — the toy cannot see the defect")

    def test_fixed_key_clusters_the_words_own_cells(self):
        _, org, _, _ = self._org()
        own = {w: [int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == org.recall("words", world.encode_word(w, org.g.ear_blank_zero))["lit"]] for w in ("bar", "cat")}
        for w in ("bar", "cat"):
            C = _cluster(org, w, "lit")
            self.assertTrue(C, f"{w}: empty cluster under the fix")
            self.assertEqual(C, own[w])
        self.assertTrue(set(own["bar"]).isdisjoint(own["cat"]))

    def test_planted_old_key_is_caught(self):
        """The negative control: the old key must NOT return bar's own cells (it returns another word's or nothing)."""
        _, org, _, _ = self._org()
        own_bar = _cluster(org, "bar", "lit")
        old = _cluster(org, "bar", "cell")
        self.assertNotEqual(old, own_bar, f"the old key returned bar's own cells {old}: the toy's id spaces coincide")
        if old:
            self.assertTrue(set(old).isdisjoint(own_bar), f"old key {old} overlaps bar's own cells {own_bar}")

    def test_induce_files_a_rule_for_bar(self):
        rng, org, v, xw = self._org()
        episodes = Episodes(cap=50, dim_s=SIGHT_DIM, dim_w=WORDS_DIM)
        for i in range(4):
            episodes.write(moment=i, x_s=_jitter(rng, v["bar"]), x_w=xw["bar"], word="bar", surprise=0.1)
        rules = [r for r in induce(episodes, k=3, org=org) if r.get("word") == "bar"]
        self.assertTrue(rules, "no rule for bar under the fixed key")
        self.assertTrue(rules[0]["accepted"]); self.assertGreaterEqual(rules[0]["agree"], 3); self.assertEqual(rules[0]["disagree"], 0)
        self.assertEqual(sorted(rules[0]["cluster"]), _cluster(org, "bar", "lit"))


if __name__ == "__main__":
    unittest.main()
