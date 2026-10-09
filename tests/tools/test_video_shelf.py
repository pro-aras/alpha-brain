# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…; test-first): tools/worlds/video_shelf.py, THE SHELF PROMOTION TOOL — the V3 bench
# tapes copied byte-exact into a life's shelf dir and the sha256 manifest written over them; the shelf is FROZEN
# at launch (additions between lives, never mid-life), so the tool refuses a non-empty target and its verify
# catches one flipped byte by name (the law's G-PLANT).
"""tests/tools/test_video_shelf.py — THE SHELF PROMOTION TOOL (PREREG-ALPHA-6 §2 B2).

The fixture is tests/creature/_video_shelf.py's toy tape standing in for the bench set; the real promotion
(records/open-world-4/bench/tape-curriculum → the life's shelf) is the same call with a bigger source. The
manifest's read/verify half is creature/senses/video.py's own (the sense and the tool share ONE form), so a
promoted shelf is exactly what the sense streams."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from creature.senses import video as V
from tests.creature import _video_shelf as F
from tools.worlds import video_shelf as P


class _Tmp(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="video-shelf-tool-"))
        self.src = self.tmp / "bench" / "tape-toy"
        F.build_toy_tape(self.src)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class ThePromotion(_Tmp):
    def test_it_copies_byte_exact_and_writes_the_manifest(self) -> None:
        shelf = self.tmp / "life" / "world" / "video-shelf"
        rec = P.promote(self.src, shelf)
        self.assertEqual((shelf / f"{F.DAY}.jsonl").read_bytes(), (self.src / f"{F.DAY}.jsonl").read_bytes())
        for rel, data in F.build_toy_tape(self.tmp / "again")["payloads"].items():
            self.assertEqual((shelf / rel).read_bytes(), data)
        man = shelf / "MANIFEST.sha256"
        self.assertTrue(man.is_file())
        entries = V.load_manifest(shelf)
        self.assertEqual(len(entries), len(rec["files"]))
        self.assertNotIn("MANIFEST.sha256", entries, "the manifest never names itself")
        self.assertEqual(rec["verify"], "ok")
        self.assertEqual(rec["rows"], len(F.rows_expected()))
        V.verify_shelf(shelf)   # raises on any doubt — passes clean here

    def test_two_promotions_of_the_same_source_write_identical_manifests(self) -> None:
        a, b = self.tmp / "a", self.tmp / "b"
        P.promote(self.src, a)
        P.promote(self.src, b)
        self.assertEqual((a / "MANIFEST.sha256").read_bytes(), (b / "MANIFEST.sha256").read_bytes())

    def test_it_refuses_a_non_empty_target(self) -> None:
        shelf = self.tmp / "occupied"
        shelf.mkdir()
        (shelf / "anything").write_text("x")
        with self.assertRaises(P.ShelfPromotionError) as e:
            P.promote(self.src, shelf)
        self.assertIn("not empty", str(e.exception))

    def test_it_refuses_a_missing_source(self) -> None:
        with self.assertRaises(P.ShelfPromotionError):
            P.promote(self.tmp / "nowhere", self.tmp / "shelf")

    def test_a_promoted_shelf_is_exactly_what_the_sense_streams(self) -> None:
        import threading
        import time
        shelf = self.tmp / "life" / "video-shelf"
        P.promote(self.src, shelf)
        pub_rows = []
        stop = threading.Event()
        root = self.tmp / "root"
        cfg = {"shelf": str(shelf), "every_s": 0.01, "loop": True, "manifest": "sha256"}

        def pub(sense, payload, meta, ext):
            pub_rows.append({"sense": sense, "payload": payload, "meta": meta, "ext": ext})
            return pub_rows[-1]

        t = threading.Thread(target=V.sense, kwargs=dict(publish=pub, stop_event=stop, root=root, cfg=cfg),
                             daemon=True)
        t.start()
        time.sleep(0.2)
        stop.set()
        t.join(timeout=5)
        want = F.rows_expected()
        self.assertGreaterEqual(len(pub_rows), len(want))
        self.assertEqual([(r["sense"], r["meta"]) for r in pub_rows[: len(want)]], [(s, m) for s, m in want])


class ThePlant(_Tmp):
    def test_one_flipped_byte_is_caught_by_name(self) -> None:
        shelf = self.tmp / "shelf"
        P.promote(self.src, shelf)
        p = shelf / "payload" / "000000002.png"
        b = bytearray(p.read_bytes())
        b[len(b) // 2] ^= 1                       # the law's own plant: one flipped byte
        p.write_bytes(bytes(b))
        with self.assertRaises(V.VideoShelfError) as e:
            V.verify_shelf(shelf)
        self.assertIn("000000002.png", str(e.exception))
        self.assertIn("sha256", str(e.exception))


if __name__ == "__main__":
    unittest.main()
