# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:27 +0400 — PREREG-HEARS-2 AMENDMENT 1 §A1.7 (D2): tools/lives/hears_d2_read.py, the read of a pre-flight life's own files after its kill and resume, written test-first on a
# fake life root built from the real pre-flight genome. Each fault the clause names (the maker's count restarting at a resume, a re-learned moment carrying another index, a wrong derived seed, a census that
# disagrees with the journal) is planted in the bytes of a file and must FAIL the read; a read with nothing to grade says NOT GRADABLE, never PASS.
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
WS = world_seed_of(20261101, "maker")


def _learn(moment, seq, world=None, scene=None, ws=None):
    r = {"kind": "brain", "act": "learn", "moment": moment, "seq": seq, "at": "t", "words": ["star"], "n_hyp": 1, "calibrated": False}
    if world is not None:
        r.update({"world": world, "scene": scene, "world_seed": ws})
    return r


def _start(resumed_from_seq):
    return {"seq": None, "at": "t", "event": "start", "resumed_from_seq": resumed_from_seq, "backlog_replayed": 0}


def timeline(reset=False, relearn_scene=None, ws_after=WS, resume=True, maker_after=True):
    """S0 M0 S1 M1 S2 M2 S3 M3 S4 M4 | the resume | M3 and M4 learned AGAIN (the journal's residual), then S5 M5 S6 M6 S7 M7. Distinct learned moments in order: 16, eight of them the maker's (scene
    index 0..7). `reset`: after the resume the maker's count restarts at 0 (the fault). `relearn_scene`: the re-learned M3 carries that index."""
    rows, seq = [_start(0)], 100
    for i in range(5):
        rows += [_learn(f"s{i}", seq), _learn(f"m{i}", seq + 1, "maker", i, WS)]
        seq += 2
    if resume:
        rows.append(_start(seq - 1))
    if maker_after:
        rows += [_learn("m3", seq, "maker", 3 if relearn_scene is None else relearn_scene, ws_after), _learn("m4", seq + 1, "maker", 4, ws_after)]
        seq += 2
        for k, i in enumerate(range(5, 8)):
            rows += [_learn(f"s{i}", seq), _learn(f"m{i}", seq + 1, "maker", (k if reset else i), ws_after)]
            seq += 2
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


class Clean(Tmp):
    def test_a_resumed_life_that_kept_the_count_passes_and_every_control_is_caught(self) -> None:
        root = build(self.mk(), timeline())
        rc, out = run(root)
        self.assertEqual(rc, 0, out)
        r = D.analyse_root(root)
        self.assertEqual((r["resumes"], r["maker_rows"], r["maker_moments"], r["relearned_rows"]), (1, 10, 8, 2))
        self.assertEqual((r["maker_rows_before_first_resume"], r["maker_rows_after_last_resume"]), (5, 5))
        self.assertEqual(r["violations"], [])
        (first,) = r["first_maker_row_after_each_resume"]
        self.assertEqual((first["moment"], first["scene"], first["relearned"], first["ok"]), ("m3", 3, True, True))
        self.assertEqual([c["scenes"] for c in r["census"]], [10, 16])
        self.assertTrue(all(c["ok"] for c in r["census"]))
        self.assertEqual(r["world_seed_expected"], WS)
        self.assertEqual(r["controls"], {"reset": "CAUGHT", "seed": "CAUGHT", "census": "CAUGHT"})
        self.assertEqual(r["verdict"], "PASS")
        for needle in ("D2 PASS", "controls", "(a)", "(b)", "(c)"):
            self.assertIn(needle, out)

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

    def test_a_relearned_moment_with_another_index_fails_b(self) -> None:
        root = self._faulty(relearn_scene=9)
        r = D.analyse_root(root)
        self.assertEqual(r["verdict"], "FAIL")
        (v,) = [x for x in r["violations"] if x["kind"] == "relearned_moment_differs"]
        self.assertEqual((v["moment"], v["was"], v["now"]), ("m3", [3, WS], [9, WS]))
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
        rows += [_learn("m0", 600, "maker", 0, WS), _learn("m1", 601, "maker", 1, WS), _start(700), _learn("m1", 701, "maker", 1, WS), _learn("m2", 702, "maker", 2, WS)]
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
        blind = lambda rows_, ws_, cen_: {"resumes": 1, "resume_rows": [11], "bracketed_resumes": 1, "maker_rows": 10, "maker_moments": 8, "relearned_rows": 2, "maker_rows_before_first_resume": 5,
                                            "maker_rows_after_last_resume": 5, "first_maker_row_after_each_resume": [], "census": [], "violations": []}
        orig = D.check
        try:
            D.check = blind
            r = D.analyse_root(root)
            rc, out = run(root)
        finally:
            D.check = orig
        self.assertEqual(set(r["controls"].values()), {"MISSED"})
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("MISSED", r["why"])
        self.assertEqual(rc, 1, out)
        self.assertEqual(D.analyse_root(root)["verdict"], "PASS", "and the real check, restored, reads the same life as clean")


class Controls(unittest.TestCase):
    def test_the_controls_are_blind_without_their_fault_and_see_it_with(self) -> None:
        rows = timeline()
        ctl = D.run_controls(rows, WS, CENSUS)
        self.assertEqual(ctl, {"reset": "CAUGHT", "seed": "CAUGHT", "census": "CAUGHT"})
        # a checker that ignored the seed would MISS the seed plant: prove the control reports a miss when the check cannot see its plant
        orig = D.check
        try:
            D.check = lambda rows_, ws_, cen_: {"violations": [], "census": [], "relearned_rows": 0}
            self.assertEqual(set(D.run_controls(rows, WS, CENSUS).values()), {"MISSED"})
        finally:
            D.check = orig


if __name__ == "__main__":
    unittest.main()
