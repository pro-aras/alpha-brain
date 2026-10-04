#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:30 +0400 (written 21:30:03) — PREREG-EVOLVE-CAL: the twin queue (one twin at a time, resumable). Tests first: tests/tools/test_evolve_cal_queue.py.
"""tools/evolve_cal_queue.py — a list of twins run ONE AT A TIME through slot, resumable.

  python3 -m tools.evolve_cal_queue run --list L.tsv --cp <checkpoint copy> --slice-root <mini tape> --from-seq A --to-seq B --out-root <dir> [--slot-mem 8G] [--dry-run]

L.tsv: `label<TAB>variant<TAB>rows-limit-or-dash`, `#` comments and blank lines ignored. A twin is DONE when `<out>/<label>/reading.json` exists (tools/evolve_cal.py's run_twin
writes it last, atomically). A half-written twin directory is moved aside to `<label>.stale-<n>`, never deleted and never overwritten. The queue stops at the first twin
that does not exit 0 (a failed twin is read before anything else runs). Each twin is its own process under `slot` with `SLOT_MEM` (default 8G: the measured price of one
twin is 6.5 GB RSS, RULES 6d); the queue itself holds no memory and spawns at most one slot job at a time.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:52 +0400 — AMENDMENT 3b A3b.4 (the verifier's E4): `make-eps-list` writes the epsilon twins of N2 at the CHOSEN level.
LEVELS = (1e-4, 1e-3, 1e-2)       # A3.4's levels {epsilon_f / 10, epsilon_f, epsilon_f x 10}, epsilon_f = 1e-3 by the ladder

_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
_VARIANT = re.compile(r"(incumbent|eps:[0-9.eE+-]+:[0-9]+|seed:[0-9]+|gene:[A-Za-z_.]+=[-0-9.eE+]+)\Z")

Entry = Tuple[str, str, Optional[int]]


def read_list(path: Path) -> List[Entry]:
    entries: List[Entry] = []
    seen = set()
    for n, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            raise ValueError(f"{path}:{n}: need label<TAB>variant<TAB>rows-limit-or-dash, got {len(parts)} field(s)")
        label, variant, rows = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not _LABEL.match(label):
            raise ValueError(f"{path}:{n}: bad label {label!r}")
        if label in seen:
            raise ValueError(f"{path}:{n}: duplicate label {label!r}")
        if not _VARIANT.match(variant):
            raise ValueError(f"{path}:{n}: bad variant {variant!r}")
        if rows == "-":
            limit = None
        elif rows.isdigit() and int(rows) > 0:
            limit = int(rows)
        else:
            raise ValueError(f"{path}:{n}: rows-limit must be a positive integer or a dash, got {rows!r}")
        seen.add(label)
        entries.append((label, variant, limit))
    return entries


def plan(entries: Sequence[Entry], out_root: Path, cp: str, slice_root: str, from_seq: int, to_seq: int, lane: str = "integrator",
         slot: str = "/data/dev/swarm/bin/slot", slot_mem: str = "8G", python: str = "/usr/bin/python3") -> List[dict]:
    out_root = Path(out_root)
    todo: List[dict] = []
    for label, variant, limit in entries:
        d = out_root / label
        if (d / "reading.json").exists():
            continue
        aside = None
        if d.exists():
            k = 1
            while (out_root / f"{label}.stale-{k}").exists():
                k += 1
            aside = out_root / f"{label}.stale-{k}"
        argv = [slot, lane, f"evcal-{label}", "--", "/usr/bin/time", "-v", "env", "PYTHONPATH=.", "OPENBLAS_NUM_THREADS=1", python, "-B", "-m", "tools.evolve_cal",
                "twin", "--cp", str(cp), "--slice-root", str(slice_root), "--from-seq", str(from_seq), "--to-seq", str(to_seq), "--variant", variant,
                "--label", label, "--out", str(d)]
        if limit is not None:
            argv += ["--rows-limit", str(limit)]
        todo.append({"label": label, "variant": variant, "argv": argv, "env": {"SLOT_MEM": slot_mem, "SLOT_SWAP": "1G"},
                     "log": out_root / f"{label}.log", "exit": out_root / f"{label}.exit", "set_aside": aside})
    return todo


def _spawn(argv: List[str], env: Dict[str, str], log: Path) -> int:
    with Path(log).open("w") as f:
        return subprocess.run(argv, env={**os.environ, **env}, stdout=f, stderr=subprocess.STDOUT).returncode


def run(entries: Sequence[Entry], out_root: Path, runner: Optional[Callable[[List[str], Dict[str, str], Path], int]] = None,
        dry_run: bool = False, **plan_args) -> List[dict]:
    todo = plan(entries, out_root, **plan_args)
    if dry_run:
        return [{"label": p["label"], "variant": p["variant"], "exit": None, "argv": p["argv"]} for p in todo]
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    runner = runner or _spawn
    results: List[dict] = []
    for p in todo:
        if p["set_aside"] is not None:
            os.rename(out_root / p["label"], p["set_aside"])
        (out_root / f"{p['label']}.started").write_text(time.strftime("%F %T %z") + "\n")
        rc = runner(p["argv"], p["env"], p["log"])
        Path(p["exit"]).write_text(f"{rc}\n")
        results.append({"label": p["label"], "variant": p["variant"], "exit": rc})
        print(json.dumps(results[-1]), flush=True)
        if rc != 0:
            break
    return results


def level_tag(level: float) -> str:
    """1e-3 -> '1e-3' (the tag the existing lists use in their labels)."""
    m, e = f"{level:.0e}".split("e")
    return f"{m}e{int(e)}"


def eps_list(level: float, n: int, prefix: str = "", with_incumbent: bool = False) -> str:
    """The text of a queue list: n epsilon twins at ONE of A3.4's three levels (k = 1 .. n; variant `eps:<level>:<k>` is lr × (1 + k·level)), optionally led by the incumbent.
    N2 in the non-degenerate branch (A3b.4) runs the SAME KIND of twin as the S1 null of the dimension it tests: epsilon twins at the chosen level for q1_seen and
    confirmed_share (seed twins never move them: F would be infinite by construction)."""
    lv = next((x for x in LEVELS if math.isclose(level, x, rel_tol=1e-9)), None)
    if lv is None:
        raise ValueError(f"eps_list: level {level!r} is not one of A3.4's three levels {LEVELS}")
    if isinstance(n, bool) or not isinstance(n, int) or not (1 <= n <= 20):
        raise ValueError(f"eps_list: n must be an integer from 1 to 20, got {n!r}")
    lines = [f"# {n} epsilon twin(s) at {lv!r} (AMENDMENT 3b A3b.4: twins of the null's own kind), written by `tools.evolve_cal_queue make-eps-list`: label<TAB>variant<TAB>rows-limit"]
    if with_incumbent:
        lines.append(f"{prefix}inc\tincumbent\t-")
    for k in range(1, n + 1):
        lines.append(f"{prefix}eps{level_tag(lv)}-k{k:02d}\teps:{lv!r}:{k}\t-")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make-eps-list")
    m.add_argument("--eps", type=float, required=True); m.add_argument("--n", type=int, required=True); m.add_argument("--prefix", default="")
    m.add_argument("--with-incumbent", action="store_true"); m.add_argument("--out", required=True)
    p = sub.add_parser("run")
    p.add_argument("--list", required=True); p.add_argument("--cp", required=True); p.add_argument("--slice-root", required=True)
    p.add_argument("--from-seq", type=int, required=True); p.add_argument("--to-seq", type=int, required=True)
    p.add_argument("--out-root", required=True); p.add_argument("--lane", default="integrator"); p.add_argument("--slot-mem", default="8G")
    p.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "make-eps-list":
        text = eps_list(a.eps, a.n, prefix=a.prefix, with_incumbent=a.with_incumbent)
        with open(a.out, "x") as f:                      # never overwrite a list: a list is a record
            f.write(text)
        return 0
    entries = read_list(Path(a.list))
    res = run(entries, Path(a.out_root), dry_run=a.dry_run, cp=a.cp, slice_root=a.slice_root, from_seq=a.from_seq, to_seq=a.to_seq, lane=a.lane,
              slot_mem=a.slot_mem)
    if a.dry_run:
        for r in res:
            print(" ".join(r["argv"]))
    return 0 if all(r["exit"] in (0, None) for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
