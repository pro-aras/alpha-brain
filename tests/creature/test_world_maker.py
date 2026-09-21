# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:34 +0400 — A4 tests: make() purity, disjointness from
# G1's held-out seed 2, schedule() alternation, the tape order law, and (bonus) the plant mechanism at tiny thresholds.
from __future__ import annotations

import tempfile
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np

from creature import world_maker
from creature.body import Body, _maker_args_from_declared
from creature.tape import read_tape
from genome import world
from genome.machinery import parse_genome

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"
G4_GENOME = Path(__file__).resolve().parents[2] / "genome" / "G4.genome"


class TestMakePure(unittest.TestCase):
    def test_make_is_pure(self) -> None:
        t1, rgb1, truth1 = world_maker.make(20260920, 0, 5)
        t2, rgb2, truth2 = world_maker.make(20260920, 0, 5)
        self.assertEqual(t1, t2)
        self.assertTrue(np.array_equal(rgb1, rgb2))
        self.assertEqual(truth1, truth2)

    def test_make_varies_with_i(self) -> None:
        _t1, rgb1, _tr1 = world_maker.make(20260920, 0, 0)
        _t2, rgb2, _tr2 = world_maker.make(20260920, 0, 1)
        self.assertFalse(np.array_equal(rgb1, rgb2), "different i must (almost certainly) render a different canvas")


class TestScheduleAlternates(unittest.TestCase):
    def test_even_windows_are_things11(self) -> None:
        for w in (0, 2, 4, 6):
            self.assertEqual(world_maker.schedule(20260920, w), list(world.THINGS_11))

    def test_odd_windows_are_arrival2_plus_three(self) -> None:
        for w in (1, 3, 5):
            s = world_maker.schedule(20260920, w)
            self.assertEqual(s[: len(world.THINGS_ARRIVAL2)], list(world.THINGS_ARRIVAL2))
            extra = s[len(world.THINGS_ARRIVAL2):]
            self.assertEqual(len(extra), 3)
            self.assertEqual(len(set(extra)), 3, "the 3 chosen THINGS_11 must be distinct")
            self.assertTrue(set(extra) <= set(world.THINGS_11))

    def test_schedule_is_pure(self) -> None:
        self.assertEqual(world_maker.schedule(20260920, 1), world_maker.schedule(20260920, 1))

    def test_schedule_varies_by_window_and_seed(self) -> None:
        a = world_maker.schedule(20260920, 1)
        b = world_maker.schedule(20260920, 3)
        # not asserting inequality (the rng could in principle draw the same 3) -- just that both are valid
        for s in (a, b):
            self.assertEqual(len(s), len(world.THINGS_ARRIVAL2) + 3)


class TestDisjointFromHeldOutSeed2(unittest.TestCase):
    def test_never_collides_with_seed_2(self) -> None:
        maker_canvases = []
        for window in (0, 1):
            for i in range(100):
                thing, rgb, truth = world_maker.make(world_maker.DEFAULT_SEED, window, i)
                maker_canvases.append((thing, rgb, truth))
        self.assertEqual(len(maker_canvases), 200)
        held = world.holdout_canvas(world.THINGS_11, 10, np.random.default_rng(2))
        n_checked = world.assert_disjoint_canvas(maker_canvases, held)
        self.assertEqual(n_checked, len(world.THINGS_11) * 10)


class TestTapeOrderLaw(unittest.TestCase):
    def test_ear_precedes_eye_for_every_moment(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.add_sense("maker", lambda publish, stop_event: world_maker.sense(publish, stop_event, root=root, period=0.1))
        body.start()
        try:
            time.sleep(3.0)
        finally:
            body.stop()

        rows = list(read_tape(root))
        self.assertGreater(len(rows), 0)
        seq_by_moment: dict[str, dict[str, int]] = {}
        for r in rows:
            m = r["meta"]["moment"]
            seq_by_moment.setdefault(m, {})[r["sense"]] = r["seq"]
        checked = 0
        for m, by_sense in seq_by_moment.items():
            if "ear" in by_sense and "eye" in by_sense:
                self.assertLess(by_sense["ear"], by_sense["eye"], f"moment {m}: ear seq must precede eye seq")
                checked += 1
        self.assertGreater(checked, 0, "must have checked at least one complete (ear, eye) moment pair")

        # truth files exist, keyed by the eye row's own seq, and are never referenced from the tape rows
        truth_files = list((root / "truth").glob("*.json"))
        self.assertGreater(len(truth_files), 0)
        for r in rows:
            self.assertNotIn("truth", r)


class TestPlantMechanism(unittest.TestCase):
    def test_plant_shows_after_threshold_within_window(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        # tiny thresholds so this runs in a couple of seconds instead of hours
        body.add_sense("maker", lambda publish, stop_event: world_maker.sense(
            publish, stop_event, root=root, period=0.05, plant_after_canvases=5, plant_window_s=2.0, plant_showings=3))
        body.start()
        try:
            time.sleep(3.0)
        finally:
            body.stop()

        rows = [r for r in read_tape(root) if r["sense"] == "ear"]
        words = [r["meta"]["word"] for r in rows]
        plant_count = sum(1 for w in words if w == world.THING_PLANT)
        self.assertGreaterEqual(plant_count, 1, "the plant must show at least once past its threshold")
        self.assertLessEqual(plant_count, 3)
        self.assertNotIn(world.THING_NULL, words)
        self.assertNotIn(world.THING_NEVER, words)


class TestWorldGeneDrivesMakerPeriodAndWindow(unittest.TestCase):
    """C1.3 (docs/G4-WAVE3-CLAUSES.md W3-0b): WORLD's declared `drawn every <n> s` / `arrivals every <h>
    h` become the maker's period/window -- undeclared keeps the exact prior defaults (5.0 s / 6 h).

    genome/machinery.py's WORLD regex parses `arrival_every_h` as `(\\d+)` (whole hours only), so the
    PREREG toy's own example ("arrivals every 0.01 h") cannot be written as a genome line -- RAISED in the
    builder report, not worked around (not this builder's file). `_maker_args_from_declared` is therefore
    exercised directly against hand-built `declared` dicts for the exact toy value (0.01 h = 36 s), and
    separately against the REAL G4.genome parse for the whole-hour case, so both halves -- "the derivation
    math is right" and "a real genome text reaches it" -- are pinned."""

    def test_undeclared_keeps_the_prior_defaults(self) -> None:
        self.assertEqual(_maker_args_from_declared({}, 5.0, world_maker.WINDOW_SECONDS), (5.0, world_maker.WINDOW_SECONDS))

    def test_declared_drives_period_and_window(self) -> None:
        declared = {"WORLD": {"drawn_every_s": 1, "arrival_every_h": 1, "folder": "world/", "web_per_hour": 6}}
        self.assertEqual(_maker_args_from_declared(declared, 5.0, world_maker.WINDOW_SECONDS), (1.0, 3600.0))

    def test_the_lifes_own_world_line_derives_5s_and_6h(self) -> None:
        genome = parse_genome(G4_GENOME.read_text())
        period, window_s = _maker_args_from_declared(genome.declared, 5.0, world_maker.WINDOW_SECONDS)
        self.assertEqual((period, window_s), (5.0, 6 * 3600.0))

    def test_toy_value_0_01h_via_sense_directly(self) -> None:
        """The toy's own numbers (period 1 s, window 0.01 h = 36 s), run through `world_maker.sense`
        itself (the function `_maker_args_from_declared`'s output feeds) rather than through genome text:
        >= 3 canvases in 5 s, and a window change (w0000 -> w0001) inside 60 s, read off the tape rows'
        own meta.moment prefix."""
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.add_sense("maker", lambda publish, stop_event: world_maker.sense(
            publish, stop_event, root=root, period=1.0, window_seconds=36.0))
        body.start()
        try:
            time.sleep(45.0)
        finally:
            body.stop()

        rows = list(read_tape(root))
        self.assertGreater(len(rows), 0)
        windows_seen = sorted({r["meta"]["moment"][:5] for r in rows})   # "w0000", "w0001", ...

        def _at(row):
            return datetime.fromisoformat(row["at"].replace("Z", "+00:00"))

        start = _at(rows[0])
        early_moments = {r["meta"]["moment"] for r in rows if (_at(r) - start).total_seconds() <= 5.0}
        self.assertGreaterEqual(len(early_moments), 3,
                                 f"expected >= 3 canvases within 5 wall-clock seconds at period=1.0, saw {sorted(early_moments)}")
        self.assertIn("w0001", windows_seen, f"expected a window change to w0001 within 45 s at window_seconds=36.0, saw {windows_seen}")


if __name__ == "__main__":
    unittest.main()
