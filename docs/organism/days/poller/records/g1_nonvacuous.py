#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:18 +0400 — POLLER-FIX G1 (docs/organism/days/PREREG-POLLER-FIX.md §3): the NOT VACUOUS clause of the identity replays.
"""g1_nonvacuous.py — G1 says an identity replay with the fix ON is NOT VACUOUS only if the replay's WORK ROOT (TMPDIR/creature-replay-*/state/) carries a SNAPSHOT.json whose
canvas_index equals its ledger.json's: the changed line ran (every 500 moments and at close); an ON replay that ignored the change would carry no key.

The integrator's replays run with TMPDIR = int/tmp, shared with every other gate, and creature.replay never prints its work root. So the work root is FOUND, not named: for each
identity replay (full cut, lean) of the label, a candidate is a creature-replay-* root modified after that replay's clock START whose manifest HAS the key; it counts only if
  (a) its manifest's canvas_index equals its own ledger.json's canvas_index (one parse of the ledger),
  (b) its manifest's last_seq equals the LAST seq of the replayed tape (the replay ran to the close, where the final snapshot is written) — a pristine-code replay of the same
      tape would lack the key, so a candidate that satisfies (a) and (b) can only be an ON replay of that tape.
All candidates are printed with their numbers (#168). --plant: the same check on a copy of a candidate's manifest with the key STRIPPED must FAIL (exit 0 = CAUGHT).
usage: python3 -B g1_nonvacuous.py --label poller-fix-9d43829 [--tmp <TMPDIR of the replays>] [--logs <int/logs>] [--plant]   exit 0 iff both replays are NON-VACUOUS."""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

INT = Path("/data/dev/swarm/2026-10-03/int")


def clock_start(clock: Path) -> float:
    first = clock.read_text().splitlines()[0]                     # «2026-10-03 22:04:48 +0400 start code ...»
    stamp = " ".join(first.split()[:3])
    return time.mktime(time.strptime(stamp[:19], "%Y-%m-%d %H:%M:%S")) - 5     # local time, a 5 s margin


def tape_last_seq(tape_dir: Path) -> int:
    last_file = sorted(Path(tape_dir).glob("*.jsonl"))[-1]
    line = subprocess.run(["tail", "-n", "1", str(last_file)], capture_output=True, text=True, check=True).stdout.strip()
    return int(json.loads(line)["seq"])


def candidates(tmp: Path, since: float, strip_key: bool = False) -> list:
    out = []
    for d in sorted(glob.glob(str(tmp / "creature-replay-*"))):
        sj, lj = Path(d) / "state" / "SNAPSHOT.json", Path(d) / "state" / "ledger.json"
        if not sj.exists() or not lj.exists() or sj.stat().st_mtime < since:
            continue
        m = json.loads(sj.read_text())
        if strip_key:
            m = {k: v for k, v in m.items() if k != "canvas_index"}
        if "canvas_index" not in m:
            continue
        led = json.loads(lj.read_text())
        out.append({"root": d, "manifest_canvas_index": m["canvas_index"], "ledger_canvas_index": led.get("canvas_index"), "manifest_t": m.get("t"), "ledger_moments": led.get("moments"),
                    "manifest_last_seq": m.get("last_seq"), "equal": m["canvas_index"] == led.get("canvas_index")})
        del led
    return out


def check(name: str, tape_dir: Path, clock: Path, tmp: Path, strip_key: bool = False) -> bool:
    since, last = clock_start(clock), tape_last_seq(tape_dir)
    cands = candidates(tmp, since, strip_key)
    print(f"{name}: tape {tape_dir} last seq {last}; replay clock start {time.strftime('%F %T', time.localtime(since + 5))}; keyed candidates {len(cands)}")
    ok = False
    for c in cands:
        hit = c["equal"] and c["manifest_last_seq"] == last
        ok |= hit
        print(f"   {'MATCH' if hit else 'no   '} {c['root']}: manifest canvas_index {c['manifest_canvas_index']} == ledger {c['ledger_canvas_index']}: {c['equal']}; manifest t {c['manifest_t']} (ledger moments {c['ledger_moments']}); last_seq {c['manifest_last_seq']} (tape's {last})")
    print(f"   {name}: {'NOT VACUOUS: a keyed work root of an ON replay of this tape, key equal to its ledger, last_seq at the tape end' if ok else 'VACUOUS or NOT FOUND'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--tmp", default=str(INT / "tmp"))
    ap.add_argument("--logs", default=str(INT / "logs"))
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    tmp, logs = Path(a.tmp), Path(a.logs)
    runs = (("full", INT / "full-cut" / "tape", logs / f"{a.label}-id-full.clock"), ("lean", INT / "lean" / "tape", logs / f"{a.label}-id-lean.clock"))
    if a.plant:
        res = [check(n + " (key STRIPPED: the plant)", t, c, tmp, strip_key=True) for n, t, c in runs]
        caught = not any(res)
        print("PLANT:", "CAUGHT: with the key stripped no work root is NON-VACUOUS" if caught else "NOT caught: the check passes a keyless manifest")
        return 0 if caught else 1
    res = [check(n, t, c, tmp) for n, t, c in runs]
    print("RESULT:", "OK: both identity replays are NON-VACUOUS" if all(res) else "NOT OK")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
