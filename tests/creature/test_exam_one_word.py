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
    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:48 +0400 — L-6/ANSWER (docs/briefs/LIFE-A-ANSWER-SELF.md
    # #2): re-pinned after `ask_glances` gained two ADDITIVE keys (Q1's "hedge_rate", Q5's "graded") -- verified
    # the move is additive-only: hashing `data` with those two keys stripped out reproduces the PRIOR golden
    # (331eb985835e8e20588758a490a0f01d91f4a82d92a930294cdf2de35f2fa575) exactly, so no existing computed value moved.
    # edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:12 +0400 — A4-LADDER-PREREG §2.2 task 2:
    # re-pinned again after every abstain-reason dict in genome/questions.py gained "minority": 0 (#235 — a
    # widened set is a chain; every reader must have the key even on a genome, like this test's G4-skeleton,
    # that never declares the clause and can never populate it). Verified additive-only the same way: hashing
    # `data` with every "minority" key stripped from the nested abstain dicts reproduces the PRIOR golden
    # (25e16cd8ddee01ec606205f6d8932633fdb91ea012442791c00a7b8fa6f084f9) exactly.
    GOLDEN = "4598b746df7626a3c89adecfc9a673a54b27085da02c8516198a36943f980617"

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


# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:12 +0400 — A4-LADDER-PREREG §2.2 task 3:
# THE SITTER SITS BOTH LAWS, live end-to-end (not just ask_glances/recall_many in isolation, already
# covered in tests/genome/test_answer_grade.py) — a real Mind, a real snapshot, run through
# creature/exam.py:run_exam exactly as the voice thread calls it every EXAM.every canvases.
_MAJORITY_GENOME_PATH = Path(tempfile.mkdtemp()) / "g4-skeleton-plus-answer-majority.genome"
_MAJORITY_GENOME_PATH.write_text(
    GENOME_PATH.read_text() + "THRESH cell own band history 30\n"
    "ANSWER resembles under own-band; unknown below 0.911; sure only when a majority of the glances light\n"
)


class TestSelfExamBothLaws(unittest.TestCase):
    def test_old_law_keys_none_and_noted_when_the_clause_is_undeclared(self) -> None:
        """#164: the schema is stable across every genome -- the keys exist even when there is nothing to
        sit twice (G4-skeleton.genome never declares ANSWER at all)."""
        root = Path(tempfile.mkdtemp())
        _build_snapshot_on(root, list(world.THINGS_11), n=60)
        data = exam_mod.run_exam(root, GENOME_PATH, held=5, check_tape=50)["data"]
        self.assertFalse(data["answer_majority_declared"])
        self.assertIsNone(data["ask_seen_words_old_law"]); self.assertIsNone(data["ask_all_words_old_law"])
        self.assertIsNone(data["lit_counts_seen"])
        self.assertIsNotNone(data["old_law_note"])

    def test_both_laws_sat_on_the_same_snapshot_when_the_clause_is_declared(self) -> None:
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot_on(root, list(world.THINGS_11), n=60)
        h0 = mind.org.state_hash()
        result = exam_mod.run_exam(root, _MAJORITY_GENOME_PATH, held=5, check_tape=50)
        data = result["data"]
        self.assertTrue(data["answer_majority_declared"])
        self.assertIsNone(data["old_law_note"])
        self.assertIsInstance(data["ask_seen_words_old_law"], dict)
        self.assertIsInstance(data["ask_all_words_old_law"], dict)
        # the read-side override never touches the organism -- a real Organism, not a toy
        self.assertEqual(mind.org.state_hash(), h0)
        self.assertTrue(data["organism_hash_unchanged_by_exam"])
        # lit_counts_seen: a real distribution over the seen canvases, keys 0..len(gaze fixations)
        counts = data["lit_counts_seen"]
        self.assertIsInstance(counts, dict); self.assertTrue(counts)
        self.assertTrue(all(0 <= int(k) <= 4 for k in counts))   # G4-skeleton's GAZE: 4 located, no coarse
        # Q1 old law is well-formed (its own acc in [0, 1]) and structurally present beside the new law
        self.assertIn("acc", data["ask_seen_words_old_law"]["Q1"])
        self.assertGreaterEqual(data["ask_seen_words_old_law"]["Q1"]["acc"], 0.0)


# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:16 +0400 — A4-LADDER-PREREG §2.2 A3/task 5,
# advisor-caught (every other tool this ladder landed has a pin; answer_readtwin.py had none): a minimal,
# hermetic test of tools/answer_readtwin.py:read_both_laws on a real built snapshot -- the one road the
# orchestrator actually drives at 05:00 (a `--snapshot`/`--genome` pair), never the live alpha4-1 root itself.
class TestAnswerReadtwin(unittest.TestCase):
    def test_read_both_laws_on_a_real_snapshot(self) -> None:
        from tools.answer_readtwin import read_both_laws
        root = Path(tempfile.mkdtemp())
        mind = _build_snapshot_on(root, list(world.THINGS_11), n=60)
        h0 = mind.org.state_hash()
        out = read_both_laws(root, _MAJORITY_GENOME_PATH, held_n=5)
        self.assertTrue(out["answer_majority_declared"])
        self.assertTrue(out["organism_unchanged"])
        self.assertEqual(out["hash_before"], h0); self.assertEqual(out["hash_after"], h0)
        for law in ("new_law", "old_law"):
            self.assertIn(law, out)
            for key in ("zog", "vex", "spiral", "Q1"):
                self.assertIn(key, out[law], f"{law} missing {key!r}")
        for thing_key in ("zog", "vex"):
            self.assertIn("answered_rate", out["new_law"][thing_key])
            self.assertIn("graded", out["new_law"][thing_key])
        self.assertIn("acc", out["new_law"]["Q1"])

    def test_read_both_laws_undeclared_genome_both_passes_identical(self) -> None:
        """The negative control: on a genome that never declares the clause, new_law and old_law read the
        SAME numbers (the override forces a no-op gate on either side) -- `answer_majority_declared` says so."""
        from tools.answer_readtwin import read_both_laws
        root = Path(tempfile.mkdtemp())
        _build_snapshot_on(root, list(world.THINGS_11), n=60)
        out = read_both_laws(root, GENOME_PATH, held_n=5)
        self.assertFalse(out["answer_majority_declared"])
        self.assertEqual(out["new_law"]["Q1"]["acc"], out["old_law"]["Q1"]["acc"])
        self.assertEqual(out["new_law"]["spiral"], out["old_law"]["spiral"])


if __name__ == "__main__":
    unittest.main()
