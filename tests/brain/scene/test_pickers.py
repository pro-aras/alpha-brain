# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:05 +0400 — PREREG-S1C §2 (genome-wt-brain3 docs/brain/r3/PREREG-S1C.md, sha a552515a…) and
# AMENDMENT 1 §3–§4 (PREREG-S1C-AMEND-1.md, sha 825f4ad8…): the held-window LOSS (the learner's own noisy-OR cross-entropy,
# frozen, over the FIXED 13-word vocabulary, an unheard word at σ(0) = 0.5) and the six PICKERS. The planted controls:
# a derangement check that CATCHES the identity and a single fixed point; an exploration checker that CATCHES one flipped
# flag; the NULL with identity credit reproduces PROGRESS's picks exactly; the pin RAISES when the null's credit would land on
# the room that produced it. Test-first: red on scene-s1b1 7706371 (brain.scene.pickers does not exist there).
from __future__ import annotations

import math
import unittest

import numpy as np

from brain.scene import learners as Lr
from brain.scene import pickers as PK

ROOMS = ("R1", "R2", "R3", "N", "K", "U")
VOCAB = ("big", "small", "red", "blue", "green", "yellow", "white", "circle", "square", "triangle", "cross", "ring", "star")
SEED = 20261301


def _toy_learner(n_scenes: int = 60, seed: int = 0) -> Lr.RWLearner:
    rng = np.random.default_rng(seed)
    L = Lr.RWLearner(lr=Lr.LR_S1B1)
    for i in range(n_scenes):
        h = int(rng.integers(1, 4))
        X = rng.normal(size=(h, Lr.RW_DIM))
        words = [VOCAB[int(k)] for k in rng.choice(8, size=int(rng.integers(1, 3)), replace=False)]
        L.train_scene(X, words, rng=np.random.default_rng(i))
    return L


def _window(n: int = 12, seed: int = 1, h_zero: int = 0) -> PK.WindowSet:
    rng = np.random.default_rng(seed)
    Xs, words = [], []
    for i in range(n):
        h = 0 if i < h_zero else int(rng.integers(1, 4))
        Xs.append(rng.normal(size=(h, Lr.RW_DIM)))
        words.append([VOCAB[int(k)] for k in rng.choice(13, size=int(rng.integers(1, 4)), replace=False)])
    return PK.WindowSet(Xs, words, VOCAB)


def _reference_loss(L: Lr.RWLearner, Xs, words) -> float:
    """A per-scene, per-word, per-hypothesis loop of §2's formula (the pin's twin)."""
    tot = []
    for X, ws in zip(Xs, words):
        Z = L.stats.standardise(X) if X.shape[0] else np.zeros((0, Lr.RW_DIM))
        s = 0.0
        for w in VOCAB:
            q = 1.0
            for t in range(Z.shape[0]):
                if w in L.index:
                    j = L.index[w]
                    p = 1.0 / (1.0 + math.exp(-(float(Z[t] @ L.V[j]) + float(L.b[j]))))
                else:
                    p = 0.5
                q *= (1.0 - p)
            P = min(max(1.0 - q, PK.P_CLIP), 1.0 - PK.P_CLIP)
            y = 1.0 if w in ws else 0.0
            s -= y * math.log(P) + (1.0 - y) * math.log(1.0 - P)
        tot.append(s)
    return float(np.mean(tot))


class TestLoss(unittest.TestCase):
    def test_a_fresh_learner_reads_the_prior_half_on_every_word(self) -> None:
        L = Lr.RWLearner(lr=Lr.LR_S1B1)
        ws = _window()
        want = []
        for X, said in zip(ws.Xs, ws.words):
            P = 1.0 - 0.5 ** X.shape[0]
            want.append(-sum(math.log(P) if w in said else math.log(1.0 - P) for w in VOCAB))
        self.assertAlmostEqual(PK.window_loss(L, ws), float(np.mean(want)), places=10)

    def test_equals_the_reference_loop_on_a_trained_learner(self) -> None:
        L = _toy_learner()
        ws = _window(h_zero=2)
        self.assertAlmostEqual(PK.window_loss(L, ws), _reference_loss(L, ws.Xs, ws.words), places=9)
        self.assertEqual(ws.n_empty, 2)

    def test_frozen_the_state_does_not_move(self) -> None:
        L = _toy_learner()
        before = (L.stats.n, L.stats.mean.copy(), L.stats.m2.copy(), L.V.copy(), L.b.copy(), L.scenes)
        PK.window_loss(L, _window())
        self.assertEqual(L.stats.n, before[0])
        for a, b in zip((L.stats.mean, L.stats.m2, L.V, L.b), before[1:5]):
            self.assertTrue(np.array_equal(a, b))
        self.assertEqual(L.scenes, before[5])

    def test_an_unheard_word_enters_at_the_prior_so_hearing_it_moves_nothing(self) -> None:
        L = _toy_learner()
        self.assertNotIn("star", L.index)
        ws = _window()
        a = PK.window_loss(L, ws)
        L._add_word("star")                                   # a new unit starts at v = 0, b = 0: σ(0) = 0.5
        self.assertAlmostEqual(PK.window_loss(L, ws), a, places=12)

    def test_the_scene_level_probability_is_clipped(self) -> None:
        L = _toy_learner()
        j = L.index[VOCAB[0]]
        L.b[j] = 60.0                                         # p ≈ 1 on every thing: log(1 − P) would be −inf unclipped
        v = PK.window_loss(L, _window())
        self.assertTrue(math.isfinite(v))


class TestDerangement(unittest.TestCase):
    def test_from_null_seed_no_fixed_point_deterministic(self) -> None:
        pi = PK.null_derangement(SEED, ROOMS)
        self.assertEqual(sorted(pi), sorted(ROOMS))
        self.assertEqual(sorted(pi.values()), sorted(ROOMS))
        self.assertTrue(all(pi[r] != r for r in ROOMS))
        self.assertEqual(pi, PK.null_derangement(SEED, ROOMS))
        self.assertTrue(PK.is_derangement(pi))
        pi5 = PK.null_derangement(SEED, ROOMS[:5])
        self.assertTrue(PK.is_derangement(pi5) and sorted(pi5) == sorted(ROOMS[:5]))

    def test_planted_identity_and_one_fixed_point_are_caught(self) -> None:
        self.assertFalse(PK.is_derangement({r: r for r in ROOMS}))
        pi = dict(PK.null_derangement(SEED, ROOMS))
        a = ROOMS[0]
        src = next(k for k, v in pi.items() if v == a)             # the room whose credit lands on a
        planted = dict(pi)
        planted[a], planted[src] = a, pi[a]                         # still a permutation, now with a fixed point at a
        self.assertEqual(sorted(planted.values()), sorted(ROOMS))
        self.assertFalse(PK.is_derangement(planted))
        self.assertFalse(PK.is_derangement({"R1": "R2", "R2": "R2"}))     # not a permutation


class TestExploration(unittest.TestCase):
    def test_the_rate_and_the_named_stream(self) -> None:
        draws = [PK.explore_draw(SEED, b, ROOMS) for b in range(7, 2007)]
        rate = sum(d is not None for d in draws) / len(draws)
        self.assertAlmostEqual(rate, PK.EPS, delta=0.02)
        self.assertEqual(draws[:50], [PK.explore_draw(SEED, b, ROOMS) for b in range(7, 57)])
        self.assertEqual(set(d for d in draws if d is not None), set(ROOMS))

    def test_the_checker_catches_one_flipped_flag(self) -> None:
        rec = []
        for b in range(7, 207):
            d = PK.explore_draw(SEED, b, ROOMS)
            rec.append({"block": b, "room": d if d is not None else "R1", "flag": "explore" if d is not None else "policy"})
        self.assertEqual(PK.exploration_mismatches(rec, SEED, ROOMS), [])
        bad = [dict(r) for r in rec]
        k = next(i for i, r in enumerate(bad) if r["flag"] == "policy")
        bad[k]["flag"] = "explore"
        self.assertEqual(PK.exploration_mismatches(bad, SEED, ROOMS), [bad[k]["block"]])
        bad2 = [dict(r) for r in rec]
        k2 = next(i for i, r in enumerate(bad2) if r["flag"] == "explore")
        bad2[k2]["room"] = next(x for x in ROOMS if x != bad2[k2]["room"])
        self.assertEqual(PK.exploration_mismatches(bad2, SEED, ROOMS), [bad2[k2]["block"]])


class _Env:
    """A stub life: a drop per (room, visit) from a fixed table, every other reading from the picker's own road."""

    def __init__(self, seed: int = 5):
        rng = np.random.default_rng(seed)
        self.drops = {r: list(rng.normal(size=300) * (0.1 if r in ("N", "K") else 1.0) + (0.0 if r in ("N", "K") else 1.0))
                      for r in ROOMS}

    def run(self, picker, n_blocks: int = 60):
        last = {r: 0 for r in ROOMS}
        visits = {r: 0 for r in ROOMS}
        L_now = {r: 10.0 + i for i, r in enumerate(ROOMS)}
        out = []
        for b in range(1, n_blocks + 1):
            if b <= len(ROOMS):
                room, flag = ROOMS[b - 1], "round-robin"
            else:
                room, flag = picker.pick(b, PK.Context(last_visit=dict(last), L_now=dict(L_now)))
            d = self.drops[room][visits[room]]
            visits[room] += 1
            credited = picker.observe(b, room, drop=d, drift=abs(d))
            L_now[room] -= d
            last[room] = b
            out.append((b, room, flag, credited))
        return out


class TestPickers(unittest.TestCase):
    def test_progress_estimate_is_the_mean_of_the_last_two_one_until_two(self) -> None:
        p = PK.ProgressPicker(ROOMS, SEED)
        p.observe(1, "R1", drop=0.4, drift=0.0)
        self.assertEqual(p.estimates()["R1"], 0.4)
        p.observe(2, "R1", drop=0.2, drift=0.0)
        self.assertAlmostEqual(p.estimates()["R1"], 0.3)
        p.observe(3, "R1", drop=-0.1, drift=0.0)
        self.assertAlmostEqual(p.estimates()["R1"], 0.05)
        self.assertIsNone(p.estimates()["R2"])

    def test_ties_go_to_the_least_recently_visited(self) -> None:
        self.assertEqual(PK.argmax_lrv({"R1": 1.0, "R2": 1.0, "N": 0.5}, {"R1": 9, "R2": 4, "N": 1}), "R2")
        self.assertEqual(PK.argmax_lrv({"R1": 1.0, "R2": 0.9}, {"R1": 9, "R2": 4}), "R1")

    def test_the_null_with_identity_credit_is_progress(self) -> None:
        a = _Env().run(PK.ProgressPicker(ROOMS, SEED))
        b = _Env().run(PK.NullPicker(ROOMS, SEED, credit={r: r for r in ROOMS}, allow_identity=True))
        self.assertEqual([x[:3] for x in a], [x[:3] for x in b])

    def test_the_null_credits_the_derangement_and_the_pin_raises_on_a_fixed_point(self) -> None:
        nul = PK.NullPicker(ROOMS, SEED)
        rec = _Env().run(nul)
        for b, room, _flag, credited in rec:
            self.assertEqual(credited, nul.pi[room])
            self.assertNotEqual(credited, room)
        planted = dict(nul.pi)
        r0 = ROOMS[0]
        src = [k for k, v in planted.items() if v == r0][0]
        planted[src], planted[r0] = planted[r0], r0
        with self.assertRaises(PK.PickerError):
            PK.NullPicker(ROOMS, SEED, credit=planted)
        bad = PK.NullPicker(ROOMS, SEED)
        bad.pi[r0] = r0                                              # planted after construction: the observe-time pin
        with self.assertRaises(PK.PickerError):
            bad.observe(1, r0, drop=1.0, drift=0.0)

    def test_error_argmax_of_the_loss_now_and_shared_exploration(self) -> None:
        e = PK.ErrorPicker(ROOMS, SEED)
        ctx = PK.Context(last_visit={r: i for i, r in enumerate(ROOMS)}, L_now={"R1": 1, "R2": 2, "R3": 3, "N": 9, "K": 0, "U": 5})
        for b in range(7, 60):
            room, flag = e.pick(b, ctx)
            d = PK.explore_draw(SEED, b, ROOMS)
            self.assertEqual((room, flag), (d, "explore") if d is not None else ("N", "policy"))

    def test_random_uniform_from_its_named_stream_and_the_band_prefix(self) -> None:
        a = [PK.RandomPicker(ROOMS, SEED).pick(b, None)[0] for b in range(7, 1207)]
        c = collections_counter(a)
        for r in ROOMS:
            self.assertAlmostEqual(c[r] / len(a), 1 / 6, delta=0.04)
        b1 = [PK.RandomPicker(ROOMS, SEED, prefix=PK.band_prefix(SEED, 1)).pick(b, None)[0] for b in range(7, 207)]
        b2 = [PK.RandomPicker(ROOMS, SEED, prefix=PK.band_prefix(SEED, 2)).pick(b, None)[0] for b in range(7, 207)]
        self.assertNotEqual(a[:200], b1)
        self.assertNotEqual(b1, b2)
        self.assertEqual(PK.band_prefix(SEED, 3), f"random-band:{SEED}:3:")
        self.assertTrue(all(PK.RandomPicker(ROOMS, SEED).pick(b, None)[1] == "policy" for b in range(7, 20)))

    def test_oracle_within_one_word_then_m1_then_least_recent(self) -> None:
        gains = {"R1": (2, 0.01), "R2": (1, 0.05), "R3": (0, 0.30), "N": (0, 0.2), "K": (-1, 0.0), "U": (1, 0.05)}
        o = PK.OraclePicker(ROOMS, SEED, gain_fn=lambda rooms: gains)
        last = {"R1": 1, "R2": 7, "R3": 3, "N": 4, "K": 5, "U": 6}
        room, flag = o.pick(8, PK.Context(last_visit=last, L_now={}))
        self.assertEqual((room, flag), ("U", "policy"))            # tie {R1 2, R2 1, U 1}; M1: R2 = U = 0.05; U last seen at 6 < 7
        last2 = dict(last, U=9)
        self.assertEqual(o.pick(10, PK.Context(last_visit=last2, L_now={}))[0], "R2")
        gains2 = {"R1": (3, 0.0), "R2": (1, 0.9), "R3": (2, 0.1), "N": (0, 0.0), "K": (0, 0.0), "U": (0, 0.0)}
        o2 = PK.OraclePicker(ROOMS, SEED, gain_fn=lambda rooms: gains2)
        self.assertEqual(o2.pick(8, PK.Context(last_visit=last, L_now={}))[0], "R3")   # R2 is 2 words below the max


class TestDrift(unittest.TestCase):
    def test_displacement_over_path_length(self) -> None:
        th = [np.zeros((13, 147)), np.ones((13, 147)), 2 * np.ones((13, 147)), 3 * np.ones((13, 147))]
        self.assertAlmostEqual(PK.drift_reading(th), 1.0)
        th2 = [np.zeros((13, 147)), np.ones((13, 147)), np.zeros((13, 147))]
        self.assertAlmostEqual(PK.drift_reading(th2), 0.0)
        self.assertEqual(PK.drift_reading([np.zeros((13, 147))] * 3), 0.0)          # no path: 0 (declared)

    def test_theta_over_the_fixed_vocabulary(self) -> None:
        L = _toy_learner()
        th = PK.theta(L, VOCAB)
        self.assertEqual(th.shape, (13, Lr.RW_DIM + 1))
        for c, w in enumerate(VOCAB):
            if w in L.index:
                self.assertTrue(np.array_equal(th[c, :-1], L.V[L.index[w]]))
                self.assertEqual(th[c, -1], L.b[L.index[w]])
            else:
                self.assertFalse(th[c].any())


def collections_counter(xs):
    import collections
    return collections.Counter(xs)


if __name__ == "__main__":
    unittest.main()
