# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 12:18 +0400 — A4L-COST task 1 (docs/briefs/A4L-COST.md): «Lossless by the invariant … assert it
# in a test on the hour-1 fixture's final state and on the snapshot copy» (the snapshot copy's test: tests/genome/test_a4l_cost_witness.py).
"""test_a4l_cost_fixture.py — alpha4-1's first hour, replayed under A4L-COST.genome by the replay tool's own road (the fixture read in
place: run_replay symlinks its payload directory and writes nothing to it). At the final state: the invariant the sparse form is
lossless by holds (0 violations, bit-level), and the incremental sparse witness equals its from-scratch recompute. ~2 min."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.replay import read_mind_journal, run_replay

TREE = Path(__file__).resolve().parents[2]
FIX_TAPE = Path("/data/dev/a4-ladder/fixtures/alpha4-1-hour1/tape/2026-09-23.jsonl")
COST = TREE / "genome" / "ladder" / "A4L-COST.genome"


@unittest.skipUnless(FIX_TAPE.exists(), "the A4 ladder hour-1 fixture is not on this box")
class TheHourOneFixturesFinalState(unittest.TestCase):
    def test_invariant_and_sparse_equals_scratch_at_the_final_state(self) -> None:
        from genome.witness import invariant_violations, scratch_digest
        out = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, out, True)
        minds = []
        orig = Mind.__init__

        def init(self_, *a, **k):
            orig(self_, *a, **k); minds.append(self_)

        Mind.__init__ = init
        try:
            journal = run_replay(COST, FIX_TAPE, out)
        finally:
            Mind.__init__ = orig
        o = minds[-1].org
        rows = read_mind_journal(journal)
        self.assertEqual(o.hash_form, "sparse")
        self.assertGreater(sum(1 for r in rows if "hash" in r), 1000, "positive control: the replay journaled its hashed rows")
        self.assertGreater(o.sight.n, 1000, "positive control: a real hour of growth")
        self.assertEqual(invariant_violations(o), {"W_nonzero_mask0": 0, "strikes_nonzero_mask0": 0, "padding_nonzero": 0})
        self.assertEqual(o.row_hash(), scratch_digest(o))
        self.assertNotEqual(o.row_hash(), o.state_hash())


if __name__ == "__main__":
    unittest.main()
