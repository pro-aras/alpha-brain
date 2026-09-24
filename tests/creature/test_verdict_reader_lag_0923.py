# edit: Claude (Opus 5.5, reader-lag builder), 2026-09-23 16:32 +0400 — READER-LAG-0923: the reader reads THE LIFE THE MIND LIVED.
"""alpha4-1 crossed its saturation line (2,433 ms a canvas at 7,030 cells at 16:05 +04 against a world of ≈ 0.456 canvases/s). At the stop
the body (creature/body.py:stop) sets `stop_event`, the mind thread leaves its `q.get` loop WITHOUT reading the queue, then `mind.close()`
lands the in-flight think at the last eye row — so the live journal ends at the mind's last consumed seq, rows before the tape's head.
v3.3 replayed the whole cut tape: REPLAY read `<missing from --against>` (the lag, not a nondeterminism), `closed_whole` compared the cut
to the TAPE's head, and every tape mark counted world rows the mind never lived.

The records here are built from the LANDED shapes (#171/#173), never typed: tape rows by `creature.tape.Tape.publish`, the live journal
and the snapshot by a real `creature.mind.Mind` consuming the first 410 rows and then `close()` (the body's own order), the body's event
rows by `creature.body.Body._journal_event`, STATUS by `creature.body.Body._build_status` (its queue depth = the unconsumed rows), and the
backlog series by `creature.senses.body_sense.sense`'s own publish road. The ALIVE cases are synthetic G dicts in gather's output shape.
RED on v3.3 (master 2357347): docs/briefs/reader-lag-0923/red-lag-0923.log."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import threading
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from creature import body as body_mod
from creature.mind import Mind
from creature.replay import compare, read_mind_journal, run_replay
from creature.senses import body_sense
from creature.tape import Tape, read_tape
from genome import world
from tests.creature.test_life_e_think_thread import _build_tape, _png, _write_threaded_genome

_spec = importlib.util.spec_from_file_location("verdict_g4_lag", Path(__file__).resolve().parents[2] / "tools" / "verdict_g4.py")
vg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(vg)

N_CANVASES, SEED = 205, 7                  # 410 rows the mind lives (the test_replay_close fixture: a think in flight at the tail)
TAIL_CANVASES, TAIL_BODY = 45, 10          # + 90 canvas rows + 10 body rows = 100 rows the mind never consumes
BODY_FIELDS = ["moments", "births", "arrivals", "budget_left", "refused", "restarts", "mind_ms", "rss", "backlog", "refused_nmax"]   # genome/ALPHA4.genome's SENSE body line
BACKLOGS = [min(150, 17 * i) for i in range(TAIL_BODY)]       # 0 → 150: the first over 100 is 102


def _ns_body(root: Path, mind=None, backlog: int = 0):
    """What Body._journal_event / Body._build_status read off `self` — a namespace, so the body's OWN writers write the rows."""
    return types.SimpleNamespace(root=Path(root), _status_lock=threading.Lock(), _mind_times=[], sense_restarts=0, crash=None, mind=mind,
                                 started_at="2026-09-23T00:00:00.000Z", q=types.SimpleNamespace(qsize=lambda: backlog))


def _event(root: Path, event: dict) -> None:
    body_mod.Body._journal_event(_ns_body(root), event)


def _body_row(tape: Tape, root: Path, status: dict) -> None:
    """One SENSE body row through creature/senses/body_sense.py:sense itself (it reads STATUS.json and publishes the declared fields)."""
    (root / "STATUS.json").write_text(json.dumps(status))
    stop = threading.Event()
    def publish(sense, payload, meta, ext):
        row = tape.publish(sense, payload, meta, ext); stop.set(); return row
    body_sense.sense(publish, stop, root, fields=BODY_FIELDS, period_s=60.0)


def build_record(d: Path, tail: bool) -> dict:
    """A CLOSED record: the start event, 410 tape rows, a Mind that consumed them and closed, then (tail=True) 100 more rows the mind
    never consumed — body rows among them with the backlog stepping 0 → 150 — the final STATUS (last_seq 410, backlog = the unconsumed
    rows) and the stop event, in the body's own order."""
    d.mkdir(parents=True, exist_ok=True)
    gp = _write_threaded_genome(d)
    root = d / "root"; root.mkdir()
    _event(root, {"event": "start", "resumed_from_seq": 0, "backlog_replayed": 0})
    _build_tape(root, n=N_CANVASES, seed=SEED)
    mind = Mind(gp, root)
    for r in read_tape(root):
        mind.consume(r)
    lived = mind.last_seq
    tape = Tape(root)
    if tail:
        rng = np.random.default_rng(SEED + 1); things = ["circle", "square", "triangle", "diamond", "bar"]; k = 0
        for i in range(TAIL_CANVASES):
            if i % 5 == 0 and k < TAIL_BODY:
                _body_row(tape, root, body_mod.Body._build_status(_ns_body(root, mind, BACKLOGS[k]))); k += 1
            thing = things[i % len(things)]; rgb, _t = world.render_canvas(thing, rng); m = f"t{i:05d}"
            tape.publish("ear", thing.encode(), {"moment": m, "source": "test", "word": thing}, "txt")
            tape.publish("eye", _png(rgb), {"moment": m, "source": "test"}, "png")
        while k < TAIL_BODY:
            _body_row(tape, root, body_mod.Body._build_status(_ns_body(root, mind, BACKLOGS[k]))); k += 1
    mind.close()                                   # creature/body.py:stop — the queue is left unread, then close() lands the in-flight think
    head = max(r["seq"] for r in read_tape(root))
    (root / "STATUS.json").write_text(json.dumps(body_mod.Body._build_status(_ns_body(root, mind, head - lived))))
    _event(root, {"event": "stop"})
    return {"genome": gp, "root": root, "lived": lived, "head": head}


def _replay(genome: Path, tape_path: Path, close: bool) -> list:
    return read_mind_journal(run_replay(genome, tape_path, Path(tempfile.mkdtemp()), close=close))


def _read(p: Path) -> list:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


class _Records(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="reader-lag-"))
        cls.lag = build_record(cls.tmp / "lag", tail=True)
        cls.flat = build_record(cls.tmp / "flat", tail=False)
        cls.G = vg.gather(cls.lag["root"], cls.tmp / "lag-out", 1.0)
        cls.Gf = vg.gather(cls.flat["root"], cls.tmp / "flat-out", 1.0)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)


class ALaggingClosedRecord(_Records):
    def test_fixture_premise(self):
        self.assertEqual((self.lag["lived"], self.lag["head"]), (410, 510), "the mind lived 410 rows of a 510-row tape")
        self.assertEqual((self.flat["lived"], self.flat["head"]), (410, 410))

    def test_the_v33_road_diverges_by_the_lag_not_by_the_mind(self):
        # the defect, on the record's own rows: the WHOLE tape replayed and closed (v3.3's road — its closed_whole compared the cut to the
        # tape's head) is not the life the mind lived. The first difference sits AT the mind's last seq: the live close() landed the think
        # in flight on the last eye row it consumed (seq 410), the whole-tape replay lands it at a later boundary — then every row past
        # 410 is «missing from --against». Nothing before the mind's last seq differs: the divergence is the lag's, never the mind's.
        live = _read(self.lag["root"] / "journal" / sorted(p.name for p in (self.lag["root"] / "journal").glob("*.jsonl"))[0])
        live = [r for r in live if "event" not in r]
        whole = sorted((self.lag["root"] / "tape").glob("*.jsonl"))[0]
        got = _replay(self.lag["genome"], whole, close=True)
        d = compare(got, live)
        self.assertEqual(d, (410, "<row count: replay 1 vs --against 2>"), d)
        self.assertEqual(compare([r for r in got if int(r["seq"]) > 410], []), (min(int(r["seq"]) for r in got if int(r["seq"]) > 410), "<missing from --against>"))
        self.assertIsNone(compare([r for r in got if int(r["seq"]) < 410], [r for r in live if int(r["seq"]) < 410]))

    def test_gather_cuts_the_read_at_the_minds_last_consumed_seq(self):
        G, L = self.G, self.G["lag"]
        self.assertTrue(L["cut"]); self.assertEqual(G["last_seq"], 410)
        self.assertEqual(L["mind_last_seq"], 410); self.assertIn("status", L["source"]); self.assertIn("ledger", L["source"]); self.assertIn("journal", L["source"])
        self.assertEqual((L["rows_unconsumed"], L["rows_cut_by_lag"], L["time_cut_seq"], L["tape_head_seq"]), (100, 100, 510, 510))
        self.assertTrue(G["closed_whole"], "the mind closed whole relative to what it consumed")
        self.assertEqual([r["seq"] for r in G["tape"]], list(range(1, 411)))
        self.assertEqual(len(G["tape_world"]), 510)
        all_rows = _read(self.tmp / "lag-out" / "tape" / "ALL.jsonl")
        self.assertEqual((len(all_rows), all_rows[-1]["seq"]), (410, 410), "every twin's tape is the cut")
        self.assertLessEqual(max(int(r["seq"]) for r in G["mind"]), 410)
        self.assertEqual((L["status_backlog_rows"], L["backlog_reconciles"]), (100, True), "STATUS's queue depth at the stop = the tape's rows past the mind")
        self.assertLessEqual(G["hours_on_tape"], G["hours_on_tape_world"])
        self.assertGreaterEqual(L["world_hours_unconsumed"], 0.0)

    def test_the_replay_of_the_cut_tape_is_the_live_journal(self):
        # the reader's own road: ALL.jsonl replayed, closed iff closed_whole (verdict_g4.main → worker), against live-journal.jsonl
        got = _replay(self.lag["genome"], self.tmp / "lag-out" / "tape" / "ALL.jsonl", close=bool(self.G["closed_whole"]))
        live = read_mind_journal(self.tmp / "lag-out" / "live-journal.jsonl")
        self.assertGreater(len(live), 200)
        self.assertIsNone(compare(got, live), f"first difference {compare(got, live)}")

    def test_a_planted_divergence_inside_the_prefix_is_still_caught(self):
        live = read_mind_journal(self.tmp / "lag-out" / "live-journal.jsonl")
        got = _replay(self.lag["genome"], self.tmp / "lag-out" / "tape" / "ALL.jsonl", close=bool(self.G["closed_whole"]))
        # (a) one live row inside the prefix altered → caught at its seq
        planted = [dict(r) for r in live]
        i = next(i for i, r in enumerate(planted) if int(r["seq"]) >= 200 and "moment" in r)
        planted[i]["moment"] = "planted"
        self.assertEqual(compare(got, planted), (int(planted[i]["seq"]), "moment"))
        # (b) one eye payload inside the prefix replaced on a copy of the cut tape (verdict_g4.main's own plant road: per-file links, one real
        # file) by ANOTHER thing's canvas → the replay diverges. (A whole-image inversion does NOT: the eye front reads |g − mean| — found
        # by this test's first run; the reader's own plant inverts a block ON the thing, from the maker's truth file this fixture lacks.)
        rows = _read(self.tmp / "lag-out" / "tape" / "ALL.jsonl")
        eye = [r for r in rows if r["sense"] == "eye"][150]
        word = next(r["meta"]["word"] for r in rows if r["sense"] == "ear" and r["meta"]["moment"] == eye["meta"]["moment"])
        proot = self.tmp / "plant"; (proot / "tape" / "payload").mkdir(parents=True, exist_ok=True)
        src_payload = (self.lag["root"] / "tape")
        for r in rows:
            dst = proot / "tape" / r["payload"]
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True); dst.symlink_to((src_payload / r["payload"]).resolve())
        pp = proot / "tape" / eye["payload"]; pp.unlink()
        other, _t = world.render_canvas("diamond" if word != "diamond" else "circle", np.random.default_rng(99))
        Image.fromarray(other).save(pp, format="PNG")
        (proot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        d = compare(_replay(self.lag["genome"], proot / "tape" / "ALL.jsonl", close=bool(self.G["closed_whole"])), live)
        self.assertIsNotNone(d, "a payload inverted inside the prefix must diverge")
        self.assertGreaterEqual(d[0], int(eye["seq"])); self.assertLessEqual(d[0], 410)

    def test_the_backlog_series_is_read_from_the_body_rows(self):
        bs = self.G["lag"]["backlog_series"]
        self.assertEqual((bs["body_rows"], bs["n"], bs["max"], bs["last"]), (10, 10, 150, 150))
        self.assertEqual(bs["first_over_100"]["backlog"], 102)
        self.assertGreater(bs["first_over_100"]["seq"], 410, "the backlog grows in the unconsumed tail")
        self.assertEqual(bs["per_hour_max"], [150])
        self.assertIsNotNone(bs["moments_advanced_per_hour"])
        s = vg.lag_summary(self.G["lag"])
        self.assertEqual((s["backlog_max"], s["backlog_last"], s["backlog_first_over_100"]["backlog"], s["rows_unconsumed"]), (150, 150, 102, 100))
        t = vg.lag_text(s)
        for needle in ("410", "100 rows", "CUT", "first > 100 at", "reconciles with the tape: True"):
            self.assertIn(needle, t)


class ARecordWithNoTailReadsAsToday(_Records):
    def test_no_tail_no_cut_and_the_lag_reads_zero(self):
        G, L = self.Gf, self.Gf["lag"]
        self.assertFalse(L["cut"])
        self.assertEqual((L["rows_unconsumed"], L["rows_cut_by_lag"], L["world_hours_unconsumed"], L["world_hours_cut_by_lag"]), (0, 0, 0.0, 0.0))
        self.assertTrue(G["closed_whole"])
        self.assertEqual(G["tape"], G["tape_world"]); self.assertEqual(G["last_seq"], 410)
        self.assertEqual(G["hours_on_tape"], G["hours_on_tape_world"])
        self.assertEqual(L["backlog_series"]["n"], 0, "no body row on this record: no series, said so")
        # the v3.3 contract on the same rows: the time cut, and closed_whole = (the cut reaches the tape's head) and a stop event
        events = [r for r in _read(sorted((self.flat["root"] / "journal").glob("*.jsonl"))[0]) if "event" in r]
        self.assertEqual(G["closed_whole"], vg.closed_whole(events, G["last_seq"], self.flat["head"]))

    def test_no_tail_replay_is_the_live_journal(self):
        got = _replay(self.flat["genome"], self.tmp / "flat-out" / "tape" / "ALL.jsonl", close=bool(self.Gf["closed_whole"]))
        self.assertIsNone(compare(got, read_mind_journal(self.tmp / "flat-out" / "live-journal.jsonl")))


class MindLastConsumed(unittest.TestCase):
    J = [{"seq": None, "event": "start", "at": "x"}, {"seq": 5, "moment": "a"}, {"seq": 9, "think": {}}, {"seq": 7, "event": "stage"}]

    def test_the_largest_valid_reading_on_a_closed_record(self):
        m = vg.mind_last_consumed(self.J, {"last_seq": 10}, {"last_seq": 8}, 20, closed=True)
        self.assertEqual((m["mind_last_seq"], m["source"], m["journal_last_mind_seq"]), (10, "status", 9))
        m = vg.mind_last_consumed(self.J, {"last_seq": 9}, {"last_seq": 9}, 20, closed=True)
        self.assertEqual((m["mind_last_seq"], m["source"]), (9, "status = ledger = journal"))

    def test_a_running_life_never_reads_the_journals_last_row(self):
        # the journal's last row may be half-written while the mind runs; STATUS/ledger name a seq whose rows are all on disk
        m = vg.mind_last_consumed(self.J, {"last_seq": 6}, {"last_seq": 5}, 20, closed=False)
        self.assertEqual((m["mind_last_seq"], m["source"]), (6, "status"))

    def test_readings_outside_the_tape_are_ignored_and_the_journal_is_the_fallback(self):
        m = vg.mind_last_consumed(self.J, {"last_seq": 99}, {"last_seq": True}, 20, closed=True)
        self.assertEqual((m["mind_last_seq"], m["source"]), (9, "journal"))
        m = vg.mind_last_consumed(self.J, {}, {}, 20, closed=False)
        self.assertEqual(m["mind_last_seq"], 9); self.assertTrue(m["source"].startswith("journal (no STATUS/ledger"))
        self.assertEqual(vg.mind_last_consumed([], {}, {}, 20, closed=False)["mind_last_seq"], 0)


class ClosedWholeIsRelativeToTheCut(unittest.TestCase):
    E = [{"event": "start"}, {"event": "stop"}]

    def test_the_cut_at_the_minds_last_seq_closes_though_the_tape_runs_on(self):
        self.assertTrue(vg.closed_whole(self.E, 410, 510, mind_last_seq=410))

    def test_a_cut_short_of_the_minds_last_seq_never_closes(self):
        self.assertFalse(vg.closed_whole(self.E, 400, 510, mind_last_seq=410))

    def test_no_stop_event_never_closes(self):
        self.assertFalse(vg.closed_whole([{"event": "start"}], 410, 510, mind_last_seq=410))

    def test_the_old_contract_is_unchanged(self):
        self.assertTrue(vg.closed_whole(self.E, 500, 500)); self.assertFalse(vg.closed_whole(self.E, 400, 500))


def _z(t: datetime) -> str:
    return t.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def synthetic_G(world_h: float = 3.0, lived_h: float = 2.4, snapshots_until_h: float = 3.0, drop_sleeps_in_hour=None, hole_at_h=None) -> dict:
    """gather's output shape over a 3 h world (an ear and an eye row every 5 s): the mind consumed the rows up to `lived_h` (its moment
    rows, a think every 10 canvases, a sleep every 180); the body snapshotted every 20 wall minutes up to `snapshots_until_h`."""
    t0 = datetime(2026, 9, 23, 0, 0, tzinfo=timezone.utc)
    tape, mind, seq = [], [], 0
    for i in range(int(world_h * 3600 / 5)):
        t = t0 + timedelta(seconds=5 * i + 1)
        if hole_at_h is not None and abs((t - t0).total_seconds() - hole_at_h * 3600) < 45:
            continue                                                   # a 90 s hole in both senses
        for sense in ("ear", "eye"):
            seq += 1; tape.append({"seq": seq, "at": _z(t), "sense": sense, "meta": {"moment": f"w0000-{i}"}})
        if (t - t0).total_seconds() <= lived_h * 3600:
            mind.append({"seq": seq, "moment": f"w0000-{i}"})
            if i % 10 == 0:
                mind.append({"seq": seq, "think": {"kind": "word"}})
            if i % 180 == 0 and int((t - t0).total_seconds() // 3600) != drop_sleeps_in_hour:
                mind.append({"seq": seq, "sleep": {}})
    events = ([{"seq": None, "at": _z(t0), "event": "start"}]
              + [{"seq": None, "at": _z(t0 + timedelta(minutes=20 * k + 1)), "event": "snapshot"} for k in range(int(snapshots_until_h * 3))]
              + [{"seq": None, "at": _z(t0 + timedelta(hours=world_h, minutes=1)), "event": "stop"}])
    M = max(int(r["seq"]) for r in mind)
    cut = M < tape[-1]["seq"]
    tape_cut = [r for r in tape if r["seq"] <= M]
    h = lambda r: (datetime.fromisoformat(r["at"].replace("Z", "+00:00")) - t0).total_seconds() / 3600
    lag = {"cut": cut, "mind_last_seq": M, "source": "status", "time_cut_seq": tape[-1]["seq"], "tape_head_seq": tape[-1]["seq"], "cut_seq": M,
           "rows_unconsumed": tape[-1]["seq"] - M, "rows_cut_by_lag": tape[-1]["seq"] - M, "hours_lived": round(h(tape_cut[-1]), 4),
           "world_hours_unconsumed": round(h(tape[-1]) - h(tape_cut[-1]), 4), "world_hours_cut_by_lag": round(h(tape[-1]) - h(tape_cut[-1]), 4),
           "backlog_series": {"n": 0, "max": None, "last": None, "first_over_100": None}}
    return {"t0": t0, "t_cut": t0 + timedelta(hours=world_h), "tape": tape_cut, "tape_world": tape, "mind": mind, "events": events,
            "status": {}, "exams": [], "mind_events": [], "lag": lag, "closed_whole": True, "last_seq": M,
            "hours_on_tape": h(tape_cut[-1]), "hours_on_tape_world": h(tape[-1])}


class AliveUnderALag(unittest.TestCase):
    def test_a_mind_behind_its_world_is_alive_and_its_lag_is_printed(self):
        a = vg.alive(synthetic_G(), 3.0, 0)
        self.assertTrue(a["pass"], a)
        self.assertEqual(a["hours_on_tape"], round(synthetic_G()["hours_on_tape_world"], 3), "the hours on the tape are the world's")
        self.assertEqual((a["mind_reach_full_hours"], a["hours_beyond_the_minds_reach"]), (2, [2]))
        self.assertTrue(a["lag"]["cut_at_mind_last_seq"]); self.assertGreater(a["lag"]["rows_unconsumed"], 0)

    def test_a_mind_that_stopped_moving_still_fails(self):
        a = vg.alive(synthetic_G(snapshots_until_h=2.0), 3.0, 0)          # no snapshot in wall hour 2
        self.assertFalse(a["pass"]); self.assertFalse(a["every_counter_moved_every_hour"])

    def test_a_dead_sense_in_the_unconsumed_tail_still_fails(self):
        a = vg.alive(synthetic_G(hole_at_h=2.7), 3.0, 0)                  # a 90 s hole after the mind's last seq (2.4 h)
        self.assertFalse(a["pass"]); self.assertGreater(max(a["max_gap_s_eye_ear"]), 60.0)

    def test_without_a_lag_the_bar_reads_as_before(self):
        a = vg.alive(synthetic_G(lived_h=3.0), 3.0, 0)
        self.assertTrue(a["pass"]); self.assertNotIn("mind_reach_full_hours", a)
        b = vg.alive(synthetic_G(lived_h=3.0, drop_sleeps_in_hour=1), 3.0, 0)   # an hour with no sleep fails, as it always did
        self.assertFalse(b["pass"])
        c = vg.alive(synthetic_G(drop_sleeps_in_hour=1), 3.0, 0)                # …and inside the mind's reach under a lag too
        self.assertFalse(c["pass"])


class CostPrintsTheLag(unittest.TestCase):
    LS = {"cut_at_mind_last_seq": True, "mind_last_seq": 410, "rows_unconsumed": 100, "rows_cut_by_lag": 100, "backlog_max": 150}

    def test_both_forms_carry_the_lag_and_the_old_callers_do_not(self):
        st = {"rss_mb": 900.0, "mind_ms_per_canvas_1min": 2433.0, "cells": 7030}
        m = vg.viii_cost(st, 21.0, 85.0, None, grow=True, lag=self.LS)
        self.assertEqual(m["lag"], self.LS); self.assertIs(m["graded"], True)
        self.assertFalse(m["pass"], "2,433 ms at 7,030 cells is over §8b's 1.5 × 0.09 × cells — the bar is untouched by the lag print")
        self.assertEqual(vg.viii_cost(st, 13.0, 39.0, None, lag=self.LS)["lag"], self.LS)
        self.assertNotIn("lag", vg.viii_cost(st, 21.0, 85.0, None, grow=True))


if __name__ == "__main__":
    unittest.main()
