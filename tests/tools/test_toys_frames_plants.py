"""Tests for TOY C's plant machinery (docs/research/toys/PREREG-TOY-FRAMES.md §3 PLANT, §4 PLANT-FOUND, §7 G4). Written FIRST, STAGE 3a (red, then green, a log each).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:01 +0400 — STAGE 3a: the PERFECT-MECHANISM reading the seat asked for (17:0x: what the ORIGINAL whole-set clause «each such set's G > 0»
# reads for a mechanism that finds the planted frame EXACTLY and keeps nothing else): the one-frame set {(zzq, xxv)} on the planted split, against its own control on the
# plain split. Every number is compared with the SLOW recount of compress.py (slow_gain), never with the code under test.
"""
from __future__ import annotations

import math
import unittest

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import plants as PL
from tools.toys.frames import streams as ST


def words_stream(n: int, seed: int = 0, vocab: int = 30):
    rng = np.random.default_rng(seed)
    return [ST.Moment("s", f"m{i}", (f"w{int(rng.integers(0, vocab))}",), (float(i + 1),)) for i in range(n)]


def parts(ms):
    tr, he = ST.split(ms)
    return [m.words for m in tr], [m.words for m in he]


class TestPerfectReading(unittest.TestCase):
    def test_the_split_is_taken_after_planting_and_the_plants_are_counted_by_part(self):
        ms = words_stream(500)
        r = PL.perfect_reading(ms, every=10)
        self.assertEqual(r["n_moments"], 550)                                     # 500 + one plant after every 10th
        self.assertEqual(r["n_train"], ST.split_index(550))                       # 330
        self.assertEqual(r["n_held"], 550 - 330)
        planted = ST.with_plant(ms, 10)
        tr, he = ST.split(planted)
        self.assertEqual(r["plants_train"], sum(1 for m in tr if m.source == "plant"))
        self.assertEqual(r["plants_held"], sum(1 for m in he if m.source == "plant"))
        self.assertEqual(r["plants_train"] + r["plants_held"], 50)
        self.assertNotEqual(r["n_moments"], len(ms))                              # the plant changed the stream

    def test_the_reading_equals_the_slow_recount_on_the_planted_split(self):
        ms = words_stream(500, seed=3)
        r = PL.perfect_reading(ms, every=10)
        slow = CO.slow_gain(*parts(ST.with_plant(ms, 10)), {ST.PLANT})
        self.assertAlmostEqual(r["G"], slow["G"], places=9)
        for k in ("bits0", "bitsF", "L"):
            self.assertAlmostEqual(r[k], slow[k], places=9, msg=k)
        for k in ("N", "K", "V"):
            self.assertEqual(r[k], slow[k], k)

    def test_a_frequent_plant_pays_and_the_same_frame_on_the_plain_stream_does_not(self):
        ms = words_stream(500, seed=4)
        r = PL.perfect_reading(ms, every=5)
        self.assertGreater(r["G"], 0.0)                                            # a frame found exactly, on a stream that carries it, saves bits net of its own cost
        slow_plain = CO.slow_gain(*parts(ms), {ST.PLANT})
        self.assertAlmostEqual(r["control_plain_G"], slow_plain["G"], places=9)    # the control IS the same one-frame set on the unplanted split
        self.assertAlmostEqual(r["control_plain_L"], slow_plain["L"], places=9)
        self.assertLess(r["control_plain_G"], -r["control_plain_L"] + 1e-9)        # it never fires: every held-out bit it changes is a loss, and K only grows
        self.assertLess(r["control_plain_G"], 0.0)

    def test_a_plant_that_is_too_rare_to_repay_its_model_cost_reads_negative(self):
        """the instrument can say NO: with one plant in train and one in the held-out part the frame cannot repay 2 log2 V bits."""
        r = PL.perfect_reading(words_stream(200, seed=5), every=100)               # 202 moments: split 121, plants after 100 (train) and 200 (held)
        self.assertEqual((r["plants_train"], r["plants_held"]), (1, 1))
        self.assertLess(r["G"], 0.0)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:09 +0400 — the plant tokens' premise («two tokens in no vocabulary», law §3) is a GATE now: xxv is a REAL word of alpha4-1's shelf text (a chapter
# heading, 4 moments: docs/research/toys/records/frames/ORIENT-plant_tokens_outside.out), so the second plant token is replaced (AMENDMENT-1) and every run counts both tokens' real occurrences.
class TestPlantTokens(unittest.TestCase):
    def test_occurrences_are_counted_outside_the_plant_moments_only(self):
        first, second = ST.PLANT
        ms = [ST.Moment("shelf", "a", ("lesson", second), (1.0, 2.0)), ST.Moment("shelf", "b", ("x",), (3.0,)), ST.Moment("shelf", "c", (first, "y"), (4.0, 5.0))]
        self.assertEqual(PL.plant_token_occurrences(ms), {first: 1, second: 1})
        planted = ST.with_plant(ms, 1)                                              # three plant moments added: they must not be counted
        self.assertEqual(sum(1 for m in planted if m.source == "plant"), 3)
        self.assertEqual(PL.plant_token_occurrences(planted), {first: 1, second: 1})
        self.assertEqual(PL.plant_token_occurrences([ST.Moment("shelf", "d", ("w",), (6.0,))]), {first: 0, second: 0})

    def test_the_plant_is_two_distinct_tokens(self):
        self.assertEqual(len(ST.PLANT), 2)
        self.assertNotEqual(*ST.PLANT)

    @unittest.skipUnless((ST.COPIES / "alpha4-1" / "tape").is_dir() and (ST.COPIES / "brain-full-20261102" / "tape").is_dir(), "the copies are not made yet")
    def test_the_plant_tokens_occur_in_no_real_stream_G1(self):
        """G1 (law §7, extended by AMENDMENT-1): both plant tokens occur in ZERO rows of every copied stream (the premise «in no vocabulary» is read, not assumed)."""
        a4 = ST.load_moments(sorted((ST.COPIES / "alpha4-1" / "tape").glob("*.jsonl")))
        sc = ST.scene_moments(ST.load_moments(sorted((ST.COPIES / "brain-full-20261102" / "tape").glob("*.jsonl"))))
        for name, ms in (("ALPHA4", a4), ("SCENE", sc)):
            self.assertEqual(PL.plant_token_occurrences(ms), {t: 0 for t in ST.PLANT}, name)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:56 +0400 — STAGE 4a: AMENDMENT-1 §1's PLANT gate: per rule (i) keeps the planted frame, (A) the whole-set G, (C) the frame's marginal credit inside the rule's own
# set; per stream (B) G({F*}) and the architect's expected value, PLANT-BEATS-NULL-2, and the gate's own parse-breaking control. Each number is compared with the SLOW recount.
from tests.tools.test_toys_frames_null import multiword_stream                     # a planted stream of 1-3-word moments (real adjacent bigrams exist)
from tools.toys.frames import null as NL


def planted_scorer(seed: int = 1):
    tr, he = ST.split(multiword_stream(seed))
    return CO.Scorer([m.words for m in tr], [m.words for m in he]), tr, he


class TestPlantReading(unittest.TestCase):
    def test_keeps_A_and_the_marginal_credit_equal_the_slow_recount(self):
        sc, tr, he = planted_scorer()
        junk = {("w00", "w01"), ("w01", "w02")}
        F = {ST.PLANT} | junk
        r = PL.plant_reading(sc, F)
        slow_all = CO.slow_gain(sc.train, sc.held, F)["G"]
        slow_without = CO.slow_gain(sc.train, sc.held, junk)["G"]
        self.assertTrue(r["kept"])
        self.assertAlmostEqual(r["A"], slow_all, places=9)
        self.assertAlmostEqual(r["C"], slow_all - slow_without, places=9)
        self.assertGreater(r["C"], 0.0)                                                          # the plant pays inside a set that also holds junk (it is a frequent, adjacent plant)

    def test_a_set_that_does_not_keep_the_plant_has_no_marginal_credit(self):
        sc, _tr, _he = planted_scorer()
        r = PL.plant_reading(sc, {("w00", "w01")})
        self.assertFalse(r["kept"])
        self.assertIsNone(r["C"])
        self.assertAlmostEqual(r["A"], CO.slow_gain(sc.train, sc.held, {("w00", "w01")})["G"], places=9)

    def test_the_empty_set_keeps_nothing_and_has_g_zero(self):
        sc, _tr, _he = planted_scorer()
        r = PL.plant_reading(sc, set())
        self.assertEqual((r["kept"], r["A"], r["C"]), (False, 0.0, None))


class TestPlantStreamBlock(unittest.TestCase):
    def test_B_the_expected_value_the_decomposition_and_plant_beats_null2(self):
        sc, tr, he = planted_scorer()
        b = PL.plant_stream_block(sc, PL.n_plants(tr), PL.n_plants(he), null_draws=100)
        slow = CO.slow_gain(sc.train, sc.held, {ST.PLANT})
        self.assertAlmostEqual(b["B"], slow["G"], places=9)
        self.assertEqual((b["plants_train"], b["plants_held"], b["V"], b["N0"]), (PL.n_plants(tr), PL.n_plants(he), sc.V, sc.n0))
        self.assertAlmostEqual(b["expected_first_order"], PL.n_plants(he) * math.log2(sc.n0 / PL.n_plants(tr)) - 2 * math.log2(sc.V), places=12)
        d = b["decomposition"]
        self.assertAlmostEqual(d["M"] + d["D"] + d["C"] - d["L"], slow["G"], places=8)
        n2 = NL.null2(sc, {ST.PLANT}, rule_tag=5, seed=0, draws=100)
        self.assertAlmostEqual(b["null2_of_plant"]["q95"], n2.q95, places=12)
        self.assertEqual(tuple(b["null2_of_plant"]["values"]), n2.values)                       # the whole draw sequence (here the fallback pool is ONE bigram, so no key shows in the values)
        self.assertEqual(PL.PLANT_NULL_TAG, 5)                                                  # the signed number: AMENDMENT-1 §4 (a) gives the PLANT gate's NULL-2 of the one-frame set the tag 5
        self.assertEqual(b["plant_beats_null2"], bool(b["B"] >= n2.q95))
        self.assertTrue(b["plant_beats_null2"])                                                    # a frequent plant beats NULL-2 (the fallback bins hold only weak real bigrams)
        self.assertGreater(b["null2_of_plant"]["fallbacks"], 0)


class TestGateModes(unittest.TestCase):
    def rows(self, kept, C, A=1.0):
        return [{"seed": i + 1, "kept": kept[i], "C": C[i], "A": A if not isinstance(A, list) else A[i]} for i in range(len(kept))]

    def test_amend1_deterministic_rule_needs_keeps_and_B_and_C(self):
        G = PL.gate_passes
        ok = [{"seed": 0, "kept": True, "C": 5.0, "A": -100.0}]
        self.assertTrue(G("WEB-H", ok, B=3.0, mode="amend1")["pass"])                                # the whole-set A is NOT read in this mode: junk cannot fail it
        self.assertFalse(G("WEB-H", ok, B=0.0, mode="amend1")["pass"])                               # B must be > 0
        self.assertFalse(G("WEB-H", ok, B=-1.0, mode="amend1")["pass"])
        self.assertFalse(G("WEB-H", [{"seed": 0, "kept": True, "C": 0.0, "A": 9.0}], B=3.0, mode="amend1")["pass"])    # C must be > 0
        self.assertFalse(G("WEB-H", [{"seed": 0, "kept": False, "C": None, "A": 9.0}], B=3.0, mode="amend1")["pass"])  # it must keep the frame

    def test_amend1_web_s_counts_a_seed_only_when_it_keeps_and_its_C_is_positive_at_nine_of_ten(self):
        G = PL.gate_passes
        nine = self.rows([True] * 9 + [False], [1.0] * 9 + [None])
        eight = self.rows([True] * 8 + [False, True], [1.0] * 8 + [None, -1.0])                      # the tenth keeps the frame but its C is negative: not counted
        self.assertTrue(G("WEB-S", nine, B=3.0, mode="amend1")["pass"])
        self.assertEqual(G("WEB-S", nine, B=3.0, mode="amend1")["n_counted"], 9)
        self.assertFalse(G("WEB-S", eight, B=3.0, mode="amend1")["pass"])
        self.assertEqual(G("WEB-S", eight, B=3.0, mode="amend1")["n_counted"], 8)
        self.assertFalse(G("WEB-S", nine, B=0.0, mode="amend1")["pass"])                             # B is seed-independent and must hold

    def test_law_mode_reads_the_whole_set(self):
        G = PL.gate_passes
        junk = [{"seed": 0, "kept": True, "C": 5.0, "A": -100.0}]
        self.assertFalse(G("SENTENCE", junk, B=3.0, mode="law")["pass"])                             # the base text's clause: the junk sinks it
        self.assertTrue(G("SENTENCE", [{"seed": 0, "kept": True, "C": -9.0, "A": 2.0}], B=-5.0, mode="law")["pass"])
        web = self.rows([True] * 10, [None] * 10, A=[1.0] * 9 + [-1.0])
        self.assertTrue(G("WEB-S", web, B=0.0, mode="law")["pass"])                                  # 9 of 10 seeds keep the frame with A > 0
        web8 = self.rows([True] * 10, [None] * 10, A=[1.0] * 8 + [-1.0, -1.0])
        self.assertFalse(G("WEB-S", web8, B=0.0, mode="law")["pass"])

    def test_an_unknown_mode_is_refused(self):
        with self.assertRaises(ValueError):
            PL.gate_passes("WEB-H", [{"seed": 0, "kept": True, "C": 1.0, "A": 1.0}], B=1.0, mode="loose")


class TestTheGatesOwnControl(unittest.TestCase):
    def test_a_compressor_whose_parse_never_fires_reads_B_and_C_at_most_zero_and_is_caught(self):
        ms = multiword_stream(2)
        c = PL.plant_gate_control(ms)
        self.assertGreater(c["B_honest"], 0.0)                                                      # the plant pays under the honest parse (so the control is a plant, not a coincidence)
        self.assertGreater(c["C_honest"], 0.0)
        self.assertLessEqual(c["B_broken"], 0.0)
        self.assertLessEqual(c["C_broken"], 0.0)
        self.assertTrue(c["caught"])
        self.assertTrue(c["bytes_changed"])                                                         # the broken parse's train token counts differ from the honest parse's
        self.assertEqual(c["gate_honest"], True)
        self.assertEqual(c["gate_broken"], False)

    def test_the_scorer_honours_a_custom_parse_and_the_default_is_unchanged(self):
        train, held = [["a", "b"], ["a", "b"], ["c"]], [["a", "b"], ["a", "d"], ["c"]]
        F = {("a", "b")}
        default = CO.Scorer(train, held).gain(F)
        explicit = CO.Scorer(train, held, parse=CO.parse_moment).gain(F)
        self.assertEqual(default, explicit)
        never = CO.Scorer(train, held, parse=lambda words, frames: list(words) + [CO.END]).gain(F)
        self.assertNotEqual(never.N, default.N)                                                      # no frame token ever formed: N counts every word
        self.assertEqual(never.N, 5 + 3)                                                             # 5 train words (a b a b c) + 3 END


if __name__ == "__main__":
    unittest.main()
