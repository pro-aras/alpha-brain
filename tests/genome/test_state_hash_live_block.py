# edit: Claude (Sonnet 5, builder F), 2026-09-21 17:14 +0400 -- G5-F task 2 (docs/briefs/G5-F-BIND-DIAGNOSTIC-AND-REPAIRS.md
# item 2; MIND-MEMORY.md §4 R1): tests for the state_hash repair (hash only the live block
# W[:sight.n, :words.n] instead of the full nmax x nmax arrays). Full numbers, the two life-2 replay
# comparisons and the digest for the pin are reported in docs/briefs/G5-F-REPORT.md (those need life 2's
# full 17,768-canvas tape and a historical worktree checked out at the commit that actually ran it --
# too slow and too far from THIS repo's tree to belong in a unit test). This file pins the REPAIR's own
# properties on fast, self-contained fixtures: the invariant the repair depends on, that the digest
# genuinely changes, that two independent builds under the new hash still agree, and (2026-09-21
# 17:4x +0400, the orchestrator's follow-up task) that Organism.load ACCEPTS a snapshot saved under
# EITHER digest (new live-block or legacy full-array) and refuses only a genuinely corrupted one.
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
        """Loaded by hand (bypassing Organism.load's hash check entirely, on purpose -- this test only
        checks the array-shape invariant the repair depends on, on the real state life 2 actually ended
        in; TestLoadAcceptsEitherDigest.test_real_life2_snapshot_now_loads below is the one that goes
        through the real load() path and checks it succeeds)."""
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


class TestLoadAcceptsEitherDigest(unittest.TestCase):
    """SUPERSEDES this file's original test (which asserted Organism.load REFUSES a pre-repair
    snapshot -- correct at the time, and now the orchestrator's explicit follow-up task, 2026-09-21
    17:4x +0400: the closed lives' readers (tools/verdict_g4.py's W3-2 reach control, the exam) must
    still LOAD old-format snapshots). load() now tries the NEW live-block hash first, falls back to
    `_state_hash_legacy()` (kept verbatim) on mismatch, and refuses only when BOTH fail -- so a
    snapshot saved by EITHER generation of the code loads, and a genuinely corrupted one still refuses
    loudly, by name. Three cases, all on the SAME small toy organism, per the orchestrator's word."""

    def test_new_format_snapshot_loads(self) -> None:
        """A snapshot saved by the CURRENT code (meta["state_hash"] == state_hash()) loads on the fast
        path -- no fallback needed."""
        org = _build_toy_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            meta = json.loads(path.with_suffix(".json").read_text())
            self.assertEqual(meta["state_hash"], org.state_hash(), "save() must write the NEW hash, not the legacy one")
            reloaded = Organism.load(path, org.g)
        self.assertEqual(reloaded.state_hash(), org.state_hash())

    def test_legacy_format_snapshot_loads(self) -> None:
        """A snapshot whose saved `state_hash` is the LEGACY (pre-repair) digest -- built by saving
        normally then overwriting the .json's state_hash field with _state_hash_legacy()'s value, the
        exact shape every real pre-repair snapshot on disk has -- must load via the fallback."""
        org = _build_toy_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            meta = json.loads(path.with_suffix(".json").read_text())
            self.assertNotEqual(org.state_hash(), org._state_hash_legacy(), "the fixture is meaningless if the two digests coincide")
            meta["state_hash"] = org._state_hash_legacy()
            path.with_suffix(".json").write_text(json.dumps(meta))
            reloaded = Organism.load(path, org.g)   # must NOT raise
        self.assertEqual(reloaded.state_hash(), org.state_hash(), "the loaded organism's own state must still be the real (new-hash) state")

    def test_corrupted_snapshot_refuses_under_both(self) -> None:
        """One entry of sight_cells flipped after save() -- corrupting `W` itself does not reach this
        toy's fixture (40 canvases never reach G4-skeleton.genome's stage2_start, so W/mask/strikes stay
        genuinely all-zero here, same value under both digests either way); sight_cells is hashed
        identically by state_hash() and _state_hash_legacy() (`a.cells[:a.n]`, untouched by the live-
        block repair) so corrupting it breaks BOTH digests just as surely. load() must still raise
        GenomeError, by name, naming the digest it could not match either way."""
        org = _build_toy_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            z = dict(np.load(path.with_suffix(".npz")))
            self.assertGreater(int(np.count_nonzero(z["sight_cells"])), 0, "the fixture needs a nonzero sight_cells entry to corrupt")
            nz = np.argwhere(z["sight_cells"] != 0)[0]
            z["sight_cells"][tuple(nz)] = z["sight_cells"][tuple(nz)] + 1.0
            np.savez_compressed(path, **z)
            meta = json.loads(path.with_suffix(".json").read_text())
            with self.assertRaises(GenomeError) as ctx:
                Organism.load(path, org.g)
        self.assertIn("state_hash", str(ctx.exception))
        self.assertIn(meta["state_hash"][:16], str(ctx.exception), "the error must name the saved digest it could not match either way")

    def test_real_life2_snapshot_now_loads(self) -> None:
        """The real thing, read-only, on disk: life 2's actual closed-root snapshot (saved under the
        pre-repair, legacy-only code) now loads without error."""
        if not LIFE2_SNAPSHOT.with_suffix(".json").exists():
            self.skipTest("life 2's snapshot is not on this box")
        meta = json.loads(LIFE2_SNAPSHOT.with_suffix(".json").read_text())
        genome = parse_genome(meta["genome_text"])
        org = Organism.load(LIFE2_SNAPSHOT, genome)   # must NOT raise
        self.assertEqual(org._state_hash_legacy(), meta["state_hash"], "life 2's snapshot is a real legacy-format one -- the control that this test means what it says")
        self.assertEqual(org.sight.n, 700); self.assertEqual(org.words.n, 17)

    def test_real_life3a_snapshot_now_loads(self) -> None:
        """Same control, life 3a's snapshot."""
        path = Path("/data/dev/genome/run-g4-life3a-20260921-1314/state/organism")
        if not path.with_suffix(".json").exists():
            self.skipTest("life 3a's snapshot is not on this box")
        meta = json.loads(path.with_suffix(".json").read_text())
        genome = parse_genome(meta["genome_text"])
        org = Organism.load(path, genome)   # must NOT raise
        self.assertEqual(org._state_hash_legacy(), meta["state_hash"])


if __name__ == "__main__":
    unittest.main()
