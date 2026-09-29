# the seat, 2026-09-29: LOOK AGAIN, a TARGETED rule — a reading on TRAINING scenes only (nothing learned, no mind, no brain)
# The rule R-BLOB, built from what the EYE itself holds (the canvas's ink on its own 16x16 grid and its own fixations):
#   ink cell   = a grid cell whose 8x8 pixels hold ink above INK_T of the canvas's ink (the eye's own rule, gaze.ink_border);
#   blob       = a connected set of ink cells (8-neighbours);
#   seen blob  = a blob holding a fixated cell, or touching one (a fixation's 32 px window covers its neighbours);
#   look again = one more fixation at the cell of the LARGEST unseen blob nearest that blob's centroid; repeat up to K times.
# No truth is read by the rule. The truth is read by the bench only, to count what the rule reached.
import collections, json, sys, time
import numpy as np
from scipy import ndimage
from brain.scene import world as W
from genome import gaze
WS = int(sys.argv[1]); N = int(sys.argv[2]); OUT = sys.argv[3]
GRID, CELL = 16, 8
INK_TS = (0.10, 0.25)
MIN_CELLS = (1, 3, 4, 6)
K_MAX = 3
def blobs(rgb, ink_t):
    ink = gaze.ink_border(gaze.luminance(rgb))
    cells = (ink.reshape(GRID, CELL, GRID, CELL).max(axis=(1, 3)) > ink_t)
    lab, n = ndimage.label(cells, structure=np.ones((3, 3), dtype=int))
    return lab, n
def look_again(lab, n, fix, k_max, min_cells=1):
    fix = list(fix); added = []
    for _ in range(k_max):
        seen = set()
        for (y, x) in fix:
            ys, xs = slice(max(0, y - 1), min(GRID, y + 2)), slice(max(0, x - 1), min(GRID, x + 2))
            seen.update(int(v) for v in np.unique(lab[ys, xs]) if v > 0)
        cand = [(int((lab == b).sum()), -b) for b in range(1, n + 1) if b not in seen and int((lab == b).sum()) >= min_cells]
        if not cand:
            break
        size, nb = max(cand); b = -nb
        ys, xs = np.nonzero(lab == b)
        cy, cx = ys.mean(), xs.mean()
        j = int(np.argmin((ys - cy) ** 2 + (xs - cx) ** 2))
        c = (int(ys[j]), int(xs[j]))
        fix.append(c); added.append(c)
    return added
t0 = time.process_time()
res = {f"{t}:min{m}": [] for t in INK_TS for m in MIN_CELLS}
for i in range(N):
    sc = W.train_scene(WS, i)
    rgb = W.render_scene(sc)[0]
    things, ref = sc.things, int(sc.referent)
    f4 = gaze.fixations(rgb, 4, "surprise", f"probe{WS}-{i}")
    on4 = [W.fixation_thing(c, things) for c in f4]
    for t, mc in [(t, m) for t in INK_TS for m in MIN_CELLS]:
        lab, n = blobs(rgb, t)
        added = look_again(lab, n, f4, K_MAX, mc)
        on_new = [W.fixation_thing(c, things) for c in added]
        rec = {"n_things": len(things), "blobs": int(n), "ref_seen@4": ref in on4, "all_seen@4": len({x for x in on4 if x is not None}) == len(things),
               "looks": len(added), "new_on_no_thing": sum(1 for x in on_new if x is None),
               "new_on_a_seen_thing": sum(1 for x in on_new if x is not None and x in on4)}
        for k in (1, 2, 3):
            on = on4 + on_new[:k]
            rec[f"ref_seen+{k}"] = ref in on
            rec[f"all_seen+{k}"] = len({x for x in on if x is not None}) == len(things)
        res[f"{t}:min{mc}"].append(rec)
def rate(xs):
    xs = list(xs); return (sum(xs) / len(xs)) if xs else None
out = {"world_seed": WS, "scenes": N, "K_max": K_MAX, "by_ink_t": {}}
for t, rows in res.items():
    missed = [r for r in rows if not r["ref_seen@4"]]
    complete = [r for r in rows if r["all_seen@4"]]
    out["by_ink_t"][t] = {
        "blobs_mean": float(np.mean([r["blobs"] for r in rows])), "things_mean": float(np.mean([r["n_things"] for r in rows])),
        "referent_seen": {"at_4": rate(r["ref_seen@4"] for r in rows), **{f"+{k}": rate(r[f"ref_seen+{k}"] for r in rows) for k in (1, 2, 3)}},
        "every_thing_seen": {"at_4": rate(r["all_seen@4"] for r in rows), **{f"+{k}": rate(r[f"all_seen+{k}"] for r in rows) for k in (1, 2, 3)}},
        "of_the_misses_at_4": {"n": len(missed), **{f"reached+{k}": rate(r[f"ref_seen+{k}"] for r in missed) for k in (1, 2, 3)}},
        "looks_taken_mean": float(np.mean([r["looks"] for r in rows])),
        "looks_taken_when_every_thing_was_already_seen": {"scenes": len(complete), "mean": float(np.mean([r["looks"] for r in complete])) if complete else None},
        "new_fixations_on_no_thing": sum(r["new_on_no_thing"] for r in rows), "new_fixations_on_a_thing_already_seen": sum(r["new_on_a_seen_thing"] for r in rows),
        "new_fixations": sum(r["looks"] for r in rows)}
out["cpu_s"] = time.process_time() - t0
json.dump(out, open(OUT, "w"), indent=1, sort_keys=True)
