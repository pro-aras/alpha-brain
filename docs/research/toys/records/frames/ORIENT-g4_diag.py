"""Diagnosis of the G4 failure: WEB-S's state at the end of the signed small synthetic stream, per seed (read-only)."""
import numpy as np
from genome import web as Wb
from tools.toys.frames import compress as CO, scene as SC, streams as ST

ms = SC.sample_moments(3000, np.random.default_rng([SC.SEED_ROOT, SC.G6_TAG, 1]))
planted = ST.with_plant(ms, 10)
tr, he = ST.split(planted)
sc = CO.Scorer([m.words for m in tr], [m.words for m in he])
flat = ST.flat_words(tr)
key = tuple(sorted(ST.PLANT))
print("train words", len(flat), "V", sc.V, "budget 2V =", 2 * sc.V, "possible pairs of V words:", sc.V * (sc.V - 1) // 2)
for s in range(1, 11):
    w = Wb.Web("S", budget=2 * sc.V, seed=s)
    first_plant_seen = None
    for i, x in enumerate(flat):
        w.hear(x)
        if first_plant_seen is None and key in w.edges:
            first_plant_seen = i
    e = w.edges.get(key)
    cons = [k for k, v in w.edges.items() if v["state"] == "consolidated"]
    print(f"seed {s:2d}: plant edge {'MADE at word %d' % first_plant_seen if e else 'NEVER MADE'}; state {e['state'] if e else None} c {e['c'] if e else None}; "
          f"edges live {len(w.edges)}, consolidated {len(cons)}; refused {w.stats['refused']}, replaced {w.stats['replaced']}, realised {w.stats['realised']}, offered {w.stats['offered']}")
