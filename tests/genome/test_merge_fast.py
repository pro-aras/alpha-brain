# edit: Claude (Opus 5.5, M6 builder), 2026-09-23 17:20 +0400 — A42-M6 (docs/briefs/A42-M6-REPORT.md §1-§2; docs/ALPHA4-2-PREREG.md §2 row M6;
# docs/ALPHA4-PREREG.md §11 item 4): the sleep merge's fast road. `genome/sleep.py:cycle` runs `Organism._merge(..., fast=True)`,
# which walks only the pairs a READ-ONLY gemm filter (`Organism._merge_candidates`) cannot rule out, through the OLD loop body — the
# same four gates read at visit time, gate (b) by the old expression on the same arrays. The old road is kept HERE, verbatim, as the
# module-level `_merge` below (bound as `_merge_reference`): its text is pinned by sha256 to genome/machinery.py at 51f71ba (lines
# 1810-1848). Every identity is read against it; every positive control must be SEEN by it (#91, #215, #228: a control blind to
# everything isolates nothing).
"""test_merge_fast.py — the fast merge road makes the SAME merges, in the SAME order, with the SAME survivors and the SAME state
(state_hash, row_hash, the merges log) as the old road — on a toy past the size where the pass matters (>= 4,000 alive sight cells)
built so that the old road's order-dependence is exercised (cascades whose second merge depends on the first), and with four
positive controls the comparison must see."""
from __future__ import annotations

import hashlib
import inspect
import textwrap
import time
import unittest
from typing import Dict, List, Tuple

import numpy as np

from genome.machinery import Area, Organism, parse_genome   # noqa: F401  (Area/List: the verbatim reference's annotations)
from genome.sleep import cycle

from ._toy import MINI_GENOME_TEXT

OLD_MERGE_SHA256 = "4f6503dd91a983ed70447994174a8bc16c31cd8db1b9483dee97d79ee639a1b1"   # genome/machinery.py@51f71ba lines 1810-1848
THETA = 0.99                                                                                  # the mini genome's MERGE cos>0.99


# ---------------------------------------------------------------------------------------------------------------------------------
# THE OLD ROAD, VERBATIM — genome/machinery.py at 51f71ba, `Organism._merge`, lines 1810-1848, dedented one level. DO NOT EDIT:
# TestReferenceIsVerbatim re-indents this function's source and checks its sha256 against the text at 51f71ba.
def _merge(self, area: Area, winners: List[int], axis: int) -> None:
    """MERGE cos>THETA_M same-answer: two alike winners with the same answer become one
    (the lower id is kept, rows averaged over the union of their edges)."""
    ws = sorted(set(w for w in winners if area.alive[w]))
    wit = getattr(self, "_witness", None)    # A4L-COST: the witness learns every row whose MASK a merge changes
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            a, b = ws[i], ws[j]
            if not (area.alive[a] and area.alive[b]):
                continue
            if float(area.cells[a] @ area.cells[b]) <= self.g.theta_m:
                continue
            aa, ab = self._answer_of(area, a), self._answer_of(area, b)
            if aa is None or ab is None or aa != ab:
                continue
            if axis == 0:
                ma, mb = self.mask[a].astype(np.float64), self.mask[b].astype(np.float64)
                den = np.maximum(ma + mb, 1.0)
                self.W[a] = (self.W[a] * ma + self.W[b] * mb) / den
                self.mask[a] = ((ma + mb) > 0).astype(np.uint8)
                self.strikes[a] = np.minimum(self.strikes[a], self.strikes[b])
                self.W[b] = 0.0; self.mask[b] = 0; self.strikes[b] = 0
                if wit is not None:
                    wit.mark_rows([a, b])
            else:
                ma, mb = self.mask[:, a].astype(np.float64), self.mask[:, b].astype(np.float64)
                den = np.maximum(ma + mb, 1.0)
                self.W[:, a] = (self.W[:, a] * ma + self.W[:, b] * mb) / den
                self.mask[:, a] = ((ma + mb) > 0).astype(np.uint8)
                self.strikes[:, a] = np.minimum(self.strikes[:, a], self.strikes[:, b])
                self.W[:, b] = 0.0; self.mask[:, b] = 0; self.strikes[:, b] = 0
                if wit is not None:
                    wit.mark_rows(np.flatnonzero(mb))     # every row of column b moved to column a
            area.alive[b] = 0
            area.misfires[b] = 0
            self.c[f"cells_merged_{area.name}"] += 1
            self.merges.append((self.t, area.name, int(a), int(b)))   # edit: Claude (Fable 5.1), 2026-09-23 04:13 +0400 — numpy ids cast: json.dumps in state_hash crashed the mind at its 2nd sleep (alpha4-pre-1, seq 2604) — the FIRST real cycle() this road ever ran
            if self.sound_meets:      # A4L-VOICE (Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:31 +0400): the merged cell's sound-meeting edges follow it (#235)
                self._merge_pair_edges(area, a, b)
# ---------------------------------------------------------------------------------------------------------------------------------
_merge_reference = _merge


def _cycle_reference(org: Organism) -> bool:
    """genome/sleep.py:cycle at 51f71ba with its two `org._merge(...)` calls routed to the verbatim reference — nothing else changed."""
    if "CYCLE" not in org.g.declared:
        return False
    cyc = org.g.declared["CYCLE"]
    if "grow_to" in cyc:
        ceiling = float(cyc["grow_to"]) * org.g.nmax
        if org.total_cells() < ceiling:
            return False
    else:
        share = float(cyc["share"])
        alive = org.total_cells()
        since_last = org.c["births_refused_redundant"] - org._cycle_baseline_redundant
        if alive == 0 or since_last / alive <= share:
            return False
    for area, axis in ((org.sight, 0), (org.words, 1)):
        _merge_reference(org, area, list(area.alive_ids()), axis=axis)
    org._prune(list(org.sight.alive_ids()), list(org.words.alive_ids()))
    org._cycle_baseline_redundant = org.c["births_refused_redundant"]
    return True


# ------------------------------------------------------------------------------------------------------------ the toy (direct state)
def _genome(hash_: bool = False):
    text = MINI_GENOME_TEXT.replace("NMAX 200\n", "GROW unbounded\n")
    text = text.replace("SCALE every 1000 moments", "SCALE every 1000 moments\nCYCLE consolidate when redundant > 0.0 of alive")
    if hash_:
        text += "HASH sparse; dense at snapshot\n"
    return parse_genome(text)


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def _toy(n_s: int, n_w: int, seed: int, *, hash_: bool = False, isolated_pairs: int = 0) -> Tuple[Organism, Dict[str, object]]:
    """An organism built by DIRECT STATE (BIRTH novelty would refuse the near-duplicates a merge pass exists for): n_s sight cells
    (5 % dead, interleaved — their rows zeroed as a merge leaves them — so a cell id is never its index in the alive list, #234),
    n_w word cells, 1-3 masked edges per alive sight cell, ~150 random near-duplicate clusters (sigma 0.004-0.02: some pairs
    above THETA, some below; 60 % sharing the centre's answer), and the PLANTED cases each identity must get right:
      A  a<b<c all alike, one answer, stable under the merge   -> the old road merges (a,b) AND (a,c), skips (b,c) (b dead)
      B  a<b<c all alike, one answer, a's answer MOVES AWAY    -> merges (a,b) only: after it a answers t2, c answers t1
      C  a<b<c alike; a,b answer t2, c answers t1; a MOVES TO t1 once it absorbs b -> merges (a,b) THEN (a,c)
      D  a tie in a's row (argmax -> the lowest word id)       -> merges with a partner on that lowest id
      E  an alike pair where one cell has no edge (None)       -> no merge
      F1 a pair whose similarity is EXACTLY theta (one-hot construction: exact in every summation order) -> no merge (<=)
      F2 a pair one ulp ABOVE theta, same answer                -> merges
      I  `isolated_pairs` alike same-answer pairs far from everything else (PC3's straddle search).
    Returns (org, plants) — plants names each case's ids. The cluster and isolated-pair counts scale with n_s (a 300-cell toy
    holds 15 clusters, the 4,320-cell toy 150).
    """
    rng = np.random.default_rng(seed)
    isolated_pairs = isolated_pairs or min(40, n_s // 25)
    n_clusters = min(150, n_s // 20)
    org = Organism(_genome(hash_))
    while n_s > org.sight.nmax:
        org.sight.grow()
    while n_w > org.words.nmax:
        org.words.grow()
    while n_s > org.W.shape[0]:
        org._grow_W(axis=0)
    while n_w > org.W.shape[1]:
        org._grow_W(axis=1)
    ds, dw = org.sight.dim, org.words.dim
    S = rng.standard_normal((n_s, ds)); S /= np.linalg.norm(S, axis=1)[:, None]
    Wd = rng.standard_normal((n_w, dw)); Wd /= np.linalg.norm(Wd, axis=1)[:, None]
    rows: Dict[int, Dict[int, float]] = {}
    for s in range(n_s):
        k = int(rng.integers(1, 4))
        ts = rng.choice(n_w, size=k, replace=False)
        rows[s] = {int(t): float(rng.uniform(0.05, 1.0)) for t in ts}
    free = list(rng.permutation(n_s))
    used = set()

    def take(k: int) -> List[int]:
        out = []
        while len(out) < k:
            x = int(free.pop())
            if x not in used:
                used.add(x); out.append(x)
        return sorted(out)

    plants: Dict[str, object] = {}
    t1, t2, t3, t4, t5 = [int(x) for x in rng.choice(n_w, size=5, replace=False)]
    lo_t, hi_t = min(t3, t5), max(t3, t5)
    # A — stable cascade
    a, b, c = take(3); base = _unit(rng.standard_normal(ds))
    S[a] = base; S[b] = _unit(base + 0.001 * rng.standard_normal(ds)); S[c] = _unit(base + 0.001 * rng.standard_normal(ds))
    rows[a], rows[b], rows[c] = {t1: 0.5}, {t1: 0.6}, {t1: 0.7}
    plants["A"] = (a, b, c)
    # B — the answer moves AWAY after the first merge
    a, b, c = take(3); base = _unit(rng.standard_normal(ds))
    S[a] = base; S[b] = _unit(base + 0.001 * rng.standard_normal(ds)); S[c] = _unit(base + 0.001 * rng.standard_normal(ds))
    rows[a], rows[b], rows[c] = {t1: 0.5, t2: 0.49}, {t1: 0.1, t3: 0.05}, {t1: 0.3}
    plants["B"] = (a, b, c)
    # C — the answer moves TOWARD the third cell after the first merge
    a, b, c = take(3); base = _unit(rng.standard_normal(ds))
    S[a] = base; S[b] = _unit(base + 0.001 * rng.standard_normal(ds)); S[c] = _unit(base + 0.001 * rng.standard_normal(ds))
    rows[a], rows[b], rows[c] = {t2: 0.5, t1: 0.45}, {t2: 0.1, t4: 0.05}, {t1: 0.7}
    plants["C"] = (a, b, c)
    # D — a tie in a's row: argmax takes the lowest word id
    a, b = take(2); base = _unit(rng.standard_normal(ds))
    S[a] = base; S[b] = _unit(base + 0.001 * rng.standard_normal(ds))
    rows[a], rows[b] = {hi_t: 0.4, lo_t: 0.4}, {lo_t: 0.4}
    plants["D"] = (a, b)
    # E — no edge on one side -> None
    a, b = take(2); base = _unit(rng.standard_normal(ds))
    S[a] = base; S[b] = _unit(base + 0.001 * rng.standard_normal(ds))
    rows[a], rows[b] = {}, {t1: 0.9}
    plants["E"] = (a, b)
    # F1 / F2 — similarity exactly theta, and one ulp above it (one-hot construction: every product but one is an exact zero)
    k = rng.choice(ds, size=4, replace=False)
    for name, cval, (i0, i1) in (("F1", THETA, (k[0], k[1])), ("F2", float(np.nextafter(THETA, 2.0)), (k[2], k[3]))):
        a, b = take(2)
        va = np.zeros(ds); va[i0] = 1.0
        vb = np.zeros(ds); vb[i0] = cval; vb[i1] = float(np.sqrt(1.0 - cval * cval))
        S[a], S[b] = va, vb
        rows[a], rows[b] = {t4: 0.8}, {t4: 0.9}
        plants[name] = (a, b, int(i0))
    # I — isolated alike pairs, one answer each
    iso = []
    for _ in range(isolated_pairs):
        a, b = take(2); base = _unit(rng.standard_normal(ds))
        S[a] = base; S[b] = _unit(base + 0.0125 * rng.standard_normal(ds))
        t = int(rng.integers(0, n_w)); rows[a], rows[b] = {t: 0.8}, {t: 0.7}
        iso.append((a, b))
    plants["I"] = iso
    # random near-duplicate clusters (the bulk realism: cascades nobody planted)
    for _ in range(n_clusters):
        ids = take(int(rng.integers(2, 6)))
        centre = ids[0]
        for v in ids[1:]:
            sigma = float(rng.choice([0.004, 0.008, 0.012, 0.016, 0.02]))
            S[v] = _unit(S[centre] + sigma * rng.standard_normal(ds))
            if rng.random() < 0.6:
                rows[v] = {t: w * float(rng.uniform(0.8, 1.2)) for t, w in rows[centre].items()}
    # dead cells: 5 % of the ids nobody planted, their rows zeroed as a merge leaves them
    dead = take(max(1, n_s // 20))
    org.sight.n, org.words.n = n_s, n_w
    org.sight.cells[:n_s] = S; org.words.cells[:n_w] = Wd
    org.sight.alive[:n_s] = 1; org.words.alive[:n_w] = 1
    org.sight.misfires[:n_s] = rng.integers(0, 4, size=n_s); org.words.misfires[:n_w] = rng.integers(0, 4, size=n_w)
    for s, r in rows.items():
        for t, w in r.items():
            org.W[s, t] = w; org.mask[s, t] = 1; org.strikes[s, t] = int(rng.integers(0, 3))
    for s in dead:
        org.sight.alive[s] = 0; org.sight.misfires[s] = 0
        org.W[s, :] = 0.0; org.mask[s, :] = 0; org.strikes[s, :] = 0
    # words: 20 alike pairs; half share a column answer (a dedicated sight cell with the column's largest edge), half do not
    wpairs = []
    for q in range(20):
        u, v = sorted(int(x) for x in rng.choice(n_w, size=2, replace=False))
        if u in {p for pp in wpairs for p in pp} or v in {p for pp in wpairs for p in pp}:
            continue
        org.words.cells[v] = _unit(org.words.cells[u] + 0.001 * rng.standard_normal(dw))
        s_star = take(1)[0]; org.sight.alive[s_star] = 1
        org.W[s_star, :] = 0.0; org.mask[s_star, :] = 0; org.strikes[s_star, :] = 0
        org.W[s_star, u] = 5.0; org.mask[s_star, u] = 1
        if q % 2 == 0:
            org.W[s_star, v] = 5.0; org.mask[s_star, v] = 1
        wpairs.append((u, v))
    plants["words"] = wpairs
    org.t = 12345
    org.c["births_refused_redundant"] = 1          # cycle()'s redundant-share form fires (share 0.0)
    return org, plants


def _fp(org: Organism) -> Dict[str, object]:
    """Everything a merge pass can move: the digests (the dense one covers cells, alive, misfires, W/mask/strikes' live block, t,
    budget, the counters and all four logs) plus the merges log and the alive vectors named explicitly."""
    return {"merges": list(org.merges), "c": dict(org.c), "state_hash": org.state_hash(), "row_hash": org.row_hash(),
            "alive_s": org.sight.alive[: org.sight.n].tobytes(), "alive_w": org.words.alive[: org.words.n].tobytes()}


def _run_ref(org: Organism) -> float:
    t0 = time.perf_counter()
    _merge_reference(org, org.sight, list(org.sight.alive_ids()), axis=0)
    _merge_reference(org, org.words, list(org.words.alive_ids()), axis=1)
    return time.perf_counter() - t0


def _run_fast(org: Organism) -> float:
    t0 = time.perf_counter()
    org._merge(org.sight, list(org.sight.alive_ids()), axis=0, fast=True)
    org._merge(org.words, list(org.words.alive_ids()), axis=1, fast=True)
    return time.perf_counter() - t0


# --------------------------------------------------------------------------------------------------------------------------- tests
class TestReferenceIsVerbatim(unittest.TestCase):
    def test_the_reference_is_the_51f71ba_text(self) -> None:
        src = textwrap.indent(inspect.getsource(_merge), "    ")
        self.assertEqual(hashlib.sha256(src.encode()).hexdigest(), OLD_MERGE_SHA256,
                         "the reference must be genome/machinery.py@51f71ba's _merge byte for byte (re-indented)")


class TestCandidates(unittest.TestCase):
    """`_merge_candidates` is a FILTER: lexicographic, strictly upper-triangular, a superset of every pair whose OLD gate (b)
    passes, and it refuses (enumerates every pair) where its error bound does not hold."""

    def setUp(self) -> None:
        self.org, self.plants = _toy(700, 150, seed=11)
        self.ws = sorted(set(w for w in self.org.sight.alive_ids() if self.org.sight.alive[w]))

    def test_order_superset_and_selectivity(self) -> None:
        org, ws = self.org, self.ws
        cand = list(org._merge_candidates(org.sight, ws))
        self.assertTrue(all(i < j for i, j in cand), "strict upper triangle")
        self.assertTrue(all(p < q for p, q in zip(cand, cand[1:])), "strictly increasing in the old road's (i, j) order")
        n = len(ws)
        passing = {(i, j) for i in range(n) for j in range(i + 1, n)
                   if not (float(org.sight.cells[ws[i]] @ org.sight.cells[ws[j]]) <= org.g.theta_m)}
        self.assertTrue(passing, "positive control: the toy HAS pairs above theta")
        self.assertTrue(passing <= set(cand), f"every pair whose old gate (b) passes is a candidate (missing {sorted(passing - set(cand))[:5]})")
        self.assertLess(len(cand), n * (n - 1) // 2 // 20, "a filter: far fewer candidates than pairs")
        f1 = self.plants["F1"]; ia, ib = ws.index(f1[0]), ws.index(f1[1])
        self.assertIn((ia, ib), cand, "the pair at EXACTLY theta is a candidate (its fate is the old gate's, not the filter's)")

    def test_refuses_where_the_bound_does_not_hold(self) -> None:
        org, ws = self.org, self.ws
        n = len(ws)
        org.sight.cells[ws[3], 5] = np.nan
        cand = list(org._merge_candidates(org.sight, ws))
        self.assertEqual(len(cand), n * (n - 1) // 2, "a non-finite cell: every pair, in the old order (NaN passes the old gate)")
        self.assertEqual(cand[:3], [(0, 1), (0, 2), (0, 3)])
        org.sight.cells[ws[3], 5] = 0.0
        org.sight.cells[ws[4]] *= 1e6
        self.assertEqual(len(list(org._merge_candidates(org.sight, ws))), n * (n - 1) // 2, "norms far from 1: the bound fails -> every pair")

    def test_fewer_than_two(self) -> None:
        self.assertEqual(list(self.org._merge_candidates(self.org.sight, [])), [])
        self.assertEqual(list(self.org._merge_candidates(self.org.sight, self.ws[:1])), [])


class TestIdentitySmall(unittest.TestCase):
    """On a 700-cell toy: fast == reference on every planted case, under both hash forms, and the four positive controls are SEEN."""

    def _pair(self, seed: int = 21, hash_: bool = False, n_s: int = 700, n_w: int = 150):
        ref, plants = _toy(n_s, n_w, seed, hash_=hash_)
        fast, _ = _toy(n_s, n_w, seed, hash_=hash_)
        if hash_:
            ref.row_hash(); fast.row_hash()          # the witness scans its first block BEFORE the pass, as in a life
        return ref, fast, plants

    def test_identity_and_the_planted_cases(self) -> None:
        for hash_ in (False, True):
            ref, fast, P = self._pair(hash_=hash_)
            self.assertEqual(_fp(ref)["state_hash"], _fp(fast)["state_hash"], "the two toys start identical")
            _run_ref(ref); _run_fast(fast)
            fr, ff = _fp(ref), _fp(fast)
            self.assertEqual(ff["merges"], fr["merges"], f"merge list (pairs, order, survivor) hash_={hash_}")
            self.assertEqual(ff, fr, f"state after the pass hash_={hash_}")
            m = {(a, b) for (_t, area, a, b) in fr["merges"] if area == "sight"}
            A, B, C, D, E, F1, F2 = (P[k] for k in ("A", "B", "C", "D", "E", "F1", "F2"))
            self.assertTrue({(A[0], A[1]), (A[0], A[2])} <= m and (A[1], A[2]) not in m, "A: (a,b) and (a,c), never (b,c)")
            self.assertIn((B[0], B[1]), m); self.assertNotIn((B[0], B[2]), m, "B: a's answer moved away -> no (a,c)")
            self.assertIn((C[0], C[1]), m); self.assertIn((C[0], C[2]), m, "C: a's answer moved TO c's -> (a,c)")
            self.assertIn((D[0], D[1]), m, "D: a tie resolves to the lowest word id")
            self.assertNotIn((E[0], E[1]), m, "E: None answers never merge")
            self.assertNotIn((F1[0], F1[1]), m, "F1: exactly theta -> no merge (<=)")
            self.assertIn((F2[0], F2[1]), m, "F2: one ulp above theta -> merge")
            self.assertTrue(any(area == "words" for (_t, area, _a, _b) in fr["merges"]), "positive control: the words pass merged too")
            if hash_:
                from genome.witness import scratch_digest
                self.assertEqual(ff["row_hash"], scratch_digest(fast), "the sparse witness after the fast pass == its from-scratch recompute")

    def test_pc1_one_ulp_across_theta_is_seen(self) -> None:
        """PC1 — a planted one-ulp perturbation of ONE similarity across theta makes the two merge lists differ, in that pair only."""
        ref, fast, P = self._pair()
        a, b, i0 = P["F2"]
        fast.sight.cells[b, i0] = THETA                  # nextafter(theta, 2) -> theta: the pair's similarity drops one ulp, onto theta
        self.assertEqual(float(fast.sight.cells[a] @ fast.sight.cells[b]), THETA)
        _run_ref(ref); _run_fast(fast)
        mr, mf = _fp(ref)["merges"], _fp(fast)["merges"]
        self.assertNotEqual(mf, mr, "the comparison SEES a one-ulp move of one similarity across theta")
        self.assertEqual([x for x in mr if x not in mf and x[1] == "sight"], [(12345, "sight", a, b)], "and the sight difference is exactly that pair")
        self.assertEqual([x for x in mf if x not in mr and x[1] == "sight"], [])
        ref2, _, _ = self._pair(); ref2.sight.cells[b, i0] = THETA
        _run_ref(ref2)
        self.assertEqual(_fp(ref2)["merges"], mf, "the same perturbation under the reference: identical again")

    def test_pc1b_theta_nudged_past_the_closest_merge_is_seen(self) -> None:
        """PC1b (the advisor's form) — theta set to the smallest merged similarity: the fast road with it differs from the reference
        without it; the reference with it is identical to the fast road with it."""
        ref, fast, _ = self._pair()
        _run_ref(ref)
        sims = [float(ref.sight.cells[a] @ ref.sight.cells[b]) for (_t, area, a, b) in ref.merges if area == "sight"]
        closest = min(sims)
        fast.g.theta_m = closest
        _run_fast(fast)
        self.assertNotEqual(_fp(fast)["merges"], _fp(ref)["merges"])
        ref2, _, _ = self._pair(); ref2.g.theta_m = closest
        _run_ref(ref2)
        self.assertEqual(_fp(ref2), _fp(fast))

    def test_pc2_static_answers_mutant_is_seen(self) -> None:
        """PC2 — the «decide every pair from the start state» shape: answers read ONCE before the pass. It must differ (cases B, C),
        which proves the toy exercises the old road's order-dependence."""
        ref, mut, P = self._pair()
        ws = list(mut.sight.alive_ids())
        static = {int(w): mut._answer_of(mut.sight, w) for w in ws}
        orig = Organism._answer_of
        mut._answer_of = lambda area, cid: static[int(cid)] if area is mut.sight else orig(mut, area, cid)
        try:
            _merge_reference(mut, mut.sight, ws, axis=0)
        finally:
            del mut._answer_of
        _merge_reference(ref, ref.sight, list(ref.sight.alive_ids()), axis=0)
        mr = {(a, b) for (_t, _ar, a, b) in ref.merges}; mm = {(a, b) for (_t, _ar, a, b) in mut.merges}
        self.assertNotEqual(mm, mr)
        B, C = P["B"], P["C"]
        self.assertIn((B[0], B[2]), mm - mr, "B's (a,c): merged on the stale answer, refused on the live one")
        self.assertIn((C[0], C[2]), mr - mm, "C's (a,c): merged on the live answer, refused on the stale one")

    def test_pc3_gemm_decided_mutant_is_seen_and_the_fast_road_is_not_fooled(self) -> None:
        """PC3 — gate (b) decided on a gemm entry instead of the old 1-D `@`. On this box they differ in the last bits for most pairs
        (report §2); theta is set BETWEEN the two values of one isolated same-answer pair: the reference and the mutant must then
        differ, and the fast road (which only FILTERS on gemm, and decides by the old expression) must equal the reference."""
        base, _, P = self._pair()
        ws = list(base.sight.alive_ids()); pos = {int(w): k for k, w in enumerate(ws)}
        C = base.sight.cells[np.asarray(ws, dtype=np.int64)]
        G = C @ C.T
        straddle = None
        for a, b in P["I"]:
            d = float(base.sight.cells[a] @ base.sight.cells[b]); g = float(G[pos[a], pos[b]])
            if d != g:
                straddle = (a, b, d, g); break
        self.assertIsNotNone(straddle, "a same-answer pair whose ddot and gemm values differ exists (they differ for most pairs)")
        a, b, d, g = straddle
        theta = min(d, g)

        class _Row:
            def __init__(self, k: int): self.k = k
            def __matmul__(self, other: "_Row"): return G[self.k, other.k]

        class _GemmCells:
            def __getitem__(self, cid): return _Row(pos[int(cid)])

        ref, fast, _ = self._pair(); mut, _, _ = self._pair()
        for o in (ref, fast, mut):
            o.g.theta_m = theta
        real = mut.sight.cells
        mut.sight.cells = _GemmCells()
        try:
            _merge_reference(mut, mut.sight, list(mut.sight.alive_ids()), axis=0)
        finally:
            mut.sight.cells = real
        _merge_reference(ref, ref.sight, list(ref.sight.alive_ids()), axis=0)
        fast._merge(fast.sight, list(fast.sight.alive_ids()), axis=0, fast=True)
        mr = {(x, y) for (_t, _ar, x, y) in ref.merges}; mm = {(x, y) for (_t, _ar, x, y) in mut.merges}
        self.assertNotEqual(mm, mr, "the comparison SEES a gemm-vs-ddot last-bit difference at the threshold")
        self.assertIn((a, b), mm ^ mr)
        self.assertEqual(_fp(fast), _fp(ref), "the fast road is decided by the old arithmetic, not by the filter's")


class TestIdentityLarge(unittest.TestCase):
    """>= 4,000 alive sight cells, the whole cycle (sight pass, words pass, prune, the baseline): cycle() on the fast road vs the old
    cycle on the verbatim reference — identical merge lists and state; the cost of both printed (the saving is the claim)."""

    def test_cycle_identity_and_cost_at_4000_cells(self) -> None:
        ref, plants = _toy(4320, 400, seed=5)
        fast, _ = _toy(4320, 400, seed=5)
        alive = len(ref.sight.alive_ids())
        self.assertGreaterEqual(alive, 4000)
        t0 = time.perf_counter(); self.assertTrue(_cycle_reference(ref)); t_ref = time.perf_counter() - t0
        t0 = time.perf_counter(); self.assertTrue(cycle(fast)); t_fast = time.perf_counter() - t0
        fr, ff = _fp(ref), _fp(fast)
        self.assertEqual(ff["merges"], fr["merges"])
        self.assertEqual(ff, fr)
        n_sight = sum(1 for x in fr["merges"] if x[1] == "sight"); n_words = sum(1 for x in fr["merges"] if x[1] == "words")
        self.assertGreater(n_sight, 50, "positive control: the large toy merges (a vacuous identity proves nothing)")
        self.assertGreater(n_words, 0)
        print(f"\n[M6 cost] toy {alive} alive sight x {len(ref.words.alive_ids())} words: cycle() reference {t_ref * 1000:.0f} ms, fast {t_fast * 1000:.0f} ms "
              f"(x{t_ref / max(t_fast, 1e-9):.1f}); merges sight {n_sight} words {n_words}", flush=True)
        self.assertLess(t_fast * 10, t_ref, "the fast road costs under a tenth of the old one at 4,000 cells (both measured in this process)")


class TestWiring(unittest.TestCase):
    def test_cycle_takes_the_fast_road_and_moment_the_old_one(self) -> None:
        calls = []
        orig = Organism._merge

        def spy(self_, area, winners, axis, **kw):
            calls.append((area.name, kw.get("fast", False)))
            return orig(self_, area, winners, axis, **kw)

        Organism._merge = spy
        try:
            org, _ = _toy(300, 80, seed=3)
            cycle(org)
            self.assertEqual(calls, [("sight", True), ("words", True)], "cycle(): both passes on the fast road")
            calls.clear()
            rng = np.random.default_rng(0)
            for _ in range(5):
                org.moment(_unit(rng.standard_normal(org.sight.dim)), _unit(rng.standard_normal(org.words.dim)))
            self.assertTrue(calls, "positive control: moment() merged-checked its winners")
            self.assertTrue(all(f is False for _n, f in calls), "moment(): the old road, every pair of its few winners")
        finally:
            Organism._merge = orig


if __name__ == "__main__":
    unittest.main()
