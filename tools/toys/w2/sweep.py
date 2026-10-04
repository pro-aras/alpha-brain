"""tools/toys/w2/sweep.py — PREREG-W2 §5 M-PURE: a STATIC sweep of the build's files (T-L4's M6 form, verbatim in kind).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file, written after tests/tools/test_w2_sweep.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §5 M-PURE (imports ⊂ the allow-list; no softmax, argmax or
rng.choice over a lexicon — read as AST nodes, never as substrings, so a docstring may name them; a scorer that reads
`words` is caught; the mentor is a table lookup from the record, never a model).

Run:  PYTHONPATH=. python3 -m tools.toys.w2.sweep [file or dir ...]      exits 0 when clean, 1 with one finding per line.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import List

ALLOWED_MODULES = {"brain.scene.learners", "brain.scene.world", "brain.world.seeds", "creature.senses.mentor",
                   "creature.senses.scene", "genome.brain", "tools.toys.tl4"}
OWN_PACKAGES = ("tools.toys.w2",)
FORBIDDEN_NAMES = {"softmax", "argmax", "choice"}
SCORER_NAMES = {"score", "scene_scores"}


def _import_ok(name: str) -> bool:
    top = name.split(".")[0]
    if top in sys.stdlib_module_names:
        return True
    if name == "numpy" or name.startswith("numpy."):
        return True
    if name == "scipy.stats" or name.startswith("scipy.stats."):
        return True
    if name in ALLOWED_MODULES:
        return True
    return any(name == p or name.startswith(p + ".") for p in OWN_PACKAGES)


def _files(target: Path) -> List[Path]:
    target = Path(target)
    if target.is_dir():
        return sorted(target.glob("*.py"))
    return [target]


def sweep(target: Path) -> List[str]:
    findings: List[str] = []
    for f in _files(target):
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if not _import_ok(a.name):
                        findings.append(f"{f.name}:{node.lineno}: import outside the allowed set: {a.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                mod = node.module or ""
                if mod == "scipy":
                    bad = [a.name for a in node.names if a.name != "stats"]
                    if bad:
                        findings.append(f"{f.name}:{node.lineno}: from scipy import {', '.join(bad)} (only scipy.stats is allowed)")
                elif not _import_ok(mod):
                    for a in node.names:
                        if not _import_ok(f"{mod}.{a.name}"):
                            findings.append(f"{f.name}:{node.lineno}: import outside the allowed set: {mod}.{a.name}")
            elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
                findings.append(f"{f.name}:{node.lineno}: forbidden attribute .{node.attr}")
            elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                findings.append(f"{f.name}:{node.lineno}: forbidden name {node.id}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in SCORER_NAMES:
                args = [a.arg for a in node.args.args + node.args.kwonlyargs + node.args.posonlyargs]
                if node.args.vararg:
                    args.append(node.args.vararg.arg)
                if node.args.kwarg:
                    args.append(node.args.kwarg.arg)
                if "words" in args:
                    findings.append(f"{f.name}:{node.lineno}: the scorer {node.name} reads the words ({', '.join(args)})")
    return findings


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    targets = [Path(a) for a in argv] if argv else [Path(__file__).resolve().parent]
    found = [line for t in targets for line in sweep(t)]
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
