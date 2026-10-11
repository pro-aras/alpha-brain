# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 12:0x +0400 — G-UNIT of PREREG-N2-TRAJECTORY
# (docs/brain/trajectory/PREREG-N2-TRAJECTORY.md, signed 2026-10-10, n2-1010 @ ffd2901): the trajectory register's
# unit gates, written BEFORE the wiring (the law's §2 order). (a) flag OFF byte-identity of modulate() against the
# inline old formula over a real canvas stream, the registers never touched; (b) causality — the first call reads
# w = exp(kappa*0) = 1 exactly and tpe == spe (r0 = 0); (c) a scripted linear le-ramp (slope s planted) — r
# converges into [s/2, 2s] inside the declared window (2 x 5*tau = 200 ramp moments) and tpe < spe over the ramp's
# tail (the law's ramp arithmetic: the path removes one lag unit); (d) determinism to the last digit on the
# (w, r, tpe, spe) sequences; (e) the degenerate e == 0 stream (an alive cell's own vector fed back): never NaN,
# r decays toward 0, w inside the clip; (f) the Mind thread (trajectory= threaded to the predictor; default OFF);
# (g) the composition pin — precision + trajectory both ON: last_weight == clip(w_precision) * clip(w_trajectory)
# each clipped at its own register (§1.5), mirrored inline to the last digit.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome, retina, retina_dim
from genome.predict import (PRECISION_FLOOR, PRECISION_PRIOR, PRECISION_W_HI, PRECISION_W_LO,
                            TRAJECTORY_ETA_M, TRAJECTORY_ETA_R, TRAJECTORY_KAPPA, Predictor)

THINGS = ["circle", "square", "triangle"]

_TOY_GENES = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.85
BIRTH error misfires 3
BUDGET 2000 per arrival
NMAX 200
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 1000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""

RAMP_SLOPE = 0.01          # G-UNIT (c)'s planted slope, declared before any run (the law's §3 value)
RAMP_WINDOW = 200          # the declared convergence window: 2 x 5*tau, tau = 1/TRAJECTORY_ETA_M = 20


def _build_genome():
    return parse_genome(_TOY_GENES)


def _unit_vec(rng: np.random.Generator, dim: int) -> np.ndarray:
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def _proto_stream(rng: np.random.Generator, dim: int, n: int):
    """A fixed prototype vector with jitter (test_predict_precision.py's own form, self-contained here):
    the vector-level form of the canvas world's measured error floor."""
    proto = _unit_vec(rng, dim)
    out = []
    for _ in range(n):
        v = proto + 0.035 * rng.normal(size=dim)
        out.append(v / np.linalg.norm(v))
    return out


def _run_vectors(pred: Predictor, org: Organism, xs) -> list:
    """Drive moments in the mind's own order (error() BEFORE moment(), note_winners after); returns the
    (w, rate, tpe, spe) instrument reads collected after every error() call."""
    reads = []
    xw = world.encode_word("circle", True)
    for x in xs:
        pred.error(x)
        reads.append((pred.last_weight, pred.last_rate, pred.last_tpe, pred.last_spe))
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    return reads


class TestTrajectoryRegister(unittest.TestCase):
    def test_a_flag_off_byte_identical(self) -> None:
        """The regression pin (the N1 form): no trajectory argument — modulate() returns exactly the old
        formula's value over a real driven canvas stream, every moment, to the last float digit, and not
        one trajectory register read is ever touched."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org)                      # the old road: no trajectory argument
        xs = [retina(world.render(t, rng, side=24), g.retina) for t in THINGS * 10]
        seen = 0
        for x in xs:
            xw = world.encode_word("circle", True)
            e = pred.error(x)
            got = pred.modulate(0.1)
            want = 0.1 * float(np.clip(0.5 + 3.0 * e, 0.5, 2.0))
            self.assertEqual(got, want, "flag OFF must run the exact old arithmetic")
            self.assertIsNone(pred.last_weight, "flag OFF: the weight register is never touched")
            self.assertIsNone(pred.last_rate, "flag OFF: the rate register is never touched")
            self.assertIsNone(pred.last_tpe, "flag OFF: tpe is never journaled")
            self.assertIsNone(pred.last_spe, "flag OFF: spe is never journaled")
            seen += 1
            S, T = org.moment(x, xw)
            pred.note_winners(S)
        self.assertGreater(seen, 0, "presence: the stream actually drove moments")

    def test_b_first_call_causality(self) -> None:
        """G-UNIT (b): the first call reads w = exp(kappa*0) = 1 EXACTLY (the r0 = 0 prior, no delta
        fingerprint — the exp(0) form, not N1's v0 ratio), tpe == spe EXACTLY (p = m + 0), and the
        first moment's modulate is byte-identical to master's."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, trajectory=True)
        x = retina(world.render("circle", rng, side=24), g.retina)
        e = pred.error(x)
        self.assertEqual(pred.last_weight, 1.0, "w = exp(0) exactly at the first call")
        self.assertEqual(pred.last_rate, 0.0, "r0 = 0 exactly")
        self.assertEqual(pred.last_tpe, pred.last_spe, "r0 = 0: the path and the point read the same")
        self.assertEqual(pred.modulate(0.1), 0.1 * float(np.clip(0.5 + 3.0 * e, 0.5, 2.0)),
                         "the first moment is byte-identical even flag-on (w = 1 exactly)")

    def test_c_planted_ramp(self) -> None:
        """G-UNIT (c): a scripted linear le-ramp le_t = base + s*t through the register's own step —
        r converges into [s/2, 2s] inside the declared window (2 x 5*tau = 200 ramp moments), and over
        the ramp's tail tpe < spe paired per-moment (the law's arithmetic: |tpe| ~ (tau-1)*s against
        |spe| ~ tau*s — the path removes one lag unit while a trend persists)."""
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, trajectory=True)
        base = float(np.log(PRECISION_PRIOR))    # the ramp starts AT the prior: m reads the stream's level
        s = RAMP_SLOPE
        tail_tpe, tail_spe = [], []
        for t in range(RAMP_WINDOW + 100):       # 200 to convergence, then the 100-moment graded tail
            pred._trajectory_step(base + s * t)
            if t == RAMP_WINDOW - 1:
                self.assertGreaterEqual(pred._t_r, s / 2, "r settled to at least half the planted slope")
                self.assertLessEqual(pred._t_r, 2 * s, "r never overshot beyond twice the planted slope")
            if t >= RAMP_WINDOW:
                tail_tpe.append(pred.last_tpe)
                tail_spe.append(pred.last_spe)
        self.assertEqual(len(tail_tpe), 100, "presence: the tail is the declared 100 moments")
        self.assertLess(float(np.mean(np.abs(tail_tpe))), float(np.mean(np.abs(tail_spe))),
                        "the path beats the point over the ramp's tail")
        gap = float(np.mean(np.abs(tail_spe))) - float(np.mean(np.abs(tail_tpe)))
        self.assertGreaterEqual(gap, s / 2, "the one-lag-unit arithmetic: the margin is about one slope unit")
        self.assertLessEqual(gap, 2 * s, "the margin never exceeds the arithmetic's own bound")

    def test_d_determinism(self) -> None:
        """Two identical runs give identical (w, rate, tpe, spe) sequences to the last digit (pure float
        EMAs, no RNG inside the register)."""
        sequences = []
        for _ in range(2):
            rng = np.random.default_rng(33)
            g = _build_genome()
            org = Organism(g)
            pred = Predictor(org, trajectory=True)
            sequences.append(_run_vectors(pred, org, _proto_stream(rng, retina_dim(g.retina), 60)))
        self.assertGreater(len(sequences[0]), 0, "presence: the reads were collected")
        self.assertIsNotNone(sequences[0][-1][0], "the flag is actually on in this test")
        self.assertEqual(sequences[0], sequences[1])

    def test_e_degenerate_zero_stream_bounded(self) -> None:
        """Feeding an alive cell's OWN vector back gives e == 0 exactly, le = log(delta) constant: never
        NaN, r decays toward 0 (the motion dies once m sits on the stream), w always inside the clip."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, trajectory=True)
        _run_vectors(pred, org, _proto_stream(rng, retina_dim(g.retina), 20))
        alive = org.sight.alive_ids()
        self.assertGreater(len(alive), 0, "presence: the stable stream bore at least one sight cell")
        own = np.asarray(org.sight.cells[int(alive[0])], dtype=float)
        ws, rs = [], []
        for _ in range(200):
            pred.error(own)
            ws.append(pred.last_weight)
            rs.append(pred.last_rate)
        self.assertTrue(all(np.isfinite(ws)) and all(np.isfinite(rs)), "never NaN/inf")
        self.assertTrue(all(PRECISION_W_LO <= w <= PRECISION_W_HI for w in ws), "always inside the declared clip")
        self.assertLess(abs(rs[-1]), 0.02, "the rate dies on a constant stream (the motion is zero)")
        self.assertLess(abs(rs[-1]), abs(rs[10]), "the decay is monotone in the limit's own reading")

    def test_f_mind_thread(self) -> None:
        """Mind(..., trajectory=True) threads the flag to its predictor; the default stays OFF."""
        from creature.mind import Mind
        genome_path = Path(tempfile.mkdtemp()) / "toy.genome"
        genome_path.write_text(_TOY_GENES + "PREDICT next glance; error scales delta 0.5..2.0; ranks replay; grades act\n")
        m_off = Mind(genome_path, Path(tempfile.mkdtemp()))
        m_on = Mind(genome_path, Path(tempfile.mkdtemp()), trajectory=True)
        self.assertIsNotNone(m_off.predictor, "presence: the toy genome declares PREDICT, the predictor exists")
        self.assertFalse(m_off.predictor.trajectory)
        self.assertTrue(m_on.predictor.trajectory)

    def test_g_composition_with_precision(self) -> None:
        """§1.5's declared composition: precision ON + trajectory ON — last_weight is the PRODUCT of the
        two registers' own clipped weights, mirrored inline to the last float digit, and modulate() reads
        the weighted error e*w_total with the [lo, hi] clip unchanged."""
        rng = np.random.default_rng(77)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, precision=True, trajectory=True)
        m_l_fast = m_l_slow = float(np.log(PRECISION_PRIOR))
        m_t_m, m_t_r = float(np.log(PRECISION_PRIOR)), 0.0
        xs = _proto_stream(rng, retina_dim(g.retina), 120)
        xw = world.encode_word("circle", True)
        seen = 0
        for x in xs:
            e = pred.error(x)
            le = float(np.log(e * e + PRECISION_FLOOR))
            w_p = float(np.clip(np.exp(m_l_slow - m_l_fast), PRECISION_W_LO, PRECISION_W_HI))
            m_l_fast = (1.0 - 0.05) * m_l_fast + 0.05 * le
            m_l_slow = (1.0 - 0.005) * m_l_slow + 0.005 * le
            w_t = float(np.clip(np.exp(TRAJECTORY_KAPPA * m_t_r), PRECISION_W_LO, PRECISION_W_HI))
            m_new = (1.0 - TRAJECTORY_ETA_M) * m_t_m + TRAJECTORY_ETA_M * le
            d = m_new - m_t_m
            m_t_m = m_new
            m_t_r = (1.0 - TRAJECTORY_ETA_R) * m_t_r + TRAJECTORY_ETA_R * d
            self.assertEqual(pred.last_weight, w_p * w_t,
                             "the composed weight is the two own-clipped weights' product")
            ew = e * (w_p * w_t)     # production's exact order: e * last_weight first, then 0.5 + 3.0 * e_w
            self.assertEqual(pred.modulate(0.1), 0.1 * float(np.clip(0.5 + 3.0 * ew, 0.5, 2.0)),
                             "modulate reads the weighted error with the unchanged clip")
            seen += 1
            S, T = org.moment(x, xw)
            pred.note_winners(S)
        self.assertGreater(seen, 0, "presence: the stream actually drove moments")


if __name__ == "__main__":
    unittest.main()
