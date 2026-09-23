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


# edit: Claude (Fable 5.1), 2026-09-22 22:27 +0400 — the counters as FUNCTIONS (tests/creature/test_lives_check.py, RED first) against the journal
# shapes the builders LANDED: builder D's game act is a DICT under `act` (the moment rows' `act` is the STRING glance/coarse), builder F's
# hands run is `act_chosen`, builder A's self beliefs are think rows of kind `self`, builder B's `confirmed` is a LIST per located glance
# (a share counts GLANCES, never rows — a list is truthy whether or not one glance confirmed). Sight births split by the row's `source`:
# the input of PREREG §19.11's sizing rule (the game's share scales with its cadence; the maker's does not).
def journal_counts(rows) -> collections.Counter:
    c = collections.Counter()
    for d in rows:
        if "event" in d:
            continue
        if "moment" in d:
            c["moments"] += 1
            if d.get("glance") == 0: c["canvases"] += 1
        if d.get("act") == "coarse": c["coarse_rows"] += 1
        if isinstance(d.get("act"), dict): c["acts_game"] += 1
        if "act_chosen" in d: c["hands_runs"] += 1
        if isinstance(d.get("think"), dict):
            c["think"] += 1
            if d["think"].get("kind") == "self": c["self_thinks"] += 1
        for k in ("question", "say", "sound", "sit", "sleep", "outcome", "body"):
            if k in d: c[k] += 1
    return c


def births_by_hour(rows):
    """(hours in first-seen order, {hour: sight births}, {hour: {source: sight births}}) over the moment rows (every glance row counts)."""
    hours = []; by_hour = collections.Counter(); by_source = collections.defaultdict(collections.Counter)
    for d in rows:
        if "moment" not in d:
            continue
        h = (d.get("when") or "")[:13]
        if h not in hours: hours.append(h)
        n = sum(1 for b in d.get("births", []) if b and b[0] == "sight")
        by_hour[h] += n
        if n: by_source[h][d.get("source") or "?"] += n
    return hours, by_hour, {h: dict(v) for h, v in by_source.items()}


def confirmed_share_by_hour(rows):
    """{hour: confirmed glances / graded glances} over the rows carrying `confirmed` (a LIST per glance); an hour with none has no key."""
    conf = collections.Counter(); tot = collections.Counter()
    for d in rows:
        if "moment" not in d or "confirmed" not in d:
            continue
        h = (d.get("when") or "")[:13]
        flags = d["confirmed"] if isinstance(d["confirmed"], list) else [d["confirmed"]]
        conf[h] += sum(1 for f in flags if f); tot[h] += len(flags)
    return {h: conf[h] / tot[h] for h in tot if tot[h]}


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--hours", type=float, default=8.0)
    a = ap.parse_args(argv); root = Path(a.root)
    status = json.load(open(root / "STATUS.json")) if (root / "STATUS.json").exists() else {}
    print(f"[check] root {root} · STATUS moments {status.get('moments')} cells {status.get('cells')} crash {status.get('crash')} "
          f"backlog {status.get('mind_backlog_rows', 'not recorded')} sight_born {status.get('sight_born', 'not recorded')}/{status.get('sight_nmax', '?')} "
          f"refused nmax {status.get('births_refused_nmax', 'not recorded')} budget {status.get('births_refused_budget', 'not recorded')}")
    # edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md §2.4
    # (docs/briefs/A4L-DROP.md task 5): "STATUS gains glances_dropped ... it must equal glances_confirmed
    # on the live record while the clause is declared: that equality is a live check the 8 h check.py
    # reads" — printed here (read-only, no assertion: check.py never raises on a live root, #164's law
    # applied to a read). "not recorded" on a genome/body that predates this task.
    gc, gd = status.get("glances_confirmed"), status.get("glances_dropped")
    eq = "not recorded (glances_dropped absent — an older body, or the clause is undeclared)" if gd is None \
        else ("OK: dropped == confirmed" if gd == gc else f"MISMATCH: dropped {gd} != confirmed {gc}")
    print(f"[check] glances confirmed {status.get('glances_confirmed', 'not recorded')} "
          f"surprised {status.get('glances_surprised', 'not recorded')} dropped {status.get('glances_dropped', 'not recorded')} — {eq}")
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
    # 2. the journal: sight births per hour (by source), confirmed shares (per glance), the landed shapes' counts
    rows = [d for f in sorted(glob.glob(str(root / "journal" / "*.jsonl"))) for d in _jsonl(f)]
    hours, births, by_source = births_by_hour(rows)
    canv = collections.Counter((d.get("when") or "")[:13] for d in rows if "moment" in d and d.get("glance") == 0)
    share = confirmed_share_by_hour(rows); counts = journal_counts(rows)
    print(f"[check] sight births/h: {[births[h] for h in hours]}")
    print(f"[check] sight births/h by source: " + " · ".join(f"{h[11:13]}h {by_source.get(h, {})}" for h in hours))
    print(f"[check] canvases/h:     {[canv[h] for h in hours]}")
    print(f"[check] confirmed share/h (glances): {[round(share[h], 3) if h in share else None for h in hours]}" + ("" if share else "   (SURPRISE not journaled on this genome — not recorded)"))
    print(f"[check] journal counts: {dict(counts)}")
    # 3. the sizing projection (PREREG §19.11): the mean births/h over the last 3 full hours × the hours left
    full = hours[1:-1] if len(hours) > 2 else hours
    rate = (sum(births[h] for h in full[-3:]) / max(1, len(full[-3:]))) if full else 0.0
    born = status.get("sight_born"); nmax = status.get("sight_nmax")
    if isinstance(born, int) and isinstance(nmax, int):
        left_h = max(0.0, 24.0 - len(hours)); proj = born + rate * left_h
        proj21 = born + rate * max(0.0, 21.0 - len(hours))   # the plant's hour (PREREG §19.11)
        cap_kind = "capacity (GROW: no cap)" if status.get("sight_capacity") is not None else "NMAX"
        crosses = ("grows past the current capacity (GROW re-allocates: not a refusal)" if cap_kind.startswith("capacity") else "CROSSES NMAX") if proj > nmax else "under " + cap_kind
        print(f"[check] SIZING: born {born} of {nmax} {cap_kind}; rate (last 3 full h) {rate:.0f}/h; projection at 24 h ≈ {proj:.0f} → {crosses} (the plant needs room at hour ≈ 21: {proj21:.0f})")   # edit: Claude (Fable 5.1), 2026-09-23 07:38 +0400 — under GROW STATUS.sight_nmax is the CURRENT capacity, never a cap: the wording said «CROSSES NMAX» on alpha4-1 at 2 h
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
