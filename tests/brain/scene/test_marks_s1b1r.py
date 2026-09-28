# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:13 +0400 — PREREG-S1B1R §5 (sha 879a22fb…) with AMENDMENT 1 §2 (a198f0b4…), test-first
# (red on 7706371): SPEAK2's items (the kind rides on the item), MINIMAL conditioned on TRUE-and-unique phrases (Fable's
# edit: a one-word mouth that says a FALSE word must not pass MINIMAL by absence), TRUTH-NEED on SPEAK2, ORDER and the
# length mix over SPEAK + SPEAK2, the per-kind lines and the achieved target mix, and the null's distribution (numpy's
# default linear percentile).
from __future__ import annotations

import unittest

import numpy as np

from brain.scene import marks as M
from brain.scene import world as W

T = lambda s, c, z: W.Thing(s, c, z, 0, 0)


def _row(r, things, target, index, split="speak2"):
    return {"row": r, "index": index, "item_id": f"{split}:x:{index:05d}", "things": [t.to_dict() for t in things],
            "fix_thing": list(range(len(things))), "referent": target, "centroids": [[0.0, 0.0]] * len(things)}


class TestMinimal(unittest.TestCase):
    def test_minimal_is_read_only_on_true_and_unique_phrases(self) -> None:
        things = [T("circle", "red", "big"), T("circle", "red", "small"), T("triangle", "red", "big")]   # an SS scene
        self.assertTrue(M.minimal_true(["big", "circle"], things, 0))
        self.assertFalse(M.minimal_true(["big", "red", "circle"], things, 0))      # «big circle» is a unique proper subset
        self.assertIsNone(M.minimal_true(["red"], things, 0))                      # not unique: not counted at all
        self.assertIsNone(M.minimal_true(["star"], things, 0))                     # false: not counted
        two = [T("circle", "red", "big"), T("square", "blue", "big")]
        self.assertTrue(M.minimal_true(["circle"], two, 0))

    def test_a_one_word_false_mouth_cannot_pass_minimal_by_absence(self) -> None:
        things = [T("circle", "red", "big"), T("circle", "red", "small"), T("triangle", "red", "big")]
        truth = [_row(0, things, 0, 40), _row(1, things, 0, 41)]
        items = M.speak2_items(truth)
        ans = {items[0]["item_id"]: {"spoken": ["circle"], "readback_point": 0, "target": 0},
               items[1]["item_id"]: {"spoken": ["red"], "readback_point": 0, "target": 0}}
        rows = M.grade_mouth_r(items, ans, truth)
        s = M.summarise_mouth_r([], rows)
        self.assertEqual(s["minimal"], None)                                       # n = 0 true-and-unique phrases
        self.assertEqual(s["n_minimal"], 0)
        self.assertEqual(s["truth_need"], 0.0)                                     # TRUTH-NEED carries the failure
        self.assertEqual(s["n_truth_need"], 2)


class TestSpeak2Grading(unittest.TestCase):
    def setUp(self) -> None:
        cs = [T("circle", "red", "big"), T("triangle", "red", "big"), T("circle", "green", "big")]
        sc = [T("circle", "red", "big"), T("circle", "red", "small"), T("circle", "green", "big")]
        ss = [T("circle", "red", "big"), T("circle", "red", "small"), T("triangle", "red", "big")]
        self.truth = [_row(0, cs, 0, 3), _row(1, sc, 0, 25), _row(2, ss, 0, 47)]
        self.items = M.speak2_items(self.truth)

    def test_items_carry_their_kind(self) -> None:
        self.assertEqual([it["kind"] for it in self.items], ["CS", "SC", "SS"])
        self.assertEqual([it["mark"] for it in self.items], ["SPEAK2"] * 3)
        self.assertEqual(set(M.question(self.items[0])), {"item_id", "mark", "row", "phrase"})

    def test_truth_need_minimal_order_per_kind(self) -> None:
        ans = {self.items[0]["item_id"]: {"spoken": ["red", "circle"], "readback_point": 0, "target": 0},       # true, minimal, ordered
               self.items[1]["item_id"]: {"spoken": ["red", "big"], "readback_point": 0, "target": 0},          # true, minimal, NOT ordered
               self.items[2]["item_id"]: {"spoken": ["big", "red", "circle"], "readback_point": 0, "target": 0}}  # true, not minimal, ordered
        rows = M.grade_mouth_r(self.items, ans, self.truth)
        s = M.summarise_mouth_r([], rows)
        self.assertEqual((s["truth_need"], s["n_truth_need"]), (1.0, 3))
        self.assertAlmostEqual(s["minimal"], 2 / 3)
        self.assertEqual(s["n_minimal"], 3)
        self.assertAlmostEqual(s["order"], 2 / 3)
        self.assertEqual(s["n_order"], 3)
        self.assertEqual(s["length_mix"], {"1": 0.0, "2": 2 / 3, "3": 1 / 3})
        k = s["kinds"]
        self.assertEqual((k["CS"]["truth_need"], k["CS"]["minimal"], k["CS"]["order"]), (1.0, 1.0, 1.0))
        self.assertEqual(k["SC"]["order"], 0.0)
        self.assertEqual(k["SS"]["minimal"], 0.0)

    def test_order_and_minimal_pool_speak_with_speak2(self) -> None:
        sp_things = [T("circle", "red", "big"), T("square", "blue", "small")]
        sp_truth = [_row(0, sp_things, 0, 0, split="speak")]
        sp_items = M.speak_items(sp_truth)
        sp_rows = M.grade_mouth_r(sp_items, {sp_items[0]["item_id"]: {"spoken": ["circle", "red"], "readback_point": 0,
                                                                      "target": 0}}, sp_truth)
        rows2 = M.grade_mouth_r(self.items[:1], {self.items[0]["item_id"]: {"spoken": ["red", "circle"], "readback_point": 0,
                                                                             "target": 0}}, self.truth)
        s = M.summarise_mouth_r(sp_rows, rows2)
        self.assertEqual((s["order"], s["n_order"]), (0.5, 2))                    # «circle red» is out of the parent's order
        self.assertEqual((s["minimal"], s["n_minimal"]), (0.5, 2))                # «circle» alone is unique on the SPEAK scene
        self.assertEqual((s["truth"], s["n_truth"]), (1.0, 1))                    # TRUTH reads SPEAK alone

    def test_the_achieved_target_mix(self) -> None:
        mix = M.target_mix(self.items, self.truth)
        self.assertEqual(mix["CS"], {"shape": {"circle": 1}, "colour": {"red": 1}, "size": {"big": 1}})


class TestNull(unittest.TestCase):
    def test_distribution_numpy_linear(self) -> None:
        v = [0.5, 0.52, 0.55, 0.48, 0.61, 0.58, 0.53, 0.49, 0.57, 0.6, 0.51, 0.54, 0.56, 0.59, 0.47, 0.5, 0.62, 0.55, 0.52, 0.58]
        s = M.null_summary(v)
        self.assertEqual(s["n"], 20)
        self.assertAlmostEqual(s["p95"], float(np.percentile(v, 95)))
        self.assertEqual((s["min"], s["max"]), (0.47, 0.62))
        self.assertAlmostEqual(s["median"], float(np.median(v)))
        self.assertIsNone(M.null_summary([])["p95"])


if __name__ == "__main__":
    unittest.main()
