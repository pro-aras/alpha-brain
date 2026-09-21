# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 12:2x +0400 — C1 (docs/G4-WAVE3-CLAUSES.md W3-0b):
# the six body-side gene values ("HEART, TAPE, WORLD, ASK, CRASH, BODY declared but nothing reads their
# VALUE") each get a toy that CHANGES the value and reads the change, per docs/briefs/W3-BUILDER-C.md C1.
# WORLD's own toy (period/window) lives in tests/creature/test_world_maker.py alongside its other coverage
# and the PIN in tests/creature/test_world_pin.py; this file covers the other five plus WORLD's regression
# (declared but undeclared/default paths stay byte-for-byte what they were).
#
# Two of the six (ASK, CRASH) have a real parser gap this builder cannot close (genome/machinery.py is not
# owned by this worktree's C1 -- "genome/*.py, not yours" per the brief): ASK's grammar accepts ONLY the
# literal six-verb string "what-is show is which next why" (never a subset), and CRASH's accepts ONLY the
# literal "sense restart journal; mind page" (never one half alone) -- `re.fullmatch` on a fixed string in
# both cases. So the toys that need a DIFFERENT declared value than what the real parser can produce are
# exercised at the pure-function level (`_ask_refusal`, `_crash_policy`) against a hand-built `declared`
# dict (the same technique tests/creature/test_refusal.py's TestPlantedControl already uses to plant a key
# `parse_genome` would never emit) -- RAISED in the builder report, not worked around.
from __future__ import annotations

import dataclasses
import io
import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from typing import Optional
from unittest import mock

import numpy as np
from PIL import Image

from creature import ask as creature_ask
from creature import body as body_module
from creature.body import Body, KNOWN_BODY_THREADS, _check_body_threads, _crash_policy
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"    # declares NONE of these six genes -- every default path
G4_GENOME = ROOT / "genome" / "G4.genome"                # declares the real, standard line for each of the six


def _append(extra_line: str) -> Path:
    """A temp genome file = G4-skeleton.genome's text + one more gene line (test_refusal.py's own
    technique: a real genome, plus exactly the one line under test, nothing else changed)."""
    d = Path(tempfile.mkdtemp())
    p = d / "genome.genome"
    p.write_text(GENOME_PATH.read_text() + extra_line + "\n")
    return p


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _journal_rows(root: Path) -> list:
    out = []
    jdir = root / "journal"
    if not jdir.exists():
        return out
    for f in sorted(jdir.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


# ============================================================================ C1.1 HEART
class TestHeartPeriod(unittest.TestCase):
    def _distinct_heartbeats(self, genome_path: Path, observe_s: float) -> int:
        root = Path(tempfile.mkdtemp())
        body = Body(root, genome_path)   # no senses -- the STATUS thread runs regardless (PREREG §2.5)
        body.start()
        seen = set()
        deadline = time.time() + observe_s
        try:
            while time.time() < deadline:
                try:
                    status = json.loads((root / "STATUS.json").read_text())
                    seen.add(status["heartbeat_at"])
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
                time.sleep(0.1)
        finally:
            body.stop()
            shutil.rmtree(root, ignore_errors=True)
        return len(seen)

    def test_heart_every_1s_writes_status_at_least_3_times_in_5s(self) -> None:
        genome_path = _append("HEART every 1 s")
        n = self._distinct_heartbeats(genome_path, observe_s=5.0)
        self.assertGreaterEqual(n, 3, f"HEART every 1 s must write STATUS >= 3 times in 5 s, saw {n}")

    def test_heart_every_60s_writes_status_once_in_5s(self) -> None:
        genome_path = _append("HEART every 60 s")
        n = self._distinct_heartbeats(genome_path, observe_s=5.0)
        self.assertEqual(n, 1, f"HEART every 60 s must write STATUS exactly once in a 5 s window, saw {n}")

    def test_heart_undeclared_keeps_default_period(self) -> None:
        self.assertEqual(Body(Path(tempfile.mkdtemp()), GENOME_PATH)._status_period_s, body_module.STATUS_PERIOD_S)


# ============================================================================ C1.2 TAPE
class TestTapeDeclaredPath(unittest.TestCase):
    def test_default_path_is_byte_identical_to_today(self) -> None:
        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        self.assertEqual(tape.tape_dir, root / "tape")

    def test_declared_run_tape_resolves_to_root_tape_too(self) -> None:
        root = Path(tempfile.mkdtemp())
        tape = Tape(root, declared_path="run/tape")
        self.assertEqual(tape.tape_dir, root / "tape")

    def test_declared_run_tape2_moves_the_directory(self) -> None:
        root = Path(tempfile.mkdtemp())
        genome_path = _append("TAPE run/tape2")

        def ear_only(publish, stop_event) -> None:
            for i in range(3):
                if stop_event.is_set():
                    return
                publish("ear", f"w{i}".encode("utf-8"), {"moment": f"t{i:03d}", "source": "test", "word": f"w{i}"}, "txt")
                stop_event.wait(0.05)

        body = Body(root, genome_path)
        self.assertEqual(body._tape_declared_path, "run/tape2")
        body.add_sense("test", ear_only)
        body.start()
        try:
            time.sleep(1.0)   # 3 rows at 0.05 s apart -- comfortable margin
        finally:
            body.stop()

        self.assertTrue((root / "tape2").exists(), "TAPE run/tape2 must land under R/tape2")
        self.assertFalse((root / "tape").exists(), "TAPE run/tape2 must write NOTHING under R/tape")
        rows = list(read_tape(root, declared_path="run/tape2"))
        self.assertEqual(len(rows), 3)

        # a restart on the SAME root+genome must find the backlog through the declared path too
        body2 = Body(root, genome_path)
        body2.start()
        time.sleep(0.5)
        body2.stop()
        self.assertEqual(len(list(read_tape(root, declared_path="run/tape2"))), 3, "a restart must not re-publish")
        shutil.rmtree(root, ignore_errors=True)


# ============================================================================ C1.4 ASK
class TestAskVerbGating(unittest.TestCase):
    def test_pure_gate_reads_the_declared_verb_list(self) -> None:
        standard = parse_genome(G4_GENOME.read_text())
        self.assertEqual(standard.declared["ASK"]["verbs"], ["what-is", "show", "is", "which", "next", "why"])
        self.assertIsNone(creature_ask._ask_refusal(standard, "show"), "the default (standard) list answers show")
        self.assertIsNone(creature_ask._ask_refusal(standard, "next"))

        restricted = dataclasses.replace(standard, declared={**standard.declared, "ASK": {"verbs": ["what-is"]}})
        self.assertEqual(creature_ask._ask_refusal(restricted, "show"), "refused: show is not an ASK verb")
        self.assertIsNone(creature_ask._ask_refusal(restricted, "what-is"))

    def test_ask_undeclared_keeps_every_verb_reachable(self) -> None:
        skeleton = parse_genome(GENOME_PATH.read_text())
        self.assertNotIn("ASK", skeleton.declared)
        for q in ("what-is", "show", "is", "which"):
            self.assertIsNone(creature_ask._ask_refusal(skeleton, q))

    def test_answer_refuses_a_verb_outside_the_declared_list_end_to_end(self) -> None:
        """A real snapshot (two canvases, single-threaded -- Mind.snapshot() is only ever safe off the
        mind's own thread, test_ask.py's own finding) + a monkey-patched parse_genome (the same technique
        test_refusal.py's TestPlantedControl uses) stand in for the genome text the real ASK grammar
        cannot express today (RAISED in the report): the declared verb list this test exercises could not
        be written as a genome line, but the READING mechanism it proves is real."""
        root = Path(tempfile.mkdtemp())
        mind = Mind(GENOME_PATH, root)
        tape = Tape(root)
        rng = np.random.default_rng(5)
        for i, thing in enumerate(("circle", "square")):
            rgb, _truth = world.render_canvas(thing, rng)
            moment = f"g{i:03d}"
            row_ear = tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
            row_eye = tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")
            mind.consume(row_ear)
            mind.consume(row_eye)
        mind.snapshot()
        self.assertTrue((root / "state" / "organism.json").exists())

        unrestricted = creature_ask.answer(root, "show", ["circle"])
        self.assertTrue(unrestricted.startswith("show "), unrestricted)

        real_parse_genome = creature_ask.parse_genome

        def _parse_with_restricted_ask(text: str):
            g = real_parse_genome(text)
            g.declared = {**g.declared, "ASK": {"verbs": ["what-is"]}}
            return g

        with mock.patch.object(creature_ask, "parse_genome", side_effect=_parse_with_restricted_ask):
            restricted = creature_ask.answer(root, "show", ["circle"])
        self.assertEqual(restricted, "refused: show is not an ASK verb")
        shutil.rmtree(root, ignore_errors=True)


# ============================================================================ C1.5 CRASH
class TestCrashPolicy(unittest.TestCase):
    def test_pure_policy_defaults_and_reads_declared(self) -> None:
        self.assertEqual(_crash_policy({}), (True, True), "CRASH undeclared -- PREREG §2.6's crash law stands regardless")
        self.assertEqual(_crash_policy({"CRASH": {"sense": "restart journal", "mind": "page"}}), (True, True))
        self.assertEqual(_crash_policy({"CRASH": {"sense": "something else", "mind": "page"}}), (False, True),
                          "\"sense restart\" absent -> a crashed sense is NOT restarted")
        self.assertEqual(_crash_policy({"CRASH": {"sense": "restart journal", "mind": "nothing"}}), (True, False),
                          "\"mind page\" absent -> no PAGE.json, but STATUS.crash + exit 3 still stand")

    def test_the_lifes_own_crash_line_reads_both_on(self) -> None:
        genome = parse_genome(G4_GENOME.read_text())
        self.assertEqual(_crash_policy(genome.declared), (True, True))

    def test_sense_not_restarted_when_restart_off(self) -> None:
        """The negative control (both True, the current genome text -- test_crash.py's own two tests) is
        already pinned there; this is the positive direction: restart=False ends the thread after its one
        journaled crash instead of retrying (SenseThread.run, C1.5)."""
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body._crash_restart_on = False   # the state a looser CRASH grammar would set; see the report

        def flaky(publish, stop_event) -> None:
            thing = "circle"
            rgb, _truth = world.render_canvas(thing, np.random.default_rng(7))
            publish("ear", thing.encode("utf-8"), {"moment": "cx001", "source": "test", "word": thing}, "txt")
            publish("eye", _png_bytes(rgb), {"moment": "cx001", "source": "test"}, "png")
            raise RuntimeError("planted crash for C1.5's restart-off toy")

        st = body.add_sense("eye", flaky)
        self.assertFalse(st.restart)
        body.start()
        try:
            deadline = time.time() + 5.0
            while st.is_alive() and time.time() < deadline:
                time.sleep(0.1)
            self.assertFalse(st.is_alive(), "restart=False: the thread must end after its one crash, never retry")
            time.sleep(1.0)   # would-be second sense_restart, if any, has time to land before we check
        finally:
            body.stop()
        restarts = [r for r in _journal_rows(root) if r.get("event") == "sense_restart"]
        self.assertEqual(len(restarts), 1, "still journaled once, even though the thread does not retry")
        shutil.rmtree(root, ignore_errors=True)

    def test_no_page_when_page_off_but_status_crash_and_exit_3_stand(self) -> None:
        for page_on, expect_page in ((True, True), (False, False)):
            with self.subTest(page_on=page_on):
                root = Path(tempfile.mkdtemp())
                body = Body(root, GENOME_PATH)
                body.mind = Mind(GENOME_PATH, root)   # a bare, unthreaded Mind -- _build_status() only reads its fields
                body._crash_page_on = page_on
                with mock.patch("os._exit") as exit_mock:
                    body._handle_mind_crash(RuntimeError("planted"), {"seq": 1})
                exit_mock.assert_called_once_with(3)
                status = json.loads((root / "STATUS.json").read_text())
                self.assertIsNotNone(status["crash"], "#230: the crash law is not a gene, it stands regardless")
                self.assertEqual((root / "pages.jsonl").exists(), expect_page)
                shutil.rmtree(root, ignore_errors=True)


# ============================================================================ C1.6 BODY threads
class TestBodyThreadRoster(unittest.TestCase):
    def test_check_body_threads_is_a_pure_function(self) -> None:
        _check_body_threads({})   # BODY undeclared -- nothing to check
        _check_body_threads({"BODY": {"threads": ["eye", "ear", "mind", "voice"]}})   # extra known names are fine
        with self.assertRaises(GenomeError):
            _check_body_threads({"BODY": {"threads": ["eye", "wings"]}})
        with self.assertRaises(GenomeError):
            _check_body_threads({"BODY": {"threads": ["eye", "ear", "voice"]}})   # 'mind' missing

    def test_unknown_thread_refuses_naming_it(self) -> None:
        bad = _append("BODY service creature threads eye ear mind voice wings")
        with self.assertRaises(GenomeError) as ctx:
            Body(Path(tempfile.mkdtemp()), bad)
        self.assertIn("wings", str(ctx.exception))

    def test_missing_mind_refuses(self) -> None:
        bad = _append("BODY service creature threads eye ear voice")
        with self.assertRaises(GenomeError) as ctx:
            Body(Path(tempfile.mkdtemp()), bad)
        self.assertIn("mind", str(ctx.exception))

    def test_the_lifes_own_line_starts(self) -> None:
        genome = parse_genome(G4_GENOME.read_text())
        self.assertEqual(genome.declared["BODY"]["threads"], ["eye", "ear", "door", "mind", "voice"])
        self.assertEqual(set(genome.declared["BODY"]["threads"]), KNOWN_BODY_THREADS)
        body = Body(Path(tempfile.mkdtemp()), G4_GENOME)   # must construct without raising
        self.assertIsNotNone(body)


if __name__ == "__main__":
    unittest.main()
