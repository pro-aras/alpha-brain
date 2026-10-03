#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:56 +0400 — POLLER-FIX G4 (docs/organism/days/PREREG-POLLER-FIX.md §3): the stand-in sweep (#235, #173).
"""stand_in_sweep.py — G4: what stands in for the pollers' reader today is FIXTURES that hand-write a ledger.json (with no manifest, so they now exercise the
LEDGER road, the old code verbatim) and mock.patch stand-ins of run_and_journal / parse_genome. The sweep is the law's command, its output is the CLOSED list,
and the plant is a fake test file in a scratch COPY of tests/ that the sweep must list:

    grep -rlE "voice_loop|canvas_count_of|senses import sit|senses\\.sit|from creature import exam|creature\\.exam|import exam|sit_sense|sit\\.sense|SNAPSHOT\\.json" tests

Default mode: run it on the worktree, print the list (with each file's matching-line count), require it to equal REVIEWED (the eight files the law's author and the
verifier read on 233a4cb, plus the new module, which names these things by design), and require that NO test file but the new module differs from the base
(`git diff --name-only <base> HEAD -- tests`): each listed test must stay green UNMODIFIED, a test that needs an edit is a RAISE.
--plant: copy tests/ to a scratch dir, add a fake test file that matches, sweep the copy: the fake must be LISTED (exit 0 = CAUGHT; 1 = the sweep is blind).
Exit 0 iff all hold; 1 otherwise."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PATTERN = r"voice_loop|canvas_count_of|senses import sit|senses\.sit|from creature import exam|creature\.exam|import exam|sit_sense|sit\.sense|SNAPSHOT\.json"
NEW_MODULE = "tests/creature/test_poller_cursor.py"
REVIEWED = sorted([
    "tests/creature/test_a42_b1.py", "tests/creature/test_alpha4_seams.py", "tests/creature/test_b2_picture_words.py", "tests/creature/test_exam.py",
    "tests/creature/test_exam_one_word.py", "tests/creature/test_g5k_outcome.py", "tests/creature/test_readiness_units.py",
    "tests/creature/test_snapshot_generations.py", NEW_MODULE])


def sweep(root: Path) -> list:
    """The law's command, run in `root` against the directory `tests`."""
    p = subprocess.run(["grep", "-rlE", PATTERN, "tests"], cwd=root, capture_output=True, text=True)
    if p.returncode not in (0, 1):
        raise SystemExit(f"grep failed: {p.stderr}")
    return sorted(l for l in p.stdout.splitlines() if l)


def line_counts(root: Path, files: list) -> dict:
    out = {}
    for f in files:
        p = subprocess.run(["grep", "-cE", PATTERN, f], cwd=root, capture_output=True, text=True)
        out[f] = int(p.stdout.strip() or 0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wt", default=str(Path(__file__).resolve().parents[5]))
    ap.add_argument("--base", default="233a4cb")
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    wt = Path(a.wt).resolve()
    if a.plant:
        tmp = Path(tempfile.mkdtemp(prefix="standin-plant-", dir=None))
        shutil.copytree(wt / "tests", tmp / "tests", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        fake = tmp / "tests" / "creature" / "test_zz_planted_stand_in.py"
        assert not fake.exists(), "the plant's file already exists in the copy"
        baseline = sweep(tmp)
        fake.write_text("from creature import exam\n\n\ndef test_planted():\n    return exam.voice_loop\n")
        assert fake.exists() and "tests/creature/test_zz_planted_stand_in.py" not in baseline
        after = sweep(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        caught = "tests/creature/test_zz_planted_stand_in.py" in after and len(after) == len(baseline) + 1
        print(f"PLANT: baseline {len(baseline)} files, with the planted fake {len(after)}; the fake is {'LISTED (CAUGHT)' if caught else 'NOT listed (the sweep is blind)'}")
        return 0 if caught else 1
    found = sweep(wt)
    counts = line_counts(wt, found)
    print(f"STAND-IN SWEEP on {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=wt, capture_output=True, text=True).stdout.strip()} (the law's grep -rlE over tests): {len(found)} files")
    for f in found:
        print(f"  {counts[f]:3d} matching lines  {f}")
    ok = True
    if found != REVIEWED:
        ok = False
        print("NOT the reviewed closed list: new =", sorted(set(found) - set(REVIEWED)), "missing =", sorted(set(REVIEWED) - set(found)))
    changed = subprocess.run(["git", "diff", "--name-only", a.base, "HEAD", "--", "tests"], cwd=wt, capture_output=True, text=True, check=True).stdout.split()
    print(f"test files differing from {a.base}: {changed}")
    if changed != [NEW_MODULE]:
        ok = False
        print("a listed test file was EDITED (or another file added): a RAISE, not a quiet inclusion")
    print("RESULT:", "OK: the closed list equals the reviewed one and no listed test is modified" if ok else "NOT OK")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
