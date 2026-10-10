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
                                    build_tape, build_twin_tape, drive, genome_text, hearsay_after, twin_texts)


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


# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 08:20 +0400 — PREREG-CONTEMPLATE-1 AMENDMENT 1
# (docs/brain/muse/PREREG-CONTEMPLATE-1-AMENDMENT-1.md, SIGNED 306c143): the NULL re-scoped to where
# content-addressing lives (the fruit, never the word-level trigger). Test-first (RED on 306c143:
# alpha_qid / build_twin_tape / fruit_by_bag / drive_twin do not exist).
class TestAmendment1Instruments(unittest.TestCase):
    def test_alpha_qid_follows_the_word_order(self) -> None:
        """The parent's answered qid is alpha's STEP in the chain — the heard order's own position
        (anchors are the heard words in order; the what-is want files per step)."""
        self.assertEqual(B.alpha_qid(PLANTED), "q-2")
        self.assertEqual(B.alpha_qid("alpha you are"), "q-0")
        self.assertEqual(B.alpha_qid("are alpha you"), "q-1")
        for t in twin_texts():
            self.assertEqual(B.alpha_qid(t), f"q-{t.split().index('alpha')}")

    def test_twin_tape_carries_the_twin_then_the_planted_reask(self) -> None:
        r1 = Path(tempfile.mkdtemp())
        try:
            build_twin_tape(r1, B._Clock(), "are you alpha")
            rows = B._rows(r1)
            chats = [r for r in rows if r["sense"] == "chat"]
            self.assertEqual(len(chats), 2, "one twin chat + the planted re-ask, nothing else")
            words = [(r.get("meta") or {}).get("words") for r in chats]
            self.assertEqual(words[0], ["are", "you", "alpha"], "the twin first (its own fresh budget)")
            self.assertEqual(words[1], PLANTED.split(), "the planted re-ask after the consolidation pass")
            lex = [r for r in rows if (r.get("meta") or {}).get("source") == "lexicon"]
            self.assertGreater(len(lex), 0, "the parent's answer rows are on the tape")
            moments = {str((r.get("meta") or {}).get("moment")) for r in lex}
            self.assertEqual(len(moments), 1, "one answer moment")
            d1 = sorted((r1 / "tape").glob("*.jsonl"))
            r2 = Path(tempfile.mkdtemp())
            build_twin_tape(r2, B._Clock(), "are you alpha")
            self.assertEqual(d1[0].read_bytes(), sorted((r2 / "tape").glob("*.jsonl"))[0].read_bytes(),
                             "the twin tape is deterministic")
            shutil.rmtree(r2, ignore_errors=True)
        finally:
            shutil.rmtree(r1, ignore_errors=True)

    def test_the_bag_control_mirrors_the_fruit_but_keys_by_the_sorted_bag(self) -> None:
        """The control must answer EXACTLY where the content-addressed lookup abstains, with the same
        candidacy resolution — and stay silent on an unpromoted chain (it is a fair twin, not a toy)."""
        considered = {8: {"line": 8, "word": "you", "current": "candidacy"},
                      9: {"line": 9, "word": "are", "current": "candidacy"},
                      10: {"line": 10, "word": "alpha", "current": "candidacy"},
                      5: {"line": 5, "word": "you", "current": "superseded"}}
        chains = {"bbbb": {"heard": ["are", "you", "alpha"], "promoted": [[5, 8], [6, 9], [7, 10]]},
                  "cccc": {"heard": ["circle", "square"], "promoted": [[1, 2]]}}
        got = B.fruit_by_bag(chains, considered, PLANTED.split(), 6)
        self.assertIsNotNone(got, "the bag control MUST answer (the instrument sees bag-addressing)")
        self.assertEqual(got["chain"], "bbbb", "the twin chain shares the planted bag")
        self.assertEqual(got["answer"], ["you", "are", "alpha"])
        self.assertEqual(got["trace"], [["you", 5, 8], ["are", 6, 9], ["alpha", 7, 10]],
                         "the trace form is the fruit's own")
        chains2 = {"bbbb": {"heard": ["are", "you", "alpha"], "promoted": []}}
        self.assertIsNone(B.fruit_by_bag(chains2, considered, PLANTED.split(), 6),
                          "the control never answers on tentative content (the fruit's own quarantine)")
        self.assertIsNone(B.fruit_by_bag(chains, considered, ["zzz"], 6),
                          "a different bag answers nothing")


class TestAmendment1OneTwinArm(unittest.TestCase):
    def test_one_fresh_budget_twin_arm_end_to_end(self) -> None:
        """One twin in its OWN 25-sentence window: fires lawfully (self), its content id != the planted
        id, promoted after the parent's answer + the SLEEP pass, the planted re-ask NEVER answered, and
        the bag-keyed control answers — the amendment's three facts at unit scale."""
        tape_root = Path(tempfile.mkdtemp())
        work = Path(tempfile.mkdtemp()) / "run"
        try:
            twin = "are you alpha"
            build_twin_tape(tape_root, B._Clock(), twin)
            rec = B.drive_twin(tape_root, work, twin)
            print(f"[amend1-unit] twin {twin!r} fired {rec['fired']} classes {rec['classes']} "
                  f"id {rec['chain_id']} planted {B.MUSE.seed_of(PLANTED.split())} "
                  f"reask {rec['planted_reask']} bag {rec['bag_answer'] and rec['bag_answer']['answer']}")
            self.assertTrue(rec["fired"], "a self-carrying twin fires lawfully (the word-level classes)")
            self.assertEqual(rec["classes"], ["self"])
            self.assertNotEqual(rec["chain_id"], B.MUSE.seed_of(PLANTED.split()),
                                "order destroyed -> another address")
            self.assertTrue(rec["promoted"], "the twin chain promoted (answered question + the pass)")
            self.assertIsNone(rec["planted_reask"], "no twin chain's content ever answers the planted re-ask")
            self.assertIsNotNone(rec["bag_answer"], "the bag-keyed control MUST answer")
            self.assertGreaterEqual(len(rec["budget_skips"]), 1,
                                    "the planted re-ask's lawful budget suppression is journaled")
        finally:
            shutil.rmtree(tape_root, ignore_errors=True)
            shutil.rmtree(work.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
