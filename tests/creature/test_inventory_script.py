# edit: Claude (Fable 5.1), 2026-09-22 18:33 +0400 — tools/inventory.py's positive controls (plan L-2): the parser's attrs are read from the source; a value
# read nowhere is found (recall_k) while a value read everywhere is not (lr); a published sense with no consume branch is found by name.
import unittest
from pathlib import Path

TREE = Path(__file__).resolve().parent.parent.parent


class InventoryScript(unittest.TestCase):
    def test_parser_attrs_come_from_the_source(self):
        from tools.inventory import parser_attrs
        attrs = parser_attrs((TREE / "genome" / "machinery.py").read_text())
        self.assertIn("hebb_window", attrs["HEBB"]); self.assertIn("recall_k", attrs["RECALL"]); self.assertIn("lr", attrs["DELTA"])

    def test_unread_value_found_and_read_value_not(self):
        from tools.inventory import grep_reads
        self.assertEqual(grep_reads(TREE, "recall_k"), 0)       # the 11:16 inventory's row 53
        self.assertGreater(grep_reads(TREE, "lr"), 0)            # the negative control: DELTA's lr is read by _delta

    def test_a_published_sense_needs_a_consume_branch(self):
        from tools.inventory import consume_text
        c = consume_text(TREE)
        self.assertIn('"eye"', c); self.assertNotIn('"zzz-no-such-sense"', c)


if __name__ == "__main__":
    unittest.main()
