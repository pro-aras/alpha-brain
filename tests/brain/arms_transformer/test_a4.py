# edit: Claude (Fable 5.1), 2026-09-24 18:50 +0400 — A4's own tests: the parameter formula equals numel; the size match lands
# within 10 % across A1's range; check_arm conformance (with the snapshot round-trip) on a synthetic cache; the
# XOR toy through the arm's OWN input road (§5.5 (0b): 4 patterns, 100 % after the offline epochs, and the
# untrained arm as the control that could have read low); determinism (two seeds-alike arms → one state_sha).
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import torch  # noqa: E402

from brain.arms.transformer import a4 as A4  # noqa: E402
from brain.glance_cache import CacheWriter, FEATURES_PER_GLANCE, GLANCES_PER_ROW  # noqa: E402
from brain.protocol import AnswerKind, check_arm, make_arm, make_row, op_row  # noqa: E402

torch.set_num_threads(1)
TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))


def _xor_cache(d: Path) -> None:
    """Four rows: glance 0's first two features carry the bits (the rest zero) — the XOR pattern through the
    arm's own glance road; rows 4..7 repeat the four with a tiny jitter so a test ask is not a memorised row."""
    w = CacheWriter(d)
    pats = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for rep in range(2):
        for i, (a, b) in enumerate(pats):
            f = np.zeros((GLANCES_PER_ROW, FEATURES_PER_GLANCE))
            f[:, 0] = a + (0.01 * rep); f[:, 1] = b + (0.01 * rep)
            w.add(item_id=f"x{rep}{i}", script="latin-lower", char="ab"[a ^ b], font="f", variant="b", seed=1, canvas_png_sha256=f"{rep * 4 + i:064x}", feats=f)
    w.finalize(seed=1, genome_sha="g", organ_pins={}, interpreter={}, library_versions={})


XOR_NAME = {(0, 0): "a", (0, 1): "b", (1, 0): "b", (1, 1): "a"}


def _xor_rows(rounds: int, seed: int = 3):
    """The four patterns, each round in a SEEDED order — a fixed cycle would let a sequence model answer from
    the previous feedback (the next pattern in the cycle) instead of from the glance bits (found the hard way:
    A4 read 'b' on every pattern under a fixed order while its training loss sat at 0.001)."""
    rows, seq = [], 0
    pats = [(0, 0), (0, 1), (1, 0), (1, 1)]
    rng = np.random.default_rng(seed)
    for r in range(rounds):
        order = [int(i) for i in rng.permutation(4)]
        for i in order:
            pat = pats[i]
            seq += 1
            rows.append(make_row(seq, "ASK", "L4", f"xor{i}", {"cues": ["NAME"], "operands": [op_row(i)], "candidate_rows": None, "answer_kind": "NAME"}))
            seq += 1
            rows.append(make_row(seq, "FEEDBACK", "L4", f"xor{i}", {"ask_seq": seq - 1, "right": XOR_NAME[pat]}))
    return rows


class TestSize(unittest.TestCase):
    def test_formula_equals_numel(self) -> None:
        for d, f in ((128, 256), (128, 16), (64, 40), (8, 16)):
            net = A4.A4Net(d, f)
            self.assertEqual(sum(p.numel() for p in net.parameters()), A4.param_count(d, f), (d, f))

    def test_match_lands_within_ten_percent_across_a1s_range(self) -> None:
        for target in (68_020, 150_000, 400_000, 1_200_000, 3_400_000):
            s = A4.solve_size(target)
            self.assertTrue(s["within_10pct"], s)
            self.assertLessEqual(s["n_params"], int(target * 1.1))
        self.assertEqual(A4.solve_size(None)["d_model"], 128)


class TestArm(unittest.TestCase):
    def setUp(self) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(dir=str(TMP), prefix="a4-")
        self.cache = Path(self._tmp.name) / "cache"
        _xor_cache(self.cache)
        self.cfg = {"cache_dir": str(self.cache), "run_dir": self._tmp.name, "seed": 7, "interpreter": "x", "epochs": 80, "match_params": 68_020}

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _arm(self, seed: int = 7):
        return make_arm(A4.ArmA4, seed, self.cfg)

    def test_conformance_and_snapshot_round_trip(self) -> None:
        arm = self._arm()
        rows = _xor_rows(2)
        for r in rows:
            arm.fit_event(r)
        arm.offline_train(rows)
        teach = make_row(99, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"})
        ask = rows[0]
        v = check_arm(arm, teach, ask, Path(self._tmp.name) / "chk", fresh_arm_factory=lambda: self._arm())
        self.assertEqual(v, [])

    def test_xor_toy_100pct_after_offline_epochs_and_low_before(self) -> None:
        arm = self._arm()
        rows = _xor_rows(16)      # 512 transcript steps: two windows, so the positions a test ask lands on were trained
        for r in rows:
            arm.fit_event(r)
        # the control: untrained → NOTHING (no epochs yet), never a lucky 4/4
        before = [arm.answer(rows[2 * i], learn=False) for i in range(4)]
        self.assertTrue(all(a.kind == AnswerKind.NOTHING for a in before))
        rep = arm.offline_train(rows)
        self.assertEqual(rep["epochs"], 80)
        pats = [(0, 0), (0, 1), (1, 0), (1, 1)]
        right, got = 0, []
        for i, pat in enumerate(pats):
            # the jittered twin rows 4..7: not the memorised training rows
            ask = make_row(500 + i, "ASK", "T_L", f"xor{i}", {"cues": ["NAME"], "operands": [op_row(4 + i)], "candidate_rows": None, "answer_kind": "NAME"})
            a = arm.answer(ask, learn=False)
            got.append((pat, a.kind, a.value, a.raw.get("conf"), (a.raw.get("forced") or {}).get("value")))
            right += int(a.kind == AnswerKind.NAME and a.value == XOR_NAME[pat])
        self.assertEqual(right, 4, f"XOR through A4's own road must read 4/4 after the offline epochs; got {got} (band {arm.band}, p5 {arm.band_p5})")
        self.assertEqual(arm.answer(make_row(600, "ASK", "L5", "p", {"cues": ["TWO_AFTER"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"})).kind, AnswerKind.NOTHING)

    def test_deterministic_and_frozen(self) -> None:
        rows = _xor_rows(3)
        shas = []
        for _ in range(2):
            arm = self._arm()
            for r in rows:
                arm.fit_event(r)
            arm.offline_train(rows)
            s1 = arm.state_sha()
            arm.answer(rows[0], learn=False)
            self.assertEqual(arm.state_sha(), s1)
            shas.append(s1)
        self.assertEqual(shas[0], shas[1])
        self.assertNotEqual(shas[0], self._arm(8).state_sha())


if __name__ == "__main__":
    unittest.main()
