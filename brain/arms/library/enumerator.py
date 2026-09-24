"""enumerator.py — the grammar of one search and its size-then-lexicographic enumerator (report §2.4).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — token-by-token DFS over pending holes, a branch
pruned the moment the remaining size cannot fill them exactly; emits EXACTLY size-then-lexicographic order.

A GRAMMAR is the set of symbols one search may use: the base (dsl.BASE), the library abstractions, the cue ops
(other fitted cues, cycle-free), the request's inputs, the bound variables in scope, and — at the program's ROOT
only — compose over cue references. Nothing here reads a clock; nothing iterates a set.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from . import dsl
from .dsl import Sig


class Symbol:
    __slots__ = ("token", "rank", "rtype", "args")

    def __init__(self, token: str, rank: int, rtype: str, args: tuple):
        self.token, self.rank, self.rtype, self.args = token, rank, rtype, args

    def __repr__(self):
        return f"Symbol({self.token}:{self.rtype})"


def bridge_ok(src: str, dst: str) -> bool:
    """compose's bridge (report §2.3): identity when the types agree; a NAME into a GLYPH slot goes through the
    name's first TEACH exemplar; anything else is ill-typed."""
    return src == dst or (src == dsl.N and dst == dsl.G)


class Grammar:
    """The symbols one search may use. `abstractions`: [(token, Sig)] in creation order; `cue_ops`: [(key, Sig)]
    in the declared cue order (first example's seq); `inputs`: [(token, type)] of the request."""

    def __init__(self, abstractions: Sequence[Tuple[str, Sig]], cue_ops: Sequence[Tuple[str, Sig]],
                 inputs: Sequence[Tuple[str, str]], out_type: str, allow_compose: bool = True):
        self.out_type = out_type
        self.inputs = tuple(inputs)
        self.allow_compose = allow_compose and len(cue_ops) > 0
        syms: List[Symbol] = []
        for i, (tok, rt, args) in enumerate(dsl.BASE):
            syms.append(Symbol(tok, dsl.RANK_BASE + i, rt, args))
        for i, (tok, sig) in enumerate(abstractions):
            syms.append(Symbol(tok, dsl.RANK_ABS + i, sig.out, tuple(sig.ins)))
        self.cue_sigs: Dict[str, Sig] = {}
        self.cue_rank: Dict[str, int] = {}
        for i, (key, sig) in enumerate(cue_ops):
            syms.append(Symbol("@" + key, dsl.RANK_CUE + i, sig.out, tuple(sig.ins)))
            self.cue_sigs[key] = sig
            self.cue_rank[key] = dsl.RANK_CUE + i
        self.expr_syms = syms  # already in rank order by construction
        self.by_type: Dict[str, List[Symbol]] = {}
        for s in syms:
            self.by_type.setdefault(s.rtype, []).append(s)
        self.input_syms = [Symbol(tok, dsl.input_rank(tok), t, ()) for tok, t in self.inputs]
        self.input_syms.sort(key=lambda s: s.rank)
        self.ref_syms = [Symbol("&" + key, self.cue_rank[key], dsl.F, ()) for key, _ in cue_ops]
        self.compose_sym = Symbol("compose", dsl.RANK_COMPOSE, dsl.F, (dsl.F, dsl.F))
        self.arity: Dict[str, int] = {s.token: len(s.args) for s in syms}
        for s in self.input_syms + self.ref_syms:
            self.arity[s.token] = 0
        self.arity["compose"] = 2
        self._prod_cache: Dict[tuple, List[Tuple[str, tuple]]] = {}

    def token_arity(self, tok: str) -> int:
        if dsl.is_bvar(tok):
            return 0
        return self.arity[tok]

    # -- productions for one hole, in rank order ---------------------------------------------------
    def productions(self, htype: str, env: tuple, is_root: bool) -> List[Tuple[str, tuple]]:
        """[(token, arg_holes)] in rank order. A hole is (type, env, is_root). Cached per hole (pure)."""
        key = (htype, env, is_root)
        hit = self._prod_cache.get(key)
        if hit is None:
            hit = self._productions(htype, env, is_root)
            self._prod_cache[key] = hit
        return hit

    def _productions(self, htype: str, env: tuple, is_root: bool) -> List[Tuple[str, tuple]]:
        out: List[Tuple[str, tuple]] = []
        if htype == dsl.F:
            for s in self.ref_syms:
                out.append((s.token, ()))
            out.append(("compose", ((dsl.F, (), False), (dsl.F, (), False))))
            return out
        for s in self.by_type.get(htype, ()):
            holes = []
            for a in s.args:
                if isinstance(a, tuple):  # ("bind", var_type, body_type)
                    holes.append((a[2], env + (a[1],), False))
                else:
                    holes.append((a, env, False))
            out.append((s.token, tuple(holes)))
        if is_root and self.allow_compose:
            out.append(("compose", ((dsl.F, (), False), (dsl.F, (), False))))
        for s in self.input_syms:
            if s.rtype == htype:
                out.append((s.token, ()))
        for k in range(len(env)):
            if env[-1 - k] == htype:
                out.append((f"${k}", ()))
        return out

    # -- F-tree (compose) signatures ----------------------------------------------------------------
    def fsig(self, tree: tuple) -> Optional[Sig]:
        tok = tree[0]
        if dsl.is_cue_ref(tok):
            return self.cue_sigs.get(tok[1:])
        if tok != "compose":
            return None
        a, b = self.fsig(tree[1]), self.fsig(tree[2])
        if a is None or b is None:
            return None
        b_ops = [t for t in b.ins]
        b_cands = bool(b_ops) and b_ops[-1] == dsl.LG and len(b_ops) == 2
        b_operands = b_ops[:-1] if b_cands else b_ops
        if len(b_operands) != 1 or not bridge_ok(a.out, b_operands[0]):
            return None
        a_ops = list(a.ins)
        a_cands = bool(a_ops) and a_ops[-1] == dsl.LG
        ins = a_ops if a_cands else a_ops + ([dsl.LG] if b_cands else [])
        return Sig(ins, b.out)


class Enumerator:
    """Yields well-typed programs of the grammar's request in size-then-lexicographic order, up to max_size.
    `request_sig` is the request's own Sig (for checking root compose forms)."""

    def __init__(self, grammar: Grammar, request_sig: Sig, max_size: int):
        self.g = grammar
        self.request_sig = request_sig
        self.max_size = int(max_size)
        self._exact_cache: Dict[tuple, bool] = {}

    # exact(hole, s): can a subtree of exactly s tokens fill this hole?
    def _exact(self, hole: tuple, s: int) -> bool:
        key = (hole, s)
        hit = self._exact_cache.get(key)
        if hit is not None:
            return hit
        self._exact_cache[key] = False  # guards against pathological self-reference at equal size
        ok = False
        if s >= 1:
            for _tok, holes in self.g.productions(hole[0], hole[1], hole[2]):
                if self._sum_exact(holes, s - 1):
                    ok = True
                    break
        self._exact_cache[key] = ok
        return ok

    def _sum_exact(self, holes: tuple, k: int) -> bool:
        if not holes:
            return k == 0
        if k < len(holes):
            return False
        key = ("sum", holes, k)
        hit = self._exact_cache.get(key)
        if hit is not None:
            return hit
        ok = False
        first, rest = holes[0], holes[1:]
        for k1 in range(1, k - len(rest) + 1):
            if self._exact(first, k1) and self._sum_exact(rest, k - k1):
                ok = True
                break
        self._exact_cache[key] = ok
        return ok

    def exact_size(self, s: int) -> Iterator[tuple]:
        """Every well-typed program of exactly s tokens, lexicographic by token rank."""
        root = (self.g.out_type, (), True)
        toks: List[str] = []

        def rec(holes: tuple, remaining: int):
            if not holes:
                if remaining == 0:
                    yield tuple(toks)
                return
            hole, rest = holes[0], holes[1:]
            for tok, new in self.g.productions(hole[0], hole[1], hole[2]):
                need = new + rest
                if not self._sum_exact(need, remaining - 1):
                    continue
                toks.append(tok)
                yield from rec(need, remaining - 1)
                toks.pop()

        for seq in rec((root,), s):
            tree = self._build(seq)
            if tree[0] == "compose":
                sig = self.g.fsig(tree)
                if sig is None or sig != self.request_sig:
                    continue  # ill-typed compose: never a candidate
            yield tree

    def _build(self, seq: Sequence[str]) -> tuple:
        pos = 0

        def node():
            nonlocal pos
            tok = seq[pos]
            pos += 1
            n = self.g.token_arity(tok)
            return (tok,) + tuple(node() for _ in range(n))

        tree = node()
        assert pos == len(seq)
        return tree

    def programs(self, start_size: int = 1) -> Iterator[tuple]:
        for s in range(start_size, self.max_size + 1):
            yield from self.exact_size(s)

    def count_exact(self, s: int) -> int:
        """The number of programs of exactly s tokens (compose forms counted only if well-typed) — by walking the
        generator; used by tests and the report's counts, never inside a search."""
        return sum(1 for _ in self.exact_size(s))
