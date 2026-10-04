# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 19:04 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §3 (the ON genomes are
# «made by a tool that refuses any other difference, as tools/brain/drive_genome.py does»), test-first.
"""tests/tools/test_voice_genome.py — the W1 ON-genome tool: a DRIVE genome plus the MOUTH clause, nothing else.

The lean lives' ON genome uncomments the `#OFF MOUTH …` line in the new spelling; the full life's replaces its active
MOUTH line by it. The tool refuses: an existing --out, a source with no MOUTH line in the old spelling (active or #OFF),
a source already carrying the clause, and any two parsed genomes that would differ in more than the MOUTH key."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "brain" / "voice_genome.py"
LIVES = ROOT / "genome" / "brain" / "lives"
NEW = "say one frame per think and the brain's phrase per canvas; journaled"
OLD = "say one frame per think; journaled"


def run_tool(src: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TOOL), "--in", str(src), "--out", str(out)],
                          capture_output=True, text=True, cwd=ROOT)


class TheLeanOnGenome(unittest.TestCase):
    def test_uncomments_mouth_in_the_new_spelling_and_nothing_else_moves(self) -> None:
        src = LIVES / "BRAIN-LEAN-DRIVE-20261101.genome"
        out = Path(tempfile.mkdtemp()) / "on.genome"
        r = run_tool(src, out)
        self.assertEqual(r.returncode, 0, r.stderr)
        old_lines, new_lines = src.read_text().splitlines(), out.read_text().splitlines()
        self.assertEqual(len(old_lines), len(new_lines))
        diff = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
        self.assertEqual(len(diff), 1, "exactly one text line differs")
        i = diff[0]
        self.assertIn("#OFF MOUTH", old_lines[i])
        self.assertTrue(new_lines[i].startswith("MOUTH    say one frame per think and the brain's phrase per canvas; journaled"))
        g0, g1 = parse_genome(src.read_text()), parse_genome(out.read_text())
        self.assertNotIn("MOUTH", g0.declared)
        self.assertEqual(g1.declared.pop("MOUTH"), {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"})
        self.assertEqual(g0.declared, g1.declared, "every other parsed key is what it was")
        self.assertIn("DRIVE", g1.declared, "the ON genome keeps the DRIVE line")


class TheFullOnGenome(unittest.TestCase):
    def test_replaces_the_active_mouth_line_and_nothing_else_moves(self) -> None:
        src = LIVES / "BRAIN-FULL-DRIVE-20261102.genome"
        out = Path(tempfile.mkdtemp()) / "on.genome"
        r = run_tool(src, out)
        self.assertEqual(r.returncode, 0, r.stderr)
        old_lines, new_lines = src.read_text().splitlines(), out.read_text().splitlines()
        diff = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
        self.assertEqual(len(diff), 1)
        i = diff[0]
        self.assertTrue(old_lines[i].startswith("MOUTH"), old_lines[i])
        self.assertNotIn("#OFF", old_lines[i].split("#")[0])
        self.assertTrue(new_lines[i].startswith("MOUTH    say one frame per think and the brain's phrase per canvas; journaled"))
        g0, g1 = parse_genome(src.read_text()), parse_genome(out.read_text())
        self.assertEqual(g0.declared["MOUTH"], {"say": "one frame per think", "journaled": True})
        self.assertEqual(g1.declared["MOUTH"], {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"})
        d0, d1 = dict(g0.declared), dict(g1.declared)
        d0.pop("MOUTH"), d1.pop("MOUTH")
        self.assertEqual(d0, d1)


class TheRefusals(unittest.TestCase):
    def test_refuses_an_existing_out(self) -> None:
        src = LIVES / "BRAIN-LEAN-DRIVE-20261101.genome"
        out = Path(tempfile.mkdtemp()) / "on.genome"
        out.write_text("here\n")
        self.assertEqual(run_tool(src, out).returncode, 2)

    def test_refuses_a_source_already_carrying_the_clause(self) -> None:
        src = LIVES / "BRAIN-LEAN-DRIVE-20261101.genome"
        out = Path(tempfile.mkdtemp()) / "on.genome"
        self.assertEqual(run_tool(src, out).returncode, 0)
        self.assertEqual(run_tool(out, Path(tempfile.mkdtemp()) / "on2.genome").returncode, 2)

    def test_refuses_a_source_with_no_mouth_line_in_the_old_spelling(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        src = tmp / "g.genome"
        text = (LIVES / "BRAIN-LEAN-DRIVE-20261101.genome").read_text()
        bad = text.replace("say one frame per think; journaled", "say one frame per think; journald")
        self.assertNotEqual(bad, text)
        src.write_text(bad)
        self.assertEqual(run_tool(src, tmp / "on.genome").returncode, 2)


if __name__ == "__main__":
    unittest.main()
