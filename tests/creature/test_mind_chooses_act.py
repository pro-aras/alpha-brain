# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:45 +0400 — LIFE-D-ACT-SOUND.md item 2 (L-8; the
# plan's §4 L-8, MOTOR-HANDS.md G-MOT-1/G-MOT-4's "replay problem, named" -- the act's INTENT is a pure
# function of (genome, seed, tape), the OUTCOME is a recorded row replay reads). creature/mind.py chooses
# the game's next act on every game eye row, writes root/game/ACT atomically, and asserts the outcome row
# that follows carries the act it chose -- a REPLAY-divergence-by-definition check (`act_mismatch`).
#
# A FAKE worker loop (no venv needed): the test itself plays the worker's part -- publish ear+eye, let the
# mind consume the eye row (which writes root/game/ACT), read that file back, then publish the matching
# outcome row exactly as a real worker obeying it would. This is the SAME protocol tools/game_worker_
# babyai.py's --act-file implements (test_game_act_file.py proves that one directly against the real venv);
# here it proves the MIND's half without needing gymnasium/minigrid at all.
from __future__ import annotations

import io
import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"

ACT_LINE = "ACT      glance open ask turn step say run"          # LIFE.genome:77, verbatim -- turn+step present
ACT_LINE_NO_GAME = "ACT      glance open ask"                     # G5-K's own line -- no turn/step
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"

GAME_ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]


def _g4_with(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _canvas(rng: np.random.Generator, size: int = 128) -> np.ndarray:
    return rng.integers(0, 255, (size, size, 3), dtype=np.uint8)


def _journal_rows(root: Path) -> List[dict]:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


class _FakeWorker:
    """Plays the worker's part of the --act-file protocol directly against a live Mind: publish ear+eye
    for a frame, let the mind consume the eye row (which -- when the ACT policy is on -- writes
    root/game/ACT), read that file back, and publish the outcome row a real, OBEDIENT worker would have
    written (chosen_by "mind", act_idx == what the mind chose, act_seq == the seq it read). A second mode
    (`obedient=False`) drives the SAME frames but ignores the ACT file (used nowhere in this file directly
    -- the shuffled-twin test instead corrupts the RECORDED tape after the fact, closer to what a real
    divergence looks like)."""

    def __init__(self, mind: Mind, tape: Tape, root: Path, seed: int = 20260922, reward: float = 0.0,
                 n_actions: int = 7, act_names: Optional[List[str]] = None):
        self.mind = mind
        self.tape = tape
        self.root = Path(root)
        self.rng = np.random.default_rng(seed)
        self.reward = reward
        self.n_actions = n_actions
        self.act_names = act_names or GAME_ACT_NAMES
        self.step = 0
        self.act_path = self.root / "game" / "ACT"

    def frame(self) -> int:
        """Publishes one ear+eye pair, lets the mind consume the eye row (choosing an act), reads the act
        file, publishes the matching outcome row, lets the mind consume THAT too. Returns the chosen
        act_idx."""
        moment = f"gfake0000000s{self.step:09d}"
        common = {"game": "babyai-gotolocal", "episode": 0, "step": self.step}
        ear_row = self.tape.publish("ear", b"ball", {"moment": moment, "source": "game", "word": "ball",
                                                       "mission": "go to the red ball", **common}, "txt")
        self.mind.consume(ear_row)
        rgb = _canvas(self.rng)
        eye_row = self.tape.publish("eye", _png_bytes(rgb),
                                     {"moment": moment, "source": "game", "n_actions": self.n_actions,
                                      "act_names": self.act_names, **common}, "png")
        self.mind.consume(eye_row)

        data = json.loads(self.act_path.read_text())
        idx, seq = int(data["act"]), int(data["seq"])
        act_name = self.act_names[idx]
        payload = json.dumps({"act": act_name, "expected": None, "got": self.reward, "residual": None,
                               "source": "game"}).encode("utf-8")
        out_row = self.tape.publish("outcome", payload,
                                     {"moment": moment, "source": "game", "act": act_name, "act_idx": idx,
                                      "expected": None, "got": self.reward, "residual": None,
                                      "chosen_by": "mind", "road": "mind", "act_seq": seq,
                                      "terminated": False, "truncated": False, **common}, "json")
        self.mind.consume(out_row)
        self.step += 1
        return idx


class TestActPolicyGate(unittest.TestCase):
    def test_turn_and_step_present_arms_the_policy(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        mind = Mind(gpath, Path(tempfile.mkdtemp()))
        self.assertTrue(mind._act_policy_on)

    def test_without_turn_and_step_the_policy_is_off(self) -> None:
        gpath = _g4_with(ACT_LINE_NO_GAME, OUTCOME_LINE)
        mind = Mind(gpath, Path(tempfile.mkdtemp()))
        self.assertFalse(mind._act_policy_on)

    def test_off_policy_never_writes_the_act_file(self) -> None:
        gpath = _g4_with(ACT_LINE_NO_GAME, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        moment = "gfake0000000s000000000"
        ear_row = tape.publish("ear", b"ball", {"moment": moment, "source": "game", "word": "ball", "mission": "go to the red ball"}, "txt")
        mind.consume(ear_row)
        rgb = np.random.default_rng(1).integers(0, 255, (128, 128, 3), dtype=np.uint8)
        eye_row = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "game", "n_actions": 7, "act_names": GAME_ACT_NAMES}, "png")
        mind.consume(eye_row)
        self.assertFalse((root / "game" / "ACT").exists())


class TestFakeWorkerTwentyFrames(unittest.TestCase):
    """The brief's own test: 20 frames, 20 acts written by the mind, 20 obeyed, chosen_by 'mind' on
    every outcome; the census (verbs, never a total); no crash, no hang (a deadline via a fixed frame
    count, never a real timeout -- the fake worker IS the deadline)."""

    def _run(self, n: int = 20, seed: int = 20260922, reward: float = 0.0):
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        worker = _FakeWorker(mind, tape, root, seed=seed, reward=reward)
        acts = [worker.frame() for _ in range(n)]
        return gpath, root, mind, acts

    def test_twenty_acts_written_and_obeyed(self) -> None:
        gpath, root, mind, acts = self._run(20)
        self.assertEqual(len(acts), 20)
        self.assertEqual(sum(mind.acts_chosen.values()), 20)
        act_rows = [r["act"] for r in _journal_rows(root) if "act" in r]
        self.assertEqual(len(act_rows), 20)
        for r in act_rows:
            self.assertEqual(r["policy"], "outcome-weighted")
            self.assertIn("weights", r)
            self.assertEqual(len(r["weights"]), 7)
        outcome_rows = [r["outcome"] for r in _journal_rows(root) if "outcome" in r]
        self.assertEqual(len(outcome_rows), 20)
        mismatch_flags = [r["outcome"].get("act_mismatch") for r in _journal_rows(root) if "outcome" in r]
        self.assertEqual(mismatch_flags, [False] * 20, "every outcome the fake worker obeyed must read act_mismatch False")
        self.assertEqual(mind.act_mismatches, 0)

    def test_census_no_verb_dominates_under_flat_residual(self) -> None:
        """200 frames, reward always 0.0 (a flat residual -- every act ties) -- the brief's own bar: no
        verb >= 95%. Prints the counts (the brief's own instruction)."""
        _gpath, _root, mind, _acts = self._run(200, seed=99, reward=0.0)
        counts = dict(mind.acts_chosen)
        print(f"census (200 frames, flat residual): {counts}")
        total = sum(counts.values())
        self.assertEqual(total, 200)
        self.assertGreater(len(counts), 1, "more than one verb must ever have been chosen")
        for name, c in counts.items():
            self.assertLess(c / total, 0.95, f"verb {name!r} took {c}/{total} >= 95%: {counts}")
        for name in GAME_ACT_NAMES:
            self.assertGreater(counts.get(name, 0), 0, f"verb {name!r} was NEVER chosen in 200 frames (0-count G-MOT-1 refusal): {counts}")


class TestReplayIdenticalIncludingActs(unittest.TestCase):
    def test_two_replays_of_the_same_tape_are_byte_identical(self) -> None:
        from creature import replay as replay_module
        gpath, root, _mind, _acts = TestFakeWorkerTwentyFrames()._run(20)
        day_files = sorted((root / "tape").glob("*.jsonl"))
        self.assertEqual(len(day_files), 1)
        out1, out2 = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        j1 = replay_module.run_replay(gpath, day_files[0], out1)
        j2 = replay_module.run_replay(gpath, day_files[0], out2)
        self.assertEqual(j1.read_bytes(), j2.read_bytes(), "two replays (including the mind's OWN re-derived acts) must be byte-identical")
        act_rows = [json.loads(l)["act"] for l in j1.read_text().splitlines() if '"act"' in l and json.loads(l).get("act")]
        self.assertEqual(len(act_rows), 20)


class TestShuffledActTwinDiverges(unittest.TestCase):
    """The control that proves the check checks (the brief's own words): corrupt ONLY the recorded
    outcome rows' act_idx (a cyclic shift, guaranteed != the original at every row since n_actions > 1)
    and replay -- the mind re-derives the SAME choice it always would (deterministic function of genome/
    seed/tape), so act_mismatch must flip to True starting at the FIRST outcome row."""

    def test_diverges_at_the_first_outcome_row(self) -> None:
        from creature import replay as replay_module

        gpath, root, _mind, _acts = TestFakeWorkerTwentyFrames()._run(20)
        day_files = sorted((root / "tape").glob("*.jsonl"))
        self.assertEqual(len(day_files), 1)
        day_file = day_files[0]

        out_orig = Path(tempfile.mkdtemp())
        j_orig = replay_module.run_replay(gpath, day_file, out_orig)
        orig_rows = replay_module.read_mind_journal(j_orig)

        shuffled_dir = Path(tempfile.mkdtemp())
        os.symlink((day_file.parent / "payload").resolve(), shuffled_dir / "payload")
        shuffled_day = shuffled_dir / day_file.name
        lines = []
        first_outcome_seq = None
        for line in day_file.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("sense") == "outcome" and (row.get("meta") or {}).get("chosen_by") == "mind":
                m = dict(row["meta"])
                orig_idx = int(m["act_idx"])
                m["act_idx"] = (orig_idx + 1) % 7   # cyclic shift: guaranteed != orig_idx for n_actions=7
                row = {**row, "meta": m}
                if first_outcome_seq is None:
                    first_outcome_seq = int(row["seq"])
            lines.append(json.dumps(row))
        shuffled_day.write_text("\n".join(lines) + "\n")
        self.assertIsNotNone(first_outcome_seq)

        out_shuf = Path(tempfile.mkdtemp())
        j_shuf = replay_module.run_replay(gpath, shuffled_day, out_shuf)
        shuf_rows = replay_module.read_mind_journal(j_shuf)

        diff = replay_module.compare(shuf_rows, orig_rows)
        self.assertIsNotNone(diff, "a cyclic act_idx shift on every mind-chosen outcome row must diverge somewhere")
        seq, field = diff
        self.assertEqual(seq, first_outcome_seq, f"must diverge at the FIRST shuffled outcome row (seq {first_outcome_seq}), got seq {seq}")
        self.assertEqual(field, "outcome", "the divergence must be inside the outcome journal row (its act_mismatch sub-field)")
        got_row = next(r for r in shuf_rows if r["seq"] == seq)
        want_row = next(r for r in orig_rows if r["seq"] == seq)
        self.assertFalse(want_row["outcome"]["act_mismatch"], "the ORIGINAL (unshuffled) replay must read act_mismatch False")
        self.assertTrue(got_row["outcome"]["act_mismatch"], "the SHUFFLED replay must read act_mismatch True at this row")


class TestActRngResumeSafe(unittest.TestCase):
    def test_resumed_mind_continues_the_same_rng_stream(self) -> None:
        """L-8: "_act_rng, resume-safe: its state in the snapshot" -- a mind that snapshots then resumes
        mid-life must choose the SAME next act a never-interrupted mind would (same genome/seed/tape),
        proving the rng stream survived the resume rather than restarting."""
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)

        root_a = Path(tempfile.mkdtemp())
        mind_a = Mind(gpath, root_a)
        tape_a = Tape(root_a)
        worker_a = _FakeWorker(mind_a, tape_a, root_a, seed=555)
        for _ in range(5):
            worker_a.frame()
        mind_a.snapshot()

        mind_b, last_seq = Mind.resume(gpath, root_a)   # resume from root_a's own snapshot (same root, continued life)
        self.assertGreater(last_seq, 0)
        tape_b = Tape(root_a)   # SAME tape/root -- continuing the same life's stream
        worker_b = _FakeWorker(mind_b, tape_b, root_a, seed=555)
        worker_b.step = worker_a.step   # continue the step/moment numbering where worker_a left off
        act6_resumed = worker_b.frame()

        # the control: an UNINTERRUPTED mind on an independent (but identically seeded) root/tape must
        # choose the identical 6th act -- proving the resumed rng stream matches the continuous one.
        root_c = Path(tempfile.mkdtemp())
        mind_c = Mind(gpath, root_c)
        tape_c = Tape(root_c)
        worker_c = _FakeWorker(mind_c, tape_c, root_c, seed=555)
        acts_c = [worker_c.frame() for _ in range(6)]

        self.assertEqual(act6_resumed, acts_c[5], "the resumed mind's 6th act must match the uninterrupted mind's 6th act")


if __name__ == "__main__":
    unittest.main()
