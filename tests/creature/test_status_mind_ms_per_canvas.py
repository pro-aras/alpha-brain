# edit: Claude (Fable 5.1), 2026-09-22 10:30 +0400 — STATUS.mind_ms_per_canvas_1min: the mind's cost in the unit the verdict reader's
# probe measures (ms per CANVAS = every row's consume time in the window ÷ eye rows consumed in the window). STATUS.mind_ms_median_1min
# (the per-ROW median, dominated by cheap ear/outcome/body rows) stays for the watch; it was never comparable to the probe (#162,
# found 2026-09-22 on the six 2 h smokes: 0.168 ms «vs» 13 ms). Written on EVERY status build (#164): None when no eye row fell in
# the window, a number otherwise — the key is always present.
from __future__ import annotations

import shutil
import tempfile
import time
import unittest
from pathlib import Path

from creature.body import Body

from .test_exam import GENOME_PATH


class TestStatusMindMsPerCanvas(unittest.TestCase):
    def _body(self) -> Body:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)   # no senses: the STATUS thread and the mind exist after start() (PREREG §2.5)
        body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        return body

    def test_per_canvas_is_all_rows_time_over_eye_rows_in_the_window(self) -> None:
        body = self._body()
        now = time.perf_counter()
        with body._status_lock:
            body._mind_times.clear()
            for sense, ms in (("ear", 0.1), ("eye", 12.0), ("outcome", 0.2), ("ear", 0.1), ("eye", 14.0), ("body", 0.05)):
                body._mind_times.append((now, ms, sense))
        st = body._build_status()
        self.assertIn("mind_ms_per_canvas_1min", st)
        self.assertAlmostEqual(st["mind_ms_per_canvas_1min"], (0.1 + 12.0 + 0.2 + 0.1 + 14.0 + 0.05) / 2, places=6)
        self.assertIn("mind_ms_median_1min", st)   # the per-row median stays for the watch

    def test_no_eye_row_in_the_window_writes_none_not_absence(self) -> None:
        body = self._body()
        now = time.perf_counter()
        with body._status_lock:
            body._mind_times.clear()
            body._mind_times.append((now, 0.1, "ear"))
        st = body._build_status()
        self.assertIn("mind_ms_per_canvas_1min", st)
        self.assertIsNone(st["mind_ms_per_canvas_1min"])

    def test_consume_records_the_row_sense(self) -> None:
        """the live road: _consume tags each timing with the row's sense (an eye row is one canvas). The mind's own consume is
        replaced by a no-op here so the row never reaches it (a raising consume would take the CRASH road, os._exit(3))."""
        body = self._body()
        body.mind.consume = lambda row: None
        with body._status_lock:
            body._mind_times.clear()
        body._consume({"seq": 1, "sense": "eye", "instant": "2026-09-22T06:30:00Z", "meta": {}, "sha256": "0" * 64})
        body._consume({"seq": 2, "sense": "ear", "instant": "2026-09-22T06:30:00Z", "meta": {}, "sha256": "0" * 64})
        with body._status_lock:
            tagged = list(body._mind_times)
        self.assertEqual([t[2] for t in tagged], ["eye", "ear"])


if __name__ == "__main__":
    unittest.main()
