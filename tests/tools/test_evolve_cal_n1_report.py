# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-04 00:15 +0400 — PREREG-EVOLVE-CAL A3.6 / A3b: the N1 reader (docs/organism/evolve/scripts/a0_report.py, now the stage reader), tests FIRST.
"""tests/tools/test_evolve_cal_n1_report.py — the stage reader on SYNTHETIC twin directories (a reading.json and a journal.jsonl.gz each, the layout run_twin writes).

The reader decides nothing: it prints, from the tested functions of tools/evolve_cal_analyse.py, (a) Stage A0's decision over the two A0 twins (variants eps:0.001:1 and eps:0.01:1) and A0+'s over the six
(k = 1..3 at both levels), (b) the level choice over every epsilon twin present (the SMALLEST level at which a twin MOVES), (c) the ruled Stage B rule (M) on the chosen level's first five twins, and
(d) which reading moved in which twin. A twin of another kind (a seed twin) is listed and decides nothing.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
_spec = importlib.util.spec_from_file_location("a0_report", ROOT / "docs" / "organism" / "evolve" / "scripts" / "a0_report.py")
rep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rep)


def rows(n=5):
    return [{"seq": 100 + s, "moment": f"m{s}", "act": "glance", "glance": 0, "cells": [10, 5], "hash": f"h{s}"} for s in range(n)]


def put(root: Path, name: str, variant: str, q1=104, frames=26, share=0.45, journal=None, cpu=2000.0) -> None:
    d = root / name
    d.mkdir(parents=True)
    r = {"variant": variant, "q1_seen": q1 / 110, "frames_filed": frames, "confirmed_share": share, "cpu_s": cpu, "wall_s": cpu + 5, "build_s": 17.0, "maxrss_kb": 6_000_000,
         "journal_rows": 5, "rows_consumed": 5, "state_hash": "s-" + name, "row_hash": "r-" + name, "code": {"dirty": False, "git_head": "x"}}
    (d / "reading.json").write_text(json.dumps(r))
    with gzip.open(d / "journal.jsonl.gz", "wt") as f:
        f.write("\n".join(json.dumps(x) for x in (journal if journal is not None else rows())))


def recorded(path: Path, n=5) -> Path:
    p = path / "rec.jsonl.gz"
    with gzip.open(p, "wt") as f:
        f.write("\n".join(json.dumps(x) for x in rows(n)))
    return p


def run(root: Path, tmp: Path, n_rec=5):
    out = tmp / "report.json"
    rc = rep.main(["--dir", str(root), "--recorded", str(recorded(tmp, n_rec)), "--out", str(out), "--ledger", str(tmp / "no-ledger.log")])
    return rc, json.loads(out.read_text())


class TestStageReader(unittest.TestCase):
    def build(self, moves):
        """moves: {(level, k): q1 items of the twin} — every other epsilon twin 1..5 at the three levels reads 104 like the incumbent."""
        tmp = Path(tempfile.mkdtemp())
        root = tmp / "n1"
        root.mkdir()
        put(root, "inc", "incumbent")
        for level, tag in ((0.0001, "1e-4"), (0.001, "1e-3"), (0.01, "1e-2")):
            for k in range(1, 6):
                put(root, f"eps{tag}-k0{k}", f"eps:{level!r}:{k}", q1=moves.get((level, k), 104))
        return tmp, root

    def test_the_a0_decision_reads_only_the_two_a0_twins_not_every_epsilon_twin_present(self) -> None:
        tmp, root = self.build({(0.001, 3): 103})                       # a twin of Stage A moved, but neither A0 twin did
        rc, d = run(root, tmp)
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(d["a0_twins"]), ["eps1e-2-k01", "eps1e-3-k01"])
        self.assertFalse(d["a0_decision"]["non_degenerate"], "the A0 decision is the two A0 twins' alone")

    def test_a_move_of_an_a0_twin_releases_stage_a_and_names_the_reading(self) -> None:
        tmp, root = self.build({(0.01, 1): 106})
        _, d = run(root, tmp)
        self.assertTrue(d["a0_decision"]["non_degenerate"])
        self.assertEqual(d["a0_decision"]["moved"], {"q1_seen": ["eps1e-2-k01"]})
        self.assertEqual(d["twins"]["eps1e-2-k01"]["moved_dims"], ["q1_seen"])
        self.assertEqual(d["twins"]["eps1e-3-k01"]["moved_dims"], [])

    def test_a0plus_is_decided_over_the_six_twins_k1_to_k3_at_the_two_levels(self) -> None:
        tmp, root = self.build({})
        _, d = run(root, tmp)
        self.assertEqual(len(d["a0plus_twins"]), 6)
        self.assertTrue(d["a0plus_decision"]["degenerate"])
        tmp, root = self.build({(0.001, 3): 103})
        _, d = run(root, tmp)
        self.assertFalse(d["a0plus_decision"]["degenerate"], "k03 at 1e-3 is one of the six")
        tmp, root = self.build({(0.01, 5): 103})
        _, d = run(root, tmp)
        self.assertTrue(d["a0plus_decision"]["degenerate"], "k05 is not one of the six")

    def test_the_level_choice_is_the_smallest_level_at_which_a_twin_moves(self) -> None:
        tmp, root = self.build({(0.001, 4): 103, (0.01, 2): 106, (0.01, 3): 107})
        _, d = run(root, tmp)
        self.assertEqual(d["choose_level"]["chosen"], 0.001)
        self.assertTrue(d["choose_level"]["per_level"]["0.01"]["spread_grows"], "the 1e-2 twins sit further from the incumbent than the 1e-3 twin: a label, never the choice")
        tmp, root = self.build({})
        _, d = run(root, tmp)
        self.assertIsNone(d["choose_level"]["chosen"])
        self.assertIsNone(d.get("stage_b"), "no level was chosen: no Stage B decision")

    def test_stage_b_is_the_ruled_rule_m_over_the_chosen_levels_first_five_twins(self) -> None:
        tmp, root = self.build({(0.01, 4): 106})
        _, d = run(root, tmp)
        self.assertEqual(d["choose_level"]["chosen"], 0.01)
        self.assertEqual((d["stage_b"]["rule"], d["stage_b"]["run"], d["stage_b"]["dims"]), ("M", True, ["q1_seen"]))

    def test_a_seed_twin_is_listed_and_decides_nothing(self) -> None:
        tmp, root = self.build({})
        put(root, "seed01", "seed:1", frames=2)
        _, d = run(root, tmp)
        self.assertEqual(d["twins"]["seed01"]["variant"], "seed:1")
        self.assertIsNone(d["twins"]["seed01"]["moved_dims"])
        self.assertFalse(d["a0_decision"]["non_degenerate"])
        self.assertIsNone(d["choose_level"]["chosen"])

    def test_a_missing_a0_twin_is_said_not_assumed(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        root = tmp / "n1"
        root.mkdir()
        put(root, "inc", "incumbent")
        put(root, "eps1e-3-k01", "eps:0.001:1")
        _, d = run(root, tmp)
        self.assertIsNone(d.get("a0_decision"))
        self.assertEqual(d["a0_missing"], ["eps:0.01:1"])

    def test_the_replication_reads_the_recorded_journal_and_a_plant_is_caught(self) -> None:
        tmp, root = self.build({})
        _, d = run(root, tmp)
        self.assertTrue(d["replication_vs_recorded"]["identical"])
        self.assertTrue(d["replication_plant"]["caught"])
        rows_long = rows(5)
        rows_long[2]["cells"] = [11, 5]
        tmp2 = Path(tempfile.mkdtemp())
        root2 = tmp2 / "n1"
        root2.mkdir()
        put(root2, "inc", "incumbent", journal=rows_long)
        _, d2 = run(root2, tmp2)
        self.assertFalse(d2["replication_vs_recorded"]["identical"], "an incumbent that differs from the recorded journal is reported as different")


if __name__ == "__main__":
    unittest.main()
