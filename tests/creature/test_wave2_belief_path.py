# edit: Claude (Fable 5.1), 2026-09-19 23:38 +0400 — regression for the belief-path crash: a life long enough for THINK's word work to
# ANSWER (recall_many over the word's last five episodes) must write state/beliefs.jsonl and never die on it.
import json, tempfile, unittest
from pathlib import Path

import numpy as np

from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world


ROOT = Path(__file__).resolve().parents[2]
GENOME = ROOT / "genome" / "G4.genome"


def _png(rgb):
    import io
    from PIL import Image
    b = io.BytesIO(); Image.fromarray(rgb).save(b, format="PNG"); return b.getvalue()


class TestBeliefPath(unittest.TestCase):
    def test_a_belief_is_written_to_the_state_file(self) -> None:
        root = Path(tempfile.mkdtemp()) / "run"
        tape = Tape(root)
        things = ["circle", "square", "triangle"]
        for i in range(150):
            t = things[i % 3]
            rgb, _truth = world.render_canvas(t, np.random.default_rng([4242, i]))
            tape.publish("ear", t.encode(), {"moment": f"m{i}", "source": "maker", "word": t}, "txt", at=f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z")
            tape.publish("eye", _png(rgb), {"moment": f"m{i}", "source": "maker"}, "png", at=f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z")
        mind = Mind(GENOME, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertGreater(mind.think_counters["thinks"], 0)
        outcomes = [json.loads(l)["think"]["outcome"] for f in (root / "journal").glob("*.jsonl") for l in f.read_text().splitlines() if '"think"' in l]
        self.assertIn("belief", outcomes, outcomes)
        beliefs = (root / "state" / "beliefs.jsonl")
        self.assertTrue(beliefs.exists(), "state/beliefs.jsonl not written")
        rows = [json.loads(l) for l in beliefs.read_text().splitlines()]
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(len(rows), mind.think_counters["beliefs"])


if __name__ == "__main__":
    unittest.main()
