# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; test-first): creature/senses/video.py, THE VIDEO WORLD SENSE — the frozen sha-manifest
# shelf streamed as the life's own rows on the declared cadence, LOOPING at the shelf's end with the count
# journaled, provenance video/video-caption and the tape's `video` meta carried untouched. A pure SENSE beside
# scene.py's form: writes only through publish, its own cursor and the journal events the body hands it.
"""tests/creature/test_sense_video.py — THE VIDEO WORLD SENSE (PREREG-ALPHA-6 §1.2/§2 B2).

The fixture is tests/creature/_video_shelf.py's DECLARED TOY SHELF (6 synthetic frames + a tiny caption stream —
never the real shelf). The pins: the tape's rows published in its own order with payloads and metas untouched;
one canvas per declared `every_s`; the loop count journaled at every wrap; the cursor resume never republishing
a durable canvas; and the law's G-PLANT discipline — a tampered shelf file CAUGHT by the manifest, an unnamed
file CAUGHT, a row the manifest doesn't name NEVER published (the sense refuses by name before any row goes
out), a row whose sha left the manifest's CAUGHT, a row of any other sense REFUSED by name."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Dict, List

from creature.senses import video as V
from tests.creature import _video_shelf as F


class Collect:
    """The publish callable: rows in, a seq back — plus the eye-row publish times for the cadence pin."""

    def __init__(self) -> None:
        self.rows: List[Dict[str, object]] = []
        self.eye_times: List[float] = []

    def __call__(self, sense: str, payload: bytes, meta: Dict[str, object], ext: str) -> Dict[str, object]:
        row = {"seq": len(self.rows) + 1, "sense": sense, "payload": payload, "meta": dict(meta), "ext": ext}
        self.rows.append(row)
        if sense == "eye":
            self.eye_times.append(time.monotonic())
        return row


class _Shelf(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="video-sense-"))
        cls.shelf = cls.tmp / "shelf"
        cls.built = F.build_toy_tape(cls.shelf)
        V.write_manifest(cls.shelf)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def fresh(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="video-root-", dir=self.tmp))
        return d

    def run_sense(self, root: Path, seconds: float, every_s: float = 0.02, events=None):
        pub = Collect()
        stop = threading.Event()
        cfg = {"shelf": str(self.shelf), "every_s": every_s, "loop": True, "manifest": "sha256"}
        progress = V.Progress()
        t = threading.Thread(target=V.sense, kwargs=dict(publish=pub, stop_event=stop, root=root, cfg=cfg,
                                                         progress=progress, events=events),
                             daemon=True)
        t.start()
        time.sleep(seconds)
        stop.set()
        t.join(timeout=5)
        return pub, progress


class TheRowsAreTheTapesOwn(_Shelf):
    def test_the_first_pass_publishes_the_tape_in_order_payloads_and_metas_untouched(self) -> None:
        root = self.fresh()
        pub, _p = self.run_sense(root, seconds=0.35, every_s=0.02)
        want = F.rows_expected()
        got = pub.rows[: len(want)]
        self.assertGreaterEqual(len(pub.rows), len(want), "one full pass published inside the window")
        self.assertEqual([(r["sense"], r["meta"]) for r in got], [(s, m) for s, m in want])
        # the payload bytes are the shelf's own (the eye rows the tape's own payload PNGs)
        for r, (s, _m) in zip(got, want):
            rel = f"payload/{r['seq']:09d}." + ("png" if s == "eye" else "txt")
            self.assertEqual(r["payload"], self.built["payloads"][rel])
            self.assertEqual(r["ext"], "png" if s == "eye" else "txt")

    def test_one_canvas_per_declared_cadence(self) -> None:
        root = self.fresh()
        pub, _p = self.run_sense(root, seconds=0.5, every_s=0.05)
        self.assertGreaterEqual(len(pub.eye_times), 4, "the presence count")
        gaps = [b - a for a, b in zip(pub.eye_times, pub.eye_times[1:])]
        self.assertTrue(all(g >= 0.04 for g in gaps), gaps)

    def test_the_loop_wraps_and_the_count_is_journaled(self) -> None:
        root = self.fresh()
        events: List[Dict[str, object]] = []
        pub, progress = self.run_sense(root, seconds=0.6, every_s=0.02, events=events.append)
        n = len(F.rows_expected())
        self.assertGreater(len(pub.rows), n + 2, "the shelf wrapped inside the window")
        self.assertEqual([(r["sense"], r["meta"]) for r in pub.rows[n: 2 * n]],
                         [(r["sense"], r["meta"]) for r in pub.rows[:n]], "the second pass is the first, row for row")
        loops = [e for e in events if e.get("event") == "video_loop"]
        self.assertGreaterEqual(len(loops), 1)
        self.assertEqual(loops[0]["loop"], 1)
        self.assertEqual(loops[0]["canvases"], 6)
        snap = progress.snapshot()
        self.assertGreaterEqual(snap["loop"], 1)
        self.assertEqual(snap["ended"], False)

    def test_a_restart_resumes_from_the_cursor_never_republishing_a_durable_canvas(self) -> None:
        root = self.fresh()
        pub1, _p = self.run_sense(root, seconds=0.18, every_s=0.02)
        n1 = len(pub1.rows)
        self.assertGreaterEqual(n1, 3, "the first run published a few canvases")
        cur = json.loads((root / "video" / "VIDEO-CURSOR").read_text())
        pub2, _p2 = self.run_sense(root, seconds=0.3, every_s=0.02)
        self.assertGreaterEqual(len(pub2.rows), 1)
        # the second run's first row is the cursor's next row — never a durable one again
        want = F.rows_expected()
        idx = (cur["loop"] * len(want)) + cur["row"]
        exp = [want[i % len(want)] for i in range(idx, idx + len(pub2.rows))]
        self.assertEqual([(r["sense"], r["meta"]) for r in pub2.rows], [(s, m) for s, m in exp])


class TheManifestDiscipline(_Shelf):
    def _expect_refusal(self, mutate, needle: str) -> None:
        shelf = self.tmp / ("shelf-" + str(next(self._n)))
        F.build_toy_tape(shelf)
        V.write_manifest(shelf)
        mutate(shelf)
        root = self.fresh()
        pub = Collect()
        stop = threading.Event()
        with self.assertRaises(V.VideoShelfError) as e:
            V.sense(publish=pub, stop_event=stop, root=root,
                    cfg={"shelf": str(shelf), "every_s": 0.01, "loop": True, "manifest": "sha256"})
        self.assertIn(needle, str(e.exception))
        self.assertEqual(pub.rows, [], "nothing is published once the shelf's honesty is in doubt")

    _n = iter(range(1000))

    def test_a_tampered_shelf_file_is_caught_by_the_manifest(self) -> None:
        def m(shelf: Path) -> None:
            p = shelf / "payload" / "000000002.png"
            b = bytearray(p.read_bytes())
            b[len(b) // 2] ^= 1                      # the law's own plant: one flipped byte
            p.write_bytes(bytes(b))
        self._expect_refusal(m, "000000002.png")

    def test_an_unnamed_shelf_file_is_caught(self) -> None:
        def m(shelf: Path) -> None:
            (shelf / "payload" / "000000099.png").write_bytes(b"sneaked-in")
        self._expect_refusal(m, "000000099.png")

    def test_a_missing_shelf_file_is_caught(self) -> None:
        def m(shelf: Path) -> None:
            (shelf / "payload" / "000000001.txt").unlink()
        self._expect_refusal(m, "000000001.txt")

    def test_a_row_the_manifest_does_not_name_is_never_published(self) -> None:
        def m(shelf: Path) -> None:
            day = shelf / f"{F.DAY}.jsonl"
            rows = [json.loads(l) for l in day.read_text().splitlines()]
            rows[0]["payload"] = "payload/000000042.png"      # no such entry anywhere
            day.write_text("".join(json.dumps(r) + "\n" for r in rows))
            V.write_manifest(shelf)          # the manifest regenerated over the LYING tape: the ROW check's own case
        self._expect_refusal(m, "payload/000000042.png")

    def test_a_row_whose_sha_left_the_manifests_is_caught(self) -> None:
        def m(shelf: Path) -> None:
            day = shelf / f"{F.DAY}.jsonl"
            rows = [json.loads(l) for l in day.read_text().splitlines()]
            rows[0]["sha"] = "0" * 64
            day.write_text("".join(json.dumps(r) + "\n" for r in rows))
            V.write_manifest(shelf)          # internally consistent, and the row's sha still lies against it
        self._expect_refusal(m, "sha")

    def test_a_row_of_any_other_sense_is_refused_by_name(self) -> None:
        def m(shelf: Path) -> None:
            day = shelf / f"{F.DAY}.jsonl"
            rows = [json.loads(l) for l in day.read_text().splitlines()]
            rows.insert(0, dict(rows[1], seq=0, sense="body"))
            day.write_text("".join(json.dumps(r) + "\n" for r in rows))
            V.write_manifest(shelf)
        self._expect_refusal(m, "body")


class ThePureSense(unittest.TestCase):
    def test_the_module_never_reads_the_mind(self) -> None:
        import ast
        src = (Path(V.__file__)).read_text()
        tree = ast.parse(src)
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names.add(node.module or "")
            elif isinstance(node, ast.Import):
                names.update(a.name for a in node.names)
        for bad in ("creature.mind", "creature.body", "genome.machinery"):
            self.assertNotIn(bad, names)
        self.assertNotIn("Organism", src)


if __name__ == "__main__":
    unittest.main()
