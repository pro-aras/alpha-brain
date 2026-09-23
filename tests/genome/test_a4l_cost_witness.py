# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:48 +0400 — A4L-COST (docs/briefs/A4L-COST.md tasks 1/3; docs/A4-LADDER-PREREG.md
# §2.1 C1): the per-row state witness made SPARSE. Written RED-first against the landed shapes: the HASH gene's parse and its refusals, the
# ladder genome pinned against the floor by difflib, the undeclared road byte-identical to state_hash() (the negative control), the sparse
# digest equal to a from-scratch recompute after EVERY moment of two toy lives that fire every W/mask/strikes writer (with positive
# controls that they fired), the plant (a one-ulp live edge seen by BOTH witnesses; the padding seen by neither), the invariant the sparse
# form rests on, and save/load under HASH.
"""test_a4l_cost_witness.py — HASH sparse; dense at snapshot (A4L-COST)."""
from __future__ import annotations

import difflib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome.machinery import GenomeError, Organism, parse_genome

from ._toy import MINI_GENOME_TEXT

TREE = Path(__file__).resolve().parent.parent.parent
FLOOR = TREE / "genome" / "ladder" / "A4L-FLOOR.genome"
COST = TREE / "genome" / "ladder" / "A4L-COST.genome"
SNAP_FIXTURE = Path("/data/dev/a4-ladder/fixtures/alpha4-1-snapshot/state")
HASH_LINE = "HASH sparse; dense at snapshot"


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def toy_text(theta_n: float = 0.995, hash_: bool = True, grow: bool = False, scale_every: int = 50) -> str:
    text = (MINI_GENOME_TEXT.replace("BIRTH novelty cos<0.5", f"BIRTH novelty cos<{theta_n}")
            .replace("SCALE every 1000 moments", f"SCALE every {scale_every} moments")
            .replace("BUDGET 400 per arrival", "BUDGET 100000 per arrival"))
    text = text.replace("NMAX 200\n", "GROW unbounded\nCYCLE consolidate when redundant > 0.0 of alive\n") if grow else text.replace("NMAX 200", "NMAX 3000")
    return text + (HASH_LINE + "\n" if hash_ else "")


# the two toy regimes (tuned on the untouched machinery, scratch/toy_tune.py, 2026-09-23 11:4x): A fires sight AND word merges, prunes and
# SCALE; B fires ERROR births (A cannot: theta_n > theta_m makes every error birth redundant) and prunes.
REGIME_A = dict(seed=1, theta_n=0.995, sig_s=0.009, sig_w=0.0045, wrong=0.15, moments=1500)
REGIME_B = dict(seed=1, theta_n=0.5, sig_s=0.1, sig_w=0.0, wrong=0.3, moments=800)


def toy_life(regime: dict, hash_: bool = True, grow: bool = False, each=None, K: int = 6):
    """A deterministic toy life: K things, each a sight prototype and a word; a moment shows a noisy view of one thing with its word
    (or, with probability `wrong`, another thing's word). `each(org, m)` is called after every moment."""
    org = Organism(parse_genome(toy_text(regime["theta_n"], hash_=hash_, grow=grow)))
    org.new_arrival()
    rng = np.random.default_rng(regime["seed"])
    P = [_unit(rng.standard_normal(64)) for _ in range(K)]
    Wd = [_unit(rng.standard_normal(208)) for _ in range(K)]
    for m in range(regime["moments"]):
        k = int(rng.integers(K))
        x = _unit(P[k] + regime["sig_s"] * rng.standard_normal(64))
        kw = int(rng.integers(K)) if rng.random() < regime["wrong"] else k
        xw = _unit(Wd[kw] + regime["sig_w"] * rng.standard_normal(208)) if regime["sig_w"] > 0 else Wd[kw]
        org.moment(x, xw)
        if each is not None:
            each(org, m)
    return org


class TestHashGeneParse(unittest.TestCase):
    def test_the_line_parses_to_its_declared_dict(self) -> None:
        g = parse_genome(toy_text())
        self.assertEqual(g.declared["HASH"], {"row": "sparse", "snapshot": "dense"})

    def test_a_misspelt_form_refuses_by_name(self) -> None:
        for bad in ("HASH sparse", "HASH dense", "HASH", "HASH sparse; dense at snapshots", "HASH sparse dense at snapshot",
                    "HASH Sparse; dense at snapshot", "HASH sparse; dense at snapshot; dense"):
            with self.subTest(bad=bad):
                with self.assertRaises(GenomeError) as cm:
                    parse_genome(toy_text(hash_=False) + bad + "\n")
                self.assertIn("HASH", str(cm.exception))

    def test_undeclared_leaves_declared_without_the_key(self) -> None:
        self.assertNotIn("HASH", parse_genome(toy_text(hash_=False)).declared)

    def test_the_gene_is_wired_so_the_mind_does_not_refuse_it(self) -> None:
        from creature import genes
        self.assertIsNotNone(genes.RUNS["machinery"].get("HASH"))
        self.assertEqual(genes.unwired(parse_genome(COST.read_text()).declared), [])


class TestLadderGenomeIsTheFloorPlusOneLine(unittest.TestCase):
    """A4-LADDER-PREREG §1.1: difflib between the rung's genome and the floor shows EXACTLY the declared line and the edit note."""

    def test_difflib_shows_exactly_the_hash_line_and_the_header_note(self) -> None:
        floor = FLOOR.read_text().splitlines(); cost = COST.read_text().splitlines()
        diff = [d for d in difflib.ndiff(floor, cost) if d[:2] in ("+ ", "- ")]
        removed = [d for d in diff if d.startswith("- ")]; added = [d[2:] for d in diff if d.startswith("+ ")]
        self.assertEqual(removed, [], "the rung may not remove or change a floor line")
        self.assertEqual(len(added), 2, added)
        self.assertTrue(added[0].startswith("# A4L-COST.genome"), added[0])
        self.assertTrue(added[1].split("#", 1)[0].split() == HASH_LINE.split(), added[1])
        self.assertEqual([l for l in cost if l not in added], floor, "every floor line, in order, unchanged")

    def test_both_ladder_genomes_parse_and_differ_only_by_hash(self) -> None:
        f = parse_genome(FLOOR.read_text()); c = parse_genome(COST.read_text())
        self.assertEqual(set(c.declared) - set(f.declared), {"HASH"})
        self.assertEqual({k: v for k, v in c.declared.items() if k != "HASH"}, f.declared)


class TestUndeclaredIsTheDenseWitness(unittest.TestCase):
    """The negative control: HASH undeclared → row_hash() IS state_hash(), byte for byte, at every moment of a toy life."""

    def test_row_hash_is_state_hash_at_every_moment(self) -> None:
        seen = []
        def each(org, m):
            if m % 7 == 0:
                seen.append((org.row_hash(), org.state_hash()))
        org = toy_life(REGIME_A, hash_=False, each=each)
        self.assertEqual(org.hash_form, "dense")
        self.assertTrue(all(a == b for a, b in seen), "undeclared HASH must be byte-identical to state_hash()")
        self.assertIsInstance(org.hash_ms_last, float)
        self.assertGreaterEqual(org.hash_ms_last, 0.0)
        self.assertIsNone(getattr(org, "_witness", None))


class TestSparseEqualsFromScratch(unittest.TestCase):
    """Declared: the incremental witness equals a from-scratch recompute after EVERY moment — on two regimes that fire every writer."""

    def _run(self, regime: dict, grow: bool) -> Organism:
        from genome.witness import scratch_digest
        bad = []
        def each(org, m):
            h = org.row_hash()
            if h != scratch_digest(org):
                bad.append(m)
        org = toy_life(regime, hash_=True, grow=grow, each=each)
        self.assertEqual(bad, [], f"the sparse witness drifted from its from-scratch recompute at moments {bad[:10]}")
        self.assertEqual(org.hash_form, "sparse")
        return org

    def test_regime_a_merges_prunes_scales(self) -> None:
        org = self._run(REGIME_A, grow=False)
        c = org.c
        self.assertGreater(c["cells_merged_sight"], 0, "positive control: sight merges fired")
        self.assertGreater(c["cells_merged_words"], 0, "positive control: word (column) merges fired")
        self.assertGreater(c["edges_pruned"], 0, "positive control: prunes fired")
        self.assertGreater(c["scale_events"], 0, "positive control: SCALE fired")

    def test_regime_b_error_births(self) -> None:
        org = self._run(REGIME_B, grow=False)
        self.assertGreater(org.c["births_error_sight"] + org.c["births_error_words"], 0, "positive control: error births fired")
        self.assertGreater(org.c["edges_pruned"], 0)

    def test_regime_a_under_grow(self) -> None:
        self._run(REGIME_A, grow=True)

    def test_sparse_is_domain_separated_from_dense(self) -> None:
        org = toy_life(REGIME_B, hash_=True)
        self.assertNotEqual(org.row_hash(), org.state_hash())


class TestThePlant(unittest.TestCase):
    """C1 (v) at toy scale: one W entry of a LIVE edge perturbed by one ulp → the sparse AND the dense witness differ from the unplanted twin at
    that call and at every later one (the planted edge is on a thing shown once and never again, so the life never rewrites it); a
    perturbation in the PADDING (beyond the live block, mask 0) → neither witness moves."""

    def _twin(self, plant: str):
        rng = np.random.default_rng(99)
        p_new = _unit(rng.standard_normal(64)); w_new = _unit(rng.standard_normal(208))
        org = toy_life(REGIME_B, hash_=True)
        org.moment(p_new, w_new)                      # a thing shown ONCE: its sight cell and word cell are new, wired by HEBB
        s, t = org.sight.n - 1, org.words.n - 1
        self.assertEqual(org.mask[s, t], 1)
        if plant == "live":
            org.W[s, t] = np.nextafter(org.W[s, t], np.inf)
        elif plant == "padding":
            org.W[org.W.shape[0] - 1, org.W.shape[1] - 1] = np.nextafter(0.0, 1.0)
        out = [(org.row_hash(), org.state_hash())]
        rng2 = np.random.default_rng(7)
        P = [org.sight.cells[i].copy() for i in range(3)]
        W0 = [org.words.cells[j].copy() for j in range(min(2, org.words.n - 1))]
        for m in range(120):                          # the old things again: never the planted thing or its word
            org.moment(_unit(P[m % 3] + 0.05 * rng2.standard_normal(64)), W0[m % len(W0)])
            out.append((org.row_hash(), org.state_hash()))
        return out, org, (s, t)

    def test_live_plant_seen_by_both_witnesses_at_every_later_call(self) -> None:
        base, _o, _st = self._twin("none")
        live, org, (s, t) = self._twin("live")
        self.assertEqual(len(base), len(live))
        sparse_diff = [a[0] != b[0] for a, b in zip(base, live)]
        dense_diff = [a[1] != b[1] for a, b in zip(base, live)]
        self.assertTrue(all(sparse_diff), f"the sparse witness missed the live plant at calls {[i for i, d in enumerate(sparse_diff) if not d][:10]}")
        self.assertTrue(all(dense_diff), "the dense witness (the old one) sees the live plant too — both witnesses see the same thing")

    def test_padding_plant_moves_neither_witness(self) -> None:
        base, _o, _st = self._twin("none")
        pad, org, _st2 = self._twin("padding")
        self.assertEqual(base, pad, "a perturbation beyond the live block (mask 0) must move neither witness")
        r, c = org.W.shape[0] - 1, org.W.shape[1] - 1
        self.assertTrue(r >= org.sight.n or c >= org.words.n, "the padding plant stayed outside the live block")
        self.assertNotEqual(org.W[r, c], 0.0, "the plant is really there")

    def test_an_unmasked_entry_inside_the_block_is_what_the_invariant_forbids(self) -> None:
        """The sparse form is lossless BY THE INVARIANT (W != 0 ⇒ mask = 1): a violation of it inside the live block moves the dense witness
        and NOT the sparse one — which is exactly why the invariant is asserted (on the snapshot copy below; on the hour-1 fixture's final
        state by the C1 driver), and why the writer sweep pins every writer."""
        from genome.witness import invariant_violations
        org = toy_life(REGIME_B, hash_=True)
        self.assertEqual(invariant_violations(org), {"W_nonzero_mask0": 0, "strikes_nonzero_mask0": 0, "padding_nonzero": 0})
        n_s, n_w = org.sight.n, org.words.n
        rr, cc = np.nonzero(org.mask[:n_s, :n_w] == 0)
        r, c = int(rr[0]), int(cc[0])
        s0, d0 = org.row_hash(), org.state_hash()
        org.W[r, c] = np.nextafter(0.0, 1.0)
        self.assertEqual(invariant_violations(org)["W_nonzero_mask0"], 1)
        self.assertNotEqual(org.state_hash(), d0)
        self.assertEqual(org.row_hash(), s0)


class TestSaveLoadUnderHash(unittest.TestCase):
    def _roundtrip(self, grow: bool) -> None:
        org = toy_life(REGIME_A, hash_=True, grow=grow)
        sparse_before, dense_before = org.row_hash(), org.state_hash()
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        org.save(d / "organism")
        meta = json.loads((d / "organism.json").read_text())
        self.assertEqual(meta["state_hash"], dense_before, "the snapshot meta keeps the DENSE digest")
        o2 = Organism.load(d / "organism", org.g)          # load's dense verification chain, unchanged — raises on a mismatch
        self.assertEqual(o2.row_hash(), sparse_before, "the sparse row hash after load equals the one before save")
        self.assertEqual(o2.state_hash(), dense_before)

    def test_roundtrip_nmax(self) -> None:
        self._roundtrip(grow=False)

    def test_roundtrip_grow(self) -> None:
        self._roundtrip(grow=True)


@unittest.skipUnless((SNAP_FIXTURE / "organism.npz").exists(), "the A4 ladder snapshot fixture is not on this box")
class TestTheInvariantOnTheSnapshotCopy(unittest.TestCase):
    """The brief: «Lossless by the invariant … assert it in a test … on the snapshot copy» (a COPY: the fixture is read-only)."""

    def test_invariant_holds_and_sparse_equals_scratch(self) -> None:
        from genome.witness import invariant_violations, scratch_digest
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        for name in ("organism.npz", "organism.json"):
            shutil.copy2(SNAP_FIXTURE / name, d / name)
        o = Organism.load(d / "organism", parse_genome(COST.read_text()))
        self.assertEqual(invariant_violations(o), {"W_nonzero_mask0": 0, "strikes_nonzero_mask0": 0, "padding_nonzero": 0})
        self.assertEqual(o.hash_form, "sparse")
        h = o.row_hash()
        self.assertEqual(h, scratch_digest(o))
        self.assertNotEqual(h, o.state_hash())


if __name__ == "__main__":
    unittest.main()
