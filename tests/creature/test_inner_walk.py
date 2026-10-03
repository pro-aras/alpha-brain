# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:30 +0400 — PREREG-INNER-1 §2 «the topic» + AMENDMENT 1 A1/A2/A4 + G3 (the law: research-1003 @
# 9c589b2, file sha256 127b063c…168d; the co-signed TEXT 857e07b2…faa82), test-first: red on f123190 (no creature/inner.py).
"""tests/creature/test_inner_walk.py — THE WALK of the inner turn, as pure functions over a REAL Web (creature/inner.py).

  lift(web, a, b, c)            c · T ÷ (n_a · n_b), the web's own counts and clock;
  candidates(web, said, mature, last, inhibit)   the union over the SAID words of their consolidated neighbours among the brain's
                                mature words, each with its largest lift, the last `inhibit` topics excluded (lifted when that leaves none);
  draw(cands, rng, rule)        «lift»: one drawn with probability ∝ lift (the genome's only rule); «greedy-count» / «greedy-lift»: test
                                parameters for G3's planted lock, never a genome value;
  first_topic(self_node, mature)   the SELF's least reliable mature word (ties by name); earliest by name when no word has a reliability;
  locked(seq)                   the cycle detector (docs/organism/inner/records/walk_counts.py's own).
The webs here are HAND-BUILT through Web.from_dict so every edge's state and count is known; the real web's walk is the bench's (G3)."""
from __future__ import annotations

import collections
import unittest

import numpy as np

from brain.world.seeds import substream
from creature import inner as I
from genome import web as _web


def web_of(nodes, edges, t=1000) -> "_web.Web":
    """A real Web (rule L, beta 10) with `nodes` = {word: n heard}, `edges` = [(a, b, c)] all CONSOLIDATED, clock t. Built from a real
    instance's OWN to_dict() so every field the code reads exists (a first draft hand-wrote the dict and left `stats` without `events`:
    the mind's first ear row then raised inside Web.hear, _web_fail switched the web AND the self off, and every chain restarted at
    the self — caught by the mind tests, pinned by HearRuns below)."""
    base = _web.Web("L", beta=10, seed=0, spend="harmonic", reach=20, author="toy").to_dict()
    base["t"] = int(t)
    base["nodes"] = {w: {"n": int(n), "first": 1, "last": int(t), "source": "lived", "author": "toy"} for w, n in nodes.items()}
    base["order"] = list(nodes)
    base["edges"] = [[*_web._key(a, b), {"c": int(c), "occ": 3, "t0": 1, "last": int(t), "touch": int(t), "miss": [0, 0], "state": "consolidated",
                                          "consolidated_at": 2, "source": "lived", "author": "toy", "looks": 0}] for a, b, c in edges]
    return _web.Web.from_dict(base)


NODES = {"big": 100, "ring": 20, "small": 90, "white": 60, "star": 40, "red": 50}
EDGES = [("big", "ring", 18), ("big", "small", 30), ("big", "white", 24), ("ring", "white", 8), ("star", "red", 20), ("small", "star", 9)]
MATURE = set(NODES)


class HearRuns(unittest.TestCase):
    def test_the_mind_can_keep_hearing_into_a_built_web(self) -> None:
        w = web_of(NODES, EDGES)
        before = set(w.consolidated())
        for x in ("big", "ring", "star", "never-heard", "big", "small"):
            w.hear(x)                                            # the production path on every ear row; a missing field raises here
        self.assertTrue(before <= set(w.consolidated()))
        self.assertEqual(w.stats["events"] > 0, True)
        self.assertIn("never-heard", w.nodes)


class Lift(unittest.TestCase):
    def test_the_formula_is_the_web_s_own_counts(self) -> None:
        w = web_of(NODES, EDGES)
        self.assertAlmostEqual(I.lift(w, "big", "ring", 18), 18 * 1000 / (100 * 20))
        self.assertAlmostEqual(I.lift(w, "ring", "big", 18), I.lift(w, "big", "ring", 18))


class Candidates(unittest.TestCase):
    def test_the_union_of_the_said_words_neighbours_with_the_largest_lift(self) -> None:
        w = web_of(NODES, EDGES)
        cands, lifted = I.candidates(w, ["big", "star"], MATURE, last=[], inhibit=2)
        self.assertFalse(lifted)
        self.assertEqual([c[0] for c in cands], ["red", "ring", "small", "white"])          # by name; big and star are not their own neighbours
        by = {c[0]: c for c in cands}
        self.assertEqual(by["small"][1], 30)
        self.assertAlmostEqual(by["small"][2], max(I.lift(w, "big", "small", 30), I.lift(w, "star", "small", 9)))

    def test_the_last_topics_are_excluded_and_the_exclusion_is_lifted_when_it_empties_the_set(self) -> None:
        w = web_of(NODES, EDGES)
        cands, lifted = I.candidates(w, ["ring"], MATURE, last=["white", "big"], inhibit=2)
        self.assertEqual(([c[0] for c in cands], lifted), (["big", "white"], True))         # both excluded → the inhibition lifted
        cands, lifted = I.candidates(w, ["ring"], MATURE, last=["white", "big"], inhibit=1)
        self.assertEqual(([c[0] for c in cands], lifted), (["white"], False))                # only the last 1 excluded

    def test_only_mature_words_and_only_words_the_web_knows(self) -> None:
        w = web_of(NODES, EDGES)
        cands, _ = I.candidates(w, ["big"], {"ring", "big"}, last=[], inhibit=2)
        self.assertEqual([c[0] for c in cands], ["ring"])
        cands, _ = I.candidates(w, ["never-heard"], MATURE, last=[], inhibit=2)
        self.assertEqual(cands, [])
        self.assertEqual(I.candidates(None, ["big"], MATURE, last=[], inhibit=2), ([], False))   # no web (an error switched it off)


class Draw(unittest.TestCase):
    def test_lift_is_seeded_and_proportional(self) -> None:
        w = web_of(NODES, EDGES)
        cands, _ = I.candidates(w, ["big"], MATURE, last=[], inhibit=2)
        a = [I.draw(cands, substream(7, f"inner-walk:{n}"), "lift") for n in range(50)]
        b = [I.draw(cands, substream(7, f"inner-walk:{n}"), "lift") for n in range(50)]
        self.assertEqual(a, b)
        counts = collections.Counter(I.draw(cands, substream(7, f"x:{n}"), "lift") for n in range(4000))
        lifts = {c[0]: c[2] for c in cands}
        tot = sum(lifts.values())
        for word, l in lifts.items():
            self.assertAlmostEqual(counts[word] / 4000, l / tot, delta=0.04, msg=word)
        self.assertIsNone(I.draw([], substream(7, "inner-walk:0"), "lift"))

    def test_the_greedy_rules_are_deterministic_and_take_the_top(self) -> None:
        w = web_of(NODES, EDGES)
        cands, _ = I.candidates(w, ["big"], MATURE, last=[], inhibit=2)
        self.assertEqual(I.draw(cands, substream(7, "inner-walk:0"), "greedy-count"), "small")      # c 30
        top_lift = max(cands, key=lambda c: (c[2], c[0]))[0]
        self.assertEqual(I.draw(cands, substream(7, "inner-walk:0"), "greedy-lift"), top_lift)
        with self.assertRaises(ValueError):
            I.draw(cands, substream(7, "inner-walk:0"), "nonsense")


class TheGreedyLockOnAToy(unittest.TestCase):
    """G3's plant, on a toy: a web whose top-count neighbours form a 2-cycle locks the greedy walk; the lift walk with inhibition and
    restart covers the toy's words. The real web's counts are the bench's (walk_counts.py: big<->ring, 2 of 13)."""

    def walk(self, w, rule, inhibit, restart, hops=300, seed=0):
        seq, last, said, pos = [], [], ["big"], 0
        for n in range(hops):
            if restart and pos % restart == 0:
                topic = "big"
                last = []
            else:
                cands, _ = I.candidates(w, said, MATURE, last=last, inhibit=inhibit)
                topic = I.draw(cands, substream(seed, f"inner-walk:{n}"), rule) or "big"
            seq.append(topic)
            last = (last + [topic])[-max(inhibit, 1):] if inhibit else []
            said = [topic]
            pos += 1
        return seq

    def test_greedy_count_locks_and_the_detector_says_so(self) -> None:
        w = web_of(NODES, EDGES)
        seq = self.walk(w, "greedy-count", inhibit=0, restart=0)
        self.assertEqual(len(set(seq)), 2, seq[:8])                        # big <-> small
        self.assertEqual(I.locked(seq), 2)

    def test_the_lift_walk_with_inhibition_and_restart_covers_the_toy(self) -> None:
        w = web_of(NODES, EDGES)
        seq = self.walk(w, "lift", inhibit=2, restart=5)
        self.assertEqual(set(seq), MATURE)
        self.assertIsNone(I.locked(seq))

    def test_the_detector_has_a_positive_and_a_negative_control(self) -> None:
        self.assertEqual(I.locked(["a", "b", "c"] * 40), 3)
        self.assertIsNone(I.locked([f"w{i}" for i in range(100)]))


class FirstTopic(unittest.TestCase):
    def test_the_least_reliable_mature_word_ties_by_name(self) -> None:
        s = _web.SelfNode(author="toy")
        s.lived["words"] = {"big": [10, 9], "ring": [10, 6], "star": [10, 6], "small": [5, 5]}
        topic, source, table = I.first_topic(s, {"big", "ring", "star", "small", "white"})
        self.assertEqual((topic, source), ("ring", "self"))                # ring and star tie at 0.6; ring first by name
        self.assertEqual(dict(table)["white"], None)                        # a mature word the self never heard: present, no value

    def test_no_reliability_at_all_takes_the_earliest_name(self) -> None:
        s = _web.SelfNode(author="toy")
        self.assertEqual(I.first_topic(s, {"ring", "big", "star"})[:2], ("big", "self (no reliability yet)"))
        self.assertEqual(I.first_topic(None, {"ring", "big"})[:2], ("big", "self (no self)"))
        self.assertEqual(I.first_topic(s, set())[:2], (None, "self (no mature word)"))


if __name__ == "__main__":
    unittest.main()
