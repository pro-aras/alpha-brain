# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:5x +0400 — L-11 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md
# task 3): SENTENCE's frame-finder, at the unit level (no genome parsing, no Mind, no Organism -- the toy
# builds a fake episode store directly, genome/sentence.py's own `_FakeEpisode`).
from __future__ import annotations

import unittest

import numpy as np

from genome.sentence import episodes_from_missions, find_frames, synthetic_missions


class TestFindFramesBasics(unittest.TestCase):
    def test_empty_store_finds_nothing(self) -> None:
        self.assertEqual(find_frames(None), [])
        self.assertEqual(find_frames(episodes_from_missions([])), [])

    def test_a_single_word_episode_never_contributes(self) -> None:
        """words_in_instant with < 2 distinct words (a world_maker canvas, one ear row) is excluded from N."""
        from genome.sentence import _FakeEpisode
        ep = _FakeEpisode([{"id": 0, "words_in_instant": ["circle"]}] * 10)
        self.assertEqual(find_frames(ep), [])

    def test_ordered_means_temporal_not_every_permutation(self) -> None:
        """"ordered" means the TEMPORAL order words_in_instant preserves (colour before object, game.py's
        own publish order) -- (object, colour) must never be filed at all (it never occurs as a temporal
        pair), never merely 'filed with a different count'. Counting every permutation would make (w1,w2)
        and (w2,w1) perfectly correlated (identical episode sets) and cap precision at 0.5 by construction."""
        missions = [("red", "ball")] * 6 + [("blue", "key"), ("green", "box"), ("blue", "box"), ("green", "key")]
        ep = episodes_from_missions(missions)
        rows = find_frames(ep, min_count=5, factor=1.5)
        pairs = {(r["w1"], r["w2"]) for r in rows}
        self.assertIn(("red", "ball"), pairs)
        self.assertNotIn(("ball", "red"), pairs, "the reverse direction never occurs as a temporal pair")

        # the general property, over the (two-pair) skewed toy corpus too: whichever pairs fire, their
        # REVERSE is never also filed (every episode's words_in_instant is [colour, object] in that order).
        rng = np.random.default_rng(20260922)
        skewed = synthetic_missions(rng, n=50, skew_pairs=sorted({("red", "ball"), ("blue", "key")}), skew_share=0.7)
        rows2 = find_frames(episodes_from_missions(skewed), min_count=5, factor=2.0)
        pairs2 = {(r["w1"], r["w2"]) for r in rows2}
        for w1, w2 in pairs2:
            self.assertNotIn((w2, w1), pairs2, f"both ({w1},{w2}) and ({w2},{w1}) filed -- not ordered")

    def test_episodes_cited_are_exactly_the_qualifying_ones(self) -> None:
        # 6 "red ball" instants plus enough uniform background noise that "red"/"ball" are each only a
        # small share of their own marginals -- so count(6) clears both count>=min_count and count>2x
        # expected, and the exact set of 6 citing episode ids is checkable against the corpus by hand.
        missions = [("red", "ball")] * 6 + [("blue", "key"), ("green", "box"), ("blue", "box"), ("green", "key")]
        ep = episodes_from_missions(missions)
        rows = find_frames(ep, min_count=5, factor=1.5)
        row = next(r for r in rows if (r["w1"], r["w2"]) == ("red", "ball"))
        self.assertEqual(row["episodes"], [0, 1, 2, 3, 4, 5])
        self.assertEqual(row["count"], 6)


class TestFindFramesRingWrap(unittest.TestCase):
    """edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 -- advisor-caught: find_frames() used
    to iterate `range(len(episodes))` and pass each index straight to `.get()` as if it were an EPISODE ID;
    once the FAST ring wraps (n_written > cap) those low ids are exactly the EVICTED ones and every live id
    is skipped, so a long life's frame-finder goes silently dead the moment its ring fills. Fixture: cap=5,
    8 writes (ids 0..7) -- ids 0,1,2 evicted (unrelated noise, irrelevant either way); ids 3,4,5 = "red
    ball" (x3, live); ids 6,7 = one unrelated live pair each (live noise, lowers the independence
    expectation exactly as the skewed-corpus toy above does)."""

    def _ring(self):
        from genome.sentence import _FakeEpisode
        rows = ([{"id": i, "words_in_instant": ["cyan", "hat"]} for i in range(3)]
                + [{"id": i, "words_in_instant": ["red", "ball"]} for i in range(3, 6)]
                + [{"id": 6, "words_in_instant": ["blue", "key"]}, {"id": 7, "words_in_instant": ["green", "box"]}])
        return _FakeEpisode(rows, cap=5)

    def test_only_the_live_ring_slots_are_counted_after_a_wrap(self) -> None:
        ep = self._ring()
        self.assertEqual(len(ep), 5, "len() mirrors genome.fast.Episodes: min(n_written, cap)")
        self.assertIsNone(ep.get(0), "evicted by the ring")
        self.assertIsNone(ep.get(2), "evicted by the ring")
        self.assertIsNotNone(ep.get(3), "still live")

        rows_found = find_frames(ep, min_count=3, factor=1.5)
        self.assertEqual(len(rows_found), 1)
        row = rows_found[0]
        self.assertEqual((row["w1"], row["w2"]), ("red", "ball"))
        self.assertEqual(row["count"], 3, "only the 3 LIVE red-ball episodes (ids 3,4,5)")
        self.assertEqual(row["episodes"], [3, 4, 5])

    def test_the_old_range_len_approach_would_have_found_nothing_on_this_fixture(self) -> None:
        """Documents the bug this test class guards against: the buggy loop asked episodes.get(i) for
        i in range(len(episodes)) == range(5) == ids 0..4 -- three of which (0,1,2) are evicted and the
        other two (3,4) are only PART of the live red-ball set, so it would have undercounted "red ball" to
        2 (< min_count=3) and filed nothing, despite 3 live qualifying episodes and a clean signal."""
        ep = self._ring()
        buggy_ids_visited = list(range(len(ep)))
        self.assertEqual(buggy_ids_visited, [0, 1, 2, 3, 4])
        live_among_them = [i for i in buggy_ids_visited if ep.get(i) is not None]
        self.assertEqual(live_among_them, [3, 4], "only 2 of the 3 live red-ball episodes ever visited")


class TestUniformWorldFilesNothing(unittest.TestCase):
    """The RAISED clause's own demonstration (genome/sentence.py's module docstring): a UNIFORM (colour,
    object) draw puts every pair at ~1x its independence expectation, so the >2x bar cannot fire."""

    def test_uniform_missions_file_no_frames(self) -> None:
        rng = np.random.default_rng(7)
        missions = synthetic_missions(rng, n=900, skew_pairs=None)   # no skew -> uniform over the 3x3 grid
        ep = episodes_from_missions(missions)
        rows = find_frames(ep, min_count=5, factor=2.0)
        self.assertEqual(rows, [], "a uniform mission distribution must file nothing (count ~= expected everywhere)")


class TestSkewedToyPrecision(unittest.TestCase):
    """L-11 task 3's own toy (the brief, verbatim): '50 synthetic missions over {red, blue, green} x
    {ball, key, box} with the eye's truth -> the frames filed have precision >= 0.8 against the truth; the
    shuffled twin <= 0.3.' The corpus must be SKEWED toward the truth pairs for the >2x-independence bar to
    have anything to find at all (see genome/sentence.py's module docstring, and this file's own
    TestUniformWorldFilesNothing above) -- skewed exactly as the plan's own worked example names it:
    'red ball' and 'blue key' are the frames filed."""

    TRUTH = {("red", "ball"), ("blue", "key")}

    def _precision(self, rows) -> float:
        if not rows:
            return 0.0
        filed = {(r["w1"], r["w2"]) for r in rows}
        return len(filed & self.TRUTH) / len(filed)

    def test_skewed_corpus_precision_at_least_0_8(self) -> None:
        rng = np.random.default_rng(20260922)
        missions = synthetic_missions(rng, n=50, skew_pairs=sorted(self.TRUTH), skew_share=0.7)
        ep = episodes_from_missions(missions)
        rows = find_frames(ep, min_count=5, factor=2.0)
        self.assertGreaterEqual(len(rows), 1, "the skewed toy must file at least one frame")
        precision = self._precision(rows)
        self.assertGreaterEqual(precision, 0.8, f"filed pairs: {[(r['w1'], r['w2']) for r in rows]}")

    def test_shuffled_pairing_twin_precision_at_most_0_3(self) -> None:
        """The blind twin (the reader's own --blind frame-shuffle, L-1's job -- exercised here at the
        function level): the SAME skewed corpus with the colour<->object pairing shuffled ACROSS missions
        (destroying which colour went with which object, while keeping each marginal's frequency
        unchanged) must file at (or under) chance precision."""
        rng = np.random.default_rng(20260922)
        missions = synthetic_missions(rng, n=50, skew_pairs=sorted(self.TRUTH), skew_share=0.7)
        colours = [c for c, _o in missions]
        objects = [o for _c, o in missions]
        shuffle_rng = np.random.default_rng(1)
        shuffled_objects = list(objects)
        shuffle_rng.shuffle(shuffled_objects)
        shuffled = list(zip(colours, shuffled_objects))
        ep = episodes_from_missions(shuffled)
        rows = find_frames(ep, min_count=5, factor=2.0)
        precision = self._precision(rows)
        self.assertLessEqual(precision, 0.3, f"shuffled twin filed pairs: {[(r['w1'], r['w2']) for r in rows]}")


if __name__ == "__main__":
    unittest.main()
