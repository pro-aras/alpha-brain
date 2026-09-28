"""d_projection.py — the PRE-REGISTERED projection check on the rule library's searches (B1-PREREG §12, 2026-09-26).

edit: Claude (Opus 5.5), 2026-09-26 17:24 +0400 — D's number (tools/b1/d_budget.py → docs/brain/b1/stage-1/d-budget.json)
is set from prices measured at 50,000 candidates per sleep and a depth factor measured at ONE sleep; no probe measured
deep programs and late-sleep data together. This reads each running search's own cost.jsonl (the arm's milliseconds at
every SLEEP) and compares the cumulative cost with the budget file's `predicted_cum_cpu_s` at the same sleep.

The rule, declared before the runs: at every completed sleep k ≥ 4 of any search, r_k = actual ÷ predicted and the
projected total = r_k × the predicted total. If a projected total exceeds 24 CPU-hours, this EXITS 10 naming the search:
the seat stops that seed's searches (the records are kept, never deleted), re-prices with the measured r_k, and relaunches.
It also EXITS 0 at a checkpoint sleep (default 7, the first expensive one) so the seat reads the ratios once by hand.
It never touches a process. The poll reads files only. `arm_ms` is WALL time inside the arm: before anything stops, a
FIRE is confirmed against the search process's own CPU time (`ps -o cputime`), which is what the allowance counts —
a burst of other work beside the searches inflates wall, not CPU.

edit: Claude (Opus 5.5), 2026-09-26 18:22 +0400 — R41: the READING SOURCE changed; the rule above did not. The first version
read each search's cost.jsonl. run.py's _Writer writes it through Python's default buffer, which is 131,072 bytes under
the venv's Python 3.14, and a whole run's cost.jsonl is about 5 KB, so the file stays EMPTY until the run closes it about
19 h later. The check armed at 17:50 could never have fired: at 18:1x it read 0 sleeps on all four searches, each
≈ 25 CPU-minutes in. It now reads:
  * WHEN sleep k closed: the mtime of the arm's own `arm/library/sleep-<k>.json`, written and closed inside the sleep
    (brain/arms/library/arm.py _after_sleep). A sleep counts only once `library_log.jsonl` carries its record, which is
    written after the snapshot, so a snapshot caught mid-write is never read.
  * WHAT it cost: the search process's CPU clock (/proc/<pid>/stat utime + stime), sampled at every poll and
    interpolated at that mtime. Before the first sample it is elapsed × the life's CPU/wall ratio. This is the CPU the
    allowance counts, so a FIRE needs no second confirmation.
  * A strict strengthening: while sleep k is still running, the CPU spent so far is a LOWER bound on the cumulative
    cost at sleep k. If even that projects past 24 CPU-h, the check fires early. It can fire early but never wrongly.
It prints a heartbeat with its control counts (pid, state, CPU, sleeps closed) every --beat seconds. It EXITS 11 when a
search process is gone before its last sleep: a monitor must say when its subject died. `--record <run-dir>` reads a
FINISHED run, the positive control: the snapshot mtimes must reproduce cost.jsonl's own sleep clock.

`python3 -m tools.b1.d_projection --budget docs/brain/b1/stage-1/d-budget.json --run-dir <runs/seed/D> [--run-dir …] [--checkpoint 7]`
`python3 -m tools.b1.d_projection --record <a finished run's arm dir, e.g. runs/20261001.toy-d/D>`
"""
# edit: Claude (Opus 5.5), 2026-09-27 00:15 +0400 — a process found gone is beaten as GONE (since, last CPU, sleeps closed, «finished» when every sleep closed), never as its last live poll: the r1 watch printed «R · CPU 0.580 h» for 45 min after seed 2's D exited.
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

LIMIT_S = 24 * 3600
TICK = os.sysconf("SC_CLK_TCK")


def _btime() -> float:
    for line in Path("/proc/stat").read_text().splitlines():
        if line.startswith("btime "):
            return float(line.split()[1])
    raise RuntimeError("no btime in /proc/stat")


def proc_times(pid: int) -> Optional[Tuple[float, float, str]]:
    """(start epoch s, CPU s = utime + stime, state letter) of a live process; None once it is gone."""
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    rest = raw[raw.rindex(")") + 2:].split()     # rest[0] is field 3 (state); field n is rest[n - 3]
    return _btime() + int(rest[19]) / TICK, (int(rest[11]) + int(rest[12])) / TICK, rest[0]


def find_pid(run_dir: Path) -> Optional[int]:
    """The `brain.harness.run` process whose --out / --arms name this run dir (run.py arm_dirname: ':' → '_')."""
    want = run_dir.resolve()
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = [a.decode("utf-8", "replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
        except OSError:
            continue
        if "brain.harness.run" not in argv or "--out" not in argv or "--arms" not in argv:
            continue
        try:
            out, arms = argv[argv.index("--out") + 1], argv[argv.index("--arms") + 1]
        except IndexError:
            continue
        if (Path(out) / arms.replace(":", "_")).resolve() == want:
            return int(d.name)
    return None


def closed_sleeps(run_dir: Path) -> List[Tuple[int, float]]:
    """[(k, mtime of sleep-k.json)] for every sleep the arm has CLOSED: its snapshot exists AND library_log.jsonl
    carries its record (written after the snapshot). In k order, 1, 2, … without gaps."""
    logp = run_dir / "arm" / "library_log.jsonl"
    logged = set()
    if logp.exists():
        for line in logp.read_text(errors="replace").splitlines():
            try:
                logged.add(int(json.loads(line)["sleep"]))
            except (ValueError, KeyError, TypeError):
                continue                        # a line being written
    out, k = [], 1
    lib = run_dir / "arm" / "library"
    while k in logged and (lib / f"sleep-{k}.json").exists():
        out.append((k, (lib / f"sleep-{k}.json").stat().st_mtime))
        k += 1
    return out


@dataclass
class Search:
    run_dir: Path
    pid: Optional[int]
    start: Optional[float] = None
    samples: List[Tuple[float, float]] = field(default_factory=list)   # (epoch s, CPU s) at each poll
    seen: set = field(default_factory=set)
    last: Optional[Tuple[float, str]] = None                          # (CPU s, state) at the latest poll
    gone_at: Optional[float] = None                                   # the first poll that found the process gone

    @property
    def label(self) -> str:
        return f"{self.run_dir.parent.name}/{self.run_dir.name}"

    def cpu_at(self, t: float) -> Tuple[float, str]:
        """CPU seconds at epoch t: interpolated between polls, or elapsed × the life's CPU/wall ratio before the first."""
        s = self.samples
        if s and t >= s[0][0]:
            for (t0, c0), (t1, c1) in zip(s, s[1:]):
                if t0 <= t <= t1:
                    return c0 + (c1 - c0) * ((t - t0) / (t1 - t0) if t1 > t0 else 0.0), "interp"
            return s[-1][1], "last-poll"
        t0, c0 = s[0]
        ratio = c0 / (t0 - self.start) if t0 > self.start else 1.0
        return max(0.0, t - self.start) * ratio, f"ratio {ratio:.3f}"


def poll(budget: dict, searches: List[Search], checkpoint: int, now: float,
         procs: Callable[[int], Optional[Tuple[float, float, str]]] = proc_times):
    """One poll: (lines, fire, reached, dead). `procs` is injectable so the tests plant a clock."""
    pred = {int(k): float(v) for k, v in budget["predicted_cum_cpu_s"].items()}
    total = float(budget["predicted_total_cpu_h"]) * 3600.0
    last_sleep = max(pred)
    lines, fire, reached, dead = [], None, [], []
    for s in searches:
        pt = procs(s.pid) if s.pid is not None else None
        if pt is not None:
            s.start = pt[0]
            s.samples.append((now, pt[1]))
            s.last = (pt[1], pt[2])
        elif s.pid is not None and s.gone_at is None:
            s.gone_at = now                     # a gone process is never beaten as its last live poll
        closed = closed_sleeps(s.run_dir)
        for k, mt in closed:
            if k in s.seen:
                continue
            if s.start is None or not s.samples:
                break                           # no clock yet for this search; read it at the next poll
            s.seen.add(k)
            act, how = s.cpu_at(mt)
            if k not in pred:
                lines.append(f"{time.strftime('%H:%M:%S', time.localtime(now))} {s.label} sleep {k} closed "
                             f"{time.strftime('%H:%M:%S', time.localtime(mt))}: actual {act / 3600:.3f} h ({how}) "
                             f"· no prediction at this sleep")
                continue
            r = act / pred[k] if pred[k] > 0 else float("inf")
            proj = r * total
            lines.append(f"{time.strftime('%H:%M:%S', time.localtime(now))} {s.label} sleep {k} closed "
                         f"{time.strftime('%H:%M:%S', time.localtime(mt))}: actual {act / 3600:.3f} h ({how}) · "
                         f"predicted {pred[k] / 3600:.3f} h · r {r:.3f} · projected total {proj / 3600:.2f} CPU-h"
                         + ("" if k >= 4 else " (k < 4: descriptive only)"))
            if k >= 4 and proj > LIMIT_S and fire is None:
                fire = (f"{s.label} at sleep {k}: projected {proj / 3600:.2f} CPU-h > 24 — STOP, re-price with "
                        f"r={r:.3f}, relaunch")
            if k >= checkpoint:
                reached.append(s.label)
        n_closed = len(closed)
        if pt is not None:
            k_next = n_closed + 1
            if k_next >= 4 and k_next in pred and pred[k_next] > 0:
                lb = pt[1] / pred[k_next] * total
                if lb > LIMIT_S and fire is None:
                    fire = (f"{s.label} still in sleep {k_next}: {pt[1] / 3600:.2f} CPU-h spent already projects "
                            f"{lb / 3600:.2f} CPU-h (a LOWER bound) > 24 — STOP, re-price, relaunch")
        elif n_closed < last_sleep:
            dead.append(f"{s.label}: process {s.pid} gone with {n_closed}/{last_sleep} sleeps closed")
    return lines, fire, reached, dead


def heartbeat(budget: dict, searches: List[Search], now: float) -> List[str]:
    pred = {int(k): float(v) for k, v in budget["predicted_cum_cpu_s"].items()}
    total = float(budget["predicted_total_cpu_h"]) * 3600.0
    out = []
    for s in searches:
        closed = closed_sleeps(s.run_dir)
        n = len(closed)
        since = f"since {time.strftime('%H:%M:%S', time.localtime(closed[-1][1]))}" if closed else "no sleep closed"
        if s.last is None:
            out.append(f"[d_projection] {time.strftime('%H:%M', time.localtime(now))} beat {s.label}: pid {s.pid} "
                       f"NOT SEEN · sleeps closed {n}")
            continue
        cpu, st = s.last
        if s.gone_at is not None:
            last_sleep = max(pred)
            out.append(f"[d_projection] {time.strftime('%H:%M', time.localtime(now))} beat {s.label}: pid {s.pid} GONE since "
                       f"{time.strftime('%H:%M:%S', time.localtime(s.gone_at))} · last CPU {cpu / 3600:.3f} h · "
                       f"{n}/{last_sleep} sleeps closed" + (" (finished)" if n >= last_sleep else ""))
            continue
        k_next = n + 1
        lb = f" · lower-bound projection {cpu / pred[k_next] * total / 3600:.2f} CPU-h" \
            if k_next in pred and pred[k_next] > 0 and k_next >= 4 else ""
        out.append(f"[d_projection] {time.strftime('%H:%M', time.localtime(now))} beat {s.label}: pid {s.pid} {st} · "
                   f"CPU {cpu / 3600:.3f} h · sleeps closed {n} · in sleep {k_next} {since}{lb}")
    return out


def record(run_dir: Path, tol_s: float = 0.25) -> int:
    """The positive control on a FINISHED run: sleep-k.json mtimes against cost.jsonl's own clock at each SLEEP."""
    closed = closed_sleeps(run_dir)
    rows = []
    for line in (run_dir / "cost.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r.get("where") == "sleep":
            rows.append(r)
    print(f"[record] {run_dir}: {len(closed)} closed snapshots · {len(rows)} SLEEP rows in cost.jsonl")
    if not closed or len(closed) != len(rows):
        print("[record] FAIL: the counts differ (or there are none)")
        return 1
    m1, w1 = closed[0][1], rows[0]["wall_s"]
    worst = 0.0
    for (k, mt), r in zip(closed, rows):
        dm, dw = mt - m1, r["wall_s"] - w1
        worst = max(worst, abs(dm - dw))
        print(f"  sleep {k:2d} seq {r['seq']:5d}: mtime−mtime₁ {dm:9.3f} s · wall_s−wall_s₁ {dw:9.3f} s · "
              f"diff {dm - dw:+.3f} s · arm_ms/1000 {r['arm_ms'] / 1000:9.3f} s · wall_s {r['wall_s']:9.3f} s")
    print(f"[record] worst |mtime clock − cost clock| = {worst:.3f} s (tolerance {tol_s} s) → "
          f"{'PASS' if worst <= tol_s else 'FAIL'}")
    return 0 if worst <= tol_s else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget")
    ap.add_argument("--run-dir", action="append")
    ap.add_argument("--checkpoint", type=int, default=7)
    ap.add_argument("--poll", type=int, default=15)
    ap.add_argument("--beat", type=int, default=600)
    ap.add_argument("--record")
    ns = ap.parse_args(argv)
    if ns.record:
        return record(Path(ns.record))
    if not ns.budget or not ns.run_dir:
        ap.error("--budget and at least one --run-dir are required (or --record)")
    budget = json.loads(Path(ns.budget).read_text())
    searches = [Search(Path(p), find_pid(Path(p))) for p in ns.run_dir]
    for s in searches:
        print(f"[d_projection] {s.label}: pid {s.pid if s.pid is not None else 'NOT FOUND'} · "
              f"sleeps closed now {len(closed_sleeps(s.run_dir))}", flush=True)
    if any(s.pid is None for s in searches):
        print("[d_projection] a search process was not found — refusing to watch a run it cannot clock", flush=True)
        return 2
    reached_all: set = set()
    last_beat = 0.0
    while True:
        now = time.time()
        lines, fire, reached, dead = poll(budget, searches, ns.checkpoint, now)
        for line in lines:
            print(line, flush=True)
        if fire:
            print(f"[d_projection] FIRE: {fire}", flush=True)
            return 10
        if dead:
            for d in dead:
                print(f"[d_projection] DEAD: {d}", flush=True)
            return 11
        if now - last_beat >= ns.beat:
            for line in heartbeat(budget, searches, now):
                print(line, flush=True)
            last_beat = now
        reached_all.update(reached)
        if len(reached_all) == len(searches):
            print(f"[d_projection] checkpoint sleep {ns.checkpoint} reached by every search; ratios above — "
                  f"read them by hand", flush=True)
            return 0
        time.sleep(ns.poll)


if __name__ == "__main__":
    sys.exit(main())
