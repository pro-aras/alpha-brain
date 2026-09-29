#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 15:15 +0400 — new tool: LOOK AGAIN read on the BENCH before any build.
"""tools/brain/diag/probe_lookagain.py --ws WS [--fit 8000] [--out DIR]

The look-again act is dated 2026-09-30. DIAG-LOOK-AGAIN read its GEOMETRY (one targeted look takes «the named thing was
seen» from 0.89 to 0.99). This probe reads what that does to the BRAIN, on TRAINING rows alone, with no production code:

  the rule R-BLOB   after the eye's own fixations, up to K more at the largest unseen ink blob of >= MIN cells (the eye's own
                    ink rule on its own 16 x 16 grid; tools/brain/diag/lookagain_blob.py's functions, imported);
  the new glance    brain.scene.eye.forced_glance at the chosen cell's centre: the eye's own composition (pinned byte-equal
                    to a fixated cell's glance; re-checked here on cached fixations as THE CONTROL);
  the brain         genome/brain.py's organ under the template's BRAIN line, fed each training scene's glances (the
                    cached four, the new ones, the coarse one) and the parent's words, in order;
  what is read      DIAG-M2B's own two parts (tools/brain/diag/probe_fm2b.py, imported): the store's attributions against
                    the bench's truth, and the reader rebuilt from each store on the validation rows' one-thing scenes.

edit: Claude (Fable 5.1, the seat), 2026-09-29 15:19 +0400 — `--grid m2b --fit 10000`: the REAL test 2b items of the test sets ALREADY READ
(never the gate's), answered by each reader of a brain that learned all 10,000 scenes WITH the arm's looks. Test 2b's scenes
hold one thing, so the asked canvas takes its cached glances; the look changes what was LEARNED.

ARMS: law (no look) · look1:min4 · look2:min4 · look1:min6. The truth is read by the bench only.
A presence count stands beside every rate. Nothing here writes the organ, a cache or any life root."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from brain.scene import cache as C          # noqa: E402
from brain.scene import eye as E            # noqa: E402
from brain.scene import world as W          # noqa: E402
from genome import brain as B               # noqa: E402
from genome import gaze as G                # noqa: E402
from tools.brain import gate_alone as GA    # noqa: E402
from tools.brain.diag import probe_fm2b as P   # noqa: E402

ARMS = {"law": (0, 0), "look1:min4": (1, 4), "look2:min4": (2, 4), "look1:min6": (1, 6)}
INK_T = 0.10
GRID, CELL = 16, 8


def blobs(rgb: np.ndarray, ink_t: float):
    from scipy import ndimage
    ink = G.ink_border(G.luminance(rgb))
    cells = (ink.reshape(GRID, CELL, GRID, CELL).max(axis=(1, 3)) > ink_t)
    return ndimage.label(cells, structure=np.ones((3, 3), dtype=int))


def look_again(lab, n, fix, k_max: int, min_cells: int) -> List[Tuple[int, int]]:
    """R-BLOB, as DIAG-LOOK-AGAIN read it: a blob is seen when a fixation lies on it or touches it; one more fixation at the
    largest unseen blob of >= min_cells, at its cell nearest its centre; up to k_max times."""
    fix = list(fix)
    added: List[Tuple[int, int]] = []
    for _ in range(k_max):
        seen = set()
        for (y, x) in fix:
            ys, xs = slice(max(0, y - 1), min(GRID, y + 2)), slice(max(0, x - 1), min(GRID, x + 2))
            seen.update(int(v) for v in np.unique(lab[ys, xs]) if v > 0)
        cand = [(int((lab == b).sum()), -b) for b in range(1, n + 1) if b not in seen and int((lab == b).sum()) >= min_cells]
        if not cand:
            break
        _size, nb = max(cand)
        ys, xs = np.nonzero(lab == -nb)
        j = int(np.argmin((ys - ys.mean()) ** 2 + (xs - xs.mean()) ** 2))
        c = (int(ys[j]), int(xs[j]))
        fix.append(c)
        added.append(c)
    return added


class Looked:
    """One world seed's training scenes WITH the look-again glances of one arm: the glance dicts the brain is fed, and the
    truth rows with `fix_thing` extended to the new fixations (the bench's own reading)."""

    def __init__(self, ws: int, train: "C.ScenePercepts", truth, k_max: int, min_cells: int, n: int, control: Dict[str, object]):
        self.ws, self.k_max, self.min_cells = ws, k_max, min_cells
        spec, gaze_cfg, colour = E.eye_config()
        self.glance: List[Dict[str, object]] = []
        self.truth: List[Dict[str, object]] = []
        self.looks = 0
        self.on_no_thing = 0
        self.on_seen_thing = 0
        self.ref_seen_before = 0
        self.ref_seen_after = 0
        canvas = int(gaze_cfg["canvas"])
        for i in range(n):
            g = GA.glance_of(train, i)
            tr = dict(truth[i])
            fix = list(g["fix"])
            ft = list(tr["fix_thing"])
            ref = int(tr["referent"])
            self.ref_seen_before += ref in ft
            if k_max > 0:
                scene = W.train_scene(ws, i)
                rgb = W.render_scene(scene)[0]
                lab, nb = blobs(rgb, INK_T)
                extra = look_again(lab, nb, fix, k_max, min_cells)
                if extra or (control is not None and control["checked"] < control["want"]):
                    an = G._analyse_frame(rgb)
                    grey = G.luminance(rgb)
                    if control is not None and control["checked"] < control["want"] and fix:
                        # THE CONTROL: the eye's forced glance at a FIXATED cell's centre is that fixation's cached glance
                        v = E.forced_glance(rgb, E.cell_centre_px(fix[0], canvas, GRID), spec, gaze_cfg, colour, an, grey)
                        control["checked"] += 1
                        control["max_abs_diff"] = max(control["max_abs_diff"], float(np.max(np.abs(v - g["feats"][0]))))
                    new = [E.forced_glance(rgb, E.cell_centre_px(c, canvas, GRID), spec, gaze_cfg, colour, an, grey) for c in extra]
                    g = {"feats": list(g["feats"][:len(fix)]) + new + [g["feats"][len(fix)]], "fix": fix + extra, "windows": [],
                         "residual": [None] * (len(fix) + len(extra) + 1)}
                    on = [W.fixation_thing(c, scene.things) for c in extra]
                    self.looks += len(extra)
                    self.on_no_thing += sum(1 for x in on if x is None)
                    self.on_seen_thing += sum(1 for x in on if x is not None and x in ft)
                    ft = ft + on
            tr["fix_thing"] = ft
            self.ref_seen_after += ref in ft
            self.glance.append(g)
            self.truth.append(tr)

    def words(self, train, i: int) -> List[str]:
        return train.words(i)


def run_arm(ws: int, name: str, train, truth, fit: int, cfg, control, grid: str = "look") -> Dict[str, object]:
    k_max, min_cells = ARMS[name]
    t0 = time.process_time()
    lk = Looked(ws, train, truth, k_max, min_cells, len(train), control if k_max > 0 else None)
    brain = B.Brain(cfg)
    nones = []
    for i in range(fit):
        r = brain.learn(lk.glance[i], train.words(i), moment=f"sc{ws}t{i:06d}", scene=i, world_seed=ws)
        nones.append(r["none"])
    brain.ask({"form": "begin", "set": "probe", "test_seed": 0}, None)
    # probe_fm2b reads a scene's glance by GA.glance_of(train, i): it is handed THIS arm's glances for the validation rows
    real = GA.glance_of
    GA.glance_of = lambda p_, i: (lk.glance[i] if p_ is train else real(p_, i))     # a TEST split's percepts keep their own
    try:
        things, counts = (P.validation_things(train, lk.truth, fit, len(train), brain.L) if fit < len(train) else ([], {}))
        part_a = P.part_a(brain, lk.truth, fit, nones)
        part_b = P.part_b(brain, things, float(cfg["eps"]), nones, lk.truth, grid_name=grid, ws=ws)
    finally:
        GA.glance_of = real
    n = len(train)
    return {"arm": name, "k_max": k_max, "min_cells": min_cells, "scenes": n, "fit": fit,
            "looks_taken": lk.looks, "looks_a_scene": lk.looks / n, "new_fixations_on_no_thing": lk.on_no_thing,
            "new_fixations_on_a_thing_already_seen": lk.on_seen_thing,
            "named_thing_seen": {"before": lk.ref_seen_before / n, "after": lk.ref_seen_after / n},
            "hypotheses_a_scene": float(np.mean([len(B.things_in_view(g)[0]) for g in lk.glance[:fit]])),
            "validation_counts": counts, "A": part_a, "B": part_b, "cpu_s": time.process_time() - t0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", type=int, required=True)
    ap.add_argument("--fit", type=int, default=8000)
    ap.add_argument("--out", default="/data/dev/brain-runs/day0929/lookagain")
    ap.add_argument("--arms", nargs="*", default=list(ARMS))
    ap.add_argument("--grid", default="look", choices=("look", "m2b"))
    a = ap.parse_args()
    cfg = P.brain_cfg()
    d = C.cache_dir(C.RUNS, a.ws, "train")
    C.check_code(d)
    train = C.ScenePercepts(d)
    truth = C.load_truth(d)
    control = {"want": 200, "checked": 0, "max_abs_diff": 0.0}
    res = {"world_seed": a.ws, "fit": a.fit, "ink_t": INK_T, "arms": {}}
    for name in a.arms:
        res["arms"][name] = run_arm(a.ws, name, train, truth, a.fit, cfg, control, a.grid)
        print(f"[look {a.ws}] {name}: cpu {res['arms'][name]['cpu_s']:.0f} s", flush=True)
    res["control_forced_glance_at_a_fixated_cell"] = control
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / (f"brain-{a.ws}-fit{a.fit}.json" if a.grid == "look" else f"brain-{a.ws}-fit{a.fit}-{a.grid}.json")
    p.write_text(json.dumps(res, indent=1, sort_keys=True, default=GA._np))
    print(f"[look {a.ws}] wrote {p} · control: {control}")
    return 0 if control["checked"] > 0 and control["max_abs_diff"] < 1e-9 else 1


if __name__ == "__main__":
    sys.exit(main())
