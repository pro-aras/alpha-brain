# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B1 (the law SIGNED; SEAT-LINE
# sha256 1d00a35f…; test-first): genome/brain.py's two `produce_believed` call sites (the turn's say, the ask's say)
# select learners.produce_incremental (brain/scene/learners.py:1358, the verdicted mechanism) when AND ONLY WHEN the
# brain is constructed under the MOUTH clause «incremental». Undeclared: produce_believed, byte-identical everywhere.
"""tests/genome/test_brain_mouth_incremental.py — THE MOUTH CLAUSE AT THE ORGAN (PREREG-ALPHA-6 §1.3).

The small life is tests/genome/test_brain_organ.py's synthetic toy (the same fixture test_brain_turn.py grows).
The flag is a CONSTRUCTION parameter (the mind reads declared["MOUTH"]["incremental"] and hands it over; the
default is the old mouth — the organism's every undeclared path byte-identical), never a BRAIN gene value: the
saved cfg and the state hash never carry it."""
from __future__ import annotations

import unittest

from brain.scene import learners as Lr
from brain.world.seeds import substream
from genome import brain as B
from genome.brain import tie_rng
from tests.genome import test_brain_organ as T

CFG = dict(T.CFG)
WS = T.WS
LIVED = 120                       # three calibrations (40, 80, 120), as test_brain_turn.py
FRESH = 10_000


def grown(**kw) -> "B.Brain":
    b = B.Brain(CFG, **kw)
    T.live(b, LIVED)
    return b


def turns_of(b: "B.Brain", n: int = 120):
    out = []
    for i in range(FRESH, FRESH + n):
        g, _w, _t, _b = T.toy_scene(i)
        out.append((b.turn(g, scene=i, world_seed=WS), g))
    return out


class TheDefaultIsTheOldMouth(unittest.TestCase):
    """Undeclared (the flag absent, or False): the two call sites are produce_believed's, byte-identical."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.b = grown()
        cls.turns = turns_of(cls.b)

    def test_the_turns_say_is_produce_believeds_row(self) -> None:
        n = 0
        for t, g in self.turns:
            if t["say"] is None:
                continue
            h = t["say"]["hyp"]
            _hy, X = B.things_in_view(g)
            a = Lr.produce_believed(self.b.road(), X, h, lambda: substream(WS, f"turn-say:{t['scene']}:{h}"))
            self.assertEqual(a["spoken"], t["say"]["words"])
            self.assertEqual(int(a["readback_point"]), t["say"]["readback"])
            n += 1
        self.assertGreater(n, 40, "the presence count")

    def test_the_asks_say_is_produce_believeds_row(self) -> None:
        n = 0
        for g, p in T.asks_for():
            if p["form"] != "say":
                continue
            out = self.b.ask(p, g)
            if out["kind"] != "phrase":
                continue
            h = int(out["hyp"])
            _hy, X = B.things_in_view(g)
            a = Lr.produce_believed(self.b.road(), X, h, lambda: tie_rng(int(p["test_seed"]), str(p["item"])))
            self.assertEqual(a["spoken"], out["words"])
            self.assertNotIn("n_readbacks", out["raw"], "the old enumeration's row carries no incremental key")
            n += 1
        self.assertGreater(n, 2, "the presence count")

    def test_the_flag_false_is_the_default(self) -> None:
        a, b = grown(), grown(mouth_incremental=False)
        for i in range(FRESH, FRESH + 30):
            g = T.toy_scene(i)[0]
            self.assertEqual(a.turn(g, scene=i, world_seed=WS), b.turn(g, scene=i, world_seed=WS))


class TheClauseSelectsTheIncrementalMouth(unittest.TestCase):
    """Declared: the SAME two call sites run learners.produce_incremental — the mechanism's own row."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.b = grown(mouth_incremental=True)
        cls.turns = turns_of(cls.b)

    def test_the_turns_say_is_produce_incrementals_row(self) -> None:
        n = 0
        for t, g in self.turns:
            if t["say"] is None:
                continue
            h = t["say"]["hyp"]
            _hy, X = B.things_in_view(g)
            a = Lr.produce_incremental(self.b.road(), X, h, lambda: substream(WS, f"turn-say:{t['scene']}:{h}"))
            self.assertEqual(a["spoken"], t["say"]["words"])
            self.assertEqual(int(a["readback_point"]), t["say"]["readback"])
            m = a.get("margin")
            import math
            self.assertEqual(None if (m is None or not math.isfinite(float(m))) else float(m), t["say"]["margin"])
            n += 1
        self.assertGreater(n, 20, "the presence count: the incremental mouth speaks on the toy stream")

    def test_the_asks_say_carries_the_mechanisms_own_keys(self) -> None:
        n = 0
        for g, p in T.asks_for():
            if p["form"] != "say":
                continue
            out = self.b.ask(p, g)
            if out["kind"] not in ("phrase", "declined"):
                continue
            raw = out["raw"]
            self.assertIn("n_readbacks", raw)
            self.assertIn("n_say", raw)
            self.assertIn("skipped", raw)
            self.assertIn("added", raw)
            self.assertLessEqual(int(raw["n_readbacks"]), len(raw["sayable"]),
                                 "the mechanism's own bound: read-backs never past the sayable list")
            if out["kind"] == "phrase":
                _hy, X = B.things_in_view(g)
                a = Lr.produce_incremental(self.b.road(), X, int(out["hyp"]),
                                           lambda: tie_rng(int(p["test_seed"]), str(p["item"])))
                self.assertEqual(a["spoken"], out["words"])
                n += 1
        self.assertGreater(n, 3, "the presence count")

    def test_the_turn_never_learns_under_either_mouth(self) -> None:
        a, b = grown(), grown(mouth_incremental=True)
        h0a, h0b = a.state_hash(), b.state_hash()
        self.assertEqual(h0a, h0b, "the two mouths learn the same brain (the turn is read-only)")
        for i in range(FRESH, FRESH + 40):
            g = T.toy_scene(i)[0]
            a.turn(g, scene=i, world_seed=WS)
            b.turn(g, scene=i, world_seed=WS)
        self.assertEqual((a.state_hash(), b.state_hash()), (h0a, h0b))

    def test_a_resume_keeps_the_clause_the_genome_declares(self) -> None:
        # the flag is a construction parameter: load() takes it exactly as __init__ does (the mind re-declares
        # at every construction — a resume never changes the genome).
        import tempfile
        from pathlib import Path
        b = grown(mouth_incremental=True)
        tmp = Path(tempfile.mkdtemp(prefix="brain-mouth-inc-"))
        b.save(tmp / "brain")
        r = B.Brain.load(tmp / "brain", CFG, mouth_incremental=True)
        g = T.toy_scene(FRESH)[0]
        self.assertEqual(r.turn(g, scene=FRESH, world_seed=WS), b.turn(g, scene=FRESH, world_seed=WS))


if __name__ == "__main__":
    unittest.main()
