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
edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400 — L-4/L-7 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
§4, docs/organs/EYE.md §4 G-EYE-5/G-EYE-6): GAZE's fullmatch gains an optional trailing ` coarse (<int>)` clause
(absent = today, byte-identical — the coarse feature is added in genome/gaze.py, gated on the key's presence);
SURPRISE's fullmatch gains an optional trailing ` predicted (mind-cell)` literal (the only accepted value; the
mechanism is Organism.expected_sight() + moment(confirm=), below). `Organism.moment`/`_resonate` gain a
`confirm` flag (default False, every existing call site untouched byte-for-byte): CONFIRMED means HEBB/DELTA
only — no birth (a would-be novelty birth is counted on the plain attribute `births_skipped_confirmed`, kept
OUT of `self.c`/state_hash for the same reason `moments_sight_only` is, see its own comment below: a new
`self.c` key would move every genome's hash, even one that never declares SURPRISE), no misfire/prune/merge.
`Organism.expected_sight(xw)` is read-only (never births, mirrors `recall()`'s own alive-masking).

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
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 00:58 +0400 — ALPHA4-G.md task 1 (docs/ALPHA4-PREREG.md
    # §2/§3): `nmax` MOVED here from its old position among the non-default fields (it sat right after
    # `budget`) so it can carry a default of None -- GROW unbounded declares no NMAX line at all, and a
    # dataclass field without a default cannot follow one that has a default. Genome is built exclusively
    # via `Genome(text=text, **g)` (genome/machinery.py's own parse_genome, the ONLY constructor call site
    # — grepped project-wide, tests included) so every call is keyword-only and this reorder changes no
    # call site's behaviour. NMAX declared (the old, unchanged road): parsed into `g["nmax"]` exactly as
    # before, an int, in the SAME dict-building code (`elif gene == "NMAX": g["nmax"] = int(args[0])`,
    # untouched). NMAX absent AND GROW declared: `g["nmax"]` is never set by the parser at all, and
    # `Genome(**g)` falls back to this field's own default, None -- byte-identical to explicitly writing
    # `g["nmax"] = None`, so `parse_genome`'s own GROW branch (below) does not need to set it.
    nmax: Optional[int] = None
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 00:58 +0400 — ALPHA4-G.md task 3: BUDGET's
    # OPTIONAL trailing "; regenerate <n> per <m> moments" clause (mirrors GAZE's "coarse" / SURPRISE's
    # "predicted" optional-trailing-clause precedent above: a NEW pair of plain Genome fields, defaulted
    # so the old bare "BUDGET <n> per arrival" line -- every genome on disk before this edit -- parses to
    # the EXACT same values as before, budget_regen_n=0 (no regeneration) and budget_regen_every=None).
    budget_regen_n: int = 0
    budget_regen_every: Optional[int] = None
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
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:25 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # item 4 (BODY-SENSES.md §4.5): SENSE smell kind size folder age. New vocabulary, dispatched on
            # args[0] exactly as ear/ear-sound/colour above (additive: those branches untouched). Stored
            # under g["declared"]["SENSE_SMELL"] (unlike eye/ear/colour, which are plain Genome fields) --
            # SENSE_SMELL names a real MIND-side consumer (creature/mind.py's _consume_smell) that
            # creature/genes.py's RUNS/unwired() law must name, matching BIND/DELIVER/MOMENT's own
            # convention for a "SENSE ..." line with a real call site.
            elif gene == "SENSE" and args[0] == "smell":
                m = re.fullmatch(r"kind size folder age", a[len("smell "):].strip())
                if not m: raise GenomeError(f"SENSE smell: cannot read {a!r} (BODY-SENSES §4.5: SENSE smell kind size folder age)")
                g["declared"]["SENSE_SMELL"] = {"fields": ["kind", "size", "folder", "age"]}
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:25 +0400 — item 3 (BODY-SENSES.md §4.6):
            # SENSE touch from hands: exit rate stalls retries bytes. Same convention as SENSE smell above.
            elif gene == "SENSE" and args[0] == "touch":
                m = re.fullmatch(r"from hands: exit rate stalls retries bytes", a[len("touch "):].strip())
                if not m: raise GenomeError(f"SENSE touch: cannot read {a!r} (BODY-SENSES §4.6: SENSE touch from hands: exit rate stalls retries bytes)")
                g["declared"]["SENSE_TOUCH"] = {"from": "hands", "fields": ["exit", "rate", "stalls", "retries", "bytes"]}
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
                # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:00 +0400 — ALPHA4-G.md task 3
                # (docs/ALPHA4-PREREG.md §2/§3): an OPTIONAL trailing "; regenerate <n> per <m> moments"
                # clause (GAZE's "coarse"/SURPRISE's "predicted" precedent, machinery.py's own comments
                # above): absent -> budget_regen_n=0, budget_regen_every=None, the exact values every
                # genome on disk before this edit already carries (the dataclass field defaults), so the
                # bare "BUDGET <n> per arrival" line is byte-identical to its old, narrower regex.
                m = re.fullmatch(r"(\d+) per arrival(?:; regenerate (\d+) per (\d+) moments)?", a)
                if not m: raise GenomeError(f"BUDGET: cannot read {a!r} (BUDGET <n> per arrival[; regenerate <n> per <m> moments])")
                g["budget"] = int(m.group(1))
                if m.group(2) is not None:
                    g["budget_regen_n"] = int(m.group(2))
                    g["budget_regen_every"] = int(m.group(3))
            elif gene == "NMAX":
                g["nmax"] = int(args[0])
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:00 +0400 — ALPHA4-G.md task 1
            # (docs/ALPHA4-PREREG.md §2/§3, his 00:17 word «no cap … nothing hardcoded except judges and
            # laws»): GROW unbounded, a strict fixed-literal gene like BIND/TRAITS above. Stored under
            # `g["declared"]["GROW"]` (a real MIND/machinery-side mechanism, not a plain field like NMAX --
            # `creature/genes.py`'s RUNS registry names its site, W3-0's own convention for every gene that
            # is more than a number). `required`'s own "nmax" entry is dropped below, post-loop, ONLY when
            # this key is present -- so a genome declaring GROW without NMAX is exactly as valid as one
            # declaring NMAX without GROW always was, and a genome declaring NEITHER still refuses with the
            # unchanged "genome lacks ['nmax']" message (never silently defaults to unbounded).
            elif gene == "GROW":
                m = re.fullmatch(r"unbounded", a)
                if not m: raise GenomeError(f"GROW: cannot read {a!r} (ALPHA4-G task 1: GROW unbounded)")
                g["declared"]["GROW"] = {"unbounded": True}
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
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:56 +0400 — ALPHA4-PREREG.md §3/§4:
            # the "moments" form is untouched, tried FIRST (byte-identical grammar, byte-identical tuple
            # shape for every genome on disk today). A NEW second form, "<n> <name> by <JUDGE>", is tried
            # only when the first does not match — never the other way round, so "moments" cannot be
            # mis-read as "by". `<JUDGE>` must be the literal "READY" (the only judge this machinery
            # implements, §4 THE READINESS JUDGE); any other word (a typo, an unimplemented judge name)
            # refuses BY NAME, never silently accepted or silently ignored. The stored tuple keeps the
            # existing 4-element (index, name, a, b) shape `stage2_start` already unpacks — `a` holds the
            # judge name (a str) instead of a moment count (an int) for this form, `b` stays None; nothing
            # currently reads `stages[i][2]` except `stage2_start`'s `name == "meet"` branch, which never
            # touches a judge-form row. `g["declared"]["STAGE_READY"]` is written ADDITIONALLY (never in
            # place of the stages entry) so W3-0's generic refusal (creature/genes.py) has a real key to
            # gate on — a genome that declares "by READY" but whose tree has no judge wired refuses to
            # start, exactly like every other G4-wave gene.
            elif gene == "STAGE":
                m = re.fullmatch(r"(\d+) (\w+) moments (\d+)\.\.(\d*)", a)
                if m:
                    g["stages"].append((int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)) if m.group(4) else None))
                else:
                    m2 = re.fullmatch(r"(\d+) (\w+) by (\w+)", a)
                    if not m2: raise GenomeError(f"STAGE: cannot read {a!r} (ALPHA4-PREREG §3: STAGE <n> <name> moments <a>..<b> | STAGE <n> <name> by <JUDGE>)")
                    idx, name, judge = int(m2.group(1)), m2.group(2), m2.group(3)
                    if judge != "READY":
                        raise GenomeError(f"STAGE: unknown judge {judge!r} (only READY is implemented, ALPHA4-PREREG §4) — the organism does not start")
                    g["stages"].append((idx, name, judge, None))
                    g["declared"]["STAGE_READY"] = {"stage": idx}
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
                # L-7 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400): an OPTIONAL trailing
                # " coarse <int>" clause, wrapped in its own non-capturing optional group so a genome that
                # never writes it (every genome on disk before this edit) parses to the exact same dict shape
                # as before — "coarse" simply absent from g["gaze"], and genome/gaze.py's glances() only adds
                # the fifth whole-canvas feature when the key IS present (byte-identical otherwise).
                m = re.fullmatch(r"surprise fixations (\d+) grid (\d+) canvas (\d+) glance (\d+) ink (contrast|border)(?: coarse (\d+))?", a)
                if not m: raise GenomeError(f"GAZE: cannot read {a!r} (G1 §1: surprise fixations F grid G canvas C glance L ink contrast [coarse N])")
                g["gaze"] = {"fixations": int(m.group(1)), "grid": int(m.group(2)), "canvas": int(m.group(3)), "glance": int(m.group(4)), "ink": m.group(5)}
                if m.group(6) is not None:
                    g["gaze"]["coarse"] = int(m.group(6))
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
                # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400): an OPTIONAL trailing
                # " predicted mind-cell" literal — the ONLY accepted value (any other word after "predicted"
                # refuses, matching CRASH/ASK's own strict-literal discipline); absent, this is byte-identical
                # to the old parse (g["declared"]["SURPRISE"] == {"floor": f}, exactly as every genome that
                # declares the OLD "SURPRISE floor <f>" line on disk still parses).
                m = re.fullmatch(r"floor (" + _NUM + r")(?: predicted (mind-cell))?", a)
                if not m: raise GenomeError(f"SURPRISE: cannot read {a!r} (row 1c: SURPRISE floor <f> [predicted mind-cell])")
                g["declared"]["SURPRISE"] = {"floor": float(m.group(1))}
                if m.group(2) is not None:
                    g["declared"]["SURPRISE"]["predicted"] = m.group(2)
            elif gene == "CYCLE":
                # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:01 +0400 — ALPHA4-G.md task 4
                # (docs/ALPHA4-PREREG.md §2/§3): a SECOND, distinct form -- "consolidate when redundant >
                # <share> of alive" -- stored under its OWN key ("share", never "grow_to") so the OLD
                # form's declared dict stays EXACTLY {"grow_to": f}, no "kind" tag added (test_parse_g4.py
                # :104 already pins that exact shape against a hand-built literal; genome/machinery.py:772
                # and genome/sleep.py's cycle() distinguish the two forms by which key is present). Task 4's
                # own refusal ("under GROW, the old form is REFUSED — a cycle keyed on a cap that does not
                # exist") cannot be checked HERE: GROW may be declared LATER in the genome text than CYCLE
                # (ALPHA4.genome's own draft has GROW on line 93, the old CYCLE line on line 47) — it is
                # checked once, post-loop, beside the `required` check below.
                m1 = re.fullmatch(r"grow to (" + _NUM + r") nmax then consolidate", a)
                m2 = re.fullmatch(r"consolidate when redundant > (" + _NUM + r") of alive", a)
                if m1:
                    g["declared"]["CYCLE"] = {"grow_to": float(m1.group(1))}
                elif m2:
                    g["declared"]["CYCLE"] = {"share": float(m2.group(1))}
                else:
                    raise GenomeError(f"CYCLE: cannot read {a!r} (CYCLE grow to <f> nmax then consolidate | CYCLE consolidate when redundant > <f> of alive)")
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
                # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 (docs/briefs/
                # LIFE-C-QUESTION-SENTENCE.md task 3; NEXT-LIFE-PLAN-2026-09-22.md §4 L-11): the OLD line
                # ("two-word frames is near under-judge" — its own "is" condition unreachable by
                # construction, MIND-THINKING-LANGUAGE.md §4.7) is REPLACED, not extended, by the new one:
                # a frame is now two words that met in ONE instant, judged by the eye's own recall, never
                # next-token. The old literal no longer parses -- a genome carrying it refuses exactly like
                # any other unknown value (tests/genome/G4-draft.genome and test_parse_g4.py's own fixture
                # updated alongside this line, in the same commit).
                m = re.fullmatch(r"two-word frames from co-occurring words; judged by the eye; never next-token", a)
                if not m: raise GenomeError(f"SENTENCE: cannot read {a!r} (L-11: SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token)")
                g["declared"]["SENTENCE"] = {"frames": "co-occurring", "judged": "eye", "next_token": False}
            elif gene == "QUESTION":
                # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 (docs/briefs/
                # LIFE-C-QUESTION-SENTENCE.md task 1; NEXT-LIFE-PLAN-2026-09-22.md §4 L-10): a want (a
                # wordless sight seen twice, a rule that failed once, a belief clash, or PARK parking one)
                # writes ONE question to the world door.
                m = re.fullmatch(r"from wants; forms what-is is which; to the world door", a)
                if not m: raise GenomeError(f"QUESTION: cannot read {a!r} (L-10: QUESTION from wants; forms what-is is which; to the world door)")
                g["declared"]["QUESTION"] = {"source": "wants", "forms": ["what-is", "is", "which"], "to": "world door"}
            elif gene == "MOUTH":
                # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 (docs/briefs/
                # LIFE-C-QUESTION-SENTENCE.md task 4; MOTOR-HANDS.md G-MOT-6): says one filed, CITED frame
                # per think; an uncited frame is refused by name, never said.
                m = re.fullmatch(r"say one frame per think; journaled", a)
                if not m: raise GenomeError(f"MOUTH: cannot read {a!r} (L-11: MOUTH say one frame per think; journaled)")
                g["declared"]["MOUTH"] = {"say": "one frame per think", "journaled": True}
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
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:25 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # item 2 (MOTOR-HANDS.md G-MOT-4, the plan's L-12): HANDS gains an OPTIONAL trailing clause
            # "shelf <dir> cpu <n> mem <n> wall <n>" wrapped in its own non-capturing optional group -- the
            # pre-existing SHORT form ("HANDS jail <path>", tests/genome/test_parse_g4.py:111's own pin
            # against tests/genome/G4-draft.genome) keeps parsing to the EXACT same one-key dict as before
            # this edit; only the full form (genome/LIFE.genome:76's own DRAFT line) gains the four extra
            # keys.
            elif gene == "HANDS":
                m = re.fullmatch(r"jail ([A-Za-z0-9_./-]+)(?: shelf ([A-Za-z0-9_./-]+) cpu (\d+) mem (\d+) wall (\d+))?", a)
                if not m: raise GenomeError(f"HANDS: cannot read {a!r} (row 6: HANDS jail <path>[ shelf <dir> cpu <n> mem <n> wall <n>])")
                d: Dict[str, object] = {"jail": m.group(1)}
                if m.group(2) is not None:
                    d.update({"shelf": m.group(2), "cpu": int(m.group(3)), "mem": int(m.group(4)), "wall": int(m.group(5))})
                g["declared"]["HANDS"] = d
            elif gene == "ASK":
                # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-14 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
                # §4 L-14): the literal six-verb line generalised to ANY space-separated list drawn from the known
                # verbs, so a genome may drop one (LIFE.genome's own line has no `next` — "no mechanism predicts a
                # next thing"). G5.genome's existing six-verb line still matches (same verbs, same order) — byte-
                # identical `declared["ASK"]["verbs"]` for every genome already on disk.
                _ASK_VERBS = ("what-is", "show", "is", "which", "next", "why")
                m = re.fullmatch(r"(?:" + "|".join(_ASK_VERBS) + r")(?: (?:" + "|".join(_ASK_VERBS) + r"))*", a)
                if not m: raise GenomeError(f"ASK: cannot read {a!r} (§2.7/L-14: ASK <verb> [<verb> ...], drawn from {_ASK_VERBS})")
                g["declared"]["ASK"] = {"verbs": a.split()}
            # ==================================================================== G4 §11 Wave 2 B9: THINK/EXAM/FROZEN.
            # edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — three new genes, parsed only (Wave 2 B9).
            # Interface fixed for Builder A: declared["THINK"] == {"every": int}, declared["EXAM"] == {"every": int},
            # declared["FROZEN"] == {"after": int}. None of these are in `required`; none touch self.c (the pin).
            elif gene == "THINK":
                # edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
                # §4 L-5, docs/briefs/LIFE-E-THINK-THREAD.md item 1): the optional tail "; on its own thread; lands next
                # boundary". Absent -> declared["THINK"] == {"every": int} EXACTLY as before this brief (no "threaded" key
                # at all, not even False) -- every existing test/genome asserting that exact shape (tests/genome/
                # test_parse_g4.py, test_parse_g4_wave2.py, tests/creature/test_wave2_think.py) stays byte-identical, and
                # creature/mind.py reads the flag with `.get("threaded", False)` so an old-shape dict (a test that builds
                # `{"every": N}` by hand) is read as untreaded, exactly today's behaviour. Present -> declared["THINK"]
                # gains "threaded": True, creature/mind.py's own switch to the threaded road.
                m = re.fullmatch(r"every (\d+) canvases(; on its own thread; lands next boundary)?", a)
                if not m: raise GenomeError(f"THINK: cannot read {a!r} (§11: THINK every <n> canvases[; on its own thread; lands next boundary])")
                g["declared"]["THINK"] = {"every": int(m.group(1))}
                if m.group(2):
                    g["declared"]["THINK"]["threaded"] = True
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
            # edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:58 +0400 — docs/A4-LADDER-PREREG.md §2.5 (A4L-EXPLORE): a
            # SECOND ACT line, `ACT value reward <n>; optimism <f>` — the game act chooser's VALUE law (creature/mind.py
            # `_maybe_choose_act`: the act's value = its mean REWARD over its last <n> outcomes; an act with no outcome in
            # that window reads <f>). Dispatched on args[0] == "value" exactly as SENSE dispatches on args[0]; stored under
            # declared["ACT_VALUE"] so the verbs line's own declared["ACT"] is never overwritten. The verbs branch below is
            # untouched byte for byte; the one form it accepted that this branch now takes is a verb list that STARTS with
            # the word "value" — no genome on disk has one (grep), and «ACT value» alone now refuses by name.
            elif gene == "ACT" and args and args[0] == "value":
                m = re.fullmatch(r"value reward (\d+); optimism (" + _NUM + r")", a)
                if not m: raise GenomeError(f"ACT value: cannot read {a!r} (A4L-EXPLORE: ACT value reward <n>; optimism <f>)")
                if int(m.group(1)) < 1: raise GenomeError(f"ACT value: the window must be >= 1 outcome, got {m.group(1)}")
                g["declared"]["ACT_VALUE"] = {"law": "reward", "window": int(m.group(1)), "optimism": float(m.group(2))}
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
            # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6 (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
            # §4 L-6; docs/briefs/LIFE-A-ANSWER-SELF.md #1/#2): THRESH (each SIGHT cell's own band of the last
            # <history> cosines it answered CORRECTLY) and ANSWER (the graded answer: sure/unsure/unknown against
            # that band, or THETA_N when the gene is undeclared/the band is thin). Both new vocabulary; a strict
            # fullmatch, so a placeholder value refuses exactly like every other gene here.
            elif gene == "THRESH":
                m = re.fullmatch(r"cell own band history (\d+)", a)
                if not m: raise GenomeError(f"THRESH: cannot read {a!r} (L-6: THRESH cell own band history <n>)")
                g["declared"]["THRESH"] = {"history": int(m.group(1))}
            elif gene == "ANSWER":
                m = re.fullmatch(r"resembles under own-band; unknown below (" + _NUM + r")", a)
                if not m: raise GenomeError(f"ANSWER: cannot read {a!r} (L-6: ANSWER resembles under own-band; unknown below <f>)")
                g["declared"]["ANSWER"] = {"unknown_below": float(m.group(1))}
            # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-9 (docs/briefs/LIFE-A-ANSWER-SELF.md
            # #3): SELF — the mind reads its own body readings; a belief about itself when a counter stalls while
            # another moves, births_refused_nmax rises, or the backlog crosses a threshold; THINK is skipped (and
            # counted) while the last body row's backlog stays over that same threshold.
            elif gene == "SELF":
                m = re.fullmatch(r"from body; beliefs about itself; skip thinks when backlog > (\d+)", a)
                if not m: raise GenomeError(f"SELF: cannot read {a!r} (L-9: SELF from body; beliefs about itself; skip thinks when backlog > <n>)")
                g["declared"]["SELF"] = {"backlog_threshold": int(m.group(1))}
            # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:0x +0400 — ALPHA4-H task 2 (docs/briefs/
            # ALPHA4-H.md; ALPHA4-PREREG.md §3): a THIRD "SENSE" shape, dispatched on args[0]=="read" exactly
            # like "eye"/"ear"/"ear-sound"/"smell"/"touch"/"colour"/"body" above (additive: none of those
            # branches are touched). `SENSE read shelf <sqlite> curriculum <md> every <n> s words <k> canvas
            # <px>` -- a sentence SHOWN (rendered on a canvas of <px>) and HEARD (its words as ear rows), at
            # most <k> words per moment, every <n> seconds. Stored under g["declared"]["SENSE_READ"] (unlike
            # SENSE eye/ear/colour, which are plain Genome fields) -- SENSE_READ names a real call site
            # (creature/senses/read.py, wired from creature/body.py) that creature/genes.py's RUNS/unwired()
            # law must name, the same convention SENSE_SMELL/SENSE_TOUCH/SENSE_BODY already use.
            elif gene == "SENSE" and args[0] == "read":
                rest = " ".join(args[1:])
                m = re.fullmatch(r"shelf ([A-Za-z0-9_./-]+) curriculum ([A-Za-z0-9_./-]+) every (\d+) s words (\d+) canvas (\d+)", rest)
                if not m: raise GenomeError(f"SENSE read: cannot read {rest!r} (ALPHA4-PREREG §3: SENSE read shelf <sqlite> curriculum <md> every <n> s words <k> canvas <px>)")
                g["declared"]["SENSE_READ"] = {"shelf": m.group(1), "curriculum": m.group(2), "every_s": int(m.group(3)),
                                                "words": int(m.group(4)), "canvas": int(m.group(5))}
            # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:0x +0400 — ALPHA4-H task 3 (ALPHA4-PREREG.md
            # §3): the FIRST "DOOR" gene word (a brand-new top-level keyword, dispatched on args[0] the same
            # way "SENSE" is -- builder I's `DOOR web ...` is a SIBLING elif on args[0]=="web", landing beside
            # this one at integration, neither touching the other). `DOOR lexicon <sqlite> answers what-is by
            # showing` -- the offline dictionary door; `DOOR_LEXICON` names creature/senses/lexicon.py's real
            # call site in creature/genes.py's RUNS/unwired() law.
            elif gene == "DOOR" and args and args[0] == "lexicon":
                rest = " ".join(args[1:])
                m = re.fullmatch(r"([A-Za-z0-9_./-]+) answers what-is by showing", rest)
                if not m: raise GenomeError(f"DOOR lexicon: cannot read {rest!r} (ALPHA4-PREREG §3: DOOR lexicon <sqlite> answers what-is by showing)")
                g["declared"]["DOOR_LEXICON"] = {"sqlite": m.group(1)}
            # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §3/§6: EVOLVE
            # every <n> h; mutate 1 gene within bounds; judge on the last <m> h; adopt at sleep under the regression
            # bar. Every clause but the two integers is a fixed literal (matching CRASH/ASK's own strict-literal
            # discipline) — the mechanism this line names is exactly and only ALPHA4-PREREG.md §6, so a genome
            # cannot silently ask for a DIFFERENT evolve mechanism by writing different words here.
            elif gene == "EVOLVE":
                m = re.fullmatch(r"every (\d+) h; mutate 1 gene within bounds; judge on the last (\d+) h; "
                                  r"adopt at sleep under the regression bar", a)
                if not m: raise GenomeError(f"EVOLVE: cannot read {a!r} (§6: EVOLVE every <n> h; mutate 1 gene "
                                             f"within bounds; judge on the last <m> h; adopt at sleep under the regression bar)")
                g["declared"]["EVOLVE"] = {"every_h": int(m.group(1)), "judge_h": int(m.group(2))}
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:56 +0400 — ALPHA4-PREREG.md §3: THE
            # WEB DOOR. New vocabulary, dispatched on args[0] exactly as SENSE eye/ear/colour/… dispatch on
            # THEIR args[0] (so a future "DOOR lexicon …" branch, builder H's, can be added the same way
            # without touching this one — two DOOR forms are additive, not a merge conflict on one regex).
            # A strict fullmatch of the PREREG's own literal line: a typo anywhere (the fixed literal
            # tokens, a non-numeric floor/rate/stage, a malformed path) refuses BY NAME, never silently
            # substitutes a default. Stored under `declared["DOOR_WEB"]` (never a bare Genome field): the
            # web door is a G4-wave "declared gene" subject to creature/genes.py's unwired() refusal law,
            # matching WORLD_GAME's own precedent for a second DOOR-shaped line.
            elif gene == "DOOR" and args[0] == "web":
                m = re.fullmatch(
                    r"web wikipedia-summary wiktionary; floor (" + _NUM + r") s; (\d+) per hour; "
                    r"opens at STAGE (\d+); hold-file ([A-Za-z0-9_./-]+)", a)
                if not m:
                    raise GenomeError(f"DOOR web: cannot read {a!r} (ALPHA4-PREREG §3: DOOR web wikipedia-summary "
                                       f"wiktionary; floor <n> s; <n> per hour; opens at STAGE <n>; hold-file <path>)")
                g["declared"]["DOOR_WEB"] = {
                    "sources": ["wikipedia-summary", "wiktionary"], "floor_s": float(m.group(1)),
                    "per_hour": int(m.group(2)), "opens_at_stage": int(m.group(3)), "hold_file": m.group(4),
                }
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:56 +0400 — ALPHA4-PREREG.md §4(d): THE
            # SEAT'S GRADES + THE HOLD. New vocabulary under the existing "SENSE" gene (dispatched on
            # args[0], exactly like SENSE smell/touch above); a thread publishing `ask/graded/<id>.json`
            # rows as `grade` tape rows, and the presence of `world/HOLD` as `hold` tape rows on every
            # change — "mentorship enters through the tape, so the judge replays" (the brief's own words).
            elif gene == "SENSE" and args[0] == "grade":
                m = re.fullmatch(r"from ask/graded", a[len("grade "):].strip())
                if not m: raise GenomeError(f"SENSE grade: cannot read {a!r} (ALPHA4-PREREG §4(d): SENSE grade from ask/graded)")
                g["declared"]["SENSE_GRADE"] = {"from": "ask/graded"}
            else:
                raise GenomeError(f"unknown gene {gene!r} ({line!r}) — the machinery does not know it; the organism does not start")
        except (IndexError, ValueError) as e:
            raise GenomeError(f"{gene}: cannot read {line!r}: {e}") from e
        seen.add(gene)
    required = ["seed", "eye", "ear_letters", "retina", "meet", "theta_n", "misfires", "budget", "nmax", "kwta",
                "hebb_window", "lr", "prune_floor", "theta_m", "scale_every", "recall_k", "abstain_ratio"]
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:02 +0400 — ALPHA4-G.md task 1: `required`'s own
    # "nmax" entry is dropped ONLY when GROW is declared (his 00:17 word «no cap»); a genome declaring
    # neither NMAX nor GROW still refuses with the unchanged "genome lacks ['nmax']" message below.
    if "GROW" in g["declared"]:
        required = [k for k in required if k != "nmax"]
    missing = [k for k in required if k not in g]
    if missing:
        raise GenomeError(f"genome lacks {missing}")
    if not {"sight", "words"} <= set(g["areas"].keys()) or set(g["areas"].keys()) - {"sight", "words", "episodes"}:
        raise GenomeError(f"needs AREA sight and AREA words (G4 §3 B1: episodes from fast is also allowed), got {sorted(g['areas'])}")
    if not g["stages"]:
        raise GenomeError("no STAGE genes")
    if g["recall_k"] < 1:
        raise GenomeError("RECALL k must be >= 1")
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:02 +0400 — ALPHA4-G.md task 4: checked here,
    # post-loop (never inside CYCLE's own branch above), because GROW may be declared LATER in the genome
    # text than CYCLE — ALPHA4.genome's own DRAFT has GROW on line 93, the old-form CYCLE line on line 47.
    if "GROW" in g["declared"] and "grow_to" in g["declared"].get("CYCLE", {}):
        raise GenomeError(
            "CYCLE grow to <f> nmax then consolidate: refused under GROW — a cycle keyed on a cap that "
            "does not exist (ALPHA4-G task 4; use CYCLE consolidate when redundant > <f> of alive instead)"
        )
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
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH: a ring of the last
        # <history> cosines each cell answered CORRECTLY (Organism.__init__ allocates these on `sight` ONLY,
        # when THRESH is declared — mirrors the `traits` field's shape: None by default, a real array only
        # when the owning gene is present, so an Area that never gets one costs nothing and hashes nothing).
        self.own_band: Optional[np.ndarray] = None      # float32 (nmax, history)
        self.own_band_n: Optional[np.ndarray] = None     # int64 (nmax,) -- entries ever pushed (ring position = n % history)

    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:10 +0400 — ALPHA4-G.md task 1
    # (docs/ALPHA4-PREREG.md §2/§3): GROW unbounded's per-cell growth -- DOUBLE this Area's capacity
    # (cells/alive/misfires/own_band/own_band_n; every per-cell array `nmax`-shaped, found by grep, per
    # the brief's own instruction). Called ONLY from Organism._birth, ONLY when GROW is declared and
    # area.n has reached area.nmax -- the NMAX road never calls this (grep shows zero other call sites),
    # so it changes no byte of the old road. The live prefix [:old_nmax] is copied verbatim; the new
    # [old_nmax:new_nmax] region is zero, matching a fresh Area's own initial state (np.zeros' default).
    def grow(self) -> None:
        old = self.nmax
        new = old * 2
        cells = np.zeros((new, self.dim), dtype=np.float64); cells[:old] = self.cells
        alive = np.zeros(new, dtype=np.uint8); alive[:old] = self.alive
        misfires = np.zeros(new, dtype=np.int64); misfires[:old] = self.misfires
        self.cells, self.alive, self.misfires = cells, alive, misfires
        if self.own_band is not None:
            hist = self.own_band.shape[1]
            own_band = np.zeros((new, hist), dtype=np.float32); own_band[:old] = self.own_band
            own_band_n = np.zeros(new, dtype=np.int64); own_band_n[:old] = self.own_band_n
            self.own_band, self.own_band_n = own_band, own_band_n
        self.nmax = new
        # Area.cos()'s H-projection cache is keyed on (traits.version, self.n) -- neither changes here
        # (only capacity does), so the cache stays valid; not invalidated on purpose (TRAITS is #OFF on
        # every genome that could ever combine with GROW today, so this is unexercised either way).

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


GROW_CHUNK = 2048    # ALPHA4-G task 1: the FIXED chunk W/mask/strikes grow by under GROW — never doubling
                     # (the advisor's amendment, 2026-09-23 00:34 +0400: a doubling re-allocation holds
                     # old + new during the copy, ≈3× the matrix; a chunk costs ≈1.2×). W starts at ONE
                     # chunk (2048×2048, 32 MB for W alone) so the chunk arithmetic stays clean (2048,
                     # 4096, 6144, …) — the brief's own "capacity = 256" is for Area's per-cell arrays only.
AREA_INITIAL_CAPACITY = 256    # ALPHA4-G task 1: each Area's own starting capacity under GROW; doubles from here.



def _json_num(o):
    """json.dumps `default` for the hash and the snapshot meta: numpy integers and floats render as the Python
    number they equal (byte-identical text to a Python int/float), anything else raises as before."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

class Organism:
    """One organism: two areas, one edge matrix, counters. Flags `grow` / `wire` exist for the
    twins T-frozen (grow off after 10 cells) and T-nowire (HEBB off) — defaults ON."""

    def __init__(self, genome: Genome, *, wire: bool = True, frozen_after: Optional[int] = None):
        self.g = genome
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:12 +0400 — ALPHA4-G.md task 1: under GROW
        # (genome.nmax is None), Areas start at AREA_INITIAL_CAPACITY and double on demand (Area.grow(),
        # called from _birth); W/mask/strikes start at ONE GROW_CHUNK and grow by fixed chunks (_grow_W(),
        # also called from _birth) — DECOUPLED from Area's own doubling schedule on purpose (a huge N×N
        # matrix costs too much to double; a small per-cell array does not). Under NMAX (GROW undeclared,
        # the negative control): genome.nmax is a plain int and every one of these lines is byte-for-byte
        # what it always was — Area/W/mask/strikes never grow, `grow()`/`_grow_W()` are never called.
        self._grow = "GROW" in genome.declared
        sight_cap = AREA_INITIAL_CAPACITY if self._grow else genome.nmax
        words_cap = AREA_INITIAL_CAPACITY if self._grow else genome.nmax
        w_cap = GROW_CHUNK if self._grow else genome.nmax
        self.sight = Area("sight", genome.sight_dim(), sight_cap)
        self.words = Area("words", genome.words_dim(), words_cap)
        self.W = np.zeros((w_cap, w_cap), dtype=np.float64)     # sight × words
        self.mask = np.zeros((w_cap, w_cap), dtype=np.uint8)
        self.strikes = np.zeros((w_cap, w_cap), dtype=np.uint8)
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
        # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400): SURPRISE's "cheap moment"
        # counter — a would-be novelty birth refused because this glance was CONFIRMED. Same reasoning as
        # moments_sight_only immediately above: a plain attribute, never a self.c key, so state_hash is
        # unmoved for every genome that never declares SURPRISE (or never confirms).
        self.births_skipped_confirmed = 0
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #1): allocated on `sight` ONLY, only when declared -- an undeclared THRESH leaves Area.own_band at None,
        # touching no byte of anything (`moment()`'s push is gated on this same presence, one line below).
        if "THRESH" in genome.declared:
            hist = int(genome.declared["THRESH"]["history"])
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:12 +0400 — ALPHA4-G.md task 1: reads
            # `self.sight.nmax` (the Area's OWN just-allocated capacity — sight_cap above) rather than
            # `genome.nmax` directly, which is None under GROW and would crash `np.zeros((None, hist))`.
            # Under NMAX, self.sight.nmax == genome.nmax always (sight_cap was set to it two lines above
            # this method's own start), so this is byte-identical to the old read for the negative control.
            self.sight.own_band = np.zeros((self.sight.nmax, hist), dtype=np.float32)
            self.sight.own_band_n = np.zeros(self.sight.nmax, dtype=np.int64)
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:35 +0400 — ALPHA4-G.md task 3: the
        # regeneration counter. DEVIATION FROM THE BRIEF'S LITERAL WORDING, raised here and in the report:
        # the brief says "counted in self.c[\"budget_regenerated\"]"; a FIRST attempt at exactly that MOVED
        # test_pin_skeleton.py's pin for G4-skeleton.genome — a genome that declares the OLD, no-regen
        # BUDGET form and never touches this feature at all (caught RED by the suite, not by inspection).
        # `self.c` is initialised in __init__ for EVERY Organism regardless of genome, so an unconditional
        # `self.c["budget_regenerated"] = 0` moves json.dumps(self.c)'s bytes — hence state_hash — for every
        # genome on disk, exactly the anti-pattern `moments_sight_only`/`births_skipped_confirmed` (above)
        # exist to avoid. Kept as a plain attribute instead, same reasoning as those two: state_hash is
        # unmoved for every genome whose BUDGET line carries no regenerate clause (budget_regen_every is
        # None) — which is every genome on disk before this task, G4-skeleton.genome included. A genome
        # that DOES declare regen still gets a hash that moves only through `budget_left` itself (already
        # hashed) — the counter is diagnostic (STATUS/SIZING read it via creature/body.py), never a fact
        # replay identity depends on. Persisted across save/load in `meta` (never self.c), like the two
        # cursors immediately below.
        self.budget_regenerated = 0
        # ALPHA4-G.md task 4 (docs/ALPHA4-PREREG.md §2/§3): CYCLE's redundant-share form counts
        # births_refused_redundant "since the last cycle" — a plain attribute (never self.c, same reasoning
        # as moments_sight_only above: no genome without the new CYCLE form should see its hash move for
        # this), persisted across save/load in `meta` (never self.c) so a resumed life's trigger doesn't
        # spuriously fire on the WHOLE history the moment it resumes (genome/sleep.py's cycle()).
        self._cycle_baseline_redundant = 0
        # ALPHA4-G.md task 3: the moment counter at which budget last regenerated one unit — a plain
        # attribute for the same reason, persisted in `meta`. `t % 60 == 0` alone would refire on every
        # replay of the SAME moment during a sleep() replay that revisits t (it never does — org.t only
        # advances — but the explicit cursor also protects the boundary at t=0, which must never regenerate
        # before any BUDGET has ever been spent).
        self._budget_regen_last_t: Optional[int] = None

    # ------------------------------------------------------------------ arrivals & budget
    def new_arrival(self) -> None:
        """A new set of things arrives: the birth budget is fresh (BUDGET N per arrival)."""
        if self.arrivals > 0:
            self.refusals_by_arrival.append(self.c["births_refused_budget"] - sum(self.refusals_by_arrival))
        self.arrivals += 1
        self.budget_left = self.g.budget

    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:12 +0400 — ALPHA4-G.md task 3
    # (docs/ALPHA4-PREREG.md §2/§3): the anti-flood LAW as a RATE, never a ceiling. Called from the tail of
    # both moment() and moment_sight() (after `self.t += 1`, beside SCALE's own `self.t % scale_every`
    # check — the same place a per-moment homeostasis tick belongs) so a replayed moment (sleep()'s replay
    # loop calls org.moment() like any live one) regenerates budget too, "a replay is not exempt from
    # BUDGET" (the brief's own words for the birth side; regeneration is the same law read the other way).
    # `budget_regen_every` is None for every genome that never declares the trailing clause — the OLD
    # "BUDGET N per arrival" form — so this method is a no-op, byte-for-byte, for every genome on disk
    # before this task (budget_left is never touched here; self.budget_regenerated stays 0 forever).
    def _maybe_regen_budget(self) -> None:
        every = self.g.budget_regen_every
        if every is None or every <= 0:
            return
        if self.t % every != 0 or self.t == self._budget_regen_last_t:
            return
        self._budget_regen_last_t = self.t
        if self.budget_left < self.g.budget:
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:12 +0400 — ALPHA4-G.md task 3: CAP the
            # added amount so a regen tick can never push budget_left past the genome's own per-arrival
            # BUDGET (a rate, never a ceiling ITSELF exceeded) — found RED by a toy with an absurdly fast
            # regen (100 per 1 moment) landing budget_left at 54 against a declared cap of 5. budget_
            # regenerated counts the REAL amount added, never the requested-but-capped surplus.
            added = min(self.g.budget_regen_n, self.g.budget - self.budget_left)
            self.budget_left += added
            self.budget_regenerated += added

    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:13 +0400 — ALPHA4-G.md task 1: W/mask/strikes
    # grow by a FIXED chunk along ONE axis (0 = sight rows, 1 = words columns), decoupled from either
    # Area's own doubling schedule. Called only from _birth, only under GROW, only when a live cell id is
    # about to be written outside the current shape — the live block is copied into the new, bigger
    # zero-filled arrays; nothing beyond the live block is ever nonzero (the state_hash invariant Builder F
    # already established for the live-block hash holds just as well across a chunk boundary).
    def _grow_W(self, axis: int) -> None:
        shape = list(self.W.shape)
        shape[axis] += GROW_CHUNK
        shape = tuple(shape)
        W = np.zeros(shape, dtype=np.float64); mask = np.zeros(shape, dtype=np.uint8); strikes = np.zeros(shape, dtype=np.uint8)
        sl = tuple(slice(0, s) for s in self.W.shape)
        W[sl] = self.W; mask[sl] = self.mask; strikes[sl] = self.strikes
        self.W, self.mask, self.strikes = W, mask, strikes

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
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:15 +0400 — ALPHA4-G.md task 1: under GROW,
        # a full Area GROWS instead of refusing — births_refused_nmax stays 0 and is still written (the
        # SIZING mark reads it, PREREG §5). Under NMAX (GROW undeclared, self._grow False): byte-for-byte
        # the old refusal, untouched.
        if area.n >= area.nmax:
            if self._grow:
                area.grow()
            else:
                self.c["births_refused_nmax"] += 1
                return None
        if "CYCLE" in self.g.declared and "grow_to" in self.g.declared["CYCLE"]:
            # G4 §3 B7: CYCLE's SOFT ceiling — refuse once ALIVE cells reach grow_to*NMAX, same counter
            # as the hard cap. This does NOT reuse ids (advisor review: reusing a dead slot's id would
            # corrupt questions.build_ledgers, which unions every id's birth history forever — a reborn
            # id would inherit a retired cell's old "born on X" facts). cycle() (genome/sleep.py) lowers
            # ALIVE count via a real merge pass, which reopens this gate with FRESH ids from here on;
            # area.n (ever-born) never decreases, so the array's real NMAX ceiling is still the only
            # hard limit, one-shot per id, exactly as it always was. A genome that never declares CYCLE
            # (G1.genome, G4-skeleton.genome — the pin) never evaluates this branch at all.
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:15 +0400 — ALPHA4-G.md task 4: gated
            # on `"grow_to" in declared["CYCLE"]` (the OLD form only) — the new "share" form has no
            # birth-side ceiling at all (redundancy is a CONSOLIDATION trigger, not a cap; GROW's whole
            # point is that nothing refuses for room). The parser already refuses GROW + the old form
            # together (a cycle keyed on a cap that does not exist), so `self.g.nmax` below is never None
            # on this line.
            ceiling = float(self.g.declared["CYCLE"]["grow_to"]) * self.g.nmax
            if self.total_cells() >= ceiling:
                self.c["births_refused_nmax"] += 1
                return None
        if self.budget_left <= 0:
            self.c["births_refused_budget"] += 1
            return None
        cid = area.n
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:15 +0400 — ALPHA4-G.md task 1: grow
        # W/mask/strikes (the FIXED +2048 chunk, decoupled from Area's own doubling) BEFORE this cid is
        # ever written into them — moment()'s _hebb runs immediately after a birth and can wire an edge to
        # THIS SAME cid (a newborn is a winner in its own birth moment, _resonate's own law), so the shape
        # must already be correct by the time _birth returns. A `while` (not `if`): the growth-mechanics
        # unit tests call area.grow() directly, which can make `cid` land more than one chunk past the
        # CURRENT W shape in principle; ordinary play through _birth only ever needs one chunk at a time.
        if self._grow:
            axis = 0 if area is self.sight else 1
            while cid >= self.W.shape[axis]:
                self._grow_W(axis)
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

    def _resonate(self, area: Area, x: np.ndarray, confirm: bool = False) -> List[int]:
        """BIRTH novelty + KWTA: births a cell if nothing resonates (cos < THETA_N), then returns
        the winners (top KWTA alive cells by cosine; a newborn is a winner in its birth moment).
        L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400): `confirm=True` (SURPRISE's
        cheap moment) refuses the would-be novelty birth instead of taking it — counted on
        births_skipped_confirmed (a plain attribute, never self.c — see __init__). Default False is
        byte-identical to every call site before this edit."""
        if area.n == 0 or float(area.cos(x).max()) < self._theta(area):
            if confirm:
                self.births_skipped_confirmed += 1
            else:
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
    def moment(self, x_s: np.ndarray, x_w: np.ndarray, lr_scale: float = 1.0, confirm: bool = False) -> Tuple[List[int], List[int]]:
        """G4 §3 B6: `lr_scale` (default 1.0, exact — `self.g.lr * 1.0 == self.g.lr` in IEEE754, so the
        pin is untouched) scales DELTA's learning rate for this moment only (PREDICT's `modulate`, B6).
        Returns (S, T), the final sight/words winners of this moment (after any misfire birth) — a NEW
        return value (moment() returned None before this gene); every existing caller discards it as a
        bare statement, so this is additive. genome/predict.py's Predictor reads S to know what to
        expect next.

        L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 18:3x +0400): `confirm=True` (default
        False, byte-identical to every existing call) is SURPRISE's cheap moment — "HEBB/DELTA only, no
        birth, no think item" (the brief's own words): `_resonate` refuses the novelty birth (above), and
        MISFIRE/PRUNE/MERGE — every mechanism that can birth an error cell, strike a misfire, or retire a
        cell — is skipped whole, not just the birth inside it. HEBB/DELTA still run on whatever already-
        resonating winners S/T this moment finds, exactly as an ordinary moment's wiring step."""
        S = self._resonate(self.sight, x_s, confirm=confirm)
        T = self._resonate(self.words, x_w, confirm=confirm)
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #1): read BEFORE this moment's own wiring below touches W -- "correctly" means the cell's ESTABLISHED
        # answer (from PAST training), never the answer this same glance is about to create (ADAPTS: a passive
        # read of existing state, no new learning). S[0]/T[0] are the winning cells: `_resonate` returns
        # `order[:kwta]` filtered, which preserves the cosine-descending order, so S[0] (if any) is the top
        # sight winner and T[0] the top word winner -- "the winning sight cell" / "the word cell of the moment's
        # word" (the brief's own words).
        # edit: Claude (Fable 5.1), 2026-09-22 19:5x +0400 — the A×B SEAM (tests/creature/test_life_seams.py): a CONFIRMED glance (SURPRISE's
        # cheap moment) is not an ANSWER — it never feeds the cell's own band, or the band fills with confirmed (high) cosines and the p5
        # floor drifts up. Found RED by the seam test on the merged bytes before this guard existed (6 != 5).
        if self.sight.own_band is not None and S and T and not confirm:
            s0 = S[0]
            if self._answer_of(self.sight, s0) == T[0]:
                self._own_band_push(s0, float(self.sight.cos(x_s)[s0]))
        if self.wire and self.t >= self.g.stage2_start and S and T:
            self._hebb(S, T)
            self._delta(S, T, lr=self.g.lr * lr_scale)
            if not confirm:
                S, T = self._misfire(S, T, x_s, x_w)
                self._prune(S, T)
                self._merge(self.sight, S, axis=0)
                self._merge(self.words, T, axis=1)
        self.t += 1
        if self.t % self.g.scale_every == 0:
            self._scale()
        # ALPHA4-G.md task 3: the regen tick sits beside SCALE's own per-moment homeostasis check, AFTER
        # `self.t += 1` — a replayed moment (sleep()'s replay loop calls this same moment()) ticks it too
        # ("a replay is not exempt from BUDGET", read the other way round for regeneration).
        self._maybe_regen_budget()
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
        self._maybe_regen_budget()

    def _hebb(self, S: List[int], T: List[int]) -> None:
        for s in S:
            for t in T:
                if self.mask[s, t] == 0:
                    self.mask[s, t] = 1
                    self.W[s, t] = self.g.lr                  # §10 clause 3: born at w = lr
                    self.strikes[s, t] = 0
                    self.c["edges_born"] += 1
                    self.edges_log.append((self.t, int(s), int(t)))   # edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — cast (same crash class as the merge log)

    def _delta(self, S: List[int], T: List[int], lr: Optional[float] = None) -> None:
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:20 +0400 — ALPHA4-G.md task 1: `tgt_w`/
        # `tgt_s` sized from `self.W.shape` (the axis each one actually indexes into, via `idx`) rather
        # than `self.g.nmax` — which is None under GROW (an immediate crash) and, more subtly, was already
        # only an ACCIDENT of correctness under NMAX: W is square there (shape (nmax, nmax)) so
        # `self.g.nmax == self.W.shape[1] == self.W.shape[0]` always held, but nothing enforced it was the
        # right axis being read. Under GROW, W is NOT generally square (sight/words grow independently in
        # fixed chunks) — `self.W.shape[1]` (tgt_w, indexed by `idx = self.mask[s] == 1`, a row of length
        # W.shape[1]) and `self.W.shape[0]` (tgt_s, `idx = self.mask[:, t] == 1`, a column of length
        # W.shape[0]) are the ONLY correct sizes either way. Byte-identical under NMAX (same values, same
        # dtype, same length) — the negative control.
        lr = self.g.lr if lr is None else lr
        tgt_w = np.zeros(self.W.shape[1]); tgt_w[T] = 1.0
        for s in S:
            idx = self.mask[s] == 1
            self.W[s, idx] += lr * (tgt_w[idx] - self.W[s, idx])
        tgt_s = np.zeros(self.W.shape[0]); tgt_s[S] = 1.0
        for t in T:
            idx = self.mask[:, t] == 1
            self.W[idx, t] += lr * (tgt_s[idx] - self.W[idx, t])
        for s in S:
            np.clip(self.W[s], -1.0, 1.0, out=self.W[s])
        for t in T:
            np.clip(self.W[:, t], -1.0, 1.0, out=self.W[:, t])

    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH.
    def _own_band_push(self, cid: int, cos_val: float) -> None:
        """Push one cosine into sight cell `cid`'s own ring (its LAST `history` correctly-answered
        glances). Only ever called when `self.sight.own_band is not None` (THRESH declared)."""
        band, n = self.sight.own_band, self.sight.own_band_n
        hist = band.shape[1]
        band[cid, int(n[cid] % hist)] = np.float32(cos_val)
        n[cid] += 1

    def own_floor(self, cid: int) -> float:
        """L-6: a sight cell's own floor -- the p5 of its own band history when that history holds >= 5
        entries, else the genome's THETA_N (also the answer when THRESH is undeclared at all, or `cid`
        has never pushed anything yet)."""
        band, n = self.sight.own_band, self.sight.own_band_n
        if band is None or int(n[cid]) < 5:
            return self.g.theta_n
        hist = band.shape[1]
        count = int(n[cid])
        data = band[cid] if count >= hist else band[cid, :count]
        return float(np.percentile(data, 5))

    def _answer_of(self, area: Area, cid: int) -> Optional[int]:
        row = self.W[cid] if area is self.sight else self.W[:, cid]
        m = self.mask[cid] if area is self.sight else self.mask[:, cid]
        if not m.any():
            return None
        vals = np.where(m == 1, row, -np.inf)
        return int(np.argmax(vals))

    # ------------------------------------------------------------------ L-4: SURPRISE's expectation
    def expected_sight(self, xw: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """SURPRISE `floor <f> predicted mind-cell` (docs/organs/EYE.md §4 G-EYE-5, docs/organs/NEXT-
        LIFE-PLAN-2026-09-22.md §4 L-4): this canvas's EXPECTATION — "the alive sight cell with the
        largest edge to the word's cell". `xw` is the encoded word (creature/mind.py's `encode_word`);
        the word's own cell is the best-lit word cell for xw (the same lighting `_lit`/`recall` use —
        RESONATE's own cos>=THETA_N rule, so an unheard word, xw=None, or nothing yet resonating all
        read None, "unknown"); its "best sight cell" is the alive sight cell with the largest W[s, t]
        edge (mirrors `_answer_of`, but masked by `self.sight.alive` EXPLICITLY rather than relying on
        MERGE always zeroing a retired cell's row — structural, not incidental, per review). None when
        the word's own cell has no edge yet. Read-only: never births, never changes any winner — the
        SAME guarantee `recall()`/`_lit()` give; called from creature/mind.py BEFORE `Organism.moment()`
        runs for this canvas, so it can never see a cell this very canvas is about to birth."""
        if xw is None or self.words.n == 0:
            return None
        lit, _c = self._lit(self.words, xw)
        if not lit:
            return None
        t = lit[0]                              # the word's own best-lit cell (RESONATE's own top winner)
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:22 +0400 — ALPHA4-G.md task 1 (the
        # advisor's review): under GROW, `self.mask[:, t]` (length W.shape[0], the sight axis's CURRENT
        # chunked capacity) and `self.sight.alive` (length sight.nmax, the Area's own DOUBLED capacity) can
        # diverge in size the moment the two schedules disagree — ANDing them raw then raises ValueError.
        # Slicing both to `self.sight.n` (the live count — always <= both capacities, by construction: no
        # cell id >= n is ever written into either array) fixes it and changes no answer under NMAX, where
        # every index >= n reads mask=0 anyway (the AND already excluded it; slicing just stops scanning
        # the now-larger padding zone).
        n_s = self.sight.n
        row = self.W[:, t][:n_s]
        m = (self.mask[:, t] == 1)[:n_s] & (self.sight.alive[:n_s] == 1)
        if not m.any():
            return None
        s = int(np.argmax(np.where(m, row, -np.inf)))
        return self.sight.cells[s].copy()

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
                self.c["edges_pruned"] += int(k)   # edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — a numpy count in self.c is a numpy int forever: cast

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
                self.merges.append((self.t, area.name, int(a), int(b)))   # edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — numpy ids cast: json.dumps in state_hash crashed the mind at its 2nd sleep (alpha4-pre-1, seq 2604) — the FIRST real cycle() this road ever ran

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

    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/ANSWER (docs/briefs/LIFE-A-ANSWER-SELF.md
    # #2): one shared helper, called at every recall()/recall_many() return site, so the grade formula is
    # written in exactly one place. `ref_cell`: the lit cell the answer/abstain actually rests on for every
    # reason but "novel" (where `lit` is None by design and the caller passes the nearest ALIVE sight cell
    # instead — genome/think.py:_nearest_in's own algorithm: raw cosine argmax over the alive block; mirrored
    # here rather than imported, since think.py imports Organism from this module and the reverse import would
    # be circular — raised in the report, not silently substituted). `cos_val`: the query's cosine to that
    # cell — already computed by the caller as `result["cos"]` for every branch.
    def _attach_grade(self, result: Dict[str, object], side: str, ref_cell: Optional[int]) -> None:
        if "ANSWER" not in self.g.declared or side != "sight" or ref_cell is None:
            result["grade"] = None; result["own_floor"] = None; result["resembles_cell"] = None
            return
        own_floor = self.own_floor(ref_cell)
        cos_val = float(result["cos"])
        unknown_below = float(self.g.declared["ANSWER"]["unknown_below"])
        if cos_val >= own_floor:
            grade = "sure"
        elif cos_val >= unknown_below:
            grade = "unsure"
        else:
            grade = "unknown"
        result["grade"] = grade; result["own_floor"] = own_floor; result["resembles_cell"] = ref_cell

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
            nearest = int(np.argmax(c)) if len(c) else None   # L-6: the nearest ALIVE cell by raw cosine, for grading only -- `lit` itself stays None
            result = {"cell": None, "reason": "novel", "lit": None, "best": 0.0, "second": 0.0, "cos": best_cos, **ranked([])}
            self._attach_grade(result, side, nearest)
            return result
        lit_set = set(lit)
        cands: List[Tuple[float, int, int]] = []          # (edge, other cell, lit cell)
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:23 +0400 — ALPHA4-G.md task 1 (the
        # advisor's review): `other.n`, read once — under GROW, a mask row/column (W's chunked axis) and
        # `other.alive` (that Area's own doubled capacity) can have different lengths; ANDing them raw
        # raises ValueError the moment the two schedules diverge. Slicing both to the live count fixes it
        # and is byte-identical under NMAX (see expected_sight's own comment, same reasoning).
        n_o = other.n
        for l in lit:
            row = (self.W[l] if side == "sight" else self.W[:, l])[:n_o]
            m = ((self.mask[l] if side == "sight" else self.mask[:, l]) == 1)[:n_o]
            m &= other.alive[:n_o] == 1
            for j in np.flatnonzero(m):
                v = float(row[j])
                if v > 0.0:
                    cands.append((v, int(j), l))
        if not cands:
            result = {"cell": None, "reason": "noedge", "lit": lit[0], "best": 0.0, "second": 0.0, "cos": float(c[lit[0]]), **ranked(cands)}
            self._attach_grade(result, side, lit[0])
            return result
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
            result = {"cell": None, "reason": "ratio", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), **ranked(cands)}
            self._attach_grade(result, side, best_l)
            return result
        close = self._margin_close(side, other, best_id, {l: float(c[l]) for l in lit})
        if close is not None:
            result = {"cell": None, "reason": "close", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), "margin": close, **ranked(cands)}
            self._attach_grade(result, side, best_l)
            return result
        result = {"cell": best_id, "reason": "answer", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l]), **ranked(cands)}
        self._attach_grade(result, side, best_l)
        return result

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
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/ANSWER: the nearest ALIVE cell
        # across every glance, tracked SEPARATELY from `best_cos` (whose own 0.0 floor is untouched, an
        # existing field) so the single-glance case (`recall_many(side,[x]) == recall(side,x)`) always picks
        # the same reference cell `recall()`'s own `argmax(c)` would, even at a boundary cosine (#171's class:
        # reusing the floored field here would silently pick no cell some glances actually resonated).
        nearest_cell: Optional[int] = None; nearest_val = float("-inf")
        evidence: Dict[int, Tuple[float, int]] = {}                       # other cell -> (summed evidence, lit cell of its first strongest edge)
        n_o = other.n   # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:24 +0400 — ALPHA4-G.md task 1: recall()'s own fix, mirrored here.
        for x in xs:
            lit, c = self._lit(area, x)
            if len(c):
                cur_max = float(c.max())
                best_cos = max(best_cos, cur_max)
                if cur_max > nearest_val:
                    nearest_val = cur_max
                    nearest_cell = int(np.argmax(c))
            if not lit:
                continue
            for l in lit:
                if l not in cos_of:
                    lit_union.append(l); cos_of[l] = float(c[l])
            per_j: Dict[int, Tuple[float, int]] = {}
            for l in lit:
                row = (self.W[l] if side == "sight" else self.W[:, l])[:n_o]
                m = ((self.mask[l] if side == "sight" else self.mask[:, l]) == 1)[:n_o]
                m &= other.alive[:n_o] == 1
                for j in np.flatnonzero(m):
                    v = float(row[j]); j = int(j)
                    if v > 0.0 and (j not in per_j or v > per_j[j][0]):
                        per_j[j] = (v, l)
            for j, (v, l) in per_j.items():
                e = evidence.get(j)
                evidence[j] = (v, l) if e is None else (e[0] + v, e[1])
        if not lit_union:
            result = {"cell": None, "reason": "novel", "lit": None, "best": 0.0, "second": 0.0, "cos": best_cos}
            self._attach_grade(result, side, nearest_cell)
            return result
        if not evidence:
            result = {"cell": None, "reason": "noedge", "lit": lit_union[0], "best": 0.0, "second": 0.0, "cos": cos_of[lit_union[0]]}
            self._attach_grade(result, side, lit_union[0])
            return result
        cands = sorted(evidence.items(), key=lambda kv: (-kv[1][0], kv[0]))
        best_id, (best, best_l) = cands[0]
        lit_set = set(lit_union); second = 0.0
        for j, (v, _l) in cands[1:]:
            if self._answer_of(other, j) not in lit_set:
                second = v
                break
        if second > 0.0 and second / best > self.g.abstain_ratio:
            result = {"cell": None, "reason": "ratio", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l]}
            self._attach_grade(result, side, best_l)
            return result
        close = self._margin_close(side, other, best_id, cos_of)
        if close is not None:
            result = {"cell": None, "reason": "close", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l], "margin": close}
            self._attach_grade(result, side, best_l)
            return result
        result = {"cell": best_id, "reason": "answer", "lit": best_l, "best": best, "second": second, "cos": cos_of[best_l]}
        self._attach_grade(result, side, best_l)
        return result

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
        n_s, n_w = self.sight.n, self.words.n
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH: the own-band ring, saved
        # ONLY when it exists (THRESH declared) — an old reader (or a genome without THRESH) simply never sees
        # these keys; np.load's `.files` lets `load()` below tell the two cases apart.
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:45 +0400 — ALPHA4-G.md task 1 (the
        # advisor's review, item 4): under GROW, own_band is ALSO sliced to the live prefix (same reasoning
        # as alive/misfires/W/mask/strikes below — capacity is not semantic state).
        extra = {}
        if self.sight.own_band is not None:
            extra["sight_own_band"] = self.sight.own_band[:n_s] if self._grow else self.sight.own_band
            extra["sight_own_band_n"] = self.sight.own_band_n[:n_s] if self._grow else self.sight.own_band_n
        if self._grow:
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:45 +0400 — ALPHA4-G.md task 1 (the
            # advisor's review, item 4): under GROW, save the LIVE BLOCK only — alive/misfires/W/mask/
            # strikes at full CAPACITY would be a 4.8 GB write per snapshot at the box's projected ceiling
            # (task 6), almost entirely zero padding whose only content is which chunk size the code
            # happened to use. `cells` was already sliced this way before this task (todays' `[: self.n]`);
            # this extends the same discipline to every other per-cell/edge array. Under NMAX: unchanged,
            # full arrays, below — the negative control.
            np.savez_compressed(path, sight_cells=self.sight.cells[:n_s], sight_alive=self.sight.alive[:n_s], sight_misfires=self.sight.misfires[:n_s],
                                words_cells=self.words.cells[:n_w], words_alive=self.words.alive[:n_w], words_misfires=self.words.misfires[:n_w],
                                W=self.W[:n_s, :n_w], mask=self.mask[:n_s, :n_w], strikes=self.strikes[:n_s, :n_w], **extra)
        else:
            np.savez_compressed(path, sight_cells=self.sight.cells[: self.sight.n], sight_alive=self.sight.alive, sight_misfires=self.sight.misfires,
                                words_cells=self.words.cells[: self.words.n], words_alive=self.words.alive, words_misfires=self.words.misfires,
                                W=self.W, mask=self.mask, strikes=self.strikes, **extra)
        meta = {"t": self.t, "budget_left": self.budget_left, "arrivals": self.arrivals, "c": self.c, "births": self.births, "merges": self.merges,
                "edges_log": self.edges_log, "prunes_log": self.prunes_log, "refusals_by_arrival": self.refusals_by_arrival,
                "sight_n": self.sight.n, "words_n": self.words.n, "genome_text": self.g.text, "state_hash": self.state_hash(),
                # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:45 +0400 — ALPHA4-G.md tasks 1/3/4:
                # three plain attributes kept OUT of self.c/state_hash (see their own __init__ comments)
                # but that DO need to survive a resume, or a resumed life's cycle/regen triggers see a
                # baseline of 0 and can fire on the WHOLE history the moment they resume. `.get(..., default)`
                # on load so a pre-ALPHA4-G snapshot (none of these keys) loads at the same defaults __init__
                # already sets.
                "grow": self._grow, "sight_nmax": self.sight.nmax, "words_nmax": self.words.nmax,
                "w_shape": list(self.W.shape), "budget_regenerated": self.budget_regenerated,
                "cycle_baseline_redundant": self._cycle_baseline_redundant, "budget_regen_last_t": self._budget_regen_last_t}
        path.with_suffix(".json").write_text(json.dumps(meta, default=_json_num))

    @classmethod
    def load(cls, path, genome: "Genome") -> "Organism":
        import pathlib as _pl
        path = _pl.Path(path)
        z = np.load(path.with_suffix(".npz")); meta = json.loads(path.with_suffix(".json").read_text())
        o = cls(genome)
        o.sight.n = int(meta["sight_n"]); o.words.n = int(meta["words_n"])
        if o._grow:
            # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:45 +0400 — ALPHA4-G.md task 1 (the
            # advisor's review, item 4): grow Areas/W to capacities that can hold n_s/n_w BEFORE copying
            # the saved live block in. `grow()`/`_grow_W()`'s own `while` condition (n > current capacity)
            # exactly reconstructs the capacity the SAME organism would hold had it never been saved at all
            # — verified: for a run that never saves, capacity after N births is the smallest
            # AREA_INITIAL_CAPACITY*2^k (resp. GROW_CHUNK*k) strictly greater than the n value at which the
            # LAST growth fired, which is exactly what `while n > capacity: grow()` reconstructs from n
            # alone (see the report for the worked boundary cases, n==capacity vs n==capacity+1).
            while o.sight.n > o.sight.nmax:
                o.sight.grow()
            while o.words.n > o.words.nmax:
                o.words.grow()
            while o.sight.n > o.W.shape[0]:
                o._grow_W(axis=0)
            while o.words.n > o.W.shape[1]:
                o._grow_W(axis=1)
        n_s, n_w = o.sight.n, o.words.n
        if o._grow:
            o.sight.cells[:n_s] = z["sight_cells"]; o.sight.alive[:n_s] = z["sight_alive"]; o.sight.misfires[:n_s] = z["sight_misfires"]
            o.words.cells[:n_w] = z["words_cells"]; o.words.alive[:n_w] = z["words_alive"]; o.words.misfires[:n_w] = z["words_misfires"]
            o.W[:n_s, :n_w] = z["W"]; o.mask[:n_s, :n_w] = z["mask"]; o.strikes[:n_s, :n_w] = z["strikes"]
        else:
            o.sight.cells[: o.sight.n] = z["sight_cells"]; o.sight.alive[:] = z["sight_alive"]; o.sight.misfires[:] = z["sight_misfires"]
            o.words.cells[: o.words.n] = z["words_cells"]; o.words.alive[:] = z["words_alive"]; o.words.misfires[:] = z["words_misfires"]
            o.W[:] = z["W"]; o.mask[:] = z["mask"]; o.strikes[:] = z["strikes"]
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH: restore the own-band ring
        # only when BOTH sides have it (the loading genome declares THRESH -- `o.sight.own_band is not None` --
        # AND the saved npz actually carries it). An old snapshot loaded under a new THRESH genome simply keeps
        # the freshly-allocated all-zero ring (own_band_n.any()==False); state_hash()'s own gate then reads the
        # same digest the pre-THRESH code would have written (see test_load_old_snapshot_without_own_band...).
        if o.sight.own_band is not None and "sight_own_band" in z.files:
            if o._grow:
                o.sight.own_band[:n_s] = z["sight_own_band"]; o.sight.own_band_n[:n_s] = z["sight_own_band_n"]
            else:
                o.sight.own_band[:] = z["sight_own_band"]; o.sight.own_band_n[:] = z["sight_own_band_n"]
        o.t = int(meta["t"]); o.budget_left = int(meta["budget_left"]); o.arrivals = int(meta["arrivals"]); o.c = dict(meta["c"])
        o.births = [tuple(r) for r in meta["births"]]; o.merges = [tuple(r) for r in meta["merges"]]
        o.edges_log = [tuple(r) for r in meta["edges_log"]]; o.prunes_log = [tuple(r) for r in meta["prunes_log"]]
        o.refusals_by_arrival = list(meta["refusals_by_arrival"])
        o.budget_regenerated = int(meta.get("budget_regenerated", 0))
        o._cycle_baseline_redundant = int(meta.get("cycle_baseline_redundant", 0))
        _brl = meta.get("budget_regen_last_t")
        o._budget_regen_last_t = int(_brl) if _brl is not None else None
        # edit: Claude (Sonnet 5, builder F), 2026-09-21 17:45 +0400 -- the orchestrator's follow-up task
        # (commit 412d721): the closed lives' readers (tools/verdict_g4.py's W3-2 reach control, the
        # exam) must still LOAD old-format snapshots (saved before the state_hash repair). Try the NEW
        # live-block hash first; on mismatch, try the LEGACY full-array hash (kept verbatim as
        # `_state_hash_legacy`, never deleted); refuse only when BOTH fail. A snapshot saved by either
        # generation of the code therefore loads; a genuinely corrupted one (neither digest matches)
        # still refuses loudly, by name (docs/briefs/G5-F-REPORT.md §4).
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:42 +0400 — ALPHA4-G.md task 2 (the
        # advisor's review): a THIRD generation. Every snapshot on this box today (L1-L5, seam-1, seam-2,
        # 3a, 3b) was saved under F's formula (live-block W, full-length alive/misfires/own_band) — neither
        # this task's new formula NOR the pre-F legacy one. Without this, Organism.load would refuse every
        # one of them the moment this task's state_hash landed. Tried in the order a snapshot is MOST
        # likely to have been saved under (newest code first): new -> F's -> pre-F's.
        new_hash = o.state_hash()
        if new_hash != meta["state_hash"]:
            f_hash = o._state_hash_legacy_f()
            if f_hash != meta["state_hash"]:
                legacy_hash = o._state_hash_legacy()
                if legacy_hash != meta["state_hash"]:
                    raise GenomeError(
                        f"loaded organism's state_hash {new_hash[:16]} (F's {f_hash[:16]}, legacy {legacy_hash[:16]}) "
                        f"is not the saved {meta['state_hash'][:16]}"
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
    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:40 +0400 — ALPHA4-G.md task 2
    # (docs/ALPHA4-PREREG.md §2/§3, brief line 7): `alive`/`misfires`/`own_band`/`own_band_n` sliced to the
    # LIVE prefix `[:a.n]` too — they were the arrays STILL hashed at full capacity length after builder
    # F's live-block repair (W/mask/strikes/cells already were). Under GROW this is not optional: an
    # untouched, capacity-driven padding region is now UNBOUNDED and a pure implementation artefact (which
    # chunk size the code happens to use), never semantic state — two lives that grew their capacity on
    # different schedules but hold the IDENTICAL live cells must hash identically, and hashing the full
    # array would make the digest depend on capacity, not content. THIS IS A DECLARED, UNCONDITIONAL
    # HASH-LAW CHANGE (every genome, GROW or not — see (b) below) — exactly F's own precedent, and handled
    # the same way: the OLD formula (this method's body immediately before this edit) is kept VERBATIM as
    # `_state_hash_legacy_f()`, `load()` now tries three generations in order, and the new PIN is computed
    # and reported, never written into tools/gate_g4.py's PIN or any test's PINNED_HASH_DEV — that is the
    # orchestrator's call, per F's own comment on this method, still true a paragraph below.
    #
    # THE BRIEF'S OWN FACTUAL GAP, raised here: task 2's line says alive/misfires "are the only arrays
    # hashed at full length" — false for every REAL genome on this tree (L1-L4, 3b, LIFE.genome, ALPHA4.genome
    # all declare THRESH): `own_band`/`own_band_n` are ALSO hashed at full nmax length whenever THRESH is
    # declared and at least one cosine has been pushed. Fixed here too, same reasoning, same live-prefix
    # slice — omitting it would leave a capacity artefact in every GROW life's hash the moment it answers
    # its first glance correctly.
    def state_hash(self) -> str:
        """sha256 over the fixed-dtype state arrays and the counters (mark vii, the replay gate). W/mask/
        strikes/alive/misfires/own_band are hashed only over their LIVE block/prefix -- no cell id >= n is
        ever written, so this is losslessly equivalent to hashing the full-capacity arrays, just without
        paying for the padding that can never be non-zero (MIND-MEMORY.md §4 R1; extended to alive/
        misfires/own_band by ALPHA4-G task 2 — the capacity itself is not semantic state under GROW)."""
        h = hashlib.sha256()
        for a in (self.sight, self.words):
            h.update(a.cells[: a.n].tobytes()); h.update(a.alive[: a.n].tobytes()); h.update(a.misfires[: a.n].tobytes())
            h.update(np.int64(a.n).tobytes())
        n_s, n_w = self.sight.n, self.words.n
        h.update(self.W[:n_s, :n_w].tobytes()); h.update(self.mask[:n_s, :n_w].tobytes()); h.update(self.strikes[:n_s, :n_w].tobytes())
        h.update(np.int64(self.t).tobytes()); h.update(np.int64(self.budget_left).tobytes())
        # edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — `default=_json_num`: a numpy integer/float that reaches a counter or a log renders
        # as the SAME text a Python number would (so the digest is unchanged for every existing record) instead of
        # aborting the mind mid-sleep (alpha4-pre-1's crash at its 2nd sleep, TypeError int64 — then a 5 s restart loop,
        # 10 identical crashes, until the unit was stopped by hand: #230's shape in the ONE-life template).
        h.update(json.dumps(self.c, sort_keys=True, default=_json_num).encode())
        h.update(json.dumps(self.births, default=_json_num).encode()); h.update(json.dumps(self.merges, default=_json_num).encode())
        h.update(json.dumps(self.edges_log, default=_json_num).encode()); h.update(json.dumps(self.prunes_log, default=_json_num).encode())
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/THRESH (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #1): included ONLY once at least one cell has actually pushed a cosine (`own_band_n.any()`) — an
        # untouched ring (all zero, `own_band_n` all zero) is byte-indistinguishable from "THRESH was never
        # declared", so (a) a genome that newly declares THRESH but has not yet answered anything correctly
        # hashes EXACTLY like the same genome without THRESH (test_thresh_own_band.py), and (b) an OLD (pre-
        # THRESH) snapshot loads under a NEW THRESH-declared genome without a digest mismatch, because the
        # freshly-allocated, never-restored ring also reads `any()==False`. Once real history exists, both
        # replay runs of the SAME genome+tape reach that point at the identical moment (mark vii holds).
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:55 +0400 — ALPHA4-G.md task 2: the gate
        # itself reads `own_band_n[:n].any()` (the LIVE prefix), not the full-capacity array — found by a
        # test that corrupted only the padding (own_band_n[n:] = 3) and watched the hash move anyway: a
        # full-length `.any()` flips the gate on padding-only noise, which is exactly the capacity-
        # dependence this task's whole change exists to remove. Byte-identical under NMAX (padding there
        # is just as dead, so `.any()` over the full array already agreed with `.any()` over `[:n]` for
        # every genuine run — the divergence only shows up under an adversarial corruption of the padding
        # itself, which no real code path produces).
        n_s2 = self.sight.n
        if self.sight.own_band is not None and bool(self.sight.own_band_n[:n_s2].any()):
            h.update(self.sight.own_band[:n_s2].tobytes()); h.update(self.sight.own_band_n[:n_s2].tobytes())
        return h.hexdigest()

    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:40 +0400 — kept VERBATIM (byte-for-byte
    # state_hash()'s body as builder F left it, live-block W/mask/strikes but FULL-length alive/misfires/
    # own_band) so Organism.load can still verify every snapshot saved by every life on this box today
    # (L1-L5, seam-1, seam-2, 3a, 3b — all saved under F's formula, none under this task's new one or the
    # pre-F one). Never called from anywhere except load()'s fallback chain below.
    def _state_hash_legacy_f(self) -> str:
        """F's state_hash, PRE-ALPHA4-G (docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md): live-block W/
        mask/strikes, but alive/misfires/own_band at FULL capacity length. Exists only so Organism.load can
        accept a snapshot saved between 2026-09-21 ~20:50 and this task; every other caller uses
        state_hash()."""
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
        if self.sight.own_band is not None and bool(self.sight.own_band_n.any()):
            h.update(self.sight.own_band.tobytes()); h.update(self.sight.own_band_n.tobytes())
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
            "edges_alive": int(self.mask.sum()), "moments_sight_only": self.moments_sight_only,
            "births_skipped_confirmed": self.births_skipped_confirmed, **self.c,
        }
