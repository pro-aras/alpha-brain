# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:14 +0400 — ALPHA4-H task 3 (docs/briefs/ALPHA4-H.md):
# creature/senses/lexicon.py, test-first.
from __future__ import annotations

import functools
import json
import shutil
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature.body import Body
from creature.senses import lexicon as lexicon_sense
from creature.tape import Tape, read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _write_lexicon(base_dir: Path, rows: list) -> Path:
    """`rows`: [(word, pos, sense_no, gloss)]. Schema verified 2026-09-23 against
    /data/alpha2-library/lexicon-enwiktionary-20260901.sqlite directly."""
    db_path = base_dir / "lexicon.sqlite"
    con = sqlite3.connect(str(db_path))
    con.execute("CREATE TABLE senses (id INTEGER PRIMARY KEY, word TEXT, lang TEXT, pos TEXT, sense_no INTEGER, "
                "gloss TEXT, etymology_ref TEXT, source TEXT, dump_date TEXT, page_rev TEXT)")
    for word, pos, sense_no, gloss in rows:
        con.execute("INSERT INTO senses (word, lang, pos, sense_no, gloss) VALUES (?, 'en', ?, ?, ?)", (word, pos, sense_no, gloss))
    con.commit()
    con.close()
    return db_path


def _lexicon_rows(root: Path):
    return [r for r in read_tape(root) if r.get("meta", {}).get("source") == "lexicon"]


class TestLookupGloss(unittest.TestCase):
    def test_picks_the_first_gloss_by_sense_no(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 2, "A second sense."), ("zog", "Noun", 1, "A made up test word.")])
        words, text = lexicon_sense._lookup_gloss(str(db), "zog", 8, 8)
        self.assertEqual(words, ["a", "made", "up", "test", "word"])
        self.assertEqual(text, "a made up test word")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_sense_no_ties_broken_by_id_the_reality_verified_against_the_real_lexicon(self) -> None:
        """The real lexicon's "cat" carries Verb sense_no=1, Noun sense_no=1, Adjective sense_no=1 (verified
        2026-09-23) -- `sense_no` alone is not a total order; `id` (insertion order, the primary key) is."""
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("cat", "Verb", 1, "To hoist an anchor."), ("cat", "Noun", 1, "A mammal.")])
        words, text = lexicon_sense._lookup_gloss(str(db), "cat", 8, 8)
        self.assertEqual(text, "to hoist an anchor", "the LOWER id (inserted first) wins the tie")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_a_gloss_that_cleans_to_nothing_tries_the_next_sense(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("the", "Pronoun", 1, "."), ("the", "Preposition", 2, "For each.")])
        words, text = lexicon_sense._lookup_gloss(str(db), "the", 8, 8)
        self.assertEqual(text, "for each")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_unknown_word_returns_empty(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A word.")])
        words, text = lexicon_sense._lookup_gloss(str(db), "vex", 8, 8)
        self.assertEqual(words, []); self.assertEqual(text, "")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_every_gloss_empty_or_unclean_returns_empty(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "."), ("zog", "Noun", 2, ""), ("zog", "Noun", 3, "42 -- !!")])
        words, text = lexicon_sense._lookup_gloss(str(db), "zog", 8, 8)
        self.assertEqual(words, [])
        shutil.rmtree(tmp, ignore_errors=True)

    def test_long_gloss_truncated_to_max_words(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        gloss = " ".join(f"w{i}" for i in range(20))
        db = _write_lexicon(tmp, [("zog", "Noun", 1, gloss)])
        words, _text = lexicon_sense._lookup_gloss(str(db), "zog", 3, 8)
        self.assertEqual(len(words), 3)
        shutil.rmtree(tmp, ignore_errors=True)


class TestMomentId(unittest.TestCase):
    def test_deterministic(self) -> None:
        self.assertEqual(lexicon_sense._moment_id("zog", "q-0"), lexicon_sense._moment_id("zog", "q-0"))

    def test_distinct_qids_for_the_same_word_get_distinct_moments(self) -> None:
        a = lexicon_sense._moment_id("zog", "q-0")
        b = lexicon_sense._moment_id("zog", "q-1")
        self.assertNotEqual(a, b)

    def test_starts_with_lex(self) -> None:
        self.assertTrue(lexicon_sense._moment_id("zog", "q-0").startswith("lex"))


class TestLexiconDoorLive(unittest.TestCase):
    def test_answers_a_known_word_ear_then_eye_and_marks_answered(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A made up test word.")])
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        (root / "world" / "questions" / "q-0.json").write_text(json.dumps({"q": "what-is", "word": "zog"}))

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: lexicon_sense.sense(
            tape.publish, stop_event, sqlite_path=str(db), root=root, canvas=128, period=0.1, words=8, letters=8),
            daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len(_lexicon_rows(root)) < 6 and time.time() < deadline:
            time.sleep(0.1)
        stop_event.set()
        t.join(timeout=5.0)

        rows = _lexicon_rows(root)
        self.assertEqual(len(rows), 6, f"5 gloss words + 1 line = 6 rows, got {rows}")
        ears = [r for r in rows if r["sense"] == "ear"]
        eyes = [r for r in rows if r["sense"] == "eye"]
        self.assertEqual([r["meta"]["word"] for r in ears], ["a", "made", "up", "test", "word"])
        self.assertEqual(len(eyes), 1)
        self.assertEqual(eyes[0]["meta"]["answers"], "zog")
        self.assertEqual(eyes[0]["meta"]["gloss"], "a made up test word")
        moments = {r["meta"]["moment"] for r in rows}
        self.assertEqual(len(moments), 1)
        self.assertTrue(next(iter(moments)).startswith("lex"))
        self.assertLess(ears[-1]["seq"], eyes[0]["seq"], "every ear row precedes the eye row")

        self.assertFalse((root / "world" / "questions" / "q-0.json").exists())
        self.assertTrue((root / "world" / "questions" / "q-0.answered.json").exists())

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_unknown_word_marks_unanswered_and_publishes_nothing(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A word.")])
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        (root / "world" / "questions" / "q-0.json").write_text(json.dumps({"q": "what-is", "word": "vex"}))

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: lexicon_sense.sense(
            tape.publish, stop_event, sqlite_path=str(db), root=root, canvas=128, period=0.05, words=8, letters=8),
            daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while not (root / "world" / "questions" / "q-0.unanswered.json").exists() and time.time() < deadline:
            time.sleep(0.05)
        time.sleep(0.3)
        stop_event.set()
        t.join(timeout=5.0)

        self.assertTrue((root / "world" / "questions" / "q-0.unanswered.json").exists())
        self.assertEqual(_lexicon_rows(root), [])

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_a_non_what_is_or_wordless_file_is_left_untouched(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A word.")])
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        (root / "world" / "questions" / "q-0.json").write_text(json.dumps({"q": "is", "word": "zog"}))
        (root / "world" / "questions" / "q-1.json").write_text(json.dumps({"q": "what-is"}))   # no word at all

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: lexicon_sense.sense(
            tape.publish, stop_event, sqlite_path=str(db), root=root, canvas=128, period=0.05, words=8, letters=8),
            daemon=True)
        t.start()
        time.sleep(0.6)
        stop_event.set()
        t.join(timeout=5.0)

        self.assertTrue((root / "world" / "questions" / "q-0.json").exists())
        self.assertTrue((root / "world" / "questions" / "q-1.json").exists())
        self.assertEqual(_lexicon_rows(root), [])

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_two_distinct_questions_for_the_same_word_both_get_answered_with_distinct_moments(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A made up test word.")])
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        (root / "world" / "questions" / "q-0.json").write_text(json.dumps({"q": "what-is", "word": "zog"}))
        (root / "world" / "questions" / "q-1.json").write_text(json.dumps({"q": "what-is", "word": "zog"}))

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: lexicon_sense.sense(
            tape.publish, stop_event, sqlite_path=str(db), root=root, canvas=128, period=0.05, words=8, letters=8),
            daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len(_lexicon_rows(root)) < 12 and time.time() < deadline:
            time.sleep(0.05)
        stop_event.set()
        t.join(timeout=5.0)

        rows = _lexicon_rows(root)
        moments = {r["meta"]["moment"] for r in rows}
        self.assertEqual(len(moments), 2, "each question, though about the same word, gets its own moment")
        self.assertTrue((root / "world" / "questions" / "q-0.answered.json").exists())
        self.assertTrue((root / "world" / "questions" / "q-1.answered.json").exists())

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


class TestDeclaredLexiconConfigArming(unittest.TestCase):
    def test_gated_true(self) -> None:
        self.assertTrue(lexicon_sense.LEXICON_DOOR_GATED)

    def test_arms_from_the_genomes_own_line(self) -> None:
        from creature import body as body_module
        declared = {"DOOR_LEXICON": {"sqlite": "/data/alpha2-library/lexicon-enwiktionary-20260901.sqlite"}}
        self.assertEqual(body_module._declared_lexicon_config(declared), declared["DOOR_LEXICON"])

    def test_undeclared_arms_nothing(self) -> None:
        from creature import body as body_module
        self.assertIsNone(body_module._declared_lexicon_config({}))


class TestLexiconMeetsBody(unittest.TestCase):
    def test_a_lexicon_moment_produces_a_meet_edge(self) -> None:
        """The mind needs NO change to CONSUME a lexicon row (same reasoning as read.py's own proof) --
        `_consume_eye` reads `meta.source` only to journal it."""
        tmp = Path(tempfile.mkdtemp())
        db = _write_lexicon(tmp, [("zog", "Noun", 1, "A made up test word.")])
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        (root / "world" / "questions" / "q-0.json").write_text(json.dumps({"q": "what-is", "word": "zog"}))
        meets_at_zero = GENOME_PATH.read_text().replace(
            "STAGE  1 senses   moments 0..200", "STAGE  1 senses   moments 0..0").replace(
            "STAGE  2 meet     moments 200..", "STAGE  2 meet     moments 0..")
        genome_path = tmp / "meet0.genome"
        genome_path.write_text(meets_at_zero)

        body = Body(root, genome_path)
        fn = functools.partial(lexicon_sense.sense, sqlite_path=str(db), root=root, canvas=128, period=0.1,
                               words=8, letters=8)
        body.add_sense("lexicon", fn)
        body.start()
        try:
            deadline = time.time() + 10.0
            while len(_lexicon_rows(root)) < 2 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
        finally:
            body.stop()

        org = body.mind.org
        self.assertGreater(len(org.edges_log), 0)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
