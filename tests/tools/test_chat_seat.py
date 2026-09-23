# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:42 +0400 — A4L-LANG task 6 (docs/briefs/A4L-LANG.md;
# A4-LADDER-PREREG §3.3): tools/chat_seat.py, the seat's side of the door — test-first on the DEV phrasings only (the
# life's TEST phrasings are the orchestrator's and are never opened here).
from __future__ import annotations

import ast
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from genome import world
from tools import chat_seat as S

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "tools" / "chat_dev_phrasings.json"


class TestPhrasings(unittest.TestCase):
    def test_the_dev_file_loads_four_families_and_ignores_underscore_keys(self) -> None:
        P = S.load_phrasings(DEV)
        self.assertEqual(sorted(P), ["what-is", "where", "which", "yes-no"])
        self.assertEqual(P["which"], ["is it a {X} or a {Y}"])

    def test_a_missing_family_refuses(self) -> None:
        d = Path(tempfile.mkdtemp()); p = d / "p.json"
        p.write_text(json.dumps({"what-is": ["what is this"], "yes-no": ["is this a {X}"], "which": ["is it a {X} or a {Y}"]}))
        with self.assertRaises(ValueError):
            S.load_phrasings(p)
        shutil.rmtree(d)

    def test_fill_places_the_thing_names(self) -> None:
        self.assertEqual(S.fill("is it a {X} or a {Y}", "ring", "star"), "is it a ring or a star")
        self.assertEqual(S.fill("what is this", "ring"), "what is this")


class TestTheSchedule(unittest.TestCase):
    def test_the_seven_slot_cycle_gives_60_60_60_30_over_hours_1_to_8(self) -> None:
        fams = [S.CYCLE[k % 7] for k in range(S.n_slots(1, 8, 120))]
        self.assertEqual(len(fams), 210)
        self.assertEqual({f: fams.count(f) for f in set(fams)}, {"what-is": 60, "yes-no": 60, "which": 60, "where": 30})

    def test_the_things_follow_the_worlds_own_schedule(self) -> None:
        self.assertEqual(S.things_at(1.0), list(world.THINGS_11))
        self.assertEqual(S.things_at(4.9), list(world.THINGS_11))
        self.assertEqual(S.things_at(5.0), list(world.THINGS_11) + list(world.THINGS_ARRIVAL2))
        for h in (1.0, 5.0, 7.9):
            for t in ("spiral", "vex", "zog"):
                self.assertNotIn(t, S.things_at(h))

    def test_one_what_is_in_ten_is_a_never_seen_thing(self) -> None:
        P = S.load_phrasings(DEV)
        plans = [S.plan_slot(k, 20260923, P, hour=1.0 + k * 120 / 3600) for k in range(210)]
        whatis = [p for p in plans if p["family"] == "what-is"]
        null = [p["thing"] for p in whatis if p["thing"] in ("spiral", "vex")]
        self.assertEqual(len(whatis), 60)
        self.assertEqual(null, ["spiral", "vex", "spiral", "vex", "spiral", "vex"])

    def test_deterministic_from_the_seed(self) -> None:
        P = S.load_phrasings(DEV)
        a, b = S.plan_slot(17, 20260923, P, hour=2.0), S.plan_slot(17, 20260923, P, hour=2.0)
        self.assertEqual({k: v for k, v in a.items() if k != "picture"}, {k: v for k, v in b.items() if k != "picture"})
        self.assertTrue(np.array_equal(a["picture"], b["picture"]))
        c = S.plan_slot(17, 7, P, hour=2.0)
        self.assertNotEqual((a["thing"], a["text"], a["picture"].tobytes()), (c["thing"], c["text"], c["picture"].tobytes()))

    def test_each_family_carries_its_truth(self) -> None:
        P = S.load_phrasings(DEV)
        seen = {}
        for k in range(14):
            p = S.plan_slot(k, 20260923, P, hour=1.5)
            seen.setdefault(p["family"], p)
        yn, wh, wr = seen["yes-no"], seen["which"], seen["where"]
        self.assertEqual(yn["options"], [yn["lure"]]); self.assertIn(yn["lure"], S.things_at(1.5))
        self.assertIn(yn["text"], ("is this a " + yn["lure"],))
        self.assertEqual(sorted(wh["options"]), sorted([wh["thing"], wh["other"]])); self.assertIn(wh["thing"], wh["options"])
        self.assertIn(wr["thing"], wr["bboxes"]); self.assertIn(wr["other"], wr["bboxes"])
        self.assertEqual(wr["text"], "where is the " + wr["thing"])

    def test_the_lure_is_wrong_about_half_the_time(self) -> None:
        P = S.load_phrasings(DEV)
        yns = [p for p in (S.plan_slot(k, 20260923, P, hour=2.0) for k in range(210)) if p["family"] == "yes-no"]
        wrong = sum(1 for p in yns if p["lure"] != p["thing"])
        self.assertTrue(20 <= wrong <= 40, wrong)


class TestPictures(unittest.TestCase):
    def test_a_single_thing_is_a_held_out_render_on_seed_3(self) -> None:
        P = S.load_phrasings(DEV)
        p = S.plan_slot(0, 20260923, P, hour=1.0)
        want, _truth = world.render_canvas(p["thing"], np.random.default_rng([3, 0]))
        self.assertTrue(np.array_equal(p["picture"], want))

    def test_the_where_composite_holds_two_things_that_never_overlap(self) -> None:
        for k in range(20):
            rgb, boxes = S.render_two("ring", "star", np.random.default_rng([3, k]))
            self.assertEqual(rgb.shape, (128, 128, 3))
            (ta, la, ha, wa), (tb, lb, hb, wb) = boxes["ring"], boxes["star"]
            self.assertTrue(ta + ha <= tb or tb + hb <= ta or la + wa <= lb or lb + wb <= la, boxes)
            for t, l, h, w in boxes.values():
                self.assertTrue(0 <= t and t + h <= 128 and 0 <= l and l + w <= 128)


class TestWriting(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_the_truth_is_written_before_the_chat_and_the_chat_never_carries_it(self) -> None:
        P = S.load_phrasings(DEV)
        order = []
        real = S._atomic_write
        def spy(path, data):
            order.append(Path(path).parent.name); return real(path, data)
        S._atomic_write = spy
        try:
            S.write_chat(self.root, S.plan_slot(2, 20260923, P, hour=1.2))
        finally:
            S._atomic_write = real
        self.assertEqual(order, ["truth", "pics", "in"])
        chat = json.loads((self.root / "chat" / "in" / "c0002.json").read_text())
        self.assertEqual(sorted(chat), ["id", "picture", "text"])
        truth = json.loads((self.root / "chat" / "truth" / "c0002.json").read_text())
        for k in ("id", "family", "thing", "lure", "options", "bboxes", "phrasing"):
            self.assertIn(k, truth)

    def test_writing_twice_is_idempotent(self) -> None:
        P = S.load_phrasings(DEV)
        p = S.plan_slot(3, 20260923, P, hour=1.2)
        self.assertTrue(S.write_chat(self.root, p)); self.assertFalse(S.write_chat(self.root, p))

    def test_say_writes_a_free_line_with_no_picture(self) -> None:
        cid = S.say(self.root, "hello, who are you?")
        self.assertEqual(cid, "s0001")
        self.assertEqual(json.loads((self.root / "chat" / "in" / "s0001.json").read_text()), {"id": "s0001", "text": "hello, who are you?"})
        self.assertEqual(json.loads((self.root / "chat" / "truth" / "s0001.json").read_text())["family"], "free")
        self.assertEqual(S.say(self.root, "again"), "s0002")

    def test_grade_writes_the_grade_senses_own_shape(self) -> None:
        S.grade(self.root, "s0001", right=True, novel=True)
        self.assertEqual(json.loads((self.root / "chat" / "graded" / "s0001.json").read_text()), {"id": "s0001", "right": True, "novel": True})

    def test_the_burst_is_n_dev_what_is_between_two_minutes(self) -> None:
        born = datetime(2026, 9, 23, 16, 0, tzinfo=timezone.utc)
        plans = S.burst_plans(10, 20260923, S.load_phrasings(DEV), born, from_min=12, to_min=16)
        self.assertEqual(len(plans), 10)
        self.assertTrue(all(p["family"] == "what-is" and p["text"] == "what is this" for p in plans))
        self.assertEqual(plans[0]["due"], born + timedelta(minutes=12)); self.assertEqual(plans[-1]["due"], born + timedelta(minutes=16))
        self.assertTrue(all(p["thing"] in world.THINGS_11 for p in plans))
        self.assertEqual(len({p["id"] for p in plans}), 10)

    def test_slot_times_run_every_120_s_from_hour_1_to_hour_8(self) -> None:
        born = datetime(2026, 9, 23, 16, 0, tzinfo=timezone.utc)
        due = [S.slot_due(born, k, 1, 120) for k in range(S.n_slots(1, 8, 120))]
        self.assertEqual(due[0], born + timedelta(hours=1)); self.assertEqual(due[-1], born + timedelta(hours=8) - timedelta(seconds=120))

    def test_born_is_read_from_the_lifes_started_at(self) -> None:
        (self.root / "STARTED-AT").write_text("2026-09-23 20:05 +0400\n")
        self.assertEqual(S.born_of(self.root), datetime(2026, 9, 23, 16, 5, tzinfo=timezone.utc))


class TestTheSeatNeverImportsTheMind(unittest.TestCase):
    def test_no_import_of_creature_mind_or_the_machinery(self) -> None:
        tree = ast.parse((ROOT / "tools" / "chat_seat.py").read_text())
        names = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                names += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                names.append(n.module or ""); names += [f"{n.module}.{a.name}" for a in n.names]
        for bad in ("creature.mind", "genome.machinery", "creature.body", "creature.replay"):
            self.assertFalse(any(x == bad or x.startswith(bad + ".") for x in names), bad)


if __name__ == "__main__":
    unittest.main()
