#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-28 23:00 +0400 — every figure of VERDICT-BRAIN-IN-BODY's tables, recomputed from the graded records.
"""Prints the verdict's numbers from grade.json / the report files of rung 2, so the text can be checked line by line
(SOLUTIONS #242: a number written from memory is cross-checked against its file by script). Reads only."""
import json
import re
import sys
from pathlib import Path

O = Path("/data/dev/brain-runs/organ/rung2")
SEEDS = (20261101, 20261102, 20261103)


def f(x, nd=3):
    return "n/a" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


rows = {}
for ws in SEEDS:
    g = json.loads((O / str(ws) / "grade-brain" / "grade.json").read_text())
    b = g["bars"]
    fr = g["sets"]["fresh"]["marks"]
    rd = fr["roads"]["LAW"]
    p = g["paired"]
    rows[ws] = {
        "M1 covered (n)": f"{f(b['M1']['value'])} ({b['M1']['n']})", "M1 all": f(fr["M1"]["graded"]["all"]),
        "coverage": f(fr["M1"]["graded"]["coverage"]),
        "M2a refusal / false": f"{f(b['M2a']['value'])} / {f(b['M2a'].get('false_refusal'))}",
        "M2b": f(b["M2b"]["value"]), "M3": f(b["M3"]["value"]),
        "M4a carry / null p95": f"{f(g['M4a']['carry'])} / {f(g['M4a']['null_p95'])}", "M4a exist": f(g["M4a"]["exist"]),
        "M5 refused / named / valid / m3": f"{f(g['M5']['refused'])} / {f(g['M5']['named'])} / {g['M5']['n_valid']} → {f(g['M5']['valid_called_misuse'])} / {g['M5']['m3_pairs_called_misuse']}",
        "M6 pooled": f"{f(g['M6_pooled']['covered'])} (n {g['M6_pooled']['n_covered']}) {g['M6_pooled']['verdict'][:14]}",
        "meeting seen": g["meeting"]["seen"],
        "SPOKEN / TRUTH / NEED / MINIMAL": " / ".join(f(b[k]["value"]) for k in ("SPOKEN", "TRUTH", "TRUTH-NEED", "MINIMAL")),
        "null M1 p95 / M3 p95": f"{f(g['null']['m1_p95'])} / {f(g['null']['m3_p95'])}",
        "pair M1": f"{f(p['M1']['first'])} vs {f(p['M1']['second'])} n {p['M1']['n']} p {p['M1']['p']:.2e} own {f(p['M1']['second_own_pointing'])} heard {p['M1']['second_items'] - p['M1']['second_unheard']}/{p['M1']['second_items']} {p['M1']['verdict']}",
        "pair M3": f"n {p['M3']['n']} heard {p['M3']['second_items'] - p['M3']['second_unheard']}/{p['M3']['second_items']} {p['M3']['verdict'][:12]}",
        "pointer mismatches": g["pointer"]["mismatches"], "asks unanswered": g["counts"]["n_asks_without_answer"],
        "parity": (O / str(ws) / "parity.txt").read_text().splitlines()[1].strip()[:70],
        "identity": (O / "logs" / f"identity-{ws}.log").read_text().strip().splitlines()[-1],
        "disturbance": re.sub(r"\s+", " ", (O / str(ws) / "disturbance.txt").read_text().splitlines()[0])[:110],
    }
keys = list(rows[SEEDS[0]])
for k in keys:
    print(f"{k:<34} | " + " | ".join(str(rows[ws][k]) for ws in SEEDS))
n = json.loads((O / "20261102" / "grade-null" / "grade.json").read_text())
print("NULL life 20261102: M1", f(n["sets"]["fresh"]["marks"]["M1"]["graded"]["covered"]), "M3", f(n["bars"]["M3"]["value"]) if n.get("bars") else "n/a",
      "M4a carry", f(n["M4a"]["carry"]), "M5", n["M5"]["verdict"])
print((O / "20261102" / "null-identity.txt").read_text().splitlines()[0])
print((O / "20261102" / "twin-vs-blind.txt").read_text().splitlines()[0])
