"""bars_line.py — FROM CEILINGS TO THE SEAT'S §12 LINE (B1-PREREG.md §3.4, §5.2, §6; the seat's own tool).

edit: Claude (Fable 5.1), 2026-09-24 19:00 +0400 — the seat, alone.

Reads stage −1's `ceilings.json` and writes `bars.json` (what `brain.harness.results` reads) + the text of the
§12 line, by ONE declared rule (the seat's draft of 2026-09-24, `b1-seat-line-draft.md`, applied here so no bar is
typed by hand):

  a relation / perceptual family's bar (a COUNT k of n items):
      k_bar = ceil(n · max(k_min/n + hw95(k_min/n, n), 0.5 · ceiling))   capped at floor(n · ceiling), never under k_min
  the NAME bar (a share, per case): ceiling − 0.10, never under 0.5        (U1 (a))
  U1b / U2b / U6: the §5.2/§5.3 k (24 of 52; 69 of 104; 4 of 10) — construction-exact, no ceiling needed
  U4a: 0.5; U5: 0.8; KEEPS: 5 pp; COST: 3 × A0's solo ms/event (from solo-probe.json when present, else NO bar)
  margins: D1 (i) 10 pp · GROWS 5 pp · A1-MA − A1-ATT 3 pp at ≤ +10 % cost · interface 5 pp

The validator (`brain.harness.bars.validate_bars_line`) refuses a bar above its ceiling or under k_min/n and names
NOT GRADABLE families (ceiling ≤ k_min/n + hw95) — those get NO bar and the mark reads ORGAN LIMIT. The line is
printed for the seat to APPEND under §12 (dated; never edited after any graded answer exists — #228).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from brain.harness import bars as B  # noqa: E402

FAMILY_N = {"AFTER": 12, "BEFORE": 12, "BETWEEN": 12, "TWO_AFTER": 21, "CHAIN": 25, "MIRROR": 16, "LOOP": 14, "VOWEL": 40, "TRANSFER": 18}
FAMILY_NULL = {"AFTER": 1 / 25, "BEFORE": 1 / 25, "BETWEEN": 1 / 25, "TWO_AFTER": 1 / 25, "OTHER_CASE": 1 / 26, "CHAIN": 1 / 26,
               "TRANSFER": 1 / 9, "MIRROR": 0.5, "LOOP": 0.5, "VOWEL": 0.5}
MARGINS = {"d1_pp": 10.0, "grows_pp": 5.0, "ma_pp": 3.0, "ma_cost_pct": 10.0, "interface_pp": 5.0}
FIXED = {"U1b": 24, "U2b": 69, "U6": 4, "U4a": 0.5, "U5": 0.8, "KEEPS": 5.0}


def k_min(n: int, p: float, alpha: float = 0.001) -> int:
    for k in range(0, n + 1):
        if sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)) < alpha:
            return k
    return n + 1


def family_bar(name: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    n = int(entry.get("n") or FAMILY_N.get(name, 0))
    ceiling = float(entry["organ_ceiling"]["max"])
    null = FAMILY_NULL.get(name, 1 / 25)
    km = k_min(n, null) if n else None
    if not n:
        return {"n": 0, "bar": None, "why": "n = 0"}
    floor_share = km / n + B.binomial_half_width_95(km / n, n)
    if ceiling <= floor_share:
        return {"n": n, "k_min": km, "ceiling": ceiling, "bar": None, "not_gradable": True, "why": f"ORGAN LIMIT: ceiling {ceiling:.3f} <= k_min/n + hw95 {floor_share:.3f}"}
    share = max(floor_share, 0.5 * ceiling)
    k_bar = min(math.ceil(n * share), math.floor(n * ceiling))
    k_bar = max(k_bar, km)
    return {"n": n, "k_min": km, "ceiling": ceiling, "bar": int(k_bar), "bar_share": k_bar / n, "rule": "max(k_min/n + hw95, 0.5·ceiling), capped at the ceiling"}


def build(ceilings: Dict[str, Any], solo: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    fam = ceilings.get("families", {})
    u3: Dict[str, Any] = {}
    detail: Dict[str, Any] = {}
    for name in ("AFTER", "BEFORE", "BETWEEN", "TWO_AFTER", "OTHER_CASE", "CHAIN", "MIRROR", "LOOP", "VOWEL"):
        if name in fam:
            d = family_bar(name, fam[name])
            detail[name] = d
            if d.get("bar") is not None:
                u3[name] = d["bar"]
    transfer = None
    if "TRANSFER_AFTER" in fam and "TRANSFER_BEFORE" in fam:
        c = (fam["TRANSFER_AFTER"]["organ_ceiling"]["max"] + fam["TRANSFER_BEFORE"]["organ_ceiling"]["max"]) / 2
        d = family_bar("TRANSFER", {"n": 18, "organ_ceiling": {"max": c}})
        detail["TRANSFER"] = d
        transfer = d.get("bar")
    u1a: Dict[str, float] = {}
    for case in ("latin-upper", "latin-lower"):
        e = fam.get(f"NAMING_{case}_4fonts")
        if e:
            c = float(e["organ_ceiling"]["max"])
            u1a[case] = round(max(0.5, c - 0.10), 4)
            detail[f"U1a:{case}"] = {"ceiling": c, "bar": u1a[case], "rule": "ceiling − 10 pp, never under 0.5"}
    cost = None
    if solo and solo.get("probes", {}).get("A0", {}).get("ms_per_event_arm"):
        cost = round(3.0 * float(solo["probes"]["A0"]["ms_per_event_arm"]), 3)
    bars = {"U1a": u1a, "U1b": FIXED["U1b"], "U2b": FIXED["U2b"], "U3": u3, "TRANSFER": transfer, "U4a": FIXED["U4a"], "U5": FIXED["U5"],
            "U6": FIXED["U6"], "KEEPS": FIXED["KEEPS"], "COST": cost}
    line = ("§12 (the seat, " + time.strftime("%Y-%m-%d %H:%M %z") + "): bars from ceilings.json by ONE rule — "
            + "; ".join(f"{k} k={v['bar']} of {v['n']} (ceiling {v['ceiling']:.3f}, k_min {v['k_min']})" for k, v in detail.items() if v.get("bar") is not None and "n" in v)
            + "; NAME " + ", ".join(f"{c} {b}" for c, b in u1a.items())
            + f"; U1b {FIXED['U1b']}/52 · U2b {FIXED['U2b']}/104 · U6 {FIXED['U6']}/10 · U4a {FIXED['U4a']} · U5 {FIXED['U5']} · KEEPS {FIXED['KEEPS']} pp · COST {cost if cost else '— (no solo probe yet)'}"
            + f"; margins D1 {MARGINS['d1_pp']} pp · GROWS {MARGINS['grows_pp']} pp · MA {MARGINS['ma_pp']} pp at ≤ +{MARGINS['ma_cost_pct']} % cost · interface {MARGINS['interface_pp']} pp"
            + "; NOT GRADABLE (organ limit): " + (", ".join(k for k, v in detail.items() if v.get("not_gradable")) or "none"))
    return {"line": line, "bars": bars, "margins": MARGINS, "detail": detail, "ceilings_sha256": B.ceilings_sha256}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ceilings", default=str(REPO_ROOT / "docs" / "brain" / "b1" / "stage-1" / "ceilings.json"))
    p.add_argument("--solo", default=str(REPO_ROOT / "docs" / "brain" / "b1" / "stage-1" / "solo-probe.json"))
    p.add_argument("--out", default=str(REPO_ROOT / "docs" / "brain" / "b1" / "bars.json"))
    ns = p.parse_args(argv)
    ceilings = json.loads(Path(ns.ceilings).read_text())
    if ceilings.get("smoke"):
        raise SystemExit("ceilings.json is a --smoke record; bars come only from the FULL stage −1 (§3.4)")
    solo = json.loads(Path(ns.solo).read_text()) if Path(ns.solo).exists() else None
    out = build(ceilings, solo)
    out["ceilings_sha256"] = B.ceilings_sha256(Path(ns.ceilings))
    # the validator's own word on the U3 bars (shares), against the ceilings
    shares = {k: v / out["detail"][k]["n"] for k, v in out["bars"]["U3"].items()}
    out["validation"] = B.validate_bars_line(ceilings.get("families", {}), shares)
    Path(ns.out).write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(out["line"])
    print(f"[bars] wrote {ns.out} · validation {out['validation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
