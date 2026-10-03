# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:00 +0400 — PREREG-RESIT-READER (law text b02cf10, sha256 f6390b0d…, signed ×3): the ORCHESTRATOR in GATE mode (R1, R1′) and its pure
# helpers (R1 (a) the row comparison, R1 (b) the marks comparison, R5 (b) the empty `find`, R12 the live STATUS reading, the grader pin R4 (j), the CPU cap R7, the two refusals of §1.0),
# written BEFORE the orchestrator. The life is a STUB (a tiny code tree, two sittings, a journal written by running the ANSWER child as the life would); the real life is R1 itself.
# Every plant asserts that it changed the bytes (#247 (5)) and is CAUGHT.
"""tests/tools/test_resit_gate.py — the re-sit reader's orchestrator, gate mode, on a stub life."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

import numpy as np

from tests.tools.test_resit import Tmp, ans, brain, epoch_row, write_journal, write_tape
from tests.tools.test_resit_children import ENV, GENOME, RESIT_PY, build_stub, last_json, png, run_child, sitting_spec, write_state
from tools.brain import resit as R

GENOME_V1 = GENOME + "KWTA 4\n"              # epoch 1: the same four eye/brain lines, one line EVOLVE may move


# ------------------------------------------------------------------------------------------------ the stub GRADER (the pinned grade_life.py's one function)
STUB_GRADER = '''
import json
from pathlib import Path


def _mean(xs):
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def grade(root, journal, scored, label, genome=None):
    rows = [json.loads(l) for l in Path(journal).read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r.get("kind") == "answer"]            # as the real grader's Life: the answer rows of a journal that holds other rows too
    pts = [r for r in rows if r["form"] == "point"]
    sets, items = {}, {}
    for s in ("fresh", "s1b1"):
        sel = [r for r in pts if (":%s:" % s) in str(r["item"])]
        m1 = [r for r in sel if r["mark"] == "M1"]
        m2 = [r for r in sel if r["mark"] == "M2a"]
        sets[s] = {"marks": {"M1": {"graded": {"n_covered": len(m1), "covered": _mean(r["answer"]["raw"]["p"] for r in m1)}},
                             "M3": {"all": {"n_covered": 0, "covered": None}},
                             "M6": {"stub": 1},
                             "roads": {"LAW": {"M2a": {"all": {"n": len(m2), "refusal": _mean(r["answer"]["raw"]["p"] for r in m2)}}}}}}
        items[s] = {"M1": [{"item_id": r["item"], "gradable": True, "covered": True, "correct": r["answer"]["hyp"] == 0} for r in m1],
                    "M3": [], "M6": []}
    return {"label": label, "root": str(root), "journal": str(journal), "counts": {"tape_rows": len(rows)}, "sets": sets, "items": items,
            "M5": {"n": 0, "refused": None, "rows": []}, "M6_pooled": {"covered": 0.5, "n_covered": 0}, "meeting": {"read_by": "stub"}}
'''


def stub_grade_of(journal: Path, root: Path = Path("/x")) -> dict:
    ns: dict = {}
    exec(compile(STUB_GRADER, "stub_grade_life", "exec"), ns)
    return ns["grade"](root, journal, Path("/none"), "ref")


def write_snapshot(prev: Path, last_seq: int = 9000, t: int = 5) -> None:
    prints = {}
    for n in ("brain.json", "brain.npz"):
        st = (prev / n).stat()
        prints[n] = [st.st_size, st.st_mtime_ns]
    (prev / "SNAPSHOT.json").write_text(json.dumps({"files": ["brain.json", "brain.npz"], "last_seq": last_seq, "prints": prints, "t": t}))


class StubLife:
    """A stub LIFE root on disk plus a stub grader checkout, an OUT dir, and the reference grade (the stub grader's own, on the life's journal)."""

    def __init__(self, base: Path, *, epoch_seq: int = None, extra_rows=(), state_calibrated_at: int = 10, tape_spec=None, genome: str = GENOME):
        self.base = base
        self.root = base / "life"
        self.root.mkdir()
        self.code = self.root / "code"
        build_stub(self.code)
        (self.root / "GENOME.genome").write_text(genome)
        write_tape(self.root, tape_spec or sitting_spec(), seq0=1000)          # ear 1001, eye 1002 (not a sitting), begin-fresh 1003, … (the first ask is 1003)
        self.prev = write_state(self.root / "state" / "prev", v=(1.0, 2.0, 3.0), n_learned=10, calibrated_at=state_calibrated_at)
        write_snapshot(self.prev)
        self.grader = base / "grader"
        (self.grader / "tools" / "brain").mkdir(parents=True)
        (self.grader / "tools" / "brain" / "grade_life.py").write_text(STUB_GRADER)
        self.out = base / "out"
        self.scored = base / "scored"
        self.scored.mkdir()
        # THE LIFE's own answers: the ANSWER child, run as the life ran it (the stub's code, the saved state, the life's genome)
        spec = {"code": str(self.code), "items_root": str(self.root), "tape_decl": "run/tape",
                "states": [{"name": "*", "dir": str(self.prev), "genome": str(self.root / "GENOME.genome")}],
                "out_dir": str(base / "life-answers"), "glance_cache": None, "check_turn": None}
        p = run_child("answer", spec, base)
        assert p.returncode == 0, p.stderr + p.stdout
        self.life_rows = [json.loads(l) for l in (base / "life-answers" / "answers.jsonl").read_text().splitlines()]
        rows = [brain(1002, "learn"), {"seq": None, "at": "2026-10-03T10:00:00.000Z", "event": "start", "resumed_from_seq": 0}] + self.life_rows
        if epoch_seq is not None:
            (self.root / "GENOME.v1.genome").write_text(GENOME_V1)
            rows.append(epoch_row(epoch_seq, 1, GENOME_V1))
        rows.extend(extra_rows)
        write_journal(self.root, rows)
        self.journal_file = self.root / "journal" / "2026-10-03.jsonl"
        self.ref = base / "ref-grade.json"
        self.ref.write_text(json.dumps(stub_grade_of(self.root / "journal" / "2026-10-03.jsonl", self.root), indent=1, sort_keys=True))

    def rewrite_journal(self, fn) -> None:
        rows = [json.loads(l) for l in self.journal_file.read_text().splitlines() if l.strip()]
        rows = fn(rows)
        self.journal_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def orch(life: StubLife, *extra: str, label: str = "r1", mode: str = "gate", flags=("-B", "-I"), env_over: dict = None, with_ref: bool = True,
         root=None, out=None, stamp: str = "20261003T000000Z"):
    args = [sys.executable, *flags, str(RESIT_PY), "run", "--mode", mode, "--root", str(root or life.root), "--code", str(life.code),
            "--items-root", str(life.root), "--grader-code", str(life.grader), "--out", str(out or life.out), "--scored", str(life.scored),
            "--label", label, "--stamp", stamp]
    if with_ref:
        args += ["--reference-grade", str(life.ref)]
    args += list(extra)
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update(ENV)
    env.update(env_over or {})
    p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(life.base))
    row_path = Path(out or life.out) / "gate" / label / "gate.json"
    row = json.loads(row_path.read_text()) if row_path.exists() else None
    return p, last_json(p.stdout), row


# ------------------------------------------------------------------------------------------------ R1 (a): the rows
class TestCompareAnswers(unittest.TestCase):
    def rows(self):
        return [ans(10, None, form="begin", mark=None), ans(11, "M1:a", eye_seq=13), ans(12, "M2a:b", eye_seq=13, mark="M2a")]

    def test_equal_rows_are_all_counted_equal_and_the_hash_field_is_set_aside(self) -> None:
        resit = self.rows()
        life = {r["seq"]: {**r, "hash": "chain-field"} for r in self.rows()}
        res = R.compare_answers(resit, life)
        self.assertEqual((res["n_resit"], res["n_equal"], res["n_diff"], res["n_missing_life_row"]), (3, 3, 0, 0))
        self.assertIsNone(res["first_diff"])

    def test_a_difference_in_one_key_is_found_and_the_first_one_is_printed_with_both_rows(self) -> None:
        resit = self.rows()
        life = {r["seq"]: dict(r) for r in self.rows()}
        life[12] = {**life[12], "answer": {"kind": "thing", "hyp": 2, "raw": {"p": 0.9}}}
        life[11] = {**life[11], "at": "2026-10-03T10:00:01.000Z"}
        self.assertNotEqual(R.canon(life[12]), R.canon(resit[2]), "the plant must change the bytes")
        res = R.compare_answers(resit, life)
        self.assertEqual((res["n_equal"], res["n_diff"]), (1, 2))
        fd = res["first_diff"]
        self.assertEqual((fd["seq"], fd["item"], fd["differing_keys"]), (11, "M1:a", ["at"]), "the LOWEST differing ask seq is the first")
        self.assertEqual(fd["resit"], resit[1])
        self.assertEqual(fd["life"], life[11])

    def test_an_extra_key_on_one_side_is_a_difference_the_key_sets_must_be_equal(self) -> None:
        resit = self.rows()
        life = {r["seq"]: dict(r) for r in self.rows()}
        life[10]["unexpected"] = 1
        res = R.compare_answers(resit, life)
        self.assertEqual(res["n_diff"], 1)
        self.assertIn("unexpected", res["first_diff"]["differing_keys"])

    def test_a_resit_row_with_no_life_row_is_counted_missing_and_a_life_row_not_resat_is_a_reading(self) -> None:
        resit = self.rows()
        life = {r["seq"]: dict(r) for r in self.rows()}
        del life[11]
        life[99] = ans(99, "M1:extra", eye_seq=100)
        res = R.compare_answers(resit, life)
        self.assertEqual((res["n_equal"], res["n_missing_life_row"], res["life_rows_not_resat"]), (2, 1, 1))
        self.assertFalse(res["all_equal"], "a missing life row is not an equal row")

    def test_the_comparison_is_over_the_json_round_trip_int_and_float_stay_different(self) -> None:
        a = ans(10, "x", answer={"kind": "thing", "hyp": 1, "raw": {"p": 1}})
        b = ans(10, "x", answer={"kind": "thing", "hyp": 1, "raw": {"p": 1.0}})
        self.assertFalse(R.compare_answers([a], {10: b})["all_equal"])
        self.assertTrue(R.compare_answers([a], {10: json.loads(json.dumps(a))})["all_equal"])


# ------------------------------------------------------------------------------------------------ R1 (b): the marks
def mk_grade(m1=0.98, n1=202, m2a=0.8525, m3=1.0, m5=0.99):
    sets = {s: {"marks": {"M1": {"graded": {"covered": m1, "n_covered": n1}}, "M3": {"all": {"covered": m3}},
                          "M6": {"x": 1}, "roads": {"LAW": {"M2a": {"all": {"n": 400, "refusal": m2a}}}}}} for s in ("fresh", "s1b1")}
    return {"sets": sets, "M5": {"n": 400, "refused": m5, "rows": [{"item_id": "a", "named": True}]}, "M6_pooled": {"covered": 0.05},
            "meeting": {"read_by": "x"}, "counts": {"tape_rows": 178579}}


class TestCompareMarks(unittest.TestCase):
    def test_identical_grades_are_equal_and_the_marks_compared_are_named(self) -> None:
        res = R.compare_marks(mk_grade(), mk_grade())
        self.assertTrue(res["equal"])
        self.assertGreater(res["n_leaves"], 8)
        self.assertEqual(res["diffs"], [])
        self.assertEqual(set(res["marks_compared"]), {"fresh.M1", "fresh.M2a", "fresh.M3", "s1b1.M1", "s1b1.M2a", "s1b1.M3", "M5"})

    def test_a_float_within_1e_minus_12_passes_and_one_beyond_it_fails_naming_its_path(self) -> None:
        self.assertTrue(R.compare_marks(mk_grade(m1=0.98 + 5e-13), mk_grade())["equal"])
        g = mk_grade(m1=0.98 + 2e-12)
        self.assertNotEqual(g["sets"]["fresh"]["marks"]["M1"], mk_grade()["sets"]["fresh"]["marks"]["M1"], "the plant must change the bytes")
        res = R.compare_marks(g, mk_grade())
        self.assertFalse(res["equal"])
        self.assertIn("sets.fresh.marks.M1.graded.covered", [d["path"] for d in res["diffs"]])

    def test_m6_counts_and_meeting_are_readings_never_compared(self) -> None:
        g = mk_grade()
        g["M6_pooled"] = {"covered": 0.9}
        g["meeting"] = {"read_by": "the grader's own look"}
        g["counts"] = {"tape_rows": 331616}
        g["sets"]["fresh"]["marks"]["M6"] = {"x": 2}
        self.assertTrue(R.compare_marks(g, mk_grade())["equal"])

    def test_a_missing_key_a_missing_set_and_a_changed_m5_row_are_each_a_difference(self) -> None:
        g = mk_grade()
        del g["sets"]["fresh"]["marks"]["roads"]["LAW"]["M2a"]["all"]["refusal"]
        self.assertFalse(R.compare_marks(g, mk_grade())["equal"])
        g = mk_grade()
        del g["sets"]["s1b1"]
        self.assertFalse(R.compare_marks(g, mk_grade())["equal"])
        g = mk_grade()
        g["M5"]["rows"][0]["named"] = False
        res = R.compare_marks(g, mk_grade())
        self.assertFalse(res["equal"])
        self.assertTrue(any(d["path"].startswith("M5.rows") for d in res["diffs"]))

    def test_nan_equals_nan_and_a_bool_is_not_an_int(self) -> None:
        g, h = mk_grade(m1=float("nan")), mk_grade(m1=float("nan"))
        self.assertTrue(R.compare_marks(g, h)["equal"])
        g, h = mk_grade(), mk_grade()
        g["sets"]["fresh"]["marks"]["M3"]["all"]["covered"] = True
        h["sets"]["fresh"]["marks"]["M3"]["all"]["covered"] = 1
        self.assertFalse(R.compare_marks(g, h)["equal"])


# ------------------------------------------------------------------------------------------------ R5 (b), R12, the grader pin
class TestNewerThan(Tmp):
    def test_an_untouched_tree_lists_nothing_and_a_new_file_or_a_touched_directory_is_listed(self) -> None:
        d = self.mk("resit-find-")
        (d / "sub").mkdir()
        (d / "sub" / "a.txt").write_text("a")
        time.sleep(0.02)
        marker_ns = time.time_ns()
        time.sleep(0.02)
        res = R.newer_than([d], marker_ns)
        self.assertEqual((res["n_newer"], res["listed"]), (0, []))
        self.assertGreater(res["n_entries_walked"], 2)
        (d / "sub" / "new.pyc").write_text("x")
        res = R.newer_than([d], marker_ns)
        self.assertGreaterEqual(res["n_newer"], 1)
        self.assertTrue(any(p.endswith("new.pyc") for p in res["listed"]))

    def test_the_listing_is_capped_but_the_count_is_not(self) -> None:
        d = self.mk("resit-find-")
        marker_ns = time.time_ns()
        time.sleep(0.02)
        for i in range(30):
            (d / f"f{i}").write_text("x")
        res = R.newer_than([d], marker_ns, limit=5)
        self.assertGreaterEqual(res["n_newer"], 30)
        self.assertEqual(len(res["listed"]), 5)

    def test_the_control_a_plain_python_import_without_dash_B_writes_bytecode_and_the_check_sees_it_R5c(self) -> None:
        d = self.mk("resit-find-")
        code = d / "code"
        (code / "tools" / "brain").mkdir(parents=True)
        (code / "tools" / "brain" / "grade_life.py").write_text("X = 1\n")
        marker_ns = time.time_ns()
        time.sleep(0.05)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {str(code)!r}); import tools.brain.grade_life"], check=True, env=env)
        self.assertTrue(list(code.rglob("*.pyc")), "the control must write bytecode into the writable tree")
        res = R.newer_than([d], marker_ns)
        self.assertGreaterEqual(res["n_newer"], 1)
        # and the same import under -B -I writes nothing: the empty find is the evidence
        d2 = self.mk("resit-find-")
        code2 = d2 / "code"
        (code2 / "tools" / "brain").mkdir(parents=True)
        (code2 / "tools" / "brain" / "grade_life.py").write_text("X = 1\n")
        marker2 = time.time_ns()
        time.sleep(0.05)
        subprocess.run([sys.executable, "-B", "-I", "-c", f"import sys; sys.path.insert(0, {str(code2)!r}); import tools.brain.grade_life"], check=True, env=env)
        self.assertEqual(R.newer_than([d2], marker2)["n_newer"], 0)


class TestStatusReading(Tmp):
    def test_the_two_fields_are_read_when_present(self) -> None:
        d = self.mk("resit-st-")
        (d / "STATUS.json").write_text(json.dumps({"mind_backlog_rows": 8, "mind_ms_per_canvas_1min": 216.17, "moments": 5}))
        r = R.status_reading(d / "STATUS.json")
        self.assertTrue(r["present"])
        self.assertEqual((r["mind_backlog_rows"], r["mind_ms_per_canvas_1min"]), (8, 216.17))

    def test_an_absent_file_or_a_missing_field_is_said_never_a_zero(self) -> None:
        d = self.mk("resit-st-")
        r = R.status_reading(d / "STATUS.json")
        self.assertFalse(r["present"])
        self.assertIsNone(r["mind_backlog_rows"])
        (d / "STATUS.json").write_text(json.dumps({"moments": 5}))
        r = R.status_reading(d / "STATUS.json")
        self.assertTrue(r["present"])
        self.assertIsNone(r["mind_ms_per_canvas_1min"])
        self.assertEqual(r["fields_present"], {"mind_backlog_rows": False, "mind_ms_per_canvas_1min": False})

    def test_a_torn_file_is_said(self) -> None:
        d = self.mk("resit-st-")
        (d / "STATUS.json").write_text('{"mind_backlog_rows": 8, "mind_ms')
        r = R.status_reading(d / "STATUS.json")
        self.assertTrue(r["present"])
        self.assertIn("unreadable", r["note"])


class TestGraderPin(Tmp):
    def info(self, d: Path) -> dict:
        return R.grader_info(d)

    def tree(self, text: str = "def grade(*a, **k): return {}\n") -> Path:
        d = self.mk("resit-gp-")
        (d / "tools" / "brain").mkdir(parents=True)
        (d / "tools" / "brain" / "grade_life.py").write_text(text)
        return d

    def test_the_pin_is_written_once_and_a_second_run_under_the_same_grader_passes(self) -> None:
        out = self.mk("resit-out-")
        g = self.tree()
        self.assertEqual(R.check_grader_pin(out, self.info(g)), "written")
        self.assertEqual(R.check_grader_pin(out, self.info(g)), "checked")
        pin = json.loads((out / "GRADER.json").read_text())
        self.assertEqual(pin["grade_life_sha256"], hashlib.sha256((g / "tools/brain/grade_life.py").read_bytes()).hexdigest())

    def test_a_changed_grader_is_refused_R4j(self) -> None:
        out = self.mk("resit-out-")
        g = self.tree()
        R.check_grader_pin(out, self.info(g))
        before = (g / "tools/brain/grade_life.py").read_bytes()
        (g / "tools/brain/grade_life.py").write_text("def grade(*a, **k): return {'other': 1}\n")
        self.assertNotEqual(before, (g / "tools/brain/grade_life.py").read_bytes(), "the plant must change the bytes")
        with self.assertRaises(R.Refused) as cm:
            R.check_grader_pin(out, self.info(g))
        self.assertIn("grader pin", str(cm.exception))
        self.assertIn("grade_life_sha256", str(cm.exception))

    def test_a_modules_digest_that_differs_after_the_grade_child_ran_is_refused_too(self) -> None:
        out = self.mk("resit-out-")
        g = self.tree()
        R.check_grader_pin(out, {**self.info(g), "modules_digest": "aaa"})
        with self.assertRaises(R.Refused):
            R.check_grader_pin(out, {**self.info(g), "modules_digest": "bbb"})

    def test_a_pin_key_the_caller_did_not_give_fails_closed_it_is_never_skipped(self) -> None:
        out = self.mk("resit-out-")
        g = self.tree()
        full = {**self.info(g), "commit": "abc123", "modules_digest": "aaa"}
        R.check_grader_pin(out, full)
        for drop in ("commit", "grade_life_sha256", "modules_digest"):
            with self.subTest(drop=drop):
                partial = {k: v for k, v in full.items() if k != drop}
                self.assertNotIn(drop, partial, "the plant must remove the key")
                with self.assertRaises(R.Refused) as cm:
                    R.check_grader_pin(out, partial)
                self.assertIn(drop, str(cm.exception))

    def test_the_modules_digest_is_skipped_only_on_the_pre_check_where_it_is_not_yet_known(self) -> None:
        out = self.mk("resit-out-")
        g = self.tree()
        pre = {**self.info(g)}
        R.check_grader_pin(out, {**pre, "modules_digest": "aaa"})
        self.assertEqual(R.check_grader_pin(out, pre, write=False), "checked", "the pre-check cannot know the digest and compares the rest")
        with self.assertRaises(R.Refused):
            R.check_grader_pin(out, pre)                            # the post-check (write=True) must give it
        with self.assertRaises(R.Refused):
            R.check_grader_pin(out, {**pre, "grade_life_sha256": "0" * 64}, write=False)       # and the pre-check still compares every other key

    def test_a_directory_that_is_no_git_checkout_says_so_never_invents_a_commit(self) -> None:
        g = self.tree()
        i = self.info(g)
        self.assertIsNone(i["commit"])
        self.assertIn("grade_life_sha256", i)

    def test_world_seed_is_read_from_the_scene_line_only(self) -> None:
        self.assertEqual(R.world_seed_of("WORLD    scene seed 20261101; train 50000; sitting fresh s1b1\n"), 20261101)
        self.assertEqual(R.world_seed_of("WORLD    drawn every 10 s\nWORLD game x; seed 20260923\n"), None)
        self.assertEqual(R.world_seed_of(GENOME), None)


# ------------------------------------------------------------------------------------------------ the gate, end to end, on a stub life
class GateBase(Tmp):
    def setUp(self) -> None:
        self.base = self.mk("resit-gate-")

    def life(self, **kw) -> StubLife:
        return StubLife(self.base, **kw)


class TestGatePass(GateBase):
    def test_r1_passes_on_a_faithful_life_and_the_row_carries_what_the_law_names(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["kind"], "gate")
        a = row["r1a"]
        self.assertEqual((a["n_resit"], a["n_equal"], a["n_diff"], a["n_missing_life_row"]), (10, 10, 0, 0))
        self.assertTrue(row["r1b"]["equal"])
        self.assertEqual(row["restart_duplicates"], 0)
        self.assertTrue(row["p0"]["ok"])
        self.assertEqual(row["reader_sha256"], hashlib.sha256(Path(RESIT_PY).read_bytes()).hexdigest())
        self.assertEqual(row["flags"], {"dont_write_bytecode": True, "isolated": True, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
        self.assertEqual(row["items"]["n_asks"], 10)
        self.assertEqual(row["items"]["pin"], "written")
        self.assertEqual(row["grader"]["pin"], "written")
        self.assertTrue(row["state"]["prints_ok"])
        self.assertEqual(row["state"]["last_seq"], 9000)
        self.assertTrue(row["subject"]["modules"])
        self.assertIn("m6_reading", row)
        self.assertEqual(row["m6_reading"]["read_by"], "stub")

    def test_without_a_reference_grade_the_gate_reads_partial_and_never_a_pass(self) -> None:
        L = self.life()
        p, res, row = orch(L, with_ref=False)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "PARTIAL")
        self.assertIn("NOT RUN", row["reading"])
        self.assertTrue(row["r1a"]["pass"])
        self.assertFalse(row["r1b"]["compared"])

    def test_the_gate_writes_no_series_and_no_origin_and_uses_its_own_run_folder(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertFalse((L.out / "RESIT.jsonl").exists())
        self.assertFalse((L.out / "ORIGIN.json").exists())
        self.assertTrue((L.out / "gate" / "r1" / "answers.jsonl").exists())
        self.assertTrue((L.out / "gate" / "r1" / "grade.json").exists())
        self.assertTrue((L.out / "gate" / "r1" / "copy" / "brain.npz").exists())

    def test_the_cost_and_the_peak_memory_of_every_process_are_in_the_row(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        cpu, mem = row["cpu"], row["memory"]
        self.assertGreater(cpu["answer_s"], 0)
        self.assertGreater(cpu["grade_s"], 0)
        self.assertGreater(cpu["total_s"], cpu["answer_s"])
        self.assertTrue(cpu["cold"])
        self.assertEqual(cpu["cap_s"], 1800)
        for k in ("answer_maxrss_mb", "grade_maxrss_mb", "orchestrator_maxrss_mb"):
            self.assertGreater(mem[k], 1, k)

    def test_the_epoch_after_both_begin_asks_leaves_the_gate_under_epoch_0_and_the_four_line_hashes_of_both_are_a_reading_AM3(self) -> None:
        L = self.life(epoch_seq=5000)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        g = row["genome"]
        self.assertEqual(g["sets"]["fresh"]["epoch"], 0)
        self.assertEqual(g["sets"]["s1b1"]["epoch"], 0)
        self.assertEqual(g["sets"]["fresh"]["path"], str(L.root / "GENOME.genome"))
        reading = {e["epoch"]: e["lines"] for e in g["epochs_reading"]}
        self.assertEqual(set(reading), {0, 1})
        for line in ("retina", "gaze", "colour", "brain"):
            self.assertEqual(reading[0][line], reading[1][line], f"epochs 0 and 1 have equal {line} lines (EVOLVE cannot move them)")
        self.assertNotEqual(reading[0]["genome"], reading[1]["genome"])
        self.assertTrue(g["epochs_four_lines_equal"])

    def test_an_epoch_before_the_first_begin_ask_puts_the_gate_under_epoch_1_and_its_sha_is_checked(self) -> None:
        L = self.life(epoch_seq=1002)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(row["genome"]["sets"]["fresh"]["epoch"], 1)
        self.assertEqual(row["genome"]["sets"]["fresh"]["sha256"], hashlib.sha256(GENOME_V1.encode()).hexdigest())

    def test_two_equal_rows_for_one_ask_collapse_to_the_last_and_are_counted_and_r1_passes(self) -> None:
        L = self.life()
        L.rewrite_journal(lambda rows: rows + [dict(next(r for r in rows if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0"))])
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(row["restart_duplicates"], 1)
        self.assertEqual(row["r1a"]["n_equal"], 10)

    def test_a_warm_run_hits_the_cache_and_answers_byte_for_byte_as_the_cold_one_R2(self) -> None:
        L = self.life()
        runs = [orch(L, label=f"r2{c}") for c in "abc"]
        for p, res, row in runs:
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        a = [(L.out / "gate" / f"r2{c}" / "answers.jsonl").read_bytes() for c in "abc"]
        self.assertEqual(a[0], a[1])
        self.assertEqual(a[0], a[2])
        rows = [r for _, _, r in runs]
        self.assertTrue(rows[0]["cpu"]["cold"])
        self.assertFalse(rows[1]["cpu"]["cold"])
        self.assertEqual(rows[1]["cpu"]["cap_s"], 480)
        self.assertEqual(rows[0]["answer_meta"]["glance_cache"]["hits"], 0)
        self.assertGreater(rows[1]["answer_meta"]["glance_cache"]["hits"], 0)
        mask = ("stamp", "cpu", "memory", "wall_s", "answer_meta", "live_load", "label", "nothing_written", "children")

        def strip(r):
            r = json.loads(json.dumps({k: v for k, v in r.items() if k not in mask}))
            r["items"]["pin"] = r["grader"]["pin"] = "-"          # «written» on the first run, «checked» on every later one: the only honest difference
            r["state"]["copy_dir"] = "-"                          # the run folder is named by the label
            return r
        self.assertEqual(strip(rows[0]), strip(rows[1]))
        self.assertEqual(strip(rows[1]), strip(rows[2]))

    def test_the_live_status_is_read_at_the_start_and_at_the_end_R12(self) -> None:
        L = self.life()
        st = self.base / "STATUS.json"
        st.write_text(json.dumps({"mind_backlog_rows": 8, "mind_ms_per_canvas_1min": 216.17}))
        p, res, row = orch(L, "--status", str(st))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        for when in ("start", "end"):
            self.assertEqual(row["live_load"][when]["mind_backlog_rows"], 8)
            self.assertEqual(row["live_load"][when]["mind_ms_per_canvas_1min"], 216.17)

    def test_r14_the_turn_pin_is_recorded_and_a_turn_that_mutates_the_brain_is_caught_through_the_gate(self) -> None:
        L = self.life()
        p, res, row = orch(L, "--check-turn", "--world-seed", "5")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertTrue(row["turn_check"]["state_hash_equal"])
        self.assertTrue(row["turn_check"]["answers_equal"])
        build_stub(L.code, turn_mutates=True)
        p, res, row = orch(L, "--check-turn", "--world-seed", "5", label="r14")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("R14", row["reason"])

    def test_the_eye_pin_is_recorded_and_a_mutable_eye_key_refuses_the_gate_R13(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(row["eye_pin"], {"n_mutable": 2, "eye_or_brain": 0})
        build_stub(L.code, mutable=("DELTA.lr", "GAZE.grid"))
        p, res, row = orch(L, label="r13")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("R13", row["reason"])
        self.assertIn("GAZE.grid", row["reason"])


class TestGateFails(GateBase):
    def test_a_planted_difference_in_one_life_row_fails_r1a_names_the_item_and_reads_a_subject_difference(self) -> None:
        L = self.life()
        before = L.journal_file.read_bytes()

        def plant(rows):
            for r in rows:
                if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0":
                    r["answer"] = {"kind": "thing", "hyp": 2, "raw": {"p": 0.123}}
            return rows
        L.rewrite_journal(plant)
        self.assertNotEqual(before, L.journal_file.read_bytes(), "the plant must change the bytes")
        p, res, row = orch(L, with_ref=False)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "FAIL")
        self.assertIn("SUBJECT", row["reading"])
        self.assertEqual((row["r1a"]["n_equal"], row["r1a"]["n_diff"]), (9, 1))
        fd = row["r1a"]["first_diff"]
        self.assertEqual((fd["item"], fd["differing_keys"]), ("M1:fresh:0", ["answer"]))
        self.assertEqual(fd["life"]["answer"]["hyp"], 2)
        self.assertNotEqual(fd["resit"]["answer"], fd["life"]["answer"])

    def test_a_resit_that_leaves_asks_unanswered_is_not_a_pass_even_when_every_row_it_wrote_is_equal(self) -> None:
        spec = [it for it in sitting_spec() if not (it[0] == "eye" and it[1] == "sc-s1b1-0")]       # the s1b1 canvas never comes: two held asks stay unanswered
        self.assertEqual(len(spec), len(sitting_spec()) - 1, "the plant must change the tape")
        L = self.life(tape_spec=spec)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "FAIL")
        a = row["r1a"]
        self.assertEqual((a["n_equal"], a["n_diff"], a["unanswered"], a["n_asks_on_tape"]), (8, 0, 2, 10))
        self.assertTrue(a["all_equal"], "every row it wrote IS equal …")
        self.assertFalse(a["pass"], "… and 8 of 10 asks is still not «every ask answered and equal»")

    def test_rows_equal_but_marks_differ_is_named_grader_drift(self) -> None:
        L = self.life()
        ref = json.loads(L.ref.read_text())
        ref["sets"]["fresh"]["marks"]["M1"]["graded"]["covered"] += 1e-6
        L.ref.write_text(json.dumps(ref))
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "FAIL")
        self.assertIn("GRADER DRIFT", row["reading"])
        self.assertEqual(row["r1a"]["n_diff"], 0)
        self.assertIn("sets.fresh.marks.M1.graded.covered", [d["path"] for d in row["r1b"]["diffs"]])

    def test_the_brain_moving_after_the_first_ask_reads_not_gradable_and_no_child_is_run_P0(self) -> None:
        L = self.life(extra_rows=[brain(1004, "learn")])                # a learn above the first sitting ask (1003)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "NOT GRADABLE")
        self.assertIn("the brain moved after the first sitting ask", row["reason"])
        self.assertFalse((L.out / "gate" / "r1" / "answers.jsonl").exists(), "P0 is checked BEFORE the children are spent")
        self.assertFalse((L.out / "gate" / "r1" / "answer-spec.json").exists())

    def test_a_turn_row_after_the_first_ask_does_not_move_the_brain_P0_stays_ok(self) -> None:
        L = self.life(extra_rows=[brain(1004, "turn"), brain(1005, "refused")])
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(row["p0"]["allowed_above"], {"turn": 1, "refused": 1})

    def test_two_unequal_rows_for_one_ask_are_restart_divergent_and_r1_reads_not_gradable_R4k(self) -> None:
        L = self.life()

        def plant(rows):
            r0 = next(r for r in rows if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0")
            return rows + [{**r0, "answer": {"kind": "thing", "hyp": 2, "raw": {"p": 0.9}}}]
        L.rewrite_journal(plant)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "NOT GRADABLE")
        self.assertIn("RESTART-DIVERGENT", row["reason"])
        self.assertFalse((L.out / "gate" / "r1" / "answers.jsonl").exists())

    def test_the_orchestrator_without_dash_B_or_dash_I_or_with_other_blas_pins_is_refused_and_writes_nothing(self) -> None:
        L = self.life()
        for flags, env_over, needle in [(("-I",), {}, "-B"), (("-B",), {}, "-I"), (("-B", "-I"), {"OPENBLAS_NUM_THREADS": "4"}, "OPENBLAS_NUM_THREADS"),
                                        (("-B", "-I"), {"OMP_NUM_THREADS": "2"}, "OMP_NUM_THREADS")]:
            with self.subTest(flags=flags, env=env_over):
                p, res, row = orch(L, flags=flags, env_over=env_over, label="flags")
                self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
                self.assertIn(needle, res["refused"])
                self.assertFalse((L.out / "gate" / "flags" / "answers.jsonl").exists())

    def test_an_out_dir_inside_the_life_is_refused_nothing_is_written_under_a_life_R5(self) -> None:
        L = self.life()
        inside = L.root / "resit-out"
        p, res, row = orch(L, out=inside)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("inside", res["refused"])
        self.assertFalse(inside.exists())

    def test_r5b_an_empty_find_after_a_real_gate_run_is_the_evidence_nothing_was_written_into_the_life(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        nw = row["nothing_written"]
        self.assertTrue(nw["checked"])
        self.assertEqual(nw["n_newer"], 0)
        self.assertGreater(nw["n_entries_walked"], 20)
        marker = L.out / "gate" / "r1" / "START.marker"
        found = subprocess.run(["find", str(L.root), "-newer", str(marker)], capture_output=True, text=True)
        self.assertEqual(found.stdout.strip(), "", "the independent oracle: GNU find -newer finds nothing either")

    def test_a_missing_state_prev_is_skipped_by_name_and_the_gate_exits_2(self) -> None:
        L = self.life()
        shutil.rmtree(L.root / "state")
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "SKIPPED")
        self.assertIn("state/prev", row["reason"])

    def test_a_state_copy_whose_mtime_differs_from_the_snapshot_prints_is_refused_R4b(self) -> None:
        L = self.life()
        f = L.prev / "brain.json"
        st = f.stat()
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 7_000_000_000))
        self.assertNotEqual(f.stat().st_mtime_ns, st.st_mtime_ns, "the plant must change the mtime")
        p, res, row = orch(L, "--copy-retry-sleep-s", "0")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("mtime_ns", row["reason"])

    def test_a_byte_flipped_inside_brain_npz_is_refused_by_name_with_the_prints_still_matching_R4a(self) -> None:
        L = self.life()
        f = L.prev / "brain.npz"
        st = f.stat()
        data = bytearray(f.read_bytes())
        at = bytes(data).find(np.array([1.0, 2.0, 3.0]).tobytes())      # inside the array's own bytes (not the zip's padding): the zip CRC or the state hash must see it
        self.assertGreaterEqual(at, 0)
        data[at + 3] ^= 0xFF
        f.write_bytes(bytes(data))
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns))             # the prints (size, mtime_ns) still match: only Brain.load can see it
        self.assertEqual(f.stat().st_mtime_ns, st.st_mtime_ns)
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("Brain.load refused", row["reason"])

    def test_a_genome_whose_sha_is_not_the_epoch_rows_is_refused_R4e(self) -> None:
        L = self.life(epoch_seq=1002)
        g = L.root / "GENOME.v1.genome"
        before = g.read_bytes()
        g.write_text(g.read_text() + "# a hand edit\n")
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("genome_sha", row["reason"])

    def test_genome_v1_with_its_epoch_rows_deleted_is_undetermined_and_refused_R4f(self) -> None:
        L = self.life(epoch_seq=1002)
        L.rewrite_journal(lambda rows: [r for r in rows if not (isinstance(r.get("epoch"), dict))])
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("undetermined", row["reason"])

    def test_sittings_that_changed_since_the_first_run_are_refused_by_name_the_tape_row_sha_must_match_its_payload(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        # the same OUT, the sittings changed: one ask payload byte
        first = sorted((L.root / "tape" / "payload").glob("*.json"))[1]
        before = first.read_bytes()
        first.write_text(first.read_text().replace('"test_seed": 7', '"test_seed": 8'))
        self.assertNotEqual(before, first.read_bytes(), "the plant must change the bytes")
        # the tape row's own sha would now disagree with the payload: the scan refuses by name before anything runs
        p, res, row = orch(L, label="r1b")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("payload", row["reason"])

    def test_a_grader_that_changed_since_the_pin_is_refused_R4j(self) -> None:
        L = self.life()
        p, res, row = orch(L)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        g = L.grader / "tools" / "brain" / "grade_life.py"
        before = g.read_bytes()
        g.write_text(g.read_text() + "\n# another grader\n")
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, row = orch(L, label="r1j")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("grader pin", row["reason"])

    def test_the_cpu_cap_stops_a_run_that_outgrows_it_and_says_so_R7(self) -> None:
        L = self.life()
        p, res, row = orch(L, "--cpu-cap-s", "1", env_over={"STUB_BURN_S": "4"})
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(row["status"], "REFUSED")
        self.assertIn("R7", row["reason"])
        self.assertIn("CPU", row["reason"])


class TestGateNudge(GateBase):
    def test_r3_a_nudged_copy_changes_answers_and_marks_and_the_dose_is_printed(self) -> None:
        L = self.life()
        p, res, row = orch(L, "--nudge", "0.5", "--nudge-seed", "20261003", label="r3-0.5")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(row["status"], "PLANT CAUGHT")
        r3 = row["r3"]
        self.assertEqual(r3["eps"], 0.5)
        self.assertGreaterEqual(r3["answers_changed"], 1)
        self.assertTrue(set(r3["marks_changed"]) & {"M1", "M2a", "M3"})
        self.assertNotEqual(r3["hash_before"], r3["hash_after"])
        self.assertNotIn("r1a", row, "a nudged run is a plant, not the gate")

    def test_r3_a_plant_that_reaches_no_answer_is_said_not_passed(self) -> None:
        L = self.life()
        p, res, row = orch(L, "--nudge", "0.0", "--nudge-seed", "1", label="r3-0")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("did not change", row["reason"])


if __name__ == "__main__":
    unittest.main()
