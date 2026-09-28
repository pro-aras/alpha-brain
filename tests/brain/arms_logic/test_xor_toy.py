# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:30 +0400 — A2's required positive
#   control (B1-PREREG.md §5.5 (0b)) plus a negative control that survived an empirical
#   correction: an argmax-over-2-scores classifier can reconstruct XOR from AND and OR alone
#   (OR - AND = a+b-ab-ab = XOR exactly, an algebraic identity, verified by hand and by a
#   scratch run before this file was written), so "excluding XOR/XNOR from a 2-gate,
#   2-group circuit" is NOT a valid negative control for the multi-gate architecture — it
#   reads 100% legitimately. The airtight negative control drops to the SAME single-gate,
#   single-threshold case Minsky & Papert's argument is actually about: with only one gate and
#   one decision threshold (no second learned score to compare against), excluding index 6
#   (XOR) leaves 15 functions each capping at <=0.75 raw agreement with the XOR truth table —
#   empirically confirmed at exactly 0.75 (chosen function: "A AND NOT B", index 2). This
#   correction is recorded here and in docs/briefs/B1-BUILDER3-REPORT.md so nobody re-derives
#   the wrong control by the same shortcut.
import os
import sys
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402

from brain.arms.logic.engine import (  # noqa: E402
    DiffLogicLayer,
    LogicBPTTTrainer,
    RecurrentDiffLogicGateNetwork,
)

XOR_X = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
XOR_Y = torch.tensor([0, 1, 1, 0])


def _train_network(seed: int, iters: int = 1500, lr: float = 0.3):
    torch.manual_seed(seed)
    net = RecurrentDiffLogicGateNetwork(
        n_input_bits=2, n_layers=2, n_gates=4, recurrent_bits=0, n_groups=2, seed=seed
    )
    trainer = LogicBPTTTrainer(net.parameters(), lr=lr, momentum=0.0, clip=10.0)
    rec0 = net.zero_state()
    best_disc = 0.0
    for _ in range(iters):
        loss = torch.zeros(())
        margins = []
        for x, y in zip(XOR_X, XOR_Y):
            groups, _ = net(x, rec0, discretise=False)
            loss = loss + torch.nn.functional.cross_entropy(groups.unsqueeze(0), y.unsqueeze(0))
            margins.append(groups)
        trainer.step(loss / len(XOR_X))
        with torch.no_grad():
            correct = 0
            for x, y in zip(XOR_X, XOR_Y):
                g, _ = net(x, rec0, discretise=True)
                if int(g.argmax()) == int(y):
                    correct += 1
            best_disc = max(best_disc, correct / len(XOR_X))
    return net, best_disc


def _train_single_gate_ceiling(seed: int, mask_xor: bool, iters: int = 1500, lr: float = 0.3) -> float:
    layer = DiffLogicLayer(n_inputs=2, n_gates=1, seed=seed, layer_index=0)
    trainer = LogicBPTTTrainer(layer.parameters(), lr=lr, momentum=0.0, clip=10.0)
    y = XOR_Y.float()
    best = 0.0
    for _ in range(iters):
        out = layer(XOR_X, discretise=False).squeeze(-1)
        loss = torch.nn.functional.binary_cross_entropy(out.clamp(1e-6, 1 - 1e-6), y)
        trainer.opt.zero_grad()
        loss.backward()
        if mask_xor:
            layer.logits.grad[:, 6] = 0.0  # never let gradient move the excluded function's logit
        trainer.opt.step()
        if mask_xor:
            with torch.no_grad():
                layer.logits[:, 6] = -1e9  # and keep it permanently unselectable
        with torch.no_grad():
            out_d = layer(XOR_X, discretise=True).squeeze(-1)
            best = max(best, float((out_d == y).float().mean()))
    return best


class TestA2XorToy(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)

    def test_network_solves_xor_100_percent_discretised(self):
        net, best = _train_network(seed=20261001)
        self.assertEqual(best, 1.0, f"A2's engine must solve XOR at 100%% (discretised), got {best}")

    def test_negative_control_single_gate_without_xor_caps_at_0_75(self):
        for seed in range(3):
            full = _train_single_gate_ceiling(seed, mask_xor=False)
            self.assertEqual(full, 1.0, f"seed {seed}: an unrestricted single gate must find XOR itself (idx 6)")
            capped = _train_single_gate_ceiling(seed, mask_xor=True)
            self.assertLessEqual(capped, 0.75 + 1e-9, f"seed {seed}: excluding XOR must cap accuracy at 0.75")
            self.assertGreaterEqual(capped, 0.75 - 1e-9, f"seed {seed}: the 0.75 ceiling should be reachable")

    def test_determinism_same_seed_same_wiring_and_weights(self):
        net1, _ = _train_network(seed=42, iters=30)
        net2, _ = _train_network(seed=42, iters=30)
        for l1, l2 in zip(net1.layers, net2.layers):
            self.assertTrue(torch.equal(l1.idx_a, l2.idx_a), "same seed must give byte-identical wiring")
            self.assertTrue(torch.equal(l1.idx_b, l2.idx_b))
            self.assertTrue(torch.equal(l1.logits, l2.logits), "same seed must give byte-identical trained logits")

    def test_abstention_margin_mechanism(self):
        net = RecurrentDiffLogicGateNetwork(n_input_bits=2, n_layers=1, n_gates=4, recurrent_bits=0, n_groups=2, seed=1)
        # feed a few confident (high-margin) training examples
        for _ in range(20):
            net.observe_training_margin(torch.tensor([5.0, 0.0]))
        thr = net.abstain_threshold()
        self.assertAlmostEqual(thr, 5.0, places=4)
        self.assertFalse(net.should_abstain(torch.tensor([5.0, 0.0])), "a margin at the training p5 must not abstain")
        self.assertTrue(net.should_abstain(torch.tensor([0.1, 0.0])), "a much smaller margin must abstain")

    def test_recurrent_state_is_fed_back_and_influences_next_step(self):
        net = RecurrentDiffLogicGateNetwork(n_input_bits=2, n_layers=2, n_gates=8, recurrent_bits=4, n_groups=2, seed=7)
        x = torch.tensor([0.2, 0.8])
        rec0 = net.zero_state()
        self.assertEqual(rec0.shape, (4,))
        g1, rec1 = net(x, rec0, discretise=False)
        g2, rec2 = net(x, rec1, discretise=False)
        self.assertFalse(torch.allclose(g1, g2), "feeding back a different recurrent state must change the output")


if __name__ == "__main__":
    unittest.main()
