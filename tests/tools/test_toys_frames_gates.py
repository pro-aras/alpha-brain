"""Tests for TOY C's gates G1-G6 (docs/research/toys/PREREG-TOY-FRAMES.md §7; AMENDMENT-1 §1.4, §3, §4 (f)-(g)): the checks the unit REQUIRES before it runs. Written FIRST, STAGE 5b (red, then green).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:10 +0400 — STAGE 5b. G1 runs here on FIXTURE copies (the real counts are asserted against the real copies by tests/tools/test_toys_frames.py and by the real `gates` run); each gate
# carries a planted failure it must NAME: a count one off (G1), a corrupted copy (G1), a ceiling set below the measured price (G5), a plant stream the rules cannot keep (G4).
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:36 +0400 — STAGE 5c (the relaunched lane): the first sweep of gates.py (the predecessor's, unrecorded) let FIVE mutants survive (the manifest check, G4's control line, PLANT-BEATS-NULL-2,
# G6's cheat condition, G3's tolerance); the cause was one shape: each was a decision line whose FAIL branch no test ever forced. Every gate decision now has a PLANTED failure that must be named, each in a test NAMED in
# docs/research/toys/records/frames/mutations/ (MUTANTS.json: the mutant, its diff, its catching test). The plants patch the names gates.py calls through (GT.find_frames, GT.CO.slow_gain, GT.RL.trace_problems,
# GT._g4_stream, GT.SC.g6_*, GT.g1..g6) so the REAL decision lines run on canned inputs; every perturbation asserts it changed the value it perturbs.
"""
from __future__ import annotations

import contextlib
import hashlib
import inspect
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from tools.toys.common import prereg as PR
from tools.toys.frames import gates as GT
from tools.toys.frames import plants as PL
from tools.toys.frames import scene as SC
from tools.toys.frames import streams as ST
from tools.toys.frames.evaluate import SEEDS as EV_SEEDS

from tests.tools.test_toys_frames_run import make_copies


def write_manifest(copies: Path):
    man = {}
    for sub in ("tape", "journal"):
        for p in sorted(copies.glob(f"*/{sub}/*.jsonl")):
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            man[str(p.relative_to(copies))] = {"source_sha256": h, "copy_sha256": h, "bytes": p.stat().st_size}
    (copies / "MANIFEST.json").write_text(json.dumps(man))
    return man


def expected_from(copies: Path):
    a4 = ST.load_moments(sorted((copies / "alpha4-1" / "tape").glob("*.jsonl")))
    c = ST.section0_counts(a4)
    sc = ST.scene_moments(ST.load_moments(sorted((copies / "brain-full-20261102" / "tape").glob("*.jsonl"))))
    from collections import Counter
    says = ST.load_says(sorted((copies / "alpha4-1" / "journal").glob("*.jsonl")))
    return {"alpha4": {"moments": c["moments"], "words": c["words"], "by_source": c["by_source"]},
            "scene": {"moments": len(sc), "per_moment": dict(sorted(Counter(len(m.words) for m in sc).items())), "dax_index": None},
            "says": (len(says), sum(1 for s in says if s[1] == "yes"), len({s[0] for s in says}))}


class TestG1(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        make_copies(self.d)
        write_manifest(self.d)
        self.exp = expected_from(self.d)

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_it_passes_when_every_count_is_the_expected_one_and_the_copies_hash_to_their_manifest(self):
        r = GT.g1(self.d, self.exp)
        self.assertTrue(r["ok"], r["failures"])
        self.assertEqual(r["failures"], [])
        self.assertEqual(r["plant_tokens"], {"ALPHA4": {t: 0 for t in ST.PLANT}, "SCENE": {t: 0 for t in ST.PLANT}})
        self.assertIn("gated", r["chi2"])
        man = json.loads((self.d / "MANIFEST.json").read_text())
        self.assertEqual(r["copies_verified"], len(man))                                              # every manifest entry verified: 3 files in the fixture
        self.assertEqual(len(man), 3)

    def test_a_count_one_off_is_named(self):
        bad = json.loads(json.dumps(self.exp, default=str))
        bad = {**self.exp, "alpha4": {**self.exp["alpha4"], "moments": self.exp["alpha4"]["moments"] + 1}}
        r = GT.g1(self.d, bad)
        self.assertFalse(r["ok"])
        self.assertTrue(any("alpha4.moments" in f for f in r["failures"]), r["failures"])

    def test_a_per_source_count_one_off_is_named(self):
        by = {k: dict(v) for k, v in self.exp["alpha4"]["by_source"].items()}
        src = sorted(by)[0]
        by[src]["words"] += 1
        r = GT.g1(self.d, {**self.exp, "alpha4": {**self.exp["alpha4"], "by_source": by}})
        self.assertFalse(r["ok"])
        self.assertTrue(any(f"alpha4.{src}.words" in f for f in r["failures"]), r["failures"])

    def test_a_scene_histogram_or_says_count_one_off_is_named(self):
        r = GT.g1(self.d, {**self.exp, "scene": {**self.exp["scene"], "moments": self.exp["scene"]["moments"] - 1}})
        self.assertTrue(any("scene.moments" in f for f in r["failures"]))
        s = self.exp["says"]
        r2 = GT.g1(self.d, {**self.exp, "says": (s[0], s[1] + 1, s[2])})
        self.assertTrue(any("says" in f for f in r2["failures"]))

    def test_every_count_the_law_names_is_checked_one_at_a_time(self):
        """Each count g1 compares — both totals, every per-source count, the scene's count and words-a-moment histogram, each entry of the says triple, the «dax» index — is moved ALONE: g1 must
        say not ok and name exactly that one count (a comparison that was dropped, or read the wrong field, leaves the others quiet and is seen here; the sweep's survivors on 2026-10-03 were
        `alpha4.words`, the scene histogram and the absent-source branch)."""
        exp = self.exp
        cases = [("alpha4.moments", {**exp, "alpha4": {**exp["alpha4"], "moments": exp["alpha4"]["moments"] + 1}}),
                 ("alpha4.words", {**exp, "alpha4": {**exp["alpha4"], "words": exp["alpha4"]["words"] + 1}})]
        for src, want in exp["alpha4"]["by_source"].items():
            for k, v in want.items():
                bumped = dict(want)
                if isinstance(v, dict):
                    first = sorted(v)[0]
                    bumped[k] = {**v, first: v[first] + 1}
                else:
                    bumped[k] = v + 1
                self.assertNotEqual(bumped[k], v)                                                    # the plant changed the value it plants
                cases.append((f"alpha4.{src}.{k}", {**exp, "alpha4": {**exp["alpha4"], "by_source": {**exp["alpha4"]["by_source"], src: bumped}}}))
        pm = dict(exp["scene"]["per_moment"])
        first = sorted(pm)[0]
        pm[first] += 1
        cases.append(("scene.moments", {**exp, "scene": {**exp["scene"], "moments": exp["scene"]["moments"] + 1}}))
        cases.append(("scene.per_moment", {**exp, "scene": {**exp["scene"], "per_moment": pm}}))
        s = exp["says"]
        for i in range(3):
            t = list(s)
            t[i] += 1
            cases.append(("says (rows, yes, distinct frames)", {**exp, "says": tuple(t)}))
        cases.append(("scene.dax@5", {**exp, "scene": {**exp["scene"], "dax_index": 5}}))
        self.assertGreater(len(cases), 12)
        for label, bad in cases:
            with self.subTest(label=label):
                r = GT.g1(self.d, bad)
                self.assertFalse(r["ok"])
                self.assertEqual(len(r["failures"]), 1, r["failures"])
                self.assertIn(label, r["failures"][0])

    def test_a_corrupted_copy_is_named_by_its_path(self):
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        b = bytearray(p.read_bytes())
        b[40] ^= 1
        p.write_bytes(bytes(b))
        r = GT.g1(self.d, self.exp)
        self.assertFalse(r["ok"])
        self.assertTrue(any("alpha4-1/tape/2026-09-23.jsonl" in f for f in r["failures"]), r["failures"])

    def test_a_copy_changed_where_only_the_manifest_can_see_it_is_named(self):
        """The change keeps the JSON valid and every count (one digit of a timestamp): NOTHING but the manifest's hash can see it, so g1's verdict and its `copies_verified` count rest on the manifest check alone
        (the survivor: the manifest line could be deleted and the byte-flip test above still failed, through the reader's error naming the same path)."""
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        before = p.read_bytes()
        after = before.replace(b"T00:00:00Z", b"T00:00:01Z", 1)
        self.assertNotEqual(after, before)                                                          # the plant changed the bytes (#247 (5))
        p.write_bytes(after)
        man = json.loads((self.d / "MANIFEST.json").read_text())
        self.assertNotEqual(hashlib.sha256(after).hexdigest(), man["alpha4-1/tape/2026-09-23.jsonl"]["copy_sha256"])
        r = GT.g1(self.d, self.exp)
        self.assertFalse(r["ok"])
        self.assertEqual(r["failures"], ["copy alpha4-1/tape/2026-09-23.jsonl: no longer hashes to its manifest"])
        self.assertEqual(r["copies_verified"], len(man) - 1)

    def test_a_copies_directory_without_a_manifest_is_named(self):
        (self.d / "MANIFEST.json").unlink()
        r = GT.g1(self.d, self.exp)
        self.assertFalse(r["ok"])
        self.assertEqual(r["failures"], ["no MANIFEST.json in the copies directory"])
        self.assertNotIn("copies_verified", r)

    def test_an_unreadable_copy_is_named_and_g1_says_not_ok(self):
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        p.write_text(p.read_text() + "this line is not json\n")
        write_manifest(self.d)                                                                      # the manifest now matches the new bytes: ONLY the reader can fail
        r = GT.g1(self.d, self.exp)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["failures"]), 1, r["failures"])
        self.assertTrue(r["failures"][0].startswith("a copy cannot be read: "), r["failures"])
        self.assertIn("not JSON", r["failures"][0])
        self.assertIn("2026-09-23.jsonl", r["failures"][0])

    def test_an_expected_source_missing_from_the_copies_is_named(self):
        by = {**self.exp["alpha4"]["by_source"], "folder": {"moments": 1, "words": 1, "distinct": 1, "per_moment": {1: 1}}}
        self.assertNotIn("folder", self.exp["alpha4"]["by_source"])                                 # the fixture has no «folder» source
        r = GT.g1(self.d, {**self.exp, "alpha4": {**self.exp["alpha4"], "by_source": by}})
        self.assertFalse(r["ok"])
        self.assertEqual(r["failures"], ["alpha4.folder: the source is absent"])

    def test_a_plant_token_found_in_a_real_stream_is_named(self):
        """AMENDMENT-1 §2: both plant tokens must occur in ZERO real rows. The plant: one real moment carrying the first token (the manifest and the counts are rebuilt so ONLY this check can fail)."""
        p = self.d / "alpha4-1" / "tape" / "2026-09-23.jsonl"
        last = [json.loads(x) for x in p.read_text().splitlines() if x.strip()][-1]["seq"]
        row = {"seq": last + 1, "at": "2026-09-23T00:00:00Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {"moment": "planted-real", "source": "shelf", "word": ST.PLANT[0]}}
        p.write_text(p.read_text() + json.dumps(row) + "\n")
        write_manifest(self.d)
        exp = expected_from(self.d)
        r = GT.g1(self.d, exp)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["failures"]), 1, r["failures"])
        self.assertIn("plant tokens occur in the real ALPHA4 stream", r["failures"][0])

    def test_a_plant_token_found_in_the_real_scene_stream_is_named(self):
        """The same premise for the SCENE stream: a scene moment of the plant token and a real shape word (so the generator's χ² reader still reads it); only the SCENE count may fail."""
        p = self.d / "brain-full-20261102" / "tape" / "2026-09-28.jsonl"
        last = [json.loads(x) for x in p.read_text().splitlines() if x.strip()][-1]["seq"]
        rows = [{"seq": last + 1 + i, "at": "2026-09-28T00:00:00Z", "sense": "ear", "sha": "x", "payload": "p", "meta": {"moment": "planted-scene", "source": "scene", "word": w}}
                for i, w in enumerate((ST.PLANT[0], SC.SHAPES[0]))]
        p.write_text(p.read_text() + "".join(json.dumps(r) + "\n" for r in rows))
        write_manifest(self.d)
        exp = expected_from(self.d)
        r = GT.g1(self.d, exp)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["failures"]), 1, r["failures"])
        self.assertIn("plant tokens occur in the real SCENE stream", r["failures"][0])
        self.assertEqual(r["plant_tokens"]["SCENE"][ST.PLANT[0]], 1)
        self.assertEqual(r["plant_tokens"]["ALPHA4"], {t: 0 for t in ST.PLANT})

    def test_the_dax_moment_is_checked_at_its_index_when_the_law_names_one(self):
        r = GT.g1(self.d, {**self.exp, "scene": {**self.exp["scene"], "dax_index": 5}})
        self.assertFalse(r["ok"])                                                                     # scene moment 5 of the fixture is not the one-word «dax» scene
        self.assertTrue(any("dax" in f for f in r["failures"]))


class TestG2G3(unittest.TestCase):
    def test_g2_the_stand_in_store_equals_the_real_episodes_store(self):
        r = GT.g2()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["frames"], [["blue", "ball"], ["green", "key"], ["red", "box"]])

    def test_g2_fails_when_the_real_store_disagrees_with_a_correct_stand_in(self):
        """the stand-in gives the known three frames, the REAL store gives one more: the two answers differ and g2 must say so (the frames list is read from the stand-in, so only the equality can see it)."""
        real_find = GT.find_frames

        def fake(store):
            rows = real_find(store)
            return rows if isinstance(store, GT.RL.StandIn) else rows + [{"w1": "x", "w2": "y"}]

        with mock.patch.object(GT, "find_frames", fake):
            r = GT.g2()
        self.assertEqual(r["frames"], [["blue", "ball"], ["green", "key"], ["red", "box"]])
        self.assertFalse(r["ok"])

    def test_g2_fails_when_the_stand_in_disagrees_with_a_correct_real_store(self):
        """the REAL store gives the known three frames, the stand-in gives none: g2 must exercise the stand-in and read it (a g2 that asked the real store twice would read ok)."""
        real_find = GT.find_frames

        def fake(store):
            return [] if isinstance(store, GT.RL.StandIn) else real_find(store)

        with mock.patch.object(GT, "find_frames", fake):
            r = GT.g2()
        self.assertFalse(r["ok"])
        self.assertEqual(r["n_rows"], 0)

    def test_g2_fails_when_both_stores_agree_on_a_wrong_frame_set(self):
        """both answers are equal and wrong (no frames at all): the known store's three frames are the pin, equality alone is not."""
        with mock.patch.object(GT, "find_frames", lambda store: []):
            r = GT.g2()
        self.assertFalse(r["ok"])
        self.assertEqual(r["frames"], [])

    def test_g3_the_fast_compressor_and_the_greedys_incremental_gain_equal_their_recounts(self):
        r = GT.g3(n_streams=6, mdl_seeds=3)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["compressor_cases"], 6 * 4)
        self.assertLess(r["max_abs_diff"], 1e-9)
        self.assertEqual(r["mdl_problems"], [])
        self.assertGreater(r["mdl_steps"], 3)                                                          # the loop took steps (a vacuous pass would be zero)

    def test_g3_pins_its_tolerance_from_both_sides_for_every_compared_key(self):
        """The recount is perturbed by +delta in ONE compared key: 1e-10 and 5e-10 are inside the law's 1e-9 (g3 stays ok), 2e-9 and 1e-6 are outside (g3 must fail), for each of G, bits0, bitsF, L — a
        tolerance loosened ten-fold, tightened ten-fold, a dropped key or a dropped abs() each moves one of these 16 readings (the survivor was `worst < 1e-9` itself)."""
        real_slow = GT.CO.slow_gain

        def perturbed(key, delta):
            def f(train, held, F):
                out = dict(real_slow(train, held, F))
                out[key] = out[key] + delta
                return out
            return f

        for key in ("G", "bits0", "bitsF", "L"):
            for delta, ok in ((1e-10, True), (5e-10, True), (2e-9, False), (1e-6, False)):
                with self.subTest(key=key, delta=delta):
                    with mock.patch.object(GT.CO, "slow_gain", perturbed(key, delta)):
                        r = GT.g3(n_streams=2, mdl_seeds=0)
                    self.assertAlmostEqual(r["max_abs_diff"], delta, delta=1e-11)                  # the plant moved exactly the value it was told to move
                    self.assertEqual(r["ok"], ok, r["max_abs_diff"])

    def test_g3_fails_when_the_token_counts_disagree(self):
        real_slow = GT.CO.slow_gain
        for key in ("N", "K", "V", "n_held_words"):
            def f(train, held, F, key=key):
                out = dict(real_slow(train, held, F))
                out[key] = out[key] + 1
                return out

            with self.subTest(key=key):
                with mock.patch.object(GT.CO, "slow_gain", f):
                    r = GT.g3(n_streams=2, mdl_seeds=0)
                self.assertFalse(r["ok"])
                self.assertGreaterEqual(r["max_abs_diff"], 1.0)

    def test_g3_fails_when_the_greedys_trace_has_a_problem(self):
        with mock.patch.object(GT.RL, "trace_problems", lambda *a, **k: ["a planted problem"]):
            r = GT.g3(n_streams=2, mdl_seeds=2)
        self.assertFalse(r["ok"])
        self.assertEqual(r["mdl_problems"], ["seed 0: a planted problem", "seed 1: a planted problem"])
        self.assertLess(r["max_abs_diff"], 1e-9)                                                       # the compressor recount is fine: ONLY the greedy's problems fail it


def canned_stream(key, **over):
    """A G4 stream block as `_g4_stream` returns it, every gate passing; `over` replaces fields."""
    required = list(GT.G4_REQUIRED[key])
    gates = {r: {"pass": True, "n_seeds": 10, "n_counted": 10, "need": 9, "mode": "amend1", "B": 700.0} for r in ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")}
    s = {"label": key, "n_moments": 3000, "every": 10, "plants": [180, 120], "V": 15, "budget": 30, "B": 700.0, "plant_beats_null2": True, "null2_q95": 100.0, "gates": gates,
         "required": required, "printed_only": [r for r in gates if r not in required], "control": {"caught": True, "bytes_changed": True, "gate_honest": True, "gate_broken": False}}
    s.update(over)
    return s


def run_g4_canned(by_key, **kw):
    """g4 with `_g4_stream` replaced by the canned blocks (so g4's OWN decision lines run on them, instantly) and the stream builders made trivial."""
    def fake(key, label, moments, every, draws, seeds):
        return by_key[key]

    with mock.patch.object(GT, "_g4_stream", fake), mock.patch.object(GT.SY, "structure_free_alpha", lambda n, seed: ([], [])):
        return GT.g4(scene_moments=5, **kw)


# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:22 +0400 — G4 under AMENDMENT-2 §2 (written FIRST; red: g4 takes no stream sizes yet): TWO planted streams, (A) the SCENE-regime stream as signed in AMENDMENT-1 §4 (g) where WEB-H, SENTENCE and
# MDL-GREEDY are required and WEB-S is PRINTED, and (B) an ALPHA4-regime stream where all four are required; the seat's 18:2x test for signing: the small-vocabulary failure stays printed, never erased.
class TestG4(unittest.TestCase):
    def test_both_streams_every_required_rule_keeps_the_plant_and_both_controls_are_caught(self):
        r = GT.g4(draws=20, seeds=(1, 2, 3), scene_moments=2500, alpha_moments=6000)
        self.assertTrue(r["ok"], r["failures"])
        a, b = r["streams"]["A"], r["streams"]["B"]
        self.assertEqual(sorted(a["required"]), ["MDL-GREEDY", "SENTENCE", "WEB-H"])
        self.assertEqual(a["printed_only"], ["WEB-S"])
        self.assertEqual(sorted(b["required"]), ["MDL-GREEDY", "SENTENCE", "WEB-H", "WEB-S"])
        self.assertEqual(b["printed_only"], [])
        for rule in b["required"]:
            self.assertTrue(b["gates"][rule]["pass"], (rule, b["gates"][rule]))
        for s in (a, b):
            self.assertTrue(s["plant_beats_null2"])
            self.assertTrue(s["control"]["caught"])
            self.assertTrue(s["control"]["bytes_changed"])
            self.assertEqual(s["budget"], 2 * s["V"])
            for rule, g in s["gates"].items():
                self.assertEqual(g["mode"], "amend1", rule)                                        # the gate runs in the signed mode (AMENDMENT-1 §1), not the base text's
        self.assertEqual((a["every"], b["every"]), (PL.PLANT_EVERY["SCENE"], PL.PLANT_EVERY["ALPHA4"]))
        self.assertGreater(b["V"], 500)                                                                 # stream B's vocabulary is the regime where B = 2V can hold a plant (stream A's is 15 words)
        self.assertLess(a["V"], 20)

    def test_stream_a_as_signed_prints_web_s_failure_and_does_not_fail_the_gate(self):
        """the signed stream (3,000 moments, replicate seed 1, a plant after every 10th, ten WEB-S seeds): WEB-S keeps the frame at 6 of 10 seeds (records/frames/ORIENT-g4_diag.out) — PRINTED in the output,
        never erased, and not a failure of G4 (AMENDMENT-2 §2 (A))."""
        r = GT.g4(draws=10, seeds=EV_SEEDS, scene_moments=3000, alpha_moments=6000)
        a = r["streams"]["A"]
        self.assertFalse(a["gates"]["WEB-S"]["pass"])
        self.assertEqual((a["gates"]["WEB-S"]["n_counted"], a["gates"]["WEB-S"]["n_seeds"], a["gates"]["WEB-S"]["need"]), (6, 10, 9))
        self.assertEqual((a["V"], a["budget"]), (15, 30))
        for rule in ("WEB-H", "SENTENCE", "MDL-GREEDY"):
            self.assertTrue(a["gates"][rule]["pass"], rule)
        self.assertTrue(r["ok"], r["failures"])                                                         # the required rules and stream B carry the gate
        self.assertFalse(any("WEB-S" in f and "stream A" in f for f in r["failures"]))

    def test_a_stream_too_short_to_carry_the_plant_fails_and_says_so(self):
        r = GT.g4(draws=10, seeds=(1, 2, 3), scene_moments=300, scene_every=100, alpha_moments=300, alpha_every=100)      # a few plants in 300 moments: nothing can repay 2 log2 V
        self.assertFalse(r["ok"])
        self.assertTrue(r["failures"])

    def test_a_required_rule_that_fails_on_stream_b_stops_the_gate(self):
        r = GT.g4(draws=10, seeds=(1, 2, 3), scene_moments=2500, alpha_moments=300, alpha_every=100)    # stream B too short for the web: required there
        self.assertFalse(r["ok"])
        self.assertTrue(any("stream B" in f for f in r["failures"]), r["failures"])

    # ---- the decision lines of g4, on canned stream blocks (stage 5c: the survivors were the PLANT-BEATS-NULL-2 line and the control line, whose fail branches nothing forced)
    def test_a_required_rule_failing_its_plant_gate_stops_g4_naming_the_stream_and_the_rule(self):
        good = run_g4_canned({k: canned_stream(k) for k in "AB"})
        self.assertTrue(good["ok"])
        self.assertEqual(good["failures"], [])
        for key in "AB":
            for rule in GT.G4_REQUIRED[key]:
                with self.subTest(stream=key, rule=rule):
                    blocks = {k: canned_stream(k) for k in "AB"}
                    blocks[key]["gates"][rule] = {**blocks[key]["gates"][rule], "pass": False, "n_counted": 0}
                    r = run_g4_canned(blocks)
                    self.assertFalse(r["ok"])
                    self.assertEqual(len(r["failures"]), 1, r["failures"])
                    self.assertTrue(r["failures"][0].startswith(f"G4 stream {key}: {rule} fails the PLANT gate"), r["failures"])
        blocks = {k: canned_stream(k) for k in "AB"}                                                      # a rule that is only PRINTED may fail (AMENDMENT-2 §2 (A))
        blocks["A"]["gates"]["WEB-S"] = {**blocks["A"]["gates"]["WEB-S"], "pass": False, "n_counted": 6}
        r = run_g4_canned(blocks)
        self.assertTrue(r["ok"], r["failures"])
        self.assertEqual(r["streams"]["A"]["printed_only"], ["WEB-S"])

    def test_a_plant_that_does_not_beat_null2_stops_g4_and_prints_both_numbers(self):
        for key in "AB":
            with self.subTest(stream=key):
                blocks = {k: canned_stream(k) for k in "AB"}
                blocks[key] = canned_stream(key, plant_beats_null2=False, B=123.456, null2_q95=234.567)
                r = run_g4_canned(blocks)
                self.assertFalse(r["ok"])
                self.assertEqual(r["failures"], [f"G4 stream {key}: PLANT-BEATS-NULL-2 fails (B 123.46, q95 234.57)"])

    def test_each_conjunct_of_the_parse_breaking_control_stops_g4(self):
        """the control passes only if it was CAUGHT, changed the bytes, the honest gate passes and the broken gate does not: each of the four is broken ALONE, on each stream, and g4 must stop naming the control."""
        ok_control = {"caught": True, "bytes_changed": True, "gate_honest": True, "gate_broken": False}
        for key in "AB":
            for field, bad in (("caught", False), ("bytes_changed", False), ("gate_honest", False), ("gate_broken", True)):
                with self.subTest(stream=key, field=field):
                    control = {**ok_control, field: bad}
                    self.assertNotEqual(control, ok_control)
                    blocks = {k: canned_stream(k) for k in "AB"}
                    blocks[key] = canned_stream(key, control=control)
                    r = run_g4_canned(blocks)
                    self.assertFalse(r["ok"])
                    self.assertEqual(len(r["failures"]), 1, r["failures"])
                    self.assertTrue(r["failures"][0].startswith(f"G4 stream {key}: the gate's parse-breaking control is not caught"), r["failures"])

    def test_the_defaults_are_the_signed_streams(self):
        """AMENDMENT-2 §2: stream A = G6's sampler at 3,000 moments, a plant after every 10th (SCENE's cadence); stream B = structure_free_alpha(20,000, 1), a plant after every 100th (ALPHA4's); 100 null draws, the
        ten WEB-S seeds; the required rules per stream exactly as signed."""
        p = inspect.signature(GT.g4).parameters
        self.assertEqual((p["draws"].default, tuple(p["seeds"].default), p["scene_moments"].default, p["scene_every"].default, p["alpha_moments"].default, p["alpha_every"].default),
                         (100, EV_SEEDS, 3000, 10, 20000, 100))
        self.assertEqual(PL.PLANT_EVERY, {"ALPHA4": 100, "SCENE": 10})
        self.assertEqual(GT.G4_REQUIRED, {"A": ("WEB-H", "SENTENCE", "MDL-GREEDY"), "B": ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")})

    def test_g4_draws_stream_a_from_replicate_seed_1_and_stream_b_from_alpha_seed_1(self):
        seen = {}

        def spy_scene(n, rng):
            seen["scene"] = (n, int(rng.integers(1 << 30)))
            return []

        def spy_alpha(n, seed):
            seen["alpha"] = (n, seed)
            return [], []

        fake = lambda key, label, moments, every, draws, seeds: canned_stream(key)
        with mock.patch.object(GT, "_g4_stream", fake), mock.patch.object(GT.SC, "sample_moments", spy_scene), mock.patch.object(GT.SY, "structure_free_alpha", spy_alpha):
            r = GT.g4()
        self.assertTrue(r["ok"])
        self.assertEqual(seen["scene"], (3000, int(np.random.default_rng([20261103, 8, 1]).integers(1 << 30))))      # default_rng([SEED_ROOT, G6_TAG, 1]): the signed «replicate seed 1»
        self.assertEqual(seen["alpha"], (20000, 1))
        self.assertEqual((SC.SEED_ROOT, SC.G6_TAG), (20261103, 8))


def stub_clock_gate(cpu_seconds, rss_kb):
    """g5's inputs made deterministic: process_time answers from `cpu_seconds` in order, the peak-RSS reader from `rss_kb`, the evaluator does nothing, the streams are empty."""
    return [mock.patch.object(GT.RN, "load_streams", lambda copies: {"alpha4": []}), mock.patch.object(GT.PL, "condition_parts", lambda moments, kind, *a, **k: ([], [])),
            mock.patch.object(GT.EV, "evaluate_condition", lambda *a, **k: {}), mock.patch.object(GT.time, "process_time", side_effect=list(cpu_seconds)),
            mock.patch.object(GT.RN, "peak_rss_kb", side_effect=list(rss_kb))]


class TestG5(unittest.TestCase):
    def test_the_pilot_extrapolates_cpu_linearly_in_the_draws_and_reports_peak_memory(self):
        # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:47 +0400 — the REAL evaluator still runs, but the CPU clock is a fake monotone counter (5 s a pilot): the first version read the real
        # process_time of a 0.2 s pilot at 3 and 6 draws, whose slope is noise — in the 2026-10-03 20:3x sweep one of 93 unmutated-G5 runs read a NEGATIVE slope, a predicted price below 1e-6 and a false
        # «the ceiling did not stop» failure (a flaky plant: #246 (8)); the deterministic boundaries live in test_g5_arithmetic_and_the_ceiling_boundaries_on_stubbed_clocks.
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d)
            ticks = iter(range(0, 10_000, 5))
            with mock.patch.object(GT.time, "process_time", side_effect=lambda: float(next(ticks))):
                r = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1000.0, rss_ceiling_mb=100000.0, seeds=(1, 2))
            self.assertTrue(r["ok"], r)
            a, b = r["pilots"]
            self.assertEqual((a["draws"], b["draws"]), (3, 6))
            self.assertEqual((a["cpu_seconds"], b["cpu_seconds"]), (5.0, 5.0))                           # the fake clock: each pilot reads two ticks 5 s apart
            slope = (b["cpu_seconds"] - a["cpu_seconds"]) / 3
            self.assertAlmostEqual(r["cpu_slope_per_draw"], slope, places=9)
            self.assertAlmostEqual(r["predicted_alpha4_cpu_seconds_at_100"], a["cpu_seconds"] + slope * 97, places=6)
            self.assertAlmostEqual(r["predicted_unit_cpu_minutes"], 5 * r["predicted_alpha4_cpu_seconds_at_100"] / 60.0, places=9)
            self.assertGreater(r["peak_rss_mb"], 0.0)
            # the plant: a ceiling below the (now certain) price must STOP, with the real evaluator and the real peak-memory reader
            ticks2 = iter(range(0, 10_000, 5))
            with mock.patch.object(GT.time, "process_time", side_effect=lambda: float(next(ticks2))):
                tight = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1e-6, rss_ceiling_mb=100000.0, seeds=(1, 2))
            self.assertFalse(tight["ok"])
            self.assertTrue(any("CPU" in f for f in tight["failures"]))
            tight_mem = GT.g5(d, sizes=(3, 6), cpu_ceiling_min=1000.0, rss_ceiling_mb=1.0, seeds=(1, 2))   # a process of ~100 MB against a 1 MB ceiling: no clock involved
            self.assertFalse(tight_mem["ok"])
            self.assertTrue(any("memory" in f for f in tight_mem["failures"]))
        finally:
            shutil.rmtree(d)

    def test_g5_arithmetic_and_the_ceiling_boundaries_on_stubbed_clocks(self):
        """The two pilots read 50 and 66 CPU-s at 10 and 20 draws and 100,000 / 101,000 kB: the slope is 1.6 s and 100 kB a draw, ALPHA4 at 100 draws is 194 s, the unit (five ALPHA4s) 16.1667 min, the memory
        (101,000 + 100 x 80) / 1024 = 106.45 MB, the reported peak the larger pilot's 98.63 MB. A ceiling EXACTLY at the price passes (the law stops ABOVE its ceiling), one float below it stops."""
        def run(**kw):
            with contextlib.ExitStack() as st:
                for m in stub_clock_gate((0.0, 50.0, 100.0, 166.0), (100000, 101000)):
                    st.enter_context(m)
                return GT.g5(Path("unused"), sizes=(10, 20), **kw)

        r = run(cpu_ceiling_min=1000.0, rss_ceiling_mb=1e6)
        self.assertTrue(r["ok"], r)
        self.assertAlmostEqual(r["cpu_slope_per_draw"], 1.6, places=9)
        self.assertAlmostEqual(r["rss_slope_kb_per_draw"], 100.0, places=9)
        self.assertAlmostEqual(r["predicted_alpha4_cpu_seconds_at_100"], 194.0, places=9)
        self.assertAlmostEqual(r["predicted_unit_cpu_minutes"], 5 * 194.0 / 60.0, places=9)
        self.assertAlmostEqual(r["predicted_peak_rss_mb"], (101000 + 100.0 * 80) / 1024.0, places=9)
        self.assertAlmostEqual(r["peak_rss_mb"], 101000 / 1024.0, places=9)
        at_cpu = r["predicted_unit_cpu_minutes"]
        at_rss = r["predicted_peak_rss_mb"]
        self.assertTrue(run(cpu_ceiling_min=at_cpu, rss_ceiling_mb=at_rss)["ok"])                       # exactly at both ceilings: ok
        below_cpu = run(cpu_ceiling_min=math.nextafter(at_cpu, 0.0), rss_ceiling_mb=at_rss)
        self.assertFalse(below_cpu["ok"])
        self.assertEqual(len(below_cpu["failures"]), 1)
        self.assertIn("CPU", below_cpu["failures"][0])
        below_rss = run(cpu_ceiling_min=at_cpu, rss_ceiling_mb=math.nextafter(at_rss, 0.0))
        self.assertFalse(below_rss["ok"])
        self.assertEqual(len(below_rss["failures"]), 1)
        self.assertIn("memory", below_rss["failures"][0])

    def test_g5_defaults_are_the_laws_ceilings(self):
        """§7 G5 / AMENDMENT-1 §3: STOP above the law's 25-40 CPU-min ceiling (40) and above 1 GB."""
        p = inspect.signature(GT.g5).parameters
        self.assertEqual((p["cpu_ceiling_min"].default, p["rss_ceiling_mb"].default), (40.0, 1024.0))


def canned_replicate(k, margin=100.0, violation=False):
    return {"k": k, "n_moments": 10000, "n_oracle": 24, "G_oracle": 10.0, "G_max": 10.0 + margin, "margin": margin, "violation": violation}


GOOD_CHEAT = {"k": 1, "bitsF_honest": 100.0, "bitsF_cheat": 90.0, "G_honest": 5.0, "G_cheat": 99.0, "G_max": 50.0, "caught": True}
GOOD_EXACT = {"sum_p": 1.0, "entropy": 6.0774, "h_length": 1.5, "h_given_length": 4.5774, "support_size": 90}


def run_g6_canned(reps=None, cheat=None, exact=None, replicates=2, **kw):
    reps = reps if reps is not None else [canned_replicate(k) for k in range(1, replicates + 1)]
    with mock.patch.object(GT.SC, "g6_replicate", side_effect=lambda k, n: reps[k - 1]), mock.patch.object(GT.SC, "g6_cheat", lambda *a, **k: dict(cheat or GOOD_CHEAT)), \
            mock.patch.object(GT.SC, "g6_exact_checks", lambda: dict(exact or GOOD_EXACT)):
        return GT.g6(replicates=len(reps), **kw)


class TestG6(unittest.TestCase):
    def test_the_ceiling_gate_controls_pass_and_a_planted_cheat_is_caught(self):
        r = GT.g6(replicates=3, n_moments=3000)
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(r["replicates"]), 3)
        self.assertTrue(all(not x["violation"] for x in r["replicates"]))
        self.assertTrue(r["cheat"]["caught"])
        self.assertLess(abs(r["exact"]["sum_p"] - 1.0), 1e-12)

    def test_g6_each_failure_is_named_and_the_tolerances_are_pinned_from_both_sides(self):
        """Canned inputs, so g6's own decision lines run on one planted fault at a time (the survivor was the cheat condition): a replicate above G_max + 20; a cheat not caught; a cheat that changed no bytes;
        each exact check just outside its tolerance (sum 1e-12, entropies 5e-5, H(length) 1e-12, the support size 90) on BOTH sides, and just inside it (ok). The printed margin is the smallest."""
        good = run_g6_canned()
        self.assertTrue(good["ok"], good["failures"])
        self.assertEqual(good["failures"], [])
        reps = [canned_replicate(1, margin=7.0), canned_replicate(2, margin=3.0)]
        self.assertEqual(run_g6_canned(reps=reps)["min_margin"], 3.0)                                      # the SMALLEST margin, not the largest
        bad = run_g6_canned(reps=[canned_replicate(1), canned_replicate(2, margin=-25.0, violation=True)])
        self.assertFalse(bad["ok"])
        self.assertEqual(len(bad["failures"]), 1)
        self.assertTrue(bad["failures"][0].startswith("G6 (a): replicate 2 has G(F_oracle) above G_max + 20 (margin -25.00)"), bad["failures"])
        for label, cheat in (("not caught", {**GOOD_CHEAT, "caught": False}), ("no bytes changed", {**GOOD_CHEAT, "bitsF_cheat": GOOD_CHEAT["bitsF_honest"]})):
            with self.subTest(cheat=label):
                self.assertNotEqual(cheat, GOOD_CHEAT)
                r = run_g6_canned(cheat=cheat)
                self.assertFalse(r["ok"])
                self.assertEqual(r["failures"], ["G6 (b): the planted cheat is not caught (or did not change the bytes)"])
        # (c): (field, value just INSIDE the tolerance, values just OUTSIDE it on both sides, the failure's prefix)
        sum_msg, ent_msg = "G6 (c): the support sums to", "G6 (c): the generator's entropies are off"
        for field, inside, outside, msg in (("sum_p", 1.0 + 5e-13, (1.0 + 2e-12, 1.0 - 2e-12), sum_msg),
                                            ("entropy", 6.0774 + 4e-5, (6.0774 + 6e-5, 6.0774 - 6e-5), ent_msg),
                                            ("h_given_length", 4.5774 + 4e-5, (4.5774 + 6e-5, 4.5774 - 6e-5), ent_msg),
                                            ("h_length", 1.5 + 5e-13, (1.5 + 2e-12, 1.5 - 2e-12), ent_msg),
                                            ("support_size", None, (89, 91), ent_msg)):
            if inside is not None:
                with self.subTest(field=field, value=inside):
                    r = run_g6_canned(exact={**GOOD_EXACT, field: inside})
                    self.assertTrue(r["ok"], r["failures"])
            for v in outside:
                with self.subTest(field=field, value=v):
                    self.assertNotEqual(v, GOOD_EXACT[field])
                    r = run_g6_canned(exact={**GOOD_EXACT, field: v})
                    self.assertFalse(r["ok"])
                    self.assertEqual(len(r["failures"]), 1, r["failures"])
                    self.assertTrue(r["failures"][0].startswith(msg), r["failures"])

    def test_g6_runs_the_laws_twenty_replicates_of_ten_thousand_moments(self):
        """§7 G6 (a) / AMENDMENT-1 §4 (a): replicate k = 1..20, 10,000 moments each, default_rng([20261103, 8, k]); the cheat on replicate 1."""
        calls, cheat_calls = [], []

        def rep(k, n):
            calls.append((k, n))
            return canned_replicate(k)

        def cheat(k, n):
            cheat_calls.append((k, n))
            return dict(GOOD_CHEAT)

        with mock.patch.object(GT.SC, "g6_replicate", rep), mock.patch.object(GT.SC, "g6_cheat", cheat), mock.patch.object(GT.SC, "g6_exact_checks", lambda: dict(GOOD_EXACT)):
            r = GT.g6()
        self.assertTrue(r["ok"], r["failures"])
        self.assertEqual(calls, [(k, 10000) for k in range(1, 21)])
        self.assertEqual(cheat_calls, [(1, 4000)])
        p = inspect.signature(GT.g6).parameters
        self.assertEqual((p["replicates"].default, p["n_moments"].default), (20, 10_000))


@contextlib.contextmanager
def stub_gates(**over):
    """run_gates with the six gates replaced by canned answers (every one ok unless overridden), recording the order they were called in."""
    gates = {"g1": lambda copies, expected=None: {"ok": True}, "g2": lambda: {"ok": True}, "g3": lambda **kw: {"ok": True}, "g4": lambda **kw: {"ok": True},
             "g5": lambda copies, **kw: {"ok": True}, "g6": lambda **kw: {"ok": True}}
    gates.update(over)
    calls = []

    def wrap(name, fn):
        def f(*a, **k):
            calls.append(name)
            return fn(*a, **k)
        return f

    with contextlib.ExitStack() as st:
        for n, fn in gates.items():
            st.enter_context(mock.patch.object(GT, n, wrap(n, fn)))
        yield calls


class TestRunGates(unittest.TestCase):
    def test_gates_json_says_passed_on_fixtures_and_the_unit_accepts_it(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            write_manifest(d / "copies")
            exp = expected_from(d / "copies")
            out = d / "runs"
            code = GT.run_gates(d / "copies", out, expected=exp, g3_kw={"n_streams": 4, "mdl_seeds": 2}, g4_kw={"scene_moments": 2500, "alpha_moments": 6000, "draws": 20, "seeds": (1, 2, 3)},
                                g5_kw={"sizes": (3, 6), "cpu_ceiling_min": 1000.0, "rss_ceiling_mb": 100000.0, "seeds": (1, 2)}, g6_kw={"replicates": 2, "n_moments": 3000})
            self.assertEqual(code, 0)
            g = json.loads((out / "GATES.json").read_text())
            self.assertTrue(g["passed"])
            self.assertEqual(g["failures"], [])
            for k in ("g1", "g2", "g3", "g4", "g5", "g6", "header"):
                self.assertIn(k, g)
            self.assertIn("toys_git_sha", g["header"])
        finally:
            shutil.rmtree(d)

    def test_a_failing_gate_writes_passed_false_and_exits_nonzero(self):
        d = Path(tempfile.mkdtemp())
        try:
            make_copies(d / "copies")
            write_manifest(d / "copies")
            exp = expected_from(d / "copies")
            exp["alpha4"]["moments"] += 1                                                               # the plant: one count off
            out = d / "runs"
            code = GT.run_gates(d / "copies", out, expected=exp, g3_kw={"n_streams": 2, "mdl_seeds": 1}, g4_kw={"scene_moments": 2500, "alpha_moments": 6000, "draws": 10, "seeds": (1, 2, 3)},
                                g5_kw={"sizes": (3, 6), "cpu_ceiling_min": 1000.0, "rss_ceiling_mb": 100000.0, "seeds": (1, 2)}, g6_kw={"replicates": 1, "n_moments": 3000})
            self.assertNotEqual(code, 0)
            g = json.loads((out / "GATES.json").read_text())
            self.assertFalse(g["passed"])
            self.assertTrue(any("alpha4.moments" in f for f in g["failures"]))
        finally:
            shutil.rmtree(d)

    def test_a_changed_law_text_stops_the_gates_before_anything_is_written(self):
        d = Path(tempfile.mkdtemp())
        try:
            docs = d / "docs"
            docs.mkdir()
            for name in ("PREREG-TOY-FRAMES.md", "PREREG-TOY-FRAMES-AMEND-1.md", "PREREG-TOY-FRAMES-AMEND-2.md"):
                shutil.copy(PR.DOCS / name, docs / name)
            amend = docs / "PREREG-TOY-FRAMES-AMEND-2.md"
            text = amend.read_bytes()
            amend.write_bytes(text.replace(b"PRINTED, not required", b"PRINTED and required", 1))
            self.assertNotEqual(amend.read_bytes(), text)                                               # the plant changed the bytes of a pinned text
            out = d / "runs"
            with stub_gates() as calls:
                with self.assertRaises(PR.PreregError):
                    GT.run_gates(d / "copies", out, prereg_root=docs)
            self.assertEqual(calls, [])                                                                 # no gate ran
            self.assertFalse((out / "GATES.json").exists())
        finally:
            shutil.rmtree(d)

    def test_a_gate_that_fails_without_a_failure_list_is_named_by_its_label_and_the_record_says_not_passed(self):
        d = Path(tempfile.mkdtemp())
        try:
            out = d / "runs"
            with stub_gates(g2=lambda: {"ok": False}, g4=lambda **kw: {"ok": False, "failures": ["G4 planted failure one", "G4 planted failure two"]}):
                code = GT.run_gates(d / "copies", out, log=lambda m: None)
            self.assertEqual(code, 1)
            g = json.loads((out / "GATES.json").read_text())
            self.assertFalse(g["passed"])
            self.assertEqual(g["failures"], ["g2 failed", "G4 planted failure one", "G4 planted failure two"])      # a gate with no failure list is NAMED, never dropped
            with stub_gates():
                code = GT.run_gates(d / "copies", out, log=lambda m: None)
            self.assertEqual(code, 0)
            self.assertTrue(json.loads((out / "GATES.json").read_text())["passed"])
        finally:
            shutil.rmtree(d)

    def test_the_log_names_each_gate_in_order_and_every_failure(self):
        d = Path(tempfile.mkdtemp())
        try:
            lines = []
            with stub_gates(g3=lambda **kw: {"ok": False, "failures": ["x1", "x2"]}) as calls:
                GT.run_gates(d / "copies", d / "runs", log=lines.append)
            self.assertEqual(calls, ["g1", "g2", "g3", "g4", "g5", "g6"])
            self.assertEqual(lines, ["[gates] g1: OK", "[gates] g2: OK", "[gates] g3: FAILED", "[gates] g4: OK", "[gates] g5: OK", "[gates] g6: OK", "[gates] FAILURE: x1", "[gates] FAILURE: x2"])
        finally:
            shutil.rmtree(d)

    def test_the_gates_record_carries_all_three_signed_shas_and_the_gate_mode(self):
        d = Path(tempfile.mkdtemp())
        try:
            with stub_gates():
                GT.run_gates(d / "copies", d / "runs", log=lambda m: None)
            g = json.loads((d / "runs" / "GATES.json").read_text())
            h = g["header"]
            self.assertEqual(h["prereg_frames_sha256"], PR.SIGNED["frames"][1])
            self.assertEqual(h["prereg_frames_amend1_sha256"], PR.SIGNED["frames_amend1"][1])
            self.assertEqual(h["prereg_frames_amend2_sha256"], PR.SIGNED["frames_amend2"][1])
            self.assertEqual(h["gate_mode"], "amend1")
            self.assertIn("toys_git_sha", h)
            self.assertIn("toys_tree_dirty", h)
            self.assertGreaterEqual(g["cpu_seconds"], 0.0)
            self.assertGreater(g["peak_rss_kb"], 0)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
