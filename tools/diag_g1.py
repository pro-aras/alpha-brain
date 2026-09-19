"""diag_g1.py — read the per-item misses of a G1-toy run BEFORE blaming anything (SOLUTIONS #225's rule).
edit: Claude (Fable 5.1), 2026-09-19 17:30 +0400. Diagnostic only: no bar moves; the organism is loaded, never changed."""
import json, os, sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from genome import world, gaze
from genome.machinery import parse_genome, Organism
from genome.run_g1 import toy_streams, glance_held, feats_only, PLANT_SHOWINGS
run = Path(sys.argv[1])
g = parse_genome((run / "G1.genome").read_text()); org = Organism.load(run / "organism", g)
L = json.loads((run / "ledger.json").read_text()); Lw = {int(k): set(v) for k, v in L["words"].items()}; Ls = {int(k): set(v) for k, v in L["sight"].items()}
R = json.load(open(run / "results.json"))
things, arr2, dev, held, a2, plant, shuf, _n = toy_streams(g, int(R["gate"].get("plant", {}).get("showings", PLANT_SHOWINGS)))
H = glance_held(held, g, "surprise")
conf = defaultdict(Counter); abst = defaultdict(Counter)
for t in things + arr2 + [world.THING_NEVER, world.THING_NULL, world.THING_PLANT]:
    for _t, feats, fix, truth, pid in H[t]:
        r = org.recall_many("sight", feats)
        if r["cell"] is None: abst[t][r["reason"]] += 1
        else: conf[t]["/".join(sorted(Lw.get(r["cell"], set())))] += 1
print("Q1 confusion at the final state (row = shown thing → answered as / abstain):")
for t in things + arr2 + [world.THING_NEVER, world.THING_NULL, world.THING_PLANT]:
    wrong = {k: v for k, v in conf[t].items() if k != t}
    print(f"  {t:8s} right {conf[t].get(t, 0):2d}  wrong {dict(wrong) if wrong else '-'}  abstain {dict(abst[t]) if abst[t] else '-'}")
# sight cells per thing and multi-thing cells; which things share cells
share = Counter(frozenset(s) for s in Ls.values() if len(s) > 1)
print("multi-thing sight cells:", dict(share) if share else "none")
# the null plant «vex»: the cosine of its glances to the nearest cell, and that cell's thing
print("null plant «vex» glances → nearest cell's thing (cos):")
for _t, feats, fix, truth, pid in H[world.THING_NULL][:5]:
    row = []
    for x in feats:
        c = org.sight.cos(x); j = int(np.argmax(c)); row.append((sorted(Ls.get(j, set())), round(float(c[j]), 3)))
    print("  ", row)
# retention: Q1 per thing at dev vs after arrival 2 (from results)
d = R["design"]; pd = d["ask_dev"]["Q1"]["per_thing"]; pa = d["ask_arr2"]["Q1"]["per_thing"]
print("Q1 per thing dev → after arrival 2:", {t: (round(pd[t], 2), round(pa[t], 2)) for t in things if abs(pd[t] - pa[t]) >= 0.05})
print("Q1 abstain reasons after arrival 2:", d["ask_arr2"]["Q1"]["abstain"], "at dev:", d["ask_dev"]["Q1"]["abstain"], "final:", d["ask_final"]["Q1"]["abstain"])
print("edges alive", d["at_final"]["edges_alive"], "born", d["at_final"]["edges_born"], "pruned", d["at_final"]["edges_pruned"])
