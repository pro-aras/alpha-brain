"""test_curiosity.py — B10 (docs/G4-PREREG.md §11.2): genome/curiosity.py's Interests.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new file, Wave 2 B10.

The required toy (§11.2): "on a pool where one kind of item can be answered and another only parks,
after 50 choices the answerable kind is chosen >= 3x as often as by the random twin; the twin is
choose with weights ignored." Plus direct unit tests for choose (ties by rng, birth at 1.0), update's
four operators (generalize/specialize/bridge/recombine), state()/save()/load(), and the population cap.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome.curiosity import Interests, choose_uniform


def _pool(n_word: int, n_sight: int) -> list:
    pool = [{"kind": "word", "key": f"w{i}", "episode": None, "pred": None} for i in range(n_word)]
    pool += [{"kind": "sight", "key": f"s{i}", "episode": None, "pred": None} for i in range(n_sight)]
    return pool


def _outcome_of(item) -> str:
    # the toy's rule: "word" kind items can be answered, "sight" kind items only park.
    return "answered" if item["kind"] == "word" else "parked"


def _run_real(seed: int, rounds: int = 50, n_word: int = 2, n_sight: int = 8) -> int:
    rng = np.random.default_rng(seed)
    interests = Interests(n=20, rng=rng)
    pool = _pool(n_word, n_sight)
    word_picks = 0
    for _ in range(rounds):
        item = interests.choose(pool, rng)
        if item["kind"] == "word":
            word_picks += 1
        interests.update(item, _outcome_of(item))
    return word_picks


def _run_null(seed: int, rounds: int = 50, n_word: int = 2, n_sight: int = 8) -> int:
    rng = np.random.default_rng(seed)
    pool = _pool(n_word, n_sight)
    word_picks = 0
    for _ in range(rounds):
        item = choose_uniform(pool, rng)
        if item["kind"] == "word":
            word_picks += 1
        # the null twin never updates weights — it has none.
    return word_picks


class TestCuriosityToy(unittest.TestCase):
    """§11.2: after 50 choices, the answerable kind ('word') is chosen >= 3x as often by the real
    Interests as by the uniform null twin. Three fixed seeds, printed and asserted individually and
    on the mean (matching the estate's "3 seeds, report every number" convention)."""

    def test_bar_3x_after_50_choices(self) -> None:
        seeds = [9, 10, 11]
        real_counts = [_run_real(s) for s in seeds]
        null_counts = [_run_null(s) for s in seeds]
        lines = []
        for s, r, n in zip(seeds, real_counts, null_counts):
            ratio = (r / n) if n else float("inf")
            lines.append(f"seed={s} real={r}/50 null={n}/50 ratio={ratio}")
        msg = "; ".join(lines)
        for s, r, n in zip(seeds, real_counts, null_counts):
            with self.subTest(seed=s):
                # n could be 0 (uniform twin never picked a word item in 50/50 draws at 20% base
                # rate — im/possible but vanishingly unlikely at these seeds); guard it explicitly.
                if n == 0:
                    self.assertGreater(r, 0, f"real picked 0 words too ({msg})")
                else:
                    self.assertGreaterEqual(r, 3 * n, f"bar missed: {msg}")
        # also report the pooled numbers, since the PREREG asks for "the answerable kind is chosen"
        # as a population statement, not only a per-seed one.
        total_real, total_null = sum(real_counts), sum(null_counts)
        self.assertGreaterEqual(total_real, 3 * total_null, f"pooled bar missed: {lines}")


class TestChoose(unittest.TestCase):
    def test_unseen_item_born_at_weight_1(self) -> None:
        rng = np.random.default_rng(1)
        interests = Interests(n=10, rng=rng)
        item = {"kind": "sight", "key": "x", "episode": None, "pred": None}
        interests.choose([item], rng)
        self.assertEqual(interests.weights[("sight", "x")], 1.0)

    def test_highest_weight_wins_no_tie(self) -> None:
        rng = np.random.default_rng(2)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        b = {"kind": "word", "key": "b", "episode": None, "pred": None}
        interests.choose([a, b], rng)  # births both at 1.0 (tie, either may win)
        interests.update(a, "answered")  # a's kind (word) generalizes +0.5 to BOTH a and b
        interests.weights[("word", "a")] += 1.0  # force a strictly ahead
        picked = interests.choose([a, b], rng)
        self.assertEqual(picked["key"], "a")

    def test_ties_broken_by_rng_not_always_first(self) -> None:
        # two freshly-seen items are both born at weight 1.0 — a tie. Across many rng seeds the
        # first pool slot must not always win, or choose() is silently list-order, not rng.
        a = {"kind": "sight", "key": "a", "episode": None, "pred": None}
        b = {"kind": "sight", "key": "b", "episode": None, "pred": None}
        first_wins = 0
        for seed in range(30):
            rng = np.random.default_rng(seed)
            interests = Interests(n=10, rng=rng)
            picked = interests.choose([a, b], rng)
            if picked["key"] == "a":
                first_wins += 1
        self.assertGreater(first_wins, 0)
        self.assertLess(first_wins, 30)

    def test_choose_empty_pool_refused(self) -> None:
        rng = np.random.default_rng(1)
        interests = Interests(n=10, rng=rng)
        with self.assertRaises(ValueError):
            interests.choose([], rng)


class TestUpdateOperators(unittest.TestCase):
    def test_generalize_answered_bumps_whole_kind(self) -> None:
        rng = np.random.default_rng(3)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        b = {"kind": "word", "key": "b", "episode": None, "pred": None}
        interests._weight_of(a)
        interests._weight_of(b)
        interests.update(a, "answered")
        # both a and b are "word" kind; both got +0.5 (a's own answer also triggers its generalize
        # pass over the whole kind population, itself included)
        self.assertEqual(interests.weights[("word", "a")], 1.5)
        self.assertEqual(interests.weights[("word", "b")], 1.5)

    def test_specialize_parked_halves_only_that_item(self) -> None:
        rng = np.random.default_rng(4)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "sight", "key": "a", "episode": None, "pred": None}
        b = {"kind": "sight", "key": "b", "episode": None, "pred": None}
        interests._weight_of(a)
        interests._weight_of(b)
        interests.update(a, "parked")
        self.assertEqual(interests.weights[("sight", "a")], 0.5)
        self.assertEqual(interests.weights[("sight", "b")], 1.0)  # untouched

    def test_bridge_new_item_whose_key_is_a_known_word(self) -> None:
        rng = np.random.default_rng(5)
        interests = Interests(n=10, rng=rng)
        word_circle = {"kind": "word", "key": "circle", "episode": None, "pred": None}
        interests._weight_of(word_circle)  # "circle" is now a known word
        sight_circle = {"kind": "sight", "key": "circle", "episode": None, "pred": None}
        w = interests._weight_of(sight_circle)  # a NEW (sight, circle) — key matches a known word
        self.assertEqual(w, 1.25)

    def test_bridge_does_not_fire_for_an_unknown_key(self) -> None:
        rng = np.random.default_rng(6)
        interests = Interests(n=10, rng=rng)
        sight_square = {"kind": "sight", "key": "square", "episode": None, "pred": None}
        w = interests._weight_of(sight_square)  # "square" was never a known word
        self.assertEqual(w, 1.0)

    def test_recombine_two_answered_in_same_window_average(self) -> None:
        rng = np.random.default_rng(7)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        b = {"kind": "word", "key": "b", "episode": None, "pred": None}
        interests._weight_of(a)
        interests._weight_of(b)
        interests.weights[("word", "a")] = 3.0
        interests.weights[("word", "b")] = 1.0
        interests.update(a, "answered")  # generalize: a=3.5, b=1.5 (first answer this window)
        interests.update(b, "answered")  # generalize: a=4.0, b=2.0; then recombine a&b -> mean 3.0
        self.assertEqual(interests.weights[("word", "a")], 3.0)
        self.assertEqual(interests.weights[("word", "b")], 3.0)

    def test_sleep_boundary_starts_a_fresh_recombine_chain(self) -> None:
        rng = np.random.default_rng(8)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        b = {"kind": "word", "key": "b", "episode": None, "pred": None}
        interests._weight_of(a)
        interests._weight_of(b)
        interests.weights[("word", "a")] = 3.0
        interests.weights[("word", "b")] = 1.0
        interests.update(a, "answered")  # generalize: a=3.5, b=1.5
        interests.sleep_boundary()  # closes the window before b is answered
        wa_before, wb_before = interests.weights[("word", "a")], interests.weights[("word", "b")]
        interests.update(b, "answered")  # generalize only (new window) — no recombine with a
        # if recombine had (wrongly) fired across the boundary, a and b would now be forced equal;
        # confirm they instead just each got their own +0.5 generalize bump.
        self.assertNotEqual(interests.weights[("word", "a")], interests.weights[("word", "b")])
        self.assertEqual(interests.weights[("word", "a")], wa_before + 0.5)
        self.assertEqual(interests.weights[("word", "b")], wb_before + 0.5)

    def test_filed_and_scored_are_noop_on_weights(self) -> None:
        rng = np.random.default_rng(9)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "due", "key": "a", "episode": None, "pred": None}
        interests._weight_of(a)
        interests.update(a, "filed")
        interests.update(a, "scored")
        self.assertEqual(interests.weights[("due", "a")], 1.0)
        self.assertEqual(interests.state()["outcomes"]["filed"], 1)
        self.assertEqual(interests.state()["outcomes"]["scored"], 1)

    def test_unknown_outcome_refused(self) -> None:
        rng = np.random.default_rng(10)
        interests = Interests(n=10, rng=rng)
        a = {"kind": "due", "key": "a", "episode": None, "pred": None}
        with self.assertRaises(ValueError):
            interests.update(a, "bogus")


class TestPruneAndState(unittest.TestCase):
    def test_population_cap_drops_lowest_weight(self) -> None:
        rng = np.random.default_rng(11)
        interests = Interests(n=3, rng=rng)
        items = [{"kind": "sight", "key": f"s{i}", "episode": None, "pred": None} for i in range(5)]
        for it in items:
            interests._weight_of(it)
        interests.weights[("sight", "s0")] = 5.0
        interests.weights[("sight", "s1")] = 4.0
        interests.weights[("sight", "s2")] = 0.1
        interests.weights[("sight", "s3")] = 0.2
        interests.weights[("sight", "s4")] = 0.3
        interests.update(items[0], "filed")  # any update() call triggers _prune()
        self.assertEqual(len(interests.weights), 3)
        self.assertIn(("sight", "s0"), interests.weights)
        self.assertIn(("sight", "s1"), interests.weights)
        self.assertNotIn(("sight", "s2"), interests.weights)

    def test_state_shape(self) -> None:
        rng = np.random.default_rng(12)
        interests = Interests(n=5, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        interests.update(a, "answered")
        st = interests.state()
        self.assertEqual(st["n"], 5)
        self.assertEqual(st["count"], 1)
        self.assertIn("word:a", st["weights"])
        self.assertEqual(st["outcomes"]["answered"], 1)


class TestSaveLoad(unittest.TestCase):
    def test_round_trip(self) -> None:
        rng = np.random.default_rng(13)
        interests = Interests(n=5, rng=rng)
        a = {"kind": "word", "key": "a", "episode": None, "pred": None}
        b = {"kind": "sight", "key": "circle", "episode": None, "pred": None}
        interests.update(a, "answered")
        interests.update(b, "parked")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "interests.json"
            interests.save(path)
            self.assertTrue(path.exists())
            with open(path) as f:
                json.load(f)  # must be valid JSON
            loaded = Interests(n=1, rng=np.random.default_rng(0))
            loaded.load(path)
        self.assertEqual(loaded.n, 5)
        self.assertEqual(loaded.weights, interests.weights)
        self.assertEqual(loaded._known_words, interests._known_words)


if __name__ == "__main__":
    unittest.main()
