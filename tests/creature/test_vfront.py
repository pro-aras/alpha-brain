# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 02:12 +0400 — AMENDMENT-1 (135f141): the shape asserts to the
# re-declared 144 (4×28 + 32) + the amendment §2.3's gate (feature length == the pinned bench genome's sight_dim()).
# RED first: the front still composed 480 when these asserts changed. The plants stand unchanged (the maps didn't move).
# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400 — PREREG-OPEN-WORLD-3 §2/§4: the plants, written
# FIRST (run RED before creature/senses/vfront.py existed), the law's exact bars, the doctored twin CAUGHT (G-PLANT).
"""tests/creature/test_vfront.py — PREREG-OPEN-WORLD-3's planted signatures of the innate video front
(creature/senses/vfront.py), with the law's exact bars, never tuned; §2.6's composition as re-declared by
AMENDMENT-1 (135f141): the per-channel band is the FRONT'S OWN declared spec ("pool8", "hog12", "unit") = 28
numbers a channel — registration-preserving steps only, no centre/thresh/blur — so the glance feature is
[band(ON)·band(OFF)·band(T-ON)·band(T-OFF)·colour_block] = 4×28 + 32 = exactly the genome's own 144, gated
against the G-TAPE-pinned bench genome's sight_dim() forever (amendment §2.3).

  P1 (M-SIGN): per-pixel ON·OFF == 0 and T-ON·T-OFF == 0 (rectification, exact); a vertical step edge:
      ON edge-mass on the increment side ≥ 4× the decrement side AND > 0, OFF the mirror. (The > 0 clause
      is the bar's own meaning — an "edge-mass" that is exactly zero carries no edge; without it a zeroed
      map would pass 0 ≥ 4·0 vacuously and the doctored twin would escape. Declared here, never moved.)
  P3 (M-SIGN): a uniform full-field canvas → the sustained maps (ON, OFF) exactly 0 (center-surround kills DC).
  P4 (M-SIGN): a bright square translated 8 px right → T-ON mass at the leading band ≥ 4× trailing (and > 0),
      T-OFF the mirror.
  P2 (M-ADAPT): the same step edge at contrast g and 2g → cosine of the pooled-normalized ON maps ≥ 0.99
      (derived: a linear filter under R/(β+mean|R|) is gain-invariant up to β — the two normalized maps are
      scalar multiples of one raw map, so the cosine is 1 up to float; printed).
  P5 (M-ADAPT): a square flashed 8 times (present/absent per frame) → the normalized transient mass
      (mean|T-ON|+mean|T-OFF|) of the 8th flash ≤ 0.5 × the 1st; the flash strength mean|D| ≥ 0.05 printed
      (the o-recursion's asymptote gives r8/r1 = (β+o_0)/(β+o_before8) ≈ 0.12 for this plant, derived in
      records/open-world-3/bench/reading.txt — never fitted).
  THE NEGATIVE CONTROL (G-PLANT): a doctored front (OFF map zeroed; pooled normalization removed) FAILS the
      bars — P1's OFF mirror (no positive mass) and P5's decay (the raw-|D| operating point never rises
      enough) — and the plant asserts the doctoring changed the maps (the instrument CAN fail).

Fixtures are synthetic 128×128 canvases built in the test; the bench genome's own RETINA/GAZE/colour values
are used for the glances-dict shape check (the 112-tower reads its seal, as every replay does).
"""
from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from creature.senses.vfront import ALPHA, BETA, FRONT_SPEC, SIGMA_C, SIGMA_S, VideoFront
from genome.machinery import parse_genome, retina_dim

CANVAS = 128
# the bench genome's own values (records/open-world-2/bench/GENOME.genome): GAZE / SENSE colour
BENCH_GENOME = Path(__file__).resolve().parents[2] / "docs" / "organism" / "whole" / "records" / "open-world-2" / "bench" / "GENOME.genome"
BENCH_GAZE = {"fixations": 4, "grid": 16, "canvas": 128, "glance": 32, "ink": "border", "coarse": 32}
BENCH_COLOUR = {"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"}


def _grey(v: int) -> np.ndarray:
    return np.full((CANVAS, CANVAS, 3), v, dtype=np.uint8)


def _edge(dark: int, bright: int, at: int = 64) -> np.ndarray:
    """A vertical step edge: left half `dark`, right half `bright` (the increment side is x ≥ `at`)."""
    rgb = _grey(dark)
    rgb[:, at:, :] = bright
    return rgb


def _with_square(base: int, sq: int, top: int, left: int, side: int) -> np.ndarray:
    rgb = _grey(base)
    rgb[top:top + side, left:left + side, :] = sq
    return rgb


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a.reshape(-1), b.reshape(-1)) / (np.linalg.norm(a) * np.linalg.norm(b)))


class DoctoredFront(VideoFront):
    """G-PLANT's doctored twin: the OFF map zeroed and the pooled normalization removed — the two
    defect classes named by the law, in one twin. The tests below prove the bars CATCH it."""

    def _pool(self, r: np.ndarray) -> np.ndarray:
        return r                                   # the normalization removed

    def _sustained(self, L: np.ndarray):
        on, off = super()._sustained(L)
        return on, np.zeros_like(off)              # the OFF map zeroed


class TestVideoFrontPlants(unittest.TestCase):
    def test_p1_rectification_exact_and_step_edge_split(self) -> None:
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        m = front.maps(_edge(60, 180))
        self.assertTrue(np.array_equal(m["ON"] * m["OFF"], np.zeros((CANVAS, CANVAS))))
        self.assertTrue(np.array_equal(m["T-ON"] * m["T-OFF"], np.zeros((CANVAS, CANVAS))))
        # a second, different frame so the transient maps are nonzero, then their rectification is read again
        m2 = front.maps(_edge(60, 200))
        self.assertTrue(np.array_equal(m2["T-ON"] * m2["T-OFF"], np.zeros((CANVAS, CANVAS))))
        self.assertGreater(float(np.abs(m2["T-ON"]).sum()) + float(np.abs(m2["T-OFF"]).sum()), 0.0)
        # the vertical step edge: ON edge-mass on the increment side ≥ 4× the decrement side, OFF the mirror
        on_inc, on_dec = float(m["ON"][:, 64:].sum()), float(m["ON"][:, :64].sum())
        off_inc, off_dec = float(m["OFF"][:, 64:].sum()), float(m["OFF"][:, :64].sum())
        self.assertGreater(on_inc, 0.0)
        self.assertGreaterEqual(on_inc, 4.0 * on_dec)
        self.assertGreater(off_dec, 0.0)                        # the mirror — an edge-mass must EXIST
        self.assertGreaterEqual(off_dec, 4.0 * off_inc)
        print(f"\nP1: ON inc {on_inc:.6f} dec {on_dec:.6f} | OFF inc {off_inc:.6f} dec {off_dec:.6f} "
              f"(bars ≥ 4× with the winning side > 0)")

    def test_p3_uniform_field_kills_dc_exactly(self) -> None:
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        m = front.maps(_grey(128))
        self.assertTrue(np.array_equal(m["ON"], np.zeros((CANVAS, CANVAS))))
        self.assertTrue(np.array_equal(m["OFF"], np.zeros((CANVAS, CANVAS))))
        self.assertTrue(np.array_equal(m["T-ON"], np.zeros((CANVAS, CANVAS))))   # first frame: T maps exactly 0
        self.assertTrue(np.array_equal(m["T-OFF"], np.zeros((CANVAS, CANVAS))))
        m2 = front.maps(_grey(128))
        self.assertTrue(np.array_equal(m2["T-ON"], np.zeros((CANVAS, CANVAS))))  # a static world: no transient, ever
        self.assertTrue(np.array_equal(m2["T-OFF"], np.zeros((CANVAS, CANVAS))))

    def test_p4_translation_leading_trailing_split(self) -> None:
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        top, left0, side, shift = 48, 40, 32, 8
        front.maps(_with_square(30, 200, top, left0, side))
        m = front.maps(_with_square(30, 200, top, left0 + shift, side))
        lead = (slice(top, top + side), slice(left0 + side, left0 + side + shift))      # new ground the square moved onto
        trail = (slice(top, top + side), slice(left0, left0 + shift))                   # old ground it left
        ton_lead, ton_trail = float(m["T-ON"][lead].sum()), float(m["T-ON"][trail].sum())
        toff_lead, toff_trail = float(m["T-OFF"][lead].sum()), float(m["T-OFF"][trail].sum())
        self.assertGreater(ton_lead, 0.0)
        self.assertGreaterEqual(ton_lead, 4.0 * ton_trail)
        self.assertGreater(toff_trail, 0.0)
        self.assertGreaterEqual(toff_trail, 4.0 * toff_lead)
        print(f"\nP4: T-ON lead {ton_lead:.6f} trail {ton_trail:.6f} | T-OFF lead {toff_lead:.6f} trail {toff_trail:.6f}")

    def test_p2_gain_invariance_cosine(self) -> None:
        # the same edge (dark 100, step g=50) at contrast 2g (step 100): the pooled-normalized ON maps
        m_g = VideoFront(BENCH_GAZE, BENCH_COLOUR).maps(_edge(100, 150))
        m_2g = VideoFront(BENCH_GAZE, BENCH_COLOUR).maps(_edge(100, 200))
        cos = _cos(m_g["ON"], m_2g["ON"])
        self.assertGreaterEqual(cos, 0.99)
        print(f"\nP2: cosine of pooled-normalized ON maps at g and 2g = {cos:.12f} (bar ≥ 0.99)")

    def test_p5_operating_point_adaptation_decays_the_flash(self) -> None:
        side = 10
        frames = [_grey(30) if k % 2 == 0 else _with_square(30, 255, 48, 48, side) for k in range(16)]
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        masses, strengths = [], []
        for f in frames:
            m = front.maps(f)
            masses.append(float(m["T-ON"].mean()) + float(m["T-OFF"].mean()))
            strengths.append(float(np.abs(m["D"]).mean()))
        self.assertEqual(masses[0], 0.0)                       # the first frame of a tape: T maps exactly 0
        flashes = masses[1::2]                                 # the 8 present-transitions
        self.assertEqual(len(flashes), 8)
        strength = float(np.mean(strengths[1:]))
        self.assertGreaterEqual(strength, 0.05)                # the plant's declared flash strength, printed
        ratio = flashes[7] / flashes[0]
        self.assertLessEqual(flashes[7], 0.5 * flashes[0])
        print(f"\nP5: flash 1 t_mass {flashes[0]:.6f}, flash 8 t_mass {flashes[7]:.6f}, "
              f"r8/r1 {ratio:.4f} (bar ≤ 0.5); mean|D| {strength:.4f} (declared ≥ 0.05)")

    def test_negative_control_the_doctored_front_is_caught(self) -> None:
        # the doctoring CHANGES the maps (RULES §11: the plant asserts it changed the bytes)
        true_m = VideoFront(BENCH_GAZE, BENCH_COLOUR).maps(_edge(60, 180))
        doc_m = DoctoredFront(BENCH_GAZE, BENCH_COLOUR).maps(_edge(60, 180))
        self.assertFalse(np.array_equal(true_m["OFF"], doc_m["OFF"]))
        self.assertFalse(np.array_equal(true_m["ON"], doc_m["ON"]))     # the removed normalization moves ON too
        # P1's OFF mirror FAILS for the twin: no positive decrement-side mass exists (0 ≥ 4·0 would be vacuous)
        off_dec = float(doc_m["OFF"][:, :64].sum())
        self.assertFalse(off_dec > 0.0 and off_dec >= 4.0 * float(doc_m["OFF"][:, 64:].sum()),
                         "the doctored twin must FAIL P1's OFF mirror")
        # P5's decay FAILS for the twin: without the pooled normalization the operating point tracks a raw
        # mean|D| too small to divide the 8th flash below half the 1st
        side = 10
        frames = [_grey(30) if k % 2 == 0 else _with_square(30, 255, 48, 48, side) for k in range(16)]
        doc = DoctoredFront(BENCH_GAZE, BENCH_COLOUR)
        masses = []
        for f in frames:
            m = doc.maps(f)
            masses.append(float(m["T-ON"].mean()) + float(m["T-OFF"].mean()))
        flashes = masses[1::2]
        self.assertEqual(len(flashes), 8)
        ratio = flashes[7] / flashes[0]
        self.assertGreater(ratio, 0.5, "the doctored twin must FAIL P5's ≤ 0.5 decay bar")
        print(f"\nG-PLANT: doctored twin — P1 OFF-mirror fails (dec mass {off_dec:.6f}); "
              f"P5 r8/r1 {ratio:.4f} > 0.5 — CAUGHT")

    def test_glances_dict_shape_and_determinism(self) -> None:
        # the glances-dict shape (mind.py:2414's contract): feats/fix/windows/residual; 144 numbers a located
        # glance (4×28 + 32, AMENDMENT-1's re-declared composition), unit-normalised once; the coarse fifth when
        # the genome declares it; the first frame's T maps exactly 0; two fresh fronts over the same frames
        # byte-identical (temporal state included)
        seq = [_edge(60, 180), _with_square(30, 200, 48, 40, 32), _with_square(30, 200, 48, 48, 32)]
        outs = []
        for _ in range(2):
            front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
            outs.append([front.glances(f, "surprise", f"plant-{i}") for i, f in enumerate(seq)])
        for a, b in zip(*outs):
            self.assertEqual(set(a), {"feats", "fix", "windows", "residual"})
            self.assertEqual(len(a["feats"]), len(a["residual"]))
            self.assertEqual(len(a["fix"]), BENCH_GAZE["fixations"])
            self.assertEqual(len(a["windows"]), BENCH_GAZE["fixations"])
            self.assertEqual(len(a["feats"]), BENCH_GAZE["fixations"] + 1)   # + the declared coarse glance
            for v in a["feats"]:
                self.assertEqual(v.shape, (144,))
                self.assertAlmostEqual(float(np.linalg.norm(v)), 1.0, places=12)
                self.assertIsNone(a["residual"][0])
            for x, y in zip(a["feats"], b["feats"]):
                self.assertTrue(np.array_equal(x, y), "two fresh fronts over the same frames must agree to the byte")
            self.assertEqual(a["fix"], b["fix"])
            self.assertEqual(a["windows"], b["windows"])
        # the instrument values the journal's `front` key carries (§2.7): t_mass and o after each canvas
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        front.glances(seq[0], "surprise", "plant-0")
        self.assertEqual(front.last_t_mass, 0.0)               # first frame: T maps exactly 0 → t_mass 0
        self.assertEqual(front.last_o, 0.0)                    # o_0 = 0 and mean|D| = 0 on the first frame
        front.glances(seq[1], "surprise", "plant-1")
        self.assertGreater(front.last_t_mass, 0.0)
        self.assertGreater(front.last_o, 0.0)                  # the causal update has run (α, the declared recursion)

    def test_amendment_gate_feature_length_equals_sight_dim(self) -> None:
        # AMENDMENT-1 §2.3's gate, forever: the composed feature's length == the G-TAPE-pinned bench genome's
        # sight_dim() — the VOID road's incompatibility class (a feature the organism's sight area cannot hold)
        # is asserted against, on the pinned genome itself, never on a copy of its arithmetic.
        g = parse_genome(BENCH_GENOME.read_text())
        self.assertEqual(g.sight_dim(), 144)                              # the bench genome's own anatomy (112 + 32)
        self.assertEqual(retina_dim(FRONT_SPEC, BENCH_GAZE["glance"]), 28)  # the amendment §2.1's own arithmetic
        front = VideoFront(BENCH_GAZE, BENCH_COLOUR)
        out = front.glances(_edge(60, 180), "surprise", "amendment-gate")
        self.assertEqual(len(out["feats"]), BENCH_GAZE["fixations"] + 1)
        for v in out["feats"]:
            self.assertEqual(len(v), g.sight_dim(),
                             "the composed feature must equal the pinned bench genome's sight_dim() (AMENDMENT-1 §2.3)")
        # and the band spec is registration-preserving: no centre/thresh/blur step (AMENDMENT-1 §2.1's own words)
        self.assertFalse(any(s.startswith(("centre", "thresh", "blur")) for s in FRONT_SPEC))

    def test_declared_constants(self) -> None:
        # the law §2's DECLARED machine-form constants, pinned so an edit to them is a loud event
        self.assertEqual((SIGMA_C, SIGMA_S, BETA, ALPHA), (1.0, 3.0, 0.01, 0.2))
        # AMENDMENT-1 §2.1's DECLARED band spec (the FRONT'S OWN, never the genome's RETINA line), pinned likewise
        self.assertEqual(tuple(FRONT_SPEC), ("pool8", "hog12", "unit"))


if __name__ == "__main__":
    unittest.main()
