# edit: Claude (Opus 5.5, T-MEM-5 builder), 2026-09-28 18:38 +0400 — a DIAGNOSIS (read by no verdict): THE FIRST GATE of T-MEM-5 stopped at step 2
# (the fixed-point toy misses at lr_g 0.001: g_B 0.31 / 0.32 / 0.24 after its 500 B-scenes, the bar ≤ 0.1). lr_g is the knob
# and its amendment is the seat's; this prints the SAME toy (the gate's own code, construction and generators, nothing else
# changed) at a grid of lr_g, so the amendment can be sized to N's budget. Its lr_g 0.001 row must equal the gate's record
# (gate/step2/toy.json) exactly, or nothing below it is read. Per seed: g_B after its 500 B-scenes, the first block (and
# B-scene count) at which g_B ≤ 0.1, g_A's minimum over the 200 blocks, and the sd of g_B over its last 10 B-blocks beside
# 0.1 × g_A (the MEMORY bar's noise clause read on the toy).
# Run: cd /data/dev/brain-runs/scene/code-<sha> && PYTHONPATH=$PWD OPENBLAS_NUM_THREADS=1 nice -n 19 /usr/bin/python3 -B <this file>
import json
from pathlib import Path
from unittest import mock

import numpy as np

from brain.scene import context as CX
from brain.scene import run_tmem5 as T5

GRID = (0.001, 0.002, 0.003, 0.005, 0.01)
gate = json.loads((T5.ROOT / "gate" / "step2" / "toy.json").read_text())
out = {}
for lr_g in GRID:
    with mock.patch.object(CX, "LR_G", lr_g):
        rows = {s: T5.toy_life(s, True) for s in T5.TOY_SEEDS}
    if lr_g == 0.001:
        same = all(rows[s]["g_B"] == gate["runs"][str(s)]["bias"]["g_B"] and rows[s]["g_A"] == gate["runs"][str(s)]["bias"]["g_A"]
                   for s in T5.TOY_SEEDS)
        print(f"control: lr_g 0.001 reproduces the gate's toy record exactly: {same}")
        if not same:
            raise SystemExit("the control misses — nothing below is read")
    out[lr_g] = {}
    for s, r in rows.items():
        last10 = r["g_B_at_B_blocks"][-10:]
        sd = float(np.std(last10, ddof=1))
        out[lr_g][s] = {"g_B_end": r["g_B_end"], "first": r["first_g_B_le_bar"], "g_A_min": r["g_A_min"], "g_A_end": r["g_A_end"],
                        "g_B_last10_mean": float(np.mean(last10)), "g_B_last10_sd": sd, "noise_bar": 0.1 * r["g_A_end"],
                        "g_A_argmin_block": int(np.argmin(r["g_A"])) + 1, "g_A_every_20": r["g_A"][19::20]}
        print(f"lr_g {lr_g:<6} seed {s}: g_B after 500 B-scenes {r['g_B_end']:.4f} · first ≤ 0.1 at "
              f"{('block ' + str(r['first_g_B_le_bar'][0]) + ' after ' + str(r['first_g_B_le_bar'][1]) + ' B-scenes') if r['first_g_B_le_bar'] else '—'} · "
              f"g_A min {r['g_A_min']:.4f} end {r['g_A_end']:.4f} · g_B over its last 10 B-blocks: mean {np.mean(last10):.4f}, sd {sd:.4f} "
              f"(vs 0.1 × g_A {0.1 * r['g_A_end']:.4f}) · toy passes: {r['g_B_end'] <= T5.TOY_GB_BAR and r['g_A_min'] >= T5.TOY_GA_BAR} · "
              f"g_A's minimum at block {int(np.argmin(r['g_A'])) + 1}; g_A every 20 blocks " + ", ".join(f"{v:.3f}" for v in r["g_A"][19::20]))
Path(T5.ROOT / "gate" / "diag").mkdir(parents=True, exist_ok=True)
(T5.ROOT / "gate" / "diag" / "toy_lr_grid.json").write_text(json.dumps({str(k): v for k, v in out.items()}, indent=1) + "\n")
