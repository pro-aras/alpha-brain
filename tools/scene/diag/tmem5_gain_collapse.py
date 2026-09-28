# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:55 +0400 — a DIAGNOSIS (read by no verdict): THE FIRST GATE's step 4 print (RANDOM-CTX,
# 60 blocks, seed 20261301, lr_g 0.005) shows a LEARNABLE room's gain collapsing — g_R1 0.988 → 0.096 by block 60, falling at
# every R1 visit while R1's own drop stays positive — beside g_N → 0. This re-runs the same life (the gate's own code, pools and
# generators) with a learner that records, BEFORE each scene's step and from the state that step reads, every word's share of
# the gain's step, e_w · Σ_t R_tw (v_w · z_t), summed per (room, word); its g trajectory must equal the gate's record exactly
# (the control), or nothing below it is read.
# Run: cd /data/dev/brain-runs/scene/code-<sha> && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import copy
import json
from unittest import mock

import numpy as np

from brain.scene import context as CX
from brain.scene import learners as Lr
from brain.scene import run_s1c as S
from brain.scene import run_tmem1 as T1
from brain.scene import run_tmem5 as T5

CONTRIB = {}


class DiagCtx(CX.CtxLearner):
    def train_scene(self, raw, words, referent=None, rng=None, project=None):
        raw2 = np.atleast_2d(np.asarray(raw, dtype=np.float64))
        room = self.ctx
        if raw2.shape[0] and self.words and room is not None:
            st = copy.deepcopy(self.stats)
            st.observe(raw2)
            Z = st.standardise(raw2)
            g, c = self._gc(room)
            Mz = Z @ self.V.T
            Pm = Lr.sigmoid(Mz * g + self.b[None, :] + c[None, :])
            p_scene = 1.0 - np.prod(1.0 - Pm, axis=0)
            said = set(words)
            y = np.array([1.0 if w in said else 0.0 for w in self.words])
            e = y - p_scene
            S_ = Pm.sum(axis=0)
            R = np.where(S_[None, :] > 0, Pm / np.where(S_ > 0, S_, 1.0)[None, :], 1.0 / Z.shape[0])
            per = e * np.sum(R * Mz, axis=0)
            d = CONTRIB.setdefault(room, {})
            for j, w in enumerate(self.words):
                t = d.setdefault(w, [0.0, 0.0, 0])                  # [sum when said, sum when not said, scenes]
                t[0 if w in said else 1] += float(per[j])
                t[2] += 1
        return super().train_scene(raw, words, referent=referent, rng=rng, project=project)


def new_diag(kind, rooms=T5.ROOMS):
    gain, bias = T5.LEARNER_KINDS[kind]
    return DiagCtx(rooms, lr=Lr.LR_S1B1, lr_g=CX.LR_G, learn_gain=gain, learn_bias=bias)


data = S.RoomData(T5.POOLS_ROOT, T5.GATE_SEED, T5.ROOMS)
test = T1.TestSetM()
with mock.patch.object(T5, "new_ctx_learner", new_diag):
    r = T5.life5(data, test, "RANDOM-CTX", n_blocks=T5.GATE4_BLOCKS, keep_learner=True)
gate = json.loads((T5.ROOT / "gate" / "step4" / "RANDOM-CTX-60.json").read_text())
same = [c["g"] for c in r["ctx_record"]] == [c["g"] for c in gate["ctx_record"]]
print(f"control: the diagnostic life's gains equal the gate's step-4 record at every block: {same}")
if not same:
    raise SystemExit("the control misses — nothing below is read")
L = r["_learner"]
print(f"lr_g {CX.LR_G} · the gains at block {T5.GATE4_BLOCKS}: " + " ".join(f"{k} {v:.3f}" for k, v in L.g.items())
      + f" · scenes per act {r['trained_under']}")
for room in T5.ROOMS:
    d = CONTRIB.get(room, {})
    tot = sum(v[0] + v[1] for v in d.values())
    said = sum(v[0] for v in d.values())
    unsaid = sum(v[1] for v in d.values())
    print(f"\n{room}: Σ over its scenes of the gain's step ÷ lr_g = {tot:+.2f} (words SAID in the scene {said:+.2f} · words NOT said {unsaid:+.2f})")
    rows = sorted(d.items(), key=lambda kv: kv[1][0] + kv[1][1])
    for w, (a, b, n) in rows:
        print(f"   {w:<9} said {a:+8.2f} · not said {b:+8.2f} · total {a + b:+8.2f}")
    print(f"   |c_{room}| {np.linalg.norm(L.c[room]):.3f} · c_{room} per word: " + " ".join(f"{w} {L.c[room][L.index[w]]:+.2f}" for w in L.words))
