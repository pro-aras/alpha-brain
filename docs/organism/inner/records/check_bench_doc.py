#!/usr/bin/env python3
# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 12:2x +0400 — BENCH-INNER-1's own check (SOLUTIONS #242: every number in a doc is read
# from its file by script before it is committed): the figures of docs/organism/inner/BENCH-INNER-1-2026-10-03.md against the record's
# GRADE.json / RUN.json; --equal compares two bench dirs section by section (the bench is deterministic). Exit 0 = every figure found; 1 = a figure
# is not in its file (named); 2 = usage. A planted wrong figure (--plant) must exit 1.
"""usage: check_bench_doc.py --doc <md> --rec <records dir with GRADE.json + RUN.json> [--plant] | --equal <dir a> <dir b>"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = ("K", "G1", "G2", "G3", "R_RET", "R_AGE", "R_ASSOC", "R_SELF", "truth_cross_check")


def figures(G: dict, R: dict) -> dict:
    K, G1, G2, G3, cc, rr, ra, rs = G["K"], G["G1"], G["G2"], G["G3"], G["truth_cross_check"], G["R_RET"], G["R_ASSOC"], G["R_SELF"]
    f = {
        "G1 turns": f"{G1['turns']:,} of {G1['n']:,}", "G1 skipped": "{backlog: 1, no backlog reading: 1}" if G1["skipped"] == {"backlog": 1, "no backlog reading": 1} else "?",
        "G2 exist": f"{G2['exist']:.3f}", "G2 ok": f"{G2['ok']:,} / {G2['n']:,}", "G2 moments": f"{G2['presence_moments']:,}", "G2 plant": "CAUGHT" if G2["plant"]["caught"] else "MISSED",
        "G3 covered": f"{G3['covered']} of {G3['mature']}", "G3 share": f"{G3['largest_share']:.3f}", "G3 sources": f"self {G3['sources'].get('self')} / web {G3['sources'].get('web')}",
        "G3 plant distinct": str(G3["plant"]["distinct"]), "G3 plant period": str(G3["plant"]["period"]), "G3 plant caught": "CAUGHT" if G3["plant"]["caught"] else "MISSED",
        "G3 read covered": f"{G3['read_plant']['covered']} of {G3['read_plant']['mature']}", "G3 read share": f"{G3['read_plant']['largest_share']:.3f}",
        "K observed": f"{K['observed']:,} of {K['n']:,}", "K rate": f"{K['rate']:.3f}", "K said": f"{K['n_said']}", "K p95": f"{K['null_p95']:.0f}", "K mean": f"{K['null_mean']:.0f}", "K max": str(K["null_max"]),
        "K draws": str(K["null_draws"]), "K pass": "PASS" if K["pass"] else "FAIL",
        "K-abl phrase": K["ablated"]["phrase"][0], "K-abl observed": str(K["ablated"]["observed"]), "K-abl failed": "FAILS" if K["ablated"]["failed_as_it_must"] else "PASSES",
        "K-plant": "CAUGHT" if K["plant"]["caught"] else "MISSED",
        "cc checked": f"{cc['checked']:,} checked, {cc['mismatch']} mismatch", "cc plant": "CAUGHT" if cc["plant_caught"] else "MISSED",
        "RET n": f"{rr['n']:,}", "RET inner": f"{rr['inner_rate']:.3f}", "RET live": f"{rr['live_rate']:.3f}", "RET both": str(rr["both"]), "RET inner-only": str(rr["inner_only"]),
        "RET live-only": str(rr["live_only"]), "RET neither": str(rr["neither"]), "RET gap": f"{rr['smallest_passing_gap']:.3f}", "RET p": f"{rr['sign_test_p_inner_better']:.4f}",
        "RET live turns": f"{rr['presence_live_turns']:,}",
        "AGE deciles": " · ".join(f"{d['rate']:.3f}" for d in G["R_AGE"]),
        "ASSOC hops": str(ra["n"]), "ASSOC share": f"{ra['share']:.3f}", "ASSOC p95": f"{ra['null_p95']:.4f}", "ASSOC mean": f"{ra['null_mean']:.4f}",
        "SELF rho": f"{rs['rho']:.3f}", "SELF p": f"{rs['p_label_permutation']:.3f}", "SELF p95": f"{rs['null_p95']:.3f}", "SELF draws": f"{rs['null_draws']:,}", "SELF words": str(rs["n_words"]),
        "cost ms": f"{R['cpu_ms_per_row']:.1f}", "cost load": f"{R['cpu_s_load']:.1f}", "B1 delta": f"+{R['B1_observed_delta']:,} on {R['body_rows_with_reading']:,}",
        "gen last_seq": f"{R['gen_last_seq']:,}", "inner rows": f"{R['inner_rows']:,}",
    }
    return f


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="check_bench_doc")
    ap.add_argument("--doc")
    ap.add_argument("--rec")
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--equal", nargs=2)
    a = ap.parse_args(argv)
    if a.equal:
        A, B = (json.loads((Path(d) / "GRADE.json").read_text()) for d in a.equal)
        diff = [k for k in SECTIONS if json.dumps(A.get(k), sort_keys=True, default=str) != json.dumps(B.get(k), sort_keys=True, default=str)]
        print(f"sections compared {len(SECTIONS)} · differing {len(diff)} {diff}")
        return 0 if not diff else 1
    if not (a.doc and a.rec):
        print(__doc__)
        return 2
    G = json.loads((Path(a.rec) / "GRADE.json").read_text())
    R = json.loads((Path(a.rec) / "RUN.json").read_text())
    text = Path(a.doc).read_text(encoding="utf-8")
    f = figures(G, R)
    if a.plant:
        f["K observed"] = f"{G['K']['observed'] + 1:,} of {G['K']['n']:,}"      # a wrong figure the check must refuse
    missing = [k for k, v in f.items() if v not in text]
    for k in sorted(f):
        print(f"{'ok ' if k not in missing else 'MISSING'} {k}: {f[k]}")
    print(f"figures {len(f)} · found {len(f) - len(missing)} · missing {len(missing)}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
