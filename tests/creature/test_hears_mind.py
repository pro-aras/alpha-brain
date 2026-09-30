# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1 (docs/organism/hears/), test-first (red on dfec420): the brain hears a
# second hand. One fixture tape of the scene world with the MAKER's canvases between its scenes (one white thing on a noisy black
# ground, one word, source `maker`, no scene / world_seed on its rows — the real maker's shape, read from brain-long-2's tape).
"""tests/creature/test_hears_mind.py — `hears scene maker` in the MIND: the derived scene index and world seed, the world on every
non-scene brain row, no new key on a scene row, a brain that hears the scene alone is blind to the maker's rows byte for byte,
the count continues across a resume, the census by world, the self's parent claims observed on scene canvases only."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from typing import Dict, List

import numpy as np

import creature.mind as MM
from brain.scene import world as W
from creature.tape import Tape
from genome import brain as B
from tests.creature import _scene_tape as S
from tests.creature.test_drive_mind import DRIVE_LINE, LEAN, is_turn

ROOT = Path(__file__).resolve().parents[2]
AT = "calibrate at 250 500 1000 2000 5000 10000"
N_TRAIN = 100
MAKER_EVERY = 4
MAKER_WORDS = ("star", "bar", "box")          # one shared with the scene hand, two of the maker's own
CANVAS = 128


def lean_text(hears: str = "scene", drive: str = DRIVE_LINE) -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), LEAN, count=1, flags=re.M)
    assert text.count(AT) == 1
    text = text.replace(AT, "calibrate at 20 40 80")
    text, n = re.subn(r"(^BRAIN    .*?replay none; hears )scene", rf"\1{hears}", text, count=1, flags=re.M)
    assert n == 1, "the lean template's BRAIN line ends in `hears scene`"
    return text + "\n" + (drive + "\n" if drive else "")


def maker_canvas(rng: np.random.Generator, word: str) -> np.ndarray:
    """The maker's shape: a black ground with faint noise, one white thing, a faint stroke or two."""
    img = (rng.random((CANVAS, CANVAS)) < 0.03).astype(np.uint8) * 60
    y, x = int(rng.integers(20, 90)), int(rng.integers(20, 90))
    yy, xx = np.mgrid[0:CANVAS, 0:CANVAS]
    if word == "star":
        m = (np.abs(yy - y) + np.abs(xx - x) <= 12) | ((np.abs(yy - y) <= 3) & (np.abs(xx - x) <= 16)) | ((np.abs(xx - x) <= 3) & (np.abs(yy - y) <= 16))
    elif word == "bar":
        m = (np.abs(yy - y) <= 4) & (np.abs(xx - x) <= 22)
    else:
        m = (np.abs(yy - y) <= 12) & (np.abs(xx - x) <= 12)
    img[m] = 255
    sy, sx = int(rng.integers(0, CANVAS - 20)), int(rng.integers(0, CANVAS - 20))
    for k in range(14):
        img[min(CANVAS - 1, sy + k), min(CANVAS - 1, sx + k // 2)] = 110
    return np.stack([img, img, img], axis=-1)


def build(root: Path, n_train: int = N_TRAIN, every: int = MAKER_EVERY, with_maker: bool = True, ws: int = S.WS) -> Dict[str, object]:
    """Scene training rows as _scene_tape.build writes them (ear rows then the eye row, truth files), a maker canvas after every
    `every` scenes (ear `word`, then the eye row: source maker, no scene / world_seed). No sitting (the grader is not this test's)."""
    tape = Tape(root)
    clock = S._Clock(S.T0)
    rng = np.random.default_rng(20260930)
    maker: List[Dict[str, object]] = []
    for i in range(n_train):
        scene = W.train_scene(ws, i)
        rgb = W.render_scene(scene)[0]
        moment = f"sc{ws}t{i:06d}"
        for w in scene.words:
            tape.publish("ear", w.encode(), {"moment": moment, "source": "scene", "word": w, "scene": i}, "txt", at=clock())
        row = tape.publish("eye", S.png(rgb), {"moment": moment, "source": "scene", "kind": "train", "scene": i, "world_seed": ws},
                           "png", at=clock())
        S._truth(root, int(row["seq"]), {"kind": "train", "scene": i, "world_seed": ws, "scene_dict": scene.to_dict(), "said": list(scene.words)})
        if with_maker and (i + 1) % every == 0:
            k = len(maker)
            word = MAKER_WORDS[k % len(MAKER_WORDS)]
            moment = f"w0000i{k:06d}t{k:09d}"
            tape.publish("ear", word.encode(), {"moment": moment, "source": "maker", "word": word}, "txt", at=clock())
            row = tape.publish("eye", S.png(maker_canvas(rng, word)), {"moment": moment, "source": "maker"}, "png", at=clock())
            maker.append({"moment": moment, "word": word, "seq": int(row["seq"]), "k": k})
    return {"maker": maker, "n_train": n_train}


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="hears-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = build(cls.tape_root)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.on, cls.on_root = cls.live(lean_text("scene maker"))
        cls.off, cls.off_root = cls.live(lean_text("scene"))
        cls.J_on, cls.J_off = S.journal(cls.on_root), S.journal(cls.off_root)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, text: str, rows=None, tape_root: Path = None):
        cls.n += 1
        root = S.link_root(tape_root or cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(text)
        m = MM.Mind(gp, root)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root


def brain_rows(J: List[Dict[str, object]], act: str, world=None) -> List[Dict[str, object]]:
    return [r for r in J if r.get("kind") == "brain" and r.get("act") == act and r.get("world") == world]


class TheSecondHand(_Lives):
    def test_the_fixture_has_the_makers_rows(self) -> None:
        self.assertEqual(len(self.info["maker"]), N_TRAIN // MAKER_EVERY)
        mk = [r for r in self.rows if (r.get("meta") or {}).get("source") == "maker"]
        self.assertEqual(len(mk), 2 * len(self.info["maker"]))
        self.assertTrue(all("scene" not in r["meta"] and "world_seed" not in r["meta"] for r in mk))

    def test_on_the_maker_canvases_are_learned_with_a_derived_index_and_seed(self) -> None:
        learns = brain_rows(self.J_on, "learn", "maker")
        self.assertEqual(len(learns), len(self.info["maker"]))
        self.assertEqual([r["scene"] for r in learns], list(range(len(learns))), "the world's own count, 0-based, in tape order")
        self.assertEqual([r["moment"] for r in learns], [m["moment"] for m in self.info["maker"]])
        self.assertEqual([r["words"] for r in learns], [[m["word"]] for m in self.info["maker"]])
        seed = B.world_seed_of(self.on.genome.seed, "maker")
        self.assertEqual({r["world_seed"] for r in learns}, {seed})
        self.assertNotEqual(seed, B.world_seed_of(self.on.genome.seed, "game"))
        self.assertNotEqual(seed, self.on.genome.seed)
        self.assertEqual(self.on.brain_refused, 0)

    def test_on_a_turn_stands_before_each_maker_learn_and_carries_the_world(self) -> None:
        turns = brain_rows(self.J_on, "turn", "maker")
        self.assertEqual(len(turns), len(self.info["maker"]))
        for t in turns:
            self.assertEqual(t["world"], "maker")
        idx = {id(r): i for i, r in enumerate(self.J_on)}
        for l in brain_rows(self.J_on, "learn", "maker"):
            t = self.J_on[idx[id(l)] - 1]
            self.assertTrue(is_turn(t) and t["world"] == "maker" and t["moment"] == l["moment"], (t, l))

    def test_on_scene_rows_carry_no_new_key(self) -> None:
        n = 0
        for r in self.J_on:
            if r.get("kind") == "brain" and str(r.get("moment", "")).startswith("sc"):
                self.assertNotIn("world", r, r)
                self.assertNotIn("world_seed", r, r)
                n += 1
        self.assertGreater(n, 2 * N_TRAIN - 1, "the presence count: the scene's turn and learn rows")

    def test_off_the_maker_rows_leave_no_brain_row_and_the_journal_is_the_journal_of_a_tape_without_them(self) -> None:
        self.assertEqual(brain_rows(self.J_off, "learn", "maker"), [])
        self.assertEqual(brain_rows(self.J_off, "turn", "maker"), [])
        alone_root = self.tmp / "tape-alone"
        alone_root.mkdir()
        build(alone_root, with_maker=False)
        rows = S.rows(alone_root)
        m_alone, root_alone = self.live(lean_text("scene"), rows=rows, tape_root=alone_root)
        J_alone = S.journal(root_alone)
        # the maker's rows move every later row's seq and its tape clock (+1 ms a row): compare the brain's rows without those two
        of = lambda J: [json.dumps({k: v for k, v in r.items() if k not in ("seq", "at")}, sort_keys=True)
                        for r in J if r.get("kind") == "brain"]
        self.assertEqual(of(self.J_off), of(J_alone), "a brain that hears the scene alone is blind to the maker's rows")
        self.assertEqual(self.off.brain.state_hash(), m_alone.brain.state_hash())

    def test_on_the_calibration_points_count_every_hand(self) -> None:
        cal = [r for r in self.J_on if r.get("kind") == "brain" and r.get("act") == "calibrate"]
        self.assertEqual([r["summary"]["learned"] for r in cal], [20, 40, 80])
        # the 20th canvas LEARNED is earlier in scene terms than the 20th scene (the law's walk, §5.3)
        first = cal[0]
        self.assertLess(int(first["moment"][-6:]) if first["moment"].startswith("sc") else 0, 20)

    def test_the_census_counts_by_world(self) -> None:
        c = self.on.brain.census()
        self.assertEqual(c["scenes_by_world"], {"maker": len(self.info["maker"]), "scene": N_TRAIN})
        star = c["words"]["star"]["meetings_by_world"]
        self.assertEqual(star["maker"], sum(1 for m in self.info["maker"] if m["word"] == "star"))
        self.assertGreater(star.get("scene", 0), 0, "the presence count: the scene hand named a star")
        self.assertEqual(c["words"]["bar"]["meetings_by_world"], {"maker": sum(1 for m in self.info["maker"] if m["word"] == "bar")})
        self.assertEqual(self.off.brain.census()["scenes_by_world"], {"scene": N_TRAIN})
        f = json.loads(sorted((self.on_root / "census").glob("*.json"))[-1].read_text())
        self.assertEqual(f["scenes_by_world"], c["scenes_by_world"])

    def test_the_selfs_parent_claims_are_observed_on_scene_canvases_only(self) -> None:
        on, off = self.on.self_node.claims, self.off.self_node.claims
        events = lambda c: c.confirmed + c.contradicted
        scene_turns = brain_rows(self.J_on, "turn", None)
        maker_turns = brain_rows(self.J_on, "turn", "maker")
        self.assertEqual(len(scene_turns), N_TRAIN)
        self.assertEqual(len(maker_turns), len(self.info["maker"]))
        # the parent's claims: one event per SCENE canvas that can bear it (T2, T3, F1 need an expectation: after the first
        # calibration, which ON reaches earlier in scene terms — the law's §5.3 — so the counts are read against ON's own rows)
        with_exp = [t for t in scene_turns if t.get("expected")]
        self.assertEqual(events(on["T2"]), len(with_exp))
        self.assertEqual(events(on["T3"]), len([t for t in with_exp if t.get("surprise") is not None]))
        self.assertEqual(events(on["F2"]), N_TRAIN)
        self.assertEqual(events(off["F2"]), N_TRAIN)
        self.assertGreater(len(maker_turns), 0)
        # T1 (four places) hears every hand; M1 hears the maker alone, once per maker canvas with an expectation
        self.assertEqual(events(on["T1"]), events(off["T1"]) + len(self.info["maker"]))
        self.assertEqual(events(on["M1"]), len([t for t in maker_turns if t.get("surprise") is not None]))
        self.assertGreater(events(on["M1"]), 0, "the presence count: the maker's canvases after the first calibration")
        self.assertEqual(events(off["M1"]), 0)
        self.assertEqual(on["M1"].text, "Usually, what I expect is what the maker names.")

    def test_a_scene_row_without_its_index_is_still_refused_by_name(self) -> None:
        rows = [dict(r) for r in self.rows]
        for r in rows:
            if r["sense"] == "eye" and r["meta"].get("source") == "scene":
                r["meta"] = {k: v for k, v in r["meta"].items() if k not in ("scene", "world_seed")}
                break
        m, root = self.live(lean_text("scene maker"), rows=rows)
        self.assertEqual(m.brain_refused, 1)
        self.assertEqual(sum(1 for r in S.journal(root) if r.get("kind") == "brain" and r.get("act") == "refused"), 1)


class TheCountContinues(_Lives):
    def test_a_resume_continues_the_makers_count(self) -> None:
        """Lived in two halves (a snapshot between), the maker's indexes are 0, 1, 2, … across both — the count is restored from the
        brain's own state, never from a fresh 0."""
        cut = next(i for i, r in enumerate(self.rows) if (r.get("meta") or {}).get("source") == "maker" and r["sense"] == "eye"
                   and int(r["meta"]["moment"][6:12]) == 9) + 1
        self.n += 1
        root = S.link_root(self.tape_root, self.tmp / f"run{self.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(lean_text("scene maker"))
        m1 = MM.Mind(gp, root)
        for row in self.rows[:cut]:
            m1.consume(row)
        m1.close()
        m2, last = MM.Mind.resume(gp, root)
        self.assertTrue(m2.brain_restored)
        for row in self.rows[cut:]:
            if int(row["seq"]) > last:
                m2.consume(row)
        m2.close()
        J = S.journal(root)
        learns = brain_rows(J, "learn", "maker")
        self.assertEqual([r["scene"] for r in learns], list(range(len(self.info["maker"]))))
        self.assertEqual(m2.brain.census()["scenes_by_world"], self.on.brain.census()["scenes_by_world"])
        self.assertEqual(m2.brain.state_hash(), self.on.brain.state_hash(), "a life in two halves learned what the whole one learned")


if __name__ == "__main__":
    unittest.main()
