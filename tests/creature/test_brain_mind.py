# edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:52 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §4 + the seat's two
# addenda): the brain organ wired into the MIND, test-first. The organ itself is builder A's (genome/brain.py); until it lands these tests
# drive a deterministic FakeBrain with the same API (tests/creature/_scene_tape.py) and the REAL-Brain class skips BY NAME.
"""The ask sense, the eye hook, THE ORGANS' ROAD, `--blind brain`, snapshot/resume/replay of the brain and the held asks."""
from __future__ import annotations

import collections
import json
import shutil
import tempfile
import unittest
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unittest import mock

import numpy as np
from PIL import Image

import creature.mind as MM
from creature import organs_road as R
from creature import replay as RP
from genome.machinery import GenomeError
from tests.creature import _scene_tape as S

try:
    import genome.brain as _real_brain          # noqa: F401  builder A's organ
    REAL_BRAIN = hasattr(_real_brain, "Brain")
except ImportError:
    REAL_BRAIN = False

H = namedtuple("H", "members pos")
BLIND = frozenset({"brain"})


def _fake():
    return mock.patch.object(MM, "_brain_class", lambda: S.FakeBrain)


def _replay(genome, tape, out, under: Path, **kw):
    """creature.replay.run_replay with its `creature-replay-*` work root made UNDER `under` (it never removes that root itself —
    pre-existing), so the class's own tearDown removes it: the tests leave no temp root behind."""
    with mock.patch.object(tempfile, "tempdir", str(under)):
        return RP.run_replay(genome, tape, out, **kw)


class _Tape:
    """One fixture tape per class, in a fresh root (#212); every mind gets its own fresh root linked to it."""
    tape_root: Path
    info: Dict[str, object]

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="brain-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = S.build(cls.tape_root)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_mind(self, blind=frozenset(), brain_line: bool = True, rows=None, fake: bool = True):
        owner = self if isinstance(self, type) else type(self)
        owner.n += 1
        root = S.link_root(self.tape_root, self.tmp / f"run{owner.n}" / "r")
        gp = S.write_genome(root.parent / "g.genome", brain=brain_line)
        ctx = _fake() if fake else mock.patch.object(MM, "_brain_class", MM._brain_class)
        with ctx:
            m = MM.Mind(gp, root, blind=blind)
            try:
                for row in (self.rows if rows is None else rows):
                    m.consume(row)
            finally:
                m.close()
        return m, root


# ------------------------------------------------------------------------------------------------ the pointer (§3, addendum 2)
class TestPointer(unittest.TestCase):
    def test_most_fixations_inside_the_box_wins(self) -> None:
        fix = [(2, 2), (2, 3), (10, 10), (3, 2)]
        hyps = [H((0, 1, 3), (2.33, 2.33)), H((2,), (10.0, 10.0))]
        self.assertEqual(R.pointer_hypothesis([8, 8, 24], None, fix, hyps), 0)      # centres 20/28 px inside 8-4 .. 8+24+4
        self.assertEqual(R.pointer_hypothesis([76, 76, 22], None, fix, hyps), 1)    # (10,10) → 84 px

    def test_no_fixation_inside_is_unseen(self) -> None:
        fix = [(2, 2)]
        self.assertIsNone(R.pointer_hypothesis([60, 60, 22], None, fix, [H((0,), (2.0, 2.0))]))

    def test_half_open_edges(self) -> None:
        fix = [(5, 5)]                                   # centre pixel 44
        hyps = [H((0,), (5.0, 5.0))]
        self.assertEqual(R.pointer_hypothesis([48, 48, 22], None, fix, hyps), 0)    # 48-4 = 44 <= 44: inside
        self.assertIsNone(R.pointer_hypothesis([49, 49, 22], None, fix, hyps))      # 45 > 44: outside
        self.assertIsNone(R.pointer_hypothesis([0, 0, 40], None, fix, hyps))        # 44 < 0+40+4 = 44 is False: outside

    def test_a_tie_goes_to_the_mean_position_nearest_the_centroid(self) -> None:
        fix = [(4, 4), (6, 6)]
        hyps = [H((0,), (4.0, 4.0)), H((1,), (6.0, 6.0))]
        box = [24, 24, 32]                               # both centres (36, 52) inside
        self.assertEqual(R.pointer_hypothesis(box, [36.0, 36.0], fix, hyps), 0)     # (36/8 - .5) = 4.0
        self.assertEqual(R.pointer_hypothesis(box, [52.0, 52.0], fix, hyps), 1)     # 6.0
        self.assertEqual(R.pointer_hypothesis(box, [44.0, 44.0], fix, hyps), 0)     # equidistant → the lower index

    @unittest.skipUnless(REAL_BRAIN and hasattr(_real_brain if REAL_BRAIN else None, "pointer_hypothesis"),
                         "genome/brain.py's pointer_hypothesis not on this tree (builder A)")
    def test_equal_to_builder_As_pointer(self) -> None:
        from brain.scene import eye
        rng = np.random.default_rng(20260928)
        n = 0
        for _ in range(400):
            k = int(rng.integers(1, 5))
            fix = [(int(rng.integers(0, 16)), int(rng.integers(0, 16))) for _ in range(k)]
            hyps = eye.hypotheses(fix, rng.standard_normal((k, eye.FEATS)))
            box = [int(rng.integers(0, 100)), int(rng.integers(0, 100)), int(rng.choice([22, 32]))]
            cen = [box[0] + float(rng.uniform(0, box[2])), box[1] + float(rng.uniform(0, box[2]))]
            self.assertEqual(R.pointer_hypothesis(box, cen, fix, hyps), _real_brain.pointer_hypothesis(box, cen, fix, hyps))
            n += 1
        self.assertEqual(n, 400)


# ------------------------------------------------------------------------------------------------ the fixture's seam pin
class TestFixtureSeam(_Tape, unittest.TestCase):
    def test_eye_row_sha_is_the_scored_caches_canvas_sha(self) -> None:
        """gaze.glances takes pic_id = row["sha"]; the scored caches used canvas_png_sha256(rgb). Equal on every eye row, or the
        brain in the body fixates differently from the brain that scored."""
        from brain.world.build import canvas_png_sha256
        eyes = [r for r in self.rows if r["sense"] == "eye"]
        self.assertEqual(len(eyes), self.info["eyes"])
        for r in eyes:
            rgb = np.asarray(Image.open(self.tape_root / "tape" / r["payload"]).convert("RGB"), dtype=np.uint8)
            self.assertEqual(r["sha"], canvas_png_sha256(rgb))

    def test_one_day_file_and_every_row_before_its_eye(self) -> None:
        self.assertEqual(len(self.info["days"]), 1)
        eye_seq = {r["meta"]["moment"]: r["seq"] for r in self.rows if r["sense"] == "eye"}
        for r in self.rows:
            if r["sense"] in ("ear", "ask") and r["meta"].get("moment") in eye_seq:
                self.assertLess(r["seq"], eye_seq[r["meta"]["moment"]])


# ------------------------------------------------------------------------------------------------ the brain's road (FakeBrain)
class TestBrainRoad(_Tape, unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.m, cls.root = cls.run_mind(cls)
        cls.J = S.journal(cls.root)

    def test_one_answer_row_per_ask_row_all_by_the_brain(self) -> None:
        asks = [r for r in self.rows if r["sense"] == "ask"]
        ans = [r for r in self.J if r.get("kind") == "answer"]
        self.assertEqual(len(asks), self.info["asks"])
        self.assertEqual([a["seq"] for a in ans], sorted(r["seq"] for r in asks))
        self.assertEqual({a["by"] for a in ans}, {"brain"})
        self.assertEqual(self.m.asks_answered, len(asks))
        self.assertEqual(self.m.pending_asks, {})

    def test_learn_rows_are_the_training_canvases_only(self) -> None:
        learn = [r for r in self.J if r.get("kind") == "brain" and r.get("act") == "learn"]
        train = [r for r in self.rows if r["sense"] == "eye" and r["meta"].get("kind") == "train"]
        self.assertEqual([r["seq"] for r in learn], [r["seq"] for r in train])
        words_by_moment: Dict[str, List[str]] = {}
        for r in self.rows:
            if r["sense"] == "ear":
                words_by_moment.setdefault(r["meta"]["moment"], []).append(r["meta"]["word"])
        for r in learn:
            self.assertEqual(r["words"], words_by_moment[r["moment"]], "the tape's words, in the parent's order")
        self.assertEqual(self.m.brain_learned, self.info["n_train"])
        from brain.scene import eye
        for r in learn:                      # PREREG: every learn row carries the canvas's fix and the eye's hypotheses
            self.assertIsInstance(r["fix"], list)
            self.assertEqual(r["hyps"], [list(m) for m in eye.groups([tuple(f) for f in r["fix"]])])

    def test_held_asks_answered_on_their_canvas_before_it(self) -> None:
        eye_by_moment = {r["meta"]["moment"]: r for r in self.rows if r["sense"] == "eye"}
        order = [r for r in self.J]
        for a in (r for r in self.J if r.get("kind") == "answer"):
            if a["form"] in ("begin", "end", "why"):
                self.assertIsNone(a["eye_seq"]); self.assertIsNone(a["fix"]); self.assertIsNone(a["hyps"])
                continue
            eye = eye_by_moment[a["moment"]]
            self.assertEqual(a["eye_seq"], eye["seq"])
            self.assertEqual(a["at"], eye["at"])
            self.assertIsInstance(a["fix"], list); self.assertIsInstance(a["hyps"], list)
            self.assertEqual(sorted(i for h in a["hyps"] for i in h), list(range(len(a["fix"]))))
            canvas_rows = [k for k, r in enumerate(order) if r.get("seq") == eye["seq"] and "hash" in r]
            self.assertLess(order.index(a), min(canvas_rows), "the answer is written before the organism lives the canvas")

    def test_every_answer_carries_raw_numpy_made_plain_and_infinity_kept(self) -> None:
        for a in (r for r in self.J if r.get("kind") == "answer"):
            self.assertIn("raw", a["answer"], a)
        pts = [a for a in self.J if a.get("kind") == "answer" and a["form"] == "point" and a["answer"]["kind"] == "thing"]
        self.assertTrue(pts)
        self.assertEqual(pts[0]["answer"]["raw"]["score"], 0.5)
        text = S.journal_bytes(self.root).decode()
        self.assertIn("Infinity", text, "the why band is +inf in the FakeBrain; json writes Infinity")

    def test_brain_status(self) -> None:
        st = self.m.brain_status()
        self.assertEqual(st["scenes"], self.info["n_train"])
        self.assertEqual(st["asks_answered"], self.info["asks"])
        self.assertEqual(st["asks_by"], {"brain": self.info["asks"], "organs": 0})
        self.assertEqual(st["learn_rows"], self.info["n_train"])
        json.dumps(st)

    def test_state_files_and_ledger(self) -> None:
        self.assertTrue((self.root / "state" / "brain.npz").exists())
        self.assertTrue((self.root / "state" / "brain.json").exists())
        self.assertFalse(list((self.root / "state").glob("brain_tmp*")))
        led = json.loads((self.root / "state" / "ledger.json").read_text())
        self.assertEqual(led["asks"]["answered"], self.info["asks"])
        self.assertEqual(led["asks"]["pending"], {})


class TestOtherBlindsLeaveTheBrainItsInput(_Tape, unittest.TestCase):
    """Declared readings, run: `--blind coarse` strips the ORGANISM's coarse glance, never the brain's (FakeBrain.learn asserts
    the coarse glance is present — its own assertion is the pin); `--blind ear` deafens the ORGANISM, the brain hears the tape."""

    def _learn_rows(self, root):
        return [r for r in S.journal(root) if r.get("kind") == "brain" and r.get("act") == "learn"]

    def test_blind_coarse(self) -> None:
        m, root = self.run_mind(blind=frozenset({"coarse"}))
        self.assertEqual(len(self._learn_rows(root)), self.info["n_train"])

    def test_blind_ear(self) -> None:
        _m0, r0 = self.run_mind()
        _m1, r1 = self.run_mind(blind=frozenset({"ear"}))
        a, b = self._learn_rows(r0), self._learn_rows(r1)
        self.assertEqual(len(b), self.info["n_train"])
        self.assertEqual([r["words"] for r in a], [r["words"] for r in b])
        self.assertTrue(all(r["words"] for r in b))


# ------------------------------------------------------------------------------------------------ THE ORGANS' ROAD (the twin)
class TestOrgansRoad(_Tape, unittest.TestCase):
    RAW_KEYS = {"point": [{"point", "none", "none_i"}, {"point", "none", "unheard"}],
                "what": [{"emit"}, {"emit", "uncovered"}],
                "say": [{"spoken", "reason", "target", "readback_point"}, {"spoken", "reason", "uncovered"}]}

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.m, cls.root = cls.run_mind(cls, blind=BLIND)
        cls.J = S.journal(cls.root)

    def test_every_ask_answered_by_the_organs_in_the_graders_shapes(self) -> None:
        self.assertIsNone(self.m.brain)
        ans = [r for r in self.J if r.get("kind") == "answer"]
        self.assertEqual(len(ans), self.info["asks"])
        self.assertEqual({a["by"] for a in ans}, {"organs"})
        kinds = {"point": {"thing", "none", "unheard"}, "what": {"words", "unknown", "unseen"},
                 "say": {"phrase", "declined", "unseen"}, "why": {"because", "unknown"}, "begin": {"begin"}, "end": {"end"}}
        for a in ans:
            self.assertIn(a["answer"]["kind"], kinds[a["form"]], a)
            if a["form"] in self.RAW_KEYS:
                self.assertIn(set(a["answer"]["raw"]), self.RAW_KEYS[a["form"]], a)
            if a["form"] == "why":
                raw = a["answer"]["raw"]
                self.assertEqual(raw, {k: v for k, v in a["answer"].items() if k != "raw"})

    def test_every_canvas_answer_carries_fix_and_hyps_point_none_included(self) -> None:
        """PREREG §3: a `point: None` answer is graded FORCED (a uniform draw over the row's `hyps`) — so it carries them."""
        pts = [a for a in self.J if a.get("kind") == "answer" and a["form"] == "point"]
        self.assertTrue(pts)
        for a in (r for r in self.J if r.get("kind") == "answer" and r["form"] in ("point", "what", "say")):
            self.assertIsInstance(a["fix"], list, a); self.assertIsInstance(a["hyps"], list, a)
            self.assertEqual(sorted(i for h in a["hyps"] for i in h), list(range(len(a["fix"]))))
        none_n = sum(1 for a in pts if a["answer"]["raw"]["point"] is None)
        print(f"\n[organs' road on the fixture] point None on {none_n} of {len(pts)} point asks: "
              f"{sorted(collections.Counter(a['answer']['kind'] for a in pts).items())}")

    def test_a_real_attempt_some_organs_answers_name_something(self) -> None:
        """#228: the twin must still be able to DO the thing — on this 60-scene fixture it says shape names on SPEAK and cites
        episodes for the shape words it met."""
        ans = [r for r in self.J if r.get("kind") == "answer"]
        self.assertTrue(any(a["answer"]["kind"] == "phrase" for a in ans), [a["answer"] for a in ans if a["form"] == "say"])
        self.assertTrue(any(a["answer"]["kind"] == "because" for a in ans))

    def test_the_organs_road_is_read_only_a_planted_write_raises(self) -> None:
        real = R.answer_point

        def planted(org, *a, **k):
            out = real(org, *a, **k)
            org.W[0, 0] += 1.0                    # the planted offender: an answer that writes the organism
            return out

        with mock.patch.object(R, "answer_point", planted):
            with self.assertRaises(RuntimeError) as cm:
                self.run_mind(blind=BLIND)
        self.assertIn("read-only", str(cm.exception))

    def test_status_of_the_twin(self) -> None:
        st = self.m.brain_status()
        self.assertEqual((st["brain"], st["blind"]), (None, True))
        self.assertEqual(st["asks_by"], {"brain": 0, "organs": self.info["asks"]})


# ------------------------------------------------------------------------------------------------ non-interference, the twin, the floor
class TestNonInterference(_Tape, unittest.TestCase):
    def test_the_brain_does_not_disturb_the_organs(self) -> None:
        mb, rb = self.run_mind()
        mo, ro = self.run_mind(blind=BLIND)
        jb = [json.dumps(r) for r in S.journal(rb) if not S.is_brain_row(r)]
        jo = [json.dumps(r) for r in S.journal(ro) if not S.is_brain_row(r)]
        self.assertGreater(len(jb), 100)
        self.assertEqual(jb, jo)
        self.assertEqual(mb.org.state_hash(), mo.org.state_hash())
        self.assertGreater(sum(1 for r in S.journal(rb) if S.is_brain_row(r)), 0)

    def test_no_brain_line_is_the_blind_twin_byte_for_byte(self) -> None:
        mo, ro = self.run_mind(blind=BLIND)
        mt, rt = self.run_mind(brain_line=False)
        self.assertEqual(S.journal_bytes(ro), S.journal_bytes(rt))
        self.assertEqual(mo.org.state_hash(), mt.org.state_hash())

    def test_no_brain_no_ask_changes_nothing(self) -> None:
        """No BRAIN line, no ask row: no answer/brain row, no brain state, no `asks` ledger key, brain_status None (the full
        creature suite pins every older tape and genome byte-identical besides)."""
        train_only = [r for r in self.rows if r["sense"] != "ask"]
        m, root = self.run_mind(brain_line=False, rows=train_only)
        self.assertFalse(any(S.is_brain_row(r) for r in S.journal(root)))
        self.assertIsNone(m.brain)
        self.assertIsNone(m.brain_status())
        self.assertNotIn("asks", json.loads((root / "state" / "ledger.json").read_text()))
        self.assertFalse(list((root / "state").glob("brain*")))

    def test_a_brain_line_whose_organ_cannot_import_refuses_by_name(self) -> None:
        root = S.link_root(self.tape_root, self.tmp / "refuse" / "r")
        gp = S.write_genome(root.parent / "g.genome")

        def gone():
            raise ImportError("No module named 'genome.brain'")

        with mock.patch.object(MM, "_brain_class", gone):
            with self.assertRaises(GenomeError) as cm:
                MM.Mind(gp, root)
        self.assertTrue(str(cm.exception).startswith("BRAIN"), str(cm.exception))
        with mock.patch.object(MM, "_brain_class", gone):
            m = MM.Mind(gp, root, blind=BLIND)       # the twin never needs the organ
            m.close()


# ------------------------------------------------------------------------------------------------ the chain: the lives' readers
class TestReadersCountNoAskRow(_Tape, unittest.TestCase):
    def test_check_counts_and_hours_are_those_of_the_journal_without_the_new_rows(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("lives_check_c", S.ROOT / "tools" / "lives" / "check.py")
        check = importlib.util.module_from_spec(spec); spec.loader.exec_module(check)
        m, root = self.run_mind()
        J = S.journal(root)
        plain = [r for r in J if not S.is_brain_row(r)]
        self.assertLess(len(plain), len(J))
        self.assertEqual(check.journal_counts(J), check.journal_counts(plain))
        self.assertEqual(check.births_by_hour(J), check.births_by_hour(plain))


# ------------------------------------------------------------------------------------------------ replay and resume
class TestReplayAndResume(_Tape, unittest.TestCase):
    def test_a_tape_replayed_twice_is_byte_identical_and_equals_the_live_journal(self) -> None:
        m, live = self.run_mind()
        gp = live.parent / "g.genome"
        outs = []
        with _fake():
            for k in range(2):
                outs.append(_replay(gp, self.info["tape"], self.tmp / f"replay{k}", self.tmp, close=True))
        self.assertEqual(outs[0].read_bytes(), outs[1].read_bytes())
        got = RP.read_mind_journal(outs[0])
        want = [r for r in S.journal(live) if RP.is_mind_row(r)]
        self.assertIsNone(RP.compare(got, want))
        self.assertEqual(sum(1 for r in got if r.get("kind") == "answer"), self.info["asks"])

    def test_blind_brain_replay_equals_the_blind_live(self) -> None:
        m, live = self.run_mind(blind=BLIND)
        with _fake():
            out = _replay(live.parent / "g.genome", self.info["tape"], self.tmp / "replay-blind", self.tmp, blind=BLIND, close=True)
        self.assertIsNone(RP.compare(RP.read_mind_journal(out), [r for r in S.journal(live) if RP.is_mind_row(r)]))

    def test_resumed_from_a_snapshot_between_an_ask_and_its_eye_row(self) -> None:
        """Whole vs stopped (close = the body's stop: a snapshot) right after the sitting's first HELD ask, resumed, continued:
        every answer/brain row identical, the held ask survives the snapshot, the brain's final state_hash equal."""
        whole, rw = self.run_mind()
        cut = next(k for k, r in enumerate(self.rows) if r["sense"] == "ask" and json.loads(
            (self.tape_root / "tape" / r["payload"]).read_text())["form"] == "point")
        first, rr = self.run_mind(rows=self.rows[:cut + 1])
        self.assertEqual(sum(len(v) for v in first.pending_asks.values()), 1)
        with _fake():
            m2, last = MM.Mind.resume(rr.parent / "g.genome", rr)
            try:
                self.assertEqual(last, self.rows[cut]["seq"])
                self.assertTrue(m2.brain_restored)
                self.assertEqual(sum(len(v) for v in m2.pending_asks.values()), 1)
                self.assertEqual(m2.brain.state_hash(), first.brain.state_hash())
                for row in self.rows:
                    if row["seq"] > last:
                        m2.consume(row)
            finally:
                m2.close()
        a = [json.dumps(r) for r in S.journal(rw) if S.is_brain_row(r)]
        b = [json.dumps(r) for r in S.journal(rr) if S.is_brain_row(r)]
        self.assertEqual(a, b)
        self.assertEqual(m2.brain.state_hash(), whole.brain.state_hash())
        self.assertEqual(m2.asks_answered, whole.asks_answered)


class TestReplayDirectory(unittest.TestCase):
    """The seat's addendum 2: run_replay reads ONE day file; a tape crossing 00:00 UTC is handed as its DIRECTORY (additive:
    a file path behaves exactly as before)."""

    def test_a_tape_across_two_days_replays_from_its_directory(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="brain-mind-days-"))
        try:
            tr = tmp / "tape-root"; tr.mkdir()
            info = S.build(tr, n_train=20, per_split=1, t0=datetime(2026, 9, 28, 23, 59, 59, 950000, tzinfo=timezone.utc), one_day=False)
            root = S.link_root(tr, tmp / "live" / "r")
            gp = S.write_genome(root.parent / "g.genome")
            with _fake():
                m = MM.Mind(gp, root)
                try:
                    for row in S.rows(tr):
                        m.consume(row)
                finally:
                    m.close()
                self.assertEqual(len(list((root / "journal").glob("*.jsonl"))), 2)
                out = _replay(gp, tr / "tape", tmp / "replay", tmp, close=True)
                one = _replay(gp, info["days"][0], tmp / "replay-one-day", tmp, close=True)
            want = [r for r in S.journal(root) if RP.is_mind_row(r)]
            self.assertIsNone(RP.compare(RP.read_mind_journal(out), want))
            self.assertIsNotNone(RP.compare(RP.read_mind_journal(one), want), "one day file is not the whole life")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------------------------------------ the REAL Brain (builder A)
@unittest.skipUnless(REAL_BRAIN, "genome/brain.py (builder A's organ) is not on this tree")
class TestEndToEndRealBrain(_Tape, unittest.TestCase):
    def test_every_ask_answered_replay_identical_and_the_organs_undisturbed(self) -> None:
        mb, rb = self.run_mind(fake=False)
        ans = [r for r in S.journal(rb) if r.get("kind") == "answer"]
        self.assertEqual(len(ans), self.info["asks"])
        self.assertEqual({a["by"] for a in ans}, {"brain"})
        for a in ans:
            self.assertIn("raw", a["answer"], a)
        self.assertEqual(sum(1 for r in S.journal(rb) if r.get("act") == "learn"), self.info["n_train"])
        out = _replay(rb.parent / "g.genome", self.info["tape"], self.tmp / "replay-real", self.tmp, close=True)
        self.assertIsNone(RP.compare(RP.read_mind_journal(out), [r for r in S.journal(rb) if RP.is_mind_row(r)]))
        mo, ro = self.run_mind(blind=BLIND, fake=False)
        self.assertEqual([json.dumps(r) for r in S.journal(rb) if not S.is_brain_row(r)],
                         [json.dumps(r) for r in S.journal(ro) if not S.is_brain_row(r)])
        self.assertEqual(mb.org.state_hash(), mo.org.state_hash())

    def test_a_malformed_ask_is_answered_refused_never_a_crash(self) -> None:
        """#230: the organ's BrainError on a malformed ask (a form it does not know) is journaled as a refused answer by name."""
        tmp = self.tmp / "malformed"
        tr = tmp / "tape-root"; tr.mkdir(parents=True)
        from creature.tape import Tape
        tape = Tape(tr)
        row = tape.publish("ask", json.dumps({"form": "sing", "item": "X:1", "mark": "X"}).encode(),
                           {"moment": "scX-sing", "source": "scene", "form": "sing"}, "json", at="2026-09-28T12:00:00.000Z")
        from brain.scene import world as W
        eye = tape.publish("eye", S.png(W.render_scene(W.test_scene(20261401, 0))[0]),
                           {"moment": "scX-sing", "source": "scene", "kind": "sitting", "set": "fresh", "split": "test", "row": 0},
                           "png", at="2026-09-28T12:00:00.001Z")
        row2 = tape.publish("ask", json.dumps({"form": "why", "item": "M4:circle", "mark": "M4", "word": "circle"}).encode(),
                            {"moment": "scX-why", "source": "scene", "form": "why"}, "json", at="2026-09-28T12:00:00.002Z")
        root = S.link_root(tr, tmp / "r")
        gp = S.write_genome(tmp / "g.genome")
        m = MM.Mind(gp, root)
        try:
            for r in (row, eye, row2):
                m.consume(r)
        finally:
            m.close()
        ans = [r for r in S.journal(root) if r.get("kind") == "answer"]
        self.assertEqual([(a["form"], a["answer"]["kind"]) for a in ans], [("sing", "refused"), ("why", "unknown")])
        self.assertIn("sing", ans[0]["answer"]["reason"])
        self.assertEqual(m.pending_asks, {})

    def test_resume_mid_sitting_equals_the_whole_life(self) -> None:
        whole, rw = self.run_mind(fake=False)
        cut = next(k for k, r in enumerate(self.rows) if r["sense"] == "ask" and json.loads(
            (self.tape_root / "tape" / r["payload"]).read_text())["form"] == "point")
        first, rr = self.run_mind(rows=self.rows[:cut + 1], fake=False)
        m2, last = MM.Mind.resume(rr.parent / "g.genome", rr)
        try:
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        self.assertEqual([json.dumps(r) for r in S.journal(rw) if S.is_brain_row(r)],
                         [json.dumps(r) for r in S.journal(rr) if S.is_brain_row(r)])
        self.assertEqual(m2.brain.state_hash(), whole.brain.state_hash())


if __name__ == "__main__":
    unittest.main()
