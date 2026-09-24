"""compress.py — arm D's Stitch-shaped compressor: top-k abstractions by compression gain per sleep (report §3).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — candidate abstractions = the anti-unifiers of every
pair of subtree occurrences in the corpus; gain = (corpus size before − after rewriting every match top-down,
leftmost-outermost, non-overlapping) − the body's size; greedy top-k (ties → smaller body, then its text).

An abstraction is CLOSED: a program input (x0, x1, cands) or a bound variable whose binder lies outside the pattern
is always a hole; a hole may not sit where its filler would capture a binder INSIDE the pattern. Fillers are stored
relative to the call site (shifted down by the pattern depth they sat at).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from . import dsl
from .dsl import Sig

MIN_BODY = 2      # non-hole symbols in an abstraction's body
MAX_HOLES = 3     # arity bound
TOP_K = 3         # abstractions added per sleep at most


# ---------------------------------------------------------------------------------------------- typing
class Typer:
    """Types of subtrees, given the base spec, the abstractions' and cue ops' signatures."""

    def __init__(self, abs_sigs: Dict[str, Sig], cue_sigs: Dict[str, Sig]):
        self.abs_sigs = abs_sigs
        self.cue_sigs = cue_sigs

    def type_of(self, tree: tuple, env: Tuple[str, ...], inputs: Dict[str, str]) -> str:
        tok = tree[0]
        if dsl.is_bvar(tok):
            return env[-1 - dsl.bvar_index(tok)]
        if dsl.is_input(tok):
            return inputs[tok]
        if tok in dsl.BASE_SPEC:
            return dsl.BASE_SPEC[tok][0]
        if dsl.is_abs(tok):
            return self.abs_sigs[tok].out
        if dsl.is_cue_op(tok):
            return self.cue_sigs[tok[1:]].out
        raise ValueError(f"cannot type {tok!r}")

    def child_envs(self, tree: tuple, env: Tuple[str, ...], inputs: Dict[str, str]) -> List[Tuple[str, ...]]:
        """The binder environment of each child (a binder's body gains the list's element type)."""
        tok = tree[0]
        out = []
        for i, c in enumerate(tree[1:]):
            if tok in dsl.BINDERS and i == 1:
                lt = self.type_of(tree[1], env, inputs)
                out.append(env + (dsl.ELEM[lt],))
            else:
                out.append(env)
        return out


# ---------------------------------------------------------------------------------------------- anti-unification
def _hole_ok(t: tuple, depth: int) -> bool:
    """A filler at pattern depth `depth` may not read a binder inside the pattern (index < depth)."""
    return all(k >= depth for k in dsl.free_bvars(t))


def anti_unify(u: tuple, v: tuple, depth: int, pairs: Dict[tuple, int], hole_types: Dict[int, str],
               typer: Typer, env_u: tuple, in_u: Dict[str, str]) -> Optional[tuple]:
    tu, tv = u[0], v[0]
    make_hole = False
    if dsl.is_input(tu) or dsl.is_input(tv):
        make_hole = True
    elif dsl.is_bvar(tu) or dsl.is_bvar(tv):
        if u == v and dsl.bvar_index(tu) < depth:
            return u
        make_hole = True
    elif tu != tv or len(u) != len(v):
        make_hole = True
    if make_hole:
        if not (_hole_ok(u, depth) and _hole_ok(v, depth)):
            return None
        fu, fv = dsl.shift(u, -depth), dsl.shift(v, -depth)
        key = (fu, fv)
        if key not in pairs:
            pairs[key] = len(pairs)
            hole_types[pairs[key]] = typer.type_of(u, env_u, in_u)
        return (f"#{pairs[key]}",)
    kids = []
    envs = typer.child_envs(u, env_u, in_u)
    for i in range(1, len(u)):
        d2 = depth + 1 if (tu in dsl.BINDERS and i == 2) else depth
        k = anti_unify(u[i], v[i], d2, pairs, hole_types, typer, envs[i - 1], in_u)
        if k is None:
            return None
        kids.append(k)
    return (tu,) + tuple(kids)


def body_size(pattern: tuple) -> int:
    return sum(1 for t in dsl.tokens(pattern) if not dsl.is_hole(t))


# ---------------------------------------------------------------------------------------------- matching / rewriting
def match(pattern: tuple, t: tuple, depth: int, binds: Dict[int, tuple]) -> bool:
    pt = pattern[0]
    if dsl.is_hole(pt):
        if not _hole_ok(t, depth):
            return False
        f = dsl.shift(t, -depth)
        i = dsl.hole_index(pt)
        if i in binds:
            return binds[i] == f
        binds[i] = f
        return True
    if pt != t[0] or len(pattern) != len(t):
        return False
    for i in range(1, len(pattern)):
        d2 = depth + 1 if (pt in dsl.BINDERS and i == 2) else depth
        if not match(pattern[i], t[i], d2, binds):
            return False
    return True


def rewrite(tree: tuple, pattern: tuple, token: str, arity: int) -> tuple:
    binds: Dict[int, tuple] = {}
    if match(pattern, tree, 0, binds):
        return (token,) + tuple(rewrite(binds[i], pattern, token, arity) for i in range(arity))
    return (tree[0],) + tuple(rewrite(c, pattern, token, arity) for c in tree[1:])


# ---------------------------------------------------------------------------------------------- the step
class Program:
    """One corpus entry: a cue's current program and its input types."""
    __slots__ = ("key", "tree", "inputs")

    def __init__(self, key: str, tree: tuple, inputs: Dict[str, str]):
        self.key, self.tree, self.inputs = key, tree, inputs


def candidates(corpus: Sequence[Program], typer: Typer) -> Dict[str, Tuple[tuple, Sig]]:
    """Every admissible anti-unifier of two distinct subtree occurrences, keyed by the body's text key."""
    occ = []
    for pi, p in enumerate(corpus):
        if p.tree[0] == "compose":
            continue
        stack = [(p.tree, (), ())]
        # walk with binder environments
        def walk(t, env, path):
            occ.append((pi, path, t, env, p.inputs))
            envs = typer.child_envs(t, env, p.inputs) if len(t) > 1 else []
            for i, c in enumerate(t[1:]):
                walk(c, envs[i], path + (i,))
        walk(p.tree, (), ())
    out: Dict[str, Tuple[tuple, Sig]] = {}
    for a in range(len(occ)):
        _pa, _patha, u, env_u, in_u = occ[a]
        if len(u) == 1:
            continue
        for b in range(a + 1, len(occ)):
            _pb, _pathb, v, _env_v, _in_v = occ[b]
            if len(v) == 1 or u[0] != v[0]:
                continue
            pairs: Dict[tuple, int] = {}
            hole_types: Dict[int, str] = {}
            pat = anti_unify(u, v, 0, pairs, hole_types, typer, env_u, in_u)
            if pat is None or len(pairs) > MAX_HOLES or body_size(pat) < MIN_BODY:
                continue
            key = dsl.text_key(pat)
            if key in out:
                continue
            out_type = typer.type_of(u, env_u, in_u)
            sig = Sig([hole_types[i] for i in range(len(pairs))], out_type)
            out[key] = (pat, sig)
    return out


def corpus_size(corpus: Sequence[Program]) -> int:
    return sum(dsl.size(p.tree) for p in corpus)


def gain(corpus: Sequence[Program], pattern: tuple, arity: int) -> int:
    before = corpus_size(corpus)
    after = 0
    for p in corpus:
        if p.tree[0] == "compose":
            after += dsl.size(p.tree)
        else:
            after += dsl.size(rewrite(p.tree, pattern, "f?", arity))
    return (before - after) - body_size(pattern)


def compress(corpus: List[Program], typer: Typer, next_index: int, top_k: int = TOP_K):
    """Greedy top-k. Returns (added: [(token, pattern, sig, gain)], rewritten corpus)."""
    added = []
    corpus = list(corpus)
    for step in range(top_k):
        cands = candidates(corpus, typer)
        best = None
        for key in sorted(cands):
            pat, sig = cands[key]
            g = gain(corpus, pat, len(sig.ins))
            if g <= 0:
                continue
            rank = (-g, body_size(pat), key)
            if best is None or rank < best[0]:
                best = (rank, pat, sig, g)
        if best is None:
            break
        _rank, pat, sig, g = best
        token = f"f{next_index + len(added)}"
        typer.abs_sigs[token] = sig
        new = []
        for p in corpus:
            if p.tree[0] == "compose":
                new.append(p)
            else:
                new.append(Program(p.key, rewrite(p.tree, pat, token, len(sig.ins)), p.inputs))
        corpus = new
        added.append((token, pat, sig, g))
    return added, corpus
