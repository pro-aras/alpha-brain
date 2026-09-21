# edit: Claude (Fable 5.1), 2026-09-21 20:57 +0400 — PINNED_HASH_DEV moved to the live-block digest b0531503… (Builder F's state_hash merged on g5-integration; found by a content sweep for the old digest — F's report named only the genome-suite pin, #214).
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 01:05 +0400 — A9: PREDICT + FAST in the mind (PREREG §11.1
# steps 1-2). err/lr/ep on every eye-row mind row, replay-identical; sight-only canvases now live through
# Organism.moment_sight (word null); episodes survive a snapshot/resume; the skeleton's own hash is unchanged (G4-8).
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import replay as replay_mod
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import run_g1, world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
SKELETON_GENOME = ROOT / "genome" / "G4-skeleton.genome"
WAVE2_GENOME = ROOT / "tests" / "creature" / "G4-wave2-test.genome"
PINNED_HASH_DEV = "b05315037ff98529836472e6ddd9ebb5a45742b0511f5facf6b73cd754fa1e3f"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_mixed_tape(root: Path, n_worded: int = 40, n_sight_only: int = 10, seed: int = 909) -> None:
    """Worded canvases (ear then eye) interleaved with sight-only canvases (eye, no matching ear)."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    order = (["worded"] * n_worded) + (["sight"] * n_sight_only)
    rng2 = np.random.default_rng(seed + 1)
    rng2.shuffle(order)
    for i, kind in enumerate(order):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if kind == "worded":
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


class TestWave2GenomeParses(unittest.TestCase):
    def test_wave2_test_genome_declares_predict_and_fast(self) -> None:
        genome = parse_genome(WAVE2_GENOME.read_text())
        self.assertIn("PREDICT", genome.declared)
        self.assertIn("FAST", genome.declared)


class TestPredictFastJournaling(unittest.TestCase):
    def test_err_lr_ep_on_every_eye_row_and_sight_only_lives_through_moment_sight(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_mixed_tape(root, n_worded=30, n_sight_only=8)
        mind = Mind(WAVE2_GENOME, root)
        rows = list(read_tape(root))
        eye_rows = [r for r in rows if r["sense"] == "eye"]
        for r in rows:
            mind.consume(r)

        journal_files = sorted((root / "journal").glob("*.jsonl"))
        self.assertEqual(len(journal_files), 1)
        import json
        journal_rows = [json.loads(l) for l in journal_files[0].read_text().splitlines() if l.strip()]
        canvas_rows = [r for r in journal_rows if "event" not in r and "sleep" not in r]
        self.assertEqual(len(canvas_rows), len(eye_rows))

        worded = [r for r in canvas_rows if r.get("word") is not None and "sight_only" not in r]
        sight_only = [r for r in canvas_rows if r.get("word") is None]
        self.assertEqual(len(worded) + len(sight_only), len(eye_rows))
        self.assertGreater(len(worded), 0)
        self.assertGreater(len(sight_only), 0, "the mixed tape must include sight-only canvases")

        for r in worded:
            self.assertIn("err", r); self.assertIn("lr", r); self.assertIn("ep", r)
            self.assertIsInstance(r["err"], float)
            self.assertIsInstance(r["lr"], float)
        for r in sight_only:
            self.assertIn("err", r); self.assertIn("ep", r)
            self.assertNotIn("sight_only", r, "FAST declared: sight-only canvases are no longer the old skip-and-count row")
            self.assertIsNotNone(r["ep"], "a sight-only canvas with FAST declared must still write an episode")

        fixations = int(mind.genome.gaze["fixations"])
        self.assertEqual(mind.org.moments_sight_only, len(sight_only) * fixations, "moments_sight_only counts GLANCES, not canvases")
        self.assertEqual(mind.sight_only_skipped, 0, "FAST declared: nothing is skipped any more")
        self.assertIsNotNone(mind.episodes)
        self.assertEqual(len(mind.episodes), len(eye_rows))

    def test_replay_is_byte_identical_with_predict_and_fast(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_mixed_tape(root, n_worded=25, n_sight_only=6, seed=111)
        mind = Mind(WAVE2_GENOME, root)
        for r in read_tape(root):
            mind.consume(r)

        tape_files = sorted((root / "tape").glob("*.jsonl"))
        journal_files = sorted((root / "journal").glob("*.jsonl"))
        self.assertEqual(len(tape_files), 1)
        self.assertEqual(len(journal_files), 1)

        out_dir = Path(tempfile.mkdtemp())
        rc = replay_mod.main(["--genome", str(WAVE2_GENOME), "--tape", str(tape_files[0]),
                               "--against", str(journal_files[0]), "--out", str(out_dir)])
        self.assertEqual(rc, 0)

    def test_episodes_and_predictor_survive_snapshot_and_resume(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_mixed_tape(root, n_worded=20, n_sight_only=5, seed=222)
        mind_a = Mind(WAVE2_GENOME, root)
        for r in read_tape(root):
            mind_a.consume(r)
        continuous_hash = mind_a.org.state_hash()
        continuous_ep_count = len(mind_a.episodes)
        continuous_last_winner = mind_a.predictor._last_winner

        root_b = Path(tempfile.mkdtemp())
        _build_mixed_tape(root_b, n_worded=20, n_sight_only=5, seed=222)
        rows = list(read_tape(root_b))
        half = len(rows) // 2
        mind_b = Mind(WAVE2_GENOME, root_b)
        for r in rows[:half]:
            mind_b.consume(r)
        mind_b.snapshot()
        self.assertTrue((root_b / "state" / "episodes.npz").exists())

        resumed, last_seq = Mind.resume(WAVE2_GENOME, root_b)
        self.assertIsNotNone(resumed.episodes)
        self.assertEqual(len(resumed.episodes), len(mind_b.episodes))
        self.assertIsNotNone(resumed.predictor)
        if mind_b.predictor._last_winner is not None:
            self.assertTrue(np.array_equal(resumed.predictor._last_winner, mind_b.predictor._last_winner))
        for r in rows[half:]:
            if r["seq"] > last_seq:
                resumed.consume(r)
        self.assertEqual(resumed.org.state_hash(), continuous_hash)
        self.assertEqual(len(resumed.episodes), continuous_ep_count)
        if continuous_last_winner is not None:
            self.assertTrue(np.array_equal(resumed.predictor._last_winner, continuous_last_winner))


class TestSkeletonHashUnchanged(unittest.TestCase):
    """G4-8: G4-skeleton.genome (no wave-2 gene declared) must still reach the exact PREREG pin after
    the A9 changes to _consume_eye — the same gate G4-2 test, re-run here as the wave-2 regression."""

    def test_skeleton_pin_unchanged(self) -> None:
        genome = parse_genome(SKELETON_GENOME.read_text())
        self.assertEqual(genome.declared, {}, "the skeleton must declare no wave-2 gene at all")
        things, arr2, dev, held, a2, plant, shuffle_words, n_checked = run_g1.toy_streams(genome, plant_showings=5)
        self.assertEqual(len(dev), 660)

        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        for i, (thing, rgb, _truth) in enumerate(dev):
            moment = f"m{i:05d}"
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "maker", "word": thing}, "txt")
            tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "maker"}, "png")

        mind = Mind(SKELETON_GENOME, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertIsNone(mind.episodes)
        self.assertIsNone(mind.predictor)
        self.assertEqual(mind.org.state_hash(), PINNED_HASH_DEV)


if __name__ == "__main__":
    unittest.main()
