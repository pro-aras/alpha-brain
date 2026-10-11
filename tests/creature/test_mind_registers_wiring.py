# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 19:2x +0400 — PREREG-BRAIN-LONG-6 §2 B3
# (the law SIGNED; SEAT-LINE sha256 2c6bb22b…; test-first): the Mind's self-wiring from
# declared["REGISTERS"] — the tri-state flags. None (every caller today) = read the genome's declaration
# (ABSENT = False, byte-identical for every genome on disk); explicit True/False = the caller's own word
# (the benches' form). The resume classmethod's declared read governs a resumed mind alike.
"""tests/creature/test_mind_registers_wiring.py — the REGISTERS self-wiring (PREREG-BRAIN-LONG-6 §1.3/§2 B3)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind

_ROOT = Path(__file__).resolve().parents[2]
_LEAN = (_ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()

_LINE = "REGISTERS content-web muse precision\n"


def _genome(text: str = "") -> Path:
    p = Path(tempfile.mkdtemp()) / "toy.genome"
    p.write_text(_LEAN + ("\n" + text if text else ""))
    return p


class TestRegistersWiring(unittest.TestCase):
    def test_no_line_means_off(self) -> None:
        """ABSENT (every genome on disk): all three registers OFF — the byte-identical form."""
        m = Mind(_genome(), Path(tempfile.mkdtemp()))
        self.assertFalse(m.precision)
        self.assertFalse(m.muse)
        self.assertFalse(m.content_web)

    def test_the_line_arms_all_three(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertTrue(m.precision)
        self.assertTrue(m.muse)
        self.assertTrue(m.content_web)

    def test_a_subset_line(self) -> None:
        m = Mind(_genome("REGISTERS muse\n"), Path(tempfile.mkdtemp()))
        self.assertFalse(m.precision)
        self.assertTrue(m.muse)
        self.assertFalse(m.content_web)

    def test_explicit_false_overrides_the_line(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), precision=False, muse=False, content_web=False)
        self.assertFalse(m.precision)
        self.assertFalse(m.muse)
        self.assertFalse(m.content_web)

    def test_explicit_true_overrides_absence(self) -> None:
        m = Mind(_genome(), Path(tempfile.mkdtemp()), precision=True, muse=True, content_web=True)
        self.assertTrue(m.precision)
        self.assertTrue(m.muse)
        self.assertTrue(m.content_web)

    def test_resume_reads_the_same_declaration(self) -> None:
        """The resume classmethod (no snapshot → a fresh mind through __init__'s own read): the line
        governs a resumed mind exactly as a born one; explicit False overrides there too."""
        m, seq = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertEqual(seq, 0, "presence: the empty root resumes fresh")
        self.assertTrue(m.precision)
        self.assertTrue(m.muse)
        self.assertTrue(m.content_web)
        m2, _ = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()), muse=False, content_web=False)
        self.assertFalse(m2.muse)
        self.assertFalse(m2.content_web)
        self.assertTrue(m2.precision, "an override names its flag and no other")

    def test_the_predictor_follows_the_declaration(self) -> None:
        """The init's Predictor build threads precision from the same read (N1's own line, moved only)."""
        lean_with_predict = _LEAN + "\nPREDICT next glance; error scales delta 0.5..2.0; ranks replay; grades act\n"
        p = Path(tempfile.mkdtemp()) / "toy.genome"
        p.write_text(lean_with_predict + "\n" + "REGISTERS precision\n")
        m = Mind(p, Path(tempfile.mkdtemp()))
        self.assertIsNotNone(m.predictor, "presence: the genome declares PREDICT")
        self.assertTrue(m.predictor.precision)


if __name__ == "__main__":
    unittest.main()
