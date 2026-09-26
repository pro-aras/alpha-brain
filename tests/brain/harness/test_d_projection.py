# edit: Claude (Opus 5.5), 2026-09-26 18:23 +0400 — R41: the projection check's first version read cost.jsonl, which the
# run writes through a 131,072-byte buffer (Python 3.14) and which therefore stays EMPTY until a run ends. These pin the new
# reading source on planted run dirs: a sleep counts only once its snapshot AND its library-log record exist; the rule
# (k ≥ 4, r × the predicted total > 24 CPU-h) fires on a planted slow sleep and stays quiet on a planted on-price one; the
# in-progress LOWER bound fires before the sleep closes; a vanished process is reported; and --record's clock comparison
# catches a planted one-second shift.
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from tools.b1 import d_projection as P

T0 = 1_000_000.0                       # the planted process start (epoch s)
BUDGET = {"predicted_cum_cpu_s": {str(k): (100.0 if k == 3 else 3600.0 * (k - 3)) for k in range(3, 18)},
          "predicted_total_cpu_h": 20.0}   # 20 h total: a FIRE needs r > 1.2


def plant_sleep(run: Path, k: int, mtime: float, logged: bool = True) -> None:
    lib = run / "arm" / "library"
    lib.mkdir(parents=True, exist_ok=True)
    p = lib / f"sleep-{k}.json"
    p.write_text("{}")
    os.utime(p, (mtime, mtime))
    if logged:
        with (run / "arm" / "library_log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"sleep": k}) + "\n")


def clock(cpu: float, alive: bool = True):
    return lambda pid: (T0, cpu, "R") if alive else None


class TestDProjection(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_dir(self, name: str) -> Path:
        d = self.root / "20261001" / name
        d.mkdir(parents=True)
        return d

    def test_a_snapshot_without_its_log_record_is_not_closed(self) -> None:
        d = self.run_dir("D")
        plant_sleep(d, 1, T0 + 1)
        plant_sleep(d, 2, T0 + 2)
        plant_sleep(d, 3, T0 + 3, logged=False)        # caught mid-write
        self.assertEqual([k for k, _ in P.closed_sleeps(d)], [1, 2])

    def test_a_slow_sleep_fires_and_an_on_price_one_does_not(self) -> None:
        slow, ok = self.run_dir("D"), self.run_dir("SHUFFLED-RELATION_D")
        for d in (slow, ok):
            for k in (1, 2):
                plant_sleep(d, k, T0 + 1)
            plant_sleep(d, 3, T0 + 100)
        plant_sleep(slow, 4, T0 + 3600 * 1.3)          # r = 1.3 → 26 CPU-h projected
        plant_sleep(ok, 4, T0 + 3600 * 1.0)            # r = 1.0 → 20 CPU-h projected
        now = T0 + 5000
        s_ok = P.Search(ok, pid=2)
        lines, fire, _, dead = P.poll(BUDGET, [s_ok], 7, now, procs=clock(5000.0))
        self.assertIsNone(fire, lines)
        self.assertEqual(dead, [])
        self.assertTrue(any("sleep 4" in l and "r 1.000" in l for l in lines), lines)
        s_slow = P.Search(slow, pid=1)
        lines, fire, _, _ = P.poll(BUDGET, [s_slow], 7, now, procs=clock(5000.0))
        self.assertIsNotNone(fire, lines)
        self.assertIn("at sleep 4", fire)

    def test_an_unflushed_cost_file_does_not_blind_the_reader(self) -> None:
        # the live shape at 18:1x: cost.jsonl EXISTS and is EMPTY (its writer's buffer holds the whole run), while the
        # arm's own snapshots have closed; the first version read 0 sleeps here for 19 hours
        d = self.run_dir("D")
        (d / "cost.jsonl").write_text("")
        for k in (1, 2):
            plant_sleep(d, k, T0 + 1)
        plant_sleep(d, 3, T0 + 100)
        plant_sleep(d, 4, T0 + 3600)
        lines, _, _, _ = P.poll(BUDGET, [P.Search(d, pid=1)], 7, T0 + 3700, procs=clock(3700.0))
        self.assertEqual(sum(1 for l in lines if " closed " in l), 4, lines)

    def test_sleeps_before_4_never_fire(self) -> None:
        d = self.run_dir("D")
        plant_sleep(d, 1, T0 + 1)
        plant_sleep(d, 2, T0 + 1)
        plant_sleep(d, 3, T0 + 1000)                   # r = 10 at sleep 3: descriptive only
        _, fire, _, _ = P.poll(BUDGET, [P.Search(d, pid=1)], 7, T0 + 1001, procs=clock(1001.0))
        self.assertIsNone(fire)

    def test_the_lower_bound_fires_while_the_sleep_is_still_running(self) -> None:
        d = self.run_dir("D")
        for k in (1, 2):
            plant_sleep(d, k, T0 + 1)
        plant_sleep(d, 3, T0 + 100)
        # still in sleep 4 (no sleep-4 snapshot) with 1.3 × its predicted cumulative already spent
        _, fire, _, _ = P.poll(BUDGET, [P.Search(d, pid=1)], 7, T0 + 4680, procs=clock(4680.0))
        self.assertIsNotNone(fire)
        self.assertIn("LOWER bound", fire)
        # the same place at 0.5 × is quiet
        _, fire, _, _ = P.poll(BUDGET, [P.Search(d, pid=1)], 7, T0 + 1800, procs=clock(1800.0))
        self.assertIsNone(fire)

    def test_a_vanished_process_is_reported(self) -> None:
        d = self.run_dir("D")
        plant_sleep(d, 1, T0 + 1)
        s = P.Search(d, pid=1)
        P.poll(BUDGET, [s], 7, T0 + 10, procs=clock(10.0))
        _, fire, _, dead = P.poll(BUDGET, [s], 7, T0 + 20, procs=clock(0.0, alive=False))
        self.assertIsNone(fire)
        self.assertEqual(len(dead), 1)
        self.assertIn("1/17", dead[0])

    def test_cpu_is_interpolated_between_polls(self) -> None:
        s = P.Search(self.run_dir("D"), pid=1, start=T0, samples=[(T0 + 100, 50.0), (T0 + 200, 150.0)])
        self.assertAlmostEqual(s.cpu_at(T0 + 150)[0], 100.0)
        self.assertAlmostEqual(s.cpu_at(T0 + 50)[0], 25.0)        # before the first poll: the life's ratio 0.5

    def test_record_passes_a_true_clock_and_catches_a_planted_shift(self) -> None:
        d = self.run_dir("D")
        walls = [0.02, 0.03, 1.5, 3.1]
        with (d / "cost.jsonl").open("w", encoding="utf-8") as f:
            for k, w in enumerate(walls, 1):
                f.write(json.dumps({"where": "sleep", "seq": 100 * k, "arm_ms": w * 900, "wall_s": w}) + "\n")
        for k, w in enumerate(walls, 1):
            plant_sleep(d, k, T0 + w)
        self.assertEqual(P.record(d), 0)
        p = d / "arm" / "library" / "sleep-3.json"
        os.utime(p, (T0 + 2.5, T0 + 2.5))              # one second late
        self.assertEqual(P.record(d), 1)


if __name__ == "__main__":
    unittest.main()
