#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1 / §2 T, G: the reader of the brain's turns PER HAND (world), as series.
"""tools/brain/worlds_read.py — what the brain said, expected and learned in each world it heard, read from a life's journal alone.

    PYTHONPATH=<repo> /usr/bin/python3 -B tools/brain/worlds_read.py --journal <journal.jsonl | dir> [--window 100] [--out <dir>]

It reads the mind's `kind: "brain"` rows: `turn` (heard, say, expected, surprise, n_hyp, world) and `learn` (words, world). A row
without `world` is the scene hand's. Per world it prints, by windows of canvases: the say rate, the AGREE rate (a said word is
among the heard words — for a ONE-WORD world such as the maker's this is TRUE of the thing, for the scene it is agreement with the
parent, not truth: the parent names one thing of several), the mean surprise, the distinct words said, and the hypotheses per
canvas. Per word and world: its first meeting, its first agreed say. TRANSFER (PREREG-HEARS-2 §2 T): on the first `k` maker
meetings of each maker word, the agree rate, split by whether the word was already learned from the scene hand before its first
maker meeting (shared) or not (maker-only). No bar is set here; the law names which readings it reads."""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Dict, List, Optional

SCENE = "scene"
TRANSFER_K = 3


def read_journal(p: Path) -> List[Dict[str, object]]:
    files = sorted(p.glob("*.jsonl")) if p.is_dir() else [p]
    out: List[Dict[str, object]] = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if line.strip() and '"brain"' in line:
                    r = json.loads(line)
                    if r.get("kind") == "brain":
                        out.append(r)
    return out


def read(rows: List[Dict[str, object]], window: int = 100, k: int = TRANSFER_K) -> Dict[str, object]:
    by_world: Dict[str, Dict[str, object]] = {}
    first_meeting: Dict[str, Dict[str, int]] = collections.defaultdict(dict)     # world → word → learn order in that world
    first_agreed: Dict[str, Dict[str, int]] = collections.defaultdict(dict)
    learned_order: Dict[str, int] = {}                                            # world → canvases learned so far
    scene_known: set = set()                                                      # words learned from the scene hand so far
    transfer: Dict[str, List[Dict[str, object]]] = {"shared": [], "maker-only": []}
    meetings_so_far: Dict[str, Dict[str, int]] = collections.defaultdict(lambda: collections.defaultdict(int))
    first_side: Dict[tuple, str] = {}                                             # (world, word) → shared | maker-only, fixed at its first meeting
    for r in rows:
        w = str(r.get("world") or SCENE)
        act = r.get("act")
        if act == "turn":
            d = by_world.setdefault(w, {"turns": 0, "windows": [], "_cur": None, "said_words": collections.Counter(),
                                        "n_hyp": collections.Counter()})
            i = d["turns"]
            d["turns"] += 1
            if i % window == 0:
                d["_cur"] = {"from": i, "n": 0, "said": 0, "agreed": 0, "asked": 0, "surprise_sum": 0.0, "surprise_n": 0, "words": set()}
                d["windows"].append(d["_cur"])
            c = d["_cur"]
            c["n"] += 1
            heard = [str(x) for x in (r.get("heard") or [])]
            say = r.get("say") or None
            agreed = False
            if say:
                c["said"] += 1
                words = [str(x) for x in say.get("words") or []]
                agreed = any(x in heard for x in words)
                c["agreed"] += int(agreed)
                for x in words:
                    c["words"].add(x)
                    d["said_words"][x] += 1
            if r.get("ask"):
                c["asked"] += 1
            if r.get("surprise") is not None:
                c["surprise_sum"] += float(r["surprise"])
                c["surprise_n"] += 1
            d["n_hyp"][int(r.get("n_hyp") or 0)] += 1
            # per word in this world: its meetings so far (this canvas included), the first agreed say
            for x in dict.fromkeys(heard):
                meetings_so_far[w][x] += 1
                if agreed and x in [str(y) for y in say.get("words") or []] and x not in first_agreed[w]:
                    first_agreed[w][x] = i
            if w != SCENE and len(heard) == 1:          # TRANSFER: the first k meetings of each word of another hand
                x = heard[0]
                if meetings_so_far[w][x] <= k:
                    if (w, x) not in first_side:
                        first_side[(w, x)] = "shared" if x in scene_known else "maker-only"
                    side = first_side[(w, x)]
                    transfer[side].append({"world": w, "word": x, "meeting": meetings_so_far[w][x], "agreed": bool(agreed),
                                           "say": ([str(y) for y in say.get("words")] if say else None)})
        elif act == "learn":
            n = learned_order.get(w, 0)
            for x in dict.fromkeys(str(y) for y in (r.get("words") or [])):
                first_meeting[w].setdefault(x, n)
                if w == SCENE:
                    scene_known.add(x)
            learned_order[w] = n + 1
    out: Dict[str, object] = {"worlds": {}, "transfer": {}, "window": window, "transfer_k": k}
    for w, d in by_world.items():
        wins = []
        for c in d["windows"]:
            wins.append({"from": c["from"], "n": c["n"], "say_rate": c["said"] / c["n"], "agree_rate": (c["agreed"] / c["said"] if c["said"] else None),
                         "ask_rate": c["asked"] / c["n"], "surprise": (c["surprise_sum"] / c["surprise_n"] if c["surprise_n"] else None),
                         "distinct_said": len(c["words"])})
        out["worlds"][w] = {"turns": d["turns"], "learned": learned_order.get(w, 0), "windows": wins,
                            "said_words": dict(d["said_words"].most_common()), "n_hyp": dict(sorted(d["n_hyp"].items())),
                            "first_meeting": dict(sorted(first_meeting[w].items(), key=lambda kv: kv[1])),
                            "first_agreed_say": dict(sorted(first_agreed[w].items(), key=lambda kv: kv[1]))}
    for side, rows_ in transfer.items():
        n = len(rows_)
        out["transfer"][side] = {"n": n, "agreed": sum(1 for t in rows_ if t["agreed"]), "rate": (sum(1 for t in rows_ if t["agreed"]) / n if n else None),
                                 "words": sorted({t["word"] for t in rows_}), "rows": rows_}
    return out


def report(o: Dict[str, object]) -> List[str]:
    L = [f"WORLDS the brain heard: {sorted(o['worlds'])} · window {o['window']} canvases"]
    for w, d in o["worlds"].items():
        L.append(f"  [{w}] turns {d['turns']} · learned {d['learned']} · hypotheses per canvas {d['n_hyp']}")
        L.append("    from     n   say   agree  ask   surprise  distinct_said")
        for c in d["windows"]:
            f = lambda v: "  —  " if v is None else f"{v:.3f}"
            L.append(f"    {c['from']:6d} {c['n']:5d}  {f(c['say_rate'])} {f(c['agree_rate'])}  {f(c['ask_rate'])} {f(c['surprise'])}    {c['distinct_said']}")
        L.append(f"    first meeting (learn order in this world): {d['first_meeting']}")
        L.append(f"    first agreed say (turn order in this world): {d['first_agreed_say']}")
        L.append(f"    words said: {d['said_words']}")
    t = o["transfer"]
    L.append(f"  TRANSFER on the first {o['transfer_k']} meetings of each word of another hand (agree = the say is the hand's word):")
    for side in ("shared", "maker-only"):
        s = t.get(side) or {"n": 0, "agreed": 0, "rate": None, "words": []}
        rate = "—" if s["rate"] is None else f"{s['rate']:.3f}"
        L.append(f"    {side:10s} n {s['n']:3d} agreed {s['agreed']:3d} rate {rate} words {s['words']}")
    return L


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="worlds_read")
    ap.add_argument("--journal", required=True)
    ap.add_argument("--window", type=int, default=100)
    ap.add_argument("--k", type=int, default=TRANSFER_K)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rows = read_journal(Path(a.journal))
    o = read(rows, window=int(a.window), k=int(a.k))
    lines = report(o)
    print("\n".join(lines))
    if a.out:
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "worlds.json").write_text(json.dumps(o, indent=1, sort_keys=True))
        (out / "worlds.txt").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
