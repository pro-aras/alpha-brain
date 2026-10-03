# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:03 +0400 — PREREG-RESIT-READER v4 §5 / R10f: tools/brain/rebuild_origin.py's PILOT — the first K rows of a life's tape replayed by the life's own Mind with CPU and peak
# memory sampled, and the cost extrapolated to the begin row with the growth the pilot shows (a three-way bracket beside the 4 CPU-h line). Written BEFORE the tool. The pure parts first (the prefix cut,
# /proc parsing, per-interval cost, the growth fit, the extrapolation arithmetic), then the whole pilot on a STUB life (a tiny `creature`/`genome` tree). Every plant asserts it changed the bytes.
"""tests/tools/test_rebuild_origin.py — the rebuild's pilot."""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from tools.brain import rebuild_origin as RB

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "brain" / "rebuild_origin.py"
ENV = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}


class Tmp(unittest.TestCase):
    def mk(self, prefix: str = "rebuild-") -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d


def write_days(tape: Path, days: list) -> list:
    """days: [[seq, ...], ...] -> tape/<day>.jsonl with one row per seq; returns every row in order."""
    tape.mkdir(parents=True, exist_ok=True)
    (tape / "payload").mkdir(exist_ok=True)
    rows = []
    for d, seqs in enumerate(days):
        with (tape / f"2026-10-0{d + 1}.jsonl").open("w") as f:
            for s in seqs:
                r = {"seq": s, "at": f"2026-10-0{d + 1}T00:00:00.000Z", "sense": "eye" if s % 2 == 0 else "ear", "sha": f"sha{s}", "payload": f"payload/{s:09d}.png", "meta": {"moment": f"m{s // 2}"}}
                f.write(json.dumps(r) + "\n")
                rows.append(r)
    return rows


class TestCutPrefix(Tmp):
    def test_the_first_k_rows_across_day_files_in_order_and_the_payload_dir_is_a_symlink_to_the_lifes(self) -> None:
        root = self.mk()
        rows = write_days(root / "tape", [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        out = self.mk()
        res = RB.cut_prefix(root / "tape", out, 7)
        self.assertEqual((res["rows"], res["last_seq"]), (7, 7))
        got = [json.loads(l) for f in sorted((out / "tape").glob("*.jsonl")) for l in f.read_text().splitlines()]
        self.assertEqual(got, rows[:7])
        self.assertTrue((out / "tape" / "payload").is_symlink())
        self.assertEqual(os.path.realpath(out / "tape" / "payload"), os.path.realpath(root / "tape" / "payload"))
        self.assertEqual(sorted(p.name for p in (out / "tape").glob("*.jsonl")), ["2026-10-01.jsonl", "2026-10-02.jsonl", "2026-10-03.jsonl"])

    def test_a_k_beyond_the_tape_takes_all_of_it_and_a_k_inside_one_file_stops_there(self) -> None:
        root = self.mk()
        write_days(root / "tape", [[1, 2, 3], [4, 5]])
        a, b = self.mk(), self.mk()
        self.assertEqual(RB.cut_prefix(root / "tape", a, 1000)["rows"], 5)
        res = RB.cut_prefix(root / "tape", b, 2)
        self.assertEqual((res["rows"], res["last_seq"]), (2, 2))
        self.assertFalse((b / "tape" / "2026-10-02.jsonl").exists(), "no row of the second day was needed")

    def test_a_torn_last_line_is_never_copied_and_is_counted(self) -> None:
        root = self.mk()
        write_days(root / "tape", [[1, 2, 3]])
        with (root / "tape" / "2026-10-01.jsonl").open("a") as f:
            f.write('{"seq": 4, "at": "t", "sense": "eye", "sha')              # a live file's half-written last line
        out = self.mk()
        res = RB.cut_prefix(root / "tape", out, 100)
        self.assertEqual(res["rows"], 3)
        self.assertEqual(res["torn_lines"], 1)
        self.assertEqual(len((out / "tape" / "2026-10-01.jsonl").read_text().splitlines()), 3)

    def test_the_source_tape_is_only_read_sizes_and_mtimes_are_unchanged(self) -> None:
        root = self.mk()
        write_days(root / "tape", [[1, 2, 3], [4, 5, 6]])
        before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in (root / "tape").iterdir()}
        RB.cut_prefix(root / "tape", self.mk(), 4)
        after = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in (root / "tape").iterdir()}
        self.assertEqual(before, after)


class TestProcStatus(unittest.TestCase):
    def test_vmrss_and_vmhwm_are_read_in_megabytes(self) -> None:
        text = "Name:\tpython3\nVmPeak:\t 2000000 kB\nVmHWM:\t 1536000 kB\nVmRSS:\t 1024000 kB\nThreads:\t3\n"
        r = RB.parse_proc_status(text)
        self.assertAlmostEqual(r["rss_mb"], 1000.0)
        self.assertAlmostEqual(r["hwm_mb"], 1500.0)

    def test_a_missing_field_reads_none_never_zero(self) -> None:
        r = RB.parse_proc_status("Name:\tx\n")
        self.assertIsNone(r["rss_mb"])
        self.assertIsNone(r["hwm_mb"])

    def test_the_real_status_of_this_process_parses(self) -> None:
        r = RB.read_self_status()
        self.assertGreater(r["rss_mb"], 1)
        self.assertGreaterEqual(r["hwm_mb"], r["rss_mb"])


def synth_samples(c0: float, p: float, n_rows: int, step: int, rss0: float = 500.0, rss_per_row: float = 0.01) -> list:
    """Samples of a replay whose per-row CPU is c0 * i^p exactly: cumulative CPU = c0 * i^(p+1) / (p+1)."""
    out = []
    for i in range(step, n_rows + 1, step):
        out.append({"i": i, "cpu_s": c0 * i ** (p + 1) / (p + 1), "wall_s": 1.5 * c0 * i ** (p + 1) / (p + 1), "rss_mb": rss0 + rss_per_row * i, "hwm_mb": rss0 + rss_per_row * i})
    return out


class TestRates(unittest.TestCase):
    def test_per_interval_cost_is_the_cpu_between_samples_over_the_rows_between_them_at_the_intervals_midpoint(self) -> None:
        s = [{"i": 100, "cpu_s": 10.0}, {"i": 200, "cpu_s": 30.0}, {"i": 400, "cpu_s": 90.0}]
        r = RB.interval_rates(s)
        self.assertEqual(r, [(50.0, 0.1), (150.0, 0.2), (300.0, 0.3)])

    def test_the_fit_recovers_an_exact_power_law(self) -> None:
        s = synth_samples(0.002, 0.5, 20000, 500)
        fit = RB.fit_power_law(RB.interval_rates(s)[1:])
        self.assertAlmostEqual(fit["p"], 0.5, places=2)
        self.assertAlmostEqual(fit["a"], 0.002, places=4)

    def test_a_constant_cost_fits_an_exponent_of_zero_and_the_plant_is_not_zero(self) -> None:
        flat = synth_samples(0.003, 0.0, 10000, 500)
        grow = synth_samples(0.003, 1.0, 10000, 500)
        self.assertNotEqual(flat[-1]["cpu_s"], grow[-1]["cpu_s"], "the plant must change the data")
        self.assertAlmostEqual(RB.fit_power_law(RB.interval_rates(flat)[1:])["p"], 0.0, places=2)
        self.assertAlmostEqual(RB.fit_power_law(RB.interval_rates(grow)[1:])["p"], 1.0, places=2)


class TestExtrapolation(unittest.TestCase):
    def test_the_central_prediction_equals_the_analytic_integral_and_the_bracket_is_ordered(self) -> None:
        c0, p, K, B = 0.002, 0.5, 20000, 160000
        s = synth_samples(c0, p, K, 500)
        e = RB.extrapolate_cpu(s, B)
        truth = c0 * B ** (p + 1) / (p + 1)
        self.assertAlmostEqual(e["central_cpu_s"] / truth, 1.0, places=2)
        self.assertLess(e["lower_cpu_s"], e["central_cpu_s"])
        self.assertLessEqual(e["central_cpu_s"], e["upper_cpu_s"] * 1.0000001)
        self.assertAlmostEqual(e["central_cpu_h"], e["central_cpu_s"] / 3600.0)
        self.assertEqual(e["measured_cpu_s"], s[-1]["cpu_s"])
        self.assertEqual((e["pilot_rows"], e["target_rows"]), (K, B))

    def test_the_lower_bound_ignores_growth_it_is_the_last_windows_rate_held_constant(self) -> None:
        s = synth_samples(0.002, 1.0, 10000, 500)
        e = RB.extrapolate_cpu(s, 20000)
        last_rate = (s[-1]["cpu_s"] - s[-2]["cpu_s"]) / (s[-1]["i"] - s[-2]["i"])
        self.assertAlmostEqual(e["lower_cpu_s"], s[-1]["cpu_s"] + last_rate * (20000 - 10000), places=6)

    def test_a_target_inside_the_pilot_is_refused_by_name(self) -> None:
        s = synth_samples(0.002, 0.5, 10000, 500)
        with self.assertRaises(ValueError) as cm:
            RB.extrapolate_cpu(s, 9000)
        self.assertIn("target", str(cm.exception))

    def test_memory_is_extrapolated_linearly_from_the_samples_and_the_bracket_names_both_ends(self) -> None:
        s = synth_samples(0.002, 0.5, 20000, 500, rss0=500.0, rss_per_row=0.02)
        m = RB.extrapolate_rss(s, 160000)
        self.assertAlmostEqual(m["central_rss_mb"], 500.0 + 0.02 * 160000, places=0)
        self.assertEqual(m["rss_at_start_mb"], s[0]["rss_mb"])
        self.assertEqual(m["rss_at_end_mb"], s[-1]["rss_mb"])
        self.assertGreaterEqual(m["peak_hwm_mb"], m["rss_at_end_mb"])
        self.assertLessEqual(m["lower_rss_mb"], m["central_rss_mb"])


# ------------------------------------------------------------------------------------------------ the whole pilot on a STUB life
STUB = {
    "genome/__init__.py": "",
    "creature/__init__.py": "",
    "genome/machinery.py": '''
class G:
    def __init__(self, declared): self.declared = declared

def parse_genome(text):
    declared = {}
    for line in text.splitlines():
        w = line.split("#", 1)[0].split()
        if w[:1] == ["TAPE"]:
            declared["TAPE"] = {"path": w[1]}
    return G(declared)
''',
    "creature/tape.py": '''
from pathlib import Path

def _resolve_tape_dir(root, declared_path):
    root = Path(root)
    if not declared_path:
        return root / "tape"
    parts = Path(declared_path).parts
    if parts and parts[0] == "run":
        parts = parts[1:]
    return root / Path(*parts) if parts else root / "tape"
''',
    "creature/mind.py": '''
import os, time
from pathlib import Path

class _Org:
    def summary(self):
        return {"cells": self.cells}

class Mind:
    """A stub: each consumed row burns a growing slice of CPU (a quadratic-ish replay) and holds a growing buffer (memory growth)."""
    def __init__(self, genome_path, run_root, blind=frozenset()):
        self.genome_path, self.run_root = Path(genome_path), Path(run_root)
        self.n = 0
        self.held = []
        self.org = _Org(); self.org.cells = 0
        (self.run_root / "journal").mkdir(parents=True, exist_ok=True)

    def consume(self, row):
        self.n += 1
        burn = float(os.environ.get("STUB_BURN_PER_ROW", "0")) * (1.0 + self.n / 200.0)
        t0 = time.process_time()
        while time.process_time() - t0 < burn:
            pass
        if self.n %% 10 == 0:
            self.held.append(bytearray(int(float(os.environ.get("STUB_MB_PER_10_ROWS", "0")) * 1024 * 1024)))
        self.org.cells = self.n // 3
''',
}


def build_stub(root: Path) -> Path:
    for rel, body in STUB.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).replace("%%", "%") if rel.endswith(".py") else body)
    return root


def run_tool(args: list, env_over: dict = None, dash=("-B", "-I")):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update(ENV)
    env.update(env_over or {})
    return subprocess.run([sys.executable, *dash, str(TOOL), *args], capture_output=True, text=True, env=env)


class PilotBase(Tmp):
    def setUp(self) -> None:
        self.work = self.mk("rebuild-pilot-")
        self.code = build_stub(self.work / "code")
        self.life = self.work / "life"
        self.life.mkdir()
        (self.life / "GENOME.genome").write_text("TAPE run/tape\n")
        write_days(self.life / "tape", [list(range(1, 201)), list(range(201, 401))])
        self.out = self.work / "out"

    def pilot(self, *extra, env_over=None, dash=("-B", "-I")):
        p = run_tool(["pilot", "--root", str(self.life), "--code", str(self.code), "--out", str(self.out), "--rows", "300", "--sample-every", "50", "--target-rows", "5000", *extra],
                     env_over=env_over, dash=dash)
        f = self.out / "pilot.json"
        return p, (json.loads(f.read_text()) if f.exists() else None)


class TestPilot(PilotBase):
    def test_the_pilot_replays_k_rows_through_the_lifes_own_mind_and_samples_cost_and_memory(self) -> None:
        p, r = self.pilot(env_over={"STUB_BURN_PER_ROW": "0.0005", "STUB_MB_PER_10_ROWS": "1"})
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual((r["rows_replayed"], r["stopped"]), (300, "rows"))
        self.assertEqual([s["i"] for s in r["samples"]], [50, 100, 150, 200, 250, 300])
        self.assertGreater(r["samples"][-1]["cpu_s"], r["samples"][0]["cpu_s"])
        self.assertGreater(r["samples"][-1]["rss_mb"], r["samples"][0]["rss_mb"] - 1, "the held buffers make the memory grow")
        self.assertEqual(r["samples"][-1]["cells"], 100, "the stub's own organism summary is read at every sample")
        self.assertEqual(r["subject"]["code"], os.path.realpath(self.code))

    def test_the_prices_carry_the_extrapolation_to_the_target_and_the_line_it_is_read_against(self) -> None:
        p, r = self.pilot(env_over={"STUB_BURN_PER_ROW": "0.0005", "STUB_MB_PER_10_ROWS": "1"})
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        e = r["cpu"]
        self.assertEqual(e["target_rows"], 5000)
        self.assertLess(e["lower_cpu_s"], e["central_cpu_s"])
        self.assertEqual(r["stop_line_cpu_h"], 4.0)
        self.assertIn(r["verdict_vs_line"], ("UNDER", "OVER", "STRADDLES"))
        self.assertEqual(r["memory"]["target_rows"], 5000)
        self.assertGreater(r["memory"]["central_rss_mb"], r["memory"]["rss_at_start_mb"])
        for k in ("windows", "fit"):
            self.assertIn(k, r["cpu"])

    def test_the_pilot_stops_at_its_cpu_cap_and_says_so(self) -> None:
        p, r = self.pilot("--cpu-cap-s", "0.6", env_over={"STUB_BURN_PER_ROW": "0.01"})
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(r["stopped"], "cpu cap")
        self.assertLess(r["rows_replayed"], 300)
        self.assertGreater(r["rows_replayed"], 0)

    def test_the_lifes_tape_is_only_read_and_the_life_gets_no_new_file(self) -> None:
        before = sorted((str(p.relative_to(self.life)), p.stat().st_size, p.stat().st_mtime_ns) for p in self.life.rglob("*") if p.is_file())
        p, r = self.pilot()
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        after = sorted((str(p.relative_to(self.life)), p.stat().st_size, p.stat().st_mtime_ns) for p in self.life.rglob("*") if p.is_file())
        self.assertEqual(before, after)

    def test_a_run_without_dash_B_or_dash_I_or_with_other_blas_pins_is_refused(self) -> None:
        for dash, env_over, needle in [(("-I",), {}, "-B"), (("-B",), {}, "-I"), (("-B", "-I"), {"OPENBLAS_NUM_THREADS": "4"}, "OPENBLAS_NUM_THREADS")]:
            with self.subTest(dash=dash, env=env_over):
                p, r = self.pilot(env_over=env_over, dash=dash)
                self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
                self.assertIn(needle, p.stdout)
                self.assertFalse((self.out / "pilot.json").exists())

    def test_an_out_inside_the_life_is_refused(self) -> None:
        p = run_tool(["pilot", "--root", str(self.life), "--code", str(self.code), "--out", str(self.life / "rb"), "--rows", "10", "--target-rows", "100"])
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("inside", p.stdout)
        self.assertFalse((self.life / "rb").exists())

    def test_a_module_of_the_lifes_packages_imported_before_the_import_step_is_refused_R11(self) -> None:
        wrapper = self.work / "wrapper.py"
        wrapper.write_text(textwrap.dedent(f'''
            import sys, runpy
            sys.path.insert(0, {str(REPO)!r})
            import genome.gaze
            sys.argv = sys.argv[1:]
            runpy.run_path(sys.argv[0], run_name="__main__")
        '''))
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(ENV)
        p = subprocess.run([sys.executable, "-B", "-I", str(wrapper), str(TOOL), "pilot", "--root", str(self.life), "--code", str(self.code), "--out", str(self.out), "--rows", "10",
                            "--target-rows", "100"], capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("R11", p.stdout)

    def test_the_mind_that_ran_is_the_one_under_the_code_dir_not_the_repos(self) -> None:
        p, r = self.pilot()
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertTrue(all(m["rel"].startswith(("creature/", "genome/")) for m in r["subject"]["modules"]))
        self.assertIn("creature/mind.py", {m["rel"] for m in r["subject"]["modules"]})


if __name__ == "__main__":
    unittest.main()
