# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:14 +0400 — PREREG-S1C §2–§4 and §6 (genome-wt-brain3 docs/brain/r3/PREREG-S1C.md, sha
# a552515a…) with AMENDMENT 1 (PREREG-S1C-AMEND-1.md, sha 825f4ad8…): the runner. The three shas are checked (a planted
# foreign sha REFUSES); the batched WORDS-LEARNED and M1 readers equal the learner's own name_forced / answer_point and S1a's
# grader item by item on REAL states (the fixed test set is S1b-1's caches of S1's three test seeds); on a synthetic room
# world, the planted identity-credit NULL reproduces PROGRESS's life exactly, the null's credit never lands home, the
# ORACLE's chosen clone IS the learner after the same block and its pick follows its own rule; the marks, the gate's room
# claims and the verdict's order read as the PREREG writes them. Test-first: red on scene-s1b1 7706371 (brain.scene.run_s1c
# does not exist there).
from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from brain.world.seeds import substream

from brain.scene import cache as C
from brain.scene import learners as Lr
from brain.scene import pickers as PK
from brain.scene import rooms as RM
from brain.scene import run_s1c as S

HAVE_TEST_SET = all((C.RUNS / str(ws) / "keys.json").exists() for ws in (20261101, 20261102, 20261103))
ROOM_WORDS = {"R1": ("circle", "square"), "R2": ("triangle", "cross"), "R3": ("ring", "star"),
              "N": RM.VOCAB13, "K": ("red", "star"), "U": ("red", "blue", "circle", "star")}


class FakeRooms:
    """A synthetic room world with the RoomData interface: a scene's inputs and words are a function of (room, i)."""

    def __init__(self, seed: int = 20261301, rooms=RM.ROOMS):
        self.seed, self.rooms = seed, list(rooms)
        self.window = {r: PK.WindowSet(*zip(*[self.visit_scene(r, 5_000 + i) for i in range(8)]), RM.VOCAB13)
                       for r in self.rooms}

    def visit_scene(self, room, i):
        rng = substream(1, f"fake:{room}:{i}")
        h = int(rng.integers(1, 4))
        X = rng.normal(size=(h, Lr.RW_DIM)) + (RM.ROOMS.index(room) - 2.5)
        vocab = ROOM_WORDS[room]
        words = [vocab[int(k)] for k in rng.choice(len(vocab), size=min(2, len(vocab)), replace=False)]
        return X, words


class TestPrereg(unittest.TestCase):
    def test_the_three_shas_and_a_planted_foreign_one(self) -> None:
        got = S.check_prereg()
        self.assertEqual(got["prereg_s1c"], S.PREREG_S1C_SHA256)
        self.assertEqual(got["amend1_s1c"], S.AMEND1_S1C_SHA256)
        with mock.patch.object(S, "AMEND1_S1C_SHA256", "0" * 64):
            with self.assertRaises(S.S1cError):
                S.check_prereg()
        with mock.patch.object(S, "PREREG_S1C_SHA256", "f" * 64):
            with self.assertRaises(S.S1cError):
                S.check_prereg()

    def test_the_learner_is_s1b1s_a_rw_at_lr_001(self) -> None:
        L = S.new_learner()
        self.assertIsInstance(L, Lr.RWLearner)
        self.assertEqual((L.lr, L.oracle), (0.01, False))


@unittest.skipUnless(HAVE_TEST_SET, "S1b-1's caches of the fixed test set are not on this box")
class TestFixedTestSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = S.FixedTestSet()
        cls.states = []
        data = FakeRooms()
        L = S.new_learner()
        cur = {r: 0 for r in RM.ROOMS}
        for b in range(18):
            r = RM.ROOMS[b % 6]
            S.train_block(L, data, r, cur[r], data.seed)
            cur[r] += 10
            if b in (2, 17):
                import copy
                cls.states.append(copy.deepcopy(L))
        # a REAL state too: S1b-1's A-RW stream (seed 20261101's training cache) for 300 scenes
        from brain.scene import run as R
        tr = R.Things(C.ScenePercepts(C.cache_dir(C.RUNS, 20261101, "train")))
        L2 = S.new_learner()
        R.train_arm("A-RW", L2, tr, tr.p.words, None, range(300), 20261101)
        cls.states.append(L2)

    def test_counts_and_per_word_n(self) -> None:
        # edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 00:1x +0400 — PREREG-BRAIN-LONG-6 §1.2 (the law
        # SIGNED; SEAT-LINE sha256 2c6bb22b…): the pin's counts gain the law's declared 4th world seed's battery
        # (20261211: NAME +163, M1 +397 — the questions run's own print; the values below MEASURED from the built
        # FixedTestSet, never hand-typed: seat's slot run bl6-s1c-counts). The pin working, caught at the launch gate.
        self.assertEqual(len(self.test.name_truth), 635)
        self.assertEqual(len(self.test.m1), 1590)
        self.assertEqual(min(self.test.word_n.values()), 73)
        self.assertEqual(self.test.word_n["big"] + self.test.word_n["small"], 635)

    def test_the_batched_readers_are_the_learners_own_calls(self) -> None:
        for L in self.states:
            pin = self.test.pin(L)
            self.assertEqual((pin["names_mismatch"], pin["points_mismatch"]), (0, 0), pin)
            ans = self.test.points(L)
            self.assertEqual(self.test.m1_fast(L, ans), self.test.m1_full(L, ans)["graded"]["covered"])

    def test_an_unnamed_word_is_a_miss(self) -> None:
        L = S.new_learner()
        n, rates = self.test.words_learned(L)
        self.assertEqual(n, 0)
        self.assertTrue(all(v == 0.0 for v in rates.values()))


@unittest.skipUnless(HAVE_TEST_SET, "S1b-1's caches of the fixed test set are not on this box")
class TestLife(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = S.FixedTestSet()
        cls.data = FakeRooms()

    def test_identity_credit_null_is_progress_and_the_null_never_credits_home(self) -> None:
        a = S.life(self.data, self.test, "PROGRESS", RM.ROOMS, n_blocks=30)
        b = S.life(self.data, self.test, "NULL", RM.ROOMS, n_blocks=30, identity_credit=True)
        keys = ("block", "room", "flag", "start", "est", "L", "drop", "drift", "credited", "wl")
        self.assertEqual([{k: x[k] for k in keys} for x in a["record"]], [{k: x[k] for k in keys} for x in b["record"]])
        n = S.life(self.data, self.test, "NULL", RM.ROOMS, n_blocks=30)
        self.assertTrue(PK.is_derangement(n["pi"]))
        for x in n["record"]:
            self.assertEqual(x["credited"], n["pi"][x["room"]])
            self.assertNotEqual(x["credited"], x["room"])
        self.assertEqual(PK.exploration_mismatches(n["record"], self.data.seed, RM.ROOMS), [])

    def test_the_oracle_clone_is_the_learner_and_the_pick_follows_the_rule(self) -> None:
        o = S.life(self.data, self.test, "ORACLE", RM.ROOMS, n_blocks=12)
        pol = [x for x in o["record"] if x["flag"] == "policy"]
        self.assertEqual(len(pol), 6)
        last = {}
        for x in o["record"]:
            if x["flag"] == "policy":
                self.assertTrue(x["clone_identical"])
                g = x["gains"]
                best = max(v[0] for v in g.values())
                tied = [r for r in RM.ROOMS if g[r][0] >= best - 1]
                m1 = {r: (g[r][1] if g[r][1] is not None else -float("inf")) for r in tied}
                top = max(m1.values())
                cands = [r for r in tied if m1[r] == top]
                self.assertEqual(x["room"], min(cands, key=lambda r: (last.get(r, 0), r)))
            last[x["room"]] = x["block"]

    def test_round_robin_cursors_and_the_drift_reading(self) -> None:
        d = S.life(self.data, self.test, "PROGRESS-DRIFT", RM.ROOMS, n_blocks=12)
        self.assertEqual([x["room"] for x in d["record"][:6]], list(RM.ROOMS))
        self.assertTrue(all(x["flag"] == "round-robin" for x in d["record"][:6]))
        starts = {}
        for x in d["record"]:
            self.assertEqual(x["start"], starts.get(x["room"], 0))
            starts[x["room"]] = x["start"] + 10
            self.assertTrue(0.0 <= x["drift"] <= 1.0 + 1e-12)
        self.assertEqual(len(d["table"]), 13)
        self.assertEqual(d["pin_end"]["names_mismatch"] + d["pin_end"]["points_mismatch"], 0)


def _rec(rooms_flags, wl=None):
    return [{"block": i + 1, "room": r, "flag": f, "drop": 0.1 * (i + 1), "wl": (wl[i] if wl else 0)}
            for i, (r, f) in enumerate(rooms_flags)]


class TestMarks(unittest.TestCase):
    def test_share_explore_leave_a_s12_and_the_lock_in(self) -> None:
        rooms = list(RM.ROOMS)
        rr = [(r, "round-robin") for r in rooms]
        pol = [("N", "policy"), ("N", "policy"), ("N", "explore"), ("R1", "policy"), ("N", "policy"), ("K", "policy")]
        wl = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 12, 13]
        table = [{r: 10.0 - 0.1 * b for r in rooms} for b in range(13)]
        run = {"record": _rec(rr + pol, wl), "rooms": rooms, "table": table, "n_blocks": 12, "m1_end_value": 0.9}
        m = S.run_marks(run)
        self.assertEqual(m["n_policy_blocks"], 6)
        self.assertAlmostEqual(m["share"]["N"], 3 / 6)
        self.assertAlmostEqual(m["explore"]["N"], 1 / 6)
        self.assertAlmostEqual(m["share"]["R1"], 1 / 6)
        self.assertEqual(m["leave"]["N"], 11)
        self.assertEqual(m["leave"]["U"], 6)                       # never picked by the policy: the round-robin's end
        self.assertAlmostEqual(m["A"], np.mean(wl) / 13)
        self.assertEqual(m["S12"], 100)
        self.assertEqual((m["longest_run"], m["longest_run_room"]), (3, "N"))
        self.assertAlmostEqual(m["interference"]["N"]["R1"], -0.1)


def _marks(A, sn, su=0.0, leave=10):
    return {"A": A, "share": {"N": sn, "U": su}, "leave": {"N": leave}}


class TestVerdict(unittest.TestCase):
    def _per_seed(self, prog, null, oracle=(0.9, 0.0), rand=0.7):
        out = {}
        for s in (1, 2, 3):
            out[s] = {"ORACLE": _marks(oracle[0], oracle[1]), "RANDOM": _marks(rand, 0.17), "PROGRESS": prog,
                      "NULL": null, "ERROR": _marks(0.5, 0.8), "PROGRESS-DRIFT": _marks(0.7, 0.2)}
        return out

    def test_pass_fail_void_not_gradable(self) -> None:
        good, weak = _marks(0.85, 0.03), _marks(0.70, 0.03)
        self.assertEqual(S.verdict_of(self._per_seed(good, weak), u_kept=True)["verdict"], "PASS")
        self.assertEqual(S.verdict_of(self._per_seed(_marks(0.85, 0.2), weak), u_kept=True)["verdict"], "FAIL")
        self.assertEqual(S.verdict_of(self._per_seed(_marks(0.85, 0.03, leave=51), weak), u_kept=True)["verdict"], "FAIL")
        self.assertEqual(S.verdict_of(self._per_seed(good, _marks(0.8, 0.02)), u_kept=True)["verdict"], "VOID")
        self.assertEqual(S.verdict_of(self._per_seed(good, weak, rand=0.87), u_kept=True)["verdict"], "NOT GRADABLE")
        v = S.verdict_of(self._per_seed(good, weak), u_kept=False)
        self.assertNotIn("SHARE_U", v["bars"][1])

    def test_the_null_voids_only_at_two_seeds(self) -> None:
        ps = self._per_seed(_marks(0.85, 0.03), _marks(0.70, 0.03))
        ps[1]["NULL"] = _marks(0.8, 0.02)
        self.assertEqual(S.verdict_of(ps, u_kept=True)["verdict"], "PASS")
        ps[2]["NULL"] = _marks(0.8, 0.02)
        self.assertEqual(S.verdict_of(ps, u_kept=True)["verdict"], "VOID")


class TestRoomClaims(unittest.TestCase):
    def test_the_gate_two_readings(self) -> None:
        rooms = list(RM.ROOMS)
        rec, table = [], [{r: 10.0 for r in rooms}]
        for b in range(1, 61):
            room = rooms[(b - 1) % 6]
            prev = dict(table[-1])
            new = dict(prev)
            if room in ("R1", "R2", "R3"):
                new[room] = prev[room] - 0.05
            rec.append({"block": b, "room": room, "flag": "policy", "drop": prev[room] - new[room]})
            table.append(new)
        c = S.room_claims({"record": rec, "table": table, "rooms": rooms})
        self.assertAlmostEqual(c["N"]["mean_drop"], 0.0)
        self.assertTrue(c["N"]["pass"])
        self.assertAlmostEqual(c["R"]["mean_drop"], 0.05)
        self.assertTrue(c["R"]["pass"])                              # ≥ 3 × |0|
        self.assertFalse(c["R"]["pass_alt"])                         # < 3 × 0.05 × 10 = 1.5: the other reading, printed
        self.assertTrue(c["K"]["pass_i"])
        self.assertFalse(c["K"]["pass_ii"])                          # L_K 10 > the learnable rooms' ≈ 9.5
        self.assertFalse(c["U"]["kept"])                             # 10 < 2 × ≈ 9.6


if __name__ == "__main__":
    unittest.main()
