# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:1x +0400 — ALPHA4-H task 0/4 (docs/briefs/ALPHA4-H.md):
# tools/read_recognised.py, test-first over a real (tiny) Body/Mind life.
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
from creature.tape import read_tape
from tools import read_recognised

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


def _meet_at_zero_genome(tmp: Path) -> Path:
    text = GENOME_PATH.read_text().replace(
        "STAGE  1 senses   moments 0..200", "STAGE  1 senses   moments 0..0").replace(
        "STAGE  2 meet     moments 200..", "STAGE  2 meet     moments 0..")
    p = tmp / "meet0.genome"
    p.write_text(text)
    return p


def _write_shelf(base_dir: Path, text: str) -> Path:
    db_path = base_dir / "SHELF.sqlite"
    con = sqlite3.connect(str(db_path))
    con.execute("CREATE TABLE docs (doc_id TEXT PRIMARY KEY, path TEXT NOT NULL, format TEXT NOT NULL, "
                "title TEXT, source_class TEXT, licence TEXT, bytes INTEGER, sha256 TEXT, catalogued_at TEXT)")
    p = base_dir / "G1-G3/readers/a.txt"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    con.execute("INSERT INTO docs (doc_id, path, format) VALUES (?,?,?)", ("a", "G1-G3/readers/a.txt", "text"))
    con.commit(); con.close()
    (base_dir / "CURRICULUM.md").write_text("# c\n")
    return db_path


class TestReadRecognisedLive(unittest.TestCase):
    def test_a_word_read_many_times_is_recognised_in_the_heldout_font(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        # "zog" repeated as its own one-word "sentence" many times so MEET gets real practice.
        text = " ".join("Zog." for _ in range(60))
        shelf = _write_shelf(tmp, text)
        root = Path(tempfile.mkdtemp())
        genome_path = _meet_at_zero_genome(tmp)

        body = Body(root, genome_path)
        fn = functools.partial(read_sense.sense, shelf_db=str(shelf), curriculum_md=str(tmp / "CURRICULUM.md"),
                               root=root, canvas=128, period=0.02, words=8, letters=8)
        body.add_sense("read", fn)
        body.start()
        try:
            deadline = time.time() + 30.0
            while len([r for r in read_tape(root) if r.get("meta", {}).get("source") == "shelf"]) < 120 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
            body.mind.snapshot()
        finally:
            body.stop()

        result = read_recognised.recognised_share(root, genome_path, ["zog"], font_path=read_common.HELDOUT_FONT_PATH)
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["predictions"][0]["word"], "zog")
        self.assertEqual(result["predictions"][0]["answered"], "zog",
                          "a word met 60 times in the DEFAULT font must be recognised rendered in the HELD-OUT font")
        self.assertEqual(result["font"], read_common.HELDOUT_FONT_PATH)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_recognised_share_never_mutates_the_organism(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        text = " ".join("Zog." for _ in range(30))
        shelf = _write_shelf(tmp, text)
        root = Path(tempfile.mkdtemp())
        genome_path = _meet_at_zero_genome(tmp)

        body = Body(root, genome_path)
        fn = functools.partial(read_sense.sense, shelf_db=str(shelf), curriculum_md=str(tmp / "CURRICULUM.md"),
                               root=root, canvas=128, period=0.02, words=8, letters=8)
        body.add_sense("read", fn)
        body.start()
        try:
            deadline = time.time() + 30.0
            while len([r for r in read_tape(root) if r.get("meta", {}).get("source") == "shelf"]) < 60 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.3)
            body.mind.snapshot()
        finally:
            body.stop()

        from tools.self_exam import load_snapshot
        _g, org_before, _L, _raw = load_snapshot(root, genome_path)
        h_before = org_before.state_hash()
        read_recognised.recognised_share(root, genome_path, ["zog", "nope"], font_path=read_common.HELDOUT_FONT_PATH)
        _g2, org_after, _L2, _raw2 = load_snapshot(root, genome_path)
        self.assertEqual(org_after.state_hash(), h_before)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


class TestBlindTwinRoot(unittest.TestCase):
    def test_blind_twin_reads_0_by_construction(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        text = " ".join("Zog." for _ in range(60))
        shelf = _write_shelf(tmp, text)
        root = Path(tempfile.mkdtemp())
        genome_path = _meet_at_zero_genome(tmp)

        body = Body(root, genome_path)
        fn = functools.partial(read_sense.sense, shelf_db=str(shelf), curriculum_md=str(tmp / "CURRICULUM.md"),
                               root=root, canvas=128, period=0.02, words=8, letters=8)
        body.add_sense("read", fn)
        body.start()
        try:
            deadline = time.time() + 30.0
            while len([r for r in read_tape(root) if r.get("meta", {}).get("source") == "shelf"]) < 120 and time.time() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
        finally:
            body.stop()

        live = read_recognised.recognised_share(root, genome_path, ["zog"], font_path=read_common.HELDOUT_FONT_PATH)
        self.assertEqual(live["predictions"][0]["answered"], "zog")

        twin_root = Path(tempfile.mkdtemp())
        read_recognised.blind_twin_root(root, genome_path, twin_root, drop_source="shelf")
        twin = read_recognised.recognised_share(twin_root, genome_path, ["zog"], font_path=read_common.HELDOUT_FONT_PATH)
        self.assertEqual(twin["predictions"][0]["answered"], None, "the blind twin never heard 'zog' -- 0 by construction")
        self.assertEqual(twin["share"], 0.0)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True); shutil.rmtree(twin_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
