# edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 19:04 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §3 (marks V, T, C, Z, F,
# R-FRAME, I1's sealed compare, I2, K) and §3's CONTROLS (each plant asserts it changed the bytes and must be CAUGHT), test-first.
"""tests/tools/test_voice_gate.py — the W1 grader on hand-built journals of a fake two-thing world, plus the REAL scene-spec
provider's integration check against brain/scene/world.py's own generator (never a cache).

The fake world: thing 0 (a small red circle, box at px 0..24) and thing 1 (a big blue square, box at px 64..88); fixations
[[0,0],[1,1],[8,8]] land thing 0, thing 0, thing 1; members [[0,1],[2]] label the two hypotheses 0 and 1. A canvas's rows:
the turn (its say), the voice (the say copied), the learn (the canvas's fixations) — the mind's own order. The controls:
the wrong voice, the ECHO (T passes, V fails, the coincidence share printed), the planted say, the silent mouth, the missing
voice, the orphan voice, the order swap — each caught by its named mark."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Dict, List

from brain.scene import world as W
from tools.brain import voice_gate as VG

T0 = {"shape": "circle", "colour": "red", "size": "small", "top": 0, "left": 0, "side": 24}
T1 = {"shape": "square", "colour": "blue", "size": "big", "top": 64, "left": 64, "side": 24}
FIX = [[0, 0], [1, 1], [8, 8]]
MEMBERS = [[0, 1], [2]]


def truth(ws: int, scene: int) -> Dict[str, object]:
    assert ws == 999
    return {"things": [dict(T0), dict(T1)], "words": ["red", "circle"], "referent": 0}


def canvas(i: int, words=("red",), hyp: int = 0, said: bool = True, calibrated: bool = True) -> List[Dict[str, object]]:
    seq = 10 + 3 * i
    say = {"hyp": hyp, "fix": list(MEMBERS[hyp]), "pos": [4.0, 4.0], "words": list(words), "readback": hyp,
           "margin": 1.0} if said else None
    turn = {"kind": "brain", "act": "turn", "moment": f"sc999t{i:06d}", "seq": seq, "at": f"2026-01-01T00:00:{i:02d}Z",
            "n_hyp": 2, "order": [0, 1], "members": [list(m) for m in MEMBERS], "held": [], "expected": [], "say": say,
            "ask": None, "reason": None if calibrated else "not calibrated", "heard": ["red", "circle"], "surprise": 0.0}
    voice = {"kind": "brain", "act": "voice", "moment": turn["moment"], "seq": seq, "at": turn["at"],
             "say": dict(say)} if said else None
    learn = {"kind": "brain", "act": "learn", "moment": turn["moment"], "seq": seq, "at": turn["at"],
             "fix": [list(f) for f in FIX], "hyps": [list(m) for m in MEMBERS], "words": ["red", "circle"]}
    return [turn] + ([voice] if voice else []) + [learn]


def journal(*specs) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for i, s in enumerate(specs):
        rows += canvas(i, **s)
    return rows


CLEAN = journal({}, {"words": ("blue",), "hyp": 1}, {}, {"said": False, "calibrated": False}, {"words": ("small",)})


class TheTruthPath(unittest.TestCase):
    def test_canvas_key_reads_the_moment_and_the_extra_keys(self) -> None:
        self.assertEqual(VG.canvas_key({"moment": "sc20261101t000042"}), (20261101, 42))
        self.assertEqual(VG.canvas_key({"moment": "mk-7", "world": "maker", "scene": 7, "world_seed": 123}), (123, 7))

    def test_true_words_of_a_thing(self) -> None:
        self.assertEqual(VG.true_words(T0), {"circle", "red", "small"})

    def test_labels_of_the_fake_canvas(self) -> None:
        labels, fix_thing = VG.labels_of(MEMBERS, FIX, [T0, T1])
        self.assertEqual(fix_thing, [0, 0, 1])
        self.assertEqual(labels, [0, 1])

    def test_the_real_provider_regenerates_the_generators_own_spec(self) -> None:
        s = W.train_scene(20261101, 0)
        spec = VG.scene_spec(20261101, 0)
        self.assertEqual(spec["things"], [t.to_dict() for t in s.things])
        self.assertEqual(spec["words"], list(s.words))
        self.assertEqual(spec["referent"], s.referent)
        # a fixation over thing k's box labels to thing k (the seat probe's own rule, W.fixation_thing)
        for k, t in enumerate(s.things):
            cell = (int(t.top) // 8, int(t.left) // 8)
            self.assertEqual(W.fixation_thing(cell, s.things), k)


class MarkV(unittest.TestCase):
    def test_the_clean_journal_passes_with_its_presence_counts(self) -> None:
        v = VG.mark_v(CLEAN)
        self.assertTrue(v["pass"], v)
        self.assertEqual(v["rows_read"], len(CLEAN))
        self.assertEqual(v["turns_with_say"], 4)
        self.assertEqual(v["voice_rows"], 4)
        self.assertIsNone(v["first_failure"])

    def test_the_wrong_voice_is_caught(self) -> None:
        rows, changed = VG.plant_wrong_voice(CLEAN, 0)
        self.assertTrue(changed and rows != CLEAN)
        v = VG.mark_v(rows)
        self.assertFalse(v["pass"])
        self.assertEqual(v["first_failure"]["kind"], "wrong-say")

    def test_the_missing_voice_is_caught(self) -> None:
        rows, changed = VG.plant_missing_voice(CLEAN, 1)
        self.assertTrue(changed and rows != CLEAN)
        v = VG.mark_v(rows)
        self.assertFalse(v["pass"])
        self.assertEqual(v["first_failure"]["kind"], "missing-voice")

    def test_the_orphan_voice_is_caught(self) -> None:
        rows, changed = VG.plant_orphan_voice(CLEAN, 1)
        self.assertTrue(changed and rows != CLEAN)
        v = VG.mark_v(rows)
        self.assertFalse(v["pass"])
        self.assertEqual(v["first_failure"]["kind"], "orphan-voice")

    def test_the_order_swap_is_caught(self) -> None:
        rows, changed = VG.plant_order_swap(CLEAN, 1)
        self.assertTrue(changed and rows != CLEAN)
        v = VG.mark_v(rows)
        self.assertFalse(v["pass"])
        self.assertEqual(v["first_failure"]["kind"], "order")

    def test_the_echo_passes_t_and_fails_v_with_the_coincidence_share_printed(self) -> None:
        rows, changed, info = VG.plant_echo(CLEAN, truth)
        self.assertTrue(changed and rows != CLEAN)
        self.assertEqual(info["dropped"], 0)
        self.assertEqual(info["coincide_share"], 0.0)          # «red circle» is never the brain's one-word say here
        t = VG.mark_t(rows, truth, 999, nulls=5)
        self.assertEqual(t["true"], 1.0, "the parent speaks true sentences: T cannot tell the echo from the brain")
        v = VG.mark_v(rows)
        self.assertFalse(v["pass"], "V is the mark that fails the echo (the law §3, control 2)")
        self.assertEqual(v["first_failure"]["kind"], "wrong-say")


class MarkT(unittest.TestCase):
    def test_the_clean_journal_is_true_above_every_dealt_draw(self) -> None:
        t = VG.mark_t(CLEAN, truth, 999, nulls=10)
        self.assertTrue(t["pass"], t)
        self.assertEqual(t["true"], 1.0)
        self.assertEqual(t["graded"], 4)
        self.assertEqual(t["null_draws"], 10)
        self.assertLess(t["null_max"], 1.0, "the dealt phrases («red» onto the blue square's canvas) read below the truth")
        again = VG.mark_t(CLEAN, truth, 999, nulls=10)
        self.assertEqual(t["null_max"], again["null_max"], "substream(SEED, voice-null:<k>) is reproducible")

    def test_a_voice_with_no_thing_under_it_is_counted_not_graded(self) -> None:
        rows = journal({"words": ("red",), "hyp": 0}, {"words": ("red",), "hyp": 0}, {"words": ("zzz",), "hyp": 0})
        t = VG.mark_t(rows, truth, 999, nulls=3)
        self.assertEqual(t["graded"], 3)
        self.assertEqual(t["true"], 2 / 3)

    def test_the_planted_say_reads_zero(self) -> None:
        rows, changed = VG.plant_planted_say(CLEAN, truth)
        self.assertTrue(changed and rows != CLEAN)
        t = VG.mark_t(rows, truth, 999, nulls=3)
        self.assertEqual(t["true"], 0.0, "every voiced word replaced by a false word of its kind (the law §3, control 3)")

    def test_the_silent_mouth_is_not_gradable_never_a_pass(self) -> None:
        rows, changed = VG.plant_silent(CLEAN)
        self.assertTrue(changed and rows != CLEAN)
        t = VG.mark_t(rows, truth, 999, nulls=3)
        self.assertEqual(t["verdict"], "NOT GRADABLE")
        self.assertFalse(t["pass"], "the silent mouth never passes T (the law §3, control 4)")
        c = VG.mark_c(rows, window=1000, bar=0.85)
        self.assertEqual(c["overall"], 0.0)
        self.assertFalse(c["pass"])


class MarkZ(unittest.TestCase):
    def test_the_constant_mouth_fails_t_and_the_gate_says_so(self) -> None:
        z = VG.mark_z(CLEAN, truth)
        self.assertEqual(z["phrase"], ["red"], "the brain's most frequent phrase on the clean journal")
        self.assertLess(z["constant_true"], 0.95, "«red» said everywhere reads ≈ the base rate, not the bar")
        self.assertTrue(z["caught"], "the absolute bar fails the constant mouth (the dealt null is blind to it, §3 Z)")


class MarkC(unittest.TestCase):
    def test_windows_after_the_first_calibration(self) -> None:
        c = VG.mark_c(CLEAN, window=3, bar=0.85)
        self.assertTrue(c["pass"], c)
        self.assertEqual(c["windows"], 2)
        self.assertEqual(c["lowest_window"]["rate"], 1.0)
        sparse = journal({}, {"said": False}, {"said": False}, {}, {"said": False}, {})
        c2 = VG.mark_c(sparse, window=3, bar=0.85)
        self.assertFalse(c2["pass"])
        self.assertLess(c2["lowest_window"]["rate"], 0.85)


class MarksI2FAndTheSealedCompare(unittest.TestCase):
    def test_i2_the_on_journal_minus_its_voice_rows_equals_the_off_journal(self) -> None:
        off = [r for r in CLEAN if not (r.get("kind") == "brain" and r.get("act") == "voice")]
        self.assertTrue(VG.mark_i2(CLEAN, off)["pass"])
        bad = json.loads(json.dumps(off))
        bad[2]["words"] = ["changed"]
        m = VG.mark_i2(CLEAN, bad)
        self.assertFalse(m["pass"])
        self.assertIsNotNone(m["first_difference"])

    def test_the_sealed_compare_names_the_first_difference(self) -> None:
        a = [{"x": 1}, {"x": 2}]
        self.assertIsNone(VG.compare_rows(a, a))
        d = VG.compare_rows(a, [{"x": 1}, {"x": 3}])
        self.assertEqual(d["row"], 1)

    def test_f_the_frame_mouth_unmoved(self) -> None:
        say_row = {"seq": 10, "say": {"frame": "red circle", "seq": 10, "heard": "yes", "episodes": [1]}}
        think_row = {"seq": 10, "think": {"item": "x", "kind": "frame", "outcome": "filed", "parked": False}}
        on = CLEAN[:2] + [say_row, think_row] + CLEAN[2:]
        off = [r for r in on if not (r.get("kind") == "brain" and r.get("act") == "voice")]
        preds = json.dumps({"accepted": True, "refused": [], "row": {"claim": '"red circle"', "route": "frame"}}) + "\n"
        f = VG.mark_f(on, off, preds, preds)
        self.assertTrue(f["pass"], f)
        self.assertEqual(f["said"], 1)
        self.assertEqual(f["heard_yes"], 1)
        self.assertEqual(f["frames_filed"], 1)
        self.assertEqual(f["frames_scored"], 1)
        f2 = VG.mark_f(on, off, preds, preds.replace("true", "false"))
        self.assertFalse(f2["pass"], "a changed predictions.jsonl moves F")


class MarkK(unittest.TestCase):
    def test_the_cpu_ratio(self) -> None:
        seqs = {"sc999t000000": [1, 2], "sc999t000001": [3, 4]}
        on = {1: {"cpu_ms": 6.0}, 2: {"cpu_ms": 6.0}, 3: {"cpu_ms": 6.0}, 4: {"cpu_ms": 6.0}}
        off = {1: {"cpu_ms": 5.0}, 2: {"cpu_ms": 5.0}, 3: {"cpu_ms": 5.0}, 4: {"cpu_ms": 5.0}}
        k = VG.mark_k(seqs, on, off, bar=1.05)
        self.assertAlmostEqual(k["ratio"], 1.2)
        self.assertFalse(k["pass"])
        self.assertTrue(VG.mark_k(seqs, on, off, bar=1.2)["pass"])


class RFrame(unittest.TestCase):
    def test_the_frame_mouth_read_by_the_same_key(self) -> None:
        rows = journal({}, {"words": ("blue",), "hyp": 1}, {}, {})
        frames = [{"seq": 10, "say": {"frame": "red circle", "heard": "yes", "episodes": [1]}},     # both true of thing 0
                  {"seq": 13, "say": {"frame": "red square", "heard": "no", "episodes": [2]}},     # not both of ONE thing
                  {"seq": 16, "say": {"frame": "small circle", "heard": "yes", "episodes": [3]}}]  # both true of thing 0
        rows = sorted(rows + frames, key=lambda r: (r["seq"], 0 if r.get("act") == "turn" else 1))
        r = VG.r_frame(rows, truth)
        self.assertEqual(r["frames"], 3)
        self.assertEqual(r["frame_true"], 2 / 3)
        self.assertEqual(r["paired"], 3, "every frame canvas also carries a voice here")
        self.assertEqual(r["paired_frame_true"], 2 / 3)
        self.assertEqual(r["paired_voice_true"], 1.0)
        self.assertEqual(r["smallest_passing_gap"], 10 / 3)
        self.assertAlmostEqual(r["heard_yes_share"], 2 / 3, "the mouth's own «heard yes», a different quantity")


class TheSavedStateAndTheTapeSeqs(unittest.TestCase):
    """The instrument's own two paths (its 20:5x faults pinned by name): the saved brain state compared as the organ's
    OWN ARRAYS plus the meta MINUS the replay work root's name (NOTE-1), and the tape's train moments read from the
    life ROOT (read_tape's own _resolve_tape_dir appends the tape dir)."""

    def _work_root(self, parent: Path, name: str, x: int, author: str) -> None:
        import numpy as np
        st = parent / name / "state"
        st.mkdir(parents=True, exist_ok=True)
        np.savez(st / "brain.npz", road=np.array([[x, x + 1], [x + 2, x + 3]]))
        (st / "brain.json").write_text(json.dumps({"version": 1, "state_hash": f"digest-inheriting-{author}",
                                                   "brain": {"segments": [{"author": author, "n": x}],
                                                             "n_calibrations": 3}}))

    def test_the_saved_brain_state_compares_the_arrays_and_masks_the_work_root(self) -> None:
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        on, off = tmp / "on", tmp / "off"
        self._work_root(on, "creature-replay-aaa111", 7, "creature-replay-aaa111")
        self._work_root(off, "creature-replay-bbb222", 7, "creature-replay-bbb222")
        m = VG._saved_brain_equal(on / "creature-replay-*", off / "creature-replay-*")
        self.assertTrue(m["equal"], m)
        self.assertTrue(m["arrays_equal"] and m["meta_minus_work_root_equal"])
        self._work_root(off, "creature-replay-bbb222", 8, "creature-replay-bbb222")   # one array value flipped
        m2 = VG._saved_brain_equal(on / "creature-replay-*", off / "creature-replay-*")
        self.assertFalse(m2["equal"], "a changed learned array must move the compare")
        self.assertFalse(m2["arrays_equal"])

    def test_the_train_seqs_are_read_from_the_life_root(self) -> None:
        import tempfile
        root = Path(tempfile.mkdtemp())
        tape = root / "tape"
        tape.mkdir()
        rows = [{"sense": "ear", "seq": 1, "meta": {"moment": "sc999t000000", "source": "scene"}},
                {"sense": "eye", "seq": 2, "meta": {"moment": "sc999t000000", "source": "scene"}},
                {"sense": "ear", "seq": 3, "meta": {"moment": "sc999t000001", "source": "scene"}},
                {"sense": "eye", "seq": 4, "meta": {"moment": "sc999t000001", "source": "scene"}}]
        (tape / "2026-01-01.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        seqs = VG._train_seqs(root)
        self.assertEqual(seqs, {"sc999t000000": [1, 2], "sc999t000001": [3, 4]})


if __name__ == "__main__":
    unittest.main()
