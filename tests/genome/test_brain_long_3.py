# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:22 +0400 — PREREG-HEARS-2 §4 + AMENDMENT 1 A1.8: genome/brain/lives/BRAIN-LONG-3.genome is BRAIN-LONG-2.genome with EXACTLY two changes (hears scene maker; the
# calibration list extended past 50000 by the seat's word: every 1,000 learned 51000-200000, then every 5,000 to 300000), parses, and its list is strictly rising; its pre-flight twin differs from it by the
# pre-flight's own two lines (train 400, calibrate at 250). The comparator is run on a planted offender and must see it (the plant asserts it changed the text).
"""tests/genome/test_brain_long_3.py — BRAIN-LONG-3.genome and BRAIN-LONG-3-PREFLIGHT.genome."""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import parse_genome

LIVES = Path(__file__).resolve().parents[2] / "genome" / "brain" / "lives"
LONG2, LONG3 = (LIVES / "BRAIN-LONG-2.genome").read_text(), (LIVES / "BRAIN-LONG-3.genome").read_text()
PRE2, PRE3 = (LIVES / "BRAIN-LONG-2-PREFLIGHT.genome").read_text(), (LIVES / "BRAIN-LONG-3-PREFLIGHT.genome").read_text()
OLD_LIST = [250, 500, 1000, 2000, 5000, 10000, 20000, 50000]
EXTENSION = list(range(51000, 200001, 1000)) + list(range(205000, 300001, 5000))      # the seat's words, 11:0x on 2026-10-03


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


def brain_line(text: str) -> str:
    return next(l for l in code_lines(text) if l.split(None, 1)[0] == "BRAIN")


class Long3(unittest.TestCase):
    def test_it_parses_hears_the_maker_and_the_list_is_strictly_rising(self) -> None:
        b = parse_genome(LONG3).declared["BRAIN"]
        self.assertEqual(b["hears"], ["scene", "maker"])
        at = b["calibrate_at"]
        self.assertTrue(all(x < y for x, y in zip(at, at[1:])), "the calibration list must be strictly rising")
        self.assertEqual(at, OLD_LIST + EXTENSION)
        self.assertEqual((len(at), at[0], at[-1]), (8 + 150 + 20, 250, 300000))

    def test_the_spacing_is_the_seats(self) -> None:
        at = parse_genome(LONG3).declared["BRAIN"]["calibrate_at"]
        past = [x for x in at if x >= 50000]
        gaps = [y - x for x, y in zip(past, past[1:])]
        self.assertEqual(gaps[:150], [1000] * 150)                 # 50000 → 51000 → … → 200000: every 1,000 learned
        self.assertEqual(gaps[150:], [5000] * 20)                  # 200000 → 205000 → … → 300000: every 5,000
        # past 50,000 the maker alone feeds the brain at 8,640 a day: 1,000 learned is 2.8 h, under the maker's 4 h arrivals
        self.assertLess(1000 / 8640 * 24, 4.0)

    def test_the_only_code_line_that_differs_from_long_2_is_the_brain_line_and_only_by_the_two_changes(self) -> None:
        only2, only3 = differing(LONG2, LONG3)
        self.assertEqual(len(only2), 1)
        self.assertEqual(len(only3), 1)
        self.assertEqual(only2[0].split(None, 1)[0], "BRAIN")
        expect = brain_line(LONG2).replace("20000 50000 and before", "20000 50000 " + " ".join(str(n) for n in EXTENSION) + " and before", 1)
        expect = expect.replace("replay none; hears scene", "replay none; hears scene maker", 1)
        self.assertEqual(only3[0], expect)

    def test_the_seed_and_the_scene_world_and_the_drive_are_long_2s(self) -> None:
        g2, g3 = parse_genome(LONG2), parse_genome(LONG3)
        self.assertEqual(g2.declared["WORLD_SCENE"], g3.declared["WORLD_SCENE"])
        self.assertEqual((g3.declared["WORLD_SCENE"]["seed"], g3.declared["WORLD_SCENE"]["train"]), (20261101, 50000))
        self.assertIn("DRIVE", g3.declared)
        self.assertEqual(g2.declared["DRIVE"], g3.declared["DRIVE"])
        # the SEED line is not in `declared` under that name: compare the lines themselves (the one-differing-line test above covers every other line)
        seed3 = next(l for l in code_lines(LONG3) if l.split(None, 1)[0] == "SEED")
        self.assertEqual(seed3, next(l for l in code_lines(LONG2) if l.split(None, 1)[0] == "SEED"))
        self.assertIn("20261101", seed3)

    def test_the_comparator_sees_a_planted_offender(self) -> None:
        seed = LONG3.replace("SEED     20261101", "SEED     20261102", 1)
        self.assertNotEqual(seed, LONG3, "the plant must change the text")
        only_real, only_planted = differing(LONG3, seed)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertTrue(only_real[0].startswith("SEED") and only_planted[0].startswith("SEED"))
        no_maker = LONG3.replace("replay none; hears scene maker", "replay none; hears scene", 1)
        self.assertNotEqual(no_maker, LONG3, "the plant must change the text")
        only_real, only_planted = differing(LONG3, no_maker)
        self.assertEqual((len(only_real), len(only_planted)), (1, 1))
        self.assertIn("hears scene maker", only_real[0])
        self.assertNotIn("hears scene maker", only_planted[0])


class Preflight3(unittest.TestCase):
    def test_it_parses_hears_the_maker_and_calibrates_at_250(self) -> None:
        b = parse_genome(PRE3).declared["BRAIN"]
        self.assertEqual(b["hears"], ["scene", "maker"])
        self.assertEqual(b["calibrate_at"], [250])

    def test_it_differs_from_long_3_by_the_preflights_two_lines_only(self) -> None:
        only_long, only_pre = differing(LONG3, PRE3)
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_long), ["BRAIN", "WORLD"])
        self.assertEqual(sorted(l.split(None, 1)[0] for l in only_pre), ["BRAIN", "WORLD"])
        self.assertIn("train 400", " ".join(only_pre))
        self.assertIn("calibrate at 250 and before a sitting", " ".join(only_pre))
        self.assertIn("hears scene maker", " ".join(only_pre))

    def test_it_differs_from_the_long_2_preflight_by_the_hears_token_alone(self) -> None:
        only2, only3 = differing(PRE2, PRE3)
        self.assertEqual((len(only2), len(only3)), (1, 1))
        self.assertEqual(only3[0], only2[0].replace("hears scene", "hears scene maker", 1))


if __name__ == "__main__":
    unittest.main()
