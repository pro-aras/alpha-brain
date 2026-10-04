"""PREREG-W2 (SIGNED x3, t-l4-1003 5b32d03) — the frozen template set v1's tests, written FIRST (red).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:00 +0400 — new file for the W2 build; law
# docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §2 (the template table, decision 8(c)/(d)).

  v1's tpl-id scheme: the exact id set of the law's §2 table; the versioned doc MENTOR-TEMPLATES-v1.md renders
  EXACTLY the code table (the equality the law owes, decision 8(d)); NP words are the parent's own T1..T4 forms
  (brain/scene/world.py's template_words, checked against it); every heard word is in the ear's alphabet
  (<= 8 letters a-z, genome/world.py's rule).
"""
from __future__ import annotations

import unittest
from pathlib import Path

from brain.scene import world as W
from creature.senses import mentor as M

LAW_V1_IDS = (
    "M-C1-T1", "M-C1-T2", "M-C1-T3", "M-C1-T4",
    "M-C2-T1", "M-C2-T2", "M-C2-T3", "M-C2-T4",
    "M-C3", "M-M1", "M-M2", "M-M3", "M-A1", "M-A2", "M-A3",
)


class TestTemplateSetV1(unittest.TestCase):
    def test_the_id_set_is_the_laws(self):
        self.assertEqual(tuple(sorted(M.TEMPLATES_V1)), tuple(sorted(LAW_V1_IDS)))

    def test_every_id_has_its_surface_and_truth_rule(self):
        for tpl, spec in M.TEMPLATES_V1.items():
            self.assertIn("surface", spec, tpl)
            self.assertIn("truth", spec, tpl)

    def test_the_doc_renders_the_code_table_exactly(self):
        doc = Path("docs/organism/whole/mentor/MENTOR-TEMPLATES-v1.md")
        self.assertTrue(doc.exists(), "the versioned template file must exist (decision 8(d))")
        text = doc.read_text(encoding="utf-8")
        self.assertEqual(text, M.render_templates_v1())

    def test_np_words_are_the_parents_own(self):
        t = M.Thing(shape="circle", colour="blue", size="big", top=0, left=0)
        mine = {"T1": ("circle",), "T2": ("blue", "circle"), "T3": ("big", "circle"), "T4": ("big", "blue", "circle")}
        for npt, words in mine.items():
            self.assertEqual(M.np_words(npt, t), words)
            self.assertEqual(M.np_words(npt, t), W.template_words(npt, t))

    def test_every_word_in_the_ears_alphabet(self):
        for word in M.MENTOR_WORDS_V1:
            self.assertTrue(word.isalpha() and word.islower() and len(word) <= 8, word)


if __name__ == "__main__":
    unittest.main()
