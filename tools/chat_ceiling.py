#!/usr/bin/env python3
# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:51 +0400 — A4L-LANG task 0 (b) as a tool (A4-LADDER-PREREG §3.4
# L5): THE WHERE POINTING CEILING, measured BEFORE a life on a COPY of a snapshot, on the seat's OWN where-canvases
# (tools/chat_seat.plan_slot, the slots k = 6 + 7i — the 7-slot cycle's where positions — two held-out things on one canvas,
# seed 3). A canvas counts when a LOCATED glance's window centre lies inside the asked thing's bbox AND that glance's own
# single-glance recall is the asked word. Read-only: the organism's state hash is asserted unchanged. A reader of a snapshot,
# never a sense, never the seat (the seat never imports the machinery).
"""usage: chat_ceiling.py --state <a COPY of a life's state/ dir> --genome G [--n 50] [--seed 20260923] [--out FILE]"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from genome import gaze                                   # noqa: E402
from genome.machinery import Organism, parse_genome        # noqa: E402
from tools import chat_seat                                # noqa: E402


def pointing_ceiling(org: Organism, g, ledger_words, plans) -> dict:
    """The share of `plans` (where-plans carrying picture + bboxes + thing) where some located glance is on the asked thing
    AND recalls it; beside it, the POINT rule itself (the FIRST located glance recalled as the asked word, graded on its
    centre) — the rule L5 grades."""
    h0 = org.state_hash(); hits = rule = 0; per = []
    glance = int((g.gaze or {}).get("glance", 32))
    for p in plans:
        gl = gaze.glances(p["picture"], g.retina, g.gaze, "surprise", p["id"], colour=g.colour)
        t, l, hh, ww = p["bboxes"][p["thing"]]
        on, said = [], []
        for i in range(len(gl["fix"])):
            top, left = gl["windows"][i]; cy, cx = top + glance / 2.0, left + glance / 2.0
            on.append(t <= cy < t + hh and l <= cx < l + ww)
            c = org.recall("sight", gl["feats"][i])["cell"]
            ws = ledger_words.get(int(c), set()) if c is not None else set()
            said.append(next(iter(ws)) if len(ws) == 1 else None)
        ok = any(o and s == p["thing"] for o, s in zip(on, said)); hits += ok
        first = next((i for i, s in enumerate(said) if s == p["thing"]), None)
        rule += bool(first is not None and on[first])
        per.append({"id": p["id"], "thing": p["thing"], "other": p.get("other"), "on": on, "said": said, "hit": ok})
    assert org.state_hash() == h0, "the ceiling probe changed the organism"
    n = len(plans)
    return {"n": n, "hits": hits, "ceiling": round(hits / n, 4) if n else None, "point_rule_hits": rule,
            "point_rule_share": round(rule / n, 4) if n else None, "per_canvas": per}


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--state", required=True); ap.add_argument("--genome", required=True)
    ap.add_argument("--n", type=int, default=50); ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--phrasings", default=str(ROOT / "tools" / "chat_dev_phrasings.json")); ap.add_argument("--out")
    a = ap.parse_args(argv)
    g = parse_genome(Path(a.genome).read_text())
    st = Path(a.state)
    org = Organism.load(st / "organism", g)
    L = json.loads((st / "ledger.json").read_text())
    Lw = {int(k): set(v) for k, v in L["words"].items()}
    P = chat_seat.load_phrasings(a.phrasings)
    plans = [chat_seat.plan_slot(6 + 7 * i, a.seed, P, hour=1.0 + (6 + 7 * i) * 120 / 3600.0) for i in range(a.n)]
    R = pointing_ceiling(org, g, Lw, plans)
    R.update({"state": str(st), "genome": str(a.genome), "seed": a.seed, "moments": org.t, "sight_cells": int(org.sight.n)})
    print(json.dumps({k: v for k, v in R.items() if k != "per_canvas"}))
    if a.out:
        Path(a.out).write_text(json.dumps(R, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
