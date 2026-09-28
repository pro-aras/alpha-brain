# edit: Claude (Fable 5.1), 2026-09-24 18:58 +0400 — A0's (0b) toy (B1-PREREG.md §5.5: "plain XOR (4 patterns through the arm's
# own input road) at 100 % for A0–A4"). Through the CELLS the toy is what the machinery can do with four patterns:
# each births a cell under its XOR name, and the arm names every pattern right on a fresh rendering of it (the
# jittered twin rows) — 4/4; the negative control: a FIFTH pattern no cell was born on reads UNKNOWN / RESEMBLES,
# never a sure NAME (the refusal U2 grades). Synthetic cache, no rendering; runs under the interpreter §3.0 gives A0.
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.arms.cells.a0 import A0Arm
from brain.glance_cache import CacheWriter, FEATURES_PER_GLANCE, GLANCES_PER_ROW
from brain.protocol import AnswerKind, make_arm, make_row, op_row

TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
PATS = [(0, 0), (0, 1), (1, 0), (1, 1)]
XOR_NAME = {(0, 0): "a", (0, 1): "b", (1, 0): "b", (1, 1): "a"}


def _feat(a: int, b: int, jitter: float, rng: np.random.Generator) -> np.ndarray:
    """Four patterns well apart through the tower's own feature space: a block of 28 dims per pattern (the 112 tower
    dims split four ways), the colour block zero (a grey canvas — §2.5), plus a small seeded jitter."""
    f = np.zeros((GLANCES_PER_ROW, FEATURES_PER_GLANCE))
    block = 2 * a + b
    f[:, block * 28:(block + 1) * 28] = 1.0
    f[:, :112] += jitter * rng.standard_normal((GLANCES_PER_ROW, 112))
    f[:, :112] = np.clip(f[:, :112], 0.0, None)
    # the tower block of a REAL glance is a UNIT vector (the gaze's `unit` retina, §2.5) — the cells' recall reads
    # dot products as cosines; an un-normalised toy read «cos 28» and «noedge» on every pattern (found the hard way)
    f[:, :112] /= np.linalg.norm(f[:, :112], axis=1, keepdims=True)
    return f


class TestA0Xor(unittest.TestCase):
    def setUp(self) -> None:
        TMP.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(dir=str(TMP), prefix="a0xor-")
        self.cache = Path(self._tmp.name) / "cache"
        rng = np.random.default_rng(5)
        w = CacheWriter(self.cache)
        for rep in range(3):                     # rows 0-3 teach, 4-7 ask (fresh renderings), 8-11 spare
            for i, (a, b) in enumerate(PATS):
                w.add(item_id=f"p{rep}{i}", script="latin-lower", char=XOR_NAME[(a, b)], font="f", variant="b", seed=1,
                      canvas_png_sha256=f"{rep * 4 + i:064x}", feats=_feat(a, b, 0.02, rng))
        novel = np.zeros((GLANCES_PER_ROW, FEATURES_PER_GLANCE)); novel[:, 100:112] = 1.0 / np.sqrt(12.0)   # a fifth shape, unit, in an untouched block
        w.add(item_id="novel", script="greek", char="ξ", font="f", variant="b", seed=1, canvas_png_sha256=f"{99:064x}", feats=novel)
        w.finalize(seed=1, genome_sha="g", organ_pins={}, interpreter={}, library_versions={})

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_four_patterns_named_right_and_a_fifth_refused(self) -> None:
        arm = make_arm(A0Arm, 1, {"cache_dir": str(self.cache), "run_dir": self._tmp.name, "seed": 1, "interpreter": "x"})
        seq = 0
        # B1-CELLS.genome: `STAGE 1 senses moments 0..200 / STAGE 2 meet moments 200..` — sight→word EDGES form only
        # from moment 200 (found the hard way: 12 teach rows = 60 moments read «noedge» on every pattern with the cells
        # born and cos 0.999). 20 rounds × 4 rows × 5 glances = 400 moments: half of them under MEET.
        for rnd in range(20):
            for i, pat in enumerate(PATS):
                seq += 1
                arm.fit_event(make_row(seq, "TEACH", "L1", XOR_NAME[pat], {"glance_row": (i if rnd % 2 == 0 else 8 + i), "name": XOR_NAME[pat]}))
        right, kinds = 0, []
        for i, pat in enumerate(PATS):
            ask = make_row(100 + i, "ASK", "T_L", "x", {"cues": ["NAME"], "operands": [op_row(4 + i)], "candidate_rows": None, "answer_kind": "NAME"})
            a = arm.answer(ask, learn=False)
            kinds.append((pat, a.kind, a.value))
            right += int(a.kind == AnswerKind.NAME and a.value == XOR_NAME[pat])
        self.assertEqual(right, 4, kinds)
        novel = arm.answer(make_row(200, "ASK", "T_L", "n", {"cues": ["NAME"], "operands": [op_row(12)], "candidate_rows": None, "answer_kind": "NAME"}), learn=False)
        self.assertIn(novel.kind, (AnswerKind.UNKNOWN, AnswerKind.RESEMBLES), novel)


if __name__ == "__main__":
    unittest.main()
