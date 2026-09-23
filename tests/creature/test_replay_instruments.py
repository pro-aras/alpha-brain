# edit: Claude (Fable 5.1), 2026-09-23 10:58 +0400 — the A4 ladder's two replay instruments (A4-LADDER-PREREG §4): `--timings` writes one
# row per tape row to DIR/timings.jsonl and `--exam-every N` sits the self-exam on the replayed organism every N canvases —
# and NEITHER changes the mind's journal (the identity control).
import json, tempfile, unittest
from pathlib import Path

from creature.replay import run_replay, read_mind_journal, compare
from tests.creature.test_replay_close import _write_threaded_genome, _closed_live_journal


class ReplayInstruments(unittest.TestCase):
    def test_timings_and_exams_leave_the_journal_identical(self):
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            root = Path(tempfile.mkdtemp())
            _closed_live_journal(gp, root)
            tape = sorted((root / "tape").glob("*.jsonl"))[0]
            n_rows = sum(1 for l in tape.read_text().splitlines() if l.strip())
            plain = read_mind_journal(run_replay(gp, tape, Path(tempfile.mkdtemp()), close=True))
            out = Path(tempfile.mkdtemp())
            inst = read_mind_journal(run_replay(gp, tape, out, close=True, timings=True, exam_every=20))
            self.assertIsNone(compare(inst, plain), f"the instruments changed the journal: {compare(inst, plain)}")
            tm = [json.loads(l) for l in (out / "timings.jsonl").read_text().splitlines() if l.strip()]
            self.assertEqual(len(tm), n_rows)
            self.assertTrue(all(r["ms"] >= 0 and "seq" in r and "sense" in r for r in tm))
            exams = sorted((out / "exam").glob("*.json"))
            self.assertGreaterEqual(len(exams), 1, "exam_every 20 on this tape must sit at least once")
            data = json.loads(exams[-1].read_text())
            self.assertIn("ask_seen_words", data)

    def test_without_the_flags_no_side_files(self):
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            root = Path(tempfile.mkdtemp())
            _closed_live_journal(gp, root)
            tape = sorted((root / "tape").glob("*.jsonl"))[0]
            out = Path(tempfile.mkdtemp())
            run_replay(gp, tape, out, close=True)
            self.assertFalse((out / "timings.jsonl").exists()); self.assertFalse((out / "exam").exists())


if __name__ == "__main__":
    unittest.main()
