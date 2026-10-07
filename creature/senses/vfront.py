# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 02:12 +0400 — AMENDMENT-1 (135f141, the seat's ruling on the
# VOID road's cause): §2.6's feature block re-composed at the genome's own 144 — the per-channel window runs the FRONT'S
# OWN declared spec ("pool8", "hog12", "unit") = 28 numbers a channel (registration-preserving steps only: no
# centre/thresh/blur), the feature [band×4 · colour_block] = 4×28 + 32 = 144 == the pinned bench genome's sight_dim().
# The maps (§2 stages 1–5) and every other byte stand untouched (the plants were already green, never re-litigated).
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400 — PREREG-OPEN-WORLD-3 §2 build (the law SIGNED at
# 5ce8012; its sha256 carried by docs/organism/whole/records/open-world-3/SEAT-LINE.txt). Tests FIRST: tests/creature/test_vfront.py.
"""creature/senses/vfront.py — THE INNATE VIDEO FRONT (PREREG-OPEN-WORLD-3, docs/organism/whole/, V2 + AMENDMENT-1).

The retina's machine form as an organ of the organism, BESIDE the scene world's own eye: the raw-frame feature
path (luminance → INK rule → retina tower) is REPLACED for the consumption when (and only when) a Mind is
constructed with this front wired (creature/mind.py:_consume_eye's ONE branch point; default None = every byte
unchanged, the G-IDENTITY gates). Never raw frames inward: fixation SELECTION stays on Alpha 2's own
analyse/`gaze_sequence` exactly as `genome.gaze.glances` does it today (the attention/transduction split, §1 —
where to look is the gaze gene's; what the look READS is the front's).

The law §2's six stages, every constant DECLARED machine-form (a 128×128 canvas carries no visual-angle
calibration; physiological exactness is not claimed), fixed before any reading and never tuned after one:

1. Center-surround: C = L∗G(σc) − L∗G(σs) over the organism's own luminance (genome/gaze.py:92), with the
   organism's own gaussian (machinery.py's `scipy.ndimage` — never a second filter). σc = 1.0 px, σs = 3.0 px.
2. The signed ON/OFF split: ON = max(C, 0), OFF = max(−C, 0) — increments and decrements are separate machines.
   The colour opponents rg/by (already opponent, already the organism's, gaze.py:74) ride the sustained path
   UNCHANGED: they enter the feature through the gene's own `colour_block`/`colour_block_whole` roads, exactly
   as the raw path's.
3. Pooled normalization (the sustained gain): each sustained channel R̃ = R / (β + mean|R| over the map),
   β = 0.01 — per frame, stateless. The transient's luminance is normalized by the same form (§2.4's
   "the NORMALIZED luminance").
4. The transient bandwidth: D = L̃_t − L̃_{t−1} over the NORMALIZED luminance; T-ON = max(out, 0),
   T-OFF = max(−out, 0) of the operating-point output below. The first frame of a tape: D := 0, so the T maps
   are exactly 0 (DECLARED) and the operating point stays at o_0 = 0.
5. Operating-point adaptation (the transient gain), CAUSAL: the output uses the operating point of the PAST,
   out = D / (β + o_{t−1}); only then does o update: o_t = (1−α)·o_{t−1} + α·mean|D_t|, α = 0.2, o_0 = 0.
   The present never sets its own gain.
6. The glance feature (what a look reads), AS RE-DECLARED BY AMENDMENT-1 §2 (135f141 — the seat's ruling on the
   VOID road's cause: the law's first composition, 4×112 + 32 = 480, could not enter the organism's genome-derived
   144-dim sight area, and every road that moves the dim is forbidden; the channels keep their own towers, the
   budget they share is the genome's own 112 — a declared simplification, printed with the reading): per fixated
   window (the gaze gene's own windows, gaze.py's `glance_window` road), each channel map runs through the
   FRONT'S OWN declared retina spec FRONT_SPEC = ("pool8", "hog12", "unit") = 28 numbers a channel —
   registration-preserving steps only: no `centre` (it would shift each channel's centroid independently and
   destroy the channels' spatial registration — the channels read the SAME visual field), no `thresh` (the maps
   are signed-rectified and normalized already), no `blur` (the DoG already smooths); `pool`/`hog` are
   place-fixed. The feature = [band(OÑ) · band(OFF̃) · band(T-ON) · band(T-OFF) · colour_block] =
   4×28 + 32 = exactly the genome's own 144, unit-normalised ONCE at the end (the fixed-gain pattern,
   unchanged); `colour_block` is the genome's own 32, unchanged. The coarse glance likewise (per-channel
   whole-canvas windows at the genome's coarse size, `colour_block_whole`'s 32) when the bench genome declares
   it. A test gates the composed length against the G-TAPE-pinned bench genome's sight_dim() forever
   (AMENDMENT-1 §2.3). The colourless genome's feature is the 4×28 concatenation under the same one outer unit
   step (the residual road, gaze.py's `_residual`, reads unit-length vectors by construction). The return is the
   glances dict's own shape — {"feats", "fix", "windows", "residual"} — so _consume_eye reads it unchanged.

The front's temporal state is exactly one previous normalized frame + the operating point, held by the front
OBJECT across a replay, never in the genome; two fresh fronts over the same frames agree to the byte (the
tests). `last_t_mass` (mean|T-ON| + mean|T-OFF|) and `last_o` (the operating point the state now holds, after
this canvas's causal update) are the instrument values §2.7's additive journal key `front` carries when (and
only when) the front is wired.

An INSTRUMENT-TRUE organ: the planted signatures (tests/creature/test_vfront.py: the split, DC-free, signed
motion, gain invariance, adaptation decay) hold EXACTLY, and a doctored twin (OFF map zeroed; normalization
removed) is CAUGHT by them. No borrowed weights, no LM, no tuned constants.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage as _ndi

from genome import gaze as _gaze
from genome.machinery import GenomeError, _unit, retina

SIGMA_C = 1.0     # §2.1 DECLARED — the DoG's center, px
SIGMA_S = 3.0     # §2.1 DECLARED — the DoG's surround (≈ 3× center, the classical ratio)
BETA = 0.01       # §2.3/§2.5 DECLARED — the pooled normalization's and the operating point's floor
ALPHA = 0.2       # §2.5 DECLARED — the operating point's causal update rate
FRONT_SPEC = ("pool8", "hog12", "unit")   # AMENDMENT-1 §2.1 DECLARED — the FRONT'S OWN band spec, 28 numbers a
                                          # channel at the glance size; registration-preserving steps only
                                          # (no centre/thresh/blur); retina_dim's own arithmetic, gated by the tests

_CHANNELS = ("ON", "OFF", "T-ON", "T-OFF")        # the four banded maps, in the feature's declared order


def _dog(lum: np.ndarray) -> np.ndarray:
    """§2.1's center-surround: L∗G(σc) − L∗G(σs), the organism's own gaussian (machinery.py's `_ndi`)."""
    return _ndi.gaussian_filter(lum, SIGMA_C) - _ndi.gaussian_filter(lum, SIGMA_S)


class VideoFront:
    """The law §2's organ (AMENDMENT-1's composition). Constructed with the genome's own GAZE dict and SENSE
    colour dict (or None); holds the temporal state — one previous normalized frame + the operating point —
    across a replay, never in the genome. The genome's RETINA line is NOT read: the band spec is the FRONT'S
    OWN (FRONT_SPEC, AMENDMENT-1 §2.1)."""

    def __init__(self, gaze: Dict[str, object], colour: Optional[Dict[str, object]] = None):
        self.gaze: Dict[str, object] = dict(gaze)
        self.colour = colour
        self._prev: Optional[np.ndarray] = None     # L̃_{t−1} — None until the first frame lands
        self._o: float = 0.0                        # the operating point, o_0 = 0 (DECLARED)
        self.last_t_mass: float = 0.0               # this canvas's mean|T-ON| + mean|T-OFF| (§2.7's t_mass)
        self.last_o: float = 0.0                    # the operating point the state now holds (§2.7's o)

    # ---------------------------------------------------------------- §2.2/§2.3 the sustained machine
    def _pool(self, r: np.ndarray) -> np.ndarray:
        """§2.3's pooled normalization: R̃ = R / (β + mean|R| over the map), per frame, stateless."""
        return r / (BETA + float(np.abs(r).mean()))

    def _sustained(self, L: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """§2.1→§2.3: the DoG, the signed split, the pooled gain — OÑ and OFF̃, separate machines."""
        C = _dog(L)
        return self._pool(np.maximum(C, 0.0)), self._pool(np.maximum(-C, 0.0))

    # ---------------------------------------------------------------- §2.4/§2.5 the transient machine
    def _advance(self, L: np.ndarray) -> Dict[str, np.ndarray]:
        """One luminance frame through the front: the sustained maps, the transient maps (CAUSAL — the
        output uses o_{t−1}, THEN o updates and the frame becomes the past), the instrument values."""
        on, off = self._sustained(L)
        ln = self._pool(L)
        d = np.zeros_like(ln) if self._prev is None else ln - self._prev   # the first frame: D := 0 (DECLARED)
        out = d / (BETA + self._o)
        t_on, t_off = np.maximum(out, 0.0), np.maximum(-out, 0.0)
        m = float(np.abs(d).mean())
        self._prev = ln
        self._o = (1.0 - ALPHA) * self._o + ALPHA * m
        self.last_t_mass = float(t_on.mean()) + float(t_off.mean())
        self.last_o = self._o
        return {"ON": on, "OFF": off, "T-ON": t_on, "T-OFF": t_off, "D": d}

    def maps(self, rgb: np.ndarray) -> Dict[str, np.ndarray]:
        """The plants' road (tests/creature/test_vfront.py): one canvas → the front's maps, state advanced."""
        return self._advance(_gaze.luminance(rgb))

    # ---------------------------------------------------------------- §2.6 the glance feature (AMENDMENT-1's composition)
    def _feature(self, blocks: List[np.ndarray], cb: Optional[np.ndarray]) -> np.ndarray:
        """[band(OÑ) · band(OFF̃) · band(T-ON) · band(T-OFF) (· colour_block)] — each channel window through
        FRONT_SPEC (28 numbers a channel, registration-preserving), colour_block's raw 32 beside, unit-
        normalised ONCE at the end (the fixed-gain pattern). = the genome's own 144 when colour is declared."""
        v = np.concatenate([retina(b, FRONT_SPEC) for b in blocks] + ([cb] if cb is not None else []))
        return _unit(v)

    def _whole(self, maps: Dict[str, np.ndarray], an: Dict[str, object], size: int) -> np.ndarray:
        """The whole-canvas feature at `size`×`size` (mode "one" and the declared coarse glance): the four
        maps box-pooled to the size — an exact mean pool, so the canvas side must divide `size` (a refusal,
        never an invented resample) — banded per channel through FRONT_SPEC, colour_block_whole's 32 beside,
        the one outer unit step."""
        n = int(maps["ON"].shape[0])
        if n % size:
            raise GenomeError(f"video front: the whole-canvas glance at {size}px does not divide the {n}px canvas")
        k = n // size
        blocks = [maps[key].reshape(size, k, size, k).mean(axis=(1, 3)) for key in _CHANNELS]
        cb = _gaze.colour_block_whole(an) if self.colour is not None else None
        return self._feature(blocks, cb)

    def glances(self, rgb: np.ndarray, mode: str = "surprise", pic_id: str = "",
                predicted: Optional[np.ndarray] = None) -> Dict[str, object]:
        """§2.6: one canvas → the glances dict's own shape ({"feats", "fix", "windows", "residual"}), so
        creature/mind.py:_consume_eye reads it unchanged. Fixation SELECTION is the gaze gene's own
        analyse/`gaze_sequence` (or `random_gaze` under the mind's --blind gaze twin), exactly as
        genome/gaze.py's glances does it; what each look READS is the front's. Advances the temporal state
        ONCE per call (one canvas)."""
        gaze = self.gaze
        F, grid, glance = int(gaze["fixations"]), int(gaze["grid"]), int(gaze["glance"])
        L = _gaze.luminance(rgb)
        maps = self._advance(L)
        an = _gaze._analyse_frame(rgb)          # the Alpha-2 analyse — the attention organ's own frame dict
        if mode == "one":
            v = self._whole(maps, an, glance)
            return {"feats": [v], "fix": [], "windows": [], "residual": [_gaze._residual(v, predicted)]}
        g, _r = _gaze.organs()
        rows = g.gaze_sequence(an, max_fixations=F, predicted=None) if mode == "surprise" else g.random_gaze(an, seed=pic_id, max_fixations=F)
        fix = [(int(z["y"]), int(z["x"])) for z in rows]
        feats, wins = [], []
        for cell in fix:
            _win, tl = _gaze.glance_window(L, cell, grid, glance)      # the gaze gene's own window road; the (top, left) is its
            blocks = [maps[key][tl[0]:tl[0] + glance, tl[1]:tl[1] + glance] for key in _CHANNELS]
            cb = _gaze.colour_block(an, tl[0], tl[1]) if self.colour is not None else None
            feats.append(self._feature(blocks, cb)); wins.append(tl)
        coarse_size = gaze.get("coarse")
        if coarse_size:
            feats.append(self._whole(maps, an, int(coarse_size)))
        residual = [_gaze._residual(v, predicted) for v in feats]
        return {"feats": feats, "fix": fix, "windows": wins, "residual": residual}
