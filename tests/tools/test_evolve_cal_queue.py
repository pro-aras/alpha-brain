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


# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:5x +0400 — AMENDMENT 3b A3b.4 (the verifier's E4), tests FIRST: N2 in the non-degenerate branch needs epsilon twins at the
# chosen level on S2 (`N2-S2.tsv` is seed twins only: a seed twin never moves q1_seen or confirmed_share, so F = infinity by construction); the list is written from the chosen level.
class TestEpsList(unittest.TestCase):
    def test_the_list_is_the_incumbent_and_n_twins_of_one_level_numbered_from_one(self) -> None:
        text = q.eps_list(0.001, 6, prefix="s2-", with_incumbent=True)
        tmp = Path(tempfile.mkdtemp())
        entries = q.read_list(lst(tmp, text))
        self.assertEqual(entries[0], ("s2-inc", "incumbent", None))
        self.assertEqual([e[0] for e in entries[1:]], [f"s2-eps1e-3-k0{k}" for k in range(1, 7)])
        self.assertEqual([e[1] for e in entries[1:]], [f"eps:0.001:{k}" for k in range(1, 7)])
        self.assertTrue(all(e[2] is None for e in entries), "full slice: no rows limit")

    def test_the_level_tags_match_the_existing_lists(self) -> None:
        for level, tag, variant in ((1e-4, "1e-4", "eps:0.0001:1"), (1e-3, "1e-3", "eps:0.001:1"), (1e-2, "1e-2", "eps:0.01:1")):
            entries = q.read_list(lst(Path(tempfile.mkdtemp()), q.eps_list(level, 1)))
            self.assertEqual(entries, [(f"eps{tag}-k01", variant, None)])

    def test_without_the_incumbent_there_is_no_inc_line_and_two_digit_numbering_reaches_twenty(self) -> None:
        entries = q.read_list(lst(Path(tempfile.mkdtemp()), q.eps_list(1e-2, 20)))
        self.assertEqual(len(entries), 20)
        self.assertEqual((entries[0][0], entries[-1][0]), ("eps1e-2-k01", "eps1e-2-k20"))
        self.assertNotIn("incumbent", [e[1] for e in entries])

    def test_a_level_outside_the_three_or_a_count_outside_one_to_twenty_is_refused(self) -> None:
        for level, n in ((1e-5, 5), (0.002, 5), (1e-3, 0), (1e-3, 21), (1e-3, -1)):
            with self.assertRaises(ValueError, msg=f"{level} {n}"):
                q.eps_list(level, n)

    def test_the_cli_writes_the_file_and_refuses_to_overwrite_one(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "N2-S2-eps.tsv"
        self.assertEqual(q.main(["make-eps-list", "--eps", "0.001", "--n", "6", "--prefix", "s2-", "--with-incumbent", "--out", str(out)]), 0)
        self.assertEqual(q.read_list(out)[0], ("s2-inc", "incumbent", None))
        with self.assertRaises(FileExistsError):
            q.main(["make-eps-list", "--eps", "0.001", "--n", "6", "--out", str(out)])


if __name__ == "__main__":
    unittest.main()
