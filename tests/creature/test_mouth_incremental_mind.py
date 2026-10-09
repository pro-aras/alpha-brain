# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B1 (the law SIGNED; SEAT-LINE
# sha256 1d00a35f…; test-first): the mind reads declared["MOUTH"]["incremental"] and hands it to the brain at EVERY
# construction (the birth at Mind.__init__, the resume at Mind.resume) — the clause declares the incremental mouth,
# its absence the old one, nothing else moves.
"""tests/creature/test_mouth_incremental_mind.py — THE MOUTH CLAUSE THROUGH THE MIND (PREREG-ALPHA-6 §1.3).

The tape and the lives are tests/creature/test_voice_mind.py's own (the LEAN body, 120 training scenes, the brain
calibrating at 20, 40 and 80): OFF = DRIVE + the W1 voice spelling; ON = the same + «; incremental». The row-level
pin is the sitting's SAY answers (journaled WHOLE, _answer_ask): ON carries the incremental mechanism's own keys
(n_say/n_readbacks/skipped/added, the read-backs never past the sayable list — the mechanism's bound, live),
OFF the old enumeration's. The organ-level exactness (the turn's and the ask's row field-for-field) is pinned in
tests/genome/test_brain_mouth_incremental.py; here the flag's flow and the life around it."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from genome.machinery import parse_genome
from tests.creature import _scene_tape as S
from tests.creature import test_voice_mind as V

MOUTH_VOICE = V.MOUTH_LINE
MOUTH_INC = V.MOUTH_LINE + "; incremental"
N_TRAIN = V.N_TRAIN
DRIVE_LINE = V.DRIVE_LINE


def lean_text(*lines: str) -> str:
    return V.lean_text(*lines)


def is_turn(r) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "turn"


def is_learn(r) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "learn"


def say_answers(J):
    return [r for r in J if r.get("kind") == "answer" and r.get("form") == "say"
            and isinstance(r.get("answer"), dict) and "raw" in r["answer"]]


class TheSpellingThroughTheMind(unittest.TestCase):
    def test_the_clause_parses_beside_the_voice_clause(self) -> None:
        d = parse_genome(lean_text(DRIVE_LINE, MOUTH_INC)).declared["MOUTH"]
        self.assertEqual(d, {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas",
                             "incremental": True})

    def test_the_mind_reads_the_clause_at_construction(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="mouth-inc-mind-"))
        gp = tmp / "g.genome"
        gp.write_text(lean_text(DRIVE_LINE, MOUTH_INC))
        m = MM.Mind(gp, tmp / "run")
        self.assertTrue(m._mouth_incremental)
        self.assertTrue(m.brain._mouth_incremental)
        m.close()

    def test_undeclared_the_mind_builds_the_old_mouth(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="mouth-inc-mind-"))
        gp = tmp / "g.genome"
        gp.write_text(lean_text(DRIVE_LINE, MOUTH_VOICE))
        m = MM.Mind(gp, tmp / "run")
        self.assertFalse(m._mouth_incremental)
        self.assertFalse(m.brain._mouth_incremental)
        m.close()


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="mouth-inc-lives-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.off, cls.off_root = cls.live(lean_text(DRIVE_LINE, MOUTH_VOICE))
        cls.on, cls.on_root = cls.live(lean_text(DRIVE_LINE, MOUTH_INC))
        cls.J_off, cls.J_on = S.journal(cls.off_root), S.journal(cls.on_root)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, text: str):
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root)
        try:
            for row in cls.rows:
                m.consume(row)
        finally:
            m.close()
        return m, root


class TheRowLevelPin(_Lives):
    def test_the_on_lifes_say_answers_carry_the_mechanisms_own_keys(self) -> None:
        rows = say_answers(self.J_on)
        self.assertGreater(len(rows), 4, "the presence count: the sitting asked the mouth to speak")
        for r in rows:
            raw = r["answer"]["raw"]
            self.assertIn("n_readbacks", raw)
            self.assertIn("n_say", raw)
            self.assertIn("skipped", raw)
            self.assertIn("added", raw)
            self.assertLessEqual(int(raw["n_readbacks"]), len(raw["sayable"]),
                                 "the mechanism's own bound, live: read-backs never past the sayable list")

    def test_the_off_lifes_say_answers_are_the_old_enumerations(self) -> None:
        rows = say_answers(self.J_off)
        self.assertGreater(len(rows), 4, "the presence count")
        for r in rows:
            self.assertNotIn("n_readbacks", r["answer"]["raw"])


class NothingElseMoves(_Lives):
    def test_both_lives_took_every_turn(self) -> None:
        turns_on = [r for r in self.J_on if is_turn(r)]
        turns_off = [r for r in self.J_off if is_turn(r)]
        self.assertGreater(len(turns_on), 100, "the presence count: the brain took its turns")
        self.assertEqual(len(turns_on), len(turns_off))

    def test_the_learn_rows_are_byte_the_two_lives(self) -> None:
        learns_on = [json.dumps(r, sort_keys=True) for r in self.J_on if is_learn(r)]
        learns_off = [json.dumps(r, sort_keys=True) for r in self.J_off if is_learn(r)]
        self.assertEqual(len(learns_on), N_TRAIN)
        self.assertEqual(learns_on, learns_off, "the mouth is read-only: the clause never moves a learn row")

    def test_the_brain_and_the_organism_end_identical(self) -> None:
        self.assertEqual(self.on.brain.state_hash(), self.off.brain.state_hash())
        self.assertEqual(self.on.org.state_hash(), self.off.org.state_hash())

    def test_every_say_row_keeps_the_say_fields_own_keys(self) -> None:
        said = [t for t in self.J_on if is_turn(t) and t["say"] is not None]
        self.assertGreater(len(said), 15, "the presence count (the same tape's brain spoke under both mouths)")
        for t in said:
            self.assertEqual(set(t["say"]), {"hyp", "fix", "pos", "words", "readback", "margin"})


if __name__ == "__main__":
    unittest.main()
