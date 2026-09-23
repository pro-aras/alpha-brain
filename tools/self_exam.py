#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-19 21:30 +0400 — THE SELF-EXAM INSTRUMENT (docs/G4-PREREG.md §5): reads the creature's latest snapshot
# (run/state/organism.npz + ledger.json — PREREG 2.7) and sits the nine marks' question set on held-out DRAWN canvases (seed 2,
# as G1; disjoint by pixels from the last N tape payloads) with the key OUTSIDE him. Writes run/exam/<stamp>.json. Read-only on the
# creature: it never writes under run/state, run/journal or run/tape. The orchestrator's own instrument (#214); the creature's own
# exam duty (wave 2) calls the same functions so the two readings can be compared.
"""usage: python3 tools/self_exam.py --root /data/dev/genome/run [--genome genome/G4-skeleton.genome] [--held 10] [--check-tape 400]"""
from __future__ import annotations

import argparse, io, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from genome.machinery import Organism, parse_genome          # noqa: E402
from genome import world, run_g1                              # noqa: E402
from genome.questions import ask_glances                      # noqa: E402


def load_snapshot(root: Path, genome_path: Path):
    g = parse_genome(genome_path.read_text())
    org = Organism.load(root / "state" / "organism", g)
    L = json.loads((root / "state" / "ledger.json").read_text())
    ledgers = {"sight": {int(k): set(v) for k, v in L["sight"].items()}, "words": {int(k): set(v) for k, v in L["words"].items()}}
    return g, org, ledgers, L


def tape_canvases(root: Path, n: int):
    """The last n eye payloads on the tape, decoded — the disjointness control's other side."""
    from PIL import Image
    rows = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            if r.get("sense") == "eye":
                rows.append(r)
    out = []
    for r in rows[-n:]:
        p = root / "tape" / r["payload"]
        if p.exists():
            out.append(("?", np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8), {}))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--genome", default=str(ROOT / "genome" / "G4-skeleton.genome"))
    ap.add_argument("--held", type=int, default=run_g1.HELD_N if hasattr(run_g1, "HELD_N") else 10)
    ap.add_argument("--check-tape", type=int, default=400)
    ap.add_argument("--read-words", type=int, default=0, help="ALPHA4: render the last N words the shelf reader HEARD (read/HEARD.json) in the held-out font and report read_share (None when fewer than N heard)")
    a = ap.parse_args()
    root = Path(a.root)
    t0 = time.perf_counter()
    g, org, ledgers, L = load_snapshot(root, Path(a.genome))
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], a.held, np.random.default_rng(2))
    seen = tape_canvases(root, a.check_tape)
    disjoint_checked = world.assert_disjoint_canvas(seen, held) if seen else 0
    # the control of the control: a planted copy of a held-out canvas among the seen ones must be CAUGHT
    caught = False
    if held[things[0]]:
        try:
            world.assert_disjoint_canvas(seen + [(things[0], held[things[0]][0][0].copy(), {})], held)
        except AssertionError:
            caught = True
    held_g = run_g1.glance_held(held, g, "surprise")
    feats = run_g1.feats_only(held_g)
    never = {world.THING_NEVER: feats[world.THING_NEVER]}
    words_seen = sorted({w for s in ledgers["words"].values() for w in s})
    # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — the seen-words exam needs two things (a distractor); with fewer than two seen it is sat
    # on ALL things and says so (`seen_words_fallback_to_all`, written True/False on every exam — #164). Before: one seen word divided by zero
    # in ask_glances (the frozen-10 twin on the game tapes, 2026-09-22 00:45 +04 — (iii) read None on g5-seam-1 and L5).
    seen_things = [t for t in things if t in words_seen]
    fallback = len(seen_things) < 2
    ask = ask_glances(org, ledgers, things if fallback else seen_things, feats, never, g.ear_blank_zero)
    ask_all = ask_glances(org, ledgers, things + arr2, feats, never, g.ear_blank_zero)
    # edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:12 +0400 — A4-LADDER-PREREG §2.2 task 3:
    # THE SITTER SITS BOTH LAWS — but only when this genome's ANSWER line actually declares the majority
    # clause (`recall_many`'s own gate would otherwise never fire, so an "old law" pass would be BYTE-
    # IDENTICAL to the new one — a wasted second full ask_glances pass on every OTHER rung's and alpha4-1's
    # own exam duty, which all share this module via creature/exam.py:run_exam). Undeclared: both keys are
    # still written (#164 — a stable schema every reader can rely on) as None, with the reason on the
    # sibling `*_old_law_note` field, never silently omitted.
    seen_for_ceiling = things if fallback else seen_things
    answer_majority_declared = bool(g.declared.get("ANSWER", {}).get("majority"))
    ask_old, ask_all_old, lit_counts_seen, old_law_note = None, None, None, None
    if answer_majority_declared:
        ask_old = ask_glances(org, ledgers, things if fallback else seen_things, feats, never, g.ear_blank_zero, majority=False)
        ask_all_old = ask_glances(org, ledgers, things + arr2, feats, never, g.ear_blank_zero, majority=False)
        # A2's own per-exam ceiling (task 0/5): the lit-glance distribution over the SAME seen canvases Q1
        # was just read on — forced ON (majority=True) so it reads the count regardless of the genome's own
        # law (moot here, since the clause IS declared, but keeps this loop's meaning independent of `ask`'s).
        lit_counts_seen = {}
        for t in seen_for_ceiling:
            for xs in feats.get(t, []):
                r = org.recall_many("sight", xs, majority=True)
                n_lit = r.get("lit_n")
                if n_lit is not None:
                    lit_counts_seen[n_lit] = lit_counts_seen.get(n_lit, 0) + 1
    else:
        old_law_note = "ANSWER's majority clause is not declared on this genome — old law == new law by construction, not sat twice"
    landing = run_g1.landing(held_g, things, first=2)
    hash_before = L.get("state_hash") or org.state_hash()
    # edit: Claude (Fable 5.1), 2026-09-23 03:02 +0400 — ALPHA4 §4(b): the reading share as a TAPE FACT. The sitter (off the mind
    # thread, on the snapshot) renders the last N HEARD shelf words in the HELD-OUT font (tools/read_recognised.py, builder
    # H's own mark instrument) and reports the share; the SIT row forwards it and the judge reads the row.
    read_share, read_words_n, read_words_list = None, int(getattr(a, "read_words", 0) or 0), []
    if read_words_n > 0:
        try:
            from creature.senses.read import heard_words as _heard_words
            from tools.read_recognised import recognised_share as _recognised_share
            heard = _heard_words(root)
            if len(heard) >= read_words_n:
                read_words_list = heard[-read_words_n:]
                rs = _recognised_share(root, Path(a.genome), read_words_list)
                read_share = float(rs.get("share")) if isinstance(rs, dict) and rs.get("share") is not None else None
        except Exception as e:   # a sitter never crashes the voice thread: the field reads None, the reason printed
            print("read_share: not computed:", repr(e))
            read_share = None
    out = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "genome": str(a.genome), "snapshot_last_seq": L.get("last_seq"),
        "moments": org.t, "cells": [int(org.sight.alive.sum()), int(org.words.alive.sum())], "words_seen": words_seen,
        "held_per_thing": a.held, "chance_q1": round(1.0 / max(1, len(things) if fallback else len(words_seen or things)), 3),
        "seen_words_fallback_to_all": fallback,
        "disjoint_checked": disjoint_checked, "disjoint_control_caught": caught,
        "ask_seen_words": ask, "ask_all_words": ask_all, "gaze_landing": landing,
        # A4-LADDER-PREREG §2.2 task 3 — both laws, one snapshot, no replay; None + a note when the clause
        # is not declared on this genome (#164: the key is always present).
        "ask_seen_words_old_law": ask_old, "ask_all_words_old_law": ask_all_old,
        "lit_counts_seen": lit_counts_seen, "answer_majority_declared": answer_majority_declared, "old_law_note": old_law_note,
        "read_share": read_share, "read_words_n": read_words_n, "read_words": read_words_list,
        "organism_hash_unchanged_by_exam": org.state_hash() == hash_before, "seconds": round(time.perf_counter() - t0, 1),
    }
    (root / "exam").mkdir(exist_ok=True)
    p = root / "exam" / (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ") + ".json")
    p.write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("moments", "cells", "words_seen", "chance_q1", "disjoint_checked", "disjoint_control_caught",
                                          "organism_hash_unchanged_by_exam", "seconds")}, default=str))
    q = ask.get("q1") or ask.get("Q1") or {k: v for k, v in ask.items() if k.startswith("q1")}
    print("Q1:", json.dumps(q, default=str)[:300]); print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
