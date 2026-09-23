# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:52 +0400 — A4L-COST task 6 (docs/briefs/A4L-COST.md): THE SEAM TESTS. The
# sparse witness meets four roads it did not write: GROW (Area.grow's doubling, _grow_W's chunks), SLEEP's cycle() (a merge pass over every
# alive cell + a full prune pass), the think thread's frozen SHADOW (object.__new__, sliced copies of W/mask), and save/load (the dense
# digest in the meta, load's verification chain unchanged). Each seam: the sparse row hash equals a from-scratch recompute across it, with a
# positive control that the road really fired. Plus the mind's own road: every hashed journal row carries the witness the genome declares.
"""test_a4l_cost_seams.py — HASH sparse × GROW, × cycle(), × the think shadow, × save/load, × the mind's journal rows."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from creature import think_thread
from creature.mind import Mind
from creature.tape import read_tape
from genome import machinery
from genome.machinery import AREA_INITIAL_CAPACITY, GROW_CHUNK, Organism, parse_genome
from genome.sleep import cycle

from tests.genome.test_a4l_cost_witness import HASH_LINE, REGIME_A, REGIME_B, toy_life, toy_text
from .test_life_e_think_thread import G4_GENOME, _build_tape, _threaded_text


def _unit(rng, d):
    v = rng.standard_normal(d)
    return v / np.linalg.norm(v)


def _write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(text)
    return p


class GrowTimesHash(unittest.TestCase):
    def test_births_across_area_grow_and_w_chunks_keep_sparse_equal_to_scratch(self) -> None:
        """A fresh thing and a fresh word every moment: both Areas double past AREA_INITIAL_CAPACITY and W grows by a chunk on BOTH axes
        (a birth whose id is past the current shape triggers _grow_W). At every growth and every 150 moments: sparse == from scratch."""
        from genome.witness import scratch_digest
        org = Organism(parse_genome(toy_text(theta_n=0.5, grow=True)))
        org.new_arrival()
        rng = np.random.default_rng(5)
        prev = (org.W.shape, org.sight.nmax, org.words.nmax)
        events = checked = 0
        for m in range(GROW_CHUNK + 250):
            org.moment(_unit(rng, 64), _unit(rng, 208))
            now = (org.W.shape, org.sight.nmax, org.words.nmax)
            if now != prev or m % 150 == 0:
                self.assertEqual(org.row_hash(), scratch_digest(org), f"moment {m}: {prev} -> {now}")
                checked += 1
                events += now != prev
            prev = now
        self.assertGreater(org.W.shape[0], GROW_CHUNK, "positive control: W grew a chunk on the sight axis")
        self.assertGreater(org.W.shape[1], GROW_CHUNK, "positive control: W grew a chunk on the words axis")
        self.assertGreater(org.sight.nmax, AREA_INITIAL_CAPACITY)
        self.assertGreater(org.words.nmax, AREA_INITIAL_CAPACITY)
        self.assertGreaterEqual(events, 5)


class CycleTimesHash(unittest.TestCase):
    """genome/sleep.py:cycle() — its merge pass over EVERY alive cell and its full prune pass go through the organism's own _merge/_prune."""

    def _cycle(self, regime: dict, what: str) -> None:
        from genome.witness import scratch_digest
        org = toy_life(regime, hash_=True, grow=True)          # CYCLE consolidate when redundant > 0.0 of alive
        self.assertEqual(org.row_hash(), scratch_digest(org))
        c0 = dict(org.c)
        self.assertTrue(cycle(org), "positive control: the cycle fired")
        moved = {"merged": (org.c["cells_merged_sight"] + org.c["cells_merged_words"]) - (c0["cells_merged_sight"] + c0["cells_merged_words"]),
                 "pruned": org.c["edges_pruned"] - c0["edges_pruned"]}
        self.assertGreater(moved[what], 0, f"positive control: the cycle {what} something ({moved})")
        self.assertEqual(org.row_hash(), scratch_digest(org), "the sparse witness after cycle() equals its from-scratch recompute")

    def test_cycle_merge_pass(self) -> None:
        self._cycle(REGIME_A, "merged")

    def test_cycle_prune_pass(self) -> None:
        self._cycle(REGIME_B, "pruned")


class ThinkShadowTimesHash(unittest.TestCase):
    """The think's frozen SHADOW (creature/think_thread.py:92-93 copies W/mask) never carries the witness and is never hashed: every row hash
    and every state hash during a threaded life is computed on the LIVE organism; the shadows exist (the positive control)."""

    def test_the_shadow_never_carries_or_computes_the_witness(self) -> None:
        from genome.witness import SparseWitness, scratch_digest
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        root = d / "run"; root.mkdir()
        _build_tape(root, n=160, seed=3)
        gp = _write(d, "G4-threaded-hash.genome", _threaded_text(G4_GENOME.read_text()) + "\n" + HASH_LINE + "\n")
        shadows, hashed_on, digested_on = [], [], []
        orig_freeze, orig_row, orig_state, orig_digest = think_thread.freeze_recall_view, Organism.row_hash, Organism.state_hash, SparseWitness.digest

        def freeze(org):
            s = orig_freeze(org); shadows.append(s); return s

        def row(self_):
            hashed_on.append(id(self_)); return orig_row(self_)

        def state(self_):
            hashed_on.append(id(self_)); return orig_state(self_)

        def digest(w, org):
            digested_on.append(id(org)); return orig_digest(w, org)

        think_thread.freeze_recall_view = freeze; Organism.row_hash = row; Organism.state_hash = state; SparseWitness.digest = digest
        try:
            mind = Mind(gp, root)
            for r in read_tape(root):
                mind.consume(r)
            mind.close()
        finally:
            think_thread.freeze_recall_view = orig_freeze; Organism.row_hash = orig_row; Organism.state_hash = orig_state; SparseWitness.digest = orig_digest
        self.assertGreater(len(shadows), 0, "positive control: the threaded think froze at least one shadow")
        shadow_ids = {id(s) for s in shadows}
        for s in shadows:
            self.assertFalse(hasattr(s, "_witness"), "a shadow never carries the witness")
        self.assertEqual(shadow_ids & set(hashed_on), set(), "no row/state hash was ever computed on a shadow")
        self.assertEqual(shadow_ids & set(digested_on), set(), "the sparse digest was never computed from a shadow")
        self.assertEqual(set(digested_on), {id(mind.org)}, "every sparse digest was the live organism's")
        self.assertEqual(mind.org.row_hash(), scratch_digest(mind.org))


class SaveLoadTimesHash(unittest.TestCase):
    """Mind.snapshot() then Mind.resume(): the snapshot meta carries the DENSE digest (load verifies it, unchanged); the resumed organism's
    sparse row hash equals the one before the snapshot."""

    def test_snapshot_resume_round_trip(self) -> None:
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        root = d / "run"; root.mkdir()
        _build_tape(root, n=80, seed=4)
        gp = _write(d, "G4-hash.genome", G4_GENOME.read_text() + "\n" + HASH_LINE + "\n")
        mind = Mind(gp, root)
        for r in read_tape(root):
            mind.consume(r)
        mind.snapshot()
        sparse, dense = mind.org.row_hash(), mind.org.state_hash()
        meta = json.loads((root / "state" / "organism.json").read_text())
        self.assertEqual(meta["state_hash"], dense, "the snapshot meta keeps the dense digest")
        mind.close()
        resumed, _last = Mind.resume(gp, root)
        self.assertEqual(resumed.org.hash_form, "sparse")
        self.assertEqual(resumed.org.row_hash(), sparse)
        self.assertEqual(resumed.org.state_hash(), dense)


class TheMindsHashedRowsAllReadTheWitness(unittest.TestCase):
    def test_every_hash_key_in_a_journal_row_is_row_hash(self) -> None:
        """creature/mind.py writes `"hash"` into FIVE journal rows (the canvas row, a sight-only canvas, the coarse row, the epoch row, the
        sleep row); every one must read `self.org.row_hash()` — the ONE per-row witness the genome declares — and none `state_hash()`
        (the dense digest is the snapshot's, written by Organism.save). An AST pin: a sixth site, or a site left on state_hash, fails."""
        import ast
        src = (Path(__file__).resolve().parents[2] / "creature" / "mind.py").read_text()
        vals = [v for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Dict)
                for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant) and k.value == "hash"]
        self.assertEqual(len(vals), 5, "the five hashed journal rows")
        for v in vals:
            self.assertTrue(isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "row_hash", ast.dump(v)[:120])
        dense_calls = [n.lineno for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "state_hash"]
        self.assertEqual(dense_calls, [], "creature/mind.py never computes the dense digest itself (an AST check: a comment cannot trip it, #113)")


class TheMindsJournalRows(unittest.TestCase):
    """The five hashed journal rows (the canvas row, the coarse row, a sight-only canvas, the sleep row, the epoch row) all read the ONE
    witness the genome declares: under HASH every hashed row's value equals the organism's row_hash at that row (checked by recording
    the witness's own returns), and a HASH-free twin of the same tape carries the dense state_hash on the same rows, every other field
    identical (C1 (ii) at unit scale)."""

    def _run(self, genome_path: Path, root: Path):
        seen = []
        orig = Organism.row_hash
        def row(self_):
            h = orig(self_); seen.append(h); return h
        Organism.row_hash = row
        try:
            mind = Mind(genome_path, root)
            for r in read_tape(root):
                mind.consume(r)
        finally:
            Organism.row_hash = orig
        rows = [json.loads(l) for f in sorted((root / "journal").glob("*.jsonl")) for l in f.read_text().splitlines() if l.strip()]
        return mind, rows, seen

    def test_hashed_rows_carry_the_declared_witness(self) -> None:
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        text = G4_GENOME.read_text().replace("SLEEP    every 2000 moments", "SLEEP    every 200 moments")
        self.assertIn("SLEEP    every 200 moments", text)
        dense_root, sparse_root = d / "dense", d / "sparse"
        for r_ in (dense_root, sparse_root):
            r_.mkdir(); _build_tape(r_, n=120, seed=6)
        g_dense = _write(d, "dense.genome", text)
        g_sparse = _write(d, "sparse.genome", text + "\n" + HASH_LINE + "\n")
        m_d, rows_d, seen_d = self._run(g_dense, dense_root)
        m_s, rows_s, seen_s = self._run(g_sparse, sparse_root)
        hashed_s = [r["hash"] for r in rows_s if "hash" in r]
        hashed_d = [r["hash"] for r in rows_d if "hash" in r]
        self.assertTrue(any("sleep" in r for r in rows_s), "positive control: a SLEEP row (a hashed row of another kind) was journaled")
        self.assertEqual(hashed_s, seen_s, "every hashed row carries the witness's own return, in order")
        self.assertEqual(hashed_d, seen_d)
        self.assertEqual(m_s.org.hash_form, "sparse"); self.assertEqual(m_d.org.hash_form, "dense")
        self.assertEqual(len(rows_s), len(rows_d))
        for a, b in zip(rows_d, rows_s):
            self.assertEqual({k: v for k, v in a.items() if k != "hash"}, {k: v for k, v in b.items() if k != "hash"})
            if "hash" in a:
                self.assertNotEqual(a["hash"], b["hash"], "the sparse witness is a different (domain-separated) digest")


if __name__ == "__main__":
    unittest.main()
