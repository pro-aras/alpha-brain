# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §2.1 + AMENDMENT 1
# (the law SIGNED; SEAT-LINE-H0.txt sha256 edda32e7…; test-first): the Mind's self-wiring from
# declared["HOMEOSTASIS"] — the tri-state drives. None (every caller today) = read the genome's
# declaration (ABSENT = no drives, byte-identical for every genome on disk); True = the full three (the
# benches' form); a dict = the solo arms; False = off; homeostasis_flat = the flat twin. The resume
# classmethod's declared read governs a resumed mind alike, and a snapshot's drives.json restores the
# state EXACTLY across a resume.
"""tests/creature/test_homeostasis_wiring.py — the HOMEOSTASIS self-wiring (PREREG-HOMEOSTASIS §2.1/A1).
Modeled whole on test_mind_registers_wiring.py (the REGISTERS precedent)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind

_ROOT = Path(__file__).resolve().parents[2]
_LEAN = (_ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()

_LINE = "HOMEOSTASIS arousal boredom fatigue\n"


def _genome(text: str = "") -> Path:
    p = Path(tempfile.mkdtemp()) / "toy.genome"
    p.write_text(_LEAN + ("\n" + text if text else ""))
    return p


class TestHomeostasisWiring(unittest.TestCase):
    def test_no_line_means_no_drives(self) -> None:
        """ABSENT (every genome on disk): no drives object at all — the byte-identical form."""
        m = Mind(_genome(), Path(tempfile.mkdtemp()))
        self.assertIsNone(m._drives)
        self.assertIsNone(m.predictor.homeostasis if m.predictor is not None else None,
                          "the predictor's gain path stays untouched without the declaration")

    def test_the_line_arms_all_three(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"arousal": True, "boredom": True, "fatigue": True})
        if m.predictor is not None:
            self.assertIs(m.predictor.homeostasis, m._drives, "the gains ride the SAME drives object")

    def test_a_subset_line(self) -> None:
        m = Mind(_genome("HOMEOSTASIS boredom\n"), Path(tempfile.mkdtemp()))
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"boredom": True})
        self.assertEqual(m._drives.gains(), (1.0, 1.0), "arousal/fatigue undeclared: the gains are neutral")

    def test_explicit_false_overrides_the_line(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), homeostasis=False)
        self.assertIsNone(m._drives)

    def test_explicit_true_overrides_absence(self) -> None:
        m = Mind(_genome(), Path(tempfile.mkdtemp()), homeostasis=True)
        self.assertIsNotNone(m._drives)
        self.assertEqual(set(m._drives.declared), {"arousal", "boredom", "fatigue"})

    def test_a_dict_is_a_solo_arm(self) -> None:
        m = Mind(_genome(), Path(tempfile.mkdtemp()), homeostasis={"arousal": True})
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.declared, {"arousal": True})

    def test_the_flat_twin_is_pinned(self) -> None:
        m = Mind(_genome(_LINE), Path(tempfile.mkdtemp()), homeostasis_flat=True)
        self.assertIsNotNone(m._drives)
        self.assertEqual(m._drives.a, 0.5)
        m._drives.note_canvas(0.99, source="scene")
        self.assertEqual((m._drives.a, m._drives.b, m._drives.f), (0.5, 0.0, 0.0),
                         "the flat twin's state never moves (H-DRIVE-EFFECT's baseline)")

    def test_resume_reads_the_same_declaration(self) -> None:
        """The resume classmethod (no snapshot → a fresh mind through __init__'s own read): the line
        governs a resumed mind exactly as a born one; explicit False overrides there too."""
        m, seq = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()))
        self.assertEqual(seq, 0, "presence: the empty root resumes fresh")
        self.assertIsNotNone(m._drives)
        m2, _ = Mind.resume(_genome(_LINE), Path(tempfile.mkdtemp()))
        m2._drives = None  # the override form is the constructor's; the resume's declared read stands
        m3, _ = Mind.resume(_genome(), Path(tempfile.mkdtemp()))
        self.assertIsNone(m3._drives)

    def test_the_state_survives_a_snapshot_round_trip(self) -> None:
        """A resume restores the drives EXACTLY (PREREG-HOMEOSTASIS §2.2's persistence clause): snapshot
        writes state/drives.json when declared; resume loads it back onto the rebuilt drives."""
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome(_LINE), root)
        self.assertIsNotNone(m._drives)
        for e in (0.9, 0.2, 0.4, 0.7):
            m._drives.note_canvas(e, source="scene")
        before = m._drives.to_json()
        m.snapshot()
        drives_file = root / "state" / "drives.json"
        self.assertTrue(drives_file.exists(), "presence: the snapshot carries drives.json when declared")
        m2, _ = Mind.resume(_genome(_LINE), root)
        self.assertIsNotNone(m2._drives)
        self.assertEqual(m2._drives.to_json(), before, "the drives restore exactly across the resume")

    def test_no_drives_file_without_the_line(self) -> None:
        """The OFF form: no drives.json is ever staged (the additive file exists only when declared —
        the web.json precedent)."""
        root = Path(tempfile.mkdtemp())
        m = Mind(_genome(), root)
        m.snapshot()
        self.assertFalse((root / "state" / "drives.json").exists())


if __name__ == "__main__":
    unittest.main()
