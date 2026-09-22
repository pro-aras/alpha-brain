"""test_self_gene.py — L-9/SELF (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-9;
docs/briefs/LIFE-A-ANSWER-SELF.md #3): `SELF from body; beliefs about itself; skip thinks when
backlog > <n>` — the body row becomes a think-pool kind `self`; its work compares this reading with the
previous one and files a belief about itself (through `genome/think.py:believe`, word encodes the
trigger, `cells=[]`, the two body rows' own seq numbers as its "episodes") when a counter among
{moments, births, arrivals} stalls while another moves, `refused_nmax` rises, or `backlog` crosses the
declared threshold; `_maybe_think` skips (and counts) THINK while the LAST RECORDED body reading's
`backlog` stays over that threshold — read from the recorded row, never the live queue, so replay reads
the same number and decides the same.

edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:27 +0400 — #3 (docs/briefs/LIFE-A-ANSWER-SELF.md).
"""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.tape import Tape
from genome import world
from genome.machinery import GenomeError, parse_genome
from genome.think import read_beliefs

GENOME_PATH = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"
SELF_LINES = (
    "\nTHINK every 1 canvases\n"
    "BELIEF clash opens never overwrites\n"
    "SENSE body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss backlog refused_nmax\n"
    "SELF from body; beliefs about itself; skip thinks when backlog > 200\n"
)
SELF_GENOME_TEXT = GENOME_PATH.read_text() + SELF_LINES

BASE_READING = {"moments": 100, "births": 50, "arrivals": 1, "budget_left": 300, "refused": 0,
                 "restarts": 0, "mind_ms": 1.0, "rss": 10.0, "backlog": 0, "refused_nmax": 0}


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO()
    Image.fromarray(rgb).save(b, format="PNG")
    return b.getvalue()


def _write_genome(text: str) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / "self.genome"
    p.write_text(text)
    return p


def _mind(text: str = SELF_GENOME_TEXT, blind: frozenset = frozenset()) -> "tuple[Mind, Tape]":
    root = Path(tempfile.mkdtemp()) / "run"
    tape = Tape(root)
    mind = Mind(_write_genome(text), root, blind=blind)
    return mind, tape


def _consume_canvas(mind: Mind, tape: Tape, seq_hint: int) -> None:
    """One sight-only canvas (no word) -- a real tower-sized picture, through the real tape/publish
    road, so `_consume_eye` needs nothing special-cased."""
    rgb, _truth = world.render_canvas("circle", np.random.default_rng([9, seq_hint]))
    row = tape.publish("eye", _png(rgb), {"moment": f"m{seq_hint}", "source": "test"}, "png")
    mind.consume(row)


def _consume_body(mind: Mind, tape: Tape, reading: dict) -> int:
    import json
    row = tape.publish("body", json.dumps(reading).encode("utf-8"), {"moment": "body", "source": "body", "reading": reading}, "json")
    mind.consume(row)
    return int(row["seq"])


class TestSelfParser(unittest.TestCase):
    def test_parses(self) -> None:
        g = parse_genome(SELF_GENOME_TEXT)
        self.assertEqual(g.declared["SELF"], {"backlog_threshold": 200})

    def test_bad_syntax_refuses(self) -> None:
        with self.assertRaises(GenomeError):
            parse_genome(GENOME_PATH.read_text() + "SELF from body\n")


class TestSelfPoolAndBelief(unittest.TestCase):
    def test_empty_pool_before_two_readings(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        self.assertEqual(mind.think_counters["thinks"], 1)
        self.assertEqual(mind.think_counters["beliefs"], 0)

    def test_births_stalled_while_moments_moved_files_a_self_belief(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        seq1 = _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 2)
        self.assertEqual(mind.think_counters["beliefs"], 0, "one reading is not a pair")
        r2 = dict(BASE_READING); r2["moments"] = 110      # moments moved, births/arrivals unchanged
        seq2 = _consume_body(mind, tape, r2)
        _consume_canvas(mind, tape, 3)                    # the pool now holds a 'self' item
        self.assertEqual(mind.think_counters["beliefs"], 1)
        rows = read_beliefs(mind.run_root / "state" / "beliefs.jsonl")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["word"], "self:births_stopped")
        self.assertEqual(rows[0]["cells"], [])
        self.assertEqual(sorted(rows[0]["episodes"]), sorted([seq1, seq2]), "cites the two body rows' own seq numbers")

    def test_refused_nmax_rising_files_no_room_belief(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 2)
        # moments/births/arrivals all move TOGETHER (isolating the refused_nmax trigger from the stall trigger)
        r2 = dict(BASE_READING); r2["moments"] = 110; r2["births"] = 55; r2["arrivals"] = 2; r2["refused_nmax"] = 5
        _consume_body(mind, tape, r2)
        _consume_canvas(mind, tape, 3)
        rows = read_beliefs(mind.run_root / "state" / "beliefs.jsonl")
        self.assertEqual([r["word"] for r in rows], ["self:no_room"])

    def test_self_trigger_no_longer_handles_backlog(self) -> None:
        """`_self_trigger` keeps only the two triggers a comparison CAN see (stall, no_room) -- the
        original finding (docs/briefs/LIFE-A-REPORT.md §3 clause 6) was that the backlog-crossing
        trigger, read the SAME way, is preempted by its own skip and can never fire; the coordinator's
        fix (below) replaces it with a run-of-skips rule instead of tuning the threshold."""
        mind, _tape = _mind()
        r1 = dict(BASE_READING); r1["backlog"] = 50
        r2 = dict(BASE_READING); r2["backlog"] = 250   # crosses 200
        self.assertIsNone(mind._self_trigger(r1, r2))

    def test_no_trigger_files_nothing_and_does_not_crash(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 2)
        r2 = dict(BASE_READING); r2["moments"] = 110; r2["births"] = 55; r2["arrivals"] = 2   # everything moved together
        _consume_body(mind, tape, r2)
        _consume_canvas(mind, tape, 3)
        self.assertEqual(mind.think_counters["beliefs"], 0)

    def test_revisiting_the_same_trigger_never_crashes_deduce_on_empty_cells(self) -> None:
        """advisor's check: a self belief's cells=[] must never crash deduce()/read_beliefs(fold=True)
        (an empty-cells row paired with anything else via a shared-cell test, or a same-word revisit)."""
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 2)
        r2 = dict(BASE_READING); r2["moments"] = 110
        _consume_body(mind, tape, r2)
        _consume_canvas(mind, tape, 3)
        r3 = dict(BASE_READING); r3["moments"] = 120       # SAME stall pattern again -> a REVISIT, not a crash
        _consume_body(mind, tape, r3)
        _consume_canvas(mind, tape, 4)
        from genome.think import deduce
        beliefs = read_beliefs(mind.run_root / "state" / "beliefs.jsonl", fold=True)
        deduce(beliefs)   # must not raise
        self.assertGreaterEqual(mind.think_counters["revisits"], 1)

    def test_no_belief_gene_dead_ends_without_crashing(self) -> None:
        text = SELF_GENOME_TEXT.replace("BELIEF clash opens never overwrites\n", "")
        mind, tape = _mind(text)
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 2)
        r2 = dict(BASE_READING); r2["moments"] = 110
        _consume_body(mind, tape, r2)
        _consume_canvas(mind, tape, 3)          # must not crash
        self.assertEqual(mind.think_counters["beliefs"], 0)


class TestBacklogSkip(unittest.TestCase):
    def test_skips_and_counts_while_last_reading_over_threshold(self) -> None:
        mind, tape = _mind()
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 0, "#164: on STATUS from the start")
        _consume_canvas(mind, tape, 1)
        r_high = dict(BASE_READING); r_high["backlog"] = 300
        _consume_body(mind, tape, r_high)
        thinks_before = mind.think_counters["thinks"]
        _consume_canvas(mind, tape, 2)          # the NEXT think boundary: skipped, not counted as a think
        self.assertEqual(mind.think_counters["thinks"], thinks_before, "a skip is not a think")
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 1)

    def test_resumes_once_backlog_drops(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, {**BASE_READING, "backlog": 300})
        _consume_canvas(mind, tape, 2)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 1)
        _consume_body(mind, tape, {**BASE_READING, "backlog": 10})
        thinks_before = mind.think_counters["thinks"]
        _consume_canvas(mind, tape, 3)
        self.assertEqual(mind.think_counters["thinks"], thinks_before + 1)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 1, "unchanged: this boundary was not skipped")


class TestBehindBeliefOnResume(unittest.TestCase):
    """The coordinator's fix (2026-09-22, after the report's §3 clause 6 finding): "I am behind" is not
    a comparison trigger (it can never win against its own skip) -- it is filed at the FIRST think that
    RUNS after a run of skips, citing the body rows the skips actually read (backlog > threshold), never
    the resuming (now <= threshold) row. The skip itself is unchanged (still protects liveness); the
    stall/no_room triggers are unchanged (TestSelfPoolAndBelief above)."""

    def test_three_skipped_rows_then_one_resume_files_exactly_one_behind_belief(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)                             # canvas 1: empty pool, nothing to compare yet
        seqs = []
        for _ in range(3):
            seqs.append(_consume_body(mind, tape, {**BASE_READING, "backlog": 300}))
            _consume_canvas(mind, tape, 2)                         # each: a SKIP (reads THIS row)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 3)
        self.assertEqual(read_beliefs(mind.run_root / "state" / "beliefs.jsonl"), [], "no belief while still skipping")
        thinks_before = mind.think_counters["thinks"]
        _consume_body(mind, tape, {**BASE_READING, "backlog": 0})
        _consume_canvas(mind, tape, 3)                             # the FIRST think that RUNS after the run of skips
        self.assertEqual(mind.think_counters["thinks"], thinks_before + 1)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 3, "the resume boundary is not itself a skip")
        rows = read_beliefs(mind.run_root / "state" / "beliefs.jsonl")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["word"], "self:behind")
        self.assertEqual(rows[0]["cells"], [])
        self.assertEqual(sorted(rows[0]["episodes"]), sorted(seqs), "cites exactly the three body rows the skips read")

    def test_run_state_resets_after_filing_a_second_run_files_a_second_belief(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, {**BASE_READING, "backlog": 300})
        _consume_canvas(mind, tape, 2)                              # skip 1
        _consume_body(mind, tape, {**BASE_READING, "backlog": 0})
        _consume_canvas(mind, tape, 3)                              # resume -> belief 1 (revisit-shaped word, same cells=[])
        _consume_body(mind, tape, {**BASE_READING, "backlog": 300})
        _consume_canvas(mind, tape, 4)                              # skip 2 (a NEW run)
        _consume_body(mind, tape, {**BASE_READING, "backlog": 0})
        _consume_canvas(mind, tape, 5)                              # resume -> belief 2 (a revisit of "self:behind", same cells)
        rows = read_beliefs(mind.run_root / "state" / "beliefs.jsonl")
        self.assertEqual([r["word"] for r in rows], ["self:behind", "self:behind"])
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 2)

    def test_no_backlog_files_none(self) -> None:
        mind, tape = _mind()
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, dict(BASE_READING))               # backlog 0 throughout
        _consume_canvas(mind, tape, 2)
        _consume_body(mind, tape, dict(BASE_READING))
        _consume_canvas(mind, tape, 3)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 0)
        self.assertEqual(read_beliefs(mind.run_root / "state" / "beliefs.jsonl"), [])

    def test_replay_of_the_skip_then_resume_tape_is_byte_identical(self) -> None:
        def run() -> Mind:
            mind, tape = _mind()
            _consume_canvas(mind, tape, 1)
            for _ in range(3):
                _consume_body(mind, tape, {**BASE_READING, "backlog": 300})
                _consume_canvas(mind, tape, 2)
            _consume_body(mind, tape, {**BASE_READING, "backlog": 0})
            _consume_canvas(mind, tape, 3)
            return mind

        m1, m2 = run(), run()
        self.assertEqual(m1.think_counters, m2.think_counters)
        b1 = read_beliefs(m1.run_root / "state" / "beliefs.jsonl")
        b2 = read_beliefs(m2.run_root / "state" / "beliefs.jsonl")
        self.assertEqual(b1, b2)
        self.assertEqual(len(b1), 1)
        self.assertEqual(b1[0]["word"], "self:behind")


class TestBlindBody(unittest.TestCase):
    def test_blind_body_files_no_self_belief_and_skips_nothing(self) -> None:
        mind, tape = _mind(blind=frozenset({"body"}))
        _consume_canvas(mind, tape, 1)
        _consume_body(mind, tape, {**BASE_READING, "backlog": 300})
        _consume_canvas(mind, tape, 2)
        _consume_body(mind, tape, {**BASE_READING, "moments": 110, "backlog": 300})
        _consume_canvas(mind, tape, 3)
        self.assertEqual(mind.think_counters["beliefs"], 0)
        self.assertEqual(mind.think_counters["think_skipped_for_backlog"], 0)


class TestSelfReplayIdentical(unittest.TestCase):
    def test_replay_produces_the_same_counters_and_beliefs(self) -> None:
        """Same seeded renderer, a FRESH tape (fresh root) each run, same genome -- the mind's decisions
        over the same row stream must be identical (mark vii, extended to SELF)."""
        def run() -> Mind:
            mind, tape = _mind()
            _consume_canvas(mind, tape, 1)
            _consume_body(mind, tape, dict(BASE_READING))
            _consume_canvas(mind, tape, 2)
            r2 = dict(BASE_READING); r2["moments"] = 110
            _consume_body(mind, tape, r2)
            _consume_canvas(mind, tape, 3)
            _consume_body(mind, tape, {**BASE_READING, "moments": 110, "backlog": 300})
            _consume_canvas(mind, tape, 4)
            return mind

        m1, m2 = run(), run()
        self.assertEqual(m1.think_counters, m2.think_counters)
        b1 = read_beliefs(m1.run_root / "state" / "beliefs.jsonl")
        b2 = read_beliefs(m2.run_root / "state" / "beliefs.jsonl")
        self.assertEqual(b1, b2)


class TestBodySenseFieldMap(unittest.TestCase):
    """L-9/SELF: `body_sense.py`'s STATUS_FIELD_MAP gains "backlog" -> mind_backlog_rows (#236, already on
    STATUS) and "refused_nmax" -> births_refused_nmax (also already on STATUS) -- the two genome words
    this task's SELF gene reads off the published body row."""

    def test_backlog_and_refused_nmax_map_to_the_right_status_keys(self) -> None:
        from creature.senses import body_sense
        self.assertEqual(body_sense.STATUS_FIELD_MAP["backlog"], "mind_backlog_rows")
        self.assertEqual(body_sense.STATUS_FIELD_MAP["refused_nmax"], "births_refused_nmax")

    def test_sense_reads_both_fields_from_a_real_status_file(self) -> None:
        import json
        import threading
        from creature.senses import body_sense
        root = Path(tempfile.mkdtemp())
        (root / "STATUS.json").write_text(json.dumps({
            "heartbeat_at": "t0", "mind_backlog_rows": 42, "births_refused_nmax": 7,
        }))
        published = []
        stop = threading.Event()

        def publish(sense, payload, meta, ext):
            published.append((sense, json.loads(payload), meta))
            stop.set()

        body_sense.sense(publish, stop, root, ["backlog", "refused_nmax"], period_s=0.01)
        self.assertEqual(len(published), 1)
        sense_name, reading, meta = published[0]
        self.assertEqual(sense_name, "body")
        self.assertEqual(reading, {"backlog": 42, "refused_nmax": 7})
        self.assertEqual(meta["reading"], reading)


if __name__ == "__main__":
    unittest.main()
