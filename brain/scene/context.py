"""context.py — T-MEM-5 (= S1c-3) «WHERE SEPARATES»: the CONTEXT learner. LEARNER side: the context is the room the learner
CHOSE, its own act (an efference copy); the world tells it nothing.

edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 17:50 +0400 — new module, written to docs/brain/memory/PREREG-TMEM5.md (genome-wt-brain3
ce41448, sha 30121082…, final) §1:
  logit_w(z, r) = g_r · (v_w · z) + b_w + c_{r,w},  g_r ≥ 0 (initialised 1.0, clipped at 0), c_{r,w} initialised 0;
  every parameter by the SAME delta rule from the same error e_w and responsibilities R_{t,w}:
    ΔV_w  = lr · e_w · g_r · Σ_t R_{t,w} z_t          — the chain rule's factor g_r, applied ONCE, here and nowhere else;
    Δb_w  = lr · e_w · Σ_t R_{t,w}                    — S1b-1's step, unchanged;
    Δg_r  = lr_g · Σ_w e_w · Σ_t R_{t,w} (v_w · z_t)  — lr_g = 0.005 (PREREG-TMEM5 AMENDMENT 2 §2.3; the PREREG's 0.001 failed the
                                                          fixed-point toy on N's budget);
    Δc_{r,w} = lr · e_w · Σ_t R_{t,w}.
The episodic write, the prototypes and the stores read the same responsibilities (now from the context logits). With the
context FROZEN (g ≡ 1, c ≡ 0, neither learned) every number is S1c's A-RW's, bit for bit: x · 1.0 and x + 0.0 are exact — the
identity pin of THE FIRST GATE 1. The fixed test set reads the SHARED map alone (the base class's answering, g = 1, c = 0).

edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:12 +0400 — PREREG-TMEM5-AMEND-1 (brain-design-3 95b6e48, sha ab9a5fca…, final) §4 (10):
the ACT beside every stored row (`store_c`, per word per meeting, the context the learner was in when it stored it — its own
efference copy, never the world's), so A-READ+WHERE can key the store by (word, room); `row_contexts` lists them in
memory.StoreRows.from_learner's row order.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

from .learners import LR_S1B1, RWLearner, sigmoid
from .pickers import P_CLIP

# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:45 +0400 — PREREG-TMEM5 AMENDMENT 2 (brain-design-3 3c28401, sha 8638072d…, final) §2.3:
# lr_g = 0.005, the smallest value of the gate's grid whose toy passes both clauses read with the MEMORY bar's own statistic at
# all three seeds (tools/scene/diag/tmem5_toy_lr_grid.out); THE FIRST GATE stopped at 0.001 (g_B 0.31 / 0.32 / 0.24 after 500).
LR_G = 0.005


class CtxLearner(RWLearner):
    def __init__(self, rooms: Sequence[str], lr: float = LR_S1B1, lr_g: float = LR_G, learn_gain: bool = True,
                 learn_bias: bool = True, dim: Optional[int] = None):
        if dim is None:
            super().__init__(lr=lr)
        else:
            super().__init__(lr=lr, dim=dim)
        self.rooms = list(rooms)
        self.g: Dict[str, float] = {r: 1.0 for r in self.rooms}
        self.c: Dict[str, np.ndarray] = {r: np.zeros(0) for r in self.rooms}
        self.lr_g = float(lr_g)
        self.learn_gain, self.learn_bias = bool(learn_gain), bool(learn_bias)
        self.ctx: Optional[str] = None
        self.store_c: List[List[Optional[str]]] = []      # per word per meeting: the act (the context) when it was stored

    def _add_word(self, w: str) -> int:
        i = super()._add_word(w)
        for r in self.rooms:
            self.c[r] = np.append(self.c[r], 0.0)
        self.store_c.append([])
        return i

    def set_context(self, room: Optional[str]) -> None:
        if room is not None and room not in self.g:
            raise ValueError(f"no such context: {room!r}")
        self.ctx = room

    def _gc(self, room: Optional[str]):
        if room is None:
            return 1.0, np.zeros(len(self.words))
        return self.g[room], self.c[room]

    def train_scene(self, raw: np.ndarray, words: Sequence[str], referent: Optional[int] = None,
                    rng: Optional[np.random.Generator] = None, project=None) -> None:
        """RWLearner.train_scene with the context in the logits and the chain rule in the steps (module doc); a learner
        of this class is never an oracle (the referent is never read)."""
        raw = np.atleast_2d(np.asarray(raw, dtype=np.float64))
        self.scenes += 1
        self.ear.hear(words)
        if raw.shape[0] == 0:
            return
        self.stats.observe(raw)
        Z = self.stats.standardise(raw)
        said = list(dict.fromkeys(words))
        new = [w for w in said if w not in self.index]
        if new:
            known = [i for i in range(len(self.words)) if self.proto_w[i] > 0]
            bands = self.bands() if self.words else np.zeros(0)
            t_star = self._farthest(Z, known, bands, rng if rng is not None else np.random.default_rng(0))
            band0 = float(np.median(bands[known])) if known else float("inf")
            for w in new:
                i = self._add_word(w)
                self.proto_sum[i] = Z[t_star]
                self.proto_w[i] = 1.0
                self.store_z[i].append(Z[t_star][None, :].copy())
                self.store_r[i].append(np.ones(1))
                self.store_x[i].append(raw[t_star][None, :].copy())
                self.store_t[i].append(self.scenes)
                self.store_c[i].append(self.ctx)
                self.episodic_band[i] = band0
        if not self.words:
            return
        room = self.ctx
        g, c = self._gc(room)
        Mz = Z @ self.V.T                                    # (H, W) the map's term v_w · z_t
        L = Mz * g + self.b[None, :] + c[None, :]
        Pm = sigmoid(L)
        p_scene = 1.0 - np.prod(1.0 - Pm, axis=0)
        y = np.array([1.0 if w in said else 0.0 for w in self.words])
        e = y - p_scene
        S = Pm.sum(axis=0)
        R = np.where(S[None, :] > 0, Pm / np.where(S > 0, S, 1.0)[None, :], 1.0 / Z.shape[0])
        upd = self.lr * e[:, None] * (R.T @ Z) * g           # the chain rule's g_r, ONCE
        db = self.lr * e * R.sum(axis=0)
        dg = self.lr_g * float(np.sum(e * np.sum(R * Mz, axis=0))) if (self.learn_gain and room is not None) else 0.0
        dc = self.lr * e * R.sum(axis=0) if (self.learn_bias and room is not None) else None
        if project is not None:
            upd, db = project(self, upd, db)
        self.V += upd
        self.b += db
        if dg != 0.0:
            self.g[room] = max(0.0, self.g[room] + dg)
        if dc is not None:
            self.c[room] = self.c[room] + dc
        for w in said:
            j = self.index[w]
            if w not in new:
                r = R[:, j]
                self.proto_sum[j] += r @ Z
                self.proto_w[j] += float(r.sum())
                self.store_z[j].append(Z.copy())
                self.store_r[j].append(r.copy())
                self.store_x[j].append(raw.copy())
                self.store_t[j].append(self.scenes)
                self.store_c[j].append(room)
            self.meetings[j] += 1

    def scene_loss(self, raw: np.ndarray, words: Sequence[str], room: Optional[str]) -> float:
        """The cross-entropy of ONE scene over the heard words under context `room` (the finite-difference pin's L)."""
        Z = self.stats.standardise(np.atleast_2d(raw))
        g, c = self._gc(room)
        L = (Z @ self.V.T) * g + self.b[None, :] + c[None, :]
        Pm = sigmoid(L)
        P = np.clip(1.0 - np.prod(1.0 - Pm, axis=0), 1e-300, 1.0 - 1e-16)
        y = np.array([1.0 if w in words else 0.0 for w in self.words])
        return -float(np.sum(y * np.log(P) + (1.0 - y) * np.log(1.0 - P)))


def row_contexts(learner) -> List[Optional[str]]:
    """The stored act of every row, in memory.StoreRows.from_learner's order (word, then meeting, then hypothesis)."""
    out: List[Optional[str]] = []
    for j in range(len(learner.words)):
        for xs, cs in zip(learner.store_x[j], learner.store_c[j]):
            out += [cs] * int(xs.shape[0])
    return out


def ctx_hyp_probs(learner, X: np.ndarray, vocab: Sequence[str], room: Optional[str]) -> np.ndarray:
    """pickers.hyp_probs under context `room` — the same sub-matrix product, then × g_r, + c_{r,w} (exact identity when
    g = 1.0 and c = 0.0)."""
    if X.shape[0] == 0:
        return np.zeros((0, len(vocab)))
    Z = learner.stats.standardise(X)
    logit = np.zeros((Z.shape[0], len(vocab)))
    cols = [(c, learner.index[w]) for c, w in enumerate(vocab) if w in learner.index]
    if cols:
        cc = [c for c, _j in cols]
        jj = [j for _c, j in cols]
        g, cr = learner._gc(room) if hasattr(learner, "_gc") else (1.0, np.zeros(len(learner.words)))
        logit[:, cc] = (Z @ learner.V[jj].T) * g + learner.b[jj][None, :] + cr[jj][None, :]
    return sigmoid(logit)


def ctx_window_loss(learner, ws, room: Optional[str]) -> float:
    """pickers.window_loss under context `room` (the window of room k is read with context k)."""
    p = ctx_hyp_probs(learner, ws.X, ws.vocab, room)
    out = np.zeros(ws.n)
    for i in range(ws.n):
        a, b = int(ws.starts[i]), int(ws.starts[i + 1])
        P = 1.0 - np.prod(1.0 - p[a:b], axis=0) if b > a else np.zeros(len(ws.vocab))
        P = np.clip(P, P_CLIP, 1.0 - P_CLIP)
        y = ws.Y[i]
        out[i] = -float(np.sum(y * np.log(P) + (1.0 - y) * np.log(1.0 - P)))
    return float(np.mean(out))
