"""test_parse_g4.py — B1: the parser. Every G4 gene parses; a placeholder or a missing number refuses;
an unknown/misspelt gene refuses; G4-skeleton.genome and G1.genome still parse to the same Genome.

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B1 (docs/briefs/G4-BUILDER-B-GENES.md,
docs/G4-PREREG.md §3): genome/G4.genome = docs/G4-DESIGN.md §9 with the PREREG's ONE correction (GAZE
fixations 4). Twenty new genes, each a strict re.fullmatch clause in genome/machinery.py's parse_genome,
storing its parsed sub-dict in Genome.declared[GENE]. `AREA episodes from fast` is now legal beside
sight/words; `RECALL k=N` accepts any N >= 1 (k=1 stays byte-identical — proven here and by the pin).
"""
from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from genome.machinery import Genome, GenomeError, Organism, parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
# edit: Claude (Fable 5.1), 2026-09-19 23:31 +0400 — genome/G4.genome became THE LIFE's genome (PREREG §12: thetas written by gate G-a,
# TRAITS/SURPRISE/SENTENCE/HANDS declared OFF, THINK/EXAM/FROZEN added); these tests pinned the DRAFT's shape, so they now read a
# frozen copy of that draft (tests/genome/G4-draft.genome) and a new test pins the LIVE file's parsed shape instead.
G4_PATH = ROOT / "tests" / "genome" / "G4-draft.genome"
G4_LIFE_PATH = ROOT / "genome" / "G4.genome"
SKELETON_PATH = ROOT / "genome" / "G4-skeleton.genome"
G1_PATH = ROOT / "genome" / "G1.genome"

# G4 §3 B1's twenty new genes: (gene, a VALID line, a line missing the number / malformed).
NEW_GENES = {
    "BODY":      ("BODY     service creature threads eye ear door mind voice",
                  "BODY     service creature threads"),
    "TAPE":      ("TAPE     run/tape",
                  "TAPE"),
    "HEART":     ("HEART    every 10 s",
                  "HEART    every s"),
    "CRASH":     ("CRASH    sense restart journal; mind page",
                  "CRASH    sense restart journal mind page"),
    "TRAITS":    ("TRAITS   contrast head 32 lr 0.01 at sleep",
                  "TRAITS   contrast head lr 0.01 at sleep"),
    "SURPRISE":  ("SURPRISE floor 0.05",
                  "SURPRISE floor"),
    "CYCLE":     ("CYCLE    grow to 0.9 nmax then consolidate",
                  "CYCLE    grow to nmax then consolidate"),
    "FAST":      ("FAST     episodes 20000 keys sight words surprise",
                  "FAST     episodes keys sight words surprise"),
    "SLEEP":     ("SLEEP    every 2000 moments replay 200 by surprise",
                  "SLEEP    every moments replay 200 by surprise"),
    "PREDICT":   ("PREDICT  next glance; error scales delta 0.5..2.0; ranks replay; grades act",
                  "PREDICT  next glance; error scales delta ..2.0; ranks replay; grades act"),
    "FILE":      ("FILE     claim route decider due",
                  "FILE     claim route decider"),
    "CURIOSITY": ("CURIOSITY interests 50 operators recombine generalize specialize bridge",
                  "CURIOSITY interests operators recombine generalize specialize bridge"),
    "PARK":      ("PARK     after 3 identical dead-ends reopen on new-sense",
                  "PARK     after identical dead-ends reopen on new-sense"),
    "INDUCE":    ("INDUCE   rule from 5 episodes no counter",
                  "INDUCE   rule from episodes no counter"),
    "DEDUCE":    ("DEDUCE   one step",
                  "DEDUCE   one"),
    "BELIEF":    ("BELIEF   clash opens never overwrites",
                  "BELIEF   clash opens overwrites"),
    "SENTENCE":  ("SENTENCE two-word frames is near under-judge",
                  "SENTENCE two-word frames is near"),
    "WORLD":     ("WORLD    drawn every 5 s arrivals every 6 h; folder world/; web 6 per hour by curiosity",
                  "WORLD    drawn every s arrivals every 6 h; folder world/; web 6 per hour by curiosity"),
    "HANDS":     ("HANDS    jail alpha3/hands/jail_run",
                  "HANDS    jail"),
    "ASK":       ("ASK      what-is show is which next why",
                  "ASK      what-is show is which next"),
}


def _filled_g4_text() -> str:
    return G4_PATH.read_text().replace("cos<THETA_N", "cos<0.5").replace("cos>THETA_M", "cos>0.99")


class TestParseG4(unittest.TestCase):
    def test_g4_genome_parses_with_thetas_filled(self) -> None:
        g = parse_genome(_filled_g4_text())
        self.assertIsInstance(g, Genome)
        self.assertEqual(sorted(g.declared.keys()), sorted(NEW_GENES.keys()))
        self.assertEqual(g.recall_k, 3)
        self.assertEqual(set(g.areas.keys()), {"sight", "words", "episodes"})

    def test_g4_genome_refuses_unwritten_thetas(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(G4_PATH.read_text())

    def test_each_new_gene_declared_dict(self) -> None:
        g = parse_genome(_filled_g4_text())
        self.assertEqual(g.declared["BODY"], {"name": "creature", "threads": ["eye", "ear", "door", "mind", "voice"]})
        self.assertEqual(g.declared["TAPE"], {"path": "run/tape"})
        self.assertEqual(g.declared["HEART"], {"every_s": 10})
        self.assertEqual(g.declared["CRASH"], {"sense": "restart journal", "mind": "page"})
        self.assertEqual(g.declared["TRAITS"], {"head": 32, "lr": 0.01, "when": "sleep"})
        self.assertEqual(g.declared["SURPRISE"], {"floor": 0.05})
        self.assertEqual(g.declared["CYCLE"], {"grow_to": 0.9})
        self.assertEqual(g.declared["FAST"], {"episodes": 20000, "keys": ["sight", "words", "surprise"]})
        self.assertEqual(g.declared["SLEEP"], {"every": 2000, "replay": 200})
        self.assertEqual(g.declared["PREDICT"], {"delta_lo": 0.5, "delta_hi": 2.0})
        self.assertEqual(g.declared["FILE"], {"fields": ["claim", "route", "decider", "due"]})
        self.assertEqual(g.declared["CURIOSITY"], {"interests": 50, "operators": ["recombine", "generalize", "specialize", "bridge"]})
        self.assertEqual(g.declared["PARK"], {"after": 3})
        self.assertEqual(g.declared["INDUCE"], {"from_episodes": 5})
        self.assertEqual(g.declared["DEDUCE"], {"steps": 1})
        self.assertEqual(g.declared["BELIEF"], {"clash": "opens", "overwrite": False})
        self.assertEqual(g.declared["SENTENCE"], {"frames": ["is", "near"], "judged": True})
        self.assertEqual(g.declared["WORLD"], {"drawn_every_s": 5, "arrival_every_h": 6, "folder": "world/", "web_per_hour": 6})
        self.assertEqual(g.declared["HANDS"], {"jail": "alpha3/hands/jail_run"})
        self.assertEqual(g.declared["ASK"], {"verbs": ["what-is", "show", "is", "which", "next", "why"]})

    def test_misspelt_gene_refused(self) -> None:
        text = "SEED 1\nPREDCIT next glance\n"
        with self.assertRaises(GenomeError) as cm:
            parse_genome(text)
        self.assertIn("unknown gene", str(cm.exception))
        self.assertIn("PREDCIT", str(cm.exception))

    def test_each_new_gene_missing_number_or_malformed_is_refused(self) -> None:
        for gene, (valid_line, broken_line) in NEW_GENES.items():
            with self.subTest(gene=gene):
                with self.assertRaises(GenomeError, msg=f"{gene} accepted a malformed line: {broken_line!r}") as cm:
                    parse_genome(broken_line + "\n")
                self.assertIn(gene, str(cm.exception))

    def test_each_new_gene_valid_line_parses_alone(self) -> None:
        # a valid new-gene line, parsed alone, must not raise a "cannot read"/"unknown gene" GenomeError —
        # it may still raise the (expected, different) "genome lacks [...]" required-fields error.
        for gene, (valid_line, broken_line) in NEW_GENES.items():
            with self.subTest(gene=gene):
                try:
                    parse_genome(valid_line + "\n")
                except GenomeError as e:
                    self.assertIn("genome lacks", str(e), f"{gene}'s own VALID line was refused: {e}")

    def test_area_episodes_from_fast_allowed(self) -> None:
        g = parse_genome(_filled_g4_text())
        self.assertEqual(g.areas["episodes"], "fast")

    def test_area_still_requires_sight_and_words(self) -> None:
        text = "SEED 1\nAREA sight from retina\nAREA episodes from fast\n"
        with self.assertRaises(GenomeError):
            parse_genome(text)   # missing AREA words

    def test_area_refuses_a_fourth_unknown_area(self) -> None:
        text = _filled_g4_text() + "\nAREA smell from nose\n"
        with self.assertRaises(GenomeError):
            parse_genome(text)

    def test_skeleton_and_g1_still_parse_to_the_same_genome(self) -> None:
        gs = parse_genome(SKELETON_PATH.read_text())
        g1 = parse_genome(G1_PATH.read_text())
        # every rung-0/G1 field must agree (declared is empty on both — neither file uses a G4 gene)
        for field in ("seed", "eye", "ear_letters", "ear_blank_zero", "retina", "areas", "meet", "theta_n",
                      "misfires", "budget", "nmax", "kwta", "hebb_window", "lr", "prune_floor", "prune_chances",
                      "theta_m", "scale_every", "stages", "recall_k", "abstain_ratio", "resonate", "theta_words",
                      "abstain_margin", "gaze", "declared"):
            self.assertEqual(getattr(gs, field), getattr(g1, field), f"field {field!r} differs")

    def test_recall_k_any_n_ge_1(self) -> None:
        base = SKELETON_PATH.read_text()
        text7 = base.replace("RECALL k=1", "RECALL k=7")
        g = parse_genome(text7)
        self.assertEqual(g.recall_k, 7)
        text0 = base.replace("RECALL k=1", "RECALL k=0")
        with self.assertRaises(GenomeError) as cm:
            parse_genome(text0)
        self.assertIn("k must be >= 1", str(cm.exception))

    def test_recall_k_gt_1_adds_ranked_k_1_byte_identical(self) -> None:
        """B1: 'extend recall so k=1 is byte-identical to today'. A tiny hand-built organism (2 sight
        cells, 2 word cells, two edges of different strength from sight cell 0) — recall(k=1) and the
        no-k default must be the exact same dict (no "ranked" key); recall(k=2) adds "ranked", the two
        answer cells sorted by edge strength, and changes nothing else about the answer."""
        text = (
            "SEED 1\nSENSE eye 24x24 grey\nRETINA pool3 unit\nSENSE ear letters 1 blank=zero\n"
            "AREA sight from retina\nAREA words from ear\nMEET sight words\n"
            "BIRTH novelty cos<0.9\nBIRTH error misfires 3\nBUDGET 400 per arrival\nNMAX 10\nKWTA 5\n"
            "HEBB window 1\nDELTA lr 0.1\nPRUNE w<0.02 after 3 chances\nMERGE cos>0.99 same-answer\n"
            "SCALE every 1000 moments\nSTAGE 1 senses moments 0..0\nSTAGE 2 meet moments 0..\n"
            "RECALL k=1\nABSTAIN second/best > 0.85\n"
        )
        g = parse_genome(text)
        org = Organism(g)
        e0 = np.zeros(64); e0[0] = 1.0
        e1 = np.zeros(64); e1[1] = 1.0
        org.sight.cells[0] = e0; org.sight.cells[1] = e1
        org.sight.alive[0] = 1; org.sight.alive[1] = 1; org.sight.n = 2
        org.words.alive[0] = 1; org.words.alive[1] = 1; org.words.n = 2
        org.mask[0, 0] = 1; org.W[0, 0] = 0.8
        org.mask[0, 1] = 1; org.W[0, 1] = 0.5

        r_default = org.recall("sight", e0)
        r_k1 = org.recall("sight", e0, k=1)
        r_k2 = org.recall("sight", e0, k=2)

        self.assertNotIn("ranked", r_default)
        self.assertEqual(r_k1, r_default, "recall(k=1) must be byte-identical to the no-k default")
        self.assertEqual(r_k2["ranked"], [(0, 0.8), (1, 0.5)])
        for key in ("cell", "reason", "lit", "best", "second", "cos"):
            self.assertEqual(r_k2[key], r_default[key], f"k=2 changed {key!r} — it must only ADD 'ranked'")


if __name__ == "__main__":
    unittest.main()


class TestTheLifeGenome(unittest.TestCase):
    """The 24 h life's genome (PREREG §12): thetas WRITTEN, the declared set exactly as stamped, the OFF genes absent."""

    def test_life_genome_parses_with_written_thetas_and_the_declared_set(self) -> None:
        from genome.machinery import parse_genome
        g = parse_genome(G4_LIFE_PATH.read_text())
        self.assertAlmostEqual(g.theta_n, 0.952, places=3)
        self.assertAlmostEqual(g.theta_m, 0.9969, places=4)
        # edit: Claude (Fable 5.1), 2026-09-20 00:38 +0400 — PREREG §14: INDUCE and DEDUCE declared OFF (no interpreter in the mind), so the life's set is 17 genes
        self.assertEqual(sorted(g.declared), ["ASK", "BELIEF", "BODY", "CRASH", "CURIOSITY", "CYCLE", "EXAM", "FAST", "FILE",
                                              "FROZEN", "HEART", "PARK", "PREDICT", "SLEEP", "TAPE", "THINK", "WORLD"])
        for off in ("TRAITS", "SURPRISE", "SENTENCE", "HANDS", "INDUCE", "DEDUCE"):
            self.assertNotIn(off, g.declared)
        self.assertEqual(g.declared["THINK"], {"every": 10}); self.assertEqual(g.declared["EXAM"], {"every": 2000}); self.assertEqual(g.declared["FROZEN"], {"after": 50})
