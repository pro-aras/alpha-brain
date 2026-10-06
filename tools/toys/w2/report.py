"""tools/toys/w2/report.py — PREREG-W2 §4-§6: the READER over the bench seeds' records — the gates, the truth family,
the marks table per seed, and §6's TOTAL, ORDERED verdict.

edit: Kimi Code (K3, kimi-code, acting seat, alone), 2026-10-06 18:15 +0400 — AMENDMENT 1 (SIGNED x3, w2-1005
1893280) + the seat's G-PICTURE ruling (option (b), the board 2026-10-06 17:5x): G-PICTURE is a READING (printed,
never a gate); the NECESSITY mark per state word per seed = gain_margin = (AUC_CONT - AUC_NOSTATE)/(1 - AUC_NOSTATE)
>= 0.5, with NOSTATE >= 1 - eps (0.001) NOT GRADABLE by name (the divide-by-zero guard); a necessity-unproven word
does not bind and is NAMED. A1.3's sharpening: PASS needs >= 2 gradable-and-binding states on every seed (binding
includes the necessity mark). Red first: tests/tools/test_w2_report.py.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 09:1x +0400 — new file; law
docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §4 (the gates), §5 (the marks), §6 (the verdict rule, corrected after the
VERIFIER's refusal). Every figure carries its n and its presence counts; a «0» prints the rows read.

Run:  PYTHONPATH=. python3 -B -m tools.toys.w2.report --records docs/organism/whole/records/w2/runs [--out VERDICT.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from tools.toys.w2 import grade as G
from tools.toys.w2 import sweep as SW

LABELS = ("doubt", "young", "ask_prev")
WORDS = ("unsure", "fresh", "asked")
LABEL_OF = dict(zip(WORDS, LABELS))
SEEDS = (20261701, 20261702, 20261703)
S6_BAND = 2.0
EPS_NECESSITY = 0.001  # AMENDMENT 1 A1.2 (b), the seat's ruling of 2026-10-06: NOSTATE >= 1 - eps reads NOT GRADABLE
                       # by name (the ablation closed the whole gap alone; the margin would divide by zero)


def _necessity(recs: Dict[int, dict], seeds: Sequence[int]) -> Dict[str, Dict[str, Dict[str, object]]]:
    """AMENDMENT 1 A1.2 (b) (the seat's ruling, the board 2026-10-06): G-PICTURE is a READING, never a gate; the
    NECESSITY mark per state word per seed = the margin the state row closes over the real ablation,
    gain_margin = (AUC_CONT - AUC_NOSTATE) / (1 - AUC_NOSTATE) >= 0.5. A word whose necessity is unproven does not
    bind and is NAMED (never a void, never a silent pass)."""
    out: Dict[str, Dict[str, Dict[str, object]]] = {w: {} for w in WORDS}
    for w in WORDS:
        for s in seeds:
            r = recs[s]
            n_ = r["nostate"]["auc"].get(w)
            c_ = r["cont"]["auc"].get(w)
            if n_ is None or c_ is None:
                out[w][s] = {"gradable": False, "why": "NOSTATE or CONT's AUC absent"}
                continue
            if n_ >= 1.0 - EPS_NECESSITY:
                out[w][s] = {"gradable": False, "nostate": n_, "why": "NOSTATE >= 1 - eps: the remaining gap is zero"}
                continue
            margin = (c_ - n_) / (1.0 - n_)
            out[w][s] = {"gradable": True, "nostate": n_, "cont": c_, "margin": margin,
                         "pass": bool(margin >= 0.5)}
    return out


def load(records: Path, seeds: Sequence[int] = SEEDS) -> Dict[int, dict]:
    return {s: json.loads((Path(records) / f"seed-{s}" / "reading.json").read_text(encoding="utf-8")) for s in seeds}


def _m5_am2(diag: Sequence[float], c_read: float) -> Dict[str, object]:
    """AMENDMENT 2's self-centred M5: centre = the seed's OWN dealt median; the plant (the ORACLE as a one-draw null)
    must reject."""
    v = [float(x) for x in diag]
    centre = float(np.median(np.asarray(v)))
    m5 = G.flatness(v, c_read, center=centre)
    plant = G.flatness([c_read], c_read, center=centre)
    m5["plant_oracle_one_draw_rejected"] = not plant["pass"]
    return m5


def _s6(recs: Dict[int, dict]) -> Dict[str, object]:
    """AMENDMENT 2's guard, verbatim: per cell, the three seeds' dealt centres span <= 2 x the pooled dealt sd."""
    rows = {}
    fires = []
    for w in WORDS:
        per = [[x for x in recs[s]["dealt_diag"][w] if x == x] for s in sorted(recs)]
        if any(len(p) < 2 for p in per):
            continue
        centres = [float(np.median(np.asarray(p))) for p in per]
        pooled = np.asarray([x for p in per for x in p])
        sd = float(np.std(pooled, ddof=1))
        span = float(max(centres) - min(centres))
        band = S6_BAND * sd
        ok = bool(span <= band)
        rows[w] = {"centres": centres, "span": span, "sigma_cell": sd, "band": band, "pass": ok}
        if not ok:
            fires.append(w)
    return {"rows": rows, "fires": fires, "pass": not fires}


def read(recs: Dict[int, dict]) -> Dict[str, object]:
    seeds = sorted(recs)
    lines: List[str] = []
    P = lines.append
    P(f"PREREG-W2 — the reader over bench seeds {seeds} (GRADED)")
    # ---- gates ----
    P("GATES (instrument; a failing gate VOIDs its cell, never a fail of the road)")
    gates_ok = True
    for s in seeds:
        r = recs[s]
        g = r["gates"]
        cen_ok = all(c["ok"] for c in g["census"])
        cen_n = sum(c["n_checked"] for c in g["census"])
        tru = g["truth"]
        g_blind = {w: bool(r["blind"].get(w) is not None and
                           (r["blind"][w] - 0.5) / max(r["oracle"].get(w, {}).get("c_read", 1.0) - 0.5, 1e-9) < 0.90)
                   for w in WORDS if r["blind"].get(w) is not None}
        g_oracle = {w: bool(r["oracle"].get(w) and r["oracle"][w]["c_read"] >= 0.90) for w in WORDS if r["oracle"].get(w)}
        ok_s = cen_ok and tru["planted_caught"] and all(g_blind.values()) and all(g_oracle.values())
        gates_ok = gates_ok and ok_s
        P(f"  seed {s}: G-CENSUS {'OK' if cen_ok else 'FAILS'} ({len(g['census'])} points, {cen_n} words checked), "
          f"G-TRUTH {tru['n_equal']}/{tru['n']} specs regenerate equal, the planted bit {'CAUGHT' if tru['planted_caught'] else 'MISSED'}, "
          f"G-STREAM one hash {g['stream_hash'][:16]}…; G-AUC CONST {[round(r['const'][w], 4) if r['const'][w] == r['const'][w] else float('nan') for w in WORDS]}; "
          f"G-BLIND skill {g_blind}; G-ORACLE C_read>=0.90: {g_oracle}")
    # AMENDMENT 1 A1.2 (b) (the seat's ruling 2026-10-06): G-PICTURE is a READING, printed, NEVER a gate —
    # the necessity mark below carries the margin form with the epsilon guard.
    nec = _necessity(recs, seeds)
    P("G-PICTURE (a READING under the ruling — printed, never a void) + the NECESSITY mark (the margin form):")
    for w in WORDS:
        cells = nec[w]
        P(f"  {w}: " + "; ".join(
            f"seed {s}: " + (f"NOSTATE {cells[s]['nostate']:.4f} CONT {cells[s]['cont']:.4f} -> gain_margin "
                             f"{cells[s]['margin']:.4f} {'>= 0.5 pass' if cells[s]['pass'] else '< 0.5 FAILS'}"
                             if cells[s]["gradable"] else f"NOT GRADABLE ({cells[s]['why']})")
            for s in seeds))
    s6 = _s6(recs)
    P(f"  S6 (AMENDMENT 2's guard): {'HOLDS' if s6['pass'] else 'FIRES on ' + str(s6['fires'])} — "
      + "; ".join(f"{w} span {r['span']:.4f} band {r['band']:.4f}" for w, r in s6["rows"].items()))
    # ---- the truth family ----
    P("TRUTH/DELIVERY family (a failure here is the build's own fault — VOID by name, never a states-verdict):")
    truth_ok = True
    sweep_found = SW.sweep(Path("creature/senses/mentor.py")) + SW.sweep(Path("tools/toys/w2"))
    truth_ok = truth_ok and not sweep_found
    P(f"  M-PURE: {'CLEAN' if not sweep_found else sweep_found}")
    for s in seeds:
        mt = recs[s]["marks_truth"]
        for name in ("m_true", "m_attrib", "m_joint", "m_contingent_i", "m_selfvoice_answers"):
            m = mt[name]
            truth_ok = truth_ok and bool(m["pass"])
        P(f"  seed {s}: M-TRUE {'pass' if mt['m_true']['pass'] else 'FAILS: ' + str(mt['m_true']['first_false'])} "
          f"({mt['m_true']['n_productions']} productions, {mt['m_true']['n_rows']} rows); "
          f"M-ATTRIB {'pass' if mt['m_attrib']['pass'] else 'FAILS'} (0/{mt['m_attrib']['n_rows']} without source+tpl, "
          f"{mt['m_attrib']['n_unparseable']} UNPARSEABLE; coverage {mt['m_attrib']['coverage']['share']:.3f} of {mt['m_attrib']['coverage']['sayable']}); "
          f"M-JOINT {'pass' if mt['m_joint']['pass'] else 'FAILS'} (attended {mt['m_joint']['share']:.4f} of n={mt['m_joint']['n_rows']} vs null "
          f"q95 {mt['m_joint']['null']['q95']:.4f} mean {mt['m_joint']['null']['mean']:.4f}, anchors 0.896/0.655); "
          f"M-CONTINGENT (i) {mt['m_contingent_i']['n_aligned']}/{mt['m_contingent_i']['n_tokens']}; "
          f"M-SELFVOICE 0 self-source of {mt['m_selfvoice_answers']['n_ear_rows']} + answers off-referent {mt['m_selfvoice_answers']['n_answer_rows_off_referent']}")
    # ---- M-BIND per seed per state ----
    P("M-BIND (the groundability family; NOT GRADABLE named, never a silent pass):")
    cell_stat: Dict[str, Dict[int, Dict[str, object]]] = {w: {} for w in WORDS}
    m5_by: Dict[tuple, Dict[str, object]] = {}
    for w in WORDS:
        l = LABEL_OF[w]
        for s in seeds:
            r = recs[s]
            pos = r["test_n"][l]["pos"]
            neg = r["test_n"][l]["neg"]
            m5 = _m5_am2(r["dealt_diag"][w], (r["oracle"].get(w) or {}).get("c_read", float("nan")))
            m5_by[(s, w)] = m5
            cr = (r["oracle"].get(w) or {}).get("c_read")
            se = G.se0(pos, neg) if pos and neg else float("nan")
            smallest = 0.5 + G.Z_P001 * se if pos and neg else float("nan")
            bar_auc = (0.5 + 0.90 * (cr - 0.5)) if cr == cr and cr is not None else float("nan")
            grad = bool(pos > 0 and cr == cr and cr is not None and cr >= 0.90 and smallest == smallest
                        and bar_auc == bar_auc and smallest <= bar_auc and r["m1"].get(w) is not None
                        and w in r["dealt_diag"] and any(x == x for x in r["dealt_diag"][w]))
            if not grad:
                P(f"    {w} seed {s}: NOT GRADABLE (pos {pos}, C_read {cr if cr is not None else None}, smallest passable "
                  f"{smallest if smallest == smallest else 'n/a'} vs the skill bar's {bar_auc if bar_auc == bar_auc else 'n/a'})")
                cell_stat[w][s] = {"gradable": False, "ok": None}
                continue
            m1 = r["m1"][w]
            ok = bool(m1["pass"]) and m5["pass"]
            P(f"    {w} seed {s}: AUC {m1['auc']:.4f} C_read {cr:.4f} skill {m1['skill']:.3f} dealt q95 {m1['q95']:.4f} "
              f"(n+ {pos} n- {neg}) M5-own-centre {'flat' if m5['pass'] else 'TEACHES'} -> {'PASS' if ok else 'FAIL'}")
            cell_stat[w][s] = {"gradable": True, "ok": ok}
    binds = {}
    nec_ok = {}
    in_walk = {}
    for w in WORDS:
        grad_oks = [c["ok"] for c in cell_stat[w].values() if c["gradable"]]
        nec_cells = [c for c in nec[w].values() if c["gradable"]]
        nec_ok[w] = bool(nec_cells) and all(c["pass"] for c in nec_cells)
        # AMENDMENT 1 A1.2 (b): a state word binds only if M-BIND's own bars hold AND its necessity is proven by
        # the margin; a necessity-unproven word does not bind and is NAMED (never a void, never a silent pass).
        binds[w] = bool(grad_oks) and all(grad_oks) and nec_ok[w]
        # A1.3: the walk reads over the GRADABLE states (M-BIND-gradable somewhere AND necessity-gradable
        # somewhere); a state the closed record cannot supply, or whose necessity the instrument cannot prove
        # (the epsilon guard), is NAMED with its counts and does not void the walk.
        in_walk[w] = bool(grad_oks) and bool(nec_cells)
    walked = [w for w in WORDS if in_walk[w]]
    any_bind = any(binds[w] for w in walked)
    named_out = [w for w in WORDS if not in_walk[w]]
    P(f"  the walk's states: {walked}; NAMED out of the walk (never a silent pass): "
      + str({w: {"m_bind_gradable_seeds": [s for s in seeds if cell_stat[w][s]['gradable']],
                 "necessity_gradable_seeds": [s for s in seeds if nec[w][s].get('gradable')],
                 "test_pos": {s: recs[s]['test_n'][LABEL_OF[w]]['pos'] for s in seeds}} for w in named_out}))
    for w in WORDS:
        P(f"  M-BIND {w}: {'HOLDS' if binds[w] else ('NOT GRADABLE anywhere (named)' if not any(c['gradable'] for c in cell_stat[w].values()) else 'FAILS')} "
          f"({ {s: (c['ok'] if c['gradable'] else None) for s, c in cell_stat[w].items()} }); NECESSITY {w}: "
          + ("pass (the margin >= 0.5 on every gradable seed)" if nec_ok[w]
             else "NOT GRADABLE anywhere (named: " + "; ".join(str(c.get('why')) for c in nec[w].values() if not c['gradable']) + ")"
             if not any(c['gradable'] for c in nec[w].values())
             else "FAILS (the state row closes less than half the remaining gap: "
                  + "; ".join(f"seed {s} margin {c['margin']:.4f}" for s, c in nec[w].items() if c['gradable']) + ")"))
    # AMENDMENT 1 A1.3: gradable-AND-binding states per seed (binding includes the necessity mark); fewer than two
    # on a seed and the verdict never reads PASS — the sharpening's own sentence.
    bound = {w: {s: bool(cell_stat[w][s]["gradable"] and cell_stat[w][s]["ok"]
                         and nec[w][s].get("gradable") and nec[w][s].get("pass")) for s in seeds} for w in WORDS}
    gb_count = {s: sum(1 for w in WORDS if bound[w][s]) for s in seeds}
    enough = all(c >= 2 for c in gb_count.values())
    P(f"  gradable-and-binding states per seed: {gb_count} (the law's PASS needs >= 2 on every seed: "
      f"{'met' if enough else 'NOT MET — the bound states named: ' + str([w for w in WORDS for s in seeds if bound[w][s]])})")
    # ---- M-NOHARM ----
    P("M-NOHARM:")
    noharm_ok = True
    for s in seeds:
        r = recs[s]
        nm = r["cont"]["naming"]
        ph = r["proto_home"]
        a_ok = (nm["pass"] if nm["gradable"] else None)
        b_ok = bool(ph["n_on_state"] == 0)
        noharm_ok = noharm_ok and (a_ok is not False) and b_ok
        P(f"  seed {s}: (a) CONT {nm['cont']:.4f} vs NOSTATE {nm['nostate']:.4f} (n {nm['n']}) -> "
          f"{'NOT GRADABLE (NOSTATE < 0.90) — a reading, never a measured harm' if not nm['gradable'] else ('pass' if nm['pass'] else 'FAIL')}; "
          f"(b) proto-home {ph['n_on_state']} on the state row of {ph['n_present']} present (n {ph['n']}, smallest gap {ph['smallest_gap']:.3f}) -> "
          f"{'pass' if b_ok else 'FAIL'}")
    # ---- the dealt mentor's own skill level (row 4's measured comparison) ----
    teaching = {}
    for w in WORDS:
        for s in seeds:
            m5 = m5_by[(s, w)]
            cr = (recs[s]["oracle"].get(w) or {}).get("c_read")
            if cr == cr and cr is not None:
                teaching[(s, w)] = bool(m5["q95"] >= 0.5 + 0.90 * (cr - 0.5))
            else:
                teaching[(s, w)] = False
    teach_any = any(teaching.values())
    P(f"  the dealt mentor reaches M-BIND's skill level on: {[f'{w}@{s}' for (s, w), t in teaching.items() if t] or 'nothing'}")
    # ---- the verdict (§6 as AMENDMENT 1 amends it, TOTAL and ORDERED) ----
    truth_family_ok = truth_ok
    no_population = not any(recs[s]["test_n"][LABEL_OF[w]]["pos"] > 0 for w in WORDS for s in seeds)
    all_bind = bool(walked) and all(binds[w] for w in walked)
    row = None
    if not (gates_ok and s6["pass"] and truth_family_ok) or no_population or not any(in_walk.values()):
        row, verdict = 1, "VOID"
    elif all_bind and any_bind and enough and noharm_ok and not teach_any:
        row, verdict = 2, "PASS"
    elif all_bind and any_bind and enough and not teach_any:
        row, verdict = 3, "PASS-WITH-HARM"
    elif teach_any:
        row, verdict = 4, "FAIL-CONTINGENCY"
    elif any_bind:
        row, verdict = 5, "PARTIAL"
    else:
        row, verdict = 6, "FAIL-STRUCTURE"
    P(f"VERDICT (§6 as amended by AMENDMENT 1, row {row}): {verdict}")
    P(f"  binds {binds} noharm {noharm_ok} teach_any {teach_any} gates {gates_ok} s6 {s6['pass']} truth {truth_family_ok}")
    out = {"seeds": seeds, "s6": s6, "cells": {w: {str(s): cell_stat[w][s] for s in seeds} for w in WORDS},
           "necessity": {w: {str(s): nec[w][s] for s in seeds} for w in WORDS},
           "gradable_and_binding_per_seed": gb_count,
           "verdict": {"row": row, "verdict": verdict}, "lines": lines}
    return out


def main(argv: Sequence[str] = None) -> int:
    ap = argparse.ArgumentParser(description="PREREG-W2: the reader over the bench seeds' records")
    ap.add_argument("--records", type=str, required=True)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--out", type=str, default=None)
    a = ap.parse_args(argv)
    out = read(load(Path(a.records), a.seeds))
    for line in out["lines"]:
        print(line)
    if a.out:
        Path(a.out).write_text(json.dumps({k: v for k, v in out.items() if k != "lines"}, indent=1, sort_keys=True,
                                          default=str), encoding="utf-8")
        print(f"written {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
