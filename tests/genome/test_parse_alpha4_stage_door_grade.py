# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:21 +0400 — ALPHA4-PREREG.md §3: the parser
# side of STAGE's new "by <JUDGE>" form, DOOR web, and SENSE grade.
from __future__ import annotations

import unittest
from pathlib import Path

from creature import genes as genes_module
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
LIFE_GENOME_PATH = ROOT / "genome" / "LIFE.genome"

STAGE_4_LINE = "STAGE    4 world by READY"
STAGE_3_LINE = "STAGE    3 nursery moments 200.."
DOOR_WEB_LINE = "DOOR     web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD"
SENSE_GRADE_LINE = "SENSE    grade from ask/graded"


def _add(text: str, *lines: str) -> str:
    return text.rstrip("\n") + "\n" + "\n".join(lines) + "\n"


class TestStageMomentsFormUnchanged(unittest.TestCase):
    def test_existing_moments_form_parses_byte_identical(self) -> None:
        """The existing grammar (STAGE <n> <name> moments <a>..<b>) must parse "as-is" (the brief's own
        words) — LIFE.genome's own two STAGE lines, untouched."""
        g = parse_genome(LIFE_GENOME_PATH.read_text())
        self.assertEqual(g.stages, [(1, "senses", 0, 200), (2, "meet", 200, None)])
        self.assertEqual(g.stage2_start, 200)

    def test_stage_3_nursery_moments_parses_like_any_other_moments_stage(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), STAGE_3_LINE))
        self.assertIn((3, "nursery", 200, None), g.stages)
        self.assertNotIn("STAGE_READY", g.declared)


class TestStageByReady(unittest.TestCase):
    def test_stage_4_world_by_ready_parses(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), STAGE_3_LINE, STAGE_4_LINE))
        self.assertIn((4, "world", "READY", None), g.stages)
        self.assertEqual(g.declared["STAGE_READY"], {"stage": 4})
        self.assertEqual(g.stage2_start, 200, "stage2_start (used for wiring) must be untouched by a judge-form stage")

    def test_misspelt_judge_name_refuses_by_name(self) -> None:
        for bad in ("REDY", "ready", "Ready", "READYY"):
            with self.assertRaises(GenomeError) as ctx:
                parse_genome(_add(LIFE_GENOME_PATH.read_text(), f"STAGE 4 world by {bad}"))
            self.assertIn(bad, str(ctx.exception))
            self.assertIn("READY", str(ctx.exception))

    def test_malformed_stage_line_refuses(self) -> None:
        for bad in ("STAGE 4 world", "STAGE world by READY", "STAGE 4 by READY", "STAGE 4 two words world by READY"):
            with self.assertRaises(GenomeError):
                parse_genome(_add(LIFE_GENOME_PATH.read_text(), bad))

    def test_a_genome_declaring_stage_ready_starts_a_mind(self) -> None:
        """W3-0's generic refusal (creature/genes.py:unwired) must find a real site."""
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), STAGE_3_LINE, STAGE_4_LINE))
        self.assertEqual(genes_module.unwired(g.declared), [])


class TestDoorWeb(unittest.TestCase):
    def test_parses_every_field(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), DOOR_WEB_LINE))
        self.assertEqual(g.declared["DOOR_WEB"], {
            "sources": ["wikipedia-summary", "wiktionary"], "floor_s": 2.0, "per_hour": 60,
            "opens_at_stage": 4, "hold_file": "world/HOLD",
        })

    def test_a_genome_declaring_door_web_starts_a_mind(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), DOOR_WEB_LINE))
        self.assertEqual(genes_module.unwired(g.declared), [])

    def test_typo_refuses_by_name(self) -> None:
        bad_lines = [
            "DOOR web wikipedia-summary wiktionary; floor 2 s; 60 per minute; opens at STAGE 4; hold-file world/HOLD",   # "per minute" not "per hour"
            "DOOR web wikipedia wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD",              # "wikipedia" not "wikipedia-summary"
            "DOOR web wikipedia-summary wiktionary; floor two s; 60 per hour; opens at STAGE 4; hold-file world/HOLD",    # non-numeric floor
            "DOOR web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE four; hold-file world/HOLD",   # non-numeric stage
        ]
        for bad in bad_lines:
            with self.assertRaises(GenomeError, msg=bad):
                parse_genome(_add(LIFE_GENOME_PATH.read_text(), bad))

    def test_world_line_own_web_0_per_hour_clause_is_a_different_gene_untouched(self) -> None:
        """LIFE.genome's own WORLD line carries the words "web 0 per hour by curiosity" as a COMMENT-ish
        trailing clause of the WORLD gene (not DOOR web) — confirms the two never collide."""
        g = parse_genome(LIFE_GENOME_PATH.read_text())
        self.assertNotIn("DOOR_WEB", g.declared)


class TestSenseGrade(unittest.TestCase):
    def test_parses(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), SENSE_GRADE_LINE))
        self.assertEqual(g.declared["SENSE_GRADE"], {"from": "ask/graded"})

    def test_a_genome_declaring_sense_grade_starts_a_mind(self) -> None:
        g = parse_genome(_add(LIFE_GENOME_PATH.read_text(), SENSE_GRADE_LINE))
        self.assertEqual(genes_module.unwired(g.declared), [])

    def test_typo_refuses_by_name(self) -> None:
        for bad in ("SENSE grade from ask/graded/extra", "SENSE grade ask/graded", "SENSE grade from somewhere/else"):
            with self.assertRaises(GenomeError):
                parse_genome(_add(LIFE_GENOME_PATH.read_text(), bad))


class TestAllThreeTogether(unittest.TestCase):
    def test_life_genome_plus_all_three_new_lines_parses_and_starts_a_mind(self) -> None:
        text = _add(LIFE_GENOME_PATH.read_text(), STAGE_3_LINE, STAGE_4_LINE, DOOR_WEB_LINE, SENSE_GRADE_LINE)
        g = parse_genome(text)
        self.assertEqual(genes_module.unwired(g.declared), [])
        self.assertEqual(g.stages[-2:], [(3, "nursery", 200, None), (4, "world", "READY", None)])


if __name__ == "__main__":
    unittest.main()
