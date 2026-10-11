"""trajectory_bench.py — the N2 bench (PREREG-N2-TRAJECTORY §3; docs/brain/trajectory/).

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 12:3x +0400 — the law's bench, written AFTER the
law (law before code). One run does the pilot, every arm, the null, and writes the report:

    python3 -B tools/brain/trajectory_bench.py OUTDIR

The world (the law §3): the N1 bench's own toy world and tape form (precision_bench.TOY + build_rows,
imported — ONE source), sliced to phases A+B: phase A = moments 0..399, the predictable 4-thing cycle
(the learning stretches carry a real error downtrend — N1's M-MMN-0 evidence); phase B = moments
400..599, the seeded-irregular stationary world (8-pool with every i % 3 == 2 a fresh random unit
vector). The planted ramp control rides phase B (a scripted linear addition to the le stream, slope
declared). The drive mirrors the live wiring (precision_bench.drive's own order): e = predictor.error(x)
BEFORE the moment, lr_scale = predictor.modulate(1.0), then org.moment(x, xw, lr_scale=lr_scale).

Arms (all over the SAME declared rows, twins exact):
  real   — trajectory=True (the mechanism);
  off    — trajectory=False (the flag-off twin; M-COST's baseline);
  plant  — FrozenRPredictor: r frozen at 0 (w == 1, tpe == spe) — the instrument must catch the
           mechanism's absence (G-PLANT: M-PATH's margin dies on this arm);
  ramp   — RampPredictor: the M-RAMP control (the le stream + s*k over phase B, k counting ramped calls);
  twins  — 10 shuffled-delta twins (§4): the real arm's le journal, first differences deranged WITHIN
           EACH PHASE (the multiset kept, the trends destroyed, phase boundaries respected), a fresh
           register driven through each twin stream via the register's OWN step.

Bench decisions named honestly (declared before any graded run):
  D-stretch — phase A's declared learning stretches are moments [0,100) and [100,200) (each >= 100 per
              the law §7's 5*tau floor; the downtrend's body per N1's M-MMN-0 first-40 evidence), graded
              pooled, printed per stretch; D-pilot — the PILOT runs FIRST on PILOT_SEED and prints the
              phase-A per-quarter separations (the §4 FAIL-FORM road reads them) and the phase-B gap
              BEFORE any mark binds; D-eps — M-STAT's epsilon = max(EPS_FLOOR, 2 x the pilot's phase-B
              gap), printed; D-ramp — RAMP_SLOPE = 0.01 (G-UNIT (c)'s own value), the convergence window
              the law's 200 ramp moments = phase B's length, the graded tail the last 100; D-margin —
              M-PATH's margin = mean|spe| - mean|tpe| paired per-moment over the pooled stretches, the
              real run's margin must EXCEED the 10 twins' MAX (the smallest passing gap printed);
  D-cost —  the timings live in cost.json ALONE (report.json/report.txt stay byte-deterministic for
              the seat's G-DET pair).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome
from genome.predict import PRECISION_FLOOR, PRECISION_W_HI, PRECISION_W_LO, Predictor
from tools.brain.precision_bench import BENCH_SEED, N_A, N_B, TOY, build_rows

PILOT_SEED = 20261011                         # declared: the pilot's own seed (never the graded one)
NULL_SEEDS = tuple(range(20261730, 20261740))  # the 10 shuffled-delta twins (fixed, declared)
RAMP_SLOPE = 0.01                             # the planted slope (G-UNIT (c)'s own declared value)
LEARN_STRETCHES = ((0, 100), (100, 200))      # phase A's declared learning stretches (D-stretch)
RAMP_CONVERGE = 200                           # the law's window: 2 x 5*tau ramp moments = phase B's length
RAMP_TAIL = 100                               # the ramp's graded tail (its last 100 moments)
SCALE_LO, SCALE_HI = 0.80, 1.25
COST_BAR = 0.05
EPS_FLOOR = 0.005                             # D-eps: max(EPS_FLOOR, 2 x the pilot's phase-B gap)


class FrozenRPredictor(Predictor):
    """G-PLANT's doctored build: r frozen at 0, so w == 1 and tpe == spe exactly — the mechanism
    absent. The bench must read M-PATH's margin DEAD on this arm."""

    def _trajectory_step(self, le: float) -> float:
        self._t_r = 0.0
        w = super()._trajectory_step(le)
        self._t_r = 0.0
        return w


class RampPredictor(Predictor):
    """M-RAMP's control arm: a scripted linear addition s*k rides the le stream while `ramping` is set
    (the bench sets it at phase B's first moment; k counts RAMPED calls only). Instrument-only: the
    organism's e is untouched; the register consumes the planted stream (the law §3's form)."""

    def __init__(self, *a, slope: float = RAMP_SLOPE, **kw):
        super().__init__(*a, **kw)
        self._ramp_slope = slope
        self._ramp_k = 0
        self.ramping = False

    def _trajectory_step(self, le: float) -> float:
        if self.ramping:
            le = le + self._ramp_slope * self._ramp_k
            self._ramp_k += 1
        return super()._trajectory_step(le)


def drive(rows, g, cls=Predictor, trajectory: bool = True):
    """The live-wiring form (precision_bench.drive's own order): error() before the moment; modulate(1.0)
    scales it. Records the instrument reads per moment (le recomputed with predict.py's own expression —
    the same float the register consumed). Returns (records, cpu_s)."""
    org = Organism(g)
    pred = cls(org, trajectory=trajectory)
    recs = []
    t0 = time.process_time()
    for i, (kind, thing, x) in enumerate(rows):
        if isinstance(pred, RampPredictor) and i == N_A:
            pred.ramping = True                    # the ramp rides phase B from its first moment (D-ramp)
        xw = world.encode_word(thing, True) if thing is not None else None
        e = pred.error(x)
        lr_scale = pred.modulate(1.0)
        S, T = org.moment(x, xw, lr_scale=lr_scale)
        pred.note_winners(S)
        recs.append({"i": i, "kind": kind, "thing": thing, "e": e,
                     "le": float(np.log(e * e + PRECISION_FLOOR)),
                     "w": pred.last_weight, "r": pred.last_rate,
                     "tpe": pred.last_tpe, "spe": pred.last_spe, "scale": lr_scale})
    return recs, time.process_time() - t0


def in_stretch(i: int) -> bool:
    return any(lo <= i < hi for lo, hi in LEARN_STRETCHES)


def path_margin(recs) -> dict:
    """M-PATH's margin (D-margin): mean|spe| - mean|tpe|, paired per-moment over the pooled learning
    stretches; printed per stretch beside the pool. `recs` carries tpe/spe per moment (any arm)."""
    pooled_tpe = [r["tpe"] for r in recs if in_stretch(r["i"])]
    pooled_spe = [r["spe"] for r in recs if in_stretch(r["i"])]
    per = {}
    for lo, hi in LEARN_STRETCHES:
        t = [r["tpe"] for r in recs if lo <= r["i"] < hi]
        s = [r["spe"] for r in recs if lo <= r["i"] < hi]
        per[f"[{lo},{hi})"] = {"margin": float(np.mean(np.abs(s))) - float(np.mean(np.abs(t))), "n": len(t)}
    return {"margin": float(np.mean(np.abs(pooled_spe))) - float(np.mean(np.abs(pooled_tpe))),
            "n": len(pooled_tpe), "per_stretch": per}


def twin_stream(le_a, le_b, seed: int):
    """One shuffled-delta twin (§4): first differences deranged WITHIN EACH PHASE (the multiset kept,
    the trends destroyed), the stream rebuilt from each phase's own le[0]."""
    rng = np.random.default_rng(seed)
    out = []
    for le_phase in (le_a, le_b):
        diffs = np.diff(le_phase)
        twin = float(le_phase[0]) + np.concatenate([[0.0], np.cumsum(diffs[rng.permutation(len(diffs))])])
        out.extend(float(v) for v in twin)
    return out


def twin_run(le_twin, g) -> list:
    """A fresh register driven through the twin stream via the register's OWN step (never a
    re-implementation); returns the per-moment records (tpe/spe journaled by the step itself)."""
    pred = Predictor(Organism(g), trajectory=True)
    recs = []
    for i, le in enumerate(le_twin):
        pred._trajectory_step(le)
        recs.append({"i": i, "tpe": pred.last_tpe, "spe": pred.last_spe})
    return recs


def pilot_readings(rows, g) -> dict:
    """D-pilot: runs FIRST, prints BEFORE any mark binds — phase A's per-quarter path/point separations
    (the §4 FAIL-FORM road reads them: inside noise everywhere = the toy's trends too weak) and phase
    B's tpe-minus-spe gap (D-eps's input)."""
    recs, _ = drive(rows, g)
    quarters = {}
    for q in range(4):
        lo, hi = q * 100, (q + 1) * 100
        t = [r["tpe"] for r in recs if lo <= r["i"] < hi]
        s = [r["spe"] for r in recs if lo <= r["i"] < hi]
        quarters[f"A[{lo},{hi})"] = {"margin": float(np.mean(np.abs(s))) - float(np.mean(np.abs(t))),
                                     "mean_abs_spe": float(np.mean(np.abs(s))), "n": len(t)}
    b_tpe = [r["tpe"] for r in recs if N_A <= r["i"] < N_A + N_B]
    b_spe = [r["spe"] for r in recs if N_A <= r["i"] < N_A + N_B]
    return {"quarters": quarters,
            "phaseB_mean_abs_tpe": float(np.mean(np.abs(b_tpe))),
            "phaseB_mean_abs_spe": float(np.mean(np.abs(b_spe))),
            "phaseB_gap": float(np.mean(np.abs(b_tpe))) - float(np.mean(np.abs(b_spe)))}


def verdicts(arms: dict, twins: list, eps: float) -> dict:
    """Every mark of the law, computed from the arms' records, with presence counts beside every number."""
    real, off, plant, ramp = arms["real"][0], arms["off"][0], arms["plant"][0], arms["ramp"][0]
    out = {}

    m_real = path_margin(real)
    twin_margins = [t["margin"] for t in twins]
    null_max = max(twin_margins)
    out["M-PATH"] = {"bar": "margin = mean|spe| - mean|tpe| over the pooled learning stretches EXCEEDS "
                            "the 10 shuffled-delta twins' MAX (the smallest passing gap printed)",
                     "margin": m_real["margin"], "n": m_real["n"], "per_stretch": m_real["per_stretch"],
                     "twin_margins": twin_margins, "null_max": null_max,
                     "smallest_passing_gap": m_real["margin"] - null_max,
                     "pass": m_real["margin"] > null_max}

    b_tpe = [r["tpe"] for r in real if N_A <= r["i"] < N_A + N_B]
    b_spe = [r["spe"] for r in real if N_A <= r["i"] < N_A + N_B]
    gap_b = float(np.mean(np.abs(b_tpe))) - float(np.mean(np.abs(b_spe)))
    out["M-STAT"] = {"bar": f"phase B: mean|tpe| <= mean|spe| + eps (eps = {eps}, declared from the pilot)",
                     "mean_abs_tpe": float(np.mean(np.abs(b_tpe))), "mean_abs_spe": float(np.mean(np.abs(b_spe))),
                     "gap": gap_b, "eps": eps, "n": len(b_tpe),
                     "pass": gap_b <= eps}

    r_end = ramp[N_A + RAMP_CONVERGE - 1]["r"]
    r_path = {f"r_at_{k}": ramp[N_A + k - 1]["r"] for k in (50, 100, 150, 200)}
    tail = ramp[N_A + RAMP_CONVERGE - RAMP_TAIL: N_A + RAMP_CONVERGE]
    tail_tpe = [r["tpe"] for r in tail]
    tail_spe = [r["spe"] for r in tail]
    ramp_gap = float(np.mean(np.abs(tail_spe))) - float(np.mean(np.abs(tail_tpe)))
    out["M-RAMP"] = {"bar": f"the planted ramp (s = {RAMP_SLOPE}): r in [s/2, 2s] after {RAMP_CONVERGE} ramp "
                            "moments, and tpe < spe over the ramp's tail (the one-lag-unit arithmetic)",
                     "slope": RAMP_SLOPE, "r_end": r_end, **r_path,
                     "tail_mean_abs_tpe": float(np.mean(np.abs(tail_tpe))),
                     "tail_mean_abs_spe": float(np.mean(np.abs(tail_spe))),
                     "tail_gap": ramp_gap, "n_tail": len(tail),
                     "pass": (RAMP_SLOPE / 2 <= r_end <= 2 * RAMP_SLOPE)
                             and float(np.mean(np.abs(tail_tpe))) < float(np.mean(np.abs(tail_spe)))
                             and RAMP_SLOPE / 2 <= ramp_gap <= 2 * RAMP_SLOPE}

    ws = [r["w"] for r in real]
    clipped = [w for w in ws if w <= PRECISION_W_LO or w >= PRECISION_W_HI]
    out["M-SCALE"] = {"bar": f"median w over the whole run in [{SCALE_LO}, {SCALE_HI}]",
                      "median_w": float(np.median(ws)), "n": len(ws),
                      "clip_share": len(clipped) / len(ws), "clip_presence": len(clipped),
                      "pass": SCALE_LO <= float(np.median(ws)) <= SCALE_HI}

    t_real, t_off = arms["real"][1], arms["off"][1]
    overhead = (t_real - t_off) / t_off if t_off > 0 else float("nan")
    out["M-COST"] = {"bar": f"ON vs OFF per-row process_time overhead <= {COST_BAR:.0%} (timings in cost.json)",
                     "pass": overhead <= COST_BAR}

    m_plant = path_margin(plant)
    out["G-PLANT"] = {"bar": "the frozen-r arm's M-PATH margin is DEAD (< the twins' MAX — the instrument "
                             "sees the mechanism absent before any pass is trusted)",
                      "plant_margin": m_plant["margin"], "n": m_plant["n"], "null_max": null_max,
                      "pass": m_plant["margin"] < null_max}
    return out, {"cpu_real_s": arms["real"][1], "cpu_off_s": arms["off"][1],
                 "overhead": (arms["real"][1] - arms["off"][1]) / arms["off"][1] if arms["off"][1] > 0 else None}


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    g = parse_genome(TOY)

    # D-pilot FIRST (the §4 FAIL-FORM road reads it): declared seed, printed before any mark binds.
    pilot = pilot_readings(build_rows(g, PILOT_SEED)[:N_A + N_B], g)
    (out / "pilot.json").write_text(json.dumps(pilot, indent=2, default=float) + "\n")
    eps = max(EPS_FLOOR, 2.0 * pilot["phaseB_gap"])

    rows = build_rows(g, BENCH_SEED)[:N_A + N_B]
    arms = {"real": drive(rows, g), "off": drive(rows, g, trajectory=False),
            "plant": drive(rows, g, cls=FrozenRPredictor), "ramp": drive(rows, g, cls=RampPredictor)}

    le_a = [r["le"] for r in arms["real"][0][:N_A]]
    le_b = [r["le"] for r in arms["real"][0][N_A:N_A + N_B]]
    twins = []
    for s in NULL_SEEDS:
        trecs = twin_run(twin_stream(le_a, le_b, s), g)
        twins.append({"seed": s, "margin": path_margin(trecs)["margin"], "recs": trecs})

    v, cost = verdicts(arms, twins, eps)

    with (out / "arms.jsonl").open("w") as f:
        for name in ("real", "off", "plant", "ramp"):
            for r in arms[name][0]:
                f.write(json.dumps({"arm": name, **r}) + "\n")
    with (out / "twins.jsonl").open("w") as f:
        for t in twins:
            for r in t["recs"]:
                f.write(json.dumps({"twin_seed": t["seed"], **r}) + "\n")
    (out / "cost.json").write_text(json.dumps(cost, indent=2, default=float) + "\n")
    (out / "report.json").write_text(json.dumps(v, indent=2, default=float) + "\n")

    lines = ["N2 TRAJECTORY bench — the law's marks (PREREG-N2-TRAJECTORY)", ""]
    lines.append(f"PILOT (PILOT_SEED {PILOT_SEED}, printed before the marks bind):")
    for q, d in pilot["quarters"].items():
        lines.append(f"    {q}: margin {d['margin']:.6f} (mean|spe| {d['mean_abs_spe']:.6f}, n {d['n']})")
    lines.append(f"    phase B gap {pilot['phaseB_gap']:.6f} -> eps {eps}")
    lines.append("")
    all_pass = True
    for mark, d in v.items():
        lines.append(f"{mark}: {'PASS' if d['pass'] else 'FAIL'} — bar {d['bar']}")
        for k, x in d.items():
            if k in ("bar", "pass"):
                continue
            lines.append(f"    {k}: {x}")
        all_pass = all_pass and bool(d["pass"])
        lines.append("")
    lines.append(f"BENCH VERDICT LINE: {'ALL MARKS PASS' if all_pass else 'AT LEAST ONE MARK FAILS'}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
