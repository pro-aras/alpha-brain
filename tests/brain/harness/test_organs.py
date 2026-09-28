# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:1x +0400 — tests for brain/world/organs.py. Must run
# under /usr/bin/python3 (loads genome.gaze, which verifies real pinned files under /data/dev/alpha2 and
# /data/dev/alpha3).
from __future__ import annotations

import unittest

from brain.world import organs


class TestOrgans(unittest.TestCase):
    def test_load_genome_has_the_declared_retina_gaze_colour(self) -> None:
        g = organs.load_genome()
        self.assertIn("tower:eye-tower-g2", g.retina)
        self.assertEqual(int(g.gaze["fixations"]), 4)
        self.assertEqual(int(g.gaze["grid"]), 16)
        self.assertEqual(int(g.gaze["canvas"]), 128)
        self.assertEqual(int(g.gaze["glance"]), 32)
        self.assertEqual(int(g.gaze["coarse"]), 32)
        self.assertIsNotNone(g.colour)

    def test_sight_dim_is_144(self) -> None:
        g = organs.load_genome()
        self.assertEqual(g.sight_dim(), 144)   # 112 tower + 32 colour, §2.5

    def test_organ_pins_has_four_entries_and_matches_declared_tower_sha(self) -> None:
        pins = organs.organ_pins()
        self.assertEqual(len(pins), 4)
        self.assertEqual(pins["eye-tower-g2/tower.bin"], organs.TOWER_BIN_SHA256)

    def test_verify_organs_load_does_not_raise(self) -> None:
        organs.verify_organs_load()

    def test_genome_sha_is_stable(self) -> None:
        self.assertEqual(organs.genome_sha(), organs.genome_sha())


if __name__ == "__main__":
    unittest.main()
