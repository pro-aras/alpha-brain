# edit: Claude (Fable 5.1, the seat), 2026-09-29 13:11 +0400 — PREREG-WORD-ROAD §1.9 / §6 (the co-signer's added control), test-first.
"""tests/genome/test_word_of_vector.py — a word cell is named by the word its own vector holds."""
from __future__ import annotations

import unittest

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome
from genome.questions import build_ledgers, word_of_vector

from ._toy import mini_genome

WORDS = ("a", "red", "circle", "triangle", "zzzzzzzz", "big", "bigger")


class Decode(unittest.TestCase):
    def test_every_word_comes_back_under_both_codes(self) -> None:
        for blank_zero in (False, True):
            for w in WORDS:
                with self.subTest(word=w, blank_zero=blank_zero):
                    self.assertEqual(word_of_vector(world.encode_word(w, blank_zero), blank_zero), w)

    def test_the_blank_word_is_the_blank_word(self) -> None:
        self.assertEqual(word_of_vector(world.encode_word("", False), False), "")

    def test_a_vector_that_is_no_words_code_refuses_by_name(self) -> None:
        v = world.encode_word("circle", False).copy()
        v[3] += 0.25                                   # a planted flip inside the first letter's slot
        with self.assertRaises(ValueError) as e:
            word_of_vector(v, False)
        self.assertIn("no word", str(e.exception))
        with self.assertRaises(ValueError):
            word_of_vector(np.zeros(5), False)

    def test_the_wrong_code_refuses(self) -> None:
        with self.assertRaises(ValueError):
            word_of_vector(world.encode_word("circle", True), False)


class TheLedgerUnderTheLine(unittest.TestCase):
    """The toy genome's ear is `blank=zero` (no genome on disk is): the decode reads the genome's own code."""

    def test_two_words_born_at_one_moment_are_each_named_by_themselves(self) -> None:
        from ._toy import onehot
        text = mini_genome().text + "HEAR     every word; thing last; arrival last\n"
        org = Organism(parse_genome(text))
        a, b = world.encode_word("red", True), world.encode_word("circle", True)
        org.moment(onehot(0, 64), [a, b])
        L = build_ledgers(org, {0: "circle"})["words"]
        self.assertEqual(sorted(next(iter(s)) for s in L.values()), ["circle", "red"])
        old = Organism(mini_genome())
        old.moment(onehot(0, 64), [a, b])
        Lo = build_ledgers(old, {0: "circle"})["words"]
        self.assertEqual(sorted(next(iter(s)) for s in Lo.values()), ["circle", "circle"], "without the line: the old ledger")


if __name__ == "__main__":
    unittest.main()
