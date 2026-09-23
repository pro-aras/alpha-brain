# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:57 +0400 — A4L-COST (docs/briefs/A4L-COST.md task 1; docs/A4-LADDER-PREREG.md
# §2.1): the per-row state witness made SPARSE — `HASH sparse; dense at snapshot`. A new module, part of the organism (it writes no file).
"""genome/witness.py — HASH sparse; dense at snapshot: the per-row state witness over the SPARSE state.

WHAT IT COVERS — exactly what Organism.state_hash (the dense witness) covers, in a sparse form:
  for each area: n, cells[:n] (a RUNNING sha256: cells are append-only — written once at birth, never rewritten), alive[:n], misfires[:n];
  the edge block: every masked (sight, word) coordinate of the live block [:n_s, :n_w] in row-major order (as int64 keys s << 32 | t)
  with its W, strikes and mask values; t; budget_left; the counters (json, sort_keys); the four append-only logs (a RUNNING sha256 over
  their json text, entry by entry, plus their lengths); own_band/own_band_n over the live prefix when own_band_n[:n].any() (the dense
  hash's own gate). A domain tag leads, so a sparse digest can never equal a dense one.

LOSSLESS BY THE INVARIANT: inside the live block W != 0 (bit-level) => mask != 0 and strikes != 0 => mask != 0, and the padding beyond it
  is all zero (`invariant_violations`; 0 of 5.19 M cells on the 10:54 snapshot copy) — every bit the dense block carries sits at a
  masked coordinate, so the triples carry every bit.

THE CONSTRUCTION — the brief's (b), in its cheapest safe form; the bars decided it, MEASURED on the 10:54 snapshot copy (6,896 x 753 born,
  10,940 edges, load 3.9): the dense digest 144.2 ms a call (the live block 119.5); (a) a scan of mask[:n_s, :n_w] 24.0 ms before a byte
  is hashed (quadratic in n_s x n_w, over C2's 10 ms witness bar at these sizes already); a gather at KNOWN keys + sha256 0.87 ms. So the
  ONE piece of incremental state for the block is the SET of masked coordinates, which changes only where the MASK changes —
  Organism._hebb, ._prune and ._merge, each of which marks the sight rows it touched (`mark` / `mark_rows`); the set is re-read for those
  rows only at the next digest. Every W/strikes/mask VALUE is gathered fresh on every call, so a VALUE write the witness is not told about
  (DELTA's column updates touch every row wired to a word — 11 to 54 rows at 10:54; SCALE touches every row) is still seen: per-row
  value digests would need every one of those writers to mark too. tests/genome/test_a4l_cost_writer_sweep.py pins every writer of the
  block (and of the cells and the logs) to one this module knows.

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


def invariant_violations(org) -> Dict[str, int]:
    """The invariant the sparse form is lossless by, counted: W bits != 0 where mask == 0 inside the live block (bit-level, so a -0.0
    counts), strikes != 0 where mask == 0, and any non-zero bit in the padding beyond the live block."""
    n_s, n_w = int(org.sight.n), int(org.words.n)
    W, M, S = org.W[:n_s, :n_w], org.mask[:n_s, :n_w], org.strikes[:n_s, :n_w]
    return {"W_nonzero_mask0": int(((W.view(np.uint64) != 0) & (M == 0)).sum()),
            "strikes_nonzero_mask0": int(((S != 0) & (M == 0)).sum()),
            "padding_nonzero": int(np.count_nonzero(org.W.view(np.uint64)) - np.count_nonzero(W.view(np.uint64))
                                   + np.count_nonzero(org.mask) - np.count_nonzero(M) + np.count_nonzero(org.strikes) - np.count_nonzero(S))}


class SparseWitness:
    """The sparse witness of ONE organism (Organism._witness, built only when HASH is declared; the think's shadow never carries one)."""

    def __init__(self) -> None:
        self._keys: Optional[np.ndarray] = None       # sorted int64 s << 32 | t of every masked coordinate; None = scan at the next digest
        self._dirty: set = set()                       # sight rows whose MASK a writer changed since the last digest
        self._cells: Dict[str, list] = {}              # area name -> [running sha256, rows folded]
        self._logs: Dict[str, list] = {}               # log name -> [running sha256, entries folded]

    # ------------------------------------------------------------------ the writers tell the witness which rows' MASK they changed
    def mark(self, row) -> None:
        self._dirty.add(int(row))

    def mark_rows(self, rows) -> None:
        self._dirty.update(np.asarray(rows, dtype=np.int64).ravel().tolist())

    # ------------------------------------------------------------------ the coordinate set, re-read only where the mask changed
    def _flush(self, org) -> np.ndarray:
        n_s, n_w = int(org.sight.n), int(org.words.n)
        if self._keys is None or 8 * len(self._dirty) > max(n_s, 1):
            self._keys = scan_keys(org.mask, n_s, n_w)          # the first digest, or so many rows changed that a scan is the cheaper road
            self._dirty.clear()
            return self._keys
        if self._dirty:
            D = np.array(sorted(r for r in self._dirty if 0 <= r < n_s), dtype=np.int64)
            self._dirty.clear()
            if D.size:
                old = self._keys
                lo = np.searchsorted(old, D << 32)
                hi = np.searchsorted(old, (D + 1) << 32)
                delta = np.zeros(old.size + 1, dtype=np.int64)
                np.add.at(delta, lo, 1)
                np.add.at(delta, hi, -1)
                kept = old[np.cumsum(delta[:-1]) == 0]            # every key outside the changed rows, still sorted
                ri, ci = np.nonzero(org.mask[D, :n_w])
                new = (D[ri] << 32) | ci.astype(np.int64)          # the changed rows re-read, row-major
                self._keys = np.insert(kept, np.searchsorted(kept, new), new)
        return self._keys

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
        keys = self._flush(org)
        s, t = keys >> 32, keys & 0xFFFFFFFF
        h.update(np.int64(keys.size).tobytes())
        h.update(keys.tobytes())
        h.update(org.W[s, t].tobytes())
        h.update(org.strikes[s, t].tobytes())
        h.update(org.mask[s, t].tobytes())
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
        return h.hexdigest()


def scratch_digest(org) -> str:
    """The same digest from nothing: a FRESH witness (a full scan, every running part folded from the start) — the reference the
    incremental one must equal after every moment (the tests, the seams, the C1 driver)."""
    return SparseWitness().digest(org)
