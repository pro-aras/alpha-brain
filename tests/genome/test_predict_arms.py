"""test_predict_arms.py — G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md; docs/organs/MIND-MEMORY.md §4
G-MIND-3): the three new PREDICT error arms (conjunctive, episodic, comparator), each tested against a
tiny hand-built organism so the arithmetic is checked by hand, not just replayed at scale (that proof is
runs/g5-e-arms/ and G5-E-REPORT.md, not a unit test — an 18,959-row tape does not belong in a suite that
must stay fast).

edit: Claude (Sonnet 5, builder E), 2026-09-21 16:58 +0400 — G5-E.
"""
from __future__ import annotations

import unittest

import numpy as np

from genome.fast import Episodes
from genome.machinery import Organism, parse_genome
from genome.predict import Predictor
from genome.world import encode_word

from ._toy import mini_genome, onehot, unit, SIGHT_DIM, WORDS_DIM


class TestNoveltyArmUnchanged(unittest.TestCase):
    """The pin: the default arm ("novelty", whether the Predictor is built with no `arm` kwarg at all
    or explicitly `arm="novelty"`) must read EXACTLY what error() read before this brief — the same six
    lines, now wrapped, produce the same float for the same inputs. Fixture values captured from the
    pre-edit formula by hand (not re-derived from the new code — that would only prove the new code
    agrees with itself)."""

    def test_default_ctor_is_arm_novelty(self) -> None:
        org = Organism(mini_genome())
        pred = Predictor(org)
        self.assertEqual(pred.arm, "novelty")

    def test_nothing_born_yet_reads_maximal_surprise(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        for arm in ("novelty", None):
            pred = Predictor(org) if arm is None else Predictor(org, arm=arm)
            self.assertEqual(pred.error(unit(np.random.default_rng(1))), 1.0)

    def test_exact_repeat_after_birth_reads_zero(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="novelty")
        x = unit(np.random.default_rng(3))
        xw = encode_word("bar", org.g.ear_blank_zero)
        self.assertEqual(pred.error(x, word="bar", xw=xw), 1.0)   # nothing alive -> births on moment()
        org.moment(x, xw)
        self.assertEqual(pred.error(x, word="bar", xw=xw), 0.0)   # exact repeat of the now-alive cell -> cos=1.0 -> 1-1.0=0.0

    def test_word_xw_episodes_kwargs_are_ignored_by_novelty(self) -> None:
        """The whole point of the byte-identity proof: passing the new kwargs to the "novelty" arm must
        never change its reading — mind.py now passes them unconditionally on every call."""
        org = Organism(mini_genome(theta_n=0.9))
        x = unit(np.random.default_rng(9))
        xw = encode_word("moon", org.g.ear_blank_zero)
        eps = Episodes(100, SIGHT_DIM, WORDS_DIM)
        eps.write(moment=0, x_s=unit(np.random.default_rng(2)), x_w=xw, word="moon", surprise=0.5)
        bare = Predictor(org, arm="novelty").error(x)
        fed = Predictor(org, arm="novelty").error(x, word="moon", xw=xw, episodes=eps)
        self.assertEqual(bare, fed)


class TestConjunctiveArm(unittest.TestCase):
    """arm A: err = max(sight_novelty, word_novelty); word_novelty=1.0 held for showings 1-3 of a word
    (G-MIND-3's own table), 0.0 from the 4th on. Isolate word_novelty's effect by repeating the SAME
    sight vector every canvas, so sight_novelty drops to 0.0 after the first birth and stays there —
    whatever the test reads past canvas 1 is word_novelty alone."""

    def test_word_novelty_held_for_first_three_showings_then_falls(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="conjunctive")
        x = unit(np.random.default_rng(11))
        xw = encode_word("bar", org.g.ear_blank_zero)

        errs = []
        for _ in range(5):
            errs.append(pred.error(x, word="bar", xw=xw))
            org.moment(x, xw)   # births the sight cell on canvas 1; every later canvas is an exact repeat

        # canvas 1: area.n==0 -> sight_novelty=1.0 (max already 1.0 regardless of word_novelty)
        self.assertEqual(errs[0], 1.0)
        # canvases 2 and 3: sight_novelty=0.0 (exact repeat, resonates at cos=1.0) but word_novelty=1.0
        # (prior deliveries 1 and 2, both < 3) -> max(0.0, 1.0) = 1.0
        self.assertEqual(errs[1], 1.0, "2nd showing: word_novelty must still be 1.0 (prior=1 < 3)")
        self.assertEqual(errs[2], 1.0, "3rd showing: word_novelty must still be 1.0 (prior=2 < 3) — G-MIND-3's own table")
        # canvases 4 and 5: prior deliveries 3 and 4, both >= 3 -> word_novelty=0.0; sight_novelty=0.0 too
        self.assertEqual(errs[3], 0.0, "4th showing: word_novelty must have fallen to 0.0 (prior=3, not < 3)")
        self.assertEqual(errs[4], 0.0)

    def test_a_different_word_on_an_already_known_sight_still_spikes(self) -> None:
        """The mechanism this arm exists for: a familiar-looking glance under a BRAND NEW word must
        still read a high error even though sight_novelty alone would read ~0 (the moon-resonates-circle
        case, MIND-MEMORY §1.4/§4)."""
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="conjunctive")
        x = unit(np.random.default_rng(21))
        xw_bar = encode_word("bar", org.g.ear_blank_zero)
        pred.error(x, word="bar", xw=xw_bar)
        org.moment(x, xw_bar)   # "bar" now known; x's sight cell alive
        xw_zog = encode_word("zog", org.g.ear_blank_zero)   # never-heard word, SAME-LOOKING glance
        e = pred.error(x, word="zog", xw=xw_zog)
        self.assertEqual(e, 1.0, "a never-heard word on an already-familiar shape must still spike (word_novelty=1.0)")

    def test_sight_only_canvas_has_no_word_to_be_new(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="conjunctive")
        x = unit(np.random.default_rng(31))
        e1 = pred.error(x, word=None, xw=None)
        self.assertEqual(e1, 1.0)   # sight_novelty alone: nothing born yet
        org.moment_sight(x)
        e2 = pred.error(x, word=None, xw=None)
        self.assertEqual(e2, 0.0, "sight-only: word_novelty is always 0.0, so err falls back to sight_novelty exactly")


class TestEpisodicArm(unittest.TestCase):
    """arm B: err = clip(max(0, cos_to_nearest_CELL - cos_to_nearest_EPISODE), 0, 2). Needs a real FAST
    store (never mutated by error() — Episodes.nearest is read-only by its own docstring)."""

    def test_bootstrap_nothing_born_nothing_written_reads_zero(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="episodic")
        eps = Episodes(100, SIGHT_DIM, WORDS_DIM)
        x = unit(np.random.default_rng(41))
        self.assertEqual(pred.error(x, episodes=eps), 0.0, "both cos default to -1.0 at the very first canvas: 0 gap, not invented as a spike")

    def test_episodes_none_behaves_like_an_empty_store(self) -> None:
        org = Organism(mini_genome(theta_n=0.9))
        pred = Predictor(org, arm="episodic")
        x = unit(np.random.default_rng(42))
        self.assertEqual(pred.error(x, episodes=None), 0.0)

    def test_prototype_explains_a_glance_no_episode_is_near(self) -> None:
        """The mechanism: a cell resonates strongly (a good prototype match) but the FAST ring holds no
        episode anywhere near this exact glance -> a real, positive gap."""
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="episodic")
        rng = np.random.default_rng(51)
        base = unit(rng)
        org.moment_sight(base)   # births a sight cell holding `base` verbatim
        eps = Episodes(100, SIGHT_DIM, WORDS_DIM)
        far = unit(rng)   # an independent random unit vector: cosine to `base` near 0 with overwhelming probability in 64-d
        eps.write(moment=0, x_s=far, x_w=np.zeros(WORDS_DIM), word="", surprise=0.0)
        near_base = base + 0.0 * base   # the exact glance the cell was born on: cos_cell = 1.0
        e = pred.error(near_base, episodes=eps)
        cos_far = float(far @ near_base)
        self.assertAlmostEqual(e, max(0.0, 1.0 - cos_far), places=9)
        self.assertGreater(e, 0.5, f"a near-orthogonal episode must leave a large explanatory gap (got {e})")

    def test_a_real_matching_episode_closes_the_gap_to_zero(self) -> None:
        """The other half: when the FAST store DOES hold an episode right at this glance, the gap must
        collapse to (clipped) zero — the CA1-style "the prototype explains nothing more than memory
        already does" case."""
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="episodic")
        rng = np.random.default_rng(61)
        base = unit(rng)
        org.moment_sight(base)
        eps = Episodes(100, SIGHT_DIM, WORDS_DIM)
        eps.write(moment=0, x_s=base, x_w=np.zeros(WORDS_DIM), word="", surprise=0.0)   # the SAME vector as the episode
        e = pred.error(base, episodes=eps)
        self.assertEqual(e, 0.0, "cos_cell == cos_episode (both 1.0 to the same vector) -> gap 0")

    def test_never_mutates_the_store(self) -> None:
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="episodic")
        eps = Episodes(100, SIGHT_DIM, WORDS_DIM)
        eps.write(moment=0, x_s=unit(np.random.default_rng(71)), x_w=np.zeros(WORDS_DIM), word="x", surprise=0.0)
        n_before = eps.n_written
        pred.error(unit(np.random.default_rng(72)), episodes=eps)
        self.assertEqual(eps.n_written, n_before, "Episodes.nearest is read-only; error() must never write")


class TestComparatorArm(unittest.TestCase):
    """arm C: err = 1.0 when the winning sight cell's established answer is not among this moment's WORD
    winners; the graded novelty otherwise. Reimplements Organism._misfire's read-only predicate."""

    def test_matching_word_reads_graded_novelty(self) -> None:
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(81))
        xw = encode_word("bar", org.g.ear_blank_zero)
        org.moment(x, xw)   # "bar" -> sight cell 0 <-> words cell 0, an edge born
        e = pred.error(x, word="bar", xw=xw)   # the SAME word again: the sight winner's established answer IS this moment's word winner
        c = org.sight.cos(x); cmax = float(c.max())
        self.assertAlmostEqual(e, max(0.0, min(2.0, 1.0 - cmax)), places=9)
        self.assertLess(e, 0.5, f"a matching answer must read the (small) graded novelty, not a maximal surprise (got {e})")

    def test_mismatched_word_reads_maximal_surprise(self) -> None:
        """The mechanism this arm exists for: the moon resonates the circle cell, whose established
        answer is «circle», but the word that arrives is «moon» -> err = 1.0 however well the shape
        matches."""
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(91))
        xw_circle = encode_word("circle", org.g.ear_blank_zero)
        org.moment(x, xw_circle)   # x <-> "circle"
        xw_moon = encode_word("moon", org.g.ear_blank_zero)   # a DIFFERENT word, same-looking glance x
        e = pred.error(x, word="moon", xw=xw_moon)
        self.assertEqual(e, 1.0, "the established answer (circle) is not among this moment's word winners (moon) -> maximal surprise")

    def test_no_established_answer_yet_falls_back_to_graded_novelty(self) -> None:
        """No edge yet -> _answer_of returns None -> _misfire's own `continue` case -> nothing to
        violate, graded novelty (never a manufactured 1.0)."""
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(101))
        org.moment_sight(x)   # births a sight cell with NO edge (moment_sight never wires)
        xw = encode_word("bar", org.g.ear_blank_zero)
        e = pred.error(x, word="bar", xw=xw)
        c = org.sight.cos(x); cmax = float(c.max())
        self.assertAlmostEqual(e, max(0.0, min(2.0, 1.0 - cmax)), places=9)

    def test_sight_only_canvas_falls_back_to_graded_novelty(self) -> None:
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(111))
        org.moment_sight(x)
        e = pred.error(x, word=None, xw=None)
        c = org.sight.cos(x); cmax = float(c.max())
        self.assertAlmostEqual(e, max(0.0, min(2.0, 1.0 - cmax)), places=9)

    def test_nothing_resonates_reads_maximal_surprise(self) -> None:
        org = Organism(mini_genome(theta_n=0.999))   # near-impossible to resonate on a random draw
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(121))
        org.moment_sight(x)   # one cell, born from x itself
        y = unit(np.random.default_rng(122))   # an independent draw: cos(x, y) near 0 << theta
        xw = encode_word("bar", org.g.ear_blank_zero)
        e = pred.error(y, word="bar", xw=xw)
        self.assertEqual(e, 1.0)

    def test_never_births_or_mutates_misfire_counters(self) -> None:
        """error() must be read-only on the organism: no births, no misfire-counter movement, no edges —
        _misfire (the mechanism this arm reimplements) does all three; this reimplementation must do
        none of them."""
        org = Organism(mini_genome(theta_n=0.5))
        pred = Predictor(org, arm="comparator")
        x = unit(np.random.default_rng(131))
        xw = encode_word("bar", org.g.ear_blank_zero)
        org.moment(x, xw)
        n_sight_before, n_words_before = org.sight.n, org.words.n
        births_before = len(org.births)
        misfires_before = org.sight.misfires.copy()
        edges_before = len(org.edges_log)
        for word, w in (("bar", xw), ("zog", encode_word("zog", org.g.ear_blank_zero))):
            pred.error(x, word=word, xw=w)
        self.assertEqual(org.sight.n, n_sight_before); self.assertEqual(org.words.n, n_words_before)
        self.assertEqual(len(org.births), births_before)
        self.assertTrue(np.array_equal(org.sight.misfires, misfires_before))
        self.assertEqual(len(org.edges_log), edges_before)


if __name__ == "__main__":
    unittest.main()
