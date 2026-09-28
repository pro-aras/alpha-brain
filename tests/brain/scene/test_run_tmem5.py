# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:16 +0400 — PREREG-TMEM5 (genome-wt-brain3 ce41448, sha 30121082…, final) with its AMENDMENT 1
# (brain-design-3 95b6e48, sha ab9a5fca…, final: the builder's 13 readings ruled, the null's VOID clause re-set on the bar's own
# window, NULL-CTX + REPLAY added, the null's four gains printed): the runner of T-MEM-5.
#   - the shas (a planted foreign one REFUSES); the arms and their learners; the per-block derangement of the context null;
#   - the MEMORY marks: N's fraction over blocks 21–200 (numerator, denominator and their n; a denominator ≤ 0 reads None),
#     g_N over the last 10 N-blocks with its sd (ddof 1), ḡ_R over each learnable room's own last 10 blocks;
#   - the split graders' order: MEMORY (NOT GRADABLE BY NAME → VOID iff the null meets the fraction clause at ≥ 2 seeds →
#     NOT GRADABLE BY NOISE / BY DENOMINATOR → FAIL → PASS) and CURIOSITY (BY NAME, a missing null included → FOR CHOICE →
#     VOID → FAIL → CEILING-BOUND → PASS), with S1c-2's «0.80 × O» a reading and never a bar;
#   - the toy: B's words independent of its things (A's parent true), exactly 50 B-blocks of 200;
#   - the finite-difference pin on a one-thing scene, and a planted doubled factor CAUGHT;
#   - A read at ḡ: the map scaled, the learner untouched;
#   - A-READ+WHERE's cells: a room whose words are independent of its things is excluded, the consistent rooms kept;
#   - on a synthetic room world with the REAL fixed test set: the FROZEN arms ARE S1c's life field for field; a context life
#     moves only the chosen label's gain; a replayed scene trains under ITS OWN act; the shuffled arm trains under σ_b(room)
#     and reads window k with label k; the ORACLE's clone carries g and c; the identity-credit null IS its estimate's picker.
# Test-first: red on scene-tmem5's base 2609670 (brain.scene.run_tmem5 does not exist there).
from __future__ import annotations

import copy
import unittest
from unittest import mock

import numpy as np

from brain.scene import context as CX
from brain.scene import learners as Lr
from brain.scene import pickers as PK
from brain.scene import rooms as RM
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from brain.scene import run_tmem5 as T5
from tests.brain.scene.test_run_s1c import HAVE_TEST_SET, FakeRooms

LAW = ("R1", "R2", "R3", "N")


class TestLaw(unittest.TestCase):
    def test_the_shas_and_a_planted_foreign_one(self) -> None:
        got = T5.check_prereg()
        self.assertEqual(got["prereg_tmem5"], "301210825f6809a9d40b706aa03b19b31b44c44c21667d2cd0420e2765e6d1ab")
        self.assertEqual(got["amend1_tmem5"], "ab9a5fca939c258f940b2191529404f12fb80f06d8b9fdbf37fd5b468ea36d00")
        self.assertEqual(got["prereg_s1c2"], S2.PREREG_S1C2_SHA256)
        with mock.patch.object(T5, "AMEND1_TMEM5_SHA256", "0" * 64):
            with self.assertRaises(T5.Tmem5Error):
                T5.check_prereg()
        with mock.patch.object(T5, "PREREG_TMEM5_SHA256", "f" * 64):
            with self.assertRaises(T5.Tmem5Error):
                T5.check_prereg()

    def test_the_arms_and_the_constants(self) -> None:
        self.assertEqual(set(T5.ARMS), {
            "PROGRESS-CTX", "PROGRESS-CTX+REPLAY", "RANDOM-CTX", "RANDOM-CTX+REPLAY", "ORACLE-CTX", "ORACLE-CTX+REPLAY",
            "NULL-CTX", "NULL-CTX+REPLAY", "SHUFFLED-CTX", "SHUFFLED-CTX-RANDOM", "BIAS-ONLY-RANDOM", "BIAS-ONLY-PROGRESS",
            "FROZEN-PROGRESS", "FROZEN-RANDOM"})
        self.assertEqual(T5.ARM_SPEC["SHUFFLED-CTX"], ("PROGRESS", None, "ctx", True))
        self.assertEqual(T5.ARM_SPEC["SHUFFLED-CTX-RANDOM"], ("RANDOM", None, "ctx", True))
        self.assertEqual(T5.ARM_SPEC["NULL-CTX+REPLAY"], ("NULL", "room", "ctx", False))
        self.assertEqual(T5.ARM_SPEC["BIAS-ONLY-RANDOM"], ("RANDOM", None, "bias", False))
        self.assertEqual(T5.ARM_SPEC["FROZEN-PROGRESS"], ("PROGRESS", None, "frozen", False))
        self.assertEqual(T5.LEARNER_KINDS, {"ctx": (True, True), "bias": (False, True), "gain": (True, False),
                                            "frozen": (False, False)})
        self.assertEqual(T5.CURIOSITY["PROGRESS-CTX"], ("ctx", "ORACLE-CTX", "RANDOM-CTX", "NULL-CTX"))
        self.assertEqual(T5.CURIOSITY["PROGRESS-CTX+REPLAY"],
                         ("ctx-replay", "ORACLE-CTX+REPLAY", "RANDOM-CTX+REPLAY", "NULL-CTX+REPLAY"))
        self.assertEqual(T5.BAND_LEARNERS, {"ctx": "RANDOM-CTX", "ctx-replay": "RANDOM-CTX+REPLAY"})
        self.assertEqual((T5.R_REPLAY, T5.MEMORY_AFTER, T5.G_LAST, T5.BAR_N_FRACTION, T5.BAR_G_RATIO, T5.REFUTE_G),
                         (10, 20, 10, 0.3, 0.1, 0.3))
        self.assertEqual((T5.TOY_BLOCKS, T5.TOY_B_BLOCKS, T5.TOY_GB_BAR, T5.TOY_GA_BAR, T5.TOY_SEEDS), (200, 50, 0.1, 0.8, (0, 1, 2)))
        self.assertEqual((CX.LR_G, T5.FD_TOL), (0.001, 1e-6))
        self.assertEqual(T5.ROOMS, LAW)
        self.assertEqual(T5.WHERE_ARMS, ("RANDOM-CTX", "PROGRESS-CTX"))

    def test_the_learners(self) -> None:
        for kind, (gain, bias) in T5.LEARNER_KINDS.items():
            L = T5.new_ctx_learner(kind)
            self.assertIsInstance(L, CX.CtxLearner)
            self.assertEqual((L.learn_gain, L.learn_bias, L.lr, L.lr_g, L.oracle, L.rooms), (gain, bias, 0.01, 0.001, False, list(LAW)))


class TestShuffle(unittest.TestCase):
    def test_a_derangement_per_block_from_its_own_stream(self) -> None:
        seen = set()
        for b in range(1, 301):
            sg = T5.shuffle_sigma(20261301, b, LAW)
            self.assertTrue(PK.is_derangement(sg))
            self.assertEqual(sg, T5.shuffle_sigma(20261301, b, LAW))
            seen.add(tuple(sg[r] for r in LAW))
        self.assertEqual(len(seen), 9)                                   # the nine derangements of four rooms all occur
        self.assertTrue(any(T5.shuffle_sigma(20261301, b, LAW) != T5.shuffle_sigma(20261302, b, LAW) for b in range(1, 20)))


def _rec(rooms_drops):
    return [{"block": b, "room": r, "drop": d} for b, (r, d) in enumerate(rooms_drops, start=1)]


class TestMemoryMarks(unittest.TestCase):
    def test_n_fraction_reads_blocks_21_to_200(self) -> None:
        seq = [("N", 9.0)] * 20 + [("N", 0.1), ("R1", 1.0), ("N", 0.3), ("R2", 0.6), ("R3", 0.2), ("N", 0.2)]
        nf = T5.n_fraction(_rec(seq))
        self.assertAlmostEqual(nf["num"], 0.2)
        self.assertAlmostEqual(nf["den"], 0.6)
        self.assertEqual((nf["n_N"], nf["n_R"]), (3, 3))
        self.assertAlmostEqual(nf["fraction"], 0.2 / 0.6)
        bad = T5.n_fraction(_rec([("R1", 0.0)] * 21 + [("R1", -0.1), ("N", 0.1)]))
        self.assertIsNone(bad["fraction"])                                # a denominator ≤ 0 → NOT GRADABLE

    def test_the_gain_reading(self) -> None:
        rooms = ["R1", "R2", "R3", "N"] * 15
        rec = [{"block": b, "room": r, "drop": 0.0} for b, r in enumerate(rooms, start=1)]
        ctx, g = [], {r: 1.0 for r in LAW}
        for x in rec:
            g = dict(g)
            g[x["room"]] = {"N": 1.0 / x["block"], "R1": 1.2, "R2": 1.0, "R3": 0.8}[x["room"]]
            ctx.append({"block": x["block"], "label": x["room"], "g": g})
        gr = T5.gain_reading({"record": rec, "ctx_record": ctx, "rooms": list(LAW)})
        last_n = [1.0 / b for b in range(4, 61, 4)][-10:]
        self.assertAlmostEqual(gr["g_N"], float(np.mean(last_n)))
        self.assertAlmostEqual(gr["g_N_sd"], float(np.std(last_n, ddof=1)))
        self.assertEqual(gr["g_N_n"], 10)
        self.assertAlmostEqual(gr["g_R"], 1.0)
        self.assertAlmostEqual(gr["g_R_at_end"], 1.0)
        self.assertEqual(gr["g_end"], ctx[-1]["g"])
        self.assertEqual([b for b, _v in gr["trajectory"]["N"]], list(range(4, 61, 4)))


def _m5(frac, gN, sd, gR, den=1.0):
    return {"n_fraction": {"fraction": frac, "num": None if frac is None else frac * den, "den": den, "n_N": 45, "n_R": 135},
            "g_N": gN, "g_N_sd": sd, "g_N_n": 10, "g_R": gR, "g_R_at_end": gR, "g_end": {"R1": gR, "R2": gR, "R3": gR, "N": gN},
            "trajectory": {"N": []}}


class TestMemoryVerdict(unittest.TestCase):
    SEEDS = (1, 2, 3)

    def _ps(self, over=None):
        ps = {s: {"X": _m5(0.1, 0.02, 0.005, 1.0), "NULL": _m5(0.7, 0.9, 0.01, 1.0), "blind": 0.7} for s in self.SEEDS}
        for (s, k), v in (over or {}).items():
            ps[s][k] = v
        return ps

    def test_the_order(self) -> None:
        self.assertEqual(T5.memory_verdict(self._ps())["verdict"], "PASS")
        self.assertEqual(T5.memory_verdict(self._ps({(2, "X"): _m5(0.35, 0.02, 0.005, 1.0)}))["verdict"], "FAIL")
        self.assertEqual(T5.memory_verdict(self._ps({(2, "X"): _m5(0.1, 0.2, 0.005, 1.0)}))["verdict"], "FAIL")
        one = self._ps({(1, "NULL"): _m5(0.2, 0.9, 0.01, 1.0)})
        self.assertEqual(T5.memory_verdict(one)["verdict"], "PASS")                   # the null meets at ONE seed: not VOID
        two = self._ps({(1, "NULL"): _m5(0.2, 0.9, 0.01, 1.0), (3, "NULL"): _m5(0.29, 0.9, 0.01, 1.0)})
        self.assertEqual(T5.memory_verdict(two)["verdict"], "VOID")                   # ≥ 2 seeds: VOID, whatever X reads
        noisy = self._ps({(3, "X"): _m5(0.1, 0.02, 0.2, 1.0)})
        self.assertEqual(T5.memory_verdict(noisy)["verdict"], "NOT GRADABLE BY NOISE")
        self.assertEqual(T5.memory_verdict({**two, 3: {**two[3], "X": _m5(0.1, 0.02, 0.2, 1.0)}})["verdict"], "VOID")
        den = self._ps({(2, "X"): _m5(None, 0.02, 0.005, 1.0, den=-0.1)})
        self.assertEqual(T5.memory_verdict(den)["verdict"], "NOT GRADABLE BY DENOMINATOR")
        missing = self._ps({(2, "NULL"): None})
        self.assertEqual(T5.memory_verdict(missing)["verdict"], "NOT GRADABLE BY NAME")
        v = T5.memory_verdict(self._ps())
        self.assertAlmostEqual(v["seeds"][1]["null_minus_blind"], 0.0)
        self.assertEqual(v["seeds"][1]["null_g_end"], {"R1": 1.0, "R2": 1.0, "R3": 1.0, "N": 0.9})


def _cm(A, shareN=0.05, leaveN=20):
    return {"A": A, "share": {"R1": 0.3, "R2": 0.3, "R3": 0.3, "N": shareN}, "leave": {"N": leaveN}}


class TestCuriosityVerdict(unittest.TestCase):
    def _ps(self, over=None):
        band = list(np.linspace(0.60, 0.70, 20))
        ps = {s: {"X": _cm(0.75), "O": _cm(0.80), "RND": _cm(0.65), "NUL": _cm(0.64, 0.25), "band_A": band, "band_n": 20}
              for s in (1, 2, 3)}
        for (s, k), v in (over or {}).items():
            ps[s][k] = v
        return ps

    def test_the_order_and_its_own_null(self) -> None:
        self.assertEqual(T5.curiosity_verdict(self._ps())["verdict"], "PASS")
        low = T5.curiosity_verdict(self._ps({(1, "X"): _cm(0.62)}))                 # inside the band
        self.assertEqual(low["verdict"], "FAIL")
        reading = T5.curiosity_verdict(self._ps({(1, "O"): _cm(0.99)}))               # X < 0.80 × O: a READING only
        self.assertEqual(reading["verdict"], "PASS")
        self.assertFalse(reading["seeds"][1]["reading_080"]["meets"])
        self.assertEqual(T5.curiosity_verdict(self._ps({(2, "NUL"): None}))["verdict"], "NOT GRADABLE BY NAME")
        self.assertEqual(T5.curiosity_verdict(self._ps({(2, "band_n"): 19}))["verdict"], "NOT GRADABLE BY NAME")
        self.assertEqual(T5.curiosity_verdict(self._ps({(2, "O"): _cm(0.69)}))["verdict"], "NOT GRADABLE FOR CHOICE")
        void = self._ps({(1, "NUL"): _cm(0.72, 0.05), (2, "NUL"): _cm(0.73, 0.02)})
        self.assertEqual(T5.curiosity_verdict(void)["verdict"], "VOID")
        ceil = T5.curiosity_verdict(self._ps({(3, "O"): _cm(0.69), (3, "RND"): _cm(0.60)}))   # O under the edge 0.6975
        self.assertEqual(ceil["verdict"], "CEILING-BOUND")
        self.assertEqual(T5.curiosity_verdict(self._ps({(3, "X"): _cm(0.75, 0.2)}))["verdict"], "FAIL")   # SHARE_N
        self.assertEqual(T5.curiosity_verdict(self._ps({(3, "X"): _cm(0.75, 0.05, 51)}))["verdict"], "FAIL")


class TestToy(unittest.TestCase):
    def test_bs_words_are_independent_of_its_things_and_as_parent_is_true(self) -> None:
        w = T5.ToyWorld(0)
        rng = np.random.default_rng(5)
        said_p, n_p, said_a, n_a, miss_a = 0, 0, 0, 0, 0
        for _ in range(4000):
            X, words, attrs = w.scene("B", rng)
            self.assertEqual(X.shape, (len(attrs), Lr.RW_DIM))
            present = {a for t in attrs for a in t}
            if "red" in present:
                n_p += 1
                said_p += int("red" in words)
            else:
                n_a += 1
                said_a += int("red" in words)
            Xa, wa, aa = w.scene("A", rng)
            miss_a += sum(1 for x in wa if x not in {a for t in aa for a in t})
        self.assertEqual(miss_a, 0)                                          # A: every word names a thing in view
        self.assertGreater(min(n_p, n_a), 500)
        self.assertAlmostEqual(said_p / n_p, said_a / n_a, delta=0.03)      # B: «red» said as often with or without red
        self.assertAlmostEqual((said_p + said_a) / (n_p + n_a), 0.5 * 0.2, delta=0.02)   # T2/T4 carry a colour; 1 of 5

    def test_the_schedule_is_fifty_b_blocks_of_two_hundred(self) -> None:
        for s in T5.TOY_SEEDS:
            order = T5.toy_order(s)
            self.assertEqual(len(order), 200)
            self.assertEqual(order.count("B"), 50)
            self.assertEqual(order, T5.toy_order(s))
        self.assertNotEqual(T5.toy_order(0), T5.toy_order(1))


def _stream(n=80, seed=3):
    rng = np.random.default_rng(seed)
    words = ("big", "small", "red", "blue", "circle", "square")
    out = []
    for i in range(n):
        h = 1 + int(rng.integers(3))
        X = rng.normal(size=(h, Lr.RW_DIM)) + (i % 4)
        ws = [words[int(k)] for k in rng.choice(len(words), size=1 + int(rng.integers(2)), replace=False)]
        out.append((LAW[i % 4], X, ws))
    return out


class TestFdPinAndScale(unittest.TestCase):
    def test_the_fd_pin_passes_and_a_doubled_factor_is_caught(self) -> None:
        L = CX.CtxLearner(LAW, lr=0.05, lr_g=0.01)
        for i, (room, X, w) in enumerate(_stream()):
            L.set_context(room)
            L.train_scene(X, w, rng=np.random.default_rng(i))
        raw = np.random.default_rng(8).normal(size=(1, Lr.RW_DIM)) + 1.0
        for g in (None, 0.5):
            LL = copy.deepcopy(L)
            if g is not None:
                LL.g["R2"] = g
            pin = T5.fd_pin(LL, raw, ["red", "circle"], "R2")
            self.assertTrue(pin["pass"], pin)
            self.assertLess(max(pin["max_err"].values()), T5.FD_TOL)
            if g is not None:
                self.assertTrue(pin["planted_doubled_caught"])
        with self.assertRaises(T5.Tmem5Error):
            T5.fd_pin(L, np.zeros((2, Lr.RW_DIM)), ["red"], "R2")          # one thing only: the delta rule IS the gradient there

    def test_a_read_at_g_scales_the_map_and_leaves_the_learner(self) -> None:
        L = CX.CtxLearner(LAW)
        for i, (room, X, w) in enumerate(_stream(120, 4)):
            L.set_context(room)
            L.train_scene(X, w, rng=np.random.default_rng(i))
        V0 = L.V.copy()
        Z = L.stats.standardise(np.random.default_rng(1).normal(size=(5, Lr.RW_DIM)))
        Lg = T5.scaled(L, 0.5)
        mature = np.flatnonzero(L.meetings >= Lr.P_FROM_MEETING)
        self.assertTrue(len(mature))
        got = Lg.logp_answer(Z)[:, mature]
        want = Lr.log_sigmoid(0.5 * (Z @ L.V.T) + L.b[None, :])[:, mature]
        self.assertTrue(np.allclose(got, want, rtol=0, atol=1e-12))
        self.assertTrue(np.array_equal(L.V, V0))
        self.assertTrue(np.array_equal(T5.scaled(L, 1.0).logp_answer(Z), L.logp_answer(Z)))


class TestWhereCells(unittest.TestCase):
    def test_a_room_whose_words_are_independent_is_excluded(self) -> None:
        rng = np.random.default_rng(0)
        L = CX.CtxLearner(LAW)
        types = [("big", "small"), ("red", "blue"), ("circle", "square")]

        def thing(k):
            base = np.zeros(Lr.RW_DIM)
            base[0], base[1], base[2] = (3.0 if k & 1 else -3.0), (3.0 if k & 2 else -3.0), (3.0 if k & 4 else -3.0)
            return base + rng.normal(size=Lr.RW_DIM) * 0.5

        def said(k):
            return [("small", "big")[k & 1], ("blue", "red")[(k >> 1) & 1], ("square", "circle")[(k >> 2) & 1]]

        for i in range(800):
            room = LAW[i % 4]
            k = int(rng.integers(8))
            X = thing(k)[None, :]
            words = said(int(rng.integers(8))) if room == "N" else said(k)
            L.set_context(room)
            L.train_scene(X, words, rng=np.random.default_rng(i))
        cells = T5.where_cells(L, types, 0.3)
        for w in ("big", "small", "red", "blue", "circle", "square"):
            self.assertIn((w, "R1"), cells["kept"])
            self.assertNotIn((w, "N"), cells["kept"])
            self.assertGreater(cells["excluded_N"][w], 0)
        kept_rooms = {cells["row_room"][i] for i in cells["kept_rows"]}
        self.assertEqual(kept_rooms, {"R1", "R2", "R3"})


@unittest.skipUnless(HAVE_TEST_SET, "S1b-1's caches of the fixed test set are not on this box")
class TestLife5(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test = S.FixedTestSet()
        cls.data = FakeRooms(rooms=LAW)

    def test_the_frozen_arms_are_s1cs_life(self) -> None:
        for arm, p in (("FROZEN-PROGRESS", "PROGRESS"), ("FROZEN-RANDOM", "RANDOM")):
            old = S.life(self.data, self.test, p, LAW, n_blocks=40)
            new = T5.life5(self.data, self.test, arm, LAW, n_blocks=40)
            self.assertEqual(S2.identity_diff(new, old), [], arm)
        old = S.life(self.data, self.test, "RANDOM", LAW, n_blocks=25, prefix=PK.band_prefix(self.data.seed, 3))
        new = T5.life5(self.data, self.test, "FROZEN-RANDOM", LAW, n_blocks=25, prefix=PK.band_prefix(self.data.seed, 3))
        self.assertEqual(S2.identity_diff(new, old), [])
        ctx = T5.life5(self.data, self.test, "RANDOM-CTX", LAW, n_blocks=25)
        self.assertNotEqual(S2.identity_diff(ctx, old), [])                   # the context learner is another learner

    def test_a_context_life_moves_only_the_chosen_labels_gain(self) -> None:
        r = T5.life5(self.data, self.test, "RANDOM-CTX", LAW, n_blocks=30)
        self.assertEqual(len(r["ctx_record"]), 30)
        prev = r["ctx0"]["g"]
        moved = set()
        for x, c in zip(r["record"], r["ctx_record"]):
            self.assertEqual(c["label"], x["room"])
            for q in LAW:
                if q != x["room"]:
                    self.assertEqual(c["g"][q], prev[q])
                elif c["g"][q] != prev[q]:
                    moved.add(q)
            prev = c["g"]
        self.assertEqual(moved, set(LAW))
        self.assertIn("marks5", r)
        self.assertEqual(r["marks5"]["g_end"], r["ctx_record"][-1]["g"])

    def _spy(self, arm, n):
        calls = []
        orig = CX.CtxLearner.train_scene

        def spy(obj, raw, words, *a, **k):
            calls.append(obj.ctx)
            return orig(obj, raw, words, *a, **k)

        with mock.patch.object(CX.CtxLearner, "train_scene", spy):
            r = T5.life5(self.data, self.test, arm, LAW, n_blocks=n, keep_learner=True)
        return r, calls

    def test_a_replayed_scene_trains_under_its_own_act(self) -> None:
        r, calls = self._spy("RANDOM-CTX+REPLAY", 12)
        want = []
        for x in r["record"]:
            want += [x["room"]] * PK.BLOCK
            want += [q for q, _i in x["replay"]]
        self.assertEqual(calls, want)
        self.assertTrue(any(q != x["room"] for x in r["record"] for q, _i in x["replay"]))

    def test_the_shuffled_arm_trains_under_sigma_and_reads_window_k_with_label_k(self) -> None:
        r, calls = self._spy("SHUFFLED-CTX-RANDOM", 12)
        want = []
        for x, c in zip(r["record"], r["ctx_record"]):
            sg = T5.shuffle_sigma(self.data.seed, x["block"], LAW)
            self.assertEqual(c["sigma"], sg)
            self.assertEqual(c["label"], sg[x["room"]])
            self.assertNotEqual(c["label"], x["room"])
            want += [sg[x["room"]]] * PK.BLOCK
        self.assertEqual(calls, want)
        L = r["_learner"]
        self.assertEqual(T5.window_losses(L, self.data, LAW), r["record"][-1]["L"])
        wrong = {k: CX.ctx_window_loss(L, self.data.window[k], r["ctx_record"][-1]["sigma"][k]) for k in LAW}
        self.assertNotEqual(wrong, r["record"][-1]["L"])

    def test_the_oracles_clone_carries_g_and_c(self) -> None:
        r = T5.life5(self.data, self.test, "ORACLE-CTX", LAW, n_blocks=8)
        self.assertTrue(all(x["clone_identical"] for x in r["record"] if x["flag"] == "policy"))
        a = T5.new_ctx_learner("ctx")
        for i, (room, X, w) in enumerate(_stream(20, 2)):
            a.set_context(room)
            a.train_scene(X, w, rng=np.random.default_rng(i))
        b = copy.deepcopy(a)
        self.assertTrue(T5.same_state5(a, b))
        b.g["N"] += 1e-12
        self.assertFalse(T5.same_state5(a, b))
        b = copy.deepcopy(a)
        b.c["R3"][0] += 1e-12
        self.assertFalse(T5.same_state5(a, b))

    def test_the_identity_credit_null_is_its_estimates_picker(self) -> None:
        a = T5.life5(self.data, self.test, "NULL-CTX", LAW, n_blocks=20, identity_credit=True)
        b = T5.life5(self.data, self.test, "PROGRESS-CTX", LAW, n_blocks=20)
        self.assertTrue(S2.rows_equal(a, b))
        n = T5.life5(self.data, self.test, "NULL-CTX", LAW, n_blocks=20)
        self.assertEqual(n["pi"], PK.null_derangement(self.data.seed, LAW))
        self.assertFalse(any(x["credited"] == x["room"] for x in n["record"]))


if __name__ == "__main__":
    unittest.main()
