# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:40 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2.
"""test_hands_arming.py — creature.body._declared_hands_config, the function main() uses to arm the hands
door from the genome (main() itself is never called -- test_game_and_ear_sound_arming.py's own precedent,
mirrored here)."""
from __future__ import annotations

import unittest
import unittest.mock as mock
from pathlib import Path

from creature import body as body_module
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME = ROOT / "genome" / "G5.genome"
HANDS_LINE = "HANDS    jail alpha3/hands/jail_run shelf world/programs cpu 10 mem 512 wall 20"
HANDS_LINE_SHORT = "HANDS    jail alpha3/hands/jail_run"


class TestDeclaredHandsConfigArming(unittest.TestCase):
    def test_gated_true_arms_from_a_full_hands_line(self) -> None:
        from creature.senses import hands as hands_sense
        self.assertTrue(hands_sense.HANDS_DOOR_GATED)
        genome = parse_genome(G5_GENOME.read_text() + "\n" + HANDS_LINE + "\n")
        got = body_module._declared_hands_config(genome.declared)
        self.assertIsNotNone(got)
        self.assertEqual(got["jail_path"], Path("/data/dev/alpha3/hands/jail_run"))
        self.assertEqual(got["shelf_dir"], ROOT / "world" / "programs")
        self.assertEqual(got["cpu"], 10)
        self.assertEqual(got["mem"], 512)
        self.assertEqual(got["wall"], 20)

    def test_short_form_arms_nothing(self) -> None:
        """The pre-existing short HANDS grammar (no shelf) has nothing for the body to arm — matching
        _declared_folder_dir's own law for a WORLD line with no folder."""
        genome = parse_genome(G5_GENOME.read_text() + "\n" + HANDS_LINE_SHORT + "\n")
        self.assertIsNone(body_module._declared_hands_config(genome.declared))

    def test_undeclared_hands_arms_nothing(self) -> None:
        self.assertIsNone(body_module._declared_hands_config({}))

    def test_gated_false_arms_nothing_even_with_a_full_line(self) -> None:
        from creature.senses import hands as hands_sense
        with mock.patch.object(hands_sense, "HANDS_DOOR_GATED", False):
            genome = parse_genome(G5_GENOME.read_text() + "\n" + HANDS_LINE + "\n")
            got = body_module._declared_hands_config(genome.declared)
        self.assertIsNone(got)


if __name__ == "__main__":
    unittest.main()
