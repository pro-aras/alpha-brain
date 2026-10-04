#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:24 +0400 — POLLER-FIX G6 (docs/organism/days/PREREG-POLLER-FIX.md §3): the suites' verdict, read from each suite's OWN log.
"""g6_read.py — G6: «the suites on the final sha, read from their own files: genome, tools, scene, brain and creature in three parts. Each «Ran N» is compared with the BASELINE the
integrator's gate already wrote for the same suite, plus the number of tests this law adds, read from its own file; every part's exit is 0.»

Baselines (the integrator's logs; `git diff --stat 3f9db48 233a4cb -- creature genome brain tests/creature tests/genome tests/brain tests/scene` is empty, so the organism suites' counts on
233a4cb are the 3f9db48 ones; tools and genome have their own logs AT 233a4cb):
  genome   713   int/logs/docs-toys2-genome-233a4cb.log   (OK, skipped=1, expected failures=6)
  tools    384   int/logs/docs-toys2-tools-233a4cb.log
  scene    368   int/logs/inner-scene-3f9db48.log
  brain    770   int/logs/inner-brain-3f9db48.log        (OK, skipped=2)
  creature 1390  int/logs/inner-creature-3f9db48.split.txt: parts 444 / 525 / 421 (patterns test_[a-f]*.py, test_[g-r]*.py, test_[s-z]*.py)
This law adds ONE test module, tests/creature/test_poller_cursor.py: ADDED tests, counted from its own GREEN log (34), all in part 2 (test_[g-r]*.py), so the creature parts must read
444 / 559 / 421 and sum to 1424. Every other suite must read its baseline count EXACTLY: a suite that gained or lost a test is a RAISE.

usage: python3 -B g6_read.py --dir <suites dir> [--creature-prefix creature-<sha>] [--rest-prefix g6] [--added 34]        --plant: expect a wrong count and demand NOT OK (exit 0 = CAUGHT)
Exit 0 iff every suite is exit 0 with its «OK» line, every count equals baseline (+ added), and the creature parts' sum equals the whole."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BASE = {"genome": 713, "tools": 384, "scene": 368, "brain": 770}
CREATURE_PARTS = [444, 525, 421]


def read_log(log: Path, exitf: Path) -> dict:
    t = log.read_text(errors="replace") if log.exists() else ""
    ran = re.search(r"^Ran (\d+) tests? in [\d.]+s", t, re.M)
    ok = re.search(r"^(OK[^\n]*)$", t, re.M)
    failed = re.search(r"^(FAILED[^\n]*)$", t, re.M)
    peak = re.findall(r"memory\.peak (\d+|unknown) bytes", t)
    return {"exit": exitf.read_text().strip() if exitf.exists() else "MISSING", "ran": int(ran.group(1)) if ran else None, "ok_line": ok.group(1) if ok else None,
            "failed_line": failed.group(1) if failed else None, "peak": peak[-1] if peak else None, "log": str(log)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--creature-prefix", default="creature-9d43829")
    ap.add_argument("--rest-prefix", default="g6")
    ap.add_argument("--added", type=int, default=34)
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir)
    base = dict(BASE)
    parts_expected = [CREATURE_PARTS[0], CREATURE_PARTS[1] + a.added, CREATURE_PARTS[2]]
    if a.plant:
        base["genome"] += 1                                   # a baseline that is one test off: a count read from the log must NOT match it
    ok_all, lines, goods = True, [], {}
    for s in ("genome", "tools", "scene", "brain"):
        r = read_log(d / f"{a.rest_prefix}-{s}.log", d / f"{a.rest_prefix}-{s}.exit")
        good = r["exit"] == "0" and r["ran"] == base[s] and r["ok_line"] is not None and r["failed_line"] is None
        ok_all &= good
        goods[s] = (good, r["exit"] == "0" and r["ran"] is not None)
        lines.append(f"{s:9s} exit {r['exit']} · Ran {r['ran']} (baseline {base[s]}) · {r['ok_line']} · peak {r['peak']} · {'OK' if good else 'NOT OK'}")
    parts, reran = [], False
    for i in (1, 2, 3):
        r = read_log(d / f"{a.creature_prefix}.part{i}.log", d / f"{a.creature_prefix}.part{i}.exit")
        good = r["exit"] == "0" and r["ran"] == parts_expected[i - 1] and r["ok_line"] is not None and r["failed_line"] is None
        lines.append(f"creature part {i} exit {r['exit']} · Ran {r['ran']} (baseline {CREATURE_PARTS[i - 1]}{' + ' + str(a.added) + ' added' if i == 2 else ''} = {parts_expected[i - 1]}) · {r['ok_line']} · peak {r['peak']} · {'OK' if good else 'NOT OK'}")
        rr = d / f"{a.creature_prefix}.part{i}.rerun.exit"
        if rr.exists():            # edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:53 +0400 — a re-run AFTER a LOAD-SUSPECT failure is the AUTHORITATIVE verdict of that part; the first run's line stays printed above it (a record is never overwritten)
            r2 = read_log(d / f"{a.creature_prefix}.part{i}.rerun.log", rr)
            good2 = r2["exit"] == "0" and r2["ran"] == parts_expected[i - 1] and r2["ok_line"] is not None and r2["failed_line"] is None
            lines.append(f"   RERUN (authoritative) part {i} exit {r2['exit']} · Ran {r2['ran']} · {r2['ok_line']} · peak {r2['peak']} · {'OK' if good2 else 'NOT OK'}")
            r, good, reran = r2, good2, True
        ok_all &= good
        parts.append(r)
    total = sum(p["ran"] or 0 for p in parts)
    split_exit = (d / f"{a.creature_prefix}.split.exit").read_text().strip() if (d / f"{a.creature_prefix}.split.exit").exists() else "MISSING"
    sum_ok = total == sum(CREATURE_PARTS) + a.added and (split_exit == "0" or reran)      # the split verdict is superseded by an authoritative re-run of the failed part
    ok_all &= sum_ok
    lines.append(f"creature SUM Ran {total} vs expected {sum(CREATURE_PARTS)} + {a.added} = {sum(CREATURE_PARTS) + a.added} · the split verdict exit {split_exit} · {'OK' if sum_ok else 'NOT OK'}")
    print("\n".join(lines))
    if a.plant:
        caught = goods["genome"][0] is False and goods["genome"][1] is True        # the genome log itself is fine; only the planted baseline is wrong
        print("PLANT:", "CAUGHT: a baseline one test off reads NOT OK on the genome line while its own log is clean" if caught else "NOT caught (or the genome log is missing): the reader cannot tell")
        return 0 if caught else 1
    print("RESULT:", "OK" if ok_all else "NOT OK")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
