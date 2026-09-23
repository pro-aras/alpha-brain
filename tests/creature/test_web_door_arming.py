# edit: Claude (Fable 5.1), 2026-09-23 04:03 +0400 — the web door as the BODY arms it (the pre-flight's 62 restarts): the partial binds
# `root`, and calling it the way SenseThread does (fn(publish, stop_event)) with the stop already set returns at once —
# no TypeError, no fetch.
import tempfile, threading, unittest
from pathlib import Path


class WebDoorArming(unittest.TestCase):
    def test_the_bodys_partial_binds_root_and_runs(self):
        from creature import body as body_module
        from creature.senses import web as web_sense
        root = Path(tempfile.mkdtemp())
        cfg = {"hold_file": "world/HOLD", "floor_s": 2.0, "per_hour": 60, "opens_at_stage": 4}
        fn = body_module._web_sense_fn(web_sense, root, cfg)
        self.assertEqual(fn.keywords["root"], root)
        self.assertEqual(fn.keywords["questions_dir"], root / "world" / "questions")
        stop = threading.Event(); stop.set()
        fn(lambda *a: {"seq": 1}, stop)   # SenseThread's own call shape; must not raise


if __name__ == "__main__":
    unittest.main()
