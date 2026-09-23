# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:57 +0400 — A4L-COST (docs/briefs/A4L-COST.md task 1; docs/A4-LADDER-PREREG.md
# §2.1): the per-row state witness made SPARSE — `HASH sparse; dense at snapshot`. A new module, part of the organism (it writes no file).
# edit: Claude (Opus 5.5, A4 seam-5 builder), 2026-09-23 15:01 +0400 — SEAM 5 (COST x VOICE; docs/ALPHA4-2-PREREG.md §7.2 on a42): the witness
# now covers A4L-VOICE's sound area and both sound meetings, under the dense digest's own gate, and every writer of a meeting's MASK marks it
# (`pair=`). Byte-identical to COST's digest for every organism with no sound state (no area, or an empty one with no sound counter moved).
"""genome/witness.py — HASH sparse; dense at snapshot: the per-row state witness over the SPARSE state.

WHAT IT COVERS — exactly what Organism.state_hash (the dense witness) covers, in a sparse form:
  for each area: n, cells[:n] (a RUNNING sha256: cells are append-only — written once at birth, never rewritten), alive[:n], misfires[:n];
  the edge block: every masked (sight, word) coordinate of the live block [:n_s, :n_w] in row-major order (as int64 keys s << 32 | t)
  with its W, strikes and mask values; t; budget_left; the counters (json, sort_keys); the four append-only logs (a RUNNING sha256 over
  their json text, entry by entry, plus their lengths); own_band/own_band_n over the live prefix when own_band_n[:n].any() (the dense
  hash's own gate). A domain tag leads, so a sparse digest can never equal a dense one.
  SEAM 5 — the SOUND state (A4L-VOICE), LAST, under the dense digest's own gate (`sound is not None and (sound.n > 0 or any(c_sound))`: an
  EMPTY sound area with no sound counter moved adds NO byte, so a soundless organism's digest is COST's byte-for-byte): a sub-tag; the sound
  area's n, cells[:n] (running), alive[:n], misfires[:n]; for each meeting in name order (sight-sound, sound-words — the dense order): its
  name, the masked coordinates of ITS live block [:a.n, :b.n] (keys r << 32 | c) with their W, strikes and mask, and its two append-only
  logs (running sha256 + lengths, keyed "<meeting>:<log>"); then c_sound (json, sort_keys).

LOSSLESS BY THE INVARIANT: inside the live block W != 0 (bit-level) => mask != 0 and strikes != 0 => mask != 0, and the padding beyond it
  is all zero (`invariant_violations`; 0 of 5.19 M cells on the 10:54 snapshot copy) — every bit the dense block carries sits at a
  masked coordinate, so the triples carry every bit. The same invariant holds in each sound meeting (the SAME writers' formulas, written
  over a `_Pair`): `sound_invariant_violations`.

THE CONSTRUCTION — the brief's (b), in its cheapest safe form; the bars decided it, MEASURED on the 10:54 snapshot copy (6,896 x 753 born,
  10,940 edges, load 3.9): the dense digest 144.2 ms a call (the live block 119.5); (a) a scan of mask[:n_s, :n_w] 24.0 ms before a byte
  is hashed (quadratic in n_s x n_w, over C2's 10 ms witness bar at these sizes already); a gather at KNOWN keys + sha256 0.87 ms. So the
  ONE piece of incremental state for the block is the SET of masked coordinates, which changes only where the MASK changes —
  Organism._hebb, ._prune and ._merge, each of which marks the sight rows it touched (`mark` / `mark_rows`); the set is re-read for those
  rows only at the next digest. Every W/strikes/mask VALUE is gathered fresh on every call, so a VALUE write the witness is not told about
  (DELTA's column updates touch every row wired to a word — 11 to 54 rows at 10:54; SCALE touches every row) is still seen: per-row
  value digests would need every one of those writers to mark too. tests/genome/test_a4l_cost_writer_sweep.py pins every writer of the
  block (and of the cells and the logs) to one this module knows.
  SEAM 5: each sound meeting keeps its OWN coordinate set (`_Block`), told by `mark(row, pair=<meeting>)` / `mark_rows(rows, pair=...)`
  from the meeting's MASK writers (Organism._pair_hebb, ._pair_prune, ._merge_pair_edges); the sight<->words set is ALSO told by
  Organism._area_merge (a sight or word cell merged INSIDE a sound meeting moves the sight<->words mask through `_merge_rows` — a write the
  attribute sweep could not see until the sweep learned the alias road). No `pair=` = the sight<->words block, exactly as before.

THE CLOCK: `timed` reads time.perf_counter around a row hash (STATUS.hash_ms_last). creature/mind.py never reads a clock (G4-PREREG §2.3,
  pinned by tests/creature/test_mind_parity.py): the organism measures its witness here and the mind only carries the float — the same
  division creature/think_thread.py keeps for think_ms. The number never enters a digest or a decision.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

TAG = b"A4L-COST sparse witness v1\x00"
LOGS = ("births", "merges", "edges_log", "prunes_log")
SOUND_TAG = b"A4 seam 5: the sound area and its meetings\x00"     # inside the sound gate only (a soundless digest never carries it)
PAIR_LOGS = ("edges_log", "prunes_log")


def _json_num(o):
    """json.dumps `default`: numpy integers and floats render as the Python number they equal (genome/machinery.py's own `_json_num`,
    repeated here so this module imports nothing from machinery — machinery imports it)."""
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def timed(fn: Callable[[], str]) -> Tuple[str, float]:
    """(fn(), its wall ms) — the witness's own cost, for STATUS.hash_ms_last only."""
    t0 = time.perf_counter()
    v = fn()
    return v, (time.perf_counter() - t0) * 1000.0


def scan_keys(mask: np.ndarray, n_s: int, n_w: int) -> np.ndarray:
    """Every masked coordinate of the live block, row-major, as int64 keys s << 32 | t (a full scan: construction (a)'s cost)."""
    r, c = np.nonzero(mask[:n_s, :n_w])
    return (r.astype(np.int64) << 32) | c.astype(np.int64)


def _block_violations(Wf: np.ndarray, Mf: np.ndarray, Sf: np.ndarray, n_r: int, n_c: int) -> Dict[str, int]:
    """The invariant over ONE matrix (full arrays + its live block [:n_r, :n_c])."""
    W, M, S = Wf[:n_r, :n_c], Mf[:n_r, :n_c], Sf[:n_r, :n_c]
    return {"W_nonzero_mask0": int(((W.view(np.uint64) != 0) & (M == 0)).sum()),
            "strikes_nonzero_mask0": int(((S != 0) & (M == 0)).sum()),
            "padding_nonzero": int(np.count_nonzero(Wf.view(np.uint64)) - np.count_nonzero(W.view(np.uint64))
                                   + np.count_nonzero(Mf) - np.count_nonzero(M) + np.count_nonzero(Sf) - np.count_nonzero(S))}


def invariant_violations(org) -> Dict[str, int]:
    """The invariant the sparse form is lossless by, counted: W bits != 0 where mask == 0 inside the live block (bit-level, so a -0.0
    counts), strikes != 0 where mask == 0, and any non-zero bit in the padding beyond the live block."""
    return _block_violations(org.W, org.mask, org.strikes, int(org.sight.n), int(org.words.n))


def sound_invariant_violations(org) -> Dict[str, Dict[str, int]]:
    """SEAM 5: the same invariant over each sound meeting's own live block [:a.n, :b.n] — {meeting name: the three counts} ({} with none)."""
    return {name: _block_violations(p.W, p.mask, p.strikes, int(p.a.n), int(p.b.n))
            for name, p in sorted(getattr(org, "sound_meets", {}).items())}


class _Block:
    """The ONE piece of incremental state of one edge matrix's live block: the sorted set of its masked coordinates (int64 r << 32 | c) and
    the rows whose MASK a writer changed since the last digest. The sight<->words W has one; SEAM 5: each sound meeting has its own."""

    __slots__ = ("keys", "dirty")

    def __init__(self) -> None:
        self.keys: Optional[np.ndarray] = None          # None = scan at the next digest
        self.dirty: set = set()

    def flush(self, mask: np.ndarray, n_r: int, n_c: int) -> np.ndarray:
        """The coordinate set, re-read only where the mask changed (a full scan at the first digest, or when so many rows changed that a
        scan is the cheaper road) — COST's `_flush`, verbatim, over any matrix."""
        if self.keys is None or 8 * len(self.dirty) > max(n_r, 1):
            self.keys = scan_keys(mask, n_r, n_c)
            self.dirty.clear()
            return self.keys
        if self.dirty:
            D = np.array(sorted(r for r in self.dirty if 0 <= r < n_r), dtype=np.int64)
            self.dirty.clear()
            if D.size:
                old = self.keys
                lo = np.searchsorted(old, D << 32)
                hi = np.searchsorted(old, (D + 1) << 32)
                delta = np.zeros(old.size + 1, dtype=np.int64)
                np.add.at(delta, lo, 1)
                np.add.at(delta, hi, -1)
                kept = old[np.cumsum(delta[:-1]) == 0]            # every key outside the changed rows, still sorted
                ri, ci = np.nonzero(mask[D, :n_c])
                new = (D[ri] << 32) | ci.astype(np.int64)          # the changed rows re-read, row-major
                self.keys = np.insert(kept, np.searchsorted(kept, new), new)
        return self.keys


def _gather(h, keys: np.ndarray, W: np.ndarray, strikes: np.ndarray, mask: np.ndarray) -> None:
    """Fold one block's coordinate set and the VALUES at it (read fresh every call) into the digest."""
    s, t = keys >> 32, keys & 0xFFFFFFFF
    h.update(np.int64(keys.size).tobytes())
    h.update(keys.tobytes())
    h.update(W[s, t].tobytes())
    h.update(strikes[s, t].tobytes())
    h.update(mask[s, t].tobytes())


class SparseWitness:
    """The sparse witness of ONE organism (Organism._witness, built only when HASH is declared; the think's shadow never carries one)."""

    def __init__(self) -> None:
        self._block = _Block()                         # the sight<->words W
        self._pairs: Dict[str, _Block] = {}            # SEAM 5: meeting name -> its own coordinate set
        self._cells: Dict[str, list] = {}              # area name -> [running sha256, rows folded]
        self._logs: Dict[str, list] = {}               # log name -> [running sha256, entries folded]

    # ------------------------------------------------------------------ the writers tell the witness which rows' MASK they changed
    def _blk(self, pair: Optional[str]) -> _Block:
        if pair is None:
            return self._block
        b = self._pairs.get(pair)
        if b is None:
            b = self._pairs[pair] = _Block()
        return b

    def mark(self, row, pair: Optional[str] = None) -> None:
        """`pair=None`: a row of the sight<->words W; `pair=<meeting name>` (SEAM 5): a row of that sound meeting."""
        self._blk(pair).dirty.add(int(row))

    def mark_rows(self, rows, pair: Optional[str] = None) -> None:
        self._blk(pair).dirty.update(np.asarray(rows, dtype=np.int64).ravel().tolist())

    # ------------------------------------------------------------------ the coordinate set of the sight<->words W (COST's name kept)
    def _flush(self, org) -> np.ndarray:
        return self._block.flush(org.mask, int(org.sight.n), int(org.words.n))

    # ------------------------------------------------------------------ the append-only parts, folded once
    def _running_cells(self, area, n: int) -> bytes:
        ent = self._cells.get(area.name)
        if ent is None or ent[1] > n:
            ent = [hashlib.sha256(), 0]
            self._cells[area.name] = ent
        if n > ent[1]:
            ent[0].update(np.ascontiguousarray(area.cells[ent[1]:n]).tobytes())
            ent[1] = n
        return ent[0].copy().digest()

    def _running_log(self, log: List[tuple], name: str) -> Tuple[int, bytes]:
        """The running sha256 of json.dumps(log)[1:-1] — the entries' json joined by ", " (json's own list separator, so the stream is the
        same however the appends were chunked between two digests)."""
        ent = self._logs.get(name)
        if ent is None or ent[1] > len(log):
            ent = [hashlib.sha256(), 0]
            self._logs[name] = ent
        k = ent[1]
        if len(log) > k:
            text = json.dumps(log[k:], default=_json_num)[1:-1]
            ent[0].update(((", " if k else "") + text).encode())
            ent[1] = len(log)
        return ent[1], ent[0].copy().digest()

    # ------------------------------------------------------------------ the digest
    def digest(self, org) -> str:
        h = hashlib.sha256(TAG)
        for a in (org.sight, org.words):
            n = int(a.n)
            h.update(np.int64(n).tobytes())
            h.update(self._running_cells(a, n))
            h.update(a.alive[:n].tobytes())
            h.update(a.misfires[:n].tobytes())
        _gather(h, self._flush(org), org.W, org.strikes, org.mask)
        h.update(np.int64(org.t).tobytes())
        h.update(np.int64(org.budget_left).tobytes())
        h.update(json.dumps(org.c, sort_keys=True, default=_json_num).encode())
        for name in LOGS:
            k, d = self._running_log(getattr(org, name), name)
            h.update(np.int64(k).tobytes())
            h.update(d)
        n_s = int(org.sight.n)
        if org.sight.own_band is not None and bool(org.sight.own_band_n[:n_s].any()):
            h.update(org.sight.own_band[:n_s].tobytes())
            h.update(org.sight.own_band_n[:n_s].tobytes())
        # SEAM 5: the sound state, LAST, under state_hash()'s own gate — `getattr`: a shadow Organism (the think thread's) has no sound
        # attributes (and is never hashed); an EMPTY area with no sound counter moved adds no byte (COST's digest, byte-for-byte).
        snd = getattr(org, "sound", None)
        if snd is not None and (snd.n > 0 or any(org.c_sound.values())):
            n = int(snd.n)
            h.update(SOUND_TAG)
            h.update(np.int64(n).tobytes())
            h.update(self._running_cells(snd, n))
            h.update(snd.alive[:n].tobytes())
            h.update(snd.misfires[:n].tobytes())
            for name in sorted(org.sound_meets):
                # `meet`, never `p`: tools/gate_g4.py's writer sweep resolves a variable NAME module-wide, last write wins — a `p = ...` here
                # masked COST's planted leak (`p = root / 'state' / ...; p.write_text(...)`) in a copy of this module (found by that test).
                meet = org.sound_meets[name]
                h.update(name.encode())
                _gather(h, self._blk(name).flush(meet.mask, int(meet.a.n), int(meet.b.n)), meet.W, meet.strikes, meet.mask)
                for log in PAIR_LOGS:
                    k, d = self._running_log(getattr(meet, log), f"{name}:{log}")
                    h.update(np.int64(k).tobytes())
                    h.update(d)
            h.update(json.dumps(org.c_sound, sort_keys=True, default=_json_num).encode())
        return h.hexdigest()


def scratch_digest(org) -> str:
    """The same digest from nothing: a FRESH witness (a full scan, every running part folded from the start) — the reference the
    incremental one must equal after every moment (the tests, the seams, the C1 driver)."""
    return SparseWitness().digest(org)
