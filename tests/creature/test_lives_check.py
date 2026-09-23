# edit: Claude (Fable 5.1), 2026-09-22 22:24 +0400 — the 8 h CHECK's counters against the journal shapes the builders LANDED (the advisor's
# read at the wrap: the checker counted a top-level `act_chosen` (builder F's hands row) and a top-level `self` nothing writes; builder D's
# game acts are a DICT under `act` — moment rows carry the STRING `act: "glance"`/`"coarse"` — and builder A's self beliefs are think rows of
# kind `self`). RED first: `journal_counts` / `births_by_hour` did not exist (the counting sat inline in main()). Sight births are split by
# the moment row's own `source` (maker / game / folder / hands), the input of PREREG §19.11's sizing rule.
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("lives_check", Path(__file__).resolve().parents[2] / "tools" / "lives" / "check.py")
check = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(check)


ROWS = [
    {"seq": 1, "moment": "m1", "when": "2026-09-23T08:00:01Z", "glance": 0, "act": "glance", "source": "maker", "word": "circle", "births": [["sight", 1], ["words", 2]], "confirmed": [True, False, False, False]},
    {"seq": 2, "moment": "m1", "when": "2026-09-23T08:00:01Z", "glance": 1, "act": "glance", "source": "maker", "births": [["sight", 3]]},
    {"seq": 3, "moment": "m2", "when": "2026-09-23T08:00:16Z", "glance": 0, "act": "glance", "source": "game", "births": [["sight", 4]]},
    {"seq": 3, "act": "coarse", "glance": 4, "births": []},
    {"seq": 4, "act": {"game": "babyai-gotolocal", "act": "left", "act_idx": 0, "seq": 4}},               # builder D: the mind's game act
    {"seq": 5, "think": {"item": "self", "kind": "self", "outcome": "belief", "parked": False}},           # builder A: a self think
    {"seq": 6, "think": {"item": "circle", "kind": "word", "outcome": "belief", "parked": False}, "act_chosen": {"act": "run", "program": "p1.py", "seq": 6}},   # builder F: hands
    {"seq": 7, "moment": "m3", "when": "2026-09-23T09:00:01Z", "glance": 0, "act": "glance", "source": "hands", "births": [["sight", 5], ["sight", 6]]},
    {"seq": 8, "question": {"q": "what-is", "args": ["x.png"]}},
    {"seq": 9, "say": {"said": "circle"}},
    {"event": "start", "at": "2026-09-23T08:00:00Z"},
]


class JournalCounts(unittest.TestCase):
    def test_counts_every_landed_shape_by_its_own_key(self):
        c = check.journal_counts(ROWS)
        self.assertEqual(c["acts_game"], 1, "builder D's game act is a DICT under `act`; the string `act: glance/coarse` on moment rows is not an act")
        self.assertEqual(c["hands_runs"], 1)
        self.assertEqual(c["self_thinks"], 1)
        self.assertEqual(c["think"], 2)
        self.assertEqual(c["question"], 1); self.assertEqual(c["say"], 1)
        self.assertNotIn("self", c, "nothing journals a top-level `self` key — a counter that can only read 0 is not printed")
        self.assertEqual(c["moments"], 4); self.assertEqual(c["canvases"], 3); self.assertEqual(c["coarse_rows"], 1)


# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:59 +0400 — A4L-VOICE: a voiced canvas's eye row carries a `sound` dict too
# (the binding: {seq, winners, cells}) — the check counts the SOUND ROWS consumed under `sound` and the bindings under `sound_bound`, never
# one tape row twice; a genome without the voice counts exactly as before.
class VoiceCounts(unittest.TestCase):
    def test_a_binding_row_is_counted_apart(self):
        rows = [{"seq": 10, "sound": {"moment": "m9", "level": 0.1, "when": 0.006, "file": None, "ep": None, "pending": True}},
                {"seq": 11, "moment": "m9", "glance": 0, "word": "cup", "births": [["sound", 0, "novelty"]], "sound": {"seq": 10, "winners": [0], "cells": 1}}]
        c = check.journal_counts(rows)
        self.assertEqual(c["sound"], 1); self.assertEqual(c["sound_bound"], 1)
        self.assertNotIn("sound_bound", check.journal_counts(ROWS))


class BirthsByHour(unittest.TestCase):
    def test_sight_births_per_hour_split_by_source(self):
        hours, by_hour, by_source = check.births_by_hour(ROWS)
        self.assertEqual(hours, ["2026-09-23T08", "2026-09-23T09"])
        self.assertEqual([by_hour[h] for h in hours], [3, 2], "sight births only (the words birth is not counted); every glance row counts")
        self.assertEqual(by_source["2026-09-23T08"], {"maker": 2, "game": 1})
        self.assertEqual(by_source["2026-09-23T09"], {"hands": 2})

    def test_confirmed_share_counts_glances_not_rows(self):
        share = check.confirmed_share_by_hour(ROWS)
        self.assertAlmostEqual(share["2026-09-23T08"], 0.25, places=6, msg="`confirmed` is a LIST per located glance: 1 of 4 confirmed reads 0.25, never 1.0")
        self.assertIsNone(share.get("2026-09-23T09"), "no `confirmed` field in that hour → no share (not 0.0)")


if __name__ == "__main__":
    unittest.main()


# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:1x +0400 — ALPHA4-2-PREREG.md §2.6's two check.py fixes, RED first:
# (1) the coarse row (creature/mind.py:_coarse_row) writes no `when` — A4L-DROP-REPORT task 3: every coarse row's confirmed flag
#     landed under the EMPTY hour (alpha4-1: the "" bucket read 0.0253 = 46 / 1818, exactly the coarse-glance count); its hour is its
#     sibling canvas row's (they share the seq — SLEEP's own "second mind row" pattern); the fix is in check.py ONLY (mind.py's
#     journal stays byte-identical: M3's regression is INCLUDING hash, and a new key on the coarse row is a format change);
# (2) the SIZING line under GROW: `status.get("sight_capacity")` is written by EVERY modern body (creature/body.py, GROW or not), so
#     the 07:38 patch's "else NMAX" branch was dead and «CROSSES NMAX» could never print on a capped genome — the signal is the run's
#     own $ROOT/GENOME.genome (tools/lives/launch.sh copies it there), parsed, `"GROW" in declared`.
import contextlib, io, json, tempfile

TREE = Path(__file__).resolve().parents[2]


class CoarseRowHour(unittest.TestCase):
    ROWS = [
        {"seq": 3, "moment": "w1", "when": "2026-09-23T08:00:01Z", "act": "glance", "glance": 0, "source": "maker", "word": "circle",
         "births": [["sight", 1, "novelty"]], "confirmed": [False, False, False, False]},
        # the landed coarse row, verbatim from ref-floor/journal.jsonl minus the digest: no `when`
        {"seq": 3, "moment": "w1", "act": "coarse", "glance": 4, "fix": None, "windows": None, "hash": "334f", "residual": None, "confirmed": True},
        {"seq": 9, "moment": "w2", "when": "2026-09-23T09:00:05Z", "act": "glance", "glance": 0, "source": "game", "births": [],
         "confirmed": [True, False, False, False]},
        {"seq": 9, "moment": "w2", "act": "coarse", "glance": 4, "fix": None, "windows": None, "hash": "5d", "residual": 0.01, "confirmed": False},
    ]

    def test_the_coarse_rows_confirmed_flag_lands_in_its_canvas_hour(self):
        share = check.confirmed_share_by_hour(self.ROWS)
        self.assertNotIn("", share, "a coarse row must never bucket under the empty hour")
        self.assertAlmostEqual(share["2026-09-23T08"], 1 / 5, places=6, msg="4 located glances (0 confirmed) + the coarse glance (confirmed)")
        self.assertAlmostEqual(share["2026-09-23T09"], 1 / 5, places=6)

    def test_the_hours_list_carries_no_empty_hour(self):
        hours, births, _ = check.births_by_hour(self.ROWS)
        self.assertEqual(hours, ["2026-09-23T08", "2026-09-23T09"])
        self.assertEqual([births[h] for h in hours], [1, 0])

    def test_a_row_with_neither_when_nor_a_sibling_keeps_the_old_bucket(self):
        lone = [{"seq": 77, "moment": "w9", "act": "coarse", "glance": 4, "fix": None, "windows": None, "hash": "0", "residual": None, "confirmed": True}]
        self.assertEqual(list(check.confirmed_share_by_hour(lone)), [""], "nothing is invented for a row no canvas row can place")


class SizingUnderGrow(unittest.TestCase):
    def test_genome_declares_grow_reads_the_roots_genome_file(self):
        root = Path(tempfile.mkdtemp())
        self.assertIsNone(check.genome_declares_grow(root), "no GENOME.genome at the root (an older run): unknown, never a guess")
        (root / "GENOME.genome").write_text((TREE / "genome" / "G0b.genome").read_text())
        self.assertIs(check.genome_declares_grow(root), False)
        (root / "GENOME.genome").write_text((TREE / "genome" / "ALPHA4.genome").read_text())
        self.assertIs(check.genome_declares_grow(root), True)
        (root / "GENOME.genome").write_text("not a genome\n")
        self.assertIsNone(check.genome_declares_grow(root))

    def test_sizing_wording_says_capacity_doubles_under_grow_and_crosses_nmax_without_it(self):
        kind, crosses = check.sizing_wording(2100.0, 2000, True)
        self.assertIn("capacity doubles", crosses); self.assertNotIn("CROSSES NMAX", crosses); self.assertIn("GROW", kind)
        kind, crosses = check.sizing_wording(2100.0, 2000, False)
        self.assertEqual(crosses, "CROSSES NMAX"); self.assertEqual(kind, "NMAX")
        kind, crosses = check.sizing_wording(2100.0, 2000, None)
        self.assertEqual(crosses, "CROSSES NMAX"); self.assertIn("unknown", kind)
        self.assertTrue(check.sizing_wording(1500.0, 2000, True)[1].startswith("under"))
        self.assertTrue(check.sizing_wording(1500.0, 2000, False)[1].startswith("under"))

    def test_main_reads_the_genome_never_sight_capacity(self):
        for genome_name, expect, absent in (("G0b.genome", "CROSSES NMAX", "capacity doubles"), ("ALPHA4.genome", "capacity doubles", "CROSSES NMAX")):
            with self.subTest(genome=genome_name):
                root = Path(tempfile.mkdtemp()); (root / "journal").mkdir(); (root / "tape").mkdir(); (root / "exam").mkdir()
                (root / "STATUS.json").write_text(json.dumps({"moments": 10, "cells": [1, 1], "sight_born": 2100, "sight_nmax": 2000, "sight_capacity": 2000}))
                (root / "GENOME.genome").write_text((TREE / "genome" / genome_name).read_text())
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    check.main(["--root", str(root)])
                lines = [l for l in buf.getvalue().splitlines() if l.startswith("[check] SIZING")]
                self.assertEqual(len(lines), 1, buf.getvalue()[-800:])
                self.assertIn(expect, lines[0]); self.assertNotIn(absent, lines[0])
