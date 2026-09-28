# edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:26 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §3): the organ's
# own pins — the truth fence (with a planted offender), the tie generator equal to marks.tie_rng, every BRAIN value READ and
# moving behaviour, the pointer, an ask never teaches, the `raw` block per form, M4 on a small life, M5's rule, save / load.
"""tests/genome/test_brain_organ.py — genome/brain.py, the BRAIN organ (rung 1 = S1b-1R's A-RW-R as it scored).

The small life here is a SYNTHETIC toy (two word types: three shapes, two colours; one fixation per thing, things ≥ 5 cells
apart so no two merge); the scored life's identity is the gate's job (tools/brain/gate_alone.py), not this file's."""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from brain.world.seeds import substream

ROOT = Path(__file__).resolve().parents[2]
BRAIN_PY = ROOT / "genome" / "brain.py"

CFG = {"lr": 0.01, "eps": 0.3, "none_level": 0.95, "conformal": 0.90, "young": 3,
       "calibrate_at": [40, 80, 120], "replay": "none", "hears": ["scene"]}

SHAPES = ("sa", "sb", "sc")
COLOURS = ("cg", "cr")
SLOTS = ((2, 2), (2, 9), (9, 5))              # fixation cells: Chebyshev ≥ 7 apart, never merged (MERGE_CELLS = 2)
WS = 777


def _protos():
    r = substream(WS, "toy-protos")
    return ({s: r.normal(size=144) for s in SHAPES}, {c: r.normal(size=144) * 0.8 for c in COLOURS})


def toy_scene(i: int):
    """(glance, words, things, boxes): 1–3 things in the SLOTS, one fixation each; the parent names one of them by
    [colour, shape] / [shape] / [colour]."""
    ps, pc = _protos()
    r = substream(WS, f"toy-scene:{i}")
    n = int(r.integers(1, 4))
    things = [(SHAPES[int(r.integers(3))], COLOURS[int(r.integers(2))]) for _ in range(n)]
    fix, feats = [], []
    for k, (s, c) in enumerate(things):
        fix.append(SLOTS[k])
        v = ps[s] + pc[c] + r.normal(size=144) * 0.3
        feats.append(v / np.linalg.norm(v))
    feats.append(np.ones(144) / 12.0)          # the coarse glance, kept aside by the organ
    t = int(r.integers(n))
    form = int(r.integers(3))
    s, c = things[t]
    words = [c, s] if form == 0 else ([s] if form == 1 else [c])
    boxes = [[y * 8 - 4, x * 8 - 4, 16] for y, x in fix]
    return {"feats": feats, "fix": fix, "windows": [], "residual": [None] * len(feats)}, words, things, boxes


def live(brain, n: int, start: int = 0):
    out = []
    for i in range(start, n):
        g, words, _t, _b = toy_scene(i)
        out.append(brain.learn(g, words, moment=f"sc{WS}t{i:06d}", scene=i, world_seed=WS))
    return out


def asks_for(test_seed: int = 4242, n: int = 12):
    """A fixed sitting: per test scene one point, one what and one say (the canvas = toy scene 10_000 + i), then the whys."""
    rows = []
    for i in range(n):
        g, words, things, boxes = toy_scene(10_000 + i)
        rows.append((g, {"form": "point", "item": f"P:{i}", "mark": "M1", "phrase": words, "box": None, "word": None,
                         "test_seed": test_seed}))
        rows.append((g, {"form": "what", "item": f"W:{i}", "mark": "M2b", "phrase": [], "box": boxes[0], "word": None,
                         "test_seed": test_seed}))
        rows.append((g, {"form": "say", "item": f"S:{i}", "mark": "SPEAK", "phrase": [], "box": boxes[-1], "word": None,
                         "test_seed": test_seed}))
    for w in SHAPES + COLOURS + ("never",):
        rows.append((None, {"form": "why", "item": f"Y:{w}", "mark": "M4", "word": w}))
    return rows


def answers(brain):
    return [json.loads(json.dumps(brain.ask(p, g), sort_keys=True)) for g, p in asks_for()]


class Fence(unittest.TestCase):
    ALLOW = {"__future__", "hashlib", "json", "math", "pathlib", "typing", "numpy", "brain.world.seeds",
             "brain.scene.learners", "brain.scene.health", "brain.scene.eye"}
    FORBIDDEN = ("truth", "fix_thing", "word_type", "word_true_of", "phrase_true_of", "brain.scene.world",
                 "brain.scene.marks", "brain.scene.cache", "brain.scene.run")

    @staticmethod
    def violations(src: str, allow, forbidden):
        tree = ast.parse(src)
        docs = set()
        for node in ast.walk(tree):
            body = getattr(node, "body", None)
            if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                docs.add(id(body[0].value))
        out = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out += [f"import {a.name}" for a in node.names if a.name not in allow]
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level:
                    out.append(f"relative import {mod}")
                    continue
                if mod not in allow:
                    full = [f"{mod}.{a.name}" for a in node.names]
                    out += [f"from-import {m}" for m in full if m not in allow]
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
                out += [f"literal {w!r}" for w in forbidden if w in node.value]
            elif isinstance(node, (ast.Name, ast.Attribute)):
                name = node.id if isinstance(node, ast.Name) else node.attr
                out += [f"name {name}" for w in ("word_type", "word_true_of", "phrase_true_of", "fixation_thing")
                        if name == w]
        return out

    def test_brain_py_imports_only_the_allow_list(self):
        self.assertEqual(self.violations(BRAIN_PY.read_text(encoding="utf-8"), self.ALLOW, self.FORBIDDEN), [])

    def test_planted_offenders_are_caught(self):
        src = BRAIN_PY.read_text(encoding="utf-8")
        for plant in ("from brain.scene import world as W\n", "from brain.scene import marks\n",
                      "import brain.scene.cache\n", "X = 'truth.jsonl'\n", "y = W.word_type('red')\n"):
            with self.subTest(plant=plant):
                self.assertNotEqual(self.violations(src + plant, self.ALLOW, self.FORBIDDEN), [])


class TieRng(unittest.TestCase):
    def test_equal_to_marks_tie_rng(self):
        from brain.scene import marks as M
        from genome import brain as B
        for seed, item in ((20261401, "M1:test:20261401:00000"), (7, "SPEAK:x"), (20261403, "SPEAK2:speak2:20261403:00059")):
            a, b = B.tie_rng(seed, item), M.tie_rng(seed, item)
            self.assertEqual(a.integers(1 << 30, size=8).tolist(), b.integers(1 << 30, size=8).tolist())


class Config(unittest.TestCase):
    def test_every_key_required_and_no_other(self):
        from genome import brain as B
        for k in CFG:
            bad = {kk: v for kk, v in CFG.items() if kk != k}
            with self.subTest(missing=k):
                with self.assertRaises(B.BrainError) as cm:
                    B.Brain(bad)
                self.assertIn(k, str(cm.exception))
        with self.assertRaises(B.BrainError):
            B.Brain({**CFG, "extra": 1})

    def test_replay_other_than_none_refuses_by_name(self):
        from genome import brain as B
        for r in ("uniform", "strong"):
            with self.subTest(replay=r):
                with self.assertRaises(B.BrainError) as cm:
                    B.Brain({**CFG, "replay": r})
                self.assertIn("not built at rung 1", str(cm.exception))
        with self.assertRaises(B.BrainError):
            B.Brain({**CFG, "replay": "surprise"})

    def test_hears(self):
        from genome import brain as B
        self.assertTrue(B.Brain(CFG).hears("scene"))
        self.assertFalse(B.Brain(CFG).hears("maker"))
        self.assertFalse(B.Brain(CFG).hears(None))
        self.assertTrue(B.Brain({**CFG, "hears": ["maker"]}).hears("maker"))
        self.assertFalse(B.Brain({**CFG, "hears": ["maker"]}).hears("scene"))


class ValuesRead(unittest.TestCase):
    """Every BRAIN value moves behaviour when changed (no VALUE-UNREAD)."""

    @classmethod
    def setUpClass(cls):
        from genome import brain as B
        cls.B = B
        cls.base = B.Brain(CFG)
        cls.base_learn = live(cls.base, 120)
        cls.base_ans = answers(cls.base)

    def other(self, **over):
        b = self.B.Brain({**CFG, **over})
        learned = live(b, 120)
        return b, learned

    def test_lr(self):
        b, _ = self.other(lr=0.1)
        self.assertNotEqual(b.state_hash(), self.base.state_hash())
        self.assertNotEqual(float(b.L.lr), float(self.base.L.lr))

    def test_eps(self):
        b, _ = self.other(eps=0.01)
        c0, c1 = self.base.calibrate(), b.calibrate()
        self.assertNotEqual(c0["bands"], c1["bands"])

    def test_none_level(self):
        b, _ = self.other(none_level=0.5)
        self.assertNotEqual(b.L.tau_none, self.base.L.tau_none)

    def test_conformal(self):
        b, _ = self.other(conformal=0.5)
        self.assertNotEqual(b.L.tau_point, self.base.L.tau_point)

    def test_young(self):
        b, _ = self.other(young=40)
        self.assertEqual(b.L.p_from, 40)
        self.assertEqual(self.base.L.p_from, 3)
        self.assertNotEqual(b.L.mature_words(), self.base.L.mature_words())
        self.assertNotEqual(answers(b), self.base_ans)

    def test_young_never_touches_the_class_default(self):
        from brain.scene import learners as Lr
        self.other(young=40)
        self.assertEqual(Lr.RWLearner.p_from, Lr.P_FROM_MEETING)
        self.assertEqual(Lr.RWLearner().p_from, 3)

    def test_calibrate_at(self):
        at = [i + 1 for i, r in enumerate(self.base_learn) if r["calibrated"]]
        self.assertEqual(at, [40, 80, 120])
        b, learned = self.other(calibrate_at=[30, 90])
        self.assertEqual([i + 1 for i, r in enumerate(learned) if r["calibrated"]], [30, 90])

    def test_replay_none_is_the_only_built_rule(self):
        self.assertEqual(self.base.cfg["replay"], "none")


class Pointer(unittest.TestCase):
    """The seat's 20:3x addition: the ask carries the pointed thing's ink `centroid` [cy, cx] px beside `box`; a tie goes to the
    nearest mean position to (cy / 8 − 0.5, cx / 8 − 0.5) — marks.thing_hypothesis's own arithmetic. No centroid → the box's
    centre (declared)."""

    def setUp(self):
        from brain.scene import eye as E
        from genome import brain as B
        self.B, self.E = B, E
        self.fix = [(2, 2), (2, 9), (3, 12), (9, 5)]        # (2, 9) and (3, 12): Chebyshev 3 → separate hypotheses
        self.hyps = E.hypotheses(self.fix, np.eye(144)[:4])

    def ptr(self, box, centroid=None):
        return self.B.pointer_hypothesis(box, centroid, self.fix, self.hyps)

    def test_most_fixations_inside_the_box(self):
        self.assertEqual(self.ptr([12, 12, 16]), 0)         # (2, 2) centre px (20, 20)
        self.assertEqual(self.ptr([68, 36, 16]), 3)

    def test_margin_is_4px_half_open(self):
        # cell (2, 2) centre = (20, 20): a box [top, left, side] holds it iff top-4 <= 20 < top+side+4 (and the same in x)
        self.assertEqual(self.ptr([24, 16, 8]), 0)          # 24 - 4 = 20 <= 20
        self.assertIsNone(self.ptr([25, 16, 8]))            # 21 > 20
        self.assertIsNone(self.ptr([4, 16, 12]))            # 20 < 4 + 12 + 4 = 20 is false

    def test_tie_goes_to_the_nearest_mean_position_to_the_centroid(self):
        # a box over (2, 9) [px (20, 76)] and (3, 12) [px (28, 100)]: one fixation each → the tie
        box = [16, 72, 32]
        self.assertEqual(self.ptr(box, [32.0, 88.0]), 2)    # centroid → cells (3.5, 10.5): (3,12) is 1.58 away, (2,9) 2.12
        self.assertEqual(self.ptr(box, [24.0, 80.0]), 1)    # centroid → cells (2.5, 9.5): (2,9) nearer
        self.assertEqual(self.ptr(box), 2)                  # no centroid: the box's centre px (32, 88)

    def test_matches_marks_thing_hypothesis(self):
        from brain.scene import marks as M
        rng = substream(5, "pointer-pin")
        for _ in range(200):
            fix = [(int(rng.integers(16)), int(rng.integers(16))) for _k in range(int(rng.integers(1, 5)))]
            hyps = self.E.hypotheses(fix, np.eye(144)[:len(fix)])
            top, left, side = int(rng.integers(0, 100)), int(rng.integers(0, 100)), int(rng.integers(8, 40))
            cent = [top + side * float(rng.random()), left + side * float(rng.random())]
            ft = [0 if (top - 4 <= y * 8 + 4 < top + side + 4 and left - 4 <= x * 8 + 4 < left + side + 4) else None
                  for y, x in fix]
            want = M.thing_hypothesis(0, [h.members for h in hyps], [h.pos for h in hyps], ft, tuple(cent))
            self.assertEqual(self.B.pointer_hypothesis([top, left, side], cent, fix, hyps), want)

    def test_no_fixation_inside(self):
        self.assertIsNone(self.ptr([200, 200, 16]))


class Life(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from genome import brain as B
        cls.B = B
        cls.brain = B.Brain(CFG)
        cls.learned = live(cls.brain, 120)

    def test_learn_return(self):
        r = self.learned[50]
        self.assertEqual(set(r), {"n_hyp", "words", "attributed", "none", "calibrated", "fix", "hyps"})
        g, _w, _t, _b = toy_scene(50)
        self.assertEqual(r["fix"], [list(c) for c in g["fix"]])                 # PREREG §3 row M6: the learn row's cells
        self.assertEqual(r["hyps"], [[k] for k in range(len(g["fix"]))])         # one fixation per thing, never merged
        self.assertIsNone(self.learned[10]["none"])                     # no «none» before the first calibration
        self.assertIn(self.learned[60]["none"], (True, False, None))
        self.assertTrue(any(r["none"] is not None for r in self.learned[40:]))

    def test_an_ask_never_teaches(self):
        h0 = self.brain.state_hash()
        a0 = answers(self.brain)
        self.assertEqual(self.brain.state_hash(), h0)
        self.assertEqual(answers(self.brain), a0)

    def test_raw_per_form(self):
        seen = {}
        for g, p in asks_for():
            a = json.loads(json.dumps(self.brain.ask(p, g)))
            self.assertIn("raw", a)
            self.assertIn("kind", a)
            seen.setdefault(p["form"], set()).add(a["kind"])
            if p["form"] == "point" and a["kind"] in ("thing", "none"):
                self.assertTrue({"point", "best", "scores", "none", "none_fit", "none_i", "none_ii", "none_ii_fit"} <= set(a["raw"]))
            if p["form"] == "what" and a["kind"] != "unseen":
                self.assertEqual(set(a["raw"]), {"emit"})
            if p["form"] == "say" and a["kind"] != "unseen":
                self.assertTrue({"believed", "n_accepted", "n_candidates", "n_unique", "reason", "sayable", "spoken",
                                 "target"} <= set(a["raw"]))
        self.assertTrue(seen["point"] & {"thing", "none"})
        self.assertTrue(seen["what"] & {"words", "unknown"})
        self.assertTrue(seen["say"] & {"phrase", "declined"})

    def test_point_names_its_hypothesis(self):
        g, words, things, boxes = toy_scene(10_003)
        a = self.brain.ask({"form": "point", "item": "P:x", "mark": "M1", "phrase": words, "box": None, "word": None,
                            "test_seed": 1}, g)
        if a["kind"] == "thing":
            h = a["hyp"]
            self.assertEqual(a["fix"], [list(g["fix"][h])])
            self.assertEqual(a["pos"], [float(g["fix"][h][0]), float(g["fix"][h][1])])

    def test_misuse(self):
        g, _w, _t, _b = toy_scene(10_001)
        types = [tuple(t) for t in self.brain.summary()["types"]]
        self.assertIn(("sa", "sb", "sc"), types)
        self.assertIn(("cg", "cr"), types)
        a = self.brain.ask({"form": "point", "item": "P:m", "mark": "M5", "phrase": ["cr", "sb", "sa"], "box": None,
                            "word": None, "test_seed": 1}, g)
        self.assertEqual(a["kind"], "misuse")
        self.assertEqual(a["words"], ["sb", "sa"])                  # the first same-type pair in the phrase's order
        self.assertEqual(a["raw"], {"point": None, "misuse": ["sb", "sa"]})
        self.assertIn("point", a["raw_forced"])
        b = self.brain.ask({"form": "point", "item": "P:m", "mark": "M1", "phrase": ["cr", "sb"], "box": None,
                            "word": None, "test_seed": 1}, g)
        self.assertNotEqual(b["kind"], "misuse")

    def test_unheard(self):
        g, _w, _t, _b = toy_scene(10_001)
        a = self.brain.ask({"form": "point", "item": "P:u", "mark": "M1", "phrase": ["zog", "sa"], "box": None,
                            "word": None, "test_seed": 1}, g)
        self.assertEqual(a["kind"], "unheard")
        self.assertEqual(a["words"], ["zog"])

    def test_unseen_pointer(self):
        g, _w, _t, _b = toy_scene(10_001)
        a = self.brain.ask({"form": "what", "item": "W:u", "mark": "NAME", "phrase": [], "box": [300, 300, 16],
                            "word": None, "test_seed": 1}, g)
        self.assertEqual(a["kind"], "unseen")
        self.assertEqual(a["raw"], {"emit": None, "uncovered": True, "name": None})
        s = self.brain.ask({"form": "say", "item": "S:u", "mark": "SPEAK", "phrase": [], "box": [300, 300, 16],
                            "word": None, "test_seed": 1}, g)
        self.assertEqual(s["kind"], "unseen")
        self.assertEqual(s["raw"], {"spoken": None, "reason": "uncovered", "uncovered": True})

    def test_begin_calibrates_only_after_new_scenes(self):
        from genome import brain as B
        b = B.Brain({**CFG, "calibrate_at": [30]})
        live(b, 35)
        a = b.ask({"form": "begin", "set": "fresh", "test_seed": 1}, None)
        self.assertEqual(a["kind"], "begin")
        self.assertTrue(a["calibrated"])
        self.assertFalse(b.ask({"form": "begin", "set": "fresh", "test_seed": 1}, None)["calibrated"])
        self.assertEqual(b.ask({"form": "end"}, None)["kind"], "end")


class Explain(unittest.TestCase):
    """M4 on a small life: every cited episode exists and heard the word; citations are deterministic; a never-heard word
    and a young word return «unknown»."""

    @classmethod
    def setUpClass(cls):
        from genome import brain as B
        cls.brain = B.Brain(CFG)
        live(cls.brain, 120)
        cls.heard = {}
        for i in range(120):
            _g, words, _t, _b = toy_scene(i)
            cls.heard[f"sc{WS}t{i:06d}"] = (i, words)

    def why(self, w):
        return self.brain.ask({"form": "why", "item": f"Y:{w}", "mark": "M4", "word": w}, None)

    def test_cited_episodes_heard_the_word(self):
        for w in SHAPES + COLOURS:
            with self.subTest(word=w):
                a = self.why(w)
                self.assertEqual(a["kind"], "because")
                self.assertTrue(1 <= len(a["episodes"]) <= 8)
                for e in a["episodes"]:
                    scene, words = self.heard[e["moment"]]
                    self.assertEqual(e["scene"], scene)
                    self.assertIn(w, words)
                    g, _w, _t, _b = toy_scene(scene)
                    self.assertEqual(e["fix"], [list(c) for c in g["fix"]])
                    self.assertGreaterEqual(len(e["hyps"]), 2)                   # PREREG §3 row M4a: ≥ 2 hypotheses in view
                    self.assertEqual(e["pos"], [float(v) for v in g["fix"][e["hyps"][e["hyp"]][0]]])
                self.assertEqual(a["rule"]["over"], [e["moment"] for e in a["episodes"]])
                self.assertEqual(a, self.why(w))                          # deterministic

    def test_the_rule_strongest_first_among_two_or_more_hypotheses(self):
        from genome import brain as B
        b = self.brain
        for w in SHAPES + COLOURS:
            pool = [e for e in b.episodes[w] if len(b.canvas[int(e[0])][1]) >= 2]
            want = [b.moments[int(e[0])] for e in sorted(pool, key=lambda e: (-e[4], e[0]))[:B.WHY_MAX]]
            self.assertEqual(self.why(w)["rule"]["over"], want)
            self.assertTrue(any(len(b.canvas[int(e[0])][1]) == 1 for e in b.episodes[w]))   # 1-hypothesis episodes exist …
            self.assertTrue(all(e["moment"] in want for e in self.why(w)["episodes"]))        # … and are never cited

    def test_only_one_hypothesis_episodes_is_unknown(self):
        from genome import brain as B
        b = B.Brain(CFG)
        k = 0
        for i in range(400):
            g, words, things, _b = toy_scene(i)
            if len(things) == 1:
                b.learn(g, words, moment=f"m{i}", scene=i, world_seed=WS)
                k += 1
        self.assertGreater(k, 40)
        for w in SHAPES + COLOURS:
            self.assertEqual(b.ask({"form": "why", "item": "Y", "mark": "M4", "word": w}, None)["kind"], "unknown")

    def test_never_heard_and_young_are_unknown(self):
        self.assertEqual(self.why("never")["kind"], "unknown")
        from genome import brain as B
        b = B.Brain({**CFG, "young": 1000})
        live(b, 50)
        self.assertEqual(b.ask({"form": "why", "item": "Y", "mark": "M4", "word": "sa"}, None)["kind"], "unknown")


class SaveLoad(unittest.TestCase):
    def test_round_trip_hash_and_resume_identity(self):
        from genome import brain as B
        straight = B.Brain(CFG)
        live(straight, 120)
        with tempfile.TemporaryDirectory(dir=None) as d:
            for n in (0, 35, 40, 77):
                with self.subTest(n=n):
                    a = B.Brain(CFG)
                    live(a, n)
                    base = Path(d) / f"brain-{n}"
                    a.save(base)
                    self.assertTrue(base.with_suffix(".npz").exists() and base.with_suffix(".json").exists())
                    b = B.Brain.load(base, CFG)
                    self.assertEqual(b.state_hash(), a.state_hash())
                    live(b, 120, start=n)
                    self.assertEqual(b.state_hash(), straight.state_hash())
                    self.assertEqual(answers(b), answers(straight))

    def test_load_refuses_another_cfg(self):
        from genome import brain as B
        a = B.Brain(CFG)
        live(a, 10)
        with tempfile.TemporaryDirectory() as d:
            a.save(Path(d) / "b")
            with self.assertRaises(B.BrainError):
                B.Brain.load(Path(d) / "b", {**CFG, "lr": 0.1})

    def test_hash_moves_with_one_scene(self):
        from genome import brain as B
        a = B.Brain(CFG)
        live(a, 30)
        h = a.state_hash()
        live(a, 31, start=30)
        self.assertNotEqual(a.state_hash(), h)


if __name__ == "__main__":
    unittest.main()
