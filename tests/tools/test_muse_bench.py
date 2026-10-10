# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:53 +0400 — the CONTEMPLATE-1 bench's own
# tests (PREREG-CONTEMPLATE-1 §2's instrument discipline): the tape build is deterministic, the twins are
# the planted bag with its order destroyed, the hearsay schedule sits at the life's tail, and the plant
# arm's doctored trigger BITES on the control (G-PLANT's planted form caught at short scale here, caught
# by the bench's control check at full scale). The full arc runs as the bench itself (records in
# docs/brain/muse/records/), never inside the unit suite.
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.brain import muse_bench as B
from tools.brain.muse_bench import (BENCH_SEED, CONTROL, GLOSS, HEARSAY_N, PLANTED, THING_ROUNDS, TOY_THINGS,
                                    build_tape, drive, genome_text, hearsay_after, twin_texts)


class TestToyBuild(unittest.TestCase):
    def test_genome_text_is_deterministic_and_carries_the_bench_lines(self) -> None:
        a, b = genome_text(), genome_text()
        self.assertEqual(a, b)
        self.assertIn("hears toy", a)
        self.assertIn(B.SLEEP_LINE, a)
        self.assertNotIn("every 2500 moments", a)

    def test_hearsay_schedule_sits_at_the_tail_star_moments(self) -> None:
        after = hearsay_after()
        star_ix = [i for i in range(THING_ROUNDS * len(TOY_THINGS)) if TOY_THINGS[i % len(TOY_THINGS)] == "star"]
        self.assertEqual(sorted(after), star_ix[-HEARSAY_N:])
        self.assertEqual(len(after), HEARSAY_N, "presence: the hearsay count is the declared one")

    def test_tape_build_deterministic(self) -> None:
        r1 = Path(tempfile.mkdtemp())
        r2 = Path(tempfile.mkdtemp())
        try:
            build_tape(r1, B._Clock())
            build_tape(r2, B._Clock())
            d1 = sorted((r1 / "tape").glob("*.jsonl"))
            d2 = sorted((r2 / "tape").glob("*.jsonl"))
            self.assertEqual(len(d1), 1)
            self.assertEqual(d1[0].read_bytes(), d2[0].read_bytes(), "the arc's tape is byte-identical")
            rows = B._rows(r1)
            self.assertGreater(len(rows), 500, "presence: the toy life + the arc's rows")
            senses = {}
            for r in rows:
                senses[r["sense"]] = senses.get(r["sense"], 0) + 1
            self.assertEqual(senses.get("chat"), 24, "the arc's 24 heard sentences (planted, control, "
                                                     "10 twins, tent, fruit, 10 twin re-asks)")
        finally:
            shutil.rmtree(r1, ignore_errors=True)
            shutil.rmtree(r2, ignore_errors=True)


class TestTwinsAndGloss(unittest.TestCase):
    def test_the_twins_are_the_planted_bag_order_destroyed(self) -> None:
        twins = twin_texts()
        bag = sorted(PLANTED.split())
        self.assertEqual(len(twins), 10, "presence: ten null trials")
        for t in twins:
            self.assertEqual(sorted(t.split()), bag, "the same bag of words")
            self.assertNotEqual(t, PLANTED, "order destroyed")
        self.assertEqual(twins, twin_texts(), "the seeded draws are deterministic")

    def test_the_gloss_words_are_ear_legal(self) -> None:
        from genome.world import encode_word
        for word, gloss in GLOSS.items():
            self.assertIn(word, PLANTED.split(), "the parent answers a question the chain asks")
            for w in gloss.split():
                encode_word(w, True)      # raises unless the ear can take it (<= 8 letters a-z)


class TestPlantBites(unittest.TestCase):
    def test_the_doctored_trigger_spawns_a_control_chain(self) -> None:
        """G-PLANT's short-scale form: the control ALONE under the doctored trigger spawns a chain —
        the instrument proves it sees the mechanism's absence before any pass is trusted (#246)."""
        tape_root = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp()) / "run"
        try:
            build_tape(tape_root, B._Clock(), short=True)
            rec = drive(tape_root, True, work, plant=True)
            self.assertGreater(rec["plant_calls"], 0, "the plant asserts it ran")
            self.assertGreaterEqual(rec["state"]["chains_started"], 1,
                                    "the plant asserts it changed the bytes: the control spawned a chain")
            seeds = [B.MUSE.seed_of(CONTROL.split())]
            self.assertTrue(any(cid in rec["chains"] for cid in seeds),
                            "the chain is the control's own content")
        finally:
            shutil.rmtree(tape_root, ignore_errors=True)
            shutil.rmtree(work.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
