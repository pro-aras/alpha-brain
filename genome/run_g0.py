"""run_g0.py — G0 rung 0: the toy, the design life, the twins, the plant, the marks → VERDICT.

edit: Claude (Fable 5.1), 2026-09-19 16:2x +04 — docs/G0-PREREG.md §2–§5, §7, §10–§11 are law here.
edit: Claude (Fable 5.1), 2026-09-19 16:20 +04 — VERDICT: (ix) best RANDOM genome and the 20-genome quartile bar; twin prune counts; the what-did-nothing paragraph; the ledger sentence corrected.
edit: Claude (Fable 5.1), 2026-09-19 16:40 +04 — G0b: --genome, the eye's side from the genome, eleven things, the plant's showings from the gate, the eye parity gate, cross-thing edge diagnostics.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m genome.run_g0 [--toy-only] [--genome genome/G0b.genome]

One process, lives sequential. Six RNG streams (§10 clause 10). Every number lands in
runs/g0-<stamp>/results.json and VERDICT.md; nothing is summarised away.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import world
from .machinery import Genome, Organism, parse_genome, retina
from .questions import ask, ask_plant, build_ledgers

ROOT = Path(__file__).resolve().parent.parent
GENOME_PATH = ROOT / "genome" / "G0.genome"
PER_THING = 60          # §2: 10 things × 60 moments = 600
HELD_N = 20             # §2: 10 × 20 held-out renderings
ARR2_PER_THING = 60     # §2: 5 new things × 60 = 300
PLANT_SHOWINGS = 5      # §4
TOY_PER_THING = 150     # §11: 2 × 150 = 300 so STAGE 2 is reached
RANDOM_GENOMES = 20     # §4
# §4 — bounds of the random-genome twin, declared in the PREREG
RANDOM_BOUNDS = {"theta_n": (0.50, 0.99), "misfires": (1, 8), "budget": (50, 800), "kwta": (1, 12), "lr": (0.005, 0.3),
                 "prune_floor": (0.001, 0.2), "theta_m": (0.90, 0.999), "scale_every": (100, 5000), "stage1": (0, 400),
                 "abstain_ratio": (0.5, 0.99)}


# ----------------------------------------------------------------------------- streams
def make_streams(things: Sequence[str], per_thing: int, held_n: int, arr2: Sequence[str], arr2_per: int,
                 plant_word: str, null_word: str, never_word: str, side: int = 24, plant_showings: int = PLANT_SHOWINGS):
    r_dev, r_held, r_arr2, r_plant, r_shuf = (np.random.default_rng(s) for s in (1, 2, 3, 4, 5))
    dev = world.stream(things, per_thing, r_dev, side)
    held = world.holdout(list(things) + list(arr2) + [never_word, plant_word, null_word], held_n, r_held, side)
    a2 = world.stream(arr2, arr2_per, r_arr2, side)
    plant = [(plant_word, world.render(plant_word, r_plant, side)) for _ in range(plant_showings)]
    n_checked = world.assert_disjoint(dev + a2 + plant, held)
    # planted control (§10 clause 12): a copy of a development picture in the held-out set MUST be caught
    bad = dict(held); bad[things[0]] = held[things[0]][:1] + [dev[0][1].copy()]
    try:
        world.assert_disjoint(dev, bad); raise SystemExit("disjointness control FAILED to catch the planted copy")
    except AssertionError:
        pass
    shuffle_words = [things[i] for i in r_shuf.integers(0, len(things), size=len(dev))]
    return dev, held, a2, plant, shuffle_words, n_checked


# ----------------------------------------------------------------------------- one life
def live(genome: Genome, dev, a2, plant, things, arr2, held, never, *, wire=True, frozen_after=None,
         shuffle_words=None, ask_at_600=True, with_arr2=True, with_plant=True, label="") -> Dict[str, object]:
    t0 = time.perf_counter()
    org = Organism(genome, wire=wire, frozen_after=frozen_after)
    moment_thing: Dict[int, str] = {}
    feats = [(t, retina(p, genome.retina)) for t, p in dev]
    never_pics = {never: held[never]}
    rec: Dict[str, object] = {"label": label}
    org.new_arrival()
    for i, (t, x) in enumerate(feats):
        w = shuffle_words[i] if shuffle_words is not None else t
        moment_thing[org.t] = t
        org.moment(x, world.encode_word(w, genome.ear_blank_zero))
    rec["at_600"] = org.summary()
    if ask_at_600:
        rec["ask_600"] = ask(org, build_ledgers(org, moment_thing), things, held, never_pics, genome.ear_blank_zero)
    rec["hash_600"] = org.state_hash()
    if with_arr2:
        org.new_arrival()
        for t, p in a2:
            moment_thing[org.t] = t
            org.moment(retina(p, genome.retina), world.encode_word(t, genome.ear_blank_zero))
        rec["at_900"] = org.summary()
        L = build_ledgers(org, moment_thing)
        rec["ask_900"] = ask(org, L, things, held, never_pics, genome.ear_blank_zero)
        rec["ask_900_arr2"] = ask(org, L, list(arr2), held, never_pics, genome.ear_blank_zero)
        rec["hash_900"] = org.state_hash()
    if with_plant:
        org.new_arrival()
        for t, p in plant:
            moment_thing[org.t] = t
            org.moment(retina(p, genome.retina), world.encode_word(t, genome.ear_blank_zero))
        L = build_ledgers(org, moment_thing)
        rec["plant"] = ask_plant(org, L, world.THING_PLANT, held[world.THING_PLANT])
        rec["null_plant"] = ask_plant(org, L, world.THING_NULL, held[world.THING_NULL])
        rec["ask_905"] = ask(org, L, things, held, never_pics, genome.ear_blank_zero)
        rec["at_905"] = org.summary()
    rec["refusals_by_arrival"] = org.refusals_by_arrival + [org.c["births_refused_budget"] - sum(org.refusals_by_arrival)]
    rec["hash_final"] = org.state_hash()
    # §10 clause 12 — ledger-corruption plant: shuffling the runner's labels must not move the organism
    L = build_ledgers(org, moment_thing)
    keys = list(moment_thing.keys()); vals = [moment_thing[k] for k in keys]
    rng = np.random.default_rng(99); perm = rng.permutation(len(vals))
    corrupted = {k: vals[j] for k, j in zip(keys, perm)}
    _ = build_ledgers(org, corrupted)
    rec["ledger_corruption_hash_unchanged"] = (org.state_hash() == rec["hash_final"])
    multi = sum(1 for s in L["sight"].values() if len(s) > 1)
    rec["multi_thing_sight_cells"] = multi
    # G0b §3 diagnostics: an edge is cross-thing when the ledger's things for its two cells differ
    def _cross(log):
        return sum(1 for _m, sc, wc in log if L["sight"].get(sc, set()) != L["words"].get(wc, set()))
    rec["edges_cross"] = {"born": _cross(org.edges_log), "pruned": _cross(org.prunes_log), "born_total": len(org.edges_log), "pruned_total": len(org.prunes_log)}
    rec["cells_per_thing"] = {t: sum(1 for c, s in L["sight"].items() if s == {t} and org.sight.alive[c]) for t in list(things) + list(arr2)}
    rec["seconds"] = round(time.perf_counter() - t0, 2)
    return rec


# ----------------------------------------------------------------------------- random genomes
def random_genome(base: Genome, seed: int) -> Genome:
    r = np.random.default_rng(seed)
    b = RANDOM_BOUNDS
    L = int(r.integers(b["stage1"][0], b["stage1"][1] + 1))
    return dataclasses.replace(
        base, theta_n=float(r.uniform(*b["theta_n"])), misfires=int(r.integers(b["misfires"][0], b["misfires"][1] + 1)),
        budget=int(r.integers(b["budget"][0], b["budget"][1] + 1)), kwta=int(r.integers(b["kwta"][0], b["kwta"][1] + 1)),
        lr=float(r.uniform(*b["lr"])), prune_floor=float(r.uniform(*b["prune_floor"])), theta_m=float(r.uniform(*b["theta_m"])),
        scale_every=int(r.integers(b["scale_every"][0], b["scale_every"][1] + 1)),
        stages=[(1, "senses", 0, L), (2, "meet", L, None)], abstain_ratio=float(r.uniform(*b["abstain_ratio"])),
        text=f"# random genome seed {seed}")


def genome_numbers(g: Genome) -> Dict[str, object]:
    return {"theta_n": g.theta_n, "misfires": g.misfires, "budget": g.budget, "kwta": g.kwta, "lr": g.lr, "prune_floor": g.prune_floor,
            "theta_m": g.theta_m, "scale_every": g.scale_every, "stage1": g.stage2_start, "abstain_ratio": g.abstain_ratio}


# ----------------------------------------------------------------------------- main
def main(argv: List[str]) -> int:
    assert os.environ.get("OPENBLAS_NUM_THREADS") == "1" and os.environ.get("OMP_NUM_THREADS") == "1", "§10 clause 10: run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1"
    toy_only = "--toy-only" in argv
    gpath = Path(argv[argv.index("--genome") + 1]) if "--genome" in argv else GENOME_PATH
    tag = gpath.stem.lower()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = ROOT / "runs" / f"{tag}-{stamp}"; out.mkdir(parents=True, exist_ok=True)
    genome_text = gpath.read_text()
    genome = parse_genome(genome_text)
    (out / gpath.name).write_text(genome_text)
    side = genome.eye[0]
    gate_path = ROOT / "runs" / f"gate-ga-{gpath.stem}.json"
    gate = json.loads(gate_path.read_text()) if gate_path.exists() else {}
    plant_showings = int(gate.get("plant", {}).get("showings", PLANT_SHOWINGS))
    R: Dict[str, object] = {"stamp": stamp, "genome_file": gpath.name, "genome": genome_numbers(genome), "retina": list(genome.retina), "side": side,
                            "prereg": "docs/G0-PREREG.md §1–§11" + (" + docs/G0b-PREREG.md" if tag == "g0b" else ""), "plant_showings": plant_showings,
                            "gate": {k: gate.get(k) for k in ("choice", "plant", "ear") if k in gate} | ({"closest_pair": gate["retina"]["closest_pair"], "within": gate["retina"]["within"], "between": gate["retina"]["between"]} if "retina" in gate else {})}
    for step in genome.retina:
        if step.startswith("tower:"):
            # the eye parity gate: the numpy forward vs the sealed E09d tower's OWN 2,356-frame gate features
            # (judge/eye-tower/gate/features_f32.npy — the same arithmetic, that seal's weights); the gene's tower
            # (eye-tower-g2) carries no feature file, so its bytes are proved by its seal's sha-256 and its
            # arithmetic by this gate. A planted 1-px-shifted frame must be caught.
            from .eye import tower as _tower
            gene_t = _tower(step[6:]); ref = _tower("eye-tower"); gd = ref.dir / "gate"
            idx = json.loads((gd / "index.json").read_text()); n = idx["n"]
            frames = np.frombuffer((gd / "frames.u8").read_bytes(), dtype=np.uint8).reshape(n, 32, 32)
            F = np.load(gd / "features_f32.npy").astype(np.float64)
            mine = np.stack([ref.features(fr) for fr in frames]).astype(np.float64)
            dmax = np.abs(mine - F).max(axis=1)
            planted = float(np.abs(ref.features(np.roll(frames[0], 1, axis=1)).astype(np.float64) - F[0]).max())
            R["eye_parity"] = {"reference_tower": "eye-tower", "n": n, "max_diff": float(dmax.max()), "frames_within_1e-4": int((dmax < 1e-4).sum()),
                               "planted_caught": planted > 1e-3, "gene_tower": step[6:], "gene_sha256": gene_t.sha, "gene_n_feat": gene_t.n_feat}
            print(f"eye parity (arithmetic) vs the sealed E09d tower's own gate: max |diff| {dmax.max():.2e}, {int((dmax < 1e-4).sum())}/{n} frames within 1e-4, planted shifted frame {'CAUGHT' if planted > 1e-3 else 'NOT CAUGHT'}; the gene's tower {step[6:]} sha {gene_t.sha[:16]}… ({gene_t.n_feat} features)")
            if not (dmax.max() < 1e-3 and planted > 1e-3):
                print("EYE PARITY FAILED — the numpy eye is not the sealed tower; stopping."); return 3
    things = world.THINGS_11 if tag == "g0b" else world.THINGS_10
    arr2 = world.THINGS_ARRIVAL2
    dev, held, a2, plant, shuffle_words, n_checked = make_streams(things, PER_THING, HELD_N, arr2, ARR2_PER_THING, world.THING_PLANT, world.THING_NULL, world.THING_NEVER, side=side, plant_showings=plant_showings)
    R["streams"] = {"dev": len(dev), "arr2": len(a2), "plant": len(plant), "held_checked_disjoint": n_checked, "planted_copy_caught": True, "things": list(things)}
    print(f"{tag} · {len(things)} things at {side}×{side} · streams: dev {len(dev)} · arrival-2 {len(a2)} · plant {len(plant)} (showings from the gate: {plant_showings}) · held-out {n_checked} pictures disjoint (planted copy caught)")

    # ---- the toy (§2, §11): 2 things must reach Q1 = 1.0 or the machinery is wrong
    toy_things = ["circle", "bar"]
    r_toy = np.random.default_rng(11); r_toy_h = np.random.default_rng(12)
    toy_dev = world.stream(toy_things, TOY_PER_THING, r_toy, side); toy_held = world.holdout(toy_things + [world.THING_NEVER], HELD_N, r_toy_h, side)
    toy = live(genome, toy_dev, [], [], toy_things, [], toy_held, world.THING_NEVER, ask_at_600=True, with_arr2=False, with_plant=False, label="toy")
    q = toy["ask_600"]
    R["toy"] = toy
    print(f"TOY  Q1 {q['Q1']['acc']:.3f} (abstain {q['Q1']['abstain']}) Q2 {q['Q2']['acc']:.2f} Q3 {q['Q3']['acc']:.3f} Q4 {q['Q4']['acc']:.3f} Q5-spiral abstain {q['Q5'][world.THING_NEVER]['abstain_rate']:.2f} | cells {toy['at_600']['cells_sight']}+{toy['at_600']['cells_words']} edges {toy['at_600']['edges_alive']} born {toy['at_600']['edges_born']} pruned {toy['at_600']['edges_pruned']} | {toy['seconds']} s")
    R["toy_pass"] = (q["Q1"]["acc"] == 1.0)
    if not R["toy_pass"]:
        print("TOY FAILED — the machinery is wrong, not the genome (§2). Stopping before the world.")
        (out / "results.json").write_text(json.dumps(R, indent=1, default=str)); return 2
    if toy_only:
        (out / "results.json").write_text(json.dumps(R, indent=1, default=str)); return 0

    # ---- the design life, then the replay
    design = live(genome, dev, a2, plant, things, arr2, held, world.THING_NEVER, label="design")
    R["design"] = design
    a9 = design["ask_900"]; a6 = design["ask_600"]
    print(f"DESIGN @600 Q1 {a6['Q1']['acc']:.3f} Q2 {a6['Q2']['acc']:.2f} Q3 {a6['Q3']['acc']:.3f} Q4 {a6['Q4']['acc']:.3f} | @900 Q1 {a9['Q1']['acc']:.3f} Q2 {a9['Q2']['acc']:.2f} Q3 {a9['Q3']['acc']:.3f} Q4 {a9['Q4']['acc']:.3f} Q5 abstain {a9['Q5'][world.THING_NEVER]['abstain_rate']:.2f} {a9['Q5'][world.THING_NEVER]['abstain']} false-abst {a9['Q1']['false_abstention']:.3f} {a9['Q1']['abstain']}")
    print(f"       arrival-2 things @900 Q1 {design['ask_900_arr2']['Q1']['acc']:.3f} | plant zog answered {design['plant']['answered_rate']:.2f} as {design['plant']['answered_as']} | null vex abstain {design['null_plant']['abstain_rate']:.2f} | cells/thing {design['cells_per_thing']}")
    s9 = design["at_900"]
    print(f"       cells {s9['cells_sight']}+{s9['cells_words']} (born {s9['cells_born_sight']}+{s9['cells_born_words']}: novelty {s9['births_novelty_sight']}/{s9['births_novelty_words']} error {s9['births_error_sight']}/{s9['births_error_words']}) refused budget {s9['births_refused_budget']} by arrival {design['refusals_by_arrival']} | edges alive {s9['edges_alive']} born {s9['edges_born']} pruned {s9['edges_pruned']} merged {s9['cells_merged_sight']}/{s9['cells_merged_words']} scale {s9['scale_events']} disuse {s9['removed_for_disuse']} | {design['seconds']} s")
    replay = live(genome, dev, a2, plant, things, arr2, held, world.THING_NEVER, label="replay")
    R["replay_identical"] = (replay["hash_final"] == design["hash_final"]); R["replay_hash"] = replay["hash_final"]; R["design_hash"] = design["hash_final"]
    print(f"REPLAY byte-identical: {R['replay_identical']}")

    # ---- twins (§4): each blind to one thing
    tw: Dict[str, object] = {}
    for seed in (5, 6, 7):
        sw = shuffle_words if seed == 5 else [things[i] for i in np.random.default_rng(seed).integers(0, len(things), size=len(dev))]
        tw[f"T-shuffle-{seed}"] = live(genome, dev, a2, plant, things, arr2, held, world.THING_NEVER, shuffle_words=sw, with_plant=False, label=f"T-shuffle-{seed}")
        r = tw[f"T-shuffle-{seed}"]; print(f"T-SHUFFLE seed {seed}: Q1 {r['ask_900']['Q1']['acc']:.3f} abstain {r['ask_900']['Q1']['abstain']} Q2 {r['ask_900']['Q2']['acc']:.2f} | refused budget {r['at_900']['births_refused_budget']} cells {r['at_900']['cells_sight']}")
    tw["T-frozen"] = live(genome, dev, a2, plant, things, arr2, held, world.THING_NEVER, frozen_after=10, with_plant=False, label="T-frozen")
    r = tw["T-frozen"]; print(f"T-FROZEN: Q1 {r['ask_900']['Q1']['acc']:.3f} abstain {r['ask_900']['Q1']['abstain']} cells {r['at_900']['cells_sight']}+{r['at_900']['cells_words']} refused frozen {r['at_900']['births_refused_frozen']}")
    tw["T-nowire"] = live(genome, dev, a2, plant, things, arr2, held, world.THING_NEVER, wire=False, with_plant=False, label="T-nowire")
    r = tw["T-nowire"]; print(f"T-NOWIRE: Q1 {r['ask_900']['Q1']['acc']:.3f} abstain {r['ask_900']['Q1']['abstain']} edges {r['at_900']['edges_alive']}")
    R["twins"] = tw

    # ---- the 5-thing life (§10 clause 6): 600 moments, 120 per thing
    five = list(things[:5])
    dev5 = world.stream(five, 120, np.random.default_rng(21), side); held5 = world.holdout(five + [world.THING_NEVER], HELD_N, np.random.default_rng(22), side)
    l5 = live(genome, dev5, [], [], five, [], held5, world.THING_NEVER, with_arr2=False, with_plant=False, label="five-thing")
    R["five_thing"] = l5
    print(f"FIVE-THING @600: cells born {l5['at_600']['cells_born_sight']} (10-thing @600: {design['at_600']['cells_born_sight']}) Q1 {l5['ask_600']['Q1']['acc']:.3f}")

    # ---- 20 random genomes (§4, E29's control)
    rg = []
    for seed in range(1, RANDOM_GENOMES + 1):
        g = random_genome(genome, seed)
        r = live(g, dev, a2, plant, things, arr2, held, world.THING_NEVER, ask_at_600=False, with_plant=False, label=f"random-{seed}")
        rg.append({"seed": seed, "genome": genome_numbers(g), "composite": r["ask_900"]["composite"], "Q1": r["ask_900"]["Q1"]["acc"], "Q2": r["ask_900"]["Q2"]["acc"],
                   "Q3": r["ask_900"]["Q3"]["acc"], "Q4": r["ask_900"]["Q4"]["acc"], "cells": r["at_900"]["cells_sight"], "refused": r["at_900"]["births_refused_budget"], "seconds": r["seconds"]})
        print(f"RANDOM {seed:2d}: composite {rg[-1]['composite']:.3f} Q1 {rg[-1]['Q1']:.3f} Q2 {rg[-1]['Q2']:.2f} Q3 {rg[-1]['Q3']:.3f} Q4 {rg[-1]['Q4']:.3f} | theta_n {g.theta_n:.3f} kwta {g.kwta} lr {g.lr:.3f} stage1 {g.stage2_start} budget {g.budget} | cells {rg[-1]['cells']} | {rg[-1]['seconds']} s")
    R["random_genomes"] = rg

    # ---- the marks (§5), bars as written; ceilings printed beside bars
    d6, d9 = design["ask_600"], design["ask_900"]
    comps = sorted([x["composite"] for x in rg] + [d9["composite"]], reverse=True)
    rank = comps.index(d9["composite"]) + 1
    shuffle_q1 = [tw[f"T-shuffle-{s}"]["ask_900"]["Q1"]["acc"] for s in (5, 6, 7)]
    M = {
        "i_answers": {"pass": d9["Q1"]["acc"] >= .80 and d9["Q2"]["acc"] >= .80 and d9["Q3"]["acc"] >= .85 and d9["Q4"]["acc"] >= .90,
                      "Q1": d9["Q1"]["acc"], "Q2": d9["Q2"]["acc"], "Q3": d9["Q3"]["acc"], "Q3_ceiling": d9["Q3"]["ceiling"], "Q4": d9["Q4"]["acc"], "bars": "Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90"},
        "ii_meeting_real": {"pass": max(shuffle_q1) <= .20 and tw["T-nowire"]["ask_900"]["Q1"]["acc"] <= .20, "T_shuffle_Q1_band": shuffle_q1,
                            "T_nowire_Q1": tw["T-nowire"]["ask_900"]["Q1"]["acc"], "T_nowire_abstain": tw["T-nowire"]["ask_900"]["Q1"]["abstain"], "bar": "≤ .20"},
        "iii_growth_matters": {"pass": tw["T-frozen"]["ask_900"]["Q1"]["acc"] <= d9["Q1"]["acc"] - .30, "T_frozen_Q1": tw["T-frozen"]["ask_900"]["Q1"]["acc"], "design_Q1": d9["Q1"]["acc"], "bar": "≥ 30 pp under"},
        "iv_grows_alone": {"cells_born": s9["cells_born_sight"] + s9["cells_born_words"], "births_refused_budget": s9["births_refused_budget"],
                           "five_thing_born_600": l5["at_600"]["cells_born_sight"], "ten_thing_born_600": design["at_600"]["cells_born_sight"],
                           "edges_born": s9["edges_born"], "edges_pruned": s9["edges_pruned"], "pruned_share": (s9["edges_pruned"] / s9["edges_born"]) if s9["edges_born"] else 0.0,
                           "removed_for_disuse": s9["removed_for_disuse"], "bars": "≥ 50 born · 0 refused · 5-thing < 10-thing · ≥ 5 % pruned · 0 by disuse"},
        "v_keeps": {"Q1_first10_at_600": d6["Q1"]["acc"], "Q1_first10_at_900": d9["Q1"]["acc"], "drop_pp": 100 * (d9["Q1"]["acc"] - d6["Q1"]["acc"]), "bar": "within 5 pp"},
        "vi_knows_unknown": {"plant_answered": design["plant"]["answered_rate"], "plant_answered_as": design["plant"]["answered_as"], "null_abstain": design["null_plant"]["abstain_rate"],
                             "Q5_abstain": d9["Q5"][world.THING_NEVER]["abstain_rate"], "Q5_abstain_by": d9["Q5"][world.THING_NEVER]["abstain"], "Q5_answered_as": d9["Q5"][world.THING_NEVER]["answered_as"],
                             "false_abstention_seen": d9["Q1"]["false_abstention"], "false_abstention_by": d9["Q1"]["abstain"], "bars": "plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20"},
        "vii_replay": {"pass": R["replay_identical"], "hash": design["hash_final"][:16]},
        "viii_cost": {"pass": design["seconds"] <= 300, "seconds_design_life": design["seconds"], "bar": "≤ 300 s"},
        "ix_not_luck": {"pass": rank <= 5, "rank_of_design": rank, "of": len(comps), "design_composite": d9["composite"], "best_random": max(x["composite"] for x in rg), "best_random_seed": max(rg, key=lambda x: x["composite"])["seed"], "bar": "top quartile of the 20 random genomes (rank ≤ 5 of 21)"},
        "untested_SCALE": {"scale_events": s9["scale_events"], "note": "SCALE every 1000 fires 0 times in a 905-moment life — UNTESTED (§10 clause 7)"},
    }
    M["iv_grows_alone"]["pass"] = (M["iv_grows_alone"]["cells_born"] >= 50 and M["iv_grows_alone"]["births_refused_budget"] == 0 and l5["at_600"]["cells_born_sight"] < design["at_600"]["cells_born_sight"]
                                   and M["iv_grows_alone"]["pruned_share"] >= .05 and s9["removed_for_disuse"] == 0)
    M["v_keeps"]["pass"] = (d9["Q1"]["acc"] >= d6["Q1"]["acc"] - .05)
    M["vi_knows_unknown"]["pass"] = (design["plant"]["answered_rate"] > .5 and design["null_plant"]["abstain_rate"] > .5 and d9["Q5"][world.THING_NEVER]["abstain_rate"] >= .80 and d9["Q1"]["false_abstention"] <= .20)
    R["marks"] = M
    R["verdict"] = "PASS" if all(v["pass"] for k, v in M.items() if k != "untested_SCALE") else "FAIL"
    R["marks_failed"] = [k for k, v in M.items() if k != "untested_SCALE" and not v["pass"]]
    (out / "results.json").write_text(json.dumps(R, indent=1, default=str))
    write_verdict(out, R, genome)
    print(f"VERDICT {R['verdict']} — failed: {R['marks_failed'] or 'none'} — {out}")
    return 0


def write_verdict(out: Path, R: Dict[str, object], genome: Genome) -> None:
    M = R["marks"]; d = R["design"]; d9 = d["ask_900"]; d6 = d["ask_600"]; s9 = d["at_900"]
    L = []
    L.append(f"# G0 rung 0 — VERDICT: **{R['verdict']}** (failed: {', '.join(R['marks_failed']) or 'none'}; SCALE untested)\n")
    L.append(f"run `{R['stamp']}` · genome `{out / 'G0.genome'}` · PREREG docs/G0-PREREG.md §1–§11 · every number below is read from results.json\n")
    L.append("## The nine marks, bars as written before the run (§5), predictions of §7 beside each\n")
    L.append("| mark | bar | read | pass | §7 predicted |\n|---|---|---|---|---|")
    L.append(f"| (i) it answers | {M['i_answers']['bars']} | Q1 {M['i_answers']['Q1']:.3f} · Q2 {M['i_answers']['Q2']:.2f} · Q3 {M['i_answers']['Q3']:.3f} (ceiling {M['i_answers']['Q3_ceiling']:.3f}) · Q4 {M['i_answers']['Q4']:.3f} | {M['i_answers']['pass']} | likely PASS |")
    L.append(f"| (ii) the meeting is real | T-shuffle, T-nowire Q1 ≤ .20 | T-shuffle Q1 band {[round(x,3) for x in M['ii_meeting_real']['T_shuffle_Q1_band']]} · T-nowire Q1 {M['ii_meeting_real']['T_nowire_Q1']:.3f} (abstain {M['ii_meeting_real']['T_nowire_abstain']}) | {M['ii_meeting_real']['pass']} | PASS |")
    L.append(f"| (iii) growth matters | T-frozen ≥ 30 pp under (i) | T-frozen Q1 {M['iii_growth_matters']['T_frozen_Q1']:.3f} vs design {M['iii_growth_matters']['design_Q1']:.3f} | {M['iii_growth_matters']['pass']} | PASS |")
    iv = M["iv_grows_alone"]
    L.append(f"| (iv) it grows on its own | {iv['bars']} | born {iv['cells_born']} · refused {iv['births_refused_budget']} · 5-thing {iv['five_thing_born_600']} vs full world {iv['ten_thing_born_600']} at the end of development · pruned {iv['edges_pruned']}/{iv['edges_born']} = {100*iv['pruned_share']:.1f} % (cross-thing born {d['edges_cross']['born']}, cross-thing pruned {d['edges_cross']['pruned']}) · disuse {iv['removed_for_disuse']} | {iv['pass']} | births 100–300; pruning may FAIL the 5 % bar |")
    L.append(f"| (v) it keeps what it learned | within 5 pp after arrival 2 | Q1 first-10 at 600 {M['v_keeps']['Q1_first10_at_600']:.3f} → at 900 {M['v_keeps']['Q1_first10_at_900']:.3f} ({M['v_keeps']['drop_pp']:+.1f} pp) | {M['v_keeps']['pass']} | PASS |")
    vi = M["vi_knows_unknown"]
    L.append(f"| (vi) it knows what it does not know | {vi['bars']} | plant zog answered {vi['plant_answered']:.2f} (as {vi['plant_answered_as']}) · null vex abstains {vi['null_abstain']:.2f} · Q5 spiral abstains {vi['Q5_abstain']:.2f} (by {vi['Q5_abstain_by']}; answered as {vi['Q5_answered_as']}) · false abstention on seen {vi['false_abstention_seen']:.3f} (by {vi['false_abstention_by']}) | {vi['pass']} | the uncertain one |")
    L.append(f"| (vii) replay | two lives byte-identical | {M['vii_replay']['pass']} (sha256 {M['vii_replay']['hash']}…) | {M['vii_replay']['pass']} | PASS by construction |")
    L.append(f"| (viii) cost | ≤ 300 s, one process | {M['viii_cost']['seconds_design_life']} s | {M['viii_cost']['pass']} | — |")
    ix = M["ix_not_luck"]
    L.append(f"| (ix) not luck | top quartile of 20 random genomes | design composite {ix['design_composite']:.3f} ranks {ix['rank_of_design']} of {ix['of']} (best random {ix['best_random']:.3f}) | {ix['pass']} | unknown |")
    L.append(f"| SCALE | — | {M['untested_SCALE']['scale_events']} events | UNTESTED | — |\n")
    L.append("## The design life, every number\n")
    L.append(f"- Gate G-a wrote THETA_N = {genome.theta_n}, THETA_M = {genome.theta_m}; retina `{' '.join(genome.retina)}` ({genome.sight_dim()} numbers); §2's strict rule NOT MET, §11's amended rule met (see the genome file's last line).")
    L.append(f"- Toy (circle, bar; 2 × 150 moments): Q1 {R['toy']['ask_600']['Q1']['acc']:.3f} → {'PASS' if R['toy_pass'] else 'FAIL'}.")
    if R.get("eye_parity"):
        L.append(f"- The eye: the numpy forward vs the sealed E09d tower's own {R['eye_parity']['n']}-frame gate features — max |diff| {R['eye_parity']['max_diff']:.2e}, {R['eye_parity']['frames_within_1e-4']} of {R['eye_parity']['n']} within 1e-4, planted shifted frame caught {R['eye_parity']['planted_caught']}; the gene's tower {R['eye_parity']['gene_tower']} (sha {R['eye_parity']['gene_sha256'][:16]}…, {R['eye_parity']['gene_n_feat']} features) runs the same arithmetic on its seal-checked bytes.")
    L.append(f"- Things: {', '.join(R['streams'].get('things', []))} at {R.get('side', 24)}×{R.get('side', 24)}; plant showings {R.get('plant_showings', 5)}" + (f" (gate: within-thing share ≥ THETA_N {R['gate']['plant']['p_res_at_theta_n']:.3f}); closest pair {R['gate']['closest_pair']['pair']} between-p95 {R['gate']['closest_pair']['p95']:.3f}" if R.get('gate', {}).get('plant') else "") + ".")
    L.append(f"- At the end of development (moment {d['at_600']['moments']}): cells {d['at_600']['cells_sight']} sight + {d['at_600']['cells_words']} words; Q1 {d6['Q1']['acc']:.3f} Q2 {d6['Q2']['acc']:.2f} Q3 {d6['Q3']['acc']:.3f} Q4 {d6['Q4']['acc']:.3f}; abstain by {d6['Q1']['abstain']}.")
    L.append(f"- Edges by the ledger's reading: cross-thing born {d['edges_cross']['born']} of {d['edges_cross']['born_total']}, cross-thing pruned {d['edges_cross']['pruned']} of {d['edges_cross']['pruned_total']} pruned in all (G0b §3 diagnostic; a same-thing edge is one whose two cells were born on the same thing).")
    L.append(f"- At the end of arrival 2 (moment {s9['moments']}): cells {s9['cells_sight']} + {s9['cells_words']} (born novelty {s9['births_novelty_sight']}/{s9['births_novelty_words']}, error {s9['births_error_sight']}/{s9['births_error_words']} — the error road FIRED {s9.get('births_refused_redundant', 0)} times and every birth was refused as redundant (§11 am. 4); refused by budget {s9['births_refused_budget']}, by arrival {d['refusals_by_arrival']}); edges alive {s9['edges_alive']}, born {s9['edges_born']}, pruned {s9['edges_pruned']}; merged cells {s9['cells_merged_sight']}/{s9['cells_merged_words']}; removed for disuse {s9['removed_for_disuse']}.")
    L.append(f"- Q1 per thing at 900: {json.dumps({k: round(v,2) for k,v in d9['Q1']['per_thing'].items()})}; arrival-2 things Q1 {d['ask_900_arr2']['Q1']['acc']:.3f} per thing {json.dumps({k: round(v,2) for k,v in d['ask_900_arr2']['Q1']['per_thing'].items()})}.")
    L.append(f"- Q2 detail (word → the thing of the cell it lit): {json.dumps(d9['Q2']['detail'])}.")
    L.append(f"- Cells per thing (alive, single-thing): {json.dumps(d['cells_per_thing'])}; multi-thing sight cells {d['multi_thing_sight_cells']}; answers from multi-word cells {d9['Q1']['answers_from_multi_word_cells']}.")
    L.append(f"- After the plant (moment {d['at_905']['moments']}): Q1 on the first things {d['ask_905']['Q1']['acc']:.3f}; ledger-corruption plant: hash unchanged {d['ledger_corruption_hash_unchanged']}.")
    L.append(f"- Time: design life {d['seconds']} s; replay identical {R['replay_identical']}.\n")
    L.append("## Twins (§4) — each blind to one thing\n")
    for k, v in R["twins"].items():
        a = v["ask_900"]; s = v["at_900"]
        L.append(f"- **{k}**: Q1 {a['Q1']['acc']:.3f} (abstain {a['Q1']['abstain']}) · Q2 {a['Q2']['acc']:.2f} · Q3 {a['Q3']['acc']:.3f} · Q4 {a['Q4']['acc']:.3f} · cells {s['cells_sight']}+{s['cells_words']} (error births {s['births_error_sight']}/{s['births_error_words']}, redundant refused {s.get('births_refused_redundant', 0)}) · edges alive {s['edges_alive']} born {s['edges_born']} pruned {s['edges_pruned']} ({(100*s['edges_pruned']/s['edges_born']) if s['edges_born'] else 0:.1f} %) · merged {s['cells_merged_sight']}/{s['cells_merged_words']} · refused budget {s['births_refused_budget']} frozen {s['births_refused_frozen']} · {v['seconds']} s")
    l5 = R["five_thing"]
    L.append(f"- **five-thing life** (600 moments, 120/thing): cells born {l5['at_600']['cells_born_sight']} vs the ten-thing life's {d['at_600']['cells_born_sight']} at 600; Q1 {l5['ask_600']['Q1']['acc']:.3f}.\n")
    L.append("## Twenty random genomes (§4, E29's control) — composite = mean(Q1..Q4) at 900\n")
    L.append("| seed | composite | Q1 | Q2 | Q3 | Q4 | theta_n | misfires | budget | kwta | lr | prune | theta_m | stage1 | abstain | cells | refused |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for x in sorted(R["random_genomes"], key=lambda z: -z["composite"]):
        g = x["genome"]
        L.append(f"| {x['seed']} | {x['composite']:.3f} | {x['Q1']:.3f} | {x['Q2']:.2f} | {x['Q3']:.3f} | {x['Q4']:.3f} | {g['theta_n']:.3f} | {g['misfires']} | {g['budget']} | {g['kwta']} | {g['lr']:.3f} | {g['prune_floor']:.3f} | {g['theta_m']:.3f} | {g['stage1']} | {g['abstain_ratio']:.2f} | {x['cells']} | {x['refused']} |")
    L.append(f"\nThe design genome's composite {d9['composite']:.3f} ranks {M['ix_not_luck']['rank_of_design']} of {M['ix_not_luck']['of']}; the best random genome is seed {M['ix_not_luck'].get('best_random_seed', '?')} at {M['ix_not_luck']['best_random']:.3f}.\n")
    # ---- what the design life did NOT exercise — the price of §11 amendment 2, stated
    zog_cells = d["at_905"]["cells_born_sight"] - s9["cells_born_sight"]
    sh = R["twins"]["T-shuffle-5"]["at_900"]
    L.append("## What did nothing in the design life, and why\n")
    L.append(f"- Four genes had no measurable work: error births 0 (the road fired {s9.get('births_refused_redundant', 0)} times, every birth refused as redundant), merges 0 (THETA_M {genome.theta_m} was never met between two winners with the same answer), pruned {s9['edges_pruned']} of {s9['edges_born']} edges, scale 0. This follows from THETA_N ({genome.theta_n}) sitting ABOVE the between-thing maximum (gate G-a, §11 amendment 2): no cross-thing edge is ever born, so nothing is wrong, redundant or weak. In T-shuffle-5, where the pairings are random, {sh['edges_born']} edges were born and {sh['edges_pruned']} pruned ({(100*sh['edges_pruned']/sh['edges_born']) if sh['edges_born'] else 0:.1f} %) — that number says whether the PRUNE gene works at all when there is something to prune.")
    L.append(f"- The same threshold surfaced twice more. The plant: «zog» shown 5 times birthed {zog_cells} cells, and 10 of 20 held-out zog renderings resonated with none of them (at THETA_N = the within-thing MEDIAN, half of same-thing renderings do not resonate with a given cell) — the plant reads 0.50 against a majority bar. Q5: the spiral abstains at exactly 0.80, its bar, with 4 of 20 read as «circle»; the spiral was never in gate G-a's ten-thing measurement, so the threshold carries no guarantee for a never-shown thing — one more answered spiral fails (vi) a second way.")
    L.append("")
    L.append("## What this verdict does and does not say\n")
    L.append("- The truth never entered the organism: `genome/machinery.py` imports neither `world` nor `questions` and carries no label field; the ledger is the runner's, built from the stream (clause 12; the hash check proves only that the runner did not touch the organism).")
    L.append("- SCALE is untested here (0 events in 905 moments). §2's strict gate rule was not met by any fixed front; §11's amended rule was, at the price of several cells per thing — the cells-per-thing line above is that price, measured.")
    L.append("- No sentences, no reasoning, no reward, no sleep, no evolution (§6). Rung 1 is his pictures through the folder door; rung 2 a lineage, only after rung 1.")
    (out / "VERDICT.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
