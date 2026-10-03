# edit: Claude (Sonnet 5.5, swarm sleep), 2026-10-03 11:26 +0400 — PREREG-SLEEP-IDLE §2.1 (co-signed 5b21fa7): the idle clause, a SUFFIX of the SLEEP line,
# written before the parser branch. The old forms parse to exactly what they parsed to, and an old malformed form refuses with today's text; every
# misspelling of the new clause refuses BY NAME; EVOLVE's SLEEP patterns still match the new line and a mutation that the law forbids is refused at parse.
"""tests/genome/test_parse_sleep_idle.py — PREREG-SLEEP-IDLE §2.1."""
from __future__ import annotations

import unittest

from creature.genes import apply_mutation, unwired
from genome.machinery import GenomeError, parse_genome

from .test_parse_g4 import _filled_g4_text

OLD = "SLEEP    every 2000 moments replay 200 by surprise"
CLAUSE = "when idle for 1 s replay by surprise walking in units of 1 s at most 0.087 per moment"
IDLE = f"SLEEP    every 2500 moments replay 0 by surprise; {CLAUSE}"


def genome_with(line: str) -> str:
    base = _filled_g4_text()
    assert OLD in base, "the fixture's SLEEP line moved — update OLD above"
    return base.replace(OLD, line)


def declared(line: str) -> dict:
    return parse_genome(genome_with(line)).declared["SLEEP"]


class OldFormsUnchanged(unittest.TestCase):
    def test_the_scheduled_form_parses_to_exactly_its_old_dict(self):
        d = declared(OLD)
        self.assertEqual(d, {"every": 2000, "replay": 200})
        self.assertNotIn("idle", d)

    def test_the_boundary_with_replay_zero_is_the_a_b_n_arm_and_parses_alone(self):
        self.assertEqual(declared("SLEEP    every 2500 moments replay 0 by surprise"), {"every": 2500, "replay": 0})

    def test_an_old_malformed_form_refuses_with_todays_text_unchanged(self):
        with self.assertRaises(GenomeError) as cm:
            parse_genome(genome_with("SLEEP    every moments replay 200 by surprise"))
        self.assertEqual(str(cm.exception), "SLEEP: cannot read 'every moments replay 200 by surprise' (B7: SLEEP every <n> moments replay <m> by surprise)")

    def test_a_genome_without_the_clause_has_no_idle_key_anywhere(self):
        g = parse_genome(genome_with(OLD))
        self.assertNotIn("idle", g.declared["SLEEP"])


class IdleClauseParses(unittest.TestCase):
    def test_the_walking_clause(self):
        self.assertEqual(declared(IDLE), {"every": 2500, "replay": 0, "idle": {"after_s": 1.0, "walking": True, "unit_s": 1.0, "rate": 0.087}})

    def test_the_head_rule_is_the_same_clause_without_walking(self):
        d = declared(IDLE.replace(" walking", ""))
        self.assertEqual(d["idle"], {"after_s": 1.0, "walking": False, "unit_s": 1.0, "rate": 0.087})
        self.assertEqual((d["every"], d["replay"]), (2500, 0))

    def test_other_numbers_and_the_inclusive_range_ends(self):
        for after, unit, rate in ((0.05, 0.01, 1), (600, 30, 0.0001), (2.5, 0.25, 0.5)):
            with self.subTest(after=after, unit=unit, rate=rate):
                d = declared(f"SLEEP    every 2500 moments replay 0 by surprise; when idle for {after} s replay by surprise in units of {unit} s at most {rate} per moment")
                self.assertEqual(d["idle"], {"after_s": float(after), "walking": False, "unit_s": float(unit), "rate": float(rate)})

    def test_a_trailing_comment_and_extra_spaces_are_the_parsers_business_not_the_clauses(self):
        d = declared(IDLE.replace("; when idle for 1 s", ";   when   idle  for 1   s") + "      # the primary arm")
        self.assertEqual(d["idle"]["walking"], True)

    def test_no_gene_key_is_unwired_by_the_new_form(self):
        self.assertEqual([k for k in unwired(parse_genome(genome_with(IDLE)).declared) if k == "SLEEP"], [])


class IdleClauseRefusesByName(unittest.TestCase):
    def refuses(self, line: str, *needles: str):
        with self.assertRaises(GenomeError, msg=line) as cm:
            parse_genome(genome_with(line))
        text = str(cm.exception)
        self.assertTrue(text.startswith("SLEEP:"), text)
        for n in needles:
            self.assertIn(n, text)
        return text

    def test_every_misspelling_refuses_and_names_the_gene_and_the_grammar(self):
        bad = {
            "connector misspelt": IDLE.replace("; when idle", "; whn idle"),
            "capital": IDLE.replace("; when idle", "; When idle"),
            "no space after the semicolon": IDLE.replace("; when idle", ";when idle"),
            "no semicolon": IDLE.replace("; when idle", " when idle"),
            "rule misspelt": IDLE.replace("by surprise walking", "by suprise walking"),
            "walking misspelt": IDLE.replace("walking", "walkin"),
            "units misspelt": IDLE.replace("in units of", "in unit of"),
            "at most missing": IDLE.replace("at most ", ""),
            "per moments": IDLE.replace("per moment", "per moments"),
            "after number missing": IDLE.replace("for 1 s replay", "for s replay"),
            "unit s missing": IDLE.replace("units of 1 s at", "units of 1 at"),
            "trailing words": IDLE + " extra",
            "no rule": IDLE.replace("replay by surprise walking", "replay walking"),
        }
        for name, line in bad.items():
            with self.subTest(case=name):
                self.refuses(line, "SLEEP: cannot read", "when idle for <s> s replay by surprise")

    def test_the_boundary_must_carry_replay_zero(self):
        t = self.refuses(IDLE.replace("replay 0 by surprise;", "replay 200 by surprise;"), "idle clause needs replay 0", "got replay 200")
        self.assertIn("two replay clocks", t)

    def test_there_is_no_idle_only_form_in_this_law(self):
        self.refuses(f"SLEEP    {CLAUSE}", "suffix of the boundary form", "every <n> moments replay 0 by surprise; when idle")

    def test_numbers_out_of_range_name_the_field_and_the_range(self):
        cases = {
            "after_s": ("0.04", "601"),
            "unit_s": ("0.009", "31"),
            "rate": ("0", "1.0001", "-0.1"),
        }
        for field, vals in cases.items():
            for v in vals:
                with self.subTest(field=field, value=v):
                    if field == "after_s":
                        line = IDLE.replace("for 1 s replay", f"for {v} s replay")
                    elif field == "unit_s":
                        line = IDLE.replace("units of 1 s", f"units of {v} s")
                    else:
                        line = IDLE.replace("at most 0.087", f"at most {v}")
                    self.refuses(line, "SLEEP: idle", field, "out of range")


class EvolveStillWorks(unittest.TestCase):
    def test_every_mutation_keeps_the_clause_and_still_parses(self):
        text = genome_with(IDLE)
        out = apply_mutation(text, "SLEEP.every", 3000)
        d = parse_genome(out).declared["SLEEP"]
        self.assertEqual((d["every"], d["replay"]), (3000, 0))
        self.assertEqual(d["idle"], {"after_s": 1.0, "walking": True, "unit_s": 1.0, "rate": 0.087})

    def test_a_replay_mutation_yields_a_text_the_parser_refuses_by_name(self):
        out = apply_mutation(genome_with(IDLE), "SLEEP.replay", 100)
        self.assertIn("replay 100 by surprise; when idle", out)
        with self.assertRaisesRegex(GenomeError, "idle clause needs replay 0"):
            parse_genome(out)


if __name__ == "__main__":
    unittest.main()
