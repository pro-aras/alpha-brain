#!/usr/bin/env python3
# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:48 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 6
# (PREREG §19.9's mark, L-12).
"""tools/hands_recognised.py — the recognised share: does the exam's own road (`recall_many` on the
rendered canvas's glances, by the ledger — the SAME mechanism genome/questions.py:ask's Q1 uses, tools/
self_exam.py's own import) answer a HANDS-rendered ASCII canvas with the program's own `shape`, even though
no HANDS run ever taught a word?

Usage: python3 tools/hands_recognised.py --root <pre-flight root> --genome <genome path used to build it>

Reads the given root's snapshot (organism.npz/ledger.json — self_exam.load_snapshot, imported not copied)
and its tape's `hands`-sourced eye rows (meta.source == "hands", meta.program, meta.shape). For each row
tagged with a real `shape` (a control program's row carries `shape: null` and is excluded from the
denominator — the mark is about the 50 shape programs, not the four controls), decodes the rendered canvas,
glances it exactly as `creature/mind.py:_consume_eye` would (`gaze.glances`, mode "surprise"), and asks
`Organism.recall_many("sight", glances)` for the words-side cell its sight glances resonate with, reading
the answer off `ledgers["words"]` — the SAME road `genome/questions.py:ask`'s Q1 uses on a held-out drawn
picture, applied here to a hands-rendered one.

Prints (never bars on) the recognised share and a SHUFFLED-SHELF TWIN (the manifest shapes permuted with a
fixed seed BEFORE scoring, so the twin answers against a WRONG label for the same predictions) — "not
gradable" under 20 runs, exactly the mark's own words.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from genome import gaze                        # noqa: E402
from tools.self_exam import load_snapshot       # noqa: E402 (imported, never copied)


def _hands_shape_rows(root: Path) -> List[dict]:
    """Every `eye` row on `root`'s tape with `meta.source == "hands"` AND a real `meta.shape` (a control
    program's row carries `shape: null` and is excluded — the mark grades the 50 shape programs)."""
    from creature.tape import read_tape
    out = []
    for r in read_tape(root):
        if r.get("sense") != "eye":
            continue
        meta = r.get("meta") or {}
        if meta.get("source") == "hands" and meta.get("shape"):
            out.append(r)
    return out


def recognised_share(root: Path, genome_path: Path, shuffle_seed: int = 20260922, min_runs: int = 20) -> Dict[str, object]:
    root = Path(root)
    rows = _hands_shape_rows(root)
    if len(rows) < min_runs:
        return {"gradable": False, "n": len(rows), "min_runs": min_runs}

    g, org, ledgers, _L = load_snapshot(root, Path(genome_path))
    predictions: List[Tuple[str, Optional[str]]] = []   # (true shape, answered word or None)
    for r in rows:
        shape = str((r.get("meta") or {}).get("shape"))
        payload_path = root / "tape" / r["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        glances = gaze.glances(rgb, org.g.retina, org.g.gaze, "surprise", r["sha"], colour=org.g.colour)
        rr = org.recall_many("sight", glances["feats"])
        if rr.get("cell") is None:
            predictions.append((shape, None))
            continue
        ans = ledgers["words"].get(rr["cell"], set())
        answered = next(iter(ans)) if len(ans) == 1 else ("|".join(sorted(ans)) if ans else None)
        predictions.append((shape, answered))

    n = len(predictions)
    correct = sum(1 for shape, answered in predictions if answered == shape)
    share = correct / n if n else float("nan")

    # the shuffled-shelf twin: the SAME predictions, scored against a PERMUTED assignment of true shapes
    # (fixed seed -- deterministic, reproducible, never re-drawn until it looks better, #158's law).
    rng = np.random.default_rng(shuffle_seed)
    true_shapes = [s for s, _ in predictions]
    shuffled_shapes = list(rng.permutation(true_shapes))
    twin_correct = sum(1 for (_, answered), shuffled in zip(predictions, shuffled_shapes) if answered == shuffled)
    twin_share = twin_correct / n if n else float("nan")

    return {
        "gradable": True, "n": n, "correct": correct, "recognised_share": share,
        "shuffled_twin_correct": twin_correct, "shuffled_twin_share": twin_share,
        "abstained": sum(1 for _, a in predictions if a is None),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--genome", required=True)
    ap.add_argument("--min-runs", type=int, default=20)
    a = ap.parse_args()
    result = recognised_share(Path(a.root), Path(a.genome), min_runs=a.min_runs)
    print(json.dumps(result, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
