"""PREREG-W2 (SIGNED x3) — M-PURE's static sweep tests, written FIRST (red).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file for the W2 build; law §5 M-PURE
# (imports inside the allow-list; no softmax, argmax or rng.choice over a lexicon; the mentor a table lookup,
# never a model; the planted offenders CAUGHT — T-L4's M6 form, its sweep read as AST nodes, never substrings).

  The build files (creature/senses/mentor.py, tools/toys/w2/) sweep CLEAN; the plants are CAUGHT: an `import torch`,
  a scorer that reads `words`, an argmax over the vocabulary.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.toys.w2 import sweep as SW


class TestSweep(unittest.TestCase):
    def test_the_build_files_are_clean(self):
        found = SW.sweep(Path("creature/senses/mentor.py")) + SW.sweep(Path("tools/toys/w2"))
        self.assertEqual(found, [])

    def _planted(self, text: str) -> list:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "planted.py"
            p.write_text(text, encoding="utf-8")
            return SW.sweep(p.parent)

    def test_the_torch_plant_is_caught(self):
        self.assertTrue(any("torch" in f for f in self._planted("import torch\n")))

    def test_the_words_scorer_plant_is_caught(self):
        self.assertTrue(self._planted("def score(X, L, words):\n    return 0.0\n"))

    def test_the_argmax_plant_is_caught(self):
        self.assertTrue(self._planted("import numpy as np\nbest = int(np.argmax(p))\n"))


if __name__ == "__main__":
    unittest.main()
