"""PREREG-W2 (SIGNED x3) — the bench runner's integration test over the record's head (the copies in scratch/bl2).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 08:56 +0400 — new file for the W2 build; law §3-§5.
# NOTE (declared): bench.py landed green in the slice-C2 round on scratch/w2_smoke_bench.py's mini-bench first; this is
# its committed form.

  A mini arms pass (canvases 250..320, TRAIN to 310, k_null 2) writes a record with the law's own fields; CONST reads
  0.5; the truth family runs over the same mini stream. Needs the copied record (scratch/bl2) — the suite's own
  territory.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.toys.w2 import bench as B
from tools.toys.w2 import marks as MK

BL2 = Path("scratch/bl2")


class TestBenchRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = B.arms_bench(BL2, 20261799, lo=250, hi=320, train_end=310, k_null=2)

    def test_the_record_carries_the_laws_fields(self):
        r = self.rec
        for k in ("test_n", "cont", "nostate", "oracle", "dealt_diag", "blind", "const", "m1", "proto_home",
                  "gradability", "stream"):
            self.assertIn(k, r, k)
        self.assertEqual(r["n_train"], 60)
        self.assertEqual(r["n_test"], 10)
        self.assertEqual(len(r["dealt_diag"]["unsure"]), 2)
        self.assertIn("fresh", r["proto_home"]["words"])
        self.assertIn("c_read", r["oracle"].get("unsure", {}))
        self.assertEqual(r["const"]["asked"], 0.5)                     # CONST at exactly 0.5 where computable

    def test_the_truth_family_over_the_mini_stream(self):
        cs, census, by_moment = B.generation(BL2, 20261799, hi=320)
        from tools.toys.w2 import stream as SM
        stream = SM.build(cs, census, 20261799, 250, 320)
        t = MK.m_true(cs[250:320], stream)
        a = MK.m_attrib(cs[250:320], stream)
        self.assertEqual(t["first_false"], None, t["first_false"])
        self.assertGreaterEqual(t["n_productions"], 1)
        self.assertEqual(a["n_bad_source"], 0)
        self.assertEqual(a["n_bad_tpl"], 0)
        self.assertEqual(a["n_unparseable"], 0)
        ci = MK.m_contingent_i(cs[250:320], stream)
        self.assertTrue(ci["pass"], ci)


if __name__ == "__main__":
    unittest.main()
