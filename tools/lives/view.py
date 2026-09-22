#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-22 22:38 +0400 — THE ORGANISM IN THE TERMINAL (his 22:23 ask: «the visuals of what this organism looks like
# and its working in the terminal»). READ-ONLY over a life's root (STATUS.json, the tape's last eye payload, the journal's tail, the ask
# outbox, the exam files): never opens the mind's state, never writes under the root (#212). usage:
#     python3 tools/lives/view.py --root /data/dev/genome-lives/<name> [--watch 5] [--ascii] [--tail-bytes 3000000]
"""The organism in the terminal: the organ map with live counters, what it sees now, what it just thought, said, asked and did, the exam line."""
from __future__ import annotations
import argparse, collections, glob, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

BOLD, DIM, RST = "\x1b[1m", "\x1b[2m", "\x1b[0m"


def _tail_rows(path: Path, n_bytes: int):
    """The last `n_bytes` of a JSONL file as rows (the first, possibly torn, line dropped)."""
    if not path.exists():
        return []
    size = path.stat().st_size
    with open(path, "rb") as f:
        if size > n_bytes:
            f.seek(size - n_bytes); f.readline()
        data = f.read().decode("utf-8", "replace")
    rows = []
    for line in data.splitlines():
        line = line.strip()
        if line:
            try: rows.append(json.loads(line))
            except Exception: pass
    return rows


def _age(iso: str) -> str:
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        s = int((datetime.now(timezone.utc) - t).total_seconds())
        return f"{s // 3600}h{(s % 3600) // 60:02d}m" if s >= 3600 else (f"{s // 60}m{s % 60:02d}s" if s >= 60 else f"{s}s")
    except Exception:
        return "?"


def _picture(png_path: Path, cols: int, ascii_only: bool):
    """The last canvas as half-block cells (two pixels a character, truecolor) or as ASCII shades."""
    try:
        import numpy as np
        from PIL import Image
        im = Image.open(png_path).convert("RGB"); w, h = im.size
        rows_px = max(2, int(cols * h / w)) & ~1
        a = np.asarray(im.resize((cols, rows_px), Image.BILINEAR))
        out = []
        if ascii_only:
            g = a.mean(axis=2); shades = " .:-=+*#%@"
            for r in range(rows_px):
                out.append("".join(shades[min(9, int(v / 256 * 10))] for v in g[r]))
            return out
        for r in range(0, rows_px, 2):
            line = []
            for c in range(cols):
                t, b = a[r, c], a[r + 1, c]
                line.append(f"\x1b[48;2;{t[0]};{t[1]};{t[2]}m\x1b[38;2;{b[0]};{b[1]};{b[2]}m▄")
            out.append("".join(line) + RST)
        return out
    except Exception as e:
        return [f"(no picture: {e!r})"]


def _clip(s: str, n: int) -> str:
    import re
    plain = re.sub(r"\x1b\[[0-9;]*m", "", s)
    return plain if len(plain) <= n else plain[:n - 1] + "…"


def _box(title: str, lines, width: int):
    top = f"┌ {BOLD}{title}{RST} " + "─" * max(0, width - len(title) - 3) + "┐"
    body = [("│ " + _clip(l, width - 1) + " " * max(0, width - _vis(_clip(l, width - 1)) - 1) + "│") for l in lines]
    return [top] + body + ["└" + "─" * width + "┘"]


def _vis(s: str) -> int:
    import re
    return len(re.sub(r"\x1b\[[0-9;]*m", "", s))


def _side_by_side(a, b, gap=2):
    n = max(len(a), len(b)); wa = max((_vis(x) for x in a), default=0)
    return [(a[i] if i < len(a) else " " * wa) + " " * (wa - (_vis(a[i]) if i < len(a) else wa) + gap) + (b[i] if i < len(b) else "") for i in range(n)]


def render(root: Path, tail_bytes: int, ascii_only: bool) -> str:
    st = json.load(open(root / "STATUS.json")) if (root / "STATUS.json").exists() else {}
    started = (root / "STARTED-AT").read_text().strip() if (root / "STARTED-AT").exists() else "?"
    commit = (root / "CODE-COMMIT").read_text().strip()[:7] if (root / "CODE-COMMIT").exists() else "?"
    genome_lines = [l for l in (root / "GENOME.genome").read_text().splitlines() if l and not l.startswith("#")] if (root / "GENOME.genome").exists() else []
    decl = {l.split()[0] for l in genome_lines}
    tapes = sorted(glob.glob(str(root / "tape" / "*.jsonl"))); journals = sorted(glob.glob(str(root / "journal" / "*.jsonl")))
    tape = _tail_rows(Path(tapes[-1]), 400_000) if tapes else []
    jr = _tail_rows(Path(journals[-1]), tail_bytes) if journals else []
    eyes = [r for r in tape if r.get("sense") == "eye"]; last_eye = eyes[-1] if eyes else None
    outcomes = [r for r in tape if r.get("sense") == "outcome"]
    moments = [r for r in jr if "moment" in r and r.get("act") != "coarse"]
    thinks = [r for r in jr if isinstance(r.get("think"), dict)]
    acts = [r for r in jr if isinstance(r.get("act"), dict)]
    says = [r for r in jr if "say" in r]; questions = [r for r in jr if "question" in r]; hands = [r for r in jr if "act_chosen" in r]
    selfs = [r for r in thinks if r["think"].get("kind") == "self"]
    sleeps = [r for r in jr if "sleep" in r]; bodies = [r for r in jr if "body" in r]
    words = collections.Counter(r.get("word") for r in moments if r.get("word"))
    conf = [(sum(1 for f in r["confirmed"] if f), len(r["confirmed"])) for r in moments if isinstance(r.get("confirmed"), list)]
    share = (sum(a for a, _ in conf) / max(1, sum(b for _, b in conf))) if conf else None
    exams = sorted(p for p in glob.glob(str(root / "exam" / "*.json")) if not p.endswith("LAST.json"))
    ex = json.load(open(exams[-1])) if exams else {}
    q1_series = []
    for p in exams[-12:]:
        try: q1_series.append(((json.load(open(p)).get("ask_all_words") or {}).get("Q1") or {}).get("acc"))
        except Exception: q1_series.append(None)
    spark = "".join("▁▂▃▄▅▆▇█"[min(7, int((v or 0) * 8))] if v is not None else " " for v in q1_series)
    asks = sorted(glob.glob(str(root / "ask" / "out" / "*.json")))[-1:]
    last_ask = json.load(open(asks[0])) if asks else None
    hb = st.get("heartbeat_at"); crash = st.get("crash")
    W = 58
    head = [f"{BOLD}{root.name}{RST}  born {started}  code {commit}  genome {len(genome_lines)} lines · {len(decl)} organs ON",
            f"alive {_age(st.get('started_at') or '')}  heartbeat {_age(hb) if hb else '?'} ago  crash {crash}  restarts {st.get('sense_restarts')}  backlog {st.get('mind_backlog_rows')} rows  rss {st.get('rss_mb')} MB"]
    eye = _box("EYE · what it sees now", [f"moments {st.get('moments')}  canvases in tail {len(moments)}  last {last_eye['at'][11:19] if last_eye else '?'} ({(last_eye or {}).get('meta', {}).get('source')})",
                                          f"word heard: {BOLD}{(moments[-1].get('word') if moments else None)}{RST}  cells lit {moments[-1].get('cells') if moments else None}  err {moments[-1].get('err') if moments else None}",
                                          f"SURPRISE confirmed share (tail) {round(share, 3) if share is not None else 'not on this genome'}  gaze fix {moments[-1].get('fix') if moments else None}"], W)
    pic = _picture(root / "tape" / last_eye["payload"], 32, ascii_only) if last_eye and last_eye.get("payload") else ["(no eye row)"]
    sight = _box("SIGHT + WORDS areas · the cells", [f"sight born {st.get('sight_born')} / NMAX {st.get('sight_nmax')}   words born {st.get('words_born')} / {st.get('words_nmax')}",
                                                     f"cells {st.get('cells')}  edges born {st.get('edges_born')} pruned {st.get('edges_pruned')}  episodes {st.get('episodes')}",
                                                     f"arrivals {st.get('arrivals')}  budget left {st.get('budget_left')}  refused: nmax {st.get('births_refused_nmax')} budget {st.get('births_refused_budget')} redundant {st.get('births_refused_redundant')}",
                                                     f"words in tail: " + " ".join(f"{w}:{n}" for w, n in words.most_common(8))], W)
    mind = _box("MIND · thinking (its own thread)" if "THINK" in decl else "MIND · thinking", [f"thinks {st.get('thinks')}  parked {st.get('parked')}  beliefs {st.get('beliefs')}  predictions {st.get('predictions_filed')}/{st.get('predictions_scored')} scored  waits {st.get('think_waits', '—')}",
                                                                                              f"last think: {thinks[-1]['think'].get('item') if thinks else None} ({thinks[-1]['think'].get('kind') if thinks else None}) → {thinks[-1]['think'].get('outcome') if thinks else None}",
                                                                                              f"SELF beliefs (tail) {len(selfs)}: {(selfs[-1]['think'].get('note') or selfs[-1]['think'].get('outcome')) if selfs else '—'}"[:W - 1],
                                                                                              f"mind ms/canvas (1 min) {st.get('mind_ms_per_canvas_1min')}  think ms last/median {st.get('think_ms_last', '—')}/{st.get('think_ms_median', '—')}  sleeps {st.get('sleeps')} (last: {sleeps[-1]['sleep'] if sleeps else '—'})"[:W - 1]], W)
    voice = _box("MOUTH · QUESTIONS · the ask door", [f"said (tail) {len(says)}: {says[-1]['say'] if says else '—'}"[:W - 1],
                                                       f"questions (tail) {len(questions)}: {questions[-1]['question'] if questions else '—'}"[:W - 1],
                                                       f"last answer at the door: {(last_ask or {}).get('answer') or (last_ask or {}).get('error') or '—'}"[:W - 1]], W)
    act_census = collections.Counter(a["act"].get("act") for a in acts)
    rewards = [float(o.get("meta", {}).get("got") or 0.0) for o in outcomes if (o.get("meta") or {}).get("source") == "game"]
    doing = _box("HANDS · GAME · BODY · what it does", [f"game acts (tail) {len(acts)} census {dict(act_census)}  reward mean {round(sum(rewards) / len(rewards), 3) if rewards else '—'} over {len(rewards)}"[:W - 1],
                                                        f"hands runs (tail) {len(hands)}: {hands[-1]['act_chosen'].get('program') if hands else '—'}  touch {st.get('touch_events', '—')} smell {st.get('smell_events', '—')}"[:W - 1],
                                                        f"body readings (tail) {len(bodies)}: {bodies[-1]['body'] if bodies else '—'}"[:W - 1]], W)
    exam_lines = [f"exams {len(exams)}  last {ex.get('at', '?')[11:19] if ex else '—'}  Q1 all words {spark} {q1_series[-1] if q1_series else '—'}"]
    for side in ("ask_seen_words", "ask_all_words"):
        a = ex.get(side) or {}
        exam_lines.append(f"{side[4:]}: " + " ".join(f"{q} {a[q].get('acc'):.3f}" for q in ("Q1", "Q2", "Q3", "Q4") if q in a and a[q].get("acc") is not None) + f"  abstain {(a.get('Q1') or {}).get('abstain')}  hedge {(a.get('Q1') or {}).get('hedge_rate', '—')}"[:W - 1])
    exam = _box("EXAM · what it knows (held-out)", exam_lines, W)
    left = eye + sight + mind + voice + doing + exam
    right = [f"{DIM}the last canvas ({last_eye['payload'] if last_eye else '—'}){RST}"] + pic
    return "\n".join(head + [""] + _side_by_side(left, right))


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--watch", type=float, default=0.0)
    ap.add_argument("--ascii", action="store_true"); ap.add_argument("--tail-bytes", type=int, default=3_000_000)
    a = ap.parse_args(argv); root = Path(a.root)
    while True:
        out = render(root, a.tail_bytes, a.ascii)
        if a.watch > 0: sys.stdout.write("\x1b[2J\x1b[H")
        print(out + f"\n{DIM}read-only · {datetime.now().strftime('%H:%M:%S')} · {'every %.0f s (Ctrl-C to stop)' % a.watch if a.watch > 0 else 'once'}{RST}", flush=True)
        if a.watch <= 0: return 0
        time.sleep(a.watch)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
