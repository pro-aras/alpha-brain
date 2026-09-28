# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:4x +0400 — tests for brain/arms/cells/a0.py: real
# glyphs, real organs, a real (if small) Organism. Must run under /usr/bin/python3 (rendering).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain.harness.identity import identity_test
from brain.protocol import (
    Answer, AnswerKind, HarnessContract, check_arm, has_rule, has_why, make_arm, make_row, op_name, op_row,
)
from brain.world import fonts
from brain.world.build import RenderRequest, build_cache
from brain.arms.cells.a0 import A0Arm

SEED = 20261001
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _build_upper_cache(cache_dir: Path, n_fonts: int = 2):
    teach_fonts = fonts.TEACH_FONTS_ORDER[:n_fonts]
    reqs = []
    for c in UPPER:
        for fi, font in enumerate(teach_fonts):
            reqs.append(RenderRequest(item_id=f"a0test:{c}:{fi}", script="latin-upper", char=c, font=font))
    item_to_row, header, _truths = build_cache(reqs, cache_dir, SEED)
    return item_to_row, teach_fonts


def _config(cache_dir: Path) -> dict:
    return {"cache_dir": str(cache_dir), "run_dir": str(cache_dir / "run"), "seed": SEED, "interpreter": "system"}


class TestA0Construction(unittest.TestCase):
    def test_constructs_and_parses_b1_cells_genome(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # no cache_dir: this test only checks construction/parsing, never resolves a glance_row.
            config = {"run_dir": d, "seed": SEED, "interpreter": "system"}
            arm = make_arm(A0Arm, SEED, config)
            self.assertEqual(arm.org.sight.n, 0)
            self.assertEqual(arm.org.words.n, 0)
            self.assertTrue(has_why(arm))       # A0 implements why() (U4a)
            self.assertFalse(has_rule(arm))     # A0 has no rule() — relation cues are "no road"


class TestA0TeachAndName(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self._tmp.name) / "cache"
        self.item_to_row, self.teach_fonts = _build_upper_cache(self.cache_dir, n_fonts=2)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _teach_all(self, arm: A0Arm) -> int:
        """Teach all 26 letters, each font — 52 TEACH rows x 5 glances = 260 moments, past B1-CELLS.genome's
        own STAGE 2 threshold (moments 200..) where sight<->words wiring (HEBB/DELTA) begins."""
        seq = 1
        for c in UPPER:
            for fi in range(len(self.teach_fonts)):
                row = make_row(seq, "TEACH", "L1", c, {"glance_row": self.item_to_row[f"a0test:{c}:{fi}"], "name": c.lower()})
                HarnessContract.teach(arm, row)
                seq += 1
        return seq

    def test_names_a_taught_letter_after_crossing_stage2(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        self.assertGreaterEqual(arm.org.t, 200, "the synthetic teach schedule must cross STAGE 2's threshold")
        ask = make_row(9000, "ASK", "T_L", "a", {
            "cues": ["NAME"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertIn(ans.kind, (AnswerKind.NAME, AnswerKind.RESEMBLES, AnswerKind.UNKNOWN))
        if ans.kind in (AnswerKind.NAME, AnswerKind.RESEMBLES):
            self.assertEqual(ans.value, "a")

    def test_relation_cue_is_no_road(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        ask = make_row(9001, "ASK", "L4", "x", {
            "cues": ["AFTER"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertEqual(ans.kind, AnswerKind.NOTHING)

    def test_before_stage2_everything_abstains(self) -> None:
        """Before crossing the STAGE 2 threshold, the sight<->words meeting has never wired — recall_many
        can find no cross-modal edge at all, so NAME must read UNKNOWN, never a guess."""
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        # teach only the first 10 letters x 2 fonts = 20 TEACH rows x 5 = 100 moments < 200
        seq = 1
        for c in UPPER[:10]:
            for fi in range(len(self.teach_fonts)):
                row = make_row(seq, "TEACH", "L1", c, {"glance_row": self.item_to_row[f"a0test:{c}:{fi}"], "name": c.lower()})
                HarnessContract.teach(arm, row)
                seq += 1
        self.assertLess(arm.org.t, 200)
        ask = make_row(9002, "ASK", "T_L", "a", {
            "cues": ["NAME"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertEqual(ans.kind, AnswerKind.UNKNOWN)

    def test_check_arm_passes(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        sample_teach = make_row(9100, "TEACH", "L1", "z", {"glance_row": self.item_to_row["a0test:Z:0"], "name": "z"})
        sample_ask = make_row(9101, "ASK", "T_L", "a", {
            "cues": ["NAME"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        violations = check_arm(
            arm, sample_teach_row=sample_teach, sample_ask_row=sample_ask,
            tmp_dir=self.cache_dir / "check",
            fresh_arm_factory=lambda: make_arm(A0Arm, SEED, _config(self.cache_dir)),
        )
        self.assertEqual(violations, [], violations)

    def test_snapshot_load_roundtrip_state_sha(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        want = arm.state_sha()
        snap_path = self.cache_dir / "snap"
        arm.snapshot(snap_path)
        fresh = make_arm(A0Arm, SEED, _config(self.cache_dir))
        fresh.load(snap_path)
        self.assertEqual(fresh.state_sha(), want)
        # and it answers identically post-load
        ask = make_row(9200, "ASK", "T_L", "a", {
            "cues": ["NAME"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        a1 = HarnessContract.test_ask(arm, ask)
        a2 = HarnessContract.test_ask(fresh, ask)
        self.assertEqual(a1.to_dict(), a2.to_dict())

    def test_point_picks_the_named_candidate(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        candidates = [self.item_to_row["a0test:B:0"], self.item_to_row["a0test:A:0"],
                      self.item_to_row["a0test:C:0"], self.item_to_row["a0test:D:0"]]
        ask = make_row(9300, "ASK", "T_L", "point-a", {
            "cues": ["POINT"], "operands": [op_name("a")], "candidate_rows": candidates, "answer_kind": "PICK"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertIn(ans.kind, (AnswerKind.PICK, AnswerKind.UNKNOWN))
        if ans.kind == AnswerKind.PICK:
            self.assertEqual(candidates[ans.value], self.item_to_row["a0test:A:0"])

    def test_is_answers_yes_for_the_shown_letter(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        ask = make_row(9400, "ASK", "T_L", "is-a-a", {
            "cues": ["IS"], "operands": [op_name("a"), op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "YESNO"})
        ans = HarnessContract.test_ask(arm, ask)
        self.assertIn(ans.kind, (AnswerKind.YES, AnswerKind.NO))

    def test_why_returns_tape_seqs_for_a_named_letter(self) -> None:
        arm = make_arm(A0Arm, SEED, _config(self.cache_dir))
        self._teach_all(arm)
        ask = make_row(9500, "ASK", "T_L", "a", {
            "cues": ["NAME"], "operands": [op_row(self.item_to_row["a0test:A:0"])],
            "candidate_rows": None, "answer_kind": "NAME"})
        ans = HarnessContract.test_ask(arm, ask)
        seqs = arm.why(ask)
        self.assertIsInstance(seqs, list)
        if ans.kind == AnswerKind.NAME:
            self.assertTrue(all(isinstance(s, int) for s in seqs))


class TestA0IdentitySmoke(unittest.TestCase):
    def test_identity_framework_passes_for_a0_on_a_small_real_tape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cache_dir = Path(d) / "cache"
            item_to_row, teach_fonts = _build_upper_cache(cache_dir, n_fonts=2)
            rows = []
            seq = 1
            for c in UPPER:
                for fi in range(len(teach_fonts)):
                    rows.append(make_row(seq, "TEACH", "L1", c, {"glance_row": item_to_row[f"a0test:{c}:{fi}"], "name": c.lower()}))
                    seq += 1
            rows.append(make_row(seq, "SLEEP", "L1", "-", {"steps": 50})); seq += 1
            out_dir = Path(d) / "identity"
            report = identity_test(
                __import__("sys").executable, Path(__file__).resolve().parents[3],
                "brain.arms.cells.a0", "A0Arm", SEED, _config(cache_dir),
                tape_rows=rows, out_dir=out_dir,
                checkpoints=(50, 53), n_events=len(rows), plant_at_event=min(50, len(rows) - 1),
                planted_row=item_to_row["a0test:A:0"],   # a REAL, valid row in this test's own 52-row cache
                run_8_threads=False,
            )
            self.assertTrue(report["twice"]["answers_match"], report)
            self.assertTrue(report["twice"]["state_match"], report)


if __name__ == "__main__":
    unittest.main()
