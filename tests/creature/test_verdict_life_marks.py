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


if __name__ == "__main__":
    unittest.main()
