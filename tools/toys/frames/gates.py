"""gates.py — TOY C's gates G1-G6 (docs/research/toys/PREREG-TOY-FRAMES.md §7; AMENDMENT-1 §1.4, §3, §4 (f)-(g)): what the unit REQUIRES before it runs.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:11 +0400 — new module, red-first against tests/tools/test_toys_frames_gates.py (stage 5b).

  G1  the copies hash to their manifest; the law's §0 counts are reproduced FROM THE COPIES (84,275 moments, 112,489 words, the per-source counts and words-a-moment histograms, the 10,000 scene moments and
      their 1 / 2 / 3-word histogram, «dax» at scene index 2,699, the 526 says / 86 yes / 40 distinct); both plant tokens occur in ZERO real rows (AMENDMENT-1 §2); G1's χ² fit of the SCENE stream to the generator's
      marginals is READ (each p > 0.001 gates G_max; a failed fit makes G_max a reading, not a failure of the gate).
  G2  genome.sentence.find_frames on the stand-in store equals the call on the REAL Episodes store holding the same known moments (a pin).
  G3  the compressor (END counted) equals its slow recount to 1e-9 on random streams, and the greedy's incremental gain equals a full recount at every step (rules.trace_problems).
  G4  on a SMALL synthetic planted stream (G6's sampler) every rule keeps the planted frame and passes the amend1 gate, PLANT-BEATS-NULL-2 holds, and the gate's own parse-breaking control is CAUGHT.
  G5  the price: ALPHA4 piloted at two null-draw counts, CPU extrapolated linearly to 100 draws (the unit's five conditions priced as five ALPHA4s: a ceiling), the peak RSS and its slope; STOP above the law's
      25-40 CPU-min ceiling (40) or above a memory ceiling (default 1 GB).
  G6  the ceiling gate's own controls: 20 replicates from the generator's constants stay under G_max + 20 (the margin printed), a planted cheat (0.9 x the generator's own code length) is CAUGHT, and the exact checks
      (the support sums to 1 within 1e-12, the entropy 6.0774, H(length) 1.5, H(utterance | length) 4.5774).
"""
from __future__ import annotations

import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from genome.fast import Episodes
from genome.sentence import find_frames

from tools.toys.common import prereg as PR

from . import compress as CO
from . import evaluate as EV
from . import plants as PL
from . import rules as RL
from . import run as RN
from . import scene as SC
from . import streams as ST
from . import synthetic as SY
from . import verdicts as VD

SECTION0: Dict[str, object] = {
    "alpha4": {"moments": 84275, "words": 112489, "by_source": {
        "shelf": {"moments": 47113, "words": 73624, "distinct": 3290, "per_moment": {1: 37546, 2: 799, 3: 592, 4: 8176}},
        "maker": {"moments": 35264, "words": 35294, "distinct": 17, "per_moment": {1: 35234, 2: 30}},
        "game": {"moments": 1574, "words": 3148, "distinct": 9, "per_moment": {2: 1574}},
        "folder": {"moments": 306, "words": 306, "distinct": 11},
        "lexicon": {"moments": 18, "words": 117}}},
    "scene": {"moments": 10000, "per_moment": {1: 2503, 2: 4988, 3: 2509}, "dax_index": 2699},
    "says": (526, 86, 40),
}


# ------------------------------------------------------------------------------------------------------------------ G1
def _cmp(failures: List[str], label: str, got, want) -> None:
    if got != want:
        failures.append(f"{label}: {got!r} != {want!r}")


def g1(copies: Path, expected: Dict[str, object] = SECTION0) -> Dict[str, object]:
    copies = Path(copies)
    failures: List[str] = []
    out: Dict[str, object] = {}
    man_path = copies / "MANIFEST.json"
    if man_path.exists():
        man = json.loads(man_path.read_text())
        bad = ST.verify_copies(copies, man)
        failures += [f"copy {rel}: no longer hashes to its manifest" for rel in bad]
        out["copies_verified"] = len(man) - len(bad)
    else:
        failures.append("no MANIFEST.json in the copies directory")
    try:
        a4 = ST.load_moments(sorted((copies / "alpha4-1" / "tape").glob("*.jsonl")))
        sc = ST.scene_moments(ST.load_moments(sorted((copies / "brain-full-20261102" / "tape").glob("*.jsonl"))))
        says = ST.load_says(sorted((copies / "alpha4-1" / "journal").glob("*.jsonl")))
    except ST.StreamError as e:
        failures.append(f"a copy cannot be read: {e}")
        return {"ok": False, "failures": failures, **out}
    c = ST.section0_counts(a4)
    ea = expected["alpha4"]
    _cmp(failures, "alpha4.moments", c["moments"], ea["moments"])
    _cmp(failures, "alpha4.words", c["words"], ea["words"])
    for src, want in ea["by_source"].items():
        got = c["by_source"].get(src)
        if got is None:
            failures.append(f"alpha4.{src}: the source is absent")
            continue
        for k, v in want.items():
            _cmp(failures, f"alpha4.{src}.{k}", got[k], v)
    es = expected["scene"]
    _cmp(failures, "scene.moments", len(sc), es["moments"])
    _cmp(failures, "scene.per_moment", dict(sorted(Counter(len(m.words) for m in sc).items())), es["per_moment"])
    if es.get("dax_index") is not None:
        i = es["dax_index"]
        got = sc[i].words if i < len(sc) else None
        if got != (SC.DAX_WORD,):
            failures.append(f"scene.dax@{i}: {got!r} != ('dax',)")
    got_says = (len(says), sum(1 for s in says if s[1] == "yes"), len({s[0] for s in says}))
    _cmp(failures, "says (rows, yes, distinct frames)", got_says, tuple(expected["says"]))
    tokens = {"ALPHA4": PL.plant_token_occurrences(a4), "SCENE": PL.plant_token_occurrences(sc)}
    for name, t in tokens.items():
        if any(t.values()):
            failures.append(f"plant tokens occur in the real {name} stream: {t}")
    chi = SC.chi2_checks(sc)
    out.update({"alpha4": {"moments": c["moments"], "words": c["words"]}, "scene": {"moments": len(sc)}, "says": got_says, "plant_tokens": tokens, "chi2": chi})
    return {"ok": not failures, "failures": failures, **out}


# ------------------------------------------------------------------------------------------------------------------ G2
def _known_store() -> List[List[str]]:
    return ([["red", "box"]] * 10 + [["blue", "ball"]] * 10 + [["green", "key"]] * 10 + [["red", "ball"]] * 2
            + [["the"]] * 3 + [["a", "a"]] * 2 + [[]] * 2 + [["x", "y", "z"]] * 4)


def g2() -> Dict[str, object]:
    ms = _known_store()
    real = Episodes(cap=64, dim_s=2, dim_w=2)
    for m in ms:
        real.write(0, np.zeros(2), np.zeros(2), "", 0.0, words_in_instant=list(m))
    a = find_frames(real)
    b = find_frames(RL.StandIn(ms))
    frames = sorted([r["w1"], r["w2"]] for r in b)
    ok = a == b and frames == [["blue", "ball"], ["green", "key"], ["red", "box"]]
    return {"ok": bool(ok), "frames": frames, "n_rows": len(b)}


# ------------------------------------------------------------------------------------------------------------------ G3
def _random_stream(seed: int, n_train: int = 40, n_held: int = 25, alphabet: str = "abcde", unk_every: int = 4):
    rng = np.random.default_rng(seed)

    def mk(n, allow_unk):
        out = []
        for _ in range(n):
            k = int(rng.integers(1, 5))
            m = [alphabet[int(i)] for i in rng.integers(0, len(alphabet), size=k)]
            if allow_unk and unk_every and rng.random() < 1.0 / unk_every:
                m[int(rng.integers(0, k))] = "z"
            out.append(m)
        return out

    return mk(n_train, False), mk(n_held, True)


def _random_frames(seed: int, k: int, alphabet: str = "abcde"):
    rng = np.random.default_rng(seed + 1000)
    out = set()
    while len(out) < k:
        out.add((alphabet[int(rng.integers(0, len(alphabet)))], alphabet[int(rng.integers(0, len(alphabet)))]))
    return out


_PLANTED_PAIRS = (("a", "b", 0.25), ("c", "d", 0.15), ("e", "f", 0.10), ("g", "h", 0.06), ("b", "c", 0.05))


def _random_train(seed: int, n: int = 300, alphabet: str = "abcdefgh") -> List[List[str]]:
    rng = np.random.default_rng(seed)
    out: List[List[str]] = []
    for _ in range(n):
        m = [alphabet[int(i)] for i in rng.integers(0, len(alphabet), size=int(rng.integers(1, 5)))]
        u = rng.random()
        acc = 0.0
        for x, y, share in _PLANTED_PAIRS:
            acc += share
            if u < acc:
                j = int(rng.integers(0, len(m) + 1))
                m[j:j] = [x, y]
                break
        out.append(m)
    return out


def g3(n_streams: int = 40, mdl_seeds: int = 8) -> Dict[str, object]:
    worst = 0.0
    cases = 0
    for seed in range(n_streams):
        train, held = _random_stream(seed)
        sc = CO.Scorer(train, held)
        for k in (1, 2, 4, 7):
            F = _random_frames(seed * 31 + k, k)
            fast, slow = sc.gain(F), CO.slow_gain(train, held, F)
            for key in ("G", "bits0", "bitsF", "L"):
                worst = max(worst, abs(getattr(fast, key) - slow[key]))
            if (fast.N, fast.K, fast.V, fast.n_held_words) != (slow["N"], slow["K"], slow["V"], slow["n_held_words"]):
                worst = max(worst, 1.0)
            cases += 1
    problems: List[str] = []
    steps = 0
    for seed in range(mdl_seeds):
        train = _random_train(seed)
        r = RL.mdl_greedy(CO.Scorer(train, [["a"]]))
        steps += r.info["steps"]
        problems += [f"seed {seed}: {p}" for p in RL.trace_problems(train, r.info["trace"])]
    return {"ok": bool(worst < 1e-9 and not problems), "compressor_cases": cases, "max_abs_diff": worst, "mdl_problems": problems, "mdl_steps": steps, "mdl_seeds": mdl_seeds}


# ------------------------------------------------------------------------------------------------------------------ G4
# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:22 +0400 — G4 under AMENDMENT-2 §2 (red-first): TWO planted synthetic streams. (A) the SCENE-regime stream as signed in AMENDMENT-1 §4 (g) (G6's sampler, replicate seed 1, a plant after every
# 10th): WEB-H, SENTENCE and MDL-GREEDY are REQUIRED to pass the amend1 gate, WEB-S is PRINTED (its small-vocabulary failure stays in the output, never erased). (B) the ALPHA4-regime stream (`synthetic.structure_free_alpha(n, 1)`, a plant
# after every 100th, ALPHA4's cadence): ALL FOUR rules are required (WEB-S at >= 9 of 10 seeds). On both: PLANT-BEATS-NULL-2 holds and the parse-breaking control is CAUGHT. Stream B gates the unit's START only; it enters no grade.
G4_REQUIRED = {"A": ("WEB-H", "SENTENCE", "MDL-GREEDY"), "B": ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")}


def _g4_stream(key: str, label: str, moments: Sequence[ST.Moment], every: int, draws: int, seeds: Sequence[int]) -> Dict[str, object]:
    planted = ST.with_plant(moments, every)
    tr, he = ST.split(planted)
    cond = EV.evaluate_condition(tr, he, name=f"G4-{key}", draws=draws, web_seeds=seeds, kind="plant")
    gates = VD.plant_gates(cond, "amend1")
    b = cond["plant_stream"]
    required = list(G4_REQUIRED[key])
    return {"label": label, "n_moments": len(moments), "every": every, "plants": [b["plants_train"], b["plants_held"]], "V": cond["V"], "budget": 2 * cond["V"],
            "B": b["B"], "plant_beats_null2": bool(b["plant_beats_null2"]), "null2_q95": b["null2_of_plant"]["q95"], "gates": gates, "required": required,
            "printed_only": [r for r in gates if r not in required], "control": PL.plant_gate_control(planted)}


def g4(draws: int = 100, seeds: Sequence[int] = EV.SEEDS, scene_moments: int = 3000, scene_every: int = PL.PLANT_EVERY["SCENE"], alpha_moments: int = 20_000,
       alpha_every: int = PL.PLANT_EVERY["ALPHA4"]) -> Dict[str, object]:
    scene = SC.sample_moments(scene_moments, np.random.default_rng([SC.SEED_ROOT, SC.G6_TAG, 1]))
    atr, ahe = SY.structure_free_alpha(alpha_moments, 1)
    streams = {"A": _g4_stream("A", "SCENE-regime (as signed, AMENDMENT-1 §4 (g))", scene, scene_every, draws, seeds),
               "B": _g4_stream("B", "ALPHA4-regime (AMENDMENT-2 §2 (B))", list(atr) + list(ahe), alpha_every, draws, seeds)}
    failures: List[str] = []
    for key, s in streams.items():
        for rule in s["required"]:
            if not s["gates"][rule]["pass"]:
                failures.append(f"G4 stream {key}: {rule} fails the PLANT gate ({s['gates'][rule]})")
        if not s["plant_beats_null2"]:
            failures.append(f"G4 stream {key}: PLANT-BEATS-NULL-2 fails (B {s['B']:.2f}, q95 {s['null2_q95']:.2f})")
        c = s["control"]
        if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):
            failures.append(f"G4 stream {key}: the gate's parse-breaking control is not caught ({c})")
    return {"ok": not failures, "failures": failures, "streams": streams, "draws": draws}


# ------------------------------------------------------------------------------------------------------------------ G5
def g5(copies: Path, sizes: Sequence[int] = (10, 20), cpu_ceiling_min: float = 40.0, rss_ceiling_mb: float = 1024.0, seeds: Sequence[int] = EV.SEEDS) -> Dict[str, object]:
    a4 = RN.load_streams(copies)["alpha4"]
    train, held = PL.condition_parts(a4, "plain")
    pilots = []
    for n in sizes:
        t0 = time.process_time()
        EV.evaluate_condition(train, held, name=f"G5-pilot-{n}", draws=n, web_seeds=seeds, kind="plain")
        pilots.append({"draws": int(n), "cpu_seconds": time.process_time() - t0, "peak_rss_kb": RN.peak_rss_kb()})
    a, b = pilots[0], pilots[-1]
    dn = b["draws"] - a["draws"]
    cpu_slope = (b["cpu_seconds"] - a["cpu_seconds"]) / dn
    rss_slope = (b["peak_rss_kb"] - a["peak_rss_kb"]) / dn
    pred_alpha = a["cpu_seconds"] + cpu_slope * (100 - a["draws"])
    pred_unit_min = 5 * pred_alpha / 60.0
    pred_rss_mb = (b["peak_rss_kb"] + rss_slope * max(0, 100 - b["draws"])) / 1024.0
    failures: List[str] = []
    if pred_unit_min > cpu_ceiling_min:
        failures.append(f"G5: the predicted unit CPU {pred_unit_min:.1f} min exceeds the ceiling {cpu_ceiling_min} min")
    if pred_rss_mb > rss_ceiling_mb:
        failures.append(f"G5: the predicted peak memory {pred_rss_mb:.0f} MB exceeds the ceiling {rss_ceiling_mb:.0f} MB")
    return {"ok": not failures, "failures": failures, "pilots": pilots, "cpu_slope_per_draw": cpu_slope, "rss_slope_kb_per_draw": rss_slope,
            "predicted_alpha4_cpu_seconds_at_100": pred_alpha, "predicted_unit_cpu_minutes": pred_unit_min, "predicted_peak_rss_mb": pred_rss_mb,
            "peak_rss_mb": max(p["peak_rss_kb"] for p in pilots) / 1024.0, "cpu_ceiling_min": cpu_ceiling_min, "rss_ceiling_mb": rss_ceiling_mb}


# ------------------------------------------------------------------------------------------------------------------ G6
def g6(replicates: int = 20, n_moments: int = 10_000) -> Dict[str, object]:
    reps = [SC.g6_replicate(k, n_moments) for k in range(1, replicates + 1)]
    cheat = SC.g6_cheat(1, min(4000, n_moments))
    ex = SC.g6_exact_checks()
    failures: List[str] = []
    for r in reps:
        if r["violation"]:
            failures.append(f"G6 (a): replicate {r['k']} has G(F_oracle) above G_max + 20 (margin {r['margin']:.2f})")
    if not (cheat["caught"] and cheat["bitsF_cheat"] != cheat["bitsF_honest"]):
        failures.append("G6 (b): the planted cheat is not caught (or did not change the bytes)")
    if abs(ex["sum_p"] - 1.0) >= 1e-12:
        failures.append(f"G6 (c): the support sums to {ex['sum_p']!r}")
    if abs(ex["entropy"] - 6.0774) >= 5e-5 or abs(ex["h_given_length"] - 4.5774) >= 5e-5 or abs(ex["h_length"] - 1.5) >= 1e-12 or ex["support_size"] != 90:
        failures.append(f"G6 (c): the generator's entropies are off ({ex})")
    return {"ok": not failures, "failures": failures, "replicates": reps, "cheat": cheat, "exact": ex, "min_margin": min(r["margin"] for r in reps)}


# ------------------------------------------------------------------------------------------------------------------ all of them
def run_gates(copies: Path, out: Path, expected: Dict[str, object] = SECTION0, g3_kw: Optional[dict] = None, g4_kw: Optional[dict] = None, g5_kw: Optional[dict] = None,
              g6_kw: Optional[dict] = None, prereg_root: Optional[Path] = None, log=print) -> int:
    PR.check(RN.LAW_KEYS, root=prereg_root)
    t0 = time.process_time()
    res: Dict[str, object] = {}
    failures: List[str] = []
    for name, fn in (("g1", lambda: g1(copies, expected)), ("g2", g2), ("g3", lambda: g3(**(g3_kw or {}))), ("g4", lambda: g4(**(g4_kw or {}))),
                     ("g5", lambda: g5(copies, **(g5_kw or {}))), ("g6", lambda: g6(**(g6_kw or {})))):
        r = fn()
        res[name] = r
        failures += list(r.get("failures", [])) if not r["ok"] and "failures" in r else ([] if r["ok"] else [f"{name} failed"])
        log(f"[gates] {name}: {'OK' if r['ok'] else 'FAILED'}")
    res.update({"passed": not failures, "failures": failures, "header": {**PR.header(RN.LAW_KEYS), **RN.code_header(), "gate_mode": RN.GATE_MODE},
                "cpu_seconds": time.process_time() - t0, "peak_rss_kb": RN.peak_rss_kb()})
    RN.write_json(Path(out) / "GATES.json", res)
    for f in failures:
        log(f"[gates] FAILURE: {f}")
    return 0 if not failures else 1
