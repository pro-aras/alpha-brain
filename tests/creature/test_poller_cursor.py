# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:52 +0400 — POLLER-FIX (docs/organism/days/PREREG-POLLER-FIX.md, signed x3): the tests of the one-key manifest cursor, written FIRST.
"""tests/creature/test_poller_cursor.py — the two five-second pollers (creature/exam.py voice_loop, creature/senses/sit.py sense) read the
mind's canvas count from the snapshot MANIFEST's own cursor (`SNAPSHOT.json["canvas_index"]`) instead of parsing the whole ledger.

What is pinned here, by the law's gates:
  G3  the REAL loops against the OLD loops, byte-pinned by the sha256 of their source (a reference someone edits is caught by its own pin),
      on scripted sequences with no sleeps and no threads (a stop event whose wait() advances the script). The traces (every fire / publish
      with its poll index and canvas count) are EQUAL in every scenario but S2, where the manifest and the ledger DIVERGE on purpose: that one
      difference is the proof the snapshot road is the road taken (the ablated system reads the same number and would pass without the fix).
  G5  the writer (a real Mind.snapshot() of a tiny mind) and the reader (`canvas_count_now`) have a NAMED catching test per mutant: MUTANT_TESTS
      is the mapping, committed BEFORE the sweep (docs/organism/days/poller/records/mutate_poller.py) runs it on a clean copy.
  G1  the readers are OFF the replay's road: a real small replay completes with voice_loop, sense and canvas_count_now patched to RAISE, and its
      work root carries a SNAPSHOT.json whose canvas_index equals the ledger's (NOT VACUOUS: an ON replay that ignored the change would carry no key).
A comment is a claim, a count is a fact (#168): every «0 reads» below is printed beside the manifest reads that prove the instrument saw.
"""
from __future__ import annotations

import contextlib
import functools
import hashlib
import inspect
import io
import json
import os
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from creature import exam as exam_module
from creature.mind import Mind
from creature.replay import run_replay
from creature.senses import sit as sit_module
from creature.tape import read_tape
from genome.machinery import parse_genome
from tests.creature import test_surprise_coarse as _tc      # helpers only (a module attribute is not a TestCase: nothing runs twice)

TREE = Path(__file__).resolve().parents[2]
SKELETON = TREE / "genome" / "G4-skeleton.genome"             # GAZE fixations=4: the unit of the ledger road's `moments // fixations`
COARSE_GENOME = TREE / "tests" / "creature" / "G5-surprise-coarse-test.genome"
FIXATIONS = 4
EVERY = 500
POLL = 5.0

# ---------------------------------------------------------------------------------------------------------------------------------------------
# THE REFERENCE: the two OLD loops, verbatim from master 233a4cb (ast.get_source_segment of the function node; records/reference_check.py repeats
# the extraction from git and compares). They are exec'd into a copy of the real module's namespace, so every helper they call is the real one.
OLD_VOICE_LOOP_SRC = r'''def voice_loop(root: Path, genome_path: Path, stop_event, every_canvases: int, poll_period: float = 5.0) -> None:
    """The voice's own exam cadence: every `every_canvases` canvases, read from the latest snapshot's
    own "moments" (state/ledger.json) divided by the genome's fixations-per-canvas -- never a counter the
    mind hands over live (the voice never touches the mind's objects, PREREG §2.7's own law, unbroken
    here). A cursor (run/exam/LAST.json) survives a restart so a re-armed voice does not immediately
    re-run the exam it already ran just before a crash."""
    root = Path(root)
    last_path = root / "exam" / "LAST.json"
    last_path.parent.mkdir(parents=True, exist_ok=True)
    last_canvas = 0
    if last_path.exists():
        try:
            last_canvas = int(json.loads(last_path.read_text()).get("last_canvas", 0))
        except (json.JSONDecodeError, OSError):
            last_canvas = 0
    from genome.machinery import parse_genome
    genome = parse_genome(Path(genome_path).read_text())
    fixations = int(genome.gaze["fixations"]) if genome.gaze else 1
    while not stop_event.is_set():
        ledger_path = root / "state" / "ledger.json"
        if ledger_path.exists():
            try:
                ledger = json.loads(ledger_path.read_text())
            except (json.JSONDecodeError, OSError):
                ledger = {}
            canvas_count = canvas_count_of(ledger, fixations)   # M4: the mind's own count when the ledger carries it
            if every_canvases > 0 and canvas_count - last_canvas >= every_canvases:
                last_canvas = canvas_count
                # edit: Claude (Fable 5.1), 2026-09-23 16:58 +0400 — SIT-ATOMIC-SWEEP-0923 FIX 1: the pointer is written atomically too (tmp + os.replace,
                # the same pattern as the report in tools/self_exam.py) — the only other writer under root/exam/. Its one reader is this loop's
                # own restart read above (a torn read there fell back to 0 and re-sat at once), so this is consistency, not a live defect.
                tmp = last_path.with_name(last_path.name + ".tmp")
                tmp.write_text(json.dumps({"last_canvas": last_canvas}))
                os.replace(str(tmp), str(last_path))
                run_and_journal(root, genome_for_sitting(root, genome_path))   # the adopted genome, if any (the J × exam seam)
        stop_event.wait(poll_period)'''
OLD_SENSE_SRC = r'''def sense(publish: Callable, stop_event, root: Path, genome_path: Path, every_canvases: int, poll_period: float = 5.0) -> None:
    """Mirrors `creature/exam.py`'s own `voice_loop` cadence (state/ledger.json's "moments" divided by the
    genome's fixations-per-canvas) so SIT's own `every` value is a real, read parameter — never a fixed
    wall-clock poll pretending to honour it. `every_canvases <= 0` never checks (the same convention
    `_maybe_think` uses for THINK.every)."""
    root = Path(root)
    exam_dir = root / "exam"
    last_canvas = 0
    last_published_name: Optional[str] = None
    torn_name: Optional[str] = None      # the file the last failed read was of, and how many consecutive polls it has failed (FIX 1)
    torn_count = 0
    from genome.machinery import parse_genome
    from creature.exam import canvas_count_of   # M4 (edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400): the ONE canvas unit, shared with voice_loop
    genome = parse_genome(Path(genome_path).read_text())
    fixations = int(genome.gaze["fixations"]) if genome.gaze else 1

    while not stop_event.is_set():
        ledger_path = root / "state" / "ledger.json"
        if ledger_path.exists() and every_canvases > 0:
            try:
                ledger = json.loads(ledger_path.read_text())
            except (json.JSONDecodeError, OSError):
                ledger = {}
            canvas_count = canvas_count_of(ledger, fixations)   # M4: the mind's own count when the ledger carries it, else moments // fixations
            if canvas_count - last_canvas >= every_canvases:
                # edit: Claude (Fable 5.1), 2026-09-23 03:25 +0400 — the boundary is CONSUMED only when a NEW exam file is seen (below); before this
                # line advanced `last_canvas` first, so a boundary crossed a few seconds before the voice thread had
                # written its report was spent on nothing and that exam's SIT row waited for the NEXT boundary (500
                # canvases; at the last one, forever) — #237 (e)'s race, in the sense, not only in its test (the
                # live-wiring test failed 2 of 3 runs ALONE at load 20 on the merged bytes).
                latest = _latest_exam_file(exam_dir)
                if latest is not None and latest.name != last_published_name:
                    # edit: Claude (Fable 5.1), 2026-09-23 16:58 +0400 — SIT-ATOMIC-SWEEP-0923 FIX 1 (docs/briefs/SEAM5-WITNESS-SOUND-REPORT.md item 2):
                    # the boundary is spent ONLY by a read that parses (or by giving a file up, below). Before, `last_canvas = canvas_count`
                    # ran HERE, before the read, so a torn read (the empty file between the voice's create and its write; a partial write)
                    # closed the gate with nothing published and the file waited for the NEXT boundary — 500 canvases on; at a life's last
                    # boundary, forever. The comment beside the except said "try again next one"; the cursor above it made that false
                    # (tests.creature.test_g5k_outcome.TestSitLiveWiring.test_a_... read 0 published on those bytes). Now a transient failure
                    # leaves BOTH cursors untouched, so the very next poll retries the SAME file; a file that fails MAX_TORN_RETRIES
                    # consecutive polls is malformed for good — both cursors advance past it, once, with a printed note (a sense has no
                    # journal channel, and must not publish a row it did not read).
                    try:
                        data = json.loads(latest.read_text())
                    except (json.JSONDecodeError, OSError):
                        data = None      # a torn/partial exam file mid-write (#47/#186): cursors untouched, this file is re-read next poll
                    if data is None:
                        torn_count = torn_count + 1 if torn_name == latest.name else 1
                        torn_name = latest.name
                        if torn_count >= MAX_TORN_RETRIES:
                            print(f"sit: gave up on {latest.name} after {MAX_TORN_RETRIES} unreadable polls (malformed exam report; never re-read)")
                            last_canvas = canvas_count
                            last_published_name = latest.name
                            torn_name, torn_count = None, 0
                    else:
                        torn_name, torn_count = None, 0
                        score = _score_of(data)
                        if score is not None:
                            composite = _composite_of(data)   # ALPHA4-PREREG §4(c): additive, alongside score (None on an exam report that carries no "composite" field)
                            payload = json.dumps({"score": score, "exam_file": latest.name, "composite": composite, "read_share": _read_share_of(data)}).encode("utf-8")
                            publish("sit", payload, {"moment": f"sit{latest.stem}", "source": "sit",
                                                      "exam_file": latest.name, "score": score, "composite": composite, "read_share": _read_share_of(data)}, "json")
                        last_canvas = canvas_count           # both cursors advance together, AFTER the row is durable (#230) — even if score was
                        last_published_name = latest.name    # None (a report that parses but carries no Q1 is not re-tried forever, as before)
        stop_event.wait(poll_period)'''
OLD_VOICE_LOOP_SHA256 = "53dbfb79d3828967d102d327104b573ae9f8cf74054771808f64ddfc1d4a4a0a"
OLD_SENSE_SHA256 = "95bc062bab85fcc6017ed8daed46bd69a69b152067108410f06ea35c95c27f43"

# G5: every mutant of the law, the test that must CATCH it. The sweep runs ONLY the named test on the mutated copy and demands it FAILS (and
# demands it PASSES on the unmutated copy). The letter-suffixed mutants split a two-sided law mutant into its sides, each with its own catcher.
MUTANT_TESTS = {
    "m1": "TestWriter.test_manifest_carries_the_ledgers_canvas_index",        # the writer omits the key
    "m2": "TestWriter.test_manifest_carries_the_ledgers_canvas_index",        # the writer writes self.org.t (moments, not canvases)
    "m3": "TestWriter.test_manifest_carries_the_ledgers_canvas_index",        # the writer writes str(canvas_index)
    "m4": "TestReaderRoads.test_the_snapshot_road_reads_the_manifest_key",   # the reader ignores the key
    "m5": "TestReaderRoads.test_a_keyless_manifest_never_stands_in_t_over_fixations",   # the reader takes t // fixations when the key is absent
    "m6": "TestReaderRoads.test_a_key_that_is_not_a_count_takes_the_ledger_road",       # the reader accepts a bool
    "m7": "TestReaderRoads.test_an_unreadable_manifest_takes_the_ledger_road",          # an unparsable manifest yields 0 instead of the ledger road
    "m8": "TestReaderRoads.test_a_keyless_manifest_takes_the_ledger_road",              # the ledger road only when the manifest is MISSING
    "m9": "TestReaderRoads.test_the_snapshot_road_never_opens_the_ledger",              # the snapshot road still parses the ledger
    "m10": "TestLoopEquivalence.test_s1_voice_loop_manifest_and_ledger_agree",          # voice_loop still calls json.loads(ledger)
    "m11": "TestLoopEquivalence.test_s1_sit_sense_manifest_and_ledger_agree",           # sense still calls json.loads(ledger)
    "m12": "TestLoopEquivalence.test_s1_voice_loop_manifest_and_ledger_agree",          # voice_loop passes `root` for `root/state`
    "m12b": "TestLoopEquivalence.test_s1_sit_sense_manifest_and_ledger_agree",          # sense passes `root` for `root/state`
    "m13": "TestReaderRoads.test_the_manifest_is_read_afresh_every_call",               # the manifest read is cached (stale forever)
    "m14": "TestReaderRoads.test_the_snapshot_road_reads_the_manifest_key",             # the reader is off by one
    "m14w": "TestWriter.test_manifest_carries_the_ledgers_canvas_index",                # the writer is off by one
    "m15": "TestReaderRoads.test_a_torn_ledger_is_zero_not_a_crash",                    # a torn ledger on the ledger road raises instead of {}
    # edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:57 +0400 — three mutants BEYOND the law's list (the author's own, added after the first sweep read 17 of 17; each has an existing catcher):
    "m16": "TestLoopEquivalence.test_s12_a_non_positive_period_never_fires_and_sit_never_polls",   # sense's every <= 0 guard dropped (SIT would poll a disabled duty)
    "m17": "TestReaderRoads.test_a_keyless_manifest_takes_the_ledger_road",             # the ledger road ignores fixations (moments // 1)
    "m18": "TestReaderRoads.test_the_snapshot_road_reads_the_manifest_key",             # a zero cursor is read as falsy: a young mind's first snapshot falls to the ledger
}


def _old_voice_loop(run_and_journal):
    ns = dict(vars(exam_module))
    ns["run_and_journal"] = run_and_journal
    exec(compile(OLD_VOICE_LOOP_SRC, "<voice_loop@233a4cb>", "exec"), ns)
    return ns["voice_loop"]


def _old_sense():
    ns = dict(vars(sit_module))
    exec(compile(OLD_SENSE_SRC, "<sense@233a4cb>", "exec"), ns)
    return ns["sense"]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# THE INSTRUMENTS
class ReadCounter:
    """Counts the opens of the two files the readers choose between, by basename — an attempt on a missing file included (the open is the cost
    and the choice). io.open AND builtins.open are wrapped: pathlib's read_text/read_bytes/open go through io.open, a bare open() through builtins
    (probed: 3 reads of one file read 3, an exists() reads 0, an attempt on a missing file reads 1). READ-mode opens only: the first RED run counted the
    fixture's own write_text of the two files and read (10, 3) where (7, 0) was meant. A read of the ledger by ANY road is counted."""
    WATCH = ("ledger.json", "SNAPSHOT.json")

    def __init__(self) -> None:
        self.n: Counter = Counter()

    def __enter__(self) -> "ReadCounter":
        real, n, watch = io.open, self.n, self.WATCH

        def counting_open(file, mode="r", *a, **k):
            if not isinstance(file, int) and "r" in mode and not any(c in mode for c in "wax+"):     # READS only: the fixture's own writes are not the loops' cost
                name = os.path.basename(os.fspath(file))
                if name in watch:
                    n[name] += 1
            return real(file, mode, *a, **k)
        self._patches = [mock.patch("io.open", counting_open), mock.patch("builtins.open", counting_open)]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc) -> None:
        for p in reversed(self._patches):
            p.stop()

    @property
    def ledger(self) -> int:
        return self.n["ledger.json"]

    @property
    def manifest(self) -> int:
        return self.n["SNAPSHOT.json"]


class ScriptedStop:
    """The loops' stop event. The loops call is_set() at the top of each iteration and wait(poll_period) at its end; here wait() number i runs
    steps[i] (the world changes between two polls) and the loop ends after len(steps) + 1 polls. `waits` is therefore the poll index."""

    def __init__(self, steps) -> None:
        self.steps, self.waits, self.timeouts = list(steps), 0, []

    def is_set(self) -> bool:
        return self.waits > len(self.steps)

    def wait(self, timeout=None) -> bool:
        self.timeouts.append(timeout)
        if self.waits < len(self.steps):
            self.steps[self.waits]()
        self.waits += 1
        return self.is_set()


EXAM_A, EXAM_B, EXAM_C = "2026-10-03T000001Z.json", "2026-10-03T000002Z.json", "2026-10-03T000003Z.json"
EXAM_BODY = json.dumps({"ask_seen_words": {"Q1": {"acc": 0.80}}})


class Fx:
    """A life's root as the pollers see it: root/state (ledger.json, SNAPSHOT.json), root/exam, nothing else."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="pollercursor-"))
        self.state, self.exam = self.root / "state", self.root / "exam"

    def ledger(self, canvas=None, moments=None, raw=None) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            (self.state / "ledger.json").write_text(raw)
            return
        d = {"last_seq": 0, "moments": canvas * 5 if moments is None else moments}
        if canvas is not None:
            d["canvas_index"] = canvas
        (self.state / "ledger.json").write_text(json.dumps(d))

    def manifest(self, canvas="ABSENT", t=None, raw=None) -> None:
        """The manifest as snapshot() writes it: t, last_seq, files, prints — and, in the NEW format, canvas_index (canvas="ABSENT" = an OLD-format life)."""
        self.state.mkdir(parents=True, exist_ok=True)
        if raw is not None:
            (self.state / "SNAPSHOT.json").write_bytes(raw)
            return
        d = {"t": 0 if t is None else t, "last_seq": 0, "files": ["ledger.json"], "prints": {}}
        if canvas != "ABSENT":
            d["canvas_index"] = canvas
        (self.state / "SNAPSHOT.json").write_text(json.dumps(d, sort_keys=True))

    def snap(self, canvas: int) -> None:
        """One snapshot generation as the mind writes it: the ledger first, the manifest LAST, both carrying the same canvas count."""
        self.ledger(canvas)
        self.manifest(canvas, t=canvas * 5)

    def exam_file(self, name=EXAM_A, body=EXAM_BODY) -> None:
        self.exam.mkdir(parents=True, exist_ok=True)
        (self.exam / name).write_text(body)

    def last(self, canvas: int) -> None:
        self.exam.mkdir(parents=True, exist_ok=True)
        (self.exam / "LAST.json").write_text(json.dumps({"last_canvas": canvas}))


class _Base(unittest.TestCase):
    def fx(self) -> Fx:
        f = Fx()
        self.addCleanup(shutil.rmtree, f.root, ignore_errors=True)
        return f


def _run_voice(which: str, fx: Fx, steps, every: int = EVERY) -> dict:
    stop = ScriptedStop([functools.partial(s, fx) for s in steps])
    fires: list = []

    def recorder(root, genome_path, *a, **k):
        fires.append((stop.waits, json.loads((Path(root) / "exam" / "LAST.json").read_text())["last_canvas"]))
        return {}
    with ReadCounter() as rc:
        if which == "new":
            with mock.patch.object(exam_module, "run_and_journal", recorder):
                exam_module.voice_loop(fx.root, SKELETON, stop, every, POLL)
        else:
            _old_voice_loop(recorder)(fx.root, SKELETON, stop, every, POLL)
    last = fx.exam / "LAST.json"
    return {"fires": fires, "last": json.loads(last.read_text()) if last.exists() else None, "polls": stop.waits,
            "timeouts": set(stop.timeouts), "ledger": rc.ledger, "manifest": rc.manifest}


def _run_sit(which: str, fx: Fx, steps, every: int = EVERY) -> dict:
    stop = ScriptedStop([functools.partial(s, fx) for s in steps])
    pubs: list = []

    def publish(sense, payload, meta, ext):
        pubs.append((stop.waits, meta["exam_file"], meta["score"]))
        return {"seq": len(pubs)}
    buf = io.StringIO()
    fn = sit_module.sense if which == "new" else _old_sense()
    with ReadCounter() as rc, contextlib.redirect_stdout(buf):
        fn(publish, stop, fx.root, SKELETON, every, POLL)
    return {"pubs": pubs, "stdout": buf.getvalue(), "polls": stop.waits, "timeouts": set(stop.timeouts), "ledger": rc.ledger, "manifest": rc.manifest}


def _noop(fx: Fx) -> None:
    return None


# ---------------------------------------------------------------------------------------------------------------------------------------------
class TestPinsAndMapping(unittest.TestCase):
    def test_the_fixture_arithmetic_is_anchored(self) -> None:
        self.assertEqual(int(parse_genome(SKELETON.read_text()).gaze["fixations"]), FIXATIONS, "the ledger road's unit: moments // 4 (S3a, S9)")

    def test_the_reference_loops_are_the_pinned_old_source(self) -> None:
        self.assertEqual(hashlib.sha256(OLD_VOICE_LOOP_SRC.encode("utf-8")).hexdigest(), OLD_VOICE_LOOP_SHA256, "the reference voice_loop was edited")
        self.assertEqual(hashlib.sha256(OLD_SENSE_SRC.encode("utf-8")).hexdigest(), OLD_SENSE_SHA256, "the reference sense was edited")
        self.assertIn("json.loads(ledger_path.read_text())", OLD_VOICE_LOOP_SRC)
        self.assertIn("json.loads(ledger_path.read_text())", OLD_SENSE_SRC)

    def test_the_real_loops_are_not_the_reference(self) -> None:
        """A reference identical to the code under test compares nothing (#171): the fixed loops must differ from the pinned old ones."""
        self.assertNotEqual(inspect.getsource(exam_module.voice_loop).strip(), OLD_VOICE_LOOP_SRC.strip())
        self.assertNotEqual(inspect.getsource(sit_module.sense).strip(), OLD_SENSE_SRC.strip())
        self.assertNotIn("json.loads(ledger_path.read_text())", inspect.getsource(exam_module.voice_loop), "voice_loop must not parse the ledger itself any more")
        self.assertNotIn("json.loads(ledger_path.read_text())", inspect.getsource(sit_module.sense), "sense must not parse the ledger itself any more")

    def test_the_mutant_mapping_names_real_tests(self) -> None:
        self.assertEqual(sorted(MUTANT_TESTS), sorted(["m%d" % i for i in range(1, 19)] + ["m12b", "m14w"]), "every mutant of the law's G5 is mapped (m1..m15, plus the splits m12b/m14w and the author's m16..m18)")
        for mid, dotted in MUTANT_TESTS.items():
            cls, meth = dotted.split(".")
            self.assertTrue(callable(getattr(globals()[cls], meth, None)), f"{mid}: {dotted} is not a test of this module")


# ---------------------------------------------------------------------------------------------------------------------------------------------
class TestWriter(_Base):
    """The WRITER: a real Mind.snapshot() of a tiny mind (the tests/creature/test_a42_b1.py shape) — m1, m2, m3, m14w."""

    def _consume_to(self, mind: Mind, rows, eye_rows: int, start: int = 0) -> int:
        seen = sum(1 for r in rows[:start] if r.get("sense") == "eye")
        i = start
        while i < len(rows) and seen < eye_rows:
            mind.consume(rows[i])
            seen += 1 if rows[i].get("sense") == "eye" else 0
            i += 1
        return i

    def _tiny(self, canvases: int):
        root = Path(tempfile.mkdtemp(prefix="pollercursor-mind-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        _tc._build_repeated_tape(root, "circle", canvases)
        return Mind(COARSE_GENOME, root), root, list(read_tape(root))

    def _read(self, root: Path):
        state = root / "state"
        return json.loads((state / "SNAPSHOT.json").read_text()), json.loads((state / "ledger.json").read_text())

    def test_manifest_carries_the_ledgers_canvas_index(self) -> None:
        mind, root, rows = self._tiny(3)
        self._consume_to(mind, rows, 3)
        self.assertEqual(mind._canvas_index, 3, "fixture premise: three canvases consumed")
        mind.snapshot()
        manifest, ledger = self._read(root)
        self.assertIn("canvas_index", manifest, "the manifest carries the cursor (an OLD-format manifest has no key)")
        ci = manifest["canvas_index"]
        self.assertIs(type(ci), int, f"an int, never a bool/str/float: {ci!r}")
        self.assertEqual(ci, ledger["canvas_index"], "the very integer the ledger written in the same call carries")
        self.assertEqual(ci, mind._canvas_index)
        self.assertNotEqual(ci, manifest["t"], f"fixture premise: moments ({manifest['t']}) are not canvases ({ci}), so a writer of org.t is distinguishable")
        self.assertNotEqual(ci, mind.org.t)

    def test_manifest_canvas_index_follows_a_second_snapshot(self) -> None:
        mind, root, rows = self._tiny(5)
        i = self._consume_to(mind, rows, 3)
        mind.snapshot()
        first = self._read(root)[0]["canvas_index"]
        self._consume_to(mind, rows, 5, start=i)
        mind.snapshot()
        manifest, ledger = self._read(root)
        self.assertEqual((first, manifest["canvas_index"], ledger["canvas_index"]), (3, 5, 5), "the cursor moves with the ledger: never a constant, never stale")

    def test_manifest_keeps_every_key_the_generation_machinery_reads(self) -> None:
        from creature.mind import _generation_t
        mind, root, rows = self._tiny(3)
        self._consume_to(mind, rows, 3)
        mind.snapshot()
        manifest, _ledger = self._read(root)
        for k in ("t", "last_seq", "files", "prints"):
            self.assertIn(k, manifest)
        self.assertIn("ledger.json", manifest["files"])
        self.assertEqual(_generation_t(root / "state"), manifest["t"], "the heal/keep-prev readers still see a whole generation")
        resumed, last_seq = Mind.resume(COARSE_GENOME, root)
        self.assertEqual(resumed._canvas_index, 3, "a resume on a new-format state still restores the count (from the ledger, as before)")
        self.assertEqual(last_seq, mind.last_seq)


# ---------------------------------------------------------------------------------------------------------------------------------------------
class TestReaderRoads(_Base):
    """canvas_count_now(state_dir, fixations) -> (count | None, road): the three roads, each said."""

    def now(self, fx: Fx):
        return exam_module.canvas_count_now(fx.state, FIXATIONS)

    def test_the_snapshot_road_reads_the_manifest_key(self) -> None:
        fx = self.fx(); fx.manifest(520, t=2600)                                  # a manifest alone: the key is the whole answer
        self.assertEqual(self.now(fx), (520, "snapshot"))
        fx.ledger(canvas=5)                                                        # a ledger that DIVERGES: the manifest still wins (S2's guard)
        self.assertEqual(self.now(fx), (520, "snapshot"), "the snapshot road reads the key, not the ledger")
        fx2 = self.fx(); fx2.snap(1030)
        self.assertEqual(self.now(fx2), (1030, "snapshot"))
        fx3 = self.fx(); fx3.manifest(0, t=0)
        self.assertEqual(self.now(fx3), (0, "snapshot"), "a zero is a count: the first snapshot of a young mind")

    def test_the_snapshot_road_never_opens_the_ledger(self) -> None:
        fx = self.fx(); fx.snap(520)
        with ReadCounter() as rc:
            got = self.now(fx)
        self.assertEqual(got, (520, "snapshot"))
        self.assertEqual((rc.ledger, rc.manifest), (0, 1), f"ledger opens 0 beside manifest opens {rc.manifest}: the instrument saw the manifest, so the 0 is a reading")

    def test_a_keyless_manifest_takes_the_ledger_road(self) -> None:
        fx = self.fx(); fx.ledger(canvas=520); fx.manifest("ABSENT", t=2600)      # an OLD-format life that has reached the boundary
        self.assertEqual(self.now(fx), (520, "ledger"))
        fx2 = self.fx(); fx2.ledger(canvas=100, moments=2200); fx2.manifest("ABSENT", t=2200)
        self.assertEqual(self.now(fx2), (100, "ledger"))
        fx3 = self.fx(); fx3.ledger(canvas=None, moments=2200); fx3.manifest("ABSENT", t=2200)   # S9: a ledger with no canvas_index at all
        self.assertEqual(self.now(fx3), (2200 // FIXATIONS, "ledger"), "the old arithmetic, unchanged")
        fx4 = self.fx(); fx4.ledger(canvas=520)                                   # S4: no manifest at all (a life older than generations)
        self.assertEqual(self.now(fx4), (520, "ledger"))

    def test_a_keyless_manifest_never_stands_in_t_over_fixations(self) -> None:
        fx = self.fx(); fx.ledger(canvas=100, moments=2200); fx.manifest("ABSENT", t=2200)
        count, road = self.now(fx)
        self.assertNotEqual(count, 2200 // FIXATIONS, "t counts MOMENTS (5 a canvas): moments // fixations is the over-count M4 removed (S3)")
        self.assertEqual((count, road), (100, "ledger"))

    def test_a_key_that_is_not_a_count_takes_the_ledger_road(self) -> None:
        for bad in (True, False, None, "520", 520.0, [520], {"n": 520}):
            with self.subTest(key=bad):
                fx = self.fx(); fx.ledger(canvas=520)
                (fx.state).mkdir(parents=True, exist_ok=True)
                (fx.state / "SNAPSHOT.json").write_text(json.dumps({"t": 2600, "last_seq": 0, "files": [], "prints": {}, "canvas_index": bad}))
                self.assertEqual(self.now(fx), (520, "ledger"), "a bool is not a count (True would read 1), and neither is a str, a float, a list")

    def test_an_unreadable_manifest_takes_the_ledger_road(self) -> None:
        cases = {"not json": b"not json at all", "not utf-8": b"\xff\xfe\x00\x01 broken", "empty": b"", "truncated": b'{"canvas_index": 52',
                 "a list": b"[1, 2, 3]", "a string": b'"520"', "null": b"null", "a dict without the key": b'{"t": 2600}'}
        for name, raw in cases.items():
            with self.subTest(manifest=name):
                fx = self.fx(); fx.ledger(canvas=520); fx.manifest(raw=raw)
                self.assertEqual(self.now(fx), (520, "ledger"), "a missing/unreadable/non-UTF-8/non-JSON manifest falls through to the ledger")
        fx = self.fx(); fx.ledger(canvas=520); (fx.state / "SNAPSHOT.json").mkdir()   # an OSError that is not FileNotFoundError
        self.assertEqual(self.now(fx), (520, "ledger"))

    def test_no_files_is_none_road_and_the_state_directory_may_be_absent(self) -> None:
        fx = self.fx()
        self.assertEqual(self.now(fx), (None, "none"), "no state directory at all: the tick is skipped, as today when ledger.json does not exist")
        fx.state.mkdir()
        self.assertEqual(self.now(fx), (None, "none"))

    def test_a_torn_ledger_is_zero_not_a_crash(self) -> None:
        fx = self.fx(); fx.ledger(raw='{"moments": 26'); fx.manifest("ABSENT", t=130)    # S8: truncated JSON, no manifest key: OLD's {} -> 0
        self.assertEqual(self.now(fx), (0, "ledger"))
        fx2 = self.fx(); fx2.ledger(raw=""); self.assertEqual(self.now(fx2), (0, "ledger"))
        fx3 = self.fx(); fx3.ledger(raw="[1, 2]")      # valid JSON, not a dict: canvas_count_of's own guard (unchanged code)
        self.assertEqual(self.now(fx3), (0, "ledger"))

    def test_the_manifest_is_read_afresh_every_call(self) -> None:
        fx = self.fx(); fx.snap(520)
        self.assertEqual(self.now(fx), (520, "snapshot"))
        fx.snap(1030)
        self.assertEqual(self.now(fx), (1030, "snapshot"), "no cache between polls: a stale-forever reader never fires again")
        (fx.state / "SNAPSHOT.json").unlink()
        self.assertEqual(self.now(fx), (1030, "ledger"), "a removed manifest falls to the ledger road at once")
        fx.manifest(2000, t=10000)
        self.assertEqual(self.now(fx), (2000, "snapshot"))

    def test_the_reader_lags_by_at_most_a_snapshot_and_never_leads(self) -> None:
        """§2.2: the ledger is renamed before the manifest, so a poll between the two sees the NEW ledger and the OLD manifest: the new reader
        lags one poll, never leads (documented, not a mutant's catcher)."""
        fx = self.fx(); fx.snap(520)
        fx.ledger(1030)                                                            # the ledger of the next generation lands first ...
        count, road = self.now(fx)
        self.assertEqual((count, road), (520, "snapshot"))
        self.assertLessEqual(count, 1030, "never ahead of the ledger")
        fx.manifest(1030, t=5150)                                                  # ... and the manifest LAST
        self.assertEqual(self.now(fx), (1030, "snapshot"))


# ---------------------------------------------------------------------------------------------------------------------------------------------
class TestLoopEquivalence(_Base):
    """G3: the REAL loops against the pinned OLD loops on scripted sequences. The trace of a loop = every fire / publish with its poll index and
    canvas count; the expected trace of each scenario is written HERE, by hand, before the code. S2 is the only scenario whose traces differ."""

    def both_voice(self, setup, steps, every=EVERY):
        out = {}
        for which in ("new", "old"):
            fx = self.fx(); setup(fx)
            out[which] = _run_voice(which, fx, steps, every)
        return out["new"], out["old"]

    def both_sit(self, setup, steps, every=EVERY):
        out = {}
        for which in ("new", "old"):
            fx = self.fx(); setup(fx)
            out[which] = _run_sit(which, fx, steps, every)
        return out["new"], out["old"]

    def assert_cadence(self, new, old, steps) -> None:
        self.assertEqual(new["polls"], len(steps) + 1)
        self.assertEqual(old["polls"], len(steps) + 1)
        self.assertEqual(new["timeouts"], {POLL}, "the wait between polls is the poll_period, as before")
        self.assertEqual(old["timeouts"], {POLL})

    # ---- S1: the manifest and the ledger agree over three snapshots
    S1_STEPS = [lambda fx: fx.snap(520), _noop, lambda fx: fx.snap(900), _noop, lambda fx: fx.snap(1030), _noop]

    def test_s1_voice_loop_manifest_and_ledger_agree(self) -> None:
        new, old = self.both_voice(lambda fx: fx.snap(250), self.S1_STEPS)
        expected = [(1, 520), (5, 1030)]
        self.assert_cadence(new, old, self.S1_STEPS)
        self.assertEqual(old["fires"], expected, "the reference loop's own trace")
        self.assertEqual(new["fires"], expected, "the same boundaries as the old loop")
        self.assertEqual((new["last"], old["last"]), ({"last_canvas": 1030},) * 2)
        polls = len(self.S1_STEPS) + 1
        self.assertEqual((old["ledger"], old["manifest"]), (polls, 0), "the old loop parses the ledger on every poll")
        self.assertEqual((new["ledger"], new["manifest"]), (0, polls), f"the new loop parses the ledger 0 times and reads the manifest once per poll ({polls} of {polls})")

    def test_s1_sit_sense_manifest_and_ledger_agree(self) -> None:
        def setup(fx):
            fx.exam_file(EXAM_A); fx.snap(250)
        steps = [lambda fx: fx.snap(520), _noop, lambda fx: fx.snap(900), _noop,
                 lambda fx: (fx.exam_file(EXAM_B), fx.snap(1030)), _noop]            # the live order: the exam writes its file, then the ledger advances
        new, old = self.both_sit(setup, steps)
        expected = [(1, EXAM_A, 0.8), (5, EXAM_B, 0.8)]
        self.assert_cadence(new, old, steps)
        self.assertEqual(old["pubs"], expected)
        self.assertEqual(new["pubs"], expected)
        polls = len(steps) + 1
        self.assertEqual((old["ledger"], old["manifest"]), (polls, 0))
        self.assertEqual((new["ledger"], new["manifest"]), (0, polls), f"the new sense parses the ledger 0 times and reads the manifest {polls} of {polls} polls")

    # ---- S2: the manifest and the ledger DIVERGE (the manifest ahead by `every`): the one pair that must differ
    def test_s2_the_manifest_and_the_ledger_diverge_voice_loop(self) -> None:
        def setup(fx):
            fx.ledger(100); fx.manifest(600, t=500)
        new, old = self.both_voice(setup, [_noop])
        self.assertEqual(old["fires"], [], "OLD reads the ledger: 100 < 500")
        self.assertEqual(new["fires"], [(0, 600)], "NEW reads the manifest: 600 >= 500, at the first poll")
        self.assertNotEqual(new["fires"], old["fires"], "the planted difference: the proof the snapshot road is the road taken")
        self.assertEqual((new["ledger"], new["manifest"]), (0, 2))

    def test_s2_the_manifest_and_the_ledger_diverge_sit_sense(self) -> None:
        def setup(fx):
            fx.exam_file(EXAM_A); fx.ledger(100); fx.manifest(600, t=500)
        new, old = self.both_sit(setup, [_noop])
        self.assertEqual(old["pubs"], [])
        self.assertEqual(new["pubs"], [(0, EXAM_A, 0.8)])
        self.assertNotEqual(new["pubs"], old["pubs"])

    # ---- S3: key absent (an OLD-format manifest): the ledger road, never t // fixations
    def test_s3_a_keyless_manifest_reads_the_ledger_never_t_over_fixations(self) -> None:
        def setup_a(fx):
            fx.ledger(canvas=100, moments=2200); fx.manifest("ABSENT", t=2200)       # 2200 // 4 = 550 would FIRE; the ledger's 100 must not
        new, old = self.both_voice(setup_a, [_noop, _noop])
        self.assertEqual((new["fires"], old["fires"]), ([], []))
        self.assertEqual((new["ledger"], old["ledger"]), (3, 3), "the ledger road at today's cost, 3 of 3 polls")
        newS, oldS = self.both_sit(lambda fx: (fx.exam_file(EXAM_A), setup_a(fx)), [_noop, _noop])
        self.assertEqual((newS["pubs"], oldS["pubs"]), ([], []))

        def setup_b(fx):
            fx.ledger(canvas=520); fx.manifest("ABSENT", t=2600)                     # an old-format life that HAS reached the boundary
        new, old = self.both_voice(setup_b, [_noop])
        self.assertEqual(old["fires"], [(0, 520)])
        self.assertEqual(new["fires"], [(0, 520)], "the ledger road fires where OLD fires")
        newS, oldS = self.both_sit(lambda fx: (fx.exam_file(EXAM_A), setup_b(fx)), [_noop])
        self.assertEqual((oldS["pubs"], newS["pubs"]), ([(0, EXAM_A, 0.8)],) * 2)

    # ---- S4: no manifest at all
    def test_s4_no_manifest_is_the_old_road(self) -> None:
        steps = [lambda fx: fx.ledger(520), lambda fx: fx.ledger(1030)]
        new, old = self.both_voice(lambda fx: fx.ledger(250), steps)
        self.assertEqual(old["fires"], [(1, 520), (2, 1030)])
        self.assertEqual(new["fires"], old["fires"])
        self.assertEqual((new["ledger"], new["manifest"], old["ledger"]), (3, 3, 3), "ledger parses equal OLD's; the manifest was tried each poll and missing")

    # ---- S5: the key is not a count
    def test_s5_a_key_that_is_not_a_count_is_the_ledger_road(self) -> None:
        for bad in (True, False, None, "520", 520.0):
            with self.subTest(key=bad):
                def setup(fx, bad=bad):
                    fx.ledger(canvas=520); fx.state.mkdir(parents=True, exist_ok=True)
                    (fx.state / "SNAPSHOT.json").write_text(json.dumps({"t": 2600, "last_seq": 0, "files": [], "prints": {}, "canvas_index": bad}))
                new, old = self.both_voice(setup, [_noop])
                self.assertEqual(old["fires"], [(0, 520)])
                self.assertEqual(new["fires"], old["fires"])

    # ---- S6: the manifest bytes are not JSON / not UTF-8 / not a dict
    def test_s6_an_unreadable_manifest_is_the_ledger_road(self) -> None:
        for name, raw in {"not json": b"not json", "not utf-8": b"\xff\xfe\x00 x", "empty": b"", "truncated": b'{"canvas_index": 52', "a list": b"[1]"}.items():
            with self.subTest(manifest=name):
                def setup(fx, raw=raw):
                    fx.ledger(canvas=520); fx.manifest(raw=raw)
                new, old = self.both_voice(setup, [_noop])
                self.assertEqual(old["fires"], [(0, 520)])
                self.assertEqual(new["fires"], old["fires"])
                newS, oldS = self.both_sit(lambda fx, setup=setup: (fx.exam_file(EXAM_A), setup(fx)), [_noop])
                self.assertEqual(newS["pubs"], oldS["pubs"])
                self.assertEqual(oldS["pubs"], [(0, EXAM_A, 0.8)])

    # ---- S7: neither file: the tick is skipped, then the files appear
    def test_s7_neither_file_skips_the_tick(self) -> None:
        steps = [_noop, lambda fx: fx.snap(520)]
        new, old = self.both_voice(lambda fx: None, steps)
        self.assertEqual(old["fires"], [(2, 520)])
        self.assertEqual(new["fires"], old["fires"], "polls 0 and 1 find nothing and skip, exactly as OLD skips when ledger.json does not exist")
        newS, oldS = self.both_sit(lambda fx: fx.exam_file(EXAM_A), steps)
        self.assertEqual(oldS["pubs"], [(2, EXAM_A, 0.8)])
        self.assertEqual(newS["pubs"], oldS["pubs"])
        self.assertEqual((new["ledger"], new["manifest"]), (0, 3), "NEW tried the manifest at all 3 polls (two misses, then the key) and never opened the ledger")

    # ---- S8: the ledger is torn and the manifest has no key
    def test_s8_a_torn_ledger_is_no_fire_then_heals(self) -> None:
        def setup(fx):
            fx.ledger(raw='{"moments": 26'); fx.manifest("ABSENT", t=130)
        steps = [lambda fx: fx.ledger(520)]
        new, old = self.both_voice(setup, steps)
        self.assertEqual(old["fires"], [(1, 520)], "poll 0: OLD's {} -> 0 -> no fire; poll 1: the healed ledger fires")
        self.assertEqual(new["fires"], old["fires"])

    # ---- S9: a ledger with moments only (the pre-M4 arithmetic)
    def test_s9_a_ledger_with_no_canvas_index_is_moments_over_fixations(self) -> None:
        new, old = self.both_voice(lambda fx: fx.ledger(canvas=None, moments=2200), [_noop])
        self.assertEqual(old["fires"], [(0, 550)])
        self.assertEqual(new["fires"], [(0, 550)])

    # ---- S10: a restart with the cursor already past / not yet reached
    def test_s10_restart_with_the_exam_cursor(self) -> None:
        new, old = self.both_voice(lambda fx: fx.snap(1300), [_noop, _noop])
        self.assertEqual(old["fires"], [(0, 1300)], "a voice with no LAST.json fires ONCE on a mind already past the boundary, then never again")
        self.assertEqual(new["fires"], old["fires"])

        def setup(fx):
            fx.last(1300); fx.snap(1300)
        steps = [lambda fx: fx.snap(1700), lambda fx: fx.snap(1801), _noop]
        new, old = self.both_voice(setup, steps)
        self.assertEqual(old["fires"], [(2, 1801)], "LAST.json already past the boundary: no fire until 500 more canvases")
        self.assertEqual(new["fires"], old["fires"])
        newS, oldS = self.both_sit(lambda fx: (fx.exam_file(EXAM_A), fx.snap(1300)), [_noop, _noop])
        self.assertEqual(oldS["pubs"], [(0, EXAM_A, 0.8)], "SIT's cursor is in memory: a restart republishes the CURRENT latest file once")
        self.assertEqual(newS["pubs"], oldS["pubs"])

    # ---- S11: SIT's own cursors
    def test_s11_sit_torn_file_is_retried_then_published_once(self) -> None:
        def setup(fx):
            fx.exam_file(EXAM_A, body=""); fx.snap(520)                                  # the torn instant between the voice's create and its write
        steps = [lambda fx: fx.exam_file(EXAM_A, EXAM_BODY), _noop, _noop]
        new, old = self.both_sit(setup, steps)
        self.assertEqual(old["pubs"], [(1, EXAM_A, 0.8)], "poll 0 reads the empty file and spends nothing; poll 1 publishes it ONCE")
        self.assertEqual(new["pubs"], old["pubs"])
        self.assertEqual(new["stdout"], old["stdout"])

    def test_s11_sit_gives_a_never_parsing_file_up_after_max_torn_retries(self) -> None:
        def setup(fx):
            fx.exam_file(EXAM_A, body="{not json"); fx.snap(520)
        steps = [_noop] * (sit_module.MAX_TORN_RETRIES + 1) + [lambda fx: (fx.exam_file(EXAM_B, EXAM_BODY), fx.snap(1100)), _noop]
        new, old = self.both_sit(setup, steps)
        self.assertIn("gave up on " + EXAM_A, old["stdout"])
        self.assertEqual(old["pubs"], [(len(steps) - 1, EXAM_B, 0.8)], "the abandoned file is never published; the next file publishes through the next boundary")
        self.assertEqual(new["pubs"], old["pubs"])
        self.assertEqual(new["stdout"], old["stdout"], "the printed note is the same bytes")

    # ---- S12: a non-positive period
    def test_s12_a_non_positive_period_never_fires_and_sit_never_polls(self) -> None:
        for every in (0, -5):
            with self.subTest(every=every):
                new, old = self.both_voice(lambda fx: fx.snap(5000), [_noop], every=every)
                self.assertEqual((new["fires"], old["fires"]), ([], []))
                newS, oldS = self.both_sit(lambda fx: (fx.exam_file(EXAM_A), fx.snap(5000)), [_noop], every=every)
                self.assertEqual((newS["pubs"], oldS["pubs"]), ([], []))
                self.assertEqual((oldS["ledger"], oldS["manifest"]), (0, 0), "OLD's SIT never opened the ledger when every <= 0")
                self.assertEqual((newS["ledger"], newS["manifest"]), (0, 0), "and NEW's never opens the manifest either: SIT never polls")


# ---------------------------------------------------------------------------------------------------------------------------------------------
class TestReadersOffTheReplaysRoad(_Base):
    """G1: a replay can show the writer's extra key moves nothing in the journal; it cannot show the pollers read the right number — because it
    never runs them. Proved, not asserted: the readers are patched to RAISE under a real replay that completes."""

    def _raising(self):
        boom = AssertionError("a poller/reader ran on the replay's road")
        return (mock.patch.object(exam_module, "voice_loop", side_effect=boom), mock.patch.object(sit_module, "sense", side_effect=boom),
                mock.patch.object(exam_module, "canvas_count_now", side_effect=boom))

    def test_a_real_replay_completes_with_the_readers_raising_and_leaves_a_keyed_manifest(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="pollercursor-tape-")); self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        _tc._build_repeated_tape(root, "circle", 6)
        tape = sorted((root / "tape").glob("*.jsonl"))[0]
        work = Path(tempfile.mkdtemp(prefix="pollercursor-work-")); self.addCleanup(shutil.rmtree, work, ignore_errors=True)
        out = Path(tempfile.mkdtemp(prefix="pollercursor-out-")); self.addCleanup(shutil.rmtree, out, ignore_errors=True)
        p1, p2, p3 = self._raising()
        with p1, p2, p3, mock.patch.object(tempfile, "tempdir", str(work)):
            journal = run_replay(COARSE_GENOME, tape, out, close=True)
        self.assertTrue(Path(journal).exists(), "the replay ran to the end with every reader patched to raise")
        roots = sorted(work.glob("creature-replay-*"))
        self.assertEqual(len(roots), 1)
        state = roots[0] / "state"
        manifest = json.loads((state / "SNAPSHOT.json").read_text()); ledger = json.loads((state / "ledger.json").read_text())
        self.assertIn("canvas_index", manifest, "NOT VACUOUS: the changed line ran on the replay's road (an ON replay that ignored the change carries no key)")
        self.assertEqual(manifest["canvas_index"], ledger["canvas_index"])
        self.assertEqual(manifest["canvas_index"], 6, "six canvases replayed")

    def test_the_same_patch_makes_a_direct_call_raise_the_positive_control(self) -> None:
        fx = self.fx(); fx.snap(520)
        p1, p2, p3 = self._raising()
        with p1, p2, p3:
            with self.assertRaises(AssertionError):
                exam_module.canvas_count_now(fx.state, FIXATIONS)
            with self.assertRaises(AssertionError):
                exam_module.voice_loop(fx.root, SKELETON, ScriptedStop([]), EVERY, POLL)
            with self.assertRaises(AssertionError):
                sit_module.sense(lambda *a: None, ScriptedStop([]), fx.root, SKELETON, EVERY, POLL)


if __name__ == "__main__":
    unittest.main()
