"""probes.py — STAGE -1 CLAUSE 3: the ceiling probe's OWN controls (B1-PREREG.md §3.3).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:2x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

"The probe's own controls: a planted DISTINGUISHABLE family (two classes: a filled 32-px square vs a thin
ring, through the same road) must read >= 0.99; a planted IDENTICAL family (one glyph given two labels)
must read chance +/- its binomial band. Either failing -> the ceilings are void and nothing proceeds."

Reuses `genome.world`'s own "square"/"ring"/"circle" things and `genome.world.render_canvas` — THE SAME
road B1's glyphs go through (`brain.world.canvas.paste_on_canvas` is that function's own body, §2.4) — so
"through the same road" is literal, not merely analogous. Must run under `/usr/bin/python3` (§3.0).
"""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

from genome import gaze as genome_gaze
from genome.world import render_canvas

from brain.world import organs
from brain.world.seeds import substream

from .oracles import LinearReadoutOracle, accuracy, f_pool


class ProbeError(Exception):
    pass


def _glance_rgb(rgb: np.ndarray, spec, gaze_cfg, colour) -> np.ndarray:
    out = genome_gaze.glances(rgb, spec, gaze_cfg, mode="surprise", pic_id="", colour=colour, predicted=None)
    return np.stack(out["feats"], axis=0)


def distinguishable_control(seed: int, n_per_class: int = 30, bar: float = 0.99) -> Dict[str, object]:
    """A filled square vs a thin ring must be trivially separable — if this reads below `bar`, the whole
    render/glance/pool road is broken and every other ceiling in this run is meaningless."""
    g = organs.load_genome()
    spec, gaze_cfg, colour = organs.gaze_config(g)
    X: List[np.ndarray] = []
    y: List[str] = []
    for thing in ("square", "ring"):
        for i in range(n_per_class):
            rng = substream(seed, f"probe:distinguishable:{thing}:{i}")
            rgb, _truth = render_canvas(thing, rng)
            X.append(f_pool(_glance_rgb(rgb, spec, gaze_cfg, colour)))
            y.append(thing)
    X = np.array(X)
    half = n_per_class // 2
    train_idx = list(range(half)) + list(range(n_per_class, n_per_class + half))
    test_idx = list(range(half, n_per_class)) + list(range(n_per_class + half, 2 * n_per_class))
    oracle = LinearReadoutOracle().fit(X[train_idx], [y[i] for i in train_idx])
    pred = oracle.predict(X[test_idx])
    acc = accuracy(pred, [y[i] for i in test_idx])
    return {"accuracy": acc, "bar": bar, "pass": acc >= bar, "n": len(test_idx)}


def identical_control(seed: int, n: int = 60, thing: str = "circle") -> Dict[str, object]:
    """The SAME thing rendered `n` times (real placement/noise variation, exactly as any other rendering)
    given a purely arbitrary, coin-flip label with no visual correlate — a working oracle must read chance."""
    g = organs.load_genome()
    spec, gaze_cfg, colour = organs.gaze_config(g)
    X: List[np.ndarray] = []
    for i in range(n):
        rng = substream(seed, f"probe:identical:{i}")
        rgb, _truth = render_canvas(thing, rng)
        X.append(f_pool(_glance_rgb(rgb, spec, gaze_cfg, colour)))
    X = np.array(X)
    label_rng = substream(seed, "probe:identical:labels")
    labels = label_rng.integers(0, 2, size=n)
    y = ["X" if v == 0 else "Y" for v in labels]
    half = n // 2
    oracle = LinearReadoutOracle().fit(X[:half], y[:half])
    pred = oracle.predict(X[half:])
    acc = accuracy(pred, y[half:])
    chance = 0.5
    n_test = n - half
    band = 1.96 * math.sqrt(chance * (1 - chance) / n_test)
    return {"accuracy": acc, "chance": chance, "band_95": band, "pass": abs(acc - chance) <= band, "n": n_test}


def run_both(seed: int) -> Dict[str, object]:
    """§3.3: "Either failing -> the ceilings are void and nothing proceeds." Callers check `["pass"]` on the
    returned dict before computing a single family ceiling."""
    dist = distinguishable_control(seed)
    ident = identical_control(seed)
    return {"distinguishable": dist, "identical": ident, "pass": bool(dist["pass"] and ident["pass"])}
