#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:20 +0400 — POLLER-FIX G2: the 40-state verdict from the runs' own rows (bl2's 38 checkpoints + the closed final state, and bl3's fallback copy).
"""g2_combine.py — reads the g2.jsonl files of the G2 runs (the bl2 job and the bl3 job ran separately: bl3's copy is priced on its own, the law's §3) and prints the verdict over the
EXPECTED 40 labels (ck1..ck38, final, bl3-fallback), counted from the rows themselves: started / read / compared / differing, the roads before and after, the ablation guard, the plant.
A label with no row, or with a row that failed any check, makes the verdict NOT OK; the LAST row of a label wins (a re-run replaces). Exit 0 iff 40 of 40 and 0 differ.
usage: python3 -B g2_combine.py --in <g2.jsonl> [--in <g2.jsonl> ...] --out <prefix>      (writes <prefix>.txt and <prefix>.json)"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXPECTED = [f"ck{n}" for n in range(1, 39)] + ["final", "bl3-fallback"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ran = {}
    for p in a.inp:
        for l in Path(p).read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                ran[r["label"]] = r
    missing = [x for x in EXPECTED if x not in ran]
    n = len(EXPECTED)
    mine = [ran[x] for x in EXPECTED if x in ran]
    c = lambda f: sum(1 for r in mine if f(r))
    s = {"expected": n, "recorded": len(mine), "missing": missing, "ledger_has_canvas_index": c(lambda r: r.get("ledger_has_canvas_index")), "manifest_key_before": c(lambda r: r.get("manifest_has_key_before")),
         "compared": c(lambda r: r.get("compared")), "differing": c(lambda r: r.get("compared") and r.get("differs")), "old_road_ledger": c(lambda r: r.get("road_old") == "ledger"),
         "new_road_snapshot": c(lambda r: r.get("road_new") == "snapshot"), "ablation_to_ledger": c(lambda r: (r.get("ablated") or [None, None])[1] == "ledger"),
         "plant_reported_different": c(lambda r: (r.get("plant") or {}).get("reported_different")), "all_checks_ok": c(lambda r: r.get("ok")),
         "copy_mismatches": sum(int(r.get("copy_mismatches", 0) or 0) for r in mine), "copy_files": sum(int(r.get("copy_files", 0) or 0) for r in mine),
         "resume_s_total": round(sum(r.get("resume_s", 0) or 0 for r in mine), 1), "snapshot_s_total": round(sum(r.get("snapshot_s", 0) or 0 for r in mine), 1),
         "hwm_mb_max": max((r.get("hwm_mb") or 0) for r in mine) if mine else None}
    s["ok"] = bool(not missing and s["all_checks_ok"] == n and s["differing"] == 0 and s["new_road_snapshot"] == n and s["old_road_ledger"] == n)
    lines = [f"G2 over {n} saved states, from the runs' own rows: recorded {s['recorded']} of {n}" + (f" (MISSING {missing})" if missing else ""),
             f"presence: the ledger carried canvas_index in {s['ledger_has_canvas_index']} of {n}; the ORIGINAL manifest carried it in {s['manifest_key_before']} of {n} (the old-format premise: 0)",
             f"started {s['recorded']} of {n}; read {s['ledger_has_canvas_index']}; compared {s['compared']}; DIFFERING {s['differing']}",
             f"road before (the old reader on the original copy) = ledger on {s['old_road_ledger']} of {n}; road after Mind.resume + Mind.snapshot() under the OVERLAY = snapshot on {s['new_road_snapshot']} of {n}",
             f"the ablated-system guard (the key stripped from the new manifest) fell to the ledger road on {s['ablation_to_ledger']} of {n}; the +1 plant was reported DIFFERENT on {s['plant_reported_different']} of {n}",
             f"every check of a state holds on {s['all_checks_ok']} of {n}; copies verified file by file (size and mtime_ns): {s['copy_files']} files, {s['copy_mismatches']} mismatches",
             f"resume {s['resume_s_total']} s + snapshot {s['snapshot_s_total']} s in all; the largest process HWM {s['hwm_mb_max']} MB", "RESULT: " + ("OK" if s["ok"] else "NOT OK")]
    for lab in EXPECTED:
        r = ran.get(lab)
        lines.append(f"  {lab:13s} " + ("MISSING" if r is None else f"moments {r.get('moments')} canvas_index {r.get('reference')} old {r.get('road_old')}:{r.get('n_old')} new {r.get('road_new')}:{r.get('n_new')} "
                                          f"resume {r.get('resume_s')}s snapshot {r.get('snapshot_s')}s hwm {r.get('hwm_mb')} MB {'OK' if r.get('ok') else 'FAIL ' + str(r.get('error') or [k for k, v in (r.get('checks') or {}).items() if not v])}"))
    Path(a.out + ".txt").write_text("\n".join(lines) + "\n")
    Path(a.out + ".json").write_text(json.dumps({"summary": s, "rows": mine}, indent=1, sort_keys=True))
    print("\n".join(lines[:8]))
    return 0 if s["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
