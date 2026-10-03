#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm sleep), 2026-10-03 10:43 +0400 — the cross-check of VERDICT-SLEEP-AB: RAW (the verdict-relevant figures recomputed from the
# arms' own exam/ and readlist/ files, without importing tools/sleep_ab_read.py), LAW (PREREG-SLEEP-AB §7 walked clause by clause by its own decide()), DOC
# (generated blocks reproduced verbatim; every other number in the doc found in a source). SOLUTIONS #242 (a number written from memory is cross-checked
# against its file by script), #246 (1), #247 (5) (every instrument carries a planted control: tests/tools/test_check_sleep_ab_verdict.py).
"""tools/brain/check_sleep_ab_verdict.py --doc DOC [--fill] [--runs DIR] [--lists DIR] [--law PREREG]

Reads only: <runs>/READING.json, READING.txt, <runs>/<ARM>/exam/*.json, <runs>/<ARM>/readlist/*.json, <lists>/READ-W0-{out,in}-list.txt, the law, the doc.
Writes only with --fill (the generated blocks between `<!-- GEN:name BEGIN -->` and `<!-- GEN:name END -->` in DOC).

  RAW  every arm's R-A, R-B (mean and per thing), lost things, READ-W0-out/in recognised at end-w0 and at the end, every paired b/c/z, every U-mean test
       recomputed from the arms' own files and compared with READING.json. Presence counts (sittings, words present, things graded) are printed.
  LAW  §7 walked by decide(): each clause's input, outcome and the law's own words, from the RAW figures (not from the reader's verdict).
  DOC  each generated block equals what this script generates now; every other number in the doc is found in READING.json, READING.txt, the law or a
       generated block (a negative number must be found as a negative); every «A of B» is an allowed pair; the doc's VERDICT word equals decide()'s.
Exit 0 only when all three hold."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# ---- declared from PREREG-SLEEP-AB (law_constants_ok() reads each one out of the law's own text)
W1, W2, W3, CUT = 17289, 33828, 50095, 50094
EIGHT = ["arrow", "bar", "circle", "cross", "diamond", "ring", "square", "wave"]
FIVE = ["moon", "house", "tree", "cup", "key"]
ARMS = ["S", "N", "P", "PR"] + [f"U{d}" for d in range(1, 11)]
UARMS = [f"U{d}" for d in range(1, 11)]
LOST_BEFORE, LOST_AFTER = 0.8, 0.2
GRADABLE_MIN = 30
K_LAST = 3

DEFAULT_RUNS = Path("/data/dev/brain-runs/day0929/sleep-ab/runs2")
DEFAULT_LISTS = Path("/data/dev/brain-runs/day0929/sleep-ab/measure")
DEFAULT_LAW = Path("docs/brain/memory/PREREG-SLEEP-AB.md")


def window_of(seq: int) -> int:
    return 0 if seq < W1 else 1 if seq < W2 else 2 if seq < W3 else 3


def law_constants_ok(law_text: str) -> List[str]:
    """Each constant above must be readable in the law; returns the list of those that are not."""
    need = {"17,289": str(W1), "33,828": str(W2), "50,095": str(W3), "50,094": str(CUT),
            "fewer than 30 of the 224": str(GRADABLE_MIN), "≤ 0.2 after ≥ 0.8": f"{LOST_AFTER}/{LOST_BEFORE}"}
    return [f"{k!r} (for {v}) is not in the law" for k, v in need.items() if k not in law_text]


# ================================================================ RAW
def _words(p: Path) -> List[str]:
    return [w.strip() for w in p.read_text().splitlines() if w.strip()]


def raw_arm(runs: Path, arm: str, words_out: List[str], words_in: List[str]) -> Dict[str, object]:
    sit = []
    for f in sorted((runs / arm / "exam").glob("*.json")):
        x = json.loads(f.read_text())
        sit.append((int(x["snapshot_last_seq"]), x["ask_all_words"]["Q1"]["per_thing"]))
    sit.sort(key=lambda r: r[0])
    rd = []
    for f in sorted((runs / arm / "readlist").glob("*.json")):
        x = json.loads(f.read_text())
        rd.append((int(x["last_seq"]), {p["word"]: (p["answered"] == p["word"]) for p in x["result"]["predictions"]}))
    rd.sort(key=lambda r: r[0])

    def level(thing: str, w: int) -> float:
        rs = [q for s, q in sit if window_of(s) == w][-K_LAST:]
        return sum(float(q[thing]) for q in rs) / len(rs)

    ra = {t: round(level(t, 1) - level(t, 0), 4) for t in EIGHT}
    rb = {t: round(level(t, 2) - level(t, 1), 4) for t in FIVE}
    lost = [t for t in EIGHT if level(t, 0) >= LOST_BEFORE and level(t, 1) <= LOST_AFTER] + \
           [t for t in FIVE if level(t, 1) >= LOST_BEFORE and level(t, 2) <= LOST_AFTER]
    e0 = [(s, r) for s, r in rd if s < W1][-1]
    en = [(s, r) for s, r in rd if W2 <= s <= CUT][-1]
    rec = {}
    for name, ws in (("out", words_out), ("in", words_in)):
        a = {w for w in ws if e0[1].get(w)}
        b = {w for w in ws if en[1].get(w)}
        rec[name] = {"e0": a, "end": b, "present_e0": sum(1 for w in ws if w in e0[1]), "present_end": sum(1 for w in ws if w in en[1])}
    return {"R-A": ra, "R-B": rb, "R-A mean": round(sum(ra.values()) / len(ra), 4), "R-B mean": round(sum(rb.values()) / len(rb), 4),
            "lost": lost, "rec": rec, "sittings": len(sit), "reads": len(rd), "e0_seq": e0[0], "end_seq": en[0],
            "sit_by_window": [sum(1 for s, _ in sit if window_of(s) == w) for w in (0, 1, 2)]}


def paired(x: Set[str], y: Set[str], universe: List[str]) -> Dict[str, object]:
    b = len(x - y)
    c = len(y - x)
    z = (b - c) / math.sqrt(b + c) if b + c > 0 else 0.0
    return {"b": b, "c": c, "z": round(z, 3), "discordant": b + c, "smallest_passable_gap": round(2 * math.sqrt(b + c), 2), "words": len(universe)}


def paired_mean(xs: List[Set[str]], y: Set[str], universe: List[str]) -> Dict[str, object]:
    d = [sum(1.0 for x in xs if w in x) / len(xs) - (1.0 if w in y else 0.0) for w in universe]
    n = len(d)
    m = sum(d) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in d) / (n - 1)) if n > 1 else 0.0
    z = m / (sd / math.sqrt(n)) if sd > 0 else 0.0
    return {"mean_diff": round(m, 5), "sd": round(sd, 5), "n": n, "z": round(z, 3), "draws": len(xs)}


def raw_all(runs: Path, lists: Path) -> Dict[str, object]:
    wo, wi = _words(lists / "READ-W0-out-list.txt"), _words(lists / "READ-W0-in-list.txt")
    arms = {a: raw_arm(runs, a, wo, wi) for a in ARMS}
    pairs: Dict[str, Dict] = {}
    for x, y in (("P", "S"), ("PR", "S"), ("N", "S"), ("S", "N"), ("P", "N"), ("P", "PR")) + tuple((u, "S") for u in UARMS) + tuple((u, "N") for u in UARMS):
        pairs[f"{x} vs {y}"] = {k: paired(arms[x]["rec"][k]["end"], arms[y]["rec"][k]["end"], wo if k == "out" else wi) for k in ("out", "in")}
    for y in ("S", "N", "P"):
        pairs[f"U-mean vs {y}"] = {"out": paired_mean([arms[u]["rec"]["out"]["end"] for u in UARMS], arms[y]["rec"]["out"]["end"], wo)}
    um = paired_mean([arms[u]["rec"]["out"]["end"] for u in UARMS], arms["P"]["rec"]["out"]["end"], wo)
    pairs["P vs U-mean"] = {"out": {**um, "mean_diff": -um["mean_diff"], "z": -um["z"]}}
    return {"arms": arms, "pairs": pairs, "words_out": len(wo), "words_in": len(wi)}


def u_band(arms: Dict[str, Dict], f) -> Dict[str, float]:
    v = [f(arms[u]) for u in UARMS]
    return {"n": len(v), "min": min(v), "max": max(v), "mean": round(sum(v) / len(v), 4)}


def raw_vs_json(raw: Dict, J: Dict) -> List[str]:
    """Every compared figure; returns the list of disagreements (empty = the reader's JSON equals the arms' own files)."""
    bad: List[str] = []

    def eq(what: str, mine, theirs, tol: float = 1e-9):
        ok = (abs(mine - theirs) <= tol) if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)) else mine == theirs
        if not ok:
            bad.append(f"{what}: recomputed {mine!r} against READING.json {theirs!r}")

    for a in ARMS:
        r, m = raw["arms"][a], J["marks"][a]
        eq(f"{a} sittings", r["sittings"], m["sittings"]); eq(f"{a} readlist sittings", r["reads"], m["readlist_sittings"])
        eq(f"{a} R-A mean", r["R-A mean"], m["R-A"]["mean"]); eq(f"{a} R-B mean", r["R-B mean"], m["R-B"]["mean"])
        for t in EIGHT:
            eq(f"{a} R-A {t}", r["R-A"][t], m["R-A"]["per_thing"][t])
        for t in FIVE:
            eq(f"{a} R-B {t}", r["R-B"][t], m["R-B"]["per_thing"][t])
        eq(f"{a} lost things", sorted(r["lost"]), sorted(m["R-A"]["lost"] + m["R-B"]["lost"])); eq(f"{a} lost_13", len(r["lost"]), m["lost_13"])
        for k, name in (("out", "READ-W0-out"), ("in", "READ-W0-in")):
            eq(f"{a} {name} end-w0", len(r["rec"][k]["e0"]), m[name]["end_w0"]); eq(f"{a} {name} end", len(r["rec"][k]["end"]), m[name]["end"])
            eq(f"{a} {name} present end-w0", r["rec"][k]["present_e0"], m[name]["present_end_w0"]); eq(f"{a} {name} present end", r["rec"][k]["present_end"], m[name]["present_end"])
        eq(f"{a} end-w0 seq", r["e0_seq"], m["READ_end_w0_seq"]); eq(f"{a} end seq", r["end_seq"], m["READ_end_seq"])
    for key, p in raw["pairs"].items():
        jp = J["pairs"].get(key)
        if jp is None:
            bad.append(f"pair {key!r} absent from READING.json")
            continue
        for part, vals in p.items():
            for f, v in vals.items():
                eq(f"pair {key} {part} {f}", v, jp[part][f])
    for k in ("R-A", "R-B"):
        for f, v in u_band(raw["arms"], lambda r, k=k: r[f"{k} mean"]).items():
            eq(f"U band {k} {f}", v, J["U_band"][k][f])
    eq("U band lost_13 max", u_band(raw["arms"], lambda r: len(r["lost"]))["max"], J["U_band"]["lost_13"]["max"])
    eq("U band READ-W0-out end min", u_band(raw["arms"], lambda r: len(r["rec"]["out"]["end"]))["min"], J["U_band"]["READ-W0-out_end"]["min"])
    eq("U band READ-W0-out end max", u_band(raw["arms"], lambda r: len(r["rec"]["out"]["end"]))["max"], J["U_band"]["READ-W0-out_end"]["max"])
    return bad


# ================================================================ LAW
def decide(marks: Dict[str, Dict], pairs: Dict[str, Dict], uband: Dict[str, Dict], identity_ok: bool = True, plant_ok: bool = True,
           each_draw: str = "z2") -> Tuple[str, List[Dict[str, str]]]:
    """PREREG-SLEEP-AB §7 walked clause by clause from the arms' own figures. marks[arm] = {R-A, R-B (means), lost (of 13), out_e0, out_end (counts of the 224)};
    pairs[«X vs Y»]["out"] = {b, c, z}; uband = {R-A: {min, max}, R-B: {min, max}}. each_draw: how «≥ 8 of the 10 draws each beat S» is read —
    «z2» (each draw's own z ≥ 2) or «more» (each draw recognises more of the 224 than S). Returns (verdict head, the steps, each with the law's words)."""
    steps: List[Dict[str, str]] = []

    def step(sid: str, law: str, reading: str, result: str) -> None:
        steps.append({"step": sid, "law": law, "reading": reading, "result": result})

    if not (identity_ok and plant_ok):
        step("0", "Nothing is read until IDENTITY (§5.1) and its planted twin have passed. If either fails, the A/B is VOID.", f"identity {identity_ok}, planted twin {plant_ok}", "VOID")
        return "VOID", steps
    step("0", "Nothing is read until IDENTITY (§5.1) and its planted twin have passed.", "identity passed; the planted twin diverged", "read on")
    S, N, P = marks["S"], marks["N"], marks["P"]
    nn = 224
    z = lambda key: pairs[key]["out"]["z"]
    gradable = S["out_e0"] >= GRADABLE_MIN
    step("1", f"READ-W0-out is GRADABLE only if ≥ {GRADABLE_MIN} of the 224 are recognised at the end-w0 sitting under S.",
         f"S recognised {S['out_e0']} of {nn} at the end-w0 sitting", "GRADABLE" if gradable else f"UNDERPOWERED ({S['out_e0']} < {GRADABLE_MIN})")
    # «cannot tell», form 1 (§5.3): N forgets nothing measurable AND S does not differ from N
    p0 = N["out_e0"] / nn
    two_se = 2 * math.sqrt(max(p0 * (1 - p0), 1e-12) / nn)
    drop = abs(N["out_end"] / nn - p0)
    n_same = drop <= two_se
    n_nothing = N["lost"] <= 1 and n_same
    step("2a", "N forgets nothing measurable (§5.3): N loses at most one of the 13 things AND N's READ-W0-out end share is within 2 binomial SE of its own end-w0 share.",
         f"N lost {N['lost']} of 13; N's share moved {N['out_e0']}/{nn} → {N['out_end']}/{nn}, a change of {drop:.4f} against 2 SE {two_se:.4f}",
         f"N forgets nothing measurable: {n_nothing}")
    s_differs = abs(z("S vs N")) >= 2 or abs(S["lost"] - N["lost"]) > 1
    step("2b", "S does not differ from N.", f"S vs N on READ-W0-out z {z('S vs N')}; lost S {S['lost']}, N {N['lost']}", f"S differs from N: {s_differs}")
    form1 = n_nothing and not s_differs
    inside = []
    for k in ("S", "P", "N"):
        for mk in ("R-A", "R-B"):
            v, b = marks[k][mk], uband[mk]
            inside.append((k, mk, v, b["min"], b["max"], b["min"] <= v <= b["max"]))
    all_inside = all(i[5] for i in inside)
    outside = [f"{k} {mk} {v}" for k, mk, v, lo, hi, ok in inside if not ok]
    step("2c", "READ-W0-out is UNDERPOWERED and the maker readings of S, P and N all lie inside U's ten-draw band.",
         f"S, P, N each on R-A and R-B against U's band (R-A [{uband['R-A']['min']}, {uband['R-A']['max']}], R-B [{uband['R-B']['min']}, {uband['R-B']['max']}]); outside: "
         + (", ".join(outside) if outside else "none"), f"{'UNDERPOWERED' if not gradable else 'gradable'}; all inside: {all_inside}")
    form2 = (not gradable) and all_inside
    if form1 or form2:
        step("2", "«This world cannot tell» is the reading when 2a and 2b both hold, or when 2c holds.", f"2a∧2b {form1}; 2c {form2}", "«this world cannot tell»")
        return "«this world cannot tell»", steps
    step("2", "«This world cannot tell» is the reading when 2a and 2b both hold, or when 2c holds.", f"2a∧2b {form1}; 2c {form2}", "does not apply")

    def u_wins(y: str) -> int:
        n = 0
        for u in UARMS:
            p = pairs[f"{u} vs {y}"]["out"]
            n += (p["z"] >= 2) if each_draw == "z2" else (p["b"] > p["c"])
        return n

    qual: Dict[str, bool] = {}
    zp = z("P vs S")
    p_veto = P["lost"] <= S["lost"] + 1
    qual["P"] = gradable and zp >= 2 and p_veto
    step("3P", "The line CHANGES to P when READ-W0-out is gradable and P recognises more of the 224 than S by z ≥ 2, and P loses no more of the 13 things than S plus one.",
         f"gradable {gradable}; P vs S z {zp}; lost P {P['lost']} ≤ S {S['lost']} + 1: {p_veto}", f"qualifies: {qual['P']}")
    zu = pairs["U-mean vs S"]["out"]["z"]
    mean_lost_u = sum(marks[u]["lost"] for u in UARMS) / len(UARMS)
    u_veto = mean_lost_u <= S["lost"] + 1
    wins = u_wins("S")
    qual["U"] = gradable and zu >= 2 and wins >= 8 and u_veto
    step("3U", "The line CHANGES to U when READ-W0-out is gradable, the ten draws' mean recognises more of the 224 than S by z ≥ 2 and ≥ 8 of the 10 draws each beat S, and U loses no more of the 13 things than S plus one.",
         f"gradable {gradable}; U-mean vs S z {zu}; draws beating S ({'z ≥ 2 each' if each_draw == 'z2' else 'more words each'}) {wins} of 10; U's mean lost {mean_lost_u:.1f} ≤ S {S['lost']} + 1: {u_veto}",
         f"qualifies: {qual['U']}")
    if qual["P"] and qual["U"]:
        take_p = pairs["P vs U-mean"]["out"]["z"] >= 2 and z("P vs PR") >= 2
        step("3PU", "If both qualify, P is taken only if it also beats U's mean by z ≥ 2 and beats PR by z ≥ 2; else U.",
             f"P vs U-mean z {pairs['P vs U-mean']['out']['z']}; P vs PR z {z('P vs PR')}", "P" if take_p else "U")
        return ("CHANGE to P" if take_p else "CHANGE to U"), steps
    if qual["P"]:
        return "CHANGE to P", steps
    if qual["U"]:
        return "CHANGE to U", steps
    p_beats_n = z("P vs N") >= 2
    u_beats_n = gradable and pairs["U-mean vs N"]["out"]["z"] >= 2 and u_wins("N") >= 8
    zn = z("N vs S")
    to_zero = gradable and zn >= 2 and not p_beats_n and not u_beats_n
    step("4", "The line CHANGES to `replay 0` when S recognises fewer of the 224 than N by z ≥ 2 and neither P nor U beats N.",
         f"gradable {gradable}; N vs S z {zn}; P beats N {p_beats_n}; U beats N {u_beats_n}", f"fires: {to_zero}")
    if to_zero:
        return "CHANGE to replay 0", steps
    worse_z = zn >= 2
    worse_lost = S["lost"] > N["lost"] + 1
    keep = not worse_z and not worse_lost
    step("5", "The line is KEPT when no rule clears those bars and S is not worse than N by z ≥ 2 nor by more than one lost thing.",
         f"no rule cleared (3P, 3U, 4); S worse than N by z ≥ 2: {worse_z} (N vs S z {zn}); S lost {S['lost']} against N's {N['lost']}, a difference of {S['lost'] - N['lost']} (more than one: {worse_lost})",
         "KEEP" if keep else "no clause fires")
    return ("KEEP" if keep else "NO CLAUSE FIRES"), steps


def marks_for_decide(raw: Dict) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    marks = {a: {"R-A": r["R-A mean"], "R-B": r["R-B mean"], "lost": len(r["lost"]), "out_e0": len(r["rec"]["out"]["e0"]), "out_end": len(r["rec"]["out"]["end"])}
             for a, r in raw["arms"].items()}
    uband = {k: u_band(raw["arms"], lambda r, k=k: r[f"{k} mean"]) for k in ("R-A", "R-B")}
    return marks, uband


# ================================================================ CONTROLS, read from their own files
def _lines(p: Path) -> List[str]:
    return [l.strip() for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def _sha(p: Path) -> Optional[str]:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def code_same_between(a: str, b: str, paths: Tuple[str, ...] = ("creature", "genome")) -> Optional[bool]:
    """True when `git diff` between two commits is empty over the replay code (None when git cannot say)."""
    import subprocess
    try:
        r = subprocess.run(["git", "diff", "--quiet", a, b, "--", *paths], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return True if r.returncode == 0 else False if r.returncode == 1 else None


def controls_from_files(runs: Path, check_code: bool = True) -> Dict[str, object]:
    """PREREG-SLEEP-AB §5's controls as their own files read them (never the reader's one-line summary)."""
    ab = runs.parent
    s = _lines(runs / "logs" / "S.log")
    ident = [l for l in s if l.startswith("REPLAY identical:")]
    sp = _lines(ab / "ctl" / "splant.log")
    plant = [l for l in sp if l.startswith("DIVERGED at seq 1271")]
    s2 = _lines(ab / "ctl" / "s2000.log")
    ua, ub = ab / "ctl" / "u1-a" / "journal.jsonl", ab / "ctl" / "u1-b" / "journal.jsonl"
    sa, sb = _sha(ua), _sha(ub)
    lh_lines = _lines(ab / "ctl" / "leverh_proof.log")
    lh = json.loads(lh_lines[0]) if lh_lines and lh_lines[0].startswith("{") else {}
    exits = {a: (_lines(runs / "logs" / f"{a}.log")[-1:] or [""])[0] for a in ARMS}
    attempts = {}
    for a in ARMS:
        f = runs / "state" / f"{a}.attempt"
        attempts[a] = f.read_text().strip() if f.exists() else None
    return {
        "identity_ok": bool(ident) and s[-1:] == ["exit 0"], "identity_line": ident[0] if ident else None,
        "plant_ok": bool(plant) and sp[-1:] == ["exit 1"], "plant_line": plant[0] if plant else None,
        "s2000_ok": any(l.startswith("REPLAY identical:") for l in s2) and s2[-1:] == ["exit 0"], "s2000_line": next((l for l in s2 if l.startswith("REPLAY identical:")), None),
        "det_ok": bool(sa) and sa == sb, "det_sha": (sa or "")[:8], "det_bytes": ua.stat().st_size if ua.exists() else None,
        "leverh_ok": bool(lh.get("identical_except_hash")) and lh.get("planted_caught_at", [None])[0] == 1271 and lh.get("null_hashes_in_bare") == lh.get("digests_in_hashed") and bool(lh.get("null_hashes_in_bare")),
        "leverh": lh,
        "arms_exit0": sum(1 for v in exits.values() if v == "exit 0"), "arms": len(ARMS), "attempts": attempts,
        "code_same": code_same_between("bbd1214", "e65b926") if check_code else None,
    }


def block_controls(c: Dict[str, object]) -> str:
    lh = c["leverh"]
    one = lambda xs: sorted(set(xs))
    h = ["| control (PREREG-SLEEP-AB) | where it is read | the reading | holds |", "|---|---|---|---|",
         f"| IDENTITY, §5.1 | `runs2/logs/S.log` | {c['identity_line']}, then `exit 0` (S against the live mind rows, every field, `hash` included) | **{c['identity_ok']}** |",
         f"| its planted twin, §5.1 | `ctl/splant.log` | {c['plant_line']}, then `exit 1` (S′ with `replay 199`, first 2,000 rows) | **{c['plant_ok']}** |",
         f"| the twin's own unplanted run | `ctl/s2000.log` | {c['s2000_line']}, then `exit 0` | **{c['s2000_ok']}** |",
         f"| DETERMINISM, §5.2 | `ctl/u1-a`, `ctl/u1-b` journals | sha256 {c['det_sha']}… for both, {c['det_bytes']} bytes each (U(1) twice, first 6,000 rows) | **{c['det_ok']}** |",
         f"| lever H, §6.3 | `ctl/leverh_proof.log` | rows {lh.get('rows')}; identical except `hash`: {lh.get('identical_except_hash')}; {lh.get('null_hashes_in_bare')} null hashes bare against {lh.get('digests_in_hashed')} digests hashed; "
         f"a planted one-field change caught at seq {lh.get('planted_caught_at', [None])[0]} | **{c['leverh_ok']}** |",
         f"| the arms | `runs2/logs/<ARM>.log`, `runs2/state/<ARM>.attempt` | {c['arms_exit0']} of {c['arms']} arms ended `exit 0`; attempts per arm {one(c['attempts'].values())} (no arm relaunched) | **{c['arms_exit0'] == c['arms']}** |",
         f"| the controls' code is the arms' code | `git diff bbd1214 e65b926 -- creature genome` | empty: {c['code_same']} (the controls ran on bbd1214, the arms on e65b926) | **{c['code_same']}** |"]
    return "\n".join(h)


# ================================================================ GENERATED BLOCKS
def fmt(v) -> str:
    return str(v).replace("-", "−") if isinstance(v, (int, float)) else str(v)


def minus(text: str) -> str:
    """A hyphen before a digit, after a non-word character, is a minus sign: print it as one, like the tables do."""
    return re.sub(r"(?<![\w])-(?=\d)", "−", text)


def block_walk(steps: List[Dict[str, str]]) -> str:
    out = ["| step | the law's words (§7) | the reading | result |", "|---|---|---|---|"]
    for s in steps:
        out.append(f"| {s['step']} | {s['law']} | {minus(s['reading'])} | **{s['result']}** |")
    return "\n".join(out)


def block_arms(raw: Dict, J: Dict) -> str:
    h = ["| arm | R-A (8 things) | R-B (5 arrivals) | lost of 13 | READ-W0-out: end-w0 → end (of 224) | kept at the end of those recognised at end-w0 | READ-W0-in end (of 51) | SER w2 per 1,000 rows | CPU-h |",
         "|---|---|---|---|---|---|---|---|---|"]
    for a in ARMS:
        r, m = raw["arms"][a], J["marks"][a]
        o = r["rec"]["out"]
        h.append(f"| {a} | {fmt(r['R-A mean'])} | {fmt(r['R-B mean'])} | {len(r['lost'])} of 13 | {len(o['e0'])} → {len(o['end'])} | {len(o['e0'] & o['end'])} of {len(o['e0'])} | "
                 f"{len(r['rec']['in']['end'])} of 51 | {fmt(m['SER_w2']['slope_per_1000_rows'])} | {m['cpu_h']:.2f} |")
    ub = {k: u_band(raw["arms"], lambda r, k=k: r[f"{k} mean"]) for k in ("R-A", "R-B")}
    uo0 = u_band(raw["arms"], lambda r: len(r["rec"]["out"]["e0"]))
    uo = u_band(raw["arms"], lambda r: len(r["rec"]["out"]["end"]))
    ul = u_band(raw["arms"], lambda r: len(r["lost"]))
    lost_txt = f"{ul['max']} of 13 in every draw" if ul["min"] == ul["max"] else f"{ul['min']}–{ul['max']} of 13"
    h.append(f"| **U band, 10 draws** | [{fmt(ub['R-A']['min'])}, {fmt(ub['R-A']['max'])}] | [{fmt(ub['R-B']['min'])}, {fmt(ub['R-B']['max'])}] | "
             f"{lost_txt} | {uo0['min']}–{uo0['max']} → {uo['min']}–{uo['max']} | | | | |")
    present = all(raw["arms"][a]["rec"]["out"]["present_e0"] == raw["words_out"] == raw["arms"][a]["rec"]["out"]["present_end"] for a in ARMS)
    graded = all(J["marks"][a]["R-A"]["things_graded"] == 8 and J["marks"][a]["R-B"]["things_graded"] == 5 for a in ARMS)
    h.append("")
    h.append(f"Presence: {len(ARMS)} of {len(ARMS)} arms read; every arm's 224 words present in both READ sittings: {present}; every arm's 13 things graded (8 and 5): {graded}; "
             f"sittings per arm {sorted({raw['arms'][a]['sittings'] for a in ARMS})}, split by window {sorted({tuple(raw['arms'][a]['sit_by_window']) for a in ARMS})}.")
    return "\n".join(h)


def block_pairs(raw: Dict) -> str:
    h = ["| comparison on READ-W0-out at the end (224 words) | b | c | z | smallest passing gap (2·√(b+c)) |", "|---|---|---|---|---|"]
    keys = ["P vs S", "PR vs S", "N vs S", "S vs N", "P vs N", "P vs PR"] + [f"{u} vs S" for u in UARMS]
    for k in keys:
        p = raw["pairs"][k]["out"]
        h.append(f"| {k} | {p['b']} | {p['c']} | {fmt(p['z'])} | {p['smallest_passable_gap']} |")
    for y in ("S", "N", "P"):
        p = raw["pairs"][f"U-mean vs {y}"]["out"]
        h.append(f"| **U-mean vs {y}** (10 draws; mean per-word difference {fmt(p['mean_diff'])}, sd {p['sd']}, n {p['n']}) | | | {fmt(p['z'])} | |")
    pi = raw["pairs"]["S vs N"]["in"]
    h.append("")
    h.append(f"READ-W0-in (the 51 words the law rehearses by construction), S against N: b {pi['b']}, c {pi['c']}, z {fmt(pi['z'])}; printed, deciding nothing (#228).")
    return "\n".join(h)


def block_maker(raw: Dict) -> str:
    h = ["| thing | window pair | S | N | P | PR | U min | U max |", "|---|---|---|---|---|---|---|---|"]
    for t in EIGHT + FIVE:
        k = "R-A" if t in EIGHT else "R-B"
        pair = "w0 → w1" if t in EIGHT else "w1 → w2"
        us = [raw["arms"][u][k][t] for u in UARMS]
        h.append(f"| {t} | {pair} | " + " | ".join(fmt(raw["arms"][a][k][t]) for a in ("S", "N", "P", "PR")) + f" | {fmt(min(us))} | {fmt(max(us))} |")
    lost = {a: raw["arms"][a]["lost"] for a in ("S", "N", "P", "PR")}
    h.append("")
    h.append("Lost (level ≤ 0.2 after ≥ 0.8): " + "; ".join(f"{a}: {', '.join(v) if v else 'none'}" for a, v in lost.items()) + "; U1–U10: none in any draw.")
    return "\n".join(h)


def pilot_and_load(runs: Path, J: Dict) -> Dict[str, object]:
    """What a pilot of the gate would have cost, and the load the arms ran under — from S's timings.jsonl (cpu_ms per tape row) and TICKS.log."""
    cpu_pre = cpu_all = 0.0
    for line in (runs / "S" / "timings.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            cpu_all += float(r.get("cpu_ms") or 0.0)
            if int(r["seq"]) <= 16198:
                cpu_pre += float(r.get("cpu_ms") or 0.0)
    loads = sorted(float(x) for x in re.findall(r"load ([0-9.]+)", (runs / "TICKS.log").read_text(errors="replace")))
    total = sum(m["cpu_h"] for m in J["marks"].values())
    return {"S CPU-h up to the end-w0 sitting (tape rows ≤ 16198)": round(cpu_pre / 3.6e6, 2), "that, as a share of S": round(cpu_pre / cpu_all, 3),
            "CPU-h of all 14 arms": round(total, 2), "that pilot, as a share of the 14 arms": round(cpu_pre / 3.6e6 / total, 4),
            "TICKS.log load readings": len(loads), "load, lowest": loads[0], "load, median": loads[len(loads) // 2], "load, highest": loads[-1]}


def derived(raw: Dict, J: Dict, runs: Optional[Path] = None) -> Dict[str, object]:
    arms = raw["arms"]
    e0 = {a: len(arms[a]["rec"]["out"]["e0"]) for a in ARMS}
    en = {a: len(arms[a]["rec"]["out"]["end"]) for a in ARMS}
    kept = sum(len(arms[a]["rec"]["out"]["e0"] & arms[a]["rec"]["out"]["end"]) for a in ARMS)
    allr = sum(e0.values())
    d = {
        "S end-w0 share": round(e0["S"] / 224, 4),
        "largest end-w0 count of any arm": max(e0.values()), "its arm": max(e0, key=e0.get),
        "smallest end-w0 count of any arm": min(e0.values()), "its arm (smallest)": min(e0, key=e0.get),
        "arms at or above the bar": sum(1 for v in e0.values() if v >= GRADABLE_MIN),
        "largest end count of any arm": max(en.values()),
        "recognised at end-w0, 14 arms pooled": allr, "of which still recognised at the end": kept, "pooled retention": round(kept / allr, 3),
        "U draws that recognise more of the 224 than S": sum(1 for u in UARMS if raw["pairs"][f"{u} vs S"]["out"]["b"] > raw["pairs"][f"{u} vs S"]["out"]["c"]),
        "U draws with z ≥ 2 against S": sum(1 for u in UARMS if raw["pairs"][f"{u} vs S"]["out"]["z"] >= 2),
        "S minus N, R-B": round(arms["S"]["R-B mean"] - arms["N"]["R-B mean"], 4),
        "S R-A below the U band's minimum by": round(u_band(arms, lambda r: r["R-A mean"])["min"] - arms["S"]["R-A mean"], 4),
        "N's share change, end-w0 to end": round(abs(en["N"] - e0["N"]) / 224, 4),
        "cheapest lever-H arm CPU-h": round(min(J["marks"][a]["cpu_h"] for a in ARMS if a != "S"), 2),
        "dearest lever-H arm CPU-h": round(max(J["marks"][a]["cpu_h"] for a in ARMS if a != "S"), 2),
        "S CPU-h": round(J["marks"]["S"]["cpu_h"], 2),
    }
    hi, lo = max(e0.values()) / 224, min(e0.values()) / 224
    d["end-w0 share gap, largest arm to smallest"] = round(hi - lo, 4)
    d["2 binomial SE of that gap"] = round(2 * math.sqrt(hi * (1 - hi) / 224 + lo * (1 - lo) / 224), 4)
    lever = [J["marks"][a]["cpu_h"] for a in ARMS if a != "S"]
    d["lever H's saving, as a share of S's CPU-h"] = round((J["marks"]["S"]["cpu_h"] - sum(lever) / len(lever)) / J["marks"]["S"]["cpu_h"], 3)
    if runs is not None:
        d.update(pilot_and_load(runs, J))
    return d


def block_derived(raw: Dict, J: Dict, runs: Optional[Path] = None) -> str:
    d = derived(raw, J, runs)
    of = {"arms at or above the bar": lambda v: f"{v} of {len(ARMS)}",
          "U draws that recognise more of the 224 than S": lambda v: f"{v} of {len(UARMS)}",
          "U draws with z ≥ 2 against S": lambda v: f"{v} of {len(UARMS)}",
          "of which still recognised at the end": lambda v: f"{v} of {d['recognised at end-w0, 14 arms pooled']}"}
    h = ["| derived figure | value |", "|---|---|"]
    for k, v in d.items():
        h.append(f"| {k} | {of[k](v) if k in of else fmt(v)} |")
    return "\n".join(h)


def blocks(raw: Dict, J: Dict, steps: List[Dict[str, str]], ctl: Optional[Dict[str, object]] = None, runs: Optional[Path] = None) -> Dict[str, str]:
    g = {"walk": block_walk(steps), "arms": block_arms(raw, J), "pairs": block_pairs(raw), "maker": block_maker(raw), "derived": block_derived(raw, J, runs)}
    if ctl is not None:
        g = {"controls": block_controls(ctl), **g}
    return g


# ================================================================ DOC
GEN_RE = re.compile(r"(<!-- GEN:(\w+) BEGIN -->\n)(.*?)(\n<!-- GEN:\2 END -->)", re.S)

_EXEMPT = [re.compile(p) for p in (
    r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{2}-\d{2}\b", r"\b\d{1,2}:\d{2}(?::\d{2})?\b", r"(?<=\s)[+]\d{4}\b",
    r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b", r"§\s*\d+(?:\.\d+)*", r"#\d+(?:\s*\(\d+\))?", r"(?m)^\s*\d+[.)]\s", r"\(\d{1,2}\)",
    r"(?:Sonnet|Opus|Fable)\s+\d+(?:\.\d+)?", r"(?<=\w):\d+(?:–\d+)?",
    r"(?=[\w./@-]*[A-Za-z])[\w./@-]*\d[\w./@-]*",      # an identifier carrying a letter and a digit: U10, w0, sleep-1003, 2026-09-29T183117Z.json
)]
_NUM = re.compile(r"(?<![\w.])([-−]?)(\d[\d,]*(?:\.\d+)?)(?![\w])")
_OF = re.compile(r"(?<![\d.])(\d+) of (?:the )?(\d+)(?!\.?\d)")      # «A of B» between whole numbers only: «0.0069 of the 66.07» is no pair


def numbers_in(text: str, exempt: bool = True) -> List[Tuple[Decimal, bool, str]]:
    """(value, had_minus_sign, token) for every number in the text outside the exempt shapes (dates, times, shas, §, #, identifiers, enumerators)."""
    t = text
    if exempt:
        for rx in _EXEMPT:
            t = rx.sub(" ", t)
    out = []
    for m in _NUM.finditer(t):
        tok = m.group(2).replace(",", "")
        try:
            out.append((Decimal(tok), m.group(1) != "", m.group(1) + m.group(2)))
        except InvalidOperation:
            pass
    return out


def json_numbers(o) -> Iterable[Decimal]:
    if isinstance(o, bool) or o is None:
        return
    if isinstance(o, (int, float)):
        yield Decimal(repr(o))
    elif isinstance(o, str):
        for v, neg, _ in numbers_in(o, exempt=False):
            yield -v if neg else v
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from json_numbers(k)
            yield from json_numbers(v)
    elif isinstance(o, list):
        for v in o:
            yield from json_numbers(v)


def source_numbers(J: Dict, reading_txt: str, law: str, gen: Dict[str, str]) -> Set[Decimal]:
    s: Set[Decimal] = set(json_numbers(J))
    for text in (reading_txt, law, "\n".join(gen.values())):
        for v, neg, _ in numbers_in(text, exempt=False):
            s.add(-v if neg else v)
    return s


def allowed_pairs(J: Dict, reading_txt: str, gen: Dict[str, str]) -> Set[Tuple[int, int]]:
    pairs: Set[Tuple[int, int]] = {(GRADABLE_MIN, 224)}
    for text in ("\n".join(gen.values()), reading_txt):
        pairs |= {(int(a), int(b)) for a, b in _OF.findall(text)}
    for m in J["marks"].values():
        for name in ("READ-W0-out", "READ-W0-in"):
            pairs |= {(m[name]["end_w0"], m[name]["of"]), (m[name]["end"], m[name]["of"])}
        pairs.add((m["lost_13"], 13))
        pairs.add((m["R-A"]["things_graded"], m["R-A"]["things_declared"])); pairs.add((m["R-B"]["things_graded"], m["R-B"]["things_declared"]))
    return pairs


def check_doc(doc: str, gen: Dict[str, str], J: Dict, reading_txt: str, law: str, verdict_head: str) -> List[str]:
    bad: List[str] = []
    found = {m.group(2): m.group(3) for m in GEN_RE.finditer(doc)}
    for name, text in gen.items():
        if name not in found:
            bad.append(f"generated block {name!r} is absent from the doc")
        elif found[name] != text:
            bad.append(f"generated block {name!r} differs from what the script generates now (re-run with --fill)")
    prose = GEN_RE.sub(" ", doc)
    src = source_numbers(J, reading_txt, law, gen)
    absabs = {abs(v) for v in src}
    for i, line in enumerate(prose.splitlines(), 1):
        for v, neg, tok in numbers_in(line):
            ok = ((-v) in src) if (neg and v != 0) else (v in absabs)   # a negative token must be found as a negative; an unsigned one by magnitude
            if not ok:
                bad.append(f"prose: {tok!r} is in no source (line {i} of the prose: …{line.strip()[:90]}…)")
    pairs = allowed_pairs(J, reading_txt, gen)
    for i, line in enumerate(prose.splitlines(), 1):
        for a, b in _OF.findall(line):
            if (int(a), int(b)) not in pairs:
                bad.append(f"prose: «{a} of {b}» is not an allowed pair (line {i} of the prose: …{line.strip()[:90]}…)")
    m = re.search(r"VERDICT:\s*\*{0,2}\s*([A-Za-z«» ]+?)(?=[*\s]*[(.\n—-])", doc)
    if not m or m.group(1).strip().rstrip("*").lower() != verdict_head.lower():
        bad.append(f"the doc's VERDICT line reads {m.group(1) if m else None!r}; the law's walk gives {verdict_head!r}")
    return bad


def fill(doc: str, gen: Dict[str, str]) -> str:
    def rep(m: "re.Match[str]") -> str:
        name = m.group(2)
        return m.group(1) + gen[name] + m.group(4) if name in gen else m.group(0)
    return GEN_RE.sub(rep, doc)


# ================================================================ main
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True)
    ap.add_argument("--runs", default=str(DEFAULT_RUNS))
    ap.add_argument("--lists", default=str(DEFAULT_LISTS))
    ap.add_argument("--law", default=str(DEFAULT_LAW))
    ap.add_argument("--fill", action="store_true", help="rewrite the generated blocks in the doc, then check")
    a = ap.parse_args(argv)
    runs, lists, docp, lawp = Path(a.runs), Path(a.lists), Path(a.doc), Path(a.law)
    J = json.loads((runs / "READING.json").read_text())
    reading_txt = (runs / "READING.txt").read_text()
    law = lawp.read_text()
    rc = 0
    miss = law_constants_ok(law)
    print(f"LAW constants read out of the law: {'all present' if not miss else miss}")
    rc |= bool(miss)
    raw = raw_all(runs, lists)
    bad = raw_vs_json(raw, J)
    print(f"RAW  {len(ARMS)} arms, {sum(r['sittings'] for r in raw['arms'].values())} exam sittings and {sum(r['reads'] for r in raw['arms'].values())} readlist sittings read; "
          f"{len(raw['pairs'])} paired tests recomputed; disagreements with READING.json: {len(bad)}")
    for b in bad[:20]:
        print("  RAW MISMATCH:", b)
    rc |= bool(bad)
    ctl = controls_from_files(runs)
    failed = [k for k in ("identity_ok", "plant_ok", "s2000_ok", "det_ok", "leverh_ok") if not ctl[k]] + (["arms_exit0"] if ctl["arms_exit0"] != ctl["arms"] else []) \
        + (["code_same"] if ctl["code_same"] is not True else [])
    print(f"CTL  controls read from their own files: identity {ctl['identity_ok']}, planted twin {ctl['plant_ok']}, determinism {ctl['det_ok']}, lever H {ctl['leverh_ok']}, "
          f"arms exit 0 {ctl['arms_exit0']} of {ctl['arms']}, controls' code == arms' code {ctl['code_same']}; failing: {failed or 'none'}")
    rc |= bool(failed)
    marks, uband = marks_for_decide(raw)
    verdict, steps = decide(marks, raw["pairs"], uband, identity_ok=bool(ctl["identity_ok"]), plant_ok=bool(ctl["plant_ok"]))
    print(f"LAW  decide() from the arms' own figures: {verdict}; the reader's own line reads {J['verdict'][:40]!r}")
    for s in steps:
        print(f"  [{s['step']}] {s['result']} — {s['reading']}")
    reader_head = J["verdict"].split(" (")[0].strip().upper()
    if verdict.upper() != reader_head:
        print(f"  LAW MISMATCH: decide() says {verdict!r}, the reader says {reader_head!r}")
        rc |= 1
    gen = blocks(raw, J, steps, ctl, runs)
    doc = docp.read_text()
    if a.fill:
        new = fill(doc, gen)
        if new != doc:
            docp.write_text(new)
            print(f"DOC  --fill rewrote the generated blocks of {docp}")
        doc = new
    problems = check_doc(doc, gen, J, reading_txt, law, verdict)
    print(f"DOC  {len(GEN_RE.findall(doc))} generated blocks, {len(numbers_in(GEN_RE.sub(' ', doc)))} prose numbers checked; problems: {len(problems)}")
    for p in problems[:40]:
        print("  DOC PROBLEM:", p)
    rc |= bool(problems)
    print("CHECK", "PASSED" if rc == 0 else "FAILED")
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
