# edit: Claude (Fable 5.1), 2026-09-23 03:02 +0400 — ALPHA 4 integration seams, written by the third hand on the merged bytes (#235's law):
# H×I (the lexicon door's `<qid>.unanswered.json` is what the web door serves), and the reading share as a TAPE FACT
# (read.py HEARD.json → self_exam --read-words → the SIT row → the judge's (b)). Each RED on the merged tree before the
# integration patch, GREEN after.
from __future__ import annotations

import json, os, shutil, sqlite3, sys, tempfile, threading, unittest
from pathlib import Path


def _tiny_lexicon(db_path: Path) -> None:
    con = sqlite3.connect(str(db_path))
    con.execute("CREATE TABLE senses (id INTEGER PRIMARY KEY, word TEXT, lang TEXT, pos TEXT, sense_no INTEGER, gloss TEXT, "
                "etymology_ref TEXT, source TEXT, dump_date TEXT, page_rev TEXT)")
    con.execute("INSERT INTO senses (word, lang, pos, sense_no, gloss) VALUES ('cat', 'en', 'Noun', 1, 'a small furry animal')")
    con.commit(); con.close()


class LexiconUnansweredFeedsTheWebDoor(unittest.TestCase):
    """H×I: a word the dictionary lacks is RENAMED `<qid>.unanswered.json` by the lexicon door, and that exact file
    is what the web door serves once STAGE 4 is on STATUS (fetcher mocked; no network)."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.q_dir = self.root / "world" / "questions"; self.q_dir.mkdir(parents=True)
        self.db = self.root / "lex.sqlite"; _tiny_lexicon(self.db)
        (self.q_dir / "q-7.json").write_text(json.dumps({"id": "q-7", "q": "what-is", "word": "zzzq"}))

    def test_unanswered_rename_is_what_the_web_door_reads(self) -> None:
        from creature.senses import lexicon, web, read_common
        rows = []
        def publish(sense, payload, meta, ext):
            rows.append((sense, meta)); return {"seq": len(rows)}
        lexicon._answer_one(publish, str(self.db), self.q_dir, 128, 8, 8, read_common.DEFAULT_FONT_PATH)
        self.assertTrue((self.q_dir / "q-7.unanswered.json").exists(), sorted(os.listdir(self.q_dir)))
        self.assertEqual(rows, [])   # no gloss -> nothing shown
        self.assertEqual(web.unanswered_questions(self.q_dir, set()), [("q-7", "zzzq")])
        self.assertEqual(web.unanswered_questions(self.q_dir, {"q-7"}), [])

    def test_web_door_fetches_the_unanswered_question_at_stage_4(self) -> None:
        from creature.senses import lexicon, web, read_common
        lexicon._answer_one(lambda *a: {"seq": 1}, str(self.db), self.q_dir, 128, 8, 8, read_common.DEFAULT_FONT_PATH)
        (self.root / "STATUS.json").write_text(json.dumps({"stage": 4}))
        published = []
        stop = threading.Event()
        def publish(sense, payload, meta, ext):
            published.append((sense, dict(meta)))
            if sense == "web":
                stop.set()
            return {"seq": len(published)}
        def fetcher(url, timeout, ua):   # builder I's own fetcher shape: (status, body, headers)
            return 200, json.dumps({"extract": "a made up thing with words"}).encode("utf-8"), None
        th = threading.Thread(target=web.sense, args=(publish, stop, self.root),
                              kwargs=dict(questions_dir=self.q_dir, hold_file=self.root / "world" / "HOLD", floor_s=0.02,
                                          per_hour=60, open_at_stage=4, poll_period=0.01, fetcher=fetcher), daemon=True)
        th.start(); th.join(timeout=8.0)   # a door that never serves the question must FAIL here, never hang the suite
        stop.set(); th.join(timeout=2.0)
        web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 1, published[:3])
        self.assertIn("q-7", json.dumps(web_rows[0]))


class TheReadingShareIsATapeFact(unittest.TestCase):
    def test_heard_words_record_is_distinct_ordered_and_atomic(self) -> None:
        from creature.senses import read
        root = Path(tempfile.mkdtemp()); (root / "read").mkdir()
        self.assertEqual(read.heard_words(root), [])
        read._record_heard(root, ["the", "cat", "the"]); read._record_heard(root, ["sat", "cat"])
        self.assertEqual(read.heard_words(root), ["the", "cat", "sat"])
        (root / "read" / read.HEARD_NAME).write_text("{not json")
        self.assertEqual(read.heard_words(root), [])   # a torn file reads as empty, never a crash

    def test_sit_forwards_read_share(self) -> None:
        from creature.senses import sit
        self.assertEqual(sit._read_share_of({"read_share": 0.7}), 0.7)
        self.assertIsNone(sit._read_share_of({"read_share": None}))
        self.assertIsNone(sit._read_share_of({}))

    def test_judge_reads_the_share_off_the_last_two_sit_rows(self) -> None:
        from creature.mind import Mind
        m = Mind.__new__(Mind)
        m._read_proxy_override = None
        m._sit_readings = [(0.99, 0.96, 0.7), (0.99, 0.96, 0.65)]
        self.assertIs(m._read_proxy(), True)
        self.assertTrue(m._sit_composite_ok())        # (c) still reads its two numbers off the wider tuple
        m._sit_readings = [(0.99, 0.96, 0.7), (0.99, 0.96, 0.5)]
        self.assertIs(m._read_proxy(), False)
        m._sit_readings = [(0.99, 0.96, None), (0.99, 0.96, 0.9)]
        self.assertIsNone(m._read_proxy())          # a row without the number fails closed
        m._sit_readings = [(0.99, 0.96, 0.9)]
        self.assertIsNone(m._read_proxy())          # fewer than two rows

    def test_self_exam_reports_read_share_on_a_closed_root(self) -> None:
        """Plumbing on a REAL closed record (dry-life-1, 16 words, no shelf): a fabricated HEARD.json of five of its own
        words -> the report carries a read_share in [0, 1] (the value is the maker's words in a serif font, not a reading
        claim). A copy of the root, never the record (#212)."""
        src = Path("/data/dev/genome-lives/dry-life-1")
        if not (src / "state" / "organism.npz").exists():
            self.skipTest("dry-life-1 not on this box")
        root = Path(tempfile.mkdtemp()) / "life"; root.mkdir()
        for d in ("state", "tape", "exam"):
            if (src / d).exists():
                shutil.copytree(src / d, root / d)
        (root / "read").mkdir()
        L = json.loads((root / "state" / "ledger.json").read_text())
        words = sorted({w for ws in L["words"].values() for w in ws if w})[:5]
        self.assertGreaterEqual(len(words), 5)
        (root / "read" / "HEARD.json").write_text(json.dumps(words))
        from tools import self_exam
        genome = src / "code" / "genome" / "LIFE.genome"
        old_argv = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome), "--held", "3", "--check-tape", "0", "--read-words", "5"]
            self_exam.main()
        finally:
            sys.argv = old_argv
        reports = sorted(p for p in (root / "exam").glob("*.json") if p.name != "LAST.json")
        data = json.loads(reports[-1].read_text())
        self.assertIn("read_share", data); self.assertEqual(data["read_words_n"], 5)
        self.assertIsNotNone(data["read_share"], "five heard words were given; the share must be a number")
        self.assertTrue(0.0 <= data["read_share"] <= 1.0, data["read_share"])


if __name__ == "__main__":
    unittest.main()
