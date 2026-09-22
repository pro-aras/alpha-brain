# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:30 +0400 — ALPHA4-G.md task 5 (docs/ALPHA4-PREREG.md
# §2/§3): STATUS gains sight_capacity, words_capacity, budget_regenerated on EVERY branch that writes
# STATUS (#164) -- mirrors test_status_births.py's own convention.
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body

from .test_exam import GENOME_PATH


class TestStatusGrowFields(unittest.TestCase):
    def test_capacity_and_regen_fields_on_every_status_write(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH); body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        st = body._build_status()
        for k in ("sight_capacity", "words_capacity", "budget_regenerated"):
            self.assertIn(k, st, k)
            self.assertIsInstance(st[k], int, k)
        self.assertEqual(st["sight_capacity"], body.mind.org.sight.nmax)
        self.assertEqual(st["words_capacity"], body.mind.org.words.nmax)
        self.assertEqual(st["budget_regenerated"], body.mind.org.budget_regenerated)
        # this genome (G4-skeleton, NMAX no GROW) never regenerates -- 0, matching the machinery-level pin
        self.assertEqual(st["budget_regenerated"], 0)


if __name__ == "__main__":
    unittest.main()
