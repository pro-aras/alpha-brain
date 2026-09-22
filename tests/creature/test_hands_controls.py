# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:39 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 5
# (MOTOR-HANDS.md G-MOT-4's own four controls, "each producing a real tape row from a real jail run"): the
# full chain — real jail, creature/senses/hands.py's own _run_one, creature/mind.py's Mind.consume — for
# each of the four controls, checked against G-MOT-4's own refusal test: "positive residual 0; negative
# residual > 0; the crash control's row carries U+FFFD and an exit code with the mind's counters moving;
# the fence control's row reads Permission denied. Refuses the line if any control crashes the mind, or the
# positive control's residual is not 0."
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.senses import hands as hands_sense
from creature.tape import Tape

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"
JAIL_PATH = Path("/data/dev/alpha3/hands/jail_run")

HANDS_LINE_TEMPLATE = "HANDS    jail alpha3/hands/jail_run shelf {shelf} cpu 10 mem 512 wall 20"
ACT_LINE = "ACT      glance open ask run"
TOUCH_LINE = "SENSE    touch from hands: exit rate stalls retries bytes"


def _write_program(shelf: Path, name: str, body: str) -> None:
    (shelf / f"{name}.py").write_text(body)


def _genome_with(shelf_rel: str, *extra: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    lines = [HANDS_LINE_TEMPLATE.format(shelf=shelf_rel), ACT_LINE, TOUCH_LINE, *extra]
    p.write_text(G5_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _run_and_consume(mind: Mind, tape: Tape, jail_path: Path, shelf: Path, program: str, seq_hint: int) -> None:
    root = mind.run_root
    seen_before = {r["sense"]: r for r in []}
    rows_before = _read_rows(root)
    hands_sense._run_one(tape.publish, root, jail_path, shelf, program, cpu=10, mem=512, wall=20, seq_hint=seq_hint)
    rows_after = _read_rows(root)
    for row in rows_after[len(rows_before):]:
        mind.consume(row)


def _read_rows(root: Path):
    out = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return sorted(out, key=lambda r: r["seq"])


def _journal_touch_outcome(root: Path):
    outs, touches, eyes = [], [], []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if "outcome" in r:
                outs.append(r["outcome"])
            if "touch" in r:
                touches.append(r["touch"])
    return outs, touches


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestPositiveControlResidualZero(unittest.TestCase):
    def test_residual_settles_to_zero_by_the_second_run(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(shelf, "positive", '# control: positive\nprint("#"*4)\n')
        gpath = _genome_with(str(shelf))
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)

        for i in range(3):
            _run_and_consume(mind, tape, JAIL_PATH, shelf, "positive", seq_hint=i + 1)

        outs, _ = _journal_touch_outcome(root)
        self.assertEqual(len(outs), 3)
        self.assertIsNone(outs[0]["residual"], "the first-ever run of a program has no expectation yet")
        self.assertEqual(outs[1]["residual"], 0.0, "the CONSTANT program's second run must read residual 0")
        self.assertEqual(outs[2]["residual"], 0.0)


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestNegativeControlResidualPositive(unittest.TestCase):
    def test_residual_stays_above_zero(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(shelf, "negative", '# control: negative\nwith open("INPUT.txt") as f:\n    print(f.read().strip())\n')
        gpath = _genome_with(str(shelf))
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)

        for i in range(4):
            _run_and_consume(mind, tape, JAIL_PATH, shelf, "negative", seq_hint=i + 1)

        outs, _ = _journal_touch_outcome(root)
        self.assertEqual(len(outs), 4)
        self.assertIsNone(outs[0]["residual"])
        for r in outs[1:]:
            self.assertIsNotNone(r["residual"])
            self.assertGreater(r["residual"], 0.0, "a program whose output changes every run must not settle to residual 0")


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestCrashControl(unittest.TestCase):
    def test_row_carries_replacement_char_and_exit_code_mind_keeps_moving(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(
            shelf, "crash",
            "# control: crash\n"
            "import sys\n"
            "sys.stdout.buffer.write(b'program 441\\n')\n"
            "sys.stdout.buffer.write('\\u25f9'.encode('utf-8')[:2])\n"
            "sys.stdout.buffer.flush()\n",
        )
        gpath = _genome_with(str(shelf))
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        moments_before = mind.org.t

        hands_sense._run_one(tape.publish, root, JAIL_PATH, shelf, "crash", cpu=10, mem=512, wall=20, seq_hint=1)
        rows = _read_rows(root)
        for row in rows:
            mind.consume(row)   # must not raise -- the whole point of the control

        eye_row = next(r for r in rows if r["sense"] == "eye")
        self.assertIn("\ufffd", eye_row["meta"]["stdout_text"])
        outcome_row = next(r for r in rows if r["sense"] == "outcome")
        self.assertIn("exit", outcome_row["meta"])
        self.assertEqual(outcome_row["meta"]["exit"], 0)
        # the mind's own counters moved: a real canvas was consumed (org.t advanced -- FAST is declared on
        # G5.genome, so even a sight-only canvas calls Organism.moment_sight)
        self.assertGreater(mind.org.t, moments_before)


@unittest.skipUnless(JAIL_PATH.exists(), "the real jail binary is not present on this box")
class TestFenceControl(unittest.TestCase):
    def test_row_reads_permission_denied_never_an_error_in_the_creature(self) -> None:
        shelf = Path(tempfile.mkdtemp())
        _write_program(shelf, "fence", '# control: fence\nimport socket\nsocket.socket()\n')
        gpath = _genome_with(str(shelf))
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)

        hands_sense._run_one(tape.publish, root, JAIL_PATH, shelf, "fence", cpu=10, mem=512, wall=20, seq_hint=1)
        rows = _read_rows(root)
        for row in rows:
            mind.consume(row)   # must not raise

        eye_row = next(r for r in rows if r["sense"] == "eye")
        self.assertIn("Permission denied", eye_row["meta"]["stderr"])
        self.assertNotEqual(eye_row["meta"]["exit"], 0)


if __name__ == "__main__":
    unittest.main()
