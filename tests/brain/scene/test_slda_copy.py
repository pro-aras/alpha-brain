# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:13 +0400 — the brief: «StreamingLDA for P-ORACLE — copy or import it read-only;
# do not modify that tree». brain/scene/slda.py is a copy; this pins every copied segment's text to the source file named
# in its header (skipped where that file is absent), and a planted one-character change is caught by the same comparison.
from __future__ import annotations

import ast
import unittest
from pathlib import Path

from brain.scene import slda

COPY = Path(slda.__file__)
NAMES = ("SLDA_RING", "_f64", "_fbytes", "StreamingLDA")


def segments(src: str) -> dict:
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in NAMES:
                    out[t.id] = ast.get_source_segment(src, node)
        elif getattr(node, "name", None) in NAMES:
            out[node.name] = ast.get_source_segment(src, node)
    return out


class TestSldaCopy(unittest.TestCase):
    def test_copy_equals_its_source(self) -> None:
        src_path = Path(slda.SOURCE_PATH)
        if not src_path.exists():
            self.skipTest(f"{src_path} is not on this box")
        a = segments(COPY.read_text(encoding="utf-8"))
        b = segments(src_path.read_text(encoding="utf-8"))
        self.assertEqual(set(a), set(NAMES))
        for n in NAMES:
            self.assertEqual(a[n], b[n], n)

    def test_a_planted_change_is_caught(self) -> None:
        text = COPY.read_text(encoding="utf-8")
        a = segments(text)
        b = segments(text.replace("mu += d / self.counts[idx]", "mu += d / (self.counts[idx] + 0)"))
        self.assertNotEqual(a["StreamingLDA"], b["StreamingLDA"])


if __name__ == "__main__":
    unittest.main()
