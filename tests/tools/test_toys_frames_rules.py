"""Tests for TOY C's three rules (docs/research/toys/PREREG-TOY-FRAMES.md §2, co-signed 2026-10-03 12:21 +0400): WEB (genome.web, rule H once and rule S with B = 2V),
SENTENCE (genome.sentence.find_frames through a stand-in store) and MDL-GREEDY (the exact incremental gain). Written FIRST, STAGE 2 (red, then green, a log each).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 16:52 +0400 — STAGE 2: the rules. Every expected number is derived by hand in the comments or by the SLOW recount of
# tools/toys/frames/compress.py (slow_train_bits), never by calling the rule under test.
"""
from __future__ import annotations

import math
import unittest
from typing import Dict, List

import numpy as np

from genome.fast import Episodes
from genome.sentence import find_frames

from tools.toys.frames import compress as CO
from tools.toys.frames import rules as RL


def flat(ms) -> List[str]:
    return [w for m in ms for w in m]


# ====================================================================================================================== orientation (WEB's edges -> ordered frames)
class TestOrientEdges(unittest.TestCase):
    def test_the_larger_adjacent_count_wins_ties_go_alphabetical_and_zero_is_dropped(self):
        """(b,a) adjacent 5 times, (a,b) twice -> the frame is (b,a); (c,d) 3 and (d,c) 3 -> the tie goes alphabetical, (c,d); e and f are never adjacent INSIDE a moment -> dropped."""
        train = [["b", "a"]] * 5 + [["a", "b"]] * 2 + [["c", "d"]] * 3 + [["d", "c"]] * 3 + [["e"], ["f"]] * 4
        sc = CO.Scorer(train, [["a"]])
        frames, dropped = RL.orient_edges([("a", "b"), ("c", "d"), ("e", "f")], sc)
        self.assertEqual(frames, {("b", "a"), ("c", "d")})
        self.assertEqual(dropped, [("e", "f")])

    def test_an_edge_given_in_either_order_is_oriented_the_same_way(self):
        train = [["d", "c"]] * 4 + [["c", "d"]] * 4
        sc = CO.Scorer(train, [["c"]])
        self.assertEqual(RL.orient_edges([("c", "d")], sc)[0], RL.orient_edges([("d", "c")], sc)[0])
        self.assertEqual(RL.orient_edges([("d", "c")], sc)[0], {("c", "d")})


# ====================================================================================================================== WEB
def planted_moments(n_blocks: int = 20, fillers: int = 40, seed: int = 3, pair=("zzq", "xxv")) -> List[List[str]]:
    """n_blocks x [the planted pair as ONE two-word moment, then `fillers` one-word moments drawn at random from 400 filler words]."""
    rng = np.random.default_rng(seed)
    pool = [f"f{i:03d}" for i in range(400)]
    ms: List[List[str]] = []
    for _ in range(n_blocks):
        ms.append(list(pair))
        for _ in range(fillers):
            ms.append([pool[int(rng.integers(0, len(pool)))]])
    return ms


class TestWebRule(unittest.TestCase):
    def setUp(self):
        self.ms = planted_moments()
        self.sc = CO.Scorer(self.ms, [["zzq"]])

    def test_h_keeps_a_pair_that_recurs_inside_a_moment_and_drops_nothing_it_made_up(self):
        r = RL.web_rule(flat(self.ms), self.sc, "H", 1)
        self.assertIn(("zzq", "xxv"), r.frames)
        self.assertEqual(r.rule, "WEB-H")
        self.assertIsNone(r.info["budget"])
        # every kept frame is adjacent INSIDE a train moment; the rest of the web's edges were dropped and counted
        for f in r.frames:
            self.assertGreater(self.sc.train_adjacent(f), 0, f)
        self.assertEqual(r.info["consolidated"], len(r.frames) + r.info["dropped_no_adjacent"])

    def test_a_consolidated_edge_that_is_never_adjacent_inside_a_moment_is_dropped_and_counted(self):
        rng = np.random.default_rng(5)
        pool = [f"f{i:03d}" for i in range(400)]
        ms: List[List[str]] = []
        for _ in range(20):
            ms += [["pq"], ["rs"], ["tu"]]                                   # flat-adjacent in the heard stream, one moment each: never adjacent inside one
            ms += [[pool[int(rng.integers(0, len(pool)))]] for _ in range(40)]
        sc = CO.Scorer(ms, [["pq"]])
        r = RL.web_rule(flat(ms), sc, "H", 1)
        self.assertEqual(r.frames, frozenset())
        self.assertGreaterEqual(r.info["consolidated"], 3)                    # the web DID consolidate pq-rs, rs-tu, pq-tu ...
        self.assertEqual(r.info["dropped_no_adjacent"], r.info["consolidated"])  # ... and every one of them was dropped

    def test_s_runs_on_a_budget_of_two_v_and_never_exceeds_it(self):
        r = RL.web_rule(flat(self.ms), self.sc, "S", 1)
        self.assertEqual(r.rule, "WEB-S")
        self.assertEqual(r.info["budget"], 2 * self.sc.V)
        self.assertLessEqual(r.info["peak_edges"], 2 * self.sc.V)             # KW-1's G3

    def test_s_is_deterministic_in_its_seed_and_seeds_differ(self):
        a = RL.web_rule(flat(self.ms), self.sc, "S", 4)
        b = RL.web_rule(flat(self.ms), self.sc, "S", 4)
        self.assertEqual(a.frames, b.frames)
        self.assertEqual(a.info["stats"], b.info["stats"])
        realised = {RL.web_rule(flat(self.ms), self.sc, "S", s).info["stats"]["realised"] for s in (1, 2, 3, 4, 5)}
        self.assertGreater(len(realised), 1)                                  # the seed is really used (rule S realises each offered edge with probability 1/2)

    def test_s_keeps_the_planted_pair_at_nine_of_ten_seeds_on_a_clear_plant(self):
        kept = sum(1 for s in range(1, 11) if ("zzq", "xxv") in RL.web_rule(flat(self.ms), self.sc, "S", s).frames)
        self.assertGreaterEqual(kept, 9)

    def test_an_unknown_rule_is_refused(self):
        with self.assertRaises(ValueError):
            RL.web_rule(flat(self.ms), self.sc, "F", 1)


# ====================================================================================================================== SENTENCE
def known_store() -> List[List[str]]:
    """10 x «red box», 10 x «blue ball», 10 x «green key», 2 x «red ball», 3 x one word, 2 x «a a», 2 empty, 4 x «x y z».
    find_frames' N = the moments with >= 2 DISTINCT words = 30 + 2 + 4 = 36 («a a» has one, the empty ones none). By hand: red = 12, box = 10, so (red, box) has count 10
    against an expectation 12 * 10 / 36 = 3.33 -> 10 >= 5 and 10 > 6.67; likewise (blue, ball) 10 vs 10 * 12 / 36 = 3.33 and (green, key) 10 vs 10 * 10 / 36 = 2.78;
    (red, ball) has count 2 < 5 and (x, y), (x, z), (y, z) count 4 < 5: not frames."""
    return ([["red", "box"]] * 10 + [["blue", "ball"]] * 10 + [["green", "key"]] * 10 + [["red", "ball"]] * 2
            + [["the"]] * 3 + [["a", "a"]] * 2 + [[]] * 2 + [["x", "y", "z"]] * 4)


class TestSentenceRule(unittest.TestCase):
    def test_the_stand_in_store_gives_the_cells_own_answer_G2(self):
        """G2: find_frames on the stand-in store equals the call on the REAL Episodes store (the cells' own, genome.fast) holding the same known moments."""
        ms = known_store()
        real = Episodes(cap=64, dim_s=2, dim_w=2)
        for m in ms:
            real.write(0, np.zeros(2), np.zeros(2), "", 0.0, words_in_instant=list(m))
        a = find_frames(real)
        b = find_frames(RL.StandIn(ms))
        self.assertEqual(a, b)
        self.assertEqual({(r["w1"], r["w2"]) for r in a}, {("red", "box"), ("blue", "ball"), ("green", "key")})     # the hand derivation of known_store's docstring
        self.assertEqual(a[0]["N"], 36)

    def test_the_rule_returns_the_cells_pairs_as_ordered_frames_with_the_cells_parameters(self):
        r = RL.sentence_rule(known_store())
        self.assertEqual(r.rule, "SENTENCE")
        self.assertEqual(r.frames, frozenset({("red", "box"), ("blue", "ball"), ("green", "key")}))
        self.assertEqual((r.info["min_count"], r.info["factor"], r.info["N"], r.info["rows"]), (5, 2.0, 36, 3))

    def test_it_counts_every_ordered_pair_of_a_moment_not_only_the_adjacent_ones(self):
        """6 x [a b c] among 30 x [p q]: N = 36; (a, b), (a, c), (b, c) each count 6 vs 6 * 6 / 36 = 1 -> all three are filed, (a, c) although never adjacent;
        (p, q): 30 vs 30 * 30 / 36 = 25 is NOT above twice the expectation."""
        r = RL.sentence_rule([["a", "b", "c"]] * 6 + [["p", "q"]] * 30)
        self.assertEqual(r.frames, frozenset({("a", "b"), ("a", "c"), ("b", "c")}))

    def test_the_stand_in_never_evicts_and_reads_every_moment(self):
        ms = known_store()
        s = RL.StandIn(ms)
        self.assertEqual((s.n_written, s.cap, len(s)), (len(ms), len(ms), len(ms)))
        self.assertEqual(s.get(0), {"id": 0, "words_in_instant": ["red", "box"]})
        self.assertIsNone(s.get(len(ms)))


# ====================================================================================================================== MDL-GREEDY
PLANTED = (("a", "b", 0.25), ("c", "d", 0.15), ("e", "f", 0.10), ("g", "h", 0.06), ("b", "c", 0.05))         # (first, second, share of moments); (b, c) overlaps (a, b) and (c, d)


def random_train(seed: int, n: int = 300, alphabet: str = "abcdefgh") -> List[List[str]]:
    """Moments of 1-5 words over a small alphabet; PLANTED shares of them carry a consecutive pair inserted at a random place (so the chains a-b-c-d arise), the rest is noise."""
    rng = np.random.default_rng(seed)
    out: List[List[str]] = []
    for _ in range(n):
        m = [alphabet[int(i)] for i in rng.integers(0, len(alphabet), size=int(rng.integers(1, 5)))]
        u = rng.random()
        acc = 0.0
        for x, y, share in PLANTED:
            acc += share
            if u < acc:
                j = int(rng.integers(0, len(m) + 1))
                m[j:j] = [x, y]
                break
        out.append(m)
    return out


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:09 +0400 — the checker moved VERBATIM into tools/toys/frames/rules.py (the gate G3 runs it too: one copy, not two); the tests below still plant faults into a trace and require it to be CAUGHT.
trace_problems = RL.trace_problems


class TestMdlGreedy(unittest.TestCase):
    def test_candidates_are_the_adjacent_train_bigrams_with_count_at_least_two(self):
        train = [["a", "b", "c"], ["a", "b"], ["b", "c"], ["c", "a"]]
        sc = CO.Scorer(train, [["a"]])
        self.assertEqual(RL.mdl_candidates(sc), [("a", "b"), ("b", "c")])         # (a,b) x2, (b,c) x2, (c,a) x1

    def test_the_incremental_delta_equals_a_full_recount_at_every_step_and_the_pick_is_the_argmax(self):
        n_steps = 0
        for seed in range(8):
            train = random_train(seed)
            sc = CO.Scorer(train, [["a"]])
            r = RL.mdl_greedy(sc)
            self.assertEqual(trace_problems(train, r.info["trace"]), [], seed)
            self.assertEqual(r.frames, frozenset(tuple(s["frame"]) for s in r.info["trace"]))
            n_steps += len(r.info["trace"])
        self.assertGreaterEqual(n_steps, 24)                                     # the loop really took steps: 3-4 a seed on 8 seeds (a vacuous pass would be all-zero)

    def test_the_recount_comparison_can_see_an_error(self):
        """a planted fault: one recorded delta moved by 1e-6 must be named by trace_problems (the plant asserts it changed the value)."""
        train = random_train(0)                                                  # 4 steps, the third an overlapping pair
        r = RL.mdl_greedy(CO.Scorer(train, [["a"]]))
        trace = [dict(s) for s in r.info["trace"]]
        self.assertGreater(len(trace), 1)
        planted = [dict(s) for s in trace]
        planted[1]["delta"] += 1e-6
        self.assertNotEqual(planted[1]["delta"], trace[1]["delta"])
        self.assertEqual(trace_problems(train, trace), [])
        self.assertTrue(any("step 1: delta" in p for p in trace_problems(train, planted)))
        wrong_pick = [dict(s) for s in trace]
        wrong_pick[0]["frame"] = ("f", "f")
        self.assertTrue(any("step 0: chose" in p for p in trace_problems(train, wrong_pick)))

    def test_it_takes_the_planted_frame_first_and_stops_when_nothing_pays(self):
        train = [["p", "q"] if i % 3 == 0 else ["w%d" % (i % 11)] for i in range(300)]
        r = RL.mdl_greedy(CO.Scorer(train, [["p"]]))
        self.assertEqual(r.info["trace"][0]["frame"], ("p", "q"))
        self.assertIn(("p", "q"), r.frames)
        self.assertEqual(r.rule, "MDL-GREEDY")
        self.assertEqual(r.info["steps"], len(r.info["trace"]))

    def test_ties_break_by_the_pairs_name(self):
        """two exactly symmetric pairs, (c, d) and (a, b), each 10 times among identical noise: their deltas are equal to float noise, so the smaller NAME goes first."""
        train = [["a", "b"]] * 10 + [["c", "d"]] * 10 + [["e"], ["f"]] * 10
        r = RL.mdl_greedy(CO.Scorer(train, [["a"]]))
        first_two = [tuple(s["frame"]) for s in r.info["trace"][:2]]
        self.assertEqual(first_two, [("a", "b"), ("c", "d")])
        d0, d1 = r.info["trace"][0]["delta"], r.info["trace"][1]["delta"]
        self.assertGreater(d0, 0.0)
        self.assertGreater(d1, 0.0)

    def test_overlapping_pairs_are_re_parsed_after_each_pick_not_double_counted(self):
        """(a,b) and (b,c) over «a b c» x 12: the first pick takes (a,b) or (b,c) and the other can then fire only where the first did not (here: never) — the trace must still equal the
        recount, which re-parses the whole train after every addition."""
        train = [["a", "b", "c"]] * 12 + [["x"]] * 5
        r = RL.mdl_greedy(CO.Scorer(train, [["a"]]))
        self.assertEqual(trace_problems(train, r.info["trace"]), [])
        self.assertEqual(len(r.info["trace"]), 1)                              # the second frame would never fire after the first (a b | c or a | b c): it only costs its model bits


if __name__ == "__main__":
    unittest.main()
