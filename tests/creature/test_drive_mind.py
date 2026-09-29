# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:30 +0400 — PREREG-BRAIN-DRIVES §2.1 / §2.4 / §2.5, test-first (red on master 262cc20: no gene DRIVE).
"""tests/creature/test_drive_mind.py — the gene DRIVE in the MIND: the brain takes its turn at every canvas it hears.

One fixture tape of the scene world (120 training scenes + a sitting), lived by the LEAN body (genome/brain/BRAIN-LEAN.genome,
its brain calibrating at 20, 40 and 80 scenes so that it speaks inside the fixture) OFF and ON, and by the FULL organism
(tests/creature/_scene_tape.py's ALPHA4 text + the BRAIN line) OFF and ON."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import creature.mind as MM
from genome.machinery import GenomeError, parse_genome
from tests.creature import _scene_tape as S

ROOT = Path(__file__).resolve().parents[2]
LEAN = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
DRIVE_LINE = "DRIVE    brain turn before hearing; says 1; asks 1"
AT = "calibrate at 250 500 1000 2000 5000 10000"
N_TRAIN = 120


def lean_text(drive: str = "", brain: bool = True) -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), LEAN, count=1, flags=re.M)
    assert text != LEAN and text.count(AT) == 1
    text = text.replace(AT, "calibrate at 20 40 80")
    if not brain:
        text, n = re.subn(r"^BRAIN    .*$", "", text, count=1, flags=re.M)
        assert n == 1
    return text + "\n" + (drive + "\n" if drive else "")


def full_text(drive: str = "") -> str:
    text = S.genome_text(brain=True, train=N_TRAIN)
    assert text.count(AT) == 1
    return text.replace(AT, "calibrate at 20 40 80") + "\n" + (drive + "\n" if drive else "")


def is_turn(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "turn"


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="drive-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.off, cls.off_root = cls.live(lean_text())
        cls.on, cls.on_root = cls.live(lean_text(DRIVE_LINE))
        cls.J_off, cls.J_on = S.journal(cls.off_root), S.journal(cls.on_root)
        cls.turns = [r for r in cls.J_on if is_turn(r)]

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, text: str, rows=None, blind=frozenset()):
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root, blind=blind)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root


class TheLine(unittest.TestCase):
    def test_parses_to_its_two_values(self) -> None:
        self.assertEqual(parse_genome(lean_text(DRIVE_LINE)).declared["DRIVE"], {"says": 1, "asks": 1})
        self.assertEqual(parse_genome(lean_text("DRIVE    brain turn before hearing; says 0; asks 1")).declared["DRIVE"],
                         {"says": 0, "asks": 1})
        self.assertNotIn("DRIVE", parse_genome(lean_text()).declared)

    def test_any_other_word_refuses_by_name(self) -> None:
        for bad in ("DRIVE    brain turn before hearing; says 2; asks 1", "DRIVE    brain turn before hearing; says 1",
                    "DRIVE    brain turn after hearing; says 1; asks 1", "DRIVE    cells turn before hearing; says 1; asks 1",
                    "DRIVE    brain turn before hearing; says 1; asks yes", "DRIVE    brain"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(lean_text(bad))
                self.assertIn("DRIVE", str(e.exception))

    def test_the_one_difference(self) -> None:
        a, b = parse_genome(lean_text()).declared, parse_genome(lean_text(DRIVE_LINE)).declared
        self.assertEqual({k: v for k, v in b.items() if k != "DRIVE"}, a)

    def test_the_registry_names_its_call_site(self) -> None:
        from creature import genes
        self.assertEqual(genes.unwired(parse_genome(lean_text(DRIVE_LINE)).declared), [])


class TheBrainTakesItsTurn(_Lives):
    def test_off_there_is_no_turn_row(self) -> None:
        self.assertEqual(sum(is_turn(r) for r in self.J_off), 0)
        self.assertGreater(sum(r.get("act") == "learn" for r in self.J_off), 100, "the presence count: the brain learned")

    def test_on_one_turn_row_stands_before_each_learn_row(self) -> None:
        learns = [i for i, r in enumerate(self.J_on) if r.get("kind") == "brain" and r.get("act") == "learn"]
        self.assertEqual(len(learns), N_TRAIN)
        self.assertEqual(len(self.turns), N_TRAIN)
        for i in learns:
            t, l = self.J_on[i - 1], self.J_on[i]
            self.assertTrue(is_turn(t), (i, t))
            self.assertEqual((t["seq"], t["moment"], t["at"]), (l["seq"], l["moment"], l["at"]))
            self.assertEqual(t["heard"], l["words"])
            self.assertEqual(t["members"], l["hyps"], "the turn's things are the things the brain then learned from")

    def test_without_its_turn_rows_the_journal_is_the_journal_without_the_line(self) -> None:
        rest = [json.dumps(r, sort_keys=True) for r in self.J_on if not is_turn(r)]
        self.assertEqual(rest, [json.dumps(r, sort_keys=True) for r in self.J_off])

    def test_the_brain_and_the_organism_end_as_they_did_without_the_line(self) -> None:
        self.assertEqual(self.on.brain.state_hash(), self.off.brain.state_hash())
        self.assertEqual(self.on.org.state_hash(), self.off.org.state_hash())

    def test_no_turn_is_taken_at_an_ask_canvas(self) -> None:
        asked = {r["moment"] for r in self.J_on if r.get("kind") == "answer" and r.get("eye_seq") is not None}
        self.assertGreater(len(asked), 5, "the presence count: the sitting asked at canvases")
        self.assertEqual(asked & {t["moment"] for t in self.turns}, set())

    def test_before_the_first_calibration_it_says_and_asks_nothing(self) -> None:
        first = self.turns[:20]
        self.assertTrue(all(t["reason"] == "not calibrated" and t["say"] is None and t["ask"] is None and t["surprise"] is None
                            for t in first), [t["reason"] for t in first])

    def test_after_it_the_brain_speaks_and_carries_its_surprise(self) -> None:
        later = [t for t in self.turns[20:] if t["n_hyp"] > 0]
        said = [t for t in later if t["say"] is not None]
        self.assertGreater(len(said), 15, "the presence count (a brain of 20 to 120 scenes spoke 29 times in 100 canvases)")
        for t in said:
            self.assertEqual(t["say"]["readback"], t["say"]["hyp"])
            self.assertTrue(t["say"]["words"] and all(isinstance(w, str) for w in t["say"]["words"]))
        self.assertTrue(all(t["surprise"] is not None and 0.0 <= t["surprise"] <= 1.0 for t in later))
        self.assertTrue(any(t["surprise"] == 0.0 for t in later) and any(t["surprise"] > 0.0 for t in later))

    def test_the_counts_are_the_rows(self) -> None:
        want = {"turns": len(self.turns), "said": sum(t["say"] is not None for t in self.turns),
                "asked": sum(t["ask"] is not None for t in self.turns)}
        self.assertEqual(self.on.brain_turns, want)
        self.assertEqual(self.on.brain_status()["turns"], want)
        self.assertNotIn("turns", self.off.brain_status())

    def test_the_same_life_twice_is_the_same_journal(self) -> None:
        _m, root = self.live(lean_text(DRIVE_LINE))
        self.assertEqual(S.journal_bytes(root), S.journal_bytes(self.on_root))

    def test_resumed_at_a_cut_the_turns_and_their_counts_go_on(self) -> None:
        eyes = [i for i, r in enumerate(self.rows) if r["sense"] == "eye"]
        cut = eyes[60] + 2
        _first, rr = self.live(lean_text(DRIVE_LINE), rows=self.rows[:cut + 1])
        m2, last = MM.Mind.resume(rr.parent / "g.genome", rr)
        try:
            self.assertEqual(last, self.rows[cut]["seq"])
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        self.assertEqual(m2.brain_turns, self.on.brain_turns)
        mine = [json.dumps({k: v for k, v in r.items() if k != "at"}, sort_keys=True) for r in S.journal(rr) if is_turn(r)]
        whole = [json.dumps({k: v for k, v in r.items() if k != "at"}, sort_keys=True) for r in self.turns]
        self.assertEqual(mine, whole)


class ItsTwoValues(_Lives):
    def test_says_0_is_a_silent_mouth(self) -> None:
        _m, root = self.live(lean_text("DRIVE    brain turn before hearing; says 0; asks 1"))
        turns = [r for r in S.journal(root) if is_turn(r)]
        self.assertEqual(len(turns), N_TRAIN)
        self.assertEqual(sum(t["say"] is not None for t in turns), 0)
        self.assertEqual([t["ask"] for t in turns], [t["ask"] for t in self.turns])

    def test_asks_0_asks_nothing(self) -> None:
        _m, root = self.live(lean_text("DRIVE    brain turn before hearing; says 1; asks 0"))
        turns = [r for r in S.journal(root) if is_turn(r)]
        self.assertEqual(sum(t["ask"] is not None for t in turns), 0)
        self.assertEqual([t["say"] for t in turns], [t["say"] for t in self.turns])
        self.assertGreater(sum(t["ask"] is not None for t in self.turns), 0, "the presence count: under asks 1 it did ask")


class Refusals(_Lives):
    def test_refused_beside_no_brain_line_by_name(self) -> None:
        with self.assertRaises(GenomeError) as e:
            self.live(lean_text(DRIVE_LINE, brain=False))
        self.assertIn("DRIVE", str(e.exception))
        self.assertIn("BRAIN", str(e.exception))

    def test_the_same_genome_without_the_line_starts(self) -> None:
        m, _root = self.live(lean_text(brain=False), rows=self.rows[:50])
        self.assertIsNone(m.brain)

    def test_under_blind_brain_there_is_no_brain_and_no_turn(self) -> None:
        m, root = self.live(lean_text(DRIVE_LINE), blind=frozenset({"brain"}))
        self.assertIsNone(m.brain)
        self.assertEqual(sum(is_turn(r) for r in S.journal(root)), 0)
        self.assertEqual(m.brain_turns, {"turns": 0, "said": 0, "asked": 0})


class TheFullOrganism(_Lives):
    """Every organ on (ALPHA4's genes) beside the brain: the turn rows are added and not one other row moves."""

    def test_the_turn_rows_are_added_and_no_other_row_moves(self) -> None:
        _a, off = self.live(full_text())
        b, on = self.live(full_text(DRIVE_LINE))
        J_off, J_on = S.journal(off), S.journal(on)
        turns = [r for r in J_on if is_turn(r)]
        self.assertEqual(len(turns), N_TRAIN)
        self.assertEqual([json.dumps(r, sort_keys=True) for r in J_on if not is_turn(r)],
                         [json.dumps(r, sort_keys=True) for r in J_off])
        self.assertGreater(sum(t["say"] is not None for t in turns), 15)
        # the lean body's brain and the full organism's brain take the same turns on the same tape
        strip = lambda t: {k: v for k, v in t.items() if k not in ("at",)}       # noqa: E731
        self.assertEqual([strip(t) for t in turns], [strip(t) for t in self.turns])


if __name__ == "__main__":
    unittest.main()
