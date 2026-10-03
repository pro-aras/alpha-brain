# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:40 +0400 — docs/organism/act/PREREG-ACT-EFFECT.md PHASE 1 (signed at 1d55eab, co-signature line c465a7b): the RED tests of the effect bench's pure half
# (tools/toys/act_chooser_toy.py, NEW classes only) and of its venv harness. Every instrument here carries a planted control that must be CAUGHT, and each plant asserts it changed the bytes (#247 (5)).
#   M9   the episode-boundary rule (a terminal-then-reset row pair reads UNKNOWN; without the rule the same two frames read «changed»)
#   M6   an ablated chooser (every effect constant) draws uniformly over the 7 acts
#   M5   the plants: P-DEAL (the live flags dealt to the wrong acts) and K-ARGMAX (argmax on change alternates between the tied turns and never moves)
#   M2   the two-act lock detector (a left/right spin holds neither act above ~0.7 and is caught only by the top-2 share)
#   M7   the new run path reproduces the landed harness' totals exactly; the boundary count in the harness; M8's obs ⟺ render equivalence (smoke)
from __future__ import annotations

import json
import math
import os
import subprocess
import unittest
from pathlib import Path
from typing import List, Optional

import numpy as np

from tools.toys import act_chooser_toy as toy

ROOT = Path(__file__).resolve().parents[2]
VENV = Path("/data/dev/game-worlds/venv/bin/python3")


class _CountingRng:
    """Wraps a Generator and counts the draws asked of it (the two-draw discipline)."""

    def __init__(self, rng):
        self._r = rng
        self.calls = 0

    def random(self, *a, **k):
        self.calls += 1
        return self._r.random(*a, **k)

    def integers(self, *a, **k):
        self.calls += 1
        return self._r.integers(*a, **k)


def _eye(seq: int, episode: int, step: int, sha: str) -> dict:
    return {"seq": seq, "sense": "eye", "sha": sha, "meta": {"source": "game", "episode": episode, "step": step}}


def _out(seq: int, episode: int, step: int, act: str, terminated: bool = False) -> dict:
    return {"seq": seq, "sense": "outcome", "meta": {"source": "game", "episode": episode, "step": step, "act": act,
                                                      "terminated": terminated, "truncated": False, "got": 0.0}}


def _fill(tracker: "toy.EffectTracker", act_idx: int, effects: List[Optional[int]]) -> None:
    for e in effects:
        tracker.record(toy.ACT_NAMES[act_idx], e)


def _true_set_tracker(tr: "toy.EffectTracker", forward_changes: int = 13) -> None:
    """left, right change every time; forward `forward_changes` of 20; the four no-ops 0 of 20 (all judged on a FULL window)."""
    _fill(tr, 0, [1] * 20)
    _fill(tr, 1, [1] * 20)
    _fill(tr, 2, [1] * forward_changes + [0] * (20 - forward_changes))
    for a in toy.NOOP_ACTS:
        _fill(tr, a, [0] * 20)


class TestBoundaryRuleM9(unittest.TestCase):
    """The silent reset: the act chosen on a terminal frame lands on a NEW episode's frame, which differs whatever the act."""

    def _tape(self) -> List[dict]:
        return [
            _eye(1, 0, 0, "A"),                          # the reset frame of episode 0 (visible)
            _eye(2, 0, 1, "B"), _out(3, 0, 1, "left"),   # changed
            _eye(4, 0, 2, "B"), _out(5, 0, 2, "done"),   # unchanged
            _eye(6, 0, 3, "C"), _out(7, 0, 3, "forward", terminated=True),   # changed; terminal
            _eye(8, 1, 4, "D"), _out(9, 1, 4, "done"),   # NEW episode: the pair (C, D) crosses the silent reset
            _eye(10, 1, 5, "D"), _out(11, 1, 5, "done"),  # same episode, unchanged
        ]

    def test_known_changes_and_no_change(self) -> None:
        got = toy.effect_pairs(self._tape())
        by_seq = {r["seq"]: r["effect"] for r in got}
        self.assertEqual(by_seq[3], 1)
        self.assertEqual(by_seq[5], 0)
        self.assertEqual(by_seq[7], 1)
        self.assertEqual(by_seq[11], 0)

    def test_the_boundary_outcome_is_unknown_and_the_plant_proves_the_rule(self) -> None:
        tape = self._tape()
        got = {r["seq"]: r["effect"] for r in toy.effect_pairs(tape)}
        self.assertIsNone(got[9], "the first outcome of a new episode must be UNKNOWN, never 0 and never 1")
        # THE PLANT asserts it changed the bytes: the terminal frame (seq 6) and the new episode's first frame (seq 8) compared WITHOUT the rule differ,
        # so the live tape's `done` would read «changed» — exactly the artefact (1 of 86) the rule removes
        terminal = next(r for r in tape if r["seq"] == 6)
        reset = next(r for r in tape if r["seq"] == 8)
        self.assertNotEqual(terminal["sha"], reset["sha"])
        self.assertEqual(int(terminal["sha"] != reset["sha"]), 1)

    def test_a_duplicate_eye_row_is_ignored(self) -> None:
        tape = [_eye(1, 0, 0, "A"), _eye(2, 0, 1, "B"), _eye(3, 0, 1, "B"), _out(4, 0, 1, "left")]   # the sense re-published step 1
        got = toy.effect_pairs(tape)
        self.assertEqual([r["effect"] for r in got], [1], "the pair is (A, B), never (B, B)")

    def test_no_previous_eye_row_is_unknown(self) -> None:
        got = toy.effect_pairs([_eye(1, 0, 0, "A"), _out(2, 0, 0, "left")])
        self.assertIsNone(got[0]["effect"])

    def test_an_outcome_not_aligned_to_the_last_eye_row_is_unknown(self) -> None:
        got = toy.effect_pairs([_eye(1, 0, 0, "A"), _eye(2, 0, 1, "B"), _out(3, 0, 7, "left")])
        self.assertIsNone(got[0]["effect"])

    def test_non_game_rows_are_never_read(self) -> None:
        tape = self._tape() + [{"seq": 99, "sense": "eye", "sha": "Z", "meta": {"source": "maker", "episode": 9, "step": 9}}]
        self.assertEqual(len(toy.effect_pairs(tape)), 5)


class TestEffectTracker(unittest.TestCase):
    def test_fewer_than_n_known_outcomes_reads_optimism_and_is_live(self) -> None:
        tr = toy.EffectTracker()
        _fill(tr, 6, [0] * 19)                            # `done`: nineteen unchanged outcomes — still unjudged
        self.assertTrue(tr.live("done"))
        self.assertEqual(tr.rate("done"), toy.EFFECT_OPTIMISM)
        _fill(tr, 6, [0])                                  # the twentieth
        self.assertFalse(tr.live("done"))

    def test_the_boundary_k_is_four_of_twenty(self) -> None:
        a, b = toy.EffectTracker(), toy.EffectTracker()
        _fill(a, 3, [1] * 3 + [0] * 17)
        _fill(b, 3, [1] * 4 + [0] * 16)
        self.assertFalse(a.live("pickup"))
        self.assertTrue(b.live("pickup"))

    def test_excluded_is_not_counted_as_zero(self) -> None:
        tr = toy.EffectTracker()
        _fill(tr, 0, [None] * 30 + [1] * 5)
        self.assertEqual(tr.counts()["left"], {"known": 5, "excluded": 30, "total": 35})
        self.assertTrue(tr.live("left"), "30 excluded outcomes must not have filled the window with zeros")

    def test_the_window_slides(self) -> None:
        tr = toy.EffectTracker()
        _fill(tr, 2, [1] * 20)
        self.assertTrue(tr.live("forward"))
        _fill(tr, 2, [0] * 17)                             # three changes left in the window
        self.assertFalse(tr.live("forward"))

    def test_live_flags_in_act_order(self) -> None:
        tr = toy.EffectTracker()
        _true_set_tracker(tr)
        self.assertEqual(tr.live_flags(), [True, True, True, False, False, False, False])


class TestScreenChooserM6(unittest.TestCase):
    def test_two_rng_draws_per_choice_in_either_branch(self) -> None:
        pol = toy.ScreenChooser(20260923)
        _true_set_tracker(pol.tracker)
        pol.rng = _CountingRng(pol.rng)
        for _ in range(2000):
            pol.act(toy.Ring(), toy.Ctx())
        self.assertEqual(pol.rng.calls, 4000)
        self.assertGreater(pol.explored, 100, "the 10 % uniform branch must have fired (both branches counted)")

    def test_uniform_over_the_live_set_plus_the_landed_floor(self) -> None:
        pol = toy.ScreenChooser(20260923)
        _true_set_tracker(pol.tracker)
        n = 60_000
        cnt = np.zeros(7)
        for _ in range(n):
            cnt[pol.act(toy.Ring(), toy.Ctx())] += 1
        p_live = 0.9 / 3 + 0.1 / 7
        p_dead = 0.1 / 7
        for a in range(7):
            p = p_live if a < 3 else p_dead
            se = math.sqrt(p * (1 - p) / n)
            self.assertLess(abs(cnt[a] / n - p), 5 * se, f"act {a}: {cnt[a] / n:.4f} vs {p:.4f}")

    def test_all_dead_falls_back_to_uniform(self) -> None:
        pol = toy.ScreenChooser(20260923)
        for a in range(7):
            _fill(pol.tracker, a, [0] * 20)
        self.assertEqual(pol.tracker.live_flags(), [False] * 7)
        n = 70_000
        cnt = np.zeros(7)
        for _ in range(n):
            cnt[pol.act(toy.Ring(), toy.Ctx())] += 1
        for a in range(7):
            self.assertLess(abs(cnt[a] / n - 1 / 7), 4 * math.sqrt((1 / 7) * (6 / 7) / n))

    def test_M6_every_effect_constant_is_uniform_over_the_seven_acts(self) -> None:
        """The ablated system: no signal = R-NULL by construction (all effects 1: everything live; all 0: everything dead -> the fallback)."""
        for const in (1, 0):
            pol = toy.ScreenChooser(20261003 + const)
            for a in range(7):
                _fill(pol.tracker, a, [const] * 20)
            n = 70_000
            cnt = np.zeros(7)
            for _ in range(n):
                cnt[pol.act(toy.Ring(), toy.Ctx())] += 1
            for a in range(7):
                self.assertLess(abs(cnt[a] / n - 1 / 7), 4 * math.sqrt((1 / 7) * (6 / 7) / n), f"constant effect {const}, act {a}")

    def test_the_live_history_records_the_flags_each_choice(self) -> None:
        pol = toy.ScreenChooser(1)
        _true_set_tracker(pol.tracker)
        pol.act(toy.Ring(), toy.Ctx())
        self.assertEqual(len(pol.live_history), 1)
        self.assertEqual(pol.live_history[0], [True, True, True, False, False, False, False])


class TestPlantsM5(unittest.TestCase):
    def test_the_dealt_plant_changed_the_bytes(self) -> None:
        true_flags = [True, True, True, False, False, False, False]
        dealt = toy.deal_flags(true_flags)
        self.assertGreaterEqual(sum(1 for a, b in zip(true_flags, dealt) if a != b), 4, "the plant must differ from the truth on >= 4 of 7 acts")
        self.assertEqual(sorted(dealt), sorted(true_flags), "dealt, not invented: the same multiset of flags")

    def test_the_dealt_plant_plays_the_no_ops(self) -> None:
        pol = toy.DealtScreen(20260923)
        _true_set_tracker(pol.tracker)
        n = 20_000
        noop = sum(1 for _ in range(n) if pol.act(toy.Ring(), toy.Ctx()) in toy.NOOP_ACTS)
        self.assertGreater(noop / n, 0.85)

    def test_effect_argmax_alternates_between_the_tied_turns_and_never_moves(self) -> None:
        pol = toy.EffectArgmax(20260923)
        _true_set_tracker(pol.tracker)
        n = 30_000
        cnt = np.zeros(7)
        for _ in range(n):
            cnt[pol.act(toy.Ring(), toy.Ctx())] += 1
        share = cnt / n
        self.assertLess(share.max(), 0.55, "no single act dominates: the tie is broken at random")
        self.assertGreater(share[0] + share[1], 0.90, "two turns hold the choice")
        self.assertLess(share[2], 0.03, "forward only by the floor")


class TestLockDetectorM2(unittest.TestCase):
    def _rng_acts(self, probs, n, seed=3):
        return list(np.random.default_rng(seed).choice(7, size=n, p=np.array(probs) / np.sum(probs)))

    def test_all_left_is_caught_by_both_detectors(self) -> None:
        acts = [0] * 1000
        t1, t2 = toy.window_shares(acts)
        self.assertEqual(float(t1.max()), 1.0)
        self.assertEqual(float(t2.max()), 1.0)
        self.assertFalse(toy.lock_pass(acts))

    def test_a_left_right_spin_holds_neither_act_above_the_single_act_bar_yet_is_caught(self) -> None:
        """THE PLANT of AMENDMENT 2: v2.1's single-act detector would have read this as NOT locked."""
        acts = self._rng_acts([0.4643, 0.4643, 0.0143, 0.0143, 0.0143, 0.0143, 0.0143], 4920)
        t1, t2 = toy.window_shares(acts)
        self.assertLess(float(t1.max()), 0.8, "the single-act detector (v2.1) is blind to a two-act spin")
        self.assertGreater(float(t2.mean()), 0.88)
        self.assertFalse(toy.lock_pass(acts))

    def test_a_three_act_mixture_passes(self) -> None:
        p = 0.9 / 3 + 0.1 / 7
        acts = self._rng_acts([p, p, p] + [0.1 / 7] * 4, 4920)
        self.assertTrue(toy.lock_pass(acts))

    def test_the_persistence_criterion_is_two_percent_of_windows(self) -> None:
        p = 0.9 / 3 + 0.1 / 7
        base = self._rng_acts([p, p, p] + [0.1 / 7] * 4, 4920, seed=5)
        spin = [0, 1] * 60                                  # a 120-act two-act episode: ~21 windows of ~4,800 (0.4 %)
        ok = base[:2000] + spin + base[2120:]
        self.assertTrue(toy.lock_pass(ok), "a short transient is not a lock")
        long_spin = base[:1000] + [0, 1] * 200 + base[1400:]   # a 400-act episode: ~300 windows (6 %)
        self.assertFalse(toy.lock_pass(long_spin), "a persistent spin is")

    def test_windows_start_after_act_120(self) -> None:
        acts = [0] * 120 + list(np.random.default_rng(1).integers(0, 7, size=1000))
        t1, t2 = toy.window_shares(acts)
        self.assertEqual(len(t1), len(acts) - 120 - 100 + 1)
        self.assertLess(float(t1.max()), 0.5)


class TestNoopShareAndM4(unittest.TestCase):
    def test_noop_share_reads_acts_241_to_960(self) -> None:
        acts = [3] * 240 + [0] * 720 + [3] * 100
        self.assertEqual(toy.noop_share(acts), 0.0)
        acts = [0] * 240 + [4] * 360 + [0] * 360
        self.assertEqual(toy.noop_share(acts), 0.5)

    def test_the_lock_passes_m3_alone(self) -> None:
        """The ablated system: the old law spinning `right` reads a no-op share of ~0.057 — M3 is graded only jointly with M1 and M2 (§5)."""
        rng = np.random.default_rng(2)
        acts = [1 if rng.random() < 0.9143 else int(rng.integers(0, 7)) for _ in range(960)]
        self.assertLess(toy.noop_share(acts), 0.25)
        self.assertFalse(toy.lock_pass(acts))

    def test_m4_readings_from_the_live_history(self) -> None:
        true_flags = [True, True, True, False, False, False, False]
        hist = [true_flags] * 960
        a, b = toy.m4_readings(hist)
        self.assertEqual((a, b), (1.0, 1.0))
        wrong = [[True, True, False, True, True, False, False]] * 960
        a, b = toy.m4_readings(wrong)
        self.assertEqual(b, 0.0)
        self.assertEqual(a, 0.5)


class TestFixedMixtures(unittest.TestCase):
    def test_r_scr_is_the_candidates_stationary_mixture(self) -> None:
        pr = toy.r_scr_probs()
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=9)
        for a in (0, 1, 2):
            self.assertAlmostEqual(pr[a], 0.9 / 3 + 0.1 / 7, places=9)
        for a in toy.NOOP_ACTS:
            self.assertAlmostEqual(pr[a], 0.1 / 7, places=9)

    def test_the_null2_stream_is_independent_of_the_null(self) -> None:
        a = toy.FixedDist(20260923, {i: 1.0 for i in range(7)})
        b = toy.FixedDistTagged(20260923, {i: 1.0 for i in range(7)}, toy.NULL2_TAG)
        sa = [a.act(toy.Ring()) for _ in range(200)]
        sb = [b.act(toy.Ring()) for _ in range(200)]
        self.assertNotEqual(sa, sb)


class TestRewardWindowArms(unittest.TestCase):
    def test_rate_sampler_weights_are_mean_reward_plus_epsilon(self) -> None:
        pol = toy.RateSampler(1)
        for got in (0.5, 0.0, 0.25):
            pol.observe("forward", got, None, False, False)
        pol.observe("left", 0.0, None, False, False)
        w = pol.weights()
        self.assertAlmostEqual(w[2], 0.25 + toy.RATE_EPS, places=9)
        self.assertAlmostEqual(w[0], 0.0 + toy.RATE_EPS, places=9)
        self.assertAlmostEqual(w[6], toy.RATE_EPS, places=9)

    def test_the_reward_window_is_the_last_two_thousand_outcomes(self) -> None:
        pol = toy.RateSampler(1)
        for _ in range(2000):
            pol.observe("forward", 1.0, None, False, False)
        for _ in range(2000):
            pol.observe("forward", 0.0, None, False, False)
        self.assertAlmostEqual(pol.weights()[2], toy.RATE_EPS, places=9, msg="the first 2,000 rewards left the window")

    def test_ucb_tries_every_act_first(self) -> None:
        pol = toy.UCBChooser(1)
        v = pol.values()
        self.assertTrue(all(math.isinf(x) for x in v))
        for name in toy.ACT_NAMES[:-1]:
            pol.observe(name, 0.0, None, False, False)
        v = pol.values()
        self.assertTrue(math.isinf(v[6]) and not any(math.isinf(x) for x in v[:6]))

    def test_both_gives_a_dead_act_zero_weight_whatever_its_reward(self) -> None:
        pol = toy.BothChooser(1)
        _true_set_tracker(pol.tracker)
        pol.observe("done", 1.0, 0, False, False)          # a rewarded outcome on a DEAD act
        w = pol.weights()
        self.assertEqual(w[6], 0.0)
        self.assertGreater(w[0], 0.0)


class TestReactiveReferences(unittest.TestCase):
    def _freq(self, pol, ctx, n=6000):
        cnt = np.zeros(7)
        for _ in range(n):
            cnt[pol.act(toy.Ring(), ctx)] += 1
        return cnt / n

    def test_walk_turns_after_a_blocked_forward_and_goes_on_after_a_moving_one(self) -> None:
        f = self._freq(toy.WALK(7), toy.Ctx(last_act=2, last_effect=0, last_novel=0))
        self.assertGreater(f[0] + f[1], 0.9)
        f = self._freq(toy.WALK(7), toy.Ctx(last_act=2, last_effect=1, last_novel=1))
        self.assertGreater(f[2], 0.9)
        f = self._freq(toy.WALK(7), toy.Ctx(last_act=0, last_effect=1, last_novel=1))
        self.assertGreater(f[2], 0.9, "after a turn: forward")
        f = self._freq(toy.WALK(7), toy.Ctx())
        self.assertGreater(f[2], 0.9, "episode start: forward")

    def test_wsls_stays_while_the_frame_is_novel(self) -> None:
        f = self._freq(toy.WSLS(7), toy.Ctx(last_act=0, last_effect=1, last_novel=1))
        self.assertGreater(f[0], 0.9)
        f = self._freq(toy.WSLS(7), toy.Ctx(last_act=0, last_effect=1, last_novel=0))
        self.assertLess(f[0], 0.45)
        self.assertGreater(f[0] + f[1] + f[2], 0.9, "else uniform over the TRUE live set")

    def test_two_rng_draws_per_choice(self) -> None:
        for cls in (toy.WALK, toy.WSLS):
            pol = cls(3)
            pol.rng = _CountingRng(pol.rng)
            for _ in range(500):
                pol.act(toy.Ring(), toy.Ctx(last_act=2, last_effect=0, last_novel=0))
            self.assertEqual(pol.rng.calls, 1000, cls.__name__)


@unittest.skipUnless(VENV.exists(), "the game-worlds venv (gymnasium + minigrid) is not installed on this machine")
class TestHarnessUnderTheVenv(unittest.TestCase):
    def _run(self, code: str) -> dict:
        env = dict(os.environ, PYTHONPATH=str(ROOT), OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        env.pop("BABYAI_DONE_ACTIONS", None)
        r = subprocess.run([str(VENV), "-B", "-c", code], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_M7_the_null_through_the_new_path_equals_the_landed_harness_exactly(self) -> None:
        out = self._run("""
import json
from tools.toys import act_chooser_toy as toy
rows = []
for s in (20260923, 21260923):
    mk = lambda: toy.FixedDist(s, {i: 1.0 for i in range(7)})
    a = toy.run_game(mk(), s, 60)
    b = toy.run_game_fx(mk(), s, 60)
    rows.append([a["successes"], b["successes"], a["steps"], b["steps"], round(a["mean_steps"], 9), round(b["mean_steps"], 9), a["episodes"], b["episodes"]])
print(json.dumps(rows))
""")
        for r in out:
            self.assertEqual(r[0], r[1], "successes")
            self.assertEqual(r[2], r[3], "steps")
            self.assertEqual(r[4], r[5], "mean steps")
            self.assertEqual(r[6], r[7], "episodes")
            self.assertGreater(r[2], 1000)

    def test_the_candidate_twice_is_identical(self) -> None:
        out = self._run("""
import json
from tools.toys import act_chooser_toy as toy
rows = []
for _ in range(2):
    p = toy.ScreenChooser(20260923)
    r = toy.run_game_fx(p, 20260923, 40)
    rows.append([r["successes"], r["steps"], r["last100"], p.live_history[-1], p.tracker.counts()["forward"]])
print(json.dumps(rows))
""")
        self.assertEqual(out[0], out[1])

    def test_the_harness_excludes_exactly_one_outcome_per_episode_boundary(self) -> None:
        out = self._run("""
import json
from tools.toys import act_chooser_toy as toy
p = toy.ScreenChooser(20260923)
r = toy.run_game_fx(p, 20260923, 30)
c = p.tracker.counts()
print(json.dumps({"excluded": sum(v["excluded"] for v in c.values()), "total": sum(v["total"] for v in c.values()),
                  "known": sum(v["known"] for v in c.values()), "steps": r["steps"], "episodes": r["episodes"]}))
""")
        self.assertEqual(out["episodes"], 30)
        self.assertEqual(out["excluded"], 29, "the first outcome of each episode after the first crosses the silent reset")
        self.assertEqual(out["total"], out["steps"])
        self.assertEqual(out["known"] + out["excluded"], out["total"])

    def test_M8_smoke_obs_equality_is_rendered_pov_equality(self) -> None:
        out = self._run("""
import json, contextlib, io, hashlib
import numpy as np
import gymnasium as gym, minigrid
env = gym.make("BabyAI-GoToLocal-v0", render_mode="rgb_array")
rng = np.random.default_rng(1)
mism = steps = changed = 0
for e in range(40):
    with contextlib.redirect_stdout(io.StringIO()):
        obs, _ = env.reset(seed=500 + e)
    po = obs["image"].tobytes(); pr = hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()
    while True:
        obs, r, te, tr, _ = env.step(int(rng.integers(0, 7)))
        co = obs["image"].tobytes(); cr = hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()
        mism += int((co == po) != (cr == pr)); changed += int(co != po); steps += 1; po, pr = co, cr
        if te or tr: break
print(json.dumps({"steps": steps, "mismatches": mism, "changed": changed}))
""")
        self.assertGreater(out["steps"], 1500)
        self.assertGreater(out["changed"], 500)
        self.assertEqual(out["mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
