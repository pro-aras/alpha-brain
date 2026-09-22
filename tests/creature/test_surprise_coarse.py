# tests/creature/test_surprise_coarse.py — L-4 (SURPRISE: the mind's prediction reaches the eye) and L-7
# (the coarse whole-canvas glance), docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4, docs/organs/EYE.md §4
# G-EYE-5/G-EYE-6. edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x-19:3x +0400.
#
# Honest account (docs/briefs/LIFE-B-REPORT.md §2 has the full version): the parser/mechanism shape was
# fixed by the brief + an advisor review BEFORE most of these were written (the brief's own "all confirmed
# on a repeat" prose does not survive the single-x-hat definition it also specifies — caught by advisor(),
# not by a failing assertion, so the toys below measure and print the REAL numbers rather than assert a
# wrong one). Two test classes reproduce a GENUINE RED: TestRunG1ChainCoarse — an IndexError crash in
# genome/run_g1.py's live(), found by grepping every gaze.glances()/glance_rows() caller (SOLUTIONS #235)
# — fixed, then GREEN; and TestSurpriseParses::test_old_form_refuses_at_mind_start — a second advisor-caught
# gap (the bare "SURPRISE floor <f>" form silently stopped refusing once RUNS["mind"]["SURPRISE"] named a
# real call site), verified RED by temporarily disabling the fix and re-running the test alone before
# restoring it — fixed, then GREEN. Every other class here was run and iterated to green on the FINAL code.
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional, Tuple
from unittest import mock

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import gaze, run_g1, world
from genome.machinery import GenomeError, Organism, parse_genome

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "tests" / "creature" / "G5-surprise-coarse-test.genome"
GENOME_TEXT = GENOME_PATH.read_text()

# The same text with L-7's clause removed (byte-for-byte the base G5-colour-test.genome's GAZE line) —
# used for "undeclared is byte-identical" / "a genome without coarse replays identical" controls.
NO_COARSE_TEXT = GENOME_TEXT.replace(
    "GAZE   surprise fixations 4 grid 16 canvas 128 glance 32 ink border coarse 32   # DIFF 1: L-7's trailing \" coarse 32\" clause added",
    "GAZE   surprise fixations 4 grid 16 canvas 128 glance 32 ink border",
)
assert NO_COARSE_TEXT != GENOME_TEXT, "the GAZE line replace target moved — update it"

# The same text with L-4's line removed entirely.
NO_SURPRISE_TEXT = "\n".join(
    line for line in GENOME_TEXT.splitlines()
    if not line.startswith("SURPRISE floor")
)
assert "SURPRISE" not in parse_genome(NO_SURPRISE_TEXT).declared


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _write_genome(tmp_dir: Path, text: str, name: str = "g.genome") -> Path:
    p = tmp_dir / name
    p.write_text(text)
    return p


def _build_repeated_tape(root: Path, word: str, n: int, seed: int = 42) -> np.ndarray:
    """`n` canvases, ALL the exact same render of `word` (deterministic — no jitter across showings),
    so any residual/confirm difference between the first and a later showing is attributable to the
    mind's own learning, never to a changed picture."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    rgb, _truth = world.render_canvas(word, rng)
    for i in range(n):
        m_id = f"m{i:05d}"
        tape.publish("ear", word.encode("utf-8"), {"moment": m_id, "source": "test", "word": word}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": m_id, "source": "test"}, "png")
    return rgb


def _mind_rows(root: Path) -> List[dict]:
    rows: List[dict] = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return [r for r in rows if "event" not in r]


class TestGazeParsesCoarse(unittest.TestCase):
    def test_coarse_absent_is_byte_identical(self) -> None:
        g = parse_genome(NO_COARSE_TEXT)
        self.assertNotIn("coarse", g.gaze)

    def test_coarse_declared(self) -> None:
        g = parse_genome(GENOME_TEXT)
        self.assertEqual(g.gaze["coarse"], 32)

    def test_placeholder_or_extra_word_refused_by_name(self) -> None:
        for bad in ("GAZE surprise fixations 4 grid 16 canvas 128 glance 32 ink border coarse",
                    "GAZE surprise fixations 4 grid 16 canvas 128 glance 32 ink border coarse 32 now",
                    "GAZE surprise fixations 4 grid 16 canvas 128 glance 32 ink border COARSE 32"):
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as cm:
                    parse_genome("SEED 1\n" + bad + "\n")
                self.assertIn("GAZE", str(cm.exception))


class TestSurpriseParses(unittest.TestCase):
    def test_undeclared_absent(self) -> None:
        g = parse_genome(NO_SURPRISE_TEXT)
        self.assertNotIn("SURPRISE", g.declared)

    def test_old_form_still_byte_identical(self) -> None:
        # every genome on disk before this brief (G5.genome's own "#OFF SURPRISE floor 0.05") — the
        # trailing clause is OPTIONAL, so the old shape must still parse to exactly {"floor": f}. Built on
        # a REAL, complete genome (theta_n etc. required to start at all) with only the trailing clause
        # dropped from the fixture's own SURPRISE line.
        old_form_text = GENOME_TEXT.replace("SURPRISE floor 0.05 predicted mind-cell", "SURPRISE floor 0.05")
        g = parse_genome(old_form_text)
        self.assertEqual(g.declared["SURPRISE"], {"floor": 0.05})

    def test_old_form_refuses_at_mind_start(self) -> None:
        # advisor-caught gap: once RUNS["mind"]["SURPRISE"] names a real call site (creature/genes.py),
        # genes_module.unwired() no longer flags a BARE "SURPRISE floor <f>" (no "predicted mind-cell")
        # as declared-but-unwired — it would pass W3-0's own check and silently run THIS brief's
        # mechanism, even though G5.genome's own comment gives the bare form a DIFFERENT, never-built
        # meaning ("a sense publishes when |actual - predicted| > floor"). Mind.__init__ must refuse the
        # bare form by name, exactly as it refused before RUNS ever named SURPRISE.
        old_form_text = GENOME_TEXT.replace("SURPRISE floor 0.05 predicted mind-cell", "SURPRISE floor 0.05")
        self.assertEqual(parse_genome(old_form_text).declared["SURPRISE"], {"floor": 0.05})  # still parses
        tmp = Path(tempfile.mkdtemp())
        gp = _write_genome(tmp, old_form_text)
        with self.assertRaises(GenomeError) as cm:
            Mind(gp, tmp / "run")
        self.assertIn("SURPRISE", str(cm.exception))

    def test_new_form_declared(self) -> None:
        g = parse_genome(GENOME_TEXT)
        self.assertEqual(g.declared["SURPRISE"], {"floor": 0.05, "predicted": "mind-cell"})

    def test_wrong_predicted_word_refused_by_name(self) -> None:
        with self.assertRaises(GenomeError) as cm:
            parse_genome("SEED 1\nSURPRISE floor 0.05 predicted last-canvas\n")
        self.assertIn("SURPRISE", str(cm.exception))


class TestOneGlanceVectorSharedHelper(unittest.TestCase):
    """L-7's own claim, to the byte: the coarse feature IS glances(..., mode='one') at the same size —
    one derivation, never two (SOLUTIONS #172's family)."""

    def test_coarse_feature_equals_mode_one_at_the_same_size(self) -> None:
        g = parse_genome(GENOME_TEXT)
        rng = np.random.default_rng(7)
        rgb, _truth = world.render_canvas("square", rng)
        one = gaze.glances(rgb, g.retina, g.gaze, mode="one", colour=g.colour)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour)
        self.assertEqual(len(out["feats"]), 5, "4 located glances + 1 coarse")
        self.assertEqual(len(out["fix"]), 4)
        self.assertEqual(len(out["windows"]), 4)
        self.assertTrue(np.array_equal(out["feats"][-1], one["feats"][0]), "coarse feature must equal mode='one' to the byte")

    def test_negative_control_coarse_differs_from_a_located_glance(self) -> None:
        # The size argument IS read, not assumed (test above): but on THIS genome's front (RETINA's
        # `tower:eye-tower-g2` step asserts its input is exactly 32x32, machinery.py:496) coarse's own
        # size is constrained to equal the tower's fixed input side — every G-EYE-6 genome line on disk
        # declares "coarse 32" beside "glance 32" for exactly this reason, so a coarse-size mismatch
        # cannot be exercised on this front (raised, not built: a front without a fixed-input tower step,
        # e.g. RETINA's pool<k>/hog<n> steps, could take any size — none of this estate's genomes use one).
        # The negative control this front CAN run: the coarse (whole-canvas) feature must differ from a
        # LOCATED glance's feature — proving the crop is real, not a no-op that happens to match "one".
        g = parse_genome(GENOME_TEXT)
        rng = np.random.default_rng(7)
        rgb, _truth = world.render_canvas("square", rng)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour)
        self.assertFalse(np.array_equal(out["feats"][0], out["feats"][-1]),
                          "the coarse (whole-canvas) feature must not equal glance 0's (cropped-window) feature")

    def test_coarse_absent_no_fifth_feature(self) -> None:
        g = parse_genome(NO_COARSE_TEXT)
        rng = np.random.default_rng(7)
        rgb, _truth = world.render_canvas("square", rng)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour)
        self.assertEqual(len(out["feats"]), 4)
        self.assertEqual(len(out["residual"]), 4)

    def test_predicted_none_residual_all_none(self) -> None:
        g = parse_genome(GENOME_TEXT)
        rng = np.random.default_rng(7)
        rgb, _truth = world.render_canvas("square", rng)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour, predicted=None)
        self.assertEqual(out["residual"], [None] * 5)

    def test_predicted_matches_first_feature_residual_near_zero(self) -> None:
        g = parse_genome(GENOME_TEXT)
        rng = np.random.default_rng(7)
        rgb, _truth = world.render_canvas("square", rng)
        out = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour)
        predicted = out["feats"][0].copy()
        out2 = gaze.glances(rgb, g.retina, g.gaze, mode="surprise", pic_id="x", colour=g.colour, predicted=predicted)
        self.assertAlmostEqual(out2["residual"][0], 0.0, places=6)


class TestBindRefusal(unittest.TestCase):
    """W3-0's own law, applied at Mind.__init__: BIND pools a canvas's feats into one vector before
    Organism.moment() sees them — SURPRISE's per-glance confirm and the coarse glance's residual are
    both index-aligned with the UNPOOLED feats, which BIND breaks by construction. Neither combination
    has a mechanism; both refuse by name rather than falling back silently."""

    def test_bind_plus_surprise_refuses(self) -> None:
        text = GENOME_TEXT.replace("#OFF EAR-SOUND", "BIND     glances per canvas\n#OFF EAR-SOUND")
        tmp = Path(tempfile.mkdtemp())
        gp = _write_genome(tmp, text)
        with self.assertRaises(GenomeError) as cm:
            Mind(gp, tmp / "run")
        self.assertIn("BIND", str(cm.exception)); self.assertIn("SURPRISE", str(cm.exception))

    def test_bind_plus_coarse_refuses(self) -> None:
        text = NO_SURPRISE_TEXT.replace("#OFF EAR-SOUND", "BIND     glances per canvas\n#OFF EAR-SOUND")
        self.assertIn("coarse 32", text)
        tmp = Path(tempfile.mkdtemp())
        gp = _write_genome(tmp, text)
        with self.assertRaises(GenomeError) as cm:
            Mind(gp, tmp / "run")
        self.assertIn("BIND", str(cm.exception)); self.assertIn("coarse", str(cm.exception))

    def test_bind_alone_still_starts(self) -> None:
        # the refusal must be SPECIFIC to BIND+SURPRISE / BIND+coarse — BIND alone (neither gene present)
        # must still start, exactly as it does today (LIFE.genome declares BIND #OFF for its own reason).
        text = NO_SURPRISE_TEXT.replace("coarse 32", "").replace("#OFF EAR-SOUND", "BIND     glances per canvas\n#OFF EAR-SOUND")
        self.assertNotIn("coarse", parse_genome(text).gaze)
        tmp = Path(tempfile.mkdtemp())
        gp = _write_genome(tmp, text)
        Mind(gp, tmp / "run")   # must not raise


class TestConfirmedMoment(unittest.TestCase):
    """L-4's own toy (the brief's words): a canvas shown twice; a corrupted block; a shuffled-expectation
    twin. Built HONESTLY on the SINGLE-x-hat definition the brief specifies (one expectation vector per
    canvas — the word's best sight cell), not on the brief's own optimistic prose ("all confirmed") —
    the advisor's review caught that a single x_hat cannot make every one of 4 distinct-location glances
    confirm at once (at most the glances near that ONE cell's location can); the actual measured numbers
    are what this test (and the report) assert and print."""

    def test_repeated_canvas_some_glances_confirm_at_steady_state(self) -> None:
        root = Path(tempfile.mkdtemp())
        rgb = _build_repeated_tape(root, "circle", n=50, seed=42)
        m = Mind(GENOME_PATH, root)
        for r in read_tape(root):
            m.consume(r)
        rows = _mind_rows(root)
        located = [r for r in rows if r.get("act") != "coarse" and "residual" in r]
        last = located[-1]
        print(f"[L-4 toy] repeated-canvas steady-state residual={last['residual']} confirmed={last['confirmed']}")
        # honest bound, not the brief's "all confirmed": at least one glance confirms (the predicted
        # cell's own location), and not every glance does (three other locations on the shape).
        self.assertGreaterEqual(sum(last["confirmed"]), 1)
        self.assertLess(sum(last["confirmed"]), 4)
        self.assertGreater(m.glances_confirmed, 0)
        self.assertGreater(m.glances_surprised, 0)

    def test_corrupted_block_raises_that_fixations_residual(self) -> None:
        """A canvas shown many times, THEN one showing with a 16x16 block corrupted ON the thing (the
        truth file's own top/left — test_replay.py's own pattern, SOLUTIONS #212's family: corrupt the
        content, never the tape)."""
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        rng = np.random.default_rng(11)
        rgb, truth = world.render_canvas("square", rng)
        N = 40
        for i in range(N):
            tape.publish("ear", b"square", {"moment": f"m{i:05d}", "source": "test", "word": "square"}, "txt")
            tape.publish("eye", _png_bytes(rgb), {"moment": f"m{i:05d}", "source": "test"}, "png")
        ty, tx = truth["top"], truth["left"]
        corrupted = rgb.copy()
        corrupted[ty:ty + 16, tx:tx + 16, :] = 255 - corrupted[ty:ty + 16, tx:tx + 16, :]
        tape.publish("ear", b"square", {"moment": "mC", "source": "test", "word": "square"}, "txt")
        tape.publish("eye", _png_bytes(corrupted), {"moment": "mC", "source": "test"}, "png")

        m = Mind(GENOME_PATH, root)
        for r in read_tape(root):
            m.consume(r)
        rows = _mind_rows(root)
        located = [r for r in rows if r.get("act") != "coarse" and "residual" in r]
        before, corrupt_row = located[-2], located[-1]
        fix = corrupt_row["fix"]
        hit = [i for i, (y, x) in enumerate(fix) if _cell_overlaps_block(y, x, ty, tx)]
        print(f"[L-4 toy] corrupted-block: fix={fix} truth-cell~({ty},{tx}) hit-glances={hit} "
              f"before={before['residual']}/{before['confirmed']} after={corrupt_row['residual']}/{corrupt_row['confirmed']}")
        if hit:
            for i in hit:
                self.assertFalse(corrupt_row["confirmed"][i], f"a fixation over the corrupted block (glance {i}) must not confirm")
        else:
            self.skipTest("no fixation of this run's 4 landed on the corrupted block (saliency-dependent) — see printed fix/truth above")

    def test_shuffled_expectation_confirms_near_chance(self) -> None:
        """The negative control: x_hat = a RANDOM alive sight cell (never the word's real best edge) —
        confirmation must NOT track the real mechanism's rate; measured and printed, not asserted to an
        exact number (a random seed's exact rate is not a law)."""
        root = Path(tempfile.mkdtemp())
        rgb = _build_repeated_tape(root, "triangle", n=50, seed=5)
        m = Mind(GENOME_PATH, root)
        rows_all = list(read_tape(root))
        for r in rows_all:
            m.consume(r)
        real_rate = m.glances_confirmed / max(1, m.glances_confirmed + m.glances_surprised)

        # replay the SAME tape with expected_sight patched to return a random alive cell (never the real edge)
        rng = np.random.default_rng(99)

        def _random_expected(self, xw):
            if self.sight.n == 0:
                return None
            alive = np.flatnonzero(self.sight.alive)
            if alive.size == 0:
                return None
            return self.sight.cells[int(rng.choice(alive))].copy()

        root2 = Path(tempfile.mkdtemp())
        rgb2 = _build_repeated_tape(root2, "triangle", n=50, seed=5)
        self.assertTrue(np.array_equal(rgb, rgb2), "the two tapes must carry the identical canvas")
        with mock.patch.object(Organism, "expected_sight", _random_expected):
            m2 = Mind(GENOME_PATH, root2)
            for r in read_tape(root2):
                m2.consume(r)
        shuffled_rate = m2.glances_confirmed / max(1, m2.glances_confirmed + m2.glances_surprised)
        print(f"[L-4 toy] confirmed rate: real={real_rate:.3f} shuffled-expectation={shuffled_rate:.3f}")
        self.assertLess(shuffled_rate, real_rate, "a random expectation must confirm less often than the real word-cell edge")


class TestBlindCoarse(unittest.TestCase):
    """The reader's own required test (the brief's words): "the blind twin's journal equals a no-coarse
    genome's replay of the same tape" — the control genome is the fixture's TEXT with only " coarse 32"
    removed (SCALE/every other number untouched), never a different genome (a confound the advisor named)."""

    def test_blind_coarse_journal_equals_no_coarse_genome_replay(self) -> None:
        # n=50 (not a smaller n): STAGE 2's "meet moments 200.." gate (org.t >= 200) means HEBB never
        # fires below it and residual/confirmed stay None on every row of BOTH sides regardless of
        # --blind coarse -- an equality that would hold trivially. n=50 x 4 glances = 200 moments,
        # crossing the gate, so this exercises real residual/confirmed parity on a wired organism.
        content_seed = 3
        root_a = Path(tempfile.mkdtemp())   # coarse-declaring genome, blind to coarse
        rgb_a = _build_repeated_tape(root_a, "diamond", n=50, seed=content_seed)
        m_a = Mind(GENOME_PATH, root_a, blind=frozenset({"coarse"}))
        for r in read_tape(root_a):
            m_a.consume(r)

        root_b = Path(tempfile.mkdtemp())   # the coarse-less genome, unblinded
        rgb_b = _build_repeated_tape(root_b, "diamond", n=50, seed=content_seed)
        self.assertTrue(np.array_equal(rgb_a, rgb_b))
        no_coarse_path = _write_genome(root_b, NO_COARSE_TEXT, "no_coarse.genome")
        m_b = Mind(no_coarse_path, root_b)
        for r in read_tape(root_b):
            m_b.consume(r)

        rows_a = _mind_rows(root_a)
        rows_b = _mind_rows(root_b)
        self.assertEqual(len(rows_a), len(rows_b), "no coarse row should have been written under --blind coarse")
        for ra, rb in zip(rows_a, rows_b):
            self.assertEqual(ra, rb)
        self.assertFalse(any(r.get("act") == "coarse" for r in rows_a))
        self.assertEqual(m_a.org.state_hash(), m_b.org.state_hash())


class TestBlindSurprise(unittest.TestCase):
    """"--blind surprise" (floor -1: nothing confirmed) — a twin that STILL computes and journals
    residual (unlike blind-coarse, which drops the row entirely), so the CONFIRM mechanism's own effect
    can be isolated by comparing this twin against the live mind."""

    def test_blind_surprise_never_confirms_but_still_journals_residual(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "cross", n=50, seed=17)
        m = Mind(GENOME_PATH, root, blind=frozenset({"surprise"}))
        for r in read_tape(root):
            m.consume(r)
        rows = _mind_rows(root)
        located = [r for r in rows if r.get("act") != "coarse" and "residual" in r]
        self.assertTrue(located)
        self.assertTrue(any(v is not None for row in located for v in row["residual"]),
                         "residual must still be COMPUTED under --blind surprise, never dropped")
        self.assertTrue(all(v is False for row in located for v in row["confirmed"]),
                         "--blind surprise must never confirm (floor -1 is below every possible residual)")
        self.assertEqual(m.glances_confirmed, 0)
        self.assertEqual(m.org.births_skipped_confirmed, 0)


class TestThinkPoolSkipsConfirmedEpisode(unittest.TestCase):
    """L-4's "no think-pool item": an episode whose glance 0 was CONFIRMED is excluded from
    _think_pool()'s word/sight loops (the FAST write, SLEEP's most_surprising() and the "ep" field are
    all untouched — additive, narrower than skipping the FAST write itself, which was raised in the
    report as the alternative)."""

    def test_confirmed_episode_excluded_from_word_pool(self) -> None:
        text = GENOME_TEXT + "\nTHINK    every 1 canvases\nPARK     after 3 identical dead-ends reopen on new-sense\n"
        tmp = Path(tempfile.mkdtemp())
        gp = _write_genome(tmp, text)
        root = tmp / "run"
        rgb = _build_repeated_tape(root, "star", n=50, seed=23)
        m = Mind(gp, root)
        for r in read_tape(root):
            m.consume(r)
        self.assertGreater(len(m._confirmed_episodes), 0, "the repeated-canvas tape must have produced at least one confirmed episode")
        pool = m._think_pool()
        pool_episodes = {item["episode"] for item in pool if item["kind"] in ("word", "sight") and item["episode"] is not None}
        self.assertTrue(pool_episodes.isdisjoint(m._confirmed_episodes),
                         "no confirmed episode id may appear in the think pool")


class TestStatusCounters(unittest.TestCase):
    def test_body_status_carries_the_three_new_counters(self) -> None:
        from creature.body import Body
        root = Path(tempfile.mkdtemp())
        _build_repeated_tape(root, "key", n=50, seed=31)
        body = Body(root, GENOME_PATH)
        body.mind = Mind(GENOME_PATH, root)   # Body.start() would also spin up sense/status threads this test does not need
        for r in read_tape(root):
            body.mind.consume(r)
        status = body._build_status()
        for key in ("glances_confirmed", "glances_surprised", "births_skipped_confirmed"):
            self.assertIn(key, status)
        self.assertEqual(status["glances_confirmed"], body.mind.glances_confirmed)
        self.assertEqual(status["glances_surprised"], body.mind.glances_surprised)
        self.assertGreater(status["glances_confirmed"], 0)


class TestRunG1ChainCoarse(unittest.TestCase):
    """SOLUTIONS #235's own chain, found by grepping every `gaze.glances(`/`glance_rows(` caller (report):
    genome/run_g1.py's `live()`'s `feed()` indexes `fix[k]` for k in range(len(feats)) — with coarse
    declared, feats has 5 entries and fix only 4, so k=4 (the coarse glance) raised IndexError. Every
    other consumer (landing(), ask_glances/ask_plant_glances, tools/self_exam.py, tools/verdict_g4.py,
    genome/ask.py's glance_picture) reads feats/fix independently or only feats — never fix[k] — so this
    was the ONE real crash in the chain (reproduced RED, then fixed by guarding k < len(fix))."""

    def test_feed_no_longer_crashes_on_a_coarse_declaring_genome(self) -> None:
        g = parse_genome(GENOME_TEXT)
        rng = np.random.default_rng(1)
        rows = world.stream_canvas(["circle", "square"], 3, rng)
        dev = run_g1.glance_rows(rows, g, "surprise")
        self.assertEqual([len(f) for _t, f, _fx, _tr, _p in dev], [5] * 6, "4 located + 1 coarse per canvas")
        self.assertEqual([len(fx) for _t, _f, fx, _tr, _p in dev], [4] * 6)
        rec = run_g1.live(g, dev, [], [], ["circle", "square"], [], {}, "never", ask_at_dev=False)
        self.assertEqual(rec["at_dev"]["moments"], 30, "6 canvases x 5 moments (4 located + 1 coarse)")
        # the coarse glance (org.t's 5th of every 5) must be excluded from on/off-thing bookkeeping —
        # not guessed either way — while the 4 located glances are still tracked exactly as before.
        bbg = rec["births_by_glance"]
        self.assertEqual(bbg["moments_on"] + bbg["moments_off"], 24, "6 canvases x 4 LOCATED glances tracked, coarse excluded")

    def test_no_coarse_byte_identical_to_before(self) -> None:
        g = parse_genome(NO_COARSE_TEXT)
        rng = np.random.default_rng(1)
        rows = world.stream_canvas(["circle", "square"], 3, rng)
        dev = run_g1.glance_rows(rows, g, "surprise")
        self.assertEqual([len(f) for _t, f, _fx, _tr, _p in dev], [4] * 6)
        rec = run_g1.live(g, dev, [], [], ["circle", "square"], [], {}, "never", ask_at_dev=False)
        self.assertEqual(rec["at_dev"]["moments"], 24, "6 canvases x 4 moments — unaffected by this fix")
        bbg = rec["births_by_glance"]
        self.assertEqual(bbg["moments_on"] + bbg["moments_off"], 24, "every glance still tracked when there is no coarse one")


class TestLife3aReplayIdentity(unittest.TestCase):
    """"With the gene undeclared, replay of life 3a's tape identical" — both task 1's and task 2's own
    words. Read-only on /data/dev/genome/run-g4-life3a-20260921-1314/ (never touches /data/dev/genome —
    the tape's payload dir is only ever symlinked, creature.replay's own law); the genome text is life
    3a's OWN saved snapshot text (state/organism.json's genome_text — the file it actually ran on, not
    whatever genome/G4.genome reads today, which SOLUTIONS #229's family warns may have moved since)."""

    LIFE3A_ROOT = Path("/data/dev/genome/run-g4-life3a-20260921-1314")

    @classmethod
    def setUpClass(cls) -> None:
        if not cls.LIFE3A_ROOT.exists():
            raise unittest.SkipTest(f"{cls.LIFE3A_ROOT} not present on this box")
        meta = json.loads((cls.LIFE3A_ROOT / "state" / "organism.json").read_text())
        cls.genome_text = meta["genome_text"]

    def test_replay_is_deterministic_and_undeclared_genes_leave_no_trace(self) -> None:
        """Two independent claims on the SAME real 4,675-row tape: (1) determinism — replaying it twice
        under this code produces byte-identical journals (mark vii's own law); (2) the parsed genome
        this life actually ran on (its own saved snapshot text) declares neither SURPRISE nor coarse, so
        every new field this brief adds (residual/confirmed, the coarse row, confirm=) is structurally
        ABSENT from the output — verified on the dict keys, not merely by non-crashing.

        NOT asserted here: byte-identity against life 3a's OWN recorded journal/2026-09-21.jsonl. That
        comparison was run (scratch/life3a_check/, this report) and diverges at seq 2's hash — but the
        SAME divergence reproduces on the UNMODIFIED pre-brief code (verified independently via `git
        stash`; both the modified and pristine trees replay this exact tape to 2,576 mind rows, byte-
        identical TO EACH OTHER, diff=None) — a pre-existing environment/pin drift (SOLUTIONS #229's
        family: something about this box's replay of an old closed life no longer matches its own record
        — the eye tower weights, gate-G-a's written thetas, or a numpy/Python version) that predates and
        is outside this brief; raised, not fixed here."""
        from creature import replay as replay_mod
        self.assertNotIn("SURPRISE", parse_genome(self.genome_text).declared)
        self.assertNotIn("coarse", parse_genome(self.genome_text).gaze)
        tape_path = self.LIFE3A_ROOT / "tape" / "2026-09-21.jsonl"

        tmp_a = Path(tempfile.mkdtemp()); gp_a = _write_genome(tmp_a, self.genome_text, "life3a.genome")
        tmp_b = Path(tempfile.mkdtemp()); gp_b = _write_genome(tmp_b, self.genome_text, "life3a.genome")
        journal_a = replay_mod.run_replay(gp_a, tape_path, tmp_a / "out")
        journal_b = replay_mod.run_replay(gp_b, tape_path, tmp_b / "out")
        rows_a = replay_mod.read_mind_journal(journal_a)
        rows_b = replay_mod.read_mind_journal(journal_b)
        diff = replay_mod.compare(rows_a, rows_b)
        self.assertIsNone(diff, f"two replays of the SAME tape under this code diverged: {diff}")
        self.assertGreater(len(rows_a), 0)
        for r in rows_a:
            self.assertNotIn("residual", r); self.assertNotIn("confirmed", r)
            self.assertNotEqual(r.get("act"), "coarse")
        print(f"[L-4/L-7 pin] life 3a real tape: {len(rows_a)} mind rows, replay-deterministic, "
              f"no residual/confirmed/coarse row anywhere (undeclared genes)")


def _cell_overlaps_block(y: int, x: int, ty: int, tx: int, glance: int = 32, block: int = 16) -> bool:
    """Whether the glance window CENTRED on grid cell (y, x) (16x16 grid, 128 canvas -> 8px/cell) overlaps
    the corrupted [ty:ty+16, tx:tx+16] block — the same window-centre math as genome/gaze.py:glance_window."""
    cy, cx = (y + 0.5) * 8, (x + 0.5) * 8
    top = min(max(round(cy - glance / 2), 0), 128 - glance)
    left = min(max(round(cx - glance / 2), 0), 128 - glance)
    return not (top + glance <= ty or ty + block <= top or left + glance <= tx or tx + block <= left)


if __name__ == "__main__":
    unittest.main()
