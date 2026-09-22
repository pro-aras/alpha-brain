# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:41 +0400 — LIFE-D-ACT-SOUND.md items 2/3: STATUS
# gains `acts_chosen` (a dict, one count PER VERB -- G-MOT-1's census, never a total), `act_mismatches`,
# `sound_events` -- every field written on EVERY status build (#164), via getattr like outcome_episodes
# above (test_status_mind_backlog.py's own pattern).
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
ACT_LINE = "ACT      glance open ask turn step say run"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"
FAST_SOUND_LINE = "FAST     episodes 2000 keys sight words surprise sound"


def _genome_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


class TestStatusActAndSoundFields(unittest.TestCase):
    def _body(self, *extra_lines: str) -> Body:
        gpath = _genome_with(*extra_lines)
        root = Path(tempfile.mkdtemp())
        body = Body(root, gpath)
        body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        return body

    def test_fields_present_and_zero_on_a_fresh_life(self) -> None:
        body = self._body(ACT_LINE, OUTCOME_LINE, FAST_SOUND_LINE)
        st = body._build_status()
        self.assertIn("acts_chosen", st)
        self.assertEqual(st["acts_chosen"], {}, "written empty, never omitted, on a life with zero acts chosen so far")
        self.assertIn("act_mismatches", st)
        self.assertEqual(st["act_mismatches"], 0)
        self.assertIn("sound_events", st)
        self.assertEqual(st["sound_events"], 0)

    def test_acts_chosen_reflects_the_mind_s_own_counter(self) -> None:
        body = self._body(ACT_LINE, OUTCOME_LINE)
        body.mind.acts_chosen["forward"] = 3
        body.mind.acts_chosen["left"] = 1
        body.mind.act_mismatches = 2
        st = body._build_status()
        self.assertEqual(st["acts_chosen"], {"forward": 3, "left": 1})
        self.assertEqual(st["act_mismatches"], 2)

    def test_sound_events_reflects_the_mind_s_own_counter(self) -> None:
        body = self._body(FAST_SOUND_LINE)
        body.mind.sound_events = 5
        st = body._build_status()
        self.assertEqual(st["sound_events"], 5)

    def test_no_act_gene_at_all_still_writes_the_fields(self) -> None:
        """#164: the field is on EVERY write, not only when the gene is declared."""
        body = self._body()
        st = body._build_status()
        self.assertEqual(st["acts_chosen"], {})
        self.assertEqual(st["act_mismatches"], 0)
        self.assertEqual(st["sound_events"], 0)


if __name__ == "__main__":
    unittest.main()
