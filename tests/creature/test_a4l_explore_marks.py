# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:57 +0400 — docs/A4-LADDER-PREREG.md §2.5 PHASE 2: the
# rung's two reader marks, test-first against the LANDED row shapes (the game eye rows of creature/senses/game.py, the journal
# `act` rows of creature/mind.py:_maybe_choose_act, the game `outcome` rows with terminated/truncated/got): X1 THE LOCK
# ABSENT and X2 SUCCESS PER EPISODE (its bar computed against the toy's state-blind ceiling before any life, #228 (b)).
# Each reads «not gradable» where the ACT value line is undeclared (L-1) — the hour-1 fixture is that control.
from __future__ import annotations

import datetime as dt
import json
import math
import unittest
from pathlib import Path
from typing import List, Sequence, Tuple

from tools.verdict_life import explore_lock_mark, explore_success_mark

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "a4l-explore" / "hour1-game-rows.json"
NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
T0 = dt.datetime(2026, 9, 23, 0, 58, 18, 639000, tzinfo=dt.timezone.utc)


def _at(s: float) -> str:
    return (T0 + dt.timedelta(seconds=s)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _choices(acts: Sequence[str], start_s: float = 0.0, step_s: float = 30.0) -> Tuple[List[dict], List[dict]]:
    """Tape: a first row at T0, then one game eye row per choice every `step_s`; journal: one `act` row per eye row."""
    tape = [{"seq": 1, "at": _at(0.0), "sense": "ear", "meta": {"source": "maker", "word": "bar"}}]
    journal = []
    seq = 2
    for i, a in enumerate(acts):
        tape.append({"seq": seq, "at": _at(start_s + i * step_s), "sense": "eye",
                     "meta": {"source": "game", "n_actions": 7, "act_names": NAMES}})
        journal.append({"seq": seq, "act": {"game": "babyai-gotolocal", "act": a, "act_idx": NAMES.index(a), "seq": seq,
                                            "policy": "reward-valued", "weights": [0.0] * 7}})
        seq += 1
    return tape, journal


def _episodes(ends: Sequence[Tuple[float, bool]]) -> List[dict]:
    """Tape rows: a first row at T0, then for each (end second, success) a non-terminal outcome 30 s before and the
    episode's terminal outcome (terminated + reward on success, truncated otherwise)."""
    rows = [{"seq": 1, "at": _at(0.0), "sense": "ear", "meta": {"source": "maker", "word": "bar"}}]
    seq = 2
    for ep, (end_s, ok) in enumerate(ends):
        rows.append({"seq": seq, "at": _at(end_s - 30), "sense": "outcome",
                     "meta": {"source": "game", "act": "left", "got": 0.0, "terminated": False, "truncated": False, "episode": ep}})
        seq += 1
        rows.append({"seq": seq, "at": _at(end_s), "sense": "outcome",
                     "meta": {"source": "game", "act": "forward", "got": 0.6 if ok else 0.0, "terminated": ok,
                              "truncated": not ok, "episode": ep}})
        seq += 1
    return rows


def _binom_k(n: int, p0: float, alpha: float = 0.05) -> int:
    for k in range(n + 1):
        if sum(math.comb(n, j) * p0 ** j * (1 - p0) ** (n - j) for j in range(k, n + 1)) <= alpha:
            return k
    return n + 1


class TestX1TheLockAbsent(unittest.TestCase):
    def test_a_planted_96_percent_lock_fails(self) -> None:
        acts = [NAMES[i % 7] for i in range(120)] + (["left"] * 96 + ["right", "forward", "done", "pickup"]) * 3
        tape, journal = _choices(acts)
        m = explore_lock_mark(tape, journal, True)
        self.assertTrue(m["graded"])
        self.assertFalse(m["pass"])
        self.assertEqual(m["max_act"], "left")
        self.assertGreaterEqual(m["max_share"], 0.96)

    def test_a_uniform_journal_passes(self) -> None:
        tape, journal = _choices([NAMES[i % 7] for i in range(600)])
        m = explore_lock_mark(tape, journal, True)
        self.assertTrue(m["graded"])
        self.assertTrue(m["pass"])
        self.assertLess(m["max_share"], 0.2)

    def test_hour_one_is_excluded(self) -> None:
        """A lock INSIDE the first hour (120 choices at 30 s) is not graded; the same lock after it is."""
        tape, journal = _choices(["left"] * 110 + [NAMES[i % 7] for i in range(300)])
        self.assertTrue(explore_lock_mark(tape, journal, True)["pass"])
        tape2, journal2 = _choices([NAMES[i % 7] for i in range(130)] + ["left"] * 110 + [NAMES[i % 7] for i in range(200)])
        self.assertFalse(explore_lock_mark(tape2, journal2, True)["pass"])

    def test_the_bar_is_strict_at_half(self) -> None:
        body = (["left"] * 50 + ["right"] * 50) * 4
        tape, journal = _choices([NAMES[i % 7] for i in range(120)] + body)
        m = explore_lock_mark(tape, journal, True)
        self.assertFalse(m["pass"], "an act at exactly 50 % of a window is ≥ 50 %: the lock clause fires")

    def test_not_gradable_undeclared_or_too_few(self) -> None:
        tape, journal = _choices([NAMES[i % 7] for i in range(600)])
        m = explore_lock_mark(tape, journal, False)
        self.assertFalse(m["graded"])
        self.assertIsNone(m["pass"])
        self.assertTrue(m["reason"].startswith("not gradable"))
        tape, journal = _choices([NAMES[i % 7] for i in range(190)])
        m = explore_lock_mark(tape, journal, True)
        self.assertFalse(m["graded"])
        self.assertIn("100", m["reason"])

    def test_the_hour_one_fixture_is_not_gradable(self) -> None:
        """The L-1 control: alpha4-1's first hour (its game rows + the 121 act rows a replay wrote) — the line is
        undeclared there, and no choice falls after hour 1 in any case."""
        doc = json.loads(FIXTURE.read_text())
        first = {"seq": 1, "at": "2026-09-23T00:58:18.639Z", "sense": "ear", "meta": {"source": "maker"}}
        tape = [first] + [dict(r, at=_at(0)) for r in doc["tape_game_rows"]]
        for declared in (False, True):
            m = explore_lock_mark(tape, doc["journal_act_rows"], declared)
            self.assertFalse(m["graded"], m)


class TestX2SuccessPerEpisode(unittest.TestCase):
    def test_an_eight_hour_life_is_not_gradable_by_its_ceiling(self) -> None:
        ends = [(7200 + 1600 * i, i % 3 == 0) for i in range(13)]            # 13 episodes in hours 2–8, 5 successes
        m = explore_success_mark(_episodes(ends), True)
        self.assertEqual(m["episodes"], 13)
        self.assertEqual(m["successes"], 5)
        self.assertEqual(m["bound_k"], _binom_k(13, 0.29))
        self.assertGreater(m["bound_rate"], m["ceiling"])
        self.assertFalse(m["graded"])
        self.assertIn("ceiling", m["reason"])

    def test_graded_where_the_bound_is_under_the_ceiling(self) -> None:
        k40 = _binom_k(40, 0.29)
        self.assertLessEqual(k40 / 40, 0.488)
        span = (28800 - 7200) / 41
        for succ, want in ((k40, True), (k40 - 1, False)):
            with self.subTest(successes=succ):
                ends = [(7200 + span * (i + 1), i < succ) for i in range(40)]
                m = explore_success_mark(_episodes(ends), True)
                self.assertTrue(m["graded"], m)
                self.assertEqual(m["episodes"], 40)
                self.assertEqual(m["successes"], succ)
                self.assertEqual(m["pass"], want)

    def test_the_window_is_hours_two_to_eight(self) -> None:
        ends = [(3600, True), (7100, True), (7300, False), (28700, True), (29000, True)]
        m = explore_success_mark(_episodes(ends), True)
        self.assertEqual(m["episodes"], 2)
        self.assertEqual(m["successes"], 1)

    def test_not_gradable_undeclared(self) -> None:
        ends = [(7200 + 500 * i, True) for i in range(40)]
        m = explore_success_mark(_episodes(ends), False)
        self.assertFalse(m["graded"])
        self.assertIsNone(m["pass"])
        self.assertTrue(m["reason"].startswith("not gradable"))

    def test_the_hour_one_fixture_is_not_gradable(self) -> None:
        doc = json.loads(FIXTURE.read_text())
        first = {"seq": 1, "at": "2026-09-23T00:58:18.639Z", "sense": "ear", "meta": {"source": "maker"}}
        tape = [first] + [dict(r, at=_at(60)) for r in doc["tape_game_rows"]]
        for declared in (False, True):
            self.assertFalse(explore_success_mark(tape, declared)["graded"])


if __name__ == "__main__":
    unittest.main()
