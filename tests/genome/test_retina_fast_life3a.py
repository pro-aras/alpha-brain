# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:5x +0400 -- docs/briefs/G5-J-BIND-COLOUR-RETINA.md
# item 3/4: byte-identity of genome/retina_fast.py's analyse_fast (F's module, branch g5-repairs, copied
# verbatim into tests/genome/test_retina_fast.py's sibling module here) against the pinned oracle's own
# analyse(), over EVERY eye canvas of life 3a's real closed-life tape (F proved life 2's; this branch's
# own retina identity bar names life 3a per the brief). Read-only on
# /data/dev/genome/run-g4-life3a-20260921-1314/ -- never writes there, never touches /data/dev/genome.
from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from genome import gaze as ggaze
from genome import retina_fast as rfast

LIFE3A_TAPE = Path("/data/dev/genome/run-g4-life3a-20260921-1314/tape/2026-09-21.jsonl")


def _eye_payloads():
    base = LIFE3A_TAPE.parent
    out = []
    for line in LIFE3A_TAPE.read_text().splitlines():
        r = json.loads(line)
        if r["sense"] == "eye":
            out.append(base / r["payload"])
    return out


@unittest.skipUnless(LIFE3A_TAPE.exists(), "life 3a's closed run root is not present on this box")
class TestRetinaFastLife3aIdentity(unittest.TestCase):
    def test_every_eye_canvas_byte_identical(self) -> None:
        oracle = rfast.oracle()
        paths = _eye_payloads()
        self.assertGreater(len(paths), 100, "life 3a's tape should carry far more than 100 eye rows")
        checked = 0
        max_delta = 0.0
        for p in paths:
            rgb = np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8)
            frame = ggaze.frame_of(rgb)
            an_old = oracle.analyse(frame)
            an_fast = rfast.analyse_fast(frame)
            sal_old = np.asarray(an_old["saliency"])
            sal_fast = np.asarray(an_fast["saliency"])
            if not np.array_equal(sal_old, sal_fast):
                self.fail(f"saliency mismatch on {p.name}")
            for ch in oracle.CHANNELS:
                a = np.asarray(an_old["channels"][ch]); b = np.asarray(an_fast["channels"][ch])
                self.assertTrue(np.array_equal(a, b), f"channel {ch} mismatch on {p.name}")
            checked += 1
        print(f"[life3a retina identity] {checked}/{len(paths)} eye canvases byte-identical, max|delta|={max_delta}")
        self.assertEqual(checked, len(paths))

    def test_negative_control_would_have_caught_a_divergence(self) -> None:
        """The check above can actually fail: same planted-corruption control as test_retina_fast.py,
        on the FIRST real life-3a canvas, so this file's own identity check is not vacuous."""
        p = _eye_payloads()[0]
        rgb = np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8)
        frame = ggaze.frame_of(rgb)
        an_fast = rfast.analyse_fast(frame)
        corrupted = np.asarray(an_fast["saliency"], dtype=np.float64).copy()
        corrupted[0, 0] += 1e-9
        oracle = rfast.oracle()
        an_old = oracle.analyse(frame)
        self.assertFalse(np.array_equal(np.asarray(an_old["saliency"]), corrupted), "negative control not planted correctly")


if __name__ == "__main__":
    unittest.main()
