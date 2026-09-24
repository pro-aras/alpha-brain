#!/usr/bin/env python3
# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:13 +0400 — A4-LADDER-PREREG §2.2 A3/task 5:
# the one-off read-twin tool. Run by the ORCHESTRATOR on alpha4-1's CLOSED final snapshot after 05:00 (never by
# this builder on the live life -- READ-ONLY like every root under genome-lives, never touched here). Both laws
# on ONE snapshot, no replay: zog (the plant, ask_plant_glances), vex (the null plant), spiral (Q5, via
# ask_glances), and Q1 on seen words -- the read-side `majority` override (genome/questions.py, genome/machinery.py
# Organism.recall_many) makes this a single load + two passes, exactly as self_exam.py's own sitter (task 3).
"""usage: python3 tools/answer_readtwin.py --snapshot <run-root-or-snapshot-copy> --genome <genome-path> [--held 10]

Prints, under BOTH the genome's own law and the old (majority-off) law, on the SAME snapshot:
  - zog   (world.THING_PLANT): ask_plant_glances -- answered_rate, graded distribution
  - vex   (world.THING_NULL):  ask_plant_glances -- answered_rate, graded distribution (A1's reader-side vex)
  - spiral(world.THING_NEVER): the Q5 entry from a full ask_glances pass -- graded distribution
  - Q1 on seen words: acc, hedge_rate
Asserts the organism's own state_hash is unchanged by every read (recall_many never mutates)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from genome import world, run_g1                                    # noqa: E402
from genome.questions import ask_glances, ask_plant_glances         # noqa: E402
from tools.self_exam import load_snapshot                           # noqa: E402


def read_both_laws(root: Path, genome_path: Path, held_n: int = 10) -> dict:
    g, org, ledgers, L = load_snapshot(root, genome_path)
    h0 = org.state_hash()
    majority_declared = bool(g.declared.get("ANSWER", {}).get("majority"))
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL],
                                held_n, np.random.default_rng(2))
    held_g = run_g1.glance_held(held, g, "surprise")
    feats = run_g1.feats_only(held_g)
    never = {world.THING_NEVER: feats[world.THING_NEVER]}
    words_seen = sorted({w for s in ledgers["words"].values() for w in s})
    seen_things = [t for t in things if t in words_seen]
    fallback = len(seen_things) < 2
    things_for_q1 = things if fallback else seen_things

    out = {"snapshot": str(root), "genome": str(genome_path), "answer_majority_declared": majority_declared,
          "moments": org.t, "cells": [int(org.sight.alive.sum()), int(org.words.alive.sum())],
          "words_seen_n": len(words_seen), "hash_before": h0}
    for law_name, majority in (("new_law", None), ("old_law", False)):
        zog = ask_plant_glances(org, ledgers, world.THING_PLANT, feats[world.THING_PLANT], majority=majority)
        vex = ask_plant_glances(org, ledgers, world.THING_NULL, feats[world.THING_NULL], majority=majority)
        ask = ask_glances(org, ledgers, things_for_q1, feats, never, g.ear_blank_zero, majority=majority)
        out[law_name] = {
            "zog": {"answered_rate": zog["answered_rate"], "graded": zog["graded"], "n": zog["n"]},
            "vex": {"answered_rate": vex["answered_rate"], "graded": vex["graded"], "n": vex["n"]},
            "spiral": ask["Q5"].get(world.THING_NEVER, {}),
            "Q1": {"acc": ask["Q1"]["acc"], "hedge_rate": ask["Q1"]["hedge_rate"], "n": ask["Q1"]["n"]},
        }
    h1 = org.state_hash()
    out["hash_after"] = h1
    out["organism_unchanged"] = (h0 == h1)
    return out


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True, help="a run root or a copy of one (must carry state/organism.npz + state/ledger.json)")
    ap.add_argument("--genome", required=True)
    ap.add_argument("--held", type=int, default=10)
    a = ap.parse_args(argv)
    root = Path(a.snapshot)
    out = read_both_laws(root, Path(a.genome), held_n=a.held)
    print(json.dumps(out, indent=1, default=str))
    if not out["organism_unchanged"]:
        print("REFUSED: the organism's own hash moved across these reads -- recall_many must never mutate; RAISED, not silently accepted", file=sys.stderr)
        return 1
    if not out["answer_majority_declared"]:
        print("NOTE: this genome does not declare ANSWER's majority clause -- old_law == new_law by construction (both passes are identical, printed anyway for the schema's sake)")
    zn, zo = out["new_law"]["zog"]["answered_rate"], out["old_law"]["zog"]["answered_rate"]
    print(f"\nA3 headline: zog answered_rate new={zn:.2f} old={zo:.2f} " +
          ("-- FAIL: the majority law costs the plant its name (old>=0.6, new<0.6)" if (zo >= 0.6 and zn < 0.6) else "-- PASS or not gradable, see the numbers above"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
