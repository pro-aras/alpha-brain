# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 21:38 +0400 — A1 test: 3 threads x 100 publishes -> 300 unique
# consecutive seqs; sha matches the payload file; read_tape order; a second Tape on the same root continues the seq.
from __future__ import annotations

import hashlib
import tempfile
import threading
import unittest
from pathlib import Path

from creature.tape import Tape, read_tape


class TestTape(unittest.TestCase):
    def test_concurrent_publish_and_resume(self) -> None:
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        n_threads, n_each = 3, 100
        errors = []

        def worker(tid: int) -> None:
            try:
                for i in range(n_each):
                    payload = f"thread{tid}-item{i}".encode()
                    tape.publish("ear", payload, {"moment": f"t{tid}i{i}", "source": "test", "word": "x"}, "txt")
            except Exception as e:  # pragma: no cover - surfaced via errors list
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(tid,)) for tid in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])

        rows = list(read_tape(root))
        self.assertEqual(len(rows), n_threads * n_each)

        seqs = [r["seq"] for r in rows]
        self.assertEqual(seqs, sorted(seqs), "read_tape must yield rows in seq order")
        self.assertEqual(len(set(seqs)), n_threads * n_each, "seqs must be unique")
        self.assertEqual(seqs, list(range(1, n_threads * n_each + 1)), "seqs must be strictly consecutive from 1")

        for row in rows:
            payload_path = root / "tape" / row["payload"]
            self.assertTrue(payload_path.exists())
            actual_sha = hashlib.sha256(payload_path.read_bytes()).hexdigest()
            self.assertEqual(row["sha"], actual_sha)

        # a second Tape on the same root continues the seq
        tape2 = Tape(root)
        row = tape2.publish("eye", b"more-bytes", {"moment": "resume1", "source": "test"}, "png")
        self.assertEqual(row["seq"], n_threads * n_each + 1)

        rows_after = list(read_tape(root))
        self.assertEqual(len(rows_after), n_threads * n_each + 1)
        self.assertEqual(rows_after[-1]["seq"], n_threads * n_each + 1)

    def test_single_publish_fields(self) -> None:
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        row = tape.publish("ear", b"hello", {"moment": "m0", "source": "maker", "word": "hello"}, "txt")
        self.assertEqual(row["seq"], 1)
        self.assertEqual(row["sense"], "ear")
        self.assertEqual(row["sha"], hashlib.sha256(b"hello").hexdigest())
        self.assertEqual(row["payload"], "payload/000000001.txt")
        self.assertTrue((root / "tape" / row["payload"]).exists())
        self.assertEqual((root / "tape" / row["payload"]).read_bytes(), b"hello")
        date = row["at"][:10]
        day_file = root / "tape" / f"{date}.jsonl"
        self.assertTrue(day_file.exists())
        self.assertIn(f'"seq": 1', day_file.read_text())


if __name__ == "__main__":
    unittest.main()
