# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:29 +0400 — PREREG-EVOLVE-CAL: the twin queue (one twin at a time, resumable): tests FIRST.
"""tests/tools/test_evolve_cal_queue.py — tools/evolve_cal_queue.py: a list of twins run ONE AT A TIME through slot, resumable.

The seat's rule (21:1x): one twin at a time (6.5 GB each beside brain-long-3's ~10 GB), SLOT_MEM=8G, sequential. The queue is a TSV (label, variant, rows-limit or -).
A twin is DONE when `<out>/<label>/reading.json` exists (run_twin writes it last, atomically); a half-written twin directory is moved aside, never deleted and never
overwritten; the queue stops at the first twin that does not exit 0.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import tools.evolve_cal_queue as q


def lst(tmp: Path, text: str) -> Path:
    p = tmp / "list.tsv"
    p.write_text(text)
    return p


ARGS = dict(cp="/cp/32", slice_root="/slices/S1", from_seq=304002, to_seq=308667, lane="integrator", slot="/bin/slot", slot_mem="8G", python="/usr/bin/python3")


class TestParse(unittest.TestCase):
    def test_a_list_is_label_variant_and_an_optional_rows_limit(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        entries = q.read_list(lst(tmp, "# a comment\n\ninc\tincumbent\t-\nseed01\tseed:1\t-\nshort\teps:0.01:1\t1000\n"))
        self.assertEqual(entries, [("inc", "incumbent", None), ("seed01", "seed:1", None), ("short", "eps:0.01:1", 1000)])

    def test_a_duplicate_label_a_bad_variant_or_a_bad_label_is_refused_by_name(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        for bad in ("a\tincumbent\t-\na\tseed:1\t-\n", "a\tbogus:1\t-\n", "a b\tincumbent\t-\n", "../x\tincumbent\t-\n", "a\tincumbent\n", "a\tincumbent\t-1\n"):
            with self.assertRaises(ValueError, msg=bad):
                q.read_list(lst(tmp, bad))


class TestPlan(unittest.TestCase):
    def test_a_twin_is_planned_as_one_slot_command_with_its_cap(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "out"
        plan = q.plan([("inc", "incumbent", None), ("short", "eps:0.01:1", 1000)], out, **ARGS)
        self.assertEqual([p["label"] for p in plan], ["inc", "short"])
        first = plan[0]
        self.assertEqual(first["argv"][:5], ["/bin/slot", "integrator", "evcal-inc", "--", "/usr/bin/time"])
        self.assertIn("tools.evolve_cal", first["argv"])
        self.assertEqual(first["argv"][first["argv"].index("--variant") + 1], "incumbent")
        self.assertEqual(first["argv"][first["argv"].index("--out") + 1], str(out / "inc"))
        self.assertNotIn("--rows-limit", first["argv"])
        self.assertEqual(plan[1]["argv"][plan[1]["argv"].index("--rows-limit") + 1], "1000")
        self.assertEqual(first["env"]["SLOT_MEM"], "8G")
        self.assertEqual(first["log"], out / "inc.log")
        self.assertEqual(first["exit"], out / "inc.exit")

    def test_a_finished_twin_is_skipped_and_a_half_written_one_is_set_aside(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "out"
        (out / "done").mkdir(parents=True)
        (out / "done" / "reading.json").write_text("{}")
        (out / "half").mkdir(parents=True)
        (out / "half" / "GENOME.genome").write_text("x")
        plan = q.plan([("done", "incumbent", None), ("half", "seed:1", None), ("new", "seed:2", None)], out, **ARGS)
        self.assertEqual([p["label"] for p in plan], ["half", "new"])
        self.assertEqual(plan[0]["set_aside"], out / "half.stale-1")
        self.assertIsNone(plan[1]["set_aside"])

    def test_stale_directories_never_collide(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "out"
        (out / "half").mkdir(parents=True)
        (out / "half.stale-1").mkdir()
        plan = q.plan([("half", "seed:1", None)], out, **ARGS)
        self.assertEqual(plan[0]["set_aside"], out / "half.stale-2")


class TestRun(unittest.TestCase):
    def test_the_queue_runs_in_order_one_at_a_time_and_stops_at_the_first_failure(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "out"
        ran, live = [], [0]
        peak = [0]

        def fake(argv, env, log):
            live[0] += 1
            peak[0] = max(peak[0], live[0])
            ran.append(argv[2])
            live[0] -= 1
            return 0 if argv[2] != "evcal-b" else 3

        results = q.run([("a", "incumbent", None), ("b", "seed:1", None), ("c", "seed:2", None)], out, runner=fake, **ARGS)
        self.assertEqual(ran, ["evcal-a", "evcal-b"], "c never ran: the queue stops at the first failure")
        self.assertEqual(peak[0], 1)
        self.assertEqual([(r["label"], r["exit"]) for r in results], [("a", 0), ("b", 3)])
        self.assertEqual((out / "a.exit").read_text().strip(), "0")
        self.assertEqual((out / "b.exit").read_text().strip(), "3")
        self.assertFalse((out / "c.exit").exists())

    def test_dry_run_plans_and_writes_nothing(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "out"
        calls = []
        results = q.run([("a", "incumbent", None)], out, runner=lambda *a: calls.append(a) or 0, dry_run=True, **ARGS)
        self.assertEqual(calls, [])
        self.assertEqual(results[0]["exit"], None)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
