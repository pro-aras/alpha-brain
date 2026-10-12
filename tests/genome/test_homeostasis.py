# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-13 — PREREG-HOMEOSTASIS AMENDMENT 2
# (SIGNED; SEAT-LINE-H0-A2.txt): the ζ=1.0 reset pin, the F1 reachability pin (432 < 439 < the count),
# the eye clause's +2, the invert control, the heard-word renewing pool, the heard-ledger round-trip.
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §2.2 + AMENDMENT 1
# (the law SIGNED 2026-10-12): the drives module's unit tests — the update rules, the thresholds, the
# neutrality when undeclared (byte-identical's invariants), the deterministic draw, the planted controls
# (the module's own plants: a surprise ramp must move arousal, a sustained calm must move boredom, fatigue
# must saw across a planted boundary).
"""tests/genome/test_homeostasis.py — the Homeostasis module's own unit tests (the wiring's byte-identity
lives in tests/creature/test_homeostasis_wiring.py)."""
from __future__ import annotations

import unittest

from genome.homeostasis import (EPS_F, FATIGUE_FORCE, REST_A, SEEK_CEILING, SEEK_REFRACTORY, TH_BABBLE,
                                TH_EXCLAIM, TH_SILENT, Homeostasis)

FULL = {"arousal": True, "boredom": True, "fatigue": True}


class UndeclaredIsInert(unittest.TestCase):
    def test_neutral_values_hold(self) -> None:
        h = Homeostasis({}, seed=1)
        for e in (0.9, 0.1, 0.0, 1.0, 0.4):
            h.note_canvas(e)
        self.assertEqual((h.a, h.b, h.f), (REST_A, 0.0, 0.0), "undeclared variables never move")
        self.assertEqual(h.gains(), (1.0, 1.0))
        self.assertEqual(h.extra_fixations(), 0)
        self.assertFalse(h.extra_event(5, "ask"))
        self.assertFalse(h.suppressed())
        self.assertFalse(h.exclaim())
        self.assertFalse(h.force_sleep(10**9, 2500))
        h.b = 1.0  # even with a planted ceiling value, an undeclared boredom never seeks
        self.assertFalse(h.seek_due())

    def test_row_rounds(self) -> None:
        h = Homeostasis(FULL, seed=1)
        h.note_canvas(0.77777)
        row = h.row()
        self.assertEqual(set(row), {"a", "b", "f"})
        for v in row.values():
            self.assertEqual(v, round(v, 4))


class Dynamics(unittest.TestCase):
    def test_arousal_tracks_surprise(self) -> None:
        h = Homeostasis({"arousal": True}, seed=1)
        for _ in range(400):
            h.note_canvas(0.9)
        self.assertGreater(h.a, 0.8, "the planted high-surprise stretch must raise arousal")
        for _ in range(2000):
            h.note_canvas(0.0)
        self.assertLess(h.a, 0.35, "a sustained calm must settle arousal toward the resting point")

    def test_boredom_needs_SUSTAINED_low_surprise(self) -> None:
        h = Homeostasis({"boredom": True}, seed=1)
        for _ in range(600):
            h.note_canvas(0.8)          # the slow mean settles: s̄ ≈ 0.8·(1−0.99^600) ≈ 0.797
        b_before = h.b
        h.note_canvas(0.75)             # ONE mild dip (above κ·s̄ ≈ 0.638) must NOT fire boredom (§8 attack 3)
        self.assertAlmostEqual(h.b, b_before * 0.9, places=6)
        self.assertEqual(h.b, 0.0)
        for _ in range(30):
            h.note_canvas(0.0)          # the SUSTAINED calm (well below κ·s̄): boredom climbs
        self.assertGreater(h.b, b_before)

    def test_fatigue_saws_across_sleep(self) -> None:
        h = Homeostasis({"fatigue": True}, seed=1)
        for _ in range(100):
            h.note_canvas(0.5)
        self.assertAlmostEqual(h.f, 100 * EPS_F, places=6)
        h.note_sleep()
        self.assertEqual(h.f, 0.0, "AMENDMENT 2 F1: ζ = 1.0 — sleep fully clears fatigue (the adenosine analog)")

    def test_fatigue_reaches_the_ceiling_inside_a_real_boundary_gap(self) -> None:
        """AMENDMENT 2 F1 (2026-10-13): ε = 0.0022 walked against the bench tape's MEASURED
        canvases-per-boundary (min 423 / p50 439 / max 483) — the ceiling lands at ⌈0.95/ε⌉ = 432
        canvases, inside the longer half of gaps (H-SLEEP-TRIGGER's population exists), while the
        genome's count still rules the shortest windows (a backstop, never a replacement)."""
        h = Homeostasis({"fatigue": True}, seed=1)
        for _ in range(423):                       # the shortest measured gap
            h.note_canvas(0.5)
        self.assertLess(h.f, FATIGUE_FORCE, "the count still rules the shortest measured window")
        for _ in range(432 - 423):
            h.note_canvas(0.5)
        self.assertGreaterEqual(h.f, FATIGUE_FORCE, "the ceiling lands at 432 canvases — inside the median gap (439)")

    def test_force_sleep_floor(self) -> None:
        h = Homeostasis({"fatigue": True}, seed=1)
        h.f = FATIGUE_FORCE
        self.assertFalse(h.force_sleep(since=1000, every=2500), "the floor: never sooner than half the count")
        self.assertTrue(h.force_sleep(since=1250, every=2500))

    def test_suppression_threshold(self) -> None:
        h = Homeostasis({"fatigue": True}, seed=1)
        h.f = TH_SILENT + 0.01
        self.assertTrue(h.suppressed())


class Effectors(unittest.TestCase):
    def test_gains_bounds_and_rest(self) -> None:
        h = Homeostasis(FULL, seed=1)
        self.assertEqual(h.gains(), (1.0, 1.0))      # at rest the gains are neutral
        h.a = 1.0
        self.assertEqual(h.gains()[0], 2.0)          # the declared clip
        h.f = 1.0
        self.assertEqual(h.gains()[1], 0.5)

    def test_extra_fixations_threshold(self) -> None:
        h = Homeostasis({"arousal": True}, seed=1)
        self.assertEqual(h.extra_fixations(), 0)
        h.a = TH_EXCLAIM + 0.01
        self.assertEqual(h.extra_fixations(), 2, "AMENDMENT 2 F2: +2 — the 1.3× bar's ceiling at 4 fixed fixations is 1.25× at +1, 1.5× at +2")

    def test_draw_is_deterministic_and_varied(self) -> None:
        h = Homeostasis(FULL, seed=20261211)
        self.assertEqual(h.draw(7, "ask"), h.draw(7, "ask"))
        self.assertNotEqual(h.draw(7, "ask"), h.draw(7, "babble"))
        vals = {h.draw(s, "ask") for s in range(200)}
        self.assertGreater(len(vals), 180, "the draw varies with the seq")
        self.assertTrue(all(0.0 <= v < 1.0 for v in vals))

    def test_extras_are_zero_below_threshold(self) -> None:
        h = Homeostasis(FULL, seed=1)
        h.b = TH_BABBLE - 0.01
        self.assertFalse(any(h.extra_event(s, "ask") for s in range(500)),
                         "below θ_babble not one extra fires (A2: extras, never gates)")
        h.b = 1.0
        fired = sum(h.extra_event(s, "ask") for s in range(500))
        self.assertGreater(fired, 100, "at the ceiling the extras fire at the declared rate")

    def test_exclaim_once_per_surprise(self) -> None:
        h = Homeostasis({"arousal": True}, seed=1)
        for _ in range(100):
            h.note_canvas(0.1)
        h.a = 0.8
        h.note_canvas(0.9)              # a planted surprise ≥ 2·s̄
        self.assertTrue(h.exclaim())
        h.note_exclaim()
        self.assertFalse(h.exclaim(), "one exclaim per surprise, never a repeat of the repeat")

    def test_seek_lifecycle(self) -> None:
        h = Homeostasis({"boredom": True}, seed=1)
        h.b = SEEK_CEILING
        self.assertTrue(h.seek_due())
        h.note_seek("video")
        self.assertEqual(h.seek_active(), "video")
        self.assertFalse(h.seek_due(), "the refractory window holds")
        h.canvases += SEEK_REFRACTORY
        self.assertTrue(h.seek_due())
        h.canvases += 1001
        self.assertIsNone(h.seek_active(), "the seek window closed")


class AmendmentTwo(unittest.TestCase):
    """PREREG-HOMEOSTASIS AMENDMENT 2 (SIGNED 2026-10-13) — the pre-run walk's new forms, each pinned."""

    def test_inverted_arousal_is_the_declared_negative_control(self) -> None:
        """F6: H-NULL — surprise drives arousal DOWN; the bench-only knob's default is untouched."""
        h = Homeostasis({"arousal": True}, seed=1, invert=True)
        for _ in range(400):
            h.note_canvas(0.9)
        self.assertLess(h.a, REST_A - 0.1, "inverted: a sustained surprise stretch pushes arousal DOWN")
        for _ in range(2000):
            h.note_canvas(0.9)
        self.assertEqual(h.a, 0.0, "inverted: sustained surprise parks arousal at the floor")
        h2 = Homeostasis({"arousal": True}, seed=1, invert=True)
        for _ in range(300):
            h2.note_canvas(0.0)
        self.assertGreater(h2.a, REST_A, "inverted: a sustained calm lets arousal climb past rest")
        h3 = Homeostasis({"arousal": True}, seed=1)   # the default form is untouched
        for _ in range(400):
            h3.note_canvas(0.9)
        self.assertGreater(h3.a, 0.8, "the law's own arousal still tracks surprise UP")
        self.assertFalse(h3.invert)

    def test_heard_word_ledger_and_the_renewing_pool(self) -> None:
        """F3: heard words feed the extras; the 1,000-canvas re-ask refractory renews; the seek
        target's source goes first (A1's attention turn)."""
        h = Homeostasis({"boredom": True}, seed=1)
        h.note_canvas(0.5, source="scene", word="star")     # canvas 0
        h.note_canvas(0.5, source="video", word="cloud")    # canvas 1 — the most recent
        self.assertEqual(h.extra_ask_word(), "cloud")
        h.note_bored_ask("cloud")
        self.assertEqual(h.extra_ask_word(), "star", "the refractory holds cloud for 1,000 canvases")
        h.canvases += 999
        self.assertEqual(h.extra_ask_word(), "star", "the refractory still holds at 999")
        h.canvases += 1
        self.assertEqual(h.extra_ask_word(), "cloud", "the refractory expired at 1,000 — the renewing form")
        h2 = Homeostasis({"boredom": True}, seed=1)
        h2.note_canvas(0.5, source="scene", word="star")
        h2.canvases += 5
        h2.note_canvas(0.5, source="video", word="cloud")
        h2.b = SEEK_CEILING
        h2.note_seek("scene")
        self.assertEqual(h2.extra_ask_word(), "star", "the seek target's words first even when older")
        self.assertIsNone(Homeostasis({"boredom": True}, seed=1).extra_ask_word(), "no heard words → no pick (never invent content)")

    def test_state_round_trip_carries_the_heard_ledger(self) -> None:
        h = Homeostasis(FULL, seed=7)
        for w in ("star", "cloud"):
            h.note_canvas(0.4, source="scene", word=w)
        h.note_bored_ask("star")
        h.note_sleep()
        h2 = Homeostasis(FULL, seed=7)
        h2.load_json(h.to_json())
        self.assertEqual(h2.to_json(), h.to_json(), "the drives restore exactly — the heard ledger rides (F3)")

    def test_a_life_without_the_line_never_builds_the_ledger(self) -> None:
        """Byte-identity's invariant: undeclared, the object itself is never built by the Mind (the
        wiring suite pins that); here: an undeclared module's effectors stay inert WITH ledgers fed."""
        h = Homeostasis({}, seed=1)
        h.note_canvas(0.9, source="scene", word="star")
        self.assertEqual(h.gains(), (1.0, 1.0))
        self.assertFalse(h.extra_event(5, "extra-ask"))
        self.assertFalse(h.extra_event(5, "babble"))
        self.assertEqual(h.extra_fixations(), 0)


if __name__ == "__main__":
    unittest.main()
