# edit: Claude (Sonnet 5, B1 builder 3), 2026-09-24 19:50 +0400 — A3's engine: a multi-class
#   Tsetlin machine (B1-PREREG.md §4, row A3). Same fence as the other two engines: no
#   brain.protocol import, no tape; driven by explicit constructor args and plain tensors.
#
# The algorithm (standard multi-class Tsetlin Machine, Granmo 2018 — PREREG parameterises it
# (C=200, T=50, s=5.0, "declared, not tuned") but does not reinvent it, so this file implements
# the literature's own training rule rather than inventing a variant):
#   - 2*n_features automata per clause (literal k = x_k, literal n_features+k = NOT x_k), each
#     an integer STATE in [1, N]; ACTION = INCLUDE iff state > N//2 (E20's own convention:
#     "ACTION = include iff state >= N/2 + 1", identical for integer N).
#   - clause polarity: clause index j even -> +1 (recognises the class), j odd -> -1 (recognises
#     the ABSENCE of the class, votes it down).
#   - a clause's OUTPUT = AND of its included literals' truth values; a clause with NO included
#     literals ("vacuous") outputs 1 during TRAINING, 0 during PREDICTION (E20's own convention,
#     verbatim — a training-time vacuous clause must still receive feedback to specialise; a
#     prediction-time one must not vote).
#   - a class's VOTE = sum(clause_output * polarity) over its own C clauses; multi-class
#     inference = argmax over classes' votes, ties to the smallest class index (unclipped);
#     abstains natively (PREREG: "abstains natively when no class sum is above 0") — the
#     argmax is taken only among classes whose vote is > 0, else UNKNOWN/NOTHING (the Arm
#     wrapper's job, per PREREG's per-answer-kind abstention shape).
#   - training a class's bank against target y_c in {0,1}: the feedback-participation
#     probability is p = (T - clip(v,-T,T))/(2T) if y_c else (T + clip(v,-T,T))/(2T) (E20's
#     own formula, "feedback probabilities (T-v)/(2T)" — a SINGLE Bernoulli draw per bank per
#     event decides whether this bank receives ANY feedback this round); when it does: Type I
#     feedback to the polarity that recognises y_c (POSITIVE clauses if y_c=1, NEGATIVE if
#     y_c=0), Type II to the other polarity.
#   - Type I (reinforce recognition): a FIRED clause's included-and-satisfied literals are
#     REWARDED (state += 1) w.p. (s-1)/s; a fired clause's un-included literals whose value is
#     ABSENT are PENALISED (state -= 1) w.p. 1/s; a clause that did NOT fire has every literal
#     penalised w.p. 1/s (decay toward "don't care", letting the clause re-specialise later).
#   - Type II (suppress false recognition): a FIRED clause's literals whose value is ABSENT
#     AND currently EXCLUDED are INCLUDED (state += 1) DETERMINISTICALLY (no probability) — the
#     minimal, deterministic specialisation that stops this one false-positive clause firing on
#     this exact input, per the literature's own rule.
#   - every class's bank is trained on EVERY event (y_c = 1 for the true class, 0 for all
#     others) — declared (D22): the literature also allows updating only ONE randomly-chosen
#     negative class per event for large class counts; training ALL classes is simpler, fully
#     specified, and RAISED as a cost trade-off for the seat if the real run's class count (up
#     to 52+ names) makes the O(n_classes) cost bar bind.
#
#   Well-defined probabilities (#171's E20 lesson, applied without needing E20's exact
#   low-level uint64 mechanism): every Bernoulli draw here is `torch.rand((), generator=gen) <
#   p` against a probability `p` computed from a VARIABLE (never a literal baked into a
#   comparison the way E20's original `llround(p*2^64)` was), and `torch.rand` with a seeded
#   `torch.Generator` is well-defined by construction — no overflow path exists to replicate.
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Sequence

import torch

from brain.arms.soft.engine import derive_seed, new_generator  # the shared (seed, site, index) law


class TsetlinClauseBank:
    """One binary (this-class-vs-not) sub-machine: C clauses over n_features boolean literals."""

    def __init__(self, n_features: int, C: int, N: int, T: int, s: float, seed: int, site: str):
        assert C % 2 == 0, "C must be even (half positive polarity, half negative — PREREG §4 row A3)"
        self.n_features = n_features
        self.C = C
        self.N = N
        self.T = T
        self.s = s
        self.seed = seed
        self.site = site
        gen = new_generator(seed, f"{site}_init", 0)
        # standard TM init: every automaton starts at the border, N//2 (just excluded) or
        # N//2+1 (just included), chosen uniformly — declared: N//2 (excluded) uniformly,
        # the simpler of the two standard choices and the one E20 itself is silent on.
        self.state = torch.full((C, 2 * n_features), N // 2, dtype=torch.int32)
        self.polarity = torch.tensor([1 if j % 2 == 0 else -1 for j in range(C)], dtype=torch.int32)
        self._pos_mask = self.polarity > 0
        self._draw_index = 0  # only used by the toy's OWN convenience seeding; feedback() takes its own gen

    # -- inference ---------------------------------------------------------------------------
    def _literals(self, x_bits: torch.Tensor) -> torch.Tensor:
        return torch.cat([x_bits, 1 - x_bits])  # (2F,)

    def clause_outputs(self, x_bits: torch.Tensor, training: bool) -> torch.Tensor:
        action = self.state > (self.N // 2)  # (C, 2F)
        lit = self._literals(x_bits).unsqueeze(0)  # (1, 2F)
        satisfied = (lit == 1) | (~action)  # not-included literals never block firing
        all_satisfied = satisfied.all(dim=1)  # (C,)
        vacuous = (~action).all(dim=1)
        out = all_satisfied.int()
        fill = torch.ones_like(out) if training else torch.zeros_like(out)
        return torch.where(vacuous, fill, out)

    def vote(self, x_bits: torch.Tensor) -> torch.Tensor:
        out = self.clause_outputs(x_bits, training=False)
        return (out.int() * self.polarity).sum()

    # -- feedback (E20's formula; the standard multi-class TM rule) --------------------------
    def _type1(self, x_bits: torch.Tensor, outputs: torch.Tensor, active: torch.Tensor, gen: torch.Generator) -> None:
        action = self.state > (self.N // 2)
        lit = self._literals(x_bits).unsqueeze(0)
        fired = outputs.bool().unsqueeze(1)
        r = torch.rand(self.state.shape, generator=gen)
        reward = fired & (lit == 1) & (r < (self.s - 1) / self.s) & active.unsqueeze(1)
        penalize_fired = fired & (lit == 0) & (r < 1.0 / self.s) & active.unsqueeze(1)
        penalize_idle = (~fired) & (r < 1.0 / self.s) & active.unsqueeze(1)
        delta = reward.int() - (penalize_fired | penalize_idle).int()
        self.state = torch.clamp(self.state + delta, 1, self.N)

    def _type2(self, x_bits: torch.Tensor, outputs: torch.Tensor, active: torch.Tensor) -> None:
        action = self.state > (self.N // 2)
        lit = self._literals(x_bits).unsqueeze(0)
        fired = outputs.bool().unsqueeze(1)
        inc = fired & (lit == 0) & (~action) & active.unsqueeze(1)
        self.state = torch.clamp(self.state + inc.int(), 1, self.N)

    def train(self, x_bits: torch.Tensor, y_c: bool, gen: torch.Generator) -> None:
        v = float(torch.clamp(self.vote(x_bits), -self.T, self.T))
        p_feedback = (self.T - v) / (2 * self.T) if y_c else (self.T + v) / (2 * self.T)
        if float(torch.rand((), generator=gen)) >= p_feedback:
            return
        outputs = self.clause_outputs(x_bits, training=True)
        if y_c:
            self._type1(x_bits, outputs, active=self._pos_mask, gen=gen)
            self._type2(x_bits, outputs, active=~self._pos_mask)
        else:
            self._type2(x_bits, outputs, active=self._pos_mask)
            self._type1(x_bits, outputs, active=~self._pos_mask, gen=gen)

    def state_dict(self) -> dict:
        return {"state": self.state.clone()}

    def load_state_dict(self, d: dict) -> None:
        self.state = d["state"].clone()

    # -- rule() reduced form (PREREG: "E20's lossless reduced form") -------------------------
    # Unlike E20's ordinal/thermometer features, our literals are ALREADY pure Booleans — no
    # interval-box collapsing is needed for losslessness; the reduction here is simply: list
    # each clause's INCLUDED literals (dropping the ones a vacuous clause has none of — such a
    # clause never fires at prediction time by the convention above, so it is dropped from the
    # READABLE text without changing any prediction, proven by the identity test comparing this
    # bank's clause_outputs against a re-evaluation of the printed literal lists).
    def reduced_clauses(self, feature_names: Optional[Sequence[str]] = None) -> List[Dict]:
        action = self.state > (self.N // 2)
        out = []
        for j in range(self.C):
            lits = []
            for k in range(self.n_features):
                name = feature_names[k] if feature_names else f"bit_{k}"
                if action[j, k]:
                    lits.append(name)
                if action[j, self.n_features + k]:
                    lits.append(f"NOT {name}")
            out.append({"clause": j, "polarity": int(self.polarity[j]), "literals": lits, "vacuous": len(lits) == 0})
        return out


class MultiClassTsetlinMachine:
    """A1/A2/A3's shared multi-class shape: one TsetlinClauseBank per class, classes growing as
    names are heard (PREREG: 'A3's classes grow as names are heard'), plus two fixed classes
    (YES, NO). A compound cue sets both marks' bits (the Arm wrapper's job, at encoding time)."""

    def __init__(self, n_features: int, C: int, N: int, T: int, s: float, seed: int, name_cap: int):
        self.n_features = n_features
        self.C, self.N, self.T, self.s = C, N, T, s
        self.seed = seed
        self.name_cap = name_cap
        self.names: List[str] = []
        self.banks: Dict[str, TsetlinClauseBank] = {
            "YES": TsetlinClauseBank(n_features, C, N, T, s, seed, "tm_yes"),
            "NO": TsetlinClauseBank(n_features, C, N, T, s, seed, "tm_no"),
        }

    def hear_name(self, name: str) -> None:
        if name in self.names or len(self.names) >= self.name_cap:
            return
        self.names.append(name)
        self.banks[name] = TsetlinClauseBank(self.n_features, self.C, self.N, self.T, self.s, self.seed, f"tm_name_{name}")

    def class_names(self) -> List[str]:
        return list(self.names) + ["YES", "NO"]

    def votes(self, x_bits: torch.Tensor) -> Dict[str, int]:
        return {c: int(bank.vote(x_bits)) for c, bank in self.banks.items()}

    def train_event(self, x_bits: torch.Tensor, target_class: str, event_seq: int, eligible: Optional[Sequence[str]] = None) -> None:
        """`eligible`, if given, restricts training to that subset of banks (D-earlier: an
        Arm wrapper scopes training by ANSWER-KIND FAMILY — training NAME's banks on a YESNO
        event, or vice versa, would contaminate a class with negative examples from a totally
        different question shape; PREREG does not name this explicitly, RAISED to the seat,
        and resolved conservatively here by scoping)."""
        gen = new_generator(self.seed, "tm", event_seq)
        targets = self.banks if eligible is None else {c: self.banks[c] for c in eligible}
        for c, bank in targets.items():
            bank.train(x_bits, y_c=(c == target_class), gen=gen)

    def state_dict(self) -> dict:
        return {"names": list(self.names), "banks": {c: b.state_dict() for c, b in self.banks.items()}}

    def load_state_dict(self, d: dict) -> None:
        self.names = list(d["names"])
        for name in self.names:
            if name not in self.banks:
                self.banks[name] = TsetlinClauseBank(self.n_features, self.C, self.N, self.T, self.s, self.seed, f"tm_name_{name}")
        for c, bd in d["banks"].items():
            self.banks[c].load_state_dict(bd)

    def state_sha_bytes(self) -> bytes:
        parts = [repr(self.names).encode()]
        for c in sorted(self.banks):
            parts.append(c.encode())
            parts.append(self.banks[c].state.numpy().tobytes())
        return b"|".join(parts)


class TwoClassMatchMachine:
    """PICK's own scorer (PREREG's shared A2/A3 note): 'a second, two-class machine
    (MATCH/NO-MATCH) of the same C, T, s' — a single TsetlinClauseBank pair (MATCH vs
    NO-MATCH), scored per (cue, operand, candidate) triple the Arm wrapper encodes as one
    bit-vector; the highest MATCH-vs-NO-MATCH margin among a PICK's candidates wins."""

    def __init__(self, n_features: int, C: int, N: int, T: int, s: float, seed: int):
        self.match = TsetlinClauseBank(n_features, C, N, T, s, seed, "tm_match")
        self.no_match = TsetlinClauseBank(n_features, C, N, T, s, seed, "tm_nomatch")
        self.seed = seed

    def score(self, x_bits: torch.Tensor) -> int:
        return int(self.match.vote(x_bits)) - int(self.no_match.vote(x_bits))

    def train_event(self, x_bits: torch.Tensor, is_match: bool, event_seq: int) -> None:
        gen = new_generator(self.seed, "tm_pick", event_seq)
        self.match.train(x_bits, y_c=is_match, gen=gen)
        self.no_match.train(x_bits, y_c=(not is_match), gen=gen)

    def state_dict(self) -> dict:
        return {"match": self.match.state_dict(), "no_match": self.no_match.state_dict()}

    def load_state_dict(self, d: dict) -> None:
        self.match.load_state_dict(d["match"])
        self.no_match.load_state_dict(d["no_match"])

    def state_sha_bytes(self) -> bytes:
        return self.match.state.numpy().tobytes() + b"|" + self.no_match.state.numpy().tobytes()


def param_count(n_features: int, C: int, n_classes: int) -> int:
    """Automaton count (each an int in [1,N], not a float parameter — reported separately from
    the PyTorch arms' parameter counts, which this file's report states explicitly)."""
    return n_classes * C * 2 * n_features
