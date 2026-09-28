# edit: Claude (Fable 5.1), 2026-09-24 18:44 +0400 — the routers' LOGIC with fake parts (fast, no cache): naming cues go to the
# cells unless they abstain (then the network, A5/F), relation cues to the network / partner / library, F to the
# library only when D fits ALL of the cue's examples; every routed answer names its part; state_sha is the parts'
# conjunction; snapshot/load round-trips per part; why() is the cells', rule() the library's. The R9 seam with the
# REAL D (a swapped snapshot must change F's answers after that sleep) is a targeted seat check on a smoke run —
# see the register — because it needs D's own sleep snapshots on disk.
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from brain.hybrids import router as RT
from brain.protocol import Answer, AnswerKind, make_row, op_name, op_row


class _Fake:
    """A part with a scripted answer per cue family and a counter as its 'state'."""
    kinds: Dict[str, Any] = {}

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.n = 0
        self.fits = bool(self.config.get("fits", False))
        self.seen: List[int] = []

    def fit_event(self, row, valence=None):
        self.n += 1
        self.seen.append(row["seq"])

    def sleep(self, steps):
        self.n += 100

    def answer(self, ask_row, learn=False):
        cue = ask_row["payload"]["cues"][0]
        k, v = self.kinds.get(cue, (AnswerKind.NOTHING, None))
        return Answer(kind=k, value=v, raw={"part": type(self).__name__})

    def state_sha(self):
        return hashlib.sha256(f"{type(self).__name__}:{self.n}".encode()).hexdigest()

    def snapshot(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(str(self.n))

    def load(self, path):
        self.n = int(Path(path).read_text())

    def cost(self):
        return {"events": self.n, "ms": 1.0 * self.n}


class Cells(_Fake):
    kinds = {"NAME": (AnswerKind.UNKNOWN, None), "IS": (AnswerKind.YES, None), "POINT": (AnswerKind.PICK, 0)}

    def why(self, ask_row):
        return [1, 2, 3]


class Net(_Fake):
    kinds = {"NAME": (AnswerKind.NAME, "net-name"), "AFTER": (AnswerKind.NAME, "net-after"), "IS": (AnswerKind.NO, None)}


class Lib(_Fake):
    kinds = {"AFTER": (AnswerKind.NAME, "lib-after")}

    def fits_all(self, ask_row):
        return self.fits

    def rule(self, cue):
        return {"text": "lib rule", "executable": lambda row: Answer(kind=AnswerKind.NAME, value="lib-after")}


class Partner(_Fake):
    kinds = {"AFTER": (AnswerKind.NAME, "partner-after")}


def _ask(seq: int, cues: List[str], answer_kind: str = "NAME", name_op: Optional[str] = None):
    ops = [op_name(name_op)] if name_op else [op_row(0)]
    cands = [0, 1, 2, 3] if answer_kind == "PICK" else None
    return make_row(seq, "ASK", "T_L", "x", {"cues": cues, "operands": ops, "candidate_rows": cands, "answer_kind": answer_kind})


class TestRouter(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = dict(RT.PART_CLASSES)
        RT.PART_CLASSES.update({"A0": (__name__, "Cells"), "A1": (__name__, "Net"), "D": (__name__, "Lib"), "A2": (__name__, "Partner"), "A3": (__name__, "Partner")})
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = {"cache_dir": None, "run_dir": self.tmp.name, "seed": 1, "interpreter": "x"}

    def tearDown(self) -> None:
        RT.PART_CLASSES.clear(); RT.PART_CLASSES.update(self._saved)
        self.tmp.cleanup()

    def test_a5_routes_naming_to_cells_with_fallback_and_relations_to_net(self) -> None:
        r = RT.ArmA5(1, self.cfg)
        a = r.answer(_ask(1, ["NAME"]))                    # cells abstain → the net answers, flagged as a fallback
        self.assertEqual((a.kind, a.value, a.raw["routed_to"], a.raw["fallback"]), ("NAME", "net-name", "net", True))
        b = r.answer(_ask(2, ["IS"], "YESNO", name_op="a"))  # cells answer → theirs, no fallback
        self.assertEqual((b.kind, b.raw["routed_to"], b.raw["fallback"]), ("YES", "cells", False))
        c = r.answer(_ask(3, ["AFTER"]))
        self.assertEqual((c.kind, c.value, c.raw["routed_to"]), ("NAME", "net-after", "net"))
        self.assertEqual(r.why(_ask(1, ["NAME"])), [1, 2, 3])
        self.assertTrue(r.rule(["AFTER"]).get("no_road"))

    def test_e_prime_and_a6(self) -> None:
        e = RT.ArmEPrime(1, self.cfg)
        a = e.answer(_ask(1, ["NAME"]))
        self.assertEqual((a.kind, a.raw["routed_to"]), ("UNKNOWN", "cells"))    # E′: no network to fall back to
        self.assertEqual(e.answer(_ask(2, ["AFTER"])).value, "lib-after")
        self.assertEqual(e.rule(["AFTER"])["text"], "lib rule")
        a6 = RT.ArmA6(1, dict(self.cfg, partner="A2"))
        self.assertEqual(a6.answer(_ask(3, ["AFTER"])).value, "partner-after")
        with self.assertRaises(RT.RouterError):
            RT.ArmA6(1, dict(self.cfg, partner="D"))

    def test_f_routes_relations_by_fits_all(self) -> None:
        f = RT.ArmF(1, dict(self.cfg, part_config={"lib": {"fits": True}}))
        self.assertEqual(f.answer(_ask(1, ["AFTER"])).raw["routed_to"], "lib")
        f2 = RT.ArmF(1, dict(self.cfg, part_config={"lib": {"fits": False}}))
        self.assertEqual(f2.answer(_ask(1, ["AFTER"])).raw["routed_to"], "net")
        self.assertEqual(f2.answer(_ask(2, ["AFTER", "OTHER_CASE"], "PICK")).raw["routed_to"], "net")

    def test_fit_sleep_state_snapshot_cost_are_the_parts_conjunction(self) -> None:
        f = RT.ArmF(1, self.cfg)
        row = make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"})
        s0 = f.state_sha()
        f.fit_event(row); f.sleep(64)
        self.assertNotEqual(s0, f.state_sha())
        for p in f.parts.values():
            self.assertEqual(p.seen, [1]); self.assertEqual(p.n, 101)
        self.assertEqual(f.cost(), {"events": 303, "ms": 303.0})
        snap = Path(self.tmp.name) / "snap"
        f.snapshot(snap)
        g = RT.ArmF(1, self.cfg)
        g.load(snap)
        self.assertEqual(g.state_sha(), f.state_sha())
        # a planted change in ONE part's snapshot moves the whole's digest (the parts are the state)
        (snap / "lib" / "state").write_text("5")
        h = RT.ArmF(1, self.cfg); h.load(snap)
        self.assertNotEqual(h.state_sha(), f.state_sha())


if __name__ == "__main__":
    unittest.main()
