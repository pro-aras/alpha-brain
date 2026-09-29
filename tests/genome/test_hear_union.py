# edit: Claude (Fable 5.1, the seat), 2026-09-29 12:46 +0400 — PREREG-WORD-ROAD §1.2–§1.6, test-first (red on day-0929 f855582: Organism.moment
# takes ONE word vector).
"""tests/genome/test_hear_union.py — ONE moment that meets SEVERAL words (the gene HEAR's organism half).

Organism.moment(x_s, [x_w1, x_w2, ...]): the words side is the UNION, in the given order, of each word's own winners; each
word's novelty birth is its own; HEBB / DELTA wire every sight winner to every word of the moment; THRESH's own band takes
a push when the top sight winner's established answer is ANY cell of the union; an error birth in the words area holds the
vector of the word that lit the misfiring cell. A single vector — and a list of ONE vector — is today's road, state for
state."""
from __future__ import annotations

import unittest

import numpy as np

from genome.machinery import Organism, parse_genome

from ._toy import mini_genome, onehot


def _words_cell_of(org: Organism, x: np.ndarray) -> int:
    """The one alive word cell whose stored vector IS x (a word cell stores its birth input)."""
    hits = [c for c in range(org.words.n) if org.words.alive[c] and np.array_equal(org.words.cells[c], x)]
    assert len(hits) == 1, hits
    return hits[0]


class OneMomentSeveralWords(unittest.TestCase):
    def test_every_word_of_the_moment_gets_its_own_cell_and_its_edge(self) -> None:
        org = Organism(mini_genome())
        xs, a, b, c = onehot(0, 64), onehot(0, 208), onehot(1, 208), onehot(2, 208)
        t0 = org.t
        S, T = org.moment(xs, [a, b, c])
        self.assertEqual(org.t, t0 + 1, "one moment: the clock moves by one")
        self.assertEqual(org.words.n, 3)
        ca, cb, cc = (_words_cell_of(org, v) for v in (a, b, c))
        self.assertEqual(T, [ca, cb, cc], "the union, in the order spoken")
        self.assertEqual(len(S), 1)
        for t in (ca, cb, cc):
            self.assertEqual(int(org.mask[S[0], t]), 1)
        self.assertEqual(len([1 for _m, area, _c, _r in org.births if area == "words"]), 3)

    def test_a_word_said_twice_is_one_winner(self) -> None:
        org = Organism(mini_genome())
        xs, a, b = onehot(0, 64), onehot(0, 208), onehot(1, 208)
        _S, T = org.moment(xs, [a, b, a])
        self.assertEqual(len(T), 2)
        self.assertEqual(org.words.n, 2)

    def test_a_list_of_one_is_todays_road_state_for_state(self) -> None:
        xs, a, b = onehot(0, 64), onehot(0, 208), onehot(1, 208)
        xs2 = onehot(5, 64)
        one, lst = Organism(mini_genome()), Organism(mini_genome())
        for x, w in ((xs, a), (xs, a), (xs2, b), (xs, b), (xs, b), (xs, b), (xs2, a)):
            r1 = one.moment(x, w)
            r2 = lst.moment(x, [w])
            self.assertEqual(r1, r2)
        self.assertEqual(one.state_hash(), lst.state_hash())
        self.assertEqual(one.births, lst.births)
        self.assertEqual(dict(one.c), dict(lst.c))

    def test_no_word_is_still_no_word(self) -> None:
        org = Organism(mini_genome())
        _S, T = org.moment(onehot(0, 64), [])
        self.assertEqual(T, [])
        self.assertEqual(org.words.n, 0)


class TheAnswerIsAnyWordOfTheMoment(unittest.TestCase):
    def test_no_misfire_when_the_cells_answer_is_the_first_word(self) -> None:
        org = Organism(mini_genome())
        xs, a, b = onehot(0, 64), onehot(0, 208), onehot(1, 208)
        org.moment(xs, a)
        org.moment(xs, a)                       # the sight cell's established answer is «a»
        s = 0
        before = int(org.sight.misfires[s])
        for _ in range(4):
            org.moment(xs, [a, b])              # «a» is said FIRST, «b» last
        self.assertEqual(int(org.sight.misfires[s]), before, "its answer is among the moment's words: no strike")
        self.assertEqual(org.sight.n, 1, "and no error birth beside it")

    def test_thresh_pushes_when_the_answer_is_not_the_last_word(self) -> None:
        g = parse_genome(mini_genome().text + "THRESH cell own band history 30\n")
        org = Organism(g)
        xs, a, b = onehot(0, 64), onehot(0, 208), onehot(1, 208)
        org.moment(xs, a)
        org.moment(xs, a)
        n0 = int(org.sight.own_band_n[0])
        self.assertEqual(n0, 1)
        org.moment(xs, [a, b])
        self.assertEqual(int(org.sight.own_band_n[0]), n0 + 1, "the answer «a» is a word of this moment")
        org.moment(xs, [b, a])
        self.assertEqual(int(org.sight.own_band_n[0]), n0 + 2, "whatever its place in the utterance")


class AnErrorBirthHoldsItsOwnWord(unittest.TestCase):
    def test_the_new_word_cell_holds_the_vector_of_the_word_that_lit_the_misfiring_cell(self) -> None:
        # «a» is wired to sight 0 alone; then «a» is said (first) beside «b» (last) over sight 5, three times: the cell of «a»
        # misfires (its answer, sight 0, is not among the winners) and an error cell is born beside it. The toy's MERGE floor
        # is 0.99 and an identical vector is refused as redundant, so the birth is COUNTED as refused-redundant — and the
        # vector the refusal compared is «a»'s own, never «b»'s (were it «b»'s, cos 0 < THETA_M, a cell holding «b» would be born).
        org = Organism(mini_genome())
        xs0, xs5, a, b = onehot(0, 64), onehot(5, 64), onehot(0, 208), onehot(1, 208)
        for _ in range(30):                     # «a»'s edge to sight 0 is strong: it stays «a»'s answer through the three moments below
            org.moment(xs0, a)
        n_words = org.words.n
        red0 = int(org.c["births_refused_redundant"])
        for _ in range(3):
            org.moment(xs5, [a, b])
        holding_b = [c for c in range(org.words.n) if np.array_equal(org.words.cells[c], b)]
        self.assertEqual(len(holding_b), 1, "«b» has its one novelty cell and no error twin born from «a»'s misfire")
        self.assertEqual(org.words.n, n_words + 1)
        self.assertGreater(int(org.c["births_refused_redundant"]), red0, "«a»'s error birth was tried with «a»'s own vector")
        self.assertEqual(getattr(org, "hear_shared_cell", None), 0)


if __name__ == "__main__":
    unittest.main()
