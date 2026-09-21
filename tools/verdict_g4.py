#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-20 12:35 +0400 — THE VERDICT READER for G4 (docs/G4-PREREG.md §5 as amended by §10, §12, §14, §15, §16).
# Written BEFORE the verdict exists (#158/#214: the reader is pre-registered; its rules are §16), dry-run on life 1's CLOSED
# root as its control (life 1's known defects must show: (iv) refused 435, (vi) unreadable). Read-only on every root (#212):
# the tape is concatenated into --out, the state is COPIED, every twin lives in its own fresh root under --out.
"""usage: python3 tools/verdict_g4.py --root <run root> --genome genome/G4.genome --out runs/g4-verdict-<stamp>
          [--hours 24] [--random 20] [--slice-hours 6] [--workers 8] [--nrestarts N] [--cpu-ns N] [--unit creature.service]
          [--skip-twins] [--skip-random]
       python3 tools/verdict_g4.py --worker <spec.json>            (one twin: replay -> snapshot -> self-exam -> summary.json)
"""
from __future__ import annotations
import argparse, json, os, shutil, statistics, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np

BLINDS = ["gaze", "sleep", "predict", "curiosity", "park", "frozen"]
REUSE = False   # --reuse: read existing twin summaries under --out instead of replaying them
WINDOW_SECONDS = 6 * 3600


def _iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read_jsonl(p: Path) -> List[dict]:
    """A journal/tape file the body may still be APPENDING to (tomorrow's live root): tolerate exactly ONE trailing partial line
    (dropped, named on stderr); a torn line anywhere else is corruption and raises. (edit: Claude (Fable 5.1), 2026-09-20 13:21 +0400 — robustness, not a bar.)"""
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    out: List[dict] = []
    for i, l in enumerate(lines):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                print(f"read_jsonl: dropped a trailing partial line in {p} ({len(l)} bytes, being written)", file=sys.stderr)
                break
            raise
    return out


# ----------------------------------------------------------------------------- the tape and the journal, cut at --hours
def _relink(link: Path, target: Path) -> None:
    """A payload symlink under the reader's own --out points at the CURRENT root's payload dir. Life 2's out dir was
    written while its root was `run/`; after the close (`mv run run-g4-life2-…`) the old link pointed into LIFE 3's
    `run/tape/payload` — a silent cross-life read for the solo probe and the plant (found 2026-09-21 14:0x, the v2
    control). A link is re-pointed when its target differs; a real directory is left alone."""
    if link.is_symlink():
        if os.readlink(link) != str(target):
            link.unlink(); os.symlink(target, link)
    elif not link.exists():
        os.symlink(target, link)


def gather(root: Path, out: Path, hours: float) -> dict:
    """Concatenates the root's tape files in seq order into out/tape/ALL.jsonl (payload symlinked, never copied), cut at
    start + hours; copies the state (a snapshot COPY); reads the journal's mind rows and event rows up to the cut."""
    tape_rows = []
    for f in sorted((root / "tape").glob("*.jsonl")):
        tape_rows += read_jsonl(f)
    tape_rows.sort(key=lambda r: r["seq"])
    assert [r["seq"] for r in tape_rows] == list(range(1, len(tape_rows) + 1)), "tape seqs are not 1..N"
    journal = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        journal += read_jsonl(f)
    events = [r for r in journal if "event" in r]
    starts = [e for e in events if e["event"] == "start"]
    assert starts, "no start event in the journal"
    t0 = _iso(starts[0]["at"])
    t_cut = t0 + timedelta(hours=hours)
    tape_cut = [r for r in tape_rows if _iso(r["at"]) <= t_cut]
    last_seq = tape_cut[-1]["seq"] if tape_cut else 0
    mind_rows = [r for r in journal if "event" not in r and int(r["seq"]) <= last_seq]
    events_cut = [e for e in events if _iso(e["at"]) <= t_cut or e["event"] == "stop"]
    (out / "tape").mkdir(parents=True, exist_ok=True)
    pl = out / "tape" / "payload"
    _relink(pl, (root / "tape" / "payload").resolve())   # §18: a --reuse after the root MOVED must not read another life's payloads
    (out / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in tape_cut))
    (out / "live-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    st = out / "live-state"; st.mkdir(exist_ok=True)
    for f in ("organism.npz", "organism.json", "ledger.json"):
        shutil.copy2(root / "state" / f, st / f)
    status = json.loads((root / "STATUS.json").read_text()) if (root / "STATUS.json").exists() else {}
    exams = []
    for f in sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit()):
        d = json.loads(f.read_text())
        if _iso(d["at"]) <= t_cut:
            d["_file"] = f.name; exams.append(d)
    return {"t0": t0, "t_cut": t_cut, "tape": tape_cut, "mind": mind_rows, "events": events_cut, "status": status, "exams": exams,
            "last_seq": last_seq, "hours_on_tape": (_iso(tape_cut[-1]["at"]) - t0).total_seconds() / 3600 if tape_cut else 0.0}


# ----------------------------------------------------------------------------- ALIVE
def alive(G: dict, hours: float, nrestarts: Optional[int]) -> dict:
    t0 = G["t0"]; at = {r["seq"]: _iso(r["at"]) for r in G["tape"]}
    n_hours = int(np.ceil(G["hours_on_tape"])) or 1
    per = {h: {"canvases": 0, "thinks": 0, "sleeps": 0, "snapshots": 0, "exams": 0} for h in range(n_hours)}
    for r in G["mind"]:
        h = int((at[int(r["seq"])] - t0).total_seconds() // 3600)
        if h not in per: continue
        if "moment" in r: per[h]["canvases"] += 1
        elif "think" in r: per[h]["thinks"] += 1
        elif "sleep" in r: per[h]["sleeps"] += 1
    for e in G["events"]:
        h = int((_iso(e["at"]) - t0).total_seconds() // 3600)
        if h in per and e["event"] in ("snapshot", "exam"): per[h][e["event"] + "s"] += 1
    gaps = []
    for sense in ("eye", "ear"):
        ts = [at[r["seq"]] for r in G["tape"] if r["sense"] == sense]
        gaps.append(max((b - a).total_seconds() for a, b in zip(ts, ts[1:])) if len(ts) > 1 else 0.0)
    restarts = [e for e in G["events"] if e["event"] == "sense_restart"]
    crashes = [e for e in G["events"] if e["event"] == "crash"] + ([G["status"]] if G["status"].get("crash") else [])
    stops = [e for e in G["events"] if e["event"] == "stop" and _iso(e["at"]) < G["t_cut"]]
    hours_full = [h for h in per if h < int(hours)]
    moved = all(all(per[h][k] > 0 for k in ("canvases", "thinks", "snapshots", "sleeps")) for h in hours_full) if hours_full else False
    ok = (G["hours_on_tape"] >= hours - 1 / 60) and moved and (max(gaps) <= 60.0) and not crashes and not stops and (nrestarts in (0, None))
    return {"pass": bool(ok), "hours_on_tape": round(G["hours_on_tape"], 3), "bar_hours": hours, "per_hour": per, "every_counter_moved_every_hour": moved,
            "max_gap_s_eye_ear": [round(g, 1) for g in gaps], "sense_restarts": len(restarts), "crashes": len(crashes), "stops_before_cut": len(stops),
            "nrestarts": nrestarts, "note": "NRestarts read from systemd (--nrestarts / --unit); None = not read"}


# ----------------------------------------------------------------------------- twins (one worker per twin, a fresh root each)
def worker(spec_path: Path) -> int:
    spec = json.loads(Path(spec_path).read_text())
    from creature.mind import Mind
    from genome.machinery import Organism, parse_genome
    from genome.predict import Predictor
    from genome.questions import build_ledgers
    root = Path(spec["root"]); (root / "tape").mkdir(parents=True, exist_ok=True)
    src_tape = Path(spec["tape"])
    _relink(root / "tape" / "payload", (src_tape.parent / "payload").resolve())
    rows = read_jsonl(src_tape)
    if spec.get("until_seq"):
        rows = [r for r in rows if r["seq"] <= spec["until_seq"]]
    if spec.get("shuffle_words"):
        # T-shuffle: the ear's words permuted across canvases by a fixed rng (the sight stream untouched)
        ears = [i for i, r in enumerate(rows) if r["sense"] == "ear"]
        words = [rows[i]["meta"]["word"] for i in ears]
        perm = np.random.default_rng(5).permutation(len(words))
        for i, j in zip(ears, perm):
            rows[i] = dict(rows[i]); rows[i]["meta"] = dict(rows[i]["meta"]); rows[i]["meta"]["word"] = words[j]
    (root / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))   # self_exam's disjointness control reads it
    genome_path = Path(spec["genome"])
    if spec.get("one_glance"):
        # edit: Claude (Fable 5.1), 2026-09-20 13:03 +0400 — PREREG §16 addendum: G1's T-one-glance = gaze mode "one" (the whole canvas at
        # glance×glance, one feature vector), forced on every glances() call of THIS worker process — the mind's learning road and
        # the exam's held-out alike — without touching creature code (the mind hardcodes surprise/random).
        from genome import gaze as _gaze
        _orig = _gaze.glances
        _gaze.glances = lambda rgb, spec_, g, mode="surprise", pic_id="": _orig(rgb, spec_, g, "one", pic_id)
    mind = Mind(genome_path, root, blind=frozenset(spec.get("blind", [])))
    if spec.get("nowire"):
        mind.org = Organism(mind.genome, wire=False)
        if mind.predictor is not None: mind.predictor = Predictor(mind.org)
    t0 = time.perf_counter(); n_canvas = 0; errs = []
    for r in rows:
        mind.consume(r)
    secs = time.perf_counter() - t0
    mind.snapshot()
    org = mind.org
    L = build_ledgers(org, mind.moment_word)
    def _cross(log):
        return sum(1 for _m, sc, wc in log if L["sight"].get(sc, set()) != L["words"].get(wc, set()))
    mind_rows = []
    for f in sorted((root / "journal").glob("*.jsonl")):
        mind_rows += [r for r in read_jsonl(f) if "event" not in r]
    (root / "mind-journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in mind_rows))
    n_canvas = sum(1 for r in mind_rows if "moment" in r)
    summary = {"label": spec["label"], "arrivals": org.arrivals, "budget_left": org.budget_left, "births": len(org.births), "c": org.c,
               "cells": [int(org.sight.alive.sum()), int(org.words.alive.sum())], "cells_born": org.sight.n + org.words.n,
               "edges_cross": {"born": _cross(org.edges_log), "pruned": _cross(org.prunes_log), "born_total": len(org.edges_log), "pruned_total": len(org.prunes_log)},
               "sleeps": sum(1 for r in mind_rows if "sleep" in r), "thinks": sum(1 for r in mind_rows if "think" in r),
               "parked": sum(1 for r in mind_rows if "think" in r and r["think"].get("parked")),
               "canvases": n_canvas, "seconds": round(secs, 1), "ms_per_canvas": round(1000 * secs / max(1, n_canvas), 2), "hash": org.state_hash()}
    if spec.get("one_glance"):
        from tools import self_exam as _se           # in-process, so the forced mode "one" applies to the held-out glances too
        old_argv = sys.argv
        try:
            sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"]
            _se.main()
        finally:
            sys.argv = old_argv
        summary["exam_stderr"] = ""
    else:
        ex = subprocess.run([sys.executable, str(ROOT / "tools" / "self_exam.py"), "--root", str(root), "--genome", str(genome_path), "--held", "10", "--check-tape", "400"],
                            capture_output=True, text=True, cwd=ROOT)
        summary["exam_stderr"] = ex.stderr[-500:] if ex.returncode else ""
    exams = sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit())
    summary["exam"] = json.loads(exams[-1].read_text()) if exams else None
    (root / "summary.json").write_text(json.dumps(summary, default=str))
    return 0


def run_workers(specs: List[dict], workers: int, out: Path) -> Dict[str, dict]:
    procs = []; pending = list(specs); done: Dict[str, dict] = {}
    while pending or procs:
        while pending and len(procs) < workers:
            s = pending.pop(0); sp = out / "specs" / (s["label"] + ".json"); sp.parent.mkdir(exist_ok=True)
            sf0 = Path(s["root"]) / "summary.json"
            if REUSE and sf0.exists():
                done[s["label"]] = json.loads(sf0.read_text()); print(f"  twin {s['label']}: reused", flush=True); continue
            sp.write_text(json.dumps(s)); log = open(out / "specs" / (s["label"] + ".log"), "w")
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker", str(sp)], stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
            procs.append((s, p, log))
        time.sleep(2.0)
        still = []
        for s, p, log in procs:
            if p.poll() is None: still.append((s, p, log)); continue
            log.close(); sf = Path(s["root"]) / "summary.json"
            done[s["label"]] = json.loads(sf.read_text()) if sf.exists() else {"label": s["label"], "error": f"worker exit {p.returncode}"}
            print(f"  twin {s['label']}: exit {p.returncode}" + ("" if sf.exists() else " (no summary)"), flush=True)
        procs = still
    return done


def genome_twin_text(base_text: str, label: str, numbers: Optional[dict] = None, fixations: Optional[int] = None, frozen_after: Optional[int] = None) -> str:
    """A genome-TEXT twin: the same file with its numbers replaced (random genomes, (ix)) or GAZE fixations 1 ((xi))."""
    import re
    lines = base_text.splitlines()
    out = []
    for line in lines:
        s = line.split("#")[0].rstrip(); head = s.split()
        if numbers:
            n = numbers
            if head[:2] == ["BIRTH", "novelty"]: line = f"BIRTH    novelty  cos<{n['theta_n']:.4f}"
            elif head[:2] == ["BIRTH", "error"]: line = f"BIRTH    error    misfires {n['misfires']}"
            elif head[:1] == ["BUDGET"]: line = f"BUDGET   {n['budget']} per arrival"
            elif head[:1] == ["KWTA"]: line = f"KWTA     {n['kwta']}"
            elif head[:1] == ["DELTA"]: line = f"DELTA    lr {n['lr']:.4f}"
            elif head[:1] == ["PRUNE"]: line = re.sub(r"w<[0-9.]+", f"w<{n['prune_floor']:.4f}", line.split("#")[0]).rstrip()
            elif head[:1] == ["MERGE"]: line = f"MERGE    cos>{n['theta_m']:.4f} same-answer"
            elif head[:1] == ["SCALE"]: line = f"SCALE    every {n['scale_every']} moments"
            elif head[:2] == ["STAGE", "1"]: line = f"STAGE    1 senses   moments 0..{n['stage1']}"
            elif head[:2] == ["STAGE", "2"]: line = f"STAGE    2 meet     moments {n['stage1']}.."
            elif head[:1] == ["ABSTAIN"]: line = f"ABSTAIN  second/best > {n['abstain_ratio']:.3f}"
        if fixations is not None and head[:1] == ["GAZE"]:
            line = re.sub(r"fixations \d+", f"fixations {fixations}", line.split("#")[0]).rstrip()
        if frozen_after is not None and head[:1] == ["FROZEN"]:
            line = f"FROZEN   after {frozen_after} cells"
        out.append(line)
    return f"# {label} — a genome-text twin written by tools/verdict_g4.py (PREREG §16)\n" + "\n".join(out) + "\n"


# ----------------------------------------------------------------------------- the reader's own asks on an organism
def own_asks(root: Path, genome_path: Path) -> dict:
    """The plant (zog), the null plant (vex), random landing and the ceiling numbers — self_exam does not ask the plant."""
    from tools import self_exam
    from genome import world, run_g1
    from genome.questions import ask_plant_glances
    g, org, ledgers, L = self_exam.load_snapshot(root, genome_path)
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], 10, np.random.default_rng(2))
    held_g = run_g1.glance_held(held, g, "surprise"); feats = run_g1.feats_only(held_g)
    h0 = org.state_hash()
    plant = ask_plant_glances(org, ledgers, world.THING_PLANT, feats[world.THING_PLANT])
    null = ask_plant_glances(org, ledgers, world.THING_NULL, feats[world.THING_NULL])
    rnd = run_g1.landing(run_g1.glance_held(held, g, "random"), things, first=2)
    assert org.state_hash() == h0
    return {"plant": plant, "null": null, "random_landing": rnd}


# ----------------------------------------------------------------------------- MODULATION (§10 verbatim, on the life's own err series)
def modulation(G: dict, F: float) -> dict:
    # edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400 — §18: MODULATION reads the DRAWN world only (maker moments "w…"); a folder row's moment is "f<sha>" and its word is a folder name
    mind = [r for r in G["mind"] if "moment" in r and r.get("word") and str(r["moment"]).startswith("w")]
    win = lambda r: int(r["moment"][1:5])
    by_seq = {int(r["seq"]): r for r in mind}
    out = {"F": F, "settle_bar": "err at the 10th showing ≤ 1.25 × the pre-window last-50 median (§16 addendum); the toy's F+.05 = %.4f printed per thing" % (F + 0.05), "windows": {}}
    seen_before: set = set()
    cur = None; idx = 0
    for i, r in enumerate(mind):
        w = win(r)
        if cur is None: cur = w
        if w != cur:
            prev = mind[max(0, i - 50):i]
            last50 = float(np.median([p["err"] for p in prev])) if prev else 0.0
            words_here = []
            for q in mind[i:]:
                if win(q) != w: break
                words_here.append(q)
            new = sorted({q["word"] for q in words_here} - seen_before)
            returning = sorted({q["word"] for q in words_here} & seen_before - {q["word"] for q in prev})
            rec = {"at_seq": int(r["seq"]), "last50_med": round(last50, 4), "new_things": new, "returning_things": returning, "per_thing": {}}
            for t in new + returning:
                errs = [q["err"] for q in words_here if q["word"] == t]
                if len(errs) < 3: continue
                first3 = float(np.median(errs[:3])); tenth = errs[9] if len(errs) >= 10 else None
                rec["per_thing"][t] = {"kind": "new" if t in new else "returning", "first3_med": round(first3, 4),
                                       "spike_ratio": round(first3 / last50, 2) if last50 > 0 else None, "spike": bool(last50 > 0 and first3 >= 3 * last50),
                                       "err_10th": round(tenth, 4) if tenth is not None else None, "settled": bool(tenth is not None and last50 > 0 and tenth <= 1.25 * last50),
                                       "settled_toy_bar_F_plus_05": bool(tenth is not None and tenth < F + 0.05)}
            out["windows"][str(w)] = rec
            cur = w
        seen_before.add(r["word"])
    # the null: a FAKE boundary at the middle of window 0 — things continuing; the same statistic must show no spike (< 1.5x)
    w0 = [r for r in mind if win(r) == 0]
    if len(w0) > 200:
        m = len(w0) // 2; prev = w0[m - 50:m]; last50 = float(np.median([p["err"] for p in prev]))
        per = {}
        for t in sorted({q["word"] for q in w0[m:]}):
            errs = [q["err"] for q in w0[m:] if q["word"] == t][:3]
            if len(errs) == 3: per[t] = round(float(np.median(errs)) / last50, 2) if last50 > 0 else None
        out["null_fake_boundary_w0"] = {"at_seq": int(w0[m]["seq"]), "last50_med": round(last50, 4), "spike_ratio_per_thing": per,
                                        "no_spike": all(v is not None and v < 1.5 for v in per.values()) if per else None}
    # grading: at every window that brings NEW things — majority of the new things spike AND settle (B13's reading, §12)
    graded = []
    for w, rec in out["windows"].items():
        news = [v for v in rec["per_thing"].values() if v["kind"] == "new"]
        if not news: continue
        sp = sum(v["spike"] for v in news); st = sum(v["settled"] for v in news)
        graded.append({"window": w, "new": len(news), "spike": sp, "settled": st, "pass": sp * 2 > len(news) and st * 2 > len(news)})
    out["graded_windows"] = graded
    out["pass"] = bool(graded) and all(x["pass"] for x in graded) and bool(out.get("null_fake_boundary_w0", {}).get("no_spike"))
    return out


# ----------------------------------------------------------------------------- main
def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker"); ap.add_argument("--root"); ap.add_argument("--genome", default=str(ROOT / "genome" / "G4.genome"))
    ap.add_argument("--out"); ap.add_argument("--hours", type=float, default=24.0); ap.add_argument("--random", type=int, default=20)
    ap.add_argument("--slice-hours", type=float, default=6.0); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--nrestarts", type=int); ap.add_argument("--cpu-ns", type=int); ap.add_argument("--unit")
    ap.add_argument("--skip-twins", action="store_true"); ap.add_argument("--skip-random", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="re-grade: read twin summaries already under --out instead of replaying")
    a = ap.parse_args(argv)
    global REUSE; REUSE = bool(a.reuse)
    if a.worker:
        return worker(Path(a.worker))
    T0 = time.perf_counter()
    root = Path(a.root).resolve(); genome_path = Path(a.genome).resolve(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    from genome.machinery import parse_genome
    from genome import run_g0, world
    g = parse_genome(genome_path.read_text())
    R: Dict[str, object] = {"root": str(root), "genome": str(genome_path), "genome_sha": __import__("hashlib").sha256(genome_path.read_bytes()).hexdigest()[:16],
                            "reader": "tools/verdict_g4.py v2 (PREREG §18: W3-2, DOOR, W3-1, PARK graded; two-sense hardening)", "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "hours": a.hours}
    nrestarts, cpu_ns = a.nrestarts, a.cpu_ns
    if a.unit:
        try:
            sh = subprocess.run(["systemctl", "--user", "show", a.unit, "-p", "NRestarts", "-p", "CPUUsageNSec"], capture_output=True, text=True).stdout
            kv = dict(l.split("=", 1) for l in sh.strip().splitlines())
            nrestarts = int(kv.get("NRestarts", nrestarts or 0)); cpu_ns = int(kv.get("CPUUsageNSec", cpu_ns or 0))
        except Exception as e:
            R["unit_read_error"] = str(e)
    print(f"[gather] root {root} cut at {a.hours} h", flush=True)
    G = gather(root, out, a.hours)
    R["tape_rows"] = len(G["tape"]); R["mind_rows_live"] = len(G["mind"]); R["exams_in_window"] = [e["_file"] for e in G["exams"]]
    R["ALIVE"] = alive(G, a.hours, nrestarts)
    print(f"[ALIVE] {R['ALIVE']['pass']} hours {R['ALIVE']['hours_on_tape']} moved {R['ALIVE']['every_counter_moved_every_hour']} gaps {R['ALIVE']['max_gap_s_eye_ear']}", flush=True)

    tape_all = out / "tape" / "ALL.jsonl"
    twins_dir = out / "twins"; twins_dir.mkdir(exist_ok=True)
    base_text = genome_path.read_text()
    first_fix = twins_dir / "first-fixation.genome"; first_fix.write_text(genome_twin_text(base_text, "T-first-fixation", fixations=1))
    frozen10 = twins_dir / "frozen-10.genome"; frozen10.write_text(genome_twin_text(base_text, "T-frozen-10", frozen_after=10))
    specs = [{"label": "unblinded-1", "root": str(twins_dir / "unblinded-1"), "tape": str(tape_all), "genome": str(genome_path)},
             {"label": "unblinded-2", "root": str(twins_dir / "unblinded-2"), "tape": str(tape_all), "genome": str(genome_path)}]
    if not a.skip_twins:
        specs += [{"label": f"blind-{b}", "root": str(twins_dir / f"blind-{b}"), "tape": str(tape_all), "genome": str(genome_path), "blind": [b]} for b in BLINDS]
        specs += [{"label": "T-shuffle", "root": str(twins_dir / "T-shuffle"), "tape": str(tape_all), "genome": str(genome_path), "shuffle_words": True},
                  {"label": "T-nowire", "root": str(twins_dir / "T-nowire"), "tape": str(tape_all), "genome": str(genome_path), "nowire": True},
                  {"label": "T-one-glance", "root": str(twins_dir / "T-one-glance"), "tape": str(tape_all), "genome": str(genome_path), "one_glance": True},
                  {"label": "T-first-fixation", "root": str(twins_dir / "T-first-fixation"), "tape": str(tape_all), "genome": str(first_fix)},
                  {"label": "T-frozen-10", "root": str(twins_dir / "T-frozen-10"), "tape": str(tape_all), "genome": str(frozen10), "blind": ["frozen"]}]
    # (ix): the first --slice-hours of the tape under 20 random genomes (numbers only, structure fixed) and under the creature's own
    slice_seq = 0
    for r in G["tape"]:
        if (_iso(r["at"]) - G["t0"]).total_seconds() <= a.slice_hours * 3600: slice_seq = r["seq"]
    if not a.skip_random:
        specs.append({"label": "slice-own", "root": str(twins_dir / "slice-own"), "tape": str(tape_all), "genome": str(genome_path), "until_seq": slice_seq})
        for seed in range(1, a.random + 1):
            rg = run_g0.random_genome(g, seed); nums = run_g0.genome_numbers(rg)
            gp = twins_dir / f"random-{seed}.genome"; gp.write_text(genome_twin_text(base_text, f"random genome seed {seed}", numbers=nums))
            parse_genome(gp.read_text())   # it must parse before it is spent on
            specs.append({"label": f"random-{seed}", "root": str(twins_dir / f"random-{seed}"), "tape": str(tape_all), "genome": str(gp), "until_seq": slice_seq, "numbers": nums})
    # G4-7's solo: the first 1,000 rows replayed ALONE before any worker starts (a replay under 8 workers is not solo)
    solo_ms = None
    try:
        from creature.mind import Mind
        sroot = out / "solo-probe"; (sroot / "tape").mkdir(parents=True, exist_ok=True)
        _relink(sroot / "tape" / "payload", (root / "tape" / "payload").resolve())
        sm = Mind(genome_path, sroot); srows = [r for r in G["tape"] if r["seq"] <= 1000]
        ts = time.perf_counter()
        for r in srows: sm.consume(r)
        solo_ms = round(1000 * (time.perf_counter() - ts) / max(1, sum(1 for r in srows if r["sense"] == "eye")), 2)
    except Exception as e:
        R["solo_probe_error"] = repr(e)
    R["solo_ms_per_canvas_probe"] = solo_ms
    print(f"[solo] {solo_ms} ms a canvas over the first 1,000 rows, alone", flush=True)
    print(f"[twins] {len(specs)} replays, {a.workers} workers, slice_seq {slice_seq}", flush=True)
    TW = run_workers(specs, a.workers, out)
    R["twins"] = TW

    # REPLAY + (vii): the unblinded replay vs the live journal, and the second unblinded replay vs the first; the planted divergence
    from creature import replay as replay_mod
    live = replay_mod.read_mind_journal(out / "live-journal.jsonl")
    u1 = replay_mod.read_mind_journal(twins_dir / "unblinded-1" / "mind-journal.jsonl")
    u2 = replay_mod.read_mind_journal(twins_dir / "unblinded-2" / "mind-journal.jsonl")
    d_live = replay_mod.compare(u1, live); d_two = replay_mod.compare(u1, u2)
    # the plant: the first 1,000 rows with one eye payload's thing inverted (its cell from the root's truth file) must DIVERGE
    plant_ok = None; plant_seq = None
    try:
        from PIL import Image
        rows = [r for r in G["tape"] if r["seq"] <= 1000]
        eye = [r for r in rows if r["sense"] == "eye" and (r.get("meta") or {}).get("source", "maker") == "maker"][300]   # §18: a folder picture has no truth file
        proot = out / "plant-root"; (proot / "tape").mkdir(parents=True, exist_ok=True); (proot / "tape" / "payload").mkdir(exist_ok=True)
        for r in rows:
            src = root / "tape" / r["payload"]; dst = proot / "tape" / r["payload"]
            if dst.is_symlink() or not dst.exists():
                _relink(dst, src.resolve())
        pp = proot / "tape" / eye["payload"]; pp.unlink()
        arr = np.array(Image.open(root / "tape" / eye["payload"]).convert("RGB"))
        truth = json.loads((root / "truth" / (Path(eye["payload"]).stem + ".json")).read_text())
        cy, cx = truth["cell"]; y0, x0 = max(0, min(int((cy + 0.5) * 8) - 12, 104)), max(0, min(int((cx + 0.5) * 8) - 12, 104))
        arr[y0:y0 + 24, x0:x0 + 24] = 255 - arr[y0:y0 + 24, x0:x0 + 24]; Image.fromarray(arr).save(pp, format="PNG")
        (proot / "tape" / "ALL.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        if (proot / "replay").exists(): shutil.rmtree(proot / "replay")   # §18: a --reuse re-grade recomputes the plant in the reader's own scratch (FileExistsError otherwise)
        pj = replay_mod.run_replay(genome_path, proot / "tape" / "ALL.jsonl", proot / "replay")
        dp = replay_mod.compare(replay_mod.read_mind_journal(pj), [r for r in live if int(r["seq"]) <= 1000])
        plant_ok = dp is not None; plant_seq = eye["seq"]; R["replay_plant_diverged_at"] = dp
    except Exception as e:
        R["replay_plant_error"] = repr(e)
    R["REPLAY"] = {"pass": d_live is None and d_two is None and plant_ok is True, "vs_live": d_live, "two_replays": d_two, "mind_rows": len(u1),
                   "plant_seq": plant_seq, "plant_caught": plant_ok}
    print(f"[REPLAY] {R['REPLAY']}", flush=True)

    # the organism at the cut = the unblinded replay's snapshot (byte-identical to the live one when REPLAY passes)
    own = own_asks(twins_dir / "unblinded-1", genome_path)
    R["own_asks"] = own
    U = TW["unblinded-1"]; E = U["exam"]; seen = E["ask_seen_words"]; allw = E["ask_all_words"]
    last_live_exam = G["exams"][-1] if G["exams"] else None
    def q(twin, key="Q1"):
        # §16 addendum 2: every TWIN is read on ask_all_words (the same 160-question denominator as the creature's all-words Q1) —
        # a twin that met only 2 words scored .75 on its own 20 questions and .094 on the 160 (the control run, 13:2x)
        t = TW.get(twin, {}); ex = t.get("exam") or {}; return (ex.get("ask_all_words") or {}).get(key, {}).get("acc")
    Q1_ALL = allw["Q1"]["acc"]
    M: Dict[str, dict] = {}
    M["i_knows"] = {"pass": seen["Q1"]["acc"] >= .80 and seen["Q2"]["acc"] >= .80 and seen["Q3"]["acc"] >= .85 and seen["Q4"]["acc"] >= .90,
                    "Q1": seen["Q1"]["acc"], "Q2": seen["Q2"]["acc"], "Q3": seen["Q3"]["acc"], "Q4": seen["Q4"]["acc"], "chance_Q1": E["chance_q1"],
                    "all_words": {k: allw[k]["acc"] for k in ("Q1", "Q2", "Q3", "Q4")}, "per_thing_Q1": seen["Q1"]["per_thing"],
                    "live_exam_last": {k: (last_live_exam["ask_seen_words"][k]["acc"] if last_live_exam else None) for k in ("Q1", "Q2", "Q3", "Q4")},
                    "bar": "Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90"}
    M["ii_meeting_real"] = {"pass": (q("T-shuffle") is not None and q("T-shuffle") <= .20) and (q("T-nowire") is not None and q("T-nowire") <= .20),
                            "T_shuffle_Q1": q("T-shuffle"), "T_nowire_Q1": q("T-nowire"), "bar": "≤ .20"}
    M["iii_growth_matters"] = {"pass": q("T-frozen-10") is not None and q("T-frozen-10") <= Q1_ALL - .30, "T_frozen_10_Q1": q("T-frozen-10"), "T_frozen_50_Q1": q("blind-frozen"),
                               "T_frozen_10_cells": TW.get("T-frozen-10", {}).get("cells"), "Q1": Q1_ALL, "bar": "≥ 30 pp under on all 16 words (the twin FROZEN after 10 cells, G0b's; the 50-cell twin printed — §16 addenda)"}
    c = U["c"]; pruned_share = c["edges_pruned"] / c["edges_born"] if c["edges_born"] else 0.0
    M["iv_grows_alone"] = {"pass": U["cells_born"] >= 50 and c["births_refused_budget"] == 0 and pruned_share >= .05 and c["removed_for_disuse"] == 0,
                           "cells_born": U["cells_born"], "births_refused_budget": c["births_refused_budget"], "arrivals": U["arrivals"], "budget_left": U["budget_left"],
                           "pruned_share": round(pruned_share, 4), "edges_born": c["edges_born"], "edges_pruned": c["edges_pruned"], "edges_cross": U["edges_cross"],
                           "removed_for_disuse": c["removed_for_disuse"], "bar": "≥ 50 born · 0 refused · ≥ 5 % pruned · 0 by disuse"}
    # (v) §15's pair: per odd window, the LAST exam inside it vs the LAST exam of the preceding even window, Q1 on the seen eleven
    seq_at = {r["seq"]: r for r in G["tape"]}
    def window_of(ex):
        s = ex.get("snapshot_last_seq") or 0
        # §18 hardening: walk back to the nearest MAKER row (a folder row's moment is "f<sha>", not a window)
        while s > 0 and (s not in seq_at or not str((seq_at[s].get("meta") or {}).get("moment", "")).startswith("w")): s -= 1
        return int(seq_at[s]["meta"]["moment"][1:5]) if s in seq_at else None
    by_w: Dict[int, List[dict]] = {}
    for ex in G["exams"]:
        w = window_of(ex)
        if w is not None: by_w.setdefault(w, []).append(ex)
    pairs = []
    for w in sorted(by_w):
        if w % 2 == 1 and (w - 1) in by_w:
            before = by_w[w - 1][-1]; first_after = by_w[w][0]; last_in = by_w[w][-1]
            q1 = lambda ex: ex["ask_seen_words"]["Q1"]["acc"]
            pairs.append({"window": w, "before": q1(before), "first_after": q1(first_after), "last_in_window": q1(last_in), "drop_pp": round(100 * (q1(before) - q1(last_in)), 1),
                          "files": [before["_file"], first_after["_file"], last_in["_file"]]})
    M["v_retention"] = {"pass": bool(pairs) and all(p["drop_pp"] <= 5.0 for p in pairs), "pairs": pairs, "bar": "≤ 5 pp on the last-of-window pair (§15)", "note": "no odd window with exams on both sides → not readable" if not pairs else ""}
    p, n = own["plant"], own["null"]
    M["vi_knows_unknown"] = {"pass": p["answered_rate"] > .5 and n["abstain_rate"] > .5 and (seen["Q5"][world.THING_NEVER]["abstain_rate"] >= .80) and seen["Q1"]["false_abstention"] <= .20,
                             "plant_zog": p, "null_vex": n, "Q5_spiral_abstain": seen["Q5"][world.THING_NEVER]["abstain_rate"], "false_abstention": seen["Q1"]["false_abstention"],
                             "bar": "plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20"}
    M["vii_replay"] = {"pass": R["REPLAY"]["pass"], **{k: v for k, v in R["REPLAY"].items() if k != "pass"}, "bar": "two replays byte-identical; the plant caught"}
    st = G["status"]; rss = st.get("rss_mb"); live_ms = st.get("mind_ms_median_1min"); solo_ms = R.get("solo_ms_per_canvas_probe") or U["ms_per_canvas"]
    M["viii_cost"] = {"pass": (rss is not None and rss < 2048) and (live_ms is None or solo_ms <= 0 or live_ms <= 2 * solo_ms),
                      "rss_mb_last_status": rss, "live_mind_ms_last_status": live_ms, "solo_ms_per_canvas_replay": solo_ms, "unblinded_replay_ms_under_workers": U["ms_per_canvas"],
                      "cpu_hours": round(cpu_ns / 3.6e12, 3) if cpu_ns else None, "bar": "G4-7: live median ≤ 2× solo · RSS < 2 GB (the 24 h CPU bill printed)"}
    if not a.skip_random:
        comps = []
        for k, t in TW.items():
            if k == "slice-own" or k.startswith("random-"):
                ex = t.get("exam") or {}; comp = (ex.get("ask_seen_words") or {}).get("composite")
                comps.append({"label": k, "composite": comp, "cells": t.get("cells"), "numbers": t.get("numbers")})
        ranked = sorted([x for x in comps if x["composite"] is not None], key=lambda x: -x["composite"])
        rank = next((i + 1 for i, x in enumerate(ranked) if x["label"] == "slice-own"), None)
        M["ix_not_luck"] = {"pass": rank is not None and rank <= max(1, len(ranked) // 4) + (1 if len(ranked) % 4 else 0) and rank <= 5,
                            "rank_of_own": rank, "of": len(ranked), "own_composite": next((x["composite"] for x in comps if x["label"] == "slice-own"), None),
                            "best_random": next((x for x in ranked if x["label"] != "slice-own"), None), "slice_seq": slice_seq, "bar": "top quartile of 20 random genomes (rank ≤ 5 of 21), numbers only, on the first slice"}
    lx = E["gaze_landing"]; lr = own["random_landing"]
    M["x_gaze_finds_thing"] = {"pass": lx["rate"] >= .90 and lx["rate"] >= 1.5 * lr["rate"], "gaze_rate": lx["rate"], "random_rate": lr["rate"], "random_ceiling_expected": 0.069,
                               "ratio": round(lx["rate"] / lr["rate"], 2) if lr["rate"] else None, "bar": "≥ .90 in the first 2 fixations · ≥ 1.5× random"}
    M["xi_gaze_earns_place"] = {"pass": q("T-one-glance") is not None and Q1_ALL - q("T-one-glance") >= .10, "Q1_gaze": Q1_ALL, "Q1_one_glance": q("T-one-glance"),
                                "Q1_first_fixation_only": q("T-first-fixation"), "Q1_random_gaze": q("blind-gaze"),
                                "bar": "≥ .10 over G1's one-glance twin (gaze mode 'one': the whole canvas at glance×glance); the first-fixation-only twin printed — §16 addendum"}
    F = 1.0 - g.theta_n
    M["MODULATION"] = modulation(G, F); M["MODULATION"]["bar"] = "§10 as amended §16: at every window bringing NEW things, a majority spike ≥ 3× the last-50 median and settle ≤ 1.25× it by the 10th showing; the fake-boundary null < 1.5×"
    np_err = None
    if "blind-predict" in TW and (twins_dir / "blind-predict" / "mind-journal.jsonl").exists():
        errs = [r["err"] for r in read_jsonl(twins_dir / "blind-predict" / "mind-journal.jsonl") if "moment" in r and "err" in r]
        np_err = {"max_err": max(errs) if errs else None, "n": len(errs)}
    M["MODULATION"]["no_predict_twin_err"] = np_err
    parked = U["parked"]
    M["PLANTS"] = {"vi": M["vi_knows_unknown"]["pass"], "predict_file_pair": "cannot fire on the maker's ear-then-eye stream (§14); predictions_filed " + str(st.get("predictions_filed")),
                   "park_unanswerable_want": "the folder door is OFF (§6)", "sleep_replay": {"sleeps": U["sleeps"], "no_sleep_twin_sleeps": TW.get("blind-sleep", {}).get("sleeps")},
                   "belief_contradiction": "clash unwired (§14)"}
    M["TWINS"] = {b: {"Q1": q(f"blind-{b}"), "Q1_seen": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_seen_words") or {}).get("Q1", {}).get("acc"),
                      "composite": ((TW.get(f"blind-{b}", {}).get("exam") or {}).get("ask_all_words") or {}).get("composite"), "cells": TW.get(f"blind-{b}", {}).get("cells")} for b in BLINDS}
    M["TWINS"]["random_gaze_loses_xi"] = {"pass": q("blind-gaze") is not None and Q1_ALL - q("blind-gaze") >= .10, "margin": None if q("blind-gaze") is None else round(Q1_ALL - q("blind-gaze"), 3)}
    M["TWINS"]["no_sleep_v"] = {"graded": False, "reason": "SLEEP's retention is not gradable on drawn worlds (§10)", "no_sleep_Q1": q("blind-sleep")}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door mark needs the folder/web door (OFF)"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "PARK unreadable (folder OFF)"}
    # ------------------------------------------------------------------ §18 (edit: Claude (Fable 5.1), 2026-09-21 13:21 +0400): W3-2, DOOR, W3-1, PARK graded
    decl = g.declared
    def _pred_rows(twin_root: Path) -> List[dict]:
        pth = twin_root / "state" / "predictions.jsonl"
        return read_jsonl(pth) if pth.exists() else []
    def _rule_stats(rows: List[dict]) -> dict:
        rules = [r for r in rows if ("cluster" in r or "shared" in r)]
        filed = [r for r in rules if r.get("accepted") and r.get("outcome") is None]
        refused = [r for r in rules if not r.get("accepted")]
        scored = [r for r in rules if r.get("outcome") in (True, False)]
        acc = (sum(1 for r in scored if r["outcome"] is True) / len(scored)) if scored else None
        words = sorted(set(str(r.get("word") or (r.get("words") or ["?"])[0]) for r in rules))
        sight_road = [r for r in rows if not ("cluster" in r or "shared" in r)]
        return {"filed": len(filed), "refused": len(refused), "scored": len(scored), "accuracy": None if acc is None else round(acc, 3), "words": words,
                "induce": sum(1 for r in rules if "cluster" in r), "deduce": sum(1 for r in rules if "shared" in r), "sight_road_rows": len(sight_road)}
    live_pred = _rule_stats(_pred_rows(twins_dir / "unblinded-1")); shuf_pred = _rule_stats(_pred_rows(twins_dir / "T-shuffle"))
    think_rows = [r for r in G["mind"] if "think" in r]
    parked_rules = sum(1 for r in think_rows if (r["think"] or {}).get("kind") == "rule" and (r["think"] or {}).get("parked"))
    rules_declared = ("INDUCE" in decl) or ("DEDUCE" in decl)
    chance = 1.0 / 11 + .10
    shuffle_ok = (shuf_pred["scored"] == 0) or (shuf_pred["accuracy"] is not None and shuf_pred["accuracy"] <= chance)
    M["W3_2_rules"] = {"graded": rules_declared,
                       "pass": rules_declared and live_pred["filed"] + live_pred["scored"] > 0 and live_pred["scored"] > 0 and (live_pred["accuracy"] or 0.0) >= .80 and shuffle_ok,
                       "live": live_pred, "T_shuffle": shuf_pred, "parked_rules": parked_rules, "shuffle_bar": "≤ 1/11 + .10 when any rule is scored; 0 scored = the shuffle destroyed the meeting (D's toy)",
                       "bar": "filed > 0 · scored > 0 · accuracy ≥ .80 (W3-2c's decider) · the shuffled-words twin at chance",
                       "reason": "" if rules_declared else "INDUCE/DEDUCE not declared in this life's genome — not graded"}
    tape = G["tape"]
    folder_rows = [r for r in tape if (r.get("meta") or {}).get("source") == "folder"]
    f_ear_moments = {(r.get("meta") or {}).get("moment") for r in folder_rows if r["sense"] == "ear"}
    f_pics = [r for r in folder_rows if r["sense"] == "eye"]
    sight_only = [r for r in f_pics if (r.get("meta") or {}).get("moment") not in f_ear_moments]
    folder_words = sorted({(r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"} - {None})
    recog = {}
    try:
        from tools import self_exam as _se2
        from genome import ask as _gask
        _g2, _org2, _led2, _L2 = _se2.load_snapshot(twins_dir / "unblinded-1", genome_path)
        _Lw2 = _led2["words"]; _h2 = _org2.state_hash()
        by_word: Dict[str, list] = {}
        for r in folder_rows:
            if r["sense"] == "ear": by_word.setdefault((r.get("meta") or {}).get("word"), [])
        moment_word = {(r.get("meta") or {}).get("moment"): (r.get("meta") or {}).get("word") for r in folder_rows if r["sense"] == "ear"}
        for r in f_pics:
            w = moment_word.get((r.get("meta") or {}).get("moment"))
            if w and len(by_word.get(w, [])) < 3: by_word.setdefault(w, []).append(r)
        for w, pics in by_word.items():
            hits = 0
            for r in pics:
                res = _org2.recall_many("sight", _gask.glance_picture(root / "tape" / r["payload"], _g2))
                ans = "/".join(sorted(_Lw2.get(res["cell"], set()))) if res.get("cell") is not None else None
                hits += int(ans == w)
            recog[w] = {"asked": len(pics), "own_word": hits}
        assert _org2.state_hash() == _h2
    except Exception as e:
        recog = {"error": repr(e)}
    door_graded = bool(decl.get("WORLD", {}).get("folder"))
    M["DOOR"] = {"graded": door_graded, "pass": door_graded and len(f_pics) >= 300 and len(folder_words) >= 11,
                 "folder_rows": len(folder_rows), "pictures": len(f_pics), "sight_only_rows": len(sight_only), "sight_only_first_seq": sight_only[0]["seq"] if sight_only else None,
                 "folder_words": folder_words, "recognition_of_seen_pictures": recog,
                 "bar": "≥ 300 pictures on the tape · ≥ 11 folder words heard (§18); sight-only rows and recognition REPORTED (§8)",
                 "reason": "" if door_graded else "no `folder <dir>` in the WORLD line — the door is OFF"}
    bel_path = twins_dir / "unblinded-1" / "state" / "beliefs.jsonl"
    bel_rows = read_jsonl(bel_path) if bel_path.exists() else []
    kinds = {}
    per_word_beliefs: Dict[str, int] = {}
    for r in bel_rows:
        k = str(r.get("kind", "belief")); kinds[k] = kinds.get(k, 0) + 1
        if k == "belief": per_word_beliefs[str(r.get("word"))] = per_word_beliefs.get(str(r.get("word")), 0) + 1
    heard = sorted({(r.get("meta") or {}).get("word") for r in tape if r["sense"] == "ear"} - {None})
    max_per_word = max(per_word_beliefs.values()) if per_word_beliefs else 0
    M["W3_1_beliefs"] = {"graded": "BELIEF" in decl, "pass": ("BELIEF" in decl) and bool(bel_rows) and max_per_word <= 1 and kinds.get("revisit", 0) > 0,
                         "rows": len(bel_rows), "kinds": kinds, "standing_words": len(per_word_beliefs), "words_heard": len(heard), "max_belief_rows_per_word": max_per_word,
                         "bar": "≤ 1 raw `belief` row per word (raw rows, never the folded view — life 2's 1,473 rows all carry kind belief) · revisits > 0 · clashes reported"}
    M["PARK"] = {"graded": True, "pass": parked >= 1 and (parked / U["thinks"] <= .05 if U["thinks"] else False), "parked": parked, "thinks": U["thinks"],
                 "parked_share": round(parked / U["thinks"], 4) if U["thinks"] else None, "parked_rules": parked_rules,
                 "no_park_twin_parked": TW.get("blind-park", {}).get("parked"),
                 "reason": "graded in this life (§18): a dead end can arrive from a rule failed 3× or a wordless sight; sight-only rows on this tape: %d" % len(sight_only),
                 "bar": "≥ 1 parked · share ≤ 5 %"}
    M["PLANTS"]["predict_file_pair"] = {"sight_road_rows": live_pred["sight_road_rows"], "rule_rows_filed": live_pred["filed"], "rule_rows_scored": live_pred["scored"], "status_predictions_filed": st.get("predictions_filed")}
    M["PLANTS"]["park_unanswerable_want"] = {"sight_only_rows": len(sight_only), "first_seq": sight_only[0]["seq"] if sight_only else None, "parked_total": parked}
    M["PLANTS"]["belief_contradiction"] = {"clash_rows": kinds.get("clash", 0), "extension_rows": kinds.get("extension", 0)}
    M["TWINS"]["no_curiosity"] = {"graded": False, "reason": "the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded"}
    M["TWINS"]["no_park"] = {"graded": False, "reason": "reported: no-park twin parked %s vs live %d" % (TW.get("blind-park", {}).get("parked"), parked)}
    # BANDS (reported): the drawn bands from gate G-a's line in the genome; photographs from the recorded runs if present
    bands = {"drawn_gate_Ga_line": next((l for l in base_text.splitlines() if "gate G-a wrote" in l), None)}
    for name, pth in (("eye_photo_g1_gate", ROOT / "runs" / "eye-photo-g1" / "gate.json"),):
        bands[name] = json.loads(pth.read_text()) if pth.exists() else "not on disk"
    M["BANDS"] = bands
    graded = ["i_knows", "ii_meeting_real", "iii_growth_matters", "iv_grows_alone", "v_retention", "vi_knows_unknown", "vii_replay", "viii_cost", "x_gaze_finds_thing", "xi_gaze_earns_place", "MODULATION"] + (["ix_not_luck"] if "ix_not_luck" in M else [])
    graded += [k for k in ("W3_2_rules", "W3_1_beliefs", "DOOR", "PARK") if M[k].get("graded")]   # §18: graded only when the life declares them
    failed = [k for k in graded if not M[k].get("pass")] + ([] if R["ALIVE"]["pass"] else ["ALIVE"]) + ([] if M["TWINS"]["random_gaze_loses_xi"]["pass"] else ["TWINS.random_gaze"])
    R["marks"] = M; R["marks_failed"] = failed; R["verdict"] = "PASS" if not failed else "FAIL"
    R["seconds_total"] = round(time.perf_counter() - T0, 1)
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str))
    write_verdict(out, R)
    print(f"VERDICT {R['verdict']} — failed: {failed or 'none'} — {out} ({R['seconds_total']} s)", flush=True)
    return 0


def write_verdict(out: Path, R: dict) -> None:
    M = R["marks"]; A = R["ALIVE"]
    def pf(x): return "PASS" if x else "FAIL"
    L = [f"# G4 VERDICT — {R['verdict']}", "", f"root `{R['root']}` · genome `{R['genome']}` (sha {R['genome_sha']}) · read {R['at']} by `{R['reader']}` (PREREG §5 as amended; the reader's rules §16) · {R['hours']} h",
         "", "| mark | bar | reading | verdict |", "|---|---|---|---|",
         f"| ALIVE | {A['bar_hours']} h under the unit, NRestarts 0, every counter moved every hour, no sense dead > 60 s | {A['hours_on_tape']} h on tape · moved every hour {A['every_counter_moved_every_hour']} · max gap eye/ear {A['max_gap_s_eye_ear']} s · sense restarts {A['sense_restarts']} · crashes {A['crashes']} · NRestarts {A['nrestarts']} | {pf(A['pass'])} |",
         f"| REPLAY / (vii) | byte-identical mind rows; the plant caught | vs live {M['vii_replay']['vs_live']} · two replays {M['vii_replay']['two_replays']} · {M['vii_replay']['mind_rows']} rows · plant at seq {M['vii_replay']['plant_seq']} caught {M['vii_replay']['plant_caught']} | {pf(M['vii_replay']['pass'])} |"]
    i = M["i_knows"]; L.append(f"| (i) | {i['bar']} | Q1 {i['Q1']:.3f} Q2 {i['Q2']:.3f} Q3 {i['Q3']:.3f} Q4 {i['Q4']:.3f} (chance {i['chance_Q1']}; all words Q1 {i['all_words']['Q1']:.3f}) | {pf(i['pass'])} |")
    m = M["ii_meeting_real"]; L.append(f"| (ii) | {m['bar']} (all 16 words) | T-shuffle Q1 {m['T_shuffle_Q1']} · T-nowire Q1 {m['T_nowire_Q1']} | {pf(m['pass'])} |")
    m = M["iii_growth_matters"]; L.append(f"| (iii) | {m['bar']} | T-frozen-10 Q1 {m['T_frozen_10_Q1']} (cells {m['T_frozen_10_cells']}) vs Q1 {m['Q1']:.3f}; the 50-cell twin {m['T_frozen_50_Q1']} | {pf(m['pass'])} |")
    m = M["iv_grows_alone"]; L.append(f"| (iv) | {m['bar']} | born {m['cells_born']} · refused {m['births_refused_budget']} (arrivals {m['arrivals']}, budget left {m['budget_left']}) · pruned {m['edges_pruned']}/{m['edges_born']} = {100*m['pruned_share']:.1f} % (cross-thing born {m['edges_cross']['born']} / pruned {m['edges_cross']['pruned']}) · disuse {m['removed_for_disuse']} | {pf(m['pass'])} |")
    m = M["v_retention"]; L.append(f"| (v) | {m['bar']} | " + ("; ".join(f"w{p['window']}: {p['before']:.3f} → first {p['first_after']:.3f} → last {p['last_in_window']:.3f} ({p['drop_pp']:+.1f} pp drop)" for p in m['pairs']) or m['note']) + f" | {pf(m['pass'])} |")
    m = M["vi_knows_unknown"]; L.append(f"| (vi) | {m['bar']} | plant zog answered {m['plant_zog']['answered_rate']:.2f} (as {m['plant_zog']['answered_as']}, abstain {m['plant_zog']['abstain']}) · null vex abstains {m['null_vex']['abstain_rate']:.2f} (answered as {m['null_vex']['answered_as']}) · Q5 {m['Q5_spiral_abstain']:.2f} · false {m['false_abstention']:.3f} | {pf(m['pass'])} |")
    m = M["viii_cost"]; L.append(f"| (viii) COST | {m['bar']} | live {m['live_mind_ms_last_status']} ms vs solo {m['solo_ms_per_canvas_replay']} ms a canvas · RSS {m['rss_mb_last_status']} MB · CPU {m['cpu_hours']} h | {pf(m['pass'])} |")
    if "ix_not_luck" in M:
        m = M["ix_not_luck"]; L.append(f"| (ix) | {m['bar']} | rank {m['rank_of_own']} of {m['of']} (own {m['own_composite']}; best random {m['best_random']}) | {pf(m['pass'])} |")
    m = M["x_gaze_finds_thing"]; L.append(f"| (x) | {m['bar']} | gaze {m['gaze_rate']:.3f} vs random {m['random_rate']:.3f} (×{m['ratio']}) | {pf(m['pass'])} |")
    m = M["xi_gaze_earns_place"]; L.append(f"| (xi) | {m['bar']} | Q1 gaze {m['Q1_gaze']:.3f} − one-glance {m['Q1_one_glance']} (first-fixation-only {m['Q1_first_fixation_only']}; random-gaze {m['Q1_random_gaze']}) | {pf(m['pass'])} |")
    m = M["MODULATION"]; L.append(f"| MODULATION | {m['bar']} | windows {m['graded_windows']} · null {m.get('null_fake_boundary_w0', {}).get('no_spike')} · no-predict twin max err {m['no_predict_twin_err']} | {pf(m['pass'])} |")
    L.append(f"| TWINS random-gaze | loses (xi) | margin {M['TWINS']['random_gaze_loses_xi']['margin']} | {pf(M['TWINS']['random_gaze_loses_xi']['pass'])} |")
    def gv(m): return ("PASS" if m.get("pass") else "FAIL") if m.get("graded") else "not graded"
    m = M["W3_2_rules"]; L.append(f"| W3-2 rules | {m['bar']} | filed {m['live']['filed']} (induce {m['live']['induce']}, deduce {m['live']['deduce']}, refused {m['live']['refused']}) · scored {m['live']['scored']} · accuracy {m['live']['accuracy']} · words {m['live']['words']} · T-shuffle scored {m['T_shuffle']['scored']} acc {m['T_shuffle']['accuracy']} · parked rules {m['parked_rules']} {m['reason']} | {gv(m)} |")
    m = M["DOOR"]; L.append(f"| DOOR | {m['bar']} | pictures {m['pictures']} (rows {m['folder_rows']}) · words {len(m['folder_words'])} · sight-only {m['sight_only_rows']} (first seq {m['sight_only_first_seq']}) · recognition {m['recognition_of_seen_pictures']} {m['reason']} | {gv(m)} |")
    m = M["W3_1_beliefs"]; L.append(f"| W3-1 beliefs | {m['bar']} | rows {m['rows']} · kinds {m['kinds']} · standing words {m['standing_words']} of {m['words_heard']} heard · max belief rows per word {m['max_belief_rows_per_word']} | {gv(m)} |")
    m = M["PARK"]; L.append(f"| PARK | {m['bar']} | parked {m['parked']} of {m['thinks']} thinks (rules {m['parked_rules']}) — {m['reason']} | {gv(m)} |")
    L.append(f"| TWINS no-sleep / no-curiosity / no-park | (v) / door / PARK | {M['TWINS']['no_sleep_v']} · {M['TWINS']['no_curiosity']['reason']} · {M['TWINS']['no_park']['reason']} | not graded |")
    L += ["", "## Twins (each a replay of the same tape blind to one gene; Q1 on all 16 words, the seen-words Q1 beside it)", "", "| twin | Q1 (all) | Q1 (seen) | composite (all) | cells |", "|---|---|---|---|---|"]
    for b in BLINDS:
        t = M["TWINS"][b]; L.append(f"| {b} | {t['Q1']} | {t['Q1_seen']} | {t['composite']} | {t['cells']} |")
    L += ["", "## Plants", "", json.dumps(M["PLANTS"], indent=1, default=str), "", "## BANDS (reported, never gating)", "", json.dumps(M["BANDS"], indent=1, default=str)[:3000],
          "", "## ALIVE per hour", "", json.dumps(A["per_hour"]), "", f"failed: {R['marks_failed'] or 'none'} · {R['seconds_total']} s"]
    (out / "VERDICT.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
