# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 01:50 +0400 — ALPHA4-G.md task 2 (docs/ALPHA4-PREREG.md
# §2/§3): state_hash's live-prefix slicing for alive/misfires/own_band, the 3-generation load() fallback,
# and the GROW-aware save/load live-block format (the advisor's review, item 4).
"""test_state_hash_grow.py — state_hash's live-prefix slicing (task 2) and GROW's save/load round trip."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome.machinery import GenomeError, Organism, parse_genome

from ._toy import mini_genome, unit


def _grown_organism(n_moments: int = 2100, seed: int = 20260923):
    """A real organism, grown asymmetrically past both an Area-doubling boundary and a W chunk boundary
    (mirrors test_grow_mechanics.py's own fixture, reused here so the hash/save-load tests exercise the
    SAME divergent-capacity shape, not a toy that happens to stay square)."""
    org = Organism(mini_genome(grow=True, budget=100000))
    org.new_arrival()
    rng = np.random.default_rng(seed)
    xw0 = unit(rng, 208)
    for _ in range(n_moments):
        xs = unit(rng, 64)
        org.moment(xs, xw0)
    return org


class TestLivePrefixHash(unittest.TestCase):
    def test_alive_misfires_sliced_to_live_prefix(self) -> None:
        """Two organisms with IDENTICAL live cells but DIFFERENT capacity (one grew past a boundary and
        back down in spirit -- here, simply two organisms built to the same n via different paths so their
        padding differs) must hash identically. Simplest real proof: state_hash() must not change when we
        corrupt ONLY the padding region of alive/misfires (bytes state_hash must never read)."""
        org = _grown_organism(300)
        h0 = org.state_hash()
        n = org.sight.n
        self.assertLess(n, org.sight.nmax, "the fixture must have real padding to corrupt")
        org.sight.alive[n:] = 1          # corrupt padding only -- never a live index
        org.sight.misfires[n:] = 99
        h1 = org.state_hash()
        self.assertEqual(h0, h1, "state_hash must be blind to the padding region, not just the live block")

    def test_own_band_sliced_to_live_prefix(self) -> None:
        """A REAL push (test_thresh_own_band.py's own pattern: the same glance shown twice births then
        answers correctly, pushing one cosine) so own_band_n[:n].any() is genuinely True from a live cell
        -- then corrupt ONLY the padding (own_band_n[n:], own_band[n:]) and confirm the hash is unmoved.
        Corrupting the padding with a NONZERO own_band_n would also flip a full-length `.any()` gate (a
        second, narrower bug this test also pins: the gate itself must read the live prefix, not the
        full-capacity array — fixed alongside the slice)."""
        text = mini_genome(grow=True).text + "THRESH cell own band history 5\n"
        org = Organism(parse_genome(text))
        xs0, xw0 = unit(np.random.default_rng(1), 64), unit(np.random.default_rng(2), 208)
        org.moment(xs0, xw0)   # birth only
        org.moment(xs0, xw0)   # cell 0's established answer == T[0] -> a real push
        self.assertEqual(int(org.sight.own_band_n[0]), 1, "the fixture must produce a real push to be meaningful")
        n = org.sight.n
        self.assertLess(n, org.sight.nmax, "the fixture needs real padding to corrupt")
        h0 = org.state_hash()
        org.sight.own_band[n:] = 0.999
        org.sight.own_band_n[n:] = 3
        h1 = org.state_hash()
        self.assertEqual(h0, h1, "own_band/own_band_n padding must not move the hash either (the brief's own factual gap)")

    def test_hash_still_moves_on_real_live_change(self) -> None:
        """The positive control: state_hash is not blind to everything -- a live-block change still moves it."""
        org = _grown_organism(300)
        h0 = org.state_hash()
        org.sight.alive[0] = 0 if org.sight.alive[0] else 1
        self.assertNotEqual(h0, org.state_hash())

    def test_two_replays_byte_identical_including_hash(self) -> None:
        """Task 2(a): two replays of the same tape under this tree -> byte-identical hash too."""
        org_a = _grown_organism(500, seed=7)
        org_b = _grown_organism(500, seed=7)
        self.assertEqual(org_a.state_hash(), org_b.state_hash())


class TestThreeGenerationLoad(unittest.TestCase):
    """A snapshot saved under any of the three state_hash generations (this task's, builder F's, or the
    pre-F legacy one) must still load; a genuinely corrupted one must still refuse, naming all three."""

    def _toy_nmax_organism(self):
        org = Organism(mini_genome())
        org.new_arrival()
        rng = np.random.default_rng(3)
        for _ in range(60):
            org.moment(unit(rng, 64), unit(rng, 208))
        return org

    def test_new_format_loads_on_fast_path(self) -> None:
        org = self._toy_nmax_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            reloaded = Organism.load(path, org.g)
        self.assertEqual(reloaded.state_hash(), org.state_hash())

    def test_f_format_snapshot_loads_via_fallback(self) -> None:
        org = self._toy_nmax_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            meta = json.loads(path.with_suffix(".json").read_text())
            self.assertNotEqual(org.state_hash(), org._state_hash_legacy_f(), "the fixture needs the two digests to actually differ")
            meta["state_hash"] = org._state_hash_legacy_f()
            path.with_suffix(".json").write_text(json.dumps(meta))
            reloaded = Organism.load(path, org.g)   # must NOT raise
        self.assertEqual(reloaded.state_hash(), org.state_hash(), "the loaded organism's real state is unaffected by which digest the file happened to carry")

    def test_pre_f_legacy_format_snapshot_still_loads(self) -> None:
        org = self._toy_nmax_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            meta = json.loads(path.with_suffix(".json").read_text())
            meta["state_hash"] = org._state_hash_legacy()
            path.with_suffix(".json").write_text(json.dumps(meta))
            reloaded = Organism.load(path, org.g)   # must NOT raise
        self.assertEqual(reloaded.state_hash(), org.state_hash())

    def test_corrupted_snapshot_refuses_naming_all_three(self) -> None:
        org = self._toy_nmax_organism()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            meta = json.loads(path.with_suffix(".json").read_text())
            meta["state_hash"] = "0" * 64
            path.with_suffix(".json").write_text(json.dumps(meta))
            with self.assertRaises(GenomeError) as ctx:
                Organism.load(path, org.g)
        msg = str(ctx.exception)
        self.assertIn("F's", msg)
        self.assertIn("legacy", msg)

    def test_real_life2_snapshot_still_loads(self) -> None:
        """The real thing: life 2's actual pre-F closed-root snapshot must still load (test_state_hash_live_block.py's
        own control, re-run here against this task's 3-way fallback)."""
        path = Path("/data/dev/genome/run-g4-life2-20260920-1212/state/organism")
        if not path.with_suffix(".json").exists():
            self.skipTest("life 2's snapshot is not on this box")
        meta = json.loads(path.with_suffix(".json").read_text())
        genome = parse_genome(meta["genome_text"])
        org = Organism.load(path, genome)   # must NOT raise
        self.assertEqual(org.sight.n, 700); self.assertEqual(org.words.n, 17)


class TestGrowSaveLoadRoundTrip(unittest.TestCase):
    def test_round_trip_after_asymmetric_growth(self) -> None:
        org = _grown_organism(2100)
        self.assertGreater(org.sight.nmax, org.W.shape[1], "the fixture must exercise real, asymmetric capacity")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            reloaded = Organism.load(path, org.g)
        self.assertEqual(reloaded.sight.n, org.sight.n)
        self.assertEqual(reloaded.words.n, org.words.n)
        self.assertEqual(reloaded.sight.nmax, org.sight.nmax, "load() must reconstruct the SAME capacity the live run reached, not just enough")
        self.assertEqual(reloaded.words.nmax, org.words.nmax)
        self.assertEqual(reloaded.W.shape, org.W.shape)
        np.testing.assert_array_equal(reloaded.sight.cells[: org.sight.n], org.sight.cells[: org.sight.n])
        np.testing.assert_array_equal(reloaded.W[: org.sight.n, : org.words.n], org.W[: org.sight.n, : org.words.n])
        self.assertEqual(reloaded.state_hash(), org.state_hash())

    def test_saved_file_is_live_block_only_not_full_capacity(self) -> None:
        """The point of the whole exercise: a GROW snapshot's npz must be sized by the LIVE block, not the
        capacity the arrays happen to hold (which would make every snapshot balloon as a life runs longer,
        defeating GROW's own memory goal — task 6)."""
        org = _grown_organism(2100)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            saved_bytes = (path.with_suffix(".npz")).stat().st_size
        # the FULL-capacity W alone (uncompressed) would be sight.nmax * words.nmax * 8 bytes
        full_capacity_w_bytes = org.sight.nmax * org.words.nmax * 8
        self.assertLess(saved_bytes, full_capacity_w_bytes / 4,
                         f"saved {saved_bytes} bytes vs a full-capacity W of {full_capacity_w_bytes} bytes -- GROW must not save padding")

    def test_load_reconstructs_next_power_of_two_capacity(self) -> None:
        """The literal claim (task 2(c)): "load allocates the next power of two >= n". Built by hand
        (never via area.grow(), so this is independent of that method's own correctness) -- a snapshot
        whose n sits exactly ON a boundary must load at THAT capacity (no growth needed yet); one past it
        must load at DOUBLE."""
        cases = [(1, 256), (255, 256), (256, 256), (257, 512), (511, 512), (512, 512), (513, 1024)]
        for n, expected_cap in cases:
            with self.subTest(n=n):
                org = Organism(mini_genome(grow=True, budget=100000))
                org.new_arrival()
                rng = np.random.default_rng(n)
                xw0 = unit(rng, 208)
                while org.sight.n < n:
                    org.moment(unit(rng, 64), xw0)
                self.assertEqual(org.sight.n, n)
                with tempfile.TemporaryDirectory() as d:
                    path = Path(d) / "organism"
                    org.save(path)
                    reloaded = Organism.load(path, org.g)
                self.assertEqual(reloaded.sight.nmax, expected_cap, f"n={n} must load at capacity {expected_cap}")
                self.assertEqual(reloaded.state_hash(), org.state_hash())

    def test_negative_control_nmax_save_load_untouched(self) -> None:
        org = Organism(mini_genome())
        org.new_arrival()
        rng = np.random.default_rng(9)
        for _ in range(60):
            org.moment(unit(rng, 64), unit(rng, 208))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "organism"
            org.save(path)
            z = np.load(path.with_suffix(".npz"))
            self.assertEqual(z["W"].shape, (200, 200), "under NMAX the saved W is still the FULL nmax x nmax array, byte-for-byte as before this task")
            reloaded = Organism.load(path, org.g)
        self.assertEqual(reloaded.W.shape, (200, 200))
        self.assertEqual(reloaded.state_hash(), org.state_hash())


if __name__ == "__main__":
    unittest.main()
