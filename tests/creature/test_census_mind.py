# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:51 +0400 — PREREG-METADATA-1 §3 (C1 to C5), test-first (red on 748b790: no segments, no census).
"""tests/creature/test_census_mind.py — the source of every memory, and the census.

One fixture tape (120 scenes), lived by the lean body. The recount of C1 is written HERE, from the learner's own store_t and
the brain's segments, never by calling the census's code."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import creature.mind as MM
from genome.brain import Brain, BrainError
from tests.creature import _scene_tape as S
from tests.creature.test_inherit_mind import N_TRAIN, lean_text

# C3's pin: the journal of this very life under the code BEFORE the build (748b790), taken twice, 528 rows of 415 tape rows.
LIVED_JOURNAL_SHA = "7cb059845c9027f093de7a7409d31e1e4980cc0913535210a8d8ba20af56e00e"
LIVED_JOURNAL_ROWS = 528
PARENT_V1 = Path("/data/dev/genome-lives/brain-lean-nearest-20261102/state/brain")
SOURCES = ("lived", "prenatal", "implanted-episode", "implanted-knowledge", "inherited")


def recount(brain) -> dict:
    """The test's OWN count: per word, its episodes by source, from store_t (1-based order of life) through the segments."""
    def source_of(order: int) -> str:
        hit = [s for s in brain.segments if s["start"] <= order < s["end"]]
        assert len(hit) == 1, (order, brain.segments)
        return hit[0]["source"]
    out = {}
    for w, j in brain.L.index.items():
        c = {}
        for t in brain.L.store_t[j]:
            src = source_of(int(t) - 1)
            c[src] = c.get(src, 0) + 1
        out[w] = c
    return out


class CensusMind(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="census-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.life, cls.life_root = cls.live(lean_text())
        cls.pair = cls.tmp / "pair"
        cls.pair.mkdir()
        cls.life.brain.save(cls.pair / "brain")

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def new_root(cls, pair: Path = None) -> Path:
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        if pair is not None:
            (root / "inherit").mkdir()
            for ext in ("json", "npz"):
                shutil.copy(Path(str(pair) + "." + ext) if pair.suffix == "" and not pair.is_dir() else pair / f"brain.{ext}",
                            root / "inherit" / f"brain.{ext}")
        return root

    @classmethod
    def live(cls, text: str, pair: Path = None, rows=None):
        root = cls.new_root(pair)
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root

    # -- C1 -------------------------------------------------------------------------------------
    def test_c1_the_census_equals_the_recount(self):
        b = self.life.brain
        c = b.census()
        mine = recount(b)
        self.assertGreater(sum(sum(v.values()) for v in mine.values()), N_TRAIN, "the recount counted something")
        for w in b.L.index:
            self.assertEqual({k: v for k, v in c["words"][w]["episodes_by_source"].items() if v}, mine[w], w)
            self.assertEqual(c["words"][w]["meetings"], int(b.L.meetings[b.L.index[w]]))
        self.assertEqual(c["scenes_by_source"], {"lived": N_TRAIN})
        self.assertEqual(c["scenes"], N_TRAIN)
        self.assertEqual(c["given_only_words"], [])
        self.assertEqual([s["source"] for s in b.segments], ["lived"])
        self.assertEqual((b.segments[0]["start"], b.segments[0]["end"]), (0, N_TRAIN))

    def test_the_census_writes_nothing(self):
        b = self.life.brain
        h = b.state_hash()
        b.census()
        self.assertEqual(b.state_hash(), h)

    # -- C2 -------------------------------------------------------------------------------------
    def test_c2_one_planted_scene_moves_the_census_by_exactly_one(self):
        b = Brain.load(self.pair / "brain", dict(self.life.genome.declared["BRAIN"]))
        before, h0 = b.census(), b.state_hash()
        X, words, _ = b.seen[5]
        b.begin_run("implanted-episode", "the test")
        b.L.train_scene(X, list(words), referent=None, rng=__import__("numpy").random.default_rng(0))
        b.seen.append((X, list(words), None)); b.moments.append("planted"); b.scenes.append(-1); b.canvas.append(b.canvas[5])
        b.note_learned("planted")
        after = b.census()
        self.assertNotEqual(b.state_hash(), h0, "the plant changed the state")
        self.assertEqual(after["scenes"], before["scenes"] + 1)
        self.assertEqual(after["scenes_by_source"], {"lived": N_TRAIN, "implanted-episode": 1})
        for w in before["words"]:
            d = after["words"][w]["meetings"] - before["words"][w]["meetings"]
            self.assertEqual(d, 1 if w in words else 0, w)
            self.assertEqual(after["words"][w]["episodes_by_source"].get("lived", 0),
                             before["words"][w]["episodes_by_source"].get("lived", 0), w)
        moved = sum(after["words"][w]["episodes_by_source"].get("implanted-episode", 0) for w in after["words"])
        self.assertGreaterEqual(moved, 1)
        self.assertEqual({k: v for w in after["words"] for k, v in after["words"][w]["episodes_by_source"].items()
                          if k not in ("lived", "implanted-episode") and v}, {})
        self.assertEqual(recount(b), {w: {k: v for k, v in after["words"][w]["episodes_by_source"].items() if v} for w in after["words"]})

    def test_an_unknown_source_refuses_by_name(self):
        b = Brain(dict(self.life.genome.declared["BRAIN"]))
        with self.assertRaises(BrainError) as cm:
            b.begin_run("dreamt", "the test")
        self.assertIn("source", str(cm.exception))

    # -- C3 -------------------------------------------------------------------------------------
    def test_c3_a_lived_life_is_unchanged(self):
        J = S.journal(self.life_root)
        self.assertEqual(len(J), LIVED_JOURNAL_ROWS)
        self.assertGreater(len(J), 100)
        self.assertEqual(hashlib.sha256(S.journal_bytes(self.life_root)).hexdigest(), LIVED_JOURNAL_SHA)
        self.assertEqual([r for r in J if r.get("kind") == "census"], [])

    def test_the_mind_writes_the_census_as_files_and_on_status(self):
        files = sorted((self.life_root / "census").glob("*.json"))
        self.assertGreaterEqual(len(files), 2, "one per calibration and one at close")
        last = json.loads(files[-1].read_text())
        self.assertEqual(last["scenes"], N_TRAIN)
        self.assertEqual(last["scenes_by_source"], {"lived": N_TRAIN})
        st = self.life.brain_status()
        self.assertEqual(st["census"]["scenes_by_source"], {"lived": N_TRAIN})

    # -- C4 -------------------------------------------------------------------------------------
    @unittest.skipUnless(Path(str(PARENT_V1) + ".json").exists(), "the real version 1 state is not on this box")
    def test_c4_a_version_1_state_loads_as_one_lived_run(self):
        meta = json.loads(Path(str(PARENT_V1) + ".json").read_text())
        self.assertEqual(meta["version"], 1)
        b = Brain.load(PARENT_V1, meta["cfg"])
        self.assertEqual(b.n_learned, 10000)
        self.assertEqual([(s["start"], s["end"], s["source"], s["author"]) for s in b.segments], [(0, 10000, "lived", None)])
        self.assertEqual(sorted(b.L.words), sorted(meta["learner"]["words"]))
        self.assertEqual(b.census()["scenes_by_source"], {"lived": 10000})

    @unittest.skipUnless(Path(str(PARENT_V1) + ".json").exists(), "the real version 1 state is not on this box")
    def test_c4_a_version_1_state_with_one_byte_changed_still_refuses(self):
        bad = self.tmp / "v1bad"
        bad.mkdir()
        for ext in ("json", "npz"):
            shutil.copy(str(PARENT_V1) + "." + ext, bad / f"brain.{ext}")
        p = bad / "brain.json"
        t = p.read_text()
        t2 = t.replace('"scenes":10000', '"scenes":10001', 1)
        self.assertNotEqual(t, t2, "the plant changed the bytes")
        p.write_text(t2)
        with self.assertRaises(BrainError):
            Brain.load(bad / "brain", json.loads(t)["cfg"])

    # -- C5 -------------------------------------------------------------------------------------
    def test_c5_a_child_names_what_it_was_given(self):
        root = self.new_root(self.pair)
        gp = root.parent / "g.genome"
        gp.write_text(lean_text())
        m = MM.Mind(gp, root)
        try:
            c0 = m.brain.census()
            self.assertEqual(c0["scenes_by_source"], {"inherited": N_TRAIN})
            self.assertEqual([s["source"] for s in m.brain.segments], ["inherited"])
            self.assertEqual(sorted(c0["given_only_words"]), sorted(m.brain.L.words))
            mature = [w for w in m.brain.L.words if int(m.brain.L.meetings[m.brain.L.index[w]]) >= 3]
            a = m.brain.why(mature[0])
            self.assertEqual((a["kind"], a["source"]), ("given", "inherited"))
            for row in self.rows:
                m.consume(row)
            c1 = m.brain.census()
            self.assertEqual(c1["scenes_by_source"], {"inherited": N_TRAIN, "lived": N_TRAIN})
            self.assertEqual([s["source"] for s in m.brain.segments], ["inherited", "lived"])
            self.assertEqual(recount(m.brain), {w: {k: v for k, v in c1["words"][w]["episodes_by_source"].items() if v} for w in c1["words"]})
        finally:
            m.close()

    def test_a_saved_state_keeps_its_segments(self):
        b = Brain.load(self.pair / "brain", dict(self.life.genome.declared["BRAIN"]))
        self.assertEqual([(s["start"], s["end"], s["source"]) for s in b.segments], [(0, N_TRAIN, "lived")])
        self.assertEqual(json.loads((self.pair / "brain.json").read_text())["version"], 2)


if __name__ == "__main__":
    unittest.main()
