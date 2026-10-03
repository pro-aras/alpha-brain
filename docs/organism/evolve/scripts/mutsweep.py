#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:48 +0400 — EVOLVE-CAL: a mutation sweep with a NAMED expected catching test per mutant.
"""docs/organism/evolve/scripts/mutsweep.py — validate an instrument's tests by planting faults in a COPY of the module.

usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/mutsweep.py --tree <worktree> --module tools/evolve_cal.py \
           --tests tests.tools.test_evolve_cal_twin --mutants docs/organism/evolve/scripts/mutants_cal_twin.json --out <dir> [--only name,name]

A temp tree is built next to the real one: `tools/` is a real COPY (the mutated file lives there), every other top-level entry is a
symlink to the real tree, so `import tools.…` resolves to the copy and nothing in the worktree is ever written. The BASELINE (no
mutant) must pass first. Each mutant is `{name, old, new, expect}`: `old` must occur EXACTLY ONCE in the module (a mutant that
changes nothing is refused), `expect` is a substring of the test name that must be among the failing tests. Exit 0 iff the baseline
passed and every mutant was CAUGHT by its named test; the table is printed and written to <out>/mutsweep.json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def build_tree(real: Path, dest: Path) -> None:
    dest.mkdir(parents=True)
    for entry in sorted(os.listdir(real)):
        if entry in (".git", "scratch", "__pycache__"):
            continue
        src = real / entry
        if entry == "tools":
            shutil.copytree(src, dest / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        else:
            os.symlink(src, dest / entry)
    (dest / "scratch" / "tmp").mkdir(parents=True)


def run_tests(tree: Path, tests: str, log: Path) -> tuple[int, list[str]]:
    env = dict(os.environ, PYTHONPATH=".", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", TMPDIR=str(tree / "scratch" / "tmp"))
    with log.open("w") as f:
        p = subprocess.run([sys.executable, "-B", "-u", "-m", "unittest", "-v", *tests.split()], cwd=tree, env=env, stdout=f, stderr=subprocess.STDOUT)
    text = log.read_text(errors="replace")
    failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+)", text, re.MULTILINE)))
    return p.returncode, failing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--tests", required=True)
    ap.add_argument("--mutants", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args(argv)
    real, out = Path(a.tree).resolve(), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    mutants = json.loads(Path(a.mutants).read_text())
    if a.only:
        want = set(a.only.split(","))
        mutants = [m for m in mutants if m["name"] in want]
    source = (real / a.module).read_text()
    work = Path(tempfile.mkdtemp(prefix="mutsweep-", dir=str(real / "scratch")))
    results = []
    try:
        # the baseline
        tree = work / "baseline"
        build_tree(real, tree)
        rc, failing = run_tests(tree, a.tests, out / "baseline.log")
        print(f"BASELINE exit {rc} failing {failing}", flush=True)
        if rc != 0:
            print("STOP: the baseline does not pass; no mutant is meaningful")
            return 3
        for m in mutants:
            n = source.count(m["old"])
            if n != 1:
                results.append({"name": m["name"], "status": "REFUSED", "why": f"`old` occurs {n} times (need exactly 1)"})
                print(f"REFUSED {m['name']}: old occurs {n} times", flush=True)
                continue
            mutated = source.replace(m["old"], m["new"], 1)
            assert mutated != source, "the mutant changed nothing"
            tree = work / m["name"]
            build_tree(real, tree)
            (tree / a.module).write_text(mutated)
            rc, failing = run_tests(tree, a.tests, out / f"{m['name']}.log")
            caught = rc != 0
            named = any(m["expect"] in t for t in failing)
            status = "CAUGHT-BY-NAMED" if (caught and named) else ("CAUGHT-OTHER" if caught else "SURVIVED")
            results.append({"name": m["name"], "status": status, "exit": rc, "expect": m["expect"], "failing": failing})
            print(f"{status:16s} {m['name']}  (expect {m['expect']}; failing {len(failing)}: {[t.split('.')[-1] for t in failing][:4]})", flush=True)
            shutil.rmtree(tree, ignore_errors=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / "mutsweep.json").write_text(json.dumps({"module": a.module, "tests": a.tests, "results": results}, indent=1) + "\n")
    bad = [r for r in results if r["status"] != "CAUGHT-BY-NAMED"]
    print(f"MUTANTS {len(results)} · caught by the named test {len(results) - len(bad)} · other {len(bad)}", flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
