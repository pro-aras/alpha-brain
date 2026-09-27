"""probe_cost_hmax.py — is A1's per-event cost the LEARNING or the pre-allocated HMAX buffers? (edit: Fable 5.1 (brain r2), 2026-09-27 19:16 +0400)
B1.1 seed 1 (summary.json, 7 slots in parallel): A1 430 ms/event, A1-LOCAL 277, A1-NO-SLEEP 147, A1-BPTT-AWAKE 250 — while the
fixed-width twins at the same live width (A1-FIXED at H 112, A1-ATT, A1-MA) read 47–51 ms/event. The growing arms allocate
(HMAX = 1,024)-wide tensors and the local trainer touches every element of every parameter at every step. Here: the SAME arm, the
same 40 TEACH rows, the same rule, at hmax 1024 (A1's) and at hmax 112 (its final width), one thread; ms per TEACH row printed.
Run:  OPENBLAS_NUM_THREADS=1 PYTHONPATH=/data/dev/genome-wt-b1-tape2 nice -n 19 /data/dev/venvs/brain/bin/python -u probe_cost_hmax.py
"""
import json
import time

import torch

from brain.arms.soft.arm import ArmA1

torch.set_num_threads(1)
root, seed = "/data/dev/brain-runs/b1.1", "20261001"
rows = [json.loads(l) for l in open(f"{root}/{seed}/tape.jsonl")]
teach = [r for r in rows if r["kind"] == "TEACH"][:40]
for hmax, h0 in ((1024, 64), (1024, 112), (112, 112)):
    arm = ArmA1(seed=int(seed), config={"variant": "A1", "cache_dir": f"{root}/cache/{seed}", "seed": int(seed), "h0": h0, "hmax": hmax})
    for r in teach[:5]:
        arm.fit_event(r)                                            # warm up
    t0 = time.perf_counter()
    for r in teach[5:]:
        arm.fit_event(r)
    ms = (time.perf_counter() - t0) * 1000 / len(teach[5:])
    n_params = sum(p.numel() for p in arm._params)
    print(f"hmax {hmax:4d} · h0 {h0:3d} · alive {arm.engine.active:3d} · allocated parameters {n_params:,} · {ms:.1f} ms per TEACH row (7 steps, the awake local rule)")
