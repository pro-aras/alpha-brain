# edit: Claude (Fable 5.1), 2026-09-22 10:26 +0400 — the exam on a mind that knows ONE word (found by the 2 h smoke of g5-seam-1 / L5,
# 2026-09-22 00:45 +04: the frozen-10 twin knew exactly one word on the game tape; tools/self_exam.py passed a one-element `things`
# to ask_glances, whose distractor rule `i % (n - 1)` divided by zero; the reader read (iii) as None on both game rungs).
# The law: ask_glances REFUSES fewer than two things by name (a distractor needs a second thing); self_exam falls back to the
# FULL thing list when fewer than two words were seen and says so in a key written on every branch (#164).
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature import exam as exam_mod
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import run_g1, world
from genome.questions import ask_glances

from .test_exam import GENOME_PATH, _png_bytes


def _build_snapshot_on(root: Path, things, n: int = 60, seed: int = 4242) -> Mind:
    """test_exam._build_snapshot's road on a chosen thing list (the tape shows only those things)."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")
    mind = Mind(GENOME_PATH, root)
    for r in read_tape(root):
        mind.consume(r)
    if mind.snapshot_count == 0:
        mind.snapshot()
    return mind


class TestAskGlancesRefusesOneThing(unittest.TestCase):
    def test_one_thing_is_refused_by_name_not_by_zero_division(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot_on(root, ["circle"], n=40)
        g = mind.genome
        from genome.questions import build_ledgers
        ledgers = build_ledgers(mind.org, mind.moment_word)
        held = world.holdout_canvas(["circle", world.THING_NEVER], 3, np.random.default_rng(2))
        held_g = run_g1.glance_held(held, g, "surprise")
        feats = run_g1.feats_only(held_g)
        never = {world.THING_NEVER: feats[world.THING_NEVER]}
        with self.assertRaises(ValueError) as cm:
            ask_glances(mind.org, ledgers, ["circle"], feats, never, g.ear_blank_zero)
        self.assertIn("two things", str(cm.exception))


class TestSelfExamOnAOneWordMind(unittest.TestCase):
    def test_exam_runs_on_a_one_word_mind_and_names_the_fallback(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot_on(root, ["circle"], n=60)
        hash_before = mind.org.state_hash()
        result = exam_mod.run_exam(root, GENOME_PATH, held=5, check_tape=50)   # the old road: ZeroDivisionError here
        data = result["data"]
        self.assertEqual(data["words_seen"], ["circle"])
        self.assertIs(data["seen_words_fallback_to_all"], True, "one seen word → the seen-words exam is sat on ALL things, and says so")
        self.assertEqual(sorted(data["ask_seen_words"]["Q1"]["per_thing"].keys()), sorted(world.THINGS_11))
        self.assertEqual(mind.org.state_hash(), hash_before)

    def test_exam_on_the_standard_mind_writes_the_fallback_key_false(self) -> None:
        """#164: the new key is written on EVERY branch — a two-or-more-words mind carries it as False."""
        from .test_exam import _build_snapshot
        root = Path(tempfile.mkdtemp())
        _build_snapshot(root, n=60)
        data = exam_mod.run_exam(root, GENOME_PATH, held=5, check_tape=50)["data"]
        self.assertGreaterEqual(len(data["words_seen"]), 2)
        self.assertIs(data["seen_words_fallback_to_all"], False)


class TestExamUnchangedOnTheStandardMind(unittest.TestCase):
    """The regression control for the one-word fix: the exam's stable parts on the standard synthetic mind (test_exam's
    _build_snapshot, seed 4242, n=140; held 5, check_tape 50) hash to the value read under the PRE-FIX code on this box,
    2026-09-22 10:27 +0400, twice (scratch exam_golden.py: run 1 == run 2). A fix that moves this hash changed the ≥ 2-word road."""
    GOLDEN = "331eb985835e8e20588758a490a0f01d91f4a82d92a930294cdf2de35f2fa575"

    @staticmethod
    def stable_hash(data) -> str:
        import hashlib
        keep = {k: data[k] for k in ("ask_seen_words", "ask_all_words", "gaze_landing", "words_seen", "cells", "moments", "chance_q1")}
        return hashlib.sha256(json.dumps(keep, sort_keys=True, default=str).encode()).hexdigest()

    def test_stable_parts_hash_to_the_pre_fix_golden(self) -> None:
        from .test_exam import _build_snapshot
        root = Path(tempfile.mkdtemp())
        _build_snapshot(root)
        data = exam_mod.run_exam(root, GENOME_PATH, held=5, check_tape=50)["data"]
        self.assertEqual(len(data["words_seen"]), 11)
        self.assertEqual(self.stable_hash(data), self.GOLDEN)


if __name__ == "__main__":
    unittest.main()
