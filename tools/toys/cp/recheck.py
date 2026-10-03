"""recheck.py — re-run lives whose record carries `toys_tree_dirty = True` and compare them with what is on disk.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:25 +0400 — written for the RESULT's provenance paragraph: 426 stage-1 lives of Toy A were written while
# uncommitted files of ANOTHER toy (tools/toys/nullspace, the lane's Toy B build) sat in the worktree, so their code header says «dirty». The life code of Toy A is
# byte-identical between the launch commit and the end (git diff), and this tool shows the dirty lives are the lives a clean tree makes: it re-runs a sample
# through `run_job` (no file is written) and compares every field but the clock, the code header, the prereg header and the pin (S1c-2's `identity_diff` rule).
# It carries its own PLANT: a stored life compared with the re-run of a DIFFERENT seed's life must differ (a comparer that reads «equal» for that is blind).

  PYTHONPATH=. python3 -m tools.toys.cp.recheck [--n 8]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from brain.scene import run_s1c as S

from tools.toys.common import pools as POOLS
from tools.toys.common import prereg as PR

from . import run as RUN

MASK = ("cpu_s", "wall_s", "code", "prereg", "world", "pin_end")


def differing(a: Mapping[str, object], b: Mapping[str, object]) -> List[str]:
    """The keys (outside MASK) at which two life records differ, compared as canonical JSON."""
    out = []
    for k in sorted(set(a) | set(b)):
        if k in MASK:
            continue
        if json.dumps(a.get(k), sort_keys=True, default=str) != json.dumps(b.get(k), sort_keys=True, default=str):
            out.append(k)
    return out


def dirty_records(root: Path) -> List[Tuple[Path, Dict[str, object]]]:
    out = []
    for f in sorted(root.glob("*/*/*.json")):
        r = json.loads(f.read_text())
        if (r.get("prereg") or {}).get("toys_tree_dirty") is True:
            out.append((f, r))
    return out


def job_of(path: Path) -> "RUN.Job":
    arm_dir, seed, rep = path.parts[-3], int(path.parts[-2]), int(path.stem)
    null = arm_dir.startswith("NULL-")
    return RUN.Job(arm_dir[5:] if null else arm_dir, seed, rep, null)


def main(argv: Sequence[str] = ()) -> int:
    ap = argparse.ArgumentParser(description="re-run dirty-flagged lives and compare them with the records")
    ap.add_argument("--n", type=int, default=8)
    ns = ap.parse_args(list(argv) if argv else None)
    PR.check(RUN.LAW_KEYS)
    recs = dirty_records(RUN.RUNS)
    print(f"records flagged dirty: {len(recs)} of {sum(1 for _ in RUN.RUNS.glob('*/*/*.json'))}")
    # a deterministic sample spread over the arms: every k-th of the arm-sorted list, one arm at most twice
    by_arm: Dict[str, List[Tuple[Path, Dict[str, object]]]] = {}
    for p, r in recs:
        by_arm.setdefault(p.parts[-3], []).append((p, r))
    sample: List[Tuple[Path, Dict[str, object]]] = []
    arms = sorted(by_arm)
    i = 0
    fracs = (0.5, 0.05, 0.95, 0.3, 0.75)                       # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:28 +0400 — the first sample took every arm's MIDDLE record, which were all one seed's; now each pass of the arms uses another position of the list
    while len(sample) < ns.n and any(by_arm.values()):
        a = arms[i % len(arms)]
        if by_arm[a]:
            lst = by_arm[a]
            sample.append(lst.pop(min(len(lst) - 1, int(len(lst) * fracs[(i // len(arms)) % len(fracs)]))))
        i += 1
    test = S.FixedTestSet()
    data_cache: Dict[int, object] = {}
    prereg = {**PR.header(RUN.LAW_KEYS), **RUN.code_header()}
    bad = 0
    redone: Dict[Path, Dict[str, object]] = {}
    for p, stored in sample:
        j = job_of(p)
        if j.seed not in data_cache:
            data_cache[j.seed] = S.RoomData(POOLS.ROOT, j.seed, RUN.ROOMS)
        again = RUN.run_job(j, data_cache[j.seed], test, prereg)
        redone[p] = again
        diff = differing(stored, again)
        print(f"   {p.parts[-3]:18s} seed {j.seed} rep {j.rep:02d}  stored header {(stored['prereg'].get('toys_git_sha') or '')[:8]} dirty {stored['prereg'].get('toys_tree_dirty')}  →  "
              f"{'EQUAL in every field but the masked' if not diff else 'DIFFERENT at ' + ', '.join(diff)}")
        bad += 1 if diff else 0
    # the planted control: a stored life against the re-run of the SAME arm and replicate at ANOTHER seed MUST differ
    # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 12:26 +0400 — the first version looked for another seed inside the sample, and the dirty lives are all of one seed (the lane that ran while Toy B's files were uncommitted), so it crashed on None; the control now runs its own life.
    (p0, s0) = sample[0]
    j0 = job_of(p0)
    other_seed = next(sd for sd in RUN.SEEDS if sd != j0.seed)
    if other_seed not in data_cache:
        data_cache[other_seed] = S.RoomData(POOLS.ROOT, other_seed, RUN.ROOMS)
    wrong = RUN.run_job(RUN.Job(j0.arm, other_seed, j0.rep, j0.null), data_cache[other_seed], test, prereg)
    control = differing(s0, wrong)
    print(f"PLANT: {p0.parts[-3]} seed {j0.seed} rep {j0.rep:02d} against the re-run of the same arm and replicate at seed {other_seed}: "
          f"{'CAUGHT (differs at ' + ', '.join(control[:4]) + ')' if control else 'MISSED — the comparer is blind'}")
    ok = (bad == 0) and bool(control)
    print(f"RECHECK: {'ALL EQUAL, control caught' if ok else 'FAILED'} · {len(sample)} lives re-run, {bad} differ")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
