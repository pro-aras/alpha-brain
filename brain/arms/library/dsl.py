"""dsl.py — arm D's typed DSL: types, symbols, program trees, text and JSON forms (B1-PREREG.md §4 row D).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — the DSL of docs/briefs/B1-BUILDER1-REPORT.md §2.

A PROGRAM is an immutable tree of nested tuples `(token, child, child, ...)`; a leaf is `(token,)`. Tokens:
  base primitives  order taught sim argmaxN argmaxG maxofN maxofG eq index_of nthN nthG add sub 0 1 not and or b2r
  inputs           x0 x1 x2 ... (the ask's operands, in order) and cands (a PICK ask's sheet)
  bound variables  $0 $1 ... (de Bruijn: $0 = the innermost enclosing binder)
  holes            #0 #1 ... (only inside a library abstraction's body)
  abstractions     f0 f1 ... (library entries made by compression; their children are the hole fillers)
  cue ops          @<key>   (the CURRENT program of a fitted cue, applied: its children are its inputs)
  cue references   &<key>   (the same, as an argument of compose — never applied directly)
  compose          compose(F, F) (a whole-program form over cue references; see report §2.3)
The only binders: argmaxN, argmaxG, maxofN, maxofG — their child 1 is a BODY with one new bound variable of the
list's element type. Size = the number of tokens (binders are forced by the type and not counted).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------------------------- types
G, N, Z, R, B, LG, LN, F = "G", "N", "Z", "R", "B", "LG", "LN", "F"
ELEM = {LG: G, LN: N}

# ---------------------------------------------------------------------------------------------- the base
# (token, result type, argument specs). An argument spec is a type, or ("bind", var_type, body_type).
# The ORDER of this list is the declared lexicographic token order of the base (report §2.4).
BASE: Tuple[Tuple[str, str, tuple], ...] = (
    ("order", LN, ()),
    ("taught", LG, (N,)),
    ("sim", R, (G, G)),
    ("argmaxN", N, (LN, ("bind", N, R))),
    ("argmaxG", G, (LG, ("bind", G, R))),
    ("maxofN", R, (LN, ("bind", N, R))),
    ("maxofG", R, (LG, ("bind", G, R))),
    ("eq", B, (N, N)),
    ("index_of", Z, (LN, N)),
    ("nthN", N, (LN, Z)),
    ("nthG", G, (LG, Z)),
    ("add", Z, (Z, Z)),
    ("sub", Z, (Z, Z)),
    ("0", Z, ()),
    ("1", Z, ()),
    ("not", B, (B,)),
    ("and", B, (B, B)),
    ("or", B, (B, B)),
    ("b2r", R, (B,)),
)
BASE_SPEC: Dict[str, Tuple[str, tuple]] = {t: (rt, args) for t, rt, args in BASE}
BINDERS = frozenset({"argmaxN", "argmaxG", "maxofN", "maxofG"})

# ranks — the declared token order (report §2.4): base < abstractions < cue ops < compose < inputs < bound vars
RANK_BASE = 0
RANK_ABS = 1_000
RANK_CUE = 100_000
RANK_COMPOSE = 900_000
RANK_INPUT = 1_000_000
RANK_BVAR = 2_000_000


def is_bvar(tok: str) -> bool:
    return tok.startswith("$")


def bvar_index(tok: str) -> int:
    return int(tok[1:])


def is_hole(tok: str) -> bool:
    return tok.startswith("#")


def hole_index(tok: str) -> int:
    return int(tok[1:])


def is_input(tok: str) -> bool:
    return tok == "cands" or (tok.startswith("x") and tok[1:].isdigit())


def is_abs(tok: str) -> bool:
    return tok.startswith("f") and tok[1:].isdigit()


def is_cue_op(tok: str) -> bool:
    return tok.startswith("@")


def is_cue_ref(tok: str) -> bool:
    return tok.startswith("&")


def input_rank(tok: str) -> int:
    return RANK_INPUT + (10_000 if tok == "cands" else int(tok[1:]))


# ---------------------------------------------------------------------------------------------- signatures
class Sig:
    """A function signature: input types in order -> output type. Used for cue keys and abstractions."""
    __slots__ = ("ins", "out")

    def __init__(self, ins: Sequence[str], out: str):
        self.ins = tuple(ins)
        self.out = out

    def __eq__(self, other):
        return isinstance(other, Sig) and self.ins == other.ins and self.out == other.out

    def __hash__(self):
        return hash((self.ins, self.out))

    def __repr__(self):
        return f"Sig({','.join(self.ins)}->{self.out})"


ANSWER_TYPE = {"NAME": N, "PICK": G, "YESNO": B}


def cue_key(cue: str, operand_types: Sequence[str], has_cands: bool, answer_kind: str) -> str:
    """The canonical key of one cue asked in one shape, e.g. AFTER(G)>NAME, POINT(N;cands)>PICK."""
    ins = ",".join(operand_types) + (";cands" if has_cands else "")
    return f"{cue}({ins})>{answer_kind}"


def parse_cue_key(key: str) -> Tuple[str, Tuple[str, ...], bool, str]:
    cue, rest = key.split("(", 1)
    ins, kind = rest.split(")>", 1)
    has_cands = ins.endswith(";cands") or ins == ";cands"
    ins = ins[: -len(";cands")] if has_cands else ins
    ops = tuple(t for t in ins.split(",") if t)
    return cue, ops, has_cands, kind


def key_sig(key: str) -> Sig:
    _cue, ops, has_cands, kind = parse_cue_key(key)
    ins = list(ops) + ([LG] if has_cands else [])
    return Sig(ins, ANSWER_TYPE[kind])


def key_input_tokens(key: str) -> Tuple[str, ...]:
    """The input tokens of a program for this key, in the order of key_sig(key).ins."""
    _cue, ops, has_cands, _kind = parse_cue_key(key)
    toks = [f"x{i}" for i in range(len(ops))]
    if has_cands:
        toks.append("cands")
    return tuple(toks)


# ---------------------------------------------------------------------------------------------- trees
def leaf(tok: str) -> tuple:
    return (tok,)


def size(tree: tuple) -> int:
    return 1 + sum(size(c) for c in tree[1:])


def tokens(tree: tuple) -> List[str]:
    out = [tree[0]]
    for c in tree[1:]:
        out.extend(tokens(c))
    return out


def text_key(tree: tuple) -> str:
    """A canonical one-line key of a tree (prefix tokens with arity brackets) — the memo and JSON identity."""
    if len(tree) == 1:
        return tree[0]
    return tree[0] + "(" + " ".join(text_key(c) for c in tree[1:]) + ")"


def to_json(tree: tuple) -> list:
    return [tree[0]] + [to_json(c) for c in tree[1:]]


def from_json(obj) -> tuple:
    return (str(obj[0]),) + tuple(from_json(c) for c in obj[1:])


def free_bvars(tree: tuple, depth: int = 0) -> frozenset:
    """Bound-variable references that ESCAPE the tree, as indices relative to the tree's root
    (a $k at binder depth d inside the tree escapes iff k >= d, and is reported as k - d)."""
    tok = tree[0]
    if is_bvar(tok):
        k = bvar_index(tok)
        return frozenset({k - depth}) if k >= depth else frozenset()
    out = frozenset()
    for i, c in enumerate(tree[1:]):
        d = depth + 1 if (tok in BINDERS and i == 1) else depth
        out = out | free_bvars(c, d)
    return out


def has_inputs(tree: tuple) -> bool:
    if is_input(tree[0]):
        return True
    return any(has_inputs(c) for c in tree[1:])


def shift(tree: tuple, delta: int, cutoff: int = 0) -> tuple:
    """Add delta to every bound-variable index >= cutoff (cutoff grows under binders)."""
    tok = tree[0]
    if is_bvar(tok):
        k = bvar_index(tok)
        return (f"${k + delta}",) if k >= cutoff else tree
    kids = []
    for i, c in enumerate(tree[1:]):
        cut = cutoff + 1 if (tok in BINDERS and i == 1) else cutoff
        kids.append(shift(c, delta, cut))
    return (tok,) + tuple(kids)


def refs(tree: tuple, prefix: str) -> List[str]:
    """Every token in the tree starting with `prefix` (e.g. '@' cue ops, '&' cue refs, 'f' abstractions)."""
    out = []
    if tree[0].startswith(prefix) and (prefix != "f" or is_abs(tree[0])):
        out.append(tree[0])
    for c in tree[1:]:
        out.extend(refs(c, prefix))
    return out


def subtrees(tree: tuple, path: Tuple[int, ...] = (), depth: int = 0):
    """Every (path, depth, subtree) in prefix order; depth = binders between the program root and the subtree."""
    yield path, depth, tree
    tok = tree[0]
    for i, c in enumerate(tree[1:]):
        d = depth + 1 if (tok in BINDERS and i == 1) else depth
        yield from subtrees(c, path + (i,), d)


def render(tree: tuple, names: Optional[List[str]] = None) -> str:
    """Readable text: binders get letter names (a, b, c ... by depth), holes stay #i."""
    names = list(names or [])
    tok = tree[0]
    if is_bvar(tok):
        k = bvar_index(tok)
        return names[-1 - k] if k < len(names) else tok
    if len(tree) == 1:
        return tok
    parts = []
    for i, c in enumerate(tree[1:]):
        if tok in BINDERS and i == 1:
            v = "abcdefghijklmnopqrstuvwxyz"[len(names) % 26] + ("" if len(names) < 26 else str(len(names) // 26))
            parts.append(f"λ{v}. " + render(c, names + [v]))
        else:
            parts.append(render(c, names))
    return f"{tok}(" + ", ".join(parts) + ")"
