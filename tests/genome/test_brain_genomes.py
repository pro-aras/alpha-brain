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


# edit: Claude (Opus 5.5, F-M6 builder), 2026-09-28 22:21 +0400 — PREREG-BRAIN-IN-BODY AMENDMENT 1 §2: the fixed life's genome is
# BRAIN-LEAN-20261102.genome with exactly `young 3` → `young 3 nearest` (one text line, one parsed value).
class LeanNearest(unittest.TestCase):
    def test_differs_from_lean_20261102_by_young_rule_alone(self):
        lives = BRAIN_DIR / "lives"
        a = (lives / "BRAIN-LEAN-20261102.genome").read_text()
        b = (lives / "BRAIN-LEAN-NEAREST-20261102.genome").read_text()
        la, lb = a.splitlines(), b.splitlines()
        self.assertEqual(len(la), len(lb))
        diff = [(x, y) for x, y in zip(la, lb) if x != y]
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][0].replace("young 3;", "young 3 nearest;"), diff[0][1])
        da, db = parse_genome(a).declared, parse_genome(b).declared
        self.assertEqual({k: v for k, v in db.items() if k != "BRAIN"}, {k: v for k, v in da.items() if k != "BRAIN"})
        self.assertEqual(db["BRAIN"], {**da["BRAIN"], "young_rule": "nearest"})
        self.assertNotIn("young_rule", da["BRAIN"])


class Preflight(unittest.TestCase):
    def test_preflight_is_300_scenes_fresh_only(self):
        declared = parse_genome((BRAIN_DIR / "BRAIN-LEAN-PREFLIGHT.genome").read_text()).declared
        self.assertEqual(declared["WORLD_SCENE"]["train"], 300)
        self.assertEqual(declared["WORLD_SCENE"]["sitting"], ["fresh"])
        self.assertEqual(declared["BRAIN"]["calibrate_at"], [250])


# edit: Claude (Fable 5.1, the seat), 2026-09-29 11:58 +0400 — his 2026-09-29 00:48 word («go for the best decisions which would work for the AI
# we want to build»), decision 2: `young 3 nearest` (F-M6, AMENDMENT 1 §2, gate PASS on never-used scenes) is the LAW of the next brain
# lives, so every template a life is seeded from carries it. The pre-flight template too: a pre-flight runs the law of the life it
# pre-flights. The closed lives' own genomes under lives/ are RECORDS and are not touched (LeanNearest above pins the pair).
class TemplatesCarryNearest(unittest.TestCase):
    TEMPLATES = ("BRAIN-LEAN.genome", "BRAIN-FULL.genome", "BRAIN-LEAN-PREFLIGHT.genome")

    def test_every_brain_template_declares_young_3_nearest(self):
        for name in self.TEMPLATES:
            with self.subTest(name=name):
                brain = parse_genome((BRAIN_DIR / name).read_text()).declared["BRAIN"]
                self.assertEqual(brain["young"], 3)
                self.assertEqual(brain.get("young_rule"), "nearest")

    def test_the_change_is_the_young_rule_alone(self):
        # each template's parsed BRAIN equals the closed life's law (lives/BRAIN-LEAN-20261101.genome) plus the rule, except
        # the pre-flight's own declared calibration schedule
        law = parse_genome((BRAIN_DIR / "lives" / "BRAIN-LEAN-20261101.genome").read_text()).declared["BRAIN"]
        self.assertNotIn("young_rule", law)
        for name in self.TEMPLATES:
            with self.subTest(name=name):
                brain = dict(parse_genome((BRAIN_DIR / name).read_text()).declared["BRAIN"])
                want = {**law, "young_rule": "nearest"}
                if name == "BRAIN-LEAN-PREFLIGHT.genome":
                    want["calibrate_at"] = [250]
                self.assertEqual(brain, want)

    def test_the_closed_lives_genomes_are_untouched(self):
        lives = BRAIN_DIR / "lives"
        for name in ("BRAIN-LEAN-20261101.genome", "BRAIN-LEAN-20261102.genome", "BRAIN-LEAN-20261103.genome",
                     "BRAIN-FULL-20261102.genome"):
            with self.subTest(name=name):
                self.assertNotIn("young_rule", parse_genome((lives / name).read_text()).declared["BRAIN"])


if __name__ == "__main__":
    unittest.main()
