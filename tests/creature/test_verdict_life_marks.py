# edit: Claude (Fable 5.1), 2026-09-22 19:2x +0400 — the ONE life's reader marks (PREREG §19.5/§19.10/§19.11; plan L-1): each must read
# «not gradable» on a record whose life did not declare the line, and grade on synthetic rows shaped like builder D's landed code.
import unittest

import numpy as np   # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:2x +0400 — ALPHA4-H task 4's ReadFrames/ReadMark tests


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
        # edit: Claude (Fable 5.1), 2026-09-22 22:24 +0400 — §19.3's plant clause RE-SPECIFIED before the life (#228 (b): a bar above its
        # ceiling): builder A's real-record grades (LIFE-A-REPORT.md §2: sure/unsure on held-out renders 10/0 … 0/10 per thing, hedge rate
        # 0.426) make «sure ≥ 6/10» a coin flip for a word seen five times. The plant's mark is the CELL — answered ≥ 6/10, G4's own (vi) —
        # with the grade distribution printed; the null's clauses (the grade's own mark) are unchanged.
        weak = dict(plant, answered_rate=0.8, graded={"sure_bare": 5, "unsure": 3, "abstain_with_resemblance": 2, "abstain": 0})
        m2 = grade_mark(weak, null, seen, True)
        self.assertTrue(m2["pass"], "the plant answered 8/10 with 5 of them «unsure» is a PASS: the cell is the mark, the grade is printed")
        self.assertEqual(m2["plant_sure"], 5); self.assertEqual(m2["plant_answered_rate"], 0.8)
        unlearned = dict(plant, answered_rate=0.5, graded={"sure_bare": 5, "unsure": 0, "abstain_with_resemblance": 3, "abstain": 2})
        self.assertFalse(grade_mark(unlearned, null, seen, True)["pass"])       # answered 5/10 is the FAIL (L5's cap shape, seam-1's 0/10)


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


def _showings(things, per_thing=(0.0, 0.0, 0.0) + (0.6,) * 197, first500=None, source="maker", extra=()):   # 5 things × 200 showings = 1,000 canvases, the mark's floor
    """edit: Claude (Fable 5.1), 2026-09-22 22:36 +0400 — journal moment rows shaped like builder B's LANDED code: `confirmed` is a LIST of four
    booleans per located glance (never a bare bool — a list is truthy whether or not one glance confirmed, the defect the first helper hid);
    things are shown in rotation, each showing's per-glance share drawn from `per_thing[k]` for its k-th showing (4 glances → shares in
    quarters). `first500`: an optional per-canvas share override for the first 500 canvases (the life-scale rise clause)."""
    rows = []; seq = 0; k = {t: 0 for t in things}; src = {}
    order = [t for _ in range(len(per_thing)) for t in things]
    for i, t in enumerate(order):
        share = per_thing[min(k[t], len(per_thing) - 1)]; k[t] += 1
        if first500 is not None and i < 500: share = first500
        n_ok = int(round(share * 4)); flags = [j < n_ok for j in range(4)]
        rows.append({"seq": seq, "moment": f"m{i:06d}", "word": t, "when": "2026-09-23T00:00:00Z", "confirmed": flags, "residual": [0.0] * 4, "births": []})
        src[seq] = source; seq += 1
    for t, flags_list, s2 in extra:
        for flags in flags_list:
            rows.append({"seq": seq, "moment": f"x{seq:06d}", "word": t, "when": "2026-09-23T00:00:00Z", "confirmed": flags, "residual": [0.0] * 4, "births": []}); src[seq] = s2; seq += 1
    return rows, src


class SurpriseMark(unittest.TestCase):
    """PREREG §19.1 as RE-SPECIFIED on 2026-09-22 22:3x from L1's real record replayed under SURPRISE (scratch/l1-surprise, builder B's recipe):
    (a) FIRST-SHOWING SURPRISE — for every maker thing with ≥ 30 showings, the per-glance confirmed share over its first 3 showings < over its
    last 20, for ≥ 80 % of them AND more than the shuffled null's p95 (L1: 16 of 16 maker things; the null 12 of 26 overall, p95 16);
    (b) the LIFE-SCALE RISE — the share over the last 500 canvases − the first 500 ≥ 0.10 (L1: 0.146; adjacent-500-bin sd 0.047);
    (c) the `--blind surprise` twin confirms 0 glances. The old window clauses are gone: on the record the world's arrival (64 % never-seen
    words in the next 100 canvases) moved the share +0.03 against a null band of sd 0.06, and the plant is 1 canvas in 100."""

    def test_not_gradable_without_confirmed_rows_or_the_gene(self):
        from tools.verdict_life import surprise_mark
        self.assertFalse(surprise_mark([{"seq": 1, "moment": "a", "word": "x"}], {}, True)["graded"])
        rows, src = _showings(["circle", "square"])
        self.assertFalse(surprise_mark(rows, {}, False, source_of=src)["graded"])

    def test_first_showings_surprised_later_confirmed_and_the_share_rises(self):
        from tools.verdict_life import surprise_mark
        things = ["circle", "square", "triangle", "cross", "ring"]
        rows, src = _showings(things, first500=0.25)       # 250 canvases in the first 500 read 0.25; the last 500 read 0.6
        twin = {"glances_confirmed": 0, "glances_surprised": 800}
        m = surprise_mark(rows, {"glances_confirmed": 500, "glances_surprised": 300}, True, source_of=src, twin_status=twin)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m)
        self.assertEqual(m["things_graded"], 5); self.assertEqual(m["things_rising"], 5)
        self.assertGreaterEqual(m["rise_first_to_last_500"], 0.10); self.assertEqual(m["twin_confirmed"], 0)
        self.assertGreater(m["things_rising"], m["null_p95"])
        self.assertIn("null_mean", m)

    def test_a_flat_record_fails_and_a_confirming_twin_fails(self):
        from tools.verdict_life import surprise_mark
        things = ["circle", "square", "triangle", "cross", "ring"]
        flat, src = _showings(things, per_thing=(0.5,) * 200)
        m = surprise_mark(flat, {}, True, source_of=src, twin_status={"glances_confirmed": 0})
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"]); self.assertEqual(m["things_rising"], 0)
        good, src2 = _showings(things, first500=0.25)
        self.assertFalse(surprise_mark(good, {}, True, source_of=src2, twin_status={"glances_confirmed": 12})["pass"])

    def test_a_word_shared_by_the_game_and_the_maker_is_graded_over_its_maker_rows_only(self):
        # edit: Claude (Fable 5.1), 2026-09-22 22:47 +0400 — the advisor's read: BabyAI's missions name «key», the maker's arrival brings «key»
        from tools.verdict_life import surprise_mark
        things = ["circle", "square", "triangle", "cross", "key"]
        rows, src = _showings(things, first500=0.25, extra=[("key", [[False] * 4] * 40, "game"), ("ball", [[False] * 4] * 40, "game")])
        m = surprise_mark(rows, {}, True, source_of=src, twin_status={"glances_confirmed": 0})
        self.assertTrue(m["pass"], m); self.assertEqual(m["things_graded"], 5); self.assertIn("key", m["things"])
        self.assertEqual(m["things"]["key"]["showings"], 200, "the game's 40 «key» frames must not enter the maker's «key» showings")
        self.assertEqual(m["by_source"]["game"]["things"], 2); self.assertEqual(m["by_source"]["game"]["share"], 0.0)
        self.assertIn("key@game", m["printed_not_graded"]); self.assertIn("ball@game", m["printed_not_graded"])
        # the row's OWN `source` wins over the tape map (a DELIVER journal carries it)
        rows2 = [dict(r, source=("game" if i % 2 else "maker")) for i, r in enumerate(rows[:1000])]
        m2 = surprise_mark(rows2, {}, True, source_of={}, twin_status={"glances_confirmed": 0})
        self.assertEqual(m2["by_source"]["game"]["glances"], 500 * 4); self.assertEqual(m2["by_source"]["maker"]["glances"], 500 * 4)

    def test_photographs_are_printed_not_graded_and_the_share_counts_glances(self):
        from tools.verdict_life import surprise_mark
        things = ["circle", "square", "triangle", "cross", "ring"]
        photos = [("anchor", [[False] * 4] * 30, "folder"), ("ant", [[False] * 4] * 30, "folder")]
        rows, src = _showings(things, first500=0.25, extra=photos)
        m = surprise_mark(rows, {}, True, source_of=src, twin_status={"glances_confirmed": 0})
        self.assertTrue(m["pass"]); self.assertEqual(m["things_graded"], 5, "the folder's things are printed, never graded (L1: 0 of 10 photographs confirm)")
        self.assertEqual(m["by_source"]["folder"]["share"], 0.0); self.assertEqual(m["by_source"]["folder"]["things"], 2)
        one_of_four, src3 = _showings(["circle"], per_thing=(0.25,) * 50)
        self.assertAlmostEqual(surprise_mark(one_of_four, {}, True, source_of=src3)["overall_share"], 0.25, places=3, msg="1 of 4 glances confirmed reads 0.25, never 1.0")


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


class HandsMark(unittest.TestCase):
    """PREREG §19.9 against builder F's shapes: eye rows `source: hands` with meta program/shape/control; STATUS runs_by_program, runs,
    hands_no_road, touch_events, smell_events; the reader's own asks give {asked, hits, shuffled_hits}."""

    def _rows(self, n):
        return [{"seq": i, "sense": "eye", "meta": {"source": "hands", "program": f"p{i}", "shape": ["circle", "square", "ring"][i % 3], "control": None}} for i in range(n)]

    def test_not_gradable_without_the_gene_or_under_20_runs(self):
        from tools.verdict_life import hands_mark
        self.assertFalse(hands_mark({}, self._rows(30), {"asked": 30, "hits": 25, "shuffled_hits": 10}, False)["graded"])
        m = hands_mark({"runs": 7}, self._rows(7), {"asked": 7, "hits": 7, "shuffled_hits": 2}, True)
        self.assertFalse(m["graded"]); self.assertIn("7", m["reason"])

    def test_recognised_share_bar_and_the_twin_printed(self):
        from tools.verdict_life import hands_mark
        st = {"runs": 30, "runs_by_program": {"p1": 10, "p2": 20}, "hands_no_road": 0, "touch_events": 30, "smell_events": 12}
        ok = hands_mark(st, self._rows(30), {"asked": 30, "hits": 20, "shuffled_hits": 11}, True)
        self.assertTrue(ok["graded"]); self.assertTrue(ok["pass"]); self.assertAlmostEqual(ok["recognised_share"], 20 / 30, places=3); self.assertAlmostEqual(ok["shuffled_share"], 11 / 30, places=3)   # the mark rounds to 4 places
        bad = hands_mark(st, self._rows(30), {"asked": 30, "hits": 5, "shuffled_hits": 2}, True)
        self.assertTrue(bad["graded"]); self.assertFalse(bad["pass"])


class ThreadMark(unittest.TestCase):
    """PREREG §19.2 against builder E's shapes: ALIVE's per-hour max sense gaps; STATUS thinks / think_waits / think_wait_ms /
    think_ms_last / think_ms_median; THINK's `threaded` flag."""

    def test_not_gradable_when_unthreaded_or_without_thinks(self):
        from tools.verdict_life import thread_mark
        self.assertFalse(thread_mark({"max_gap_s_eye_ear": [1.0, 2.0]}, {"thinks": 100, "think_waits": 0}, False)["graded"])
        self.assertFalse(thread_mark({"max_gap_s_eye_ear": [1.0]}, {"thinks": 0, "think_waits": 0}, True)["graded"])

    def test_gap_and_wait_bars(self):
        from tools.verdict_life import thread_mark
        ok = thread_mark({"max_gap_s_eye_ear": [1.6, 2.0, 1.2]}, {"thinks": 832, "think_waits": 0, "think_wait_ms": 0.0, "think_ms_last": 6.3, "think_ms_median": 3.1}, True)
        self.assertTrue(ok["graded"]); self.assertTrue(ok["pass"]); self.assertEqual(ok["max_gap_s"], 2.0); self.assertEqual(ok["waits_share"], 0.0)
        self.assertFalse(thread_mark({"max_gap_s_eye_ear": [1.0, 6.0]}, {"thinks": 100, "think_waits": 0}, True)["pass"])     # a gap over 5.1 s
        self.assertFalse(thread_mark({"max_gap_s_eye_ear": [1.0]}, {"thinks": 100, "think_waits": 6}, True)["pass"])          # waits 6 % ≥ 5 %


# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:2x +0400 — ALPHA4-H task 4 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §5 READ): the SAME "must read not-gradable on a record whose life did not declare the
# line, and grade on synthetic rows shaped like the landed code" discipline this file's header states.
def _tape_shelf(sentences, source="shelf"):
    """`sentences`: a list of word-lists. Builds ear-then-eye rows (PREREG §2.2's order law) on one moment
    per sentence, shaped exactly like creature/senses/read.py's own publish order."""
    rows = []
    seq = 1
    for i, words in enumerate(sentences):
        moment = f"read{i:08d}"
        for w in words:
            rows.append({"seq": seq, "sense": "ear", "meta": {"source": source, "moment": moment, "word": w}}); seq += 1
        rows.append({"seq": seq, "sense": "eye", "meta": {"source": source, "moment": moment}}); seq += 1
    return rows


def _journal_births(sentences, words_born_per_sentence):
    """One journal MOMENT row per sentence, `words_born_per_sentence[i]` words-area births on it (matching
    creature/mind.py:_consume_eye's own `journal_row["births"]` shape: [area, cell, reason])."""
    out = []
    for i, _words in enumerate(sentences):
        moment = f"read{i:08d}"
        births = [["words", 100 + i, "novelty"] for _ in range(words_born_per_sentence[i])]
        out.append({"seq": i, "moment": moment, "births": births})
    return out


class ReadWordsBorn(unittest.TestCase):
    def test_counts_only_words_births_on_shelf_moments(self):
        from tools.verdict_life import read_words_born
        sentences = [["cat", "sat"], ["dog", "ran"]]
        tape = _tape_shelf(sentences) + [{"seq": 99, "sense": "eye", "meta": {"source": "maker", "moment": "w0i0t0"}}]
        journal = _journal_births(sentences, [2, 1]) + [{"seq": 100, "moment": "w0i0t0", "births": [["words", 5, "novelty"]]}]
        self.assertEqual(read_words_born(tape, journal), 3, "the maker's own moment's word-birth must not count")

    def test_sight_births_never_counted(self):
        from tools.verdict_life import read_words_born
        sentences = [["cat", "sat"]]
        tape = _tape_shelf(sentences)
        journal = [{"seq": 0, "moment": "read00000000", "births": [["sight", 1, "novelty"], ["sight", 2, "novelty"]]}]
        self.assertEqual(read_words_born(tape, journal), 0)

    def test_zero_on_an_empty_record(self):
        from tools.verdict_life import read_words_born
        self.assertEqual(read_words_born([], []), 0)


class ShelfEpisodesFromTape(unittest.TestCase):
    def test_extracts_words_in_instant_in_publish_order(self):
        from tools.verdict_life import shelf_episodes_from_tape
        sentences = [["red", "ball"], ["blue", "key", "box"]]
        rows = shelf_episodes_from_tape(_tape_shelf(sentences))
        self.assertEqual([r["words_in_instant"] for r in rows], sentences)

    def test_a_non_shelf_moment_is_excluded(self):
        from tools.verdict_life import shelf_episodes_from_tape
        rows = _tape_shelf([["a", "b"]]) + _tape_shelf([["c", "d"]], source="maker")
        got = shelf_episodes_from_tape(rows)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["words_in_instant"], ["a", "b"])


class ShuffledShelfEpisodes(unittest.TestCase):
    def test_preserves_lengths_and_the_word_pool_destroys_pairing(self):
        from tools.verdict_life import shuffled_shelf_episodes
        rows = [{"id": i, "words_in_instant": ws} for i, ws in enumerate([["red", "ball"], ["blue", "key"], ["red", "ball"], ["red", "ball"]])]
        twin = shuffled_shelf_episodes(rows, seed=1)
        self.assertEqual([len(r["words_in_instant"]) for r in twin], [len(r["words_in_instant"]) for r in rows])
        real_pool = sorted(w for r in rows for w in r["words_in_instant"])
        twin_pool = sorted(w for r in twin for w in r["words_in_instant"])
        self.assertEqual(real_pool, twin_pool, "the multiset of every word is preserved exactly")

    def test_deterministic_for_a_fixed_seed(self):
        from tools.verdict_life import shuffled_shelf_episodes
        rows = [{"id": i, "words_in_instant": ws} for i, ws in enumerate([["a", "b"], ["c", "d"], ["a", "b"]])]
        a = shuffled_shelf_episodes(rows, seed=7)
        b = shuffled_shelf_episodes(rows, seed=7)
        self.assertEqual(a, b)


class ReadFrames(unittest.TestCase):
    def test_a_skewed_corpus_files_the_skewed_pair_with_high_precision(self):
        from tools.verdict_life import read_frames
        from genome.sentence import synthetic_missions
        # genome/sentence.py's OWN calibrated toy (its module docstring's worked example): a lift>2 pair is
        # NOT necessarily the deliberately-skewed one -- when a pair dominates BOTH its words' marginals,
        # lift = count/(N*p1*p2) approaches N/count, which caps below 2 once skew_share > 0.5 (measured
        # here, not assumed); the OTHER, modestly-skewed pairs are what clears the bar, and that is exactly
        # what this toy is FOR (find_frames' own statistic, not this file's fixture).
        rng = np.random.default_rng(20260923)
        missions = synthetic_missions(rng, n=200, skew_pairs=[("red", "ball")], skew_share=0.6)
        rows = _tape_shelf([list(m) for m in missions])
        out = read_frames(rows, shuffle_seed=20260923)
        self.assertGreaterEqual(out["filed"], 1)
        self.assertIsNotNone(out["precision"])
        self.assertGreaterEqual(out["precision"], 0.5)

    def test_a_uniform_corpus_files_nothing_precision_is_none(self):
        from tools.verdict_life import read_frames
        rng_pairs = [(c, o) for c in ("red", "blue", "green") for o in ("ball", "key", "box")]
        sentences = (rng_pairs * 6)   # every pair equally often -> no lift over independence
        rows = _tape_shelf(sentences)
        out = read_frames(rows)
        self.assertEqual(out["filed"], 0)
        self.assertIsNone(out["precision"], "no denominator -- never a spurious 0 or 1 (#162's class)")

    def test_multiword_moments_counted_correctly(self):
        from tools.verdict_life import read_frames
        rows = _tape_shelf([["only"], ["two", "words"], ["three", "words", "here"]])
        out = read_frames(rows)
        self.assertEqual(out["shelf_moments"], 3)
        self.assertEqual(out["shelf_multiword_moments"], 2, "a one-word moment carries no pair")


class ReadMark(unittest.TestCase):
    def _skewed_tape_and_journal(self, n_extra_born=520):
        from genome.sentence import synthetic_missions
        rng = np.random.default_rng(20260923)
        missions = synthetic_missions(rng, n=200, skew_pairs=[("red", "ball")], skew_share=0.6)
        sentences = [list(m) for m in missions]
        tape = _tape_shelf(sentences)
        per_sentence = [1] * len(sentences)
        per_sentence[-1] += max(0, n_extra_born - len(sentences))
        journal = _journal_births(sentences, per_sentence)
        return tape, journal

    def test_not_gradable_without_the_gene(self):
        from tools.verdict_life import read_mark
        self.assertFalse(read_mark([], [], False, {"n": 40, "share": 0.8}, {"n": 40, "share": 0.0})["graded"])

    def test_not_gradable_without_reading_asks_on_the_record(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal()
        m = read_mark(tape, journal, True, None, None)
        self.assertFalse(m["graded"])
        self.assertIn("no reading-mark asks", m["reason"])

    def test_graded_pass_when_every_clause_clears_its_bar(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal(n_extra_born=520)
        recog = {"n": 50, "correct": 40, "share": 0.8}
        recog_blind = {"n": 50, "correct": 0, "share": 0.0}
        m = read_mark(tape, journal, True, recog, recog_blind, min_words_born=500, min_frames=1)
        self.assertTrue(m["graded"])
        self.assertTrue(m["clause_words_born"]); self.assertTrue(m["clause_reading"]); self.assertTrue(m["clause_blind_twin"])
        self.assertTrue(m["pass"], m)

    def test_fails_when_words_born_under_the_bar(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal(n_extra_born=10)
        recog = {"n": 50, "correct": 40, "share": 0.8}
        recog_blind = {"n": 50, "correct": 0, "share": 0.0}
        m = read_mark(tape, journal, True, recog, recog_blind, min_words_born=500, min_frames=1)
        self.assertTrue(m["graded"]); self.assertFalse(m["clause_words_born"]); self.assertFalse(m["pass"])

    def test_fails_when_the_reading_share_is_under_the_bar(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal(n_extra_born=520)
        recog = {"n": 50, "correct": 10, "share": 0.2}
        recog_blind = {"n": 50, "correct": 0, "share": 0.0}
        m = read_mark(tape, journal, True, recog, recog_blind, min_words_born=500, min_frames=1)
        self.assertTrue(m["graded"]); self.assertFalse(m["clause_reading"]); self.assertFalse(m["pass"])

    def test_fails_when_the_blind_twin_does_not_read_zero(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal(n_extra_born=520)
        recog = {"n": 50, "correct": 40, "share": 0.8}
        recog_blind = {"n": 50, "correct": 3, "share": 0.06}
        m = read_mark(tape, journal, True, recog, recog_blind, min_words_born=500, min_frames=1)
        self.assertTrue(m["graded"]); self.assertFalse(m["clause_blind_twin"]); self.assertFalse(m["pass"])

    def test_no_blind_twin_run_fails_and_says_so(self):
        from tools.verdict_life import read_mark
        tape, journal = self._skewed_tape_and_journal(n_extra_born=520)
        recog = {"n": 50, "correct": 40, "share": 0.8}
        m = read_mark(tape, journal, True, recog, None, min_words_born=500, min_frames=1)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])
        self.assertIn("blind twin was not run", m["reason"])


if __name__ == "__main__":
    unittest.main()
