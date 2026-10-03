"""run.py — TOY B's runs: the job list (87 lives a seed, ten seeds), resumable workers, the slot-gated lane launcher, the G2 identity gate with T-MEM-1's BASE record, G4
(the pre-pass rows equal a learner's), the G5 price.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:47 +0400 — new module, written to docs/research/toys/PREREG-TOY-NULLSPACE.md §1, §4, §6 (text co-signed
# 2026-10-03 11:24 +0400, sha256 d15a6353…). Every command except `status` first checks the signed text (tools/toys/common/prereg.py): a run REFUSES on a text that
# differs from the co-signed one. Heavy work goes through /data/dev/swarm/bin/slot (the `launch` lanes and the gates' own commands are run under it).

  PYTHONPATH=. python3 -m tools.toys.nullspace.run life --arm OWM@0.01 --seed 20261301 [--rep K]     one life -> scratch/toys-ns/runs/...
  PYTHONPATH=. python3 -m tools.toys.nullspace.run work --share I --of N                              a worker: its share of the seeds, resumable, parents before SHRINK
  PYTHONPATH=. python3 -m tools.toys.nullspace.run launch --lanes 2                                   N workers, each under `slot toys ns-wI`
  PYTHONPATH=. python3 -m tools.toys.nullspace.run gate-g2                                            G2 (PLAIN == T-MEM-1's BASE) and G4 (pre-pass rows == a learner's), seeds 01-03
  PYTHONPATH=. python3 -m tools.toys.nullspace.run price                                              G5: one life of each kind, CPU-seconds
  PYTHONPATH=. python3 -m tools.toys.nullspace.run status                                             the records on disk against the job list

ARM NAMES (job.arm): PLAIN · OWM@tau · NSCL@tau · ROT@tau (rep k = 1..10) · RANDRANK@tau (rep k) · SHRINK-OWM@tau · SHRINK-NSCL@tau · STD-ONLY@j · FREEZE-OLD@j · LRSHRINK@s
· OWM-NB@0.01 · OWM-RESTD@0.01 · OWM-BM@0.01 · OWM-OLDONLY@0.01 · ANTI-OWM@0.01.
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

import numpy as np

from brain.scene import run as R
from brain.scene import run_s1c as S
from brain.scene import run_s1c2 as S2
from brain.scene import run_tmem1 as T1

from tools.toys.common import pools as POOLS
from tools.toys.common import prereg as PR

from . import life as NL
from . import projector as NP

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "scratch" / "toys-ns"
RUNS = ROOT / "runs"
LOGS = ROOT / "logs"
SEEDS: Tuple[int, ...] = POOLS.ALL_SEEDS
GATE_SEEDS: Tuple[int, ...] = (20261301, 20261302, 20261303)
LAW_KEYS = ["nullspace"]
SLOT = "/data/dev/swarm/bin/slot"
TMEM1_ROOT = Path("/data/dev/brain-runs/scene-tmem1")
TAUS = NP.TAUS
HEADLINE = 0.01
DRAWS = 10
LR_SCALES = (0.5, 0.25, 0.125)


def tau_name(tau: float) -> str:
    return f"{tau:g}"


@dataclass(frozen=True)
class Job:
    arm: str
    seed: int
    rep: int = 0

    @property
    def path(self) -> Path:
        return RUNS / self.arm / str(self.seed) / f"{self.rep:02d}.json"


def seed_jobs(seed: int) -> List[Job]:
    """One seed's 87 lives, parents (OWM, NSCL) before their SHRINK children."""
    J = [Job("PLAIN", seed)]
    J += [Job(f"STD-ONLY@{j}", seed) for j in (1, 2, 3)]
    J += [Job(f"FREEZE-OLD@{j}", seed) for j in (1, 2, 3)]
    J += [Job(f"OWM@{tau_name(t)}", seed) for t in TAUS]
    J += [Job(f"NSCL@{tau_name(t)}", seed) for t in TAUS]
    J += [Job(f"SHRINK-OWM@{tau_name(t)}", seed) for t in TAUS]
    J += [Job(f"SHRINK-NSCL@{tau_name(t)}", seed) for t in TAUS]
    J += [Job(f"ROT@{tau_name(t)}", seed, k) for t in TAUS for k in range(1, DRAWS + 1)]
    J += [Job(f"RANDRANK@{tau_name(t)}", seed, k) for t in TAUS for k in range(1, DRAWS + 1)]
    J += [Job(f"LRSHRINK@{s:g}", seed) for s in LR_SCALES]
    h = tau_name(HEADLINE)
    J += [Job(f"OWM-NB@{h}", seed), Job(f"OWM-RESTD@{h}", seed), Job(f"OWM-BM@{h}", seed), Job(f"OWM-OLDONLY@{h}", seed), Job(f"ANTI-OWM@{h}", seed)]
    return J


def stage1_jobs(seeds: Sequence[int] = SEEDS) -> List[Job]:
    return [j for s in seeds for j in seed_jobs(s)]


class LrArm(NP.PlainArm):
    """LRSHRINK: the unprojected learner at lr x s (the life passes project=None)."""

    def __init__(self, s: float):
        super().__init__()
        self.lr_scale = float(s)
        self.name = f"LRSHRINK@{s:g}"


def parent_rho(arm: str, seed: int) -> Dict[int, float]:
    kind, tau = arm.split("@")
    parent = Job(f"{kind.split('-', 1)[1]}@{tau}", seed)          # SHRINK-OWM@t -> OWM@t, SHRINK-NSCL@t -> NSCL@t
    if not parent.path.exists():
        raise FileNotFoundError(f"{arm} needs its parent's record {parent.path}")
    return {int(k): float(v) for k, v in json.loads(parent.path.read_text())["extra"]["rho"].items()}


def make_arm(job: Job, proj: NP.Projectors) -> NP.Arm:
    name, _, spec = job.arm.partition("@")
    if name == "PLAIN":
        return NP.PlainArm()
    if name == "STD-ONLY":
        return NP.FreezeArm(int(spec), False)
    if name == "FREEZE-OLD":
        return NP.FreezeArm(int(spec), True)
    if name == "LRSHRINK":
        return LrArm(float(spec))
    tau = float(spec)
    if name == "OWM":
        return NP.OwmArm(proj.owm(tau))
    if name == "NSCL":
        return NP.OwmArm(proj.nscl(tau)[0])
    if name == "ROT":
        return NP.OwmArm(proj.rot(tau, job.rep))
    if name == "RANDRANK":
        return NP.OwmArm(proj.rank(tau, job.rep))
    if name in ("SHRINK-OWM", "SHRINK-NSCL"):
        return NP.ScaleArm(parent_rho(job.arm, job.seed))
    if name == "OWM-NB":
        return NP.NbArm(proj.nb(tau))
    if name == "OWM-RESTD":
        return NP.RestdArm(proj, tau)
    if name == "OWM-BM":
        return NP.OwmArm(proj.bm(tau))
    if name == "OWM-OLDONLY":
        return NP.OldOnlyArm(proj.owm(tau))
    if name == "ANTI-OWM":
        return NP.OwmArm(NP.anti_all(proj.owm(tau)))
    raise ValueError(f"no such arm: {job.arm!r}")


def run_job(job: Job, data, test, proj: NP.Projectors, prereg: Dict[str, str]) -> Dict[str, object]:
    out = NL.life_ns(data, test, make_arm(job, proj), job.arm, rep=job.rep, prereg=prereg)
    name, _, spec = job.arm.partition("@")
    if spec and name in ("OWM", "NSCL", "ROT", "RANDRANK", "OWM-NB", "OWM-RESTD", "OWM-BM", "OWM-OLDONLY", "ANTI-OWM"):
        tau = float(spec)
        out["extra"]["alpha"] = proj.alpha(tau)
        out["extra"]["capacity"] = {str(j): proj.capacity(tau, j) for j in (1, 2, 3)}      # OWM's trace(I - P_j) after rooms 1..j
        out["extra"]["nscl_dims"] = {str(j): d for j, d in proj.nscl(tau)[1].items()}      # NSCL's null dimension d_j after rooms 1..j
    return out


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=R._jsonable))
    tmp.rename(path)


def code_header() -> Dict[str, object]:
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
    test = T1.TestSetM()
    n_done = n_skip = 0
    for s in seeds:
        todo = [j for j in by_seed[s] if not j.path.exists()]
        n_skip += len(by_seed[s]) - len(todo)
        if not todo:
            continue
        data = S.RoomData(POOLS.ROOT, s, list(NP.ROOMS))
        proj = NP.Projectors(data, s)
        t0 = time.time()
        for j in todo:
            write_json(j.path, run_job(j, data, test, proj, prereg))
            n_done += 1
        log(f"[work {share}/{of}] seed {s}: {len(todo)} lives in {time.time() - t0:.0f} s wall (skipped {len(by_seed[s]) - len(todo)})")
    log(f"[work {share}/{of}] done: {n_done} lives written, {n_skip} already on disk")
    return 0


def launch(lanes: int) -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": ".", "TMPDIR": str(REPO / "scratch" / "tmp")}
    procs = []
    for i in range(lanes):
        cmd = [SLOT, "toys", f"ns-w{i}", "--", sys.executable, "-B", "-u", "-m", "tools.toys.nullspace.run", "work", "--share", str(i), "--of", str(lanes)]
        f = open(LOGS / f"work-{i}.log", "a")
        procs.append((subprocess.Popen(cmd, cwd=REPO, env=env, stdout=f, stderr=subprocess.STDOUT), f))
    codes = [p.wait() for p, _f in procs]
    for _p, f in procs:
        f.close()
    print(f"launch: {lanes} lanes finished, exit codes {codes}")
    return 0 if all(c == 0 for c in codes) else 1


# ================================================================================================ G2 and G4
def gate_g2(log=print) -> bool:
    """G2: this toy's PLAIN life reproduces T-MEM-1's BASE / seq record at seeds 20261301–03 (rates_rw, pairs, table, first_meet, every row). G4: the pre-pass rows
    equal the rows a learner receives (a full unhooked life), to 1e-12."""
    test = T1.TestSetM()
    ok = True
    for s in GATE_SEEDS:
        data = S.RoomData(POOLS.ROOT, s, list(NP.ROOMS))
        old = json.loads((TMEM1_ROOT / str(s) / "runs" / "seq" / "BASE.json").read_text())
        new = NL.life_ns(data, test, NP.PlainArm(), "PLAIN")
        cols = ("block", "room", "flag", "start", "L", "drop", "wl")
        eq = {k: S2._canon(new[k]) == S2._canon(old[k]) for k in ("rates_rw", "pairs", "table", "first_meet")}
        eq["record rows"] = len(new["record"]) == len(old["record"]) and all(
            S2._canon({c: x[c] for c in cols}) == S2._canon({c: y[c] for c in cols}) for x, y in zip(new["record"], old["record"]))
        proj = NP.Projectors(data, s)
        got = NL.learner_rows(data)
        dev = max(float(np.abs(got[r] - proj.rows[r]).max()) for r in NP.ROOMS)
        eq["G4 pre-pass rows == a learner's (max abs difference %.1e)" % dev] = dev < 1e-12
        for k, v in eq.items():
            log(f"G2/G4 seed {s}: {k:60s} {'EQUAL' if v else 'DIFFERENT'}")
        ok &= all(eq.values())
    log(f"G2/G4: {'ALL EQUAL' if ok else 'A MISS — STOP'}")
    return ok


def price(log=print) -> Dict[str, float]:
    test = T1.TestSetM()
    seed = 20261301
    data = S.RoomData(POOLS.ROOT, seed, list(NP.ROOMS))
    proj = NP.Projectors(data, seed)
    prereg = PR.header(LAW_KEYS)
    try:
        load = os.getloadavg()
    except OSError:
        load = (float("nan"),) * 3
    log(f"G5 price, solo lives at seed {seed}; box load {load[0]:.2f} {load[1]:.2f} {load[2]:.2f} (a CPU-second here is inflated by what else runs, #243 (5))")
    out: Dict[str, float] = {}
    h = tau_name(HEADLINE)
    t0 = time.process_time()
    NP.Projectors(data, seed)
    out["pre-pass"] = time.process_time() - t0
    log(f"   {'pre-pass (rows, Grams)':26s} {out['pre-pass']:7.2f} CPU-s a seed")
    order = ["PLAIN", f"OWM@{h}", f"NSCL@{h}", f"ROT@{h}", f"RANDRANK@{h}", f"SHRINK-OWM@{h}", "STD-ONLY@2", "FREEZE-OLD@2", "LRSHRINK@0.5",
             f"OWM-NB@{h}", f"OWM-RESTD@{h}", f"OWM-BM@{h}", f"OWM-OLDONLY@{h}", f"ANTI-OWM@{h}"]
    for arm in order:
        job = Job(arm, seed, 1 if arm.startswith(("ROT", "RANDRANK")) else 0)
        if arm.startswith("SHRINK") and not Job(f"OWM@{h}", seed).path.exists():
            write_json(Job(f"OWM@{h}", seed).path, run_job(Job(f"OWM@{h}", seed), data, test, proj, prereg))
        t0 = time.process_time()
        run_job(job, data, test, proj, prereg)
        out[arm] = time.process_time() - t0
        log(f"   {arm:26s} {out[arm]:7.2f} CPU-s")
    jobs = stage1_jobs()
    def cost(a: str) -> float:
        base = a.split("@")[0]
        for k in out:
            if k.split("@")[0] == base:
                return out[k]
        return out["PLAIN"]
    total = sum(cost(j.arm) for j in jobs) + len(SEEDS) * out["pre-pass"]
    log(f"G5: stage 1 = {len(jobs)} lives ≈ {total / 60:.1f} CPU-min at these prices (the PREREG estimated ≈ 33)")
    return out


def status() -> None:
    jobs = stage1_jobs()
    have = sum(1 for j in jobs if j.path.exists())
    print(f"stage 1: {have} of {len(jobs)} lives on disk")
    kinds: Dict[str, List[Job]] = {}
    for j in jobs:
        kinds.setdefault(j.arm.split("@")[0], []).append(j)
    for k, a in sorted(kinds.items()):
        print(f"   {k:12s} {sum(1 for j in a if j.path.exists()):4d} of {len(a)}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("life")
    a.add_argument("--arm", required=True)
    a.add_argument("--seed", type=int, required=True)
    a.add_argument("--rep", type=int, default=0)
    w = sub.add_parser("work")
    w.add_argument("--share", type=int, required=True)
    w.add_argument("--of", type=int, required=True)
    l = sub.add_parser("launch")
    l.add_argument("--lanes", type=int, default=2)
    sub.add_parser("gate-g2")
    sub.add_parser("price")
    sub.add_parser("status")
    ns = ap.parse_args(argv)
    if ns.cmd == "status":
        status()
        return 0
    PR.check(LAW_KEYS)
    if ns.cmd == "life":
        data = S.RoomData(POOLS.ROOT, ns.seed, list(NP.ROOMS))
        job = Job(ns.arm, ns.seed, ns.rep)
        out = run_job(job, data, T1.TestSetM(), NP.Projectors(data, ns.seed), {**PR.header(LAW_KEYS), **code_header()})
        write_json(job.path, out)
        print(f"{job.path}: CPU {out['cpu_s']:.2f} s")
        return 0
    if ns.cmd == "work":
        return work(ns.share, ns.of, stage1_jobs())
    if ns.cmd == "launch":
        return launch(ns.lanes)
    if ns.cmd == "gate-g2":
        return 0 if gate_g2() else 1
    if ns.cmd == "price":
        price()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
