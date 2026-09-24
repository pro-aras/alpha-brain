# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:33 +0400 — READER v3.5: the ladder-2 marks (A4-LADDER-2-PREREG §2 + ADDENDUM §7(2)),
# pure functions in tools/verdict_life.py, gathered by tools/verdict_g4.py:ladder2_read and rendered by ladder2_rows. Synthetic fixtures (the landed row
# shapes: tape eye rows {seq, at, sense, sha, meta.source}; journal canvas rows {seq, moment, glance 0, source, births [[area, id, why]], cells}; sleep rows;
# game act/outcome rows; predictions.jsonl frame rows; HEARD.json lists) + the real pre-flight records as controls where a copy is on this box.
"""READER v3.5's ladder-2 marks: IDENTITY, X1/X2's window and census, LINE, NURSERY (+ READ vs R0), DROP_EQ, CHAT_COUNTERS, and their wiring."""
import ast
import json
import tempfile
import unittest
from pathlib import Path

TREE = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(TREE))
from tools import verdict_life as vl          # noqa: E402
import tools.verdict_g4 as vg                  # noqa: E402

SCRATCH = Path("/data/dev/scratch-reader35")   # the builder's copies of the CLOSED ladder-2 pre-flight roots (skipped where absent)


def _eye(seq, src, sha, at="2026-09-23T10:00:00.000Z"):
    return {"seq": seq, "at": at, "sense": "eye", "sha": sha, "payload": f"payload/{seq:09d}.png", "meta": {"moment": f"m{seq}", "source": src}}


def _canvas(seq, src, births=(), cells=None):
    r = {"seq": seq, "moment": f"m{seq}", "glance": 0, "act": "glance", "source": src, "when": "2026-09-23T10:00:00.000Z"}
    if cells is not None:
        r["births"] = [list(b) for b in births]; r["cells"] = list(cells)
    return r


def _life(order, sleep_after=None):
    """A tiny life: `order` = [(src, sha, births, cells)] in the life's own interleaving; a hands canvas journals no births/cells (as the body)."""
    tape, jr = [], []
    for i, (src, sha, births, cells) in enumerate(order, start=1):
        tape.append(_eye(i, src, sha))
        jr.append(_canvas(i, src, births, None if src == "hands" else cells))
        if sleep_after is not None and i == sleep_after:
            jr.append({"seq": i, "sleep": {"replayed": 10, "births": 1, "merged": 0, "pruned": 0}})
    return tape, jr


class Identity(unittest.TestCase):
    def _pair(self):
        # life A: maker, hands, folder, maker ; life B: maker, folder, hands, maker (the hands canvas interleaved differently)
        a = [("maker", "m1", [("sight", 0, "n")], (1, 1)), ("hands", "h1", [], None), ("folder", "f1", [("sight", 2, "n")], (3, 1)), ("maker", "m2", [], (3, 1))]
        b = [("maker", "m1", [("sight", 0, "n")], (1, 1)), ("folder", "f1", [("sight", 1, "n")], (2, 1)), ("hands", "h1", [], None), ("maker", "m2", [], (3, 1))]
        return _life(a), _life(b)

    def test_same_streams_different_interleaving_pass_and_the_id_order_is_printed_only(self):
        (ta, ja), (tb, jb) = self._pair()
        m = vl.identity_mark(ta, ja, tb, jb, min_canvases=1)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m["reason"])
        self.assertTrue(m["streams_identical"])
        self.assertEqual(m["meeting_points_disagree"], 0)
        self.assertGreaterEqual(m["meeting_points"], 2)
        self.assertEqual(m["streams"]["hands"]["graded"], False, "hands is printed beside, never one of the four graded world streams")

    def test_keyed_on_every_source_a_hands_canvas_never_makes_two_moments_one_meeting_point(self):
        (ta, ja), (tb, jb) = self._pair()
        ra, _ = vl.meeting_readings(ja); rb, _ = vl.meeting_readings(jb)
        # A's folder row is keyed WITH hands 1, B's WITHOUT: they are different meeting points (keyed on four sources they would collide: 3 vs 2 cells)
        self.assertIn((("folder", 1), ("hands", 1), ("maker", 1)), ra)
        self.assertIn((("folder", 1), ("maker", 1)), rb)
        self.assertNotIn((("folder", 1), ("maker", 1)), ra)

    def test_a_row_without_its_own_reading_is_never_a_meeting_point(self):
        (_ta, ja), _ = self._pair()
        ra, n = vl.meeting_readings(ja)
        self.assertEqual(n, 4, "every canvas counts in the canvas index")
        self.assertEqual(len(ra), 3, "the hands canvas carries no cells: no reading there")

    def test_a_diverged_game_stream_fails_alone(self):
        a = [("maker", "m1", [], (1, 1)), ("game", "g1", [], (1, 1)), ("game", "g2", [], (1, 1))]
        b = [("maker", "m1", [], (1, 1)), ("game", "g1", [], (1, 1)), ("game", "gX", [], (1, 1))]
        (ta, ja), (tb, jb) = _life(a), _life(b)
        m = vl.identity_mark(ta, ja, tb, jb, min_canvases=1)
        self.assertTrue(m["graded"]); self.assertFalse(m["pass"])
        self.assertEqual(m["streams"]["game"]["first_divergence"]["index"], 1)
        self.assertIn("game at 1", m["reason"])

    def test_counts_that_differ_at_a_meeting_point_fail(self):
        a = [("maker", "m1", [("sight", 0, "n")], (1, 1)), ("maker", "m2", [("sight", 1, "n")], (2, 1))]
        b = [("maker", "m1", [("sight", 0, "n")], (1, 1)), ("maker", "m2", [], (1, 1))]
        (ta, ja), (tb, jb) = _life(a), _life(b)
        m = vl.identity_mark(ta, ja, tb, jb, min_canvases=1)
        self.assertTrue(m["streams_identical"]); self.assertFalse(m["pass"])
        self.assertEqual(m["meeting_points_disagree"], 1)
        self.assertEqual(m["disagreements"][0]["canvas"], 2)

    def test_a_sleep_counts_in_both_births_and_sleeps(self):
        a = [("maker", "m1", [], (1, 1)), ("maker", "m2", [], (1, 1))]
        (ta, ja), (tb, jb) = _life(a, sleep_after=1), _life(a)
        m = vl.identity_mark(ta, ja, tb, jb, min_canvases=1)
        self.assertFalse(m["pass"], "one mind slept, the other did not: a real difference at the next meeting point")

    def test_not_given_and_too_short_are_not_gradable(self):
        self.assertFalse(vl.identity_mark([], [], [], [], provided=False)["graded"])
        (ta, ja), (tb, jb) = self._pair()
        m = vl.identity_mark(ta, ja, tb, jb, min_canvases=100)
        self.assertFalse(m["graded"]); self.assertIn("< 100", m["reason"])


class WallBand(unittest.TestCase):
    def test_the_band_is_the_references_own_rate_times_the_canvas_gap(self):
        canvas_seqs = list(range(1, 201))
        series = [{"heartbeat_at": "2026-09-23T10:00:00.000Z", "last_seq": 100, "cells": 50, "sight_born": 60, "births": 70, "sleeps": 1},
                  {"heartbeat_at": "2026-09-23T11:00:00.000Z", "last_seq": 200, "cells": 90, "sight_born": 110, "births": 130, "sleeps": 2}]
        cut = vl._at_s("2026-09-23T11:00:00.000Z")
        wb = vl.wall_reading(series, {}, canvas_seqs, cut)
        self.assertEqual((wb["canvases"], wb["births"]), (200, 130))
        self.assertAlmostEqual(wb["rate_per_canvas_last_hour"]["births"], 0.6)
        wa = {"canvases": 190, "cells": 86, "sight_born": 104, "births": 124, "sleeps": 2}
        band = vl.wall_band(wa, wb)
        self.assertEqual(band["delta_canvases"], -10)
        self.assertEqual(band["per_counter"]["births"]["band"], 6)
        self.assertTrue(band["per_counter"]["births"]["inside"])
        self.assertEqual(band["per_counter"]["births"]["delta"], -6)

    def test_a_reading_after_the_cut_is_never_used(self):
        series = [{"heartbeat_at": "2026-09-23T12:00:00.000Z", "last_seq": 5, "cells": 1}]
        w = vl.wall_reading(series, {}, [1, 2], vl._at_s("2026-09-23T11:00:00.000Z"))
        self.assertIsNone(w["at"])


class ExploreWindowAndCensus(unittest.TestCase):
    def _game(self, n, act_of):
        tape, jr = [], []
        base = vl._at_s("2026-09-23T10:00:00.000Z")
        import datetime as dt
        for i in range(1, n + 1):
            at = dt.datetime.fromtimestamp(base + 30 * i, dt.timezone.utc).isoformat().replace("+00:00", "Z")
            tape.append({"seq": 2 * i, "at": at, "sense": "eye", "sha": f"s{i}", "meta": {"source": "game"}})
            jr.append({"seq": 2 * i, "act": {"game": "babyai", "act": act_of(i), "policy": "reward-valued"}})
        return tape, jr

    def test_the_window_is_located(self):
        tape, jr = self._game(400, lambda i: "left" if 250 <= i < 330 else ["forward", "right", "pickup"][i % 3])
        m = vl.explore_lock_mark(tape, jr, True)
        w = vl.explore_lock_window(tape, jr)["window"]
        self.assertEqual(round(w["top_share"], 4), m["max_share"])
        self.assertGreater(w["first_hour"], 1.0)
        self.assertEqual(w["census"].get("left"), max(w["census"].values()))
        self.assertFalse(m["pass"], "80 of a 100-window on one act: locked")

    def test_the_census_prints_the_presence_count_beside_the_zero(self):
        tape = [{"seq": 1, "at": "2026-09-23T10:00:00.000Z", "sense": "outcome", "meta": {"source": "game", "got": 0.0, "terminated": False, "truncated": False}},
                {"seq": 2, "at": "2026-09-23T10:00:30.000Z", "sense": "outcome", "meta": {"source": "game", "got": 0.62, "terminated": True, "truncated": False}},
                {"seq": 3, "at": "2026-09-23T10:01:00.000Z", "sense": "outcome", "meta": {"source": "game", "got": 0.0, "terminated": False, "truncated": True}}]
        jr = [{"seq": 1, "outcome": {"source": "game", "got": 0.0}}, {"seq": 2, "outcome": {"source": "game", "got": 0.62}},
              {"seq": 3, "outcome": {"source": "game"}}, {"seq": 4, "outcome": {"source": "hands", "got": 0.9}}]
        c = vl.explore_x2_census(tape, jr, {"act_policy": "reward-valued", "act_weights": [0.0] * 7})
        self.assertEqual((c["journal_game_outcome_rows"], c["rows_carrying_got"], c["rewarded_rows"]), (3, 2, 1))
        self.assertEqual((c["episodes_terminal_rows"], c["terminated"], c["truncated"], c["successes"]), (2, 1, 1, 1))
        self.assertEqual(c["success_per_episode"], 0.5)
        self.assertEqual(c["act_policy"], "reward-valued"); self.assertEqual(c["act_explored"], "not recorded")


def _frame(outcome, instant=None):
    r = {"accepted": True, "refused": [], "row": {"claim": '"a b"', "route": "frame"}, "outcome": outcome}
    if instant is not None:
        r["instant"] = instant
    return r


class Line(unittest.TestCase):
    SHELF = {"source": "shelf", "words": ["to", "the"], "line": True}
    GAME = {"source": "game", "words": ["red", "box"], "line": False}

    def test_undeclared_is_not_gradable(self):
        m = vl.line_mark([_frame(True, self.SHELF)], {}, False)
        self.assertFalse(m["graded"]); self.assertIn("not declared", m["reason"])

    def test_no_shelf_line_scored_is_the_horizon_never_fail(self):
        m = vl.line_mark([_frame(None), _frame(True, self.GAME)], {"frames_scored": 1}, True)
        self.assertFalse(m["graded"]); self.assertEqual(m["by_instant"], {"game": {"scored": 1, "true": 1}})
        self.assertTrue(m["scored_reconciles_with_status"])

    def test_one_true_shelf_line_passes_and_zero_fails(self):
        rows = [_frame(None), _frame(True, self.SHELF), _frame(False, self.SHELF), _frame(True, self.GAME)]
        m = vl.line_mark(rows, {"frames_scored": 3, "frames_true": 2}, True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"])
        self.assertEqual((m["shelf_line_scored"], m["shelf_line_true"], m["shelf_true_rate"]), (2, 1, 0.5))
        self.assertAlmostEqual(m["ratio_to_ceiling"], round(0.5 / vl.LINE_CEILING, 3))
        m0 = vl.line_mark([_frame(False, self.SHELF)], {}, True)
        self.assertTrue(m0["graded"]); self.assertFalse(m0["pass"])

    def test_a_one_word_shelf_moment_is_not_a_line(self):
        m = vl.line_mark([_frame(True, {"source": "shelf", "words": ["to"], "line": False})], {}, True)
        self.assertEqual(m["by_instant"], {"shelf_word": {"scored": 1, "true": 1}}); self.assertFalse(m["graded"])


R0_HEARD = ["the", "project", "gutenber", "ebook", "of", "body1", "body2", "the2", "body3", "body4"]


class Nursery(unittest.TestCase):
    def test_the_body_only_life_passes_with_the_measured_shift(self):
        r3 = ["body1", "the", "body2", "of", "the2", "body3", "body4", "beyond1"]
        m = vl.nursery_mark(r3, R0_HEARD, ["body1", "the", "body2"], True)
        self.assertTrue(m["graded"]); self.assertTrue(m["pass"], m["reason"])
        self.assertEqual(m["shift_measured"], 5)
        self.assertEqual(m["header_shared_reheard"], 2, "«the» and «of»: heard in R0's header, re-heard in the body — never a failure")
        self.assertEqual(m["beyond_control"], 1)
        self.assertEqual(m["stronger_prefix_equal"]["first_mismatch"], None)

    def test_a_header_token_fails(self):
        m = vl.nursery_mark(["body1", "ebook", "body2"], R0_HEARD, [], True)
        self.assertFalse(m["pass"]); self.assertEqual(m["header_tokens_n"], 1)

    def test_project_fails_only_as_the_headers_bigram(self):
        self.assertTrue(vl.nursery_mark(["body1", "project", "body2"], R0_HEARD, ["body1", "project", "body2"], True)["pass"],
                        "«project» alone is a body word")
        m = vl.nursery_mark(["body1", "project", "body2"], R0_HEARD, ["body1", "project", "gutenber"], True)
        self.assertFalse(m["pass"]); self.assertEqual(m["project_gutenberg_bigrams_heard"], 1)

    def test_out_of_order_fails(self):
        m = vl.nursery_mark(["body1", "body3", "body2"], R0_HEARD, [], True)
        self.assertFalse(m["pass"]); self.assertEqual(m["order_breaks_n"], 1)

    def test_undeclared_or_no_control_is_not_gradable(self):
        self.assertFalse(vl.nursery_mark(["body1"], R0_HEARD, [], False)["graded"])
        self.assertFalse(vl.nursery_mark(["body1"], None, [], True)["graded"])
        self.assertFalse(vl.nursery_mark(["zzz"], R0_HEARD, [], True)["graded"], "the first word absent from R0's list: no shift to read")

    def test_read_within_noise(self):
        ex = lambda s: [{"at": "x", "read_share": s, "read_words_n": 50}]
        self.assertTrue(vl.nursery_read_mark(ex(0.26), ex(0.44), True)["pass"])
        self.assertFalse(vl.nursery_read_mark(ex(0.10), ex(0.60), True)["pass"])
        self.assertFalse(vl.nursery_read_mark(ex(0.26), None, True)["graded"])
        self.assertFalse(vl.nursery_read_mark(ex(0.26), ex(0.44), False)["graded"])


class DropAndChat(unittest.TestCase):
    def test_drop_equality(self):
        self.assertTrue(vl.drop_equality_mark({"glances_confirmed": 5, "glances_dropped": 5}, True)["pass"])
        self.assertFalse(vl.drop_equality_mark({"glances_confirmed": 5, "glances_dropped": 4}, True)["pass"])
        m = vl.drop_equality_mark({"glances_confirmed": 5, "glances_dropped": 0}, False)
        self.assertFalse(m["graded"]); self.assertIn("ordinary", m["reason"])
        self.assertFalse(vl.drop_equality_mark({"glances_confirmed": 5}, True)["graded"])

    def test_chat_counters_never_fabricate_a_zero(self):
        m = vl.chat_counters_mark({"chats": 193, "chat_answered": 185}, True)
        self.assertEqual((m["chats"], m["chat_answered"], m["chat_refused_form"]), (193, 185, "not recorded"))
        self.assertFalse(m["graded"])


def _write_root(d: Path, order, genome_text: str, status: dict, heard=None, preds=()):
    (d / "tape").mkdir(parents=True); (d / "journal").mkdir(); (d / "exam").mkdir(); (d / "state").mkdir(); (d / "read").mkdir()
    tape, jr = _life(order)
    (d / "tape" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in tape))
    start = {"seq": None, "at": "2026-09-23T09:59:00.000Z", "event": "start"}; stop = {"seq": None, "at": "2026-09-23T10:30:00.000Z", "event": "stop"}
    (d / "journal" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [start] + jr + [stop]))
    (d / "STATUS.json").write_text(json.dumps(status)); (d / "GENOME.genome").write_text(genome_text)
    if heard is not None:
        (d / "read" / "HEARD.json").write_text(json.dumps(heard))
    (d / "state" / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in preds))


class TheLastLink(unittest.TestCase):
    """ladder2_read gathers every mark from fixture roots exactly as main() hands them in; ladder2_rows renders a row for each (#180)."""
    def test_ladder2_read_and_rows_on_fixture_roots(self):
        from genome.machinery import parse_genome
        all_text = (TREE / "genome" / "ladder2" / "A4L2-ALL.genome").read_text()
        order = [("maker", f"m{i}", [("sight", i, "n")], (i + 1, 1)) for i in range(120)]
        with tempfile.TemporaryDirectory() as td:
            a, b, c = Path(td) / "a", Path(td) / "b", Path(td) / "c"
            _write_root(a, order, all_text, {"glances_confirmed": 3, "glances_dropped": 3, "chats": 2},
                        heard=["body1", "body2"], preds=[_frame(True, Line.SHELF)])
            _write_root(b, order, all_text, {})
            _write_root(c, order, all_text, {}, heard=R0_HEARD)
            A = vg.side_record(a, 1.0)
            self.assertEqual(len(A["tape"]), 120); self.assertTrue(A["closed"])
            decl = parse_genome(all_text).declared
            M = vg.ladder2_read(a, {"t0": A["t0"], "exams": []}, A["tape"], A["mind"], A["status"], decl, 1.0, identity_root=b, control_root=c)
            self.assertEqual(set(M), {"IDENTITY", "X1_LOCK", "X2_SUCCESS", "LINE", "NURSERY", "NURSERY_READ", "DROP_EQ", "CHAT_COUNTERS", "A1_NULL", "A2_SEEN"})
            self.assertTrue(M["IDENTITY"]["pass"], M["IDENTITY"]["reason"])
            self.assertEqual(M["IDENTITY"]["streams"]["maker"]["compared"], 120)
            self.assertTrue(M["LINE"]["pass"]); self.assertTrue(M["NURSERY"]["pass"]); self.assertEqual(M["NURSERY"]["shift_measured"], 5)
            self.assertTrue(M["DROP_EQ"]["pass"]); self.assertEqual(M["CHAT_COUNTERS"]["chats"], 2)
            rows = vg.ladder2_rows(M)
            for name in ("IDENTITY", "X1_LOCK", "X2_SUCCESS", "LINE", "NURSERY", "NURSERY_READ", "DROP_EQ", "CHAT_COUNTERS", "A1 NULL", "A2 SEEN"):
                self.assertTrue(any(r.startswith("| " + name) for r in rows), name)
            M2 = vg.ladder2_read(a, {"t0": A["t0"], "exams": []}, A["tape"], A["mind"], A["status"], decl, 1.0)
            self.assertFalse(M2["IDENTITY"]["graded"]); self.assertFalse(M2["NURSERY"]["graded"])
            fail, ng, miss = vg.partition_marks(M2, {"pass": True})
            self.assertEqual(miss, [], "every v3.5 mark carries `graded`")

    def test_main_calls_the_gatherer_and_write_verdict_the_renderer(self):
        src = (TREE / "tools" / "verdict_g4.py").read_text()
        tree = ast.parse(src)
        fn = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        called = lambda f, name: any(isinstance(x, ast.Call) and getattr(x.func, "id", None) == name for x in ast.walk(fn[f]))
        self.assertTrue(called("main", "ladder2_read")); self.assertTrue(called("write_verdict", "ladder2_rows"))
        for flag in ("--identity-root", "--identity-hours", "--control-root", "--line-ceiling"):
            self.assertIn(f'"{flag}"', src)
        self.assertIn("v3.5", vg.READER_VERSION)


@unittest.skipUnless((SCRATCH / "a4l2-pre-floor-copy").exists() and (SCRATCH / "a4l2-pre-cost-copy").exists()
                     and (SCRATCH / "a4l2-pre-act-copy").exists() and (SCRATCH / "a4l2-pre-nursery-copy").exists(),
                     "the ladder-2 pre-flight copies are not on this box")
class TheRealPreflights(unittest.TestCase):
    """Controls on the CLOSED 20-min pre-flight records (copies): R0 vs R0b identical (the positive); R0 vs R1 (the act's value changes the game
    stream) and R0 vs R3 (the nursery changes the shelf stream from its first canvas) diverge (the negatives)."""
    def _id(self, a, b):
        A = vg.side_record(SCRATCH / a); B = vg.side_record(SCRATCH / b)
        return vl.identity_mark(A["tape"], A["mind"], B["tape"], B["mind"])

    def test_floor_vs_cost_is_identical(self):
        m = self._id("a4l2-pre-floor-copy", "a4l2-pre-cost-copy")
        self.assertTrue(m["pass"], m["reason"]); self.assertGreater(m["meeting_points"], 500)

    def test_floor_vs_act_diverges_on_the_game(self):
        m = self._id("a4l2-pre-floor-copy", "a4l2-pre-act-copy")
        self.assertFalse(m["pass"]); self.assertIsNotNone(m["streams"]["game"]["first_divergence"])
        self.assertIsNone(m["streams"]["folder"]["first_divergence"])

    def test_floor_vs_nursery_diverges_on_the_shelf_at_its_first_canvas(self):
        m = self._id("a4l2-pre-floor-copy", "a4l2-pre-nursery-copy")
        self.assertFalse(m["pass"]); self.assertEqual(m["streams"]["shelf"]["first_divergence"]["index"], 0)

    def test_the_nursery_shift_reads_79(self):
        r3 = json.loads((SCRATCH / "a4l2-pre-nursery-copy" / "read" / "HEARD.json").read_text())
        r0 = json.loads((SCRATCH / "a4l2-pre-floor-copy" / "read" / "HEARD.json").read_text())
        m = vl.nursery_mark(r3, r0, [], True)
        self.assertEqual(m["shift_measured"], 79); self.assertTrue(m["pass"], m["reason"])


if __name__ == "__main__":
    unittest.main()
