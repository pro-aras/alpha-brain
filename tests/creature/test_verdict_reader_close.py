# edit: Claude (Fable 5.1), 2026-09-22 22:31 +0400 — the reader's decision to END a twin's mind the way the body did (tools/verdict_g4.py:
# closed_whole → every whole-tape twin's `close`; creature/replay.py:run_replay(close=)): a CLOSED life read WHOLE closes; a live life, a
# cut short of the tape's end, or a journal without the `stop` event never does (the live mind lands the in-flight think at a later boundary).
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("verdict_g4", Path(__file__).resolve().parents[2] / "tools" / "verdict_g4.py")
vg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(vg)


class ClosedWhole(unittest.TestCase):
    def test_closed_life_read_whole_closes(self):
        self.assertTrue(vg.closed_whole([{"event": "start", "at": "t"}, {"event": "stop", "at": "u"}], last_seq=500, tape_last_seq=500))

    def test_a_cut_short_of_the_end_never_closes(self):
        self.assertFalse(vg.closed_whole([{"event": "start"}, {"event": "stop"}], last_seq=400, tape_last_seq=500))

    def test_a_live_life_never_closes(self):
        self.assertFalse(vg.closed_whole([{"event": "start"}, {"event": "snapshot"}], last_seq=500, tape_last_seq=500))

    def test_an_empty_tape_never_closes(self):
        self.assertFalse(vg.closed_whole([{"event": "stop"}], last_seq=0, tape_last_seq=0))


if __name__ == "__main__":
    unittest.main()
