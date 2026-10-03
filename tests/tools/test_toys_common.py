"""Tests for the TOYS lane's shared pieces: the signed-text pins (a run REFUSES on a text that differs from the signed one).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:33 +0400 — written FIRST (red before tools/toys/common/prereg.py exists).
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.toys.common import prereg as PR

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs" / "research" / "toys"


class TestPrereg(unittest.TestCase):
    def test_the_three_signed_texts_check(self):
        got = PR.check(["cp", "cp_amend1", "nullspace"])
        self.assertEqual(set(got), {"cp", "cp_amend1", "nullspace"})
        self.assertEqual(got["cp"], "726d032918b3a2114ce2d7802865ffd64d3458910106a3af88c21df0c4866900")
        self.assertEqual(got["cp_amend1"], "59181d22d873614674728450a8a3f3a2428784656066577eaae8b8bc8d273448")
        self.assertEqual(got["nullspace"], "d15a6353d6b62e7ba74c407e2a220054c127250c7b4ee07f55d4564bc40ac2ca")

    def test_signature_lines_are_not_part_of_the_signed_text(self):
        d = Path(tempfile.mkdtemp())
        try:
            f = d / "x.md"
            f.write_bytes(b"a\nb\n- Co-signed: someone, a time\n")
            g = d / "y.md"
            g.write_bytes(b"a\nb\n")
            self.assertEqual(PR.signed_sha(f), PR.signed_sha(g))
            h = d / "z.md"
            h.write_bytes(b"a\nb\n- Co-signed: one\n- Co-signed: two\n")
            self.assertEqual(PR.signed_sha(h), PR.signed_sha(g))
        finally:
            shutil.rmtree(d)

    def test_a_planted_edit_to_a_signed_text_is_refused(self):
        d = Path(tempfile.mkdtemp())
        try:
            src = DOCS / "PREREG-TOY-CP.md"
            bad = d / "PREREG-TOY-CP.md"
            text = src.read_bytes()
            self.assertIn(b"0.0056", text)
            bad.write_bytes(text.replace(b"0.0056", b"0.0057", 1))                 # the plant: one character of a bar
            self.assertNotEqual(bad.read_bytes(), text)                             # the plant changed the bytes
            with self.assertRaises(PR.PreregError):
                PR.check(["cp"], root=d)
            ok = d / "PREREG-TOY-CP.md"
            ok.write_bytes(text)
            self.assertEqual(PR.check(["cp"], root=d)["cp"], PR.SIGNED["cp"][1])
        finally:
            shutil.rmtree(d)

    def test_the_frames_text_is_pinned_and_a_planted_edit_of_a_bar_is_refused(self):
        # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:23 +0400 — Toy C's law, co-signed 2026-10-03 12:21 +0400 at ee9fe93; written FIRST (red: no «frames» pin yet).
        want = "a9787ef8026e8e6d8ab41f16d088bb5259f5cf9f5d64de7176da848a2a52c31a"
        self.assertEqual(PR.check(["frames"])["frames"], want)
        d = Path(tempfile.mkdtemp())
        try:
            src = DOCS / "PREREG-TOY-FRAMES.md"
            bad = d / "PREREG-TOY-FRAMES.md"
            text = src.read_bytes()
            self.assertIn(b"G_max + 20", text)
            bad.write_bytes(text.replace(b"G_max + 20", b"G_max + 21", 1))          # the plant: one character of the ceiling gate's tolerance
            self.assertNotEqual(bad.read_bytes(), text)                             # the plant changed the bytes
            with self.assertRaises(PR.PreregError):
                PR.check(["frames"], root=d)
        finally:
            shutil.rmtree(d)

    def test_header_carries_the_signed_shas(self):
        h = PR.header(["cp", "cp_amend1"])
        self.assertEqual(h["prereg_cp_sha256"], PR.SIGNED["cp"][1])
        self.assertEqual(h["prereg_cp_amend1_sha256"], PR.SIGNED["cp_amend1"][1])


if __name__ == "__main__":
    unittest.main()
