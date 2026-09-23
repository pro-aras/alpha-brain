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
}
# the known writers that change the MASK in place and must tell the witness which rows
MUST_MARK = {("genome/machinery.py", "Organism._hebb"), ("genome/machinery.py", "Organism._prune"), ("genome/machinery.py", "Organism._merge")}
# the known writers that may write the mask WITHOUT marking: each is a point where the witness has not been asked yet (it scans then)
REBUILD_POINTS = {("genome/machinery.py", "Organism.__init__"), ("genome/machinery.py", "Organism._grow_W"), ("genome/machinery.py", "Organism.load"),
                  ("creature/think_thread.py", "freeze_recall_view")}
KNOWN_CELLS = {("genome/machinery.py", "Area.__init__"), ("genome/machinery.py", "Area.grow"), ("genome/machinery.py", "Organism._birth"),
               ("genome/machinery.py", "Organism.load"), ("creature/think_thread.py", "_freeze_area")}
KNOWN_LOG_REBIND = {("genome/machinery.py", "Organism.__init__"), ("genome/machinery.py", "Organism.load"), ("creature/think_thread.py", "freeze_recall_view")}


def _root_attr(node) -> str:
    """The attribute name a target is rooted at: `x.W[a][b]` -> 'W', `x.W` -> 'W', `x.W.T[...]` -> 'T' (a view by another name, not
    counted: none exists in the tree), else ''."""
    while isinstance(node, ast.Subscript):
        node = node.value
    return node.attr if isinstance(node, ast.Attribute) else ""


def find_writes(relpath: str, source: str) -> List[dict]:
    """Every write into the block, the cells or the logs in one module: {file, func, attr, line, kind}."""
    tree = ast.parse(source)
    out: List[dict] = []

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
                    out.append({"file": relpath, "func": func, "attr": attr, "line": child.lineno, "kind": kind})
            if isinstance(child, ast.Call):
                fn = child.func
                for kw in child.keywords:
                    if kw.arg == "out" and _root_attr(kw.value) in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": _root_attr(kw.value), "line": child.lineno, "kind": "out="})
                if isinstance(fn, ast.Attribute):
                    recv = _root_attr(fn.value)
                    if fn.attr in INPLACE_METHODS and recv in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": recv, "line": child.lineno, "kind": f".{fn.attr}()"})
                    if fn.attr in LIST_MUTATORS and recv in LOGS:
                        out.append({"file": relpath, "func": func, "attr": recv, "line": child.lineno, "kind": f".{fn.attr}()"})
                    if fn.attr in NP_WRITERS and child.args and _root_attr(child.args[0]) in BLOCK | {"cells"}:
                        out.append({"file": relpath, "func": func, "attr": _root_attr(child.args[0]), "line": child.lineno, "kind": f"np.{fn.attr}()"})
            walk(child, qual)

    walk(tree, [])
    return out


def marks_witness(relpath: str, source: str, qual: str) -> bool:
    """True iff the function `qual` in the module calls `.mark(` or `.mark_rows(` somewhere in its body."""
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
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("mark", "mark_rows") for n in ast.walk(f))


def offenders(modules: List[Tuple[str, str]]) -> List[str]:
    """Every write the witness does not know, and every in-place mask writer that does not mark it — by (file:line func attr kind)."""
    bad: List[str] = []
    for relpath, source in modules:
        for w in find_writes(relpath, source):
            key = (w["file"], w["func"])
            where = f"{w['file']}:{w['line']} {w['func']} .{w['attr']} {w['kind']}"
            if w["attr"] in BLOCK:
                if key not in KNOWN_BLOCK:
                    bad.append("unknown block writer: " + where)
                elif w["attr"] == "mask" and w["kind"] != "rebind" and key not in REBUILD_POINTS:
                    if key not in MUST_MARK or not marks_witness(relpath, source, w["func"]):
                        bad.append("writes the MASK without marking the witness: " + where)
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
        seen = {(w["file"], w["func"]) for rel, src in tree_modules() for w in find_writes(rel, src) if w["attr"] in BLOCK}
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
