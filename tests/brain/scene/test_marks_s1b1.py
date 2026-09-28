# edit: Claude (Opus 5.5, S1b-1 builder), 2026-09-28 13:48 +0400 — PREREG-S1B1 §4, §5 (sha caace482…), test-first (red on 4093ff9): the
# graders of M3 COMPOSE (items, per distractor kind / size / pair) and of SPEAK / DECLINE (SPOKEN, TRUTH order-free on the
# world's things, TRUTH-SEEN, READ-BACK re-checked from the recorded point and target — the wiring pin, ORDER against the
# parent's template order, the length mix, DECLINE with its kinds, the chance of a random true phrase for N-SHUF).
from __future__ import annotations

import unittest

from brain.scene import marks as M
from brain.scene import world as W


def _rows(scenes):
    rows = []
    for r, s in enumerate(scenes):
        d = s.to_dict()
        d.update({"row": r, "fix_thing": list(range(len(s.things))), "centroids": [[0.0, 0.0]] * len(s.things)})
        rows.append(d)
    return rows


class TestM3Items(unittest.TestCase):
    def test_items_carry_kind_pair_and_the_necessary_words(self) -> None:
        rows = _rows(W.scenes_for("m3", 20261201))
        items = M.m3_items(rows)
        self.assertEqual(len(items), 60)
        for it in items:
            idx = rows[it["row"]]["index"]
            self.assertEqual(it["kind"], W.m3_kind(idx))
            self.assertEqual(tuple(it["pair"]), W.HELDOUT[idx % 6])
            self.assertEqual(it["phrase"], [it["pair"][1], it["pair"][0]])
            want = {"colour": ["shape"], "shape": ["colour"], "both": ["colour", "shape"]}[it["kind"]]
            self.assertEqual(it["types"], want)
            self.assertEqual(set(M.question(it)), {"item_id", "mark", "row", "phrase"})

    def test_summary_by_kind_size_pair(self) -> None:
        rows = _rows(W.scenes_for("m3", 20261201))
        items = M.m3_items(rows)
        g = [{"item_id": it["item_id"], "covered": True, "correct": (k % 2 == 0), "gradable": True, "none": False,
              "answered": True, "chance": 1.0 / it["n_things"], "n_things": it["n_things"], "types": it["types"],
              "template": "T2"} for k, it in enumerate(items)]
        s = M.summarise_m3(g, items)
        self.assertEqual(s["all"]["n_covered"], 60)
        self.assertEqual(s["kind:colour"]["n_covered"], 20)
        self.assertEqual(s["kind:shape"]["n_covered"], 20)
        self.assertEqual(s["kind:both"]["n_covered"], 20)
        self.assertEqual(sum(s[f"pair:{p[0]}-{p[1]}"]["n_covered"] for p in W.HELDOUT), 60)


class TestSpeakGrading(unittest.TestCase):
    def setUp(self) -> None:
        rc = {"shape": "circle", "colour": "red", "size": "big", "top": 0, "left": 0}
        bc = {"shape": "circle", "colour": "blue", "size": "big", "top": 0, "left": 60}
        rs = {"shape": "square", "colour": "red", "size": "small", "top": 60, "left": 0}
        self.truth = [{"row": 0, "things": [rc, bc], "fix_thing": [0, 0, 1], "referent": 0},
                      {"row": 1, "things": [rc, bc, rs], "fix_thing": [0, 1, 1], "referent": 0},
                      {"row": 2, "things": [rc, rs], "fix_thing": [1, 1, 1], "referent": 0}]
        self.items = [{"item_id": f"SPEAK:s{r}", "mark": "SPEAK", "row": r, "target": 0,
                       "n_things": len(self.truth[r]["things"])} for r in range(3)]

    def test_truth_is_order_free_and_unique_on_all_things(self) -> None:
        ans = {"SPEAK:s0": {"spoken": ["red", "circle"], "readback_point": 0, "target": 0},
               "SPEAK:s1": {"spoken": ["circle", "red"], "readback_point": 0, "target": 0},
               "SPEAK:s2": {"spoken": None, "reason": "uncovered", "uncovered": True}}
        rows = M.grade_speak(self.items, ans, self.truth)
        self.assertEqual([r["covered"] for r in rows], [True, True, False])
        self.assertTrue(rows[0]["true"] and rows[1]["true"])                    # order-free
        self.assertTrue(rows[0]["in_order"] and not rows[1]["in_order"])         # the parent says colour before shape
        s = M.summarise_speak(rows)
        self.assertEqual((s["spoken"], s["n_covered"]), (1.0, 2))
        self.assertEqual((s["truth"], s["n_spoken"]), (1.0, 2))
        self.assertEqual(s["readback"], 1.0)
        self.assertEqual(s["order"], 0.5)
        self.assertEqual(s["length_mix"], {"1": 0.0, "2": 1.0, "3": 0.0})

    def test_a_phrase_true_of_another_thing_is_not_true_and_readback_is_rechecked(self) -> None:
        ans = {"SPEAK:s0": {"spoken": ["circle"], "readback_point": 1, "target": 0},
               "SPEAK:s1": {"spoken": ["red"], "readback_point": 0, "target": 0},
               "SPEAK:s2": {"spoken": None, "reason": "no held word"}}
        rows = M.grade_speak(self.items, ans, self.truth)
        self.assertFalse(rows[0]["true"])                                       # «circle» is true of both circles
        self.assertFalse(rows[1]["true"])                                       # «red» is true of the red square too
        s = M.summarise_speak(rows)
        self.assertEqual(s["readback"], 0.5)                                    # the recorded point ≠ the target once
        self.assertEqual(s["truth"], 0.0)

    def test_truth_seen_reads_only_the_things_the_gaze_landed_on(self) -> None:
        # row 1: the red square (thing 2) has no fixation → «red» is true-seen though not true
        truth = [dict(self.truth[1], fix_thing=[0, 1, 1])]
        items = [dict(self.items[1], row=0)]
        rows = M.grade_speak(items, {"SPEAK:s1": {"spoken": ["red"], "readback_point": 0, "target": 0}}, truth)
        self.assertFalse(rows[0]["true"])
        self.assertTrue(rows[0]["true_seen"])

    def test_chance_of_a_random_true_phrase(self) -> None:
        things = [W.Thing("circle", "red", "big", 0, 0), W.Thing("circle", "blue", "big", 0, 60)]
        c = M.random_true_phrase_chance(things, 0)
        # the grammar (size|∅) × (colour|∅) × shape = 108 phrases; uniquely true of the red circle: «red circle»,
        # «big red circle» → 2 / 108
        self.assertAlmostEqual(c, 2 / 108)


class TestDeclineGrading(unittest.TestCase):
    def test_decline_counts_no_colour_word_and_kinds(self) -> None:
        pc = {"shape": "circle", "colour": "purple", "size": "big", "top": 0, "left": 0}
        rc = {"shape": "circle", "colour": "red", "size": "big", "top": 0, "left": 60}
        rs = {"shape": "square", "colour": "red", "size": "small", "top": 60, "left": 0}
        truth = [{"row": 0, "index": 0, "item_id": "decline:x:00000", "things": [pc, rc], "fix_thing": [0, 1], "referent": 0},
                 {"row": 1, "index": 1, "item_id": "decline:x:00001", "things": [pc, rs], "fix_thing": [0, 1], "referent": 0},
                 {"row": 2, "index": 3, "item_id": "decline:x:00003", "things": [pc, rs], "fix_thing": [0, 1], "referent": 0}]
        items = M.decline_items(truth)
        self.assertEqual([it["kind"] for it in items], ["B", "A", "A"])
        ans = {items[0]["item_id"]: {"spoken": None, "reason": "no unique read-back"},
               items[1]["item_id"]: {"spoken": ["circle"], "readback_point": 0, "target": 0},
               items[2]["item_id"]: {"spoken": ["red", "circle"], "readback_point": 0, "target": 0}}
        rows = M.grade_decline(items, ans, truth)
        s = M.summarise_decline(rows)
        self.assertAlmostEqual(s["decline"], 2 / 3)                             # a decline, and «circle», are colourless
        self.assertEqual(s["kind_B_decline_rate"], 1.0)
        self.assertEqual(s["kind_A_spoken"], 1.0)
        self.assertEqual(s["kind_A_truth"], 0.5)                                # «red circle» is false of a purple circle


if __name__ == "__main__":
    unittest.main()
