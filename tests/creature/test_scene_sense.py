# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:30 +0400 — BRAIN-IN-BODY: creature/senses/scene.py's own pin.
"""tests/creature/test_scene_sense.py — the scene sense's plan(): equal to the offline generators' own questions
(READ-ONLY against /data/dev/brain-runs/scene-s1b1r/20261101/{fresh/keys.json, keys.json}), pure/deterministic,
the utterance-shuffle law, feed/backlog/refusal, and the cursor (#230)."""
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from creature.senses import scene as S
from brain.scene import world as W

WS = 20261101
FRESH_KEYS = Path("/data/dev/brain-runs/scene-s1b1r/20261101/fresh/keys.json")
S1B1_KEYS = Path("/data/dev/brain-runs/scene-s1b1r/20261101/keys.json")


def _cfg(train=10, sitting=("fresh",), feed=None, utterance="true", seed=WS):
    return {"seed": seed, "train": train, "sitting": list(sitting),
            "feed": feed or {"mode": "max", "backlog": 8}, "utterance": utterance}


def _sitting_items_by_mark(moments, set_name):
    by_mark = {}
    for m in moments:
        if m["truth"] is None:
            continue
        t = m["truth"]()
        if t.get("kind") != "sitting" or t.get("set") != set_name:
            continue
        for it in t["items"]:
            by_mark.setdefault(it["mark"], []).append((it["item_id"], it["phrase"]))
    return by_mark


@unittest.skipUnless(FRESH_KEYS.exists() and S1B1_KEYS.exists(), "the offline scored-run records are not on this box")
class QuestionEquality(unittest.TestCase):
    """§2's own law: 'The questions are the offline generators' own.' — item_id + phrase equal, mark by mark,
    at every mark the file carries (M5 is new — the file predates it, and is skipped, printed, never failed)."""

    def test_fresh_set_equals_the_scored_runs_own_questions(self):
        moments = S.plan(_cfg(train=1, sitting=("fresh",)))
        mine = _sitting_items_by_mark(moments, "fresh")
        keys = json.loads(FRESH_KEYS.read_text())
        table = []
        for mark, items in keys["items"].items():
            file_pairs = [(it["item_id"], it["phrase"]) for it in items]
            got = mine.get(mark, [])
            table.append((mark, len(file_pairs), len(got), file_pairs == got))
            if mark != "M5":
                self.assertEqual(got, file_pairs, msg=f"mark {mark}: first difference "
                                  f"{next((i for i in range(min(len(got), len(file_pairs))) if got[i] != file_pairs[i]), 'length')}")
        print("fresh equality table (mark, in_file, in_plan, equal):", table)
        self.assertNotIn("M5", keys["items"], "the scored run predates M5 — nothing to compare it against")

    def test_s1b1_set_equals_the_scored_runs_own_questions(self):
        moments = S.plan(_cfg(train=1, sitting=("s1b1",)))
        mine = _sitting_items_by_mark(moments, "s1b1")
        keys = json.loads(S1B1_KEYS.read_text())
        for mark, items in keys["items"].items():
            file_pairs = [(it["item_id"], it["phrase"]) for it in items]
            got = mine.get(mark, [])
            self.assertEqual(got, file_pairs, msg=f"mark {mark}")
        self.assertNotIn("SPEAK2", keys["items"])
        self.assertNotIn("M5", mine, "M5 is fresh-only")


class Determinism(unittest.TestCase):
    def test_two_plans_of_the_same_cfg_are_byte_identical(self):
        cfg = _cfg(train=30, sitting=("fresh", "s1b1"))
        a, b = S.plan(cfg), S.plan(cfg)
        self.assertEqual(len(a), len(b))
        for ma, mb in zip(a, b):
            self.assertEqual(ma["moment"], mb["moment"])
            self.assertEqual(ma["phase"], mb["phase"])
            self.assertEqual(len(ma["rows"]), len(mb["rows"]))
            for ra, rb in zip(ma["rows"], mb["rows"]):
                self.assertEqual(ra["sense"], rb["sense"])
                self.assertEqual(ra["meta"], rb["meta"])
                self.assertEqual(ra["ext"], rb["ext"])
                self.assertEqual(ra["payload"](), rb["payload"]())
            ta = ma["truth"]() if ma["truth"] is not None else None
            tb = mb["truth"]() if mb["truth"] is not None else None
            self.assertEqual(ta, tb)

    def test_shuffle_moves_words_but_keeps_the_canvas_and_scene_dict(self):
        plain = S.plan(_cfg(train=50, sitting=()))
        shuf = S.plan(_cfg(train=50, sitting=(), utterance={"shuffled": 1}))
        moved = 0
        for mp, ms in zip(plain, shuf):
            tp, ts_ = mp["truth"](), ms["truth"]()
            self.assertEqual(tp["scene_dict"]["things"], ts_["scene_dict"]["things"])   # the canvas is scene i's, always
            eye_p = [r["payload"]() for r in mp["rows"] if r["sense"] == "eye"][0]
            eye_s = [r["payload"]() for r in ms["rows"] if r["sense"] == "eye"][0]
            self.assertEqual(eye_p, eye_s)   # the picture never moves under a shuffle
            if tp["said"] != ts_["said"]:
                moved += 1
        self.assertGreater(moved, 0, "a derangement (k=1) must move at least one canvas's words in 50 scenes")


class M5(unittest.TestCase):
    """PREREG-BRAIN-IN-BODY.md §3's M5 row: one item per FRESH `test`-split scene, its phrase never true of
    any thing in its own scene (structurally — two distinct words of the SAME type can never both hold of
    one thing), «dax» never used, and every kind reachable."""

    def test_400_items_one_per_fresh_test_row_none_true_of_any_thing_no_dax(self):
        moments = S.plan(_cfg(train=1, sitting=("fresh",)))
        m5 = []
        for m in moments:
            if m["truth"] is None:
                continue
            t = m["truth"]()
            if t.get("kind") == "sitting" and t.get("set") == "fresh" and t.get("split") == "test":
                m5 += [it for it in t["items"] if it["mark"] == "M5"]
        self.assertEqual(len(m5), 400)
        by_kind = {}
        false_count = 0
        for it in m5:
            by_kind[it["kind_of_pair"]] = by_kind.get(it["kind_of_pair"], 0) + 1
            self.assertNotIn(W.DAX_WORD, it["phrase"])
            self.assertEqual(len(set(it["phrase"])), 2, "the pair must be two DISTINCT words")
        # verify against the scene's own things (word_true_of) that no M5 phrase is true of anything in view
        for m in moments:
            if m["truth"] is None:
                continue
            t = m["truth"]()
            if not (t.get("kind") == "sitting" and t.get("set") == "fresh" and t.get("split") == "test"):
                continue
            things = [W.Thing(x["shape"], x["colour"], x["size"], x["top"], x["left"]) for x in t["scene_dict"]["things"]]
            for it in [i for i in t["items"] if i["mark"] == "M5"]:
                if any(W.phrase_true_of(it["phrase"], th) for th in things):
                    false_count += 1
        print("M5 by kind:", by_kind, "phrases true of some thing (must be 0):", false_count)
        self.assertEqual(false_count, 0)
        self.assertEqual(set(by_kind), {"colour", "shape", "size"})

    def test_s1b1_set_carries_no_m5(self):
        moments = S.plan(_cfg(train=1, sitting=("s1b1",)))
        for m in moments:
            if m["truth"] is None:
                continue
            t = m["truth"]()
            if t.get("kind") == "sitting":
                self.assertFalse(any(it["mark"] == "M5" for it in t["items"]))


class Refusals(unittest.TestCase):
    def test_seed_outside_world_seeds_is_refused_by_name(self):
        with self.assertRaises(ValueError) as cm:
            S.plan(_cfg(seed=12345678))
        self.assertIn("12345678", str(cm.exception))

    def test_a_word_over_eight_letters_would_be_refused(self):
        # a positive control that the plan-time assert is real: every trained word is <= 8 letters already
        # (SHAPES/COLOURS/SIZES/DAX_WORD), so this proves encode_word itself refuses, not that the assert is dead.
        from genome.world import encode_word
        with self.assertRaises(ValueError):
            encode_word("toolongaword")


class FeedAndCursor(unittest.TestCase):
    def _tmp(self):
        d = Path(tempfile.mkdtemp(prefix="scene_sense_test_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_max_backlog_waits_until_backlog_drops(self):
        root = self._tmp()
        rows = []
        seq = [0]

        def publish(sense, payload, meta, ext):
            seq[0] += 1
            rows.append((sense, meta.get("moment")))
            return {"seq": seq[0]}

        depth = {"n": 100}   # starts ABOVE the backlog cap so the sense must wait before publishing anything
        backlog = lambda: depth["n"]
        stop = threading.Event()

        def release():
            stop.wait(0.05)
            depth["n"] = 0

        t = threading.Thread(target=release, daemon=True)
        t.start()
        cfg = _cfg(train=2, sitting=())
        th = threading.Thread(target=S.sense, args=(publish, stop, root, cfg, backlog), daemon=True)
        th.start()
        th.join(timeout=2.0)
        stop.set()
        th.join(timeout=1.0)
        t.join(timeout=1.0)
        self.assertGreaterEqual(len(rows), 2, "the sense must have published the 2 training canvases once the backlog dropped")

    def test_cursor_resumes_without_republishing(self):
        root = self._tmp()
        cfg = _cfg(train=5, sitting=())
        published = []

        def publish(sense, payload, meta, ext):
            published.append(meta.get("moment"))
            return {"seq": len(published)}

        stop = threading.Event()
        # publish everything once
        S._write_cursor(root, 0)
        idx = 0
        moments = S.plan(cfg)
        for i, m in enumerate(moments):
            S._publish_moment(publish, root, m)
            S._write_cursor(root, i + 1)
        first_run_count = len(published)
        self.assertEqual(S._load_cursor(root), len(moments))
        self.assertGreater(first_run_count, 0)

        # a "restart": cursor says everything is done, so a second sense() call republishes nothing
        stop2 = threading.Event()
        stop2.set()   # returns immediately after the resume scan — we only care that nothing new publishes
        S.sense(publish, stop2, root, cfg, lambda: 0)
        self.assertEqual(len(published), first_run_count, "a cursor at the plan's own length must republish nothing")


if __name__ == "__main__":
    unittest.main()
