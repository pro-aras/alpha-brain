# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:4x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 2 (EAR.md §4).
"""genome/cochlea.py — the EAR's FIXED front.

E52's gammatone bank + rectify/compress + AGC + modulation-filterbank machinery is sha-PINNED and imported
VERBATIM from `/data/dev/alpha3/experiments/E52-hearing-the-cochlear-front/code/{gammatone.py,front.py}`
-- never reimplemented. E52's own G0 PASS (1.000 held-out, `results/g0-full.json`) was measured on these
exact bytes; the estate's own rule for reusing another tree's fixed front (`genome/gaze.py`'s sha-pinned
import of Alpha 2's `organs/{retina,gaze}.py`) is applied here to a second tree's code, for the same
reason: refusing to re-derive Slaney/Holdsworth IIR coefficients by hand when a measured, audited
implementation already exists (SOLUTIONS #190/#192's law: byte-identical is not cost-identical, and a
re-derivation is where a silent transcription error would hide).

What THIS file adds is what E52 never built (EAR.md §0.3 correction 3: "G1, G2 and every machine arm were
never run... nothing in §2 of this document may cite E52 as evidence"): EVENT DETECTION -- peak-picking on
the BROADBAND onset channel (EAR.md §4's own line: "EVENT publish on onset peak; prominence 2 db gap 60
ms" -- the front's own onset group, summed across bands, never graded by E52) and the per-event TRAIT
vector (`TRAIT sound band 32 + onset-shape 4 + level 1 unit`).

FIXED, never learned (BRIEF.md's bin): every parameter here is a constant set at development (the ERB
spacing, the compression exponent, the AGC time constants, the event threshold) -- nothing in this file
adapts within a life or learns from data. The organ prefilters; the mind (not built here -- AREA sound /
MEET sight sound / MEET sound words are NOT wired by this file, see the builder report) would be where
learning belongs.
"""
from __future__ import annotations

import hashlib
import sys
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.signal import find_peaks, resample_poly

A3 = Path("/data/dev/alpha3/experiments/E52-hearing-the-cochlear-front/code")
PINS = {
    "gammatone.py": "afb637a9e9638798d47758b9caa225eecd9c58bdff836afb7cc964b40c3a97b7",
    "front.py": "91bddd4e00bb94cc5c5f83b1358169df5a1d67a2763d37a14c1873610489c755",
}
_MODULES: Optional[Tuple[object, object]] = None


class CochleaError(Exception):
    """A gene/config the front cannot run, or a pinned source file whose bytes have changed."""


def modules():
    """(gammatone_module, front_module) -- E52's own code, sha-pinned. CochleaError if a byte differs."""
    global _MODULES
    if _MODULES is None:
        for rel, sha in PINS.items():
            p = A3 / rel
            if not p.exists():
                raise CochleaError(f"cochlea front refused: {p} does not exist (E52's tree moved or was deleted)")
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            if h != sha:
                raise CochleaError(f"cochlea front refused: {rel} sha256 {h[:16]}… is not the pinned {sha[:16]}…")
        if str(A3) not in sys.path:
            sys.path.insert(0, str(A3))
        import gammatone as _gt   # noqa: E402
        import front as _fr       # noqa: E402
        _MODULES = (_gt, _fr)
    return _MODULES


# ---------------------------------------------------------------------------------------------- EVENT rule
EVENT_PROMINENCE_DB = 2.0     # EAR.md §4: "EVENT publish on onset peak; prominence 2 db"
EVENT_GAP_S = 0.060           # EAR.md §4: "... gap 60 ms"
N_BANDS = 32                  # EAR.md §4: COCHLEA gammatone erb 32 from 50 to 7800
BAND_LOW_HZ, BAND_HIGH_HZ = 50.0, 7800.0


def _fcoefs(n_bands: int):
    gt, _fr = modules()
    cf = gt.erb_space(BAND_LOW_HZ, BAND_HIGH_HZ, n_bands)
    return cf, gt.make_erb_filters(_fr.FS, cf)


def read_wav_mono(path: Path, target_rate: int = 16000) -> np.ndarray:
    """A mono float32 waveform in [-1, 1], resampled to `target_rate` if the file's own rate differs
    (`scipy.signal.resample_poly`, exact for the rational ratios any sane recording rate gives). A stereo
    file (nchannels != 1) is REFUSED -- SENSE ear-sound's own genome line declares "mono" (machinery.py's
    parser), and mixing channels would silently invent a signal nobody asked for."""
    with wave.open(str(path), "rb") as w:
        nchan, sampwidth, rate, nframes = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(nframes)
    if nchan != 1:
        raise CochleaError(f"read_wav_mono: {path} has {nchan} channels; SENSE ear-sound is mono-only (raised, not resolved)")
    if sampwidth == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sampwidth == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    else:
        raise CochleaError(f"read_wav_mono: {path} has sample width {sampwidth} bytes; only 8/16-bit PCM are read")
    if rate != target_rate:
        from math import gcd
        g = gcd(int(rate), int(target_rate))
        x = resample_poly(x, up=int(target_rate // g), down=int(rate // g))
    return x.astype(np.float64)


def analyse(x: np.ndarray, fs: int = 16000, n_bands: int = N_BANDS,
            prominence_db: float = EVENT_PROMINENCE_DB, gap_s: float = EVENT_GAP_S) -> Dict[str, object]:
    """The full chain (COCHLEA -> HAIRCELL -> AGC -> ONSET -> MODBANK -> EVENT), FIXED parameters
    throughout (EAR.md §4's own line, verbatim): gammatone ERB 32 bands 50-7800 Hz; half-wave rectify,
    power 0.3; per-channel AGC, fast 5 ms / slow 200 ms, gain clamped [0.1, 10]; a broadband onset (the
    per-band onset channels summed, EAR.md §0.3's own description: "one onset channel per band ... plus a
    broadband onset sum"); a 4-band modulation filterbank (2-4, 4-8, 8-16, 16-32 Hz) on the AGC'd
    envelope; EVENTS = peaks of the broadband onset's dB trace with prominence >= `prominence_db` and a
    minimum gap of `gap_s` between events (find_peaks' own `distance` in samples).

    Returns {"events": [{"t_s": float, "trait": (37,) unit-length float array, "band": (32,), "onset_shape":
    (4,), "level": float}, ...], "n_bands": int, "duration_s": float}. An x with no peak clearing the bar
    returns {"events": []} -- SILENCE PUBLISHES NOTHING (EAR.md §5 Q1's own recommendation; the sense
    thread built on this function publishes one tape row per event in this list, zero if this list is
    empty)."""
    gt, fr = modules()
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return {"events": [], "n_bands": n_bands, "duration_s": 0.0}
    cf, fcoefs = _fcoefs(n_bands)
    chan = gt.erb_filterbank(x, fcoefs)                         # (n_bands, N) -- fine structure, at fs
    compressed = fr.rectify_compress(chan, exponent=fr.COMPRESS_EXP)   # E52's own 0.3 exponent
    env = fr.envelope_lpf(compressed, fs=fs)                    # (n_bands, N)
    agc, onset = fr.agc_and_onset(env, fs=fs)                   # (n_bands, N) each
    broadband_onset = onset.sum(axis=0)                          # EAR.md §0.3: "plus a broadband onset sum"
    mod, mod_fs = fr.modulation_bank(agc, fs=fs)                # (n_bands, 4, T@mod_fs)

    eps = 1e-9
    onset_db = 20.0 * np.log10(broadband_onset + eps)
    distance = max(1, int(round(gap_s * fs)))
    peaks, props = find_peaks(onset_db, prominence=prominence_db, distance=distance)

    events: List[Dict[str, object]] = []
    T_mod = mod.shape[-1]
    for i in peaks:
        t_s = float(i) / fs
        band = agc[:, i].astype(np.float64)                     # the band profile AT the onset instant
        mod_idx = min(T_mod - 1, max(0, int(round(i * mod_fs / fs))))
        onset_shape = mod[:, :, mod_idx].mean(axis=0).astype(np.float64)   # (4,) — averaged across channels
        level = float(env[:, i].mean())                          # a single loudness number for this instant
        raw = np.concatenate([band, onset_shape, [level]])
        n = np.linalg.norm(raw)
        trait = (raw / n) if n > 0 else raw
        events.append({"t_s": t_s, "trait": trait, "band": band, "onset_shape": onset_shape, "level": level})
    return {"events": events, "n_bands": n_bands, "duration_s": float(x.size) / fs,
            "onset_db_peak_props": {k: [float(v) for v in vals] for k, vals in props.items() if k == "prominences"}}


def event_rate(events_or_x, fs: int = 16000, **kwargs) -> float:
    """events/second — either called on an already-`analyse`d dict, or on a raw waveform (analyses it
    first). A convenience wrapper for T7's own count-before-wiring discipline."""
    if isinstance(events_or_x, dict):
        result = events_or_x
    else:
        result = analyse(events_or_x, fs=fs, **kwargs)
    dur = result["duration_s"]
    return (len(result["events"]) / dur) if dur > 0 else 0.0
