# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:13 +0400 — S1a step 2 (PREREG-R3-TONIGHT §S1a «The eye's segmentation»: «The
# world's truth maps each fixation to its thing for GRADING ONLY. An import allow-list / AST test proves no learner
# module can read the truth.»). The learner modules (learners.py, its slda.py, and eye.py's segmentation) may import
# only the allow-listed modules and may not name the truth file; two planted offenders (an import of the world / the
# cache's truth reader, and a literal naming truth.jsonl) must be CAUGHT by the same checker.
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
    # edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:30 +0400 — PREREG-TMEM2: the HEALTH row is kept WITHOUT the world
    "health.py": {"__future__", "math", "typing", "numpy", "brain.scene.learners"},
}
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


if __name__ == "__main__":
    unittest.main()
