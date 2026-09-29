# edit: Claude (Fable 5.1, the seat), 2026-09-29 13:22 +0400 — the gate's reader, pinned BEFORE the read (PREREG-WORD-ROAD §3: «written and
# pinned before the read, each with a planted control»).
"""tests/tools/test_wordroad_gate.py — tools/brain/wordroad_gate.py: its arithmetic against known values, its re-pointing
against the organs' road's OWN answer for the shorter phrase (in a real mind), its populations, and its first-hearing bar."""
from __future__ import annotations

import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import creature.mind as MM
from brain.scene import world as W
from creature import organs_road as R
from tests.creature import _scene_tape as S
from tests.creature import test_hear_mind as TH
from tools.brain import wordroad_gate as WG


class Arithmetic(unittest.TestCase):
    def test_the_sign_test_is_exact(self) -> None:
        self.assertEqual(WG.sign_p(0, 0), 1.0)
        self.assertEqual(WG.sign_p(10, 0), 1.0 / 1024.0)
        self.assertEqual(WG.sign_p(9, 0), 1.0 / 512.0)
        self.assertAlmostEqual(WG.sign_p(3, 1), 5.0 / 16.0, places=15)
        self.assertEqual(WG.sign_p(0, 5), 1.0)
        self.assertLess(WG.sign_p(10, 0), 1e-3)                       # the smallest passing result at p < 0.001
        self.assertGreater(WG.sign_p(9, 0), 1e-3)

    def test_the_poisson_binomial_tail_is_the_binomials_when_every_chance_is_equal(self) -> None:
        n, p = 12, 0.5
        for k in range(n + 2):
            want = sum(math.comb(n, j) for j in range(k, n + 1)) / 2 ** n
            self.assertAlmostEqual(WG.pb_tail([p] * n, k), want, places=12)
        self.assertAlmostEqual(WG.pb_tail([1.0, 0.0, 0.5], 2), 0.5, places=15)

    def test_paired_counts_both_ways(self) -> None:
        a = [True, True, False, False, True]
        b = [True, False, True, False, False]
        r = WG.paired(a, b)
        self.assertEqual((r["n"], r["f"], r["u"]), (5, 2, 1))
        self.assertAlmostEqual(r["diff"], 0.2)
        self.assertAlmostEqual(r["a"] - r["b"], r["diff"])
        self.assertEqual(r["p_a_higher"], WG.sign_p(2, 1))
        self.assertEqual(r["p_a_lower"], WG.sign_p(1, 2))
        with self.assertRaises(WG.GateError):
            WG.paired([True], [True, False])

    def test_repoint_none_and_ties(self) -> None:
        by = {"red": [0.0, 0.0], "ring": [0.0, 0.0]}
        self.assertIsNone(WG.repoint(by, ["red", "ring"], ["ring"], lambda n: 0))
        by = {"red": [0.1, 0.3], "ring": [0.5, 0.5]}
        self.assertEqual(WG.repoint(by, ["red", "ring"], ["red", "ring"], lambda n: 0), 1)
        self.assertEqual(WG.repoint(by, ["red", "ring"], ["ring"], lambda n: 1), 1)      # a tie: the generator decides
        self.assertEqual(WG.repoint(by, ["red", "ring"], ["ring"], lambda n: 0), 0)
        self.assertIsNone(WG.repoint(by, ["red", "ring"], [], lambda n: 0))


class RepointIsTheRoadsOwnAnswer(unittest.TestCase):
    """In a REAL mind under the line: for every pointing ask, the organs' road is asked a second time with the phrase's shape
    words alone (the same cells, the same glance, the same item); the reader's re-pointing from the first answer's
    `scores_by_word` must be that second answer, item by item."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="wordroad-gate-"))
        tape_root = cls.tmp / "tape-root"
        tape_root.mkdir()
        cls.info = S.build(tape_root, n_train=TH.N_TRAIN, per_split=6)
        rows = S.rows(tape_root)
        root = S.link_root(tape_root, cls.tmp / "run" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(TH.genome_text(True))
        cls.pairs = []
        real = R.answer_point

        def both(org, Lw, payload, fix, located, hyps):
            full = real(org, Lw, payload, fix, located, hyps)
            shape = [w for w in (payload.get("phrase") or []) if W.word_type(w) == "shape"]
            alone = real(org, Lw, {**payload, "phrase": shape}, fix, located, hyps) if shape else None
            cls.pairs.append((dict(payload), full, alone))
            return full

        with mock.patch.object(R, "answer_point", both):
            m = MM.Mind(gp, root)
            try:
                for row in rows:
                    m.consume(row)
            finally:
                m.close()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _cases(self):
        for payload, (full, detail), alone in self.pairs:
            if full["raw"].get("unheard") or "scores_by_word" not in detail:
                continue
            yield payload, full, detail, alone

    def test_the_fixture_holds_pointings_of_several_words_and_a_none(self) -> None:
        cases = list(self._cases())
        self.assertGreaterEqual(sum(1 for p, _f, _d, _a in cases if len(p["phrase"]) > 1), 5)
        self.assertGreaterEqual(len(cases), 8)

    def test_the_whole_phrase_again_is_the_answer(self) -> None:
        for payload, full, detail, _alone in self._cases():
            got = WG.repoint(detail["scores_by_word"], payload["phrase"], payload["phrase"],
                             WG.tie_of(payload["test_seed"], payload["item"]))
            self.assertEqual(got, full["raw"]["point"], payload["item"])

    def test_the_shape_word_alone_is_the_roads_own_answer_for_it(self) -> None:
        n = differ = 0
        for payload, full, detail, alone in self._cases():
            shape = [w for w in payload["phrase"] if W.word_type(w) == "shape"]
            if not shape or alone is None:
                continue
            got = WG.repoint(detail["scores_by_word"], payload["phrase"], shape, WG.tie_of(payload["test_seed"], payload["item"]))
            self.assertEqual(got, alone[0]["raw"]["point"], payload["item"])
            n += 1
            differ += got != full["raw"]["point"]
        self.assertGreaterEqual(n, 8)
        self.assertGreater(differ, 0, "the fixture must hold an item where the shape word alone points elsewhere")

    def test_the_planted_control_a_rounded_score_is_caught(self) -> None:
        # scores rounded to 1 decimal (a reader fed rounded values): at least one re-pointing must differ from the road's
        bad = 0
        for payload, full, detail, _alone in self._cases():
            rounded = {w: [round(v, 1) for v in vs] for w, vs in detail["scores_by_word"].items()}
            got = WG.repoint(rounded, payload["phrase"], payload["phrase"], WG.tie_of(payload["test_seed"], payload["item"]))
            bad += got != full["raw"]["point"]
        self.assertGreater(bad, 0)


class Populations(unittest.TestCase):
    THINGS = [{"shape": "circle", "colour": "red", "size": "big"}, {"shape": "circle", "colour": "blue", "size": "big"},
              {"shape": "star", "colour": "red", "size": "small"}]

    def test_needed(self) -> None:
        tr = {"things": self.THINGS, "fix_thing": [0, 1, 2, 0]}
        it = {"target": 0, "n_things": 3}
        self.assertTrue(WG.needed(it, tr, ["red", "circle"]))
        self.assertFalse(WG.needed(it, tr, ["circle"]), "no size or colour word")
        self.assertFalse(WG.needed({"target": 2, "n_things": 3}, tr, ["red", "star"]), "no other star: the word is not needed")
        self.assertFalse(WG.needed(it, {"things": self.THINGS, "fix_thing": [1, 1, 2, 2]}, ["red", "circle"]), "the target was not seen")
        self.assertFalse(WG.needed({"target": 0, "n_things": 1}, {"things": self.THINGS[:1], "fix_thing": [0]}, ["red", "circle"]))

    def test_right_needs_a_named_hypothesis(self) -> None:
        self.assertTrue(WG.is_right(1, [0, 2], 2))
        self.assertFalse(WG.is_right(0, [0, 2], 2))
        self.assertFalse(WG.is_right(None, [0, 2], 2), "«none» is not right")
        self.assertFalse(WG.is_right(5, [0, 2], 2))


class FirstHearings(unittest.TestCase):
    class _Life:
        train_moment = {0: "m0", 1: "m1", 2: "m2"}
        moment_words = {"m0": ["small", "star"], "m1": ["star"], "m2": ["red", "red", "ring"]}

    class _Arm:
        pass

    def _arm(self):
        a = self._Arm()
        a.life = self._Life()
        return a

    def test_every_word_born_where_it_is_first_heard(self) -> None:
        j = [{"moment": "m0", "word": "star", "births": [["sight", 0, "novelty"], ["words", 0, "novelty"], ["words", 1, "novelty"]]},
             {"moment": "m1", "word": "star", "births": []},
             {"moment": "m2", "word": "ring", "births": [["words", 2, "novelty"], ["words", 3, "novelty"]]}]
        r = WG.first_hearings(self._arm(), j)
        self.assertEqual(r["canvases_wrong"], [])
        self.assertEqual(r["words_heard"], 4)
        self.assertEqual(r["first_heard_at_scene"], {"small": 0, "star": 0, "red": 2, "ring": 2})

    def test_a_word_with_no_cell_at_its_first_hearing_is_named(self) -> None:
        j = [{"moment": "m0", "word": "star", "births": [["words", 0, "novelty"]]},          # «small» got no cell
             {"moment": "m1", "word": "star", "births": []},
             {"moment": "m2", "word": "ring", "births": [["words", 1, "novelty"], ["words", 2, "novelty"]]}]
        r = WG.first_hearings(self._arm(), j)
        self.assertEqual(r["canvases_wrong"], [{"scene": 0, "first_heard": ["small", "star"], "word_cells_born": 1}])

    def test_a_canvas_with_no_journal_row_is_named(self) -> None:
        j = [{"moment": "m0", "word": "star", "births": [["words", 0, "novelty"], ["words", 1, "novelty"]]}]
        r = WG.first_hearings(self._arm(), j)
        self.assertEqual([w["scene"] for w in r["canvases_wrong"]], [1, 2])


if __name__ == "__main__":
    unittest.main()
