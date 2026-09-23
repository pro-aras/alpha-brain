# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:54 +0400 — A4L-COST task 5 (docs/briefs/A4L-COST.md; A4-LADDER-PREREG §1.9, §2.1):
# the SURFACES, test-first against the landed shapes (#171/#173): STATUS gains `hash_ms_last` and `hash_form` on EVERY branch that writes
# STATUS (#164 — one builder, every write passes through it, pinned by an AST sweep of creature/body.py); the reader's COST line prints both;
# and `tools/verdict_life.py:hash_law_mark` — «not gradable» on the hour-1 fixture (HASH undeclared there), graded on a REAL record and its
# real replays (C1 (iii): the rung's replay identical INCLUDING hash; C1 (ii): the floor's replay identical EXCEPT hash), with a planted
# hash, a planted field and a dense STATUS each caught.
"""test_a4l_cost_marks.py — STATUS hash_ms_last/hash_form, the COST line, hash_law_mark."""
from __future__ import annotations

import ast
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from creature.body import Body
from creature.mind import Mind
from creature.replay import read_mind_journal, run_replay
from creature.tape import read_tape
from genome.machinery import parse_genome

from tests.genome.test_a4l_cost_witness import HASH_LINE
from .test_exam import GENOME_PATH
from .test_life_e_think_thread import G4_GENOME, _build_tape

TREE = Path(__file__).resolve().parents[2]
FIXTURE_GENOME = Path("/data/dev/a4-ladder/fixtures/alpha4-1-hour1/GENOME.genome")


def _genome(d: Path, name: str, text: str) -> Path:
    p = d / name
    p.write_text(text)
    return p


class StatusCarriesTheWitness(unittest.TestCase):
    def test_both_keys_on_the_status_build_dense_and_sparse(self) -> None:
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        for form, text in (("dense", GENOME_PATH.read_text()), ("sparse", GENOME_PATH.read_text() + "\n" + HASH_LINE + "\n")):
            root = d / form; root.mkdir()
            body = Body(root, _genome(d, form + ".genome", text)); body.start()
            try:
                st = body._build_status()
                self.assertEqual(st["hash_form"], form)
                self.assertIn("hash_ms_last", st)
                self.assertIsNone(st["hash_ms_last"], "no row hashed yet: None, never absent (#164)")
                body.mind.org.row_hash()
                st = body._build_status()
                self.assertIsInstance(st["hash_ms_last"], float)
                self.assertGreaterEqual(st["hash_ms_last"], 0.0)
            finally:
                body.stop()

    def test_every_status_write_goes_through_the_one_builder(self) -> None:
        """#164: a key on 'every branch that writes STATUS' — creature/body.py writes STATUS at four sites (the loop twice, the crash page,
        stop); each passes `self._build_status()` or a name bound to it in the same function, so the builder's keys are on every write."""
        src = (TREE / "creature" / "body.py").read_text()
        tree = ast.parse(src)
        sites = bad = 0
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef):
                continue
            bound = {t.id for n in ast.walk(fn) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                     and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "_build_status" for t in n.targets if isinstance(t, ast.Name)}
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "_write_status" and fn.name != "_write_status":
                    sites += 1
                    a = n.args[0] if n.args else None
                    ok = (isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "_build_status") or (isinstance(a, ast.Name) and a.id in bound)
                    bad += not ok
        self.assertGreaterEqual(sites, 4)
        self.assertEqual(bad, 0)


class TheReadersCostLine(unittest.TestCase):
    def test_viii_cost_carries_and_prints_both(self) -> None:
        from tools.verdict_g4 import cost_line, viii_cost
        m = viii_cost({"mind_ms_per_canvas_1min": 500.0, "mind_ms_median_1min": 0.2, "rss_mb": 900.0, "hash_form": "sparse", "hash_ms_last": 1.734}, 450.0, 0.0, 0)
        self.assertEqual(m["hash_form"], "sparse"); self.assertEqual(m["hash_ms_last"], 1.734)
        line = cost_line(m)
        self.assertIn("hash sparse", line); self.assertIn("1.734 ms", line)
        old = viii_cost({"mind_ms_per_canvas_1min": 500.0, "rss_mb": 900.0}, 450.0, 0.0, 0)
        self.assertEqual(old["hash_form"], "not recorded"); self.assertIn("hash not recorded", cost_line(old))


class HashLawMark(unittest.TestCase):
    @unittest.skipUnless(FIXTURE_GENOME.exists(), "the A4 ladder hour-1 fixture is not on this box")
    def test_not_gradable_on_the_hour1_fixture(self) -> None:
        from tools.verdict_life import hash_law_mark
        declared = "HASH" in parse_genome(FIXTURE_GENOME.read_text()).declared
        self.assertFalse(declared, "alpha4-1's genome does not declare HASH")
        rows = [{"seq": 3, "moment": "m", "hash": "ab" * 32}]
        m = hash_law_mark(rows, {"hash_form": "dense"}, declared, replay_same=rows, replay_floor=rows)
        self.assertFalse(m["graded"]); self.assertIsNone(m["pass"]); self.assertIn("not gradable", m["reason"]); self.assertIn("HASH", m["reason"])

    def test_the_non_mind_events_match_the_replay_tool(self) -> None:
        from creature.replay import NON_MIND_EVENTS
        from tools.verdict_life import _NON_MIND_EVENTS
        self.assertEqual(_NON_MIND_EVENTS, NON_MIND_EVENTS)

    def test_graded_on_a_real_record_and_its_real_replays(self) -> None:
        from tools.verdict_life import hash_law_mark
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        root = d / "life"; root.mkdir()
        _build_tape(root, n=60, seed=8)
        g_sparse = _genome(d, "sparse.genome", G4_GENOME.read_text() + "\n" + HASH_LINE + "\n")
        g_dense = _genome(d, "dense.genome", G4_GENOME.read_text())
        mind = Mind(g_sparse, root)                            # the "life": its own journal is the record
        for r in read_tape(root):
            mind.consume(r)
        life = [r for f in sorted((root / "journal").glob("*.jsonl")) for r in read_mind_journal(f)]
        tape_file = sorted((root / "tape").glob("*.jsonl"))[0]
        same = read_mind_journal(run_replay(g_sparse, tape_file, d / "replay-same"))
        floor = read_mind_journal(run_replay(g_dense, tape_file, d / "replay-floor"))
        st = {"hash_form": "sparse", "hash_ms_last": 0.9}
        m = hash_law_mark(life, st, True, replay_same=same, replay_floor=floor)
        self.assertTrue(m["graded"], m); self.assertTrue(m["pass"], m)
        self.assertIsNone(m["iii_first_diff"]); self.assertIsNone(m["ii_first_diff"])
        self.assertGreater(m["hash_rows"], 0)
        self.assertEqual(m["hash_rows_differing_from_floor"], m["hash_rows"], "the sparse witness differs from the dense on every hashed row")
        # the plants — each must be CAUGHT, by clause
        bad_same = copy.deepcopy(same); i = next(k for k, r in enumerate(bad_same) if "hash" in r); bad_same[i]["hash"] = "0" * 64
        m1 = hash_law_mark(life, st, True, replay_same=bad_same, replay_floor=floor)
        self.assertTrue(m1["graded"]); self.assertFalse(m1["pass"]); self.assertEqual(m1["iii_first_diff"], [bad_same[i]["seq"], "hash"])
        bad_floor = copy.deepcopy(floor); j = next(k for k, r in enumerate(bad_floor) if "births" in r); bad_floor[j]["births"] = bad_floor[j]["births"] + [["sight", 999, "novelty"]]
        m2 = hash_law_mark(life, st, True, replay_same=same, replay_floor=bad_floor)
        self.assertFalse(m2["pass"]); self.assertEqual(m2["ii_first_diff"], [bad_floor[j]["seq"], "births"])
        m3 = hash_law_mark(life, {"hash_form": "dense", "hash_ms_last": 140.0}, True, replay_same=same, replay_floor=floor)
        self.assertFalse(m3["pass"], "a HASH-declared life whose STATUS says dense did not run the sparse witness")
        # (iii) alone (the reader's own replay; the floor replay is the tape twin's): graded on what is given, (ii) printed as not read
        m4 = hash_law_mark(life, st, True, replay_same=same)
        self.assertTrue(m4["graded"]); self.assertTrue(m4["pass"]); self.assertIn("not read", str(m4["ii"]))
        m5 = hash_law_mark(life, st, True)
        self.assertFalse(m5["graded"]); self.assertIn("no replay", m5["reason"])


if __name__ == "__main__":
    unittest.main()
