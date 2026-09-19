# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:58 +0400 — A5 test: a frozen STATUS (same numbers, 61 min
# apart by the readings' OWN stamps) pages; a moving one does not. Driven by check()/run_once() directly against
# synthetic STATUS.json files, so this never sleeps a real hour.
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools import creature_watch


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _status(at: datetime, moments: int, tape_rows: int) -> dict:
    return {
        "heartbeat_at": _iso(at), "started_at": _iso(at), "moments": moments, "tape_rows": tape_rows,
        "journal_rows": moments, "births": 5, "edges_born": 3, "edges_pruned": 0, "cells": 8,
        "sight_only_skipped": 0, "sense_restarts": 0, "snapshots": 0, "last_seq": tape_rows,
        "mind_ms_median_1min": 4.2, "rss_mb": 120.0, "crash": None,
    }


def _write_status(root: Path, status: dict) -> None:
    (root / "STATUS.json").write_text(json.dumps(status))


class TestWatchCheck(unittest.TestCase):
    def test_frozen_status_61_min_apart_pages(self) -> None:
        t0 = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
        s1 = _status(t0, 100, 100)
        s2 = _status(t0 + timedelta(minutes=61), 100, 100)   # unchanged counters, 61 min later
        paged1, last1, why1 = creature_watch.check(s1, None)
        self.assertFalse(paged1)
        paged2, last2, why2 = creature_watch.check(s2, last1)
        self.assertTrue(paged2)
        self.assertIsNotNone(why2)
        self.assertIn("frozen", why2)

    def test_moving_status_does_not_page(self) -> None:
        t0 = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
        s1 = _status(t0, 100, 100)
        s2 = _status(t0 + timedelta(minutes=61), 150, 140)   # moments AND tape_rows moved
        paged1, last1, _why1 = creature_watch.check(s1, None)
        self.assertFalse(paged1)
        paged2, last2, why2 = creature_watch.check(s2, last1)
        self.assertFalse(paged2)
        self.assertIsNone(why2)
        self.assertEqual(last2["moments"], 150)

    def test_under_the_threshold_does_not_page(self) -> None:
        t0 = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
        s1 = _status(t0, 100, 100)
        s2 = _status(t0 + timedelta(minutes=30), 100, 100)   # unchanged, but only 30 min
        _p1, last1, _w1 = creature_watch.check(s1, None)
        paged2, _last2, why2 = creature_watch.check(s2, last1)
        self.assertFalse(paged2)
        self.assertIsNone(why2)


class TestWatchRunOnce(unittest.TestCase):
    def test_run_once_frozen_writes_page_and_pages_jsonl(self) -> None:
        root = Path(tempfile.mkdtemp())
        t0 = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
        _write_status(root, _status(t0, 100, 100))
        self.assertFalse(creature_watch.run_once(root))
        self.assertIsNone(json.loads((root / "PAGE.json").read_text()))

        _write_status(root, _status(t0 + timedelta(minutes=61), 100, 100))
        self.assertTrue(creature_watch.run_once(root))
        page = json.loads((root / "PAGE.json").read_text())
        self.assertIsNotNone(page)
        self.assertIn("why", page)

        pages = [json.loads(line) for line in (root / "pages.jsonl").read_text().splitlines() if line.strip()]
        self.assertEqual(len(pages), 1)
        self.assertIn("status", pages[0])

    def test_run_once_moving_never_pages(self) -> None:
        root = Path(tempfile.mkdtemp())
        t0 = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
        for k in range(4):
            _write_status(root, _status(t0 + timedelta(minutes=20 * k), 100 + 10 * k, 100 + 10 * k))
            self.assertFalse(creature_watch.run_once(root))
        self.assertIsNone(json.loads((root / "PAGE.json").read_text()))
        self.assertFalse((root / "pages.jsonl").exists())

    def test_run_once_missing_status_is_noop(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.assertFalse(creature_watch.run_once(root))
        self.assertFalse((root / "PAGE.json").exists())


if __name__ == "__main__":
    unittest.main()
