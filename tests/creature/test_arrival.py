# edit: Claude (Fable 5.1), 2026-09-20 12:01 +0400 — PREREG §15 (Amendment 5): a never-heard word OPENS AN ARRIVAL (the birth budget
# is fresh before the moment that meets it); the negative twin without the gene spends its budget once and refuses;
# the arrival journal replays byte-identical; the heard-set survives a resume. Life 1 (00:42 → 12:xx +04, 2026-09-20)
# never called new_arrival: arrivals 0, 419 births refused, nothing born after 07:41.
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import replay as replay_mod
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
WAVE2_GENOME = ROOT / "tests" / "creature" / "G4-wave2-test.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _genomes(tmp: Path) -> tuple[Path, Path]:
    """The wave-2 test genome with BUDGET 3 per arrival: one copy declaring ARRIVAL, one twin without it."""
    base = WAVE2_GENOME.read_text()
    assert base.count("BUDGET 400 per arrival") == 1
    base = base.replace("BUDGET 400 per arrival", "BUDGET 3 per arrival")
    with_ = tmp / "with-arrival.genome"; with_.write_text(base + "\nARRIVAL  never-heard word\n")
    without = tmp / "without-arrival.genome"; without.write_text(base)
    return with_, without


def _build_tape(root: Path, seed: int = 4242) -> None:
    """10 canvases each of two words interleaved, then 10 of a THIRD word never heard before."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    order = ["circle", "square"] * 10 + ["triangle"] * 10
    for i, thing in enumerate(order):
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


def _run(genome: Path, root: Path) -> tuple[Mind, list]:
    mind = Mind(genome, root)
    for r in read_tape(root):
        mind.consume(r)
    rows = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip() and "event" not in l]
    return mind, [r for r in rows if "moment" in r]


class TestArrivalOpensTheBudget(unittest.TestCase):
    def test_never_heard_word_refreshes_and_the_twin_refuses(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        with_, without = _genomes(tmp)
        root_a, root_b = tmp / "a", tmp / "b"
        _build_tape(root_a); _build_tape(root_b)     # the same seed -> the same canvases on both roads

        mind_a, rows_a = _run(with_, root_a)
        mind_b, rows_b = _run(without, root_b)

        # the gene: circle -> 1, square -> 2, triangle -> 3; on the rows where each first met the eye
        arrivals = [(r["word"], r["arrival"]) for r in rows_a if "arrival" in r]
        self.assertEqual(arrivals, [("circle", 1), ("square", 2), ("triangle", 3)])
        self.assertEqual(mind_a.org.arrivals, 3)
        # the budget was fresh when the triangle arrived: something was born ON or AFTER its first canvas
        tri_rows = [r for r in rows_a if r["word"] == "triangle"]
        self.assertGreater(sum(len(r["births"]) for r in tri_rows), 0, "the third word's arrival should birth cells from a fresh budget")

        # the negative twin: never told, spends BUDGET 3 once, refuses, and its rows carry no arrival field
        self.assertEqual(mind_b.org.arrivals, 0)
        self.assertGreater(mind_b.org.c["births_refused_budget"], 0)
        self.assertFalse(any("arrival" in r for r in rows_b))
        tri_rows_b = [r for r in rows_b if r["word"] == "triangle"]
        self.assertEqual(sum(len(r["births"]) for r in tri_rows_b), 0, "the twin's spent budget births nothing for the third word")

        # the two roads differ ONLY through the budget: the same tape, the same first canvases (control: rows before any refusal agree)
        self.assertEqual(rows_a[0]["fix"], rows_b[0]["fix"])
        self.assertEqual(rows_a[0]["word"], rows_b[0]["word"])

    def test_arrival_journal_replays_identical(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        with_, _ = _genomes(tmp)
        root = tmp / "live"
        _build_tape(root)
        _mind, live_rows = _run(with_, root)
        tape_file = sorted((root / "tape").glob("*.jsonl"))[0]
        out = replay_mod.run_replay(with_, tape_file, tmp / "replay")
        got = replay_mod.read_mind_journal(out)
        want = [r for r in got]  # shape check
        self.assertIsNone(replay_mod.compare(got, live_rows))
        self.assertEqual(sum(1 for r in got if "arrival" in r), 3)

    def test_heard_set_survives_a_resume(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        with_, _ = _genomes(tmp)
        root = tmp / "resume"
        _build_tape(root)
        rows = list(read_tape(root))
        mind = Mind(with_, root)
        for r in rows[:20]:          # 10 canvases: circle and square met, the triangle not yet
            mind.consume(r)
        mind.snapshot()
        self.assertEqual(mind._heard, {"circle", "square"})
        resumed, last_seq = Mind.resume(with_, root)
        self.assertEqual(last_seq, mind.last_seq)
        self.assertEqual(resumed._heard, {"circle", "square"})
        self.assertEqual(resumed.org.arrivals, 2)
        for r in rows[20:]:
            resumed.consume(r)
        self.assertEqual(resumed.org.arrivals, 3)


if __name__ == "__main__":
    unittest.main()
