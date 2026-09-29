# the seat, 2026-09-29: LOOK AGAIN — a first reading on TRAINING scenes only (no test scene, no mind, no brain, nothing learned)
# Question: the eye takes 4 fixations a canvas. How often does it miss the NAMED thing, and how many of those misses would
# 1, 2 or 4 MORE fixations of the SAME organ reach? Read-only: scenes are rendered by the world's own code, fixations come
# from genome.gaze.fixations (the pinned organ), a fixation's thing from brain.scene.world.fixation_thing.
import collections, json, sys, time
import numpy as np
from brain.scene import world as W
from genome import gaze
WS = int(sys.argv[1]); N = int(sys.argv[2]); OUT = sys.argv[3]
FS = (4, 5, 6, 8)
t0 = time.process_time()
prefix_ok = collections.Counter(); rows = []
for i in range(N):
    sc = W.train_scene(WS, i)
    rgb = W.render_scene(sc)[0]
    things = sc.things
    ref = int(sc.referent)
    fx = {F: gaze.fixations(rgb, F, "surprise", f"probe{WS}-{i}") for F in FS}
    for F in FS[1:]:
        prefix_ok[F] += fx[F][:4] == fx[4]
    rec = {"i": i, "n_things": len(things), "n_fix": {F: len(fx[F]) for F in FS}}
    for F in FS:
        on = [W.fixation_thing(c, things) for c in fx[F]]
        rec[f"ref_seen@{F}"] = ref in on
        rec[f"things_seen@{F}"] = len({t for t in on if t is not None})
        rec[f"off_things@{F}"] = sum(1 for t in on if t is None)
    rows.append(rec)
def rate(xs):
    xs = list(xs); return (sum(xs) / len(xs)) if xs else None
out = {"world_seed": WS, "scenes": N, "prefix_of_4_kept": {str(F): prefix_ok[F] for F in FS[1:]}, "by_F": {}, "by_n_things": {}}
for F in FS:
    out["by_F"][str(F)] = {"fixations_taken_mean": float(np.mean([r["n_fix"][F] for r in rows])),
                           "referent_seen": rate(r[f"ref_seen@{F}"] for r in rows),
                           "every_thing_seen": rate(r[f"things_seen@{F}"] == r["n_things"] for r in rows),
                           "things_seen_share": sum(r[f"things_seen@{F}"] for r in rows) / sum(r["n_things"] for r in rows),
                           "fixations_on_no_thing_mean": float(np.mean([r[f"off_things@{F}"] for r in rows]))}
for n in (1, 2, 3):
    sel = [r for r in rows if r["n_things"] == n]
    out["by_n_things"][str(n)] = {"scenes": len(sel), **{f"referent_seen@{F}": rate(r[f"ref_seen@{F}"] for r in sel) for F in FS},
                                  **{f"every_thing_seen@{F}": rate(r[f"things_seen@{F}"] == n for r in sel) for F in FS}}
missed = [r for r in rows if not r["ref_seen@4"]]
out["of_the_scenes_whose_referent_4_fixations_missed"] = {"n": len(missed), **{f"reached@{F}": rate(r[f"ref_seen@{F}"] for r in missed) for F in FS[1:]}}
out["cpu_s"] = time.process_time() - t0
json.dump(out, open(OUT, "w"), indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
