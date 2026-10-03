# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:23 +0400 — PREREG-RESIT-READER v4: the ORCHESTRATOR in ORIGIN mode — the brain AT the sittings (rebuilt states, or the labelled fallback copy) answered and graded over the LIFE's OWN
# sittings taken from a SOURCE COPY of its tape (option A), ITEMS-MATCH first (R15), the cross-check R9 (exact in every key but hash for a rebuilt origin; a labelled reading for a fallback; LATE items counted by
# thirds; a set with no tested EARLY item reads UNTESTED), the refusals R4 (d) (g) (h) (i) (k), ORIGIN.json written ONCE (R8 a), and daily mode pairing against it. Written BEFORE the mode.
# The lives are STUBS: the live life is a StubLife with the WORLD scene line, the pinned items are a second stub life at another tape position (so no seq can match by luck).
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:25 +0400 — THE COMMON FAILURE of 24 of these 26 tests, diagnosed: `run_origin` reads the scene index of the «dax» meeting from the PINNED GRADER checkout's
# brain/scene/world.py (`dax_index_of`, v4 §1.6 (ii)); OriginBase's stub grader held only tools/brain/grade_life.py, so every test that got past the early refusals died on a FileNotFoundError (an ERROR row). The stub grader
# now carries a world.py (STUB_WORLD, DAX_SCENE = 2700 ↔ index 2699, the index make_life's training row carries), and a plant that REMOVES it is a named refusal (TestOriginRefusals).
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:40 +0400 — the VERIFIER's ask on c887b50: «show me on a planted run that the origin ROW (not only the r9 dict) says R9 UNTESTED and is not summarised as a pass, with the
# series row saying so» (law R9: «the series row says so»). The origin row now carries a top-level `r9_reading` line and `r9_untested_sets`; the planted run is asserted on ORIGIN.json, the RESIT.jsonl line and RESIT.md.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:48 +0400 — the survivors of the first mutation sweep of origin mode, each killed by a test named in the sweep log: R9 exact in EVERY key but hash (a plant per key, hash alone is no
# difference); the source copy re-verified at the END of the run (a stub that touches the copy during the answer child); EYE-CHANGED against the grader and between the sets; equal restart duplicates counted; the fresh-begin state's
# n_learned (two states that differ); the grader pin refused BEFORE any child; the fallback's genome by the state's last seq; a second origin refused before any child; ITEMS-MATCH plant f at run level.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:52 +0400 — FOUND BY READING origin mode against the law's honesty rules (#168/#246: a count of completed cases prints started/completed/still-open): the origin never checked that it
# ANSWERED every ask of the life's sittings, and R9 counted only origin rows that lack a life row — never the life's rows that lack an origin row. An origin that skipped an item would have been written. Plants: a stub tape that drops one ask.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:38 +0400 — the VERIFIER's ruling on r9_reading (21:3x): E1 reserves «tested» for the EARLY items other than begin and end, so a line that put the structural rows into the TESTED denominator
# («EXACT where tested: 6 of 6 EARLY items (begin and end included)») would let a reader take begin/end for tests. The line prints SEPARATE counts: «R9 EXACT on k of k TESTED EARLY items; the structural begin/end rows equal on j of j (not counted as tests)».
"""tests/tools/test_resit_origin.py — origin mode on stub lives."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

from tests.tools.test_resit import Tmp, ans, brain, epoch_row
from tests.tools.test_resit_children import ENV, RESIT_PY, last_json, png, write_state
from tests.tools.test_resit_daily import STUB_GRADER_DAILY
from tests.tools.test_resit_gate import StubLife
from tests.tools.test_resit_origin_copy import GENOME_ORIGIN, make_life
from tools.brain import resit as R

STUB_WORLD = "# the stub of brain/scene/world.py: the one constant the origin's source copy reads from the pinned grader checkout\nDAX_SCENE = 2700                                  # 1-based → the index 2699\nDAX_INDEX = DAX_SCENE - 1\n"
BEGIN = {"fresh": 1003, "s1b1": 1009}                                  # the stub life's two begin asks (seq0 1000: ear 1001, eye 1002, begin 1003 … begin 1009)
STUB_V = np.array([[1.0, -1.0, 0.0], [2.0, -2.0, 0.0], [3.0, -3.0, 0.0], [0.5, -0.5, 0.0]])


def stub_state_hash(v, n_learned: int) -> str:
    return hashlib.sha256(np.array(v, dtype=np.float64).tobytes() + str(n_learned).encode() + STUB_V.tobytes()).hexdigest()


def chain_below(tape: Path, below_seq: int) -> str:
    """An independent recomputation of the rebuild's tape digest: sha256 over «seq NUL sha NEWLINE» of the rows below the begin seq, in order."""
    h = hashlib.sha256()
    for f in sorted(tape.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            if int(r["seq"]) < below_seq:
                h.update(f"{r['seq']}\0{r['sha']}\n".encode())
    return h.hexdigest()


class OriginBase(Tmp):
    def setUp(self) -> None:
        self.base = self.mk("resit-origin-")
        self.life = StubLife(self.base, genome=GENOME_ORIGIN)
        (self.life.grader / "tools" / "brain" / "grade_life.py").write_text(STUB_GRADER_DAILY)
        (self.life.grader / "brain" / "scene").mkdir(parents=True)
        (self.life.grader / "brain" / "scene" / "world.py").write_text(STUB_WORLD)
        self.items_root = make_life(self.base, "items", seq0=5000)        # the pinned items: the same sittings at ANOTHER tape position
        self.out = self.base / "out-origin"
        self.n = 0

    # ---- fixtures
    def rebuilt_state(self, name: str, setname: str, *, v=(1.0, 2.0, 3.0), n_learned: int = 10, begin_seq: int = None, genome_text: str = GENOME_ORIGIN,
                      bad_state_hash: bool = False, bad_genome_sha: bool = False, bad_tape_digest: bool = False) -> Path:
        d = write_state(self.base / name, v=v, n_learned=n_learned, calibrated_at=n_learned)
        (d / "GENOME.in-force.genome").write_text(genome_text)
        b = begin_seq if begin_seq is not None else BEGIN[setname]
        side = {"life": "life", "set": setname, "begin_seq": b, "rows_replayed": b - 1001, "tape_digest": chain_below(self.life.root / "tape", b), "code_commit": None,
                "genome_in_force_sha": hashlib.sha256(genome_text.encode()).hexdigest(), "state_hash": stub_state_hash(v, n_learned), "n_learned": n_learned, "calibrated_at": n_learned}
        if bad_state_hash:
            side["state_hash"] = "0" * 64
        if bad_genome_sha:
            side["genome_in_force_sha"] = "0" * 64
        if bad_tape_digest:
            side["tape_digest"] = "0" * 64
        (d / "ORIGIN.json").write_text(json.dumps(side))
        return d

    def both(self, **over) -> list:
        return [f"fresh={self.rebuilt_state('st-fresh', 'fresh', **over)}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1', **over)}"]

    def run_origin(self, *extra: str, kind: str = "rebuilt", states=None, reason: str = None, stamp: str = None, out: Path = None, flags=("-B", "-I"), env_over: dict = None):
        self.n += 1
        stamp = stamp or f"2026100412{self.n:02d}00Z"
        args = [sys.executable, *flags, str(RESIT_PY), "run", "--mode", "origin", "--root", str(self.life.root), "--code", str(self.life.code), "--items-root", str(self.items_root),
                "--grader-code", str(self.life.grader), "--out", str(out or self.out), "--scored", str(self.life.scored), "--stamp", stamp, "--copy-retry-sleep-s", "0",
                "--origin-kind", kind]
        for s in states or []:
            args += ["--state", s]
        if reason is not None:
            args += ["--reason", reason]
        args += list(extra)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(ENV)
        env.update(env_over or {})
        p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(self.base))
        o = out or self.out
        att = o / "origin" / stamp / "origin.json"
        return p, last_json(p.stdout), (json.loads(att.read_text()) if att.exists() else None), stamp

    def origin_row(self, out: Path = None):
        f = (out or self.out) / "ORIGIN.json"
        return json.loads(f.read_text()) if f.exists() else None

    def series(self, out: Path = None) -> list:
        f = (out or self.out) / "RESIT.jsonl"
        return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []


class TestOriginRebuilt(OriginBase):
    def test_a_rebuilt_origin_is_written_once_with_provenance_vectors_and_the_lives_own_tables_beside(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertIsNotNone(o)
        self.assertEqual((o["kind"], o["origin_kind"], o["reason"]), ("origin", "rebuilt", None))
        self.assertEqual(self.series()[0]["kind"], "origin")
        self.assertEqual((o["origin_n_learned_fresh_begin"], o["begin_seq_fresh"]), (10, 1003))
        self.assertEqual({s["set"] for s in o["states"]}, {"fresh", "s1b1"})
        self.assertEqual(set(o["vectors"]), {"M1", "M2a"})
        self.assertEqual(len(o["vectors"]["M1"]), 2)
        self.assertTrue(o["partition"]["ok"], o["partition"])
        self.assertTrue(o["life_own"]["partition"]["ok"])
        self.assertEqual(set(o["life_own"]["marks"]), {"M1", "M2a"})
        self.assertEqual(o["genome"]["grader"]["path"], str(self.items_root / "GENOME.genome"))
        self.assertTrue(o["genome_lines"])

    def test_the_children_read_the_source_copy_and_the_grader_is_the_pinned_configuration_of_the_daily_rows_v4(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        d = self.out / "origin" / stamp
        src = d / "src"
        a, g, lg = (json.loads((d / n).read_text()) for n in ("answer-spec.json", "grade-spec.json", "life-grade/grade-spec.json"))
        self.assertEqual(a["items_root"], str(src))
        self.assertEqual(g["items_root"], str(src))
        self.assertEqual(lg["items_root"], str(src))
        self.assertEqual(g["genome"], str(self.items_root / "GENOME.genome"), "ONE grader configuration: brain-long-2's genome, only the tape changes")
        self.assertEqual(lg["genome"], g["genome"])
        self.assertEqual(lg["scored"], g["scored"])
        self.assertEqual(lg["journal"], str(src / "journal"), "the life's own grade reads the copy of ITS journal")
        self.assertEqual(g["journal"], str(d / "answers.jsonl"))
        self.assertEqual([s["name"] for s in a["states"]], ["fresh", "s1b1"])
        o = self.origin_row()
        self.assertEqual(o["source_copy"]["verify"], [])
        self.assertEqual(R.verify_source_copy(src, o["source_copy"]["sha256"]), [], "the row's sha256 names the bytes both children read")

    def test_r9_every_early_item_equals_the_lifes_row_in_every_key_but_hash_and_the_row_counts_them(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r9 = self.origin_row()["r9"]
        self.assertTrue(r9["refusing"])
        self.assertEqual(r9["early_diff_count"], 0)
        self.assertEqual(r9["early_equal"], r9["early_total"])
        self.assertEqual(r9["early_total"], 10, "no brain-moving row lies inside either sitting: all ten answers are EARLY")
        for s in ("fresh", "s1b1"):
            self.assertEqual(r9["by_set"][s]["n_late"], 0)
            self.assertEqual(r9["by_set"][s]["n_early"], 5, "begin, two points, the why and the end: five answers a set, all EARLY in the law's sense")
            self.assertEqual(r9["by_set"][s]["n_early_tested"], 3, "the two point items AND the why (the brain answers it from its state, and the sibling test lets a learn push it LATE); begin and end are EARLY but test nothing")
            self.assertFalse(r9["by_set"][s]["untested"])
        o = self.origin_row()
        self.assertEqual(o["r9_untested_sets"], [])
        self.assertTrue(o["r9_reading"].startswith("R9 EXACT on 6 of 6 TESTED EARLY items"), o["r9_reading"])
        self.assertIn("the structural begin/end rows equal on 4 of 4 (not counted as tests)", o["r9_reading"])
        self.assertEqual((r9["early_tested_total"], r9["early_structural_total"], r9["early_total"]), (6, 4, 10), "the two counts are the row's own, and sum to the whole")
        self.assertNotIn("UNTESTED", o["r9_reading"])
        self.assertNotIn("UNTESTED", (self.out / "RESIT.md").read_text(), "the control: a fully tested origin never says UNTESTED")

    def test_r9_a_planted_state_difference_refuses_the_origin_naming_the_first_item_and_writes_no_origin(self) -> None:
        base_hash = stub_state_hash((1.0, 2.0, 3.0), 10)
        self.assertNotEqual(base_hash, stub_state_hash((9.0, 2.0, 3.0), 10), "the plant must change the state")
        states = [f"fresh={self.rebuilt_state('st-fresh', 'fresh', v=(9.0, 2.0, 3.0))}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1', v=(9.0, 2.0, 3.0))}"]
        p, res, att, stamp = self.run_origin(states=states)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("R9", att["reason"])
        self.assertIn("M1:fresh:0", att["reason"])
        self.assertIsNone(self.origin_row())
        self.assertEqual(self.series(), [], "a refused origin writes no series line")

    def test_a_late_item_that_differs_is_printed_by_thirds_and_does_not_refuse(self) -> None:
        self.life.rewrite_journal(lambda rows: rows + [brain(1004, "learn")])                     # a learn inside the fresh sitting: the items answered after it are LATE
        def plant(rows):
            for r in rows:
                if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0":
                    r["answer"] = {"kind": "thing", "hyp": 2, "raw": {"p": 0.5}}
            return rows
        before = self.life.journal_file.read_bytes()
        self.life.rewrite_journal(plant)
        self.assertNotEqual(before, self.life.journal_file.read_bytes(), "the plant must change the bytes")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r9 = self.origin_row()["r9"]
        self.assertEqual(r9["early_diff_count"], 0)
        self.assertGreaterEqual(r9["late_total"], 3)
        self.assertEqual(r9["late_discordant"], 1)
        self.assertEqual(sum(r9["late_by_thirds"]["fresh"]), 1)
        self.assertEqual(len(r9["late_by_thirds"]["fresh"]), 3)
        self.assertEqual(sum(r9["late_by_thirds"]["s1b1"]), 0)
        self.assertEqual(r9["late_by_thirds"]["fresh"], [0, 1, 0], "five rows in seq order (begin | M1, M2a | why, end): the discordant M1 sits in the MIDDLE third")

    def test_a_late_item_that_differs_late_in_the_sitting_lands_in_the_last_third(self) -> None:
        self.life.rewrite_journal(lambda rows: rows + [brain(1004, "learn")])
        def plant(rows):
            for r in rows:
                if r.get("kind") == "answer" and r.get("form") == "why" and r.get("moment") == "sc-fresh-why":
                    r["answer"]["n"] = 99.0
            return rows
        before = self.life.journal_file.read_bytes()
        self.life.rewrite_journal(plant)
        self.assertNotEqual(before, self.life.journal_file.read_bytes(), "the plant must change the bytes")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r9 = self.origin_row()["r9"]
        self.assertEqual((r9["late_discordant"], r9["early_diff_count"]), (1, 0))
        self.assertEqual(r9["late_by_thirds"]["fresh"], [0, 0, 1], "the position of a discordant LATE item in the sitting is the reading (HEARS-2 A1.5), not only the count")

    def test_a_set_with_no_tested_early_item_reads_untested_never_a_pass(self) -> None:
        self.life.rewrite_journal(lambda rows: rows + [brain(1004, "learn")])                     # right after the fresh begin: every held item and the why are LATE
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        by = self.origin_row()["r9"]["by_set"]
        self.assertTrue(by["fresh"]["untested"])
        self.assertIn("R9 UNTESTED", by["fresh"]["note"])
        self.assertEqual(by["fresh"]["n_early_tested"], 0)
        self.assertGreaterEqual(by["fresh"]["n_early"], 1, "the begin row is EARLY in the law's sense, and tests nothing")
        self.assertFalse(by["s1b1"]["untested"])
        # the verifier's ask: the ROW says so (not only the r9 block), the series row says so, and RESIT.md says so — and none of them reads like a pass
        o = self.origin_row()
        self.assertEqual(o["r9_untested_sets"], ["fresh"])
        self.assertTrue(o["r9_reading"].startswith("R9 UNTESTED for set(s) fresh"), o["r9_reading"])
        self.assertIn("NOT A PASS", o["r9_reading"])
        self.assertIn("R10c", o["r9_reading"])
        self.assertNotIn("s1b1 (no tested", o["r9_reading"], "only the untested set is named untested")
        s = self.series()[-1]
        self.assertEqual(s["kind"], "origin")
        self.assertEqual((s["r9_reading"], s["r9_untested_sets"]), (o["r9_reading"], ["fresh"]), "the series row carries the same line")
        md = (self.out / "RESIT.md").read_text()
        self.assertIn("R9 UNTESTED for set(s) fresh", md)
        self.assertNotIn("R9 EXACT: ", md.split("| origin |")[1].split("\n")[0], "the table's origin line does not open with a pass")
        self.assertIn("R9 EXACT on 3 of 3 TESTED EARLY items", o["r9_reading"], "only the other set's three tested items are claimed exact")
        self.assertIn("equal on 3 of 3 (not counted as tests)", o["r9_reading"], "the untested set's own begin is among the structural rows, never among the tests")

    def test_the_acts_inside_each_sitting_are_censused(self) -> None:
        self.life.rewrite_journal(lambda rows: rows + [brain(1004, "learn"), brain(1010, "turn")])
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        census = self.origin_row()["r9"]["act_census"]
        self.assertEqual(census["fresh"], {"learn": 1})
        self.assertEqual(census["s1b1"], {"turn": 1})

    def test_r9_a_difference_in_any_key_but_hash_refuses_and_a_difference_in_hash_alone_does_not(self) -> None:
        orig = self.life.journal_file.read_bytes()

        def planted(key):
            def fn(rows):
                for r in rows:
                    if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0":
                        r[key] = (int(r[key]) + 1) if key == "eye_seq" else ["PLANTED", r.get(key)]
                return rows
            return fn
        for key in ("at", "moment", "fix", "hyps", "detail", "by", "eye_seq"):
            with self.subTest(key=key):
                self.life.journal_file.write_bytes(orig)
                self.life.rewrite_journal(planted(key))
                self.assertNotEqual(orig, self.life.journal_file.read_bytes(), "the plant must change the bytes")
                p, res, att, stamp = self.run_origin(states=self.both(), out=self.base / f"out-{key}")
                self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
                self.assertEqual(att["status"], "REFUSED")
                self.assertIn("R9", att["reason"])
                self.assertIn(f"'{key}'", att["reason"], "the refusal names the differing key")
        # the control: the chain field alone is not a difference
        self.life.journal_file.write_bytes(orig)
        self.life.rewrite_journal(lambda rows: [{**r, "hash": "chain-field"} if r.get("kind") == "answer" else r for r in rows])
        p, res, att, stamp = self.run_origin(states=self.both(), out=self.base / "out-hash")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

    def test_a_source_copy_that_changed_during_the_run_refuses_the_origin_and_writes_none_source_copy_changed_during_the_run(self) -> None:
        g = self.life.code / "genome" / "gaze.py"                                                  # the stub's glance touches the file the env names — here the COPY's genome, while the answer child runs
        g.write_text(g.read_text() + "\n_real_glances = glances\n\n\ndef glances(*a, **k):\n    import os\n    t = os.environ.get('STUB_TOUCH')\n    if t:\n        with open(t, 'a') as f:\n            f.write('# touched during the run\\n')\n    return _real_glances(*a, **k)\n")
        copy_genome = self.out / "origin" / "20261004120100Z" / "src" / "GENOME.genome"
        p, res, att, stamp = self.run_origin(states=self.both(), env_over={"STUB_TOUCH": str(copy_genome)})
        self.assertEqual(stamp, "20261004120100Z", "the touched path was computed for the first run's stamp")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("source copy changed during the run", att["reason"])
        self.assertIsNone(self.origin_row())
        self.assertEqual(self.series(), [], "a refused origin writes no series line")
        self.assertIn("touched during the run", copy_genome.read_text(), "the plant did touch the copy")

    def test_the_origin_n_learned_of_the_fresh_begin_state_is_read_not_the_later_sets(self) -> None:
        # the s1b1 begin state has learned the maker canvases of the fresh sitting: a larger count, and the life's own begin row for s1b1 reports it
        def plant(rows):
            for r in rows:
                if r.get("kind") == "answer" and r.get("moment") == "sc-s1b1-begin":
                    r["answer"]["at"] = 12
                    r["answer"]["raw"]["at"] = 12
            return rows
        before = self.life.journal_file.read_bytes()
        self.life.rewrite_journal(plant)
        self.assertNotEqual(before, self.life.journal_file.read_bytes(), "the plant must change the bytes")
        states = [f"fresh={self.rebuilt_state('st-fresh', 'fresh', n_learned=10)}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1', n_learned=12)}"]
        p, res, att, stamp = self.run_origin(states=states)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertEqual(o["origin_n_learned_fresh_begin"], 10, "the fresh-begin state's count, not the later set's")
        self.assertEqual({s["set"]: s["n_learned"] for s in o["states"]}, {"fresh": 10, "s1b1": 12})
        self.assertEqual(o["begin_seq_fresh"], 1003)

    def test_two_equal_duplicate_answer_rows_for_one_ask_are_collapsed_and_counted_restart_duplicates(self) -> None:
        self.life.rewrite_journal(lambda rows: rows + [dict(next(r for r in rows if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0"))])
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertEqual(o["restart_duplicates"], 1)
        self.assertEqual(o["r9"]["early_diff_count"], 0)

    def test_a_normal_origin_is_not_eye_changed_the_control_of_the_two_forms(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertFalse(o["eye_changed"])
        for s in ("fresh", "s1b1"):
            eye = o["genome"]["sets"][s]["eye"]
            self.assertEqual((eye["within_life"], eye["against_grader"], eye["against_grader_lines"], eye["within_life_lines"]), (False, False, [], []))

    def test_eye_changed_against_the_grader_is_labelled_and_the_origin_is_still_written(self) -> None:
        changed = GENOME_ORIGIN.replace("GAZE g 4", "GAZE g 5")
        self.assertNotEqual(changed, GENOME_ORIGIN, "the plant must change the genome")
        p, res, att, stamp = self.run_origin(states=self.both(genome_text=changed))
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertTrue(o["eye_changed"], "an anomaly: labelled, never refused")
        for s in ("fresh", "s1b1"):
            eye = o["genome"]["sets"][s]["eye"]
            self.assertTrue(eye["against_grader"])
            self.assertEqual(eye["against_grader_lines"], ["gaze"])
            self.assertFalse(eye["within_life"], "the two sets agree with each other: form (i) is false")

    def test_eye_changed_between_the_sets_is_labelled_and_the_origin_is_still_written(self) -> None:
        changed = GENOME_ORIGIN.replace("GAZE g 4", "GAZE g 5")
        self.assertNotEqual(changed, GENOME_ORIGIN, "the plant must change the genome")
        states = [f"fresh={self.rebuilt_state('st-fresh', 'fresh')}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1', genome_text=changed)}"]
        p, res, att, stamp = self.run_origin(states=states)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertTrue(o["eye_changed"])
        fresh, s1b1 = o["genome"]["sets"]["fresh"]["eye"], o["genome"]["sets"]["s1b1"]["eye"]
        self.assertFalse(fresh["within_life"])
        self.assertTrue(s1b1["within_life"])
        self.assertEqual(s1b1["within_life_lines"], ["gaze"])

    def test_the_origin_is_the_first_series_line_and_a_following_daily_row_pairs_against_it_by_item(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        args = [sys.executable, "-B", "-I", str(RESIT_PY), "run", "--mode", "daily", "--root", str(self.life.root), "--code", str(self.life.code), "--items-root", str(self.items_root),
                "--grader-code", str(self.life.grader), "--out", str(self.out), "--scored", str(self.life.scored), "--stamp", "20261005T000000Z", "--copy-retry-sleep-s", "0"]
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(ENV)
        q = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(self.base))
        self.assertEqual(q.returncode, 0, q.stderr + q.stdout)
        rows = self.series()
        self.assertEqual([r["kind"] for r in rows], ["origin", "daily"])
        d = rows[1]
        self.assertNotIn("refused", d)
        self.assertIsNotNone(d["vs_origin"])
        self.assertEqual(d["vs_origin"]["M1"]["pooled"]["n_paired"], 2)
        self.assertEqual(d["vs_origin"]["M1"]["pooled"]["discordant"], 0, "the same brain at the same items reads the same as the origin")
        self.assertEqual(d["post_origin_learned"], 0)
        self.assertFalse(d["eye_changed"])
        self.assertFalse(d["genome"]["eye"]["within_life"], "with an origin present, form (i) is determined and false")
        self.assertNotIn("verdict_copy", d)


class TestOriginRefusals(OriginBase):
    def test_r4g_a_second_origin_is_refused_and_the_first_is_untouched(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        first = (self.out / "ORIGIN.json").read_bytes()
        p2, res2, att2, stamp2 = self.run_origin(states=self.both())
        self.assertEqual(p2.returncode, 2, p2.stderr + p2.stdout)
        self.assertIn("written once", res2["refused"])
        self.assertEqual(first, (self.out / "ORIGIN.json").read_bytes())
        self.assertEqual(len(self.series()), 1)
        d2 = self.out / "origin" / stamp2
        self.assertFalse((d2 / "answer-spec.json").exists() or (d2 / "src").exists(), "refused BEFORE any copy or child: the written-once rule is a cheap refusal, not a late one")

    def plant_the_stub_graders_aggregate(self, only_for: str) -> None:
        """The stub grader's M1 aggregate is replaced by a number its items do not sum to — for the ORIGIN's grade only (its journal is the answers FILE) or the LIFE's own grade only (its journal is a DIRECTORY)."""
        g = self.life.grader / "tools" / "brain" / "grade_life.py"
        before = g.read_text()
        old = '"covered": _rate(r["answer"]["hyp"] == 0 for r in m1)}}'
        good = '_rate(r["answer"]["hyp"] == 0 for r in m1)'
        new = f'"covered": ({good} if Path(journal).is_dir() else 0.123)}}}}' if only_for == "origin" else f'"covered": (0.123 if Path(journal).is_dir() else {good})}}}}'
        self.assertEqual(before.count(old), 1)
        g.write_text(before.replace(old, new))
        self.assertNotEqual(before, g.read_text(), "the plant must change the grader")

    def test_a_grade_whose_aggregate_disagrees_with_its_items_refuses_the_origin_R6(self) -> None:
        self.plant_the_stub_graders_aggregate("origin")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("R6 PARTITION", att["reason"])
        self.assertIsNone(self.origin_row())

    def test_a_life_own_grade_whose_aggregate_disagrees_with_its_items_refuses_the_origin_R6(self) -> None:
        self.plant_the_stub_graders_aggregate("life")                                              # the origin's own grade is clean: only the LIFE's table can fail
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("R6 PARTITION", att["reason"])
        self.assertIsNone(self.origin_row())

    def drop_one_ask_from_the_answer_childs_tape(self) -> None:
        t = self.life.code / "creature" / "tape.py"
        before = t.read_text()
        after = before.replace("                yield json.loads(line)", "                r = json.loads(line)\n                import os\n                if str(r.get('seq')) != os.environ.get('STUB_DROP_SEQ'):\n                    yield r\n                    if str(r.get('seq')) == os.environ.get('STUB_DUP_SEQ'):\n                        yield r")
        self.assertNotEqual(before, after, "the plant must change the stub")
        t.write_text(after)

    def test_an_origin_that_answered_one_ask_twice_and_skipped_another_is_refused_by_the_life_rows_it_lacks(self) -> None:
        self.drop_one_ask_from_the_answer_childs_tape()                                            # 10 rows answered of 10 asks — the COUNT is right; the ROWS are not (1004 twice, 1005 never)
        p, res, att, stamp = self.run_origin(states=self.both(), env_over={"STUB_DROP_SEQ": "1005", "STUB_DUP_SEQ": "1004"})
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("have no origin row", att["reason"])
        self.assertIn("1005", att["reason"])
        self.assertIsNone(self.origin_row())
        self.assertNotIn("did not answer every ask", att["reason"], "the count check passed: only the row-level check could see it")

    def test_an_origin_that_answered_fewer_asks_than_the_lives_sittings_is_refused_by_name_and_so_is_a_fallback(self) -> None:
        self.drop_one_ask_from_the_answer_childs_tape()                                            # the ANSWER child never sees the ask at seq 1005 (M2a:fresh:0)
        for kind, kw in (("rebuilt", {"states": self.both()}), ("fallback_copy", {"reason": "the seat's words"})):
            with self.subTest(kind=kind):
                out = self.base / f"out-{kind}"
                p, res, att, stamp = self.run_origin(kind=kind, out=out, env_over={"STUB_DROP_SEQ": "1005"}, **kw)
                self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
                self.assertEqual(att["status"], "REFUSED")
                self.assertIn("did not answer every ask", att["reason"])
                self.assertIn("9 answered of 10", att["reason"])
                self.assertIsNone(self.origin_row(out))
                self.assertFalse((out / "origin" / stamp / "grade-spec.json").exists(), "refused before the grade children are spent")

    def test_a_grader_that_is_not_the_pinned_one_is_refused_before_any_child_grader_pin(self) -> None:
        self.out.mkdir(parents=True)
        pin = {"grader_code": "x", "commit": None, "dirty": None, "grade_life_sha256": "0" * 64, "modules_digest": None}
        (self.out / "GRADER.json").write_text(json.dumps(pin))
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("grader pin", att["reason"])
        self.assertIn("grade_life_sha256", att["reason"])
        d = self.out / "origin" / stamp
        self.assertFalse((d / "answer-spec.json").exists(), "no child was spawned: the pin is a PRE-check")
        self.assertIsNone(self.origin_row())

    def test_a_pinned_grader_checkout_without_world_py_is_refused_by_name_before_any_child_never_an_error_row(self) -> None:
        w = self.life.grader / "brain" / "scene" / "world.py"
        self.assertTrue(w.is_file(), "the fixture's grader carries a world.py — the plant removes it")
        w.unlink()
        self.assertFalse(w.exists(), "the plant must change the tree")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED", "a missing pinned input is a NAMED refusal (#230), not an ERROR row")
        self.assertIn("world.py", att["reason"])
        self.assertIsNone(self.origin_row())
        self.assertFalse((self.out / "origin" / stamp / "answers.jsonl").exists(), "no child ran")
        self.assertFalse((self.out / "origin" / stamp / "src").exists() and any((self.out / "origin" / stamp / "src").iterdir()), "no source copy was built from a half-provisioned grader")

    def test_r4h_an_origin_from_state_prev_without_the_fallback_kind_is_refused(self) -> None:
        p, res, att, stamp = self.run_origin(kind="rebuilt")                      # no --state: the source would be state/prev
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("fallback", (att or res).get("reason", res.get("refused", "")))

    def test_r4i_a_fallback_copy_without_the_seats_reason_is_refused(self) -> None:
        p, res, att, stamp = self.run_origin(kind="fallback_copy")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("--reason", (att or res).get("reason", res.get("refused", "")))
        self.assertIsNone(self.origin_row())

    def test_r4d_a_sidecar_whose_state_hash_is_not_the_loaded_states_is_refused_by_name(self) -> None:
        states = [f"fresh={self.rebuilt_state('st-fresh', 'fresh', bad_state_hash=True)}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1')}"]
        p, res, att, stamp = self.run_origin(states=states)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("state_hash", att["reason"])
        self.assertFalse((self.out / "origin" / stamp / "answers.jsonl").exists() and self.origin_row() is not None)

    def test_a_genome_whose_sha_is_not_the_sidecars_is_refused(self) -> None:
        states = [f"fresh={self.rebuilt_state('st-fresh', 'fresh', bad_genome_sha=True)}", f"s1b1={self.rebuilt_state('st-s1b1', 's1b1')}"]
        p, res, att, stamp = self.run_origin(states=states)
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("genome_in_force_sha", att["reason"])

    def test_a_rebuild_of_another_tape_is_refused_its_begin_seq_and_its_tape_digest_must_be_the_lifes(self) -> None:
        for kw, needle in (({"begin_seq": 1004}, "begin_seq"), ({"bad_tape_digest": True}, "tape_digest")):
            with self.subTest(kw=kw):
                out = self.base / f"out-{needle}"
                states = [f"fresh={self.rebuilt_state('st-fresh-x', 'fresh', **kw)}", f"s1b1={self.rebuilt_state('st-s1b1-x', 's1b1')}"]
                p, res, att, stamp = self.run_origin(states=states, out=out)
                self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
                self.assertIn(needle, att["reason"])
                self.assertIsNone(self.origin_row(out))

    def test_a_bare_state_pair_of_unknown_provenance_is_refused_for_a_rebuilt_origin(self) -> None:
        d = write_state(self.base / "bare", v=(1.0, 2.0, 3.0), n_learned=10, calibrated_at=10)
        p, res, att, stamp = self.run_origin(states=[str(d)])
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("ORIGIN.json", att["reason"])

    def test_a_bare_dir_with_a_sidecar_serves_every_set_and_is_refused_where_its_sidecar_names_another_set(self) -> None:
        d = self.rebuilt_state("st-one", "fresh")                                 # a complete rebuilt pair; its sidecar names the set «fresh» and ONE begin seq
        p, res, att, stamp = self.run_origin(states=[str(d)])
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("ORIGIN.json names the set 'fresh', not 's1b1'", att["reason"], "the provenance check ran on the sidecar, per set — not the earlier assignment message, which also lists both set names")
        self.assertIsNone(self.origin_row())

    def test_a_bare_dir_beside_named_dirs_is_refused_the_assignment_would_be_ambiguous(self) -> None:
        fresh, s1b1 = self.rebuilt_state("st-fresh", "fresh"), self.rebuilt_state("st-s1b1", "s1b1")
        p, res, att, stamp = self.run_origin(states=[str(fresh), f"s1b1={s1b1}"])
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("bare", att["reason"])
        self.assertIsNone(self.origin_row())

    def test_r4k_two_unequal_answer_rows_for_one_ask_in_the_lives_journal_refuse_the_origin_by_name(self) -> None:
        def plant(rows):
            r0 = next(r for r in rows if r.get("kind") == "answer" and r.get("item") == "M1:fresh:0")
            return rows + [{**r0, "answer": {"kind": "thing", "hyp": 2, "raw": {"p": 0.9}}}]
        self.life.rewrite_journal(plant)
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("RESTART-DIVERGENT", att["reason"])
        self.assertFalse((self.out / "origin" / stamp / "answers.jsonl").exists())

    def test_the_sittings_not_complete_on_the_lives_tape_skips_the_origin_exit_2_R4c(self) -> None:
        # the life's tape is cut after the first set's end: the second sitting has not happened yet
        for f in (self.life.root / "tape").glob("*.jsonl"):
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            f.write_text("\n".join(json.dumps(r) for r in rows if r["seq"] <= 1008) + "\n")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "SKIPPED")
        self.assertIn("sittings are not complete", att["reason"])

    def test_the_orchestrator_flags_and_an_out_inside_the_life_are_refused_in_origin_mode_too(self) -> None:
        p, res, att, stamp = self.run_origin(states=self.both(), flags=("-I",))
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("-B", res["refused"])
        p, res, att, stamp = self.run_origin(states=self.both(), out=self.life.root / "o")
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("inside", res["refused"])


class TestOriginItemsMatch(OriginBase):
    """R15 at run level: a plant on the life's tape is refused at ITEMS-MATCH, by name, with NO child spawned and NO answer row written."""

    def refused_before_children(self, p, att, stamp, needle: str) -> None:
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertEqual(att["status"], "REFUSED")
        self.assertIn("ITEMS-MATCH", att["reason"])
        self.assertIn(needle, att["reason"])
        d = self.out / "origin" / stamp
        self.assertFalse((d / "answers.jsonl").exists(), "no answer row is written")
        self.assertFalse((d / "answer-spec.json").exists(), "no child was spawned")
        self.assertIsNone(self.origin_row())

    def test_plant_a_a_sitting_asks_payload_byte_changed_with_its_row_sha_updated(self) -> None:
        payload = sorted((self.life.root / "tape" / "payload").glob("*.json"))[1]
        before = payload.read_bytes()
        payload.write_text(payload.read_text().replace('"test_seed": 7', '"test_seed": 8'))
        self.assertNotEqual(before, payload.read_bytes(), "the plant must change the bytes")
        for f in (self.life.root / "tape").glob("*.jsonl"):
            rows = [json.loads(l) for l in f.read_text().splitlines()]
            for r in rows:
                if r.get("payload") == f"payload/{payload.name}":
                    r["sha"] = hashlib.sha256(payload.read_bytes()).hexdigest()
            f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.refused_before_children(p, att, stamp, "ask_digest")

    def test_plant_c_one_sitting_canvases_png_byte_changed_its_row_sha_untouched(self) -> None:
        f = sorted((self.life.root / "tape" / "payload").glob("*.png"))[1]
        before = f.read_bytes()
        f.write_bytes(before[:-1] + bytes([before[-1] ^ 1]))
        self.assertNotEqual(before, f.read_bytes(), "the plant must change the bytes")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn(f.name, att["reason"])
        self.assertFalse((self.out / "origin" / stamp / "answers.jsonl").exists())

    def test_plant_d_the_lives_world_scene_line_edited(self) -> None:
        g = self.life.root / "GENOME.genome"
        before = g.read_bytes()
        g.write_text(g.read_text().replace("seed 20261101", "seed 20261102"))
        self.assertNotEqual(before, g.read_bytes(), "the plant must change the bytes")
        p, res, att, stamp = self.run_origin(states=self.both())
        self.refused_before_children(p, att, stamp, "world_scene_line_sha")

    def test_plant_b_one_ask_rows_moment_changed(self) -> None:
        changed = 0
        for tf in sorted((self.life.root / "tape").glob("*.jsonl")):
            raw = tf.read_bytes()
            rows = [json.loads(l) for l in tf.read_text().splitlines()]
            for r in rows:
                if r["sense"] == "ask" and not changed:
                    r["meta"]["moment"] = r["meta"]["moment"] + "-x"
                    changed += 1
            tf.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
            self.assertNotEqual(raw, tf.read_bytes(), "the plant must change the bytes")
        self.assertEqual(changed, 1)
        p, res, att, stamp = self.run_origin(states=self.both())
        self.refused_before_children(p, att, stamp, "ask_digest")

    def test_plant_e_one_ask_row_removed(self) -> None:
        removed = 0
        for tf in sorted((self.life.root / "tape").glob("*.jsonl")):
            raw = tf.read_bytes()
            rows = [json.loads(l) for l in tf.read_text().splitlines()]
            victim = next(r for r in rows if r["sense"] == "ask" and r["meta"]["form"] == "point")
            rows.remove(victim)
            removed += 1
            tf.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
            self.assertNotEqual(raw, tf.read_bytes(), "the plant must change the bytes")
        self.assertEqual(removed, 1)
        p, res, att, stamp = self.run_origin(states=self.both())
        self.refused_before_children(p, att, stamp, "n_asks")

    def test_plant_f_one_sitting_canvas_replaced_by_another_valid_picture_with_its_row_sha_updated(self) -> None:
        f = sorted((self.life.root / "tape" / "payload").glob("*.png"))[1]
        before = f.read_bytes()
        f.write_bytes(png(201, 101, 51))
        self.assertNotEqual(before, f.read_bytes(), "the plant must change the bytes")
        new_sha = hashlib.sha256(f.read_bytes()).hexdigest()
        changed = 0
        for tf in (self.life.root / "tape").glob("*.jsonl"):
            rows = [json.loads(l) for l in tf.read_text().splitlines()]
            for r in rows:
                if r.get("payload") == f"payload/{f.name}":
                    r["sha"] = new_sha
                    changed += 1
            tf.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        self.assertEqual(changed, 1)
        p, res, att, stamp = self.run_origin(states=self.both())
        self.refused_before_children(p, att, stamp, "canvas_digest")


class TestOriginFallback(OriginBase):
    REASON = "the seat's reason: the scene world ended at 19:02 and the rebuild's pilot priced above 4 CPU-h"

    def test_a_fallback_origin_from_the_lives_state_prev_needs_the_reason_and_is_labelled(self) -> None:
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        o = self.origin_row()
        self.assertEqual((o["origin_kind"], o["reason"]), ("fallback_copy", self.REASON))
        self.assertIn("FALLBACK ORIGIN — late by at most one snapshot", o["label"])
        self.assertEqual(o["origin_n_learned_fresh_begin"], 10)
        self.assertEqual(len(o["states"]), 1)
        self.assertEqual(o["states"][0]["set"], "*")

    def test_a_fallback_from_a_copy_directory_has_its_snapshot_prints_checked_R4b(self) -> None:
        d = self.base / "seat-copy"
        shutil.copytree(self.life.root / "state" / "prev", d)
        f = d / "brain.json"
        st = f.stat()
        os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
        self.assertNotEqual(f.stat().st_mtime_ns, st.st_mtime_ns, "the plant must change the mtime")
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON, states=[str(d)])
        self.assertEqual(p.returncode, 2, p.stderr + p.stdout)
        self.assertIn("mtime_ns", att["reason"])

    def test_r9_is_a_reading_for_a_fallback_a_differing_brain_is_printed_never_a_refusal(self) -> None:
        d = self.base / "seat-copy-9"
        shutil.copytree(self.life.root / "state" / "prev", d)
        import numpy as np
        with open(d / "brain.npz", "wb") as fh:
            np.savez(fh, v=np.array([9.0, 2.0, 3.0]))
        meta = json.loads((d / "brain.json").read_text())
        meta["state_hash"] = hashlib.sha256(np.array([9.0, 2.0, 3.0]).tobytes()).hexdigest()
        (d / "brain.json").write_text(json.dumps(meta))
        snap = json.loads((d / "SNAPSHOT.json").read_text())
        for n in ("brain.json", "brain.npz"):
            stt = (d / n).stat()
            snap["prints"][n] = [stt.st_size, stt.st_mtime_ns]
        (d / "SNAPSHOT.json").write_text(json.dumps(snap))
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON, states=[str(d)])
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        r9 = self.origin_row()["r9"]
        self.assertFalse(r9["refusing"])
        self.assertGreater(r9["early_diff_count"], 0, "the late copy answers differently; printed, labelled")
        self.assertIn("FALLBACK", r9["label"])

    def test_a_daily_row_paired_against_a_fallback_origin_prints_the_label_S3(self) -> None:
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        args = [sys.executable, "-B", "-I", str(RESIT_PY), "run", "--mode", "daily", "--root", str(self.life.root), "--code", str(self.life.code), "--items-root", str(self.items_root),
                "--grader-code", str(self.life.grader), "--out", str(self.out), "--scored", str(self.life.scored), "--stamp", "20261005T000000Z", "--copy-retry-sleep-s", "0"]
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(ENV)
        q = subprocess.run(args, capture_output=True, text=True, env=env, cwd=str(self.base))
        self.assertEqual(q.returncode, 0, q.stderr + q.stdout)
        d = self.series()[-1]
        self.assertIn("FALLBACK ORIGIN — late by at most one snapshot", d["vs_origin_fallback_label"])
        self.assertEqual(d["vs_origin_fallback_reason"], self.REASON)


class TestOriginFallbackGenomeInForce(OriginBase):
    """§1.2: for a fallback copy the genome in force is the highest epoch whose row seq is <= the state's last_seq (the daily rule); an adoption AFTER the snapshot is not in force. The stub snapshot's last_seq is 9000."""
    REASON = "the seat's words: the scene stream ended; the copy was taken at 19:30"

    def with_epoch(self, seq: int) -> str:
        text = GENOME_ORIGIN + "KWTA 4\n"
        (self.life.root / "GENOME.v1.genome").write_text(text)
        self.life.rewrite_journal(lambda rows: rows + [epoch_row(seq, 1, text)])
        return text

    def test_an_epoch_adopted_before_the_states_last_seq_is_the_genome_in_force(self) -> None:
        text = self.with_epoch(5000)
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        path = self.origin_row()["genome"]["sets"]["*"]["path"]
        self.assertTrue(path.endswith("GENOME.v1.genome"), path)
        self.assertEqual(Path(path).read_text(), text, "the in-force genome file is the copy's GENOME.v1.genome")

    def test_an_epoch_adopted_after_the_states_last_seq_is_not_yet_in_force(self) -> None:
        self.with_epoch(9500)
        p, res, att, stamp = self.run_origin(kind="fallback_copy", reason=self.REASON)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        path = self.origin_row()["genome"]["sets"]["*"]["path"]
        self.assertTrue(path.endswith("GENOME.genome") and not path.endswith("v1.genome"), path)


class TestOriginIsReadOnlyForTheLife(OriginBase):
    def test_nothing_is_written_under_the_live_life_sizes_and_mtimes_are_unchanged(self) -> None:
        before = {str(p.relative_to(self.life.root)): (p.stat().st_size, p.stat().st_mtime_ns) for p in self.life.root.rglob("*") if p.is_file()}
        p, res, att, stamp = self.run_origin(states=self.both())
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        after = {str(p.relative_to(self.life.root)): (p.stat().st_size, p.stat().st_mtime_ns) for p in self.life.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


class TestR9Reading(unittest.TestCase):
    """`r9_reading`: the ONE line of the origin ROW that says what R9 showed (law R9: «the series row says so»). A set with no tested EARLY item reads UNTESTED first and is never summarised as a pass. Pure."""

    @staticmethod
    def r9(tested_fresh=3, tested_s1b1=3, *, structural=4, refusing=True, tested_diff=0, structural_diff=0, late_total=0, late_disc=0) -> dict:
        """The TESTED and the STRUCTURAL (begin, end) EARLY rows are counted apart, as r9_cross_check counts them."""
        def one(n_tested):
            return {"n_early": n_tested + 2, "n_late": 0, "n_early_tested": n_tested, "untested": n_tested == 0,
                    "note": "R9 UNTESTED for this set (no tested EARLY item): its begin state is verified only by R10c" if n_tested == 0 else ""}
        tt, st = tested_fresh + tested_s1b1, structural
        return {"refusing": refusing, "early_tested_total": tt, "early_tested_equal": tt - tested_diff, "early_structural_total": st, "early_structural_equal": st - structural_diff,
                "early_total": tt + st, "early_equal": tt + st - tested_diff - structural_diff, "early_diff_count": tested_diff + structural_diff,
                "late_total": late_total, "late_discordant": late_disc, "by_set": {"fresh": one(tested_fresh), "s1b1": one(tested_s1b1)}}

    def test_every_set_tested_and_exact_reads_exact_with_the_tested_and_the_structural_counts_apart(self) -> None:
        line, untested = R.r9_reading(self.r9())
        self.assertEqual(untested, [])
        self.assertTrue(line.startswith("R9 EXACT on 6 of 6 TESTED EARLY items"), line)
        self.assertIn("the structural begin/end rows equal on 4 of 4 (not counted as tests)", line)
        self.assertIn("fresh 3, s1b1 3", line, "the tested EARLY count of each set is printed beside the pass")
        self.assertNotIn("10 of 10", line, "the structural rows are never in the denominator of a TESTED count")
        self.assertNotIn("UNTESTED", line)

    def test_the_two_counts_move_apart_a_structural_difference_leaves_the_tested_count_alone(self) -> None:
        line, _ = R.r9_reading(self.r9(structural_diff=1))
        self.assertIn("R9 EXACT on 6 of 6 TESTED EARLY items", line)
        self.assertIn("the structural begin/end rows equal on 3 of 4", line)
        line2, _ = R.r9_reading(self.r9(tested_diff=2))
        self.assertIn("on 4 of 6 TESTED EARLY items", line2, "the plant (two tested rows differ) changes the tested count and only it")
        self.assertIn("equal on 4 of 4", line2)

    def test_one_untested_set_leads_the_line_and_is_not_a_pass(self) -> None:
        line, untested = R.r9_reading(self.r9(tested_fresh=0, structural=3))
        self.assertEqual(untested, ["fresh"])
        self.assertTrue(line.startswith("R9 UNTESTED for set(s) fresh"), line)
        self.assertIn("NOT A PASS", line)
        self.assertIn("R10c", line)
        self.assertFalse(line.startswith("R9 EXACT"))
        self.assertIn("R9 EXACT on 3 of 3 TESTED EARLY items", line, "the exactness it still claims is over the TESTED rows alone")
        self.assertIn("equal on 3 of 3 (not counted as tests)", line)

    def test_every_untested_set_is_named(self) -> None:
        line, untested = R.r9_reading(self.r9(tested_fresh=0, tested_s1b1=0))
        self.assertEqual(untested, ["fresh", "s1b1"])
        self.assertTrue(line.startswith("R9 UNTESTED for set(s) fresh, s1b1"), line)

    def test_the_line_reads_the_untested_flag_not_a_constant_the_plant_changes_the_line(self) -> None:
        a, b = R.r9_reading(self.r9(tested_fresh=3))[0], R.r9_reading(self.r9(tested_fresh=0))[0]
        self.assertNotEqual(a, b, "the plant (one set's tested count 3 -> 0) must change the reading")

    def test_a_fallback_is_a_labelled_reading_never_exact_and_still_names_an_untested_set(self) -> None:
        line, untested = R.r9_reading(self.r9(tested_fresh=0, tested_s1b1=6, refusing=False, tested_diff=4))
        self.assertEqual(untested, ["fresh"])
        self.assertIn("READING", line)
        self.assertIn("4 of 6 TESTED EARLY items differ", line)
        self.assertIn("the structural begin/end rows differ on 0 of 4 (not counted as tests)", line)
        self.assertNotIn("EXACT", line)
        self.assertIn("UNTESTED", line)

    def test_late_items_are_counted_in_the_line(self) -> None:
        line, _ = R.r9_reading(self.r9(late_total=7, late_disc=2))
        self.assertIn("LATE items 7, discordant 2", line)


class TestR9Omissions(unittest.TestCase):
    """The life's answer rows that have NO origin row are counted (an origin that skipped an item must not read as an equal one), and the line says so. Pure."""
    ASKS = [{"seq": 10, "set": "fresh", "form": "begin"}, {"seq": 11, "set": "fresh", "form": "point"}, {"seq": 12, "set": "fresh", "form": "end"}]

    def life(self, *seqs):
        forms = {10: "begin", 11: "point", 12: "end", 99: "point"}
        return {s: ans(s, f"M1:{s}", form=forms[s], eye_seq=None) for s in seqs}

    def cross(self, origin_seqs, life_seqs):
        life = self.life(*life_seqs)
        origin = [dict(life[s]) for s in origin_seqs]
        return R.r9_cross_check(origin, life, {s: "EARLY" for s in life_seqs}, self.ASKS, refusing=True)

    def test_an_origin_row_missing_for_a_life_row_of_a_sitting_ask_is_counted_and_named(self) -> None:
        r9 = self.cross(origin_seqs=(10, 12), life_seqs=(10, 11, 12))
        self.assertEqual((r9["life_rows_not_resat"], r9["first_life_row_not_resat"]), (1, 11))
        self.assertEqual(r9["early_diff_count"], 0, "the rows that exist are equal: only the omission is the finding")

    def test_tested_and_structural_early_rows_are_counted_apart_by_form(self) -> None:
        r9 = self.cross(origin_seqs=(10, 11, 12), life_seqs=(10, 11, 12))
        self.assertEqual((r9["early_tested_total"], r9["early_tested_equal"], r9["early_structural_total"], r9["early_structural_equal"]), (1, 1, 2, 2),
                         "one point (tested) and begin + end (structural), all equal")
        life = self.life(10, 11, 12)
        origin = [dict(life[s]) for s in (10, 11, 12)]
        origin[1] = {**origin[1], "answer": {"kind": "thing", "hyp": 9}}                          # the plant: the TESTED row differs
        r9 = R.r9_cross_check(origin, life, {s: "EARLY" for s in (10, 11, 12)}, self.ASKS, refusing=True)
        self.assertEqual((r9["early_tested_total"], r9["early_tested_equal"], r9["early_structural_total"], r9["early_structural_equal"]), (1, 0, 2, 2))
        self.assertEqual(r9["early_diff_count"], 1)

    def test_the_control_a_complete_origin_counts_zero(self) -> None:
        r9 = self.cross(origin_seqs=(10, 11, 12), life_seqs=(10, 11, 12))
        self.assertEqual((r9["life_rows_not_resat"], r9["first_life_row_not_resat"]), (0, None))

    def test_a_life_row_that_is_not_a_sitting_ask_is_not_counted(self) -> None:
        r9 = self.cross(origin_seqs=(10, 11, 12), life_seqs=(10, 11, 12, 99))                     # seq 99 is no ask of the sittings: the life answered something else
        self.assertEqual(r9["life_rows_not_resat"], 0)

    def test_the_reading_line_says_it_whenever_a_count_is_not_zero(self) -> None:
        base = TestR9Reading.r9()
        clean, _ = R.r9_reading({**base, "life_rows_not_resat": 0, "n_without_a_life_row_or_class": 0})
        self.assertNotIn("have no origin row", clean)
        self.assertNotIn("had no life row", clean)
        a, _ = R.r9_reading({**base, "life_rows_not_resat": 3, "n_without_a_life_row_or_class": 0})
        self.assertIn("3 of the life's own answer rows have no origin row", a)
        b, _ = R.r9_reading({**base, "life_rows_not_resat": 0, "n_without_a_life_row_or_class": 2})
        self.assertIn("2 origin rows had no life row or class", b)


class TestStatesBySet(unittest.TestCase):
    """`states_by_set`: law §1.1 S2 — `--state SET=DIR` once per sitting set, or ONE bare `--state DIR` that serves every set; mixed, repeated, unknown or missing names are refused by name. Pure."""
    ORDERED = ["fresh", "s1b1"]

    def sp(self, *specs):
        return R.parse_state_specs(list(specs))

    def test_named_dirs_one_per_sitting_set(self) -> None:
        self.assertEqual(R.states_by_set(self.sp("fresh=/a", "s1b1=/b"), self.ORDERED), {"fresh": Path("/a"), "s1b1": Path("/b")})

    def test_a_bare_dir_serves_every_set(self) -> None:
        self.assertEqual(R.states_by_set(self.sp("/a"), self.ORDERED), {"fresh": Path("/a"), "s1b1": Path("/a")})

    def test_the_order_of_the_flags_does_not_matter(self) -> None:
        self.assertEqual(R.states_by_set(self.sp("s1b1=/b", "fresh=/a"), self.ORDERED), {"fresh": Path("/a"), "s1b1": Path("/b")})

    def test_every_other_assignment_is_refused_by_name(self) -> None:
        cases = {
            "a bare dir beside a named one": (self.sp("/a", "s1b1=/b"), "bare"),
            "two bare dirs": (self.sp("/a", "/b"), "bare"),
            "a set named twice": (self.sp("fresh=/a", "fresh=/b", "s1b1=/c"), "twice"),
            "a set with no state": (self.sp("fresh=/a"), "s1b1"),
            "a name that is no sitting set": (self.sp("fresh=/a", "s1b1=/b", "zog=/c"), "zog"),
        }
        for label, (specs, needle) in cases.items():
            with self.subTest(label):
                with self.assertRaises(R.Refused) as cm:
                    R.states_by_set(specs, self.ORDERED)
                self.assertIn(needle, str(cm.exception))


if __name__ == "__main__":
    unittest.main()
