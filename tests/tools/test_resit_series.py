# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:37 +0400 — PREREG-RESIT-READER (law v4 text): the SERIES helpers of daily and origin rows — the phrase-class tables of §2 built from the grader's own per-item rows, the
# per-item vectors the pairing of §4 reads, R6's partition check against the grade's own aggregates, and the grader/life genome line hashes of §1.2 (v4) with EYE-CHANGED's two forms.
# Written BEFORE the code. Every plant asserts that it changed the bytes (#247 (5)) and is CAUGHT.
"""tests/tools/test_resit_series.py — class tables, vectors, the partition check (R6), the genome lines and EYE-CHANGED."""
from __future__ import annotations

import copy
import unittest

from tools.brain import resit as R

SETS = ("fresh", "s1b1")


def asks_fixture():
    """Three marks in two sets, a class for every M1 / M2a / M3 item (M2a and M3 hold no shape-only item, as the real record does)."""
    out = []
    n = 0
    for s in SETS:
        for i, (phrase, cls) in enumerate([(["circle"], "shape_only"), (["red", "star"], "colour_or_size"), (["white", "cross"], "white"), (["big", "ring"], "colour_or_size")]):
            out.append({"item": f"M1:{s}:{i}", "mark": "M1", "set": s, "phrase": phrase, "class": cls, "form": "point"})
        for i, (phrase, cls) in enumerate([(["red", "star"], "colour_or_size"), (["white", "cross"], "white")]):
            out.append({"item": f"M2a:{s}:{i}", "mark": "M2a", "set": s, "phrase": phrase, "class": cls, "form": "point"})
        for i, (phrase, cls) in enumerate([(["green", "circle"], "colour_or_size")]):
            out.append({"item": f"M3:{s}:{i}", "mark": "M3", "set": s, "phrase": phrase, "class": cls, "form": "point"})
        out.append({"item": f"M4:{s}", "mark": "M4", "set": s, "phrase": None, "form": "why"})      # no class: not a class mark
        n += 1
    return out


def grade_fixture():
    """The real grade.json's shape, small: items rows for M1 and M3, aggregates under sets.<s>.marks, M2a under roads.LAW."""
    g = {"items": {}, "sets": {}}
    for s in SETS:
        m1 = [{"item_id": f"M1:{s}:0", "gradable": True, "covered": True, "correct": True, "n_things": 2},
              {"item_id": f"M1:{s}:1", "gradable": True, "covered": True, "correct": False, "n_things": 3},
              {"item_id": f"M1:{s}:2", "gradable": True, "covered": False, "correct": False, "n_things": 2},      # not covered: left out of the covered rate
              {"item_id": f"M1:{s}:3", "gradable": False, "covered": True, "correct": False, "n_things": 2}]      # unheard: not gradable, left out
        m3 = [{"item_id": f"M3:{s}:0", "gradable": True, "covered": True, "correct": True, "n_things": 2}]
        g["items"][s] = {"M1": m1, "M3": m3, "M6": []}
        g["sets"][s] = {"marks": {"M1": {"graded": {"n_covered": 2, "covered": 0.5}}, "M3": {"all": {"n_covered": 1, "covered": 1.0}},
                                  "roads": {"LAW": {"M2a": {"all": {"n": 2, "refusal": 0.5}}}}}}
    return g


def m2a_fixture():
    return {s: [{"item_id": f"M2a:{s}:0", "answered": True, "refused": True}, {"item_id": f"M2a:{s}:1", "answered": True, "refused": False}] for s in SETS}


class TestItemClasses(unittest.TestCase):
    def test_a_class_is_mapped_by_item_name_for_the_three_class_marks_only(self) -> None:
        m = R.item_class_map(asks_fixture())
        self.assertEqual(m["M1:fresh:0"], "shape_only")
        self.assertEqual(m["M2a:s1b1:1"], "white")
        self.assertEqual(m["M3:fresh:0"], "colour_or_size")
        self.assertNotIn("M4:fresh", m)
        self.assertEqual(len([k for k in m if k.startswith("M1:")]), 8)


class TestRecords(unittest.TestCase):
    def test_records_carry_the_class_and_the_graded_population_flags(self) -> None:
        rec = R.records_from_grade(grade_fixture(), m2a_fixture(), R.item_class_map(asks_fixture()))
        self.assertEqual(set(rec), {"M1", "M2a", "M3"})
        r = {x["item"]: x for x in rec["M1"]["fresh"]}
        self.assertEqual((r["M1:fresh:0"]["in_g"], r["M1:fresh:0"]["correct"], r["M1:fresh:0"]["class"]), (True, True, "shape_only"))
        self.assertFalse(r["M1:fresh:2"]["in_g"], "an item the gaze did not cover is not in the covered population")
        self.assertFalse(r["M1:fresh:3"]["in_g"], "an unheard (not gradable) item is not in it either")
        self.assertTrue(r["M1:fresh:3"]["covered"] and not r["M1:fresh:3"]["gradable"])
        m2 = {x["item"]: x for x in rec["M2a"]["fresh"]}
        self.assertEqual((m2["M2a:fresh:0"]["in_g"], m2["M2a:fresh:0"]["correct"]), (True, True))
        self.assertEqual(m2["M2a:fresh:1"]["correct"], False)

    def test_an_item_with_no_class_is_refused_by_name_never_binned_R6(self) -> None:
        classes = R.item_class_map(asks_fixture())
        del classes["M1:fresh:1"]
        with self.assertRaises(R.ResitError) as cm:
            R.records_from_grade(grade_fixture(), m2a_fixture(), classes)
        self.assertIn("M1:fresh:1", str(cm.exception))
        self.assertIn("class", str(cm.exception))

    def test_an_unanswered_m2a_item_is_left_out_not_scored_wrong(self) -> None:
        m2 = m2a_fixture()
        m2["fresh"][0] = {"item_id": "M2a:fresh:0", "answered": False, "refused": None}
        rec = R.records_from_grade(grade_fixture(), m2, R.item_class_map(asks_fixture()))
        x = {r["item"]: r for r in rec["M2a"]["fresh"]}["M2a:fresh:0"]
        self.assertEqual((x["in_g"], x["correct"]), (False, False))


class TestGradedPopulation(unittest.TestCase):
    """The REAL grade's `M1.graded` is the 2- and 3-thing items only (brain/scene/marks.py summarise_pointing: «graded» = n_things >= 2, the bars read it; `all` adds the one-thing items).
    The law's own R6 figure (brain-long-2 M1 fresh: 202 covered of 244) is that block. A real-data daily run found the class tables counting 353 (every gradable covered item)."""

    def one_thing_world(self):
        g = grade_fixture()
        asks = asks_fixture()
        for s in SETS:
            g["items"][s]["M1"].append({"item_id": f"M1:{s}:4", "gradable": True, "covered": True, "correct": True, "n_things": 1})      # trivial: one thing in view
            asks.append({"item": f"M1:{s}:4", "mark": "M1", "set": s, "phrase": ["circle"], "class": "shape_only", "form": "point"})
        return g, asks

    def test_a_covered_gradable_one_thing_m1_item_is_not_in_the_graded_population(self) -> None:
        g, asks = self.one_thing_world()
        rec = R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks))
        x = {r["item"]: r for r in rec["M1"]["fresh"]}["M1:fresh:4"]
        self.assertEqual((x["gradable"], x["covered"], x["in_g"], x["graded"]), (True, True, False, False))
        t = R.class_tables(rec)["M1"]["sets"]["fresh"]["shape_only"]
        self.assertEqual((t["items"], t["n"], t["left_out"]), (2, 1, 1), "counted among the class's items, left out of its covered rate")

    def test_the_partition_holds_against_the_graded_aggregate_with_the_one_thing_items_present(self) -> None:
        g, asks = self.one_thing_world()
        rec = R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks))
        res = R.partition_check(rec, g)
        self.assertTrue(res["ok"], res)

    def test_the_old_reading_every_gradable_covered_item_breaks_the_partition_the_plant_is_caught(self) -> None:
        g, asks = self.one_thing_world()
        rec = R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks))
        bad = copy.deepcopy(rec)
        for r in bad["M1"]["fresh"]:
            r["in_g"] = r["gradable"] and r["covered"]                       # the defect: the one-thing item counted
        self.assertNotEqual([r["in_g"] for r in bad["M1"]["fresh"]], [r["in_g"] for r in rec["M1"]["fresh"]], "the plant must change the data")
        res = R.partition_check(bad, g)
        self.assertFalse(res["ok"])
        self.assertEqual([(r["mark"], r["set"]) for r in res["rows"] if not r["ok"]], [("M1", "fresh")])

    def test_a_row_with_no_n_things_is_refused_by_name_the_graded_split_cannot_be_guessed(self) -> None:
        g = grade_fixture()
        del g["items"]["fresh"]["M1"][0]["n_things"]
        with self.assertRaises(R.ResitError) as cm:
            R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks_fixture()))
        self.assertIn("n_things", str(cm.exception))


class TestTables(unittest.TestCase):
    def tables(self):
        return R.class_tables(R.records_from_grade(grade_fixture(), m2a_fixture(), R.item_class_map(asks_fixture())))

    def test_each_mark_has_a_table_per_set_and_pooled_with_k_n_and_the_smallest_gap(self) -> None:
        t = self.tables()
        m1 = t["M1"]
        self.assertEqual(set(m1), {"sets", "pooled"})
        f = m1["sets"]["fresh"]
        self.assertEqual((f["shape_only"]["n"], f["shape_only"]["k"], f["shape_only"]["items"]), (1, 1, 1))
        self.assertEqual((f["colour_or_size"]["items"], f["colour_or_size"]["n"], f["colour_or_size"]["k"], f["colour_or_size"]["left_out"]), (2, 1, 0, 1))
        self.assertEqual(f["white"]["n"], 0)
        p = m1["pooled"]
        self.assertEqual((p["shape_only"]["n"], p["shape_only"]["k"]), (2, 2), "pooled over fresh and s1b1")
        self.assertEqual(p["shape_only"]["smallest_gap"], 10 / 2)
        self.assertTrue(p["shape_only"]["underpowered"], "n 2 < 30 reads UNDERPOWERED by name")

    def test_an_empty_class_reads_na_never_zero(self) -> None:
        t = self.tables()
        cell = t["M2a"]["sets"]["fresh"]["shape_only"]
        self.assertTrue(cell["na"])
        self.assertIsNone(cell["rate"])
        self.assertEqual(cell["items"], 0)


class TestPartition(unittest.TestCase):
    def test_the_classes_sum_to_the_grades_own_aggregate_for_every_mark_and_set(self) -> None:
        rec = R.records_from_grade(grade_fixture(), m2a_fixture(), R.item_class_map(asks_fixture()))
        res = R.partition_check(rec, grade_fixture())
        self.assertTrue(res["ok"], res)
        keys = {(r["mark"], r["set"]) for r in res["rows"]}
        self.assertEqual(keys, {(m, s) for m in ("M1", "M2a", "M3") for s in SETS})
        r = next(x for x in res["rows"] if (x["mark"], x["set"]) == ("M1", "fresh"))
        self.assertEqual((r["n_classes"], r["n_agg"], r["k_classes"], r["k_agg"]), (2, 2, 1, 1))

    def test_a_class_that_loses_an_item_breaks_the_partition_and_is_caught_R6(self) -> None:
        g = grade_fixture()
        rec = R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks_fixture()))
        broken = copy.deepcopy(rec)
        broken["M1"]["fresh"] = [x for x in broken["M1"]["fresh"] if x["item"] != "M1:fresh:0"]     # the plant: one covered item vanishes
        self.assertNotEqual(len(broken["M1"]["fresh"]), len(rec["M1"]["fresh"]), "the plant must change the data")
        res = R.partition_check(broken, g)
        self.assertFalse(res["ok"])
        bad = [r for r in res["rows"] if not r["ok"]]
        self.assertEqual([(b["mark"], b["set"]) for b in bad], [("M1", "fresh")])
        with self.assertRaises(R.Refused) as cm:
            R.require_partition(res)
        self.assertIn("R6", str(cm.exception))

    def test_a_grade_aggregate_that_disagrees_with_the_items_is_caught(self) -> None:
        g = grade_fixture()
        rec = R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks_fixture()))
        g2 = copy.deepcopy(g)
        g2["sets"]["s1b1"]["marks"]["M1"]["graded"]["covered"] = 1.0       # k 2 of 2 where the items say 1 of 2
        self.assertNotEqual(g2["sets"]["s1b1"]["marks"]["M1"]["graded"], g["sets"]["s1b1"]["marks"]["M1"]["graded"])
        res = R.partition_check(rec, g2)
        self.assertFalse(res["ok"])


class TestVectors(unittest.TestCase):
    def test_vectors_are_one_zero_or_none_by_item_name_and_the_class_of_each_item_is_kept(self) -> None:
        rec = R.records_from_grade(grade_fixture(), m2a_fixture(), R.item_class_map(asks_fixture()))
        v = R.vectors_from_records(rec)
        self.assertEqual(v["vectors"]["M1"]["M1:fresh:0"], 1)
        self.assertEqual(v["vectors"]["M1"]["M1:fresh:1"], 0)
        self.assertIsNone(v["vectors"]["M1"]["M1:fresh:2"])
        self.assertIsNone(v["vectors"]["M1"]["M1:fresh:3"])
        self.assertEqual(v["vectors"]["M2a"]["M2a:fresh:0"], 1)
        self.assertEqual(v["vectors"]["M2a"]["M2a:s1b1:1"], 0)
        self.assertEqual(v["item_class"]["M1:s1b1:2"], "white")
        self.assertEqual(len(v["vectors"]["M1"]), 8)

    def test_a_pairing_through_these_vectors_reads_the_planted_fall(self) -> None:
        rec = R.records_from_grade(grade_fixture(), m2a_fixture(), R.item_class_map(asks_fixture()))
        origin = R.vectors_from_records(rec)
        g = grade_fixture()
        g["items"]["fresh"]["M1"][0]["correct"] = False                  # day t: the first covered item, right at the origin, is now wrong
        day = R.vectors_from_records(R.records_from_grade(g, m2a_fixture(), R.item_class_map(asks_fixture())))
        self.assertNotEqual(day["vectors"]["M1"], origin["vectors"]["M1"], "the plant must change the vector")
        res = R.pair_with_origin(day, origin)["vs_origin"]["M1"]["pooled"]
        self.assertEqual((res["b"], res["c"], res["n_paired"]), (1, 0, 4))
        self.assertAlmostEqual(res["g"], -0.25)
        shape = R.pair_with_origin(day, origin)["vs_origin"]["M1"]["shape_only"]
        self.assertEqual((shape["b"], shape["n_paired"]), (1, 2))


LIFE = "SEED 1\nRETINA a b c\nGAZE g 4\nSENSE colour rg\nBRAIN lr 0.01; hears scene\nWORLD scene seed 20261101; train 50000; sitting fresh s1b1\nTAPE run/tape\n"


class TestGraderLines(unittest.TestCase):
    def test_the_lines_the_grader_reads_are_hashed_and_the_brain_line_is_a_separate_reading(self) -> None:
        h = R.grader_line_hashes(LIFE)
        self.assertEqual(set(h), {"world_scene", "tape", "retina", "gaze", "colour", "brain", "genome"})
        h2 = R.grader_line_hashes(LIFE.replace("hears scene", "hears scene maker"))
        self.assertEqual({k: v for k, v in h.items() if k not in ("brain", "genome")}, {k: v for k, v in h2.items() if k not in ("brain", "genome")})
        self.assertNotEqual(h["brain"], h2["brain"])

    def test_a_comment_or_spacing_change_moves_no_line_hash(self) -> None:
        a = R.grader_line_hashes(LIFE)
        b = R.grader_line_hashes(LIFE.replace("GAZE g 4", "GAZE   g   4   # a comment"))
        self.assertEqual(a["gaze"], b["gaze"])


class TestEyeChanged(unittest.TestCase):
    def test_within_the_life_any_of_the_four_lines_differing_from_the_origin_is_form_i(self) -> None:
        a = R.grader_line_hashes(LIFE)
        for old, new, line in [("RETINA a b c", "RETINA a b d", "retina"), ("GAZE g 4", "GAZE g 5", "gaze"), ("SENSE colour rg", "SENSE colour gb", "colour"),
                               ("BRAIN lr 0.01; hears scene", "BRAIN lr 0.02; hears scene", "brain")]:
            b = R.grader_line_hashes(LIFE.replace(old, new))
            self.assertNotEqual(a[line], b[line], "the plant must change the line")
            res = R.eye_changed(b, origin=a, grader=a)
            self.assertTrue(res["within_life"], line)
            self.assertIn(line, res["within_life_lines"])
            self.assertTrue(res["eye_changed"])

    def test_against_the_grader_the_brain_line_is_not_compared_across_lives(self) -> None:
        grader = R.grader_line_hashes(LIFE)
        life = R.grader_line_hashes(LIFE.replace("hears scene", "hears scene maker"))
        res = R.eye_changed(life, origin=life, grader=grader)
        self.assertFalse(res["against_grader"], "the BRAIN line differs between the lives by the ladder's design and the grader never reads it")
        self.assertFalse(res["eye_changed"])
        self.assertNotEqual(res["brain_reading"]["life"], res["brain_reading"]["grader"])

    def test_against_the_grader_the_eye_the_world_scene_and_the_tape_lines_are_compared_form_ii(self) -> None:
        grader = R.grader_line_hashes(LIFE)
        for old, new, line in [("RETINA a b c", "RETINA a b d", "retina"), ("GAZE g 4", "GAZE g 5", "gaze"), ("SENSE colour rg", "SENSE colour gb", "colour"),
                               ("seed 20261101", "seed 20261102", "world_scene"), ("TAPE run/tape", "TAPE run/tape2", "tape")]:
            life = R.grader_line_hashes(LIFE.replace(old, new))
            self.assertNotEqual(grader[line], life[line], "the plant must change the line")
            res = R.eye_changed(life, origin=life, grader=grader)
            self.assertTrue(res["against_grader"], line)
            self.assertIn(line, res["against_grader_lines"])
            self.assertTrue(res["eye_changed"])

    def test_no_origin_yet_leaves_form_i_undetermined_never_false(self) -> None:
        a = R.grader_line_hashes(LIFE)
        res = R.eye_changed(a, origin=None, grader=a)
        self.assertIsNone(res["within_life"])
        self.assertFalse(res["against_grader"])
        self.assertFalse(res["eye_changed"], "nothing differs that can be compared")
        self.assertIn("NO ORIGIN", res["note"])


if __name__ == "__main__":
    unittest.main()
