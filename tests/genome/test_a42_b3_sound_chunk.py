# edit: Claude (Sonnet 5, ALPHA4-2 builder B3), 2026-09-23 17:1x +0400 — A42-B3 task 1 (docs/ALPHA4-2-PREREG.md §2 G7,
# §2.6): the sound-axis chunk law. Both sound meetings (`sight-sound`, `sound-words`) grow along their SOUND axis in
# chunks of SOUND_GROW_CHUNK=64 instead of the general GROW_CHUNK=2048 (the sight/words axis of each pair is
# untouched). Proven here with a from-scratch toy (never a Mind/tape): two Organisms fed the IDENTICAL deterministic
# stream of >128 distinct novel sounds -- one under the real SOUND_GROW_CHUNK=64, one with it patched to 2048 (the
# pre-task law, everything grows by the same constant) -- assert every state_hash()/row_hash() in the stream is
# IDENTICAL between the two arms (a chunk size is never semantic state; genome/machinery.py's state_hash/
# genome/witness.py's sparse digest both slice a pair's live block by `.a.n`/`.b.n`, never by `.W.shape`) while the
# two arms' SHAPES visibly diverge starting at cell 64 -- the positive control that this harness CAN see a
# difference when one really exists, so the hash-equality above is not vacuous. A one-ulp plant on a MASKED live
# coordinate (never padding -- #91's rule: a plant that lands where nothing reads it proves nothing) must move
# both digests. Two Organisms are run to completion SEPARATELY (never interleaved patches of the same global).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import machinery
from genome.machinery import Organism, parse_genome
from genome.witness import scratch_digest

from .test_a4l_voice_machinery import BASE, SOUND, S_DIM, W_DIM, SND_DIM, unit

HASH_LINE = "HASH     sparse; dense at snapshot"
N_MOMENTS = 200     # > 3 * SOUND_GROW_CHUNK(64): crosses the 64 AND 128 boundaries, reaches into the 192-256 chunk


def genome_text(budget: int = 5000, hash_: bool = False) -> str:
    t = BASE.replace("BUDGET 400", f"BUDGET {budget}").replace("NMAX 200\n", "GROW unbounded\n") + SOUND
    return t + (HASH_LINE + "\n" if hash_ else "")


def _run_stream(seed: int, n: int, sound_chunk_value: int, hash_: bool = False):
    """Feeds a deterministic stream of n moments (fresh novel sight AND sound every moment, ONE fixed word so the
    words axis of `sound-words` never grows past its first chunk -- the sound axis is the whole point) to a FRESH
    Organism built with `machinery.SOUND_GROW_CHUNK` pinned to `sound_chunk_value` for this run's entire duration
    (patched, run to completion, restored -- never interleaved with another arm's run). Returns
    (org, [(state_hash, row_hash, ss.W.shape, sw.W.shape), ...] per moment)."""
    old = machinery.SOUND_GROW_CHUNK
    machinery.SOUND_GROW_CHUNK = sound_chunk_value
    try:
        org = Organism(parse_genome(genome_text(hash_=hash_)))
        rng = np.random.default_rng(seed)
        xw = unit(rng, W_DIM)     # FIXED once (test_sound_area_and_pairs_grow's own pattern): budget goes to sight+sound
        trace = []
        for _ in range(n):
            xs = unit(rng, S_DIM); xsnd = unit(rng, SND_DIM)
            org.moment(xs, xw, x_snd=xsnd)
            ss = org.sound_meets["sight-sound"]; sw = org.sound_meets["sound-words"]
            trace.append((org.state_hash(), org.row_hash(), ss.W.shape, sw.W.shape))
        return org, trace
    finally:
        machinery.SOUND_GROW_CHUNK = old


class TestSoundAxisChunkIsHashNeutral(unittest.TestCase):
    def test_dense_hash_identical_across_chunk_sizes_shapes_diverge(self) -> None:
        org_a, trace_a = _run_stream(seed=11, n=N_MOMENTS, sound_chunk_value=64)     # the real law (task 1)
        org_b, trace_b = _run_stream(seed=11, n=N_MOMENTS, sound_chunk_value=2048)   # the pre-task law, reproduced
        self.assertEqual(org_a.sound.n, N_MOMENTS, "positive control: every moment bred a novel sound cell")
        self.assertEqual(org_a.sound.n, org_b.sound.n, "same stream: same number of sound cells born in both arms")
        hashes_a = [t[0] for t in trace_a]; hashes_b = [t[0] for t in trace_b]
        self.assertEqual(hashes_a, hashes_b, "state_hash() at every one of 200 moments: chunk size 64 vs 2048 -- identical")
        shapes_ss_a = [t[2] for t in trace_a]; shapes_ss_b = [t[2] for t in trace_b]
        self.assertNotEqual(shapes_ss_a, shapes_ss_b,
                             "positive control: the shapes DO differ between arms -- the hash-equality above is not vacuous")
        ss_a, sw_a = org_a.sound_meets["sight-sound"], org_a.sound_meets["sound-words"]
        self.assertEqual(ss_a.W.shape[1] % machinery.SOUND_GROW_CHUNK, 0, "sight<->sound's SOUND axis is a multiple of 64")
        self.assertEqual(sw_a.W.shape[0] % machinery.SOUND_GROW_CHUNK, 0, "sound<->words' SOUND axis is a multiple of 64")
        self.assertEqual(ss_a.W.shape[0] % machinery.GROW_CHUNK, 0, "sight<->sound's SIGHT axis is a multiple of 2048 (untouched)")
        self.assertEqual(sw_a.W.shape[1] % machinery.GROW_CHUNK, 0, "sound<->words' WORDS axis is a multiple of 2048 (untouched)")
        self.assertGreater(ss_a.W.shape[1], 128, "crossed the 64 AND 128 boundaries (>3 chunks of 64)")
        ss_b = org_b.sound_meets["sight-sound"]
        self.assertEqual(ss_b.W.shape[1], 2048, "the 2048 arm never grows past its own first (and only) chunk at 200 cells")

    def test_sparse_row_hash_identical_across_chunk_sizes(self) -> None:
        """The same comparison under HASH sparse (genome/witness.py): the incremental witness's digest is ALSO
        chunk-size independent (it gathers live blocks by `.a.n`/`.b.n`, never `.W.shape` -- confirmed by reading
        genome/witness.py before writing this test), and each arm's row_hash() == a from-scratch scratch_digest()
        at the end (the running witness never drifted while chunk sizes differed)."""
        n = 80        # crosses ONE boundary (64) -- enough to prove the sparse witness sees the same law; the dense
                      # test above already proves the multi-boundary case exhaustively
        org_a, trace_a = _run_stream(seed=23, n=n, sound_chunk_value=64, hash_=True)
        org_b, trace_b = _run_stream(seed=23, n=n, sound_chunk_value=2048, hash_=True)
        self.assertEqual(org_a.hash_form, "sparse"); self.assertEqual(org_b.hash_form, "sparse")
        rows_a = [t[1] for t in trace_a]; rows_b = [t[1] for t in trace_b]
        self.assertEqual(rows_a, rows_b, "row_hash() (sparse) at every moment: chunk size 64 vs 2048 -- identical")
        self.assertEqual(org_a.row_hash(), scratch_digest(org_a), "the running sparse witness == a from-scratch recompute (arm A)")
        self.assertEqual(org_b.row_hash(), scratch_digest(org_b), "the running sparse witness == a from-scratch recompute (arm B)")
        shapes_a = [t[2] for t in trace_a]; shapes_b = [t[2] for t in trace_b]
        self.assertNotEqual(shapes_a, shapes_b, "positive control: shapes diverge here too")

    def test_one_ulp_plant_on_a_masked_live_coordinate_moves_both_digests(self) -> None:
        """#91's rule: a plant that lands where nothing reads it proves nothing. `ss.W[shape-1, shape-1]` (an
        existing test's OWN plant, test_a4l_seam5_witness_sound.py:311) sits in PADDING once cells are few -- the
        witness's own docstring says it gathers only at MASKED coordinates, so an unmasked plant would report
        'the digest is insensitive' for the wrong reason (nothing is there to see) rather than confirm sensitivity.
        This plant is at a coordinate `ss.mask` itself says is live."""
        org, _trace = _run_stream(seed=37, n=N_MOMENTS, sound_chunk_value=64, hash_=True)
        ss = org.sound_meets["sight-sound"]
        live = ss.mask[: org.sight.n, : org.sound.n]
        self.assertTrue(live.any(), "positive control: sight<->sound has at least one masked (live) edge to plant on")
        rs, cs = np.nonzero(live); r, c = int(rs[0]), int(cs[0])   # the first masked (live) coordinate
        self.assertEqual(ss.mask[r, c], 1, "the chosen coordinate really is live")
        before_dense, before_sparse = org.state_hash(), org.row_hash()
        old_val = float(ss.W[r, c])
        ss.W[r, c] = np.nextafter(old_val, old_val + 1.0)
        self.assertNotEqual(float(ss.W[r, c]), old_val, "the ulp nudge actually changed the float64 bit pattern")
        after_dense, after_sparse = org.state_hash(), org.row_hash()
        self.assertNotEqual(before_dense, after_dense, "a one-ulp change at a LIVE coordinate must move the dense digest")
        self.assertNotEqual(before_sparse, after_sparse, "...and the sparse digest too (it re-gathers VALUES fresh on every call)")


class TestLoadAsymmetryMissingMeetingCaughtByDigest(unittest.TestCase):
    """genome/machinery.py's Organism.load() re-grows the sight/words axes of every sound pair to cover loaded
    live cells (a migration safety net for a meeting whose own pair_*_W data was absent from the snapshot) but,
    before this task, never re-grew the SOUND axis the same way (the hand-back plan's own flagged asymmetry,
    ~line 2393). Tested here rather than assumed: the only way to REACH the gap -- a meeting declared at LOAD
    time but not at SAVE time, with sound.n > 0 -- changes state_hash()'s own `sound_meets` iteration and is
    refused by load()'s digest-mismatch gate before the gap ever matters. `o.sound` is added to the re-grow
    tuple anyway: one hash-neutral token (state_hash()/the sparse witness both slice a pair's live block by
    `.a.n`/`.b.n`, never `.W.shape` -- read in both before this was written), defensive against a future change
    that might decouple 'which meetings are declared' from the digest."""

    def test_a_meeting_declared_only_at_load_time_is_refused_by_the_digest_not_silently_undersized(self) -> None:
        text1 = (BASE.replace("BUDGET 400", "BUDGET 5000").replace("NMAX 200\n", "GROW unbounded\n")
                 + "AREA sound from cochlea cos>=0.975\n")          # AREA_SOUND declared, NO MEET lines
        org1 = Organism(parse_genome(text1))
        rng = np.random.default_rng(41)
        xw = unit(rng, W_DIM)
        n = machinery.SOUND_GROW_CHUNK + 30          # past ONE chunk of the fresh pair a load would construct
        for _ in range(n):
            org1.moment(unit(rng, S_DIM), xw, x_snd=unit(rng, SND_DIM))
        self.assertEqual(org1.sound.n, n)
        self.assertEqual(org1.sound_meets, {}, "positive control: no meeting object exists to save")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "o1"
            org1.save(path)
            text2 = BASE.replace("BUDGET 400", "BUDGET 5000").replace("NMAX 200\n", "GROW unbounded\n") + SOUND  # + both MEETs
            g2 = parse_genome(text2)
            with self.assertRaises(machinery.GenomeError) as ctx:
                Organism.load(path, g2)
            self.assertIn("state_hash", str(ctx.exception), "refused by the digest-mismatch gate, not a silent undersized load")

    def test_the_defensive_sound_regrow_is_hash_neutral_on_a_normal_matching_round_trip(self) -> None:
        """The `o.sound` line's own positive control: a NORMAL save/load (same declared meetings both sides,
        past the sound chunk boundary) is untouched by adding it -- state_hash() before save == after load,
        exactly as test_a4l_voice_machinery.py's own test_sound_area_and_pairs_grow already pins, reproduced
        here at SOUND_GROW_CHUNK's real value (64) rather than a patched GROW_CHUNK."""
        org, _trace = _run_stream(seed=53, n=N_MOMENTS, sound_chunk_value=64)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "o"
            before = org.state_hash()
            org.save(path)
            back = Organism.load(path, parse_genome(genome_text()))
            self.assertEqual(back.state_hash(), before)
            self.assertEqual(back.sound.n, org.sound.n)
            ss_back = back.sound_meets["sight-sound"]
            self.assertGreaterEqual(ss_back.W.shape[1], back.sound.n, "the sound axis covers every loaded cell")


if __name__ == "__main__":
    unittest.main()
