"""world.py — the rung-0 world: things drawn as 24×24 grey pictures, words as letters.

edit: Claude (Fable 5.1), 2026-09-19 16:0x +04 — G0 rung 0 (docs/G0-PREREG.md §2, §10 clauses 10, 12, 14).
edit: Claude (Fable 5.1), 2026-09-19 16:37 +04 — G0b: the picture side is a parameter (32 for the sealed eye tower); «diamond», a designed near-pair to «square».

The world is OUTSIDE the organism. It renders pictures, encodes words, and hands the
runner streams of (thing, picture, word) moments. The organism never imports this file.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

SIDE = 24            # the eye: 24×24 grey (SENSE eye 24x24 grey)
HI = 96              # rendered at 96×96 then box-downsampled ×4 for clean edges
LETTERS = "abcdefghijklmnopqrstuvwxyz"
WORD_SLOTS = 8       # SENSE ear letters 8

# §10 clause 14 — shapes with an orientation get the ±15° rotation jitter
ORIENTED = {"triangle", "cross", "bar", "arrow", "wave", "house", "tree", "cup", "key", "spiral", "zog", "vex", "diamond"}
THINGS_11 = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave", "diamond"]   # G0b: + the designed near-pair
THINGS_10 = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave"]
THINGS_ARRIVAL2 = ["moon", "house", "tree", "cup", "key"]
THING_NEVER = "spiral"      # Q5: never shown
THING_PLANT = "zog"         # the plant: a made-up thing shown 5 times
THING_NULL = "vex"          # the null plant: a made-up thing shown 0 times


# ----------------------------------------------------------------------------- drawing
def _rot(points, deg, cx, cy):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in points]


def _draw(thing: str, d: ImageDraw.ImageDraw, cx: float, cy: float, s: float, deg: float) -> None:
    """Draw `thing` with ink 255 on a black canvas; centre (cx, cy), scale s, rotation deg."""
    R = lambda pts: _rot(pts, deg, cx, cy)
    if thing == "circle":
        r = 30 * s; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    elif thing == "square":
        h = 26 * s; d.polygon(R([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]), fill=255)
    elif thing == "diamond":      # G0b's designed near-pair: the square turned 45°
        h = 26 * s; d.polygon(_rot([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)], 45 + deg, cx, cy), fill=255)
    elif thing == "triangle":
        r = 34 * s
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-90, 30, 150)]
        d.polygon(R(pts), fill=255)
    elif thing == "cross":
        w, L = 6 * s, 32 * s
        d.polygon(R([(cx - L, cy - w), (cx + L, cy - w), (cx + L, cy + w), (cx - L, cy + w)]), fill=255)
        d.polygon(R([(cx - w, cy - L), (cx + w, cy - L), (cx + w, cy + L), (cx - w, cy + L)]), fill=255)
    elif thing == "ring":
        r, w = 30 * s, 7 * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        d.ellipse([cx - r + w, cy - r + w, cx + r - w, cy + r - w], fill=0)
    elif thing == "bar":
        L, w = 35 * s, 7 * s
        d.polygon(R([(cx - L, cy - w), (cx + L, cy - w), (cx + L, cy + w), (cx - L, cy + w)]), fill=255)
    elif thing == "dot":
        r = 8 * s; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    elif thing == "star":
        ro, ri = 34 * s, 14 * s
        pts = []
        for k in range(10):
            r = ro if k % 2 == 0 else ri
            a = math.radians(-90 + k * 36)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=255)
    elif thing == "arrow":
        pts = [(cx - 34 * s, cy - 6 * s), (cx + 4 * s, cy - 6 * s), (cx + 4 * s, cy - 20 * s), (cx + 34 * s, cy),
               (cx + 4 * s, cy + 20 * s), (cx + 4 * s, cy + 6 * s), (cx - 34 * s, cy + 6 * s)]
        d.polygon(R(pts), fill=255)
    elif thing == "wave":
        pts = [(cx - 34 * s + i * (68 * s / 40), cy + 14 * s * math.sin(i / 40 * 2 * math.pi * 1.5)) for i in range(41)]
        d.line(R(pts), fill=255, width=max(2, int(6 * s)), joint="curve")
    elif thing == "moon":
        r = 30 * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        d.ellipse([cx - r + 14 * s, cy - r - 2 * s, cx + r + 14 * s, cy + r - 2 * s], fill=0)
    elif thing == "house":
        h = 20 * s
        d.polygon(R([(cx - h, cy - 2 * s), (cx + h, cy - 2 * s), (cx + h, cy + 30 * s), (cx - h, cy + 30 * s)]), fill=255)
        d.polygon(R([(cx - 30 * s, cy - 2 * s), (cx, cy - 32 * s), (cx + 30 * s, cy - 2 * s)]), fill=255)
    elif thing == "tree":
        d.polygon(R([(cx - 28 * s, cy + 12 * s), (cx, cy - 34 * s), (cx + 28 * s, cy + 12 * s)]), fill=255)
        d.polygon(R([(cx - 6 * s, cy + 12 * s), (cx + 6 * s, cy + 12 * s), (cx + 6 * s, cy + 34 * s), (cx - 6 * s, cy + 34 * s)]), fill=255)
    elif thing == "cup":
        w = 7 * s
        outer = [(cx - 26 * s, cy - 30 * s), (cx + 26 * s, cy - 30 * s), (cx + 26 * s, cy + 30 * s), (cx - 26 * s, cy + 30 * s)]
        inner = [(cx - 26 * s + w, cy - 34 * s), (cx + 26 * s - w, cy - 34 * s), (cx + 26 * s - w, cy + 30 * s - w), (cx - 26 * s + w, cy + 30 * s - w)]
        d.polygon(R(outer), fill=255); d.polygon(R(inner), fill=0)
    elif thing == "key":
        r, w = 14 * s, 5 * s
        d.ellipse([cx - 34 * s, cy - r, cx - 34 * s + 2 * r, cy + r], fill=255)
        d.ellipse([cx - 34 * s + w, cy - r + w, cx - 34 * s + 2 * r - w, cy + r - w], fill=0)
        d.polygon(R([(cx - 8 * s, cy - 4 * s), (cx + 34 * s, cy - 4 * s), (cx + 34 * s, cy + 4 * s), (cx - 8 * s, cy + 4 * s)]), fill=255)
        for off in (18 * s, 28 * s):
            d.polygon(R([(cx + off - 4 * s, cy + 4 * s), (cx + off + 4 * s, cy + 4 * s), (cx + off + 4 * s, cy + 14 * s), (cx + off - 4 * s, cy + 14 * s)]), fill=255)
    elif thing == "spiral":
        pts = []
        for i in range(0, 121):
            t = i / 120 * 2 * math.pi * 2.5
            r = 3 * s + 31 * s * i / 120
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        d.line(R(pts), fill=255, width=max(2, int(5 * s)), joint="curve")
    elif thing == "zog":      # a made-up thing: an hourglass (two triangles meeting at a point)
        d.polygon(R([(cx - 26 * s, cy - 30 * s), (cx + 26 * s, cy - 30 * s), (cx, cy)]), fill=255)
        d.polygon(R([(cx - 26 * s, cy + 30 * s), (cx + 26 * s, cy + 30 * s), (cx, cy)]), fill=255)
    elif thing == "vex":      # a made-up thing: a hexagon outline with a bar inside
        pts = [(cx + 32 * s * math.cos(math.radians(a)), cy + 32 * s * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        inner = [(cx + 24 * s * math.cos(math.radians(a)), cy + 24 * s * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        d.polygon(R(pts), fill=255); d.polygon(R(inner), fill=0)
        d.polygon(R([(cx - 4 * s, cy - 18 * s), (cx + 4 * s, cy - 18 * s), (cx + 4 * s, cy + 18 * s), (cx - 4 * s, cy + 18 * s)]), fill=255)
    else:
        raise KeyError(f"no such thing: {thing}")


def render(thing: str, rng: np.random.Generator, side: int = SIDE) -> np.ndarray:
    """One jittered side×side grey picture of `thing` in [0, 1] (§2: position ±3 px, scale 0.8–1.2,
    rotation ±15° where oriented, noise σ 0.05). The RNG draws are the same for every side."""
    img = Image.new("L", (HI, HI), 0)
    d = ImageDraw.Draw(img)
    k = HI / side
    dx, dy = rng.uniform(-3, 3) * k, rng.uniform(-3, 3) * k          # ±3 px of the picture
    s = rng.uniform(0.8, 1.2)
    deg = rng.uniform(-15, 15) if thing in ORIENTED else 0.0
    _draw(thing, d, HI / 2 + dx, HI / 2 + dy, s, deg)
    small = img.resize((side, side), Image.BOX)
    pic = np.asarray(small, dtype=np.float64) / 255.0
    pic = pic + rng.normal(0.0, 0.05, size=pic.shape)
    return np.clip(pic, 0.0, 1.0)


# ----------------------------------------------------------------------------- the ear
def encode_word(word: str, blank_zero: bool = False) -> np.ndarray:
    """SENSE ear letters 8: one slot per position, one-hot over 26 letters (+ blank unless
    blank_zero), unit length. A word longer than 8 letters is refused (the world's fault)."""
    word = word.lower()
    if len(word) > WORD_SLOTS or any(c not in LETTERS for c in word):
        raise ValueError(f"the ear takes ≤ {WORD_SLOTS} letters a–z: {word!r}")
    width = 26 if blank_zero else 27
    v = np.zeros(WORD_SLOTS * width, dtype=np.float64)
    for i in range(WORD_SLOTS):
        if i < len(word):
            v[i * width + LETTERS.index(word[i])] = 1.0
        elif not blank_zero:
            v[i * width + 26] = 1.0
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


# ----------------------------------------------------------------------------- streams
Moment = Tuple[str, np.ndarray]     # (thing, picture) — the word is the thing's name


def stream(things: Sequence[str], per_thing: int, rng: np.random.Generator, side: int = SIDE) -> List[Moment]:
    """A development stream: `per_thing` renderings of each thing, in a shuffled arrival order."""
    moments: List[Moment] = [(t, render(t, rng, side)) for t in things for _ in range(per_thing)]
    order = rng.permutation(len(moments))
    return [moments[i] for i in order]


def holdout(things: Sequence[str], n: int, rng: np.random.Generator, side: int = SIDE) -> Dict[str, List[np.ndarray]]:
    return {t: [render(t, rng, side) for _ in range(n)] for t in things}


def assert_disjoint(dev: Sequence[Moment], held: Dict[str, List[np.ndarray]]) -> int:
    """Held-out ∩ development must be empty, byte for byte. Returns the number of held-out pictures checked."""
    seen = {p.tobytes() for _, p in dev}
    k = 0
    for t, pics in held.items():
        for p in pics:
            k += 1
            if p.tobytes() in seen:
                raise AssertionError(f"held-out picture of {t!r} is byte-identical to a development picture")
    return k
