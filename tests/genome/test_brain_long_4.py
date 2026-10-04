# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-05 01:40 +0400 — Decision 6 of the WHOLE-ORGANISM design (DECIDED, standing):
# genome/brain/lives/BRAIN-LONG-4.genome is BRAIN-LONG-3.genome with EXACTLY one change — the MOUTH line in the W1 spelling
# (PREREG-W1-MOUTH-VOICES-BRAIN §2, landed at master 5b0942c): «say one frame per think and the brain's phrase per canvas;
# journaled» — made by tools/brain/voice_genome.py (one text line, every other parsed key equal). Its pre-flight twin
# differs from it by the pre-flight's own two lines (train 400, calibrate at 250). The comparator runs on planted offenders
# and must see them (each plant asserts it changed the text). The refusals (a misspelt clause; the clause beside no DRIVE)
# fire by name. The poller fix comes free (master since 0ede0a8 carries it; bl3 launched on d2fe75b).
"""tests/genome/test_brain_long_4.py — BRAIN-LONG-4.genome and BRAIN-LONG-4-PREFLIGHT.genome."""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

LIVES = Path(__file__).resolve().parents[2] / "genome" / "brain" / "lives"
LONG3, LONG4 = (LIVES / "BRAIN-LONG-3.genome").read_text(), (LIVES / "BRAIN-LONG-4.genome").read_text()
PRE3, PRE4 = (LIVES / "BRAIN-LONG-3-PREFLIGHT.genome").read_text(), (LIVES / "BRAIN-LONG-4-PREFLIGHT.genome").read_text()
OLD_MOUTH = "MOUTH    say one frame per think; journaled"
NEW_MOUTH = "MOUTH    say one frame per think and the brain's phrase per canvas; journaled"
OLD_DICT = {"say": "one frame per think", "journaled": True}
NEW_DICT = {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"}


def code_lines(text: str):
    """Every non-comment line with its trailing comment cut off."""
    out = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        out.append(line.split("#", 1)[0].rstrip())
    return out


def differing(a: str, b: str):
    """The code lines in one text and not the other, as (only in a, only in b)."""
    ca, cb = code_lines(a), code_lines(b)
    return [l for l in ca if l not in cb], [l for l in cb if l not in ca]


def one_line_of(text: str, gene: str) -> str:
    return next(l for l in code_lines(text) if l.split(None, 1)[0] == gene)


class Long4(unittest.TestCase):
    def test_it_parses_and_carries_exactly_the_one_new_key(self) -> None:
        self.assertEqual(parse_genome(LONG4).declared["MOUTH"], NEW_DICT)

    def test_the_only_code_line_that_differs_from_long_3_is_the_mouth_line_and_only_by_the_clause(self) -> None:
        only3, only4 = differing(LONG3, LONG4)
        self.assertEqual((len(only3), len(only4)), (1, 1))
        self.assertEqual(only3[0], OLD_MOUTH)
        self.assertEqual(only4[0], NEW_MOUTH)
        self.assertEqual(only4[0], one_line_of(LONG3, "MOUTH").replace("per think;", "per think and the brain's phrase per canvas;", 1))

    def test_everything_else_is_long_3s(self) -> None:
        g3, g4 = parse_genome(LONG3), parse_genome(LONG4)
        self.assertEqual({k: v for k, v in g4.declared.items() if k != "MOUTH"},
                         {k: v for k, v in g3.declared.items() if k != "MOUTH"})
        b = g4.declared["BRAIN"]
        self.assertEqual(b["hears"], ["scene", "maker"])
        self.assertTrue(all(x < y for x, y in zip(b["calibrate_at"], b["calibrate_at"][1:])), "the list stays strictly rising")
        self.assertEqual(g3.declared["DRIVE"], g4.declared["DRIVE"])
        self.assertEqual(g3.declared["SLEEP"], g4.declared["SLEEP"])
        self.assertEqual(one_line_of(LONG3, "SEED"), one_line_of(LONG4, "SEED"))
        self.assertIn("DRIVE", g4.declared, "the voice's own precondition (the clause beside no DRIVE is refused)")

    def test_a_misspelt_clause_refuses_by_name(self) -> None:
        bad = LONG4.replace("the brain's phrase per canvas", "the brains phrase per canvas", 1)
        self.assertNotEqual(bad, LONG4, "the plant must change the text")
        with self.assertRaises(GenomeError) as e:
            parse_genome(bad)
        self.assertIn("MOUTH", str(e.exception))

    def test_the_clause_beside_no_drive_refuses_at_the_minds_start_by_name(self) -> None:
        text, n = re.subn(r"^DRIVE    .*\n", "", LONG4, count=1, flags=re.M)
        self.assertEqual(n, 1, "bl4 carries one DRIVE line")
        tmp = Path(tempfile.mkdtemp(prefix="bl4-refusal-"))
        gp = tmp / "g.genome"
        gp.write_text(text)
        from creature.mind import Mind
        with self.assertRaises(GenomeError) as e:
            Mind(gp, tmp / "run")
        self.assertIn("the phrase is the DRIVE turn's", str(e.exception))

    def test_the_comparator_sees_a_planted_offender(self) -> None:
        old_spelling = LONG4.replace(NEW_MOUTH, OLD_MOUTH, 1)
        self.assertNotEqual(old_spelling, LONG4, "the plant must change the text")
        only_real, only_planted = differing(LONG4, old_spelling)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertEqual(only_real[0], NEW_MOUTH)
        self.assertEqual(only_planted[0], OLD_MOUTH)
        seeded = LONG4.replace("SEED     20261101", "SEED     20261102", 1)
        self.assertNotEqual(seeded, LONG4, "the plant must change the text")
        only_real, only_planted = differing(LONG4, seeded)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertTrue(only_real[0].startswith("SEED") and only_planted[0].startswith("SEED"))


class Preflight4(unittest.TestCase):
    def test_it_parses_calibrates_at_250_and_carries_the_clause(self) -> None:
        g = parse_genome(PRE4)
        self.assertEqual(g.declared["MOUTH"], NEW_DICT)
        self.assertEqual(g.declared["BRAIN"]["calibrate_at"], [250])
        self.assertEqual(g.declared["BRAIN"]["hears"], ["scene", "maker"])

    def test_it_differs_from_long_4_by_the_preflights_two_lines_only(self) -> None:
        only_long, only_pre = differing(LONG4, PRE4)
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_long), ["BRAIN", "WORLD"])
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_pre), ["BRAIN", "WORLD"])
        self.assertIn("train 400", " ".join(only_pre))
        self.assertIn("calibrate at 250 and before a sitting", " ".join(only_pre))

    def test_it_differs_from_the_long_3_preflight_by_the_mouth_line_alone(self) -> None:
        only3, only4 = differing(PRE3, PRE4)
        self.assertEqual((len(only3), len(only4)), (1, 1))
        self.assertEqual(only3[0], OLD_MOUTH)
        self.assertEqual(only4[0], NEW_MOUTH)


if __name__ == "__main__":
    unittest.main()
