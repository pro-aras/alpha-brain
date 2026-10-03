#!/usr/bin/env python3
# edit: Claude (Opus 5.5, swarm architect), 2026-10-03 10:53 +0400 — the HEARS-2 law review's counts, read from a closed life's tape alone (read-only):
# the maker canvases and words, the scene utterances spoken alone, the calibrations each arm (OFF = hears scene, ON = hears scene maker)
# makes, and for TRANSFER / GROWTH whether each maker turn can say its word at all (calibrated, and the word typed at the calibration in force).
"""docs/organism/hears/records/hears2_counts.py --tape <tape day file .jsonl> [--plant]

Counts for docs/organism/hears/REVIEW-HEARS-2-ARCHITECT-2026-10-03.md. It mirrors genome/brain.py's own rules without importing them:
`calibrate at 250 500 1000 2000 5000 10000 and before a sitting` (a sitting `begin` calibrates when scenes were learned since), a word
is typed at a calibration iff its meetings then are >= young (3), and a learned canvas counts one meeting per distinct word it carries.
The turn of a canvas precedes its learn (DRIVE «turn before hearing»), so a turn sees the meetings BEFORE that canvas.

--plant: the planted control (RULES §11). Three synthetic scene training canvases saying «bar» are put at the head of the tape; the
maker-only word «bar» then enters the maker world already met three times, so the count of usable maker-only TRANSFER turns must
change from 0. The script asserts the plant changed the event list and exits 1 if the count did not move (the plant was not caught)."""
from __future__ import annotations

import argparse
import collections
import json
import sys
from typing import Dict, List

SHARED = {"square", "ring", "cross", "star", "triangle", "circle"}
CAL = [250, 500, 1000, 2000, 5000, 10000]
YOUNG = 3


def load(path: str) -> List[Dict[str, object]]:
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["seq"])
    return rows


def events(rows: List[Dict[str, object]]) -> List[tuple]:
    words_at: Dict[str, List[str]] = collections.defaultdict(list)
    for r in rows:
        m = r.get("meta") or {}
        if r["sense"] == "ear" and m.get("source") in ("scene", "maker"):
            words_at[m["moment"]].append(str(m["word"]))
    ev = []
    for r in rows:
        m = r.get("meta") or {}
        src = m.get("source")
        if r["sense"] == "ask" and src == "scene" and m.get("form") == "begin":
            ev.append(("B", m["moment"], r["at"]))
        elif r["sense"] == "eye" and src == "scene" and m.get("kind") == "train":
            ev.append(("S", tuple(words_at[m["moment"]]), r["at"]))
        elif r["sense"] == "eye" and src == "maker":
            ev.append(("M", tuple(words_at[m["moment"]]), r["at"]))
        elif r["sense"] == "eye" and src == "scene" and m.get("kind") == "sitting":
            ev.append(("Q", m.get("set"), r["at"]))
    return ev


def simulate(ev: List[tuple], on: bool) -> Dict[str, object]:
    learned, ncal, last_cal = 0, 0, None
    meet: collections.Counter = collections.Counter()
    meet_at_cal: Dict[str, int] = {}
    cals, turns = [], []
    for kind, payload, at in ev:
        if kind == "B":
            if learned > 0 and last_cal != learned:
                ncal, last_cal, meet_at_cal = ncal + 1, learned, dict(meet)
                cals.append((learned, at, "begin"))
            continue
        if kind == "S" or (kind == "M" and on):
            if kind == "M":
                w = payload[0]
                turns.append({"word": w, "prior": meet[w], "calibrated": ncal > 0, "cal": last_cal,
                              "typed": meet_at_cal.get(w, 0) >= YOUNG, "mat": meet_at_cal.get(w, 0), "at": at})
            for w in set(payload):
                meet[w] += 1
            learned += 1
            if learned in CAL:
                ncal, last_cal, meet_at_cal = ncal + 1, learned, dict(meet)
                cals.append((learned, at, "list"))
    return {"cals": cals, "turns": turns, "meet": meet, "learned": learned}


def read(ev: List[tuple]) -> Dict[str, object]:
    mk = [e for e in ev if e[0] == "M"]
    words = collections.Counter(e[1][0] for e in mk)
    S = [e for e in ev if e[0] == "S"]
    alone = collections.Counter(e[1][0] for e in S if len(e[1]) == 1)
    lens = collections.Counter(len(e[1]) for e in S)
    B = [e for e in ev if e[0] == "B"]
    last_train_at = S[-1][2]
    on, off = simulate(ev, True), simulate(ev, False)
    T = on["turns"]
    first3 = {w: [t for t in T if t["word"] == w][:3] for w in words}
    sh = [t for w in words if w in SHARED for t in first3[w]]
    mo = [t for w in words if w not in SHARED for t in first3[w]]
    usable = lambda t: t["calibrated"] and t["typed"]
    last_cal = on["cals"][-1][0]
    last100 = T[-100:]
    return {
        "maker_canvases": len(mk), "maker_words": dict(words.most_common()),
        "shared": sorted(set(words) & SHARED), "maker_only": sorted(set(words) - SHARED),
        "scene_train": len(S), "scene_utterance_lengths": dict(sorted(lens.items())), "scene_alone_by_word": dict(alone.most_common()),
        "maker_during_training": sum(1 for e in mk if e[2] <= last_train_at),
        "maker_during_sittings": sum(1 for e in mk if e[2] > last_train_at),
        "sitting_begins": [b[2] for b in B],
        "maker_after_last_begin": sum(1 for e in mk if B and e[2] > B[-1][2]),
        "on_calibrations": on["cals"], "off_calibrations": off["cals"],
        "maker_before_first_on_calibration": [t["word"] for t in T if not t["calibrated"]],
        "transfer_first3": {w: [(t["prior"], t["calibrated"], t["typed"]) for t in first3[w]] for w in sorted(words, key=lambda w: (w not in SHARED, w))},
        "T_shared_n": len(sh), "T_shared_usable": sum(usable(t) for t in sh),
        "T_maker_only_n": len(mo), "T_maker_only_usable": sum(usable(t) for t in mo),
        "T_maker_only_calibrated": sum(t["calibrated"] for t in mo),
        "G_last100_typed": sum(usable(t) for t in last100), "G_last100_after_last_cal": sum(1 for t in last100 if t["cal"] == last_cal),
        "maker_after_last_on_calibration": sum(1 for t in T if t["cal"] == last_cal),
        # the meetings each maker word had AT the last ON calibration (its last turn carries the calibration in force)
        "maker_meetings_at_last_cal": {w: [t for t in T if t["word"] == w][-1]["mat"] for w in sorted(words)},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="hears2_counts")
    ap.add_argument("--tape", required=True)
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args(argv)
    ev = events(load(a.tape))
    base = read(ev)
    if not a.plant:
        print(json.dumps(base, indent=1, default=str))
        return 0
    first_at = ev[0][2]
    planted = [("S", ("bar",), first_at)] * 3 + ev
    assert planted != ev and len(planted) == len(ev) + 3, "the plant did not change the event list"
    got = read(planted)
    caught = got["T_maker_only_usable"] != base["T_maker_only_usable"]
    print(f"PLANT: maker-only usable TRANSFER turns {base['T_maker_only_usable']} -> {got['T_maker_only_usable']} · "
          f"{'CAUGHT' if caught else 'MISSED'}")
    return 0 if caught else 1


if __name__ == "__main__":
    sys.exit(main())
