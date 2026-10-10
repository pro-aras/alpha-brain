# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 17:55 +0400 — REVISE-1 G-UNIT (tier 1 + bench B),
# written BEFORE the bench (law before code; RED on the law commit 66eaffa, where tools.brain.revise_bench
# does not exist). Pins against PREREG-REVISE-1.md (docs/brain/revise/, signed 2026-10-09 23:39, revise-1009
# @ 66eaffa): the FIVE tier-1 streams' exact rows through the real genome.think.believe (kind sequences +
# standing sets, incl. (e) LEDGER-REASSIGN with the cells UNCHANGED — the wild's own clash shape, verifier
# read V1); the derangement order-null arithmetic (clash count == standing-boundary count on all 10 seeded
# draws; the ordered flip == 1); the locality reader (the bystander X's chain byte-identical at every
# checkpoint, presence counts printed, the doctoring CAUGHT); the mechanism's own OFF-switch control
# (clash_enabled=False reads clash_refused and never a clash row, and the M-T1-FORM grader FAILS on that
# neutered store — G-PLANT (b)); bench B's exact crossing arithmetic (the always claim demotes AT the
# crossing observation, the usually twin trusted, the min_events floor, the sign null); determinism x2 to
# the last digit. Every constant is the bench's own declared one (imported, never re-derived here).
from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import mkdtemp

from genome import think as think_laws
from genome.web import Claim
from tools.brain import revise_bench as RB


def _row(line, kind, word, **kw):
    row = {"line": line, "kind": kind, "word": word}
    row.update(kw)
    return row


# The hand-traced disk rows of every stream (the store's own bytes, read back — revisit rows carry no
# "line" of their own on disk; the X bystander's belief is line 0 in every stream).
X_ROW = {"line": 0, "kind": "belief", "word": "x", "cells": [98, 99], "episodes": [0], "moment": 100,
         "clashes": []}

EXPECTED_DISK = {
    "a": [X_ROW,
          _row(1, "belief", "w", cells=[11, 22], episodes=[1], moment=101, clashes=[]),
          {"kind": "revisit", "of": 1, "word": "w", "episodes_added": [2], "moment": 102},
          {"kind": "revisit", "of": 1, "word": "w", "episodes_added": [3], "moment": 103},
          _row(4, "belief", "w", cells=[33, 44], episodes=[4], moment=104, clashes=[]),
          _row(5, "clash", "w", clashes=[1, 4], moment=104),
          {"kind": "revisit", "of": 4, "word": "w", "episodes_added": [5], "moment": 105},
          {"kind": "revisit", "of": 4, "word": "w", "episodes_added": [6], "moment": 106}],
    "b": [X_ROW,
          _row(1, "belief", "w", cells=[11, 22], episodes=[1], moment=101, clashes=[]),
          _row(2, "belief", "w", cells=[22, 33], episodes=[2], moment=102, clashes=[]),
          _row(3, "clash", "w", clashes=[1, 2], moment=102),
          {"kind": "revisit", "of": 2, "word": "w", "episodes_added": [3], "moment": 103}],
    "c": [X_ROW,
          _row(1, "belief", "w", cells=[11, 22], episodes=[1], moment=101, clashes=[]),
          _row(2, "extension", "w", of=1, added=[33], cells=[11, 22, 33], episodes=[2], moment=102),
          {"kind": "revisit", "of": 2, "word": "w", "episodes_added": [3], "moment": 103}],
    "d": [X_ROW,
          _row(1, "belief", "w", cells=[11, 22], episodes=[1], moment=101, clashes=[]),
          {"kind": "revisit", "of": 1, "word": "w", "episodes_added": [2], "moment": 102},
          {"kind": "revisit", "of": 1, "word": "w", "episodes_added": [3], "moment": 103}],
    "e": [X_ROW,
          _row(1, "belief", "w", cells=[11, 22], episodes=[1], moment=101, clashes=[]),
          _row(2, "belief", "w", cells=[11, 22], episodes=[2], moment=102, clashes=[]),
          _row(3, "clash", "w", clashes=[1, 2], moment=102),
          _row(4, "belief", "w", cells=[11, 22], episodes=[3], moment=103, clashes=[]),
          _row(5, "clash", "w", clashes=[2, 4], moment=103)],
}

EXPECTED_RETURNED = {
    "a": ["belief", "revisit", "revisit", "clash", "revisit", "revisit"],
    "b": ["belief", "clash", "revisit"],
    "c": ["belief", "extension", "revisit"],
    "d": ["belief", "revisit", "revisit"],
    "e": ["belief", "clash", "clash"],
}

EXPECTED_STANDING_CELLS = {"a": [33, 44], "b": [22, 33], "c": [11, 22, 33], "d": [11, 22], "e": [11, 22]}
EXPECTED_CLASHES = {"a": 1, "b": 1, "c": 0, "d": 0, "e": 2}

DERA_EXPECTED = [("ABBAAB", 3), ("ABAABB", 3), ("BABABA", 5), ("BBAAAB", 2), ("ABBABA", 4),
                 ("ABABAB", 5), ("BAAABB", 2), ("BBAABA", 3), ("BABBAA", 3), ("AABBBA", 2)]


class TestTier1StreamsExact(unittest.TestCase):
    """G-UNIT (the law §2): the FIVE planted stream shapes through the real believe() — exact rows."""

    def test_five_shapes_exact_rows_and_standings(self):
        for shape in RB.T1_SHAPES:
            with self.subTest(shape=shape):
                out = RB.run_tier1_stream(shape, mkdtemp())
                self.assertEqual(out["disk_rows"], EXPECTED_DISK[shape],
                                 f"shape {shape}: the store's exact rows (kind sequence + every field)")
                self.assertEqual(out["returned_kinds"], EXPECTED_RETURNED[shape])
                self.assertEqual(out["standing"]["cells"], EXPECTED_STANDING_CELLS[shape],
                                 f"shape {shape}: the standing belief's cells")
                self.assertEqual(out["clash_count"], EXPECTED_CLASHES[shape])

    def test_stream_e_cells_unchanged(self):
        """(e) LEDGER-REASSIGN: every belief row of W carries the UNCHANGED cells — the clash is the
        ledger half of rule 4 (the wild's own shape), never a cell move."""
        out = RB.run_tier1_stream("e", mkdtemp())
        belief_rows = [r for r in out["disk_rows"] if r["word"] == "w" and r["kind"] == "belief"]
        self.assertEqual(len(belief_rows), 3, "presence: the re-clash-per-call shape, 3 beliefs")
        for r in belief_rows:
            self.assertEqual(r["cells"], [11, 22], "the cells never moved; only the ledger label drifted")
        self.assertGreaterEqual(out["clash_count"], 1, "M-T1-FORM (e): >= 1 clash with the cells unchanged")

    def test_stream_a_post_flip_standing_exactly_the_planted_set(self):
        """M-T1-FORM (a) + M-T1-DIR: the post-flip standing is EXACTLY the planted post-flip set, and the
        pre-flip standing line never stands again after the flip (read off the store's own rows)."""
        out = RB.run_tier1_stream("a", mkdtemp())
        self.assertEqual(out["standing"]["cells"], [33, 44])
        self.assertEqual(out["standing"]["line"], 4, "the post-flip fork's belief row stands")
        post_rows = [r for r in out["disk_rows"] if r.get("moment", 0) >= 104]
        standing_lines = [r["line"] for r in post_rows if r["kind"] in ("belief", "extension")]
        self.assertNotIn(1, standing_lines, "the pre-flip standing (line 1) never reappears post-flip")


class TestClashDisabledControl(unittest.TestCase):
    """The mechanism's own OFF-switch as the control (the law §1): clash_enabled=False must read
    clash_refused and never a clash row — and the M-T1-FORM grader must FAIL on that neutered store
    (G-PLANT (b): a grader that cannot see this is blind)."""

    def test_control_reads_clash_refused_never_a_clash_row(self):
        for shape in ("a", "b", "e"):
            with self.subTest(shape=shape):
                out = RB.run_tier1_stream(shape, mkdtemp(), clash_enabled=False)
                refused = [k for k in out["returned_kinds"] if k == "clash_refused"]
                self.assertGreater(len(refused), 0, f"shape {shape}: presence of the refusal rows")
                self.assertNotIn("clash", out["disk_kinds"], "never a clash row on disk")
                self.assertEqual(out["clash_count"], 0)

    def test_control_fails_the_form_grader(self):
        out = RB.run_tier1(mkdtemp(), clash_enabled=False)
        graded = RB.grade_t1_form(out)
        self.assertFalse(graded["pass"], "the neutered store MUST fail M-T1-FORM (the control is caught)")
        self.assertFalse(graded["per_shape"]["a"]["pass"])
        self.assertFalse(graded["per_shape"]["b"]["pass"])
        self.assertFalse(graded["per_shape"]["e"]["pass"])

    def test_control_refusal_row_shape(self):
        out = RB.run_tier1_stream("a", mkdtemp(), clash_enabled=False)
        refusal = out["returned_rows"][3]
        self.assertEqual(refusal["kind"], "clash_refused")
        self.assertIsNone(refusal["line"], "a refusal writes nothing — no line of its own")
        self.assertEqual(refusal["of"], 1, "the refusal names the standing it refused to clash with")


class TestDerangementArithmetic(unittest.TestCase):
    """G-UNIT: the ORDER null — clash count == standing-boundary count on all 10 seeded draws;
    the ordered flip reads exactly 1 (the law §1's arithmetic, the verifier's construction)."""

    def test_the_draws_are_the_declared_ones(self):
        self.assertEqual(list(RB.DERA_DRAWS), [s for s, _ in DERA_EXPECTED])
        self.assertEqual(len(RB.derangement_family()), 18, "20 multiset permutations minus 2 monotone")
        for seq, boundaries in DERA_EXPECTED:
            self.assertGreaterEqual(boundaries, 2, "the draw excludes both monotone orders")
            self.assertEqual(RB.boundary_count(seq), boundaries)

    def test_family_all_above_one_boundary(self):
        for seq in RB.derangement_family():
            self.assertGreaterEqual(RB.boundary_count(seq), 2,
                                    "every non-monotone derangement has >= 2 boundaries (by construction)")

    def test_clash_count_equals_boundary_count_on_every_draw(self):
        out = RB.run_order_null(mkdtemp())
        self.assertEqual(out["ordered_clashes"], 1, "the ordered flip reads EXACTLY 1 clash (one boundary)")
        self.assertEqual(out["ordered_boundaries"], 1)
        for d in out["draws"]:
            self.assertEqual(d["clashes"], d["boundaries"],
                             f"{d['seq']}: the store's arithmetic — a clash per standing boundary")
            self.assertGreaterEqual(d["clashes"], 2)
        self.assertLess(out["ordered_clashes"], min(d["clashes"] for d in out["draws"]),
                        "M-T1-ORDER: the ordered flip strictly below all 10 derangements")


class TestLocalityReader(unittest.TestCase):
    """G-UNIT + M-T1-LOCAL: the bystander X's chain byte-identical at every checkpoint of every stream;
    the doctoring is CAUGHT (a grader that cannot see a rewrite is blind)."""

    def test_x_chain_byte_identical_everywhere(self):
        for shape in RB.T1_SHAPES:
            with self.subTest(shape=shape):
                out = RB.run_tier1_stream(shape, mkdtemp())
                self.assertEqual(out["x_presence"], 1, "presence: exactly 1 row of X, planted once")
                self.assertEqual(RB.locality_violations(out["x_bytes"]), [],
                                 "X's raw bytes identical at every checkpoint")
                # the store's own writer uses json.dumps' default separators; compare against THOSE bytes
                first = out["x_bytes"][0]
                self.assertEqual(first, [json.dumps(X_ROW) + "\n"],
                                 "the planted X row's exact bytes (the writer's own serialization)")

    def test_doctored_x_rewrite_is_caught(self):
        out = RB.run_tier1_stream("a", mkdtemp())
        clean = out["x_bytes"]
        tampered = [list(clean[0]) for _ in clean]
        tampered[2] = ['{"line": 0, "kind": "belief", "word": "x", "cells": [98, 97], '
                       '"episodes": [0], "moment": 100, "clashes": []}\n']
        self.assertEqual(RB.locality_violations(tampered), [2],
                         "a mid-stream rewrite of X's bytes must be caught at its checkpoint")

    def test_doctored_x_appended_row_is_caught(self):
        out = RB.run_tier1_stream("a", mkdtemp())
        grown = [list(s) for s in out["x_bytes"]]
        grown[3] = grown[3] + [json.dumps({"kind": "revisit", "of": 0, "word": "x",
                                           "episodes_added": [77], "moment": 200}) + "\n"]
        self.assertEqual(RB.locality_violations(grown), [3],
                         "an appended X row (a revisit the stream never planted) must be caught")


class TestBenchBArithmetic(unittest.TestCase):
    """G-UNIT: bench B's exact crossing arithmetic (web.py:366-382's own math, computed by hand here)."""

    def test_the_crossing_is_exactly_computable(self):
        # the hand arithmetic (the verifier read's own): level 0.05, floor 30:
        # 1/31 = 0.0323 holds, 2/32 = 0.0625 crosses -> demotion AT the 2nd contradiction, index 32.
        self.assertLessEqual(1 / 31, 0.05)
        self.assertGreater(2 / 32, 0.05)

    def test_always_demotes_exactly_at_the_crossing(self):
        out = RB.run_bench_b()
        a = out["always"]
        self.assertEqual(a["crossing"], 32, "M-B-DIR: demotion AT the crossing observation")
        self.assertEqual(a["first_demoted_at"], 32)
        self.assertEqual(a["states"][30], "trusted", "event 31 (1/31 contradicted) still holds")
        self.assertEqual(a["states"][31], "demoted", "event 32 (2/32) crosses")
        self.assertTrue(all(s == "trusted" for s in a["states"][:31]))
        self.assertTrue(all(s == "demoted" for s in a["states"][31:]))
        self.assertEqual((a["confirmed"], a["contradicted"]), (30, 5), "presence: the full stream landed")

    def test_usually_twin_stays_trusted_under_confirmations(self):
        u = RB.run_bench_b()["usually"]
        self.assertTrue(all(s == "trusted" for s in u["states"]))
        self.assertIsNone(u["first_demoted_at"])
        self.assertEqual(u["n_events"], 35, "presence: 35 observations")

    def test_floor_never_fires_below_min_events(self):
        f = RB.run_bench_b()["floor"]
        self.assertEqual(f["n_below_floor"], 29, "presence: 29 all-contradicted events below the floor")
        self.assertTrue(all(s == "trusted" for s in f["states_below_floor"]),
                        "M-B-FLOOR: an all-contradicted claim stays trusted below min_events")
        self.assertIsNone(f["first_demoted_at_below_floor"])
        self.assertEqual(f["edge_demoted_at"], 30, "the floor's edge printed: event 30 demotes")

    def test_sign_null_never_demotes(self):
        s = RB.run_bench_b()["sign"]
        self.assertEqual(s["n_events"], 35, "the same event count as the crossing run")
        self.assertEqual(s["contradicted"], 0, "contradictions swapped for confirmations")
        self.assertTrue(all(x == "trusted" for x in s["states"]))
        self.assertIsNone(s["first_demoted_at"],
                          "M-B-SIGN: the SIGN of the evidence, not its amount, drives the revision")


class TestDeterminism(unittest.TestCase):
    """G-UNIT/G-DET at unit scale: tiers 1 + B twice, identical to the last digit."""

    def test_tier1_and_bench_b_twice_identical(self):
        one = RB.run_tier1(mkdtemp())
        two = RB.run_tier1(mkdtemp())
        self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(two, sort_keys=True))
        self.assertEqual(json.dumps(RB.run_order_null(mkdtemp()), sort_keys=True),
                         json.dumps(RB.run_order_null(mkdtemp()), sort_keys=True))
        self.assertEqual(json.dumps(RB.run_bench_b(), sort_keys=True),
                         json.dumps(RB.run_bench_b(), sort_keys=True))


class TestClaimMechanismSanity(unittest.TestCase):
    """The bench's planted Claims are the organism's own web.Claim (never a re-implementation)."""

    def test_bench_b_uses_the_real_claim(self):
        c = Claim("T", "text", "always", 0.05, min_events=30)
        for k in range(1, 31):
            c.observe(True, at=k)
        self.assertEqual(c.state, "trusted")
        c.observe(False, at=31)
        self.assertEqual(c.state, "trusted", "1/31 = 0.0323 <= 0.05 holds")
        c.observe(False, at=32)
        self.assertEqual(c.state, "demoted", "2/32 = 0.0625 > 0.05 crosses")
        self.assertEqual(c.first_demoted_at, 32)


if __name__ == "__main__":
    unittest.main()
