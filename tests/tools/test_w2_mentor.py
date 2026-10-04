"""PREREG-W2 (SIGNED x3) — the mentor generator's tests, written FIRST (red).

# edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:00 +0400 — new file for the W2 build; law
# docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §2 (the carriers C1-C5, the referent rule, the seat decisions).

  C1: the referent is the thing holding the MOST fixated cells (ties by the per-canvas substream); a canvas with
  NO fixated thing is SILENT for C1/C3 (never names unattended). C2 names an UNSEEN thing (in the truth spec,
  never fixated), never a fixated one. C3: runs of >= 3 utterances, one carrier, one position changed, over the
  canvas's different things, FRONT-LOADED (the declared schedule). C4: the mirror tokens land on the state's OWN
  canvas. C5: confirm after a true say / correct after a not-true say / re-name after an ask — the answer is
  built from the REFERENT (never copied from the organism's sentence: the self-voice rule by construction).
  Every row: source "mentor", a tpl of the frozen v1 set, one word a row, the ear's alphabet.
"""
from __future__ import annotations

import unittest

from brain.world.seeds import substream
from creature.senses import mentor as M

STAR = M.Thing(shape="star", colour="blue", size="big", top=4, left=30)
CROSS = M.Thing(shape="cross", colour="blue", size="small", top=104, left=81)
RING = M.Thing(shape="ring", colour="red", size="small", top=60, left=60)
SQUARE = M.Thing(shape="square", colour="green", size="big", top=20, left=100)


def canvas(moment="sc20261101t000000", things=(STAR, CROSS), fix=((4, 4),), state=None, say=None, ask_target=None, order=0):
    st = {"doubt": 0, "young": 0, "ask_prev": 0}
    if state:
        st.update(state)
    return M.Canvas(moment=moment, things=list(things), fix=[list(c) for c in fix], state=st, say=say,
                    ask_target=ask_target, order=order)


def rows(c, seed=1):
    return M.mentor_rows(c, substream(seed, f"test:{c.order}"))


def words(rs):
    return [r["meta"]["word"] for r in rs]


class TestReferent(unittest.TestCase):
    def test_most_fixated_cells_wins(self):
        c = canvas(things=(STAR, CROSS), fix=[list(p) for p in STAR.cells()][:3])
        self.assertEqual(M.referent(c), 0)
        c2 = canvas(things=(STAR, CROSS), fix=[list(p) for p in CROSS.cells()][:2])
        self.assertEqual(M.referent(c2), 1)

    def test_a_canvas_with_no_fixated_thing_is_silent_for_c1_and_c3(self):
        c = canvas(things=(STAR, CROSS), fix=((15, 15),), order=0)     # an empty corner, and order 0 is a run-due one
        rs = rows(c)
        self.assertFalse(any(r["meta"]["tpl"].startswith("M-C1") for r in rs))
        self.assertFalse(any(r["meta"]["tpl"] == "M-C3" for r in rs))
        self.assertIsNone(M.referent(c))

    def test_c1_names_the_referent_truly(self):
        c = canvas(things=(STAR, CROSS), fix=((4, 4),), order=1)
        rs = [r for r in rows(c) if r["meta"]["tpl"].startswith("M-C1")]
        self.assertTrue(rs)
        self.assertEqual(words(rs), ["alpha", "sees"] + list(M.np_words(rs[0]["meta"]["tpl"].split("-")[-1], STAR)))
        self.assertTrue(all(w in ("alpha", "sees", "blue", "star", "big") for w in words(rs)))


class TestPolarity(unittest.TestCase):
    def test_c2_names_an_unseen_thing_never_a_fixated_one(self):
        c = canvas(things=(STAR, CROSS, RING), fix=[list(p) for p in STAR.cells()][:3])
        rs = [r for r in rows(c) if r["meta"]["tpl"].startswith("M-C2")]
        self.assertTrue(rs)
        ws = words(rs)
        self.assertEqual(ws[:4], ["alpha", "does", "not", "see"])
        self.assertNotIn("star", ws)                                  # the fixated thing is never the unseen one

    def test_c2_is_silent_when_everything_is_seen(self):
        c = canvas(things=(STAR,), fix=[list(p) for p in STAR.cells()][:2])
        self.assertFalse(any(r["meta"]["tpl"].startswith("M-C2") for r in rows(c)))


class TestVariationSets(unittest.TestCase):
    def test_a_run_is_three_utterances_one_carrier_one_position_changed(self):
        c = canvas(things=(STAR, CROSS, RING), fix=((4, 4), (13, 10), (8, 8)), order=0)     # due
        rs = [r for r in rows(c) if r["meta"]["tpl"] == "M-C3"]
        self.assertTrue(rs)
        prods = M.productions(rs)
        self.assertGreaterEqual(len(prods), 3)
        heads = [p[-1] for p in prods]                                # the head nouns of «alpha sees <NP>»
        self.assertEqual(len(set(heads)), 3)                          # over three different things
        self.assertTrue(all(p[:2] == ["alpha", "sees"] for p in prods))

    def test_a_two_thing_run_is_a_b_a(self):
        c = canvas(things=(STAR, CROSS), fix=((4, 4), (13, 10)), order=0)
        prods = M.productions([r for r in rows(c) if r["meta"]["tpl"] == "M-C3"])
        self.assertEqual(len(prods), 3)
        self.assertEqual(prods[0], prods[2])
        self.assertNotEqual(prods[0], prods[1])

    def test_a_not_due_canvas_has_no_run_but_keeps_c1(self):
        c = canvas(things=(STAR, CROSS, RING), fix=((4, 4), (13, 10), (8, 8)), order=1)
        rs = rows(c)
        self.assertFalse(any(r["meta"]["tpl"] == "M-C3" for r in rs))
        self.assertTrue(any(r["meta"]["tpl"].startswith("M-C1") for r in rs))

    def test_the_schedule_is_front_loaded(self):
        self.assertLess(M.run_every(0), M.run_every(1000))
        self.assertLess(M.run_every(1000), M.run_every(3000))
        self.assertEqual(M.run_every(10_000), 48)


class TestMirrorAndAnswers(unittest.TestCase):
    def test_the_mirror_tokens_land_on_the_states_own_canvas(self):
        c = canvas(things=(STAR,), fix=((4, 4),), state={"doubt": 1, "young": 1, "ask_prev": 1})
        rs = rows(c)
        got = {r["meta"]["word"]: r["meta"]["tpl"] for r in rs if r["meta"]["tpl"].startswith("M-M")}
        self.assertEqual(got, {"unsure": "M-M1", "fresh": "M-M2", "asked": "M-M3"})
        self.assertTrue(all(r["meta"]["moment"] == c.moment for r in rs))

    def test_confirm_after_a_true_say_and_correct_after_a_not_true_one(self):
        c_true = canvas(things=(STAR,), fix=((4, 4),), say=["star"])
        c_false = canvas(things=(STAR,), fix=((4, 4),), say=["circle"])
        self.assertTrue(any(r["meta"]["tpl"] == "M-A1" for r in rows(c_true)))
        self.assertFalse(any(r["meta"]["tpl"] == "M-A2" for r in rows(c_true)))
        self.assertTrue(any(r["meta"]["tpl"] == "M-A2" for r in rows(c_false)))
        self.assertFalse(any(r["meta"]["tpl"] == "M-A1" for r in rows(c_false)))

    def test_the_answer_is_built_from_the_referent_never_copied(self):
        c1 = canvas(things=(STAR,), fix=((4, 4),), say=["blue", "star"])      # a true say in T2's words
        c2 = canvas(things=(STAR,), fix=((4, 4),), say=["star"])              # a true say in T1's words
        a1 = M.productions([r for r in rows(c1) if r["meta"]["tpl"] == "M-A1"])
        a2 = M.productions([r for r in rows(c2) if r["meta"]["tpl"] == "M-A1"])
        self.assertEqual(a1, a2)                                              # the answer does not depend on the say's words

    def test_the_answer_to_an_ask_names_the_asked_thing(self):
        c = canvas(things=(STAR, CROSS), fix=((4, 4),), ask_target=1)
        prods = M.productions([r for r in rows(c) if r["meta"]["tpl"] == "M-A3"])
        self.assertEqual(len(prods), 1)
        self.assertIn("cross", prods[0])


class TestRowDiscipline(unittest.TestCase):
    def test_every_row_is_an_ear_row_with_source_tpl_and_a_legal_word(self):
        c = canvas(things=(STAR, CROSS, RING), fix=((4, 4), (13, 10), (8, 8)), state={"doubt": 1, "young": 1, "ask_prev": 1},
                   say=["star"], ask_target=2, order=0)
        for r in rows(c):
            self.assertEqual(r["sense"], "ear")
            self.assertEqual(r["meta"]["source"], "mentor")
            self.assertIn(r["meta"]["tpl"], M.TEMPLATES_V1)
            w = r["meta"]["word"]
            self.assertTrue(w.isalpha() and w.islower() and len(w) <= 8, w)


if __name__ == "__main__":
    unittest.main()
