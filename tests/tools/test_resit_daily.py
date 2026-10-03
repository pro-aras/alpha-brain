# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:45 +0400 — PREREG-RESIT-READER (law v4 text, signed ×3): the ORCHESTRATOR in DAILY mode — one series row a day from a COPY of the live life's state/prev, answered on the
# fixed items of a CLOSED life, graded by the pinned grader, tabled by phrase class (§2), vectored by item name, paired against the ORIGIN (§4), with the genome in force at the copy's last seq (§1.2 S1),
# EYE-CHANGED's two forms, the verdict-copy flag, the restarts between the origin and the copy, and every refusal a ROW with exit 0 (a timer must not loop). Written BEFORE the mode.
# The life is a STUB (a tiny code tree, the stub items life of test_resit_gate, a live root holding only what a daily run reads). Every plant asserts it changed the bytes (#247 (5)).
"""tests/tools/test_resit_daily.py — daily mode on a stub live life and a stub closed items life."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tests.tools.test_resit import Tmp, brain, epoch_row, write_journal
from tests.tools.test_resit_children import ENV, GENOME, RESIT_PY, build_stub, last_json, write_state
from tests.tools.test_resit_gate import GENOME_V1, StubLife, write_snapshot
from tools.brain import resit as R

# ------------------------------------------------------------------------------------------------ a stub grader with the internals grader_m2a_rows calls
STUB_GRADER_DAILY = '''
import json
from pathlib import Path


class Life:
    def __init__(self, root, journal, genome=None):
        rows = [json.loads(l) for l in Path(journal).read_text().splitlines() if l.strip()]
        self.answers = [r for r in rows if r.get("kind") == "answer"]
        self.cfg = {"sitting": ["fresh", "s1b1"]}


class SetCtx:
    def __init__(self, life, tset):
        self.items = {"M2a": [{"item_id": r["item"]} for r in life.answers if r["mark"] == "M2a" and (":%s:" % tset) in r["item"]]}


def offline_answers(life, sc):
    return {"point": {r["item"]: {"hyp": r["answer"]["hyp"]} for r in life.answers if r["mark"] == "M2a"}, "m2a_keys": {"LAW": "none_i"}}


class M:
    @staticmethod
    def grade_m2a(items, answers, key):
        a = answers.get(items[0]["item_id"])
        return {"all": {"n": 1 if a is not None else 0, "refusal": 1.0 if (a is not None and a["hyp"] == 1) else 0.0}}


def _rate(xs):
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def grade(root, journal, scored, label, genome=None):
    rows = [json.loads(l) for l in Path(journal).read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r.get("kind") == "answer"]
    pts = [r for r in rows if r["form"] == "point"]
    sets, items = {}, {}
    for s in ("fresh", "s1b1"):
        sel = [r for r in pts if (":%s:" % s) in str(r["item"])]
        m1 = [r for r in sel if r["mark"] == "M1"]
        m2 = [r for r in sel if r["mark"] == "M2a"]
        sets[s] = {"n_items": {"M1": len(m1), "M2a": len(m2), "M3": 0},
                   "marks": {"M1": {"graded": {"n_covered": len(m1), "covered": _rate(r["answer"]["hyp"] == 0 for r in m1)}},
                             "M3": {"all": {"n_covered": 0, "covered": None}},
                             "roads": {"LAW": {"M2a": {"all": {"n": len(m2), "refusal": _rate(r["answer"]["hyp"] == 1 for r in m2)}}}}}}
        items[s] = {"M1": [{"item_id": r["item"], "gradable": True, "covered": True, "correct": r["answer"]["hyp"] == 0} for r in m1], "M3": [], "M6": []}
    return {"label": label, "root": str(root), "counts": {"tape_rows": len(rows)}, "sets": sets, "items": items,
            "M5": {"n": 0, "refused": None, "rows": []}, "M6_pooled": {"covered": 0.5}, "meeting": {"read_by": "stub"}}
'''


def write_live(base: Path, name: str = "live", *, v=(1.0, 2.0, 3.0), n_learned: int = 10, last_seq: int = 7000, epochs=(), starts=(), torn_tail: bool = False,
               status: dict = None) -> Path:
    """A stub LIVE root holding only what a daily run reads: state/prev (+ SNAPSHOT.json), GENOME.genome (+ GENOME.v<k>), a journal with epoch and start rows, STATUS.json."""
    root = base / name
    root.mkdir()
    (root / "GENOME.genome").write_text(GENOME)
    prev = write_state(root / "state" / "prev", v=v, n_learned=n_learned, calibrated_at=n_learned)
    write_snapshot(prev, last_seq=last_seq)
    rows = [{"seq": None, "at": "2026-10-03T10:00:00.000Z", "event": "start", "resumed_from_seq": 0}]
    rows.extend(starts)
    for seq, k, text in epochs:
        (root / f"GENOME.v{k}.genome").write_text(text)
        rows.append(epoch_row(seq, k, text))
    write_journal(root, rows)
    if torn_tail:
        with (root / "journal" / "2026-10-03.jsonl").open("a") as f:
            f.write('{"kind": "brain", "act": "learn", "seq": 99999, "moment": "m')          # a live file's half-written last line
    if status is not None:
        (root / "STATUS.json").write_text(json.dumps(status))
    return root


class DailyBase(Tmp):
    def setUp(self) -> None:
        self.base = self.mk("resit-daily-")
        self.items = StubLife(self.base)
        (self.items.grader / "tools" / "brain" / "grade_life.py").write_text(STUB_GRADER_DAILY)
        self.out = self.base / "out-daily"

    def daily(self, live: Path, *extra: str, stamp: str = "20261004T000000Z", flags=("-B", "-I"), env_over: dict = None, out: Path = None):
        args = [sys.executable, *flags, str(RESIT_PY), "run", "--mode", "daily", "--root", str(live), "--code", str(self.items.code), "--items-root", str(self.items.root),
                "--grader-code", str(self.items.grader), "--out", str(out or self.out), "--scored", str(self.items.scored), "--stamp", stamp, "--copy-retry-sleep-s", "0"]
        args += list(extra)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(ENV)
        env.update(env_over or {})
        p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(self.base))
        return p, last_json(p.stdout), self.series(out or self.out)

    @staticmethod
    def series(out: Path) -> list:
        f = out / "RESIT.jsonl"
        return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []

    def write_origin_from(self, row: dict, *, fresh_n_learned: int = 5, begin_seq: int = 1003, lines: dict = None, vectors: dict = None) -> None:
        """What the origin mode will write (law §4.1): the origin row is the same shape as a daily row plus its provenance. Here a stand-in made from a first day's own vectors."""
        R.write_origin(self.out, {"kind": "origin", "stamp": "20261003T000000Z", "origin_kind": "rebuilt", "reason": None, "vectors": vectors or row["vectors"], "item_class": row["item_class"],
                                  "genome_lines": lines or row["genome"]["lines"], "origin_n_learned_fresh_begin": fresh_n_learned, "begin_seq_fresh": begin_seq})


class TestDailyRow(DailyBase):
    def test_a_first_daily_row_with_no_origin_says_so_and_pairs_nothing(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual((r["kind"], r["stamp"]), ("daily", "20261004T000000Z"))
        self.assertIsNone(r["vs_origin"])
        self.assertIn("NO ORIGIN", r["vs_origin_note"])
        self.assertIsNone(r["post_origin_learned"])
        self.assertFalse((self.out / "ORIGIN.json").exists(), "a daily run is never an origin (R8 b)")
        self.assertNotIn("verdict_copy", r)

    def test_the_row_carries_the_state_the_items_the_tables_the_partition_and_the_vectors(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r = rows[0]
        self.assertEqual(r["reader_sha256"], hashlib.sha256(Path(RESIT_PY).read_bytes()).hexdigest())
        self.assertEqual(r["flags"]["OPENBLAS_NUM_THREADS"], "1")
        self.assertEqual((r["state"]["last_seq"], r["state"]["n_learned"], r["state"]["prints_ok"]), (7000, 10, True))
        self.assertEqual(r["items"]["n_asks"], 10)
        self.assertTrue(r["partition"]["ok"], r["partition"])
        t = r["marks"]["M1"]
        self.assertEqual(set(t), {"sets", "pooled"})
        self.assertEqual(t["pooled"]["colour_or_size"]["n"] + t["pooled"]["shape_only"]["n"] + t["pooled"]["white"]["n"], 2)
        self.assertTrue(t["pooled"]["shape_only"]["na"], "the stub items hold no shape-only M1 item: n/a, never 0")
        self.assertEqual(set(r["vectors"]), {"M1", "M2a"})
        self.assertEqual(len(r["vectors"]["M1"]), 2)
        self.assertEqual(r["item_class"]["M1:fresh:0"], "colour_or_size")
        self.assertEqual(r["m6_reading"]["read_by"], "stub")
        self.assertGreater(r["memory"]["answer_maxrss_mb"], 1)
        self.assertGreater(r["cpu"]["answer_s"], 0)
        self.assertEqual((r["cpu"]["cap_s"], r["cpu"]["cold"]), (1800, True), "the first run has no glance cache: cold, the 30 CPU-min cap")

    def test_the_grade_child_is_given_the_items_genome_and_the_answer_child_the_lifes_in_force_genome_v4(self) -> None:
        live = write_live(self.base, last_seq=7000, epochs=[(6000, 1, GENOME_V1)])
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        d = self.out / "days" / "20261004T000000Z"
        gs = json.loads((d / "grade-spec.json").read_text())
        as_ = json.loads((d / "answer-spec.json").read_text())
        self.assertEqual(gs["genome"], str(self.items.root / "GENOME.genome"), "ONE grader configuration: the pinned items genome, never the life's")
        self.assertEqual(gs["scored"], str(self.items.scored))
        self.assertTrue(gs["m2a_rows"], "the per-item M2a rows the pairing needs")
        self.assertEqual(as_["states"][0]["genome"], str(live / "GENOME.v1.genome"), "the brain is loaded under the genome in force at its copy")
        self.assertEqual(as_["items_root"], str(self.items.root))
        self.assertEqual(as_["states"][0]["dir"], str(d / "copy"), "the brain is read from the COPY, never from state/prev in place")

    def test_the_answers_and_the_grade_are_kept_and_their_sha256_is_in_the_row_A4(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        d = self.out / "days" / "20261004T000000Z"
        for name, key in (("answers.jsonl", "answers_sha256"), ("grade.json", "grade_sha256")):
            self.assertTrue((d / name).exists(), name)
            self.assertEqual(rows[0][key], hashlib.sha256((d / name).read_bytes()).hexdigest(), key)

    def test_the_restart_duplicates_of_the_items_roots_journal_are_counted_in_the_row_AM1_d(self) -> None:
        self.items.rewrite_journal(lambda rows: rows + [dict(next(r for r in rows if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0"))])
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(rows[0]["restart_duplicates"], 1)

    def test_a_second_day_appends_a_second_line_and_the_md_is_rewritten_from_the_whole_series(self) -> None:
        live = write_live(self.base)
        self.daily(live, stamp="20261004T000000Z")
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual([r["stamp"] for r in rows], ["20261004T000000Z", "20261005T000000Z"])
        self.assertEqual((rows[1]["cpu"]["cap_s"], rows[1]["cpu"]["cold"]), (480, False), "the second run is warm: the 8 CPU-min cap")
        self.assertEqual(rows[1]["answer_meta"]["glance_cache"]["hits"], 2)
        md = (self.out / "RESIT.md").read_text()
        self.assertIn("20261004T000000Z", md)
        self.assertIn("20261005T000000Z", md)

    def test_the_nothing_written_check_covers_the_closed_items_root_and_says_it_does_not_cover_a_live_root(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        nw = rows[0]["nothing_written"]
        self.assertTrue(nw["checked"])
        self.assertEqual(nw["n_newer"], 0)
        self.assertEqual(nw["roots"], [str(self.items.root.resolve())])
        self.assertIn("live", nw["scope"])

    def test_the_status_of_the_live_life_is_read_at_the_start_and_the_end_R12(self) -> None:
        live = write_live(self.base, status={"mind_backlog_rows": 9, "mind_ms_per_canvas_1min": 55.5})
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        for when in ("start", "end"):
            self.assertEqual((rows[0]["live_load"][when]["mind_backlog_rows"], rows[0]["live_load"][when]["mind_ms_per_canvas_1min"]), (9, 55.5))

    def test_the_copy_is_of_state_prev_and_the_life_is_not_written(self) -> None:
        live = write_live(self.base)
        before = {str(p.relative_to(live)): (p.stat().st_size, p.stat().st_mtime_ns) for p in live.rglob("*") if p.is_file()}
        p, res, rows = self.daily(live)
        after = {str(p.relative_to(live)): (p.stat().st_size, p.stat().st_mtime_ns) for p in live.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "the live root is only read")
        self.assertTrue((self.out / "days" / "20261004T000000Z" / "copy" / "brain.npz").exists())


class TestDailyGenome(DailyBase):
    def test_the_genome_in_force_is_the_epoch_at_or_before_the_copys_last_seq_S1(self) -> None:
        live = write_live(self.base, last_seq=7000, epochs=[(6000, 1, GENOME_V1)])
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        g = rows[0]["genome"]
        self.assertEqual(g["epoch"], 1)
        self.assertEqual(g["sha256"], hashlib.sha256(GENOME_V1.encode()).hexdigest())

    def test_an_epoch_after_the_copys_last_seq_is_not_in_force(self) -> None:
        live = write_live(self.base, last_seq=7000, epochs=[(8000, 1, GENOME_V1)])
        p, res, rows = self.daily(live)
        self.assertEqual(rows[0]["genome"]["epoch"], 0)

    def test_the_grader_genome_is_the_items_genome_and_both_sets_of_hashes_are_printed_v4(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        g = rows[0]["genome"]
        self.assertEqual(g["grader"]["path"], str(self.items.root / "GENOME.genome"))
        self.assertEqual(g["grader"]["sha256"], hashlib.sha256(GENOME.encode()).hexdigest())
        self.assertEqual(set(g["lines"]), set(g["grader"]["lines"]))
        self.assertEqual(set(g["lines"]), {"retina", "gaze", "colour", "brain", "genome", "world_scene", "tape"})
        self.assertFalse(g["eye"]["eye_changed"])
        self.assertIsNone(g["eye"]["within_life"], "no origin yet: form (i) is undetermined")
        self.assertFalse(rows[0]["eye_changed"])

    def test_a_life_whose_eye_differs_from_the_grader_genome_reads_eye_changed_form_ii_and_is_still_written(self) -> None:
        live = write_live(self.base)
        g = live / "GENOME.genome"
        before = g.read_bytes()
        g.write_text(g.read_text().replace("GAZE g 4", "GAZE g 5"))
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r = rows[0]
        self.assertTrue(r["eye_changed"])
        self.assertIn("gaze", r["genome"]["eye"]["against_grader_lines"])
        self.assertNotIn("refused", r)


class TestDailyPairing(DailyBase):
    def test_a_day_is_paired_against_the_origin_by_item_and_a_planted_difference_is_read(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live, stamp="20261004T000000Z")
        planted = json.loads(json.dumps(rows[0]["vectors"]))
        item = "M1:fresh:0"
        self.assertIn(planted["M1"][item], (0, 1))
        planted["M1"][item] = 1 - planted["M1"][item]                       # the origin read this item the other way: exactly one discordant pair
        self.assertNotEqual(planted, rows[0]["vectors"], "the plant must change the vectors")
        self.write_origin_from(rows[0], vectors=planted)
        p, res, rows = self.daily(live, stamp="20261005T000000Z")           # the SAME brain again: the only difference is the origin's planted item
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r = rows[1]
        m1 = r["vs_origin"]["M1"]["pooled"]
        self.assertEqual((m1["n_paired"], m1["b"] + m1["c"], m1["discordant"]), (2, 1, 1))
        day_right = r["vectors"]["M1"][item] == 1
        self.assertEqual((m1["c"], m1["b"]), (1, 0) if day_right else (0, 1), "right now and wrong at the origin is c; wrong now and right at the origin is b")
        self.assertAlmostEqual(m1["g"], (m1["c"] - m1["b"]) / 2)
        self.assertEqual(m1["smallest_gap"], 10 / 2)
        self.assertEqual(r["vs_origin_note"], "")
        self.assertEqual(r["vs_origin"]["M2a"]["pooled"]["discordant"], 0, "the other mark is untouched")

    def test_post_origin_learned_and_the_restarts_between_the_origin_and_the_copy_are_printed_A3_4(self) -> None:
        starts = [{"seq": None, "at": "t", "event": "start", "resumed_from_seq": 1200},      # inside (1003, 7000]
                  {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 500},       # before the origin's fresh-begin seq: outside
                  {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 7500}]      # after the copy's last_seq: outside
        live = write_live(self.base, n_learned=60, starts=starts)
        p, res, rows = self.daily(live, stamp="20261004T000000Z")
        self.write_origin_from(rows[0], fresh_n_learned=11, begin_seq=1003)
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        r = rows[1]
        self.assertEqual(r["post_origin_learned"], 60 - 11)
        self.assertEqual([x["resumed_from_seq"] for x in r["restarts_between"]["restarts"]], [1200])
        self.assertEqual(r["restarts_between"]["start_rows_seen"], 4)

    def test_the_verdict_copy_flag_fires_on_the_first_row_at_8640_and_on_no_other(self) -> None:
        live = write_live(self.base, n_learned=9000)
        p, res, rows = self.daily(live, stamp="20261004T000000Z")
        self.write_origin_from(rows[0], fresh_n_learned=100)
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        self.assertEqual(rows[1]["post_origin_learned"], 8900)
        self.assertTrue(rows[1].get("verdict_copy"))
        p, res, rows = self.daily(live, stamp="20261006T000000Z")
        self.assertNotIn("verdict_copy", rows[2], "only the FIRST row at or above 8,640 is the verdict copy")
        live_small = write_live(self.base, "live-small", n_learned=9)
        p, res, rows2 = self.daily(live_small, stamp="20261007T000000Z", out=self.base / "out-other")
        self.assertNotIn("verdict_copy", rows2[0])

    def test_an_eye_changed_row_is_labelled_its_pairing_is_a_reading_and_no_verdict_copy_is_taken_AM2(self) -> None:
        live = write_live(self.base, n_learned=9000)
        p, res, rows = self.daily(live, stamp="20261004T000000Z")
        planted = dict(rows[0]["genome"]["lines"])
        planted["retina"] = "0" * 64                                          # the origin's RETINA line differs from this row's: form (i)
        self.assertNotEqual(planted, rows[0]["genome"]["lines"], "the plant must change the lines")
        self.write_origin_from(rows[0], fresh_n_learned=100, lines=planted)
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        r = rows[1]
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertTrue(r["eye_changed"])
        self.assertTrue(r["genome"]["eye"]["within_life"])
        self.assertIn("retina", r["genome"]["eye"]["within_life_lines"])
        self.assertIn("EYE-CHANGED", r["vs_origin_label"])
        self.assertIsNotNone(r["vs_origin"], "the pairing is still printed, only as a labelled reading")
        self.assertNotIn("verdict_copy", r)
        self.assertEqual(r["verdict_copy_note"], "verdict copy NOT taken: EYE-CHANGED")


class TestDailyRefusals(DailyBase):
    def test_a_missing_state_prev_is_a_skipped_row_and_exit_0(self) -> None:
        live = write_live(self.base)
        shutil.rmtree(live / "state")
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(len(rows), 1)
        self.assertIn("state/prev", rows[0]["skipped"])
        self.assertEqual(rows[0]["kind"], "daily")

    def test_a_state_whose_prints_do_not_match_is_a_refused_row_and_exit_0_R4b(self) -> None:
        live = write_live(self.base)
        f = live / "state" / "prev" / "brain.json"
        st = f.stat()
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
        self.assertNotEqual(f.stat().st_mtime_ns, st.st_mtime_ns, "the plant must change the mtime")
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("mtime_ns", rows[0]["refused"])

    def test_a_flipped_byte_in_the_brain_is_a_refused_row_and_exit_0_R4a(self) -> None:
        import numpy as np
        live = write_live(self.base)
        f = live / "state" / "prev" / "brain.npz"
        st = f.stat()
        data = bytearray(f.read_bytes())
        at = bytes(data).find(np.array([1.0, 2.0, 3.0]).tobytes())
        self.assertGreaterEqual(at, 0)
        data[at + 3] ^= 0xFF
        f.write_bytes(bytes(data))
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns))
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("Brain.load refused", rows[0]["refused"])

    def test_a_genome_whose_sha_is_not_the_epoch_rows_is_a_refused_row_R4e(self) -> None:
        live = write_live(self.base, last_seq=7000, epochs=[(6000, 1, GENOME_V1)])
        g = live / "GENOME.v1.genome"
        before = g.read_bytes()
        g.write_text(g.read_text() + "# a hand edit\n")
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("genome_sha", rows[0]["refused"])

    def test_genome_v1_with_its_epoch_rows_deleted_is_undetermined_and_a_refused_row_R4f(self) -> None:
        live = write_live(self.base, last_seq=7000, epochs=[(6000, 1, GENOME_V1)])
        j = live / "journal" / "2026-10-03.jsonl"
        rows_ = [json.loads(l) for l in j.read_text().splitlines()]
        j.write_text("\n".join(json.dumps(r) for r in rows_ if not isinstance(r.get("epoch"), dict)) + "\n")
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("undetermined", rows[0]["refused"])

    def test_a_changed_grader_is_a_refused_row_R4j(self) -> None:
        live = write_live(self.base)
        self.daily(live, stamp="20261004T000000Z")
        g = self.items.grader / "tools" / "brain" / "grade_life.py"
        before = g.read_bytes()
        g.write_text(g.read_text() + "\n# another grader\n")
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("grader pin", rows[1]["refused"])
        self.assertFalse((self.out / "days" / "20261005T000000Z" / "answers.jsonl").exists(), "the grader's pin is checked BEFORE any child is spent")

    def test_changed_sittings_are_a_refused_row_the_series_is_about_the_pinned_items_R4(self) -> None:
        live = write_live(self.base)
        self.daily(live, stamp="20261004T000000Z")
        first = sorted((self.items.root / "tape" / "payload").glob("*.json"))[1]
        before = first.read_bytes()
        first.write_text(first.read_text().replace('"test_seed": 7', '"test_seed": 8'))
        self.assertNotEqual(before, first.read_bytes(), "the plant must change the bytes")
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("payload", rows[1]["refused"])

    def test_a_grade_whose_aggregate_disagrees_with_its_items_is_a_refused_row_R6(self) -> None:
        g = self.items.grader / "tools" / "brain" / "grade_life.py"
        before = g.read_bytes()
        g.write_text(g.read_text().replace('"covered": _rate(r["answer"]["hyp"] == 0 for r in m1)}}', '"covered": 0.123}}'))
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("R6 PARTITION", rows[0]["refused"])
        self.assertNotIn("vectors", rows[0], "a row that fails its partition carries no vectors to pair")

    def test_a_graded_item_the_tape_never_asked_has_no_class_and_is_refused_by_name_never_binned_R6(self) -> None:
        g = self.items.grader / "tools" / "brain" / "grade_life.py"
        before = g.read_bytes()
        g.write_text(g.read_text().replace('for r in m1], "M3": [], "M6": []}',
                                           'for r in m1] + [{"item_id": "M1:ghost", "gradable": True, "covered": True, "correct": True}], "M3": [], "M6": []}'))
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("M1:ghost", rows[0]["refused"])
        self.assertIn("no phrase class", rows[0]["refused"])

    def test_a_changed_items_pin_is_a_refused_row_the_pin_is_checked_every_day(self) -> None:
        live = write_live(self.base)
        self.daily(live, stamp="20261004T000000Z")
        pin = json.loads((self.out / "ITEMS.json").read_text())
        pin["ask_digest"] = "0" * 64
        (self.out / "ITEMS.json").write_text(json.dumps(pin))
        p, res, rows = self.daily(live, stamp="20261005T000000Z")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("items pin", rows[1]["refused"])
        self.assertIn("ask_digest", rows[1]["refused"])

    def test_a_run_without_dash_B_is_a_refused_row_and_exit_0_in_daily_mode(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live, flags=("-I",))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(len(rows), 1)
        self.assertIn("-B", rows[0]["refused"])

    def test_the_cpu_cap_is_a_refused_row_and_exit_0(self) -> None:
        live = write_live(self.base)
        p, res, rows = self.daily(live, "--cpu-cap-s", "1", env_over={"STUB_BURN_S": "4"})
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("R7", rows[0]["refused"])

    def test_an_item_with_no_phrase_class_cannot_be_binned_the_tape_refuses_a_phrase_of_no_type_R6(self) -> None:
        shutil.rmtree(self.items.root / "tape")
        from tests.tools.test_resit import write_tape
        from tests.tools.test_resit_children import sitting_spec
        spec = []
        for it in sitting_spec():
            if it[0] == "ask" and it[2].get("item") == "M1:fresh:0":
                it = ("ask", it[1], {**it[2], "phrase": ["zog", "circle"]})                    # a word of NO type
            spec.append(it)
        write_tape(self.items.root, spec, seq0=1000)
        live = write_live(self.base)
        p, res, rows = self.daily(live)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertIn("zog", rows[0]["refused"])
        self.assertIn("no type", rows[0]["refused"])


class TestLiveJournalRead(Tmp):
    def test_a_half_written_last_line_of_a_live_journal_does_not_stop_the_epoch_and_start_scan(self) -> None:
        base = self.mk("resit-live-")
        live = write_live(base, last_seq=7000, epochs=[(6000, 1, GENOME_V1)], starts=[{"seq": None, "at": "t", "event": "start", "resumed_from_seq": 1200}], torn_tail=True)
        sc = R.scan_life_events(live / "journal")
        self.assertEqual([e["epoch"] for e in sc["epochs"]], [1])
        self.assertEqual(sorted(s["resumed_from_seq"] for s in sc["starts"]), [0, 1200])
        self.assertEqual(sc["torn_lines"], 1)

    def test_only_epochs_and_starts_are_kept_a_live_journal_is_not_loaded_into_memory(self) -> None:
        base = self.mk("resit-live-")
        live = write_live(base)
        write_journal(live, [{"kind": "brain", "act": "learn", "seq": i, "moment": "m", "at": "t"} for i in range(500)])
        sc = R.scan_life_events(live / "journal")
        self.assertEqual(set(sc), {"epochs", "starts", "torn_lines", "lines_read"})
        self.assertGreaterEqual(sc["lines_read"], 500)


if __name__ == "__main__":
    import unittest
    unittest.main()
