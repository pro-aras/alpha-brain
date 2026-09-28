# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:45 +0400 — BRAIN-IN-BODY §5's own pin: genome/brain/*.genome.
"""tests/genome/test_brain_genomes.py — the four genome/brain/*.genome files parse; RETINA/GAZE/SENSE colour are
byte-equal to ALPHA4's in all four; LEAN and TWIN differ by exactly the BRAIN line; FULL = ALPHA4's declared dict
plus exactly BRAIN and WORLD_SCENE; a full Mind() constructs under BRAIN-LEAN-TWIN.genome."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
BRAIN_DIR = ROOT / "genome" / "brain"
ALPHA4_TEXT = (ROOT / "genome" / "ALPHA4.genome").read_text()


def _line(text: str, keyword: str) -> str:
    """The first non-#OFF line starting with `keyword` (whitespace-separated first token)."""
    for line in text.splitlines():
        if line.split(None, 1)[:1] == [keyword]:
            return line
    raise AssertionError(f"no {keyword!r} line in text")


class Parsing(unittest.TestCase):
    def test_all_four_parse(self):
        for name in ("BRAIN-LEAN.genome", "BRAIN-LEAN-TWIN.genome", "BRAIN-FULL.genome", "BRAIN-LEAN-PREFLIGHT.genome"):
            with self.subTest(name=name):
                g = parse_genome((BRAIN_DIR / name).read_text())
                self.assertIsNotNone(g)


class SharedEyeFront(unittest.TestCase):
    """RETINA, GAZE and SENSE colour must be byte-equal to ALPHA4's in all four files (INTERFACE §5's own law:
    the body's eye is the eye the brain scored with)."""

    def test_retina_gaze_sense_colour_byte_equal_to_alpha4(self):
        for name in ("BRAIN-LEAN.genome", "BRAIN-LEAN-TWIN.genome", "BRAIN-FULL.genome", "BRAIN-LEAN-PREFLIGHT.genome"):
            text = (BRAIN_DIR / name).read_text()
            with self.subTest(name=name):
                self.assertEqual(_line(text, "RETINA"), _line(ALPHA4_TEXT, "RETINA"))
                self.assertEqual(_line(text, "GAZE"), _line(ALPHA4_TEXT, "GAZE"))
                # SENSE has three lines (eye/ear/colour) in ALPHA4 -- match the "colour" one specifically
                alpha4_colour = next(l for l in ALPHA4_TEXT.splitlines() if re.match(r"SENSE\s+colour\b", l))
                got_colour = next(l for l in text.splitlines() if re.match(r"SENSE\s+colour\b", l))
                self.assertEqual(got_colour, alpha4_colour)


class LeanVsTwin(unittest.TestCase):
    def test_differ_by_exactly_the_brain_line(self):
        lean = (BRAIN_DIR / "BRAIN-LEAN.genome").read_text().splitlines()
        twin = (BRAIN_DIR / "BRAIN-LEAN-TWIN.genome").read_text().splitlines()
        lean_only = [l for l in lean if l not in twin]
        twin_only = [l for l in twin if l not in lean]
        # the header comment lines differ in wording (each names its own file) -- filter to code lines only
        lean_code = [l for l in lean_only if not l.startswith("#")]
        twin_code = [l for l in twin_only if not l.startswith("#")]
        self.assertEqual(twin_code, [])
        self.assertEqual(len(lean_code), 1)
        self.assertTrue(lean_code[0].startswith("BRAIN "), lean_code[0])


class FullEqualsAlpha4PlusTwo(unittest.TestCase):
    def test_full_declared_dict_is_alpha4s_plus_exactly_brain_and_world_scene(self):
        alpha4_declared = parse_genome(ALPHA4_TEXT).declared
        full_declared = parse_genome((BRAIN_DIR / "BRAIN-FULL.genome").read_text()).declared
        extra = set(full_declared) - set(alpha4_declared)
        missing = set(alpha4_declared) - set(full_declared)
        self.assertEqual(extra, {"BRAIN", "WORLD_SCENE"})
        self.assertEqual(missing, set())
        for k in alpha4_declared:
            if k == "SEED":
                continue   # deliberately overridden to match WORLD_SCENE's seed (declared, see the file's header)
            self.assertEqual(full_declared[k], alpha4_declared[k], msg=f"{k} differs from ALPHA4's own")


class SeedConsistency(unittest.TestCase):
    def test_seed_matches_world_scene_seed_in_every_file(self):
        for name in ("BRAIN-LEAN.genome", "BRAIN-LEAN-TWIN.genome", "BRAIN-FULL.genome", "BRAIN-LEAN-PREFLIGHT.genome"):
            g = parse_genome((BRAIN_DIR / name).read_text())
            with self.subTest(name=name):
                self.assertEqual(g.seed, g.declared["WORLD_SCENE"]["seed"])
                self.assertEqual(g.seed, 20261101)


class MindConstructsUnderTwin(unittest.TestCase):
    def test_a_full_mind_constructs_under_brain_lean_twin(self):
        import shutil
        import tempfile
        from creature.mind import Mind
        d = Path(tempfile.mkdtemp(prefix="brain_genome_mind_test_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        m = Mind(BRAIN_DIR / "BRAIN-LEAN-TWIN.genome", d)
        self.assertIsNotNone(m)
        self.assertFalse(hasattr(m, "brain_status") and callable(getattr(m, "brain_status", None)) and m.brain_status() is not None)


class Preflight(unittest.TestCase):
    def test_preflight_is_300_scenes_fresh_only(self):
        declared = parse_genome((BRAIN_DIR / "BRAIN-LEAN-PREFLIGHT.genome").read_text()).declared
        self.assertEqual(declared["WORLD_SCENE"]["train"], 300)
        self.assertEqual(declared["WORLD_SCENE"]["sitting"], ["fresh"])
        self.assertEqual(declared["BRAIN"]["calibrate_at"], [250])


if __name__ == "__main__":
    unittest.main()
