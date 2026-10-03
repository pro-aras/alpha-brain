# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:17 +0400 — found by the bench's read stage: tools/brain/grade_life.py crashed on the ON arm's journal («WorldError: not a word of this world: 'arrow'»). The grader was written for a brain that hears ONE
# world, so every word of a learned type and of a said phrase was a scene word; with `hears scene maker` the brain's types hold the maker's words (arrow, bar, diamond …) and it may SAY one on a scene canvas.
# The scene world cannot type those words, so the grader adapts them HERE (never in the scored modules): a type is voted by the words the world knows, a type with none is skipped and counted, and a foreign word in a SAID
# phrase is read as the world's one shape word that is true of nothing a SPEAK, SPEAK2 or DECLINE scene shows (dax; the moon is drawn only in training scene 2,700 and in M6's scenes, and M6 takes no said phrase), counted.
# The tests run the SCORED functions on the adapted phrase.
"""tests/tools/test_grade_foreign_words.py — tools/brain/grade_life.py's handling of words the scene world cannot type."""
from __future__ import annotations

import unittest

from brain.scene import marks as M
from brain.scene import world as W
from tools.brain import grade_life as G


def things():
    return [W.Thing("circle", "red", "big", 0, 0), W.Thing("star", "blue", "small", 0, 0)]


class TypeKeys(unittest.TestCase):
    def test_a_learned_type_holding_the_makers_words_is_still_the_shape_type(self) -> None:
        key = "arrow|bar|circle|cross|diamond|dot|ring|square|star|triangle|wave"
        self.assertEqual(G.world_type_of_key(key), "shape")          # the vote is over the words the world knows (it raised on «arrow» before)

    def test_a_key_of_scene_words_only_is_what_it_was(self) -> None:
        self.assertEqual(G.world_type_of_key("blue|green|red|white|yellow"), "colour")
        self.assertEqual(G.world_type_of_key("big|small"), "size")
        self.assertEqual(G.world_type_of_key("shape"), "shape")        # a world type name passes through

    def test_a_type_with_no_word_of_the_world_has_no_world_type(self) -> None:
        self.assertIsNone(G.world_type_of_key("arrow|bar|wave"))

    def test_the_name_road_skips_a_type_of_foreign_words_and_counts_it(self) -> None:
        raw = {"name": {"circle|cross|star|arrow": "star", "blue|red": "red", "big|small": "big", "arrow|bar": "bar"}}
        out, skipped = G.name_by_world_type(raw, count=True)
        self.assertEqual(out["name"], {"shape": "star", "colour": "red", "size": "big"})
        self.assertEqual(skipped, 1)
        again = G.name_by_world_type(raw)                              # the default call returns the raw as before (a dict)
        self.assertEqual(again["name"], out["name"])

    def test_two_learned_types_for_one_world_type_is_still_an_error(self) -> None:
        with self.assertRaises(G.GradeError):
            G.name_by_world_type({"name": {"circle|star": "star", "cross|square|arrow": "cross"}})


class SaidPhrases(unittest.TestCase):
    def test_a_foreign_word_becomes_the_world_word_that_is_true_of_nothing_in_view_and_is_counted(self) -> None:
        out, n = G.world_words(["big", "arrow"])
        self.assertEqual((out, n), (["big", W.DAX_WORD], 1))
        self.assertEqual(G.world_words(["big", "circle"]), (["big", "circle"], 0))            # a world phrase is unchanged

    def test_the_scored_functions_run_on_the_adapted_phrase_and_read_it_as_a_wrong_shape(self) -> None:
        sp, _ = G.world_words(["big", "arrow"])
        self.assertTrue(M.in_parent_order(sp))                          # size before shape: in the parent's order, and no WorldError
        self.assertFalse(M.unique_true(sp, things(), 0, range(2)))       # «big arrow» is true of nothing: not TRUE
        sp2, _ = G.world_words(["arrow", "big"])
        self.assertFalse(M.in_parent_order(sp2))                         # a shape before a size: out of order, as the phrase said it
        with self.assertRaises(W.WorldError):
            M.in_parent_order(["big", "arrow"])                          # the unadapted phrase is what crashed the grader

    def test_a_single_foreign_word_phrase_is_not_true_of_the_target(self) -> None:
        sp, n = G.world_words(["arrow"])
        self.assertEqual((sp, n), ([W.DAX_WORD], 1))
        self.assertFalse(M.unique_true(sp, things(), 0, range(2)))

    def test_the_dax_stand_in_is_true_of_no_thing_a_said_phrase_is_graded_against(self) -> None:
        # PIN BY ENUMERATION (edit 12:28 +0400; the first wording said «a sitting» and M6's sitting DOES show the moon): the stand-in must not accidentally be TRUE of a thing a said phrase is
        # graded against. Those are the SPEAK, SPEAK2 and DECLINE scenes (the only marks that take a said phrase); the moon (the dax shape) is drawn only in training scene 2,700 and in M6's scenes.
        seeds = sorted(set(W.TEST_SEEDS.values()) | set(W.FRESH_TEST_SEEDS.values()))
        seen_things = 0
        for seed in seeds:
            for split in ("speak", "speak2", "decline"):
                for sc in W.scenes_for(split, seed):
                    for t in sc.things:
                        seen_things += 1
                        self.assertFalse(W.word_true_of(W.DAX_WORD, t), (seed, split, sc.index))
        self.assertGreater(seen_things, 2000)                                                  # a presence count: the enumeration walked things, it did not pass over nothing
        # the PLANT that the check can see a moon: M6's scenes carry it, and there the stand-in WOULD be true
        m6 = [t for sc in W.scenes_for("m6", seeds[0]) for t in sc.things if t.shape == W.DAX_SHAPE]
        self.assertGreater(len(m6), 0)
        self.assertTrue(W.word_true_of(W.DAX_WORD, m6[0]))


if __name__ == "__main__":
    unittest.main()
