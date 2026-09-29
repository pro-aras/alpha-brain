# edit: Claude (Opus 5.5, the seat), 2026-09-30 00:02 +0400 — his 23:20 word («add all these features today so it runs for few days»),
# test-first (red on d96c25e: the mind has no web). THE KNOWLEDGE WEB and THE SELF inside a living mind, as BOOKKEEPING: every heard word
# grows two webs (L, and N the steered sprouts; beta 10 edges a word; the spent consolidation test); the brain's own turns and learns
# feed the self node and its placed claims; both are saved in the snapshot and restored at a resume; nothing is journaled, so a
# life's journal is the one it was; an error inside them switches them off and is shown, never crashes the mind.
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from genome import web as Wb
from tests.creature import _scene_tape as S
from tests.creature.test_census_mind import LIVED_JOURNAL_SHA, LIVED_JOURNAL_ROWS
from tests.creature.test_inherit_mind import N_TRAIN, lean_text

REPO = Path(__file__).resolve().parents[2]


def ear_words(rows):
    return [str((r.get("meta") or {}).get("word")) for r in rows if r["sense"] == "ear" and (r.get("meta") or {}).get("word")]


class WebInTheMind(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="web-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.m, cls.root = cls.live(lean_text())

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def new_root(cls):
        cls.n += 1
        return S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")

    @classmethod
    def live(cls, text, rows=None, root=None):
        root = root or cls.new_root()
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root

    def test_the_minds_webs_equal_webs_fed_the_same_heard_words(self):
        self.assertEqual(sorted(self.m.webs), ["L", "N"])
        for rule, w in self.m.webs.items():
            twin = Wb.Web(rule, beta=MM.WEB_BETA, seed=self.m.genome.seed, spend="harmonic", reach=MM.WEB_REACH, author=self.root.name)
            for x in ear_words(self.rows):
                twin.hear(x)
            self.assertEqual(w.dumps(), twin.dumps(), rule)
            self.assertGreater(len(w.nodes), 5)

    def test_the_journal_is_the_one_it_was(self):
        J = S.journal(self.root)
        self.assertEqual(len(J), LIVED_JOURNAL_ROWS)
        self.assertEqual(hashlib.sha256(S.journal_bytes(self.root)).hexdigest(), LIVED_JOURNAL_SHA)

    def test_the_self_node_hears_the_brains_own_record(self):
        node = self.m.self_node
        learns = [r for r in S.journal(self.root) if r.get("kind") == "brain" and r.get("act") == "learn"]
        self.assertEqual(node.lived["canvases"], len(learns))
        self.assertEqual(node.claims["T1"].confirmed + node.claims["T1"].contradicted, len(learns))
        self.assertEqual(sorted(node.claims), ["B1", "F1", "F2", "T1", "T2", "T3"])
        self.assertEqual(node.claims["F2"].source, "implanted-knowledge")

    def test_the_snapshot_holds_them_and_a_resume_goes_on_identically(self):
        k = len(self.rows) // 2
        root = self.new_root()
        gp = root.parent / "g.genome"
        gp.write_text(lean_text())
        m = MM.Mind(gp, root)
        try:
            for row in self.rows[:k]:
                m.consume(row)
            m.snapshot()
            last = m.last_seq
        finally:
            m.close()
        self.assertTrue((root / "state" / "web.json").exists())
        m2, _ = MM.Mind.resume(gp, root)
        try:
            self.assertTrue(m2.web_restored)
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        for rule in ("L", "N"):
            self.assertEqual(m2.webs[rule].dumps(), self.m.webs[rule].dumps(), rule)
        self.assertEqual(json.dumps(m2.self_node.to_dict(), sort_keys=True), json.dumps(self.m.self_node.to_dict(), sort_keys=True))

    def test_status_carries_the_web_without_walking_it(self):
        st = self.m.brain_status()
        self.assertEqual(st["web"]["L"]["nodes"], len(self.m.webs["L"].nodes))
        self.assertIn("T1", st["self"]["claims"])
        self.assertIsNone(st["web_error"])

    def test_an_error_inside_the_web_switches_it_off_and_never_crashes_the_mind(self):
        root = self.new_root()
        gp = root.parent / "g.genome"
        gp.write_text(lean_text())
        m = MM.Mind(gp, root)
        try:
            def boom(word):
                raise RuntimeError("planted")
            m.webs["L"].hear = boom
            for row in self.rows:
                m.consume(row)                       # must not raise
            self.assertIsNone(m.webs)
            self.assertIn("planted", m.web_error)
            self.assertIn("planted", m.brain_status()["web_error"])
            self.assertTrue((root / "web" / "ERROR.txt").exists())
        finally:
            m.close()
        self.assertEqual(hashlib.sha256(S.journal_bytes(root)).hexdigest(), LIVED_JOURNAL_SHA, "the journal is untouched by the failure")

    def test_a_life_without_a_brain_grows_no_web(self):
        root = self.new_root()
        gp = root.parent / "g.genome"
        gp.write_text((REPO / "genome" / "G4-skeleton.genome").read_text())
        m = MM.Mind(gp, root)
        try:
            self.assertIsNone(m.webs)
            self.assertIsNone(m.self_node)
        finally:
            m.close()


if __name__ == "__main__":
    unittest.main()
