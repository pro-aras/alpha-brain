# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:42 +0400 — A4L-VOICE task 5 (docs/briefs/A4L-VOICE.md;
# docs/A4-LADDER-PREREG.md §2.3 V1–V5): the rung's marks as PURE functions over the shapes this branch LANDED
# (genome/questions.py:ask_sound's dict; the journal's `sound` rows; STATUS's sound keys) — each reads «not gradable» on a
# record whose life did not declare the voice (the hour-1 fixture: alpha4-1 has no sound area), grades on synthetic records
# shaped like the landed ones, and the shuffled-sound transform is the null's own tape (#171/#173: fed the landed shapes).
import copy
import unittest

THINGS16 = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave", "diamond",
            "moon", "house", "tree", "cup", "key"]


def _ask(v1=16, v2=0.95, v5=0.95, voiced=10, v5_none=False, n=16):
    """An ask_sound output (genome/questions.py) with the given correct counts / accuracies."""
    return {"things": THINGS16[:n], "sound_born": n, "sound_alive": n,
            "V1": {"correct": v1, "n": n, "acc": v1 / n, "abstain": {}, "per_thing": {}},
            "V5": None if v5_none else {"correct": round(v5 * n), "n": n, "acc": v5, "abstain": {}, "per_thing": {}},
            "V2": {"correct": round(v2 * 10 * n), "n": 10 * n, "acc": v2, "abstain": {}, "ledger_correct": 0, "per_thing": {}},
            "V1b": {"0.96": {"correct": 6, "n": n, "acc": 6 / n}, "1.04": {"correct": 7, "n": n, "acc": 7 / n}},
            "voiced": {t: voiced for t in THINGS16[:n]}, "gradable": voiced >= 5,
            "reason": "graded" if voiced >= 5 else "not gradable: voiced < 5 times: [...]"}


class HearMark(unittest.TestCase):
    def test_not_gradable_on_a_record_without_the_voice(self):
        from tools.verdict_life import hear_mark
        m = hear_mark(None, None, None)
        self.assertFalse(m["graded"]); self.assertIsNone(m["pass"]); self.assertIn("not gradable", m["reason"])
        m = hear_mark({"gradable": False, "reason": "no sound area (AREA sound undeclared)"}, None, None)
        self.assertFalse(m["graded"]); self.assertIn("no sound area", m["reason"])

    def test_not_gradable_until_every_thing_was_voiced_five_times(self):
        from tools.verdict_life import hear_mark
        m = hear_mark(_ask(voiced=4), _ask(voiced=4), _ask(v1=1, v2=0.05, voiced=4))
        self.assertFalse(m["graded"]); self.assertIn("voiced", m["reason"])

    def test_not_gradable_without_both_twins(self):
        from tools.verdict_life import hear_mark
        self.assertFalse(hear_mark(_ask(), None, _ask(v1=0, v2=0.0))["graded"])
        self.assertFalse(hear_mark(_ask(), _ask(), None)["graded"])

    def test_pass_and_each_clause_fails_alone(self):
        from tools.verdict_life import hear_mark
        good = hear_mark(_ask(), _ask(v1=15), _ask(v1=1, v2=0.06))
        self.assertTrue(good["graded"]); self.assertTrue(good["pass"], good)
        self.assertEqual(good["V1"]["blind_ear_correct"], 15); self.assertEqual(good["V1"]["shuffled_correct"], 1)
        self.assertFalse(hear_mark(_ask(), _ask(v1=12), _ask(v1=1, v2=0.06))["pass"], "V1 12/16 < 13/16")
        self.assertFalse(hear_mark(_ask(), _ask(v1=15), _ask(v1=3, v2=0.06))["pass"], "the null V1 3/16 > 2/16")
        self.assertFalse(hear_mark(_ask(v2=0.79), _ask(v1=15), _ask(v1=1, v2=0.06))["pass"], "V2 0.79 < 0.8")
        self.assertFalse(hear_mark(_ask(), _ask(v1=15), _ask(v1=1, v2=0.16))["pass"], "the null V2 0.16 > 0.15")
        self.assertFalse(hear_mark(_ask(v5=0.75), _ask(v1=15), _ask(v1=1, v2=0.06))["pass"], "V5 0.75 < 0.8")

    def test_v5_off_reads_not_gradable_and_v1_v2_still_grade(self):
        from tools.verdict_life import hear_mark
        m = hear_mark(_ask(v5_none=True), _ask(v1=15, v5_none=True), _ask(v1=1, v2=0.06, v5_none=True))
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"])
        self.assertFalse(m["V5"]["graded"]); self.assertIn("MEET sound words", m["V5"]["reason"])

    def test_v1b_is_printed_never_graded(self):
        from tools.verdict_life import hear_mark
        m = hear_mark(_ask(), _ask(v1=15), _ask(v1=1, v2=0.06))
        self.assertIn("V1b", m); self.assertNotIn("V1b", m["bar"].split("·")[0])


class VoiceHarmMark(unittest.TestCase):
    def _exam(self, q1):
        return {"ask_seen_words": {"Q1": {"acc": q1}}}

    def test_not_gradable_without_the_voice_or_the_twin(self):
        from tools.verdict_life import voice_harm_mark
        self.assertFalse(voice_harm_mark(self._exam(0.95), self._exam(0.95), declared=False)["graded"])
        self.assertFalse(voice_harm_mark(self._exam(0.95), None, declared=True)["graded"])

    def test_the_regression_bar(self):
        from tools.verdict_life import voice_harm_mark
        self.assertTrue(voice_harm_mark(self._exam(0.95), self._exam(0.955), declared=True)["pass"])     # −0.005 >= −0.01
        self.assertFalse(voice_harm_mark(self._exam(0.93), self._exam(0.95), declared=True)["pass"])     # −0.02
        m = voice_harm_mark(self._exam(0.95), self._exam(0.95), declared=True)
        self.assertEqual(m["delta"], 0.0)


class SoundCells(unittest.TestCase):
    def test_v4_prints_born_and_refused_from_status(self):
        from tools.verdict_life import sound_cells_mark
        m = sound_cells_mark({"sound_born": 17, "sound_cells": 17, "sound_births_refused": 0, "voice_rows": 5760, "voice_bound": 5760})
        self.assertEqual(m["sound_born"], 17); self.assertEqual(m["voice_bound"], 5760); self.assertIsNone(m["pass"])
        self.assertIn("printed", m["bar"])
        m = sound_cells_mark({})
        self.assertFalse(m["graded"])


class SoundMarkOnAVoicedTape(unittest.TestCase):
    def test_a_bound_canvas_row_is_not_counted_as_a_second_consumption(self):
        """The eye row that BINDS a sound carries a `sound` dict too (its seq/winners) — sound_mark must count the sound
        ROWS consumed, never those binding rows (else consumed > rows on every voiced tape)."""
        from tools.verdict_life import sound_mark
        tape = [{"seq": 2, "sense": "ear-sound", "meta": {"source": "maker", "word": "cup", "when": 0.006, "duration_s": 0.45}}]
        journal = [{"seq": 2, "sound": {"moment": "m", "level": 0.1, "when": 0.006, "file": None, "ep": None, "pending": True}},
                   {"seq": 3, "moment": "m", "word": "cup", "births": [], "sound": {"seq": 2, "winners": [0], "cells": 1}}]
        m = sound_mark(tape, journal, {"sound_events": 0, "voice_rows": 1, "voice_bound": 1})
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m)
        self.assertEqual(m["consumed"], 1); self.assertEqual(m["voiced_rows"], 1); self.assertEqual(m["bound_rows"], 1)
        self.assertAlmostEqual(m["heard_s"], 0.45)

    def test_silent_record_still_not_gradable(self):
        from tools.verdict_life import sound_mark
        m = sound_mark([{"seq": 1, "sense": "eye", "meta": {"source": "maker"}}], [], {})
        self.assertFalse(m["graded"]); self.assertIn("heard 0 s", m["reason"])


class ShuffleVoice(unittest.TestCase):
    def _tape(self):
        rows = []; s = 1
        for i in range(3):
            for w in ("cup", "key", "moon"):
                rows.append({"seq": s, "sense": "ear", "meta": {"source": "maker", "word": w, "moment": f"m{s}"}}); s += 1
                rows.append({"seq": s, "sense": "ear-sound", "payload": f"payload/{w}-{i}.f32", "meta": {"source": "maker", "word": w, "moment": f"m{s-1}"}}); s += 1
                rows.append({"seq": s, "sense": "eye", "payload": f"payload/{w}-{i}.png", "meta": {"source": "maker", "moment": f"m{s-2}"}}); s += 1
        rows.append({"seq": s, "sense": "ear-sound", "payload": "payload/door.f32", "meta": {"source": "ear_sound", "moment": "aXe0000"}})
        return rows

    def test_a_derangement_of_the_chords_by_the_readers_seed_and_the_input_untouched(self):
        from tools.verdict_life import shuffle_voice
        rows = self._tape(); before = copy.deepcopy(rows)
        out, perm = shuffle_voice(rows, seed=20260923)
        self.assertEqual(rows, before, "pure: the input rows are never touched")
        self.assertEqual(sorted(perm), ["cup", "key", "moon"]); self.assertTrue(all(perm[w] != w for w in perm), perm)
        for r0, r1 in zip(rows, out):
            if r0["sense"] == "ear-sound" and r0["meta"]["source"] == "maker":
                self.assertTrue(r1["payload"].startswith(f"payload/{perm[r0['meta']['word']]}-"), (r0, r1))
                self.assertEqual(r1["meta"]["word"], r0["meta"]["word"])
            else:
                self.assertEqual(r0, r1)
        self.assertEqual(shuffle_voice(rows, seed=20260923)[1], perm, "a fixed permutation for a fixed seed")


if __name__ == "__main__":
    unittest.main()
