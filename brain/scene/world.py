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


def scenes_for(split: str, seed: int) -> List[Scene]:
    """Every scene of one cache: train (world seed) · test / m2b / m6 (test seed) · toy-train / toy-test · stage."""
    if split == "train":
        return train_stream(seed)
    if split == "test":
        return [test_scene(seed, i) for i in range(N_TEST)]
    if split == "m2b":
        return [m2b_scene(seed, i) for i in range((len(M2B_SHAPES) + 1) * M2B_PER_SHAPE)]
    if split == "m6":
        return [m6_scene(seed, i) for i in range(M6_TWO + M6_THREE)]
    if split == "toy-train":
        return [toy_train_scene(i) for i in range(TOY_TRAIN_N)]
    if split == "toy-test":
        return [toy_test_scene(i) for i in range(TOY_TEST_N)]
    if split == "stage":
        return [stage_scene(i) for i in range(STAGE_N)]
    raise WorldError(f"no such split: {split!r}")


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
