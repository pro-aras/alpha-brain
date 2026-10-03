"""g5_cost_count.py — how many rng draws does one NULL-2 pick consume on WEB-H's real set, and does a vectorised integers() equal k scalar calls?  (counts only; no value printed)

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 22:30 +0400 — new, scratch (untracked).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.toys.frames import compress as CO
from tools.toys.frames import null as NL
from tools.toys.frames import plants as PL
from tools.toys.frames import rules as RL
from tools.toys.frames import run as RN
from tools.toys.frames import streams as ST

# 1. the stream identity (numpy version dependent; the test a speed-up would have to pass)
for total in (5, 100, 7919, 123456):
    a = np.random.default_rng([1, 2, 3]); b = np.random.default_rng([1, 2, 3])
    scalar = [int(a.integers(total)) for _ in range(1000)]
    vec = [int(x) for x in b.integers(total, size=1000)]
    print(f"total {total}: vectorised == 1000 scalar calls: {scalar == vec}; state after equal: {a.bit_generator.state == b.bit_generator.state}")

# 2. the picks of WEB-H's NULL-2 draw: draws consumed per pick
a4 = RN.load_streams(Path(sys.argv[1]))["alpha4"]
train, held = PL.condition_parts(a4, "plain")
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
bb = NL.bigram_bins(sc)
print("bigram bins (bin: n entries):", {k: len(v) for k, v in sorted(bb.items())})
for label, r in (("WEB-H", RL.web_rule(ST.flat_words(train), sc, "H", 0)), ("WEB-S s1", RL.web_rule(ST.flat_words(train), sc, "S", 1)), ("SENTENCE", RL.sentence_rule(sc.train))):
    frames = sorted(set(r.frames))
    own = [NL.log2_bin(max(1, sc.train_adjacent(f))) for f in frames]
    lo, hi = min(bb), max(bb)

    class Counting:
        def __init__(self, g): self.g = g; self.n = 0
        def integers(self, *a, **k): self.n += 1; return self.g.integers(*a, **k)
    rng = Counting(np.random.default_rng([NL.SEED_ROOT, RL.RULE_TAG[r.rule], 0 if r.rule != "WEB-S" else r.seed, 2]))
    excluded = set(frames)
    per_pick = []
    fell = 0
    for b0 in own:
        n0 = rng.n
        p, f = NL._pick_bigram(rng, bb, b0, excluded, lo, hi)
        excluded.add(p)
        per_pick.append(rng.n - n0)
        fell += int(f)
    full = sum(1 for x in per_pick if x >= NL.MAX_REJECT)
    print(f"{label}: |F| {len(frames)}; own-bin histogram {dict(sorted({b: own.count(b) for b in set(own)}.items()))}")
    print(f"   rng draws per pick: mean {sum(per_pick)/len(per_pick):.0f}, max {max(per_pick)}; picks that exhausted MAX_REJECT ({NL.MAX_REJECT}) at least once: {full} of {len(per_pick)}; fallback picks {fell}")
