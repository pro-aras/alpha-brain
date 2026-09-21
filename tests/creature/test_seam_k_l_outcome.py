# edit: Claude (Fable 5.1), 2026-09-21 21:36 +0400 — THE K×L SEAM (SOLUTIONS #232 addendum: two modules by two builders wired by a third are
# tested AT THE SEAM): Builder L's game door publishes the reward as a tape row of sense "outcome" in Builder K's declared
# shape (act/expected/got/residual/source) PLUS its own extra meta keys (chosen_by, road, terminated, truncated, game,
# episode, step); Builder K's consumer (Mind._consume_outcome → _record_reflex) must read such a row, compute the residual
# from its per-act running expectation, write the reflex episode and the journal row — and be undisturbed by the extra keys
# and by an act outside K's ACT vocabulary (L's acts are the game's; K tags in_vocab, never refuses). The row below is
# built EXACTLY as creature/senses/game.py builds it (its meta dict copied), not a paraphrase.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.tape import Tape
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
ACT_LINE = "ACT      glance open ask"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"


def _genome_with(*lines: str) -> Path:
    p = Path(tempfile.mkdtemp()) / "seam.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _game_outcome_row(tape: Tape, step: int, act_name: str, reward: float) -> dict:
    """creature/senses/game.py's own publish, field for field (read 2026-09-21 21:3x on branch g5-world-ear)."""
    moment = f"gBaby{20260922:08d}s{step:09d}"
    common = {"game": "BabyAI-GoToLocal-v0", "episode": 0, "step": step}
    payload = json.dumps({"act": act_name, "expected": None, "got": reward, "residual": None, "source": "game"}).encode("utf-8")
    return tape.publish("outcome", payload,
                        {"moment": moment, "source": "game", "act": act_name, "expected": None,
                         "got": reward, "residual": None, "chosen_by": "schedule", "road": "no road",
                         "terminated": False, "truncated": False, **common}, "json")


def _journal_rows(root: Path) -> list:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


class TestGameRewardRowIsConsumedByOutcome(unittest.TestCase):
    def setUp(self) -> None:
        self.gpath = _genome_with(ACT_LINE, OUTCOME_LINE)
        self.root = Path(tempfile.mkdtemp())
        self.mind = Mind(self.gpath, self.root)
        self.tape = Tape(self.root)

    def test_l_shaped_row_reaches_k_ring_and_journal(self) -> None:
        # a game act outside K's vocabulary, three times with a constant reward: the residual must floor at 0.0
        # from the second occurrence (K's running-mean prediction), the ring must hold three reflex episodes, and
        # the journal must carry three "outcome" rows — the extra L keys never disturb the read.
        h0 = self.mind.org.state_hash()
        for step in range(3):
            row = _game_outcome_row(self.tape, step, "forward", 0.0)
            self.mind.consume(row)
        self.assertEqual(self.mind.outcome_episodes.n_written, 3)
        journal = [r for r in _journal_rows(self.root) if "outcome" in r]
        self.assertEqual(len(journal), 3)
        res = [r["outcome"] for r in journal]
        self.assertEqual(res[1].get("residual"), 0.0)
        self.assertEqual(res[2].get("residual"), 0.0)
        self.assertFalse(res[0].get("in_vocab", False), f"a game act is outside ACT's vocabulary: {res[0]}")
        self.assertEqual(self.mind.org.state_hash(), h0, "an outcome row never reaches the Organism")

    def test_reward_change_is_a_surprise(self) -> None:
        # the same act, reward 0 twice then 1: the third residual must be > 0 (the prediction was 0)
        for step, reward in enumerate([0.0, 0.0, 1.0]):
            self.mind.consume(_game_outcome_row(self.tape, step, "forward", reward))
        journal = [r["outcome"] for r in _journal_rows(self.root) if "outcome" in r]
        self.assertGreater(journal[2].get("residual"), 0.0)

    def test_without_outcome_declared_the_row_is_ignored(self) -> None:
        # the negative control: a genome without OUTCOME — the row is a fact on the tape with no consumer
        gpath = _genome_with(ACT_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        mind.consume(_game_outcome_row(tape, 0, "forward", 0.0))
        self.assertIsNone(mind.outcome_episodes)
        self.assertEqual([r for r in _journal_rows(root) if "outcome" in r], [])


if __name__ == "__main__":
    unittest.main()
