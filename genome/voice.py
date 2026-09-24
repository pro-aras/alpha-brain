# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:09 +0400 — A4L-VOICE task 0/1 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3): the drawn world's VOICE — a fixed formant chord per word, a NAME, not a voice.
"""genome/voice.py — the world's voice: each drawn thing's name as a fixed three-formant chord.

A4-LADDER-PREREG §2.3, verbatim: «a fixed formant chord for that word — three sinusoids at F1 ∈ [300, 900] Hz,
F2 ∈ [900, 2400] Hz, F3 ∈ [2400, 3400] Hz drawn from sha256(word), 0.45 s, 10 ms raised-cosine ramps, 16 kHz
mono, the same every time: a NAME, not a voice».

The mapping from sha256(word) to the three frequencies (this builder's, fixed here once, never tuned after V0):
the digest's first three big-endian 32-bit words u0, u1, u2 (each / 2**32, in [0, 1)) place F1, F2, F3 linearly
inside their bands. The three partials carry EQUAL amplitude, zero phase; the chord's peak is held at LEVEL (one
fixed level for every word); the ramps are raised-cosine (Hann halves) of RAMP_S at each end. The waveform is
quantised to 16-bit PCM — exactly the samples a wav file of it holds — and read back as `pcm / 32768.0`, the
SAME scaling `genome.cochlea.read_wav_mono` applies to a 16-bit wav, so `trait(word)` is byte-for-byte what the
ear door (creature/senses/ear.py) would publish for the same chord dropped into its folder as a wav.

`trait(word)` runs the SEALED E52 front (`genome.cochlea.analyse`, sha-pinned, never changed here) and returns
the FIRST event's 37-number trait (band 32 + onset-shape 4 + level 1, unit length). V0 (tools/voice_bands.py, run
2026-09-23 11:10 +0400) measured 6–7 events per chord, not one: the first at 4.7–7.7 ms — INSIDE the 10 ms rising ramp,
so the trait is the AGC'd band profile mid-onset — and the rest the onset detector re-firing on a stationary chord
(66–126 ms on), a front artefact. The FIRST event is the chord's trait, said here and in the report.

`shift` scales all three formants (V1b's held-out «the same name in another voice»: ±4 %).

Pure: no clock, no rng, no file I/O (the maker writes the wav for audit, never this module). A SENSE imports it
(creature/world_maker.py), so it obeys the writer law too: it never imports Organism/machinery and never writes
state/journal/memory (tools/gate_g4.py step 1 walks it; tests/creature/test_writer_sweep.py plants an offender
shaped like it).
"""
from __future__ import annotations

import functools
import hashlib
from typing import Dict, List, Optional, Tuple

import numpy as np

RATE = 16000                 # 16 kHz mono (the PREREG's own number; SENSE ear-sound wav 16000 mono)
DURATION_S = 0.45            # 0.45 s
RAMP_S = 0.010               # 10 ms raised-cosine ramps
LEVEL = 0.5                  # the chord's fixed peak amplitude (full scale 1.0) — one level for every word
BANDS: Tuple[Tuple[float, float], ...] = ((300.0, 900.0), (900.0, 2400.0), (2400.0, 3400.0))   # F1, F2, F3


class VoiceError(Exception):
    """A chord the voice cannot make (an empty word), or a chord the sealed front heard no event in."""


def formants(word: str, shift: float = 1.0) -> Tuple[float, float, float]:
    """(F1, F2, F3) in Hz for `word`: sha256(word)'s first three 32-bit words placed linearly in their bands,
    times `shift` (1.0 = the name itself; 1.04 / 0.96 = V1b's held-out voices)."""
    if not word:
        raise VoiceError("the voice names a word; an empty word has no chord")
    d = hashlib.sha256(word.encode("utf-8")).digest()
    out = []
    for i, (lo, hi) in enumerate(BANDS):
        u = int.from_bytes(d[4 * i: 4 * i + 4], "big") / float(2 ** 32)
        out.append((lo + (hi - lo) * u) * float(shift))
    return (out[0], out[1], out[2])


def chord_pcm16(word: str, shift: float = 1.0) -> np.ndarray:
    """The chord as 16-bit PCM samples (int16, RATE Hz, mono) — the exact samples the maker's audit wav holds."""
    f = formants(word, shift)
    n = int(round(DURATION_S * RATE))
    t = np.arange(n, dtype=np.float64) / RATE
    x = np.zeros(n, dtype=np.float64)
    for fk in f:
        x += np.sin(2.0 * np.pi * fk * t)
    peak = float(np.max(np.abs(x)))
    x = x * (LEVEL / peak) if peak > 0 else x
    r = int(round(RAMP_S * RATE))
    if r > 0:
        ramp = 0.5 * (1.0 - np.cos(np.pi * np.arange(r, dtype=np.float64) / r))    # raised cosine, 0 -> 1
        x[:r] *= ramp
        x[n - r:] *= ramp[::-1]
    return np.clip(np.round(x * 32767.0), -32768, 32767).astype(np.int16)


def waveform(word: str, shift: float = 1.0) -> np.ndarray:
    """float64 in [-1, 1): the PCM read back exactly as genome.cochlea.read_wav_mono reads a 16-bit wav."""
    return chord_pcm16(word, shift).astype(np.float64) / 32768.0


def analyse(word: str, shift: float = 1.0) -> Dict[str, object]:
    """The sealed E52 front's full result for the chord (genome.cochlea.analyse at RATE — the ear door's own call)."""
    from genome import cochlea
    return cochlea.analyse(waveform(word, shift), fs=RATE)


@functools.lru_cache(maxsize=512)
def _first_event(word: str, shift: float) -> Tuple[float, float, Tuple[float, ...]]:
    """(t_s, level, trait) of the chord's FIRST event — cached: a chord is a pure function of (word, shift) and the front
    costs ≈ 0.1 s a chord (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:35 +0400 — the maker speaks every
    5 s beside a live life; the load guard of A4-LADDER-PREREG §1.8 reads the life's backlog)."""
    ev = analyse(word, shift)["events"]
    if not ev:
        raise VoiceError(f"the sealed front heard no event in the chord of {word!r} (shift {shift})")
    e = ev[0]
    return float(e["t_s"]), float(e["level"]), tuple(float(v) for v in e["trait"])


def event(word: str, shift: float = 1.0) -> Dict[str, object]:
    """The chord's FIRST event: {"t_s", "level", "trait"} (trait a fresh float64 array — the cache is never handed out)."""
    t_s, level, tr = _first_event(word, float(shift))
    return {"t_s": t_s, "level": level, "trait": np.asarray(tr, dtype=np.float64)}


def trait(word: str, shift: float = 1.0) -> np.ndarray:
    """The FIRST event's 37-number trait (unit length, float64). VoiceError when the front hears no event."""
    return event(word, shift)["trait"]


def trait_f32(word: str, shift: float = 1.0) -> np.ndarray:
    """The trait as the float32 the tape carries (the ear door publishes `trait.astype('float32').tobytes()`),
    decoded back to float64 exactly as creature/mind.py decodes an ear-sound payload."""
    return trait(word, shift).astype(np.float32).astype(np.float64)


def wav_bytes(word: str, shift: float = 1.0) -> bytes:
    """A 16-bit mono RIFF wav of the chord (the maker's audit copy under its truth dir; the mind never reads it)."""
    import io
    import wave
    pcm = chord_pcm16(word, shift)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()
