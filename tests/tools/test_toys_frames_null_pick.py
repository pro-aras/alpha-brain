"""Tests for the BYTE-IDENTICAL speed-up of TOY C's NULL-2 pick (`null._BigramPool` against the reference `null._pick_bigram`): the PROOF of identity the seat made the condition of option A.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 22:41 +0400 — written FIRST (red: `_BigramPool` does not exist), after the REAL gates stopped at G5 (predicted unit CPU 182.1 min against the ceiling 40): the
# cost was NULL-2's pick (`null._pick_bigram`: on the real ALPHA4 split 4.46 of 4.89 s for ONE WEB-H NULL-2 draw; 892 of its 1,430 picks ran the 1,000-try rejection loop to its end), not the gain.

THE PROOF (the seat's words, 2026-10-03 22:3x: «a test drives the old and the new pick on the same seeds and the same real count bins, and asserts identical picks AND identical RNG consumption: the
generator's state compared after each draw. A planted one-line change in the new pick must fail it»):
  1. the REFERENCE trace: the old `_pick_bigram` driven exactly as `null2` drives it (a set of excluded frames, `excluded.add(pick)` after each pick, a fresh `excluded = set(base)` each draw), with the
     pick, the fallback flag, the bit-generator STATE after the pick, and the number of scalar `integers()` calls the pick made;
  2. the NEW trace: `_BigramPool` driven the same way (`reset(base)` each draw, `exclude(pick)` after each pick);
  3. the two traces are compared pick by pick: the pick, the flag, the STATE (the whole PCG64 state dict, `has_uint32` and `uinteger` included) and, where the reference raised NullError, the error and
     the state after it. The scenarios: (a) hand-built ones for every branch (a pool of at most 64 enumerated; a pool above 64 with every entry excluded — the doomed loop; with a FEW entries admissible
     out of thousands, where the loop sometimes succeeds late and sometimes fails all 1,000 tries and then enumerates; sizes exactly 64 and 65; two bins at one distance; two doomed levels in one pick;
     a NullError at the end), (b) random ones, and (c) the REAL ALPHA4 count bins and the REAL frame sets of SENTENCE, WEB-H and WEB-S (seed 1) and the plant;
  4. `null2` ITSELF against a reference `null2` that calls the old pick (values, pairs, fallbacks, on real sets): the harness's loop cannot drift from the code's;
  5. the PLANTS: each is a one-line change of the new class's source, loaded in memory; each must be CAUGHT (the plant asserts it changed the bytes); the first (a redraw of one draw too few) changes
     NO pick at the moment of its first difference and only the STATE comparison sees it, which is why the state is in the proof. A control, the unmutated source loaded the same way, must read identical.

Real-data tests need the copies (`python3 -m tools.toys.frames.streams copy`): without them they SKIP, and with `TOYS_REAL_REQUIRED=1` they FAIL instead (the gate's runs set it: a skipped proof is not a pass).
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import os
import unittest
from typing import Dict, List, Sequence, Set, Tuple

import numpy as np

from tools.toys.frames import compress as CO
from tools.toys.frames import null as NL
from tools.toys.frames import plants as PL
from tools.toys.frames import rules as RL
from tools.toys.frames import run as RN
from tools.toys.frames import streams as ST

Frame = Tuple[str, str]
COPIES = ST.REPO / "scratch" / "toys-frames" / "copies"
REAL_OK = (COPIES / "alpha4-1" / "tape").is_dir()
REQUIRED = os.environ.get("TOYS_REAL_REQUIRED") == "1"


# ====================================================================================================================== the two drivers and the comparison
class CountingRng:
    """A transparent proxy that counts the scalar `integers()` calls the REFERENCE pick makes (it uses nothing else of the generator)."""

    def __init__(self, g):
        self.g = g
        self.n = 0

    def integers(self, *a, **k):
        self.n += 1
        return self.g.integers(*a, **k)


def ref_trace(bins: Dict[int, List[Frame]], own: Sequence[int], base: Set[Frame], key: Sequence[int], draws: int) -> List[tuple]:
    """The OLD pick driven as `null2` drives it. Each entry: (pick, fell, state_after, scalar_calls) or ('error', message, state_after, scalar_calls)."""
    lo, hi = min(bins), max(bins)
    g = np.random.default_rng(list(key))
    rng = CountingRng(g)
    out: List[tuple] = []
    for _ in range(draws):
        excluded = set(base)
        for b0 in own:
            n0 = rng.n
            try:
                p, fell = NL._pick_bigram(rng, bins, b0, excluded, lo, hi)
            except NL.NullError as e:
                out.append(("error", str(e), copy.deepcopy(g.bit_generator.state), rng.n - n0))
                return out
            excluded.add(p)
            out.append((p, fell, copy.deepcopy(g.bit_generator.state), rng.n - n0))
    return out


def new_trace(pool_cls, bins: Dict[int, List[Frame]], own: Sequence[int], base: Set[Frame], key: Sequence[int], draws: int) -> List[tuple]:
    """The NEW pool driven as `null2` drives it: `reset(base)` each draw, `exclude(pick)` after each pick."""
    g = np.random.default_rng(list(key))
    pool = pool_cls(bins)
    out: List[tuple] = []
    for _ in range(draws):
        pool.reset(base)
        for b0 in own:
            try:
                p, fell = pool.pick(g, b0)
            except NL.NullError as e:
                out.append(("error", str(e), copy.deepcopy(g.bit_generator.state), None))
                return out
            pool.exclude(p)
            out.append((p, fell, copy.deepcopy(g.bit_generator.state), None))
    return out


def first_difference(ref: List[tuple], got: List[tuple]):
    """The index of the first pick where the new trace differs from the reference, and what differs there: 'pick' | 'flag' | 'state' | 'length' | None."""
    for i, (a, b) in enumerate(zip(ref, got)):
        if a[0] != b[0]:
            return i, "pick"
        if a[1] != b[1]:
            return i, "flag"
        if a[2] != b[2]:
            return i, "state"
    if len(ref) != len(got):
        return min(len(ref), len(got)), "length"
    return None


def diffs(ref: List[tuple], got: List[tuple]) -> List[str]:
    fd = first_difference(ref, got)
    return [] if fd is None else [f"first difference at pick {fd[0]}: {fd[1]}"]


# ====================================================================================================================== the scenarios
def mk_bins(sizes: Dict[int, int]) -> Dict[int, List[Frame]]:
    """A bin of n distinct bigrams, sorted as `bigram_bins` sorts them."""
    return {b: sorted((f"a{b}_{i:05d}", f"b{b}_{i:05d}") for i in range(n)) for b, n in sizes.items()}


def scenario(name: str, sizes: Dict[int, int], own: Sequence[int], exclude, draws: int = 1, idx: int = 0):
    """(name, bins, own, base, key, draws). `exclude`: 'none' | 'all' | ('all_but', k) | ('frac', f, seed) | ('bins', [bins fully excluded]) | ('mixed', [bins fully excluded], f, seed: the others at fraction f)."""
    bins = mk_bins(sizes)
    allp = [p for b in sorted(bins) for p in bins[b]]
    if isinstance(exclude, str):
        base: Set[Frame] = set() if exclude == "none" else set(allp) if exclude == "all" else None
        if base is None:
            raise ValueError(exclude)
    elif exclude[0] == "all_but":
        base = set(allp[: max(0, len(allp) - exclude[1])])
    elif exclude[0] == "frac":
        r = np.random.default_rng(exclude[2])
        base = {p for p in allp if r.random() < exclude[1]}
    elif exclude[0] == "bins":
        base = {p for b in exclude[1] for p in bins[b]}
    elif exclude[0] == "mixed":
        r = np.random.default_rng(exclude[3])
        base = {p for b in sorted(bins) for p in bins[b] if b in exclude[1] or r.random() < exclude[2]}
    else:
        raise ValueError(exclude)
    return (name, bins, list(own), base, [NL.SEED_ROOT, 99, idx, 2], draws)


def hand_scenarios() -> List[tuple]:
    sc = []
    sc.append(scenario("small pools enumerated, then widened, then NullError", {0: 10, 2: 5}, [0] * 20, "none", idx=1))
    sc.append(scenario("a big bin, every try accepted", {0: 500}, [0] * 40, "none", draws=2, idx=2))
    sc.append(scenario("the doomed loop: bin 0 fully excluded (100 > 64), then widened to bin 3", {0: 100, 3: 100}, [0] * 12, ("bins", [0]), draws=2, idx=3))
    sc.append(scenario("single bin, two admissible of 2,000: late accepts and the all-1,000-fail enumeration at ONE level", {0: 2000}, [0, 0], ("all_but", 2), draws=12, idx=4))
    sc.append(scenario("two admissible of 2,000 with a bin beside it: the doomed level after them", {0: 2000, 2: 12}, [0] * 6, ("all_but", 14), draws=10, idx=17))
    sc.append(scenario("a doomed level, then a level with 90 % excluded (a late accept past a doomed level)", {0: 100, 3: 100}, [0] * 8, ("mixed", [0], 0.9, 7), draws=3, idx=18))
    sc.append(scenario("a few admissible of 3,000 (a bin beside it)", {0: 3000, 5: 40}, [0] * 30, ("all_but", 47), draws=2, idx=5))
    sc.append(scenario("sizes exactly 64 and 65 (the SMALL_ENUM boundary)", {5: 64, 6: 65}, [5] * 70 + [6] * 70, "none", idx=6))
    sc.append(scenario("sizes exactly 64 and 65, half excluded", {5: 64, 6: 65}, [5] * 40 + [6] * 40, ("frac", 0.5, 11), draws=2, idx=7))
    sc.append(scenario("two bins at one distance (above 64 together)", {2: 40, 4: 40}, [3] * 100, "none", idx=8))
    sc.append(scenario("two bins at one distance, nearly all excluded", {2: 40, 4: 40}, [3] * 30, ("frac", 0.97, 5), idx=9))
    sc.append(scenario("only the upper of the two bins exists", {7: 90}, [6] * 50, ("frac", 0.9, 3), idx=10))
    sc.append(scenario("only the lower of the two bins exists", {2: 90}, [3] * 50, ("frac", 0.9, 4), idx=11))
    sc.append(scenario("a NullError at the end: three entries, five picks", {1: 3}, [1] * 5, "none", idx=12))
    sc.append(scenario("a NullError at the first pick: everything excluded", {1: 100, 4: 70}, [1] * 3, "all", idx=13))
    sc.append(scenario("a bin without entries beside a full one", {0: 0, 3: 80}, [0] * 20, "none", idx=14))
    sc.append(scenario("the real shape: a thin top, a fat bin 0", {0: 800, 2: 300, 3: 60, 4: 66, 5: 30, 9: 4, 16: 1}, [0] * 20 + [3] * 80 + [4] * 90 + [5] * 40 + [9] * 6 + [16] * 3, ("frac", 0.3, 17), draws=2, idx=15))
    sc.append(scenario("two doomed levels in one pick (bin 3, then bins 2 and 4 together, then bin 7)", {2: 70, 3: 80, 4: 70, 7: 100}, [3] * 5, ("bins", [2, 3, 4]), draws=2, idx=16))
    return sc


def random_scenarios(n: int = 24) -> List[tuple]:
    r = np.random.default_rng(20261103)
    choices = [0, 1, 3, 10, 40, 64, 65, 66, 200, 700]
    sc = []
    for i in range(n):
        keys = sorted(int(k) for k in r.choice(np.arange(0, 17), size=int(r.integers(2, 7)), replace=False))
        sizes = {k: int(r.choice(choices)) for k in keys}
        if sum(sizes.values()) == 0:
            sizes[keys[0]] = 5
        frac = float(r.choice([0.0, 0.3, 0.9, 0.99]))
        own = [int(r.choice(keys + [int(keys[0]) - 1, int(keys[-1]) + 1])) for _ in range(int(r.integers(10, 40)))]
        sc.append(scenario(f"random {i}", sizes, own, ("frac", frac, int(r.integers(1, 10 ** 6))), draws=int(r.integers(1, 3)), idx=100 + i))
    return sc


_SYN: Dict[str, object] = {}


def synthetic():
    """(scenarios, reference traces), computed once for the whole module (the reference's doomed loops are the slow part)."""
    if not _SYN:
        scn = hand_scenarios() + random_scenarios()
        _SYN["scn"] = scn
        _SYN["refs"] = [ref_trace(bins, own, base, key, draws) for (_, bins, own, base, key, draws) in scn]
    return _SYN["scn"], _SYN["refs"]


# ====================================================================================================================== the proof on synthetic bins
class TestIdentitySynthetic(unittest.TestCase):
    def test_every_scenario_reads_identical_in_pick_flag_and_generator_state_after_every_pick(self):
        scn, refs = synthetic()
        for (name, bins, own, base, key, draws), ref in zip(scn, refs):
            got = new_trace(NL._BigramPool, bins, own, base, key, draws)
            self.assertEqual(diffs(ref, got), [], name)
            self.assertEqual(len(got), len(ref), name)

    def test_the_scenarios_reach_every_branch_of_the_reference(self):
        """The instrument check: the proof is only as wide as the branches it reaches, counted from the REFERENCE's own scalar draws a pick made."""
        _, refs = synthetic()
        calls = [e[3] for ref in refs for e in ref]
        errors = [e for ref in refs for e in ref if e[0] == "error"]
        self.assertTrue(any(c == 1 for c in calls), "an immediate accept or a one-draw enumeration")
        self.assertTrue(any(1 < c < NL.MAX_REJECT for c in calls), "a rejection loop that accepted after several tries")
        self.assertTrue(any(c >= NL.MAX_REJECT for c in calls), "a doomed or failed loop (>= MAX_REJECT tries)")
        scn, _ = synthetic()
        one = [e[3] for (n, *_), ref in zip(scn, refs) if n.startswith("single bin") for e in ref]        # one level only: no doomed level can precede the pick
        self.assertTrue(any(c == NL.MAX_REJECT + 1 for c in one), "all MAX_REJECT tries failed at ONE level and the pick was drawn from the enumeration")
        self.assertTrue(any(1 < c < NL.MAX_REJECT for c in one), "a late accept at one level (after several tries, before MAX_REJECT)")
        self.assertTrue(any(NL.MAX_REJECT + 1 < c < 2 * NL.MAX_REJECT for c in calls), "a late accept past a doomed level (more than one try at the next level)")
        self.assertTrue(any(c >= 2 * NL.MAX_REJECT for c in calls), "two doomed levels in one pick")
        self.assertGreaterEqual(len(errors), 2, "NullError reached (the state after it is compared too)")
        flags = [e[1] for ref in refs for e in ref if e[0] != "error"]
        self.assertTrue(any(f is True for f in flags) and any(f is False for f in flags), "fallback and non-fallback picks")

    def test_an_error_leaves_the_same_text_and_the_same_state(self):
        scn, refs = synthetic()
        seen = 0
        for (name, bins, own, base, key, draws), ref in zip(scn, refs):
            if ref and ref[-1][0] == "error":
                seen += 1
                got = new_trace(NL._BigramPool, bins, own, base, key, draws)
                self.assertEqual(got[-1][0], "error", name)
                self.assertEqual(got[-1][1], ref[-1][1], name)
                self.assertEqual(got[-1][2], ref[-1][2], name)
        self.assertGreaterEqual(seen, 2)

    def test_a_reset_forgets_every_exclusion_and_the_counters_agree_with_the_masks(self):
        bins = mk_bins({0: 500, 3: 30})
        pool = NL._BigramPool(bins)
        self.assertEqual(sum(pool.n_excl.values()), 0)                         # a pool nobody has reset yet excludes nothing
        self.assertFalse(any(m.any() for m in pool.mask.values()))
        g = np.random.default_rng(1)
        pool.reset(set())
        picks = []
        for _ in range(30):
            p, _ = pool.pick(g, 0)
            pool.exclude(p)
            picks.append(p)
        self.assertEqual(len(set(picks)), 30)                                  # distinct within a draw
        self.assertEqual(sum(pool.n_excl.values()), 30)
        self.assertEqual(sum(int(m.sum()) for m in pool.mask.values()), 30)
        pool.exclude(picks[0])                                                 # excluding twice counts once
        self.assertEqual(sum(pool.n_excl.values()), 30)
        pool.reset({picks[1], ("not", "in the pool")})                         # a frame that is not in the pool is ignored; one in it is excluded
        self.assertEqual(sum(pool.n_excl.values()), 1)
        self.assertEqual(sum(int(m.sum()) for m in pool.mask.values()), 1)


# ====================================================================================================================== the proof on the REAL bins and sets
def _real_required() -> None:
    if not REAL_OK:
        if REQUIRED:
            raise AssertionError("TOYS_REAL_REQUIRED=1 and the real copies are absent: the proof on the real count bins cannot be skipped")
        raise unittest.SkipTest("the copies are not made yet (python3 -m tools.toys.frames.streams copy)")


_REAL: Dict[str, object] = {}


def real():
    """The real ALPHA4 plain split's Scorer and count bins, the real frame sets of SENTENCE, WEB-H, WEB-S seed 1 and the plant, and the reference traces (cached for the module)."""
    _real_required()
    if not _REAL:
        a4 = RN.load_streams(COPIES)["alpha4"]
        train, held = PL.condition_parts(a4, "plain")
        sc = CO.Scorer([m.words for m in train], [m.words for m in held])
        bins = NL.bigram_bins(sc)
        flat = ST.flat_words(train)
        sets = {}
        for label, r in (("SENTENCE", RL.sentence_rule(sc.train)), ("WEB-H", RL.web_rule(flat, sc, "H", 0)), ("WEB-S s1", RL.web_rule(flat, sc, "S", 1))):
            sets[label] = (r.rule, r.seed, sorted(set(r.frames)))
        sets["PLANT"] = ("PLANT", 0, [ST.PLANT])
        cases = []
        for label, (rule, seed, frames) in sets.items():
            tag = RL.RULE_TAG.get(rule, 5)
            key = [NL.SEED_ROOT, int(tag), int(seed if rule == "WEB-S" else 0), 2]
            own = [NL.log2_bin(max(1, sc.train_adjacent(f))) for f in frames]
            cases.append((label, own, set(frames), key, 3 if label == "PLANT" else 2))
        refs = [ref_trace(bins, own, base, key, draws) for (_, own, base, key, draws) in cases]
        _REAL.update(sc=sc, bins=bins, sets=sets, cases=cases, refs=refs)
    return _REAL


class TestIdentityRealBins(unittest.TestCase):
    def test_the_real_count_bins_are_the_ones_the_diagnosis_read(self):
        sizes = {b: len(v) for b, v in sorted(real()["bins"].items())}
        self.assertEqual(sizes[0], 5453)
        self.assertEqual(sizes[2], 1861)
        self.assertEqual((sizes[3], sizes[4], sizes[5]), (349, 389, 120))

    def test_identical_pick_flag_and_generator_state_after_every_pick_on_real_bins_and_real_frame_sets(self):
        R = real()
        for (label, own, base, key, draws), ref in zip(R["cases"], R["refs"]):
            got = new_trace(NL._BigramPool, R["bins"], own, base, key, draws)
            self.assertEqual(diffs(ref, got), [], label)
            self.assertEqual(len(got), len(own) * draws, label)

    def test_the_real_traces_reach_the_branch_that_cost_the_time(self):
        """The proof is on the branch that mattered: WEB-H's picks that ran the reference's loop to its end, the fallbacks, and the picks accepted after several tries."""
        R = real()
        ref = dict((c[0], r) for c, r in zip(R["cases"], R["refs"]))["WEB-H"]
        calls = [e[3] for e in ref]
        self.assertGreater(sum(1 for c in calls if c >= NL.MAX_REJECT), 300)
        self.assertGreater(sum(1 for e in ref if e[1] is True), 300)
        self.assertGreater(sum(1 for c in calls if 1 < c < NL.MAX_REJECT), 20)

    def test_null2_itself_equals_a_reference_null2_that_calls_the_old_pick_on_real_sets(self):
        R = real()
        for label in ("SENTENCE", "WEB-S s1"):
            rule, seed, frames = R["sets"][label]
            tag = RL.RULE_TAG[rule]
            s = seed if rule == "WEB-S" else 0
            want = _null2_reference(R["sc"], frames, tag, s, 2)
            got = NL.null2(R["sc"], frames, tag, s, 2, keep_pairs=True)
            self.assertEqual(got.pairs, want.pairs, label)
            self.assertEqual(got.values, want.values, label)
            self.assertEqual(got.fallbacks, want.fallbacks, label)
            self.assertEqual((got.k, got.draws, got.kind), (want.k, want.draws, want.kind), label)


def _null2_reference(scorer, F, rule_tag: int, seed: int, draws: int) -> NL.NullResult:
    """`null2` as it stood at 724865d: the OLD pick, a fresh `excluded` set each draw."""
    frames = sorted(set(F))
    bb = NL.bigram_bins(scorer)
    lo, hi = min(bb), max(bb)
    own = [NL.log2_bin(max(1, scorer.train_adjacent(f))) for f in frames]
    rng = np.random.default_rng([NL.SEED_ROOT, int(rule_tag), int(seed), 2])
    base = set(frames)
    values: List[float] = []
    pairs: List[Tuple[Frame, ...]] = []
    fallbacks = 0
    for _ in range(draws):
        excluded = set(base)
        dealt: List[Frame] = []
        for b0 in own:
            p, fell = NL._pick_bigram(rng, bb, b0, excluded, lo, hi)
            excluded.add(p)
            dealt.append(p)
            fallbacks += int(fell)
        values.append(scorer.gain(set(dealt)).G)
        pairs.append(tuple(dealt))
    return NL.NullResult("NULL-2", draws, len(frames), tuple(values), fallbacks, tuple(pairs))


class TestNull2KeepsItsContractOnSmallStreams(unittest.TestCase):
    def test_null2_equals_the_reference_null2_on_a_small_hand_stream_with_fallbacks(self):
        from tests.tools.test_toys_frames_null import bigram_stream, held_for

        train = bigram_stream()
        sc = CO.Scorer(train, held_for(train))
        F = {("x1", "y1"), ("x4", "y4"), ("x5", "y5"), ("z1", "z2")}          # x4 and x5 are BOTH of bin 2 and the pool holds only them: each draw needs two fallbacks, from two different bins
        for tag, seed in ((3, 0), (4, 0), (3, 1)):
            want = _null2_reference(sc, F, tag, seed, 30)
            got = NL.null2(sc, F, tag, seed, 30, keep_pairs=True)
            self.assertEqual((got.pairs, got.values, got.fallbacks), (want.pairs, want.values, want.fallbacks))
            self.assertEqual(want.fallbacks, 60)                                # two a draw: the instrument reaches the fallback branch


# ====================================================================================================================== the reference is the OLD pick, unchanged
REF_SOURCE_SHA256 = "285f20e4c64f5189c6203d86622b7af7171a3686e897b500387aee394f550081"   # sha256 of inspect.getsource(null._pick_bigram) at commit 724865d (959 bytes)


class TestTheReferenceIsTheOldPickUnchanged(unittest.TestCase):
    """The proof compares the new pick with the reference IN THE SAME TREE: a change to the reference or to a constant both read would leave them equal and the proof silent. So the reference is pinned to the
    bytes it had at 724865d, the commit the real gates ran on, and so are the constants and the seed root."""

    def test_the_reference_source_is_the_one_of_724865d(self):
        self.assertEqual(hashlib.sha256(inspect.getsource(NL._pick_bigram).encode()).hexdigest(), REF_SOURCE_SHA256)

    def test_the_constants_both_picks_read_are_the_ones_of_724865d(self):
        self.assertEqual((NL.MAX_REJECT, NL.SMALL_ENUM, NL.SEED_ROOT), (1000, 64, 20261103))


# ====================================================================================================================== the PLANTS: a one-line change of the new class must be caught
def _plant_class(old: str, new: str):
    """The new class's source with ONE fragment changed, loaded in memory (the worktree is never written). Asserts the change is real and unique."""
    src = inspect.getsource(NL._BigramPool)
    assert src.count(old) == 1, (src.count(old), old)
    mut = src.replace(old, new)
    assert mut != src, "the plant changed nothing"
    ns = dict(NL.__dict__)
    exec(compile(mut, "<plant>", "exec"), ns)
    return ns["_BigramPool"]


PLANTS = [
    # name, fragment, replacement, a one-line description
    ("redraw one draw too few", "rng.integers(total, size=j + 1)", "rng.integers(total, size=j)", "the pick is right and the generator is one draw behind: ONLY the state comparison sees it at first"),
    ("doomed advance one draw too few", "rng.integers(total, size=MAX_REJECT)\n                    continue", "rng.integers(total, size=MAX_REJECT - 1)\n                    continue", "the doomed level consumes 999 draws: the stream shifts by one"),
    ("the fallback flag", "return self._item(ks, sizes, int(r[j])), d > 0", "return self._item(ks, sizes, int(r[j])), d >= 0", "the flag of a rejection-loop accept"),
    ("the enumeration boundary", "if total > SMALL_ENUM:", "if total >= SMALL_ENUM:", "a pool of exactly 64 is rejection-sampled instead of enumerated"),
    ("the accept test inverted", "ok = ~m[r]", "ok = m[r]", "the loop accepts excluded entries"),
    ("no state restore", "rng.bit_generator.state = saved\n", "pass\n", "the generator keeps the whole batch of 1,000 draws"),
]


class TestPlantsAreCaught(unittest.TestCase):
    def _synthetic_diffs(self, pool_cls) -> List[str]:
        scn, refs = synthetic()
        out: List[str] = []
        for (name, bins, own, base, key, draws), ref in zip(scn, refs):
            try:
                got = new_trace(pool_cls, bins, own, base, key, draws)
            except Exception as e:                                       # a plant that crashes is caught too
                out.append(f"{name}: {type(e).__name__}")
                continue
            out += [f"{name}: {d}" for d in diffs(ref, got)]
        return out

    def test_the_control_the_unmutated_source_loaded_the_same_way_reads_identical(self):
        src = inspect.getsource(NL._BigramPool)
        ns = dict(NL.__dict__)
        exec(compile(src, "<control>", "exec"), ns)
        self.assertEqual(self._synthetic_diffs(ns["_BigramPool"]), [])

    def test_each_plant_is_caught_on_the_synthetic_scenarios(self):
        for name, old, new, why in PLANTS:
            found = self._synthetic_diffs(_plant_class(old, new))
            self.assertTrue(found, f"the plant «{name}» was NOT caught ({why})")

    def test_the_first_plant_changes_no_pick_where_it_first_differs_and_only_the_state_comparison_sees_it(self):
        scn, refs = synthetic()
        cls = _plant_class(*PLANTS[0][1:3])
        state_only = 0
        for (name, bins, own, base, key, draws), ref in zip(scn, refs):
            fd = first_difference(ref, new_trace(cls, bins, own, base, key, draws))
            if fd is not None and fd[1] == "state":
                state_only += 1
        self.assertGreater(state_only, 0, "no scenario's FIRST difference was a state-only one: the state comparison is not what catches this plant")


@unittest.skipUnless(REAL_OK or REQUIRED, "the copies are not made yet")
class TestPlantsAreCaughtOnTheRealBins(unittest.TestCase):
    def test_four_plants_are_caught_on_the_real_traces(self):
        R = real()
        for name, old, new, why in (PLANTS[0], PLANTS[1], PLANTS[2], PLANTS[5]):
            cls = _plant_class(old, new)
            caught = any(diffs(ref, new_trace(cls, R["bins"], own, base, key, draws)) for (label, own, base, key, draws), ref in zip(R["cases"], R["refs"]))
            self.assertTrue(caught, f"the plant «{name}» was not caught on the real bins ({why})")

    def test_the_first_plant_is_state_only_at_its_first_difference_on_the_real_bins_too(self):
        R = real()
        cls = _plant_class(*PLANTS[0][1:3])
        kinds = []
        for (label, own, base, key, draws), ref in zip(R["cases"], R["refs"]):
            fd = first_difference(ref, new_trace(cls, R["bins"], own, base, key, draws))
            kinds.append(fd[1] if fd else None)
        self.assertIn("state", kinds)


if __name__ == "__main__":
    unittest.main()
