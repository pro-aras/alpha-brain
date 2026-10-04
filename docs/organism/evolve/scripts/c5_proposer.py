#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:58 +0400 — PREREG-EVOLVE-CAL C5 (the proposer never emits the incumbent's own value).
"""usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/c5_proposer.py --out c5.json
C5: over (SEED 20261101, epochs 1-3, proposal_no 1-50) = 150 draws, with the per-epoch incumbent text (epoch 1: brain-long-2's life genome; epochs 2 and 3: after #5's
adoption, KWTA 4 — epoch 3's incumbent is hypothetical, no second adoption happened), the REDRAWN proposer (tools.evolve.mutate_distinct) emits the incumbent's own value
0 of 150 times; the RAW proposer (creature.genes.draw_mutation) is counted beside it as the positive control (it must collide at least once: (20261101, 1, 3) is
BIRTH.misfires 3). Both counts are printed with the number of draws the redrawn proposer took when it had to."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from creature import genes                       # noqa: E402
from tools import evolve as ev                   # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
V0 = (ROOT / "genome" / "brain" / "lives" / "BRAIN-LONG-2.genome").read_text()
V1 = genes.apply_mutation(V0, "KWTA.k", 4)


def collides(text, key, value):
    return float(ev._printed_value(key, value)) == float(ev.gene_text(text, key))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = redrawn = 0
    redraws = []
    rows = []
    for epoch, base in ((1, V0), (2, V1), (3, V1)):
        for no in range(1, 51):
            k0, v0 = genes.draw_mutation(20261101, epoch, no)
            r = collides(base, k0, v0)
            text, key, value, draws = ev.mutate_distinct(base, 20261101, epoch, no)
            c = collides(base, key, value)
            raw += int(r)
            redrawn += int(c)
            if draws > 1:
                redraws.append({"epoch": epoch, "proposal_no": no, "raw": [k0, v0], "taken": [key, value], "draws": draws})
            rows.append((epoch, no))
    out = {"draws": len(rows), "raw_collisions": raw, "redrawn_collisions": redrawn, "redraws": redraws, "c5": bool(redrawn == 0 and raw >= 1)}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"draws {len(rows)} · RAW proposer collides with the incumbent's own value {raw} times · REDRAWN proposer {redrawn} times (C5 needs 0 and the raw count >= 1: "
          f"{'PASS' if out['c5'] else 'FAIL'}) · redraws taken: {[(x['epoch'], x['proposal_no'], x['raw'], '->', x['taken'], x['draws']) for x in redraws]}")
    return 0 if out["c5"] else 1


if __name__ == "__main__":
    sys.exit(main())
