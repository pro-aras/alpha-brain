# edit: Claude (Opus 5.5, S1c-2 builder), 2026-09-28 16:17 +0400 — PREREG-S1C2 (genome-wt-brain3 141a8cd, sha 5e4585c1…) §1–§5 with the
# coordinator's rulings (16:1x): the runner of S1c-2. On a synthetic room world with the REAL fixed test set:
#   - the new life, run as S1c's five arms, reproduces S1c's own life() field for field (the identity control's twin);
#   - PROGRESS+REPLAY at R = 0 IS PROGRESS; at R = 10 a block's drop is the room's own (a clone that sees only the block
#     reproduces POST_b), and a planted replay placed BEFORE POST is CAUGHT;
#   - the replay draws: the room grain uniform over the visited rooms then their consumed scenes, the visit grain uniform
#     over the consumed scenes, from `replay:<seed>:<block>`, never a scene not yet consumed;
#   - NET's pin algebra on the record; NULL-NET and NULL+REPLAY with identity credit ARE their estimates' pickers;
#   - the ORACLE+REPLAY's clone (no replay) IS the learner after the chosen block, before its replay;
#   - the BLOCK and FULL-STEP tables are equal on the bare learner (a pin) and differ by the replay on the replay learner;
#   - the identity diff catches a planted one-ulp change by field name and prints the masked fields side by side;
#   - the arm verdict's order (NOT GRADABLE BY NAME → FOR CHOICE → VOID → FAIL → CEILING-BOUND → PASS) and the refutations.
# Test-first: red on scene-s1c 2679fb3 (brain.scene.run_s1c2 does not exist there).
from __future__ import annotations

import copy
import math
import unittest
from unittest import mock

import numpy as np

from brain.scene import pickers as PK
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from tests.brain.scene.test_run_s1c import HAVE_TEST_SET, FakeRooms

LAW = ("R1", "R2", "R3", "N")


class TestLawAndArms(unittest.TestCase):
    def test_the_four_shas(self) -> None:
        got = S2.check_prereg()
        self.assertEqual(got["prereg_s1c2"], "5e4585c11c94d68d5294c35149aefd5636481d6eddcbed2e9b3952a42def2c46")
        self.assertEqual(got["prereg_s1c"], S.PREREG_S1C_SHA256)
        self.assertEqual(got["amend1_s1c"], "92188d04cd4de52eede4b1d2288c239ddd284d20ce93cce01545c98eb444f451")
        with mock.patch.object(S2, "PREREG_S1C2_SHA256", "0" * 64):
            with self.assertRaises(S2.S2Error):
                S2.check_prereg()

    def test_the_arms(self) -> None:
        self.assertEqual(len(S2.ARMS), 14)
        self.assertEqual(S2.IDENTITY_ARMS, ("PROGRESS", "RANDOM", "ERROR", "ORACLE", "NULL"))
        self.assertEqual(S2.ARM_SPEC["PROGRESS+REPLAY"], ("PROGRESS", "room"))
        self.assertEqual(S2.ARM_SPEC["PROGRESS+REPLAY-V"], ("PROGRESS", "visit"))
        self.assertEqual(sum(1 for a in S2.ARMS if S2.ARM_SPEC[a][1] is not None), 6)
        self.assertEqual(S2.ROOMS, LAW)
        self.assertEqual(S2.R_REPLAY, 10)
        self.assertEqual(S2.VOLATILE, ("cpu_s", "wall_s", "code", "prereg", "world"))


class TestReplayDraws(unittest.TestCase):
    def test_the_room_grain_and_the_visit_grain(self) -> None:
        by_room = {"R1": list(range(30)), "R2": list(range(10)), "R3": [], "N": list(range(60))}
        buffer = [(r, i) for r in ("R1", "R2", "N") for i in by_room[r]]
        rooms, scenes = [], []
        for b in range(1, 401):
            d = S2.replay_draws(20261301, b, by_room, buffer, LAW, 10, "room")
            self.assertEqual(len(d), 10)
            self.assertEqual(d, S2.replay_draws(20261301, b, by_room, buffer, LAW, 10, "room"))
            for r, i in d:
                self.assertIn(i, by_room[r])
            rooms += [r for r, _ in d]
            scenes += [(r, i) for r, i in d if r == "N"]
        for r in ("R1", "R2", "N"):
            self.assertAlmostEqual(rooms.count(r) / len(rooms), 1 / 3, delta=0.03)
        self.assertNotIn("R3", rooms)
        v = [x for b in range(1, 401) for x in S2.replay_draws(20261301, b, by_room, buffer, LAW, 10, "visit")]
        self.assertAlmostEqual(sum(1 for r, _ in v if r == "N") / len(v), 60 / 100, delta=0.03)
        self.assertNotEqual(S2.replay_draws(20261301, 7, by_room, buffer, LAW, 10, "room"),
                            S2.replay_draws(20261302, 7, by_room, buffer, LAW, 10, "room"))


@unittest.skipUnless(HAVE_TEST_SET, "S1b-1's caches of the fixed test set are not on this box")
class TestLife2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = S.FixedTestSet()
        cls.data = FakeRooms(rooms=LAW)

    def test_s1cs_five_arms_on_the_new_life_are_s1cs_life(self) -> None:
        for arm in S2.IDENTITY_ARMS:
            n = 12 if arm == "ORACLE" else 40
            old = S.life(self.data, self.test, arm, LAW, n_blocks=n)
            new = S2.life2(self.data, self.test, arm, LAW, n_blocks=n)
            self.assertEqual(S2.identity_diff(new, old), [], arm)
        old = S.life(self.data, self.test, "RANDOM", LAW, n_blocks=30, prefix=PK.band_prefix(self.data.seed, 3))
        new = S2.life2(self.data, self.test, "RANDOM", LAW, n_blocks=30, prefix=PK.band_prefix(self.data.seed, 3))
        self.assertEqual(S2.identity_diff(new, old), [])

    def test_the_identity_diff_catches_one_ulp_by_name_and_masks_only_the_five(self) -> None:
        old = S.life(self.data, self.test, "PROGRESS", LAW, n_blocks=20)
        new = copy.deepcopy(old)
        new["cpu_s"] += 1.0
        new["code"] = {"x": 1}
        self.assertEqual(S2.identity_diff(new, old), [])
        side = S2.masked_side_by_side(new, old)
        self.assertEqual(sorted(side), sorted(S2.VOLATILE))
        self.assertNotEqual(side["cpu_s"][0], side["cpu_s"][1])
        new["record"][7]["drop"] = float(np.nextafter(new["record"][7]["drop"], np.inf))
        self.assertEqual(S2.identity_diff(new, old), ["record"])

    def test_replay_at_r0_is_progress_and_the_bracket_is_the_rooms(self) -> None:
        p = S2.life2(self.data, self.test, "PROGRESS", LAW, n_blocks=30)
        r0 = S2.life2(self.data, self.test, "PROGRESS+REPLAY", LAW, n_blocks=30, R_=0)
        self.assertEqual(S2.identity_diff(r0, p), [])
        r10 = S2.life2(self.data, self.test, "PROGRESS+REPLAY", LAW, n_blocks=30, bracket_check=True)
        self.assertEqual(r10["bracket_check"], [])
        planted = S2.life2(self.data, self.test, "PROGRESS+REPLAY", LAW, n_blocks=10, bracket_check=True,
                           planted_replay_before_post=True)
        self.assertEqual(planted["bracket_check"], list(range(1, 11)))   # CAUGHT at every block
        for x in r10["record"]:
            self.assertEqual(len(x["replay"]), 10)
            self.assertEqual(sum(x["replay_mix"].values()), 10)
            for r in LAW:
                self.assertEqual(x["replay_effect"][r], x["L"][r] - x["PRE"][r])
            self.assertAlmostEqual(x["drop"], r10["table_pre"][x["block"] - 1][x["room"]] - x["L"][x["room"]], places=12)
            consumed = {(q, i) for y in r10["record"][:x["block"]] for q, i in
                        [(y["room"], j) for j in range(y["start"], y["start"] + 10)]}
            for q, i in x["replay"]:
                self.assertIn((q, i), consumed)
        self.assertNotEqual(r10["record"][-1]["L"], p["record"][-1]["L"])

    def test_the_block_and_full_step_tables(self) -> None:
        p = S2.life2(self.data, self.test, "PROGRESS", LAW, n_blocks=40)
        m = p["marks2"]
        self.assertEqual(m["block_table"], m["full_table"])               # the bare learner's pin
        self.assertEqual(m["block_table"], p["marks"]["interference"])    # = S1c's interference, exactly
        r = S2.life2(self.data, self.test, "PROGRESS+REPLAY", LAW, n_blocks=40)
        mr = r["marks2"]
        self.assertNotEqual(mr["block_table"], mr["full_table"])
        k = r["record"][10]
        b, room = k["block"], k["room"]
        self.assertTrue(math.isfinite(mr["offdiag_full"]) and math.isfinite(mr["offdiag_block"]))
        full_step = r["table_pre"][b][room] - r["table_pre"][b - 1][room]
        self.assertAlmostEqual(full_step, -k["drop"] - k["replay_effect"][room], places=9)
        self.assertAlmostEqual(mr["buffer_n_share"], r["replayed"]["N"] / sum(r["replayed"].values()))

    def test_net_pin_and_the_nulls_identity_credit(self) -> None:
        n = S2.life2(self.data, self.test, "PROGRESS-NET", LAW, n_blocks=60)
        self.assertEqual(S2.net_pin(n), [])
        bad = copy.deepcopy(n)
        bad["record"][30]["net"]["R1"] += 1e-6
        self.assertEqual(S2.net_pin(bad), [(31, "R1")])
        i = S2.life2(self.data, self.test, "NULL-NET", LAW, n_blocks=60, identity_credit=True)
        self.assertEqual(S2.rows_equal(i, n), True)
        nn = S2.life2(self.data, self.test, "NULL-NET", LAW, n_blocks=60)
        self.assertTrue(all(x["credited"] != x["room"] for x in nn["record"]))
        pr = S2.life2(self.data, self.test, "PROGRESS+REPLAY", LAW, n_blocks=30)
        ir = S2.life2(self.data, self.test, "NULL+REPLAY", LAW, n_blocks=30, identity_credit=True)
        self.assertEqual(S2.rows_equal(ir, pr), True)
        self.assertEqual(PK.exploration_mismatches(nn["record"], self.data.seed, LAW), [])

    def test_the_oracle_replays_after_its_clone_matched(self) -> None:
        o = S2.life2(self.data, self.test, "ORACLE+REPLAY", LAW, n_blocks=8)
        pol = [x for x in o["record"] if x["flag"] == "policy"]
        self.assertEqual(len(pol), 4)
        self.assertTrue(all(x["clone_identical"] for x in pol))
        self.assertTrue(all(len(x["replay"]) == 10 for x in o["record"]))

    def test_ucb_pin(self) -> None:
        u = S2.life2(self.data, self.test, "PROGRESS-UCB", LAW, n_blocks=40)
        self.assertEqual(S2.ucb_pin(u), {"visits_ge_1": True, "c_positive_from_5": True, "t_ge_1": True})


def _mk(A, sn, leave=10):
    return {"A": A, "share": {"N": sn}, "leave": {"N": leave}}


class TestArmVerdict(unittest.TestCase):
    def _seeds(self, x, o=(0.9, 0.0), rnd=0.6, nul=(0.3, 0.6), band=(0.55, 0.62)):
        out = {}
        for s in (1, 2, 3):
            lo, hi = band
            out[s] = {"X": _mk(*x) if isinstance(x, tuple) else x, "O": _mk(*o), "RND": _mk(rnd, 0.25), "NUL": _mk(*nul),
                      "band_A": list(np.linspace(lo, hi, 20)), "band_n": 20}
        return out

    def test_the_order(self) -> None:
        v = S2.arm_verdict(self._seeds((0.8, 0.03)))
        self.assertEqual(v["verdict"], "PASS")
        self.assertEqual(S2.arm_verdict(self._seeds((0.8, 0.2)))["verdict"], "FAIL")
        self.assertEqual(S2.arm_verdict(self._seeds((0.6, 0.03)))["verdict"], "FAIL")          # inside the band, O above
        ceil = self._seeds((0.8, 0.03), o=(0.61, 0.0), band=(0.55, 0.62), rnd=0.5)
        ceil = {s: dict(v, X=_mk(0.6, 0.03)) for s, v in ceil.items()}
        self.assertEqual(S2.arm_verdict(ceil)["verdict"], "CEILING-BOUND")                  # O not above the edge
        mixed = self._seeds((0.8, 0.2), o=(0.61, 0.0), band=(0.55, 0.62), rnd=0.5)
        self.assertEqual(S2.arm_verdict(mixed)["verdict"], "FAIL")                          # a meetable miss → FAIL
        self.assertEqual(S2.arm_verdict(self._seeds((0.8, 0.03), nul=(0.8, 0.02)))["verdict"], "VOID")
        self.assertEqual(S2.arm_verdict(self._seeds((0.8, 0.03), rnd=0.88))["verdict"], "NOT GRADABLE FOR CHOICE")
        miss = self._seeds((0.8, 0.03))
        del miss[2]["NUL"]
        v = S2.arm_verdict(miss)
        self.assertEqual(v["verdict"], "NOT GRADABLE BY NAME")
        self.assertIn("NUL@2", v["missing"])
        short = self._seeds((0.8, 0.03))
        short[3]["band_A"] = short[3]["band_A"][:19]
        short[3]["band_n"] = 19
        self.assertEqual(S2.arm_verdict(short)["verdict"], "NOT GRADABLE BY NAME")


class TestRefutations(unittest.TestCase):
    def _runs(self, net_share=0.3, net_A=0.5, off_rep=-0.1, off_prog=0.2, rep_A=0.6, er_share=0.7, o_rep=0.8, r_rep=0.6):
        def run(A, sn, off=None):
            return {"marks": {"A": A, "share": {"N": sn}}, "marks2": {"offdiag_full": off}}
        return {s: {"PROGRESS-NET": run(net_A, net_share), "ORACLE": run(0.75, 0.01), "PROGRESS": run(0.55, 0.2, off_prog),
                    "PROGRESS+REPLAY": run(rep_A, 0.1, off_rep), "ERROR+REPLAY": run(0.2, er_share),
                    "ORACLE+REPLAY": run(o_rep, 0.01), "RANDOM+REPLAY": run(r_rep, 0.25)} for s in (20261301, 20261302, 20261303)}

    def _bands(self):
        def life(A, sn):
            return {"marks": {"A": A, "share": {"N": sn}}}
        bare = [life(a, sn) for a, sn in zip(np.linspace(0.52, 0.58, 20), np.linspace(0.19, 0.30, 20))]
        rep = [life(a, sn) for a, sn in zip(np.linspace(0.58, 0.64, 20), np.linspace(0.20, 0.29, 20))]
        return {s: {"bare": bare, "replay": rep} for s in (20261301, 20261302, 20261303)}

    def test_each_refutation_reads_its_own_clause(self) -> None:
        r = S2.refutations2(self._runs(), self._bands())
        self.assertTrue(all(r["a"].values()))                      # 0.30 ≥ the band's low edge
        self.assertFalse(any(r["b"].values()))                     # SHARE_N 0.30 misses its bar
        self.assertFalse(any(r["c"].values()))                     # −0.1 < 0.2: forgetting reduced
        self.assertTrue(all(r["d"].values()))                      # 0.60 inside [0.58, 0.64], the control 0.2
        self.assertFalse(any(r["e"].values()))                     # 0.70 above the band
        r2 = S2.refutations2(self._runs(net_share=0.02, net_A=0.40, off_rep=0.3, er_share=0.1), self._bands())
        self.assertFalse(any(r2["a"].values()))
        self.assertTrue(all(r2["b"].values()))                     # the starvation mode
        self.assertTrue(all(r2["c"].values()))
        self.assertTrue(all(r2["e"].values()))
        short = self._bands()
        short[20261302]["replay"] = short[20261302]["replay"][:10]
        r3 = S2.refutations2(self._runs(), short)
        self.assertIsNone(r3["d"][20261302])                       # a short band is NOT GRADABLE, never shrunk
        self.assertIsNone(r3["e"][20261302])


if __name__ == "__main__":
    unittest.main()
