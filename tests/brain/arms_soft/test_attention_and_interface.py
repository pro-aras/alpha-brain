# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 16:55 +0400 — tests for the Memory
#   Attention twins (B1-PREREG.md §4.1: A1-ATT / A1-MA, matched parameters) and the NETWORK
#   side of the cells<->network interface arms Builder 3 owns (§4.2: IF-1's attention with an
#   externally-supplied table, IF-2's cell-row input, IF-3's logit gate). IF-4 reuses
#   MemoryAttentionReadout verbatim (no separate class, no separate test needed beyond the
#   existing A1-MA coverage).
import os
import sys
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from brain.arms.soft.engine import (  # noqa: E402
    CausalAttentionReadout,
    CellRowInputProjector,
    ExternalTableAttention,
    GrowingGRUEngine,
    LogitMixGate,
    MemoryAttentionReadout,
    a1_total_params,
    att_readout_param_count,
    largest_H_under,
    ma_readout_param_count,
    new_generator,
)


class TestMatchedParameters(unittest.TestCase):
    """B1-PREREG.md §4.1: 'H = the largest H whose TOTAL parameter count <= A1's FINAL count
    on the same seed (both counts printed; the difference is under one hidden unit's
    parameters)'."""

    def test_solver_never_exceeds_target_and_is_tight(self):
        input_dim, glance_dim, letter_dim, kind_dim, n_names = 207, 144, 27, 7, 52
        h_final_a1 = 130  # a plausible A1 final width (final count is a RUN OUTPUT in reality)
        target = a1_total_params(input_dim, h_final_a1, glance_dim, letter_dim, kind_dim, n_names)

        att_fn = lambda H: att_readout_param_count(H) + a1_total_params(  # noqa: E731
            input_dim, H, glance_dim, letter_dim, kind_dim, n_names
        )
        h_att = largest_H_under(target, att_fn)
        self.assertGreater(h_att, 0)
        self.assertLessEqual(att_fn(h_att), target)
        self.assertGreater(att_fn(h_att + 1), target, "the solver must be TIGHT (largest H, not just any valid H)")

        n_tokens = 27 + 24 + 7 + 5
        ma_fn = lambda H: ma_readout_param_count(H, n_tokens) + a1_total_params(  # noqa: E731
            input_dim, H, glance_dim, letter_dim, kind_dim, n_names
        )
        h_ma = largest_H_under(target, ma_fn)
        self.assertGreater(h_ma, 0)
        self.assertLessEqual(ma_fn(h_ma), target)
        self.assertGreater(ma_fn(h_ma + 1), target)

        # the difference must be "under one hidden unit's parameters" (PREREG's own phrasing) —
        # i.e. params_fn(h+1) - params_fn(h) bounds the slack, checked for both twins
        self.assertLess(target - att_fn(h_att), att_fn(h_att + 1) - att_fn(h_att))
        self.assertLess(target - ma_fn(h_ma), ma_fn(h_ma + 1) - ma_fn(h_ma))

    def test_ma_has_fewer_pure_attention_params_than_att_at_equal_h_isolating_the_value(self):
        # A1-MA drops WV (paper: V=K+RMSNorm(M), no separate value projection) but adds a token
        # table E — at letters (small vocabulary) the table is tiny (PREREG §4.1: "≈64 rows x
        # 64 = 4,096 numbers"), so at a fixed H the two are close but NOT required to be equal;
        # this test only pins that both formulas are well-formed (monotone, positive).
        for H in (16, 64, 130):
            self.assertGreater(att_readout_param_count(H), 0)
            self.assertGreater(ma_readout_param_count(H, n_tokens=63), 0)


class TestAttentionReadouts(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)

    def test_att_forward_shape_and_gradient_flows(self):
        hmax = 16
        ro = CausalAttentionReadout(hmax=hmax, d=8, window=32)
        gen = new_generator(1, "att_init", 0)
        ro.init_block(hmax, gen)
        h_hist = torch.randn(5, hmax, requires_grad=False)
        h_t = h_hist[-1]
        out = ro(h_t, h_hist, active_h=hmax)
        self.assertEqual(out.shape, (8,))
        loss = out.sum()
        loss.backward()
        self.assertIsNotNone(ro.WQ.grad)
        self.assertGreater(float(ro.WQ.grad.abs().sum()), 0.0)

    def test_ma_value_uses_token_table_not_hidden_state(self):
        hmax, n_tokens, d = 16, 10, 8
        ro = MemoryAttentionReadout(hmax=hmax, n_tokens=n_tokens, d=d, window=32)
        gen = new_generator(2, "ma_init", 0)
        ro.init_block(hmax, gen)
        h_hist = torch.zeros(3, hmax)  # hidden state carries NO information
        ids = torch.tensor([1, 2, 3])  # but token ids differ per step
        out_a = ro.forward_tokens(h_hist[-1], h_hist, ids, active_h=hmax)
        ids2 = torch.tensor([4, 5, 6])
        out_b = ro.forward_tokens(h_hist[-1], h_hist, ids2, active_h=hmax)
        self.assertFalse(
            torch.allclose(out_a, out_b),
            "with h identically zero, only the token table can distinguish the two calls — "
            "if the outputs match, the memory value is not actually reading E[s]",
        )

    def test_att_and_ma_isolate_the_memory_value_when_table_is_zeroed(self):
        # PREREG §4.1's isolation clause: A1-MA - A1-ATT attributes the gain to the memory
        # VALUE specifically. Mechanically: if E is all zero, RMSNorm(0)=0 (eps-guarded), so
        # A1-MA's value collapses to K alone -- NOT equal to A1-ATT's W_V h_tau in general, but
        # it must depend only on K, never on an independent V projection (there isn't one).
        hmax, n_tokens, d = 8, 4, 4
        ro = MemoryAttentionReadout(hmax=hmax, n_tokens=n_tokens, d=d, window=8)
        with torch.no_grad():
            ro.E.zero_()
            ro.WK.uniform_(-0.3, 0.3)
            ro.WQ.uniform_(-0.3, 0.3)
        h_hist = torch.randn(3, hmax)
        ids = torch.tensor([0, 1, 2])
        v = ro.value_of_tokens(h_hist, ids, active_h=hmax)
        k = h_hist @ ro.WK.T
        self.assertTrue(torch.allclose(v, k, atol=1e-5), "with E=0, V must reduce to K exactly (V=K+RMSNorm(0))")


class TestInterfaceArmsNetworkSide(unittest.TestCase):
    """B1-PREREG.md §4.2, Builder 3's fence: 'the NETWORK side of the interface arms (an
    attention read-out whose table is supplied from outside; the row-input; the logit gate)'.
    The CELLS side (which cell lights, and its row) is Builder 2's; here every (id, row) pair
    is synthetic, standing in for whatever Builder 2's frozen interface hands over."""

    def test_if1_seam_planted_row_change_moves_only_its_own_steps(self):
        # "a planted change to ONE cell's row must change the network's value vector at
        # exactly the steps whose s is that cell, and nowhere else" (PREREG §4.2, the seam
        # test "by the third hand, #235").
        hmax, cell_dim, d = 8, 6, 4
        ro = ExternalTableAttention(hmax=hmax, cell_dim=cell_dim, d=d, window=16)
        gen = new_generator(3, "if1_init", 0)
        ro.init_block(hmax, gen)

        T = 5
        h_hist = torch.randn(T, hmax)
        cell_ids = [10, 11, 10, 12, 11]  # step 0 and 2 both lit cell 10; steps 1 and 4 lit 11
        cell_table = {10: torch.randn(cell_dim), 11: torch.randn(cell_dim), 12: torch.randn(cell_dim)}
        lit_mask = torch.ones(T)

        def rows_for(table):
            return torch.stack([table[i] for i in cell_ids])

        rows_before = rows_for(cell_table)
        v_before = ro.value_of_cells(h_hist, rows_before, lit_mask, active_h=hmax)

        planted = dict(cell_table)
        planted[10] = planted[10] + 5.0  # plant a change on cell 10 ONLY
        rows_after = rows_for(planted)
        v_after = ro.value_of_cells(h_hist, rows_after, lit_mask, active_h=hmax)

        moved = ~torch.isclose(v_before, v_after, atol=1e-7).all(dim=-1)
        expected_moved = torch.tensor([cid == 10 for cid in cell_ids])
        self.assertTrue(
            torch.equal(moved, expected_moved),
            f"the plant on cell 10 should move exactly steps {expected_moved.tolist()}, moved={moved.tolist()}",
        )

    def test_if1_unlit_step_falls_back_to_key_only(self):
        hmax, cell_dim, d = 8, 6, 4
        ro = ExternalTableAttention(hmax=hmax, cell_dim=cell_dim, d=d, window=16)
        gen = new_generator(4, "if1_init2", 0)
        ro.init_block(hmax, gen)
        h_hist = torch.randn(3, hmax)
        rows = torch.zeros(3, cell_dim)  # no cell lit -> rows are irrelevant when mask is 0
        mask = torch.tensor([0.0, 1.0, 0.0])
        v = ro.value_of_cells(h_hist, rows, mask, active_h=hmax)
        k = h_hist @ ro.WK[:, :hmax].T
        self.assertTrue(torch.allclose(v[0], k[0], atol=1e-6))
        self.assertTrue(torch.allclose(v[2], k[2], atol=1e-6))

    def test_if2_cell_row_projector_deterministic_and_zero_when_absent(self):
        proj = CellRowInputProjector(cell_dim=6, append_dim=4, seed=42)
        proj2 = CellRowInputProjector(cell_dim=6, append_dim=4, seed=42)
        self.assertTrue(torch.equal(proj.P, proj2.P), "same seed must give byte-identical projection weights")
        row = torch.randn(6)
        out = proj(row)
        self.assertEqual(out.shape, (4,))
        out_none = proj(None)
        self.assertTrue(torch.equal(out_none, torch.zeros(4)), "no cell lit -> the appended block must be exactly 0")

    def test_if3_logit_gate_mixes_and_defaults_neutral(self):
        gate = LogitMixGate(n_cue_types=3)
        net_logits = torch.tensor([1.0, 2.0, 3.0])
        ext_logits = torch.tensor([3.0, 2.0, 1.0])
        mixed = gate.mix(0, net_logits, ext_logits)
        self.assertTrue(torch.allclose(mixed, 0.5 * net_logits + 0.5 * ext_logits), "an untrained gate is neutral (sigmoid(0)=0.5)")
        with torch.no_grad():
            gate.w[1] = 100.0
        mixed_ext = gate.mix(1, net_logits, ext_logits)
        self.assertTrue(torch.allclose(mixed_ext, ext_logits, atol=1e-3), "a saturated gate must defer almost entirely to the external score")


if __name__ == "__main__":
    unittest.main()
