# edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:1x +0400 — A42-B2 PART 1 (ALPHA4-2-PREREG §2 G9 "the LINE scorer";
# the smoke's finding, register 11:23: «the mind's frame scorer reads a one-word shelf canvas, so a shelf frame's w2 is never on
# w1's instant»). The reader publishes every word of a chunk as its OWN moment (the word alone, shown large) and THEN the whole
# line (creature/senses/read.py:_publish_chunk); a frame (w1, w2) is due on any instant carrying w1, so it was scored on w1's
# one-word canvas — alpha4-1: 0 of 63 shelf frames true, and 4 of 4 on the hour-1 replay (scratch/b2/ceiling-h1/ceiling.txt).
# Under `SENTENCE …; judged by the eye on the line; …` a SHELF instant scores a frame only when it is a LINE (>= 2 distinct
# words) and the evidence is ANY of the line's located glances (its CEILING: 0.272 on the 10:54 copy, 0.089 with glance 0 alone).
# Every other source (the game's mission, a lexicon gloss, a test tape) keeps today's trigger and evidence by the same code path.
"""tests/creature/test_g9_line_scorer.py — the mind half of G9, through the REAL consume() road with the reader's own two shapes."""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image

from creature import mind as mind_module
from creature.mind import Mind
from creature.senses import read_common
from creature.tape import Tape
from genome import world
from genome.predict import file as predict_file

ROOT = Path(__file__).resolve().parents[2]
BASE_GENOME_TEXT = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()
OLD = "SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token"
NEW = "SENTENCE two-word frames from co-occurring words; judged by the eye on the line; never next-token"
AT = "2026-09-23T01:00:00.000Z"


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(b, format="PNG"); return b.getvalue()


def _mind(sentence_line: str):
    root = Path(tempfile.mkdtemp(prefix="g9-"))
    gp = root / "g.genome"
    gp.write_text(BASE_GENOME_TEXT.rstrip("\n") + "\nFILE     claim route decider due\n" + sentence_line + "\n")
    return root, Tape(root), Mind(gp, root)


def _plant_frame(mind: Mind, w1: str, w2: str) -> None:
    """A FILED frame, exactly as _think_work's "frame" branch files one (the pool/think road is not under test here)."""
    key = f"{w1}|{w2}"
    filed = predict_file(claim=f'"{w1} {w2}"', route="frame",
                         decider="the eye answers BOTH words on the next instant that carries w1", due=f"the next instant with {w1!r}")
    mind._frame_pending.add(key)
    mind._frames[key] = {"w1": w1, "w2": w2, "episodes": []}
    mind._filed_predictions.append({"row": filed, "target_word": w1, "due_canvas": mind._canvas_index, "frame_w2": w2, "frame_key": key})


def _shelf_word(tape: Tape, mind: Mind, word: str, moment: str, ix: int) -> None:
    """The reader's per-word moment: ONE ear row + the word alone rendered large (read.py:_publish_chunk, one_word_moments)."""
    mind.consume(tape.publish("ear", word.encode(), {"moment": moment, "source": "shelf", "word": word}, "txt", at=AT))
    rgb = read_common.render_line(word, 128, read_common.DEFAULT_FONT_PATH)
    mind.consume(tape.publish("eye", _png(rgb), {"moment": moment, "source": "shelf", "word_ix": ix, "text": word}, "png", at=AT))


def _line(tape: Tape, mind: Mind, words: List[str], moment: str, source: str = "shelf") -> None:
    """The sentence moment: every word an ear row, the whole line rendered (same publisher shape for a lexicon gloss)."""
    for w in words:
        mind.consume(tape.publish("ear", w.encode(), {"moment": moment, "source": source, "word": w}, "txt", at=AT))
    rgb = read_common.render_line(" ".join(words), 128, read_common.DEFAULT_FONT_PATH)
    mind.consume(tape.publish("eye", _png(rgb), {"moment": moment, "source": source, "text": " ".join(words)}, "png", at=AT))


def _game(tape: Tape, mind: Mind, colour: str, obj: str, moment: str, k: int = 0) -> None:
    """The game's two-ear-row instant with a PICTURE (game.py's own shape): colour then object, then the frame."""
    for w in (colour, obj):
        mind.consume(tape.publish("ear", w.encode(), {"moment": moment, "source": "game", "word": w}, "txt", at=AT))
    rgb, _t = world.render_canvas("circle", np.random.default_rng([7, k]))
    mind.consume(tape.publish("eye", _png(rgb), {"moment": moment, "source": "game"}, "png", at=AT))


def _scored_rows(root: Path) -> List[Dict[str, object]]:
    p = root / "state" / "predictions.jsonl"
    if not p.exists():
        return []
    return [r for r in (json.loads(l) for l in p.read_text().splitlines() if l.strip())
            if (r.get("row") or {}).get("route") == "frame" and r.get("outcome") is not None]


class TestTheOldClauseIsTheControl(unittest.TestCase):
    """Today's road, kept byte-for-byte when the clause is undeclared: the frame is scored on w1's ONE-WORD shelf moment."""

    def test_scored_on_the_one_word_moment(self) -> None:
        root, tape, mind = _mind(OLD)
        try:
            _plant_frame(mind, "the", "cat")
            _shelf_word(tape, mind, "the", "r0:w0", 0)
            self.assertEqual(mind.think_counters["frames_scored"], 1, "the old clause scores on w1's one-word canvas (the finding)")
            rows = _scored_rows(root)
            self.assertEqual(len(rows), 1)
            self.assertNotIn("instant", rows[0], "undeclared: the scored row is exactly what it always was")
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)


class TestTheLineClause(unittest.TestCase):
    def test_a_shelf_frame_waits_for_the_line_and_is_scored_there(self) -> None:
        root, tape, mind = _mind(NEW)
        try:
            _plant_frame(mind, "the", "cat")
            _shelf_word(tape, mind, "the", "r0:w0", 0)
            _shelf_word(tape, mind, "cat", "r0:w1", 1)
            self.assertEqual(mind.think_counters["frames_scored"], 0, "a one-word shelf moment never scores a frame under the clause")
            self.assertEqual(len(mind._filed_predictions), 1, "the entry is still pending")
            _line(tape, mind, ["the", "cat"], "r0")
            self.assertEqual(mind.think_counters["frames_scored"], 1, "the LINE moment scores it")
            self.assertEqual(len(mind._filed_predictions), 0)
            rows = _scored_rows(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["instant"], {"source": "shelf", "words": ["the", "cat"], "line": True})
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)

    def test_a_one_word_shelf_chunk_is_never_a_line(self) -> None:
        """A chunk of ONE word publishes a per-word moment and then a "line" of the same single word: neither scores."""
        root, tape, mind = _mind(NEW)
        try:
            _plant_frame(mind, "the", "cat")
            _shelf_word(tape, mind, "the", "r1:w0", 0)
            _line(tape, mind, ["the"], "r1")
            self.assertEqual(mind.think_counters["frames_scored"], 0)
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)

    def test_the_game_road_is_unchanged(self) -> None:
        """A game instant (two ear rows, a picture) carrying w1 scores the frame exactly as today, first-glance evidence."""
        root, tape, mind = _mind(NEW)
        try:
            _plant_frame(mind, "red", "box")
            with mock.patch.object(Mind, "_frame_evidence", return_value=False) as old_road, \
                    mock.patch.object(Mind, "_frame_evidence_line", return_value=False) as line_road:
                _game(tape, mind, "red", "box", "g0")
            self.assertEqual(mind.think_counters["frames_scored"], 1)
            self.assertEqual(old_road.call_count, 1, "the game's evidence is the old decider")
            self.assertEqual(line_road.call_count, 0)
            rows = _scored_rows(root)
            self.assertEqual(rows[0]["instant"], {"source": "game", "words": ["red", "box"], "line": False})
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)

    def test_a_lexicon_gloss_keeps_todays_trigger__documented(self) -> None:
        """The clause is SHELF-only: a lexicon gloss (multi-word, its own source) is not a shelf line and keeps today's road —
        w1 in the gloss still scores the frame with the old decider. Documented, so a later change to this is deliberate (RAISED
        in A42-B2-REPORT: the DECLARED replay prints how many scorings fire on lexicon instants)."""
        root, tape, mind = _mind(NEW)
        try:
            _plant_frame(mind, "the", "cat")
            with mock.patch.object(Mind, "_frame_evidence", return_value=False) as old_road:
                _line(tape, mind, ["to", "move", "the", "hand"], "lex0", source="lexicon")
            self.assertEqual(mind.think_counters["frames_scored"], 1)
            self.assertEqual(old_road.call_count, 1)
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)


class TestTheLineEvidence(unittest.TestCase):
    """The decider on a line: ANY located glance whose recall answers a words cell whose ledger is exactly {w2} — the strict
    decider of `_frame_evidence`, asked once per glance (the ceiling: glance 0 alone 0.089, any located glance 0.272)."""

    def test_any_glance_not_only_the_first(self) -> None:
        root, tape, mind = _mind(NEW)
        try:
            g = [np.full(4, float(i)) for i in range(4)]
            hit = g[2]

            def fake_recall(side, x, k=1, to=None):
                return {"cell": 7, "reason": "answer"} if x is hit else {"cell": 3, "reason": "answer"}
            fake_ledgers = {"sight": {}, "words": {7: {"cat"}, 3: {"the"}}, "sound": {}}
            with mock.patch.object(mind.org, "recall", side_effect=fake_recall), \
                    mock.patch.object(mind_module, "build_ledgers", return_value=fake_ledgers):
                self.assertFalse(mind._frame_evidence("cat", g[0]), "the old decider reads glance 0 only")
                self.assertTrue(mind._frame_evidence_line("cat", g), "the line decider reads every located glance")
                self.assertFalse(mind._frame_evidence_line("cat", g[:2]))
                self.assertFalse(mind._frame_evidence_line("dog", g))
            # a merged cell carrying two words is NOT w2's cell (the strict decider, as today)
            fake_ledgers2 = {"sight": {}, "words": {7: {"cat", "hat"}}, "sound": {}}
            with mock.patch.object(mind.org, "recall", side_effect=fake_recall), \
                    mock.patch.object(mind_module, "build_ledgers", return_value=fake_ledgers2):
                self.assertFalse(mind._frame_evidence_line("cat", g))
        finally:
            mind.close(); shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
