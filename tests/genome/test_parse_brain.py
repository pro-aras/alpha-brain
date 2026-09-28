# edit: Claude (Fable 5.1), 2026-09-28 20:10 +0400 — BRAIN-IN-BODY: the parser pin for the two new lines (BRAIN, WORLD scene).
"""tests/genome/test_parse_brain.py — `BRAIN …` and `WORLD scene …` parse to their declared dicts, refuse BY NAME when
mis-spelt, and leave every older WORLD shape exactly as it was (ALPHA4.genome's own drawn and game lines)."""
from __future__ import annotations

import unittest
from pathlib import Path

from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
ALPHA4 = (ROOT / "genome" / "ALPHA4.genome").read_text()
BRAIN_LINE = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; "
              "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene")
SCENE_LINE = "WORLD    scene seed 20261101; train 10000; sitting fresh s1b1; feed max backlog 8; utterance true"


def with_lines(*lines: str) -> str:
    return ALPHA4 + "\n" + "\n".join(lines) + "\n"


class ParseBrain(unittest.TestCase):
    def test_both_lines_parse_to_their_dicts(self):
        d = parse_genome(with_lines(BRAIN_LINE, SCENE_LINE)).declared
        self.assertEqual(d["BRAIN"], {"lr": 0.01, "eps": 0.3, "none_level": 0.95, "conformal": 0.90, "young": 3,
                                      "calibrate_at": [250, 500, 1000, 2000, 5000, 10000], "replay": "none", "hears": ["scene"]})
        self.assertEqual(d["WORLD_SCENE"], {"seed": 20261101, "train": 10000, "sitting": ["fresh", "s1b1"],
                                            "feed": {"mode": "max", "backlog": 8}, "utterance": "true"})

    def test_control_absent_lines_declare_nothing(self):
        d = parse_genome(ALPHA4).declared
        self.assertNotIn("BRAIN", d)
        self.assertNotIn("WORLD_SCENE", d)

    def test_older_world_shapes_untouched(self):
        before = parse_genome(ALPHA4).declared
        after = parse_genome(with_lines(BRAIN_LINE, SCENE_LINE)).declared
        self.assertIn("WORLD", before)
        self.assertIn("WORLD_GAME", before)
        self.assertEqual(before["WORLD"], after["WORLD"])
        self.assertEqual(before["WORLD_GAME"], after["WORLD_GAME"])
        self.assertEqual({k: v for k, v in after.items() if k not in ("BRAIN", "WORLD_SCENE")}, before)

    def test_scene_variants(self):
        d = parse_genome(with_lines("WORLD scene seed 20261102; train 300; sitting none; feed every 50 ms; utterance shuffled 7")).declared
        self.assertEqual(d["WORLD_SCENE"], {"seed": 20261102, "train": 300, "sitting": [], "feed": {"mode": "every", "ms": 50},
                                            "utterance": {"shuffled": 7}})

    def test_refusals_by_name(self):
        bad = {
            "BRAIN": [BRAIN_LINE.replace("word-map", "wordmap"), BRAIN_LINE.replace("lr 0.01", "lr 0"),
                      BRAIN_LINE.replace("250 500", "500 250"), BRAIN_LINE.replace("young 3", "young 0"),
                      BRAIN_LINE.replace("replay none", "replay surprise"), BRAIN_LINE.replace("hears scene", "hears scene scene"),
                      BRAIN_LINE.replace(" and before a sitting", "")],
            "WORLD scene": [SCENE_LINE.replace("sitting fresh s1b1", "sitting fresh fresh"),
                            SCENE_LINE.replace("sitting fresh s1b1", "sitting exam"), SCENE_LINE.replace("train 10000", "train 0"),
                            SCENE_LINE.replace("backlog 8", "backlog 0"), SCENE_LINE.replace("utterance true", "utterance false"),
                            SCENE_LINE.replace("seed 20261101; ", "")],
        }
        for name, lines in bad.items():
            for line in lines:
                with self.subTest(line=line):
                    with self.assertRaises(GenomeError) as cm:
                        parse_genome(with_lines(line))
                    self.assertTrue(str(cm.exception).startswith(name), str(cm.exception))


if __name__ == "__main__":
    unittest.main()
