# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 15:41 +0400 — PREREG-RESIT-READER (branch resit-1003; the law's text b02cf10, sha256 f6390b0d…, signed by the author, the architect 15:30 and the seat 15:31):
# tools/brain/resit.py's PURE parts, written BEFORE the reader. Each test reads what the law says; every plant asserts that it changed the bytes (#247 (5)) and is CAUGHT.
# The children (ANSWER, GRADE), the orchestrator and R1 itself are tested in test_resit_children.py and by the real run.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:39 +0400 — the VERIFIER's finding on c887b50: test_n_early_is_printed_per_set_and_zero_reads_untested used a fixture with NO begin row, so it pinned a clause («n_early = 0
# reads UNTESTED») that cannot fire on real data: `begin` is EARLY by construction. Rebuilt on the REAL shape (begin, two held items, a why, an end); n_early_tested (begin and end left out) is what UNTESTED reads (law erratum E1).
"""tests/tools/test_resit.py — the re-sit reader's pure helpers (flags, canonical rows, phrase classes, pairing, the genome in force, state copies,
items and journal scans, R9's early/late split, restarts, the verdict-copy flag, the series store)."""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np
from scipy import stats

from tools.brain import resit as R

SHAPES = ("circle", "cross", "ring", "square", "star", "triangle")
COLOURS = ("blue", "green", "red", "white", "yellow")
SIZES = ("big", "small")


class Tmp(unittest.TestCase):
    def mk(self, prefix: str = "resit-") -> Path:
        d = Path(tempfile.mkdtemp(prefix=prefix))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------------------------------------ flags (§1.0, R11's «a run without -B is refused»)
class TestFlags(unittest.TestCase):
    ENV = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}

    def test_all_set_is_accepted_and_recorded(self) -> None:
        got = R.check_flags(1, 1, dict(self.ENV))
        self.assertEqual(got["dont_write_bytecode"], True)
        self.assertEqual(got["isolated"], True)
        self.assertEqual(got["OPENBLAS_NUM_THREADS"], "1")
        self.assertEqual(got["OMP_NUM_THREADS"], "1")

    def test_a_run_without_B_is_refused(self) -> None:
        with self.assertRaises(R.ResitError) as cm:
            R.check_flags(0, 1, dict(self.ENV))
        self.assertIn("-B", str(cm.exception))

    def test_a_run_without_I_is_refused(self) -> None:
        with self.assertRaises(R.ResitError) as cm:
            R.check_flags(1, 0, dict(self.ENV))
        self.assertIn("-I", str(cm.exception))

    def test_each_blas_pin_is_required_and_must_be_one(self) -> None:
        for var in self.ENV:
            for bad in (None, "4", "0", ""):
                env = dict(self.ENV)
                if bad is None:
                    env.pop(var)
                else:
                    env[var] = bad
                with self.subTest(var=var, bad=bad):
                    with self.assertRaises(R.ResitError) as cm:
                        R.check_flags(1, 1, env)
                    self.assertIn(var, str(cm.exception))


# ------------------------------------------------------------------------------------------------ canonical rows (R1 (a): deep equality after a JSON round trip)
class TestCanon(unittest.TestCase):
    def test_key_order_is_irrelevant(self) -> None:
        a = {"x": 1, "y": [1, 2, {"b": 1, "a": 2}]}
        b = {"y": [1, 2, {"a": 2, "b": 1}], "x": 1}
        self.assertTrue(R.rows_equal(a, b))

    def test_int_and_float_are_different_bytes(self) -> None:
        self.assertFalse(R.rows_equal({"v": 1}, {"v": 1.0}))

    def test_nan_equals_nan_and_infinity_is_kept(self) -> None:
        a = {"v": float("nan"), "w": float("inf")}
        b = {"v": float("nan"), "w": float("inf")}
        self.assertTrue(R.rows_equal(a, b))
        self.assertFalse(R.rows_equal({"v": float("inf")}, {"v": float("-inf")}))

    def test_hash_is_set_aside_and_nothing_else(self) -> None:
        a = {"item": "M1:1", "answer": {"kind": "thing", "hyp": 1}, "hash": "aaa"}
        b = {"item": "M1:1", "answer": {"kind": "thing", "hyp": 1}, "hash": "bbb"}
        self.assertTrue(R.rows_equal(a, b))
        c = {"item": "M1:1", "answer": {"kind": "thing", "hyp": 2}, "hash": "aaa"}
        self.assertFalse(R.rows_equal(a, c))

    def test_a_planted_one_digit_change_is_caught_and_changed_the_bytes(self) -> None:
        a = {"fix": [[1, 2], [3, 4]], "answer": {"raw": {"p": 0.5}}}
        b = json.loads(json.dumps(a))
        b["answer"]["raw"]["p"] = 0.5000000000000001
        self.assertNotEqual(R.canon(a), R.canon(b), "the plant must change the bytes")
        self.assertFalse(R.rows_equal(a, b))

    def test_a_missing_key_is_a_difference(self) -> None:
        self.assertFalse(R.rows_equal({"a": 1, "b": 2}, {"a": 1}))


# ------------------------------------------------------------------------------------------------ phrase classes (R6)
class TestPhraseClass(unittest.TestCase):
    def test_the_three_classes_and_the_priority(self) -> None:
        self.assertEqual(R.phrase_class(["small", "green", "circle"]), "colour_or_size")
        self.assertEqual(R.phrase_class(["circle"]), "shape_only")
        self.assertEqual(R.phrase_class(["white", "circle"]), "white")
        self.assertEqual(R.phrase_class(["small", "white", "star"]), "white")      # white > colour_or_size
        self.assertEqual(R.phrase_class(["big", "circle"]), "colour_or_size")
        self.assertEqual(R.phrase_class(["green", "star"]), "colour_or_size")

    def test_exactly_one_class_for_every_phrase_of_up_to_three_words(self) -> None:
        import itertools
        words = SHAPES + COLOURS + SIZES
        n = 0
        for r in (1, 2, 3):
            for combo in itertools.combinations(words, r):
                cls = R.phrase_class(list(combo))
                self.assertIn(cls, R.CLASSES)
                n += 1
                if "white" in combo:
                    self.assertEqual(cls, "white")
                elif any(w in COLOURS or w in SIZES for w in combo):
                    self.assertEqual(cls, "colour_or_size")
                else:
                    self.assertEqual(cls, "shape_only")
        self.assertEqual(n, 13 + 78 + 286)

    def test_a_word_of_no_type_is_refused_by_name(self) -> None:
        with self.assertRaises(R.ResitError) as cm:
            R.phrase_class(["zog", "circle"])
        self.assertIn("zog", str(cm.exception))

    def test_an_empty_phrase_is_refused(self) -> None:
        with self.assertRaises(R.ResitError):
            R.phrase_class([])


class TestClassRates(unittest.TestCase):
    RECS = [
        {"class": "white", "in_g": True, "correct": True},
        {"class": "white", "in_g": True, "correct": False},
        {"class": "white", "in_g": False, "correct": False},
        {"class": "colour_or_size", "in_g": True, "correct": True},
        {"class": "colour_or_size", "in_g": True, "correct": True},
    ]

    def test_counts_rates_left_out_and_the_smallest_gap(self) -> None:
        t = R.class_rates(self.RECS)
        self.assertEqual(t["white"]["n"], 2)
        self.assertEqual(t["white"]["k"], 1)
        self.assertEqual(t["white"]["items"], 3)
        self.assertEqual(t["white"]["left_out"], 1)
        self.assertAlmostEqual(t["white"]["rate"], 0.5)
        self.assertAlmostEqual(t["white"]["smallest_gap"], 10 / 2)
        self.assertEqual(t["colour_or_size"]["k"], 2)
        self.assertTrue(t["white"]["underpowered"], "n < 30 reads UNDERPOWERED by name")

    def test_an_empty_class_reads_na_never_zero(self) -> None:
        t = R.class_rates(self.RECS)
        self.assertTrue(t["shape_only"]["na"])
        self.assertIsNone(t["shape_only"]["rate"])
        self.assertEqual(t["shape_only"]["items"], 0)

    def test_thirty_is_not_underpowered(self) -> None:
        recs = [{"class": "white", "in_g": True, "correct": True}] * 30
        self.assertFalse(R.class_rates(recs)["white"]["underpowered"])
        recs = [{"class": "white", "in_g": True, "correct": True}] * 29
        self.assertTrue(R.class_rates(recs)["white"]["underpowered"])


# ------------------------------------------------------------------------------------------------ pairing (R8 c)
class TestPairing(unittest.TestCase):
    O = [1, 1, 1, 1, 0, 0, 1, None, 0, 1]
    D = [1, 0, 1, 0, 0, 1, 1, 1, None, 1]

    def vec(self, v):
        return {f"i{k}": x for k, x in enumerate(v)}

    def test_planted_vectors_with_known_b_and_c(self) -> None:
        p = R.pair_vectors(self.vec(self.D), self.vec(self.O))
        # by hand: both present on i0..i6 and i9 -> 8 paired; right->wrong at i1, i3 (b = 2); wrong->right at i5 (c = 1)
        self.assertEqual(p["n_paired"], 8)
        self.assertEqual(p["b"], 2)
        self.assertEqual(p["c"], 1)
        self.assertAlmostEqual(p["g"], (1 - 2) / 8)
        self.assertAlmostEqual(p["smallest_gap"], 10 / 8)
        nd = 3
        self.assertAlmostEqual(p["p_fall"], float(stats.binom.sf(2 - 1, nd, 0.5)), places=12)
        self.assertAlmostEqual(p["p_rise"], float(stats.binom.sf(1 - 1, nd, 0.5)), places=12)

    def test_exact_sign_p_equals_scipy_on_a_grid(self) -> None:
        for b in range(0, 12):
            for c in range(0, 12):
                nd = b + c
                want = 1.0 if nd == 0 else float(stats.binom.sf(b - 1, nd, 0.5)) if b > 0 else 1.0
                self.assertAlmostEqual(R.exact_sign_p(b, c), want, places=12, msg=f"b={b} c={c}")

    def test_no_discordant_pair_is_p_one(self) -> None:
        p = R.pair_vectors(self.vec([1, 0, 1]), self.vec([1, 0, 1]))
        self.assertEqual(p["b"], 0)
        self.assertEqual(p["c"], 0)
        self.assertEqual(p["p_fall"], 1.0)
        self.assertEqual(p["g"], 0.0)

    def test_nothing_paired_reads_none_not_zero(self) -> None:
        p = R.pair_vectors({"a": None}, {"a": 1})
        self.assertEqual(p["n_paired"], 0)
        self.assertIsNone(p["g"])
        self.assertIsNone(p["smallest_gap"])

    def test_swapping_the_two_vectors_swaps_b_and_c_the_check_can_fail(self) -> None:
        a = R.pair_vectors(self.vec(self.D), self.vec(self.O))
        b = R.pair_vectors(self.vec(self.O), self.vec(self.D))
        self.assertEqual((a["b"], a["c"]), (b["c"], b["b"]))
        self.assertNotEqual(a["g"], b["g"])

    def test_items_in_one_vector_only_are_left_out(self) -> None:
        p = R.pair_vectors({"a": 1, "b": 0, "x": 1}, {"a": 1, "b": 1, "y": 0})
        self.assertEqual(p["n_paired"], 2)     # a and b only; x and y are in one vector each
        self.assertEqual(p["b"], 1)            # b: right in the origin (1), wrong on the day (0)
        self.assertEqual(p["c"], 0)


# ------------------------------------------------------------------------------------------------ the genome in force (§1.2, AM2, AM3; R4 e, f)
GEN0 = "SEED 1\nKWTA 5\nRETINA a b c\nGAZE g 4\nSENSE colour rg\nBRAIN lr 0.01\n"
GEN1 = "SEED 1\nKWTA 4\nRETINA a b c\nGAZE g 4\nSENSE colour rg\nBRAIN lr 0.01\n"
GEN2 = "SEED 1\nKWTA 3\nRETINA a b c\nGAZE g 4\nSENSE colour rg\nBRAIN lr 0.01\n"


def epoch_row(seq: int, epoch: int, text: str, gene: str = "KWTA.k", value: int = 4) -> dict:
    return {"seq": seq, "epoch": {"epoch": epoch, "genome_sha": sha(text.encode("utf-8")), "moment": 1, "gene": gene, "value": value,
                                  "proposal_no": epoch}, "hash": "h"}


class TestGenomeInForce(Tmp):
    def life(self, epochs=((100, 1, GEN1),), extra_rows=()) -> Path:
        root = self.mk("resit-life-")
        (root / "journal").mkdir()
        (root / "GENOME.genome").write_text(GEN0)
        lines = []
        for seq, ep, text in epochs:
            (root / f"GENOME.v{ep}.genome").write_text(text)
            lines.append(json.dumps(epoch_row(seq, ep, text)))
        lines.extend(json.dumps(r) for r in extra_rows)
        (root / "journal" / "2026-10-03.jsonl").write_text("\n".join(lines) + "\n")
        return root

    def test_the_gate_rule_is_strictly_before_the_begin_ask(self) -> None:
        root = self.life()
        rows = R.read_epoch_rows(root / "journal")
        self.assertEqual(R.genome_in_force(root, rows, before_seq=50)["epoch"], 0)
        self.assertEqual(R.genome_in_force(root, rows, before_seq=100)["epoch"], 0, "the adoption AT the begin seq is not before it")
        self.assertEqual(R.genome_in_force(root, rows, before_seq=101)["epoch"], 1)

    def test_the_daily_rule_is_at_or_before_the_states_last_seq(self) -> None:
        root = self.life()
        rows = R.read_epoch_rows(root / "journal")
        self.assertEqual(R.genome_in_force(root, rows, upto_seq=99)["epoch"], 0)
        self.assertEqual(R.genome_in_force(root, rows, upto_seq=100)["epoch"], 1)
        self.assertEqual(R.genome_in_force(root, rows, upto_seq=10**9)["epoch"], 1)

    def test_epoch_zero_is_the_launch_genome_and_epoch_k_its_file(self) -> None:
        root = self.life()
        rows = R.read_epoch_rows(root / "journal")
        g0 = R.genome_in_force(root, rows, before_seq=1)
        g1 = R.genome_in_force(root, rows, upto_seq=1000)
        self.assertEqual(g0["path"], root / "GENOME.genome")
        self.assertEqual(g1["path"], root / "GENOME.v1.genome")
        self.assertEqual(g1["sha256"], sha(GEN1.encode("utf-8")))
        self.assertEqual(g0["sha256"], sha(GEN0.encode("utf-8")))

    def test_the_highest_epoch_inside_the_bound_wins(self) -> None:
        root = self.life(epochs=((100, 1, GEN1), (200, 2, GEN2)))
        rows = R.read_epoch_rows(root / "journal")
        self.assertEqual(R.genome_in_force(root, rows, upto_seq=150)["epoch"], 1)
        self.assertEqual(R.genome_in_force(root, rows, upto_seq=250)["epoch"], 2)
        self.assertEqual(R.genome_in_force(root, rows, before_seq=200)["epoch"], 1)

    def test_a_genome_whose_sha_is_not_the_epoch_rows_is_refused_R4e(self) -> None:
        root = self.life()
        before = (root / "GENOME.v1.genome").read_bytes()
        (root / "GENOME.v1.genome").write_text(GEN1.replace("KWTA 4", "KWTA 9"))
        self.assertNotEqual(before, (root / "GENOME.v1.genome").read_bytes(), "the plant must change the bytes")
        rows = R.read_epoch_rows(root / "journal")
        with self.assertRaises(R.Refused) as cm:
            R.genome_in_force(root, rows, upto_seq=1000)
        self.assertIn("sha", str(cm.exception).lower())

    def test_versioned_files_and_no_epoch_rows_is_undetermined_R4f(self) -> None:
        root = self.life()
        (root / "journal" / "2026-10-03.jsonl").write_text("")
        rows = R.read_epoch_rows(root / "journal")
        self.assertEqual(rows, [])
        with self.assertRaises(R.Refused) as cm:
            R.genome_in_force(root, rows, upto_seq=1000)
        self.assertIn("undetermined", str(cm.exception).lower())

    def test_an_epoch_row_without_its_file_is_refused(self) -> None:
        root = self.life()
        (root / "GENOME.v1.genome").unlink()
        rows = R.read_epoch_rows(root / "journal")
        with self.assertRaises(R.Refused):
            R.genome_in_force(root, rows, upto_seq=1000)

    def test_no_versioned_files_and_no_epoch_rows_is_the_launch_genome(self) -> None:
        root = self.mk("resit-life-")
        (root / "journal").mkdir()
        (root / "GENOME.genome").write_text(GEN0)
        (root / "journal" / "x.jsonl").write_text(json.dumps({"seq": 1, "kind": "answer"}) + "\n")
        g = R.genome_in_force(root, R.read_epoch_rows(root / "journal"), upto_seq=10)
        self.assertEqual(g["epoch"], 0)

    def test_only_a_real_epoch_row_counts_not_a_refused_one_or_a_stray_word(self) -> None:
        extra = [{"seq": 5, "epoch_refused": {"reason": "x", "gene": "KWTA.k", "value": 4, "proposal_no": 2}},
                 {"seq": 6, "kind": "say", "words": ["epoch"], "note": "the epoch"},
                 {"seq": 7, "epoch": "not a dict"}]
        root = self.life(extra_rows=extra)
        rows = R.read_epoch_rows(root / "journal")
        self.assertEqual([r["epoch"] for r in rows], [1])
        self.assertEqual(rows[0]["seq"], 100)

    def test_line_hashes_are_taken_of_the_four_lines_alone(self) -> None:
        a = R.genome_line_hashes(GEN0)
        b = R.genome_line_hashes(GEN1)          # KWTA differs, the four lines do not
        self.assertEqual(a["retina"], b["retina"])
        self.assertEqual(a["gaze"], b["gaze"])
        self.assertEqual(a["colour"], b["colour"])
        self.assertEqual(a["brain"], b["brain"])
        self.assertNotEqual(a["genome"], b["genome"])
        c = R.genome_line_hashes(GEN0.replace("GAZE g 4", "GAZE g 5"))
        self.assertNotEqual(a["gaze"], c["gaze"], "the plant (one GAZE line changed) must be seen")
        self.assertEqual(a["retina"], c["retina"])

    def test_a_trailing_comment_does_not_move_a_line_hash(self) -> None:
        a = R.genome_line_hashes(GEN0)
        b = R.genome_line_hashes(GEN0.replace("GAZE g 4", "GAZE g 4   # a comment"))
        self.assertEqual(a["gaze"], b["gaze"])


# ------------------------------------------------------------------------------------------------ state copies (R4 a-c; §1.1 S1)
class TestStateCopy(Tmp):
    def life_with_prev(self) -> Path:
        root = self.mk("resit-life-")
        prev = root / "state" / "prev"
        prev.mkdir(parents=True)
        (prev / "brain.json").write_text('{"v": 1}')
        (prev / "brain.npz").write_bytes(os.urandom(4096))
        os.utime(prev / "brain.json", ns=(1_700_000_000_000_000_000, 1_700_000_000_123_456_789))
        os.utime(prev / "brain.npz", ns=(1_700_000_001_000_000_000, 1_700_000_001_987_654_321))
        prints = {}
        for n in ("brain.json", "brain.npz"):
            st = (prev / n).stat()
            prints[n] = [st.st_size, st.st_mtime_ns]
        (prev / "SNAPSHOT.json").write_text(json.dumps({"files": list(prints), "last_seq": 777, "prints": prints, "t": 4242}))
        return root

    def test_a_good_copy_keeps_size_and_mtime_ns_and_reports_the_manifest(self) -> None:
        root = self.life_with_prev()
        dest = self.mk("resit-copy-")
        info = R.copy_state_prev(root, dest, sleeper=lambda s: None)
        for n in ("brain.json", "brain.npz"):
            a, b = (root / "state" / "prev" / n).stat(), (dest / n).stat()
            self.assertEqual((a.st_size, a.st_mtime_ns), (b.st_size, b.st_mtime_ns))
        self.assertEqual(info["last_seq"], 777)
        self.assertEqual(info["t"], 4242)
        self.assertTrue(info["prints_ok"])

    def test_a_copy_whose_mtime_ns_differs_is_refused_R4b(self) -> None:
        root = self.life_with_prev()
        dest = self.mk("resit-copy-")
        R.copy_state_prev(root, dest, sleeper=lambda s: None)
        prints = json.loads((root / "state" / "prev" / "SNAPSHOT.json").read_text())["prints"]
        before = (dest / "brain.npz").stat().st_mtime_ns
        os.utime(dest / "brain.npz", ns=(before, before + 1))
        self.assertNotEqual(before, (dest / "brain.npz").stat().st_mtime_ns, "the plant must change the mtime")
        with self.assertRaises(R.Refused) as cm:
            R.verify_prints(dest, prints)
        self.assertIn("mtime_ns", str(cm.exception))

    def test_a_copy_whose_size_differs_is_refused(self) -> None:
        root = self.life_with_prev()
        dest = self.mk("resit-copy-")
        R.copy_state_prev(root, dest, sleeper=lambda s: None)
        prints = json.loads((root / "state" / "prev" / "SNAPSHOT.json").read_text())["prints"]
        with open(dest / "brain.npz", "ab") as f:
            f.write(b"x")
        with self.assertRaises(R.Refused) as cm:
            R.verify_prints(dest, prints)
        self.assertIn("size", str(cm.exception))

    def test_no_state_prev_is_a_skip_by_name_R4c(self) -> None:
        root = self.mk("resit-life-")
        dest = self.mk("resit-copy-")
        with self.assertRaises(R.Skipped) as cm:
            R.copy_state_prev(root, dest, sleeper=lambda s: None)
        self.assertIn("state/prev", str(cm.exception))

    def test_a_generation_replaced_during_the_copy_is_retried_then_refused(self) -> None:
        root = self.life_with_prev()
        dest = self.mk("resit-copy-")
        sleeps = []
        n = {"calls": 0}

        def hook() -> None:      # the generation is replaced under the copier's feet, every time
            n["calls"] += 1
            p = root / "state" / "prev" / "SNAPSHOT.json"
            d = json.loads(p.read_text())
            d["last_seq"] += 1
            p.write_text(json.dumps(d))

        with self.assertRaises(R.Refused) as cm:
            R.copy_state_prev(root, dest, retries=3, sleep_s=20.0, sleeper=sleeps.append, after_copy=hook)
        self.assertEqual(n["calls"], 3)
        self.assertEqual(sleeps, [20.0, 20.0], "sleep between the tries, not after the last")
        self.assertIn("3", str(cm.exception))

    def test_a_generation_replaced_once_is_retried_and_then_good(self) -> None:
        root = self.life_with_prev()
        dest = self.mk("resit-copy-")
        n = {"calls": 0}

        def hook() -> None:
            n["calls"] += 1
            if n["calls"] == 1:
                p = root / "state" / "prev" / "SNAPSHOT.json"
                d = json.loads(p.read_text())
                d["t"] += 1
                p.write_text(json.dumps(d))

        info = R.copy_state_prev(root, dest, retries=3, sleeper=lambda s: None, after_copy=hook)
        self.assertEqual(n["calls"], 2)
        self.assertEqual(info["t"], 4243)


# ------------------------------------------------------------------------------------------------ the tape fixture (§1.3)
def write_tape(root: Path, spec: list, seq0: int = 1000, payload_bytes=None) -> None:
    """spec: ("ask", moment, payload_dict) | ("eye", moment, kind, png_bytes) | ("ear", moment, word). Writes root/tape/<day>.jsonl + payload/."""
    tape = root / "tape"
    (tape / "payload").mkdir(parents=True, exist_ok=True)
    rows = []
    seq = seq0
    for item in spec:
        seq += 1
        if item[0] == "ask":
            _, moment, payload = item
            body = json.dumps(payload).encode()
            name = f"payload/{seq:09d}.json"
            (tape / name).write_bytes(body)
            meta = {"moment": moment, "source": "scene", "form": payload["form"]}
            if payload.get("item"):
                meta["item"] = payload["item"]
            rows.append({"seq": seq, "at": f"2026-10-03T10:00:{seq % 60:02d}.000Z", "sense": "ask", "sha": sha(body), "payload": name, "meta": meta})
        elif item[0] == "eye":
            _, moment, kind, png = item
            name = f"payload/{seq:09d}.png"
            (tape / name).write_bytes(png)
            meta = {"moment": moment, "source": "scene"}
            if kind:
                meta.update({"kind": kind, "set": "fresh", "split": "test", "row": 0})
            rows.append({"seq": seq, "at": f"2026-10-03T10:00:{seq % 60:02d}.000Z", "sense": "eye", "sha": sha(png), "payload": name, "meta": meta})
        elif item[0] == "ear":
            _, moment, word = item
            rows.append({"seq": seq, "at": f"2026-10-03T10:00:{seq % 60:02d}.000Z", "sense": "ear", "sha": "e", "payload": "x",
                         "meta": {"moment": moment, "source": "maker", "word": word}})
    (tape / "2026-10-03.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def two_set_spec(png: bytes = b"\x89PNG-a") -> list:
    asks = []
    for s in ("fresh", "s1b1"):
        asks.append(("ask", f"sc-{s}-begin", {"form": "begin", "set": s, "test_seed": 7}))
        asks.append(("ask", f"sc-{s}-0", {"form": "point", "item": f"M1:{s}:0", "mark": "M1", "phrase": ["small", "green", "circle"], "test_seed": 7,
                                           "box": None, "centroid": None, "word": None}))
        asks.append(("ask", f"sc-{s}-0", {"form": "point", "item": f"M2a:{s}:0", "mark": "M2a", "phrase": ["green", "star"], "test_seed": 7,
                                           "box": None, "centroid": None, "word": None}))
        asks.append(("eye", f"sc-{s}-0", "sitting", png + s.encode()))
        asks.append(("ask", f"sc-{s}-why", {"form": "why", "item": "M4:red", "mark": "M4", "word": "red", "test_seed": 7}))
        asks.append(("ask", f"sc-{s}-end", {"form": "end", "set": s, "test_seed": 7}))
    spec = [("ear", "m-other", "bar"), ("eye", "m-other", None, b"\x89PNG-maker")] + asks
    return spec


class TestItemsScan(Tmp):
    def life(self, spec=None) -> Path:
        root = self.mk("resit-items-")
        write_tape(root, spec if spec is not None else two_set_spec())
        return root

    def test_sets_begin_end_and_counts(self) -> None:
        sc = R.scan_items(self.life(), None)
        self.assertEqual(sorted(sc["sets"]), ["fresh", "s1b1"])
        f = sc["sets"]["fresh"]
        self.assertEqual(f["n_asks"], 5)            # begin, 2 points, why, end
        self.assertLess(f["begin_seq"], f["end_seq"])
        self.assertLess(f["end_seq"], sc["sets"]["s1b1"]["begin_seq"])
        self.assertEqual(sc["n_asks"], 10)
        self.assertEqual(sc["n_canvases"], 2, "only the eye rows of kind sitting are the items' canvases; the maker's is not")

    def test_asks_carry_item_mark_set_phrase_and_class(self) -> None:
        sc = R.scan_items(self.life(), None)
        by_item = {a["item"]: a for a in sc["asks"] if a["item"]}
        m1 = by_item["M1:fresh:0"]
        self.assertEqual((m1["mark"], m1["set"], m1["class"]), ("M1", "fresh", "colour_or_size"))
        self.assertEqual(by_item["M2a:s1b1:0"]["class"], "colour_or_size")

    def test_the_digests_do_not_depend_on_the_seq_numbers(self) -> None:
        a = R.scan_items(self.life(), None)
        root2 = self.mk("resit-items-")
        write_tape(root2, two_set_spec(), seq0=50_000)
        b = R.scan_items(root2, None)
        self.assertEqual(a["ask_digest"], b["ask_digest"])
        self.assertEqual(a["canvas_digest"], b["canvas_digest"])
        self.assertNotEqual(a["sets"]["fresh"]["begin_seq"], b["sets"]["fresh"]["begin_seq"])

    def test_a_planted_payload_byte_changes_the_ask_digest_and_a_canvas_byte_the_canvas_digest(self) -> None:
        a = R.scan_items(self.life(), None)
        spec = two_set_spec()
        spec2 = []
        for it in spec:
            if it[0] == "ask" and it[2].get("item") == "M1:fresh:0":
                p = dict(it[2]); p["phrase"] = ["small", "green", "cross"]
                it = ("ask", it[1], p)
            spec2.append(it)
        root2 = self.mk("resit-items-")
        write_tape(root2, spec2)
        b = R.scan_items(root2, None)
        self.assertNotEqual(a["ask_digest"], b["ask_digest"])
        self.assertEqual(a["canvas_digest"], b["canvas_digest"])
        root3 = self.mk("resit-items-")
        write_tape(root3, two_set_spec(png=b"\x89PNG-b"))
        c = R.scan_items(root3, None)
        self.assertNotEqual(a["canvas_digest"], c["canvas_digest"])
        self.assertEqual(a["ask_digest"], c["ask_digest"])

    def test_a_tape_without_sittings_reads_zero_sets(self) -> None:
        sc = R.scan_items(self.life([("ear", "m", "bar"), ("eye", "m", None, b"x")]), None)
        self.assertEqual(sc["sets"], {})
        self.assertEqual(sc["n_asks"], 0)

    def test_an_ask_row_whose_sha_is_not_its_payloads_is_refused(self) -> None:
        root = self.life()
        f = next((root / "tape").glob("*.jsonl"))
        lines = f.read_text().splitlines()
        rows = [json.loads(x) for x in lines]
        for r in rows:
            if r["sense"] == "ask":
                r["sha"] = "0" * 64
                break
        f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        with self.assertRaises(R.Refused) as cm:
            R.scan_items(root, None)
        self.assertIn("sha", str(cm.exception))

    def test_a_phrase_of_no_type_is_refused_by_name_R6(self) -> None:
        spec = []
        for it in two_set_spec():
            if it[0] == "ask" and it[2].get("item") == "M1:fresh:0":
                it = ("ask", it[1], dict(it[2], phrase=["zog", "circle"]))
            spec.append(it)
        root = self.mk("resit-items-")
        write_tape(root, spec)
        with self.assertRaises(R.ResitError) as cm:
            R.scan_items(root, None)
        self.assertIn("zog", str(cm.exception))

    def test_the_tape_dir_follows_the_declared_path(self) -> None:
        root = self.mk("resit-items-")
        write_tape(root, two_set_spec())
        os.rename(root / "tape", root / "tape2")
        sc = R.scan_items(root, "run/tape2")
        self.assertEqual(sc["n_asks"], 10)
        self.assertEqual(R.resolve_tape_dir(root, "run/tape2"), root / "tape2")
        self.assertEqual(R.resolve_tape_dir(root, None), root / "tape")
        self.assertEqual(R.resolve_tape_dir(root, "run/tape"), root / "tape")

    def test_resolve_tape_dir_is_the_lifes_own_function(self) -> None:
        from creature.tape import _resolve_tape_dir
        root = Path("/x")
        for decl in (None, "", "run/tape", "run/tape2", "tape3", "a/b/c", "run"):
            self.assertEqual(R.resolve_tape_dir(root, decl), _resolve_tape_dir(root, decl), decl)


class TestItemsPin(Tmp):
    def scan(self, **over) -> dict:
        root = self.mk("resit-items-")
        write_tape(root, two_set_spec())
        sc = R.scan_items(root, None)
        sc.update(over)
        return sc

    def test_first_run_writes_the_pin_and_the_second_identical_run_passes(self) -> None:
        out = self.mk("resit-out-")
        sc = self.scan()
        pin = R.pin_items(out, sc, scored={"path": "/s", "marks_sha256": "abc"}, world_line_sha="w1", items_root="/r")
        self.assertTrue((out / "ITEMS.json").exists())
        self.assertEqual(pin["ask_digest"], sc["ask_digest"])
        again = R.pin_items(out, sc, scored={"path": "/s", "marks_sha256": "abc"}, world_line_sha="w1", items_root="/r")
        self.assertEqual(again, pin)

    def test_every_pinned_field_is_checked_and_a_difference_is_refused_by_name(self) -> None:
        out = self.mk("resit-out-")
        sc = self.scan()
        R.pin_items(out, sc, scored={"path": "/s", "marks_sha256": "abc"}, world_line_sha="w1", items_root="/r")
        base = dict(scored={"path": "/s", "marks_sha256": "abc"}, world_line_sha="w1", items_root="/r")
        cases = [("ask_digest", dict(sc, ask_digest="x" * 64), base), ("canvas_digest", dict(sc, canvas_digest="y" * 64), base),
                 ("n_asks", dict(sc, n_asks=sc["n_asks"] + 1), base), ("n_canvases", dict(sc, n_canvases=99), base),
                 ("world_scene_line_sha", sc, dict(base, world_line_sha="w2")),
                 ("scored", sc, dict(base, scored={"path": "/s", "marks_sha256": "zzz"})),
                 ("root", sc, dict(base, items_root="/other"))]
        for field, s2, kw in cases:
            with self.subTest(field=field):
                with self.assertRaises(R.Refused) as cm:
                    R.pin_items(out, s2, **kw)
                self.assertIn(field, str(cm.exception))


# ------------------------------------------------------------------------------------------------ the journal fixture (P0, R9, restarts)
def ans(seq, item, form="point", eye_seq=None, answer=None, mark="M1", moment="m", at="2026-10-03T10:00:00.000Z", fix=None, hyps=None):
    return {"kind": "answer", "by": "brain", "item": item, "mark": mark, "form": form,
            "answer": answer if answer is not None else {"kind": "thing", "hyp": 0, "raw": {"p": 0.5}},
            "moment": moment, "seq": seq, "eye_seq": eye_seq, "at": at, "fix": fix, "hyps": hyps, "detail": None}


def brain(seq, act, **extra):
    return {"kind": "brain", "act": act, "moment": "m", "seq": seq, "at": "2026-10-03T10:00:00.000Z", **extra}


def write_journal(root: Path, rows: list, name: str = "2026-10-03.jsonl") -> Path:
    j = root / "journal"
    j.mkdir(parents=True, exist_ok=True)
    with (j / name).open("a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return j


class TestJournalScan(Tmp):
    def test_answers_by_ask_seq_acts_epochs_and_starts_are_read(self) -> None:
        root = self.mk("resit-j-")
        rows = [brain(5, "turn"), brain(5, "learn"), brain(5, "calibrate"),
                {"seq": None, "at": "t", "event": "start", "resumed_from_seq": 0},
                ans(10, None, form="begin", mark=None),
                ans(11, "M1:a", eye_seq=13),
                {"seq": None, "at": "t2", "event": "start", "resumed_from_seq": 12},
                epoch_row(20, 1, GEN1)]
        write_journal(root, rows)
        js = R.scan_journal(root / "journal")
        self.assertEqual(sorted(js["answers"]), [10, 11])
        self.assertEqual(js["brain_rows"], [(5, "turn"), (5, "learn"), (5, "calibrate")])
        self.assertEqual([e["epoch"] for e in js["epochs"]], [1])
        self.assertEqual([s["resumed_from_seq"] for s in js["starts"]], [0, 12])

    def test_why_asked_in_two_sittings_under_one_item_name_are_two_asks_not_duplicates(self) -> None:
        root = self.mk("resit-j-")
        write_journal(root, [ans(100, "M4:red", form="why", mark="M4"), ans(200, "M4:red", form="why", mark="M4")])
        js = R.scan_journal(root / "journal")
        dup = R.collapse_duplicates(js["answers"])
        self.assertEqual(dup["restart_duplicates"], 0)
        self.assertEqual(sorted(dup["rows"]), [100, 200])

    def test_two_equal_rows_for_one_ask_seq_collapse_to_the_last_and_are_counted(self) -> None:
        root = self.mk("resit-j-")
        a = ans(100, "M1:x")
        b = dict(a)                              # the resumed process wrote it again, byte for byte
        write_journal(root, [a, ans(101, "M1:y"), b])
        dup = R.collapse_duplicates(R.scan_journal(root / "journal")["answers"])
        self.assertEqual(dup["restart_duplicates"], 1)
        self.assertEqual(dup["divergent"], [])
        self.assertEqual(dup["rows"][100], b)

    def test_two_unequal_rows_for_one_ask_seq_are_restart_divergent_R4k(self) -> None:
        root = self.mk("resit-j-")
        a = ans(100, "M1:x")
        b = ans(100, "M1:x", answer={"kind": "thing", "hyp": 2, "raw": {"p": 0.9}})
        self.assertNotEqual(R.canon(a), R.canon(b), "the plant must change the bytes")
        write_journal(root, [a, b])
        dup = R.collapse_duplicates(R.scan_journal(root / "journal")["answers"])
        self.assertEqual(dup["divergent"], [100])
        with self.assertRaises(R.Refused) as cm:
            R.require_no_divergent(dup)
        self.assertIn("RESTART-DIVERGENT", str(cm.exception))

    def test_an_answer_row_in_a_second_day_file_is_found(self) -> None:
        root = self.mk("resit-j-")
        write_journal(root, [ans(1, "a")], "2026-10-02.jsonl")
        write_journal(root, [ans(2, "b")], "2026-10-03.jsonl")
        js = R.scan_journal(root / "journal")
        self.assertEqual(sorted(js["answers"]), [1, 2])


class TestEarlyLate(Tmp):
    """R9 / AM1 (a)-(c): EARLY iff no kind:brain row whose act is NOT in {turn, refused} has begin_seq < seq < answering_seq."""

    BEGIN = 10

    def classify(self, answers, brain_rows):
        return R.classify_early_late({"answers": answers, "brain_rows": brain_rows}, {"fresh": self.BEGIN})

    def test_the_answering_seq_is_the_eye_seq_for_a_held_form_and_the_ask_seq_otherwise(self) -> None:
        self.assertEqual(R.answering_seq({"seq": 11, "eye_seq": 13}), 13)
        self.assertEqual(R.answering_seq({"seq": 11, "eye_seq": None}), 11)

    def test_a_learn_between_a_held_ask_and_its_eye_row_makes_the_item_late(self) -> None:
        answers = {11: [ans(11, "M1:a", eye_seq=13)]}
        got = self.classify(answers, [(12, "learn")])
        self.assertEqual(got["by_ask_seq"][11], "LATE")

    def test_the_seq_keyed_reading_would_have_said_early_the_plant_changes_the_outcome(self) -> None:
        # the AM1 (a) defect, planted: classed by the ASK's seq (11) the learn at 12 lies AFTER it, so the item reads EARLY; by the answering seq (13) it is LATE
        row = ans(11, "M1:a", eye_seq=13)
        learn = [(12, "learn")]
        naive_early = not any(self.BEGIN < s < row["seq"] for s, a in learn if a not in ("turn", "refused"))
        right_early = not any(self.BEGIN < s < R.answering_seq(row) for s, a in learn if a not in ("turn", "refused"))
        self.assertTrue(naive_early)
        self.assertFalse(right_early)
        self.assertEqual(self.classify({11: [row]}, learn)["by_ask_seq"][11], "LATE")

    def test_a_canvas_less_form_is_answered_at_its_ask_row(self) -> None:
        answers = {11: [ans(11, None, form="why", eye_seq=None)]}
        self.assertEqual(self.classify(answers, [(12, "learn")])["by_ask_seq"][11], "EARLY")
        self.assertEqual(self.classify(answers, [(10 + 0, "learn")])["by_ask_seq"][11], "EARLY", "begin_seq is exclusive")
        self.assertEqual(self.classify(answers, [(11, "learn")])["by_ask_seq"][11], "EARLY", "answering_seq is exclusive")
        self.assertEqual(self.classify({11: [ans(11, None, form="why", eye_seq=None)]}, [(10, "x")])["by_ask_seq"][11], "EARLY")

    def test_the_bounds_are_strict_on_both_sides(self) -> None:
        answers = {11: [ans(11, "M1:a", eye_seq=14)]}
        self.assertEqual(self.classify(answers, [(10, "learn")])["by_ask_seq"][11], "EARLY")     # at begin_seq: not after it
        self.assertEqual(self.classify(answers, [(11, "learn")])["by_ask_seq"][11], "LATE")      # between
        self.assertEqual(self.classify(answers, [(13, "learn")])["by_ask_seq"][11], "LATE")
        self.assertEqual(self.classify(answers, [(14, "learn")])["by_ask_seq"][11], "EARLY")     # at the answering seq: not before it

    def test_a_calibrate_only_row_is_late(self) -> None:
        answers = {11: [ans(11, "M1:a", eye_seq=13)]}
        self.assertEqual(self.classify(answers, [(12, "calibrate")])["by_ask_seq"][11], "LATE")

    def test_an_unknown_act_is_late_the_set_fails_closed(self) -> None:
        answers = {11: [ans(11, "M1:a", eye_seq=13)]}
        for act in ("sleep", "rehearse", "xyz", None):
            with self.subTest(act=act):
                self.assertEqual(self.classify(answers, [(12, act)])["by_ask_seq"][11], "LATE")

    def test_a_turn_or_a_refused_row_is_still_early(self) -> None:
        answers = {11: [ans(11, "M1:a", eye_seq=13)]}
        self.assertEqual(self.classify(answers, [(12, "turn")])["by_ask_seq"][11], "EARLY")
        self.assertEqual(self.classify(answers, [(12, "refused")])["by_ask_seq"][11], "EARLY")
        self.assertEqual(self.classify(answers, [(12, "turn"), (12, "refused"), (12, "turn")])["by_ask_seq"][11], "EARLY")

    def sitting(self) -> dict:
        """The REAL shape of a sitting: a begin ask (answered at its own row), two held items, a why, an end."""
        return {10: [ans(10, None, form="begin", mark=None)], 11: [ans(11, "M1:a", eye_seq=13)], 14: [ans(14, "M1:b", eye_seq=16)],
                17: [ans(17, "M4:red", form="why", mark="M4")], 20: [ans(20, None, form="end", mark=None)]}

    def test_n_early_and_n_early_tested_are_both_printed_begin_and_end_test_nothing(self) -> None:
        got = self.classify(self.sitting(), [(25, "learn")])                                     # the brain moves only after the sitting: all five answers are EARLY
        d = got["by_set"]["fresh"]
        self.assertEqual((d["n_early"], d["n_early_tested"], d["n_late"], d["untested"]), (5, 3, 0, False))
        self.assertEqual(d["note"], "")

    def test_a_set_whose_only_early_item_is_begin_reads_untested_the_real_shape(self) -> None:
        # a learn right after begin: begin stays EARLY (nothing lies strictly between begin and its own seq); every other answer is LATE. The old clause («n_early = 0») could never fire here: n_early is 1.
        got = self.classify(self.sitting(), [(12, "learn"), (15, "learn")])
        d = got["by_set"]["fresh"]
        self.assertEqual((d["n_early"], d["n_early_tested"], d["n_late"]), (1, 0, 4))
        self.assertTrue(d["untested"])
        self.assertIn("UNTESTED", d["note"])

    def test_one_tested_early_item_is_enough_to_be_tested(self) -> None:
        got = self.classify(self.sitting(), [(15, "learn")])                                     # M1:a (11 -> 13) lies before the learn; M1:b, the why and the end do not
        d = got["by_set"]["fresh"]
        self.assertEqual((d["n_early"], d["n_early_tested"], d["n_late"]), (2, 1, 3))
        self.assertFalse(d["untested"])
        self.assertNotIn("UNTESTED", d["note"])

    def test_begin_and_end_alone_test_nothing_an_equal_acknowledgement_is_not_a_test(self) -> None:
        answers = {10: [ans(10, None, form="begin", mark=None)], 20: [ans(20, None, form="end", mark=None)]}
        d = self.classify(answers, [])["by_set"]["fresh"]
        self.assertEqual((d["n_early"], d["n_early_tested"]), (2, 0))
        self.assertTrue(d["untested"], "both structural forms are left out, not only begin")
        self.assertIn("UNTESTED", d["note"])

    def test_answers_before_their_sets_begin_are_not_classified(self) -> None:
        answers = {5: [ans(5, "M1:old", eye_seq=6)], 11: [ans(11, "M1:a", eye_seq=13)]}
        got = self.classify(answers, [])
        self.assertNotIn(5, got["by_ask_seq"])
        self.assertIn(11, got["by_ask_seq"])

    def test_the_act_census_inside_each_sitting(self) -> None:
        brain_rows = [(3, "learn"), (12, "learn"), (12, "turn"), (13, "calibrate"), (30, "learn"), (40, "refused")]
        c = R.act_census(brain_rows, {"fresh": (10, 20)})
        self.assertEqual(c["fresh"], {"learn": 1, "turn": 1, "calibrate": 1})

    def test_the_two_sets_use_their_own_begin_seq(self) -> None:
        answers = {11: [ans(11, "a", eye_seq=13)], 51: [ans(51, "b", eye_seq=53)]}
        got = R.classify_early_late({"answers": answers, "brain_rows": [(12, "learn")]}, {"fresh": 10, "s1b1": 50})
        self.assertEqual(got["by_ask_seq"][11], "LATE")
        self.assertEqual(got["by_ask_seq"][51], "EARLY", "the learn at 12 is before s1b1's begin: not inside its sitting")


class TestPreconditionP0(unittest.TestCase):
    def test_no_row_of_a_closed_set_of_acts_above_the_first_ask_passes(self) -> None:
        rows = [(1, "turn"), (1, "learn"), (2, "calibrate"), (50, "turn"), (51, "refused")]
        got = R.precondition_p0(rows, first_ask_seq=100)
        self.assertTrue(got["ok"])
        self.assertEqual(got["above"], {})

    def test_a_learn_above_the_first_ask_fails_and_reads_not_gradable(self) -> None:
        rows = [(1, "learn"), (101, "learn")]
        with self.assertRaises(R.NotGradable) as cm:
            R.precondition_p0(rows, first_ask_seq=100)
        self.assertIn("NOT GRADABLE", str(cm.exception))

    def test_every_act_outside_turn_and_refused_fails_it_even_an_unknown_one(self) -> None:
        for act in ("learn", "calibrate", "sleep", "xyz"):
            with self.subTest(act=act):
                with self.assertRaises(R.NotGradable):
                    R.precondition_p0([(1, "turn"), (200, act)], first_ask_seq=100)

    def test_turn_and_refused_above_the_first_ask_are_allowed_and_counted(self) -> None:
        got = R.precondition_p0([(1, "learn"), (200, "turn"), (201, "refused")], first_ask_seq=100)
        self.assertTrue(got["ok"])
        self.assertEqual(got["allowed_above"], {"turn": 1, "refused": 1})

    def test_the_row_at_the_first_ask_seq_is_not_above_it(self) -> None:
        self.assertTrue(R.precondition_p0([(100, "learn")], first_ask_seq=100)["ok"])


# ------------------------------------------------------------------------------------------------ restarts and the verdict-copy flag (R8 d, e, f)
class TestRestarts(unittest.TestCase):
    STARTS = [{"at": "a", "resumed_from_seq": 0}, {"at": "b", "resumed_from_seq": 120}, {"at": "c", "resumed_from_seq": 500},
              {"at": "d", "resumed_from_seq": 400}]

    def test_only_resumed_starts_inside_the_interval_are_printed(self) -> None:
        got = R.restarts_between(self.STARTS, lo_seq=100, hi_seq=400)
        self.assertEqual([r["resumed_from_seq"] for r in got], [120, 400])

    def test_lo_is_exclusive_and_hi_inclusive_and_a_cold_start_never_counts(self) -> None:
        self.assertEqual([r["at"] for r in R.restarts_between(self.STARTS, lo_seq=120, hi_seq=400)], ["d"])
        self.assertEqual(R.restarts_between(self.STARTS, lo_seq=0, hi_seq=10), [], "resumed_from_seq 0 is the cold start, not a restart")

    def test_an_interval_with_no_restart_is_an_empty_list_with_the_presence_count(self) -> None:
        got = R.restarts_info(self.STARTS, lo_seq=1000, hi_seq=2000)
        self.assertEqual(got["restarts"], [])
        self.assertEqual(got["start_rows_seen"], 4)


class TestVerdictFlag(unittest.TestCase):
    def rows(self, post, eye=None):
        eye = eye or [False] * len(post)
        return [{"post_origin_learned": p, "eye_changed": e, "n": i} for i, (p, e) in enumerate(zip(post, eye))]

    def test_the_first_row_at_or_above_8640_is_flagged_and_no_earlier_one(self) -> None:
        got = R.flag_verdict_copy(self.rows([100, 8639, 8640, 9000]))
        self.assertEqual([r.get("verdict_copy", False) for r in got], [False, False, True, False])

    def test_post_origin_learned_is_the_difference_of_the_two_learned_counts(self) -> None:
        self.assertEqual(R.post_origin_learned(copy_n_learned=58_640, origin_n_learned=50_000), 8_640)

    def test_an_eye_changed_row_never_takes_the_verdict_copy(self) -> None:
        got = R.flag_verdict_copy(self.rows([100, 8640, 9000], eye=[False, True, False]))
        self.assertFalse(got[1].get("verdict_copy", False))
        self.assertIn("EYE-CHANGED", got[1]["verdict_copy_note"])
        self.assertFalse(got[2].get("verdict_copy", False), "this law adds no replacement rule: what follows is HEARS-2's to rule")

    def test_nothing_reaches_the_threshold_flags_nothing(self) -> None:
        got = R.flag_verdict_copy(self.rows([1, 2, 3]))
        self.assertFalse(any(r.get("verdict_copy") for r in got))


# ------------------------------------------------------------------------------------------------ the series store (R8 a, b)
class TestSeriesStore(Tmp):
    def test_the_origin_is_written_once_and_a_second_is_refused_R4g(self) -> None:
        out = self.mk("resit-out-")
        R.write_origin(out, {"kind": "origin", "state_hash": "a"})
        self.assertTrue((out / "ORIGIN.json").exists())
        with self.assertRaises(R.Refused) as cm:
            R.write_origin(out, {"kind": "origin", "state_hash": "b"})
        self.assertIn("ORIGIN", str(cm.exception))
        self.assertEqual(R.load_origin(out)["state_hash"], "a", "the first origin is untouched")

    def test_a_daily_run_never_becomes_an_origin_R8b(self) -> None:
        out = self.mk("resit-out-")
        self.assertIsNone(R.load_origin(out))
        pairing = R.pair_with_origin({"marks": {}}, None)
        self.assertIsNone(pairing["vs_origin"])
        self.assertIn("NO ORIGIN", pairing["note"])
        self.assertIn("never", pairing["note"])
        R.append_series(out, {"kind": "daily", "stamp": "x"})
        self.assertFalse((out / "ORIGIN.json").exists(), "appending a daily row creates no origin")

    def test_append_series_is_jsonl_and_the_md_is_rewritten_from_it(self) -> None:
        out = self.mk("resit-out-")
        R.append_series(out, {"kind": "daily", "stamp": "d1", "marks": {}})
        R.append_series(out, {"kind": "daily", "stamp": "d2", "marks": {}})
        lines = (out / "RESIT.jsonl").read_text().splitlines()
        self.assertEqual([json.loads(l)["stamp"] for l in lines], ["d1", "d2"])
        self.assertIn("d2", (out / "RESIT.md").read_text())

    def test_the_fallback_origin_needs_the_seats_reason_R4i(self) -> None:
        with self.assertRaises(R.Refused) as cm:
            R.check_origin_kind("fallback_copy", None)
        self.assertIn("--reason", str(cm.exception))
        with self.assertRaises(R.Refused):
            R.check_origin_kind("fallback_copy", "   ")
        self.assertEqual(R.check_origin_kind("fallback_copy", "the pilot failed")["reason"], "the pilot failed")
        self.assertIsNone(R.check_origin_kind("rebuilt", None)["reason"])

    def test_an_origin_from_state_prev_without_the_fallback_flag_is_refused_R4h(self) -> None:
        with self.assertRaises(R.Refused) as cm:
            R.check_origin_source(from_state_prev=True, origin_kind="rebuilt")
        self.assertIn("fallback_copy", str(cm.exception))
        R.check_origin_source(from_state_prev=True, origin_kind="fallback_copy")
        R.check_origin_source(from_state_prev=False, origin_kind="rebuilt")


if __name__ == "__main__":
    unittest.main()
