"""machinery.py — the ribosome: reads a genome text and runs an organism by it.

edit: Claude (Fable 5.1), 2026-09-19 16:0x +04 — G0 rung 0 (docs/G0-PREREG.md §1, §10).
edit: Claude (Fable 5.1), 2026-09-19 16:09 +04 — §11: the retina as a list of fixed steps (gate G-a's finding); winners must resonate.
edit: Claude (Fable 5.1), 2026-09-19 16:14 +04 — §11 amendments 4–6 (from the toy): redundant error births refused; ABSTAIN's second is a competitor that answers back differently; a question lights the resonating winners, not one cell.

Laws of this file:
- The genome is text. A gene this machinery does not know REFUSES to start (GenomeError),
  never silently ignored. A gene whose value is still a placeholder (THETA_N / THETA_M
  before gate G-a) refuses too.
- The organism holds cells (fixed prototypes), one shared edge matrix between the two
  areas, and counters. It holds NO label of any kind: the birth log carries only
  (moment, area, cell, reason). The truth lives in the runner's ledger, never here.
- Nothing is removed for disuse. Removal happens only by PRUNE (an edge that stayed under
  the floor for 3 chances) and MERGE (two alike cells with the same answer).
- No randomness inside a life: every step is a deterministic function of the genome and
  the stream, so two lives from the same genome + stream are byte-identical (mark vii).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


class GenomeError(Exception):
    """A gene the machinery cannot run. The organism does not start."""


# ============================================================================ the genome
@dataclass
class Genome:
    seed: int
    eye: Tuple[int, int]            # 24×24
    ear_letters: int                # 8
    ear_blank_zero: bool            # §10 clause 9: False = 27 symbols, True = 26 (blank is zero)
    retina: Tuple[str, ...]         # the fixed front's steps, e.g. ('thresh0.25','centre','blur0.8','pool3','hog8','hogcells8x6','unit')
    areas: Dict[str, str]           # area -> sense
    meet: Tuple[str, str]           # ('sight', 'words')
    theta_n: float                  # BIRTH novelty cos<THETA_N
    misfires: int                   # BIRTH error misfires N
    budget: int                     # BUDGET per arrival
    nmax: int
    kwta: int
    hebb_window: int
    lr: float
    prune_floor: float
    prune_chances: int
    theta_m: float
    scale_every: int
    stages: List[Tuple[int, str, int, Optional[int]]]   # (index, name, from, to)
    recall_k: int
    abstain_ratio: float
    text: str = field(default="", repr=False)

    @property
    def stage2_start(self) -> int:
        for _, name, a, _b in self.stages:
            if name == "meet":
                return a
        raise GenomeError("no STAGE named meet")

    def sight_dim(self) -> int:
        return retina_dim(self.retina)

    def words_dim(self) -> int:
        return self.ear_letters * (26 if self.ear_blank_zero else 27)


_NUM = r"[-+]?\d+(?:\.\d+)?"


def parse_genome(text: str) -> Genome:
    """Parse the genome text. Unknown gene → GenomeError. Placeholder value → GenomeError."""
    g: Dict[str, object] = {"areas": {}, "stages": [], "ear_blank_zero": False}
    seen = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        toks = line.split()
        gene, args = toks[0], toks[1:]
        a = " ".join(args)
        try:
            if gene == "SEED":
                g["seed"] = int(args[0])
            elif gene == "SENSE" and args[0] == "eye":
                m = re.fullmatch(r"(\d+)x(\d+) grey", a[4:].strip())
                if not m: raise GenomeError(f"SENSE eye: cannot read {a!r}")
                g["eye"] = (int(m.group(1)), int(m.group(2)))
            elif gene == "SENSE" and args[0] == "ear":
                m = re.fullmatch(r"letters (\d+)(?: blank=(zero|symbol))?", a[4:].strip())
                if not m: raise GenomeError(f"SENSE ear: cannot read {a!r}")
                g["ear_letters"] = int(m.group(1))
                g["ear_blank_zero"] = (m.group(2) == "zero")
            elif gene == "RETINA":
                for step in args:
                    if not re.fullmatch(r"thresh" + _NUM + r"|centre|blur" + _NUM + r"|pool\d+|hog\d+|hogcells\d+x\d+|unit", step):
                        raise GenomeError(f"RETINA: unknown fixed step {step!r} in {a!r}")
                if args[-1] != "unit": raise GenomeError("RETINA: the last step must be unit")
                g["retina"] = tuple(args)
            elif gene == "AREA":
                if len(args) != 3 or args[1] != "from": raise GenomeError(f"AREA: cannot read {a!r}")
                g["areas"][args[0]] = args[2]
            elif gene == "MEET":
                if len(args) != 2: raise GenomeError(f"MEET: cannot read {a!r}")
                g["meet"] = (args[0], args[1])
            elif gene == "BIRTH" and args[0] == "novelty":
                m = re.fullmatch(r"cos<(" + _NUM + ")", args[1])
                if not m: raise GenomeError(f"BIRTH novelty: THETA_N not set (gate G-a writes it): {a!r}")
                g["theta_n"] = float(m.group(1))
            elif gene == "BIRTH" and args[0] == "error":
                if args[1] != "misfires": raise GenomeError(f"BIRTH error: cannot read {a!r}")
                g["misfires"] = int(args[2])
            elif gene == "BUDGET":
                if args[1:] != ["per", "arrival"]: raise GenomeError(f"BUDGET: cannot read {a!r}")
                g["budget"] = int(args[0])
            elif gene == "NMAX":
                g["nmax"] = int(args[0])
            elif gene == "KWTA":
                g["kwta"] = int(args[0])
            elif gene == "HEBB":
                if args[0] != "window": raise GenomeError(f"HEBB: cannot read {a!r}")
                g["hebb_window"] = int(args[1])
            elif gene == "DELTA":
                if args[0] != "lr": raise GenomeError(f"DELTA: cannot read {a!r}")
                g["lr"] = float(args[1])
            elif gene == "PRUNE":
                m = re.fullmatch(r"w<(" + _NUM + r") after (\d+) chances", a)
                if not m: raise GenomeError(f"PRUNE: cannot read {a!r}")
                g["prune_floor"], g["prune_chances"] = float(m.group(1)), int(m.group(2))
            elif gene == "MERGE":
                m = re.fullmatch(r"cos>(" + _NUM + r") same-answer", a)
                if not m: raise GenomeError(f"MERGE: THETA_M not set (gate G-a writes it): {a!r}")
                g["theta_m"] = float(m.group(1))
            elif gene == "SCALE":
                m = re.fullmatch(r"every (\d+) moments", a)
                if not m: raise GenomeError(f"SCALE: cannot read {a!r}")
                g["scale_every"] = int(m.group(1))
            elif gene == "STAGE":
                m = re.fullmatch(r"(\d+) (\w+) moments (\d+)\.\.(\d*)", a)
                if not m: raise GenomeError(f"STAGE: cannot read {a!r}")
                g["stages"].append((int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)) if m.group(4) else None))
            elif gene == "RECALL":
                m = re.fullmatch(r"k=(\d+)", a)
                if not m: raise GenomeError(f"RECALL: cannot read {a!r}")
                g["recall_k"] = int(m.group(1))
            elif gene == "ABSTAIN":
                m = re.fullmatch(r"second/best > (" + _NUM + ")", a)
                if not m: raise GenomeError(f"ABSTAIN: cannot read {a!r}")
                g["abstain_ratio"] = float(m.group(1))
            else:
                raise GenomeError(f"unknown gene {gene!r} ({line!r}) — the machinery does not know it; the organism does not start")
        except (IndexError, ValueError) as e:
            raise GenomeError(f"{gene}: cannot read {line!r}: {e}") from e
        seen.add(gene)
    required = ["seed", "eye", "ear_letters", "retina", "meet", "theta_n", "misfires", "budget", "nmax", "kwta",
                "hebb_window", "lr", "prune_floor", "theta_m", "scale_every", "recall_k", "abstain_ratio"]
    missing = [k for k in required if k not in g]
    if missing:
        raise GenomeError(f"genome lacks {missing}")
    if set(g["areas"].keys()) != {"sight", "words"}:
        raise GenomeError(f"rung 0 needs AREA sight and AREA words, got {sorted(g['areas'])}")
    if not g["stages"]:
        raise GenomeError("no STAGE genes")
    if g["recall_k"] != 1:
        raise GenomeError("rung 0 machinery runs RECALL k=1 only")
    return Genome(text=text, **g)  # type: ignore[arg-type]


# ============================================================================ the retina
from scipy import ndimage as _ndi


def retina_dim(spec: Tuple[str, ...]) -> int:
    d = 0
    for step in spec:
        if step.startswith("pool"):
            k = int(step[4:]); d += (24 // k) ** 2
        elif step.startswith("hogcells"):
            k, nb = (int(v) for v in step[8:].split("x")); d += (24 // k) ** 2 * nb
        elif step.startswith("hog"):
            d += int(step[3:])
    if d == 0:
        raise GenomeError("RETINA: no feature step (pool/hog/hogcells)")
    return d


def _grad(p):
    gy = np.zeros_like(p); gx = np.zeros_like(p)
    gy[1:-1, :] = (p[2:, :] - p[:-2, :]) / 2.0
    gx[:, 1:-1] = (p[:, 2:] - p[:, :-2]) / 2.0
    return gx, gy


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def retina(pic: np.ndarray, spec: Tuple[str, ...] = ("thresh0.25", "centre", "blur0.8", "pool3", "hog8", "hogcells8x6", "unit")) -> np.ndarray:
    """RETINA — a FIXED front (never learned), run step by step as the gene lists them.
    thresh<t>: ink under t is dark (a contrast floor) · centre: shift the ink's centroid to the centre,
    sub-pixel, ZERO FILL (§10 clause 14) · blur<s>: gaussian · pool<k>: k×k mean pool → (24/k)² numbers,
    unit length · hog<n>: histogram of edge orientation over the whole picture, n bins, unit length ·
    hogcells<k>x<n>: the same per k×k cell · unit: the concatenation to unit length.
    Every feature block is unit length before concatenation so no block outweighs another by scale."""
    assert pic.shape == (24, 24)
    q = pic.astype(np.float64)
    feats = []
    for step in spec:
        if step.startswith("thresh"):
            t = float(step[6:]); q = np.where(q >= t, q, 0.0)
        elif step == "centre":
            total = q.sum()
            if total > 0:
                ys, xs = np.mgrid[0:24, 0:24]
                cy, cx = (ys * q).sum() / total, (xs * q).sum() / total
                q = _ndi.shift(q, (11.5 - cy, 11.5 - cx), order=1, mode="constant", cval=0.0)
        elif step.startswith("blur"):
            q = _ndi.gaussian_filter(q, float(step[4:]))
        elif step.startswith("pool"):
            k = int(step[4:]); n = 24 // k
            feats.append(_unit(q.reshape(n, k, n, k).mean(axis=(1, 3)).reshape(-1)))
        elif step.startswith("hogcells"):
            k, nb = (int(v) for v in step[8:].split("x")); n = 24 // k
            gx, gy = _grad(q); mag = np.hypot(gx, gy); b = ((np.arctan2(gy, gx) % np.pi) / np.pi * nb).astype(int) % nb
            out = np.zeros((n, n, nb))
            for i in range(n):
                for j in range(n):
                    sl = (slice(i * k, (i + 1) * k), slice(j * k, (j + 1) * k))
                    out[i, j] = np.bincount(b[sl].ravel(), weights=mag[sl].ravel(), minlength=nb)
            feats.append(_unit(out.reshape(-1)))
        elif step.startswith("hog"):
            nb = int(step[3:])
            gx, gy = _grad(q); mag = np.hypot(gx, gy); b = ((np.arctan2(gy, gx) % np.pi) / np.pi * nb).astype(int) % nb
            feats.append(_unit(np.bincount(b.ravel(), weights=mag.ravel(), minlength=nb)))
        elif step == "unit":
            return _unit(np.concatenate(feats))
        else:
            raise GenomeError(f"RETINA: unknown fixed step {step!r}")
    raise GenomeError("RETINA: no unit step")


# ============================================================================ the organism
class Area:
    def __init__(self, name: str, dim: int, nmax: int):
        self.name, self.dim, self.nmax = name, dim, nmax
        self.cells = np.zeros((nmax, dim), dtype=np.float64)
        self.alive = np.zeros(nmax, dtype=np.uint8)
        self.misfires = np.zeros(nmax, dtype=np.int64)
        self.n = 0                                  # cells ever born (ids 0..n-1)

    def alive_ids(self) -> np.ndarray:
        return np.flatnonzero(self.alive[: self.n])

    def cos(self, x: np.ndarray) -> np.ndarray:
        """cosine of x to every cell ever born (dead cells read -1 so they never win)."""
        c = self.cells[: self.n] @ x
        c[self.alive[: self.n] == 0] = -1.0
        return c


class Organism:
    """One organism: two areas, one edge matrix, counters. Flags `grow` / `wire` exist for the
    twins T-frozen (grow off after 10 cells) and T-nowire (HEBB off) — defaults ON."""

    def __init__(self, genome: Genome, *, wire: bool = True, frozen_after: Optional[int] = None):
        self.g = genome
        self.sight = Area("sight", genome.sight_dim(), genome.nmax)
        self.words = Area("words", genome.words_dim(), genome.nmax)
        self.W = np.zeros((genome.nmax, genome.nmax), dtype=np.float64)     # sight × words
        self.mask = np.zeros((genome.nmax, genome.nmax), dtype=np.uint8)
        self.strikes = np.zeros((genome.nmax, genome.nmax), dtype=np.uint8)
        self.t = 0                                   # moments lived
        self.wire = wire
        self.frozen_after = frozen_after
        self.budget_left = genome.budget
        self.arrivals = 0
        self.c = {                                   # counters (int64 in the hash)
            "births_novelty_sight": 0, "births_novelty_words": 0, "births_error_sight": 0, "births_error_words": 0,
            "births_refused_budget": 0, "births_refused_nmax": 0, "births_refused_frozen": 0, "births_refused_redundant": 0,
            "edges_born": 0, "edges_pruned": 0, "cells_merged_sight": 0, "cells_merged_words": 0,
            "scale_events": 0, "removed_for_disuse": 0,
        }
        self.births: List[Tuple[int, str, int, str]] = []      # (moment, area, cell, reason) — nothing else
        self.merges: List[Tuple[int, str, int, int]] = []      # (moment, area, kept, dropped)
        self.refusals_by_arrival: List[int] = []

    # ------------------------------------------------------------------ arrivals & budget
    def new_arrival(self) -> None:
        """A new set of things arrives: the birth budget is fresh (BUDGET N per arrival)."""
        if self.arrivals > 0:
            self.refusals_by_arrival.append(self.c["births_refused_budget"] - sum(self.refusals_by_arrival))
        self.arrivals += 1
        self.budget_left = self.g.budget

    def total_cells(self) -> int:
        return int(self.sight.alive.sum() + self.words.alive.sum())

    # ------------------------------------------------------------------ births
    def _birth(self, area: Area, x: np.ndarray, reason: str) -> Optional[int]:
        if self.frozen_after is not None and (self.sight.n + self.words.n) >= self.frozen_after:
            self.c["births_refused_frozen"] += 1
            return None
        if area.n >= area.nmax:
            self.c["births_refused_nmax"] += 1
            return None
        if self.budget_left <= 0:
            self.c["births_refused_budget"] += 1
            return None
        cid = area.n
        area.cells[cid] = x
        area.alive[cid] = 1
        area.n += 1
        self.budget_left -= 1
        self.c[f"births_{reason}_{area.name}"] += 1
        self.births.append((self.t, area.name, cid, reason))
        return cid

    def _resonate(self, area: Area, x: np.ndarray) -> List[int]:
        """BIRTH novelty + KWTA: births a cell if nothing resonates (cos < THETA_N), then returns
        the winners (top KWTA alive cells by cosine; a newborn is a winner in its birth moment)."""
        if area.n == 0 or float(area.cos(x).max()) < self.g.theta_n:
            self._birth(area, x, "novelty")
        if area.n == 0:
            return []
        c = area.cos(x)
        order = np.argsort(-c, kind="stable")
        # §11 clause 3: a winner must RESONATE (cos ≥ THETA_N) — up to KWTA of them; a cell that does not
        # resonate is not active and is never a delta-rule target (else the target marks every word right)
        winners = [int(i) for i in order[: self.g.kwta] if area.alive[i] and c[i] >= self.g.theta_n]
        return winners

    # ------------------------------------------------------------------ one moment
    def moment(self, x_s: np.ndarray, x_w: np.ndarray) -> None:
        S = self._resonate(self.sight, x_s)
        T = self._resonate(self.words, x_w)
        if self.wire and self.t >= self.g.stage2_start and S and T:
            self._hebb(S, T)
            self._delta(S, T)
            S, T = self._misfire(S, T, x_s, x_w)
            self._prune(S, T)
            self._merge(self.sight, S, axis=0)
            self._merge(self.words, T, axis=1)
        self.t += 1
        if self.t % self.g.scale_every == 0:
            self._scale()

    def _hebb(self, S: List[int], T: List[int]) -> None:
        for s in S:
            for t in T:
                if self.mask[s, t] == 0:
                    self.mask[s, t] = 1
                    self.W[s, t] = self.g.lr                  # §10 clause 3: born at w = lr
                    self.strikes[s, t] = 0
                    self.c["edges_born"] += 1

    def _delta(self, S: List[int], T: List[int]) -> None:
        lr = self.g.lr
        tgt_w = np.zeros(self.g.nmax); tgt_w[T] = 1.0
        for s in S:
            idx = self.mask[s] == 1
            self.W[s, idx] += lr * (tgt_w[idx] - self.W[s, idx])
        tgt_s = np.zeros(self.g.nmax); tgt_s[S] = 1.0
        for t in T:
            idx = self.mask[:, t] == 1
            self.W[idx, t] += lr * (tgt_s[idx] - self.W[idx, t])
        for s in S:
            np.clip(self.W[s], -1.0, 1.0, out=self.W[s])
        for t in T:
            np.clip(self.W[:, t], -1.0, 1.0, out=self.W[:, t])

    def _answer_of(self, area: Area, cid: int) -> Optional[int]:
        row = self.W[cid] if area is self.sight else self.W[:, cid]
        m = self.mask[cid] if area is self.sight else self.mask[:, cid]
        if not m.any():
            return None
        vals = np.where(m == 1, row, -np.inf)
        return int(np.argmax(vals))

    def _misfire(self, S, T, x_s, x_w):
        """BIRTH error misfires N: a cell whose strongest edge is not among this moment's winners on
        the other side misfires; N misfires → a cell is born beside it holding the current input."""
        for area, winners, other, x in ((self.sight, S, T, x_s), (self.words, T, S, x_w)):
            for cid in list(winners):
                ans = self._answer_of(area, cid)
                if ans is None:
                    continue
                if ans in other:
                    area.misfires[cid] = 0
                else:
                    area.misfires[cid] += 1
                    if area.misfires[cid] >= self.g.misfires:
                        area.misfires[cid] = 0
                        # §11 amendment 4: a cell born beside a cell it is already within THETA_M of would be
                        # born redundant (an immediate MERGE candidate) — refused, counted
                        if float(area.cells[cid] @ x) > self.g.theta_m:
                            self.c["births_refused_redundant"] += 1
                            continue
                        new = self._birth(area, x, "error")
                        if new is not None and new not in winners:
                            winners.append(new)
        return S, T

    def _prune(self, S: List[int], T: List[int]) -> None:
        fl, ch = self.g.prune_floor, self.g.prune_chances
        rows = np.array(sorted(set(S)), dtype=np.int64); cols = np.array(sorted(set(T)), dtype=np.int64)
        for sel in ((rows, slice(None)), (slice(None), cols)):
            m = self.mask[sel] == 1
            low = (np.abs(self.W[sel]) < fl) & m
            st = self.strikes[sel]
            st = np.where(low, np.minimum(st + 1, 255), 0).astype(np.uint8)
            self.strikes[sel] = st
            dead = (st >= ch) & m
            k = int(dead.sum())
            if k:
                W = self.W[sel]; M = self.mask[sel]; ST = self.strikes[sel]
                W[dead] = 0.0; M[dead] = 0; ST[dead] = 0
                self.W[sel] = W; self.mask[sel] = M; self.strikes[sel] = ST
                self.c["edges_pruned"] += k

    def _merge(self, area: Area, winners: List[int], axis: int) -> None:
        """MERGE cos>THETA_M same-answer: two alike winners with the same answer become one
        (the lower id is kept, rows averaged over the union of their edges)."""
        ws = sorted(set(w for w in winners if area.alive[w]))
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                if not (area.alive[a] and area.alive[b]):
                    continue
                if float(area.cells[a] @ area.cells[b]) <= self.g.theta_m:
                    continue
                aa, ab = self._answer_of(area, a), self._answer_of(area, b)
                if aa is None or ab is None or aa != ab:
                    continue
                if axis == 0:
                    ma, mb = self.mask[a].astype(np.float64), self.mask[b].astype(np.float64)
                    den = np.maximum(ma + mb, 1.0)
                    self.W[a] = (self.W[a] * ma + self.W[b] * mb) / den
                    self.mask[a] = ((ma + mb) > 0).astype(np.uint8)
                    self.strikes[a] = np.minimum(self.strikes[a], self.strikes[b])
                    self.W[b] = 0.0; self.mask[b] = 0; self.strikes[b] = 0
                else:
                    ma, mb = self.mask[:, a].astype(np.float64), self.mask[:, b].astype(np.float64)
                    den = np.maximum(ma + mb, 1.0)
                    self.W[:, a] = (self.W[:, a] * ma + self.W[:, b] * mb) / den
                    self.mask[:, a] = ((ma + mb) > 0).astype(np.uint8)
                    self.strikes[:, a] = np.minimum(self.strikes[:, a], self.strikes[:, b])
                    self.W[:, b] = 0.0; self.mask[:, b] = 0; self.strikes[:, b] = 0
                area.alive[b] = 0
                area.misfires[b] = 0
                self.c[f"cells_merged_{area.name}"] += 1
                self.merges.append((self.t, area.name, a, b))

    def _scale(self) -> None:
        """SCALE every N moments — synaptic scaling: a cell's edge vector is scaled down to unit norm
        when it exceeds it (never up, never removed)."""
        self.c["scale_events"] += 1
        for s in self.sight.alive_ids():
            n = float(np.linalg.norm(self.W[s]))
            if n > 1.0:
                self.W[s] /= n
        for t in self.words.alive_ids():
            n = float(np.linalg.norm(self.W[:, t]))
            if n > 1.0:
                self.W[:, t] /= n

    # ------------------------------------------------------------------ answering
    def _lit(self, area: Area, x: np.ndarray) -> Tuple[List[int], np.ndarray]:
        """§11 amendment 6: a question lights a side exactly as a moment does — its resonating cells
        (cos ≥ THETA_N), up to KWTA, best first. No birth: questions never change the organism."""
        if area.n == 0:
            return [], np.zeros(0)
        c = area.cos(x)
        order = np.argsort(-c, kind="stable")
        lit = [int(i) for i in order[: self.g.kwta] if area.alive[i] and c[i] >= self.g.theta_n]
        return lit, c

    def recall(self, side: str, x: np.ndarray) -> Dict[str, object]:
        """RECALL k=1 + ABSTAIN: light one side (its resonating winners, §11 am. 6; none → NOVEL), read
        the strongest edge from any lit cell to the other side (none positive → NOEDGE); ABSTAIN when the
        strongest COMPETING edge — to a cell whose own answer leads back outside the lit set (§11 am. 5) —
        is within the ratio (→ RATIO). Otherwise the answer cell. Never changes the organism."""
        area, other = (self.sight, self.words) if side == "sight" else (self.words, self.sight)
        lit, c = self._lit(area, x)
        if not lit:
            best_cos = float(c.max()) if len(c) else 0.0
            return {"cell": None, "reason": "novel", "lit": None, "best": 0.0, "second": 0.0, "cos": best_cos}
        lit_set = set(lit)
        cands: List[Tuple[float, int, int]] = []          # (edge, other cell, lit cell)
        for l in lit:
            row = self.W[l] if side == "sight" else self.W[:, l]
            m = (self.mask[l] if side == "sight" else self.mask[:, l]) == 1
            m &= other.alive == 1
            for j in np.flatnonzero(m):
                v = float(row[j])
                if v > 0.0:
                    cands.append((v, int(j), l))
        if not cands:
            return {"cell": None, "reason": "noedge", "lit": lit[0], "best": 0.0, "second": 0.0, "cos": float(c[lit[0]])}
        cands.sort(key=lambda z: (-z[0], z[1], z[2]))
        best, best_id, best_l = cands[0]
        second = 0.0
        for v, j, _l in cands[1:]:
            if j == best_id:
                continue
            if self._answer_of(other, j) not in lit_set:      # a competitor: it answers back to something not lit
                second = v
                break
        if second > 0.0 and second / best > self.g.abstain_ratio:
            return {"cell": None, "reason": "ratio", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l])}
        return {"cell": best_id, "reason": "answer", "lit": best_l, "best": best, "second": second, "cos": float(c[best_l])}

    def edge(self, side: str, x: np.ndarray, other_cell: int) -> float:
        """The strongest edge from the lit cells on `side` (none resonating → 0) to `other_cell` — Q3/Q4."""
        area = self.sight if side == "sight" else self.words
        lit, _c = self._lit(area, x)
        best = 0.0
        for l in lit:
            if side == "sight":
                v = float(self.W[l, other_cell]) if self.mask[l, other_cell] else 0.0
            else:
                v = float(self.W[other_cell, l]) if self.mask[other_cell, l] else 0.0
            best = max(best, v)
        return best

    # ------------------------------------------------------------------ identity
    def state_hash(self) -> str:
        """sha256 over the fixed-dtype state arrays and the counters (mark vii, the replay gate)."""
        h = hashlib.sha256()
        for a in (self.sight, self.words):
            h.update(a.cells[: a.n].tobytes()); h.update(a.alive.tobytes()); h.update(a.misfires.tobytes())
            h.update(np.int64(a.n).tobytes())
        h.update(self.W.tobytes()); h.update(self.mask.tobytes()); h.update(self.strikes.tobytes())
        h.update(np.int64(self.t).tobytes()); h.update(np.int64(self.budget_left).tobytes())
        h.update(json.dumps(self.c, sort_keys=True).encode())
        h.update(json.dumps(self.births).encode()); h.update(json.dumps(self.merges).encode())
        return h.hexdigest()

    def summary(self) -> Dict[str, object]:
        return {
            "moments": self.t, "cells_sight": int(self.sight.alive.sum()), "cells_words": int(self.words.alive.sum()),
            "cells_born_sight": self.sight.n, "cells_born_words": self.words.n,
            "edges_alive": int(self.mask.sum()), **self.c,
        }
