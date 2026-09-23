# edit: Claude (Opus 5.5, A4 seam-5 builder), 2026-09-23 15:03 +0400 — SEAM 5 (docs/ALPHA4-2-PREREG.md §7.2 on a42: COST x VOICE), at the MIND:
# the rung genome A4L-VOICE.genome + the HASH line, on a voiced tape made by the maker's own publish road (creature/world_maker.py), against
# its dense twin (the same genome without HASH) on the same rows. The seams the genome-level tests cannot reach: the mind's five hashed
# row kinds (the canvas row carrying a bound sound, the coarse row, the sleep row whose cycle() merges cells that sit on sound meetings),
# GROW crossing capacity in the sound area and both meetings, the threaded think (its shadow carries no witness), snapshot/resume.
"""test_a4l_seam5_witness_sound_seams.py — HASH sparse x VOICE at the mind: every hashed row is the witness, == a from-scratch recompute."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from creature.mind import Mind
from genome import machinery, world
from genome.machinery import Organism, parse_genome
from genome.sleep import cycle
from genome.witness import SparseWitness, scratch_digest, sound_invariant_violations

from .test_a4l_voice_seams import _journal, _voiced_rows

ROOT = Path(__file__).resolve().parents[2]
HASH_LINE = "HASH     sparse; dense at snapshot"
ZERO = {"W_nonzero_mask0": 0, "strikes_nonzero_mask0": 0, "padding_nonzero": 0}


class _VoicedHashLives:
    """ONE voiced tape (the sixteen things + the plant, three canvases each) lived twice: under A4L-VOICE.genome + HASH (sparse) and under
    A4L-VOICE.genome (dense), SLEEP every 100 moments so a sleep row (and its cycle()) lands inside the tape, the area capacities shrunk so
    the sound area and both meetings grow mid-life (A4L-VOICE's own seam does the same). Every row_hash call on the sparse life records its
    return, a from-scratch recompute, the dense digest beside it and the organism it ran on."""
    _built = None

    @classmethod
    def get(cls):
        if cls._built is not None:
            return cls._built
        d = Path(tempfile.mkdtemp(prefix="seam5-mind-"))
        text = (ROOT / "genome" / "ladder" / "A4L-VOICE.genome").read_text()
        assert "SLEEP    every 2500 moments" in text
        text = text.replace("SLEEP    every 2500 moments", "SLEEP    every 100 moments")
        g_dense = d / "voice-dense.genome"; g_dense.write_text(text)
        g_sparse = d / "voice-hash.genome"; g_sparse.write_text(text + "\n" + HASH_LINE + "\n")
        # edit: Claude (Sonnet 5, ALPHA4-2 builder B3), 2026-09-23 17:1x +0400 — A42-B3 task 1: SOUND_GROW_CHUNK patched down
        # alongside the other two, else the sound axis of each pair starts at the real 64 regardless of this patch and the
        # "positive control: ... grew on its sound axis" assert below (this class's own docstring: "the sound pairs grow by
        # chunks") would clear `> 8` with zero growth -- a vacuous control.
        old = (machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK)
        machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = 4, 8, 8
        orig_row = Organism.row_hash
        orig_digest = SparseWitness.digest
        rec = {"sparse": [], "dense": [], "digest_on": []}

        def row(self_):
            h = orig_row(self_)
            if self_.hash_form == "sparse":
                rec["sparse"].append((h, scratch_digest(self_), self_.state_hash(), id(self_)))
            else:
                rec["dense"].append(h)
            return h

        def digest(w, org):
            rec["digest_on"].append(id(org)); return orig_digest(w, org)

        Organism.row_hash = row; SparseWitness.digest = digest
        try:
            things = list(world.THINGS_11) + list(world.THINGS_ARRIVAL2) + [world.THING_PLANT]
            root_d = d / "dense"; root_d.mkdir()
            rows = _voiced_rows(root_d, things, 3)
            root_s = d / "sparse"; (root_s / "tape").mkdir(parents=True)
            (root_s / "tape" / "payload").symlink_to(root_d / "tape" / "payload")
            m_s = Mind(g_sparse, root_s)
            for r in rows:
                m_s.consume(r)
            m_s.snapshot()
            before = (orig_row(m_s.org), m_s.org.state_hash(), int(m_s.org.sound.n))
            m_s.close()
            m_d = Mind(g_dense, root_d)
            for r in rows:
                m_d.consume(r)
            m_d.close()
        finally:
            Organism.row_hash = orig_row; SparseWitness.digest = orig_digest
            machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = old
        cls._built = dict(d=d, g_sparse=g_sparse, g_dense=g_dense, root_s=root_s, root_d=root_d, rows=rows, m_s=m_s, m_d=m_d,
                          rec=rec, before=before, things=things)
        return cls._built


class VoicedMindUnderHash(unittest.TestCase):
    def test_journals_identical_except_hash_and_every_hashed_row_is_the_witness(self) -> None:
        L = _VoicedHashLives.get()
        js, jd = _journal(L["root_s"]), _journal(L["root_d"])
        mind_rows = lambda js_: [j for j in js_ if j.get("event") not in ("start", "sense_restart", "snapshot", "stop", "exam")]
        js, jd = mind_rows(js), mind_rows(jd)
        self.assertEqual(len(js), len(jd))
        for a, b in zip(jd, js):
            self.assertEqual({k: v for k, v in a.items() if k != "hash"}, {k: v for k, v in b.items() if k != "hash"})
            if "hash" in a:
                self.assertNotEqual(a["hash"], b["hash"], "the sparse witness is domain-separated from the dense digest")
        hashed_s = [j["hash"] for j in js if "hash" in j]
        hashed_d = [j["hash"] for j in jd if "hash" in j]
        rec = L["rec"]
        self.assertGreater(sum(1 for j in js if "sound" in j and isinstance(j["sound"], dict) and "winners" in j["sound"]), 0,
                           "positive control: canvases carried a bound sound")
        self.assertTrue(any("sleep" in j for j in js), "positive control: a sleep row (its cycle()) is inside the tape")
        self.assertTrue(any(j.get("act") == "coarse" for j in js), "positive control: coarse rows")
        sparse_returns = [x[0] for x in rec["sparse"]]
        self.assertEqual(hashed_s, sparse_returns[:len(hashed_s)], "every hashed row carries the witness's own return, in order")
        self.assertEqual([x[0] for x in rec["sparse"] if x[0] != x[1]], [], "the running witness == a from-scratch recompute at EVERY row hash")
        self.assertEqual([x[2] for x in rec["sparse"]][:len(hashed_d)], hashed_d,
                         "the dense digest beside every sparse row == the dense twin's row: the two lives hold the same state row for row")
        self.assertEqual(set(rec["digest_on"]), {id(L["m_s"].org)}, "every sparse digest was the LIVE organism's (never a think shadow)")

    def test_the_sound_area_and_both_meetings_grew_and_the_invariant_holds(self) -> None:
        L = _VoicedHashLives.get()
        org = L["m_s"].org
        self.assertEqual(org.sound.n, len(L["things"]))
        self.assertGreater(org.sound.nmax, 4, "positive control: the sound area crossed its (shrunk) capacity")
        for name, p in org.sound_meets.items():
            with self.subTest(meeting=name):
                self.assertGreater(int(p.mask[:p.a.n, :p.b.n].sum()), 0, "the meeting holds edges")
        self.assertGreater(org.sound_meets["sight-sound"].W.shape[1], 8, "positive control: sight<->sound grew on its sound axis")
        self.assertEqual(sound_invariant_violations(org), {"sight-sound": ZERO, "sound-words": ZERO})

    def test_snapshot_keeps_the_dense_digest_and_resume_restores_the_sparse_row_hash(self) -> None:
        L = _VoicedHashLives.get()
        sparse_before, dense_before, n_before = L["before"]
        meta = json.loads((L["root_s"] / "state" / "organism.json").read_text())
        meta_d = json.loads((L["root_d"] / "state" / "organism.json").read_text())
        self.assertEqual(meta["state_hash"], meta_d["state_hash"], "dense at snapshot: the sparse life's snapshot carries the dense twin's digest")
        old = (machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK)
        machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = 4, 8, 8
        try:
            resumed, _last = Mind.resume(L["g_sparse"], L["root_s"])
        finally:
            machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK, machinery.SOUND_GROW_CHUNK = old
        self.assertEqual(resumed.org.hash_form, "sparse")
        self.assertEqual(int(resumed.org.sound.n), n_before)
        self.assertEqual(resumed.org.state_hash(), meta["state_hash"])
        self.assertEqual(resumed.org.row_hash(), scratch_digest(resumed.org))
        resumed.close()


class ThePlantOnTheLivedOrganism(unittest.TestCase):
    """The designer's RED at the mind's own organism (ALPHA4-2-PREREG §7.2 seam 5): after the voiced life, one masked W value of EACH sound
    meeting's live block moved by one ulp moves the ROW hash (the dense digest moves too — the precondition); restored, both come back."""

    def test_a_one_ulp_plant_in_each_meeting_moves_the_row_hash(self) -> None:
        org = _VoicedHashLives.get()["m_s"].org
        for name, p in sorted(org.sound_meets.items()):
            with self.subTest(meeting=name):
                r, c = [int(v[0]) for v in np.nonzero(p.mask[:p.a.n, :p.b.n])]
                s0, d0, w0 = org.row_hash(), org.state_hash(), float(p.W[r, c])
                p.W[r, c] = np.nextafter(w0, np.inf)
                self.assertNotEqual(org.state_hash(), d0, "precondition: the dense digest sees the plant")
                self.assertNotEqual(org.row_hash(), s0, "the row hash (the sparse witness) sees the plant")
                p.W[r, c] = w0
                self.assertEqual((org.row_hash(), org.state_hash()), (s0, d0))


class CycleTimesHashTimesVoice(unittest.TestCase):
    """genome/sleep.py:cycle() on a VOICED organism: its merge pass merges sight/word cells whose sound-meeting edges must follow them
    (`_merge_pair_edges`, marked per meeting) — the sparse witness == its from-scratch recompute after the cycle."""

    def test_the_cycle_moves_meeting_edges_and_the_witness_follows(self) -> None:
        from tests.genome.test_a4l_seam5_witness_sound import VREGIME_A, voiced_life
        org = voiced_life(VREGIME_A, hash_=True, grow=True, moments=700)
        self.assertEqual(org.row_hash(), scratch_digest(org))
        masks = {k: p.mask.copy() for k, p in org.sound_meets.items()}
        merged0 = org.c["cells_merged_sight"] + org.c["cells_merged_words"]
        self.assertTrue(cycle(org), "positive control: the cycle fired")
        self.assertGreater(org.c["cells_merged_sight"] + org.c["cells_merged_words"], merged0, "positive control: the cycle merged cells")
        moved = [k for k, p in org.sound_meets.items() if p.mask.shape != masks[k].shape or not np.array_equal(p.mask, masks[k])]
        self.assertTrue(moved, "positive control: a merged cell's sound-meeting edges moved")
        self.assertEqual(org.row_hash(), scratch_digest(org), "the sparse witness after cycle() equals its from-scratch recompute")


def tearDownModule() -> None:
    L = _VoicedHashLives._built
    if L is not None:
        shutil.rmtree(L["d"], True)


if __name__ == "__main__":
    unittest.main()
