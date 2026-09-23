# edit: Claude (Fable 5.1), 2026-09-23 19:55 +0400 — LADDER 2's genome pins (A4-LADDER-2-PREREG §2, §5): every genome under genome/ladder2/ parses WHOLE with the
# merged parser, and each rung differs from A4L-FLOOR by exactly its ONE declared change (R0 none; R0b/R1 one added line; R2/R3 one changed
# line; R5 the union of every rung's change + EVOLVE on + the nursery clause). A rung whose difference is not the one the PREREG names refuses here.
import difflib, unittest
from pathlib import Path
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
L, L2 = ROOT / "genome" / "ladder", ROOT / "genome" / "ladder2"


def _code(line: str) -> str:
    return line.split("#", 1)[0].rstrip()


def _genes(path: Path):
    return [_code(l) for l in path.read_text(encoding="utf-8").splitlines() if _code(l)]


def _diff(path: Path):
    a, b = _genes(L / "A4L-FLOOR.genome"), _genes(path)
    d = [x for x in difflib.unified_diff(a, b, lineterm="", n=0) if x[:1] in "+-" and x[:3] not in ("+++", "---")]
    return sorted(x for x in d if x.startswith("-")), sorted(x for x in d if x.startswith("+"))


class Ladder2Genomes(unittest.TestCase):
    def test_every_ladder2_genome_parses_whole(self):
        for p in sorted(L2.glob("*.genome")):
            with self.subTest(p.name):
                parse_genome(p.read_text(encoding="utf-8"))

    def test_r0_floor_is_the_floor_byte_for_byte_in_its_genes(self):
        self.assertEqual(_diff(L2 / "A4L2-FLOOR.genome"), ([], []))

    def test_r0b_cost_is_todays_cost_genome(self):
        self.assertEqual(_genes(L2 / "A4L2-COST.genome"), _genes(L / "A4L-COST.genome"))
        rem, add = _diff(L2 / "A4L2-COST.genome"); self.assertEqual(rem, []); self.assertEqual(len(add), 1); self.assertTrue(add[0].startswith("+HASH"))

    def test_r1_act_adds_exactly_the_value_line(self):
        rem, add = _diff(L2 / "A4L2-ACT.genome"); self.assertEqual(rem, []); self.assertEqual(add, ["+ACT      value reward 10; optimism 1"])

    def test_r2_line_changes_exactly_the_sentence_clause(self):
        rem, add = _diff(L2 / "A4L2-LINE.genome")
        self.assertEqual(len(rem), 1); self.assertEqual(len(add), 1)
        self.assertTrue(rem[0].startswith("-SENTENCE") and add[0].startswith("+SENTENCE") and "on the line" in add[0] and "on the line" not in rem[0])

    def test_r3_nursery_changes_exactly_the_read_line_by_the_gutenberg_clause(self):
        rem, add = _diff(L2 / "A4L2-NURSERY.genome")
        self.assertEqual(len(rem), 1); self.assertEqual(len(add), 1)
        self.assertTrue(rem[0].startswith("-SENSE    read") and add[0] == "+" + rem[0][1:] + "; gutenberg body only")
        g = parse_genome((L2 / "A4L2-NURSERY.genome").read_text(encoding="utf-8"))
        self.assertTrue(g.declared["SENSE_READ"].get("gutenberg_body_only"))

    def test_r5_all_is_the_union_with_evolve_on_and_the_nursery_clause(self):
        rem, add = _diff(L2 / "A4L2-ALL.genome")
        added_genes = {x.split()[0][1:] for x in add}
        for gene in ("EVOLVE", "ACT", "HASH", "AREA", "MEET", "CHAT", "WORLD", "SENTENCE", "SURPRISE", "ANSWER", "SENSE"):
            self.assertIn(gene, added_genes, gene)
        self.assertTrue(any("gutenberg body only" in x for x in add))
        self.assertTrue(any(x.startswith("+ACT      value") for x in add))
        g = parse_genome((L2 / "A4L2-ALL.genome").read_text(encoding="utf-8"))
        self.assertIn("EVOLVE", g.declared); self.assertIn("CHAT", g.declared); self.assertTrue(g.declared["SENSE_READ"].get("gutenberg_body_only"))


if __name__ == "__main__":
    unittest.main()
