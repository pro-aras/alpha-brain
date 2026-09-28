# edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:57 +0400 — arm D against the FROZEN protocol (brain/protocol.py, ac7d2ff):
# check_arm's battery on D, its planted control (a D that mutates under learn=False must be CAUGHT), and the
# HarnessContract road end to end (TEACH -> training ASK -> FEEDBACK -> SLEEP -> frozen TEST ask -> why/rule).
# Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/tmp nice -n 19 \
#      /data/dev/venvs/brain/bin/python -m unittest discover -s tests/brain/arms_library -t . -v
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Mapping

from brain.protocol import (Answer, AnswerKind, HarnessContract, ProtocolError, check_arm, has_rule, has_why,
                            make_arm, make_row, op_name, op_row)
from brain.arms.library import LibraryArm

from .synth import SynthWorld

LETTERS = "abcdefgh"


def build_world(tmp: Path):
    w = SynthWorld(seed=3)
    teach = [(nm, w.render(nm)) for _r in range(3) for nm in LETTERS]
    asks = [(nm, w.render(nm)) for _r in range(2) for nm in LETTERS]
    after = [(LETTERS[i], LETTERS[i + 1], w.render(LETTERS[i])) for i in range(0, len(LETTERS) - 1, 2) for _ in range(2)]
    probe = [(LETTERS[i], LETTERS[i + 1], w.render(LETTERS[i])) for i in range(1, len(LETTERS) - 1, 2)]
    w.write(tmp / "cache")
    return teach, asks, after, probe


def cfg(tmp: Path, **extra) -> Dict[str, Any]:
    c = {"cache_dir": str(tmp / "cache"), "run_dir": str(tmp / "run"), "seed": 20261001, "interpreter": "venv",
         "candidates_per_sleep": 3000, "max_size": 14}
    c.update(extra)
    return c


def ask_row(seq, cues, operands, kind, cands=None):
    return make_row(seq, "ASK", "L4", "x", {"cues": cues, "operands": operands, "candidate_rows": cands,
                                             "answer_kind": kind})


def drive(arm, teach, asks, after, seq0=1):
    seq = seq0
    for nm, r in teach:
        HarnessContract.teach(arm, make_row(seq, "TEACH", "L1", nm, {"glance_row": r, "name": nm}))
        seq += 1
    for nm, r in asks:
        a = ask_row(seq, ["NAME"], [op_row(r)], "NAME")
        ans = HarnessContract.training_ask(arm, a)
        HarnessContract.feedback(arm, make_row(seq + 1, "FEEDBACK", "L4", nm, {"ask_seq": seq, "right": nm}), ans, "NAME")
        seq += 2
    for x, y, r in after:
        a = ask_row(seq, ["AFTER"], [op_row(r)], "NAME")
        ans = HarnessContract.training_ask(arm, a)
        HarnessContract.feedback(arm, make_row(seq + 1, "FEEDBACK", "L4", x, {"ask_seq": seq, "right": y}), ans, "NAME")
        seq += 2
    return seq


class TestConformance(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=None)
        self.tmp = Path(self._tmp.name)
        self.teach, self.asks, self.after, self.probe = build_world(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_check_arm_passes_on_D(self):
        c = cfg(self.tmp)
        arm = make_arm(LibraryArm, 20261001, c)
        seq = drive(arm, self.teach, self.asks, self.after)
        HarnessContract.sleep(arm, make_row(seq, "SLEEP", "L4", "-", {"steps": 0}))
        HarnessContract.sleep(arm, make_row(seq + 1, "SLEEP", "L4", "-", {"steps": 0}))
        violations = check_arm(
            arm,
            sample_teach_row=make_row(seq + 2, "TEACH", "L1", "a", {"glance_row": self.teach[0][1], "name": "a"}),
            sample_ask_row=ask_row(seq + 3, ["NAME"], [op_row(self.asks[0][1])], "NAME"),
            tmp_dir=self.tmp / "check",
            fresh_arm_factory=lambda: make_arm(LibraryArm, 20261001, c))
        self.assertEqual(violations, [], violations)
        self.assertTrue(has_why(arm) and has_rule(arm))

    def test_check_arm_catches_a_mutating_D(self):
        """#228: the checker's negative control, on D's own state — a D that records under learn=False."""
        c = cfg(self.tmp)

        class LeakyD(LibraryArm):
            def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
                self.core.intern("__leak__%d" % len(self.core.names))
                return super().answer(ask_row, learn=learn)

        arm = make_arm(LeakyD, 1, c)
        drive(arm, self.teach[:4], [], [])
        violations = check_arm(arm, sample_teach_row=make_row(99, "TEACH", "L1", "b", {"glance_row": 1, "name": "b"}),
                               sample_ask_row=ask_row(100, ["NAME"], [op_row(0)], "NAME"),
                               tmp_dir=self.tmp / "check2", fresh_arm_factory=lambda: make_arm(LeakyD, 1, c))
        self.assertTrue(any("state_sha" in v for v in violations), violations)

    def test_the_road_end_to_end(self):
        c = cfg(self.tmp)
        arm = make_arm(LibraryArm, 20261001, c)
        seq = drive(arm, self.teach, self.asks, self.after)
        for _ in range(2):
            HarnessContract.sleep(arm, make_row(seq, "SLEEP", "L4", "-", {"steps": 0}))
            seq += 1
        right = 0
        for x, y, r in self.probe:
            a = make_row(seq, "ASK", "T_L", "probe", {"cues": ["AFTER"], "operands": [op_row(r)],
                                                       "candidate_rows": None, "answer_kind": "NAME"})
            seq += 1
            ans = HarnessContract.test_ask(arm, a)          # raises if state_sha moved (0e)
            right += int(ans.kind == AnswerKind.NAME and ans.value == y)
            cited = arm.why(a)
            self.assertTrue(cited, "an answered relation cites the examples its program was fitted on")
            r_ = arm.rule(["AFTER"])
            self.assertIn("AFTER(G)>NAME :=", r_["text"])
            self.assertEqual(r_["executable"](a).to_dict(), ans.to_dict(), "the rule is what D did (U4b)")
        self.assertEqual(right, len(self.probe), "the synthetic world's held-out AFTER pairs")
        # a never-fitted cue reads NOTHING, and so does a compound whose part is missing
        a = ask_row(seq, ["MIRROR"], [op_row(self.teach[0][1])], "YESNO")
        self.assertEqual(arm.answer(a).kind, AnswerKind.NOTHING)
        # a row whose sha does not verify is refused
        bad = make_row(seq + 1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"})
        bad["payload"]["name"] = "b"
        with self.assertRaises(ProtocolError):
            arm.fit_event(bad)

    def test_valence_is_ignored(self):
        """D reads the SHOWN right answer, never its own valence: two arms fed the same rows with opposite
        valences end in the same state."""
        c1, c2 = cfg(self.tmp), cfg(self.tmp)
        a1, a2 = make_arm(LibraryArm, 1, c1), make_arm(LibraryArm, 1, c2)
        for arm, flip in ((a1, False), (a2, True)):
            seq = 1
            for nm, r in self.teach:
                arm.fit_event(make_row(seq, "TEACH", "L1", nm, {"glance_row": r, "name": nm})); seq += 1
            for nm, r in self.asks:
                arm.fit_event(ask_row(seq, ["NAME"], [op_row(r)], "NAME"))
                arm.fit_event(make_row(seq + 1, "FEEDBACK", "L4", nm, {"ask_seq": seq, "right": nm}),
                              valence="no" if flip else "reward")
                seq += 2
            arm.sleep(0)
        self.assertEqual(a1.state_sha(), a2.state_sha())


if __name__ == "__main__":
    unittest.main()
