# edit: Claude (Fable 5.1), 2026-09-22 19:2x +0400 — the ONE life's reader marks (PREREG §19.5/§19.10/§19.11; plan L-1): each must read
# «not gradable» on a record whose life did not declare the line, and grade on synthetic rows shaped like builder D's landed code.
import unittest


def _tape_game(n_mind, n_sched, reward=0.0):
    rows = [{"seq": 1, "sense": "eye", "meta": {"source": "game", "act_names": ["left", "right", "forward"], "n_actions": 3}}]
    s = 2
    for i in range(n_mind):
        rows.append({"seq": s, "sense": "outcome", "meta": {"source": "game", "chosen_by": "mind", "act": ["left", "right", "forward"][i % 3], "act_idx": i % 3, "got": reward, "terminated": (i % 10 == 9), "truncated": False}}); s += 1
    for i in range(n_sched):
        rows.append({"seq": s, "sense": "outcome", "meta": {"source": "game", "chosen_by": "schedule", "act": "left", "act_idx": 0, "got": 0.0}}); s += 1
    return rows


class ActMark(unittest.TestCase):
    def test_not_gradable_without_game_rows_and_without_mind_choices(self):
        from tools.verdict_life import act_mark
        self.assertFalse(act_mark([], [], {})["graded"])
        m = act_mark(_tape_game(0, 120), [], {})
        self.assertFalse(m["graded"]); self.assertIn("schedule", m["reason"])

    def test_graded_pass_on_a_mind_driven_tape(self):
        from tools.verdict_life import act_mark
        journal = [{"seq": i, "act": {"act": ["left", "right", "forward"][i % 3]}} for i in range(120)]
        m = act_mark(_tape_game(120, 0), journal, {"acts_chosen": {"left": 40, "right": 40, "forward": 40}, "act_mismatches": 0})
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["mind_share"], 1.0); self.assertEqual(m["zero_acts"], [])

    def test_a_mismatch_or_a_dead_act_fails(self):
        from tools.verdict_life import act_mark
        m = act_mark(_tape_game(120, 0), [{"seq": 5, "outcome": {"act_mismatch": True}}], {"acts_chosen": {"left": 120, "right": 0, "forward": 0}})
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"]); self.assertEqual(m["mismatches_journal"], 1); self.assertEqual(sorted(m["zero_acts"]), ["forward", "right"])

    def test_shift_acts_moves_only_mind_chosen_game_outcomes_and_keeps_the_input(self):
        from tools.verdict_life import shift_acts
        rows = _tape_game(3, 1); before = [dict(r["meta"]) for r in rows]
        out = shift_acts(rows)
        self.assertEqual([r["meta"]["act_idx"] for r in out if r["sense"] == "outcome"], [1, 2, 0, 0])
        self.assertEqual([r["meta"]["act"] for r in out if r["sense"] == "outcome"], ["right", "forward", "left", "left"])
        self.assertEqual([r["meta"] for r in rows], before)     # pure


class SoundMark(unittest.TestCase):
    def test_silent_world_is_not_gradable_and_a_heard_world_grades(self):
        from tools.verdict_life import sound_mark
        self.assertFalse(sound_mark([], [], {})["graded"])
        tape = [{"seq": 1, "sense": "ear-sound", "meta": {"when": 0.5}}, {"seq": 2, "sense": "ear-sound", "meta": {"when": 0.9}}]
        ok = sound_mark(tape, [{"sound": {"moment": "a"}}, {"sound": {"moment": "b"}}], {"sound_events": 2})
        self.assertTrue(ok["graded"]); self.assertTrue(ok["pass"])
        bad = sound_mark(tape, [{"sound": {"moment": "a"}}, {"sound": {"error": "x"}}], {})
        self.assertTrue(bad["graded"]); self.assertFalse(bad["pass"])


class SizingMark(unittest.TestCase):
    def test_not_gradable_without_a_prediction_or_an_old_body(self):
        from tools.verdict_life import sizing_mark
        self.assertFalse(sizing_mark({"sight_born": 10, "sight_nmax": 100}, [], None)["graded"])
        self.assertFalse(sizing_mark({}, [], 1000)["graded"])

    def test_graded_band_refusals_and_the_plants_birth(self):
        from tools.verdict_life import sizing_mark
        j = [{"moment": "w1", "when": "2026-09-23T12:00:00Z", "word": "circle", "births": [["sight", 1, "novelty"]]},
             {"moment": "w2", "when": "2026-09-23T13:00:00Z", "word": "zog", "births": [["sight", 2, "novelty"], ["words", 0, "novelty"]]}]
        ok = sizing_mark({"sight_born": 1000, "sight_nmax": 4000, "births_refused_nmax": 0}, j, 1000)
        self.assertTrue(ok["graded"]); self.assertTrue(ok["pass"]); self.assertEqual(ok["series_sight_births_per_hour"], [1, 1]); self.assertEqual(ok["plant_sight_births"], 1)
        self.assertFalse(sizing_mark({"sight_born": 3000, "sight_nmax": 4000, "births_refused_nmax": 0}, j, 1000)["pass"])   # over the band
        self.assertFalse(sizing_mark({"sight_born": 1000, "sight_nmax": 4000, "births_refused_nmax": 5}, j, 1000)["pass"])   # refused at the cap


class GradeMark(unittest.TestCase):
    """PREREG §19.3 against builder A's landed shapes: `graded` counts {sure_bare, unsure, abstain_with_resemblance, abstain} on the
    reader's own plant/null asks, `hedge_rate` on the seen-words Q1."""

    def test_not_gradable_without_graded_counts(self):
        from tools.verdict_life import grade_mark
        m = grade_mark({"answered_rate": 0.4, "abstain_rate": 0.6, "n": 10}, {"abstain_rate": 0.5, "n": 10}, {"Q1": {"acc": 0.98}}, "ANSWER" in {})
        self.assertFalse(m["graded"])

    def test_null_and_plant_bars(self):
        from tools.verdict_life import grade_mark
        plant = {"answered_rate": 0.7, "n": 10, "graded": {"sure_bare": 7, "unsure": 1, "abstain_with_resemblance": 2, "abstain": 0}}
        null = {"answered_rate": 0.0, "n": 10, "graded": {"sure_bare": 0, "unsure": 7, "abstain_with_resemblance": 3, "abstain": 0}}
        seen = {"Q1": {"acc": 0.98, "hedge_rate": 0.426}}
        m = grade_mark(plant, null, seen, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["null_sure_bare"], 0); self.assertEqual(m["hedge_rate"], 0.426)
        tie = dict(null, graded={"sure_bare": 5, "unsure": 3, "abstain_with_resemblance": 2, "abstain": 0})
        self.assertFalse(grade_mark(plant, tie, seen, True)["pass"])            # 5/10 sure-bare is a FAIL, never a tie
        weak = dict(plant, graded={"sure_bare": 5, "unsure": 3, "abstain_with_resemblance": 2, "abstain": 0})
        self.assertFalse(grade_mark(weak, null, seen, True)["pass"])            # the plant must be answered SURE ≥ 6/10


class SelfMark(unittest.TestCase):
    """PREREG §19.6 against builder A's shapes: belief rows whose word starts with `self:`, cells [], episodes = two body-row seqs."""

    def test_not_gradable_under_24_body_rows_or_without_the_gene(self):
        from tools.verdict_life import self_mark
        tape = [{"seq": i, "sense": "body", "meta": {}} for i in range(10)]
        self.assertFalse(self_mark(tape, [], [], {}, True)["graded"])
        self.assertFalse(self_mark([{"seq": i, "sense": "body", "meta": {}} for i in range(30)], [], [], {}, False)["graded"])

    def test_a_self_belief_citing_two_body_rows_passes(self):
        from tools.verdict_life import self_mark
        tape = [{"seq": i, "sense": "body", "meta": {}} for i in range(30)]
        bel = [{"word": "self:births_stopped", "kind": "belief", "cells": [], "episodes": [3, 4]}, {"word": "circle", "kind": "belief", "cells": [1], "episodes": [9]}]
        journal = [{"think": {"kind": "self", "outcome": "belief"}}, {"think": {"kind": "self", "outcome": "no_change"}}]
        m = self_mark(tape, bel, journal, {"think_skipped_for_backlog": 2}, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["self_beliefs"], 1); self.assertEqual(m["self_thinks"], 2); self.assertEqual(m["think_skipped_for_backlog"], 2)
        bad = [{"word": "self:no_room", "kind": "belief", "cells": [], "episodes": [3]}]     # one row cited, not two
        self.assertFalse(self_mark(tape, bad, journal, {}, True)["pass"])
        self.assertFalse(self_mark(tape, [], journal, {}, True)["pass"])


def _moments(shares_by_window, canvases_per_window=200, words=("circle",), new_words_at=()):
    """journal moment rows: one row per canvas (glance 0 only, for brevity) with `confirmed` drawn deterministically to hit each
    window's (first-half, second-half) shares; `when` marks the hour; new words first appear at the given window indexes."""
    rows = []; seq = 0
    for w, (s1, s2) in enumerate(shares_by_window):
        for c in range(canvases_per_window):
            half = 0 if c < canvases_per_window // 2 else 1
            share = (s1, s2)[half]
            confirmed = (c % 100) < int(round(share * 100))
            word = f"new{w}" if (w in new_words_at and c < 5) else words[c % len(words)]
            rows.append({"seq": seq, "moment": f"w{w:04d}i{c:06d}", "word": word, "when": f"2026-09-23T{(w * 4) % 24:02d}:{(c * 60 // canvases_per_window) % 60:02d}:00Z",
                         "glance": 0, "confirmed": confirmed, "residual": 0.0 if confirmed else 0.3, "births": []}); seq += 1
    return rows


class SurpriseMark(unittest.TestCase):
    """PREREG §19.1 against builder B's shapes: `confirmed` on every eye moment row; STATUS glances_confirmed/glances_surprised."""

    def test_not_gradable_without_confirmed_rows(self):
        from tools.verdict_life import surprise_mark
        self.assertFalse(surprise_mark([{"seq": 1, "moment": "a", "glance": 0, "word": "x"}], {}, 200, True)["graded"])
        self.assertFalse(surprise_mark(_moments([(0.4, 0.6)]), {}, 200, False)["graded"])

    def test_rises_within_windows_and_drops_at_new_thing_boundaries(self):
        from tools.verdict_life import surprise_mark
        rows = _moments([(0.40, 0.60), (0.30, 0.55), (0.45, 0.62), (0.35, 0.58), (0.44, 0.61), (0.36, 0.57)], new_words_at=(1, 3))
        m = surprise_mark(rows, {"glances_confirmed": 10, "glances_surprised": 10}, 200, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["windows_rising"], 6); self.assertEqual(sorted(m["new_thing_windows"]), [1, 3])
        flat = surprise_mark(_moments([(0.5, 0.5)] * 6, new_words_at=(1,)), {}, 200, True)
        self.assertTrue(flat["graded"]); self.assertFalse(flat["pass"])


class CoarseMark(unittest.TestCase):
    """PREREG §19.4: Q1 on all words ≥ 0.975 beside the blind-coarse twin; the house prediction printed."""

    def test_not_gradable_without_the_gene_or_the_twin(self):
        from tools.verdict_life import coarse_mark
        self.assertFalse(coarse_mark({"Q1": {"acc": 0.98, "per_thing": {"house": 0.9}}}, None, True)["graded"])
        self.assertFalse(coarse_mark({"Q1": {"acc": 0.98, "per_thing": {}}}, {"Q1": {"acc": 0.9, "per_thing": {}}}, False)["graded"])

    def test_bar_and_the_house_prediction(self):
        from tools.verdict_life import coarse_mark
        live = {"Q1": {"acc": 0.98, "per_thing": {"house": 0.9, "cup": 0.3}}}; twin = {"Q1": {"acc": 0.95, "per_thing": {"house": 0.5, "cup": 0.3}}}
        m = coarse_mark(live, twin, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertTrue(m["house_prediction_held"]); self.assertEqual(m["cup_live"], 0.3)
        self.assertFalse(coarse_mark({"Q1": {"acc": 0.96, "per_thing": {}}}, twin, True)["pass"])


class QuestionMark(unittest.TestCase):
    """PREREG §19.7 against builder C's shapes: journal `question` rows; tape rows with meta `answering`; STATUS questions_written/answered."""

    def test_not_gradable_without_the_gene_or_under_two_hours(self):
        from tools.verdict_life import question_mark
        self.assertFalse(question_mark([], [], {}, 24.0, False)["graded"])
        self.assertFalse(question_mark([{"seq": 1, "question": {"q": "what-is"}}], [], {}, 1.5, True)["graded"])

    def test_rate_after_hour_two_and_the_answered_share(self):
        from tools.verdict_life import question_mark
        journal = [{"seq": i, "question": {"q": "what-is", "args": ["w%d" % i]}, "when": "2026-09-23T%02d:00:00Z" % (3 + i % 20)} for i in range(24)]
        tape = [{"seq": 100 + i, "sense": "eye", "meta": {"source": "maker", "answering": "q-%d" % i}} for i in range(12)]
        m = question_mark(journal, tape, {"questions_written": 24, "questions_answered": 12}, 24.0, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["questions"], 24); self.assertEqual(m["answered_rows"], 12); self.assertAlmostEqual(m["answered_share"], 0.5)
        few = question_mark(journal[:5], tape, {}, 24.0, True)
        self.assertTrue(few["graded"]); self.assertFalse(few["pass"])


class SentenceMark(unittest.TestCase):
    """PREREG §19.8 with its ceiling clause: the world's own pair skew from the game's mission ear rows; graded only when a frame can exist."""

    def _tape(self, missions):
        rows = []
        for i, (c, o) in enumerate(missions):
            rows.append({"seq": 3 * i, "sense": "ear", "meta": {"source": "game", "word": c, "mission": f"go to the {c} {o}"}})
            rows.append({"seq": 3 * i + 1, "sense": "ear", "meta": {"source": "game", "word": o, "mission": f"go to the {c} {o}"}})
        return rows

    def test_independent_world_is_not_gradable_with_its_max_lift_printed(self):
        from tools.verdict_life import sentence_mark
        import itertools
        missions = [(c, o) for c, o in itertools.product(["red", "blue", "green"], ["ball", "key", "box"])] * 15   # 135 missions, uniform
        m = sentence_mark(self._tape(missions), {"frames_filed": 0, "frames_scored": 0, "frames_true": 0}, True)
        self.assertFalse(m["graded"]); self.assertLess(m["max_lift"], 2.0); self.assertEqual(m["missions"], 135)

    def test_skewed_world_grades_on_frames_and_precision(self):
        from tools.verdict_life import sentence_mark
        # a world with STRUCTURE: each colour keeps its object (lift 3.0 at 1/3 × 1/3), plus a little noise — C's arithmetic: a single
        # skewed pair on an otherwise uniform grid caps near 1.33×, so structure, not repetition, is what buys lift over 2×
        missions = [("red", "ball")] * 50 + [("blue", "key")] * 50 + [("green", "box")] * 50 + [("red", "key")] * 3 + [("blue", "box")] * 3 + [("green", "ball")] * 3
        tape = self._tape(missions)
        m = sentence_mark(tape, {"frames_filed": 4, "frames_scored": 4, "frames_true": 4}, True)
        self.assertTrue(m["graded"]); self.assertGreaterEqual(m["max_lift"], 2.0); self.assertTrue(m["pass"])
        self.assertFalse(sentence_mark(tape, {"frames_filed": 2, "frames_scored": 2, "frames_true": 2}, True)["pass"])          # < 3 frames
        self.assertFalse(sentence_mark(tape, {"frames_filed": 4, "frames_scored": 4, "frames_true": 2}, True)["pass"])          # precision .5
        self.assertFalse(sentence_mark(tape[:100], {"frames_filed": 4, "frames_scored": 4, "frames_true": 4}, True)["graded"])  # < 100 missions


if __name__ == "__main__":
    unittest.main()
