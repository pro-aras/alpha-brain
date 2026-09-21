# edit: Claude (Fable 5.1), 2026-09-21 20:54 +0400 — the 8 h seam lives (docs/G5-SEAM-LIFE-PLAN.md §1): the maker's plant fires
# after PLANT_AFTER_CANVASES = 15000 (hour ~21) and would NEVER show in an 8 h life (SOLUTIONS #228 (a): a plant
# placed where the mechanism cannot fire). `--plant-after N` on the body's CLI reaches world_maker.sense's
# plant_after_canvases; these tests pin (1) the argv reader, (2) that the value reaches the maker partial (the
# last link, #180), (3) the mechanism at tiny thresholds: exactly 5 showings with the knob, 0 without it (the
# old default is the negative control — the refusing half of the test).
from __future__ import annotations

import functools
import tempfile
import time
import unittest
from pathlib import Path

from creature import world_maker
from creature.body import Body, _maker_sense_fn, _plant_after_from_argv
from creature.tape import read_tape
from genome import world
from genome.machinery import parse_genome

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"


class TestPlantAfterArgv(unittest.TestCase):
    def test_default_when_absent(self) -> None:
        self.assertEqual(_plant_after_from_argv([], 15000), 15000)
        self.assertEqual(_plant_after_from_argv(["--root", "x", "--genome", "y"], 15000), 15000)

    def test_reads_the_value(self) -> None:
        self.assertEqual(_plant_after_from_argv(["--root", "x", "--plant-after", "5000"], 15000), 5000)

    def test_malformed_raises(self) -> None:
        with self.assertRaises((ValueError, IndexError)):
            _plant_after_from_argv(["--plant-after"], 15000)
        with self.assertRaises(ValueError):
            _plant_after_from_argv(["--plant-after", "soon"], 15000)


class TestKnobReachesTheMakerPartial(unittest.TestCase):
    """#180: the value must reach the LAST link — the keywords of the partial the body runs as the maker sense."""
    def setUp(self) -> None:
        self.declared = parse_genome(GENOME_PATH.read_text()).declared
        self.root = Path(tempfile.mkdtemp())

    def test_default_is_the_module_constant(self) -> None:
        fn = _maker_sense_fn(["--root", str(self.root)], self.declared, self.root)
        self.assertIs(fn.func, world_maker.sense)
        self.assertEqual(fn.keywords["plant_after_canvases"], world_maker.PLANT_AFTER_CANVASES)
        self.assertEqual(fn.keywords["plant_after_canvases"], 15000)

    def test_flag_reaches_the_partial(self) -> None:
        fn = _maker_sense_fn(["--root", str(self.root), "--plant-after", "5000"], self.declared, self.root)
        self.assertEqual(fn.keywords["plant_after_canvases"], 5000)
        # the other two derivations are untouched by the new knob
        self.assertEqual(fn.keywords["period"], 5.0)
        self.assertEqual(fn.keywords["window_seconds"], world_maker.WINDOW_SECONDS)


class TestPlantMechanismWithTheKnob(unittest.TestCase):
    """Tiny thresholds: with --plant-after 5 the plant shows EXACTLY plant_showings times inside its window;
    with the old default (15000) it shows 0 times in the same run — the refusing half."""
    def _run(self, argv, seconds: float = 4.0) -> list:
        root = Path(tempfile.mkdtemp())
        declared = parse_genome(GENOME_PATH.read_text()).declared
        body = Body(root, GENOME_PATH)
        fn = _maker_sense_fn(argv + ["--maker-period", "0.05"], declared, root)
        fn = functools.partial(fn, plant_window_s=2.0, plant_showings=5)   # a partial of the partial: only the test's tiny window
        body.add_sense("maker", fn)
        body.start()
        try:
            time.sleep(seconds)
        finally:
            body.stop()
        return [r["meta"]["word"] for r in read_tape(root) if r["sense"] == "ear"]

    def test_exactly_five_showings_with_the_knob(self) -> None:
        words = self._run(["--plant-after", "5"])
        self.assertGreater(len(words), 5)
        self.assertEqual(sum(1 for w in words if w == world.THING_PLANT), 5)
        self.assertNotIn(world.THING_NULL, words)
        self.assertNotIn(world.THING_NEVER, words)

    def test_zero_showings_without_the_knob(self) -> None:
        words = self._run([])
        self.assertGreater(len(words), 5)
        self.assertEqual(sum(1 for w in words if w == world.THING_PLANT), 0)


if __name__ == "__main__":
    unittest.main()
