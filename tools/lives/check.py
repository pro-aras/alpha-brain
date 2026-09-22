#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-22 18:27 +0400 — THE 8 h CHECK of the ONE life (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §6; PREREG §19):
# reads a LIVE life WITHOUT replaying it (no worker, no reader beside the life — #236): the body rows on the tape (the STATUS series),
# the journal (sight births per hour, confirmed shares, questions, frames, acts, thinks), the exam files (Q1–Q5 per thing, the misses),
# and prints the sizing projection against NMAX. Read-only; never opens the mind's state. usage: check.py --root <root> [--hours 8]
"""The 8 h CHECK: STATUS series + journal + exam files, no replay."""
from __future__ import annotations
import argparse, collections, glob, json, os, sys
from pathlib import Path


def _jsonl(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue   # a torn trailing line on a live file


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--hours", type=float, default=8.0)
    a = ap.parse_args(argv); root = Path(a.root)
    status = json.load(open(root / "STATUS.json")) if (root / "STATUS.json").exists() else {}
    print(f"[check] root {root} · STATUS moments {status.get('moments')} cells {status.get('cells')} crash {status.get('crash')} "
          f"backlog {status.get('mind_backlog_rows', 'not recorded')} sight_born {status.get('sight_born', 'not recorded')}/{status.get('sight_nmax', '?')} "
          f"refused nmax {status.get('births_refused_nmax', 'not recorded')} budget {status.get('births_refused_budget', 'not recorded')}")
    # 1. the body rows on the tape = the STATUS series (every 60 s)
    body = []
    for f in sorted(glob.glob(str(root / "tape" / "*.jsonl"))):
        for r in _jsonl(f):
            if r.get("sense") == "body":
                m = (r.get("meta") or {}).get("reading") or {}
                body.append((r.get("at", ""), m))
    print(f"[check] body rows on the tape: {len(body)}" + ("" if body else " (not recorded — the body sense is not on this genome)"))
    if body:
        keys = sorted({k for _, m in body for k in m if isinstance(m.get(k), (int, float))})
        per_hour = collections.OrderedDict()
        for at, m in body:
            per_hour.setdefault(at[:13], m)      # the LAST reading of each hour wins (overwritten in order)
        print("[check] hour-end readings: " + " · ".join(f"{h[11:13]}h " + ",".join(f"{k}={per_hour[h].get(k)}" for k in keys if k in ("births", "budget_left", "refused", "backlog", "mind_ms")) for h in per_hour))
    # 2. the journal: sight births per hour, confirmed shares, questions, says, acts, thinks, self beliefs
    births = collections.Counter(); canv = collections.Counter(); conf = collections.Counter(); moms = collections.Counter()
    counts = collections.Counter(); hours = []
    for f in sorted(glob.glob(str(root / "journal" / "*.jsonl"))):
        for d in _jsonl(f):
            if "moment" in d:
                h = (d.get("when") or "")[:13]
                if h not in hours: hours.append(h)
                births[h] += sum(1 for b in d.get("births", []) if b and b[0] == "sight")
                moms[h] += 1
                if d.get("glance") == 0: canv[h] += 1
                if d.get("confirmed"): conf[h] += 1
            for k in ("think", "question", "say", "act_chosen", "sound", "sit", "sleep", "outcome", "body", "self"):
                if k in d: counts[k] += 1
            if "think" in d and (d["think"] or {}).get("kind") == "self": counts["self_thinks"] += 1
    print(f"[check] sight births/h: {[births[h] for h in hours]}")
    print(f"[check] canvases/h:     {[canv[h] for h in hours]}")
    print(f"[check] confirmed share/h: {[round(conf[h] / moms[h], 3) if moms[h] else None for h in hours]}" + ("" if any(conf.values()) else "   (SURPRISE not journaled on this genome — not recorded)"))
    print(f"[check] journal counts: {dict(counts)}")
    # 3. the sizing projection (PREREG §19.11): the mean births/h over the last 3 full hours × the hours left
    full = hours[1:-1] if len(hours) > 2 else hours
    rate = (sum(births[h] for h in full[-3:]) / max(1, len(full[-3:]))) if full else 0.0
    born = status.get("sight_born"); nmax = status.get("sight_nmax")
    if isinstance(born, int) and isinstance(nmax, int):
        left_h = max(0.0, 24.0 - len(hours)); proj = born + rate * left_h
        print(f"[check] SIZING: born {born} of {nmax}; rate (last 3 full h) {rate:.0f}/h; projection at 24 h ≈ {proj:.0f} → {'CROSSES NMAX' if proj > nmax else 'under NMAX'} (the plant needs room at hour ≈ 21: {born + rate * max(0.0, 21.0 - len(hours)):.0f})")
    else:
        print("[check] SIZING: sight_born/sight_nmax not recorded on STATUS (an older body)")
    # 4. the exam files: the newest, Q1–Q5 and the per-thing misses
    exams = sorted(p for p in glob.glob(str(root / "exam" / "*.json")) if not p.endswith("LAST.json"))   # digit-prefixed, never the pointer
    print(f"[check] exam files: {len(exams)}")
    if exams:
        e = json.load(open(exams[-1]))
        for side in ("ask_seen_words", "ask_all_words"):
            asks = e.get(side) or {}
            line = " ".join(f"{q} {asks[q].get('acc'):.3f}" for q in ("Q1", "Q2", "Q3", "Q4") if q in asks and asks[q].get("acc") is not None)
            print(f"[check] {os.path.basename(exams[-1])} {side}: {line}  Q1 abstain {(asks.get('Q1') or {}).get('abstain')}  hedge {(asks.get('Q1') or {}).get('hedge_rate', 'not recorded')}")
        per = ((e.get("ask_all_words") or {}).get("Q1") or {}).get("per")
        if per: print("[check] Q1 per thing [correct, asked]: " + " · ".join(f"{t} {v}" for t, v in sorted(per.items())))
        q5 = ((e.get("ask_all_words") or {}).get("Q5") or {})
        for name, v in q5.items(): print(f"[check] Q5 {name}: {json.dumps(v)[:240]}")
        comp = (e.get("ask_all_words") or {}).get("composite")
        if comp: print(f"[check] composite: {json.dumps(comp)[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
