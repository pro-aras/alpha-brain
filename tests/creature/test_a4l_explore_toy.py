# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:37 +0400 — docs/A4-LADDER-PREREG.md §2.5 PHASE 1:
# the toy's ADMISSION. tools/toys/act_chooser_toy.py carries a VERBATIM copy of the game act chooser's arithmetic
# (creature/mind.py `_maybe_choose_act` + `_recent_reflex_residuals` + `_record_reflex`); these tests pin that copy to
# the mind three ways: (1) the hour-1 fixture — alpha4-1's own game rows and the 121 `act` journal rows a replay of
# them wrote (tests/fixtures/a4l-explore/, committed; weights all zero: nothing was rewarded in hour 1); (2) a REAL Mind
# driven through a planted-reward history in the LIFE's row order (the NONZERO weights the first hour never has);
# (3) the harness itself (the game-worlds venv only) replaying the life's first 120 game steps act for act.
from __future__ import annotations

import inspect
import io
import json
import math
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape
from tools.toys import act_chooser_toy as toy

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "a4l-explore" / "hour1-game-rows.json"
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
ACT_LINE = "ACT      glance open ask turn step say run"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"
VENV = Path("/data/dev/game-worlds/venv/bin/python3")      # G5-G's install road (gymnasium + minigrid live only there)


def _jsonl(d: Path) -> List[dict]:
    out: List[dict] = []
    for f in sorted(d.glob("*.jsonl")):
        out.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
    return out


def _png(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


class TestPinnedToTheMind(unittest.TestCase):
    """A drift alarm: the copy's constants and the lines it copies must still be the mind's."""

    def test_constants(self) -> None:
        import creature.mind as cm
        from creature.senses import game as game_sense
        self.assertEqual(toy.OUTCOME_EPISODES_CAP, cm.OUTCOME_EPISODES_CAP)
        self.assertEqual(toy.ACT_NAMES, game_sense.ACT_NAMES)

    def test_the_copied_lines_are_still_the_minds(self) -> None:
        src = inspect.getsource(Mind._maybe_choose_act)
        for line in ("residuals = self._recent_reflex_residuals(name, k=10)",
                     "weights.append(sum(residuals) / len(residuals) if residuals else 0.0)",
                     "u = float(self._act_rng.random())",
                     "if u < 0.1:",
                     "idx = int(self._act_rng.integers(0, n_actions))",
                     "tied = [i for i, w in enumerate(weights) if w == best]",
                     "pick = int(self._act_rng.integers(0, len(tied)))"):
            self.assertIn(line, src, f"the mind's chooser changed: {line!r} — re-pin the toy's copy")
        self.assertIn("np.random.default_rng([int(self.genome.seed), 0x4143544d])", inspect.getsource(Mind.__init__))
        rec = inspect.getsource(Mind._record_reflex)
        for line in ("residual = abs(got_f - expected)",
                     "surprise=float(residual) if residual is not None else 0.0",
                     "self._act_expected[act] = old + (got_f - old) / n"):
            self.assertIn(line, rec, f"the mind's reflex filing changed: {line!r}")


class TestHourOneFixtureParity(unittest.TestCase):
    """THE ADMISSION (the brief's words): the function fed the same outcome history reproduces the journal's
    weights on ≥ 50 rows — here on all 121, and the chosen act on all 121 (the act rng is consumed only here)."""

    def test_every_act_row_reproduced(self) -> None:
        doc = json.loads(FIXTURE.read_text())
        rows = toy.replay_choices(doc["tape_game_rows"], doc["journal_act_rows"], doc["life_seed"])
        self.assertEqual(len(rows), 121)
        self.assertEqual(sum(r["weights_match"] for r in rows), 121)
        self.assertEqual(sum(r["act_match"] for r in rows), 121)

    def test_a_wrong_seed_is_caught(self) -> None:
        """The control that the check checks: the same history under another seed reproduces the (zero) weights
        but NOT the chosen acts."""
        doc = json.loads(FIXTURE.read_text())
        rows = toy.replay_choices(doc["tape_game_rows"], doc["journal_act_rows"], doc["life_seed"] + 1)
        self.assertEqual(sum(r["weights_match"] for r in rows), 121)
        self.assertLess(sum(r["act_match"] for r in rows), 60)


class TestRealMindNonzeroWeights(unittest.TestCase):
    """A real Mind in the LIFE's row order — frame t's ear+eye (the mind chooses a_{t+1}), THEN frame t's outcome
    (the act a_t that produced it, its planted reward) — with rewards planted so the weights become NONZERO; the
    pure walk over the same tape must reproduce every act row the mind journaled."""

    REWARDS: Dict[int, float] = {12: 0.38125, 40: 0.859375, 75: 0.5, 110: 0.1}

    def test_nonzero_weights_reproduced(self) -> None:
        d = Path(tempfile.mkdtemp())
        gpath = d / "genome.genome"
        gpath.write_text(G4_GENOME_PATH.read_text() + "\n" + ACT_LINE + "\n" + OUTCOME_LINE + "\n")
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        rng = np.random.default_rng(7)
        act_path = root / "game" / "ACT"

        def frame(step: int):
            moment = f"gfake0000000s{step:09d}"
            common = {"game": "babyai-gotolocal", "episode": 0, "step": step}
            mind.consume(tape.publish("ear", b"ball", {"moment": moment, "source": "game", "word": "ball",
                                                        "mission": "go to the red ball", **common}, "txt"))
            mind.consume(tape.publish("eye", _png(rng.integers(0, 255, (128, 128, 3), dtype=np.uint8)),
                                      {"moment": moment, "source": "game", "n_actions": 7,
                                       "act_names": toy.ACT_NAMES, **common}, "png"))
            data = json.loads(act_path.read_text())
            return int(data["act"]), int(data["seq"]), moment, common

        pending = frame(0)[:2]
        for t in range(1, 161):
            act_idx, act_seq = pending
            nxt_idx, nxt_seq, moment, common = frame(t)
            got = self.REWARDS.get(t, 0.0)
            name = toy.ACT_NAMES[act_idx]
            payload = json.dumps({"act": name, "expected": None, "got": got, "residual": None, "source": "game"}).encode()
            mind.consume(tape.publish("outcome", payload,
                                      {"moment": moment, "source": "game", "act": name, "act_idx": act_idx,
                                       "expected": None, "got": got, "residual": None, "chosen_by": "mind",
                                       "road": "mind", "act_seq": act_seq, "terminated": False, "truncated": False,
                                       **common}, "json"))
            pending = (nxt_idx, nxt_seq)
        self.assertEqual(mind.act_mismatches, 0)
        rows = toy.replay_choices(_jsonl(root / "tape"), _jsonl(root / "journal"), int(mind.genome.seed))
        self.assertEqual(len(rows), 161)
        nonzero = [r for r in rows if any(r["weights"])]
        self.assertGreaterEqual(len(nonzero), 50, f"only {len(nonzero)} rows carry a nonzero weight")
        bad = [r["seq"] for r in rows if not (r["weights_match"] and r["act_match"])]
        self.assertEqual(bad, [], f"rows the pure copy does not reproduce: {bad[:5]}")


class TestPureParts(unittest.TestCase):
    def test_candidate_values_optimism_and_window(self) -> None:
        ring = toy.Ring()
        self.assertEqual(toy.reward_values(ring, toy.ACT_NAMES), [1.0] * 7)          # untried → the optimism prior
        ring.record("left", 0.0)
        v = toy.reward_values(ring, toy.ACT_NAMES)
        self.assertEqual(v[0], 0.0)
        self.assertEqual(v[1:], [1.0] * 6)
        for _ in range(9):
            ring.record("left", 0.0)
        ring.record("left", 0.5)                                                      # the 11th: the window is the last 10
        self.assertAlmostEqual(toy.reward_values(ring, toy.ACT_NAMES)[0], 0.05, places=12)
        self.assertEqual(toy.old_weights(ring, toy.ACT_NAMES)[1:], [0.0] * 6)

    def test_old_weights_residual_law(self) -> None:
        """The surprise is |got − the act's running mean BEFORE this outcome|; the first outcome files 0.0."""
        ring = toy.Ring()
        f0 = ring.record("left", 0.0)
        self.assertIsNone(f0["residual"])
        f1 = ring.record("left", 0.4)
        self.assertEqual(f1["residual"], 0.4)
        f2 = ring.record("left", 0.0)                                                 # mean after two = 0.2
        self.assertAlmostEqual(f2["residual"], 0.2, places=15)
        self.assertAlmostEqual(toy.old_weights(ring, ["left"])[0], (0.0 + 0.4 + 0.2) / 3, places=15)

    def test_two_draws_every_call_either_branch(self) -> None:
        class Counting:
            def __init__(self, rng):
                self.rng, self.calls = rng, 0

            def random(self):
                self.calls += 1
                return self.rng.random()

            def integers(self, lo, hi):
                self.calls += 1
                return self.rng.integers(lo, hi)

        branches = set()
        for s in range(200):
            c = Counting(np.random.default_rng(s))
            _idx, explored = toy.choose([0.0, 0.3, 0.3, 0.0, 0.0, 0.0, 0.0], c, 7)
            branches.add(explored)
            self.assertEqual(c.calls, 2)
        self.assertEqual(branches, {True, False})

    def test_sampled_choice_two_draws_and_proportional(self) -> None:
        """(v-b)/(v-c)'s draw (edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 12:21 +0400): two draws every call, either
        branch; outside the 10 % branch the act is drawn ∝ value."""
        class Counting:
            def __init__(self, rng):
                self.rng, self.calls = rng, 0

            def random(self):
                self.calls += 1
                return self.rng.random()

            def integers(self, lo, hi):
                self.calls += 1
                return self.rng.integers(lo, hi)

        vals = [0.05, 0.05, 0.9, 0.05, 0.05, 0.05, 0.05]
        counts = [0] * 7
        rng = np.random.default_rng(3)
        for _ in range(20000):
            c = Counting(rng)
            idx, explored = toy.sampled_choice(vals, c, 7)
            self.assertEqual(c.calls, 2)
            if not explored:
                counts[idx] += 1
        share = counts[2] / sum(counts)
        self.assertAlmostEqual(share, 0.9 / 1.2, delta=0.01)

    def test_episode_credit_values(self) -> None:
        pol = toy.EpisodeCredit(1)
        for act, got, te, tr in (("left", 0.0, False, False), ("forward", 0.0, False, False), ("pickup", 0.6, True, False),
                                 ("left", 0.0, False, False), ("done", 0.0, False, True)):
            pol.observe(act, got, te, tr)
        v = dict(zip(toy.ACT_NAMES, pol.values()))
        self.assertAlmostEqual(v["left"], 0.3 + toy.EPS, places=12)
        self.assertAlmostEqual(v["forward"], 0.6 + toy.EPS, places=12)
        self.assertAlmostEqual(v["pickup"], 0.6 + toy.EPS, places=12)
        self.assertAlmostEqual(v["done"], 0.0 + toy.EPS, places=12)
        for a in ("right", "drop", "toggle"):
            self.assertAlmostEqual(v[a], 1.0 + toy.EPS, places=12)
        self.assertEqual(pol.episode_acts, [])

    def test_null_bound(self) -> None:
        for n, p0 in ((14, 0.29), (24, 0.29), (100, 0.29)):
            k, rate = toy.null_bound(n, p0)
            tail = lambda kk: sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(kk, n + 1))
            self.assertLessEqual(tail(k), 0.05)
            self.assertGreater(tail(k - 1), 0.05)
            self.assertEqual(rate, k / n)


@unittest.skipUnless(VENV.exists(), "the game-worlds venv (gymnasium + minigrid) is not on this box")
class TestHarnessReplaysTheLifesFirstHour(unittest.TestCase):
    """(0b) in the suite: the harness under the venv, the old chooser at the life's seed — its first 120 game
    steps equal alpha4-1's first-hour outcome rows on act, reward, terminated, truncated, episode and step."""

    def test_first_120_steps(self) -> None:
        code = ("import sys, json\n"
                f"sys.path.insert(0, {str(ROOT)!r})\n"
                "from tools.toys.act_chooser_toy import OldChooser, run_game, LIFE_SEED\n"
                "r = run_game(OldChooser(LIFE_SEED), LIFE_SEED, episodes=3, keep_trace=120)\n"
                "print(json.dumps(r['trace']))\n")
        env = {k: v for k, v in os.environ.items() if k != "BABYAI_DONE_ACTIONS"}
        env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        p = subprocess.run([str(VENV), "-c", code], capture_output=True, text=True, timeout=300, env=env)
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        trace = json.loads(p.stdout.strip().splitlines()[-1])
        doc = json.loads(FIXTURE.read_text())
        life = [r["meta"] for r in doc["tape_game_rows"] if r["sense"] == "outcome"]
        self.assertEqual(len(life), 120)
        for i, m in enumerate(life):
            got = trace[i]
            self.assertEqual((got["act"], got["act_idx"], got["got"], got["terminated"], got["truncated"],
                              got["episode"], got["step"]),
                             (m["act"], m["act_idx"], m["got"], m["terminated"], m["truncated"], m["episode"], m["step"]),
                             f"game step {i + 1}")


if __name__ == "__main__":
    unittest.main()
