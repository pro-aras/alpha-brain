# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:45 +0400 — PREREG-KW-1 §2 / §4.0 / §4.3, test-first (red on 865adcf: no genome/web.py).
# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:49 +0400 — PREREG-KW-1 AMENDMENT 1: the consolidation test is 3 spaced occasions + a Poisson tail
# at 0.001 (the signed lift test passed chance bursts); the test below recomputes it independently; S against S0 re-asserted.
"""tests/genome/test_web.py — the knowledge web: its metadata is TRUE (a recount written here, never in web.py), its rules keep
their budgets and their one difference each, its randomness is seeded, and a quantified self-memory is kept or demoted by life."""
from __future__ import annotations

import json
import math
import random
import unittest

import numpy as np

from genome import web as Wb


def stream(n=4000, v=40, seed=3, q=0.3):
    """A small toy stream (not the law's toy): Zipf-ish words with two planted associates each."""
    rng = random.Random(seed)
    words = [f"w{i:02d}" for i in range(v)]
    weights = [1.0 / (i + 1) for i in range(v)]
    assoc = {w: rng.sample([x for x in words if x != w], 2) for w in words}
    out = [rng.choices(words, weights)[0]]
    for _ in range(n - 1):
        cur = out[-1]
        out.append(rng.choice(assoc[cur]) if rng.random() < q else rng.choices(words, weights)[0])
    return out, assoc


def recount_nodes(ws):
    nodes = {}
    for t, w in enumerate(ws, 1):
        nd = nodes.setdefault(w, {"n": 0, "first": t, "last": t})
        nd["n"] += 1
        nd["last"] = t
    return nodes


def pair_events(ws, d=3):
    """The law's window, written here independently: each word pairs with each of the previous d DISTINCT words (itself excluded)."""
    recent, out = [], []
    for t, w in enumerate(ws, 1):
        for u in recent:
            if u != w:
                out.append((t, tuple(sorted((u, w)))))
        recent = [w] + [x for x in recent if x != w]
        recent = recent[:d]
    return out


def poisson_sf(c, E):
    """P(X >= c), X ~ Poisson(E): written here, not imported from web.py."""
    if E <= 0:
        return 0.0
    term = math.exp(-E)
    cdf = term
    for i in range(1, c):
        term *= E / i
        cdf += term
    return max(0.0, 1.0 - cdf)


class Nodes(unittest.TestCase):
    def test_node_metadata_equals_a_recount_for_every_rule(self):
        ws, _ = stream(1500)
        want = recount_nodes(ws)
        for rule in Wb.RULES:
            w = Wb.Web(rule, budget=None if rule == "H" else 80, seed=7)
            for x in ws:
                w.hear(x)
            got = {k: {"n": v["n"], "first": v["first"], "last": v["last"]} for k, v in w.nodes.items()}
            self.assertEqual(got, want, rule)
            self.assertEqual(w.t, len(ws))

    def test_the_window_is_the_previous_d_distinct_words(self):
        w = Wb.Web("H", seed=1)
        for x in ["a", "b", "a", "c", "d", "e"]:
            w.hear(x)
        want = {}
        for _t, k in pair_events(["a", "b", "a", "c", "d", "e"]):
            want[k] = want.get(k, 0) + 1
        self.assertEqual({k: e["c"] for k, e in w.edges.items()}, want)
        self.assertNotIn(("a", "a"), w.edges)


class Hebbian(unittest.TestCase):
    def test_every_pair_event_is_counted_and_nothing_is_dropped(self):
        ws, _ = stream(3000)
        w = Wb.Web("H", seed=1)
        for x in ws:
            w.hear(x)
        want = {}
        first = {}
        last = {}
        for t, k in pair_events(ws):
            want[k] = want.get(k, 0) + 1
            first.setdefault(k, t)
            last[k] = t
        self.assertEqual({k: e["c"] for k, e in w.edges.items()}, want)
        self.assertEqual({k: e["t0"] for k, e in w.edges.items()}, first)
        self.assertEqual({k: e["last"] for k, e in w.edges.items()}, last)

    def test_consolidation_is_the_amended_test_at_the_evidence_event(self):
        ws, _ = stream(3000)
        w = Wb.Web("H", seed=1)
        # recompute, independently, the first evidence event at which c >= 3, occasions >= 3 (gap > 6) and P(X >= c | E) < 0.001
        counts, t0, n, occ, lastev = {}, {}, {}, {}, {}
        want = {}
        recent = []
        for t, x in enumerate(ws, 1):
            n[x] = n.get(x, 0) + 1
            for u in recent:
                if u == x:
                    continue
                key = tuple(sorted((u, x)))
                if key not in t0:
                    t0[key], counts[key], occ[key], lastev[key] = t, 0, 0, None
                counts[key] += 1
                if lastev[key] is None or t - lastev[key] > 6:
                    occ[key] += 1
                lastev[key] = t
                if key not in want and counts[key] >= 3 and occ[key] >= 3:
                    fa, fb = n[key[0]] / t, n[key[1]] / t
                    E = 2 * 3 * fa * fb * max(1, t - t0[key] + 1)
                    if poisson_sf(counts[key], E) < 1e-3:
                        want[key] = t
            recent = ([x] + [y for y in recent if y != x])[:3]
        for x in ws:
            w.hear(x)
        got = {k: e["consolidated_at"] for k, e in w.edges.items() if e["state"] == "consolidated"}
        self.assertEqual(got, want)
        self.assertGreater(len(want), 5, "the stream consolidates something")
        self.assertEqual({k: e["occ"] for k, e in w.edges.items()}, occ)

    def test_a_shuffled_stream_consolidates_few_edges(self):
        ws, _ = stream(6000, v=40)
        sh = ws[:]
        random.Random(1).shuffle(sh)
        real, shuf = Wb.Web("H", seed=1), Wb.Web("H", seed=1)
        for x in ws:
            real.hear(x)
        for x in sh:
            shuf.hear(x)
        self.assertLess(len(shuf.consolidated()), len(real.consolidated()) / 2)


class Budgets(unittest.TestCase):
    def test_no_budgeted_rule_ever_holds_more_than_B_edges(self):
        ws, _ = stream(4000)
        for rule in ("F", "L", "S", "R", "S0"):
            w = Wb.Web(rule, budget=60, seed=11)
            peak = 0
            for x in ws:
                w.hear(x)
                peak = max(peak, len(w.edges))
            self.assertLessEqual(peak, 60, rule)
            self.assertGreater(peak, 0, rule)

    def test_first_come_never_makes_an_edge_after_it_is_full(self):
        ws, _ = stream(4000)
        w = Wb.Web("F", budget=30, seed=1)
        keys_at_full = None
        for x in ws:
            w.hear(x)
            if keys_at_full is None and len(w.edges) == 30:
                keys_at_full = set(w.edges)
        self.assertIsNotNone(keys_at_full)
        self.assertEqual(set(w.edges), keys_at_full)
        self.assertGreater(w.stats["refused"], 0)

    def test_least_evidence_out_replaces_the_weakest_silent_edge(self):
        w = Wb.Web("L", budget=2, seed=1, z=10 ** 6)
        for x in ["a", "b", "a", "b", "c", "d"]:
            w.hear(x)
        # a-b has 3 events, the rest 1 each; the budget forces replacements of the weakest SILENT edges, never of a-b
        self.assertIn(("a", "b"), w.edges)
        self.assertLessEqual(len(w.edges), 2)
        self.assertGreater(w.stats["replaced"], 0)

    def test_missed_chances_remove_a_silent_edge_and_never_a_consolidated_one(self):
        w = Wb.Web("L", budget=100, seed=1, z=3)
        seq = ["a", "b"] + ["a", "x", "y", "z", "b", "p", "q", "r"] * 4
        for x in seq:
            w.hear(x)
        self.assertNotIn(("a", "b"), w.edges, "a and b were heard apart 3+ times each since the pair's last evidence")
        self.assertGreater(w.stats["removed_missed"], 0)
        w2 = Wb.Web("L", budget=100, seed=1, z=3, k=1, alpha=1.0)
        for x in seq:
            w2.hear(x)
        self.assertEqual(w2.edges[("a", "b")]["state"], "consolidated")
        self.assertIn(("a", "b"), w2.edges)


class Randomness(unittest.TestCase):
    def test_the_same_seed_gives_byte_identical_webs_and_another_seed_differs(self):
        ws, _ = stream(3000)
        a, b, c = (Wb.Web("S", budget=80, seed=s) for s in (5, 5, 6))
        for x in ws:
            a.hear(x); b.hear(x); c.hear(x)
        self.assertEqual(a.dumps(), b.dumps())
        self.assertNotEqual(a.dumps(), c.dumps())

    def test_S_realises_about_p_of_the_pairs_it_is_offered(self):
        ws, _ = stream(6000, v=60)
        w = Wb.Web("S", budget=10 ** 9, seed=2, p=0.5, z=10 ** 9)
        for x in ws:
            w.hear(x)
        offered, made = w.stats["offered"], w.stats["realised"]
        self.assertGreater(offered, 1000)
        self.assertLess(abs(made / offered - 0.5), 0.05)

    def test_R_makes_edges_only_by_blind_sprouts(self):
        ws, _ = stream(2000)
        w = Wb.Web("R", budget=10 ** 9, seed=3, z=10 ** 9)
        for x in ws:
            w.hear(x)
        self.assertEqual(w.stats["realised"], 0, "R never makes an edge from the heard pair")
        self.assertGreater(w.stats["sprouted"], 1000)
        self.assertEqual(len(w.edges), w.stats["sprouted"] - w.stats["sprout_existing"])

    def test_S0_gives_the_evidence_to_random_pairs(self):
        ws, assoc = stream(6000, v=40)
        planted = {tuple(sorted((a, b))) for a, bs in assoc.items() for b in bs}
        s = Wb.Web("S", budget=80, seed=4)
        s0 = Wb.Web("S0", budget=80, seed=4)
        for x in ws:
            s.hear(x); s0.hear(x)
        def rec(w):
            return len({k for k, e in w.edges.items() if e["state"] == "consolidated"} & planted) / len(planted)
        self.assertGreater(rec(s), 0.15)
        self.assertGreater(rec(s), 2 * rec(s0))


class SaveLoad(unittest.TestCase):
    def test_a_saved_web_loads_to_the_same_bytes_and_goes_on_identically(self):
        ws, _ = stream(3000)
        a = Wb.Web("S", budget=80, seed=9)
        for x in ws[:1500]:
            a.hear(x)
        b = Wb.Web.loads(a.dumps())
        self.assertEqual(a.dumps(), b.dumps())
        for x in ws[1500:]:
            a.hear(x); b.hear(x)
        self.assertEqual(a.dumps(), b.dumps())

    def test_a_bad_rule_or_a_missing_budget_refuses_by_name(self):
        with self.assertRaises(Wb.WebError):
            Wb.Web("Q")
        with self.assertRaises(Wb.WebError):
            Wb.Web("L", budget=None)


class Faithful(unittest.TestCase):
    def test_the_recount_checker_passes_a_true_web_and_catches_one_planted_count(self):
        ws, _ = stream(2000)
        w = Wb.Web("L", budget=60, seed=1)
        for x in ws:
            w.hear(x)
        self.assertEqual(Wb.recount_errors(w, ws), [])
        k = next(iter(w.edges))
        w.edges[k]["c"] += 1
        self.assertNotEqual(Wb.recount_errors(w, ws), [])
        w.edges[k]["c"] -= 1
        node = next(iter(w.nodes))
        w.nodes[node]["n"] += 1
        self.assertNotEqual(Wb.recount_errors(w, ws), [])


class SelfClaims(unittest.TestCase):
    def test_an_always_claim_is_demoted_past_its_tolerance_and_stays_with_its_counts(self):
        c = Wb.Claim("F9", "the parent always says three words", "always", 0.05, source="implanted-knowledge", author="the seat")
        for i in range(100):
            c.observe(i % 10 != 0, at=i)          # 10 % contradictions
        self.assertEqual(c.state, "demoted")
        self.assertEqual((c.confirmed, c.contradicted), (90, 10))
        self.assertIsNotNone(c.first_demoted_at)

    def test_an_always_claim_within_tolerance_and_a_usually_claim_above_its_level_are_trusted(self):
        a = Wb.Claim("T9", "x", "always", 0.05)
        u = Wb.Claim("T8", "y", "usually", 0.70)
        for i in range(200):
            a.observe(i % 50 != 0, at=i)          # 2 % contradictions
            u.observe(i % 4 != 0, at=i)           # 75 % confirmations
        self.assertEqual((a.state, u.state), ("trusted", "trusted"))

    def test_no_verdict_before_thirty_events(self):
        c = Wb.Claim("F8", "z", "always", 0.05)
        for i in range(29):
            c.observe(False, at=i)
        self.assertEqual(c.state, "trusted")
        c.observe(False, at=29)
        self.assertEqual(c.state, "demoted")

    def test_a_usually_claim_below_its_level_is_demoted(self):
        u = Wb.Claim("F7", "w", "usually", 0.70)
        for i in range(100):
            u.observe(i % 2 == 0, at=i)           # 50 %
        self.assertEqual(u.state, "demoted")


# edit: Claude (Opus 5.5, the seat), 2026-09-29 22:54 +0400 — PREREG-KW-1 §4.3 K10: the SELF node's lived rates equal a recount written here.
class SelfNodeLived(unittest.TestCase):
    def test_the_lived_rates_equal_a_recount(self):
        rng = random.Random(5)
        shapes = ["circle", "ring", "star"]
        node = Wb.SelfNode(author="t")
        turns = []
        for i in range(400):
            node.canvas(rng.choice([3, 4, 4, 4]))
            heard = [rng.choice(["big", "small"]), rng.choice(shapes)][: rng.choice([1, 2])]
            expected = [[rng.choice(shapes), "big"], [rng.choice(shapes), "small"]] if i > 20 else []
            surprise = None if not expected else (0.0 if all(any(w in h for h in expected) for w in heard) else 0.5)
            node.turn(heard, expected, surprise)
            turns.append((heard, expected, surprise))
        fix = {}
        n_exp = ok = 0
        words = {}
        for heard, expected, surprise in turns:
            if surprise is None:
                continue
            n_exp += 1
            ok += int(surprise == 0)
            union = {w for h in expected for w in h}
            for w in dict.fromkeys(heard):
                hc = words.setdefault(w, [0, 0])
                hc[0] += 1
                hc[1] += int(w in union)
        lv = node.to_dict()["lived"]
        self.assertEqual(lv["canvases"], 400)
        self.assertEqual(sum(lv["fix"].values()), 400)
        self.assertEqual((lv["turns_expecting"], lv["expect_confirmed"]), (n_exp, ok))
        self.assertEqual(lv["words"], words)
        w0 = next(iter(words))
        self.assertAlmostEqual(node.reliability(w0), words[w0][1] / words[w0][0])
        self.assertIsNone(node.reliability("never-heard"))

    def test_placed_claims_keep_their_source_and_author(self):
        node = Wb.SelfNode(author="life-x")
        node.place(Wb.Claim("T1", "x", "always", 0.05, source="implanted-knowledge", author="the seat"))
        d = node.to_dict()
        self.assertEqual(d["claims"]["T1"]["source"], "implanted-knowledge")
        self.assertEqual(d["claims"]["T1"]["author"], "the seat")


if __name__ == "__main__":
    unittest.main()
