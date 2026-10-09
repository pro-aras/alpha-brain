# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:30 +0400 — G-UNIT of PREREG-N1-PRECISION
# (+ AMENDMENT 1): the precision register's unit gates. (a) flag OFF byte-identity of modulate() against the
# inline old formula over a real canvas stream; (b) first call w = 1 (the v0 prior, within the δ fingerprint);
# (c) the register's comparative response at the vector level (stable deviant w > 1, noisy deviant w < 1,
# ratio ≥ 1.25); (d) determinism to the last digit (the weight sequence collected at every error() call);
# (e) the degenerate e ≡ 0 stream (an alive cell's own vector fed back) stays bounded, never NaN;
# (f) the Mind thread (precision= threaded to the predictor; default OFF).
#
# Vector-level streams (c–e): a 'thing' is a fixed random prototype vector with small jitter; an unstructured
# scene is a fresh random unit vector (pairwise cos ≈ ±0.08 in 112-dim, never resonating). Pixel-noise canvases
# are NOT used as noise: through the pool3 retina they collapse to the same grey mush (measured 2026-10-09:
# noise-vs-noise cos ≈ 0.963, p95 0.971) — they would be LEARNED, the opposite of noise.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome, retina, retina_dim
from genome.predict import Predictor

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


def _build_genome():
    return parse_genome(_TOY_GENES)


def _unit_vec(rng: np.random.Generator, dim: int) -> np.ndarray:
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def _proto_stream(rng: np.random.Generator, dim: int, n: int, noise_every_3rd: bool = False):
    """A fixed prototype vector with small jitter (a learnable 'thing' at the vector level); with
    noise_every_3rd, every i % 3 == 2 moment is a fresh random unit vector (AMENDMENT 1's noisy world)."""
    proto = _unit_vec(rng, dim)
    out = []
    for i in range(n):
        if noise_every_3rd and i % 3 == 2:
            out.append(_unit_vec(rng, dim))
        else:
            v = proto + 0.02 * rng.normal(size=dim)
            out.append(v / np.linalg.norm(v))
    return out


def _run_vectors(pred: Predictor, org: Organism, xs) -> list:
    """Drive moments in the mind's own order (error() BEFORE moment(), note_winners after — the
    test_predict.py form) over retina-space vectors; returns the weight read after every error() call."""
    weights = []
    xw = world.encode_word("circle", True)
    for x in xs:
        pred.error(x)
        weights.append(pred.last_weight)
        S, T = org.moment(x, xw)
        pred.note_winners(S)
    return weights


class TestPrecisionRegister(unittest.TestCase):
    def test_a_flag_off_byte_identical(self) -> None:
        """The regression pin (the G5-E form): flag OFF, modulate() returns exactly the old formula's
        value over a real driven canvas stream — every moment, to the last float digit — and the weight
        register is never touched."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org)                      # no precision argument: the old road
        xs = [retina(world.render(t, rng, side=24), g.retina) for t in THINGS * 10]
        seen = 0
        for x in xs:
            xw = world.encode_word("circle", True)
            e = pred.error(x)
            got = pred.modulate(0.1)
            want = 0.1 * float(np.clip(0.5 + 3.0 * e, 0.5, 2.0))
            self.assertEqual(got, want, "flag OFF must run the exact old arithmetic")
            self.assertIsNone(pred.last_weight, "flag OFF: the weight register is never touched")
            seen += 1
            S, T = org.moment(x, xw)
            pred.note_winners(S)
        self.assertGreater(seen, 0, "presence: the stream actually drove moments")

    def test_b_first_call_weight_one(self) -> None:
        """AMENDMENT 1's prior: the first call reads w = v0/(v0 + δ) = 1 within the δ fingerprint, and the
        first moment's modulate is byte-identical to master's (the [lo, hi] clip absorbs the 4e-6)."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, precision=True)
        x = retina(world.render("circle", rng, side=24), g.retina)
        e = pred.error(x)
        self.assertAlmostEqual(pred.last_weight, 1.0, places=5)
        self.assertEqual(pred.modulate(0.1), 0.1 * float(np.clip(0.5 + 3.0 * e, 0.5, 2.0)),
                         "the first moment is byte-identical even flag-on (w = 1 to within the clip's reading)")

    def test_c_register_response_comparative(self) -> None:
        """G-UNIT (c), AMENDMENT 1's comparative form: the SAME deviant (a fresh random unit vector)
        reads w > 1 after a stable stream and w < 1 after a noisy stream, ratio ≥ 1.25."""
        rng = np.random.default_rng(21)
        g = _build_genome()
        dim = retina_dim(g.retina)

        org_s = Organism(g)
        pred_s = Predictor(org_s, precision=True)
        _run_vectors(pred_s, org_s, _proto_stream(rng, dim, 120))
        pred_s.error(_unit_vec(rng, dim))
        w_stable = pred_s.last_weight

        org_n = Organism(g)
        pred_n = Predictor(org_n, precision=True)
        _run_vectors(pred_n, org_n, _proto_stream(rng, dim, 120, noise_every_3rd=True))
        pred_n.error(_unit_vec(rng, dim))
        w_noisy = pred_n.last_weight

        self.assertGreater(w_stable, 1.0, "a deviant in a learned-predictable world is amplified")
        self.assertLess(w_noisy, 1.0, "the same deviant in a noisy world is discounted")
        self.assertGreaterEqual(w_stable / w_noisy, 1.25)

    def test_d_determinism(self) -> None:
        """Two identical runs give identical weight sequences to the last digit (pure float EMAs, no RNG)."""
        sequences = []
        for _ in range(2):
            rng = np.random.default_rng(33)
            g = _build_genome()
            org = Organism(g)
            pred = Predictor(org, precision=True)
            sequences.append(_run_vectors(pred, org, _proto_stream(rng, retina_dim(g.retina), 60, noise_every_3rd=True)))
        self.assertGreater(len(sequences[0]), 0, "presence: weights were collected")
        self.assertIsNotNone(sequences[0][-1], "the flag is actually on in this test")
        self.assertEqual(sequences[0], sequences[1])

    def test_e_degenerate_zero_stream_bounded(self) -> None:
        """Feeding an alive cell's OWN vector back gives e ≡ 0 exactly: w must stay inside the clip and
        never NaN (the pin at 4.0 is the declared correct mode of a maximally trusted channel)."""
        rng = np.random.default_rng(9)
        g = _build_genome()
        org = Organism(g)
        pred = Predictor(org, precision=True)
        _run_vectors(pred, org, _proto_stream(rng, retina_dim(g.retina), 20))
        alive = org.sight.alive_ids()
        self.assertGreater(len(alive), 0, "presence: the stable stream bore at least one sight cell")
        own = np.asarray(org.sight.cells[int(alive[0])], dtype=float)
        ws = []
        for _ in range(50):
            pred.error(own)
            ws.append(pred.last_weight)
        self.assertTrue(all(np.isfinite(ws)), "never NaN/inf")
        self.assertTrue(all(0.25 <= w <= 4.0 for w in ws), "always inside the declared clip")
        self.assertEqual(ws[-1], 4.0, "a perfectly predicted channel pins at the top clip — the declared mode")

    def test_f_mind_thread(self) -> None:
        """Mind(..., precision=True) threads the flag to its predictor; the default stays OFF."""
        from creature.mind import Mind
        genome_path = Path(tempfile.mkdtemp()) / "toy.genome"
        genome_path.write_text(_TOY_GENES + "PREDICT next glance; error scales delta 0.5..2.0; ranks replay; grades act\n")
        m_off = Mind(genome_path, Path(tempfile.mkdtemp()))
        m_on = Mind(genome_path, Path(tempfile.mkdtemp()), precision=True)
        self.assertIsNotNone(m_off.predictor, "presence: the toy genome declares PREDICT, the predictor exists")
        self.assertFalse(m_off.predictor.precision)
        self.assertTrue(m_on.predictor.precision)


if __name__ == "__main__":
    unittest.main()
