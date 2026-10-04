# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:35 +0400 — PREREG-EVOLVE-CAL §1 D3 (the E3 call-site shift): tests FIRST.
"""tests/tools/test_evolve_cal_d3.py — D3 of docs/organism/evolve/PREREG-EVOLVE-CAL.md.

`tools/evolve.py:151` called `surprise_mark(tape_slice, journal_rows, status, ...)` against the signature
`surprise_mark(journal, status, surprise_declared, ...)`: every argument landed one place off and `confirmed_share` read «not
gradable» on 13 of 13 judged rounds, falsely (the twin journals carry `confirmed` on every moment row). The law pins the right
order by a test that grades a twin journal carrying `confirmed` (RED on the shifted line) and a planted journal with `confirmed`
stripped, which must read None — so a DEAD input is told from a MIS-ROUTED one.
"""
from __future__ import annotations

import json
import tempfile
import types
import unittest
from pathlib import Path

import tools.evolve as ev


def _stub_mind(declared: dict):
    """The attributes `_twin_status` and `grade_twin` read from a Mind, and nothing else."""
    return types.SimpleNamespace(
        think_counters={"frames_filed": 7, "frames_scored": 0, "frames_true": 0, "said": 0, "heard_yes": 0, "heard_no": 0},
        acts_chosen={}, act_mismatches=0, glances_confirmed=0, glances_surprised=0,
        genome=types.SimpleNamespace(declared=declared))


def _twin_root_with_journal(rows) -> Path:
    root = Path(tempfile.mkdtemp())
    jdir = root / "journal"
    jdir.mkdir()
    (jdir / "2026-10-02.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return root


def _rows(n: int, confirmed_pattern, strip: bool = False):
    out = []
    for i in range(n):
        r = {"seq": 1000 + i, "moment": f"m{i:05d}", "act": "fix", "word": "circle", "hash": f"h{i}"}
        if not strip:
            r["confirmed"] = list(confirmed_pattern[i % len(confirmed_pattern)])
        out.append(r)
    return out


class TestGradeTwinSurpriseCallSite(unittest.TestCase):
    def test_a_journal_that_carries_confirmed_is_graded(self) -> None:
        # 40 moment rows, half of the located glances confirmed: the share counts GLANCES, so 0.5 exactly
        rows = _rows(40, [(True, False), (False, True)])
        root = _twin_root_with_journal(rows)
        r = ev.grade_twin(_stub_mind({"SURPRISE": {}}), root, root / "GENOME.genome", [], 1.0)
        self.assertEqual(r["journal_rows"], 40, "the reader found the journal (presence count)")
        self.assertIsNotNone(r["confirmed_share"],
                             "confirmed_share must be read from the twin journal's `confirmed` rows (D3: the call-site shift read None)")
        self.assertEqual(r["confirmed_share"], 0.5)
        self.assertEqual(r["detail"]["surprise"]["canvases"], 40)

    def test_a_planted_journal_without_confirmed_reads_none(self) -> None:
        # the same 40 rows with `confirmed` STRIPPED: a dead input must read None (not 0.0, not a guess)
        rows = _rows(40, [(True, False)], strip=True)
        self.assertFalse(any("confirmed" in r for r in rows), "the plant changed the bytes: no row carries `confirmed`")
        root = _twin_root_with_journal(rows)
        r = ev.grade_twin(_stub_mind({"SURPRISE": {}}), root, root / "GENOME.genome", [], 1.0)
        self.assertEqual(r["journal_rows"], 40)
        self.assertIsNone(r["confirmed_share"])
        self.assertFalse(r["detail"]["surprise"].get("graded"))

    def test_the_stripped_and_the_intact_journal_read_differently(self) -> None:
        # the pair that tells a dead input from a mis-routed one: same rows, `confirmed` present vs absent
        intact = _twin_root_with_journal(_rows(40, [(True, True)]))
        stripped = _twin_root_with_journal(_rows(40, [(True, True)], strip=True))
        a = ev.grade_twin(_stub_mind({"SURPRISE": {}}), intact, intact / "GENOME.genome", [], 1.0)
        b = ev.grade_twin(_stub_mind({"SURPRISE": {}}), stripped, stripped / "GENOME.genome", [], 1.0)
        self.assertEqual(a["confirmed_share"], 1.0)
        self.assertIsNone(b["confirmed_share"])

    def test_surprise_not_declared_reads_none_even_with_confirmed_rows(self) -> None:
        rows = _rows(40, [(True, False)])
        root = _twin_root_with_journal(rows)
        r = ev.grade_twin(_stub_mind({}), root, root / "GENOME.genome", [], 1.0)
        self.assertIsNone(r["confirmed_share"], "SURPRISE not declared: the mark is not gradable by its own rule")


if __name__ == "__main__":
    unittest.main()
