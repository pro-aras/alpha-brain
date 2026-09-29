#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:18 +0400 — new tool: STAGE −1 of «the brain takes its turn» (docs/organism/HUMAN-MECHANISM-MAP-2026-09-29.md §5 step 1).
"""tools/brain/diag/probe_drive.py --ws WS [--n 10000] [--out DIR] [--nulls 10]

Read on the BENCH, on TRAINING rows alone, with no production code changed: what the brain would SAY and ASK by itself at
every canvas, and what it EXPECTS before it hears — measured against the bench's truth, so the law's bars can be set at
their ceilings (SOLUTIONS #228 b) before anything is built.

THE TURN, as this probe defines it (the production function must give these numbers again):
  at a training canvas, BEFORE the brain learns from it, with the brain as it then is:
  things    the eye's hypotheses (genome.brain.things_in_view);
  order     the hypotheses by their number of fixations, most first, ties by the lower index («what it looked at most»);
  expect    per hypothesis, the LAW road's held words (RWRoad.held_words): the words it would expect to hear of that thing;
  say       the first hypothesis in `order` for which the mouth speaks (learners.produce_believed, the read-back
            included); at most one say a canvas; nothing before the first calibration;
  ask       the first hypothesis in `order` with NO held word; at most one ask a canvas; nothing before the first calibration;
  surprise  after the turn, against the parent's utterance U: h* = the hypothesis whose expected words hold the most of U
            (ties by `order`); surprise = 1 − |U ∩ expect[h*]| / |U|.
The truth (the thing a hypothesis is: marks.hyp_label over its fixations; a thing's true words: its shape, colour and size)
is read by the bench only. A presence count stands beside every rate. Nothing here writes the organ, a cache or a life root."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import cache as C          # noqa: E402
from brain.scene import learners as Lr      # noqa: E402
from brain.scene import marks as M          # noqa: E402
from brain.world.seeds import substream     # noqa: E402
from genome import brain as B               # noqa: E402
from tools.brain import gate_alone as GA    # noqa: E402
from tools.brain.diag import probe_fm2b as P   # noqa: E402

WINDOW = 1000


def turn(brain: "B.Brain", glance: Dict[str, object], scene: int, ws: int) -> Dict[str, object]:
    hyps, X = B.things_in_view(glance)
    n = int(X.shape[0])
    out: Dict[str, object] = {"n_hyp": n, "order": [], "expect": [], "believed": [], "say": None, "ask": None, "reason": None}
    if n == 0:
        out["reason"] = "nothing in view"
        return out
    order = sorted(range(n), key=lambda h: (-len(hyps[h].members), h))
    out["order"] = order
    out["members"] = [[int(m) for m in h.members] for h in hyps]
    if not brain.n_calibrations:
        out["reason"] = "not calibrated"
        return out
    road = brain.road()
    out["expect"] = [list(road.held_words(X[h])) for h in range(n)]
    Bv = road.believed(X)
    out["believed"] = [[Bv[k][h] for k in range(len(Bv))] for h in range(n)]
    tried = []
    for h in order:
        a = Lr.produce_believed(road, X, h, lambda h=h: substream(int(ws), f"turn-say:{int(scene)}:{h}"))
        tried.append({"hyp": h, "reason": a.get("reason")})
        if a.get("spoken"):
            m = a.get("margin")
            out["say"] = {"hyp": h, "words": list(a["spoken"]), "margin": (None if m is None or not np.isfinite(m) else float(m)),
                          "margin_inf": bool(m is not None and not np.isfinite(m))}
            break
    out["say_tried"] = tried
    for h in order:
        if not out["expect"][h]:
            out["ask"] = {"hyp": h}
            break
    return out


def surprise_of(t: Dict[str, object], U: List[str], key: str = "expect") -> Optional[float]:
    """1 − the largest share of the utterance's words one hypothesis's expectation holds. `key` = "expect" (the held words:
    every word whose band holds the thing) or "believed" (ONE name per learned type: the forced best guess)."""
    if not U or not t[key]:
        return None
    U = list(dict.fromkeys(U))
    got = -1
    for h in t["order"]:
        k = len(set(U) & set(w for w in t[key][h] if w is not None))
        if k > got:
            got = k
    return 1.0 - got / len(U)


def true_words(thing: Dict[str, object]) -> set:
    return {str(thing["shape"]), str(thing["colour"]), str(thing["size"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", type=int, required=True)
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--nulls", type=int, default=10)
    ap.add_argument("--out", default="/data/dev/brain-runs/day0929/drive/stage-1")
    a = ap.parse_args()
    t0 = time.process_time()
    cfg = P.brain_cfg()
    d = C.cache_dir(C.RUNS, a.ws, "train")
    C.check_code(d)
    train = C.ScenePercepts(d)
    truth = C.load_truth(d)
    n = min(a.n, len(train))
    brain = B.Brain(cfg)
    rows: List[Dict[str, object]] = []
    for i in range(n):
        g = GA.glance_of(train, i)
        h0 = brain.state_hash() if i in (300, 3000) else None        # the turn never learns: checked at two canvases
        t = turn(brain, g, i, a.ws)
        if h0 is not None and brain.state_hash() != h0:
            raise RuntimeError(f"the turn changed the brain at canvas {i}")
        tr = truth[i]
        U = train.words(i)
        things = tr["things"]
        labels = []
        if t["n_hyp"]:
            counts = M.hyp_counts(t["members"], tr["fix_thing"]) if "members" in t else []
            labels = [M.hyp_label(c) for c in counts]
        r = {"i": i, "n_hyp": t["n_hyp"], "n_things": len(things), "reason": t["reason"], "U": list(U),
             "calibrated": bool(brain.n_calibrations), "surprise": surprise_of(t, U, "expect"),
             "surprise_believed": surprise_of(t, U, "believed"), "say": None, "ask": None, "hyps": []}
        for h in range(len(labels)):
            lab = labels[h]
            tw = sorted(true_words(things[lab])) if lab is not None else None
            r["hyps"].append({"label": lab, "true": tw, "expect": (t["expect"][h] if t["expect"] else None),
                              "believed": (t["believed"][h] if t["believed"] else None)})
        if t["say"] is not None:
            h = t["say"]["hyp"]
            lab = labels[h]
            words = t["say"]["words"]
            ok = None if lab is None else all(w in true_words(things[lab]) for w in words)
            uniq = None
            if lab is not None:
                uniq = bool(M.unique_true(words, M.things_of(tr), lab, range(len(things))))
            r["say"] = {"hyp": h, "label": lab, "words": words, "true": ok, "unique_true": uniq, "margin_inf": t["say"]["margin_inf"],
                        "is_referent": (lab is not None and lab == int(tr["referent"]))}
        if t["ask"] is not None:
            h = t["ask"]["hyp"]
            r["ask"] = {"hyp": h, "label": labels[h]}
        rows.append(r)
        brain.learn(g, U, moment=f"sc{a.ws}t{i:06d}", scene=i, world_seed=a.ws)
    cpu_learn = time.process_time() - t0

    # ------------------------------------------------------------------ the readings
    def window_series(fn) -> List[Dict[str, object]]:
        out = []
        for s in range(0, n, WINDOW):
            out.append({"from": s, "to": min(n, s + WINDOW), **fn(rows[s:s + WINDOW])})
        return out

    def says(rs):
        cal = [r for r in rs if r["calibrated"] and r["n_hyp"] > 0]
        sd = [r["say"] for r in cal if r["say"] is not None]
        graded = [s for s in sd if s["true"] is not None]
        return {"canvases": len(cal), "said": len(sd), "rate": (len(sd) / len(cal) if cal else None),
                "graded": len(graded), "no_thing_under_the_target": len(sd) - len(graded),
                "true": (sum(bool(s["true"]) for s in graded) / len(graded) if graded else None),
                "unique_true": (sum(bool(s["unique_true"]) for s in graded) / len(graded) if graded else None),
                "two_or_more_words": sum(1 for s in sd if len(s["words"]) >= 2),
                "margin_inf": sum(1 for s in sd if s["margin_inf"]),
                "about_the_parents_thing": (sum(bool(s["is_referent"]) for s in graded) / len(graded) if graded else None)}

    def asks(rs):
        cal = [r for r in rs if r["calibrated"] and r["n_hyp"] > 0]
        ak = [r for r in cal if r["ask"] is not None]
        return {"canvases": len(cal), "asked": len(ak), "rate": (len(ak) / len(cal) if cal else None),
                "asked_a_thing": sum(1 for r in ak if r["ask"]["label"] is not None)}

    def surprise_by(key):
        def f(rs):
            v = [r[key] for r in rs if r[key] is not None]
            return {"n": len(v), "mean": (float(np.mean(v)) if v else None),
                    "expected_every_word": (sum(1 for x in v if x == 0.0) / len(v) if v else None)}
        return f

    # DOUBT INFORMS: the forced (believed) names of a DOUBTED hypothesis (no held word) against an UNDOUBTED one
    def doubt(rs):
        out = {}
        for key, want in (("doubted", True), ("undoubted", False)):
            right = total = hyp_n = 0
            for r in rs:
                if not r["calibrated"]:
                    continue
                for h in r["hyps"]:
                    if h["label"] is None or h["expect"] is None or h["believed"] is None:
                        continue
                    if (len(h["expect"]) == 0) != want:
                        continue
                    hyp_n += 1
                    for b in h["believed"]:
                        if b is None:
                            continue
                        total += 1
                        right += b in h["true"]
            out[key] = {"hypotheses": hyp_n, "believed_names": total, "right": (right / total if total else None)}
        return out

    # the NULLS (a distribution, SOLUTIONS #244 (2)): utterances / said phrases dealt to OTHER canvases
    rng = np.random.default_rng([int(a.ws), 20260929, 7])
    cal_rows = [r for r in rows if r["calibrated"] and r["n_hyp"] > 0]
    said_rows = [r for r in cal_rows if r["say"] is not None and r["say"]["true"] is not None]
    null_true, null_surprise, null_surprise_b = [], [], []
    sup_rows = [r for r in rows if r["surprise"] is not None]
    for _k in range(a.nulls):
        p = Lr.nshuf_permutation(rng, len(said_rows)) if len(said_rows) > 1 else np.arange(len(said_rows))
        ok = 0
        for j, r in enumerate(said_rows):
            words = said_rows[int(p[j])]["say"]["words"]
            lab = r["say"]["label"]
            tw = set(r["hyps"][r["say"]["hyp"]]["true"])
            ok += all(w in tw for w in words)
        null_true.append(ok / len(said_rows) if said_rows else None)
        p = Lr.nshuf_permutation(rng, len(sup_rows)) if len(sup_rows) > 1 else np.arange(len(sup_rows))
        for key, acc in (("expect", null_surprise), ("believed", null_surprise_b)):
            v = []
            for j, r in enumerate(sup_rows):
                U = list(dict.fromkeys(sup_rows[int(p[j])]["U"]))
                got = max(len(set(U) & set(w for w in (h[key] or []) if w is not None)) for h in r["hyps"]) if r["hyps"] else 0
                v.append(1.0 - got / len(U))
            acc.append(float(np.mean(v)) if v else None)

    res = {"world_seed": a.ws, "scenes": n, "cfg": cfg, "cpu_s": time.process_time() - t0, "cpu_s_learning_and_turns": cpu_learn,
           "first_calibrated_canvas": next((r["i"] for r in rows if r["calibrated"]), None),
           "says": says(rows), "says_series": window_series(says),
           "asks": asks(rows), "asks_series": window_series(asks),
           "surprise_held": surprise_by("surprise")(rows), "surprise_held_series": window_series(surprise_by("surprise")),
           "surprise_believed": surprise_by("surprise_believed")(rows),
           "surprise_believed_series": window_series(surprise_by("surprise_believed")),
           "doubt": doubt(rows),
           "null": {"says_true": null_true, "surprise_held": null_surprise, "surprise_believed": null_surprise_b, "draws": a.nulls},
           "say_lengths": {str(k): sum(1 for r in cal_rows if r["say"] is not None and len(r["say"]["words"]) == k) for k in (1, 2, 3)},
           "by_things_in_scene": {str(k): says([r for r in rows if r["n_things"] == k]) for k in (1, 2, 3)}}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"drive-{a.ws}-n{n}.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=GA._np))
    (out / f"drive-{a.ws}-n{n}-rows.jsonl").write_text("\n".join(json.dumps(r, default=GA._np) for r in rows) + "\n")
    s = res["says"]
    print(f"[drive {a.ws}] canvases {s['canvases']} · said {s['said']} (rate {s['rate']}) · true {s['true']} · unique-true {s['unique_true']} · "
          f"null true {[round(x, 3) for x in null_true]} · asks {res['asks']} · doubt {res['doubt']} · surprise held {res['surprise_held']} "
          f"null {[round(x, 3) for x in null_surprise]} · surprise believed {res['surprise_believed']} null {[round(x, 3) for x in null_surprise_b]} · "
          f"cpu {res['cpu_s']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
