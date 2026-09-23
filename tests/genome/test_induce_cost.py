# edit: Claude (Opus 5.5, INDUCE-COST builder), 2026-09-23 14:07 +0400 — new: INDUCE made cheap WITHOUT changing one decision
# (stamp corrected 2026-09-23 15:19 +0400 from `stat` — the file was written 14:05–14:07:11; the first stamp typed here read 14:12, AHEAD of the clock, #50)
# (docs/briefs/INDUCE-COST-0923-REPORT.md). The finding (A4L-COST-REPORT §0.5): genome/think.py:induce, run on the MIND thread every THINK
# boundary, was 57.9 % of a canvas at 6,896 x 753 (a 5.03 s median stall a think): a Python scan of the WHOLE ring per distinct word
# (752 x 10,160 string compares), one gemv per worded episode, a cluster pass per word over every alive sight cell.
# The change is an INDEX plus three EXACT EARLY EXITS, each read off the emission predicate `agree >= k and disagree == 0 and C`:
#   index   — the ring is walked ONCE (word -> its slots, ascending: the order the old per-word scan visited them); the answer map is
#             inverted ONCE (answer cell -> the alive sight cells answering it, ascending: the old per-word `sorted(...)` pass).
#   exit 1  — a word with fewer than k episodes files nothing (agree <= its slot count < k): recall() is not asked (recall is pure:
#             it never writes the organism) — the ear's encode_word() IS still called for every word, in order, so an unhearable word
#             raises exactly where it raised before.
#   exit 2  — a word whose cluster is empty files nothing (the old `and C`): no gemv for it.
#   exit 3  — a word stops at its FIRST counter-example (disagree > 0 already refuses the rule; the rest cannot change that).
# Every nearest that feeds a decision is still the SAME call — `_nearest_in(ids, M, episodes.x_s[i])` with ids/M built by the same two
# lines — so the float path (the gemv's own sum order and rounding) is untouched. REFUSED, by measurement (scratch/toy/*_probe.py):
# a batched gemm (a different sum order), a per-row dot (a row's value inside the gemv differs from the same row alone), and a nearest
# cached across thinks (one appended row moved another row's gemv value in 902 of 2,000 random alive matrices; one removed row in 1,780).
"""test_induce_cost.py — the INDUCE-COST pin: the new induce() against master 2357347's induce() (its SOURCE TEXT, exec'd verbatim and
pinned by sha256), on a toy whose ring carries every road the index and the early exits could get wrong — planted, and each plant's
POWER asserted (a plant that plants nothing passes every comparison, #91/#175):
  * a WRAPPED ring (cap 40, 55 writes): slot order != id order, so a rule's `episodes` list pins the slot-order walk;
  * EXACTLY k episodes (filed) and k-1 (not filed): the `len(slots) < k` exit's boundary;
  * an EMPTY cluster (a word heard once on another word's picture: its word cell is born, no sight cell answers it);
  * a counter-example at a word's FIRST slot, and one AFTER k agreements at its LAST slot (a scan that stopped at k would file it);
  * two words lighting the SAME word cell (dog/zog, bat/bar): equal clusters, never the same list object;
  * an EXACT tie (two cells = the same basis vector; argmax's first index decides the verdict);
  * a ONE-ULP near-tie (a float32 path would tie and flip the verdict);
  * a LAST-BIT road: two rows whose exact dot products are EQUAL (math.fsum) while the gemv rounds them apart — the verdict exists
    only because of the gemv's own rounding, so "identical outputs" here is a statement about the float path;
  * an unhearable word (> 8 letters) with ONE episode: both versions must raise the same ValueError.
The spies (written RED on master): recall() only for words that can file; no gemv for a word that cannot file; none after a word's
first counter-example."""
from __future__ import annotations

import hashlib
import json
import math
import unittest
from typing import Dict, List, Optional
from unittest import mock

import numpy as np

from genome import think, world
from genome.fast import Episodes
from genome.machinery import Organism
from genome.predict import file as _predict_file

from ._toy import SIGHT_DIM, mini_genome

# ------------------------------------------------------------------------------------------ the twin: master 2357347's own text
# genome/think.py lines 397-458 at commit 2357347 (`_nearest_in` and `induce`), byte for byte (`sed -n 397,458p`); exec'd in its own
# namespace so the twin can never follow a later edit of genome/think.py.
MASTER_2357347_INDUCE_SRC = r'''def _nearest_in(ids: np.ndarray, M: np.ndarray, x: np.ndarray) -> Optional[int]:
    """_nearest_sight_cell over a HOISTED alive matrix: `ids = org.sight.alive_ids()` and `M = org.sight.cells[ids]` computed once
    by the caller. The same contiguous bytes through the same matvec, so the answer is bit-identical to the per-call twin
    (tests/genome/test_induce_hoist.py pins it on every episode + 100 random vectors; the real-tape gate is the replay of
    g5-seam-1's 2 h smoke tape). edit: Claude (Fable 5.1), 2026-09-22 11:0x +0400 — profiled on the closed seam life's end state:
    one think = 147 s, 133 s of them 14,648 fresh 2 MB copies of the alive matrix, one per episode."""
    if len(ids) == 0:
        return None
    cos = M @ x
    return int(ids[int(np.argmax(cos))])


# ============================================================================ INDUCE
def induce(episodes, k: int, org: Organism) -> List[Dict[str, object]]:
    """PREREG row 4d: INDUCE rule from <n> episodes no counter — a rule W => cluster C when >= k
    episodes agree and none disagrees (decision 1 above). Returns FILE-ready rows (predict.file()'s
    shape: {"accepted", "refused", "row", "outcome"} plus "word"/"cluster"/"agree"/"disagree"). An
    induced rule (agree>=k, disagree==0) is always ROUTABLE — C is non-empty by construction (an empty
    cluster cannot ever accumulate an agreeing episode) — so every row this function emits is accepted;
    the "REFUSED by name" case belongs to deduce() (decision 2)."""
    rules: List[Dict[str, object]] = []
    if episodes is None or len(episodes) == 0:
        return rules
    words_seen = sorted(set(str(episodes.word[i]) for i in range(len(episodes)) if str(episodes.word[i])))
    # edit: Claude (Fable 5.1), 2026-09-22 11:0x +0400 — the alive matrix and each alive cell's answer are read ONCE per call (induce never
    # writes the organism, so they cannot move inside it); before, every episode fancy-indexed a fresh 2 MB copy (see _nearest_in).
    ids = org.sight.alive_ids(); M = org.sight.cells[ids]
    answer_of = {int(c): org._answer_of(org.sight, int(c)) for c in ids}
    for word in words_seen:
        r = org.recall("words", world.encode_word(word, org.g.ear_blank_zero))
        word_cell = r["lit"]   # edit: Claude (Fable 5.1), 2026-09-21 15:14 +0400 — was r["cell"], the SIGHT cell the word recalls; _answer_of(sight, c) is a WORDS index, so the
        #                        cluster compared a sight id to a words index (2/21 words clustered on life 3, both the WRONG cells). r["lit"] is the word's own cell.
        if word_cell is None:
            continue  # the organism itself abstains on this word — nothing to cluster against
        C = sorted(c for c in answer_of if answer_of[c] == word_cell)
        agree = disagree = 0
        ep_ids: List[int] = []
        for i in range(len(episodes)):
            if str(episodes.word[i]) != word:
                continue
            nearest = _nearest_in(ids, M, episodes.x_s[i])
            if nearest is None:
                continue
            if nearest in C:
                agree += 1
                ep_ids.append(int(episodes.ids[i]))
            else:
                disagree += 1
        if agree >= k and disagree == 0 and C:
            row = _file(
                claim=f'"{word}" resonates cluster {C}',
                route=f"recall(sight) on the next episode with word {word!r}",
                decider=f"recall(sight) in cluster {C}",
                due=f"moment {org.t}",
            )
            row["word"] = word
            row["cluster"] = C
            row["agree"] = agree
            row["disagree"] = disagree
            row["episodes"] = ep_ids
            rules.append(row)
    return rules
'''
MASTER_2357347_INDUCE_SHA256 = "6ae21f95760bad915fada85cd44aa3213baf1eb808d61c4f558709a278836994"


def _load_twin():
    ns = {"np": np, "Optional": Optional, "List": List, "Dict": Dict, "Organism": Organism, "world": world, "_file": _predict_file}
    exec(compile(MASTER_2357347_INDUCE_SRC, "<genome/think.py@2357347:397-458>", "exec"), ns)
    return ns["induce"], ns["_nearest_in"]


_induce_twin, _nearest_in_twin = _load_twin()

K = 3
TRAIN = ["ant", "asp", "elk", "ape", "zogA", "zogB", "bar", "cat", "dog", "fox", "owl", "hen", "yak"]
WORD_OF = {"zogA": "zog", "zogB": "zog"}
E17 = np.zeros(SIGHT_DIM); E17[17] = 1.0
E29 = np.zeros(SIGHT_DIM); E29[29] = 1.0


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def _jit(rng, v, s=0.02):
    return _unit(v + rng.normal(scale=s, size=v.shape))


def _leaf_types(o):
    """Every leaf's TYPE, in order — `==` alone would read an np.int64 and an int as the same value."""
    if isinstance(o, dict):
        return [(k, _leaf_types(v)) for k, v in sorted(o.items())]
    if isinstance(o, (list, tuple)):
        return [type(o).__name__, [_leaf_types(v) for v in o]]
    return type(o).__name__


class Toy:
    """The trained organism, the planted cells and the wrapped ring — built once per test (a few ms)."""

    def __init__(self, seed: int = 11):
        rng = np.random.default_rng(seed)
        self.org = org = Organism(mini_genome())
        self.base = base = {b: _unit(rng.normal(size=SIGHT_DIM)) for b in TRAIN}
        xw = lambda w: world.encode_word(w, org.g.ear_blank_zero)
        for _ in range(6):
            for b in TRAIN:
                org.moment(_jit(rng, base[b]), xw(WORD_OF.get(b, b)))
        org.moment(_jit(rng, base["owl"]), xw("emu"))        # emu: heard ONCE, on owl's picture — its word cell is born, nobody answers it
        self.cell = {b: think._nearest_sight_cell(org, base[b]) for b in TRAIN}   # the sight cell each base picture was born into
        assert len(set(self.cell.values())) == len(TRAIN), f"two base pictures share a sight cell: {self.cell}"
        # the plants (cells only — W/mask, and so every answer, untouched):
        org.sight.cells[self.cell["ant"]] = E17; org.sight.cells[self.cell["hen"]] = E17          # EXACT tie, ant's id lower
        org.sight.cells[self.cell["asp"]] = np.nextafter(1.0, 0.0) * E29                           # ONE-ULP near-tie: asp (lower id) one ulp under
        org.sight.cells[self.cell["owl"]] = E29
        self.x_lastbit = self._plant_last_bit(rng)                                                  # elk vs ape, decided by the gemv's rounding
        ring = [("", _jit(rng, base["bar"])) for _ in range(15)]                                   # ids 0-14: overwritten by 40-54
        ring[3] = ("bar", _jit(rng, base["bar"]))                                                   # an overwritten bar: must count nowhere
        ring += [("", _jit(rng, base["cat"])) for _ in range(5)]                                   # 15-19 sight-only
        ring += [("bar", _jit(rng, base["bar"]))]                                                   # 20
        ring += [("bat", _jit(rng, base["bar"])) for _ in range(3)]                                # 21-23: bat lights bar's word cell
        ring += [("fox", _jit(rng, base["yak"]))]                                                   # 24: fox's counter-example, its FIRST slot
        ring += [("fox", _jit(rng, base["fox"])) for _ in range(3)]                                # 25-27
        ring += [("yak", _jit(rng, base["yak"])) for _ in range(3)]                                # 28-30: k agreements ...
        ring += [("yak", _jit(rng, base["cat"]))]                                                   # 31: ... then a counter-example, its LAST slot
        ring += [("cat", _jit(rng, base["cat"])) for _ in range(2)]                                # 32-33: k-1
        ring += [("emu", _jit(rng, base["yak"])) for _ in range(3)]                                # 34-36: an empty cluster
        ring += [("zog", _jit(rng, base[b])) for b in ("zogA", "zogB", "zogA")]                   # 37-39
        ring += [("dog", _jit(rng, base["dog"])) for _ in range(2)]                                # 40-41: dog lights zog's word cell
        ring += [("bar", _jit(rng, base["bar"]))]                                                   # 42
        ring += [("dog", _jit(rng, base["dog"]))]                                                   # 43
        ring += [("bar", _jit(rng, base["bar"]))]                                                   # 44
        ring += [("hen", E17.copy()) for _ in range(3)]                                            # 45-47: the exact tie
        ring += [("owl", E29.copy()) for _ in range(3)]                                            # 48-50: the one-ulp near-tie
        ring += [("ape", self.x_lastbit.copy()) for _ in range(3)]                                 # 51-53: the last-bit road
        ring += [("", _jit(rng, base["cat"]))]                                                      # 54
        assert len(ring) == 55
        self.ep = self._ring(ring, cap=40)

    def _ring(self, rows, cap):
        ep = Episodes(cap=cap, dim_s=self.org.g.sight_dim(), dim_w=self.org.g.words_dim())
        for t, (w, x) in enumerate(rows):
            try:
                xw = world.encode_word(w, self.org.g.ear_blank_zero) if w else np.zeros(self.org.g.words_dim())
            except ValueError:
                xw = np.zeros(self.org.g.words_dim())      # an unhearable word's x_w: induce never reads x_w
            ep.write(moment=t, x_s=x, x_w=xw, word=w, surprise=0.0)
        return ep

    def _plant_last_bit(self, rng) -> np.ndarray:
        """elk (lower id, answers elk) and ape (answers ape): b = a with components i, j swapped where x_i == x_j, so the EXACT dot
        products are equal (the same rounded products, summed in a different order); searched until the gemv induce runs — `M @ x`
        over the FINAL alive matrix (a row's value depends on the other rows) — puts ape strictly above elk and both above every row."""
        org = self.org
        a_id, b_id = self.cell["elk"], self.cell["ape"]
        for _ in range(5000):
            x = rng.normal(size=SIGHT_DIM)
            i, j = (int(v) for v in rng.choice(SIGHT_DIM, 2, replace=False))
            x[j] = x[i]
            x = _unit(x)
            a = _unit(x + 0.05 * rng.normal(size=SIGHT_DIM))
            b = a.copy(); b[i], b[j] = a[j], a[i]
            org.sight.cells[a_id] = a; org.sight.cells[b_id] = b
            ids = org.sight.alive_ids(); c = org.sight.cells[ids] @ x
            pa, pb = int(np.flatnonzero(ids == a_id)[0]), int(np.flatnonzero(ids == b_id)[0])
            others = np.delete(c, [pa, pb])
            if math.fsum(a * x) == math.fsum(b * x) and c[pb] > c[pa] and c[pa] > others.max():
                return x
        raise AssertionError("the last-bit road could not be planted — the toy would test nothing")

    def slots(self, word: str) -> List[int]:
        return [i for i in range(len(self.ep)) if str(self.ep.word[i]) == word]

    def cluster(self, word: str) -> Optional[List[int]]:
        r = self.org.recall("words", world.encode_word(word, self.org.g.ear_blank_zero))
        if r["lit"] is None:
            return None
        return sorted(int(c) for c in self.org.sight.alive_ids() if self.org._answer_of(self.org.sight, int(c)) == r["lit"])


def _slot_of(ep: Episodes, x: np.ndarray) -> int:
    """The ring slot whose x_s row `x` IS (induce passes `episodes.x_s[i]`, a view)."""
    off = x.__array_interface__["data"][0] - ep.x_s.__array_interface__["data"][0]
    assert off % ep.x_s.strides[0] == 0 and x.base is not None
    return off // ep.x_s.strides[0]


def _same(test: unittest.TestCase, got, want, msg: str = "") -> None:
    test.assertEqual(got, want, msg)
    test.assertEqual(json.dumps(got, sort_keys=True), json.dumps(want, sort_keys=True), msg)
    test.assertEqual(_leaf_types(got), _leaf_types(want), msg)


# ============================================================================================ the plants are planted
class TestThePlantsHavePower(unittest.TestCase):
    """Each road the comparison below claims to cover is asserted to EXIST on the toy — else an identical output means nothing."""

    @classmethod
    def setUpClass(cls):
        cls.toy = Toy()

    def test_twin_text_is_master_2357347_byte_for_byte(self):
        self.assertEqual(hashlib.sha256(MASTER_2357347_INDUCE_SRC.encode()).hexdigest(), MASTER_2357347_INDUCE_SHA256)

    def test_the_ring_is_wrapped_so_slot_order_is_not_id_order(self):
        ep = self.toy.ep
        self.assertEqual((ep.n_written, len(ep)), (55, 40))
        self.assertEqual([int(ep.ids[i]) for i in self.toy.slots("bar")], [42, 44, 20])

    def test_id_spaces_are_disjoint(self):
        """#234 (1): a sight id that equalled its word index would hide a key confusion."""
        for w in ("bar", "yak", "owl"):
            r = self.toy.org.recall("words", world.encode_word(w, self.toy.org.g.ear_blank_zero))
            self.assertNotEqual(r["cell"], r["lit"], w)

    def test_boundaries_empty_cluster_and_shared_word_cells(self):
        t = self.toy
        self.assertEqual(len(t.slots("bar")), K); self.assertEqual(len(t.slots("cat")), K - 1)
        self.assertEqual(t.cluster("emu"), [])
        self.assertIsNotNone(t.cluster("emu"))
        self.assertEqual(t.cluster("dog"), t.cluster("zog")); self.assertEqual(t.cluster("bat"), t.cluster("bar"))
        self.assertTrue(t.cluster("bar"))

    def test_counter_examples_sit_first_and_last(self):
        t = self.toy; ids = t.org.sight.alive_ids(); M = t.org.sight.cells[ids]
        def verdicts(w):
            C = t.cluster(w)
            return [_nearest_in_twin(ids, M, t.ep.x_s[i]) in C for i in t.slots(w)]
        self.assertEqual(verdicts("fox"), [False, True, True, True])
        self.assertEqual(verdicts("yak"), [True, True, True, False])      # a scan that stopped at k agreements would file yak

    def test_the_exact_tie_decides_hen(self):
        t = self.toy; ids = t.org.sight.alive_ids(); M = t.org.sight.cells[ids]
        c = M @ E17
        pa, ph = (int(np.flatnonzero(ids == t.cell[b])[0]) for b in ("ant", "hen"))
        self.assertEqual(c[pa], c[ph]); self.assertEqual(c.max(), c[pa]); self.assertLess(pa, ph)
        self.assertEqual(_nearest_in_twin(ids, M, E17), t.cell["ant"])    # first index wins: hen DISAGREES
        self.assertEqual(ids[len(c) - 1 - int(np.argmax(c[::-1]))], t.cell["hen"])   # a last-index tie-break would file hen

    def test_the_one_ulp_near_tie_decides_owl(self):
        t = self.toy; ids = t.org.sight.alive_ids(); M = t.org.sight.cells[ids]
        self.assertEqual(_nearest_in_twin(ids, M, E29), t.cell["owl"])
        c32 = M.astype(np.float32) @ E29.astype(np.float32)
        self.assertEqual(int(ids[int(np.argmax(c32))]), t.cell["asp"])  # a float32 path ties and flips owl's verdict

    def test_the_last_bit_road_decides_ape(self):
        t = self.toy; ids = t.org.sight.alive_ids(); M = t.org.sight.cells[ids]; x = t.x_lastbit
        a, b = t.org.sight.cells[t.cell["elk"]], t.org.sight.cells[t.cell["ape"]]
        self.assertEqual(math.fsum(a * x), math.fsum(b * x))               # equal in exact arithmetic ...
        self.assertEqual(_nearest_in_twin(ids, M, x), t.cell["ape"])       # ... the gemv's rounding puts ape first
        exact = [math.fsum(row * x) for row in M]
        self.assertEqual(int(ids[int(np.argmax(exact))]), t.cell["elk"])  # an exact-arithmetic path ties and flips ape's verdict

    def test_the_twin_files_what_the_plants_say(self):
        rules = _induce_twin(self.toy.ep, K, self.toy.org)
        self.assertEqual([r["word"] for r in rules], ["ape", "bar", "bat", "dog", "owl", "zog"])
        bar = [r for r in rules if r["word"] == "bar"][0]
        self.assertEqual((bar["agree"], bar["episodes"]), (K, [42, 44, 20]))


# ============================================================================================ identity: every field, every k
class TestInduceEqualsMaster2357347(unittest.TestCase):
    def test_the_toy_every_k(self):
        toy = Toy()
        for k in (0, 1, 2, 3, 4, 5):
            _same(self, think.induce(toy.ep, k, toy.org), _induce_twin(toy.ep, k, toy.org), f"k={k}")

    def test_other_seeds(self):
        for seed in (12, 13, 14):
            toy = Toy(seed)
            _same(self, think.induce(toy.ep, K, toy.org), _induce_twin(toy.ep, K, toy.org), f"seed={seed}")

    def test_random_rings(self):
        """40 random rings over the toy's vocabulary (+ words that light another word's cell, + words that light nothing), random
        pictures (a base's jitter, a planted vector, or noise), random caps (wrapped or not) and k."""
        toy = Toy()
        rng = np.random.default_rng(20260923)
        b = toy.base
        own = {"ape": toy.x_lastbit, "bar": b["bar"], "bat": b["bar"], "cat": b["cat"], "dog": b["dog"], "emu": b["yak"], "fox": b["fox"],
               "hen": E17, "owl": E29, "yak": b["yak"], "zog": b["zogA"], "ant": E17, "asp": b["asp"], "elk": b["elk"], "qux": b["cat"], "zzz": b["fox"], "": b["cat"]}
        vocab = sorted(own)
        pics = [b[t] for t in TRAIN] + [E17, E29, toy.x_lastbit]
        filed = 0
        for trial in range(40):
            cap = int(rng.integers(5, 60)); n = int(rng.integers(0, 90))
            rows = []
            for _ in range(n):
                w = vocab[int(rng.integers(0, len(vocab)))]
                u = rng.random()
                if u < 0.45:
                    x = own[w].copy()                                                     # the word's own picture, exact (ties live here)
                elif u < 0.9:
                    x = _jit(rng, own[w], 0.01)                                           # its own picture, jittered
                elif u < 0.97:
                    x = _jit(rng, pics[int(rng.integers(0, len(pics)))], 0.01)          # another word's picture: a counter-example
                else:
                    x = _unit(rng.normal(size=SIGHT_DIM))                                 # noise
                rows.append((w, x))
            ep = toy._ring(rows, cap)
            for k in (1, 2, 3, 4):
                got, want = think.induce(ep, k, toy.org), _induce_twin(ep, k, toy.org)
                _same(self, got, want, f"trial {trial} cap {cap} n {n} k {k}")
                filed += len(want)
        self.assertGreater(filed, 50, "the random rings must file rules, or they compare empty lists")

    def test_none_and_empty(self):
        toy = Toy()
        self.assertEqual(think.induce(None, K, toy.org), [])
        empty = Episodes(cap=10, dim_s=toy.org.g.sight_dim(), dim_w=toy.org.g.words_dim())
        self.assertEqual(think.induce(empty, K, toy.org), _induce_twin(empty, K, toy.org))

    def test_no_alive_sight_cell(self):
        toy = Toy()
        toy.org.sight.alive[:] = 0
        _same(self, think.induce(toy.ep, K, toy.org), _induce_twin(toy.ep, K, toy.org))

    def test_an_unhearable_word_raises_the_same_error(self):
        """encode_word refuses > 8 letters. The old loop encoded EVERY word; a word with one episode (it can never file) must still
        raise, at the same word."""
        toy = Toy()
        rows = [("bar", _jit(np.random.default_rng(1), toy.base["bar"])) for _ in range(4)] + [("verylongword", toy.base["cat"].copy())]
        ep = toy._ring(rows, 20)
        with self.assertRaises(ValueError) as twin:
            _induce_twin(ep, K, toy.org)
        with self.assertRaises(ValueError) as new:
            think.induce(ep, K, toy.org)
        self.assertEqual(str(new.exception), str(twin.exception))

    def test_clusters_are_never_shared_list_objects(self):
        toy = Toy()
        rules = {r["word"]: r for r in think.induce(toy.ep, K, toy.org)}
        self.assertEqual(rules["dog"]["cluster"], rules["zog"]["cluster"])
        self.assertIsNot(rules["dog"]["cluster"], rules["zog"]["cluster"])
        self.assertIsNot(rules["bat"]["cluster"], rules["bar"]["cluster"])
        rules["dog"]["cluster"].append(-1)
        self.assertNotIn(-1, rules["zog"]["cluster"])

    def test_induce_writes_nothing(self):
        toy = Toy()
        h0 = toy.org.state_hash()
        ring0 = hashlib.sha256(toy.ep.x_s.tobytes() + toy.ep.word.tobytes() + toy.ep.ids.tobytes()).hexdigest()
        think.induce(toy.ep, K, toy.org)
        self.assertEqual(toy.org.state_hash(), h0)
        self.assertEqual(hashlib.sha256(toy.ep.x_s.tobytes() + toy.ep.word.tobytes() + toy.ep.ids.tobytes()).hexdigest(), ring0)


# ============================================================================================ negative controls: the pin CATCHES
class TestThePinCatchesPlantedDefects(unittest.TestCase):
    """A comparison that cannot fail is not a pin (#91): each planted defect below must make think.induce DIFFER from the twin."""

    def _differs(self, fn):
        toy = Toy()
        got = fn(toy)
        want = _induce_twin(toy.ep, K, toy.org)
        self.assertNotEqual(json.dumps(got, sort_keys=True), json.dumps(want, sort_keys=True))

    def test_a_last_index_tie_break_is_caught(self):
        def last(ids, M, x):
            c = M @ x
            return None if len(ids) == 0 else int(ids[len(c) - 1 - int(np.argmax(c[::-1]))])
        self._differs(lambda toy: self._patched(toy, last))

    def test_a_float32_path_is_caught(self):
        def f32(ids, M, x):
            return None if len(ids) == 0 else int(ids[int(np.argmax(M.astype(np.float32) @ x.astype(np.float32)))])
        self._differs(lambda toy: self._patched(toy, f32))

    def test_an_exact_arithmetic_path_is_caught(self):
        def exact(ids, M, x):
            return None if len(ids) == 0 else int(ids[int(np.argmax([math.fsum(r * x) for r in M]))])
        self._differs(lambda toy: self._patched(toy, exact))

    def test_the_old_sight_cell_key_is_caught(self):
        def run(toy):
            real = toy.org.recall
            def swapped(side, x, k=1):
                r = dict(real(side, x, k)); r["lit"] = r["cell"]; return r
            with mock.patch.object(toy.org, "recall", side_effect=swapped):
                return think.induce(toy.ep, K, toy.org)
        self._differs(run)

    def test_id_order_instead_of_slot_order_is_caught(self):
        def run(toy):
            rules = think.induce(toy.ep, K, toy.org)
            for r in rules:
                r["episodes"] = sorted(r["episodes"])
            return rules
        self._differs(run)

    @staticmethod
    def _patched(toy, fn):
        with mock.patch.object(think, "_nearest_in", side_effect=fn):
            return think.induce(toy.ep, K, toy.org)


# ============================================================================================ the spies (RED on master)
class TestInduceDoesOnlyTheWorkThatCanFile(unittest.TestCase):
    def test_recall_only_for_words_with_at_least_k_episodes(self):
        toy = Toy()
        real = toy.org.recall
        asked: List[str] = []
        enc = {world.encode_word(w, toy.org.g.ear_blank_zero).tobytes(): w for w in ("ape", "bar", "bat", "cat", "dog", "emu", "fox", "hen", "owl", "yak", "zog")}
        def spy(side, x, k=1):
            asked.append(enc.get(np.asarray(x).tobytes(), "?")); return real(side, x, k)
        with mock.patch.object(toy.org, "recall", side_effect=spy):
            think.induce(toy.ep, K, toy.org)
        self.assertEqual(asked, ["ape", "bar", "bat", "dog", "emu", "fox", "hen", "owl", "yak", "zog"])   # cat (k-1) never asked

    def test_no_gemv_for_a_word_that_cannot_file_and_none_after_a_counter_example(self):
        toy = Toy()
        seen: List[int] = []
        real = think._nearest_in
        def spy(ids, M, x):
            seen.append(_slot_of(toy.ep, x)); return real(ids, M, x)
        with mock.patch.object(think, "_nearest_in", side_effect=spy):
            think.induce(toy.ep, K, toy.org)
        per_word: Dict[str, int] = {}
        for s in seen:
            w = str(toy.ep.word[s]); per_word[w] = per_word.get(w, 0) + 1
        self.assertEqual(per_word, {"ape": 3, "bar": 3, "bat": 3, "dog": 3, "fox": 1, "hen": 1, "owl": 3, "yak": 4, "zog": 3})
        self.assertEqual(len(seen), len(set(seen)), "no episode is asked twice")


if __name__ == "__main__":
    unittest.main()
