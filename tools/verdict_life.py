#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-22 19:2x +0400 — THE ONE LIFE's marks (PREREG §19; docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §6, L-1): PURE
# functions over the tape rows, the live journal rows and STATUS, imported by tools/verdict_g4.py. Each reads «not gradable» (graded False,
# with the reason) on a record whose life did not declare the line — the six closed 8 h records and life 3b are the control (L-1). Written
# test-first against builder D's landed shapes (creature/senses/game.py:213-220; creature/mind.py:_maybe_choose_act / _consume_ear_sound).
"""The ONE life's verdict marks: ACT (§19.5), SOUND (§19.10), SIZING (§19.11); the shuffled-act plant.

edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:18 +0400 — ALPHA4-H task 4 (docs/briefs/ALPHA4-H.md;
ALPHA4-PREREG.md §5 READ (H)): read_words_born / shelf_episodes_from_tape / shuffled_shelf_episodes /
read_mark, added below the existing marks, none of them touched.
"""
from __future__ import annotations

import collections
import copy
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


def _meta(r: dict) -> dict:
    return r.get("meta") or {}


def act_mark(tape: Iterable[dict], journal: Iterable[dict], status: dict, min_outcomes: int = 100) -> Dict[str, object]:
    """PREREG §19.5: outcome rows with chosen_by == mind = 100 % of the game's outcome rows; act_mismatch 0 (the journal's own check and
    STATUS); the census per act (G-MOT-1: no act ≥ 95 %, no reachable act at 0); the reward printed beside G's random null 0.29, no bar.
    Not gradable when the game published fewer than `min_outcomes` outcome rows or the mind chose none (the worker's schedule chose)."""
    game_out = [r for r in tape if r.get("sense") == "outcome" and _meta(r).get("source") == "game"]
    mind = [r for r in game_out if _meta(r).get("chosen_by") == "mind"]
    act_names: List[str] = []
    for r in tape:
        if r.get("sense") == "eye" and _meta(r).get("act_names"):
            act_names = list(_meta(r)["act_names"]); break
    choices = [j for j in journal if isinstance(j.get("act"), dict)]
    mism_j = sum(1 for j in journal if isinstance(j.get("outcome"), dict) and j["outcome"].get("act_mismatch"))
    census = dict(status.get("acts_chosen") or {})
    if not census:
        census = dict(collections.Counter(j["act"].get("act") for j in choices))
    total = sum(census.values())
    max_share = (max(census.values()) / total) if total else None
    reachable = act_names or sorted(census)
    zero_acts = [a for a in reachable if census.get(a, 0) == 0]
    rewards = [float(_meta(r).get("got") or 0.0) for r in game_out]
    episodes = sum(1 for r in game_out if _meta(r).get("terminated") or _meta(r).get("truncated"))
    successes = sum(1 for r in game_out if float(_meta(r).get("got") or 0.0) > 0)
    out: Dict[str, object] = {
        "game_outcomes": len(game_out), "mind_chosen": len(mind), "mind_share": (len(mind) / len(game_out)) if game_out else None,
        "choices_journaled": len(choices), "mismatches_journal": mism_j, "mismatches_status": int(status.get("act_mismatches") or 0),
        "census": census, "max_share": (round(max_share, 4) if max_share is not None else None), "zero_acts": zero_acts,
        "reachable_acts": reachable, "reward_mean": (round(sum(rewards) / len(rewards), 4) if rewards else None),
        "episodes": episodes, "successes": successes, "success_per_episode": (round(successes / episodes, 4) if episodes else None),
        "random_null_success": 0.29,
        "bar": f"mind-chosen = 100 % of ≥ {min_outcomes} game outcomes · mismatches 0 · census: no act ≥ 95 %, no reachable act at 0 · the shuffled-act plant diverges · reward printed, no bar",
    }
    if not game_out:
        out.update(graded=False, pass_=None, reason="not gradable: the game published no outcome rows on this tape")
    elif not mind:
        out.update(graded=False, pass_=None, reason="not gradable: no outcome row was chosen by the mind (the worker's schedule chose — the ACT line did not drive the game)")
    elif len(game_out) < min_outcomes:
        out.update(graded=False, pass_=None, reason=f"not gradable: {len(game_out)} game outcomes < {min_outcomes}")
    else:
        ok = (len(mind) == len(game_out)) and mism_j == 0 and int(status.get("act_mismatches") or 0) == 0 \
            and (max_share is not None and max_share < 0.95) and not zero_acts
        out.update(graded=True, pass_=ok, reason="graded (§19.5)")
    out["pass"] = out.pop("pass_")
    return out


def shift_acts(rows: List[dict]) -> List[dict]:
    """The shuffled-act PLANT (§19.5's control): copies of the rows with every mind-chosen game outcome's act moved to the next act
    (index + 1 modulo the game's action count, the name re-drawn from the eye row's act_names when known). A replay of these rows must
    journal an act_mismatch on the first such outcome — the check that proves the check checks. Pure: never touches the input rows."""
    act_names: List[str] = []
    for r in rows:
        if r.get("sense") == "eye" and _meta(r).get("act_names"):
            act_names = list(_meta(r)["act_names"]); break
    out = []
    for r in rows:
        m = _meta(r)
        if r.get("sense") == "outcome" and m.get("source") == "game" and m.get("chosen_by") == "mind" and m.get("act_idx") is not None:
            r2 = copy.deepcopy(r); n = len(act_names) if act_names else (max(int(m["act_idx"]), 6) + 1)
            idx = (int(m["act_idx"]) + 1) % max(2, n)
            r2["meta"]["act_idx"] = idx
            if act_names: r2["meta"]["act"] = act_names[idx]
            out.append(r2)
        else:
            out.append(r)
    return out


def sound_mark(tape: Iterable[dict], journal: Iterable[dict], status: dict) -> Dict[str, object]:
    """PREREG §19.10: «not gradable: heard 0 s» in a silent world (the plan's §10 names the rung that brings sound); with sound on the
    tape, every ear-sound row is consumed (a journal `sound` row per tape row, none an error)."""
    rows = [r for r in tape if r.get("sense") == "ear-sound"]
    consumed = [j for j in journal if isinstance(j.get("sound"), dict) and "error" not in j["sound"]]
    errors = [j for j in journal if isinstance(j.get("sound"), dict) and "error" in j["sound"]]
    heard_s = 0.0
    try:
        heard_s = float(sum(float(_meta(r).get("when") or 0.0) for r in rows))
    except Exception:
        heard_s = 0.0
    out: Dict[str, object] = {"ear_sound_rows": len(rows), "consumed": len(consumed), "errors": len(errors),
                              "status_sound_events": status.get("sound_events", "not recorded"),
                              "bar": "every ear-sound row consumed into the sound ring, 0 errors; not gradable while the world is silent"}
    if not rows:
        out.update(graded=False, **{"pass": None}, reason="not gradable: heard 0 s — no ear-sound row on the tape (the world is silent; the plan's §10 names the rung that brings a voice)")
    else:
        out.update(graded=True, **{"pass": len(consumed) == len(rows) and not errors}, reason="graded (§19.10)")
    return out


def grade_mark(plant: dict, null: dict, seen: dict, answer_declared: bool) -> Dict[str, object]:
    """PREREG §19.3 (builder A's shapes: `graded` = {sure_bare, unsure, abstain_with_resemblance, abstain} on the reader's own plant/null
    asks; `hedge_rate` on the seen-words Q1): the null «vex» sure-bare ≤ 1 of 10 and unsure+abstain ≥ 8 of 10 (a 5/10 tie is a FAIL);
    the plant «zog» ANSWERED (the cell) ≥ 6 of 10 with its grade distribution printed; the hedge rate printed (the plan predicted < 10 %;
    L1's replay read 0.426 — a finding).
    edit: Claude (Fable 5.1), 2026-09-22 22:27 +0400 — the plant clause RE-SPECIFIED before the life (#228 (b)): «sure ≥ 6/10» sat above
    its ceiling — builder A's real-record grades on held-out renders read sure/unsure 10/0 … 0/10 per thing (LIFE-A-REPORT.md §2; hedge
    0.426), so a word seen five times grading «sure» six times in ten is a coin flip by construction. The plant's mark is the cell (G4's
    own (vi)); the grade's own mark is the null's two clauses, unchanged."""
    gp = (plant or {}).get("graded"); gn = (null or {}).get("graded")
    hedge = ((seen or {}).get("Q1") or {}).get("hedge_rate")
    par = (plant or {}).get("answered_rate")
    out: Dict[str, object] = {"plant_graded": gp, "null_graded": gn, "hedge_rate": hedge, "plant_answered_rate": par,
                              "bar": "null sure-bare ≤ 1/10 · null unsure+abstain ≥ 8/10 (a tie fails) · plant ANSWERED ≥ 6/10 (its grades printed) · hedge rate printed, no bar (predicted < 0.10)"}
    if not answer_declared or not isinstance(gp, dict) or not isinstance(gn, dict) or par is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: ANSWER not declared / no graded counts on the asks (a life before the graded answer)")
        return out
    n_null = sum(gn.values()) or 1; n_plant = sum(gp.values()) or 1
    null_sb = int(gn.get("sure_bare", 0)); null_soft = int(gn.get("unsure", 0)) + int(gn.get("abstain_with_resemblance", 0)) + int(gn.get("abstain", 0))
    plant_sure = int(gp.get("sure_bare", 0))
    out.update(null_sure_bare=null_sb, null_soft=null_soft, null_n=n_null, plant_sure=plant_sure, plant_n=n_plant,
               graded=True, **{"pass": (null_sb / n_null <= 0.1) and (null_soft / n_null >= 0.8) and (float(par) >= 0.6)},
               reason="graded (§19.3)")
    return out


def self_mark(tape: Iterable[dict], beliefs: Iterable[dict], journal: Iterable[dict], status: dict, self_declared: bool, min_body_rows: int = 24) -> Dict[str, object]:
    """PREREG §19.6 (builder A's shapes: a belief row whose word starts with `self:`, cells [], episodes = the two body rows' seqs):
    ≥ 1 self belief citing two real body rows; `think_skipped_for_backlog` printed. Not gradable under `min_body_rows` body rows or
    without the gene."""
    body_seqs = {int(r["seq"]) for r in tape if r.get("sense") == "body"}
    selfs = [b for b in beliefs if str(b.get("word", "")).startswith("self:")]
    cited_ok = [b for b in selfs if len(b.get("episodes") or []) == 2 and all(int(e) in body_seqs for e in b["episodes"])]
    self_thinks = sum(1 for j in journal if isinstance(j.get("think"), dict) and j["think"].get("kind") == "self")
    out: Dict[str, object] = {"body_rows": len(body_seqs), "self_beliefs": len(selfs), "self_beliefs_citing_two_body_rows": len(cited_ok),
                              "self_words": sorted({b.get("word") for b in selfs}), "self_thinks": self_thinks,
                              "think_skipped_for_backlog": status.get("think_skipped_for_backlog", "not recorded"),
                              "bar": "≥ 1 belief about itself citing two real body rows; skips printed; not gradable under %d body rows" % min_body_rows}
    if not self_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: SELF not declared on this life"); return out
    if len(body_seqs) < min_body_rows:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {len(body_seqs)} body rows < {min_body_rows}"); return out
    out.update(graded=True, **{"pass": len(cited_ok) >= 1}, reason="graded (§19.6)")
    return out


def surprise_mark(journal: Iterable[dict], status: dict, surprise_declared: bool, source_of: Optional[Dict[int, str]] = None,
                  twin_status: Optional[dict] = None, min_showings: int = 30, null_draws: int = 200) -> Dict[str, object]:
    """PREREG §19.1 as RE-SPECIFIED (edit: Claude (Fable 5.1), 2026-09-22 22:33 +0400) on L1's closed tape replayed under SURPRISE (builder B's recipe,
    the journal kept under scratch/l1-surprise/; the reasons in the PREREG): builder B's `confirmed` is a LIST of booleans per located glance
    (a share counts GLANCES — the first version of this mark tested the list's truthiness and read 1.0 on every row), the coarse row excluded.
    (a) FIRST-SHOWING SURPRISE: for every maker thing with ≥ `min_showings` showings, the share over its first 3 showings < over its last 20,
    for ≥ 80 % of them AND more than the shuffled null's p95 (each thing's showings permuted, `null_draws` draws, a fixed seed);
    (b) the LIFE-SCALE RISE: the share over the last 500 canvases − the first 500 ≥ 0.10; (c) the `--blind surprise` twin confirms 0 glances.
    Things from other sources (folder / game / hands) and things under `min_showings` are PRINTED, never graded (L1: 0 of 10 photographs
    confirmed a glance at floor 0.05); a word shown by two sources is graded over its MAKER rows and printed as `word@source` for the rest.
    `source_of`: eye-row seq → source from the tape, used when the row carries no `source` (None = every row counts as the maker's, said so)."""
    import random as _random, statistics as _statistics
    rows = [j for j in journal if "moment" in j and "confirmed" in j and j.get("act") != "coarse"]
    bar = "maker things with ≥ 30 showings: first-3 share < last-20 for ≥ 80 % and > the shuffled null's p95 · last-500 − first-500 share ≥ 0.10 · the blind-surprise twin confirms 0 glances"
    if not surprise_declared or not rows:
        return {"graded": False, "pass": None, "reason": "not gradable: SURPRISE not declared / no `confirmed` field on the moment rows", "bar": bar}
    def pair(j):
        f = j["confirmed"]; f = f if isinstance(f, list) else [f]
        return (sum(1 for x in f if x), len(f))
    def share(pairs):
        n = sum(b for _, b in pairs); return (sum(a for a, _ in pairs) / n) if n else None
    per_canvas = [pair(j) for j in rows]
    overall = share(per_canvas)
    first = share(per_canvas[:500]); last = share(per_canvas[-500:])
    rise = (round(last - first, 4) if (len(per_canvas) >= 1000 and first is not None and last is not None) else None)
    # edit: Claude (Fable 5.1), 2026-09-22 22:47 +0400 — per ROW, not per word (the advisor's read before the commit): the game's missions name «key»/«ball»/«box» and
    # the maker's arrival brings «key», so one word lives under two sources in one-1's world; a word is graded over its MAKER rows only, and
    # every row is bucketed by its own source (the row's `source` when the journal carries it — DELIVER declared — else the tape's by seq).
    src = source_of or {}
    per_thing: Dict[str, List[Tuple[int, int]]] = {}; other_things: Dict[str, List[Tuple[int, int]]] = {}
    by_source: Dict[str, dict] = {}; things_by_source: Dict[str, set] = {}
    for j, pc in zip(rows, per_canvas):
        s = j.get("source") or (src.get(int(j["seq"])) if src else None) or ("maker" if not src else "?")
        d = by_source.setdefault(str(s), {"things": 0, "confirmed": 0, "glances": 0})
        d["confirmed"] += pc[0]; d["glances"] += pc[1]
        w = j.get("word")
        if not w:
            continue
        things_by_source.setdefault(str(s), set()).add(w)
        (per_thing if s == "maker" else other_things).setdefault(w if s == "maker" else f"{w}@{s}", []).append(pc)
    for s, d in by_source.items():
        d["things"] = len(things_by_source.get(s, ()))
        d["share"] = round(d["confirmed"] / d["glances"], 4) if d["glances"] else None
    graded_things = {w: pcs for w, pcs in per_thing.items() if len(pcs) >= min_showings}
    things: Dict[str, dict] = {}; rising = 0
    for w, pcs in graded_things.items():
        f3 = share(pcs[:3]); l20 = share(pcs[-20:]); up = bool(f3 < l20); rising += up
        things[w] = {"showings": len(pcs), "first3": round(f3, 4), "last20": round(l20, 4), "rising": up}
    printed = {w: {"showings": len(pcs), "source": "maker", "first3": share(pcs[:3]), "rest": share(pcs[3:])} for w, pcs in per_thing.items() if w not in graded_things}
    printed.update({k: {"showings": len(pcs), "source": k.rsplit("@", 1)[1], "first3": share(pcs[:3]), "rest": share(pcs[3:])} for k, pcs in other_things.items()})
    rng = _random.Random(20260922); counts: List[int] = []
    for _ in range(null_draws if graded_things else 0):
        h = 0
        for w, pcs in graded_things.items():
            u = list(pcs); rng.shuffle(u); h += bool(share(u[:3]) < share(u[-20:]))
        counts.append(h)
    null_mean = round(_statistics.mean(counts), 2) if counts else None
    null_p95 = sorted(counts)[max(0, int(0.95 * len(counts)) - 1)] if counts else None
    twin_conf = (twin_status or {}).get("glances_confirmed")
    n_things = len(graded_things)
    out: Dict[str, object] = {"overall_share": round(overall, 4) if overall is not None else None, "canvases": len(per_canvas),
                              "first_500": round(first, 4) if first is not None else None, "last_500": round(last, 4) if last is not None else None,
                              "rise_first_to_last_500": rise, "things_graded": n_things, "things_rising": rising, "things": things, "null_mean": null_mean,
                              "null_p95": null_p95, "printed_not_graded": printed, "by_source": by_source, "source_known": bool(src),
                              "twin_confirmed": twin_conf, "status_confirmed": status.get("glances_confirmed", "not recorded"),
                              "status_surprised": status.get("glances_surprised", "not recorded"), "bar": bar}
    if n_things == 0 or rise is None:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {n_things} maker things with ≥ {min_showings} showings / {len(per_canvas)} canvases (needs ≥ 1000)")
        return out
    ok_things = rising >= 0.8 * n_things and (null_p95 is None or rising > null_p95)
    ok_rise = rise >= 0.10
    ok_twin = twin_conf is not None and int(twin_conf) == 0
    out.update(graded=True, **{"pass": bool(ok_things and ok_rise and ok_twin)}, clause_things=ok_things, clause_rise=ok_rise, clause_twin=ok_twin,
               reason="graded (§19.1 as re-specified 2026-09-22 22:33 +0400)" + ("" if twin_conf is not None else "; the blind-surprise twin was not run — the twin clause FAILS"))
    return out


def coarse_mark(live_allw: dict, twin_allw: Optional[dict], coarse_declared: bool) -> Dict[str, object]:
    """PREREG §19.4: Q1 on all words ≥ 0.975 (G-EYE-2's bar) beside the blind-coarse twin; the PREDICTION printed: house ≥ 0.8 live where
    the twin reads < 0.6; cup printed, no bar. Not gradable without the gene or the twin's exam."""
    q1 = ((live_allw or {}).get("Q1") or {}); tq1 = ((twin_allw or {}).get("Q1") or {}) if twin_allw else {}
    if not coarse_declared or q1.get("acc") is None or tq1.get("acc") is None:
        return {"graded": False, "pass": None, "reason": "not gradable: GAZE coarse not declared / no blind-coarse twin exam", "bar": "Q1 all words ≥ 0.975 beside the blind-coarse twin; house ≥ 0.8 vs twin < 0.6 (a prediction)"}
    per = q1.get("per_thing") or {}; tper = tq1.get("per_thing") or {}
    house, thouse = per.get("house"), tper.get("house")
    held = (house is not None and thouse is not None and house >= 0.8 and thouse < 0.6)
    return {"graded": True, "pass": float(q1["acc"]) >= 0.975, "q1_live": q1["acc"], "q1_blind_coarse": tq1["acc"], "house_live": house, "house_blind_coarse": thouse,
            "house_prediction_held": held if (house is not None and thouse is not None) else None, "cup_live": per.get("cup"), "cup_blind_coarse": tper.get("cup"),
            "reason": "graded (§19.4)", "bar": "Q1 all words ≥ 0.975 beside the blind-coarse twin; house ≥ 0.8 vs twin < 0.6 (a prediction)"}


def question_mark(journal: Iterable[dict], tape: Iterable[dict], status: dict, hours: float, question_declared: bool) -> Dict[str, object]:
    """PREREG §19.7 (builder C's shapes: journal `question` rows; tape rows whose meta carries `answering`; STATUS questions_written /
    questions_answered): questions written ≥ 1 per 2 h after hour 2 (≥ (hours − 2)/2 over the life); the share the world answered
    within its next canvases printed (the plan's prediction ≥ 0.5 for maker things). Not gradable without the gene or under 2 h."""
    qs = [j for j in journal if isinstance(j.get("question"), dict)]
    answered = [r for r in tape if _meta(r).get("answering")]
    forms = collections.Counter(str(j["question"].get("q")) for j in qs)
    out: Dict[str, object] = {"questions": len(qs), "forms": dict(forms), "answered_rows": len(answered),
                              "answered_share": (round(len(answered) / len(qs), 4) if qs else None),
                              "status_written": status.get("questions_written", "not recorded"), "status_answered": status.get("questions_answered", "not recorded"),
                              "bar": "questions ≥ (hours − 2)/2 · the answered share printed (prediction ≥ 0.5 for maker things)"}
    if not question_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: QUESTION not declared on this life"); return out
    if hours < 2.0:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {hours} h < 2 h (questions are graded after hour 2)"); return out
    need = max(1, int((hours - 2.0) / 2.0))
    out.update(needed=need, graded=True, **{"pass": len(qs) >= need}, reason=f"graded (§19.7): {len(qs)} questions vs {need} needed")
    return out


def world_pair_skew(tape: Iterable[dict]) -> Dict[str, object]:
    """The world's OWN pair skew (PREREG §19.8's ceiling clause): over the game's missions on the tape (one per object ear row, the
    mission's last two tokens = colour, object), the max lift count / (n · p(colour) · p(object)) over pairs met ≥ 5 times."""
    pairs: collections.Counter = collections.Counter()
    for r in tape:
        m = _meta(r)
        if r.get("sense") != "ear" or m.get("source") != "game" or not m.get("mission"):
            continue
        toks = str(m["mission"]).split()
        if len(toks) < 2 or m.get("word") != toks[-1]:
            continue                                  # count each mission ONCE, on its object row
        pairs[(toks[-2], toks[-1])] += 1
    n = sum(pairs.values())
    if not n:
        return {"missions": 0, "max_lift": None, "max_pair": None, "pairs": 0}
    pc: collections.Counter = collections.Counter(); po: collections.Counter = collections.Counter()
    for (c, o), k in pairs.items():
        pc[c] += k; po[o] += k
    best = None; best_pair = None
    for (c, o), k in pairs.items():
        if k < 5: continue
        lift = k / (n * (pc[c] / n) * (po[o] / n))
        if best is None or lift > best: best, best_pair = lift, f"{c} {o}"
    return {"missions": n, "max_lift": (round(best, 4) if best is not None else None), "max_pair": best_pair, "pairs": len(pairs)}


def sentence_mark(tape: Iterable[dict], status: dict, sentence_declared: bool, min_missions: int = 100) -> Dict[str, object]:
    """PREREG §19.8 + its ceiling clause: ≥ 3 frames filed with precision ≥ 0.8 (frames_true / frames_scored), not gradable under
    `min_missions` missions on the tape, and NOT GRADABLE when the world's own max pair lift < 2 (no frame can exist there — builder C's
    finding on BabyAI GoToLocal's independent colour/object draws)."""
    tape = list(tape); skew = world_pair_skew(tape)
    filed = int(status.get("frames_filed") or 0); scored = int(status.get("frames_scored") or 0); true = int(status.get("frames_true") or 0)
    out: Dict[str, object] = {**skew, "frames_filed": filed, "frames_scored": scored, "frames_true": true,
                              "precision": (round(true / scored, 4) if scored else None), "said": status.get("said", "not recorded"),
                              "heard_yes": status.get("heard_yes", "not recorded"), "heard_no": status.get("heard_no", "not recorded"),
                              "bar": "≥ 3 frames · precision ≥ 0.8 · not gradable under %d missions or when the world's max pair lift < 2 (the ceiling clause)" % min_missions}
    if not sentence_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: SENTENCE not declared on this life"); return out
    if skew["missions"] < min_missions:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {skew['missions']} missions < {min_missions}"); return out
    if skew["max_lift"] is None or skew["max_lift"] < 2.0:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: the world's word pairs are independent (max lift {skew['max_lift']} < 2; a frame cannot exist there — PREREG §19.8's ceiling clause)"); return out
    out.update(graded=True, **{"pass": filed >= 3 and scored >= 1 and (true / scored) >= 0.8}, reason="graded (§19.8): the world admits a frame (max lift %s on «%s»)" % (skew["max_lift"], skew["max_pair"]))
    return out


def hands_rows(tape: Iterable[dict]) -> List[dict]:
    """The hands' pictures on the tape: eye rows `source: hands` carrying a shape (the control programs carry none)."""
    return [r for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "hands" and _meta(r).get("shape")]


def hands_mark(status: dict, rows: Iterable[dict], recog: Optional[dict], hands_declared: bool, min_runs: int = 20) -> Dict[str, object]:
    """PREREG §19.9 (builder F's shapes): not gradable under `min_runs` runs; then the recognised share (the reader's own asks of the
    hands' rendered canvases answered with the program's own shape) ≥ 0.6 beside the shuffled-shelf twin (shapes permuted). The
    prediction on the record: ≈ 0.1–0.2 with the ASCII render (the eye's generalisation across render styles), a FAIL kept as a result."""
    rows = list(rows); runs = int(status.get("runs") or len(rows))
    out: Dict[str, object] = {"runs": runs, "pictures_with_shape": len(rows), "runs_by_program": status.get("runs_by_program", "not recorded"),
                              "hands_no_road": status.get("hands_no_road", "not recorded"), "touch_events": status.get("touch_events", "not recorded"),
                              "smell_events": status.get("smell_events", "not recorded"),
                              "bar": "≥ 0.6 recognised (the exam answers the run's canvas with the program's own shape) vs the shuffled-shelf twin; not gradable under %d runs" % min_runs}
    if not hands_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: HANDS not declared on this life"); return out
    if runs < min_runs or len(rows) < 1:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {runs} runs < {min_runs}"); return out
    if not recog or not recog.get("asked"):
        out.update(graded=False, **{"pass": None}, reason="not gradable: the reader could not ask the hands' pictures (%s)" % (recog or {}).get("error", "no asks")); return out
    share = recog["hits"] / recog["asked"]; tw = recog.get("shuffled_hits", 0) / recog["asked"]
    out.update(asked=recog["asked"], hits=recog["hits"], recognised_share=round(share, 4), shuffled_share=round(tw, 4),
               graded=True, **{"pass": share >= 0.6}, reason="graded (§19.9)")
    return out


def thread_mark(alive: dict, status: dict, threaded: bool, max_gap_bar: float = 5.1, waits_bar: float = 0.05) -> Dict[str, object]:
    """PREREG §19.2 (builder E's shapes): ALIVE's max sense gap ≤ 5.1 s (life 3b's, the box otherwise idle) with the think ms series
    printed; think_waits / thinks < 5 %. Not gradable when THINK is not on its own thread, or when no think ran."""
    gaps = [float(g) for g in (alive or {}).get("max_gap_s_eye_ear") or [] if g is not None]
    thinks = int(status.get("thinks") or 0); waits = int(status.get("think_waits") or 0)
    out: Dict[str, object] = {"max_gap_s": (max(gaps) if gaps else None), "gaps_per_hour": gaps, "thinks": thinks, "think_waits": waits,
                              "waits_share": (round(waits / thinks, 4) if thinks else None), "think_wait_ms": status.get("think_wait_ms", "not recorded"),
                              "think_ms_last": status.get("think_ms_last", "not recorded"), "think_ms_median": status.get("think_ms_median", "not recorded"),
                              "bar": f"max sense gap ≤ {max_gap_bar} s · think_waits / thinks < {waits_bar:.0%}"}
    if not threaded:
        out.update(graded=False, **{"pass": None}, reason="not gradable: THINK is not on its own thread on this life"); return out
    if thinks == 0 or not gaps:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no think ran / no sense gaps on the record"); return out
    out.update(graded=True, **{"pass": max(gaps) <= max_gap_bar and (waits / thinks) < waits_bar}, reason="graded (§19.2)")
    return out


def evolve_mark(tape: Iterable[dict], journal: Iterable[dict], evolve_declared: bool, hours: float,
                 negative_control: Optional[Dict[str, dict]] = None) -> Dict[str, object]:
    """ALPHA4-PREREG.md §5/§6 (builder J's shapes): proposals filed (tape rows sense=="proposal") >= a bar
    SCALED by the record's own hours (3 in 24 h — the plan's own figure — never a fixed 3 under a shorter
    window, the same scaling `question_mark` above already uses for its own "per 2 h after hour 2" bar),
    each with BOTH readings paired on the same rows (meta carries dict "incumbent" and "mutant" — the SAME
    tape slice by construction, `tools/evolve.py:run_judging_round`'s own shape); adoptions (journal rows
    carrying a nested "epoch" dict — never a top-level "event" key, see `creature/mind.py:Mind._maybe_
    adopt_evolve_proposal`'s own docstring for why) <= proposals; every adoption's genome sha/moment
    printed. `negative_control`, when given (the two `NEGATIVE-CONTROL-*.json` files
    `tools/evolve.py --negative-control` writes, read by the caller — the planted-bad and null mutants are
    NEVER run against the live tape itself, so this reader cannot derive them from `tape`/`journal` alone):
    both must read REFUSED for the mark to pass; omitted, the mark is still graded on the tape's own record
    but says so in its reason (never silently assumed true). Not gradable without the gene (the seven
    closed records that predate EVOLVE, L-1's own control).

    `shadow_lag_rows` (printed, never gated on — #236's failure mode): the worst `shadow_lag_rows` any
    proposal on the tape recorded — the gap between the live tape's own head seq and the shadow's, at the
    moment that round was judged. A box loaded with other work can let the shadow fall behind, silently
    shrinking a round's slice below `judge_h` while its record still claims the full window; this number
    lets a reader see that without the mark refusing on it.

    TWO KNOWN LIMITS of a judging round's own readings, both structural (found in review, not fixed here
    — see the builder report): (1) `reward_mean` is READ FROM THE RECORDED SLICE's own outcome rows, which
    both twins consume UNCHANGED regardless of their own genome — it is therefore IDENTICAL for incumbent
    and mutant on every round, can never clear its declared margin, and can never register a regression
    either; it is not a live signal on a replayed tape, only on a genome that is actually driving the game
    (`creature.senses.game.mind_drives_acts` — true once ACT declares both "turn" and "step", as ALPHA4's
    own genome does). (2) When a genome DOES drive acts, a mutant twin whose chosen act diverges from the
    tape's own historical choice (made under the INCUMBENT, not the mutant) is graded `act_mismatch > 0`
    by `act_mark`'s own bar, which fails `act_pass` and reads as a "regression" in `regression_bar` — a
    mutation that changes ANY decision-relevant gene is structurally more likely to diverge from a history
    it did not produce, independent of whether the change is actually better or worse."""
    proposals = [r for r in tape if r.get("sense") == "proposal"]
    paired = [p for p in proposals if isinstance(_meta(p).get("incumbent"), dict) and isinstance(_meta(p).get("mutant"), dict)]
    epochs = [j for j in journal if isinstance(j.get("epoch"), dict)]
    epoch_events = [{"epoch": j["epoch"].get("epoch"), "genome_sha": j["epoch"].get("genome_sha"),
                      "moment": j["epoch"].get("moment"), "gene": j["epoch"].get("gene"), "value": j["epoch"].get("value")}
                     for j in epochs]
    lags = [int(_meta(p)["shadow_lag_rows"]) for p in proposals if isinstance(_meta(p).get("shadow_lag_rows"), (int, float))]
    out: Dict[str, object] = {
        "proposals": len(proposals), "paired_readings": len(paired), "adoptions": len(epochs),
        "epoch_events": epoch_events, "hours": hours, "negative_control": negative_control,
        "max_shadow_lag_rows": (max(lags) if lags else None),
        "bar": "proposals >= 3 scaled to the record's own hours (min 1) · every proposal paired (incumbent+mutant readings) "
               "· adoptions <= proposals · every adoption's genome sha printed · REPLAY identical across epochs (the "
               "existing REPLAY mark, on a tape carrying a proposal row) · the negative control's planted-bad and null "
               "mutants both REFUSED · max_shadow_lag_rows printed, never gated (#236)",
    }
    if not evolve_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: EVOLVE not declared on this life")
        return out
    if hours <= 0:
        out.update(graded=False, **{"pass": None}, reason="not gradable: hours <= 0")
        return out
    needed = max(1, round(3 * hours / 24.0))
    all_paired = len(paired) == len(proposals)
    adoptions_ok = len(epochs) <= len(proposals)
    nc_ok: Optional[bool] = None
    if negative_control is not None:
        nc_ok = (negative_control.get("planted_bad", {}).get("verdict") == "REFUSED"
                 and negative_control.get("null", {}).get("verdict") == "REFUSED")
    out.update(
        needed=needed, graded=True,
        **{"pass": bool(len(proposals) >= needed and all_paired and adoptions_ok and (nc_ok is not False))},
        reason=(f"graded (§5/§6): {len(proposals)} proposals vs {needed} needed; paired {len(paired)}/{len(proposals)}; "
                f"adoptions {len(epochs)} <= proposals; negative control "
                + ("REFUSED both (ok)" if nc_ok else ("not checked this read" if negative_control is None else "DID NOT REFUSE — a finding about the bar, not loosened"))),
    )
    return out


# edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:50 +0400 — ALPHA4-G.md task 5 (docs/ALPHA4-PREREG.md
# §2/§3, PREREG §5's GROW mark): `grow` (default False, every existing call site byte-identical) — under
# GROW there is no NMAX cap and no pre-flight banding prediction to grade against, so the bar reads
# refused-by-nmax 0 (any nmax refusal is a real defect: GROW must NEVER refuse for room) and the plant's
# birth, with `born` printed for the record but no [0.5x, 1.5x] band. `births_refused_budget`/
# `budget_regenerated` print beside `births_refused_nmax` in EVERY case (both regimes) — BUDGET's own
# refusal/regeneration counters are a separate concern from NMAX's, worth seeing whichever form CYCLE/GROW
# a life declares.
def sizing_mark(status: dict, journal: Iterable[dict], prediction: Optional[float], plant_word: str = "zog", grow: bool = False) -> Dict[str, object]:
    """PREREG §19.11: sight born by 24 h within [0.5×, 1.5×] of the pre-flight's prediction; births_refused_nmax 0; the plant birthed ≥ 1
    sight cell. The per-hour sight-births SERIES is on the record (#233's instrument). Not gradable without a prediction or an older body.
    Under GROW (ALPHA4-G task 5): no prediction is needed or graded against — refused-by-nmax must be 0, the plant must have birthed,
    born is printed with no band."""
    per_hour: "collections.OrderedDict[str, int]" = collections.OrderedDict(); plant_births = 0; plant_shown = 0
    for j in journal:
        if "moment" in j:
            h = (j.get("when") or "")[:13]
            n = sum(1 for b in (j.get("births") or []) if b and b[0] == "sight")
            per_hour[h] = per_hour.get(h, 0) + n
            if j.get("word") == plant_word:
                plant_shown += 1; plant_births += n
    born = status.get("sight_born"); nmax = status.get("sight_nmax"); refused = status.get("births_refused_nmax")
    bar = ("under GROW: refused-by-nmax 0 · the plant birthed ≥ 1 sight cell · born printed (no band — there is no prediction under GROW)"
           if grow else "born within [0.5×, 1.5×] of the prediction · refused at NMAX 0 · the plant birthed ≥ 1 sight cell")
    out: Dict[str, object] = {"sight_born": born, "sight_nmax": nmax, "births_refused_nmax": refused,
                              "births_refused_budget": status.get("births_refused_budget"), "budget_regenerated": status.get("budget_regenerated"),
                              "prediction": prediction, "series_sight_births_per_hour": list(per_hour.values()),
                              "plant_shown_moments": plant_shown, "plant_sight_births": plant_births, "bar": bar}
    if grow:
        if not isinstance(born, int) or not isinstance(refused, int):
            out.update(graded=False, **{"pass": None}, reason="not gradable: sight_born / births_refused_nmax not on STATUS (an older body)")
        else:
            out.update(graded=True, **{"pass": refused == 0 and plant_births >= 1},
                       reason=f"graded (§19.11, GROW): refused {refused}; plant births {plant_births}; born {born} (no band)")
    elif prediction is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight)")
    elif not isinstance(born, int) or not isinstance(nmax, int):
        out.update(graded=False, **{"pass": None}, reason="not gradable: sight_born / sight_nmax not on STATUS (an older body)")
    else:
        band = 0.5 * prediction <= born <= 1.5 * prediction
        out.update(graded=True, **{"pass": band and int(refused or 0) == 0 and plant_births >= 1},
                   reason=f"graded (§19.11): band {'ok' if band else 'MISSED'}; refused {refused}; plant births {plant_births}")
    return out


# ============================================================================ ALPHA4-PREREG §5: READ (builder H)
# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:2x +0400 — docs/briefs/ALPHA4-H.md task 4. Three
# tape-only helpers (never the mind's internal FAST ring — world_pair_skew's own precedent above) + the
# mark itself, which additionally takes `recog`/`recog_blind` (dicts from tools/read_recognised.py's
# `recognised_share`, computed OUTSIDE this pure module — hands_mark's own precedent for `recog` above).
def read_words_born(tape: Iterable[dict], journal: Iterable[dict]) -> int:
    """"words born from shelf moments (map birth moments -> source via the tape)" (ALPHA4-H.md task 4's own
    words): a journal MOMENT row's own `moment` field IS the tape's moment string (shared by construction,
    creature/mind.py:_consume_eye writes both from the SAME `moment` local); build moment->source from every
    EYE row's own meta, then count `births` entries with area=="words" whose row's moment resolves to
    source=="shelf". A moment the tape never carries (should not happen, defensive) resolves to None and is
    never counted."""
    source_of_moment: Dict[str, Optional[str]] = {}
    for r in tape:
        if r.get("sense") == "eye":
            source_of_moment[_meta(r).get("moment")] = _meta(r).get("source")
    n = 0
    for j in journal:
        if "moment" not in j or not j.get("births"):
            continue
        if source_of_moment.get(j["moment"]) != "shelf":
            continue
        n += sum(1 for b in j["births"] if b and b[0] == "words")
    return n


def shelf_episodes_from_tape(tape: Iterable[dict]) -> List[Dict[str, object]]:
    """Every shelf "sentence moment" as a `words_in_instant` row -- genome.sentence.find_frames' own input
    shape (_FakeEpisode's `.get(eid)["words_in_instant"]`) -- built PURELY from the tape: every `ear` row
    with `meta.source == "shelf"` published BEFORE its own moment's `eye` row (PREREG §2.2's order law)
    supplies that moment's words, in publish order (creature/senses/read.py's own chunk order). Never reads
    the mind's FAST ring (the SAME tape-only discipline `world_pair_skew` above already uses for the game's
    missions) -- so this is gradable on a closed record with no episodes.npz at all."""
    tape = list(tape)
    words_by_moment: Dict[str, List[str]] = {}
    for r in tape:
        if r.get("sense") == "ear" and _meta(r).get("source") == "shelf":
            words_by_moment.setdefault(_meta(r)["moment"], []).append(str(_meta(r).get("word")))
    out: List[Dict[str, object]] = []
    i = 0
    for r in tape:
        if r.get("sense") == "eye" and _meta(r).get("source") == "shelf":
            words = words_by_moment.get(_meta(r)["moment"], [])
            out.append({"id": i, "words_in_instant": words})
            i += 1
    return out


def shuffled_shelf_episodes(rows: List[Dict[str, object]], seed: int = 20260923) -> List[Dict[str, object]]:
    """The shuffled twin (task 4's own words: "vs the shuffled twin"): every word across every shelf moment,
    pooled and shuffled (a fixed seed -- #158's law: never re-drawn until it looks better), then
    redistributed back into moments of their ORIGINAL lengths -- word MARGINALS (how often "cat" appears at
    all) and each moment's OWN size are preserved; the actual observed PAIRING (which words met in the SAME
    moment) is destroyed. A pair genome.sentence.find_frames() still files on this shuffled corpus is, by
    construction, a false positive its own statistical bar (count > factor*expected) could not tell apart
    from chance -- the standard permutation-test null for a co-occurrence claim."""
    rng = np.random.default_rng(seed)
    lengths = [len(r["words_in_instant"]) for r in rows]
    pool: List[str] = [w for r in rows for w in r["words_in_instant"]]
    order = rng.permutation(len(pool))
    shuffled_pool = [pool[i] for i in order]
    out: List[Dict[str, object]] = []
    i = 0
    for idx, n in enumerate(lengths):
        out.append({"id": idx, "words_in_instant": shuffled_pool[i:i + n]})
        i += n
    return out


def read_frames(tape: Iterable[dict], shuffle_seed: int = 20260923) -> Dict[str, object]:
    """Frames filed from shelf moments (genome.sentence.find_frames -- "SENTENCE's own twin machinery",
    task 4's own words) + the shuffled-twin precision: of the pairs find_frames() files on the REAL shelf
    corpus, the share that do NOT also get filed on the shuffled corpus (a pair the shuffle still files is
    indistinguishable from a false positive under find_frames' own bar). `None` precision when nothing was
    filed on the real corpus (never a spurious 0 or 1 — #162's class: a ratio needs a denominator)."""
    from genome.sentence import find_frames, _FakeEpisode
    rows = shelf_episodes_from_tape(tape)
    real = find_frames(_FakeEpisode(rows))
    twin_rows = shuffled_shelf_episodes(rows, seed=shuffle_seed)
    twin = find_frames(_FakeEpisode(twin_rows))
    real_pairs = {(f["w1"], f["w2"]) for f in real}
    twin_pairs = {(f["w1"], f["w2"]) for f in twin}
    true_pairs = real_pairs - twin_pairs
    precision = (len(true_pairs) / len(real_pairs)) if real_pairs else None
    multiword = sum(1 for r in rows if len({w for w in r["words_in_instant"] if w}) >= 2)
    return {"shelf_moments": len(rows), "shelf_multiword_moments": multiword, "filed": len(real),
            "true_vs_shuffled": len(true_pairs), "shuffled_filed": len(twin),
            "precision": (round(precision, 4) if precision is not None else None),
            "pairs": sorted(f"{w1}|{w2}" for w1, w2 in real_pairs)}


def read_mark(tape: Iterable[dict], journal: Iterable[dict], read_declared: bool, recog: Optional[dict],
              recog_blind: Optional[dict], min_words_born: int = 500, min_frames: int = 20,
              frame_precision_bar: float = 0.8, reading_bar: float = 0.6, shuffle_seed: int = 20260923) -> Dict[str, object]:
    """ALPHA4-PREREG.md §5 READ (H): words born from shelf moments >= `min_words_born`; frames from shelf
    moments >= `min_frames` with precision >= `frame_precision_bar` vs the shuffled twin; the READING mark
    (`recog`, from tools/read_recognised.py:recognised_share over the life's own snapshot) >= `reading_bar`;
    the blind twin (`recog_blind`, the SAME instrument over a Mind replayed with every shelf row dropped,
    tools/read_recognised.py:blind_twin_root) reads 0 by construction. `recog`/`recog_blind` are computed
    OUTSIDE this pure function (hands_mark's own precedent: a script does the I/O, this module only grades
    the numbers) — see the builder report for the RAISED clause on what "held out" means for the 50 words
    (the FONT, not the word: a word never heard has no words-cell, recall_many can only ever read 0 for it
    by construction, #228 (b)'s class — ALPHA4-H.md's own task-4 text asked for both at once, which cannot
    both hold)."""
    tape = list(tape); journal = list(journal)
    words_born = read_words_born(tape, journal)
    frames = read_frames(tape, shuffle_seed=shuffle_seed)
    out: Dict[str, object] = {
        "shelf_eye_rows": sum(1 for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "shelf"),
        "words_born_from_shelf": words_born, "frames": frames, "reading": recog, "reading_blind_twin": recog_blind,
        "bar": (f"words born from shelf >= {min_words_born} · frames from shelf >= {min_frames} with precision "
                f">= {frame_precision_bar} vs the shuffled twin · the reading mark >= {reading_bar} (50 shelf "
                f"words the life DID hear, rendered in the held-out font) · the blind twin reads 0 by construction"),
    }
    if not read_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: SENSE_READ not declared on this life")
        return out
    if not isinstance(recog, dict) or not recog.get("n"):
        out.update(graded=False, **{"pass": None}, reason="not gradable: no reading-mark asks on the record")
        return out
    ok_words = words_born >= min_words_born
    ok_frames = frames["filed"] >= min_frames and frames["precision"] is not None and frames["precision"] >= frame_precision_bar
    ok_reading = recog.get("share") is not None and float(recog["share"]) >= reading_bar
    blind_share = (recog_blind or {}).get("share")
    ok_blind = blind_share is not None and float(blind_share) == 0.0
    out.update(graded=True, clause_words_born=ok_words, clause_frames=ok_frames, clause_reading=ok_reading,
               clause_blind_twin=ok_blind, **{"pass": bool(ok_words and ok_frames and ok_reading and ok_blind)},
               reason="graded (ALPHA4-PREREG §5, READ/H)" + ("" if recog_blind is not None else "; the blind twin was not run — that clause FAILS"))
    return out   # edit: Claude (Fable 5.1), 2026-09-23 03:24 +0400 — restored at integration: the merge matched read_mark's closing `return out` with stage_mark's as shared context and kept ONE (read_mark returned None; five ReadMark tests errored on the merged bytes, none on H's branch)


# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:22 +0400 — ALPHA4-PREREG.md §5: WEB and STAGE (I).
def web_mark(tape: Iterable[dict], journal: Iterable[dict], door_web_declared: bool) -> Dict[str, object]:
    """§5 WEB: fetch counts (made [ok+failed] / refused_rate / refused_hold); every web row traceable to
    a question — this mark's own proxy (RAISED; see the builder report and creature/senses/web.py's own
    module docstring): builder H's lexicon door had not landed when this was written, so there is no real
    "QUESTION row" shape on the tape yet to cross-reference against — every `web` row's own `question_id`
    (never null, by construction of creature/senses/web.py's own `_record_meta`) is read as the mark's
    traceability proxy instead; a null there is what "a fetch without one" (the PREREG's own words) means
    here, and FAILS the mark. Under STAGE 3 (no stage-4 event on this record) the made count must be 0 —
    the door's own law, checked directly against the record rather than assumed."""
    rows = [r for r in tape if r.get("sense") == "web"]
    made = [r for r in rows if _meta(r).get("status") in ("ok", "failed")]
    refused_rate = [r for r in rows if _meta(r).get("status") == "refused_rate"]
    refused_hold = [r for r in rows if _meta(r).get("status") == "refused_hold"]
    untraceable = [r for r in rows if _meta(r).get("question_id") is None]
    stage4_events = [j for j in journal if j.get("event") == "stage" and j.get("stage") == 4]
    out: Dict[str, object] = {
        "web_rows": len(rows), "made": len(made), "refused_rate": len(refused_rate), "refused_hold": len(refused_hold),
        "untraceable": len(untraceable), "stage4_reached": bool(stage4_events),
        "bar": "made/refused_rate/refused_hold printed · every web row's question_id present (this mark's own traceability proxy, RAISED) · under STAGE 3 (no stage-4 event) made == 0",
    }
    if not door_web_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: DOOR_WEB not declared on this life")
        return out
    if not rows:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no web row on this tape (STAGE 4 never reached, or the door never had a question to serve)")
        return out
    stage3_law_ok = bool(stage4_events) or len(made) == 0
    out.update(graded=True, **{"pass": len(untraceable) == 0 and stage3_law_ok}, reason="graded (§5 WEB)")
    return out


def stage_mark(journal: Iterable[dict], stage_ready_declared: bool) -> Dict[str, object]:
    """§5 STAGE: the stage series by moment, each with the READINESS judge's own readings (a..e) at the
    moment it fired; exactly one stage-4 event or none — never more (the mind's own "never undone" law,
    checked directly: a second event would mean the guard in `_maybe_advance_stage` broke)."""
    events = [j for j in journal if j.get("event") == "stage"]
    series = [{"moment": j.get("moment"), "stage": j.get("stage"), "readings": j.get("readings")} for j in events]
    out: Dict[str, object] = {"stage_events": len(events), "series": series,
                              "bar": "the stage series by moment, each with its five readings · at most ONE stage-4 event, ever"}
    if not stage_ready_declared:
        out.update(graded=False, **{"pass": None}, reason='not gradable: STAGE_READY ("by READY") not declared on this life')
        return out
    out.update(graded=True, **{"pass": len(events) <= 1}, reason="graded (§5 STAGE)")
    return out


# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:58 +0400 — A4L-COST task 5 (docs/briefs/A4L-COST.md; docs/A4-LADDER-PREREG.md §1.9, §2.1 C1):
# the rung's own mark, a PURE function over the landed row shapes (#171/#173) — «not gradable» on a life whose genome does not declare HASH
# (the hour-1 fixture is the control: alpha4-1's genome declares none), else C1 (ii)/(iii) read from a record and a replay.
_NON_MIND_EVENTS = frozenset({"start", "sense_restart", "snapshot", "stop", "exam"})   # creature/replay.py's NON_MIND_EVENTS, repeated so this
                                                                                         # module stays import-light; a test pins them equal


def _first_diff(record: List[dict], replay: List[dict], ignore=()) -> Optional[Tuple[int, str]]:
    """creature/replay.py:compare's rule, pure: rows grouped by seq into ordered lists and compared field by field (minus `ignore`); the
    first (seq, field) that differs, a row-count mismatch at a seq, or a seq present on one side only."""
    a: Dict[int, List[dict]] = {}; b: Dict[int, List[dict]] = {}
    for r in record:
        a.setdefault(int(r["seq"]), []).append(r)
    for r in replay:
        b.setdefault(int(r["seq"]), []).append(r)
    skip = set(ignore)
    for seq in sorted(set(a) | set(b)):
        ra, rb = a.get(seq), b.get(seq)
        if ra is None:
            return seq, "<missing from the record>"
        if rb is None:
            return seq, "<missing from the replay>"
        if len(ra) != len(rb):
            return seq, f"<row count: record {len(ra)} vs replay {len(rb)}>"
        for x, y in zip(ra, rb):
            for key in sorted((set(x) | set(y)) - skip):
                if x.get(key) != y.get(key):
                    return seq, key
    return None


def hash_law_mark(journal: Iterable[dict], status: dict, declared: bool, replay_same: Optional[List[dict]] = None,
                  replay_floor: Optional[List[dict]] = None) -> Dict[str, object]:
    """A4-LADDER-PREREG §2.1 C1, read from a record and a replay. (iii) a replay of the life's own tape under the RUNG's code and genome is
    identical to the record INCLUDING `hash` — the sparse witness replays; (ii) a replay under the FLOOR genome (no HASH line) is identical
    EXCEPT `hash`, and every hashed row's value differs (the sparse digest is domain-separated) — the witness decides nothing; STATUS names
    the form it ran (`hash_form` sparse; a HASH life whose STATUS says dense did not run the sparse witness). Each clause is graded on what
    is given; a missing replay is printed «not read». «not gradable» when HASH is undeclared (the dense per-row witness) or no replay is
    given. `journal`: the life's mind rows (event bookkeeping rows are dropped here)."""
    J = [r for r in journal if r.get("event") not in _NON_MIND_EVENTS]
    hashed = [r for r in J if "hash" in r]
    form = status.get("hash_form", "not recorded")
    out: Dict[str, object] = {"mind_rows": len(J), "hash_rows": len(hashed), "status_hash_form": form,
                              "status_hash_ms_last": status.get("hash_ms_last", "not recorded"),
                              "iii": None, "iii_first_diff": None, "ii": None, "ii_first_diff": None, "hash_rows_differing_from_floor": None,
                              "bar": "(iii) the rung's replay identical INCLUDING hash · (ii) the floor's replay identical EXCEPT hash, every hashed "
                                     "row's value differing · STATUS hash_form sparse"}
    if not declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: HASH not declared on this life (the dense per-row witness — the floor)")
        return out
    if replay_same is None and replay_floor is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no replay given (C1 (ii)/(iii) are read from a record AND a replay)")
        return out
    ok = form != "dense"
    if replay_same is not None:
        S = [r for r in replay_same if r.get("event") not in _NON_MIND_EVENTS]
        d = _first_diff(J, S)
        out["iii_first_diff"] = list(d) if d else None
        out["iii"] = "identical including hash" if d is None else f"DIVERGED at seq {d[0]} ({d[1]})"
        ok = ok and d is None
    else:
        out["iii"] = "not read (no replay under the rung's own code and genome given)"
    if replay_floor is not None:
        F = [r for r in replay_floor if r.get("event") not in _NON_MIND_EVENTS]
        d = _first_diff(J, F, ignore=("hash",))
        out["ii_first_diff"] = list(d) if d else None
        out["ii"] = "identical except hash" if d is None else f"DIVERGED at seq {d[0]} ({d[1]})"
        fh: Dict[int, List[str]] = {}
        for r in F:
            if "hash" in r:
                fh.setdefault(int(r["seq"]), []).append(r["hash"])
        seen: Dict[int, int] = {}; differ = 0
        for r in hashed:
            s_ = int(r["seq"]); i_ = seen.get(s_, 0); seen[s_] = i_ + 1
            other = fh.get(s_, [])
            differ += (i_ < len(other) and other[i_] != r["hash"])
        out["hash_rows_differing_from_floor"] = differ
        ok = ok and d is None and differ == len(hashed)
    else:
        out["ii"] = "not read (the floor's replay of this tape is the tape twin's, A4-LADDER-PREREG §1.4 (c))"
    out.update(graded=True, **{"pass": bool(ok)},
               reason="graded (A4-LADDER-PREREG §2.1 C1)" + ("" if form != "dense" else " — STATUS says the life ran the DENSE witness"))
    return out
