# edit: Claude (Fable 5.1), 2026-09-22 10:58 +0400 — INDUCE's cost, found by profiling the closed g5-seam-1's end state on a hard-link copy
# (2026-09-22 10:5x +04): one think = 147 s, of which 133 s were 14,648 calls of _nearest_sight_cell, each fancy-indexing a fresh copy of
# the whole alive-cell matrix (1,767 × 144 float64 = 2 MB) before one matvec — 29 GB of copies per think, growing with episodes × cells.
# The hoist: `ids` and `M = cells[ids]` (and the per-cell answer map) are computed ONCE per induce() call; `M @ x` per episode is the
# same contiguous bytes through the same BLAS call, so the decision is byte-identical (pinned here against the untouched twin and
# against a verbatim copy of the pre-hoist loop; the real-tape gate is the replay of seam-1's 2 h smoke tape).
from __future__ import annotations

import unittest
from typing import Dict, List
from unittest import mock

import numpy as np

from genome import think, world
from genome.fast import Episodes
from genome.machinery import Organism, retina

from ._toy import mini_genome


def _life(seed: int = 2):
    g = mini_genome(nmax=200, budget=400)
    things = ["circle", "square", "triangle"]
    rng = np.random.default_rng(seed)
    dev = world.stream(things, 20, rng, side=24)
    org = Organism(g)
    ep = Episodes(cap=1000, dim_s=g.sight_dim(), dim_w=g.words_dim())
    for t, pic in dev:
        x_s = retina(pic, g.retina)
        x_w = world.encode_word(t, g.ear_blank_zero)
        org.moment(x_s, x_w)
        ep.write(moment=org.t - 1, x_s=x_s, x_w=x_w, word=t, surprise=float(org.t))
    return g, org, ep


def _induce_reference(episodes, k: int, org: Organism) -> List[Dict[str, object]]:
    """The pre-hoist loop, verbatim (genome/think.py induce() as of 34f97f4), minus the FILE call: returns (word, cluster, agree,
    disagree, episode ids) per word so the decision — not the filed row's prose — is what the pin compares."""
    out = []
    if episodes is None or len(episodes) == 0:
        return out
    words_seen = sorted(set(str(episodes.word[i]) for i in range(len(episodes)) if str(episodes.word[i])))
    for word in words_seen:
        r = org.recall("words", world.encode_word(word, org.g.ear_blank_zero))
        word_cell = r["lit"]
        if word_cell is None:
            continue
        C = sorted(int(c) for c in org.sight.alive_ids() if org._answer_of(org.sight, int(c)) == word_cell)
        agree = disagree = 0
        ep_ids: List[int] = []
        for i in range(len(episodes)):
            if str(episodes.word[i]) != word:
                continue
            nearest = think._nearest_sight_cell(org, episodes.x_s[i])
            if nearest is None:
                continue
            if nearest in C:
                agree += 1
                ep_ids.append(int(episodes.ids[i]))
            else:
                disagree += 1
        if agree >= k and disagree == 0 and C:
            out.append((word, C, agree, disagree, ep_ids))
    return out


class TestNearestInEqualsNearestSightCell(unittest.TestCase):
    def test_hoisted_lookup_equals_the_per_call_lookup_on_every_input(self) -> None:
        g, org, ep = _life()
        ids = org.sight.alive_ids(); M = org.sight.cells[ids]
        rng = np.random.default_rng(7)
        xs = [ep.x_s[i] for i in range(len(ep))] + [v / np.linalg.norm(v) for v in rng.normal(size=(100, g.sight_dim()))]
        for x in xs:
            self.assertEqual(think._nearest_in(ids, M, x), think._nearest_sight_cell(org, x))

    def test_empty_ids_gives_none_like_the_twin(self) -> None:
        g, org, ep = _life()
        x = ep.x_s[0]
        self.assertIsNone(think._nearest_in(np.zeros(0, dtype=np.int64), np.zeros((0, g.sight_dim())), x))


class TestInduceHoisted(unittest.TestCase):
    def test_induce_no_longer_calls_the_per_episode_copy(self) -> None:
        g, org, ep = _life()
        with mock.patch.object(think, "_nearest_sight_cell", wraps=think._nearest_sight_cell) as spy:
            think.induce(ep, 3, org)
        self.assertEqual(spy.call_count, 0, "induce must use the hoisted matrix, never the per-episode copy")

    def test_induce_decisions_are_byte_identical_to_the_pre_hoist_loop(self) -> None:
        for seed in (2, 3, 4):
            g, org, ep = _life(seed)
            ref = _induce_reference(ep, 3, org)
            got = [(r["word"], r["cluster"], r["agree"], r["disagree"], r["episodes"]) for r in think.induce(ep, 3, org)]
            self.assertEqual(got, ref, f"seed {seed}")
            self.assertTrue(ref or got == [], "the pin must see at least one induced rule on some seed")


if __name__ == "__main__":
    unittest.main()
