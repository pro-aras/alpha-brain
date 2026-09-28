# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:59 +0400 — the TOYS' world (B1-PREREG §5.5 (0b)), on the creature's OWN
# front (#232): real base-32 glyphs of latin-upper in the 4 TEACH fonts, pasted and glanced by
# brain/world/build.py's one road (render_glyph_canvas -> genome.gaze.glances, ALPHA4's organs) under
# /usr/bin/python3 (§3.0: no arm renders or glances). The toys give these real percepts INVENTED names in a toy
# order, so no B1 name, pair or relation is ever taught here.
#
# Build (once; minutes): cd <worktree> && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 19 \
#   /usr/bin/python3 -m tests.brain.arms_library.toy_world /data/dev/brain-runs/tmp/b1-library-toys
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

TOY_SEED = 20260930            # the pilot seed's number, used ONLY to seed this toy's own renderings
TOY_DIR = Path("/data/dev/brain-runs/tmp/b1-library-toys")
TEACH_FONTS = ["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf", "UbuntuSans[wdth,wght].ttf", "cmr10.ttf"]
# XOR toy: two glyph kinds; the planted-relation toy: sixteen, in a toy order with invented names
XOR_CHARS = {"S": "ki", "Y": "lo"}
PLANT_CHARS = "ABCDEFGHIJKLMNOP"
PLANT_NAMES = ["ba", "be", "bi", "bo", "bu", "da", "de", "di", "do", "du", "ga", "ge", "gi", "go", "gu", "ka"]


def requests():
    """Every rendering the toys use, with a unique item_id (§2.4's rng purpose key); k fresh renderings per
    (char, font) — the toys draw TEACH, training and held-out renderings from DIFFERENT k."""
    from brain.world.build import RenderRequest
    reqs = []
    for ch in list(XOR_CHARS) + list(PLANT_CHARS):
        for f in TEACH_FONTS:
            for k in range(6):
                reqs.append(RenderRequest(item_id=f"toy:{ch}:{f}:{k}", script="latin-upper", char=ch, font=f))
    return reqs


def build(out: Path) -> Dict[str, int]:
    from brain.world.build import build_cache
    out.mkdir(parents=True, exist_ok=True)
    item_to_row, header, _ = build_cache(requests(), out / "cache", TOY_SEED)
    (out / "rows.json").write_text(json.dumps(item_to_row, sort_keys=True, indent=0))
    return item_to_row


def load_rows(out: Path = TOY_DIR) -> Dict[str, int]:
    return json.loads((out / "rows.json").read_text())


def row(rows: Dict[str, int], ch: str, font_i: int, k: int) -> int:
    return rows[f"toy:{ch}:{TEACH_FONTS[font_i % 4]}:{k}"]


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else TOY_DIR
    m = build(target)
    print(f"toy cache: {len(m)} rows -> {target / 'cache'}")
