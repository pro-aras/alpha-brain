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
    ledgers = {"sight": {int(k): set(v) for k, v in L["sight"].items()}, "words": {int(k): set(v) for k, v in L["words"].items()},
               # A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:39 +0400): the SOUND ledger (absent -> empty)
               "sound": {int(k): set(v) for k, v in (L.get("sound") or {}).items()}}
    return g, org, ledgers, L


def voiced_counts(root: Path) -> dict:
    """A4L-VOICE: the maker's sound rows on the tape, per word (the «voiced ≥ 5 times» gradability rule of V1/V2/V5)."""
    counts: dict = {}
    for f in sorted((root / "tape").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if '"ear-sound"' not in line:
                continue
            r = json.loads(line)
            m = r.get("meta") or {}
            if r.get("sense") == "ear-sound" and m.get("source") == "maker" and m.get("word"):
                counts[m["word"]] = counts.get(m["word"], 0) + 1
    return counts


def sound_exam(org, ledgers, things, feats, voiced=None) -> dict:
    """A4L-VOICE task 4: ask_sound on the snapshot — the chords are genome/voice.py's (the bytes the maker publishes), the
    renders the exam's own held-out ones (seed 2), the ±4 % shifted chords printed (V1b). None when there is no sound area."""
    if getattr(org, "sound", None) is None:
        return None
    from genome import voice as _voice
    from genome.questions import ask_sound as _ask_sound
    chords = {t: _voice.trait_f32(t) for t in things}
    shifted = {t: {s: _voice.trait_f32(t, shift=float(s)) for s in ("0.96", "1.04")} for t in things}
    return {"chords_from": "genome/voice.py formant (sha256(word) -> F1/F2/F3), the sealed E52 front's FIRST event",
            **_ask_sound(org, ledgers, things, {t: feats[t] for t in things if t in feats}, chords, shifted, voiced=voiced)}


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


# edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:43 +0400 — ALPHA4-PREREG §4(b) AMENDED (§11 finding 1): the read
# proxy tested heard[-N:] — the N NEWEST, least-exposed words the shelf had read (≥ 0.6 in 2 of alpha4-1's 23 sittings,
# never two in a row). It is now a FIXED-SEED sample over ALL of read/HEARD.json. The sitter (creature/exam.py) passes
# «--read-words 50 --read-seed 20260923»; the default seed is the same, so the tool run alone reads what the sitter reads.
READ_SEED_DEFAULT = 20260923


def read_sample(heard, n: int, seed: int = READ_SEED_DEFAULT) -> list:
    """n words drawn WITHOUT replacement, uniformly over ALL the heard words (first-heard order, distinct — creature/senses/
    read.py:heard_words), by numpy's PCG64 seeded with `seed`, returned in first-heard order. Deterministic for a given
    heard list and seed; the oldest words are as likely as the newest. Fewer than n heard -> [] (the share then reads None
    and the judge's (b) fails closed — a proxy on fewer words than its own n is not the proxy)."""
    heard = list(heard)
    n = int(n)
    if n <= 0 or len(heard) < n:
        return []
    idx = np.random.default_rng(int(seed)).choice(len(heard), size=n, replace=False)
    return [heard[i] for i in sorted(int(i) for i in idx)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--genome", default=str(ROOT / "genome" / "G4-skeleton.genome"))
    ap.add_argument("--held", type=int, default=run_g1.HELD_N if hasattr(run_g1, "HELD_N") else 10)
    ap.add_argument("--check-tape", type=int, default=400)
    ap.add_argument("--read-words", type=int, default=0, help="ALPHA4 §4(b): render a fixed-seed sample of N of ALL the words the shelf reader HEARD (read/HEARD.json) in the held-out font and report read_share (None when fewer than N heard)")
    ap.add_argument("--read-seed", type=int, default=READ_SEED_DEFAULT, help="the --read-words sample's seed (the sitter passes 20260923, the default)")
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
    # A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:39 +0400): the exam by SOUND (V1/V2/V5/V1b) on the
    # 16 drawn things — None (the key still written, #164) on a genome with no sound area; sat AFTER hash_before, so the
    # exam's own `organism_hash_unchanged_by_exam` covers it.
    ask_sound_out = sound_exam(org, ledgers, things + arr2, feats, voiced=voiced_counts(root)) if getattr(org, "sound", None) is not None else None
    # edit: Claude (Fable 5.1), 2026-09-23 03:02 +0400 — ALPHA4 §4(b): the reading share as a TAPE FACT. The sitter (off the mind
    # thread, on the snapshot) renders N HEARD shelf words in the HELD-OUT font (tools/read_recognised.py, builder
    # H's own mark instrument) and reports the share; the SIT row forwards it and the judge reads the row.
    # (Opus 5.5, 2026-09-23 11:43 +0400: the N are `read_sample`'s fixed-seed draw over ALL heard words, no longer the last N.)
    read_share, read_words_n, read_words_list = None, int(getattr(a, "read_words", 0) or 0), []
    read_seed, read_heard_n = int(getattr(a, "read_seed", READ_SEED_DEFAULT)), None
    if read_words_n > 0:
        try:
            from creature.senses.read import heard_words as _heard_words
            from tools.read_recognised import recognised_share as _recognised_share
            heard = _heard_words(root)
            read_heard_n = len(heard)
            read_words_list = read_sample(heard, read_words_n, read_seed)     # AMENDED 2026-09-23: was heard[-read_words_n:]
            if read_words_list:
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
        "ask_sound": ask_sound_out,
        "read_share": read_share, "read_words_n": read_words_n, "read_words": read_words_list,
        "read_seed": read_seed, "read_heard_n": read_heard_n,        # the sample's own numbers beside the share (#164)
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
