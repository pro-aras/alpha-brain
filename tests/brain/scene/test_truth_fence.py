# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:13 +0400 — S1a step 2 (PREREG-R3-TONIGHT §S1a «The eye's segmentation»: «The
# world's truth maps each fixation to its thing for GRADING ONLY. An import allow-list / AST test proves no learner
# module can read the truth.»). The learner modules (learners.py, its slda.py, and eye.py's segmentation) may import
# only the allow-listed modules and may not name the truth file; two planted offenders (an import of the world / the
# cache's truth reader, and a literal naming truth.jsonl) must be CAUGHT by the same checker.
# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:06 +0400 — PREREG-S1C §6 THE FIRST GATE 1 («the truth fence's AST sweep covers rooms.py
# and pickers.py»): pickers.py joins the learner side (numpy, math, dataclasses, typing, the named substreams and the
# learner's own module — never the world, the rooms, the cache or the marks; a planted `from . import rooms` is CAUGHT);
# rooms.py is WORLD side and the reverse fence holds for it (it never imports a learner, a picker or a runner; a planted
# `from .pickers import …` is CAUGHT). Test-first: red on scene-s1b1 7706371 (neither file exists there).
from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path

SCENE = Path(__file__).resolve().parents[3] / "brain" / "scene"

ALLOW = {
    "learners.py": {"__future__", "math", "typing", "numpy", "brain.scene.slda"},
    "slda.py": {"__future__", "collections", "hashlib", "json", "typing", "numpy"},
    "eye.py": {"__future__", "dataclasses", "typing", "numpy", "genome", "genome.gaze", "genome.machinery",
               "brain.world", "brain.world.organs", "brain.world.build"},
    "pickers.py": {"__future__", "math", "dataclasses", "typing", "numpy", "brain.world.seeds", "brain.scene.learners"},
    # edit: Claude (Opus 5.5, T-MEM-1 builder), 2026-09-28 17:25 +0400 — memory.py (the store read back) is LEARNER side: it reads only what
    # the learner holds (its store, its ear, its statistics) and the loss's arithmetic from pickers.py.
    "memory.py": {"__future__", "math", "typing", "numpy", "brain.scene.learners", "brain.scene.pickers"},
    # edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:27 +0400 — context.py (the CONTEXT learner: its own act as context) is LEARNER side: the
    # learner's own module and the loss's clip from pickers.py, never the world, the rooms, the cache or the marks.
    "context.py": {"__future__", "typing", "numpy", "brain.scene.learners", "brain.scene.pickers"},
}
# the WORLD side's reverse fence: no world module imports a learner, a picker or a runner
WORLD_SIDE = ("world.py", "rooms.py")
LEARNER_OR_RUNNER = {"brain.scene.learners", "brain.scene.pickers", "brain.scene.slda", "brain.scene.run",
                     "brain.scene.run_s1c", "brain.scene.marks"}


def imports_of(path: Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level:
                mod = "brain.scene" + ("." + mod if mod else "")
            out.update([mod] if node.module else [f"{mod}.{a.name}" for a in node.names])
    return out
FORBIDDEN_WORDS = ("truth", "fix_thing")


def violations(path: Path, allowed: set) -> list:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name not in allowed:
                    out.append(f"import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if node.level:                                    # relative: resolve against brain.scene
                mod = "brain.scene" + ("." + mod if mod else "")
            full = [mod] if node.module else [f"{mod}.{a.name}" for a in node.names]
            for m in full:
                if m not in allowed:
                    out.append(f"from-import {m}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            doc = False
            if node.value and any(w in node.value for w in FORBIDDEN_WORDS):
                # a module / class / function DOCSTRING may say what the fence is; any other literal may not
                for parent in ast.walk(tree):
                    body = getattr(parent, "body", None)
                    if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and body[0].value is node:
                        doc = True
                if not doc:
                    out.append(f"literal {node.value[:40]!r}")
        elif isinstance(node, (ast.Name, ast.Attribute)):
            name = node.id if isinstance(node, ast.Name) else node.attr
            if name in ("load_truth", "fixation_thing", "fix_thing"):
                out.append(f"name {name}")
    return out


class TestTruthFence(unittest.TestCase):
    def test_learner_modules_stay_inside_the_allow_list(self) -> None:
        for name, allowed in ALLOW.items():
            self.assertEqual(violations(SCENE / name, allowed), [], name)

    def test_planted_offenders_are_caught(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "offender.py"
            p.write_text("from . import world\nimport numpy as np\n")
            self.assertEqual(violations(p, ALLOW["learners.py"]), ["from-import brain.scene.world"])
            p.write_text("from brain.scene.cache import load_truth\n")
            v = violations(p, ALLOW["learners.py"])
            self.assertIn("from-import brain.scene.cache", v)
            p.write_text("import json\nX = open('truth.jsonl').read()\n")
            v = violations(p, ALLOW["learners.py"])
            self.assertIn("import json", v)
            self.assertTrue(any(s.startswith("literal") for s in v), v)
            p.write_text("def f(t):\n    return t.fix_thing\n")
            self.assertEqual(violations(p, ALLOW["learners.py"]), ["name fix_thing"])
            p.write_text("from . import rooms\nimport numpy as np\n")
            self.assertEqual(violations(p, ALLOW["pickers.py"]), ["from-import brain.scene.rooms"])

    def test_the_world_side_never_imports_a_learner(self) -> None:
        for name in WORLD_SIDE:
            self.assertEqual(imports_of(SCENE / name) & LEARNER_OR_RUNNER, set(), name)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "world_offender.py"
            p.write_text("from .pickers import window_loss\nfrom . import world\n")
            self.assertEqual(imports_of(p) & LEARNER_OR_RUNNER, {"brain.scene.pickers"})


if __name__ == "__main__":
    unittest.main()
