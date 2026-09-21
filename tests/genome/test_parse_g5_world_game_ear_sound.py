"""test_parse_g5_world_game_ear_sound.py — G5-L brief (docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1/2):
the two additive parser changes, `WORLD game ...` and `SENSE ear-sound ...`.

edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:1x +0400.

The refusing test for both is the SAME test: the existing `WORLD drawn ...` regex (machinery.py:256-259,
pre-this-change) and `G4.genome`'s own declared dict must parse BYTE-IDENTICAL to before — proven here by
parsing G4.genome (unmodified on this branch) both with and without this file's new code in play (there
is only one machinery.py, so the proof is: G4.genome parses at all, its declared["WORLD"] has exactly the
four old keys with the old values, and NOTHING under declared["WORLD_GAME"] or .ear_sound appears — the
old genome text contains neither new gene). A SECOND genome, holding BOTH WORLD lines together, is parsed
to prove the two shapes coexist without collision (the G5-DESIGN §3 requirement: "the whole life" runs the
maker's drawn world AND the babyai world at once).
"""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
G4_TEXT = (ROOT / "genome" / "G4.genome").read_text()
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()

WORLD_GAME_LINE = ("WORLD    game babyai-gotolocal every 5 s; seed 20260922; "
                    "frames pov 7x7 tile 32; consequence: his act chooses the next frame")
EAR_SOUND_LINE = "SENSE    ear-sound wav 16000 mono"


class TestOldWorldLineByteIdentical(unittest.TestCase):
    """The refusing test named in the brief: the pre-existing `WORLD drawn ...` shape (and everything
    else in G4.genome, the live creature's own genome file) parses EXACTLY as it did before this branch —
    proven on the genome file itself, not a paraphrase of it."""

    def test_g4_genome_parses_and_old_world_dict_is_unchanged(self) -> None:
        g = parse_genome(G4_TEXT)
        self.assertIn("WORLD", g.declared)
        self.assertEqual(g.declared["WORLD"], {
            "drawn_every_s": 5, "arrival_every_h": 6, "folder": "world/", "web_per_hour": 6,
        })
        self.assertNotIn("WORLD_GAME", g.declared, "G4.genome names no WORLD game line; declared must not invent one")
        self.assertIsNone(g.ear_sound, "G4.genome names no SENSE ear-sound line; the field must stay None")

    def test_old_world_line_alone_still_parses_the_same_four_keys(self) -> None:
        text = SKELETON_TEXT + "\nWORLD    drawn every 5 s arrivals every 6 h; folder world/; web 6 per hour by curiosity\n"
        g = parse_genome(text)
        self.assertEqual(g.declared["WORLD"], {
            "drawn_every_s": 5, "arrival_every_h": 6, "folder": "world/", "web_per_hour": 6,
        })

    def test_malformed_old_world_line_still_refused_the_same_way(self) -> None:
        text = SKELETON_TEXT + "\nWORLD    drawn every s arrivals every 6 h; folder world/; web 6 per hour by curiosity\n"
        with self.assertRaises(GenomeError) as cm:
            parse_genome(text)
        self.assertIn("WORLD", str(cm.exception))


class TestWorldGameLine(unittest.TestCase):
    def test_valid_line_parses_into_its_own_declared_key(self) -> None:
        g = parse_genome(SKELETON_TEXT + "\n" + WORLD_GAME_LINE + "\n")
        self.assertEqual(g.declared["WORLD_GAME"], {
            "game": "babyai-gotolocal", "every_s": 5, "seed": 20260922,
            "pov_h": 7, "pov_w": 7, "tile": 32,
            "consequence": "his act chooses the next frame",
        })
        self.assertNotIn("WORLD", g.declared, "a genome with ONLY the game line must not invent a drawn-world dict")

    def test_missing_number_is_refused_by_name(self) -> None:
        broken = ("WORLD    game babyai-gotolocal every s; seed 20260922; "
                   "frames pov 7x7 tile 32; consequence: his act chooses the next frame")
        with self.assertRaises(GenomeError) as cm:
            parse_genome(SKELETON_TEXT + "\n" + broken + "\n")
        self.assertIn("WORLD game", str(cm.exception))

    def test_missing_consequence_clause_is_refused(self) -> None:
        broken = "WORLD    game babyai-gotolocal every 5 s; seed 20260922; frames pov 7x7 tile 32"
        with self.assertRaises(GenomeError):
            parse_genome(SKELETON_TEXT + "\n" + broken + "\n")

    def test_both_world_lines_coexist_without_collision(self) -> None:
        """The G5 life's own shape (G5-DESIGN §3 lines 90-91): the maker's drawn world AND the babyai
        world declared together. Order must not matter — tried both ways."""
        drawn = "WORLD    drawn every 5 s arrivals every 6 h; folder world/; web 6 per hour by curiosity"
        for order in ((drawn, WORLD_GAME_LINE), (WORLD_GAME_LINE, drawn)):
            with self.subTest(order=order):
                text = SKELETON_TEXT + "\n" + "\n".join(order) + "\n"
                g = parse_genome(text)
                self.assertEqual(g.declared["WORLD"], {
                    "drawn_every_s": 5, "arrival_every_h": 6, "folder": "world/", "web_per_hour": 6,
                }, "the drawn world's dict must be untouched regardless of the game line's presence or order")
                self.assertEqual(g.declared["WORLD_GAME"]["game"], "babyai-gotolocal")


class TestSenseEarSoundLine(unittest.TestCase):
    def test_valid_line_sets_the_ear_sound_field(self) -> None:
        g = parse_genome(SKELETON_TEXT + "\n" + EAR_SOUND_LINE + "\n")
        self.assertEqual(g.ear_sound, {"rate": 16000, "channels": "mono"})
        self.assertNotIn("ear_sound", g.declared, "SENSE ear-sound is a Genome FIELD, never a declared[...] key")

    def test_old_sense_ear_line_untouched(self) -> None:
        # G4-skeleton.genome already carries `SENSE ear letters 8`; confirm it still parses to the
        # letters-based fields exactly, with ear_sound left None, when ear-sound is ALSO declared.
        g = parse_genome(SKELETON_TEXT + "\n" + EAR_SOUND_LINE + "\n")
        self.assertEqual(g.ear_letters, 8)
        self.assertFalse(g.ear_blank_zero)

    def test_malformed_line_refused_by_name(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome(SKELETON_TEXT + "\nSENSE    ear-sound wav mono\n")
        self.assertIn("ear-sound", str(cm.exception))

    def test_stereo_is_refused_not_silently_accepted(self) -> None:
        # the brief's own line is "wav 16000 mono" — stereo (needed for EAR.md's WHERE/ITD/ILD) is
        # explicitly out of scope here (raised in the builder report), and must refuse rather than parse
        # into something the sense thread would misread.
        with self.assertRaises(GenomeError):
            parse_genome(SKELETON_TEXT + "\nSENSE    ear-sound wav 16000 stereo\n")

    def test_undeclared_means_none(self) -> None:
        g = parse_genome(SKELETON_TEXT)
        self.assertIsNone(g.ear_sound)


class TestUnwiredRefusalForWorldGame(unittest.TestCase):
    """W3-0 (creature/genes.py): a declared gene with no RUNS site refuses the organism. WORLD_GAME now
    HAS a site (creature/body.py:main), so a genome declaring it must NOT be refused for that reason —
    proven directly against genes.unwired() (Mind's own check), not by starting a live Mind (too heavy
    for this test file; test_wave3_seams.py-style direct genes.unwired() calls are the established
    pattern for this check — see creature/genes.py's own docstring)."""

    def test_world_game_is_wired(self) -> None:
        from creature import genes as genes_module
        g = parse_genome(SKELETON_TEXT + "\n" + WORLD_GAME_LINE + "\n")
        bad = genes_module.unwired(g.declared)
        self.assertNotIn("WORLD_GAME", bad, f"WORLD_GAME must have a RUNS site now; unwired() returned {bad}")


if __name__ == "__main__":
    unittest.main()
