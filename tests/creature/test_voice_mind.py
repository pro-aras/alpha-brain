# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 18:29 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §2/§3 (the law SIGNED ×3 at
# toys-1003 1ccc3bf; its §7 test-first order: the parser's two spellings and the refusals, the mind's clause on a synthetic canvas
# stream — a said turn voices once, a silent one never, a planted order swap caught — the ledger key and its resume restore).
"""tests/creature/test_voice_mind.py — THE MOUTH VOICES THE BRAIN (W1): the MOUTH line's OPTIONAL clause
«say one frame per think and the brain's phrase per canvas; journaled» makes the body's journal carry the DRIVE turn's say.

The tape and the lives are tests/creature/test_drive_mind.py's own (120 training scenes + a sitting, the LEAN body, the brain
calibrating at 20, 40 and 80): OFF = the lean body under DRIVE alone; ON = the same plus the MOUTH clause. The clause's frame
half is inert here (SENTENCE is off on the lean body: _maybe_say loops over no frames). The FULL organism (ALPHA4's own MOUTH
line, its frame mouth live) is lived OFF and ON too: the voice rows are added and the frame mouth does not move (mark F's unit
form). The planted order swap and the wrong/echo/orphan mouths are the GRADER's controls (tests/tools/test_voice_gate.py)."""
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
_TEMPLATE = (ROOT / "genome" / "brain" / "BRAIN-LEAN.genome").read_text()
LEAN, _n = re.subn(r"^DRIVE    .*\n", "", _TEMPLATE, count=1, flags=re.M)
assert _n == 1, "the lean template carries one DRIVE line"
DRIVE_LINE = "DRIVE    brain turn before hearing; says 1; asks 1"
MOUTH_LINE = "MOUTH    say one frame per think and the brain's phrase per canvas; journaled"
MOUTH_OLD = "MOUTH    say one frame per think; journaled"
AT = "calibrate at 250 500 1000 2000 5000 10000"
N_TRAIN = 120


def lean_text(*lines: str) -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), LEAN, count=1, flags=re.M)
    assert text != LEAN and text.count(AT) == 1
    text = text.replace(AT, "calibrate at 20 40 80")
    return text + "\n" + ("\n".join(lines) + "\n" if lines else "")


def full_text(*lines: str, voice: bool = False) -> str:
    text = S.genome_text(brain=True, train=N_TRAIN)
    assert text.count(AT) == 1
    text = text.replace(AT, "calibrate at 20 40 80")
    if voice:   # ALPHA4's own MOUTH line, in the new spelling (the law's ON form for the full life: its MOUTH line replaced)
        text, n = re.subn(r"^MOUTH    say one frame per think; journaled.*$", MOUTH_LINE, text, count=1, flags=re.M)
        assert n == 1, "ALPHA4 carries one MOUTH line in the old spelling"
    return text + "\n" + ("\n".join(lines) + "\n" if lines else "")


def is_turn(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "turn"


def is_voice(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "voice"


def is_learn(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "learn"


class TheSpelling(unittest.TestCase):
    """The parser (the law §2, the genome row): ONE optional clause; absent, the dict is EXACTLY the old one; present, ONE key."""

    def test_the_old_spelling_parses_to_exactly_the_old_dict(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_OLD)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True})

    def test_the_new_spelling_adds_exactly_one_key(self) -> None:
        self.assertEqual(parse_genome(lean_text(MOUTH_LINE)).declared["MOUTH"],
                         {"say": "one frame per think", "journaled": True, "brain": "phrase per canvas"})

    def test_absent_there_is_no_mouth_key(self) -> None:
        self.assertNotIn("MOUTH", parse_genome(lean_text()).declared)

    def test_the_one_difference_is_the_mouth_key(self) -> None:
        a, b = parse_genome(lean_text(DRIVE_LINE)).declared, parse_genome(lean_text(DRIVE_LINE, MOUTH_LINE)).declared
        self.assertEqual({k: v for k, v in b.items() if k != "MOUTH"}, a)

    def test_every_misspelling_refuses_by_name(self) -> None:
        for bad in ("MOUTH    say one frame per think and the brains phrase per canvas; journaled",
                    "MOUTH    say one frame per think and the brain's phrase per canvas",
                    "MOUTH    say one frame per think and the brain's phrases per canvas; journaled",
                    "MOUTH    say two frames per think and the brain's phrase per canvas; journaled",
                    "MOUTH    say one frame per think; and the brain's phrase per canvas; journaled",
                    "MOUTH    say one frame per canvas and the brain's phrase per canvas; journaled",
                    "MOUTH    say one frame per think and the brain's phrase per think; journaled",
                    "MOUTH    the brain's phrase per canvas; journaled"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(lean_text(bad))
                self.assertIn("MOUTH", str(e.exception))

    def test_the_registry_names_its_call_site(self) -> None:
        from creature import genes
        self.assertEqual(genes.unwired(parse_genome(lean_text(DRIVE_LINE, MOUTH_LINE)).declared), [])


class TheRefusal(unittest.TestCase):
    """The law §2 (the refusal): the clause declared beside no DRIVE line is refused at the mind's start BY NAME —
    «the phrase is the DRIVE turn's». The old spelling beside no DRIVE starts (the frame mouth never needed DRIVE)."""

    def test_the_clause_beside_no_drive_is_refused_by_name(self) -> None:
        g = parse_genome(lean_text(MOUTH_LINE))   # the PARSER takes the line: the refusal is the mind's, not the parser's
        self.assertIn("brain", g.declared["MOUTH"])
        with self.assertRaises(GenomeError) as e:
            self._mind(lean_text(MOUTH_LINE))
        self.assertIn("MOUTH", str(e.exception))
        self.assertIn("DRIVE", str(e.exception))
        self.assertIn("the phrase is the DRIVE turn's", str(e.exception))

    def test_the_old_spelling_beside_no_drive_starts(self) -> None:
        m = self._mind(lean_text(MOUTH_OLD))
        self.assertEqual(m.genome.declared["MOUTH"], {"say": "one frame per think", "journaled": True})

    def _mind(self, text: str) -> MM.Mind:
        tmp = Path(tempfile.mkdtemp(prefix="voice-refusal-"))
        gp = tmp / "g.genome"
        gp.write_text(text)
        return MM.Mind(gp, tmp / "run")


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="voice-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.off, cls.off_root = cls.live(lean_text(DRIVE_LINE))
        cls.on, cls.on_root = cls.live(lean_text(DRIVE_LINE, MOUTH_LINE))
        cls.J_off, cls.J_on = S.journal(cls.off_root), S.journal(cls.on_root)
        cls.turns = [r for r in cls.J_on if is_turn(r)]
        cls.voices = [r for r in cls.J_on if is_voice(r)]

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


class TheMouthVoicesTheBrain(_Lives):
    def test_off_there_is_no_voice_row_and_no_voiced_key(self) -> None:
        self.assertEqual(sum(is_voice(r) for r in self.J_off), 0)
        self.assertGreater(sum(is_turn(r) for r in self.J_off), 100, "the presence count: the brain took its turns")
        self.assertNotIn("voiced", self.off.brain_turns)
        self.assertNotIn("voice", self.off.acts_chosen)

    def test_one_voice_row_between_its_turn_and_its_learn(self) -> None:
        learns = [i for i, r in enumerate(self.J_on) if is_learn(r)]
        self.assertEqual(len(learns), N_TRAIN)
        for i in learns:
            t = self.J_on[i - 2] if self.J_on[i - 1].get("act") == "voice" else self.J_on[i - 1]
            self.assertTrue(is_turn(t), (i, t))
            self.assertEqual((t["seq"], t["moment"], t["at"]), (self.J_on[i]["seq"], self.J_on[i]["moment"], self.J_on[i]["at"]))
            if t["say"] is not None:
                v = self.J_on[i - 1]
                self.assertTrue(is_voice(v), (i, v))
                self.assertEqual((v["seq"], v["moment"], v["at"]), (t["seq"], t["moment"], t["at"]))
            else:
                self.assertTrue(is_turn(self.J_on[i - 1]), (i, self.J_on[i - 1]))

    def test_a_voice_row_exists_iff_its_turn_said(self) -> None:
        said = [t for t in self.turns if t["say"] is not None]
        self.assertGreater(len(said), 15, "the presence count (the same tape's brain spoke 29 times in 100 canvases)")
        self.assertEqual(len(self.voices), len(said))
        self.assertEqual([v["seq"] for v in self.voices], [t["seq"] for t in said])

    def test_the_voice_is_the_turns_say_field_by_field(self) -> None:
        by_seq = {t["seq"]: t for t in self.turns}
        for v in self.voices:
            s = by_seq[v["seq"]]["say"]
            self.assertEqual(v["say"], s, v["seq"])
            self.assertEqual(set(s), {"hyp", "fix", "pos", "words", "readback", "margin"}, v["seq"])

    def test_without_its_voice_rows_the_journal_is_the_journal_without_the_clause(self) -> None:
        rest = [json.dumps(r, sort_keys=True) for r in self.J_on if not is_voice(r)]
        self.assertEqual(rest, [json.dumps(r, sort_keys=True) for r in self.J_off])

    def test_the_brain_and_the_organism_end_as_they_did_without_the_clause(self) -> None:
        self.assertEqual(self.on.brain.state_hash(), self.off.brain.state_hash())
        self.assertEqual(self.on.org.state_hash(), self.off.org.state_hash())

    def test_before_the_first_calibration_nothing_is_voiced(self) -> None:
        early = [t for t in self.turns[:20]]
        self.assertTrue(all(t["reason"] == "not calibrated" and t["say"] is None for t in early))
        self.assertEqual({v["seq"] for v in self.voices} & {t["seq"] for t in early}, set())
        self.assertGreater(len(self.voices), 0, "the presence count: the later canvases are voiced")

    def test_no_voice_row_at_an_ask_canvas(self) -> None:
        asked = {r["moment"] for r in self.J_on if r.get("kind") == "answer" and r.get("eye_seq") is not None}
        self.assertGreater(len(asked), 5, "the presence count: the sitting asked at canvases")
        self.assertEqual(asked & {v["moment"] for v in self.voices}, set())

    def test_the_counts_are_the_rows(self) -> None:
        said = sum(t["say"] is not None for t in self.turns)
        want = {"turns": len(self.turns), "said": said, "asked": sum(t["ask"] is not None for t in self.turns),
                "voiced": len(self.voices)}
        self.assertEqual(self.on.brain_turns, want)
        self.assertEqual(said, len(self.voices))
        self.assertEqual(self.on.acts_chosen.get("voice"), len(self.voices))
        self.assertEqual(self.on.brain_status()["turns"], want)
        self.assertNotIn("voiced", self.off.brain_status()["turns"])

    def test_the_same_life_twice_is_the_same_journal(self) -> None:
        _m, root = self.live(lean_text(DRIVE_LINE, MOUTH_LINE))
        self.assertEqual(S.journal_bytes(root), S.journal_bytes(self.on_root))

    def test_under_blind_brain_there_is_no_brain_and_no_voice(self) -> None:
        m, root = self.live(lean_text(DRIVE_LINE, MOUTH_LINE), blind=frozenset({"brain"}))
        self.assertIsNone(m.brain)
        self.assertEqual(sum(is_voice(r) for r in S.journal(root)), 0)
        self.assertEqual(m.brain_turns, {"turns": 0, "said": 0, "asked": 0, "voiced": 0})


class ItsFrameHalfStaysInert(_Lives):
    def test_the_lean_body_writes_no_frame_say_row_under_the_clause(self) -> None:
        says = [r for r in self.J_on if "say" in r and "kind" not in r]   # the cells' frame mouth's rows carry no kind/act
        self.assertEqual(says, [], "without SENTENCE the clause's frame half loops over no frames (the law §2)")


class ItsTwoValues(_Lives):
    def test_says_0_voices_nowhere(self) -> None:
        _m, root = self.live(lean_text("DRIVE    brain turn before hearing; says 0; asks 1", MOUTH_LINE))
        turns = [r for r in S.journal(root) if is_turn(r)]
        self.assertEqual(len(turns), N_TRAIN)
        self.assertEqual(sum(t["say"] is not None for t in turns), 0)
        self.assertEqual(sum(is_voice(r) for r in S.journal(root)), 0)


class TheLedgerAndResume(_Lives):
    def test_the_ledger_carries_voiced_only_under_the_clause(self) -> None:
        on = json.loads((self.on_root / "state" / "ledger.json").read_text())["asks"]["turns"]
        off = json.loads((self.off_root / "state" / "ledger.json").read_text())["asks"]["turns"]
        self.assertIn("voiced", on)
        self.assertEqual(on["voiced"], len(self.voices))
        self.assertNotIn("voiced", off)

    def test_resumed_at_a_cut_the_voices_and_their_counts_go_on(self) -> None:
        eyes = [i for i, r in enumerate(self.rows) if r["sense"] == "eye"]
        cut = eyes[60] + 2
        _first, rr = self.live(lean_text(DRIVE_LINE, MOUTH_LINE), rows=self.rows[:cut + 1])
        m2, last = MM.Mind.resume(rr.parent / "g.genome", rr)
        try:
            self.assertEqual(last, self.rows[cut]["seq"])
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        self.assertEqual(m2.brain_turns, self.on.brain_turns)
        self.assertGreater(m2.brain_turns["voiced"], 0, "the presence count: the resumed life voiced")
        mine = [json.dumps({k: v for k, v in r.items() if k != "at"}, sort_keys=True) for r in S.journal(rr) if is_voice(r)]
        whole = [json.dumps({k: v for k, v in r.items() if k != "at"}, sort_keys=True) for r in self.voices]
        self.assertEqual(mine, whole)


class TheFullOrganism(_Lives):
    """Every organ on beside the brain (ALPHA4's own MOUTH line, its frame mouth live): the voice rows are added and the frame
    mouth does not move — mark F's unit form (the law §3)."""

    def test_the_voice_rows_are_added_and_the_frame_mouth_does_not_move(self) -> None:
        _a, off = self.live(full_text(DRIVE_LINE))
        b, on = self.live(full_text(DRIVE_LINE, voice=True))
        J_off, J_on = S.journal(off), S.journal(on)
        voices = [r for r in J_on if is_voice(r)]
        turns = [r for r in J_on if is_turn(r)]
        self.assertEqual(len(voices), sum(t["say"] is not None for t in turns))
        self.assertGreater(len(voices), 15, "the presence count: the full organism's brain spoke")
        self.assertEqual([json.dumps(r, sort_keys=True) for r in J_on if not is_voice(r)],
                         [json.dumps(r, sort_keys=True) for r in J_off])
        frames_off = sum(1 for r in J_off if "say" in r and "kind" not in r)   # the frame mouth's rows carry no kind/act
        frames_on = sum(1 for r in J_on if "say" in r and "kind" not in r)
        # On THIS 120-canvas tape the frame mouth says nothing (0 rows; its own fixture — test_question_sentence_mouth.py —
        # plants cited frames by hand to make it say, and stays green beside this clause). The nonzero frame presence is the
        # BENCH's F on the real full life (986 frame says). The bar here is the equality above: no frame row moves, at any count.
        self.assertEqual(frames_on, frames_off)
        self.assertEqual(b.acts_chosen.get("voice"), len(voices))
        self.assertEqual(b.acts_chosen.get("say"), _a.acts_chosen.get("say"), "the cells' mouth's own count is unmoved")


if __name__ == "__main__":
    unittest.main()
