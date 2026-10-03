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

    def test_the_frames_amendment_is_pinned_and_a_planted_edit_of_its_gate_is_refused(self):
        # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:20 +0400 — Toy C's AMENDMENT-1 (the PLANT gate, the plant's second token, the memory price, the readings), text at d94392b, co-signed by the
        # architect 17:17 (d830146) and signed by the seat 17:19 (27edde2); written FIRST (red: no «frames_amend1» pin yet).
        want = "158660bbfe6a1fd0c551dabc1308dbd4f89fc90a07fd9c58d19e163e9b4abce0"
        got = PR.check(["frames", "frames_amend1"])
        self.assertEqual(got["frames_amend1"], want)
        self.assertEqual(got["frames"], "a9787ef8026e8e6d8ab41f16d088bb5259f5cf9f5d64de7176da848a2a52c31a")      # the base law's pin is untouched
        d = Path(tempfile.mkdtemp())
        try:
            src = DOCS / "PREREG-TOY-FRAMES-AMEND-1.md"
            bad = d / "PREREG-TOY-FRAMES-AMEND-1.md"
            text = src.read_bytes()
            self.assertIn(b"> 0 on that stream", text)
            bad.write_bytes(text.replace(b"> 0 on that stream", b"> 1 on that stream", 1))                  # the plant: the threshold of gate (B)
            self.assertNotEqual(bad.read_bytes(), text)                                                         # the plant changed the bytes
            with self.assertRaises(PR.PreregError):
                PR.check(["frames_amend1"], root=d)
            # a signature line moves nothing: the seat's line is dropped like the architect's
            ok = d / "PREREG-TOY-FRAMES-AMEND-1.md"
            ok.write_bytes(text + b"Signed: someone else, later\n")
            self.assertEqual(PR.check(["frames_amend1"], root=d)["frames_amend1"], want)
        finally:
            shutil.rmtree(d)
        h = PR.header(["frames", "frames_amend1"])
        self.assertEqual(h["prereg_frames_amend1_sha256"], want)

    def test_both_families_of_signature_lines_are_dropped(self):
        # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 15:45 +0400 — Toy D's law (the architect's) signs with «Signed:» / «Co-signed:» at the line start, the toys laws with «- Co-signed:»;
        # written FIRST (red: the second family is not yet dropped). The seat's signature REPLACES the placeholder line «Signed: the seat — pending.» — both are dropped, so it cannot move the sha.
        d = Path(tempfile.mkdtemp())
        try:
            base = d / "base.md"
            base.write_bytes(b"a\nb\n")
            sig = d / "sig.md"
            sig.write_bytes(b"a\nb\nSigned: the author, 15:35\nCo-signed: the builder, pending\n- Signed: x\n- Co-signed: y\nSigned: the seat \xe2\x80\x94 pending.\n")
            self.assertEqual(PR.signed_sha(sig), PR.signed_sha(base))
            swapped = d / "swapped.md"
            swapped.write_bytes(b"a\nb\nSigned: the author, 15:35\nCo-signed: the builder, 15:50\nSigned: the seat, 15:59 (the placeholder replaced)\n")
            self.assertEqual(PR.signed_sha(swapped), PR.signed_sha(base))
        finally:
            shutil.rmtree(d)

    def test_a_body_line_beginning_signed_without_the_colon_stays_in_the_text(self):
        d = Path(tempfile.mkdtemp())
        try:
            base = d / "base.md"
            base.write_bytes(b"a\nb\n")
            body = d / "body.md"
            body.write_bytes(b"a\nSigned off by the whole team.\nb\n")                  # prose, no colon: part of the law
            self.assertNotEqual(PR.signed_sha(body), PR.signed_sha(base))
            caps = d / "caps.md"
            caps.write_bytes(b"a\nb\nSIGNED:\n")                                          # the laws' own all-caps header stays inside the signed text (case-sensitive)
            self.assertNotEqual(PR.signed_sha(caps), PR.signed_sha(base))
            mid = d / "mid.md"
            mid.write_bytes(b"a\n  Signed: indented text is not a signature line\nb\n")
            self.assertNotEqual(PR.signed_sha(mid), PR.signed_sha(base))
        finally:
            shutil.rmtree(d)

    def test_the_four_pinned_shas_do_not_move_under_the_wider_rule(self):
        got = PR.check(["cp", "cp_amend1", "nullspace", "frames"])
        self.assertEqual(got["frames"], "a9787ef8026e8e6d8ab41f16d088bb5259f5cf9f5d64de7176da848a2a52c31a")
        for name in ("PREREG-TOY-CP.md", "PREREG-TOY-CP-AMEND-1.md", "PREREG-TOY-NULLSPACE.md", "PREREG-TOY-FRAMES.md"):
            lines = (DOCS / name).read_bytes().split(b"\n")
            for ln in lines:
                self.assertFalse(ln.startswith((b"Signed:", b"Co-signed:", b"- Signed:")), (name, ln[:60]))      # no existing law has a line the wider rule would newly drop

    def test_header_carries_the_signed_shas(self):
        h = PR.header(["cp", "cp_amend1"])
        self.assertEqual(h["prereg_cp_sha256"], PR.SIGNED["cp"][1])
        self.assertEqual(h["prereg_cp_amend1_sha256"], PR.SIGNED["cp_amend1"][1])


if __name__ == "__main__":
    unittest.main()
