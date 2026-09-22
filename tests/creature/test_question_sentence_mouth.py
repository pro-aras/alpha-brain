# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — L-10/L-11 (docs/briefs/
# LIFE-C-QUESTION-SENTENCE.md): QUESTION (the mind's own side -- the world door is
# tests/creature/test_question_door.py's own file), SENTENCE's frame filing/scoring through a real Mind,
# and MOUTH, each on the smallest fixture that exercises the real code path (never a stub of it). The
# base genome is `G4-wave2-test.genome` (PREDICT/FAST already on it, its own #OFF SENTENCE line inert)
# plus a small EXTRA_GENES block, matching test_wave3_rules.py's own discipline (lift verbatim, build the
# combined text in a tempdir, never edit genome/G4.genome itself).
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PIL import Image

from creature.mind import Mind, _THINK_LAWS_AVAILABLE
from creature.tape import Tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
BASE_GENOME_TEXT = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()

EXTRA_GENES = """\
FILE     claim route decider due
PARK     after 1 identical dead-ends reopen on new-sense
BELIEF   clash opens never overwrites
THINK    every 1 canvases
QUESTION from wants; forms what-is is which; to the world door
SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token
MOUTH    say one frame per think; journaled
"""


def _genome_text(extra: str = EXTRA_GENES) -> str:
    return BASE_GENOME_TEXT.rstrip("\n") + "\n" + extra


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _at(i: int) -> str:
    return f"2026-09-22T{(i // 3600) % 24:02d}:{(i // 60) % 60:02d}:{i % 60:02d}.{i % 1000:03d}Z"


def _publish_worded(tape: Tape, mind: Mind, word: str, rgb: np.ndarray, moment: str, i: int) -> Dict[str, object]:
    """Publishes ear THEN eye and CONSUMES both, in order -- mind.consume() must see the ear row before
    the eye row or `self.pending` never carries the word (the SAME tape-order law every real sense obeys;
    a caller that only consumes the returned eye row starves the mind of the word entirely)."""
    at = _at(i)
    ear = tape.publish("ear", word.encode("utf-8"), {"moment": moment, "source": "test", "word": word}, "txt", at=at)
    mind.consume(ear)
    eye = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png", at=at)
    mind.consume(eye)
    return eye


def _publish_sight_only(tape: Tape, mind: Mind, rgb: np.ndarray, moment: str, i: int) -> Dict[str, object]:
    eye = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png", at=_at(i))
    mind.consume(eye)
    return eye


def _publish_two_words(tape: Tape, mind: Mind, colour: str, obj: str, rgb: np.ndarray, moment: str, i: int) -> Dict[str, object]:
    at = _at(i)
    ear1 = tape.publish("ear", colour.encode("utf-8"), {"moment": moment, "source": "test", "word": colour}, "txt", at=at)
    mind.consume(ear1)
    ear2 = tape.publish("ear", obj.encode("utf-8"), {"moment": moment, "source": "test", "word": obj}, "txt", at=at)
    mind.consume(ear2)
    eye = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png", at=at)
    mind.consume(eye)
    return eye


def _questions_written(root: Path) -> List[Dict[str, object]]:
    out_dir = root / "ask" / "out"
    if not out_dir.exists():
        return []
    rows = []
    for p in sorted(out_dir.glob("q-*.json")):
        rows.append(json.loads(p.read_text()))
    return rows


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestQuestionWordlessSecondShowing(unittest.TestCase):
    """L-10 task 1's OWN trigger (a), independent of PARK/THINK: 'a wordless sight ... seen for the
    SECOND time without a word' -- exercised directly on _consume_eye, THINK undeclared so PARK's own
    parking trigger (d) cannot also fire and confound the count."""

    def test_second_identical_wordless_showing_asks_what_is(self) -> None:
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        # THINK/PARK removed here -- only QUESTION+FAST -- so trigger (a) is isolated from (d).
        genome_path.write_text(_genome_text(extra="QUESTION from wants; forms what-is is which; to the world door\n"))
        tape = Tape(root)
        mind = Mind(genome_path, root)

        rng = np.random.default_rng(1)
        rgb, _truth = world.render_canvas("circle", rng)   # the SAME picture both times -> the SAME resonating cell
        _publish_sight_only(tape, mind, rgb, "f_pic_a", 0)
        self.assertEqual(_questions_written(root), [], "the FIRST wordless showing must not ask yet")

        _publish_sight_only(tape, mind, rgb, "f_pic_a_again", 1)

        qs = _questions_written(root)
        self.assertEqual(len(qs), 1, f"the SECOND identical wordless showing must ask exactly once: {qs}")
        self.assertEqual(qs[0]["q"], "what-is")
        self.assertEqual(qs[0]["args"], ["f_pic_a_again"])
        self.assertEqual(qs[0]["from"], "mind")

        # at most once per want: a THIRD identical wordless showing must not ask again
        _publish_sight_only(tape, mind, rgb, "f_pic_a_third", 2)
        self.assertEqual(len(_questions_written(root)), 1, "at most one question per want")


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestQuestionParkParksAWordlessSight(unittest.TestCase):
    """L-10 task 1's own test: 'a parked wordless sight -> a question row within one think' -- the
    THINK/PARK road (trigger (d)): a sight-only episode with no worded episode anywhere in FAST's ring
    dead-ends 'no_route' on its very first think (PARK's `after 1`), which parks it immediately."""

    def test_parked_sight_want_asks_within_one_think(self) -> None:
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        genome_path.write_text(_genome_text())
        tape = Tape(root)
        mind = Mind(genome_path, root)

        rng = np.random.default_rng(2)
        rgb, _truth = world.render_canvas("square", rng)
        _publish_sight_only(tape, mind, rgb, "f_square_1", 0)   # writes the sight-only episode AND runs THINK (every 1 canvas)

        self.assertEqual(mind.think_counters["thinks"], 1)
        self.assertGreaterEqual(mind.think_counters["parked"], 1, "PARK after=1 must have parked the sight want on its first think")
        qs = _questions_written(root)
        self.assertGreaterEqual(len(qs), 1, "a question must exist within the SAME think that parked it")
        self.assertTrue(any(q["q"] == "what-is" for q in qs))


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestQuestionRuleFailsAndClash(unittest.TestCase):
    """Tasks (b)/(c): 'a rule fails once' and 'a belief CLASH is filed' each form a want. Exercised at the
    QUESTION integration seam (_grade_rule / _maybe_ask_clash) against a Mind holding a REAL episode for
    the word in question (so _latest_tape_moment_for_word has a real tape_moment to cite) -- the
    rule-failure and clash DETECTION mechanisms themselves (INDUCE/DEDUCE/BELIEF) are proven elsewhere
    (tests/creature/test_wave3_rules.py, test_wave2_belief_path.py); this file proves QUESTION's own
    reaction to them."""

    def _mind_with_one_episode(self, word: str) -> "Mind":
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        # QUESTION+FAST only here -- no THINK/PARK/BELIEF, so the ONLY question that can appear comes
        # from the explicit _grade_rule/_maybe_ask_clash call each test makes below, never an incidental
        # THINK-driven dead-end on this same episode (TestQuestionParkParksAWordlessSight already proves
        # THAT road, separately).
        genome_path.write_text(_genome_text(extra="QUESTION from wants; forms what-is is which; to the world door\n"))
        tape = Tape(root)
        mind = Mind(genome_path, root)
        rng = np.random.default_rng(3)
        rgb, _truth = world.render_canvas(word, rng)
        _publish_worded(tape, mind, word, rgb, f"m_{word}_0", 0)
        return mind

    def test_rule_fails_once_asks_what_is(self) -> None:
        mind = self._mind_with_one_episode("circle")
        self.assertEqual(_questions_written(mind.run_root), [], "no want yet")
        mind._grade_rule({"op": "induce", "want": "induce:circle"}, evidence=False)
        qs = _questions_written(mind.run_root)
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["q"], "what-is")
        self.assertEqual(qs[0]["args"], ["m_circle_0"])
        self.assertIn("why", qs[0])

    def test_belief_clash_asks_is(self) -> None:
        mind = self._mind_with_one_episode("square")
        mind._maybe_ask_clash("clash:square:[1, 2]", "square")
        qs = _questions_written(mind.run_root)
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["q"], "is")
        self.assertEqual(qs[0]["args"], ["m_square_0", "square"])


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestSentenceFramesThroughTheMind(unittest.TestCase):
    """L-11 task 3, driven through the REAL consume() pipeline (game.py's own two-ear-row shape): a
    skewed "red ball"/"blue key" corpus files at least one frame; feeding w1 again afterwards scores it."""

    @staticmethod
    def _feed(tape: Tape, mind: Mind, missions: List[tuple], start_i: int) -> int:
        # the RENDERED picture is always "circle" (any real genome/world.py thing works -- "ball"/"key"/
        # "box" are the GAME's own BabyAI object names, not genome/world.py's drawable vocabulary; this
        # test is about the WORD-PAIRING mechanism, not the picture, exactly as game.py's own colour/
        # object split never touches what gets drawn).
        rng = np.random.default_rng(9)
        i = start_i
        for colour, obj in missions:
            rgb, _truth = world.render_canvas("circle", rng)
            _publish_two_words(tape, mind, colour, obj, rgb, f"g{i:05d}", i)
            i += 1
        return i

    def test_a_skewed_corpus_files_a_frame_and_it_scores(self) -> None:
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        genome_path.write_text(_genome_text())
        tape = Tape(root)
        mind = Mind(genome_path, root)

        # "red"/"ball" together 6 times, 8 noise instances over 4 OTHER pairs that touch neither "red" nor
        # "ball" -- with the mind's own default bar (find_frames(episodes), min_count=5, factor=2.0), 6
        # noise pairs is not enough lift (marginal(red)==marginal(ball)==6, N=10 -> expected 3.6, 6 <= 7.2);
        # 8 noise instances (N=14) gives expected 2.57, 6 > 5.14 clears it (see genome/sentence.py's module
        # docstring: a single skewed pair's OWN marginals rise with its count, capping the ratio -- more
        # UNRELATED background is what buys the lift, not more repeats of the pair itself).
        missions = ([("red", "ball")] * 6
                    + [("blue", "key")] * 2 + [("blue", "box")] * 2 + [("green", "key")] * 2 + [("green", "box")] * 2)
        i = self._feed(tape, mind, missions, 0)

        self.assertGreaterEqual(mind.think_counters["frames_filed"], 1,
                                 f"no frame filed: think_counters={mind.think_counters}")
        self.assertIn("red|ball", mind._frames)

        # score it: feed "red ball" again (w1="red" recurs) -- _score_due_predictions' frame branch fires
        rng = np.random.default_rng(11)
        rgb, _truth = world.render_canvas("circle", rng)
        _publish_two_words(tape, mind, "red", "ball", rgb, f"g{i:05d}", i)

        self.assertGreaterEqual(mind.think_counters["frames_scored"], 1, mind.think_counters)


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestMouth(unittest.TestCase):
    """L-11 task 4: says a filed, cited frame when its w1 recurs (journal `say` + ask/out `is` + heard
    yes/no); refuses a planted UNCITED frame by name, never says it."""

    def _mind(self) -> "Mind":
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        genome_path.write_text(_genome_text())
        return Mind(genome_path, root)

    def test_says_a_cited_frame_and_journals_heard(self) -> None:
        mind = self._mind()
        tape = Tape(mind.run_root)
        mind._frames["red|ball"] = {"w1": "red", "w2": "ball", "episodes": [0, 1, 2, 3, 4, 5]}

        rng = np.random.default_rng(5)
        rgb, _truth = world.render_canvas("circle", rng)
        _publish_two_words(tape, mind, "red", "ball", rgb, "g00000", 0)   # THINK every 1 canvas -> _maybe_think -> _maybe_say

        self.assertEqual(mind.think_counters["said"], 1, mind.think_counters)
        self.assertEqual(mind.think_counters["heard_yes"] + mind.think_counters["heard_no"], 1)
        journal_path = list((mind.run_root / "journal").glob("*.jsonl"))[0]
        say_rows = [json.loads(l) for l in journal_path.read_text().splitlines() if '"say"' in l]
        self.assertGreaterEqual(len(say_rows), 1)
        self.assertIn("heard", say_rows[-1]["say"])

        ask_out = list((mind.run_root / "ask" / "out").glob("q-*.json"))
        self.assertGreaterEqual(len(ask_out), 1, "MOUTH's own ask/out 'is' row")
        payloads = [json.loads(p.read_text()) for p in ask_out]
        self.assertTrue(any(p["q"] == "is" and p.get("from") == "mouth" for p in payloads))

    def test_says_even_when_the_think_pool_is_empty(self) -> None:
        """edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught: _maybe_say used
        to run only AFTER `_think_choose(pool)` returned a real item, so a think whose pool was EMPTY
        (exactly the state a settled life reaches once every want is parked and nothing is due) never
        reached the mouth. Fixture: park the ONLY word this canvas writes to FAST ("ball" -- self.pending
        keeps the LAST ear row of the instant, game.py's own colour-then-object order) BEFORE publishing,
        so _think_pool()'s word-kind loop adds nothing for it; nothing else can populate the pool on a
        fresh mind's first canvas (no due predictions, no INDUCE/DEDUCE declared, find_frames() needs
        >= min_count episodes so one canvas never qualifies, no outcome episodes -- OUTCOME/SIT undeclared)."""
        mind = self._mind()
        tape = Tape(mind.run_root)
        mind._frames["red|ball"] = {"w1": "red", "w2": "ball", "episodes": [0, 1, 2, 3, 4, 5]}
        mind.park.answer("ball", "pre-parked-for-this-test")

        rng = np.random.default_rng(5)
        rgb, _truth = world.render_canvas("circle", rng)
        _publish_two_words(tape, mind, "red", "ball", rgb, "g00000", 0)

        self.assertEqual(mind.think_counters["thinks"], 1)
        journal_path = list((mind.run_root / "journal").glob("*.jsonl"))[0]
        think_rows = [json.loads(l) for l in journal_path.read_text().splitlines() if '"think"' in l]
        self.assertEqual(think_rows[-1]["think"]["outcome"], "empty_pool", "the pool really was empty this tick")
        self.assertEqual(mind.think_counters["said"], 1, "MOUTH must still say a planted, cited frame on an empty-pool think")

    def test_two_says_get_two_distinct_q_files(self) -> None:
        """edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught:
        `questions_written` used to be incremented only inside `_maybe_ask`, never by `_write_ask_out`
        itself -- a second MOUTH 'is' row would silently OVERWRITE the first q-N.json instead of getting
        its own file (both writes computing the same, never-advanced `n`)."""
        mind = self._mind()
        tape = Tape(mind.run_root)
        mind._frames["red|ball"] = {"w1": "red", "w2": "ball", "episodes": [0, 1, 2, 3, 4, 5]}

        rng = np.random.default_rng(5)
        for i in range(2):
            rgb, _truth = world.render_canvas("circle", rng)
            _publish_two_words(tape, mind, "red", "ball", rgb, f"g{i:05d}", i)

        self.assertEqual(mind.think_counters["said"], 2, mind.think_counters)
        ask_out = sorted((mind.run_root / "ask" / "out").glob("q-*.json"))
        mouth_rows = [(p.name, json.loads(p.read_text())) for p in ask_out]
        mouth_rows = [(name, row) for name, row in mouth_rows if row.get("from") == "mouth"]
        self.assertEqual(len(mouth_rows), 2, f"two SAYs must produce two distinct q-files, got: {mouth_rows}")
        names = {name for name, _row in mouth_rows}
        self.assertEqual(len(names), 2, "must be two DISTINCT filenames, not one overwritten twice")
        seqs = {row["seq"] for _name, row in mouth_rows}
        self.assertEqual(len(seqs), 2, "two distinct canvases' own seq, not the same row twice")

    def test_refuses_an_uncited_planted_frame(self) -> None:
        mind = self._mind()
        tape = Tape(mind.run_root)
        # G-MOT-6's own toy: a planted frame with NO episodes cited must be refused, never said.
        mind._frames["red|ball"] = {"w1": "red", "w2": "ball", "episodes": []}

        rng = np.random.default_rng(5)
        rgb, _truth = world.render_canvas("circle", rng)
        _publish_two_words(tape, mind, "red", "ball", rgb, "g00000", 0)

        self.assertEqual(mind.think_counters["said"], 0, "an uncited frame must never be SAID")
        journal_path = list((mind.run_root / "journal").glob("*.jsonl"))[0]
        say_rows = [json.loads(l) for l in journal_path.read_text().splitlines() if '"say"' in l]
        self.assertEqual(len(say_rows), 1)
        self.assertEqual(say_rows[0]["say"]["outcome"], "refused")
        self.assertEqual(say_rows[0]["say"]["reason"], "uncited")


if __name__ == "__main__":
    unittest.main()
