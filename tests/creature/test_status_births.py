# edit: Claude (Fable 5.1), 2026-09-22 12:0x +0400 — STATUS carries the BIRTH ledger the (iv) mark and the watch need: cells ever born per area
# (NMAX is a lifetime budget of ids — never reused, by G4 §3 B7's own design) and every cap refusal. g5-seam-1 spent its 2,000 sight ids by
# hour ~6 and refused 1,988 births at NMAX while STATUS showed `births_refused_budget 0` and the plant went unlearned (#164: the numbers
# that decide whether the mind can still learn belong on every write).
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body

from .test_exam import GENOME_PATH


class TestStatusBirthLedger(unittest.TestCase):
    def test_born_and_cap_refusals_are_on_every_status_write(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH); body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        st = body._build_status()
        for k in ("sight_born", "words_born", "sight_nmax", "births_refused_nmax", "births_refused_frozen", "births_refused_redundant", "births_refused_caps"):
            self.assertIn(k, st, k)
            self.assertIsInstance(st[k], int, k)
        self.assertEqual(st["births_refused_caps"], st["births_refused_budget"] + st["births_refused_nmax"] + st["births_refused_frozen"])
        self.assertEqual(st["sight_nmax"], body.mind.org.sight.nmax)


if __name__ == "__main__":
    unittest.main()
