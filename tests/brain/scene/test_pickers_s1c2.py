# edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:15 +0400 — PREREG-S1C2 §2 (genome-wt-brain3 docs/brain/r3/PREREG-S1C2.md at brain-design-3
# 141a8cd, sha 5e4585c1…): the two new estimates. PROGRESS-NET — net_k = PRE_{v_k}(k) − PRE_now(k), re-read at every boundary
# (it refreshes without a visit and cannot freeze), no smoothing, an unvisited room picked first; NULL-NET — the same estimate
# with room k's reading credited to π(k) (a derangement from `null:seed`; the identity credit reproduces NET's picks exactly;
# a credit landing home RAISES). PROGRESS-UCB (a reading) — S1c's estimate + c · √(2 ln t / n_k), c the running mean |drop|,
# t the policy blocks including the one being picked (declared), n_k the room's visits. Test-first: red on scene-s1c 2679fb3.
from __future__ import annotations

import math
import unittest

import numpy as np

from brain.scene import pickers as PK

ROOMS = ("R1", "R2", "R3", "N")
SEED = 20261301


class _Env:
    """A stub life with PRE readings: each room's loss falls by its own drop on its block and rises by `rise` on the other
    rooms' blocks (the forgetting S1c named)."""

    def __init__(self, seed: int = 3, rise: float = 0.2):
        rng = np.random.default_rng(seed)
        self.drops = {r: list(np.abs(rng.normal(size=400)) * (0.2 if r == "N" else 1.0)) for r in ROOMS}
        self.rise = rise

    def run(self, picker, n_blocks: int = 60):
        last = {r: 0 for r in ROOMS}
        visits = {r: 0 for r in ROOMS}
        pre = {r: 10.0 for r in ROOMS}
        out = []
        for b in range(1, n_blocks + 1):
            est = picker.estimates()
            if b <= len(ROOMS):
                room, flag = ROOMS[b - 1], "round-robin"
            else:
                room, flag = picker.pick(b, PK.Context(last_visit=dict(last), L_now=dict(pre)))
            d = self.drops[room][visits[room]]
            visits[room] += 1
            post = {r: (pre[r] - d if r == room else pre[r] + self.rise) for r in ROOMS}
            credited = picker.observe(b, room, drop=pre[room] - post[room], drift=0.0, pre_before=dict(pre), pre_after=dict(post))
            out.append({"block": b, "room": room, "flag": flag, "est": est, "credited": credited,
                        "pre": dict(pre), "post": dict(post)})
            pre = post
            last[room] = b
        return out


class TestNet(unittest.TestCase):
    def test_net_is_the_loss_before_the_last_visit_minus_the_loss_now(self) -> None:
        p = PK.NetPicker(ROOMS, SEED)
        self.assertEqual(p.estimates(), {r: None for r in ROOMS})
        pre0 = {"R1": 10.0, "R2": 9.0, "R3": 8.0, "N": 7.0}
        post1 = {"R1": 6.0, "R2": 9.5, "R3": 8.2, "N": 7.1}
        self.assertEqual(p.observe(1, "R1", drop=4.0, drift=0.0, pre_before=pre0, pre_after=post1), "R1")
        self.assertEqual(p.estimates()["R1"], 4.0)
        post2 = {"R1": 6.9, "R2": 5.0, "R3": 8.3, "N": 7.2}
        p.observe(2, "R2", drop=4.5, drift=0.0, pre_before=post1, pre_after=post2)
        e = p.estimates()
        self.assertAlmostEqual(e["R1"], 10.0 - 6.9)                  # refreshed WITHOUT a visit: the time away is netted
        self.assertAlmostEqual(e["R2"], 9.5 - 5.0)
        self.assertIsNone(e["R3"])

    def test_an_unvisited_room_is_picked_first_and_the_readings_are_required(self) -> None:
        p = PK.NetPicker(ROOMS, SEED)
        p.observe(1, "R1", drop=1.0, drift=0.0, pre_before={r: 5.0 for r in ROOMS}, pre_after={r: 4.0 for r in ROOMS})
        b = next(b for b in range(5, 500) if PK.explore_draw(SEED, b, ROOMS) is None)
        room, flag = p.pick(b, PK.Context(last_visit={"R1": 1, "R2": 0, "R3": 0, "N": 0}, L_now={}))
        self.assertEqual((room, flag), ("N", "policy"))                # unvisited, least recently visited then by name
        with self.assertRaises(PK.PickerError):
            p.observe(2, "R2", drop=1.0, drift=0.0)

    def test_the_pin_algebra_on_a_life(self) -> None:
        rec = _Env().run(PK.NetPicker(ROOMS, SEED), n_blocks=80)
        last_v, drop_v, cum = {}, {}, {}
        for x in rec:
            k = x["room"]
            last_v[k], drop_v[k], cum[k] = x["block"], x["pre"][k] - x["post"][k], 0.0
            for r in ROOMS:
                if r != k and r in cum:
                    cum[r] += x["post"][r] - x["pre"][r]      # the intervening change of r's PRE reading
            if x["block"] < len(rec):
                nxt = rec[x["block"]]["est"]                  # the estimate read at the next pick
                for r in last_v:
                    self.assertAlmostEqual(nxt[r], drop_v[r] - cum[r], places=9)

    def test_null_net_credits_the_derangement_and_the_identity_is_net(self) -> None:
        a = _Env().run(PK.NetPicker(ROOMS, SEED))
        b = _Env().run(PK.NullNetPicker(ROOMS, SEED, credit={r: r for r in ROOMS}, allow_identity=True))
        self.assertEqual([(x["room"], x["flag"], x["est"]) for x in a], [(x["room"], x["flag"], x["est"]) for x in b])
        n = PK.NullNetPicker(ROOMS, SEED)
        self.assertEqual(n.pi, PK.null_derangement(SEED, ROOMS))
        rec = _Env().run(n)
        for x in rec:
            self.assertEqual(x["credited"], n.pi[x["room"]])
            self.assertNotEqual(x["credited"], x["room"])
        net = PK.NetPicker(ROOMS, SEED)
        nul = PK.NullNetPicker(ROOMS, SEED)
        for x in rec[:12]:
            for q in (net, nul):
                q.observe(x["block"], x["room"], drop=0.0, drift=0.0, pre_before=x["pre"], pre_after=x["post"])
        en, eu = net.estimates(), nul.estimates()
        for k in ROOMS:
            self.assertEqual(eu[nul.pi[k]], en[k])                   # room k's reading lands on π(k)
        bad = PK.NullNetPicker(ROOMS, SEED)
        bad.pi["R1"] = "R1"
        with self.assertRaises(PK.PickerError):
            bad.observe(1, "R1", drop=0.0, drift=0.0, pre_before={r: 1.0 for r in ROOMS}, pre_after={r: 1.0 for r in ROOMS})
        with self.assertRaises(PK.PickerError):
            PK.NullNetPicker(ROOMS, SEED, credit={r: r for r in ROOMS})


class TestUCB(unittest.TestCase):
    def test_the_score_the_bonus_and_its_scale(self) -> None:
        u = PK.UCBPicker(ROOMS, SEED, n_round_robin=4)
        drops = {"R1": 1.0, "R2": 3.0, "R3": 0.5, "N": 0.1}
        for b, r in enumerate(ROOMS, start=1):
            u.observe(b, r, drop=drops[r], drift=0.0)
        self.assertEqual(u.visits, {r: 1 for r in ROOMS})
        self.assertAlmostEqual(u.c(), np.mean([abs(v) for v in drops.values()]))
        b = next(b for b in range(5, 500) if PK.explore_draw(SEED, b, ROOMS) is None)
        room, flag = u.pick(b, PK.Context(last_visit={r: i + 1 for i, r in enumerate(ROOMS)}, L_now={}))
        info = u.last_pick
        t = b - 4
        for r in ROOMS:
            bonus = u.c() * math.sqrt(2.0 * math.log(t) / 1.0)
            self.assertAlmostEqual(info["bonus"][r], bonus)
            self.assertAlmostEqual(info["score"][r], drops[r] + bonus)
        self.assertEqual((room, flag), ("R2", "policy"))
        self.assertEqual(info["t"], t)

    def test_t_counts_the_pick_itself_so_the_first_policy_block_is_defined(self) -> None:
        u = PK.UCBPicker(ROOMS, SEED, n_round_robin=4)
        for b, r in enumerate(ROOMS, start=1):
            u.observe(b, r, drop=1.0, drift=0.0)
        b5 = 5 if PK.explore_draw(SEED, 5, ROOMS) is None else None
        if b5 is not None:
            u.pick(5, PK.Context(last_visit={r: i + 1 for i, r in enumerate(ROOMS)}, L_now={}))
            self.assertEqual(u.last_pick["t"], 1)
            self.assertTrue(all(v == 0.0 for v in u.last_pick["bonus"].values()))   # ln 1 = 0
        self.assertTrue(all(math.isfinite(v) for v in u.scores(6)[0].values()))

    def test_a_long_absent_room_gains_score_without_a_visit(self) -> None:
        u = PK.UCBPicker(ROOMS, SEED, n_round_robin=4)
        for b, r in enumerate(ROOMS, start=1):
            u.observe(b, r, drop=1.0, drift=0.0)
        for b in range(5, 40):
            u.observe(b, "R1", drop=1.0, drift=0.0)
        s10, _ = u.scores(10)
        s100, _ = u.scores(100)
        self.assertGreater(s100["N"] - s10["N"], s100["R1"] - s10["R1"])
        self.assertEqual(u.estimates()["R1"], 1.0)                    # S1c's estimate underneath, unchanged


if __name__ == "__main__":
    unittest.main()
