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
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:51 +0400 — A4L-LANG task 10: a chat `say` row (kind "chat") and a
        # kind-chat grade are counted APART from the think-mouth's `say` and the ask door's grades (#180: two mechanisms, two names).
        if isinstance(d.get("say"), dict) and d["say"].get("kind") == "chat":
            c["chat_say"] += 1
            continue
        if isinstance(d.get("grade"), dict) and d["grade"].get("kind") == "chat":
            c["chat_grade"] += 1
        for k in ("question", "say", "sound", "sit", "sleep", "outcome", "body"):
            if k in d: c[k] += 1
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:59 +0400 — A4L-VOICE: the eye row that BINDS a maker sound carries a
        # `sound` dict ({seq, winners, cells}); it is counted as `sound_bound`, never as a second `sound` (one tape row counted once).
        if isinstance(d.get("sound"), dict) and "winners" in d["sound"]:
            c["sound"] -= 1; c["sound_bound"] += 1
            if c["sound"] == 0: del c["sound"]
    return c


CHAT_KEYS = ("chats", "chat_answered", "chat_abstained", "chat_refused_form", "chat_refused_content", "chat_words_mean",
             "chat_longest", "chat_graded", "chat_graded_right", "chat_graded_novel")


def chat_status_line(status) -> str:
    """edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:51 +0400 — A4L-LANG task 10: STATUS's ten chat keys, «not recorded»
    for a key an older body never wrote (never a fabricated 0)."""
    return "[check] chat: " + " · ".join(f"{k} {status[k]}" if k in status else f"{k} not recorded" for k in CHAT_KEYS)


# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2.6 (A4L-DROP-REPORT task 3): the coarse row (creature/mind.py:_coarse_row)
# writes no `when`, so every coarse row's confirmed flag landed under the EMPTY hour (alpha4-1: the "" bucket read 0.0253 = 46 / 1818,
# exactly the coarse-glance count). Its hour is its sibling canvas row's — the two share the seq (SLEEP's own "second mind row" pattern,
# creature/replay.py groups by it). Fixed HERE only: the journal's bytes stay (M3's regression is INCLUDING hash; a key on the coarse
# row is a format change). A row with neither a `when` nor a sibling keeps the old "" bucket — nothing is invented.
def seq_when(rows) -> dict:
    """seq -> the `when` of the first moment row carrying one under that seq (the canvas row, DELIVER's own field)."""
    out = {}
    for d in rows:
        if "moment" in d and d.get("when") and "seq" in d:
            out.setdefault(d["seq"], d["when"])
    return out


def hour_of(d, by_seq) -> str:
    """The row's hour bucket: its own `when`, else its sibling's (same seq), else "" (the old bucket)."""
    return (d.get("when") or by_seq.get(d.get("seq")) or "")[:13]


def births_by_hour(rows):
    """(hours in first-seen order, {hour: sight births}, {hour: {source: sight births}}) over the moment rows (every glance row counts)."""
    rows = list(rows); by_seq = seq_when(rows)
    hours = []; by_hour = collections.Counter(); by_source = collections.defaultdict(collections.Counter)
    for d in rows:
        if "moment" not in d:
            continue
        h = hour_of(d, by_seq)
        if h not in hours: hours.append(h)
        n = sum(1 for b in d.get("births", []) if b and b[0] == "sight")
        by_hour[h] += n
        if n: by_source[h][d.get("source") or "?"] += n
    return hours, by_hour, {h: dict(v) for h, v in by_source.items()}


def confirmed_share_by_hour(rows):
    """{hour: confirmed glances / graded glances} over the rows carrying `confirmed` (a LIST per glance); an hour with none has no key."""
    rows = list(rows); by_seq = seq_when(rows)
    conf = collections.Counter(); tot = collections.Counter()
    for d in rows:
        if "moment" not in d or "confirmed" not in d:
            continue
        h = hour_of(d, by_seq)   # the coarse row: its canvas row's hour
        flags = d["confirmed"] if isinstance(d["confirmed"], list) else [d["confirmed"]]
        conf[h] += sum(1 for f in flags if f); tot[h] += len(flags)
    return {h: conf[h] / tot[h] for h in tot if tot[h]}


# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2.6 (review §7): the SIZING line under GROW. The 07:38 patch decided
# GROW-vs-NMAX on `status.get("sight_capacity")`, but creature/body.py writes sight_capacity for EVERY body (GROW or not), so the
# «NMAX» branch was dead and «CROSSES NMAX» could never print on a capped genome. The signal is the run's OWN genome text —
# $ROOT/GENOME.genome, which tools/lives/launch.sh copies beside the life — parsed by the machinery's parser (`#OFF GROW` and a
# comment naming GROW are not declarations). Unknown (no parseable file: an older run) reads as NMAX and says so.
def genome_declares_grow(root):
    """True / False from $ROOT/GENOME.genome's declared genes; None when the file is absent or refuses to parse."""
    p = Path(root) / "GENOME.genome"
    if not p.exists():
        return None
    try:
        tree = str(Path(__file__).resolve().parents[2])
        if tree not in sys.path:
            sys.path.insert(0, tree)
        from genome.machinery import parse_genome
        return "GROW" in parse_genome(p.read_text()).declared
    except Exception:
        return None


def sizing_wording(proj, nmax, grow):
    """(cap_kind, crosses): under a declared GROW `sight_nmax` is the CURRENT capacity and passing it means «capacity doubles» (a
    re-allocation, never a refusal); without GROW — or unknown — it is NMAX and passing it is «CROSSES NMAX», a refusal."""
    if grow is True:
        return "capacity (GROW: no cap)", ("capacity doubles (GROW re-allocates: not a refusal)" if proj > nmax else "under capacity")
    kind = "NMAX" if grow is False else "NMAX (GROW unknown: no parseable GENOME.genome at the root)"
    return kind, ("CROSSES NMAX" if proj > nmax else "under " + kind)


# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:12 +0400 — A4-LADDER-2-PREREG ADDENDUM §7(2) item 2: the «MISMATCH: dropped 0 != confirmed N»
# line fired on FLOOR', COST, ACT, LINE and NURSERY — genomes that never declare `; drop confirmed` (only A4L2-ALL does). The body writes
# `glances_dropped 0` on EVERY write (creature/body.py, #164), so the key's presence says nothing about the clause: the comparison is
# gated on the genome's OWN SURPRISE clause (genome.machinery.parse_genome's declared["SURPRISE"]["drop"] == "confirmed", the key
# creature/genes.py RUNS for the drop) read from $ROOT/GENOME.genome (tools/lives/launch.sh's copy), else unit.env's GENOME= path.
def genome_text(root):
    """The run's genome text: $ROOT/GENOME.genome, else the file unit.env's GENOME= names; None when neither is readable."""
    root = Path(root)
    p = root / "GENOME.genome"
    if p.exists():
        try:
            return p.read_text()
        except OSError:
            return None
    env = root / "unit.env"
    if env.exists():
        try:
            for line in env.read_text().splitlines():
                if line.startswith("GENOME="):
                    g = Path(line.split("=", 1)[1].strip())
                    return g.read_text() if g.exists() else None
        except OSError:
            return None
    return None


def drop_declared(root):
    """True / False: the genome declares SURPRISE's `; drop confirmed` clause; None when the genome is absent or refuses to parse."""
    text = genome_text(root)
    if text is None:
        return None
    try:
        tree = str(Path(__file__).resolve().parents[2])
        if tree not in sys.path:
            sys.path.insert(0, tree)
        from genome.machinery import parse_genome
        return (parse_genome(text).declared.get("SURPRISE") or {}).get("drop") == "confirmed"
    except Exception:
        return None


def glances_line(status, declared) -> str:
    """The glances line: MISMATCH only when the genome DECLARES `; drop confirmed` AND dropped != confirmed; «not declared» when it does
    not (dropped 0 is the ordinary reading there); «not recorded» when the body never wrote the key (an older body)."""
    gc, gd = status.get("glances_confirmed"), status.get("glances_dropped")
    if gd is None:
        eq = "not recorded (glances_dropped absent — an older body)"
    elif declared is True:
        eq = "OK: dropped == confirmed (declared: `; drop confirmed`)" if gd == gc else f"MISMATCH: dropped {gd} != confirmed {gc} (the genome declares `; drop confirmed`)"
    elif declared is False:
        eq = "not declared (no `; drop confirmed` in the genome; dropped 0 is the ordinary reading)"
        if gd != 0:
            eq += f" — UNEXPECTED: dropped {gd} under an undeclared clause (an undeclared drop must never drop a glance)"
    else:
        eq = "genome unknown (no parseable GENOME.genome / unit.env genome at the root): the drop clause not read, dropped vs confirmed not compared"
    return (f"[check] glances confirmed {status.get('glances_confirmed', 'not recorded')} "
            f"surprised {status.get('glances_surprised', 'not recorded')} dropped {status.get('glances_dropped', 'not recorded')} — {eq}")


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--hours", type=float, default=8.0)
    a = ap.parse_args(argv); root = Path(a.root)
    status = json.load(open(root / "STATUS.json")) if (root / "STATUS.json").exists() else {}
    print(f"[check] root {root} · STATUS moments {status.get('moments')} cells {status.get('cells')} crash {status.get('crash')} "
          f"backlog {status.get('mind_backlog_rows', 'not recorded')} sight_born {status.get('sight_born', 'not recorded')}/{status.get('sight_nmax', '?')} "
          f"refused nmax {status.get('births_refused_nmax', 'not recorded')} budget {status.get('births_refused_budget', 'not recorded')}")
    print(chat_status_line(status))   # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:51 +0400 — A4L-LANG task 10
    # edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md §2.4
    # (docs/briefs/A4L-DROP.md task 5): "STATUS gains glances_dropped ... it must equal glances_confirmed
    # on the live record while the clause is declared: that equality is a live check the 8 h check.py
    # reads" — printed here (read-only, no assertion: check.py never raises on a live root, #164's law
    # applied to a read). "not recorded" on a genome/body that predates this task.
    print(glances_line(status, drop_declared(root)))   # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:12 +0400 — gated on the genome's own clause (ADDENDUM §7(2) item 2)
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
        cap_kind, crosses = sizing_wording(proj, nmax, genome_declares_grow(root))   # Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400: the genome's own declaration, never STATUS.sight_capacity (written for every body)
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
        # A4L-VOICE (Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:59 +0400): the exam by sound, when the genome has the area —
        # the 16-thing marks and the scores over the things the world has voiced (a 20-min pre-flight voices window 0's eleven only).
        snd = e.get("ask_sound")
        if isinstance(snd, dict):
            def _acc(b):
                return None if not isinstance(b, dict) or b.get("acc") is None else round(float(b["acc"]), 3)
            print(f"[check] ask_sound: V1 {_acc(snd.get('V1'))} V2 {_acc(snd.get('V2'))} V5 {_acc(snd.get('V5'))} · on the voiced "
                  f"{len(snd.get('voiced_things') or [])}: V1 {_acc(snd.get('V1_on_voiced'))} V2 {_acc(snd.get('V2_on_voiced'))} V5 {_acc(snd.get('V5_on_voiced'))}"
                  f" · V1b {json.dumps({k: (v or {}).get('correct') for k, v in (snd.get('V1b') or {}).items()})} · {snd.get('reason')}")
    if status.get("sound_born") is not None:
        print(f"[check] voice: sound_born {status.get('sound_born')} alive {status.get('sound_cells')} refused {status.get('sound_births_refused')} "
              f"· voice rows {status.get('voice_rows')} bound {status.get('voice_bound')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
