# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:55 +0400 — docs/A4-LADDER-PREREG.md §2.5 PHASE 2: the
# mind's game act chooser reading the declared VALUE law (`ACT value reward <n>; optimism <f>`) — the act's value = its mean
# REWARD over its last <n> outcomes, <f> for an act with no outcome in its window; the 10 % uniform draw and the two draws of
# the act rng unchanged. Undeclared → the old outcome-weighted law, byte-identical (the landing's negative control replays
# the hour-1 fixture; here the journal's own policy string and weights). Pinned against the toy's candidate arm (v)
# (tools/toys/act_chooser_toy.py `reward_values`), so the rung's life runs exactly the law the toy measured.
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

from creature.body import Body
from creature.mind import Mind
from creature.tape import Tape
from tools.toys import act_chooser_toy as toy

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
ACT_LINE = "ACT      glance open ask turn step say run"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"
VALUE_LINE = "ACT      value reward 10; optimism 1"
REWARDS: Dict[int, float] = {9: 0.38125, 30: 0.859375, 58: 0.5, 91: 0.2, 120: 0.1}


def _genome(*lines: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(G4_GENOME_PATH.read_text() + "\n" + "\n".join(lines) + "\n")
    return p


def _jsonl(d: Path) -> List[dict]:
    out: List[dict] = []
    for f in sorted(Path(d).glob("*.jsonl")):
        out.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
    return out


def _png(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def life_order_run(gpath: Path, frames: int = 140, rewards: Dict[int, float] = REWARDS) -> Tuple[Path, Mind]:
    """A real Mind in the LIFE's row order (creature/senses/game.py): frame t's ear+eye — the mind chooses a_{t+1} on
    the eye row — THEN frame t's outcome row (the act a_t that produced frame t, obeyed as the worker obeys, its reward
    planted at the steps in `rewards`)."""
    root = Path(tempfile.mkdtemp())
    mind = Mind(gpath, root)
    tape = Tape(root)
    rng = np.random.default_rng(11)
    act_path = root / "game" / "ACT"

    def frame(step: int):
        moment = f"gfake0000000s{step:09d}"
        common = {"game": "babyai-gotolocal", "episode": 0, "step": step}
        mind.consume(tape.publish("ear", b"ball", {"moment": moment, "source": "game", "word": "ball",
                                                    "mission": "go to the red ball", **common}, "txt"))
        mind.consume(tape.publish("eye", _png(rng.integers(0, 255, (128, 128, 3), dtype=np.uint8)),
                                  {"moment": moment, "source": "game", "n_actions": 7, "act_names": toy.ACT_NAMES,
                                   **common}, "png"))
        data = json.loads(act_path.read_text())
        return int(data["act"]), int(data["seq"]), moment, common

    pending = frame(0)[:2]
    for t in range(1, frames + 1):
        act_idx, act_seq = pending
        nxt_idx, nxt_seq, moment, common = frame(t)
        got = rewards.get(t, 0.0)
        name = toy.ACT_NAMES[act_idx]
        payload = json.dumps({"act": name, "expected": None, "got": got, "residual": None, "source": "game"}).encode()
        mind.consume(tape.publish("outcome", payload,
                                  {"moment": moment, "source": "game", "act": name, "act_idx": act_idx, "expected": None,
                                   "got": got, "residual": None, "chosen_by": "mind", "road": "mind", "act_seq": act_seq,
                                   "terminated": False, "truncated": False, **common}, "json"))
        pending = (nxt_idx, nxt_seq)
    return root, mind


class TestTheRewardLaw(unittest.TestCase):
    def test_journal_carries_the_declared_policy_and_the_toys_values(self) -> None:
        root, mind = life_order_run(_genome(ACT_LINE, OUTCOME_LINE, VALUE_LINE))
        acts = [r["act"] for r in _jsonl(root / "journal") if isinstance(r.get("act"), dict)]
        self.assertEqual(len(acts), 141)
        self.assertEqual({a["policy"] for a in acts}, {"reward-valued"})
        self.assertEqual(acts[0]["weights"], [1.0] * 7, "every act untried → the optimism prior")
        self.assertEqual(mind.act_mismatches, 0)
        rows = toy.replay_choices(_jsonl(root / "tape"), _jsonl(root / "journal"), int(mind.genome.seed),
                                  law="reward", window=10, optimism=1.0)
        self.assertEqual(len(rows), 141)
        bad = [r["seq"] for r in rows if not (r["weights_match"] and r["act_match"])]
        self.assertEqual(bad, [], f"rows the toy's candidate does not reproduce: {bad[:5]}")
        rewarded = [r for r in rows if any(0.0 < w < 1.0 for w in r["weights"])]
        self.assertGreater(len(rewarded), 5, "the planted rewards must reach the values")

    def test_the_explore_counter_moves_on_both_laws(self) -> None:
        for lines in ((ACT_LINE, OUTCOME_LINE, VALUE_LINE), (ACT_LINE, OUTCOME_LINE)):
            with self.subTest(law="reward" if VALUE_LINE in lines else "old"):
                root, mind = life_order_run(_genome(*lines), frames=80)
                law = "reward" if VALUE_LINE in lines else "old"
                rows = toy.replay_choices(_jsonl(root / "tape"), _jsonl(root / "journal"), int(mind.genome.seed), law=law)
                self.assertEqual(mind.act_explored, sum(1 for r in rows if r["explored"]))
                self.assertGreater(mind.act_explored, 0)

    def test_undeclared_keeps_the_old_policy_string_and_weights(self) -> None:
        root, mind = life_order_run(_genome(ACT_LINE, OUTCOME_LINE), frames=80)
        acts = [r["act"] for r in _jsonl(root / "journal") if isinstance(r.get("act"), dict)]
        self.assertEqual({a["policy"] for a in acts}, {"outcome-weighted"})
        rows = toy.replay_choices(_jsonl(root / "tape"), _jsonl(root / "journal"), int(mind.genome.seed), law="old")
        self.assertTrue(all(r["weights_match"] and r["act_match"] for r in rows))


class TestStatusOnEveryWrite(unittest.TestCase):
    def test_keys_present_before_and_after_choices(self) -> None:
        for lines, law in (((ACT_LINE, OUTCOME_LINE, VALUE_LINE), "reward-valued"), ((ACT_LINE, OUTCOME_LINE), "outcome-weighted"),
                           ((), None)):
            with self.subTest(law=law):
                gpath = _genome(*lines)
                root = Path(tempfile.mkdtemp())
                self.addCleanup(shutil.rmtree, root, True)
                body = Body(root, gpath)
                body.mind = Mind(gpath, root)   # a bare, unthreaded Mind — _build_status() only reads its fields (test_gene_values' own pattern)
                st = body._build_status()
                self.assertIn("act_policy", st)
                self.assertIn("act_weights", st)
                self.assertEqual(st["act_explored"], 0)
                self.assertIsNone(st["act_policy"])
                self.assertIsNone(st["act_weights"])
                if law is None:
                    continue
                root2, mind = life_order_run(gpath, frames=40)
                self.addCleanup(shutil.rmtree, root2, True)
                body.mind = mind
                st = body._build_status()
                self.assertEqual(st["act_policy"], law)
                self.assertEqual(len(st["act_weights"]), 7)
                self.assertEqual(st["act_explored"], mind.act_explored)


class TestReplayUnderTheLaw(unittest.TestCase):
    """X3 in miniature and the tape twin's shape: a reward-law tape replays identical under its own genome (acts
    re-derived, act_mismatch never True); the FLOOR's law replayed on the same tape chooses otherwise — the act rows
    differ from the first (the policy string), act_mismatch turns True where a choice first differs — and the
    organism is untouched by the chooser: `hash` equal on every row."""

    def test_self_replay_identical_and_the_old_law_twin(self) -> None:
        from creature import replay as replay_module
        gpath = _genome(ACT_LINE, OUTCOME_LINE, VALUE_LINE)
        root, _mind = life_order_run(gpath, frames=90)
        day = sorted((root / "tape").glob("*.jsonl"))[0]
        j1 = replay_module.run_replay(gpath, day, Path(tempfile.mkdtemp()))
        j2 = replay_module.run_replay(gpath, day, Path(tempfile.mkdtemp()))
        self.assertEqual(j1.read_bytes(), j2.read_bytes())
        live = replay_module.read_mind_journal(sorted((root / "journal").glob("*.jsonl"))[0])
        self.assertIsNone(replay_module.compare(replay_module.read_mind_journal(j1), live))
        rows1 = replay_module.read_mind_journal(j1)
        self.assertFalse(any(r["outcome"].get("act_mismatch") for r in rows1 if isinstance(r.get("outcome"), dict)))

        old_gpath = _genome(ACT_LINE, OUTCOME_LINE)
        j_old = replay_module.run_replay(old_gpath, day, Path(tempfile.mkdtemp()))
        rows_old = replay_module.read_mind_journal(j_old)
        self.assertEqual(len(rows_old), len(rows1))
        differing_fields = set()
        for a, b in zip(rows1, rows_old):
            self.assertEqual(a["seq"], b["seq"])
            if "hash" in a or "hash" in b:
                self.assertEqual(a.get("hash"), b.get("hash"), f"seq {a['seq']}: the chooser must not touch the organism")
            for key in set(a) | set(b):
                if a.get(key) != b.get(key):
                    if key == "act":
                        differing_fields |= {f"act.{k}" for k in set(a["act"]) | set(b["act"]) if a["act"].get(k) != b["act"].get(k)}
                    elif key == "outcome":
                        differing_fields |= {f"outcome.{k}" for k in set(a["outcome"]) | set(b["outcome"]) if a["outcome"].get(k) != b["outcome"].get(k)}
                    else:
                        differing_fields.add(key)
        self.assertTrue(differing_fields <= {"act.policy", "act.weights", "act.act", "act.act_idx", "outcome.act_mismatch"},
                        differing_fields)
        self.assertIn("act.policy", differing_fields)
        self.assertIn("outcome.act_mismatch", differing_fields)


if __name__ == "__main__":
    unittest.main()
