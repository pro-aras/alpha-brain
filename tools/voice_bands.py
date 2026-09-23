#!/usr/bin/env python3
# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:31 +0400 — A4L-VOICE task 0 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3 V0): THE BANDS, before any machinery — the ceiling first (#228 (b), #231 (3)).
"""usage: python3 tools/voice_bands.py [--json OUT]

V0 BANDS: the 17 chords (the 16 drawn things + the plant «zog») made by genome/voice.py, each run through the
sealed E52 front exactly as the ear door runs a wav (16-bit PCM, /32768, cochlea.analyse at 16 kHz), the FIRST
event's trait read as the float32 the tape carries. Prints: events per chord; the 17 × 17 cosine matrix of the
traits; between-word p5/median/p95/max over the 136 pairs; within-word p5 (the maker adds NO noise: every showing
of a name is the SAME samples, so within = 1.0 by construction — measured anyway, the chord made twice); the
±4 % pitch-shifted chords' cosines to their originals (V1b, held out, printed) and to every OTHER original.

THE DECISION RULE (written in the brief before this ran): if between-p95 >= within-p5 the rung is REFUSED at its
ceiling — raised with the matrix; the chord design changes only with the orchestrator's word, never a bar.
Otherwise THETA_SOUND is a number STRICTLY between between-p95 and within-p5; this tool proposes the midpoint of
(between-MAX, within-p5) when between-max < within-p5 (so no two names resonate one cell), else the midpoint of
(between-p95, within-p5), and prints which.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from genome import voice, world      # noqa: E402

WORDS = list(world.THINGS_11) + list(world.THINGS_ARRIVAL2) + [world.THING_PLANT]


def measure() -> dict:
    events, traits, first_t = {}, {}, {}
    for w in WORDS:
        res = voice.analyse(w)
        events[w] = len(res["events"])
        first_t[w] = [round(float(e["t_s"]), 4) for e in res["events"]]
        traits[w] = voice.trait_f32(w)
    T = np.stack([traits[w] for w in WORDS])
    C = T @ T.T
    iu = np.triu_indices(len(WORDS), k=1)
    between = C[iu]
    again = np.array([float(voice.trait_f32(w) @ traits[w]) for w in WORDS])        # the chord made a second time
    within_p5 = float(np.percentile(again, 5))
    shifted = {}
    for w in WORDS:
        row = {}
        for s in (0.96, 1.04):
            ts = voice.trait_f32(w, shift=s)
            own = float(ts @ traits[w])
            others = {u: float(ts @ traits[u]) for u in WORDS if u != w}
            best_other = max(others.items(), key=lambda kv: kv[1])
            row[str(s)] = {"own": round(own, 4), "best_other": best_other[0], "best_other_cos": round(best_other[1], 4),
                           "events": len(voice.analyse(w, shift=s)["events"])}
        shifted[w] = row
    b_p95 = float(np.percentile(between, 95)); b_max = float(between.max())
    refused = b_p95 >= within_p5
    if refused:
        theta, rule = None, "REFUSED at its ceiling: between-p95 >= within-p5"
    elif b_max < within_p5:
        theta, rule = round((b_max + within_p5) / 2.0, 3), "midpoint of (between-MAX, within-p5): no two names resonate one cell"
    else:
        theta, rule = round((b_p95 + within_p5) / 2.0, 3), "midpoint of (between-p95, within-p5): between-max >= within-p5 — some pair shares a cell"
    return {
        "words": WORDS, "formants": {w: [round(f, 1) for f in voice.formants(w)] for w in WORDS},
        "events_per_chord": events, "event_times_s": first_t,
        "cos_matrix": [[round(float(v), 4) for v in row] for row in C],
        "between": {"n": int(between.size), "p5": round(float(np.percentile(between, 5)), 4), "median": round(float(np.median(between)), 4),
                    "p95": round(b_p95, 4), "max": round(b_max, 4),
                    "max_pair": [WORDS[iu[0][int(np.argmax(between))]], WORDS[iu[1][int(np.argmax(between))]]]},
        "within": {"p5": round(within_p5, 6), "min": round(float(again.min()), 6), "note": "the maker adds no noise: within = 1.0 by construction (the chord made twice, float32 round-trip)"},
        "shifted_pm4pct": shifted, "theta_sound": theta, "rule": rule, "refused": refused,
    }


def main(argv) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    m = measure()
    print("V0 BANDS — 17 chords through the sealed E52 front (genome/voice.py -> genome/cochlea.py)")
    print("events per chord:", m["events_per_chord"])
    print("first event at (s):", {w: t[:3] for w, t in m["event_times_s"].items()})
    print("formants (Hz):", m["formants"])
    w8 = [w[:6] for w in m["words"]]
    print("cos matrix (rows/cols in order):", " ".join(f"{w:>6}" for w in w8))
    for w, row in zip(w8, m["cos_matrix"]):
        print(f"  {w:>6} " + " ".join(f"{v:6.3f}" for v in row))
    print("between:", m["between"]); print("within:", m["within"])
    for w, row in m["shifted_pm4pct"].items():
        print(f"  shifted {w:>8}: 0.96 own {row['0.96']['own']:.4f} (best other {row['0.96']['best_other']} {row['0.96']['best_other_cos']:.4f}) · "
              f"1.04 own {row['1.04']['own']:.4f} (best other {row['1.04']['best_other']} {row['1.04']['best_other_cos']:.4f})")
    print("THETA_SOUND:", m["theta_sound"], "—", m["rule"])
    if a.json:
        Path(a.json).write_text(json.dumps(m, indent=1))
        print("wrote", a.json)
    return 2 if m["refused"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
