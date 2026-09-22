# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE), brief
# item 1: creature/genes.py's BOUNDS table, `draw_mutation`/`apply_mutation`/`mutate_genome_text`.
"""tests/creature/test_evolve_bounds.py

Round-trip: mutating every gene in BOUNDS (at its lo, hi and mid value) through `apply_mutation` and
re-parsing via `genome.machinery.parse_genome` must succeed AND change EXACTLY the one line named —
brief item 1's own test requirement ("mutating and re-parsing every gene in the table round-trips through
parse_genome"). Determinism: the same (seed, epoch, proposal_no) triple always draws the same (gene,
value) — the mind's own rng law. Exclusion: every EXCLUDED entry carries a "reason" string (never a bare
drop) and is never chosen by `draw_mutation`.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from creature.genes import BOUNDS, MUTABLE_KEYS, apply_mutation, draw_mutation, mutate_genome_text
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
BASE_TEXT = (ROOT / "genome" / "LIFE.genome").read_text()
EVOLVE_LINE = ("EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; "
               "adopt at sleep under the regression bar")
FULL_TEXT = BASE_TEXT.rstrip("\n") + "\n" + EVOLVE_LINE + "\n"


class TestBoundsTableShape(unittest.TestCase):
    def test_every_entry_is_mutable_or_carries_a_reason(self) -> None:
        for key, spec in BOUNDS.items():
            with self.subTest(key=key):
                if spec.get("excluded"):
                    self.assertIn("reason", spec, f"{key} is excluded but names no reason")
                    self.assertTrue(spec["reason"].strip())
                else:
                    for field in ("lo", "hi", "kind", "pattern"):
                        self.assertIn(field, spec, f"{key} is mutable but lacks {field!r}")
                    self.assertIn(spec["kind"], ("int", "float"))
                    if spec["kind"] == "float":
                        self.assertIn("decimals", spec)
                    self.assertLess(spec["lo"], spec["hi"])

    def test_mutable_keys_matches_the_brief_final_list(self) -> None:
        """The brief's own "Mutate RATES and THRESHOLDS only" sentence names exactly these 13 gene lines
        (15 values, BUDGET/SLEEP/PRUNE each carrying one or two): theta_n, DELTA lr, KWTA, BUDGET per
        arrival, SLEEP every/replay, THINK every, PRUNE w/chances, MERGE cos, ABSTAIN ratio, CURIOSITY
        interests, SCALE every, BIRTH misfires, PARK after."""
        self.assertEqual(len(MUTABLE_KEYS), 15)
        for key in ("BIRTH.theta_n", "DELTA.lr", "KWTA.k", "BUDGET.per_arrival", "SLEEP.every", "SLEEP.replay",
                    "THINK.every", "PRUNE.floor", "PRUNE.chances", "MERGE.theta_m", "ABSTAIN.ratio",
                    "CURIOSITY.interests", "SCALE.every", "BIRTH.misfires", "PARK.after"):
            self.assertIn(key, MUTABLE_KEYS)

    def test_shape_genes_are_excluded(self) -> None:
        for key in ("GAZE.fixations", "SENSE.ear_letters", "RETINA", "FAST.episodes", "HEBB.window",
                    "SENSE.colour", "EXAM.every", "SIT.every", "STAGE"):
            self.assertIn(key, BOUNDS)
            self.assertTrue(BOUNDS[key].get("excluded"), f"{key} must be excluded (a shape gene)")

    def test_frozen_and_induce_are_named_and_excluded(self) -> None:
        """Read conservatively from the brief's own final list (see creature/genes.py's module docstring):
        named here, never a silent drop."""
        for key in ("FROZEN.after", "INDUCE.from_episodes"):
            self.assertIn(key, BOUNDS)
            self.assertTrue(BOUNDS[key].get("excluded"))
            self.assertTrue(BOUNDS[key]["reason"].strip())

    def test_planted_bad_theta_n_is_outside_bounds(self) -> None:
        """The negative control's own planted value (0.5, brief item 4) must be OUTSIDE theta_n's mutable
        band — a mutation the worker would ever draw could never be the bad plant (the plant is always
        constructed directly, never drawn — advisor's point 7)."""
        spec = BOUNDS["BIRTH.theta_n"]
        self.assertLess(0.5, spec["lo"])


class TestRoundTrip(unittest.TestCase):
    def test_every_mutable_gene_round_trips_at_lo_hi_and_mid(self) -> None:
        for key in MUTABLE_KEYS:
            spec = BOUNDS[key]
            for v in (spec["lo"], spec["hi"], (spec["lo"] + spec["hi"]) / 2.0):
                val = int(round(v)) if spec["kind"] == "int" else round(float(v), spec["decimals"])
                with self.subTest(key=key, value=val):
                    new_text = apply_mutation(FULL_TEXT, key, val)
                    g2 = parse_genome(new_text)   # must not raise
                    self.assertIsNotNone(g2)
                    old_lines = FULL_TEXT.splitlines()
                    new_lines = new_text.splitlines()
                    self.assertEqual(len(old_lines), len(new_lines), f"{key}: line count changed")
                    diffs = [i for i in range(len(old_lines)) if old_lines[i] != new_lines[i]]
                    self.assertEqual(len(diffs), 1, f"{key}: expected exactly 1 changed line, got {diffs}")

    def test_think_optional_tail_survives_mutation(self) -> None:
        new_text = apply_mutation(FULL_TEXT, "THINK.every", 7)
        line = next(l for l in new_text.splitlines() if l.startswith("THINK"))
        self.assertIn("every 7 canvases", line)
        self.assertIn("; on its own thread; lands next boundary", line)
        g = parse_genome(new_text)
        self.assertEqual(g.declared["THINK"], {"every": 7, "threaded": True})

    def test_budget_suffix_survives_mutation_and_a_future_regen_clause(self) -> None:
        """Anchored on group(1)=prefix, group(2)=` per arrival` + whatever follows (advisor's point 8):
        proven here against LIFE.genome's own plain form AND a synthetic future form carrying builder G's
        own regen clause, so the substitution is provably forward-compatible with it."""
        new_text = apply_mutation(FULL_TEXT, "BUDGET.per_arrival", 500)
        line = next(l for l in new_text.splitlines() if l.startswith("BUDGET"))
        self.assertEqual(line.strip(), "BUDGET   500 per arrival")
        with_regen = FULL_TEXT.replace("BUDGET   400 per arrival",
                                        "BUDGET   400 per arrival; regenerate 1 per 60 moments")
        new_text2 = apply_mutation(with_regen, "BUDGET.per_arrival", 500)
        line2 = next(l for l in new_text2.splitlines() if l.startswith("BUDGET"))
        self.assertEqual(line2.strip(), "BUDGET   500 per arrival; regenerate 1 per 60 moments")

    def test_excluded_key_refuses(self) -> None:
        with self.assertRaises(ValueError):
            apply_mutation(FULL_TEXT, "STAGE", 5)

    def test_unknown_key_refuses(self) -> None:
        with self.assertRaises(ValueError):
            apply_mutation(FULL_TEXT, "NOT.A.GENE", 5)

    def test_a_pattern_matching_zero_times_refuses(self) -> None:
        """A genome text lacking the gene line entirely must refuse (never silently mutate nothing)."""
        text_without_kwta = "\n".join(l for l in FULL_TEXT.splitlines() if not l.startswith("KWTA"))
        with self.assertRaises(ValueError):
            apply_mutation(text_without_kwta, "KWTA.k", 6)


class TestDrawDeterminism(unittest.TestCase):
    def test_same_triple_draws_the_same_mutation(self) -> None:
        for epoch in range(3):
            for proposal_no in range(3):
                a = draw_mutation(20260923, epoch, proposal_no)
                b = draw_mutation(20260923, epoch, proposal_no)
                self.assertEqual(a, b)

    def test_different_proposal_no_can_draw_differently(self) -> None:
        draws = {draw_mutation(20260923, 1, n) for n in range(20)}
        self.assertGreater(len(draws), 1, "20 different proposal_no draws should not all collide on one (gene,value)")

    def test_draw_only_ever_picks_a_mutable_key(self) -> None:
        for epoch in range(5):
            for proposal_no in range(5):
                key, _value = draw_mutation(20260923, epoch, proposal_no)
                self.assertIn(key, MUTABLE_KEYS)
                self.assertFalse(BOUNDS[key].get("excluded"))

    def test_draw_stays_within_its_own_bounds(self) -> None:
        for epoch in range(10):
            for proposal_no in range(10):
                key, value = draw_mutation(20260923, epoch, proposal_no)
                spec = BOUNDS[key]
                self.assertGreaterEqual(value, spec["lo"])
                self.assertLessEqual(value, spec["hi"])

    def test_different_seed_can_draw_differently(self) -> None:
        a = draw_mutation(1, 0, 0)
        b = draw_mutation(2, 0, 0)
        # not asserting they always differ (a coincidence is possible) -- but across many seeds at least
        # one must differ, else the seed is not actually part of the stream.
        draws = {draw_mutation(s, 0, 0) for s in range(30)}
        self.assertGreater(len(draws), 1)


class TestMutateGenomeText(unittest.TestCase):
    def test_end_to_end_returns_text_key_and_value_and_parses(self) -> None:
        new_text, key, value = mutate_genome_text(FULL_TEXT, 20260923, 1, 1)
        self.assertIsInstance(new_text, str)
        self.assertIn(key, MUTABLE_KEYS)
        g = parse_genome(new_text)
        self.assertIsNotNone(g)
        # the mutant TEXT is what is stored (brief item 1) -- never a dict -- proven by the fact this
        # function's first return is a plain str fed straight to parse_genome above.


if __name__ == "__main__":
    unittest.main()
