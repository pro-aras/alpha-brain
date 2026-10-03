"""sweep.py — a mutation sweep over ONE module (TOY C's gates.py, report.py ...): each mutant is a single textual replacement applied IN MEMORY (mutrun.py), run through slot, and judged CAUGHT only
when the run FAILS and the NAMED catching test(s) are among the failing tests.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:29 +0400 — new sweep driver (the relaunched lane); replaces the predecessor's unrecorded one-off mutations: the table is data, the mutated source and its diff are saved.

usage: PYTHONPATH=. python3 -B -u scratch/mutgates2/sweep.py <table.py> <outdir> [--only name,name] [--jobs 3] [--label tag]

A table is a python file defining TABLE = {"module": dotted name, "file": path, "tests": dotted unittest module, "control_broken": {old, new}, "mutants": [ {name, old, new, expect: ["Class.method", ...], why, [count]} ... ]}.
Every mutant: `old` must occur exactly `count` (default 1) times in the file (a mutation that does not apply is an ERROR, never a pass), the mutated text must DIFFER from the original (the plant asserts it changed
the bytes, #247 (5)), its unified diff is saved. Two controls are added by the driver: IDENTITY (the unmutated text through the same injection, must PASS) and BROKEN (the table's control_broken replacement, an unconditional raise, must be CAUGHT) — a harness that cannot tell them apart measures nothing.
Verdicts: CAUGHT (exit 1, expected tests among the failing ones), CAUGHT-UNEXPECTED (exit 1 but not by the named test: the named test is wrong or missing), SURVIVED (exit 0), HARNESS (anything else).
"""
from __future__ import annotations

import concurrent.futures as cf
import difflib
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SLOT = "/data/dev/swarm/bin/slot"
HERE = Path(__file__).resolve().parent


def load_table(path: Path):
    spec = importlib.util.spec_from_file_location("mut_table", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TABLE


def failing_tests(log: str):
    out = []
    for m in re.finditer(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", log, flags=re.M):
        out.append(m.group(3))                                    # the dotted id: tests.tools.<module>.<Class>.<method>
    return out


def run_one(table, mut, outdir: Path, label: str, source: str):
    name = mut["name"]
    d = outdir / name
    d.mkdir(parents=True, exist_ok=True)
    kind = mut.get("kind", "mutant")
    if kind == "identity":
        mutated = source
    elif kind == "broken":
        cb = table["control_broken"]
        if source.count(cb["old"]) != 1:
            return {"name": name, "verdict": "ERROR", "detail": "the broken control's `old` does not occur exactly once", "failing": [], "secs": 0.0}
        mutated = source.replace(cb["old"], cb["new"], 1)
    else:
        n = source.count(mut["old"])
        want = mut.get("count", 1)
        if n != want:
            return {"name": name, "verdict": "ERROR", "detail": f"`old` occurs {n} times, expected {want}", "failing": [], "secs": 0.0}
        mutated = source.replace(mut["old"], mut["new"], 1)
    if kind == "mutant" and mutated == source:
        return {"name": name, "verdict": "ERROR", "detail": "the mutation did not change the bytes", "failing": [], "secs": 0.0}
    if kind == "broken" and mutated == source:
        return {"name": name, "verdict": "ERROR", "detail": "the broken control did not change the bytes", "failing": [], "secs": 0.0}
    mpath = d / Path(table["file"]).name
    mpath.write_text(mutated)
    (outdir / f"{name}.diff").write_text("".join(difflib.unified_diff(source.splitlines(True), mutated.splitlines(True), "a/" + table["file"], "b/" + table["file"], n=1)))
    log_path = outdir / f"{name}.log"
    env = dict(os.environ, SLOT_MEM="1G", PYTHONPATH=".", OPENBLAS_NUM_THREADS="1", TMPDIR=str(Path("scratch/tmp").resolve()))
    cmd = [SLOT, "toys", f"{label}-{name}", "--", sys.executable, "-B", "-u", str(HERE / "mutrun.py"), table["module"], str(mpath), table["tests"]]
    t0 = time.time()
    with open(log_path, "w") as fh:
        p = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, env=env)
    secs = time.time() - t0
    (outdir / f"{name}.exit").write_text(f"{p.returncode}\n")
    log = log_path.read_text()
    loaded = "MUTANT-LOADED:" in log and "TESTS-USE-THE-MUTANT: True" in log
    fails = failing_tests(log)
    if not loaded:
        verdict, detail = "HARNESS", "the mutant was not loaded / the tests do not use it"
    elif p.returncode == 0:
        verdict, detail = "SURVIVED", ""
    elif p.returncode == 1:
        exp = mut.get("expect", [])
        missing = [e for e in exp if not any(f.endswith("." + e) for f in fails)]
        verdict, detail = ("CAUGHT", "") if not missing else ("CAUGHT-UNEXPECTED", f"named test(s) did not fail: {missing}")
    else:
        verdict, detail = "HARNESS", f"exit {p.returncode}"
    if kind == "identity":
        verdict = "CONTROL-OK" if verdict == "SURVIVED" else "CONTROL-FAIL"
    if kind == "broken":
        verdict = "CONTROL-OK" if verdict.startswith("CAUGHT") else "CONTROL-FAIL"
    return {"name": name, "verdict": verdict, "detail": detail, "failing": [f.rsplit(".", 2)[-2] + "." + f.rsplit(".", 1)[-1] for f in fails], "secs": secs}


def main(argv) -> int:
    table = load_table(Path(argv[0]))
    outdir = Path(argv[1])
    only = None
    jobs = 3
    label = "mutgt2"
    rest = list(argv[2:])
    if "--only" in rest:
        only = set(rest[rest.index("--only") + 1].split(","))
    if "--jobs" in rest:
        jobs = int(rest[rest.index("--jobs") + 1])
    if "--label" in rest:
        label = rest[rest.index("--label") + 1]
    outdir.mkdir(parents=True, exist_ok=True)
    source = Path(table["file"]).read_text()
    sha = hashlib.sha256(source.encode()).hexdigest()
    muts = [{"name": "CONTROL-identity", "kind": "identity"}, {"name": "CONTROL-broken", "kind": "broken"}] + list(table["mutants"])
    if only:
        muts = [m for m in muts if m["name"] in only]
    names = [m["name"] for m in muts]
    assert len(names) == len(set(names)), "duplicate mutant names"
    (outdir / "MUTANTS.json").write_text(json.dumps({"module": table["module"], "file": table["file"], "source_sha256": sha, "tests": table["tests"],
                                                      "mutants": [m for m in muts]}, indent=1, sort_keys=True))
    results = []
    with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(run_one, table, m, outdir, label, source): m for m in muts}
        for f in cf.as_completed(futs):
            r = f.result()
            results.append(r)
            print(f"{r['verdict']:<17} {r['name']:<40} {r['secs']:5.1f}s  {', '.join(r['failing'][:3])}{' ...' if len(r['failing']) > 3 else ''} {r['detail']}", flush=True)
    order = {n: i for i, n in enumerate(names)}
    results.sort(key=lambda r: order[r["name"]])
    with open(outdir / "SWEEP.tsv", "w") as fh:
        fh.write("verdict\tmutant\tsecs\tfailing_tests\tdetail\n")
        for r in results:
            fh.write(f"{r['verdict']}\t{r['name']}\t{r['secs']:.1f}\t{';'.join(r['failing'])}\t{r['detail']}\n")
    bad = [r for r in results if r["verdict"] not in ("CAUGHT", "CONTROL-OK")]
    n_m = sum(1 for r in results if not r["name"].startswith("CONTROL-"))
    n_c = sum(1 for r in results if r["verdict"] == "CAUGHT")
    print(f"SWEEP {table['module']}: {n_c} of {n_m} mutants CAUGHT by their named test; not caught: {[r['name'] + ':' + r['verdict'] for r in bad]}; source sha256 {sha[:16]}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
