# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 16:33 +0400 — PREREG-EAR-COVER-CAP (signed; file sha256
# a00d649c2a95e4449893a11536b795ce92c78eb7beddcd5f41bf7321f7116eee, SEAT-LINE in docs/organism/records/ear-cover-cap/),
# TESTS FIRST (red on the pre-build learners.py: no COVER_FULL_BELOW / _largest_clique_bounded / COVER_JOURNAL yet):
#   G-BYTE  below the bound, cover() byte-identical to the pre-law module loaded from git history (569de62~1) on every
#           existing test-fixture vocabulary (the s1b1/s1b1r ear fixtures, re-declared below as replayable streams), on
#           the OW-1/2 bench tapes' mature ears, and on the declared synthetic 25-word scene ear;
#   G-KNEE  the V3 tape's real exclusion graph at the knee (canvas 967 — scratch/ow4/coverprobe.py's own rebuild form):
#           the bounded form completes ≤ 60 s CPU and ≤ 500 MB, the cover is VALID (a partition; every type a clique of
#           the exclusion graph — verified against it), two runs byte-identical;
#   G-PLANT a synthetic exclusion graph with a planted UNIQUE maximum clique: the bounded form finds exactly it; a
#           doctored form (one start skipped — the plant's own seed start "p0") misses it and is CAUGHT; M-AGREE over
#           every graph the enumeration can reach (the fixtures + the declared synthetic ladder): bounded vs
#           enumeration agreement MEASURED and PRINTED, disagreements named — a reading, never a gate.
from __future__ import annotations

import importlib.util
import json
import random
import resource
import subprocess
import sys
import tempfile
import time
import unittest
from bisect import bisect_right
from pathlib import Path

from brain.scene import learners as Lr
from brain.scene import world as W

ROOT = Path(__file__).resolve().parents[3]
ORACLE_REF = "569de62~1:brain/scene/learners.py"      # the pre-law module (the law's G-BYTE oracle; 569de62 = the law's
                                                      # own commit, docs only — learners.py there is the pre-law byte)
RECORDS = ROOT / "docs/organism/whole/records"
TAPE_OW1A = RECORDS / "open-world-1/bench/tape-a"
TAPE_OW1B = RECORDS / "open-world-1/bench/tape-b"
TAPE_OW2_2 = RECORDS / "open-world-2/bench/tape-2"
TAPE_OW2_502 = RECORDS / "open-world-2/bench/tape-502"
TAPE_OW4 = RECORDS / "open-world-4/bench/tape-curriculum"
KNEE = 967                                            # the canvas of the 250th worded canvas (VERDICT-OPEN-WORLD-4)
P_FROM = 3                                            # the learner's own maturity rule (P_FROM_MEETING)

_ORACLE = None


def _oracle():
    """The pre-law learners.py loaded from git history (the law's oracle). Loaded once, beside the build's module."""
    global _ORACLE
    if _ORACLE is None:
        src = subprocess.run(["git", "show", ORACLE_REF], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        tmp = Path(tempfile.mkdtemp()) / "learners_pre_law.py"
        tmp.write_text(src)
        spec = importlib.util.spec_from_file_location("brain.scene.learners_pre_law", tmp)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        _ORACLE = mod
    return _ORACLE


def _p(*a):
    print(*a, flush=True)


# -------------------------------------------------------------------------------- the declared graph/ear builders
def _replay(ear, utts):
    for u in utts:
        ear.hear(u)
    return ear


def _edges(ear, words):
    """The exclusion-edge count among `words` from the ear's own counters (pairs never heard in one utterance)."""
    ws = sorted(set(words))
    return sum(1 for i in range(len(ws)) for j in range(i + 1, len(ws)) if ear.count(ws[i], ws[j]) == 0)


def _utts_world_ear(heldout):
    """test_learners_s1b1r._world_ear's utterance stream, re-declared as a replayable stream (the fixture builds its ear
    internally; the gate replays the SAME utterances into the oracle's Ear and the build's Ear)."""
    for s in W.SHAPES:
        yield (s,)
        for z in W.SIZE_NAMES:
            yield (z, s)
        for c in W.COLOUR_NAMES:
            if (s, c) in heldout:
                continue
            yield (c, s)
            for z in W.SIZE_NAMES:
                yield (z, c, s)


# the hand-built 7-word fixture of test_learners_s1b1r.test_a_lone_word_is_its_own_type_and_ties_go_lexicographic
HAND7_UTTS = (("a", "x"), ("a", "y"), ("b", "x"), ("b", "y"), ("c", "x"), ("c", "y"), ("a", "z"), ("b", "z"), ("c", "z"),
              ("x", "q"), ("y", "q"), ("z", "q"), ("a", "q"), ("b", "q"), ("c", "q"))
HAND7_WORDS = ["q", "z", "y", "x", "c", "b", "a"]
# test_learners_s1b1.TestEar.test_order_key_first_heard_and_exclusion's two small ears
TESTEAR_SMALL_UTTS = (("big", "red", "circle"), ("red", "circle"), ("circle",), ("small", "star"))
TESTEAR_E2_UTTS = (("small", "star"), ("tiny",))
# test_learners_s1b1.TestProduction.UTTS and test_learners_s1b1r.TestBelievedMouth.UTTS (the road stubs' own ears)
PROD_UTTS = (("big", "red", "circle"), ("red", "circle"), ("big", "circle"), ("small", "blue", "star"))
BELIEVED_UTTS = (("big", "red", "circle"), ("red", "circle"), ("big", "circle"), ("circle",), ("star",),
                 ("small", "blue", "star"))

# the declared SYNTHETIC 25-WORD SCENE EAR (the law's G-BYTE "a scene life's 25-word ear"): 25 words in 5 type groups
# of 5 — within a group the words are never co-heard (an exclusion clique, the scene world's own type form); every
# cross-group pair co-heard EXCEPT a declared held-out set of 6 (W.HELDOUT's own count); one declared cycle.
SCENE25_WORDS = [f"w{g}{i}" for g in range(5) for i in range(5)]
SCENE25_HELDOUT = {("w00", "w10"), ("w01", "w20"), ("w10", "w30"), ("w20", "w40"), ("w02", "w11"), ("w30", "w41")}


def _scene25_utts():
    for g in range(5):
        for i in range(5):
            yield (f"w{g}{i}",)
    for g in range(5):
        for h in range(g + 1, 5):
            for i in range(5):
                for j in range(5):
                    a, b = f"w{g}{i}", f"w{h}{j}"
                    if (a, b) not in SCENE25_HELDOUT:
                        yield (a, b)


def _order_pin_utts():
    """test_learners_s1b1.TestOrderKeyPin's own stream: seed 20261101's first 300 scene-world utterances."""
    return [W.train_scene(20261101, i).words for i in range(300)]


def _tape_ear(tape_dir, upto_canvas=None):
    """scratch/ow4/coverprobe.py's own rebuild form (the law's named probe form for the knee; V0's mapping — the ear
    row's canvas is the first eye row after it, the tape's order law). Returns (ear, meetings, mature)."""
    rows = []
    for f in sorted(Path(tape_dir).glob("*.jsonl")):
        rows.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
    rows.sort(key=lambda r: int(r["seq"]))
    eyepos = [i for i, r in enumerate(rows) if r["sense"] == "eye"]
    per_canvas = {}
    for i, r in enumerate(rows):
        if r["sense"] != "ear":
            continue
        j = bisect_right(eyepos, i)
        per_canvas.setdefault(j, []).append(r["meta"]["word"])
    ear = Lr.Ear()
    meetings = {}
    for c in sorted(per_canvas):
        if upto_canvas is not None and c > upto_canvas:
            break
        ws = per_canvas[c]
        ear.hear(ws)
        for w in set(ws):
            meetings[w] = meetings.get(w, 0) + 1
    mature = sorted(w for w, m in meetings.items() if m >= P_FROM)
    return ear, meetings, mature


def _synth_ear(n, p, seed):
    """The declared synthetic family: the exclusion graph G(n, p) — each pair exclusion-adjacent with probability p,
    drawn in (i < j) sorted order from random.Random(seed); realized as an Ear by hearing every NON-adjacent pair once
    (so ear.count(a, b) == 0 EXACTLY on the drawn edges). Returns (ear, words, adj)."""
    words = [f"g{i:03d}" for i in range(n)]
    rng = random.Random(seed)
    adj = {w: set() for w in words}
    ear = Lr.Ear()
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[words[i]].add(words[j])
                adj[words[j]].add(words[i])
            else:
                ear.hear((words[i], words[j]))
    return ear, words, adj


def synth_seed(n, p):
    return 20261008 + n + int(p * 100)                 # the declared seed form for every synthetic graph of this law


# the declared M-AGREE ladder (the fixtures beside it): the enumeration can reach every one of these in-test (the
# build's own pre-readings: G(48, 0.92) = 55,846 maximal cliques at 0.43 s CPU — far inside the 60 s / 1 GB band).
AGREE_LADDER = [(n, p) for p in (0.92, 0.5) for n in (8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48)]

# the G-PLANT graph (declared): 17 words. The planted UNIQUE maximum clique PLANT (5 words, pairwise exclusion);
# blocker a_i exclusion-adjacent to p_i ONLY (i = 1..4 — so the greedy finds the plant from start "p0" ALONE, the
# doctor's target); G1, G2 two exclusion-K4s (every other clique < 5); every other pair co-heard (count ≥ 1).
PLANT = ("p0", "p1", "p2", "p3", "p4")
PLANT_BLOCKERS = ("a1", "a2", "a3", "a4")
PLANT_G1 = ("g1_0", "g1_1", "g1_2", "g1_3")
PLANT_G2 = ("g2_0", "g2_1", "g2_2", "g2_3")
PLANT_WORDS = sorted(PLANT + PLANT_BLOCKERS + PLANT_G1 + PLANT_G2)


def _plant_ear():
    excl = set()
    for grp in (PLANT, PLANT_G1, PLANT_G2):
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                excl.add((min(grp[i], grp[j]), max(grp[i], grp[j])))
    for i in range(1, 5):
        excl.add((f"a{i}", f"p{i}"))
    ear = Lr.Ear()
    adj = {w: set() for w in PLANT_WORDS}
    for x in range(len(PLANT_WORDS)):
        for y in range(x + 1, len(PLANT_WORDS)):
            a, b = PLANT_WORDS[x], PLANT_WORDS[y]
            if (a, b) in excl:
                adj[a].add(b)
                adj[b].add(a)
            else:
                ear.hear((a, b))
    return ear, PLANT_WORDS, adj


def _cover_with(ear, words, search):
    """A bench replica of Ear.cover's loop (brain/scene/learners.py:203-210, verbatim form) with the clique search
    passed in — the law's M-AGREE reads the bounded form's TYPES against the enumeration's on the same graphs."""
    rest = sorted(set(words))
    types = []
    while rest:
        adj = {w: {u for u in rest if u != w and ear.count(w, u) == 0} for w in rest}
        best = search(rest, adj)
        types.append(best)
        rest = [w for w in rest if w not in best]
    return types


def _search_enum(rest, adj):
    return min(_oracle()._maximal_cliques(rest, adj), key=lambda c: (-len(c), c))


def _search_bounded(rest, adj):
    return Lr._largest_clique_bounded(rest, adj)


def _valid_cover(ear, words, types):
    """The downstream contract (the law's §0 iii): a partition of the words; every type a clique of the exclusion
    graph — verified against the ear's own counters."""
    if sorted(w for t in types for w in t) != sorted(set(words)):
        return False
    for t in types:
        for i in range(len(t)):
            for j in range(i + 1, len(t)):
                if ear.count(t[i], t[j]) != 0:
                    return False
    return True


def _largest_clique_bounded_skip_start(nodes, adj, skip):
    """The G-PLANT DOCTOR: the law's DECLARED bounded form (§2.3) with ONE start word skipped. Nothing else changes."""
    best = ()
    for s in sorted(nodes):
        if s == skip:
            continue
        members = [s]
        for u in sorted(adj[s]):
            if all(u in adj[m] for m in members):
                members.append(u)
        c = tuple(sorted(members))
        if len(c) > len(best) or (len(c) == len(best) and c < best):
            best = c
    return best


# -------------------------------------------------------------------------------- G-BYTE
class TestGBYTE(unittest.TestCase):
    """Below the bound: cover() byte-identical to the pre-law oracle on every existing fixture vocabulary, the OW-1/2
    bench tapes' mature ears, and the declared synthetic 25-word scene ear."""

    @classmethod
    def setUpClass(cls):
        cls.oracle = _oracle()
        sq = tuple((s, c) for s, c in W.ALLOWED if s == "square") + W.HELDOUT
        cls.fixtures = [
            ("s1b1r-world-ear", list(_utts_world_ear(W.HELDOUT)), list(W.SHAPES) + list(W.COLOUR_NAMES) + list(W.SIZE_NAMES)),
            ("s1b1r-world-ear-square-heldout", list(_utts_world_ear(sq)), list(W.SHAPES) + list(W.COLOUR_NAMES) + list(W.SIZE_NAMES)),
            ("s1b1r-hand-7", list(HAND7_UTTS), list(HAND7_WORDS)),
            ("s1b1-testear-small", list(TESTEAR_SMALL_UTTS), None),
            ("s1b1-testear-e2", list(TESTEAR_E2_UTTS), None),
            ("s1b1-order-pin-300", _order_pin_utts(), None),
            ("s1b1-production-utts", list(PROD_UTTS), None),
            ("s1b1r-believed-utts", list(BELIEVED_UTTS), None),
            ("synthetic-scene-25", list(_scene25_utts()), list(SCENE25_WORDS)),
        ]

    def test_below_bound_byte_identical_fixtures(self):
        w0, e0 = Lr.COVER_FULL_BELOW
        for name, utts, words in self.fixtures:
            words = words if words is not None else sorted({w for u in utts for w in u})
            e_new = _replay(Lr.Ear(), utts)
            e_old = _replay(self.oracle.Ear(), utts)
            n, m = len(set(words)), _edges(e_new, words)
            self.assertLessEqual(n, w0, f"{name}: {n} words ABOVE the bound's W0={w0}")
            self.assertLessEqual(m, e0, f"{name}: {m} edges ABOVE the bound's E0={e0}")
            Lr.COVER_JOURNAL.clear()
            t_new = e_new.cover(words)
            t_old = e_old.cover(words)
            self.assertEqual(t_new, t_old, f"{name}: the build's types differ from the pre-law oracle's below the bound")
            self.assertEqual(Lr.COVER_JOURNAL[-1], {"words": n, "edges": m, "path": "full"})
            _p(f"G-BYTE fixture {name}: W={n} E={m} types={[len(t) for t in t_new]} — byte-identical to the oracle, "
               f"path=full (bound W0={w0} E0={e0})")

    def test_below_bound_byte_identical_ow_tapes(self):
        w0, e0 = Lr.COVER_FULL_BELOW
        for name, tape in (("ow1-tape-a", TAPE_OW1A), ("ow1-tape-b", TAPE_OW1B),
                           ("ow2-tape-2", TAPE_OW2_2), ("ow2-tape-502", TAPE_OW2_502)):
            if not tape.exists():
                self.skipTest(f"{name}: the bench tape is not on disk")
            ear, meetings, mature = _tape_ear(tape)
            rows = []
            for f in sorted(tape.glob("*.jsonl")):
                rows.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
            rows.sort(key=lambda r: int(r["seq"]))
            eyepos = [i for i, r in enumerate(rows) if r["sense"] == "eye"]
            per_canvas = {}
            for i, r in enumerate(rows):
                if r["sense"] == "ear":
                    per_canvas.setdefault(bisect_right(eyepos, i), []).append(r["meta"]["word"])
            e_old = self.oracle.Ear()
            meetings = {}
            for c in sorted(per_canvas):
                e_old.hear(per_canvas[c])
                for w in set(per_canvas[c]):
                    meetings[w] = meetings.get(w, 0) + 1
            mature = sorted(w for w, m in meetings.items() if m >= P_FROM)
            n, m = len(mature), _edges(ear, mature)
            self.assertLessEqual(n, w0, f"{name}: {n} mature words ABOVE the bound's W0={w0}")
            self.assertLessEqual(m, e0, f"{name}: {m} edges ABOVE the bound's E0={e0}")
            Lr.COVER_JOURNAL.clear()
            t_new = ear.cover(mature)
            t_old = e_old.cover(mature)
            self.assertEqual(t_new, t_old, f"{name}: the build's types differ from the pre-law oracle's below the bound")
            self.assertEqual(Lr.COVER_JOURNAL[-1], {"words": n, "edges": m, "path": "full"})
            _p(f"G-BYTE tape {name}: mature W={n} E={m} types={[len(t) for t in t_new]} — byte-identical, path=full")


# -------------------------------------------------------------------------------- G-KNEE
@unittest.skipUnless(TAPE_OW4.exists(), "the V3 bench tape is not on disk")
class TestGKNEE(unittest.TestCase):
    """The knee's REAL exclusion graph (the V3 tape to canvas 967, coverprobe's own form): the bounded form completes
    ≤ 60 s CPU and ≤ 500 MB; the cover is VALID; two runs byte-identical."""

    @classmethod
    def setUpClass(cls):
        cls.ear, cls.meetings, cls.mature = _tape_ear(TAPE_OW4, upto_canvas=KNEE)

    def test_knee_real_graph_bounded_form(self):
        ear, mature = self.ear, self.mature
        n, m = len(mature), _edges(ear, mature)
        w0, e0 = Lr.COVER_FULL_BELOW
        self.assertTrue(n > w0 or m > e0, "the knee must sit AT/ABOVE the bound (the bounded path is what is read)")
        Lr.COVER_JOURNAL.clear()
        rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        t0 = time.process_time()
        types1 = ear.cover(mature)
        cpu = time.process_time() - t0
        rss1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        types2 = ear.cover(mature)
        self.assertLessEqual(cpu, 60.0, f"the bounded form took {cpu:.2f}s CPU > 60s on the knee")
        self.assertLessEqual((rss1 - rss0) / 1024.0, 500.0, f"the bounded form grew RSS {(rss1-rss0)/1024:.0f} MB > 500 MB")
        self.assertEqual(types1, types2, "two bounded runs on the knee differ")
        self.assertTrue(_valid_cover(ear, mature, types1), "the knee's cover is not a partition into exclusion cliques")
        self.assertEqual(Lr.COVER_JOURNAL[0], {"words": n, "edges": m, "path": "bounded"})
        self.assertEqual(Lr.COVER_JOURNAL[1], {"words": n, "edges": m, "path": "bounded"})
        _p(f"G-KNEE: the knee's real graph W={n} E={m} — the bounded form: {cpu:.2f}s CPU (≤ 60), "
           f"RSS Δ{(rss1-rss0)/1024:.1f} MB (≤ 500), {len(types1)} types sizes={[len(t) for t in types1]}, "
           f"valid partition of cliques, deterministic ×2, path=bounded ×2 (bound W0={w0} E0={e0})")


# -------------------------------------------------------------------------------- G-PLANT + M-AGREE
class TestGPLANT(unittest.TestCase):
    """The planted UNIQUE maximum clique: the bounded form finds exactly it; the doctored skip-a-start form misses it
    and is CAUGHT; M-AGREE measured and printed over the enumeration's whole reachable band."""

    def test_planted_unique_maximum_found_exactly(self):
        ear, words, adj = _plant_ear()
        plant = tuple(sorted(PLANT))
        enum = _oracle()._maximal_cliques(words, adj)
        biggest = [c for c in enum if len(c) == max(len(c) for c in enum)]
        self.assertEqual(biggest, [plant], "the plant is not the graph's UNIQUE maximum clique (the fixture is broken)")
        got = Lr._largest_clique_bounded(words, adj)
        self.assertEqual(got, plant, "the bounded form did not find the planted unique maximum EXACTLY")
        Lr.COVER_JOURNAL.clear()
        types = ear.cover(words)
        self.assertEqual(types[0], plant, "cover() below the bound did not take the plant first")
        _p(f"G-PLANT: the planted unique maximum {plant} — the enumeration's only size-5 clique; "
           f"the bounded form found it EXACTLY; cover() took it first (path={Lr.COVER_JOURNAL[-1]['path']})")

    def test_doctored_skip_a_start_is_caught(self):
        ear, words, adj = _plant_ear()
        plant = tuple(sorted(PLANT))
        real = Lr._largest_clique_bounded(words, adj)
        doctored = _largest_clique_bounded_skip_start(words, adj, skip="p0")   # the plant's own seed start
        self.assertEqual(real, plant)
        self.assertNotEqual(doctored, plant, "the doctored form did NOT miss the plant — the plant is not load-bearing")
        self.assertNotEqual(doctored, real, "the doctor's result equals the real form's — the skip is NOT caught")
        _p(f"G-PLANT doctor: start 'p0' skipped → the doctored form returned {doctored} ≠ {plant} — MISSES, CAUGHT")

    def test_m_agree_measured_and_printed(self):
        surfaces = []                                   # (name, ear, words)
        sq = tuple((s, c) for s, c in W.ALLOWED if s == "square") + W.HELDOUT
        for name, utts, words in (("s1b1r-world-ear", list(_utts_world_ear(W.HELDOUT)), None),
                                  ("s1b1r-world-ear-square-heldout", list(_utts_world_ear(sq)), None),
                                  ("s1b1r-hand-7", list(HAND7_UTTS), list(HAND7_WORDS)),
                                  ("s1b1-order-pin-300", _order_pin_utts(), None),
                                  ("synthetic-scene-25", list(_scene25_utts()), list(SCENE25_WORDS))):
            words = words if words is not None else sorted({w for u in utts for w in u})
            surfaces.append((name, _replay(Lr.Ear(), utts), words))
        for n, p in AGREE_LADDER:
            ear, words, adj = _synth_ear(n, p, synth_seed(n, p))
            surfaces.append((f"synth-g{n}-p{p}", ear, words))
        agree, disagree = 0, []
        for name, ear, words in surfaces:
            t_enum = _cover_with(ear, words, _search_enum)
            t_bounded = _cover_with(ear, words, _search_bounded)
            self.assertTrue(_valid_cover(ear, words, t_bounded), f"{name}: the bounded form's cover is INVALID")
            self.assertTrue(_valid_cover(ear, words, t_enum), f"{name}: the enumeration's cover is INVALID")
            if t_enum == t_bounded:
                agree += 1
                _p(f"M-AGREE {name}: W={len(set(words))} E={_edges(ear, words)} — AGREE ({len(t_enum)} types)")
            else:
                disagree.append(name)
                _p(f"M-AGREE {name}: W={len(set(words))} E={_edges(ear, words)} — DISAGREE\n"
                   f"  enumeration: {t_enum}\n  bounded:     {t_bounded}")
        total = agree + len(disagree)
        _p(f"M-AGREE: {agree}/{total} graphs agree ({100.0*agree/total:.1f}%); disagreements named: "
           f"{disagree if disagree else 'NONE'} — a READING of the declared semantics difference, never a gate")


if __name__ == "__main__":
    unittest.main()
