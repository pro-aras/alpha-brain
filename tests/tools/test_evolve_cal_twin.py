# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:44 +0400 — PREREG-EVOLVE-CAL §2 (the calibration's instrument): tests FIRST.
"""tests/tools/test_evolve_cal_twin.py — tools/evolve_cal.py's genome variants, staging, twin runner and twin comparison.

The calibration (docs/organism/evolve/PREREG-EVOLVE-CAL.md §2 + A1/A2) replays the INCUMBENT and many TWINS of one genome over
the same 2 h slice of a closed life's tape, from the same shadow checkpoint, and reads how far merit-neutral twins drift apart.
Everything below is the instrument: a genome variant is ONE changed number and nothing else; a staged slice is a mini tape that
`tools.evolve.tape_slice` / `build_twin` read unchanged and a verifier can re-read against the source; a twin runs in its own
process, writes its readings, its dense `state_hash` and its journal digest, and removes its big state copy; two twins are
compared row by row. Every comparison carries a PLANT that must be caught, and the plant asserts it changed the bytes (#247 (5)).
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import tools.evolve as ev
import tools.evolve_cal as cal
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
BASE = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
FIXTURE = ROOT / "tests" / "creature" / "G4-evolve-test.genome"
if not FIXTURE.exists():
    FIXTURE.write_text(BASE.rstrip("\n") + "\n" + (
        "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
        "PARK     after 3 identical dead-ends reopen on new-sense\n"
        "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"))
FIXTURE_TEXT = FIXTURE.read_text()

TEXT = (
    "# a comment that mentions KWTA 9 and DELTA lr 0.99 and SEED 1 inside a comment line\n"
    "SEED     20261101   # trailing comment kept\n"
    "KWTA     4\n"
    "DELTA    lr 0.05\n"
    "BIRTH    novelty  cos<0.952\n"
    "BIRTH    error    misfires 3\n"
    "MERGE    cos>0.9969 same-answer\n"
    "SLEEP    every 2500 moments replay 200 by surprise\n"
    "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"
)


def _lines_changed(a: str, b: str):
    la, lb = a.splitlines(), b.splitlines()
    assert len(la) == len(lb), "a variant must not add or remove a line"
    return [(i, x, y) for i, (x, y) in enumerate(zip(la, lb)) if x != y]


class TestGenomeVariants(unittest.TestCase):
    def test_gene_text_reads_the_number_the_bounds_pattern_names(self) -> None:
        self.assertEqual(cal.gene_text(TEXT, "DELTA.lr"), "0.05")
        self.assertEqual(cal.gene_text(TEXT, "KWTA.k"), "4")
        self.assertEqual(cal.gene_text(TEXT, "MERGE.theta_m"), "0.9969")
        self.assertEqual(cal.gene_text(TEXT, "BIRTH.misfires"), "3")

    def test_gene_text_refuses_an_unknown_or_excluded_key_and_a_missing_line(self) -> None:
        with self.assertRaises(ValueError):
            cal.gene_text(TEXT, "NO.SUCH")
        with self.assertRaises(ValueError):
            cal.gene_text(TEXT, "GAZE.grid")                     # an excluded shape gene
        with self.assertRaises(ValueError):
            cal.gene_text(TEXT.replace("KWTA     4\n", ""), "KWTA.k")   # the line is not in this text

    def test_set_gene_text_changes_exactly_one_line_and_exactly_the_number(self) -> None:
        for key, old, new, line_no in (("DELTA.lr", "0.05", "0.0500005", 3), ("KWTA.k", "4", "7", 2), ("MERGE.theta_m", "0.9969", "0.99", 6)):
            out = cal.set_gene_text(TEXT, key, new)
            changed = _lines_changed(TEXT, out)
            self.assertEqual(len(changed), 1, key)
            self.assertEqual(changed[0][0], line_no, key)
            self.assertEqual(changed[0][2], changed[0][1].replace(old, new, 1), key)
            self.assertEqual(cal.gene_text(out, key), new)

    def test_set_gene_text_refuses_a_non_number(self) -> None:
        with self.assertRaises(ValueError):
            cal.set_gene_text(TEXT, "DELTA.lr", "abc")
        with self.assertRaises(ValueError):
            cal.set_gene_text(TEXT, "DELTA.lr", "0.05; DROP")

    def test_comment_lines_are_never_edited(self) -> None:
        out = cal.set_gene_text(TEXT, "KWTA.k", "9")
        self.assertEqual(out.splitlines()[0], TEXT.splitlines()[0])
        self.assertEqual(out.splitlines()[0].count("KWTA 9"), 1, "the comment still says KWTA 9 and was left alone")

    def test_eps_variant_scales_delta_lr_and_nothing_else(self) -> None:
        for eps, k in ((1e-6, 1), (1e-5, 3), (1e-4, 20)):
            out = cal.eps_variant(TEXT, eps, k)
            new = float(cal.gene_text(out, "DELTA.lr"))
            self.assertNotEqual(new, 0.05, (eps, k))
            self.assertLess(abs(new / 0.05 - (1 + k * eps)), 1e-12, (eps, k))
            self.assertEqual(len(_lines_changed(TEXT, out)), 1)

    def test_eps_variant_refuses_a_perturbation_that_changes_nothing_or_makes_no_sense(self) -> None:
        for eps, k in ((0.0, 1), (-1e-5, 1), (1e-5, 0), (1e-5, -2), (1e-30, 1)):
            with self.assertRaises(ValueError, msg=(eps, k)):
                cal.eps_variant(TEXT, eps, k)

    def test_the_eps_genome_still_parses_and_carries_the_perturbed_rate(self) -> None:
        out = cal.eps_variant(BASE, 1e-6, 1)
        g = parse_genome(out)
        self.assertEqual(g.lr, float(cal.gene_text(out, "DELTA.lr")))
        self.assertNotEqual(g.lr, parse_genome(BASE).lr)

    def test_seed_variant_adds_k_to_the_seed_and_keeps_the_trailing_comment(self) -> None:
        self.assertEqual(cal.read_seed(TEXT), 20261101)
        out = cal.seed_variant(TEXT, 2)
        self.assertEqual(cal.read_seed(out), 20261103)
        changed = _lines_changed(TEXT, out)
        self.assertEqual(len(changed), 1)
        self.assertIn("# trailing comment kept", changed[0][2])
        with self.assertRaises(ValueError):
            cal.seed_variant(TEXT, 0)

    def test_the_seed_genome_still_parses_with_the_new_seed(self) -> None:
        out = cal.seed_variant(BASE, 1)
        self.assertEqual(parse_genome(out).seed, parse_genome(BASE).seed + 1)

    def test_variant_dispatch(self) -> None:
        self.assertEqual(cal.variant_text(TEXT, "incumbent"), TEXT)
        self.assertEqual(cal.variant_text(TEXT, "eps:1e-05:3"), cal.eps_variant(TEXT, 1e-5, 3))
        self.assertEqual(cal.variant_text(TEXT, "seed:2"), cal.seed_variant(TEXT, 2))
        self.assertEqual(cal.variant_text(TEXT, "gene:MERGE.theta_m=0.9834"),
                         __import__("creature.genes", fromlist=["x"]).apply_mutation(TEXT, "MERGE.theta_m", 0.9834))
        with self.assertRaises(ValueError):
            cal.variant_text(TEXT, "bogus:1")


# ----------------------------------------------------------------------------------------------------- a synthetic closed life
def _png(rgb) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _at(i: int) -> str:
    return f"2026-09-23T{(i * 2) // 60:02d}:{(i * 2) % 60:02d}:00.000Z"


def _build_tape(root: Path, n: int, seed: int = 4242, start: int = 0) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(start, start + n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        at = _at(i)
        if i % 7 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt", at=at)
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png", at=at)


class _Synthetic(unittest.TestCase):
    """One closed life: 40 canvases, a shadow checkpoint, 24 more canvases. The slice is the tape after the checkpoint."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-test-"))
        cls.root = cls.tmp / "life"
        _build_tape(cls.root, 40)
        shadow = ev.build_or_resume_shadow(cls.tmp / "shadow", FIXTURE, cls.root)
        ev.advance_shadow(shadow, cls.root)
        cls.cp_dir = ev.checkpoint_shadow(shadow, cls.tmp / "checkpoints", "2026-09-23T01:20:00.000Z")
        cls.cp_last_seq = shadow.last_seq
        shadow.close()
        _build_tape(cls.root, 24, seed=9999, start=40)
        cls.to_seq = max(int(r["seq"]) for r in read_tape(cls.root))
        cls.slice_root = cls.tmp / "slice"
        cls.manifest = cal.stage_slice(cls.root, None, cls.cp_last_seq, cls.to_seq, cls.slice_root)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)


class TestStageSlice(_Synthetic):
    def test_the_staged_tape_holds_exactly_the_slice_rows_and_reads_through_the_shared_reader(self) -> None:
        want = [r for r in read_tape(self.root) if self.cp_last_seq < int(r["seq"]) <= self.to_seq]
        got = list(read_tape(self.slice_root))
        self.assertGreater(len(want), 20, "presence: the slice is not empty")
        self.assertEqual(got, want)
        self.assertEqual(ev.tape_slice(self.slice_root, self.cp_last_seq, self.to_seq), want)

    def test_every_payload_a_row_names_was_copied_byte_for_byte(self) -> None:
        n = 0
        for r in read_tape(self.slice_root):
            if r.get("payload"):
                src = self.root / "tape" / r["payload"]
                dst = self.slice_root / "tape" / r["payload"]
                self.assertTrue(dst.exists(), r["payload"])
                self.assertEqual(dst.read_bytes(), src.read_bytes())
                n += 1
        self.assertEqual(n, self.manifest["n_payloads"])
        self.assertGreater(n, 20)

    def test_the_manifest_names_what_was_staged(self) -> None:
        m = self.manifest
        self.assertEqual((m["from_seq"], m["to_seq"]), (self.cp_last_seq, self.to_seq))
        self.assertEqual(m["n_rows"], len(list(read_tape(self.slice_root))))
        self.assertEqual(len(m["rows_sha256"]), 64)
        self.assertEqual(json.loads((self.slice_root / "STAGED.json").read_text()), m)
        self.assertIn("source_root", m)

    def test_verify_reads_the_source_again_and_agrees(self) -> None:
        v = cal.verify_staged_slice(self.root, None, self.slice_root)
        self.assertTrue(v["equal"], v)
        self.assertEqual(v["row_mismatches"], 0)
        self.assertEqual(v["missing_payloads"], [])
        self.assertGreater(v["rows_checked"], 20)

    def test_verify_catches_a_deleted_payload_and_a_changed_row(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-plant-"))
        try:
            plant = tmp / "slice"
            shutil.copytree(self.slice_root, plant)
            pay = sorted((plant / "tape" / "payload").iterdir())[3]
            self.assertTrue(pay.exists())
            pay.unlink()
            self.assertFalse(pay.exists(), "the plant removed the file")
            v = cal.verify_staged_slice(self.root, None, plant)
            self.assertFalse(v["equal"])
            self.assertIn("payload/" + pay.name, v["missing_payloads"])
            # a changed row (one byte of one row's sha)
            plant2 = tmp / "slice2"
            shutil.copytree(self.slice_root, plant2)
            day = sorted((plant2 / "tape").glob("*.jsonl"))[0]
            text = day.read_text()
            before = text
            text = text.replace('"sha": "', '"sha": "0', 1)
            self.assertNotEqual(text, before, "the plant changed the bytes")
            day.write_text(text)
            v2 = cal.verify_staged_slice(self.root, None, plant2)
            self.assertFalse(v2["equal"])
            self.assertGreaterEqual(v2["row_mismatches"], 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:49 +0400 — two gaps the instrument's own mutation sweep named before it ran
    # (a verifier that never reads payload CONTENT; a stager that skips a hole instead of refusing it).
    def test_verify_catches_a_changed_payload_byte(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-plant-"))
        try:
            plant = tmp / "slice"
            shutil.copytree(self.slice_root, plant)
            pay = sorted((plant / "tape" / "payload").iterdir())[5]
            b = bytearray(pay.read_bytes())
            before = bytes(b)
            b[len(b) // 2] ^= 1
            self.assertNotEqual(bytes(b), before, "the plant changed the bytes")
            pay.write_bytes(bytes(b))
            v = cal.verify_staged_slice(self.root, None, plant)
            self.assertFalse(v["equal"])
            self.assertIn("payload/" + pay.name, v["payload_mismatches"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_missing_source_payload_is_refused_not_skipped(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-hole-"))
        try:
            life = tmp / "life"
            shutil.copytree(self.root, life)
            victim = next(p for p in sorted((life / "tape" / "payload").iterdir()) if int(p.name.split(".")[0]) > self.cp_last_seq)
            self.assertTrue(victim.exists())
            victim.unlink()
            self.assertFalse(victim.exists(), "the plant removed the file")
            with self.assertRaises(FileNotFoundError):
                cal.stage_slice(life, None, self.cp_last_seq, self.to_seq, tmp / "s")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_staging_refuses_a_non_empty_destination(self) -> None:
        with self.assertRaises(FileExistsError):
            cal.stage_slice(self.root, None, self.cp_last_seq, self.to_seq, self.slice_root)

    def test_a_declared_run_tape_path_resolves_like_the_tape_does(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="evolve-cal-decl-"))
        try:
            out = tmp / "s"
            m = cal.stage_slice(self.root, "run/tape", self.cp_last_seq, self.to_seq, out)
            self.assertEqual(m["rows_sha256"], self.manifest["rows_sha256"])
            self.assertTrue((out / "tape" / "payload").is_dir())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestStageCheckpoint(unittest.TestCase):
    def _fake_cp(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="evolve-cal-cp-"))
        (d / "state" / "prev").mkdir(parents=True)
        rng = np.random.default_rng(1)
        (d / "state" / "organism.npz").write_bytes(rng.bytes(50_000))
        (d / "state" / "ledger.json").write_text(json.dumps({"a": [1, 2, 3]}))
        (d / "state" / "prev" / "organism.npz").write_bytes(rng.bytes(10_000))
        (d / "GENOME.genome").write_text(TEXT)
        (d / "META.json").write_text(json.dumps({"n": 1, "at": "2026-09-23T01:00:00.000Z", "last_seq": 10}))
        return d

    def test_stage_copies_every_file_and_the_manifest_hashes_them(self) -> None:
        src = self._fake_cp()
        dst = Path(tempfile.mkdtemp(prefix="evolve-cal-cp-dst-")) / "cp"
        try:
            m = cal.stage_checkpoint(src, dst)
            self.assertEqual(m["n_files"], 5)
            self.assertEqual(m["files"]["state/organism.npz"], hashlib.sha256((src / "state" / "organism.npz").read_bytes()).hexdigest())
            self.assertTrue(cal.verify_staged_checkpoint(src, dst)["equal"])
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(dst.parent, ignore_errors=True)

    def test_verify_catches_a_flipped_byte_and_an_extra_file(self) -> None:
        src = self._fake_cp()
        dst = Path(tempfile.mkdtemp(prefix="evolve-cal-cp-dst-")) / "cp"
        try:
            cal.stage_checkpoint(src, dst)
            f = dst / "state" / "organism.npz"
            b = bytearray(f.read_bytes())
            before = bytes(b)
            b[100] ^= 1
            self.assertNotEqual(bytes(b), before, "the plant changed the bytes")
            f.write_bytes(bytes(b))
            v = cal.verify_staged_checkpoint(src, dst)
            self.assertFalse(v["equal"])
            self.assertIn("state/organism.npz", v["mismatches"])
            f.write_bytes(before)
            self.assertTrue(cal.verify_staged_checkpoint(src, dst)["equal"], "restored: equal again (the control)")
            (dst / "state" / "extra.bin").write_bytes(b"x")
            v2 = cal.verify_staged_checkpoint(src, dst)
            self.assertFalse(v2["equal"])
            self.assertIn("state/extra.bin", v2["extra"])
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(dst.parent, ignore_errors=True)

    def test_stage_refuses_a_non_empty_destination(self) -> None:
        src = self._fake_cp()
        dst = Path(tempfile.mkdtemp(prefix="evolve-cal-cp-dst-"))
        try:
            (dst / "already").write_text("x")
            with self.assertRaises(FileExistsError):
                cal.stage_checkpoint(src, dst)
        finally:
            shutil.rmtree(src, ignore_errors=True)
            shutil.rmtree(dst, ignore_errors=True)


class TestCompareTwins(unittest.TestCase):
    ROWS = [
        {"seq": 1, "moment": "a", "act": "glance", "fix": [[1, 2]], "cells": [10, 5], "err": 0.5, "lr": 0.5, "hash": "h1", "residual": [0.1], "confirmed": [False]},
        {"seq": 2, "moment": "b", "act": "glance", "fix": [[2, 2]], "cells": [10, 5], "err": 0.4, "lr": 0.5, "hash": "h2", "residual": [0.2], "confirmed": [True]},
        {"seq": 3, "think": {"say": "x"}},
        {"seq": 4, "moment": "c", "act": "glance", "fix": [[3, 3]], "cells": [11, 5], "err": 0.3, "lr": 0.4, "hash": "h3", "residual": [0.3], "confirmed": [True]},
    ]

    def test_identical_journals_are_identical(self) -> None:
        r = cal.compare_twins(self.ROWS, json.loads(json.dumps(self.ROWS)))
        self.assertTrue(r["identical"])
        self.assertEqual((r["n_a"], r["n_b"], r["rows_differing"], r["first_diff"]), (4, 4, 0, None))
        self.assertEqual(r["equal_prefix"], 4)
        self.assertIsNone(r["first_discrete_diff"])

    def test_a_float_only_difference_is_a_difference_but_not_a_discrete_one(self) -> None:
        other = json.loads(json.dumps(self.ROWS))
        other[1]["residual"] = [0.2000001]
        other[1]["hash"] = "h2x"
        r = cal.compare_twins(self.ROWS, other)
        self.assertFalse(r["identical"])
        self.assertEqual(r["first_diff"], 1)
        self.assertEqual(r["rows_differing"], 1)
        self.assertEqual(r["discrete_diff_rows"], 0, "residual and hash are continuous witnesses, not discrete outcomes")
        self.assertIsNone(r["first_discrete_diff"], "no discrete outcome ever differed: there is no first one")
        self.assertEqual(sorted(r["diff_key_counts"]), ["hash", "residual"])

    def test_a_discrete_difference_is_counted_and_located(self) -> None:
        other = json.loads(json.dumps(self.ROWS))
        before = json.dumps(other[3])
        other[3]["cells"] = [12, 5]
        other[2]["think"] = {"say": "y"}
        self.assertNotEqual(json.dumps(other[3]), before, "the plant changed the bytes")
        r = cal.compare_twins(self.ROWS, other)
        self.assertEqual(r["first_diff"], 2)
        self.assertEqual(r["rows_differing"], 2)
        self.assertEqual(r["discrete_diff_rows"], 2)
        self.assertEqual(r["first_discrete_diff"], 2)
        self.assertEqual(r["diff_key_counts"]["cells"], 1)
        self.assertEqual(r["diff_key_counts"]["think"], 1)
        self.assertEqual(len(r["by_decile"]), 10)
        self.assertEqual(sum(r["by_decile"]), 2)

    def test_the_first_discrete_difference_is_not_the_first_difference(self) -> None:
        # a continuous witness differs from row 0 (an epsilon perturbation), a discrete outcome only at row 3: both positions are reported
        other = json.loads(json.dumps(self.ROWS))
        other[0]["hash"] = "h1x"
        before = json.dumps(other[3])
        other[3]["cells"] = [12, 5]
        self.assertNotEqual(json.dumps(other[3]), before, "the plant changed the bytes")
        r = cal.compare_twins(self.ROWS, other)
        self.assertEqual(r["first_diff"], 0)
        self.assertEqual(r["first_discrete_diff"], 3)
        self.assertEqual(r["discrete_diff_rows"], 1)

    def test_different_lengths_are_not_identical_and_say_so(self) -> None:
        r = cal.compare_twins(self.ROWS, self.ROWS[:3])
        self.assertFalse(r["identical"])
        self.assertEqual((r["n_a"], r["n_b"]), (4, 3))
        self.assertEqual(r["equal_prefix"], 3)
        self.assertEqual(r["first_diff"], 3)


class TestCompareKeyed(unittest.TestCase):
    """A think row that lands one boundary later shifts every later row by one INDEX (the seed pair of the STOP test read 307 of 935 rows «different» with
    the organism's final state_hash EQUAL): the keyed comparison matches rows by what they ARE — a moment row by (seq, glance, act), any other row by its
    kind and seq — so a shifted journal is not a diverged one."""

    @staticmethod
    def moment(seq, glance=0, cells=(10, 5), err=0.5, hash_="h", word="circle"):
        return {"seq": seq, "moment": f"m{seq}", "act": "glance", "glance": glance, "cells": list(cells), "err": err, "hash": f"{hash_}{seq}",
                "word": word, "fix": [[1, 2]], "residual": [0.1], "confirmed": [False]}

    def rows(self):
        return [self.moment(10), self.moment(11), {"seq": 12, "think": {"say": "x"}}, self.moment(13), {"seq": 14, "outcome": {"r": 0}}, self.moment(15)]

    def test_identical_journals_have_no_keyed_difference(self) -> None:
        r = cal.compare_twins_keyed(self.rows(), json.loads(json.dumps(self.rows())))
        self.assertEqual((r["moment"]["matched"], r["moment"]["differing"], r["moment"]["discrete_differing"]), (4, 0, 0))
        self.assertEqual((r["moment"]["only_a"], r["moment"]["only_b"]), (0, 0))
        self.assertIsNone(r["moment"]["first_discrete_seq"])
        self.assertEqual(r["other"]["think"], {"matched": 1, "differing": 0, "only_a": 0, "only_b": 0})

    def test_a_shifted_journal_is_not_a_diverged_one(self) -> None:
        a = self.rows()
        b = json.loads(json.dumps(a))
        b.insert(1, {"seq": 10, "think": {"say": "late"}})            # an extra row early: every later row moves by one index
        pos = cal.compare_twins(a, b)
        self.assertGreater(pos["rows_differing"], 2, "the positional comparison reads the shift as divergence")
        r = cal.compare_twins_keyed(a, b)
        self.assertEqual((r["moment"]["differing"], r["moment"]["discrete_differing"]), (0, 0))
        self.assertEqual(r["other"]["think"]["only_b"], 1)
        self.assertEqual(r["other"]["think"]["matched"], 1)

    def test_a_discrete_difference_in_a_moment_row_is_found_by_its_seq(self) -> None:
        a = self.rows()
        b = json.loads(json.dumps(a))
        before = json.dumps(b[3], sort_keys=True)
        b[3]["cells"] = [11, 5]
        self.assertNotEqual(json.dumps(b[3], sort_keys=True), before, "the plant changed the bytes")
        r = cal.compare_twins_keyed(a, b)
        self.assertEqual((r["moment"]["differing"], r["moment"]["discrete_differing"]), (1, 1))
        self.assertEqual(r["moment"]["first_discrete_seq"], 13)
        self.assertEqual(r["moment"]["diff_key_counts"], {"cells": 1})

    def test_a_float_only_or_hash_only_difference_is_not_discrete(self) -> None:
        a = self.rows()
        b = json.loads(json.dumps(a))
        b[0]["hash"] = "other"
        b[1]["err"] = 0.5000001
        r = cal.compare_twins_keyed(a, b)
        self.assertEqual((r["moment"]["differing"], r["moment"]["discrete_differing"]), (2, 0))
        self.assertIsNone(r["moment"]["first_discrete_seq"])

    def test_a_moment_row_only_one_twin_wrote_is_counted_not_dropped(self) -> None:
        a = self.rows()
        b = [x for x in json.loads(json.dumps(a)) if x.get("seq") != 13]
        self.assertEqual(len(b), len(a) - 1, "the plant removed the row")
        r = cal.compare_twins_keyed(a, b)
        self.assertEqual((r["moment"]["only_a"], r["moment"]["only_b"], r["moment"]["matched"]), (1, 0, 3))

    def test_two_glances_of_one_seq_are_two_rows_and_a_repeat_is_matched_in_order(self) -> None:
        a = [self.moment(20, glance=0), self.moment(20, glance=1), {"seq": 21, "outcome": {"r": 1}}, {"seq": 21, "outcome": {"r": 2}}]
        b = json.loads(json.dumps(a))
        b[3]["outcome"] = {"r": 3}
        r = cal.compare_twins_keyed(a, b)
        self.assertEqual(r["moment"]["matched"], 2)
        self.assertEqual(r["other"]["outcome"], {"matched": 2, "differing": 1, "only_a": 0, "only_b": 0})


class TestRunTwin(_Synthetic):
    def _run(self, name: str, variant: str, **kw) -> dict:
        out = self.tmp / "out" / name
        text = cal.variant_text((self.cp_dir / "GENOME.genome").read_text(), variant)
        return cal.run_twin(self.cp_dir, text, self.slice_root, self.cp_last_seq, self.to_seq, out, variant=variant, **kw)

    def test_a_twin_writes_its_readings_and_cleans_its_state_copy(self) -> None:
        r = self._run("t1", "incumbent")
        out = self.tmp / "out" / "t1"
        for k in ("q1_seen", "confirmed_share", "frames_filed", "wall_s", "cpu_s", "state_hash", "row_hash", "journal_sha256",
                  "journal_rows", "rows_consumed", "load0", "load1", "psi0", "psi1", "maxrss_kb", "variant", "genome_sha256", "code"):
            self.assertIn(k, r, k)
        self.assertEqual(r["variant"], "incumbent")
        self.assertEqual(len(r["state_hash"]), 64)
        self.assertGreater(r["cpu_s"], 0)
        self.assertGreater(r["wall_s"], 0)
        self.assertGreater(r["maxrss_kb"], 0)
        self.assertEqual(r["rows_consumed"], self.manifest["n_rows"])
        self.assertEqual(json.loads((out / "reading.json").read_text()), json.loads(json.dumps(r)))
        self.assertTrue((out / "GENOME.genome").exists())
        self.assertFalse((out / "root" / "state").exists(), "the big state copy is removed once graded")
        with gzip.open(out / "journal.jsonl.gz", "rt") as f:
            lines = f.read().splitlines()
        self.assertEqual(len(lines), r["journal_rows"])
        self.assertEqual(hashlib.sha256("\n".join(lines).encode()).hexdigest(), r["journal_sha256"])

    def test_state_hash_is_the_snapshots_own_digest(self) -> None:
        # the reading's dense hash is the organism's state_hash AFTER close, equal to the digest the close wrote into its own snapshot
        r = self._run("sh", "incumbent", keep_state=True)
        meta = json.loads((self.tmp / "out" / "sh" / "root" / "state" / "organism.json").read_text())
        self.assertEqual(len(meta["state_hash"]), 64)
        self.assertEqual(r["state_hash"], meta["state_hash"])

    def test_the_same_twin_twice_is_bit_identical(self) -> None:
        a = self._run("same-a", "incumbent")
        b = self._run("same-b", "incumbent")
        self.assertEqual(a["state_hash"], b["state_hash"])
        self.assertEqual(a["journal_sha256"], b["journal_sha256"])
        self.assertEqual(a["q1_seen"], b["q1_seen"])
        ra = cal.read_twin_journal(self.tmp / "out" / "same-a")
        rb = cal.read_twin_journal(self.tmp / "out" / "same-b")
        self.assertTrue(cal.compare_twins(ra, rb)["identical"])

    def test_the_variant_reaches_the_twins_genome_file(self) -> None:
        r = self._run("eps", "eps:1e-05:3")
        text = (self.tmp / "out" / "eps" / "GENOME.genome").read_text()
        want = cal.eps_variant((self.cp_dir / "GENOME.genome").read_text(), 1e-5, 3)
        self.assertEqual(text, want)
        self.assertEqual(r["genome_sha256"], hashlib.sha256(want.encode()).hexdigest())
        self.assertNotEqual(r["genome_sha256"], hashlib.sha256((self.cp_dir / "GENOME.genome").read_bytes()).hexdigest())

    def test_rows_limit_cuts_the_slice(self) -> None:
        r = self._run("short", "incumbent", rows_limit=10)
        self.assertEqual(r["rows_consumed"], 10)

    def test_a_planted_change_in_one_twin_is_caught_by_the_comparison(self) -> None:
        self._run("pa", "incumbent")
        ra = cal.read_twin_journal(self.tmp / "out" / "pa")
        rb = json.loads(json.dumps(ra))
        i = next(k for k, x in enumerate(rb) if "cells" in x)
        before = json.dumps(rb[i])
        rb[i]["cells"] = [rb[i]["cells"][0] + 1, rb[i]["cells"][1]]
        self.assertNotEqual(json.dumps(rb[i]), before, "the plant changed the bytes")
        r = cal.compare_twins(ra, rb)
        self.assertFalse(r["identical"])
        self.assertEqual(r["first_diff"], i)
        self.assertEqual(r["discrete_diff_rows"], 1)


class TestCli(_Synthetic):
    def test_the_twin_and_compare_commands_run_end_to_end(self) -> None:
        a, b = self.tmp / "cli-a", self.tmp / "cli-b"
        common = ["--cp", str(self.cp_dir), "--slice-root", str(self.slice_root), "--from-seq", str(self.cp_last_seq),
                  "--to-seq", str(self.to_seq), "--variant", "incumbent", "--rows-limit", "12"]
        self.assertEqual(cal.main(["twin", *common, "--out", str(a)]), 0)
        self.assertEqual(cal.main(["twin", *common, "--out", str(b)]), 0)
        self.assertTrue((a / "reading.json").exists() and (b / "reading.json").exists())
        out = self.tmp / "cmp.json"
        self.assertEqual(cal.main(["compare", "--a", str(a), "--b", str(b), "--out", str(out)]), 0)
        res = json.loads(out.read_text())
        self.assertTrue(res["journal"]["identical"])
        self.assertTrue(res["state_hash_equal"])

    def test_stage_commands_run_and_the_verify_flag_reads_the_source_again(self) -> None:
        s = self.tmp / "cli-slice"
        rc = cal.main(["stage-slice", "--live-root", str(self.root), "--from-seq", str(self.cp_last_seq),
                       "--to-seq", str(self.to_seq), "--out", str(s), "--verify"])
        self.assertEqual(rc, 0)
        c = self.tmp / "cli-cp"
        self.assertEqual(cal.main(["stage-checkpoint", "--src", str(self.cp_dir), "--dst", str(c), "--verify"]), 0)


if __name__ == "__main__":
    unittest.main()
