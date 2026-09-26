# edit: Claude (Opus 5.5), 2026-09-26 17:36 +0400 — R39: the tape teaches CONST only after the last SLEEP before T_L, so a
# learner of relation cues that learns only in sleep (D, E′) cannot hold a CONST program at T_L. Its failing CONST control
# reads NOT GRADABLE, named; with a sleep on the tape between the teaching and the sitting, the control is graded again.
from __future__ import annotations

import unittest
from pathlib import Path

from brain.harness import graders as G

TAPE = Path("/data/dev/brain-runs/b1/20261001")


def _tape(with_sleep_after_const: bool):
    rows, seq = [], 0

    def add(kind, payload, phase="L"):
        nonlocal seq
        seq += 1
        rows.append({"seq": seq, "kind": kind, "payload": payload, "phase": phase})
        return seq

    add("SLEEP", {"steps": 64})
    for i in range(5):
        a = add("ASK", {"cues": ["CONST"], "operands": [], "answer_kind": "NAME"})
        add("FEEDBACK", {"ask_seq": a, "right": "a"})
    if with_sleep_after_const:
        add("SLEEP", {"steps": 64})
    add("TEST_BEGIN", {"sitting": "T_L"}, "T_L")
    return rows


def _record(arm: str):
    answers = [{"sitting": "T_L", "family": "CONTROL_CONST", "item": f"c:{i}", "correct": False,
                "answer": {"kind": "NOTHING", "value": None}} for i in range(20)]
    return {"answers": answers, "sittings": {}, "summary": {"arm": arm}, "why": [], "rules": [], "missing": []}


class TestConstSleep(unittest.TestCase):
    def test_the_fact_on_a_planted_tape(self) -> None:
        self.assertTrue(G.const_taught_after_last_sleep(_tape(False))["unsleepable"])
        self.assertFalse(G.const_taught_after_last_sleep(_tape(True))["unsleepable"])

    def test_a_sleep_only_learner_reads_not_gradable(self) -> None:
        fact = G.const_taught_after_last_sleep(_tape(False))
        for arm in ("D", "E′", "SHUFFLED-RELATION:D", "SHUFFLED-RELATION:E′"):
            m = G.grade_controls(_record(arm), const_fact=fact)["C0a_CONST"]
            self.assertFalse(m["graded"], arm)
            self.assertEqual(m["reason_code"], "NO_SLEEP_BEFORE_SITTING", arm)

    def test_with_a_sleep_the_control_is_graded_and_fails(self) -> None:
        """Negative control: the same failing answers FAIL when the tape gave the learner a sleep."""
        fact = G.const_taught_after_last_sleep(_tape(True))
        m = G.grade_controls(_record("D"), const_fact=fact)["C0a_CONST"]
        self.assertTrue(m["graded"])
        self.assertFalse(m["pass"])

    def test_an_awake_learner_is_graded_either_way(self) -> None:
        fact = G.const_taught_after_last_sleep(_tape(False))
        for arm in ("A1", "A2", "A3", "F", "A5"):
            m = G.grade_controls(_record(arm), const_fact=fact)["C0a_CONST"]
            self.assertTrue(m["graded"], arm)
            self.assertFalse(m["pass"], arm)

    @unittest.skipUnless((TAPE / "tape.jsonl").exists(), "the graded tape is not on this box")
    def test_the_graded_tape_carries_the_fact(self) -> None:
        from brain.harness.run import load_tape
        rows, _ = load_tape(TAPE)
        fact = G.const_taught_after_last_sleep(rows)
        self.assertTrue(fact["unsleepable"])
        self.assertEqual(fact["last_sleep_before_T_L"], 4540)
        self.assertEqual(fact["T_L_begins"], 4825)
        self.assertEqual(fact["const_teaching_seqs"][0], 4670)


if __name__ == "__main__":
    unittest.main()
