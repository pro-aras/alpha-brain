# edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — W3-3 (docs/G4-WAVE3-CLAUSES.md; the one-line
# wiring of genome/curiosity.py's own contract, B10 note 3): `Mind._maybe_sleep` now calls
# `Interests.sleep_boundary()` once per SLEEP boundary crossed. `Interests.update()` itself is not called
# anywhere by the mind today (THINK's outcome vocabulary and CURIOSITY's {"answered","parked","filed",
# "scored"} vocabulary are not yet the same thing — a separate, later wiring, not this clause's job), so
# this toy plants "answered" items directly on `mind.interests` — exactly what the clause names ("plant
# one answered item before a sleep and one after") — around a REAL sleep boundary crossed by a real tape
# through `Mind.consume`, never a synthetic `_maybe_sleep` call.
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
BASE_SLEEP_GENOME = ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome"
SLEEP_CURIOSITY_GENOME = ROOT / "tests" / "creature" / "G4-wave3-sleep-boundary-test.genome"


def _write_sleep_curiosity_genome() -> None:
    """SLEEP+FAST (already on G4-wave2-sleep-test.genome, Builder A's own wave-2 fixture) plus CURIOSITY
    (needed so `mind.interests` exists) -- a NEW fixture file under tests/creature/, never an edit to the
    base one, same technique test_wave2_think.py's `_write_park_genome()` uses."""
    base = BASE_SLEEP_GENOME.read_text()
    extra = "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
    SLEEP_CURIOSITY_GENOME.write_text(base.rstrip("\n") + "\n" + extra)


_write_sleep_curiosity_genome()


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, n: int = 90, seed: int = 4242) -> None:
    """Enough worded canvases to cross the genome's SLEEP boundary (every 40 moments = 10 canvases at 4
    fixations each) at least once -- the same shape test_wave2_sleep_and_blinds.py's own tape uses."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if i % 7 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


class TestGenomeFixture(unittest.TestCase):
    def test_fixture_declares_sleep_fast_curiosity(self) -> None:
        g = parse_genome(SLEEP_CURIOSITY_GENOME.read_text())
        self.assertIn("SLEEP", g.declared)
        self.assertIn("FAST", g.declared)
        self.assertIn("CURIOSITY", g.declared)


class TestSleepBoundaryWired(unittest.TestCase):
    """The positive: with the wiring (today's mind.py, unmodified), a boundary genuinely crosses and the
    window is cut there -- an "answered" plant made before the boundary never recombines with one made
    after it."""

    def _run(self, root: Path):
        mind = Mind(SLEEP_CURIOSITY_GENOME, root)
        self.assertIsNotNone(mind.interests, "CURIOSITY must be declared for this toy to mean anything")

        before_key = ("word", "planted_before")
        mind.interests.update({"kind": "word", "key": "planted_before"}, "answered")
        self.assertEqual(mind.interests._window_answered, [before_key], "the plant must actually open the window")

        crossed = False
        for row in read_tape(root):
            mind.consume(row)
            if mind._last_sleep_at > 0 and not crossed:
                crossed = True
                # the exact assertion the clause names: the window is EMPTY right after the boundary --
                # nothing carries across it for a later "answered" plant to pair with.
                self.assertEqual(mind.interests._window_answered, [],
                                  "sleep_boundary() must have closed the window at the first boundary crossed")
        self.assertTrue(crossed, "the tape must be long enough to cross at least one SLEEP boundary")

        mind.interests.update({"kind": "word", "key": "planted_after"}, "answered")
        return mind

    def test_window_empty_right_after_the_boundary_and_no_recombine(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root)
        mind = self._run(root)
        w = mind.interests.weights
        self.assertNotEqual(
            w[("word", "planted_before")], w[("word", "planted_after")],
            "wired: an answer from before the sleep must never recombine (mean) with one from after it",
        )
        self.assertEqual(mind.interests._window_answered, [("word", "planted_after")],
                          "the post-sleep window holds only the post-sleep plant")


class TestSleepBoundaryUnwiredControl(unittest.TestCase):
    """The negative control the clause asks for: monkeypatch sleep_boundary() to a no-op -- the SAME tape,
    the SAME plants, but now the window survives the boundary uncut, and recombine DOES fire (both ends
    up with the mean weight). If this control did not diverge from the wired test above, the wired test
    would be proving nothing (SOLUTIONS #91: a 0-finding audit needs a negative control that can fail)."""

    def test_without_the_wiring_the_plants_recombine(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root)
        mind = Mind(SLEEP_CURIOSITY_GENOME, root)
        mind.interests.sleep_boundary = lambda: None   # the no-op: the exact thing W3-3 adds, removed

        mind.interests.update({"kind": "word", "key": "planted_before"}, "answered")
        crossed = False
        for row in read_tape(root):
            mind.consume(row)
            if mind._last_sleep_at > 0 and not crossed:
                crossed = True
                # unwired: the window is NOT cut -- the pre-sleep plant is still sitting there
                self.assertEqual(mind.interests._window_answered, [("word", "planted_before")],
                                  "unwired control: the window must survive the boundary uncut")
        self.assertTrue(crossed, "the tape must be long enough to cross at least one SLEEP boundary")

        mind.interests.update({"kind": "word", "key": "planted_after"}, "answered")
        w = mind.interests.weights
        self.assertEqual(
            w[("word", "planted_before")], w[("word", "planted_after")],
            "unwired control: an answer from before the sleep DOES recombine with one from after it",
        )


if __name__ == "__main__":
    unittest.main()
