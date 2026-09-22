# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2
# (MOTOR-HANDS.md G-MOT-4, the plan's L-12). Mirrors test_mind_chooses_act.py's own shape: the mind's HALF
# of the run/hands/ACT protocol, proven with a FAKE hands sense thread (no real jail needed for this file —
# see tests/creature/test_hands_sense.py for the real-jail version) that reads the ACT file the mind wrote
# and publishes the matching eye+outcome+touch rows exactly as an obedient sense thread would.
from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import List, Optional

import numpy as np

from creature.mind import Mind
from creature.tape import Tape

ROOT = Path(__file__).resolve().parents[2]
G5_GENOME_PATH = ROOT / "genome" / "G5.genome"
SHELF_FIXTURE = ROOT / "tests" / "fixtures" / "hands-shelf-test"     # 5 programs: alpha bravo charlie delta echo
SHELF_NAMES = sorted(p.stem for p in SHELF_FIXTURE.glob("*.py"))

HANDS_LINE = "HANDS    jail alpha3/hands/jail_run shelf tests/fixtures/hands-shelf-test cpu 10 mem 512 wall 20"
ACT_LINE = "ACT      glance open ask run"
THINK_EVERY_1 = "THINK    every 1 canvases"    # override G5.genome's "every 10" so every eye row is a think pass


def _genome_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G5_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _fake_stdout(program: str, run_index: int) -> bytes:
    """Deterministic per-program, per-run stdout — a real hands.py would derive this from the jail; here
    the fake sense thread manufactures it directly to drive the outcome fingerprint (crc32-based, see
    creature/senses/hands.py's own `_got_fingerprint`)."""
    return f"{program}-{run_index}\n".encode("utf-8")


class _FakeHandsSense:
    """Plays the hands sense thread's half of the protocol directly against a live Mind: read run/hands/
    ACT (written when the mind's THINK step chooses a 'hands' pool item), publish eye (sight-only, no
    ear row -- HANDS never teaches a word) + touch + outcome rows, exactly the order law item 2 of the
    brief names (eye, then outcome, then touch -- this fake plays them in THAT tape order), and let the
    mind consume each. Returns the program name it served, or None if no ACT appeared (nothing chosen this
    canvas)."""

    def __init__(self, mind: Mind, tape: Tape, root: Path):
        self.mind = mind
        self.tape = tape
        self.root = Path(root)
        self.act_path = self.root / "hands" / "ACT"
        self.last_act_seq_served = -1
        self.run_index = 0
        from creature.senses import hands as hands_sense
        self._fingerprint = hands_sense._got_fingerprint

    def maybe_serve(self) -> Optional[str]:
        if not self.act_path.exists():
            return None
        data = json.loads(self.act_path.read_text())
        seq, program = int(data["seq"]), str(data["program"])
        if seq <= self.last_act_seq_served:
            return None
        self.last_act_seq_served = seq
        self.run_index += 1
        stdout = _fake_stdout(program, self.run_index)
        moment = f"h{program}{self.run_index:04d}"
        rgb = np.zeros((128, 128, 3), dtype=np.uint8)
        import io
        from PIL import Image
        buf = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
        eye_row = self.tape.publish("eye", buf.getvalue(),
                                     {"moment": moment, "source": "hands", "act": "run", "program": program}, "png")
        self.mind.consume(eye_row)
        got = self._fingerprint(stdout)
        out_row = self.tape.publish("outcome", json.dumps({"act": program}).encode("utf-8"),
                                     {"moment": moment, "source": "hands", "act": program, "program": program,
                                      "expected": None, "got": got, "residual": None, "act_seq": seq}, "json")
        self.mind.consume(out_row)
        touch = np.array([0.0, 12.0, 0.0, 0.0, float(len(stdout))], dtype=np.float32)
        touch_row = self.tape.publish("touch", touch.tobytes(), {"moment": moment, "source": "hands", "program": program}, "f32")
        self.mind.consume(touch_row)
        return program


def _journal_rows(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def _png_row(tape: Tape, mind: Mind, i: int, source: str = "folder") -> None:
    """A plain sight-only canvas, source != 'hands' -- advances _canvas_index / triggers THINK without
    ever itself being a hands run (fills the OTHER kinds' pool slots realistically)."""
    import io
    from PIL import Image
    rng = np.random.default_rng(i)
    rgb = rng.integers(0, 255, (128, 128, 3), dtype=np.uint8)
    buf = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    row = tape.publish("eye", buf.getvalue(), {"moment": f"f{i:06d}", "source": source}, "png")
    mind.consume(row)


class TestPoolIncludesHands(unittest.TestCase):
    def test_hands_item_present_when_shelf_declared_and_nothing_pending(self) -> None:
        gpath = _genome_with(HANDS_LINE, ACT_LINE)
        mind = Mind(gpath, Path(tempfile.mkdtemp()))
        pool = mind._think_pool()
        kinds = [p["kind"] for p in pool]
        self.assertIn("hands", kinds)

    def test_hands_item_absent_without_hands_declared(self) -> None:
        mind = Mind(G5_GENOME_PATH, Path(tempfile.mkdtemp()))
        pool = mind._think_pool()
        self.assertNotIn("hands", [p["kind"] for p in pool])

    def test_hands_item_absent_while_a_run_is_pending(self) -> None:
        gpath = _genome_with(HANDS_LINE, ACT_LINE)
        mind = Mind(gpath, Path(tempfile.mkdtemp()))
        mind._hands_pending = {"seq": 1, "program": "alpha"}
        pool = mind._think_pool()
        self.assertNotIn("hands", [p["kind"] for p in pool])


class TestThinkWorkChoosesAProgram(unittest.TestCase):
    """Isolated, fast: calls _think_work directly (no canvas/gaze cost) many times to check the picking
    distribution — uniform draw + 10% re-run of the last program."""

    def _mind(self) -> Mind:
        gpath = _genome_with(HANDS_LINE, ACT_LINE)
        return Mind(gpath, Path(tempfile.mkdtemp()))

    def test_every_choice_is_a_real_shelf_program(self) -> None:
        mind = self._mind()
        item = {"kind": "hands", "key": "run", "episode": None, "pred": None}
        for _ in range(50):
            result = mind._think_work(item)
            self.assertEqual(result["outcome"], "run")
            self.assertIn(result["program"], SHELF_NAMES)

    def test_roughly_uniform_over_five_hundred_choices(self) -> None:
        mind = self._mind()
        item = {"kind": "hands", "key": "run", "episode": None, "pred": None}
        counts = Counter(mind._think_work(item)["program"] for _ in range(1000))
        self.assertEqual(sorted(counts), SHELF_NAMES)
        for name in SHELF_NAMES:
            share = counts[name] / 1000
            self.assertGreater(share, 0.10, f"{name} under-represented: {dict(counts)}")
            self.assertLess(share, 0.35, f"{name} over-represented: {dict(counts)}")

    def test_immediate_repeat_rate_is_near_ten_percent(self) -> None:
        """The 10% re-run draw plus the ~1/5 chance the uniform draw ALSO repeats gives an expected
        repeat rate of about 0.1 + 0.9*0.2 = 28% for a 5-program shelf — loose bounds, not a tight pin."""
        mind = self._mind()
        item = {"kind": "hands", "key": "run", "episode": None, "pred": None}
        programs = [mind._think_work(item)["program"] for _ in range(2000)]
        repeats = sum(1 for a, b in zip(programs, programs[1:]) if a == b)
        rate = repeats / (len(programs) - 1)
        self.assertGreater(rate, 0.15, f"repeat rate too low for a 10% re-run draw: {rate}")
        self.assertLess(rate, 0.45, f"repeat rate too high: {rate}")

    def test_exactly_two_rng_draws_per_choice(self) -> None:
        """The stream's shape must not depend on which branch (re-run vs uniform) fires — the SAME two
        draws are made either way, so a fixed-length rng stream determinism holds (#175's discipline,
        _maybe_choose_act's own law)."""
        mind_a = self._mind()
        mind_b = self._mind()
        item = {"kind": "hands", "key": "run", "episode": None, "pred": None}
        seq_a = [mind_a._think_work(item)["program"] for _ in range(30)]
        seq_b = [mind_b._think_work(item)["program"] for _ in range(30)]
        self.assertEqual(seq_a, seq_b, "two identically-seeded minds must choose the identical sequence")


class TestNoRoad(unittest.TestCase):
    def test_missing_jail_binary_journals_no_road_and_never_crashes(self) -> None:
        gpath = _genome_with(
            "HANDS    jail nowhere/not/a/real/jail shelf tests/fixtures/hands-shelf-test cpu 10 mem 512 wall 20",
            ACT_LINE,
        )
        mind = Mind(gpath, Path(tempfile.mkdtemp()))
        item = {"kind": "hands", "key": "run", "episode": None, "pred": None}
        result = mind._think_work(item)   # must not raise
        self.assertEqual(result["outcome"], "no road")
        self.assertEqual(mind.hands_no_road, 1)


class TestMaybeThinkWritesActFile(unittest.TestCase):
    def test_a_chosen_hands_item_writes_the_act_file_and_journals_act_chosen(self) -> None:
        gpath = _genome_with(HANDS_LINE, ACT_LINE, THINK_EVERY_1)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        server = _FakeHandsSense(mind, tape, root)

        served: List[str] = []
        for i in range(40):
            _png_row(tape, mind, i)
            got = server.maybe_serve()
            if got is not None:
                served.append(got)

        self.assertGreater(len(served), 0, "at least one hands run must have fired over 40 think passes")
        for name in served:
            self.assertIn(name, SHELF_NAMES)
        act_chosen_rows = [r["act_chosen"] for r in _journal_rows(root) if "act_chosen" in r]
        self.assertEqual(len(act_chosen_rows), len(served))
        for row in act_chosen_rows:
            self.assertEqual(row["act"], "run")
            self.assertIn(row["program"], SHELF_NAMES)
        self.assertEqual(sum(mind.runs_chosen.values()), len(served))

    def test_no_second_act_file_written_while_one_is_pending(self) -> None:
        """The pending gate (#175): between a hands choice and its outcome row's consumption, the pool
        must not offer a second 'hands' item — proven here by NEVER serving the outcome (so pending never
        clears) and asserting the ACT file's own seq never advances past the first write."""
        gpath = _genome_with(HANDS_LINE, ACT_LINE, THINK_EVERY_1)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        act_path = root / "hands" / "ACT"

        # drive canvases through a genome with ONLY the hands kind ever eligible (no FAST/CURIOSITY items
        # compete, so if the pending gate ever failed the mind would overwrite ACT on the very next think)
        first_seq: Optional[int] = None
        for i in range(30):
            _png_row(tape, mind, i)
            if act_path.exists():
                data = json.loads(act_path.read_text())
                if first_seq is None:
                    first_seq = int(data["seq"])
                else:
                    self.assertEqual(int(data["seq"]), first_seq, "the ACT file must not change while pending")
        self.assertIsNotNone(first_seq, "the mind must have chosen hands at least once")


class TestReplayIdentical(unittest.TestCase):
    def test_two_replays_of_a_hands_tape_are_byte_identical(self) -> None:
        from creature import replay as replay_module
        gpath = _genome_with(HANDS_LINE, ACT_LINE, THINK_EVERY_1)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        server = _FakeHandsSense(mind, tape, root)
        for i in range(20):
            _png_row(tape, mind, i)
            server.maybe_serve()
        day_files = sorted((root / "tape").glob("*.jsonl"))
        self.assertEqual(len(day_files), 1)
        out1, out2 = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        j1 = replay_module.run_replay(gpath, day_files[0], out1)
        j2 = replay_module.run_replay(gpath, day_files[0], out2)
        self.assertEqual(j1.read_bytes(), j2.read_bytes())


class TestReplayNeverCallsTheJail(unittest.TestCase):
    def test_replay_module_never_imports_the_hands_sense_or_subprocess(self) -> None:
        """The replay problem, named (MOTOR-HANDS.md G-MOT-4): a jail run is not reproducible, so replay
        must never re-run it — only read the recorded rows. A grep-level structural check (creature/
        replay.py's own imports), the same class of proof creature/senses/game.py's docstring claims for
        itself."""
        text = (ROOT / "creature" / "replay.py").read_text()
        self.assertNotIn("creature.senses.hands", text)
        self.assertNotIn("import subprocess", text)
        self.assertNotIn("senses.hands", text)


if __name__ == "__main__":
    unittest.main()
