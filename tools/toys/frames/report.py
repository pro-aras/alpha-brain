"""report.py — TOY C's report: the text every figure of docs/research/toys/RESULT-TOY-FRAMES.md is quoted from, rendered from the records and from nothing else
(docs/research/toys/PREREG-TOY-FRAMES.md §3-§4, AMENDMENT-1 §1, AMENDMENT-2 §2).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:47 +0400 — new module (stage 6b), written to the RED tests/tools/test_toys_frames_report.py (stage 6a, ImportError) and to the records the runner writes.
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:51 +0400 — stage 6b, red-first against tests/tools/test_toys_frames_report_figures.py (12 of 26 RED): counts print as integers, a null that could not be dealt prints its error, the
# provenance gains four planted-and-caught checks (grade, eye reading, overlaps, SCENE rows against the five condition records) and a signed-text flag per source.

  PYTHONPATH=. python3 -m tools.toys.frames.report [--root DIR] [--out FILE]      (defaults: the runner's runs directory; docs/research/toys/RESULT-TOY-FRAMES-REPORT.txt)

`load` reads the five condition records, RESULTS.json and, if present, GATES.json; `render` turns them into text that is BYTE-DETERMINISTIC (no clock, no path, nothing random): the same records give
the same bytes. Every number printed is read from a record or is a plain aggregate of numbers read from a record (a mean, a count, a boolean of the predictions). Two instrument checks print beside the
provenance: that each thing RESULTS.json carries and the report prints from it — the grade in both modes, the eye reading (against its own per-frame table), the overlaps, the SCENE rows and recalls — equals what the
five condition records give when recomputed (a changed record reads NO), and that every record carries the same signed texts.
THE PREDICTIONS P-C1 .. P-C6 are read MECHANICALLY with their definitions printed beside them; the definitions were fixed in this file BEFORE the unit ran. A reading, never a bar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from . import run as RN
from . import scene as SC
from . import streams as ST
from . import verdicts as VD

CONDITIONS: Tuple[str, ...] = tuple(name for name, *_ in RN.CONDITIONS)
RULES: Tuple[str, ...] = VD.RULES
DEFAULT_OUT = ST.REPO / "docs" / "research" / "toys" / "RESULT-TOY-FRAMES-REPORT.txt"
# the readings' own constants (fixed before the unit ran; a reading, never a bar)
P_C3_FRACTION = 0.10                      # «every G ≪ G_max» is read as G <= 0.10 x G_max on plain SCENE
P_C4_MIN_SAYS = 5                         # a said frame is GROUNDED if the eye confirmed >= 50 % of >= 5 says, a FUNCTION pair if >= 5 says and 0 confirmed
P_C4_GROUNDED_RATE = 0.5
P_C5_PAIRS = (("the", "letters"), ("a", "big"), ("to", "the"))
GAME_COLOURS = ("green", "yellow", "grey", "purple", "red", "blue")
GAME_OBJECTS = ("box", "key", "ball")
WEB_S_MIN = VD.WEB_S_MIN


class ReportError(Exception):
    pass


# ------------------------------------------------------------------------------------------------------------------ loading
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root: Path) -> Dict[str, object]:
    """The five condition records, RESULTS.json and GATES.json (optional) of a runs directory, with the sha256 of each file read."""
    root = Path(root)
    conds: Dict[str, Dict[str, object]] = {}
    files: List[Tuple[str, str]] = []
    for name in CONDITIONS:
        p = root / f"{name}.json"
        if not p.is_file():
            raise ReportError(f"{p.name}: the condition record is missing from {root.name}")
        conds[name] = json.loads(p.read_text())
        files.append((p.name, _sha256(p)))
    p = root / "RESULTS.json"
    if not p.is_file():
        raise ReportError(f"RESULTS.json is missing from {root.name}")
    results = json.loads(p.read_text())
    files.append((p.name, _sha256(p)))
    gates: Optional[Dict[str, object]] = None
    p = root / "GATES.json"
    if p.is_file():
        gates = json.loads(p.read_text())
        files.append((p.name, _sha256(p)))
    return {"conds": conds, "results": results, "gates": gates, "files": files}


# ------------------------------------------------------------------------------------------------------------------ small helpers
def num(x: Optional[float], nd: int = 2) -> str:
    return "none" if x is None else f"{x:.{nd}f}"


def signed(x: Optional[float], nd: int = 2) -> str:
    return "none" if x is None else f"{x:+.{nd}f}"


def mean(xs: Sequence[float]) -> Optional[float]:
    return (sum(xs) / len(xs)) if xs else None


def recs(cond: Dict[str, object], rule: str) -> List[Dict[str, object]]:
    return [r for r in cond["records"] if r["rule"] == rule]


def spread(xs: Sequence[float], nd: int = 2) -> str:
    """«mean (min to max)» of a list, or the single value."""
    if not xs:
        return "none"
    if len(xs) == 1:
        return num(xs[0], nd)
    return f"{num(mean(xs), nd)} ({num(min(xs), nd)} to {num(max(xs), nd)})"


def counts(xs: Sequence[float]) -> str:
    """A COUNT a record carries (frames, says, firings): an integer when there is one record, «mean (min to max)» over seeds (the mean to one decimal, the extremes as integers)."""
    if not xs:
        return "none"
    if len(xs) == 1:
        return str(int(xs[0]))
    return f"{sum(xs) / len(xs):.1f} ({int(min(xs))} to {int(max(xs))})"


def null_of(rec: Dict[str, object], key: str) -> Dict[str, object]:
    n = rec.get(key) or {}
    return {} if "error" in n else n


def null_error(rec: Dict[str, object], key: str) -> Optional[str]:
    n = rec.get(key) or {}
    return str(n["error"]) if "error" in n else None


def kept_sets(cond: Dict[str, object], rule: str) -> List[frozenset]:
    return [frozenset(tuple(f) for f in r["frames"]) for r in recs(cond, rule)]


def grade_ok(rep: Dict[str, object]) -> Tuple[bool, bool]:
    """RESULTS.json's grade equals the grade recomputed from the five condition records, in the run's mode and in the base text's (a JSON round trip makes the two comparable)."""
    conds, res = rep["conds"], rep["results"]
    again = json.loads(json.dumps(VD.grade(conds, res["mode"])))
    again_law = json.loads(json.dumps(VD.grade(conds, "law")))
    return again == res["grade"], again_law == res["grade_law"]


def _roundtrip(x):
    return json.loads(json.dumps(x))


def check_eye(rep: Dict[str, object]) -> Optional[bool]:
    """RESULTS.json's eye reading equals the reading recomputed from ALPHA4.json and the per-frame table it carries (the says rebuilt from the table: the reading depends on the counts a frame has, nothing else).
    None when RESULTS.json has no table."""
    eye = rep["results"]["eye"]
    frames = eye.get("frames")
    if frames is None:
        return None
    says: List[Tuple[str, str, int]] = []
    for f in frames:
        for i in range(int(f["says"])):
            says.append((f["frame"], "yes" if i < int(f["yes"]) else "no", len(says)))
    return _roundtrip(VD.eye_reading(rep["conds"]["ALPHA4"], says)) == eye


def check_overlaps(rep: Dict[str, object]) -> bool:
    return _roundtrip({name: VD.overlaps(rep["conds"][name]) for name in CONDITIONS}) == rep["results"]["overlaps"]


def check_scene(rep: Dict[str, object]) -> bool:
    """The SCENE block's rows are the SCENE record's (rule, seed, G), each margin is G_max − G, the oracle's margin is G_max − its G, and its recalls are recomputed from SCENE.json against the 24 oracle frames."""
    sc, sb = rep["conds"]["SCENE"], rep["results"]["scene"]
    recs_ = sc["records"]
    if len(sb["rows"]) != len(recs_):
        return False
    for row, r in zip(sb["rows"], recs_):
        if (row["rule"], row["seed"]) != (r["rule"], r["seed"]) or row["G"] != r["gain"]["G"] or abs(row["margin"] - (sb["G_max"] - r["gain"]["G"])) > 1e-9:
            return False
    o = sb["oracle"]
    return abs(o["margin"] - (sb["G_max"] - o["G"])) <= 1e-9 and _roundtrip(VD.oracle_recall(sc, SC.oracle_frames())) == o["recall"]


def law_flags(rep: Dict[str, object]) -> List[Tuple[str, bool]]:
    """Per source, whether its header carries the same three signed texts as RESULTS.json."""
    h = rep["results"].get("header", {})
    keys = [f"prereg_{k}_sha256" for k in ("frames", "frames_amend1", "frames_amend2")]
    out = [(name, all(rep["conds"][name]["header"].get(k) == h.get(k) for k in keys)) for name in CONDITIONS]
    if rep["gates"] is not None:
        out.append(("GATES.json", all(rep["gates"]["header"].get(k) == h.get(k) for k in keys)))
    return out


def _yn(ok: Optional[bool]) -> str:
    return "yes" if ok else "NO"


# ------------------------------------------------------------------------------------------------------------------ 0 · provenance
def sec_provenance(rep: Dict[str, object]) -> List[str]:
    conds, res, gates = rep["conds"], rep["results"], rep["gates"]
    h = res.get("header", {})
    L = ["== 0 · PROVENANCE"]
    L.append(f"gate mode: {res.get('mode')}; code sha (RESULTS.json): {h.get('toys_git_sha')}; the toy's tree differed from it when the unit ran: {h.get('toys_tree_dirty')}")
    keys = ("frames", "frames_amend1", "frames_amend2")
    for k in keys:
        L.append(f"signed text {k}: sha256 {h.get(f'prereg_{k}_sha256')}")
    L.append("signed texts: every record carries RESULTS.json's three: " + "; ".join(f"{name} {_yn(ok)}" for name, ok in law_flags(rep)))
    code = sorted({str(c["header"].get("toys_git_sha")) for c in conds.values()} | {str(h.get("toys_git_sha"))})
    L.append(f"code sha across the five conditions and RESULTS.json: {'one' if len(code) == 1 else str(len(code)) + ' DIFFERENT'} ({', '.join(code)})")
    if gates is not None:
        L.append(f"code sha of GATES.json: {gates['header'].get('toys_git_sha')} ({'the same' if gates['header'].get('toys_git_sha') == h.get('toys_git_sha') else 'DIFFERENT from the unit'})")
    ok_a, ok_l = grade_ok(rep)
    L.append(f"CHECK grade: RESULTS.json's grade equals the grade recomputed from the five condition records: {_yn(ok_a)} (mode {res.get('mode')}); the base text's mode: {_yn(ok_l)}")
    eye_ok = check_eye(rep)
    L.append("CHECK eye: not checked: RESULTS.json has no per-frame table" if eye_ok is None
             else f"CHECK eye: RESULTS.json's eye reading equals the reading recomputed from ALPHA4.json and its own per-frame table: {_yn(eye_ok)}")
    L.append(f"CHECK overlaps: RESULTS.json's overlaps equal the overlaps recomputed from the five records: {_yn(check_overlaps(rep))}")
    L.append(f"CHECK scene: RESULTS.json's SCENE rows, margins and recalls equal those recomputed from SCENE.json: {_yn(check_scene(rep))}")
    L.append("records (sha256, two spaces, file name — the format of sha256sum):")
    for name, sha in rep["files"]:
        L.append(f"{sha}  {name}")
    if gates is None:
        L.append("GATES.json: not present")
    return L


# ------------------------------------------------------------------------------------------------------------------ 1 · gates
def _g4_stream_lines(key: str, s: Dict[str, object]) -> List[str]:
    L = [f"  stream {key}: {s.get('label')}: {s.get('n_moments')} moments, a plant after every {s.get('every')}th ({s['plants'][0]} train / {s['plants'][1]} held plants); "
         f"V {s.get('V')}, budget B = 2V = {s.get('budget')}; B = G({{F*}}) {num(s.get('B'))}; PLANT-BEATS-NULL-2 {s.get('plant_beats_null2')} (NULL-2 q95 {num(s.get('null2_q95'))})"]
    required = list(s.get("required", []))
    for rule in RULES:
        g = s["gates"].get(rule)
        if g is None:
            continue
        tag = "REQUIRED" if rule in required else "PRINTED, not required"
        L.append(f"    {rule} {g['n_counted']} of {g['n_seeds']} seeds count (need {g['need']}): gate {'PASS' if g['pass'] else 'FAIL'} — {tag}")
    c = s.get("control", {})
    L.append(f"    the gate's parse-breaking control: caught {c.get('caught')}, bytes changed {c.get('bytes_changed')}; honest gate (B {num(c.get('B_honest'))}, C {num(c.get('C_honest'))}) "
             f"{c.get('gate_honest')}, broken gate (B {num(c.get('B_broken'))}, C {num(c.get('C_broken'))}) {c.get('gate_broken')}")
    return L


def sec_gates(rep: Dict[str, object]) -> List[str]:
    g = rep["gates"]
    L = ["== 1 · GATES (G1-G6 on the real copies, before the unit)"]
    if g is None:
        L.append("GATES.json: not present — the gates are not recorded here")
        return L
    L.append(f"GATES.json: passed {g.get('passed')} (failures: {g.get('failures') or 'none'}); gate mode {g['header'].get('gate_mode')}; {num(g.get('cpu_seconds'), 1)} CPU-s; peak RSS {num((g.get('peak_rss_kb') or 0) / 1024.0, 0)} MB")
    g1 = g["g1"]
    c2 = g1.get("chi2", {})
    L.append(f"G1 {'OK' if g1['ok'] else 'FAILED'}: {g1.get('copies_verified')} copies verified; ALPHA4 {g1['alpha4']['moments']} moments / {g1['alpha4']['words']} words; SCENE {g1['scene']['moments']} moments; "
             f"says {tuple(g1.get('says', ()))} (rows, yes, distinct frames); plant tokens in real rows: ALPHA4 {g1.get('plant_tokens', {}).get('ALPHA4')}, SCENE {g1.get('plant_tokens', {}).get('SCENE')}")
    L.append("   χ² fit of SCENE to the generator (each p > 0.001 gates G_max): " + ", ".join(f"{k} p {num((c2.get(k) or {}).get('p'), 3)}" for k in ("length", "shape", "colour", "size", "pairs"))
             + f"; held-out pairs seen {c2.get('heldout_pairs_seen')}; «dax» excluded {c2.get('dax_excluded')}; G_max gated: {c2.get('gated')}")
    g2 = g["g2"]
    L.append(f"G2 {'OK' if g2['ok'] else 'FAILED'}: find_frames on the stand-in store equals the call on the real Episodes store: {g2.get('n_rows')} rows, frames {g2.get('frames')}")
    g3 = g["g3"]
    L.append(f"G3 {'OK' if g3['ok'] else 'FAILED'}: {g3.get('compressor_cases')} compressor cases, max |fast − slow| {g3.get('max_abs_diff'):.3g} (bar 1e-9); the greedy's {g3.get('mdl_steps')} steps over {g3.get('mdl_seeds')} seeds, problems {g3.get('mdl_problems') or 'none'}")
    g4 = g["g4"]
    L.append(f"G4 {'OK' if g4['ok'] else 'FAILED'}: two planted synthetic streams (AMENDMENT-2 §2); failures {g4.get('failures') or 'none'}")
    for key in sorted(g4["streams"]):
        L += _g4_stream_lines(key, g4["streams"][key])
    g5 = g["g5"]
    L.append(f"G5 {'OK' if g5['ok'] else 'FAILED'}: pilots " + "; ".join(f"{p['draws']} draws {num(p['cpu_seconds'], 1)} CPU-s, peak {num(p['peak_rss_kb'] / 1024.0, 0)} MB" for p in g5.get("pilots", []))
             + f"; slope {num(g5.get('cpu_slope_per_draw'), 3)} CPU-s a draw; predicted unit {num(g5.get('predicted_unit_cpu_minutes'), 1)} CPU-min (ceiling {num(g5.get('cpu_ceiling_min'), 1)}); "
             f"predicted peak {num(g5.get('predicted_peak_rss_mb'), 0)} MB (ceiling {num(g5.get('rss_ceiling_mb'), 0)}); measured peak {num(g5.get('peak_rss_mb'), 0)} MB")
    g6 = g["g6"]
    ex = g6.get("exact", {})
    ch = g6.get("cheat", {})
    L.append(f"G6 {'OK' if g6['ok'] else 'FAILED'}: {len(g6.get('replicates', []))} replicates, smallest margin G_max − G(F_oracle) {num(g6.get('min_margin'))}, violations "
             f"{sum(1 for r in g6.get('replicates', []) if r.get('violation'))}; the planted cheat: caught {ch.get('caught')} (G {num(ch.get('G_cheat'))} against G_max {num(ch.get('G_max'))} + 20); "
             f"exact checks: support sums to {ex.get('sum_p')!r}, entropy {num(ex.get('entropy'), 4)}, H(length) {num(ex.get('h_length'), 4)}, H(utterance | length) {num(ex.get('h_given_length'), 4)}, support {ex.get('support_size')}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 2 · the five conditions
def sec_conditions(rep: Dict[str, object]) -> List[str]:
    L = ["== 2 · THE FIVE CONDITIONS",
         f"{'condition':<16}{'kind':<9}{'every':>6}{'train/held moments':>22}{'train/held words':>20}{'V':>7}{'N0':>9}{'draws':>7}{'CPU-s':>9}{'peak MB':>9}"]
    for name in CONDITIONS:
        c = rep["conds"][name]
        L.append(f"{name:<16}{c['kind']:<9}{str(c.get('every') or '-'):>6}{str(c['n_train_moments']) + '/' + str(c['n_held_moments']):>22}{str(c['n_train_words']) + '/' + str(c['n_held_words']):>20}"
                 f"{c['V']:>7}{c['N0']:>9}{c['draws']:>7}{num(c.get('cpu_seconds'), 1):>9}{num((c.get('peak_rss_kb') or 0) / 1024.0, 0):>9}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 3 · the plant gate
def sec_plant(rep: Dict[str, object]) -> List[str]:
    conds, res = rep["conds"], rep["results"]
    L = ["== 3 · THE PLANT GATE (AMENDMENT-1 §1: keeps F*, (B) G({F*}) > 0, (C) F*'s marginal credit in the rule's own set > 0; WEB-S at >= 9 of 10 seeds, a seed counted only if it keeps F* AND (C) > 0)"]
    for name, side in (("ALPHA4+PLANT", "alpha4"), ("SCENE+PLANT", "scene")):
        c = conds[name]
        ps = c["plant_stream"]
        d = ps.get("decomposition", {})
        n2 = ps.get("null2_of_plant", {})
        L.append(f"{name}: plants {ps['plants_train']} train / {ps['plants_held']} held; V {ps['V']}; N0 {ps['N0']}")
        L.append(f"  (B) G({{F*}}) = {signed(ps['B'])} bits; the architect's first-order expected value {num(ps.get('expected_first_order'))}; decomposition M {num(d.get('M'))} + D {num(d.get('D'))} + C {num(d.get('C'))} − L {num(d.get('L'))}"
                 f" = {num(d.get('G'))} (T = D + C = {num(d.get('T'))}; denominator effect {num(d.get('delta'), 5)} bits a token; {d.get('firings')} held firings)")
        L.append(f"  PLANT-BEATS-NULL-2 {name}: {ps['plant_beats_null2']} (B {num(ps['B'])} against NULL-2 of {{F*}}: mean {num(n2.get('mean'))}, sd {num(n2.get('sd'))}, q95 {num(n2.get('q95'))}, "
                 f"fallbacks {n2.get('fallbacks')}, {n2.get('draws')} draws)")
        for rule in RULES:
            rs = recs(c, rule)
            if not rs:
                continue
            pg = res["grade"][side][rule]["plant_gate"]
            lg = res["grade_law"][side][rule]["plant_gate"]
            kept = sum(1 for r in rs if r["plant"]["kept"])
            A = [r["plant"]["A"] for r in rs]
            C = [r["plant"]["C"] for r in rs if r["plant"]["C"] is not None]
            L.append(f"  plant gate {name} {rule}: {'PASS' if pg['pass'] else 'FAIL'} — {pg['n_counted']} of {pg['n_seeds']} seeds count (need {pg['need']}); keeps F* at {kept} of {len(rs)}; "
                     f"(A) whole-set G {spread(A)}; (C) F*'s marginal credit {spread(C)}; the base text's clause (keeps AND (A) > 0): {'pass' if lg['pass'] else 'fail'} (a reading)")
    L.append("GATE FIRST: a rule that fails its plant gate on a stream is NOT GRADABLE there:")
    for rule in RULES:
        if rule in res["grade"]["alpha4"]:
            L.append(f"  {rule}: ALPHA4 {'gradable' if res['grade']['alpha4'][rule]['plant_gate']['pass'] else 'NOT GRADABLE'} on the plant; SCENE {'gradable' if res['grade']['scene'][rule]['gradable'] else 'NOT GRADABLE'}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 4 · shuffle
def sec_shuffle(rep: Dict[str, object]) -> List[str]:
    c = rep["conds"]["ALPHA4+SHUFFLE"]
    res = rep["results"]
    L = ["== 4 · SHUFFLE-QUIET (ALPHA4+SHUFFLE: G(F) <= NULL-1's q95, or F empty; WEB-S quiet at >= 8 of 10 seeds)"]
    for rule in RULES:
        rs = recs(c, rule)
        if not rs:
            continue
        sq = res["grade"]["alpha4"][rule]["shuffle_quiet"]
        L.append(f"SHUFFLE-QUIET {rule}: {'QUIET' if sq['quiet'] else 'LOUD'} — {sq['n_quiet']} of {sq['n']} (need {sq['need']}); empty sets {sq['empty']}; |F| {counts([r['n_frames'] for r in rs])}; "
                 f"G {spread([r['gain']['G'] for r in rs])}; NULL-1 q95 {spread([null_of(r, 'null1').get('q95') for r in rs if null_of(r, 'null1')])}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 5 · gain
def _null_row(rs: List[Dict[str, object]], key: str) -> str:
    label = key.upper().replace("NULL", "NULL-")
    ns = [null_of(r, key) for r in rs]
    ns = [n for n in ns if n]
    errs = [e for e in (null_error(r, key) for r in rs) if e is not None]
    if not ns:
        return f"{label} error: {errs[0]}" if errs else f"{label} none"
    out = (f"{label} mean {spread([n['mean'] for n in ns])} sd {spread([n['sd'] for n in ns])} q95 {spread([n['q95'] for n in ns])} "
           f"z {spread([n['z'] for n in ns if n.get('z') is not None])} fallbacks {sum(n.get('fallbacks', 0) for n in ns)}")
    if errs:
        out += f" ({len(errs)} of {len(rs)} without a null: {errs[0]})"
    return out


def sec_gain(rep: Dict[str, object]) -> List[str]:
    a4, res = rep["conds"]["ALPHA4"], rep["results"]
    L = ["== 5 · GAIN (ALPHA4: G(F) > q95 of NULL-1 AND G(F) > 0; WEB-S judged by the seeds that pass, >= 8 of 10, exact sign p printed)"]
    for rule in RULES:
        rs = recs(a4, rule)
        if not rs:
            continue
        gv = res["grade"]["alpha4"][rule]
        gn = gv["gain"]
        adj = [r["adjacency"]["train_adjacent_share"] for r in rs if r["adjacency"]["train_adjacent_share"] is not None]
        L.append(f"GAIN {rule}: {gv['gain_verdict']} — gate first {'ok' if gv['gate_first_ok'] else 'NOT ok'} (plant gate {'pass' if gv['plant_gate']['pass'] else 'FAIL'}, "
                 f"shuffle {'quiet' if gv['shuffle_quiet']['quiet'] else 'LOUD'}); {gn['n_pass']} of {gn['n']} seeds pass (need {gn['need']}; exact sign p {num(gn['exact_sign_p'], 4)}); {gn['no_null']} without a null")
        L.append(f"    |F| {counts([r['n_frames'] for r in rs])}; share with a within-moment adjacent train occurrence {spread(adj, 3)}; G {spread([r['gain']['G'] for r in rs])} bits "
                 f"= {spread([r['gain']['per_word'] for r in rs], 5)} a held-out word; L {spread([r['gain']['L'] for r in rs])}; held adjacency: zero-firing frames {counts([r['adjacency']['held_adjacent_zero'] for r in rs])}, "
                 f"firings {counts([r['adjacency']['held_firings'] for r in rs])}")
        L.append(f"    {_null_row(rs, 'null1')}")
        an = [r["anatomy"] for r in rs]
        L.append(f"    anatomy G = M + D + C − L: M {spread([a['M'] for a in an])}, D {spread([a['D'] for a in an])}, C {spread([a['C'] for a in an])}, L {spread([a['L'] for a in an])}; T = D + C {spread([a['T'] for a in an])}")
        if rule == "WEB-S":
            for r in rs:
                n1 = null_of(r, "null1")
                L.append(f"      WEB-S seed {r['seed']}: |F| {r['n_frames']}, G {num(r['gain']['G'])}, NULL-1 q95 {num(n1.get('q95'))}, beats q95 {n1.get('beats_q95')}")
    mdl = recs(a4, "MDL-GREEDY")
    if mdl and mdl[0].get("info", {}).get("trace"):
        tr = mdl[0]["info"]["trace"]
        L.append(f"MDL-GREEDY took {len(tr)} steps; its first {min(15, len(tr))} picks (frame, train Δ bits, train firings):")
        for t in tr[:15]:
            L.append(f"      {' '.join(t['frame'])}  Δ {num(t['delta'])}  fires {t['fires']}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 6 · criterion
def sec_criterion(rep: Dict[str, object]) -> List[str]:
    a4, res = rep["conds"]["ALPHA4"], rep["results"]
    beats = res["grade"]["plant_beats_null2"]
    L = ["== 6 · CRITERION-MATTERS (NULL-2) (a reading, no bar: G(F) > q95 of NULL-2 AND G(F) > 0; WEB-S: seeds of ten; gated by PLANT-BEATS-NULL-2)",
         f"PLANT-BEATS-NULL-2: ALPHA4+PLANT {beats['ALPHA4+PLANT']}, SCENE+PLANT {beats['SCENE+PLANT']}"]
    for rule in RULES:
        rs = recs(a4, rule)
        if not rs:
            continue
        cr = res["grade"]["alpha4"][rule]["criterion"]
        L.append(f"CRITERION-MATTERS {rule}: {cr['verdict']} — {cr['n_pass']} of {cr['n']} seeds (need {cr['need']})")
        L.append(f"    G {spread([r['gain']['G'] for r in rs])}; {_null_row(rs, 'null2')}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 7 · the eye
def _rate(r: Optional[float], n: int) -> str:
    return f"{num(r, 3)} (n {n})"


def sec_eye(rep: Dict[str, object]) -> List[str]:
    eye = rep["results"]["eye"]
    a4 = rep["conds"]["ALPHA4"]
    L = ["== 7 · THE EYE'S READING (ALPHA4: the cells' said frames against each rule's kept set; a reading, never a bar)",
         f"the cells said {eye['distinct_said']} distinct frames, {eye['says']} says, {eye['yes']} confirmed by the eye: base rate {num(eye['base_rate'], 4)}"]
    for rule in RULES:
        er = [r for r in eye["records"] if r["rule"] == rule]
        if not er:
            continue
        L.append(f"  {rule}: keeps {counts([r['said_kept'] for r in er])} of the {eye['distinct_said']} said frames; pooled yes-rate of the says of the frames it KEEPS "
                 f"{spread([r['rate_kept'] for r in er if r['rate_kept'] is not None], 3)} (says kept {counts([r['says_kept'] for r in er])}) against those it does not keep "
                 f"{spread([r['rate_not_kept'] for r in er if r['rate_not_kept'] is not None], 3)} (says not kept {counts([r['says_not_kept'] for r in er])}); "
                 f"frames it keeps that the cells never said {counts([r['kept_never_said'] for r in er])} of |F| {counts([r['n_frames'] for r in er])}")
    frames = eye.get("frames")
    if frames:
        L.append("the said frames (says, eye-confirmed) and which rules keep each (WEB-S: seeds keeping it):")
        sets = {rule: kept_sets(a4, rule) for rule in RULES}
        for f in frames:
            pair = tuple(f["pair"]) if f["pair"] else None
            flags = []
            for rule in RULES:
                if pair is None:
                    flags.append(f"{rule} -")
                elif rule == "WEB-S":
                    flags.append(f"{rule} {sum(1 for s in sets[rule] if pair in s)}/{len(sets[rule])}")
                else:
                    flags.append(f"{rule} {'kept' if pair in sets[rule][0] else 'no'}")
            L.append(f"      «{f['frame']}»  says {f['says']}  yes {f['yes']}  " + "  ".join(flags))
    else:
        L.append("the per-frame table is not in RESULTS.json (eye.frames absent)")
    return L


# ------------------------------------------------------------------------------------------------------------------ 8 · overlaps
def sec_overlaps(rep: Dict[str, object]) -> List[str]:
    L = ["== 8 · OVERLAPS (Jaccard between the rules' kept sets; WEB-S: the mean over its seeds)"]
    for name in CONDITIONS:
        ov = rep["results"]["overlaps"][name]
        L.append(f"{name}: " + "; ".join(f"{k} {num(v, 3)}" for k, v in sorted(ov.items())))
    return L


# ------------------------------------------------------------------------------------------------------------------ 9 · scene
def sec_scene(rep: Dict[str, object]) -> List[str]:
    res = rep["results"]
    sb = res["scene"]
    sc = rep["conds"]["SCENE"]
    L = ["== 9 · SCENE (the control with a known generator)"]
    ch = sb["chi2"]
    L.append(f"generator fit (G1 χ²): " + ", ".join(f"{k} p {num((ch.get(k) or {}).get('p'), 3)} (n {(ch.get(k) or {}).get('n')})" for k in ("length", "shape", "colour", "size", "pairs"))
             + f"; held-out pairs seen {ch.get('heldout_pairs_seen')}; G_max gated: {sb['gmax_gated']}")
    L.append(f"THE CEILING: G_max {num(sb['G_max'])} bits (bits(held | empty) {num(sb['bits0'])} minus the generator's own code length); the expected form bits(empty) − 6.0774 · N_utt {num(sb['expected_form'])}; "
             f"entropy {num(sb['entropy'], 4)}; H(utterance | length) {num(sb['h_given_length'], 4)} (a reference for a code handed the lengths, never a gate); STOP {sb['stop']}")
    for r in sb["rows"]:
        L.append(f"  {r['rule']:<11}seed {r['seed']:>2}  G {num(r['G'])}  margin to G_max {num(r['margin'])}  {'VIOLATION' if r['violation'] else 'under G_max + 20'}")
    o = sb["oracle"]
    L.append(f"G(F_oracle) {num(o['G'])} ({o['n_frames']} frames; margin to G_max {num(o['margin'])}; violation {o['violation']}); each rule's recall of F_oracle: "
             + ", ".join(f"{k} {num(v, 3)}" for k, v in sorted(o["recall"].items())))
    for rule in RULES:
        rs = recs(sc, rule)
        if not rs:
            continue
        L.append(f"SCENE {rule}: {'gradable' if res['grade']['scene'][rule]['gradable'] else 'NOT GRADABLE'} (SCENE+PLANT plant gate: {res['grade']['scene'][rule]['plant_gate']['n_counted']} of "
                 f"{res['grade']['scene'][rule]['plant_gate']['n_seeds']} seeds count, need {res['grade']['scene'][rule]['plant_gate']['need']})")
        L.append(f"    |F| {counts([r['n_frames'] for r in rs])}; G {spread([r['gain']['G'] for r in rs])}; {_null_row(rs, 'null1')}; {_null_row(rs, 'null2')}")
    return L


# ------------------------------------------------------------------------------------------------------------------ 10 · predictions
def _pairs_said(eye: Dict[str, object]) -> List[Dict[str, object]]:
    return [f for f in (eye.get("frames") or []) if f.get("pair")]


def predictions(rep: Dict[str, object]) -> List[Tuple[str, str, str]]:
    """(name, verdict, detail) for P-C1 .. P-C6, each a MECHANICAL reading with its definition in the detail (fixed before the unit ran)."""
    a4, sc, res = rep["conds"]["ALPHA4"], rep["conds"]["SCENE"], rep["results"]
    G = {rule: [r["gain"]["G"] for r in recs(a4, rule)] for rule in RULES}
    out: List[Tuple[str, str, str]] = []
    mdl = G["MDL-GREEDY"][0]
    mean_s = sum(G["WEB-S"]) / len(G["WEB-S"])
    holds = mdl >= max(G["WEB-H"][0], mean_s, G["SENTENCE"][0])
    out.append(("P-C1", "holds" if holds else "does not hold",
                f"[Likely] MDL-GREEDY's G is the largest: G {num(mdl)} against WEB-H {num(G['WEB-H'][0])}, WEB-S mean {num(mean_s)}, SENTENCE {num(G['SENTENCE'][0])} (reading: MDL's G >= the largest of the other three, WEB-S as its seed mean)"))
    # P-C2: WEB and SENTENCE beat their dealt nulls but with G below MDL's
    parts: List[str] = []
    ok2 = True
    for rule in ("WEB-H", "SENTENCE"):
        r = recs(a4, rule)[0]
        n1 = null_of(r, "null1")
        b = bool(n1) and r["gain"]["G"] > n1["q95"]
        below = r["gain"]["G"] < mdl
        ok2 = ok2 and b and below
        parts.append(f"{rule} beats NULL-1 q95 {b}, G below MDL's {below}")
    rs = recs(a4, "WEB-S")
    beat = sum(1 for r in rs if null_of(r, "null1") and r["gain"]["G"] > null_of(r, "null1")["q95"])
    need = -(-WEB_S_MIN * len(rs) // 10)
    below_s = mean_s < mdl
    ok2 = ok2 and beat >= need and below_s
    parts.append(f"WEB-S beats its NULL-1 q95 at {beat} of {len(rs)} seeds (need {need}), seed-mean G below MDL's {below_s}")
    out.append(("P-C2", "holds" if ok2 else "does not hold", "[Guessing] WEB and SENTENCE beat their dealt nulls on ALPHA4 with G below MDL-GREEDY's (reading: G > NULL-1 q95 — WEB-S at >= 8 of 10 seeds — and G < MDL's G): " + "; ".join(parts)))
    # P-C3: on plain SCENE every G is far below G_max
    gm = res["scene"]["G_max"]
    if gm is None or gm <= 0:
        out.append(("P-C3", "not readable", f"[Guessing] on SCENE every G ≪ G_max: G_max {num(gm)} is not positive"))
    else:
        ratios = {rule: mean([r["gain"]["G"] for r in recs(sc, rule)]) / gm for rule in RULES if recs(sc, rule)}
        ok3 = all(v <= P_C3_FRACTION for v in ratios.values())
        out.append(("P-C3", "holds" if ok3 else "does not hold",
                    f"[Guessing] on SCENE no rule's G is near G_max (reading: every rule's G, WEB-S as its seed mean, <= {P_C3_FRACTION:.2f} x G_max {num(gm)}): " + ", ".join(f"{k} {num(v, 4)}" for k, v in sorted(ratios.items()))
                    + f"; G(F_oracle) / G_max {num(res['scene']['oracle']['G'] / gm, 4)}"))
    # P-C4 and P-C5 read the said frames
    eye = res["eye"]
    said = _pairs_said(eye)
    mdl_kept = kept_sets(a4, "MDL-GREEDY")[0]
    grounded = [f for f in said if f["says"] >= P_C4_MIN_SAYS and f["yes"] / f["says"] >= P_C4_GROUNDED_RATE]
    function = [f for f in said if f["says"] >= P_C4_MIN_SAYS and f["yes"] == 0]
    kept_g = [f["frame"] for f in grounded if tuple(f["pair"]) in mdl_kept]
    kept_f = [f["frame"] for f in function if tuple(f["pair"]) in mdl_kept]
    er = [r for r in eye["records"] if r["rule"] == "MDL-GREEDY"][0]
    base = f"MDL-GREEDY keeps grounded said frames {kept_g or 'none'} of {len(grounded)} and function-word pairs {kept_f or 'none'} of {len(function)}; pooled yes-rate of the says it keeps {num(er['rate_kept'], 3)} (n {er['says_kept']}) against {num(er['rate_not_kept'], 3)} (n {er['says_not_kept']}), base rate {num(eye['base_rate'], 3)}"
    if not grounded or not function:
        out.append(("P-C4", "not readable", f"[Likely] the eye's reading splits MDL's frames (reading: it keeps >= 1 GROUNDED said frame (>= {P_C4_MIN_SAYS} says, >= {P_C4_GROUNDED_RATE:.0%} confirmed) AND >= 1 FUNCTION-WORD pair (>= {P_C4_MIN_SAYS} says, 0 confirmed)): "
                                                    f"the said set has {len(grounded)} grounded and {len(function)} function-word frames; {base}"))
    else:
        out.append(("P-C4", "holds" if (kept_g and kept_f) else "does not hold",
                    f"[Likely] the eye's reading splits MDL's frames (reading: it keeps >= 1 GROUNDED said frame (>= {P_C4_MIN_SAYS} says, >= {P_C4_GROUNDED_RATE:.0%} confirmed) AND >= 1 FUNCTION-WORD pair (>= {P_C4_MIN_SAYS} says, 0 confirmed)): {base}"))
    sent = kept_sets(a4, "SENTENCE")[0]
    named = [(" ".join(p), p in sent) for p in P_C5_PAIRS]
    game_kept = sorted(" ".join(p) for p in sent if p[0] in GAME_COLOURS and p[1] in GAME_OBJECTS)
    ok5 = all(k for _p, k in named) and len(game_kept) >= 1
    out.append(("P-C5", "holds" if ok5 else "does not hold",
                "[Guessing] SENTENCE keeps «the letters», «a big», «to the» and a game pair or two (reading: all three kept AND >= 1 (colour, object) game pair kept): SENTENCE "
                + ", ".join(f"kept «{p}»: {'yes' if k else 'no'}" for p, k in named) + f"; game pairs kept {game_kept or 'none'}"))
    # P-C6: NULL-2, two guesses
    n2 = null_of(recs(a4, "MDL-GREEDY")[0], "null2")
    if not n2:
        out.append(("P-C6", "not readable", "[Guessing] MDL's G against NULL-2: no NULL-2 on MDL-GREEDY's record"))
    else:
        z = {}
        for rule in RULES:
            zs = [null_of(r, "null2").get("z") for r in recs(a4, rule)]
            zs = [v for v in zs if v is not None]
            z[rule] = mean(zs) if zs else None
        inside = mdl <= n2["q95"]
        above = mdl > n2["q95"]
        others = [z[r] for r in ("WEB-H", "WEB-S", "SENTENCE")]
        nearer = z["MDL-GREEDY"] is not None and all(v is not None and v < z["MDL-GREEDY"] for v in others)
        out.append(("P-C6", "architect's guess " + ("holds" if inside else "does not hold") + "; mine " + ("holds" if (above and nearer) else "does not hold"),
                    f"[Guessing, two] on NULL-2: (architect) MDL-GREEDY's G sits near NULL-2's band = G <= q95: {inside}; (mine) it is above NULL-2's q95 {above} and WEB and SENTENCE sit nearer to it "
                    f"(their NULL-2 z, WEB-S as its seed mean, all below MDL's) {nearer}: MDL G {num(mdl)} vs NULL-2 mean {num(n2['mean'])} sd {num(n2['sd'])} q95 {num(n2['q95'])}; z "
                    + ", ".join(f"{k} {num(v, 2)}" for k, v in sorted(z.items()))))
    return out


def sec_predictions(rep: Dict[str, object]) -> List[str]:
    L = ["== 10 · PREDICTIONS (the law's §4, read mechanically with the definitions fixed before the unit ran; readings, never bars)"]
    for name, verdict, detail in predictions(rep):
        L.append(f"{name} {verdict} — {detail}")
    return L


# ------------------------------------------------------------------------------------------------------------------ the whole text
def render(rep: Dict[str, object]) -> str:
    parts = [sec_provenance(rep), sec_gates(rep), sec_conditions(rep), sec_plant(rep), sec_shuffle(rep), sec_gain(rep), sec_criterion(rep), sec_eye(rep), sec_overlaps(rep), sec_scene(rep),
             sec_predictions(rep)]
    return "\n\n".join("\n".join(p) for p in parts) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="TOY C's report: every figure of RESULT-TOY-FRAMES.md, rendered from the runner's records")
    ap.add_argument("--root", default=str(RN.RUNS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(list(argv) if argv is not None else None)
    text = render(load(Path(a.root)))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"wrote {out.name}: {len(text)} bytes, sha256 {hashlib.sha256(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
