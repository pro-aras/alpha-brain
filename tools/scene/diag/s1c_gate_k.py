"""S1c THE FIRST GATE, step 2's miss — K is not flat (and U falls under 2 × the learnable rooms): READINGS ONLY, read by no
verdict (docs/brain/r3/S1C-HANDBACK.md).

edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:17 +0400 — the step-2 life re-run by the gate's own call (a control: it must reproduce
the gate's printed claims exactly), then replayed block by block from its own record to read, per block, L_K before and
after, K's own drops against its rises in the other rooms' blocks, the K column of the interference, and the per-word
terms of L_K and L_U at chosen boundaries.

  python3 -B tools/scene/diag/s1c_gate_k.py > /data/dev/brain-runs/scene-s1c/gate/diag_k.out
"""
from __future__ import annotations

import json

import numpy as np

from brain.scene import pickers as PK
from brain.scene import rooms as RM
from brain.scene import run_s1c as S

SEED = S.GATE_SEED


def per_word(L, ws):
    """The per-word terms of the window loss (mean over the window's scenes), the loss's own arithmetic."""
    p = PK.hyp_probs(L, ws.X, ws.vocab)
    tot = np.zeros(len(ws.vocab))
    for i in range(ws.n):
        a, b = int(ws.starts[i]), int(ws.starts[i + 1])
        P = 1.0 - np.prod(1.0 - p[a:b], axis=0) if b > a else np.zeros(len(ws.vocab))
        P = np.clip(P, PK.P_CLIP, 1.0 - PK.P_CLIP)
        y = ws.Y[i]
        tot += -(y * np.log(P) + (1.0 - y) * np.log(1.0 - P))
    return {w: float(v) for w, v in zip(ws.vocab, tot / ws.n)}


def main() -> None:
    data = S.RoomData(S.ROOT, SEED, RM.ROOMS)
    test = S.FixedTestSet()
    run = S.life(data, test, "RANDOM", RM.ROOMS, n_blocks=S.GATE2_BLOCKS)
    cl = S.room_claims(run)
    g = json.loads((S.ROOT / "gate" / "first_gate.json").read_text())["step2"]
    same = all(cl[k] == g[k] for k in ("N", "R", "K", "U"))
    print(f"the control: the re-run reproduces the gate's step-2 claims exactly: {same}")
    rec, table = run["record"], run["table"]
    print("per block: the room · L_K before → after (ΔL_K) · L_U after · the learnable rooms' mean L after:")
    for x in rec:
        b = x["block"]
        print(f"   b{b:>2} {x['room']:<2} L_K {table[b - 1]['K']:6.3f} → {table[b]['K']:6.3f} ({table[b]['K'] - table[b - 1]['K']:+6.3f})"
              f" · L_U {table[b]['U']:6.3f} · R̄ {np.mean([table[b][r] for r in ('R1', 'R2', 'R3')]):6.3f}")
    kb = [x["block"] for x in rec if x["room"] == "K"]
    print(f"K's visits: blocks {kb}; its own drops {[round(x['drop'], 3) for x in rec if x['room'] == 'K']}")
    rises = []
    for a, b in zip(kb, kb[1:] + [S.GATE2_BLOCKS + 1]):
        end = min(b - 1, S.GATE2_BLOCKS)
        rises.append((a, end, round(table[end]["K"] - table[a]["K"], 3)))
    print(f"L_K's rise over the other rooms' blocks between K's visits (from after K's block to before the next): {rises}")
    col = {r: [table[x['block']]['K'] - table[x['block'] - 1]['K'] for x in rec if x['room'] == r] for r in RM.ROOMS}
    print("the K column of the interference — the mean ΔL_K per block in each room (n): "
          + " · ".join(f"{r} {np.mean(v):+.3f} ({len(v)})" for r, v in col.items() if v))
    lvl = {"the gate's (mean over boundaries 21–60)": cl["K"]["level"], "L_K at 60": table[60]["K"],
           "the largest L_K in 21–60": max(table[b]["K"] for b in range(21, 61))}
    print("(i) under three readings of «L_K's level»: " + " · ".join(
        f"{k} {v:.3f} → bound {0.05 * v:.3f}" for k, v in lvl.items()) + f" — K's mean own drop {cl['K']['mean_drop']:.3f}")
    # replay from the record to read the per-word terms
    L = S.new_learner()
    marks = {kb[-1], kb[-1] - 1, S.GATE2_BLOCKS}
    for x in rec:
        S.train_block(L, data, x["room"], x["start"], SEED)
        if x["block"] in marks:
            pk = per_word(L, data.window["K"])
            pu = per_word(L, data.window["U"])
            pr = {w: np.mean([per_word(L, data.window[r])[w] for r in ("R1", "R2", "R3")]) for w in S.VOCAB}
            chk = abs(sum(pk.values()) - table[x["block"]]["K"])
            print(f"after block {x['block']} ({x['room']}): L_K {sum(pk.values()):.3f} (the table {table[x['block']]['K']:.3f}, |Δ| {chk:.1e})")
            print("   L_K per word (K's window says «red star»): " + " ".join(f"{w} {v:.2f}" for w, v in sorted(pk.items(), key=lambda z: -z[1])))
            print("   L_U per word: " + " ".join(f"{w} {v:.2f}" for w, v in sorted(pu.items(), key=lambda z: -z[1])))
            print("   the learnable rooms' mean per word: " + " ".join(f"{w} {v:.2f}" for w, v in sorted(pr.items(), key=lambda z: -z[1])))


if __name__ == "__main__":
    main()
