# edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:29 +0400 — READER-FIX-0923 (the third hand's review of alpha4-1's first
# five hours, §3/§6's INSTRUMENT rows, plus the seat's 11:2x fixes 9–11 from alpha4-1's 2 h smoke). Written RED first, every row shaped
# like the LANDED code (#171/#173): the void proposal row is tools/evolve.py:355's own dict; game ear rows carry game/episode/step
# (creature/senses/game.py:209); the maker stamps `answering` on BOTH its ear and eye rows (creature/world_maker.py:68-70); the lexicon
# door's eye row carries `answers` and a moment hashed from (word, qid) (creature/senses/lexicon.py:_moment_id); the readiness
# readings ride on the `sit` journal row (creature/mind.py:_consume_sit); a `sleep` journal row carries the triggering canvas's seq and
# NO timestamp (creature/mind.py:_maybe_sleep); the mind's `stage` event row carries `seq` and NO `at` (creature/mind.py:877).
from __future__ import annotations

import datetime as _dt
import json
import tempfile
import unittest
from pathlib import Path

GAME_ACTS = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
T0 = _dt.datetime(2026, 9, 23, 0, 58, 18, tzinfo=_dt.timezone.utc)


def _at(seconds: float) -> str:
    return (T0 + _dt.timedelta(seconds=seconds)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# ----------------------------------------------------------------------------------------------------------------- 1 · EVOLVE
def _void_proposal(seq, no=1):
    """tools/evolve.py:run_judging_round's own no-checkpoint return, republished as a tape row by creature/senses/evolve.py (meta = the dict)."""
    return {"seq": seq, "sense": "proposal", "meta": {"no": no, "epoch": 0, "verdict": "REFUSED",
                                                      "reason": "not gradable: no shadow checkpoint at or before 2026-09-22T22:58:19.675Z yet",
                                                      "shadow_lag_rows": 7}}


def _judged_proposal(seq, no, verdict="REFUSED", reason="no reading cleared its declared margin (no regressions either)"):
    return {"seq": seq, "sense": "proposal", "meta": {"no": no, "epoch": 0, "gene": "KWTA.k", "value": 7, "checkpoint": 2,
                                                      "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.9},
                                                      "verdict": verdict, "reason": reason, "shadow_lag_rows": 0}}


class EvolveVoidRound(unittest.TestCase):
    def test_the_designed_void_round_is_not_a_judged_round(self):
        """The review §6: the minute-2 round put an unpaired `proposal` row on the tape and `evolve_mark` passes only if EVERY proposal is
        paired — a FAIL by construction on every ALPHA4 life. Three judged rounds + the void one must read PASS (void printed apart)."""
        from tools.verdict_life import evolve_mark
        tape = [_void_proposal(29), _judged_proposal(10000, 2), _judged_proposal(20000, 3), _judged_proposal(30000, 4)]
        m = evolve_mark(tape, [], True, 24.0, every_h=6)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m)
        self.assertEqual(m["void_rounds"], 1); self.assertEqual(m["judged_rounds"], 3); self.assertEqual(m["paired_readings"], 3)
        self.assertEqual(m["proposals"], 4, "every proposal row is still counted and printed")
        self.assertIn("no shadow checkpoint", m["void_round_reasons"][0])

    def test_the_hour_one_shape_reads_zero_judged_against_one_needed_with_the_schedule_printed(self):
        from tools.verdict_life import evolve_mark
        m = evolve_mark([_void_proposal(29)], [], True, 1.0, every_h=6)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])        # a real reading of the schedule, never softened
        self.assertEqual(m["void_rounds"], 1); self.assertEqual(m["judged_rounds"], 0); self.assertEqual(m["needed"], 1)
        self.assertEqual(m["every_h"], 6); self.assertEqual(m["rounds_possible"], 0)

    def test_a_not_gradable_reason_WITH_paired_readings_is_a_judged_round(self):
        from tools.verdict_life import evolve_mark
        tape = [_judged_proposal(10, 1, reason="not gradable: every mark read not gradable for both twins")]
        m = evolve_mark(tape, [], True, 2.0, every_h=6)
        self.assertEqual(m["void_rounds"], 0); self.assertEqual(m["judged_rounds"], 1); self.assertTrue(m["pass"])

    def test_an_unpaired_row_without_the_void_reason_still_fails(self):
        from tools.verdict_life import evolve_mark
        bad = {"seq": 5, "sense": "proposal", "meta": {"no": 2, "epoch": 0, "verdict": "PASS", "reason": "improved q1_seen", "shadow_lag_rows": 0}}
        m = evolve_mark([_void_proposal(1), bad, _judged_proposal(9, 3), _judged_proposal(12, 4)], [], True, 24.0, every_h=6)
        self.assertEqual(m["void_rounds"], 1); self.assertEqual(m["judged_rounds"], 3); self.assertEqual(m["paired_readings"], 2)
        self.assertFalse(m["pass"])

    def test_adoptions_are_bounded_by_judged_rounds(self):
        from tools.verdict_life import evolve_mark
        epoch = {"seq": 50, "epoch": {"epoch": 1, "genome_sha": "a" * 64, "moment": 500, "gene": "KWTA.k", "value": 7}}
        m = evolve_mark([_void_proposal(1)], [epoch], True, 2.0, every_h=6)
        self.assertFalse(m["pass"], "an adoption with no judged round behind it is a defect, whatever the void rows say")


# ----------------------------------------------------------------------------------------------------------------- 2 · COST (§8b)
class CostFunctionOfCells(unittest.TestCase):
    def test_a_grow_life_is_graded_against_one_and_a_half_times_the_function_at_its_own_cell_count(self):
        """ALPHA4-PREREG §8b: 0.09 ms × cells per canvas; the mark reads the 24 h figure against 1.5× that at the final cell count."""
        from tools.verdict_g4 import viii_cost
        st = {"rss_mb": 965.0, "mind_ms_median_1min": 0.03, "mind_ms_per_canvas_1min": 756.0, "cells": 4900}
        m = viii_cost(st, 21.0, 85.0, None, grow=True)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"], "0.154 ms/cell > 0.135: a RESULT, never softened")
        self.assertEqual(m["form"], "§8b"); self.assertEqual(m["cells_alive"], 4900)
        self.assertAlmostEqual(m["bar_ms"], 1.5 * 0.09 * 4900, places=3); self.assertAlmostEqual(m["per_cell_ms"], 756.0 / 4900, places=4)
        self.assertEqual(len(m["review_points"]), 4)
        self.assertIn("g4_7", m); self.assertFalse(m["g4_7"]["pass"])   # 756 > 2 × 21 — printed beside, never graded here

    def test_under_the_function_passes_where_the_fixed_g4_7_number_would_fail(self):
        from tools.verdict_g4 import viii_cost
        st = {"rss_mb": 965.0, "mind_ms_median_1min": 0.03, "mind_ms_per_canvas_1min": 600.0, "cells": 4900}
        m = viii_cost(st, 21.0, 85.0, None, grow=True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertFalse(m["g4_7"]["pass"])

    def test_a_grow_status_without_cells_is_not_graded(self):
        from tools.verdict_g4 import viii_cost
        m = viii_cost({"rss_mb": 900.0, "mind_ms_per_canvas_1min": 600.0}, 21.0, 85.0, None, grow=True)
        self.assertFalse(m["graded"]); self.assertIsNone(m["pass"]); self.assertIn("cells", m["reason"])

    def test_a_non_grow_record_reads_g4_7_exactly_as_before(self):
        from tools.verdict_g4 import viii_cost
        for st in ({"rss_mb": 400.0, "mind_ms_median_1min": 0.17, "mind_ms_per_canvas_1min": 20.0, "cells": 1000},
                   {"rss_mb": 400.0, "mind_ms_median_1min": 0.17, "mind_ms_per_canvas_1min": 40.0, "cells": 1000},
                   {"rss_mb": 400.0, "mind_ms_median_1min": 0.17}):
            m = viii_cost(st, 13.0, 39.0, None)
            self.assertEqual(m["form"], "G4-7"); self.assertEqual((m["graded"], m["pass"]), (m["g4_7"]["graded"], m["g4_7"]["pass"]))

    def test_the_sleep_flag_is_printed_never_graded(self):
        from tools.verdict_g4 import viii_cost
        st = {"rss_mb": 965.0, "mind_ms_per_canvas_1min": 600.0, "cells": 4900}
        m = viii_cost(st, 21.0, 85.0, None, grow=True, sleeps_in_window=1)
        self.assertTrue(m["pass"]); self.assertEqual(m["sleeps_in_window"], 1)


# ----------------------------------------------------------------------------------------------------------------- 3 · ACT
def _act_tape(acts):
    rows = [{"seq": 1, "sense": "eye", "meta": {"source": "game", "act_names": GAME_ACTS, "n_actions": 7}}]
    for i, a in enumerate(acts):
        rows.append({"seq": 2 + i, "sense": "outcome", "meta": {"source": "game", "chosen_by": "mind", "act": a, "act_idx": GAME_ACTS.index(a),
                                                               "got": 0.0, "terminated": False, "truncated": (i % 64 == 63)}})
    return rows


class ActCensusGameOnlyLast100(unittest.TestCase):
    def test_the_mouths_say_is_not_a_game_act_and_the_last_100_lock_fails(self):
        """The review §6: `left` 96 of the last 100; STATUS `acts_chosen` mixes the mouth's `say` with the seven game acts over the whole
        life, so «no verb ≥ 95 %» could not see the lock."""
        from tools.verdict_life import act_mark
        acts = [a for a in GAME_ACTS for _ in range(3)] + ["left"] * 100          # 121 game acts: 21 spread, then the lock
        status = {"acts_chosen": {**{a: acts.count(a) for a in GAME_ACTS}, "say": 300}, "act_mismatches": 0}
        m = act_mark(_act_tape(acts), [], status)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"], m)
        self.assertNotIn("say", m["census"]); self.assertEqual(sum(m["census"].values()), 121)
        self.assertEqual(m["census_last100"]["left"], 100); self.assertEqual(m["max_share_last100"], 1.0)
        self.assertEqual(m["census_all"]["say"], 300, "the old whole-life STATUS census is printed as census_all")
        self.assertLess(m["max_share"], 0.95, "the whole-life census alone cannot see the lock")

    def test_a_spread_last_100_passes(self):
        from tools.verdict_life import act_mark
        acts = [GAME_ACTS[i % 7] for i in range(140)]
        m = act_mark(_act_tape(acts), [], {"acts_chosen": {a: acts.count(a) for a in GAME_ACTS}, "act_mismatches": 0})
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m); self.assertEqual(m["zero_acts"], [])
        self.assertEqual(sum(m["census_last100"].values()), 100)


# ----------------------------------------------------------------------------------------------------------------- 4 · SENTENCE
def _episodes_tape(missions, frames_per_episode):
    """Game ear rows exactly as creature/senses/game.py:209-225 publishes them: per FRAME the colour row then the object row, both
    carrying game/episode/step and the whole mission."""
    rows = []; seq = 1
    for ep, (c, o) in enumerate(missions):
        mission = f"go to the {c} {o}"
        for step in range(frames_per_episode):
            common = {"game": "babyai-gotolocal", "episode": ep, "step": step}
            moment = f"gbaby20260923s{seq:09d}"
            rows.append({"seq": seq, "sense": "ear", "meta": {"moment": moment, "source": "game", "word": c, "mission": mission, **common}}); seq += 1
            rows.append({"seq": seq, "sense": "ear", "meta": {"moment": moment, "source": "game", "word": o, "mission": mission, **common}}); seq += 1
    return rows


class SentenceMissionsPerEpisode(unittest.TestCase):
    def test_a_64_frame_episode_is_one_meeting(self):
        """The review §6: the world-pair-skew gate counted every game FRAME as a mission (≤ 64 an episode), so one episode clears «met ≥ 5»
        and the gate measured episode sparsity, not the world. Three episodes of 64 frames are THREE missions."""
        from tools.verdict_life import world_pair_skew, sentence_mark
        tape = _episodes_tape([("red", "ball"), ("blue", "key"), ("green", "box")], 64)
        sk = world_pair_skew(tape)
        self.assertEqual(sk["missions"], 3); self.assertEqual(sk["missions_per_frame"], 192)
        m = sentence_mark(tape, {"frames_filed": 4, "frames_scored": 4, "frames_true": 4}, True)
        self.assertFalse(m["graded"], m); self.assertIn("3 missions", m["reason"])

    def test_enough_structured_episodes_still_grade(self):
        from tools.verdict_life import sentence_mark
        missions = [("red", "ball")] * 50 + [("blue", "key")] * 50 + [("green", "box")] * 50 + [("red", "key")] * 3 + [("blue", "box")] * 3 + [("green", "ball")] * 3
        m = sentence_mark(_episodes_tape(missions, 2), {"frames_filed": 4, "frames_scored": 4, "frames_true": 4}, True)
        self.assertTrue(m["graded"]); self.assertEqual(m["missions"], 159); self.assertEqual(m["missions_per_frame"], 318); self.assertTrue(m["pass"])


# ----------------------------------------------------------------------------------------------------------------- 5 · QUESTION
def _question_row(seq, n, form, args):
    return {"seq": seq, "question": {"q": form, "args": list(args), "from": "mind", "seq": n, "at": _at(seq)}}


class QuestionAnsweredOncePerQuestion(unittest.TestCase):
    MAKER_MOMENT = "w0000i000030t000000030"
    MAKER_MOMENT_2 = "w0000i000147t000000148"
    SHELF_MOMENT = "readc15a6d32"
    HANDS_MOMENT = "hc495474bb9df"

    def _record(self):
        from creature.senses.lexicon import _moment_id          # the door's own hash — never re-typed in the test either
        journal = [_question_row(10, 0, "what-is", [self.MAKER_MOMENT]), _question_row(20, 1, "what-is", [self.SHELF_MOMENT]),
                   _question_row(30, 2, "what-is", [self.HANDS_MOMENT]), _question_row(40, 3, "is", [self.SHELF_MOMENT, "cat"]),
                   _question_row(50, 4, "what-is", [self.MAKER_MOMENT_2])]
        tape = [{"seq": 5, "sense": "eye", "meta": {"moment": self.MAKER_MOMENT, "source": "maker"}},
                {"seq": 6, "sense": "eye", "meta": {"moment": self.SHELF_MOMENT, "source": "shelf"}},
                {"seq": 7, "sense": "eye", "meta": {"moment": self.HANDS_MOMENT, "source": "hands", "act": "run", "shape": "dot"}},
                {"seq": 8, "sense": "eye", "meta": {"moment": self.MAKER_MOMENT_2, "source": "maker"}}]
        # the maker answers q-0 and q-4 by drawing again: ear AND eye rows, both stamped (creature/world_maker.py:68-70)
        for seq, qid, word in ((60, "q-0", "wave"), (70, "q-4", "circle")):
            tape.append({"seq": seq, "sense": "ear", "meta": {"moment": f"w0001{seq}", "source": "maker", "word": word, "answering": qid}})
            tape.append({"seq": seq + 1, "sense": "eye", "meta": {"moment": f"w0001{seq}", "source": "maker", "answering": qid}})
        # the lexicon answers q-0 («wave», a maker word the maker ALSO answered) and q-1 («the», a shelf word) by showing a gloss
        for seq, qid, word in ((80, "q-0", "wave"), (90, "q-1", "the")):
            mid = _moment_id(word, qid)
            tape.append({"seq": seq, "sense": "ear", "meta": {"moment": mid, "source": "lexicon", "word": "to"}})
            tape.append({"seq": seq + 1, "sense": "eye", "meta": {"moment": mid, "source": "lexicon", "answers": word, "gloss": "to move"}})
        return journal, tape

    def test_each_question_counts_once_and_the_lexicon_answers(self):
        """The review §4/§6: 28 questions, 9 answered — the reader's `answered_rows` counted ear AND eye rows of each maker answer and none
        of the lexicon's; 16 of the unanswered were about the hands' own pictures (no door answers a hands moment)."""
        from tools.verdict_life import question_mark
        journal, tape = self._record()
        m = question_mark(journal, tape, {"questions_written": 5, "questions_answered": 2}, 24.0, True)
        self.assertEqual(m["questions"], 5)
        self.assertEqual(m["answered_by_maker"], 2); self.assertEqual(m["answered_by_lexicon"], 2); self.assertEqual(m["answered_by_both"], 1)
        self.assertEqual(m["answered"], 3); self.assertEqual(m["unanswered"], 2)
        self.assertEqual(m["hands_picture_questions"], 1); self.assertEqual(m["unanswered_hands_pictures"], 1)
        self.assertAlmostEqual(m["answered_share"], 0.6)
        self.assertEqual(m["answered_rows"], 4, "the old row count stays printed, never the share's numerator")


# ----------------------------------------------------------------------------------------------------------------- 6 · READ's sample
def _shelf_tape(words, other=()):
    rows = []; seq = 1
    for w in words:
        rows.append({"seq": seq, "sense": "ear", "meta": {"moment": f"read{seq:08x}", "source": "shelf", "word": w}}); seq += 1
    for w, src in other:
        rows.append({"seq": seq, "sense": "ear", "meta": {"moment": f"x{seq}", "source": src, "word": w}}); seq += 1
    return rows


class ReadSample(unittest.TestCase):
    def test_a_fixed_seed_draw_over_the_whole_heard_list_not_the_newest_fifty(self):
        from tools.verdict_life import read_sample
        heard = [f"w{i:03d}" for i in range(300)]
        s = read_sample(heard, _shelf_tape(heard))
        self.assertEqual(s["seed"], 20260923); self.assertEqual(len(s["words"]), 50)
        self.assertEqual(s, read_sample(heard, _shelf_tape(heard)), "deterministic")
        self.assertNotEqual(set(s["words"]), set(heard[-50:]))
        self.assertLess(min(s["indices"]), 100); self.assertGreater(max(s["indices"]), 200)
        self.assertEqual(s["words"], [heard[i] for i in s["indices"]]); self.assertEqual(s["indices"], sorted(s["indices"]))

    def test_words_the_shelf_does_not_own_on_the_cut_tape_are_excluded(self):
        """The blind twin (shelf rows dropped) reads 0 BY CONSTRUCTION only on words heard from the shelf alone: 7 of 255 shelf words of
        alpha4-1's hour 1 were also heard in the lexicon's glosses (of/and/with/or/to/more/a); a word first heard after the cut was never
        heard by the twins at all."""
        from tools.verdict_life import read_sample
        heard = [f"w{i:03d}" for i in range(120)] + ["the", "late"]
        tape = _shelf_tape(heard[:-1], other=[("the", "lexicon")])       # «late» is not on the cut tape
        s = read_sample(heard, tape)
        self.assertEqual(s["population_heard"], 122); self.assertEqual(s["excluded_other_source"], ["the"])
        self.assertEqual(s["excluded_not_on_cut_tape"], 1); self.assertEqual(s["eligible"], 120)
        self.assertNotIn("the", s["words"]); self.assertNotIn("late", s["words"])

    def test_fewer_than_fifty_eligible_asks_nothing(self):
        from tools.verdict_life import read_sample
        heard = [f"w{i}" for i in range(30)]
        s = read_sample(heard, _shelf_tape(heard))
        self.assertEqual(s["words"], []); self.assertIn("30", s["note"])


# ----------------------------------------------------------------------------------------------------------------- 7 · THREAD
def _thread_record():
    """Eye rows every 2 s; a 7.0 s gap starting at the canvas that triggered sleep 1 (the stall of its O(n²) merge) and a 5.5 s gap ≈ 400 s
    from any sleep; each ear row 0.5 s after its eye row, so the ear carries the same two gaps."""
    tape = []; seq = 1; t = 0.0; sleep_seq = None
    for i in range(400):
        tape.append({"seq": seq, "at": _at(t), "sense": "eye", "meta": {"source": "maker"}})
        if i == 100: sleep_seq = seq
        seq += 1
        tape.append({"seq": seq, "at": _at(t + 0.5), "sense": "ear", "meta": {"source": "maker", "word": "x"}}); seq += 1
        t += 7.0 if i == 100 else (5.5 if i == 300 else 2.0)
    journal = [{"seq": sleep_seq, "sleep": {"replay": 200, "cycle": True}, "hash": "h"}]
    return tape, journal


class ThreadAttributesGapsToSleeps(unittest.TestCase):
    def test_gaps_in_the_minute_after_a_sleep_are_printed_apart_and_the_bar_stays(self):
        from tools.verdict_life import thread_mark
        tape, journal = _thread_record()
        alive = {"max_gap_s_eye_ear": [7.0, 7.0]}
        m = thread_mark(alive, {"thinks": 300, "think_waits": 0}, True, tape=tape, journal=journal)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"], "the 5.1 s bar is unchanged — the reader attributes, never excuses")
        self.assertEqual(m["sleeps_on_record"], 1)
        self.assertAlmostEqual(m["max_gap_in_sleep_minutes_s"], 7.0, places=3)
        self.assertAlmostEqual(m["max_gap_outside_sleep_minutes_s"], 5.5, places=3)
        self.assertEqual(m["over_bar_in_sleep_minutes"], 2); self.assertEqual(m["over_bar_outside_sleep_minutes"], 2)   # eye and ear each

    def test_without_the_tape_the_old_reading_is_unchanged(self):
        from tools.verdict_life import thread_mark
        m = thread_mark({"max_gap_s_eye_ear": [1.6, 2.0]}, {"thinks": 832, "think_waits": 0}, True)
        self.assertTrue(m["pass"]); self.assertIsNone(m.get("max_gap_outside_sleep_minutes_s"))


# ----------------------------------------------------------------------------------------------------------------- 8 · STAGE
def _sit_boundary(seq, a, b, c, d, e, proxy=None):
    return {"seq": seq, "sit": {"act": "sit", "got": 0.9}, "readiness": {"a": a, "b": b, "c": c, "d": d, "e": e, "b_read_proxy": proxy}}


class StageReadinessSeries(unittest.TestCase):
    def test_the_readiness_series_is_printed_beside_the_unchanged_bar(self):
        from tools.verdict_life import stage_mark
        journal = [_sit_boundary(100, False, False, True, False, True), _sit_boundary(200, False, False, True, False, True, False),
                   _sit_boundary(300, True, True, True, True, True, True), _sit_boundary(400, True, True, True, True, True, True),
                   {"seq": 400, "event": "stage", "stage": 4, "moment": 9000, "readings": {k: True for k in "abcde"}}]
        tape = [{"seq": s, "sense": "sit", "meta": {"score": sc, "composite": co, "read_share": rs}}
                for s, sc, co, rs in ((100, 0.88, 0.90, 0.55), (200, 0.89, 0.93, 0.35), (300, 0.99, 0.97, 0.65), (400, 0.99, 0.96, 0.7))]
        m = stage_mark(journal, True, tape=tape)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"]); self.assertEqual(m["stage_events"], 1)
        self.assertEqual(m["readiness_boundaries"], 4); self.assertEqual(m["all_five_held"], 2); self.assertEqual(m["longest_all_five_streak"], 2)
        self.assertEqual(m["held"], {"a": 2, "b": 2, "c": 4, "d": 2, "e": 4})
        self.assertEqual(m["readiness_series"][0]["composite"], 0.90); self.assertEqual(m["readiness_series"][1]["b_read_proxy"], False)

    def test_a_record_without_the_gene_is_not_gradable(self):
        from tools.verdict_life import stage_mark
        m = stage_mark([_sit_boundary(100, False, False, True, False, True)], False, tape=[])
        self.assertFalse(m["graded"])


class GatherToleratesTheMindsStageEvent(unittest.TestCase):
    def test_a_stage_event_without_at_is_carried_not_crashed_on(self):
        """creature/mind.py:877 journals {"seq", "event": "stage", ...} with NO `at`; gather() cut every "event" row by `_iso(e["at"])` —
        a KeyError the first time the door opened, on every read of that life."""
        from tools.verdict_g4 import gather
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "root"; out = Path(d) / "out"
            for sub in ("tape/payload", "journal", "state", "exam"):
                (root / sub).mkdir(parents=True)
            for f in ("organism.npz", "organism.json", "ledger.json"):
                (root / "state" / f).write_bytes(b"x")
            tape = [{"seq": i, "at": _at(i), "sense": "eye", "meta": {"source": "maker"}} for i in range(1, 11)]
            (root / "tape" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in tape))
            journal = [{"seq": None, "at": _at(0), "event": "start", "resumed_from_seq": 0, "backlog_replayed": 0},
                       {"seq": 5, "moment": "w1", "word": "circle"},
                       {"seq": 6, "event": "stage", "stage": 4, "moment": 60, "readings": {k: True for k in "abcde"}},
                       {"seq": None, "at": _at(11), "event": "stop"}]
            (root / "journal" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in journal))
            G = gather(root, out, 1.0)
            self.assertEqual([e["event"] for e in G["events"]], ["start", "stop"])
            self.assertEqual(G["mind_events"], [journal[2]])
            self.assertEqual([r["seq"] for r in G["mind"]], [5])


# ----------------------------------------------------------------------------------------------------------------- 9 · not gradable ≠ failed
class PartitionMarks(unittest.TestCase):
    def test_a_not_gradable_mark_never_sits_in_failed(self):
        """alpha4-1's 2 h smoke: MODULATION's own reason read «… not gradable» and it was still in `marks_failed`."""
        from tools.verdict_g4 import partition_marks
        M = {"i_knows": {"graded": True, "pass": True}, "viii_cost": {"graded": True, "pass": False},
             "MODULATION": {"graded": False, "pass": False, "reason": "no window change on this tape yet — not gradable"},
             "SOUND": {"graded": False, "pass": None, "reason": "not gradable: heard 0 s"},
             "READ": {"graded": True, "pass": False, "reason": "graded"},
             "PLANTS": {"vi": False}, "BANDS": {"x": 1},
             "TWINS": {"gaze": {"Q1": 0.5}, "random_gaze_loses_xi": {"graded": True, "pass": False, "margin": 0.01},
                       "no_sleep_v": {"graded": False, "reason": "SLEEP's retention is not gradable on drawn worlds (§10)"}}}
        failed, not_gradable, missing = partition_marks(M, {"pass": False})
        self.assertEqual(failed, ["viii_cost", "READ", "ALIVE", "TWINS.random_gaze"])   # the old list's order and names: legacy marks, the rest, ALIVE, the twin
        self.assertEqual([k for k, _r in not_gradable], ["MODULATION", "SOUND", "TWINS.no_sleep_v"])
        self.assertEqual(missing, [])

    def test_a_mark_without_graded_is_named_and_kept_in_failed_when_it_fails(self):
        from tools.verdict_g4 import partition_marks
        failed, not_gradable, missing = partition_marks({"x_new": {"pass": False}}, {"pass": True})
        self.assertEqual(failed, ["x_new"]); self.assertEqual(missing, ["x_new"])

    def test_modulation_without_a_window_change_reads_not_gradable(self):
        from tools.verdict_g4 import modulation
        mind = [{"seq": i, "moment": f"w0000i{i:06d}t{i:09d}", "word": ["circle", "square"][i % 2], "err": 0.02} for i in range(1, 300)]
        m = modulation({"mind": mind}, 0.05, regime_step=25)
        self.assertFalse(m["graded"]); self.assertIn("not gradable", m["reason"])

    def test_retention_without_a_pair_reads_not_gradable(self):
        from tools.verdict_g4 import retention_mark
        self.assertFalse(retention_mark([])["graded"])
        m = retention_mark([{"window": 1, "before": 0.98, "first_after": 0.9, "last_in_window": 0.97, "drop_pp": 1.0, "files": []}])
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"])


# ----------------------------------------------------------------------------------------------------------------- 10 · the plant clauses
class PlantClausesBeforeThePlant(unittest.TestCase):
    NULL_OK = {"answered_rate": 0.0, "abstain_rate": 0.8, "n": 10, "graded": {"sure_bare": 0, "unsure": 5, "abstain_with_resemblance": 3, "abstain": 2}}
    PLANT_UNLEARNED = {"answered_rate": 0.0, "abstain_rate": 0.1, "n": 10, "graded": {"sure_bare": 9, "unsure": 1, "abstain_with_resemblance": 0, "abstain": 0}}

    def test_grade_reads_the_plant_clause_not_gradable_while_the_plant_was_never_shown(self):
        from tools.verdict_life import grade_mark
        m = grade_mark(self.PLANT_UNLEARNED, self.NULL_OK, {"Q1": {"hedge_rate": 0.24}}, True, plant_shown=0)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m)                     # the null's two clauses carry the mark
        self.assertFalse(m["plant_clause"]["graded"]); self.assertIn("plant shown 0", m["plant_clause"]["reason"])
        m6 = grade_mark(self.PLANT_UNLEARNED, self.NULL_OK, {"Q1": {"hedge_rate": 0.24}}, True, plant_shown=6)
        self.assertTrue(m6["plant_clause"]["graded"]); self.assertFalse(m6["pass"])

    def test_sizing_reads_the_plant_clause_not_gradable_while_the_plant_was_never_shown(self):
        from tools.verdict_life import sizing_mark
        j = [{"moment": "w1", "when": "2026-09-23T12:00:00Z", "word": "circle", "births": [["sight", 1, "novelty"]]}]
        st = {"sight_born": 3329, "sight_nmax": 4096, "births_refused_nmax": 0, "births_refused_budget": 0, "budget_regenerated": 328}
        m = sizing_mark(st, j, None, grow=True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m); self.assertFalse(m["plant_clause"]["graded"])
        shown = j + [{"moment": f"w{i}", "when": "2026-09-23T13:00:00Z", "word": "zog", "births": []} for i in range(2, 8)]
        m6 = sizing_mark(st, shown, None, grow=True)
        self.assertTrue(m6["plant_clause"]["graded"]); self.assertFalse(m6["pass"]); self.assertEqual(m6["plant_shown_moments"], 6)

    def test_vi_reads_its_plant_clause_the_same_way(self):
        from tools.verdict_g4 import vi_mark
        plant = {"answered_rate": 0.0, "abstain_rate": 0.1, "answered_as": {"s": 5}}; null = {"answered_rate": 0.0, "abstain_rate": 0.9, "answered_as": {}}
        m = vi_mark(plant, null, 0.9, 0.02, plant_shown=0)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m); self.assertFalse(m["plant_clause"]["graded"])
        self.assertFalse(vi_mark(plant, null, 0.9, 0.02, plant_shown=5)["pass"])

    def test_plant_showings_counts_glance_rows_of_the_plant_word(self):
        from tools.verdict_life import plant_showings
        j = [{"moment": "w1", "word": "zog"}, {"moment": "w1", "act": "coarse"}, {"moment": "w2", "word": "circle"}, {"seq": 3, "think": {}}]
        self.assertEqual(plant_showings(j), 1)


# ----------------------------------------------------------------------------------------------------------------- 11 · READ's blind twin
class ReadBlindTwin(unittest.TestCase):
    def _tape_and_journal(self):
        from genome.sentence import synthetic_missions
        import numpy as np
        missions = synthetic_missions(np.random.default_rng(20260923), n=200, skew_pairs=[("red", "ball")], skew_share=0.6)
        rows = []; seq = 1; journal = []
        for i, words in enumerate(missions):
            moment = f"read{i:08d}"
            for w in words:
                rows.append({"seq": seq, "sense": "ear", "meta": {"source": "shelf", "moment": moment, "word": w}}); seq += 1
            rows.append({"seq": seq, "sense": "eye", "meta": {"source": "shelf", "moment": moment}}); seq += 1
            journal.append({"seq": i, "moment": moment, "births": [["words", 100 + i, "novelty"]] * (3 if i < 180 else 1)})
        return rows, journal

    def test_a_blind_twin_that_could_not_run_is_not_gradable_never_fail(self):
        from tools.verdict_life import read_mark
        tape, journal = self._tape_and_journal()
        m = read_mark(tape, journal, True, {"n": 50, "correct": 40, "share": 0.8}, None, min_words_born=500, min_frames=1,
                      blind_reason="not gradable: no shelf rows on the cut tape — the blind twin would equal the unblinded one")
        self.assertTrue(m["graded"]); self.assertIsNone(m["clause_blind_twin"]); self.assertTrue(m["pass"], m)
        self.assertIn("no shelf rows", m["blind_twin"]["reason"])

    def test_a_blind_twin_that_ran_is_graded_and_its_seconds_printed(self):
        from tools.verdict_life import read_mark
        tape, journal = self._tape_and_journal()
        m = read_mark(tape, journal, True, {"n": 50, "correct": 40, "share": 0.8}, {"n": 50, "correct": 0, "share": 0.0, "seconds": 812.5},
                      min_words_born=500, min_frames=1)
        self.assertTrue(m["clause_blind_twin"]); self.assertTrue(m["pass"]); self.assertEqual(m["blind_twin"]["seconds"], 812.5)

    def test_the_worker_drops_the_named_source_before_the_mind_sees_a_row(self):
        from tools.verdict_g4 import rows_for_spec
        rows = [{"seq": 1, "sense": "ear", "meta": {"source": "shelf", "word": "the"}}, {"seq": 2, "sense": "eye", "meta": {"source": "maker"}},
                {"seq": 3, "sense": "eye", "meta": {"source": "shelf"}}]
        self.assertEqual([r["seq"] for r in rows_for_spec(rows, {"drop_source": "shelf"})], [2])
        self.assertEqual([r["seq"] for r in rows_for_spec(rows, {})], [1, 2, 3])
        self.assertEqual([r["seq"] for r in rows_for_spec(rows, {"until_seq": 2})], [1, 2])


if __name__ == "__main__":
    unittest.main()
