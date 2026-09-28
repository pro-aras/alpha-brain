# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:01 +0400 — PREREG-S1C §1 (genome-wt-brain3 docs/brain/r3/PREREG-S1C.md, sha a552515a…)
# and its AMENDMENT 1 §1–§2 (PREREG-S1C-AMEND-1.md, sha 825f4ad8…): the six ROOMS carved from S1's world. R1–R3 draw only
# their two shapes' ALLOWED pairs and the parent is TRUE; N's utterance is a template of trained words drawn INDEPENDENT of
# the things; U says ONE true word, the colour iff [shape ∈ {circle, triangle, ring}] XOR [size = big]; K is ONE spec
# re-rendered per visit. Every visit pool holds 2,000 scenes (AMENDMENT 1 §1) and a visit past the pool RAISES — it never
# wraps. Test-first: red on scene-s1b1 7706371 (brain.scene.rooms does not exist there).
from __future__ import annotations

import collections
import unittest

import numpy as np

from brain.scene import rooms as RM
from brain.scene import world as W

SEED = 20261301


class TestConstants(unittest.TestCase):
    def test_the_preregs_numbers(self) -> None:
        self.assertEqual(RM.ROOMS, ("R1", "R2", "R3", "N", "K", "U"))
        self.assertEqual(RM.ROOM_SHAPES, {"R1": ("circle", "square"), "R2": ("triangle", "cross"), "R3": ("ring", "star")})
        self.assertEqual((RM.N_VISIT, RM.N_WINDOW, RM.K_WINDOW), (2000, 40, 1))
        self.assertEqual(RM.S1C_SEEDS, (20261301, 20261302, 20261303))
        self.assertEqual(RM.K_THING, W.Thing("star", "red", "big", 48, 48))
        self.assertEqual(RM.K_WORDS, W.template_words("T2", RM.K_THING))
        self.assertEqual(len(RM.VOCAB13), 13)
        self.assertEqual(set(RM.VOCAB13), set(W.SHAPES) | set(W.COLOUR_NAMES) | set(W.SIZE_NAMES))
        self.assertNotIn(W.DAX_WORD, RM.VOCAB13)

    def test_n_slot_types_are_the_templates(self) -> None:
        t = W.Thing("circle", "red", "big", 0, 0)
        for tpl in W.TEMPLATES:
            self.assertEqual(RM.SLOT_TYPES[tpl], tuple(W.word_type(w) for w in W.template_words(tpl, t)))


class TestPools(unittest.TestCase):
    def test_a_visit_past_the_pool_raises_never_wraps(self) -> None:
        for r in RM.ROOMS:
            RM.room_scene(SEED, r, "visit", RM.N_VISIT - 1)
            with self.assertRaises(RM.RoomError):
                RM.room_scene(SEED, r, "visit", RM.N_VISIT)
            with self.assertRaises(RM.RoomError):
                RM.room_scene(SEED, r, "visit", -1)
            n_win = RM.K_WINDOW if r == "K" else RM.N_WINDOW
            self.assertEqual(RM.pool_size(r, "window"), n_win)
            RM.room_scene(SEED, r, "window", n_win - 1)
            with self.assertRaises(RM.RoomError):
                RM.room_scene(SEED, r, "window", n_win)
        with self.assertRaises(RM.RoomError):
            RM.room_scene(SEED, "X", "visit", 0)
        with self.assertRaises(RM.RoomError):
            RM.room_scene(SEED, "R1", "test", 0)

    def test_a_scene_is_a_function_of_seed_room_kind_index(self) -> None:
        a = [RM.room_scene(SEED, r, "visit", i) for r in RM.ROOMS for i in (0, 7, 1999)]
        b = [RM.room_scene(SEED, r, "visit", i) for r in reversed(RM.ROOMS) for i in (1999, 7, 0)]
        self.assertEqual(sorted(s.item_id for s in a), sorted(s.item_id for s in b))
        by = {s.item_id: s for s in b}
        for s in a:
            self.assertEqual(s, by[s.item_id])
        self.assertNotEqual(RM.room_scene(SEED, "R1", "visit", 3).things, RM.room_scene(SEED + 1, "R1", "visit", 3).things)
        self.assertNotEqual(RM.room_scene(SEED, "R1", "visit", 3).things, RM.room_scene(SEED, "R1", "window", 3).things)

    def test_item_ids_name_the_room_the_kind_and_the_index(self) -> None:
        s = RM.room_scene(SEED, "N", "window", 12)
        self.assertEqual(s.item_id, f"room:N:window:{SEED}:00012")
        self.assertEqual((s.split, s.index, s.seed), ("room:N:window", 12, SEED))


class TestLearnableRooms(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sc = {r: [RM.room_scene(SEED, r, "visit", i) for i in range(400)] for r in ("R1", "R2", "R3")}

    def test_only_the_rooms_two_shapes_in_allowed_pairs_both_sizes(self) -> None:
        for r, sc in self.sc.items():
            shapes, pairs, sizes = set(), set(), set()
            for s in sc:
                for t in s.things:
                    self.assertIn(t.shape, RM.ROOM_SHAPES[r])
                    self.assertIn((t.shape, t.colour), W.ALLOWED)
                    shapes.add(t.shape); pairs.add((t.shape, t.colour)); sizes.add(t.size)
            self.assertEqual(shapes, set(RM.ROOM_SHAPES[r]))
            self.assertEqual(pairs, {p for p in W.ALLOWED if p[0] in RM.ROOM_SHAPES[r]})
            self.assertEqual(sizes, set(W.SIZE_NAMES))

    def test_the_mix_and_a_true_parent(self) -> None:
        n = collections.Counter()
        for sc in self.sc.values():
            for s in sc:
                n[len(s.things)] += 1
                self.assertIn(s.template, W.TEMPLATES)
                self.assertEqual(s.words, W.template_words(s.template, s.things[s.referent]))
                for a in range(len(s.things)):
                    for b in range(a + 1, len(s.things)):
                        self.assertGreaterEqual(W.box_gap(s.things[a], s.things[b]), W.SEPARATION_PX)
        tot = sum(n.values())
        for k, p in W.SCENE_MIX:
            self.assertAlmostEqual(n[k] / tot, p, delta=0.05)

    def test_r2_has_no_yellow_the_fact_amendment_1_records(self) -> None:
        cols = {t.colour for s in self.sc["R2"] for t in s.things}
        self.assertNotIn("yellow", cols)
        self.assertEqual(cols, {"blue", "green", "red", "white"})


class TestNoisyTV(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sc = [RM.room_scene(SEED, "N", "visit", i) for i in range(1000)]

    def test_template_of_trained_words_independent_of_the_things(self) -> None:
        true_rate, words = [], collections.Counter()
        for s in self.sc:
            self.assertIn(s.template, W.TEMPLATES)
            self.assertIsNone(s.referent)
            self.assertEqual(tuple(W.word_type(w) for w in s.words), RM.SLOT_TYPES[s.template])
            for w in s.words:
                self.assertIn(w, RM.VOCAB13)
                words[w] += 1
            true_rate.append(any(W.phrase_true_of(s.words, t) for t in s.things))
            for t in s.things:
                self.assertIn((t.shape, t.colour), W.ALLOWED)       # S1's full generator for the SCENE
        # a true parent would read 1.0; words independent of the things read the base rate (≈ 0.13, the S1b-1 follow-up's A1)
        self.assertLess(float(np.mean(true_rate)), 0.25)
        self.assertEqual(set(words), set(RM.VOCAB13))               # every trained word is uttered


class TestUnlearnable(unittest.TestCase):
    def test_one_true_word_colour_iff_xor(self) -> None:
        kinds = collections.Counter()
        for i in range(600):
            s = RM.room_scene(SEED, "U", "visit", i)
            t = s.things[s.referent]
            self.assertEqual(len(s.words), 1)
            self.assertTrue(W.word_true_of(s.words[0], t))
            colour = (t.shape in ("circle", "triangle", "ring")) != (t.size == "big")
            self.assertEqual(s.words[0], t.colour if colour else t.shape)
            kinds[(t.shape in ("circle", "triangle", "ring"), t.size == "big")] += 1
        self.assertEqual(len(kinds), 4)                              # all four cells of the XOR occur


class TestKnownRoom(unittest.TestCase):
    def test_one_spec_every_visit_and_the_window(self) -> None:
        for kind, n in (("visit", 5), ("window", 1)):
            for i in range(n):
                s = RM.room_scene(SEED, "K", kind, i)
                self.assertEqual(s.things, (RM.K_THING,))
                self.assertEqual((s.words, s.referent, s.template), (("red", "star"), 0, "T2"))

    def test_re_rendered_per_visit_under_its_own_item_id(self) -> None:
        a, _ = W.render_scene(RM.room_scene(SEED, "K", "visit", 0))
        a2, _ = W.render_scene(RM.room_scene(SEED, "K", "visit", 0))
        b, _ = W.render_scene(RM.room_scene(SEED, "K", "visit", 1))
        c, _ = W.render_scene(RM.room_scene(SEED, "K", "window", 0))
        self.assertTrue(np.array_equal(a, a2))
        self.assertFalse(np.array_equal(a, b))
        self.assertFalse(np.array_equal(a, c))

    def test_the_star_red_pair_is_held_out_in_s1_the_fact_recorded(self) -> None:
        self.assertIn(("star", "red"), W.HELDOUT)


class TestRoomCache(unittest.TestCase):
    """A small real cache through S1a's road: the eye once per scene, the parent's words beside, the truth apart, no forced
    windows (declared), rooms.py's sha under its own key — a planted foreign sha is REFUSED by RoomPercepts."""

    @classmethod
    def setUpClass(cls) -> None:
        import os
        import tempfile
        from pathlib import Path
        tmp = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))
        tmp.mkdir(parents=True, exist_ok=True)
        cls._td = tempfile.TemporaryDirectory(dir=str(tmp), prefix="scene-rooms-test-")
        cls.root = Path(cls._td.name)
        cls.sh = RM.build_room_cache(cls.root, SEED, "N", "visit", limit=4, recheck_n=2)
        cls.d = RM.room_cache_dir(cls.root, SEED, "N", "visit")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._td.cleanup()

    def test_rows_words_and_truth_align(self) -> None:
        p = RM.RoomPercepts(self.d)
        self.assertEqual(len(p), 4)
        tr = RM.load_room_truth(self.d)
        for i in range(4):
            s = RM.room_scene(SEED, "N", "visit", i)
            self.assertEqual(p.words(i), list(s.words))
            self.assertEqual(tr[i]["item_id"], s.item_id)
            self.assertEqual(len(p.forced(i)), 0)
        self.assertEqual(self.sh["room_code"], RM.rooms_code_sha())
        self.assertFalse(self.sh["forced_windows"])
        self.assertEqual(self.sh["self_check_rows"], sorted(self.sh["self_check_rows"]))

    def test_written_once_and_a_foreign_room_code_is_refused(self) -> None:
        import json
        import shutil
        with self.assertRaises(RM.RoomError):
            RM.build_room_cache(self.root, SEED, "N", "visit", limit=4)
        bad = self.d.with_name("N-visit-planted")
        shutil.copytree(self.d, bad)
        h = json.loads((bad / "scene_header.json").read_text())
        h["room_code"] = "0" * 64
        (bad / "scene_header.json").write_text(json.dumps(h))
        with self.assertRaises(RM.RoomError):
            RM.RoomPercepts(bad)


if __name__ == "__main__":
    unittest.main()
