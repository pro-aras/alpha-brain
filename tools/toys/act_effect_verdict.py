#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:47 +0400 — docs/organism/act/PREREG-ACT-EFFECT.md §5/§7: THE MECHANICAL VERDICT. The admission is read by this code from the bench's JSON files, never by a person;
# every threshold below is the law's own number (signed at 1d55eab). Pure functions over plain dicts (tests/creature/test_act_effect_verdict.py plants a failure for each mark).
"""tools/toys/act_effect_verdict.py — read the effect bench's JSON against PREREG-ACT-EFFECT's marks.

  python3 tools/toys/act_effect_verdict.py --statusquo docs/organism/act/data/statusquo-arms-12seeds.json --bench B.json --bench2 B2.json --lives L.json --equiv E.json \
      [--transfer T.json] [--oracle O.json] --unit-tests-ok --out V.json

Marks: M1 success (a +0.10 over R-NULL, b >= 11 of 12 seeds, c paired t p < 0.001, d >= R-SCR - 0.03, e the bar exceeds 5 SD of R-NULL2 - R-NULL); M2 lock (the two-act detector: >= 95 % of lives pass
at 960 acts, >= 90 % at 4,920); M3 no-ops (>= 95 % of lives <= 0.25, graded ONLY jointly with M1 and M2); M4 learned set (a and b each in >= 90 % of lives); M5 the plants; M6/M9 unit tests; M7 determinism;
M8 equivalence. ADMIT iff every mark passes and the bench is not VOID (a plant not caught, or a determinism failure, means the instrument is wrong).
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

T_CRIT_P001 = {11: 4.437}              # one-sided p < 0.001, df = 11 (12 seeds)
BAR_GAIN = 0.10                        # M1 (a): the A4L-EXPLORE §5 bar over R-NULL
BAR_VS_R_SCR = -0.03                   # M1 (d)
MIN_POSITIVE_SEEDS = 11                # M1 (b)
M2_PASS_960, M2_PASS_4920 = 0.95, 0.90
M3_SHARE = 0.95
M4_SHARE = 0.90
PLANT_PASS_MAX = 0.05                  # P-OLD, K-ARGMAX: at most 5 % of lives pass the lock detector
DEAL_MAX_OVER_NULL = 0.02
DEAL_NOOP_SHARE = 0.5
EPS = 1e-12
ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
NEW_ALTERNATIVES = ("A-PROP", "A-UCB", "A-RATE", "A-BOTH", "R-WSLS", "R-WALK")


def per_seed(arm: Dict[str, object]) -> List[float]:
    return [float(x) for x in arm["per_seed"]] if "per_seed" in arm else [float(r["success_rate"]) for r in arm["runs"]]


def mean(xs: Sequence[float]) -> float:
    return statistics.fmean(xs)


def sd(xs: Sequence[float]) -> float:
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def paired_t(d: Sequence[float]) -> float:
    s = sd(d)
    return mean(d) / (s / math.sqrt(len(d))) if s > 0 else (math.inf if mean(d) > 0 else 0.0)


def merge_benches(benches: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:49 +0400 — the bench runs in halves (two slots); united here, and refused if the halves disagree on the seeds or hold the same arm twice."""
    seeds = benches[0].get("seeds")
    arms: Dict[str, object] = {}
    for b in benches:
        if b.get("seeds") != seeds:
            raise ValueError("the bench halves were run on different seeds")
        for k, v in b["arms"].items():
            if k in arms:
                raise ValueError(f"arm {k!r} appears in two halves")
            arms[k] = v
    return {"seeds": seeds, "arms": arms}


def presence_counts(arm: Dict[str, object]) -> Optional[Dict[str, Dict[str, int]]]:
    """Per act, the outcomes with a KNOWN effect, the EXCLUDED ones (the silent-reset boundary, a life's start) and the total, summed over the seeds (#168). None when a run carries no counts —
    never zeros. A row where known + excluded != total is a defect of the instrument and raises."""
    runs = arm.get("runs", [])
    have = [("effect_counts" in r) for r in runs]
    if not runs or not any(have):
        return None
    if not all(have):
        raise ValueError("presence counts are on some runs and missing on others (never summed over a part)")
    out = {a: {"known": 0, "excluded": 0, "total": 0} for a in ACT_NAMES}
    for r in runs:
        for a in ACT_NAMES:
            c = r["effect_counts"][a]
            if c["known"] + c["excluded"] != c["total"]:
                raise ValueError(f"presence counts do not reconcile for {a!r} (seed {r.get('seed')}): {c}")
            for k in ("known", "excluded", "total"):
                out[a][k] += int(c[k])
    return out


def verdict(statusquo: Dict[str, object], bench: Dict[str, object], bench2: Dict[str, object], lives: Dict[str, object], equiv: Dict[str, object],
            unit_tests_ok: bool) -> Dict[str, object]:
    sq = statusquo["arms"]
    null, r3, ceil = per_seed(sq["ii"]), per_seed(sq["iii"]), per_seed(sq["iv-0.5"])
    arms = bench["arms"]
    n = len(null)
    if n != 12 or bench.get("seeds") != statusquo.get("seeds"):
        raise ValueError(f"the law reads 12 paired seeds; got n = {n}, seeds equal: {bench.get('seeds') == statusquo.get('seeds')}")
    c, r_scr, null2 = per_seed(arms["C-SCR"]), per_seed(arms["R-SCR"]), per_seed(arms["R-NULL2"])
    d = [x - y for x, y in zip(c, null)]
    t = paired_t(d)
    pos = sum(1 for x in d if x > 0)
    null_diff_sd = sd([x - y for x, y in zip(null2, null)])
    r3_p95 = mean(r3) + 1.645 * sd(r3)
    m1 = {"a": mean(d) >= BAR_GAIN - EPS, "b": pos >= MIN_POSITIVE_SEEDS, "c": t > T_CRIT_P001[n - 1], "d": mean(c) - mean(r_scr) >= BAR_VS_R_SCR - EPS,
          "e": BAR_GAIN > 5.0 * null_diff_sd, "gain": mean(d), "positive_seeds": pos, "t": t, "t_crit": T_CRIT_P001[n - 1], "minus_r_scr": mean(c) - mean(r_scr)}
    m1["pass"] = all(m1[k] for k in "abcde")

    key = lambda h: f"h{lives['acts']}" if h == "full" else "h960"
    cs = lives["arms"]["C-SCR"]["summary"]
    m2 = {"pass_960": cs["h960"]["lock_pass_share"], "pass_full": cs[key("full")]["lock_pass_share"]}
    m2["pass"] = m2["pass_960"] >= M2_PASS_960 - EPS and m2["pass_full"] >= M2_PASS_4920 - EPS
    m3_alone = cs["noop_share"]["le_0.25_share"] >= M3_SHARE - EPS
    m3 = {"alone": m3_alone, "le_0.25_share": cs["noop_share"]["le_0.25_share"], "median": cs["noop_share"]["median"], "pass": bool(m3_alone and m1["pass"] and m2["pass"])}
    m4 = {"a_share": cs.get("m4a_ge_0.95_share"), "b_share": cs.get("m4b_ge_0.95_share"), "a_median": cs.get("m4a_median"), "b_median": cs.get("m4b_median"),
          "exact_set_median": cs.get("exact_set_median"), "latency": cs.get("latency_first_act_set_holds_60")}
    m4["pass"] = bool(m4["a_share"] is not None and m4["a_share"] >= M4_SHARE - EPS and m4["b_share"] is not None and m4["b_share"] >= M4_SHARE - EPS)

    la = lives["arms"]
    deal_mean = mean(per_seed(arms["P-DEAL"]))
    plants = {"P-DEAL": {"mean": deal_mean, "over_null": deal_mean - mean(null), "noop_ge_0.5_share": la["P-DEAL"]["summary"]["noop_share"]["ge_0.5_share"]},
              "K-ARGMAX": {"pass_960": la["K-ARGMAX"]["summary"]["h960"]["lock_pass_share"], "pass_full": la["K-ARGMAX"]["summary"][key("full")]["lock_pass_share"]},
              "P-OLD": {"pass_960": la["P-OLD"]["summary"]["h960"]["lock_pass_share"], "pass_full": la["P-OLD"]["summary"][key("full")]["lock_pass_share"]}}
    plants["P-DEAL"]["caught"] = plants["P-DEAL"]["over_null"] <= DEAL_MAX_OVER_NULL + EPS and plants["P-DEAL"]["noop_ge_0.5_share"] >= DEAL_NOOP_SHARE - EPS
    for k in ("K-ARGMAX", "P-OLD"):
        plants[k]["caught"] = plants[k]["pass_960"] <= PLANT_PASS_MAX + EPS and plants[k]["pass_full"] <= PLANT_PASS_MAX + EPS
    m5 = {"plants": plants, "pass": all(p["caught"] for p in plants.values()) and bool(unit_tests_ok)}

    b2 = bench2["arms"]
    m7_null = per_seed(arms["R-NULL"]) == null if "R-NULL" in arms else False
    m7_twice = per_seed(arms["C-SCR"]) == per_seed(b2["C-SCR"]) if "C-SCR" in b2 else False
    m7_null_twice = per_seed(arms["R-NULL"]) == per_seed(b2["R-NULL"]) if ("R-NULL" in arms and "R-NULL" in b2) else False
    m7 = {"null_equals_landed_rows": m7_null, "candidate_twice_identical": m7_twice, "null_twice_identical": m7_null_twice, "pass": m7_null and m7_twice and m7_null_twice}
    m8 = {"steps": equiv.get("steps"), "mismatches": equiv.get("mismatches"), "pass": bool(equiv.get("pass"))}
    marks = {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": {"pass": bool(unit_tests_ok), "what": "unit test (tests/creature/test_act_effect_toy.py)"},
             "M7": m7, "M8": m8, "M9": {"pass": bool(unit_tests_ok), "what": "unit test (tests/creature/test_act_effect_toy.py TestBoundaryRuleM9)"}}
    void = (not m5["pass"]) or (not m7["pass"])
    admit = all(marks[k]["pass"] for k in marks) and not void

    alts: Dict[str, Dict[str, object]] = {}
    for k in NEW_ALTERNATIVES:
        if k in arms:
            ps = per_seed(arms[k])
            alts[k] = {"mean": mean(ps), "minus_null": mean(ps) - mean(null), "minus_r3": mean(ps) - mean(r3), "clears_r3_seedwise_p95": mean(ps) > r3_p95}
    for k, name in (("v", "A-VAL"), ("v-b", "A-SMP")):
        if k in sq:
            ps = per_seed(sq[k])
            alts[name] = {"mean": mean(ps), "minus_null": mean(ps) - mean(null), "minus_r3": mean(ps) - mean(r3), "clears_r3_seedwise_p95": mean(ps) > r3_p95}
    readings = {"null_mean": mean(null), "null_sd": sd(null), "r3_mean": mean(r3), "r3_sd": sd(r3), "r3_seedwise_p95": r3_p95, "ceiling_mean": mean(ceil), "r_scr_mean": mean(r_scr),
                "c_scr_mean": mean(c), "c_scr_minus_null": mean(d), "c_scr_minus_r3": mean(c) - mean(r3), "c_scr_minus_r_scr": mean(c) - mean(r_scr),
                "null2_minus_null_sd": null_diff_sd, "smallest_detectable_gap_seed_level": T_CRIT_P001[n - 1] * sd(d) / math.sqrt(n), "paired_diff_sd_vs_null": sd(d),
                "c_scr_per_seed": c, "c_scr_effect_counts": presence_counts(arms["C-SCR"])}
    return {"marks": marks, "admit": admit, "void": void, "readings": readings, "alternatives": alts,
            "next_law_cases": [k for k, v in alts.items() if v["clears_r3_seedwise_p95"] and k != "C-SCR"]}


def _fmt(v: Dict[str, object]) -> str:
    m, r = v["marks"], v["readings"]
    lines = [f"PREREG-ACT-EFFECT verdict — ADMIT: {v['admit']} · VOID: {v['void']}",
             f"  R-NULL {r['null_mean']:.4f} ± {r['null_sd']:.4f} · R-3 {r['r3_mean']:.4f} (seed-wise p95 {r['r3_seedwise_p95']:.4f}) · R-SCR {r['r_scr_mean']:.4f} · R-CEIL {r['ceiling_mean']:.4f} · C-SCR {r['c_scr_mean']:.4f}",
             f"  C-SCR − R-NULL {r['c_scr_minus_null']:+.4f} · − R-3 {r['c_scr_minus_r3']:+.4f} · − R-SCR {r['c_scr_minus_r_scr']:+.4f} · smallest detectable gap {r['smallest_detectable_gap_seed_level']:.4f} · null-vs-null SD {r['null2_minus_null_sd']:.4f}"]
    for k, x in m.items():
        extra = {kk: vv for kk, vv in x.items() if kk != "pass" and not isinstance(vv, (dict, list))}
        lines.append(f"  {k}: {'PASS' if x['pass'] else 'FAIL'} {extra}")
    cnt = r.get("c_scr_effect_counts")
    if cnt:
        lines.append("  C-SCR per-act outcomes (known / excluded / total), summed over the seeds: " + "; ".join(f"{a} {x['known']}/{x['excluded']}/{x['total']}" for a, x in cnt.items()))
    lines.append("  alternatives (printed, never admitted): " + "; ".join(f"{k} {x['minus_null']:+.3f} vs null, {x['minus_r3']:+.3f} vs R-3{' [clears R-3 p95]' if x['clears_r3_seedwise_p95'] else ''}" for k, x in v["alternatives"].items()))
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--statusquo", required=True)
    ap.add_argument("--bench", required=True, nargs="+", help="one or more halves of the bench (united)")
    ap.add_argument("--bench2", required=True, nargs="+", help="the second run of R-NULL and C-SCR (M7)")
    ap.add_argument("--lives", required=True)
    ap.add_argument("--equiv", required=True)
    ap.add_argument("--unit-tests-ok", action="store_true", help="assert that tests/creature/test_act_effect_toy.py read OK on the code that produced the files (the caller reads the log)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(list(argv) if argv is not None else None)
    load = lambda p: json.loads(Path(p).read_text())
    v = verdict(load(a.statusquo), merge_benches([load(p) for p in a.bench]), merge_benches([load(p) for p in a.bench2]), load(a.lives), load(a.equiv), a.unit_tests_ok)
    Path(a.out).write_text(json.dumps(v, indent=1))
    print(_fmt(v))
    return 0 if v["admit"] else 1


if __name__ == "__main__":
    sys.exit(main())
