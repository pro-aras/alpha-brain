# edit: Claude (Sonnet 5, ALPHA4-2 builder B3), 2026-09-23 17:2x +0400 — A42-B3 task 2 (docs/ALPHA4-2-PREREG.md
# §2.3, branch A, ADOPTED by Ahmad 2026-09-23 16:56 +0400 -- "yes fix that Gutenberg part"; his 16:56 amendment
# on top of the original brief: the clause WILL be declared in the next lives' genomes tonight, so its LIVE
# behaviour matters, not only its inertness when absent). creature/senses/read.py's `_doc_sentences` and
# `sense()`, plus creature/body.py's wiring, test-first.
from __future__ import annotations

import inspect
import re
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature import body as body_module
from creature.senses import read as read_sense
from creature.senses import read_common
from creature.tape import Tape, read_tape

REAL_LIBRARY = Path("/data/alpha3-library")           # READ-ONLY throughout this file -- never written to.
REAL_SHELF_DB = REAL_LIBRARY / "SHELF.sqlite"
REAL_PG14640_REL = "G1-G3/readers/pg14640.txt"
REAL_PG14640 = REAL_LIBRARY / REAL_PG14640_REL

# PREREG §2.3's own list of licence-only tokens (A4-LADDER-PREREG §3.1 / this task's Q3 probe), lower-cased and
# truncated to the ear's real `letters` limit (8, genome/ALPHA4.genome's `SENSE ear letters 8`) -- the SAME
# cleaning `creature/senses/read_common.words_of` applies before a word ever reaches the tape, so this is what
# an ear row for "Gutenberg" or "trademark" actually LOOKS LIKE, not the dictionary spelling.
_MARKER_WORDS = ("gutenberg", "license", "licence", "trademark", "distribution", "donations",
                  "foundation", "copyright", "agreement", "liability", "warranty")
_MARKER_EAR_FORMS = {read_common.words_of(w, max_words=1, letters=8)[0] for w in _MARKER_WORDS}
_FORBIDDEN_PHRASES = ("gutenberg", "literary archive foundation", "www.gutenberg.org")


def _write_shelf_pointing_at(tmp_dir: Path, doc_id: str, real_abs_path: Path) -> Path:
    """A throwaway SHELF.sqlite (matching /data/alpha3-library/SHELF.sqlite's real schema, tests/creature/
    test_read_door.py's own convention) whose ONE row's `path` is the REAL file's ABSOLUTE path. `base_dir /
    path` on an absolute `path` returns the absolute path unchanged (pathlib's own rule for `/`), so
    `_doc_sentences`/`sense()` read the REAL file through their real production code path without this test
    writing anywhere near the read-only library."""
    db_path = tmp_dir / "shelf.sqlite"
    con = sqlite3.connect(str(db_path))
    con.execute("CREATE TABLE docs (doc_id TEXT PRIMARY KEY, path TEXT NOT NULL, format TEXT NOT NULL, "
                "title TEXT, source_class TEXT, licence TEXT, bytes INTEGER, sha256 TEXT, catalogued_at TEXT)")
    con.execute("INSERT INTO docs (doc_id, path, format, title, source_class, bytes) VALUES (?,?,?,?,?,?)",
                (doc_id, str(real_abs_path), "text", doc_id, "primary", real_abs_path.stat().st_size))
    con.commit(); con.close()
    return db_path


def _write_curriculum(tmp_dir: Path) -> Path:
    p = tmp_dir / "CURRICULUM.md"
    p.write_text("# a curriculum\n\nno per-doc order here.\n")
    return p


class TestDocSentencesMarkerLogic(unittest.TestCase):
    """Planted docs -- the marker-finding rule in isolation, before the real file is ever touched."""

    def _doc(self, tmp: Path, text: str) -> None:
        p = tmp / "a.txt"; p.write_text(text)
        return p

    def test_both_markers_present_keeps_only_the_body_marker_lines_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            text = "HEADER JUNK.\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\nThe cat sat. The dog ran.\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\nLICENCE JUNK.\n"
            self._doc(tmp, text)
            on = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=True)
            self.assertEqual(on, ["The cat sat.", "The dog ran."])
            self.assertNotIn("HEADER", " ".join(on)); self.assertNotIn("LICENCE", " ".join(on))
            self.assertNotIn("START OF", " ".join(on)); self.assertNotIn("END OF", " ".join(on))

    def test_no_markers_is_byte_identical_to_flag_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            text = "The cat sat. The dog ran.\n"
            self._doc(tmp, text)
            on = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=True)
            off = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=False)
            default = read_sense._doc_sentences(tmp, "a.txt")   # the default (no third arg at all) -- pre-task-2 call shape
            self.assertEqual(on, off); self.assertEqual(on, default)
            self.assertEqual(on, ["The cat sat.", "The dog ran."])

    def test_only_start_marker_present_falls_back_to_the_whole_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            text = "*** START OF THE PROJECT GUTENBERG EBOOK X ***\nThe cat sat.\n"
            self._doc(tmp, text)
            on = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=True)
            off = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=False)
            self.assertEqual(on, off, "defensive: one marker is not enough to trust the boundary")

    def test_only_end_marker_present_falls_back_to_the_whole_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            text = "The cat sat.\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\n"
            self._doc(tmp, text)
            on = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=True)
            off = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=False)
            self.assertEqual(on, off)

    def test_end_marker_before_start_marker_falls_back_to_the_whole_file(self) -> None:
        """A pathological ordering (an END with no START before it, then a later START with nothing after it
        counting as its own END): the search for END only ever looks AFTER the found START, so this can only
        ever read as 'no END found' -- never a body that runs backwards."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            text = "*** END OF SOMETHING ELSE ***\nJunk.\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\nThe cat sat.\n"
            self._doc(tmp, text)
            on = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=True)
            off = read_sense._doc_sentences(tmp, "a.txt", gutenberg_body_only=False)
            self.assertEqual(on, off)


@unittest.skipUnless(REAL_SHELF_DB.exists() and REAL_PG14640.exists(), "the real shelf library is not present on this box")
class TestDesignersProbeReproducedOnTheRealShelf(unittest.TestCase):
    """The PREREG's own Q2 probe (docs/ALPHA4-2-PREREG.md §11 Q2, on /data/alpha3-library/SHELF.sqlite,
    READ-ONLY): 129 header words, 10,649 total, 2,909 from the END marker's own line, 269 of 2,094 nursery
    docs carry both markers. Reproduced here with the SAME method the PREREG cites (`len(text.split())`,
    plain whitespace tokens -- NOT read_common.words_of's cleaned/truncated form, a different pipeline used
    for a different count in the same PREREG paragraph) as a control that this task's marker-finding logic
    sits on the boundaries the PREREG's own numbers were computed from, not merely near them."""

    def test_pg14640_header_body_licence_word_counts(self) -> None:
        text = REAL_PG14640.read_text()
        start = text.find("*** START OF")
        end = text.find("*** END OF", start + len("*** START OF"))
        self.assertNotEqual(start, -1); self.assertNotEqual(end, -1)
        start_line_end = text.find("\n", start)
        header = text[:start]
        body = text[start_line_end + 1:end]
        licence_from_marker = text[end:]
        self.assertEqual(len(header.split()), 129, "PREREG §11 Q2's own header-word count")
        self.assertEqual(len(text.split()), 10649, "PREREG §11 Q2's own total-word count")
        self.assertEqual(len(licence_from_marker.split()), 2909, "PREREG §11 Q2's own 'from the END marker's own line' count")
        self.assertGreater(len(body.split()), 0, "the body itself is non-empty")

    def test_269_of_2094_nursery_docs_carry_both_markers(self) -> None:
        con = sqlite3.connect(f"file:{REAL_SHELF_DB}?mode=ro", uri=True)
        try:
            cur = con.cursor()
            cur.execute("SELECT doc_id, path FROM docs WHERE format='text' AND path NOT LIKE '%holdout%' AND path NOT LIKE '%.jsonl'")
            rows = [(str(r[0]), str(r[1])) for r in cur.fetchall()]
        finally:
            con.close()
        self.assertEqual(len(rows), 2094, "PREREG §11 Q2's own nursery doc count")
        both = 0
        for _doc_id, path in rows:
            text = (REAL_LIBRARY / path).read_text(errors="replace")
            s = text.find("*** START OF")
            if s != -1 and text.find("*** END OF", s + len("*** START OF")) != -1:
                both += 1
        self.assertEqual(both, 269, "PREREG §11 Q2's own count of nursery docs carrying both markers")


@unittest.skipUnless(REAL_PG14640.exists(), "the real pg14640.txt is not present on this box")
class TestDocSentencesOnTheRealFirstReader(unittest.TestCase):
    """Ahmad's 16:56 ask, at the `_doc_sentences` level ('acceptable per the coordinator'): no returned
    sentence contains a forbidden phrase with the flag ON; the licence sentences ARE present with it OFF
    (the negative control); the first body sentence is pinned and printed."""

    def test_flag_on_no_forbidden_phrase_and_first_sentence_pinned(self) -> None:
        base_dir = REAL_PG14640.parent
        on = read_sense._doc_sentences(base_dir, REAL_PG14640.name, gutenberg_body_only=True)
        self.assertGreater(len(on), 0)
        joined_lower = " ".join(on).lower()
        for phrase in _FORBIDDEN_PHRASES:
            self.assertNotIn(phrase, joined_lower, f"{phrase!r} must not reach a sentence with the flag ON")
        # split_sentences does not cut on ':' -- the real first sentence runs to the first '.'/'!'/'?', pinned
        # exactly (not approximated) so a change to either the source file or split_sentences is caught here.
        first = on[0]
        print(f"[A42-B3 task 2] pg14640's first body sentence (flag ON): {first!r}")
        self.assertEqual(first, "[Transcriber's Notes: Welcome to the schoolroom of 1900.")

    def test_flag_off_licence_sentences_present_negative_control(self) -> None:
        base_dir = REAL_PG14640.parent
        off = read_sense._doc_sentences(base_dir, REAL_PG14640.name, gutenberg_body_only=False)
        joined_lower = " ".join(off).lower()
        for phrase in _FORBIDDEN_PHRASES:
            self.assertIn(phrase, joined_lower, f"{phrase!r} must be present with the flag OFF (negative control)")


@unittest.skipUnless(REAL_PG14640.exists(), "the real pg14640.txt is not present on this box")
class TestRealShelfThroughTheSenseRoad(unittest.TestCase):
    """Ahmad's STRONGER ask (16:56): the road the BODY actually walks -- `read_sense.sense()` in a thread
    (tests/creature/test_read_door.py's own pattern), a real `Tape`, `stop_event.set()` once rows land, then
    read back the published TAPE rows exactly as the mind would consume them. PREREG line 99's own clause:
    the licence's marker words 'never reach read/HEARD.json' -- checked here one level upstream, on the ear
    rows the sense actually PUBLISHES (HEARD.json is populated FROM these same rows in creature/mind.py)."""

    def _run_sense(self, gutenberg_body_only: bool, seconds: float = 6.0):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            shelf = _write_shelf_pointing_at(tmp, "pg14640", REAL_PG14640.resolve())
            curriculum = _write_curriculum(tmp)
            root = Path(tempfile.mkdtemp())
            tape = Tape(root)
            stop_event = threading.Event()
            t = threading.Thread(target=lambda: read_sense.sense(
                tape.publish, stop_event, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
                canvas=128, period=0.05, words=4, letters=8, gutenberg_body_only=gutenberg_body_only), daemon=True)
            t.start()
            deadline = time.time() + seconds
            rows = []
            while time.time() < deadline:
                rows = [r for r in read_tape(root) if r.get("meta", {}).get("source") == "shelf"]
                if len(rows) >= 40:      # enough ear rows to have walked well past the header either way
                    break
                time.sleep(0.1)
            stop_event.set(); t.join(timeout=5.0)
            import shutil
            shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)
            return rows

    def test_flag_on_no_forbidden_ear_word_reaches_the_tape(self) -> None:
        rows = self._run_sense(gutenberg_body_only=True)
        ears = [r for r in rows if r["sense"] == "ear"]
        self.assertGreater(len(ears), 0, "positive control: the sense actually published ear rows")
        ear_words = {r["meta"]["word"] for r in ears}
        hit = ear_words & _MARKER_EAR_FORMS
        self.assertEqual(hit, set(), f"no licence/Gutenberg marker word (ear form) may reach the tape with the flag ON, got {hit}")

    def test_flag_off_a_forbidden_ear_word_does_reach_the_tape_eventually(self) -> None:
        """The negative control for the test above: WITHOUT the flag, the reader walks the header first (129
        words at 4 words/moment ~ 33 moments), and the doc's own title line ("The Project Gutenberg eBook of
        McGuffey's...") carries 'gutenberg' among its first few words -- it must appear near-immediately,
        proving this harness can see the word when it is really there (#91's rule: a 0-finding check needs a
        positive control)."""
        rows = self._run_sense(gutenberg_body_only=False, seconds=6.0)
        ears = [r for r in rows if r["sense"] == "ear"]
        ear_words = [r["meta"]["word"] for r in ears]
        self.assertIn(read_common.words_of("gutenberg", max_words=1, letters=8)[0], ear_words,
                      "positive control: the header's own title word reaches the tape when the flag is OFF")


class TestBodyWiresTheDeclaredFlagIntoTheSensePartial(unittest.TestCase):
    """creature/body.py's `main()` blocks forever once wired (a `while not stop_requested.is_set()` CLI loop
    registering SIGTERM/SIGINT) -- not practically unit-testable end-to-end in isolation. This pins the exact
    source line that threads SENSE_READ's declared flag into the `functools.partial` `add_sense("read", ...)`
    receives, so a regression (the kwarg silently dropped, or read from the wrong dict) fails a fast test
    instead of only a live life. The BEHAVIOURAL half of this wiring (does `sense()` actually change what it
    publishes when the kwarg is True) is TestRealShelfThroughTheSenseRoad above, on the exact same function."""

    def test_the_partial_reads_gutenberg_body_only_from_the_declared_config(self) -> None:
        src = inspect.getsource(body_module.main)
        self.assertIn('gutenberg_body_only=bool(read_cfg.get("gutenberg_body_only"))', src,
                      "the SENSE_READ partial must thread the declared flag (default False when absent)")
        # the read-cfg->kwarg arithmetic itself, isolated from the surrounding CLI plumbing:
        self.assertFalse(bool({}.get("gutenberg_body_only")))
        self.assertTrue(bool({"gutenberg_body_only": True}.get("gutenberg_body_only")))


if __name__ == "__main__":
    unittest.main()
