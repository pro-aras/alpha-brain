"""Throwaway price probe (scratch, never committed): time and peak memory of the heavy operations on the REAL copies. Run through slot under a cap."""
import sys
import time
import resource
from pathlib import Path

import numpy as np

from tools.toys.frames import streams as ST, compress as CO, rules as RL

COP = ST.COPIES


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


t0 = time.time()
ms = ST.load_moments(sorted((COP / "alpha4-1" / "tape").glob("*.jsonl")))
print(f"load_moments {len(ms)} moments {time.time() - t0:.1f}s rss {rss_mb():.0f} MB", flush=True)
tr, he = ST.split(ms)
sc_t = time.time()
sc = CO.Scorer([m.words for m in tr], [m.words for m in he])
print(f"Scorer built V={sc.V} train {len(tr)} held {len(he)} held_words {sc.n_held_words} {time.time() - sc_t:.1f}s rss {rss_mb():.0f} MB", flush=True)

# gain() timing on random frame sets of 10 and 100 pairs drawn from the train bigrams
rng = np.random.default_rng(1)
bg = sorted(sc.train_bigrams())
for k in (10, 100):
    ts = []
    for _ in range(5):
        F = {bg[int(i)] for i in rng.integers(0, len(bg), size=k)}
        t1 = time.time()
        g = sc.gain(F)
        ts.append(time.time() - t1)
    print(f"gain() on {k} frames: mean {np.mean(ts):.3f}s  (last G {g.G:.1f})", flush=True)

# MDL
t1 = time.time()
r = RL.mdl_greedy(sc)
print(f"MDL-GREEDY: {r.info['steps']} steps, {r.info['candidates']} candidates, {time.time() - t1:.1f}s rss {rss_mb():.0f} MB; G(F) {sc.gain(r.frames).G:.1f}", flush=True)

# SENTENCE
t1 = time.time()
r = RL.sentence_rule([m.words for m in tr])
print(f"SENTENCE: {len(r.frames)} frames, N {r.info['N']}, {time.time() - t1:.1f}s rss {rss_mb():.0f} MB; G(F) {sc.gain(r.frames).G:.1f}", flush=True)

# WEB H and one S
flat = ST.flat_words(tr)
print(f"flat train words {len(flat)}", flush=True)
for rule, seed in (("H", 0), ("S", 1)):
    t1 = time.time()
    r = RL.web_rule(flat, sc, rule, seed)
    print(f"WEB-{rule}: consolidated {r.info['consolidated']} kept {len(r.frames)} dropped {r.info['dropped_no_adjacent']} peak_edges {r.info['peak_edges']} {time.time() - t1:.1f}s rss {rss_mb():.0f} MB; G(F) {sc.gain(r.frames).G:.1f}", flush=True)
print(f"final peak rss {rss_mb():.0f} MB", flush=True)
