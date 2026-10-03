# edit: Claude (Sonnet 5.5, swarm sleep), 2026-10-03 10:47 +0400 — tests for tools/brain/check_sleep_ab_verdict.py, written before the checker was run on any doc.
# Every instrument here carries a planted control that must be CAUGHT, and each plant asserts it changed the bytes (SOLUTIONS #247 (5)); decide() is driven
# through every branch of PREREG-SLEEP-AB §7 on synthetic readings, so the gate that decided the real reading (READ-W0-out's ≥ 30) is shown to bind.
"""tests/tools/test_check_sleep_ab_verdict.py"""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from tools.brain import check_sleep_ab_verdict as C

RUNS = C.DEFAULT_RUNS
LISTS = C.DEFAULT_LISTS
LAW = Path(__file__).resolve().parents[2] / "docs" / "brain" / "memory" / "PREREG-SLEEP-AB.md"
HAVE_RUNS = (RUNS / "READING.json").exists() and (LISTS / "READ-W0-out-list.txt").exists() and LAW.exists()


def pr(b: int, c: int) -> dict:
    z = (b - c) / math.sqrt(b + c) if b + c else 0.0
    return {"out": {"b": b, "c": c, "z": round(z, 3)}}


def base():
    """The real reading's figures as the decision function takes them (READING.json, copied by hand once; the real-data tests below recompute them from the files)."""
    marks = {
        "S": {"R-A": -0.0583, "R-B": -0.5733, "lost": 3, "out_e0": 17, "out_end": 1},
        "N": {"R-A": 0.0, "R-B": -0.48, "lost": 2, "out_e0": 19, "out_end": 3},
        "P": {"R-A": -0.0167, "R-B": -0.3933, "lost": 2, "out_e0": 11, "out_end": 2},
        "PR": {"R-A": 0.0125, "R-B": -0.0267, "lost": 0, "out_e0": 16, "out_end": 1},
    }
    ura = [-0.025, -0.0083, -0.0167, -0.0458, 0.0, -0.0292, -0.0125, -0.025, -0.0125, 0.0625]
    urb = [0.0, -0.0267, -0.02, -0.04, -0.0067, -0.0133, 0.0, -0.04, 0.0, 0.0]
    e0 = [20, 28, 20, 25, 23, 23, 18, 19, 21, 19]
    en = [4, 7, 2, 3, 2, 3, 5, 2, 6, 5]
    for d in range(10):
        marks[f"U{d + 1}"] = {"R-A": ura[d], "R-B": urb[d], "lost": 0, "out_e0": e0[d], "out_end": en[d]}
    pairs = {"P vs S": pr(1, 0), "PR vs S": pr(0, 0), "N vs S": pr(2, 0), "S vs N": pr(0, 2), "P vs N": pr(0, 1), "P vs PR": pr(1, 0),
             "U-mean vs S": {"out": {"z": 2.82}}, "U-mean vs N": {"out": {"z": 0.594}}, "P vs U-mean": {"out": {"z": -1.68}}}
    for d, (bs, cs, bn, cn) in enumerate([(3, 0, 2, 1), (6, 0, 5, 1), (1, 0, 1, 2), (2, 0, 1, 1), (1, 0, 1, 2), (2, 0, 2, 2), (4, 0, 4, 2), (1, 0, 1, 2), (5, 0, 4, 1), (4, 0, 4, 2)], 1):
        pairs[f"U{d} vs S"] = pr(bs, cs)
        pairs[f"U{d} vs N"] = pr(bn, cn)
    uband = {"R-A": {"min": -0.0458, "max": 0.0625}, "R-B": {"min": -0.04, "max": 0.0}}
    return marks, pairs, uband


class Decide(unittest.TestCase):
    """PREREG-SLEEP-AB §7, every branch, on synthetic readings. The real reading is the first row."""

    def test_the_real_reading_is_keep_and_the_gate_is_what_holds_the_u_rule_back(self):
        m, p, b = base()
        v, steps = C.decide(m, p, b)
        self.assertEqual(v, "KEEP")
        by = {s["step"]: s for s in steps}
        self.assertIn("UNDERPOWERED", by["1"]["result"])
        self.assertEqual(by["2"]["result"], "does not apply")
        self.assertEqual(by["3U"]["result"], "qualifies: False")
        self.assertIn("U-mean vs S z 2.82", by["3U"]["reading"], "the figure that looks like a U win is printed in the walk, with the gate beside it")

    def test_the_gate_binds_the_same_reading_gradable_changes_the_line_under_the_loose_reading_of_each_draw_beat_s(self):
        m, p, b = base()
        m["S"]["out_e0"] = 31                                 # PLANT: S at the bar
        self.assertNotEqual(m["S"]["out_e0"], base()[0]["S"]["out_e0"])
        v_loose, _ = C.decide(m, p, b, each_draw="more")      # every draw recognises more than S (10 of 10)
        v_strict, steps = C.decide(m, p, b, each_draw="z2")   # only 4 of the 10 draws reach z >= 2
        self.assertEqual(v_loose, "CHANGE to U")
        self.assertEqual(v_strict, "KEEP")
        self.assertIn("draws beating S (z ≥ 2 each) 4 of 10", {s["step"]: s for s in steps}["3U"]["reading"])

    def test_identity_or_its_planted_twin_failing_voids_everything(self):
        m, p, b = base()
        self.assertEqual(C.decide(m, p, b, identity_ok=False)[0], "VOID")
        self.assertEqual(C.decide(m, p, b, plant_ok=False)[0], "VOID")

    def test_cannot_tell_form_one_n_forgets_nothing_and_s_does_not_differ(self):
        m, p, b = base()
        m["N"].update(lost=1, out_e0=19, out_end=19)          # PLANT: N holds everything it recognised
        m["S"]["lost"] = 1
        p["S vs N"] = pr(1, 1)
        self.assertEqual(C.decide(m, p, b)[0], "«this world cannot tell»")

    def test_cannot_tell_form_two_underpowered_and_every_maker_reading_inside_the_u_band(self):
        m, p, b = base()
        for k in ("S", "P", "N"):
            m[k]["R-A"], m[k]["R-B"] = -0.02, -0.02            # PLANT: inside both bands
        self.assertEqual(C.decide(m, p, b)[0], "«this world cannot tell»")
        m["N"]["R-B"] = -0.48                                  # one reading outside the band again
        self.assertEqual(C.decide(m, p, b)[0], "KEEP")

    def test_p_changes_the_line_only_when_gradable_z_two_and_the_veto_allows_it(self):
        m, p, b = base()
        m["S"]["out_e0"] = 40
        p["P vs S"] = pr(9, 0)                                 # z 3.0
        self.assertEqual(C.decide(m, p, b)[0], "CHANGE to P")
        m["P"]["lost"] = 5                                     # S 3 + 1 = 4 < 5: the maker VETO
        self.assertEqual(C.decide(m, p, b)[0], "KEEP")
        m2, p2, b2 = base()
        p2["P vs S"] = pr(9, 0)                                # not gradable: the same z changes nothing
        self.assertEqual(C.decide(m2, p2, b2)[0], "KEEP")

    def test_both_qualify_p_needs_to_beat_u_mean_and_pr_by_z_two_else_u(self):
        m, p, b = base()
        m["S"]["out_e0"] = 40
        p["P vs S"] = pr(9, 0)
        p["U-mean vs S"] = {"out": {"z": 3.0}}
        for d in range(1, 11):
            p[f"U{d} vs S"] = pr(9, 0)
        self.assertEqual(C.decide(m, p, b)[0], "CHANGE to U")  # P vs U-mean z -1.68, P vs PR z 1.0
        p["P vs U-mean"] = {"out": {"z": 2.5}}
        p["P vs PR"] = pr(9, 0)
        self.assertEqual(C.decide(m, p, b)[0], "CHANGE to P")

    def test_replay_zero_when_n_beats_s_by_z_two_and_neither_p_nor_u_beats_n(self):
        m, p, b = base()
        m["S"]["out_e0"] = 40
        p["N vs S"] = pr(9, 0)
        self.assertEqual(C.decide(m, p, b)[0], "CHANGE to replay 0")
        p["P vs N"] = pr(9, 0)                                 # P beats N: the clause does not fire
        self.assertNotEqual(C.decide(m, p, b)[0], "CHANGE to replay 0")

    def test_keep_is_refused_when_s_is_worse_than_n_by_more_than_one_lost_thing_and_the_law_names_no_reading(self):
        m, p, b = base()
        m["S"]["lost"] = 4                                     # N 2: more than one lost thing
        v, steps = C.decide(m, p, b)
        self.assertEqual(v, "NO CLAUSE FIRES")
        m["S"]["lost"] = 3                                     # exactly one more: KEEP (the real reading)
        self.assertEqual(C.decide(m, p, b)[0], "KEEP")


@unittest.skipUnless(HAVE_RUNS, "the A/B's run folder is not on this box")
class RawAgainstReading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.J = json.loads((RUNS / "READING.json").read_text())
        cls.raw = C.raw_all(RUNS, LISTS)

    def test_the_arms_own_files_reproduce_every_figure_in_reading_json(self):
        self.assertEqual(C.raw_vs_json(self.raw, self.J), [])
        self.assertEqual(len(self.raw["arms"]), 14)
        self.assertEqual({r["sittings"] for r in self.raw["arms"].values()}, {40})

    def test_a_planted_change_in_the_reading_is_caught(self):
        for path, new in ((("marks", "S", "R-B", "mean"), -0.5373), (("marks", "N", "lost_13"), 1), (("marks", "S", "READ-W0-out", "end_w0"), 31),
                          (("pairs", "U2 vs S", "out", "z"), 2.0)):
            J2 = copy.deepcopy(self.J)
            d = J2
            for k in path[:-1]:
                d = d[k]
            self.assertNotEqual(d[path[-1]], new, "the plant must change the bytes")
            d[path[-1]] = new
            self.assertNotEqual(json.dumps(J2, sort_keys=True), json.dumps(self.J, sort_keys=True))
            bad = C.raw_vs_json(self.raw, J2)
            self.assertTrue(bad, f"a planted change at {path} was not caught")

    def test_the_laws_own_text_carries_every_constant_the_checker_declares(self):
        self.assertEqual(C.law_constants_ok(LAW.read_text()), [])
        self.assertTrue(C.law_constants_ok("nothing here"), "a law without the constants is refused")

    def test_the_walk_from_the_arms_own_figures_is_keep_like_the_reader(self):
        marks, uband = C.marks_for_decide(self.raw)
        v, steps = C.decide(marks, self.raw["pairs"], uband)
        self.assertEqual(v, "KEEP")
        self.assertEqual(self.J["verdict"].split(" (")[0], "KEEP")
        d = C.derived(self.raw, self.J)
        self.assertEqual(d["arms at or above the bar"], 0, "no arm reached 30 recognised at end-w0 (the bar was out of reach for every rule)")
        self.assertEqual(d["U draws that recognise more of the 224 than S"], 10)
        self.assertEqual(d["U draws with z ≥ 2 against S"], 4)


@unittest.skipUnless(HAVE_RUNS, "the A/B's run folder is not on this box")
class DocCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.J = json.loads((RUNS / "READING.json").read_text())
        cls.txt = (RUNS / "READING.txt").read_text()
        cls.law = LAW.read_text()
        cls.raw = C.raw_all(RUNS, LISTS)
        marks, uband = C.marks_for_decide(cls.raw)
        cls.verdict, steps = C.decide(marks, cls.raw["pairs"], uband)
        cls.gen = C.blocks(cls.raw, cls.J, steps)

    def doc(self, prose: str) -> str:
        parts = [f"<!-- GEN:{n} BEGIN -->\n{t}\n<!-- GEN:{n} END -->" for n, t in self.gen.items()]
        return prose + "\n\n" + "\n\n".join(parts) + "\n"

    def problems(self, doc: str):
        return C.check_doc(doc, self.gen, self.J, self.txt, self.law, self.verdict)

    GOOD = ("**VERDICT: KEEP** — the line stays. S recognised 17 of 224 at the end-w0 sitting (the bar is 30 of the 224), on 2026-10-03 at 10:47 +0400, "
            "see §7 and #228 in e65b926. S's R-B was −0.5733 and S lost 3 of 13 things.")

    def test_a_true_doc_passes(self):
        self.assertEqual(self.problems(self.doc(self.GOOD)), [])

    def test_a_transposed_decimal_is_caught(self):
        bad = self.GOOD.replace("−0.5733", "−0.5373")
        self.assertNotEqual(bad, self.GOOD)
        self.assertTrue(any("0.5373" in p for p in self.problems(self.doc(bad))))

    def test_a_pair_that_is_no_pair_of_the_reading_is_caught(self):
        bad = self.GOOD.replace("17 of 224", "27 of 224")
        self.assertNotEqual(bad, self.GOOD)
        self.assertTrue(any("27 of 224" in p for p in self.problems(self.doc(bad))))

    def test_a_negative_that_the_sources_only_carry_as_positive_is_caught(self):
        bad = self.GOOD + " N's R-A was −0.0083 in draw U2."   # U2's R-A is −0.0083 (negative); this one is a plain match
        self.assertEqual(self.problems(self.doc(bad)), [])
        bad2 = self.GOOD + " The z was −2.82."                   # the sources carry +2.82 only (U-mean vs S)
        self.assertTrue(any("2.82" in p for p in self.problems(self.doc(bad2))))
        ok2 = self.GOOD + " The z was 2.82."
        self.assertEqual(self.problems(self.doc(ok2)), [])

    def test_a_generated_block_edited_by_hand_is_caught(self):
        doc = self.doc(self.GOOD)
        marker = "| S | −0.0583 |"
        self.assertIn(marker, doc)
        bad = doc.replace(marker, "| S | −0.0538 |", 1)
        self.assertNotEqual(bad, doc)
        self.assertTrue(any("differs from what the script generates" in p for p in self.problems(bad)))

    def test_a_missing_block_and_a_wrong_verdict_word_are_caught(self):
        doc = self.doc(self.GOOD)
        no_maker = doc.replace("<!-- GEN:maker BEGIN -->", "<!-- X -->")
        self.assertNotEqual(no_maker, doc)
        self.assertTrue(any("'maker' is absent" in p for p in self.problems(no_maker)))
        wrong = doc.replace("VERDICT: KEEP", "VERDICT: CHANGE")
        self.assertNotEqual(wrong, doc)
        self.assertTrue(any("VERDICT line" in p for p in self.problems(wrong)))

    def test_dates_shas_sections_identifiers_and_enumerators_are_not_numbers_to_check(self):
        prose = self.GOOD + "\n1. U10 and w0 at 09-30 12:20:10 in sleep-1003, 2026-09-30T012436Z.json, genome/machinery.py:446, (1), Sonnet 5.5, §5.3, #246 (1)."
        self.assertEqual(self.problems(self.doc(prose)), [])

    def test_fill_rewrites_the_blocks_and_is_idempotent(self):
        stale = self.doc(self.GOOD)
        stale = stale.replace(self.gen["arms"], "stale")
        self.assertNotEqual(stale, self.doc(self.GOOD))
        once = C.fill(stale, self.gen)
        self.assertEqual(once, self.doc(self.GOOD))
        self.assertEqual(C.fill(once, self.gen), once)
        self.assertEqual(self.problems(once), [])


class Controls(unittest.TestCase):
    """controls_from_files: PREREG-SLEEP-AB §5's controls read from their own files; each is refused when its file says otherwise."""

    def setUp(self) -> None:
        import tempfile
        self.tmp = Path(tempfile.mkdtemp(prefix="sleepab-ctl-"))
        self.runs = self.tmp / "ab" / "runs2"
        (self.runs / "logs").mkdir(parents=True)
        (self.runs / "state").mkdir()
        ctl = self.tmp / "ab" / "ctl"
        for d in ("u1-a", "u1-b"):
            (ctl / d).mkdir(parents=True)
            (ctl / d / "journal.jsonl").write_text('{"seq": 1}\n{"seq": 2}\n')
        (ctl / "splant.log").write_text("DIVERGED at seq 1271: hash\nexit 1\n")
        (ctl / "s2000.log").write_text("REPLAY identical: 1880 mind rows\nexit 0\n")
        (ctl / "leverh_proof.log").write_text(json.dumps({"rows": [5667, 5667], "identical_except_hash": True, "null_hashes_in_bare": 4767, "digests_in_hashed": 4767,
                                                         "planted_caught_at": [1271, "sleep"]}) + "\nexit 0\n")
        (self.runs / "logs" / "S.log").write_text("REPLAY identical: 47274 mind rows\nexit 0\n")
        for a in C.ARMS:
            if a != "S":
                (self.runs / "logs" / f"{a}.log").write_text("replay wrote /x/journal.jsonl\nexit 0\n")
            (self.runs / "state" / f"{a}.attempt").write_text("1\n")
        self.ctl = ctl

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self):
        return C.controls_from_files(self.runs, check_code=False)

    def test_every_control_holds_on_the_true_files(self):
        c = self.read()
        for k in ("identity_ok", "plant_ok", "s2000_ok", "det_ok", "leverh_ok"):
            self.assertTrue(c[k], k)
        self.assertEqual((c["arms_exit0"], c["arms"]), (14, 14))
        self.assertEqual(c["identity_line"], "REPLAY identical: 47274 mind rows")
        text = C.block_controls({**c, "code_same": True})
        self.assertIn("**True**", text)
        self.assertNotIn("**False**", text)

    def test_a_planted_failure_in_each_control_file_is_caught(self):
        def plant(path: Path, new: str, key: str, expect):
            before = path.read_text()
            held = self.read()[key]
            self.assertNotEqual(held, expect, "the control must hold on the true file before it is planted")
            self.assertNotEqual(before, new, "the plant must change the bytes")
            path.write_text(new)
            try:
                self.assertEqual(self.read()[key], expect, f"{path.name}: the planted change was not caught")
            finally:
                path.write_text(before)
            self.assertEqual(self.read()[key], held, "restored, the control holds again")

        plant(self.runs / "logs" / "S.log", "REPLAY DIVERGED at seq 9\nexit 1\n", "identity_ok", False)
        plant(self.ctl / "splant.log", "REPLAY identical: 1880 mind rows\nexit 0\n", "plant_ok", False)
        plant(self.ctl / "u1-b" / "journal.jsonl", '{"seq": 1}\n{"seq": 3}\n', "det_ok", False)
        plant(self.ctl / "s2000.log", "DIVERGED at seq 5: hash\nexit 1\n", "s2000_ok", False)
        bad_lh = json.dumps({"rows": [5667, 5667], "identical_except_hash": False, "null_hashes_in_bare": 4767, "digests_in_hashed": 4767,
                             "planted_caught_at": [1271, "sleep"]}) + "\nexit 1\n"
        plant(self.ctl / "leverh_proof.log", bad_lh, "leverh_ok", False)
        plant(self.runs / "logs" / "U7.log", "killed\nexit 137\n", "arms_exit0", 13)

    def test_a_missing_file_reads_as_not_holding_never_as_holding(self):
        (self.ctl / "splant.log").unlink()
        self.assertFalse(self.read()["plant_ok"])
        (self.runs / "logs" / "S.log").unlink()
        self.assertFalse(self.read()["identity_ok"])

    def test_the_code_comparison_sees_a_difference_and_a_sameness(self):
        import subprocess
        have = subprocess.run(["git", "cat-file", "-e", "7bbc995"], capture_output=True).returncode == 0 and \
            subprocess.run(["git", "cat-file", "-e", "e65b926"], capture_output=True).returncode == 0
        if not have:
            self.skipTest("the sleep-ab commits are not in this repository")
        self.assertTrue(C.code_same_between("HEAD", "HEAD"))
        self.assertFalse(C.code_same_between("7bbc995", "e65b926"), "creature/replay.py changed between them")
        self.assertTrue(C.code_same_between("bbd1214", "e65b926"))


class PilotAndLoad(unittest.TestCase):
    def test_a_synthetic_timings_file_gives_the_pilot_share_and_the_load_range(self):
        import shutil
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="sleepab-pilot-"))
        try:
            (tmp / "S").mkdir()
            rows = [{"seq": 1, "cpu_ms": 3.6e6}, {"seq": 16198, "cpu_ms": 3.6e6}, {"seq": 16199, "cpu_ms": 3.6e6 * 2}, {"seq": 20000, "cpu_ms": 3.6e6 * 4}]
            (tmp / "S" / "timings.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
            (tmp / "TICKS.log").write_text("a load 1.5 mem\nb load 7.25 mem\nc load 3.0 mem\n")
            J = {"marks": {"S": {"cpu_h": 8.0}, "N": {"cpu_h": 4.0}}}
            d = C.pilot_and_load(tmp, J)
            self.assertEqual(d["S CPU-h up to the end-w0 sitting (tape rows ≤ 16198)"], 2.0)       # rows 1 and 16198, never 16199
            self.assertEqual(d["that, as a share of S"], 0.25)
            self.assertEqual(d["CPU-h of all 14 arms"], 12.0)
            self.assertEqual((d["load, lowest"], d["load, median"], d["load, highest"], d["TICKS.log load readings"]), (1.5, 3.0, 7.25, 3))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @unittest.skipUnless(HAVE_RUNS, "the A/B's run folder is not on this box")
    def test_the_real_pilot_is_a_small_share_of_s_and_of_the_whole_a_b(self):
        J = json.loads((RUNS / "READING.json").read_text())
        d = C.pilot_and_load(RUNS, J)
        self.assertLess(d["that, as a share of S"], 0.1)
        self.assertLess(d["that pilot, as a share of the 14 arms"], 0.01)


class NumberShapes(unittest.TestCase):
    def test_numbers_in_reads_thousands_signs_and_skips_identifiers(self):
        vals = [(str(v), neg) for v, neg, _ in C.numbers_in("a −0.5733 and 47,274 rows, U10 and e65b926 and 2026-10-03 and z 2.82 [−0.04, 0.0]")]
        self.assertEqual(vals, [("0.5733", True), ("47274", False), ("2.82", False), ("0.04", True), ("0.0", False)])


if __name__ == "__main__":
    unittest.main()
