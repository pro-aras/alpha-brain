#!/usr/bin/env python3
# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 1
# (MOTOR-HANDS.md G-MOT-4's own shelf: "a small shelf of programs each with a known output"). A ONE-TIME
# generator (run to produce world/programs/*.py, then committed as data — the generator itself is not
# imported by the creature or its tests) for the 50 shape programs + the two "shape" control programs
# (positive/negative already have a fixed body of their own, written by hand below, not generated).
"""tools/build_hands_shelf.py — writes world/programs/*.py: 50 tiny, import-free `print('''...''')`
programs, each a 32-line x <=32-char ASCII picture of one of the maker's own things (circle square triangle
cross ring bar dot star arrow wave diamond moon house tree cup key -- genome/world.py's THINGS_11 +
THINGS_ARRIVAL2, verbatim), several size/offset variants each, drawn in roughly an 8x8-CHARACTER region
(<= 32 px after the 4x4-block expansion) at a varied grid offset -- MATCHING the maker's own scale (a
THING_SIDE=32 px shape on a CANVAS=128 canvas, genome/world.py's own constants) so a single 32x32-px glance
can see the whole shape, the same way it can see one of the maker's own drawn things (SOLUTIONS #228 (a)/
(c): a shape that fills the WHOLE 128x128 canvas would give every glance only a corner or an edge -- fair
scale, not tuning).

Each program is PURE STDLIB (`print('''ascii art''')`, zero imports): the jail's Landlock grants
read+execute beneath the shelf and /usr//etc only, never a site-packages tree, so a shelf program that
imported numpy/PIL (this generator's OWN tools, run OUTSIDE the jail) would not run inside it.

Also writes the four control programs (positive/negative/crash/fence) — G-MOT-4's own four.

Usage: python3 tools/build_hands_shelf.py   (idempotent: overwrites world/programs/*.py deterministically)
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SHELF = ROOT / "world" / "programs"

GRID = 32          # the shelf program's own 32x32 CHAR grid (matches creature/senses/hands.py's GRID_CHARS)
INK = "#"
GROUND = " "

THINGS_11 = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave", "diamond"]
THINGS_ARRIVAL2 = ["moon", "house", "tree", "cup", "key"]
THINGS_16 = THINGS_11 + THINGS_ARRIVAL2

# (size, offset_y, offset_x) variants, each a bounding box of roughly SIZE chars, placed with its top-left
# at (offset_y, offset_x) -- all comfortably inside the 32x32 grid, none overlapping the grid's edge.
VARIANTS: List[Tuple[int, int, int]] = [
    (8, 4, 4), (8, 18, 6), (6, 10, 16), (10, 4, 18),
]


def _blank() -> List[List[str]]:
    return [[GROUND] * GRID for _ in range(GRID)]


def _set(g: List[List[str]], y: int, x: int) -> None:
    if 0 <= y < GRID and 0 <= x < GRID:
        g[y][x] = INK


def _render(g: List[List[str]]) -> str:
    return "\n".join("".join(row) for row in g)


# ------------------------------------------------------------------------------ per-thing drawers
# Each drawer takes (size, oy, ox) -- a bounding box of roughly `size` characters with its top-left at
# (oy, ox) -- and returns the 32-line ASCII text. Filled shapes use '#'; outlines draw only the boundary.

def _circle(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = size / 2.0
    cy, cx = oy + r, ox + r
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            if ((y + 0.5 - cy) ** 2 + (x + 0.5 - cx) ** 2) <= r * r:
                _set(g, y, x)
    return _render(g)


def _ring(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = size / 2.0
    inner = r * 0.5
    cy, cx = oy + r, ox + r
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            d2 = (y + 0.5 - cy) ** 2 + (x + 0.5 - cx) ** 2
            if inner * inner <= d2 <= r * r:
                _set(g, y, x)
    return _render(g)


def _dot(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = max(1.0, size / 4.0)
    cy, cx = oy + size / 2.0, ox + size / 2.0
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            if ((y + 0.5 - cy) ** 2 + (x + 0.5 - cx) ** 2) <= r * r:
                _set(g, y, x)
    return _render(g)


def _square(size: int, oy: int, ox: int) -> str:
    g = _blank()
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            _set(g, y, x)
    return _render(g)


def _diamond(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = size / 2.0
    cy, cx = oy + r, ox + r
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            if abs(y + 0.5 - cy) + abs(x + 0.5 - cx) <= r:
                _set(g, y, x)
    return _render(g)


def _triangle(size: int, oy: int, ox: int) -> str:
    """Isoceles, point up, filled: at row i (0 at the top), the half-width grows linearly from 0 to
    size/2, so the base (row size-1) spans the full box width."""
    g = _blank()
    cx = ox + size // 2
    for i, y in enumerate(range(oy, oy + size)):
        half_width = int(round((i + 1) * (size / 2.0) / size))
        for x in range(cx - half_width, cx + half_width + 1):
            _set(g, y, x)
    return _render(g)


def _cross(size: int, oy: int, ox: int) -> str:
    g = _blank()
    mid = size // 2
    w = max(1, size // 5)
    for y in range(oy, oy + size):
        for x in range(ox + mid - w, ox + mid + w + 1):
            _set(g, y, x)
    for x in range(ox, ox + size):
        for y in range(oy + mid - w, oy + mid + w + 1):
            _set(g, y, x)
    return _render(g)


def _bar(size: int, oy: int, ox: int) -> str:
    g = _blank()
    h = max(1, size // 5)
    mid = oy + size // 2
    for y in range(mid - h, mid + h + 1):
        for x in range(ox, ox + size):
            _set(g, y, x)
    return _render(g)


def _star(size: int, oy: int, ox: int) -> str:
    import math
    g = _blank()
    r_out, r_in = size / 2.0, size / 4.5
    cy, cx = oy + size / 2.0, ox + size / 2.0
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        a = math.radians(-90 + k * 36)
        pts.append((cy + r * math.sin(a), cx + r * math.cos(a)))
    # rasterise via a simple point-in-polygon scan (small grid, cheap)
    for y in range(oy, oy + size):
        for x in range(ox, ox + size):
            if _point_in_polygon(y + 0.5, x + 0.5, pts):
                _set(g, y, x)
    return _render(g)


def _point_in_polygon(py: float, px: float, pts) -> bool:
    inside = False
    n = len(pts)
    for i in range(n):
        y1, x1 = pts[i]
        y2, x2 = pts[(i + 1) % n]
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside


def _arrow(size: int, oy: int, ox: int) -> str:
    g = _blank()
    mid = oy + size // 2
    w = max(1, size // 6)
    shaft_end = ox + int(size * 0.6)
    for y in range(mid - w, mid + w + 1):
        for x in range(ox, shaft_end):
            _set(g, y, x)
    head_h = size // 2
    for i in range(head_h):
        for y in range(mid - (head_h - i), mid + (head_h - i) + 1):
            _set(g, y, shaft_end + i)
    return _render(g)


def _wave(size: int, oy: int, ox: int) -> str:
    import math
    g = _blank()
    mid = oy + size // 2
    for i, x in enumerate(range(ox, ox + size)):
        y = mid + int(round((size / 4.0) * math.sin(i / max(1, size) * 2 * math.pi * 1.5)))
        _set(g, y, x)
        _set(g, y + 1, x)   # a 2px-thick line so it survives the 4x4 block coarsening
    return _render(g)


def _moon(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = size / 2.0
    cy, cx = oy + r, ox + r
    cx2 = cx + r * 0.45
    for y in range(oy, oy + size):
        for x in range(ox, ox + size + int(r)):
            d1 = (y + 0.5 - cy) ** 2 + (x + 0.5 - cx) ** 2
            d2 = (y + 0.5 - cy) ** 2 + (x + 0.5 - cx2) ** 2
            if d1 <= r * r and d2 > (r * 0.9) ** 2:
                _set(g, y, x)
    return _render(g)


def _house(size: int, oy: int, ox: int) -> str:
    g = _blank()
    wall_top = oy + size // 3
    for y in range(wall_top, oy + size):
        for x in range(ox, ox + size):
            _set(g, y, x)
    roof_h = size // 3
    for i in range(roof_h):
        y = wall_top - 1 - i
        left = ox + size // 2 - i
        right = ox + size // 2 + i
        for x in range(max(ox, left), min(ox + size, right + 1)):
            _set(g, y, x)
    return _render(g)


def _tree(size: int, oy: int, ox: int) -> str:
    g = _blank()
    canopy_h = int(size * 0.7)
    for i in range(canopy_h):
        y = oy + i
        half = int((i + 1) * size / (2.0 * canopy_h))
        for x in range(ox + size // 2 - half, ox + size // 2 + half + 1):
            _set(g, y, x)
    trunk_w = max(1, size // 6)
    for y in range(oy + canopy_h, oy + size):
        for x in range(ox + size // 2 - trunk_w, ox + size // 2 + trunk_w + 1):
            _set(g, y, x)
    return _render(g)


def _cup(size: int, oy: int, ox: int) -> str:
    g = _blank()
    w = max(1, size // 6)
    for y in range(oy, oy + size):
        for x in range(ox, ox + w):
            _set(g, y, x)
        for x in range(ox + size - w, ox + size):
            _set(g, y, x)
    for x in range(ox, ox + size):
        for y in range(oy + size - w, oy + size):
            _set(g, y, x)
    return _render(g)


def _key(size: int, oy: int, ox: int) -> str:
    g = _blank()
    r = size // 3
    cy, cx = oy + r, ox + r
    for y in range(oy, oy + 2 * r):
        for x in range(ox, ox + 2 * r):
            d2 = (y + 0.5 - cy) ** 2 + (x + 0.5 - cx) ** 2
            if (r * 0.5) ** 2 <= d2 <= r * r:
                _set(g, y, x)
    shaft_w = max(1, size // 8)
    mid = cy
    for y in range(int(mid) - shaft_w, int(mid) + shaft_w + 1):
        for x in range(cx + r, ox + size):
            _set(g, y, x)
    return _render(g)


DRAWERS: Dict[str, Callable[[int, int, int], str]] = {
    "circle": _circle, "square": _square, "triangle": _triangle, "cross": _cross,
    "ring": _ring, "bar": _bar, "dot": _dot, "star": _star, "arrow": _arrow, "wave": _wave,
    "diamond": _diamond, "moon": _moon, "house": _house, "tree": _tree, "cup": _cup, "key": _key,
}


def build() -> List[str]:
    SHELF.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    variant_i = 0
    names_written = 0
    per_thing_target = {t: 3 for t in THINGS_16}
    # 16 things * 3 = 48; two extra variants for circle and square to reach exactly 50 (brief's own count).
    per_thing_target["circle"] = 4
    per_thing_target["square"] = 4
    for thing in THINGS_16:
        drawer = DRAWERS[thing]
        for k in range(per_thing_target[thing]):
            size, oy, ox = VARIANTS[k % len(VARIANTS)]
            art = drawer(size, oy, ox)
            name = f"{thing}_{k}"
            path = SHELF / f"{name}.py"
            body = f'# shape: {thing}\nprint("""{art}""")\n'
            path.write_text(body)
            written.append(name)
            names_written += 1
    return written


POSITIVE = '# control: positive\nprint("#" * 8)\n'
NEGATIVE = ('# control: negative\n'
            'with open("INPUT.txt") as f:\n'
            '    print(f.read().strip())\n')
CRASH = ('# control: crash\n'
         'import sys\n'
         "sys.stdout.buffer.write(b'program 441\\n')\n"
         "sys.stdout.buffer.write('\\u25f9'.encode('utf-8')[:2])\n"
         'sys.stdout.buffer.flush()\n')
FENCE = '# control: fence\nimport socket\nsocket.socket()\n'


def build_controls() -> List[str]:
    SHELF.mkdir(parents=True, exist_ok=True)
    for name, body in (("_control_positive", POSITIVE), ("_control_negative", NEGATIVE),
                        ("_control_crash", CRASH), ("_control_fence", FENCE)):
        (SHELF / f"{name}.py").write_text(body)
    return ["_control_positive", "_control_negative", "_control_crash", "_control_fence"]


def main() -> int:
    shapes = build()
    controls = build_controls()
    print(f"wrote {len(shapes)} shape programs + {len(controls)} control programs to {SHELF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
