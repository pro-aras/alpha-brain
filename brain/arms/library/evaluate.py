"""evaluate.py — arm D's column-wise evaluator (report §2.7).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — values are arrays over a batch of examples with a
validity mask (a raise on one example marks that example only); every real value (a `sim`, a `b2r`) is an EXACT
int64 in units of 2**-52, so no answer depends on the batch, the order of a reduction, or the process.

Semantics (report §2.3): argmax/maxof over a list evaluate the body on every element (a raise on any PRESENT
element raises the whole call for that example; an empty list raises; ties go to the FIRST element — repeats are
evaluated once, in first-occurrence order, which is exact); index_of = the first occurrence, absent raises; nth is
0-based, negative or past the end raises; an abstraction or a cue op is applied call-by-value; compose bridges a
NAME into a GLYPH slot through the name's first TEACH exemplar.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import dsl

SCALE_BITS = 26                     # F_pool components are rounded to multiples of 2**-26 ...
SIM_ONE = 1 << (2 * SCALE_BITS)     # ... so a cosine of 1.0 is 2**52 in the exact integer dot
B2R_TRUE = SIM_ONE                  # b2r(true) = 1.0 in the same units
MEMO_CAP = 120_000                  # a memo past this many entries is cleared whole (pure values: safe)


class EvalError(Exception):
    """A program that cannot be evaluated at all (a malformed tree) — never a per-example raise."""


# ---------------------------------------------------------------------------------------------- values
class Val:
    """A scalar-per-example value. const: `v` is a Python int (or bool) and `ok` a bool; else `v` is an (n,)
    array and `ok` an (n,) bool array."""
    __slots__ = ("const", "v", "ok")

    def __init__(self, const: bool, v, ok):
        self.const, self.v, self.ok = const, v, ok


class LVal:
    """A list value. const: `items` a tuple of ints, `ok` a bool; else `mat` (n, K) int64 padded with 0, `lens` (n,)
    int64 and `ok` (n,) bool."""
    __slots__ = ("const", "items", "mat", "lens", "ok")

    def __init__(self, const: bool, items=None, mat=None, lens=None, ok=True):
        self.const, self.items, self.mat, self.lens, self.ok = const, items, mat, lens, ok


def _col(val: Val, n: int, dtype=np.int64) -> Tuple[np.ndarray, np.ndarray]:
    if val.const:
        return (np.full(n, val.v, dtype=dtype), np.full(n, bool(val.ok), dtype=bool))
    return val.v, val.ok


# ---------------------------------------------------------------------------------------------- the data context
class Data:
    """What a program may read besides its inputs: the quantized percepts and the data memory (order, taught).
    Built from D's state; immutable during one search or one answer."""

    def __init__(self, Q: np.ndarray, order: Sequence[int], taught: Dict[int, Sequence[int]], n_names: int):
        self.Q = Q                                   # (rows, 144) int64 — quantized F_pool per cache row
        self.order = tuple(int(x) for x in order)
        self.order_distinct = tuple(dict.fromkeys(self.order))
        self.n_names = max(int(n_names), 1)
        fi = np.full(self.n_names, -1, dtype=np.int64)
        for i, nid in enumerate(self.order):
            if fi[nid] < 0:
                fi[nid] = i
        self.first_index = fi
        self.taught = {int(k): tuple(int(r) for r in v) for k, v in taught.items()}
        kmax = max([len(v) for v in self.taught.values()] + [1])
        tp = np.zeros((self.n_names, kmax), dtype=np.int64)
        tl = np.zeros(self.n_names, dtype=np.int64)
        for nid, rows in self.taught.items():
            tp[nid, : len(rows)] = rows
            tl[nid] = len(rows)
        self.taught_pad, self.taught_len = tp, tl
        self.order_arr = np.array(self.order, dtype=np.int64) if self.order else np.zeros(0, dtype=np.int64)


class Batch:
    """The examples one program is scored on (or the single ask it answers): the inputs as columns."""

    def __init__(self, n: int, inputs: Dict[str, object]):
        self.n = int(n)
        self.inputs = inputs   # token -> Val (x_i) or LVal (cands)


# ---------------------------------------------------------------------------------------------- the evaluator
class Evaluator:
    """Evaluates program trees over one Batch against one Data, with the library's abstractions and the frozen cue
    programs of this search. `abstractions`: token -> (body tree, arity); `cue_programs`: key -> (tree, input
    tokens, sig)."""

    def __init__(self, data: Data, batch: Batch, abstractions: Dict[str, Tuple[tuple, int]],
                 cue_programs: Dict[str, Tuple[tuple, Tuple[str, ...], "dsl.Sig"]], memo: bool = True,
                 fast: bool = True):
        self.d, self.b = data, batch
        self.abs = abstractions
        self.cues = cue_programs
        self.memo_on = memo
        self.fast_on = fast   # the sim-body fast paths (exact: pinned equal to the loop by a test)
        self.memo: Dict[tuple, object] = {}
        self._free_cache: Dict[tuple, frozenset] = {}
        self.evals = 0

    # -- public ---------------------------------------------------------------------------------------------
    def run(self, tree: tuple):
        """The program's value over the batch (a Val, or an LVal for a list-typed tree)."""
        self.evals += 1
        if tree[0] == "compose":
            return self._apply_f(tree, self._top_operands(), self.b.inputs.get("cands"))
        return self._ev(tree, [], self.b.inputs, None, top=True)

    def _top_operands(self) -> List[object]:
        ops = []
        i = 0
        while f"x{i}" in self.b.inputs:
            ops.append(self.b.inputs[f"x{i}"])
            i += 1
        return ops

    # -- memo -----------------------------------------------------------------------------------------------
    def _free(self, tree: tuple) -> frozenset:
        f = self._free_cache.get(tree)
        if f is None:
            f = dsl.free_bvars(tree)
            self._free_cache[tree] = f
        return f

    # env entries: (value, descriptor) — descriptor ('c', int) for a constant binding, ('k', list_key, k) for the
    # k-th element of a per-example list whose own memo key is list_key; None when not describable.
    def _memo_key(self, tree: tuple, env: list) -> Optional[tuple]:
        free = self._free(tree)
        desc = []
        for k in sorted(free):
            if k >= len(env):
                return None
            d = env[-1 - k][1]
            if d is None:
                return None
            desc.append((k, d))
        return (tree, tuple(desc))

    # -- the recursive core ---------------------------------------------------------------------------------
    def _ev(self, tree: tuple, env: list, inputs: Dict[str, object], holes: Optional[List[object]], top: bool):
        key = None
        if top and self.memo_on and len(tree) > 1:
            key = self._memo_key(tree, env)
            if key is not None:
                hit = self.memo.get(key)
                if hit is not None:
                    return hit
        val = self._ev_node(tree, env, inputs, holes, top)
        if key is not None:
            if len(self.memo) >= MEMO_CAP:
                self.memo.clear()
            self.memo[key] = val
        return val

    def _ev_node(self, tree, env, inputs, holes, top):
        tok = tree[0]
        n = self.b.n
        d = self.d
        if dsl.is_bvar(tok):
            k = dsl.bvar_index(tok)
            return env[-1 - k][0]
        if dsl.is_hole(tok):
            return holes[dsl.hole_index(tok)]
        if dsl.is_input(tok):
            return inputs[tok]
        if tok == "0":
            return Val(True, 0, True)
        if tok == "1":
            return Val(True, 1, True)
        if tok == "order":
            return LVal(True, items=d.order, ok=True)
        if tok == "taught":
            nv = self._ev(tree[1], env, inputs, holes, top)
            if nv.const:
                if not nv.ok:
                    return LVal(True, items=(), ok=False)
                return LVal(True, items=d.taught.get(int(nv.v), ()), ok=True)
            idx = np.where(nv.ok, nv.v, 0)
            idx = np.clip(idx, 0, d.n_names - 1)
            known = (nv.v >= 0) & (nv.v < d.n_names)
            lens = np.where(known, d.taught_len[idx], 0)
            return LVal(False, mat=d.taught_pad[idx], lens=lens, ok=nv.ok.copy())
        if tok == "sim":
            a = self._ev(tree[1], env, inputs, holes, top)
            c = self._ev(tree[2], env, inputs, holes, top)
            return self._sim(a, c)
        if tok in ("argmaxN", "argmaxG", "maxofN", "maxofG"):
            return self._binder(tree, env, inputs, holes, top)
        if tok == "eq":
            a = self._ev(tree[1], env, inputs, holes, top)
            c = self._ev(tree[2], env, inputs, holes, top)
            if a.const and c.const:
                return Val(True, bool(a.v == c.v), bool(a.ok and c.ok))
            av, ao = _col(a, n)
            cv, co = _col(c, n)
            return Val(False, av == cv, ao & co)
        if tok == "index_of":
            lst = self._ev(tree[1], env, inputs, holes, top)
            nv = self._ev(tree[2], env, inputs, holes, top)
            return self._index_of(lst, nv)
        if tok in ("nthN", "nthG"):
            lst = self._ev(tree[1], env, inputs, holes, top)
            zv = self._ev(tree[2], env, inputs, holes, top)
            return self._nth(lst, zv)
        if tok in ("add", "sub"):
            a = self._ev(tree[1], env, inputs, holes, top)
            c = self._ev(tree[2], env, inputs, holes, top)
            if a.const and c.const:
                return Val(True, a.v + c.v if tok == "add" else a.v - c.v, bool(a.ok and c.ok))
            av, ao = _col(a, n)
            cv, co = _col(c, n)
            return Val(False, av + cv if tok == "add" else av - cv, ao & co)
        if tok == "not":
            a = self._ev(tree[1], env, inputs, holes, top)
            if a.const:
                return Val(True, not a.v, a.ok)
            return Val(False, ~a.v, a.ok)
        if tok in ("and", "or"):
            a = self._ev(tree[1], env, inputs, holes, top)
            c = self._ev(tree[2], env, inputs, holes, top)
            if a.const and c.const:
                v = (a.v and c.v) if tok == "and" else (a.v or c.v)
                return Val(True, bool(v), bool(a.ok and c.ok))
            av, ao = _col(a, n, bool)
            cv, co = _col(c, n, bool)
            return Val(False, (av & cv) if tok == "and" else (av | cv), ao & co)
        if tok == "b2r":
            a = self._ev(tree[1], env, inputs, holes, top)
            if a.const:
                return Val(True, B2R_TRUE if a.v else 0, a.ok)
            return Val(False, np.where(a.v, B2R_TRUE, 0).astype(np.int64), a.ok)
        if dsl.is_abs(tok):
            body, arity = self.abs[tok]
            args = [self._ev(c, env, inputs, holes, top) for c in tree[1:]]
            if len(args) != arity:
                raise EvalError(f"{tok} takes {arity} arguments, got {len(args)}")
            return self._ev(body, [], inputs, args, False)
        if dsl.is_cue_op(tok):
            key = tok[1:]
            prog, in_toks, _sig = self.cues[key]
            args = [self._ev(c, env, inputs, holes, top) for c in tree[1:]]
            sub_inputs = dict(zip(in_toks, args))
            return self._run_cue(prog, sub_inputs)
        raise EvalError(f"unknown token {tok!r}")

    def _run_cue(self, prog: tuple, sub_inputs: Dict[str, object]):
        if prog[0] == "compose":
            ops = []
            i = 0
            while f"x{i}" in sub_inputs:
                ops.append(sub_inputs[f"x{i}"])
                i += 1
            return self._apply_f(prog, ops, sub_inputs.get("cands"))
        return self._ev(prog, [], sub_inputs, None, False)

    # -- compose ----------------------------------------------------------------------------------------------
    def _f_sig(self, ftree: tuple) -> "dsl.Sig":
        tok = ftree[0]
        if dsl.is_cue_ref(tok):
            return self.cues[tok[1:]][2]
        raise EvalError("nested compose signature is resolved by the enumerator, not here")

    def _apply_f(self, ftree: tuple, operands: List[object], cands):
        """Apply a cue-level function (a cue reference or a compose) to operands (+ the ask's cands)."""
        tok = ftree[0]
        if dsl.is_cue_ref(tok):
            prog, in_toks, sig = self.cues[tok[1:]]
            sub = {}
            ops_toks = [t for t in in_toks if t != "cands"]
            if len(ops_toks) != len(operands):
                raise EvalError(f"{tok}: {len(ops_toks)} operands expected, {len(operands)} given")
            sub.update(zip(ops_toks, operands))
            if "cands" in in_toks:
                if cands is None:
                    raise EvalError(f"{tok} needs a candidate sheet")
                sub["cands"] = cands
            return self._run_cue(prog, sub)
        if tok != "compose":
            raise EvalError(f"not a cue-level function: {tok!r}")
        first = self._apply_f(ftree[1], operands, cands)
        want = self._operand_type(ftree[2])
        bridged = self._bridge(first, want)
        return self._apply_f(ftree[2], [bridged], cands)

    def _operand_type(self, ftree: tuple) -> str:
        """The type of the (single) operand a cue-level function takes."""
        tok = ftree[0]
        if dsl.is_cue_ref(tok):
            sig = self.cues[tok[1:]][2]
            ins = list(sig.ins)
            if ins and ins[-1] == dsl.LG:
                ins = ins[:-1]
            return ins[0]
        return self._operand_type(ftree[1])

    def _bridge(self, val: Val, want: str):
        # N -> G: the name's first TEACH exemplar; otherwise identity (the enumerator admits only these).
        if want != dsl.G:
            return val
        d = self.d
        n = self.b.n
        if val.const:
            rows = d.taught.get(int(val.v), ()) if val.ok else ()
            if not rows:
                return Val(True, 0, False)
            return Val(True, rows[0], bool(val.ok))
        v, ok = val.v, val.ok
        idx = np.clip(np.where(ok, v, 0), 0, d.n_names - 1)
        has = (d.taught_len[idx] > 0) & ok
        return Val(False, d.taught_pad[idx, 0].copy(), has)

    # -- primitives --------------------------------------------------------------------------------------------
    def _sim(self, a: Val, c: Val) -> Val:
        Q = self.d.Q
        if a.const and c.const:
            ok = bool(a.ok and c.ok)
            if not ok:
                return Val(True, 0, False)
            return Val(True, int(Q[int(a.v)] @ Q[int(c.v)]), True)
        if a.const or c.const:
            const, col = (a, c) if a.const else (c, a)
            rows = np.where(col.ok, col.v, 0)
            v = Q[rows] @ Q[int(const.v)] if const.ok else np.zeros(len(rows), dtype=np.int64)
            ok = col.ok & bool(const.ok)
            return Val(False, v, ok)
        ra = np.where(a.ok, a.v, 0)
        rc = np.where(c.ok, c.v, 0)
        v = np.einsum("ij,ij->i", Q[ra], Q[rc])
        return Val(False, v, a.ok & c.ok)

    def _index_of(self, lst: LVal, nv: Val) -> Val:
        d = self.d
        if not lst.const:
            raise EvalError("index_of on a per-example list")  # only `order` is an [N] list
        if lst.items is not d.order and lst.items != d.order:
            # an [N] list other than order cannot arise in this DSL; kept honest
            first = {}
            for i, x in enumerate(lst.items):
                first.setdefault(x, i)
            if nv.const:
                i = first.get(int(nv.v), -1)
                return Val(True, i, bool(nv.ok and i >= 0 and lst.ok))
            vals = np.array([first.get(int(x), -1) for x in nv.v], dtype=np.int64)
            return Val(False, vals, nv.ok & (vals >= 0) & bool(lst.ok))
        if nv.const:
            nid = int(nv.v)
            i = int(d.first_index[nid]) if (nv.ok and 0 <= nid < d.n_names) else -1
            return Val(True, i, bool(nv.ok and i >= 0))
        idx = np.clip(np.where(nv.ok, nv.v, 0), 0, d.n_names - 1)
        inrange = (nv.v >= 0) & (nv.v < d.n_names)
        vals = np.where(inrange, d.first_index[idx], -1)
        return Val(False, vals, nv.ok & (vals >= 0))

    def _nth(self, lst: LVal, zv: Val) -> Val:
        n = self.b.n
        if lst.const:
            items = lst.items
            m = len(items)
            if zv.const:
                z = int(zv.v)
                ok = bool(zv.ok and lst.ok and 0 <= z < m)
                return Val(True, items[z] if ok else 0, ok)
            arr = np.array(items, dtype=np.int64) if m else np.zeros(1, dtype=np.int64)
            z = zv.v
            inr = (z >= 0) & (z < m)
            safe = np.where(inr, z, 0)
            vals = arr[safe] if m else np.zeros(n, dtype=np.int64)
            return Val(False, vals, zv.ok & inr & bool(lst.ok))
        zc, zo = _col(zv, n)
        inr = (zc >= 0) & (zc < lst.lens)
        safe = np.where(inr, zc, 0)
        vals = lst.mat[np.arange(n), np.clip(safe, 0, lst.mat.shape[1] - 1)]
        return Val(False, vals, lst.ok & zo & inr)

    # -- the binders -------------------------------------------------------------------------------------------
    def _binder(self, tree, env, inputs, holes, top):
        tok = tree[0]
        want_arg = tok.startswith("argmax")
        lst = self._ev(tree[1], env, inputs, holes, top)
        body = tree[2]
        n = self.b.n
        fast = self._fast_sim_body(body) if self.fast_on else None
        if lst.const:
            items = tuple(dict.fromkeys(lst.items))
            if not lst.ok or not items:
                return Val(True, 0, False)
            if fast is not None and tok.endswith("G"):
                u = self._ev(dsl.shift(fast, -1, 0), env, inputs, holes, top)
                return self._fast_const(tok, u, items)
            list_key = None
            vals, oks = [], []
            all_const = True
            for it in items:
                env.append((Val(True, it, True), ("c", it)))
                r = self._ev(body, env, inputs, holes, top)
                env.pop()
                vals.append(r)
                all_const = all_const and r.const
            if all_const:
                if not all(bool(r.ok) for r in vals):
                    return Val(True, 0, False)
                best = max(range(len(items)), key=lambda i: (vals[i].v, -i))
                return Val(True, items[best] if want_arg else vals[best].v, True)
            V = np.stack([_col(r, n)[0] for r in vals], axis=1)
            O = np.stack([_col(r, n, bool)[1] for r in vals], axis=1)
            ok = O.all(axis=1)
            best = np.argmax(V, axis=1)            # the FIRST max per row
            if want_arg:
                return Val(False, np.array(items, dtype=np.int64)[best], ok)
            return Val(False, V[np.arange(n), best], ok)
        # a per-example list
        K = lst.mat.shape[1]
        if K == 0:
            return Val(False, np.zeros(n, dtype=np.int64), np.zeros(n, dtype=bool))
        lkey = self._memo_key(tree[1], env) if (top and self.memo_on) else None
        if fast is not None and tok.endswith("G"):
            u = self._ev(dsl.shift(fast, -1, 0), env, inputs, holes, top)
            return self._fast_col(tok, u, lst)
        V = np.zeros((n, K), dtype=np.int64)
        O = np.ones((n, K), dtype=bool)
        present = np.arange(K)[None, :] < lst.lens[:, None]
        for k in range(K):
            col = Val(False, lst.mat[:, k].copy(), lst.ok & present[:, k])
            desc = ("k", lkey, k) if lkey is not None else None
            env.append((col, desc))
            r = self._ev(body, env, inputs, holes, top)
            env.pop()
            rv, ro = _col(r, n)
            V[:, k] = rv
            O[:, k] = ro | ~present[:, k]
        ok = lst.ok & (lst.lens > 0) & O.all(axis=1)
        Vm = np.where(present, V, np.iinfo(np.int64).min)
        best = np.argmax(Vm, axis=1)
        if want_arg:
            return Val(False, lst.mat[np.arange(n), best], ok)
        return Val(False, Vm[np.arange(n), best], ok)

    @staticmethod
    def _fast_sim_body(body: tuple) -> Optional[tuple]:
        """If the body is sim(u, $0) or sim($0, u) with u not reading $0, return u (still at body depth)."""
        if body[0] != "sim":
            return None
        a, c = body[1], body[2]
        if c == ("$0",) and 0 not in dsl.free_bvars(a):
            return a
        if a == ("$0",) and 0 not in dsl.free_bvars(c):
            return c
        return None

    def _fast_const(self, tok: str, u: Val, items: Tuple[int, ...]) -> Val:
        Q = self.d.Q
        M = Q[np.array(items, dtype=np.int64)]              # (m, 144)
        if u.const:
            if not u.ok:
                return Val(True, 0, False)
            s = M @ Q[int(u.v)]                              # exact int64
            best = int(np.argmax(s))
            return Val(True, items[best] if tok.startswith("argmax") else int(s[best]), True)
        rows = np.where(u.ok, u.v, 0)
        S = Q[rows] @ M.T                                    # (n, m) exact int64
        best = np.argmax(S, axis=1)
        if tok.startswith("argmax"):
            return Val(False, np.array(items, dtype=np.int64)[best], u.ok.copy())
        return Val(False, S[np.arange(len(rows)), best], u.ok.copy())

    def _fast_col(self, tok: str, u: Val, lst: LVal) -> Val:
        Q = self.d.Q
        n = self.b.n
        K = lst.mat.shape[1]
        uc, uo = _col(u, n)
        rows = np.where(uo, uc, 0)
        S = np.einsum("nkd,nd->nk", Q[lst.mat], Q[rows])    # exact int64
        present = np.arange(K)[None, :] < lst.lens[:, None]
        Sm = np.where(present, S, np.iinfo(np.int64).min)
        best = np.argmax(Sm, axis=1)
        ok = lst.ok & uo & (lst.lens > 0)
        if tok.startswith("argmax"):
            return Val(False, lst.mat[np.arange(n), best], ok)
        return Val(False, Sm[np.arange(n), best], ok)


# ---------------------------------------------------------------------------------------------- scoring
def correct_mask(val: Val, answer_kind: str, right: np.ndarray, batch: Batch) -> np.ndarray:
    """Per example: did the program reproduce the shown right answer? right: NAME -> name ids; PICK -> the index
    into the ask's own sheet; YESNO -> bool."""
    n = batch.n
    if answer_kind == "NAME":
        v, ok = _col(val, n)
        return ok & (v == right)
    if answer_kind == "YESNO":
        v, ok = _col(val, n, bool)
        return ok & (v == right)
    if answer_kind == "PICK":
        v, ok = _col(val, n)
        c = batch.inputs["cands"]
        return ok & (pick_index(v, c) == right)
    raise EvalError(f"unknown answer kind {answer_kind!r}")


def pick_index(v: np.ndarray, cands: LVal) -> np.ndarray:
    """The index of each value in its example's own sheet (by row identity), -1 if absent — a G that is not a
    candidate never answers a PICK (report §2.5)."""
    K = cands.mat.shape[1]
    present = np.arange(K)[None, :] < cands.lens[:, None]
    hit = (cands.mat == v[:, None]) & present
    has = hit.any(axis=1)
    first = np.argmax(hit, axis=1)
    return np.where(has, first, -1)
