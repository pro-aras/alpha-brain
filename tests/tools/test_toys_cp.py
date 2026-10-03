"""Tests for TOY A (compression-progress curiosity): the losses, the estimators, the life's identity with S1c's own records, the report's statistics.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:23 +0400 — written FIRST (law: docs/research/toys/PREREG-TOY-CP.md, base text sha256
# 726d0329…, co-signed 11:13, and PREREG-TOY-CP-AMEND-1.md): red before any module under tools/toys/cp exists, green after.

THE GROUPS
  Losses       L equals pickers.window_loss; C on an untrained learner is log|T| per pair; C equals a slow per-(scene, type) recomputation to
               1e-9; an empty scene contributes the uniform; the snapshot stand-in reads the learner's own loss; the prequential loss equals
               pickers.scene_losses on a one-scene window.
  Estimators   hand-computed tables (own / hist x last2 / ema; L and C tables kept apart); one visited room: hist == own; ema's first value
               initialises; LP-OUDEYER on a hand-written list; the epsilon streams; the tie rule; the NULL's credit (never on its producer,
               identity credit reproduces the arm, a planted fixed point RAISES); planted swaps and a planted zero history weight are CAUGHT;
               AMEND-1 §1 (b): an INTERFERENCE-FREE two-room toy on which all nine arms pick the learnable room.
  Life         (integration, the redrawn pools of seed 20261301) the loop reproduces S1c's RANDOM band life, ERROR, PROGRESS and NULL records
               field for field — the estimators' equivalence with S1c's pickers is read from these.
  Report       the permutation null, the sign counts, the held-out reading, the replicate-SD flag, the unclipped share, the main effects.
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

from brain.scene import learners as Lr
from brain.scene import pickers as PK
from brain.scene import rooms as RM
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from brain.world.seeds import substream

from tools.toys.common import pools as POOLS
from tools.toys.cp import estimators as ES
from tools.toys.cp import life as LF
from tools.toys.cp import losses as LS
from tools.toys.cp import report as RP

SEED = 20261301
POOL_OK = all(POOLS.present(POOLS.ROOT, SEED).values())
S1C_OK = (S.ROOT / str(SEED) / "runs" / "law" / "PROGRESS.json").exists()
VOCAB = RM.VOCAB13
ROOMS = list(S.WORLDS["law"])

_CACHE = {}


def real_data():
    if "data" not in _CACHE:
        _CACHE["data"] = S.RoomData(POOLS.ROOT, SEED, ROOMS)
        _CACHE["test"] = S.FixedTestSet()
    return _CACHE["data"], _CACHE["test"]


def trained_learner(n_scenes=60):
    data, _ = real_data()
    L = S.new_learner()
    for room in ROOMS:
        for i in range(n_scenes // len(ROOMS)):
            X, words = data.visit_scene(room, i)
            L.train_scene(X, words, referent=None, rng=substream(SEED, f"episodic:room:{room}:visit:{i}"))
    return L


# ====================================================================================================== LOSSES
@unittest.skipUnless(POOL_OK, "the redrawn pools of seed 20261301 are absent")
class TestLosses(unittest.TestCase):
    def test_types_cover_the_vocabulary_once(self):
        flat = sorted(w for ws in LS.TYPE_WORDS.values() for w in ws)
        self.assertEqual(flat, sorted(VOCAB))
        self.assertEqual({t: len(v) for t, v in LS.TYPE_WORDS.items()}, {"shape": 6, "colour": 5, "size": 2})

    def test_L_equals_window_loss(self):
        data, _ = real_data()
        L = trained_learner()
        for r in ROOMS:
            self.assertEqual(LS.window_L(L, data.window[r]), PK.window_loss(L, data.window[r]))

    def slow_C(self, L, ws):
        p = PK.hyp_probs(L, ws.X, ws.vocab)
        vals = []
        for i in range(ws.n):
            a, b = int(ws.starts[i]), int(ws.starts[i + 1])
            P = np.clip(1.0 - np.prod(1.0 - p[a:b], axis=0) if b > a else np.zeros(len(VOCAB)), 1e-6, 1 - 1e-6)
            for t, words in LS.TYPE_WORDS.items():
                idx = [VOCAB.index(w) for w in words]
                said = [w for w in ws.words[i] if w in words]
                for w in said:
                    q = P[VOCAB.index(w)] / sum(P[j] for j in idx)
                    vals.append(-math.log(q))
        return sum(vals) / len(vals), len(vals)

    def test_C_matches_a_slow_recomputation_on_a_trained_learner(self):
        data, _ = real_data()
        L = trained_learner()
        for r in ROOMS:
            slow, n = self.slow_C(L, data.window[r])
            self.assertGreater(n, 40)
            self.assertAlmostEqual(LS.window_C(L, data.window[r]), slow, places=9)

    def test_C_on_an_untrained_learner_is_log_T_per_pair(self):
        data, _ = real_data()
        L = S.new_learner()                                   # no word heard: every p = sigma(0)
        for r in ROOMS:
            ws = data.window[r]
            counts = {t: sum(1 for i in range(ws.n) for w in ws.words[i] if w in words) for t, words in LS.TYPE_WORDS.items()}
            want = sum(counts[t] * math.log(len(LS.TYPE_WORDS[t])) for t in counts) / sum(counts.values())
            self.assertAlmostEqual(LS.window_C(L, ws), want, places=9)

    def test_an_empty_scene_contributes_the_uniform(self):
        L = S.new_learner()
        ws = PK.WindowSet([np.zeros((0, Lr.RW_DIM))], [["big", "circle"]], VOCAB)
        want = (math.log(2) + math.log(6)) / 2                # a size word and a shape word: log|T| each
        self.assertAlmostEqual(LS.window_C(L, ws), want, places=9)

    def test_the_two_losses_differ_on_a_trained_learner(self):
        data, _ = real_data()
        L = trained_learner()
        self.assertNotAlmostEqual(LS.window_L(L, data.window["R1"]), LS.window_C(L, data.window["R1"]), places=3)

    def test_snapshot_reads_the_learners_own_loss(self):
        data, _ = real_data()
        L = trained_learner()
        snap = LS.Snap.of(L)
        for r in ROOMS:
            self.assertAlmostEqual(PK.window_loss(snap, data.window[r]), PK.window_loss(L, data.window[r]), places=12)

    def test_mix_takes_only_the_named_components(self):
        data, _ = real_data()
        L = trained_learner()
        before = LS.Snap.of(L)
        X, words = data.visit_scene("R1", 100)
        for i in range(100, 110):
            X, words = data.visit_scene("R1", i)
            L.train_scene(X, words, referent=None, rng=substream(SEED, f"episodic:room:R1:visit:{i}"))
        after = LS.Snap.of(L)
        ws = data.window["R1"]
        same = LS.Snap.mix(before, after)                     # nothing taken from `after`
        self.assertEqual(PK.window_loss(same, ws), PK.window_loss(before, ws))
        everything = LS.Snap.mix(before, after, bias=True, weights=True, stats=True)
        self.assertEqual(PK.window_loss(everything, ws), PK.window_loss(after, ws))
        b = LS.Snap.mix(before, after, bias=True)
        self.assertTrue(np.array_equal(b.V, before.V) and np.array_equal(b.b, after.b))
        w = LS.Snap.mix(before, after, weights=True)
        self.assertTrue(np.array_equal(w.V, after.V) and np.array_equal(w.b, before.b))
        s = LS.Snap.mix(before, after, stats=True)
        self.assertEqual(s.stats.n, after.stats.n)
        self.assertNotEqual(PK.window_loss(b, ws), PK.window_loss(before, ws))          # the plant changed the bytes

    def test_prequential_loss_equals_scene_losses_on_one_scene(self):
        data, _ = real_data()
        L = trained_learner()
        X, words = data.visit_scene("R2", 7)
        ws = PK.WindowSet([X], [words], VOCAB)
        self.assertAlmostEqual(LS.scene_loss_pre(L, X, words), float(PK.scene_losses(L, ws)[0]), places=12)


# ====================================================================================================== ESTIMATORS
def info(block, room, Lb, La, Cb=None, Ca=None, n_after=None, preq=None):
    return ES.Info(block=block, room=room, L_before=Lb, L_after=La, C_before=Cb if Cb is not None else Lb,
                   C_after=Ca if Ca is not None else La, n_after=n_after, drop=Lb[room] - La[room], drift=0.0,
                   preq=list(preq) if preq is not None else [])


# THE HAND TABLE (rooms A, B, C; blocks 1-3 the round-robin, then A, B). L after each block, L(0) = 10 everywhere:
#   after b1 (A): A 6   B 11   C 10        after b2 (B): A 7   B 8   C 10.5      after b3 (C): A 7.5  B 8.5  C 7
#   after b4 (A): A 4   B 9    C 7.5       after b5 (B): A 4.5 B 5   C 8
# own rewards (the visited room's drop; the «before» of block b is the table AFTER block b-1): b1 A 10-6 = 4 · b2 B 11-8 = 3 · b3 C 10.5-7 = 3.5 · b4 A 7.5-4 = 3.5
#   · b5 B 9-5 = 4   (B stood at 9 after block 4: the interference of A's block raised it from 8.5 — the first draft of this table read 3.5 here, a slip of the
#   author's arithmetic found by the first run and re-derived by hand, independently of the code)
# history weights n_j(b) = 10 x visits through b:  b1 {A10}  b2 {A10 B10}  b3 {A10 B10 C10}  b4 {A20 B10 C10}  b5 {A20 B20 C10}
# hist rewards: b1 (10x4)/10 = 4 · b2 (10x(6-7) + 10x(11-8))/20 = 1 · b3 (-0.5 -0.5 +3.5)/3 = 5/6 · b4 (20x3.5 + 10x(8.5-9) + 10x(7-7.5))/40 = 1.5
#               · b5 (20x(4-4.5) + 20x(9-5) + 10x(7.5-8))/50 = 1.3
# last2 after b5: A own (4+3.5)/2 = 3.75, hist (4+1.5)/2 = 2.75 · B own (3+4)/2 = 3.5, hist (1+1.3)/2 = 1.15 · C own 3.5, hist 5/6
# ema (a = 0.1) after b5: A own 0.9x4 + 0.1x3.5 = 3.95, hist 0.9x4 + 0.1x1.5 = 3.75 · B own 0.9x3 + 0.1x4 = 3.1, hist 0.9x1 + 0.1x1.3 = 1.03
#                         · C own 3.5, hist 5/6
HAND_L = [{"A": 10, "B": 10, "C": 10}, {"A": 6, "B": 11, "C": 10}, {"A": 7, "B": 8, "C": 10.5}, {"A": 7.5, "B": 8.5, "C": 7},
          {"A": 4, "B": 9, "C": 7.5}, {"A": 4.5, "B": 5, "C": 8}]
HAND_ROOMS = ["A", "B", "C", "A", "B"]


def feed(picker, tab=HAND_L, rooms=HAND_ROOMS, tabC=None):
    n = {"A": 0, "B": 0, "C": 0}
    for b, room in enumerate(rooms, start=1):
        n[room] += 10
        picker.observe_block(info(b, room, tab[b - 1], tab[b], None if tabC is None else tabC[b - 1], None if tabC is None else tabC[b], dict(n)))


class TestEstimators(unittest.TestCase):
    def test_hand_table_last2_and_ema(self):
        want = {("L", "own", "last2"): {"A": 3.75, "B": 3.5, "C": 3.5},
                ("L", "hist", "last2"): {"A": 2.75, "B": 1.15, "C": 5 / 6},
                ("L", "own", "ema"): {"A": 3.95, "B": 3.1, "C": 3.5},
                ("L", "hist", "ema"): {"A": 3.75, "B": 1.03, "C": 5 / 6}}
        for (loss, scope, scale), est in want.items():
            p = ES.CellPicker(["A", "B", "C"], 1, loss, scope, scale)
            feed(p)
            got = p.estimates()
            for r in "ABC":
                self.assertAlmostEqual(got[r], est[r], places=12, msg=f"{loss}-{scope}-{scale} room {r}")

    def test_C_cells_read_the_C_table_not_the_L_table(self):
        tabC = [{r: 2 * v for r, v in row.items()} for row in HAND_L]           # C = 2 L: every reward doubles
        pL = ES.CellPicker(["A", "B", "C"], 1, "L", "own", "last2")
        pC = ES.CellPicker(["A", "B", "C"], 1, "C", "own", "last2")
        feed(pL, tabC=tabC)
        feed(pC, tabC=tabC)
        for r in "ABC":
            self.assertAlmostEqual(pC.estimates()[r], 2 * pL.estimates()[r], places=12)

    def test_cell_names(self):
        self.assertEqual(ES.CellPicker(["A", "B"], 1, "C", "hist", "ema").name, "C-hist-ema")
        self.assertEqual(ES.CELLS, ("L-own-last2", "L-own-ema", "L-hist-last2", "L-hist-ema", "C-own-last2", "C-own-ema", "C-hist-last2", "C-hist-ema"))

    def test_one_visited_room_hist_equals_own(self):
        n = {"A": 10, "B": 0, "C": 0}
        i = info(1, "A", {"A": 10, "B": 99, "C": 99}, {"A": 6, "B": 11, "C": 10}, n_after=n)
        self.assertAlmostEqual(ES.hist_reward(i.L_before, i.L_after, n), ES.own_reward(i.L_before, i.L_after, "A"), places=12)

    def test_ema_first_value_initialises(self):
        p = ES.CellPicker(["A", "B"], 1, "L", "own", "ema", a=0.1)
        p.observe_block(info(1, "A", {"A": 10, "B": 10}, {"A": 7, "B": 10}, n_after={"A": 10, "B": 0}))
        self.assertAlmostEqual(p.estimates()["A"], 3.0, places=12)
        p.observe_block(info(2, "A", {"A": 7, "B": 10}, {"A": 6, "B": 10}, n_after={"A": 20, "B": 0}))
        self.assertAlmostEqual(p.estimates()["A"], 0.9 * 3.0 + 0.1 * 1.0, places=12)

    def test_hist_with_planted_weights_is_caught(self):
        n = {"A": 20, "B": 20, "C": 10}
        b, a = HAND_L[4], HAND_L[5]
        good = ES.hist_reward(b, a, n)
        self.assertAlmostEqual(good, 1.3, places=12)                              # the hand value (1.3), pinned
        swapped = ES.hist_reward(b, a, {"A": 20, "B": 10, "C": 20})               # PLANT: B's and C's weights exchanged (A and C drop alike, so A/C would not move it)
        self.assertAlmostEqual(swapped, 0.4, places=12)                            # (20x-0.5 + 10x4 + 20x-0.5)/50 by hand
        self.assertNotAlmostEqual(swapped, good, places=6)                         # the plant changed the bytes, so the pin above would CATCH it
        equal = ES.hist_reward(b, a, {"A": 1, "B": 1, "C": 1})                    # PLANT: equal weights (the variant the law does NOT run)
        self.assertNotAlmostEqual(equal, good, places=6)
        with self.assertRaises(ES.EstimatorError):
            ES.hist_reward(b, a, {"A": 0, "B": 0, "C": 0})                       # every weight zero: refuses, never returns a silent 0

    def test_planted_room_swap_flips_the_pick(self):
        p = ES.CellPicker(["A", "B"], 1, "L", "own", "last2")
        q = ES.CellPicker(["A", "B"], 1, "L", "own", "last2")
        # A learns (drop 4), B does not (drop 0): the picker must prefer A; with the credit SWAPPED it must prefer B
        for pk, swap in ((p, False), (q, True)):
            for room in ("A", "B"):
                drop = 4.0 if room == "A" else 0.0
                credited = ({"A": "B", "B": "A"}[room]) if swap else room
                pk.rewards[credited].append(drop)
        ctx = PK.Context(last_visit={"A": 1, "B": 2}, L_now={"A": 0.0, "B": 0.0})
        # force the policy branch: choose a block whose epsilon coin is tails
        blk = next(b for b in range(10, 400) if ES.explore_draw_rep(1, b, ["A", "B"], 0) is None)
        self.assertEqual(p.pick(blk, ctx), ("A", "policy"))
        self.assertEqual(q.pick(blk, ctx), ("B", "policy"))

    def test_the_tie_rule_prefers_the_least_recently_visited(self):
        p = ES.CellPicker(["A", "B"], 1, "L", "own", "last2")
        p.rewards["A"].append(1.0)
        p.rewards["B"].append(1.0)
        ctx = PK.Context(last_visit={"A": 7, "B": 3}, L_now={"A": 0.0, "B": 0.0})
        blk = next(b for b in range(10, 400) if ES.explore_draw_rep(1, b, ["A", "B"], 0) is None)
        self.assertEqual(p.pick(blk, ctx)[0], "B")

    def test_epsilon_stream_replicate_zero_is_s1c_and_others_differ(self):
        rooms = ["R1", "R2", "R3", "N"]
        for b in range(1, 200):
            self.assertEqual(ES.explore_draw_rep(20261301, b, rooms, 0), PK.explore_draw(20261301, b, rooms))
        a = [ES.explore_draw_rep(20261301, b, rooms, 1) for b in range(1, 200)]
        c = [ES.explore_draw_rep(20261301, b, rooms, 2) for b in range(1, 200)]
        self.assertNotEqual(a, c)
        self.assertEqual(a, [ES.explore_draw_rep(20261301, b, rooms, 1) for b in range(1, 200)])
        share = np.mean([x is not None for x in a])
        self.assertTrue(0.04 < share < 0.20, share)

    # -- LP-OUDEYER ------------------------------------------------------------------------------
    def test_lp_hand_list(self):
        p = ES.LPPicker(["A", "B"], 1)
        feed_lp = lambda room, vals, b: p.observe_block(info(b, room, {"A": 0, "B": 0}, {"A": 0, "B": 0}, n_after={"A": 10, "B": 10}, preq=vals))
        feed_lp("A", [10.0] * 10, 1)
        feed_lp("A", [10.0] * 10, 2)
        feed_lp("A", [7.0] * 10, 3)
        self.assertIsNone(p.estimates()["A"])                       # 30 scenes: undefined (needs 2 x 20 = 40)
        feed_lp("A", [7.0] * 10, 4)
        self.assertAlmostEqual(p.estimates()["A"], 3.0, places=12)  # (10 - 7)
        feed_lp("A", [7.0] * 10, 5)
        self.assertAlmostEqual(p.estimates()["A"], 1.5, places=12)  # older window scenes 11-30: (10x10 + 7x10)/20 = 8.5; recent 7
        self.assertIsNone(p.estimates()["B"])

    def test_lp_undefined_rooms_are_picked_first_least_recently_visited(self):
        p = ES.LPPicker(["A", "B", "C"], 1)
        ctx = PK.Context(last_visit={"A": 3, "B": 1, "C": 2}, L_now={"A": 0.0, "B": 0.0, "C": 0.0})
        blk = next(b for b in range(10, 400) if ES.explore_draw_rep(1, b, ["A", "B", "C"], 0) is None)
        self.assertEqual(p.pick(blk, ctx), ("B", "policy"))

    # -- the NULL ----------------------------------------------------------------------------------
    def test_null_credit_is_a_derangement_and_never_lands_on_its_producer(self):
        rooms = ["R1", "R2", "R3", "N"]
        pi = PK.null_derangement(20261301, rooms)
        p = ES.CellPicker(rooms, 20261301, "L", "own", "last2", credit=pi)
        n = {r: 10 for r in rooms}
        got = p.observe_block(info(5, "R1", {r: 5.0 for r in rooms}, {r: 4.0 for r in rooms}, n_after=n))
        self.assertEqual(got, pi["R1"])
        self.assertNotEqual(got, "R1")
        with self.assertRaises(ES.EstimatorError):
            ES.CellPicker(rooms, 1, "L", "own", "last2", credit={"R1": "R1", "R2": "R3", "R3": "R2", "N": "R1"})   # a planted fixed point RAISES

    def test_identity_credit_reproduces_the_arm_exactly(self):
        rooms = ["A", "B", "C"]
        a = ES.CellPicker(rooms, 1, "L", "hist", "ema")
        b = ES.CellPicker(rooms, 1, "L", "hist", "ema", credit={r: r for r in rooms}, allow_identity=True)
        feed(a)
        feed(b)
        self.assertEqual(a.estimates(), b.estimates())
        lp1, lp2 = ES.LPPicker(rooms, 1), ES.LPPicker(rooms, 1, credit={r: r for r in rooms}, allow_identity=True)
        for pk in (lp1, lp2):
            for b_i, room in enumerate(["A", "A", "A", "A"], start=1):
                pk.observe_block(info(b_i, room, {r: 0 for r in rooms}, {r: 0 for r in rooms}, n_after={r: 10 for r in rooms}, preq=[float(b_i)] * 10))
        self.assertEqual(lp1.estimates(), lp2.estimates())

    def test_lp_null_deals_the_error_stream_across_rooms(self):
        rooms = ["A", "B"]
        pi = {"A": "B", "B": "A"}
        p = ES.LPPicker(rooms, 1, credit=pi)
        for b, vals in enumerate(([10.0] * 10, [10.0] * 10, [7.0] * 10, [7.0] * 10), start=1):
            p.observe_block(info(b, "A", {"A": 0, "B": 0}, {"A": 0, "B": 0}, n_after={"A": 10, "B": 10}, preq=vals))
        self.assertIsNone(p.estimates()["A"])
        self.assertAlmostEqual(p.estimates()["B"], 3.0, places=12)          # room A's stream landed on B

    # -- the controls ------------------------------------------------------------------------------
    def test_r_only_never_picks_N_and_is_deterministic(self):
        rooms = ["R1", "R2", "R3", "N"]
        a = ES.ROnlyPicker(rooms, 20261301, 3)
        b = ES.ROnlyPicker(rooms, 20261301, 3)
        ctx = PK.Context(last_visit={}, L_now={})
        picks = [a.pick(blk, ctx) for blk in range(5, 201)]
        self.assertEqual(picks, [b.pick(blk, ctx) for blk in range(5, 201)])
        self.assertNotIn("N", [r for r, _f in picks])
        self.assertEqual({r for r, _f in picks}, {"R1", "R2", "R3"})
        self.assertTrue(all(f == "policy" for _r, f in picks))

    def test_n_only_always_picks_N(self):
        p = ES.NOnlyPicker(["R1", "R2", "R3", "N"], 1)
        ctx = PK.Context(last_visit={}, L_now={})
        self.assertEqual({p.pick(b, ctx) for b in range(5, 50)}, {("N", "policy")})

    # -- AMEND-1 §1 (b): the interference-free two-room toy ------------------------------------------
    def run_toy(self, arm, n_blocks=60, seed=11):
        rooms = ["A", "B"]
        picker = ES.make_arm(arm, rooms, seed, 0)
        rng = np.random.default_rng(seed)
        exc = 100.0
        noise = 0.01
        n = {r: 0 for r in rooms}
        last = {r: 0 for r in rooms}
        L_now = {"A": 3.0 + exc, "B": 5.0}
        C_now = {"A": 1.0 + 0.5 * exc, "B": 1.5}
        picks = []
        for block in range(1, n_blocks + 1):
            defined = all(v is not None for v in picker.estimates().values())      # AMEND-1 §1 (b): a pick counts only if no estimate was undefined
            if block <= 2:
                room, flag = rooms[block - 1], "round-robin"
            else:
                room, flag = picker.pick(block, PK.Context(last_visit=dict(last), L_now=dict(L_now)))
            Lb, Cb = dict(L_now), dict(C_now)
            preq = []
            for _s in range(10):
                if room == "A":
                    preq.append(3.0 + exc + rng.normal(0, 0.05))
                    exc *= 0.99
                else:
                    preq.append(5.0 + rng.normal(0, 0.05))
            L_now = {"A": 3.0 + exc, "B": 5.0 + rng.normal(0, noise)}
            C_now = {"A": 1.0 + 0.5 * exc, "B": 1.5 + rng.normal(0, noise)}
            n[room] += 10
            picker.observe_block(info(block, room, Lb, L_now, Cb, C_now, dict(n), preq))
            last[room] = block
            if block > 2:
                picks.append((room, flag, defined))
        return picks

    def counted(self, picks):
        """The picks that count: policy (not ε-exploration) and made while every room's estimate was defined."""
        return [r for r, f, d in picks if f == "policy" and d]

    def test_interference_free_toy_all_nine_arms_pick_the_learnable_room(self):
        for arm in list(ES.CELLS) + ["LP-OUDEYER"]:
            policy = self.counted(self.run_toy(arm))
            self.assertGreater(len(policy), 35, f"{arm}: only {len(policy)} counted picks")
            share = sum(1 for r in policy if r == "A") / len(policy)
            print(f"   toy {arm:12s} A-share {share:.3f} of {len(policy)} counted picks")
            self.assertGreaterEqual(share, 0.95, f"{arm}: picked the learnable room {share:.3f} of {len(policy)} counted picks")

    def test_every_cell_has_every_estimate_defined_from_block_3(self):
        for arm in ES.CELLS:
            picks = self.run_toy(arm)
            self.assertTrue(all(d for _r, _f, d in picks), arm)                     # the eight cells: nothing is ever undefined at a pick
        lp = self.run_toy("LP-OUDEYER")
        first_defined = next(i for i, (_r, _f, d) in enumerate(lp, start=3) if d)
        explores = [ES.explore_draw_rep(11, b, ["A", "B"], 0) for b in range(3, 9)]
        if all(e is None for e in explores):
            self.assertEqual(first_defined, 9)                                      # LP: blocks 3-8 are optimism picks (AMEND-1 §1 (b))
        else:
            self.assertGreater(first_defined, 4)                                    # an ε pick in 3-8 shifts the visits; the exact 9 holds only without one

    def test_the_toy_can_fail_a_planted_blind_arm(self):
        picks = self.run_toy("RANDOM-PLANT")                       # an arm that ignores its estimates and picks uniformly: it has none, so every policy pick counts
        policy = [r for r, f, _d in picks if f == "policy"]
        self.assertGreater(len(policy), 35)
        self.assertLess(sum(1 for r in policy if r == "A") / len(policy), 0.95)


# ====================================================================================================== LIFE (integration)
@unittest.skipUnless(POOL_OK and S1C_OK, "the redrawn pools or S1c's records are absent")
class TestLifeIdentity(unittest.TestCase):
    def old(self, name):
        return json.loads((S.ROOT / str(SEED) / "runs" / "law" / f"{name}.json").read_text())

    def test_random_band_life_equals_s1c(self):
        data, test = real_data()
        new = LF.life_cp(data, test, ES.S1cAdapter(PK.RandomPicker(ROOMS, SEED, prefix=PK.band_prefix(SEED, 1))), "RANDOM", ROOMS,
                         prefix=PK.band_prefix(SEED, 1))
        old = json.loads((S.ROOT / str(SEED) / "band" / "law" / "random-01.json").read_text())
        self.assertEqual(S2.identity_diff(new, old), [])

    def test_error_life_equals_s1c(self):
        data, test = real_data()
        new = LF.life_cp(data, test, ES.S1cAdapter(PK.ErrorPicker(ROOMS, SEED)), "ERROR", ROOMS)
        self.assertEqual(S2.identity_diff(new, self.old("ERROR")), [])

    def test_L_own_last2_equals_s1c_progress(self):
        data, test = real_data()
        picker = ES.CellPicker(ROOMS, SEED, "L", "own", "last2")
        new = LF.life_cp(data, test, picker, "PROGRESS", ROOMS)
        self.assertEqual(S2.identity_diff(new, self.old("PROGRESS")), [])

    def test_null_of_L_own_last2_equals_s1c_null(self):
        data, test = real_data()
        pi = PK.null_derangement(SEED, ROOMS)
        picker = ES.CellPicker(ROOMS, SEED, "L", "own", "last2", credit=pi)
        new = LF.life_cp(data, test, picker, "NULL", ROOMS)
        self.assertEqual(S2.identity_diff(new, self.old("NULL")), [])

    def test_the_extras_are_present_and_do_not_move_the_record(self):
        data, test = real_data()
        new = LF.life_cp(data, test, ES.CellPicker(ROOMS, SEED, "C", "hist", "ema"), "C-hist-ema", ROOMS, n_blocks=30)
        ex = new["extra"]
        self.assertEqual(len(ex["C"]), 31)
        self.assertEqual(len(ex["hist_w_N"]), 30)
        self.assertEqual(len(ex["ear_ok"]), 30)
        self.assertEqual(len(ex["rates_curve"]), 30)
        self.assertTrue(all(0.0 <= w <= 1.0 for w in ex["hist_w_N"]))
        self.assertEqual(ex["arm"], "C-hist-ema")

    def test_the_drops_anatomy_adds_up_and_leaves_the_life_alone(self):
        data, test = real_data()
        base = LF.life_cp(data, test, ES.S1cAdapter(PK.RandomPicker(ROOMS, SEED, prefix=PK.band_prefix(SEED, 2))), "RANDOM", ROOMS,
                          prefix=PK.band_prefix(SEED, 2), n_blocks=40)
        dec = LF.life_cp(data, test, ES.S1cAdapter(PK.RandomPicker(ROOMS, SEED, prefix=PK.band_prefix(SEED, 2))), "RANDOM", ROOMS,
                         prefix=PK.band_prefix(SEED, 2), n_blocks=40, decompose=True)
        self.assertEqual(S2._canon(base["record"]), S2._canon(dec["record"]))              # the anatomy never touches the life
        rows = dec["extra"]["decomp"]
        self.assertEqual(len(rows), 40)
        for r in rows:
            for scope in ("own", "hist"):
                self.assertEqual(set(r[scope]), {"total", "bias", "weight", "stats"})
            # the own total is the recorded drop
        for r, rec in zip(rows, dec["record"]):
            self.assertAlmostEqual(r["own"]["total"], rec["drop"], places=12)


# ====================================================================================================== REPORT (statistics on synthetic data)
class TestReport(unittest.TestCase):
    def synth(self, shift=0.0, sd=0.025, seeds=10, n=20, seed=3):
        rng = np.random.default_rng(seed)
        return {s: rng.normal(0.55 + shift, sd, n) for s in range(seeds)}

    def test_null_distribution_is_centred_and_has_the_right_spread(self):
        rand = self.synth()
        d = RP.null_distribution(rand, draws=4000, fake=10, seed=1)
        self.assertEqual(len(d), 4000)
        self.assertLess(abs(float(np.mean(d))), 0.002)
        want = 0.025 * math.sqrt(0.2) / math.sqrt(10)               # per-seed sd of a 10-vs-10 mean difference, over 10 seeds
        self.assertAlmostEqual(float(np.std(d)), want, delta=0.0006)

    def test_p_value_is_small_for_a_shifted_arm_and_not_for_an_exchangeable_one(self):
        rand = self.synth(seed=3)
        d = RP.null_distribution(rand, draws=4000, fake=10, seed=1)
        shifted = self.synth(shift=0.03, n=10, seed=4)
        same = self.synth(shift=0.0, n=10, seed=5)
        self.assertLess(RP.p_upper(RP.arm_D(shifted, rand), d), 0.005)
        self.assertGreater(RP.p_upper(RP.arm_D(same, rand), d), 0.05)

    def test_smallest_passing_D_is_the_quantile_of_the_null(self):
        d = np.linspace(-1, 1, 10001)
        self.assertAlmostEqual(RP.smallest_passing(d, 0.0056), float(np.quantile(d, 1 - 0.0056)), places=9)

    def test_sign_counts_and_the_exact_sign_p(self):
        self.assertEqual(RP.sign_count([0.1, 0.2, -0.1, 0.3, 0.1, 0.2, 0.1, 0.1, 0.2, 0.3], +1), 9)
        self.assertAlmostEqual(RP.sign_p(8, 10), 56 / 1024, places=12)
        self.assertAlmostEqual(RP.sign_p(9, 10), 11 / 1024, places=12)
        self.assertAlmostEqual(RP.sign_p(6, 7), 8 / 128, places=12)

    def test_held_out_restricts_to_seeds_04_to_10(self):
        seeds = list(range(20261301, 20261311))
        self.assertEqual(RP.held_out_seeds(seeds), list(range(20261304, 20261311)))

    def test_replicate_sd_flag(self):
        rand_sd = {s: 0.02 for s in range(10)}
        wide = {s: 0.05 for s in range(10)}
        narrow = {s: 0.015 for s in range(10)}
        self.assertTrue(RP.sd_flag(wide, rand_sd))
        self.assertFalse(RP.sd_flag(narrow, rand_sd))

    def test_escaped_noise_share_is_not_clipped(self):
        self.assertAlmostEqual(RP.escaped_share(0.70, 0.55, 0.60), 3.0, places=12)       # beats R-ONLY: share 3
        self.assertAlmostEqual(RP.escaped_share(0.50, 0.55, 0.60), -1.0, places=12)      # worse than RANDOM: negative

    def test_main_effects_recover_a_planted_factor(self):
        # a synthetic 2x2x2 table where only `scope` matters (+0.1 for hist), per seed
        seeds = list(range(5))
        cells = {}
        for loss in "LC":
            for scope in ("own", "hist"):
                for scale in ("last2", "ema"):
                    cells[f"{loss}-{scope}-{scale}"] = {s: 0.5 + (0.1 if scope == "hist" else 0.0) for s in seeds}
        eff = RP.main_effects(cells, seeds)
        self.assertAlmostEqual(eff["scope"]["mean"], 0.1, places=12)
        self.assertAlmostEqual(eff["loss"]["mean"], 0.0, places=12)
        self.assertAlmostEqual(eff["time"]["mean"], 0.0, places=12)
        self.assertEqual(eff["scope"]["signs"], 5)


if __name__ == "__main__":
    unittest.main()
