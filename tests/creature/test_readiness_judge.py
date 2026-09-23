# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:20 +0400 — ALPHA4-PREREG.md §4: THE READINESS
# JUDGE. Tests drive `Mind.consume()` directly against hand-built rows (the same technique
# tests/creature/test_g5k_outcome.py's snapshot/resume tests use) rather than the full Body/SenseThread
# machinery — this file's job is the JUDGE's OWN commit/persistence/replay mechanism, not to
# re-prove SENTENCE's frame-filing (builder C's own precision toy already does that) or OUTCOME/SIT's own
# reflex-episode mechanism (G5-K's own tests already do that).
#
# edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:48 +0400 — REWRITTEN under ALPHA4-PREREG §4 AMENDED (branch
# judge-units-0923, §11 finding 1). What changed and why:
#  - the rows are the LANDED shapes (tests/creature/readiness_rows.py): (a) reads COMPLETED EPISODES now, and builder I's
#    per-act outcome rows (`got` 0.5 on 200 bare acts, no terminated/truncated/episode) complete none — under the amended
#    judge every «condition removed alone» test below would have blocked on (a) ALONE and passed for the wrong reason
#    (#238: a mark whose fixtures predate the shape). So every removal test now asserts that its OWN clause is the ONLY
#    one reading False on the last reading, beside the door staying shut;
#  - the door opens on ONE reading whose five clauses all hold (the streak defined once), so the passing case commits at
#    the second sitting — the first at which (c) and (b)'s read half have their two sittings — and `_stage_ready_streak`
#    is gone;
#  - (b)'s read half is fed as it lives, a `read_share` on each SIT row; the test-only `_read_proxy_override` is gone;
#  - (b)'s frame half reads the frames ALIVE in the FAST ring (find_frames over `mind.episodes`), never the filed set;
#  - the stage event's readings are five BLOCKS, each verdict read by its own "ok" key — builder I's
#    `assertTrue(all(readings.values()))` would pass VACUOUSLY on non-empty dicts (#238's SURPRISE mark).
from __future__ import annotations

import itertools
import json
import tempfile
import unittest
from pathlib import Path
from typing import Callable, Dict, List, Optional

from creature.mind import Mind
from tests.creature import readiness_rows as rr

ROOT = Path(__file__).resolve().parents[2]
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()

EXTRA_LINES = rr.EXTRA_LINES
FRAME_PAIRS = [("red", "ball"), ("blue", "key"), ("green", "box")]
PASSING_EPISODES = "SSFSSFSSFSSFSSFSSFFF"       # 12 successes in the last 20 completed episodes (the bound is 10)


def _genome_path(tmp_root: Path, extra: List[str] = EXTRA_LINES) -> Path:
    p = tmp_root / "test.genome"
    p.write_text(SKELETON_TEXT + "\n" + "\n".join(extra) + "\n")
    return p


def _new_mind(tmp_root: Path, extra: List[str] = EXTRA_LINES) -> Mind:
    root = tmp_root / "run"
    root.mkdir(parents=True, exist_ok=True)
    return Mind(_genome_path(tmp_root, extra), root)


def _seed_frames(mind: Mind, pairs=FRAME_PAIRS, n_each: int = 10) -> None:
    """§4(b)'s frame half: real `Episodes.write()` calls into the mind's own FAST ring (a heavily skewed corpus: exactly
    `len(pairs)` rows from the real `find_frames()`, each lift 4.2 with the noise below) — the counts the judge reads. THINK's
    own filing is not needed: the amended judge counts the frames ALIVE in the ring, never the filed set."""
    rr.write_pairs(mind, [(w1, w2, n_each) for w1, w2 in pairs])
    rr.write_pairs(mind, [(a, b, 1) for a, b in itertools.permutations(["aa", "bb", "cc", "dd"], 2)])   # noise: count 1, never min_count


def _feed(mind: Mind, rows: List[Dict[str, object]]) -> None:
    for r in rows:
        mind.consume(r)


def _base_setup(mind: Mind, clk: rr.Clock, episodes: str = PASSING_EPISODES, frames=FRAME_PAIRS,
                grades: Optional[Callable[[rr.Clock], List[Dict[str, object]]]] = None) -> None:
    """Every clause satisfied EXCEPT what the test's own two real `sit` rows bring ((c) and (b)'s read half each read the
    last two sittings) — the common setup every «one condition removed» test starts from, so each test's OWN deviation is
    the only difference from the passing case."""
    _seed_frames(mind, pairs=frames)
    _feed(mind, rr.episodes(clk, episodes))
    _feed(mind, (grades or rr.grades_passing)(clk))      # built AFTER the episodes: seqs stay strictly increasing, as on a tape


def _journal(tmp: Path) -> List[Dict[str, object]]:
    return rr.journal(tmp / "run")


def _last_reading(tmp: Path) -> Dict[str, object]:
    return [r for r in _journal(tmp) if "readiness" in r][-1]["readiness"]


def _false_clauses(reading: Dict[str, object]) -> set:
    return {k for k in "abcde" if reading[k]["ok"] is not True}


class TestAllFiveHoldReachesStage4(unittest.TestCase):
    def test_all_five_hold_on_one_reading_opens_the_door(self) -> None:
        """The positive control of every removal test below: the base setup and two good sittings open the door — at the
        SECOND sitting, the first reading whose five clauses all hold (§4 AMENDED: one reading, never two in a row)."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)

        mind.consume(rr.sit(clk, 0.99, 0.97, 0.7))       # sitting 1: (c) and (b)-read have one reading — not yet
        self.assertEqual(_false_clauses(_last_reading(tmp)), {"b", "c"})
        self.assertNotEqual(mind.stage, 4, "must not commit before (c) has its two sittings")
        mind.consume(rr.sit(clk, 0.99, 0.97, 0.7))       # sitting 2: all five hold on this ONE reading -> COMMIT
        self.assertEqual(mind.stage, 4, "must commit on the first reading whose five clauses all hold")

        stage_events = [r for r in _journal(tmp) if r.get("event") == "stage"]
        self.assertEqual(len(stage_events), 1, "exactly ONE stage event, never more")
        self.assertEqual(stage_events[0]["stage"], 4)
        readings = stage_events[0]["readings"]
        self.assertEqual(set(readings), {"a", "b", "c", "d", "e"})
        self.assertTrue(all(readings[k]["ok"] is True for k in "abcde"), readings)   # by key — a dict is always truthy
        self.assertEqual((readings["a"]["n"], readings["a"]["successes"], readings["b"]["frames_alive"]), (20, 12, 3))

    def test_never_undone_once_committed(self) -> None:
        """§4's own law: "never undone by the mind" — a LATER window that would fail must not revert it."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        _feed(mind, [rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)])
        self.assertEqual(mind.stage, 4)
        mind.consume(rr.hold(clk, True))                   # everything now fails (e)
        mind.consume(rr.sit(clk, 0.10, 0.10, 0.10))         # (c) and (b) also fail now
        self.assertEqual(mind.stage, 4, "stage 4, once committed, must never be undone by a later bad window")

    def test_sittings_without_a_read_share_block_honestly(self) -> None:
        """(b)'s read half fails CLOSED: two sittings that carry no read_share (fewer than 50 heard words, or an older
        sitter) leave the door shut even with every other clause perfect — and the row says why."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        _feed(mind, [rr.sit(clk, 0.99, 0.97, None), rr.sit(clk, 0.99, 0.97, None)])
        self.assertNotEqual(mind.stage, 4)
        reading = _last_reading(tmp)
        self.assertEqual(_false_clauses(reading), {"b"})
        self.assertEqual((reading["b"]["frames_ok"], reading["b"]["read_ok"], reading["b"]["read_share_last2"]),
                         (True, False, [None, None]))


class TestEachConditionRemovedAlone(unittest.TestCase):
    """Each test differs from the passing case (TestAllFiveHoldReachesStage4's first test, the positive control) by ONE
    condition, and asserts that condition's clause is the ONLY one reading False — never a pass on another clause's failure."""

    def _run_to_stage(self, mind: Mind, clk: rr.Clock, first=(0.99, 0.97, 0.7), second=(0.99, 0.97, 0.7)) -> None:
        mind.consume(rr.sit(clk, *first))
        mind.consume(rr.sit(clk, *second))

    def _assert_only(self, tmp: Path, mind: Mind, clause: str) -> None:
        self.assertNotEqual(mind.stage, 4)
        self.assertEqual(_false_clauses(_last_reading(tmp)), {clause})

    def test_a_removed_nine_of_twenty_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk, episodes="S" * 9 + "F" * 11)    # one under the bound (P(X >= 9 | 0.29) = 0.095)
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "a")
        self.assertEqual(_last_reading(tmp)["a"]["successes"], 9)

    def test_a_removed_window_not_full_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk, episodes="S" * 19)              # 19 completed, every one a success: the window is not full
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "a")
        self.assertEqual(_last_reading(tmp)["a"]["n"], 19)

    def test_b_removed_too_few_frames_alive_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk, frames=FRAME_PAIRS[:2])         # only 2 frames alive, need >= 3
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "b")
        self.assertEqual((_last_reading(tmp)["b"]["frames_alive"], _last_reading(tmp)["b"]["frames_ok"]), (2, False))

    def test_b_removed_one_sitting_reads_under_the_share_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        self._run_to_stage(mind, clk, first=(0.99, 0.97, 0.5))  # the first of the two sittings reads 0.5 < 0.6
        self._assert_only(tmp, mind, "b")
        self.assertEqual(_last_reading(tmp)["b"]["read_share_last2"], [0.5, 0.7])

    def test_c_removed_low_composite_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        self._run_to_stage(mind, clk, first=(0.99, 0.80, 0.7), second=(0.99, 0.80, 0.7))   # composite under 0.95
        self._assert_only(tmp, mind, "c")

    def test_c_removed_low_q1_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        self._run_to_stage(mind, clk, first=(0.90, 0.97, 0.7), second=(0.90, 0.97, 0.7))   # Q1 (score) under 0.98
        self._assert_only(tmp, mind, "c")

    def test_d_removed_too_few_grades_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        grades = lambda c: [rr.grade(c, f"g{i}", True, i >= 5) for i in range(15)]     # 15 < 20 (10 novel, all right)
        _base_setup(mind, clk, grades=grades)
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "d")

    def test_d_removed_novel_window_not_yet_full_blocks_even_when_all_seen_are_right(self) -> None:
        """Regression (advisor-caught, builder I): PREREG §4(d)/§8 point 7 both name TEN as the novel denominator
        ("8 of the last 10"; "ten of them never-seen pictures") — 8 novel grades, all right, must NOT satisfy (d) before
        the last-10 window has ever filled. 20 graded, all right: only the novel window is short."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        grades = lambda c: [rr.grade(c, f"g{i}", True, False) for i in range(12)] + [rr.grade(c, f"n{i}", True, True) for i in range(8)]
        _base_setup(mind, clk, grades=grades)
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "d")
        self.assertEqual((_last_reading(tmp)["d"]["answered"], _last_reading(tmp)["d"]["novel_window_n"]), (20, 8))

    def test_d_removed_too_few_novel_right_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        grades = lambda c: ([rr.grade(c, f"g{i}", True, False) for i in range(15)]
                            + [rr.grade(c, f"n{i}", i < 5, True) for i in range(10)])   # 5 of 10 novel right, need >= 8; 20/25 = 0.8 overall
        _base_setup(mind, clk, grades=grades)
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "d")
        self.assertEqual(_last_reading(tmp)["d"]["novel_right"], 5)

    def test_e_removed_hold_active_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        mind.consume(rr.hold(clk, True))
        self._run_to_stage(mind, clk)
        self._assert_only(tmp, mind, "e")


class TestGradeAndHoldConsumption(unittest.TestCase):
    def test_grade_rows_update_counters_and_journal(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        mind.consume(rr.grade(clk, "g0", True, False))
        mind.consume(rr.grade(clk, "g1", False, True))
        self.assertEqual(mind._grades_total, 2)
        self.assertEqual(mind._grades_right, 1)
        self.assertEqual(list(mind._novel_grades), [False])

    def test_hold_row_updates_the_flag(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        self.assertFalse(mind._hold_active)
        mind.consume(rr.hold(clk, True))
        self.assertTrue(mind._hold_active)
        mind.consume(rr.hold(clk, False))
        self.assertFalse(mind._hold_active)

    def test_grade_and_hold_rows_are_dead_weight_when_gene_undeclared(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        no_grade = [l for l in EXTRA_LINES if not l.strip().startswith("SENSE    grade")]
        mind = _new_mind(tmp, extra=no_grade)
        clk = rr.Clock()
        mind.consume(rr.grade(clk, "g0", True, True))
        mind.consume(rr.hold(clk, True))
        self.assertEqual(mind._grades_total, 0)
        self.assertFalse(mind._hold_active)

    def test_web_row_counters(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind.consume({"seq": 1, "at": "2026-09-23T00:00:00.000Z", "sense": "web",
                      "meta": {"status": "ok", "question_id": "0"}})
        mind.consume({"seq": 2, "at": "2026-09-23T00:00:01.000Z", "sense": "web",
                      "meta": {"status": "refused_rate", "question_id": "1"}})
        mind.consume({"seq": 3, "at": "2026-09-23T00:00:02.000Z", "sense": "web",
                      "meta": {"status": "refused_hold", "question_id": "2"}})
        mind.consume({"seq": 4, "at": "2026-09-23T00:00:03.000Z", "sense": "web",
                      "meta": {"status": "failed", "question_id": "3"}})
        self.assertEqual(mind.web_fetches, 2)      # ok + failed
        self.assertEqual(mind.web_refused_rate, 1)
        self.assertEqual(mind.web_refused_hold, 1)


class TestResumeKeepsStage(unittest.TestCase):
    def test_resume_mid_life_keeps_the_stage(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        _feed(mind, [rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)])
        self.assertEqual(mind.stage, 4)
        mind.snapshot()

        resumed, last_seq = Mind.resume(_genome_path(tmp), tmp / "run")
        self.assertEqual(resumed.stage, 4, "a resume mid-life must keep the committed stage")
        self.assertEqual(resumed._grades_total, mind._grades_total)
        self.assertEqual(resumed._grades_right, mind._grades_right)
        self.assertEqual(list(resumed._novel_grades), list(mind._novel_grades))
        self.assertEqual(resumed._hold_active, mind._hold_active)
        self.assertEqual(list(resumed._game_episodes), list(mind._game_episodes))
        self.assertEqual(len(resumed._game_episodes), 20)
        self.assertEqual([tuple(x) for x in resumed._sit_readings], list(mind._sit_readings))
        self.assertEqual(json.dumps(resumed._readiness_readings(), sort_keys=True),
                         json.dumps(mind._readiness_readings(), sort_keys=True), "the resumed mind reads the same judge")

    def test_resume_before_stage_4_recomputes_moments_stage(self) -> None:
        """No ledger "stage" key at all (an older snapshot) -> `_moments_stage()` against the LOADED org,
        never the pre-load org's t=0."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind.snapshot()
        ledger_path = tmp / "run" / "state" / "ledger.json"
        ledger = json.loads(ledger_path.read_text())
        del ledger["stage"]
        ledger_path.write_text(json.dumps(ledger))
        resumed, _ = Mind.resume(_genome_path(tmp), tmp / "run")
        self.assertEqual(resumed.stage, 1)   # org.t == 0 in this test -- still stage 1, but via the fallback path, not a KeyError


class TestReplayIdentityOfAStageEvent(unittest.TestCase):
    def _build_and_run(self) -> Path:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        clk = rr.Clock()
        _base_setup(mind, clk)
        _feed(mind, [rr.sit(clk, 0.99, 0.97, 0.7), rr.sit(clk, 0.99, 0.97, 0.7)])
        self.assertEqual(mind.stage, 4, "setup must actually reach stage 4, or this test proves nothing")
        journals = list((tmp / "run" / "journal").glob("*.jsonl"))
        self.assertEqual(len(journals), 1)
        return journals[0]

    def test_two_independent_minds_given_the_same_setup_and_tape_commit_identically(self) -> None:
        """Proves `_maybe_advance_stage`'s own journal write is deterministic — the same law gate_g4.py's
        own gate2/gate3 prove for the rest of the mind (two independent runs, same input, compared) — AND
        routed through creature.replay's own `read_mind_journal`/`compare()` (the SAME functions
        gate_g4.py's gate3 and every --against comparison use), not a hand-rolled read, so this test also
        stands as the direct proof for creature/replay.py's own fix: a "stage" event is a MIND row, kept by
        `read_mind_journal`, and `compare()` sees it agree on both sides."""
        from creature.replay import compare, read_mind_journal

        path_a, path_b = self._build_and_run(), self._build_and_run()
        rows_a, rows_b = read_mind_journal(path_a), read_mind_journal(path_b)
        stage_a = [r for r in rows_a if r.get("event") == "stage"]
        stage_b = [r for r in rows_b if r.get("event") == "stage"]
        self.assertEqual(len(stage_a), 1, "read_mind_journal must KEEP the mind-level 'stage' event, not drop it as a body-only one")
        self.assertEqual(len(stage_b), 1)
        diff = compare(rows_a, rows_b, ignore=("at",))   # "at" is the tape row's own wall-clock instant, carried verbatim -- identical here since both builds use identical synthetic timestamps; excluded anyway to mirror creature/replay.py's own `ignore` convention (the reader masks fields it has declared volatile)
        self.assertIsNone(diff, f"two independent Minds given the identical setup and tape must compare identical via creature.replay.compare(): {diff}")

    def test_read_mind_journal_keeps_stage_but_drops_body_only_events(self) -> None:
        """The precise regression this fix targets: a hand-built journal file mixing a real "stage" event
        (mind-level, ALPHA4-PREREG §4) with the four BODY-only bookkeeping events (creature/body.py's own
        `_journal_event`, grep-verified exhaustive) — only the four are dropped."""
        from creature.replay import read_mind_journal

        tmp = Path(tempfile.mkdtemp())
        jpath = tmp / "j.jsonl"
        rows = [
            {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 0, "backlog_replayed": 0},
            {"seq": 1, "at": "t", "sit": {"score": 0.9}},
            {"seq": None, "at": "t", "event": "snapshot", "snapshots": 1, "at_moment": 500},
            {"seq": 222, "at": "t", "event": "stage", "stage": 4, "moment": 0, "readings": {"a": {"ok": True}}},
            {"seq": None, "at": "t", "event": "sense_restart", "sense": "web", "error": "x"},
            {"seq": None, "at": "t", "event": "stop"},
        ]
        jpath.write_text("".join(json.dumps(r) + "\n" for r in rows))
        kept = read_mind_journal(jpath)
        self.assertEqual(kept, [rows[1], rows[3]], f"expected only the 'sit' row and the 'stage' event kept, got {kept}")


if __name__ == "__main__":
    unittest.main()
