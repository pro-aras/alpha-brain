# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:34 +0400 — BRAIN-IN-BODY: tools/brain/make_tape.py's own pin.
"""tests/creature/test_make_tape.py — make_tape.py writes the SAME rows (sense, meta, payload sha) as the threaded
`creature.senses.scene.sense()` for the same cfg, and is deterministic across two runs (the seat's fixed-clock amendment)."""
from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from creature.senses import scene as S
from tools.brain import make_tape as MT


def _cfg(train=8, sitting=("fresh",)):
    return {"seed": 20261101, "train": train, "sitting": list(sitting),
            "feed": {"mode": "max", "backlog": 10_000}, "utterance": "true"}


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class HarnessEquality(unittest.TestCase):
    """The tape-maker's own rows must equal, row for row, what the threaded sense() publishes through a
    Body-less recording harness for the SAME cfg (INTERFACE §5's own requirement)."""

    def test_make_tape_matches_the_threaded_sense_row_for_row(self):
        cfg = _cfg()
        recorded = []

        def publish(sense, payload, meta, ext):
            recorded.append((sense, meta, ext, _sha(payload)))
            return {"seq": len(recorded)}

        d = Path(tempfile.mkdtemp(prefix="make_tape_test_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        harness_root = d / "harness"
        harness_root.mkdir()

        # sense() checks stop_event.is_set() BEFORE each moment, so it must start UNSET; run it on its own
        # thread and stop it once the (finite) plan is exhausted — the trailing "wait for stop" loop then returns.
        stop = threading.Event()
        th = threading.Thread(target=S.sense, args=(publish, stop, harness_root, cfg, lambda: 0), daemon=True)
        th.start()
        th.join(timeout=10.0)
        stop.set()
        th.join(timeout=1.0)

        genome_path = self._genome(d)
        MT.make(genome_path, d / "root", limit_train=cfg["train"])
        made = []
        for row_line in sorted((d / "root" / "tape").glob("*.jsonl")):
            import json
            for line in row_line.read_text().splitlines():
                row = json.loads(line)
                payload_bytes = (d / "root" / "tape" / row["payload"]).read_bytes()
                made.append((row["sense"], row["meta"], "?", _sha(payload_bytes)))

        self.assertEqual(len(recorded), len(made))
        for (rs, rm, _re, rsha), (ms, mm, _me, msha) in zip(recorded, made):
            self.assertEqual(rs, ms)
            self.assertEqual(rm, mm)
            self.assertEqual(rsha, msha)

    def _genome(self, d: Path) -> Path:
        alpha4 = (REPO_ROOT / "genome" / "ALPHA4.genome").read_text()
        lines = ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; "
                 "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene\n"
                 "WORLD    scene seed 20261101; train 8; sitting fresh; feed max backlog 10000; utterance true\n")
        p = d / "smoke.genome"
        p.write_text(alpha4 + "\n" + lines)
        return p


class Determinism(unittest.TestCase):
    def test_two_makes_of_the_same_cfg_are_byte_identical(self):
        d = Path(tempfile.mkdtemp(prefix="make_tape_det_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        genome_path = HarnessEquality()._genome(d)
        MT.make(genome_path, d / "a", limit_train=5)
        MT.make(genome_path, d / "b", limit_train=5)
        fa = sorted((d / "a" / "tape").glob("*.jsonl"))
        fb = sorted((d / "b" / "tape").glob("*.jsonl"))
        self.assertEqual([p.name for p in fa], [p.name for p in fb])
        self.assertEqual(fa[0].read_bytes(), fb[0].read_bytes())
        self.assertEqual(len(fa), 1, "the whole made tape must land in a single day file")


if __name__ == "__main__":
    unittest.main()
