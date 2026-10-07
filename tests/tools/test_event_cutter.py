# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-07 — PREREG-OPEN-WORLD-2 §2 build (the law signed at 00b7af0)
"""tests/tools/test_event_cutter.py — the gates and the planted truths of PREREG-OPEN-WORLD-2 on
tools/worlds/event_cutter.py (V1: the organism's own cutter + the brain's first engagement).

Written FIRST, run RED before the tool existed. Fixtures: (i) a synthetic 640-frame err series with 10 planted
spikes at known frames (the cutter must fire at those frames and the shuffled-residual control must NOT align —
the instrument CAN fail); (ii) a hand-written journal in the replay's own row forms (canvas rows with `err` /
`births`, a coarse row that must never be read as a canvas, brain turn/learn rows) so the analyzer's numbers are
known by construction without a replay; (iii) a real small replay for G-INSTRUMENT (byte-identical journals with
and without the cutter reading them); (iv) the bench's own records for G-HEARS (the one-line genome diff, the
untouched provenance).
"""
from __future__ import annotations

import io
import json
import random
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from tools.worlds import event_cutter as EC

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "docs" / "organism" / "whole" / "records" / "open-world-2" / "bench"
BL2_GENOME = Path("/data/dev/genome-wt-mouthcap/scratch/bl2/GENOME.genome")
DATE = "2026-10-07"

N_FRAMES = 640
PLANTS = [20 + 60 * k for k in range(10)]          # the 10 known frames, G-PLANT's own truth
SPIKE = 1.0


def _planted_errs() -> list:
    rng = random.Random(20261007)                   # the fixture's own seed — the baseline, never the science
    errs = [rng.uniform(0.001, 0.01) for _ in range(N_FRAMES)]
    for p in PLANTS:
        errs[p] = SPIKE
    return errs


class SyntheticPlant(unittest.TestCase):
    def test_planted_spikes_fire_at_the_planted_frames(self) -> None:
        seg = EC.segment(_planted_errs())
        for tau in EC.TAUS:
            self.assertEqual(seg["scales"][tau]["boundaries"], PLANTS)      # every scale, exactly the plants
        self.assertEqual(seg["union"], PLANTS)
        self.assertEqual(seg["nesting"]["16_in_1"]["exact"], (10, 10))      # the human form: coarse ⊆ fine

    def test_shuffled_residual_control_does_not_align(self) -> None:
        errs = _planted_errs()
        real = EC.segment(errs)["scales"][1.0]["boundaries"]
        sh = errs[:]
        random.Random(EC.SHUFFLE_SEED).shuffle(sh)                          # the declared fixed seed
        shuf = EC.segment(sh)["scales"][1.0]["boundaries"]
        self.assertEqual(real, PLANTS)                                      # the instrument CAN aim (10 of 10)
        aligned = EC.aligned_count(real, shuf, tol=EC.ALIGN_TOL)
        self.assertEqual((len(shuf), aligned), (9, 2))                      # deterministic at the declared seed
        self.assertLess(aligned / len(real), EC.CONTROL_LIKE_BAR)           # …and the shuffle does NOT segment like it

    def test_naive_knife_and_disagreement_counted(self) -> None:
        knife = EC.naive_knife([0.0, 0.9, 0.0, 0.8, 0.0], 2)
        self.assertEqual(knife, {1, 3})                                     # top-|err| frames, ties to the earlier frame
        self.assertEqual(EC.disagreement({1, 2, 3}, {3, 4}), (3, 2, 1))     # |△|, only-a, only-b


def _canvas(seq: int, err: float, births: int = 0, word: str = None) -> dict:
    r = {"seq": seq, "moment": f"m{seq}", "word": word, "err": err, "ep": None, "hash": "h",
         "act": "glance", "glance": 0, "source": "video"}
    if word is not None:
        r["words"] = [word]
        r["births"] = [[f"w{i}", 100 + i, 0] for i in range(births)]
    return r


JOURNAL = [
    _canvas(1, 0.10), _canvas(2, 0.20, births=2, word="red"),
    {"kind": "brain", "act": "turn", "seq": 2, "moment": "m2", "heard": ["red"], "say": {"words": ["red"]},
     "surprise": 0.5, "n_hyp": 2, "ask": None, "reason": None},
    {"kind": "brain", "act": "learn", "seq": 2, "moment": "m2", "words": ["red"]},
    _canvas(3, 0.90, births=1, word="apple"),
    {"kind": "brain", "act": "turn", "seq": 3, "moment": "m3", "heard": ["apple"], "say": None,
     "surprise": 1.5, "n_hyp": 1, "ask": None, "reason": "not calibrated"},
    {"kind": "brain", "act": "learn", "seq": 3, "moment": "m3", "words": ["apple"]},
    _canvas(4, 0.10),
    {"seq": 4, "moment": "m4", "act": "coarse", "glance": 4, "fix": None, "windows": None, "hash": "h"},   # never a canvas
    _canvas(5, 0.10), _canvas(6, 0.80), _canvas(7, 0.10), _canvas(8, 0.10),
]

TAPE_EYE = [{"seq": i, "sense": "eye", "meta": {"source": "video", "series": "song1"}} for i in range(1, 9)]


class AnalyzerKnown(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="event-cutter-test-"))
        self.journal = self.tmp / "journal.jsonl"
        self.journal.write_text("".join(json.dumps(r) + "\n" for r in JOURNAL))
        tape = self.tmp / "tape"
        tape.mkdir()
        (tape / f"{DATE}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in TAPE_EYE))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_err_series_skips_the_coarse_row(self) -> None:
        errs, canvases = EC.err_series(EC.load_journal(self.journal))
        self.assertEqual(errs, [0.10, 0.20, 0.90, 0.10, 0.10, 0.80, 0.10, 0.10])
        self.assertEqual([c["seq"] for c in canvases], list(range(1, 9)))

    def test_engage_counts_with_presence(self) -> None:
        e = EC.engage(EC.load_journal(self.journal))
        self.assertEqual((e["turns"], e["learns"], e["said"]), (2, 2, 1))
        self.assertEqual((e["canvases"], e["worded"]), (8, 2))
        self.assertEqual(e["turn_reasons"], {"None": 1, "not calibrated": 1})   # the rows' own reasons, tallied
        self.assertAlmostEqual(e["surprise_mean"], 1.0)
        self.assertAlmostEqual(e["surprise_max"], 1.5)

    def test_memory_effect_pair_and_matched_controls(self) -> None:
        rows = EC.load_journal(self.journal)
        _, canvases = EC.err_series(rows)
        learns = EC.learn_per_frame(rows, canvases)
        self.assertEqual(learns, [0, 3, 2, 0, 0, 0, 0, 0])                # births + the brain's learn row at that seq
        ctrls = EC.matched_controls({2}, 8, ["video"] * 8)
        self.assertEqual(ctrls, [1])                                       # nearest non-boundary, tie to the earlier frame
        b, c = EC.memory_pair(learns, [2], ctrls)
        self.assertEqual((b["total"], c["total"]), (2, 3))

    def test_shuffled_boundaries_deterministic_at_the_declared_seed(self) -> None:
        a = EC.shuffled_boundaries(640, 10, EC.SHUFFLE_SEED)
        b = EC.shuffled_boundaries(640, 10, EC.SHUFFLE_SEED)
        self.assertEqual(a, b)
        self.assertEqual((len(a), len(set(a))), (10, 10))
        self.assertTrue(all(0 <= i < 640 for i in a))


class Gates(unittest.TestCase):
    def test_g_hears_the_one_line_diff_and_the_untouched_provenance(self) -> None:
        import difflib
        old = BL2_GENOME.read_text().splitlines()
        new = (BENCH / "GENOME.genome").read_text().splitlines()
        diff = list(difflib.unified_diff(old, new, lineterm=""))
        minus = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
        plus = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
        self.assertEqual((len(minus), len(plus)), (1, 1))                  # EXACTLY one line changed
        self.assertEqual(plus[0], minus[0].replace("hears scene", "hears scene video", 1))
        rows = [json.loads(l) for l in (BENCH / "tape-502" / f"{DATE}.jsonl").read_text().splitlines() if l.strip()]
        eye = [r for r in rows if r["sense"] == "eye"]
        ear = [r for r in rows if r["sense"] == "ear"]
        # the provenance the declaration names: every EYE row keeps source "video"; every ear row keeps the
        # V0 converter's own "video-caption" — unchanged everywhere (§7: no provenance edits)
        self.assertTrue(all(r["meta"]["source"] == "video" for r in eye))
        self.assertTrue(all(r["meta"]["source"] == "video-caption" for r in ear))
        self.assertEqual((len(eye), len(ear)), (502, 428))

    def test_g_instrument_byte_identical_journals_with_and_without_the_cutter(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="event-cutter-gate-"))
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        genome = tmp / "GENOME.genome"
        shutil.copy(BENCH / "GENOME.genome", genome)                       # the bench genome, COPIED, never written
        tape_root = tmp / "troot"
        from creature.tape import Tape
        tape = Tape(tape_root, "vtape")
        rng = np.random.RandomState(7)
        for i in range(12):
            t = f"{DATE}T00:00:{i:02d}.000Z"
            if i in (2, 5):
                tape.publish("ear", b"red", {"moment": f"v{i:06d}", "word": "red", "start": float(i),
                                             "duration": 1.0, "track_kind": "authored", "source": "video-caption"},
                             "txt", at=t)
            rgb = rng.randint(0, 255, size=(128, 128, 3)).astype(np.uint8)
            buf = io.BytesIO()
            Image.fromarray(rgb, "RGB").save(buf, format="PNG")
            tape.publish("eye", buf.getvalue(), {"moment": f"v{i:06d}", "source": "video", "t": float(i)},
                         "png", at=t)
        from creature.replay import run_replay
        j1 = run_replay(genome, tape_root / "vtape", tmp / "out1")
        before = j1.read_bytes()
        EC.analyze(j1, tape_root / "vtape")                                # the cutter observes
        self.assertEqual(j1.read_bytes(), before)                          # …and the journal never moves
        j2 = run_replay(genome, tape_root / "vtape", tmp / "out2")         # the replay without the cutter
        self.assertEqual(j1.read_bytes(), j2.read_bytes())                 # byte-identical, with and without


if __name__ == "__main__":
    unittest.main()
