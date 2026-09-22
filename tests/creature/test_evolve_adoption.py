# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE), brief
# item 3: adoption at the SLEEP boundary.
"""tests/creature/test_evolve_adoption.py

A synthetic tape carrying a PASS "proposal" row: the mind adopts at the next SLEEP boundary (writes
GENOME.v1.genome, re-parses self.genome/self.org.g, journals the epoch as a MIND row — never a top-level
"event" key), and TWO independent replays from birth are byte-identical to EACH OTHER and to the live
mind's own journal, epoch row included (the brief's own test requirement, item 3: "two replays byte-
identical including the epoch event"). A REFUSED proposal never adopts. PARK.after/CURIOSITY.interests
(cached at construction, unlike every other mutable gene) are live-patched. `Mind.resume` is epoch-aware.
"""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from creature.genes import apply_mutation
from creature.mind import Mind
from creature.replay import compare, read_mind_journal, run_replay
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parent.parent.parent
BASE = (ROOT / "tests" / "creature" / "G4-wave2-sleep-test.genome").read_text()
EVOLVE_FIXTURE = ROOT / "tests" / "creature" / "G4-evolve-test.genome"


def _write_fixture() -> None:
    """A NEW fixture file under tests/creature/ (never an edit to the base one, test_sleep_boundary.py's
    own technique): SLEEP+FAST (from the base) plus CURIOSITY, PARK and EVOLVE."""
    extra = (
        "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
        "PARK     after 3 identical dead-ends reopen on new-sense\n"
        "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar\n"
    )
    EVOLVE_FIXTURE.write_text(BASE.rstrip("\n") + "\n" + extra)


_write_fixture()


def _png(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _build_tape(root: Path, proposal: Optional[dict] = None, proposal_at: int = 20, n: int = 90, seed: int = 4242) -> None:
    """90 canvases -- crosses the fixture's SLEEP boundary (every 40 moments) several times. `proposal`,
    when given, is published as ONE "proposal" tape row at canvas index `proposal_at` (well before the
    tape ends, so at least one later eye row crosses a boundary and can adopt it -- adoption only ever
    happens on an eye row's own call to `_maybe_sleep`, never on the proposal row itself)."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle", "diamond"]
    for i in range(n):
        thing = things[i % len(things)]
        rgb, _truth = world.render_canvas(thing, rng)
        moment = f"m{i:05d}"
        if i % 7 != 0:
            tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
        tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png")
        if proposal is not None and i == proposal_at:
            tape.publish("proposal", json.dumps(proposal).encode("utf-8"), proposal, "json")


def _pass_proposal(gene: str, value: object, no: int = 1) -> dict:
    fixture_text = EVOLVE_FIXTURE.read_text()
    mutant_text = apply_mutation(fixture_text, gene, value)
    return {"no": no, "epoch": 0, "gene": gene, "value": value, "mutant_genome_text": mutant_text,
            "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.95},
            "verdict": "PASS", "reason": "q1_seen improved"}


class TestAdoptionAtSleepBoundary(unittest.TestCase):
    def test_pass_proposal_adopts_at_the_next_boundary(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("KWTA.k", 7)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.evolve_epoch, 1)
        self.assertEqual(mind.genome.kwta, 7)
        self.assertEqual(mind.org.g.kwta, 7, "the ORGANISM's own live genome reference must also update")
        self.assertTrue((root / "GENOME.v1.genome").exists())
        self.assertEqual((root / "GENOME.v1.genome").read_text(), proposal["mutant_genome_text"])

    def test_epoch_row_is_a_mind_row_never_a_top_level_event_key(self) -> None:
        """PREREG §2.4's own discriminator: the BODY writes rows with a top-level "event" key; the MIND
        never does. The epoch row is journaled by the MIND (Mind._maybe_adopt_evolve_proposal), so it must
        survive `creature.replay.read_mind_journal`'s own filter (`"event" not in r`) — else REPLAY's own
        byte-identity machinery would silently never compare it."""
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("KWTA.k", 7)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        rows = []
        for f in sorted((root / "journal").glob("*.jsonl")):
            rows.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
        epoch_rows = [r for r in rows if "epoch" in r]
        self.assertEqual(len(epoch_rows), 1)
        self.assertNotIn("event", epoch_rows[0])
        # read_mind_journal's own filter is `"event" not in r` -- applied here directly on the in-memory
        # rows (its file-reading half is exercised by TestReplayIdentity below, on a REAL replay output).
        kept = [r for r in rows if "event" not in r]
        self.assertEqual(len([r for r in kept if "epoch" in r]), 1, "the epoch row must survive read_mind_journal's own filter")
        e = epoch_rows[0]["epoch"]
        self.assertEqual(e["epoch"], 1)
        self.assertEqual(e["gene"], "KWTA.k")
        self.assertEqual(e["value"], 7)
        self.assertIsInstance(e["genome_sha"], str)
        self.assertEqual(len(e["genome_sha"]), 64)

    def test_refused_proposal_never_adopts(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = {"no": 1, "epoch": 0, "gene": "KWTA.k", "value": 7, "mutant_genome_text": "unused",
                    "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.80},
                    "verdict": "REFUSED", "reason": "q1_seen regressed"}
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.evolve_epoch, 0)
        self.assertEqual(mind.genome.kwta, 5)
        self.assertFalse((root / "GENOME.v1.genome").exists())

    def test_no_proposal_at_all_never_adopts(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, proposal=None)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.evolve_epoch, 0)
        self.assertEqual(mind.evolve_proposals_seen, 0)

    def test_park_after_is_live_patched(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("PARK.after", 7)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        self.assertEqual(mind.park.n, 3)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.park.n, 7, "Park caches its own gene value at construction -- adoption must live-patch it")

    def test_curiosity_interests_is_live_patched(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("CURIOSITY.interests", 77)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        self.assertEqual(mind.interests.n, 50)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.interests.n, 77, "Interests caches its own gene value at construction -- adoption must live-patch it")

    def test_a_second_pass_proposal_produces_a_second_epoch(self) -> None:
        root = Path(tempfile.mkdtemp())
        p1 = _pass_proposal("KWTA.k", 7, no=1)
        tape = Tape(root)
        rng = np.random.default_rng(4242)
        things = ["circle", "square", "triangle", "diamond"]
        for i in range(150):
            thing = things[i % len(things)]
            rgb, _truth = world.render_canvas(thing, rng)
            moment = f"m{i:05d}"
            if i % 7 != 0:
                tape.publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "test", "word": thing}, "txt")
            tape.publish("eye", _png(rgb), {"moment": moment, "source": "test"}, "png")
            if i == 20:
                tape.publish("proposal", json.dumps(p1).encode("utf-8"), p1, "json")
            if i == 80:
                # the SECOND mutation is drawn from the ALREADY-MUTATED text (kwta=7), never the birth text
                # -- exactly what a live worker reading the shadow's own current genome_text would produce.
                p2_text = apply_mutation(p1["mutant_genome_text"], "DELTA.lr", 0.09)
                p2 = {"no": 2, "epoch": 1, "gene": "DELTA.lr", "value": 0.09, "mutant_genome_text": p2_text,
                      "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.95}, "verdict": "PASS", "reason": "ok"}
                tape.publish("proposal", json.dumps(p2).encode("utf-8"), p2, "json")
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertEqual(mind.evolve_epoch, 2)
        self.assertEqual(mind.genome.kwta, 7)
        self.assertAlmostEqual(mind.genome.lr, 0.09)
        self.assertTrue((root / "GENOME.v1.genome").exists())
        self.assertTrue((root / "GENOME.v2.genome").exists())


class TestReplayIdentity(unittest.TestCase):
    """Brief item 3's own test: "a synthetic tape with a PASS proposal row: two replays byte-identical
    including the epoch event"."""

    def _tape_all(self, root: Path) -> Path:
        tape_files = sorted((root / "tape").glob("*.jsonl"))
        tape_all = root / "tape" / "ALL.jsonl"
        tape_all.write_text("".join(f.read_text() for f in tape_files))
        return tape_all

    def test_two_replays_from_birth_are_byte_identical_including_the_epoch_row(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("KWTA.k", 7)
        _build_tape(root, proposal=proposal)
        tape_all = self._tape_all(root)
        j1 = run_replay(EVOLVE_FIXTURE, tape_all, Path(tempfile.mkdtemp()) / "r1")
        j2 = run_replay(EVOLVE_FIXTURE, tape_all, Path(tempfile.mkdtemp()) / "r2")
        r1, r2 = read_mind_journal(j1), read_mind_journal(j2)
        self.assertIsNone(compare(r1, r2))
        epoch_rows = [r for r in r1 if "epoch" in r]
        self.assertEqual(len(epoch_rows), 1)
        self.assertEqual(epoch_rows[0]["epoch"]["gene"], "KWTA.k")

    def test_replay_matches_the_live_minds_own_journal(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("KWTA.k", 7)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        live_rows = []
        for f in sorted((root / "journal").glob("*.jsonl")):
            live_rows.extend(json.loads(l) for l in f.read_text().splitlines() if l.strip())
        live_mind_rows = [r for r in live_rows if "event" not in r]
        tape_all = self._tape_all(root)
        j = run_replay(EVOLVE_FIXTURE, tape_all, Path(tempfile.mkdtemp()) / "r")
        replayed = read_mind_journal(j)
        self.assertIsNone(compare(replayed, live_mind_rows))

    def test_refused_proposal_no_epoch_on_replay_either(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = {"no": 1, "epoch": 0, "gene": "KWTA.k", "value": 7, "mutant_genome_text": "unused",
                    "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.80},
                    "verdict": "REFUSED", "reason": "q1_seen regressed"}
        _build_tape(root, proposal=proposal)
        tape_all = self._tape_all(root)
        j = run_replay(EVOLVE_FIXTURE, tape_all, Path(tempfile.mkdtemp()) / "r")
        replayed = read_mind_journal(j)
        self.assertEqual([r for r in replayed if "epoch" in r], [])


class TestResumeEpochAware(unittest.TestCase):
    def test_resume_picks_up_the_latest_adopted_genome(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = _pass_proposal("KWTA.k", 7)
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        mind.snapshot()
        self.assertEqual(mind.evolve_epoch, 1)
        mind2, _last_seq = Mind.resume(EVOLVE_FIXTURE, root)
        self.assertEqual(mind2.evolve_epoch, 1)
        self.assertEqual(mind2.genome.kwta, 7)
        self.assertEqual(mind2.org.g.kwta, 7)
        self.assertEqual(mind2.park.n, 3)   # unaffected gene: still the fixture's own value

    def test_resume_with_no_epoch_uses_the_birth_genome(self) -> None:
        root = Path(tempfile.mkdtemp())
        _build_tape(root, proposal=None)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)
        mind.snapshot()
        mind2, _last_seq = Mind.resume(EVOLVE_FIXTURE, root)
        self.assertEqual(mind2.evolve_epoch, 0)
        self.assertEqual(mind2.genome.kwta, 5)


class TestMalformedProposalRefusesNotCrashes(unittest.TestCase):
    def test_a_pass_proposal_whose_mutant_text_does_not_parse_is_refused_not_adopted(self) -> None:
        root = Path(tempfile.mkdtemp())
        proposal = {"no": 1, "epoch": 0, "gene": "KWTA.k", "value": 7,
                    "mutant_genome_text": "KWTA garbage not a number\nnonsense line",
                    "incumbent": {"q1_seen": 0.9}, "mutant": {"q1_seen": 0.95},
                    "verdict": "PASS", "reason": "ok"}
        _build_tape(root, proposal=proposal)
        mind = Mind(EVOLVE_FIXTURE, root)
        for row in read_tape(root):
            mind.consume(row)   # must not raise
        self.assertEqual(mind.evolve_epoch, 0)
        self.assertEqual(mind.genome.kwta, 5)


if __name__ == "__main__":
    unittest.main()
