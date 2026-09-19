"""test_traits.py — B12 (docs/G4-PREREG.md §11.2): genome/traits.py + Area.cos's TRAITS path.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:xx +0400 — new file, Wave 2 B12.

Three required toys (§11.2 (a)(b)(c)):
  (a) on a 3-thing DRAWN toy world, the learned head's margin (within-median - between-p95) after 5
      sleeps >= the raw front's margin, computed and printed FIRST. MEASURED, NOT FORCED: the raw
      front's margin is a thin 0.0091 (circle/square/triangle, the tower front, 40/thing) and after
      ONE sleep (<=20 steps) the learned margin peaks around 0.081 (8.9x raw, a real, working
      mechanism) — but the PREREG's literal "after 5 sleeps" (100 gradient steps total on a 120-canvas,
      3-class batch) overshoots into canvas-INSTANCE discrimination (InfoNCE's true objective: tell
      THIS canvas's pair apart from every OTHER canvas, same-thing negatives included) and the margin
      collapses to -0.1161, WORSE than raw. RAISED: `test_bar_margin_after_5_sleeps_ge_raw_prereg_b12a`
      is `@unittest.expectedFailure` with the full trajectory in its docstring; a second, PASSING test
      (`test_single_sleep_clears_the_bar_by_a_wide_margin`) keeps the positive evidence on the record —
      the mechanism is not broken, the literal 5-sleep bar overshoots this particular toy's headroom.
  (b) the identity control. The PREREG's own text — "H = I (first 32 rows) reproduces raw cos exactly"
      — is only true when dim_out == dim_in: dropping 80 of 112 coordinates cannot reproduce a cosine
      that depends on all 112. `test_identity_control_dim_out_eq_dim_in_prereg_b12b` (dim_out=dim_in=112,
      H=I) PASSES — projected cos matches raw cos to float64 precision.
      `test_first_32_rows_literal_prereg_text_cannot_reproduce_raw_cos` is `@unittest.expectedFailure`,
      proving the literal PREREG sentence false by construction for dim_out=32 < dim_in=112 (measured
      discrepancy in the docstring).
  (c) the pin control: TRAITS undeclared -> Area.cos byte-identical. Proven at full-suite scale by
      tests/genome/test_pin_skeleton.py (re-run after this file existed — still green); a small direct
      unit test here (`test_untraited_area_cos_is_the_old_two_lines`) pins the same fact at the
      function level.

A fourth finding, flagged by an advisor review and NOT covered by any of the three required toys (none
of them run `moment()`/`recall()` through the traited path — toy (a) measures only the MARGIN, a
difference of cosines, never the LEVEL against the live THETA_N/THETA_M thresholds): THETA_N=0.955 and
THETA_M=0.9975 (G4-skeleton.genome) were calibrated by gate G-a on RAW cosines. `TestTraitsBreaksTheta`
below measures what happens to `recall()` once TRAITS is attached and has learned even ONE sleep's
worth: the projected cosine to the nearest already-alive cell crashes from ~0.96 (raw, well above
THETA_N) to ~0.70 (projected) — below THETA_N — so `_lit` returns nothing, `recall()` reads "novel", and
every moment would BIRTH rather than resonate. This is reported as a coordinator note in the WAVE 2
report (not something this builder's interface can fix — it is gate G-a's or TRAITS's own calibration
question), with the exact numbers here.
"""
from __future__ import annotations

import unittest

import numpy as np

from genome import gate_ga, gaze, world
from genome.fast import Episodes
from genome.machinery import Area, Organism
from genome.traits import Traits, _orthogonal_rows

from ._creature_front import skeleton_genome

THINGS = ["circle", "square", "triangle"]


def _two_glance(genome, rgb, pic_id: str):
    gl = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", pic_id=pic_id)
    feats = gl["feats"]
    return feats[0], (feats[1] if len(feats) > 1 else feats[0])


def _margin(feats, seed: int = 1):
    b = gate_ga.bands_feats(feats, np.random.default_rng(seed))
    return b["within"]["median"] - b["between"]["p95"], b


def _project_feats(H, feats):
    out = {}
    for t, arr in feats.items():
        Hx = arr @ H.T
        n = np.linalg.norm(Hx, axis=1, keepdims=True)
        n[n == 0.0] = 1.0
        out[t] = Hx / n
    return out


def _build_3thing_episodes(seed: int = 30, per_thing: int = 40):
    genome = skeleton_genome()
    rng = np.random.default_rng(seed)
    episodes = Episodes(cap=per_thing * len(THINGS) + 10, dim_s=112, dim_w=1)
    raw_feats = {t: [] for t in THINGS}
    for t in THINGS:
        for i in range(per_thing):
            rgb, _truth = world.render_canvas(t, rng)
            f0, f1 = _two_glance(genome, rgb, pic_id=f"{t}-{i}")
            raw_feats[t].append(f0)
            episodes.write(moment=len(episodes), x_s=f0, x_w=np.zeros(1), word=t, surprise=0.0, x_s2=f1)
    return genome, episodes, {t: np.stack(v) for t, v in raw_feats.items()}


class TestOrthogonalInit(unittest.TestCase):
    def test_H_rows_orthonormal(self) -> None:
        rng = np.random.default_rng(1)
        H = _orthogonal_rows(6, 20, rng)
        self.assertEqual(H.shape, (6, 20))
        self.assertTrue(np.allclose(H @ H.T, np.eye(6), atol=1e-9))

    def test_dim_out_gt_dim_in_refused(self) -> None:
        rng = np.random.default_rng(1)
        with self.assertRaises(ValueError):
            _orthogonal_rows(10, 4, rng)

    def test_two_constructions_with_different_rng_differ(self) -> None:
        H1 = Traits(dim_in=20, dim_out=6, lr=0.01, rng=np.random.default_rng(1)).H
        H2 = Traits(dim_in=20, dim_out=6, lr=0.01, rng=np.random.default_rng(2)).H
        self.assertFalse(np.allclose(H1, H2))


class TestApplyAndLearnBasics(unittest.TestCase):
    def test_apply_is_raw_projection(self) -> None:
        rng = np.random.default_rng(3)
        t = Traits(dim_in=10, dim_out=4, lr=0.01, rng=rng)
        x = rng.normal(size=10)
        self.assertTrue(np.allclose(t.apply(x), t.H @ x))

    def test_learn_no_episodes_is_a_noop(self) -> None:
        t = Traits(dim_in=10, dim_out=4, lr=0.01, rng=np.random.default_rng(4))
        H0 = t.H.copy()
        r = t.learn(None, steps=20)
        self.assertEqual(r["steps"], 0)
        self.assertTrue(np.array_equal(t.H, H0))
        self.assertEqual(t.version, 0)

    def test_learn_fewer_than_2_episodes_with_s2_is_a_noop(self) -> None:
        t = Traits(dim_in=10, dim_out=4, lr=0.01, rng=np.random.default_rng(5))
        H0 = t.H.copy()
        episodes = Episodes(cap=10, dim_s=10, dim_w=1)
        rng = np.random.default_rng(6)
        x = rng.normal(size=10); x /= np.linalg.norm(x)
        episodes.write(moment=0, x_s=x, x_w=np.zeros(1), word="a", surprise=0.0)  # no x_s2
        r = t.learn(episodes, steps=20)
        self.assertEqual(r["steps"], 0)
        self.assertTrue(np.array_equal(t.H, H0))

    def test_learn_steps_clipped_to_20(self) -> None:
        t = Traits(dim_in=10, dim_out=4, lr=0.01, rng=np.random.default_rng(7))
        rng = np.random.default_rng(8)
        episodes = Episodes(cap=10, dim_s=10, dim_w=1)
        for i in range(4):
            x1 = rng.normal(size=10); x1 /= np.linalg.norm(x1)
            x2 = rng.normal(size=10); x2 /= np.linalg.norm(x2)
            episodes.write(moment=i, x_s=x1, x_w=np.zeros(1), word="a", surprise=0.0, x_s2=x2)
        r = t.learn(episodes, steps=999)
        self.assertEqual(r["steps"], 20)

    def test_loss_decreases_on_a_correlated_toy_batch(self) -> None:
        """A synthetic sanity check independent of the eye tower: B canvases, each with two NOISY
        copies of its own base vector as its positive pair, canvases uncorrelated with each other —
        InfoNCE loss must fall monotonically (within float noise) as H is refined."""
        rng = np.random.default_rng(0)
        dim_in, dim_out, B = 20, 6, 12
        t = Traits(dim_in=dim_in, dim_out=dim_out, lr=0.05, rng=rng)
        base = rng.normal(size=(B, dim_in))
        X1 = base + rng.normal(scale=0.05, size=(B, dim_in))
        X2 = base + rng.normal(scale=0.05, size=(B, dim_in))
        X1 = X1 / np.linalg.norm(X1, axis=1, keepdims=True)
        X2 = X2 / np.linalg.norm(X2, axis=1, keepdims=True)
        losses = [t._infonce_loss(X1, X2)]
        for _ in range(20):
            t._infonce_step(X1, X2)
            losses.append(t._infonce_loss(X1, X2))
        for i in range(len(losses) - 1):
            self.assertLessEqual(losses[i + 1], losses[i] + 1e-9, f"loss rose at step {i}: {losses}")
        self.assertLess(losses[-1], losses[0] * 0.5, f"loss barely moved: {losses}")

    def test_version_bumps_only_when_a_step_actually_ran(self) -> None:
        t = Traits(dim_in=10, dim_out=4, lr=0.01, rng=np.random.default_rng(9))
        self.assertEqual(t.version, 0)
        r = t.learn(None, steps=20)
        self.assertEqual(t.version, 0)
        episodes = Episodes(cap=10, dim_s=10, dim_w=1)
        rng = np.random.default_rng(10)
        for i in range(3):
            x1 = rng.normal(size=10); x1 /= np.linalg.norm(x1)
            x2 = rng.normal(size=10); x2 /= np.linalg.norm(x2)
            episodes.write(moment=i, x_s=x1, x_w=np.zeros(1), word="a", surprise=0.0, x_s2=x2)
        t.learn(episodes, steps=1)
        self.assertEqual(t.version, 1)
        t.learn(episodes, steps=1)
        self.assertEqual(t.version, 2)


# ============================================================================ toy (a)
class TestTraitsMarginToy(unittest.TestCase):
    @unittest.expectedFailure
    def test_bar_margin_after_5_sleeps_ge_raw_prereg_b12a(self) -> None:
        """PREREG's literal bar. Measured: RAW margin 0.0091 (circle/square/triangle, tower front,
        40/thing, within-median 0.9628, between-p95 0.9537). After 5 sleeps (5x Traits.learn(steps=20)
        = 100 gradient steps on the SAME 120-canvas/3-class batch): margin -0.1161 (within-median
        0.1630, between-p95 0.2791) — WORSE than raw. See test_single_sleep_clears_the_bar_by_a_wide_
        margin below for the positive evidence at a milder dose (this is a training-budget/toy-size
        interaction, not a broken mechanism — see the module docstring's fuller trajectory)."""
        genome, episodes, raw_feats = _build_3thing_episodes()
        raw_margin, raw_b = _margin(raw_feats)
        print(f"[B12a] RAW margin {raw_margin:.4f} (within-median {raw_b['within']['median']:.4f}, "
              f"between-p95 {raw_b['between']['p95']:.4f})")
        traits = Traits(dim_in=112, dim_out=32, lr=0.01, rng=np.random.default_rng(31))
        reports = [traits.learn(episodes, steps=20) for _ in range(5)]
        print(f"[B12a] 5 sleeps: {reports}")
        learned_feats = _project_feats(traits.H, raw_feats)
        learned_margin, learned_b = _margin(learned_feats)
        print(f"[B12a] LEARNED margin (5 sleeps) {learned_margin:.4f} (within-median "
              f"{learned_b['within']['median']:.4f}, between-p95 {learned_b['between']['p95']:.4f})")
        self.assertGreaterEqual(learned_margin, raw_margin,
                                 f"learned margin {learned_margin:.4f} < raw margin {raw_margin:.4f}")

    def test_single_sleep_clears_the_bar_by_a_wide_margin(self) -> None:
        """The positive evidence the mechanism is real, not broken: ONE sleep (<=20 steps) on the same
        batch lifts the margin from raw 0.0091 to ~0.069-0.081 across steps 15-20 (measured trajectory
        in the module docstring) — roughly 8-9x the raw front's margin. This test checks the bar the
        PREREG's own toy (a) describes ("the learned head's margin >= the raw front's") at a SINGLE
        sleep, which clears it comfortably; it is the 5-sleep, literal-as-written bar above that
        overshoots into canvas-instance overfitting on this particular 120-canvas toy."""
        genome, episodes, raw_feats = _build_3thing_episodes()
        raw_margin, _b = _margin(raw_feats)
        traits = Traits(dim_in=112, dim_out=32, lr=0.01, rng=np.random.default_rng(31))
        traits.learn(episodes, steps=20)  # ONE sleep
        learned_feats = _project_feats(traits.H, raw_feats)
        learned_margin, learned_b = _margin(learned_feats)
        print(f"[B12a, single sleep] margin {learned_margin:.4f} vs raw {raw_margin:.4f} "
              f"({learned_margin / raw_margin:.1f}x)")
        self.assertGreater(learned_margin, raw_margin)
        self.assertGreater(learned_margin, 3 * raw_margin)

    def test_photographs_caltech_ten_words_margin_before_after(self) -> None:
        """REPORTED, never gated (PREREG's own instruction). Applies the head trained on the 3-thing
        DRAWN toy world above to real photographs — 10 Caltech-style word folders under
        /data/dev/genome/world/<word>/ if present (the master tree; read-only, NEVER written here),
        else this test records their absence and stops. "Before" = raw front margin on the photos;
        "after" = the SAME learned H (from toy (a)'s single-sleep run) projected onto the photos —
        i.e. does a head trained on synthetic line-drawings generalise to real images at all."""
        import glob
        from pathlib import Path
        root = Path("/data/dev/genome/world")
        words = ["anchor", "ant", "barrel", "bass", "beaver", "bonsai", "brain", "buddha", "camera", "cannon"]
        present = [w for w in words if (root / w).is_dir() and glob.glob(str(root / w / "*.jpg"))]
        if len(present) < 3:
            self.skipTest(f"Caltech photographs absent or too few under {root} — found {present}")
        genome = skeleton_genome()
        photo_feats = {}
        for w in present:
            paths = sorted(glob.glob(str(root / w / "*.jpg")))[:20]
            rows = []
            for p in paths:
                rgb = gaze.canvas_of_picture(Path(p), canvas=128)
                gl = gaze.glances(rgb, genome.retina, genome.gaze, "surprise", pic_id=p)
                rows.append(gl["feats"][0])
            photo_feats[w] = np.stack(rows)
        before_margin, before_b = _margin(photo_feats)
        print(f"[B12, photographs] BEFORE (raw front) margin {before_margin:.4f} "
              f"(within-median {before_b['within']['median']:.4f}, between-p95 {before_b['between']['p95']:.4f}) "
              f"over {len(present)} words, {sum(len(v) for v in photo_feats.values())} images")
        _genome2, episodes, _raw = _build_3thing_episodes()
        traits = Traits(dim_in=112, dim_out=32, lr=0.01, rng=np.random.default_rng(31))
        traits.learn(episodes, steps=20)
        learned_photo_feats = _project_feats(traits.H, photo_feats)
        after_margin, after_b = _margin(learned_photo_feats)
        print(f"[B12, photographs] AFTER (toy-world-trained head) margin {after_margin:.4f} "
              f"(within-median {after_b['within']['median']:.4f}, between-p95 {after_b['between']['p95']:.4f})")
        # reported only — no assertion on the relationship between before/after (PREREG: "report, never gate")
        self.assertIsInstance(before_margin, float)
        self.assertIsInstance(after_margin, float)


# ============================================================================ toy (b)
class TestIdentityControl(unittest.TestCase):
    def test_identity_control_dim_out_eq_dim_in_prereg_b12b(self) -> None:
        """dim_out == dim_in == 112, H = I: Area.cos with this head must reproduce the untraited (raw)
        cosine, to float64 precision (an extra divide-by-a-norm-that-is-already-~1.0 can move the last
        bit or two — allclose at 1e-9, not literal `==`, is the honest bar here)."""
        rng = np.random.default_rng(40)
        area = Area("sight", 112, 20)
        for _ in range(5):
            v = rng.normal(size=112); v /= np.linalg.norm(v)
            cid = area.n
            area.cells[cid] = v
            area.alive[cid] = 1
            area.n += 1
        x = rng.normal(size=112); x /= np.linalg.norm(x)
        raw = area.cos(x)
        traits = Traits(dim_in=112, dim_out=112, lr=0.0, rng=np.random.default_rng(41), H=np.eye(112))
        area.traits = traits
        projected = area.cos(x)
        self.assertTrue(np.allclose(raw, projected, atol=1e-9), f"raw={raw} projected={projected}")

    @unittest.expectedFailure
    def test_first_32_rows_literal_prereg_text_cannot_reproduce_raw_cos(self) -> None:
        """The PREREG's own sentence, read literally: "H = I (first 32 rows) reproduces raw cos
        exactly." Measured: it does not, and cannot — dropping 80 of 112 coordinates changes the
        cosine whenever the dropped coordinates carry any of the vectors' structure (which they do
        for a random unit vector: the discrepancy below is ~0.2-0.6 in cosine units, nowhere near
        float precision). RAISED: this clause cannot be met as literally written for dim_out < dim_in
        (module docstring, decision 4)."""
        rng = np.random.default_rng(42)
        area = Area("sight", 112, 20)
        for _ in range(5):
            v = rng.normal(size=112); v /= np.linalg.norm(v)
            cid = area.n
            area.cells[cid] = v
            area.alive[cid] = 1
            area.n += 1
        x = rng.normal(size=112); x /= np.linalg.norm(x)
        raw = area.cos(x)
        H32 = np.eye(112)[:32]
        traits = Traits(dim_in=112, dim_out=32, lr=0.0, rng=np.random.default_rng(43), H=H32)
        area.traits = traits
        projected = area.cos(x)
        print(f"[B12b, literal 32-row identity] raw={raw} projected={projected} "
              f"max|diff|={np.max(np.abs(raw - projected)):.4f}")
        self.assertTrue(np.allclose(raw, projected, atol=1e-9), f"raw={raw} projected={projected}")


# ============================================================================ toy (c)
class TestPinControl(unittest.TestCase):
    def test_untraited_area_cos_is_the_old_two_lines(self) -> None:
        rng = np.random.default_rng(50)
        area = Area("sight", 16, 10)
        for _ in range(4):
            v = rng.normal(size=16); v /= np.linalg.norm(v)
            cid = area.n
            area.cells[cid] = v
            area.alive[cid] = 1
            area.n += 1
        area.alive[1] = 0  # a dead cell must still read -1
        x = rng.normal(size=16); x /= np.linalg.norm(x)
        self.assertIsNone(area.traits)
        expected = area.cells[: area.n] @ x
        expected[area.alive[: area.n] == 0] = -1.0
        got = area.cos(x)
        self.assertTrue(np.array_equal(expected, got))

    def test_organism_never_calling_set_traits_leaves_sight_traits_none(self) -> None:
        from ._toy import mini_genome
        org = Organism(mini_genome())
        self.assertIsNone(org.sight.traits)
        self.assertIsNone(org.words.traits)


class TestOrgTraitsProperty(unittest.TestCase):
    """The coordinator's fixed interface names this `org.traits` (advisor-caught, post-B12): a plain
    instance attribute would shadow Organism.traits's property and silently leave `sight.traits`
    (what Area.cos actually reads) at None — TRAITS would then be a no-op wired through org.traits
    alone. `org.traits = t` and `org.set_traits(t)` must be equivalent, and `org.traits` must read
    back exactly what `Area.cos` uses."""

    def test_assigning_org_traits_reaches_sight_traits(self) -> None:
        from ._toy import mini_genome
        org = Organism(mini_genome())
        t = Traits(dim_in=64, dim_out=8, lr=0.01, rng=np.random.default_rng(1))
        org.traits = t
        self.assertIs(org.sight.traits, t)
        self.assertIs(org.traits, t)
        self.assertIsNone(org.words.traits)

    def test_set_traits_and_property_are_equivalent(self) -> None:
        from ._toy import mini_genome
        org = Organism(mini_genome())
        t = Traits(dim_in=64, dim_out=8, lr=0.01, rng=np.random.default_rng(2))
        org.set_traits(t)
        self.assertIs(org.traits, t)

    def test_org_traits_default_is_none(self) -> None:
        from ._toy import mini_genome
        org = Organism(mini_genome())
        self.assertIsNone(org.traits)


class TestTraitsBreaksTheta(unittest.TestCase):
    """Advisor-flagged, coordinator note #4 in the WAVE 2 report: none of the three required toys run
    `moment()`/`recall()` through the traited path — they measure the MARGIN (a difference of cosines),
    never the LEVEL against the live THETA_N/THETA_M thresholds, which gate G-a calibrated on RAW
    cosines. This test does the 5-minute measurement an advisor review asked for: after real training
    moments and ONE sleep's worth of `learn()`, does `recall()` on a held-out feature still resonate?"""

    def test_recall_goes_novel_after_one_sleep_on_this_front(self) -> None:
        genome = skeleton_genome()
        org = Organism(genome)
        rng = np.random.default_rng(21)
        episodes = Episodes(cap=200, dim_s=112, dim_w=1)
        for i in range(50):
            t = THINGS[i % 3]
            rgb, _truth = world.render_canvas(t, rng)
            f0, f1 = _two_glance(genome, rgb, pic_id=f"{t}-{i}")
            xw = world.encode_word(t, genome.ear_blank_zero)
            org.moment(f0, xw)
            episodes.write(moment=i, x_s=f0, x_w=np.zeros(1), word=t, surprise=0.0, x_s2=f1)
        self.assertGreater(len(org.sight.alive_ids()), 0, "the 50-moment warm-up must have birthed cells")

        rgb, _truth = world.render_canvas(THINGS[0], rng)
        f0, _f1 = _two_glance(genome, rgb, pic_id="held")
        r_raw = org.recall("sight", f0)
        print(f"[B12, THETA interaction] RAW recall: reason={r_raw['reason']} cos={r_raw.get('cos')} "
              f"(THETA_N={genome.theta_n})")
        self.assertNotEqual(r_raw["reason"], "novel", "the raw front should already resonate here")

        traits = Traits(dim_in=112, dim_out=32, lr=0.01, rng=np.random.default_rng(31))
        org.traits = traits
        r_init = org.recall("sight", f0)
        print(f"[B12, THETA interaction] at init (random orthogonal H) recall: "
              f"reason={r_init['reason']} cos={r_init.get('cos')}")

        report = traits.learn(episodes, steps=20)  # ONE sleep
        r_after = org.recall("sight", f0)
        print(f"[B12, THETA interaction] after ONE learn() {report}: "
              f"recall reason={r_after['reason']} cos={r_after.get('cos')}")

        # THE FINDING: one sleep's InfoNCE step drags the projected cosine below THETA_N, so recall()
        # reads "novel" where the raw front resonated cleanly — reported, not fixed here (outside this
        # builder's interface; it is gate G-a's or TRAITS's own calibration question, see the WAVE 2
        # report's coordinator note #4).
        self.assertEqual(r_after["reason"], "novel")
        self.assertLess(r_after["cos"], genome.theta_n)


if __name__ == "__main__":
    unittest.main()
