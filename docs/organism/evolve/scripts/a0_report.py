#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:15 +0400 — PREREG-EVOLVE-CAL A3.6 (1) as amended by A3b.2: Stage A0's reader. It reads the incumbent and the epsilon twins of the FULL S1, prints WHICH of the three readings
# moved in each twin (the verifier's limit 1), the keyed comparison with the incumbent (moment flips = discrete + unmatched rows, A3b.1; other kinds' discrete payloads named OUTSIDE it), the replication of the incumbent's journal
# against the production worker's RECORDED round-13 journal with its plant, and the slot ledger's END line (cap, peak, exit) and the anon sampler's maxima for each twin.
"""docs/organism/evolve/scripts/a0_report.py — the N1 STAGE READER (Stage A0's report, and the level choice and the ruled Stage B rule over every epsilon twin present; tests/tools/test_evolve_cal_n1_report.py).

usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/a0_report.py --dir <n1 out root> --recorded <round-13 incumbent journal (.jsonl.gz or a dir of .jsonl)> --out report.json [--ledger L] [--sampler anon.csv]

The incumbent is `<dir>/inc`; every other directory with a reading.json whose variant starts with `eps:` is an epsilon twin and is read against it (`seed:` twins are listed, not decided on).
Nothing here chooses: it prints the A3b.2 decision functions' own outputs (`a0_decision`; `a0plus_decision` once six epsilon twins are present).
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from pathlib import Path

from tools import evolve_cal as cal                     # noqa: E402
from tools import evolve_cal_analyse as an              # noqa: E402


def load(d: Path):
    return json.loads((d / "reading.json").read_text()), cal.read_twin_journal(d)


def recorded_rows(p: Path):
    p = Path(p)
    if p.is_file() and p.name.endswith(".gz"):
        with gzip.open(p, "rt") as f:
            return [json.loads(x) for x in f.read().splitlines() if x.strip()]
    rows = []
    for f in sorted(p.glob("*.jsonl")):
        rows += [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    return rows


def ledger_end(ledger: Path, label: str):
    """The slot ledger's END line of `evcal-<label>` (exit, cap, peak, swap) — the measured memory price of that twin (RULES 6d)."""
    out = None
    pat = re.compile(rf"END\s+\S+\s+evcal-{re.escape(label)}\s+slot\s+\d+\s+(.*)$")
    if ledger.exists():
        for line in ledger.read_text(errors="replace").splitlines():
            m = pat.search(line)
            if m:
                out = m.group(1).strip()
    return out


def sampler_max(csv: Path):
    """Per scope: the maximum anon / file / current / peak (kB) the 10 s sampler saw, and the number of samples."""
    out = {}
    if csv and csv.exists():
        for line in csv.read_text().splitlines()[1:]:
            c = line.split(",")
            if len(c) < 9:
                continue
            scope = c[1]
            vals = [int(x) if x.strip().isdigit() else 0 for x in c[2:7]]
            cur = out.setdefault(scope, {"n": 0, "anon_kb_max": 0, "file_kb_max": 0, "current_kb_max": 0, "peak_kb_max": 0, "memavail_kb_min": None})
            cur["n"] += 1
            cur["anon_kb_max"] = max(cur["anon_kb_max"], vals[0]); cur["file_kb_max"] = max(cur["file_kb_max"], vals[1])
            cur["current_kb_max"] = max(cur["current_kb_max"], vals[3]); cur["peak_kb_max"] = max(cur["peak_kb_max"], vals[4])
            ma = int(c[7]) if c[7].strip().isdigit() else None
            if ma is not None:
                cur["memavail_kb_min"] = ma if cur["memavail_kb_min"] is None else min(cur["memavail_kb_min"], ma)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--recorded", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ledger", default="/data/dev/swarm/slots/ledger.log")
    ap.add_argument("--sampler", default=None)
    ap.add_argument("--incumbent", default="inc", help="the incumbent twin's directory name (the STOP stage called it T0)")
    a = ap.parse_args(argv)
    d = Path(a.dir)
    if not (d / a.incumbent / "reading.json").exists():
        print(f"STOP: the incumbent twin ({a.incumbent}) has no reading.json yet")
        return 2
    inc_r, inc_j = load(d / a.incumbent)
    out: dict = {"incumbent": {k: inc_r.get(k) for k in ("variant", "q1_seen", "confirmed_share", "frames_filed", "journal_rows", "rows_consumed", "state_hash", "row_hash",
                                                       "cpu_s", "wall_s", "build_s", "maxrss_kb", "load0", "load1", "psi0", "psi1", "code")}}
    # ---- the replication control at FULL length: the incumbent's journal against the production worker's recorded journal, and the plant
    rec = recorded_rows(Path(a.recorded))
    n0 = len(inc_j)
    out["replication_vs_recorded"] = {"incumbent_rows": n0, "recorded_rows": len(rec), **{k: v for k, v in cal.compare_twins(inc_j, rec[:n0]).items() if k != "by_decile"},
                                      "keyed_full": cal.compare_twins_keyed(inc_j, rec)["moment"],
                                      "first_row_seq_mine_recorded": [inc_j[0].get("seq"), rec[0].get("seq") if rec else None],
                                      "last_row_seq_mine_recorded": [inc_j[-1].get("seq"), rec[-1].get("seq") if rec else None]}
    rows = json.loads(json.dumps(inc_j))
    i = next(k for k, x in enumerate(rows) if isinstance(x.get("cells"), list))
    before = json.dumps(rows[i], sort_keys=True)
    rows[i]["cells"] = [rows[i]["cells"][0] + 1, rows[i]["cells"][1]]
    assert json.dumps(rows[i], sort_keys=True) != before, "the plant changed nothing"
    pc = cal.compare_twins(inc_j, rows)
    out["replication_plant"] = {"row": i, "caught": (not pc["identical"]) and pc["first_diff"] == i and pc["discrete_diff_rows"] == 1}
    # ---- the epsilon twins (and the listing of seed twins), each against the incumbent
    twins, eps_readings, records = {}, {}, {}
    for sub in sorted(p for p in d.iterdir() if p.is_dir() and (p / "reading.json").exists() and p.name != a.incumbent):
        r, j = load(sub)
        variant = str(r.get("variant", ""))
        cmpk = cal.compare_twins_keyed(inc_j, j)
        row = {"variant": variant, "q1_seen": r.get("q1_seen"), "confirmed_share": r.get("confirmed_share"), "frames_filed": r.get("frames_filed"),
               "q1_seen_items": (round(r["q1_seen"] * an.Q1_ITEMS) if r.get("q1_seen") is not None else None),
               "journal_rows": r.get("journal_rows"), "state_hash_equal_to_incumbent": r.get("state_hash") == inc_r.get("state_hash"),
               "cpu_s": r.get("cpu_s"), "wall_s": r.get("wall_s"), "build_s": r.get("build_s"), "maxrss_kb": r.get("maxrss_kb"), "code": r.get("code"),
               "moment": cmpk["moment"], "other": cmpk["other"], "other_discrete": cmpk["other_discrete"],
               "moved_dims": (an.moved_dims(inc_r, r) if variant.startswith("eps:") else None),
               "frames_differs": r.get("frames_filed") != inc_r.get("frames_filed"),
               "equals_incumbent": (an.twin_equals(inc_r, an.twin_record(sub.name, r, cmpk)) if variant.startswith("eps:") else None)}
        twins[sub.name] = row
        if variant.startswith("eps:"):
            eps_readings[sub.name] = r
            records[sub.name] = an.twin_record(sub.name, r, cmpk)
    out["twins"] = twins
    out["epsilon_twins"] = sorted(eps_readings)
    # ---- the stages (A3.6 as amended by A3b): A0 = the k = 1 twins at 1e-3 and 1e-2; A0+ = k = 1..3 at both levels (six); the level choice over EVERY epsilon twin present (the smallest level
    # at which a twin MOVES); Stage B = the ruled rule M over the chosen level's first five twins. Every decision is the tested function's own output; missing twins are SAID, never assumed.
    by_vk = {}
    for label, r in eps_readings.items():
        lk = an._eps_k(r)
        if lk is not None:
            by_vk[lk] = (label, r)
    a0_keys = [(0.001, 1), (0.01, 1)]
    out["a0_twins"] = [by_vk[k][0] for k in a0_keys if k in by_vk]
    out["a0_missing"] = [f"eps:{k[0]!r}:{k[1]}" for k in a0_keys if k not in by_vk]
    if not out["a0_missing"]:
        out["a0_decision"] = an.a0_decision(inc_r, {by_vk[k][0]: by_vk[k][1] for k in a0_keys})
    six_keys = [(lv, k) for lv in (0.001, 0.01) for k in (1, 2, 3)]
    out["a0plus_twins"] = [by_vk[k][0] for k in six_keys if k in by_vk]
    if all(k in by_vk for k in six_keys):
        out["a0plus_decision"] = an.a0plus_decision(inc_r, {by_vk[k][0]: by_vk[k][1] for k in six_keys})
    levels = {}
    for label, rec in records.items():
        lk = an._eps_k(eps_readings[label])
        if lk is not None:
            levels.setdefault(lk[0], []).append(rec)
    out["choose_level"] = an.choose_level(inc_r, levels) if levels else {"chosen": None, "per_level": {}, "flat_factor": an.FLAT_FACTOR, "flatness_note": None}
    chosen = out["choose_level"]["chosen"]
    if chosen is not None:
        five = [by_vk[(chosen, k)][1] for k in range(1, 6) if (chosen, k) in by_vk]
        out["stage_b"] = an.stage_b_decision(inc_r, five) if len(five) == 5 else {"insufficient": f"{len(five)} of the first five twins at {chosen!r} are present"}
    # ---- the memory price (RULES 6d): the ledger's END line of each twin, the sampler's maxima
    labels = [a.incumbent] + sorted(twins)
    out["ledger_end"] = {lab: ledger_end(Path(a.ledger), lab) for lab in labels}
    out["sampler"] = sampler_max(Path(a.sampler)) if a.sampler else None
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("incumbent", "replication_vs_recorded", "replication_plant")}, sort_keys=True, default=str)[:3000])
    for name in sorted(twins):
        t = twins[name]
        print(f"{name:16s} {t['variant']:16s} q1 {t['q1_seen_items']} cs {t['confirmed_share']} frames {t['frames_filed']} moved {t['moved_dims']} flips {t['moment']['flips']} "
              f"(discrete {t['moment']['discrete_differing']}, unmatched {t['moment']['only_a'] + t['moment']['only_b']}) equals {t['equals_incumbent']} other_discrete {t['other_discrete']}")
    print("a0_decision:", json.dumps(out.get("a0_decision"), sort_keys=True, default=str), "· a0_missing:", out["a0_missing"])
    if "a0plus_decision" in out:
        print("a0plus_decision:", json.dumps(out["a0plus_decision"], sort_keys=True, default=str))
    cl = out["choose_level"]
    print("choose_level: chosen", cl["chosen"], "· per level:", json.dumps({str(e): {k: v[k] for k in ("n", "twins_moved", "flips", "twins_equal_to_incumbent", "flip_without_move", "spread_grows")} for e, v in cl["per_level"].items()}, sort_keys=True))
    if "stage_b" in out:
        print("stage_b (rule M):", json.dumps(out["stage_b"], sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
