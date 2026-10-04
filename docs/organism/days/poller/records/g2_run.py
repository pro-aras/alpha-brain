#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:01 +0400 — POLLER-FIX G2 (docs/organism/days/PREREG-POLLER-FIX.md §3): the driver over the 40 saved states.
"""g2_run.py — G2 over brain-long-2's 38 checkpoints, its closed final state, and brain-long-3's fallback copy: each state in its OWN child process (so a state's
memory is its own), the child run with cwd = the life's own code with the fix applied (the OVERLAY), PYTHONPATH=. , BLAS threads 1.

    python3 -B <this file> --out <dir> [--only ck1,final] [--skip-bl3] [--work <scratch>] [--ov-bl2 <tree>] [--ov-bl3 <tree>]

Per state it prints started / read / compared / differing; at the end the counts (every «0 of 40 differ» is printed beside the presence counts, #168):
states started, read (the ledger carried a canvas_index), compared, differing, road «ledger» before (old format), road «snapshot» after, ablation → ledger,
plant reported different. Exit 0 iff all states ran and every check of every state holds.
bl2's checkpoints are read from /data/dev/genome-lives/brain-long-2/evolve/checkpoints/<n>/{state,GENOME.genome}, the closed state from .../state with its latest
GENOME.v<n>.genome (the pilot's rule); bl3's fallback copy is FLAT (no state/, no genome): it is copied into root/state and named by genome/brain/lives/BRAIN-LONG-3.genome
of its own code tree."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

LIFE2 = Path("/data/dev/genome-lives/brain-long-2")
BL3_COPY = Path("/data/dev/brain-runs/day1003/brain-long-3-origin-fallback/copy-20261003-193014")
HERE = Path(__file__).resolve().parent


def states(ov2: Path, ov3: Path, skip_bl3: bool) -> list:
    out = []
    for n in range(1, 39):
        out.append((f"ck{n}", LIFE2 / "evolve" / "checkpoints" / str(n) / "state", LIFE2 / "evolve" / "checkpoints" / str(n) / "GENOME.genome", ov2))
    v = sorted(LIFE2.glob("GENOME.v*.genome"))
    out.append(("final", LIFE2 / "state", v[-1] if v else LIFE2 / "GENOME.genome", ov2))
    if not skip_bl3:
        out.append(("bl3-fallback", BL3_COPY, ov3 / "genome" / "brain" / "lives" / "BRAIN-LONG-3.genome", ov3))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-bl3", action="store_true")
    ap.add_argument("--work", default=os.environ.get("TMPDIR", "/tmp"))
    ap.add_argument("--ov-bl2", default="/data/dev/genome-wt-poller-ov-9f19879")
    ap.add_argument("--ov-bl3", default="/data/dev/genome-wt-poller-ov-d2fe75b")
    ap.add_argument("--timeout", type=int, default=2400)
    a = ap.parse_args()
    out_dir = Path(a.out).resolve()                           # ABSOLUTE: the child's cwd is the overlay tree, not this one (the first ck1 run died on a relative --out)
    a.work = str(Path(a.work).resolve())
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "g2.jsonl"
    want = [s for s in a.only.split(",") if s]
    todo = [s for s in states(Path(a.ov_bl2), Path(a.ov_bl3), a.skip_bl3) if not want or s[0] in want]
    started = 0
    t_all = time.time()
    for label, src, genome, ov in todo:
        assert src.exists() and genome.exists() and ov.exists(), f"{label}: a path is missing ({src.exists()}, {genome.exists()}, {ov.exists()})"
        started += 1
        env = dict(os.environ, PYTHONPATH=".", OPENBLAS_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
        cmd = [sys.executable, "-B", str(HERE / "g2_cadence.py"), "--label", label, "--src", str(src), "--genome", str(genome), "--work", a.work, "--out", str(jsonl)]
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=ov, env=env, capture_output=True, text=True, timeout=a.timeout)
            line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else f"(no stdout) exit {p.returncode} {p.stderr[-300:]}"
        except subprocess.TimeoutExpired:
            line = f"TIMEOUT after {a.timeout}s"
        print(f"[{started}/{len(todo)}] {label}: {line}  ({time.time() - t0:.0f}s)", flush=True)
    rows = [json.loads(l) for l in jsonl.read_text().splitlines() if l.strip()] if jsonl.exists() else []
    ran = {r["label"]: r for r in rows}                       # the LAST line of a label wins (a re-run replaces)
    n = len(todo)
    read = sum(1 for r in ran.values() if r.get("ledger_has_canvas_index"))
    compared = sum(1 for r in ran.values() if r.get("compared"))
    differing = sum(1 for r in ran.values() if r.get("compared") and r.get("differs"))
    old_ledger = sum(1 for r in ran.values() if r.get("road_old") == "ledger")
    new_snap = sum(1 for r in ran.values() if r.get("road_new") == "snapshot")
    abl = sum(1 for r in ran.values() if r.get("ablated", [None, None])[1] == "ledger")
    plant = sum(1 for r in ran.values() if r.get("plant", {}).get("reported_different"))
    ok_all = sum(1 for r in ran.values() if r.get("ok"))
    summary = {"states_expected": n, "states_started": started, "states_recorded": len(ran), "ledger_has_canvas_index": read, "compared": compared, "differing": differing,
               "old_road_ledger": old_ledger, "new_road_snapshot": new_snap, "ablation_falls_to_ledger": abl, "plant_reported_different": plant, "all_checks_ok": ok_all,
               "wall_s": round(time.time() - t_all), "ok": bool(len(ran) == n and ok_all == n and differing == 0)}
    (out_dir / "g2-summary.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True))
    txt = [f"G2 SUMMARY: started {started} of {n}; recorded {len(ran)}; the ledger carried canvas_index in {read} of {n} (presence); compared {compared}; DIFFERING {differing}",
           f"road before (old format) = ledger on {old_ledger} of {n}; road after resume+snapshot = snapshot on {new_snap} of {n}; ablation (key stripped) -> ledger on {abl} of {n}; plant reported DIFFERENT on {plant} of {n}",
           f"every check of a state holds on {ok_all} of {n}; wall {summary['wall_s']} s", "RESULT: " + ("OK" if summary["ok"] else "NOT OK")]
    for r in sorted(ran.values(), key=lambda r: (r["label"].startswith("bl3"), r["label"] == "final", int(r["label"][2:]) if r["label"].startswith("ck") else 0)):
        txt.append(f"  {r['label']:13s} moments {r.get('moments')} canvas_index {r.get('reference')} old {r.get('road_old')}:{r.get('n_old')} new {r.get('road_new')}:{r.get('n_new')} "
                   f"resume {r.get('resume_s')}s snapshot {r.get('snapshot_s')}s hwm {r.get('hwm_mb')} MB {'OK' if r.get('ok') else 'FAIL ' + str(r.get('error') or [k for k, v in r.get('checks', {}).items() if not v])}")
    (out_dir / "g2-summary.txt").write_text("\n".join(txt) + "\n")
    print("\n".join(txt[:4]))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
