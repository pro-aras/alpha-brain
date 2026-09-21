# edit: Claude (Fable 5.1), 2026-09-21 22:12 +0400 — the verdict reader's twins under G5 (found at J's landing): (1) the T-one-glance wrapper must
# forward every keyword the mind passes (colour=…), (2) the no-wire twin must keep the genome's declared error arm. Both pinned
# through the reader's own helpers; the negative half of (1) is the old lambda's shape, which must raise on the new call.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from creature.mind import Mind
from genome import gaze, world
from genome.machinery import parse_genome
from tools import verdict_g4

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME = ROOT / "genome" / "G4.genome"


class TestOneGlanceWrapperForwardsKeywords(unittest.TestCase):
    def tearDown(self) -> None:
        gaze.glances = self._orig

    def setUp(self) -> None:
        self._orig = gaze.glances

    def test_new_wrapper_accepts_colour_and_forces_mode_one(self) -> None:
        g = parse_genome(G4_GENOME.read_text())
        rgb, _ = world.render_canvas("circle", np.random.default_rng(3))
        verdict_g4._force_one_glance()
        out = gaze.glances(rgb, g.retina, g.gaze, "surprise", "pic", colour=None)   # the mind's own call shape
        self.assertEqual(len(out["feats"]), 1, "mode one: one feature vector for the whole canvas")

    def test_old_lambda_shape_raises_on_the_mind_call(self) -> None:
        # the negative control: the pre-fix wrapper (no **kw) cannot take the mind's colour= keyword
        orig = gaze.glances
        gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="": orig(rgb, spec_, g, "one", pic_id)
        g = parse_genome(G4_GENOME.read_text())
        rgb, _ = world.render_canvas("circle", np.random.default_rng(3))
        with self.assertRaises(TypeError):
            gaze.glances(rgb, g.retina, g.gaze, "surprise", "pic", colour=None)


class TestNowireKeepsTheArm(unittest.TestCase):
    def test_comparator_arm_survives_nowire(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        text = G4_GENOME.read_text().replace("PREDICT  next glance; error scales delta 0.5..2.0; ranks replay; grades act",
                                             "PREDICT  next glance; error scales delta 0.5..2.0; ranks replay; grades act; error comparator")
        gp = tmp / "cmp.genome"; gp.write_text(text)
        mind = Mind(gp, tmp / "run")
        self.assertEqual(mind.predictor.arm, "comparator")
        verdict_g4._nowire(mind)
        self.assertEqual(mind.predictor.arm, "comparator", "the no-wire twin must run the life's own error arm")
        self.assertIs(mind.predictor.org, mind.org)


if __name__ == "__main__":
    unittest.main()
