"""run_g1.py — rung 1: the GAZE gene ON (docs/G1-PREREG.md). Two runs, declared apart:
  python3 -m genome.run_g1 --toy            G1-toy: canvases with a KNOWN thing position (gates the gene)
  python3 -m genome.run_g1 --his            G1-his: his pictures from world/<word>/ (gates the organism on his world)
  python3 -m genome.run_g1 --gate-toy       gate G-a on the toy's first-fixation glances → writes G1.genome's thetas
  python3 -m genome.run_g1 --gate-his       gate G-a on his pictures' first-fixation glances → writes G1-his.genome's thetas

edit: Claude (Fable 5.1), 2026-09-19 18:18 +0400 — G2: `--genome <path>` on the his road; the gate file and the run tag are named by the genome's stem.
edit: Claude (Fable 5.1), 2026-09-19 17:54 +0400 — §7 addendum: the withheld word is drawn among rule-added words only (world/OWN-FOLDERS.txt).
edit: Claude (Fable 5.1), 2026-09-19 17:48 +0400 — §1's overlap clause: on his pictures the toy's thetas are carried when the gate finds the bands overlapping, stated on the page.
edit: Claude (Fable 5.1), 2026-09-19 17:42 +0400 — after the advisor: (v) read in counts; the verdict page names the run kind and its own predictions (§4 first run, §6 amended); the cost row states what it excludes.
edit: Claude (Fable 5.1), 2026-09-19 17:27 +0400 — on Ahmad's 17:10 «Ok go for it» (D-G4 road (a)). Every bar is G1 §3's, written before
this file. A picture is gazed ONCE (its glances cached); each glance is one moment with the same word (§1).
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import gate_ga, gaze, world
from .machinery import Genome, GenomeError, Organism, parse_genome
from .questions import ask_glances, ask_plant_glances, build_ledgers
from .run_g0 import ARR2_PER_THING, HELD_N, PER_THING, PLANT_SHOWINGS, RANDOM_GENOMES, TOY_PER_THING, genome_numbers, random_genome

ROOT = Path(__file__).resolve().parent.parent
GENOME_TOY = ROOT / "genome" / "G1.genome"
GENOME_HIS = ROOT / "genome" / "G1-his.genome"
WORLD_HIS = ROOT / "world"
MIN_PICS, MIN_WORDS, HOLD_EVERY = 5, 4, 3
COST_BAR_S = 600

Glanced = Tuple[str, List[np.ndarray], List[Tuple[int, int]], Optional[Dict[str, object]], str]   # (thing, feats, fixations, truth|None, picture id)


def _pid(rgb: np.ndarray) -> str:
    return hashlib.sha256(rgb.tobytes()).hexdigest()[:16]


def glance_rows(rows: Sequence[Tuple[str, np.ndarray, Optional[Dict[str, object]]]], genome: Genome, mode: str) -> List[Glanced]:
    out: List[Glanced] = []
    for t, rgb, truth in rows:
        pid = _pid(rgb); g = gaze.glances(rgb, genome.retina, genome.gaze, mode, pid)
        out.append((t, g["feats"], g["fix"], truth, pid))
    return out


def glance_held(held: Dict[str, List[Tuple[np.ndarray, Optional[Dict[str, object]]]]], genome: Genome, mode: str) -> Dict[str, List[Glanced]]:
    return {t: [(t, *(lambda g: (g["feats"], g["fix"]))(gaze.glances(rgb, genome.retina, genome.gaze, mode, _pid(rgb))), truth, _pid(rgb)) for rgb, truth in rows] for t, rows in held.items()}


def on_thing(fix: Tuple[int, int], cell: Tuple[int, int]) -> bool:
    return max(abs(fix[0] - cell[0]), abs(fix[1] - cell[1])) <= 1


def feats_only(held_g: Dict[str, List[Glanced]]) -> Dict[str, List[List[np.ndarray]]]:
    return {t: [r[1] for r in rows] for t, rows in held_g.items()}


# ----------------------------------------------------------------------------- one life
def live(genome: Genome, dev: List[Glanced], a2: List[Glanced], plant: List[Glanced], things: Sequence[str], arr2: Sequence[str],
         held_g: Dict[str, List[Glanced]], never: str, *, wire=True, frozen_after=None, shuffle_words=None, ask_at_dev=True,
         with_arr2=True, with_plant=True, plant_word: str = world.THING_PLANT, null_word: str = world.THING_NULL, label="", keep=False) -> Dict[str, object]:
    t0 = time.perf_counter()
    org = Organism(genome, wire=wire, frozen_after=frozen_after)
    moment_thing: Dict[int, str] = {}; moment_on: Dict[int, bool] = {}
    held = feats_only(held_g); never_h = {never: held[never]} if never in held else {}
    rec: Dict[str, object] = {"label": label}

    def feed(rows: List[Glanced], words: Optional[List[str]] = None) -> None:
        for i, (t, feats, fix, truth, _pid_) in enumerate(rows):
            w = words[i] if words is not None else t
            xw = world.encode_word(w, genome.ear_blank_zero)
            for k, x in enumerate(feats):
                moment_thing[org.t] = t
                if truth is not None and fix:
                    moment_on[org.t] = on_thing(fix[k], truth["cell"])
                org.moment(x, xw)

    org.new_arrival(); feed(dev, shuffle_words)
    rec["at_dev"] = org.summary(); rec["hash_dev"] = org.state_hash()
    if ask_at_dev:
        rec["ask_dev"] = ask_glances(org, build_ledgers(org, moment_thing), things, held, never_h, genome.ear_blank_zero)
    if with_arr2 and a2:
        org.new_arrival(); feed(a2)
        rec["at_arr2"] = org.summary(); L = build_ledgers(org, moment_thing)
        rec["ask_arr2"] = ask_glances(org, L, things, held, never_h, genome.ear_blank_zero)
        rec["ask_arr2_new"] = ask_glances(org, L, list(arr2), held, never_h, genome.ear_blank_zero)
        rec["hash_arr2"] = org.state_hash()
    if with_plant and plant:
        org.new_arrival(); feed(plant)
        L = build_ledgers(org, moment_thing)
        rec["plant"] = ask_plant_glances(org, L, plant_word, held[plant_word])
        rec["null_plant"] = ask_plant_glances(org, L, null_word, held[null_word])
        rec["ask_final"] = ask_glances(org, L, things, held, never_h, genome.ear_blank_zero)
    rec["at_final"] = org.summary()
    rec["refusals_by_arrival"] = org.refusals_by_arrival + [org.c["births_refused_budget"] - sum(org.refusals_by_arrival)]
    rec["hash_final"] = org.state_hash()
    L = build_ledgers(org, moment_thing)
    keys = list(moment_thing.keys()); vals = [moment_thing[k] for k in keys]
    perm = np.random.default_rng(99).permutation(len(vals))
    _ = build_ledgers(org, {k: vals[j] for k, j in zip(keys, perm)})
    rec["ledger_corruption_hash_unchanged"] = (org.state_hash() == rec["hash_final"])
    rec["multi_thing_sight_cells"] = sum(1 for s in L["sight"].values() if len(s) > 1)
    def _cross(log):
        return sum(1 for _m, sc, wc in log if L["sight"].get(sc, set()) != L["words"].get(wc, set()))
    rec["edges_cross"] = {"born": _cross(org.edges_log), "pruned": _cross(org.prunes_log), "born_total": len(org.edges_log), "pruned_total": len(org.prunes_log)}
    rec["cells_per_thing"] = {t: sum(1 for c, s in L["sight"].items() if s == {t} and org.sight.alive[c]) for t in list(things) + list(arr2)}
    if moment_on:
        on = [m for m, area, _c, _r in org.births if area == "sight" and moment_on.get(m) is True]
        off = [m for m, area, _c, _r in org.births if area == "sight" and moment_on.get(m) is False]
        rec["births_by_glance"] = {"on_thing": len(on), "off_thing": len(off), "moments_on": sum(1 for v in moment_on.values() if v), "moments_off": sum(1 for v in moment_on.values() if not v)}
    rec["seconds"] = round(time.perf_counter() - t0, 2)
    if keep:
        rec["_org"] = org; rec["_ledger"] = {"sight": {int(k): sorted(v) for k, v in L["sight"].items()}, "words": {int(k): sorted(v) for k, v in L["words"].items()}}
    return rec


def landing(held_g: Dict[str, List[Glanced]], things: Sequence[str], first: int = 2) -> Dict[str, object]:
    """Mark (x): a fixation within Chebyshev distance 1 of the thing's centroid cell among the first `first` fixations."""
    n = 0; hit = 0; per = {}
    for t in things:
        h = 0
        for _t, _f, fix, truth, _p in held_g[t]:
            n += 1; ok = any(on_thing(f, truth["cell"]) for f in fix[:first]); hit += ok; h += ok
        per[t] = h / len(held_g[t]) if held_g[t] else 0.0
    return {"rate": hit / n if n else 0.0, "n": n, "hit": hit, "per_thing": per, "first": first}


# ----------------------------------------------------------------------------- the toy world
def toy_streams(genome: Genome, plant_showings: int):
    things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
    r_dev, r_held, r_arr2, r_plant, r_shuf = (np.random.default_rng(s) for s in (1, 2, 3, 4, 5))
    dev = world.stream_canvas(things, PER_THING, r_dev)
    held = world.holdout_canvas(things + arr2 + [world.THING_NEVER, world.THING_PLANT, world.THING_NULL], HELD_N, r_held)
    a2 = world.stream_canvas(arr2, ARR2_PER_THING, r_arr2)
    plant = [(world.THING_PLANT, *world.render_canvas(world.THING_PLANT, r_plant)) for _ in range(plant_showings)]
    n_checked = world.assert_disjoint_canvas(dev + a2 + plant, held)
    bad = dict(held); bad[things[0]] = held[things[0]][:1] + [(dev[0][1].copy(), dev[0][2])]
    try:
        world.assert_disjoint_canvas(dev, bad); raise SystemExit("disjointness control FAILED to catch the planted copy")
    except AssertionError:
        pass
    shuffle_words = [things[i] for i in r_shuf.integers(0, len(things), size=len(dev))]
    return things, arr2, dev, held, a2, plant, shuffle_words, n_checked


# ----------------------------------------------------------------------------- his world (the folder door)
def load_his(genome: Genome, root: Path = WORLD_HIS, seed: int = 20260919) -> Dict[str, object]:
    words: Dict[str, Dict[str, object]] = {}; unreadable = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        pics = sorted(p for p in d.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
        rows = []
        for p in pics:
            try:
                rows.append((p.name, gaze.canvas_of_picture(p, int(genome.gaze["canvas"]))))
            except Exception as e:      # an unreadable picture is named, never silently dropped
                unreadable.append((str(p), f"{type(e).__name__}: {e}"))
        words[d.name] = {"ok_name": bool(re.fullmatch(r"[a-z]{1,8}", d.name)), "rows": rows}
    shown = sorted(w for w, v in words.items() if v["ok_name"] and len(v["rows"]) >= MIN_PICS)
    short = {w: {"pictures": len(v["rows"]), "name_ok": v["ok_name"]} for w, v in words.items() if w not in shown}
    if len(shown) < MIN_WORDS:
        raise SystemExit(f"G1-his refused: {len(shown)} usable words (need ≥ {MIN_WORDS}: a–z ≤ 8 letters, ≥ {MIN_PICS} readable pictures). Folders short: {short}. Unreadable: {unreadable}")
    own_file = root / "OWN-FOLDERS.txt"                      # §7 addendum: folders he gave himself are never the withheld word
    own = set(own_file.read_text().split()) if own_file.exists() else set()
    pool = [w for w in shown if w not in own] or shown
    withheld = str(np.random.default_rng(seed).choice(pool))
    shown_words = [w for w in shown if w != withheld]
    dev_rows = []; held: Dict[str, List[Tuple[np.ndarray, None]]] = {}; split = {}
    for w in shown_words:
        rows = words[w]["rows"]; hi = [i for i in range(len(rows)) if i % HOLD_EVERY == HOLD_EVERY - 1] or [len(rows) - 1]
        held[w] = [(rows[i][1], None) for i in hi]
        dev_rows += [(w, rows[i][1], None) for i in range(len(rows)) if i not in hi]
        split[w] = {"dev": [rows[i][0] for i in range(len(rows)) if i not in hi], "held": [rows[i][0] for i in hi]}
    held[withheld] = [(rgb, None) for _n, rgb in words[withheld]["rows"]]
    seen: Dict[str, str] = {}
    for w, rgb, _t in dev_rows:
        seen[hashlib.sha256(rgb.tobytes()).hexdigest()] = w
    dups = [(w, i) for w, rows in held.items() for i, (rgb, _t) in enumerate(rows) if hashlib.sha256(rgb.tobytes()).hexdigest() in seen]
    if dups:
        raise SystemExit(f"G1-his refused: held-out pictures byte-identical to development ones (word, index): {dups}")
    order = np.random.default_rng(1).permutation(len(dev_rows)); dev_rows = [dev_rows[i] for i in order]
    shuffle_words = [shown_words[i] for i in np.random.default_rng(5).integers(0, len(shown_words), size=len(dev_rows))]
    return {"things": shown_words, "withheld": withheld, "dev": dev_rows, "held": held, "split": split, "short": short, "unreadable": unreadable, "shuffle_words": shuffle_words}


# ----------------------------------------------------------------------------- gates
def gate(genome_path: Path, feats: Dict[str, np.ndarray], words: Sequence[str], out_path: Path, label: str) -> Dict[str, object]:
    return gate_ga.run_feats(feats, words, genome_path, out_path, seed=20260919, label=label)


def first_glance_feats(rows_by_thing: Dict[str, List[np.ndarray]], genome: Genome) -> Dict[str, np.ndarray]:
    return {t: np.stack([gaze.glances(rgb, genome.retina, genome.gaze, "surprise", _pid(rgb))["feats"][0] for rgb in rgbs]) for t, rgbs in rows_by_thing.items()}


# ----------------------------------------------------------------------------- main
def main(argv: List[str]) -> int:
    assert os.environ.get("OPENBLAS_NUM_THREADS") == "1" and os.environ.get("OMP_NUM_THREADS") == "1", "G0 §10 clause 10: run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1"
    his = "--his" in argv or "--gate-his" in argv
    gpath = Path(argv[argv.index("--genome") + 1]) if "--genome" in argv else (GENOME_HIS if his else GENOME_TOY)   # G2: --genome genome/G2-his.genome
    if "--gate-toy" in argv:
        g = parse_genome(gpath.read_text().replace("cos<THETA_N", "cos<0.5").replace("cos>THETA_M", "cos>0.99"))   # the gate needs only the eye and the gaze
        rng = np.random.default_rng(20260919)
        rows = {t: [world.render_canvas(t, rng)[0] for _ in range(PER_THING)] for t in world.THINGS_11}
        gate(gpath, first_glance_feats(rows, g), list(world.THINGS_11), ROOT / "runs" / "gate-ga-G1.json", "toy first-fixation glances")
        return 0
    if "--gate-his" in argv:
        if not gpath.exists():
            gpath.write_text(GENOME_TOY.read_text().replace("# G1.genome — G0b's genome with the GAZE gene switched ON", "# G1-his.genome — G1.genome with the thetas re-written by gate G-a on HIS pictures' glances (G1 §5 step 7)", 1))
            t = re.sub(r"cos<[0-9.]+", "cos<THETA_N", gpath.read_text()); t = re.sub(r"cos>[0-9.]+ same-answer", "cos>THETA_M same-answer", t); t = re.sub(r"\n# gate G-a wrote.*", "", t)
            gpath.write_text(t)
        g = parse_genome(gpath.read_text().replace("cos<THETA_N", "cos<0.5").replace("cos>THETA_M", "cos>0.99"))
        H = load_his(g)
        rows = {w: [rgb for ww, rgb, _t in H["dev"] if ww == w] for w in H["things"]}
        gate(gpath, first_glance_feats(rows, g), H["things"], ROOT / "runs" / f"gate-ga-{gpath.stem}.json", f"his first-fixation glances ({gpath.stem})")
        return 0

    tag = (gpath.stem.lower().replace("-his", "") + "-his") if his else "g1-toy"        # g1-his / g2-his
    stamp = time.strftime("%Y%m%d-%H%M%S"); out = ROOT / "runs" / f"{tag}-{stamp}"; out.mkdir(parents=True, exist_ok=True)
    gate_path0 = ROOT / "runs" / (f"gate-ga-{gpath.stem}.json" if his else "gate-ga-G1.json")
    if his and "cos<THETA_N" in gpath.read_text():
        # G1 §1: the bands overlap on his pictures → the run still reads, with the TOY's thetas carried, and the verdict says so
        rep0 = json.loads(gate_path0.read_text()) if gate_path0.exists() else {}
        if not rep0.get("overlap"):
            raise GenomeError("G1-his.genome has placeholders and the gate did not report an overlap — run --gate-his first")
        toy = parse_genome(GENOME_TOY.read_text())
        gate_ga.write_thetas(gpath, toy.theta_n, toy.theta_m, f"G1 §1: gate G-a on his glances found the bands OVERLAPPING (within-median {rep0['retina']['within']['median']:.3f} ≤ floor {rep0['choice']['amended']['floor']:.3f}); the TOY's thetas are carried so the run can read; the verdict says so")
        print(f"gate G-a on his glances: bands OVERLAP — the toy's THETA_N={toy.theta_n} THETA_M={toy.theta_m} carried into {gpath.name} (G1 §1)")
    genome_text = gpath.read_text(); genome = parse_genome(genome_text); (out / gpath.name).write_text(genome_text)
    if genome.gaze is None:
        raise GenomeError("G1 needs the GAZE gene ON")
    gate_path = gate_path0
    gate_rep = json.loads(gate_path.read_text()) if gate_path.exists() else {}
    R: Dict[str, object] = {"stamp": stamp, "kind": tag, "genome_file": gpath.name, "genome": genome_numbers(genome), "gaze": genome.gaze, "retina": list(genome.retina),
                            "prereg": "docs/G1-PREREG.md", "gate": {k: gate_rep.get(k) for k in ("choice", "plant", "ear", "overlap", "label") if k in gate_rep}}
    if gate_rep:
        R["gate"]["bands"] = {"within": gate_rep["retina"]["within"], "between": gate_rep["retina"]["between"], "closest_pair": gate_rep["retina"]["closest_pair"]}
    plant_showings = int(gate_rep.get("plant", {}).get("showings", PLANT_SHOWINGS))
    t_all = time.perf_counter()

    if his:
        H = load_his(genome)
        things, arr2, never = H["things"], [], H["withheld"]
        dev_rows, held, a2_rows, plant_rows, shuffle_words = H["dev"], H["held"], [], [], H["shuffle_words"]
        R["his"] = {"words": things, "withheld_for_Q5": never, "split": H["split"], "folders_short": H["short"], "unreadable": H["unreadable"],
                    "dev_pictures": len(dev_rows), "held_pictures": {w: len(v) for w, v in held.items()}}
        print(f"{tag} · {len(things)} words shown {things} · withheld for Q5: {never} · dev {len(dev_rows)} pictures · held-out {sum(len(v) for v in held.values())} (every {HOLD_EVERY}rd per word + all of {never})")
    else:
        things, arr2, dev_rows, held, a2_rows, plant_rows, shuffle_words, n_checked = toy_streams(genome, plant_showings)
        never = world.THING_NEVER
        R["streams"] = {"dev": len(dev_rows), "arr2": len(a2_rows), "plant": len(plant_rows), "held_checked_disjoint": n_checked, "planted_copy_caught": True, "things": things}
        print(f"{tag} · {len(things)} things on {genome.gaze['canvas']}×{genome.gaze['canvas']} canvases · {genome.gaze['fixations']} glances a showing · dev {len(dev_rows)} showings · arrival-2 {len(a2_rows)} · plant {len(plant_rows)} · held-out {n_checked} canvases disjoint (planted copy caught)")

    # ---- glance everything once per mode (the gaze runs once per picture)
    G: Dict[str, Dict[str, object]] = {}
    for mode in ("surprise", "random", "one"):
        t0 = time.perf_counter()
        G[mode] = {"dev": glance_rows(dev_rows, genome, mode), "a2": glance_rows(a2_rows, genome, mode), "plant": glance_rows(plant_rows, genome, mode), "held": glance_held(held, genome, mode)}
        print(f"glanced [{mode}] in {time.perf_counter() - t0:.1f} s")
    Gs = G["surprise"]
    kw = dict(never=never, with_arr2=bool(a2_rows), with_plant=bool(plant_rows))

    # ---- the design life, the replay
    design = live(genome, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], label="design", keep=True, **kw)
    org_design, ledger_design = design.pop("_org"), design.pop("_ledger")
    R["design"] = design
    key_final = "ask_final" if "ask_final" in design else ("ask_arr2" if "ask_arr2" in design else "ask_dev")
    A = design[key_final]
    print(f"DESIGN Q1 {A['Q1']['acc']:.3f} Q2 {A['Q2']['acc']:.2f} Q3 {A['Q3']['acc']:.3f} Q4 {A['Q4']['acc']:.3f} Q5 {never} abstain {A['Q5'].get(never, {}).get('abstain_rate', float('nan')):.2f} {A['Q5'].get(never, {}).get('abstain')} false-abst {A['Q1']['false_abstention']:.3f} | {design['seconds']} s")
    s = design["at_final"]
    print(f"       cells {s['cells_sight']}+{s['cells_words']} born {s['cells_born_sight']}+{s['cells_born_words']} (novelty {s['births_novelty_sight']} error {s['births_error_sight']} refused budget {s['births_refused_budget']} redundant {s['births_refused_redundant']}) edges born {s['edges_born']} pruned {s['edges_pruned']} merged {s['cells_merged_sight']}+{s['cells_merged_words']} | cross {design['edges_cross']} | births by glance {design.get('births_by_glance')}")
    if "plant" in design:
        print(f"       plant answered {design['plant']['answered_rate']:.2f} as {design['plant']['answered_as']} | null abstain {design['null_plant']['abstain_rate']:.2f} as {design['null_plant']['answered_as']} | arrival-2 new things Q1 {design['ask_arr2_new']['Q1']['acc']:.3f}")
    replay = live(genome, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], label="replay", **kw)
    R["replay_identical"] = replay["hash_final"] == design["hash_final"]; R["design_hash"] = design["hash_final"]
    print(f"REPLAY byte-identical: {R['replay_identical']}")

    # ---- twins
    tw: Dict[str, object] = {}
    tw["T-random-gaze"] = live(genome, G["random"]["dev"], G["random"]["a2"], G["random"]["plant"], things, arr2, G["random"]["held"], label="T-random-gaze", **kw)
    tw["T-one-glance"] = live(genome, G["one"]["dev"], G["one"]["a2"], G["one"]["plant"], things, arr2, G["one"]["held"], label="T-one-glance", **kw)
    for name in ("T-random-gaze", "T-one-glance"):
        r = tw[name]; a = r[key_final]; print(f"{name.upper()}: Q1 {a['Q1']['acc']:.3f} abstain {a['Q1']['abstain']} Q2 {a['Q2']['acc']:.2f} Q3 {a['Q3']['acc']:.3f} Q4 {a['Q4']['acc']:.3f} | cells {r['at_final']['cells_sight']} born {r['at_final']['cells_born_sight']} refused {r['at_final']['births_refused_budget']} | {r['seconds']} s")
    tw["T-shuffle-5"] = live(genome, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], shuffle_words=shuffle_words, label="T-shuffle-5", **{**kw, "with_plant": False})
    tw["T-frozen"] = live(genome, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], frozen_after=10, label="T-frozen", **{**kw, "with_plant": False})
    tw["T-nowire"] = live(genome, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], wire=False, label="T-nowire", **{**kw, "with_plant": False})
    key_tw = "ask_arr2" if a2_rows else "ask_dev"
    for name in ("T-shuffle-5", "T-frozen", "T-nowire"):
        r = tw[name]; a = r[key_tw]; print(f"{name.upper()}: Q1 {a['Q1']['acc']:.3f} abstain {a['Q1']['abstain']} Q2 {a['Q2']['acc']:.2f} | cells {r['at_final']['cells_sight']} edges {r['at_final']['edges_alive']} refused {r['at_final']['births_refused_budget']}")
    R["twins"] = tw

    # ---- the smaller life ((iv)'s third clause): five things on the toy, the first half of his words
    if his:
        five = things[: max(2, (len(things) + 1) // 2)]
        dev5 = [row for row in dev_rows if row[0] in five]; held5 = {t: held[t] for t in five}; held5[never] = held[never]
        d5 = glance_rows(dev5, genome, "surprise"); h5 = glance_held(held5, genome, "surprise")
    else:
        five = things[:5]; per5 = PER_THING * len(things) // 5
        dev5 = world.stream_canvas(five, per5, np.random.default_rng(21)); held5 = world.holdout_canvas(five + [never], HELD_N, np.random.default_rng(22))
        d5 = glance_rows(dev5, genome, "surprise"); h5 = glance_held(held5, genome, "surprise")
    l5 = live(genome, d5, [], [], five, [], h5, never, with_arr2=False, with_plant=False, label="smaller-life")
    R["smaller_life"] = l5; R["smaller_life_things"] = five
    print(f"SMALLER LIFE ({len(five)} things, {len(d5)} showings): cells born {l5['at_dev']['cells_born_sight']} vs the full world's {design['at_dev']['cells_born_sight']} at the end of development · Q1 {l5['ask_dev']['Q1']['acc']:.3f}")

    # ---- 20 random genomes (the GAZE gene fixed)
    rg = []
    for seed in range(1, RANDOM_GENOMES + 1):
        g = random_genome(genome, seed)
        r = live(g, Gs["dev"], Gs["a2"], Gs["plant"], things, arr2, Gs["held"], ask_at_dev=not a2_rows, label=f"random-{seed}", **{**kw, "with_plant": False})
        a = r[key_tw]
        rg.append({"seed": seed, "genome": genome_numbers(g), "composite": a["composite"], "Q1": a["Q1"]["acc"], "Q2": a["Q2"]["acc"], "Q3": a["Q3"]["acc"], "Q4": a["Q4"]["acc"],
                   "cells": r["at_final"]["cells_sight"], "refused": r["at_final"]["births_refused_budget"], "seconds": r["seconds"]})
        print(f"RANDOM {seed:2d}: composite {a['composite']:.3f} Q1 {a['Q1']['acc']:.3f} Q2 {a['Q2']['acc']:.2f} Q3 {a['Q3']['acc']:.3f} Q4 {a['Q4']['acc']:.3f} | theta_n {g.theta_n:.3f} kwta {g.kwta} lr {g.lr:.3f} budget {g.budget} | cells {rg[-1]['cells']} | {r['seconds']} s")
    R["random_genomes"] = rg

    # ---- the marks (G1 §3), bars as written; (iv) reported on the toy, gating on his pictures; (v), (x) only where gradable
    D = A; d_dev = design["ask_dev"]; s = design["at_final"]
    comps = sorted([x["composite"] for x in rg] + [D["composite"]], reverse=True); rank = comps.index(D["composite"]) + 1
    one = tw["T-one-glance"][key_final]
    M: Dict[str, Dict[str, object]] = {
        "i_answers": {"pass": D["Q1"]["acc"] >= .80 and D["Q2"]["acc"] >= .80 and D["Q3"]["acc"] >= .85 and D["Q4"]["acc"] >= .90, "Q1": D["Q1"]["acc"], "Q2": D["Q2"]["acc"], "Q3": D["Q3"]["acc"], "Q3_ceiling": D["Q3"]["ceiling"], "Q4": D["Q4"]["acc"],
                      "counts": {"Q1": f"{D['Q1']['correct']}/{D['Q1']['n']}", "Q2": f"{D['Q2']['correct']}/{D['Q2']['n']}", "Q3": f"{D['Q3']['correct']}/{D['Q3']['n']}", "Q4": f"{D['Q4']['correct']}/{D['Q4']['n']}"}, "bars": "Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90"},
        "ii_meeting_real": {"pass": tw["T-shuffle-5"][key_tw]["Q1"]["acc"] <= .20 and tw["T-nowire"][key_tw]["Q1"]["acc"] <= .20, "T_shuffle_Q1": tw["T-shuffle-5"][key_tw]["Q1"]["acc"], "T_nowire_Q1": tw["T-nowire"][key_tw]["Q1"]["acc"], "T_nowire_abstain": tw["T-nowire"][key_tw]["Q1"]["abstain"], "bar": "≤ .20"},
        "iii_growth_matters": {"pass": tw["T-frozen"][key_tw]["Q1"]["acc"] <= D["Q1"]["acc"] - .30, "T_frozen_Q1": tw["T-frozen"][key_tw]["Q1"]["acc"], "design_Q1": D["Q1"]["acc"], "bar": "≥ 30 pp under"},
        "iv_grows_alone": {"gating": his, "cells_born": s["cells_born_sight"] + s["cells_born_words"], "births_refused_budget": s["births_refused_budget"], "smaller_life_born": l5["at_dev"]["cells_born_sight"], "full_world_born_at_dev": design["at_dev"]["cells_born_sight"],
                           "edges_born": s["edges_born"], "edges_pruned": s["edges_pruned"], "pruned_share": (s["edges_pruned"] / s["edges_born"]) if s["edges_born"] else 0.0, "removed_for_disuse": s["removed_for_disuse"],
                           "edges_cross": design["edges_cross"], "births_by_glance": design.get("births_by_glance"), "bars": "≥ 50 born · 0 refused · smaller life < full world · ≥ 5 % pruned · 0 by disuse"},
        "v_keeps": {"gradable": bool(a2_rows), "Q1_at_dev": d_dev["Q1"]["acc"], "Q1_after_arrival2": design.get("ask_arr2", {}).get("Q1", {}).get("acc"),
                    "correct_at_dev": d_dev["Q1"]["correct"], "correct_after_arrival2": design.get("ask_arr2", {}).get("Q1", {}).get("correct"), "n": d_dev["Q1"]["n"],
                    "allowed_loss": int(math.ceil(0.05 * d_dev["Q1"]["n"])), "bar": "within 5 pp, read in COUNTS: lost ≤ ceil(0.05 · n)"},
        "vi_knows_unknown": {"Q5_abstain": D["Q5"].get(never, {}).get("abstain_rate"), "Q5_abstain_by": D["Q5"].get(never, {}).get("abstain"), "Q5_answered_as": D["Q5"].get(never, {}).get("answered_as"), "Q5_n": D["Q5"].get(never, {}).get("n"),
                             "false_abstention_seen": D["Q1"]["false_abstention"], "false_abstention_by": D["Q1"]["abstain"], "bars": "plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20"},
        "vii_replay": {"pass": R["replay_identical"], "hash": design["hash_final"][:16]},
        "viii_cost": {"pass": design["seconds"] <= COST_BAR_S, "seconds_design_life": design["seconds"], "bar": f"≤ {COST_BAR_S} s"},
        "ix_not_luck": {"pass": rank <= 5, "rank_of_design": rank, "of": len(comps), "design_composite": D["composite"], "best_random": max(x["composite"] for x in rg), "best_random_seed": max(rg, key=lambda x: x["composite"])["seed"], "bar": "rank ≤ 5 of 21"},
        "xi_gaze_earns_place": {"pass": D["Q1"]["acc"] - one["Q1"]["acc"] >= .10, "Q1_gaze": D["Q1"]["acc"], "Q1_one_glance": one["Q1"]["acc"], "margin": D["Q1"]["acc"] - one["Q1"]["acc"], "bar": "≥ .10"},
        "untested_SCALE": {"scale_events": s["scale_events"], "note": f"SCALE every {genome.scale_every} fired {s['scale_events']} times in a {s['moments']}-moment life"},
    }
    M["iv_grows_alone"]["pass"] = (M["iv_grows_alone"]["cells_born"] >= 50 and s["births_refused_budget"] == 0 and l5["at_dev"]["cells_born_sight"] < design["at_dev"]["cells_born_sight"] and M["iv_grows_alone"]["pruned_share"] >= .05 and s["removed_for_disuse"] == 0)
    if a2_rows:
        M["v_keeps"]["pass"] = design["ask_arr2"]["Q1"]["correct"] >= d_dev["Q1"]["correct"] - M["v_keeps"]["allowed_loss"]   # counts, never a float tie
    if plant_rows:
        M["vi_knows_unknown"].update({"plant_answered": design["plant"]["answered_rate"], "plant_answered_as": design["plant"]["answered_as"], "null_abstain": design["null_plant"]["abstain_rate"], "null_answered_as": design["null_plant"]["answered_as"]})
        M["vi_knows_unknown"]["pass"] = design["plant"]["answered_rate"] > .5 and design["null_plant"]["abstain_rate"] > .5 and D["Q5"][never]["abstain_rate"] >= .80 and D["Q1"]["false_abstention"] <= .20
    else:
        nul = org_design.recall_many("words", [world.encode_word(world.THING_NULL, genome.ear_blank_zero)])
        M["vi_knows_unknown"].update({"plant": "none on his pictures (G1 §2)", "null_vex_on_the_ear": nul["reason"]})
        M["vi_knows_unknown"]["pass"] = nul["cell"] is None and D["Q5"][never]["abstain_rate"] >= .80 and D["Q1"]["false_abstention"] <= .20
    if not his:
        Lx = landing(Gs["held"], things); Lr = landing(G["random"]["held"], things)
        ceiling = 1.0 - (1.0 - 9.0 / 256.0) ** 2
        M["x_gaze_finds_thing"] = {"pass": Lx["rate"] >= .90 and Lx["rate"] >= 1.5 * Lr["rate"], "gaze_rate": Lx["rate"], "gaze_hit": f"{Lx['hit']}/{Lx['n']}", "random_rate": Lr["rate"], "random_hit": f"{Lr['hit']}/{Lr['n']}", "random_ceiling_expected": ceiling, "ratio": (Lx["rate"] / Lr["rate"]) if Lr["rate"] else float("inf"), "per_thing": Lx["per_thing"], "bar": "≥ .90 within the first 2 fixations · ≥ 1.5× random"}
    gating = [k for k in M if k != "untested_SCALE" and "pass" in M[k] and not (k == "iv_grows_alone" and not his)]
    R["marks"] = M; R["gating_marks"] = gating
    R["verdict"] = "PASS" if all(M[k]["pass"] for k in gating) else "FAIL"
    R["marks_failed"] = [k for k in gating if not M[k]["pass"]]
    R["seconds_total"] = round(time.perf_counter() - t_all, 1)
    org_design.save(out / "organism.npz"); (out / "ledger.json").write_text(json.dumps(ledger_design))
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str))
    write_verdict(out, R, genome, his)
    print(f"VERDICT {R['verdict']} — failed: {R['marks_failed'] or 'none'} — {out} ({R['seconds_total']} s)")
    return 0


# ----------------------------------------------------------------------------- the verdict page
def write_verdict(out: Path, R: Dict[str, object], genome: Genome, his: bool) -> None:
    M = R["marks"]; d = R["design"]; tw = R["twins"]
    amended = str(R.get("gaze", {}).get("ink")) == "border"
    kind = "G1-his (his pictures)" if his else ("G1b-toy (canvases, known truth; §6 amendment 1, ink border)" if amended else "G1-toy (canvases, known truth; ink contrast — the first run)")
    P6 = {"i": "§6: Q1 ≥ .80 (the trio separates; circle/diamond may stay close)", "ii": "PASS", "iii": "PASS", "iv": "§6: reported; §4 said under 5 % — MISSED on the first run (54.6 %)", "v": "§6: uncertain (triangle→tree, diamond→house are a context fact)", "vi": "§6: the null plant abstains ≥ .5", "vii": "PASS", "viii": "PASS", "ix": "unknown", "x": "PASS as before", "xi": "PASS as before"}
    P = P6 if amended else {"i": "PASS on the toy; his: unknown", "ii": "PASS", "iii": "PASS", "iv": "toy: births above G0b's 86, refusals possible, pruning under 5 % — REPORTED; his: GATING, unknown", "v": "PASS (toy); not gradable on his pictures", "vi": "plant PASS, spiral uncertain (toy); his: unknown", "vii": "PASS", "viii": "PASS", "ix": "unknown", "x": "PASS: first fixation on the thing on > 95 %; random near 0.07", "xi": "PASS: one glance leaves the thing at 8 px; T-one-glance Q1 under 0.6"}
    def row(k, name, bar, read, pk):
        m = M[k]; p = m.get("pass"); g = k in R["gating_marks"]
        return f"| {name} | {bar} | {read} | {'—' if p is None else p}{'' if g else ' (reported, not gating)'} | {P[pk]} |"
    pred_src = "§6" if amended else "§4"
    L = [f"# G1 rung 1 — {kind} — VERDICT: **{R['verdict']}** (failed: {', '.join(R['marks_failed']) or 'none'}; gating marks: {', '.join(R['gating_marks'])})\n",
         f"run `{R['stamp']}` · genome `{R['genome_file']}` · PREREG docs/G1-PREREG.md · GAZE {R['gaze']} · every number below is read from results.json\n",
         f"## The marks, bars as written before the run (G1 §3), predictions of {pred_src} beside each\n", f"| mark | bar | read | pass | {pred_src} predicted |", "|---|---|---|---|---|"]
    m = M["i_answers"]; L.append(row("i_answers", "(i) it answers", m["bars"], f"Q1 {m['Q1']:.3f} ({m['counts']['Q1']}) · Q2 {m['Q2']:.2f} ({m['counts']['Q2']}) · Q3 {m['Q3']:.3f} ({m['counts']['Q3']}; ceiling {m['Q3_ceiling']:.3f}) · Q4 {m['Q4']:.3f} ({m['counts']['Q4']})", "i"))
    m = M["ii_meeting_real"]; L.append(row("ii_meeting_real", "(ii) the meeting is real", "T-shuffle, T-nowire Q1 ≤ .20", f"T-shuffle Q1 {m['T_shuffle_Q1']:.3f} · T-nowire Q1 {m['T_nowire_Q1']:.3f} (abstains {m['T_nowire_abstain']})", "ii"))
    m = M["iii_growth_matters"]; L.append(row("iii_growth_matters", "(iii) growth matters", "T-frozen ≥ 30 pp under (i)", f"T-frozen Q1 {m['T_frozen_Q1']:.3f} vs {m['design_Q1']:.3f}", "iii"))
    m = M["iv_grows_alone"]; L.append(row("iv_grows_alone", "(iv) it grows on its own", m["bars"], f"born {m['cells_born']} · refused {m['births_refused_budget']} · smaller life {m['smaller_life_born']} vs full {m['full_world_born_at_dev']} · pruned {m['edges_pruned']}/{m['edges_born']} = {100 * m['pruned_share']:.1f} % (cross-thing born {m['edges_cross']['born']}, pruned {m['edges_cross']['pruned']}) · disuse {m['removed_for_disuse']} · births by glance {m['births_by_glance']}", "iv"))
    m = M["v_keeps"]; L.append(row("v_keeps", "(v) it keeps what it learned", m["bar"], (f"Q1 {m['Q1_at_dev']:.3f} → {m['Q1_after_arrival2']:.3f} ({m['correct_at_dev']} → {m['correct_after_arrival2']} of {m['n']}; lost {m['correct_at_dev'] - m['correct_after_arrival2']}, allowed {m['allowed_loss']})" if m["gradable"] else "not gradable (one arrival)"), "v"))
    m = M["vi_knows_unknown"]; L.append(row("vi_knows_unknown", "(vi) it knows what it does not know", m["bars"], (f"plant answered {m['plant_answered']:.2f} (as {m['plant_answered_as']}) · null abstains {m['null_abstain']:.2f} (as {m['null_answered_as']}) · " if "plant_answered" in m else f"{m.get('plant')} · «vex» on the ear: {m.get('null_vex_on_the_ear')} · ") + f"Q5 abstains {m['Q5_abstain']:.2f} of {m['Q5_n']} (by {m['Q5_abstain_by']}; answered as {m['Q5_answered_as']}) · false abstention {m['false_abstention_seen']:.3f} (by {m['false_abstention_by']})", "vi"))
    m = M["vii_replay"]; L.append(row("vii_replay", "(vii) replay", "two lives byte-identical", f"identical {m['pass']} (hash {m['hash']})", "vii"))
    m = M["viii_cost"]; L.append(row("viii_cost", "(viii) cost", m["bar"], f"{m['seconds_design_life']} s a design life, one process — EXCLUDES the glancing (the gaze + the eye run ONCE per picture before any life: see the log's 'glanced' lines, ~10 s for all pictures); G0b's seconds included its retina", "viii"))
    m = M["ix_not_luck"]; L.append(row("ix_not_luck", "(ix) not luck", m["bar"], f"rank {m['rank_of_design']} of {m['of']} (design {m['design_composite']:.3f}; best random {m['best_random']:.3f}, seed {m['best_random_seed']})", "ix"))
    if "x_gaze_finds_thing" in M:
        m = M["x_gaze_finds_thing"]; L.append(row("x_gaze_finds_thing", "(x) the gaze finds the thing", m["bar"], f"gaze {m['gaze_rate']:.3f} ({m['gaze_hit']}) · random twin {m['random_rate']:.3f} ({m['random_hit']}; expected ceiling {m['random_ceiling_expected']:.3f}) · ratio {m['ratio']:.1f}×", "x"))
    else:
        L.append("| (x) the gaze finds the thing | — | not gradable on his pictures (no truth for the thing's position) | — | — |")
    m = M["xi_gaze_earns_place"]; L.append(row("xi_gaze_earns_place", "(xi) the gaze earns its place", "Q1(gaze) − Q1(one glance) ≥ .10", f"gaze {m['Q1_gaze']:.3f} − one glance {m['Q1_one_glance']:.3f} = {m['margin']:+.3f}", "xi"))
    L.append(f"\nSCALE: {M['untested_SCALE']['note']} — UNTESTED.\n")
    if his:
        H = R["his"]; L.append(f"## His world\nWords shown: {H['words']} · withheld for Q5: **{H['withheld_for_Q5']}** · development pictures {H['dev_pictures']} · held-out per word {H['held_pictures']} · folders short of the minimum: {H['folders_short'] or 'none'} · unreadable: {H['unreadable'] or 'none'}\n")
    gt = R.get("gate", {})
    if gt.get("bands"):
        b = gt["bands"]; L.append(f"## Gate G-a on the first-fixation glances ({gt.get('label')})\nwithin-thing: median {b['within']['median']:.3f} p5 {b['within']['p5']:.3f} p95 {b['within']['p95']:.3f} · between-thing: median {b['between']['median']:.3f} p95 {b['between']['p95']:.3f} max {b['between']['max']:.3f} · closest pair {b['closest_pair']['pair']} p95 {b['closest_pair']['p95']:.3f} · strict rule {'MET' if gt['choice']['strict']['met'] else 'NOT MET'} · THETA_N {gt['choice'].get('theta_n')} THETA_M {gt['choice'].get('theta_m')}" + (f" · plant showings {gt['plant']['showings']} (p_res {gt['plant']['p_res_at_theta_n']:.3f})" if gt.get("plant") else "") + ("\n**The bands OVERLAP under the INK rule — thetas not written; the run used the toy's.**" if gt.get("overlap") else "") + "\n")
    s = d["at_final"]
    L.append(f"## The design life\n{s['moments']} moments ({R['gaze']['fixations']} glances a showing) · cells {s['cells_sight']}+{s['cells_words']} (born {s['cells_born_sight']}+{s['cells_born_words']}: novelty {s['births_novelty_sight']}/{s['births_novelty_words']}, error {s['births_error_sight']}/{s['births_error_words']}; refused budget {s['births_refused_budget']}, redundant {s['births_refused_redundant']}) · edges born {s['edges_born']} pruned {s['edges_pruned']} alive {s['edges_alive']} · merged {s['cells_merged_sight']}+{s['cells_merged_words']} · multi-thing sight cells {d['multi_thing_sight_cells']} · ledger-corruption plant left the organism unchanged: {d['ledger_corruption_hash_unchanged']} · cells per thing {d['cells_per_thing']} · {d['seconds']} s\n")
    L.append("## Twins (each blind to exactly one thing)\n")
    for name, r in tw.items():
        k = "ask_final" if "ask_final" in r else ("ask_arr2" if "ask_arr2" in r else "ask_dev"); a = r[k]; st = r["at_final"]
        L.append(f"- **{name}**: Q1 {a['Q1']['acc']:.3f} (abstain {a['Q1']['abstain']}) Q2 {a['Q2']['acc']:.2f} Q3 {a['Q3']['acc']:.3f} Q4 {a['Q4']['acc']:.3f} · cells {st['cells_sight']} born {st['cells_born_sight']} refused {st['births_refused_budget']} · edges born {st['edges_born']} pruned {st['edges_pruned']} · error births {st['births_error_sight']} merges {st['cells_merged_sight']} · {r['seconds']} s")
    l5 = R["smaller_life"]; L.append(f"- **smaller life** ({len(R['smaller_life_things'])} things {R['smaller_life_things']}, {l5['at_dev']['moments']} moments): cells born {l5['at_dev']['cells_born_sight']} vs the full world's {d['at_dev']['cells_born_sight']} at the end of development; Q1 {l5['ask_dev']['Q1']['acc']:.3f}.\n")
    L.append("## 20 random genomes within the declared bounds (the GAZE gene fixed)\n| seed | composite | Q1 | Q2 | Q3 | Q4 | θN | kwta | lr | budget | cells |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for x in R["random_genomes"]:
        g = x["genome"]; L.append(f"| {x['seed']} | {x['composite']:.3f} | {x['Q1']:.3f} | {x['Q2']:.2f} | {x['Q3']:.3f} | {x['Q4']:.3f} | {g.get('theta_n', 0):.3f} | {g.get('kwta')} | {g.get('lr', 0):.3f} | {g.get('budget')} | {x['cells']} |")
    L.append(f"\n**Read as written.** {kind}: {R['verdict']}; failed {R['marks_failed'] or 'none'}. Whole run {R['seconds_total']} s.\n")
    (out / "VERDICT.md").write_text("\n".join(L))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
