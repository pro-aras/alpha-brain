"""machinery.py — the ribosome: reads a genome text and runs an organism by it.

edit: Claude (Fable 5.1), 2026-09-19 19:33 +0400 — G3 (docs/G3-LAWS-PREREG.md): RESONATE sight nearest words cos>=T (a per-area threshold; the sight floor is THETA_N written by the gate as between-p5), ABSTAIN margin cos<M (reason «close»); absent genes = the old law, pinned.
edit: Claude (Fable 5.1), 2026-09-19 18:10 +0400 — G2: the tower step asserts the tower's OWN input side (64 for the photograph eye).
edit: Claude (Fable 5.1), 2026-09-19 16:0x +04 — G0 rung 0 (docs/G0-PREREG.md §1, §10).
edit: Claude (Fable 5.1), 2026-09-19 16:09 +04 — §11: the retina as a list of fixed steps (gate G-a's finding); winners must resonate.
edit: Claude (Fable 5.1), 2026-09-19 16:37 +04 — G0b: RETINA step tower:<sealed eye>; any square picture; every edge's birth and pruning logged by cell ids (no labels).
edit: Claude (Fable 5.1), 2026-09-19 17:21 +0400 — G1: the GAZE gene (parsed; its work is done in gaze.py and the runner); recall_many/edge_many — the rung-0 recall summed over glances, pinned equal to recall/edge for one glance; save/load for the ask door (never touch state_hash).
edit: Claude (Fable 5.1), 2026-09-19 16:14 +04 — §11 amendments 4–6 (from the toy): redundant error births refused; ABSTAIN's second is a competitor that answers back differently; a question lights the resonating winners, not one cell.
edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B1 (docs/G4-PREREG.md §3): a `declared: Dict[str, dict]`
field on Genome holding every G4 gene's own parsed sub-dict (BODY, TAPE, HEART, CRASH, TRAITS, SURPRISE, CYCLE, FAST,
SLEEP, PREDICT, FILE, CURIOSITY, PARK, INDUCE, DEDUCE, BELIEF, SENTENCE, WORLD, HANDS, ASK); `AREA episodes from fast`
allowed beside sight/words; `RECALL k=N` for any N >= 1 (k=1 byte-identical — the rung-0 restriction lifted). A gene
the machinery cannot run is still a GenomeError; a placeholder value (THETA_N/THETA_M unwritten) still refuses.
edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:07 +0400 — B2 `Organism.moment_sight`; B6 `moment(x_s, x_w,
lr_scale=1.0)` now returns `(S, T)` (was None) and threads `lr_scale` into `_delta`'s lr (default 1.0 is exact,
`x*1.0==x`, so the pin is untouched) for genome/predict.py's Predictor.

Laws of this file:
- The genome is text. A gene this machinery does not know REFUSES to start (GenomeError),
  never silently ignored. A gene whose value is still a placeholder (THETA_N / THETA_M
  before gate G-a) refuses too.
- The organism holds cells (fixed prototypes), one shared edge matrix between the two
  areas, and counters. It holds NO label of any kind: the birth log carries only
  (moment, area, cell, reason). The truth lives in the runner's ledger, never here.
- Nothing is removed for disuse. Removal happens only by PRUNE (an edge that stayed under
  the floor for 3 chances) and MERGE (two alike cells with the same answer).
- No randomness inside a life: every step is a deterministic function of the genome and
  the stream, so two lives from the same genome + stream are byte-identical (mark vii).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


class GenomeError(Exception):
    """A gene the machinery cannot run. The organism does not start."""


# ============================================================================ the genome
@dataclass
class Genome:
    seed: int
    eye: Tuple[int, int]            # 24×24
    ear_letters: int                # 8
    ear_blank_zero: bool            # §10 clause 9: False = 27 symbols, True = 26 (blank is zero)
    retina: Tuple[str, ...]         # the fixed front's steps, e.g. ('thresh0.25','centre','blur0.8','pool3','hog8','hogcells8x6','unit')
    areas: Dict[str, str]           # area -> sense
    meet: Tuple[str, str]           # ('sight', 'words')
    theta_n: float                  # BIRTH novelty cos<THETA_N
    misfires: int                   # BIRTH error misfires N
    budget: int                     # BUDGET per arrival
    nmax: int
    kwta: int
    hebb_window: int
    lr: float
    prune_floor: float
    prune_chances: int
    theta_m: float
    scale_every: int
    stages: List[Tuple[int, str, int, Optional[int]]]   # (index, name, from, to)
    recall_k: int
    abstain_ratio: float
    resonate: str = "threshold"                     # G3: "nearest" — sight winners = nearest KWTA at or above the FLOOR (theta_n)
    theta_words: Optional[float] = None             # G3: the words area's own threshold (None = theta_n, the old law)
    abstain_margin: Optional[float] = None          # G3: ABSTAIN margin cos<M (None = off)
    gaze: Optional[Dict[str, object]] = None     # G1: GAZE surprise fixations F grid G canvas C glance L ink contrast (None = off)
    # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:0x +0400 — G-G/EAR.md §4: SENSE ear-sound wav <rate>
    # mono (None = off). A Genome FIELD, like `gaze`, NEVER a `declared[...]` key — it is read by
    # creature/senses/ear.py directly off the parsed Genome, so it is never subject to genes.py's
    # `unwired()` refusal (the same reason SENSE eye/SENSE ear are plain fields, not declared entries).
    ear_sound: Optional[Dict[str, object]] = None
    # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:07 +0400 — G-EYE-3 as measured (Researcher G, §3.6):
    # SENSE colour rg by 4x4 under the glance fixed-gain. Parsed directly onto the Genome (like `eye`/`ear_letters`
    # above), NEVER into `declared` — colour is a core sense dimension, not a G4-wave "declared gene" subject to
    # creature/genes.py's unwired() refusal law. None (undeclared) is a complete no-op: sight_dim() below is
    # untouched, gaze.glances() below never computes or appends anything — parity with every existing pin.
    colour: Optional[Dict[str, object]] = None
    declared: Dict[str, dict] = field(default_factory=dict)   # G4 §3 B1: every G4 gene's own parsed sub-dict (BODY, TAPE, HEART, …)
    text: str = field(default="", repr=False)

    @property
    def stage2_start(self) -> int:
        for _, name, a, _b in self.stages:
            if name == "meet":
                return a
        raise GenomeError("no STAGE named meet")

    def sight_dim(self) -> int:
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:07 +0400 — +32 when SENSE colour is declared
        # (G-EYE-3/§3.6: rg + by, 4x4 cells each, 16+16=32 numbers) appended BESIDE the tower's 112 (or
        # whatever the RETINA line otherwise sizes to). Undeclared (colour is None, the default): unchanged.
        d = retina_dim(self.retina, self.eye[0])
        return d + 32 if self.colour is not None else d

    def words_dim(self) -> int:
        return self.ear_letters * (26 if self.ear_blank_zero else 27)


_NUM = r"[-+]?\d+(?:\.\d+)?"


def parse_genome(text: str) -> Genome:
    """Parse the genome text. Unknown gene → GenomeError. Placeholder value → GenomeError."""
    g: Dict[str, object] = {"areas": {}, "stages": [], "ear_blank_zero": False, "declared": {}}
    seen = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        toks = line.split()
        gene, args = toks[0], toks[1:]
        a = " ".join(args)
        try:
            if gene == "SEED":
                g["seed"] = int(args[0])
            elif gene == "SENSE" and args[0] == "eye":
                m = re.fullmatch(r"(\d+)x(\d+) grey", a[4:].strip())
                if not m: raise GenomeError(f"SENSE eye: cannot read {a!r}")
                g["eye"] = (int(m.group(1)), int(m.group(2)))
            elif gene == "SENSE" and args[0] == "ear":
                m = re.fullmatch(r"letters (\d+)(?: blank=(zero|symbol))?", a[4:].strip())
                if not m: raise GenomeError(f"SENSE ear: cannot read {a!r}")
                g["ear_letters"] = int(m.group(1))
                g["ear_blank_zero"] = (m.group(2) == "zero")
            # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:0x +0400 — EAR.md §4: `SENSE ear-sound wav
            # <rate> mono` — a NEW alternative under the existing "SENSE" gene, dispatched on args[0] exactly
            # as "eye"/"ear" are (additive: those two branches are untouched byte-for-byte). Stored as the
            # Genome field `ear_sound` (never `declared[...]` — see the field's own comment above), so it is
            # never subject to genes.py's `unwired()` refusal.
            elif gene == "SENSE" and args[0] == "ear-sound":
                m = re.fullmatch(r"wav (\d+) mono", a[len("ear-sound "):].strip())
                if not m: raise GenomeError(f"SENSE ear-sound: cannot read {a!r} (EAR.md §4: SENSE ear-sound wav <rate> mono)")
                g["ear_sound"] = {"rate": int(m.group(1)), "channels": "mono"}
            elif gene == "SENSE" and args[0] == "colour":
                # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:07 +0400 — G-EYE-3/§3.6: SENSE colour rg
                # by 4x4 under the glance fixed-gain. New vocabulary; a strict fullmatch on the literal decided
                # form (Researcher G measured "fixed-gain" as the form that does not amplify a legitimately-zero
                # block's noise, #231(1) — "block-unit" is not accepted here, on purpose).
                m = re.fullmatch(r"rg by 4x4 under the glance fixed-gain", a[7:].strip())
                if not m: raise GenomeError(f"SENSE colour: cannot read {a!r} (§3.6: SENSE colour rg by 4x4 under the glance fixed-gain)")
                g["colour"] = {"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"}
            elif gene == "RETINA":
                for step in args:
                    if not re.fullmatch(r"thresh" + _NUM + r"|centre|blur" + _NUM + r"|pool\d+|hog\d+|hogcells\d+x\d+|tower:[A-Za-z0-9_.-]+|sqrt|unit", step):
                        raise GenomeError(f"RETINA: unknown fixed step {step!r} in {a!r}")
                if args[-1] != "unit": raise GenomeError("RETINA: the last step must be unit")
                g["retina"] = tuple(args)
            elif gene == "AREA":
                if len(args) != 3 or args[1] != "from": raise GenomeError(f"AREA: cannot read {a!r}")
                g["areas"][args[0]] = args[2]
            elif gene == "MEET":
                if len(args) != 2: raise GenomeError(f"MEET: cannot read {a!r}")
                g["meet"] = (args[0], args[1])
            elif gene == "BIRTH" and args[0] == "novelty":
                m = re.fullmatch(r"cos<(" + _NUM + ")", args[1])
                if not m: raise GenomeError(f"BIRTH novelty: THETA_N not set (gate G-a writes it): {a!r}")
                g["theta_n"] = float(m.group(1))
            elif gene == "BIRTH" and args[0] == "error":
                if args[1] != "misfires": raise GenomeError(f"BIRTH error: cannot read {a!r}")
                g["misfires"] = int(args[2])
            elif gene == "BUDGET":
                if args[1:] != ["per", "arrival"]: raise GenomeError(f"BUDGET: cannot read {a!r}")
                g["budget"] = int(args[0])
            elif gene == "NMAX":
                g["nmax"] = int(args[0])
            elif gene == "KWTA":
                g["kwta"] = int(args[0])
            elif gene == "HEBB":
                if args[0] != "window": raise GenomeError(f"HEBB: cannot read {a!r}")
                g["hebb_window"] = int(args[1])
            elif gene == "DELTA":
                if args[0] != "lr": raise GenomeError(f"DELTA: cannot read {a!r}")
                g["lr"] = float(args[1])
            elif gene == "PRUNE":
                m = re.fullmatch(r"w<(" + _NUM + r") after (\d+) chances", a)
                if not m: raise GenomeError(f"PRUNE: cannot read {a!r}")
                g["prune_floor"], g["prune_chances"] = float(m.group(1)), int(m.group(2))
            elif gene == "MERGE":
                m = re.fullmatch(r"cos>(" + _NUM + r") same-answer", a)
                if not m: raise GenomeError(f"MERGE: THETA_M not set (gate G-a writes it): {a!r}")
                g["theta_m"] = float(m.group(1))
            elif gene == "SCALE":
                m = re.fullmatch(r"every (\d+) moments", a)
                if not m: raise GenomeError(f"SCALE: cannot read {a!r}")
                g["scale_every"] = int(m.group(1))
            elif gene == "STAGE":
                m = re.fullmatch(r"(\d+) (\w+) moments (\d+)\.\.(\d*)", a)
                if not m: raise GenomeError(f"STAGE: cannot read {a!r}")
                g["stages"].append((int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)) if m.group(4) else None))
            elif gene == "RECALL":
                m = re.fullmatch(r"k=(\d+)", a)
                if not m: raise GenomeError(f"RECALL: cannot read {a!r}")
                g["recall_k"] = int(m.group(1))
            elif gene == "ABSTAIN":
                m = re.fullmatch(r"second/best > (" + _NUM + ")", a)
                m2 = re.fullmatch(r"margin cos<(" + _NUM + ")", a)
                if m: g["abstain_ratio"] = float(m.group(1))
                elif m2: g["abstain_margin"] = float(m2.group(1))
                elif re.fullmatch(r"margin cos<MARGIN", a): raise GenomeError("ABSTAIN margin: MARGIN not set (gate G-a writes it)")
                else: raise GenomeError(f"ABSTAIN: cannot read {a!r}")
            elif gene == "RESONATE":
                m = re.fullmatch(r"sight nearest words cos>=(" + _NUM + ")", a)
                if not m: raise GenomeError(f"RESONATE: cannot read {a!r} (G3 §1: sight nearest words cos>=T)")
                g["resonate"] = "nearest"; g["theta_words"] = float(m.group(1))
            elif gene == "GAZE":
                m = re.fullmatch(r"surprise fixations (\d+) grid (\d+) canvas (\d+) glance (\d+) ink (contrast|border)", a)
                if not m: raise GenomeError(f"GAZE: cannot read {a!r} (G1 §1: surprise fixations F grid G canvas C glance L ink contrast)")
                g["gaze"] = {"fixations": int(m.group(1)), "grid": int(m.group(2)), "canvas": int(m.group(3)), "glance": int(m.group(4)), "ink": m.group(5)}
            elif gene == "BIND":
                # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:07 +0400 — G-EYE-2 (= G-MIND-2): one canvas
                # = one moment. New vocabulary; stored in `declared` (unlike SENSE eye/ear/colour above) because
                # BIND names a real MIND-side mechanism with a real call site (creature/mind.py's _consume_eye
                # pooling branch) that creature/genes.py's RUNS/unwired() law must name, exactly like every other
                # G4-wave declared gene — an undeclared BIND leaves every existing pin (today's per-glance moments)
                # untouched.
                m = re.fullmatch(r"glances per canvas", a)
                if not m: raise GenomeError(f"BIND: cannot read {a!r} (G-EYE-2: BIND glances per canvas)")
                g["declared"]["BIND"] = {"pool": "glances per canvas"}
            # ======================================================================== G4 §3 B1: the new genes.
            # Each is a strict re.fullmatch (a placeholder or a missing number refuses); the parsed sub-dict is
            # stored under g["declared"][GENE] — a gene the machinery cannot run is a GenomeError, so nobody can
            # "declare" a mechanism into existence (docs/G4-DESIGN.md §3). None of these are in `required`.
            elif gene == "BODY":
                m = re.fullmatch(r"service ([a-z][a-z0-9_]*) threads ([a-z]+(?: [a-z]+)*)", a)
                if not m: raise GenomeError(f"BODY: cannot read {a!r} (G4 §2: service <name> threads <a> <b> …)")
                g["declared"]["BODY"] = {"name": m.group(1), "threads": m.group(2).split()}
            elif gene == "TAPE":
                m = re.fullmatch(r"([A-Za-z0-9_./-]+)", a)
                if not m: raise GenomeError(f"TAPE: cannot read {a!r} (G4 §2.1: TAPE <path>)")
                g["declared"]["TAPE"] = {"path": m.group(1)}
            elif gene == "HEART":
                m = re.fullmatch(r"every (\d+) s", a)
                if not m: raise GenomeError(f"HEART: cannot read {a!r} (G4 §2.5: HEART every <n> s)")
                g["declared"]["HEART"] = {"every_s": int(m.group(1))}
            elif gene == "CRASH":
                m = re.fullmatch(r"sense restart journal; mind page", a)
                if not m: raise GenomeError(f"CRASH: cannot read {a!r} (G4 §2.6: CRASH sense restart journal; mind page)")
                g["declared"]["CRASH"] = {"sense": "restart journal", "mind": "page"}
            elif gene == "TRAITS":
                m = re.fullmatch(r"contrast head (\d+) lr (" + _NUM + r") at sleep", a)
                if not m: raise GenomeError(f"TRAITS: cannot read {a!r} (row 2b: TRAITS contrast head <n> lr <f> at sleep)")
                g["declared"]["TRAITS"] = {"head": int(m.group(1)), "lr": float(m.group(2)), "when": "sleep"}
            elif gene == "SURPRISE":
                m = re.fullmatch(r"floor (" + _NUM + r")", a)
                if not m: raise GenomeError(f"SURPRISE: cannot read {a!r} (row 1c: SURPRISE floor <f>)")
                g["declared"]["SURPRISE"] = {"floor": float(m.group(1))}
            elif gene == "CYCLE":
                m = re.fullmatch(r"grow to (" + _NUM + r") nmax then consolidate", a)
                if not m: raise GenomeError(f"CYCLE: cannot read {a!r} (row 7: CYCLE grow to <f> nmax then consolidate)")
                g["declared"]["CYCLE"] = {"grow_to": float(m.group(1))}
            # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:33 +0400 — LIFE-D-ACT-SOUND.md item 3
            # (L-13): FAST accepts an optional trailing " sound" key (genome/LIFE.genome:51's own DRAFT
            # line) -- additive only, the plain "keys sight words surprise" line (no "sound") parses to
            # the exact same dict as before (test_fast_sound_key.py's own regression clause).
            elif gene == "FAST":
                m = re.fullmatch(r"episodes (\d+) keys sight words surprise( sound)?", a)
                if not m: raise GenomeError(f"FAST: cannot read {a!r} (B3/L-13: FAST episodes <n> keys sight words surprise [sound])")
                keys = ["sight", "words", "surprise"] + (["sound"] if m.group(2) else [])
                g["declared"]["FAST"] = {"episodes": int(m.group(1)), "keys": keys}
            elif gene == "SLEEP":
                m = re.fullmatch(r"every (\d+) moments replay (\d+) by surprise", a)
                if not m: raise GenomeError(f"SLEEP: cannot read {a!r} (B7: SLEEP every <n> moments replay <m> by surprise)")
                g["declared"]["SLEEP"] = {"every": int(m.group(1)), "replay": int(m.group(2))}
            elif gene == "PREDICT":
                # edit: Claude (Sonnet 5, builder E), 2026-09-21 16:58 +0400 — G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md;
                # docs/organs/MIND-MEMORY.md §4 G-MIND-3): an OPTIONAL trailing clause names which error arm PREDICT
                # computes — novelty (today's, the default when the clause is absent) | conjunctive | episodic | comparator.
                # The clause is wrapped in its own non-capturing optional group so a genome that never writes it (every
                # genome on disk today, G4.genome included) parses to the exact same three-key dict shape as before this
                # edit, plus "arm": "novelty" — byte-identical downstream, since genome/predict.py's Predictor branches
                # the "novelty" arm through the SAME lines error() ran before this change.
                m = re.fullmatch(r"next glance; error scales delta (" + _NUM + r")\.\.(" + _NUM + r"); ranks replay; grades act(?:; error (novelty|conjunctive|episodic|comparator))?", a)
                if not m: raise GenomeError(f"PREDICT: cannot read {a!r} (B6: PREDICT next glance; error scales delta <lo>..<hi>; ranks replay; grades act[; error novelty|conjunctive|episodic|comparator])")
                g["declared"]["PREDICT"] = {"delta_lo": float(m.group(1)), "delta_hi": float(m.group(2)), "arm": m.group(3) or "novelty"}
            elif gene == "FILE":
                m = re.fullmatch(r"claim route decider due", a)
                if not m: raise GenomeError(f"FILE: cannot read {a!r} (B6: FILE claim route decider due)")
                g["declared"]["FILE"] = {"fields": ["claim", "route", "decider", "due"]}
            elif gene == "CURIOSITY":
                m = re.fullmatch(r"interests (\d+) operators recombine generalize specialize bridge", a)
                if not m: raise GenomeError(f"CURIOSITY: cannot read {a!r} (row 8: CURIOSITY interests <n> operators recombine generalize specialize bridge)")
                g["declared"]["CURIOSITY"] = {"interests": int(m.group(1)), "operators": ["recombine", "generalize", "specialize", "bridge"]}
            elif gene == "PARK":
                m = re.fullmatch(r"after (\d+) identical dead-ends reopen on new-sense", a)
                if not m: raise GenomeError(f"PARK: cannot read {a!r} (B4: PARK after <n> identical dead-ends reopen on new-sense)")
                g["declared"]["PARK"] = {"after": int(m.group(1))}
            elif gene == "INDUCE":
                m = re.fullmatch(r"rule from (\d+) episodes no counter", a)
                if not m: raise GenomeError(f"INDUCE: cannot read {a!r} (row 4d: INDUCE rule from <n> episodes no counter)")
                g["declared"]["INDUCE"] = {"from_episodes": int(m.group(1))}
            elif gene == "DEDUCE":
                m = re.fullmatch(r"one step", a)
                if not m: raise GenomeError(f"DEDUCE: cannot read {a!r} (row 4d: DEDUCE one step)")
                g["declared"]["DEDUCE"] = {"steps": 1}
            elif gene == "BELIEF":
                m = re.fullmatch(r"clash opens never overwrites", a)
                if not m: raise GenomeError(f"BELIEF: cannot read {a!r} (row 4b: BELIEF clash opens never overwrites)")
                g["declared"]["BELIEF"] = {"clash": "opens", "overwrite": False}
            elif gene == "SENTENCE":
                m = re.fullmatch(r"two-word frames is near under-judge", a)
                if not m: raise GenomeError(f"SENTENCE: cannot read {a!r} (row 5b: SENTENCE two-word frames is near under-judge)")
                g["declared"]["SENTENCE"] = {"frames": ["is", "near"], "judged": True}
            elif gene == "WORLD" and (not args or args[0] != "game"):
                m = re.fullmatch(r"drawn every (\d+) s arrivals every (\d+) h; folder ([A-Za-z0-9_./-]+); web (\d+) per hour by curiosity", a)
                if not m: raise GenomeError(f"WORLD: cannot read {a!r} (row 8: WORLD drawn every <n> s arrivals every <h> h; folder <p>; web <k> per hour by curiosity)")
                g["declared"]["WORLD"] = {"drawn_every_s": int(m.group(1)), "arrival_every_h": int(m.group(2)), "folder": m.group(3), "web_per_hour": int(m.group(4))}
            # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:0x +0400 — G-G §4.1 / G5-L brief: `WORLD game
            # <id> every <n> s; seed <s>; frames pov <h>x<w> tile <t>; consequence: <text>` — a SECOND, distinct
            # shape of the WORLD gene, dispatched on args[0]=="game" so the existing "drawn ..." branch above
            # (dispatched on args[0]!="game") is untouched byte-for-byte and BOTH lines can appear in the same
            # genome text: stored under its OWN declared key `WORLD_GAME`, never overwriting `declared["WORLD"]`
            # (the drawn world's dict) in either order — creature/body.py's `_maker_args_from_declared` and
            # `_declared_folder_dir` read `declared["WORLD"]` unconditionally and must see it unchanged.
            elif gene == "WORLD" and args[0] == "game":
                m = re.fullmatch(
                    r"game ([a-z][a-z0-9-]*) every (\d+) s; seed (\d+); frames pov (\d+)x(\d+) tile (\d+); consequence: (.+)", a)
                if not m:
                    raise GenomeError(f"WORLD game: cannot read {a!r} "
                                       f"(G-G §4.1: WORLD game <id> every <n> s; seed <s>; frames pov <h>x<w> tile <t>; consequence: <text>)")
                g["declared"]["WORLD_GAME"] = {
                    "game": m.group(1), "every_s": int(m.group(2)), "seed": int(m.group(3)),
                    "pov_h": int(m.group(4)), "pov_w": int(m.group(5)), "tile": int(m.group(6)),
                    "consequence": m.group(7),
                }
            elif gene == "HANDS":
                m = re.fullmatch(r"jail ([A-Za-z0-9_./-]+)", a)
                if not m: raise GenomeError(f"HANDS: cannot read {a!r} (row 6: HANDS jail <path>)")
                g["declared"]["HANDS"] = {"jail": m.group(1)}
            elif gene == "ASK":
                m = re.fullmatch(r"what-is show is which next why", a)
                if not m: raise GenomeError(f"ASK: cannot read {a!r} (§2.7: ASK what-is show is which next why)")
                g["declared"]["ASK"] = {"verbs": ["what-is", "show", "is", "which", "next", "why"]}
            # ==================================================================== G4 §11 Wave 2 B9: THINK/EXAM/FROZEN.
            # edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — three new genes, parsed only (Wave 2 B9).
            # Interface fixed for Builder A: declared["THINK"] == {"every": int}, declared["EXAM"] == {"every": int},
            # declared["FROZEN"] == {"after": int}. None of these are in `required`; none touch self.c (the pin).
            elif gene == "THINK":
                m = re.fullmatch(r"every (\d+) canvases", a)
                if not m: raise GenomeError(f"THINK: cannot read {a!r} (§11: THINK every <n> canvases)")
                g["declared"]["THINK"] = {"every": int(m.group(1))}
            elif gene == "EXAM":
                m = re.fullmatch(r"every (\d+) canvases", a)
                if not m: raise GenomeError(f"EXAM: cannot read {a!r} (§11: EXAM every <n> canvases)")
                g["declared"]["EXAM"] = {"every": int(m.group(1))}
            elif gene == "FROZEN":
                m = re.fullmatch(r"after (\d+) cells", a)
                if not m: raise GenomeError(f"FROZEN: cannot read {a!r} (§11: FROZEN after <n> cells)")
                g["declared"]["FROZEN"] = {"after": int(m.group(1))}
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15 (Amendment 5): ARRIVAL, the creature-side rule for
            # BUDGET's "per arrival": a word the ear has never delivered opens an arrival (the mind calls
            # Organism.new_arrival(), G0b's method verbatim). Parsed here; interpreted in creature/mind.py; a genome
            # that never declares it never evaluates the branch (G1/G4-skeleton: the pin d4b5c6b8… untouched).
            elif gene == "ARRIVAL":
                m = re.fullmatch(r"never-heard word", a)
                if not m: raise GenomeError(f"ARRIVAL: cannot read {a!r} (§15: ARRIVAL never-heard word)")
                g["declared"]["ARRIVAL"] = {"rule": "never-heard word"}
            # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md,
            # MOTOR-HANDS.md §4 G-MOT-1/2/3, BODY-SENSES.md §4.1): ACT (the vocabulary), OUTCOME (an act's residual becomes
            # an episode), SIT (the exam score returns as a sense — extends EXAM), and SENSE body (a fourth SENSE shape,
            # beside eye/ear). Each a strict re.fullmatch; each stored under g["declared"][...]; each REQUIRES a RUNS entry
            # in creature/genes.py or Mind.__init__'s generic refusal (W3-0) refuses the organism by name — nobody can
            # "declare" ACT/OUTCOME/SIT/SENSE-body into existence by parsing alone.
            elif gene == "ACT":
                m = re.fullmatch(r"[a-z]+(?: [a-z]+)*", a)
                if not m: raise GenomeError(f"ACT: cannot read {a!r} (G-MOT-1: ACT <verb> [<verb> ...], lowercase words)")
                g["declared"]["ACT"] = {"verbs": a.split()}
            elif gene == "OUTCOME":
                m = re.fullmatch(r"act to episode; error grades it; ranks replay", a)
                if not m: raise GenomeError(f"OUTCOME: cannot read {a!r} (G-MOT-2: OUTCOME act to episode; error grades it; ranks replay)")
                g["declared"]["OUTCOME"] = {"fields": ["act", "expected", "got", "residual", "source"]}
            elif gene == "SIT":
                m = re.fullmatch(r"exam every (\d+) canvases; the score returns as a sense", a)
                if not m: raise GenomeError(f"SIT: cannot read {a!r} (G-MOT-3: SIT exam every <n> canvases; the score returns as a sense)")
                g["declared"]["SIT"] = {"every": int(m.group(1))}
            elif gene == "SENSE" and args[0] == "body":
                rest = " ".join(args[1:])
                m = re.fullmatch(r"every (\d+) s fields ([a-z_]+(?: [a-z_]+)*)", rest)
                if not m: raise GenomeError(f"SENSE body: cannot read {rest!r} (BODY-SENSES §4.1: SENSE body every <n> s fields <f1> <f2> …)")
                g["declared"]["SENSE_BODY"] = {"period_s": int(m.group(1)), "fields": m.group(2).split()}
            # edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-EYE-1/G-MIND-1 (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md;
            # docs/organs/G5-DESIGN.md §3/§4): the seam contract. DELIVER (the eye's promise) and MOMENT (the mind's promise) are
            # both NEW, additive gene words — two more elif branches, nothing renamed, no existing branch touched. Each is a strict
            # literal fullmatch (the design's own line is the only accepted value; there is no vocabulary yet for a second ACT or a
            # second WHERE shape, so a placeholder or an extra word refuses exactly like every other gene here). Interpreted in
            # creature/mind.py (_consume_eye) and genome/fast.py (Episodes); the four field names — where, when, act, source — and
            # the glance index are additive fields on the FAST episode row and the journal row ONLY: never on x_s/x_w, so a genome
            # that declares neither gene, or declares them beside an unmodified retina, is byte-for-byte the walking skeleton (the
            # G4-2 pin, and the parity test in tests/genome/test_deliver_moment.py, prove it — nothing here touches self.c,
            # state_hash's inputs, or any existing field).
            elif gene == "DELIVER":
                m = re.fullmatch(r"where fixation when instant act glance", a)
                if not m: raise GenomeError(f"DELIVER: cannot read {a!r} (G-EYE-1: DELIVER where fixation when instant act glance)")
                g["declared"]["DELIVER"] = {"where": "fixation", "when": "instant", "act": "glance"}
            elif gene == "MOMENT":
                m = re.fullmatch(r"keys sight words surprise where when act source", a)
                if not m: raise GenomeError(f"MOMENT: cannot read {a!r} (G-MIND-1: MOMENT keys sight words surprise where when act source)")
                g["declared"]["MOMENT"] = {"keys": ["sight", "words", "surprise", "where", "when", "act", "source"]}
            else:
                raise GenomeError(f"unknown gene {gene!r} ({line!r}) — the machinery does not know it; the organism does not start")
        except (IndexError, ValueError) as e:
            raise GenomeError(f"{gene}: cannot read {line!r}: {e}") from e
        seen.add(gene)
    required = ["seed", "eye", "ear_letters", "retina", "meet", "theta_n", "misfires", "budget", "nmax", "kwta",
                "hebb_window", "lr", "prune_floor", "theta_m", "scale_every", "recall_k", "abstain_ratio"]
    missing = [k for k in required if k not in g]
    if missing:
        raise GenomeError(f"genome lacks {missing}")
    if not {"sight", "words"} <= set(g["areas"].keys()) or set(g["areas"].keys()) - {"sight", "words", "episodes"}:
        raise GenomeError(f"needs AREA sight and AREA words (G4 §3 B1: episodes from fast is also allowed), got {sorted(g['areas'])}")
    if not g["stages"]:
        raise GenomeError("no STAGE genes")
    if g["recall_k"] < 1:
        raise GenomeError("RECALL k must be >= 1")
    return Genome(text=text, **g)  # type: ignore[arg-type]


# ============================================================================ the retina
from scipy import ndimage as _ndi


def retina_dim(spec: Tuple[str, ...], side: int = 24) -> int:
    """`side`: the eye's own SENSE side (default 24, rung 0's only value until G4 §3 B1's GAZE-fed
    32x32 eye — edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:07 +0400: pool/hogcells sizing now
    reads the genome's OWN `side` instead of a hardcoded 24, so a 32x32-eye genome's sight_dim() is
    correct. Never exercised by the pin — G4-skeleton.genome's RETINA has no pool/hogcells step (its
    only feature block is `tower:`, which was always computed correctly), so this fix touches no byte
    the pin reads; a regression test pins the old default (side=24) unchanged too."""
    d = 0
    for step in spec:
        if step.startswith("tower:"):
            from .eye import tower as _tower                     # the sealed eye (G0b gene EYE); no labels are read
            d += _tower(step[6:]).n_feat
        elif step.startswith("pool"):
            k = int(step[4:]); d += (side // k) ** 2
        elif step.startswith("hogcells"):
            k, nb = (int(v) for v in step[8:].split("x")); d += (side // k) ** 2 * nb
        elif step.startswith("hog"):
            d += int(step[3:])
    if d == 0:
        raise GenomeError("RETINA: no feature step (pool/hog/hogcells)")
    return d


def _grad(p):
    gy = np.zeros_like(p); gx = np.zeros_like(p)
    gy[1:-1, :] = (p[2:, :] - p[:-2, :]) / 2.0
    gx[:, 1:-1] = (p[:, 2:] - p[:, :-2]) / 2.0
    return gx, gy


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def retina(pic: np.ndarray, spec: Tuple[str, ...] = ("thresh0.25", "centre", "blur0.8", "pool3", "hog8", "hogcells8x6", "unit")) -> np.ndarray:
    """RETINA — a FIXED front (never learned), run step by step as the gene lists them.
    thresh<t>: ink under t is dark (a contrast floor) · centre: shift the ink's centroid to the centre,
    sub-pixel, ZERO FILL (§10 clause 14) · blur<s>: gaussian · pool<k>: k×k mean pool → (24/k)² numbers,
    unit length · hog<n>: histogram of edge orientation over the whole picture, n bins, unit length ·
    hogcells<k>x<n>: the same per k×k cell · unit: the concatenation to unit length.
    Every feature block is unit length before concatenation so no block outweighs another by scale."""
    assert pic.ndim == 2 and pic.shape[0] == pic.shape[1]
    q = pic.astype(np.float64)
    feats = []
    for step in spec:
        if step.startswith("tower:"):
            from .eye import tower as _tower
            t = _tower(step[6:])
            assert pic.shape == (t.side, t.side), f"the sealed eye tower {step[6:]} reads {t.side}×{t.side} frames (SENSE eye {t.side}x{t.side} grey)"
            frame = np.clip(np.rint(q * 255.0), 0, 255).astype(np.uint8)   # q: after the steps before it (thresh, centre)
            feats.append(_unit(t.features(frame).astype(np.float64)))
        elif step.startswith("thresh"):
            t = float(step[6:]); q = np.where(q >= t, q, 0.0)
        elif step == "centre":
            total = q.sum(); n = q.shape[0]
            if total > 0:
                ys, xs = np.mgrid[0:n, 0:n]
                cy, cx = (ys * q).sum() / total, (xs * q).sum() / total
                q = _ndi.shift(q, ((n - 1) / 2 - cy, (n - 1) / 2 - cx), order=1, mode="constant", cval=0.0)
        elif step.startswith("blur"):
            q = _ndi.gaussian_filter(q, float(step[4:]))
        elif step.startswith("pool"):
            k = int(step[4:]); n = q.shape[0] // k
            feats.append(_unit(q.reshape(n, k, n, k).mean(axis=(1, 3)).reshape(-1)))
        elif step.startswith("hogcells"):
            k, nb = (int(v) for v in step[8:].split("x")); n = q.shape[0] // k
            gx, gy = _grad(q); mag = np.hypot(gx, gy); b = ((np.arctan2(gy, gx) % np.pi) / np.pi * nb).astype(int) % nb
            out = np.zeros((n, n, nb))
            for i in range(n):
                for j in range(n):
                    sl = (slice(i * k, (i + 1) * k), slice(j * k, (j + 1) * k))
                    out[i, j] = np.bincount(b[sl].ravel(), weights=mag[sl].ravel(), minlength=nb)
            feats.append(_unit(out.reshape(-1)))
        elif step.startswith("hog"):
            nb = int(step[3:])
            gx, gy = _grad(q); mag = np.hypot(gx, gy); b = ((np.arctan2(gy, gx) % np.pi) / np.pi * nb).astype(int) % nb
            feats.append(_unit(np.bincount(b.ravel(), weights=mag.ravel(), minlength=nb)))
        elif step == "sqrt":
            # a fixed nonlinearity on the last feature block (the tower's ReLU features are ≥ 0): square root, unit length
            feats[-1] = _unit(np.sqrt(np.maximum(feats[-1], 0.0)))
        elif step == "unit":
            return _unit(np.concatenate(feats))
        else:
            raise GenomeError(f"RETINA: unknown fixed step {step!r}")
    raise GenomeError("RETINA: no unit step")


# ============================================================================ the organism
class Area:
    def __init__(self, name: str, dim: int, nmax: int):
        self.name, self.dim, self.nmax = name, dim, nmax
        self.cells = np.zeros((nmax, dim), dtype=np.float64)
        self.alive = np.zeros(nmax, dtype=np.uint8)
        self.misfires = np.zeros(nmax, dtype=np.int64)
        self.n = 0                                  # cells ever born (ids 0..n-1)
        # G4 §11 Wave 2 B12 (TRAITS): None until Organism.set_traits() binds a genome/traits.py Traits
        # instance — words area never gets one (TRAITS is a SIGHT contrast head). TRAITS undeclared ->
        # this stays None for the whole life -> cos()'s `if self.traits is None` branch below is the
        # exact two lines this class had before B12 existed -> the pin is untouched by construction.
        self.traits = None
        self._traits_cache_version = None
        self._traits_cache_n = None
        self._traits_cache_Hc = None

    def alive_ids(self) -> np.ndarray:
        return np.flatnonzero(self.alive[: self.n])

    def cos(self, x: np.ndarray) -> np.ndarray:
        """cosine of x to every cell ever born (dead cells read -1 so they never win). G4 §11 Wave 2
        B12: when `self.traits` is set (sight area only, after Organism.set_traits()), both the cell
        and the query are projected through the head's H before the cosine — cos(H·cell, H·x) — while
        `self.cells` itself stays the RAW, untouched feature (a changing head strands no cell). H·cells
        is cached and invalidated whenever the cell count changes (growth) or `traits.version` changes
        (a fresh learn() call) — never silently stale."""
        if self.traits is None:
            c = self.cells[: self.n] @ x
            c[self.alive[: self.n] == 0] = -1.0
            return c
        H = self.traits.H
        if self._traits_cache_version != self.traits.version or self._traits_cache_n != self.n or self._traits_cache_Hc is None:
            Hc = self.cells[: self.n] @ H.T
            norms = np.linalg.norm(Hc, axis=1)
            norms[norms == 0.0] = 1.0
            self._traits_cache_Hc = Hc / norms[:, None]
            self._traits_cache_version = self.traits.version
            self._traits_cache_n = self.n
        Hx = H @ x
        nx = float(np.linalg.norm(Hx))
        Hx = Hx / nx if nx > 0.0 else Hx
        c = self._traits_cache_Hc @ Hx
        c[self.alive[: self.n] == 0] = -1.0
        return c


class Organism:
    """One organism: two areas, one edge matrix, counters. Flags `grow` / `wire` exist for the
    twins T-frozen (grow off after 10 cells) and T-nowire (HEBB off) — defaults ON."""

    def __init__(self, genome: Genome, *, wire: bool = True, frozen_after: Optional[int] = None):
        self.g = genome
        self.sight = Area("sight", genome.sight_dim(), genome.nmax)
        self.words = Area("words", genome.words_dim(), genome.nmax)
        self.W = np.zeros((genome.nmax, genome.nmax), dtype=np.float64)     # sight × words
        self.mask = np.zeros((genome.nmax, genome.nmax), dtype=np.uint8)
        self.strikes = np.zeros((genome.nmax, genome.nmax), dtype=np.uint8)
        self.t = 0                                   # moments lived
        self.wire = wire
        self.frozen_after = frozen_after
        self.budget_left = genome.budget
        self.arrivals = 0
        self.c = {                                   # counters (int64 in the hash)
            "births_novelty_sight": 0, "births_novelty_words": 0, "births_error_sight": 0, "births_error_words": 0,
            "births_refused_budget": 0, "births_refused_nmax": 0, "births_refused_frozen": 0, "births_refused_redundant": 0,
            "edges_born": 0, "edges_pruned": 0, "cells_merged_sight": 0, "cells_merged_words": 0,
            "scale_events": 0, "removed_for_disuse": 0,
        }
        self.births: List[Tuple[int, str, int, str]] = []      # (moment, area, cell, reason) — nothing else
        self.merges: List[Tuple[int, str, int, int]] = []      # (moment, area, kept, dropped)
        self.edges_log: List[Tuple[int, int, int]] = []        # (moment, sight cell, word cell) — every edge born
        self.prunes_log: List[Tuple[int, int, int]] = []       # (moment, sight cell, word cell) — every edge pruned
        self.refusals_by_arrival: List[int] = []
        # G4 §3 B2: a plain attribute, NEVER a self.c key — state_hash hashes json.dumps(self.c), so a
        # new self.c key would move the pin (d4b5c6b8…) even at value 0, for every genome that never
        # calls moment_sight. Kept out of state_hash entirely; a life that DOES call moment_sight still
        # gets a different hash, but only through the sight cells/W it actually touches.
        self.moments_sight_only = 0

    # ------------------------------------------------------------------ arrivals & budget
    def new_arrival(self) -> None:
        """A new set of things arrives: the birth budget is fresh (BUDGET N per arrival)."""
        if self.arrivals > 0:
            self.refusals_by_arrival.append(self.c["births_refused_budget"] - sum(self.refusals_by_arrival))
        self.arrivals += 1
        self.budget_left = self.g.budget

    def total_cells(self) -> int:
        return int(self.sight.alive.sum() + self.words.alive.sum())

    def set_traits(self, traits) -> None:
        """G4 §11 Wave 2 B12: bind a genome/traits.py Traits instance to the sight area only (words
        never gets one — TRAITS is a visual contrast head). Never called -> self.sight.traits stays
        None -> Area.cos's untouched two-line path -> the pin (test_pin_skeleton.py) is unaffected."""
        self.sight.traits = traits

    @property
    def traits(self):
        """The coordinator's fixed interface names this `org.traits` (not `org.sight.traits`) — Builder
        A's mind code reads/writes it under that exact name. A plain `self.traits = t` attribute would
        shadow this property and silently leave `self.sight.traits` (what Area.cos actually reads) at
        None — TRAITS would then be a no-op with every other link green (#180's class). This property
        is the single source of truth; `set_traits()` above is kept as an equivalent explicit method."""
        return self.sight.traits

    @traits.setter
    def traits(self, t) -> None:
        self.sight.traits = t

    # ------------------------------------------------------------------ births
    def _birth(self, area: Area, x: np.ndarray, reason: str) -> Optional[int]:
        if self.frozen_after is not None and (self.sight.n + self.words.n) >= self.frozen_after:
            self.c["births_refused_frozen"] += 1
            return None
        if area.n >= area.nmax:
            self.c["births_refused_nmax"] += 1
            return None
        if "CYCLE" in self.g.declared:
            # G4 §3 B7: CYCLE's SOFT ceiling — refuse once ALIVE cells reach grow_to*NMAX, same counter
            # as the hard cap. This does NOT reuse ids (advisor review: reusing a dead slot's id would
            # corrupt questions.build_ledgers, which unions every id's birth history forever — a reborn
            # id would inherit a retired cell's old "born on X" facts). cycle() (genome/sleep.py) lowers
            # ALIVE count via a real merge pass, which reopens this gate with FRESH ids from here on;
            # area.n (ever-born) never decreases, so the array's real NMAX ceiling is still the only
            # hard limit, one-shot per id, exactly as it always was. A genome that never declares CYCLE
            # (G1.genome, G4-skeleton.genome — the pin) never evaluates this branch at all.
            ceiling = float(self.g.declared["CYCLE"]["grow_to"]) * self.g.nmax
            if self.total_cells() >= ceiling:
                self.c["births_refused_nmax"] += 1
                return None
        if self.budget_left <= 0:
            self.c["births_refused_budget"] += 1
            return None
        cid = area.n
        area.cells[cid] = x
        area.alive[cid] = 1
        area.n += 1
        self.budget_left -= 1
        self.c[f"births_{reason}_{area.name}"] += 1
        self.births.append((self.t, area.name, cid, reason))
        return cid

    def _theta(self, area: Area) -> float:
        """G3 §1: the words area may carry its own threshold (RESONATE … words cos>=T); sight uses THETA_N (the floor under `nearest`)."""
        return self.g.theta_words if (area is self.words and self.g.theta_words is not None) else self.g.theta_n

    def _resonate(self, area: Area, x: np.ndarray) -> List[int]:
        """BIRTH novelty + KWTA: births a cell if nothing resonates (cos < THETA_N), then returns
        the winners (top KWTA alive cells by cosine; a newborn is a winner in its birth moment)."""
        if area.n == 0 or float(area.cos(x).max()) < self._theta(area):
            self._birth(area, x, "novelty")
        if area.n == 0:
            return []
        c = area.cos(x)
        order = np.argsort(-c, kind="stable")
        # §11 clause 3: a winner must RESONATE (cos ≥ THETA_N) — up to KWTA of them; a cell that does not
        # resonate is not active and is never a delta-rule target (else the target marks every word right)
        th = self._theta(area)
        winners = [int(i) for i in order[: self.g.kwta] if area.alive[i] and c[i] >= th]
        return winners

    # ------------------------------------------------------------------ one moment
    def moment(self, x_s: np.ndarray, x_w: np.ndarray, lr_scale: float = 1.0) -> Tuple[List[int], List[int]]:
        """G4 §3 B6: `lr_scale` (default 1.0, exact — `self.g.lr * 1.0 == self.g.lr` in IEEE754, so the
        pin is untouched) scales DELTA's learning rate for this moment only (PREDICT's `modulate`, B6).
        Returns (S, T), the final sight/words winners of this moment (after any misfire birth) — a NEW
        return value (moment() returned None before this gene); every existing caller discards it as a
        bare statement, so this is additive. genome/predict.py's Predictor reads S to know what to
        expect next."""
        S = self._resonate(self.sight, x_s)
        T = self._resonate(self.words, x_w)
        if self.wire and self.t >= self.g.stage2_start and S and T:
            self._hebb(S, T)
            self._delta(S, T, lr=self.g.lr * lr_scale)
            S, T = self._misfire(S, T, x_s, x_w)
            self._prune(S, T)
            self._merge(self.sight, S, axis=0)
            self._merge(self.words, T, axis=1)
        self.t += 1
        if self.t % self.g.scale_every == 0:
            self._scale()
        return S, T

    def moment_sight(self, x_s: np.ndarray) -> None:
        """G4 §3 B2 (docs/G4-PREREG.md, row 1a's BODY/tape: a sight-only moment — an eye row whose moment
        has no matching ear row, §2.2 of the body contract). Resonance + novelty birth on sight ONLY: no
        MEET (no HEBB, DELTA, misfire-birth, PRUNE or MERGE — those all compare sight winners against
        word winners of the SAME moment, which a sight-only moment does not have). Mirrors moment()'s
        tail exactly (t advances; SCALE fires at its own multiples of t) so a life mixing moment_sight
        and moment stays on one homeostasis clock. Counted in `self.moments_sight_only` — see its
        docstring in __init__ for why that counter is a plain attribute and not a self.c key."""
        self._resonate(self.sight, x_s)
        self.moments_sight_only += 1
        self.t += 1
        if self.t % self.g.scale_every == 0:
            self._scale()

    def _hebb(self, S: List[int], T: List[int]) -> None:
        for s in S:
            for t in T:
                if self.mask[s, t] == 0:
                    self.mask[s, t] = 1
                    self.W[s, t] = self.g.lr                  # §10 clause 3: born at w = lr
                    self.strikes[s, t] = 0
                    self.c["edges_born"] += 1
                    self.edges_log.append((self.t, s, t))

    def _delta(self, S: List[int], T: List[int], lr: Optional[float] = None) -> None:
        lr = self.g.lr if lr is None else lr
        tgt_w = np.zeros(self.g.nmax); tgt_w[T] = 1.0
        for s in S:
            idx = self.mask[s] == 1
            self.W[s, idx] += lr * (tgt_w[idx] - self.W[s, idx])
        tgt_s = np.zeros(self.g.nmax); tgt_s[S] = 1.0
        for t in T:
            idx = self.mask[:, t] == 1
            self.W[idx, t] += lr * (tgt_s[idx] - self.W[idx, t])
        for s in S:
            np.clip(self.W[s], -1.0, 1.0, out=self.W[s])
        for t in T:
            np.clip(self.W[:, t], -1.0, 1.0, out=self.W[:, t])

    def _answer_of(self, area: Area, cid: int) -> Optional[int]:
        row = self.W[cid] if area is self.sight else self.W[:, cid]
        m = self.mask[cid] if area is self.sight else self.mask[:, cid]
        if not m.any():
            return None
        vals = np.where(m == 1, row, -np.inf)
        return int(np.argmax(vals))

    def _misfire(self, S, T, x_s, x_w):
        """BIRTH error misfires N: a cell whose strongest edge is not among this moment's winners on
        the other side misfires; N misfires → a cell is born beside it holding the current input."""
        for area, winners, other, x in ((self.sight, S, T, x_s), (self.words, T, S, x_w)):
            for cid in list(winners):
                ans = self._answer_of(area, cid)
                if ans is None:
                    continue
                if ans in other:
                    area.misfires[cid] = 0
                else:
                    area.misfires[cid] += 1
                    if area.misfires[cid] >= self.g.misfires:
                        area.misfires[cid] = 0
                        # §11 amendment 4: a cell born beside a cell it is already within THETA_M of would be
                        # born redundant (an immediate MERGE candidate) — refused, counted
                        if float(area.cells[cid] @ x) > self.g.theta_m:
                            self.c["births_refused_redundant"] += 1
                            continue
                        new = self._birth(area, x, "error")
                        if new is not None and new not in winners:
                            winners.append(new)
        return S, T

    def _prune(self, S: List[int], T: List[int]) -> None:
        fl, ch = self.g.prune_floor, self.g.prune_chances
        rows = np.array(sorted(set(S)), dtype=np.int64); cols = np.array(sorted(set(T)), dtype=np.int64)
        for sel in ((rows, slice(None)), (slice(None), cols)):
            m = self.mask[sel] == 1
            low = (np.abs(self.W[sel]) < fl) & m
            st = self.strikes[sel]
            st = np.where(low, np.minimum(st + 1, 255), 0).astype(np.uint8)
            self.strikes[sel] = st
            dead = (st >= ch) & m
            k = int(dead.sum())
            if k:
                W = self.W[sel]; M = self.mask[sel]; ST = self.strikes[sel]
                # log every pruned edge by its (sight, word) ids before it is erased
                if isinstance(sel[0], slice):
                    for r_, c_ in zip(*np.nonzero(dead)):
                        self.prunes_log.append((self.t, int(r_), int(cols[c_])))
                else:
                    for r_, c_ in zip(*np.nonzero(dead)):
                        self.prunes_log.append((self.t, int(rows[r_]), int(c_)))
                W[dead] = 0.0; M[dead] = 0; ST[dead] = 0
                self.W[sel] = W; self.mask[sel] = M; self.strikes[sel] = ST
                self.c["edges_pruned"] += k

    def _merge(self, area: Area, winners: List[int], axis: int) -> None:
        """MERGE cos>THETA_M same-answer: two alike winners with the same answer become one
        (the lower id is kept, rows averaged over the union of their edges)."""
        ws = sorted(set(w for w in winners if area.alive[w]))
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                if not (area.alive[a] and area.alive[b]):
                    continue
                if float(area.cells[a] @ area.cells[b]) <= self.g.theta_m:
                    continue
                aa, ab = self._answer_of(area, a), self._answer_of(area, b)
                if aa is None or ab is None or aa != ab:
                    continue
                if axis == 0:
                    ma, mb = self.mask[a].astype(np.float64), self.mask[b].astype(np.float64)
                    den = np.maximum(ma + mb, 1.0)
                    self.W[a] = (self.W[a] * ma + self.W[b] * mb) / den
                    self.mask[a] = ((ma + mb) > 0).astype(np.uint8)
                    self.strikes[a] = np.minimum(self.strikes[a], self.strikes[b])
                    self.W[b] = 0.0; self.mask[b] = 0; self.strikes[b] = 0
                else:
                    ma, mb = self.mask[:, a].astype(np.float64), self.mask[:, b].astype(np.float64)
                    den = np.maximum(ma + mb, 1.0)
                    self.W[:, a] = (self.W[:, a] * ma + self.W[:, b] * mb) / den
                    self.mask[:, a] = ((ma + mb) > 0).astype(np.uint8)
                    self.strikes[:, a] = np.minimum(self.strikes[:, a], self.strikes[:, b])
                    self.W[:, b] = 0.0; self.mask[:, b] = 0; self.strikes[:, b] = 0
                area.alive[b] = 0
                area.misfires[b] = 0
                self.c[f"cells_merged_{area.name}"] += 1
                self.merges.append((self.t, area.name, a, b))

    def _scale(self) -> None:
        """SCALE every N moments — synaptic scaling: a cell's edge vector is scaled down to unit norm
        when it exceeds it (never up, never removed)."""
        self.c["scale_events"] += 1
        for s in self.sight.alive_ids():
            n = float(np.linalg.norm(self.W[s]))
            if n > 1.0:
                self.W[s] /= n
        for t in self.words.alive_ids():
            n = float(np.linalg.norm(self.W[:, t]))
            if n > 1.0:
                self.W[:, t] /= n

    # ------------------------------------------------------------------ answering
    def _lit(self, area: Area, x: np.ndarray) -> Tuple[List[int], np.ndarray]:
        """§11 amendment 6: a question lights a side exactly as a moment does — its resonating cells
        (cos ≥ THETA_N), up to KWTA, best first. No birth: questions never change the organism."""
        if area.n == 0:
            return [], np.zeros(0)
        c = area.cos(x)
        order = np.argsort(-c, kind="stable")
        th = self._theta(area)
        lit = [int(i) for i in order[: self.g.kwta] if area.alive[i] and c[i] >= th]
        return lit, c

    def recall(self, side: str, x: np.ndarray, k: int = 1) -> Dict[str, object]:
        """RECALL k=1 + ABSTAIN: light one side (its resonating winners, §11 am. 6; none → NOVEL), read
        the strongest edge from any lit cell to the other side (none positive → NOEDGE); ABSTAIN when the
        strongest COMPETING edge — to a cell whose own answer leads back outside the lit set (§11 am. 5) —
        is within the ratio (→ RATIO). Otherwise the answer cell. Never changes the organism.

        G4 §3 B1 (RECALL k=N): k > 1 additionally returns "ranked", the top-k distinct answer cells by
        their strongest edge from a lit cell (ties by cell id) — it never changes which cell/reason is
        returned. k=1 (the default) is byte-identical to G1's recall: `ranked(...)` returns {} so the
        returned dict carries exactly the same keys as before this gene existed."""
        area, other = (self.sight, self.words) if side == "sight" else (self.words, self.sight)
        lit, c = self._lit(area, x)

        def ranked(cands: List[Tuple[float, int, int]]) -> Dict[str, object]:
            if k <= 1:
                return {}
            best_per: Dict[int, float] = {}
            for v, j, _l in cands:
                if j not in best_per or v > best_per[j]:
                    best_per[j] = v
            top = sorted(best_per.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
            return {"ranked": [(int(j), float(v)) for j, v in top]}

        if not lit:
            best_cos = float(c.max()) if len(c) else 0.0
            return {"cell": None, "reason": "novel", "lit": None, "best": 0.0, "second": 0.0, "cos": best_cos, **ranked([])}
        lit_set = set(lit)
        cands: List[Tuple[float, int, int]] = []          # (edge, other cell, lit cell)
        for l in lit:
            row = self.W[l] if side == "sight" else self.W[:, l]
            m = (self.mask[l] if side == "sight" else self.mask[:, l]) == 1
            m &= other.alive == 1
            for j in np.flatnonzero(m):
                v = float(row[j])
                if v > 0.0:
                    cands.append((v, int(j), l))
        if not cands:
            return {"cell": None, "reason": "noedge", "lit": lit[0], "best": 0.0, "second": 0.0, "cos": float(c[lit[0]]), **ranked(cands)}
        cands.sort(key=lambda z: (-z[0], z[1], z[2]))
        best, best_id, best_l = cands[0]
        second = 0.0
        for v, j, _l in cands[1:]:
            if j == best_id:
                continue
            if self._answer_of(other, j) not in lit_set:      # a competitor: it answers back to something not lit
                second = v
                break
        if second > 0.0 and second / best > self.g.abstain_ratio:
            return {"cell": None, "reason": "ratio", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), **ranked(cands)}
        close = self._margin_close(side, other, best_id, {l: float(c[l]) for l in lit})
        if close is not None:
            return {"cell": None, "reason": "close", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), "margin": close, **ranked(cands)}
        return {"cell": best_id, "reason": "answer", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), **ranked(cands)}

    def _margin_close(self, side: str, other: Area, best_id: int, cos_of: Dict[int, float]) -> Optional[float]:
        """G3 §1 ABSTAIN margin: on the sight side, the best-answering lit cell's cosine must beat the best lit cell of a
        DIFFERENT answer by the margin; returns the gap when it is too small, else None. Off when the gene is absent or side is words."""
        if self.g.abstain_margin is None or side != "sight":
            return None
        c_best = max([v for l, v in cos_of.items() if self._answer_of(self.sight, l) == best_id], default=None)
        c_other = max([v for l, v in cos_of.items() if self._answer_of(self.sight, l) not in (None, best_id)], default=None)
        if c_best is None or c_other is None:
            return None
        gap = c_best - c_other
        return gap if gap < self.g.abstain_margin else None

    def recall_many(self, side: str, xs: List[np.ndarray]) -> Dict[str, object]:
        """G1 §1: RECALL over glances. Each glance lights its resonating winners as `recall` does; the evidence for a cell
        on the other side is the SUM over glances of the strongest edge from that glance's lit cells to it; best/second/
        abstain by the same rules over the union of the lit sets. For ONE glance this is `recall`, result for result
        (pinned in tools/pin_g1.py). Never changes the organism."""
        area, other = (self.sight, self.words) if side == "sight" else (self.words, self.sight)
        lit_union: List[int] = []; cos_of: Dict[int, float] = {}; best_cos = 0.0
        evidence: Dict[int, Tuple[float, int]] = {}                       # other cell -> (summed evidence, lit cell of its first strongest edge)
        for x in xs:
            lit, c = self._lit(area, x)
            if len(c):
                best_cos = max(best_cos, float(c.max()))
            if not lit:
                continue
            for l in lit:
                if l not in cos_of:
                    lit_union.append(l); cos_of[l] = float(c[l])
            per_j: Dict[int, Tuple[float, int]] = {}
            for l in lit:
                row = self.W[l] if side == "sight" else self.W[:, l]
                m = (self.mask[l] if side == "sight" else self.mask[:, l]) == 1
                m &= other.alive == 1
                for j in np.flatnonzero(m):
                    v = float(row[j]); j = int(j)
                    if v > 0.0 and (j not in per_j or v > per_j[j][0]):
                        per_j[j] = (v, l)
            for j, (v, l) in per_j.items():
                e = evidence.get(j)
                evidence[j] = (v, l) if e is None else (e[0] + v, e[1])
        if not lit_union:
            return {"cell": None, "reason": "novel", "lit": None, "best": 0.0, "second": 0.0, "cos": best_cos}
        if not evidence:
            return {"cell": None, "reason": "noedge", "lit": lit_union[0], "best": 0.0, "second": 0.0, "cos": cos_of[lit_union[0]]}
        cands = sorted(evidence.items(), key=lambda kv: (-kv[1][0], kv[0]))
        best_id, (best, best_l) = cands[0]
        lit_set = set(lit_union); second = 0.0
        for j, (v, _l) in cands[1:]:
            if self._answer_of(other, j) not in lit_set:
                second = v
                break
        if second > 0.0 and second / best > self.g.abstain_ratio:
            return {"cell": None, "reason": "ratio", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l]}
        close = self._margin_close(side, other, best_id, cos_of)
        if close is not None:
            return {"cell": None, "reason": "close", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l], "margin": close}
        return {"cell": best_id, "reason": "answer", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l]}

    def edge_many(self, side: str, xs: List[np.ndarray], other_cell: int) -> float:
        """G1 §1: Q3/Q4's edge summed over glances (one glance = `edge`)."""
        return float(sum(self.edge(side, x, other_cell) for x in xs))

    def edge(self, side: str, x: np.ndarray, other_cell: int) -> float:
        """The strongest edge from the lit cells on `side` (none resonating → 0) to `other_cell` — Q3/Q4."""
        area = self.sight if side == "sight" else self.words
        lit, _c = self._lit(area, x)
        best = 0.0
        for l in lit:
            if side == "sight":
                v = float(self.W[l, other_cell]) if self.mask[l, other_cell] else 0.0
            else:
                v = float(self.W[other_cell, l]) if self.mask[other_cell, l] else 0.0
            best = max(best, v)
        return best

    # ------------------------------------------------------------------ the ask door (G1 §5 step 7): save / load, never in the hash
    def save(self, path) -> None:
        import pathlib as _pl
        path = _pl.Path(path)
        np.savez_compressed(path, sight_cells=self.sight.cells[: self.sight.n], sight_alive=self.sight.alive, sight_misfires=self.sight.misfires,
                            words_cells=self.words.cells[: self.words.n], words_alive=self.words.alive, words_misfires=self.words.misfires,
                            W=self.W, mask=self.mask, strikes=self.strikes)
        meta = {"t": self.t, "budget_left": self.budget_left, "arrivals": self.arrivals, "c": self.c, "births": self.births, "merges": self.merges,
                "edges_log": self.edges_log, "prunes_log": self.prunes_log, "refusals_by_arrival": self.refusals_by_arrival,
                "sight_n": self.sight.n, "words_n": self.words.n, "genome_text": self.g.text, "state_hash": self.state_hash()}
        path.with_suffix(".json").write_text(json.dumps(meta))

    @classmethod
    def load(cls, path, genome: "Genome") -> "Organism":
        import pathlib as _pl
        path = _pl.Path(path)
        z = np.load(path.with_suffix(".npz")); meta = json.loads(path.with_suffix(".json").read_text())
        o = cls(genome)
        o.sight.n = int(meta["sight_n"]); o.words.n = int(meta["words_n"])
        o.sight.cells[: o.sight.n] = z["sight_cells"]; o.sight.alive[:] = z["sight_alive"]; o.sight.misfires[:] = z["sight_misfires"]
        o.words.cells[: o.words.n] = z["words_cells"]; o.words.alive[:] = z["words_alive"]; o.words.misfires[:] = z["words_misfires"]
        o.W[:] = z["W"]; o.mask[:] = z["mask"]; o.strikes[:] = z["strikes"]
        o.t = int(meta["t"]); o.budget_left = int(meta["budget_left"]); o.arrivals = int(meta["arrivals"]); o.c = dict(meta["c"])
        o.births = [tuple(r) for r in meta["births"]]; o.merges = [tuple(r) for r in meta["merges"]]
        o.edges_log = [tuple(r) for r in meta["edges_log"]]; o.prunes_log = [tuple(r) for r in meta["prunes_log"]]
        o.refusals_by_arrival = list(meta["refusals_by_arrival"])
        # edit: Claude (Sonnet 5, builder F), 2026-09-21 17:45 +0400 -- the orchestrator's follow-up task
        # (commit 412d721): the closed lives' readers (tools/verdict_g4.py's W3-2 reach control, the
        # exam) must still LOAD old-format snapshots (saved before the state_hash repair). Try the NEW
        # live-block hash first; on mismatch, try the LEGACY full-array hash (kept verbatim as
        # `_state_hash_legacy`, never deleted); refuse only when BOTH fail. A snapshot saved by either
        # generation of the code therefore loads; a genuinely corrupted one (neither digest matches)
        # still refuses loudly, by name (docs/briefs/G5-F-REPORT.md §4).
        new_hash = o.state_hash()
        if new_hash != meta["state_hash"]:
            legacy_hash = o._state_hash_legacy()
            if legacy_hash != meta["state_hash"]:
                raise GenomeError(
                    f"loaded organism's state_hash {new_hash[:16]} (legacy {legacy_hash[:16]}) is not the saved {meta['state_hash'][:16]}"
                )
        return o

    # ------------------------------------------------------------------ identity
    # edit: Claude (Sonnet 5, builder F), 2026-09-21 16:45 +0400 -- G5-F task 2 / MIND-MEMORY.md R1: hash
    # only the LIVE block W[:n_s, :n_w] (mask, strikes likewise) instead of the full nmax x nmax arrays.
    # A cell id is only ever written by _birth() with cid < area.n at the time of the write, and area.n
    # never decreases (G4 CYCLE retires/merges cells but keeps their ids below n) -- so every nonzero
    # entry of W/mask/strikes already lives inside [:sight.n, :words.n]; verified empirically (not just
    # argued) on life 1/2/3a's real closed snapshots: count_nonzero(W) == count_nonzero(W[:n_s,:n_w]),
    # same for mask and strikes, on all three (docs/briefs/G5-F-REPORT.md). This CHANGES THE DIGEST for
    # the same state (the bytes hashed are different) -- it is a new pin, reported, never written to
    # tools/gate_g4.py's PIN or any test's PINNED_HASH_DEV on master; that is the orchestrator's call.
    def state_hash(self) -> str:
        """sha256 over the fixed-dtype state arrays and the counters (mark vii, the replay gate). W/mask/
        strikes are hashed only over their LIVE block [:sight.n, :words.n] -- no cell id >= n is ever
        written, so this is losslessly equivalent to hashing the full nmax x nmax arrays, just without
        paying for the >99.6% that can never be non-zero (MIND-MEMORY.md §4 R1)."""
        h = hashlib.sha256()
        for a in (self.sight, self.words):
            h.update(a.cells[: a.n].tobytes()); h.update(a.alive.tobytes()); h.update(a.misfires.tobytes())
            h.update(np.int64(a.n).tobytes())
        n_s, n_w = self.sight.n, self.words.n
        h.update(self.W[:n_s, :n_w].tobytes()); h.update(self.mask[:n_s, :n_w].tobytes()); h.update(self.strikes[:n_s, :n_w].tobytes())
        h.update(np.int64(self.t).tobytes()); h.update(np.int64(self.budget_left).tobytes())
        h.update(json.dumps(self.c, sort_keys=True).encode())
        h.update(json.dumps(self.births).encode()); h.update(json.dumps(self.merges).encode())
        h.update(json.dumps(self.edges_log).encode()); h.update(json.dumps(self.prunes_log).encode())
        return h.hexdigest()

    # edit: Claude (Sonnet 5, builder F), 2026-09-21 17:45 +0400 -- kept VERBATIM (byte-for-byte the old
    # state_hash body, before the live-block repair) so Organism.load can still verify a pre-repair
    # snapshot's saved digest. Never called from anywhere except load()'s fallback; state_hash() above
    # remains the one every NEW save() writes and every live/replay path reads.
    def _state_hash_legacy(self) -> str:
        """The PRE-REPAIR state_hash: sha256 over the FULL nmax x nmax W/mask/strikes arrays (docs/briefs/
        G5-F-REPORT.md §4). Exists only so Organism.load can accept a snapshot saved before the live-block
        repair; every other caller uses state_hash()."""
        h = hashlib.sha256()
        for a in (self.sight, self.words):
            h.update(a.cells[: a.n].tobytes()); h.update(a.alive.tobytes()); h.update(a.misfires.tobytes())
            h.update(np.int64(a.n).tobytes())
        h.update(self.W.tobytes()); h.update(self.mask.tobytes()); h.update(self.strikes.tobytes())
        h.update(np.int64(self.t).tobytes()); h.update(np.int64(self.budget_left).tobytes())
        h.update(json.dumps(self.c, sort_keys=True).encode())
        h.update(json.dumps(self.births).encode()); h.update(json.dumps(self.merges).encode())
        h.update(json.dumps(self.edges_log).encode()); h.update(json.dumps(self.prunes_log).encode())
        return h.hexdigest()

    def summary(self) -> Dict[str, object]:
        return {
            "moments": self.t, "cells_sight": int(self.sight.alive.sum()), "cells_words": int(self.words.alive.sum()),
            "cells_born_sight": self.sight.n, "cells_born_words": self.words.n,
            "edges_alive": int(self.mask.sum()), "moments_sight_only": self.moments_sight_only, **self.c,
        }
