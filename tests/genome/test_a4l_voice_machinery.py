# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:31 +0400 — A4L-VOICE task 2 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3): the sound area and its two meetings, at the machinery. Every consumer of «the areas»
# and «the edge matrix» widens (SOLUTIONS #235): the hash (an EMPTY sound area is HASH-NEUTRAL), save/load (an old
# snapshot loads), GROW, build_ledgers (a sound birth is filed as SOUND), recall/recall_many for the new sides — and the
# sight↔words road is untouched by a voice (the W path's own state identical with and without sound on the same stream).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import machinery
from genome.machinery import Organism, parse_genome
from genome.questions import build_ledgers

BASE = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.5
BIRTH error misfires 3
BUDGET 400 per arrival
NMAX 200
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 7 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""
SOUND = "AREA sound from cochlea cos>=0.975\nMEET sight sound\nMEET sound words\n"
S_DIM, W_DIM, SND_DIM = 64, 208, 37


def genome(sound: bool = True, grow: bool = False, budget: int = 400):
    t = BASE.replace("BUDGET 400", f"BUDGET {budget}")
    if grow:
        t = t.replace("NMAX 200\n", "GROW unbounded\n")
    return parse_genome(t + (SOUND if sound else ""))


def unit(rng, d):
    v = rng.normal(size=d)
    return v / np.linalg.norm(v)


def world(seed: int = 7, things: int = 4):
    """Each thing: a sight prototype (64-d), a word (208-d), a chord (37-d, mutually far below 0.975)."""
    rng = np.random.default_rng(seed)
    return [(unit(rng, S_DIM), unit(rng, W_DIM), unit(rng, SND_DIM)) for _ in range(things)]


def glance(rng, proto, noise=0.15):
    return machinery._unit(proto + noise * rng.normal(size=proto.shape))


class TestHashNeutral(unittest.TestCase):
    def test_empty_sound_area_is_hash_neutral_at_every_moment(self) -> None:
        a, b = Organism(genome(sound=False)), Organism(genome(sound=True))
        rng = np.random.default_rng(1); W = world()
        for i in range(60):
            xs, xw, _c = W[i % 4]
            x = glance(rng, xs)
            a.moment(x, xw); b.moment(x, xw)
            self.assertEqual(a.state_hash(), b.state_hash(), f"moment {i}")
        self.assertEqual(a.c, b.c, "self.c never gains a key from a declared-but-silent sound area")

    def test_empty_sound_area_is_hash_neutral_under_grow(self) -> None:
        a, b = Organism(genome(sound=False, grow=True)), Organism(genome(sound=True, grow=True))
        rng = np.random.default_rng(2); W = world()
        for i in range(40):
            xs, xw, _c = W[i % 4]
            x = glance(rng, xs); a.moment(x, xw); b.moment(x, xw)
        self.assertEqual(a.state_hash(), b.state_hash())

    def test_a_sound_moves_the_hash(self) -> None:
        a, b = Organism(genome()), Organism(genome())
        xs, xw, c = world()[0]
        a.moment(xs, xw); b.moment(xs, xw, x_snd=c)
        self.assertNotEqual(a.state_hash(), b.state_hash())


class TestSoundArea(unittest.TestCase):
    def test_novelty_birth_resonance_and_the_one_budget(self) -> None:
        org = Organism(genome()); W = world()
        xs, xw, c = W[0]
        budget0 = org.budget_left
        org.moment(xs, xw, x_snd=c)
        self.assertEqual(org.sound.n, 1)
        self.assertIn((0, "sound", 0, "novelty"), org.births)
        self.assertEqual(org.c_sound["births_novelty_sound"], 1)
        self.assertEqual(budget0 - org.budget_left, org.sight.n + org.words.n + org.sound.n, "a sound birth spends the ONE budget")
        org.moment(xs, xw, x_snd=c)
        self.assertEqual(org.sound.n, 1, "the same chord resonates its own cell (cos 1.0 >= 0.975): no birth")
        org.moment(W[1][0], W[1][1], x_snd=W[1][2])
        self.assertEqual(org.sound.n, 2, "another chord (cos << 0.975) is born")
        self.assertNotIn("births_novelty_sound", org.c, "sound counters live in c_sound, never self.c")

    def test_a_refused_sound_birth_is_counted_twice(self) -> None:
        org = Organism(genome(budget=2)); W = world()
        org.moment(W[0][0], W[0][1], x_snd=W[0][2])      # sight + words spend the 2
        self.assertEqual(org.budget_left, 0)
        self.assertEqual(org.sound.n, 0)
        self.assertEqual(org.c["births_refused_budget"], 1, "the one budget's own counter")
        self.assertEqual(org.c_sound["births_refused_budget_sound"], 1, "and the sound's attribution")

    def test_the_w_path_is_untouched_by_a_voice(self) -> None:
        """Same (sight, word) stream, one organism also hears each thing's chord: every array and counter of the
        sight↔words road is identical (the budget never binds here) — the voice adds a road, never moves the old one."""
        a, b = Organism(genome()), Organism(genome())
        rng1, rng2 = np.random.default_rng(3), np.random.default_rng(3); W = world(things=5)
        for i in range(120):
            k = (i * 7) % 5
            x1 = glance(rng1, W[k][0], 0.35); x2 = glance(rng2, W[k][0], 0.35)
            a.moment(x1, W[k][1]); b.moment(x2, W[k][1], x_snd=W[k][2])
        for name in ("cells", "alive", "misfires"):
            for area in ("sight", "words"):
                np.testing.assert_array_equal(getattr(getattr(a, area), name), getattr(getattr(b, area), name), f"{area}.{name}")
        np.testing.assert_array_equal(a.W, b.W); np.testing.assert_array_equal(a.mask, b.mask); np.testing.assert_array_equal(a.strikes, b.strikes)
        self.assertEqual(a.c, b.c)
        self.assertEqual(a.edges_log, b.edges_log); self.assertEqual(a.prunes_log, b.prunes_log)
        self.assertEqual([x for x in b.births if x[1] != "sound"], a.births)
        self.assertEqual([x for x in b.merges if x[1] != "sound"], a.merges)
        self.assertGreater(b.sound.n, 0); self.assertGreater(len(b.sound_meets["sight-sound"].edges_log), 0)


class TestRecallAcrossSound(unittest.TestCase):
    def _trained(self, blind_words: bool = False, things: int = 4, n: int = 80):
        org = Organism(genome()); W = world(things=things); rng = np.random.default_rng(5)
        moment_thing = {}
        for i in range(n):
            k = i % things
            moment_thing[org.t] = f"t{k}"
            org.moment(glance(rng, W[k][0]), None if blind_words else W[k][1], x_snd=W[k][2])
        return org, W, build_ledgers(org, moment_thing)

    def test_sound_to_sight_to_words_and_back(self) -> None:
        org, W, L = self._trained()
        for k in range(4):
            r = org.recall("sound", W[k][2], to="sight")
            self.assertEqual(r["reason"], "answer", r); self.assertEqual(L["sight"][r["cell"]], {f"t{k}"})
            r = org.recall_many("sight", [W[k][0]], to="sound")
            self.assertEqual(r["reason"], "answer", r); self.assertEqual(L["sound"][r["cell"]], {f"t{k}"})
            r = org.recall("sound", W[k][2], to="words")
            self.assertEqual(r["reason"], "answer", r); self.assertEqual(L["words"][r["cell"]], {f"t{k}"})
        self.assertTrue(all(area in ("sight", "words", "sound") for _m, area, _c, _r in org.births))
        self.assertTrue(set(L["sound"]) and all(len(v) == 1 for v in L["sound"].values()), "a sound birth is filed as SOUND")

    def test_blind_words_the_sight_sound_meeting_still_forms(self) -> None:
        org, W, L = self._trained(blind_words=True)
        self.assertEqual(org.words.n, 0, "no word ever reaches the organism: the words area never lights")
        self.assertEqual(int(org.mask.sum()), 0)
        for k in range(4):
            r = org.recall("sound", W[k][2], to="sight")
            self.assertEqual(r["reason"], "answer", r); self.assertEqual(L["sight"][r["cell"]], {f"t{k}"})

    def test_a_novel_chord_abstains(self) -> None:
        org, W, _L = self._trained()
        r = org.recall("sound", unit(np.random.default_rng(99), SND_DIM), to="sight")
        self.assertEqual(r["reason"], "novel")

    def test_default_recall_never_touches_sound(self) -> None:
        """recall/recall_many with no `to` are the old road: they run on a shadow Organism that has no sound attrs
        (creature/think_thread.py's freeze_recall_view builds exactly such a shadow)."""
        org, W, _L = self._trained()
        shadow = object.__new__(Organism)
        shadow.g = org.g; shadow.W = org.W; shadow.mask = org.mask; shadow.sight = org.sight; shadow.words = org.words
        shadow.births = org.births; shadow.merges = org.merges
        r1 = Organism.recall_many(shadow, "sight", [W[0][0]]); r2 = org.recall_many("sight", [W[0][0]])
        self.assertEqual(r1, r2)

    def test_pair_recall_equals_recall_on_the_same_matrix(self) -> None:
        """«the SAME rules»: the pair road's recall/recall_many, pointed at the sight↔words matrix itself, return
        exactly what recall/recall_many return (one algorithm, two matrices)."""
        org, W, _L = self._trained()
        main = machinery._Pair("sight-words", org.sight, org.words, 1, 1)
        main.W, main.mask, main.strikes = org.W, org.mask, org.strikes
        rng = np.random.default_rng(11)
        for k in range(4):
            xs = [glance(rng, W[k][0]) for _ in range(3)]
            self.assertEqual(org._recall_pair_many(main, "sight", xs), org.recall_many("sight", xs))
            self.assertEqual(org._recall_pair_many(main, "words", [W[k][1]]), org.recall_many("words", [W[k][1]]))
            self.assertEqual(org._recall_pair(main, "sight", xs[0]), org.recall("sight", xs[0]))


class TestMisfireOneChancePerMoment(unittest.TestCase):
    def test_sight_misfires_in_the_sound_meeting_only_when_no_word_met(self) -> None:
        """A cell gets ONE misfire/merge chance a moment, in the first meeting that runs (sight↔words, then
        sight↔sound, then sound↔words). One sight prototype shown with two chords in turn: with its word the sight
        cell's counter is the W road's; with no word the sight↔sound meeting counts it."""
        W = world(things=2)
        seq = [0] * 10 + [1] * 3          # the sight cell learns chord 0, then hears chord 1 three times
        for blind in (False, True):
            org = Organism(genome())
            xs = W[0][0]
            for k in seq:
                org.moment(xs, None if blind else W[0][1], x_snd=W[k][2])
            if blind:
                self.assertGreaterEqual(org.c["births_refused_redundant"], 1,
                                        "blind: the sight cell's sound answer is chord 0 while chord 1 sounds — 3 misfires in "
                                        "sight↔sound, then the error birth (the same x) is refused as redundant")
            else:
                twin = Organism(genome())
                for k in seq:
                    twin.moment(xs, W[0][1])
                np.testing.assert_array_equal(org.sight.misfires, twin.sight.misfires)
                self.assertEqual(org.c, twin.c, "with its word, the sight cell's one chance is the W road's")


class TestMergeCarriesSoundEdges(unittest.TestCase):
    def test_a_w_path_merge_moves_the_dropped_cells_sound_edges(self) -> None:
        org = Organism(genome()); W = world()
        xs, xw, c = W[0]
        org.moment(xs, xw, x_snd=c)
        y = machinery._unit(xs + 1e-3 * np.random.default_rng(1).normal(size=S_DIM))
        b = org._birth(org.sight, y, "novelty"); a = 0
        ss = org.sound_meets["sight-sound"]
        org.mask[b, 0] = 1; org.W[b, 0] = org.W[a, 0]                 # same word answer
        ss.mask[b, 0] = 1; ss.W[b, 0] = 0.4
        org._merge(org.sight, [a, b], axis=0)
        self.assertEqual(int(org.sight.alive[b]), 0)
        self.assertEqual(int(ss.mask[b].sum()), 0); self.assertEqual(float(np.abs(ss.W[b]).sum()), 0.0)
        self.assertEqual(int(ss.mask[a, 0]), 1)


class TestGrowAndSnapshot(unittest.TestCase):
    def test_sound_area_and_pairs_grow(self) -> None:
        old = machinery.GROW_CHUNK
        machinery.GROW_CHUNK = 8
        try:
            org = Organism(genome(grow=True, budget=5000))
            rng = np.random.default_rng(4); xw = unit(rng, W_DIM)
            for i in range(300):
                org.moment(unit(rng, S_DIM), xw, x_snd=unit(rng, SND_DIM))
            self.assertEqual(org.sound.n, 300)
            self.assertGreaterEqual(org.sound.nmax, 300)
            ss = org.sound_meets["sight-sound"]; sw = org.sound_meets["sound-words"]
            self.assertGreaterEqual(ss.W.shape[1], 300); self.assertGreaterEqual(sw.W.shape[0], 300)
            self.assertGreaterEqual(ss.W.shape[0], org.sight.n)
            twin = Organism(genome(grow=True, budget=5000))
            rng = np.random.default_rng(4); xw = unit(rng, W_DIM)
            for i in range(300):
                twin.moment(unit(rng, S_DIM), xw, x_snd=unit(rng, SND_DIM))
            self.assertEqual(org.state_hash(), twin.state_hash(), "a from-scratch recompute of the same stream")
            with tempfile.TemporaryDirectory() as d:
                org.save(Path(d) / "o")
                back = Organism.load(Path(d) / "o", genome(grow=True, budget=5000))
                self.assertEqual(back.state_hash(), org.state_hash())
                self.assertEqual(back.sound.n, 300)
        finally:
            machinery.GROW_CHUNK = old

    def test_an_old_snapshot_loads_under_the_voice_genome(self) -> None:
        org = Organism(genome(sound=False)); W = world(); rng = np.random.default_rng(6)
        for i in range(30):
            org.moment(glance(rng, W[i % 4][0]), W[i % 4][1])
        with tempfile.TemporaryDirectory() as d:
            org.save(Path(d) / "o")
            back = Organism.load(Path(d) / "o", genome(sound=True))
            self.assertEqual(back.state_hash(), org.state_hash())
            self.assertEqual(back.sound.n, 0)

    def test_a_voiced_snapshot_round_trips(self) -> None:
        org = Organism(genome()); W = world(); rng = np.random.default_rng(8)
        for i in range(40):
            org.moment(glance(rng, W[i % 4][0]), W[i % 4][1], x_snd=W[i % 4][2])
        with tempfile.TemporaryDirectory() as d:
            org.save(Path(d) / "o")
            back = Organism.load(Path(d) / "o", genome())
            self.assertEqual(back.state_hash(), org.state_hash())
            for k in range(4):
                self.assertEqual(back.recall("sound", W[k][2], to="sight"), org.recall("sound", W[k][2], to="sight"))


if __name__ == "__main__":
    unittest.main()
