"""test_believe_scope.py — W3-1 (docs/G4-WAVE3-CLAUSES.md, D-G12): genome/think.py's believe() scope
law — one belief per word; a change is an EXTENSION; a contradiction a CLASH.

edit: Claude (Sonnet 5, W3 builder B), 2026-09-20 22:44 +0400 — new file, Wave 3 W3-1.

The five toys the brief names (docs/briefs/W3-BUILDER-B.md):
    (a) a stable stream -> 1 belief + N revisits + 0 extensions; read_beliefs(fold=True) folds them.
    (b) a stream whose second half adds a cell -> exactly 1 extension.
    (c) a stream whose second half re-labels the word's cells to another word (via `ledgers`) -> >= 1 clash.
    (d) the NEGATIVE CONTROL: (c) with clash_enabled=False writes no clash row and no other row.
    (e) the append-only law: the file's earlier bytes never change across the whole toy.
Plus life 1's real beliefs.jsonl (762 rows, 16 words) replayed through the new believe() as the scale
control (read-only source copied to a temp dir first — SOLUTIONS #212: never operate on the live file).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from genome.think import believe, read_beliefs

LIFE1_BELIEFS = Path("/data/dev/genome/run-g4-life1-20260920-0042/state/beliefs.jsonl")


def _prefix_hash(path: Path, k: int) -> str:
    """sha256 of the first k lines' bytes, exactly as they sit on disk (the append-only control: this
    must never change once computed, however many more lines are appended after it)."""
    if not path.exists():
        return hashlib.sha256(b"").hexdigest()
    lines = path.read_text().splitlines(keepends=True)[:k]
    return hashlib.sha256("".join(lines).encode()).hexdigest()


class TestBelieveScopeStable(unittest.TestCase):
    def test_a_stable_stream_is_one_belief_plus_revisits(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            kinds = []
            for i in range(5):
                row = believe("zog", [1, 2], [10 + i], 100 + i, path)
                kinds.append(row["kind"])
            self.assertEqual(kinds, ["belief", "revisit", "revisit", "revisit", "revisit"])

            rows = read_beliefs(path)
            self.assertEqual(len(rows), 5)
            self.assertEqual(sum(1 for r in rows if r["kind"] == "belief"), 1)
            self.assertEqual(sum(1 for r in rows if r["kind"] == "revisit"), 4)
            self.assertEqual(sum(1 for r in rows if r["kind"] == "extension"), 0)

            # every revisit returns the STANDING row's line (the fixed interface's own words)
            row = believe("zog", [1, 2], [999], 200, path)
            self.assertEqual(row["kind"], "revisit")
            self.assertEqual(row["line"], 0)  # zog's one and only belief sits at line 0

            folded = read_beliefs(path, fold=True)
            self.assertEqual(len(folded), 1)
            f = folded[0]
            self.assertEqual(f["word"], "zog")
            self.assertEqual(f["cells"], [1, 2])
            self.assertEqual(f["revisits"], 5)  # the 4 in the loop + the 1 just above
            self.assertEqual(f["extensions"], 0)
            self.assertEqual(f["clashes"], 0)
            self.assertEqual(f["episodes"], sorted({10, 11, 12, 13, 14, 999}))


class TestBelieveScopeExtension(unittest.TestCase):
    def test_b_second_half_adds_a_cell_is_exactly_one_extension(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            kinds = []
            # first half: cells [1, 2] stable
            for i in range(2):
                kinds.append(believe("zog", [1, 2], [i], i, path)["kind"])
            # second half: cell 3 added, nothing removed
            for i in range(2, 4):
                kinds.append(believe("zog", [1, 2, 3], [i], i, path)["kind"])

            self.assertEqual(kinds, ["belief", "revisit", "extension", "revisit"])
            rows = read_beliefs(path)
            self.assertEqual(sum(1 for r in rows if r["kind"] == "extension"), 1)
            ext = next(r for r in rows if r["kind"] == "extension")
            self.assertEqual(ext["of"], 0)
            self.assertEqual(ext["added"], [3])
            self.assertEqual(ext["cells"], [1, 2, 3])

            folded = read_beliefs(path, fold=True)
            self.assertEqual(len(folded), 1)
            self.assertEqual(folded[0]["cells"], [1, 2, 3])
            self.assertEqual(folded[0]["extensions"], 1)
            self.assertEqual(folded[0]["revisits"], 2)


class TestBelieveScopeClash(unittest.TestCase):
    def _relabelled_ledger(self, cells, other_word="not_zog"):
        return {"sight": {c: {other_word} for c in cells}, "words": {}}

    def test_c_ledger_relabel_is_at_least_one_clash(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            # first half: an ordinary stable belief, no ledger passed at all
            believe("zog", [1, 2], [1], 1, path)
            believe("zog", [1, 2], [2], 2, path)

            # second half: the SAME cells, but the ledger now says they answer another word
            ledgers = self._relabelled_ledger([1, 2])
            kinds = []
            for i in range(3, 5):
                row = believe("zog", [1, 2], [i], i, path, ledgers=ledgers)
                kinds.append(row["kind"])

            self.assertGreaterEqual(kinds.count("clash"), 1, kinds)
            rows = read_beliefs(path)
            clash_rows = [r for r in rows if r["kind"] == "clash"]
            self.assertGreaterEqual(len(clash_rows), 1)
            for c in clash_rows:
                self.assertEqual(c["word"], "zog")
                self.assertEqual(len(c["clashes"]), 2)
                # both named rows are real, on-disk, distinct lines
                a, b = c["clashes"]
                self.assertNotEqual(a, b)
                self.assertLess(max(a, b), len(rows))

    def test_c_removed_cells_without_ledger_is_also_a_clash(self) -> None:
        """The other half of rule 4: cells REMOVED (fully disjoint), no ledger involved at all."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            believe("bar", [1, 2], [1], 1, path)
            row = believe("bar", [9, 10], [2], 2, path)  # disjoint from [1, 2] -- cells removed
            self.assertEqual(row["kind"], "clash")
            self.assertEqual(sorted(row["clashes"]), [0, 1])
            rows = read_beliefs(path)
            self.assertEqual(rows[0]["word"], "bar")
            self.assertEqual(rows[0]["cells"], [1, 2])
            self.assertEqual(rows[1]["cells"], [9, 10])  # the new belief, written whole, still readable

    def test_d_negative_control_clash_disabled_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            believe("zog", [1, 2], [1], 1, path)
            believe("zog", [1, 2], [2], 2, path)

            before_lines = path.read_text().splitlines()
            before_hash = _prefix_hash(path, len(before_lines))

            ledgers = self._relabelled_ledger([1, 2])
            for i in range(3, 6):
                row = believe("zog", [1, 2], [i], i, path, ledgers=ledgers, clash_enabled=False)
                self.assertEqual(row["kind"], "clash_refused")

            after_lines = path.read_text().splitlines()
            after_hash = _prefix_hash(path, len(before_lines))
            self.assertEqual(len(after_lines), len(before_lines), "clash_enabled=False must write nothing")
            self.assertEqual(before_hash, after_hash)

            # the SAME scenario with clash_enabled defaulting True (the positive twin) DOES write:
            row = believe("zog", [1, 2], [999], 999, path, ledgers=ledgers)
            self.assertEqual(row["kind"], "clash")
            self.assertGreater(len(path.read_text().splitlines()), len(before_lines))


class TestBelieveScopeAppendOnly(unittest.TestCase):
    def test_e_append_only_across_a_mixed_stream(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "beliefs.jsonl"
            checkpoints = []

            believe("zog", [1, 2], [1], 1, path)                      # belief, line 0
            checkpoints.append(_prefix_hash(path, 1))
            believe("zog", [1, 2], [2], 2, path)                      # revisit
            believe("zog", [1, 2, 3], [3], 3, path)                   # extension
            checkpoints.append(_prefix_hash(path, 1))
            checkpoints.append(_prefix_hash(path, 3))

            ledgers = {"sight": {1: {"other"}, 2: {"other"}, 3: {"other"}}, "words": {}}
            believe("zog", [1, 2, 3], [4], 4, path, ledgers=ledgers)  # clash
            checkpoints.append(_prefix_hash(path, 1))
            checkpoints.append(_prefix_hash(path, 3))

            believe("zog", [1, 2, 3], [5], 5, path, ledgers=ledgers, clash_enabled=False)  # clash_refused, writes nothing
            checkpoints.append(_prefix_hash(path, 1))
            checkpoints.append(_prefix_hash(path, 3))

            # every hash of the same prefix length, taken at different points in time, must agree --
            # the file's earlier bytes never changed no matter what was appended after them.
            self.assertEqual(len(set(checkpoints[0:1] + [checkpoints[1]] + [checkpoints[3]] + [checkpoints[5]])), 1,
                              "the first line's hash drifted across the stream")
            self.assertEqual(len(set([checkpoints[2], checkpoints[4], checkpoints[6]])), 1,
                              "the first three lines' hash drifted across the stream")


class TestBelieveScopeLife1Replay(unittest.TestCase):
    """The positive control for scale: life 1's real beliefs.jsonl (762 rows, ~15-16 words, written by
    the OLD unconditional believe()) replayed through the NEW scoped believe(), in order, onto a fresh
    file. life 1's own file is READ-ONLY (a live/closed creature root, SOLUTIONS #212) -- copied to a
    temp dir before it is ever opened."""

    def test_life1_replay_stays_within_bound(self) -> None:
        if not LIFE1_BELIEFS.exists():
            self.skipTest(f"life 1's beliefs file not present at {LIFE1_BELIEFS} (not this box/run)")
        with tempfile.TemporaryDirectory() as d:
            src_copy = Path(d) / "life1_source_beliefs.jsonl"
            shutil.copy2(LIFE1_BELIEFS, src_copy)  # never open the original directly
            source_rows = [json.loads(l) for l in src_copy.read_text().splitlines() if l.strip()]

            out_path = Path(d) / "replayed_beliefs.jsonl"
            kinds_count = {"belief": 0, "revisit": 0, "extension": 0, "clash": 0, "clash_refused": 0}
            for r in source_rows:
                row = believe(r["word"], r["cells"], r["episodes"], r["moment"], out_path)
                kinds_count[row["kind"]] = kinds_count.get(row["kind"], 0) + 1

            standing_words = {r["word"] for r in source_rows}
            print(
                f"\n[life1 replay] source rows={len(source_rows)} distinct words={len(standing_words)} "
                f"-> {kinds_count}"
            )
            self.assertLessEqual(len(standing_words), 16)
            folded = read_beliefs(out_path, fold=True)
            self.assertLessEqual(len(folded), 16)
            self.assertEqual(
                kinds_count["belief"] + kinds_count["revisit"] + kinds_count["extension"]
                + kinds_count["clash"] + kinds_count["clash_refused"],
                len(source_rows),
            )
            print(f"[life1 replay] folded standing beliefs: {len(folded)}")
            for f in folded:
                print(f"  {f['word']!r}: cells={len(f['cells'])} episodes={len(f['episodes'])} "
                      f"revisits={f['revisits']} extensions={f['extensions']} clashes={f['clashes']}")


if __name__ == "__main__":
    unittest.main()
