#!/usr/bin/env python3
# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:07 +0400 — ALPHA4-H task 0/4 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §5's READ mark, "the reading mark"). Mirrors tools/hands_recognised.py's own shape exactly
# (the SAME road: recall_many on the rendered canvas's glances, by the ledger — genome/questions.py:ask's Q1
# road, self_exam.load_snapshot imported not copied).
"""tools/read_recognised.py — the reading mark's own instrument: does the exam's own road answer a WORD
rendered in the HELD-OUT font (DejaVu Serif, creature/senses/read_common.py's own constant — imported, never
re-typed, "so the mark and the sense cannot drift") with the same word the shelf's ear rows heard for it?

**RAISED (advisor-caught, 2026-09-23, before any toy ran):** ALPHA4-H.md's task 4 text says the 50 marked
words are "never among the first N read" (picked from the curriculum's LATER, unshown docs). That
contradicts the mark's own stated mechanism in the SAME sentence — "the mechanism is MEET sight-words on
the rendered line" — and ALPHA4-PREREG.md §5's own wording, which never says the WORD is held out, only
that the mark is read "on 50 held-out shelf words" with the FONT named as what is held out ("rendered in a
held-out font, never shown"). `org.recall_many("sight", ...)` can only ever answer with a word some sight
glance was actually bound to (creature/mind.py:_consume_eye's MEET road, `org.moment(x, xw)`) — a word the
life never heard has no words-cell, and the rate on such words is 0 BY CONSTRUCTION for every mechanism,
confirming vs. refuting nothing (#228 (b)'s own class: a bar the mechanism cannot clear by design). This
module therefore implements PREREG §5's coherent reading: the 50 (or, for the toy, all) words are words the
shelf DID show (heard, in the DEFAULT font); "held out" is the RENDER — a font that font never met, testing
generalisation across font the same way the K-corpus's own glyph exams do (CURRICULUM.md §1: "a held-out
IMAGE of a letter in a font the organism has already read is not held out; a held-out FONT is").

Usage: python3 tools/read_recognised.py --root <closed root> --genome <genome> --word zog --word cat ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from genome import gaze                                    # noqa: E402
from creature.senses import read_common                    # noqa: E402
from tools.self_exam import load_snapshot                  # noqa: E402 (imported, never copied)


def recognised_share(root: Path, genome_path: Path, words: Sequence[str],
                      font_path: str = read_common.HELDOUT_FONT_PATH, canvas: Optional[int] = None) -> Dict[str, object]:
    """For each of `words`: render it ALONE (read_common.render_line, the held-out font by default) at the
    life's own GAZE canvas size, glance it exactly as `creature/mind.py:_consume_eye` would (`gaze.glances`,
    mode "surprise" — the live road, never the replay-only "random" twin), and ask
    `Organism.recall_many("sight", glances)` for the words-side cell's answer, read off `ledgers["words"]`.
    Never mutates `org` (recall_many's own guarantee, asserted below by a state_hash pin, hands_recognised.py's
    own pattern)."""
    g, org, ledgers, _L = load_snapshot(Path(root), Path(genome_path))
    h0 = org.state_hash()
    canvas_px = int(canvas if canvas is not None else g.gaze["canvas"])
    predictions: List[Tuple[str, Optional[str]]] = []
    for w in words:
        rgb = read_common.render_line(w, canvas_px, font_path)
        sha = hashlib.sha256(w.encode("utf-8")).hexdigest()
        glances = gaze.glances(rgb, g.retina, g.gaze, "surprise", sha, colour=g.colour)
        rr = org.recall_many("sight", glances["feats"])
        if rr.get("cell") is None:
            predictions.append((w, None))
            continue
        ans = ledgers["words"].get(rr["cell"], set())
        answered = next(iter(ans)) if len(ans) == 1 else ("|".join(sorted(ans)) if ans else None)
        predictions.append((w, answered))
    assert org.state_hash() == h0, "recognised_share must never mutate the organism (recall_many's own guarantee)"

    n = len(predictions)
    correct = sum(1 for w, a in predictions if a == w)
    share = (correct / n) if n else float("nan")
    return {
        "n": n, "correct": correct, "share": share, "font": str(font_path), "canvas": canvas_px,
        "predictions": [{"word": w, "answered": a} for w, a in predictions],
        "abstained": sum(1 for _w, a in predictions if a is None),
    }


def blind_twin_root(source_root: Path, genome_path: Path, out_root: Path, drop_source: str = "shelf") -> Path:
    """PREREG §5's own control: "the blind twin (the shelf rows dropped) reads 0 by construction". A FRESH
    Mind, fed `source_root`'s tape with every row whose `meta.source == drop_source` removed, closed (so it
    snapshots) — `out_root` is then a normal `load_snapshot`-able root. Never touches `source_root`
    (mirrors creature/replay.py:run_replay's own "a temporary work root ... tape/payload is a symlink"
    discipline — never copied, never written to)."""
    import os
    from creature.mind import Mind
    from creature.tape import read_tape, _resolve_tape_dir
    from genome.machinery import parse_genome

    source_root = Path(source_root); out_root = Path(out_root); genome_path = Path(genome_path)
    out_root.mkdir(parents=True, exist_ok=True)
    declared_tape_path = parse_genome(genome_path.read_text()).declared.get("TAPE", {}).get("path")
    source_tape_dir = _resolve_tape_dir(source_root, declared_tape_path)
    work_tape = _resolve_tape_dir(out_root, declared_tape_path)
    work_tape.mkdir(parents=True, exist_ok=True)
    payload_src = source_tape_dir / "payload"
    if payload_src.exists() and not (work_tape / "payload").exists():
        os.symlink(payload_src.resolve(), work_tape / "payload")

    mind = Mind(genome_path, out_root)
    for row in read_tape(source_root, declared_path=declared_tape_path):
        if (row.get("meta") or {}).get("source") == drop_source:
            continue
        mind.consume(row)
    mind.close()
    return out_root


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--genome", required=True)
    ap.add_argument("--word", action="append", default=[], dest="words")
    ap.add_argument("--font", default=read_common.HELDOUT_FONT_PATH)
    a = ap.parse_args()
    result = recognised_share(Path(a.root), Path(a.genome), a.words, font_path=a.font)
    print(json.dumps(result, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
