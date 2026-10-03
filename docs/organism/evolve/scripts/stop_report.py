#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:02 +0400 — PREREG-EVOLVE-CAL A1 (iii) + A2.1: the STOP test's reader.
"""docs/organism/evolve/scripts/stop_report.py — the STOP test's report (PREREG-EVOLVE-CAL A1 (iii), A2.1) with the controls that make it readable.

usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/stop_report.py --dir <stop records dir> --recorded <recorded round-N incumbent journal dir> --out report.json

Reads the twin directories T0 (incumbent), T0b (the incumbent AGAIN: the determinism control), Ts (SEED + 1), Te (DELTA lr x (1 + 1e-5)) of ONE
short slice, and the journal the production worker recorded for the same incumbent on the same slice (the replication control). Every
reading carries its presence count (rows read); the plant (one discrete field of one row of T0's own journal changed in memory) must be CAUGHT
by the same comparison, and asserts it changed the bytes.

The law's two pairs (A1 (iii)): the SEED pair — predicted organism EQUAL, think rows DIFFERENT — and the epsilon pair — predicted organism
DIFFERENT. Read here beside: (a) T0 vs T0b (a twin run twice must be bit-identical, else the epsilon pair's «DIFFERENT» could be a
non-deterministic replay), (b) T0 vs the recorded incumbent (the twin pipeline reproduces the production round). «Organism» is read at the
dense state_hash (the snapshot's own digest) AND as the journal's discrete outcomes (a continuous perturbation must flip a discrete outcome
before a count-valued reading can move).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import evolve_cal as cal      # noqa: E402


def load(d: Path):
    r = json.loads((d / "reading.json").read_text())
    return r, cal.read_twin_journal(d)


def recorded_rows(d: Path):
    rows = []
    for f in sorted(Path(d).glob("*.jsonl")):
        rows += [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    return rows


def pair(name, a, b):
    (ra, ja), (rb, jb) = a, b
    c = cal.compare_twins(ja, jb)
    return {"pair": name, "state_hash_equal": ra["state_hash"] == rb["state_hash"], "row_hash_equal": ra["row_hash"] == rb["row_hash"],
            "q1_seen": [ra["q1_seen"], rb["q1_seen"]], "frames_filed": [ra["frames_filed"], rb["frames_filed"]],
            "confirmed_share": [ra["confirmed_share"], rb["confirmed_share"]], "cpu_s": [ra["cpu_s"], rb["cpu_s"]],
            "journal": c}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--recorded", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    d = Path(a.dir)
    have = {n: (d / n / "reading.json").exists() for n in ("T0", "T0b", "Ts", "Te")}
    print("twins present:", have)
    t = {n: load(d / n) for n, ok in have.items() if ok}
    rep = recorded_rows(Path(a.recorded))
    out = {"twins_present": have, "recorded_rows": len(rep)}
    if "T0" in t:
        n0 = len(t["T0"][1])
        out["replication_vs_recorded"] = {**cal.compare_twins(t["T0"][1], rep[:n0]), "compared_rows": n0,
                                          "first_row_seq_mine_recorded": [t["T0"][1][0].get("seq"), rep[0].get("seq")]}
        # the plant: a discrete field of one row of T0's own journal changed in memory
        rows = json.loads(json.dumps(t["T0"][1]))
        i = next(k for k, x in enumerate(rows) if isinstance(x.get("cells"), list))
        before = json.dumps(rows[i], sort_keys=True)
        rows[i]["cells"] = [rows[i]["cells"][0] + 1, rows[i]["cells"][1]]
        assert json.dumps(rows[i], sort_keys=True) != before, "the plant changed nothing"
        pc = cal.compare_twins(t["T0"][1], rows)
        out["plant"] = {"row": i, "caught": (not pc["identical"]) and pc["first_diff"] == i and pc["discrete_diff_rows"] == 1}
    for name, (x, y) in (("determinism T0 vs T0b", ("T0", "T0b")), ("seed pair T0 vs Ts (SEED+1)", ("T0", "Ts")),
                         ("epsilon pair T0 vs Te (lr x (1+1e-5))", ("T0", "Te"))):
        if x in t and y in t:
            out[name] = pair(name, t[x], t[y])
    for n, (r, j) in t.items():
        out.setdefault("readings", {})[n] = {k: r.get(k) for k in ("variant", "q1_seen", "confirmed_share", "frames_filed", "journal_rows", "rows_consumed",
                                                                    "state_hash", "row_hash", "cpu_s", "wall_s", "build_s", "maxrss_kb", "load0", "load1", "psi0", "psi1")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
