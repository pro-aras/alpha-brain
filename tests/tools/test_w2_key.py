"""PREREG-W2 (SIGNED x3) — the fenced examiner's key's tests, written FIRST (red).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:08 +0400 — new file for the W2 build; law §3 item 4 (the
# fenced examiner's key: a table-driven parser of the WORLD's grammar returning {subject, verb, polarity, np, tpl} or
# UNPARSEABLE — its table is the frozen v1 set and nothing else).

  Every v1 production parses to its tuple (the G-KEY self-check); the UNPARSEABLE set is CAUGHT: wrong order, an
  unknown verb, a tpl/words family mismatch, a broken negation, a negation carrying a C1 id, a token/id mismatch,
  an unknown tpl, an NP outside the vocabulary, a word outside the ear's alphabet.
"""
from __future__ import annotations

import unittest

from tools.toys.w2 import key as K

C1 = {"M-C1-T1": ["alpha", "sees", "cross"], "M-C1-T2": ["alpha", "sees", "blue", "cross"],
      "M-C1-T3": ["alpha", "sees", "big", "cross"], "M-C1-T4": ["alpha", "sees", "big", "blue", "cross"]}
C2 = {"M-C2-T1": ["alpha", "does", "not", "see", "cross"], "M-C2-T2": ["alpha", "does", "not", "see", "blue", "cross"],
      "M-C2-T3": ["alpha", "does", "not", "see", "big", "cross"], "M-C2-T4": ["alpha", "does", "not", "see", "big", "blue", "cross"]}
ANSWERS = {"M-A1": ["alpha", "sees", "blue", "cross"], "M-A2": ["alpha", "sees", "blue", "cross"],
           "M-A3": ["alpha", "sees", "big", "cross"]}
MIRROR = {"M-M1": ["unsure"], "M-M2": ["fresh"], "M-M3": ["asked"]}


class TestParse(unittest.TestCase):
    def test_every_v1_production_parses(self):
        for tpl, words in {**C1, **C2, **ANSWERS, **MIRROR}.items():
            out = K.parse(words, tpl)
            self.assertIsNotNone(out, tpl)
            self.assertEqual(out["tpl"], tpl)

    def test_the_tuple_fields(self):
        out = K.parse(["alpha", "sees", "blue", "cross"], "M-C1-T2")
        self.assertEqual(out, {"subject": "alpha", "verb": "sees", "polarity": "+", "np": ("blue", "cross"), "tpl": "M-C1-T2"})
        out = K.parse(["alpha", "does", "not", "see", "big", "cross"], "M-C2-T3")
        self.assertEqual(out, {"subject": "alpha", "verb": "see", "polarity": "-", "np": ("big", "cross"), "tpl": "M-C2-T3"})
        out = K.parse(["unsure"], "M-M1")
        self.assertEqual(out, {"subject": None, "verb": "mirror", "polarity": None, "np": None, "tpl": "M-M1"})

    def test_a_run_row_parses_under_m_c3(self):
        out = K.parse(["alpha", "sees", "big", "blue", "cross"], "M-C3")
        self.assertEqual(out["tpl"], "M-C3")
        self.assertEqual(out["np"], ("big", "blue", "cross"))

    def test_the_unparseable_set_is_caught(self):
        for words, tpl in (
            (["sees", "alpha", "cross"], "M-C1-T1"),                 # wrong order
            (["alpha", "watches", "cross"], "M-C1-T1"),              # an unknown verb
            (["alpha", "sees", "cross"], "M-C1-T2"),                 # T1's words, T2's id
            (["alpha", "sees", "big", "blue", "cross"], "M-C1-T3"),  # T4's words, T3's id
            (["alpha", "does", "see", "cross"], "M-C2-T1"),          # a broken negation
            (["alpha", "does", "not", "see", "cross"], "M-C1-T1"),   # a negation carrying a C1 id
            (["alpha", "sees", "cross"], "M-C2-T1"),                 # a positive carrying a C2 id
            (["fresh"], "M-M1"),                                     # a token/id mismatch
            (["unsure"], "M-M2"),                                    # another
            (["alpha", "sees", "star"], "M-C9"),                     # an unknown tpl
            (["alpha", "sees", "flurp"], "M-C1-T1"),                 # an NP outside the vocabulary
            (["Alpha", "sees", "cross"], "M-C1-T1"),                 # outside the ear's alphabet
            ([], "M-C1-T1"),
        ):
            self.assertIsNone(K.parse(words, tpl), (words, tpl))


if __name__ == "__main__":
    unittest.main()
