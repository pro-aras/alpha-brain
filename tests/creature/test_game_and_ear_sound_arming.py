# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 23:3x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1/2.
"""test_game_and_ear_sound_arming.py — creature.body._declared_game_config, the one function main() uses
to arm the game door from the genome (main() itself is never called by any test -- C2/C3's own precedent
in test_folder_door.py's TestDeclaredFolderDirArming, mirrored here for the game door and, one layer
simpler, for genome.ear_sound's own gate)."""
from __future__ import annotations

import unittest
import unittest.mock as mock
from pathlib import Path

from creature import body as body_module
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_SKELETON = ROOT / "genome" / "G4-skeleton.genome"
WORLD_GAME_LINE = ("WORLD    game babyai-gotolocal every 5 s; seed 20260922; "
                    "frames pov 7x7 tile 32; consequence: his act chooses the next frame")


class TestDeclaredGameConfigArming(unittest.TestCase):
    def test_gated_true_arms_from_a_declared_world_game_line(self) -> None:
        from creature.senses import game as game_sense
        self.assertTrue(game_sense.GAME_DOOR_GATED)
        genome = parse_genome(G4_SKELETON.read_text() + "\n" + WORLD_GAME_LINE + "\n")
        got = body_module._declared_game_config(genome.declared)
        self.assertEqual(got, {"game": "babyai-gotolocal", "every_s": 5, "seed": 20260922,
                                "pov_h": 7, "pov_w": 7, "tile": 32,
                                "consequence": "his act chooses the next frame"})

    def test_undeclared_world_game_arms_nothing(self) -> None:
        self.assertIsNone(body_module._declared_game_config({}))
        self.assertIsNone(body_module._declared_game_config({"WORLD": {"folder": "world/"}}),
                           "the DRAWN world's own dict must not be mistaken for WORLD_GAME")

    def test_gated_false_arms_nothing_even_with_a_declared_line(self) -> None:
        from creature.senses import game as game_sense
        with mock.patch.object(game_sense, "GAME_DOOR_GATED", False):
            got = body_module._declared_game_config({"WORLD_GAME": {"game": "babyai-gotolocal"}})
        self.assertIsNone(got)


# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:38 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8):
# creature/body.py:_game_act_file_path, main()'s own half of the ONE gate (game_sense.mind_drives_acts)
# that decides whether --act-file is ever passed to the worker.
class TestGameActFilePathArming(unittest.TestCase):
    def test_turn_and_step_declared_arms_the_act_file_path(self) -> None:
        root = Path("/tmp/does-not-need-to-exist-for-this-check")
        declared = {"ACT": {"verbs": ["glance", "open", "ask", "turn", "step", "say", "run"]}}
        got = body_module._game_act_file_path(root, declared)
        self.assertEqual(got, root / "game" / "ACT")

    def test_act_without_turn_or_step_arms_nothing(self) -> None:
        root = Path("/tmp/does-not-need-to-exist-for-this-check")
        declared = {"ACT": {"verbs": ["glance", "open", "ask"]}}
        self.assertIsNone(body_module._game_act_file_path(root, declared))

    def test_undeclared_act_arms_nothing(self) -> None:
        root = Path("/tmp/does-not-need-to-exist-for-this-check")
        self.assertIsNone(body_module._game_act_file_path(root, {}))


class TestEarSoundGate(unittest.TestCase):
    def test_gated_true_reads_the_genome_field(self) -> None:
        from creature.senses import ear as ear_sense
        self.assertTrue(ear_sense.EAR_SOUND_DOOR_GATED)
        genome = parse_genome(G4_SKELETON.read_text() + "\nSENSE    ear-sound wav 16000 mono\n")
        self.assertEqual(genome.ear_sound, {"rate": 16000, "channels": "mono"})

    def test_undeclared_ear_sound_is_none(self) -> None:
        genome = parse_genome(G4_SKELETON.read_text())
        self.assertIsNone(genome.ear_sound)


if __name__ == "__main__":
    unittest.main()
