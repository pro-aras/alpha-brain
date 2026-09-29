#!/usr/bin/env python3
# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:45 +0400 — his 23:20 word («make sure to clear any possible errors that might occur within
# these few days»): THE HEALTH WATCH of a days-long life, run every 20 min and at boot by creature-brain-health@<name>.timer.
"""tools/lives/health.py --root <life root> --unit <unit> [--recover] [--sleep-ab <runs2 dir>]

Writes <root>/HEALTH.md (overwritten: the state NOW, and every PROBLEM it sees, in plain words) and appends one line to
<root>/HEALTH.jsonl (the history). It reads; with --recover it may also act, and every act is one line of <root>/RECOVERY.log:
  - the life's unit FAILED (it gave up after 5 starts in 10 minutes) or is inactive while its root is not closed → `reset-failed` + `start`,
    at most 4 times in any 24 hours;
  - the unit active but its heartbeat older than 90 minutes (frozen) → `restart`, at most once in 6 hours (and within the 4 a day);
  - the unit active, its heartbeat fresh, but its moments and last_seq unchanged across an hour of watches (a STUCK mind: the heartbeat
    is the body's own status thread, so a hung mind thread keeps it fresh) → `restart`, sharing the once-in-6-hours with «frozen».
It never acts on a CLOSED life (STOPPED-AT). It never raises: a check that fails is itself reported."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MAX_RECOVERIES_24H = 4
FROZEN_S = 90 * 60
FROZEN_GAP_S = 6 * 3600
STALE_S = 15 * 60
STUCK_S = 60 * 60       # edit: Claude (Opus 5.5, the seat), 2026-09-30 00:16 +0400 — no motion for an hour = a stuck mind (a calibration at
                        # 20,000 scenes paused learning 0.3 s on brain-long-1; the clock worlds publish every 10–60 s, so a healthy mind moves)
HISTORY_ROWS = 12       # the watches read back from HEALTH.jsonl (four hours at 20 min)


def sh(*a):
    try:
        return subprocess.run(list(a), capture_output=True, text=True, timeout=60)
    except Exception as e:                                   # pragma: no cover
        return subprocess.CompletedProcess(a, 99, "", repr(e))


def unit_show(unit):
    r = sh("systemctl", "--user", "show", unit, "-p", "ActiveState", "-p", "SubState", "-p", "NRestarts", "-p", "Result",
           "-p", "MemoryCurrent", "-p", "UnitFileState")
    out = {}
    for line in r.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


def iso_age_s(s):
    try:
        t = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - t).total_seconds()
    except Exception:
        return None


def read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def last_line(p):
    try:
        lines = [l for l in Path(p).read_text().splitlines() if l.strip()]
        return lines[-1] if lines else None
    except Exception:
        return None


def parse_at(s):
    """A watch's own `at` (HEALTH.jsonl, "%Y-%m-%d %H:%M:%S %z") as epoch seconds; None when it cannot be read."""
    try:
        return datetime.strptime(str(s), "%Y-%m-%d %H:%M:%S %z").timestamp()
    except Exception:
        return None


def recent_rows(p, n=HISTORY_ROWS) -> list:
    """The last n watches of HEALTH.jsonl, oldest first; an unreadable line is skipped."""
    out = []
    try:
        lines = [l for l in Path(p).read_text().splitlines() if l.strip()][-n:]
    except Exception:
        return out
    for l in lines:
        try:
            out.append(json.loads(l))
        except Exception:
            continue
    return out


def stuck_since(rows, moments, last_seq, now_t):
    """Seconds since the OLDEST watch of the unbroken recent run that saw the same moments and last_seq as now; None when the mind moved
    since the last watch, when there is no history, or when the position is unread (an unread STATUS is never «no motion»)."""
    if moments is None or last_seq is None:
        return None
    oldest = None
    for r in reversed(rows):
        if r.get("moments") != moments or r.get("last_seq") != last_seq:
            break
        t = parse_at(r.get("at"))
        if t is None:
            break
        oldest = t
    return None if oldest is None else max(0.0, now_t - oldest)


def recover(root: Path, unit: str, problems, st_unit, hb_age, stuck_s=None) -> list:
    acts = []
    if (root / "STOPPED-AT").exists():
        return acts
    rec_path = root / "RECOVERY.json"
    rec = read_json(rec_path) or {"acts": []}
    now = time.time()
    recent = [a for a in rec["acts"] if now - a["at"] < 24 * 3600]
    last_frozen = max([a["at"] for a in rec["acts"] if a.get("why") in ("frozen", "no motion")] or [0])
    active = st_unit.get("ActiveState")
    why = None
    if active == "failed" or (active == "inactive" and st_unit.get("UnitFileState") == "enabled"):
        why = f"unit {active}"
        cmds = [["systemctl", "--user", "reset-failed", unit], ["systemctl", "--user", "start", unit]]
    elif active == "active" and hb_age is not None and hb_age > FROZEN_S and now - last_frozen > FROZEN_GAP_S:
        why = "frozen"
        cmds = [["systemctl", "--user", "restart", unit]]
    elif active == "active" and stuck_s is not None and stuck_s >= STUCK_S and now - last_frozen > FROZEN_GAP_S:
        why = "no motion"               # edit: Claude (Opus 5.5, the seat), 2026-09-30 00:16 +0400 — a hung mind thread keeps the heartbeat fresh
        cmds = [["systemctl", "--user", "restart", unit]]
    if why is None:
        return acts
    if len(recent) >= MAX_RECOVERIES_24H:
        problems.append(f"RECOVERY REFUSED: {why}, but {len(recent)} recoveries in the last 24 h already (the cap is {MAX_RECOVERIES_24H})")
        return acts
    results = [sh(*c) for c in cmds]
    entry = {"at": now, "when": datetime.now(timezone.utc).isoformat(timespec="seconds"), "why": why,
             "cmds": [" ".join(c) for c in cmds], "exits": [r.returncode for r in results],
             "stderr": [r.stderr.strip()[-300:] for r in results]}
    rec["acts"] = (recent + [entry])[-50:]
    try:
        rec_path.write_text(json.dumps(rec, indent=1))
        with (root / "RECOVERY.log").open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    acts.append(entry)
    return acts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--unit", required=True)
    ap.add_argument("--recover", action="store_true")
    ap.add_argument("--sleep-ab", default="/data/dev/brain-runs/day0929/sleep-ab/runs2")
    a = ap.parse_args(argv)
    root = Path(a.root)
    problems, facts = [], {}
    now_s = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    try:
        st_unit = unit_show(a.unit)
    except Exception as e:
        st_unit = {}
        problems.append(f"could not read the unit: {e!r}")
    facts["unit"] = st_unit
    closed = (root / "STOPPED-AT").exists()
    s = read_json(root / "STATUS.json") or {}
    hb_age = iso_age_s(s.get("heartbeat_at")) if s else None
    prev = None
    hist = root / "HEALTH.jsonl"
    try:
        pl = last_line(hist)
        prev = json.loads(pl) if pl else None
    except Exception:
        prev = None
    try:
        stuck_s = stuck_since(recent_rows(hist), s.get("moments"), s.get("last_seq"), time.time()) if s else None
    except Exception:
        stuck_s = None
    facts["stuck_s"] = stuck_s
    keys = ("moments", "tape_rows", "last_seq", "mind_backlog_rows", "mind_ms_per_canvas_1min", "rss_mb", "cells", "crash",
            "sense_restarts", "hash_form", "hash_ms_last", "think_ms_median", "stage")
    for k in keys:
        facts[k] = s.get(k)
    br = s.get("brain") or {}
    facts["brain"] = {k: br.get(k) for k in ("learned", "calibrations", "words", "mature", "asks_answered", "restored")}
    facts["web"] = br.get("web")
    facts["web_error"] = br.get("web_error")
    facts["self"] = (br.get("self") or {}).get("claims")
    facts["scene"] = s.get("scene")
    facts["heartbeat_age_s"] = hb_age
    try:
        du = shutil.disk_usage(str(root))
        facts["disk_free_gb"] = round(du.free / 2 ** 30, 1)
    except Exception:
        facts["disk_free_gb"] = None
    try:
        mem = {l.split(":")[0]: int(l.split()[1]) for l in open("/proc/meminfo") if l.split(":")[0] in ("MemAvailable", "SwapFree", "SwapTotal")}
        facts["mem_available_gb"] = round(mem["MemAvailable"] / 2 ** 20, 1)
        facts["swap_used_gb"] = round((mem["SwapTotal"] - mem["SwapFree"]) / 2 ** 20, 1)
        facts["load"] = open("/proc/loadavg").read().split()[:3]
    except Exception:
        pass
    try:
        reps = [l for l in (root / "repairs" / "REPAIRS.jsonl").read_text().splitlines() if l.strip()] if (root / "repairs" / "REPAIRS.jsonl").exists() else []
        facts["repairs"] = len(reps)
        facts["last_repair"] = json.loads(reps[-1]) if reps else None
    except Exception:
        facts["repairs"] = None
    page = read_json(root / "PAGE.json")
    facts["page"] = page
    try:
        sab = Path(a.sleep_ab)
        facts["sleep_ab"] = {"done": (sab / "DONE").exists(), "last_tick": (last_line(sab / "TICKS.log") or "")[:400],
                             "reading": (sab / "READING.txt").exists()}
    except Exception:
        facts["sleep_ab"] = None
    # the PROBLEMS, in plain words
    if closed:
        problems.append("the life is CLOSED (STOPPED-AT): nothing is watched or recovered")
    else:
        if st_unit.get("ActiveState") != "active":
            problems.append(f"the life is NOT RUNNING: its unit is {st_unit.get('ActiveState')} ({st_unit.get('Result')})")
        if hb_age is not None and hb_age > STALE_S:
            problems.append(f"its heartbeat is {hb_age / 60:.0f} minutes old")
        if prev and prev.get("moments") is not None and s.get("moments") == prev.get("moments") and s.get("tape_rows") == prev.get("tape_rows"):
            problems.append("no motion since the last watch (moments and tape rows unchanged)")
        if stuck_s is not None and stuck_s >= STUCK_S:
            problems.append(f"no motion for {stuck_s / 60:.0f} minutes (moments {s.get('moments')}, last_seq {s.get('last_seq')}, "
                            f"backlog {s.get('mind_backlog_rows')}): a stuck mind")
        if (s.get("mind_backlog_rows") or 0) > 500:
            problems.append(f"the mind is {s.get('mind_backlog_rows')} rows behind its senses")
        if (s.get("rss_mb") or 0) > 14000:
            problems.append(f"its memory is {s.get('rss_mb'):.0f} MB (the fence slows it at 16 GB and stops it at 20 GB)")
        if s.get("crash"):
            problems.append(f"a crash is recorded: {str(s.get('crash'))[:200]}")
        if facts.get("web_error"):
            problems.append(f"the knowledge web switched itself off: {facts['web_error'][:200]}")
        try:        # edit: Claude (Opus 5.5, the seat), 2026-09-30 00:17 +0400 — an INCREASE only: `reset-failed` (the watch's own act, or a close) sets it to 0
            n_now, n_prev = int(st_unit.get("NRestarts")), int(((prev or {}).get("unit") or {}).get("NRestarts"))
        except (TypeError, ValueError):
            n_now = n_prev = None
        if n_now is not None and n_now > n_prev:
            problems.append(f"the unit restarted since the last watch (NRestarts {n_prev} → {n_now})")
        if prev and facts.get("repairs") is not None and prev.get("repairs") is not None and facts["repairs"] > prev["repairs"]:
            problems.append(f"a power-cut repair ran at a start ({facts['repairs'] - prev['repairs']} new; see repairs/REPAIRS.jsonl)")
        if page:
            problems.append(f"the watch paged: {str(page)[:200]}")
    if facts.get("disk_free_gb") is not None and facts["disk_free_gb"] < 50:
        problems.append(f"the disk has {facts['disk_free_gb']} GB free")
    if facts.get("mem_available_gb") is not None and facts["mem_available_gb"] < 3:
        problems.append(f"the box has {facts['mem_available_gb']} GB of memory available")
    acts = []
    if a.recover:
        try:
            acts = recover(root, a.unit, problems, st_unit, hb_age, stuck_s=stuck_s)
        except Exception as e:
            problems.append(f"the recovery step failed: {e!r}")
    facts["problems"] = problems
    facts["acts"] = acts
    facts["at"] = now_s
    try:
        with hist.open("a") as f:
            f.write(json.dumps(facts, default=str) + "\n")
    except Exception:
        pass
    L = [f"# HEALTH of {root.name} — {now_s}", "",
         ("**No problem seen.**" if not problems else "**PROBLEMS:**"), *[f"- {p}" for p in problems],
         *([f"- ACTED: {x['why']} → {x['cmds']} exits {x['exits']}" for x in acts]), "",
         f"- unit: {st_unit.get('ActiveState')} / {st_unit.get('SubState')}, restarts {st_unit.get('NRestarts')}, memory {st_unit.get('MemoryCurrent')}",
         f"- heartbeat {('%.0f s' % hb_age) if hb_age is not None else 'none'} ago · moments {s.get('moments')} · tape rows {s.get('tape_rows')} · "
         f"backlog {s.get('mind_backlog_rows')} · {s.get('mind_ms_per_canvas_1min')} ms a canvas · {s.get('rss_mb')} MB · cells {s.get('cells')} · hash {s.get('hash_form')}",
         f"- brain: {facts['brain']} · scene: {facts['scene']}",
         f"- knowledge web: {facts['web']} · error {facts['web_error']}",
         f"- self claims [state, confirmed, contradicted]: {facts['self']}",
         f"- repairs at starts: {facts.get('repairs')} · disk free {facts.get('disk_free_gb')} GB · memory available {facts.get('mem_available_gb')} GB · "
         f"swap used {facts.get('swap_used_gb')} GB · load {facts.get('load')}",
         f"- the sleep A/B: {facts.get('sleep_ab')}"]
    try:
        (root / "HEALTH.md").write_text("\n".join(L) + "\n")
    except Exception:
        pass
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
