# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 19:13 +0400 — a DIAGNOSIS (read by no verdict): THE FIRST GATE at 9e23231 STOPPED at step 2 —
# the rebuilt toy (AMENDMENT 3 §3: A1, A2 sharing words, B by N's rule) fails at EVERY lr_g of the grid under the SAID-only gain:
# g_B's last-10 mean stays 1.00–1.28 while both learnable gains drift UP (1.2 → 2.7). Two questions, on the gate's own toy code:
#   (1) WHY g_B does not fall: every B-scene's said-only gain term Σ_{w said} e_w Σ_t R_tw (v_w · z_t), recorded before its step
#       from the state that step reads, split by the scene's number of things H (a said word is random in B, but its
#       responsibilities pick, among 1–3 things, the one the map finds most compatible — a selection the H = 1 scenes lack);
#   (2) does the rebuilt toy SHOW the life's pathology under the OLD all-words gain (a learnable room's g collapsing), i.e. is
#       it the instrument AMENDMENT 3 asked for — the same toy, the same seeds, the gain's step over every word.
# The control: this script's said-only toy reproduces the gate's toy record (lr_g 0.005, seeds 0–2) at every block, or nothing
# below it is read.
# Run: cd /data/dev/brain-runs/scene/code-<sha> && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import json
from unittest import mock

import numpy as np

from brain.scene import context as CX
from brain.scene import learners as Lr
from brain.scene import run_tmem5 as T5

TERMS = []            # (room, H, the said-only term, the unsaid words' term) per scene, before its step


class Probe(CX.CtxLearner):
    all_words = False

    def train_scene(self, raw, words, referent=None, rng=None, project=None):
        raw2 = np.atleast_2d(np.asarray(raw, dtype=np.float64))
        room = self.ctx
        if raw2.shape[0] and self.words and room is not None:
            st = __import__("copy").deepcopy(self.stats)
            st.observe(raw2)
            Z = st.standardise(raw2)
            g, c = self._gc(room)
            Mz = Z @ self.V.T
            Pm = Lr.sigmoid(Mz * g + self.b[None, :] + c[None, :])
            p_scene = 1.0 - np.prod(1.0 - Pm, axis=0)
            y = np.array([1.0 if w in words else 0.0 for w in self.words])
            e = y - p_scene
            S_ = Pm.sum(axis=0)
            R = np.where(S_[None, :] > 0, Pm / np.where(S_ > 0, S_, 1.0)[None, :], 1.0 / Z.shape[0])
            per = e * np.sum(R * Mz, axis=0)
            TERMS.append((room, int(raw2.shape[0]), float(per[y > 0].sum()), float(per[y == 0].sum())))
            if self.all_words:
                g0 = self.g[room]
                out = super().train_scene(raw, words, referent=referent, rng=rng, project=project)
                self.g[room] = max(0.0, g0 + self.lr_g * float(per.sum()))        # the OLD rule: every word's term
                return out
        return super().train_scene(raw, words, referent=referent, rng=rng, project=project)


class ProbeAll(Probe):
    all_words = True


def run(cls, seed):
    with mock.patch.object(CX, "CtxLearner", cls):
        return T5.toy_life(seed, True, 0.005)


gate = json.loads((T5.ROOT / "gate" / "step2" / "toy.json").read_text())
law = gate["grid"]["0.005"]["runs"]
TERMS.clear()
said = {s: run(Probe, s) for s in T5.TOY_SEEDS}
same = all(said[s]["g"] == law[str(s)]["g"] for s in T5.TOY_SEEDS)
print(f"control: the probe's said-only toy equals the gate's toy record (lr_g 0.005, seeds 0–2) at every block: {same}")
if not same:
    raise SystemExit("the control misses — nothing below is read")
T = np.array([(("A1", "A2", "B").index(r), h, a, b) for r, h, a, b in TERMS])
print("\n(1) the gain's terms per scene under the SAID-only rule (seeds 0–2 pooled; mean ± sd; the unsaid term is what the rule drops):")
for k, room in enumerate(("A1", "A2", "B")):
    for h in (1, 2, 3):
        m = (T[:, 0] == k) & (T[:, 1] == h)
        if m.any():
            print(f"   {room} H = {h}: n {int(m.sum()):>4} · said term {T[m, 2].mean():+.4f} ± {T[m, 2].std():.4f} · unsaid term "
                  f"{T[m, 3].mean():+.4f} ± {T[m, 3].std():.4f}")
    m = T[:, 0] == k
    print(f"   {room} all: said {T[m, 2].sum():+.1f} · unsaid {T[m, 3].sum():+.1f} (sums over its scenes)")
TERMS.clear()
old = {s: run(ProbeAll, s) for s in T5.TOY_SEEDS}
print("\n(2) the SAME rebuilt toy under the OLD all-words gain (lr_g 0.005):")
for s in T5.TOY_SEEDS:
    rd = T5.toy_reading(old[s])
    print(f"   seed {s}: g_B's last-10 mean {rd['g_B_last10']:.4f} · g_A1 {rd['g_A_last10']['A1']:.4f}, g_A2 {rd['g_A_last10']['A2']:.4f} "
          f"(minima {rd['g_A_min']['A1']:.3f} / {rd['g_A_min']['A2']:.3f}) · ends " + " ".join(f"{q} {v:.3f}" for q, v in rd["g_end"].items())
          + f" · the toy passes: {rd['pass']}")
