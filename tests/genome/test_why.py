"""test_why.py — B5: «why» (genome/questions.py's why) — the record behind an answer.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B5 (docs/G4-PREREG.md §3, docs/briefs/
G4-BUILDER-B-GENES.md): after a G0b-style life on 3 things with an Episodes store written beside it,
why(org, ledgers, episodes, "circle") names only circle's cells and episodes; a word never shown returns
empty lists, never an error.
"""
from __future__ import annotations

import unittest

import numpy as np

from genome import world
from genome.fast import Episodes
from genome.machinery import Organism, retina
from genome.questions import build_ledgers, why

from ._toy import mini_genome


class TestWhy(unittest.TestCase):
    def _life(self):
        g = mini_genome(nmax=200, budget=400)
        things = ["circle", "square", "triangle"]
        rng = np.random.default_rng(2)
        dev = world.stream(things, 20, rng, side=24)   # SENSE eye 24x24 matches _toy's mini_genome
        org = Organism(g)
        ep = Episodes(cap=1000, dim_s=g.sight_dim(), dim_w=g.words_dim())
        moment_thing = {}
        for t, pic in dev:
            x_s = retina(pic, g.retina)
            x_w = world.encode_word(t, g.ear_blank_zero)
            moment_thing[org.t] = t
            org.moment(x_s, x_w)
            ep.write(moment=org.t - 1, x_s=x_s, x_w=x_w, word=t, surprise=float(org.t))
        ledgers = build_ledgers(org, moment_thing)
        return org, ledgers, ep

    def test_why_names_only_circles_cells_and_episodes(self) -> None:
        org, ledgers, ep = self._life()
        r = why(org, ledgers, ep, "circle")
        self.assertTrue(r["cells"], "circle must have at least one cell after 20 showings")
        self.assertTrue(r["episodes"], "circle must have at least one episode")
        for area, c in r["cells"]:
            self.assertIn(area, ("sight", "words"))
            L = ledgers[area]
            self.assertEqual(L.get(c), {"circle"}, f"a cell named by why(circle) must be born on circle alone")
        for eid in r["episodes"]:
            rec = ep.get(eid)
            self.assertIsNotNone(rec)
            self.assertEqual(rec["word"], "circle")
        for s, t, w in r["edges"]:
            self.assertIn(("sight", s), r["cells"])
            self.assertIn(("words", t), r["cells"])
            self.assertIsInstance(w, float)

    def test_why_names_no_other_things_cells_or_episodes(self) -> None:
        org, ledgers, ep = self._life()
        r = why(org, ledgers, ep, "circle")
        square = why(org, ledgers, ep, "square")
        triangle = why(org, ledgers, ep, "triangle")
        self.assertFalse(set(r["episodes"]) & set(square["episodes"]))
        self.assertFalse(set(r["episodes"]) & set(triangle["episodes"]))
        self.assertFalse(set(r["cells"]) & set(square["cells"]))
        self.assertFalse(set(r["cells"]) & set(triangle["cells"]))

    def test_a_word_never_shown_returns_empty_never_an_error(self) -> None:
        org, ledgers, ep = self._life()
        r = why(org, ledgers, ep, "hexagon")
        self.assertEqual(r, {"cells": [], "episodes": [], "edges": []})

    def test_why_with_no_episode_store(self) -> None:
        org, ledgers, _ep = self._life()
        r = why(org, ledgers, None, "circle")
        self.assertEqual(r["episodes"], [])
        self.assertTrue(r["cells"])   # cells/edges still work without a FAST store

    def test_why_never_changes_the_organism_or_the_store(self) -> None:
        org, ledgers, ep = self._life()
        h_before = org.state_hash()
        ep_before = (ep.n_written, ep._next_slot, ep.ids.copy())
        why(org, ledgers, ep, "circle")
        why(org, ledgers, ep, "hexagon")
        self.assertEqual(org.state_hash(), h_before)
        self.assertEqual(ep.n_written, ep_before[0])
        self.assertEqual(ep._next_slot, ep_before[1])
        self.assertTrue(np.array_equal(ep.ids, ep_before[2]))


if __name__ == "__main__":
    unittest.main()
