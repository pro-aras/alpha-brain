# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 16:25 +0400 — initial engine: GrowingGRU,
#   growable heads, the two attention read-outs (A1-ATT / A1-MA), the interface NETWORK-side
#   pieces of B1-PREREG.md §4.2 (IF-1/IF-2/IF-3; IF-4 reuses MemoryAttentionReadout), and the
#   matched-parameter solver for §4.1. Written BEFORE brain/protocol.py is frozen (b1-integration
#   still at 94546ce when this file was started) — by B1-PREREG.md §9's fence this file imports
#   NOTHING from brain.protocol and knows nothing of tape rows, Arm, Answer or config dicts; it
#   is pure PyTorch learning machinery, driven by explicit constructor arguments and plain
#   tensors. The Arm-conforming wrapper (brain/arms/soft/arm.py) is added after the merge and
#   translates tape rows into the step vectors this module consumes.
#
# Design decisions this file makes that B1-PREREG.md leaves open (each RAISED in
# docs/briefs/B1-BUILDER3-REPORT.md §2 as well, per the PREREG's own law, §11: "a clause a
# builder cannot implement is RAISED to the seat, never worked around" — these are not clauses
# the file fails, they are free parameters the PREREG deliberately leaves to "a GRU layer" /
# "an attention read-out" / "a learned gate", and a builder must pick SOMETHING to build; each
# choice is named here so the seat can overrule it before any graded run):
#   D1. GRU equation: r_t = sigmoid(x Wir^T + h Whr^T + br); z_t = sigmoid(x Wiz^T + h Whz^T + bz);
#       n_t = tanh(x Win^T + r*(h Whn^T) + bn); h_t = (1-z_t)*n_t + z_t*h_prev. Three SEPARATE
#       (H, ·) matrices per gate rather than one stacked (3H, ·) matrix, so a newborn unit's rows
#       are contiguous per gate and growth is a simple row/column slice (a stacked layout would
#       split one unit's rows across three disjoint blocks).
#   D2. Growth allocates a fixed (HMAX, ·) buffer at construction and tracks an `active` count;
#       birth = randomising rows [active:active+n) and zeroing the columns [active:active+n)
#       for EVERY row up to the new active count (Dohare et al. 2024: incoming random, outgoing
#       zero — applied uniformly, so old-units'-incoming-from-new is zero too, and new-to-new is
#       zero). This mirrors the codebase's own idiom for a growing Area's W (genome/creature: a
#       pre-allocated block + a live/pad split — SOLUTIONS #211 names the same pattern), which
#       also keeps the identity law simple (the tensor's SHAPE never changes across an identical
#       run — only its live sub-block and `active` do).
#   D3. Every head that reads h_t (WORLD's sub-heads, ANSWER's heads, the PICK bilinear form)
#       grows its INPUT columns in lock-step with the GRU, new columns ZERO (Dohare's law applied
#       to every consumer of h, not only the recurrent weights — otherwise a birth would change
#       an existing answer, which the PREREG's "a birth never changes what it already computes"
#       forbids for the network as a whole, not only for W_hh).
#   D4. The awake LOCAL rule (e-prop-style): a per-parameter eligibility trace
#       e_t = lam*e_{t-1} + dL/dtheta|_{one-step, h_{t-1} detached} (a 1-step-truncated gradient,
#       lam declared below), and the parameter update is `-lr * e_t * gate`, gate=1 by default and
#       the FEEDBACK valence's sign/magnitude when a FEEDBACK row carries one (the "third factor").
#       This is the cheapest defensible reading of "eligibility traces on the recurrent weights x
#       the WORLD error projected by the read-out" that a single autograd call can produce every
#       step (detach h_{t-1}, backward, accumulate into a trace buffer) without an exact multi-step
#       gradient (which is what asleep BPTT is for).
#   D5. PICK candidate encoding: clone the engine's OWN weights (no grad) into a scratch forward
#       pass, run the candidate's own glance steps from the query state h_t as the initial hidden
#       state, take the resulting h; score = h_query . (M h_candidate) for a learned bilinear M
#       (PREREG: "its encoded glances . the query state").
#   D6. `answer(learn=False)` must leave state_sha unchanged (PREREG §5.1, control 0e): every
#       method that "peeks" (PICK candidate encoding, the abstention check) clones the hidden
#       state and any budget/window counters it touches BEFORE using them, and never writes back
#       through the clone. `Engine.frozen_forward()` is the one entry point that guarantees this.
#
# nothing in this file renders or glances (PREREG §3.0); it consumes vectors only.
from __future__ import annotations

import collections
import hashlib
import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import torch
import torch.nn as nn


# ───────────────────────── seeding (PREREG §3.1: one generator per draw site) ─────────────────
def derive_seed(seed: int, site: str, index: int) -> int:
    """(seed, site, index) -> a deterministic 63-bit int, one torch.Generator per random-draw
    site (B1-PREREG.md §3.1; also used by A1's row: generators keyed (seed,"birth",i) and
    (seed,"replay",sleep_index))."""
    h = hashlib.sha256(f"{seed}:{site}:{index}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") % (2**63 - 1)


def new_generator(seed: int, site: str, index: int) -> torch.Generator:
    g = torch.Generator(device="cpu")
    g.manual_seed(derive_seed(seed, site, index))
    return g


# ───────────────────────── growth budget (#227, #233, #237, #238: series, never silent) ───────
@dataclass
class GrowthBudget:
    """A regenerating per-arrival unit budget. PREREG §4 row A1: "a unit budget (16,
    regenerating 1 per 500 steps)"; #227's law: never a cap that eats — refusals are COUNTED,
    the remaining is always readable as a SERIES, never folded into a single total (#233)."""

    capacity: int
    regen_every: int
    remaining: int = field(init=False)
    _last_regen_step: int = field(init=False, default=0)
    refused: int = field(init=False, default=0)
    granted: int = field(init=False, default=0)

    def __post_init__(self):
        self.remaining = self.capacity

    def tick(self, step: int) -> None:
        while step - self._last_regen_step >= self.regen_every:
            self._last_regen_step += self.regen_every
            if self.remaining < self.capacity:
                self.remaining += 1

    def request(self, n: int) -> int:
        grant = max(0, min(n, self.remaining))
        self.remaining -= grant
        self.granted += grant
        self.refused += n - grant
        return grant

    def reset_arrival(self, step0: int) -> None:
        # RAISED (docs/briefs/B1-BUILDER3-REPORT.md §2, item R1): B1-PREREG.md §2.7 places no
        # ARRIVAL row before L1 (only "ARRIVAL {digits}" before phase D) — read literally, a
        # per-ARRIVAL budget never opens during the whole letters phase and A1 births 0 units
        # at L1-L6 (#233's shape: a budget keyed to an event that never fires). Builder 3's
        # declared stand-in, pending the seat's word: treat construction time (before any tape
        # row) as an implicit "arrival 0" that opens this budget once; a real ARRIVAL row (the
        # digits) resets it again via this same method. This value is a SERIES field
        # (series()), never silently absorbed.
        self.remaining = self.capacity
        self._last_regen_step = step0

    def series(self) -> dict:
        return {"remaining": self.remaining, "refused": self.refused, "granted": self.granted}


def _cap_by_hmax(n_request: int, active: int, hmax: int) -> tuple[int, int]:
    """Split a birth request into (granted-by-hmax, refused-by-hmax) — the declared bound
    'H <= 1024 births refused and COUNTED at it, never a cap that eats' (PREREG §4 row A1)."""
    room = max(0, hmax - active)
    grant = min(n_request, room)
    return grant, n_request - grant


# ───────────────────────── growable linear (D3) ────────────────────────────────────────────────
class GrowableLinear(nn.Module):
    """y = W[:, :active] @ x + b, where W is pre-allocated to (n_out, HMAX) or grows its OWN
    n_out too (add_output, for A1's NAME head: "a new name adds an output unit with zero
    weights"). New hidden columns and new output rows are always zero (Dohare, D3)."""

    def __init__(self, hmax: int, n_out: int, growable_out: bool = False, out_cap: int = 0):
        super().__init__()
        self.hmax = hmax
        self.growable_out = growable_out
        out_alloc = out_cap if growable_out else n_out
        assert not growable_out or out_cap >= n_out
        self.W = nn.Parameter(torch.zeros(out_alloc, hmax))
        self.b = nn.Parameter(torch.zeros(out_alloc))
        self.n_out = n_out  # active outputs

    def init_block(self, active_h: int, gen: torch.Generator) -> None:
        k = 1.0 / math.sqrt(max(1, active_h))
        with torch.no_grad():
            self.W[: self.n_out, :active_h].uniform_(-k, k, generator=gen)

    def grow_hidden(self, new_active: int) -> None:
        # new hidden columns start at ZERO (D3): a birth must not move an existing answer.
        pass  # the buffer is pre-allocated to hmax and already zero beyond old `active`

    def add_output(self, active_h: int) -> int:
        """Append one new output row, weights ZERO (PREREG: 'a new name adds an output unit
        with zero weights') — never random, unlike a hidden unit's incoming weights: the two
        laws are different on purpose (a name must not be GUESSABLE before it is heard)."""
        assert self.growable_out and self.n_out < self.W.shape[0], "add_output: out of out_cap"
        idx = self.n_out
        self.n_out += 1
        return idx

    def forward(self, h: torch.Tensor, active_h: int) -> torch.Tensor:
        # h may be hmax-wide (GrowingGRUEngine.step always returns an hmax-wide tensor, the
        # tail beyond `active` being the not-yet-born units' zero padding) or already sliced
        # to active_h — accept either, always read only the live [:active_h] slice.
        h_active = h[..., :active_h]
        return h_active @ self.W[: self.n_out, :active_h].T + self.b[: self.n_out]


# ───────────────────────── the growing GRU (A1's trunk) ────────────────────────────────────────
class GrowingGRUEngine(nn.Module):
    """PREREG §4 row A1: 'a GRU layer grown by error ... H0 = 64 units; a unit is born when the
    WORLD error's running mean over the last 200 steps exceeds 1.5x its median over the
    arrival's first 200 steps AND the arrival's unit budget has room ... incoming weights from
    the init distribution, outgoing weights ZERO ... H <= 1024'.

    No tape, no protocol: `step()` takes a plain (input_dim,) tensor and a (HMAX,) hidden
    tensor (only [:active] is meaningful) and returns the next hidden tensor, still HMAX-wide.
    Callers (the toy, and later the Arm wrapper) drive the birth criterion via `observe_error`
    and `maybe_grow`; the engine does not decide FOR ITSELF when a "step" ends an arrival.
    """

    def __init__(
        self,
        input_dim: int,
        h0: int,
        hmax: int,
        seed: int,
        arrival_budget: int = 16,
        arrival_regen: int = 500,
        birth_batch: int = 1,
    ):
        super().__init__()
        assert 0 < h0 <= hmax
        self.input_dim = input_dim
        self.hmax = hmax
        self.active = h0
        self.seed = seed
        self.birth_batch = birth_batch
        H = hmax
        for g in ("r", "z", "n"):
            setattr(self, f"W_ih_{g}", nn.Parameter(torch.zeros(H, input_dim)))
            setattr(self, f"W_hh_{g}", nn.Parameter(torch.zeros(H, H)))
            setattr(self, f"b_{g}", nn.Parameter(torch.zeros(H)))
        gen0 = new_generator(seed, "init", 0)
        self._init_rows(0, h0, gen0, from_active=0)
        self.budget = GrowthBudget(arrival_budget, arrival_regen)
        self.births = 0
        self.refused_hmax = 0
        self._birth_draw_index = 0
        self._err_window: collections.deque = collections.deque(maxlen=200)
        self._arrival_first200: list[float] = []
        self._arrival_baseline: Optional[float] = None
        self._step_count = 0
        self._growth_listeners: list = []  # GrowableLinear-like objects to notify on growth

    # -- growth plumbing --------------------------------------------------------------------
    def register_growth_listener(self, obj: GrowableLinear) -> None:
        self._growth_listeners.append(obj)

    def _init_rows(self, lo: int, hi: int, gen: torch.Generator, from_active: int) -> None:
        k_i = 1.0 / math.sqrt(self.input_dim)
        k_h = 1.0 / math.sqrt(max(1, from_active)) if from_active > 0 else 1.0
        with torch.no_grad():
            for g in ("r", "z", "n"):
                Wih = getattr(self, f"W_ih_{g}")
                Wih[lo:hi, :].uniform_(-k_i, k_i, generator=gen)
                Whh = getattr(self, f"W_hh_{g}")
                if from_active > 0:
                    Whh[lo:hi, :from_active].uniform_(-k_h, k_h, generator=gen)
                # D2: outgoing columns [lo:hi) zero for EVERY row up to hi (old-from-new AND
                # new-from-new); rows [lo:hi) beyond from_active columns already zero (fresh alloc)
                Whh[:hi, lo:hi] = 0.0
                getattr(self, f"b_{g}")[lo:hi] = 0.0

    def pad_state(self, h: torch.Tensor) -> torch.Tensor:
        """h may be narrower than hmax (e.g. loaded from an older snapshot); pad with zeros —
        a new unit's h before it is born is, by definition, 0."""
        if h.shape[-1] == self.hmax:
            return h
        pad = torch.zeros(*h.shape[:-1], self.hmax - h.shape[-1], dtype=h.dtype)
        return torch.cat([h, pad], dim=-1)

    def zero_state(self, batch_shape: Sequence[int] = ()) -> torch.Tensor:
        return torch.zeros(*batch_shape, self.hmax)

    def grow(self, n_request: int) -> int:
        grant_hmax, refused_hmax = _cap_by_hmax(n_request, self.active, self.hmax)
        self.refused_hmax += refused_hmax
        grant = self.budget.request(grant_hmax)
        if grant <= 0:
            return 0
        gen = new_generator(self.seed, "birth", self._birth_draw_index)
        self._birth_draw_index += 1
        lo, hi = self.active, self.active + grant
        self._init_rows(lo, hi, gen, from_active=self.active)
        self.active = hi
        self.births += grant
        for obj in self._growth_listeners:
            obj.grow_hidden(self.active)
        return grant

    # -- birth criterion (driven by the caller, once per "step") --------------------------------
    def observe_world_error(self, err: float, step: int, arrival_started_at: int) -> None:
        self.budget.tick(step)
        self._err_window.append(err)
        if step - arrival_started_at < 200:
            self._arrival_first200.append(err)
        elif self._arrival_baseline is None and self._arrival_first200:
            self._arrival_baseline = float(torch.tensor(self._arrival_first200).median())

    def should_birth(self) -> bool:
        if self._arrival_baseline is None or len(self._err_window) < 200:
            return False
        running_mean = float(torch.tensor(list(self._err_window)).mean())
        return running_mean > 1.5 * self._arrival_baseline

    def maybe_grow(self, step: int, arrival_started_at: int) -> int:
        if self.should_birth():
            got = self.grow(self.birth_batch)
            if got:
                self._err_window.clear()
            return got
        return 0

    def start_arrival(self, step0: int) -> None:
        self.budget.reset_arrival(step0)
        self._err_window.clear()
        self._arrival_first200 = []
        self._arrival_baseline = None

    # -- the recurrence (D1) --------------------------------------------------------------------
    def step(self, x_t: torch.Tensor, h_prev: torch.Tensor) -> torch.Tensor:
        a = self.active
        hp = h_prev[..., :a]
        Wir, Wiz, Win = self.W_ih_r[:a], self.W_ih_z[:a], self.W_ih_n[:a]
        Whr, Whz, Whn = self.W_hh_r[:a, :a], self.W_hh_z[:a, :a], self.W_hh_n[:a, :a]
        br, bz, bn = self.b_r[:a], self.b_z[:a], self.b_n[:a]
        r = torch.sigmoid(x_t @ Wir.T + hp @ Whr.T + br)
        z = torch.sigmoid(x_t @ Wiz.T + hp @ Whz.T + bz)
        n = torch.tanh(x_t @ Win.T + r * (hp @ Whn.T) + bn)
        h_new = (1 - z) * n + z * hp
        if a < self.hmax:
            pad = h_prev[..., a:]
            h_new = torch.cat([h_new, pad], dim=-1)
        return h_new

    def state_sha_bytes(self) -> bytes:
        """The raw bytes this engine contributes to an Arm's state_sha (PREREG §3.1): every
        parameter tensor, sorted by name, plus the size fields growth changes (active, births,
        budget). Snapshot/load round-trips these exactly."""
        parts = []
        for name, p in sorted(self.named_parameters()):
            parts.append(name.encode())
            parts.append(p.detach().contiguous().numpy().tobytes())
        parts.append(f"active={self.active};births={self.births};refused_hmax={self.refused_hmax}".encode())
        parts.append(str(self.budget.series()).encode())
        return b"|".join(parts)


# ───────────────────────── heads ────────────────────────────────────────────────────────────────
class WorldHead(nn.Module):
    """PREREG §4 row A1, WORLD head: predicts the next step (glance: MSE; letter/kind: CE) —
    the LEARNING SIGNAL for the awake/asleep rules. One sub-head per block; the loss for a
    block is only computed when the NEXT step actually carries that block (declared: a step's
    "kind" — glance / letter / cue — decides which sub-head's loss is live for it, matching
    §4's per-step-type encoding; see brain/arms/soft/steps.py, added after the merge)."""

    def __init__(self, hmax: int, glance_dim: int, letter_dim: int, kind_dim: int):
        super().__init__()
        self.glance_head = GrowableLinear(hmax, glance_dim)
        self.letter_head = GrowableLinear(hmax, letter_dim)
        self.kind_head = GrowableLinear(hmax, kind_dim)

    def init_all(self, active_h: int, gen: torch.Generator) -> None:
        for h in (self.glance_head, self.letter_head, self.kind_head):
            h.init_block(active_h, gen)

    def grow_hidden(self, new_active: int) -> None:
        for h in (self.glance_head, self.letter_head, self.kind_head):
            h.grow_hidden(new_active)

    def forward(self, h: torch.Tensor, active_h: int):
        return {
            "glance": self.glance_head(h, active_h),
            "letter": self.letter_head(h, active_h),
            "kind": self.kind_head(h, active_h),
        }

    @staticmethod
    def loss(pred: dict, target_glance=None, target_letter=None, target_kind=None) -> torch.Tensor:
        total = torch.zeros(())
        if target_glance is not None:
            total = total + torch.nn.functional.mse_loss(pred["glance"], target_glance)
        if target_letter is not None:
            total = total + torch.nn.functional.cross_entropy(
                pred["letter"].unsqueeze(0), target_letter.unsqueeze(0)
            )
        if target_kind is not None:
            total = total + torch.nn.functional.cross_entropy(
                pred["kind"].unsqueeze(0), target_kind.unsqueeze(0)
            )
        return total


class NameAnswerHead(GrowableLinear):
    """PREREG: 'NAME = a classifier over the names HEARD so far (a new name adds an output
    unit with zero weights; never letter-by-letter generation — the mouth law)'."""

    def __init__(self, hmax: int, out_cap: int):
        super().__init__(hmax, n_out=0, growable_out=True, out_cap=out_cap)
        self.names: list[str] = []

    def hear_name(self, name: str, active_h: int) -> int:
        if name in self.names:
            return self.names.index(name)
        idx = self.add_output(active_h)
        self.names.append(name)
        return idx


class YesNoHead(GrowableLinear):
    def __init__(self, hmax: int):
        super().__init__(hmax, n_out=2)  # [NO, YES] logits


class PickScorer(nn.Module):
    """PREREG: PICK 'a score per candidate (its encoded glances . the query state)' (D5:
    bilinear form so the two vectors need not share a basis)."""

    def __init__(self, hmax: int):
        super().__init__()
        self.M = nn.Parameter(torch.zeros(hmax, hmax))

    def init_block(self, active_h: int, gen: torch.Generator) -> None:
        k = 1.0 / math.sqrt(max(1, active_h))
        with torch.no_grad():
            self.M[:active_h, :active_h].uniform_(-k, k, generator=gen)

    def grow_hidden(self, new_active: int) -> None:
        pass

    def score(self, h_query: torch.Tensor, h_candidate: torch.Tensor, active_h: int) -> torch.Tensor:
        Ma = self.M[:active_h, :active_h]
        return h_query[..., :active_h] @ Ma @ h_candidate[..., :active_h]


# ───────────────────────── attention read-outs (§4.1 Memory Attention twins) ───────────────────
class CausalAttentionReadout(nn.Module):
    """A1-ATT: 'ONE causal attention read-out over its own last 256 steps: a single head,
    d = 64, Q = W_Q h_t, K = W_K h_τ, V = W_V h_τ (the paper's eq. 1, the standard value)'."""

    def __init__(self, hmax: int, d: int = 64, window: int = 256):
        super().__init__()
        self.d = d
        self.window = window
        self.WQ = nn.Parameter(torch.zeros(d, hmax))
        self.WK = nn.Parameter(torch.zeros(d, hmax))
        self.WV = nn.Parameter(torch.zeros(d, hmax))

    def init_block(self, active_h: int, gen: torch.Generator) -> None:
        k = 1.0 / math.sqrt(max(1, active_h))
        with torch.no_grad():
            for W in (self.WQ, self.WK, self.WV):
                W[:, :active_h].uniform_(-k, k, generator=gen)

    def grow_hidden(self, new_active: int) -> None:
        pass  # columns beyond old `active` are already zero: growth adds zero-weighted inputs

    def value_of(self, h_hist: torch.Tensor, active_h: int) -> torch.Tensor:
        """The standard value, V = W_V h_tau — overridden by MemoryAttentionReadout."""
        return h_hist[..., :active_h] @ self.WV[:, :active_h].T

    def forward(self, h_t: torch.Tensor, h_hist: torch.Tensor, active_h: int) -> torch.Tensor:
        """h_hist: (T<=window, hmax) causal history INCLUDING h_t as the last row. Returns a
        (d,) read-out vector to concatenate into the answer heads' input."""
        hist = h_hist[-self.window :]
        q = h_t[..., :active_h] @ self.WQ[:, :active_h].T  # (d,)
        k = hist[..., :active_h] @ self.WK[:, :active_h].T  # (T, d)
        v = self.value_of(hist, active_h)  # (T, d)
        scores = (k @ q) / math.sqrt(self.d)  # (T,)
        weights = torch.softmax(scores, dim=-1)
        return weights @ v  # (d,)

    def out_dim(self) -> int:
        return self.d


def rmsnorm(x: torch.Tensor, gain: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    ms = (x * x).mean(dim=-1, keepdim=True)
    return x * torch.rsqrt(ms + eps) * gain


class MemoryAttentionReadout(CausalAttentionReadout):
    """A1-MA: Kang, 'Memory Attention', arXiv 2609.28399 — V = K + RMSNorm(E[s]), E a learned
    (n_tokens, d) table indexed by TOKEN id, RMSNorm with a learned gain (PREREG §4.1). Token
    ids (declared there): the 27 letter-steps, the 24 cue-mark slots, the event kinds, and — for
    a glance step — its glance POSITION 1-5. `n_tokens` is passed by the caller (the Arm wrapper,
    which owns the frozen tape's vocabulary sizes); this module only needs the total count."""

    def __init__(self, hmax: int, n_tokens: int, d: int = 64, window: int = 256):
        super().__init__(hmax, d=d, window=window)
        self.n_tokens = n_tokens
        self.E = nn.Parameter(torch.zeros(n_tokens, d))
        self.gain = nn.Parameter(torch.ones(d))

    def init_block(self, active_h: int, gen: torch.Generator) -> None:
        super().init_block(active_h, gen)
        k = 1.0 / math.sqrt(self.d)
        with torch.no_grad():
            self.E.uniform_(-k, k, generator=gen)

    def value_of_tokens(self, hist: torch.Tensor, token_ids: torch.Tensor, active_h: int) -> torch.Tensor:
        k = hist[..., :active_h] @ self.WK[:, :active_h].T
        mem = rmsnorm(self.E[token_ids], self.gain)
        return k + mem

    def forward_tokens(self, h_t, h_hist, token_ids_hist, active_h):
        hist = h_hist[-self.window :]
        ids = token_ids_hist[-self.window :]
        q = h_t[..., :active_h] @ self.WQ[:, :active_h].T
        k = hist[..., :active_h] @ self.WK[:, :active_h].T
        v = self.value_of_tokens(hist, ids, active_h)
        scores = (k @ q) / math.sqrt(self.d)
        weights = torch.softmax(scores, dim=-1)
        return weights @ v


# ───────────────────────── §4.2 interface arms — the NETWORK side (Builder 3's fence) ──────────
# "The cells side" (the lit cell's id and row handed to the network each step) is Builder 2's
# (PREREG §9 table). Builder 3 builds the NETWORK side only: what the network DOES with an
# (id, row) pair it is handed. Until the protocol is frozen, the type of "an (id, row) pair" is
# left open (a plain (int, Tensor) tuple here); the Arm wrapper adapts whatever Builder 2's
# frozen interface actually hands over.
class ExternalTableAttention(MemoryAttentionReadout):
    """IF-1 (memory values FROM THE CELLS): identical mechanism to MemoryAttentionReadout,
    except the 'table' is not a learned embedding indexed by a closed token vocabulary — it is
    whatever cell row the CELLS hand over for that step, projected to d by a learned P.
    V = K + RMSNorm(P . c_s). `cell_dim` (the cells' vector width) is a constructor argument;
    PREREG §2.4/§4.2 do not pin it (it is A0's own cell width) — RAISED in the report."""

    def __init__(self, hmax: int, cell_dim: int, d: int = 64, window: int = 256):
        # do NOT call MemoryAttentionReadout.__init__ (it allocates a token table E we don't
        # want); build the causal Q/K/V base directly.
        CausalAttentionReadout.__init__(self, hmax, d=d, window=window)
        self.cell_dim = cell_dim
        self.P = nn.Parameter(torch.zeros(d, cell_dim))
        self.gain = nn.Parameter(torch.ones(d))

    def init_block(self, active_h: int, gen: torch.Generator) -> None:
        CausalAttentionReadout.init_block(self, active_h, gen)
        k = 1.0 / math.sqrt(self.cell_dim)
        with torch.no_grad():
            self.P.uniform_(-k, k, generator=gen)

    def value_of_cells(self, hist: torch.Tensor, cell_rows: torch.Tensor, lit_mask: torch.Tensor, active_h: int):
        """cell_rows: (T, cell_dim), one row per history step (zero row where lit_mask is 0,
        i.e. no cell was lit for that step — a glance the cells never lit contributes K alone,
        matching IF-0's fallback: no representation crosses when the cells have nothing to say).
        """
        k = hist[..., :active_h] @ self.WK[:, :active_h].T
        mem = rmsnorm(cell_rows @ self.P.T, self.gain) * lit_mask.unsqueeze(-1)
        return k + mem

    def forward_cells(self, h_t, h_hist, cell_rows_hist, lit_mask_hist, active_h):
        hist = h_hist[-self.window :]
        rows = cell_rows_hist[-self.window :]
        mask = lit_mask_hist[-self.window :]
        q = h_t[..., :active_h] @ self.WQ[:, :active_h].T
        k = hist[..., :active_h] @ self.WK[:, :active_h].T
        v = self.value_of_cells(hist, rows, mask, active_h)
        scores = (k @ q) / math.sqrt(self.d)
        weights = torch.softmax(scores, dim=-1)
        return weights @ v

    # the seam test (#235, PREREG §4.2): "a planted change to ONE cell's row must change the
    # network's value vector at exactly the steps whose s is that cell, and nowhere else" — this
    # holds STRUCTURALLY here because value_of_cells is a pure per-row function of cell_rows
    # (no cross-step mixing before the attention weights are applied), verified in
    # tests/brain/arms_soft/test_interface_arms.py.


class CellRowInputProjector(nn.Module):
    """IF-2 (CELL-ROW INPUT): 'the lit cell's row (P . c_s) appended to the network's input at
    each glance step: the cells as the tokenizer, no attention.' This is the network-side half:
    a learned projection from the cells' vector width to a declared append-width; the Arm
    wrapper concatenates the result onto the standard step vector before GrowingGRUEngine.step.
    """

    def __init__(self, cell_dim: int, append_dim: int, seed: int):
        super().__init__()
        self.cell_dim = cell_dim
        self.append_dim = append_dim
        self.P = nn.Parameter(torch.zeros(append_dim, cell_dim))
        gen = new_generator(seed, "if2_init", 0)
        k = 1.0 / math.sqrt(cell_dim)
        with torch.no_grad():
            self.P.uniform_(-k, k, generator=gen)

    def forward(self, cell_row: Optional[torch.Tensor]) -> torch.Tensor:
        if cell_row is None:
            return torch.zeros(self.append_dim)
        return self.P @ cell_row


class LogitMixGate(nn.Module):
    """IF-3 (ANSWER MIX): 'the cells' recall (their score per name) mixed into the network's
    ANSWER logits by a learned gate per cue' — g(cue) = sigmoid(w[cue]); final = g*external +
    (1-g)*network, external and network logits assumed over the SAME name vocabulary (both are
    'a score per name heard'; the Arm wrapper is responsible for aligning the two index spaces,
    since only it knows both the network's NameAnswerHead.names order and the cells' own name
    order — RAISED in the report as a seam question for Builder 2)."""

    def __init__(self, n_cue_types: int):
        super().__init__()
        self.w = nn.Parameter(torch.zeros(n_cue_types))  # sigmoid(0)=0.5: no prior favourite

    def mix(self, cue_id: int, network_logits: torch.Tensor, external_logits: torch.Tensor) -> torch.Tensor:
        n = network_logits.shape[-1]
        e = external_logits
        if e.shape[-1] != n:
            # pad/truncate defensively; the real seam aligns vocabularies exactly (see docstring)
            if e.shape[-1] < n:
                e = torch.cat([e, torch.full((n - e.shape[-1],), float("-inf"))])
            else:
                e = e[:n]
        g = torch.sigmoid(self.w[cue_id])
        return g * e + (1 - g) * network_logits


# IF-4 ("the network's own table"): literally MemoryAttentionReadout used inside the hybrid —
# no new class; the Arm wrapper instantiates MemoryAttentionReadout directly for IF-4.


# ───────────────────────── trainers (D4: the awake LOCAL rule; the asleep EXACT rule) ───────────
class LocalEligibilityTrainer:
    """The awake LOCAL rule (D4): an e-prop-STYLE eligibility trace — e_t = lam*e_{t-1} +
    grad(loss_t, theta) computed with h_{t-1} DETACHED (a 1-step-truncated gradient at every
    call), update = -lr * valence * e_t. This is a decaying-trace approximation to Bellec et
    al.'s forward-mode e-prop (the exact form needs a per-cell forward Jacobian recursion
    specific to the GRU equations, D1; PREREG says 'e-prop-STYLE', not e-prop exactly — the
    approximation is declared, not hidden). `valence` is the FEEDBACK third factor (PREREG
    CONCLUSION §3 law 2): 1.0 with no FEEDBACK row, the reward/'-1 push the wrong logit down'
    reading otherwise (the Arm wrapper computes it; this class only multiplies by it)."""

    def __init__(self, params, lam: float = 0.9, lr: float = 0.01):
        self.params = list(params)
        self.lam = lam
        self.lr = lr
        self.traces = [torch.zeros_like(p) for p in self.params]

    def step(self, loss: torch.Tensor, valence: float = 1.0) -> None:
        grads = torch.autograd.grad(loss, self.params, retain_graph=False, allow_unused=True)
        with torch.no_grad():
            for p, g, e in zip(self.params, grads, self.traces):
                if g is None:
                    e.mul_(self.lam)
                    continue
                e.mul_(self.lam).add_(g)
                p.add_(-self.lr * valence * e)

    def reset(self) -> None:
        for e in self.traces:
            e.zero_()


class BPTTTrainer:
    """The asleep EXACT rule (PREREG §4 row A1): SGD, momentum 0.9, lr 0.01, clip 1.0, over
    truncated windows (R=64 windows of W=32 steps at sleep; the A1-BPTT-AWAKE twin reuses this
    SAME class as its awake rule too, over a shorter per-event window — 'the awake local rule
    replaced by truncated BPTT over the last 32 steps per event')."""

    def __init__(self, params, lr: float = 0.01, momentum: float = 0.9, clip: float = 1.0):
        self.opt = torch.optim.SGD(list(params), lr=lr, momentum=momentum)
        self.params = list(self.opt.param_groups[0]["params"])
        self.clip = clip

    def step(self, loss: torch.Tensor) -> None:
        self.opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.params, self.clip)
        self.opt.step()


# ───────────────────────── parameter-count formulas (§4.1 matched-parameter solver) ────────────
def gru_param_count(input_dim: int, H: int) -> int:
    """3 gates x (input_dim*H W_ih + H*H W_hh + H bias) — D1's separate-matrix layout."""
    return 3 * (input_dim * H + H * H + H)


def linear_param_count(H: int, n_out: int) -> int:
    return H * n_out + n_out


def bilinear_param_count(H: int) -> int:
    return H * H


def att_readout_param_count(H: int, d: int = 64) -> int:
    return 3 * d * H  # WQ, WK, WV


def ma_readout_param_count(H: int, n_tokens: int, d: int = 64) -> int:
    return 2 * d * H + n_tokens * d + d  # WQ, WK (no WV), E table, RMSNorm gain


def a1_total_params(input_dim: int, H: int, glance_dim: int, letter_dim: int, kind_dim: int, n_names: int) -> int:
    """A1's total parameter count at hidden width H and n_names heard names — the basis every
    matched-parameter twin (A1-ATT, A1-MA) is solved against (PREREG §4.1: 'H = the largest H
    whose TOTAL parameter count <= A1's FINAL count on the same seed')."""
    return (
        gru_param_count(input_dim, H)
        + linear_param_count(H, glance_dim)
        + linear_param_count(H, letter_dim)
        + linear_param_count(H, kind_dim)
        + linear_param_count(H, n_names)
        + bilinear_param_count(H)  # PICK
        + linear_param_count(H, 2)  # YES/NO
    )


def largest_H_under(target_params: int, params_fn, lo: int = 1, hi: int = 4096) -> int:
    """Binary search for the largest H with params_fn(H) <= target_params. params_fn must be
    non-decreasing in H (true of every formula above: every term is H times a positive
    constant plus an H^2 term). Returns 0 if even H=lo exceeds the target (RAISE: the twin
    cannot be matched at any positive width)."""
    if params_fn(lo) > target_params:
        return 0
    while params_fn(hi) <= target_params:
        hi *= 2
        if hi > 1 << 24:
            raise OverflowError("largest_H_under: target_params too large or params_fn ill-formed")
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if params_fn(mid) <= target_params:
            lo = mid
        else:
            hi = mid - 1
    return lo
