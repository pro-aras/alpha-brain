"""spectrum.py — the input-space spectrum of S1c's rooms: the WORLD'S OWN COUNTS for TOY B's ceilings (PREREG-TOY-NULLSPACE §0, §6).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:06 +0400 — new module. A MEASUREMENT of the world (no learner is trained, no
# projector is applied, no mark of the toy is read): the rows a word unit receives — the learner's own standardised hypothesis
# inputs augmented with the constant 1 for the bias, [z || 1] (147 numbers) — as the learner SAW them, in T-MEM-1's sequential order
# (R1 x 50 blocks, R2 x 50, R3 x 50, N x 50, 10 scenes a block, the first 500 scenes of each room's pool). The running
# standardiser (learners.RunningStandardiser) depends only on the scenes, so these rows are the same for every arm and every seed's
# arms; the learner's own path is observe(raw) then standardise(raw), copied here.

What it prints, per seed and for the cumulative rooms R1, R1+R2, R1+R2+R3 (the spans a projector for rooms 2, 3, 4 has to protect):
  rows            the number of hypothesis rows
  lambda_max      the largest eigenvalue of the uncentred covariance C = M'M / n
  eff. rank(tau)  #{eigenvalues > tau * lambda_max}, tau in TAUS  — how much of the 147-dim space the old rooms OCCUPY
  null dim(tau)   147 - eff. rank: the hard null space of Adam-NSCL's rule at that relative threshold
  OWM capacity    trace(I - P) for P = alpha (alpha I + G)^-1 and alpha_tau = tau * lambda_max(G_1) (G the Gram M'M): the OWM
                  paper's own capacity measure (rank of the removed part, soft) after each room
  outside(tau)    the share of the NEXT room's input energy that lies OUTSIDE the span of the old rooms' eigen-directions above tau:
                  what a learner can still move in the new room without touching the old inputs.

  PYTHONPATH=. python3 -m tools.toys.nullspace.spectrum [--root scratch/toys-pools] [--seeds 20261301,...]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import learners as Lr
from brain.scene import run_s1c as S

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "scratch" / "toys-pools"
ROOMS: Tuple[str, ...] = tuple(S.WORLDS["law"])        # R1, R2, R3, N — T-MEM-1's sequential order
BLOCKS_PER_ROOM = 50
BLOCK = 10
SEEDS: Tuple[int, ...] = tuple(range(20261301, 20261311))
TAUS: Tuple[float, ...] = (1e-1, 1e-2, 1e-3, 1e-4)
DIM = Lr.RW_DIM + 1                                    # 146 inputs + the bias's constant 1


def rows_as_seen(data, rooms: Sequence[str] = ROOMS, blocks_per_room: int = BLOCKS_PER_ROOM) -> Dict[str, np.ndarray]:
    """Per room, the stacked [z || 1] rows of its first blocks_per_room * 10 scenes, z standardised by the running statistics
    AS THEY STOOD when the scene was learned (observe first, then standardise — RWLearner.train_scene's own order)."""
    st = Lr.RunningStandardiser(Lr.RW_DIM)
    out: Dict[str, List[np.ndarray]] = {r: [] for r in rooms}
    cursor = {r: 0 for r in rooms}
    for block in range(1, len(rooms) * blocks_per_room + 1):
        room = rooms[(block - 1) // blocks_per_room]
        for i in range(cursor[room], cursor[room] + BLOCK):
            X, _words = data.visit_scene(room, i)
            X = np.atleast_2d(np.asarray(X, dtype=np.float64))
            if X.shape[0] == 0:
                continue                                 # train_scene returns before observing an empty scene
            st.observe(X)
            Z = st.standardise(X)
            out[room].append(np.hstack([Z, np.ones((Z.shape[0], 1))]))
        cursor[room] += BLOCK
    return {r: (np.vstack(v) if v else np.zeros((0, DIM))) for r, v in out.items()}


def gram(rows: np.ndarray) -> np.ndarray:
    return rows.T @ rows


def effective_rank(ev: np.ndarray, tau: float) -> int:
    return int((ev > tau * ev[0]).sum())


def owm_capacity(ev_gram: np.ndarray, alpha: float) -> float:
    """trace(I - P) with P = alpha (alpha I + G)^-1: sum_d E_d / (alpha + E_d), E_d the Gram's eigenvalues."""
    return float(np.sum(ev_gram / (alpha + ev_gram)))


def outside_share(old_rows: np.ndarray, new_rows: np.ndarray, tau: float) -> Tuple[int, float]:
    """The share of new_rows' energy outside the span of old_rows' eigen-directions whose eigenvalue exceeds tau * lambda_max."""
    C = gram(old_rows) / max(1, old_rows.shape[0])
    ev, U = np.linalg.eigh(C)
    keep = ev > tau * ev[-1]
    B = U[:, keep]
    inside = float(np.sum((new_rows @ B) ** 2) / np.sum(new_rows ** 2))
    return int(keep.sum()), 1.0 - inside


def seed_report(root: Path, seed: int, log=print) -> Dict[str, object]:
    data = S.RoomData(root, seed, ROOMS)
    rows = rows_as_seen(data)
    res: Dict[str, object] = {"seed": seed, "rows": {r: int(rows[r].shape[0]) for r in ROOMS}, "cum": {}, "outside": {}, "alpha": {}}
    log(f"seed {seed}: rows per room {res['rows']}")
    G1 = gram(rows[ROOMS[0]])
    lam1 = float(np.linalg.eigvalsh(G1)[-1])
    cum = np.zeros((0, DIM))
    for j, r in enumerate(ROOMS[:-1]):                 # the spans a projector for rooms j+2.. protects: after R1, R1+R2, R1+R2+R3
        cum = np.vstack([cum, rows[r]])
        evC = np.linalg.eigvalsh(gram(cum) / cum.shape[0])[::-1]
        evG = np.linalg.eigvalsh(gram(cum))[::-1]
        entry = {"n": int(cum.shape[0]), "lambda_max": float(evC[0]), "trace": float(evC.sum()),
                 "eff_rank": {t: effective_rank(evC, t) for t in TAUS},
                 "null_dim": {t: DIM - effective_rank(evC, t) for t in TAUS},
                 "owm_capacity": {t: owm_capacity(evG, t * lam1) for t in TAUS}}
        res["cum"]["+".join(ROOMS[:j + 1])] = entry
        nxt = ROOMS[j + 1]
        old_name = "+".join(ROOMS[:j + 1])
        outside = {t: outside_share(cum, rows[nxt], t) for t in TAUS}
        res["outside"][f"{old_name} -> {nxt}"] = outside
        lam_g = entry["lambda_max"] * entry["n"]               # lambda_max of the Gram G_j = n * lambda_max(C_j)
        log(f"  after {old_name:9s} n {entry['n']:5d} lam_max(C) {entry['lambda_max']:6.2f} lam_max(G) {lam_g:9.1f} — OWM and NSCL side by side per tau "
            f"(OWM keeps alpha_tau = tau*lam_max(G_1) FIXED, so its resolution alpha/lam_max(G_j) TIGHTENS; NSCL re-relativizes tau*lam_max(C_j) at every room):")
        for t in TAUS:
            log(f"     tau {t:<7g} OWM capacity trace(I-P) {entry['owm_capacity'][t]:6.1f} of {DIM} (alpha {t * lam1:9.1f}, alpha/lam_max(G_j) {t * lam1 / lam_g:.4f})"
                f"  |  NSCL removed rank {entry['eff_rank'][t]:3d}, null dim {entry['null_dim'][t]:3d}"
                f"  |  the next room {nxt}: energy outside the old span {outside[t][1]:.3f} ({outside[t][0]} dims kept)")
    res["alpha"] = {t: t * lam1 for t in TAUS}
    log("  alpha_tau = tau * lambda_max(G_1): " + "  ".join(f"{t:g}: {t * lam1:.1f}" for t in TAUS))
    return res


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--seeds", default=",".join(str(s) for s in SEEDS))
    a = ap.parse_args(argv)
    allres = [seed_report(a.root, int(s)) for s in a.seeds.split(",")]
    print("\nACROSS SEEDS (min / median / max of the eff. rank and the outside share):")
    for key in allres[0]["cum"]:
        for t in TAUS:
            v = [r["cum"][key]["eff_rank"][t] for r in allres]
            print(f"  {key:9s} eff.rank(tau={t:g}) {min(v)} / {int(np.median(v))} / {max(v)}")
    for key in allres[0]["outside"]:
        for t in TAUS:
            v = [r["outside"][key][t][1] for r in allres]
            print(f"  {key:12s} outside(tau={t:g}) {min(v):.3f} / {float(np.median(v)):.3f} / {max(v):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
