# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §4 (d)/(e): SENSE
# grade — the seat's grades and the HOLD file, both published onto the tape (creature/senses/grade.py).
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import List, Tuple

from creature.senses import grade as grade_module


def _run(root: Path, seconds: float, graded_dir=None, hold_file=None, period: float = 0.01):
    published: List[Tuple[str, dict]] = []
    lock = threading.Lock()

    def fake_publish(sense, payload, meta, ext):
        with lock:
            published.append((sense, meta))
        return {"seq": len(published)}

    stop = threading.Event()

    def go():
        grade_module.sense(fake_publish, stop, root, graded_dir=graded_dir, hold_file=hold_file, period=period)

    th = threading.Thread(target=go, daemon=True)
    th.start()
    time.sleep(seconds)
    stop.set()
    th.join(timeout=2.0)
    return published


class TestGradeSense(unittest.TestCase):
    def test_each_graded_file_becomes_one_grade_row(self) -> None:
        root = Path(tempfile.mkdtemp())
        graded_dir = root / "ask" / "graded"
        graded_dir.mkdir(parents=True)
        (graded_dir / "g1.json").write_text(json.dumps({"id": "g1", "right": True, "novel": False}))
        (graded_dir / "g2.json").write_text(json.dumps({"id": "g2", "right": False, "novel": True}))

        published = _run(root, 0.2, graded_dir=graded_dir)
        grades = [m for s, m in published if s == "grade"]
        self.assertEqual(len(grades), 2)
        by_id = {m["id"]: m for m in grades}
        self.assertEqual(by_id["g1"], {"moment": "gradeg1", "source": "grade", "id": "g1", "right": True, "novel": False})
        self.assertEqual(by_id["g2"]["right"], False)
        self.assertEqual(by_id["g2"]["novel"], True)

    def test_a_grade_is_never_republished_after_it_is_seen(self) -> None:
        root = Path(tempfile.mkdtemp())
        graded_dir = root / "ask" / "graded"
        graded_dir.mkdir(parents=True)
        (graded_dir / "g1.json").write_text(json.dumps({"id": "g1", "right": True, "novel": False}))
        _run(root, 0.15, graded_dir=graded_dir)
        # a second run over the SAME root/graded_dir (a restart) must not re-publish g1
        published2 = _run(root, 0.15, graded_dir=graded_dir)
        grades2 = [m for s, m in published2 if s == "grade"]
        self.assertEqual(grades2, [])

    def test_no_hold_file_configured_publishes_no_hold_rows(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "ask" / "graded").mkdir(parents=True)
        published = _run(root, 0.15, hold_file=None)
        self.assertEqual([m for s, m in published if s == "hold"], [])

    def test_hold_absent_at_birth_publishes_one_false_row_on_first_scan(self) -> None:
        """Advisor's fix: the FIRST scan must always count as a change from an unknown prior state, or a
        reader could not tell "never checked" from "checked, not held"."""
        root = Path(tempfile.mkdtemp())
        (root / "ask" / "graded").mkdir(parents=True)
        hold_file = root / "world" / "HOLD"
        published = _run(root, 0.15, hold_file=hold_file)
        holds = [m for s, m in published if s == "hold"]
        self.assertEqual(len(holds), 1)
        self.assertEqual(holds[0]["active"], False)

    def test_hold_present_at_birth_publishes_one_true_row_on_first_scan(self) -> None:
        """The risk named in the advisor's fix, made concrete: a HOLD file that predates this sense's
        first scan must not read as "not held" for want of a prior observation to differ from."""
        root = Path(tempfile.mkdtemp())
        (root / "ask" / "graded").mkdir(parents=True)
        hold_dir = root / "world"
        hold_dir.mkdir(parents=True)
        hold_file = hold_dir / "HOLD"
        hold_file.write_text("held before birth")
        published = _run(root, 0.15, hold_file=hold_file)
        holds = [m for s, m in published if s == "hold"]
        self.assertEqual(len(holds), 1)
        self.assertEqual(holds[0]["active"], True)

    def test_hold_toggles_publish_one_row_per_change_only(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "ask" / "graded").mkdir(parents=True)
        hold_dir = root / "world"
        hold_dir.mkdir(parents=True)
        hold_file = hold_dir / "HOLD"

        published: List[Tuple[str, dict]] = []
        lock = threading.Lock()

        def fake_publish(sense, payload, meta, ext):
            with lock:
                published.append((sense, meta))
            return {}

        stop = threading.Event()
        th = threading.Thread(target=lambda: grade_module.sense(fake_publish, stop, root, hold_file=hold_file, period=0.02), daemon=True)
        th.start()
        time.sleep(0.1)       # first scan: not held -> one False row
        hold_file.write_text("now held")
        time.sleep(0.1)       # second observation: held -> one True row
        hold_file.unlink()
        time.sleep(0.1)       # third observation: not held again -> one False row
        stop.set()
        th.join(timeout=2.0)

        holds = [m["active"] for s, m in published if s == "hold"]
        self.assertEqual(holds, [False, True, False])

    def test_torn_grade_file_is_skipped_not_fatal(self) -> None:
        root = Path(tempfile.mkdtemp())
        graded_dir = root / "ask" / "graded"
        graded_dir.mkdir(parents=True)
        (graded_dir / "bad.json").write_text("{not json")
        published = _run(root, 0.1, graded_dir=graded_dir)
        self.assertEqual([m for s, m in published if s == "grade"], [])

    def test_default_graded_dir_is_root_ask_graded(self) -> None:
        root = Path(tempfile.mkdtemp())
        graded_dir = root / "ask" / "graded"
        graded_dir.mkdir(parents=True)
        (graded_dir / "g1.json").write_text(json.dumps({"id": "g1", "right": True, "novel": False}))
        published = _run(root, 0.15)   # graded_dir=None -> the module's own default
        self.assertEqual(len([m for s, m in published if s == "grade"]), 1)


if __name__ == "__main__":
    unittest.main()
