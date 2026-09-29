# edit: Claude (Opus 5.5, the seat), 2026-09-30 00:14 +0400 — his 23:20 word («make sure to clear any possible errors that might occur within
# these few days»), test-first (red on 84d5ad5): the life's heartbeat is written by the body's own status thread, so a mind thread that hangs
# keeps a fresh heartbeat and the watch's «frozen» rule (a heartbeat older than 90 min) can never fire. A mind whose moments and last_seq
# have not moved across an hour of watches, while its unit is active, is STUCK: it is restarted, at most once in 6 h (shared with «frozen»)
# and within the 4 recoveries a day. A mind that moved, and a closed life, are never touched.
"""tests/tools/test_health_watch.py — tools/lives/health.py's stuck-mind rule."""
from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from tools.lives import health as H


def at(minutes_ago: float) -> str:
    """The watch's own `at` format (HEALTH.jsonl)."""
    return (datetime.now().astimezone() - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S %z")


def row(minutes_ago: float, moments, last_seq):
    return {"at": at(minutes_ago), "moments": moments, "last_seq": last_seq}


class StuckMind(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="health-watch-"))
        self.calls = []

        def fake_sh(*a):
            self.calls.append(list(a))
            return H.subprocess.CompletedProcess(list(a), 0, "", "")

        self.patch = mock.patch.object(H, "sh", fake_sh)
        self.patch.start()

    def tearDown(self) -> None:
        self.patch.stop()
        shutil.rmtree(self.root, ignore_errors=True)

    def test_stuck_since_is_the_age_of_the_oldest_unbroken_watch_with_the_same_position(self):
        rows = [row(80, 5, 9), row(60, 7, 11), row(40, 7, 11), row(20, 7, 11)]
        s = H.stuck_since(rows, 7, 11, time.time())
        self.assertAlmostEqual(s / 60, 60, delta=1)
        self.assertIsNone(H.stuck_since(rows, 8, 12, time.time()), "it moved since the last watch")
        self.assertIsNone(H.stuck_since([], 7, 11, time.time()), "no history, no claim")
        self.assertIsNone(H.stuck_since([row(90, None, None)], None, None, time.time()), "an unread STATUS is not «no motion»")
        # a watch whose `at` cannot be read ends the run (never counted as old)
        self.assertAlmostEqual(H.stuck_since([row(80, 7, 11), {"at": "?", "moments": 7, "last_seq": 11}, row(20, 7, 11)], 7, 11,
                                             time.time()) / 60, 20, delta=1)

    def test_an_active_mind_with_no_motion_for_an_hour_is_restarted_once_in_six_hours(self):
        acts = H.recover(self.root, "u.service", [], {"ActiveState": "active"}, 10.0, stuck_s=65 * 60)
        self.assertEqual([a["why"] for a in acts], ["no motion"])
        self.assertEqual(self.calls, [["systemctl", "--user", "restart", "u.service"]])
        self.assertIn("no motion", (self.root / "RECOVERY.log").read_text())
        problems = []
        self.assertEqual(H.recover(self.root, "u.service", problems, {"ActiveState": "active"}, 10.0, stuck_s=85 * 60), [],
                         "once in 6 h")
        self.assertEqual(len(self.calls), 1)

    def test_the_six_hours_are_shared_with_frozen(self):
        self.assertEqual([a["why"] for a in H.recover(self.root, "u.service", [], {"ActiveState": "active"}, 100 * 60.0)], ["frozen"])
        self.assertEqual(H.recover(self.root, "u.service", [], {"ActiveState": "active"}, 10.0, stuck_s=65 * 60), [])

    def test_a_mind_that_moved_a_short_stall_or_a_closed_life_is_left_alone(self):
        self.assertEqual(H.recover(self.root, "u", [], {"ActiveState": "active"}, 10.0, stuck_s=None), [])
        self.assertEqual(H.recover(self.root, "u", [], {"ActiveState": "active"}, 10.0, stuck_s=30 * 60), [])
        (self.root / "STOPPED-AT").write_text("2026-09-30 00:14 +0400\n")
        self.assertEqual(H.recover(self.root, "u", [], {"ActiveState": "active"}, 10.0, stuck_s=5 * 3600), [])
        self.assertEqual(self.calls, [])

    def test_main_reads_the_watch_history_names_the_problem_and_acts(self):
        now = datetime.now().astimezone()
        (self.root / "STATUS.json").write_text(json.dumps({
            "heartbeat_at": now.isoformat(), "moments": 7, "last_seq": 11, "tape_rows": 11, "mind_backlog_rows": 40}))
        with (self.root / "HEALTH.jsonl").open("w") as f:
            for r in (row(95, 3, 5), row(65, 7, 11), row(45, 7, 11), row(25, 7, 11), row(5, 7, 11)):
                f.write(json.dumps(r) + "\n")
        with mock.patch.object(H, "unit_show", lambda u: {"ActiveState": "active", "NRestarts": "0", "UnitFileState": "enabled"}):
            H.main(["--root", str(self.root), "--unit", "u.service", "--recover", "--sleep-ab", str(self.root / "none")])
        self.assertIn(["systemctl", "--user", "restart", "u.service"], self.calls)
        page = (self.root / "HEALTH.md").read_text()
        self.assertIn("no motion for 65 minutes", page)
        self.assertIn("ACTED: no motion", page)

    def test_main_leaves_a_moving_mind_alone(self):
        now = datetime.now().astimezone()
        (self.root / "STATUS.json").write_text(json.dumps({"heartbeat_at": now.isoformat(), "moments": 9, "last_seq": 13}))
        with (self.root / "HEALTH.jsonl").open("w") as f:
            for r in (row(65, 7, 11), row(45, 7, 11), row(25, 7, 11), row(5, 8, 12)):
                f.write(json.dumps(r) + "\n")
        with mock.patch.object(H, "unit_show", lambda u: {"ActiveState": "active", "NRestarts": "0", "UnitFileState": "enabled"}):
            H.main(["--root", str(self.root), "--unit", "u.service", "--recover", "--sleep-ab", str(self.root / "none")])
        self.assertEqual(self.calls, [])
        self.assertNotIn("no motion for", (self.root / "HEALTH.md").read_text())


    def test_a_restart_count_is_a_problem_only_when_it_grows(self):
        now = datetime.now().astimezone()
        (self.root / "STATUS.json").write_text(json.dumps({"heartbeat_at": now.isoformat(), "moments": 9, "last_seq": 13}))
        for prev_n, now_n, said in (("5", "0", False), ("0", "2", True)):
            (self.root / "HEALTH.jsonl").write_text(json.dumps({**row(20, 8, 12), "unit": {"NRestarts": prev_n}}) + "\n")
            with mock.patch.object(H, "unit_show", lambda u, n=now_n: {"ActiveState": "active", "NRestarts": n, "UnitFileState": "enabled"}):
                H.main(["--root", str(self.root), "--unit", "u.service", "--sleep-ab", str(self.root / "none")])
            self.assertEqual("restarted since the last watch" in (self.root / "HEALTH.md").read_text(), said, (prev_n, now_n))


if __name__ == "__main__":
    unittest.main()
