# edit: Claude (Fable 5.1), 2026-09-21 22:03 +0400 — THE I×J SEAM (SOLUTIONS #232 addendum: two builders' modules meet at the seam):
# Builder I's DELIVER/MOMENT (where = glance 0's window origin, when, act, source as EXTRA episode columns) must survive
# Builder J's two eye changes — the COLOUR block (a 144-vector: 32 fixed-gain rg/by numbers appended BESIDE the 112) and
# BIND (the four glances mean-pooled into ONE org.moment per canvas; #OFF in G5.genome on its refused bar, but the machinery
# ships and the seam must hold). I's own fixtures are reused (SEAM_GENOME_TEXT, _build_mixed_tape), never paraphrased.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.tape import read_tape
from genome.machinery import parse_genome
from tests.creature.test_g5i_seam_deliver_moment import SEAM_GENOME_TEXT, _write_genome
from tests.creature.test_wave2_predict_fast import _build_mixed_tape

COLOUR_LINE = "SENSE    colour rg by 4x4 under the glance fixed-gain"
BIND_LINE = "BIND     glances per canvas"


def _run(genome_text: str, n_worded: int = 6, n_sight_only: int = 2, seed: int = 4321):
    tmp = Path(tempfile.mkdtemp())
    gpath = _write_genome(tmp, genome_text, "seam.genome")
    root = tmp / "run"
    _build_mixed_tape(root, n_worded=n_worded, n_sight_only=n_sight_only, seed=seed)
    mind = Mind(gpath, root)
    rows = list(read_tape(root))
    for r in rows:
        mind.consume(r)
    n_eye = sum(1 for r in rows if r["sense"] == "eye")
    return mind, n_eye


class TestDeliverBesideColour(unittest.TestCase):
    def test_where_survives_the_144_vector(self) -> None:
        text = SEAM_GENOME_TEXT + COLOUR_LINE + "\n"
        g = parse_genome(text)
        base = parse_genome(SEAM_GENOME_TEXT)
        self.assertEqual(g.sight_dim(), base.sight_dim() + 32)
        mind, n_eye = _run(text)
        self.assertGreater(mind.episodes.n_written, 0)
        self.assertEqual(mind.episodes.dim_s, g.sight_dim(), "the episode's sight column is the 144-vector")
        for eid in range(mind.episodes.n_written):
            rec = mind.episodes.get(eid)
            if rec is None:
                continue
            self.assertIsNotNone(rec["where"]); self.assertEqual(len(rec["where"]), 2)
            self.assertEqual(rec["act"], "glance"); self.assertEqual(rec["glance"], 0)
            self.assertEqual(rec["source"], "test")
        # the grey tape: the 32 colour numbers are exactly zero on every stored episode (J's grey no-op, to the byte)
        import numpy as np
        xs = np.stack([mind.episodes.get(e)["x_s"] for e in range(mind.episodes.n_written) if mind.episodes.get(e) is not None])
        self.assertEqual(float(np.abs(xs[:, -32:]).max()), 0.0)


class TestDeliverUnderBind(unittest.TestCase):
    def test_one_episode_per_canvas_still_carries_glance0_where(self) -> None:
        text = SEAM_GENOME_TEXT + BIND_LINE + "\n"
        mind, n_eye = _run(text)
        self.assertEqual(mind.org.t, n_eye, "BIND: one moment per canvas")
        self.assertEqual(mind.episodes.n_written, n_eye, "BIND: one episode per canvas")
        for eid in range(mind.episodes.n_written):
            rec = mind.episodes.get(eid)
            self.assertIsNotNone(rec)
            self.assertIsNotNone(rec["where"]); self.assertEqual(len(rec["where"]), 2)
            self.assertEqual(rec["glance"], 0, "where is glance 0's window origin whether or not the glances are pooled")

    def test_unbound_twin_advances_fixations_moments_per_canvas(self) -> None:
        # the twin: without BIND the same tape advances org.t by GAZE.fixations per canvas, while the FAST episode is
        # one per canvas on BOTH roads (the first draft of this twin asserted fixations EPISODES per canvas and read
        # 8 != 32 — the episode was never per glance; corrected on that reading, the moment count is what BIND changes)
        mind, n_eye = _run(SEAM_GENOME_TEXT)
        self.assertEqual(mind.org.t, n_eye * mind.genome.gaze["fixations"])
        self.assertEqual(mind.episodes.n_written, n_eye)


if __name__ == "__main__":
    unittest.main()
