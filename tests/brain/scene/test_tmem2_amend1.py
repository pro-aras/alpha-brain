# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:15 +0400 — PREREG-TMEM2 AMENDMENT 1 (final a7dceea, sha 6da8ff67…), its
# own rows, test-first (red on scene-tmem2 2b7d800): a claim set aside is UNGRADED «about a thing I did not see», counted under
# the claimed word b_T(h*) and moving nothing else; the two readings beside the rule; step 5's price a STOP when OVER.
# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:41 +0400 — AMENDMENT 2 (final b1e2b15, sha 76d8ac86…) REPLACES AMENDMENT 1
# §2's rule (the said word's band at h*) by the learner's own M2a «none»; the rows that pinned the band rule (a said word set
# aside where its band refuses h*; both rows through it; a confirmation never set aside by it) are retired from this file, and
# the rule's rows now live in test_tmem2_amend2.py. What of AMENDMENT 1 stands is pinned here.
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from brain.scene import health as H
from brain.scene import run_tmem2 as T


class TestWhatStands(unittest.TestCase):
    def test_the_reason(self) -> None:
        self.assertEqual(H.REASON_UNSEEN, "about a thing I did not see")

    def test_the_book_counts_a_set_aside_claim_under_the_claimed_word_and_moves_nothing_else(self) -> None:
        b = H.HealthBook()
        b.add_grades([("circle", True, "circle")] * 20)
        r = b.rows["circle"]
        before = (r.n_graded, r.cal20(), H.row_gate(r), list(r.outcomes))
        b.add_grades([("circle", None, "star")])
        self.assertEqual((r.n_graded, r.cal20(), H.row_gate(r), list(r.outcomes)), before)
        self.assertEqual(r.unseen, 1)
        self.assertEqual(b.row("star").missed, 0)                             # a set-aside claim is no miss of the said word
        self.assertEqual(r.summary()["unseen"], 1)
        b.add_grades([("circle", False, "star")])                              # a refutation: as before
        self.assertEqual((r.outcomes[-1], b.rows["star"].missed, r.unseen), (0, 1, 1))

    def test_a_set_aside_claim_moves_nothing_in_the_toy(self) -> None:
        for seed in (0, 1, 2):
            t = H.row_toy(seed)
            self.assertTrue(t["unseen_moves_nothing"], t)
            self.assertTrue(T.toy_passes(t), t)
        self.assertFalse(T.toy_passes(dict(H.row_toy(0), unseen_moves_nothing=False)))


class TestTheLawAndTheGate(unittest.TestCase):
    def test_the_amendments_sha_is_checked(self) -> None:
        self.assertEqual(T.PREREG_TMEM2_AMEND1_SHA256, "6da8ff679a317166c7a4e82bf9efd183785b5ecb90ad1bcb6fbae90d241386e6")
        self.assertEqual(T.PREREG_TMEM2_AMEND1_PATH.name, "PREREG-TMEM2-AMEND-1.md")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("not the amendment\n")
        try:
            with mock.patch.object(T, "PREREG_TMEM2_AMEND1_PATH", Path(f.name)):
                with self.assertRaises(T.TMem2Error):
                    T.check_prereg_tmem2()
        finally:
            os.unlink(f.name)

    def test_step5_the_price_is_a_stop_when_over(self) -> None:
        self.assertEqual(T.price_verdict(67.0), {"within": True, "stop": False})
        self.assertEqual(T.price_verdict(300.0), {"within": True, "stop": False})       # ≤ 5 CPU-min
        self.assertEqual(T.price_verdict(300.5), {"within": False, "stop": True})


if __name__ == "__main__":
    unittest.main()
