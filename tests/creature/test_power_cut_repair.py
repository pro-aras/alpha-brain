# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:32 +0400 — his 23:20 word («make sure to clear any possible errors that might occur
# within these few days»), test-first (red on 3e6e1e9: no creature/repair.py). A power cut (2026-09-29 18:59, and 09-24) leaves the files
# a life had open with a TORN TAIL: zero-filled bytes or a half-written row, a SEQ file emptied mid-rewrite, a payload the row names but
# the disk never got. Today the body then refuses to start (read_tape names the torn line) and the unit gives up after 5 tries; worse,
# an emptied SEQ restarts the seq at 1. These pin the repair: at an OPEN life's start, a torn TAIL of every append-only JSON-lines file is
# cut and kept (never deleted) with a record; a torn line in the MIDDLE is left for read_tape to refuse; the seq never goes back; a
# closed life's record is never written.
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from creature import repair as RP
from creature.body import Body
from creature.tape import Tape, _resolve_tape_dir, read_tape

REPO = Path(__file__).resolve().parents[2]
GENOME_PATH = REPO / "genome" / "G4-skeleton.genome"


def _life(n: int = 6):
    root = Path(tempfile.mkdtemp())
    t = Tape(root)
    for i in range(n):
        t.publish("ear", f"w{i}".encode(), {"moment": f"m{i}", "source": "test", "word": f"w{i}"}, "txt")
    day = sorted(_resolve_tape_dir(root, None).glob("*.jsonl"))[0]
    return root, day


def _records(root: Path):
    p = root / RP.QDIR / RP.RECORD
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


class TailCut(unittest.TestCase):
    def test_a_clean_life_is_untouched(self):
        root, day = _life()
        before = day.read_bytes()
        self.assertEqual(RP.repair_life(root, None), [])
        self.assertEqual(day.read_bytes(), before)
        self.assertFalse((root / RP.QDIR).exists())

    def test_a_zero_filled_tail_is_cut_and_kept(self):
        root, day = _life()
        good = day.read_bytes()
        day.write_bytes(good + b"\x00" * 500)
        recs = RP.repair_life(root, None)
        self.assertEqual(day.read_bytes(), good)
        self.assertEqual([r["seq"] for r in read_tape(root)], [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(recs), 1)
        r = recs[0]
        self.assertEqual((r["kind"], r["bytes"], r["nul_bytes"]), ("tail_cut", 500, 500))
        kept = (root / RP.QDIR / r["quarantine"]).read_bytes()
        self.assertEqual(kept, b"\x00" * 500)
        self.assertEqual(r["sha256"], hashlib.sha256(kept).hexdigest())
        self.assertEqual(_records(root), recs)

    def test_a_half_written_row_and_torn_lines_before_it_are_cut(self):
        root, day = _life()
        good = day.read_bytes()
        day.write_bytes(good + b"\x00\x00\x00\n" + b'{"seq": 7, "at": "2026-09-29T14')
        RP.repair_life(root, None)
        self.assertEqual(day.read_bytes(), good)

    def test_a_whole_row_missing_only_its_newline_is_completed_not_cut(self):
        root, day = _life()
        good = day.read_bytes()
        row = json.dumps({"seq": 7, "at": "2026-09-29T14:00:00.000Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {}})
        day.write_bytes(good + row.encode())
        recs = RP.repair_life(root, None, check_payload_rows=0)
        self.assertEqual(day.read_bytes(), good + row.encode() + b"\n")
        self.assertEqual(recs[0]["kind"], "newline_added")

    def test_a_hole_with_good_rows_after_it_near_the_end_is_cut_with_them_and_kept(self):
        root, day = _life(3)
        good = day.read_bytes()
        later = json.dumps({"seq": 9, "at": "2026-09-29T14:00:00.000Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {}}) + "\n"
        day.write_bytes(good + b"\x00" * 20 + b"\n" + later.encode())      # pages flushed out of order: a hole, then a good row
        recs = RP.repair_life(root, None, check_payload_rows=0)
        self.assertEqual(day.read_bytes(), good)
        self.assertEqual((recs[0]["kind"], recs[0]["good_rows_cut"]), ("tail_cut", 1))
        self.assertEqual((root / RP.QDIR / recs[0]["quarantine"]).read_bytes(), b"\x00" * 20 + b"\n" + later.encode())

    def test_a_torn_line_older_than_the_tail_is_left_for_read_tape_to_refuse(self):
        root, day = _life(3)
        good = day.read_bytes()
        rows = "".join(json.dumps({"seq": 10 + i, "at": "2026-09-29T14:00:00.000Z", "sense": "ear", "sha": "x" * 200, "payload": "p",
                                   "meta": {"i": i}}) + "\n" for i in range(6000))
        day.write_bytes(good + b"\x00" * 20 + b"\n" + rows.encode())          # more than 1 MiB of good rows after it
        before = day.read_bytes()
        self.assertGreater(len(rows), RP.MAX_TAIL)
        RP.repair_life(root, None, check_payload_rows=0)
        self.assertEqual(day.read_bytes(), before)
        with self.assertRaises(ValueError):
            list(read_tape(root))

    def test_every_append_only_file_of_the_life_is_repaired(self):
        root, _ = _life()
        (root / "journal").mkdir()
        (root / "state").mkdir()
        j = root / "journal" / "2026-09-29.jsonl"
        b = root / "state" / "beliefs.jsonl"
        j.write_bytes(b'{"event": "start"}\n' + b"\x00" * 30)
        b.write_bytes(b'{"word": "ring"}\n{"word": "st')
        recs = RP.repair_life(root, None)
        self.assertEqual(j.read_bytes(), b'{"event": "start"}\n')
        self.assertEqual(b.read_bytes(), b'{"word": "ring"}\n')
        self.assertEqual(sorted(r["file"] for r in recs), ["journal/2026-09-29.jsonl", "state/beliefs.jsonl"])


class Payloads(unittest.TestCase):
    def test_a_row_whose_payload_the_disk_never_got_cuts_the_tape_there(self):
        root, day = _life(10)
        tape = _resolve_tape_dir(root, None)
        rows = list(read_tape(root))
        (tape / rows[7]["payload"]).write_bytes(b"\x00" * 2)          # row 8's payload torn
        recs = RP.repair_life(root, None)
        self.assertEqual([r["seq"] for r in read_tape(root)], [1, 2, 3, 4, 5, 6, 7])
        cut = [r for r in recs if r["kind"] == "payload_cut"]
        self.assertEqual((cut[0]["first_bad_seq"], cut[0]["rows"]), (8, 3))
        for r in rows[7:]:
            self.assertFalse((tape / r["payload"]).exists())
            self.assertTrue((root / RP.QDIR / "payload" / Path(r["payload"]).name).exists())


class Seq(unittest.TestCase):
    def test_an_emptied_or_zero_filled_SEQ_heals_from_the_rows(self):
        for junk in (b"", b"\x00\x00\x00", b"4"):
            root, _ = _life(6)
            (_resolve_tape_dir(root, None) / "SEQ").write_bytes(junk)
            t = Tape(root)
            row = t.publish("ear", b"x", {"moment": "m", "source": "test", "word": "x"}, "txt")
            self.assertEqual(row["seq"], 7, junk)

    def test_the_seq_never_goes_below_what_the_mind_has_seen(self):
        root, _ = _life(3)
        t = Tape(root)
        t.ensure_seq_at_least(40)
        self.assertEqual(t.publish("ear", b"x", {"moment": "m", "source": "test", "word": "x"}, "txt")["seq"], 41)
        t.ensure_seq_at_least(10)
        self.assertEqual(t.publish("ear", b"y", {"moment": "m2", "source": "test", "word": "y"}, "txt")["seq"], 42)


class BodyAfterAPowerCut(unittest.TestCase):
    def test_the_body_starts_after_a_power_cut_and_journals_the_repair(self):
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        try:
            body.start()
            for i in range(5):
                body._publish("ear", f"w{i}".encode(), {"moment": f"m{i}", "source": "test", "word": f"w{i}"}, "txt")
        finally:
            body.stop()
        tape = _resolve_tape_dir(root, None)
        day = sorted(tape.glob("*.jsonl"))[0]
        top = max(r["seq"] for r in read_tape(root))
        with day.open("ab") as f:                                    # the cut: a zero-filled tail and an emptied SEQ
            f.write(b"\x00" * 300)
        (tape / "SEQ").write_bytes(b"")
        jday = sorted((root / "journal").glob("*.jsonl"))[0]
        with jday.open("ab") as f:
            f.write(b'{"kind": "brai')
        body2 = Body(root, GENOME_PATH)
        try:
            body2.start()
            row = body2._publish("ear", b"z", {"moment": "mz", "source": "test", "word": "z"}, "txt")
            self.assertGreater(row["seq"], top)
        finally:
            body2.stop()
        rows = list(read_tape(root))
        self.assertEqual(len(rows), len({r["seq"] for r in rows}), "no seq is used twice")
        events = [json.loads(l) for f in sorted((root / "journal").glob("*.jsonl")) for l in f.read_text().splitlines() if l.strip()]
        self.assertTrue(any(e.get("event") == "repair" for e in events))
        self.assertEqual({r["file"] for r in _records(root)}, {str(day.relative_to(root)), str(jday.relative_to(root))})

    def test_a_closed_life_is_never_repaired(self):
        root, day = _life()
        good = day.read_bytes()
        day.write_bytes(good + b"\x00" * 50)
        (root / "STOPPED-AT").write_text("2026-09-29 23:00 +0400\n")
        body = Body(root, GENOME_PATH)
        try:
            with self.assertRaises(RuntimeError):
                body.start()
        finally:
            body.stop()
        self.assertEqual(day.read_bytes(), good + b"\x00" * 50)
        self.assertFalse((root / RP.QDIR).exists())


if __name__ == "__main__":
    unittest.main()
