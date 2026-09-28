# edit: Claude (Opus 5.5), 2026-09-26 12:00 +0400 — PREREG §4.1's matched-parameter twins (A1-ATT, A1-MA). Found at the
# solo probe on 09-26: the runner gave each twin A1's final WIDTH, so it carried its readout and its 64-wider answer heads on
# top of A1's count (+60 % at H 20), and its size() reported A1's formula, hiding the difference. These tests pin
# (1) the count formula against the modules' OWN tensors, (2) that MA never trains the WV its parent allocates,
# (3) the solve, and (4) the seam: the runner's config_from keys reach the arm, and the OLD wiring exceeds A1's count.
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.soft.arm import ArmA1  # noqa: E402
from brain.arms.soft.engine import a1_total_params, twin_total_params  # noqa: E402
from brain.arms.soft.steps import GLANCE_DIM, KIND_DIM, LETTER_DIM, STEP_DIM  # noqa: E402
from brain.harness import run as R  # noqa: E402
from brain.protocol import make_row  # noqa: E402
from tests.brain.arms_soft.test_arm_a1_conformance import _build_synthetic_cache  # noqa: E402

D = 64
TOK = 63


def used_params(arm: ArmA1) -> int:
    """The parameters the arm USES, read from its own tensors: every engine/world/pick/yes-no tensor whole (fixed width),
    the names head's ACTIVE rows only (its out_cap rows beyond the names heard are unused), and the readout — ATT: WQ, WK,
    WV; MA: WQ, WK, E, gain (its value path is K + RMSNorm(E[s]); WV is never read — test 2)."""
    n = sum(p.numel() for m in (arm.engine, arm.world, arm.pick, arm.yesno) for p in m.parameters())
    k = arm.names.n_out
    n += k * arm.names.W.shape[1] + k
    ro = arm.readout
    n += ro.WQ.numel() + ro.WK.numel()
    if arm.variant == "A1-ATT":
        n += ro.WV.numel()
    else:
        n += ro.E.numel() + ro.gain.numel()
    return n


class TestTwinParams(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.tmp = tempfile.mkdtemp(prefix="b1_twin_params_", dir="/data/dev/brain-runs/tmp")
        self.cache_dir, self.rows = _build_synthetic_cache(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _arm(self, variant, **extra):
        cfg = {"cache_dir": self.cache_dir, "run_dir": self.tmp, "seed": 42, "interpreter": "venv", "h0": 8, "hmax": 16,
               "variant": variant, "att_d": D}
        if variant == "A1-MA":
            cfg["ma_n_tokens"] = TOK
        cfg.update(extra)
        return ArmA1(seed=42, config=cfg)

    def _hear(self, arm, names):
        for i, nm in enumerate(names):
            arm.fit_event(make_row(i + 1, "TEACH", "L1", f"{nm}-{i}", {"glance_row": self.rows[nm][0], "name": nm}), valence=None)

    def test_1_formula_equals_the_modules_own_tensors(self):
        for variant in ("A1-ATT", "A1-MA"):
            for H in (8, 20, 33):
                for heard in ((), ("a", "b")):
                    arm = self._arm(variant, fixed_h=H)
                    self._hear(arm, heard)
                    n_names = len(arm.names.names)
                    want = twin_total_params(variant, STEP_DIM, H, GLANCE_DIM, LETTER_DIM, KIND_DIM, n_names, D,
                                             TOK if variant == "A1-MA" else 0)
                    self.assertEqual(used_params(arm), want, f"{variant} H={H} names={n_names}")
                    self.assertEqual(arm.size()["n_params_active"], want, f"{variant} size() must report its OWN count")

    def test_2_ma_output_never_reads_wv(self):
        """Functional, not a training check (a first form that trained 4 names + a sleep moved NO readout tensor at all, so
        «WV unchanged» proved nothing): the arm calls `forward_tokens` for MA (arm.py, both call sites); perturbing WV must
        leave its output unchanged, and the control — perturbing WK — must change it."""
        arm = self._arm("A1-MA", fixed_h=20)
        ro = arm.readout
        g = torch.Generator().manual_seed(7)
        ro.init_block(20, g)
        h_hist = torch.randn(5, 20, generator=g)
        ids = torch.tensor([1, 5, 9, 2, 0])
        base = ro.forward_tokens(h_hist[-1], h_hist, ids, active_h=20).detach().clone()
        with torch.no_grad():
            ro.WV.add_(torch.randn(ro.WV.shape, generator=g))
        self.assertTrue(torch.equal(ro.forward_tokens(h_hist[-1], h_hist, ids, active_h=20).detach(), base), "MA reads WV — count it")
        with torch.no_grad():
            ro.WK.add_(torch.randn(ro.WK.shape, generator=g))
        self.assertFalse(torch.allclose(ro.forward_tokens(h_hist[-1], h_hist, ids, active_h=20).detach(), base),
                         "control: MA must read WK")

    def test_3_the_solve_is_the_largest_width_under_a1s_count(self):
        target = a1_total_params(STEP_DIM, 64, GLANCE_DIM, LETTER_DIM, KIND_DIM, 36)
        for variant in ("A1-ATT", "A1-MA"):
            arm = self._arm(variant, match_params=target, match_n_names=36)
            m = arm.size()["match"]
            self.assertLessEqual(m["twin_params_at_solved_h"], target)
            self.assertGreater(m["twin_params_at_h_plus_1"], target)
            self.assertEqual((arm.engine.hmax, arm.engine.active), (m["solved_h"], m["solved_h"]))
            self.assertLess(m["solved_h"], 64, "a twin at A1's own width exceeds A1's count")

    def test_4_the_runner_seam_and_the_old_wiring_as_control(self):
        out_root = Path(self.tmp) / "run"
        (out_root / "A1").mkdir(parents=True)
        a1_h, a1_names = 64, 36
        target = a1_total_params(STEP_DIM, a1_h, GLANCE_DIM, LETTER_DIM, KIND_DIM, a1_names)
        (out_root / "A1" / "summary.json").write_text(json.dumps(
            {"final_h": a1_h, "size": {"h_alive": a1_h, "n_names": a1_names, "n_params_active": target}}))
        for variant in ("A1-ATT", "A1-MA"):
            spec = R.spec_for(variant)
            R._resolve_config_from(spec, out_root)
            self.assertEqual((spec.config.get("match_params"), spec.config.get("match_n_names")), (target, a1_names))
            self.assertNotIn("fixed_h", spec.config)
            cfg = {"cache_dir": self.cache_dir, "run_dir": self.tmp, "seed": 42, "interpreter": "venv", **spec.config}
            arm = ArmA1(seed=42, config=cfg)
            self.assertLessEqual(arm.size()["match"]["twin_params_at_solved_h"], target)
            # the control: the pre-fix wiring gave the twin A1's WIDTH — its count at 64 with A1's names exceeds A1's count
            old = twin_total_params(variant, STEP_DIM, a1_h, GLANCE_DIM, LETTER_DIM, KIND_DIM, a1_names, D,
                                    TOK if variant == "A1-MA" else 0)
            self.assertGreater(old, target)


if __name__ == "__main__":
    unittest.main()
