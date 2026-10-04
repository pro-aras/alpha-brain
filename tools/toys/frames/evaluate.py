"""evaluate.py — TOY C's condition evaluator: every rule on ONE train/held-out split as a JSON-able record (docs/research/toys/PREREG-TOY-FRAMES.md §2-§4).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 17:47 +0400 — new module, red-first against tests/tools/test_toys_frames_evaluate.py (stage 3e).

For a condition (a name, the TRAIN moments, the HELD-OUT moments): the rules WEB-H (once), WEB-S (one run a seed), SENTENCE and MDL-GREEDY each give a frame set F from the train part only; each
record carries F (sorted), the compressor's gain (G, L, bits, N, K, V, per held word), its ANATOMY (M, D, C, T: anatomy.py), the ADJACENCY readings the law says to print (the share of frames with a
within-moment adjacent train occurrence; the frames with zero held-out adjacency, which cost bits and saved none; the held-out firings), the rule's own info, and NULL-1 and NULL-2 (100 draws:
the dealt values, mean, sd, q95, z, whether G beats q95, the counted fallbacks). The seed of a null's key is the web seed for WEB-S and 0 for the other rules (AMENDMENT-1 §4 (a)).
`quiet_rows` / `quiet_text` are the architect's 17:1x check as a table: per rule, G(F) against NULL-1's q95 (LOUD or QUIET) beside the anatomy of G(F).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from . import anatomy as AN
from . import compress as CO
from . import null as NL
from . import plants as PL
from . import rules as RL
from . import streams as ST

SEEDS: Tuple[int, ...] = tuple(range(1, 11))


def _null_dict(n: NL.NullResult, G: float) -> Dict[str, object]:
    d = n.read(G)
    d["values"] = list(n.values)
    d["kind"] = n.kind
    return d


def _record(sc: CO.Scorer, r: RL.RuleResult, draws: int, with_nulls: bool) -> Dict[str, object]:
    frames = sorted(r.frames)
    g = sc.gain(r.frames)
    an = AN.decompose_gain(sc, r.frames)
    adj_train = [sc.train_adjacent(f) for f in frames]
    adj_held = [sc.held_adjacent(f) for f in frames]
    rec: Dict[str, object] = {
        "rule": r.rule, "seed": r.seed, "n_frames": len(frames), "frames": [list(f) for f in frames], "info": r.info,
        "gain": {"G": g.G, "L": g.L, "bits0": g.bits0, "bitsF": g.bitsF, "N": g.N, "K": g.K, "V": g.V, "n_held_words": g.n_held_words, "per_word": g.per_word},
        "anatomy": an,
        "adjacency": {"train_adjacent_share": (sum(1 for a in adj_train if a > 0) / len(frames) if frames else None),
                      "held_adjacent_zero": sum(1 for a in adj_held if a == 0), "held_adjacent_total": sum(adj_held), "held_firings": an["firings"]},
    }
    if with_nulls:
        tag = RL.RULE_TAG[r.rule]
        seed = r.seed if r.rule == "WEB-S" else 0
        for key, fn in (("null1", NL.null1), ("null2", NL.null2)):
            try:
                rec[key] = _null_dict(fn(sc, r.frames, tag, seed, draws), g.G)
            except NL.NullError as e:
                rec[key] = {"error": str(e)}
    return rec


def evaluate_condition(train: Sequence[ST.Moment], held: Sequence[ST.Moment], name: str = "", draws: int = 100,
                       web_seeds: Sequence[int] = SEEDS, with_nulls: bool = True, kind: str = "plain") -> Dict[str, object]:
    # edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 18:01 +0400 — stage 4b: `kind` ('plain' | 'plant' | 'shuffle'); a PLANT condition carries each record's plant reading (keeps, A, C) and the stream's
    # block (B, the expected value, its decomposition, PLANT-BEATS-NULL-2): AMENDMENT-1 §1.
    if kind not in ("plain", "plant", "shuffle"):
        raise ValueError(f"evaluate_condition: kind {kind!r} is not plain | plant | shuffle")
    sc = CO.Scorer([m.words for m in train], [m.words for m in held])
    flat = ST.flat_words(train)
    results: List[RL.RuleResult] = [RL.web_rule(flat, sc, "H", 0)]
    results += [RL.web_rule(flat, sc, "S", s) for s in web_seeds]
    results.append(RL.sentence_rule(sc.train))
    results.append(RL.mdl_greedy(sc))
    recs = [_record(sc, r, draws, with_nulls) for r in results]
    cond: Dict[str, object] = {"name": name, "kind": kind, "n_train_moments": len(train), "n_held_moments": len(held), "n_train_words": sum(len(m.words) for m in train),
                               "n_held_words": sc.n_held_words, "V": sc.V, "N0": sc.n0, "draws": draws, "records": recs}
    if kind == "plant":
        for rec, r in zip(recs, results):
            rec["plant"] = PL.plant_reading(sc, r.frames)
        cond["plant_stream"] = PL.plant_stream_block(sc, PL.n_plants(train), PL.n_plants(held), draws)
    return cond


# ------------------------------------------------------------------------------------------------------------------ the architect's 17:1x check as a table
def quiet_rows(cond: Dict[str, object]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for r in cond["records"]:
        n1 = r.get("null1", {})
        n2 = r.get("null2", {})
        if r["n_frames"] == 0:
            verdict = "EMPTY"
        elif "error" in n1 or not n1:
            verdict = "NO-NULL"
        else:
            verdict = "LOUD" if r["gain"]["G"] > n1["q95"] else "QUIET"
        a = r["anatomy"]
        rows.append({"rule": r["rule"], "seed": r["seed"], "n_frames": r["n_frames"], "G": r["gain"]["G"], "verdict": verdict,
                     "null1_mean": n1.get("mean"), "null1_sd": n1.get("sd"), "null1_q95": n1.get("q95"),
                     "null2_mean": n2.get("mean"), "null2_sd": n2.get("sd"), "null2_q95": n2.get("q95"),
                     "null2_beats": (r["gain"]["G"] > n2["q95"]) if n2 and "error" not in n2 else None,
                     "M": a["M"], "D": a["D"], "C": a["C"], "T": a["T"], "L": a["L"], "firings": a["firings"]})
    return rows


def _f(x: Optional[float], w: int = 10, p: int = 2) -> str:
    return f"{x:{w}.{p}f}" if x is not None else " " * (w - 4) + "none"


def quiet_text(cond: Dict[str, object]) -> str:
    head = (f"{cond['name']}: {cond['n_train_moments']} train / {cond['n_held_moments']} held moments, {cond['n_train_words']} train words, V {cond['V']}, "
            f"{cond['draws']} null draws\n")
    cols = f"{'rule':<11}{'seed':>4}{'|F|':>6}{'G(F)':>11}{'NULL-1 mean':>12}{'sd':>8}{'q95':>11}{'verdict':>9}{'NULL-2 q95':>12}{'M':>10}{'D':>9}{'C':>10}{'T=D+C':>10}{'L':>10}{'firings':>8}\n"
    lines = [head, cols]
    for row in quiet_rows(cond):
        lines.append(f"{row['rule']:<11}{row['seed']:>4}{row['n_frames']:>6}{_f(row['G'], 11)}{_f(row['null1_mean'], 12)}{_f(row['null1_sd'], 8)}{_f(row['null1_q95'], 11)}"
                     f"{row['verdict']:>9}{_f(row['null2_q95'], 12)}{_f(row['M'])}{_f(row['D'], 9)}{_f(row['C'])}{_f(row['T'])}{_f(row['L'])}{row['firings']:>8}\n")
    return "".join(lines)
