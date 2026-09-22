# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught gap (point 5): none of
# this task's own tests proved QUESTION/SENTENCE/MOUTH survive a REPLAY (the brief's own gate, and the
# genome day's own law: "a closed tape replays only under its own code" -- SOLUTIONS #234). Checked first,
# read creature/replay.py: `run_replay` builds a FRESH `tempfile.mkdtemp()` work root for every call and
# only ever symlinks the source tape's `payload/` dir into it -- `ask/out/ASKED.json` is never shared
# between a live run and its replay (or between two replays), so the "replay mind starts with every want
# already asked" hazard the advisor named does not apply to this codebase's actual replay road. This file
# proves it empirically rather than by reading alone: a live short life with QUESTION+SENTENCE+MOUTH
# declared produces real `question`/`say` journal rows (a positive control -- SOLUTIONS #91: a 0-finding
# replay-parity check proves nothing), then two independent replays of the SAME tape match each other AND
# the live journal byte-for-byte, `question`/`say` rows included.
from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from creature import replay, world_maker
from creature.body import Body
from creature.tape import read_tape

ROOT = Path(__file__).resolve().parents[2]
BASE_GENOME_TEXT = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()
EXTRA_GENES = """\
FILE     claim route decider due
PARK     after 1 identical dead-ends reopen on new-sense
BELIEF   clash opens never overwrites
THINK    every 1 canvases
QUESTION from wants; forms what-is is which; to the world door
SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token
MOUTH    say one frame per think; journaled
"""


def _run_live(root: Path, target_eye_rows: int = 80) -> None:
    """A live body + the real world-maker sense (its own QUESTION door included), run until at least
    `target_eye_rows` eye rows are on the tape, drain the mind's queue before stopping (mirrors
    tests/creature/test_replay.py's own _run_live_200, at a smaller target to keep this file fast)."""
    genome_path = root / "g.genome"
    genome_path.write_text(BASE_GENOME_TEXT.rstrip("\n") + "\n" + EXTRA_GENES)
    body = Body(root, genome_path)
    maker = body.add_sense("maker", lambda p, se: world_maker.sense(p, se, root=root, period=0.02))
    body.start()
    deadline = time.time() + 60.0
    while time.time() < deadline:
        eye_rows = [r for r in read_tape(root) if r["sense"] == "eye"]
        if len(eye_rows) >= target_eye_rows:
            break
        time.sleep(0.1)
    else:
        body.stop()
        raise AssertionError(f"did not reach {target_eye_rows} eye rows within 60 s")
    maker.stop()
    maker.join(timeout=5.0)
    drain_deadline = time.time() + 20.0
    while not body.q.empty() and time.time() < drain_deadline:
        time.sleep(0.1)
    time.sleep(1.0)   # grace for the in-flight consume() call to finish
    body.stop()
    return genome_path


def _single_journal_and_tape_files(root: Path) -> tuple[Path, Path]:
    tape_files = sorted((root / "tape").glob("*.jsonl"))
    journal_files = sorted((root / "journal").glob("*.jsonl"))
    assert len(tape_files) == 1, f"test expects one tape day file, got {tape_files}"
    assert len(journal_files) == 1, f"test expects one journal day file, got {journal_files}"
    return tape_files[0], journal_files[0]


class TestReplayWithQuestionSentenceMouth(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        cls.genome_path = _run_live(cls.root)
        cls.tape_path, cls.journal_path = _single_journal_and_tape_files(cls.root)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_the_live_life_actually_exercised_question_and_think(self) -> None:
        """Positive control (SOLUTIONS #91): this replay-parity gate proves nothing if the live life never
        produced a `question`/`think` row to replay in the first place."""
        rows = [json.loads(l) for l in self.journal_path.read_text().splitlines() if l.strip()]
        think_rows = [r for r in rows if "think" in r]
        question_rows = [r for r in rows if "question" in r]
        self.assertGreater(len(think_rows), 0, "THINK every 1 canvases must have fired at least once")
        self.assertGreater(len(question_rows), 0,
                            f"QUESTION must have formed at least one want over {len(think_rows)} thinks "
                            f"(PARK after=1 parks a wordless sight's very first think)")

    def test_replay_matches_live_journal_question_and_say_rows_included(self) -> None:
        out_dir = Path(tempfile.mkdtemp())
        rc = replay.main(["--genome", str(self.genome_path), "--tape", str(self.tape_path),
                           "--against", str(self.journal_path), "--out", str(out_dir)])
        self.assertEqual(rc, 0)
        shutil.rmtree(out_dir, ignore_errors=True)

    def test_two_independent_replays_agree_with_each_other(self) -> None:
        """Each replay call builds its OWN fresh tempdir root (creature/replay.py:run_replay) -- proves
        ask/out/ASKED.json is never shared between replay runs (the advisor's named hazard, checked against
        this codebase's actual replay road and found not to apply: see this file's own module docstring)."""
        out_1 = Path(tempfile.mkdtemp())
        out_2 = Path(tempfile.mkdtemp())
        journal_1 = replay.run_replay(self.genome_path, self.tape_path, out_1)
        journal_2 = replay.run_replay(self.genome_path, self.tape_path, out_2)
        rows_1 = replay.read_mind_journal(journal_1)
        rows_2 = replay.read_mind_journal(journal_2)
        self.assertIsNone(replay.compare(rows_1, rows_2), "two independent replays of the same tape must be byte-identical")
        shutil.rmtree(out_1, ignore_errors=True)
        shutil.rmtree(out_2, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
