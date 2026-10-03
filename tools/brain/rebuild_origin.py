#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:03 +0400 — PREREG-RESIT-READER v4 §5 / R10: the ORIGIN REBUILD, built in the law's order — the PILOT first (R10f: the first K rows of a life's tape replayed by the life's
# own Mind, CPU and peak memory sampled, extrapolated to the begin row with the growth the pilot shows, printed beside the 4 CPU-h line). The replay-and-save driver (R10a–e) follows in this file.
"""tools/brain/rebuild_origin.py — rebuild the brain AT a life's sittings by replaying its tape, and price that replay first.

RUN BY PATH, never `-m`:  python3 -B -I tools/brain/rebuild_origin.py pilot --root R --code C --out OUT --rows K --target-rows B [--sample-every N] [--cpu-cap-s S] [--genome G]

The tool imports the standard library only until the life's code is put FIRST on sys.path; then it imports the life's own `creature.mind.Mind` (it replays the mind) and refuses a harness that
imported a module of those packages before (R11). It reads the life's tape (only complete lines), writes only under its own --out, never under a life, never touches a unit."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

MODULE_PREFIXES = ("genome", "brain", "creature", "tools")
STOP_LINE_CPU_H = 4.0                 # law R10f: above this the builder STOPS and the seat decides
PILOT_CPU_CAP_S = 900                 # law R10f: a pilot that costs at most 15 CPU-min


class RebuildError(Exception):
    """A refusal by name (exit 2)."""


# ================================================================================================ small helpers
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def check_flags(dont_write_bytecode: int, isolated: int, env: Mapping[str, str]) -> Dict[str, object]:
    """§1.0 for the rebuild too: -B (no bytecode written into a life's code dir), -I (no PYTHON* variable can put another tree first), and both BLAS pins at 1 (a brain state's float bits depend on
    the BLAS thread count, #246 (8))."""
    problems: List[str] = []
    if not dont_write_bytecode:
        problems.append("python was not started with -B (an import would write .pyc files into the life's code dir)")
    if not isolated:
        problems.append("python was not started with -I (a PYTHON* variable could put another tree first on sys.path)")
    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
        if env.get(var) != "1":
            problems.append(f"{var} is {env.get(var)!r}, not '1' (a brain state's float bits depend on it)")
    if problems:
        raise RebuildError("refused: " + "; ".join(problems))
    return {"dont_write_bytecode": True, "isolated": True, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}


def pre_import_check(prefixes: Sequence[str] = MODULE_PREFIXES) -> None:
    pre = sorted(m for m in sys.modules if m.split(".")[0] in prefixes)
    if pre:
        raise RebuildError(f"R11: {len(pre)} module(s) of {list(prefixes)} were imported before the import step, e.g. {pre[:6]} — refused")


def modules_report(code: str, prefixes: Sequence[str] = MODULE_PREFIXES) -> Dict[str, object]:
    """R11: every loaded module of the life's packages has its realpath under realpath(<code>); the sha256 of each file goes into the row."""
    code_real = os.path.realpath(code)
    bad: List[str] = []
    files: Dict[str, str] = {}
    for name, mod in list(sys.modules.items()):
        if name.split(".")[0] not in prefixes:
            continue
        f = getattr(mod, "__file__", None)
        paths = [f] if f else list(getattr(mod, "__path__", None) or [])
        for pth in paths:
            rp = os.path.realpath(pth)
            if not (rp == code_real or rp.startswith(code_real + os.sep)):
                bad.append(f"{name} ({rp})")
            elif f and os.path.isfile(rp):
                files[os.path.relpath(rp, code_real)] = sha256_file(rp)
    if bad:
        raise RebuildError(f"R11: {len(bad)} module(s) are not under {code_real}: {sorted(bad)[:6]} — refused")
    mods = [{"rel": r, "sha256": s} for r, s in sorted(files.items())]
    return {"modules": mods, "digest": sha256_bytes("".join(f"{m['rel']}\0{m['sha256']}\n" for m in mods).encode("utf-8"))}


def resolve_tape_dir(root, declared_path: Optional[str]) -> Path:
    """creature.tape._resolve_tape_dir, copied (the life's own function is the authority; a parity test pins it)."""
    root = Path(root)
    if not declared_path:
        return root / "tape"
    parts = Path(declared_path).parts
    if parts and parts[0] == "run":
        parts = parts[1:]
    return root / Path(*parts) if parts else root / "tape"


def tape_decl_of(genome_text: str) -> Optional[str]:
    for line in genome_text.splitlines():
        w = line.split("#", 1)[0].split()
        if len(w) >= 2 and w[0] == "TAPE":
            return w[1]
    return None


def parse_proc_status(text: str) -> Dict[str, Optional[float]]:
    """VmRSS and VmHWM of a /proc/<pid>/status text, in MB; a missing field reads None, never 0."""
    out: Dict[str, Optional[float]] = {"rss_mb": None, "hwm_mb": None}
    for line in text.splitlines():
        if line.startswith("VmRSS:"):
            out["rss_mb"] = int(line.split()[1]) / 1024.0
        elif line.startswith("VmHWM:"):
            out["hwm_mb"] = int(line.split()[1]) / 1024.0
    return out


def read_self_status() -> Dict[str, Optional[float]]:
    return parse_proc_status(Path("/proc/self/status").read_text())


# ================================================================================================ the cut (law §5 step 1, R10a)
def cut_prefix(tape_dir, out_dir, k_rows: int) -> Dict[str, object]:
    """Stream the FIRST `k_rows` rows of a life's tape (every day file in order, complete lines only) into `<out>/tape/<day>.jsonl`; `<out>/tape/payload` is a symlink to the life's own payload
    directory (never copied, as creature.replay does). The life's files are only read. A line that does not end in `}` is a half-written one and is COUNTED, never copied."""
    tape_dir, out_dir = Path(tape_dir), Path(out_dir)
    (out_dir / "tape").mkdir(parents=True, exist_ok=True)
    rows = torn = 0
    last_seq: Optional[int] = None
    files: List[str] = []
    h = hashlib.sha256()
    for day in sorted(tape_dir.glob("*.jsonl")):
        if rows >= k_rows:
            break
        kept: List[str] = []
        with day.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.rstrip("\n")
                if not s.strip():
                    continue
                if not s.rstrip().endswith("}"):
                    torn += 1
                    continue
                if rows >= k_rows:
                    break
                r = json.loads(s)
                kept.append(s)
                rows += 1
                last_seq = int(r["seq"])
                h.update(f"{r['seq']}\0{r.get('sha')}\n".encode("utf-8"))
        if kept:
            (out_dir / "tape" / day.name).write_text("\n".join(kept) + "\n", encoding="utf-8")
            files.append(day.name)
    payload_src = tape_dir / "payload"
    link = out_dir / "tape" / "payload"
    if payload_src.exists() and not link.exists() and not link.is_symlink():
        os.symlink(os.path.realpath(payload_src), link)
    return {"rows": rows, "last_seq": last_seq, "files": files, "torn_lines": torn, "tape_digest": h.hexdigest()}


# ================================================================================================ the price: rates, growth fit, extrapolation (law R10f)
def interval_rates(samples: Sequence[Mapping[str, float]]) -> List[Tuple[float, float]]:
    """[(midpoint row, CPU-s per row)] for each interval between consecutive samples, the first interval running from row 0 / CPU 0."""
    out: List[Tuple[float, float]] = []
    pi, pc = 0.0, 0.0
    for s in samples:
        di = float(s["i"]) - pi
        if di > 0:
            out.append(((pi + float(s["i"])) / 2.0, (float(s["cpu_s"]) - pc) / di))
        pi, pc = float(s["i"]), float(s["cpu_s"])
    return out


def fit_power_law(points: Sequence[Tuple[float, float]]) -> Optional[Dict[str, float]]:
    """Least squares of ln(rate) on ln(row): rate = a * row^p. None with fewer than two usable points."""
    pts = [(math.log(x), math.log(y)) for x, y in points if x > 0 and y > 0]
    n = len(pts)
    if n < 2:
        return None
    mx, my = sum(x for x, _ in pts) / n, sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    p = sum((x - mx) * (y - my) for x, y in pts) / sxx
    ln_a = my - p * mx
    ss_tot = sum((y - my) ** 2 for _, y in pts)
    ss_res = sum((y - (ln_a + p * x)) ** 2 for x, y in pts)
    return {"p": p, "a": math.exp(ln_a), "n": n, "r2": (1.0 - ss_res / ss_tot) if ss_tot > 0 else 1.0}


def _integral(fit: Mapping[str, float], lo: float, hi: float) -> float:
    a, p = fit["a"], fit["p"]
    if abs(p + 1.0) < 1e-12:
        return a * math.log(hi / lo)
    return a / (p + 1.0) * (hi ** (p + 1.0) - lo ** (p + 1.0))


def extrapolate_cpu(samples: Sequence[Mapping[str, float]], target_rows: int, skip_first: int = 1) -> Dict[str, object]:
    """The pilot's CPU to the begin row, three ways, all printed: LOWER = the last interval's rate held constant (growth ignored); CENTRAL = the power law fitted to every interval after the first
    (warm-up) integrated from the pilot's end to the target; UPPER = the same law fitted to the last third of the intervals (the steepest local growth), never below CENTRAL."""
    K = float(samples[-1]["i"])
    if target_rows <= K:
        raise ValueError(f"the target ({target_rows} rows) must exceed the pilot's rows ({int(K)})")
    measured = float(samples[-1]["cpu_s"])
    rates = interval_rates(samples)
    last_rate = rates[-1][1]
    lower = measured + last_rate * (target_rows - K)
    use = rates[skip_first:] if len(rates) > skip_first + 1 else rates
    fit = fit_power_law(use)
    central = measured + (_integral(fit, K, float(target_rows)) if fit else last_rate * (target_rows - K))
    third = use[-max(2, len(use) // 3):]
    fit_u = fit_power_law(third)
    upper = max(central, measured + (_integral(fit_u, K, float(target_rows)) if fit_u else 0.0))
    mid = rates[len(rates) // 2]
    return {"pilot_rows": int(K), "target_rows": int(target_rows), "measured_cpu_s": measured, "lower_cpu_s": lower, "central_cpu_s": central, "upper_cpu_s": upper,
            "lower_cpu_h": lower / 3600.0, "central_cpu_h": central / 3600.0, "upper_cpu_h": upper / 3600.0,
            "fit": ({k: fit[k] for k in ("p", "a", "n", "r2")} if fit else None), "fit_last_third": ({k: fit_u[k] for k in ("p", "a", "n", "r2")} if fit_u else None),
            "windows": {"start_cpu_s_per_row": rates[0][1], "mid_cpu_s_per_row": mid[1], "end_cpu_s_per_row": last_rate, "n_intervals": len(rates)}}


def _linear(points: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    n = len(points)
    mx, my = sum(x for x, _ in points) / n, sum(y for _, y in points) / n
    sxx = sum((x - mx) ** 2 for x, _ in points)
    s = (sum((x - mx) * (y - my) for x, y in points) / sxx) if sxx > 0 else 0.0
    return s, my - s * mx


def extrapolate_rss(samples: Sequence[Mapping[str, float]], target_rows: int) -> Dict[str, object]:
    """The pilot's resident memory to the begin row (RULES 6d): LOWER = the last sample held flat; CENTRAL = the straight line through every sample; UPPER = the line through the last third
    (the steepest local growth), never below CENTRAL. Also the sampled RSS at the start and end and the peak VmHWM."""
    pts = [(float(s["i"]), float(s["rss_mb"])) for s in samples if s.get("rss_mb") is not None]
    if len(pts) < 2:
        raise ValueError("memory: fewer than two samples carry an RSS reading")
    s_all, r_all = _linear(pts)
    third = pts[-max(2, len(pts) // 3):]
    s_up, r_up = _linear(third)
    t = float(target_rows)
    last = pts[-1][1]
    central = max(last, r_all + s_all * t)
    upper = max(central, r_up + s_up * t)
    hwm = [float(s["hwm_mb"]) for s in samples if s.get("hwm_mb") is not None]
    return {"target_rows": int(target_rows), "rss_at_start_mb": pts[0][1], "rss_at_end_mb": last, "peak_hwm_mb": max(hwm) if hwm else None, "lower_rss_mb": last,
            "central_rss_mb": central, "upper_rss_mb": upper, "slope_mb_per_row": s_all, "slope_last_third_mb_per_row": s_up}


# ================================================================================================ the pilot
def cmd_pilot(a: argparse.Namespace) -> int:
    flags = check_flags(sys.flags.dont_write_bytecode, sys.flags.isolated, os.environ)
    root, out, code = Path(a.root), Path(a.out), Path(a.code)
    ro = os.path.realpath(root)
    oo = os.path.realpath(out)
    if oo == ro or oo.startswith(ro + os.sep):
        raise RebuildError(f"--out {a.out} lies inside {root}: nothing is ever written under a life; give an OUT elsewhere")
    genome_path = Path(a.genome) if a.genome else root / "GENOME.genome"
    tape_decl = tape_decl_of(genome_path.read_text())
    out.mkdir(parents=True, exist_ok=True)
    t_wall0 = time.time()
    cut = cut_prefix(resolve_tape_dir(root, tape_decl), out / "cut", int(a.rows))
    if cut["rows"] == 0:
        raise RebuildError(f"the tape under {root} yielded no row")
    pre_import_check()
    codes = os.path.realpath(code)
    sys.path.insert(0, codes)
    from creature.mind import Mind                              # the LIFE's own mind (R11 asserts it came from <code>)
    from creature.tape import _resolve_tape_dir
    from genome.machinery import parse_genome
    rep = modules_report(codes)
    work_root = out / "work"
    if work_root.exists() and any(work_root.iterdir()):
        raise RebuildError(f"{work_root} exists and is not empty: a replay needs a FRESH root (PREREG section 2.11)")
    work_root.mkdir(parents=True, exist_ok=True)
    work_tape = _resolve_tape_dir(work_root, parse_genome(genome_path.read_text()).declared.get("TAPE", {}).get("path"))
    work_tape.mkdir(parents=True, exist_ok=True)
    os.symlink(os.path.realpath(out / "cut" / "tape" / "payload"), work_tape / "payload")
    mind = Mind(genome_path, work_root, blind=frozenset())
    samples: List[Dict[str, object]] = []
    stopped = "rows"
    i = 0
    cpu0 = time.process_time()
    w0 = time.time()

    def sample(row_seq) -> None:
        st = read_self_status()
        cells = None
        try:
            cells = int(mind.org.summary()["cells"])
        except Exception:
            pass
        samples.append({"i": i, "seq": row_seq, "cpu_s": round(time.process_time() - cpu0, 4), "wall_s": round(time.time() - w0, 3), "rss_mb": st["rss_mb"], "hwm_mb": st["hwm_mb"], "cells": cells})

    last_seq = None
    done = False
    for day in sorted((out / "cut" / "tape").glob("*.jsonl")):
        with day.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                mind.consume(row)
                i += 1
                last_seq = row["seq"]
                if i % int(a.sample_every) == 0:
                    sample(last_seq)
                if time.process_time() - cpu0 >= float(a.cpu_cap_s):
                    stopped = "cpu cap"
                    done = True
                    break
                if i >= int(a.rows):
                    done = True
                    break
        if done:
            break
    if not done and i < int(a.rows):
        stopped = "tape end"
    if not samples or samples[-1]["i"] != i:
        sample(last_seq)
    cpu_total = time.process_time() - cpu0
    res: Dict[str, object] = {"kind": "rebuild-pilot", "reader_sha256": sha256_file(__file__), "flags": flags, "root": str(root), "genome": str(genome_path),
                              "subject": {"code": codes, "modules": rep["modules"], "modules_digest": rep["digest"], "python": sys.version.split()[0]},
                              "cut": cut, "rows_requested": int(a.rows), "rows_replayed": i, "stopped": stopped, "sample_every": int(a.sample_every), "samples": samples,
                              "cpu_replay_s": round(cpu_total, 3), "wall_s": round(time.time() - t_wall0, 3), "target_rows": int(a.target_rows),
                              "stop_line_cpu_h": STOP_LINE_CPU_H}
    if i < int(a.target_rows) and len(samples) >= 2:
        cpu = extrapolate_cpu(samples, int(a.target_rows))
        res["cpu"] = cpu
        res["memory"] = extrapolate_rss(samples, int(a.target_rows))
        lo, hi = cpu["lower_cpu_h"], cpu["upper_cpu_h"]
        res["verdict_vs_line"] = "UNDER" if hi < STOP_LINE_CPU_H else ("OVER" if lo > STOP_LINE_CPU_H else "STRADDLES")
    else:
        res["cpu"], res["memory"], res["verdict_vs_line"] = None, None, "NOT EXTRAPOLATED (the pilot reached or passed the target, or fewer than two samples)"
    atomic_write(out / "pilot.json", json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    short = {"pilot": str(out / "pilot.json"), "rows_replayed": i, "stopped": stopped, "cpu_replay_s": res["cpu_replay_s"], "verdict_vs_line": res["verdict_vs_line"]}
    if res["cpu"]:
        short["central_cpu_h"] = round(res["cpu"]["central_cpu_h"], 3)
        short["range_cpu_h"] = [round(res["cpu"]["lower_cpu_h"], 3), round(res["cpu"]["upper_cpu_h"], 3)]
        short["central_rss_mb"] = round(res["memory"]["central_rss_mb"])
    print(json.dumps(short))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="rebuild_origin.py", allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pilot", allow_abbrev=False)
    p.add_argument("--root", required=True, help="the life whose tape is replayed (a closed life, or a copy of a live one)")
    p.add_argument("--code", required=True, help="the code the life's own Mind runs (its code/ checkout)")
    p.add_argument("--out", required=True)
    p.add_argument("--genome", help="the launch genome (default <root>/GENOME.genome)")
    p.add_argument("--rows", type=int, required=True, help="K: how many rows of the tape the pilot replays")
    p.add_argument("--target-rows", type=int, required=True, help="B: the begin row's count, counted from the tape")
    p.add_argument("--sample-every", type=int, default=500)
    p.add_argument("--cpu-cap-s", type=float, default=PILOT_CPU_CAP_S)
    a = ap.parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if a.cmd == "pilot":
            return cmd_pilot(a)
    except RebuildError as e:
        print(json.dumps({"refused": str(e)}))
        return 2
    return 64


if __name__ == "__main__":
    sys.exit(main())
