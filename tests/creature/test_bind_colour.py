# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:23 +0400 -- docs/briefs/G5-J-BIND-COLOUR-RETINA.md:
# BIND (G-EYE-2, "one canvas = one moment") and SENSE colour (G-EYE-3/§3.6) mechanics, pinned. The BabyAI
# band reproduction and the full life-2/life-3a replays live in the report (scratch/, not committed --
# they read real closed-life data and Researcher G's harvested frames, neither of which belongs in a fast
# unit test); this file pins the MECHANISM: the parser grammar, sight_dim, colour's grey no-op, and BIND's
# call-count/unit-norm behaviour through a real (small) Mind + tape, the same technique
# tests/creature/test_sleep_boundary.py uses.
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind, _bind_pool
from creature.tape import Tape, read_tape
from genome import gaze, world
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
BASE_GAZE_GENOME = ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome"   # real GAZE + sealed tower, no SLEEP/FAST needed here
BIND_GENOME = ROOT / "tests" / "creature" / "G5-bind-test.genome"


def _write_bind_genome() -> None:
    base = BASE_GAZE_GENOME.read_text()
    BIND_GENOME.write_text(base.rstrip("\n") + "\nBIND     glances per canvas\n")


_write_bind_genome()


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, n: int = 8, seed: int = 909) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


# ------------------------------------------------------------------------------------------ the grammar
class TestGrammar(unittest.TestCase):
    def test_bind_line_declares(self) -> None:
        g = parse_genome(BASE_GAZE_GENOME.read_text() + "\nBIND     glances per canvas\n")
        self.assertEqual(g.declared["BIND"], {"pool": "glances per canvas"})

    def test_bind_bad_line_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(BASE_GAZE_GENOME.read_text() + "\nBIND     fixations per canvas\n")

    def test_colour_line_declares_and_sight_dim_grows_by_32(self) -> None:
        g0 = parse_genome(BASE_GAZE_GENOME.read_text())
        g1 = parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance fixed-gain\n")
        self.assertIsNone(g0.colour)
        self.assertEqual(g1.colour, {"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"})
        self.assertEqual(g1.sight_dim(), g0.sight_dim() + 32)

    def test_colour_block_unit_refused(self) -> None:
        """Only 'fixed-gain' is accepted -- 'block-unit' (the OTHER form Researcher G measured, and
        rejected: #231(1), a legitimately-zero block's noise amplified to norm 1) is not new vocabulary
        the machinery knows, by design."""
        with self.assertRaises(GenomeError):
            parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance block-unit\n")

    def test_undeclared_genomes_unaffected(self) -> None:
        """The G4-wave2 fixture itself (no BIND, no colour) must be untouched by this file's own edits --
        the parity control every additive gene needs (#231's family)."""
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        self.assertNotIn("BIND", g.declared)
        self.assertIsNone(g.colour)


# ------------------------------------------------------------------------------------------ colour's grey no-op
class TestColourGreyNoOp(unittest.TestCase):
    def test_maker_world_colour_channels_are_exactly_zero(self) -> None:
        rng = np.random.default_rng(11)
        maxabs = 0.0
        for thing in world.THINGS_11:
            rgb, _truth = world.render_canvas(thing, rng)
            an = gaze._analyse_frame(rgb)
            maxabs = max(maxabs, float(np.max(np.abs(an["channels"]["rg"]))), float(np.max(np.abs(an["channels"]["by"]))))
        self.assertEqual(maxabs, 0.0, "the maker's world is one grey plane x3 -- rg/by must be exact zero, not merely small")

    def test_colour_on_is_byte_identical_to_colour_off_on_grey(self) -> None:
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        rng = np.random.default_rng(12)
        rgb, _truth = world.render_canvas("circle", rng)
        no_colour = gaze.glances(rgb, g.retina, g.gaze, "surprise", pic_id="x")
        colour = gaze.glances(rgb, g.retina, g.gaze, "surprise", pic_id="x",
                              colour={"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"})
        self.assertEqual(len(no_colour["feats"][0]), 112)
        self.assertEqual(len(colour["feats"][0]), 144)
        for a, b in zip(no_colour["feats"], colour["feats"]):
            self.assertTrue(np.array_equal(a, b[:112]), "the tower's own 112 numbers must be untouched by an inert (all-zero) colour block")
            self.assertTrue(np.all(b[112:] == 0.0))


# ------------------------------------------------------------------------------------------ _bind_pool as a pure function
class TestBindPoolPure(unittest.TestCase):
    def test_empty_is_a_noop(self) -> None:
        self.assertEqual(_bind_pool([]), [])

    def test_pools_to_one_unit_vector(self) -> None:
        rng = np.random.default_rng(3)
        vs = []
        for _ in range(4):
            v = rng.normal(size=16)
            vs.append(v / np.linalg.norm(v))
        pooled = _bind_pool(vs)
        self.assertEqual(len(pooled), 1)
        expect = np.mean(vs, axis=0)
        expect = expect / np.linalg.norm(expect)
        self.assertTrue(np.allclose(pooled[0], expect))
        self.assertAlmostEqual(float(np.linalg.norm(pooled[0])), 1.0, places=12)

    def test_four_identical_glances_pool_to_the_same_unit_vector(self) -> None:
        rng = np.random.default_rng(4)
        v = rng.normal(size=16); v = v / np.linalg.norm(v)
        pooled = _bind_pool([v, v, v, v])
        self.assertTrue(np.allclose(pooled[0], v))


# ------------------------------------------------------------------------------------------ BIND wired through a real Mind
class TestBindWiredMomentCount(unittest.TestCase):
    """The mechanism the report's cadence table (§3) depends on: org.t advances once per canvas under
    BIND, GAZE.fixations times per canvas without it -- checked on a REAL Mind + tape (creature/mind.py's
    _consume_eye), never a synthetic call to Organism.moment()."""

    def test_unbound_advances_t_by_fixations_per_canvas(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=6)
        mind = Mind(BASE_GAZE_GENOME, root)
        n_eye = 0
        for row in read_tape(root):
            mind.consume(row)
            if row["sense"] == "eye":
                n_eye += 1
        self.assertEqual(mind.org.t, n_eye * mind.genome.gaze["fixations"])

    def test_bind_advances_t_by_one_per_canvas(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=6)
        mind = Mind(BIND_GENOME, root)
        n_eye = 0
        for row in read_tape(root):
            mind.consume(row)
            if row["sense"] == "eye":
                n_eye += 1
        self.assertEqual(mind.org.t, n_eye, "BIND: one org.moment()/moment_sight() call per canvas")

    def test_bind_births_no_more_than_unbound_on_the_same_tape(self) -> None:
        """Not the report's headline number (that needs life 2's real tape, §1/§2 of the report) but the
        same DIRECTION, pinned on a small deterministic fixture: pooling four looks into one before any
        birth/resonance decision can only reduce or equal the number of independent birth opportunities."""
        root_u = Path(tempfile.mkdtemp()); _build_tape(root_u, n=8, seed=77)
        root_b = Path(tempfile.mkdtemp()); _build_tape(root_b, n=8, seed=77)
        mind_u = Mind(BASE_GAZE_GENOME, root_u)
        mind_b = Mind(BIND_GENOME, root_b)
        for row in read_tape(root_u):
            mind_u.consume(row)
        for row in read_tape(root_b):
            mind_b.consume(row)
        self.assertLessEqual(len(mind_b.org.births), len(mind_u.org.births))


if __name__ == "__main__":
    unittest.main()
