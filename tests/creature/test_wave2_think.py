# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 01:45 +0400 — A11: THINK (PREREG §11.1 step 3).
#
# THINK's own gene clause ("THINK every <n> canvases") is not on master's parser at the time this was
# written, so no genome this worktree can parse ever sets `"THINK" in genome.declared` -- the gate this
# whole step lives behind can never fire through a real genome file today. RAISED, not worked around
# (docs/briefs/G4-BUILDER-A-BODY.md's own instruction for exactly this case). To still exercise the gated
# path end-to-end, these tests mutate the ALREADY-PARSED Genome object's `declared` dict in memory
# (`mind.genome.declared["THINK"] = {"every": N}`) -- this touches no file under genome/, only the Python
# object my own Mind instance already holds; it is the same technique as constructing any other in-memory
# test fixture, not a stub module.
#
# genome.curiosity and genome.think are ALSO not on master; the CURIOSITY-choice and belief-formation
# (kind "word") paths are gated with unittest.skipUnless(importable) rather than asserted.
from __future__ import annotations

import io
import json
import importlib
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from creature.mind import Mind, _CURIOSITY_AVAILABLE, _THINK_LAWS_AVAILABLE
from creature.tape import Tape, read_tape
from genome import world

ROOT = Path(__file__).resolve().parents[2]
GENOME_WITH_PARK = ROOT / "tests" / "creature" / "G4-wave2-park-test.genome"


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _write_park_genome() -> None:
    base = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()
    extra = "PARK     after 3 identical dead-ends reopen on new-sense\n"
    GENOME_WITH_PARK.write_text(base.rstrip("\n") + "\n" + extra)


_write_park_genome()


def _build_tape(root: Path, n: int = 60, seed: int = 321) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if i % 5 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "test"}, "png")


class TestGenomeParses(unittest.TestCase):
    def test_park_test_genome_declares_park_predict_fast(self) -> None:
        from genome.machinery import parse_genome
        g = parse_genome(GENOME_WITH_PARK.read_text())
        self.assertIn("PARK", g.declared); self.assertIn("PREDICT", g.declared); self.assertIn("FAST", g.declared)
        self.assertNotIn("THINK", g.declared, "THINK's own gene clause is not yet parseable — confirmed here, not assumed")

    def test_think_gene_line_parses_since_b9(self) -> None:
        # edit: Claude (Fable 5.1), 2026-09-19 23:21 +0400 — this test asserted the THINK line was UNPARSEABLE (true when A11 was written,
        # before Builder B's B9 landed on master); after the merge its premise flipped and it failed. Inverted: the gene parses
        # and lands in declared with its number (PREREG §11.2), so the step's gate can fire through a real genome file.
        from genome.machinery import parse_genome
        text = GENOME_WITH_PARK.read_text() + "THINK    every 10 canvases\n"
        g = parse_genome(text)
        self.assertEqual(g.declared.get("THINK"), {"every": 10})


class TestThinkPoolAndChoose(unittest.TestCase):
    def test_pool_has_sight_items_and_choose_picks_first_without_curiosity(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=40)
        mind = Mind(GENOME_WITH_PARK, root)
        for r in read_tape(root):
            mind.consume(r)
        self.assertIsNone(mind.interests, "no CURIOSITY declared -> no Interests object")

        pool = mind._think_pool()
        self.assertGreater(len(pool), 0, "a mixed worded/sight-only tape must produce a non-empty pool")
        kinds = {item["kind"] for item in pool}
        self.assertIn("sight", kinds, "sight-only episodes (word \"\") must appear in the pool")

        chosen = mind._think_choose(pool)
        self.assertEqual(chosen, pool[0], "no CURIOSITY declared -> the first item, deterministically")

    def test_pool_and_choose_are_deterministic_across_two_identical_runs(self) -> None:
        pools = []
        for _ in range(2):
            root = Path(tempfile.mkdtemp())
            _build_tape(root, n=40)
            mind = Mind(GENOME_WITH_PARK, root)
            for r in read_tape(root):
                mind.consume(r)
            pool = mind._think_pool()
            pools.append([(it["kind"], it["key"]) for it in pool])
        self.assertEqual(pools[0], pools[1])


class TestThinkWorkSightAndFile(unittest.TestCase):
    def test_sight_item_files_a_prediction_or_dead_ends_by_name(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=40)
        mind = Mind(GENOME_WITH_PARK, root)
        for r in read_tape(root):
            mind.consume(r)
        pool = mind._think_pool()
        sight_items = [it for it in pool if it["kind"] == "sight"]
        self.assertGreater(len(sight_items), 0)
        result = mind._think_work(sight_items[0])
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-0b (docs/G4-WAVE3-CLAUSES.md):
        # predict_file() is now gated on "FILE" in declared; GENOME_WITH_PARK (this fixture, above) never
        # declares FILE, so the sight road now dead-ends "no_file_gene" here — added to the accepted set,
        # nothing else in this test (or its fixture) touched.
        self.assertIn(result["outcome"], ("filed", "no_route", "episode_gone", "no_file_gene"))
        if result["outcome"] == "filed":
            self.assertEqual(len(mind._filed_predictions), 1)
            self.assertIn("route_word", result)

    def test_dead_ends_park_after_n_identical_reasons(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=10)
        mind = Mind(GENOME_WITH_PARK, root)
        for r in read_tape(root):
            mind.consume(r)
        self.assertIsNotNone(mind.park)
        # drive the SAME (want, reason) pair through Park directly -- PARK's own contract (genome/park.py,
        # already on master and tested by Builder B) is what THINK's dead-end path calls into.
        for _ in range(2):
            self.assertEqual(mind.park.answer("nowhere-thing", "no_route"), "open")
        self.assertEqual(mind.park.answer("nowhere-thing", "no_route"), "parked")
        self.assertEqual(mind.think_counters["parked"], 0, "these direct Park calls bypass _think_work's own counter")


class TestMaybeThinkJournaling(unittest.TestCase):
    """Exercises the FULL gated _maybe_think path by mutating the parsed Genome's declared dict in
    memory (see the module docstring) — no genome/ file involved."""

    def test_think_fires_every_n_canvases_and_journals(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=30)
        mind = Mind(GENOME_WITH_PARK, root)
        mind.genome.declared["THINK"] = {"every": 5}
        for r in read_tape(root):
            mind.consume(r)
        self.assertGreater(mind.think_counters["thinks"], 0)

        journal_files = sorted((root / "journal").glob("*.jsonl"))
        rows = [json.loads(l) for l in journal_files[0].read_text().splitlines() if l.strip()]
        think_rows = [r for r in rows if "think" in r]
        self.assertGreater(len(think_rows), 0)
        for tr in think_rows:
            t = tr["think"]
            self.assertIn("item", t); self.assertIn("kind", t); self.assertIn("outcome", t); self.assertIn("parked", t)

    def test_think_replay_is_deterministic(self) -> None:
        """Two independent minds fed the SAME tape with the SAME in-memory THINK gene must produce
        byte-identical think journal rows -- the rng THINK uses is seeded from the genome's own seed,
        never wall clock (the determinism law, unaffected by this step's addition)."""
        journals = []
        for _ in range(2):
            root = Path(tempfile.mkdtemp())
            _build_tape(root, n=30, seed=999)
            mind = Mind(GENOME_WITH_PARK, root)
            mind.genome.declared["THINK"] = {"every": 5}
            for r in read_tape(root):
                mind.consume(r)
            journal_files = sorted((root / "journal").glob("*.jsonl"))
            rows = [json.loads(l) for l in journal_files[0].read_text().splitlines() if l.strip()]
            journals.append([r["think"] for r in rows if "think" in r])
        self.assertEqual(journals[0], journals[1])


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not yet on master")
class TestThinkBeliefFormation(unittest.TestCase):
    def test_word_item_forms_a_belief_when_answered(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, n=80)
        mind = Mind(GENOME_WITH_PARK, root)
        for r in read_tape(root):
            mind.consume(r)
        pool = mind._think_pool()
        word_items = [it for it in pool if it["kind"] == "word"]
        if word_items:
            result = mind._think_work(word_items[0])
            # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-0b (docs/G4-WAVE3-CLAUSES.md):
            # think_laws.believe() is now gated on "BELIEF" in declared; GENOME_WITH_PARK (this fixture,
            # above) never declares BELIEF, so the word road now dead-ends "no_belief_gene" here — the
            # exact same fix already made to the sight-item test above for "no_file_gene", added to the
            # accepted set, nothing else in this test (or its fixture) touched.
            self.assertIn(result["outcome"], ("belief", "no_cell_answers", "episode_gone", "no_belief_gene"))


@unittest.skipUnless(_CURIOSITY_AVAILABLE, "genome.curiosity not yet on master")
class TestThinkCuriosityChoice(unittest.TestCase):
    def test_curiosity_declared_uses_interests_choose(self) -> None:
        pass  # placeholder for when genome.curiosity lands — CURIOSITY gene already parses today


if __name__ == "__main__":
    unittest.main()
