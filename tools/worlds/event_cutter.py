# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-07 — PREREG-OPEN-WORLD-2 §2 build (the law signed at 00b7af0)
"""tools/worlds/event_cutter.py — THE ORGANISM'S OWN CUTTER (PREREG-OPEN-WORLD-2 §2, docs/organism/whole/).

V1: the error-gated event cut (RESEARCH-OPEN-WORLD.md W2's computation — Zacks's reset transient as a bank of
error integrators; ITS OWN negative results carried: raw surprise ≠ boundary once sequences are learned, so the
naive max-surprise knife is a named, planted-against failure mode) over the eye's OWN residual stream — the
replay journal's glance-row `err` per frame (the law §2.1 says so plainly), never a new signal invented.

An INSTRUMENT ONLY: it reads a replay journal and the tape; it writes nothing near them (G-INSTRUMENT — the
replay with the cutter observing vs without is byte-identical, asserted by tests/tools/test_event_cutter.py and
re-run at bench scale by `bench` below).

§2.2 the integrator bank: K = 3 integrators, declared time constants τ ∈ {1, 4, 16} frames; per frame
`x_i += (err_i − x_i)·(1 − e^(−1/τ))` from x = 0. A boundary at scale τ is an UPWARD CROSSING: x_i rises above
the series' own median + 3×MAD (per integrator, DECLARED, never tuned) from at-or-below it — one boundary per
excursion ("boundaries at integrated-error crossings", the law §0's own words).

§2.3 the nesting print: per coarse scale, the share of its boundaries with a finer scale's boundary at the same
frame (exact) and within ±NEST_TOL frames — the human form's coarse⊆fine approximation, a reading.

§2.4 the naive knife (the named control): the top-|err| frames of the same count as the gated form's union,
ties to the earlier frame — printed beside, the disagreement counted both directions (Avrahami & Kareev's
lesson: once sequences are learned the two knives part, and the parting is the reading).

§2.5 the memory effect: learning rows attributed to boundary frames vs matched non-boundary frames — per frame
the learning count is the canvas row's `births` plus the brain's learn rows at that canvas's seq; each boundary
(in ascending order) is matched to the nearest UNUSED non-boundary frame of the SAME source (ties to the
earlier frame; if no same-source candidate remains, the source rule is relaxed and the relaxation counted).
The shuffled-boundary negative control takes the same number of boundaries at uniform-random frames under the
DECLARED fixed seed 20261777, matched the same way — printed side by side, never one without the other (§7).

M-CUT's own negative control: the err series itself is shuffled (same declared seed) and segmented; a real
boundary counts as ALIGNED if a shuffled-stream boundary lands within ±ALIGN_TOL frames. The declared line
(read BEFORE the bench reading, never tuned after): an aligned share of CONTROL_LIKE_BAR (50%) or more would
be "the shuffle segments like the real stream" — below it, it does not.

CLI:
  python3 -m tools.worlds.event_cutter analyze --journal J --tape T
  python3 -m tools.worlds.event_cutter bench --tape T --genome G --out FILE   (replay ×2 + the gates + the reading)
"""
from __future__ import annotations

import argparse
import json
import math
import random
import resource
import sys
import time
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional, Sequence, Set, Tuple

TAUS = (1.0, 4.0, 16.0)      # the law §2.2's declared time constants, frames
MAD_K = 3.0                  # the law §2.2: median + 3×MAD — DECLARED, never tuned
NEST_TOL = 2                 # the nesting reading's declared window, frames
ALIGN_TOL = 3                # the shuffle-alignment reading's declared window, frames
CONTROL_LIKE_BAR = 0.5       # M-CUT's declared line for "segments like" — named BEFORE the bench reading
SHUFFLE_SEED = 20261777      # the shuffled negative controls' declared fixed seed
BL2_GENOME = Path("/data/dev/genome-wt-mouthcap/scratch/bl2/GENOME.genome")   # the bench genome's own parent copy


# ----------------------------------------------------------------------------- the journal side (§2.1)
def load_journal(path: Path) -> List[Dict[str, object]]:
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def err_series(rows: Sequence[Dict[str, object]]) -> Tuple[List[float], List[Dict[str, object]]]:
    """The eye's residual per frame: the replay journal's canvas rows — the mind rows carrying `err` (one per
    eye row; the coarse glance's own row carries none, creature/mind.py:_coarse_row) — in journal order."""
    canvases = [r for r in rows if "err" in r]
    return [float(r["err"]) for r in canvases], canvases


def engage(rows: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """M-ENGAGE's presence counts: the brain's turn/learn rows over the tape, said and surprise beside —
    and the turn rows' own `reason` tally (a null say/surprise carries its cause on the row, never hidden)."""
    _, canvases = err_series(rows)
    turns = [r for r in rows if r.get("kind") == "brain" and r.get("act") == "turn"]
    learns = [r for r in rows if r.get("kind") == "brain" and r.get("act") == "learn"]
    refused = [r for r in rows if r.get("kind") == "brain" and r.get("act") == "refused"]
    said = [t for t in turns if isinstance(t.get("say"), dict) and (t["say"] or {}).get("words")]
    surprises = [float(t["surprise"]) for t in turns if t.get("surprise") is not None]
    worded = [c for c in canvases if c.get("words") or c.get("word")]
    reasons: Dict[str, int] = {}
    for t in turns:
        key = str(t.get("reason"))
        reasons[key] = reasons.get(key, 0) + 1
    return {"canvases": len(canvases), "worded": len(worded), "turns": len(turns), "learns": len(learns),
            "refused": len(refused), "said": len(said), "turn_reasons": reasons,
            "surprise_mean": (sum(surprises) / len(surprises)) if surprises else None,
            "surprise_max": max(surprises) if surprises else None}


def learn_per_frame(rows: Sequence[Dict[str, object]], canvases: Sequence[Dict[str, object]]) -> List[int]:
    """§2.5's learning count per frame: the canvas row's `births` plus the brain's learn rows at its seq."""
    learn_seqs: Dict[int, int] = {}
    for r in rows:
        if r.get("kind") == "brain" and r.get("act") == "learn":
            learn_seqs[int(r["seq"])] = learn_seqs.get(int(r["seq"]), 0) + 1
    return [len(c.get("births") or []) + learn_seqs.get(int(c["seq"]), 0) for c in canvases]


# ----------------------------------------------------------------------------- the integrator bank (§2.2)
def integrate(errs: Sequence[float], tau: float) -> List[float]:
    a = 1.0 - math.exp(-1.0 / tau)
    x, out = 0.0, []
    for e in errs:
        x += (e - x) * a
        out.append(x)
    return out


def crossings(x: Sequence[float], k: float = MAD_K) -> Dict[str, object]:
    med = median(x)
    mad = median([abs(v - med) for v in x])
    thr = med + k * mad
    bounds = [i for i in range(len(x)) if x[i] > thr and (i == 0 or x[i - 1] <= thr)]
    return {"boundaries": bounds, "median": med, "mad": mad, "threshold": thr}


def segment(errs: Sequence[float]) -> Dict[str, object]:
    scales: Dict[float, Dict[str, object]] = {}
    for tau in TAUS:
        scales[tau] = crossings(integrate(errs, tau))
    union = sorted({b for tau in TAUS for b in scales[tau]["boundaries"]})
    nesting: Dict[str, Dict[str, Tuple[int, int]]] = {}
    ordered = sorted(TAUS, reverse=True)                       # 16, 4, 1 — coarse to fine
    for ci, coarse in enumerate(ordered[:-1]):
        for fine in ordered[ci + 1:]:
            cset, fset = scales[coarse]["boundaries"], set(scales[fine]["boundaries"])
            key = f"{coarse:g}_in_{fine:g}"
            nesting[key] = {
                "exact": (sum(1 for b in cset if b in fset), len(cset)),
                f"within{NEST_TOL}": (sum(1 for b in cset if any(abs(b - f) <= NEST_TOL for f in fset)), len(cset)),
            }
    return {"scales": scales, "union": union, "nesting": nesting, "n_frames": len(errs)}


# ----------------------------------------------------------------------------- the controls (§2.4/§2.5, M-CUT)
def naive_knife(errs: Sequence[float], n: int) -> Set[int]:
    """The named control: the top-|err| frames of the same count, ties to the earlier frame."""
    return {i for i, _ in sorted(enumerate(errs), key=lambda p: (-abs(p[1]), p[0]))[:n]}


def disagreement(a: Set[int], b: Set[int]) -> Tuple[int, int, int]:
    """|a △ b|, |only a|, |only b|."""
    return len(a ^ b), len(a - b), len(b - a)


def aligned_count(a: Sequence[int], b: Sequence[int], tol: int = ALIGN_TOL) -> int:
    return sum(1 for x in a if any(abs(x - y) <= tol for y in b))


def shuffled_boundaries(n_frames: int, count: int, seed: int = SHUFFLE_SEED) -> List[int]:
    """The shuffled-boundary negative control: `count` uniform-random frames, the declared fixed seed."""
    return sorted(random.Random(seed).sample(range(n_frames), count))


def matched_controls(boundaries: Set[int], n_frames: int, sources: Sequence[str]) -> List[int]:
    """§2.5's matched non-boundary frames: for each boundary in ascending order, the nearest UNUSED
    non-boundary frame of the same source (ties to the earlier frame; the source rule is relaxed only when no
    same-source candidate remains, and the relaxation is counted on the return's own ledger)."""
    used: Set[int] = set()
    out: List[int] = []
    for b in sorted(boundaries):
        cands = [i for i in range(n_frames) if i not in boundaries and i not in used and sources[i] == sources[b]]
        if not cands:
            cands = [i for i in range(n_frames) if i not in boundaries and i not in used]
        pick = min(cands, key=lambda i: (abs(i - b), i))
        used.add(pick)
        out.append(pick)
    return out


def memory_pair(learns: Sequence[int], side: Sequence[int], ctrl: Sequence[int]) -> Tuple[Dict[str, object], Dict[str, object]]:
    def block(frames: Sequence[int]) -> Dict[str, object]:
        tot = sum(learns[i] for i in frames)
        return {"frames": len(frames), "total": tot, "mean": (tot / len(frames)) if frames else None}
    return block(side), block(ctrl)


# ----------------------------------------------------------------------------- the whole reading
def analyze(journal_path: Path, tape_dir: Path) -> Dict[str, object]:
    rows = load_journal(journal_path)
    errs, canvases = err_series(rows)
    eye = sorted((r for f in sorted(Path(tape_dir).glob("*.jsonl"))
                  for r in (json.loads(l) for l in f.read_text().splitlines() if l.strip()) if r["sense"] == "eye"),
                 key=lambda r: int(r["seq"]))
    if len(errs) != len(eye) or [int(c["seq"]) for c in canvases] != [int(r["seq"]) for r in eye]:
        raise RuntimeError(f"canvas rows ({len(errs)}) do not line up with the tape's eye rows ({len(eye)}) "
                           "— a finding, never patched over")
    n = len(errs)
    sources = [str(r["meta"].get("source")) for r in eye]
    series = [str(r["meta"].get("series")) for r in eye]
    seg = segment(errs)
    eng = engage(rows)
    learns = learn_per_frame(rows, canvases)

    union = set(seg["union"])
    ctrls = matched_controls(union, n, sources)
    pair_real = memory_pair(learns, sorted(union), ctrls)
    shuf = shuffled_boundaries(n, len(union))
    shuf_ctrls = matched_controls(set(shuf), n, sources)
    pair_shuf = memory_pair(learns, shuf, shuf_ctrls)

    knife = naive_knife(errs, len(union))
    dis = disagreement(union, knife)

    sh = list(errs)
    random.Random(SHUFFLE_SEED).shuffle(sh)
    seg_sh = segment(sh)
    aligned = aligned_count(seg["union"], seg_sh["union"])

    worded_err = [float(c["err"]) for c in canvases if c.get("words") or c.get("word")]
    k_sh = len(seg_sh["union"])
    p_chance = 1.0 - (1.0 - (2 * ALIGN_TOL + 1) / n) ** k_sh if n else 0.0     # P(≥1 of k shuffled boundaries within ±ALIGN_TOL of a real one), uniform
    return {"n_frames": n, "err": {"median": median(errs), "mean": sum(errs) / n, "max": max(errs), "min": min(errs)},
            "series_counts": {s: series.count(s) for s in sorted(set(series))}, "sources": sorted(set(sources)),
            "segment": seg, "engage": eng, "learns_total": sum(learns),
            "births_total": sum(len(c.get("births") or []) for c in canvases),
            "worded_err_mean": (sum(worded_err) / len(worded_err)) if worded_err else None,
            "memory": {"real": pair_real, "real_controls": ctrls,
                       "shuffled": pair_shuf, "shuffled_boundaries": shuf, "shuffled_controls": shuf_ctrls},
            "naive": {"count": len(union), "disagreement": dis, "knife_only": sorted(knife - union),
                      "gated_only": sorted(union - knife)},
            "shuffle_stream": {"boundaries": k_sh, "aligned": aligned,
                               "share": (aligned / len(union)) if union else None,
                               "chance_expected": (len(union) * p_chance) if union else None,
                               "bar": CONTROL_LIKE_BAR}}


def report(a: Dict[str, object]) -> List[str]:
    L: List[str] = []
    e = a["err"]
    L.append(f"the error series (the eye's own residual, the journal's glance-row err): {a['n_frames']} frames; "
             f"median {e['median']:.4f} mean {e['mean']:.4f} min {e['min']:.4f} max {e['max']:.4f}; "
             f"frames per series {a['series_counts']}; sources {a['sources']}")
    seg = a["segment"]
    L.append(f"M-CUT — the integrator bank (τ ∈ {{1, 4, 16}} frames; boundary = an upward crossing of the "
             f"series' own median + {MAD_K:g}×MAD; declared, never tuned):")
    for tau in TAUS:
        s = seg["scales"][tau]
        L.append(f"  τ={tau:g}: {len(s['boundaries'])} boundaries {s['boundaries']} "
                 f"(median {s['median']:.4f} mad {s['mad']:.4f} threshold {s['threshold']:.4f})")
    L.append(f"  union: {len(seg['union'])} boundary frames {seg['union']}")
    for key, shares in seg["nesting"].items():
        L.append(f"  nesting {key}: exact {shares['exact'][0]}/{shares['exact'][1]}, "
                 f"within±{NEST_TOL} {shares[f'within{NEST_TOL}'][0]}/{shares[f'within{NEST_TOL}'][1]} "
                 f"(the human form's coarse⊆fine approximation — a reading)")
    sh = a["shuffle_stream"]
    like = "DOES NOT segment like the real stream" if (sh["share"] is not None and sh["share"] < sh["bar"]) \
        else "SEGMENTS LIKE the real stream (the control FAILS)"
    L.append(f"  the shuffled-residual negative control (seed {SHUFFLE_SEED}): {sh['boundaries']} boundaries; "
             f"aligned within±{ALIGN_TOL} with the real union: {sh['aligned']}/{len(seg['union'])} "
             f"(share {sh['share'] if sh['share'] is None else round(sh['share'], 3)}, declared line {sh['bar']}) → {like}")
    L.append(f"    context (arithmetic, not a moved line): the chance alignment of {sh['boundaries']} uniform boundaries "
             f"against {len(seg['union'])} fixed ones at ±{ALIGN_TOL} over {a['n_frames']} frames expects "
             f"≈{sh['chance_expected']:.1f} aligned — the observed {sh['aligned']} is what a random stream shows "
             f"(the shuffle preserves the err VALUES, not their times; the real segmentation is of the times)")
    g = a["engage"]
    road = "the brain ENGAGES" if g["turns"] > 0 else "ZERO TURNS — the FAIL-HEAR road, printed with presence counts (the seat's call)"
    L.append(f"M-ENGAGE — the brain over the video tape with the hears declaration: turns {g['turns']} "
             f"over {g['worded']} worded canvases of {g['canvases']} (presence counts, never silent) → {road}; "
             f"learns {g['learns']}, said {g['said']}, refused {g['refused']}, "
             f"surprise mean {g['surprise_mean']} max {g['surprise_max']}; the turn rows' own reasons {g['turn_reasons']}")
    m = a["memory"]
    rb, rc = m["real"]
    sb, sc = m["shuffled"]
    L.append(f"M-MEM — the memory effect (learning = glance births + the brain's learn rows; {a['learns_total']} "
             f"learning events over {a['n_frames']} frames — {a['births_total']} births + {g['learns']} learns):")
    L.append(f"  REAL boundaries ({rb['frames']}): learning {rb['total']} (mean {rb['mean']})  vs  "
             f"matched controls ({rc['frames']}): learning {rc['total']} (mean {rc['mean']})  →  "
             f"{'boundary-side > control-side' if (rb['mean'] or 0) > (rc['mean'] or 0) else 'NO effect on the real boundaries'}")
    L.append(f"  SHUFFLED boundaries ({sb['frames']}, seed {SHUFFLE_SEED}): learning {sb['total']} (mean {sb['mean']})  vs  "
             f"matched controls ({sc['frames']}): learning {sc['total']} (mean {sc['mean']})  →  "
             f"{'CONCENTRATION ON THE SHUFFLE (the control fires)' if (sb['mean'] or 0) > (sc['mean'] or 0) else 'no concentration — the control shows nothing'}")
    if a["worded_err_mean"] is not None:
        L.append(f"  context for the seat: the worded canvases' mean err is {a['worded_err_mean']:.4f} vs the stream's "
                 f"{a['err']['mean']:.4f} — the word's own prediction error lives in the residual, so learning and "
                 f"boundaries meet by the organism's own dynamics (read M-MEM against this, never past it)")
    nv = a["naive"]
    d = nv["disagreement"]
    L.append(f"M-NAIVE — the naive knife (top-|err| frames of the same count, {nv['count']}) vs the gated form: "
             f"disagreement {d[0]} frames ({d[1]} gated-only, {d[2]} knife-only); "
             f"gated-only {nv['gated_only']}; knife-only {nv['knife_only']} (a reading — the two knives answer "
             f"different questions once sequences are learned)")
    return L


# ----------------------------------------------------------------------------- the gates, re-read at bench scale
def gate_hears(bench_genome: Path, bl2_genome: Path, tape_dir: Path) -> Tuple[bool, List[str]]:
    import difflib
    old = Path(bl2_genome).read_text().splitlines()
    new = Path(bench_genome).read_text().splitlines()
    diff = list(difflib.unified_diff(old, new, lineterm=""))
    minus = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
    plus = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
    ok = (len(minus), len(plus)) == (1, 1) and plus[0] == minus[0].replace("hears scene", "hears scene video", 1)
    rows = [json.loads(l) for f in sorted(Path(tape_dir).glob("*.jsonl"))
            for l in f.read_text().splitlines() if l.strip()]
    eye = [r for r in rows if r["sense"] == "eye"]
    ear = [r for r in rows if r["sense"] == "ear"]
    prov = all(r["meta"].get("source") == "video" for r in eye) and all(r["meta"].get("source") == "video-caption" for r in ear)
    lines = [f"G-HEARS: the bench genome's diff vs bl2's copy is {len(minus)}/{len(plus)} line(s) "
             f"({'EXACTLY the one declared line' if ok else 'NOT the one declared line — the gate FAILS'}); "
             f"provenance: every eye row source 'video' ({len(eye)}), every ear row 'video-caption' ({len(ear)}) "
             f"— {'unchanged everywhere' if prov else 'CHANGED — the gate FAILS'}"]
    return ok and prov, lines


def bench(tape_dir: Path, genome: Path, out_file: Path, work: Optional[Path] = None) -> int:
    """The full V1 bench: two replays (G-INSTRUMENT at bench scale), the cutter's reading, the prices."""
    import hashlib
    import tempfile
    from creature.replay import run_replay
    tape_dir, genome = Path(tape_dir), Path(genome)
    work = Path(work) if work else Path(tempfile.mkdtemp(prefix="event-cutter-bench-"))
    work.mkdir(parents=True, exist_ok=True)
    lines: List[str] = ["PREREG-OPEN-WORLD-2 (V1) — the bench reading (the builder lane's run; the seat walks the verdict)",
                        f"tape: {tape_dir}   genome: {genome} (the bench copy, hears 'video' — the ONE declared change)", ""]

    t0, c0 = time.perf_counter(), time.process_time()
    j1 = run_replay(genome, tape_dir, work / "replay-1")
    wall1, cpu1 = time.perf_counter() - t0, time.process_time() - c0
    h1 = hashlib.sha256(j1.read_bytes()).hexdigest()
    t0, c0 = time.perf_counter(), time.process_time()
    analysis = analyze(j1, tape_dir)
    wall_cut, cpu_cut = time.perf_counter() - t0, time.process_time() - c0
    h1_after = hashlib.sha256(j1.read_bytes()).hexdigest()
    j2 = run_replay(genome, tape_dir, work / "replay-2")
    h2 = hashlib.sha256(j2.read_bytes()).hexdigest()
    rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

    ok_hears, hears_lines = gate_hears(genome, BL2_GENOME, tape_dir)
    same = h1 == h1_after == h2
    lines += ["THE GATES", "---------", *hears_lines,
              f"G-INSTRUMENT: the replay's journal sha256 with the cutter observing (before {h1[:12]}… / after "
              f"{h1_after[:12]}…) and a second replay without it ({h2[:12]}…): "
              f"{'byte-identical — the cutter never interferes' if same else 'DIFFER — the gate FAILS'}",
              f"G-PLANT: tests/tools/test_event_cutter.py's planted truths (10 planted spikes fire at the 10 known "
              f"frames at every scale; the shuffled stream aligns 2/10 — the instrument CAN fail), run with the suite", "",
              "THE MARKS", "--------"]
    lines += report(analysis)
    lines += ["", f"M-COST — replay-1 {wall1:.1f}s wall / {cpu1:.1f}s CPU; the cutter {wall_cut:.1f}s wall / "
              f"{cpu_cut:.1f}s CPU; peak RSS {rss_mb:.0f} MB (the process's own, both replays + the cutter in it); "
              f"the conversion's prices are on the seat's record (records/open-world-2, the two videos converted "
              f"by V0's own tool). §6's bounds: replay CPU < 1 CPU-h, peak < 3,800 MB at SLOT_MEM 4G — "
              f"{'INSIDE' if cpu1 < 3600 and rss_mb < 3800 else 'OUTSIDE — FAIL-COST road'}"]
    out_file = Path(out_file)
    out_file.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="tools.worlds.event_cutter", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="the cutter's reading over a replay journal + its tape")
    a.add_argument("--journal", required=True, type=Path)
    a.add_argument("--tape", required=True, type=Path)
    b = sub.add_parser("bench", help="the full V1 bench: replay ×2, the gates, the marks, the prices")
    b.add_argument("--tape", required=True, type=Path)
    b.add_argument("--genome", required=True, type=Path)
    b.add_argument("--out", required=True, type=Path)
    b.add_argument("--work", default=None, type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "analyze":
        print("\n".join(report(analyze(args.journal, args.tape))))
        return 0
    return bench(args.tape, args.genome, args.out, args.work)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
