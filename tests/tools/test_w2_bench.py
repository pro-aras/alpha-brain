"""PREREG-W2 (SIGNED x3) — the bench drivers' tests, written FIRST (red): the SHARED feed, the mentor stream, the ON-tape
injector, the I2 diff reader, the arms primitives.

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:35 +0400 — new file for the W2 build; law §3 (the bench),
# §4 (the gates' forms), §5 M-CONTINGENT/M-BIND's dealt forms.

  feed: the SHARED state row's layout (dims 0-5 the state, 6-143 the neutral fill = the shadow standardiser's running
  mean, 144-145 the (0,0) kind tag), always present; NOSTATE one row fewer; the shadow standardiser ends byte-identical
  to the learner's own (the G0g form). stream: the canvas's utterance parts (parent, carriers with tpl, mirror tokens),
  the dealt mirror moving ONLY the tokens with counts preserved and no fixed point. inject: the ON tape's non-mentor
  rows equal after renumbering; mentor rows before their moments' eye rows with payloads and shas. diffj: the journal
  confinement form — non-brain rows equal, the first difference a brain row at the first mentor moment, heard deltas
  inside the moment's mentor words; the planted violations CAUGHT. arms: a tiny end-to-end smoke and CONST at 0.5.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.scene import learners as Lr
from brain.world.seeds import substream
from tools.toys.w2 import arms as A
from tools.toys.w2 import census as C
from tools.toys.w2 import diffj as D
from tools.toys.w2 import feed as F
from tools.toys.w2 import inject as I
from tools.toys.w2 import record as R
from tools.toys.w2 import state as ST
from tools.toys.w2 import stream as SM

BL2 = Path("scratch/bl2")


class TestFeed(unittest.TestCase):
    def _tiny(self):
        rng = np.random.default_rng(3)
        Xs = [rng.standard_normal((2, 146)) for _ in range(6)]
        states = [np.array([1.0, 0.0, 0.0, 1.0, 0.5, 0.25]) for _ in range(6)]
        return Xs, states

    def test_the_state_rows_layout_and_the_always_present_rule(self):
        Xs, states = self._tiny()
        mats, stats = F.build(Xs, states, "S")
        self.assertEqual(len(mats), 6)
        for i, M in enumerate(mats):
            self.assertEqual(M.shape[0], 3)                          # two thing rows + the state row, every canvas
            sr = M[-1]
            self.assertTrue(np.array_equal(sr[:6], states[i]))
            self.assertEqual((sr[144], sr[145]), (0.0, 0.0))           # the declared kind tag
        matsN, _ = F.build(Xs, states, "N")
        for M in matsN:
            self.assertEqual(M.shape[0], 2)                            # NOSTATE: one row fewer
        self.assertEqual(stats.n, 18)                                # the standardiser's n counts ROWS: 6 canvases x 3

    def test_the_shadow_standardiser_equals_the_learners_own(self):
        Xs, states = self._tiny()
        mats, stats = F.build(Xs, states, "S")
        L = Lr.RWLearner(lr=0.01, dim=146)
        for t, M in enumerate(mats):
            L.train_scene(M, ["alpha"], referent=None, rng=substream(1, f"t:{t}"))
        self.assertTrue(np.array_equal(L.stats.mean, stats.mean))
        self.assertTrue(np.array_equal(L.stats.m2, stats.m2))

    def test_the_test_window_fills_with_the_frozen_mean(self):
        Xs, states = self._tiny()
        _, stats = F.build(Xs, states, "S")
        mats, stats2 = F.build(Xs, states, "S", window="test", frozen_mean=stats.mean)
        self.assertEqual(stats2.n, 0)                                  # a test window observes nothing
        self.assertTrue(np.array_equal(mats[0][-1][6:144], stats.mean[6:144]))


class TestStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canvases = R.assemble(BL2, 0, 290)
        cls.census = C.meeting_counts([c.words for c in cls.canvases])
        cls.stream = SM.build(cls.canvases, cls.census, 20261799, 250, 290)

    def test_utterance_parts_and_the_mirror_tokens(self):
        for u in self.stream.utterances:
            self.assertTrue(u["parent"])
            for w in u["mirror"]:
                self.assertIn(w, ("unsure", "fresh", "asked"))
        for pos, u in enumerate(self.stream.utterances):
            lead = self.stream.referents[pos]
            lw = self.canvases[250 + pos].things[lead].shape if lead is not None else self.canvases[250 + pos].words[-1]
            m = self.census[250 + pos].get(lw, 0)
            self.assertEqual("fresh" in u["mirror"], m < 3, (pos, lw, m))      # young is the GLOBAL census's own rule

    def test_the_dealt_mirror_moves_only_the_tokens(self):
        perm = Lr.nshuf_permutation(substream(20261799, "w2:deal:1"), len(self.stream.utterances))
        dealt = SM.deal_mirror(self.stream.utterances, perm)
        for u0, u1 in zip(self.stream.utterances, dealt):
            self.assertEqual(u0["parent"], u1["parent"])
            self.assertEqual(u0["carrier"], u1["carrier"])
        for w in ("unsure", "fresh", "asked"):
            self.assertEqual(sum(w in u["mirror"] for u in dealt), sum(w in u["mirror"] for u in self.stream.utterances))
        self.assertFalse(any(perm[t] == t for t in range(len(perm))))


class TestInject(unittest.TestCase):
    def _mini_tape(self, d: Path):
        (d / "payload").mkdir(parents=True)
        rows = [{"seq": 1, "at": "a", "sense": "ear", "sha": "s1", "payload": "payload/000000001.txt", "meta": {"moment": "m0", "source": "scene", "word": "cross"}},
                {"seq": 2, "at": "a", "sense": "ear", "sha": "s2", "payload": "payload/000000002.txt", "meta": {"moment": "m0", "source": "scene", "word": "blue"}},
                {"seq": 3, "at": "b", "sense": "eye", "sha": "s3", "payload": "payload/000000003.png", "meta": {"moment": "m0", "source": "scene", "kind": "train", "scene": 0, "world_seed": 1}},
                {"seq": 4, "at": "c", "sense": "body", "sha": "s4", "payload": "payload/000000004.json", "meta": {"moment": "b0", "source": "body"}}]
        (d / "2026-01-01.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def test_the_on_tape(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"; src.mkdir()
            self._mini_tape(src)
            mentor = {"m0": [{"sense": "ear", "meta": {"moment": "m0", "source": "mentor", "word": "unsure", "tpl": "M-M1"}, "payload": "unsure".encode()}]}
            out = Path(td) / "on"
            counts = I.build_on_tape(src, out, mentor)
            rows = [json.loads(l) for l in (out / "2026-01-01.jsonl").read_text().splitlines()]
            self.assertEqual(counts["mentor_rows"], 1)
            self.assertEqual(rows[2]["meta"]["source"], "mentor")
            self.assertEqual(rows[2]["meta"]["tpl"], "M-M1")
            self.assertEqual(rows[3]["sense"], "eye")                       # the mentor row sits before its moment's eye row
            seqs = [r["seq"] for r in rows]
            self.assertEqual(seqs, sorted(seqs))
            non_mentor = [r for r in rows if r["meta"].get("source") != "mentor"]
            self.assertEqual([r["meta"].get("word") for r in non_mentor[:2]], ["cross", "blue"])
            p = out / rows[2]["payload"]
            self.assertTrue(p.exists())
            self.assertEqual(rows[2]["sha"], hashlib.sha256(p.read_bytes()).hexdigest())


class TestDiffJ(unittest.TestCase):
    def _journals(self):
        off = [{"kind": "body", "seq": 1, "v": 1},
               {"kind": "brain", "act": "turn", "seq": 2, "moment": "m0", "heard": ["cross"], "say": None},
               {"kind": "brain", "act": "learn", "seq": 3, "moment": "m0", "words": ["cross"], "attributed": {"cross": 0}},
               {"kind": "brain", "act": "turn", "seq": 4, "moment": "m1", "heard": ["ring"], "say": None},
               {"kind": "brain", "act": "learn", "seq": 5, "moment": "m1", "words": ["ring"], "attributed": {"ring": 0}},
               {"kind": "body", "seq": 6, "v": 2}]
        on = [{"kind": "body", "seq": 1, "v": 1},
              {"kind": "brain", "act": "turn", "seq": 2, "moment": "m0", "heard": ["cross", "unsure"], "say": None},
              {"kind": "brain", "act": "learn", "seq": 3, "moment": "m0", "words": ["cross", "unsure"], "attributed": {"cross": 0, "unsure": 1}},
              {"kind": "brain", "act": "turn", "seq": 4, "moment": "m1", "heard": ["ring"], "say": {"words": ["ring"]}},
              {"kind": "brain", "act": "learn", "seq": 5, "moment": "m1", "words": ["ring"], "attributed": {"ring": 1}},
              {"kind": "body", "seq": 6, "v": 2}]
        mentor = {"m0": ["unsure"]}
        return off, on, mentor

    def test_the_clean_confinement_passes(self):
        off, on, mentor = self._journals()
        out = D.journal_confinement(off, on, mentor)
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["first_diff_kind"], "brain")
        self.assertEqual(out["n_diff_by_kind"]["brain"], 4)

    def test_a_differing_non_brain_row_is_caught(self):
        off, on, mentor = self._journals()
        on[0]["v"] = 99                                                          # the planted violation
        out = D.journal_confinement(off, on, mentor)
        self.assertFalse(out["ok"])
        self.assertIn("body", out["reason"])

    def test_a_heard_delta_outside_the_mentor_words_is_caught(self):
        off, on, mentor = self._journals()
        on[1]["heard"] = ["cross", "ghost"]                                      # a word the mentor never said
        out = D.journal_confinement(off, on, mentor)
        self.assertFalse(out["ok"])
        self.assertIn("ghost", out["reason"])


class TestArms(unittest.TestCase):
    def test_train_score_and_const_at_a_half(self):
        rng = np.random.default_rng(5)
        mats = [rng.standard_normal((2, 146)) for _ in range(10)]
        utts = [["cross"] for _ in range(10)]
        L = A.train_arm(mats, utts, 1)
        W = A.score_window(L, mats)
        self.assertEqual(W.shape, (10, len(L.words)))
        self.assertEqual(A.state_word_columns(L), [])
        from tools.toys.w2 import grade as G
        self.assertEqual(G.auc(A.const_scores(0.5, 10), np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])), 0.5)


if __name__ == "__main__":
    unittest.main()
