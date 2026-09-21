# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:23 +0400 -- docs/briefs/G5-J-BIND-COLOUR-RETINA.md:
# BIND (G-EYE-2, "one canvas = one moment") and SENSE colour (G-EYE-3/§3.6) mechanics, pinned. The BabyAI
# band reproduction and the full life-2/life-3a replays live in the report (scratch/, not committed --
# they read real closed-life data and Researcher G's harvested frames, neither of which belongs in a fast
# unit test); this file pins the MECHANISM: the parser grammar, sight_dim, colour's grey no-op, and BIND's
# call-count/unit-norm behaviour through a real (small) Mind + tape, the same technique
# tests/creature/test_sleep_boundary.py uses.
# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 22:40 +0400 -- the orchestrator's two follow-ups: mode
# "one"/"random" + colour (TestModeOneColour, above the BIND-pool tests) and the colour-feature-road sweep
# (TestColourFeatureRoadsParity, TestColourExamRoads, TestAskDoorColour, below) -- every gaze.glances() caller
# that feeds recall/ask needed `colour=genome.colour` forwarded, or a colour-declared genome (every G5.genome
# life) crashes the exam/ask doors on a 112-vs-144 shape mismatch in Area.cos.
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind, _bind_pool
from creature.tape import Tape, read_tape
from genome import gaze, world
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
BASE_GAZE_GENOME = ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome"   # real GAZE + sealed tower, no SLEEP/FAST needed here
BIND_GENOME = ROOT / "tests" / "creature" / "G5-bind-test.genome"


def _write_bind_genome() -> None:
    base = BASE_GAZE_GENOME.read_text()
    BIND_GENOME.write_text(base.rstrip("\n") + "\nBIND     glances per canvas\n")


_write_bind_genome()


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, n: int = 8, seed: int = 909) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


# ------------------------------------------------------------------------------------------ the grammar
class TestGrammar(unittest.TestCase):
    def test_bind_line_declares(self) -> None:
        g = parse_genome(BASE_GAZE_GENOME.read_text() + "\nBIND     glances per canvas\n")
        self.assertEqual(g.declared["BIND"], {"pool": "glances per canvas"})

    def test_bind_bad_line_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(BASE_GAZE_GENOME.read_text() + "\nBIND     fixations per canvas\n")

    def test_colour_line_declares_and_sight_dim_grows_by_32(self) -> None:
        g0 = parse_genome(BASE_GAZE_GENOME.read_text())
        g1 = parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance fixed-gain\n")
        self.assertIsNone(g0.colour)
        self.assertEqual(g1.colour, {"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"})
        self.assertEqual(g1.sight_dim(), g0.sight_dim() + 32)

    def test_colour_block_unit_refused(self) -> None:
        """Only 'fixed-gain' is accepted -- 'block-unit' (the OTHER form Researcher G measured, and
        rejected: #231(1), a legitimately-zero block's noise amplified to norm 1) is not new vocabulary
        the machinery knows, by design."""
        with self.assertRaises(GenomeError):
            parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance block-unit\n")

    def test_undeclared_genomes_unaffected(self) -> None:
        """The G4-wave2 fixture itself (no BIND, no colour) must be untouched by this file's own edits --
        the parity control every additive gene needs (#231's family)."""
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        self.assertNotIn("BIND", g.declared)
        self.assertIsNone(g.colour)


# ------------------------------------------------------------------------------------------ colour's grey no-op
class TestColourGreyNoOp(unittest.TestCase):
    def test_maker_world_colour_channels_are_exactly_zero(self) -> None:
        rng = np.random.default_rng(11)
        maxabs = 0.0
        for thing in world.THINGS_11:
            rgb, _truth = world.render_canvas(thing, rng)
            an = gaze._analyse_frame(rgb)
            maxabs = max(maxabs, float(np.max(np.abs(an["channels"]["rg"]))), float(np.max(np.abs(an["channels"]["by"]))))
        self.assertEqual(maxabs, 0.0, "the maker's world is one grey plane x3 -- rg/by must be exact zero, not merely small")

    def test_colour_on_is_byte_identical_to_colour_off_on_grey(self) -> None:
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        rng = np.random.default_rng(12)
        rgb, _truth = world.render_canvas("circle", rng)
        no_colour = gaze.glances(rgb, g.retina, g.gaze, "surprise", pic_id="x")
        colour = gaze.glances(rgb, g.retina, g.gaze, "surprise", pic_id="x",
                              colour={"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"})
        self.assertEqual(len(no_colour["feats"][0]), 112)
        self.assertEqual(len(colour["feats"][0]), 144)
        for a, b in zip(no_colour["feats"], colour["feats"]):
            self.assertTrue(np.array_equal(a, b[:112]), "the tower's own 112 numbers must be untouched by an inert (all-zero) colour block")
            self.assertTrue(np.all(b[112:] == 0.0))


# ------------------------------------------------------------------------------------------ mode "one" + colour
# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 22:12 +0400 -- the orchestrator's follow-up: mode "one"
# used to refuse (GenomeError) when colour was declared; verdict_g4.py's T-one-glance twin builds every G5
# life's genome (which declares SENSE colour on every life) with mode "one" forced, so that twin refused on
# every 8h verdict. Fixed in genome/gaze.py (colour_block_whole(), the mode=="one" branch of glances());
# these tests pin the fix.
COLOUR_GENE = {"channels": ("rg", "by"), "cells": (4, 4), "gain": "fixed"}


def _coloured_canvas(canvas: int = 128) -> np.ndarray:
    """A synthetic RGB canvas with real colour variation -- world.render_canvas() is grey-only by design
    (TestColourGreyNoOp above), so a mode-'one' non-zero-colour-block test needs its own fixture."""
    rgb = np.full((canvas, canvas, 3), 128, dtype=np.uint8)
    rgb[20:60, 20:60] = (220, 40, 40)     # a red patch
    rgb[80:120, 80:120] = (40, 40, 220)   # a blue patch
    return rgb


class TestModeOneColour(unittest.TestCase):
    def test_undeclared_colour_matches_independent_computation(self) -> None:
        """(b) parity: colour=None in mode 'one' is byte-identical to before this fix -- recomputed here
        independently of glances() (resize -> ink rule -> retina, the same three steps glances() always ran
        for mode 'one'), not merely re-reading glances()'s own code back at itself."""
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        rng = np.random.default_rng(21)
        rgb, _truth = world.render_canvas("square", rng)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="one")
        self.assertEqual(len(out["feats"]), 1)
        self.assertEqual(out["feats"][0].shape, (112,))
        self.assertEqual(out["fix"], [])
        self.assertEqual(out["windows"], [])
        ink_rule = gaze.INK_RULES[str(g.gaze.get("ink", "contrast"))]
        small = np.asarray(Image.fromarray(rgb).convert("L").resize((g.gaze["glance"], g.gaze["glance"]), Image.BOX), dtype=np.float64) / 255.0
        expect = gaze.retina(ink_rule(small), tuple(g.retina))
        self.assertTrue(np.array_equal(out["feats"][0], expect))

    def test_colour_block_exactly_zero_on_grey_nonzero_on_coloured(self) -> None:
        """(a): mode 'one' + colour returns one 144-vector; its colour tail is exactly 0.0 on a grey
        (maker's-world) canvas and non-zero on a genuinely coloured one."""
        g1 = parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance fixed-gain\n")
        rng = np.random.default_rng(31)
        grey_rgb, _truth = world.render_canvas("triangle", rng)
        no_colour = gaze.glances(grey_rgb, g1.retina, g1.gaze, mode="one")
        out_grey = gaze.glances(grey_rgb, g1.retina, g1.gaze, mode="one", colour=COLOUR_GENE)
        self.assertEqual(out_grey["feats"][0].shape, (144,))
        self.assertTrue(np.array_equal(no_colour["feats"][0], out_grey["feats"][0][:112]),
                         "grey canvas: the outer unit-step over (unit tower, true-zero block) must be a true no-op")
        self.assertTrue(np.all(out_grey["feats"][0][112:] == 0.0))

        coloured_rgb = _coloured_canvas()
        out_colour = gaze.glances(coloured_rgb, g1.retina, g1.gaze, mode="one", colour=COLOUR_GENE)
        self.assertEqual(out_colour["feats"][0].shape, (144,))
        self.assertGreater(float(np.max(np.abs(out_colour["feats"][0][112:]))), 0.0,
                            "a genuinely coloured canvas must produce a non-zero colour tail")
        self.assertAlmostEqual(float(np.linalg.norm(out_colour["feats"][0])), 1.0, places=10)

    def test_colour_block_whole_matches_direct_pooling(self) -> None:
        """Pins colour_block_whole()'s own arithmetic: mean-pool the retina's 16x16 rg/by grids into 4x4
        blocks (4 cells per block per side, 16/4=4), /255 -- independent of the function under test."""
        rgb = _coloured_canvas()
        an = gaze._analyse_frame(rgb)
        got = gaze.colour_block_whole(an)
        self.assertEqual(got.shape, (32,))
        expect = []
        for key in ("rg", "by"):
            m = np.asarray(an["channels"][key], dtype=np.float64)
            self.assertEqual(m.shape, (16, 16))
            pooled = m.reshape(4, 4, 4, 4).mean(axis=(1, 3))
            expect.append(pooled.reshape(-1) / 255.0)
        expect = np.concatenate(expect)
        self.assertTrue(np.allclose(got, expect))

    def test_mode_random_with_colour_works(self) -> None:
        """Confirms the reader's blind-gaze (T-random-gaze) twin: mode 'random' already shared the
        per-glance-window colour path (only mode 'one' needed a code change) -- pinned here so a future
        change to that shared path is caught for BOTH modes."""
        g1 = parse_genome(BASE_GAZE_GENOME.read_text() + "\nSENSE    colour rg by 4x4 under the glance fixed-gain\n")
        rng = np.random.default_rng(41)
        rgb, _truth = world.render_canvas("diamond", rng)
        out = gaze.glances(rgb, g1.retina, g1.gaze, mode="random", pic_id="rand1", colour=COLOUR_GENE)
        self.assertEqual(len(out["feats"]), g1.gaze["fixations"])
        for v in out["feats"]:
            self.assertEqual(v.shape, (144,))
            self.assertAlmostEqual(float(np.linalg.norm(v)), 1.0, places=10)


# ------------------------------------------------------------------------------------------ _bind_pool as a pure function
class TestBindPoolPure(unittest.TestCase):
    def test_empty_is_a_noop(self) -> None:
        self.assertEqual(_bind_pool([]), [])

    def test_pools_to_one_unit_vector(self) -> None:
        rng = np.random.default_rng(3)
        vs = []
        for _ in range(4):
            v = rng.normal(size=16)
            vs.append(v / np.linalg.norm(v))
        pooled = _bind_pool(vs)
        self.assertEqual(len(pooled), 1)
        expect = np.mean(vs, axis=0)
        expect = expect / np.linalg.norm(expect)
        self.assertTrue(np.allclose(pooled[0], expect))
        self.assertAlmostEqual(float(np.linalg.norm(pooled[0])), 1.0, places=12)

    def test_four_identical_glances_pool_to_the_same_unit_vector(self) -> None:
        rng = np.random.default_rng(4)
        v = rng.normal(size=16); v = v / np.linalg.norm(v)
        pooled = _bind_pool([v, v, v, v])
        self.assertTrue(np.allclose(pooled[0], v))


# ------------------------------------------------------------------------------------------ BIND wired through a real Mind
class TestBindWiredMomentCount(unittest.TestCase):
    """The mechanism the report's cadence table (§3) depends on: org.t advances once per canvas under
    BIND, GAZE.fixations times per canvas without it -- checked on a REAL Mind + tape (creature/mind.py's
    _consume_eye), never a synthetic call to Organism.moment()."""

    def test_unbound_advances_t_by_fixations_per_canvas(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=6)
        mind = Mind(BASE_GAZE_GENOME, root)
        n_eye = 0
        for row in read_tape(root):
            mind.consume(row)
            if row["sense"] == "eye":
                n_eye += 1
        self.assertEqual(mind.org.t, n_eye * mind.genome.gaze["fixations"])

    def test_bind_advances_t_by_one_per_canvas(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=6)
        mind = Mind(BIND_GENOME, root)
        n_eye = 0
        for row in read_tape(root):
            mind.consume(row)
            if row["sense"] == "eye":
                n_eye += 1
        self.assertEqual(mind.org.t, n_eye, "BIND: one org.moment()/moment_sight() call per canvas")

    def test_bind_births_no_more_than_unbound_on_the_same_tape(self) -> None:
        """Not the report's headline number (that needs life 2's real tape, §1/§2 of the report) but the
        same DIRECTION, pinned on a small deterministic fixture: pooling four looks into one before any
        birth/resonance decision can only reduce or equal the number of independent birth opportunities."""
        root_u = Path(tempfile.mkdtemp()); _build_tape(root_u, n=8, seed=77)
        root_b = Path(tempfile.mkdtemp()); _build_tape(root_b, n=8, seed=77)
        mind_u = Mind(BASE_GAZE_GENOME, root_u)
        mind_b = Mind(BIND_GENOME, root_b)
        for row in read_tape(root_u):
            mind_u.consume(row)
        for row in read_tape(root_b):
            mind_b.consume(row)
        self.assertLessEqual(len(mind_b.org.births), len(mind_u.org.births))


# ------------------------------------------------------------------------------------------ every glance-feature
# road that feeds recall/ask -- the orchestrator's second follow-up. glance_held()/glance_rows()/
# first_glance_feats() (genome/run_g1.py) and glance_picture() (genome/ask.py) all call gaze.glances()
# themselves and MUST forward the parsed Genome's own .colour (never a literal, never omitted) or a
# colour-declared genome (every G5.genome life) produces 112-dim vectors against a 144-dim organism and
# Organism.cos()/Area.cos raises a shape-mismatch ValueError -- not a GenomeError, not a clean refusal, a
# crash -- the first time recall/ask is asked anything. questions.py's ask_glances/ask_plant_glances/ask
# never call gaze.glances themselves (they consume already-built feats), so they needed no change; covered
# here by proxy (TestColourExamRoads runs the real tools/self_exam.py road, which calls ask_glances on
# feats built by the now-fixed glance_held()).
COLOUR_TEST_GENOME = ROOT / "tests" / "creature" / "G5-colour-test.genome"


def _write_colour_genome() -> Path:
    base = BASE_GAZE_GENOME.read_text()
    COLOUR_TEST_GENOME.write_text(base.rstrip("\n") + "\nSENSE    colour rg by 4x4 under the glance fixed-gain\n")
    return COLOUR_TEST_GENOME


_write_colour_genome()


def _build_small_life(genome_path: Path, root: Path, n: int = 10, seed: int = 505) -> Mind:
    _build_tape(root, n=n, seed=seed)
    mind = Mind(genome_path, root)
    for row in read_tape(root):
        mind.consume(row)
    mind.close()   # writes state/organism.npz + .json + ledger.json -- unconditional, per Mind.close()'s own body
    return mind


class TestColourFeatureRoadsParity(unittest.TestCase):
    """(b) the parity pin: with colour UNDECLARED, run_g1.glance_held()'s forwarded `colour=genome.colour`
    (which is then None) must be a true no-op -- identical, canvas for canvas, to the OLD call shape
    (gaze.glances() with no colour argument at all, exactly what this function called before this fix)."""

    def test_glance_held_colour_none_matches_pre_fix_direct_call(self) -> None:
        from genome import run_g1
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        self.assertIsNone(g.colour)
        rng = np.random.default_rng(51)
        held = {"circle": [world.render_canvas("circle", rng) for _ in range(3)]}
        got = run_g1.glance_held(held, g, "surprise")
        for t, rows in held.items():
            for i, (rgb, _truth) in enumerate(rows):
                pid = run_g1._pid(rgb)
                expect = gaze.glances(rgb, g.retina, g.gaze, "surprise", pid)["feats"]   # the pre-fix call: no colour kwarg at all
                got_feats = got[t][i][1]
                self.assertEqual(len(got_feats), len(expect))
                for a, b in zip(got_feats, expect):
                    self.assertTrue(np.array_equal(a, b))

    def test_glance_rows_colour_none_matches_pre_fix_direct_call(self) -> None:
        from genome import run_g1
        g = parse_genome(BASE_GAZE_GENOME.read_text())
        rng = np.random.default_rng(52)
        rgb, truth = world.render_canvas("square", rng)
        got = run_g1.glance_rows([("square", rgb, truth)], g, "surprise")
        pid = run_g1._pid(rgb)
        expect = gaze.glances(rgb, g.retina, g.gaze, "surprise", pid)["feats"]
        self.assertEqual(len(got[0][1]), len(expect))
        for a, b in zip(got[0][1], expect):
            self.assertTrue(np.array_equal(a, b))


class TestColourExamRoads(unittest.TestCase):
    """(a): tools/self_exam.py -- the live exam duty's own instrument -- must run to completion on a root
    whose genome declares SENSE colour, not crash on the first held-out question."""

    def test_self_exam_runs_to_completion_on_colour_genome(self) -> None:
        genome_path = _write_colour_genome()
        root = Path(tempfile.mkdtemp())
        _build_small_life(genome_path, root, n=10, seed=707)
        from tools import self_exam
        old_argv = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome_path), "--held", "2", "--check-tape", "50"]
            rc = self_exam.main()
        finally:
            sys.argv = old_argv
        self.assertEqual(rc, 0)
        exam_files = sorted((root / "exam").glob("*.json"))
        self.assertEqual(len(exam_files), 1, "self_exam.py must have written exactly one exam file, not crashed before writing it")
        out = json.loads(exam_files[0].read_text())
        self.assertTrue(out["organism_hash_unchanged_by_exam"], "a read-only exam must never change the organism it read")
        self.assertIn("Q1", out.get("ask_all_words", {}), "the exam must have actually scored Q1, not stopped early")


class TestAskDoorColour(unittest.TestCase):
    """genome/ask.py's `python3 -m genome.ask what-is <picture>` door: a live consumer of gaze.glances(),
    separate from the exam/verdict roads. Against a saved run whose genome declares colour, recall_many()
    must return a well-formed answer (or an honest abstain) -- never a ValueError from a shape mismatch."""

    def test_ask_what_is_on_colour_genome_no_crash(self) -> None:
        genome_path = _write_colour_genome()
        root = Path(tempfile.mkdtemp())
        _build_small_life(genome_path, root, n=8, seed=808)
        # genome/ask.py's load() wants run/organism.npz + run/organism.json + run/ledger.json + a *.genome
        # file, all in the SAME directory -- exactly Mind.snapshot()'s own state/ layout (its own docstring:
        # "the shape genome/ask.py's load() reads"), plus one genome file dropped in (Mind doesn't write one).
        state_dir = root / "state"
        (state_dir / "colour.genome").write_text(genome_path.read_text())
        from genome import ask as gask
        g, org, Ls, Lw = gask.load(state_dir)
        self.assertIsNotNone(g.colour)
        pic_path = root / "ask_pic.png"
        Image.fromarray(_coloured_canvas(canvas=int(g.gaze["canvas"])), mode="RGB").save(pic_path)
        feats = gask.glance_picture(pic_path, g)
        self.assertEqual(len(feats), int(g.gaze["fixations"]))
        for v in feats:
            self.assertEqual(v.shape, (144,))
        r = org.recall_many("sight", feats)   # must not raise -- the shape-mismatch ValueError this fix prevents
        self.assertIn("reason" if r["cell"] is None else "cell", r)


if __name__ == "__main__":
    unittest.main()
