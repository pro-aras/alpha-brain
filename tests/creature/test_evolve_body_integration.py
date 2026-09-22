# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE): a real
# `Body` (never the CLI's own subprocess-of-a-subprocess) with EVOLVE armed exactly the way
# `creature/body.py:main` wires it (worker subprocess + in-process sense thread) — the ONE test that
# proves the whole chain (genome -> _declared_evolve_config -> start_worker -> tools/evolve.py's own CLI
# -> its shadow -> a checkpoint on disk) without waiting for a real 2/6 h cadence to elapse (the worker
# checkpoints on its VERY FIRST poll when no checkpoint exists yet — `last_checkpoint_at is None` — proven
# directly against `tools/evolve.py:main`'s own code, not paraphrased).
"""tests/creature/test_evolve_body_integration.py"""
from __future__ import annotations

import io
import json
import tempfile
import time
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.body import Body, _declared_evolve_config
from creature.tape import Tape
from genome import world
from genome.machinery import parse_genome

from .test_exam import GENOME_PATH

ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE = ROOT / "tests" / "creature" / "G4-evolve-test.genome"
if not FIXTURE.exists():
    base = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
    FIXTURE.write_text(base.rstrip("\n") + "\n" + (
        "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
        "PARK     after 3 identical dead-ends reopen on new-sense\n"
        "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"
    ))


def _png(rgb) -> bytes:
    buf = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(buf, format="PNG"); return buf.getvalue()


class TestBodyArmsEvolveWorker(unittest.TestCase):
    def test_declared_evolve_config_reads_the_gene(self) -> None:
        g = parse_genome(FIXTURE.read_text())
        cfg = _declared_evolve_config(g.declared)
        self.assertEqual(cfg, {"every_h": 6, "judge_h": 2})

    def test_no_evolve_line_arms_nothing(self) -> None:
        base = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
        g = parse_genome(base)
        self.assertIsNone(_declared_evolve_config(g.declared))

    def test_a_real_body_with_evolve_armed_produces_a_shadow_checkpoint(self) -> None:
        """Mirrors creature/body.py:main's own wiring (arm from declared['EVOLVE'], start_worker, add_sense)
        directly against `Body`, never through the CLI's own argv parsing (out of scope here) -- the same
        objects `main()` builds, in the same order."""
        root = Path(tempfile.mkdtemp())
        body = Body(root, FIXTURE)

        # pre-seed a little tape BEFORE start() -- Body.start() replays any existing backlog first, so the
        # shadow (started fresh by the worker subprocess) has real eye/ear rows to consume from its very
        # first poll.
        tape = Tape(root)
        rng = np.random.default_rng(4242)
        things = ["circle", "square", "triangle", "diamond"]
        for i in range(40):
            thing = things[i % len(things)]
            rgb, _truth = world.render_canvas(thing, rng)
            moment = f"m{i:05d}"
            if i % 7 != 0:
                tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
            tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png")

        declared = parse_genome(FIXTURE.read_text()).declared
        evolve_cfg = _declared_evolve_config(declared)
        self.assertIsNotNone(evolve_cfg)
        from creature.senses import evolve as evolve_sense
        evolve_stop_file = root / "evolve" / "STOP"
        evolve_stop_file.parent.mkdir(parents=True, exist_ok=True)
        evolve_proc = evolve_sense.start_worker(root, FIXTURE, evolve_stop_file, poll_period=1.0)
        import functools
        body.add_sense("evolve", functools.partial(evolve_sense.sense, root=root, poll_period=0.5))

        try:
            body.start()
            deadline = time.time() + 60.0
            checkpoints_dir = root / "evolve" / "checkpoints"
            shadow_state = root / "evolve" / "shadow" / "state" / "organism.npz"
            while time.time() < deadline:
                if checkpoints_dir.exists() and any(checkpoints_dir.iterdir()):
                    break
                time.sleep(1.0)
            self.assertTrue(checkpoints_dir.exists() and any(checkpoints_dir.iterdir()),
                             f"the worker never checkpointed within 60 s (poll_period=1.0 s, shadow_state exists={shadow_state.exists()})")
            self.assertTrue(shadow_state.exists())
            meta = json.loads(next(checkpoints_dir.iterdir()).joinpath("META.json").read_text())
            self.assertGreater(meta["last_seq"], 0)
        finally:
            body.stop()
            evolve_sense.stop_worker(evolve_proc, stop_file=evolve_stop_file, timeout=20.0)


class TestStatusExportsEvolveCounters(unittest.TestCase):
    """#164: a new counter is on STATUS on EVERY branch that writes STATUS -- 0 on a genome that never
    declares EVOLVE (matches tests/creature/test_status_births.py's own convention: a real Body, a real
    _build_status() call)."""

    def test_zero_on_a_genome_without_evolve(self) -> None:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.start()
        self.addCleanup(body.stop)
        st = body._build_status()
        self.assertIn("evolve_epoch", st)
        self.assertIn("evolve_proposals_seen", st)
        self.assertEqual(st["evolve_epoch"], 0)
        self.assertEqual(st["evolve_proposals_seen"], 0)

    def test_counts_a_consumed_proposal_and_an_adopted_epoch(self) -> None:
        """Tape rows written BEFORE `body.start()` are replayed by `Body.start()`'s own backlog road
        (`for row in read_tape(...): self._consume(row)`) -- the same real path a live process takes on
        every restart -- so this proves the counters reach STATUS through the ORDINARY consume road, not a
        hand-built Body."""
        import io
        import json
        from PIL import Image
        from creature.genes import apply_mutation

        root = Path(tempfile.mkdtemp())
        tape = Tape(root)
        rng = np.random.default_rng(4242)
        things = ["circle", "square", "triangle", "diamond"]
        mutant_text = apply_mutation(FIXTURE.read_text(), "KWTA.k", 7)
        for i in range(90):
            thing = things[i % len(things)]
            rgb, _truth = world.render_canvas(thing, rng)
            moment = f"m{i:05d}"
            if i % 7 != 0:
                tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
            buf = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
            tape.publish("eye", buf.getvalue(), {"moment": moment, "source": "test"}, "png")
            if i == 20:
                proposal = {"no": 1, "epoch": 0, "gene": "KWTA.k", "value": 7, "mutant_genome_text": mutant_text,
                            "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.95}, "verdict": "PASS", "reason": "ok"}
                tape.publish("proposal", json.dumps(proposal).encode("utf-8"), proposal, "json")
        body = Body(root, FIXTURE)
        body.start()
        self.addCleanup(body.stop)
        st = body._build_status()
        self.assertEqual(st["evolve_epoch"], 1)
        self.assertEqual(st["evolve_proposals_seen"], 1)


if __name__ == "__main__":
    unittest.main()
