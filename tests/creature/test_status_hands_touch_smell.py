# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:41 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2/3/4:
# STATUS gains `runs_by_program` (a dict, one count PER PROGRAM -- G-MOT-1's census, never a total), `runs`
# (its sum), `hands_no_road`, `touch_events`, `smell_events` -- every field written on EVERY status build
# (#164), via getattr like sound_events above (test_status_act_and_sound.py's own pattern, mirrored here).
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"
TOUCH_LINE = "SENSE    touch from hands: exit rate stalls retries bytes"
SMELL_LINE = "SENSE    smell kind size folder age"


def _genome_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G5_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


class TestStatusHandsTouchSmellFields(unittest.TestCase):
    def _body(self, *extra_lines: str) -> Body:
        gpath = _genome_with(*extra_lines)
        root = Path(tempfile.mkdtemp())
        body = Body(root, gpath)
        body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        return body

    def test_fields_present_and_zero_on_a_fresh_life(self) -> None:
        body = self._body(TOUCH_LINE, SMELL_LINE)
        st = body._build_status()
        self.assertIn("runs_by_program", st)
        self.assertEqual(st["runs_by_program"], {})
        self.assertIn("runs", st)
        self.assertEqual(st["runs"], 0)
        self.assertIn("hands_no_road", st)
        self.assertEqual(st["hands_no_road"], 0)
        self.assertIn("touch_events", st)
        self.assertEqual(st["touch_events"], 0)
        self.assertIn("smell_events", st)
        self.assertEqual(st["smell_events"], 0)

    def test_runs_by_program_reflects_the_mind_s_own_counter(self) -> None:
        body = self._body()
        body.mind.runs_chosen["circle_0"] = 4
        body.mind.runs_chosen["square_1"] = 2
        body.mind.hands_no_road = 1
        st = body._build_status()
        self.assertEqual(st["runs_by_program"], {"circle_0": 4, "square_1": 2})
        self.assertEqual(st["runs"], 6)
        self.assertEqual(st["hands_no_road"], 1)

    def test_touch_smell_events_reflect_the_mind_s_own_counters(self) -> None:
        body = self._body(TOUCH_LINE, SMELL_LINE)
        body.mind.touch_events = 7
        body.mind.smell_events = 3
        st = body._build_status()
        self.assertEqual(st["touch_events"], 7)
        self.assertEqual(st["smell_events"], 3)

    def test_no_hands_gene_at_all_still_writes_the_fields(self) -> None:
        """#164: the field is on EVERY write, not only when the gene is declared."""
        body = self._body()
        st = body._build_status()
        self.assertEqual(st["runs_by_program"], {})
        self.assertEqual(st["runs"], 0)
        self.assertEqual(st["hands_no_road"], 0)
        self.assertEqual(st["touch_events"], 0)
        self.assertEqual(st["smell_events"], 0)


if __name__ == "__main__":
    unittest.main()
