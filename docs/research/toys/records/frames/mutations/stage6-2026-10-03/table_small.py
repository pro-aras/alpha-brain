"""Two small mutant tables of this session's OTHER code changes: verdicts.eye_reading's per-frame table and run.py's command line (`_main`). Each is selected by the TABLE env var (`eye` | `cli`).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 22:12 +0400 — new (the eye table and the gates CLI were written test-first today; their sweeps run beside the report's).
"""
import os

KIND = os.environ.get("TABLE", "eye")
MUTANTS = []


def M(name, old, new, expect, why, count=1):
    MUTANTS.append({"name": name, "old": old, "new": new, "expect": list(expect), "why": why, "count": count})


if KIND == "eye":
    T = "TestEyeReading.test_the_per_frame_table_each_said_frame_with_its_says_and_its_yes_count"
    M("eye-sort-says", "key=lambda kv: (-kv[1][\"says\"], kv[0]))", "key=lambda kv: (kv[1][\"says\"], kv[0]))", [T], "fewest says first")
    M("eye-sort-ties", "key=lambda kv: (-kv[1][\"says\"], kv[0]))", "key=lambda kv: (-kv[1][\"says\"],))", [T], "ties in the order the says came (not alphabetical)")
    M("eye-sort-ties-rev", "key=lambda kv: (-kv[1][\"says\"], kv[0]))", "key=lambda kv: (-kv[1][\"says\"], tuple(-ord(c) for c in kv[0])))", [T], "ties in reverse alphabetical order")
    M("eye-pair-list", '"pair": (list(e["pair"]) if e["pair"] is not None else None)', '"pair": e["pair"]', [T], "the pair stays a tuple")
    M("eye-pair-none", '"pair": (list(e["pair"]) if e["pair"] is not None else None)', '"pair": (list(e["pair"]) if e["pair"] is not None else [])', [T], "a said text that is not two words has an empty pair")
    M("eye-frame-text", '{"frame": text, "pair"', '{"frame": text.upper(), "pair"', [T], "the frame text is upper-cased")
    M("eye-says", '"says": e["says"], "yes": e["yes"]}\n              for text', '"says": e["yes"], "yes": e["yes"]}\n              for text', [T], "says prints the yes count")
    M("eye-yes", '"says": e["says"], "yes": e["yes"]}\n              for text', '"says": e["says"], "yes": e["says"]}\n              for text', [T], "yes prints the says count")
    M("eye-key-dropped", '"base_rate": (total_yes / total_says if total_says else None), "frames": frames, "records": recs}', '"base_rate": (total_yes / total_says if total_says else None), "records": recs}', [T], "the table is not returned")
    TABLE = {"module": "tools.toys.frames.verdicts", "file": "tools/toys/frames/verdicts.py", "tests": "tests.tools.test_toys_frames_verdicts",
             "control_broken": {"old": "def _need(rule: str, n: int) -> int:\n    return", "new": "def _need(rule: str, n: int) -> int:\n    raise RuntimeError('BROKEN CONTROL')\n    return"}, "mutants": MUTANTS}
else:
    T1 = "TestCli.test_gates_runs_run_gates_on_the_given_directories_and_returns_its_code"
    T2 = "TestCli.test_gates_defaults_to_the_runners_copies_and_runs_directories"
    T3 = "TestCli.test_the_unit_command_passes_its_options_to_run_unit"
    T4 = "TestCli.test_status_lists_each_condition_and_the_two_records"
    T5 = "TestCli.test_the_unit_command_still_refuses_without_a_passed_gates_record"
    M("cli-gates-const", "return GT.run_gates(Path(a.copies), out)", "return 0", [T1], "gates always exits 0")
    M("cli-gates-copies", "return GT.run_gates(Path(a.copies), out)", "return GT.run_gates(out, out)", [T1, T2], "the copies are the runs directory")
    M("cli-gates-out", "return GT.run_gates(Path(a.copies), out)", "return GT.run_gates(Path(a.copies), Path(a.copies))", [T1, T2], "the output is the copies directory")
    M("cli-gates-64", "return GT.run_gates(Path(a.copies), out)", "print('gates: see tools/toys/frames/gates.py', file=sys.stderr); return 64", [T1, T2], "the old stub")
    M("cli-unit-draws", 'ap.add_argument("--draws", type=int, default=100)', 'ap.add_argument("--draws", type=int, default=99)', [T3], "the law's 100 draws become 99")
    M("cli-unit-only", 'only = [x for x in a.only.split(",") if x] or None', 'only = [x for x in a.only.split(",")] or None', [T3], "an empty --only is [''] instead of None")
    M("cli-unit-only-none", 'only = [x for x in a.only.split(",") if x] or None', "only = None", [T3], "--only is ignored")
    M("cli-unit-draws-pass", "return run_unit(Path(a.copies), out, draws=a.draws, only=only)", "return run_unit(Path(a.copies), out, only=only)", [T3], "--draws is not passed")
    M("cli-unit-copies", "return run_unit(Path(a.copies), out, draws=a.draws, only=only)", "return run_unit(out, out, draws=a.draws, only=only)", [T3], "the unit reads the runs directory as copies")
    M("cli-status-text", "'on disk' if (out / f'{name}.json').exists() else 'missing'}\")", "'missing' if (out / f'{name}.json').exists() else 'on disk'}\")", [T4], "on disk / missing swapped")
    M("cli-status-results", "print(f\"RESULTS.json: {'on disk' if (out / 'RESULTS.json').exists() else 'missing'};", "print(f\"RESULTS.json: {'on disk' if (out / 'GATES.json').exists() else 'missing'};", [T4], "RESULTS.json reads GATES.json")
    M("cli-status-code", "print(f\"RESULTS.json: {'on disk' if (out / 'RESULTS.json').exists() else 'missing'}; GATES.json: {'on disk' if (out / 'GATES.json').exists() else 'missing'}\")\n        return 0", "print(f\"RESULTS.json: {'on disk' if (out / 'RESULTS.json').exists() else 'missing'}; GATES.json: {'on disk' if (out / 'GATES.json').exists() else 'missing'}\")\n        return 1", [T4], "status exits 1")
    TABLE = {"module": "tools.toys.frames.run", "file": "tools/toys/frames/run.py", "tests": "tests.tools.test_toys_frames_run",
             "control_broken": {"old": "def write_json(path: Path, obj) -> None:\n    path.parent", "new": "def write_json(path: Path, obj) -> None:\n    raise RuntimeError('BROKEN CONTROL')\n    path.parent"}, "mutants": MUTANTS}
