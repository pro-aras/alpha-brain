# edit: Claude (Fable 5.1), 2026-09-23 03:43 +0400 — RE-PIN at ALPHA 4 integration: G's declared hash-law change (state_hash over the live prefix of alive/misfires) moved every genome's digest once; the new digest read identically from the genome suite, the creature suite and gate 2 on the merged tree 6ff2204 (three witnesses).
"""test_pin_skeleton.py — B0: THE PIN. G4-skeleton.genome's toy-dev hash_dev must never move.
# edit: Claude (Fable 5.1), 2026-09-21 20:50 +0400 — PIN_HASH_DEV moved to the live-block digest b0531503… (Builder F's state_hash; the old d4b5c6b8… digest is the legacy road).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 21:32 +0400 — B0 (docs/briefs/G4-BUILDER-B-GENES.md):
independently re-derives the orchestrator's G4-2 pin (docs/G4-PREREG.md §4, read at git 9a36475:
hash_dev = 44f6fa81f9c21c549036a44f89dfb04276cd07aaec9565ccbd13ef75a11bcc00 on toy_streams' 660 dev
canvases, 2,640 moments, ~9.9 s) and asserts it holds at every later commit. A gene declared but OFF
moves nothing (SOLUTIONS #226) — this test is that control, run before and after every change.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from genome import world
from genome.machinery import parse_genome
from genome.run_g1 import PLANT_SHOWINGS, glance_held, glance_rows, live, toy_streams

ROOT = Path(__file__).resolve().parent.parent.parent
GENOME_PATH = ROOT / "genome" / "G4-skeleton.genome"

PIN_HASH_DEV = "44f6fa81f9c21c549036a44f89dfb04276cd07aaec9565ccbd13ef75a11bcc00"
PIN_MOMENTS = 2640
PIN_DEV_CANVASES = 660


class TestPinSkeleton(unittest.TestCase):
    """The G4-2 gate's own control: run_g1.live(...)["hash_dev"] on G4-skeleton.genome's toy dev
    canvases (glanced by glance_rows(dev, genome, "surprise")), with_arr2=False, with_plant=False,
    ask_at_dev=False — must equal the orchestrator's independently-read pin, every commit. The genome
    file is read fresh (never cached) so an accidental edit to G4-skeleton.genome itself is caught too.
    """

    def test_hash_dev_unchanged(self) -> None:
        genome = parse_genome(GENOME_PATH.read_text())
        things, arr2, dev, held, a2, plant, shuffle_words, n_checked = toy_streams(genome, PLANT_SHOWINGS)
        self.assertEqual(len(dev), PIN_DEV_CANVASES, "toy_streams' dev canvas count moved")
        dev_g = glance_rows(dev, genome, "surprise")
        held_g = glance_held(held, genome, "surprise")
        rec = live(genome, dev_g, [], [], things, arr2, held_g, world.THING_NEVER,
                   with_arr2=False, with_plant=False, ask_at_dev=False)
        self.assertEqual(rec["at_dev"]["moments"], PIN_MOMENTS, "moment count moved")
        self.assertEqual(
            rec["hash_dev"], PIN_HASH_DEV,
            "G4-skeleton.genome's dev hash moved — a gene declared but OFF must move nothing (#226); "
            "stop and find why before continuing (PREREG task B0, G4-2's control)",
        )


if __name__ == "__main__":
    unittest.main()
