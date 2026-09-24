# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:49 +0400 — A4L-COST task 2 (docs/briefs/A4L-COST.md; #232's planted-offender law):
# THE WRITER SWEEP FOR THE BLOCK. The sparse witness (genome/witness.py) keeps ONE piece of incremental state for the edge block — the SET of
# masked coordinates — and re-reads every W/strikes/mask VALUE fresh on every call. So a VALUE write it is not told about is still seen, but a
# MASK write it is not told about leaves the set stale. This AST sweep pins, for every .py under genome/ and creature/: (1) every assignment
# into `.W[`/`.mask[`/`.strikes[` (plain, augmented, annotated, tuple targets), every rebinding of `.W`/`.mask`/`.strikes`, every `out=` into
# them and every in-place array method/np.* writer on them sits in a (file, function) the witness KNOWS, each with the reason it is safe;
# (2) every known function that writes the MASK in place either marks the witness (`.mark(` / `.mark_rows(`) or is one of the named
# rebuild points (allocation, capacity growth, load, the think's shadow copy); and (3) the append-only law the running digests rest on:
# `.cells` is written only by birth/grow/load/allocation/the shadow, and the four logs are only ever `.append`ed (or rebound at
# allocation/load/the shadow). A planted offender for each law is CAUGHT; a planted clean module is NOT flagged.
# edit: Claude (Opus 5.5, A4 seam-5 builder), 2026-09-23 14:52 +0400 — SEAM 5 (docs/ALPHA4-2-PREREG.md §7.2 on a42: COST x VOICE). The sweep now
# knows VOICE's writers of the two sound meetings (`_Pair` W/mask/strikes and their logs), each with its reason, and closes a blind spot it
# had: a write THROUGH A PARAMETER (`_merge_rows(W, M, ST, ...)` writes the arrays it is handed) was invisible to the attribute walk, so
# `Organism._area_merge` wrote the sight<->words MASK without marking the witness and the sweep could not see it. Two rules added: (4) a
# block array passed BARE to a callee that writes through one of its own parameters (or to a callee the tree does not define) is a write
# by the CALLER; (5) a known MASK writer tells the witness WHICH block: a write through `self.` (the organism's own sight<->words W) marks
# with no `pair=`, a write through any other receiver (a `_Pair`) marks with `pair=`. Planted offenders for both rules are CAUGHT.
"""test_a4l_cost_writer_sweep.py — every writer of the edge block, the cells and the logs is one the sparse witness knows."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

TREE = Path(__file__).resolve().parent.parent.parent
BLOCK = {"W", "mask", "strikes"}
LOGS = {"births", "merges", "edges_log", "prunes_log"}
INPLACE_METHODS = {"fill", "put", "itemset", "sort", "resize", "setfield", "partition", "byteswap"}
NP_WRITERS = {"copyto", "put", "place", "putmask", "put_along_axis", "fill_diagonal"}
LIST_MUTATORS = {"extend", "insert", "pop", "remove", "clear", "sort", "reverse", "__setitem__", "__delitem__", "__iadd__"}

# (file, qualified function) -> why the witness is safe with this writer. Every write site of the block must be HERE.
KNOWN_BLOCK: Dict[Tuple[str, str], str] = {
    ("genome/machinery.py", "Organism.__init__"): "allocation (zeros); the witness starts empty and scans the live block on its first call",
    ("genome/machinery.py", "Organism._grow_W"): "capacity only: the live block copied into bigger zero arrays; keys are s<<32|t, capacity-free; values read fresh",
    ("genome/machinery.py", "Organism._hebb"): "MASK: marks every row it wires",
    ("genome/machinery.py", "Organism._delta"): "VALUES only (masked W; the clip of a whole row/column moves no unmasked zero); read fresh every call",
    ("genome/machinery.py", "Organism._prune"): "MASK: marks every row holding a pruned edge; strikes VALUES read fresh",
    ("genome/machinery.py", "Organism._merge"): "MASK: marks rows a and b (sight) / every row of column b (words); W/strikes VALUES read fresh",
    ("genome/machinery.py", "Organism._scale"): "VALUES only (whole rows/columns scaled; an unmasked zero stays zero)",
    ("genome/machinery.py", "Organism.load"): "bulk write into a FRESH organism before its first row hash; the witness scans on its first call",
    ("creature/think_thread.py", "freeze_recall_view"): "the think's SHADOW (object.__new__): its own sliced copies; it carries no witness and is never hashed",
    # SEAM 5 — A4L-VOICE's two sound meetings (`_Pair`: rows = area a, cols = area b), each with the SAME reason its sight<->words twin has:
    ("genome/machinery.py", "_Pair.__init__"): "allocation (zeros) of a sound meeting; the witness scans each meeting's live block on its first digest",
    ("genome/machinery.py", "_Pair.grow"): "capacity only: the meeting's live block copied into bigger zero arrays; keys are r<<32|c, capacity-free; values read fresh",
    ("genome/machinery.py", "Organism._pair_hebb"): "a meeting's MASK: marks every row it wires (pair=)",
    ("genome/machinery.py", "Organism._pair_delta"): "VALUES only (masked W of a meeting; the clip of a whole row/column moves no unmasked zero); read fresh every call",
    ("genome/machinery.py", "Organism._pair_prune"): "a meeting's MASK: marks every row holding a pruned edge (pair=); strikes VALUES read fresh",
    ("genome/machinery.py", "Organism._scale_pairs"): "VALUES only (whole rows/columns of a meeting scaled; an unmasked zero stays zero)",
    ("genome/machinery.py", "Organism._area_merge"): "the sight<->words MASK through _merge_rows(self.W, self.mask, ...) (a sight or word cell merged in a sound meeting): marks rows a, b / every row of column b (no pair=)",
    ("genome/machinery.py", "Organism._merge_pair_edges"): "each sound meeting's MASK through _merge_rows(p.W, p.mask, ...) (a merged cell's meeting edges follow it): marks the rows _merge_rows reports (pair=)",
}
# the known writers that change the MASK in place and must tell the witness which rows
MUST_MARK = {("genome/machinery.py", "Organism._hebb"), ("genome/machinery.py", "Organism._prune"), ("genome/machinery.py", "Organism._merge"),
             ("genome/machinery.py", "Organism._pair_hebb"), ("genome/machinery.py", "Organism._pair_prune"),          # SEAM 5
             ("genome/machinery.py", "Organism._area_merge"), ("genome/machinery.py", "Organism._merge_pair_edges")}
# the known writers that may write the mask WITHOUT marking: each is a point where the witness has not been asked yet (it scans then)
REBUILD_POINTS = {("genome/machinery.py", "Organism.__init__"), ("genome/machinery.py", "Organism._grow_W"), ("genome/machinery.py", "Organism.load"),
                  ("creature/think_thread.py", "freeze_recall_view"),
                  ("genome/machinery.py", "_Pair.__init__"), ("genome/machinery.py", "_Pair.grow")}          # SEAM 5: a meeting's allocation / capacity
KNOWN_CELLS = {("genome/machinery.py", "Area.__init__"), ("genome/machinery.py", "Area.grow"), ("genome/machinery.py", "Organism._birth"),
               ("genome/machinery.py", "Organism.load"), ("creature/think_thread.py", "_freeze_area")}
KNOWN_LOG_REBIND = {("genome/machinery.py", "Organism.__init__"), ("genome/machinery.py", "Organism.load"), ("creature/think_thread.py", "freeze_recall_view"),
                    ("genome/machinery.py", "_Pair.__init__")}          # SEAM 5: a meeting's two EMPTY logs at allocation, before any digest


def _root_attr(node) -> str:
    """The attribute name a target is rooted at: `x.W[a][b]` -> 'W', `x.W` -> 'W', `x.W.T[...]` -> 'T' (a view by another name, not
    counted: none exists in the tree), else ''."""
    while isinstance(node, ast.Subscript):
        node = node.value
    return node.attr if isinstance(node, ast.Attribute) else ""


def _recv(node) -> str:
    """SEAM 5: the RECEIVER of the attribute a target is rooted at — `self.mask[s, t]` -> 'self', `p.mask[sel]` -> 'p', `org.W` -> 'org'
    (a non-Name receiver is rendered by ast.unparse). 'self' is the organism's own sight<->words block inside Organism's methods."""
    while isinstance(node, ast.Subscript):
        node = node.value
    if not isinstance(node, ast.Attribute):
        return ""
    return node.value.id if isinstance(node.value, ast.Name) else ast.unparse(node.value)


def _root_name(node) -> str:
    """The NAME a target is rooted at through subscripts and attributes: `M[a]` -> 'M', `W.T[0]` -> 'W', `self.x[0]` -> 'self'."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else ""


def _is_numpy_call(fn) -> bool:
    return isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id in ("np", "numpy")


def _callee_name(fn) -> str:
    return fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")


def param_writers(modules: List[Tuple[str, str]]) -> Dict[str, bool]:
    """SEAM 5 — the ALIAS road: for every function DEFINED in `modules`, by name: True iff it writes THROUGH one of its own parameters
    (a subscript / augmented / deleted target rooted at a parameter name, `out=` a parameter, an in-place method or np writer on one).
    `_merge_rows(W, M, ST, a, b, axis)` is the shape: it writes whatever arrays it is handed. Same-named functions are OR-ed (conservative)."""
    out: Dict[str, bool] = {}
    for _rel, source in modules:
        for fn in ast.walk(ast.parse(source)):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            a = fn.args
            params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs} | {x.arg for x in (a.vararg, a.kwarg) if x is not None}
            params -= {"self", "cls"}
            writes = False
            for n in ast.walk(fn):
                targets = []
                if isinstance(n, ast.Assign):
                    targets = list(n.targets)
                elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                    targets = [n.target]
                elif isinstance(n, ast.Delete):
                    targets = list(n.targets)
                flat = []
                for t in targets:
                    flat.extend(t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t])
                if any(isinstance(t, ast.Subscript) and _root_name(t) in params for t in flat):
                    writes = True
                if isinstance(n, ast.Call):
                    if any(kw.arg == "out" and _root_name(kw.value) in params for kw in n.keywords):
                        writes = True
                    f = n.func
                    if isinstance(f, ast.Attribute) and f.attr in INPLACE_METHODS and _root_name(f.value) in params:
                        writes = True
                    if isinstance(f, ast.Attribute) and f.attr in NP_WRITERS and n.args and _root_name(n.args[0]) in params:
                        writes = True
            out[fn.name] = out.get(fn.name, False) or writes
    return out


def find_writes(relpath: str, source: str, writers: Dict[str, bool] = None) -> List[dict]:
    """Every write into the block, the cells or the logs in one module: {file, func, attr, line, kind, recv}. `writers` (SEAM 5): the
    tree's `param_writers` map — a block array passed BARE to a non-numpy callee that writes through its parameters (or to a callee the
    map does not know) is a write by the caller, kind 'call-alias'. None: the map of this module alone."""
    tree = ast.parse(source)
    out: List[dict] = []
    if writers is None:
        writers = param_writers([(relpath, source)])

    def walk(node, qual: List[str]):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                walk(child, qual + [child.name])
                continue
            func = ".".join(qual)
            targets = []
            if isinstance(child, ast.Assign):
                targets = list(child.targets)
            elif isinstance(child, (ast.AugAssign, ast.AnnAssign)):
                targets = [child.target]
            elif isinstance(child, ast.Delete):
                targets = list(child.targets)
            flat = []
            for t in targets:
                flat.extend(t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t])
            for t in flat:
                attr = _root_attr(t)
                if attr in BLOCK | LOGS | {"cells"}:
                    kind = ("rebind" if isinstance(t, ast.Attribute) else "subscript") + ("+aug" if isinstance(child, ast.AugAssign) else "") + ("+del" if isinstance(child, ast.Delete) else "")
                    out.append({"file": relpath, "func": func, "attr": attr, "line": child.lineno, "kind": kind, "recv": _recv(t)})
            if isinstance(child, ast.Call):
                fn = child.func
                for kw in child.keywords:
                    if kw.arg == "out" and _root_attr(kw.value) in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": _root_attr(kw.value), "line": child.lineno, "kind": "out=", "recv": _recv(kw.value)})
                if isinstance(fn, ast.Attribute):
                    recv = _root_attr(fn.value)
                    if fn.attr in INPLACE_METHODS and recv in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": recv, "line": child.lineno, "kind": f".{fn.attr}()", "recv": _recv(fn.value)})
                    if fn.attr in LIST_MUTATORS and recv in LOGS:
                        out.append({"file": relpath, "func": func, "attr": recv, "line": child.lineno, "kind": f".{fn.attr}()", "recv": _recv(fn.value)})
                    if fn.attr in NP_WRITERS and child.args and _root_attr(child.args[0]) in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": _root_attr(child.args[0]), "line": child.lineno, "kind": f"np.{fn.attr}()", "recv": _recv(child.args[0])})
                # SEAM 5, rule (4): the alias road — a BARE block array handed to a callee that writes through its parameters
                if not _is_numpy_call(fn) and writers.get(_callee_name(fn), True):
                    for arg in list(child.args) + [kw.value for kw in child.keywords if kw.arg != "out"]:
                        if isinstance(arg, ast.Attribute) and arg.attr in BLOCK:
                            out.append({"file": relpath, "func": func, "attr": arg.attr, "line": child.lineno, "kind": f"call-alias {_callee_name(fn) or '?'}()",
                                        "recv": _recv(arg)})
            walk(child, qual)

    walk(tree, [])
    return out


def marks_witness(relpath: str, source: str, qual: str, pair: bool = None) -> bool:
    """True iff the function `qual` in the module calls `.mark(` or `.mark_rows(` somewhere in its body. SEAM 5, rule (5): `pair=True`
    requires such a call WITH a `pair=` keyword (a sound meeting's block), `pair=False` one WITHOUT it (the sight<->words block); None: any."""
    tree = ast.parse(source)

    def find(node, q: List[str]):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ".".join(q + [child.name]) == qual:
                    return child
                r = find(child, q + [child.name])
                if r is not None:
                    return r
        return None

    f = find(tree, [])
    if f is None:
        return False
    for n in ast.walk(f):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("mark", "mark_rows"):
            has_pair = any(kw.arg == "pair" for kw in n.keywords)
            if pair is None or has_pair == pair:
                return True
    return False


def offenders(modules: List[Tuple[str, str]]) -> List[str]:
    """Every write the witness does not know, and every in-place mask writer that does not mark it — by (file:line func attr kind)."""
    bad: List[str] = []
    writers = param_writers(modules)
    for relpath, source in modules:
        for w in find_writes(relpath, source, writers):
            key = (w["file"], w["func"])
            where = f"{w['file']}:{w['line']} {w['func']} .{w['attr']} {w['kind']}"
            if w["attr"] in BLOCK:
                if key not in KNOWN_BLOCK:
                    bad.append("unknown block writer: " + where)
                elif w["attr"] == "mask" and w["kind"] != "rebind" and key not in REBUILD_POINTS:
                    # SEAM 5, rule (5): through `self.` = the organism's own sight<->words block (a mark without pair=); through any
                    # other receiver = a sound meeting (a mark with pair=)
                    if key not in MUST_MARK or not marks_witness(relpath, source, w["func"], pair=(w.get("recv") != "self")):
                        bad.append("writes the MASK without marking the witness (for that block): " + where)
            elif w["attr"] == "cells":
                if key not in KNOWN_CELLS:
                    bad.append("cells written outside birth/grow/load (the running cells digest is append-only): " + where)
            elif w["attr"] in LOGS:
                if w["kind"] == "rebind" and key in KNOWN_LOG_REBIND:
                    continue
                bad.append("a log mutated other than by .append (the running log digests are append-only): " + where)
    return sorted(set(bad))


def tree_modules() -> List[Tuple[str, str]]:
    mods = []
    for d in ("genome", "creature"):
        for p in sorted((TREE / d).rglob("*.py")):
            mods.append((str(p.relative_to(TREE)), p.read_text()))
    return mods


class TestTheTreeIsClean(unittest.TestCase):
    def test_every_block_writer_is_one_the_witness_knows(self) -> None:
        self.assertEqual(offenders(tree_modules()), [])

    def test_the_sweep_sees_every_known_writer(self) -> None:
        """The positive control of the walker itself: every (file, function) in KNOWN_BLOCK is FOUND writing the block (a stale entry is a
        name the sweep no longer sees — it would silently allow a writer by that name)."""
        mods = tree_modules()
        writers = param_writers(mods)
        seen = {(w["file"], w["func"]) for rel, src in mods for w in find_writes(rel, src, writers) if w["attr"] in BLOCK}
        self.assertEqual(set(KNOWN_BLOCK) - seen, set())
        self.assertTrue(MUST_MARK <= seen)


class TestPlantedModules(unittest.TestCase):
    def test_a_planted_block_writer_is_caught(self) -> None:
        src = ("import numpy as np\n"
               "class Sneak:\n"
               "    def poke(self, org):\n"
               "        org.W[0, 0] = 1.0\n"
               "        org.mask[1, 2] += 1\n"
               "        org.strikes, org.W = 0, 0\n"
               "        np.clip(org.W[3], -1, 1, out=org.W[3])\n"
               "        org.mask.fill(0)\n"
               "        np.copyto(org.strikes, 0)\n")
        bad = offenders([("genome/planted_offender.py", src)])
        self.assertEqual(len(bad), 7, bad)
        self.assertTrue(all("unknown block writer" in b for b in bad))

    def test_a_known_mask_writer_that_stops_marking_is_caught(self) -> None:
        src = ("class Organism:\n"
               "    def _hebb(self, S, T):\n"
               "        for s in S:\n"
               "            for t in T:\n"
               "                self.mask[s, t] = 1\n")
        bad = offenders([("genome/machinery.py", src)])
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("without marking the witness", bad[0])
        ok = src + "                w = self._witness\n                w.mark(s)\n"
        self.assertEqual(offenders([("genome/machinery.py", ok)]), [])

    # ---------------------------------------------------------------- SEAM 5 (2026-09-23 14:52 +0400): the alias road and the which-block rule
    def test_a_write_through_a_parameter_is_caught_at_the_call_site(self) -> None:
        """Rule (4): `_merge_rows(W, M, ST, ...)`'s shape — a helper writes the arrays it is HANDED; the caller that hands it a bare block
        array is the writer. Caught for a module function, a staticmethod, and a callee the tree does not define (conservative)."""
        src = ("import numpy as np\n"
               "def poke(W, M):\n"
               "    M[0, 0] = 1\n"
               "    W[0, 0] += 2.0\n"
               "class Sneak:\n"
               "    @staticmethod\n"
               "    def _rows(W, M, ST, a):\n"
               "        np.clip(W[a], -1, 1, out=W[a])\n"
               "    def f(self, org):\n"
               "        poke(org.W, org.mask)\n"
               "        self._rows(org.W, org.mask, org.strikes, 3)\n"
               "        somelib.touch(org.strikes)\n")
        bad = offenders([("genome/planted_alias.py", src)])
        self.assertEqual(len(bad), 6, bad)
        self.assertTrue(all("unknown block writer" in b and "call-alias" in b for b in bad), bad)

    def test_a_known_mask_writer_through_an_alias_must_mark_the_right_block(self) -> None:
        """Rule (5), on `_area_merge`'s real shape: the sight<->words MASK handed to `_merge_rows` through `self.` must be marked with no
        `pair=`; marked only as a meeting (`pair=`), or not at all, it is CAUGHT. A meeting's MASK (`p.mask`) needs `pair=`."""
        src = ("class Organism:\n"
               "    @staticmethod\n"
               "    def _merge_rows(W, M, ST, a, b, axis):\n"
               "        M[b] = 0\n"
               "        return [a, b]\n"
               "    def _area_merge(self, area, a, b):\n"
               "        wit = self._witness\n"
               "        rows = self._merge_rows(self.W, self.mask, self.strikes, a, b, 0)\n")
        rel = "genome/machinery.py"
        bad = offenders([(rel, src)])
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("without marking the witness", bad[0])
        self.assertEqual(offenders([(rel, src + "        wit.mark_rows(rows)\n")]), [])
        wrong = offenders([(rel, src + "        wit.mark_rows(rows, pair='sight-sound')\n")])
        self.assertEqual(len(wrong), 1, "a mark on a MEETING does not answer a write into the sight<->words block")
        pair_src = ("class Organism:\n"
                    "    def _pair_hebb(self, p, R, C):\n"
                    "        w = self._witness\n"
                    "        for r in R:\n"
                    "            p.mask[r, C[0]] = 1\n")
        self.assertEqual(len(offenders([(rel, pair_src)])), 1, "unmarked")
        self.assertEqual(len(offenders([(rel, pair_src + "            w.mark(r)\n")])), 1, "marked on the WRONG block (no pair=)")
        self.assertEqual(offenders([(rel, pair_src + "            w.mark(r, pair=p.name)\n")]), [])

    def test_the_alias_rule_does_not_flag_a_reader(self) -> None:
        """Rule (4)'s negative control: a bare block array handed to a callee that only READS its parameter (scan_keys' shape), to numpy,
        or a param-writing helper handed something that is not the block — none of it is a write."""
        src = ("import numpy as np\n"
               "def reader(M, n):\n"
               "    return M[:n].sum()\n"
               "def poke(buf):\n"
               "    buf[0] = 1\n"
               "class Reader:\n"
               "    def look(self, org):\n"
               "        a = reader(org.mask, 3)\n"
               "        b = np.count_nonzero(org.W) + np.count_nonzero(org.strikes)\n"
               "        np.savez_compressed('x', W=org.W, mask=org.mask)\n"
               "        poke(self.scratch)\n"
               "        poke(org.W[:3].copy())\n")
        self.assertEqual(offenders([("creature/planted_reader.py", src)]), [])

    def test_append_only_law_offenders_are_caught(self) -> None:
        src = ("class X:\n"
               "    def f(self, org):\n"
               "        org.edges_log.pop()\n"
               "        org.births[0] = (0, 'sight', 0, 'novelty')\n"
               "        org.prunes_log += [(1, 2, 3)]\n"
               "        org.merges = []\n"
               "        del org.births[3]\n"
               "        org.sight.cells[3] = 0.0\n")
        bad = offenders([("creature/planted.py", src)])
        self.assertEqual(len(bad), 6, bad)

    def test_a_planted_clean_module_is_not_flagged(self) -> None:
        src = ("import numpy as np\n"
               "class Reader:\n"
               "    def look(self, org):\n"
               "        v = org.W[0, 0]; m = org.mask.sum(); s = org.strikes[:3].copy()\n"
               "        W = org.W[[1, 2]]\n"
               "        W[0] = 5.0\n"
               "        self.Wx = 1; self.weights = [0]; self.weights[0] = 2; self.masks = 3\n"
               "        org.edges_log.append((1, 2, 3)); org.births.append((0, 'sight', 1, 'novelty'))\n"
               "        n = len(org.merges); last = org.prunes_log[-1:]\n"
               "        x = np.clip(v, -1, 1)\n")
        self.assertEqual(offenders([("creature/planted_clean.py", src)]), [])


class TestGateG4SweepsTheNewModule(unittest.TestCase):
    """The writer law (the brief's RULES): tools/gate_g4.py step 1 stays green and gains a planted offender for the new module. The witness
    writes NO file (it is part of the organism, computed on the mind thread): the gate's writer check sweeps it, the real module is clean,
    and a planted copy that writes under state/ is caught."""

    def test_the_new_module_is_swept_clean_and_a_planted_copy_is_caught(self) -> None:
        import tempfile
        from tools import gate_g4
        self.assertIn("genome/witness.py", gate_g4.SENSE_FILES)
        real = TREE / "genome" / "witness.py"
        self.assertEqual(gate_g4.sweep([real]), [])
        with tempfile.TemporaryDirectory() as d:
            plant = Path(d) / "witness.py"
            plant.write_text(real.read_text() + "\n\ndef _leak(root, digest):\n    p = root / 'state' / 'witness.json'\n    p.write_text(digest)\n")
            self.assertEqual(len(gate_g4.sweep([plant])), 1)


if __name__ == "__main__":
    unittest.main()
