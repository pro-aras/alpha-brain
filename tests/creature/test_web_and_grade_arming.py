# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:29 +0400 — ALPHA4-PREREG.md §3/§4: the web
# door's own arming (creature.body._declared_web_config) and the grade sense's hold_file resolution
# (creature.body.Body.start's own SENSE_GRADE branch) — main()/Body.start() are never called, mirroring
# test_hands_arming.py's/test_game_and_ear_sound_arming.py's own established precedent for this codebase.
from __future__ import annotations

import unittest
import unittest.mock as mock
from pathlib import Path

from creature import body as body_module
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
LIFE_GENOME = ROOT / "genome" / "LIFE.genome"
SKELETON_GENOME = ROOT / "genome" / "G4-skeleton.genome"   # no SIT/EXAM/HANDS/BODY-thread-roster declared -- the lightest base for a Body.start() test
DOOR_WEB_LINE = "DOOR     web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD"
SENSE_GRADE_LINE = "SENSE    grade from ask/graded"


def _genome(*lines: str):
    return parse_genome(LIFE_GENOME.read_text() + "\n" + "\n".join(lines) + "\n")


class TestDeclaredWebConfigArming(unittest.TestCase):
    def test_gated_true_arms_from_the_door_web_line(self) -> None:
        from creature.senses import web as web_sense
        self.assertTrue(web_sense.WEB_DOOR_GATED)
        g = _genome(DOOR_WEB_LINE)
        got = body_module._declared_web_config(g.declared)
        self.assertEqual(got, {"sources": ["wikipedia-summary", "wiktionary"], "floor_s": 2.0, "per_hour": 60,
                                "opens_at_stage": 4, "hold_file": "world/HOLD"})

    def test_undeclared_door_web_arms_nothing(self) -> None:
        self.assertIsNone(body_module._declared_web_config({}))

    def test_gated_false_arms_nothing_even_with_the_line(self) -> None:
        from creature.senses import web as web_sense
        with mock.patch.object(web_sense, "WEB_DOOR_GATED", False):
            g = _genome(DOOR_WEB_LINE)
            got = body_module._declared_web_config(g.declared)
        self.assertIsNone(got)


class TestBodyStartWiresGradeAndHoldFile(unittest.TestCase):
    """The one piece `_declared_web_config` alone does not cover: `Body.start()`'s own SENSE_GRADE branch
    threads DOOR_WEB's hold_file into the grade sense — tested here directly against the constructed
    `functools.partial`'s own bound keywords (never running the thread), the same "prove the LAST link"
    discipline #180 asks for."""

    def _body_for(self, tmp_path: Path, *extra_lines: str):
        from creature.body import Body
        root = tmp_path / "run"
        gpath = tmp_path / "g.genome"
        gpath.write_text(SKELETON_GENOME.read_text() + "\n" + "\n".join(extra_lines) + "\n")
        return Body(root, gpath)

    def test_sense_grade_with_door_web_threads_the_resolved_hold_file(self) -> None:
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        body = self._body_for(tmp, SENSE_GRADE_LINE, DOOR_WEB_LINE)
        body.start()   # builds body.mind itself (fresh root -> no snapshot to resume)
        try:
            grade_threads = [st for st in body.sense_threads if st.sense_name == "grade"]
            self.assertEqual(len(grade_threads), 1)
            bound = grade_threads[0].fn
            self.assertEqual(bound.keywords["hold_file"], body.root / "world" / "HOLD")
        finally:
            body.stop()

    def test_sense_grade_without_door_web_threads_no_hold_file(self) -> None:
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        body = self._body_for(tmp, SENSE_GRADE_LINE)   # SENSE_GRADE alone, no DOOR_WEB
        body.start()
        try:
            grade_threads = [st for st in body.sense_threads if st.sense_name == "grade"]
            self.assertEqual(len(grade_threads), 1)
            self.assertIsNone(grade_threads[0].fn.keywords["hold_file"])
        finally:
            body.stop()


if __name__ == "__main__":
    unittest.main()
