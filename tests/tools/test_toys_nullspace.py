"""Tests for TOY B (null-space protection): the projectors' mathematics, the arms' hooks, the pre-pass, the life's identity with T-MEM-1's BASE record, the
byte-identities the law pins (P = I is PLAIN; every arm is PLAIN through room 1).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:42 +0400 — written FIRST (red before tools/toys/nullspace/{projector,life}.py exist); law:
# docs/research/toys/PREREG-TOY-NULLSPACE.md (text co-signed 2026-10-03 11:24 +0400, sha256 d15a6353…), §1 (the arms), §4 (G2 identity, G3 the gate toy and the
# identities with PLANTS, G4 the pre-pass).

  Math      the all-rows closed form equals the RLS recursion over SINGLE rows; the Methods recursion over batch MEANS is a different (looser) projector; P is symmetric with
            eigenvalues in [0, 1]; NSCL's projector is idempotent with the rank the threshold names; ROT keeps the spectrum and moves the eigenvectors; RAND-RANK keeps the rank;
            ANTI lies inside the span; the gate toy: old outputs unchanged to 1e-9 under OWM (alpha -> 0), moved by > 0.1 by the plain step.
  Hooks     OWM leaves room 1 alone and right-multiplies [dV | db] by P afterwards and records its realised ratio; OWM-NB leaves the bias free; OLDONLY projects only the units
            that existed when the room began; FREEZE zeroes all rows (STD-ONLY) or only the old units' (FREEZE-OLD); SHRINK applies the parent's scalar.
  Pre-pass  the rows the pre-pass produces equal the rows a learner receives, to 1e-12, on a full life; its capacity equals the spectrum tool's.
  Life      (the redrawn pools of seed 20261301) PLAIN reproduces T-MEM-1's BASE/seq record; P = I and rho = 1 reproduce PLAIN byte for byte; every arm equals PLAIN through block 50.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from brain.scene import run_tmem1 as T1

from tools.toys.common import pools as POOLS
from tools.toys.nullspace import life as NL
from tools.toys.nullspace import projector as NP
from tools.toys.nullspace import spectrum as SP

SEED = 20261301
POOL_OK = all(POOLS.present(POOLS.ROOT, SEED).values())
TMEM1_OK = (Path("/data/dev/brain-runs/scene-tmem1") / str(SEED) / "runs" / "seq" / "BASE.json").exists()
ROOMS = list(S.WORLDS["law"])
_CACHE = {}


def real():
    if "data" not in _CACHE:
        _CACHE["data"] = S.RoomData(POOLS.ROOT, SEED, ROOMS)
        _CACHE["test"] = T1.TestSetM()
        _CACHE["proj"] = NP.Projectors(_CACHE["data"], SEED)
    return _CACHE["data"], _CACHE["test"], _CACHE["proj"]


class FakeL:
    def __init__(self, scenes=1, words=("a", "b", "c", "d")):
        self.scenes = scenes
        self.words = list(words)
        self.index = {w: i for i, w in enumerate(words)}


def rows(n=40, d=8, seed=0, rank=None):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    if rank is not None:
        X[:, rank:] = 0.0
    return X


# ====================================================================================================== MATH
class TestProjectorMath(unittest.TestCase):
    def test_all_rows_closed_form_equals_the_recursion_over_single_rows(self):
        X = rows()
        alpha = 0.7
        closed = NP.owm_projector(NP.gram(X), alpha)
        rec = NP.rls_rows(X, alpha)
        self.assertLess(np.max(np.abs(closed - rec)), 1e-9)
        d = X.shape[1]
        direct = np.eye(d) - X.T @ np.linalg.solve(X @ X.T + alpha * np.eye(X.shape[0]), X)        # the paper's I - A (A'A + alpha I)^-1 A', A = X'
        self.assertLess(np.max(np.abs(closed - direct)), 1e-9)

    def test_the_batch_mean_recursion_is_its_own_closed_form_and_a_different_projector(self):
        X = rows(n=40)
        means = X.reshape(8, 5, -1).mean(axis=1)                       # eight batches of five rows
        alpha = 0.7
        bm = NP.rls_batches(means, alpha)
        self.assertLess(np.max(np.abs(bm - NP.owm_projector(NP.gram(means), alpha))), 1e-9)
        allrows = NP.owm_projector(NP.gram(X), alpha)
        self.assertGreater(np.max(np.abs(bm - allrows)), 1e-3)           # the plant: the two forms are NOT the same projector
        self.assertGreater(np.trace(bm), np.trace(allrows))              # fewer constraints: more of the space left free

    def test_P_is_symmetric_with_eigenvalues_in_the_unit_interval(self):
        P = NP.owm_projector(NP.gram(rows()), 0.3)
        self.assertLess(np.max(np.abs(P - P.T)), 1e-12)
        ev = np.linalg.eigvalsh(P)
        self.assertGreaterEqual(ev.min(), -1e-12)
        self.assertLessEqual(ev.max(), 1 + 1e-12)

    def test_nscl_projector_is_idempotent_and_has_the_rank_the_threshold_names(self):
        X = rows(n=60, d=10, seed=2)
        X[:, 7:] *= 1e-3                                                # three nearly-null directions
        G = NP.gram(X)
        P, d = NP.nscl_projector(G, X.shape[0], 1e-3)
        self.assertLess(np.max(np.abs(P @ P - P)), 1e-12)
        ev = np.linalg.eigvalsh(G / X.shape[0])
        self.assertEqual(d, int((ev <= 1e-3 * ev.max()).sum()))
        self.assertEqual(int(round(np.trace(P))), d)
        self.assertEqual(d, 3)

    def test_rot_keeps_the_spectrum_and_moves_the_eigenvectors(self):
        P = NP.owm_projector(NP.gram(rows(d=10)), 0.3)
        Q = NP.haar(7, "ns:rot:1", 10)
        self.assertLess(np.max(np.abs(Q @ Q.T - np.eye(10))), 1e-12)
        R = NP.rotate(P, Q)
        self.assertLess(np.max(np.abs(np.linalg.eigvalsh(R) - np.linalg.eigvalsh(P))), 1e-9)
        self.assertGreater(np.max(np.abs(R - P)), 1e-3)                  # the plant changed the bytes
        self.assertLess(np.max(np.abs(R - R.T)), 1e-12)

    def test_haar_is_deterministic_and_differs_between_streams(self):
        self.assertTrue(np.array_equal(NP.haar(7, "ns:rot:1", 6), NP.haar(7, "ns:rot:1", 6)))
        self.assertFalse(np.array_equal(NP.haar(7, "ns:rot:1", 6), NP.haar(7, "ns:rot:2", 6)))

    def test_rand_rank_has_the_rank_asked(self):
        Q = NP.haar(3, "ns:rank:1", 10)
        P = NP.random_subspace(Q, 4)
        self.assertEqual(int(round(np.trace(P))), 4)
        self.assertLess(np.max(np.abs(P @ P - P)), 1e-12)

    def test_anti_lies_inside_the_span_and_moves_old_outputs(self):
        X = rows(n=30, d=8, seed=4)
        P = NP.owm_projector(NP.gram(X), 1e-6)
        A = NP.anti(P)
        self.assertLess(np.max(np.abs(P + A - np.eye(8))), 1e-12)
        u = np.random.default_rng(1).standard_normal((5, 8))
        old_plain = np.abs(u @ X.T).max()
        old_owm = np.abs((u @ P) @ X.T).max()
        old_anti = np.abs((u @ A) @ X.T).max()
        self.assertLess(old_owm, 1e-5)                                  # OWM: the old rows' outputs do not move
        self.assertGreater(old_plain, 0.1)                              # PLAIN: they do
        self.assertGreater(old_anti, 0.9 * old_plain)                   # ANTI: they move as much (the plant that must LOSE)

    def test_the_gate_toy_old_outputs_unchanged_to_1e_9_under_owm(self):
        X_old = rows(n=50, d=6, seed=5, rank=4)                         # old inputs live in a 4-dim subspace of 6
        X_new = rows(n=20, d=6, seed=6)
        W = np.zeros((3, 6))
        P = NP.owm_projector(NP.gram(X_old), 1e-12 * np.linalg.eigvalsh(NP.gram(X_old)).max())
        out_before = X_old @ W.T
        for x in X_new:                                                 # a delta-rule-like stream: rank-1 updates along the new inputs
            err = np.array([1.0, -0.5, 0.25])
            W_plain = W + 0.1 * np.outer(err, x)
            W = W + 0.1 * np.outer(err, x) @ P
        self.assertLess(np.abs(X_old @ W.T - out_before).max(), 1e-9)
        plain = np.zeros((3, 6))
        for x in X_new:
            plain = plain + 0.1 * np.outer(np.array([1.0, -0.5, 0.25]), x)
        self.assertGreater(np.abs(X_old @ plain.T).max(), 0.1)          # the plain step moves them
        self.assertGreater(np.abs(W).max(), 0.0)                        # and OWM still LEARNED something in the null directions


# ====================================================================================================== HOOKS
class TestHooks(unittest.TestCase):
    def upd(self, w=4, d=8, seed=0):
        r = np.random.default_rng(seed)
        return r.standard_normal((w, d - 1)), r.standard_normal(w)

    def test_owm_arm_leaves_room_1_alone_and_projects_afterwards(self):
        P = NP.owm_projector(NP.gram(rows(d=8)), 0.5)
        arm = NP.OwmArm({2: P})
        L = FakeL(scenes=5)
        upd, db = self.upd()
        u0, d0 = upd.copy(), db.copy()
        arm.begin_block(1, 1, L)
        a, b = arm(L, upd.copy(), db.copy())
        self.assertTrue(np.array_equal(a, u0) and np.array_equal(b, d0))               # room 1: untouched
        arm.begin_block(51, 2, L)
        a, b = arm(L, upd.copy(), db.copy())
        want = np.hstack([u0, d0[:, None]]) @ P
        self.assertLess(np.abs(np.hstack([a, b[:, None]]) - want).max(), 1e-12)
        self.assertIn(L.scenes, arm.rho)
        U = np.hstack([u0, d0[:, None]])
        self.assertAlmostEqual(arm.rho[L.scenes], float(np.linalg.norm(U @ P) / np.linalg.norm(U)), places=12)

    def test_P_equal_identity_changes_nothing_byte_for_byte(self):
        arm = NP.OwmArm({2: np.eye(8)})
        L = FakeL(scenes=9)
        upd, db = self.upd(seed=3)
        arm.begin_block(51, 2, L)
        a, b = arm(L, upd.copy(), db.copy())
        self.assertTrue(np.array_equal(a, upd) and np.array_equal(b, db))
        self.assertAlmostEqual(arm.rho[9], 1.0, places=12)

    def test_nb_arm_leaves_the_bias_free(self):
        Pz = NP.owm_projector(NP.gram(rows(d=7)), 0.5)
        arm = NP.NbArm({2: Pz})
        L = FakeL()
        upd, db = self.upd()
        arm.begin_block(51, 2, L)
        a, b = arm(L, upd.copy(), db.copy())
        self.assertTrue(np.array_equal(b, db))
        self.assertLess(np.abs(a - upd @ Pz).max(), 1e-12)

    def test_oldonly_projects_only_the_units_that_existed_when_the_room_began(self):
        P = NP.owm_projector(NP.gram(rows(d=8)), 0.5)
        arm = NP.OldOnlyArm({2: P})
        L = FakeL(words=("a", "b"))                                     # two units exist when room 2 begins
        arm.begin_block(51, 2, L)
        L.words += ["c", "d"]                                           # two words born in the room
        upd, db = self.upd(w=4)
        a, b = arm(L, upd.copy(), db.copy())
        U = np.hstack([upd, db[:, None]])
        W = U @ P
        self.assertLess(np.abs(np.hstack([a, b[:, None]])[:2] - W[:2]).max(), 1e-12)   # old rows projected
        self.assertTrue(np.array_equal(a[2:], upd[2:]) and np.array_equal(b[2:], db[2:]))   # new rows plain
        arm.begin_block(52, 2, L)                                       # the room's start is remembered across its blocks
        a, b = arm(L, upd.copy(), db.copy())
        self.assertTrue(np.array_equal(a[2:], upd[2:]))

    def test_freeze_zeroes_every_row_after_its_room_and_freeze_old_only_the_old_ones(self):
        L = FakeL(words=("a", "b"))
        std = NP.FreezeArm(after_room=1, only_old=False)
        old = NP.FreezeArm(after_room=1, only_old=True)
        for arm in (std, old):
            arm.begin_block(50, 1, L)
            u, d = self.upd(w=2)
            a, b = arm(L, u.copy(), d.copy())
            self.assertTrue(np.array_equal(a, u) and np.array_equal(b, d))             # through its room: PLAIN
        for arm in (std, old):
            arm.begin_block(51, 2, L)                                   # room 2 begins: two words exist (the units of room 1)
        L.words += ["c", "d"]                                           # words born IN room 2: units 2, 3
        u, d = self.upd(w=4)
        a, b = std(L, u.copy(), d.copy())
        self.assertEqual(float(np.abs(a).max()), 0.0)
        self.assertEqual(float(np.abs(b).max()), 0.0)
        a, b = old(L, u.copy(), d.copy())
        self.assertEqual(float(np.abs(a[:2]).max()), 0.0)                # the units that existed at room 1's end: frozen... (2 words then)
        self.assertTrue(np.array_equal(a[2:], u[2:]) and np.array_equal(b[2:], d[2:]))  # the new ones learn plain

    def test_shrink_applies_the_parents_scalar_per_scene(self):
        arm = NP.ScaleArm({7: 0.25})
        L = FakeL(scenes=7)
        u, d = self.upd()
        arm.begin_block(1, 1, L)
        a, b = arm(L, u.copy(), d.copy())
        self.assertLess(np.abs(a - 0.25 * u).max(), 1e-15)
        L.scenes = 8                                                    # a scene the parent has no scalar for: 1
        a, b = arm(L, u.copy(), d.copy())
        self.assertTrue(np.array_equal(a, u))
        one = NP.ScaleArm({7: 1.0})
        L.scenes = 7
        a, b = one(L, u.copy(), d.copy())
        self.assertTrue(np.array_equal(a, u) and np.array_equal(b, d))                  # rho = 1 is PLAIN byte for byte


# ====================================================================================================== PRE-PASS
@unittest.skipUnless(POOL_OK, "the redrawn pools of seed 20261301 are absent")
class TestPrePass(unittest.TestCase):
    def test_the_rows_equal_the_rows_a_learner_receives(self):
        data, test, proj = real()
        L = S.new_learner()
        got = {r: [] for r in ROOMS}
        cursor = {r: 0 for r in ROOMS}
        for block in range(1, 201):
            room = ROOMS[(block - 1) // 50]
            for i in range(cursor[room], cursor[room] + 10):
                X, words = data.visit_scene(room, i)
                L.train_scene(X, words, referent=None, rng=NL.episodic_rng(SEED, room, i))
                Xa = np.atleast_2d(X)
                if Xa.shape[0]:
                    got[room].append(np.hstack([L.stats.standardise(Xa), np.ones((Xa.shape[0], 1))]))        # what the learner standardised the scene with, observed first
            cursor[room] += 10
        for r in ROOMS:
            self.assertLess(np.abs(np.vstack(got[r]) - proj.rows[r]).max(), 1e-12, r)

    def test_capacity_equals_the_spectrum_tools(self):
        data, test, proj = real()
        rows_ = SP.rows_as_seen(data)
        lam1 = float(np.linalg.eigvalsh(SP.gram(rows_["R1"]))[-1])
        cum = np.zeros((0, SP.DIM))
        for j, r in enumerate(ROOMS[:3], start=1):
            cum = np.vstack([cum, rows_[r]])
            evG = np.linalg.eigvalsh(SP.gram(cum))
            for tau in (0.1, 0.01, 0.001):
                self.assertAlmostEqual(proj.capacity(tau, j), SP.owm_capacity(evG, tau * lam1), places=6)

    def test_projectors_have_the_declared_shapes_and_properties(self):
        data, test, proj = real()
        owm = proj.owm(0.01)
        self.assertEqual(sorted(owm), [2, 3, 4])
        for P in owm.values():
            self.assertEqual(P.shape, (147, 147))
            ev = np.linalg.eigvalsh(P)
            self.assertGreaterEqual(ev.min(), -1e-9)
            self.assertLessEqual(ev.max(), 1 + 1e-9)
        nscl, dims = proj.nscl(0.01)
        self.assertEqual(sorted(dims), [1, 2, 3])
        for j, P in nscl.items():
            self.assertLess(np.abs(P @ P - P).max(), 1e-9)
            self.assertEqual(int(round(np.trace(P))), dims[j - 1])
        self.assertGreater(proj.alpha(0.1), proj.alpha(0.01))


# ====================================================================================================== LIFE
@unittest.skipUnless(POOL_OK and TMEM1_OK, "the redrawn pools or T-MEM-1's records are absent")
class TestLife(unittest.TestCase):
    def plain(self, n_blocks=200):
        data, test, proj = real()
        return NL.life_ns(data, test, NP.PlainArm(), "PLAIN", n_blocks=n_blocks)

    def test_plain_life_reproduces_tmem1_base(self):
        old = json.loads((Path("/data/dev/brain-runs/scene-tmem1") / str(SEED) / "runs" / "seq" / "BASE.json").read_text())
        new = self.plain()
        for k in ("rates_rw", "pairs", "table", "first_meet"):
            self.assertEqual(S2._canon(new[k]), S2._canon(old[k]), k)
        cols = ("block", "room", "flag", "start", "L", "drop", "wl")
        self.assertEqual(len(new["record"]), len(old["record"]))
        for x, y in zip(new["record"], old["record"]):
            self.assertEqual(S2._canon({c: x[c] for c in cols}), S2._canon({c: y[c] for c in cols}))

    def test_P_identity_and_rho_one_reproduce_plain_byte_for_byte(self):
        base = self.plain(60)
        data, test, proj = real()
        ident = NL.life_ns(data, test, NP.OwmArm({2: np.eye(NP.DIM), 3: np.eye(NP.DIM), 4: np.eye(NP.DIM)}), "OWM-I", n_blocks=60)
        one = NL.life_ns(data, test, NP.ScaleArm({}), "SHRINK-1", n_blocks=60)
        for other in (ident, one):
            self.assertEqual(S2._canon(other["rates_rw"]), S2._canon(base["rates_rw"]))
            self.assertEqual(S2._canon(other["table"]), S2._canon(base["table"]))

    def test_every_arm_equals_plain_through_block_50(self):
        base = self.plain(60)
        data, test, proj = real()
        arms = {"OWM": NP.OwmArm(proj.owm(0.01)), "NSCL": NP.OwmArm(proj.nscl(0.01)[0]), "ANTI": NP.OwmArm(NP.anti_all(proj.owm(0.01))),
                "ROT": NP.OwmArm(proj.rot(0.01, 1)), "STD-ONLY(1)": NP.FreezeArm(1, False)}
        for name, arm in arms.items():
            life = NL.life_ns(data, test, arm, name, n_blocks=60)
            self.assertEqual(S2._canon(life["rates_rw"][:51]), S2._canon(base["rates_rw"][:51]), name)
            self.assertNotEqual(S2._canon(life["rates_rw"]), S2._canon(base["rates_rw"]), f"{name}: the arm must differ from PLAIN after room 1 (a plant that changed nothing)")

    def test_a_projected_life_records_its_ratios_and_capacity(self):
        data, test, proj = real()
        life = NL.life_ns(data, test, NP.OwmArm(proj.owm(0.01)), "OWM(0.01)", n_blocks=60)
        rho = life["extra"]["rho"]
        self.assertTrue(rho and all(0.0 <= v <= 1.0 + 1e-9 for v in rho.values()))
        self.assertTrue(all(int(k) > 500 for k in rho))                                    # nothing recorded in room 1 (scenes 1-500)


if __name__ == "__main__":
    unittest.main()
