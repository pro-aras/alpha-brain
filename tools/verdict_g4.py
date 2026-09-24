#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-20 12:35 +0400 — THE VERDICT READER for G4 (docs/G4-PREREG.md §5 as amended by §10, §12, §14, §15, §16).
# Written BEFORE the verdict exists (#158/#214: the reader is pre-registered; its rules are §16), dry-run on life 1's CLOSED
# root as its control (life 1's known defects must show: (iv) refused 435, (vi) unreadable). Read-only on every root (#212):
# the tape is concatenated into --out, the state is COPIED, every twin lives in its own fresh root under --out.
"""usage: python3 tools/verdict_g4.py --root <run root> --genome genome/G4.genome --out runs/g4-verdict-<stamp>
          [--hours 24] [--random 20] [--slice-hours 6] [--regime-step 100] [--workers 8] [--nrestarts N] [--cpu-ns N] [--unit creature.service]
          [--skip-twins] [--skip-random] [--identity-root <closed root> [--identity-hours H]] [--control-root <R0's closed root>] [--line-ceiling F]
       python3 tools/verdict_g4.py --worker <spec.json>            (one twin: replay -> snapshot -> self-exam -> summary.json)
"""
from __future__ import annotations
import argparse, json, os, shutil, statistics, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np

# edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400 — L-4/L-7 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
# §4): "coarse" (drops the fifth, whole-canvas glance from the mind's own learning road — Mind._consume_eye
# strips it from org_feats and writes no coarse journal row) and "surprise" (floor -1: residual/confirmed are
# STILL computed and journaled — a twin to compare the CONFIRM mechanism's effect against, never a twin blind
# to the computation itself) beside the six existing blinds. Neither gene needs to be declared for its blind
# to be harmless (Mind gates every use of self.blind on the gene's OWN presence first).
BLINDS = ["gaze", "sleep", "predict", "curiosity", "park", "frozen", "coarse", "surprise"]
REUSE = False   # --reuse: read existing twin summaries under --out instead of replaying them
WINDOW_SECONDS = 6 * 3600


# edit: Claude (Fable 5.1), 2026-09-22 18:29 +0400 — v3.2 (PREREG §19 / the plan's L-1, Appendix A «what is owed»): the version string names the reader that
# read a record (v3.1 never bumped it — every verdict-8h-v31/results.json said v3); `hash` is a DECLARED volatile field of the vs-live
# comparison only when the reader's commit is not the life's (a live journal is a record of the code it loaded — #234; life 3b's REPLAY
# FAIL at 16:49 was a cross-version hash); the two-replays comparison never masks anything.
# edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — v3.3: READER-FIX-0923's eleven fixes (the third hand's review of alpha4-1 §3/§6 +
# the seat's three from the 2 h smoke), every one reader-only; the mind, the senses and the body untouched.
# edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — v3.4: READER-LAG-0923 — the read is of the life the MIND lived. alpha4-1 crossed
# its saturation line (2,433 ms a canvas at 7,030 cells at 16:05 against a world of ≈ 0.456 canvases/s); at its stop the body leaves the
# queue unread, so the live journal ends thousands of rows before the tape's head, and v3.3 replayed rows the mind never lived (REPLAY
# `<missing from --against>`, `closed_whole` False, every tape mark counting world rows past the mind). Reader-only; the mind, the senses and
# the body untouched.
# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:08 +0400 — v3.5: THE RECONCILIATION (docs/briefs/READER-V35-REPORT.md): master's v3.4 (READER-LAG-0923,
# the read CUT at the mind's last consumed seq) merged with a4-integration's v3.3-line ladder additions (A4L-VOICE's twins and HEAR/VOICE_HARM/
# SOUND_CELLS, A4L-LANG's blind-chat twin and CHAT L1-L9, A4L-COST's HASH and the witness beside COST) — both sides kept whole, the three
# conflicting hunks (this header, the COST dict, the COST row) resolved additively.
# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:34 +0400 — v3.5 step 3: the ladder-2 marks named in the version string (A4-LADDER-2-PREREG §2 + ADDENDUM §7(2)).
READER_VERSION = ("tools/verdict_g4.py v3.5 (2026-09-24: v3.4 + a4-integration's ladder marks + READER-V35's ladder-2 marks — IDENTITY per source stream and at "
                  "equal per-source canvas counts (--identity-root; the wall-clock band printed), X1_LOCK/X2_SUCCESS wired (+ the window and the census with "
                  "the got-presence count), LINE from the scorer's own ledger (predictions.jsonl + STATUS, never the journal), NURSERY/NURSERY_READ vs R0 "
                  "(--control-root), DROP_EQ, CHAT_COUNTERS, ANSWER's A1_NULL/A2_SEEN wired; A4L-VOICE's voice twins blind-ear/blind-sound/T-shuffle-sound "
                  "when AREA sound is declared and the marks HEAR/VOICE_HARM/SOUND_CELLS; A4L-LANG's blind-chat twin and CHAT L1-L9; A4L-COST's HASH mark "
                  "and the per-row witness's form and ms beside COST; v3.4: "
                  "READER-LAG-0923 — the read is CUT at the mind's last consumed seq when the mind is "
                  "behind its world (ledger/STATUS last_seq, the journal's last mind row on a closed record): every twin replays the cut tape, "
                  "closed_whole is judged against the cut, every mark reads the cut; ALIVE reads the world's hours and gaps, the mind's counters over "
                  "the hours it lived; the unconsumed tail printed under ALIVE, COST and REPLAY; v3.3: EVOLVE's void round apart; COST as §8b's "
                  "function of cells; ACT's census over the game's acts, ≥ 95 % on the last 100; SENTENCE's missions per episode; QUESTION once per "
                  "question, the lexicon counted; READ's fixed-seed sample of shelf-only words + its blind twin; THREAD's gaps attributed to sleeps; "
                  "STAGE's readiness series + the mind's stage events carried; not gradable never failed; the plant clauses not gradable before the plant)")


def _git_head(tree) -> "str | None":
    try:
        import subprocess
        return subprocess.check_output(["git", "-C", str(tree), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip() or None
    except Exception:
        return None


def _life_commit(root) -> "str | None":
    """The commit a life LIVED on: its root's CODE-COMMIT (the seam lives, written by tools/lives/launch.sh) or its own checkout's HEAD;
    None when neither exists (the G4 lives under /data/dev/genome ran on master at a commit the register names, not the root)."""
    root = Path(root)
    f = root / "CODE-COMMIT"
    if f.exists():
        v = f.read_text().strip()
        return _git_head(root / "code") or v if (root / "code").exists() else v
    if (root / "code").exists():
        return _git_head(root / "code")
    return None


def replay_ignore_fields(reader_commit, life_commit, has_m1=None) -> set:
    """PURE: the fields the vs-live comparison masks. Same commit (both known, equal, or one a prefix of the other) → none; else {"hash"}.

    edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 07:04 +0400 — READER v3.5, the merge's own consequence: a4-integration's M1 (the readiness judge in its
    own units, judge-units-0923 `M1_JUDGE_UNITS_COMMIT`) changed the FORM of every `readiness` row (numbers for booleans), and this reader now carries
    it, so a pre-M1 life (alpha4-1, ladder 1) replayed under it differs in `readiness` on every judge row by construction — measured on a4l-cost's
    closed 8 h tape: `readiness` is the ONLY differing field besides `hash` (36 of 36 judge rows; 0 row-count mismatches over 31,964 rows).
    A4-LADDER-2-PREREG §2 declares M1 a machinery difference of the whole ladder and §3 compares across it «masked on `readiness` with the
    judge-units commit named beside the mask». `has_m1(commit) -> True/False/None` (git ancestry); `readiness` is added iff it PROVES exactly one
    side carries M1 (an unknown ancestry masks nothing — REPLAY then reads the difference, loudly); None = the v3.2 rule, unchanged."""
    if reader_commit and life_commit and (reader_commit == life_commit or reader_commit.startswith(life_commit) or life_commit.startswith(reader_commit)):
        return set()
    out = {"hash"}
    if has_m1 is not None and reader_commit and life_commit:
        r, l = has_m1(reader_commit), has_m1(life_commit)
        if r is not None and l is not None and r != l:
            out.add("readiness")
    return out


# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 07:04 +0400 — M1's first code commit (judge-units-0923: «THE READINESS JUDGE in its own units», ALPHA4-PREREG §4
# AMENDED; merged into a4-integration by 3cedc75 with its tip 76cdc48). The readiness rows change form here.
M1_JUDGE_UNITS_COMMIT = "56b08dc"


def has_commit(tree, ancestor: str, commit: str) -> "bool | None":
    """True/False: `ancestor` is an ancestor of (or is) `commit` in the repo at `tree`; None when git cannot say (unknown commit, no git)."""
    try:
        rc = subprocess.run(["git", "-C", str(tree), "merge-base", "--is-ancestor", ancestor, commit], capture_output=True).returncode
    except Exception:
        return None
    return True if rc == 0 else (False if rc == 1 else None)


def readiness_rows_differing(got: Sequence[dict], want: Sequence[dict]) -> Dict[str, int]:
    """The rows carrying `readiness` on either side (paired by seq, in order) and how many differ in it — printed beside the mask (36 of 36 on a4l-cost:
    every judge row in other units is the declared M1; a count below the total would be a different fact)."""
    g: Dict[int, List[dict]] = {}; w: Dict[int, List[dict]] = {}
    for r in got: g.setdefault(int(r["seq"]), []).append(r)
    for r in want: w.setdefault(int(r["seq"]), []).append(r)
    n = k = 0
    for s in sorted(set(g) & set(w)):
        for a, b in zip(g[s], w[s]):
            if "readiness" in a or "readiness" in b:
                n += 1; k += int(a.get("readiness") != b.get("readiness"))
    return {"rows_with_readiness": n, "differing": k}


def _iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read_jsonl(p: Path) -> List[dict]:
    """A journal/tape file the body may still be APPENDING to (tomorrow's live root): tolerate exactly ONE trailing partial line
    (dropped, named on stderr); a torn line anywhere else is corruption and raises. (edit: Claude (Fable 5.1), 2026-09-20 13:21 +0400 — robustness, not a bar.)"""
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    out: List[dict] = []
    for i, l in enumerate(lines):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                print(f"read_jsonl: dropped a trailing partial line in {p} ({len(l)} bytes, being written)", file=sys.stderr)
                break
            raise
    return out


# ----------------------------------------------------------------------------- the tape and the journal, cut at --hours
def _relink(link: Path, target: Path) -> None:
    """A payload symlink under the reader's own --out points at the CURRENT root's payload dir. Life 2's out dir was
    written while its root was `run/`; after the close (`mv run run-g4-life2-…`) the old link pointed into LIFE 3's
    `run/tape/payload` — a silent cross-life read for the solo probe and the plant (found 2026-09-21 14:0x, the v2
    control). A link is re-pointed when its target differs; a real directory is left alone."""
    if link.is_symlink():
        if os.readlink(link) != str(target):
            link.unlink(); os.symlink(target, link)
    elif not link.exists():
        os.symlink(target, link)


def closed_whole(events: Sequence[dict], last_seq: int, tape_last_seq: int, mind_last_seq: Optional[int] = None) -> bool:
    """edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — plan L-1 × L-5: True iff the record is a CLOSED life read WHOLE (a `stop` event in its
    journal and the cut reaching the tape's last row). Then every whole-tape twin ends its mind the way the body did
    (creature/replay.py:run_replay(close=) — the think in flight lands at the last eye row's seq) or the closed journal carries one
    think row no replay can. A live life, or a cut short of the tape's end, never closes: the live mind lands that think later.

    edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: «whole» is relative to what the MIND consumed.
    A mind behind its world stops with the tape's head rows unconsumed (creature/body.py:stop sets the stop event, the mind thread leaves
    its `q.get` loop without reading the queue, then `mind.close()` lands the in-flight think at the last eye row ≤ its last seq). With
    `mind_last_seq` given (gather's `mind_last_consumed`): True iff a `stop` event AND the cut IS the mind's last consumed seq. None = the
    old contract (the mind consumed the whole tape: `mind_last_seq` = `tape_last_seq`), byte-identical for every existing caller."""
    if mind_last_seq is None:
        mind_last_seq = tape_last_seq
    return bool(last_seq) and int(last_seq) == int(mind_last_seq) and any(e.get("event") == "stop" for e in events)


def _seq_or_none(v, tape_last_seq: int) -> Optional[int]:
    """A seq reading kept only when it is an int inside 1..tape_last_seq (a missing key, a torn file or a seq past the tape is no reading)."""
    if isinstance(v, bool):
        return None
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return v if 0 < v <= int(tape_last_seq) else None


def mind_last_consumed(journal: Sequence[dict], status: dict, ledger: dict, tape_last_seq: int, closed: bool) -> dict:
    """edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923, PURE: the mind's last CONSUMED seq and the three
    records it is read from, every one printed, none asserted. The body's `stop` event carries no seq (creature/body.py:_journal_event
    writes {"seq": None, "at", "event"}). What records the mind's position:
      · `state/ledger.json` `last_seq` — every snapshot writes it; the last one is `mind.close()`'s, inside `stop()`;
      · STATUS.json `last_seq` — the status thread writes it every HEART period, and `stop()` writes it last, after `close()`, just before
        the stop event;
      · the journal's last MIND-written row — every row carrying a seq (the mind's domain rows and its own `stage` rows; the body's and the
        exam's event rows carry seq None). A LOWER bound: an ear row journals nothing, so a mind that consumed a trailing ear row sits one
        past it. On a RUNNING life its last row may be half-written (a sleep row lands after its canvas row), so it is read only on a
        CLOSED record (a `stop` event), where the journal is complete.
    The ledger and STATUS are written AFTER the consume of the seq they name returns, so every journal row of every seq ≤ them is on disk
    when gather reads the journal (it reads them FIRST). M = the largest valid reading; with none valid, the journal's last row (source
    named). A reading outside 1..tape_last_seq is ignored."""
    J = max((int(r["seq"]) for r in journal if r.get("seq") is not None), default=0)
    readings = {"status": _seq_or_none((status or {}).get("last_seq"), tape_last_seq),
                "ledger": _seq_or_none((ledger or {}).get("last_seq"), tape_last_seq),
                "journal": (_seq_or_none(J, tape_last_seq) if closed else None)}
    valid = {k: v for k, v in readings.items() if v is not None}
    if valid:
        m = max(valid.values())
        src = " = ".join(k for k in ("status", "ledger", "journal") if valid.get(k) == m)
    else:
        m = min(J, int(tape_last_seq)) if J > 0 else 0
        src = ("journal (no STATUS/ledger last_seq; a lower bound — an ear row journals nothing)" if m else "none (no mind row, no STATUS/ledger last_seq)")
    return {"mind_last_seq": int(m), "source": src, "journal_last_mind_seq": J, "status_last_seq": (status or {}).get("last_seq"),
            "ledger_last_seq": (ledger or {}).get("last_seq"), "closed": bool(closed)}


def backlog_series(tape: Sequence[dict], t0: datetime) -> dict:
    """edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923, PURE: the body's own record of the mind's backlog as
    a SERIES (#236 — never a total). SENSE body publishes STATUS's `mind_backlog_rows` as `meta.reading.backlog` on a tape row every
    `period_s` (creature/senses/body_sense.py STATUS_FIELD_MAP), so the series is on the tape — the unconsumed tail included, where it
    grows. Printed: the max and the last (seq/at), the first row over 100 rows (the brief's line), the max per hour (the row's own `at`), and the mind's
    `moments` advanced per hour from the same rows (its motion while behind — «a mind behind its world is alive» read, never assumed)."""
    body = [r for r in tape if r.get("sense") == "body"]
    out: Dict[str, object] = {"source": "the tape's `body` rows: meta.reading.backlog = STATUS.mind_backlog_rows when the row was published", "body_rows": len(body)}
    pts: List[Tuple[int, str, int, int]] = []; mom: List[Tuple[int, int]] = []
    for r in body:
        rd = (r.get("meta") or {}).get("reading") or {}
        h = int((_iso(r["at"]) - t0).total_seconds() // 3600)
        b = rd.get("backlog"); mo = rd.get("moments")
        if isinstance(b, (int, float)) and not isinstance(b, bool):
            pts.append((int(r["seq"]), r["at"], h, int(b)))
        if isinstance(mo, (int, float)) and not isinstance(mo, bool):
            mom.append((h, int(mo)))
    if not body:
        out.update(n=0, max=None, last=None, first_over_100=None, note="no body rows on this tape (SENSE body not declared): no backlog series exists on this record")
        return out
    if not pts:
        out.update(n=0, max=None, last=None, first_over_100=None, note="the body rows carry no `backlog` reading (the genome's SENSE body fields omit it)")
        return out
    mx = max(pts, key=lambda p: p[3])
    first = next((p for p in pts if p[3] > 100), None)
    n_h = max(0, max(p[2] for p in pts)) + 1
    per_hour: List[Optional[int]] = [None] * n_h
    for _s, _a, h, b in pts:
        if 0 <= h < n_h:
            per_hour[h] = b if per_hour[h] is None else max(per_hour[h], b)
    adv: List[Optional[int]] = []
    if mom:
        last_by_h: Dict[int, int] = {}
        for h, mo in mom:
            last_by_h[h] = mo
        prev = 0
        for h in range(max(0, max(last_by_h)) + 1):
            if h in last_by_h:
                adv.append(last_by_h[h] - prev); prev = last_by_h[h]
            else:
                adv.append(None)
    out.update(n=len(pts), max=mx[3], max_seq=mx[0], max_at=mx[1], last=pts[-1][3], last_seq=pts[-1][0], last_at=pts[-1][1],
               first_over_100=({"seq": first[0], "at": first[1], "hour": round((_iso(first[1]) - t0).total_seconds() / 3600, 3), "backlog": first[3]}
                               if first is not None else None),
               per_hour_max=per_hour, moments_advanced_per_hour=(adv or None))
    return out


def lag_summary(lag: Optional[dict]) -> dict:
    """edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: the unconsumed tail in one dict, printed under ALIVE,
    COST and REPLAY (never a gate: a mind behind its world is alive; its lag is COST's finding)."""
    if not lag:
        return {}
    bs = lag.get("backlog_series") or {}
    return {"cut_at_mind_last_seq": bool(lag.get("cut")), "mind_last_seq": lag.get("mind_last_seq"), "mind_last_seq_source": lag.get("source"),
            "time_cut_seq": lag.get("time_cut_seq"), "tape_head_seq": lag.get("tape_head_seq"),
            "rows_unconsumed": lag.get("rows_unconsumed"), "rows_cut_by_lag": lag.get("rows_cut_by_lag"),
            "world_hours_unconsumed": lag.get("world_hours_unconsumed"), "world_hours_cut_by_lag": lag.get("world_hours_cut_by_lag"),
            "hours_lived": lag.get("hours_lived"), "mind_last_at": lag.get("mind_last_at"), "tape_head_at": lag.get("tape_head_at"),
            "backlog_max": bs.get("max"), "backlog_max_at": bs.get("max_at"), "backlog_last": bs.get("last"), "backlog_last_at": bs.get("last_at"),
            "backlog_first_over_100": bs.get("first_over_100"), "backlog_body_rows": bs.get("n"),
            "status_backlog_rows": lag.get("status_backlog_rows"), "backlog_reconciles": lag.get("backlog_reconciles")}


def lag_text(ls: dict) -> str:
    """The lag in one VERDICT.md clause (READER-LAG-0923)."""
    if not ls:
        return "lag not read"
    first = ls.get("backlog_first_over_100")
    series = (f"backlog (body rows, n {ls.get('backlog_body_rows')}): max {ls.get('backlog_max')} at {ls.get('backlog_max_at')}, last {ls.get('backlog_last')}, "
              f"first > 100 {('at ' + str(first.get('at')) + ' (hour ' + str(first.get('hour')) + ', seq ' + str(first.get('seq')) + ')') if first else 'never'}")
    head = (f"the mind's last consumed seq {ls.get('mind_last_seq')} ({ls.get('mind_last_seq_source')}) of the tape's {ls.get('tape_head_seq')}: "
            f"{ls.get('rows_unconsumed')} rows / {ls.get('world_hours_unconsumed')} world h unconsumed")
    cut = (f"; the read is CUT at it ({ls.get('rows_cut_by_lag')} rows / {ls.get('world_hours_cut_by_lag')} world h of the {ls.get('time_cut_seq')}-row window the mind never lived; it lived {ls.get('hours_lived')} h)"
           if ls.get("cut_at_mind_last_seq") else "; not cut (the mind reached the read's window)")
    rec = f"; STATUS backlog {ls.get('status_backlog_rows')} (reconciles with the tape: {ls.get('backlog_reconciles')})"
    return "LAG: " + head + cut + "; " + series + rec


def gather(root: Path, out: Path, hours: float) -> dict:
    """Concatenates the root's tape files in seq order into out/tape/ALL.jsonl (payload symlinked, never copied), cut at
    start + hours; copies the state (a snapshot COPY); reads the journal's mind rows and event rows up to the cut.

    edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: the read is of the life THE MIND LIVED. STATUS.json and
    the ledger are read FIRST (before the tape and the journal: on a running life every journal row of a seq ≤ their `last_seq` is then on
    disk, and no row they name is missing from the tape as read), then the mind's last consumed seq M (`mind_last_consumed`). When M is
    short of the time cut the read is CUT at M: ALL.jsonl (every twin's tape), the live journal, the mind's events and every mark read
    rows ≤ M, and `closed_whole` is judged against M (the mind closed whole relative to what it consumed). `tape_world` — the time cut
    alone — is kept for ALIVE (the senses lived the whole window; a mind behind its world is alive), and the unconsumed tail is a fact
    on the record (`lag`: rows and world hours unconsumed, the body rows' backlog series). With no lag every output is today's."""
    status = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
    try:
        ledger = json.loads((root / "state" / "ledger.json").read_text())
    except (OSError, json.JSONDecodeError):
        ledger = {}
    tape_rows = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        tape_rows += read_jsonl(f)
    tape_rows.sort(key=lambda r: r["seq"])
    assert [r["seq"] for r in tape_rows] == list(range(1, len(tape_rows) + 1)), "tape seqs are not 1..N"
    journal = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        journal += read_jsonl(f)
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (8): the MIND's own event rows (the READINESS
    # judge's `stage` event, creature/mind.py:877) carry a `seq` and NO `at` — `_iso(e["at"])` below raised KeyError on every read of a
    # life whose door opened. They are cut by seq and carried apart as `mind_events` (STAGE and WEB read them); `events` keeps its
    # contract (the body's and the exam's rows, every one with `at`); the mind rows and REPLAY's inputs are unchanged.
    events = [r for r in journal if "event" in r and r.get("at") is not None]
    mind_events_all = [r for r in journal if "event" in r and r.get("at") is None]
    starts = [e for e in events if e["event"] == "start"]
    assert starts, "no start event in the journal"
    t0 = _iso(starts[0]["at"])
    t_cut = t0 + timedelta(hours=hours)
    tape_world = [r for r in tape_rows if _iso(r["at"]) <= t_cut]
    time_cut_seq = tape_world[-1]["seq"] if tape_world else 0
    tape_last_seq = tape_rows[-1]["seq"] if tape_rows else 0
    closed = any(e.get("event") == "stop" for e in events)
    ml = mind_last_consumed(journal, status, ledger, tape_last_seq, closed)
    M_seq = ml["mind_last_seq"]
    lag_cut = 0 < M_seq < time_cut_seq
    last_seq = M_seq if lag_cut else time_cut_seq
    tape_cut = [r for r in tape_world if r["seq"] <= last_seq]
    mind_rows = [r for r in journal if "event" not in r and int(r["seq"]) <= last_seq]
    mind_events = [r for r in mind_events_all if r.get("seq") is not None and int(r["seq"]) <= last_seq]
    events_cut = [e for e in events if _iso(e["at"]) <= t_cut or e["event"] == "stop"]
    (out / "tape").mkdir(parents=True, exist_ok=True)
    pl = out / "tape" / "payload"
    _relink(pl, (root / "tape" / "payload").resolve())   # §18: a --reuse after the root MOVED must not read another life's payloads
    (out / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in tape_cut))
    (out / "live-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    st = out / "live-state"; st.mkdir(exist_ok=True)
    for f in ("organism.npz", "organism.json", "ledger.json"):
        shutil.copy2(root / "state" / f, st / f)
    exams = []
    for f in sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit()):
        d = json.loads(f.read_text())
        if _iso(d["at"]) <= t_cut:
            d["_file"] = f.name; exams.append(d)
    hours_on_tape = (_iso(tape_cut[-1]["at"]) - t0).total_seconds() / 3600 if tape_cut else 0.0
    hours_on_tape_world = (_iso(tape_world[-1]["at"]) - t0).total_seconds() / 3600 if tape_world else 0.0
    at_of = {int(r["seq"]): r["at"] for r in tape_rows}
    def _hours_between(a, b):
        return round(max(0.0, (_iso(b) - _iso(a)).total_seconds()) / 3600, 4) if (a and b) else None
    m_at = at_of.get(M_seq) if M_seq else None
    head_at = tape_rows[-1]["at"] if tape_rows else None
    S_seq = ml["status_last_seq"]; bl = status.get("mind_backlog_rows")
    lag = {"cut": bool(lag_cut), **ml, "time_cut_seq": time_cut_seq, "tape_head_seq": tape_last_seq, "cut_seq": last_seq,
           "rows_unconsumed": (tape_last_seq - M_seq) if M_seq else None, "rows_cut_by_lag": time_cut_seq - last_seq,
           "mind_last_at": m_at, "time_cut_at": (tape_world[-1]["at"] if tape_world else None), "tape_head_at": head_at,
           "world_hours_unconsumed": (_hours_between(m_at, head_at) if M_seq else None),
           "world_hours_cut_by_lag": (_hours_between(m_at, tape_world[-1]["at"]) if lag_cut else 0.0),
           "hours_lived": round(hours_on_tape, 4), "hours_on_tape_world": round(hours_on_tape_world, 4),
           "status_backlog_rows": bl, "status_heartbeat_at": status.get("heartbeat_at"),
           "backlog_reconciles": (((tape_last_seq - int(S_seq)) == int(bl)) if (closed and isinstance(S_seq, int) and not isinstance(S_seq, bool)
                                                                               and isinstance(bl, int) and not isinstance(bl, bool)) else None),
           "backlog_series": backlog_series(tape_world, t0)}
    return {"t0": t0, "t_cut": t_cut, "tape": tape_cut, "mind": mind_rows, "events": events_cut, "status": status, "exams": exams,
            "mind_events": mind_events, "tape_world": tape_world, "lag": lag,
            "closed_whole": closed_whole(events, last_seq, tape_last_seq, mind_last_seq=(M_seq or None)),
            "last_seq": last_seq, "hours_on_tape": hours_on_tape, "hours_on_tape_world": hours_on_tape_world}


# ----------------------------------------------------------------------------- ALIVE
def alive(G: dict, hours: float, nrestarts: Optional[int]) -> dict:
    """edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: the bar is unchanged («every counter moved every
    hour, no sense dead > 60 s», 24 h on the tape, NRestarts 0); what it READS under a lag is not. The hours on the tape and the sense
    gaps are the WORLD's (`tape_world`: the time cut alone — the senses lived the whole window, and a sense dead in the unconsumed tail
    must still fail). The mind's own counters (canvases, thinks, sleeps — keyed by the world hour of the row they consumed) are required
    in every world hour the mind FULLY lived; the world hours beyond its reach are named, not failed (a mind behind its world is alive —
    its lag is COST's finding). The snapshots (the body's events, keyed by WALL time) are still required in every hour: a mind that
    stopped moving still fails. With no lag cut every reading is today's. The lag is printed beside (`lag`)."""
    world = G.get("tape_world") or G["tape"]
    hours_world = G.get("hours_on_tape_world", G["hours_on_tape"])
    lag = G.get("lag") or {}
    t0 = G["t0"]; at = {r["seq"]: _iso(r["at"]) for r in world}
    n_hours = int(np.ceil(hours_world)) or 1
    per = {h: {"canvases": 0, "thinks": 0, "sleeps": 0, "snapshots": 0, "exams": 0} for h in range(n_hours)}
    for r in G["mind"]:
        h = int((at[int(r["seq"])] - t0).total_seconds() // 3600)
        if h not in per: continue
        if "moment" in r: per[h]["canvases"] += 1
        elif "think" in r: per[h]["thinks"] += 1
        elif "sleep" in r: per[h]["sleeps"] += 1
    for e in G["events"]:
        h = int((_iso(e["at"]) - t0).total_seconds() // 3600)
        if h in per and e["event"] in ("snapshot", "exam"): per[h][e["event"] + "s"] += 1
    gaps = []
    for sense in ("eye", "ear"):
        ts = [at[r["seq"]] for r in world if r["sense"] == sense]
        gaps.append(max((b - a).total_seconds() for a, b in zip(ts, ts[1:])) if len(ts) > 1 else 0.0)
    restarts = [e for e in G["events"] if e["event"] == "sense_restart"]
    crashes = [e for e in G["events"] if e["event"] == "crash"] + ([G["status"]] if G["status"].get("crash") else [])
    stops = [e for e in G["events"] if e["event"] == "stop" and _iso(e["at"]) < G["t_cut"]]
    hours_full = [h for h in per if h < int(hours)]
    # READER-LAG-0923: under a lag cut the mind's own counters are graded over the world hours it FULLY lived (h < int(hours lived));
    # beyond them only the wall-clock snapshots are (the mind still moved in that wall hour — or it did not, and ALIVE fails)
    reach = int(G["hours_on_tape"]) if lag.get("cut") else None
    def _moved(h: int) -> bool:
        ks = ("snapshots",) if (reach is not None and h >= reach) else ("canvases", "thinks", "snapshots", "sleeps")
        return all(per[h][k] > 0 for k in ks)
    moved = all(_moved(h) for h in hours_full) if hours_full else False
    ok = (hours_world >= hours - 1 / 60) and moved and (max(gaps) <= 60.0) and not crashes and not stops and (nrestarts in (0, None))
    out = {"pass": bool(ok), "hours_on_tape": round(hours_world, 3), "bar_hours": hours, "per_hour": per, "every_counter_moved_every_hour": moved,
           "max_gap_s_eye_ear": [round(g, 1) for g in gaps], "sense_restarts": len(restarts), "crashes": len(crashes), "stops_before_cut": len(stops),
           "nrestarts": nrestarts, "note": "NRestarts read from systemd (--nrestarts / --unit); None = not read"}
    if lag:
        out["lag"] = lag_summary(lag)
    if reach is not None:
        out["mind_reach_full_hours"] = reach
        out["hours_beyond_the_minds_reach"] = [h for h in hours_full if h >= reach]
        out["reach_note"] = ("the mind lived %.3f world h of the window: canvases/thinks/sleeps are graded in world hours < %d; in the hours beyond "
                             "its reach only the wall-clock snapshots are (the body's own record that it kept moving)" % (G["hours_on_tape"], reach))
    return out


# ----------------------------------------------------------------------------- twins (one worker per twin, a fresh root each)
# edit: Claude (Fable 5.1), 2026-09-21 22:12 +0400 — two twin defects found at J's landing (G5): (1) the one-glance wrapper's lambda DROPPED every
# keyword the mind now passes (`colour=`, Builder J's block) → TypeError in the T-one-glance worker → (xi) unreadable on every
# G5 verdict; it forwards **kw now. (2) the nowire twin rebuilt Predictor() WITHOUT the genome's declared error arm (E's
# `; error comparator`) → the twin ran the novelty arm while the life ran the comparator; it keeps the arm now. Both factored
# out of worker() so tests/creature/test_verdict_twins_g5.py can call them without a worker process.
# (Builder J found the same dropped-keyword defect independently at 22:20 on its branch — its lambda variant with `colour=None` was dropped at the merge in favour of this **kw helper, which its test pins.)
def _plant_eye_row(rows: List[dict], root: Path) -> dict:
    """REPLAY's planted divergence: the maker eye row WITH a truth file at index 300 among the first 1,000 tape rows when more
    than 300 exist (a G4-shaped tape: exactly the row always picked), else the middle one (a G5 tape shares the seq space with
    the game and folder doors: ~241 maker rows in 1,000). Raises IndexError, named, when no such row exists."""
    mk = [r for r in rows if r["sense"] == "eye" and (r.get("meta") or {}).get("source", "maker") == "maker"
          and (root / "truth" / (Path(r["payload"]).stem + ".json")).exists()]   # §18: a folder/game picture has no truth file
    if not mk:
        raise IndexError("no maker eye row with a truth file in the first 1,000 tape rows")
    return mk[300] if len(mk) > 300 else mk[len(mk) // 2]


def _force_one_glance() -> None:
    """T-one-glance: gaze mode "one" on every glances() call of THIS process (PREREG §16 addendum), every other argument forwarded."""
    from genome import gaze as _gaze
    _orig = _gaze.glances
    _gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="", **kw: _orig(rgb, spec_, g, "one", pic_id, **kw)


def _force_no_coarse() -> None:
    """The blind-coarse twin ASKS with the four located glances it LEARNED on (builder B's clause 9, docs/briefs/LIFE-B-REPORT.md §6:
    a `--blind coarse` twin learned without the fifth glance and was asked with it — «learned without, asked with»). The sibling of
    `_force_one_glance()`: every glances() call of THIS process sees a gaze dict without `coarse`, every other argument forwarded.
    edit: Claude (Fable 5.1), 2026-09-22 20:39 +0400 — written RED first (tests/creature/test_verdict_blind_coarse.py)."""
    from genome import gaze as _gaze
    _orig = _gaze.glances
    _gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="", **kw: _orig(rgb, spec_, {k: v for k, v in dict(g).items() if k != "coarse"}, mode, pic_id, **kw)


def _nowire(mind: "Mind") -> None:
    """The no-wire twin: a fresh unwired Organism; the Predictor rebuilt on it with the SAME declared arm the life runs."""
    from genome.machinery import Organism
    from genome.predict import Predictor
    mind.org = Organism(mind.genome, wire=False)
    if mind.predictor is not None:
        mind.predictor = Predictor(mind.org, arm=mind.predictor.arm)


def rows_for_spec(rows: List[dict], spec: dict) -> List[dict]:
    """The rows a twin's mind sees, from its spec — PURE (never mutates `rows`). `until_seq` cuts; `shuffle_words` is T-shuffle (the ear's
    words permuted across canvases by a fixed rng, the sight stream untouched); `drop_source` removes every row whose `meta.source` is it.
    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (11): `drop_source` is READ's blind twin —
    tools/read_recognised.py:blind_twin_root's own mechanism («a Mind fed the tape with every row whose meta.source == drop_source
    removed») applied to the reader's CUT tape through the worker road (close/snapshot, seconds, --reuse), where blind_twin_root itself
    reads the root's WHOLE tape and closes unconditionally. Factored out of worker() so the filter is tested without a Mind."""
    if spec.get("until_seq"):
        rows = [r for r in rows if r["seq"] <= spec["until_seq"]]
    if spec.get("drop_source"):
        rows = [r for r in rows if (r.get("meta") or {}).get("source") != spec["drop_source"]]
    if spec.get("shuffle_words"):
        # T-shuffle: the ear's words permuted across canvases by a fixed rng (the sight stream untouched)
        rows = list(rows)
        ears = [i for i, r in enumerate(rows) if r["sense"] == "ear"]
        words = [rows[i]["meta"]["word"] for i in ears]
        perm = np.random.default_rng(5).permutation(len(words))
        for i, j in zip(ears, perm):
            rows[i] = dict(rows[i]); rows[i]["meta"] = dict(rows[i]["meta"]); rows[i]["meta"]["word"] = words[j]
    return rows


def worker(spec_path: Path) -> int:
    spec = json.loads(Path(spec_path).read_text())
    from creature.mind import Mind
    from genome.machinery import Organism, parse_genome
    from genome.predict import Predictor
    from genome.questions import build_ledgers
    root = Path(spec["root"]); (root / "tape").mkdir(parents=True, exist_ok=True)
    src_tape = Path(spec["tape"])
    _relink(root / "tape" / "payload", (src_tape.parent / "payload").resolve())
    rows = rows_for_spec(read_jsonl(src_tape), spec)
    if spec.get("shuffle_voice") is not None:
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:48 +0400 — A4L-VOICE: the SHUFFLED-SOUND twin (V1/V2's null) — every
        # maker ear-sound row's payload replaced by ANOTHER thing's chord by a fixed derangement of the reader's seed (tools/verdict_life.py:shuffle_voice)
        from tools import verdict_life as _vl_w
        rows, _voice_perm = _vl_w.shuffle_voice(rows, int(spec["shuffle_voice"]))
        (root / "voice_perm.json").write_text(json.dumps(_voice_perm))
    (root / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))   # self_exam's disjointness control reads it
    genome_path = Path(spec["genome"])
    if spec.get("one_glance"):
        # edit: Claude (Fable 5.1), 2026-09-20 13:03 +0400 — PREREG §16 addendum: G1's T-one-glance = gaze mode "one" (the whole canvas at
        # glance×glance, one feature vector), forced on every glances() call of THIS worker process — the mind's learning road and
        # the exam's held-out alike — without touching creature code (the mind hardcodes surprise/random).
        _force_one_glance()
    if "coarse" in spec.get("blind", []):
        _force_no_coarse()      # edit: Claude (Fable 5.1), 2026-09-22 20:39 +0400 — B's clause 9: the twin asks with the glances it learned on
    mind = Mind(genome_path, root, blind=frozenset(spec.get("blind", [])))
    if spec.get("nowire"):
        _nowire(mind)
    t0 = time.perf_counter(); n_canvas = 0; errs = []
    for r in rows:
        mind.consume(r)
    secs = time.perf_counter() - t0
    if spec.get("close"):
        mind.close()        # edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — a CLOSED life's whole tape: the tail think lands as the body's stop() landed it (close() snapshots)
    else:
        mind.snapshot()
    org = mind.org
    L = build_ledgers(org, mind.moment_word)
    def _cross(log):
        return sum(1 for _m, sc, wc in log if L["sight"].get(sc, set()) != L["words"].get(wc, set()))
    mind_rows = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        mind_rows += [r for r in read_jsonl(f) if "event" not in r]
    (root / "mind-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    n_canvas = sum(1 for r in mind_rows if "moment" in r)
    summary = {"label": spec["label"], "arrivals": org.arrivals, "budget_left": org.budget_left, "births": len(org.births), "c": org.c,
               "glances_confirmed": getattr(mind, "glances_confirmed", None), "glances_surprised": getattr(mind, "glances_surprised", None),   # edit: Claude (Fable 5.1), 2026-09-22 22:33 +0400 — §19.1's twin clause reads the blind-surprise twin's own count
               "closed": bool(spec.get("close")),
               "cells": [int(org.sight.alive.sum()), int(org.words.alive.sum())], "cells_born": org.sight.n + org.words.n,
               "edges_cross": {"born": _cross(org.edges_log), "pruned": _cross(org.prunes_log), "born_total": len(org.edges_log), "pruned_total": len(org.prunes_log)},
               "sleeps": sum(1 for r in mind_rows if "sleep" in r), "thinks": sum(1 for r in mind_rows if "think" in r),
               "parked": sum(1 for r in mind_rows if "think" in r and r["think"].get("parked")),
               "canvases": n_canvas, "seconds": round(secs, 1), "ms_per_canvas": round(1000 * secs / max(1, n_canvas), 2), "hash": org.state_hash()}
    if spec.get("drop_source"):
        # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (11): READ's blind twin is ASKED by the reader
        # (tools/read_recognised.py:recognised_share on its snapshot); no self-exam is spent on it.
        summary.update(rows_replayed=len(rows), dropped_source=spec["drop_source"], exam=None, exam_stderr="",
                       exam_skipped="a drop-source twin: the reader asks its snapshot directly")
        (root / "summary.json").write_text(json.dumps(summary, default=str))
        return 0
    if spec.get("one_glance") or "coarse" in spec.get("blind", []):
        from tools import self_exam as _se           # in-process, so the forced mode "one" (or the forced no-coarse) applies to the held-out glances too
        old_argv = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"]
            _se.main()
        finally:
            sys.argv = old_argv
        summary["exam_stderr"] = ""
    else:
        ex = subprocess.run([sys.executable, str(ROOT / "tools" / "self_exam.py"), "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"],
                            capture_output=True, text=True, cwd=ROOT)
        summary["exam_stderr"] = ex.stderr[-500:] if ex.returncode else ""
    exams = sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit())
    summary["exam"] = json.loads(exams[-1].read_text()) if exams else None
    (root / "summary.json").write_text(json.dumps(summary, default=str))
    return 0


def run_workers(specs: List[dict], workers: int, out: Path) -> Dict[str, dict]:
    procs = []; pending = list(specs); done: Dict[str, dict] = {}
    while pending or procs:
        while pending and len(procs) < workers:
            s = pending.pop(0); sp = out / "specs" / (s["label"] + ".json"); sp.parent.mkdir(exist_ok=True)
            sf0 = Path(s["root"]) / "summary.json"
            if REUSE and sf0.exists():
                done[s["label"]] = json.loads(sf0.read_text()); print(f"  twin {s['label']}: reused", flush=True); continue
            sp.write_text(json.dumps(s)); log = open(out / "specs" / (s["label"] + ".log"), "w")
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker", str(sp)], stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            procs.append((s, p, log))
        time.sleep(2.0)
        still = []
        for s, p, log in procs:
            if p.poll() is None: still.append((s, p, log)); continue
            log.close(); sf = Path(s["root"]) / "summary.json"
            done[s["label"]] = json.loads(sf.read_text()) if sf.exists() else {"label": s["label"], "error": f"worker exit {p.returncode}"}
            print(f"  twin {s['label']}: exit {p.returncode}" + ("" if sf.exists() else " (no summary)"), flush=True)
        procs = still
    return done


def genome_twin_text(base_text: str, label: str, numbers: Optional[dict] = None, fixations: Optional[int] = None, frozen_after: Optional[int] = None) -> str:
    """A genome-TEXT twin: the same file with its numbers replaced (random genomes, (ix)) or GAZE fixations 1 ((xi))."""
    import re
    lines = base_text.splitlines()
    out = []
    for line in lines:
        s = line.split("#")[0].rstrip(); head = s.split()
        if numbers:
            n = numbers
            if head[:2] == ["BIRTH", "novelty"]: line = f"BIRTH    novelty  cos<{n['theta_n']:.4f}"
            elif head[:2] == ["BIRTH", "error"]: line = f"BIRTH    error    misfires {n['misfires']}"
            elif head[:1] == ["BUDGET"]: line = f"BUDGET   {n['budget']} per arrival"
            elif head[:1] == ["KWTA"]: line = f"KWTA     {n['kwta']}"
            elif head[:1] == ["DELTA"]: line = f"DELTA    lr {n['lr']:.4f}"
            elif head[:1] == ["PRUNE"]: line = re.sub(r"w<[0-9.]+", f"w<{n['prune_floor']:.4f}", line.split("#")[0]).rstrip()
            elif head[:1] == ["MERGE"]: line = f"MERGE    cos>{n['theta_m']:.4f} same-answer"
            elif head[:1] == ["SCALE"]: line = f"SCALE    every {n['scale_every']} moments"
            elif head[:2] == ["STAGE", "1"]: line = f"STAGE    1 senses   moments 0..{n['stage1']}"
            elif head[:2] == ["STAGE", "2"]: line = f"STAGE    2 meet     moments {n['stage1']}.."
            elif head[:1] == ["ABSTAIN"]: line = f"ABSTAIN  second/best > {n['abstain_ratio']:.3f}"
        if fixations is not None and head[:1] == ["GAZE"]:
            line = re.sub(r"fixations \d+", f"fixations {fixations}", line.split("#")[0]).rstrip()
        if frozen_after is not None and head[:1] == ["FROZEN"]:
            line = f"FROZEN   after {frozen_after} cells"
        out.append(line)
    return f"# {label} — a genome-text twin written by tools/verdict_g4.py (PREREG §16)\n" + "\n".join(out) + "\n"


# ----------------------------------------------------------------------------- the reader's own asks on an organism
def own_asks(root: Path, genome_path: Path) -> dict:
    """The plant (zog), the null plant (vex), random landing and the ceiling numbers — self_exam does not ask the plant."""
    from tools import self_exam
    from genome import world, run_g1
    from genome.questions import ask_plant_glances
    g, org, ledgers, L = self_exam.load_snapshot(root, genome_path)
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], 10, np.random.default_rng(2))
    held_g = run_g1.glance_held(held, g, "surprise"); feats = run_g1.feats_only(held_g)
    h0 = org.state_hash()
    plant = ask_plant_glances(org, ledgers, world.THING_PLANT, feats[world.THING_PLANT])
    null = ask_plant_glances(org, ledgers, world.THING_NULL, feats[world.THING_NULL])
    rnd = run_g1.landing(run_g1.glance_held(held, g, "random"), things, first=2)
    assert org.state_hash() == h0
    return {"plant": plant, "null": null, "random_landing": rnd}


# ----------------------------------------------------------------------------- MODULATION (§10 verbatim, on the life's own err series)
def _regime_calibration(mind: List[dict], step: int = 100, prev_window: int = 50, first_n: int = 3, settle_skip: int = 3) -> dict:
    """edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3 (G5-H-MODULATION-BARS-W32B.md): the
    null band and the settle bar DERIVED FROM DATA at read time (#158's argument for adaptivity — never a typed
    ratio), from the life's OWN pre-window (window-0) canvases. §16 addendum's ratio bars (3x spike / 1.25x settle /
    1.5x null) were calibrated on the pre-W3-2b ~0.23 steady-state error; W3-2b's memory-relative error collapses the
    steady state to ~0.016 (E's report §0/§3), which makes a ratio bar on a near-floor baseline report on the
    instrument, not the mechanism (SOLUTIONS #162, #228 b) — the same shape as the toy-front repair §16 addendum
    already made once, now needed again for the new regime.

    NULL BAND: at every `step`-th canvas inside window 0, treat it as a FAKE boundary and compute — for every thing
    with >= `first_n` showings after it — the SAME statistic the real spike rule computes: median(its first
    `first_n` errs after the boundary) / median(the `prev_window` errs immediately before it). Doing this at MANY
    boundaries (not just the one midpoint the original null used) over EVERY continuing thing yields a sample of
    "what ratio does pure noise produce on this life's own tape"; its 95th percentile is the null band. A real spike
    must clear this band AND the fixed 3x bar (both, §18 addendum 3 step 1).

    SETTLE BAR: window 0's own per-showing errors, for each thing's showings AFTER its own first `settle_skip`
    (excluding each thing's own bootstrap transient at the very start of the life — the only place on the tape a
    window-0 thing is itself new) — a continuing thing's own steady per-canvas noise. Its 95th percentile is the
    settle bar: an ABSOLUTE error ceiling, not a ratio on a baseline that can collapse to near-zero (1.25x of a
    ~0.016 median is ~0.02 — a bar a single glance's rounding can trip).

    Both derivations read ONLY window-0 rows (pre-window canvases — the only stretch with no real arrival to
    confound the calibration); if window 0 is too short for a given knob, the corresponding reading is None and
    every caller checks for it before grading — never a divide-by-zero, never a silent 0.
    """
    w0 = [r for r in mind if int(r["moment"][1:5]) == 0]
    n = len(w0)
    ratios: List[float] = []
    samples: List[dict] = []
    for m in range(step, max(step, n - first_n), step):
        prev = w0[max(0, m - prev_window):m]
        if not prev:
            continue
        last50 = float(np.median([p["err"] for p in prev]))
        if last50 <= 0:
            continue
        by_thing: Dict[str, list] = {}
        for q in w0[m:]:
            by_thing.setdefault(q["word"], []).append(q["err"])
        for t, errs in by_thing.items():
            if len(errs) >= first_n:
                ratio = float(np.median(errs[:first_n])) / last50
                ratios.append(ratio)
                samples.append({"thing": t, "boundary_idx": m, "last50_med": round(last50, 4), "ratio": round(ratio, 4)})
    null_band_95 = float(np.percentile(ratios, 95)) if ratios else None
    share_within = (sum(1 for r in ratios if r < null_band_95) / len(ratios)) if (ratios and null_band_95 is not None) else None
    seen_count: Dict[str, int] = {}
    noise_errs: List[float] = []
    for r in w0:
        t = r["word"]
        seen_count[t] = seen_count.get(t, 0) + 1
        if seen_count[t] > settle_skip:
            noise_errs.append(r["err"])
    settle_bar_err = float(np.percentile(noise_errs, 95)) if noise_errs else None
    return {"source": "window-0 (pre-window) canvases, this life's own tape — the fake-boundary sample and the settle noise are both derived here, never typed",
            "n_w0_rows": n, "step": step, "prev_window": prev_window, "first_n": first_n,
            "null_ratio_samples": len(ratios), "null_band_95": round(null_band_95, 4) if null_band_95 is not None else None,
            "null_share_within_band": round(share_within, 4) if share_within is not None else None,
            "settle_noise_n": len(noise_errs), "settle_skip_first": settle_skip,
            "settle_bar_err_95": round(settle_bar_err, 6) if settle_bar_err is not None else None,
            "sample_head": samples[:5]}


def modulation(G: dict, F: float, regime_step: int = 100) -> dict:
    # edit: Claude (Fable 5.1), 2026-09-21 20:57 +0400 — `regime_step` (CLI --regime-step): the fake-boundary sampling step of _regime_calibration; 100 = the recorded default; a 2 h window 0 (8 h seam lives) has ~14 boundaries × ~11 things ≈ 150 samples at 100 — enough; 25 is a convenience there (docs/G5-SEAM-LIFE-PLAN.md §1)
    # edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400 — §18: MODULATION reads the DRAWN world only (maker moments "w…"); a folder row's moment is "f<sha>" and its word is a folder name
    # edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3: BOTH the §16 fixed-bar reading (the
    # record — "pass_fixed_bars_record") and the regime-derived reading (_regime_calibration — "pass") are computed
    # and printed; grading (M["MODULATION"]["pass"], what the top-level verdict reads) uses the regime-derived one.
    mind = [r for r in G["mind"] if "moment" in r and r.get("word") and str(r["moment"]).startswith("w")]
    win = lambda r: int(r["moment"][1:5])
    by_seq = {int(r["seq"]): r for r in mind}
    reg = _regime_calibration(mind, step=int(regime_step))
    out = {"F": F,
           "settle_bar": ("record (§16 addendum): err at the 10th showing ≤ 1.25 × the pre-window last-50 median; the toy's F+.05 = %.4f printed per thing. "
                          "§18 addendum 3: the regime-derived bar is an ABSOLUTE ceiling — the life's own pre-window 95th percentile, see 'regime.settle_bar_err_95'.") % (F + 0.05),
           "regime": reg, "windows": {}}
    seen_before: set = set()
    cur = None; idx = 0
    for i, r in enumerate(mind):
        w = win(r)
        if cur is None: cur = w
        if w != cur:
            prev = mind[max(0, i - 50):i]
            last50 = float(np.median([p["err"] for p in prev])) if prev else 0.0
            words_here = []
            for q in mind[i:]:
                if win(q) != w: break
                words_here.append(q)
            new = sorted({q["word"] for q in words_here} - seen_before)
            returning = sorted({q["word"] for q in words_here} & seen_before - {q["word"] for q in prev})
            rec = {"at_seq": int(r["seq"]), "last50_med": round(last50, 4), "new_things": new, "returning_things": returning, "per_thing": {}}
            for t in new + returning:
                errs = [q["err"] for q in words_here if q["word"] == t]
                if len(errs) < 3: continue
                first3 = float(np.median(errs[:3])); tenth = errs[9] if len(errs) >= 10 else None
                spike_fixed = bool(last50 > 0 and first3 >= 3 * last50)
                spike_regime = bool(last50 > 0 and first3 >= 3 * last50 and (reg["null_band_95"] is None or (first3 / last50) >= reg["null_band_95"]))
                settled_fixed = bool(tenth is not None and last50 > 0 and tenth <= 1.25 * last50)
                settled_regime = bool(tenth is not None and reg["settle_bar_err_95"] is not None and tenth <= reg["settle_bar_err_95"])
                first_settle_regime = next((j + 1 for j, e in enumerate(errs) if reg["settle_bar_err_95"] is not None and e <= reg["settle_bar_err_95"]), None)
                rec["per_thing"][t] = {"kind": "new" if t in new else "returning", "first3_med": round(first3, 4),
                                       "spike_ratio": round(first3 / last50, 2) if last50 > 0 else None,
                                       "spike": spike_fixed, "spike_regime": spike_regime,
                                       "err_10th": round(tenth, 4) if tenth is not None else None,
                                       "settled": settled_fixed, "settled_regime": settled_regime,
                                       "settled_toy_bar_F_plus_05": bool(tenth is not None and tenth < F + 0.05),
                                       "first_settle_showing_regime": first_settle_regime, "n_showings": len(errs)}
            out["windows"][str(w)] = rec
            cur = w
        seen_before.add(r["word"])
    # the null: a FAKE boundary at the middle of window 0 — things continuing; the same statistic must show no spike
    w0 = [r for r in mind if win(r) == 0]
    if len(w0) > 200:
        m = len(w0) // 2; prev = w0[m - 50:m]; last50 = float(np.median([p["err"] for p in prev]))
        per = {}
        for t in sorted({q["word"] for q in w0[m:]}):
            errs = [q["err"] for q in w0[m:] if q["word"] == t][:3]
            if len(errs) == 3: per[t] = round(float(np.median(errs)) / last50, 2) if last50 > 0 else None
        out["null_fake_boundary_w0"] = {"at_seq": int(w0[m]["seq"]), "last50_med": round(last50, 4), "spike_ratio_per_thing": per,
                                        "no_spike": all(v is not None and v < 1.5 for v in per.values()) if per else None,   # the §16 record, kept as recorded
                                        # §18 addendum 4 (b2): the graded null clears by MAJORITY under the p95 band (all() failed by construction ~43 % of the time)
                                        "no_spike_regime": null_clears(per, reg["null_band_95"])[0],
                                        "share_under_band_regime": null_clears(per, reg["null_band_95"])[1]}
    # grading: at every window that brings NEW things — majority of the new things spike AND settle (B13's reading, §12)
    # §16 fixed-bar reading — the record; §18 addendum 3 — the regime-derived reading (the top-level verdict grades on it); §18 addendum 4
    # (2026-09-22) — a window whose new things never reached 10 showings (the plant's window) is NOT GRADABLE, never FAIL
    graded, graded_regime, skipped = grade_modulation_windows(out["windows"])
    out["graded_windows"] = graded
    out["graded_windows_regime"] = graded_regime
    out["not_gradable_windows"] = skipped
    nb = out.get("null_fake_boundary_w0", {}) or {}
    out["pass_fixed_bars_record"] = bool(graded) and all(x["pass"] for x in graded) and bool(nb.get("no_spike"))
    out["pass"] = bool(graded_regime) and all(x["pass"] for x in graded_regime) and bool(nb.get("no_spike_regime"))
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): the mark carries `graded`. Not gradable (pass
    # None, never in `marks_failed`) when no window changed, when no window's new things reached 10 showings, or when the fake-boundary
    # null could not be read — alpha4-1's 2 h smoke said «… not gradable» in its reason and was still counted FAILED.
    out["graded"] = True
    if not out["windows"]:
        out["reason"] = "no window change on this tape yet (e.g. a smoke shorter than the maker's window) — not gradable; the regime band is still derived and printed under 'regime'"
        out["graded"] = False
    elif not graded_regime:
        out["reason"] = "not gradable: no window brought a new thing that reached 10 showings (§18 add. 4) — the windows are printed"
        out["graded"] = False
    elif nb.get("no_spike_regime") is None:
        out["reason"] = "not gradable: the fake-boundary null could not be read (window 0 holds ≤ 200 canvases or no regime band)"
        out["graded"] = False
    if not out["graded"]:
        out["pass"] = None
    return out


# ----------------------------------------------------------------------------- main
def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker"); ap.add_argument("--root"); ap.add_argument("--genome", default=str(ROOT / "genome" / "G4.genome"))
    ap.add_argument("--out"); ap.add_argument("--hours", type=float, default=24.0); ap.add_argument("--random", type=int, default=20)
    ap.add_argument("--slice-hours", type=float, default=6.0); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--regime-step", type=int, default=100, help="MODULATION: the fake-boundary sampling step over window 0 (100 = the recorded default; 25 for a 2 h window)")
    ap.add_argument("--nrestarts", type=int); ap.add_argument("--cpu-ns", type=int); ap.add_argument("--unit")
    ap.add_argument("--skip-twins", action="store_true"); ap.add_argument("--skip-random", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="re-grade: read twin summaries already under --out instead of replaying")
    ap.add_argument("--sizing-prediction", type=float, default=None, help="PREREG §19.11: the pre-flight's predicted sight births by 24 h (absent = SIZING not gradable)")
    # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:50 +0400 — A4L-LANG L5: the WHERE pointing ceiling measured BEFORE the life
    # (task 0 (b), tools/chat_ceiling.py on alpha4-1's 10:54 snapshot copy); the default is that pre-registered number.
    ap.add_argument("--chat-pointing-ceiling", type=float, default=None, help="A4-LADDER-PREREG §3.4 L5: the pre-life pointing ceiling (default: tools/verdict_life.CHAT_POINTING_CEILING_PRELIFE)")
    # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:30 +0400 — READER v3.5: the second roots the ladder-2 marks read (read-only; never replayed)
    ap.add_argument("--identity-root", default=None, help="A4-LADDER-2-PREREG ADDENDUM §7(2): R0b's twin life (a CLOSED root) — the IDENTITY mark compares per source stream and at equal per-source canvas counts; absent = not gradable")
    ap.add_argument("--identity-hours", type=float, default=None, help="cut the identity root at ITS OWN t0 + H (default: read it whole; its wall-clock reading is at its t0 + --hours)")
    ap.add_argument("--control-root", default=None, help="A4-LADDER-2-PREREG §3: R0's closed root for R1–R3's one-difference readings (NURSERY's HEARD and READ vs R0; LINE's game frames beside R0's)")
    ap.add_argument("--line-ceiling", type=float, default=None, help="R2 LINE: the ceiling printed beside (default tools/verdict_life.LINE_CEILING, B2's 0.272)")
    a = ap.parse_args(argv)
    global REUSE; REUSE = bool(a.reuse)
    if a.worker:
        return worker(Path(a.worker))
    T0 = time.perf_counter()
    root = Path(a.root).resolve(); genome_path = Path(a.genome).resolve(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    from genome.machinery import parse_genome
    from genome import run_g0, world
    g = parse_genome(genome_path.read_text())
    R: Dict[str, object] = {"root": str(root), "genome": str(genome_path), "genome_sha": __import__("hashlib").sha256(genome_path.read_bytes()).hexdigest()[:16],
                            "reader": READER_VERSION, "reader_commit": _git_head(Path(__file__).resolve().parent.parent), "life_commit": _life_commit(root), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hours": a.hours}
    nrestarts, cpu_ns = a.nrestarts, a.cpu_ns
    if a.unit:
        try:
            sh = subprocess.run(["systemctl", "--user", "show", a.unit, "-p", "NRestarts", "-p", "CPUUsageNSec"], capture_output=True, text=True).stdout
            kv = dict(l.split("=", 1) for l in sh.strip().splitlines())
            nrestarts = int(kv.get("NRestarts", nrestarts or 0)); cpu_ns = int(kv.get("CPUUsageNSec", cpu_ns or 0))
        except Exception as e:
            R["unit_read_error"] = str(e)
    print(f"[gather] root {root} cut at {a.hours} h", flush=True)
    G = gather(root, out, a.hours)
    R["tape_rows"] = len(G["tape"]); R["mind_rows_live"] = len(G["mind"]); R["exams_in_window"] = [e["_file"] for e in G["exams"]]
    # edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: the world's window beside the cut, and the lag whole
    R["tape_rows_world"] = len(G["tape_world"]); R["LAG"] = G["lag"]; LAG_S = lag_summary(G["lag"])
    print(f"[LAG] {lag_text(LAG_S)}", flush=True)
    R["ALIVE"] = alive(G, a.hours, nrestarts)
    print(f"[ALIVE] {R['ALIVE']['pass']} hours {R['ALIVE']['hours_on_tape']} moved {R['ALIVE']['every_counter_moved_every_hour']} gaps {R['ALIVE']['max_gap_s_eye_ear']}", flush=True)

    tape_all = out / "tape" / "ALL.jsonl"
    twins_dir = out / "twins"; twins_dir.mkdir(exist_ok=True)
    base_text = genome_path.read_text()
    first_fix = twins_dir / "first-fixation.genome"; first_fix.write_text(genome_twin_text(base_text, "T-first-fixation", fixations=1))
    frozen10 = twins_dir / "frozen-10.genome"; frozen10.write_text(genome_twin_text(base_text, "T-frozen-10", frozen_after=10))
    specs = [{"label": "unblinded-1", "root": str(twins_dir / "unblinded-1"), "tape": str(tape_all), "genome": str(genome_path)},
             {"label": "unblinded-2", "root": str(twins_dir / "unblinded-2"), "tape": str(tape_all), "genome": str(genome_path)}]
    if not a.skip_twins:
        specs += [{"label": f"blind-{b}", "root": str(twins_dir / f"blind-{b}"), "tape": str(tape_all), "genome": str(genome_path), "blind": [b]} for b in BLINDS]
        specs += [{"label": "T-shuffle", "root": str(twins_dir / "T-shuffle"), "tape": str(tape_all), "genome": str(genome_path), "shuffle_words": True},
                  {"label": "T-nowire", "root": str(twins_dir / "T-nowire"), "tape": str(tape_all), "genome": str(genome_path), "nowire": True},
                  {"label": "T-one-glance", "root": str(twins_dir / "T-one-glance"), "tape": str(tape_all), "genome": str(genome_path), "one_glance": True},
                  {"label": "T-first-fixation", "root": str(twins_dir / "T-first-fixation"), "tape": str(tape_all), "genome": str(first_fix)},
                  {"label": "T-frozen-10", "root": str(twins_dir / "T-frozen-10"), "tape": str(tape_all), "genome": str(frozen10), "blind": ["frozen"]}]
    # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:31 +0400 — A4L-LANG L1: the READ-ONLY law's twin is the LANG rung's OWN twin set
    # (A4-LADDER-PREREG §4: «each with its twin set only … LANG + blind-chat»), so it runs OUTSIDE `if not a.skip_twins:` — a read
    # with --skip-twins still grades L1 (the first draft sat inside that block; the advisor's catch before the life).
    specs += chat_twin_specs(g.declared, twins_dir, tape_all, genome_path)
    # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:48 +0400 — A4L-VOICE (A4-LADDER-PREREG §4: «VOICE + blind-ear, blind-sound,
    # shuffled-sound»): the rung's OWN twin set, run whenever the life's genome declares the sound area — with or without --skip-twins.
    if "AREA_SOUND" in g.declared:
        specs += [{"label": "blind-ear", "root": str(twins_dir / "blind-ear"), "tape": str(tape_all), "genome": str(genome_path), "blind": ["ear"]},
                  {"label": "blind-sound", "root": str(twins_dir / "blind-sound"), "tape": str(tape_all), "genome": str(genome_path), "blind": ["sound"]},
                  {"label": "T-shuffle-sound", "root": str(twins_dir / "T-shuffle-sound"), "tape": str(tape_all), "genome": str(genome_path), "shuffle_voice": 20260923}]
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (11): READ's blind twin (every shelf row dropped) is
    # one more twin of the set — under --skip-random too (it is not a random twin); skipped with its reason (the clause then reads not
    # gradable, never FAIL) when SENSE_READ is undeclared, under --skip-twins, or when the cut tape carries no shelf row (it would be the
    # unblinded twin again — a replay burned to read nothing).
    shelf_rows_cut = sum(1 for r in G["tape"] if (r.get("meta") or {}).get("source") == "shelf")
    read_blind_reason: Optional[str] = None
    if "SENSE_READ" not in g.declared:
        read_blind_reason = "not gradable: SENSE_READ not declared"
    elif a.skip_twins:
        read_blind_reason = "not gradable: --skip-twins (the blind-shelf twin was not run)"
    elif shelf_rows_cut == 0:
        read_blind_reason = "not gradable: no shelf rows on the cut tape — the blind twin would equal the unblinded one"
    else:
        specs.append({"label": "blind-shelf", "root": str(twins_dir / "blind-shelf"), "tape": str(tape_all), "genome": str(genome_path), "drop_source": "shelf"})
    # edit: Claude (Fable 5.1), 2026-09-22 22:28 +0400 — a CLOSED life read WHOLE (gather's `closed_whole`) ends every whole-tape twin's mind the way the
    # body did; the slice/random twins below cut the tape short and never close (the live mind lands that think at a later boundary).
    for _s in specs:
        if not _s.get("until_seq"):
            _s["close"] = bool(G.get("closed_whole"))
    # (ix): the first --slice-hours of the tape under 20 random genomes (numbers only, structure fixed) and under the creature's own
    slice_seq = 0
    for r in G["tape"]:
        if (_iso(r["at"]) - G["t0"]).total_seconds() <= a.slice_hours * 3600: slice_seq = r["seq"]
    if not a.skip_random:
        specs.append({"label": "slice-own", "root": str(twins_dir / "slice-own"), "tape": str(tape_all), "genome": str(genome_path), "until_seq": slice_seq})
        for seed in range(1, a.random + 1):
            rg = run_g0.random_genome(g, seed); nums = run_g0.genome_numbers(rg)
            gp = twins_dir / f"random-{seed}.genome"; gp.write_text(genome_twin_text(base_text, f"random genome seed {seed}", numbers=nums))
            parse_genome(gp.read_text())   # it must parse before it is spent on
            specs.append({"label": f"random-{seed}", "root": str(twins_dir / f"random-{seed}"), "tape": str(tape_all), "genome": str(gp), "until_seq": slice_seq, "numbers": nums})
    # G4-7's solo: the first 1,000 rows replayed ALONE before any worker starts (a replay under 8 workers is not solo)
    solo_ms = None
    try:
        from creature.mind import Mind
        sroot = out / "solo-probe"; (sroot / "tape").mkdir(parents=True, exist_ok=True)
        _relink(sroot / "tape" / "payload", (root / "tape" / "payload").resolve())
        sm = Mind(genome_path, sroot); srows = [r for r in G["tape"] if r["seq"] <= 1000]
        ts = time.perf_counter()
        for r in srows: sm.consume(r)
        solo_ms = round(1000 * (time.perf_counter() - ts) / max(1, sum(1 for r in srows if r["sense"] == "eye")), 2)
    except Exception as e:
        R["solo_probe_error"] = repr(e)
    R["solo_ms_per_canvas_probe"] = solo_ms
    print(f"[solo] {solo_ms} ms a canvas over the first 1,000 rows, alone", flush=True)
    print(f"[twins] {len(specs)} replays, {a.workers} workers, slice_seq {slice_seq}", flush=True)
    TW = run_workers(specs, a.workers, out)
    R["twins"] = TW

    # REPLAY + (vii): the unblinded replay vs the live journal, and the second unblinded replay vs the first; the planted divergence
    from creature import replay as replay_mod
    live = replay_mod.read_mind_journal(out / "live-journal.jsonl")
    u1 = replay_mod.read_mind_journal(twins_dir / "unblinded-1" / "mind-journal.jsonl")
    u2 = replay_mod.read_mind_journal(twins_dir / "unblinded-2" / "mind-journal.jsonl")
    # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 07:04 +0400 — the M1 boundary (replay_ignore_fields' docstring): `readiness` masked iff git proves exactly one side carries it
    _has_m1 = (lambda c: has_commit(ROOT, M1_JUDGE_UNITS_COMMIT, c))
    _ign = replay_ignore_fields(R.get("reader_commit"), R.get("life_commit"), has_m1=_has_m1)
    d_live = replay_mod.compare(u1, live, ignore=_ign); d_two = replay_mod.compare(u1, u2)   # v3.2: the two-replays comparison masks nothing
    # the plant: the first 1,000 rows with one eye payload's thing inverted (its cell from the root's truth file) must DIVERGE
    plant_ok = None; plant_seq = None
    try:
        from PIL import Image
        rows = [r for r in G["tape"] if r["seq"] <= 1000]
        # edit: Claude (Fable 5.1), 2026-09-21 22:40 +0400 — G5 dry-run (0.1 h of a tape with the game door ON): the first 1,000 rows hold only ~241 MAKER
        # eye rows (the game and folder rows share the seq space), so a fixed index 300 raised IndexError and the plant read as an error.
        # The plant is now the maker eye row WITH a truth file at index 300 when there are more than 300, else the middle one; a G4-shaped
        # tape (maker only, ~500 eye rows in 1,000) picks exactly the row it always picked. The chosen seq is on the record (plant_seq).
        eye = _plant_eye_row(rows, root)
        proot = out / "plant-root"; (proot / "tape").mkdir(parents=True, exist_ok=True); (proot / "tape" / "payload").mkdir(exist_ok=True)
        for r in rows:
            src = root / "tape" / r["payload"]; dst = proot / "tape" / r["payload"]
            if dst.is_symlink() or not dst.exists():
                _relink(dst, src.resolve())
        pp = proot / "tape" / eye["payload"]; pp.unlink()
        arr = np.array(Image.open(root / "tape" / eye["payload"]).convert("RGB"))
        truth = json.loads((root / "truth" / (Path(eye["payload"]).stem + ".json")).read_text())
        cy, cx = truth["cell"]; y0, x0 = max(0, min(int((cy + 0.5) * 8) - 12, 104)), max(0, min(int((cx + 0.5) * 8) - 12, 104))
        arr[y0:y0 + 24, x0:x0 + 24] = 255 - arr[y0:y0 + 24, x0:x0 + 24]; Image.fromarray(arr).save(pp, format="PNG")
        (proot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        if (proot / "replay").exists(): shutil.rmtree(proot / "replay")   # §18: a --reuse re-grade recomputes the plant in the reader's own scratch (FileExistsError otherwise)
        pj = replay_mod.run_replay(genome_path, proot / "tape" / "ALL.jsonl", proot / "replay")
        dp = replay_mod.compare(replay_mod.read_mind_journal(pj), [r for r in live if int(r["seq"]) <= 1000])
        plant_ok = dp is not None; plant_seq = eye["seq"]; R["replay_plant_diverged_at"] = dp
    except Exception as e:
        R["replay_plant_error"] = repr(e)
    R["REPLAY"] = {"pass": d_live is None and d_two is None and plant_ok is True, "vs_live": d_live, "two_replays": d_two, "mind_rows": len(u1), "hash_masked": sorted(_ign), "closed_whole": bool(G.get("closed_whole")),
                   "plant_seq": plant_seq, "plant_caught": plant_ok,
                   "cut_seq": G["last_seq"], "lag": LAG_S}     # READER-LAG-0923: the replays and the live journal are compared up to the cut; the tail printed
    if "readiness" in _ign:     # READER v3.5: the M1 mask, named with its commit, both sides' ancestry and the count it covers (never a silent mask)
        R["REPLAY"]["readiness_mask"] = {"m1_commit": M1_JUDGE_UNITS_COMMIT, "reader_has_m1": _has_m1(R.get("reader_commit")),
                                         "life_has_m1": _has_m1(R.get("life_commit")), **readiness_rows_differing(u1, live),
                                         "rule": "A4-LADDER-2-PREREG §2 (M1 a declared machinery difference) and §3 («masked on readiness with the judge-units commit named»)"}
    print(f"[REPLAY] {R['REPLAY']}", flush=True)

    # the organism at the cut = the unblinded replay's snapshot (byte-identical to the live one when REPLAY passes)
    own = own_asks(twins_dir / "unblinded-1", genome_path)
    R["own_asks"] = own
    U = TW["unblinded-1"]; E = U["exam"]; seen = E["ask_seen_words"]; allw = E["ask_all_words"]
    last_live_exam = G["exams"][-1] if G["exams"] else None
    def q(twin, key="Q1"):
        # §16 addendum 2: every TWIN is read on ask_all_words (the same 160-question denominator as the creature's all-words Q1) —
        # a twin that met only 2 words scored .75 on its own 20 questions and .094 on the 160 (the control run, 13:2x)
        t = TW.get(twin, {}); ex = t.get("exam") or {}; return (ex.get("ask_all_words") or {}).get(key, {}).get("acc")
    Q1_ALL = allw["Q1"]["acc"]
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): EVERY mark carries `graded` (partition_marks
    # builds `marks_failed` from graded marks only). A mark read off a twin that did not run (--skip-twins, a worker error) is NOT GRADABLE
    # with the twin's own error in its reason — never FAIL, never silently PASS.
    def _twins_missing(*labels) -> Optional[str]:
        miss = [f"{l} ({TW.get(l, {}).get('error') or ('not run' if l not in TW else 'no exam')})" for l in labels if q(l) is None]
        return ("not gradable: twin " + ", ".join(miss) + " — the reading does not exist") if miss else None
    M: Dict[str, dict] = {}
    M["i_knows"] = {"graded": True, "pass": seen["Q1"]["acc"] >= .80 and seen["Q2"]["acc"] >= .80 and seen["Q3"]["acc"] >= .85 and seen["Q4"]["acc"] >= .90,
                    "Q1": seen["Q1"]["acc"], "Q2": seen["Q2"]["acc"], "Q3": seen["Q3"]["acc"], "Q4": seen["Q4"]["acc"], "chance_Q1": E["chance_q1"],
                    "all_words": {k: allw[k]["acc"] for k in ("Q1", "Q2", "Q3", "Q4")}, "per_thing_Q1": seen["Q1"]["per_thing"],
                    "live_exam_last": {k: (last_live_exam["ask_seen_words"][k]["acc"] if last_live_exam else None) for k in ("Q1", "Q2", "Q3", "Q4")},
                    "bar": "Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90"}
    M["ii_meeting_real"] = {"pass": (q("T-shuffle") is not None and q("T-shuffle") <= .20) and (q("T-nowire") is not None and q("T-nowire") <= .20),
                            "T_shuffle_Q1": q("T-shuffle"), "T_nowire_Q1": q("T-nowire"), "bar": "≤ .20"}
    M["iii_growth_matters"] = {"pass": q("T-frozen-10") is not None and q("T-frozen-10") <= Q1_ALL - .30, "T_frozen_10_Q1": q("T-frozen-10"), "T_frozen_50_Q1": q("blind-frozen"),
                               "T_frozen_10_cells": TW.get("T-frozen-10", {}).get("cells"), "Q1": Q1_ALL, "bar": "≥ 30 pp under on all 16 words (the twin FROZEN after 10 cells, G0b's; the 50-cell twin printed — §16 addenda)"}
    for _k, _labels in (("ii_meeting_real", ("T-shuffle", "T-nowire")), ("iii_growth_matters", ("T-frozen-10",))):
        _why = _twins_missing(*_labels)
        M[_k].update(graded=_why is None, **({"pass": None, "reason": _why} if _why else {}))
    c = U["c"]; pruned_share = c["edges_pruned"] / c["edges_born"] if c["edges_born"] else 0.0
    refused = iv_refusals(c)   # §18 addendum 4 (2026-09-22): every CAP refusal counts — budget, nmax, frozen; redundant printed only
    M["iv_grows_alone"] = {"graded": True, "pass": U["cells_born"] >= 50 and refused["caps_total"] == 0 and pruned_share >= .05 and c["removed_for_disuse"] == 0,
                           "cells_born": U["cells_born"], "births_refused_budget": c["births_refused_budget"], "refused": refused, "arrivals": U["arrivals"], "budget_left": U["budget_left"],
                           "pruned_share": round(pruned_share, 4), "edges_born": c["edges_born"], "edges_pruned": c["edges_pruned"], "edges_cross": U["edges_cross"],
                           "removed_for_disuse": c["removed_for_disuse"], "bar": "≥ 50 born · 0 refused at ANY cap (budget · nmax · frozen; §18 add. 4) · ≥ 5 % pruned · 0 by disuse"}
    # (v) §15's pair: per odd window, the LAST exam inside it vs the LAST exam of the preceding even window, Q1 on the seen eleven
    seq_at = {r["seq"]: r for r in G["tape"]}
    def window_of(ex):
        s = ex.get("snapshot_last_seq") or 0
        # §18 hardening: walk back to the nearest MAKER row (a folder row's moment is "f<sha>", not a window)
        while s > 0 and (s not in seq_at or not str((seq_at[s].get("meta") or {}).get("moment", "")).startswith("w")): s -= 1
        return int(seq_at[s]["meta"]["moment"][1:5]) if s in seq_at else None
    by_w: Dict[int, List[dict]] = {}
    for ex in G["exams"]:
        w = window_of(ex)
        if w is not None: by_w.setdefault(w, []).append(ex)
    pairs = []
    for w in sorted(by_w):
        if w % 2 == 1 and (w - 1) in by_w:
            before = by_w[w - 1][-1]; first_after = by_w[w][0]; last_in = by_w[w][-1]
            q1 = lambda ex: ex["ask_seen_words"]["Q1"]["acc"]
            pairs.append({"window": w, "before": q1(before), "first_after": q1(first_after), "last_in_window": q1(last_in), "drop_pp": round(100 * (q1(before) - q1(last_in)), 1),
                          "files": [before["_file"], first_after["_file"], last_in["_file"]]})
    M["v_retention"] = retention_mark(pairs)      # READER-FIX-0923 (9): no pair → not gradable, never FAIL
    p, n = own["plant"], own["null"]
    from tools import verdict_life as _vl
    _plant_shown = _vl.plant_showings(G["mind"], world.THING_PLANT)   # READER-FIX-0923 (10): one count for (vi), GRADE and SIZING
    M["vi_knows_unknown"] = vi_mark(p, n, seen["Q5"][world.THING_NEVER]["abstain_rate"], seen["Q1"]["false_abstention"], plant_shown=_plant_shown)
    M["vii_replay"] = {"graded": True, "pass": R["REPLAY"]["pass"], **{k: v for k, v in R["REPLAY"].items() if k != "pass"}, "bar": "two replays byte-identical; the plant caught"}
    st = G["status"]
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — (viii) in ONE unit (#162): the per-row median it read until today is not the probe's ms per canvas
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (2): a GROW life is graded against ALPHA4-PREREG §8b's
    # FUNCTION of its own final cell count (0.09 ms × cells × 1.5); G4-7 printed beside as `g4_7`; the older records read G4-7 as before.
    _sleeps_window = None
    # edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: a sleep's time is its triggering canvas's TAPE time; STATUS's
    # heartbeat is WALL time. Under a lag cut the mind's «now» on the tape is its last consumed row's `at`, and that is the window's end.
    _sw_ref = None
    try:
        _hb = G["lag"].get("mind_last_at") if (G["lag"].get("cut") and G["lag"].get("mind_last_at")) else st.get("heartbeat_at")
        if _hb:
            _hbt = _iso(_hb); _sw_ref = _hb
            _sleeps_window = sum(1 for _s, _t in _vl.sleep_times(G["tape"], G["mind"]) if 0 <= (_hbt - _t).total_seconds() <= 180)
    except Exception:
        _sleeps_window = None
    M["viii_cost"] = viii_cost(st, R.get("solo_ms_per_canvas_probe") or U["ms_per_canvas"], U["ms_per_canvas"], cpu_ns,
                               grow=("GROW" in g.declared), sleeps_in_window=_sleeps_window,
                               lag={**LAG_S, "sleeps_window_end": _sw_ref,
                                    "sleeps_window_end_is": ("the mind's last consumed row's tape time (a lag cut: the heartbeat is wall time, a sleep's time is its canvas's tape time)"
                                                             if G["lag"].get("cut") else "STATUS heartbeat_at")})
    if not a.skip_random:
        comps = []
        for k, t in TW.items():
            if k == "slice-own" or k.startswith("random-"):
                ex = t.get("exam") or {}; comp = (ex.get("ask_seen_words") or {}).get("composite")
                comps.append({"label": k, "composite": comp, "cells": t.get("cells"), "numbers": t.get("numbers")})
        ranked = sorted([x for x in comps if x["composite"] is not None], key=lambda x: -x["composite"])
        rank = next((i + 1 for i, x in enumerate(ranked) if x["label"] == "slice-own"), None)
        M["ix_not_luck"] = {"pass": rank is not None and rank <= max(1, len(ranked) // 4) + (1 if len(ranked) % 4 else 0) and rank <= 5,
                            "rank_of_own": rank, "of": len(ranked), "own_composite": next((x["composite"] for x in comps if x["label"] == "slice-own"), None),
                            "best_random": next((x for x in ranked if x["label"] != "slice-own"), None), "slice_seq": slice_seq, "bar": "top quartile of 20 random genomes (rank ≤ 5 of 21), numbers only, on the first slice"}
        # READER-FIX-0923 (9): no rank = the slice-own twin's exam does not exist — not gradable, its error printed
        M["ix_not_luck"]["graded"] = rank is not None
        if rank is None:
            M["ix_not_luck"].update(**{"pass": None, "reason": "not gradable: no composite for slice-own (%s)" % (TW.get("slice-own", {}).get("error") or "no exam")})
    lx = E["gaze_landing"]; lr = own["random_landing"]
    M["x_gaze_finds_thing"] = {"graded": True, "pass": lx["rate"] >= .90 and lx["rate"] >= 1.5 * lr["rate"], "gaze_rate": lx["rate"], "random_rate": lr["rate"], "random_ceiling_expected": 0.069,
                               "ratio": round(lx["rate"] / lr["rate"], 2) if lr["rate"] else None, "bar": "≥ .90 in the first 2 fixations · ≥ 1.5× random"}
    M["xi_gaze_earns_place"] = {"pass": q("T-one-glance") is not None and Q1_ALL - q("T-one-glance") >= .10, "Q1_gaze": Q1_ALL, "Q1_one_glance": q("T-one-glance"),
                                "Q1_first_fixation_only": q("T-first-fixation"), "Q1_random_gaze": q("blind-gaze"),
                                "bar": "≥ .10 over G1's one-glance twin (gaze mode 'one': the whole canvas at glance×glance); the first-fixation-only twin printed — §16 addendum"}
    _why = _twins_missing("T-one-glance")
    M["xi_gaze_earns_place"].update(graded=_why is None, **({"pass": None, "reason": _why} if _why else {}))
    F = 1.0 - g.theta_n
    # edit: Claude (Sonnet 5, builder H), 2026-09-21 18:44 +0400 — §18 addendum 3: the bar text now names both readings; M["MODULATION"]["pass"] grades on the regime-derived one (modulation()'s own doc)
    M["MODULATION"] = modulation(G, F, regime_step=a.regime_step)
    M["MODULATION"]["bar"] = ("§18 addendum 3: at every window bringing NEW things, a majority spike (≥ 3× the last-50 median AND ≥ the life's own regime null-band) and settle "
                              "(≤ the life's own regime settle-bar) by the 10th showing; the fake-boundary null clears the same band. "
                              "The §16 record (3× spike / 1.25× settle / 1.5× null, calibrated pre-W3-2b) is printed as 'pass_fixed_bars_record'.")
    np_err = None
    if "blind-predict" in TW and (twins_dir / "blind-predict" / "mind-journal.jsonl").exists():
        errs = [r["err"] for r in read_jsonl(twins_dir / "blind-predict" / "mind-journal.jsonl") if "moment" in r and "err" in r]
        np_err = {"max_err": max(errs) if errs else None, "n": len(errs)}
    M["MODULATION"]["no_predict_twin_err"] = np_err
    parked = U["parked"]
    M["PLANTS"] = {"vi": M["vi_knows_unknown"]["pass"], "predict_file_pair": "cannot fire on the maker's ear-then-eye stream (§14); predictions_filed " + str(st.get("predictions_filed")),
                   "park_unanswerable_want": "the folder door is OFF (§6)", "sleep_replay": {"sleeps": U["sleeps"], "no_sleep_twin_sleeps": TW.get("blind-sleep", {}).get("sleeps")},
                   "belief_contradiction": "clash unwired (§14)"}
    M["TWINS"] = {b: {"Q1": q(f"blind-{b}"), "Q1_seen": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_seen_words") or {}).get("Q1", {}).get("acc"),
                      "composite": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_all_words") or {}).get("composite"), "cells": TW.get(f"blind-{b}", {}).get("cells")} for b in BLINDS}
    M["TWINS"]["random_gaze_loses_xi"] = {"pass": q("blind-gaze") is not None and Q1_ALL - q("blind-gaze") >= .10, "margin": None if q("blind-gaze") is None else round(Q1_ALL - q("blind-gaze"), 3)}
    _why = _twins_missing("blind-gaze")      # READER-FIX-0923 (9)
    M["TWINS"]["random_gaze_loses_xi"].update(graded=_why is None, **({"pass": None, "reason": _why} if _why else {}))
    M["TWINS"]["no_sleep_v"] = {"graded": False, "reason": "SLEEP's retention is not gradable on drawn worlds (§10)", "no_sleep_Q1": q("blind-sleep")}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door mark needs the folder/web door (OFF)"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "PARK unreadable (folder OFF)"}
    # ------------------------------------------------------------------ §18 (edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400): W3-2, DOOR, W3-1, PARK graded
    decl = g.declared
    def _pred_rows(twin_root: Path) -> List[dict]:
        pth = twin_root / "state" / "predictions.jsonl"
        return read_jsonl(pth) if pth.exists() else []
    def _rule_stats(rows: List[dict]) -> dict:
        rules = [r for r in rows if ("cluster" in r or "shared" in r)]
        filed = [r for r in rules if r.get("accepted") and r.get("outcome") is None]
        refused = [r for r in rules if not r.get("accepted")]
        scored = [r for r in rules if r.get("outcome") in (True, False)]
        acc = (sum(1 for r in scored if r["outcome"] is True) / len(scored)) if scored else None
        words = sorted(set(str(r.get("word") or (r.get("words") or ["?"])[0]) for r in rules))
        sight_road = [r for r in rows if not ("cluster" in r or "shared" in r)]
        return {"filed": len(filed), "refused": len(refused), "scored": len(scored), "accuracy": None if acc is None else round(acc, 3), "words": words,
                "induce": sum(1 for r in rules if "cluster" in r), "deduce": sum(1 for r in rules if "shared" in r), "sight_road_rows": len(sight_road)}
    live_pred = _rule_stats(_pred_rows(twins_dir / "unblinded-1")); shuf_pred = _rule_stats(_pred_rows(twins_dir / "T-shuffle"))
    # edit: Claude (Fable 5.1), 2026-09-21 15:21 +0400 — §18 addendum 2 (the #162 control on W3-2): a rule's CLUSTER must be the word's OWN cells.
    # Life 3a's INDUCE compared a sight cell id to a words index (genome/think.py:411, fixed at the life-3b boundary), so its rules were
    # induced from ANOTHER word's cells and scored 6/6 by accident. Read from the ROOT's OWN predictions and END snapshot (never the replay,
    # which runs the current code): per induce rule, the share of its cluster that answers its word at the end; the eligible-word count
    # (words with ≥ 1 own cell) is the denominator printed beside the accuracy. Refuses to grade PASS when any scored/filed rule's cluster
    # share < .5 (wrong cells) or fewer than 5 words are eligible.
    def _cluster_control(root: Path) -> dict:
        try:
            from genome.machinery import Organism as _Org
            from genome import world as _world
            org = _Org.load(root / "state" / "organism", g)
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}", "ok": False}
        L = json.loads((root / "state" / "ledger.json").read_text())
        words = sorted({w for s in L["words"].values() for w in s if w})
        own: Dict[str, List[int]] = {}
        for w in words:
            r = org.recall("words", _world.encode_word(w, g.ear_blank_zero))
            lit = r.get("lit")
            own[w] = [] if lit is None else sorted(int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == lit)
        eligible = sorted(w for w in words if own[w])
        rows = read_jsonl(root / "state" / "predictions.jsonl") if (root / "state" / "predictions.jsonl").exists() else []
        per_rule = []
        for r in rows:
            if "cluster" not in r or not r.get("accepted"):
                continue
            w = str(r.get("word")); cl = [int(c) for c in (r.get("cluster") or [])]
            share = (sum(1 for c in cl if c in set(own.get(w, []))) / len(cl)) if cl else 0.0
            per_rule.append({"word": w, "cluster": len(cl), "own_share": round(share, 3), "outcome": r.get("outcome")})
        wrong = [x for x in per_rule if x["own_share"] < .5]
        reached = sorted({x["word"] for x in per_rule})          # the words the mechanism actually REACHED (life 3a: 1 of 21 — «bar», by a coincidence of ids)
        ok = (len(eligible) >= 5) and not wrong and (len(reached) >= 5)
        return {"eligible_words": len(eligible), "words": len(words), "own_cells": {w: len(own[w]) for w in words}, "rules": per_rule,
                "wrong_cell_rules": len(wrong), "words_with_rules": len(reached), "reached": reached, "ok": ok,
                "reason": "" if ok else w3_2_reason(len(eligible), len(reached), wrong)}   # §18 add. 4: the reason names the clause that failed
    cluster_ctl = _cluster_control(root)
    think_rows = [r for r in G["mind"] if "think" in r]
    parked_rules = sum(1 for r in think_rows if (r["think"] or {}).get("kind") == "rule" and (r["think"] or {}).get("parked"))
    rules_declared = ("INDUCE" in decl) or ("DEDUCE" in decl)
    chance = 1.0 / 11 + .10
    shuffle_ok = (shuf_pred["scored"] == 0) or (shuf_pred["accuracy"] is not None and shuf_pred["accuracy"] <= chance)
    M["W3_2_rules"] = {"graded": rules_declared,
                       "pass": rules_declared and live_pred["filed"] + live_pred["scored"] > 0 and live_pred["scored"] > 0 and (live_pred["accuracy"] or 0.0) >= .80 and shuffle_ok and bool(cluster_ctl.get("ok")),
                       "cluster_control": cluster_ctl,
                       "live": live_pred, "T_shuffle": shuf_pred, "parked_rules": parked_rules, "shuffle_bar": "≤ 1/11 + .10 when any rule is scored; 0 scored = the shuffle destroyed the meeting (D's toy)",
                       "bar": "filed > 0 · scored > 0 · accuracy ≥ .80 (W3-2c's decider) · the shuffled-words twin at chance · every rule's cluster ≥ .5 the word's OWN cells · rules reach ≥ 5 of ≥ 5 eligible words (§18 add. 2)",
                       "reason": ("" if rules_declared else "INDUCE/DEDUCE not declared in this life's genome — not graded") + (cluster_ctl.get("reason") or "")}
    tape = G["tape"]
    folder_rows = [r for r in tape if (r.get("meta") or {}).get("source") == "folder"]
    f_ear_moments = {(r.get("meta") or {}).get("moment") for r in folder_rows if r["sense"] == "ear"}
    f_pics = [r for r in folder_rows if r["sense"] == "eye"]
    sight_only = [r for r in f_pics if (r.get("meta") or {}).get("moment") not in f_ear_moments]
    folder_words = sorted({(r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"} - {None})
    recog = {}
    try:
        from tools import self_exam as _se2
        from genome import ask as _gask
        _g2, _org2, _led2, _L2 = _se2.load_snapshot(twins_dir / "unblinded-1", genome_path)
        _Lw2 = _led2["words"]; _h2 = _org2.state_hash()
        by_word: Dict[str, list] = {}
        for r in folder_rows:
            if r["sense"] == "ear": by_word.setdefault((r.get("meta") or {}).get("word"), [])
        moment_word = {(r.get("meta") or {}).get("moment"): (r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"}
        for r in f_pics:
            w = moment_word.get((r.get("meta") or {}).get("moment"))
            if w and len(by_word.get(w, [])) < 3: by_word.setdefault(w, []).append(r)
        for w, pics in by_word.items():
            hits = 0
            for r in pics:
                res = _org2.recall_many("sight", _gask.glance_picture(root / "tape" / r["payload"], _g2))
                ans = "/".join(sorted(_Lw2.get(res["cell"], set()))) if res.get("cell") is not None else None
                hits += int(ans == w)
            recog[w] = {"asked": len(pics), "own_word": hits}
        assert _org2.state_hash() == _h2
    except Exception as e:
        recog = {"error": repr(e)}
    door_graded = bool(decl.get("WORLD", {}).get("folder"))
    M["DOOR"] = {"graded": door_graded, "pass": door_graded and len(f_pics) >= 300 and len(folder_words) >= 11,
                 "folder_rows": len(folder_rows), "pictures": len(f_pics), "sight_only_rows": len(sight_only), "sight_only_first_seq": sight_only[0]["seq"] if sight_only else None,
                 "folder_words": folder_words, "recognition_of_seen_pictures": recog,
                 "bar": "≥ 300 pictures on the tape · ≥ 11 folder words heard (§18); sight-only rows and recognition REPORTED (§8)",
                 "reason": "" if door_graded else "no `folder <dir>` in the WORLD line — the door is OFF"}
    bel_path = twins_dir / "unblinded-1" / "state" / "beliefs.jsonl"
    bel_rows = read_jsonl(bel_path) if bel_path.exists() else []
    heard = sorted({(r.get("meta") or {}).get("word") for r in tape if r["sense"] == "ear"} - {None})
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — the bar accounts for the clash law's own fresh belief row (found on the six 2 h smokes)
    M["W3_1_beliefs"] = w3_1_beliefs(bel_rows, decl, heard)
    kinds = M["W3_1_beliefs"]["kinds"]
    M["PARK"] = {"graded": True, "pass": parked >= 1 and (parked / U["thinks"] <= .05 if U["thinks"] else False), "parked": parked, "thinks": U["thinks"],
                 "parked_share": round(parked / U["thinks"], 4) if U["thinks"] else None, "parked_rules": parked_rules,
                 "no_park_twin_parked": TW.get("blind-park", {}).get("parked"),
                 "reason": "graded in this life (§18): a dead end can arrive from a rule failed 3× or a wordless sight; sight-only rows on this tape: %d" % len(sight_only),
                 "bar": "≥ 1 parked · share ≤ 5 %"}
    # edit: Claude (Fable 5.1), 2026-09-22 19:3x +0400 — THE ONE LIFE's marks (PREREG §19.5/§19.10/§19.11; plan L-1): pure functions in
    # tools/verdict_life.py; each reads «not gradable» on a record whose life did not declare the line (the closed records are the control).
    from tools import verdict_life as _vl
    M["ACT"] = _vl.act_mark(tape, live, st)
    if M["ACT"].get("graded"):
        # the shuffled-act PLANT (§19.5's control): the first rows up to the 20th mind-chosen game outcome, every such outcome's act moved
        # to the next one; the replay must journal an act_mismatch on the first of them, or the check does not check.
        try:
            _mind_out = [r for r in tape if r["sense"] == "outcome" and (r.get("meta") or {}).get("chosen_by") == "mind"]
            _cut = int(_mind_out[min(19, len(_mind_out) - 1)]["seq"])
            _rows = _vl.shift_acts([r for r in tape if int(r["seq"]) <= _cut])
            aroot = out / "act-plant-root"; (aroot / "tape" / "payload").mkdir(parents=True, exist_ok=True)
            for r in _rows:
                src = root / "tape" / r["payload"]; dst = aroot / "tape" / r["payload"]
                if r["sense"] == "outcome" and (r.get("meta") or {}).get("chosen_by") == "mind":
                    if dst.is_symlink() or dst.exists(): dst.unlink()
                    _m = r["meta"]; dst.write_text(json.dumps({"act": _m.get("act"), "expected": None, "got": _m.get("got"), "residual": None, "source": "game"}))
                elif dst.is_symlink() or not dst.exists():
                    _relink(dst, src.resolve())
            (aroot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in _rows))
            if (aroot / "replay").exists(): shutil.rmtree(aroot / "replay")
            _pj = replay_mod.run_replay(genome_path, aroot / "tape" / "ALL.jsonl", aroot / "replay")
            _mis = [j for j in replay_mod.read_mind_journal(_pj) if isinstance(j.get("outcome"), dict) and j["outcome"].get("act_mismatch")]
            M["ACT"]["shuffled_twin_diverged"] = bool(_mis); M["ACT"]["shuffled_twin_first_mismatch_seq"] = (int(_mis[0]["seq"]) if _mis else None)
            M["ACT"]["pass"] = bool(M["ACT"]["pass"]) and bool(_mis)
        except Exception as e:
            M["ACT"]["shuffled_twin_diverged"] = None; M["ACT"]["shuffled_twin_error"] = repr(e); M["ACT"]["pass"] = False
    else:
        M["ACT"]["shuffled_twin_diverged"] = "not run (not gradable)"
    M["SOUND"] = _vl.sound_mark(tape, live, st)
    # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:48 +0400 — A4L-VOICE's marks (A4-LADDER-PREREG §2.3): V1 on the blind-ear twin, V2/V5
    # on the organism at the cut (the unblinded replay), both nulls on the shuffled-sound twin; V3 against the blind-sound twin; V4 printed from STATUS.
    def _ask_sound_of(label):
        return ((TW.get(label, {}) or {}).get("exam") or {}).get("ask_sound")
    M["HEAR"] = _vl.hear_mark((E or {}).get("ask_sound"), _ask_sound_of("blind-ear"), _ask_sound_of("T-shuffle-sound"))
    M["VOICE_HARM"] = _vl.voice_harm_mark(E, (TW.get("blind-sound", {}) or {}).get("exam"), "AREA_SOUND" in decl)
    M["SOUND_CELLS"] = _vl.sound_cells_mark(st)
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:52 +0400 — ALPHA4-G.md task 5: `grow=` from
    # the life's OWN genome (`decl`, already parsed above for "SELF"/"ANSWER") — never guessed from STATUS
    # shape, so a genome that happens to have a small sight_nmax under NMAX is never mistaken for GROW.
    M["SIZING"] = _vl.sizing_mark(st, live, a.sizing_prediction, grow=("GROW" in decl))
    M["GRADE"] = _vl.grade_mark(own["plant"], own["null"], seen, "ANSWER" in decl, plant_shown=_plant_shown)      # §19.3; READER-FIX-0923 (10)
    M["SELF"] = _vl.self_mark(tape, bel_rows, live, st, "SELF" in decl)                 # §19.6 (builder A's SELF)
    # edit: Claude (Fable 5.1), 2026-09-22 22:33 +0400 — §19.1 as re-specified: per thing by SOURCE (the eye row's `meta.source` on the tape), the blind-surprise twin's own count
    _src = {int(r["seq"]): ((r.get("meta") or {}).get("source")) for r in tape if r.get("sense") == "eye"}
    M["SURPRISE"] = _vl.surprise_mark(live, st, "SURPRISE" in decl, source_of=_src, twin_status=TW.get("blind-surprise"))   # §19.1 (builder B's confirmed glances)
    M["COARSE"] = _vl.coarse_mark(allw, (TW.get("blind-coarse", {}).get("exam") or {}).get("ask_all_words"), bool((getattr(g, "gaze", None) or {}).get("coarse")))   # §19.4
    M["QUESTION"] = _vl.question_mark(live, tape, st, float(a.hours), "QUESTION" in decl)   # §19.7 (builder C's question rows; the world's `answering` rows)
    if G["lag"].get("cut"):      # READER-LAG-0923: the bar keeps --hours; the world hours the mind lived printed beside (the report names it)
        M["QUESTION"]["hours_lived"] = round(G["hours_on_tape"], 3)
    M["SENTENCE"] = _vl.sentence_mark(tape, st, "SENTENCE" in decl)                        # §19.8 + the ceiling clause (the world's own pair skew)
    # §19.9 HANDS (builder F): the reader ASKS the hands' rendered canvases (up to 50) through the unblinded twin's organism and grades
    # the program's own shape; the shuffled-shelf twin = the same asks with the shapes permuted by a fixed rng.
    _hrows = _vl.hands_rows(tape)[:50]; _hrecog = None
    if "HANDS" in decl and _hrows:
        try:
            from tools import self_exam as _se3
            from genome import ask as _gask3
            _g3, _org3, _led3, _L3 = _se3.load_snapshot(twins_dir / "unblinded-1", genome_path)
            _Lw3 = _led3["words"]; _h3 = _org3.state_hash()
            _answers = []
            for r in _hrows:
                res = _org3.recall_many("sight", _gask3.glance_picture(root / "tape" / r["payload"], _g3))
                _answers.append("/".join(sorted(_Lw3.get(res["cell"], set()))) if res.get("cell") is not None else None)
            assert _org3.state_hash() == _h3
            _shapes = [(r.get("meta") or {}).get("shape") for r in _hrows]
            _perm = np.random.default_rng(7).permutation(len(_shapes))
            _hrecog = {"asked": len(_hrows), "hits": sum(1 for a, s_ in zip(_answers, _shapes) if a == s_),
                       "shuffled_hits": sum(1 for a, k in zip(_answers, _perm) if a == _shapes[int(k)])}
        except Exception as e:
            _hrecog = {"asked": 0, "error": repr(e)}
    M["HANDS"] = _vl.hands_mark(st, _hrows, _hrecog, "HANDS" in decl)
    # edit: Claude (Fable 5.1), 2026-09-23 04:05 +0400 — ALPHA4-PREREG §5 READ (builder H's mark, wired at integration — H's report deferred
    # this three-line pattern to the integrator): the reader ASKS the last 50 words the shelf reader HEARD (the record's own
    # `read/HEARD.json`, builder H's HELD-OUT font) through the unblinded twin's organism via H's own instrument
    # (tools/read_recognised.py, recall_many — never mutating, its state_hash pinned inside). The BLIND twin (the same tape with
    # the shelf rows dropped) is NOT run by this reader yet: `recog_blind=None` and the mark says so in its reason ("the blind
    # twin was not run — that clause FAILS") — a reader-only addition owed after alpha4-1's launch, never a loosened bar.
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (6) + (11): the 50 words are a FIXED-SEED sample over
    # the whole of HEARD.json that the shelf ALONE heard on the cut tape (`read_sample` — the newest 50 were the least-exposed words; a word
    # also heard from the lexicon's glosses would let the blind twin answer it), printed; the BLIND twin is the `blind-shelf` twin of the set
    # (its snapshot asked the same 50 words; its replay seconds printed) or, when it could not run, `read_blind_reason` — not gradable.
    _rrecog = None; _rblind = None; _rsample = None
    if "SENSE_READ" in decl:
        try:
            import json as _json_r
            from tools import read_recognised as _rr
            _heard_p = root / "read" / "HEARD.json"
            _heard = _json_r.loads(_heard_p.read_text()) if _heard_p.exists() else []
            _rsample = _vl.read_sample(_heard, tape)
            _words_r = list(_rsample["words"])
            if len(_words_r) >= 50:
                _rrecog = _rr.recognised_share(twins_dir / "unblinded-1", genome_path, _words_r)
                if read_blind_reason is None:
                    _bt = TW.get("blind-shelf", {})
                    if _bt.get("error") or not (twins_dir / "blind-shelf" / "state" / "organism.npz").exists():
                        read_blind_reason = "not gradable: the blind-shelf twin did not run (%s)" % (_bt.get("error") or "no snapshot")
                    else:
                        _rblind = _rr.recognised_share(twins_dir / "blind-shelf", genome_path, _words_r)
                        _rblind["seconds"] = _bt.get("seconds"); _rblind["rows_replayed"] = _bt.get("rows_replayed")
            else:
                _rrecog = {"n": 0, "share": None, "note": _rsample.get("note") or f"only {len(_words_r)} shelf words; the mark asks 50"}
        except Exception as e:
            _rrecog = {"n": 0, "share": None, "error": repr(e)}
    M["READ"] = _vl.read_mark(tape, live, "SENSE_READ" in decl, _rrecog, _rblind, sample=_rsample, blind_reason=(None if _rblind is not None else read_blind_reason))
    M["THREAD"] = _vl.thread_mark(R["ALIVE"], st, bool((decl.get("THINK") or {}).get("threaded")), tape=tape, journal=live)   # §19.2; READER-FIX-0923 (7): gaps attributed to sleeps
    if G["lag"].get("cut"):      # READER-LAG-0923
        M["THREAD"]["lag_note"] = ("the graded max gap is ALIVE's (the world's window, the unconsumed tail included); the attribution reads the tape the mind "
                                   "lived (to seq %s), by TAPE time — under a lag a sleep's wall time trails its canvas's tape time by the lag, so the "
                                   "attribution is approximate there" % G["last_seq"])
    # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §5/§6: EVOLVE. The negative
    # control (brief item 4) is run ONCE, before the life, by `tools/evolve.py --negative-control` with `--out`
    # pointing into the life's own `evolve/` dir — its two files persist as part of the record; this reader loads
    # them if present (never re-runs them: a planted-bad/null mutant is never part of the real tape).
    _nc_bad_path = root / "evolve" / "NEGATIVE-CONTROL-planted_bad.json"
    _nc_null_path = root / "evolve" / "NEGATIVE-CONTROL-null.json"
    _evolve_nc = None
    if _nc_bad_path.exists() and _nc_null_path.exists():
        try:
            _evolve_nc = {"planted_bad": json.loads(_nc_bad_path.read_text()), "null": json.loads(_nc_null_path.read_text())}
        except (json.JSONDecodeError, OSError):
            _evolve_nc = None
    M["EVOLVE"] = _vl.evolve_mark(tape, live, "EVOLVE" in decl, float(a.hours), negative_control=_evolve_nc,
                                  every_h=(decl.get("EVOLVE") or {}).get("every_h"))   # §5/§6; READER-FIX-0923 (1): the void round printed apart
    if G["lag"].get("cut"):      # READER-LAG-0923: as QUESTION — the bar keeps --hours, the hours lived printed beside
        M["EVOLVE"]["hours_lived"] = round(G["hours_on_tape"], 3)
    # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:5x +0400 — ALPHA4-PREREG.md §5: WEB and STAGE (I) —
    # wired the SAME way every other builder's mark above is (a pure function in tools/verdict_life.py, called here
    # with `decl`/`tape`/`live`), so a run of THIS reader against an ALPHA4 life computes them, never leaves them
    # DECLARED-ONLY in the sense #180 exists to catch. Both read «not gradable» on every closed record this reader
    # has ever seen (none declares DOOR_WEB/STAGE_READY) — the control every OTHER mark above already gets for free.
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (8): the mind's `stage` event rows (gather's
    # `mind_events`, no `at`) ride beside the mind rows — `live` alone never carried them, so «≤ 1 stage-4 event» and WEB's stage-3 law read 0
    # events whatever the life did; STAGE prints the readiness series (the `sit` rows' readings, the tape's sit scores joined by seq).
    _stage_journal = list(live) + list(G.get("mind_events") or [])
    M["WEB"] = _vl.web_mark(tape, _stage_journal, "DOOR_WEB" in decl)
    M["STAGE"] = _vl.stage_mark(_stage_journal, "STAGE_READY" in decl, tape=tape)
    # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:00 +0400 — A4-LADDER-PREREG §3.4 L1-L9: `chat_read` (below main) gathers the
    # record and calls the pure marks; lifted out of main() so a test reads the LAST link (#180).
    M["CHAT"] = chat_read(root, tape, live, G["exams"], decl, twins_dir,
                          a.chat_pointing_ceiling if a.chat_pointing_ceiling is not None else _vl.CHAT_POINTING_CEILING_PRELIFE, G["t0"])
    # edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:59 +0400 — A4L-COST (A4-LADDER-PREREG §2.1 C1 (iii)): the reader's own unblinded replay IS a replay under
    # the life's code+genome when the commits agree (hash unmasked); the floor's replay (ii) is the tape twin's (§1.4 (c)), not this reader's.
    M["HASH"] = _vl.hash_law_mark(live, st, "HASH" in decl, replay_same=(u1 if not _ign else None))
    # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:30 +0400 — READER v3.5: the ladder-2 marks (A4-LADDER-2-PREREG §2 + ADDENDUM §7(2))
    M.update(ladder2_read(root, G, tape, live, st, decl, float(a.hours),
                          identity_root=(Path(a.identity_root).resolve() if a.identity_root else None), identity_hours=a.identity_hours,
                          control_root=(Path(a.control_root).resolve() if a.control_root else None), line_ceiling=a.line_ceiling,
                          twins_dir=twins_dir, genome_path=genome_path))
    print(f"[LADDER-2] " + " · ".join(f"{k} {gv_(M[k])}" for k in ("IDENTITY", "X1_LOCK", "X2_SUCCESS", "LINE", "NURSERY", "NURSERY_READ", "DROP_EQ", "A1_NULL", "A2_SEEN")), flush=True)
    M["PLANTS"]["predict_file_pair"] = {"sight_road_rows": live_pred["sight_road_rows"], "rule_rows_filed": live_pred["filed"], "rule_rows_scored": live_pred["scored"], "status_predictions_filed": st.get("predictions_filed")}
    M["PLANTS"]["park_unanswerable_want"] = {"sight_only_rows": len(sight_only), "first_seq": sight_only[0]["seq"] if sight_only else None, "parked_total": parked}
    M["PLANTS"]["belief_contradiction"] = {"clash_rows": kinds.get("clash", 0), "extension_rows": kinds.get("extension", 0)}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "reported: no-park twin parked %s vs live %d" % (TW.get("blind-park", {}).get("parked"), parked)}
    # BANDS (reported): the drawn bands from gate G-a's line in the genome; photographs from the recorded runs if present
    bands = {"drawn_gate_Ga_line": next((l for l in base_text.splitlines() if "gate G-a wrote" in l), None)}
    for name, pth in (("eye_photo_g1_gate", ROOT / "runs" / "eye-photo-g1" / "gate.json"),):
        bands[name] = json.loads(pth.read_text()) if pth.exists() else "not on disk"
    M["BANDS"] = bands
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): the verdict is STRUCTURAL — `failed` = every
    # GRADED mark whose pass is not True (a hand-kept list of names had left READ/WEB/STAGE out of it and put a «not gradable» MODULATION in
    # it); the not-gradable marks are their own list with their reasons; a mark missing `graded` is named, and judged by its pass.
    failed, not_gradable, missing = partition_marks(M, R["ALIVE"])
    R["marks"] = M; R["marks_failed"] = failed; R["marks_not_gradable"] = not_gradable; R["marks_missing_graded"] = missing
    R["verdict"] = "PASS" if not failed else "FAIL"
    R["seconds_total"] = round(time.perf_counter() - T0, 1)
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str))
    write_verdict(out, R)
    print(f"VERDICT {R['verdict']} — failed: {failed or 'none'} — not gradable: {[k for k, _r in not_gradable] or 'none'} — {out} ({R['seconds_total']} s)", flush=True)
    return 0



# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:00 +0400 — A4-LADDER-PREREG §3.4 L1-L9 (builder LANG's marks, pure, in
# tools/verdict_life.py): the chat/out answers joined with the seat's chat/truth, the tape, the live journal, the exams, the
# blind-chat twin's journal (`twins_dir/blind-chat/mind-journal.jsonl`, run only when CHAT is declared), the pre-life pointing
# ceiling; the chat pictures checked disjoint from the maker's canvases on the tape. «not gradable» on every record that did not
# declare CHAT. A summary `graded`/`pass` over L1-L7 for the verdict's failed-list.

# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:31 +0400 — A4L-LANG L1: the blind-chat twin's worker spec — every chat row and every
# kind-chat grade ignored (the Mind's own `chat` blind; creature/replay.py's tape filter is pinned equal to it by
# tests/creature/test_replay_blind_chat.py). Only a life that declares CHAT gets it: every other record reads exactly as before.
def chat_twin_specs(declared: dict, twins_dir: Path, tape_all: Path, genome_path: Path) -> List[dict]:
    if "CHAT" not in declared:
        return []
    return [{"label": "blind-chat", "root": str(Path(twins_dir) / "blind-chat"), "tape": str(tape_all), "genome": str(genome_path), "blind": ["chat"]}]

def chat_read(root: Path, tape: List[dict], live: List[dict], exams: List[dict], decl: dict, twins_dir: Path,
              pointing_ceiling: Optional[float], t0) -> Dict[str, object]:
    from tools import verdict_life as _vl
    from creature import replay as replay_mod
    try:
        cout = {p_.stem: json.loads(p_.read_text()) for p_ in sorted((root / "chat" / "out").glob("*.json"))} if (root / "chat" / "out").exists() else {}
        ctru = {p_.stem: json.loads(p_.read_text()) for p_ in sorted((root / "chat" / "truth").glob("*.json"))} if (root / "chat" / "truth").exists() else {}
        bj = Path(twins_dir) / "blind-chat" / "mind-journal.jsonl"
        blind = replay_mod.read_mind_journal(bj) if bj.exists() else None
        tape_cv, pics = None, None
        if "CHAT" in decl and cout:
            from PIL import Image as _CImg
            tape_cv = [np.asarray(_CImg.open(root / "tape" / r["payload"]).convert("RGB"), dtype=np.uint8)
                       for r in tape if r.get("sense") == "eye" and (r.get("meta") or {}).get("source") == "maker"]
            pics = {p_.stem: np.asarray(_CImg.open(p_).convert("RGB"), dtype=np.uint8) for p_ in sorted((root / "chat" / "pics").glob("*.png"))}
        C = _vl.chat_marks(cout, ctru, tape, live, exams, decl, blind_journal=blind, pointing_ceiling=pointing_ceiling,
                           born=(t0.isoformat() if hasattr(t0, "isoformat") else t0), tape_canvases=tape_cv, chat_pics=pics or None)
    except Exception as e:
        C = {"error": repr(e)}
    graded = [k for k in _vl.CHAT_MARKS if isinstance(C.get(k), dict) and C[k].get("graded")]
    C["graded"] = bool(graded) or ("error" in C and "CHAT" in decl)
    C["pass"] = bool(graded) and all(C[k].get("pass") for k in graded) and "error" not in C
    return C

# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:30 +0400 — READER v3.5 (A4-LADDER-2-PREREG §2 + ADDENDUM §7(2)): a SECOND closed root read
# read-only — the identity root (R0b's twin life) or the control root (R0, for R1–R3's one-difference readings). Nothing is replayed, copied or
# written: the tape, the journal's mind rows, STATUS, the sampler's series, HEARD.json, the exam files and the scorer's ledger, cut by the SAME
# rule gather uses (t0 = the journal's first start event; the time cut at t0 + hours; the mind's last consumed seq when the mind is behind).
# hours None = the whole record.
def gv_(m: dict) -> str:
    """A mark's verdict word (the renderer's own rule, module-level for the [LADDER-2] progress line)."""
    return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"


def side_record(root: Path, hours: Optional[float] = None) -> dict:
    root = Path(root)
    status = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
    try:
        ledger = json.loads((root / "state" / "ledger.json").read_text())
    except (OSError, json.JSONDecodeError):
        ledger = {}
    tape_rows: List[dict] = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        tape_rows += read_jsonl(f)
    tape_rows.sort(key=lambda r: r["seq"])
    journal: List[dict] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        journal += read_jsonl(f)
    events = [r for r in journal if "event" in r and r.get("at") is not None]
    starts = [e for e in events if e["event"] == "start"]
    t0 = _iso(starts[0]["at"]) if starts else (_iso(tape_rows[0]["at"]) if tape_rows else None)
    t_cut = (t0 + timedelta(hours=hours)) if (t0 is not None and hours is not None) else None
    tape_world = [r for r in tape_rows if t_cut is None or _iso(r["at"]) <= t_cut]
    time_cut_seq = tape_world[-1]["seq"] if tape_world else 0
    tape_last_seq = tape_rows[-1]["seq"] if tape_rows else 0
    closed = any(e.get("event") == "stop" for e in events)
    ml = mind_last_consumed(journal, status, ledger, tape_last_seq, closed)
    M_seq = ml["mind_last_seq"]
    lag_cut = 0 < M_seq < time_cut_seq
    last_seq = M_seq if lag_cut else time_cut_seq
    mind = [r for r in journal if "event" not in r and r.get("seq") is not None and int(r["seq"]) <= last_seq]
    series_p = root / "readings" / "status-series.jsonl"
    series: List[dict] = []
    if series_p.exists():
        for l in series_p.read_text().splitlines():
            try:
                series.append(json.loads(l))
            except json.JSONDecodeError:
                continue
    heard_p = root / "read" / "HEARD.json"
    try:
        heard = json.loads(heard_p.read_text()) if heard_p.exists() else None
    except (OSError, json.JSONDecodeError):
        heard = None
    exams: List[dict] = []
    for f in sorted(p for p in (root / "exam").glob("*.json") if p.name[:1].isdigit()):
        try:
            d = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if t_cut is None or _iso(d["at"]) <= t_cut:
            d["_file"] = f.name; exams.append(d)
    preds: List[dict] = []
    pp = root / "state" / "predictions.jsonl"
    if pp.exists():
        for l in pp.read_text().splitlines():
            try:
                preds.append(json.loads(l))
            except json.JSONDecodeError:
                continue
    tape_cut = [r for r in tape_world if r["seq"] <= last_seq]
    return {"root": str(root), "t0": t0, "t_cut": t_cut, "hours": hours, "tape": tape_cut, "mind": mind, "status": status, "series": series,
            "heard": heard, "exams": exams, "predictions": preds, "closed": closed, "last_seq": last_seq, "lag_cut": bool(lag_cut),
            "hours_on_tape": (round((_iso(tape_cut[-1]["at"]) - t0).total_seconds() / 3600, 3) if (tape_cut and t0 is not None) else 0.0)}


def _canvas_seqs(mind_rows: Sequence[dict]) -> List[int]:
    return [int(r["seq"]) for r in mind_rows if "moment" in r and r.get("glance") == 0 and r.get("source") is not None]


def _read_jsonl_tolerant(p: Path) -> List[dict]:
    out: List[dict] = []
    if p.exists():
        for l in p.read_text().splitlines():
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                continue
    return out


def ladder2_read(root: Path, G: dict, tape: List[dict], live: List[dict], st: dict, decl: dict, hours: float,
                 identity_root: Optional[Path] = None, identity_hours: Optional[float] = None, control_root: Optional[Path] = None,
                 line_ceiling: Optional[float] = None, twins_dir: Optional[Path] = None, genome_path: Optional[Path] = None) -> Dict[str, dict]:
    """edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:30 +0400 — the ladder-2 marks, gathered and graded in one place (a test reads
    the LAST link, #180): IDENTITY (R0b, --identity-root), X1_LOCK/X2_SUCCESS (R1, R5), LINE (R2), NURSERY/NURSERY_READ (R3, --control-root = R0),
    DROP_EQ/CHAT_COUNTERS (R5), A1_NULL/A2_SEEN (ladder 1's ANSWER marks, R5). Each reads «not gradable» where its line is undeclared."""
    from tools import verdict_life as _vl
    M: Dict[str, dict] = {}
    t0 = G.get("t0"); t_cut_a = (t0 + timedelta(hours=hours)) if t0 is not None else None
    series_a = _read_jsonl_tolerant(Path(root) / "readings" / "status-series.jsonl")
    # R0b IDENTITY
    if identity_root is not None:
        try:
            B = side_record(Path(identity_root), identity_hours)
            wa = _vl.wall_reading(series_a, st, _canvas_seqs(live), (t_cut_a.timestamp() if t_cut_a is not None else None))
            tb = (B["t0"] + timedelta(hours=(identity_hours if identity_hours is not None else hours))) if B["t0"] is not None else None
            wb = _vl.wall_reading(B["series"], B["status"], _canvas_seqs(B["mind"]), (tb.timestamp() if tb is not None else None))
            M["IDENTITY"] = _vl.identity_mark(tape, live, B["tape"], B["mind"], provided=True, wall=_vl.wall_band(wa, wb),
                                              label_a=Path(root).name, label_b=Path(identity_root).name)
            M["IDENTITY"]["identity_root"] = {"root": B["root"], "hours": B["hours"], "hours_on_tape": B["hours_on_tape"], "closed": B["closed"],
                                              "lag_cut": B["lag_cut"], "last_seq": B["last_seq"]}
        except Exception as e:
            M["IDENTITY"] = {"graded": True, "pass": False, "error": repr(e), "bar": "ADDENDUM §7(2)",
                             "reason": f"the identity read raised on a root that was GIVEN: {e!r} (a given root that cannot be read is a failure, never hidden)"}
    else:
        M["IDENTITY"] = _vl.identity_mark([], [], [], [], provided=False)
    # R1 / R5: X1 the lock absent, X2 success per episode (printed)
    value_on = "ACT_VALUE" in decl
    M["X1_LOCK"] = _vl.explore_lock_mark(tape, live, value_on)
    M["X1_LOCK"]["window"] = _vl.explore_lock_window(tape, live)
    M["X2_SUCCESS"] = _vl.explore_success_mark(tape, value_on)
    M["X2_SUCCESS"]["census"] = _vl.explore_x2_census(tape, live, st)
    # the control (R0) root, read once
    C = None
    if control_root is not None:
        try:
            C = side_record(Path(control_root), hours)
        except Exception as e:
            C = {"error": repr(e)}
    # R2 LINE
    preds = _read_jsonl_tolerant(Path(root) / "state" / "predictions.jsonl")
    ctl_line = None
    if C is not None and "error" not in C:
        _cl = _vl.line_mark(C["predictions"], C["status"], True)
        ctl_line = {"root": C["root"], "status": _cl["status"], "by_instant": _cl["by_instant"], "frame_rows_scored": _cl["frame_rows_scored"],
                    "note": "R0 (FLOOR) writes no instant stamp: its scored frames read «unstamped» (every source together) — printed beside, never graded"}
    elif C is not None:
        ctl_line = {"error": C["error"]}
    try:
        _tf = _vl.read_frames(tape)
    except Exception as e:
        _tf = {"error": repr(e)}
    M["LINE"] = _vl.line_mark(preds, st, bool((decl.get("SENTENCE") or {}).get("line")),
                              ceiling=(line_ceiling if line_ceiling is not None else _vl.LINE_CEILING), tape_frames=_tf, control=ctl_line)
    M["LINE"]["ledger_note"] = "state/predictions.jsonl read WHOLE (its rows carry no seq to cut by)"
    # R3 NURSERY
    body_only = bool((decl.get("SENSE_READ") or {}).get("gutenberg_body_only"))
    heard_p = Path(root) / "read" / "HEARD.json"
    try:
        heard = json.loads(heard_p.read_text()) if heard_p.exists() else []
    except (OSError, json.JSONDecodeError):
        heard = []
    shelf_words = [str((r.get("meta") or {}).get("word")) for r in tape if r.get("sense") == "ear" and (r.get("meta") or {}).get("source") == "shelf"
                   and (r.get("meta") or {}).get("word") is not None]
    ctl_heard = (C.get("heard") if (C is not None and "error" not in C) else None)
    M["NURSERY"] = _vl.nursery_mark(heard, ctl_heard, shelf_words, body_only)
    M["NURSERY_READ"] = _vl.nursery_read_mark(G.get("exams") or [], (C.get("exams") if (C is not None and "error" not in C) else None), body_only)
    if C is not None:
        M["NURSERY"]["control_root"] = C.get("root") or C.get("error")
    # R5: the live drop equality, the chat door's counters
    M["DROP_EQ"] = _vl.drop_equality_mark(st, (decl.get("SURPRISE") or {}).get("drop") == "confirmed")
    M["CHAT_COUNTERS"] = _vl.chat_counters_mark(st, "CHAT" in decl)
    # ladder 1's ANSWER marks (A4-LADDER-PREREG §2.2) — A2 from the exam files; A1's vex asked on the organism at the cut (the unblinded replay),
    # both laws, by tools/answer_readtwin.py's own road (the organism's hash asserted unmoved)
    majority = bool((decl.get("ANSWER") or {}).get("majority"))
    M["A2_SEEN"] = _vl.answer_seen_mark(G.get("exams") or [], majority)
    vex_new = vex_old = None; rt = None
    if majority and twins_dir is not None and genome_path is not None and (Path(twins_dir) / "unblinded-1" / "state" / "organism.npz").exists():
        try:
            from tools import answer_readtwin as _art
            rt = _art.read_both_laws(Path(twins_dir) / "unblinded-1", Path(genome_path))
            if rt.get("organism_unchanged"):
                vex_new, vex_old = rt["new_law"]["vex"], rt["old_law"]["vex"]
        except Exception as e:
            rt = {"error": repr(e)}
    M["A1_NULL"] = _vl.answer_null_mark(G.get("exams") or [], vex_new, vex_old, majority)
    if rt is not None:
        M["A1_NULL"]["readtwin"] = {k: rt.get(k) for k in ("snapshot", "cells", "moments", "organism_unchanged", "error") if k in rt}
        if "new_law" in rt:
            M["A1_NULL"]["readtwin"]["zog_A3"] = {"new": rt["new_law"]["zog"], "old": rt["old_law"]["zog"],
                                                  "note": "A3 is read on alpha4-1's CLOSED record (the plant is never shown in an 8 h life: PLANT_AFTER 15000) — printed"}
    return M


# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:31 +0400 — READER v3.5: the ladder-2 marks' VERDICT.md rows (one renderer, testable; every
# row prints the mark's denominator and reach beside its verdict — #234).
def ladder2_rows(M: Dict[str, dict], gv=None) -> List[str]:
    gv = gv or gv_
    L: List[str] = []
    def _j(x, n=500):
        return json.dumps(x, default=str)[:n]
    m = M.get("IDENTITY")
    if isinstance(m, dict) and "streams" not in m:      # not given / raised: the reason alone
        L.append(f"| IDENTITY (R0b) | {m.get('bar')} | {m.get('reason')} | {gv(m)} |")
    elif isinstance(m, dict):
        st = m.get("streams") or {}
        def _fd(v):
            f = v.get("first_divergence")
            if not f:
                return ""
            ra_ = f.get("realigned") or {}
            return (f"; first divergence at {f['index']} seq {f['seq_a']}/{f['seq_b']}"
                    + (f" (a {f.get('tags_a')} / b {f.get('tags_b')})" if (f.get('tags_a') or f.get('tags_b')) else "")
                    + (f", the rest identical at offset {ra_['offset']:+d} for {ra_['matched']} of {ra_['of']}" if ra_.get('offset') is not None else ""))
        streams = " · ".join(f"{s} {v['identical']}/{v['compared']} (a {v['a']}, b {v['b']}{_fd(v)}){'' if v.get('graded') else ' [printed]'}"
                             for s, v in st.items())
        lm = m.get("last_meeting_point") or {}
        w = (m.get("wall") or {})
        wall = ""
        if w:
            pc = w.get("per_counter") or {}
            wall = (f" · WALL-CLOCK (printed, not graded): {m.get('label_a')} at {(w.get('a') or {}).get('at')} vs {m.get('label_b')} at {(w.get('b') or {}).get('at')}, "
                    f"Δcanvases {w.get('delta_canvases')}: " + "; ".join(f"{k} {v.get('a')} vs {v.get('b')} (Δ {v.get('delta')}, band ±{v.get('band')}, inside {v.get('inside')})" for k, v in pc.items()))
        body = (f"streams: {streams or 'none'} · meeting points {m.get('meeting_points')} (agree {m.get('meeting_points_agree')}, disagree {m.get('meeting_points_disagree')}; "
                f"max |Δ| {_j(m.get('disagreement_max_abs'), 120)}; last agreeing at canvas {m.get('last_agreeing_meeting_point_canvas')}) · "
                f"canvases {m.get('canvases_a')} / {m.get('canvases_b')} · reach {_j(m.get('reach'), 160)} · last meeting point canvas {lm.get('canvas')}: "
                f"{_j(lm.get('a'), 220)} vs {_j(lm.get('b'), 220)}{(' · ' + m['id_order_note']) if m.get('id_order_note') else ''}{wall} — {m.get('reason')}")
        L.append(f"| IDENTITY (R0b) | {m.get('bar')} | {body} | {gv(m)} |")
    m = M.get("X1_LOCK")
    if isinstance(m, dict):
        w = (m.get("window") or {}).get("window") or {}
        L.append(f"| X1_LOCK (R1) | {m.get('bar')} | max share {m.get('max_share')} ({m.get('max_act')}) in choices {w.get('first_choice')}–{w.get('last_choice')} "
                 f"(seq {w.get('first_seq')}–{w.get('last_seq')}, hour {w.get('first_hour')}–{w.get('last_hour')}; census {_j(w.get('census'), 160)}) · "
                 f"choices {m.get('choices')} (after hour 1: {m.get('choices_after')}) · policies {_j(m.get('policies'), 120)} — {m.get('reason')} | {gv(m)} |")
    m = M.get("X2_SUCCESS")
    if isinstance(m, dict):
        c = m.get("census") or {}
        L.append(f"| X2_SUCCESS (R1) | {m.get('bar')} | hours 2–8: {m.get('successes')} of {m.get('episodes')} episodes (null bound {m.get('bound_k')}; ceiling {m.get('ceiling')}) · "
                 f"whole cut: journal game outcome rows {c.get('journal_game_outcome_rows')} (carrying got {c.get('rows_carrying_got')}; paid {c.get('rewarded_rows')} {c.get('rewards')}) · "
                 f"tape game outcome rows {c.get('tape_game_outcome_rows')} (with flags {c.get('rows_carrying_flags')}): episodes {c.get('episodes_terminal_rows')} "
                 f"(terminated {c.get('terminated')}, truncated {c.get('truncated')}), successes {c.get('successes')} = {c.get('success_per_episode')} per episode · "
                 f"STATUS act_policy {c.get('act_policy')} act_weights {c.get('act_weights')} act_explored {c.get('act_explored')} — {m.get('reason')} | {gv(m)} |")
    m = M.get("LINE")
    if isinstance(m, dict):
        tf = m.get("tape_frames_read") or {}
        L.append(f"| LINE (R2) | {m.get('bar')} | shelf-line frames {m.get('shelf_line_true')} true of {m.get('shelf_line_scored')} scored (rate {m.get('shelf_true_rate')}; "
                 f"{m.get('ratio_to_ceiling')}× the ceiling {m.get('ceiling')}) · by instant {_j(m.get('by_instant'), 240)} · frame rows {m.get('frame_rows')} "
                 f"(filed {m.get('frame_rows_filed')}, scored {m.get('frame_rows_scored')}; reconciles with STATUS {m.get('scored_reconciles_with_status')}) · STATUS {_j(m.get('status'), 120)} · "
                 f"READ's tape frames (not the scorer): precision {tf.get('precision')} = {tf.get('true_vs_shuffled')} of {tf.get('filed')} filed pairs not also filed by the shuffled twin ({tf.get('shuffled_filed')} filed there) · "
                 f"R0 beside: {_j(m.get('control'), 240)} — {m.get('reason')} | {gv(m)} |")
    m = M.get("NURSERY")
    if isinstance(m, dict):
        L.append(f"| NURSERY (R3) | {m.get('bar')} | heard {m.get('heard')} words (R0 {m.get('control_heard')}) · header tokens {m.get('header_tokens_n')} {m.get('header_tokens_in_heard')} · "
                 f"«project gutenb…» bigrams {m.get('project_gutenberg_bigrams_heard')} · first word {m.get('first_word')!r} at R0 index {m.get('shift_measured')} (PREREG guessed {m.get('prereg_shift_guess')}) · "
                 f"ordered subsequence {m.get('ordered_subsequence')} over {m.get('body_words_matched')} body words (breaks {m.get('order_breaks_n')}) · re-heard header words {m.get('header_shared_reheard')} · "
                 f"beyond R0 {m.get('beyond_control')} · prefix-equal (stronger) {_j(m.get('stronger_prefix_equal'), 160)} — {m.get('reason')} | {gv(m)} |")
    m = M.get("NURSERY_READ")
    if isinstance(m, dict):
        L.append(f"| NURSERY_READ (R3) | {m.get('bar')} | this {_j(m.get('this'), 160)} vs R0 {_j(m.get('control'), 160)} · Δ {m.get('delta')} band ±{m.get('band')} — {m.get('reason')} | {gv(m)} |")
    m = M.get("DROP_EQ")
    if isinstance(m, dict):
        L.append(f"| DROP_EQ (R5) | {m.get('bar')} | dropped {m.get('glances_dropped')} · confirmed {m.get('glances_confirmed')} · surprised {m.get('glances_surprised')} — {m.get('reason')} | {gv(m)} |")
    m = M.get("CHAT_COUNTERS")
    if isinstance(m, dict):
        from tools.verdict_life import CHAT_COUNTER_KEYS as _CK
        L.append(f"| CHAT_COUNTERS (R5) | {m.get('bar')} | " + " · ".join(f"{k} {m.get(k)}" for k in _CK) + f" — {m.get('reason')} | {gv(m)} |")
    for k, name in (("A1_NULL", "A1 NULL (ANSWER)"), ("A2_SEEN", "A2 SEEN (ANSWER)")):
        m = M.get(k)
        if isinstance(m, dict):
            per = m.get("spiral_per_exam") or m.get("per_exam") or []
            extra = (f" · vex new {_j(m.get('vex_graded'), 120)} old {_j(m.get('vex_old_law_graded'), 120)} · readtwin {_j(m.get('readtwin'), 300)}" if k == "A1_NULL" else "")
            L.append(f"| {name} | {m.get('bar')} | exams {len(per)}: {_j(per[-3:], 400)}{extra} — {m.get('reason')} | {gv(m)} |")
    return L


def w3_1_beliefs(bel_rows: List[dict], decl: dict, heard: Sequence[str]) -> dict:
    """W3-1 (PREREG §18) as amended 2026-09-22: a word carries ONE raw `belief` row, plus one more for every clash — genome/think.py's
    clash law (decision 5) FIRST writes the new observation as its own fresh `belief` row and then a `clash` row naming
    [standing_line, new_line], so the extra row is the clash's second side by design. Every belief row beyond a word's first must
    be NAMED as `clashes[1]` of a clash row of that word; an unnamed extra row is life 2's dedupe defect (1,473 rows, all kind
    belief, no clash) and still fails. Revisits > 0 as before. Found on the 2 h smokes of the six 8 h lives (L4 max 2, L5/seam-1
    max 4 — all 24 extra rows named by a clash, measured on the live files 2026-09-22 10:1x +04)."""
    kinds: Dict[str, int] = {}
    per_word_beliefs: Dict[str, List[int]] = {}
    named: Dict[str, set] = {}
    for r in bel_rows:
        k = str(r.get("kind", "belief")); kinds[k] = kinds.get(k, 0) + 1
        w = str(r.get("word"))
        if k == "belief":
            per_word_beliefs.setdefault(w, []).append(int(r.get("line", -1)))
        elif k == "clash":
            c = r.get("clashes")
            if isinstance(c, list) and len(c) == 2:
                named.setdefault(w, set()).add(int(c[1]))
    unaccounted = [[w, ln] for w, lines in per_word_beliefs.items() for ln in lines[1:] if ln not in named.get(w, set())]
    max_per_word = max((len(v) for v in per_word_beliefs.values()), default=0)
    extra = sum(len(v) - 1 for v in per_word_beliefs.values())
    graded = "BELIEF" in decl
    return {"graded": graded, "pass": graded and bool(bel_rows) and not unaccounted and kinds.get("revisit", 0) > 0,
            "rows": len(bel_rows), "kinds": kinds, "standing_words": len(per_word_beliefs), "words_heard": len(heard),
            "max_belief_rows_per_word": max_per_word, "extra_belief_rows": extra, "clash_rows": kinds.get("clash", 0), "unaccounted": unaccounted,
            "bar": "every raw `belief` row beyond a word's first is the named second side of a `clash` row of that word (the clash law writes it; "
                   "life 2's 1,473 unnamed rows fail) · revisits > 0 · clashes reported"}


def grade_modulation_windows(windows: dict, min_showings: int = 10):
    """PREREG §18 addendum 4 (2026-09-22): a window is graded over the NEW things that reached `min_showings` showings — «settled by
    the 10th showing» cannot be read on a thing shown fewer times (the PLANT is shown 5 times by design; on every rung of the ladder
    window 3's only new thing was the plant and the mark read FAIL on a bar above its ceiling, #228 (b)). A window whose new things
    ALL fall under the floor is reported NOT GRADABLE (skipped), never FAIL. Returns (graded_fixed, graded_regime, skipped)."""
    graded, graded_regime, skipped = [], [], []
    for w, rec in windows.items():
        news_all = {t: v for t, v in rec["per_thing"].items() if v["kind"] == "new"}
        if not news_all:
            continue
        news = [v for v in news_all.values() if v.get("n_showings", 0) >= min_showings]
        if not news:
            skipped.append({"window": w, "new": len(news_all), "new_under_min": sorted(news_all), "gradable": False,
                            "reason": f"no new thing reached {min_showings} showings (the plant is shown 5 times by design) — settle cannot be read; not gradable"})
            continue
        sp = sum(v["spike"] for v in news); st = sum(v["settled"] for v in news)
        graded.append({"window": w, "new": len(news), "spike": sp, "settled": st, "pass": sp * 2 > len(news) and st * 2 > len(news)})
        spr = sum(v["spike_regime"] for v in news); str_ = sum(v["settled_regime"] for v in news)
        graded_regime.append({"window": w, "new": len(news), "spike": spr, "settled": str_, "pass": spr * 2 > len(news) and str_ * 2 > len(news)})
    return graded, graded_regime, skipped


def null_clears(per: dict, band):
    """§18 addendum 4 (b2): the fake-boundary NULL clears when the MAJORITY of continuing things' spike ratios sit under the regime band
    (the spike rule's own majority). The band is the 95th percentile of exactly these ratios, so `all()` over eleven things failed by
    construction ~43 % of the time (L1: ten of eleven under 2.27, «wave» 3.73). Returns (pass, share_under_band); (None, None) when
    there is no band or nothing to read."""
    vals = [v for v in per.values() if v is not None] if per else []
    if band is None or not vals:
        return None, None
    share = sum(1 for v in vals if v < band) / len(vals)
    return share > 0.5, share


def iv_refusals(c: dict) -> dict:
    """(iv)'s refusals, §18 addendum 4: every CAP refusal counts (budget · nmax · frozen); `redundant` is the ordinary no-birth path and is
    printed only. g5-seam-1 refused 1,988 births at NMAX (its 2,000 sight ids spent by hour ~6) while the old bar read `births_refused_budget`
    alone and PASSED — the plant could not be learned and no surface said so."""
    b = int(c.get("births_refused_budget", 0)); n = int(c.get("births_refused_nmax", 0)); f = int(c.get("births_refused_frozen", 0))
    return {"budget": b, "nmax": n, "frozen": f, "redundant": int(c.get("births_refused_redundant", 0)), "caps_total": b + n + f}


def w3_2_reason(eligible_n: int, reached_n: int, wrong: list) -> str:
    """The W3-2 cluster control's reason names the clause that failed (§18 addendum 4): «VOID by the wiring» is the REACH floor only
    (life 3a's shape — one word of 21 by a coincidence of ids); a cluster under .5 own share is a real reading of the rules."""
    fails = []
    if eligible_n < 5:
        fails.append(f"fewer than 5 eligible words ({eligible_n})")
    if reached_n < 5:
        return f" VOID by the wiring: rules reached {reached_n} of {eligible_n} eligible words (floor 5)" + (f"; {len(wrong)} rule(s) under .5 own share" if wrong else "")
    if wrong:
        fails.append("own-cells clause: " + ", ".join(f"{x['word']} {x['own_share']:.3f}" for x in wrong) + " (bar .5 of the word's own cells)")
    return (" FAIL on the " + "; ".join(fails)) if fails else ""


def _viii_g4_7(status: dict, solo_ms: float, unblinded_ms: float, cpu_ns) -> dict:
    """(viii) COST, G4-7, in ONE unit (#162 — found 2026-09-22 on the six 2 h smokes: STATUS.mind_ms_median_1min is the median of
    `mind.consume(row)` over EVERY tape row — ear, outcome, body rows included — while the probe is all rows' time ÷ CANVASES; 0.168 ms
    «vs» 13 ms passed in every life to date). The live number is STATUS.mind_ms_per_canvas_1min (creature/body.py writes it from
    2026-09-22); a status that carries only the per-row median is NOT GRADED — never PASS."""
    rss = status.get("rss_mb"); per_canvas = status.get("mind_ms_per_canvas_1min"); per_row = status.get("mind_ms_median_1min")
    graded = per_canvas is not None
    m = {"graded": graded, "pass": None, "rss_mb_last_status": rss, "live_ms_per_canvas": per_canvas, "live_mind_ms_median_per_row": per_row,
         "solo_ms_per_canvas_replay": solo_ms, "unblinded_replay_ms_under_workers": unblinded_ms,
         "cpu_hours": round(cpu_ns / 3.6e12, 3) if cpu_ns else None,
         "bar": "G4-7: live ms per CANVAS (STATUS.mind_ms_per_canvas_1min) ≤ 2× the solo probe's · RSS < 2 GB (the 24 h CPU bill printed)",
         "reason": "",
         # edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:59 +0400 — A4L-COST task 5: the per-row witness's form and its own ms (STATUS, #164)
         "hash_form": status.get("hash_form", "not recorded"), "hash_ms_last": status.get("hash_ms_last", "not recorded")}
    if not graded:
        m["reason"] = ("STATUS carries only the per-row median (mind_ms_median_1min), which is not the probe's unit (ms per canvas, #162): "
                       "not graded — every (viii) PASS before 2026-09-22 was a reading of this instrument")
        return m
    m["pass"] = (rss is not None and rss < 2048) and (solo_ms is None or solo_ms <= 0 or per_canvas <= 2 * solo_ms)
    return m


# edit: Claude (Fable 5.1), 2026-09-23 12:49 +0400 — the merge of A4L-COST task 5 (one renderer for the (viii) row, the witness's form and ms beside the
# cost) with READER-FIX-0923 (2) (the §8b function-of-cells form): ONE `cost_line` for BOTH forms; `gv` is the renderer's own when given.
def cost_line(m: dict, gv=None, ls: Optional[dict] = None) -> str:
    # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:08 +0400 — the v3.5 merge: master's READER-LAG-0923 row clauses (the sleeps window's end;
    # `lag_text(m['lag'] or ls)` after the reason, on BOTH forms) folded into this one renderer; `ls` = write_verdict's lag summary.
    def _gv(x): return (("PASS" if x.get("pass") else "FAIL") if x.get("graded") else "not graded")
    gv = gv or _gv
    form = m.get("hash_form", "not recorded")
    hash_part = " · hash not recorded" if form == "not recorded" else f" · hash {form} {m.get('hash_ms_last')} ms a row"
    tail = f"{hash_part}{(' · ' + m['reason']) if m.get('reason') else ''} · {lag_text(m.get('lag') or ls or {})} | {gv(m)} |"
    if m.get("form") == "§8b":
        _pts = " · ".join(f"{p['ms_per_cell']} at {p['cells']:,}" for p in m.get("review_points") or [])
        _g = m.get("g4_7") or {}
        return (f"| (viii) COST | {m['bar']} | live {m['live_ms_per_canvas']} ms a canvas at {m['cells_alive']} alive cells = {m['per_cell_ms']} ms/cell vs the bar {m['bar_per_cell_ms']} ms/cell ({m['bar_ms']} ms) · the review's points (ms/cell at cells): {_pts} · {m['reading_window']}; sleeps in its last 3 min {m.get('sleeps_in_window')} (window end: {(m.get('lag') or {}).get('sleeps_window_end_is', 'STATUS heartbeat_at')}) · RSS {m['rss_mb_last_status']} MB (a peak) · CPU {m['cpu_hours']} h · G4-7 beside (not graded): {gv(_g)} vs solo {_g.get('solo_ms_per_canvas_replay')} ms" + tail)
    return (f"| (viii) COST | {m['bar']} | live {m['live_ms_per_canvas']} ms a canvas (per-row median {m['live_mind_ms_median_per_row']} ms) vs solo {m.get('solo_ms_per_canvas_replay')} ms a canvas · RSS {m['rss_mb_last_status']} MB · CPU {m['cpu_hours']} h" + tail)


# edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (2): ALPHA4-PREREG §8b's COST bar, «stated as a FUNCTION,
# not a number: 0.09 ms × cells per canvas; the mark reads the 24 h figure against 1.5× that function at the life's own final cell count
# (the reader prints both). A fixed number would fail by construction on a growing mind.» The pre-flight's figure and the third hand's
# four points (docs: the review §2 — the ms/cell BENDS: exponents 1.9 and 1.2 between points; the §8b addendum names the cause, the
# quadratic state hash run twice a canvas), printed beside, never graded.
PREFLIGHT_MS_PER_CELL = 0.09          # ALPHA4-PREREG §8b (pre-3/pre-4 at 1,579–2,058 cells)
COST_FACTOR = 1.5                     # ALPHA4-PREREG §5 COST / §8b
REVIEW_COST_POINTS = [                # ALPHA4-1-FIRST-HOURS-REVIEW §2, «It is not linear.» (ms per cell per canvas)
    {"ms_per_cell": 0.075, "cells": 1579, "source": "alpha4-pre-4, 118 ms/canvas"},
    {"ms_per_cell": 0.092, "cells": 2058, "source": "alpha4-pre-3 at 22 min, 190 ms/canvas"},
    {"ms_per_cell": 0.143, "cells": 3334, "source": "alpha4-pre-3 at 39 min, 476 ms/canvas (a faster reader)"},
    {"ms_per_cell": 0.155, "cells": 4900, "source": "alpha4-1 live, median of 55 STATUS samples 09:55–10:15 +04 (756 ms/canvas)"},
]


def viii_cost(status: dict, solo_ms: float, unblinded_ms: float, cpu_ns, grow: bool = False,
              per_cell_ms: float = PREFLIGHT_MS_PER_CELL, factor: float = COST_FACTOR, sleeps_in_window: Optional[int] = None,
              lag: Optional[dict] = None) -> dict:
    """(viii) COST. A life that declares GROW (ALPHA4: no cap, «the world decides the cell count») is graded against §8b's FUNCTION of its
    own final cell count — STATUS `mind_ms_per_canvas_1min` ≤ factor × per_cell_ms × STATUS `cells` (alive sight + words,
    Organism.total_cells) — with the per-cell figure, the cell count, the bar and the review's four points printed; the G4-7 reading is
    printed beside as `g4_7`. Every other record reads G4-7 exactly as before (its `graded`/`pass` ARE g4_7's — the seven closed records'
    control). Two honesty prints, never gates: the figure is ONE 1-min window (STATUS's last write — no per-canvas series exists on any
    record), and `sleeps_in_window` counts the sleep rows whose triggering canvas fell in the 3 min before that write (a sleep minute
    reads ≈ 2.2×, the review §2)."""
    # edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: `lag` (gather's lag_summary) is printed on the mark in
    # both forms — the unconsumed tail is COST's finding (a mind behind its world), never a gate here and never hidden in a pass.
    g47 = _viii_g4_7(status, solo_ms, unblinded_ms, cpu_ns)
    if not grow:
        return {**g47, "form": "G4-7", "g4_7": dict(g47), **({"lag": lag} if lag is not None else {})}
    per_canvas = status.get("mind_ms_per_canvas_1min"); cells = status.get("cells")
    m = {"form": "§8b", "graded": False, "pass": None, "live_ms_per_canvas": per_canvas, "cells_alive": cells,
         "per_cell_ms": (round(per_canvas / cells, 4) if (per_canvas is not None and cells) else None),
         "preflight_ms_per_cell": per_cell_ms, "factor": factor, "bar_per_cell_ms": round(factor * per_cell_ms, 4),
         "bar_ms": (round(factor * per_cell_ms * cells, 3) if cells else None),
         "review_points": REVIEW_COST_POINTS, "rss_mb_last_status": status.get("rss_mb"),
         "rss_note": "STATUS rss_mb is ru_maxrss — the process's PEAK, not its current size",
         "live_mind_ms_median_per_row": status.get("mind_ms_median_1min"), "cpu_hours": g47.get("cpu_hours"),
         "reading_window": "ONE 1-min window: STATUS's last write (heartbeat %s) — no per-canvas series exists on any record" % status.get("heartbeat_at"),
         "sleeps_in_window": sleeps_in_window, "g4_7": g47, **({"lag": lag} if lag is not None else {}),   # READER-LAG-0923 (master)
         "hash_form": g47.get("hash_form", "not recorded"), "hash_ms_last": g47.get("hash_ms_last", "not recorded"),   # A4L-COST task 5, carried onto the §8b form at the merge
         "bar": f"ALPHA4-PREREG §8b: live ms per CANVAS (STATUS.mind_ms_per_canvas_1min) ≤ {factor} × {per_cell_ms} ms × the life's own final alive cells (STATUS cells); G4-7 printed beside, not graded",
         "reason": ""}
    if per_canvas is None:
        m["reason"] = "not graded: STATUS carries no mind_ms_per_canvas_1min (the per-canvas unit, #162)"
        return m
    if not cells:
        m["reason"] = "not graded: STATUS carries no alive cell count (`cells`) — the §8b bar is a function of it"
        return m
    m["graded"] = True
    m["pass"] = bool(per_canvas <= factor * per_cell_ms * cells)
    return m


def retention_mark(pairs: List[dict]) -> dict:
    """(v) §15's pair: the last exam of each odd window vs the last of the even window before it, ≤ 5 pp. edit: Claude (Opus 5.5,
    reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): with no such pair on the record the mark is NOT GRADABLE (it said
    «not readable» and was counted FAILED)."""
    out = {"graded": bool(pairs), "pass": (all(p["drop_pp"] <= 5.0 for p in pairs) if pairs else None), "pairs": pairs,
           "bar": "≤ 5 pp on the last-of-window pair (§15)", "note": "no odd window with exams on both sides → not readable" if not pairs else ""}
    if not pairs:
        out["reason"] = "not gradable: no odd window with exams on both sides (the maker's second window has not closed on this record)"
    return out


def vi_mark(plant: dict, null: dict, q5_abstain: float, false_abstention: float, plant_shown: Optional[int] = None) -> dict:
    """(vi) knows the unknown: plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20. edit: Claude (Opus 5.5,
    reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (10), the same fact as GRADE's and SIZING's plant clauses: «plant
    majority answered» is NOT GRADABLE while the plant was never shown (printed); the other three clauses carry the mark."""
    from tools.verdict_life import plant_clause
    pc = plant_clause(plant["answered_rate"] > .5, plant_shown, "plant majority answered")
    ok_rest = null["abstain_rate"] > .5 and q5_abstain >= .80 and false_abstention <= .20
    return {"graded": True, "pass": bool(ok_rest and (pc["pass"] if pc["graded"] else True)), "plant_clause": pc, "plant_shown": plant_shown,
            "plant_zog": plant, "null_vex": null, "Q5_spiral_abstain": q5_abstain, "false_abstention": false_abstention,
            "bar": "plant majority answered (not gradable while the plant was never shown) · null majority abstains · Q5 ≥ .80 · false ≤ .20"}


# READER-FIX-0923 (9): the order the failed list was always printed in (the old hand-kept `graded` list), then every other mark in M's own order.
_LEGACY_MARK_ORDER = ["i_knows", "ii_meeting_real", "iii_growth_matters", "iv_grows_alone", "v_retention", "vi_knows_unknown", "vii_replay",
                      "x_gaze_finds_thing", "xi_gaze_earns_place", "MODULATION", "ix_not_luck", "viii_cost", "W3_2_rules", "W3_1_beliefs",
                      "DOOR", "PARK", "ACT", "SOUND", "SIZING", "GRADE", "SELF", "SURPRISE", "COARSE", "QUESTION", "SENTENCE", "HANDS",
                      "THREAD", "EVOLVE"]
_MARK_CONTAINERS = ("PLANTS", "TWINS", "BANDS")
_TWIN_MARK_ALIAS = {"random_gaze_loses_xi": "TWINS.random_gaze"}     # the name the failed list has always used


def partition_marks(M: Dict[str, dict], alive: dict) -> Tuple[List[str], List[List[str]], List[str]]:
    """edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): PURE. Returns (failed, not_gradable,
    missing_graded). Every dict in M except the containers (PLANTS/TWINS/BANDS) is a mark, and so is every TWINS entry carrying `pass` or
    `graded`; ALIVE is always graded. failed = graded marks whose pass is not True; not_gradable = [name, reason] of marks with graded
    False — never in failed; a mark without `graded` is named in missing_graded and judged by its pass (a failure is never hidden)."""
    names = [k for k in _LEGACY_MARK_ORDER if k in M] + [k for k in M if k not in _LEGACY_MARK_ORDER]
    failed: List[str] = []; not_gradable: List[List[str]] = []; missing: List[str] = []
    def _one(name: str, m: dict) -> None:
        if "graded" not in m:
            missing.append(name)
            if not m.get("pass"):
                failed.append(name)
        elif m["graded"]:
            if not m.get("pass"):                     # truthiness, as the old list read it (a numpy bool is a pass too)
                failed.append(name)
        else:
            not_gradable.append([name, str(m.get("reason") or "")])
    for k in names:
        if k in _MARK_CONTAINERS or not isinstance(M[k], dict):
            continue
        _one(k, M[k])
    if not (alive or {}).get("pass"):
        failed.append("ALIVE")
    tw = M.get("TWINS") or {}
    for k in sorted(tw, key=lambda x: (x not in _TWIN_MARK_ALIAS, x)):
        m = tw[k]
        if isinstance(m, dict) and ("pass" in m or "graded" in m):
            _one(_TWIN_MARK_ALIAS.get(k, f"TWINS.{k}"), m)
    return failed, not_gradable, missing


def write_verdict(out: Path, R: dict) -> None:
    M = R["marks"]; A = R["ALIVE"]
    def pf(x): return "PASS" if x else "FAIL"
    def gv(m): return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"   # hoisted 2026-09-22: (viii) renders through it before its old definition below
    # edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:26 +0400 — READER-LAG-0923: the lag in the header (when the read is cut) and on the
    # ALIVE, REPLAY and COST rows (always) — never hidden in a pass.
    _LS = lag_summary(R.get("LAG")); _cut = bool(_LS.get("cut_at_mind_last_seq"))
    _alive_reach = (f" · the mind's counters graded over the {A.get('mind_reach_full_hours')} world h it fully lived; beyond its reach (hours {A.get('hours_beyond_the_minds_reach')}) the wall-clock snapshots only"
                    if A.get("mind_reach_full_hours") is not None else "")
    L = [f"# G4 VERDICT — {R['verdict']}", "", f"root `{R['root']}` · genome `{R['genome']}` (sha {R['genome_sha']}) · read {R['at']} by `{R['reader']}` (PREREG §5 as amended; the reader's rules §16) · {R['hours']} h",
         *(["", f"**The read is CUT at the mind's last consumed seq {_LS.get('mind_last_seq')}** — it lived {_LS.get('hours_lived')} of the window's world hours; {lag_text(_LS)}"] if _cut else []),
         "", "| mark | bar | reading | verdict |", "|---|---|---|---|",
         f"| ALIVE | {A['bar_hours']} h under the unit, NRestarts 0, every counter moved every hour, no sense dead > 60 s | {A['hours_on_tape']} h on tape · moved every hour {A['every_counter_moved_every_hour']}{_alive_reach} · max gap eye/ear {A['max_gap_s_eye_ear']} s · sense restarts {A['sense_restarts']} · crashes {A['crashes']} · NRestarts {A['nrestarts']} · {lag_text(A.get('lag') or _LS)} | {pf(A['pass'])} |",
         # edit: Claude (Fable 5.1), 2026-09-22 11:0x +0400 — compare() returns None when EVERY row matches; the old rendering printed "vs live None", which reads as unmeasured (the advisor's read, 2026-09-22 10:5x)
         f"| REPLAY / (vii) | byte-identical mind rows; the plant caught | vs live {'identical' if M['vii_replay']['vs_live'] is None else 'DIVERGED at ' + str(M['vii_replay']['vs_live'])} · two replays {'identical' if M['vii_replay']['two_replays'] is None else 'DIVERGED at ' + str(M['vii_replay']['two_replays'])} · {M['vii_replay']['mind_rows']} rows · plant at seq {M['vii_replay']['plant_seq']} caught {M['vii_replay']['plant_caught']}{(' · masked ' + ','.join(M['vii_replay']['hash_masked']) + ' (reader ' + str(R.get('reader_commit'))[:7] + ' ≠ life ' + str(R.get('life_commit'))[:7] + ')') if M['vii_replay'].get('hash_masked') else ''}{(' · readiness masked across M1 (judge-units ' + str(M['vii_replay']['readiness_mask']['m1_commit']) + ': the reader carries it ' + str(M['vii_replay']['readiness_mask']['reader_has_m1']) + ', the life ' + str(M['vii_replay']['readiness_mask']['life_has_m1']) + '; ' + str(M['vii_replay']['readiness_mask']['differing']) + ' of ' + str(M['vii_replay']['readiness_mask']['rows_with_readiness']) + ' readiness rows differ — A4-LADDER-2-PREREG §3)') if M['vii_replay'].get('readiness_mask') else ''} · closed whole {M['vii_replay'].get('closed_whole')} at the cut seq {M['vii_replay'].get('cut_seq')}{(' (the mind' + chr(39) + 's last consumed seq)') if _cut else ''} · {lag_text(M['vii_replay'].get('lag') or _LS)} | {pf(M['vii_replay']['pass'])} |"]
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (9): every mark row renders through gv() — a not-gradable
    # mark reads «not graded» with its reason, never FAIL; (2)/(3)/(4)/(5)/(7)/(10)/(11) print their new readings; READ, EVOLVE, WEB, STAGE get rows.
    def _why(m): return (" — " + str(m.get("reason"))) if (not m.get("graded") and m.get("reason")) else ""
    i = M["i_knows"]; L.append(f"| (i) | {i['bar']} | Q1 {i['Q1']:.3f} Q2 {i['Q2']:.3f} Q3 {i['Q3']:.3f} Q4 {i['Q4']:.3f} (chance {i['chance_Q1']}; all words Q1 {i['all_words']['Q1']:.3f}) | {gv(i)} |")
    m = M["ii_meeting_real"]; L.append(f"| (ii) | {m['bar']} (all 16 words) | T-shuffle Q1 {m['T_shuffle_Q1']} · T-nowire Q1 {m['T_nowire_Q1']}{_why(m)} | {gv(m)} |")
    m = M["iii_growth_matters"]; L.append(f"| (iii) | {m['bar']} | T-frozen-10 Q1 {m['T_frozen_10_Q1']} (cells {m['T_frozen_10_cells']}) vs Q1 {m['Q1']:.3f}; the 50-cell twin {m['T_frozen_50_Q1']}{_why(m)} | {gv(m)} |")
    m = M["iv_grows_alone"]; L.append(f"| (iv) | {m['bar']} | born {m['cells_born']} · refused at caps {m['refused']['caps_total']} (budget {m['refused']['budget']} · nmax {m['refused']['nmax']} · frozen {m['refused']['frozen']}; redundant {m['refused']['redundant']}, not a refusal) (arrivals {m['arrivals']}, budget left {m['budget_left']}) · pruned {m['edges_pruned']}/{m['edges_born']} = {100*m['pruned_share']:.1f} % (cross-thing born {m['edges_cross']['born']} / pruned {m['edges_cross']['pruned']}) · disuse {m['removed_for_disuse']} | {gv(m)} |")
    m = M["v_retention"]; L.append(f"| (v) | {m['bar']} | " + ("; ".join(f"w{p['window']}: {p['before']:.3f} → first {p['first_after']:.3f} → last {p['last_in_window']:.3f} ({p['drop_pp']:+.1f} pp drop)" for p in m['pairs']) or m['note']) + f"{_why(m)} | {gv(m)} |")
    m = M["vi_knows_unknown"]; _pc = m.get("plant_clause") or {}
    L.append(f"| (vi) | {m['bar']} | plant zog answered {m['plant_zog']['answered_rate']:.2f} (as {m['plant_zog']['answered_as']}, abstain {m['plant_zog']['abstain']}; plant shown {m.get('plant_shown')} — plant clause {'graded' if _pc.get('graded', True) else 'NOT GRADABLE'}) · null vex abstains {m['null_vex']['abstain_rate']:.2f} (answered as {m['null_vex']['answered_as']}) · Q5 {m['Q5_spiral_abstain']:.2f} · false {m['false_abstention']:.3f} | {gv(m)} |")
    # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:08 +0400 — the merge: a4-integration's ONE renderer (cost_line) now carries master's
    # READER-LAG-0923 clauses (the sleeps window's end and the lag text); `_LS` is the fallback when the mark carries no lag of its own.
    m = M["viii_cost"]; L.append(cost_line(m, gv, _LS))   # A4L-COST: one renderer (cost_line, above) for both forms — the witness beside the cost
    if "ix_not_luck" in M:
        m = M["ix_not_luck"]; L.append(f"| (ix) | {m['bar']} | rank {m['rank_of_own']} of {m['of']} (own {m['own_composite']}; best random {m['best_random']}){_why(m)} | {gv(m)} |")
    m = M["x_gaze_finds_thing"]; L.append(f"| (x) | {m['bar']} | gaze {m['gaze_rate']:.3f} vs random {m['random_rate']:.3f} (×{m['ratio']}) | {gv(m)} |")
    m = M["xi_gaze_earns_place"]; L.append(f"| (xi) | {m['bar']} | Q1 gaze {m['Q1_gaze']:.3f} − one-glance {m['Q1_one_glance']} (first-fixation-only {m['Q1_first_fixation_only']}; random-gaze {m['Q1_random_gaze']}){_why(m)} | {gv(m)} |")
    m = M["MODULATION"]; reg = m.get("regime", {}) or {}; nb = m.get("null_fake_boundary_w0", {}) or {}
    L.append(f"| MODULATION | {m['bar']} | windows(regime) {m.get('graded_windows_regime')} · windows(fixed) {m['graded_windows']} · null(regime) {nb.get('no_spike_regime')} · null(fixed) {nb.get('no_spike')} "
             f"· regime band {reg.get('null_band_95')} (n={reg.get('null_ratio_samples')}, share {reg.get('null_share_within_band')}) · regime settle bar {reg.get('settle_bar_err_95')} "
             f"· not gradable (§18 add. 4: no new thing reached 10 showings) {m.get('not_gradable_windows')} "
             f"· no-predict twin max err {m['no_predict_twin_err']} · fixed-bar record {pf(m.get('pass_fixed_bars_record'))} · {m.get('reason','')} | {gv(m)} |")
    m = M["TWINS"]["random_gaze_loses_xi"]; L.append(f"| TWINS random-gaze | loses (xi) | margin {m['margin']}{_why(m)} | {gv(m)} |")
    def gv(m): return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"
    m = M["W3_2_rules"]; L.append(f"| W3-2 rules | {m['bar']} | filed {m['live']['filed']} (induce {m['live']['induce']}, deduce {m['live']['deduce']}, refused {m['live']['refused']}) · scored {m['live']['scored']} · accuracy {m['live']['accuracy']} · words {m['live']['words']} · T-shuffle scored {m['T_shuffle']['scored']} acc {m['T_shuffle']['accuracy']} · parked rules {m['parked_rules']} · clusters: rules reached {m['cluster_control'].get('words_with_rules')} of {m['cluster_control'].get('eligible_words')} eligible words (of {m['cluster_control'].get('words')}), wrong-cell rules {m['cluster_control'].get('wrong_cell_rules')} {m['reason']} | {gv(m)} |")
    m = M["DOOR"]; L.append(f"| DOOR | {m['bar']} | pictures {m['pictures']} (rows {m['folder_rows']}) · words {len(m['folder_words'])} · sight-only {m['sight_only_rows']} (first seq {m['sight_only_first_seq']}) · recognition {m['recognition_of_seen_pictures']} {m['reason']} | {gv(m)} |")
    m = M["W3_1_beliefs"]; L.append(f"| W3-1 beliefs | {m['bar']} | rows {m['rows']} · kinds {m['kinds']} · standing words {m['standing_words']} of {m['words_heard']} heard · max belief rows per word {m['max_belief_rows_per_word']} · extra belief rows {m['extra_belief_rows']} vs clash rows {m['clash_rows']} · unaccounted {m['unaccounted']} | {gv(m)} |")
    m = M["PARK"]; L.append(f"| PARK | {m['bar']} | parked {m['parked']} of {m['thinks']} thinks (rules {m['parked_rules']}) — {m['reason']} | {gv(m)} |")
    # edit: Claude (Fable 5.1), 2026-09-22 19:3x +0400 — THE ONE LIFE's marks (PREREG §19)
    for _k in ("ACT", "SOUND", "SIZING", "GRADE", "SELF", "SURPRISE", "COARSE", "QUESTION", "SENTENCE", "HANDS", "THREAD", "HASH", "READ", "EVOLVE", "WEB", "STAGE"):
        if _k in M:
            m = M[_k]
            if _k == "HASH":     # A4L-COST (Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:59 +0400)
                body = (f"form {m.get('status_hash_form')} · hash ms last {m.get('status_hash_ms_last')} · hashed rows {m.get('hash_rows')} · "
                        f"(iii) {m.get('iii')} · (ii) {m.get('ii')} — {m['reason']}")
            elif _k == "THREAD":
                body = (f"max sense gap {m.get('max_gap_s')} s (eye/ear {m.get('gaps_per_hour')}) · in the minute after a sleep: max {m.get('max_gap_in_sleep_minutes_s')} s, "
                        f"{m.get('over_bar_in_sleep_minutes')} over the bar · outside those minutes: max {m.get('max_gap_outside_sleep_minutes_s')} s, {m.get('over_bar_outside_sleep_minutes')} over the bar "
                        f"({m.get('sleeps_on_record')} sleeps) · thinks {m.get('thinks')} waits {m.get('think_waits')} (share {m.get('waits_share')}, {m.get('think_wait_ms')} ms) · think ms last {m.get('think_ms_last')} median {m.get('think_ms_median')} — {m['reason']}")
            elif _k == "HANDS":
                body = f"runs {m.get('runs')} (by program {m.get('runs_by_program')}; no road {m.get('hands_no_road')}) · asked {m.get('asked')} recognised {m.get('recognised_share')} vs shuffled shelf {m.get('shuffled_share')} · touch {m.get('touch_events')} smell {m.get('smell_events')} — {m['reason']}"
            elif _k == "QUESTION":
                body = (f"questions {m.get('questions')} (forms {m.get('forms')}; needed {m.get('needed')}) · ANSWERED {m.get('answered')} (share {m.get('answered_share')}): by the maker {m.get('answered_by_maker')}, "
                        f"by the lexicon {m.get('answered_by_lexicon')}, both {m.get('answered_by_both')} · unanswered {m.get('unanswered')} (about the hands' own pictures, no door answers: {m.get('unanswered_hands_pictures')}; "
                        f"others by form {m.get('unanswered_other_by_form')}) · rows stamped `answering` {m.get('answered_rows')} (ear+eye) · STATUS written {m.get('status_written')} answered {m.get('status_answered')} — {m['reason']}")
            elif _k == "SENTENCE":
                body = (f"missions {m.get('missions')} (one per game episode; {m.get('missions_per_frame')} per frame, lift {m.get('max_lift_per_frame')}) · the world's max pair lift {m.get('max_lift')} on «{m.get('max_pair')}» · "
                        f"frames filed {m.get('frames_filed')} scored {m.get('frames_scored')} true {m.get('frames_true')} (precision {m.get('precision')}) · said {m.get('said')} heard yes {m.get('heard_yes')} no {m.get('heard_no')} — {m['reason']}")
            elif _k == "READ":
                _s = m.get("reading_sample") or {}; _b = m.get("blind_twin") or {}; _rd = m.get("reading") or {}
                body = (f"words born from shelf {m.get('words_born_from_shelf')} · frames {(m.get('frames') or {}).get('filed')} (precision vs shuffled {(m.get('frames') or {}).get('precision')}) · "
                        f"reading {_rd.get('share')} on {_rd.get('n')} words — the sample: seed {_s.get('seed')}, {len(_s.get('words') or [])} of {_s.get('eligible')} eligible "
                        f"(heard {_s.get('population_heard')}; excluded: heard elsewhere too {len(_s.get('excluded_other_source') or [])}, not on the cut tape {_s.get('excluded_not_on_cut_tape')}) · "
                        f"blind twin {'share ' + str(_b.get('share')) + ' in ' + str(_b.get('seconds')) + ' s' if _b.get('share') is not None else _b.get('reason')} — {m['reason']}")
            elif _k == "EVOLVE":
                body = (f"judged rounds {m.get('judged_rounds')} (needed {m.get('needed')}; every {m.get('every_h')} h → {m.get('rounds_possible')} possible) · void rounds {m.get('void_rounds')} {m.get('void_round_reasons')} · "
                        f"paired {m.get('paired_readings')} · adoptions {m.get('adoptions')} {m.get('epoch_events')} · max shadow lag {m.get('max_shadow_lag_rows')} rows — {m['reason']}")
            elif _k == "WEB":
                body = f"web rows {m.get('web_rows')} · made {m.get('made')} · refused rate {m.get('refused_rate')} hold {m.get('refused_hold')} · untraceable {m.get('untraceable')} · stage 4 reached {m.get('stage4_reached')} — {m['reason']}"
            elif _k == "STAGE":
                _ser = " ".join(("".join(k if x.get(k) is True else "·" for k in "abcde")) for x in (m.get("readiness_series") or []))
                body = (f"stage-4 events {m.get('stage_events')} {m.get('series')} · READINESS at {m.get('readiness_boundaries')} SIT boundaries: held a {(m.get('held') or {}).get('a')} · b {(m.get('held') or {}).get('b')} · "
                        f"c {(m.get('held') or {}).get('c')} · d {(m.get('held') or {}).get('d')} · e {(m.get('held') or {}).get('e')}; all five {m.get('all_five_held')} (longest run {m.get('longest_all_five_streak')}, 2 open the door) · "
                        f"per boundary [{_ser}] · {m.get('readiness_note')} — {m['reason']}")
            elif _k == "SURPRISE":
                body = (f"overall confirmed share {m.get('overall_share')} over {m.get('canvases')} canvases · maker things rising {m.get('things_rising')} of {m.get('things_graded')} (null mean {m.get('null_mean')} p95 {m.get('null_p95')}) · first 500 {m.get('first_500')} → last 500 {m.get('last_500')} (rise {m.get('rise_first_to_last_500')}) · by source {m.get('by_source')} · printed not graded {len(m.get('printed_not_graded') or {})} things · blind-surprise twin confirmed {m.get('twin_confirmed')} · STATUS confirmed {m.get('status_confirmed')} surprised {m.get('status_surprised')} — {m['reason']}")
            elif _k == "COARSE":
                body = f"Q1 all words {m.get('q1_live')} vs blind-coarse {m.get('q1_blind_coarse')} · house {m.get('house_live')} vs {m.get('house_blind_coarse')} (prediction held {m.get('house_prediction_held')}) · cup {m.get('cup_live')} vs {m.get('cup_blind_coarse')} — {m['reason']}"
            elif _k == "GRADE":
                _pc = m.get("plant_clause") or {}
                body = f"null graded {m['null_graded']} · plant answered {m.get('plant_answered_rate')} graded {m['plant_graded']} (plant shown {m.get('plant_shown')}; plant clause {'graded' if _pc.get('graded', True) else 'NOT GRADABLE'}) · hedge rate on seen words {m['hedge_rate']} — {m['reason']}"
            elif _k == "SELF":
                body = f"self beliefs {m['self_beliefs']} (citing two body rows {m['self_beliefs_citing_two_body_rows']}; words {m['self_words']}) · self thinks {m['self_thinks']} · body rows {m['body_rows']} · skipped for backlog {m['think_skipped_for_backlog']} — {m['reason']}"
            elif _k == "ACT":
                body = (f"mind-chosen {m['mind_chosen']} of {m['game_outcomes']} (share {m['mind_share']}) · mismatches journal {m['mismatches_journal']} status {m['mismatches_status']} · "
                        f"the GAME's census {m['census']} max {m['max_share']} zero {m['zero_acts']} · the last {m.get('last_n')} game acts {m.get('census_last100')} max {m.get('max_share_last100')} (the ≥ 95 % clause) · "
                        f"STATUS acts_chosen (with the mouth's say, printed only) {m.get('census_all')} · shuffled twin diverged {m.get('shuffled_twin_diverged')} · reward mean {m['reward_mean']} success/episode {m['success_per_episode']} (random null {m['random_null_success']}) — {m['reason']}")
            elif _k == "SOUND":
                body = f"ear-sound rows {m['ear_sound_rows']} · consumed {m['consumed']} · errors {m['errors']} · STATUS sound_events {m['status_sound_events']} — {m['reason']}"
            else:
                _pc = m.get("plant_clause") or {}
                body = f"born {m['sight_born']} of {m['sight_nmax']} · prediction {m['prediction']} · refused at NMAX {m['births_refused_nmax']} · series/h {m['series_sight_births_per_hour']} · plant shown {m['plant_shown_moments']} birthed {m['plant_sight_births']} (plant clause {'graded' if _pc.get('graded', True) else 'NOT GRADABLE'}) — {m['reason']}"
            L.append(f"| {_k} | {m['bar']} | {body} | {gv(m)} |")
    L.append(f"| TWINS no-sleep / no-curiosity / no-park | (v) / door / PARK | {M['TWINS']['no_sleep_v']} · {M['TWINS']['no_curiosity']['reason']} · {M['TWINS']['no_park']['reason']} | not graded |")
    # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:50 +0400 — A4-LADDER-PREREG §3.4: the LANG rung's L1-L9, one row each.
    if isinstance(M.get("CHAT"), dict):
        C = M["CHAT"]
        if "error" in C:
            L.append(f"| CHAT | §3.4 L1-L9 | the chat marks raised: {C['error']} | FAIL |")
        for _ck in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9"):
            m = C.get(_ck)
            if not isinstance(m, dict):
                continue
            nums = {k_: v_ for k_, v_ in m.items() if k_ not in ("bar", "reason", "graded", "pass", "said", "per_hour", "by_family")}
            extra = m.get("said") or m.get("per_hour") or m.get("by_family") or ""
            L.append(f"| CHAT {_ck} | {m.get('bar', '')} | {json.dumps(nums, default=str)[:600]} {json.dumps(extra, default=str)[:400] if extra else ''} — {m.get('reason')} | {gv(m)} |")
        if isinstance(C.get("disjoint"), dict):
            L.append(f"| CHAT pictures disjoint | §3.3: seed-3 renders never a tape canvas (+ planted control) | {json.dumps(C['disjoint'])} | reported |")
    L += ladder2_rows(M, gv)   # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:32 +0400 — READER v3.5: the ladder-2 marks' rows (A4-LADDER-2-PREREG §2)
    L += ["", f"**failed ({len(R['marks_failed'])}):** {', '.join(R['marks_failed']) or 'none'}", "",
          f"**not gradable ({len(R.get('marks_not_gradable') or [])}) — never in the failed list (READER-FIX-0923 (9)):** "
          + ("; ".join(f"{k} ({r})" for k, r in (R.get("marks_not_gradable") or [])) or "none")]
    if R.get("marks_missing_graded"):
        L += ["", f"**marks carrying no `graded` (judged by their pass):** {R['marks_missing_graded']}"]
    L += ["", "## Twins (each a replay of the same tape blind to one gene; Q1 on all 16 words, the seen-words Q1 beside it)", "", "| twin | Q1 (all) | Q1 (seen) | composite (all) | cells |", "|---|---|---|---|---|"]
    for b in BLINDS:
        t = M["TWINS"][b]; L.append(f"| {b} | {t['Q1']} | {t['Q1_seen']} | {t['composite']} | {t['cells']} |")
    L += ["", "## Plants", "", json.dumps(M["PLANTS"], indent=1, default=str), "", "## BANDS (reported, never gating)", "", json.dumps(M["BANDS"], indent=1, default=str)[:3000],
          "", "## ALIVE per hour", "", json.dumps(A["per_hour"]), "",
          f"failed: {R['marks_failed'] or 'none'} · not gradable: {[k for k, _r in (R.get('marks_not_gradable') or [])] or 'none'} · {R['seconds_total']} s"]
    (out / "VERDICT.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
