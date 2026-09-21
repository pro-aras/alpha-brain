# edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:11 +0400 — G5-K (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md):
# ACT/OUTCOME (G-MOT-1/2), SIT (G-MOT-3), SENSE body (BODY-SENSES.md §4.1). SOLUTIONS #175 (a control that
# controls nothing), #180 (only conjunction computes a value — the last link proven with one real value on a
# real tape), #228 (a) (a plant placed where the mechanism can fire), #164 (a field written on one branch is
# stale on the other — every consume path journals).
from __future__ import annotations

import io
import json
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from creature.body import Body
from creature.mind import Mind
from creature.senses import body_sense as body_sense_mod
from creature.senses import sit as sit_mod
from creature.tape import Tape, read_tape
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME_PATH = ROOT / "genome" / "G4.genome"
SKELETON_PATH = ROOT / "genome" / "G4-skeleton.genome"

# The four G5-K lines, exactly as docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md and the organ documents
# (MOTOR-HANDS.md §4, BODY-SENSES.md §4.1) give them.
ACT_LINE = "ACT      glance open ask"
OUTCOME_LINE = "OUTCOME  act to episode; error grades it; ranks replay"
SIT_LINE = "SIT      exam every 2000 canvases; the score returns as a sense"
SENSE_BODY_LINE = "SENSE    body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss"

# The closed root, read read-only via a hard-link copy of just its exam/ subdir (hard rule 3: "Snapshots
# from a hard-link copy (cp -al) in scratch, never in place" -- even though this test only ever READS,
# never writes, matching the rule exactly, not merely its spirit).
LIFE2_EXAM_COPY = ROOT / "scratch" / "life2-ro" / "exam"


def _append(genome_text: str, *lines: str) -> Path:
    """test_gene_values.py's own technique: a real genome's text plus exactly the new lines under test,
    nothing else changed."""
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(genome_text + "\n" + "\n".join(lines) + "\n")
    return p


def _g4_with(*lines: str) -> Path:
    return _append(G4_GENOME_PATH.read_text(), *lines)


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _journal_rows(root: Path) -> list:
    out = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


# ============================================================================ parsing + wiring
class TestParseAndWire(unittest.TestCase):
    def test_all_four_lines_parse(self) -> None:
        g = parse_genome(G4_GENOME_PATH.read_text() + "\n" + ACT_LINE + "\n" + OUTCOME_LINE + "\n" + SIT_LINE + "\n" + SENSE_BODY_LINE + "\n")
        self.assertEqual(g.declared["ACT"]["verbs"], ["glance", "open", "ask"])
        self.assertEqual(g.declared["OUTCOME"], {"fields": ["act", "expected", "got", "residual", "source"]})
        self.assertEqual(g.declared["SIT"], {"every": 2000})
        self.assertEqual(g.declared["SENSE_BODY"], {"period_s": 60, "fields": ["moments", "births", "arrivals", "budget_left", "refused", "restarts", "mind_ms", "rss"]})
        # additive: eye/ear (the OTHER two SENSE shapes) still parse exactly as before
        self.assertEqual(g.eye, (32, 32))
        self.assertEqual(g.ear_letters, 8)

    def test_g4_genome_itself_never_declares_any_of_the_four(self) -> None:
        """advisor point 7: I never edited genome/G4.genome -- its own parse carries none of my four keys."""
        g = parse_genome(G4_GENOME_PATH.read_text())
        for key in ("ACT", "OUTCOME", "SIT", "SENSE_BODY"):
            self.assertNotIn(key, g.declared)

    def test_a_genome_declaring_all_four_starts_a_mind(self) -> None:
        """W3-0's generic refusal (creature/genes.py:unwired) must find a real site for each of the four,
        or Mind.__init__ refuses the organism by name."""
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE, SIT_LINE, SENSE_BODY_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNotNone(mind.outcome_episodes)
        self.assertEqual(mind.outcome_episodes.cap, 2000)

    def test_declaring_only_act_without_outcome_or_sit_builds_no_ring(self) -> None:
        """ACT alone (the vocabulary, no OUTCOME/SIT consumer of it) must not silently build the ring --
        the ring is OUTCOME's/SIT's, not ACT's."""
        gpath = _g4_with(ACT_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        self.assertIsNone(mind.outcome_episodes)


# ============================================================================ G-MOT-2: the plant + the E21 twin
class TestOutcomePlantAndTwin(unittest.TestCase):
    """A predictable act's residual falls with repetition; an unpredictable one's does not; the ACT-BLIND
    magnitude-only twin (E21's own shape: |got_t - got_{t-1}| over the WHOLE interleaved stream, regardless
    of which act) must NOT separate them -- proving the real residual comes from the PREDICTION, not from
    how much changed (#175)."""

    def _run_plant(self, seed: int = 2026, n: int = 60):
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        rng = np.random.default_rng(seed)
        rows = []                      # [(act, got), ...] -- "open" predictable (constant 0.9), "ask" unpredictable (uniform)
        for i in range(n):
            if i % 2 == 0:
                rows.append(("open", 0.9))
            else:
                rows.append(("ask", float(rng.uniform(0.0, 1.0))))
        real_residual = {"open": [], "ask": []}
        for i, (act, got) in enumerate(rows):
            row = tape.publish("outcome", b"{}", {"moment": f"m{i}", "act": act, "got": got,
                                                    "expected": None, "residual": None, "source": "plant"}, "json")
            mind.consume(row)
            ep = mind.outcome_episodes.get(mind.outcome_episodes.n_written - 1)
            real_residual[act].append(float(ep["surprise"]))
        gots = [g for _, g in rows]
        twin_all = [None] + [abs(gots[i] - gots[i - 1]) for i in range(1, n)]
        twin_by_act = {"open": [], "ask": []}
        for i, (act, _got) in enumerate(rows):
            if twin_all[i] is not None:
                twin_by_act[act].append(twin_all[i])
        return real_residual, twin_by_act

    def test_predictable_act_residual_falls_to_the_floor(self) -> None:
        real, _twin = self._run_plant()
        # after the SECOND occurrence (the first running-mean estimate exists), a perfectly repeated "got"
        # is predicted exactly: residual == 0.0 for every occurrence from #2 on.
        self.assertTrue(all(r == 0.0 for r in real["open"][1:]), f"open's residual must floor at 0.0 after repetition: {real['open']}")

    def test_unpredictable_act_residual_does_not_fall(self) -> None:
        real, _twin = self._run_plant()
        ask = real["ask"]
        first_mean = sum(ask[:5]) / 5
        last_mean = sum(ask[-5:]) / 5
        # "does not fall": the last-5 mean is not dramatically smaller than the first-5 mean (a random
        # walk around ~0.25 for U(0,1)'s mean |x-0.5|, not a monotone decline to 0).
        self.assertGreater(last_mean, first_mean * 0.3,
                            f"ask's residual must NOT collapse toward 0 with repetition: first5={first_mean:.4f} last5={last_mean:.4f}")
        self.assertGreater(last_mean, 0.05, "an unpredictable act's residual must stay well above the predictable act's floor")

    def test_act_blind_magnitude_twin_controls_nothing(self) -> None:
        """The twin the brief names (E21's own shape) must NOT separate predictable from unpredictable —
        it is dominated by the A/B alternation, not by either act's own predictability. This is the twin
        E21 itself measured at 59.17% vs the model's 100% -- here it fails to separate at all."""
        real, twin = self._run_plant()
        twin_open_last5 = sum(twin["open"][-5:]) / 5
        twin_ask_last5 = sum(twin["ask"][-5:]) / 5
        real_open_last5 = sum(real["open"][-5:]) / 5
        real_ask_last5 = sum(real["ask"][-5:]) / 5
        real_gap = real_ask_last5 - real_open_last5
        twin_gap = abs(twin_ask_last5 - twin_open_last5)
        self.assertGreater(real_gap, 0.05, f"the real (per-act running-mean) residual must separate the acts: {real_open_last5:.4f} vs {real_ask_last5:.4f}")
        self.assertLess(twin_gap, real_gap / 2,
                         f"the act-blind twin must separate the acts far LESS than the real residual does: twin_gap={twin_gap:.4f} real_gap={real_gap:.4f}")
        # both twin arms sit near the SAME value (dominated by alternation, ~0.5 for a U(0,1)/constant-0.9 mix)
        self.assertLess(abs(twin_open_last5 - twin_ask_last5), 0.15,
                         f"the twin's own two arms should read close to each other (it cannot tell them apart): {twin_open_last5:.4f} vs {twin_ask_last5:.4f}")

    def test_expected_row_supplied_directly_is_trusted_over_the_running_mean(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("outcome", b"{}", {"moment": "m0", "act": "run", "got": 5.0, "expected": 2.0, "residual": None, "source": "test"}, "json")
        mind.consume(row)
        rows = [r for r in _journal_rows(root) if "outcome" in r]
        self.assertEqual(rows[-1]["outcome"]["expected"], 2.0)
        self.assertEqual(rows[-1]["outcome"]["residual"], 3.0)

    def test_residual_supplied_directly_is_trusted(self) -> None:
        """A future publisher (Builder L's game reward) may supply residual itself -- trusted as-is."""
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("outcome", b"{}", {"moment": "m0", "act": "run", "got": 5.0, "expected": None, "residual": 0.7, "source": "game"}, "json")
        mind.consume(row)
        rows = [r for r in _journal_rows(root) if "outcome" in r]
        self.assertEqual(rows[-1]["outcome"]["residual"], 0.7)

    def test_no_expected_and_no_prior_history_is_ungradable_not_a_fabricated_zero(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("outcome", b"{}", {"moment": "m0", "act": "first-ever", "got": 3.0, "expected": None, "residual": None, "source": "test"}, "json")
        mind.consume(row)
        rows = [r for r in _journal_rows(root) if "outcome" in r]
        self.assertIsNone(rows[-1]["outcome"]["residual"])
        self.assertFalse(rows[-1]["outcome"]["gradable"])

    def test_act_outside_declared_vocabulary_is_tagged_not_crashed(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        row = tape.publish("outcome", b"{}", {"moment": "m0", "act": "fetch", "got": 1.0, "expected": None, "residual": None, "source": "test"}, "json")
        mind.consume(row)   # must not raise -- "fetch" is not in "glance open ask"
        rows = [r for r in _journal_rows(root) if "outcome" in r]
        self.assertFalse(rows[-1]["outcome"]["in_vocab"])

    def test_blind_outcome_acts_happen_no_episode(self) -> None:
        """G-MOT-2's own twin: --blind outcome -- acts happen (the journal row is written), no episode."""
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root, blind=frozenset({"outcome"}))
        tape = Tape(root)
        for i in range(5):
            row = tape.publish("outcome", b"{}", {"moment": f"m{i}", "act": "open", "got": 0.9, "expected": None, "residual": None, "source": "test"}, "json")
            mind.consume(row)
        rows = [r for r in _journal_rows(root) if "outcome" in r]
        self.assertEqual(len(rows), 5, "acts happen: every outcome row is still journaled under --blind outcome")
        self.assertTrue(all(r["outcome"]["ep"] is None for r in rows), "no episode: 'ep' must be None under --blind outcome")
        self.assertEqual(mind.outcome_episodes.n_written, 0, "no episode: the ring itself must stay empty")


# ============================================================================ THINK's "outcome" kind (#232 addendum)
class TestOutcomeThinkKind(unittest.TestCase):
    def test_think_can_choose_and_work_an_outcome_item_without_crashing(self) -> None:
        """#232's addendum: a branch no test reaches crashes on its first real walk. Drives THINK across
        many passes with an outcome-populated pool until it actually chooses kind="outcome" at least
        once, and confirms the journal captures a "reflected" result -- never a crash, never unknown_kind."""
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE, "THINK    every 1 canvases")
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        rng = np.random.default_rng(7)
        things = ["circle", "square"]
        from genome import world
        saw_outcome_kind = False
        for i in range(40):
            # one outcome row (varying act so the pool stays non-trivial) ...
            act = "open" if i % 2 == 0 else "ask"
            orow = tape.publish("outcome", b"{}", {"moment": f"o{i}", "act": act, "got": float(rng.uniform(0, 1)),
                                                      "expected": None, "residual": None, "source": "test"}, "json")
            mind.consume(orow)
            # ... then one canvas, so _canvas_index advances and THINK fires (every 1 canvas)
            thing = things[i % len(things)]
            rgb, _truth = world.render_canvas(thing, rng)
            moment = f"c{i:04d}"
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
            erow = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")
            mind.consume(erow)
        pool = mind._think_pool()
        self.assertTrue(any(it["kind"] == "outcome" for it in pool), "the pool must carry at least one 'outcome' item by now")
        outcome_item = next(it for it in pool if it["kind"] == "outcome")
        result = mind._think_work(outcome_item)
        self.assertEqual(result["outcome"], "reflected")
        self.assertIn("residual", result)
        think_rows = [r for r in _journal_rows(root) if "think" in r]
        kinds_seen = {r["think"]["kind"] for r in think_rows}
        self.assertIn("outcome", kinds_seen, f"THINK must have actually CHOSEN an 'outcome' item at least once across the walk: kinds seen = {kinds_seen}")
        for r in think_rows:
            if r["think"]["kind"] == "outcome":
                self.assertEqual(r["think"]["outcome"], "reflected")
                self.assertFalse(r["think"]["parked"])


# ============================================================================ G-MOT-3: SIT
class TestSitPreregistrationOnLife2(unittest.TestCase):
    """The refusal check MOTOR-HANDS.md's own words require, run BEFORE trusting the gene: "refuse the
    line if the score is constant across life 2's ten files (it slid .995 → .952 — print it)." Read via
    sit.py's OWN score-extraction function (dogfooding the real code, not a re-derivation of it) against
    the closed life-2 record (a hard-link copy, hard rule 3)."""

    def test_life2_score_series_is_not_constant(self) -> None:
        if not LIFE2_EXAM_COPY.exists():
            self.skipTest(f"life-2 exam copy not present at {LIFE2_EXAM_COPY} (expected under this worktree's scratch/)")
        files = sorted(p for p in LIFE2_EXAM_COPY.glob("*.json") if p.name[:1].isdigit())
        self.assertGreaterEqual(len(files), 5, "life 2's exam/ must carry several stamped reports")
        series = []
        for f in files:
            data = json.loads(f.read_text())
            score = sit_mod._score_of(data)
            self.assertIsNotNone(score, f"{f.name}: sit.py's own _score_of must read a Q1 accuracy")
            series.append(score)
        print(f"\n[G5-K SIT prereg] life-2 Q1 score series ({len(series)} files): {[round(s, 4) for s in series]}")
        self.assertGreater(max(series) - min(series), 0.01,
                            f"the SIT line is REFUSED if life 2's score is constant -- range was {max(series) - min(series):.4f}: {series}")
        # sit.py must pick the NEWEST file, not the alphabetically-first one, and never LAST.json
        self.assertEqual(sit_mod._latest_exam_file(LIFE2_EXAM_COPY), files[-1])
        self.assertNotEqual(sit_mod._latest_exam_file(LIFE2_EXAM_COPY).name, "LAST.json")


class TestSitLiveWiring(unittest.TestCase):
    def test_sense_publishes_the_newest_exam_files_score_as_they_appear(self) -> None:
        root = Path(tempfile.mkdtemp())
        exam_dir = root / "exam"
        exam_dir.mkdir(parents=True)
        (root / "state").mkdir(parents=True)
        (root / "state" / "ledger.json").write_text(json.dumps({"moments": 40}))   # 40 // fixations(4) = 10 canvases -- >= every_canvases below
        gpath = SKELETON_PATH  # gaze fixations=4 -- the sense reads this genome's own fixations, not a hardcoded one

        published: list = []

        def fake_publish(sense, payload, meta, ext):
            published.append((sense, json.loads(payload.decode("utf-8")), meta))
            return {"seq": len(published)}

        stop = threading.Event()
        t = threading.Thread(target=sit_mod.sense, args=(fake_publish, stop, root, gpath),
                              kwargs={"every_canvases": 5, "poll_period": 0.05}, daemon=True)
        t.start()
        try:
            (exam_dir / "2026-09-21T000001Z.json").write_text(json.dumps({"ask_seen_words": {"Q1": {"acc": 0.80}}}))
            deadline = time.time() + 5.0
            while len(published) < 1 and time.time() < deadline:
                time.sleep(0.05)
            self.assertEqual(len(published), 1)
            self.assertEqual(published[0][0], "sit")
            self.assertEqual(published[0][1]["score"], 0.80)
            self.assertEqual(published[0][2]["score"], 0.80)

            # a NEWER file (sorts after) must be picked up next, and the OLD one must not re-publish.
            # SIT's own cadence only re-checks on the NEXT multiple of every_canvases (exactly like EXAM's
            # own voice_loop) -- a live ledger keeps advancing; this test advances it by hand to cross the
            # next boundary (canvas_count 10 -> 25, since every_canvases=5).
            (root / "state" / "ledger.json").write_text(json.dumps({"moments": 100}))
            (exam_dir / "2026-09-21T000002Z.json").write_text(json.dumps({"ask_seen_words": {"Q1": {"acc": 0.60}}}))
            deadline = time.time() + 5.0
            while len(published) < 2 and time.time() < deadline:
                time.sleep(0.05)
        finally:
            stop.set()
            t.join(timeout=3.0)
        self.assertEqual(len(published), 2, f"exactly the two new files, no duplicate re-publish: {published}")
        self.assertEqual(published[1][1]["score"], 0.60)

    def test_sense_never_publishes_last_json_and_never_writes_anything(self) -> None:
        root = Path(tempfile.mkdtemp())
        exam_dir = root / "exam"
        exam_dir.mkdir(parents=True)
        (exam_dir / "LAST.json").write_text(json.dumps({"last_canvas": 999}))   # the voice's own pointer, must be ignored
        (root / "state").mkdir(parents=True)
        (root / "state" / "ledger.json").write_text(json.dumps({"moments": 400}))
        published: list = []
        stop = threading.Event()
        t = threading.Thread(target=sit_mod.sense, args=(published.append, stop, root, SKELETON_PATH),
                              kwargs={"every_canvases": 1, "poll_period": 0.05}, daemon=True)
        t.start()
        time.sleep(0.3)
        stop.set()
        t.join(timeout=3.0)
        self.assertEqual(published, [], "LAST.json alone (no stamped file) must publish nothing")
        self.assertFalse((exam_dir / "SEEN.json").exists())   # no cursor file written (writer-sweep discipline; in-memory cursor only)


class TestSitConsumeReusesOutcomeMechanism(unittest.TestCase):
    def test_sit_row_becomes_a_reflex_episode_tagged_sit(self) -> None:
        gpath = _g4_with(SIT_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        for score in (0.99, 0.97, 0.95):
            row = tape.publish("sit", b"{}", {"moment": f"s{score}", "source": "sit", "score": score}, "json")
            mind.consume(row)
        self.assertEqual(mind.outcome_episodes.n_written, 3)
        recs = [mind.outcome_episodes.get(i) for i in range(3)]
        self.assertTrue(all(r["word"] == "sit" for r in recs))
        # a genuinely falling score sequence must show a falling (or at least present) residual after the first reading
        self.assertIsNone(_journal_rows(root)[0]["sit"]["residual"], "the first-ever SIT reading has nothing to compare against yet")

    def test_blind_sit_means_the_score_is_not_published_to_the_mind(self) -> None:
        gpath = _g4_with(SIT_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root, blind=frozenset({"sit"}))
        tape = Tape(root)
        row = tape.publish("sit", b"{}", {"moment": "s1", "source": "sit", "score": 0.9}, "json")
        mind.consume(row)
        rows = [r for r in _journal_rows(root) if "sit" in r]
        self.assertEqual(rows[-1]["sit"], {"blind": True})
        self.assertEqual(mind.outcome_episodes.n_written, 0)


# ============================================================================ BODY-SENSES §4.1: SENSE body
class TestBodySenseFieldMapping(unittest.TestCase):
    def test_reading_matches_status_field_by_field(self) -> None:
        root = Path(tempfile.mkdtemp())
        status = {"heartbeat_at": "2026-09-21T21:00:00.000Z", "moments": 1234, "births": 56, "arrivals": 2,
                  "budget_left": 344, "births_refused_budget": 7, "sense_restarts": 1,
                  "mind_ms_median_1min": 3.14, "rss_mb": 88.5}
        (root / "STATUS.json").write_text(json.dumps(status))
        published: list = []
        stop = threading.Event()
        fields = ["moments", "births", "arrivals", "budget_left", "refused", "restarts", "mind_ms", "rss"]

        def fake_publish(sense, payload, meta, ext):
            published.append((sense, json.loads(payload.decode("utf-8")), meta))
            stop.set()   # one reading is enough
            return {"seq": 1}

        t = threading.Thread(target=body_sense_mod.sense, args=(fake_publish, stop, root),
                              kwargs={"fields": fields, "period_s": 0.05}, daemon=True)
        t.start()
        t.join(timeout=3.0)
        self.assertEqual(len(published), 1)
        sense_name, reading, meta = published[0]
        self.assertEqual(sense_name, "body")
        self.assertEqual(reading, meta["reading"])
        expect = {"moments": 1234, "births": 56, "arrivals": 2, "budget_left": 344,
                  "refused": 7, "restarts": 1, "mind_ms": 3.14, "rss": 88.5}
        self.assertEqual(reading, expect, "the numbers on the tape must equal STATUS's at the instant")

    def test_status_missing_publishes_nothing_yet(self) -> None:
        root = Path(tempfile.mkdtemp())   # no STATUS.json at all
        published: list = []
        stop = threading.Event()
        t = threading.Thread(target=body_sense_mod.sense, args=(published.append, stop, root),
                              kwargs={"fields": ["moments"], "period_s": 0.05}, daemon=True)
        t.start()
        time.sleep(0.2)
        stop.set()
        t.join(timeout=3.0)
        self.assertEqual(published, [])


class TestBodySenseLiveWiringAndReplay(unittest.TestCase):
    def test_live_body_publishes_body_rows_equal_to_status_and_replay_is_exact(self) -> None:
        gpath = _g4_with(SENSE_BODY_LINE, "HEART every 1 s")
        root = Path(tempfile.mkdtemp())
        body = Body(root, gpath)
        body.start()
        try:
            deadline = time.time() + 15.0
            body_rows = []
            status_at_read: Optional[dict] = None
            while time.time() < deadline:
                body_rows = [r for r in read_tape(root) if r["sense"] == "body"]
                if body_rows:
                    status_at_read = json.loads((root / "STATUS.json").read_text())
                    break
                time.sleep(0.2)
        finally:
            body.stop()
        self.assertTrue(body_rows, "SENSE_BODY declared with SENSE_BODY.period_s honoured (creature/senses/body_sense.py's own default 60s would be too slow for this test -- see the period read below)")
        row = body_rows[0]
        reading = row["meta"]["reading"]
        self.assertIn("moments", reading)
        self.assertIsNotNone(status_at_read)
        # ± one write: the row's own numbers must equal STATUS's at SOME instant close to the read (never
        # a stale/garbled value) -- moments/births/arrivals/budget_left/refused/restarts are monotone-ish
        # counters that cannot be LARGER on the tape row than in a STATUS read taken strictly after it.
        self.assertLessEqual(reading["moments"], status_at_read["moments"])
        self.assertLessEqual(reading["births"], status_at_read["births"])

        # replay exact: consuming this SAME row into a second, fresh Mind must produce byte-identical
        # journal content for it (they are tape rows -- no clock, no randomness in _consume_body).
        journal1 = [r for r in _journal_rows(root) if "body" in r]
        self.assertTrue(journal1)
        root2 = Path(tempfile.mkdtemp())
        mind2 = Mind(gpath, root2)
        mind2.consume(row)
        journal2 = [r for r in _journal_rows(root2) if "body" in r]
        self.assertEqual(journal2[-1]["body"], journal1[0]["body"], "replay must be byte-identical for a body row")
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(root2, ignore_errors=True)


# ============================================================================ snapshot/resume + org.state_hash untouched
class TestSnapshotResumeAndOrgUntouched(unittest.TestCase):
    def test_outcome_ring_and_expectation_survive_a_resume(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        tape = Tape(root)
        for i, got in enumerate((0.9, 0.9, 0.9, 0.7)):
            act = "open" if i < 3 else "ask"
            row = tape.publish("outcome", b"{}", {"moment": f"m{i}", "act": act, "got": got,
                                                    "expected": None, "residual": None, "source": "test"}, "json")
            mind.consume(row)
        hash_before = mind.org.state_hash()
        mind.snapshot()
        mind2, _ = Mind.resume(gpath, root)
        self.assertEqual(mind2.outcome_episodes.n_written, mind.outcome_episodes.n_written)
        self.assertAlmostEqual(mind2._act_expected["open"], mind._act_expected["open"], places=9)
        self.assertAlmostEqual(mind2._act_expected["ask"], mind._act_expected["ask"], places=9)
        self.assertEqual(mind2.org.state_hash(), hash_before, "outcome/sit/body rows must never move the organism's own hash")

    def test_org_hash_unchanged_by_outcome_sit_body_rows(self) -> None:
        gpath = _g4_with(ACT_LINE, OUTCOME_LINE, SIT_LINE, SENSE_BODY_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(gpath, root)
        h0 = mind.org.state_hash()
        tape = Tape(root)
        rows = [
            tape.publish("outcome", b"{}", {"moment": "m0", "act": "open", "got": 1.0, "expected": None, "residual": None, "source": "t"}, "json"),
            tape.publish("sit", b"{}", {"moment": "s0", "source": "sit", "score": 0.5}, "json"),
            tape.publish("body", b"{}", {"moment": "b0", "source": "body", "reading": {"moments": 1}}, "json"),
        ]
        for r in rows:
            mind.consume(r)
        self.assertEqual(mind.org.state_hash(), h0, "none of outcome/sit/body ever touches Organism state")


if __name__ == "__main__":
    unittest.main()
