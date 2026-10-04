#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:57 +0400 — PREREG-EVOLVE-CAL §2 «E3 re-graded» and C4.
"""docs/organism/evolve/scripts/e3_regrade.py — `confirmed_share` read RIGHT on the 13 judged rounds' recorded twin journals.

usage: PYTHONPATH=. python3 -B docs/organism/evolve/scripts/e3_regrade.py --recorded <evolve-cal-scratch/recorded> --out e3.json

The law (§2, C4): `tools/evolve.py:151` called `surprise_mark` with its arguments one place off, so every one of the 13 judged rounds read `confirmed_share` None
(«not gradable») although every twin journal carries `confirmed` on its moment rows. Here each round's recorded incumbent and mutant journals (brain-long-2's
`evolve/round-<n>/{incumbent,mutant}/journal`, copied) are graded with the call as D3 fixes it — `surprise_mark(journal_rows, status, declared)` — and printed:
the share of each twin, Δ = mutant − incumbent, the presence count (moment rows carrying `confirmed` / moment rows), and what the LEGACY two-verdict bar
(`tools.evolve.regression_bar`, margins and wall cost unchanged) reads once confirmed_share is graded: whether any of the 13 recorded verdicts would have changed.
(The three-verdict reading under the bands waits for the bands.) The PLANT: round 13's incumbent journal with `confirmed` stripped in memory must read None.
C4: every judged round graded (not None) on both twins AND the plant caught -> exit 0.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import evolve as ev                      # noqa: E402
from tools.verdict_life import surprise_mark        # noqa: E402

ROUNDS = tuple(range(2, 15))


def journal(d: Path):
    rows = []
    for f in sorted(Path(d).glob("*.jsonl")):
        rows += [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
    return rows


def read(rows):
    sm = surprise_mark(rows, {}, True)                 # D3's call: (journal, status, surprise_declared)
    moment = sum(1 for r in rows if "moment" in r and r.get("act") != "coarse")
    carrying = sum(1 for r in rows if "moment" in r and "confirmed" in r and r.get("act") != "coarse")
    return sm.get("overall_share"), {"moment_rows": moment, "carrying_confirmed": carrying, "canvases": sm.get("canvases")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recorded", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rec = Path(a.recorded)
    out = {"rounds": [], "plant": None}
    graded = 0
    for n in ROUNDS:
        p = json.loads((rec / "proposals" / f"PROPOSAL-{n}.json").read_text())
        si, pi = read(journal(rec / f"round-{n}" / "incumbent" / "journal"))
        sm_, pm = read(journal(rec / f"round-{n}" / "mutant" / "journal"))
        ok = si is not None and sm_ is not None
        graded += int(ok)
        inc, mut = dict(p["incumbent"]), dict(p["mutant"])
        inc["confirmed_share"], mut["confirmed_share"] = si, sm_
        legacy_verdict, legacy_reason = ev.regression_bar(inc, mut)
        out["rounds"].append({"round": n, "gene": p.get("gene"), "value": p.get("value"), "recorded_verdict": p["verdict"], "recorded_reason": p["reason"],
                              "confirmed_share": {"incumbent": si, "mutant": sm_, "delta": (None if not ok else round(sm_ - si, 6)),
                                                  "presence_incumbent": pi, "presence_mutant": pm},
                              "legacy_bar_with_confirmed_share": {"verdict": legacy_verdict, "reason": legacy_reason, "changed": legacy_verdict != p["verdict"]}})
    rows = journal(rec / "round-13" / "incumbent" / "journal")
    stripped = [{k: v for k, v in r.items() if k != "confirmed"} for r in rows]
    assert json.dumps(stripped) != json.dumps(rows), "the plant changed nothing"
    plant_share, _ = read(stripped)
    out["plant"] = {"stripped_of": "confirmed", "reads": plant_share, "caught": plant_share is None}
    out["graded_rounds"] = graded
    out["c4"] = bool(graded == len(ROUNDS) and out["plant"]["caught"])
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"{'round':>5} {'gene':<20} {'value':>8} {'recorded':<8} {'share inc':>9} {'share mut':>9} {'delta':>9} {'rows carrying':>14}  legacy bar with confirmed_share")
    for r in out["rounds"]:
        c = r["confirmed_share"]
        print(f"{r['round']:>5} {str(r['gene']):<20} {str(r['value']):>8} {r['recorded_verdict']:<8} {c['incumbent']!s:>9} {c['mutant']!s:>9} {c['delta']!s:>9} "
              f"{c['presence_incumbent']['carrying_confirmed']}/{c['presence_incumbent']['moment_rows']:<7} {r['legacy_bar_with_confirmed_share']['verdict']}"
              f"{' (CHANGED)' if r['legacy_bar_with_confirmed_share']['changed'] else ''}")
    print(f"graded rounds {graded} of {len(ROUNDS)} · plant {'CAUGHT' if out['plant']['caught'] else 'MISSED'} · C4 {'PASS' if out['c4'] else 'FAIL'} · "
          f"verdicts changed under the legacy bar once confirmed_share is graded: {sum(r['legacy_bar_with_confirmed_share']['changed'] for r in out['rounds'])} of {len(ROUNDS)}")
    return 0 if out["c4"] else 1


if __name__ == "__main__":
    sys.exit(main())
