# edit: Claude (Opus 5.5, A4 seam-5 builder), 2026-09-23 15:01 +0400 — SEAM 5 (docs/ALPHA4-2-PREREG.md §7.2 on a42: COST x VOICE). Written
# RED-first on the merged bytes (a4-integration cc98e98): A4L-COST's sparse witness (genome/witness.py) was built before A4L-VOICE and digests
# nothing of the sound area or its two meetings, and the sight<->words mask written by `_area_merge` (a sight or word cell merged INSIDE a
# sound meeting) never marks it. These tests pin, on voiced toy lives that fire every writer of the sound state (with positive controls
# that each fired): the incremental witness == a from-scratch recompute after EVERY moment; every part of the sound state the dense
# state_hash() reads moves the sparse digest too, and every part the dense one ignores (the padding beyond a live block) moves neither;
# the one-ulp plant in a meeting's live block is seen by BOTH witnesses at every later call (the designer's RED); an EMPTY sound area is
# hash-neutral for the sparse digest exactly as for the dense one; undeclared HASH on a voiced life is still state_hash(); save/load.
"""test_a4l_seam5_witness_sound.py — HASH sparse x AREA sound + MEET sight sound + MEET sound words (seam 5)."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from genome import machinery
from genome.machinery import Organism, parse_genome
from genome.witness import scratch_digest

from .test_a4l_cost_witness import toy_text

SND_DIM = machinery.SOUND_TRAIT_DIM


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def voiced_text(theta_n: float, theta_snd: float, hash_: bool = True, grow: bool = False, sound: bool = True) -> str:
    """COST's toy genome (tests/genome/test_a4l_cost_witness.py:toy_text) + A4L-VOICE's three lines (the ladder genome's own forms)."""
    lines = f"AREA     sound  from cochlea cos>={theta_snd}\nMEET     sight  sound\nMEET     sound  words\n" if sound else ""
    return toy_text(theta_n, hash_=hash_, grow=grow) + lines


# The two voiced regimes, tuned on the untouched machinery (scratch/seam5/toy_tune.py, 2026-09-23 14:58 +0400). A': near-duplicate sight
# cells, words and chords — sight merges INSIDE the sight<->sound meeting on wordless canvases (`_area_merge` on the sight<->words mask),
# sound merges, word merges, a merged cell's meeting edges following it (`_merge_pair_edges`), prunes in both meetings, SCALE. B': error
# births of sound (and sight) cells, sound merges, prunes. `blind`: the share of canvases whose word never came (x_w None, the voice still
# heard — the `--blind ear` road).
VREGIME_A = dict(seed=1, theta_n=0.995, sig_s=0.009, sig_w=0.0045, theta_snd=0.997, sig_c=0.008, wrong=0.15, wrong_snd=0.15, blind=0.3, moments=1500)
VREGIME_B = dict(seed=1, theta_n=0.5, sig_s=0.1, sig_w=0.0, theta_snd=0.7, sig_c=0.1, wrong=0.3, wrong_snd=0.3, blind=0.2, moments=800)


def voiced_life(reg: dict, hash_: bool = True, grow: bool = False, each=None, K: int = 6, voiced: bool = True, sound: bool = True,
                moments: int = None) -> Organism:
    """A deterministic voiced toy life: K things, each a sight prototype, a word and a chord (a 37-number trait, as the sealed front
    publishes). `voiced=False` draws the SAME randomness and passes no chord (the silent twin); `sound=False` declares no sound area."""
    org = Organism(parse_genome(voiced_text(reg["theta_n"], reg["theta_snd"], hash_=hash_, grow=grow, sound=sound)))
    org.new_arrival()
    rng = np.random.default_rng(reg["seed"])
    P = [_unit(rng.standard_normal(64)) for _ in range(K)]
    Wd = [_unit(rng.standard_normal(208)) for _ in range(K)]
    Ch = [_unit(rng.standard_normal(SND_DIM)) for _ in range(K)]
    for m in range(reg["moments"] if moments is None else moments):
        k = int(rng.integers(K))
        x = _unit(P[k] + reg["sig_s"] * rng.standard_normal(64))
        kw = int(rng.integers(K)) if rng.random() < reg["wrong"] else k
        blind = rng.random() < reg["blind"]
        xw = _unit(Wd[kw] + reg["sig_w"] * rng.standard_normal(208)) if reg["sig_w"] > 0 else Wd[kw]
        kc = int(rng.integers(K)) if rng.random() < reg["wrong_snd"] else k
        xc = _unit(Ch[kc] + reg["sig_c"] * rng.standard_normal(SND_DIM))
        org.moment(x, None if blind else xw, x_snd=xc if voiced else None)
        if each is not None:
            each(org, m)
    return org


class _Calls:
    """Counts, around the machinery's own writers, what each one CHANGED (the positive controls: a writer that never fired proves nothing)."""

    def __init__(self):
        self.n = {"area_merge_sight": 0, "area_merge_words": 0, "area_merge_sound": 0, "pair_mask_moved_by_merge_pair_edges": 0}
        self._orig = (Organism._area_merge, Organism._merge_pair_edges)

    def __enter__(self):
        orig_am, orig_mpe = self._orig
        calls = self.n

        def am(org, area, winners, via):
            before = (org.c["cells_merged_sight"], org.c["cells_merged_words"], org.c_sound.get("cells_merged_sound", 0))
            orig_am(org, area, winners, via)
            after = (org.c["cells_merged_sight"], org.c["cells_merged_words"], org.c_sound.get("cells_merged_sound", 0))
            for i, nm in enumerate(("sight", "words", "sound")):
                calls[f"area_merge_{nm}"] += after[i] - before[i]

        def mpe(org, area, a, b):
            before = {k: p.mask.copy() for k, p in org.sound_meets.items()}
            r = orig_mpe(org, area, a, b)
            calls["pair_mask_moved_by_merge_pair_edges"] += sum(int(not np.array_equal(before[k], p.mask)) for k, p in org.sound_meets.items())
            return r

        Organism._area_merge, Organism._merge_pair_edges = am, mpe
        return self

    def __exit__(self, *exc):
        Organism._area_merge, Organism._merge_pair_edges = self._orig
        return False


class TestSparseEqualsScratchOnVoicedLives(unittest.TestCase):
    """The incremental witness == a from-scratch recompute (scratch_digest) after EVERY moment of a voiced life."""

    def _run(self, reg: dict, grow: bool = False) -> tuple:
        bad = []

        def each(org, m):
            if org.row_hash() != scratch_digest(org):
                bad.append(m)

        with _Calls() as calls:
            org = voiced_life(reg, hash_=True, grow=grow, each=each)
        self.assertEqual(bad, [], f"the sparse witness drifted from its from-scratch recompute at moments {bad[:10]} (of {len(bad)})")
        self.assertEqual(org.hash_form, "sparse")
        return org, calls.n

    def test_regime_a_merges_in_the_meetings_prunes_scale(self) -> None:
        org, calls = self._run(VREGIME_A)
        cs = org.c_sound
        self.assertGreater(calls["area_merge_sight"], 0, "positive control: a sight cell merged INSIDE sight<->sound (the sight<->words mask moved by _area_merge)")
        self.assertGreater(calls["area_merge_sound"], 0, "positive control: sound cells merged")
        self.assertGreater(calls["pair_mask_moved_by_merge_pair_edges"], 0, "positive control: a merged cell's meeting edges followed it")
        self.assertGreater(org.c["cells_merged_words"], 0, "positive control: word merges (the sound<->words columns follow)")
        self.assertGreater(cs["edges_pruned_sight_sound"], 0, "positive control: sight<->sound prunes")
        self.assertGreater(cs["edges_pruned_sound_words"], 0, "positive control: sound<->words prunes")
        self.assertGreater(org.c["scale_events"], 0, "positive control: SCALE (the meetings' _scale_pairs) fired")

    def test_regime_b_error_births_of_sound_cells(self) -> None:
        org, calls = self._run(VREGIME_B)
        self.assertGreater(org.c_sound["births_error_sound"], 0, "positive control: sound error births")
        self.assertGreater(org.c["births_error_sight"], 0, "positive control: sight error births")
        self.assertGreater(calls["area_merge_sound"], 0, "positive control: sound merges")

    def test_regime_a_under_grow_with_the_meetings_growing(self) -> None:
        """GROW with the chunk and the initial capacity shrunk (A4L-VOICE's own seam does the same): every Area doubles past its start and
        BOTH meetings grow by chunks on both axes (`_Pair.grow` via `_grow_pairs`) — == scratch at every moment."""
        old = (machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK)
        machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK = 4, 8
        try:
            org, _calls = self._run(VREGIME_A, grow=True)
        finally:
            machinery.AREA_INITIAL_CAPACITY, machinery.GROW_CHUNK = old
        ss, sw = org.sound_meets["sight-sound"], org.sound_meets["sound-words"]
        self.assertGreater(ss.W.shape[0], 8, "positive control: sight<->sound grew on its sight axis")
        self.assertGreater(ss.W.shape[1], 8, "positive control: sight<->sound grew on its sound axis")
        self.assertGreater(sw.W.shape[0], 8, "positive control: sound<->words grew on its sound axis")
        self.assertGreater(sw.W.shape[1], 8, "positive control: sound<->words grew on its words axis")
        self.assertGreater(org.sound.nmax, 4, "positive control: the sound area doubled")

    def test_a_word_cell_merged_inside_sound_words_marks_the_sight_words_block(self) -> None:
        """`_area_merge(words, T, sound<->words)` (a word cell's chance falls in sound<->words when no sight winner met it) moves every row of
        the sight<->words column b into column a. No natural toy reaches it (S empty with T lit needs a refused sight birth), so it is
        driven directly — after a real voiced life — on two word cells built by the machinery's own writers (a birth, HEBB-shaped wiring,
        each wire marked as the writers mark it)."""
        org = voiced_life(VREGIME_A, hash_=True, moments=300)
        sw, w = org.sound_meets["sound-words"], org._witness
        a = int(org.words.alive_ids()[0])
        y = machinery._unit(org.words.cells[a] + 1e-4 * np.random.default_rng(3).standard_normal(208))
        b = org._birth(org.words, y, "novelty")
        self.assertIsNotNone(b)
        u = int(np.flatnonzero(sw.mask[:org.sound.n, a])[0]) if sw.mask[:org.sound.n, a].any() else 0
        sw.mask[u, a] = 1; sw.W[u, a] = max(float(sw.W[u, a]), 0.5); w.mark(u, pair="sound-words")
        sw.mask[u, b] = 1; sw.W[u, b] = float(sw.W[u, a]); w.mark(u, pair="sound-words")        # b answers what a answers
        rows_b = [s for s in org.sight.alive_ids()[:3] if not org.mask[s, b]]
        for s in rows_b:                                                                         # sight<->words edges on column b
            org.mask[s, b] = 1; org.W[s, b] = 0.3; w.mark(s)
        self.assertEqual(org.row_hash(), scratch_digest(org), "the set-up itself keeps the witness exact")
        merged0 = org.c["cells_merged_words"]
        org._area_merge(org.words, [a, b], sw)
        self.assertEqual(org.c["cells_merged_words"], merged0 + 1, "positive control: the word cells merged in sound<->words")
        self.assertEqual(int(org.mask[:, b].sum()), 0, "column b's sight<->words edges moved to column a")
        self.assertTrue(all(org.mask[s, a] for s in rows_b))
        self.assertEqual(org.row_hash(), scratch_digest(org), "the sparse witness saw the sight<->words mask move")


def _copy_org(org: Organism) -> Organism:
    """A deep copy through save/load (the machinery's own road), with a FRESH witness (scans at its first call)."""
    d = Path(tempfile.mkdtemp())
    try:
        org.save(d / "o")
        return Organism.load(d / "o", org.g)
    finally:
        shutil.rmtree(d, True)


class TestEveryPartTheDenseReadsMovesTheSparse(unittest.TestCase):
    """«The sparse row hash must see every change the dense digest sees»: each part of the sound state state_hash() reads is perturbed ONCE
    on a copy of a voiced organism; the dense digest moves (the precondition) AND the sparse one — both the running witness (the value a
    writer would leave; a MASK change is marked as the writers mark it) and a from-scratch recompute. Each part the dense digest ignores
    (the padding beyond a live block or a live prefix) moves NEITHER."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = voiced_life(VREGIME_A, hash_=True, moments=500)

    def _check(self, perturb, moves: bool) -> None:
        org = _copy_org(self.base)
        d0, s0, x0 = org.state_hash(), org.row_hash(), scratch_digest(org)
        perturb(org)
        d1, s1, x1 = org.state_hash(), org.row_hash(), scratch_digest(org)
        self.assertEqual(s1, x1, "the running witness equals its from-scratch recompute after the perturbation")
        if moves:
            self.assertNotEqual(d0, d1, "precondition: the dense digest reads this part")
            self.assertNotEqual(s0, s1, "the sparse witness must see what the dense one sees")
        else:
            self.assertEqual(d0, d1, "precondition: the dense digest ignores this part")
            self.assertEqual(s0, s1, "the sparse witness must ignore what the dense one ignores")

    @staticmethod
    def _masked(org, name):
        p = org.sound_meets[name]
        r, c = np.nonzero(p.mask[:p.a.n, :p.b.n])
        return p, int(r[0]), int(c[0])

    def test_the_sound_area_parts(self) -> None:
        n = self.base.sound.n
        self.assertGreater(n, 2)
        for name, f in (("alive", lambda o: o.sound.alive.__setitem__(1, 1 - o.sound.alive[1])),
                        ("misfires", lambda o: o.sound.misfires.__setitem__(1, o.sound.misfires[1] + 1)),
                        ("c_sound", lambda o: o.c_sound.__setitem__("births_refused_budget_sound", o.c_sound["births_refused_budget_sound"] + 1))):
            with self.subTest(part=name):
                self._check(f, moves=True)

    def test_the_sound_cells_are_read_by_the_digest_function(self) -> None:
        """A born cell rewritten in place is what the append-only law FORBIDS (the running cells digest folds a cell once, at birth — the
        writer sweep pins `.cells` to birth/grow/load); the digest FUNCTION still reads every born cell: a from-scratch recompute moves."""
        org = _copy_org(self.base)
        d0, x0 = org.state_hash(), scratch_digest(org)
        org.sound.cells[1, 0] = np.nextafter(org.sound.cells[1, 0], np.inf)
        self.assertNotEqual(org.state_hash(), d0)
        self.assertNotEqual(scratch_digest(org), x0)

    def test_each_meetings_block_values_and_mask(self) -> None:
        for name in ("sight-sound", "sound-words"):
            with self.subTest(meeting=name, part="W one ulp"):
                def f(o, name=name):
                    p, r, c = self._masked(o, name)
                    p.W[r, c] = np.nextafter(p.W[r, c], np.inf)
                self._check(f, moves=True)
            with self.subTest(meeting=name, part="strikes"):
                def f(o, name=name):
                    p, r, c = self._masked(o, name)
                    p.strikes[r, c] = p.strikes[r, c] + 1
                self._check(f, moves=True)
            with self.subTest(meeting=name, part="a new masked coordinate (W 0, allowed by the invariant), marked as HEBB marks"):
                def f(o, name=name):
                    p = o.sound_meets[name]
                    r, c = [(int(r), int(c)) for r, c in zip(*np.nonzero(p.mask[:p.a.n, :p.b.n] == 0))][0]
                    p.mask[r, c] = 1
                    o._witness.mark(r, pair=name)
                self._check(f, moves=True)
            with self.subTest(meeting=name, part="edges_log"):
                self._check(lambda o, name=name: o.sound_meets[name].edges_log.append((o.t, 0, 0)), moves=True)
            with self.subTest(meeting=name, part="prunes_log"):
                self._check(lambda o, name=name: o.sound_meets[name].prunes_log.append((o.t, 0, 0)), moves=True)

    def test_the_padding_moves_neither(self) -> None:
        for name in ("sight-sound", "sound-words"):
            for arr in ("W", "strikes", "mask"):
                with self.subTest(meeting=name, part=f"{arr} beyond the live block"):
                    def f(o, name=name, arr=arr):
                        p = o.sound_meets[name]
                        A = getattr(p, arr)
                        r, c = A.shape[0] - 1, A.shape[1] - 1
                        self.assertTrue(r >= p.a.n or c >= p.b.n)
                        A[r, c] = np.nextafter(0.0, 1.0) if arr == "W" else 1
                    self._check(f, moves=False)
        for part in ("cells", "alive", "misfires"):
            with self.subTest(part=f"sound.{part} beyond the live prefix"):
                def f(o, part=part):
                    A = getattr(o.sound, part)
                    self.assertGreater(A.shape[0], o.sound.n)
                    if part == "cells":
                        A[-1, 0] = 0.5
                    else:
                        A[-1] = 1
                self._check(f, moves=False)

    def test_the_gate_opens_on_a_moved_sound_counter_before_any_sound_cell(self) -> None:
        """The dense digest reads the sound state once the area holds a cell OR a sound counter moved (`births_refused_budget_sound` can move
        with n == 0: a chord refused by the ONE budget). The sparse gate is the same gate."""
        org = voiced_life(VREGIME_A, hash_=True, voiced=False, moments=200)
        self.assertEqual(org.sound.n, 0)
        d0, s0 = org.state_hash(), org.row_hash()
        org.c_sound["births_refused_budget_sound"] += 1
        self.assertNotEqual(org.state_hash(), d0)
        self.assertNotEqual(org.row_hash(), s0)
        self.assertEqual(org.row_hash(), scratch_digest(org))


class TestThePlantInAMeeting(unittest.TestCase):
    """The designer's RED (ALPHA4-2-PREREG §7.2 seam 5): a one-ulp plant in a sound meeting's live block moves the dense state_hash — and
    must move the per-row hash at that call and at every later one (the planted edge is on a thing shown once and never again, so the life
    never rewrites it); a plant in a meeting's PADDING moves neither witness at any call."""

    def _twin(self, plant: str):
        rng = np.random.default_rng(99)
        p_new, w_new, c_new = _unit(rng.standard_normal(64)), _unit(rng.standard_normal(208)), _unit(rng.standard_normal(SND_DIM))
        org = voiced_life(VREGIME_B, hash_=True, moments=400)
        org.moment(p_new, w_new, x_snd=c_new)                   # a thing shown ONCE, with its voice: its sight cell and its sound cell are new
        s, u = org.sight.n - 1, org.sound.n - 1
        ss = org.sound_meets["sight-sound"]
        self.assertEqual(int(ss.mask[s, u]), 1, "the new sight cell and the new sound cell are wired in sight<->sound")
        self.assertTrue(0.0 < float(ss.W[s, u]) < 1.0)
        if plant == "live":
            ss.W[s, u] = np.nextafter(ss.W[s, u], np.inf)
        elif plant == "padding":
            ss.W[ss.W.shape[0] - 1, ss.W.shape[1] - 1] = np.nextafter(0.0, 1.0)
        out = [(org.row_hash(), org.state_hash())]
        rng2 = np.random.default_rng(7)
        P = [org.sight.cells[i].copy() for i in range(3)]
        Wd = [org.words.cells[j].copy() for j in range(2)]
        Cs = [org.sound.cells[k].copy() for k in range(2)]
        for m in range(120):                                    # the old things again: never the planted thing, its word or its chord
            org.moment(_unit(P[m % 3] + 0.05 * rng2.standard_normal(64)), Wd[m % 2], x_snd=Cs[m % 2])
            out.append((org.row_hash(), org.state_hash()))
        return out, org

    def test_live_plant_seen_by_both_witnesses_at_every_later_call(self) -> None:
        base, _o = self._twin("none")
        live, _o2 = self._twin("live")
        self.assertEqual(len(base), len(live))
        sparse_diff = [a[0] != b[0] for a, b in zip(base, live)]
        dense_diff = [a[1] != b[1] for a, b in zip(base, live)]
        self.assertTrue(all(dense_diff), "precondition: the dense witness sees the plant at every call")
        self.assertTrue(all(sparse_diff), f"the sparse witness missed the meeting plant at calls {[i for i, d in enumerate(sparse_diff) if not d][:10]}")

    def test_padding_plant_moves_neither_witness(self) -> None:
        base, _o = self._twin("none")
        pad, org = self._twin("padding")
        self.assertEqual(base, pad, "a perturbation beyond a meeting's live block must move neither witness")
        ss = org.sound_meets["sight-sound"]
        r, c = ss.W.shape[0] - 1, ss.W.shape[1] - 1
        self.assertTrue(r >= org.sight.n or c >= org.sound.n)
        self.assertNotEqual(float(ss.W[r, c]), 0.0, "the plant is really there")


class TestTheInvariantInTheMeetings(unittest.TestCase):
    """The sparse form is lossless BY THE INVARIANT (W != 0 => mask = 1 and strikes != 0 => mask = 1 inside a live block; the padding all
    zero) — asserted for BOTH meetings after both regimes; a violation inside a meeting's live block moves the dense witness and NOT the
    sparse one, which is exactly why it is asserted (and why the writer sweep pins every writer)."""

    ZERO = {"W_nonzero_mask0": 0, "strikes_nonzero_mask0": 0, "padding_nonzero": 0}

    def test_zero_violations_after_both_regimes(self) -> None:
        from genome.witness import sound_invariant_violations
        for reg in (VREGIME_A, VREGIME_B):
            org = voiced_life(reg, hash_=True)
            v = sound_invariant_violations(org)
            self.assertEqual(set(v), {"sight-sound", "sound-words"})
            for name, counts in v.items():
                with self.subTest(regime=reg["theta_n"], meeting=name):
                    self.assertEqual(counts, self.ZERO)

    def test_a_violation_inside_a_meeting_moves_the_dense_and_not_the_sparse(self) -> None:
        from genome.witness import sound_invariant_violations
        org = voiced_life(VREGIME_B, hash_=True)
        ss = org.sound_meets["sight-sound"]
        rr, cc = np.nonzero(ss.mask[:org.sight.n, :org.sound.n] == 0)
        r, c = int(rr[0]), int(cc[0])
        s0, d0 = org.row_hash(), org.state_hash()
        ss.W[r, c] = np.nextafter(0.0, 1.0)
        self.assertEqual(sound_invariant_violations(org)["sight-sound"]["W_nonzero_mask0"], 1)
        self.assertNotEqual(org.state_hash(), d0)
        self.assertEqual(org.row_hash(), s0)

    def test_the_main_block_report_is_unchanged(self) -> None:
        from genome.witness import invariant_violations
        org = voiced_life(VREGIME_A, hash_=True, moments=300)
        self.assertEqual(invariant_violations(org), self.ZERO, "the sight<->words report keeps its three keys (COST's tests compare it whole)")


class TestAnEmptySoundAreaIsHashNeutral(unittest.TestCase):
    """VOICE's V3 fixture clause for the dense digest, now for the sparse one (proof (b)'s unit form): HASH + AREA sound + both MEETs on a
    life that never hears a chord == HASH alone, at EVERY moment, both witnesses."""

    def test_never_voiced_equals_the_soundless_genome_at_every_moment(self) -> None:
        seen = {"voice": [], "plain": []}
        for key, sound in (("voice", True), ("plain", False)):
            voiced_life(VREGIME_A, hash_=True, voiced=False, sound=sound, moments=400,
                        each=lambda o, m, key=key: seen[key].append((o.row_hash(), o.state_hash())))
        self.assertEqual(len(seen["voice"]), 400)
        self.assertEqual(seen["voice"], seen["plain"])

    def test_the_voice_moves_the_sparse_digest(self) -> None:
        a = voiced_life(VREGIME_A, hash_=True, voiced=False, moments=50)
        b = voiced_life(VREGIME_A, hash_=True, voiced=True, moments=50)
        self.assertGreater(b.sound.n, 0)
        self.assertNotEqual(a.row_hash(), b.row_hash())


class TestUndeclaredHashOnAVoicedLife(unittest.TestCase):
    def test_row_hash_is_state_hash_at_every_moment(self) -> None:
        """The negative control: HASH undeclared -> row_hash() IS state_hash() on a voiced life too (no witness is built)."""
        pairs = []
        org = voiced_life(VREGIME_A, hash_=False, moments=300, each=lambda o, m: pairs.append((o.row_hash(), o.state_hash())))
        self.assertIsNone(getattr(org, "_witness", None))
        self.assertGreater(org.sound.n, 0)
        self.assertTrue(all(a == b for a, b in pairs))

    def test_sparse_is_domain_separated_from_dense_on_a_voiced_organism(self) -> None:
        org = voiced_life(VREGIME_B, hash_=True, moments=200)
        self.assertNotEqual(org.row_hash(), org.state_hash())


class TestSaveLoadUnderHashAndVoice(unittest.TestCase):
    def _roundtrip(self, grow: bool) -> None:
        org = voiced_life(VREGIME_A, hash_=True, grow=grow, moments=400)
        self.assertGreater(org.sound.n, 0)
        sparse_before, dense_before = org.row_hash(), org.state_hash()
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        org.save(d / "organism")
        meta = json.loads((d / "organism.json").read_text())
        self.assertEqual(meta["state_hash"], dense_before, "the snapshot meta keeps the DENSE digest")
        o2 = Organism.load(d / "organism", org.g)
        self.assertEqual(o2.row_hash(), sparse_before, "the sparse row hash after load equals the one before save (the sound state included)")
        self.assertEqual(o2.state_hash(), dense_before)

    def test_roundtrip_nmax(self) -> None:
        self._roundtrip(grow=False)

    def test_roundtrip_grow(self) -> None:
        self._roundtrip(grow=True)

    def test_an_old_soundless_snapshot_loads_under_hash_and_voice(self) -> None:
        plain = voiced_life(VREGIME_A, hash_=True, voiced=False, sound=False, moments=200)
        d = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, d, True)
        plain.save(d / "o")
        back = Organism.load(d / "o", parse_genome(voiced_text(VREGIME_A["theta_n"], VREGIME_A["theta_snd"], hash_=True, sound=True)))
        self.assertEqual(back.sound.n, 0)
        self.assertEqual(back.row_hash(), plain.row_hash(), "an empty sound area loaded from an old snapshot is hash-neutral")


if __name__ == "__main__":
    unittest.main()
