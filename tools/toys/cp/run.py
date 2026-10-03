"""run.py — TOY A's runs: the job list (stage 1), resumable workers, the lane launcher, the G2 identity gate, the G5 price.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:34 +0400 — new module, written to docs/research/toys/PREREG-TOY-CP.md §2, §6 and
# PREREG-TOY-CP-AMEND-1.md §3, §5. Every command except `status` first checks the signed texts (tools/toys/common/prereg.py): a run REFUSES on a text that
# differs from the co-signed one. Heavy work goes through /data/dev/swarm/bin/slot (the `launch` lanes and the gates' own commands are run under it).

  PYTHONPATH=. python3 -m tools.toys.cp.run life --arm L-own-last2 --seed 20261301 --rep 0 [--null]   one life -> scratch/toys-cp/runs/...
  PYTHONPATH=. python3 -m tools.toys.cp.run work --share I --of N [--stage 1]                          a worker: its share of the seeds, resumable
  PYTHONPATH=. python3 -m tools.toys.cp.run launch --lanes 3 [--stage 1]                               N workers, each under `slot toys cp-wI`
  PYTHONPATH=. python3 -m tools.toys.cp.run gate-g2                                                    G2: my life vs S1c's records at seeds 01-03 (+ ORACLE)
  PYTHONPATH=. python3 -m tools.toys.cp.run price                                                      G5: one life of each kind, CPU-seconds
  PYTHONPATH=. python3 -m tools.toys.cp.run status                                                     the records on disk against the job list
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from brain.scene import pickers as PK
from brain.scene import run as R
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2

from tools.toys.common import pools as POOLS
from tools.toys.common import prereg as PR

from . import estimators as ES
from . import life as LF

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "scratch" / "toys-cp"
RUNS = ROOT / "runs"
GATE = ROOT / "gate"
LOGS = ROOT / "logs"
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])
SEEDS: Tuple[int, ...] = POOLS.ALL_SEEDS
GATE_SEEDS: Tuple[int, ...] = (20261301, 20261302, 20261303)
LAW_KEYS = ["cp", "cp_amend1"]
SLOT = "/data/dev/swarm/bin/slot"
REPS = 10                      # replicates of every ε-greedy arm per seed
BAND = 20                      # RANDOM's and R-ONLY's lives per seed


@dataclass(frozen=True)
class Job:
    arm: str
    seed: int
    rep: int
    null: bool = False

    @property
    def name(self) -> str:
        return f"NULL-{self.arm}" if self.null else self.arm

    @property
    def path(self) -> Path:
        return RUNS / self.name / str(self.seed) / f"{self.rep:02d}.json"


def stage1_jobs(seeds: Sequence[int] = SEEDS) -> List[Job]:
    jobs: List[Job] = []
    for s in seeds:
        jobs += [Job("RANDOM", s, k) for k in range(1, BAND + 1)]
        jobs += [Job("R-ONLY", s, k) for k in range(1, BAND + 1)]
        jobs += [Job("N-ONLY", s, 0)]
        jobs += [Job("ERROR", s, r) for r in range(REPS)]
        jobs += [Job(c, s, r) for c in ES.CELLS for r in range(REPS)]
        jobs += [Job("LP-OUDEYER", s, r) for r in range(REPS)]
        jobs += [Job("ORACLE", s, 0)]
    return jobs


def stage2_jobs(arms: Sequence[str], seeds: Sequence[int] = SEEDS) -> List[Job]:
    return [Job(a, s, r, null=True) for s in seeds for a in arms for r in range(REPS)]


def run_job(job: Job, data, test, prereg: Dict[str, str]) -> Dict[str, object]:
    rooms = list(ROOMS)
    if job.arm == "ORACLE":
        out = S.life(data, test, "ORACLE", rooms)               # S1c's own function: the greedy one-block lookahead, a reference
        out["prereg"] = dict(prereg)
        out["extra"] = {"arm": "ORACLE", "rep": 0}
        return out
    picker = ES.make_arm(job.arm, rooms, job.seed, job.rep, null=job.null)
    prefix = PK.band_prefix(job.seed, job.rep) if job.arm == "RANDOM" else ""
    label = f"NULL:{job.arm}" if job.null else job.arm
    return LF.life_cp(data, test, picker, label, rooms, prefix=prefix, decompose=(job.arm == "RANDOM"), rep=job.rep, prereg=prereg)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=R._jsonable))
    tmp.rename(path)


def code_header() -> Dict[str, object]:
    """Which commit of the toy produced a record, and whether the toy's own files differed from it (a dirty tree is recorded, not hidden).
    edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:40 +0400 — added before the stage-1 unit."""
    def git(*a: str) -> str:
        return subprocess.check_output(["git", *a], cwd=REPO, text=True).strip()
    try:
        dirty = git("status", "--porcelain", "--", "tools/toys", "tests/tools", "docs/research/toys")
        return {"toys_git_sha": git("rev-parse", "HEAD"), "toys_tree_dirty": bool(dirty)}
    except (subprocess.CalledProcessError, OSError):
        return {"toys_git_sha": None, "toys_tree_dirty": None}


def work(share: int, of: int, jobs: Sequence[Job], log=print) -> int:
    prereg = {**PR.header(LAW_KEYS), **code_header()}
    by_seed: Dict[int, List[Job]] = {}
    for j in jobs:
        by_seed.setdefault(j.seed, []).append(j)
    seeds = sorted(by_seed)[share::of]
    test = S.FixedTestSet()
    n_done = n_skip = 0
    for s in seeds:
        todo = [j for j in by_seed[s] if not j.path.exists()]
        n_skip += len(by_seed[s]) - len(todo)
        if not todo:
            continue
        data = S.RoomData(POOLS.ROOT, s, ROOMS)
        t0 = time.time()
        for j in todo:
            out = run_job(j, data, test, prereg)
            write_json(j.path, out)
            n_done += 1
        log(f"[work {share}/{of}] seed {s}: {len(todo)} lives in {time.time() - t0:.0f} s wall (skipped {len(by_seed[s]) - len(todo)})")
    log(f"[work {share}/{of}] done: {n_done} lives written, {n_skip} already on disk")
    return 0


def launch(lanes: int, stage: int, arms: str = "") -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": ".", "TMPDIR": str(REPO / "scratch" / "tmp")}
    procs = []
    for i in range(lanes):
        cmd = [SLOT, "toys", f"cp-w{i}", "--", sys.executable, "-B", "-u", "-m", "tools.toys.cp.run", "work", "--share", str(i), "--of", str(lanes),
               "--stage", str(stage)] + (["--arms", arms] if arms else [])
        f = open(LOGS / f"work-{i}.log", "a")
        procs.append((subprocess.Popen(cmd, cwd=REPO, env=env, stdout=f, stderr=subprocess.STDOUT), f))
    codes = [p.wait() for p, _f in procs]
    for _p, f in procs:
        f.close()
    print(f"launch: {lanes} lanes finished, exit codes {codes}")
    return 0 if all(c == 0 for c in codes) else 1


# ================================================================================================ G2: the identity gate
def _s1c_record(name: str, seed: int, k: Optional[int] = None) -> Dict[str, object]:
    base = S.ROOT / str(seed)
    p = (base / "band" / "law" / f"random-{k:02d}.json") if name == "RANDOM" else (base / "runs" / "law" / f"{name}.json")
    return json.loads(p.read_text())


def gate_g2(log=print) -> bool:
    """G2 (PREREG §6, AMEND-1 §3): this toy's life — and S1c's own ORACLE through S1c's own function — on the redrawn pools reproduces S1c's records at seeds
    20261301–03: RANDOM's 20 band lives, ERROR, PROGRESS (= L-own-last2 replicate 0), NULL (the credit derangement), ORACLE; every field but the masked five."""
    test = S.FixedTestSet()
    rooms = list(ROOMS)
    rows: List[Tuple[str, bool, str]] = []
    for s in GATE_SEEDS:
        data = S.RoomData(POOLS.ROOT, s, rooms)
        pi = PK.null_derangement(s, rooms)
        cases: List[Tuple[str, object, Dict[str, object]]] = []
        for k in range(1, BAND + 1):
            cases.append((f"RANDOM band {k:02d}", LF.life_cp(data, test, ES.make_arm("RANDOM", rooms, s, k), "RANDOM", rooms, prefix=PK.band_prefix(s, k)),
                          _s1c_record("RANDOM", s, k)))
        cases.append(("ERROR", LF.life_cp(data, test, ES.make_arm("ERROR", rooms, s, 0), "ERROR", rooms), _s1c_record("ERROR", s)))
        cases.append(("PROGRESS (= L-own-last2)", LF.life_cp(data, test, ES.make_arm("L-own-last2", rooms, s, 0), "PROGRESS", rooms), _s1c_record("PROGRESS", s)))
        cases.append(("NULL (credit derangement)", LF.life_cp(data, test, ES.CellPicker(rooms, s, "L", "own", "last2", credit=pi), "NULL", rooms), _s1c_record("NULL", s)))
        cases.append(("ORACLE", S.life(data, test, "ORACLE", rooms), _s1c_record("ORACLE", s)))
        for name, new, old in cases:
            diff = S2.identity_diff(new, old)
            rows.append((f"{s} {name}", not diff, ",".join(diff)))
        log(f"G2 seed {s}: {sum(1 for r in rows if r[0].startswith(str(s)) and r[1])} of {sum(1 for r in rows if r[0].startswith(str(s)))} EQUAL")
    bad = [r for r in rows if not r[1]]
    for r in bad:
        log(f"  DIFFERENT: {r[0]} — fields {r[2]}")
    log(f"G2: {len(rows) - len(bad)} of {len(rows)} lives EQUAL to S1c's records (every field but the masked five)")
    return not bad


# ================================================================================================ G5: the price
def price(log=print) -> Dict[str, float]:
    test = S.FixedTestSet()
    rooms = list(ROOMS)
    seed = 20261301
    data = S.RoomData(POOLS.ROOT, seed, rooms)
    prereg = PR.header(LAW_KEYS)
    out: Dict[str, float] = {}
    try:
        load = os.getloadavg()
    except OSError:
        load = (float("nan"),) * 3
    log(f"G5 price, solo lives at seed {seed}; box load {load[0]:.2f} {load[1]:.2f} {load[2]:.2f} (a CPU-second here is inflated by what else runs, #243 (5))")
    for arm, rep in (("RANDOM", 1), ("R-ONLY", 1), ("N-ONLY", 0), ("ERROR", 0), ("L-own-last2", 0), ("L-hist-ema", 0), ("C-own-last2", 0),
                     ("C-hist-ema", 0), ("LP-OUDEYER", 0), ("ORACLE", 0)):
        j = Job(arm, seed, rep)
        t0 = time.process_time()
        run_job(j, data, test, prereg)
        out[arm] = time.process_time() - t0
        log(f"   {arm:12s} {out[arm]:7.2f} CPU-s" + (" (with the drop's anatomy)" if arm == "RANDOM" else ""))
    jobs = stage1_jobs()
    per = {a: out.get(a, out["L-own-last2"]) for a in {j.arm for j in jobs}}
    total = sum(per[j.arm] if j.arm != "RANDOM" else out["RANDOM"] for j in jobs)
    log(f"G5: stage 1 = {len(jobs)} lives ≈ {total / 60:.1f} CPU-min at these prices (the PREREG estimated 45-55 + 5 for the ORACLE)")
    return out


def status() -> None:
    jobs = stage1_jobs()
    have = sum(1 for j in jobs if j.path.exists())
    print(f"stage 1: {have} of {len(jobs)} lives on disk")
    for arm in sorted({j.arm for j in jobs}):
        a = [j for j in jobs if j.arm == arm]
        print(f"   {arm:12s} {sum(1 for j in a if j.path.exists()):4d} of {len(a)}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("life")
    a.add_argument("--arm", required=True)
    a.add_argument("--seed", type=int, required=True)
    a.add_argument("--rep", type=int, default=0)
    a.add_argument("--null", action="store_true")
    w = sub.add_parser("work")
    w.add_argument("--share", type=int, required=True)
    w.add_argument("--of", type=int, required=True)
    w.add_argument("--stage", type=int, default=1)
    w.add_argument("--arms", default="", help="stage 2: comma-separated arms whose NULL runs")
    l = sub.add_parser("launch")
    l.add_argument("--lanes", type=int, default=3)
    l.add_argument("--stage", type=int, default=1)
    l.add_argument("--arms", default="", help="stage 2: comma-separated arms whose NULL runs")
    sub.add_parser("gate-g2")
    sub.add_parser("price")
    sub.add_parser("status")
    ns = ap.parse_args(argv)
    if ns.cmd == "status":
        status()
        return 0
    PR.check(LAW_KEYS)
    if ns.cmd == "life":
        job = Job(ns.arm, ns.seed, ns.rep, ns.null)
        out = run_job(job, S.RoomData(POOLS.ROOT, ns.seed, ROOMS), S.FixedTestSet(), {**PR.header(LAW_KEYS), **code_header()})
        write_json(job.path, out)
        print(f"{job.path}: A {out['marks']['A']:.4f} · SHARE_N {out['marks']['share']['N']:.3f} · CPU {out['cpu_s']:.2f} s")
        return 0
    if ns.cmd == "work":
        jobs = stage1_jobs() if ns.stage == 1 else stage2_jobs([x for x in ns.arms.split(",") if x])
        return work(ns.share, ns.of, jobs)
    if ns.cmd == "launch":
        return launch(ns.lanes, ns.stage, ns.arms)
    if ns.cmd == "gate-g2":
        return 0 if gate_g2() else 1
    if ns.cmd == "price":
        price()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
