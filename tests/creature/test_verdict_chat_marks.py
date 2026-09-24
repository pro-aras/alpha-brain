# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:46 +0400 — A4L-LANG task 7 (docs/briefs/A4L-LANG.md;
# A4-LADDER-PREREG §3.4 L1-L9): tools/verdict_life.py:chat_marks, test-first on the shapes LANDED (#171/#173) —
# creature/mind.py:_consume_chat's out file and say row, tools/chat_seat.py's truth file, creature/senses/chat.py's rows.
from __future__ import annotations

import copy
import unittest

import numpy as np

from tools import verdict_life as V

DECL = {"CHAT": {"in": "chat/in", "out": "chat/out", "links_adjacent": 5, "pivot_distinct": 10, "pivot_instants": 20,
                 "max_words": 6, "teaches": False}}
BORN = "2026-09-23T16:00:00+00:00"
THINGS = ["circle", "square", "triangle", "cross", "ring", "bar", "dot", "star", "arrow", "wave", "diamond"]


def at_h(h: float) -> str:
    total = int(h * 3600); return f"2026-09-23T{16 + total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}.000Z"


class Rec:
    """A synthetic record in the landed shapes: tape rows (maker ear/eye + chat rows), the live journal (a hashed moment row
    per canvas + a say row per chat), chat/out and chat/truth."""
    def __init__(self):
        self.tape, self.journal, self.out, self.truth = [], [], {}, {}
        self.seq = 0
        for k in range(40):                  # forty «it is X» instants: the link «it is» (adjacent 40x) and the pivot «is» (12 followers)
            self._instant(["it", "is", f"x{k % 12}"], at_h(0.1))
        self.canvas(at_h(0.2))

    def _row(self, sense, meta, at):
        self.seq += 1; r = {"seq": self.seq, "at": at, "sense": sense, "sha": "0" * 64, "payload": f"payload/{self.seq:09d}.x", "meta": meta}
        self.tape.append(r); return r

    def _instant(self, words, at):
        m = f"m{self.seq}"
        for w in words:
            self._row("ear", {"moment": m, "source": "shelf", "word": w}, at)
        e = self._row("eye", {"moment": m, "source": "shelf"}, at)
        self.journal.append({"seq": e["seq"], "moment": m, "word": words[-1], "hash": f"h{e['seq']}"})

    def canvas(self, at):
        m = f"c{self.seq}"
        self._row("ear", {"moment": m, "source": "maker", "word": "ring"}, at)
        e = self._row("eye", {"moment": m, "source": "maker"}, at)
        self.journal.append({"seq": e["seq"], "moment": m, "word": "ring", "hash": f"h{e['seq']}"})

    def chat(self, cid, family, thing, content, hour, chain=None, lure=None, options=None, point=None, bboxes=None,
             grounded=True, candidates_n=2, links=None, pivot_followers=12, h_after=None):
        r = self._row("chat", {"moment": f"chat-{cid}", "source": "chat", "id": cid, "words": ["what", "is", "this"], "shown": "picture"}, at_h(hour))
        said = chain if chain is not None else (["it", "is", content] if content else [])
        say = {"kind": "chat", "id": cid, "heard": ["what", "is", "this"], "content": content, "grade": "sure", "chain": said,
               "form": ["it", "is"] if len(said) > 1 else [], "pivot": "is" if len(said) > 1 else None,
               "links": links if links is not None else ([["it", "is", 40, 40]] if len(said) > 1 else []),
               "pivot_followers": pivot_followers if len(said) > 1 else None, "point": point,
               "abstain_reason": None if content else "novel", "resembles": None, "refused": None, "road": "recall",
               "named_things": [], "edges": None, "grounded": ({"ok": grounded, "lit": 3, "edge": [1, 2, 0.4]} if content else None),
               "form_reason": None, "candidates_n": candidates_n, "truncated": False,
               "hash_before": "H", "hash_after": h_after or "H"}
        self.journal.append({"seq": r["seq"], "say": say})
        self.out[cid] = {"id": cid, "seq": r["seq"], "at": r["at"], "answer": said or None, **{k: v for k, v in say.items() if k != "kind"}}
        self.truth[cid] = {"id": cid, "family": family, "thing": thing, "lure": lure, "options": options or [], "other": None,
                           "bboxes": bboxes or {thing: [40, 40, 32, 32]}, "phrasing": "", "text": "", "k": 0, "hour": hour}
        self.canvas(at_h(hour))

    def blind(self):
        return [copy.deepcopy(j) for j in self.journal if "say" not in j]


def marks(rec, **kw):
    kw.setdefault("blind_journal", rec.blind()); kw.setdefault("born", BORN)
    return V.chat_marks(rec.out, rec.truth, rec.tape, rec.journal, kw.pop("exams", []), DECL, **kw)


def full_record(n=24, wrong=0, echo=0):
    rec = Rec()
    for i in range(n):
        t = THINGS[i % len(THINGS)]
        rec.chat(f"w{i}", "what-is", t, t if i >= wrong else THINGS[(i + 1) % len(THINGS)], 1.0 + i * 6.0 / n)
    for i in range(n):
        t = THINGS[i % len(THINGS)]; lure = t if i % 2 == 0 else THINGS[(i + 3) % len(THINGS)]
        content = lure if (i % 2 == 1 and i < 2 * echo) else t
        rec.chat(f"y{i}", "yes-no", t, content, 1.1 + i * 6.0 / n, lure=lure, options=[lure])
    for i in range(n):
        t = THINGS[i % len(THINGS)]; o = THINGS[(i + 5) % len(THINGS)]
        rec.chat(f"h{i}", "which", t, t, 1.2 + i * 6.0 / n, options=[t, o])
    for i in range(12):
        t = THINGS[i % len(THINGS)]
        rec.chat(f"p{i}", "where", t, t, 1.3 + i * 0.5, point={"glance": 0, "window": [40, 40], "word": t},
                 bboxes={t: [40, 40, 32, 32], "other": [0, 0, 32, 32]})
    rec.chat("n0", "what-is", "spiral", "dot", 2.0); rec.chat("n1", "what-is", "vex", None, 3.0)
    return rec


class TestNotGradableWithoutTheGene(unittest.TestCase):
    def test_every_mark_reads_not_gradable_on_a_record_that_did_not_declare_chat(self) -> None:
        M = V.chat_marks({}, {}, [], [], [], {"SENSE_GRADE": {}})
        for k in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9"):
            self.assertFalse(M[k]["graded"], k); self.assertIn("CHAT not declared", M[k]["reason"])


class TestL1ReadOnly(unittest.TestCase):
    def test_the_law_holds_when_the_twin_matches_and_every_hash_pair_agrees(self) -> None:
        M = marks(full_record())
        self.assertTrue(M["L1"]["graded"]); self.assertTrue(M["L1"]["pass"], M["L1"])
        self.assertEqual(M["L1"]["say_rows"], M["L1"]["hash_equal"])

    def test_a_twin_that_differs_by_one_hash_fails_the_law(self) -> None:
        rec = full_record(); tw = rec.blind(); tw[5]["hash"] = "planted"
        M = marks(rec, blind_journal=tw)
        self.assertFalse(M["L1"]["pass"]); self.assertEqual(M["L1"]["twin_first_difference"][1], "hash")

    def test_one_hash_pair_that_differs_fails_the_law(self) -> None:
        rec = full_record(); rec.chat("bad", "what-is", "ring", "ring", 5.0, h_after="H2")
        self.assertFalse(marks(rec)["L1"]["pass"])

    def test_no_twin_run_fails_its_clause_by_name(self) -> None:
        M = marks(full_record(), blind_journal=None)
        self.assertFalse(M["L1"]["pass"]); self.assertIn("not run", M["L1"]["reason"])


class TestL2WhatIs(unittest.TestCase):
    def test_precision_abstention_and_the_bar_from_the_nearest_exam(self) -> None:
        exams = [{"at": "2026-09-23T17:00:00+00:00", "ask_seen_words": {"Q1": {"acc": 0.95}}},
                 {"at": "2026-09-23T20:00:00+00:00", "ask_seen_words": {"Q1": {"acc": 0.99}}}]
        # 40 items over 11 things: the shuffled twin's p95 sits under 0.20 (at 24 items it reads 5/24 = 0.208 — a small-n
        # property of that null, reported, never a loosened bar)
        M = marks(full_record(n=40, wrong=2), exams=exams)
        L2 = M["L2"]
        self.assertTrue(L2["graded"]); self.assertEqual((L2["answered"], L2["correct"]), (40, 38))
        self.assertAlmostEqual(L2["precision"], 38 / 40, places=4)
        self.assertGreater(L2["bar_precision"], 0.8)
        self.assertEqual(L2["abstention_seen"], 0.0)
        self.assertIsNotNone(L2["shuffled_p95"])
        self.assertTrue(L2["pass"], L2)

    def test_the_null_things_are_excluded_and_printed_in_l9(self) -> None:
        M = marks(full_record())
        self.assertEqual(M["L2"]["items"], 24)
        self.assertEqual(sorted(M["L9"]["said"]), ["spiral", "vex"])
        self.assertEqual(M["L9"]["said"]["vex"][0]["said"], "(I do not know) — novel")

    def test_under_20_answered_is_not_gradable(self) -> None:
        self.assertFalse(marks(full_record(n=10))["L2"]["graded"])


class TestL3YesNo(unittest.TestCase):
    def test_echo_counts_only_wrong_lures(self) -> None:
        M = marks(full_record(echo=3))
        L3 = M["L3"]
        self.assertEqual(L3["wrong_lures_answered"], 12); self.assertEqual(L3["echo"], 3)
        self.assertAlmostEqual(L3["echo_rate"], 3 / 12, places=4)
        self.assertFalse(L3["pass"], "an echo rate of 0.25 > 0.10")
        self.assertAlmostEqual(L3["echo_twin_precision"], 0.5, places=4)

    def test_no_echo_passes(self) -> None:
        self.assertTrue(marks(full_record())["L3"]["pass"])


class TestL4Which(unittest.TestCase):
    def test_precision_over_answered(self) -> None:
        M = marks(full_record())
        self.assertTrue(M["L4"]["graded"]); self.assertEqual(M["L4"]["precision"], 1.0); self.assertTrue(M["L4"]["pass"])


class TestL5Where(unittest.TestCase):
    def test_graded_on_the_pointing_ceiling_and_the_bbox(self) -> None:
        M = marks(full_record(), pointing_ceiling=0.84)
        self.assertTrue(M["L5"]["graded"]); self.assertEqual(M["L5"]["point_rate"], 1.0)
        self.assertAlmostEqual(M["L5"]["bar"], 0.69, places=4); self.assertTrue(M["L5"]["pass"])

    def test_a_point_outside_the_bbox_is_a_miss(self) -> None:
        rec = full_record()
        for cid in [c for c in rec.out if c.startswith("p")][:6]:
            rec.out[cid]["point"] = {"glance": 0, "window": [0, 90], "word": rec.truth[cid]["thing"]}
        M = marks(rec, pointing_ceiling=0.84)
        self.assertEqual(M["L5"]["point_rate"], 0.5); self.assertFalse(M["L5"]["pass"])

    def test_not_gradable_under_the_ceiling(self) -> None:
        M = marks(full_record(), pointing_ceiling=0.4)
        self.assertFalse(M["L5"]["graded"]); self.assertIn("pointing ceiling is 0.4", M["L5"]["reason"])


class TestL6Length(unittest.TestCase):
    def test_share_of_correct_answers_with_three_words_from_hour_4(self) -> None:
        M = marks(full_record())
        L6 = M["L6"]
        self.assertTrue(L6["graded"]); self.assertEqual(L6["share_3plus"], 1.0); self.assertTrue(L6["pass"])
        self.assertEqual(L6["longest"], 3); self.assertIn("4", {str(k) for k in L6["per_hour"]})

    def test_not_gradable_when_no_chat_ever_had_a_candidate(self) -> None:
        rec = Rec()
        for i in range(24):
            rec.chat(f"w{i}", "what-is", "ring", "ring", 4.5, chain=["ring"], candidates_n=0)
        self.assertFalse(marks(rec)["L6"]["graded"])


class TestL7GroundedCited(unittest.TestCase):
    def test_grounded_and_cited_by_the_record_and_by_the_tape(self) -> None:
        M = marks(full_record())
        L7 = M["L7"]
        self.assertTrue(L7["pass"], L7)
        self.assertGreaterEqual(L7["tape_min_link_adjacency"], 5); self.assertGreaterEqual(L7["tape_min_pivot_followers"], 10)

    def test_an_ungrounded_said_content_fails(self) -> None:
        rec = full_record(); rec.chat("u", "what-is", "ring", "ring", 5.0, grounded=False)
        self.assertFalse(marks(rec)["L7"]["pass"])

    def test_a_link_the_tape_never_heard_adjacent_fails(self) -> None:
        rec = full_record(); rec.chat("z", "what-is", "ring", "ring", 5.0, chain=["big", "is", "ring"], links=[["big", "is", 40, 40]])
        M = marks(rec)
        self.assertFalse(M["L7"]["pass"]); self.assertIn("big is", " ".join(M["L7"]["tape_short_links"]))


class TestL8AndDisjoint(unittest.TestCase):
    def test_the_seats_grades_are_printed_per_family(self) -> None:
        rec = full_record()
        rec.journal.append({"seq": 9999, "grade": {"id": "w0", "right": True, "novel": False, "kind": "chat"}})
        rec.journal.append({"seq": 9999, "grade": {"id": "y1", "right": False, "novel": False, "kind": "chat"}})
        M = marks(rec)
        self.assertFalse(M["L8"]["graded"])
        self.assertEqual(M["L8"]["by_family"], {"what-is": {"right": 1, "wrong": 0}, "yes-no": {"right": 0, "wrong": 1}})

    def test_the_disjointness_check_and_its_planted_control(self) -> None:
        rng = np.random.default_rng(0)
        seen = [rng.integers(0, 255, size=(8, 8, 3), dtype=np.uint8) for _ in range(5)]
        pics = {"c1": rng.integers(0, 255, size=(8, 8, 3), dtype=np.uint8)}
        M = marks(full_record(), tape_canvases=seen, chat_pics=pics)
        self.assertEqual(M["disjoint"]["checked"], 1); self.assertTrue(M["disjoint"]["control_caught"])
        M2 = marks(full_record(), tape_canvases=seen + [pics["c1"].copy()], chat_pics=pics)
        self.assertFalse(M2["disjoint"]["ok"])


if __name__ == "__main__":
    unittest.main()
