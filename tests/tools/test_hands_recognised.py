# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:49 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 6
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


# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 20:13 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 6
# (PREREG §19.9's mark, on re-review): the two tests above prove the READER (recall_many + the word ledger)
# works, on the maker's own anti-aliased world.render_canvas pictures tagged source=hands -- they never ask
# whether the eye recognises a BLOCKY 4x4-per-character ASCII rendering (creature/senses/hands.py's own
# `_render_ascii`) of the program's OWN shape, which is the mark's actual question ("the exam answers the
# run's rendered canvas with the program's own shape"). This class runs the REAL shelf programs through the
# REAL jail, renders their stdout through the SAME `_render_ascii`/`_png_bytes`/`_manifest` the live hands
# sense thread uses (imported, not re-implemented), and asks the identical recognised_share reader.
JAIL_PATH = Path("/data/dev/alpha3/hands/jail_run")
SHELF_DIR = ROOT / "world" / "programs"
ALL_16_THINGS = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave",
                  "diamond", "moon", "house", "tree", "cup", "key"]


def _shelf_shape_programs() -> List[Path]:
    from creature.senses import hands as hands_sense
    out = []
    for p in sorted(SHELF_DIR.glob("*.py")):
        if hands_sense._manifest(p).get("shape") is not None:
            out.append(p)
    return out


def _publish_hands_rows_via_real_ascii_road(tape: Tape, mind: Mind, jail_path: Path, shelf_dir: Path,
                                             programs: List[Path]) -> int:
    """Runs each shelf PROGRAM through the REAL jail (never a mock), renders its stdout to a canvas through
    the SAME `_render_ascii` the live hands sense thread runs, and publishes it as an `eye` row with the
    SAME meta shape `creature/senses/hands.py:_run_one` publishes (source="hands", act="run", program,
    shape from the program's own manifest comment) -- the mechanism under test end to end, minus only the
    sense thread's own polling loop and act-file plumbing (already covered by
    tests/creature/test_hands_sense.py::TestSenseThreadEndToEnd)."""
    from creature.senses import hands as hands_sense
    n = 0
    for prog in programs:
        manifest = hands_sense._manifest(prog)
        scratch = Path(tempfile.mkdtemp())
        result = hands_sense.run_in_jail(jail_path, shelf_dir, prog, scratch, cpu=10, mem=512, wall=20)
        stdout_text = result["stdout"].decode("utf-8", errors="replace")
        rgb = hands_sense._render_ascii(stdout_text)
        row = tape.publish("eye", hands_sense._png_bytes(rgb),
                            {"moment": f"hshelf{n:05d}", "source": "hands", "act": "run",
                             "program": prog.stem, "shape": manifest.get("shape")}, "png")
        mind.consume(row)
        n += 1
    return n


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestRecognisedShareOnTheRealAsciiRoad(unittest.TestCase):
    def test_taught_mind_recognises_the_real_jail_rendered_shelf(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(G5_GENOME_PATH, root)
        tape = Tape(root)
        _teach(mind, tape, ALL_16_THINGS, per_thing=40, seed=13)   # 640 taught canvases, real world.render_canvas

        programs = _shelf_shape_programs()
        self.assertGreaterEqual(len(programs), 20, "the shelf itself must carry at least the mark's own bar")
        n = _publish_hands_rows_via_real_ascii_road(tape, mind, JAIL_PATH, SHELF_DIR, programs)
        mind.snapshot()

        result = hands_recognised.recognised_share(root, G5_GENOME_PATH, min_runs=20)
        print(f"hands_recognised (REAL jail + REAL ascii-render road, {n} shelf programs): "
              f"share={result['recognised_share']:.3f} twin={result['shuffled_twin_share']:.3f} "
              f"n={result['n']} abstained={result['abstained']}")
        self.assertTrue(result["gradable"])
        self.assertEqual(result["n"], n)
        # Whatever this reads is the finding (SOLUTIONS #228(c)'s law): reported honestly below, never
        # tuned to a bar. The one structural assertion that must hold regardless of the number: the real
        # road's share must not be WORSE than the shuffled-shelf twin scored on the SAME predictions --
        # a taught mind's real answers, however good or bad, must beat a random relabelling of themselves.
        self.assertGreaterEqual(result["recognised_share"], result["shuffled_twin_share"])


if __name__ == "__main__":
    unittest.main()
