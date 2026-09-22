# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE): the
# in-process sense thread (creature/senses/evolve.py) and the worker's own start/stop (mirroring
# creature/senses/game.py's own test conventions).
"""tests/creature/test_evolve_sense.py"""
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from creature.senses import evolve as evolve_sense
from tools.gate_g4 import sweep


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


class _FakeStopEvent:
    """A one-shot stop_event: is_set() flips True after `sense()`'s first full scan, so the test never
    blocks on the real `poll_period` wait — the same technique the folder/game door tests use."""

    def __init__(self) -> None:
        self._set = False

    def is_set(self) -> bool:
        was = self._set
        self._set = True
        return was

    def wait(self, _period: float) -> None:
        self._set = True


class TestSensePublishesProposals(unittest.TestCase):
    def test_publishes_each_proposal_file_in_order(self) -> None:
        root = _tmp()
        evolve_dir = root / "evolve"
        evolve_dir.mkdir(parents=True)
        published = []

        def fake_publish(sense, payload, meta, ext):
            published.append((sense, json.loads(payload.decode()), dict(meta), ext))
            return {"seq": len(published)}

        for n, verdict in ((1, "REFUSED"), (2, "PASS")):
            (evolve_dir / f"PROPOSAL-{n}.json").write_text(json.dumps({"no": n, "verdict": verdict, "gene": "KWTA.k", "value": 6}))

        evolve_sense.sense(fake_publish, _FakeStopEvent(), root, poll_period=0.01)

        self.assertEqual(len(published), 2)
        self.assertEqual([p[0] for p in published], ["proposal", "proposal"])
        self.assertEqual([p[1]["no"] for p in published], [1, 2])
        self.assertEqual(published[0][2]["verdict"], "REFUSED")
        self.assertEqual(published[1][2]["verdict"], "PASS")
        # meta carries the FULL proposal dict (Mind._consume_proposal reads meta, never the payload bytes)
        self.assertEqual(published[1][2]["gene"], "KWTA.k")

    def test_cursor_persists_and_a_restart_never_republishes(self) -> None:
        root = _tmp()
        evolve_dir = root / "evolve"
        evolve_dir.mkdir(parents=True)
        (evolve_dir / "PROPOSAL-1.json").write_text(json.dumps({"no": 1, "verdict": "PASS"}))
        published = []
        evolve_sense.sense(lambda s, p, m, e: published.append(m) or {"seq": 1}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(len(published), 1)
        self.assertTrue((evolve_dir / "CURSOR_SENSE").exists())
        self.assertEqual((evolve_dir / "CURSOR_SENSE").read_text().strip(), "1")

        # simulate a restart: a FRESH call to sense() (a new SenseThread run after the restart law's 1 s
        # backoff, creature/body.py:SenseThread.run) must read the DISK cursor, not start over.
        evolve_sense.sense(lambda s, p, m, e: published.append(m) or {"seq": 2}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(len(published), 1, "a duplicate publish would let Mind._consume_proposal adopt the SAME mutation as a SECOND epoch")

    def test_no_evolve_dir_yet_publishes_nothing(self) -> None:
        root = _tmp()
        published = []
        evolve_sense.sense(lambda s, p, m, e: published.append(m) or {"seq": 1}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(published, [])

    def test_ten_or_more_proposals_publish_in_numeric_order_none_skipped(self) -> None:
        """A regression test for a real bug found in review: `sorted(glob(...))` sorts filenames
        LEXICOGRAPHICALLY, and "PROPOSAL-10.json" < "PROPOSAL-2.json" bytewise ('1' < '2') -- publishing
        in that raw order would advance the cursor past 10 and then skip 2..9 forever (the exact class of
        bug creature/senses/game.py's own zero-padded manifest names exist to avoid)."""
        root = _tmp()
        evolve_dir = root / "evolve"
        evolve_dir.mkdir(parents=True)
        for n in range(1, 13):   # 1..12 -- crosses the '9' -> '10' boundary where lexicographic order breaks
            (evolve_dir / f"PROPOSAL-{n}.json").write_text(json.dumps({"no": n, "verdict": "PASS"}))
        published = []
        evolve_sense.sense(lambda s, p, m, e: published.append(m["no"]) or {"seq": m["no"]}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(published, list(range(1, 13)), "every proposal must publish exactly once, in numeric order")

    def test_a_torn_json_file_is_retried_not_skipped(self) -> None:
        """A proposal file read mid-write (worker crash between open() and write()) must not be
        permanently skipped — the next scan (after the worker's own atomic replace) picks it up."""
        root = _tmp()
        evolve_dir = root / "evolve"
        evolve_dir.mkdir(parents=True)
        (evolve_dir / "PROPOSAL-1.json").write_text("{not valid json")
        published = []
        evolve_sense.sense(lambda s, p, m, e: published.append(m) or {"seq": 1}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(published, [])
        self.assertFalse((evolve_dir / "CURSOR_SENSE").exists(), "an unreadable file must never advance the cursor")
        (evolve_dir / "PROPOSAL-1.json").write_text(json.dumps({"no": 1, "verdict": "PASS"}))
        evolve_sense.sense(lambda s, p, m, e: published.append(m) or {"seq": 1}, _FakeStopEvent(), root, poll_period=0.01)
        self.assertEqual(len(published), 1)


class TestStartStopWorker(unittest.TestCase):
    """A minimal subprocess round-trip: `main()` exits 0 immediately when EVOLVE is not declared on the
    given genome (tools/evolve.py's own early-out), so this proves start/stop plumbing without needing a
    full life running."""

    def test_start_and_stop_a_worker_with_no_evolve_gene(self) -> None:
        root = _tmp()
        genome_path = root / "GENOME.genome"
        ROOT = Path(__file__).resolve().parent.parent.parent
        genome_path.write_text((ROOT / "genome" / "LIFE.genome").read_text())   # no EVOLVE line
        (root / "tape").mkdir(parents=True, exist_ok=True)
        stop_file = root / "evolve" / "STOP"
        proc = evolve_sense.start_worker(root, genome_path, stop_file, poll_period=1.0)
        try:
            rc = proc.wait(timeout=30)
            self.assertEqual(rc, 0)
        finally:
            evolve_sense.stop_worker(proc, stop_file=stop_file, timeout=5.0)

    def test_stop_worker_kills_by_pid_never_a_pattern(self) -> None:
        """#193/#197: stop_worker must terminate THIS process object, never `pkill -f` a pattern (which
        could match the CALLER's own command line)."""
        root = _tmp()
        genome_path = root / "GENOME.genome"
        ROOT = Path(__file__).resolve().parent.parent.parent
        base = (ROOT / "genome" / "LIFE.genome").read_text()
        genome_path.write_text(base + "\nEVOLVE every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n")
        (root / "tape").mkdir(parents=True, exist_ok=True)
        stop_file = root / "evolve" / "STOP"
        proc = evolve_sense.start_worker(root, genome_path, stop_file, poll_period=1.0)
        time.sleep(1.0)   # let the worker enter its poll loop
        self.assertIsNone(proc.poll(), "the worker should still be running (EVOLVE is declared, no --stop-file yet)")
        evolve_sense.stop_worker(proc, stop_file=stop_file, timeout=15.0)
        self.assertIsNotNone(proc.poll(), "stop_worker must have terminated the process")


class TestWriterSweepCatchesAnEvolveOffender(unittest.TestCase):
    """RULES FOR EVERY BUILDER: "tools/gate_g4.py step 1 (the writer sweep) must stay green and you ADD a
    planted offender for your new module." `creature/senses/evolve.py` is itself already swept clean by
    `tools/gate_g4.py gate1` (it globs `creature/senses/*.py`, 0 offenders, proven above by running the
    real gate); this is the brief's own SECOND, NAMED control: an "evolve worker"-shaped file (importing
    Organism the way a sense module never may, and writing under `state/`) must be CAUGHT by the SAME
    `sweep()` gate1 itself calls — proven directly, not by re-running the whole gate script."""

    def test_an_evolve_flavoured_sense_that_imports_organism_is_caught(self) -> None:
        d = Path(tempfile.mkdtemp())
        plant = d / "senses" / "evolve_offender.py"
        plant.parent.mkdir(parents=True)
        plant.write_text(
            "from genome.machinery import Organism\n"
            "def sense(publish, stop_event, root):\n"
            "    pass\n"
        )
        offenders = sweep([plant])
        self.assertTrue(offenders, "a fake sense module importing Organism must be CAUGHT")
        self.assertIn("imports Organism", offenders[0][2])

    def test_an_evolve_flavoured_worker_that_writes_state_is_caught(self) -> None:
        d = Path(tempfile.mkdtemp())
        plant = d / "senses" / "evolve_offender2.py"
        plant.parent.mkdir(parents=True)
        plant.write_text(
            "from pathlib import Path\n"
            "def sense(publish, stop_event, root):\n"
            "    with open(Path(root) / 'state' / 'organism.npz', 'wb') as h:\n"
            "        h.write(b'evolve-worker-should-never-write-here')\n"
        )
        offenders = sweep([plant])
        self.assertTrue(offenders, "a fake sense module writing under state/ must be CAUGHT")
        self.assertIn("forbidden dir", offenders[0][2])

    def test_the_real_evolve_sense_module_has_zero_offenders(self) -> None:
        real = Path(evolve_sense.__file__)
        self.assertEqual(sweep([real]), [], "creature/senses/evolve.py itself must stay clean")


if __name__ == "__main__":
    unittest.main()
