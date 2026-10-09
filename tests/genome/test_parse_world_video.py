# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §1.2/§2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; test-first): the NEW world line `WORLD video shelf <dir> every <n> s; loop; manifest
# sha256` — a FOURTH shape of the WORLD gene (the game/scene branches' precedent), stored under its OWN declared key
# WORLD_VIDEO, never overwriting WORLD / WORLD_GAME / WORLD_SCENE. ONE declared form; every other spelling refuses
# BY NAME. This parser branch and the MOUTH «incremental» hunk share the law's ONE pinned window (the law §6).
"""tests/genome/test_parse_world_video.py — the WORLD video line (PREREG-ALPHA-6 §1.2).

The sense (creature/senses/video.py), the shelf's promotion tool and the line's own genome rows are pinned
elsewhere (tests/creature/test_sense_video.py, tests/tools/test_video_shelf.py); here the parser, whole and only."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()

VIDEO_LINE = "WORLD    video shelf /data/dev/genome-lives/brain-long-5/world/video-shelf every 2 s; loop; manifest sha256"


def lean_text(*lines: str) -> str:
    return _TEMPLATE + "\n" + ("\n".join(lines) + "\n" if lines else "")


class TheDeclaredForm(unittest.TestCase):
    def test_the_line_parses_to_its_own_key(self) -> None:
        d = parse_genome(lean_text(VIDEO_LINE)).declared
        self.assertEqual(d["WORLD_VIDEO"], {"shelf": "/data/dev/genome-lives/brain-long-5/world/video-shelf",
                                            "every_s": 2, "loop": True, "manifest": "sha256"})

    def test_a_relative_shelf_path_parses(self) -> None:
        d = parse_genome(lean_text("WORLD    video shelf world/video-shelf-toy every 2 s; loop; manifest sha256")).declared
        self.assertEqual(d["WORLD_VIDEO"]["shelf"], "world/video-shelf-toy")

    def test_it_never_overwrites_the_other_world_keys(self) -> None:
        text = lean_text(VIDEO_LINE)
        d = parse_genome(text).declared
        self.assertIn("WORLD_SCENE", d)          # the lean template's own scene world, untouched
        self.assertNotIn("WORLD_GAME", d)
        self.assertEqual(d["WORLD_SCENE"]["seed"], 20261101)


class GarbageRefusesByName(unittest.TestCase):
    def test_every_misspelling_refuses(self) -> None:
        for bad in ("WORLD    video shelf /x every 2 s; manifest sha256",                       # no «loop»
                    "WORLD    video shelf /x every 2 s; loop",                                  # no «manifest sha256»
                    "WORLD    video shelf /x every 2 s; loop; manifest md5",                    # the wrong hash word
                    "WORLD    video shelf /x every 2 s; loop; manifest sha256; manifest sha256",
                    "WORLD    video shelf /x every two s; loop; manifest sha256",
                    "WORLD    video shelf /x every 0 s; loop; manifest sha256",                 # 0 is no cadence
                    "WORLD    video shelf /x every -2 s; loop; manifest sha256",
                    "WORLD    video shelf /x every 2; loop; manifest sha256",                   # the unit word is the law's
                    "WORLD    video shelfs /x every 2 s; loop; manifest sha256",
                    "WORLD    videos shelf /x every 2 s; loop; manifest sha256",
                    "WORLD    video shelf every 2 s; loop; manifest sha256",                    # no dir
                    "WORLD    video shelf /x; loop; manifest sha256",                           # no cadence
                    "WORLD    video shelf /x every 2 s; loops; manifest sha256",
                    "WORLD    video shelf /x every 2 s; loop; manifest",
                    "WORLD    video shelf /x y every 2 s; loop; manifest sha256"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(lean_text(bad))
                self.assertIn("WORLD", str(e.exception))

    def test_a_video_line_with_no_cadence_number_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(lean_text("WORLD    video shelf /x every s; loop; manifest sha256"))

    def test_the_cadence_must_be_at_least_one(self) -> None:
        with self.assertRaises(GenomeError) as e:
            parse_genome(lean_text("WORLD    video shelf /x every 0 s; loop; manifest sha256"))
        self.assertIn("WORLD", str(e.exception))


class EveryGenomeOnDiskIsUnchanged(unittest.TestCase):
    def test_a_genome_declares_the_key_iff_its_line_says_so(self) -> None:
        # the line is OPT-IN: for every genome on disk (BRAIN-LONG-5's own included), the parsed dict carries
        # WORLD_VIDEO iff a `WORLD video …` line is present — never silently, never by default.
        for gp in sorted((ROOT / "genome").rglob("*.genome")):
            with self.subTest(genome=gp.name):
                text = gp.read_text()
                d = parse_genome(text).declared
                has_line = any(l.split("#", 1)[0].split()[1:3] == ["video", "shelf"]
                               for l in text.splitlines() if l.startswith(("WORLD ", "WORLD\t")))
                self.assertEqual("WORLD_VIDEO" in d, has_line, gp.name)


if __name__ == "__main__":
    unittest.main()
