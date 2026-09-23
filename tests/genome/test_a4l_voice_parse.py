# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:23 +0400 — A4L-VOICE task 1/2 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3): the four lines of the one road parse; every mis-spelt form refuses BY NAME; the old
# lines parse to the exact shapes they always had (the WORLD dict, g.meet); the rung genome is the floor + exactly its
# declared lines + one edit note (the ladder law §1.1, pinned by difflib).
from __future__ import annotations

import difflib
import re
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"
VOICE = ROOT / "genome" / "ladder" / "A4L-VOICE.genome"

BASE = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.5
BIRTH error misfires 3
BUDGET 400 per arrival
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
SOUND_LINES = "AREA sound from cochlea cos>=0.975\nMEET sight sound\nMEET sound words\n"
WORLD_LINE = "WORLD drawn every 5 s arrivals every 4 h; folder world/; web 0 per hour by curiosity"


class TestVoiceParse(unittest.TestCase):
    def test_the_three_sound_lines_parse(self) -> None:
        g = parse_genome(BASE + SOUND_LINES)
        self.assertEqual(g.declared["AREA_SOUND"], {"from": "cochlea", "theta": 0.975})
        self.assertEqual(g.areas["sound"], "cochlea")
        self.assertEqual(g.declared["MEET_SIGHT_SOUND"], {"pair": ["sight", "sound"]})
        self.assertEqual(g.declared["MEET_SOUND_WORDS"], {"pair": ["sound", "words"]})
        self.assertEqual(g.meet, ("sight", "words"), "the MEET sight words line keeps its own field; a later MEET line never overwrites it")

    def test_meet_order_does_not_move_g_meet(self) -> None:
        g = parse_genome(BASE.replace("MEET sight words\n", "") + SOUND_LINES + "MEET sight words\n")
        self.assertEqual(g.meet, ("sight", "words"))

    def test_the_old_genome_parses_to_the_same_shapes(self) -> None:
        g = parse_genome(BASE)
        self.assertNotIn("AREA_SOUND", g.declared)
        self.assertNotIn("sound", g.areas)
        self.assertEqual(set(g.areas), {"sight", "words"})

    def test_theta_sound_placeholder_refuses_by_name(self) -> None:
        with self.assertRaisesRegex(GenomeError, "THETA_SOUND not set"):
            parse_genome(BASE + "AREA sound from cochlea cos>=THETA_SOUND\n")

    def test_misspelt_area_sound_refuses_by_name(self) -> None:
        for bad in ("AREA sound from cochlea\n", "AREA sound from cochlear cos>=0.9\n", "AREA sound from cochlea cos>0.9\n",
                    "AREA sound from cochlea cos>=0.9 extra\n"):
            with self.assertRaisesRegex(GenomeError, "AREA sound: cannot read", msg=bad):
                parse_genome(BASE + bad)

    def test_misspelt_meet_refuses_by_name(self) -> None:
        for bad in ("MEET sight sounds\n", "MEET sound word\n", "MEET words sound\n", "MEET sound sight\n", "MEET sight\n"):
            with self.assertRaisesRegex(GenomeError, "MEET", msg=bad):
                parse_genome(BASE + "AREA sound from cochlea cos>=0.975\n" + bad)

    def test_a_meet_to_sound_without_the_area_refuses(self) -> None:
        for line in ("MEET sight sound\n", "MEET sound words\n"):
            with self.assertRaisesRegex(GenomeError, "no AREA sound", msg=line):
                parse_genome(BASE + line)

    def test_world_voice_clause(self) -> None:
        g = parse_genome(BASE + WORLD_LINE + "; voice formant\n")
        self.assertEqual(g.declared["WORLD"], {"drawn_every_s": 5, "arrival_every_h": 4, "folder": "world/", "web_per_hour": 0, "voice": "formant"})
        g0 = parse_genome(BASE + WORLD_LINE + "\n")
        self.assertEqual(g0.declared["WORLD"], {"drawn_every_s": 5, "arrival_every_h": 4, "folder": "world/", "web_per_hour": 0},
                         "undeclared: the WORLD dict is exactly the shape every pin reads (no voice key at all)")

    def test_world_voice_misspelt_refuses_by_name(self) -> None:
        with self.assertRaisesRegex(GenomeError, "WORLD voice"):
            parse_genome(BASE + WORLD_LINE + "; voice formants\n")
        with self.assertRaisesRegex(GenomeError, "WORLD"):
            parse_genome(BASE + WORLD_LINE + "; voise formant\n")


class TestTheRungGenome(unittest.TestCase):
    """The ladder law §1.1: the rung's genome = the floor + its declared line(s) + one edit-note header line."""

    def test_voice_genome_parses_and_declares_the_road(self) -> None:
        g = parse_genome(VOICE.read_text())
        self.assertEqual(g.declared["WORLD"].get("voice"), "formant")
        self.assertIn("AREA_SOUND", g.declared)
        self.assertIn("MEET_SIGHT_SOUND", g.declared)
        self.assertIn("MEET_SOUND_WORDS", g.declared)
        self.assertNotIn("EVOLVE", g.declared, "the floor's EVOLVE #OFF is kept")

    def test_difflib_against_the_floor_shows_exactly_the_declared_lines(self) -> None:
        floor = FLOOR.read_text().splitlines()
        voice = VOICE.read_text().splitlines()
        added, removed = [], []
        for d in difflib.ndiff(floor, voice):
            if d.startswith("+ "):
                added.append(d[2:])
            elif d.startswith("- "):
                removed.append(d[2:])
        # exactly one floor line changes (the WORLD line gains "; voice formant"), and nothing else is removed
        self.assertEqual(len(removed), 1, removed)
        self.assertTrue(removed[0].startswith("WORLD    drawn every 5 s"), removed)
        world_new = [a for a in added if a.startswith("WORLD    drawn every 5 s")]
        self.assertEqual(len(world_new), 1, added)
        self.assertIn("; voice formant", world_new[0])
        self.assertEqual(world_new[0].split("#")[0].replace("; voice formant", "").rstrip(), removed[0].split("#")[0].rstrip(),
                         "the WORLD line changes ONLY by its voice clause")
        rest = [a for a in added if a not in world_new]
        header = [a for a in rest if a.startswith("#")]
        genes = [a for a in rest if not a.startswith("#")]
        self.assertEqual(len(header), 1, f"one edit-note header line, got {header}")
        self.assertEqual([re.split(r"\s+", gl.split("#")[0].strip())[:3] for gl in genes],
                         [["AREA", "sound", "from"], ["MEET", "sight", "sound"], ["MEET", "sound", "words"]],
                         f"the three new gene lines, in order, got {genes}")


if __name__ == "__main__":
    unittest.main()
