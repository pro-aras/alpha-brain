"""credit_split.py — counts only, post-hoc: of each rule's positive per-frame marginal credits (scratch/perframe-credit.json), how much belongs to frames with ZERO held-out adjacent occurrences (credit that cannot come from a held-out firing).

# edit: Claude (Sonnet 5.5, swarm toys), written at the RESULT, 2026-10-04 00:24 +0400 (post-hoc reading, no mark).
usage: PYTHONPATH=. python3 credit_split.py <copies> <perframe-credit.json>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.toys.frames import compress as CO
from tools.toys.frames import plants as PL
from tools.toys.frames import run as RN

a4 = RN.load_streams(Path(sys.argv[1]))["alpha4"]
train, held = PL.condition_parts(a4, "plain")
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
r = json.load(open(sys.argv[2]))
for rule, v in r["rules"].items():
    # `top` holds the 25 best; the positive frames beyond them are not stored, so recompute from the record's frames is not possible here: split the stored top 25 and say so
    top = v["top"]
    pos = [(c, tuple(f)) for c, f in top if c > 0]
    z = [(c, f) for c, f in pos if sc.held_adjacent(f) == 0]
    nz = [(c, f) for c, f in pos if sc.held_adjacent(f) > 0]
    print(f"{rule}: of its {v['n_positive']} paying frames the stored top {len(top)} hold {len(pos)} positive: {len(z)} with ZERO held-out adjacent occurrences (credit sum {sum(c for c, _ in z):.1f}), {len(nz)} with at least one (credit sum {sum(c for c, _ in nz):.1f})")
    print("   zero-held:", [" ".join(f) for _c, f in z][:14])
    print("   with held firings:", [(" ".join(f), sc.held_adjacent(f)) for _c, f in nz][:14])
