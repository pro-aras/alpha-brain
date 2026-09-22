# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:49 +0400 — ALPHA4-PREREG.md §4/§6: found while
# proving "a tape carrying a stage/web row replays identically" through the CANONICAL road
# (tools/gate_g5_landing.sh's own tool, not just an ad hoc comparison): tools/replay_diff.py carried its
# OWN duplicate of creature/replay.py's "mind row" filter (a blanket `"event" not in r`), silently
# dropping a MIND-level semantic event ("stage", ALPHA4-PREREG §4; "epoch", §6) from ITS OWN comparison —
# the same gap creature/replay.py's own fix addresses, now closed here too by importing that fix's own
# `is_mind_row` instead of re-implementing it a second time (a definition kept in one place cannot drift
# out of sync with the other's fix the way these two already had).
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("replay_diff", ROOT / "tools" / "replay_diff.py")
rd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rd)

_BODY_EVENT_ROWS = [
    {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 0, "backlog_replayed": 0},
    {"seq": None, "at": "t", "event": "snapshot", "snapshots": 1, "at_moment": 500},
    {"seq": None, "at": "t", "event": "sense_restart", "sense": "web", "error": "x"},
    {"seq": None, "at": "t", "event": "stop"},
]
_MIND_ROWS = [
    {"seq": 1, "at": "t", "sit": {"score": 0.9}},
    {"seq": 222, "at": "t", "event": "stage", "stage": 4, "moment": 0, "readings": {"a": True}},
    {"seq": 300, "at": "t", "event": "epoch", "genome_sha": "abc", "moment": 999},
]


def _write(rows) -> str:
    p = Path(tempfile.mkdtemp()) / "j.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return str(p)


class TestMindRows(unittest.TestCase):
    def test_body_only_events_are_dropped(self) -> None:
        kept = rd.mind_rows(_write(_BODY_EVENT_ROWS))
        self.assertEqual(kept, [])

    def test_ordinary_domain_rows_and_mind_level_events_are_kept(self) -> None:
        kept = rd.mind_rows(_write(_MIND_ROWS))
        self.assertEqual(kept, _MIND_ROWS)

    def test_a_mixed_journal_keeps_only_the_non_body_rows(self) -> None:
        kept = rd.mind_rows(_write(_BODY_EVENT_ROWS + _MIND_ROWS))
        self.assertEqual(kept, _MIND_ROWS)


class TestMainComparesStageEventsCorrectly(unittest.TestCase):
    def test_identical_stage_events_on_both_sides_pass(self) -> None:
        a = _write(_MIND_ROWS)
        b = _write(_MIND_ROWS)
        self.assertEqual(rd.main([a, b]), 0)

    def test_a_stage_event_missing_on_one_side_is_caught_not_silently_ignored(self) -> None:
        a = _write(_MIND_ROWS)
        b = _write([_MIND_ROWS[0]])   # the stage/epoch events silently dropped on this side would be invisible under the OLD blanket filter
        self.assertEqual(rd.main([a, b]), 1)

    def test_a_differing_stage_reading_is_caught(self) -> None:
        a = _write(_MIND_ROWS)
        changed = [dict(r) for r in _MIND_ROWS]
        changed[1] = {**changed[1], "readings": {"a": False}}
        b = _write(changed)
        self.assertEqual(rd.main([a, b]), 1)


if __name__ == "__main__":
    unittest.main()
