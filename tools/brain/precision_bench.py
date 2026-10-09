"""precision_bench.py — the N1 bench (PREREG-N1-PRECISION + AMENDMENTS 1–2; docs/brain/precision/).

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:40 +0400 — the law's bench, written AFTER the
law (law before code). One run does every arm and writes the report:

    python3 -B tools/brain/precision_bench.py OUTDIR

Arms (all over the SAME declared world, twins exact):
  real   — precision=True (the mechanism);
  off    — precision=False (the flag-off twin; M-COST's baseline);
  plant  — the doctored register (FrozenPredictor: v_fast ≡ v_slow after every update, w ≡ 1) — the
           instrument must catch the mechanism's absence (G-PLANT: M-MMN-1 FAILS on this arm);
  nullN  — 10 no-noise twins (AMENDMENT 1.5): phase-B noise slots filled with cycle rows, seeds fixed.

The world (AMENDMENTS 1/2): phase A = moments 0..399, the 4-things cycle (real canvases through the real
retina), one-showing deviants (arrow/wave/diamond) at 350/375/399; phase B = moments 400..599, the 8-pool
with every i % 3 == 2 a fresh random unit vector in retina space (the vector-level noise form — pixel noise
pool3-collapses, measured 2026-10-09: noise-vs-noise cos ≈ 0.963), deviants (moon/house/tree) at 49/100/151;
phase C = moments 600..1799, the 4-cycle continued (the slow register's convergence appendix).

The drive mirrors the live wiring (creature/mind.py:2498's form): e = predictor.error(x) BEFORE the moment,
lr_scale = predictor.modulate(1.0), then org.moment(x, xw, lr_scale=lr_scale).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from genome import world
from genome.machinery import Organism, parse_genome, retina, retina_dim
from genome.predict import (PRECISION_FLOOR, PRECISION_W_HI, PRECISION_W_LO, Predictor)

TOY = """\
SEED 1
SENSE eye 24x24 grey
RETINA pool3 unit
SENSE ear letters 8 blank=zero
AREA sight from retina
AREA words from ear
MEET sight words
BIRTH novelty cos<0.85
BIRTH error misfires 3
BUDGET 2000 per arrival
NMAX 200
KWTA 5
HEBB window 1
DELTA lr 0.1
PRUNE w<0.02 after 3 chances
MERGE cos>0.99 same-answer
SCALE every 1000 moments
STAGE 1 senses moments 0..0
STAGE 2 meet moments 0..
RECALL k=1
ABSTAIN second/best > 0.85
"""

BENCH_SEED = 20261009          # declared, fixed before any run
NULL_SEEDS = tuple(range(20261710, 20261720))   # the 10 no-noise twins (AMENDMENT 1.5)
N_A, N_B, N_C = 400, 200, 1200
THINGS_A = ["circle", "square", "triangle", "cross"]
POOL_B = THINGS_A + ["ring", "bar", "dot", "star"]
DEV_A = {350: "arrow", 375: "wave", 399: "diamond"}
DEV_B = {49: "moon", 100: "house", 151: "tree"}
BAR_RATIO = 1.25
BAR_SUPPRESS = 0.05           # M-MMN-0's absolute form (the G5-E table's own)
SCALE_LO, SCALE_HI = 0.80, 1.25
COST_BAR = 0.05


class FrozenPredictor(Predictor):
    """G-PLANT's doctored build: the registers can never separate (l_fast ≡ l_slow after every update),
    so w ≡ 1 — the mechanism absent. The bench must read M-MMN-1 FAILED on this arm."""

    def error(self, *a, **kw):
        e = super().error(*a, **kw)
        if self.precision:
            self._l_fast = self._l_slow          # frozen: the registers can never separate (AMENDMENT 3's form)
            self.last_weight = float(np.clip(np.exp(self._l_slow - self._l_fast),
                                             PRECISION_W_LO, PRECISION_W_HI))
        return e


def _unit_vec(rng: np.random.Generator, dim: int) -> np.ndarray:
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def build_rows(g, seed: int, no_noise: bool = False):
    """The declared world as (kind, thing|None, x) rows. Deterministic under the seed; the no-noise twin
    fills phase-B noise slots with cycle rows (AMENDMENT 1.5's null form)."""
    rng = np.random.default_rng(seed)
    dim = retina_dim(g.retina)
    rows = []
    for i in range(N_A):                                   # phase A
        if i in DEV_A:
            thing, kind = DEV_A[i], "deviant"
        else:
            thing, kind = THINGS_A[i % len(THINGS_A)], "cycle"
        rows.append((kind, thing, retina(world.render(thing, rng, side=24), g.retina)))
    b_thing_i = 0
    for i_b in range(N_B):                                 # phase B
        if i_b in DEV_B:
            thing = DEV_B[i_b]
            rows.append(("deviant", thing, retina(world.render(thing, rng, side=24), g.retina)))
        elif i_b % 3 == 2 and not no_noise:
            rows.append(("noise", None, _unit_vec(rng, dim)))
        else:
            # AMENDMENT 3.3: the no-noise twin's phase B runs the 4-CYCLE alone (contexts symmetric with
            # phase A — the first build drew from the 8-pool and left a real reliability difference in).
            pool = THINGS_A if no_noise else POOL_B
            thing = pool[b_thing_i % len(pool)]
            b_thing_i += 1
            rows.append(("cycle", thing, retina(world.render(thing, rng, side=24), g.retina)))
    for i in range(N_C):                                   # phase C (the stationary appendix, A2.3)
        thing = THINGS_A[i % len(THINGS_A)]
        rows.append(("cycle", thing, retina(world.render(thing, rng, side=24), g.retina)))
    return rows


def drive(rows, g, precision: bool, plant: bool = False):
    """The live-wiring form: error() before the moment; modulate(1.0) scales it. Returns (records, cpu_s)."""
    org = Organism(g)
    pred = (FrozenPredictor if plant else Predictor)(org, precision=precision)
    recs = []
    t0 = time.process_time()
    for i, (kind, thing, x) in enumerate(rows):
        xw = world.encode_word(thing, True) if thing is not None else None
        e = pred.error(x)
        lr_scale = pred.modulate(1.0)
        S, T = org.moment(x, xw, lr_scale=lr_scale)
        pred.note_winners(S)
        recs.append({"i": i, "kind": kind, "thing": thing, "e": e,
                     "w": pred.last_weight, "scale": lr_scale})
    return recs, time.process_time() - t0


def _phase(recs, lo: int, hi: int):
    return [r for r in recs if lo <= r["i"] < hi]


def _med(xs) -> float:
    return float(np.median(list(xs)))


def verdicts(arms: dict) -> dict:
    """Every mark of the law, computed from the arms' records, with presence counts beside every number."""
    real, off, plant = arms["real"][0], arms["off"][0], arms["plant"][0]
    nulls = arms["nulls"]
    out = {}

    a_first = [r["e"] for r in _phase(real, 0, 40)]
    a_last = [r["e"] for r in _phase(real, N_A - 40, N_A)]
    c_last = [r["e"] for r in _phase(real, N_A + N_B + N_C - 100, N_A + N_B + N_C)]
    # AMENDMENT 3.2: the suppression instrument reads the world's OWN convergence timescale — the first 40
    # moments of phase A vs the last 100 of phase C. The +0.05 bar is unchanged.
    out["M-MMN-0"] = {"bar": f"median(first40 of A) >= median(last100 of C) + {BAR_SUPPRESS} (A3.2's window)",
                      "first40_median": _med(a_first), "c_last100_median": _med(c_last),
                      "n": [len(a_first), len(c_last)],
                      "pass": _med(a_first) >= _med(c_last) + BAR_SUPPRESS}

    w_dev_a = [r["w"] for r in _phase(real, 0, N_A) if r["kind"] == "deviant"]
    w_dev_b = [r["w"] for r in _phase(real, N_A, N_A + N_B) if r["kind"] == "deviant"]
    ratio = _med(w_dev_a) / _med(w_dev_b)
    null_ratios = []
    for recs, _cpu in nulls:
        na = [r["w"] for r in _phase(recs, 0, N_A) if r["kind"] == "deviant"]
        nb = [r["w"] for r in _phase(recs, N_A, N_A + N_B) if r["kind"] == "deviant"]
        null_ratios.append(_med(na) / _med(nb))
    out["M-MMN-1"] = {"bar": f"median w(deviant|late A) >= {BAR_RATIO} x median w(deviant|B), and > null MAX",
                      "w_deviant_A": w_dev_a, "w_deviant_B": w_dev_b, "ratio": ratio,
                      "null_ratios": null_ratios, "null_max": max(null_ratios),
                      "n": [len(w_dev_a), len(w_dev_b), len(null_ratios)],
                      "pass": ratio >= BAR_RATIO and ratio > max(null_ratios)}

    a_first_w = [r["e"] * r["w"] for r in _phase(real, 0, 40)]
    a_last_w = [r["e"] * r["w"] for r in _phase(real, N_A - 40, N_A)]
    slope_raw = _med(a_first) - _med(a_last)
    slope_w = _med(a_first_w) - _med(a_last_w)
    out["M-MMN-2"] = {"bar": "weighted slope > 0 and >= raw slope (the protective form)",
                      "slope_raw": slope_raw, "slope_weighted": slope_w,
                      "pass": slope_w > 0 and slope_w >= slope_raw}

    tail = [r["w"] for r in _phase(real, N_A + N_B + N_C - 100, N_A + N_B + N_C)]
    clipped = [r for r in real if r["w"] is not None and (r["w"] <= PRECISION_W_LO or r["w"] >= PRECISION_W_HI)]
    out["M-SCALE"] = {"bar": f"median w over phase C's last 100 in [{SCALE_LO}, {SCALE_HI}]",
                      "tail_median": _med(tail), "n_tail": len(tail),
                      "clip_share": len(clipped) / len(real), "clip_presence": len(clipped),
                      "n_all": len(real),
                      "pass": SCALE_LO <= _med(tail) <= SCALE_HI}

    t_real, t_off = arms["real"][1], arms["off"][1]
    overhead = (t_real - t_off) / t_off if t_off > 0 else float("nan")
    out["M-COST"] = {"bar": f"ON vs OFF process_time overhead <= {COST_BAR:.0%}",
                     "cpu_real_s": t_real, "cpu_off_s": t_off, "overhead": overhead,
                     "pass": overhead <= COST_BAR}

    wpa = [r["w"] for r in _phase(plant, 0, N_A) if r["kind"] == "deviant"]
    wpb = [r["w"] for r in _phase(plant, N_A, N_A + N_B) if r["kind"] == "deviant"]
    plant_ratio = _med(wpa) / _med(wpb)
    out["G-PLANT"] = {"bar": "the frozen-register arm FAILS M-MMN-1 (the instrument sees the mechanism absent)",
                      "plant_ratio": plant_ratio, "n": [len(wpa), len(wpb)],
                      "pass": plant_ratio < BAR_RATIO}
    return out


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    g = parse_genome(TOY)
    arms = {}
    rows = build_rows(g, BENCH_SEED)
    arms["real"] = drive(rows, g, precision=True)
    arms["off"] = drive(rows, g, precision=False)
    arms["plant"] = drive(rows, g, precision=True, plant=True)
    arms["nulls"] = [drive(build_rows(g, s, no_noise=True), g, precision=True) for s in NULL_SEEDS]

    with (out / "arms.jsonl").open("w") as f:
        for name, (recs, cpu) in (("real", arms["real"]), ("off", arms["off"]), ("plant", arms["plant"])):
            for r in recs:
                f.write(json.dumps({"arm": name, **r}) + "\n")
        for si, (recs, cpu) in enumerate(arms["nulls"]):
            for r in recs:
                f.write(json.dumps({"arm": f"null{si}", **r}) + "\n")

    v = verdicts(arms)
    (out / "report.json").write_text(json.dumps(v, indent=2, default=float))
    lines = ["N1 PRECISION bench — the law's marks (PREREG-N1-PRECISION + AMENDMENTS 1-2)", ""]
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
