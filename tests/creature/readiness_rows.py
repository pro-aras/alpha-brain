# edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:45 +0400 — ALPHA4-PREREG §4 AMENDED (branch judge-units-0923): the
# READINESS judge's test rows in the LANDED shapes, shared by tests/creature/test_readiness_units.py and
# tests/creature/test_readiness_judge.py so the two can never drift apart (#173/#238: a mark whose fixtures predate the shape
# passes for the wrong reason — builder I's per-act outcome rows made every «condition removed» test block on (a) alone once
# (a) became per-episode). Not a test module (no `test_` prefix): unittest discovery never collects it.
#
# The shapes, read off the alpha4-1 hour-1 fixture's tape (/data/dev/a4-ladder/fixtures/alpha4-1-hour1/tape/2026-09-23.jsonl,
# 2026-09-23 11:3x +0400) and the code that writes them:
#   game outcome (creature/senses/game.py): meta = moment/source/act/act_idx/expected/got/residual/chosen_by/road/act_seq/
#     terminated/truncated/game/episode/step. The worker (tools/game_worker_babyai.py:main) writes ONE reset frame at startup
#     (step 0: an eye row, no outcome); after a terminal step it resets WITHOUT a frame, so the next episode's first act takes
#     the next step index (the fixture: episode 0 = steps 1..64, truncated). The terminal row carries the finishing episode's
#     number. BabyAI pays reward only on a successful terminal step: 1 - 0.9 * steps / max_steps; a failure is truncated at
#     64 steps with 0.0 on every row.
#   sit (creature/senses/sit.py): meta = moment/source/exam_file/score/composite/read_share.
#   grade / hold (creature/senses/grade.py): meta = moment/source/id/right/novel; moment/source/active.
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]    # the worker's own 7, verbatim order

# The judge's test genome: builder I's own lines (G4-skeleton + these), unchanged.
EXTRA_LINES = [
    "FAST     episodes 2000 keys sight words surprise",
    "ACT      turn step",
    "OUTCOME  act to episode; error grades it; ranks replay",
    "SIT      exam every 500 canvases; the score returns as a sense",
    "STAGE    3 nursery moments 200..",
    "STAGE    4 world by READY",
    "DOOR     web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD",
    "SENSE    grade from ask/graded",
]


class Clock:
    """seq (strictly increasing, like the tape), the game's GLOBAL step index and the worker's episode number."""

    def __init__(self) -> None:
        self.seq = 0
        self.step = 0
        self.episode = 0

    def next_seq(self) -> int:
        self.seq += 1
        return self.seq


def at(seq: int) -> str:
    return f"2026-09-23T01:{(seq // 60) % 60:02d}:{seq % 60:02d}.{seq % 1000:03d}Z"


def game_outcome(clk: Clock, act_idx: int, got: float, terminated: bool, truncated: bool,
                 chosen_by: str = "mind") -> Dict[str, object]:
    seq = clk.next_seq()
    clk.step += 1
    return {"seq": seq, "at": at(seq), "sense": "outcome", "sha": "0" * 64, "payload": f"payload/{seq:09d}.json",
            "meta": {"moment": f"gbaby20260923s{clk.step:09d}", "source": "game", "act": ACT_NAMES[act_idx],
                     "act_idx": act_idx, "expected": None, "got": got, "residual": None, "chosen_by": chosen_by,
                     "road": "mind" if chosen_by == "mind" else "no road", "act_seq": seq - 1,
                     "terminated": terminated, "truncated": truncated, "game": "babyai-gotolocal",
                     "episode": clk.episode, "step": clk.step}}


def episode(clk: Clock, success: bool, success_len: int = 10, max_steps: int = 64, chosen_by: str = "mind",
            finish: bool = True, steps: Optional[int] = None) -> List[Dict[str, object]]:
    """One GoToLocal episode as its outcome rows. `finish=False` stops after `steps` rows with no terminal row (an episode
    still in progress)."""
    n = steps if steps is not None else (success_len if success else max_steps)
    rows = []
    for i in range(1, n + 1):
        last = finish and i == n
        got = round(1.0 - 0.9 * (n / max_steps), 4) if (success and last) else 0.0
        rows.append(game_outcome(clk, act_idx=2 if success else 0, got=got,
                                 terminated=bool(success and last), truncated=bool((not success) and last),
                                 chosen_by=chosen_by))
    if finish:
        clk.episode += 1
    return rows


def episodes(clk: Clock, pattern: str, **kw) -> List[Dict[str, object]]:
    """'S' = a successful episode, 'F' = a failed one, in order."""
    rows: List[Dict[str, object]] = []
    for ch in pattern:
        rows.extend(episode(clk, success=(ch == "S"), **kw))
    return rows


def sit(clk: Clock, score: Optional[float], composite: Optional[float], read_share: Optional[float]) -> Dict[str, object]:
    seq = clk.next_seq()
    stem = f"2026-09-23T01{seq:04d}Z"
    return {"seq": seq, "at": at(seq), "sense": "sit", "sha": "0" * 64, "payload": f"payload/{seq:09d}.json",
            "meta": {"moment": f"sit{stem}", "source": "sit", "exam_file": f"{stem}.json", "score": score,
                     "composite": composite, "read_share": read_share}}


def grade(clk: Clock, gid: str, right: bool, novel: bool) -> Dict[str, object]:
    seq = clk.next_seq()
    return {"seq": seq, "at": at(seq), "sense": "grade", "sha": "0" * 64, "payload": f"payload/{seq:09d}.json",
            "meta": {"moment": f"grade{gid}", "source": "grade", "id": gid, "right": right, "novel": novel}}


def hold(clk: Clock, active: bool) -> Dict[str, object]:
    seq = clk.next_seq()
    return {"seq": seq, "at": at(seq), "sense": "hold", "sha": "0" * 64, "payload": f"payload/{seq:09d}.json",
            "meta": {"moment": f"hold{seq:06d}", "source": "grade", "active": active}}


def grades_passing(clk: Clock) -> List[Dict[str, object]]:
    """(d) met exactly: 20 graded answers, 18 right (0.9); the last 10 flagged novel, 8 of them right."""
    rows = [grade(clk, f"g{i}", True, False) for i in range(10)]
    rows += [grade(clk, f"n{i}", i < 8, True) for i in range(10)]
    return rows


def write_pairs(mind, pairs: List[tuple]) -> None:
    """Real `Episodes.write()` calls into the mind's own FAST ring (the counts SENTENCE's find_frames() reads), one two-word
    instant per episode, in the order given — a ring smaller than the total EVICTS the oldest (a frame's evidence leaves)."""
    dim_s, dim_w = mind.genome.sight_dim(), mind.genome.words_dim()
    m = 0
    for w1, w2, n in pairs:
        for _ in range(n):
            mind.episodes.write(moment=m, x_s=np.zeros(dim_s), x_w=np.zeros(dim_w), word=w2, surprise=0.0,
                                words_in_instant=[w1, w2])
            m += 1


def ok(readings: Dict[str, object], k: str):
    """A clause's verdict from either row shape: the amended block's own "ok", or the unamended judge's bare boolean — so a
    RED run on the unamended tree fails on the defect's READING, not on a KeyError."""
    v = readings[k]
    return v.get("ok") if isinstance(v, dict) else v


def per_act_mean_last_200(rows: List[Dict[str, object]]) -> float:
    """The arithmetic the UNAMENDED clause (a) computed, on the same history — a documented fact about the history, never a
    twin judge: the mean per-STEP reward over the last 200 mind-chosen game acts."""
    gots = [float(r["meta"]["got"]) for r in rows
            if r["sense"] == "outcome" and r["meta"].get("source") == "game" and r["meta"].get("chosen_by") == "mind"]
    last = gots[-200:]
    return sum(last) / len(last)


def journal(root: Path) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for f in sorted((Path(root) / "journal").glob("*.jsonl")):
        out.extend(json.loads(line) for line in f.read_text().splitlines() if line.strip())
    return out
