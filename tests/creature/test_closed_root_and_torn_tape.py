# edit: Claude (Opus 5.5), 2026-09-26 18:52 +0400 — the 09-24 update reboot (SOLUTIONS #240) started 35 closed lives on their closed
# roots, and 19 of them crash-looped on a zero-filled tape line with a BARE JSONDecodeError («Expecting value: line 1 column 1»),
# which named neither the file nor the line. These pin two of the incident's structural fixes: the body REFUSES to start on a
# root that carries STOPPED-AT (a closed life is never resumed by a restart; `main` exits 4, which the unit template never
# restarts), and `read_tape` NAMES a torn line — the day file, the line number and what the line holds — never skipping it.
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from creature.body import Body
from creature.tape import Tape, _resolve_tape_dir, read_tape

REPO = Path(__file__).resolve().parents[2]
GENOME_PATH = REPO / "genome" / "G4-skeleton.genome"


def _tape(n: int = 3):
    root = Path(tempfile.mkdtemp())
    t = Tape(root)
    for i in range(n):
        t.publish("ear", f"w{i}".encode(), {"moment": f"m{i}", "source": "test", "word": "x"}, "txt")
    days = sorted(_resolve_tape_dir(root, None).glob("*.jsonl"))
    assert len(days) == 1, days
    return root, days[0]


class TestTornTapeLine(unittest.TestCase):
    def test_a_zero_filled_line_is_named(self) -> None:
        root, day = _tape()
        with day.open("ab") as f:
            f.write(b"\x00" * 57 + b"\n")            # what the 22:00 shutdown left in the files the lives had open
        with self.assertRaises(ValueError) as cm:
            list(read_tape(root))
        msg = str(cm.exception)
        self.assertIn(day.name, msg)
        self.assertIn("line 4", msg)
        self.assertIn("NUL", msg)

    def test_a_cut_json_line_is_named(self) -> None:
        root, day = _tape()
        with day.open("a") as f:
            f.write('{"seq": 4, "at": "2026-09-24T21')  # a write cut mid-row
        with self.assertRaises(ValueError) as cm:
            list(read_tape(root))
        msg = str(cm.exception)
        self.assertIn(day.name, msg)
        self.assertIn("line 4", msg)
        self.assertIn("torn", msg)

    def test_a_whole_tape_reads_as_before(self) -> None:
        """Negative control: no torn line, every row read, in seq order."""
        root, _ = _tape(5)
        self.assertEqual([r["seq"] for r in read_tape(root)], [1, 2, 3, 4, 5])


class TestClosedRoot(unittest.TestCase):
    def test_the_body_refuses_to_start_on_a_closed_root(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "STOPPED-AT").write_text("2026-09-24 21:00 +0400\n")
        body = Body(root, GENOME_PATH)
        try:
            with self.assertRaises(RuntimeError) as cm:
                body.start()
            self.assertIn("STOPPED-AT", str(cm.exception))
            self.assertIsNone(getattr(body, "_mind_thread", None))
        finally:
            body.stop()
        # the closed record is never written: no STATUS, no journal row from a refused start or its stop
        self.assertFalse((root / "STATUS.json").exists())
        self.assertEqual(list((root / "journal").glob("*")) if (root / "journal").exists() else [], [])

    def test_main_exits_4_on_a_closed_root(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "STOPPED-AT").write_text("2026-09-24 21:00 +0400\n")
        p = subprocess.run([sys.executable, "-m", "creature.body", "--root", str(root), "--genome", str(GENOME_PATH), "--no-maker"],
                           cwd=REPO, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 4, p.stderr[-2000:])
        self.assertIn("STOPPED-AT", p.stderr)
        self.assertFalse((root / "tape").exists(), "a refused start must not write a tape")

    def test_an_open_root_still_starts(self) -> None:
        """Negative control: the same genome on a root without STOPPED-AT starts and stops cleanly."""
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        try:
            body.start()
            self.assertIsNotNone(body._mind_thread)
        finally:
            body.stop()


if __name__ == "__main__":
    unittest.main()
