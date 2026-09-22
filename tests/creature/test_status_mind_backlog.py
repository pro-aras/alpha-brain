# edit: Claude (Fable 5.1), 2026-09-22 10:47 +0400 — STATUS.mind_backlog_rows: the rows the senses have delivered that the mind has not yet
# consumed (the body's queue depth). Found 2026-09-22 10:3x +04: g5-seam-1 / L5 sat 6,917 / 5,941 rows behind their own tapes under the
# verdict readers' load, and NOTHING on any surface said so — STATUS.tape_rows is the mind's own position (last_seq), the watch reads
# motion, the reader's ALIVE reads sense gaps. A mind behind its world is a fact about the life (#164 on every write; #180: motion is
# not keeping up).
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body

from .test_exam import GENOME_PATH


class TestStatusMindBacklog(unittest.TestCase):
    def _body(self) -> Body:
        root = Path(tempfile.mkdtemp())
        body = Body(root, GENOME_PATH)
        body.start()
        self.addCleanup(lambda: (body.stop(), shutil.rmtree(root, ignore_errors=True)))
        return body

    def test_backlog_is_the_queue_depth(self) -> None:
        body = self._body()
        body.mind.consume = lambda row: None     # the rows must not reach the mind; only the depth is under test
        # the mind loop drains the queue on its own thread; freeze it by holding rows it cannot see: put after a stop of the loop
        body.stop_event.set()
        body._mind_thread.join(timeout=5.0)
        self.assertFalse(body._mind_thread.is_alive(), "the mind loop must have exited before rows are queued")
        for i in range(3):
            body.q.put({"seq": i, "sense": "eye", "meta": {}, "sha256": "0" * 64})
        st = body._build_status()
        self.assertIn("mind_backlog_rows", st)
        self.assertEqual(st["mind_backlog_rows"], 3)

    def test_backlog_zero_is_written_not_omitted(self) -> None:
        body = self._body()
        st = body._build_status()
        self.assertIn("mind_backlog_rows", st)
        self.assertEqual(st["mind_backlog_rows"], 0)


if __name__ == "__main__":
    unittest.main()
