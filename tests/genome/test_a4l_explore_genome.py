# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:55 +0400 — docs/A4-LADDER-PREREG.md §2.5 PHASE 2 (the
# rung A4L-EXPLORE): the ONE gene line `ACT value reward <n>; optimism <f>`, its parser branch (a SECOND ACT line, dispatched
# on args[0] == "value" as SENSE dispatches — the verbs line untouched), its registry row, its BOUNDS rows (excluded: a
# ladder rung under EVOLVE #OFF), and the rung genome = the FLOOR + that one line + one header note (difflib pin, §1.1).
from __future__ import annotations

import difflib
import unittest
from pathlib import Path

from creature import genes
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
FLOOR = ROOT / "genome" / "ladder" / "A4L-FLOOR.genome"
RUNG = ROOT / "genome" / "ladder" / "A4L-EXPLORE.genome"
G4 = ROOT / "genome" / "G4.genome"
ACT_VERBS = "ACT      glance open ask turn step say run"
ACT_VALUE = "ACT      value reward 10; optimism 1"
OUTCOME = "OUTCOME  act to episode; error grades it; ranks replay"


def _g4(*lines: str):
    return parse_genome(G4.read_text() + "\n" + "\n".join(lines) + "\n")


class TestParser(unittest.TestCase):
    def test_the_value_line_parses_beside_the_verbs_line(self) -> None:
        g = _g4(ACT_VERBS, ACT_VALUE, OUTCOME)
        self.assertEqual(g.declared["ACT_VALUE"], {"law": "reward", "window": 10, "optimism": 1.0})
        self.assertEqual(g.declared["ACT"], {"verbs": ["glance", "open", "ask", "turn", "step", "say", "run"]})

    def test_order_does_not_matter(self) -> None:
        g = _g4(ACT_VALUE, ACT_VERBS, OUTCOME)
        self.assertEqual(g.declared["ACT"]["verbs"][3:5], ["turn", "step"])
        self.assertEqual(g.declared["ACT_VALUE"]["window"], 10)

    def test_other_windows_and_optimism(self) -> None:
        g = _g4(ACT_VERBS, "ACT      value reward 25; optimism 0.5", OUTCOME)
        self.assertEqual(g.declared["ACT_VALUE"], {"law": "reward", "window": 25, "optimism": 0.5})

    def test_undeclared_carries_no_key(self) -> None:
        g = _g4(ACT_VERBS, OUTCOME)
        self.assertNotIn("ACT_VALUE", g.declared)

    def test_misspelt_forms_refuse_by_name(self) -> None:
        for bad in ("ACT      value rewrad 10; optimism 1", "ACT      value reward ten; optimism 1",
                    "ACT      value reward 10", "ACT      value reward 10; optimism", "ACT      value reward 0; optimism 1",
                    "ACT      value surprise 10; optimism 1", "ACT      value"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as cm:
                    _g4(ACT_VERBS, bad, OUTCOME)
                self.assertIn("ACT value", str(cm.exception))

    def test_the_verbs_line_still_refuses_what_it_refused(self) -> None:
        with self.assertRaises(GenomeError):
            _g4("ACT      glance 3", OUTCOME)


class TestRegistryAndBounds(unittest.TestCase):
    def test_act_value_has_its_own_runs_row(self) -> None:
        site = genes.RUNS["mind"].get("ACT_VALUE")
        self.assertIsNotNone(site)
        self.assertIn("_maybe_choose_act", site)
        self.assertEqual(genes.unwired(_g4(ACT_VERBS, ACT_VALUE, OUTCOME).declared), [])

    def test_bounds_rows_excluded_with_reasons(self) -> None:
        for key in ("ACT_VALUE.window", "ACT_VALUE.optimism"):
            with self.subTest(key=key):
                self.assertIn(key, genes.BOUNDS)
                self.assertTrue(genes.BOUNDS[key].get("excluded"))
                self.assertTrue(genes.BOUNDS[key]["reason"].strip())
        self.assertEqual(len(genes.MUTABLE_KEYS), 15)


class TestTheRungGenome(unittest.TestCase):
    """§1.1: the rung = A4L-FLOOR.genome + ONE line + one header note — difflib shows exactly those."""

    def test_difflib_shows_exactly_the_line_and_the_note(self) -> None:
        floor = FLOOR.read_text().splitlines()
        rung = RUNG.read_text().splitlines()
        added, removed = [], []
        for op in difflib.SequenceMatcher(a=floor, b=rung, autojunk=False).get_opcodes():
            tag, i1, i2, j1, j2 = op
            if tag in ("replace", "delete"):
                removed.extend(floor[i1:i2])
            if tag in ("replace", "insert"):
                added.extend((j, rung[j]) for j in range(j1, j2))
        self.assertEqual(removed, [])
        self.assertEqual(len(added), 2, added)
        (j_note, note), (j_line, line) = added
        self.assertTrue(note.startswith("# A4L-EXPLORE.genome"), note)
        self.assertEqual(j_note, 1)
        self.assertTrue(line.startswith(ACT_VALUE), line)
        self.assertTrue(rung[j_line - 1].startswith(ACT_VERBS), "the value line sits right after the FLOOR's ACT line")

    def test_rung_parses_and_declares_the_law(self) -> None:
        g = parse_genome(RUNG.read_text())
        self.assertEqual(g.declared["ACT_VALUE"], {"law": "reward", "window": 10, "optimism": 1.0})
        self.assertEqual(genes.unwired(g.declared), [])
        self.assertNotIn("ACT_VALUE", parse_genome(FLOOR.read_text()).declared)


if __name__ == "__main__":
    unittest.main()
