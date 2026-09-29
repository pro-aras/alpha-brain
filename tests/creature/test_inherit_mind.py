# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:34 +0400 — PREREG-INHERIT §3 / §5 (I5, I6, I7's state half), test-first (red on master c22b70c: no inheritance).
"""tests/creature/test_inherit_mind.py — a newborn takes its parent's brain from <root>/inherit/brain.{json,npz}.

A PARENT lives the lean body on one fixture tape (120 scenes). Its saved brain is placed in a CHILD's root. The child is
born knowing (its brain holds the parent's words before its first row), cites nothing of the parent, journals one inherit
row, and a life with no inherit folder is unchanged."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from genome.brain import Brain, BrainError
from tests.creature import _scene_tape as S

ROOT = Path(__file__).resolve().parents[2]
LEAN = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
AT = "calibrate at 250 500 1000 2000 5000 10000"
N_TRAIN = 120


def lean_text(young: str = "young 3 nearest") -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), LEAN, count=1, flags=re.M)
    assert text != LEAN and text.count(AT) == 1 and text.count("young 3 nearest; " + AT) == 1
    return text.replace("young 3 nearest; " + AT, young + "; calibrate at 20 40 80") + "\n"


class InheritMind(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="inherit-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        # the parent lives the whole tape; its brain is saved as the pair
        cls.parent, cls.parent_root = cls.live(lean_text())
        cls.pair = cls.tmp / "pair"
        cls.pair.mkdir()
        cls.parent.brain.save(cls.pair / "brain")
        cls.parent_learned = cls.parent.brain.n_learned
        cls.parent_words = sorted(cls.parent.brain.L.words)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def new_root(cls, pair: Path = None) -> Path:
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        if pair is not None:
            (root / "inherit").mkdir()
            for ext in ("json", "npz"):
                shutil.copy(pair / f"brain.{ext}", root / "inherit" / f"brain.{ext}")
        return root

    @classmethod
    def mind(cls, root: Path, text: str):
        gp = root.parent / "g.genome"
        gp.write_text(text)
        return MM.Mind(gp, root)

    @classmethod
    def live(cls, text: str, pair: Path = None, rows=None):
        root = cls.new_root(pair)
        m = cls.mind(root, text)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root

    # -- born knowing ---------------------------------------------------------------------------
    def test_the_parent_learned_something(self):
        self.assertGreaterEqual(self.parent_learned, N_TRAIN)
        self.assertGreater(len(self.parent_words), 5)
        self.assertGreater(sum(len(v) for v in self.parent.brain.episodes.values()), 0, "the parent cites episodes")

    def test_a_child_is_born_with_the_parents_words_before_its_first_row(self):
        m = self.mind(self.new_root(self.pair), lean_text())
        try:
            self.assertEqual(sorted(m.brain.L.words), self.parent_words)
            self.assertEqual(m.brain.n_learned, self.parent_learned)
            self.assertEqual(m.brain.n_calibrations, self.parent.brain.n_calibrations)
            self.assertEqual(m.brain.episodes, {}, "a child cites nothing it did not live")
            st = m.brain_status()
            self.assertEqual(st["inherited"]["learned"], self.parent_learned)
            self.assertEqual(len(st["inherited"]["hash"]), 64)
        finally:
            m.close()

    def test_a_blank_birth_carries_no_inherited_field_and_no_word(self):
        m = self.mind(self.new_root(), lean_text())
        try:
            self.assertEqual(list(m.brain.L.words), [])
            self.assertNotIn("inherited", m.brain_status())
        finally:
            m.close()

    def test_the_child_learns_on_top_and_journals_one_inherit_row(self):
        m, root = self.live(lean_text(), pair=self.pair)
        J = S.journal(root)
        rows = [r for r in J if r.get("kind") == "inherit"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["learned"], self.parent_learned)
        self.assertEqual(m.brain.n_learned, self.parent_learned + N_TRAIN)
        self.assertEqual(J.index(rows[0]), 0, "the inherit row is the life's first journal row")
        own = [e for v in m.brain.episodes.values() for e in v]
        self.assertGreater(len(own), 0)
        self.assertTrue(all(int(e[0]) >= self.parent_learned for e in own), "every cited episode is one the child lived")

    # -- I5: a life with no inherit folder is unchanged -----------------------------------------
    def test_a_life_without_the_folder_equals_the_parents_own_life(self):
        _, root = self.live(lean_text())
        self.assertEqual(S.journal(root), S.journal(self.parent_root))

    # -- I6: refusals, each plant asserting it changed the bytes --------------------------------
    def test_a_pair_with_one_byte_changed_refuses_by_name(self):
        bad = self.tmp / "bad-byte"
        shutil.copytree(self.pair, bad)
        p = bad / "brain.npz"
        b = bytearray(p.read_bytes())
        i = len(b) // 2
        b[i] ^= 0xFF
        p.write_bytes(bytes(b))
        self.assertNotEqual(p.read_bytes(), (self.pair / "brain.npz").read_bytes())
        with self.assertRaises(Exception) as cm:
            self.mind(self.new_root(bad), lean_text())
        self.assertIn("inherit", str(cm.exception).lower())

    def test_a_pair_under_another_brain_line_refuses_by_name(self):
        with self.assertRaises(Exception) as cm:
            self.mind(self.new_root(self.pair), lean_text(young="young 3"))
        self.assertIn("inherit", str(cm.exception).lower())

    def test_half_a_pair_refuses_by_name(self):
        half = self.tmp / "half"
        half.mkdir()
        shutil.copy(self.pair / "brain.json", half / "brain.json")
        root = self.new_root()
        (root / "inherit").mkdir()
        shutil.copy(half / "brain.json", root / "inherit" / "brain.json")
        with self.assertRaises(Exception) as cm:
            self.mind(root, lean_text())
        self.assertIn("inherit", str(cm.exception).lower())

    # -- I7's state half: a resume keeps the inheritance ----------------------------------------
    def test_a_resumed_child_keeps_its_inherited_count(self):
        k = len(self.rows) // 2
        root = self.new_root(self.pair)
        m = self.mind(root, lean_text())
        try:
            for row in self.rows[:k]:
                m.consume(row)
            m.snapshot()
            learned = m.brain.n_learned
        finally:
            m.close()
        m2, _ = MM.Mind.resume(root.parent / "g.genome", root)
        try:
            self.assertTrue(m2.brain_restored)
            self.assertEqual(m2.brain.n_learned, learned)
            self.assertEqual(m2.brain_status()["inherited"]["learned"], self.parent_learned)
        finally:
            m2.close()


if __name__ == "__main__":
    unittest.main()
