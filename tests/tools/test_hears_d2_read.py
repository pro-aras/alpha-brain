# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:27 +0400 — PREREG-HEARS-2 AMENDMENT 1 §A1.7 (D2): tools/lives/hears_d2_read.py, the read of a pre-flight life's own files after its kill and resume, written test-first on a
# fake life root built from the real pre-flight genome. Each fault the clause names (the maker's count restarting at a resume, a re-consumed row carrying another index, a wrong derived seed, a census that disagrees with
# the journal) is planted in the bytes of a file and must FAIL the read; a read with nothing to grade says NOT GRADABLE, never PASS.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:04 +0400 — AMENDMENT 3: the FIRST REAL pre-flight (the seat's, 11:55) read FAIL with 16 false violations because the checker keyed a canvas by its moment NAME and the maker
# world redraws its first pictures under the SAME names on NEW tape rows after every restart (creature/world_maker.py sense() keeps window / i / total in the thread's memory). The real life's rows are now a FIXTURE
# (tests/fixtures/hears_d2/…, red on the name-keyed checker, green on the seq-keyed one); the synthetic timeline models the real facts (a re-consumed row keeps its seq and is journaled BEFORE the `start` row; a restarted maker
# reuses names on new seqs); a fourth control reads a redrawn canvas as NEW.
"""tests/tools/test_hears_d2_read.py — tools/lives/hears_d2_read.py."""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from genome.brain import world_seed_of
from tools.lives import hears_d2_read as D

REPO = Path(__file__).resolve().parents[2]
GENOME = REPO / "genome" / "brain" / "lives" / "BRAIN-LONG-3-PREFLIGHT.genome"
FIXTURE = REPO / "tests" / "fixtures" / "hears_d2" / "preflight-brain-long-3-pre-1.json"
WS = world_seed_of(20261101, "maker")


def _learn(moment, seq, world=None, scene=None, ws=None):
    r = {"kind": "brain", "act": "learn", "moment": moment, "seq": seq, "at": "t", "words": ["star"], "n_hyp": 1, "calibrated": False}
    if world is not None:
        r.update({"world": world, "scene": scene, "world_seed": ws})
    return r


def _start(resumed_from_seq):
    return {"seq": None, "at": "t", "event": "start", "resumed_from_seq": resumed_from_seq, "backlog_replayed": 0}


def timeline(reset=False, relearn_scene=None, ws_after=WS, resume=True, maker_after=True, redraw=0, replay_before_start=False):
    """S0 M0 S1 M1 S2 M2 S3 M3 S4 M4 | the resume | M3 and M4 journaled AGAIN (the same tape rows re-consumed: the SAME seqs, the days law's residual), then S5 M5 S6 M6 S7 M7. Distinct tape rows in order: 16,
    eight of them the maker's (scene index 0..7). `reset`: after the resume the maker's count restarts at 0 (the fault). `relearn_scene`: the re-consumed M3 carries that index. `redraw`: after the resume the maker WORLD
    restarted — that many of its first pictures again, under their OLD names, on NEW tape rows (each takes the next index). `replay_before_start`: the startup replay writes the re-consumed rows BEFORE the `start` row (the real order)."""
    rows, seq, mseq = [_start(0)], 100, {}
    for i in range(5):
        rows += [_learn(f"s{i}", seq), _learn(f"m{i}", seq + 1, "maker", i, WS)]
        mseq[i] = seq + 1
        seq += 2
    replay = [_learn("m3", mseq[3], "maker", 3 if relearn_scene is None else relearn_scene, ws_after), _learn("m4", mseq[4], "maker", 4, ws_after)]
    if resume and replay_before_start and maker_after:
        rows += replay
    if resume:
        rows.append(_start(seq - 1))
    if maker_after:
        if not (resume and replay_before_start):
            rows += replay
        nxt = 0 if reset else 5
        for k in range(redraw):
            rows.append(_learn(f"m{k}", seq, "maker", nxt, ws_after))
            seq += 1
            nxt += 1
        for i in range(5, 8):
            rows += [_learn(f"s{i}", seq), _learn(f"m{i}", seq + 1, "maker", nxt, ws_after)]
            seq += 2
            nxt += 1
    return rows


def census(n, maker):
    return {"scenes": n, "scenes_by_world": {"maker": maker, "scene": n - maker}, "n_words": 14}


CENSUS = {10: census(10, 5), 16: census(16, 8)}


def build(root: Path, rows, census_files=CENSUS, genome=GENOME):
    root = Path(root)
    (root / "journal").mkdir(parents=True, exist_ok=True)
    (root / "census").mkdir(parents=True, exist_ok=True)
    (root / "GENOME.genome").write_text(Path(genome).read_text())
    (root / "journal" / "2026-10-03.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    for n, c in census_files.items():
        (root / "census" / f"{n:08d}.json").write_text(json.dumps(c, sort_keys=True) + "\n")
    return root


def run(root):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = D.main([str(root)])
    return rc, buf.getvalue()


class Tmp(unittest.TestCase):
    def mk(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="hears-d2-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d


def build_from_fixture(root: Path):
    """The REAL pre-flight life of 2026-10-03 (three resumes), reduced to the rows the checker reads — built into a root with the real pre-flight genome."""
    fx = json.loads(FIXTURE.read_text())
    return build(root, fx["rows"], {int(n): c for n, c in fx["census"].items()})


class RealPreflight(Tmp):
    """The first real D2 (the seat's pre-flight, 11:55) read FAIL with 16 violations: the checker keyed «the same canvas» by the moment NAME, and the maker world keeps window / i / total in the
    sense thread's memory (creature/world_maker.py sense()), so after every resume it redraws its first pictures under the SAME names on NEW tape rows. The mind was right: each new tape row took
    the next index, and the rows re-consumed after the last resume (seq 5925 / 5931 / 5949) carried 9 / 10 / 11 again."""

    def test_the_real_preflight_reads_pass_a_redrawn_canvas_is_a_new_canvas(self) -> None:
        r = D.analyse_root(build_from_fixture(self.mk()))
        self.assertEqual(r["verdict"], "PASS", r["violations"][:4])
        self.assertEqual((r["resumes"], r["bracketed_resumes"]), (3, 3))
        self.assertEqual(r["relearned_rows"], 3)                           # by SEQ: 5925 / 5931 / 5949 journaled twice, scene 9 / 10 / 11 both times
        self.assertGreater(r["moment_ids_reused"], 0)                      # the maker's names repeated on new tape rows: counted, never a violation
        self.assertEqual((r["maker_rows"], r["maker_tape_rows"]), (55, 52))
        self.assertEqual(r["violations"], [])
        first = r["first_maker_row_after_each_resume"]
        self.assertEqual([f["scene"] for f in first], [2, 6, 12])          # each a NEW tape row that re-uses the name …i000001t000000000
        self.assertTrue(all(f["ok"] and not f["replayed"] and f["name_reused"] for f in first))
        self.assertEqual(r["controls"], {"reset": "CAUGHT", "seed": "CAUGHT", "census": "CAUGHT", "redrawn": "NEW"})

    def test_the_same_real_rows_with_the_count_restarted_at_the_last_resume_fail(self) -> None:
        fx = json.loads(FIXTURE.read_text())
        rows = fx["rows"]
        start = [i for i, r in enumerate(rows) if r.get("event") == "start"][-1]
        planted = json.loads(json.dumps(rows))
        k = 0
        for r in planted[start:]:
            if r.get("world") == "maker":
                r["scene"] = k                                             # the plant: after the last resume the maker's count restarts at 0
                k += 1
        self.assertNotEqual(json.dumps(planted), json.dumps(rows), "the plant must change the rows")
        r = D.analyse_root(build(self.mk(), planted, {int(n): c for n, c in fx["census"].items()}))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("count_does_not_continue", {v["kind"] for v in r["violations"]})

    def test_the_same_real_rows_with_a_reconsumed_row_given_another_index_fail(self) -> None:
        fx = json.loads(FIXTURE.read_text())
        planted = json.loads(json.dumps(fx["rows"]))
        twice = [r for r in planted if r.get("world") == "maker" and r["seq"] == 5925]
        self.assertEqual(len(twice), 2)
        twice[1]["scene"] = 99                                              # the second journaling of seq 5925 (scene 9) carries 99
        self.assertNotEqual(json.dumps(planted), json.dumps(fx["rows"]), "the plant must change the rows")
        r = D.analyse_root(build(self.mk(), planted, {int(n): c for n, c in fx["census"].items()}))
        self.assertEqual(r["verdict"], "FAIL")
        (v,) = [x for x in r["violations"] if x["kind"] == "relearned_row_differs"]
        self.assertEqual((v["seq"], v["was"][0], v["now"][0]), (5925, 9, 99))


class Clean(Tmp):
    def test_a_resumed_life_that_kept_the_count_passes_and_every_control_is_caught(self) -> None:
        root = build(self.mk(), timeline())
        rc, out = run(root)
        self.assertEqual(rc, 0, out)
        r = D.analyse_root(root)
        self.assertEqual((r["resumes"], r["maker_rows"], r["maker_tape_rows"], r["maker_moments"], r["relearned_rows"], r["moment_ids_reused"]), (1, 10, 8, 8, 2, 0))
        self.assertEqual((r["maker_rows_before_first_resume"], r["maker_rows_after_last_resume"]), (5, 5))
        self.assertEqual(r["violations"], [])
        (first,) = r["first_maker_row_after_each_resume"]
        self.assertEqual((first["moment"], first["scene"], first["replayed"], first["name_reused"], first["ok"]), ("m3", 3, True, False, True))
        self.assertEqual([c["scenes"] for c in r["census"]], [10, 16])
        self.assertTrue(all(c["ok"] for c in r["census"]))
        self.assertEqual(r["world_seed_expected"], WS)
        self.assertEqual(r["controls"], {"reset": "CAUGHT", "seed": "CAUGHT", "census": "CAUGHT", "redrawn": "NEW"})
        self.assertEqual(r["verdict"], "PASS")
        for needle in ("D2 PASS", "controls", "(a)", "(b)", "(c)"):
            self.assertIn(needle, out)

    def test_the_startup_replay_writing_its_rows_before_the_start_row_is_the_same_life(self) -> None:
        # the real order: the re-consumed rows are journaled BEFORE the `start` row, so the first maker row AFTER it is a new tape row
        root = build(self.mk(), timeline(replay_before_start=True))
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "PASS", r["violations"])
        (first,) = r["first_maker_row_after_each_resume"]
        self.assertEqual((first["moment"], first["scene"], first["replayed"], first["ok"]), ("m5", 5, False, True))
        self.assertEqual(r["relearned_rows"], 2)

    def test_a_restarted_maker_redraws_its_first_pictures_under_the_same_names_and_that_is_not_a_fault(self) -> None:
        root = build(self.mk(), timeline(redraw=3), {10: census(10, 5), 19: census(19, 11)})
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "PASS", r["violations"])
        self.assertEqual((r["maker_rows"], r["maker_tape_rows"], r["maker_moments"], r["moment_ids_reused"], r["relearned_rows"]), (13, 11, 8, 3, 2))
        self.assertEqual([c["ok"] for c in r["census"]], [True, True])
        # the first maker row after the resume here is the replayed m3; the redrawn m0 comes next with the NEXT index (5), not its old one (0)
        rows = timeline(redraw=3)
        redrawn = [x for x in rows if x.get("world") == "maker" and x["moment"] == "m0"]
        self.assertEqual([x["scene"] for x in redrawn], [0, 5])
        self.assertNotEqual(redrawn[0]["seq"], redrawn[1]["seq"])

    def test_torn_lines_from_a_power_cut_are_counted_not_fatal(self) -> None:
        root = build(self.mk(), timeline())
        p = root / "journal" / "2026-10-03.jsonl"
        before = p.read_bytes()
        with p.open("ab") as f:
            f.write(b'{"kind": "brain", "act": "le\n' + b"\x00" * 64 + b"\n")
        self.assertNotEqual(p.read_bytes(), before, "the plant must change the bytes")
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["torn_lines"], 2)


class Faults(Tmp):
    def _faulty(self, **kw):
        clean_dir, bad_dir = self.mk(), self.mk()
        census_files = kw.pop("census_files", CENSUS)
        build(clean_dir, timeline())
        build(bad_dir, timeline(**kw), census_files)
        self.assertNotEqual((clean_dir / "journal" / "2026-10-03.jsonl").read_bytes() + b"".join(p.read_bytes() for p in sorted((clean_dir / "census").glob("*.json"))),
                            (bad_dir / "journal" / "2026-10-03.jsonl").read_bytes() + b"".join(p.read_bytes() for p in sorted((bad_dir / "census").glob("*.json"))),
                            "the plant must change the bytes")
        return bad_dir

    def test_the_makers_count_restarting_at_the_resume_fails_a(self) -> None:
        root = self._faulty(reset=True)
        rc, out = run(root)
        self.assertEqual(rc, 1, out)
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        kinds = {v["kind"] for v in r["violations"]}
        self.assertIn("count_does_not_continue", kinds)
        first_new = next(v for v in r["violations"] if v["kind"] == "count_does_not_continue")
        self.assertEqual((first_new["moment"], first_new["scene"], first_new["expected"]), ("m5", 0, 5))
        self.assertIn("D2 FAIL", out)

    def test_a_redrawn_canvas_whose_count_restarted_fails_a_whatever_its_name(self) -> None:
        root = self._faulty(redraw=3, reset=True, census_files={10: census(10, 5), 19: census(19, 11)})
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        first_new = next(v for v in r["violations"] if v["kind"] == "count_does_not_continue")
        self.assertEqual((first_new["moment"], first_new["scene"], first_new["expected"]), ("m0", 0, 5))

    def test_a_reconsumed_row_with_another_index_fails_b(self) -> None:
        root = self._faulty(relearn_scene=9)
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        (v,) = [x for x in r["violations"] if x["kind"] == "relearned_row_differs"]
        self.assertEqual((v["moment"], v["seq"], v["was"], v["now"]), ("m3", 107, [3, WS], [9, WS]))
        self.assertFalse(r["first_maker_row_after_each_resume"][0]["ok"])

    def test_a_wrong_derived_seed_fails(self) -> None:
        root = self._faulty(ws_after=WS + 1)
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("world_seed", {v["kind"] for v in r["violations"]})

    def test_a_census_that_disagrees_with_the_journal_fails_c(self) -> None:
        root = self._faulty(census_files={10: census(10, 5), 16: census(16, 9)})
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        bad = [c for c in r["census"] if not c["ok"]]
        self.assertEqual([(c["scenes"], c["maker_expected"], c["maker_got"]) for c in bad], [(16, 8, 9)])

    def test_a_census_that_counts_more_scenes_than_the_journal_holds_fails(self) -> None:
        root = self._faulty(census_files={10: census(10, 5), 99: census(99, 40)})
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(any(c["scenes"] == 99 and not c["ok"] and "fewer" in c["why"] for c in r["census"]))

    def test_the_census_counts_tape_rows_not_names(self) -> None:
        # with the maker redrawing its names, a census counted by NAME would read 8 where the brain learned 11
        root = build(self.mk(), timeline(redraw=3), {10: census(10, 5), 19: census(19, 8)})
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual([(c["scenes"], c["maker_expected"], c["maker_got"]) for c in r["census"] if not c["ok"]], [(19, 11, 8)])


class NothingToGrade(Tmp):
    def test_no_resume_in_the_journal_is_not_gradable_never_pass(self) -> None:
        root = build(self.mk(), timeline(resume=False))
        rc, out = run(root)
        self.assertEqual(rc, 3, out)
        self.assertEqual(D.analyse_root(root)["verdict"], "NOT GRADABLE")
        self.assertIn("no resume", out)

    def test_no_maker_row_after_the_resume_is_not_gradable(self) -> None:
        root = build(self.mk(), timeline(maker_after=False), {10: census(10, 5)})
        rc, out = run(root)
        self.assertEqual(rc, 3, out)
        r = D.analyse_root(root)
        self.assertEqual(r["maker_rows_after_last_resume"], 0)
        self.assertEqual(r["verdict"], "NOT GRADABLE")

    def test_one_bracketed_resume_is_enough_a_maker_silent_before_the_first_kill_is_still_gradable(self) -> None:
        # the maker publishes nothing before the FIRST resume, but the second resume has maker rows on both sides: the read grades that one
        rows = [_start(0)] + [_learn(f"s{i}", 100 + i) for i in range(4)] + [_start(500)]
        rows += [_learn("m0", 600, "maker", 0, WS), _learn("m1", 601, "maker", 1, WS), _start(700), _learn("m1", 601, "maker", 1, WS), _learn("m2", 702, "maker", 2, WS)]
        root = build(self.mk(), rows, {})
        r = D.analyse_root(root)
        self.assertEqual((r["resumes"], r["maker_rows_before_first_resume"], r["maker_rows_after_last_resume"]), (2, 0, 2))
        self.assertEqual(r["bracketed_resumes"], 1)
        self.assertEqual(r["verdict"], "PASS", r)
        # and a resume with maker rows on one side only is never bracketed
        rows2 = [_start(0), _learn("m0", 100, "maker", 0, WS), _start(500), _learn("s0", 600)]
        r2 = D.analyse_root(build(self.mk(), rows2, {}))
        self.assertEqual(r2["bracketed_resumes"], 0)
        self.assertEqual(r2["verdict"], "NOT GRADABLE")
        self.assertIn("both before and after", r2["why"])

    def test_a_root_with_no_journal_is_an_error_naming_the_path(self) -> None:
        d = self.mk()
        (d / "GENOME.genome").write_text(GENOME.read_text())
        with self.assertRaises(D.D2Error) as cm:
            D.analyse_root(d)
        self.assertIn("journal", str(cm.exception))


class BlindRead(Tmp):
    def test_a_read_that_cannot_see_its_own_plants_fails_even_when_the_life_looks_clean(self) -> None:
        # found by the mutation sweep (a mutant that ignored a MISSED control survived): the verdict itself must turn a blind read into FAIL
        root = build(self.mk(), timeline())
        blind = lambda rows_, ws_, cen_: {"resumes": 1, "resume_rows": [11], "bracketed_resumes": 1, "maker_rows": 10, "maker_tape_rows": 8, "maker_moments": 8, "moment_ids_reused": 0,
                                            "relearned_rows": 2, "maker_rows_before_first_resume": 5, "maker_rows_after_last_resume": 5, "first_maker_row_after_each_resume": [],
                                            "census": [], "violations": []}
        orig = D.check
        try:
            D.check = blind
            r = D.analyse_root(root)
            rc, out = run(root)
        finally:
            D.check = orig
        self.assertEqual(set(r["controls"].values()), {"MISSED", "MISREAD"})
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("MISSED", r["why"])
        self.assertEqual(rc, 1, out)
        self.assertEqual(D.analyse_root(root)["verdict"], "PASS", "and the real check, restored, reads the same life as clean")


class Controls(unittest.TestCase):
    def test_the_controls_are_blind_without_their_fault_and_see_it_with(self) -> None:
        rows = timeline()
        ctl = D.run_controls(rows, WS, CENSUS)
        self.assertEqual(ctl, {"reset": "CAUGHT", "seed": "CAUGHT", "census": "CAUGHT", "redrawn": "NEW"})
        # a checker that saw nothing would MISS the three plants, and would not count the redrawn canvas as a new row: prove the controls report it
        orig = D.check
        try:
            D.check = lambda rows_, ws_, cen_: {"violations": [], "census": [], "relearned_rows": 0, "maker_tape_rows": 0, "moment_ids_reused": 0}
            self.assertEqual(D.run_controls(rows, WS, CENSUS), {"reset": "MISSED", "seed": "MISSED", "census": "MISSED", "redrawn": "MISREAD"})
        finally:
            D.check = orig

    def test_the_redrawn_control_is_misread_by_a_checker_that_keys_on_names(self) -> None:
        # the first real D2's checker: a canvas identified by its NAME reads the redrawn canvas as a violation (and as a re-learned moment): the control must say MISREAD
        orig = D.check

        def by_name(rows_, ws_, cen_):
            res = orig(rows_, ws_, cen_)
            seen, bad = {}, list(res["violations"])
            for r in rows_:
                if r.get("kind") == "brain" and r.get("act") == "learn" and r.get("world") == "maker":
                    if r["moment"] in seen and seen[r["moment"]] != r["scene"]:
                        bad.append({"kind": "relearned_moment_differs"})
                    seen.setdefault(r["moment"], r["scene"])
            return {**res, "violations": bad}
        try:
            D.check = by_name
            self.assertEqual(D.run_controls(timeline(), WS, CENSUS)["redrawn"], "MISREAD")
        finally:
            D.check = orig


if __name__ == "__main__":
    unittest.main()
