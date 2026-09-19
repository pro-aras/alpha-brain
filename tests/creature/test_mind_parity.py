# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 21:52 +0400 — A2 tests: the determinism-law AST sweep, the PNG
# round-trip, and gate G4-2 (mind parity against run_g1.live's hash_dev) with its swapped-canvas control.
from __future__ import annotations

import ast
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import run_g1, world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"
MIND_SOURCE = ROOT / "creature" / "mind.py"

# G4-2's pin (docs/G4-PREREG.md §4, read independently by the orchestrator at git 9a36475, 2026-09-19 21:26 +0400):
# hash_dev for G4-skeleton.genome over toy_streams(genome, 5)'s 660 dev canvases, glanced by glance_rows(dev, genome,
# "surprise"), with_arr2=False with_plant=False ask_at_dev=False -- 2,640 moments, ~10 s.
PINNED_HASH_DEV = "d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, dev) -> None:
    tape = Tape(root)
    for i, (thing, rgb, _truth) in enumerate(dev):
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "maker", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "maker"}, "png")


class TestMindHasNoClock(unittest.TestCase):
    def test_mind_has_no_clock(self) -> None:
        """Determinism law (PREREG §2.3): creature/mind.py imports none of time, datetime, random,
        os.urandom. An AST sweep, not a text grep (comments/strings must not trip it either way)."""
        tree = ast.parse(MIND_SOURCE.read_text(), filename=str(MIND_SOURCE))
        forbidden_modules = {"time", "datetime", "random"}
        offenders = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in forbidden_modules:
                        offenders.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in forbidden_modules:
                    offenders.append(f"from {node.module} import ...")
            elif isinstance(node, ast.Attribute) and node.attr == "urandom":
                offenders.append("os.urandom")
        self.assertEqual(offenders, [], f"creature/mind.py must never read the wall clock or randomness itself: {offenders}")


class TestPngRoundTrip(unittest.TestCase):
    def test_canvas_round_trips_byte_exact(self) -> None:
        genome = parse_genome(GENOME_PATH.read_text())
        rng = np.random.default_rng(20260919)
        for thing in ("circle", "square", "diamond"):
            rgb, _truth = world.render_canvas(thing, rng)
            png = _png_bytes(rgb)
            back = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"), dtype=np.uint8)
            self.assertTrue(np.array_equal(rgb, back), f"PNG round-trip changed bytes for {thing!r}")


class TestGate42MindParity(unittest.TestCase):
    """Gate G4-2 (PREREG §4): the creature's Mind fed G1-toy's dev canvases as a tape must reach the same
    state_hash as run_g1.live's hash_dev for the identical genome and canvases."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.genome_text = GENOME_PATH.read_text()
        cls.genome = parse_genome(cls.genome_text)
        cls.things, cls.arr2, cls.dev, cls.held, cls.a2, cls.plant, cls.shuffle_words, cls.n_checked = run_g1.toy_streams(cls.genome, plant_showings=5)
        assert len(cls.dev) == 660, f"expected 660 dev canvases (11 things x 60), got {len(cls.dev)}"

    def test_g4_2_parity(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, self.dev)

        mind = Mind(GENOME_PATH, root)
        n_rows = 0
        for row in read_tape(root):
            mind.consume(row)
            n_rows += 1
        self.assertEqual(n_rows, len(self.dev) * 2)
        self.assertEqual(mind.org.t, len(self.dev) * int(self.genome.gaze["fixations"]))

        got = mind.org.state_hash()

        # held_g's content is provably unused by this call: `held = feats_only(held_g)` and `never_h` are
        # only ever dereferenced inside the ask_dev/ask_arr2/plant blocks, all gated False here (verified
        # by reading genome/run_g1.py's live()) -- {} avoids ~380 canvases of extra gazing just to build it.
        expected = run_g1.live(self.genome, run_g1.glance_rows(self.dev, self.genome, "surprise"), [], [],
                                self.things, self.arr2, {}, world.THING_NEVER,
                                with_arr2=False, with_plant=False, ask_at_dev=False)["hash_dev"]
        self.assertEqual(got, expected, "Mind's state_hash must match run_g1.live's hash_dev")
        self.assertEqual(got, PINNED_HASH_DEV, "must also match the PREREG's independently-read pin")

    def test_g4_2_control_swapped_canvas(self) -> None:
        """Control: swap two canvases in the feed order -> the hash must differ."""
        swapped = list(self.dev)
        swapped[0], swapped[1] = swapped[1], swapped[0]

        root = Path(tempfile.mkdtemp())
        _build_tape(root, swapped)
        mind = Mind(GENOME_PATH, root)
        for row in read_tape(root):
            mind.consume(row)
        swapped_hash = mind.org.state_hash()

        root2 = Path(tempfile.mkdtemp())
        _build_tape(root2, self.dev)
        mind2 = Mind(GENOME_PATH, root2)
        for row in read_tape(root2):
            mind2.consume(row)
        correct_hash = mind2.org.state_hash()

        self.assertNotEqual(swapped_hash, correct_hash, "swapping two canvases must change the state_hash")
        self.assertEqual(correct_hash, PINNED_HASH_DEV)


class TestSnapshotResume(unittest.TestCase):
    """snapshot()/Mind.resume() round-trip: a small tape (not the full 660), split so a snapshot lands
    mid-stream, then resumed and fed the rest -- must reach the same state_hash as one continuous mind,
    and ledger.json must carry the sight/words ledgers genome/ask.py's load() reads."""

    def test_snapshot_then_resume_matches_continuous(self) -> None:
        genome = parse_genome(GENOME_PATH.read_text())
        rng = np.random.default_rng(4242)
        dev = [(t, *world.render_canvas(t, rng)) for t in ("circle", "square", "circle", "diamond", "square", "circle")]

        root_a = Path(tempfile.mkdtemp())
        _build_tape(root_a, dev)
        mind_a = Mind(GENOME_PATH, root_a)
        for row in read_tape(root_a):
            mind_a.consume(row)
        continuous_hash = mind_a.org.state_hash()

        root_b = Path(tempfile.mkdtemp())
        _build_tape(root_b, dev)
        rows = list(read_tape(root_b))
        half = len(rows) // 2
        mind_b = Mind(GENOME_PATH, root_b)
        for row in rows[:half]:
            mind_b.consume(row)
        mind_b.snapshot()
        self.assertTrue((root_b / "state" / "organism.npz").exists())
        self.assertTrue((root_b / "state" / "organism.json").exists())
        self.assertTrue((root_b / "state" / "ledger.json").exists())

        resumed, last_seq = Mind.resume(GENOME_PATH, root_b)
        self.assertEqual(last_seq, mind_b.last_seq)
        self.assertEqual(resumed.org.state_hash(), mind_b.org.state_hash())
        for row in rows[half:]:
            if row["seq"] > last_seq:
                resumed.consume(row)
        self.assertEqual(resumed.org.state_hash(), continuous_hash, "resume must reproduce the continuous life")

        ledger = json.loads((root_b / "state" / "ledger.json").read_text())
        for key in ("last_seq", "moment_word", "moments", "sight", "words"):
            self.assertIn(key, ledger)
        self.assertTrue(ledger["sight"] or ledger["words"], "the derived ledgers must not be empty on a real life")


if __name__ == "__main__":
    unittest.main()
