#!/usr/bin/env python3
# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:02 +0400 — PREREG-KW-1 §3.3 / §4.3: THE SELF, on a closed lean life's own record.
"""tools/web/kw1_self.py --root <closed life root> --out <dir> — the memories of the self, placed before life and kept or demoted
by it (K9), the lived self equal to a recount (K10), and whether its lived reliability knows its own exam answers (K11).

Reads (never writes) <root>/journal/*.jsonl in order: learn rows (fixations), calibrate rows (the brain's own learned kinds),
turn rows (what it expected, what it heard, its surprise); <root>/grade/grade.json (the fresh sitting's M1 items and whether each
was answered right) and <root>/tape (each M1 item's phrase). Only TRAINING rows feed the self (the sitting begins at the first
answer row). Writes <dir>/self.json and <dir>/SELF-READINGS.md."""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from genome import web as Wb  # noqa: E402

SHAPES = {"circle", "cross", "ring", "square", "star", "triangle"}   # declared in PREREG-KW-1 §4.3 (F1's check)


def claims():
    """PREREG-KW-1 §4.3, verbatim, placed before the record is read."""
    return [Wb.Claim("T1", "I look at no more than four places on a canvas.", "always", 0.05, author="the seat"),
            Wb.Claim("T2", "The parent says at most one word of each kind at a time.", "always", 0.05, author="the seat"),
            Wb.Claim("T3", "Usually, what I expect is what the parent says.", "usually", 0.70, author="the seat"),
            Wb.Claim("F1", "I see every thing the parent names.", "always", 0.05, author="the seat"),
            Wb.Claim("F2", "The parent always says three words.", "always", 0.05, author="the seat")]


def rows(root: Path):
    for f in sorted(glob.glob(str(root / "journal" / "*.jsonl"))):
        with open(f, "rb") as fh:
            for raw in fh:
                try:
                    yield json.loads(raw.replace(b"\x00", b"").decode("utf-8"))
                except Exception:
                    continue


def scene_of(moment: str):
    try:
        return int(str(moment).rsplit("t", 1)[1])
    except Exception:
        return None


def auroc(scores, labels):
    """P(a random right item scores above a random wrong one), ties counted 1/2."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    tot = 0.0
    for p in pos:
        for n in neg:
            tot += 1.0 if p > n else (0.5 if p == n else 0.0)
    return tot / (len(pos) * len(neg))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    node = Wb.SelfNode(author=root.name)
    for c in claims():
        node.place(c)
    C = node.claims
    kinds = None
    events = []                      # the recount's own copy of every training event (K10)
    n_learn = 0
    for r in rows(root):
        if r.get("kind") == "answer":
            break                    # the sitting begins: only training feeds the self
        if r.get("kind") != "brain":
            continue
        act = r.get("act")
        if act == "calibrate":
            kinds = [set(t) for t in (r.get("summary") or {}).get("types") or []]
        elif act == "learn":
            n_learn += 1
            nf = len(r.get("fix") or [])
            node.canvas(nf)
            C["T1"].observe(nf <= 4, at=scene_of(r.get("moment")))
            events.append(("canvas", nf))
        elif act == "turn":
            at = r.get("scene")
            heard = [str(w) for w in (r.get("heard") or [])]
            expected = [list(h) for h in (r.get("expected") or [])]
            surprise = r.get("surprise")
            node.turn(heard, expected, surprise)
            events.append(("turn", heard, expected, surprise))
            if kinds:
                C["T2"].observe(all(sum(1 for w in heard if w in k) <= 1 for k in kinds), at=at)
            if surprise is not None:
                C["T3"].observe(surprise == 0, at=at)
                heard_shapes = [w for w in heard if w in SHAPES]
                if heard_shapes:
                    union = {w for h in expected for w in h}
                    C["F1"].observe(any(w in union for w in heard_shapes), at=at)
            C["F2"].observe(len(heard) == 3, at=at)
    # K10: the recount, written here, from the events alone
    fix, n_exp, ok, words = {}, 0, 0, {}
    for e in events:
        if e[0] == "canvas":
            fix[str(e[1])] = fix.get(str(e[1]), 0) + 1
            continue
        _t, heard, expected, surprise = e
        if surprise is None:
            continue
        n_exp += 1
        ok += int(surprise == 0)
        union = {w for h in expected for w in h}
        for w in dict.fromkeys(heard):
            hc = words.setdefault(w, [0, 0])
            hc[0] += 1
            hc[1] += int(w in union)
    lived = node.to_dict()["lived"]
    k10 = (lived["fix"] == fix and lived["turns_expecting"] == n_exp and lived["expect_confirmed"] == ok and lived["words"] == words
           and lived["canvases"] == n_learn)
    planted = json.loads(json.dumps(words))
    w0 = next(iter(planted))
    planted[w0][1] += 1
    k10_plant = planted != lived["words"]
    # K11: the lived reliability of an item's phrase against whether the item was answered right
    g = json.loads((root / "grade" / "grade.json").read_text())
    items = {x["item_id"]: bool(x["correct"]) for x in g["items"]["fresh"]["M1"]}
    phrase = {}
    for f in sorted(glob.glob(str(root / "tape" / "*.jsonl"))):
        with open(f, "rb") as fh:
            for raw in fh:
                if b'"sense": "ask"' not in raw:
                    continue
                try:
                    r = json.loads(raw.replace(b"\x00", b"").decode("utf-8"))
                except Exception:
                    continue
                it = (r.get("meta") or {}).get("item")
                if it in items and r.get("payload"):
                    try:
                        phrase[it] = json.loads((root / "tape" / r["payload"]).read_text()).get("phrase") or []
                    except Exception:
                        pass
    rel = {w: hc[1] / hc[0] for w, hc in words.items() if hc[0]}

    def item_score(ph, table):
        vals = [table.get(w) for w in ph]
        vals = [v for v in vals if v is not None]
        return min(vals) if vals else 0.0

    ids = [i for i in items if i in phrase]
    labels = [items[i] for i in ids]
    k11 = auroc([item_score(phrase[i], rel) for i in ids], labels)
    null = []
    ws = sorted(rel)
    for dd in range(1, 21):
        perm = np.random.default_rng([dd, 7004]).permutation(len(ws))
        table = {ws[i]: rel[ws[j]] for i, j in enumerate(perm)}
        null.append(auroc([item_score(phrase[i], table) for i in ids], labels))
    nullv = sorted(x for x in null if x is not None)
    res = {"root": str(root), "claims": {k: c.to_dict() for k, c in C.items()}, "lived": lived, "K10": k10, "K10_plant_caught": k10_plant,
           "K11": {"items": len(ids), "right": sum(labels), "wrong": len(labels) - sum(labels), "auroc": k11,
                   "null_auroc": null, "null_p95": (nullv[int(0.95 * (len(nullv) - 1))] if nullv else None),
                   "reliability": dict(sorted(rel.items()))}}
    (out / "self.json").write_text(json.dumps(res, sort_keys=True, indent=1))
    L = ["# KW-1 · the self (written by tools/web/kw1_self.py)", "", f"record: {root} · training canvases {n_learn}", "",
         "| claim | text | quantifier | confirmed | contradicted | share confirmed | end state | first demoted at scene |", "|---|---|---|---|---|---|---|---|"]
    for k, c in C.items():
        d = c.to_dict()
        L.append(f"| {k} | {d['text']} | {d['quantifier']} {d['level']} | {d['confirmed']} | {d['contradicted']} | "
                 f"{(d['share_confirmed'] or 0):.3f} | {d['state']} | {d['first_demoted_at']} |")
    want = {"T1": "trusted", "T2": "trusted", "T3": "trusted", "F1": "demoted", "F2": "demoted"}
    k9 = all(C[k].state == v for k, v in want.items())
    L += ["", f"**K9 LIFE KEEPS THE TRUE AND DEMOTES THE FALSE:** {'PASS' if k9 else 'FAIL'} "
              f"({', '.join(f'{k} {C[k].state} (wanted {v})' for k, v in want.items())})",
          f"**K10 THE LIVED SELF IS TRUE:** recount equal {k10}; a planted change caught {k10_plant} → {'PASS' if (k10 and k10_plant) else 'FAIL'}",
          f"K11 reading: {res['K11']['items']} M1 items ({res['K11']['right']} right, {res['K11']['wrong']} wrong); type-2 area of the phrase's lived "
          f"reliability {k11} · the null's 20 draws (reliabilities permuted across words): p95 {res['K11']['null_p95']}, "
          f"{', '.join('%.3f' % x for x in nullv)}"
          + (" · UNDERPOWERED (fewer than 100 wrong items)" if res['K11']['wrong'] < 100 else ""),
          f"The lived self: {lived['canvases']} canvases; fixations a canvas {lived['fix']}; expectations confirmed "
          f"{lived['expect_confirmed']} of {lived['turns_expecting']}; per word (heard, named something it expected that word for): "
          + ", ".join(f"{w} {hc[1]}/{hc[0]}" for w, hc in sorted(lived['words'].items()))]
    text = "\n".join(L) + "\n"
    (out / "SELF-READINGS.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
