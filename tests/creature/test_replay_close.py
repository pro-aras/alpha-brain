# edit: Claude (Fable 5.1), 2026-09-22 22:24 +0400 — THE REPLAY ROAD ENDS THE MIND THE WAY THE BODY DOES (plan L-1 × L-5; builder E's
# own tail note in docs/briefs/LIFE-E-REPORT.md §3: `run_replay` never called `Mind.close()`, so a CLOSED threaded life's journal carried
# one think row its replay could not — the body's `stop()` applies the in-flight think at the last eye row's seq, the replay dropped it).
# RED first: `run_replay(..., close=True)` did not exist. The old road (close=False, the default — the right ending for a MID-tape cut,
# where the live mind lands that think at a later boundary) is kept as the control: it must still LACK the tail row.
import json
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind
from creature.replay import compare, main as replay_main, read_mind_journal, run_replay
from creature.tape import read_tape
from tests.creature.test_life_e_think_thread import _build_tape, _write_threaded_genome

N_CANVASES, SEED = 205, 7      # ends five canvases after a THINK boundary (every 10): a word/self think is in flight at the tail


def _closed_live_journal(genome_path: Path, root: Path):
    _build_tape(root, n=N_CANVASES, seed=SEED)
    mind = Mind(genome_path, root)
    for r in read_tape(root):
        mind.consume(r)
    mind.close()                                   # the body's own ending (creature/body.py:stop)
    rows = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    live = [r for r in rows if "event" not in r]
    (root / "live-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in live))
    return live


class ReplayOfAClosedThreadedTape(unittest.TestCase):
    def test_close_true_matches_the_closed_live_journal_and_the_old_road_lacks_the_tail_think(self):
        with tempfile.TemporaryDirectory() as d:
            gp = _write_threaded_genome(Path(d))
            root = Path(tempfile.mkdtemp())
            live = _closed_live_journal(gp, root)
            tape = sorted((root / "tape").glob("*.jsonl"))[0]
            old = read_mind_journal(run_replay(gp, tape, Path(tempfile.mkdtemp())))
            diff_old = compare(old, live)
            self.assertIsNotNone(diff_old, "fixture premise broken: the old road already matches a closed journal (no think in flight at the tail)")
            self.assertEqual(sum(1 for r in live if "think" in r) - sum(1 for r in old if "think" in r), 1,
                             "fixture premise: the closed journal carries exactly ONE think row more than the old road")
            new = read_mind_journal(run_replay(gp, tape, Path(tempfile.mkdtemp()), close=True))
            self.assertIsNone(compare(new, live), f"close=True must reproduce the closed journal field by field; first diff {compare(new, live)}")
            # the CLI: --closed exits 0 against the closed journal; without it the same call is the old road and exits 1 at the tail
            self.assertEqual(replay_main(["--genome", str(gp), "--tape", str(tape), "--against", str(root / "live-journal.jsonl"), "--out", tempfile.mkdtemp(), "--closed"]), 0)
            self.assertEqual(replay_main(["--genome", str(gp), "--tape", str(tape), "--against", str(root / "live-journal.jsonl"), "--out", tempfile.mkdtemp()]), 1)


if __name__ == "__main__":
    unittest.main()
