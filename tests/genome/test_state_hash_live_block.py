# edit: Claude (Sonnet 5, builder F), 2026-09-21 17:14 +0400 -- G5-F task 2 (docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md
# item 2; MIND-MEMORY.md §4 R1): tests for the state_hash repair (hash only the live block
# W[:sight.n, :words.n] instead of the full nmax x nmax arrays). Full numbers, the two life-2 replay
# comparisons and the digest for the pin are reported in docs/briefs/G5-F-REPORT.md (those need life 2's
# full 17,768-canvas tape and a historical worktree checked out at the commit that actually ran it --
# too slow and too far from THIS repo's tree to belong in a unit test). This file pins the REPAIR's own
# properties on fast, self-contained fixtures: the invariant the repair depends on, that the digest
# genuinely changes, that Organism.load correctly REFUSES a pre-repair snapshot (never silently
# accepts), and that two independent builds under the new hash still agree.
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import GenomeError, Organism, parse_genome
from genome.run_g1 import PLANT_SHOWINGS, glance_rows, toy_streams

ROOT = Path(__file__).resolve().parent.parent.parent
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"

# The REAL closed life-2 snapshot (run-g4-life2-20260920-1212), saved under the pre-repair state_hash.
LIFE2_SNAPSHOT = Path("/data/dev/genome/run-g4-life2-20260920-1212/state/organism")


def _hash_old(org: Organism) -> str:
    """Verbatim copy of the PRE-REPAIR Organism.state_hash (the full nmax x nmax arrays) -- kept here,
    never restored into machinery.py, so this file can prove the digest MOVED without needing to check
    out the pre-repair commit."""
    h = hashlib.sha256()
    for a in (org.sight, org.words):
        h.update(a.cells[: a.n].tobytes()); h.update(a.alive.tobytes()); h.update(a.misfires.tobytes())
        h.update(np.int64(a.n).tobytes())
    h.update(org.W.tobytes()); h.update(org.mask.tobytes()); h.update(org.strikes.tobytes())
    h.update(np.int64(org.t).tobytes()); h.update(np.int64(org.budget_left).tobytes())
    h.update(json.dumps(org.c, sort_keys=True).encode())
    h.update(json.dumps(org.births).encode()); h.update(json.dumps(org.merges).encode())
    h.update(json.dumps(org.edges_log).encode()); h.update(json.dumps(org.prunes_log).encode())
    return h.hexdigest()


def _build_toy_organism(n_canvases: int = 40) -> Organism:
    """A small, fast, real Organism with actual sight/word births and edges -- G4-skeleton.genome's own
    toy dev stream (test_pin_skeleton.py's fixture), fed only partway for speed."""
    genome = parse_genome(GENOME_PATH.read_text())
    things, arr2, dev, held, a2, plant, shuffle_words, n_checked = toy_streams(genome, PLANT_SHOWINGS)
    dev_g = glance_rows(dev[:n_canvases], genome, "surprise")
    org = Organism(genome)
    org.new_arrival()
    for (t, feats, fix, truth, pid) in dev_g:
        xw = world.encode_word(t, genome.ear_blank_zero)
        for x in feats:
            org.moment(x, xw)
    return org


class TestLiveBlockInvariant(unittest.TestCase):
    """The repair's precondition: every nonzero entry of W/mask/strikes already lies inside
    [:sight.n, :words.n] -- a cell id is only ever written by _birth() with cid < area.n at write time,
    and area.n never decreases (CYCLE retires/merges cells but keeps their ids below n)."""

    def test_invariant_on_toy_organism(self) -> None:
        org = _build_toy_organism()
        self.assertGreater(org.sight.n, 0); self.assertGreater(org.words.n, 0)
        n_s, n_w = org.sight.n, org.words.n
        self.assertEqual(int(np.count_nonzero(org.W)), int(np.count_nonzero(org.W[:n_s, :n_w])))
        self.assertEqual(int(np.count_nonzero(org.mask)), int(np.count_nonzero(org.mask[:n_s, :n_w])))
        self.assertEqual(int(np.count_nonzero(org.strikes)), int(np.count_nonzero(org.strikes[:n_s, :n_w])))

    def test_invariant_on_real_life2_snapshot(self) -> None:
        """Loaded WITHOUT the hash self-check (Organism.load would correctly refuse this pre-repair
        snapshot under the new code -- test_old_snapshot_refuses_to_load below proves that refusal
        itself); this test only checks the array-shape invariant the repair depends on, on the real
        state life 2 actually ended in."""
        if not LIFE2_SNAPSHOT.with_suffix(".json").exists():
            self.skipTest("life 2's snapshot is not on this box")
        meta = json.loads(LIFE2_SNAPSHOT.with_suffix(".json").read_text())
        genome = parse_genome(meta["genome_text"])
        z = np.load(LIFE2_SNAPSHOT.with_suffix(".npz"))
        org = Organism(genome)
        org.sight.n = int(meta["sight_n"]); org.words.n = int(meta["words_n"])
        org.W[:] = z["W"]; org.mask[:] = z["mask"]; org.strikes[:] = z["strikes"]
        n_s, n_w = org.sight.n, org.words.n
        self.assertEqual(n_s, 700); self.assertEqual(n_w, 17)   # the real end state, named so a future re-run of life 2 doesn't silently pass on a different one
        self.assertEqual(int(np.count_nonzero(org.W)), int(np.count_nonzero(org.W[:n_s, :n_w])))
        self.assertEqual(int(np.count_nonzero(org.mask)), int(np.count_nonzero(org.mask[:n_s, :n_w])))
        self.assertEqual(int(np.count_nonzero(org.strikes)), int(np.count_nonzero(org.strikes[:n_s, :n_w])))


class TestDigestChanged(unittest.TestCase):
    def test_new_digest_differs_from_old_on_a_real_state(self) -> None:
        org = _build_toy_organism()
        self.assertLess(org.sight.n, org.g.nmax)   # the live block really is a strict subset -- otherwise this test proves nothing
        self.assertNotEqual(org.state_hash(), _hash_old(org))

    def test_new_digest_is_deterministic(self) -> None:
        org_a = _build_toy_organism(); org_b = _build_toy_organism()
        self.assertEqual(org_a.state_hash(), org_b.state_hash(), "two identical builds must hash identically under the new function too")


class TestLoadRefusesPreRepairSnapshot(unittest.TestCase):
    """Organism.load's saved-hash assertion must still FIRE -- loudly, by name -- on a snapshot saved
    under the OLD algorithm; it must never silently accept a digest computed a different way. This is
    the expected, correct behaviour of the repair (a migration/version-tag is the orchestrator's call,
    MIND-MEMORY.md §4 R1's own words), not a bug to work around."""

    def test_real_life2_snapshot_refuses(self) -> None:
        if not LIFE2_SNAPSHOT.with_suffix(".json").exists():
            self.skipTest("life 2's snapshot is not on this box")
        meta = json.loads(LIFE2_SNAPSHOT.with_suffix(".json").read_text())
        genome = parse_genome(meta["genome_text"])
        with self.assertRaises(GenomeError) as ctx:
            Organism.load(LIFE2_SNAPSHOT, genome)
        self.assertIn("state_hash", str(ctx.exception))
        self.assertIn(meta["state_hash"][:16], str(ctx.exception), "the error must name the OLD saved digest it could not match")

    def test_a_snapshot_saved_under_the_new_code_round_trips(self) -> None:
        """The positive control beside the refusal above: save/load under the SAME (new) code must still
        agree with itself -- the repair breaks only cross-version loads, never same-version ones."""
        org = _build_toy_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            reloaded = Organism.load(path, org.g)
        self.assertEqual(reloaded.state_hash(), org.state_hash())


if __name__ == "__main__":
    unittest.main()
