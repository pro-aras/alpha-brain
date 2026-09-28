# edit: Claude (Fable 5.1), 2026-09-24 18:24 +0400 — the materialiser end to end at SMOKE scale: real glyphs, the real pinned
# organs, the SAME code path a graded tape takes (schedule → build_cache → resolve → controls → files). Asserts
# every written row under the frozen validator, both truth record types, the counts against the formulas, the
# DISJOINT (0f) and MLC-leak (0g) controls WITH their planted negatives, and — the world's identity law — that the
# tape built twice into two directories is byte-identical (tape.jsonl, truth.jsonl, mlc.jsonl, the cache index).
# Slow (one real render of ~2,400 canvases, ~5 min under load); the second build (the byte-identity of the whole
# world, the strongest control) runs only with B1_TAPE_TWICE=1 — it was run once on 2026-09-24 (see the register).
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from brain.glance_cache import Cache
from brain.protocol import validate_tape_row, verify_row
from brain.world import mlc as M
from brain.world import schedule as S
from brain.world import tape as T
from brain.world.families import LETTER_NAMES

SEED = 20261001
TMP = Path(os.environ.get("TMPDIR", "/data/dev/brain-runs/tmp"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_SHARED: dict = {}


def setUpModule() -> None:
    """ONE smoke tape per module run (a real render, ~5 min under load), shared by every class below."""
    TMP.mkdir(parents=True, exist_ok=True)
    _SHARED["tmp"] = tempfile.TemporaryDirectory(dir=str(TMP), prefix="b1-tape-smoke-")
    root = Path(_SHARED["tmp"].name)
    _SHARED["root"] = root
    _SHARED["world"] = T.smoke_world(SEED)
    _SHARED["log"] = []
    _SHARED["summary"] = T.build_tape(SEED, root / "a", root / "a" / "cache", _SHARED["world"], S.SMOKE, log=_SHARED["log"].append)


def tearDownModule() -> None:
    _SHARED["tmp"].cleanup()


class TestTapeSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _SHARED["root"]
        cls.world = _SHARED["world"]
        cls.log_lines = _SHARED["log"]
        cls.summary = _SHARED["summary"]
        cls.out = cls.root / "a"

    def _rows(self, name: str):
        return [json.loads(l) for l in (self.out / name).read_text().splitlines() if l.strip()]

    def test_files_and_every_row_validates(self) -> None:
        for name in ("tape.jsonl", "tape.sha256", "truth.jsonl", "mlc.jsonl", "counts.json", "schedule-notes.json"):
            self.assertTrue((self.out / name).exists(), name)
        rows = self._rows("tape.jsonl")
        for r in rows:
            validate_tape_row(r)
            self.assertTrue(verify_row(r))
        self.assertEqual([r["seq"] for r in rows], list(range(1, len(rows) + 1)))
        self.assertEqual((self.out / "tape.sha256").read_text().strip(), _sha(self.out / "tape.jsonl"))
        for r in self._rows("mlc.jsonl"):
            M.validate_mlc_row(r)

    def test_counts_match_the_formulas_and_the_printed_record(self) -> None:
        e = S.expected_counts(n_test_fonts_upper=3, n_test_fonts_lower=3, p=S.SMOKE)
        kinds = self.summary["kinds"]
        for k in ("TEACH", "ASK", "FEEDBACK", "ARRIVAL", "TEST_BEGIN", "TEST_END"):
            self.assertEqual(kinds[k], e[k], k)
        self.assertEqual(self.summary["mlc"]["episodes"], e["mlc_episodes"])
        self.assertEqual(self.summary["renderings"], len(Cache(self.out / "cache")))
        text = "\n".join(self.log_lines)
        self.assertIn("plant «zog» taught at seq", text)     # R3: the plant's position is printed
        self.assertIn("sleeps (", text)                       # R2: the sleep positions are printed
        self.assertIn("DISJOINT (0f): PASS", text)
        self.assertGreater(self.summary["ms_per_canvas"], 0)

    def test_truth_has_both_record_types_and_maps_rows(self) -> None:
        recs = self._rows("truth.jsonl")
        renders = [r for r in recs if r["type"] == "rendering"]
        asks = [r for r in recs if r["type"] == "ask"]
        self.assertEqual(len(renders), self.summary["renderings"])
        n_ask_rows = sum(1 for r in self._rows("tape.jsonl") if r["kind"] == "ASK")
        n_mlc_asks = sum(1 for r in self._rows("mlc.jsonl") if r["kind"] == "ASK")
        self.assertEqual(len(asks), n_ask_rows + n_mlc_asks)
        cache = Cache(self.out / "cache")
        by_row = {r["cache_row"]: r for r in renders}
        for r in renders[:50]:
            m = cache.meta(r["cache_row"])
            self.assertEqual(m["canvas_png_sha256"], r["canvas_png_sha256"])
            self.assertEqual((m["script"], m["char"], m["font"]), (r["script"], r["char"], r["font"]))
        # a NAME ask's truth answer is the name of the glyph its operand row renders (the KEY's own road)
        tape = {r["seq"]: r for r in self._rows("tape.jsonl")}
        checked = 0
        for a in asks:
            if a["family"] == "U1a_NAME":
                row = tape[a["seq"]]["payload"]["operands"][0]["value"]
                self.assertEqual(by_row[row]["char"].lower(), a["answer"])
                checked += 1
        self.assertGreater(checked, 100)
        mlc_asks = [a for a in asks if a.get("mlc")]
        self.assertTrue(all(a["seq"] >= M.MLC_SEQ_BASE for a in mlc_asks))

    def test_disjoint_control_catches_a_planted_copy(self) -> None:
        rows = self._rows("tape.jsonl")
        cache = Cache(self.out / "cache")
        sha_of = lambda row: cache.meta(row)["canvas_png_sha256"]  # noqa: E731
        self.assertTrue(T.disjoint_check(rows, sha_of)["pass"])
        teach_row = next(r for r in rows if r["kind"] == "TEACH")["payload"]["glance_row"]
        planted = [dict(r) for r in rows]
        in_sit = False
        for r in planted:
            if r["kind"] == "TEST_BEGIN":
                in_sit = True
            if in_sit and r["kind"] == "ASK" and any(op["kind"] == "row" for op in r["payload"]["operands"]):
                p = dict(r["payload"]); ops = [dict(op) for op in p["operands"]]
                i = next(i for i, op in enumerate(ops) if op["kind"] == "row")
                ops[i]["value"] = teach_row; p["operands"] = ops; r["payload"] = p
                break
        res = T.disjoint_check(planted, sha_of)
        self.assertFalse(res["pass"])
        self.assertEqual(res["collisions"][0]["cache_row"], teach_row)

    def test_mlc_leak_check_passes_and_catches_a_planted_plus_two(self) -> None:
        rows = self._rows("mlc.jsonl")
        cache = Cache(self.out / "cache")
        char_of = lambda row: (cache.meta(row)["script"], cache.meta(row)["char"])  # noqa: E731
        res = M.leak_check(rows, char_of)
        self.assertTrue(res["pass"], res["violations"][:3])
        self.assertEqual(res["n_pairs"], sum(1 for r in rows if r["kind"] == "FEEDBACK"))
        ask = next(r for r in rows if r["kind"] == "ASK")
        script, ch = char_of(ask["payload"]["operands"][0]["value"])
        x = LETTER_NAMES.index(ch.lower())
        y = LETTER_NAMES[(x + 2) % 26]
        planted_fb = M.make_mlc_row(ask["seq"] - M.MLC_SEQ_BASE + 1, ask["after_seq"], ask["episode"], "FEEDBACK", "L4", ask["item"],
                                    {"ask_seq": ask["seq"], "right": y})
        res2 = M.leak_check([ask, planted_fb], char_of)
        self.assertFalse(res2["pass"])
        self.assertEqual(res2["violations"][0]["diff"], 2)

    @unittest.skipUnless(os.environ.get("B1_TAPE_TWICE") == "1", "set B1_TAPE_TWICE=1 to build the world twice")
    def test_built_twice_is_byte_identical(self) -> None:
        T.build_tape(SEED, self.root / "b", self.root / "b" / "cache", self.world, S.SMOKE, log=lambda s: None)
        for name in ("tape.jsonl", "truth.jsonl", "mlc.jsonl", "cache/index.jsonl", "cache/glances.npy"):
            self.assertEqual(_sha(self.root / "a" / name), _sha(self.root / "b" / name), name)



class TestRunnerAndGradersOnTheSmokeTape(unittest.TestCase):
    """edit: Claude (Fable 5.1), 2026-09-24 18:38 +0400 — the runner (brain/harness/run.py) and the graders
    (brain/harness/graders.py) on the tape this module built: the harness arms KEY / SHIFTED-KEY / RING-READ, the
    dummy, and A0 (the cells) — every record's shape, the KEY control (every graded test mark passes; CANARY is
    the leak detector, excluded for KEY by construction — R26), SHIFTED-KEY failing many, RING-READ reading REACH
    at 1.0 and the new cue at 0, and A0 running the whole tape with no VOID sitting."""

    @classmethod
    def setUpClass(cls) -> None:
        from brain.harness import graders as G
        from brain.harness import run as R
        cls.G, cls.R = G, R
        cls.tape_dir = _SHARED["root"] / "a"
        cls.out = _SHARED["root"] / "run"
        cls.rows, cls.tape_sha = R.load_tape(cls.tape_dir)
        cls.truth = R.load_truth(cls.tape_dir)["asks"]
        cls.counts = json.loads((cls.tape_dir / "counts.json").read_text())
        cls.summaries = R.run(SEED, ["DUMMY", "KEY", "SHIFTED-KEY", "RING-READ", "A0"], cls.out, cls.tape_dir, cls.tape_dir / "cache", log=lambda s: None)

    def _bars(self, rec):
        G = self.G
        ans = rec["answers"]
        b = {"U1a": {"latin-upper": 0.5, "latin-lower": 0.5}, "U3": {}, "U4a": 0.5, "U5": 0.8, "KEEPS": 5.0, "COST": 50.0}
        for fam in G.U3_LETTER_FAMILIES:
            n = len(G.family_items(ans, fam, "T_L")); b["U3"][fam] = G.k_min(n, G.FAMILY_NULL[fam]) if n else None
        n = len(G.family_items(ans, "TRANSFER", "T_D")); b["TRANSFER"] = G.k_min(n, 1 / 9) if n else None
        b["U1b"] = G.k_min(len(G._by_sitting(ans, "T_L", "U1b_PICK")), .25)
        b["U2b"] = G.k_min(len(G._by_sitting(ans, "T_L", "U2b_LURES")), .5)
        b["U6"] = G.k_min(len(G._by_sitting(ans, "T_L", "U6_PLANT")), 1 / 27)
        return b

    def _marks(self, arm):
        rec = self.G.load_record(self.out / arm)
        return rec, self.G.grade_arm(rec, self.truth, self.rows, bars=self._bars(rec), tape_counts=self.counts, seed=SEED)

    def test_record_shape_R27(self) -> None:
        for arm in ("DUMMY", "KEY", "A0"):
            d = self.out / arm
            for name in ("answers.jsonl", "state_sha.jsonl", "cost.jsonl", "feedback.jsonl", "why.jsonl", "rules.jsonl", "sittings.json", "summary.json", "run-facts.json"):
                self.assertTrue((d / name).exists(), f"{arm}/{name}")
            summ = json.loads((d / "summary.json").read_text())
            self.assertEqual(summ["tape_sha256"], self.tape_sha)
            n_ask_rows = sum(1 for r in self.rows if r["kind"] == "ASK")
            self.assertEqual(summ["counts"]["asks"], n_ask_rows)
            answers = [json.loads(l) for l in (d / "answers.jsonl").read_text().splitlines() if l.strip()]
            self.assertEqual(len(answers), n_ask_rows)
            self.assertTrue(all(a["truth"] is not None for a in answers))          # every ask has a truth record
            self.assertEqual(summ["counts"]["void_sittings"], 0)
            self.assertEqual(sorted(summ["sittings"]), ["P1", "P2", "T_D", "T_L"])

    def test_key_passes_every_graded_test_mark_and_shifted_key_does_not(self) -> None:
        _, km = self._marks("KEY")
        part = self.G.partition(km)
        self.assertEqual([f for f in part["failed"] if f != "C0d_CANARY"], [])   # KEY answers the canary from the truth: the one mark it MUST fail
        self.assertIn("C0d_CANARY", part["failed"])
        self.assertTrue(km["U3_AFTER@T_L"]["graded"] and km["U3_AFTER@T_L"]["pass"])
        self.assertEqual(km["U3_AFTER@T_L"]["fields"]["n"], 12)
        _, sm = self._marks("SHIFTED-KEY")
        failed = self.G.partition(sm)["failed"]
        self.assertGreaterEqual(len(failed), 8, failed)
        for fam in ("AFTER", "TWO_AFTER", "CHAIN", "OTHER_CASE"):
            self.assertIn(f"U3_{fam}@T_L", failed)

    def test_ring_read_reads_reach_and_nothing_else(self) -> None:
        _, m = self._marks("RING-READ")
        for fam in ("AFTER", "BEFORE", "BETWEEN"):
            self.assertEqual(m[f"U3_{fam}@T_L"]["reading"], 1.0)
        for fam in ("TWO_AFTER", "OTHER_CASE", "CHAIN"):
            self.assertEqual(m[f"U3_{fam}@T_L"]["reading"], 0.0)
        self.assertEqual(m["U3_TRANSFER@T_D"]["reading"], 1.0)              # index arithmetic reaches the digits too
        self.assertEqual(m["U1a_NAME@T_L"]["reading"], {"latin-upper": 0.0, "latin-lower": 0.0})

    def test_a0_runs_the_whole_tape_frozen_and_grounded(self) -> None:
        rec, m = self._marks("A0")
        self.assertTrue(m["C0e_FROZEN"]["pass"])
        self.assertTrue(rec["summary"]["has_why"])
        self.assertGreater(rec["summary"]["cost"]["arm_ms"], 0)
        kinds = set(a["answer"]["kind"] for a in rec["answers"])
        self.assertTrue({"NAME", "UNKNOWN", "NOTHING"} <= kinds, kinds)
        # every relation cue reads NOTHING for the cells (§4's table): no road, never a guess
        rel = [a for a in rec["answers"] if a["sitting"] == "T_L" and a["family"] in ("AFTER", "TWO_AFTER", "CHAIN", "MIRROR")]
        self.assertTrue(rel and all(a["answer"]["kind"] == "NOTHING" for a in rel))
        self.assertEqual(m["U4a_EXPLAINS_EXPERIENCE"]["reason_code"] in ("NOT_GRADABLE_N_LT_13", "", "NO_BAR"), True)

    def test_partition_never_counts_not_gradable_as_failed(self) -> None:
        _, m = self._marks("DUMMY")
        part = self.G.partition(m)
        ng = {n for n, _ in part["not_gradable"]}
        self.assertFalse(ng & set(part["failed"]))
        self.assertIn("U4a_EXPLAINS_EXPERIENCE", ng)      # the dummy has no why(): «no road», never a fail



class TestResultsOnTheSmokeRun(unittest.TestCase):
    """edit: Claude (Fable 5.1), 2026-09-24 18:43 +0400 — brain/harness/results.py on the run the class above made: results.json
    canonical and hashed, the instrument sound (KEY passes every graded test mark, CANARY excepted; SHIFTED-KEY does
    not), a re-read reproducing the hash, and a planted one-row change in a COPY of an answers.jsonl changing it (§8)."""

    @classmethod
    def setUpClass(cls) -> None:
        from brain.harness import results as RS
        cls.RS = RS
        cls.run_dir = _SHARED["root"] / "run"
        cls.tape_dir = _SHARED["root"] / "a"
        if not (cls.run_dir / "KEY" / "summary.json").exists():
            from brain.harness import run as R
            R.run(SEED, ["KEY", "SHIFTED-KEY", "DUMMY"], cls.run_dir, cls.tape_dir, cls.tape_dir / "cache", log=lambda s: None)
        cls.res = RS.assemble(cls.run_dir, cls.tape_dir)
        cls.written = RS.write_all(cls.res, cls.run_dir / "results", cls.run_dir)

    def test_files_instrument_and_reproducibility(self) -> None:
        out = self.run_dir / "results"
        for n in ("results.json", "results.sha256", "run-facts.json", "VERDICT.md"):
            self.assertTrue((out / n).exists(), n)
        self.assertEqual((out / "results.sha256").read_text().strip(), self.written["results_sha256"])
        inst = self.res["instrument"]
        self.assertFalse(inst["void"], inst)
        self.assertEqual(inst["key_failed"], [])
        self.assertGreater(len(inst["shifted_key_failed"]), 0)
        self.assertTrue(self.res["smoke"])           # no bars → a smoke
        again = self.RS.assemble(self.run_dir, self.tape_dir)
        from brain.protocol import canonical_json
        self.assertEqual(canonical_json(again), canonical_json(self.res))     # a re-read reproduces the hash
        text = (out / "VERDICT.md").read_text()
        self.assertIn("The instrument (0c) — sound", text)
        self.assertIn("REACH (read beside RING-READ)", text)

    def test_a_planted_row_change_changes_the_hash(self) -> None:
        import shutil
        copy = _SHARED["root"] / "run-planted"
        if copy.exists():
            shutil.rmtree(copy)
        shutil.copytree(self.run_dir, copy, ignore=shutil.ignore_patterns("results"))
        p = copy / "KEY" / "answers.jsonl"
        lines = p.read_text().splitlines()
        # plant on a T_L AFTER item (a graded row): the mark's reading must move, and so must the hash
        idx = next(i for i, l in enumerate(lines) if json.loads(l).get("sitting") == "T_L" and json.loads(l).get("family") == "AFTER")
        rec = json.loads(lines[idx])
        rec["correct"] = False
        rec["answer"]["kind"] = "SILENT"; rec["answer"]["value"] = None
        lines[idx] = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        p.write_text("\n".join(lines) + "\n")
        planted = self.RS.assemble(copy, self.tape_dir)
        from brain.protocol import canonical_json
        h1 = hashlib.sha256(canonical_json(self.res).encode()).hexdigest()
        h2 = hashlib.sha256(canonical_json(planted).encode()).hexdigest()
        self.assertNotEqual(h1, h2)
        self.assertEqual(h1, self.written["results_sha256"])
        before = self.res["arms"]["KEY"]["marks"]["U3_AFTER@T_L"]["fields"]["renderings"]
        self.assertNotEqual(planted["arms"]["KEY"]["inputs_sha256"]["answers.jsonl"], self.res["arms"]["KEY"]["inputs_sha256"]["answers.jsonl"])
        self.assertLess(planted["arms"]["KEY"]["marks"]["U3_AFTER@T_L"]["fields"]["breakdown_by_class"][rec["class"]]["right"],
                        self.res["arms"]["KEY"]["marks"]["U3_AFTER@T_L"]["fields"]["breakdown_by_class"][rec["class"]]["right"])
        self.assertEqual(before, planted["arms"]["KEY"]["marks"]["U3_AFTER@T_L"]["fields"]["renderings"])


class TestResultsMissingRelationTwin(unittest.TestCase):
    """edit: Claude (Opus 5.5), 2026-09-27 11:40 +0400 — R44 through `assemble`, on the smoke run: KEY's record copied as E′ (an arm §4
    feeds SHUFFLED-RELATION to) and graded with a U3 bar of 1. Before R44, E′'s U3 marks were graded on the bar alone when
    no twin record existed: no band, a pass without its null. Now: no twin record → NOT GRADABLE (TWIN_MISSING); the R43
    stop's marker on SHUFFLED-RELATION_D → NOT GRADABLE (TWIN_VOID, by cost); DUMMY's record copied as the twin → graded
    against its band as before (the positive control). Every mark outside U3 is the same in all three. The marker's name is
    written as a literal here so that the old code reads the defect, not a missing constant."""

    @classmethod
    def setUpClass(cls) -> None:
        import shutil
        from brain.harness import graders as G
        from brain.harness import results as RS
        run_dir = _SHARED["root"] / "run"
        tape_dir = _SHARED["root"] / "a"
        if not (run_dir / "KEY" / "summary.json").exists():
            from brain.harness import run as R
            R.run(SEED, ["KEY", "SHIFTED-KEY", "DUMMY"], run_dir, tape_dir, tape_dir / "cache", log=lambda s: None)
        bars = {"U3": {f: 1 for f in G.U3_LETTER_FAMILIES}, "TRANSFER": 1}
        cls.res = {}
        # edit: Claude (Opus 5.5), 2026-09-28 02:32 +0400 — R51: two more cases with KEY's record copied as D (D's own U3 null is its own
        # SHUFFLED-RELATION:D search, R36): the stop's marker on SHUFFLED-RELATION_D, and DUMMY's record as that twin.
        for case in ("missing", "by_cost", "twin", "d_by_cost", "d_twin"):
            d = _SHARED["root"] / f"run-r44-{case}"
            if d.exists():
                shutil.rmtree(d)
            d.mkdir()
            if (run_dir / "inputs.json").exists():
                shutil.copy(run_dir / "inputs.json", d / "inputs.json")
            shutil.copytree(run_dir / "KEY", d / ("D" if case.startswith("d_") else "E′"))
            if case in ("by_cost", "d_by_cost"):
                (d / "SHUFFLED-RELATION_D").mkdir()
                (d / "SHUFFLED-RELATION_D" / "VOID-BY-COST.json").write_text(json.dumps({"why": "planted stop (R43)"}) + "\n")
            if case == "twin":
                shutil.copytree(run_dir / "DUMMY", d / "SHUFFLED-RELATION_E′")
            if case == "d_twin":
                shutil.copytree(run_dir / "DUMMY", d / "SHUFFLED-RELATION_D")
            cls.res[case] = RS.assemble(d, tape_dir, bars=bars)

    def _marks(self, case: str, u3: bool) -> dict:
        return {k: v for k, v in self.res[case]["arms"]["E′"]["marks"].items() if k.startswith("U3_") == u3}

    def test_the_positive_control_grades_u3_against_the_twins_band(self) -> None:
        graded = {k: v for k, v in self._marks("twin", True).items() if v["graded"]}
        self.assertTrue(graded)
        self.assertEqual(self.res["twin"]["twin_void"], {})
        for k, v in graded.items():
            self.assertIsNotNone(v["fields"].get("twin_band_95"), k)

    def test_no_twin_record_reads_not_gradable_never_a_pass_on_the_bar(self) -> None:
        with_twin = [k for k, v in self._marks("twin", True).items() if v["graded"]]
        u3 = self._marks("missing", True)
        for k in with_twin:
            self.assertFalse(u3[k]["graded"], k)
            self.assertIsNone(u3[k]["pass"], k)
            self.assertEqual(u3[k]["reason_code"], "TWIN_MISSING", k)
        self.assertEqual(self.res["missing"]["twin_void"], {"E′": ["MISSING: no SHUFFLED-RELATION:E′ record"]})

    def test_the_r43_stop_reads_void_by_cost(self) -> None:
        with_twin = [k for k, v in self._marks("twin", True).items() if v["graded"]]
        u3 = self._marks("by_cost", True)
        for k in with_twin:
            self.assertFalse(u3[k]["graded"], k)
            self.assertEqual(u3[k]["reason_code"], "TWIN_VOID", k)
        by = self.res["by_cost"]["twin_void"]["E′"]
        self.assertTrue(by[0].startswith("VOID_BY_COST") and "planted stop" in by[0], by)

    def test_d_reads_its_own_twins_stop_not_gradable(self) -> None:
        """edit: Claude (Opus 5.5), 2026-09-28 02:32 +0400 — R51, through `assemble`. The positive control first: with DUMMY's record as
        SHUFFLED-RELATION:D, D's U3 marks are graded against that twin's band. Then the stop: with only the marker on
        SHUFFLED-RELATION_D, every one of those marks reads NOT GRADABLE, TWIN_VOID by cost — never a pass on the bar alone,
        which is what B1.0 seed 1's D read at 02:2x before R51. Every mark outside U3 is the same in both."""
        d_twin = {k: v for k, v in self.res["d_twin"]["arms"]["D"]["marks"].items() if k.startswith("U3_") and v["graded"]}
        self.assertTrue(d_twin)
        self.assertEqual(self.res["d_twin"]["twin_void"], {})
        for k, v in d_twin.items():
            self.assertIsNotNone(v["fields"].get("twin_band_95"), k)
        u3 = self.res["d_by_cost"]["arms"]["D"]["marks"]
        for k in d_twin:
            self.assertFalse(u3[k]["graded"], k)
            self.assertIsNone(u3[k]["pass"], k)
            self.assertEqual(u3[k]["reason_code"], "TWIN_VOID", k)
        by = self.res["d_by_cost"]["twin_void"]["D"]
        self.assertTrue(by[0].startswith("VOID_BY_COST: SHUFFLED-RELATION:D") and "planted stop" in by[0], by)
        outside = lambda case: {k: v for k, v in self.res[case]["arms"]["D"]["marks"].items() if not k.startswith("U3_")}
        self.assertEqual(outside("d_by_cost"), outside("d_twin"))

    def test_every_mark_outside_u3_is_unchanged(self) -> None:
        self.assertEqual(self._marks("missing", False), self._marks("twin", False))
        self.assertEqual(self._marks("by_cost", False), self._marks("twin", False))


if __name__ == "__main__":
    unittest.main()
