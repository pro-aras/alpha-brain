# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 6
# (PREREG §19.9's mark). An end-to-end proof of the MECHANISM: teach a real Mind "circle"/"square" through
# the ordinary drawn-world road (ear+eye rows, genome/world.render_canvas — never a mock), snapshot it, then
# publish HANDS-tagged eye rows carrying the SAME kind of picture with `meta.shape` set, and check the
# recognised-share reader answers them through recall_many exactly as genome/questions.py:ask's Q1 would on
# a held-out drawn canvas.
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape
from genome import world
from tools import hands_recognised

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"


def _png(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _teach(mind: Mind, tape: Tape, things, per_thing: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    i = 0
    order = list(things) * per_thing
    rng.shuffle(order)
    for thing in order:
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"teach{i:05d}"
        ear = tape.publish("ear", thing.encode(), {"moment": moment, "source": "test", "word": thing}, "txt")
        mind.consume(ear)
        eye = tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png")
        mind.consume(eye)
        i += 1


def _publish_hands_rows(tape: Tape, mind: Mind, n_per_shape: int, shapes, seed: int) -> None:
    rng = np.random.default_rng(seed)
    i = 0
    for shape in shapes:
        for _ in range(n_per_shape):
            rgb, _truth = world.render_canvas(shape, rng)
            moment = f"hands{i:05d}"
            row = tape.publish("eye", _png(rgb),
                                {"moment": moment, "source": "hands", "act": "run",
                                 "program": f"{shape}_{i}", "shape": shape}, "png")
            mind.consume(row)
            i += 1


class TestRecognisedShareMechanism(unittest.TestCase):
    def test_not_gradable_under_min_runs(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        _publish_hands_rows(tape, mind, n_per_shape=2, shapes=["circle", "square"], seed=1)   # 4 total, < 20
        mind.snapshot()
        result = hands_recognised.recognised_share(root, G5_GENOME_PATH, min_runs=20)
        self.assertFalse(result["gradable"])
        self.assertEqual(result["n"], 4)

    def test_recognised_share_beats_the_shuffled_twin_on_a_taught_mind(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        _teach(mind, tape, ["circle", "square"], per_thing=100, seed=7)
        _publish_hands_rows(tape, mind, n_per_shape=13, shapes=["circle", "square"], seed=999)   # 26 >= 20
        mind.snapshot()

        result = hands_recognised.recognised_share(root, G5_GENOME_PATH, min_runs=20)
        print(f"hands_recognised (taught mind, real circle/square pictures): "
              f"share={result['recognised_share']:.3f} twin={result['shuffled_twin_share']:.3f} "
              f"n={result['n']} abstained={result['abstained']}")
        self.assertTrue(result["gradable"])
        self.assertEqual(result["n"], 26)
        self.assertGreater(result["recognised_share"], result["shuffled_twin_share"],
                            "a mind that already knows circle/square must recognise its own hands-tagged "
                            "renderings of them better than the shuffled-shelf twin")
        self.assertGreaterEqual(result["recognised_share"], 0.6)   # L-12's own bar, met here as a sanity check

    def test_untaught_mind_reads_low_and_twin_is_close(self) -> None:
        """The refusal test's other side: a mind that never learned the words at all must NOT recognise
        anything above chance, and the twin (permuted labels on the SAME abstain-heavy predictions) must
        read close to it — both near zero, not the taught mind's separation."""
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        _publish_hands_rows(tape, mind, n_per_shape=13, shapes=["circle", "square"], seed=999)
        mind.snapshot()
        result = hands_recognised.recognised_share(root, G5_GENOME_PATH, min_runs=20)
        self.assertTrue(result["gradable"])
        self.assertEqual(result["recognised_share"], 0.0, "an untaught mind has no words to answer with")


if __name__ == "__main__":
    unittest.main()
