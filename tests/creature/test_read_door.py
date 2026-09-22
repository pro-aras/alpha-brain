# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 00:57 +0400 — ALPHA4-H task 2 (docs/briefs/ALPHA4-H.md):
# creature/senses/read.py, test-first.
from __future__ import annotations

import functools
import shutil
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature.body import Body
from creature.senses import read as read_sense
from creature.senses import read_common
from creature.tape import Tape, read_tape

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _write_shelf(base_dir: Path, docs: list) -> Path:
    """`docs`: [(doc_id, relpath, text, format, extra_source_class)]. Writes each text file under
    `base_dir/relpath` and a `docs` table matching /data/alpha3-library/SHELF.sqlite's real schema
    (verified 2026-09-23 by reading it directly)."""
    db_path = base_dir / "SHELF.sqlite"
    con = sqlite3.connect(str(db_path))
    con.execute("CREATE TABLE docs (doc_id TEXT PRIMARY KEY, path TEXT NOT NULL, format TEXT NOT NULL, "
                "title TEXT, source_class TEXT, licence TEXT, bytes INTEGER, sha256 TEXT, catalogued_at TEXT)")
    for doc_id, relpath, text, fmt, source_class in docs:
        p = base_dir / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        con.execute("INSERT INTO docs (doc_id, path, format, title, source_class, bytes) VALUES (?,?,?,?,?,?)",
                    (doc_id, relpath, fmt, relpath, source_class, len(text.encode())))
    con.commit()
    con.close()
    return db_path


def _write_curriculum(base_dir: Path, text: str = "# a curriculum\n\nno per-doc order here.\n") -> Path:
    p = base_dir / "CURRICULUM.md"
    p.write_text(text)
    return p


def _shelf_rows(root: Path):
    return [r for r in read_tape(root) if r.get("meta", {}).get("source") == "shelf"]


class TestNurseryDocsOrderingAndExclusion(unittest.TestCase):
    def test_excludes_holdout_and_jsonl_and_non_text_format(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [
            ("a", "G1-G3/readers/a.txt", "The cat sat. The dog ran.", "text", "primary"),
            ("b", "K/mathematics/compare.holdout.jsonl", '{"q":1}', "text", "textbook"),
            ("c", "K/mathematics/compare.train.jsonl", '{"q":1}', "text", "textbook"),
            ("d", "College/x/y-holdout-notes.txt", "held out text.", "text", "primary"),
            ("e", "video/z.txt", "a transcript.", "text", "film"),
            ("f", "K/glyphs/latin/a.png", "not text", "image", "primary"),
        ])
        curriculum = _write_curriculum(tmp)
        got = read_sense._nursery_docs(str(shelf), str(curriculum))
        ids = [d for d, _p in got]
        self.assertIn("a", ids)
        self.assertIn("e", ids)
        self.assertNotIn("b", ids, "a .jsonl holdout file must never be shown")
        self.assertNotIn("c", ids, "a .jsonl exam family file must never be shown, holdout or not")
        self.assertNotIn("d", ids, "any path containing 'holdout' must never be shown")
        self.assertNotIn("f", ids, "only format='text' rows are the nursery shelf")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_class_band_order_K_then_G1G3_then_college_then_university(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [
            ("u", "University/z.txt", "u text.", "text", "primary"),
            ("c", "College/z.txt", "c text.", "text", "primary"),
            ("g", "G1-G3/readers/z.txt", "g text.", "text", "textbook"),
            ("k", "K/mathematics/z.txt", "k text.", "text", "textbook"),
        ])
        curriculum = _write_curriculum(tmp)
        got = read_sense._nursery_docs(str(shelf), str(curriculum))
        self.assertEqual([d for d, _p in got], ["k", "g", "c", "u"])
        shutil.rmtree(tmp, ignore_errors=True)

    def test_within_a_band_sorted_by_path(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [
            ("z", "G1-G3/readers/zzz.txt", "z.", "text", "primary"),
            ("a", "G1-G3/readers/aaa.txt", "a.", "text", "primary"),
        ])
        curriculum = _write_curriculum(tmp)
        got = read_sense._nursery_docs(str(shelf), str(curriculum))
        self.assertEqual([d for d, _p in got], ["a", "z"])
        shutil.rmtree(tmp, ignore_errors=True)

    def test_explicit_reading_order_section_is_honoured_when_present(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [
            ("a", "College/a.txt", "a.", "text", "primary"),
            ("b", "K/b.txt", "b.", "text", "primary"),
        ])
        curriculum = _write_curriculum(tmp, "# c\n\n## Reading order\n\n- College/a.txt\n- K/b.txt\n")
        got = read_sense._nursery_docs(str(shelf), str(curriculum))
        self.assertEqual([d for d, _p in got], ["a", "b"], "an explicit order overrides the class-band fallback")
        shutil.rmtree(tmp, ignore_errors=True)

    def test_real_curriculum_file_names_no_per_doc_order(self) -> None:
        real = Path("/data/alpha3-library/CURRICULUM.md")
        if not real.exists():
            self.skipTest("the real curriculum is not present on this box")
        self.assertIsNone(read_sense._explicit_order(real.read_text()),
                          "CURRICULUM.md was read in full 2026-09-23 and names no per-doc order -- a change here is a finding")


class TestChunking(unittest.TestCase):
    def test_short_sentence_one_chunk(self) -> None:
        got = read_sense._chunks_of("The cat sat.", words=8, letters=8)
        self.assertEqual(got, [["the", "cat", "sat"]])

    def test_long_sentence_splits_into_chunks_of_words_size(self) -> None:
        sentence = "one two three four five six seven eight nine ten"
        got = read_sense._chunks_of(sentence, words=8, letters=8)
        self.assertEqual(got, [["one", "two", "three", "four", "five", "six", "seven", "eight"], ["nine", "ten"]])

    def test_empty_sentence_no_chunks(self) -> None:
        self.assertEqual(read_sense._chunks_of("", words=8, letters=8), [])
        self.assertEqual(read_sense._chunks_of("42 -- !!", words=8, letters=8), [])


class TestMomentId(unittest.TestCase):
    def test_deterministic_from_doc_sentence_chunk(self) -> None:
        a = read_sense._moment_id("doc1", 0, 0)
        b = read_sense._moment_id("doc1", 0, 0)
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("read"))
        self.assertEqual(len(a), len("read") + 8)

    def test_distinct_for_distinct_chunks(self) -> None:
        ids = {read_sense._moment_id("doc1", 0, c) for c in range(3)}
        self.assertEqual(len(ids), 3)

    def test_word_moment_distinct_from_sentence_moment(self) -> None:
        sentence_m = read_sense._moment_id("doc1", 0, 0)
        word_m = read_sense._moment_id("doc1", 0, 0, word_ix=0)
        self.assertNotEqual(sentence_m, word_m)


class TestReadSenseLive(unittest.TestCase):
    def test_one_short_sentence_publishes_ear_then_eye_on_one_moment(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [("a", "G1-G3/readers/a.txt", "The cat sat.", "text", "primary")])
        curriculum = _write_curriculum(tmp)
        root = Path(tempfile.mkdtemp())

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: read_sense.sense(
            tape.publish, stop_event, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
            canvas=128, period=0.1, words=8, letters=8), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len(_shelf_rows(root)) < 4 and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set()
        t.join(timeout=5.0)

        rows = _shelf_rows(root)
        self.assertEqual(len(rows), 4, f"3 words + 1 line = 4 rows, got {rows}")
        ears = [r for r in rows if r["sense"] == "ear"]
        eyes = [r for r in rows if r["sense"] == "eye"]
        self.assertEqual([r["meta"]["word"] for r in ears], ["the", "cat", "sat"])
        self.assertEqual(len(eyes), 1)
        moments = {r["meta"]["moment"] for r in rows}
        self.assertEqual(len(moments), 1)
        self.assertTrue(next(iter(moments)).startswith("read"))
        self.assertEqual(eyes[0]["meta"]["doc_id"], "a")
        self.assertEqual(eyes[0]["meta"]["sentence_ix"], 0)
        self.assertEqual(eyes[0]["meta"]["chunk_ix"], 0)
        self.assertEqual(eyes[0]["meta"]["text"], "the cat sat")
        for r in rows:
            self.assertEqual(r["meta"]["source"], "shelf")
        self.assertLess(ears[0]["seq"], eyes[0]["seq"], "ear precedes eye (PREREG §2.2)")
        self.assertLess(ears[-1]["seq"], eyes[0]["seq"], "EVERY ear row precedes the eye row")

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_long_sentence_continues_on_a_second_moment(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        text = "one two three four five six seven eight nine ten."
        shelf = _write_shelf(tmp, [("a", "G1-G3/readers/a.txt", text, "text", "primary")])
        curriculum = _write_curriculum(tmp)
        root = Path(tempfile.mkdtemp())

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: read_sense.sense(
            tape.publish, stop_event, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
            canvas=128, period=0.1, words=8, letters=8), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len({r["meta"]["moment"] for r in _shelf_rows(root)}) < 2 and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set()
        t.join(timeout=5.0)

        rows = _shelf_rows(root)
        by_moment = {}
        for r in rows:
            by_moment.setdefault(r["meta"]["moment"], []).append(r)
        self.assertEqual(len(by_moment), 2, "10 words at 8/chunk = 2 chunks = 2 moments")
        eyes = sorted([r for r in rows if r["sense"] == "eye"], key=lambda r: r["meta"]["chunk_ix"])
        self.assertEqual([e["meta"]["chunk_ix"] for e in eyes], [0, 1])
        self.assertEqual(eyes[0]["meta"]["text"], "one two three four five six seven eight")
        self.assertEqual(eyes[1]["meta"]["text"], "nine ten")

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_cursor_resume_never_republishes(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [("a", "G1-G3/readers/a.txt", "The cat sat. The dog ran. The bird flew.", "text", "primary")])
        curriculum = _write_curriculum(tmp)
        root = Path(tempfile.mkdtemp())

        def run_until(min_rows, timeout=10.0):
            # period=2.0: wide apart from the poll granularity below, so "stop the instant we see
            # min_rows" never races the NEXT chunk starting to publish (no wall-clock guess, #158's law).
            tape = Tape(root)
            stop_event = threading.Event()
            t = threading.Thread(target=lambda: read_sense.sense(
                tape.publish, stop_event, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
                canvas=128, period=2.0, words=8, letters=8), daemon=True)
            t.start()
            deadline = time.time() + timeout
            while len(_shelf_rows(root)) < min_rows and time.time() < deadline:
                time.sleep(0.02)
            stop_event.set()
            t.join(timeout=5.0)

        run_until(4)   # exactly the first sentence's one chunk
        rows1 = _shelf_rows(root)
        self.assertEqual(len(rows1), 4, "must stop before the second sentence starts publishing")
        self.assertTrue((root / "read" / "CURSOR.json").exists())

        run_until(8)   # resume: must continue from the cursor, never re-publish the first sentence
        rows2 = _shelf_rows(root)
        self.assertEqual(len(rows2), 8)
        # every row from the first run must still be present, byte-identical, after the resume
        rows2_by_seq = {r["seq"]: r for r in rows2}
        for r in rows1:
            self.assertEqual(rows2_by_seq[r["seq"]]["meta"], r["meta"])
        # the second sentence's words must appear exactly once (no duplicate moment)
        second_sentence_eyes = [r for r in rows2 if r["sense"] == "eye" and r["meta"]["sentence_ix"] == 1]
        self.assertEqual(len(second_sentence_eyes), 1)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_one_word_moments_shape_publishes_a_moment_per_word_plus_the_sentence_moment(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [("a", "G1-G3/readers/a.txt", "The cat sat.", "text", "primary")])
        curriculum = _write_curriculum(tmp)
        root = Path(tempfile.mkdtemp())

        tape = Tape(root)
        stop_event = threading.Event()
        t = threading.Thread(target=lambda: read_sense.sense(
            tape.publish, stop_event, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
            canvas=128, period=0.1, words=8, letters=8, one_word_moments=True), daemon=True)
        t.start()
        deadline = time.time() + 10.0
        while len({r["meta"]["moment"] for r in _shelf_rows(root)}) < 4 and time.time() < deadline:
            time.sleep(0.1)
        time.sleep(0.3)
        stop_event.set()
        t.join(timeout=5.0)

        rows = _shelf_rows(root)
        moments = {r["meta"]["moment"] for r in rows}
        self.assertEqual(len(moments), 4, "3 word-moments + 1 sentence-moment")
        eyes = [r for r in rows if r["sense"] == "eye"]
        self.assertEqual(len(eyes), 4)
        word_eyes = [e for e in eyes if "word_ix" in e["meta"]]
        sentence_eyes = [e for e in eyes if "word_ix" not in e["meta"]]
        self.assertEqual(len(word_eyes), 3)
        self.assertEqual(len(sentence_eyes), 1)
        self.assertEqual(sorted(e["meta"]["text"] for e in word_eyes), ["cat", "sat", "the"])
        self.assertEqual(sentence_eyes[0]["meta"]["text"], "the cat sat")
        # every word-moment has EXACTLY one ear row (its own word) -- MEET binds it, and only it
        for e in word_eyes:
            ears_here = [r for r in rows if r["sense"] == "ear" and r["meta"]["moment"] == e["meta"]["moment"]]
            self.assertEqual(len(ears_here), 1)
            self.assertEqual(ears_here[0]["meta"]["word"], e["meta"]["text"])

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


class TestReadMeetsBody(unittest.TestCase):
    def test_a_read_moment_produces_a_meet_edge_between_sight_and_the_heard_word(self) -> None:
        """The mind needs NO change for a shelf row: `_consume_eye` reads `meta.source` only to journal it
        (never to branch on), so a "shelf" eye row runs the exact same MEET road a "folder" row does. This
        is the direct proof, over a real Body/Mind, that read.py's rows are usable as-is.
        G4-skeleton.genome's own `STAGE 2 meet moments 200..` (HEBB/DELTA only fire once org.t >= 200,
        genome/machinery.py:Organism.moment) would make a one-canvas toy see zero edges by construction --
        not a read.py defect, an artefact of STAGE 1 not being a plausible unit-test width. A LOCAL genome
        text (STAGE 2 at moment 0, everything else byte-identical to G4-skeleton.genome) isolates the
        thing under test."""
        tmp = Path(tempfile.mkdtemp())
        shelf = _write_shelf(tmp, [("a", "G1-G3/readers/a.txt", "Zog.", "text", "primary")])
        curriculum = _write_curriculum(tmp)
        root = Path(tempfile.mkdtemp())
        meets_at_zero = GENOME_PATH.read_text().replace("STAGE  1 senses   moments 0..200", "STAGE  1 senses   moments 0..0") \
                                                .replace("STAGE  2 meet     moments 200..", "STAGE  2 meet     moments 0..")
        self.assertNotEqual(meets_at_zero, GENOME_PATH.read_text(), "the STAGE lines must actually be present to replace")
        genome_path = tmp / "meet-at-zero.genome"
        genome_path.write_text(meets_at_zero)

        body = Body(root, genome_path)
        fn = functools.partial(read_sense.sense, shelf_db=str(shelf), curriculum_md=str(curriculum), root=root,
                               canvas=128, period=0.1, words=8, letters=8)
        body.add_sense("read", fn)
        body.start()
        try:
            deadline = time.time() + 10.0
            while len(_shelf_rows(root)) < 2 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
        finally:
            body.stop()

        org = body.mind.org
        self.assertGreater(len(org.edges_log), 0, "MEET must have logged at least one sight<->words edge")
        self.assertEqual(int(org.words.n), 1, "one word ('zog') ever heard -> one words cell born")

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


class TestDeclaredReadDirArming(unittest.TestCase):
    def test_gated_true(self) -> None:
        self.assertTrue(read_sense.READ_DOOR_GATED, "the commit landing the real door must flip this True")

    def test_declared_read_config_arms_from_the_genomes_own_line(self) -> None:
        from creature import body as body_module
        declared = {"SENSE_READ": {"shelf": "/data/alpha3-library/SHELF.sqlite",
                                    "curriculum": "/data/alpha3-library/CURRICULUM.md",
                                    "every_s": 5, "words": 8, "canvas": 128}}
        got = body_module._declared_read_config(declared)
        self.assertEqual(got, declared["SENSE_READ"])

    def test_undeclared_arms_nothing(self) -> None:
        from creature import body as body_module
        self.assertIsNone(body_module._declared_read_config({}))

    def test_gated_false_arms_nothing_even_with_a_declared_line(self) -> None:
        from creature import body as body_module
        import unittest.mock as mock
        with mock.patch.object(read_sense, "READ_DOOR_GATED", False):
            got = body_module._declared_read_config({"SENSE_READ": {"shelf": "x", "curriculum": "y"}})
        self.assertIsNone(got)


class TestReadShapeFromArgv(unittest.TestCase):
    """ALPHA4-H task 0's own decision, pinned: the two-moment shape (0.60, 24/40) is the PRODUCTION
    default over the genome line's own literal single-moment shape (0.15, 6/40) -- see
    docs/briefs/ALPHA4-H-REPORT.md."""

    def test_default_is_the_validated_two_moment_shape(self) -> None:
        from creature import body as body_module
        self.assertTrue(body_module._read_shape_from_argv(["--root", "R", "--genome", "G"]))

    def test_the_one_override_forces_the_literal_single_moment_shape(self) -> None:
        from creature import body as body_module
        self.assertFalse(body_module._read_shape_from_argv(["--root", "R", "--read-single-moment"]))


class TestPlantedReadOffender(unittest.TestCase):
    """The brief's own gate line ("+ your planted offender: a read sense that writes state"): a variant of
    THIS module's own shape (a `sense()` function taking `root`, writing a cursor file) that writes its
    cursor under `root/state/` instead of `root/read/`."""

    def _planted_offender_text(self, inline: bool) -> str:
        if inline:
            # the literal path spelt out INSIDE the write call itself.
            return (
                "from pathlib import Path\n"
                "def sense(publish, stop_event, shelf_db, curriculum_md, root, canvas=128, period=5.0):\n"
                "    (Path(root) / 'state' / 'CURSOR.json').write_text('{}')\n"
            )
        # read.py's OWN real style: the path built on an earlier line, held in a variable, then written.
        return (
            "from pathlib import Path\n"
            "def sense(publish, stop_event, shelf_db, curriculum_md, root, canvas=128, period=5.0):\n"
            "    cursor_path = Path(root) / 'state' / 'CURSOR.json'\n"
            "    cursor_path.parent.mkdir(parents=True, exist_ok=True)\n"
            "    cursor_path.write_text('{}')\n"
        )

    def test_caught_by_the_test_writer_sweeps_own_walker_inline_and_via_a_variable(self) -> None:
        """tests/creature/test_writer_sweep.py's walker resolves simple `x = <path expr>` assignments
        (its own `_build_env`/`_flatten`) -- it catches the offender EITHER way, inline or through
        read.py's own real variable-then-write style. This is the walker that actually sweeps
        creature/senses/*.py (read.py included) in tests.creature.test_writer_sweep.sense_module_paths()."""
        from tests.creature.test_writer_sweep import find_offenders
        tmp_dir = Path(tempfile.mkdtemp())
        for inline in (True, False):
            offender = tmp_dir / f"planted_read_offender_{inline}.py"
            offender.write_text(self._planted_offender_text(inline))
            self.assertTrue(find_offenders(offender, check_organism_import=False),
                            f"a read-shaped sense writing under root/state/ (inline={inline}) must be caught")
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_gate_g4s_own_sweep_catches_the_inline_form_but_not_the_variable_form(self) -> None:
        """A RAISED finding, not worked around: tools/gate_g4.py's own `sweep()` reads string constants
        only from the call's OWN argument expression (`_literal_text`) -- it never resolves an earlier
        `x = Path(root) / "state" / ...` assignment the way test_writer_sweep.py's `_flatten`/`_build_env`
        does. It catches the INLINE offender (the literal sits in the call itself) but MISSES the
        variable-built one -- which is read.py's, folder.py's, game.py's and hands.py's own real style for
        every cursor/seen-file write in this tree. Reported here rather than silently patched (not this
        builder's file, and the REAL read.py has no forbidden-dir write either way -- see the control
        below): the writer law is still enforced, by test_writer_sweep.py's walker, which IS exhaustive
        over creature/senses/*.py; gate_g4.py's OWN sweep has a real blind spot for this shape."""
        import importlib.util
        gate_path = Path(__file__).resolve().parents[2] / "tools" / "gate_g4.py"
        spec = importlib.util.spec_from_file_location("gate_g4_for_test", gate_path)
        gate_g4 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate_g4)
        tmp_dir = Path(tempfile.mkdtemp())
        inline = tmp_dir / "planted_inline.py"; inline.write_text(self._planted_offender_text(True))
        via_var = tmp_dir / "planted_via_var.py"; via_var.write_text(self._planted_offender_text(False))
        self.assertTrue(gate_g4.sweep([inline]), "the inline literal form must still be caught")
        self.assertEqual(gate_g4.sweep([via_var]), [], "documents the gap: the variable-built form is missed by gate_g4.py's own sweep")
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_the_real_read_module_is_never_flagged(self) -> None:
        """The negative control's own negative control (#91): read.py's REAL cursor write (root/read/, not
        root/state/) must NOT be flagged by either walker -- proving the sweep tells the two apart, not
        that it rejects every write."""
        from tests.creature.test_writer_sweep import find_offenders
        real = Path(__file__).resolve().parents[2] / "creature" / "senses" / "read.py"
        self.assertEqual(find_offenders(real, check_organism_import=False), [])
        self.assertEqual(find_offenders(real, check_organism_import=True), [])


if __name__ == "__main__":
    unittest.main()
