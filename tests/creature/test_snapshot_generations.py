# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:52 +0400 — his 23:20 word, test-first (red on 867c55c). The days life's pre-flight
# (23:45) was killed INSIDE a snapshot: organism.* came from moment 5,700, ledger.json from 5,200, and every restart died on
# `KeyError: 5204` in build_ledgers — a snapshot torn by a kill ends a life for good. These pin the fix: a snapshot writes every file
# under a staged name first and renames them back to back, SNAPSHOT.json last; the complete generation before it is kept as hard links in
# state/prev/; a resume that finds the organism, the ledger and SNAPSHOT.json disagreeing restores prev/ (and the tape replays from its
# last_seq), and with no prev/ it moves the torn state aside and rebuilds from the whole tape. Every heal is recorded.
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from creature import repair as RP
from tests.creature import _scene_tape as S
from tests.creature.test_inherit_mind import N_TRAIN, lean_text


class Generations(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="snap-gen-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        # the uninterrupted life, the twin every healed life must end equal to
        cls.whole, _ = cls.live(cls.rows)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def new_root(cls):
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        (root.parent / "g.genome").write_text(lean_text())
        return root

    @classmethod
    def live(cls, rows, root=None):
        root = root or cls.new_root()
        m = MM.Mind(root.parent / "g.genome", root)
        try:
            for row in rows:
                m.consume(row)
        finally:
            m.close()
        return m, root

    def _resume_and_finish(self, root):
        m2, last = MM.Mind.resume(root.parent / "g.genome", root)
        try:
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        return m2

    def test_a_snapshot_writes_a_generation_and_keeps_the_last_complete_one(self):
        root = self.new_root()
        m = MM.Mind(root.parent / "g.genome", root)
        try:
            for row in self.rows[: len(self.rows) // 3]:
                m.consume(row)
            m.snapshot()
            t1 = m.org.t
            for row in self.rows[len(self.rows) // 3: 2 * len(self.rows) // 3]:
                m.consume(row)
            m.snapshot()
        finally:
            m.close()
        st = root / "state"
        gen = json.loads((st / "SNAPSHOT.json").read_text())
        self.assertEqual(gen["t"], json.loads((st / "ledger.json").read_text())["moments"])
        self.assertTrue((st / "prev" / "SNAPSHOT.json").exists())
        self.assertFalse(list(st.glob("*_tmp*")) + list(st.glob("*.staged")), "no staged file is left behind")
        self.assertIn("organism.npz", gen["files"])

    def test_a_kill_inside_the_renames_heals_from_prev_and_ends_equal_to_the_whole_life(self):
        root = self.new_root()
        m = MM.Mind(root.parent / "g.genome", root)
        k = len(self.rows) // 2
        for row in self.rows[:k]:
            m.consume(row)
        m.snapshot()                                   # generation A, complete
        for row in self.rows[k: k + 60]:
            m.consume(row)
        m._crash_after_renames = 1                     # generation B: the organism renamed, then the process «dies»
        with self.assertRaises(MM.SnapshotCrash):
            m.snapshot()
        st = root / "state"
        # the plant tore the snapshot, proved WITHOUT the production check: organism.npz is no longer the file generation A recorded
        # (only it was renamed; organism.json and the ledger still agree with each other, which is why a t-only check was blind)
        rec_a = json.loads((st / "SNAPSHOT.json").read_text())["prints"]["organism.npz"]
        s = (st / "organism.npz").stat()
        self.assertNotEqual([s.st_size, s.st_mtime_ns], rec_a, "the plant tore the snapshot")
        m2 = self._resume_and_finish(root)
        self.assertEqual(m2.snapshot_heal["kind"], "torn_snapshot")
        self.assertEqual(m2.snapshot_heal["restored"], "prev")
        self.assertEqual(m2.org.state_hash(), self.whole.org.state_hash())
        recs = [json.loads(l) for l in (root / RP.QDIR / RP.RECORD).read_text().splitlines()]
        self.assertEqual(recs[-1]["kind"], "torn_snapshot")

    def test_a_torn_first_snapshot_with_no_prev_rebuilds_from_the_whole_tape(self):
        root = self.new_root()
        m = MM.Mind(root.parent / "g.genome", root)
        for row in self.rows[: len(self.rows) // 2]:
            m.consume(row)
        m._crash_after_renames = 1
        with self.assertRaises(MM.SnapshotCrash):
            m.snapshot()
        m2, last = MM.Mind.resume(root.parent / "g.genome", root)
        try:
            self.assertEqual(last, 0, "nothing trusted: the whole tape replays")
            self.assertEqual(m2.snapshot_heal["restored"], "none: rebuilt from the tape")
            for row in self.rows:
                m2.consume(row)
        finally:
            m2.close()
        self.assertEqual(m2.org.state_hash(), self.whole.org.state_hash())
        self.assertTrue(any(p.name.startswith("state.torn.") for p in (root / RP.QDIR).iterdir()))

    def test_a_whole_state_resumes_as_before(self):
        root = self.new_root()
        m = MM.Mind(root.parent / "g.genome", root)
        for row in self.rows[: len(self.rows) // 2]:
            m.consume(row)
        m.close()
        m2 = self._resume_and_finish(root)
        self.assertIsNone(m2.snapshot_heal)
        self.assertEqual(m2.org.state_hash(), self.whole.org.state_hash())


if __name__ == "__main__":
    unittest.main()
