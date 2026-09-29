#!/usr/bin/env python3
# edit: Claude (Fable 5.1, the seat), 2026-09-29 16:44 +0400 — PREREG-BRAIN-DRIVES §4 (signed 3aa380b, sha256 a5fdea1e…): the gate's reader.
"""tools/brain/drive_gate.py --runs RUNS --bench BENCH --stage1 STAGE1 [--out OUT] [--new-seed 20261104]

Reads the gate of PREREG-BRAIN-DRIVES once its runs are done, and decides nothing the law does not say:
  I1   each B-OFF replay equals its closed journal (the replay's own exit, written by the gate's script) and the identity
       plant diverged;
  I2   each B-ON journal, its `turn` rows removed, equals B-OFF's row for row;
  JB   each B-ON `turn` row equals the bench's turn for the same scene (the probe's `-bench.jsonl`, under the life's own BRAIN line);
  J    the probe with the production turn gives stage −1's table again, figure for figure;
  S U R D E   read on the never-used world's bench run; the planted say and the two nulls beside them;
  C    the mind's CPU per training canvas, B-ON over B-OFF (the replay's `cpu_ms`).
The truth is read by the bench only. A presence count stands beside every rate."""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SEEDS = (20261101, 20261102, 20261103)
LIVES = Path("/data/dev/genome-lives")
BARS = {"S": 0.95, "U": 0.90, "R": 0.85, "D": 0.05, "D_p": 1e-3, "E": 0.20, "C": 1.5, "planted": 0.05}
TURN_KEYS = ("scene", "n_hyp", "order", "members", "held", "expected", "say", "ask", "reason", "surprise", "heard")
J_KEYS = ("says", "says_series", "asks", "asks_series", "surprise_believed", "surprise_believed_series", "surprise_held",
          "surprise_held_series", "doubt", "null", "say_lengths", "by_things_in_scene", "first_calibrated_canvas")


def rows_of(p: Path) -> List[Dict[str, object]]:
    return [json.loads(line) for line in Path(p).read_text().splitlines() if line.strip()]


def is_turn(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "turn"


def canon(r: Dict[str, object]) -> str:
    return json.dumps(r, sort_keys=True)


# ================================================================================================ the body's marks
def mark_i1(run: Path, plant: Optional[Path]) -> Dict[str, object]:
    p = run / "off.exit"
    j = run / "off" / "journal.jsonl"
    out = {"exit": int(p.read_text().strip()) if p.exists() else None,
           "rows": len(j.read_text().splitlines()) if j.exists() else None}
    out["pass"] = bool(out["exit"] == 0 and out["rows"])
    if plant is not None:
        q = plant / "plant.exit"
        out["plant_exit"] = int(q.read_text().strip()) if q.exists() else None
    return out


def mark_i2(jon: Sequence[Dict[str, object]], joff: Sequence[Dict[str, object]]) -> Dict[str, object]:
    rest = [r for r in jon if not is_turn(r)]
    first = None
    for k, (a, b) in enumerate(zip(rest, joff)):
        if canon(a) != canon(b):
            first = {"row": k, "seq": a.get("seq"), "on": canon(a)[:200], "off": canon(b)[:200]}
            break
    return {"rows_on": len(jon), "turn_rows": len(jon) - len(rest), "rows_off": len(joff), "first_difference": first,
            "pass": bool(first is None and len(rest) == len(joff) and len(joff) > 0)}


def mark_jb(jon: Sequence[Dict[str, object]], bench: Sequence[Dict[str, object]]) -> Dict[str, object]:
    turns = {int(r["scene"]): r for r in jon if is_turn(r)}
    first, equal, by_key = None, 0, collections.Counter()
    for b in bench:
        t = turns.get(int(b["scene"]))
        if t is None:
            by_key["no turn row"] += 1
            first = first or {"scene": b["scene"], "key": "no turn row"}
            continue
        bad = [k for k in TURN_KEYS if canon({"v": t.get(k)}) != canon({"v": b.get(k)})]
        if bad:
            by_key.update(bad)
            first = first or {"scene": b["scene"], "key": bad[0], "body": canon({"v": t.get(bad[0])})[:200],
                              "bench": canon({"v": b.get(bad[0])})[:200]}
        else:
            equal += 1
    return {"bench_rows": len(bench), "turn_rows": len(turns), "equal": equal, "differing_by_key": dict(by_key),
            "first_difference": first, "pass": bool(len(bench) > 0 and equal == len(bench) == len(turns))}


def train_rows(root: Path, ws: int) -> Dict[str, List[int]]:
    """Per training moment of the closed life's tape, the seqs of its ear rows and its eye row."""
    from creature.tape import read_tape
    seqs: Dict[str, List[int]] = collections.defaultdict(list)
    for r in read_tape(root):
        meta = r.get("meta") or {}
        m = meta.get("moment")
        if meta.get("source") == "scene" and r["sense"] in ("ear", "eye") and m is not None and str(m).startswith(f"sc{ws}t"):
            seqs[str(m)].append(int(r["seq"]))
    return seqs


def canvas_cpu(timings: Path, seqs: Dict[str, List[int]]) -> Dict[str, object]:
    ms = {int(r["seq"]): r for r in rows_of(timings)}
    cpu, wall, missing = [], [], 0
    for m in sorted(seqs):
        ss = seqs[m]
        if any(s not in ms or "cpu_ms" not in ms[s] for s in ss):
            missing += 1
            continue
        cpu.append(sum(float(ms[s]["cpu_ms"]) for s in ss))
        wall.append(sum(float(ms[s]["ms"]) for s in ss))
    return {"n": len(cpu), "missing": missing, "mean_cpu_ms": float(np.mean(cpu)) if cpu else None,
            "median_cpu_ms": float(np.median(cpu)) if cpu else None, "mean_wall_ms": float(np.mean(wall)) if wall else None,
            "last_1000_mean_cpu_ms": float(np.mean(cpu[-1000:])) if cpu else None}


def mark_c(run: Path, root: Path, ws: int) -> Dict[str, object]:
    seqs = train_rows(root, ws)
    a, b = canvas_cpu(run / "on" / "timings.jsonl", seqs), canvas_cpu(run / "off" / "timings.jsonl", seqs)
    ratio = (a["mean_cpu_ms"] / b["mean_cpu_ms"]) if (a["mean_cpu_ms"] and b["mean_cpu_ms"]) else None
    return {"on": a, "off": b, "ratio": ratio, "bar": BARS["C"], "canvases": len(seqs),
            "pass": bool(ratio is not None and ratio <= BARS["C"] and a["n"] == b["n"] == len(seqs) and len(seqs) > 0)}


def turn_row_bytes(jon: Sequence[Dict[str, object]]) -> Dict[str, object]:
    v = [len(json.dumps(r)) + 1 for r in jon if is_turn(r)]
    return {"rows": len(v), "mean_bytes": float(np.mean(v)) if v else None, "total_mb": sum(v) / 1e6}


# ================================================================================================ the bench's marks
def mark_j(new: Dict[str, object], old: Dict[str, object]) -> Dict[str, object]:
    bad = [k for k in J_KEYS if canon({"v": new.get(k)}) != canon({"v": old.get(k)})]
    return {"keys_read": len(J_KEYS), "differing": bad, "pass": not bad}


def bench_marks(g: Dict[str, object]) -> Dict[str, object]:
    s, null = g["says"], g["null"]
    series = [w for w in g["says_series"] if w["canvases"]]
    low = min(series, key=lambda w: w["rate"])
    S = {"true": s["true"], "n": s["graded"], "not_graded": s["no_thing_under_the_target"], "null_max": max(null["says_true"]),
         "null_draws": len(null["says_true"]), "bar": BARS["S"]}
    S["pass"] = bool(s["graded"] and s["true"] >= BARS["S"] and s["true"] > S["null_max"])
    U = {"unique_true": s["unique_true"], "n": s["graded"], "bar": BARS["U"],
         "pass": bool(s["graded"] and s["unique_true"] >= BARS["U"])}
    R = {"lowest_window": {"from": low["from"], "to": low["to"], "rate": low["rate"], "canvases": low["canvases"]},
         "windows": len(series), "overall": s["rate"], "bar": BARS["R"], "pass": bool(low["rate"] >= BARS["R"])}
    D = {**g["D"], "n_doubted": g["doubt"]["doubted"]["believed_names"], "n_undoubted": g["doubt"]["undoubted"]["believed_names"],
         "right_doubted": g["doubt"]["doubted"]["right"], "right_undoubted": g["doubt"]["undoubted"]["right"], "bar": BARS["D"]}
    D["pass"] = bool(D["difference"] >= BARS["D"] and D["p_exact_one_sided"] < BARS["D_p"])
    e = g["surprise_believed"]
    E = {"mean": e["mean"], "n": e["n"], "null_min": min(null["surprise_believed"]), "null_draws": len(null["surprise_believed"]),
         "bar": BARS["E"]}
    E["pass"] = bool(e["n"] and e["mean"] <= BARS["E"] and e["mean"] < E["null_min"])
    P = {**g["control_planted_say"], "bar": BARS["planted"]}
    P["caught"] = bool(P["n"] and P["true"] < BARS["planted"])
    return {"S": S, "U": U, "R": R, "D": D, "E": E, "control_planted_say": P}


# ================================================================================================ the gate
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--stage1", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--new-seed", type=int, default=20261104)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--plant-seed", type=int, default=20261102)
    a = ap.parse_args()
    runs, bench, stage1 = Path(a.runs), Path(a.bench), Path(a.stage1)
    out = Path(a.out) if a.out else runs.parent / "read"
    out.mkdir(parents=True, exist_ok=True)
    res: Dict[str, object] = {"seeds": [], "bars": BARS}
    for ws in a.seeds:
        run = runs / str(ws)
        jon, joff = rows_of(run / "on" / "journal.jsonl"), rows_of(run / "off" / "journal.jsonl")
        jb_rows = rows_of(bench / "jb" / f"drive-{ws}-n10000-bench.jsonl")
        one = {"world_seed": ws,
               "I1": mark_i1(run, (runs / str(a.plant_seed)) if ws == a.plant_seed else None),
               "I2": mark_i2(jon, joff), "JB": mark_jb(jon, jb_rows),
               "C": mark_c(run, LIVES / f"brain-lean-{ws}", ws), "turn_rows": turn_row_bytes(jon),
               "J": mark_j(json.loads((bench / "j" / f"drive-{ws}-n10000.json").read_text()),
                           json.loads((stage1 / f"drive-{ws}-n10000.json").read_text()))}
        res["seeds"].append(one)
        print(f"[{ws}] I1 {one['I1']} · I2 pass {one['I2']['pass']} (turn rows {one['I2']['turn_rows']}) · JB pass {one['JB']['pass']} "
              f"(equal {one['JB']['equal']} of {one['JB']['bench_rows']}) · J pass {one['J']['pass']} · C ratio {one['C']['ratio']}", flush=True)
    g = json.loads((bench / "g" / f"drive-{a.new_seed}-n10000.json").read_text())
    res["G"] = {"world_seed": a.new_seed, **bench_marks(g), "readings": g["readings"], "asks": g["asks"],
                "about_the_parents_thing": g["says"]["about_the_parents_thing"], "two_or_more_words": g["says"]["two_or_more_words"],
                "say_lengths": g["say_lengths"], "by_things_in_scene": g["by_things_in_scene"],
                "surprise_series": g["surprise_believed_series"], "says_series": g["says_series"], "null": g["null"]}
    S = res["seeds"]
    plant = next((s["I1"].get("plant_exit") for s in S if "plant_exit" in s["I1"]), None)
    v = {"I1": all(s["I1"]["pass"] for s in S) and plant not in (None, 0), "I1_plant_exit": plant,
         "I2": all(s["I2"]["pass"] for s in S), "JB": all(s["JB"]["pass"] for s in S), "J": all(s["J"]["pass"] for s in S),
         "C": all(s["C"]["pass"] for s in S),
         **{k: res["G"][k]["pass"] for k in ("S", "U", "R", "D", "E")},
         "control_planted_say_caught": res["G"]["control_planted_say"]["caught"]}
    v["wiring"] = bool(v["I1"] and v["I2"] and v["JB"] and v["J"])
    v["ADOPT"] = bool(v["wiring"] and v["S"] and v["U"] and v["R"] and v["D"] and v["E"] and v["C"] and v["control_planted_say_caught"])
    res["verdict"] = v
    (out / "gate.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    lines = [f"PREREG-BRAIN-DRIVES — the gate, read from {runs} and {bench}", ""]
    for k in ("I1", "I2", "JB", "J", "S", "U", "R", "D", "E", "C"):
        lines.append(f"  {k:3s} {'PASS' if v[k] else 'FAIL'}")
    lines += [f"  the identity plant's exit: {plant} (it must not be 0)",
              f"  the planted say caught: {v['control_planted_say_caught']}",
              f"  ADOPT: {v['ADOPT']}", ""]
    (out / "gate-report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
