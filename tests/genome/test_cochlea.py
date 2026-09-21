# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 23:0x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 2.
"""test_cochlea.py — genome/cochlea.py: the sha-pin refuses on a changed byte (mirroring genome/gaze.py's
own A2-organ pin discipline), silence produces zero events, and T1's frequency-path plant (EAR.md §4 T1,
the ear's OWN toy) passes at its measured ceiling while a properly-blind control sits at chance -- pinned
here as a real regression, not only a one-off scratch measurement (the pair choice and the reasoning for
it are in the builder report; this file only re-runs the FINAL, non-leaking design)."""
from __future__ import annotations

import math
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from genome import cochlea

A3_PRESENT = Path("/data/dev/alpha3/experiments/E52-hearing-the-cochlear-front/code/gammatone.py").exists()


class TestPin(unittest.TestCase):
    def test_real_files_match_the_pin(self) -> None:
        gt, fr = cochlea.modules()
        self.assertTrue(hasattr(gt, "erb_space"))
        self.assertTrue(hasattr(fr, "agc_and_onset"))

    def test_changed_byte_refuses(self) -> None:
        cochlea._MODULES = None   # force re-check
        with mock.patch.dict(cochlea.PINS, {"gammatone.py": "0" * 64}):
            with self.assertRaises(cochlea.CochleaError) as cm:
                cochlea.modules()
        self.assertIn("gammatone.py", str(cm.exception))
        cochlea._MODULES = None   # leave the module cache clean for later tests


@unittest.skipUnless(A3_PRESENT, "E52's tree is not present on this box")
class TestSilence(unittest.TestCase):
    def test_zero_signal_zero_events(self) -> None:
        r = cochlea.analyse(np.zeros(16000 * 5))
        self.assertEqual(r["events"], [])
        self.assertEqual(cochlea.event_rate(r), 0.0)

    def test_empty_signal(self) -> None:
        r = cochlea.analyse(np.zeros(0))
        self.assertEqual(r["events"], [])
        self.assertEqual(r["duration_s"], 0.0)


@unittest.skipUnless(A3_PRESENT, "E52's tree is not present on this box")
class TestAnalyseShape(unittest.TestCase):
    def test_a_real_tone_produces_a_unit_trait_vector(self) -> None:
        fs = 16000
        t = np.arange(int(0.3 * fs)) / fs
        ramp_n = int(0.05 * fs)
        ramp = np.ones_like(t); ramp[:ramp_n] = np.linspace(0, 1, ramp_n); ramp[-ramp_n:] = np.linspace(1, 0, ramp_n)
        x = 0.3 * np.sin(2 * np.pi * 1000.0 * t) * ramp
        r = cochlea.analyse(x, fs=fs)
        self.assertGreaterEqual(len(r["events"]), 1)
        ev = r["events"][0]
        self.assertEqual(ev["trait"].shape, (cochlea.N_BANDS + 4 + 1,))
        self.assertAlmostEqual(float(np.linalg.norm(ev["trait"])), 1.0, places=5)
        self.assertEqual(ev["band"].shape, (cochlea.N_BANDS,))
        self.assertEqual(ev["onset_shape"].shape, (4,))


@unittest.skipUnless(A3_PRESENT, "E52's tree is not present on this box")
class TestT1FrequencyPathPlant(unittest.TestCase):
    """EAR.md §4 T1, the ear's own toy: a 4-bit code where each bit chooses between two neighbouring
    carrier frequencies, identical amplitude/duration/schedule regardless of bit -- the message is ONLY in
    frequency. Channel pairs are chosen >= 5x the envelope low-pass cutoff (320 Hz, front.py's own
    ENV_LPF_HZ) -- an earlier choice near/below that cutoff made the "blind broadband channel" control leak
    (+315% / +8-10% relative level difference, measured and reported in the builder report); this pin uses
    the corrected, non-leaking pairs."""

    FS = 16000
    PIP_S = 0.20
    RAMP_S = 0.05
    AMP = 0.3
    PAIR_IDX = [(18, 19), (22, 23), (25, 26), (29, 30)]   # centre frequencies ~1.6-6.3 kHz

    @classmethod
    def setUpClass(cls):
        cls.gt, cls.fr = cochlea.modules()
        cls.cf, cls.fcoefs = cochlea._fcoefs(cochlea.N_BANDS)
        cls.pair_hz = [(float(cls.cf[a]), float(cls.cf[b])) for a, b in cls.PAIR_IDX]

    def _synth_pip(self, f: float) -> np.ndarray:
        pip_n = int(self.PIP_S * self.FS)
        ramp_n = int(self.RAMP_S * self.FS)
        t = np.arange(pip_n) / self.FS
        ramp = np.ones(pip_n)
        up = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp_n))
        ramp[:ramp_n] = up; ramp[-ramp_n:] = up[::-1]
        return self.AMP * np.sin(2 * np.pi * f * t) * ramp

    def _front_agc(self, x: np.ndarray) -> np.ndarray:
        chan = self.gt.erb_filterbank(x, self.fcoefs)
        compressed = self.fr.rectify_compress(chan, exponent=self.fr.COMPRESS_EXP)
        env = self.fr.envelope_lpf(compressed, fs=self.FS)
        agc, _onset = self.fr.agc_and_onset(env, fs=self.FS)
        return agc

    def _front_decode(self, code) -> list:
        centre = int(self.PIP_S * self.FS) // 2
        bits = []
        for i, (a, b) in enumerate(self.PAIR_IDX):
            f = self.pair_hz[i][code[i]]
            agc = self._front_agc(self._synth_pip(f))
            bits.append(1 if agc[b, centre] > agc[a, centre] else 0)
        return bits

    def _blind_broadband_decode(self, code) -> list:
        centre = int(self.PIP_S * self.FS) // 2
        levels = []
        for i, _pair in enumerate(self.PAIR_IDX):
            f = self.pair_hz[i][code[i]]
            x = self._synth_pip(f)
            chan = x[None, :]
            compressed = self.fr.rectify_compress(chan, exponent=self.fr.COMPRESS_EXP)
            env = self.fr.envelope_lpf(compressed, fs=self.FS)
            agc, _onset = self.fr.agc_and_onset(env, fs=self.FS)
            levels.append(float(agc[0, centre]))
        med = float(np.median(levels))
        return [1 if lv > med else 0 for lv in levels]

    def test_front_decodes_at_ceiling(self) -> None:
        rng = np.random.default_rng(20260921)
        codes = [[int(rng.integers(0, 2)) for _ in range(4)] for _ in range(20)]
        bit_correct = code_correct = 0
        for code in codes:
            d = self._front_decode(code)
            bit_correct += sum(int(a == b) for a, b in zip(d, code))
            code_correct += int(d == code)
        self.assertEqual(bit_correct, 20 * 4, "the front must decode every bit correctly (ceiling 1.0)")
        self.assertEqual(code_correct, 20)

    def test_blind_broadband_control_leaks_below_significance(self) -> None:
        """The brief's own refusal rule: "[the blind control] must sit within the shuffled twin's noise
        band around 0.5 ... If it rises above chance, the plant leaks through the envelope and the design
        is refused before the front is judged at all." A binomial two-sided check at N=200 bits, alpha
        ~0.01 (|z| < 2.6) rather than a bare "close to 0.5" eyeball."""
        rng = np.random.default_rng(20260921)
        codes = [[int(rng.integers(0, 2)) for _ in range(4)] for _ in range(50)]
        bit_correct = 0
        n = 0
        for code in codes:
            bd = self._blind_broadband_decode(code)
            bit_correct += sum(int(a == b) for a, b in zip(bd, code))
            n += 4
        p = bit_correct / n
        z = (bit_correct - n * 0.5) / math.sqrt(n * 0.25)
        self.assertLess(abs(z), 2.6, f"blind control per-bit accuracy {p:.3f} (z={z:.2f}) is significantly "
                                      f"off chance -- the plant leaks and this design must be refused")


if __name__ == "__main__":
    unittest.main()
