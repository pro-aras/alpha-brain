# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:20 +0400 — ALPHA4-PREREG.md §4: THE READINESS
# JUDGE. Tests drive `Mind.consume()` directly against hand-built rows (the same technique
# tests/creature/test_g5k_outcome.py's snapshot/resume tests use) rather than the full Body/SenseThread
# machinery — this file's job is the JUDGE's OWN streak/commit/persistence/replay mechanism, not to
# re-prove SENTENCE's frame-filing (builder C's own precision toy already does that) or OUTCOME/SIT's own
# reflex-episode mechanism (G5-K's own tests already do that).
#
# Condition (b)'s frame/lift half is seeded DIRECTLY: `mind._frames` (a plain dict, populated in real life
# only by THINK's own frame-filing call sites) and `mind.episodes` (via real `.write()` calls carrying a
# heavily-skewed `words_in_instant` corpus — verified against the REAL `genome.sentence.find_frames()`,
# never a stub) — this proves `_frames_lift_ok()`'s own integration with `find_frames()` is correct without
# needing THINK's kind-fair pool selection to reliably choose "frame" over competing kinds across dozens of
# ticks (a separate, already-tested concern). Condition (b)'s READ-PROXY half is RAISED (see
# creature/mind.py's own `_read_proxy`/`_READ_PROXY_RAISE_REASON`); `_read_proxy_override` (test-only) lets
# these tests prove the streak/commit machinery independently of that one open question, AND a dedicated
# test proves the shipped (override-absent) behaviour stays fail-closed.
from __future__ import annotations

import itertools
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import numpy as np

from creature.mind import Mind

ROOT = Path(__file__).resolve().parents[2]
SKELETON_TEXT = (ROOT / "genome" / "G4-skeleton.genome").read_text()

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

FRAME_PAIRS = [("red", "ball"), ("blue", "key"), ("green", "box")]


def _genome_path(tmp_root: Path, extra: List[str] = EXTRA_LINES) -> Path:
    p = tmp_root / "test.genome"
    p.write_text(SKELETON_TEXT + "\n" + "\n".join(extra) + "\n")
    return p


def _new_mind(tmp_root: Path, extra: List[str] = EXTRA_LINES) -> Mind:
    root = tmp_root / "run"
    root.mkdir(parents=True, exist_ok=True)
    return Mind(_genome_path(tmp_root, extra), root)


def _seed_frames(mind: Mind, pairs=FRAME_PAIRS, n_each: int = 10) -> None:
    """§4(b)'s frame/lift half: real `Episodes.write()` calls (a heavily skewed corpus, verified against
    the real `find_frames()` in a standalone check before this file was written: exactly `len(pairs)`
    qualifying rows, each lift 4.2), plus `mind._frames` populated directly — THINK's own two call sites
    are the only OTHER way to populate it in production; this is the seam this file tests around, not a
    fabrication of a different mechanism."""
    dim_s, dim_w = mind.genome.sight_dim(), mind.genome.words_dim()
    i = 0
    for w1, w2 in pairs:
        for _ in range(n_each):
            mind.episodes.write(moment=i, x_s=np.zeros(dim_s), x_w=np.zeros(dim_w), word=w1, surprise=0.0,
                                 words_in_instant=[w1, w2])
            i += 1
    for a, b in itertools.permutations(["aa", "bb", "cc", "dd"], 2):   # noise: each pair count=1, never clears min_count=5
        mind.episodes.write(moment=i, x_s=np.zeros(dim_s), x_w=np.zeros(dim_w), word=a, surprise=0.0,
                             words_in_instant=[a, b])
        i += 1
    for w1, w2 in pairs:
        mind._frames[f"{w1}|{w2}"] = {"w1": w1, "w2": w2, "episodes": []}


def _outcome_row(seq: int, got: float) -> Dict[str, object]:
    return {"seq": seq, "at": f"2026-09-23T00:00:{seq % 60:02d}.{seq:03d}Z", "sense": "outcome",
            "meta": {"act": "forward", "got": got, "expected": None, "residual": None, "source": "game", "chosen_by": "mind"}}


def _sit_row(seq: int, score, composite) -> Dict[str, object]:
    return {"seq": seq, "at": f"2026-09-23T00:01:{seq % 60:02d}.{seq:03d}Z", "sense": "sit",
            "meta": {"score": score, "exam_file": f"{seq}.json", "composite": composite, "source": "sit"}}


def _grade_row(seq: int, gid: str, right: bool, novel: bool) -> Dict[str, object]:
    return {"seq": seq, "at": f"2026-09-23T00:02:{seq % 60:02d}.{seq:03d}Z", "sense": "grade",
            "meta": {"id": gid, "right": right, "novel": novel}}


def _hold_row(seq: int, active: bool) -> Dict[str, object]:
    return {"seq": seq, "at": f"2026-09-23T00:03:{seq % 60:02d}.{seq:03d}Z", "sense": "hold", "meta": {"active": active}}


def _feed_outcomes(mind: Mind, n: int = 200, got: float = 0.5, start_seq: int = 1) -> int:
    seq = start_seq
    for _ in range(n):
        mind.consume(_outcome_row(seq, got))
        seq += 1
    return seq


def _feed_grades(mind: Mind, start_seq: int) -> int:
    """20 grades total: 10 non-novel (all right), 10 novel (8 right, 2 wrong) — 18/20 = 0.9 >= 0.8 overall;
    8/10 of the novel ones right, meeting (d)'s own "8 of the last 10 flagged novel" bar exactly."""
    seq = start_seq
    for i in range(10):
        mind.consume(_grade_row(seq, f"g{i}", True, False))
        seq += 1
    novel_rights = [True] * 8 + [False] * 2
    for i, right in enumerate(novel_rights):
        mind.consume(_grade_row(seq, f"n{i}", right, True))
        seq += 1
    return seq


def _base_setup(mind: Mind, start_seq: int = 1) -> int:
    """Every condition satisfied EXCEPT (c) (which needs the test's own two real `sit` rows) — the common
    setup every "one condition removed" test starts from, so each test's OWN deviation is the only
    difference from the passing case."""
    mind._read_proxy_override = True
    _seed_frames(mind)
    seq = _feed_outcomes(mind, start_seq=start_seq)
    seq = _feed_grades(mind, seq)
    # a PRIOR exam reading, as if this life already had one before the test's own tape begins — (c) needs
    # TWO readings to ever be non-trivially true; the test's own two REAL sit rows below are then the two
    # CONSECUTIVE windows the brief's own words describe ("stage 4 at the second window").
    mind._sit_readings.append((0.99, 0.97))
    return seq


class TestAllFiveHoldReachesStage4(unittest.TestCase):
    def test_all_five_hold_at_second_window(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        seq = _base_setup(mind)

        mind.consume(_sit_row(seq, 0.99, 0.97))          # window 1: sit_readings = [seed, this] -- all hold -> streak 1
        self.assertEqual(mind.stage, 1, "must not commit on the FIRST all-hold window")
        seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97))          # window 2: sit_readings = [row1, row2] -- all hold again -> streak 2 -> COMMIT
        self.assertEqual(mind.stage, 4, "must commit exactly on the SECOND consecutive all-hold window")

        journals = list((tmp / "run" / "journal").glob("*.jsonl"))
        self.assertTrue(journals)
        rows = [__import__("json").loads(l) for f in journals for l in f.read_text().splitlines()]
        stage_events = [r for r in rows if r.get("event") == "stage"]
        self.assertEqual(len(stage_events), 1, "exactly ONE stage event, never more")
        self.assertEqual(stage_events[0]["stage"], 4)
        self.assertEqual(set(stage_events[0]["readings"]), {"a", "b", "c", "d", "e"})
        self.assertTrue(all(stage_events[0]["readings"].values()))

    def test_never_undone_once_committed(self) -> None:
        """§4's own law: "never undone by the mind" — a LATER window that would fail must not revert it."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        seq = _base_setup(mind)
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        self.assertEqual(mind.stage, 4)
        mind._hold_active = True                          # everything now fails (e)
        mind.consume(_sit_row(seq, 0.10, 0.10))            # (c) also fails now
        self.assertEqual(mind.stage, 4, "stage 4, once committed, must never be undone by a later bad window")

    def test_read_proxy_absent_by_default_blocks_stage_4_honestly(self) -> None:
        """The SHIPPED behaviour (no override): (b)'s read-proxy is RAISED, so even with every other
        condition perfect, stage 4 must never commit — fail-closed, exactly as the PREREG's own stance on
        an unmet bar requires."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        seq = _feed_outcomes(mind, start_seq=1)
        seq = _feed_grades(mind, seq)
        _seed_frames(mind)   # frames/lift genuinely satisfied -- read_proxy_override left at its default None
        mind._sit_readings.append((0.99, 0.97))
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        self.assertEqual(mind.stage, 1, "with no honest read proxy, (b) can never hold -- stage 4 must not commit")


class TestEachConditionRemovedAlone(unittest.TestCase):
    def _run_to_stage(self, mind: Mind, seq: int) -> None:
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1

    def test_a_removed_low_reward_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, n=200, got=0.1, start_seq=1)   # under 0.35
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_a_removed_too_few_rewards_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, n=150, got=0.9, start_seq=1)   # under 200 samples
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_b_removed_too_few_frames_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind, pairs=FRAME_PAIRS[:2])   # only 2 frames, need >= 3
        seq = _feed_outcomes(mind, start_seq=1)
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_b_removed_a_frame_no_longer_clears_lift_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        mind._frames["nonexistent|pair"] = {"w1": "nonexistent", "w2": "pair", "episodes": []}   # alive, but find_frames() will never return it
        seq = _feed_outcomes(mind, start_seq=1)
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_c_removed_low_composite_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, start_seq=1)
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.99, 0.80))   # composite under 0.95
        mind.consume(_sit_row(seq, 0.99, 0.80)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.80)); seq += 1
        self.assertNotEqual(mind.stage, 4)

    def test_c_removed_low_q1_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, start_seq=1)
        seq = _feed_grades(mind, seq)
        mind._sit_readings.append((0.90, 0.97))   # Q1 (score) under 0.98
        mind.consume(_sit_row(seq, 0.90, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.90, 0.97)); seq += 1
        self.assertNotEqual(mind.stage, 4)

    def test_d_removed_too_few_grades_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, start_seq=1)
        for i in range(15):   # under 20
            mind.consume(_grade_row(seq, f"g{i}", True, i >= 5)); seq += 1
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_d_removed_novel_window_not_yet_full_blocks_even_when_all_seen_are_right(self) -> None:
        """Regression (advisor-caught): PREREG §4(d)/§8 point 7 both name TEN as the novel denominator
        ("8 of the last 10"; "ten of them never-seen pictures") — 8 novel grades, all right, must NOT
        satisfy (d) before the last-10 window has ever filled."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, start_seq=1)
        for i in range(10):
            mind.consume(_grade_row(seq, f"g{i}", True, False)); seq += 1
        for i in range(8):   # only 8 novel grades total, all right -- the window (10) never fills
            mind.consume(_grade_row(seq, f"n{i}", True, True)); seq += 1
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_d_removed_too_few_novel_right_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind._read_proxy_override = True
        _seed_frames(mind)
        seq = _feed_outcomes(mind, start_seq=1)
        for i in range(10):
            mind.consume(_grade_row(seq, f"g{i}", True, False)); seq += 1
        novel_rights = [True] * 5 + [False] * 5   # only 5 of 10 novel right, need >= 8
        for i, right in enumerate(novel_rights):
            mind.consume(_grade_row(seq, f"n{i}", right, True)); seq += 1
        mind._sit_readings.append((0.99, 0.97))
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)

    def test_e_removed_hold_active_blocks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        seq = _base_setup(mind)
        mind.consume(_hold_row(seq, True)); seq += 1
        self._run_to_stage(mind, seq)
        self.assertNotEqual(mind.stage, 4)


class TestGradeAndHoldConsumption(unittest.TestCase):
    def test_grade_rows_update_counters_and_journal(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind.consume(_grade_row(1, "g0", True, False))
        mind.consume(_grade_row(2, "g1", False, True))
        self.assertEqual(mind._grades_total, 2)
        self.assertEqual(mind._grades_right, 1)
        self.assertEqual(list(mind._novel_grades), [False])

    def test_hold_row_updates_the_flag(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        self.assertFalse(mind._hold_active)
        mind.consume(_hold_row(1, True))
        self.assertTrue(mind._hold_active)
        mind.consume(_hold_row(2, False))
        self.assertFalse(mind._hold_active)

    def test_grade_and_hold_rows_are_dead_weight_when_gene_undeclared(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        no_grade = [l for l in EXTRA_LINES if not l.strip().startswith("SENSE    grade")]
        mind = _new_mind(tmp, extra=no_grade)
        mind.consume(_grade_row(1, "g0", True, True))
        mind.consume(_hold_row(2, True))
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
        seq = _base_setup(mind)
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        self.assertEqual(mind.stage, 4)
        mind.snapshot()

        resumed, last_seq = Mind.resume(_genome_path(tmp), tmp / "run")
        self.assertEqual(resumed.stage, 4, "a resume mid-life must keep the committed stage")
        self.assertEqual(resumed._stage_ready_streak, mind._stage_ready_streak)
        self.assertEqual(resumed._grades_total, mind._grades_total)
        self.assertEqual(resumed._grades_right, mind._grades_right)
        self.assertEqual(list(resumed._novel_grades), list(mind._novel_grades))
        self.assertEqual(resumed._hold_active, mind._hold_active)
        self.assertEqual(list(resumed._game_rewards), list(mind._game_rewards))
        self.assertEqual([tuple(x) for x in resumed._sit_readings], list(mind._sit_readings))

    def test_resume_before_stage_4_recomputes_moments_stage(self) -> None:
        """No ledger "stage" key at all (an older snapshot) -> `_moments_stage()` against the LOADED org,
        never the pre-load org's t=0."""
        tmp = Path(tempfile.mkdtemp())
        mind = _new_mind(tmp)
        mind.snapshot()
        import json
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
        seq = _base_setup(mind)
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        mind.consume(_sit_row(seq, 0.99, 0.97)); seq += 1
        self.assertEqual(mind.stage, 4, "setup must actually reach stage 4, or this test proves nothing")
        journals = list((tmp / "run" / "journal").glob("*.jsonl"))
        self.assertEqual(len(journals), 1)
        return journals[0]

    def test_two_independent_minds_given_the_same_setup_and_tape_commit_identically(self) -> None:
        """Proves `_maybe_advance_stage`'s own journal write is deterministic — the same law gate_g4.py's
        own gate2/gate3 prove for the rest of the mind (two independent runs, same input, compared) — AND
        routed through creature.replay's own `read_mind_journal`/`compare()` (the SAME functions
        gate_g4.py's gate3 and every --against comparison use), not a hand-rolled read, so this test also
        stands as the direct proof for creature/replay.py's own fix (below): a "stage" event is a MIND
        row, kept by `read_mind_journal`, and `compare()` sees it agree on both sides."""
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
        import json as _json
        from creature.replay import read_mind_journal

        tmp = Path(tempfile.mkdtemp())
        jpath = tmp / "j.jsonl"
        rows = [
            {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 0, "backlog_replayed": 0},
            {"seq": 1, "at": "t", "sit": {"score": 0.9}},
            {"seq": None, "at": "t", "event": "snapshot", "snapshots": 1, "at_moment": 500},
            {"seq": 222, "at": "t", "event": "stage", "stage": 4, "moment": 0, "readings": {"a": True}},
            {"seq": None, "at": "t", "event": "sense_restart", "sense": "web", "error": "x"},
            {"seq": None, "at": "t", "event": "stop"},
        ]
        jpath.write_text("".join(_json.dumps(r) + "\n" for r in rows))
        kept = read_mind_journal(jpath)
        self.assertEqual(kept, [rows[1], rows[3]], f"expected only the 'sit' row and the 'stage' event kept, got {kept}")


if __name__ == "__main__":
    unittest.main()
