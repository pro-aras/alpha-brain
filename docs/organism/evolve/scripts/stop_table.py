#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:41 +0400 — the STOP stage's table for the law's AMENDMENT 3, generated from the twins' own files (no figure typed).
"""usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/stop_table.py --dir <stop records dir> > table.md
Prints one markdown row per twin against T0: variant, whether the dense state_hash equals T0's, the keyed moment rows (matched / differing in any key / differing in a
DISCRETE key), the first seq of a discrete difference, the other kinds' differing rows, q1_seen in items, frames_filed, confirmed_share, CPU-seconds, wall, RSS."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import evolve_cal as cal      # noqa: E402

ORDER = ("T0", "T0b", "Ts", "Te", "P1e-4", "P1e-3", "P1e-2")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    d = Path(a.dir)
    base_r = json.loads((d / "T0" / "reading.json").read_text())
    base_j = cal.read_twin_journal(d / "T0")
    print("| twin | variant | dense state_hash vs T0 | moment rows matched / differing / DISCRETE | first discrete seq | other kinds differing (rows) | q1_seen (of 110) | frames_filed | confirmed_share | CPU s | wall s | RSS GB |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n in ORDER:
        if not (d / n / "reading.json").exists():
            continue
        r = json.loads((d / n / "reading.json").read_text())
        j = cal.read_twin_journal(d / n)
        k = cal.compare_twins_keyed(base_j, j)
        m = k["moment"]
        other = {kind: v["differing"] + v["only_a"] + v["only_b"] for kind, v in k["other"].items() if v["differing"] or v["only_a"] or v["only_b"]}
        eq = "EQUAL" if r["state_hash"] == base_r["state_hash"] else "differs"
        q1 = round(r["q1_seen"] * 110) if r["q1_seen"] is not None else None
        print(f"| {n} | {r['variant']} | {eq if n != 'T0' else '—'} | {m['matched']} / {m['differing']} / {m['discrete_differing']} | {m['first_discrete_seq']} | {other or 'none'} | {q1} | {r['frames_filed']} | {r['confirmed_share']} | {r['cpu_s']} | {r['wall_s']} | {r['maxrss_kb'] / 1048576:.2f} |")


if __name__ == "__main__":
    main()
