"""results.py — results.json · run-facts.json · VERDICT.md for one seed (B1-PREREG.md §8, §6, §4.1, §4.2;
docs/bench/BENCH-PLAN.md §4.7's partition; SEAT-DECISIONS R26, R27).

edit: Claude (Fable 5.1), 2026-09-24 18:40 +0400 — the seat, alone.

`python -m brain.harness.results --run <run-dir> --tape-dir <tape-dir> [--bars bars.json] [--ceilings ceilings.json]
[--out docs/brain/b1/<seed>/]` under the venv. Reads every arm directory under the run (the runner's R27 record),
grades each with `brain.harness.graders` (pure), reads the twins' records for the bands, and writes:

  results.json  — canonical (sorted keys, NO clock), hashed: {prereg_sha, seed, tape_sha, cache_header_sha,
                  ceilings_sha, bars_line, arms: {<arm>: {controls, marks, partition, cost, size, state_sha_series,
                  births_series}}, pilot, decisions: {selection, d1_i, d1_ii, d1_iii, mlc_vs_d, grows, ma_isolation,
                  interface, predictions}, partition, instrument: {key, shifted_key}}.
  results.sha256 — of results.json's bytes. A re-read reproduces it; a planted one-row change in an
                  answers.jsonl copy changes it. (No test pins this: `tests/brain/harness/test_results.py`, named here
                  since 09-24, never existed — found 2026-09-26 at R40.)
  run-facts.json — every clock, load, RSS and pid (from the arms' own run-facts), never hashed.
  VERDICT.md    — rendered from templates: per family n and the denominator on every line, reach printed where
                  it applies, VOID / NOT GRADABLE / «no road» in words, never blended; the selection and D1's
                  three comparisons computed and printed WITH their inputs.

THE INSTRUMENT (0c): KEY must pass every graded TEST mark (the controls C0a/C0e and the tests U1–U6, KEEPS,
COST) — C0d_CANARY excepted, since KEY answers the canary from the truth by construction (R26) — and
SHIFTED-KEY must NOT pass them all; otherwise every arm's marks are INSTRUMENT-VOID and the verdict says so
first. Bars come from the seat's §12 line as `bars.json` (validated against the ceilings by
`brain.harness.bars`); without one the run is a SMOKE and every mark reads NO_BAR.

edit: Claude (Opus 5.5), 2026-09-26 18:34 +0400 — R40: PREREG §5.5 «a failing control VOIDS the arm, never "fails" it». Until
now a failed control was an ordinary failed mark: the selection read a voided candidate as FAILED, and D1, GROWS, Memory
Attention's comparisons and the interface read the readings of arms §5.5 voids. Now `arm_status` reads every graded
CONTROL mark; a failure VOIDS the arm unless the arm's own construction guarantees it (the EXEMPT tables, each with
its source: KEY's canary (R26), SHIFTED-KEY (built to fail), and the relation controls the shuffled twins' transforms
rewrite (§4, R22, R23)). A VOID arm fails nothing: its would-be failures are kept as `failed_if_read`, its readings stay
on the record, and no decision reads it. A VOID SHUFFLED-RELATION twin supplies no null, so the U3 marks that needed its
band read NOT GRADABLE (TWIN_VOID). RESULTS_VERSION → v2.

edit: Claude (Opus 5.5), 2026-09-27 11:40 +0400 — R44: §4 feeds SHUFFLED-RELATION to A1, A5, E′ and F, and §5 grades U3 as «≥ its bar
AND above SHUFFLED-RELATION's 95 % band». `graders.grade_u3_family` passes on the bar alone when the band is None, and
until now a twin was voided only for a failed control (R40): a twin that left NO record — stopped VOID by cost under R43, or
never run — handed its arm a U3 pass without its null. `missing_relation_twins` now reads that gap for the four arms §4
names: NOT GRADABLE, TWIN_VOID by cost when the stop's marker (`VOID-BY-COST.json`) is on the twin's directory or on the
search it loads (E′ and F run no search: their twins load SHUFFLED-RELATION:D's library, R36), TWIN_MISSING otherwise.
`twin_void` in results.json names every such arm, and VERDICT.md prints them. The arms §4 does not twin keep their U3 on
the bar alone, as before. RESULTS_VERSION → v3.

edit: Claude (Sonnet 5, A1-TEACH builder), 2026-09-27 14:00 +0400 — R46 (docs/brain/b1/SEAT-DECISIONS.md; PREREG §12's
2026-09-27 13:33 line): A1-TEACH joins RELATION_TWINNED (its own SHUFFLED-RELATION:A1-TEACH is the null for its U3, like
A1's). A new DIAGNOSTIC decision `a1_teach` (§_decisions) prints U1a per case (latin-upper, latin-lower) for A1-TEACH, A1
and SHUFFLED-NAME:A1-TEACH, WITH their inputs — `computable: False` names whichever of the three is missing or VOID. It
decides nothing by itself: R46's own question (does the switch explain A1's NAME collapse?) is read by the seat from
`u1a`, never computed here. U1a's own reading is a DICT `{case: share}` (`graders.grade_u1a`), never a float, so the
existing `_reading()` helper (float-or-None) would read None for every arm — `_u1a_reading()` reads the dict directly.
RESULTS_VERSION → v4.

edit: Claude (Opus 5.5), 2026-09-28 02:32 +0400 — R51 (docs/brain/b1/SEAT-DECISIONS.md): D joins RELATION_TWINNED. R36 made
SHUFFLED-RELATION:D D's OWN U3 null too (PREREG line 272: «D's own U3 also reads against its band (stricter, never
looser)»), and R44's list — written from §4's original feed list — omitted D, so a D whose twin search left no record
(B1.0 seed 1's, stopped VOID by cost at 2026-09-28 02:09:57 under R45) read its U3 PASS on the bar alone. D has no
RELATION_TWIN_SOURCE entry: its twin is its own search, whose stop marker sits on SHUFFLED-RELATION_D. Pinned by
tests/brain/harness/test_results_void.py (a scan: every SHUFFLED-RELATION:<base> tools/b1/*.sh launches is twinned
here) and test_tape.py (D through `assemble`). RESULTS_VERSION → v4.1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from brain.harness import graders as G  # noqa: E402
from brain.harness.run import arm_dirname, load_tape, load_truth  # noqa: E402
from brain.protocol import canonical_json  # noqa: E402

RESULTS_VERSION = "b1-results-v4.1"
KEY_EXEMPT = ("C0d_CANARY",)
TWIN_PREFIXES = ("SHUFFLED-NAME:", "SHUFFLED-RELATION:", "FORCED:")

# R40 — a control an arm's own construction guarantees to fail says nothing about the arm: printed, never voids it
CONTROL_EXEMPT: Dict[str, Dict[str, str]] = {
    "KEY": {"C0d_CANARY": "R26: KEY answers the canary from the truth by construction"},
}
EXEMPT_EVERY_CONTROL: Dict[str, str] = {
    "SHIFTED-KEY": "(0c): built to fail the graders; read only by the instrument rule",
}
TWIN_CONTROL_EXEMPT: Dict[str, Dict[str, str]] = {
    "SHUFFLED-RELATION:": {"C0a_CONST": "§4 / R23: every relation FEEDBACK answer is rewritten per cue, CONST's too",
                           "C0a_SAME": "§4 / R23: every relation FEEDBACK answer is rewritten per cue, SAME's too"},
    "SHUFFLED-NAME:": {"C0a_CONST": "§4 / R22: every name the tape teaches is mapped, CONST's answer `a` too"},
}


def arm_status(name: str, marks: Mapping[str, Any]) -> Dict[str, Any]:
    """§5.5: VOID iff a graded CONTROL mark failed that the arm's construction does not guarantee to fail."""
    by: List[str] = []
    exempt: Dict[str, str] = {}
    for k, m in marks.items():
        if m.get("class") != "CONTROL" or not m.get("graded") or m.get("pass") is not False:
            continue
        why = EXEMPT_EVERY_CONTROL.get(name) or CONTROL_EXEMPT.get(name, {}).get(k)
        if why is None:
            why = next((t[k] for pre, t in TWIN_CONTROL_EXEMPT.items() if name.startswith(pre) and k in t), None)
        if why:
            exempt[k] = why
        else:
            by.append(k)
    return {"void": bool(by), "by": sorted(by), "exempt": exempt}


def read_partition(name: str, marks: Mapping[str, Any]) -> Dict[str, Any]:
    """The graders' partition, read under §5.5: a VOID arm fails nothing (its would-be failures kept as
    `failed_if_read`); an exempt control is not a failure."""
    p = G.partition(marks)
    s = arm_status(name, marks)
    p["failed"] = [k for k in p["failed"] if k not in s["exempt"]]
    p.update({"void": s["void"], "void_by": s["by"], "exempt": s["exempt"]})
    if s["void"]:
        p["failed_if_read"], p["failed"] = p["failed"], []
    return p


def without_void_twin(marks: Mapping[str, Any], twin_by: Sequence[str], reason_code: str = "TWIN_VOID") -> Dict[str, Any]:
    """A VOID SHUFFLED-RELATION twin supplies no null: every graded U3 mark (which needs its band) reads NOT GRADABLE.
    R44: a twin that left no record reads the same, under its own reason (TWIN_MISSING, or TWIN_VOID by cost)."""
    out = dict(marks)
    for k, m in marks.items():
        if k.startswith("U3_") and m.get("graded"):
            out[k] = G._mark(m["mark"], reading=m["reading"], graded=False, passed=None, bar=m.get("bar"),
                             ceiling=m.get("ceiling"), null=m.get("null"), control=m.get("control"), reason_code=reason_code,
                             fields=dict(m.get("fields") or {}, twin_void_by=list(twin_by)), sources=m.get("sources"),
                             klass=m.get("class", ""))
    return out


# R44 — the arms §4 feeds SHUFFLED-RELATION to (the composition null for U3). E′ and F run no search: their twins load
# SHUFFLED-RELATION:D's library (R36), so a stop of that search is a stop of their twins.
# R46 — A1-TEACH is a plain network like A1 (not a hybrid): it runs its OWN SHUFFLED-RELATION:A1-TEACH search, so it
# carries no entry in RELATION_TWIN_SOURCE below, exactly like A1.
# R51 — D: its own U3 reads against its own SHUFFLED-RELATION:D search (R36), so D is twinned too, with no source entry.
RELATION_TWINNED = ("A1", "A1-TEACH", "A5", "D", "E′", "F")
RELATION_TWIN_SOURCE = {"E′": "SHUFFLED-RELATION:D", "F": "SHUFFLED-RELATION:D"}
VOID_BY_COST = "VOID-BY-COST.json"


def missing_relation_twins(run_dir: Path, names: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    """R44: an arm §4 twins with SHUFFLED-RELATION whose twin left no graded record has no null — {base: {reason_code, by}}.
    By cost (TWIN_VOID) when the stop's marker is on the twin's directory or on the search it loads, with the marker's
    `why`; TWIN_MISSING otherwise. A twin record present is no gap here (its band, or R40's control VOID, as before)."""
    present = set(names)
    out: Dict[str, Dict[str, Any]] = {}
    for base in RELATION_TWINNED:
        twin = f"SHUFFLED-RELATION:{base}"
        if base not in present or twin in present:
            continue
        stop = None
        for w in [twin] + ([RELATION_TWIN_SOURCE[base]] if base in RELATION_TWIN_SOURCE else []):
            f = Path(run_dir) / arm_dirname(w) / VOID_BY_COST
            if f.exists():
                stop = (w, str(json.loads(f.read_text()).get("why", "")))
                break
        out[base] = ({"reason_code": "TWIN_VOID", "by": [f"VOID_BY_COST: {stop[0]} — {stop[1]}"]} if stop else
                     {"reason_code": "TWIN_MISSING", "by": [f"MISSING: no {twin} record"]})
    return out


class ResultsError(Exception):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> Optional[str]:
    return sha256_bytes(Path(p).read_bytes()) if Path(p).exists() else None


def _series(path: Path, key: str) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for l in path.read_text().splitlines():
        if l.strip():
            r = json.loads(l)
            out.append({"where": r.get("where"), "seq": r.get("seq"), key: r.get(key)})
    return out


def shuffled_relation_bands(twin_marks: Mapping[str, Any]) -> Dict[str, float]:
    """The SHUFFLED-RELATION twin's 95 % band per family: its share + the 95 % binomial half-width on its n."""
    bands: Dict[str, float] = {}
    for name, m in twin_marks.items():
        if not name.startswith("U3_") or m.get("reading") is None:
            continue
        fam = name[3:].split("@")[0]
        n = m["fields"].get("n") or 0
        share = float(m["reading"])
        bands[fam] = min(1.0, share + G.half_width_95(max(share, 1e-9), n)) if n else share
    return bands


def assemble(run_dir: Path, tape_dir: Path, bars: Optional[Mapping[str, Any]] = None, ceilings: Optional[Mapping[str, Any]] = None,
             prereg_path: Optional[Path] = None, bars_line: Optional[str] = None, margins: Optional[Mapping[str, float]] = None) -> Dict[str, Any]:
    run_dir, tape_dir = Path(run_dir), Path(tape_dir)
    inputs = json.loads((run_dir / "inputs.json").read_text()) if (run_dir / "inputs.json").exists() else {}
    seed = int(inputs.get("seed", 0))
    rows, tape_sha = load_tape(tape_dir)
    truth = load_truth(tape_dir)["asks"]
    counts = json.loads((tape_dir / "counts.json").read_text()) if (tape_dir / "counts.json").exists() else {}
    cache_header = tape_dir / "cache" / "header.json"
    if not cache_header.exists() and inputs.get("cache_dir"):
        cache_header = Path(inputs["cache_dir"]) / "header.json"
    margins = dict(margins or {})

    arm_dirs = sorted(p for p in run_dir.iterdir() if p.is_dir() and (p / "summary.json").exists())
    names = [p.name.replace("_", ":", 1) if p.name.startswith(("SHUFFLED-NAME_", "SHUFFLED-RELATION_", "FORCED_")) else p.name for p in arm_dirs]
    records = {n: G.load_record(p) for n, p in zip(names, arm_dirs)}

    # 1. the twins first: SHUFFLED-RELATION bands per BASE arm
    bands_by_base: Dict[str, Dict[str, float]] = {}
    twin_void: Dict[str, List[str]] = {}
    twin_reason: Dict[str, str] = {}
    for n, rec in records.items():
        if n.startswith("SHUFFLED-RELATION:"):
            base = n.split(":", 1)[1]
            marks = G.grade_arm(rec, truth, rows, bars=None, ceilings=ceilings, tape_counts=counts, seed=seed)
            st = arm_status(n, marks)
            if st["void"]:                     # R40: a VOID twin supplies no null
                twin_void[base], twin_reason[base] = st["by"], "TWIN_VOID"
                continue
            bands_by_base[base] = shuffled_relation_bands(marks)
    for base, gap in missing_relation_twins(run_dir, names).items():   # R44: a twin with no record supplies none either
        twin_void[base], twin_reason[base] = gap["by"], gap["reason_code"]

    # 2. every arm's marks
    arms: Dict[str, Any] = {}
    for n, rec in records.items():
        base = n.split(":", 1)[1] if any(n.startswith(p) for p in TWIN_PREFIXES) else n
        marks = G.grade_arm(rec, truth, rows, bars=bars, ceilings=ceilings, twin_bands=bands_by_base.get(base), tape_counts=counts, seed=seed)
        if base in twin_void and not n.startswith("SHUFFLED-RELATION:"):
            marks = without_void_twin(marks, twin_void[base], reason_code=twin_reason[base])
        part = read_partition(n, marks)
        summ = rec["summary"]
        d = Path(rec["dir"])
        inputs_sha = {f: sha256_file(d / f) for f in ("answers.jsonl", "why.jsonl", "rules.jsonl", "sittings.json", "feedback.jsonl")}
        arms[n] = {"marks": marks, "partition": part, "inputs_sha256": inputs_sha,
                   "cost": summ.get("cost"), "size": summ.get("size"), "final_state_sha": summ.get("final_state_sha"),
                   "sittings": summ.get("sittings"), "has_why": summ.get("has_why"), "has_rule": summ.get("has_rule"), "twin": summ.get("twin"),
                   "forced": summ.get("forced"), "state_sha_series": _series(Path(rec["dir"]) / "state_sha.jsonl", "state_sha"),
                   "births_series": _series(Path(rec["dir"]) / "cost.jsonl", "arm_events"), "missing": rec.get("missing")}

    # 3. the instrument (0c)
    def test_marks(m: Mapping[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in m.items() if v.get("graded") and k not in KEY_EXEMPT}

    instrument: Dict[str, Any] = {"key_present": "KEY" in arms, "shifted_key_present": "SHIFTED-KEY" in arms}
    if "KEY" in arms:
        km = test_marks(arms["KEY"]["marks"])
        instrument["key_failed"] = [k for k, v in km.items() if not v.get("pass")]
        instrument["key_graded_marks"] = len(km)
    if "SHIFTED-KEY" in arms:
        sm = test_marks(arms["SHIFTED-KEY"]["marks"])
        instrument["shifted_key_failed"] = [k for k, v in sm.items() if not v.get("pass")]
    instrument["void"] = (not instrument["key_present"]) or bool(instrument.get("key_failed")) or ("SHIFTED-KEY" in arms and not instrument.get("shifted_key_failed"))
    instrument["why"] = ("KEY missing" if not instrument["key_present"] else
                         (f"KEY failed {instrument['key_failed']}" if instrument.get("key_failed") else
                          ("SHIFTED-KEY passed every graded mark — the graders are passable by a shifted answer stream" if ("SHIFTED-KEY" in arms and not instrument.get("shifted_key_failed")) else "")))

    # 4. the decisions (§6, §4.1, §4.2) — computed over the arms present; a missing arm is NAMED, never assumed
    decisions = _decisions(arms, margins)

    partition_all = {n: a["partition"] for n, a in arms.items()}
    results = {
        "version": RESULTS_VERSION, "seed": seed, "tape_sha": tape_sha, "prereg_sha": (sha256_file(prereg_path) if prereg_path else None),
        "cache_header_sha": sha256_file(cache_header), "ceilings_sha": (sha256_bytes(canonical_json(ceilings).encode()) if ceilings else None),
        "bars_line": bars_line, "bars": (dict(bars) if bars else None), "margins": margins, "smoke": not bool(bars) or not bool(counts.get("params_are_prereg", False)),
        "tape_params_are_prereg": counts.get("params_are_prereg"), "arms": arms, "instrument": instrument, "decisions": decisions,
        "partition": partition_all, "twin_bands": bands_by_base, "twin_void": twin_void, "pilot": {"a6_partner": None, "inputs": None},
    }
    return results


def _reading(arms: Mapping[str, Any], arm: str, mark: str) -> Optional[float]:
    m = (arms.get(arm) or {}).get("marks", {}).get(mark)
    r = m.get("reading") if m else None
    return float(r) if isinstance(r, (int, float)) else None


# R46 — the three arms the a1_teach diagnostic reads (docs/brain/b1/SEAT-DECISIONS.md; PREREG §12's 2026-09-27 13:33 line).
A1_TEACH_DIAGNOSTIC_ARMS = ("A1-TEACH", "A1", "SHUFFLED-NAME:A1-TEACH")


def _u1a_reading(arms: Mapping[str, Any], arm: str) -> Optional[Dict[str, float]]:
    """U1a's own reading is a DICT `{case: share}` (`graders.grade_u1a`), never a float — `_reading()` above reads
    None for it (`isinstance({}, (int, float))` is False), which would silently read every arm's U1a as "no
    reading" (#162's class: an instrument that reads its own None as a negative). Read the dict directly instead."""
    m = (arms.get(arm) or {}).get("marks", {}).get("U1a_NAME@T_L")
    r = m.get("reading") if m else None
    return dict(r) if isinstance(r, dict) else None


def _a1_teach_diagnostic(arms: Mapping[str, Any], void: Mapping[str, Any]) -> Dict[str, Any]:
    """R46: a DIAGNOSTIC of A1's NAME collapse, never a selection candidate (§6's selection never reads this) — U1a
    per case (latin-upper, latin-lower) for A1-TEACH, A1 and SHUFFLED-NAME:A1-TEACH, printed WITH their inputs.
    `computable: False` names whichever of the three arms is missing or VOID, rather than silently reading the
    others alone. It decides nothing by itself: R46's own question (does the switch explain the collapse — does
    A1-TEACH pass U1a, above its SHUFFLED-NAME twin, at both seeds where A1 fails?) is read by the seat from `u1a`."""
    missing = [a for a in A1_TEACH_DIAGNOSTIC_ARMS if a not in arms]
    voided = {a: void[a] for a in A1_TEACH_DIAGNOSTIC_ARMS if a in void}
    u1a = {a: _u1a_reading(arms, a) for a in A1_TEACH_DIAGNOSTIC_ARMS if a in arms}
    out: Dict[str, Any] = {"computable": not missing and not voided, "u1a": u1a}
    if missing:
        out["missing"] = missing
    if voided:
        out["void"] = voided
    return out


def _decisions(arms: Mapping[str, Any], margins: Mapping[str, float]) -> Dict[str, Any]:
    fams = list(G.U3_LETTER_FAMILIES)
    void = {n: s["by"] for n, s in ((n, arm_status(n, a.get("marks") or {})) for n, a in arms.items()) if s["void"]}   # R40
    a1_teach = _a1_teach_diagnostic(arms, void)   # R46 — a diagnostic; decides nothing by itself

    def u3(arm: str) -> Dict[str, Optional[float]]:
        return {f: _reading(arms, arm, f"U3_{f}@T_L") for f in fams}

    def diff(a: str, b: str, which: Sequence[str]) -> Dict[str, Any]:
        if a not in arms or b not in arms:
            return {"computable": False, "missing": [x for x in (a, b) if x not in arms]}
        if a in void or b in void:
            return {"computable": False, "void": {x: void[x] for x in (a, b) if x in void}}
        ua, ub = u3(a), u3(b)
        d = {f: ((ua[f] - ub[f]) if (ua[f] is not None and ub[f] is not None) else None) for f in which}
        return {"computable": True, "inputs": {a: {f: ua[f] for f in which}, b: {f: ub[f] for f in which}}, "diff_pp": {f: (None if v is None else round(100 * v, 1)) for f, v in d.items()}}

    def all_pass(arm: str) -> Any:
        a = arms.get(arm)
        if not a:
            return None
        if arm in void:
            return "VOID"
        return not a["partition"]["failed"]

    m_d1 = margins.get("d1_pp")
    m_grows = margins.get("grows_pp")
    m_ma = margins.get("ma_pp")
    m_if = margins.get("interface_pp")
    d1_i = diff("F", "A5", ["TWO_AFTER", "CHAIN"])
    if d1_i.get("computable") and m_d1 is not None:
        vals = [v for v in d1_i["diff_pp"].values() if v is not None]
        d1_i["verdict_this_seed"] = ("STAYS" if vals and all(v >= m_d1 for v in vals) else ("DROPPED" if vals and all(v <= -m_d1 for v in vals) else "OPEN"))
    d1_ii: Dict[str, Any] = {"computable": "E′" in arms and "F" in arms and "E′" not in void and "F" not in void}
    if any(x in void for x in ("E′", "F")):
        d1_ii["void"] = {x: void[x] for x in ("E′", "F") if x in void}
    if d1_ii["computable"]:
        fe, ff = arms["E′"]["marks"], arms["F"]["marks"]
        worse = [k for k, v in fe.items() if v.get("graded") and ff.get(k, {}).get("graded") and isinstance(v.get("reading"), (int, float))
                 and isinstance(ff[k].get("reading"), (int, float)) and v["reading"] < ff[k]["reading"]]
        d1_ii.update({"e_prime_below_f_on": worse, "verdict_this_seed": ("NETWORK DROPPED" if not worse else "network stays")})
    d1_iii = diff("D", "A1", fams)
    grows = diff("A1", "A1-FIXED", fams)
    if grows.get("computable") and m_grows is not None:
        vals = [v for v in grows["diff_pp"].values() if v is not None]
        grows["verdict_this_seed"] = "GROWS" if vals and all(v >= m_grows for v in vals) else "growth bought nothing at letters"
    ma = {"claim": diff("A1-MA", "A1", fams), "isolation": diff("A1-MA", "A1-ATT", fams)}
    if ma["isolation"].get("computable") and m_ma is not None:
        vals = [v for v in ma["isolation"]["diff_pp"].values() if v is not None]
        ma["isolation"]["verdict_this_seed"] = "memory value carries" if vals and all(v >= m_ma for v in vals) else "attention's, not the memory's"
    interface: Dict[str, Any] = {"arms_present": [a for a in ("A5", "A5-IF1", "A5-IF2", "A5-IF3", "A5-IF4") if a in arms and a not in void],
                                 "void": {a: void[a] for a in ("A5", "A5-IF1", "A5-IF2", "A5-IF3", "A5-IF4") if a in void}}
    if "A5" in interface["arms_present"] and len(interface["arms_present"]) > 1:
        scores = {a: [v for v in (_reading(arms, a, f"U3_{f}@T_L") for f in G.DISCRIMINATING_FAMILIES) if v is not None] for a in interface["arms_present"]}
        means = {a: (sum(v) / len(v) if v else None) for a, v in scores.items()}
        interface["mean_discriminating_u3"] = means
        if m_if is not None and means.get("A5") is not None:
            best = max((a for a in means if a != "A5" and means[a] is not None), key=lambda a: means[a], default=None)
            interface["verdict_this_seed"] = (best if best and (means[best] - means["A5"]) * 100 >= m_if else "F keeps IF-0")
    selection = {"candidates": {a: all_pass(a) for a in ("A5", "A6", "E′", "F") if a in arms}, "rule": "every bar including all six tests at BOTH seeds (§6)",
                 "void": {a: void[a] for a in ("A5", "A6", "E′", "F") if a in void},
                 "this_seed_only": True}
    return {"selection": selection, "d1_i": d1_i, "d1_ii": d1_ii, "d1_iii": d1_iii, "grows": grows, "ma": ma, "interface": interface,
            "mlc_vs_d": {a: ({"void": void[a]} if a in void else _examples(arms, a)) for a in ("A1-MLC", "D", "A1")},
            "void": void, "a1_teach": a1_teach,
            "predictions": "DEBATE rounds 1–2 (B1-PREREG.md §6) — read against the arms above by the seat, never by this code"}


def _examples(arms: Mapping[str, Any], arm: str) -> Any:
    m = (arms.get(arm) or {}).get("marks", {}).get("EXAMPLES_TO_BAR_TWO_AFTER")
    return {"reading": m.get("reading"), "ladder": m.get("fields", {}).get("ladder")} if m else None


# ================================================================================================ VERDICT.md
def _fmt(x: Any) -> str:
    if isinstance(x, float):
        return f"{x:.3f}"
    if isinstance(x, dict):
        return ", ".join(f"{k} {_fmt(v)}" for k, v in x.items())
    return str(x)


def render_verdict(results: Mapping[str, Any]) -> str:
    L: List[str] = []
    L.append(f"# B1 VERDICT — seed {results['seed']} ({'SMOKE — no bars declared' if results.get('smoke') else 'graded'})")
    L.append("")
    L.append(f"tape sha `{results['tape_sha'][:16]}…` · results {RESULTS_VERSION} · bars: {results.get('bars_line') or '— none (every mark NO_BAR)'}")
    inst = results["instrument"]
    L.append("")
    L.append(f"## The instrument (0c) — {'VOID: ' + inst.get('why', '') if inst.get('void') else 'sound'}")
    L.append(f"- KEY: {'present' if inst.get('key_present') else 'MISSING'}; graded marks {inst.get('key_graded_marks')}; failed {inst.get('key_failed')}")
    L.append(f"- SHIFTED-KEY: {'present' if inst.get('shifted_key_present') else 'missing'}; failed {len(inst.get('shifted_key_failed') or [])} marks")
    tv = results.get("twin_void") or {}
    if tv:                                     # R44: a null that is gone is named, never silent
        L.append("")
        L.append("## The composition nulls (SHUFFLED-RELATION, §4) — VOID or missing")
        for b, why in tv.items():
            L.append(f"- {b}: {why} — its U3 marks read NOT GRADABLE (R40, R44), never a pass on the bar alone")
    for arm, a in results["arms"].items():
        L.append("")
        L.append(f"## {arm}")
        p = a["partition"]
        if p.get("void"):
            L.append(f"**VOID** — failed controls {p['void_by']} (§5.5: a failing control VOIDS the arm, never «fails» it; its marks "
                     f"are printed for the record and read by no decision) · would-be failures, read by nothing: {p.get('failed_if_read')}")
            L.append(f"not gradable {[n for n, _ in p['not_gradable']] or 'none'} · missing-graded {p['missing_graded'] or 'none'}")
        else:
            L.append(f"failed {p['failed'] or 'none'} · not gradable {[n for n, _ in p['not_gradable']] or 'none'} · missing-graded {p['missing_graded'] or 'none'}")
        if p.get("exempt"):
            L.append(f"controls failed by construction, never voiding (R40): {p['exempt']}")
        if a.get("cost"):
            L.append(f"cost: {_fmt(a['cost'].get('ms_per_event'))} ms per event over {a['cost'].get('arm_events')} events · size {a.get('size')}")
        L.append("")
        L.append("| mark | graded | pass | reading | bar | ceiling | null | n / k | note |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for name, m in a["marks"].items():
            f = m.get("fields") or {}
            nk = ""
            if "n" in f:
                nk = f"{f.get('n')} / {f.get('k', f.get('known', f.get('refused', '')))}"
            note = m.get("reason_code") or ""
            if name.startswith("U3_") and (f.get("breakdown_by_class")):
                note += " · " + "; ".join(f"{c}: {v['right']}/{v['renderings']}" for c, v in f["breakdown_by_class"].items())
            if m["mark"].startswith("U3_") and m["mark"].split("_", 1)[1].split("@")[0] in G.REACH_FAMILIES:
                note += " · REACH (read beside RING-READ)"
            L.append(f"| {name} | {'yes' if m['graded'] else 'no'} | {'PASS' if m['pass'] else ('FAIL' if m['pass'] is False else '—')} | {_fmt(m['reading'])} | {_fmt(m['bar'])} | {_fmt(m['ceiling'])} | {_fmt(m['null'])} | {nk} | {note} |")
    d = results["decisions"]
    L.append("")
    L.append("## The decisions (§6, §4.1, §4.2) — this seed's inputs; the rule needs BOTH seeds")
    L.append(f"- selection candidates (all bars this seed; VOID = a failed control, §5.5): {d['selection']['candidates']}"
             + (f" · void by {d['selection']['void']}" if d["selection"].get("void") else ""))

    def why_not(v: Mapping[str, Any]) -> str:
        return f"VOID {v['void']}" if v.get("void") else f"missing {v.get('missing')}"

    for key, label in (("d1_i", "D1 (i) F − A5 on TWO_AFTER / CHAIN"), ("d1_iii", "D1 (iii) D − A1 (diagnostic)"), ("grows", "GROWS A1 − A1-FIXED")):
        v = d[key]
        L.append(f"- {label}: " + (f"diff pp {v['diff_pp']} · inputs {v['inputs']} · {v.get('verdict_this_seed', '')}" if v.get("computable") else f"not computable — {why_not(v)}"))
    v = d["d1_ii"]
    L.append(f"- D1 (ii) E′ vs F: " + (f"E′ below F on {v['e_prime_below_f_on']} → {v['verdict_this_seed']}" if v.get("computable")
                                      else ("not computable — " + (f"VOID {v['void']}" if v.get("void") else "E′ or F missing"))))
    ma_c, ma_i = d["ma"]["claim"], d["ma"]["isolation"]
    L.append(f"- Memory Attention: claim {ma_c['diff_pp'] if ma_c.get('computable') else why_not(ma_c)} · isolation "
             f"{ma_i['diff_pp'] if ma_i.get('computable') else why_not(ma_i)} {ma_i.get('verdict_this_seed', '')}")
    L.append(f"- interface: {d['interface']}")
    L.append(f"- examples-to-bar (TWO_AFTER): {d['mlc_vs_d']}")
    v = d.get("a1_teach") or {}
    if v.get("computable"):
        L.append(f"- A1-TEACH (R46 — a diagnostic; decides nothing by itself): U1a {v.get('u1a')}")
    else:
        bits = []
        if v.get("missing"):
            bits.append(f"missing {v['missing']}")
        if v.get("void"):
            bits.append(f"void {v['void']}")
        L.append(f"- A1-TEACH (R46 — a diagnostic; decides nothing by itself): NOT COMPUTABLE — " + " · ".join(bits) + f" · U1a so far {v.get('u1a')}")
    L.append("")
    L.append("## Reading rules")
    L.append("- A mark NOT GRADED is never counted as failed; «no road» names a capability the arm does not have; INSTRUMENT-VOID (0c) names the "
             "instrument, never the arm; an arm VOID names a §5.5 control that arm failed — never «failed» (R40).")
    L.append("- REACH families are printed beside RING-READ (reach given the name); the U3 verdict rests on the discriminating families TWO_AFTER · OTHER_CASE · CHAIN.")
    return "\n".join(L) + "\n"


# ================================================================================================ main
def write_all(results: Mapping[str, Any], out_dir: Path, run_dir: Path) -> Dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    blob = canonical_json(results).encode("utf-8")
    (out_dir / "results.json").write_bytes(blob + b"\n")
    sha = sha256_bytes(blob)
    (out_dir / "results.sha256").write_text(sha + "\n")
    facts = {}
    for p in sorted(Path(run_dir).iterdir()):
        if (p / "run-facts.json").exists():
            facts[p.name] = json.loads((p / "run-facts.json").read_text())
    (out_dir / "run-facts.json").write_text(json.dumps(facts, sort_keys=True, indent=2) + "\n")
    (out_dir / "VERDICT.md").write_text(render_verdict(results))
    return {"results_sha256": sha, "out_dir": str(out_dir)}


def u3_bar_shares(bars_doc: Mapping[str, Any]) -> Dict[str, float]:
    """edit: Claude (Opus 5.5), 2026-09-26 16:57 +0400 — bars.json stores each U3 bar as a COUNT k of n NAME items (what
    `grade_u3_family` compares: k >= bar), but `bars.validate_bars_line` compares a SHARE with the family's organ ceiling.
    The first graded read (seed 20261001) raised «AFTER: declared bar 8 is ABOVE its organ ceiling 0.886» — a count against
    a share (#162). The shares are k / n with n from bars.json's own `detail`, the arithmetic `bars_line.main` validated with."""
    bars = (bars_doc or {}).get("bars") or {}
    detail = (bars_doc or {}).get("detail") or {}
    out: Dict[str, float] = {}
    for fam, k in (bars.get("U3") or {}).items():
        n = (detail.get(fam) or {}).get("n")
        if isinstance(k, (int, float)) and n:
            out[fam] = k / n
    return out


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--tape-dir", required=True)
    p.add_argument("--bars", default=None, help="bars.json from the seat's §12 line")
    p.add_argument("--ceilings", default=None)
    p.add_argument("--out", default=None, help="default: <run>/results/")
    p.add_argument("--prereg", default=str(REPO_ROOT / "docs" / "brain" / "B1-PREREG.md"))
    ns = p.parse_args(argv)
    bars_doc = json.loads(Path(ns.bars).read_text()) if ns.bars else None
    bars = (bars_doc or {}).get("bars") if bars_doc else None
    margins = (bars_doc or {}).get("margins") if bars_doc else None
    ceilings = json.loads(Path(ns.ceilings).read_text()) if ns.ceilings else None
    if bars and ceilings:
        from brain.harness import bars as B
        B.validate_bars_line(ceilings.get("families", {}), u3_bar_shares(bars_doc))
    res = assemble(Path(ns.run), Path(ns.tape_dir), bars=bars, ceilings=ceilings, prereg_path=Path(ns.prereg) if Path(ns.prereg).exists() else None,
                   bars_line=(bars_doc or {}).get("line"), margins=margins)
    out = Path(ns.out) if ns.out else Path(ns.run) / "results"
    w = write_all(res, out, Path(ns.run))
    print(f"[results] seed {res['seed']} · arms {list(res['arms'])} · instrument {'VOID' if res['instrument']['void'] else 'sound'} · results.json sha {w['results_sha256'][:16]}… → {out}")
    for arm, a in res["arms"].items():
        p = a["partition"]
        print(f"[results]   {arm}: " + (f"VOID by {p['void_by']}" if p.get("void") else f"failed {p['failed']}")
              + f" · not gradable {len(p['not_gradable'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
