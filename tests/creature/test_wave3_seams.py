# edit: Claude (Fable 5.1), 2026-09-21 12:02 +0400 — W3-2c (the rule decider «winner ∈ C», PREREG §18) and the W3-0b TAPE seam
# (the mind and the replay read payloads under the genome's own TAPE path — Builder C's findings 4 and 5).
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.replay import run_replay
from creature.tape import Tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _live(mind: Mind, tape: Tape, things=("circle", "square", "triangle")) -> None:
    rng = np.random.default_rng(7)
    for i, thing in enumerate(things):
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"s{i:03d}"
        at = f"2026-09-21T00:00:{i:02d}.000Z"
        mind.consume(tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt", at=at))
        mind.consume(tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png", at=at))


class TestRuleEvidenceWinner(unittest.TestCase):
    def test_winner_in_cluster_true_other_cluster_false_empty_false(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = Mind(GENOME_PATH, root)
        _live(mind, Tape(root))
        area = mind.org.sight
        alive = [int(i) for i in np.nonzero(np.asarray(area.alive, dtype=bool)[: area.n])[0]]
        self.assertGreaterEqual(len(alive), 2, "the toy needs two alive sight cells")
        w = alive[0]
        glance = np.asarray(area.cells[w], dtype=float)          # cos 1.0 with itself: the winner, and it resonates
        self.assertTrue(mind._rule_evidence([w], glance))
        self.assertTrue(mind._rule_evidence([alive[1], w], glance), "the winner anywhere in C is enough")
        others = [c for c in alive if c != w and float(np.asarray(area.cos(glance))[c]) < 1.0]
        self.assertTrue(others, "a second, non-identical cell is needed for the control")
        self.assertFalse(mind._rule_evidence([others[0]], glance), "a cluster without the winner reads False")
        self.assertFalse(mind._rule_evidence([], glance))


class TestTapePathSeam(unittest.TestCase):
    def test_mind_and_replay_read_payloads_under_the_declared_tape_path(self) -> None:
        genome_text = GENOME_PATH.read_text() + "\nTAPE run/tape2\n"
        genome_path = Path(tempfile.mkdtemp()) / "tape2.genome"
        genome_path.write_text(genome_text)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        tape = Tape(root, declared_path="run/tape2")
        _live(mind, tape)
        self.assertFalse((root / "tape").exists(), "nothing may exist under root/tape: the read could only come from tape2")
        self.assertTrue((root / "tape2" / "payload").exists())
        self.assertGreater(mind.org.t, 0, "the mind lived the canvases — it read their payloads under tape2")
        mind.snapshot()
        live_rows = [json.loads(l) for l in (root / "journal").glob("*.jsonl").__next__().read_text().splitlines()]
        live_rows = [r for r in live_rows if "hash" in r]
        self.assertGreaterEqual(len(live_rows), 3)
        day = next((root / "tape2").glob("*.jsonl"))
        out_journal = run_replay(genome_path, day, Path(tempfile.mkdtemp()))
        replay_rows = [json.loads(l) for l in Path(out_journal).read_text().splitlines()]
        replay_rows = [r for r in replay_rows if "hash" in r]
        self.assertEqual([r["hash"] for r in replay_rows], [r["hash"] for r in live_rows], "the replay under TAPE run/tape2 reads the same payloads")


if __name__ == "__main__":
    unittest.main()
