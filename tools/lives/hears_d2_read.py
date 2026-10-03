#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:30 +0400 — PREREG-HEARS-2 AMENDMENT 1 §A1.7 (D2): the read of a HEARS-2 pre-flight life's own files after its kill and resume (`heard_by_world`, which §3 named, exists in no
# code). Built test-first (tests/tools/test_hears_d2_read.py); read-only; its controls run on the real inputs.
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:02 +0400 — AMENDMENT 3: found by the first REAL pre-flight (16 false violations): a learn event is identified by its TAPE ROW (`seq`), never by the moment NAME — the
# maker sense keeps window / i / total in the thread's memory (creature/world_maker.py sense()), so after every resume it redraws its first pictures under the SAME names on NEW tape rows. «Learned twice» = the same seq
# journaled twice (the days law's residual); a seq not seen before is a NEW canvas whatever its name; (c)'s order is by seq too; a fourth control, `redrawn` (same name, new seq, the next index) must read NEW.
"""tools/lives/hears_d2_read.py <life root> [--out <json file>]

What AMENDMENT 1 §A1.7 (as corrected by AMENDMENT 3) asks of a pre-flight life of `hears scene maker` that was killed (and cut, and failed) and came back, read from the life's OWN files and nothing else.
A learn event is a TAPE ROW: its `seq`. The maker world re-draws its first pictures under the same moment names after every restart, so a NAME says nothing about which tape row the brain heard.
  (a) the maker's count CONTINUES across each resume: the first maker `learn` row after a `start` event row with resumed_from_seq > 0 carries the index the brain restored — the index the same seq carried before if the
      journal already holds that seq (a row re-consumed after the resume), else one past the number of distinct maker seqs learned so far — never 0 again;
  (b) any maker tape row journaled twice (the days law's residual: rows appear twice after a resume, the startup replay writing them BEFORE the `start` row) carries the SAME `scene` and `world_seed` both times; every NEW
      seq (whatever its name) takes the next index (0, 1, 2 … no restart, no gap); every maker row carries world_seed_of(<the genome's SEED>, "maker");
  (c) the census files (<root>/census/<scenes learned>.json) agree with the journal: for the file of N scenes, the maker count among the first N distinct learned seqs (by first appearance, any world) equals the file's
      scenes_by_world.maker, and the scene count its scenes_by_world.scene.
Four controls run on the real rows every time — the maker's count restarted at the last resume (reset), the first maker row's derived seed changed (seed), the last census file's maker count raised by one (census): each
must be CAUGHT; and a canvas REDRAWN (an earlier name on an unseen seq with the next index): it must read NEW, no violation added. A control that is MISSED or MISREAD means the read is blind and the run fails. A life
with no resume that has maker rows on both sides is NOT GRADABLE (exit 3), never PASS. Torn lines (a power cut) are counted, not fatal. The number of maker tape rows whose name had been used on an earlier row is
PRINTED (`moment_ids_reused`): it is the world's restarts made visible, not a fault. Exit 0 PASS, 1 FAIL, 2 an unreadable root, 3 NOT GRADABLE."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genome.brain import world_seed_of  # noqa: E402
from genome.machinery import parse_genome  # noqa: E402

MAKER = "maker"


class D2Error(Exception):
    """A root that cannot be read, named by the path that is missing."""


def read_journal(root: Path) -> Tuple[List[Dict[str, object]], int]:
    files = sorted((Path(root) / "journal").glob("*.jsonl"))
    if not files:
        raise D2Error(f"{root}/journal holds no *.jsonl — nothing to read")
    rows: List[Dict[str, object]] = []
    torn = 0
    for f in files:
        with f.open("rb") as fh:
            for raw in fh:
                if not raw.strip():
                    continue
                try:
                    rows.append(json.loads(raw))
                except ValueError:                      # a torn tail or a zero-filled run from a power cut: counted
                    torn += 1
    return rows, torn


def read_census(root: Path) -> Dict[int, Dict[str, object]]:
    out: Dict[int, Dict[str, object]] = {}
    for f in sorted((Path(root) / "census").glob("*.json")):
        try:
            out[int(f.stem)] = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            out[int(f.stem)] = {"unreadable": True}
    return out


def _is_learn(r: Dict[str, object]) -> bool:
    return r.get("kind") == "brain" and r.get("act") == "learn"


def check(rows: Sequence[Dict[str, object]], world_seed: Optional[int], census: Dict[int, Dict[str, object]]) -> Dict[str, object]:
    """The pure comparison (a), (b), the seed and (c) over journal rows and census files; no I/O. A learn event is identified by its tape `seq`."""
    resumes = [i for i, r in enumerate(rows) if r.get("event") == "start" and int(r.get("resumed_from_seq") or 0) > 0]
    maker = [(i, r) for i, r in enumerate(rows) if _is_learn(r) and r.get("world") == MAKER]
    seen: Dict[object, Tuple[object, object, str]] = {}          # tape seq -> (scene, world_seed, name) of the FIRST journal row for that seq
    first_seq_of_name: Dict[str, object] = {}
    violations: List[Dict[str, object]] = []
    first_after: Dict[int, Dict[str, object]] = {}
    relearned = 0
    ids_reused = 0
    for i, r in maker:
        sq = r.get("seq") if r.get("seq") is not None else ("row", i)
        m, sc, ws = str(r.get("moment")), r.get("scene"), r.get("world_seed")
        was_seen = sq in seen
        expected = seen[sq][0] if was_seen else len(seen)
        name_reused = m in first_seq_of_name and first_seq_of_name[m] != sq
        for ri in resumes:
            if ri < i and ri not in first_after:
                first_after[ri] = {"resume_row": ri, "resumed_from_seq": rows[ri].get("resumed_from_seq"), "seq": r.get("seq"), "moment": m, "scene": sc, "world_seed": ws,
                                   "replayed": was_seen, "name_reused": name_reused, "expected": expected,
                                   "ok": sc == expected and (world_seed is None or ws == world_seed)}
        if world_seed is not None and ws != world_seed:
            violations.append({"kind": "world_seed", "row": i, "seq": r.get("seq"), "moment": m, "got": ws, "expected": world_seed})
        if was_seen:
            relearned += 1
            if (seen[sq][0], seen[sq][1]) != (sc, ws):
                violations.append({"kind": "relearned_row_differs", "row": i, "seq": r.get("seq"), "moment": m, "was": [seen[sq][0], seen[sq][1]], "now": [sc, ws]})
        else:
            if sc != len(seen):
                violations.append({"kind": "count_does_not_continue", "row": i, "seq": r.get("seq"), "moment": m, "scene": sc, "expected": len(seen)})
            if name_reused:
                ids_reused += 1
            seen[sq] = (sc, ws, m)
        first_seq_of_name.setdefault(m, sq)
    order: List[str] = []
    seen_all: set = set()
    for i, r in enumerate(rows):
        if _is_learn(r):
            sq = r.get("seq") if r.get("seq") is not None else ("row", i)
            if sq not in seen_all:
                seen_all.add(sq)
                order.append(str(r.get("world") or "scene"))
    cen: List[Dict[str, object]] = []
    for n in sorted(census):
        c = census[n]
        by = c.get("scenes_by_world") if isinstance(c, dict) else None
        if not isinstance(by, dict) or c.get("scenes") != n:
            e = {"scenes": n, "ok": False, "why": "the file is unreadable or its scenes do not match its name"}
        elif len(order) < n:
            e = {"scenes": n, "ok": False, "why": f"the journal holds fewer distinct learned tape rows ({len(order)}) than the census counts ({n})"}
        else:
            mk_exp, sc_exp = order[:n].count(MAKER), n - order[:n].count(MAKER)
            mk_got, sc_got = int(by.get(MAKER, 0)), int(by.get("scene", 0))
            e = {"scenes": n, "maker_expected": mk_exp, "maker_got": mk_got, "scene_expected": sc_exp, "scene_got": sc_got,
                 "ok": mk_exp == mk_got and sc_exp == sc_got, "why": ""}
        cen.append(e)
        if not e["ok"]:
            violations.append({"kind": "census", **e})
    maker_ix = [i for i, _ in maker]
    bracketed = [ri for ri in resumes if any(i < ri for i in maker_ix) and any(i > ri for i in maker_ix)]   # a resume with maker rows on BOTH sides is gradable
    return {"resumes": len(resumes), "resume_rows": resumes, "bracketed_resumes": len(bracketed), "maker_rows": len(maker), "maker_tape_rows": len(seen),
            "maker_moments": len({str(r.get("moment")) for _, r in maker}), "moment_ids_reused": ids_reused, "relearned_rows": relearned,
            "maker_rows_before_first_resume": (sum(1 for i, _ in maker if i < resumes[0]) if resumes else 0),
            "maker_rows_after_last_resume": (sum(1 for i, _ in maker if i > resumes[-1]) if resumes else 0),
            "first_maker_row_after_each_resume": [first_after[k] for k in sorted(first_after)], "census": cen, "violations": violations}


def run_controls(rows: Sequence[Dict[str, object]], world_seed: Optional[int], census: Dict[int, Dict[str, object]]) -> Dict[str, str]:
    """Three plants the check must CATCH and one it must READ AS NEW, on copies of the real inputs (each must change the inputs)."""
    out: Dict[str, str] = {}

    def attempt(name: str, prows, pcensus) -> None:
        changed = json.dumps(prows, sort_keys=True) != json.dumps(list(rows), sort_keys=True) or json.dumps(pcensus, sort_keys=True) != json.dumps(census, sort_keys=True)
        res = check(prows, world_seed, pcensus)
        out[name] = "CAUGHT" if (changed and res["violations"]) else "MISSED"

    resumes = [i for i, r in enumerate(rows) if r.get("event") == "start" and int(r.get("resumed_from_seq") or 0) > 0]
    after = [i for i, r in enumerate(rows) if resumes and i > resumes[-1] and _is_learn(r) and r.get("world") == MAKER]
    if after:
        p = copy.deepcopy(list(rows))
        p[after[0]]["scene"] = 0 if p[after[0]].get("scene") != 0 else 1
        attempt("reset", p, census)
    else:
        out["reset"] = "NOT RUN"
    first = next((i for i, r in enumerate(rows) if _is_learn(r) and r.get("world") == MAKER), None)
    if first is not None and world_seed is not None:
        p = copy.deepcopy(list(rows))
        p[first]["world_seed"] = int(p[first].get("world_seed") or 0) + 1
        attempt("seed", p, census)
    else:
        out["seed"] = "NOT RUN"
    if census:
        c = copy.deepcopy(census)
        last = max(c)
        by = dict(c[last].get("scenes_by_world") or {})
        by[MAKER] = int(by.get(MAKER, 0)) + 1
        c[last] = {**c[last], "scenes_by_world": by}
        attempt("census", list(rows), c)
    else:
        out["census"] = "NOT RUN"
    if first is not None:
        base = check(rows, world_seed, census)
        top = max([int(r["seq"]) for r in rows if r.get("seq") is not None] or [0])
        mk = [r for r in rows if _is_learn(r) and r.get("world") == MAKER]
        planted = {**copy.deepcopy(mk[-1]), "moment": mk[0].get("moment"), "seq": top + 1, "scene": base["maker_tape_rows"]}   # an EARLIER name, an UNSEEN seq, the next index
        res = check(list(rows) + [planted], world_seed, census)
        ok = (len(res["violations"]) == len(base["violations"]) and res["maker_tape_rows"] == base["maker_tape_rows"] + 1
              and res["moment_ids_reused"] == base["moment_ids_reused"] + 1)
        out["redrawn"] = "NEW" if ok else "MISREAD"
    else:
        out["redrawn"] = "NOT RUN"
    return out


def analyse_root(root) -> Dict[str, object]:
    root = Path(root)
    rows, torn = read_journal(root)
    gp = root / "GENOME.genome"
    if not gp.exists():
        raise D2Error(f"{gp} is missing: the derived seed cannot be computed")
    seed = int(parse_genome(gp.read_text()).seed)
    ws = world_seed_of(seed, MAKER)
    census = read_census(root)
    res = check(rows, ws, census)
    gradable = bool(res["bracketed_resumes"])
    res.update({"root": str(root), "journal_rows": len(rows), "torn_lines": torn, "genome_seed": seed, "world_seed_expected": ws, "census_files": len(census),
                "controls": run_controls(rows, ws, census), "gradable": gradable})
    why = ""
    if res["violations"]:
        verdict = "FAIL"
    elif not gradable:
        verdict = "NOT GRADABLE"
        why = ("no resume event in the journal" if not res["resumes"] else "no resume has a maker learn row both before and after it")
    else:
        verdict = "PASS"
    if verdict == "PASS" and any(v in ("MISSED", "MISREAD") for v in res["controls"].values()):
        verdict, why = "FAIL", "a control was MISSED or MISREAD: the read is blind to a fault it was planted with, or false-alarms on a redrawn canvas"
    res["verdict"], res["why"] = verdict, why
    return res


def report(r: Dict[str, object]) -> List[str]:
    L = [f"D2 · HEARS-2 pre-flight read of {r['root']} (read-only; a learn event is a TAPE ROW, its seq — AMENDMENT 3)",
         f"  journal rows {r['journal_rows']} (torn lines {r['torn_lines']}) · resume events {r['resumes']} at rows {r['resume_rows']} (with maker rows on both sides: {r['bracketed_resumes']}) · maker learn rows "
         f"{r['maker_rows']} on {r['maker_tape_rows']} tape rows (before the first resume {r['maker_rows_before_first_resume']}, after the last {r['maker_rows_after_last_resume']}) · rows journaled twice "
         f"(same seq) {r['relearned_rows']} · maker tape rows that REUSE a name an earlier row had {r['moment_ids_reused']} of {r['maker_tape_rows']} ({r['maker_moments']} distinct names: the maker redraws its first "
         f"pictures after a restart; not a fault)"]
    for f in r["first_maker_row_after_each_resume"]:
        L.append(f"  (a) the count continues: the first maker row after the resume at row {f['resume_row']} (resumed_from_seq {f['resumed_from_seq']}): seq {f['seq']} {f['moment']} scene {f['scene']} "
                 f"({'a row re-consumed: its earlier index' if f['replayed'] else 'a NEW tape row' + (' under a name used before' if f['name_reused'] else '') + ': one past the distinct maker rows so far'} {f['expected']}) "
                 f"→ {'ok' if f['ok'] else 'WRONG'}")
    if not r["first_maker_row_after_each_resume"]:
        L.append("  (a) no maker row after any resume: nothing to read")
    bad = r["violations"]
    L.append(f"  (b) every tape row journaled twice carries the same scene and world_seed, every new seq the next index, every maker row world_seed_of({r['genome_seed']}, maker) = "
             f"{r['world_seed_expected']}: violations {len([v for v in bad if v['kind'] != 'census'])}")
    for v in [v for v in bad if v["kind"] != "census"][:6]:
        L.append(f"      {json.dumps(v, sort_keys=True)}")
    L.append("  (c) census files against the journal: " + (" · ".join(f"{c['scenes']}: maker {c.get('maker_expected', '?')} vs {c.get('maker_got', '?')} {'ok' if c['ok'] else 'WRONG ' + str(c['why'])}"
                                                                     for c in r["census"]) or "no census file"))
    L.append("  controls (planted on the real rows; CAUGHT = the check fired, NEW = a redrawn canvas was read as new): " + " · ".join(f"{k} {v}" for k, v in r["controls"].items()))
    L.append(f"D2 {r['verdict']}" + (f": {r['why']}" if r["why"] else (f": {len(bad)} violations" if bad else "")))
    return L


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="hears_d2_read")
    ap.add_argument("root")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        r = analyse_root(a.root)
    except D2Error as e:
        print(f"hears_d2_read: {e}", file=sys.stderr)
        return 2
    print("\n".join(report(r)))
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=1, sort_keys=True, default=str))
    return {"PASS": 0, "FAIL": 1, "NOT GRADABLE": 3}[r["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
