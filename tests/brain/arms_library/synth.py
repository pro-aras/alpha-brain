# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:56 +0400 — a SYNTHETIC glance cache for PLUMBING tests of arm D only
# (protocol conformance, identity, the evaluator's semantics). It is NOT the creature's front: the toys of
# B1-PREREG §5.5 (0b) run on real renderings through brain/world/build.py's road (tests/brain/arms_library/
# test_toys.py), never on this. Written through brain.glance_cache.CacheWriter, read back through Cache — the
# same reader every arm uses.
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from brain.glance_cache import CacheWriter


class SynthWorld:
    """Named "forms", each a random prototype in R^144; a rendering = 5 glances = prototype + noise."""

    def __init__(self, seed: int = 7, noise: float = 0.30):
        self.rng = np.random.default_rng(seed)
        self.noise = noise
        self.protos: Dict[Tuple[str, str], np.ndarray] = {}
        self.rows: List[np.ndarray] = []
        self.meta: List[Tuple[str, str]] = []

    def render(self, name: str, form: str = "U") -> int:
        key = (name, form)
        if key not in self.protos:
            self.protos[key] = self.rng.normal(size=144)
        p = self.protos[key]
        g = np.stack([p + self.rng.normal(scale=self.noise, size=144) for _ in range(5)])
        self.rows.append(g)
        self.meta.append(key)
        return len(self.rows) - 1

    def write(self, out_dir: Path) -> Path:
        w = CacheWriter(out_dir)
        for i, g in enumerate(self.rows):
            name, form = self.meta[i]
            w.add(item_id=f"synth-{i}", script="synth", char=f"{name}{form}", font="synth", variant="synth",
                  seed=0, canvas_png_sha256="0" * 64, feats=g)
        w.finalize(seed=0, genome_sha="synthetic", organ_pins={}, interpreter={}, library_versions={})
        return out_dir
