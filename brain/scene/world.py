"""world.py — S1a «THE SCENE-TALK WORLD»: the things, the scenes, the parent's grammar, the held-outs, the truth.

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:02 +0400 — new module, written to docs/brain/r3/PREREG-R3-TONIGHT.md §S1a
«The world» (signed 2026-09-28 11:42 +0400). Every number below is the PREREG's; nothing here is chosen by the builder
except the one-line READINGS marked «declared» (each is listed in docs/brain/r3/S1A-HANDBACK.md).

The world is OUTSIDE the learner. No learner module imports this file (tests/brain/scene/test_truth_fence.py pins it with
an AST sweep and a planted offender). A scene is a SPEC (things, boxes, the parent's words, the referent) and, apart
from it, its PIXELS: the spec walks (the parent never lies; the held-outs; dax once) run over 10,000 scenes in seconds,
and the pixels are drawn only by `render_scene`.

Things are the maker world's own drawings: `genome.world.render(shape, rng, side)` (its jitter: position ±3 px of the
picture, scale 0.8–1.2, rotation ±15° where oriented, noise σ 0.05), multiplied by the colour's RGB / 255 and pasted at
their box on a black 128 × 128 ground, then the maker world's three faint clutter strokes (render_canvas's own stroke
code and constants) taken by maximum. Declared (a READING, RAISED): no canvas-wide noise is added — the PREREG names
σ 0.05 under the things (render's own words), and the ground as «a black ground with the maker world's three faint
clutter strokes».

edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:58 +0400 — PREREG-S1B1R §2 (sha 879a22fb…) with AMENDMENT 1 (sha a198f0b4…): the FRESH
test seeds and the two test sets (S1b-1's own and the fresh), and SPEAK2 (speak2_kind, speak2_pin, speak2_scene). Additive:
every generator S1b-1 drew is byte-for-byte as it was (the gate's step 2 re-draws S1b-1's caches and TESTS it).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

from genome.world import CANVAS, CLUTTER_INK, CLUTTER_STROKES, render

from brain.world.seeds import rendering_rng, substream

# ------------------------------------------------------------------------------------------------ the PREREG's numbers
SHAPES: Tuple[str, ...] = ("circle", "square", "triangle", "cross", "ring", "star")          # trained shapes (6)
COLOURS: Dict[str, Tuple[int, int, int]] = {                                                 # trained colours (5)
    "red": (230, 50, 50), "blue": (60, 90, 240), "green": (50, 200, 70), "yellow": (235, 220, 50),
    "white": (245, 245, 245)}
COLOUR_NAMES: Tuple[str, ...] = tuple(COLOURS)
PURPLE: Tuple[str, Tuple[int, int, int]] = ("purple", (150, 60, 200))                         # never appears (S1b's DECLINE)
SIZES: Dict[str, int] = {"big": 32, "small": 22}                                             # picture side, px
SIZE_NAMES: Tuple[str, ...] = tuple(SIZES)
NEVER_TAUGHT: Tuple[str, ...] = ("arrow", "wave", "diamond", "house", "tree", "cup", "key")  # never appear in training
M2B_SHAPES: Tuple[str, ...] = ("arrow", "wave", "house", "tree", "cup", "key")               # M2b's graded six (× 8)
M2B_APART: str = "diamond"                                                                   # read apart (8 items)
M2B_PER_SHAPE = 8
DAX_SHAPE, DAX_WORD = "moon", "dax"
DAX_SCENE = 2700                                  # «the 2,700th scene» (1-based) → index 2699
DAX_INDEX = DAX_SCENE - 1
HELDOUT_SEED, N_HELDOUT, MIN_PARTNERS = 20260928, 6, 3
SCENE_MIX: Tuple[Tuple[int, float], ...] = ((1, 0.4), (2, 0.4), (3, 0.2))
SEPARATION_PX = 24                                # boxes separated by ≥ 24 px (three grid cells)
WORLD_SEEDS: Tuple[int, ...] = (20261101, 20261102, 20261103)
TEST_SEEDS: Dict[int, int] = {20261101: 20261201, 20261102: 20261202, 20261103: 20261203}
TOY_SEED, STAGE_SEED = 20261099, 20261100
N_TRAIN, N_TEST = 10_000, 400
READING_POINTS: Tuple[int, ...] = (250, 500, 1_000, 2_000, 5_000, 10_000)
GATE_N, STAGE_N = 300, 300
TOY_TRAIN_N, TOY_TEST_N = 1_000, 200
M6_TWO, M6_THREE = 28, 14                          # 42 scenes, «2 or 3 things in a 2:1 mix»
# PREREG-S1B1 §4–§5 (edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:42 +0400): the three new test splits
M3_TWO, M3_THREE = 40, 20                          # M3 COMPOSE: 60 (10 per held-out pair)
SPEAK_TWO, SPEAK_THREE = 64, 32                    # SPEAK: 96
DECLINE_TWO, DECLINE_THREE = 32, 16                # DECLINE: 48 (kind A 32 · kind B 16)
_TWIN_REDRAWS = 1000
# PREREG-S1B1R §2 with AMENDMENT 1 §2, §4 (h) (edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:58 +0400): the FRESH test seeds, one per
# world seed (the graded marks are read on these alone; 2026130x are S1c's world seeds — a different role), beside S1b-1's
# own test set; SPEAK2, the NEED items: 60 THREE-thing scenes per seed in three kinds of 20.
FRESH_TEST_SEEDS: Dict[int, int] = {20261101: 20261401, 20261102: 20261402, 20261103: 20261403}
TEST_SETS: Dict[str, Dict[int, int]] = {"s1b1": TEST_SEEDS, "fresh": FRESH_TEST_SEEDS}
SPEAK2_PER_KIND = 20
SPEAK2_KINDS: Tuple[str, ...] = ("CS", "SC", "SS")                      # i 0–19 · 20–39 · 40–59
SPEAK2_KIND_TYPES: Dict[str, Tuple[str, str]] = {"CS": ("colour", "shape"), "SC": ("size", "colour"), "SS": ("size", "shape")}
_SPEAK2_TRIES = 100_000
TEMPLATES: Tuple[str, ...] = ("T1", "T2", "T3", "T4")
WORD_TYPES: Tuple[str, ...] = ("colour", "shape", "size")

# placement retries (declared: a rejection sampler; bounded, deterministic by seed)
_TRIES_PER_THING, _RESTARTS = 400, 200


class WorldError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ words and their truth
def word_type(w: str) -> str:
    if w in SHAPES or w == DAX_WORD:
        return "shape"
    if w in COLOURS:
        return "colour"
    if w in SIZES:
        return "size"
    raise WorldError(f"not a word of this world: {w!r}")


VOCAB: Tuple[str, ...] = SIZE_NAMES + COLOUR_NAMES + SHAPES + (DAX_WORD,)
SHAPE_WORDS: Tuple[str, ...] = SHAPES + (DAX_WORD,)


@dataclass(frozen=True)
class Thing:
    shape: str
    colour: str
    size: str
    top: int
    left: int

    @property
    def side(self) -> int:
        return SIZES[self.size]

    def to_dict(self) -> Dict[str, object]:
        return {"shape": self.shape, "colour": self.colour, "size": self.size, "top": self.top, "left": self.left,
                "side": self.side}


def word_true_of(w: str, t: Thing) -> bool:
    if w == DAX_WORD:
        return t.shape == DAX_SHAPE
    if w in SHAPES:
        return t.shape == w
    if w in COLOURS:
        return t.colour == w
    if w in SIZES:
        return t.size == w
    return False


def phrase_true_of(words: Sequence[str], t: Thing) -> bool:
    return all(word_true_of(w, t) for w in words)


def template_words(template: str, t: Thing) -> Tuple[str, ...]:
    """The parent's four templates (PREREG): T1 «⟨shape⟩», T2 «⟨colour⟩ ⟨shape⟩», T3 «⟨size⟩ ⟨shape⟩»,
    T4 «⟨size⟩ ⟨colour⟩ ⟨shape⟩»."""
    if template == "T1":
        return (t.shape,)
    if template == "T2":
        return (t.colour, t.shape)
    if template == "T3":
        return (t.size, t.shape)
    if template == "T4":
        return (t.size, t.colour, t.shape)
    raise WorldError(f"no such template: {template!r}")


# ------------------------------------------------------------------------------------------------ the held-outs
def heldout_pairs() -> Tuple[Tuple[str, str], ...]:
    """6 of the 30 colour × shape pairs never exist in training, drawn by the generator seeded 20260928, each shape and
    each colour keeping ≥ 3 partners. Declared: pair p ↔ (SHAPES[p // 5], COLOUR_NAMES[p % 5]); draws of 6 distinct
    pairs (Generator.choice without replacement) are repeated until the partner rule holds; the result is sorted."""
    rng = np.random.default_rng(HELDOUT_SEED)
    for _ in range(10_000):
        pick = rng.choice(len(SHAPES) * len(COLOUR_NAMES), size=N_HELDOUT, replace=False)
        pairs = [(SHAPES[int(p) // len(COLOUR_NAMES)], COLOUR_NAMES[int(p) % len(COLOUR_NAMES)]) for p in pick]
        shape_keep = {s: len(COLOUR_NAMES) - sum(1 for ps, _c in pairs if ps == s) for s in SHAPES}
        colour_keep = {c: len(SHAPES) - sum(1 for _s, pc in pairs if pc == c) for c in COLOUR_NAMES}
        if min(shape_keep.values()) >= MIN_PARTNERS and min(colour_keep.values()) >= MIN_PARTNERS:
            return tuple(sorted(pairs))
    raise WorldError("no held-out draw satisfied the partner rule in 10,000 draws")


HELDOUT: Tuple[Tuple[str, str], ...] = heldout_pairs()
ALLOWED: Tuple[Tuple[str, str], ...] = tuple((s, c) for s in SHAPES for c in COLOUR_NAMES if (s, c) not in HELDOUT)


# ------------------------------------------------------------------------------------------------ scenes (specs)
@dataclass(frozen=True)
class Scene:
    split: str
    index: int
    seed: int
    things: Tuple[Thing, ...]
    words: Tuple[str, ...]          # the parent's utterance; () when the parent is silent (every test scene)
    referent: Optional[int]         # the thing the utterance was made from (TRUTH — never a learner's input)
    template: Optional[str]

    @property
    def item_id(self) -> str:
        return f"{self.split}:{self.seed}:{self.index:05d}"

    def to_dict(self) -> Dict[str, object]:
        return {"item_id": self.item_id, "split": self.split, "index": self.index, "seed": self.seed,
                "things": [t.to_dict() for t in self.things], "words": list(self.words), "referent": self.referent,
                "template": self.template}


def box_gap(a: Thing, b: Thing) -> int:
    """The Chebyshev gap between two boxes, px (negative when they overlap). Declared reading of «separated by ≥ 24 px»:
    box_gap ≥ 24, i.e. the boxes are ≥ 24 px apart along at least one axis."""
    gy = max(b.top - (a.top + a.side), a.top - (b.top + b.side))
    gx = max(b.left - (a.left + a.side), a.left - (b.left + b.side))
    return max(gy, gx)


def _place(attrs: Sequence[Tuple[str, str, str]], rng: np.random.Generator) -> Tuple[Thing, ...]:
    """Positions uniform over the canvas (top-left in [0, CANVAS − side]) for each thing in order, a thing redrawn until
    it keeps ≥ 24 px from every thing placed before it; after _TRIES_PER_THING failures the whole scene is re-placed."""
    for _restart in range(_RESTARTS):
        placed: List[Thing] = []
        for shape, colour, size in attrs:
            side = SIZES[size]
            for _try in range(_TRIES_PER_THING):
                top, left = (int(v) for v in rng.integers(0, CANVAS - side + 1, size=2))
                cand = Thing(shape, colour, size, top, left)
                if all(box_gap(cand, p) >= SEPARATION_PX for p in placed):
                    placed.append(cand)
                    break
            else:
                break
        if len(placed) == len(attrs):
            return tuple(placed)
    raise WorldError(f"could not place {attrs} with ≥ {SEPARATION_PX} px between boxes")


def _trained_attrs(rng: np.random.Generator) -> Tuple[str, str, str]:
    """(shape, colour, size): the pair uniform over the 24 ALLOWED pairs (≡ rejection of the held-out six from the
    uniform 6 × 5 draw), the size uniform over big/small."""
    s, c = ALLOWED[int(rng.integers(len(ALLOWED)))]
    return s, c, SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))]


def _n_things(rng: np.random.Generator) -> int:
    ns = [n for n, _p in SCENE_MIX]
    ps = [p for _n, p in SCENE_MIX]
    return int(ns[int(rng.choice(len(ns), p=ps))])


def _parent(things: Sequence[Thing], rng: np.random.Generator) -> Tuple[Tuple[str, ...], int, str]:
    """ONE true utterance: a thing uniformly among the things in view, a template uniformly among T1–T4."""
    ref = int(rng.integers(len(things)))
    tpl = TEMPLATES[int(rng.integers(len(TEMPLATES)))]
    return template_words(tpl, things[ref]), ref, tpl


def train_scene(seed: int, index: int) -> Scene:
    """The index-th training scene of world seed `seed` (0-based). Scene 2,700 (index 2699) is the ONE meeting: the moon
    alone with one trained thing, and the parent says «dax». Every other scene: 1/2/3 things in the mix 0.4/0.4/0.2."""
    rng = substream(seed, f"scene:train:{index}")
    if index == DAX_INDEX:
        other = _trained_attrs(rng)
        moon = (DAX_SHAPE, COLOUR_NAMES[int(rng.integers(len(COLOUR_NAMES)))], SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])
        pos = int(rng.integers(2))
        attrs = [other, moon] if pos == 1 else [moon, other]
        things = _place(attrs, rng)
        return Scene("train", index, seed, things, (DAX_WORD,), pos, None)
    n = _n_things(rng)
    things = _place([_trained_attrs(rng) for _ in range(n)], rng)
    words, ref, tpl = _parent(things, rng)
    return Scene("train", index, seed, things, words, ref, tpl)


def train_stream(seed: int, n: int = N_TRAIN) -> List[Scene]:
    return [train_scene(seed, i) for i in range(n)]


def test_scene(test_seed: int, index: int) -> Scene:
    """A regular test scene (M1 and M2a's items are built from it by marks.py): the training mix, the parent silent."""
    rng = substream(test_seed, f"scene:test:{index}")
    n = _n_things(rng)
    things = _place([_trained_attrs(rng) for _ in range(n)], rng)
    return Scene("test", index, test_seed, things, (), None, None)


def m2b_scene(test_seed: int, index: int) -> Scene:
    """M2b: ONE never-taught shape alone, through the same render road, in the trained colours and sizes (declared: the
    colour and size uniform per item); the parent silent. Items 0..47 are the graded six × 8 (shape = index // 8);
    items 48..55 are «diamond» × 8, read apart."""
    shapes = M2B_SHAPES + (M2B_APART,)
    if not 0 <= index < len(shapes) * M2B_PER_SHAPE:
        raise WorldError(f"m2b index {index} out of range")
    shape = shapes[index // M2B_PER_SHAPE]
    rng = substream(test_seed, f"scene:m2b:{index}")
    attrs = [(shape, COLOUR_NAMES[int(rng.integers(len(COLOUR_NAMES)))], SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])]
    return Scene("m2b", index, test_seed, _place(attrs, rng), (), None, None)


def m6_scene(test_seed: int, index: int) -> Scene:
    """M6: «dax» (a moon) in 42 scenes with 2 or 3 things in a 2:1 mix (items 0..27 two things, 28..41 three things);
    the others are trained things; the moon's colour and size uniform over the trained ones (declared); the phrase «dax»."""
    if not 0 <= index < M6_TWO + M6_THREE:
        raise WorldError(f"m6 index {index} out of range")
    n = 2 if index < M6_TWO else 3
    rng = substream(test_seed, f"scene:m6:{index}")
    others = [_trained_attrs(rng) for _ in range(n - 1)]
    moon = (DAX_SHAPE, COLOUR_NAMES[int(rng.integers(len(COLOUR_NAMES)))], SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])
    pos = int(rng.integers(n))
    attrs = others[:pos] + [moon] + others[pos:]
    return Scene("m6", index, test_seed, _place(attrs, rng), (DAX_WORD,), pos, None)


# ------------------------------------------------------------------------------------------------ S1b-1's new splits
# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:42 +0400 — PREREG-S1B1 §1 «New, per test seed»: M3 / SPEAK / DECLINE scenes from
# named substreams of the TEST seed, placed by _place (≥ 24 px), drawn by render_scene, the parent silent. S1a's split
# functions above are untouched (their specs and canvases are the S1a caches', TESTED at the gate). A thing whose triple
# (shape, colour, size) equals another's is a TWIN and the scene's attributes are redrawn from the SAME generator. The
# item kinds are functions of the index (m3_kind, decline_kind) — no Scene field is added, so S1a's truth rows stay equal.
def _has_twin(attrs: Sequence[Tuple[str, str, str]]) -> bool:
    return len(set(attrs)) < len(attrs)


def m3_kind(index: int) -> str:
    """The distractor kind of M3 item `index`: 2-thing i even «colour» (a distractor shares the target's colour — the
    SHAPE word is necessary), 2-thing i odd «shape» (shares the shape — the COLOUR word is necessary), 3-thing «both»."""
    if index < M3_TWO:
        return "colour" if index % 2 == 0 else "shape"
    return "both"


def decline_kind(index: int) -> str:
    """DECLINE item `index`: kind B = 2-thing i even (the distractor shares the target's shape and size — the colour is
    the only difference, the right act is to decline); kind A = 2-thing i odd and every 3-thing item (other shapes)."""
    return "B" if (index < DECLINE_TWO and index % 2 == 0) else "A"


def m3_scene(test_seed: int, index: int) -> Scene:
    """M3 COMPOSE (§4): the target's pair = HELDOUT[index mod 6] (never in training), its size uniform; distractors are
    trained (ALLOWED) things, sizes uniform — a colour-sharer's shape uniform among the shapes allowed with the target's
    colour, a shape-sharer's colour uniform among the colours allowed with its shape (neither can be the target's pair,
    which is held out). Declared draw order: the target's size, the distractors ([colour-sharer, shape-sharer] for
    3-thing), the target's index among the things, the placement. The phrase «⟨colour⟩ ⟨shape⟩» and the target ride on
    the scene as its words and referent (the question and its truth, as the M6 split carries them)."""
    if not 0 <= index < M3_TWO + M3_THREE:
        raise WorldError(f"m3 index {index} out of range")
    rng = substream(test_seed, f"scene:m3:{index}")
    shape, colour = HELDOUT[index % len(HELDOUT)]
    target = (shape, colour, SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])

    def colour_sharer() -> Tuple[str, str, str]:
        shapes = [sh for sh in SHAPES if (sh, colour) in ALLOWED]
        return (shapes[int(rng.integers(len(shapes)))], colour, SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])

    def shape_sharer() -> Tuple[str, str, str]:
        colours = [c for c in COLOUR_NAMES if (shape, c) in ALLOWED]
        return (shape, colours[int(rng.integers(len(colours)))], SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))])

    kind = m3_kind(index)
    others = [colour_sharer()] if kind == "colour" else [shape_sharer()] if kind == "shape" else [colour_sharer(), shape_sharer()]
    n = len(others) + 1
    pos = int(rng.integers(n))
    attrs = others[:pos] + [target] + others[pos:]
    if _has_twin(attrs):
        raise WorldError("an M3 scene with a twin — impossible, the target's pair is held out")
    return Scene("m3", index, test_seed, _place(attrs, rng), (colour, shape), pos, "T2")


def speak_scene(test_seed: int, index: int) -> Scene:
    """SPEAK (§5): 2 things (i < 64) or 3, trained things only, twins redrawn from the same generator; the target a thing
    drawn uniformly (the scene's referent); the learner hears nothing. Declared draw order: attributes (redrawn while a
    twin), the placement, the target."""
    if not 0 <= index < SPEAK_TWO + SPEAK_THREE:
        raise WorldError(f"speak index {index} out of range")
    rng = substream(test_seed, f"scene:speak:{index}")
    n = 2 if index < SPEAK_TWO else 3
    for _ in range(_TWIN_REDRAWS):
        attrs = [_trained_attrs(rng) for _ in range(n)]
        if not _has_twin(attrs):
            break
    else:
        raise WorldError("no twin-free SPEAK scene drawn")
    things = _place(attrs, rng)
    return Scene("speak", index, test_seed, things, (), int(rng.integers(n)), None)


def decline_scene(test_seed: int, index: int) -> Scene:
    """DECLINE (§5): the target is PURPLE (never in training) with a trained shape and a uniform size; kind B (2-thing,
    i even): the distractor shares the target's shape and size, its colour uniform among the colours allowed with that
    shape; kind A: trained distractors of OTHER shapes (a trained draw rejected while its shape is the target's). Twins
    redrawn from the same generator. Declared draw order: the target's shape and size, the distractors, the target's
    index, the placement."""
    if not 0 <= index < DECLINE_TWO + DECLINE_THREE:
        raise WorldError(f"decline index {index} out of range")
    rng = substream(test_seed, f"scene:decline:{index}")
    n = 2 if index < DECLINE_TWO else 3
    kind = decline_kind(index)
    for _ in range(_TWIN_REDRAWS):
        shape = SHAPES[int(rng.integers(len(SHAPES)))]
        size = SIZE_NAMES[int(rng.integers(len(SIZE_NAMES)))]
        target = (shape, PURPLE[0], size)
        if kind == "B":
            colours = [c for c in COLOUR_NAMES if (shape, c) in ALLOWED]
            others = [(shape, colours[int(rng.integers(len(colours)))], size)]
        else:
            others = []
            for _k in range(n - 1):
                for _r in range(_TWIN_REDRAWS):
                    a = _trained_attrs(rng)
                    if a[0] != shape:
                        break
                others.append(a)
        if not _has_twin(others + [target]):
            break
    else:
        raise WorldError("no twin-free DECLINE scene drawn")
    pos = int(rng.integers(n))
    attrs = others[:pos] + [target] + others[pos:]
    return Scene("decline", index, test_seed, _place(attrs, rng), (), pos, None)


# ------------------------------------------------------------------------------------------------ S1b-1R's NEED items
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 15:58 +0400 — PREREG-S1B1R §2 as AMENDMENT 1 §2 rules it (the S1b-1R builder's RAISED
# clause: a need for two words takes three things). S1b-1's generators above are untouched.
def speak2_kind(index: int) -> str:
    """SPEAK2 item `index`'s kind: CS (i 0–19; «⟨colour⟩ ⟨shape⟩» the only unique 2-word phrase), SC (i 20–39; «⟨size⟩
    ⟨colour⟩»), SS (i 40–59; «⟨size⟩ ⟨shape⟩»)."""
    if not 0 <= index < SPEAK2_PER_KIND * len(SPEAK2_KINDS):
        raise WorldError(f"speak2 index {index} out of range")
    return SPEAK2_KINDS[index // SPEAK2_PER_KIND]


def _unique_of(words: Sequence[str], things: Sequence[Thing], target: int) -> bool:
    """True of the target and of no other thing in view (order-free, the world's truth)."""
    if not phrase_true_of(words, things[target]):
        return False
    return not any(phrase_true_of(words, u) for k, u in enumerate(things) if k != target)


def speak2_pin(things: Sequence[Thing], target: int, kind: str) -> Dict[str, object]:
    """AMENDMENT 1 §2's pins on one scene: the §2 pin (no single word of the target unique; some 2-word phrase unique) AND
    the kind's pin (the kind's 2-word phrase unique; the kind's other two 2-word phrases NOT unique). Returns every word's
    and pair's uniqueness and `pass`."""
    t = things[target]
    word = {"size": t.size, "colour": t.colour, "shape": t.shape}
    single = {typ: _unique_of([w], things, target) for typ, w in word.items()}
    pairs = {(a, b): _unique_of([word[a], word[b]], things, target)
             for a, b in (("size", "colour"), ("size", "shape"), ("colour", "shape"))}
    own = SPEAK2_KIND_TYPES[kind]
    key = own if own in pairs else (own[1], own[0])
    ok = (not any(single.values())) and pairs[key] and not any(v for k, v in pairs.items() if k != key)
    return {"single": single, "pairs": {f"{a}+{b}": v for (a, b), v in pairs.items()}, "kind": kind,
            "kind_pair": f"{key[0]}+{key[1]}", "pass": bool(ok)}


def speak2_scene(test_seed: int, index: int) -> Scene:
    """SPEAK2 (PREREG-S1B1R §2 / AMENDMENT 1 §2): THREE trained things, no twins; the item is drawn WHOLE — the target and
    both distractors, each a trained draw (`_trained_attrs`) — by REJECTION from its own substream `scene:speak2:<i>`
    until `speak2_pin` holds for its kind (so the target's draw is uniform only over the trained things that admit the
    kind; the achieved mix is printed per kind). Declared draw order: [target, distractor, distractor] per try; after
    acceptance, the target's index among the things (uniform), then the placement. The learner hears nothing."""
    kind = speak2_kind(index)
    rng = substream(test_seed, f"scene:speak2:{index}")
    for _ in range(_SPEAK2_TRIES):
        attrs = [_trained_attrs(rng) for _ in range(3)]
        if _has_twin(attrs):
            continue
        if speak2_pin([Thing(s, c, z, 0, 0) for s, c, z in attrs], 0, kind)["pass"]:
            break
    else:
        raise WorldError(f"no SPEAK2 {kind} scene drawn in {_SPEAK2_TRIES} tries")
    target, others = attrs[0], attrs[1:]
    pos = int(rng.integers(3))
    attrs = others[:pos] + [target] + others[pos:]
    return Scene("speak2", index, test_seed, _place(attrs, rng), (), pos, None)


def toy_train_scene(index: int) -> Scene:
    """The toy (THE FIRST GATE 1): 1,000 ONE-thing scenes of seed 20261099, the parent speaking (no ambiguity)."""
    rng = substream(TOY_SEED, f"scene:toy-train:{index}")
    things = _place([_trained_attrs(rng)], rng)
    words, ref, tpl = _parent(things, rng)
    return Scene("toy-train", index, TOY_SEED, things, words, ref, tpl)


def toy_test_scene(index: int) -> Scene:
    """The toy's test: 200 TWO-thing scenes of the same seed, the parent silent (M1's items are built by marks.py)."""
    rng = substream(TOY_SEED, f"scene:toy-test:{index}")
    things = _place([_trained_attrs(rng) for _ in range(2)], rng)
    return Scene("toy-test", index, TOY_SEED, things, (), None, None)


def stage_scene(index: int) -> Scene:
    """Stage −1: 300 scenes of seed 20261100 in the training mix (organ facts; the parent silent)."""
    rng = substream(STAGE_SEED, f"scene:stage:{index}")
    n = _n_things(rng)
    things = _place([_trained_attrs(rng) for _ in range(n)], rng)
    return Scene("stage", index, STAGE_SEED, things, (), None, None)


def split_size(split: str) -> int:
    sizes = {"train": N_TRAIN, "test": N_TEST, "m2b": (len(M2B_SHAPES) + 1) * M2B_PER_SHAPE, "m6": M6_TWO + M6_THREE,
             "toy-train": TOY_TRAIN_N, "toy-test": TOY_TEST_N, "stage": STAGE_N,
             "m3": M3_TWO + M3_THREE, "speak": SPEAK_TWO + SPEAK_THREE, "decline": DECLINE_TWO + DECLINE_THREE,
             "speak2": SPEAK2_PER_KIND * len(SPEAK2_KINDS)}
    if split not in sizes:
        raise WorldError(f"no such split: {split!r}")
    return sizes[split]


def scenes_for(split: str, seed: int, limit: Optional[int] = None) -> List[Scene]:
    """Every scene of one cache (or its first `limit`): train (world seed) · test / m2b / m6 (test seed) · toy-train /
    toy-test · stage. Each scene is a function of (seed, index) alone, so a prefix is the full stream's prefix."""
    n = split_size(split) if limit is None else min(int(limit), split_size(split))
    make = {"train": lambda i: train_scene(seed, i), "test": lambda i: test_scene(seed, i),
            "m2b": lambda i: m2b_scene(seed, i), "m6": lambda i: m6_scene(seed, i),
            "toy-train": toy_train_scene, "toy-test": toy_test_scene, "stage": stage_scene,
            "m3": lambda i: m3_scene(seed, i), "speak": lambda i: speak_scene(seed, i),
            "decline": lambda i: decline_scene(seed, i), "speak2": lambda i: speak2_scene(seed, i)}[split]
    return [make(i) for i in range(n)]


# ------------------------------------------------------------------------------------------------ pixels
def colour_rgb(name: str) -> Tuple[int, int, int]:
    if name in COLOURS:
        return COLOURS[name]
    if name == PURPLE[0]:
        return PURPLE[1]
    raise WorldError(f"no such colour: {name!r}")


def render_scene(scene: Scene) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """(rgb uint8 CANVAS × CANVAS × 3, each thing's ink centroid (cy, cx) px). One rendering generator per scene,
    `brain.world.seeds.rendering_rng(seed, item_id)` (B1's own rule), drawn thing by thing in order, then the clutter.
    The centroid is render_canvas's own truth: the grey picture's ink-weighted mean, offset by the box."""
    rng = rendering_rng(scene.seed, scene.item_id)
    cv = np.zeros((CANVAS, CANVAS, 3), dtype=np.float64)
    cents: List[Tuple[float, float]] = []
    for t in scene.things:
        side = t.side
        pic = render(t.shape, rng, side)
        cv[t.top:t.top + side, t.left:t.left + side] = pic[:, :, None] * np.asarray(colour_rgb(t.colour), dtype=np.float64)[None, None, :] / 255.0
        tot = pic.sum()
        ys, xs = np.mgrid[0:side, 0:side]
        cy = t.top + ((ys * pic).sum() / tot if tot > 0 else side / 2)
        cx = t.left + ((xs * pic).sum() / tot if tot > 0 else side / 2)
        cents.append((float(cy), float(cx)))
    layer = Image.new("L", (CANVAS, CANVAS), 0)
    d = ImageDraw.Draw(layer)
    for _ in range(CLUTTER_STROKES):                    # genome.world.render_canvas's own three strokes
        x0, y0 = rng.uniform(0, CANVAS, size=2)
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(8, 16)
        d.line([(x0, y0), (x0 + L * math.cos(ang), y0 + L * math.sin(ang))], fill=255, width=1)
    cl = np.asarray(layer, dtype=np.float64) / 255.0 * CLUTTER_INK
    cv = np.maximum(cv, cl[:, :, None])
    rgb = np.clip(np.rint(cv * 255.0), 0, 255).astype(np.uint8)
    return rgb, cents


# ------------------------------------------------------------------------------------------------ the truth of a fixation
def fixation_thing(cell: Tuple[int, int], things: Sequence[Thing], cell_px: int = 8, margin: int = 4) -> Optional[int]:
    """GRADING ONLY. The thing a fixation cell lands on: the cell's centre pixel inside the thing's box ± 4 px — the seat's
    probe's own rule (seat_scene_probe.py `thing_of`), declared. None when it lands on no thing. With boxes ≥ 24 px apart
    the expanded boxes are ≥ 16 px apart, so the answer is unique (and two fixations on two different things are ≥ 3
    grid cells apart — tests/brain/scene/test_world.py proves both)."""
    py, px = cell[0] * cell_px + cell_px // 2, cell[1] * cell_px + cell_px // 2
    hit = [i for i, t in enumerate(things)
           if t.top - margin <= py < t.top + t.side + margin and t.left - margin <= px < t.left + t.side + margin]
    if len(hit) > 1:
        raise WorldError(f"a fixation cell {cell} lands on {len(hit)} things — the separation rule is broken")
    return hit[0] if hit else None
