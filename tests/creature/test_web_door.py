# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §3: DOOR web. No
# network in any test (the brief's own rule) — every fetch is MOCKED via the injected `fetcher`/`now`.
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import List, Tuple

from creature.senses import web as web_module


def _make_root(stage) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "STATUS.json").write_text(json.dumps({"stage": stage}))
    (root / "world" / "questions").mkdir(parents=True)
    return root


def _plant_question(root: Path, qid: str, word: str, status: str = "unanswered") -> None:
    """edit: Claude (Fable 5.1), 2026-09-23 03:03 +0400 — at integration: builder H's REAL convention (creature/senses/lexicon.py renames
    the question file to `<qid>.unanswered.json` / `<qid>.answered.json`; the body still carries id/q/word; no sidecar)."""
    qdir = root / "world" / "questions"
    (qdir / f"{qid}.{status}.json").write_text(json.dumps({"id": qid, "q": "what-is", "word": word}))


def _ok_fetcher(u, t, ua):
    return 200, json.dumps({"extract": "a definition of something"}).encode(), None


def _run(root: Path, seconds: float, **kwargs):
    published: List[Tuple[str, dict]] = []
    lock = threading.Lock()

    def fake_publish(sense, payload, meta, ext):
        with lock:
            published.append((sense, meta))
        return {"seq": len(published)}

    stop = threading.Event()
    kwargs.setdefault("fetcher", _ok_fetcher)
    kwargs.setdefault("poll_period", 0.01)
    kwargs.setdefault("floor_s", 0.02)

    def go():
        web_module.sense(fake_publish, stop, root, **kwargs)

    th = threading.Thread(target=go, daemon=True)
    th.start()
    time.sleep(seconds)
    stop.set()
    th.join(timeout=2.0)
    return published


class TestUnansweredQuestions(unittest.TestCase):
    def test_reads_only_unanswered_with_a_word(self) -> None:
        root = _make_root(4)
        qdir = root / "world" / "questions"
        _plant_question(root, "0", "zog", status="unanswered")
        _plant_question(root, "1", "bar", status="answered")
        (qdir / "2.unanswered.json").write_text(json.dumps({"id": "2", "q": "what-is"}))   # no word
        (qdir / "3.json").write_text(json.dumps({"id": "3", "q": "what-is", "word": "pending"}))  # not yet looked up by the lexicon door: not served
        out = web_module.unanswered_questions(qdir, exclude=set())
        self.assertEqual(out, [("0", "zog")])

    def test_excludes_ids_in_the_exclude_set(self) -> None:
        root = _make_root(4)
        qdir = root / "world" / "questions"
        _plant_question(root, "0", "zog")
        out = web_module.unanswered_questions(qdir, exclude={"0"})
        self.assertEqual(out, [])


class TestWebDoorGating(unittest.TestCase):
    def test_stage_3_yields_zero_fetches(self) -> None:
        root = _make_root(3)
        _plant_question(root, "0", "zog")
        published = _run(root, 0.2, open_at_stage=4)
        self.assertEqual([m for s, m in published if s == "web"], [])

    def test_stage_4_fetches(self) -> None:
        root = _make_root(4)
        _plant_question(root, "0", "zog")
        published = _run(root, 0.2, open_at_stage=4)
        web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 1)
        self.assertEqual(web_rows[0]["status"], "ok")
        self.assertEqual(web_rows[0]["question_id"], "0")
        self.assertEqual(web_rows[0]["word"], "zog")

    def test_no_status_json_yet_is_treated_as_stage_not_reached(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "world" / "questions").mkdir(parents=True)
        _plant_question(root, "0", "zog")
        published = _run(root, 0.15, open_at_stage=4)   # no STATUS.json written at all
        self.assertEqual([m for s, m in published if s == "web"], [])

    def test_61_questions_60_fetches_1_refused_rate(self) -> None:
        root = _make_root(4)
        for i in range(61):
            _plant_question(root, str(i), f"thing{i}")
        published = _run(root, 2.0, per_hour=60, open_at_stage=4)
        web_rows = [m for s, m in published if s == "web"]
        made = [m for m in web_rows if m["status"] in ("ok", "failed")]
        refused_rate = [m for m in web_rows if m["status"] == "refused_rate"]
        self.assertEqual(len(made), 60, f"expected 60 made, got {len(made)}: {[m['status'] for m in web_rows]}")
        self.assertEqual(len(set(m["question_id"] for m in made)), 60, "every made fetch must be a DISTINCT question")
        self.assertEqual(len(refused_rate), 1, f"expected exactly 1 refused_rate row (de-duplicated), got {len(refused_rate)}")

    def test_hold_file_present_yields_zero_fetches(self) -> None:
        root = _make_root(4)
        hold_dir = root / "world"
        hold_file = hold_dir / "HOLD"
        hold_file.write_text("held")
        _plant_question(root, "0", "zog")
        published = _run(root, 0.2, open_at_stage=4, hold_file=hold_file)
        web_rows = [m for s, m in published if s == "web"]
        made = [m for m in web_rows if m["status"] in ("ok", "failed")]
        self.assertEqual(len(made), 0, "the hold must block every real fetch")
        self.assertTrue(any(m["status"] == "refused_hold" for m in web_rows), "a hold refusal must be journaled")

    def test_floor_is_at_least_2_seconds_between_real_fetches(self) -> None:
        root = _make_root(4)
        _plant_question(root, "0", "zog")
        _plant_question(root, "1", "bar")
        timestamps: List[float] = []

        def timed_fetcher(u, t, ua):
            timestamps.append(time.monotonic())
            return 200, json.dumps({"extract": "x"}).encode(), None

        _run(root, 4.3, open_at_stage=4, floor_s=2.0, fetcher=timed_fetcher, poll_period=0.05)
        self.assertGreaterEqual(len(timestamps), 2, "expected two real fetches within 4.3 s at a 2.0 s floor")
        self.assertGreaterEqual(timestamps[1] - timestamps[0], 2.0)

    def test_wikipedia_404_falls_back_to_wiktionary(self) -> None:
        root = _make_root(4)
        _plant_question(root, "0", "zog")
        calls = []

        def fetcher(u, t, ua):
            calls.append(u)
            if "wikipedia" in u:
                return 404, b"{}", None
            return 200, json.dumps({"en": [{"partOfSpeech": "noun", "definitions": [{"definition": "a made-up word"}]}]}).encode(), None

        published = _run(root, 0.2, open_at_stage=4, fetcher=fetcher)
        web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 1)
        self.assertEqual(web_rows[0]["status"], "ok")
        self.assertIn("wiktionary", web_rows[0]["url"])
        self.assertTrue(web_rows[0]["had_extract"])
        self.assertEqual(len(calls), 2, "must have tried wikipedia THEN wiktionary")

    def test_transient_failure_is_retried_after_the_hour_not_before(self) -> None:
        """A single continuous sense() call, driven by a fake clock the test controls directly: the first
        attempt fails (a 503, transient); a moment later (real time, small) the clock has NOT yet advanced
        an hour, so the question must not be retried; once the fake clock is pushed past the hour, the
        SAME question is retried and this time succeeds."""
        root = _make_root(4)
        _plant_question(root, "0", "zog")
        calls: List[str] = []
        fail_until = [True]

        def fetcher(u, t, ua):
            calls.append(u)
            if fail_until[0]:
                return 503, None, "server error"
            return 200, json.dumps({"extract": "a real definition"}).encode(), None

        t = [1000.0]

        def fake_now():
            return t[0]

        published: List[Tuple[str, dict]] = []
        lock = threading.Lock()

        def fake_publish(sense, payload, meta, ext):
            with lock:
                published.append((sense, meta))
            return {}

        stop = threading.Event()
        th = threading.Thread(target=lambda: web_module.sense(
            fake_publish, stop, root, open_at_stage=4, floor_s=0.01, poll_period=0.01,
            fetcher=fetcher, now=fake_now), daemon=True)
        th.start()
        time.sleep(0.15)                       # let the first (failing) attempt happen
        with lock:
            first_web = [m for s, m in published if s == "web"]
        self.assertEqual(len(first_web), 1)
        self.assertEqual(first_web[0]["status"], "failed")
        calls_before_jump = len(calls)

        time.sleep(0.1)                        # real time passes, but the FAKE clock has not moved -- still within the hour
        with lock:
            still_one = len([m for s, m in published if s == "web"])
        self.assertEqual(still_one, 1, "a transient failure must not be retried before the hour is up")

        fail_until[0] = False
        t[0] += 3700.0                          # push the fake clock past the hour
        time.sleep(0.15)
        stop.set()
        th.join(timeout=2.0)

        with lock:
            web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 2, f"expected a retry after the hour; got {web_rows}")
        self.assertEqual(web_rows[1]["status"], "ok")
        self.assertGreater(len(calls), calls_before_jump)

    def test_real_read_common_publishes_the_record_with_rendered_true_and_ear_eye_rows(self) -> None:
        # edit: Claude (Fable 5.1), 2026-09-23 03:06 +0400 — this test pinned the STUB's behaviour (rendered False, no rows); builder H's real
        # read_common landed at integration and flipped the premise (#232 addendum (c): never pin the ABSENCE of a feature
        # another lane is building). With the real renderer: the record says rendered True and the extract's words are
        # heard and its line shown on web moments.
        root = _make_root(4)
        _plant_question(root, "0", "zog")
        published = _run(root, 0.3, open_at_stage=4)
        web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 1)
        self.assertTrue(web_rows[0]["rendered"])
        ears = [m for s, m in published if s == "ear"]; eyes = [m for s, m in published if s == "eye"]
        self.assertGreaterEqual(len(ears), 1); self.assertGreaterEqual(len(eyes), 1)
        self.assertTrue(all(m["source"] == "web" and m["moment"].startswith("web0") for m in ears + eyes))

    def test_a_fetch_with_no_content_still_counts_ok_and_is_not_retried(self) -> None:
        root = _make_root(4)
        _plant_question(root, "0", "zog")

        def empty_fetcher(u, t, ua):
            return 404, b"{}", None   # neither wikipedia nor wiktionary has anything -- a definitive, non-transient "nothing"

        published = _run(root, 0.2, open_at_stage=4, fetcher=empty_fetcher)
        web_rows = [m for s, m in published if s == "web"]
        self.assertEqual(len(web_rows), 1)
        self.assertEqual(web_rows[0]["status"], "ok")
        self.assertFalse(web_rows[0]["had_extract"])


class TestATapeCarryingWebRowsReplaysIdentically(unittest.TestCase):
    def test_two_independent_minds_consuming_the_same_web_tape_agree(self) -> None:
        """The sense's own OUTPUT (three real `web` rows: ok/failed/refused_rate, written through a real
        `creature.tape.Tape` so they carry real seq/payload-path shape) fed through TWO independent
        `Mind`s via DOOR_WEB — `_consume_web` is a pure function of the row (counters + one journal write,
        no clock/randomness), so this is the same law gate_g4.py's gate2/gate3 prove for the rest of the
        mind, applied to this builder's own new consumer."""
        from creature.mind import Mind
        from creature.tape import Tape
        from genome.machinery import parse_genome

        skel = (Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome").read_text()
        genome_text = skel + "\nDOOR     web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD\n"

        def build_tape(root: Path) -> None:
            tape = Tape(root)
            tape.publish("web", b'{"extract": "x"}', {"status": "ok", "question_id": "0", "word": "zog",
                                                         "url": "https://en.wikipedia.org/...", "http_status": 200,
                                                         "source": "web", "rendered": False, "had_extract": True}, "bin",
                         at="2026-09-23T00:00:00.000Z")
            tape.publish("web", b"", {"status": "failed", "question_id": "1", "word": "bar", "url": None,
                                       "http_status": None, "source": "web"}, "bin", at="2026-09-23T00:00:01.000Z")
            tape.publish("web", b"", {"status": "refused_rate", "question_id": "2", "word": "baz", "url": None,
                                       "http_status": None, "source": "web"}, "bin", at="2026-09-23T00:00:02.000Z")

        def consume_all(root: Path, gpath: Path) -> tuple:
            mind = Mind(gpath, root)
            for row in __import__("creature.tape", fromlist=["read_tape"]).read_tape(root):
                mind.consume(row)
            journals = sorted((root / "journal").glob("*.jsonl"))
            rows = [__import__("json").loads(l) for f in journals for l in f.read_text().splitlines()]
            web_journal = [r for r in rows if "web" in r]
            return (mind.web_fetches, mind.web_refused_rate, mind.web_refused_hold), web_journal

        results = []
        for _ in range(2):
            tmp = Path(tempfile.mkdtemp())
            root = tmp / "run"
            gpath = tmp / "g.genome"
            gpath.write_text(genome_text)
            parse_genome(genome_text)   # sanity: the genome itself parses before building the tape
            build_tape(root)
            results.append(consume_all(root, gpath))

        (counts_a, journal_a), (counts_b, journal_b) = results
        self.assertEqual(counts_a, (2, 1, 0), f"2 made [ok+failed] / 1 refused_rate / 0 refused_hold, got {counts_a}")
        self.assertEqual(counts_a, counts_b)
        self.assertEqual(journal_a, journal_b)


if __name__ == "__main__":
    unittest.main()
