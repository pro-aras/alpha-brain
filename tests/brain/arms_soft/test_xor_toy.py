# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 16:33 +0400 — the required positive control
#   (B1-PREREG.md §5.5 (0b): "plain XOR (4 patterns through the arm's own input road) at 100%
#   for A0-A4") for A1's engine, plus a negative control that PROVES the harness can also read
#   a failure (#91/#158's law: a 100%-finding needs a control that could have come back
#   negative). Runs under both trainers this file's engine exposes (LocalEligibilityTrainer —
#   A1's awake rule, and BPTTTrainer — A1's asleep rule / A1-BPTT-AWAKE's awake rule), since
#   for a ONE-STEP toy (no time gap between the two bits and the answer) the two rules are not
#   yet distinguishable — declared as a toy limitation in docs/briefs/B1-BUILDER3-REPORT.md,
#   not hidden.
#
# Determinism (B1-PREREG.md §3.1): 1 thread, deterministic algorithms, one seed per draw site
# (this module's generators all come from brain.arms.soft.engine.new_generator).
import os
import sys
import unittest

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from brain.arms.soft.engine import (  # noqa: E402
    BPTTTrainer,
    GrowingGRUEngine,
    LocalEligibilityTrainer,
    YesNoHead,
    new_generator,
)

XOR = [
    (torch.tensor([0.0, 0.0]), 0),
    (torch.tensor([0.0, 1.0]), 1),
    (torch.tensor([1.0, 0.0]), 1),
    (torch.tensor([1.0, 1.0]), 0),
]


def _train_engine(trainer_name: str, seed: int, max_iters: int = 4000):
    torch.manual_seed(seed)
    engine = GrowingGRUEngine(input_dim=2, h0=8, hmax=8, seed=seed)
    head = YesNoHead(hmax=8)
    gen = new_generator(seed, "head_init", 0)
    head.init_block(8, gen)
    params = list(engine.parameters()) + list(head.parameters())
    if trainer_name == "local":
        trainer = LocalEligibilityTrainer(params, lam=0.9, lr=0.2)
    else:
        trainer = BPTTTrainer(params, lr=0.2, momentum=0.9, clip=1.0)

    for it in range(max_iters):
        correct = 0
        for x, y in XOR:
            h0 = engine.zero_state()
            h1 = engine.step(x, h0)
            logits = head(h1, active_h=8)
            loss = nn.functional.cross_entropy(logits.unsqueeze(0), torch.tensor([y]))
            trainer.step(loss) if trainer_name == "bptt" else trainer.step(loss, valence=1.0)
            if int(logits.argmax()) == y:
                correct += 1
        if correct == 4:
            return engine, head, it + 1
    return engine, head, None


def _eval_accuracy(engine, head) -> float:
    correct = 0
    with torch.no_grad():
        for x, y in XOR:
            h1 = engine.step(x, engine.zero_state())
            logits = head(h1, active_h=8)
            if int(logits.argmax()) == y:
                correct += 1
    return correct / len(XOR)


class LinearBaseline(nn.Module):
    """The NEGATIVE control: a bare affine map, x -> 2 logits, NO hidden nonlinearity at all —
    Minsky & Papert's 1969 result: a linear threshold/affine unit caps at 3 of 4 = 0.75 on XOR.
    If this ever reads 1.0, the test harness itself cannot tell a solvable toy from an
    unsolvable one, and the positive control above is worthless (#91's law, applied to a
    100%-reading rather than a 0-finding)."""

    def __init__(self):
        super().__init__()
        self.W = nn.Parameter(torch.zeros(2, 2))
        self.b = nn.Parameter(torch.zeros(2))

    def forward(self, x):
        return x @ self.W.T + self.b


def _train_linear_baseline(seed: int, max_iters: int = 3000) -> float:
    """Full-batch GD (not per-example online SGD: at W=b=0 the AVERAGE cross-entropy gradient
    over the 4 XOR points is EXACTLY zero by the problem's own symmetry — a genuine saddle,
    verified by hand: sum_i (0.5 - onehot(y_i)) x_i = 0 — so a symmetric or unlucky init can
    get stuck at chance (0.5) rather than reaching the 0.75 ceiling; this is a property of
    linear models on XOR, not a test bug, and is why the init is randomised at a scale (U(-2,2))
    large enough to usually escape the saddle. Either outcome (stuck at 0.5, or reaching 0.75)
    is a valid negative-control reading: what must NEVER happen is 1.0."""
    gen = torch.Generator().manual_seed(seed)
    model = LinearBaseline()
    with torch.no_grad():
        model.W.uniform_(-2.0, 2.0, generator=gen)
        model.b.uniform_(-2.0, 2.0, generator=gen)
    opt = torch.optim.SGD(model.parameters(), lr=0.3, momentum=0.0)
    X = torch.stack([x for x, _ in XOR])
    Y = torch.tensor([y for _, y in XOR])
    best = 0.0
    for _ in range(max_iters):
        logits = model(X)
        loss = nn.functional.cross_entropy(logits, Y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        acc = (logits.argmax(dim=1) == Y).float().mean().item()
        best = max(best, acc)
    return best


class TestA1XorToy(unittest.TestCase):
    """B1-PREREG.md §5.5 (0b), for A1 (the GRU engine Builder 3 owns)."""

    def setUp(self):
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)

    def test_bptt_solves_xor_100_percent(self):
        engine, head, iters = _train_engine("bptt", seed=20261001)
        acc = _eval_accuracy(engine, head)
        self.assertEqual(acc, 1.0, f"A1 engine (BPTT rule) must solve XOR at 100%%, got {acc} after {iters} iters")

    def test_local_rule_solves_xor_100_percent(self):
        # a single-step toy: no time gap between input and answer, so the 1-step-truncated
        # LOCAL rule (D4) is not yet distinguished from BPTT here (declared in the report) —
        # both must still reach the required 100%.
        engine, head, iters = _train_engine("local", seed=20261001)
        acc = _eval_accuracy(engine, head)
        self.assertEqual(acc, 1.0, f"A1 engine (LOCAL rule) must solve XOR at 100%%, got {acc} after {iters} iters")

    def test_negative_control_linear_baseline_caps_at_0_75(self):
        # a sweep of control seeds (none of them B1's graded seeds): confirms the 0.75 XOR
        # ceiling is empirically reachable (Minsky & Papert 1969) and 1.0 never is, whatever a
        # given init lands on (see _train_linear_baseline's docstring on the saddle at W=0).
        bests = [_train_linear_baseline(seed=s) for s in range(1, 6)]
        for s, best in zip(range(1, 6), bests):
            self.assertLessEqual(best, 0.75 + 1e-9, f"seed {s}: linear baseline must NOT exceed the 0.75 ceiling")
        self.assertTrue(
            any(b >= 0.75 - 1e-9 for b in bests),
            f"at least one control seed should reach the achievable 0.75 ceiling; got {bests}",
        )

    def test_determinism_same_seed_same_trajectory(self):
        # a cheap sanity check ahead of §3.1's real identity test (which lives at the Arm
        # level, added after the protocol freeze): two BPTT runs from the same seed, same
        # number of iterations, must produce bit-identical final parameters.
        e1, h1, it1 = _train_engine("bptt", seed=777, max_iters=50)
        e2, h2, it2 = _train_engine("bptt", seed=777, max_iters=50)
        for p1, p2 in zip(e1.parameters(), e2.parameters()):
            self.assertTrue(torch.equal(p1, p2), "same seed must give byte-identical parameters")
        for p1, p2 in zip(h1.parameters(), h2.parameters()):
            self.assertTrue(torch.equal(p1, p2))


if __name__ == "__main__":
    unittest.main()
