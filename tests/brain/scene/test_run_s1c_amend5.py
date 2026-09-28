# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:35 +0400 — AMENDMENT 1 §5 (genome-wt-brain3 docs/brain/r3/PREREG-S1C-AMEND-1.md at
# brain-design-3 04b3846, sha 46fbd5dd…), after THE FIRST GATE stopped on K: THE LAW'S WORLD is R1, R2, R3 and N (a 4-block
# round-robin, 196 policy blocks, ε, π and the ORACLE's clones over the four; every §4 bar but SHARE_U — A, SHARE_N + 0.05,
# LEAVE_N ≤ 50 (earliest now 4), the positive control, §3's null clause; refutation (c) gone with U); K
# runs BESIDE it as a READING world (R1, R2, R3, N, K) that carries no bar — A, SHARE_N, SHARE_K, LEAVE_N, the interference
# column of L_K, K's own drop per visit and RANDOM's band are printed. Gate step 2 re-runs on the law's four rooms (N flat,
# R1–R3 ≥ 3 × N) and only PRINTS K (i) / K (ii) on the reading world — a K miss never flips the gate. The unit is LOCKED
# (the run and band commands refuse) until the co-signed sha lands. Test-first: red on scene-s1c 556b5b2.
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import pickers as PK
from brain.scene import run_s1c as S
from tests.brain.scene.test_run_s1c import HAVE_TEST_SET, FakeRooms

LAW = ("R1", "R2", "R3", "N")
KW = ("R1", "R2", "R3", "N", "K")


class TestWorldsAndShas(unittest.TestCase):
    def test_the_two_worlds_and_the_pools_they_read(self) -> None:
        self.assertEqual(S.WORLDS, {"law": LAW, "k": KW})
        self.assertEqual(S.POOL_ROOMS, KW)

    def test_the_gate_checks_the_text_it_implements(self) -> None:
        self.assertEqual(S.AMEND1_S1C_SHA256, "92188d04cd4de52eede4b1d2288c239ddd284d20ce93cce01545c98eb444f451")   # co-signed, 2daeb66
        self.assertEqual(S.check_prereg()["amend1_s1c"], S.AMEND1_S1C_SHA256)

    def test_the_unit_is_locked_until_the_cosigned_sha(self) -> None:
        self.assertFalse(S.AMEND1_COSIGNED)
        for argv in (["run", "--world", "law", "--picker", "RANDOM", "--seed", "20261301"],
                     ["band", "--world", "k", "--seed", "20261301", "--k", "1-1"]):
            with self.assertRaises(S.S1cError):
                S.main(argv + ["--root", "/nonexistent/s1c-lock-test"])


def _run(rooms, n_blocks=60, k_rise=0.0):
    """A synthetic step-2 life: rooms in rotation; each learnable room falls 0.05 per own block; N flat; K falls 5.0 on its
    own block and rises `k_rise` on every other room's block."""
    rec, table = [], [{r: 10.0 for r in rooms}]
    for b in range(1, n_blocks + 1):
        room = rooms[(b - 1) % len(rooms)]
        prev = dict(table[-1])
        new = dict(prev)
        if room in ("R1", "R2", "R3"):
            new[room] = prev[room] - 0.05
        if "K" in rooms:
            new["K"] = prev["K"] - 5.0 if room == "K" else prev["K"] + k_rise
        rec.append({"block": b, "room": room, "flag": "policy", "drop": prev[room] - new[room]})
        table.append(new)
    return {"record": rec, "table": table, "rooms": list(rooms)}


class TestGateStepTwo(unittest.TestCase):
    def test_the_laws_world_reads_n_and_r_only(self) -> None:
        c = S.room_claims(_run(LAW))
        self.assertNotIn("K", c)
        self.assertNotIn("U", c)
        self.assertTrue(c["N"]["pass"] and c["R"]["pass"] and c["pass"])

    def test_the_k_world_prints_k_and_a_k_miss_never_flips_the_gate(self) -> None:
        c = S.room_claims(_run(KW, k_rise=1.25))
        k = c["K"]
        self.assertTrue(c["pass"])                                    # N and R pass; K is a print
        self.assertFalse(k["pass_i"])                                 # own drop 5.0 ≫ 0.05 × level
        self.assertEqual(set(k["levels"]), {"mean over boundaries 21–60", "L_K at the last boundary", "the largest L_K in 21–60"})
        self.assertTrue(all(not v["pass"] for v in k["levels"].values()))
        own = [x["drop"] for x in _run(KW, k_rise=1.25)["record"] if x["room"] == "K"]
        self.assertEqual(k["own_drops"], own)
        self.assertAlmostEqual(k["all_blocks_mean_drop"], (c["K"]["L_K_at"][20] - c["K"]["L_K_at"][60]) / 40)
        self.assertIn("pass_ii", k)


@unittest.skipUnless(HAVE_TEST_SET, "S1b-1's caches of the fixed test set are not on this box")
class TestFourAndFiveRoomLives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = S.FixedTestSet()
        cls.law = FakeRooms(rooms=LAW)
        cls.kw = FakeRooms(rooms=KW)

    def test_the_laws_world_round_robin_exploration_and_null_over_four(self) -> None:
        p = S.life(self.law, self.test, "PROGRESS", LAW, n_blocks=40)
        self.assertEqual([x["room"] for x in p["record"][:4]], list(LAW))
        self.assertTrue(all(x["flag"] == "round-robin" for x in p["record"][:4]))
        self.assertTrue(set(x["room"] for x in p["record"]) <= set(LAW))
        self.assertEqual(PK.exploration_mismatches(p["record"], self.law.seed, LAW), [])
        self.assertEqual(p["marks"]["n_policy_blocks"], 36)
        self.assertTrue(all(v >= 4 for v in p["marks"]["leave"].values()))
        n = S.life(self.law, self.test, "NULL", LAW, n_blocks=40)
        self.assertTrue(PK.is_derangement(n["pi"]) and sorted(n["pi"]) == sorted(LAW))
        ident = S.life(self.law, self.test, "NULL", LAW, n_blocks=40, identity_credit=True)
        keys = ("block", "room", "flag", "est", "L", "drop", "credited", "wl")
        self.assertEqual([{k: x[k] for k in keys} for x in p["record"]], [{k: x[k] for k in keys} for x in ident["record"]])

    def test_the_oracles_clones_cover_the_four(self) -> None:
        o = S.life(self.law, self.test, "ORACLE", LAW, n_blocks=7)
        pol = [x for x in o["record"] if x["flag"] == "policy"]
        self.assertEqual(len(pol), 3)
        for x in pol:
            self.assertEqual(sorted(x["gains"]), sorted(LAW))
            self.assertTrue(x["clone_identical"])

    def test_the_k_world_readings(self) -> None:
        runs = {p: S.life(self.kw, self.test, p, KW, n_blocks=25) for p in PK.PICKERS}
        rd = S.k_readings(runs)
        for p in PK.PICKERS:
            r = rd[p]
            m = runs[p]["marks"]
            self.assertEqual((r["A"], r["SHARE_N"], r["SHARE_K"], r["LEAVE_N"]),
                             (m["A"], m["share"]["N"], m["share"]["K"], m["leave"]["N"]))
            self.assertEqual(r["K_own_drops"], [x["drop"] for x in runs[p]["record"] if x["room"] == "K"])
            self.assertEqual(r["K_column"], {j: m["interference"][j]["K"] for j in KW})
            self.assertEqual(r["n_K_visits"], len(r["K_own_drops"]))


class TestLawVerdict(unittest.TestCase):
    def _per_seed(self, prog, null, leave_ok=True):
        def mk(A, sn, leave=10):
            return {"A": A, "share": {"N": sn}, "leave": {"N": leave}}
        return {s: {"ORACLE": mk(0.9, 0.0), "RANDOM": mk(0.7, 0.25), "PROGRESS": prog, "NULL": null,
                    "ERROR": mk(0.5, 0.8), "PROGRESS-DRIFT": mk(0.7, 0.2)} for s in (1, 2, 3)}

    def test_no_share_u_and_no_refutation_c_in_the_laws_world(self) -> None:
        good = {"A": 0.85, "share": {"N": 0.03}, "leave": {"N": 10}}
        weak = {"A": 0.70, "share": {"N": 0.03}, "leave": {"N": 10}}
        v = S.verdict_of(self._per_seed(good, weak), u_kept=False)
        self.assertEqual(v["verdict"], "PASS")
        self.assertNotIn("SHARE_U", v["bars"][1])
        self.assertNotIn("c", S.refutations(self._per_seed(good, weak), u_kept=False))


if __name__ == "__main__":
    unittest.main()
