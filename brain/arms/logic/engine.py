# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:05 +0400 — A2's engine: a recurrent
#   differentiable logic-gate network (B1-PREREG.md §4, row A2). Same fence as
#   brain/arms/soft/engine.py: no brain.protocol import, no tape, driven by explicit
#   constructor arguments and plain tensors; the Arm wrapper is added after the merge.
#
# What "a softmax over the 16 binary functions" means, made exact (PREREG names the shape —
# "the RDDLGN shape" — but not the relaxation; this is the standard probabilistic reading,
# re-derived from first principles here, not copied from a specific paper's code): treat two
# soft inputs a, b in [0,1] as independent Bernoulli probabilities: P(f(a,b)=1) has a closed
# form for each of the 16 two-input Boolean functions (AND=ab, OR=a+b-ab, XOR=a+b-2ab, etc).
# TRAINING (relaxed): a gate's output is the softmax-weighted MIXTURE of the 16 closed forms.
# DISCRETISED inference (PREREG: "tested DISCRETISED (argmax gate per node)"): the gate's
# function is the SINGLE argmax function, evaluated at HARD-ROUNDED a, b — since every closed
# form evaluates to an exact 0/1 at hard 0/1 inputs, this reuses the identical formula table,
# only the input rounding and the combining weights (one-hot vs softmax) differ.
#
# Declared choices (RAISED in docs/briefs/B1-BUILDER3-REPORT.md §2 alongside soft/engine.py's
# D1-D6, numbered D7 onward there):
#   D7. Wiring: gate g in layer l takes inputs from two indices drawn WITHOUT replacement from
#       layer l-1's node set (the input vector, for l=0), via torch.randint seeded from
#       (seed, "wiring", l) — PREREG: "random fixed wiring from the seed". Fixed for the
#       engine's lifetime (never re-drawn, never learned).
#   D8. The recurrent state is the LAST 256 gate outputs of the final layer (declared: "last",
#       not "first" — arbitrary but fixed), concatenated onto the input vector at the NEXT
#       step, before layer 0. At the very first step (no history), the recurrent block is 0.
#   D9. "Outputs by group sums per answer class": the final layer's G gates are split into
#       n_groups equal contiguous blocks (declared: contiguous, not interleaved — the random
#       wiring already scrambles which INPUT reaches which gate, so a contiguous grouping of
#       OUTPUT gates adds no further structure that matters); a group's score = the sum of its
#       gates' soft (or, discretised, hard 0/1) outputs.
#   D10. Abstention margin: the winning group's (top1 - top2) score gap, compared against the
#       p5 of that same gap on the arm's own training answers (recomputed at each sleep, same
#       law as A1's abstention bands — PREREG only states this for A1's ANSWER head; A2's row
#       says "abstains when the winning group's margin is below the p5 of its training
#       margins", so the mechanism is the SAME shape, reimplemented here for A2's group-sum
#       output instead of A1's softmax head).
#   D11. Growth: none (PREREG: "none (the literature has no growth; declared)") — L and G are
#       fixed at construction; there is no grow() method on this engine at all (unlike A1's).
import math
from typing import Optional

import torch
import torch.nn as nn

from brain.arms.soft.engine import derive_seed, new_generator  # reuse the identity-law seeding


class RunningBinariser:
    """A2/A3 both binarise 'each of the 144 glance dims thresholded at its median over the
    TEACH glances (thresholds computed once, on the record)' (PREREG §4, row A2). Online: a
    per-dim running median cannot be exact without buffering, so this keeps every glance
    vector it is shown (bounded — the TEACH phase is finite, a few thousand rows) and computes
    the exact median only when `freeze()` is called. Builder 3's declared timing (RAISED to
    the seat alongside D7-D11): freeze() is called by the Arm wrapper at the FIRST SLEEP row
    seen on the tape, over every TEACH glance observed so far; thresholds are then FIXED for
    the rest of the run (PREREG: 'computed once')."""

    def __init__(self, dim: int):
        self.dim = dim
        self._rows: list[torch.Tensor] = []
        self.thresholds: Optional[torch.Tensor] = None

    def observe(self, glance: torch.Tensor) -> None:
        if self.thresholds is None:
            self._rows.append(glance.detach().clone())

    def freeze(self) -> torch.Tensor:
        if self.thresholds is None:
            if not self._rows:
                self.thresholds = torch.zeros(self.dim)
            else:
                stacked = torch.stack(self._rows)
                self.thresholds = stacked.median(dim=0).values
            self._rows = []
        return self.thresholds

    def binarise(self, glance: torch.Tensor) -> torch.Tensor:
        thr = self.thresholds if self.thresholds is not None else torch.zeros_like(glance)
        return (glance > thr).float()


# ───────────────────────── the 16 two-input Boolean functions, probabilistic closed form ──────
def _all_16(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """a, b: (...,) in [0,1] (or exactly {0,1} for a hard/discretised call). Returns
    (..., 16): P(f_i(a,b)=1) for the 16 two-input Boolean functions, ordered as in the module
    docstring's table (0=False ... 15=True)."""
    zero = torch.zeros_like(a)
    one = torch.ones_like(a)
    ab = a * b
    f = torch.stack(
        [
            zero,  # 0 False
            ab,  # 1 AND
            a - ab,  # 2 A AND NOT B
            a,  # 3 A
            b - ab,  # 4 NOT A AND B
            b,  # 5 B
            a + b - 2 * ab,  # 6 XOR
            a + b - ab,  # 7 OR
            one - (a + b - ab),  # 8 NOR
            one - (a + b - 2 * ab),  # 9 XNOR
            one - b,  # 10 NOT B
            one - b + ab,  # 11 A OR NOT B
            one - a,  # 12 NOT A
            one - a + ab,  # 13 NOT A OR B
            one - ab,  # 14 NAND
            one,  # 15 True
        ],
        dim=-1,
    )
    return f


class DiffLogicLayer(nn.Module):
    """One layer of G two-input gates, each wired (fixed, random) to two nodes of the
    PREVIOUS layer (or the input, for layer 0), each a learned softmax over the 16 functions."""

    def __init__(self, n_inputs: int, n_gates: int, seed: int, layer_index: int):
        super().__init__()
        self.n_inputs = n_inputs
        self.n_gates = n_gates
        gen = new_generator(seed, f"wiring_l{layer_index}", 0)
        # without-replacement pairs per gate (D7); n_inputs must be >= 2
        assert n_inputs >= 2, "a logic layer needs at least 2 inputs to wire from"
        idx = torch.stack(
            [torch.randperm(n_inputs, generator=gen)[:2] for _ in range(n_gates)]
        )  # (n_gates, 2) -- one perm per gate keeps a,b distinct within that gate
        self.register_buffer("idx_a", idx[:, 0])
        self.register_buffer("idx_b", idx[:, 1])
        # edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:45 +0400 — logits start at a
        # SMALL random perturbation, not exact zero. Exact zero is a genuine symmetric fixed
        # point of this basis (hand-derived and confirmed numerically): the unweighted average
        # of all 16 probabilistic functions is the CONSTANT 0.5, independent of a, b — so a
        # network with every gate at uniform softmax outputs a flat 0.5 everywhere, at every
        # layer, regardless of the input or the recurrent state (propagated forward, since 0.5
        # in => 0.5 out at every subsequent gate too). Training from that exact point can get
        # stuck near it (the XOR toy read 0.5/0.5 accuracy — chance — after 1,500 iterations
        # from a zero start; the same shape as this codebase's OTHER symmetric-saddle finding,
        # brain/arms/soft/... test_xor_toy's linear-baseline negative control). A small random
        # nudge (scale declared: 0.1) breaks the symmetry the same way that control's random
        # init does, without changing what "no gate favoured at init" means in spirit.
        logit_gen = new_generator(seed, f"logit_init_l{layer_index}", 0)
        self.logits = nn.Parameter(torch.empty(n_gates, 16).uniform_(-0.1, 0.1, generator=logit_gen))

    def forward(self, x: torch.Tensor, discretise: bool = False) -> torch.Tensor:
        a = x.index_select(-1, self.idx_a)
        b = x.index_select(-1, self.idx_b)
        if discretise:
            ah, bh = (a > 0.5).float(), (b > 0.5).float()
            funcs = _all_16(ah, bh)  # (..., n_gates, 16), exact 0/1 at hard inputs
            # edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 17:20 +0400 — `gather` with a
            # (n_gates,) index against a (batch, n_gates, 16) `funcs` silently produced a
            # batch-size-1 output (PyTorch broadcasts the index's missing leading dim to 1,
            # not to `batch`) — caught by test_xor_toy's own discretised-accuracy check
            # reading a nonsense 0.5 on a hand-forced perfect (XNOR, XOR) gate pair. Fixed by
            # a one-hot multiply, whose broadcasting is unambiguous over any number of leading
            # (batch) dims.
            choice_onehot = torch.nn.functional.one_hot(self.logits.argmax(dim=-1), num_classes=16).float()
            return (funcs * choice_onehot).sum(dim=-1)
        funcs = _all_16(a, b)  # (..., n_gates, 16)
        p = torch.softmax(self.logits, dim=-1)  # (n_gates, 16)
        return (funcs * p).sum(dim=-1)


class RecurrentDiffLogicGateNetwork(nn.Module):
    """A2 (PREREG §4 row A2): L=4 layers x G=2048 gates (both declared, configurable for the
    toy), a 256-bit recurrent state fed back (D8), group-sum outputs (D9), margin-based
    abstention (D10), no growth (D11)."""

    def __init__(
        self,
        n_input_bits: int,
        n_layers: int,
        n_gates: int,
        recurrent_bits: int,
        n_groups: int,
        seed: int,
    ):
        super().__init__()
        self.recurrent_bits = recurrent_bits
        self.n_groups = n_groups
        self.n_gates = n_gates
        assert n_gates % n_groups == 0, "the final layer's gates must split evenly into groups (D9)"
        self.group_size = n_gates // n_groups
        layers = []
        prev_n = n_input_bits + recurrent_bits
        for l in range(n_layers):
            layers.append(DiffLogicLayer(prev_n, n_gates, seed, l))
            prev_n = n_gates
        self.layers = nn.ModuleList(layers)
        self._train_margins: list[float] = []

    def zero_state(self) -> torch.Tensor:
        return torch.zeros(self.recurrent_bits)

    def forward(self, x_bits: torch.Tensor, recurrent_prev: torch.Tensor, discretise: bool = False):
        h = torch.cat([x_bits, recurrent_prev], dim=-1)
        for layer in self.layers:
            h = layer(h, discretise=discretise)
        final = h  # (n_gates,)
        recurrent_next = final[-self.recurrent_bits :]
        groups = final.view(self.n_groups, self.group_size).sum(dim=-1)  # (n_groups,)
        return groups, recurrent_next

    # -- abstention (D10) --------------------------------------------------------------------
    def observe_training_margin(self, groups: torch.Tensor) -> None:
        top2 = torch.topk(groups.detach(), k=min(2, groups.numel())).values
        margin = float(top2[0] - top2[-1])
        self._train_margins.append(margin)

    def abstain_threshold(self) -> float:
        if not self._train_margins:
            return 0.0
        t = torch.tensor(self._train_margins)
        return float(torch.quantile(t, 0.05))

    def should_abstain(self, groups: torch.Tensor) -> bool:
        top2 = torch.topk(groups.detach(), k=min(2, groups.numel())).values
        margin = float(top2[0] - top2[-1])
        return margin < self.abstain_threshold()


# ───────────────────────── trainer: truncated BPTT over the last K steps (PREREG: 8 awake) ────
class LogicBPTTTrainer:
    """PREREG §4 row A2: 'trained through its relaxation -- awake: truncated BPTT over the
    last 8 steps per event; asleep: as A1's replay' -- both are the SAME mechanism (full
    backward over a bounded window) at a different window length K, exactly like
    brain.arms.soft.engine.BPTTTrainer; a separate class only because A2's forward signature
    (recurrent bit-state, discretise flag) differs from the GRU's."""

    def __init__(self, params, lr: float = 0.05, momentum: float = 0.9, clip: float = 1.0):
        self.opt = torch.optim.SGD(list(params), lr=lr, momentum=momentum)
        self.params = list(self.opt.param_groups[0]["params"])
        self.clip = clip

    def step(self, loss: torch.Tensor) -> None:
        self.opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.params, self.clip)
        self.opt.step()


def param_count(n_input_bits: int, n_layers: int, n_gates: int, recurrent_bits: int) -> int:
    """Every DiffLogicLayer has n_gates*16 learned logits (the wiring is fixed, not learned)."""
    return n_layers * n_gates * 16
