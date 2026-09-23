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


def act_mark(tape: Iterable[dict], journal: Iterable[dict], status: dict, min_outcomes: int = 100, last_n: int = 100) -> Dict[str, object]:
    """PREREG §19.5: outcome rows with chosen_by == mind = 100 % of the game's outcome rows; act_mismatch 0 (the journal's own check and
    STATUS); the census per act (G-MOT-1: no act ≥ 95 %, no reachable act at 0); the reward printed beside G's random null 0.29, no bar.
    Not gradable when the game published fewer than `min_outcomes` outcome rows or the mind chose none (the worker's schedule chose).

    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (3), the third hand's review of alpha4-1 §6:
    the census is over the GAME's own acts — the tape's mind-chosen game outcome rows in seq order — never STATUS `acts_chosen`, which
    counts the mouth's `say` beside the seven game acts (creature/mind.py:_maybe_say, the C×D seam) over the whole life (`left` read 244
    of 669 = 36 % there at 09:41 while it was 96 of the last 100 game acts). «no act ≥ 95 %» reads the census of the LAST `last_n` game
    acts (a lock the whole-life census cannot see); «no reachable act at 0» reads the whole life. STATUS's dict is printed as
    `census_all` (the old number), never graded."""
    game_out = [r for r in tape if r.get("sense") == "outcome" and _meta(r).get("source") == "game"]
    mind = [r for r in game_out if _meta(r).get("chosen_by") == "mind"]
    act_names: List[str] = []
    for r in tape:
        if r.get("sense") == "eye" and _meta(r).get("act_names"):
            act_names = list(_meta(r)["act_names"]); break
    choices = [j for j in journal if isinstance(j.get("act"), dict)]
    mism_j = sum(1 for j in journal if isinstance(j.get("outcome"), dict) and j["outcome"].get("act_mismatch"))
    census_all = dict(status.get("acts_chosen") or {})
    if not census_all:
        census_all = dict(collections.Counter(j["act"].get("act") for j in choices))
    game_acts = [str(_meta(r).get("act")) for r in mind]
    reachable = act_names or sorted(set(game_acts))
    census: Dict[str, int] = {a: 0 for a in reachable}
    for a in game_acts:
        census[a] = census.get(a, 0) + 1
    last = game_acts[-last_n:] if last_n > 0 else []
    census_last: Dict[str, int] = {a: 0 for a in reachable}
    for a in last:
        census_last[a] = census_last.get(a, 0) + 1
    total = len(game_acts)
    max_share = (max(census.values()) / total) if total else None
    max_share_last = (max(census_last.values()) / len(last)) if last else None
    zero_acts = [a for a in reachable if census.get(a, 0) == 0]
    rewards = [float(_meta(r).get("got") or 0.0) for r in game_out]
    episodes = sum(1 for r in game_out if _meta(r).get("terminated") or _meta(r).get("truncated"))
    successes = sum(1 for r in game_out if float(_meta(r).get("got") or 0.0) > 0)
    out: Dict[str, object] = {
        "game_outcomes": len(game_out), "mind_chosen": len(mind), "mind_share": (len(mind) / len(game_out)) if game_out else None,
        "choices_journaled": len(choices), "mismatches_journal": mism_j, "mismatches_status": int(status.get("act_mismatches") or 0),
        "census": census, "max_share": (round(max_share, 4) if max_share is not None else None), "zero_acts": zero_acts,
        f"census_last{last_n}": census_last, f"max_share_last{last_n}": (round(max_share_last, 4) if max_share_last is not None else None),
        "last_n": len(last), "census_all": census_all,
        "census_source": "the tape's mind-chosen game outcome rows (seq order): the game's own acts; census_all = STATUS acts_chosen (with the mouth's say), printed only",
        "reachable_acts": reachable, "reward_mean": (round(sum(rewards) / len(rewards), 4) if rewards else None),
        "episodes": episodes, "successes": successes, "success_per_episode": (round(successes / episodes, 4) if episodes else None),
        "random_null_success": 0.29,
        "bar": f"mind-chosen = 100 % of ≥ {min_outcomes} game outcomes · mismatches 0 · census over the GAME's acts: no act ≥ 95 % of the last {last_n} game acts, no reachable act at 0 over the life · the shuffled-act plant diverges · reward printed, no bar",
    }
    if not game_out:
        out.update(graded=False, pass_=None, reason="not gradable: the game published no outcome rows on this tape")
    elif not mind:
        out.update(graded=False, pass_=None, reason="not gradable: no outcome row was chosen by the mind (the worker's schedule chose — the ACT line did not drive the game)")
    elif len(game_out) < min_outcomes:
        out.update(graded=False, pass_=None, reason=f"not gradable: {len(game_out)} game outcomes < {min_outcomes}")
    else:
        ok = (len(mind) == len(game_out)) and mism_j == 0 and int(status.get("act_mismatches") or 0) == 0 \
            and (max_share_last is not None and max_share_last < 0.95) and not zero_acts
        out.update(graded=True, pass_=ok, reason=f"graded (§19.5; the ≥ 95 % clause on the last {len(last)} game acts)")
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
    # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:43 +0400 — A4L-VOICE task 5: on a VOICED tape the eye row that
    # BINDS a maker sound carries a `sound` dict too ({seq, winners, cells}); counting it would read consumed > rows on every voiced
    # tape. A binding row is told by its SHAPE (its `sound` dict carries `winners`; a sound row's never does) and is never counted
    # as a consumption. Heard time sums each row's `duration_s` when the maker stamps it (a chord is 0.45 s), else its onset `when`
    # as before; the maker's rows and the bound canvases are printed.
    consumed = [j for j in journal if isinstance(j.get("sound"), dict) and "error" not in j["sound"] and "winners" not in j["sound"]]
    errors = [j for j in journal if isinstance(j.get("sound"), dict) and "error" in j["sound"]]
    bound = [j for j in journal if isinstance(j.get("sound"), dict) and "winners" in j["sound"]]
    heard_s = 0.0
    try:
        heard_s = float(sum(float(_meta(r).get("duration_s") or _meta(r).get("when") or 0.0) for r in rows))
    except Exception:
        heard_s = 0.0
    out: Dict[str, object] = {"ear_sound_rows": len(rows), "consumed": len(consumed), "errors": len(errors),
                              "voiced_rows": sum(1 for r in rows if _meta(r).get("source") == "maker"), "bound_rows": len(bound),
                              "heard_s": round(heard_s, 3),
                              "status_sound_events": status.get("sound_events", "not recorded"),
                              "status_voice_rows": status.get("voice_rows", "not recorded"), "status_voice_bound": status.get("voice_bound", "not recorded"),
                              "bar": "every ear-sound row consumed into the sound ring, 0 errors; not gradable while the world is silent"}
    if not rows:
        out.update(graded=False, **{"pass": None}, reason="not gradable: heard 0 s — no ear-sound row on the tape (the world is silent; the plan's §10 names the rung that brings a voice)")
    else:
        out.update(graded=True, **{"pass": len(consumed) == len(rows) and not errors}, reason="graded (§19.10)")
    return out


def plant_showings(journal: Iterable[dict], plant_word: str = "zog") -> int:
    """edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (10): how many canvases showed the plant, from
    the journal's glance rows (`moment` + `word`; the coarse row carries no word) — `sizing_mark`'s own count, shared so GRADE and (vi)
    read the same fact. The plant lands at maker canvas PLANT_AFTER (15,000 on alpha4-1 ≈ hour 21): before it, a plant clause has
    nothing to read."""
    return sum(1 for j in journal if "moment" in j and j.get("act") != "coarse" and j.get("word") == plant_word)


def plant_clause(ok: Optional[bool], plant_shown: Optional[int], what: str) -> Dict[str, object]:
    """READER-FIX-0923 (10): a mark's PLANT clause is NOT GRADABLE while the plant was never shown (printed, never FAIL); graded from the
    first showing. `plant_shown` None = the caller could not count (an older call) — graded as before."""
    if plant_shown is not None and int(plant_shown) == 0:
        return {"graded": False, "pass": None, "plant_shown": 0, "what": what,
                "reason": "not gradable: plant shown 0 (the plant lands at the maker's PLANT_AFTER canvas; graded from its first showing)"}
    return {"graded": True, "pass": bool(ok), "plant_shown": plant_shown, "what": what, "reason": "graded"}


def grade_mark(plant: dict, null: dict, seen: dict, answer_declared: bool, plant_shown: Optional[int] = None) -> Dict[str, object]:
    """PREREG §19.3 (builder A's shapes: `graded` = {sure_bare, unsure, abstain_with_resemblance, abstain} on the reader's own plant/null
    asks; `hedge_rate` on the seen-words Q1): the null «vex» sure-bare ≤ 1 of 10 and unsure+abstain ≥ 8 of 10 (a 5/10 tie is a FAIL);
    the plant «zog» ANSWERED (the cell) ≥ 6 of 10 with its grade distribution printed; the hedge rate printed (the plan predicted < 10 %;
    L1's replay read 0.426 — a finding).
    edit: Claude (Fable 5.1), 2026-09-22 22:27 +0400 — the plant clause RE-SPECIFIED before the life (#228 (b)): «sure ≥ 6/10» sat above
    its ceiling — builder A's real-record grades on held-out renders read sure/unsure 10/0 … 0/10 per thing (LIFE-A-REPORT.md §2; hedge
    0.426), so a word seen five times grading «sure» six times in ten is a coin flip by construction. The plant's mark is the cell (G4's
    own (vi)); the grade's own mark is the null's two clauses, unchanged.
    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (10): the plant clause is NOT GRADABLE while
    `plant_shown` is 0 (alpha4-1's 2 h smoke read GRADE FAIL on «plant answered 0.0» with the plant 19 hours away); the null's two
    clauses stay graded and carry the mark; the plant clause is printed as `plant_clause` with its reason."""
    gp = (plant or {}).get("graded"); gn = (null or {}).get("graded")
    hedge = ((seen or {}).get("Q1") or {}).get("hedge_rate")
    par = (plant or {}).get("answered_rate")
    out: Dict[str, object] = {"plant_graded": gp, "null_graded": gn, "hedge_rate": hedge, "plant_answered_rate": par, "plant_shown": plant_shown,
                              "bar": "null sure-bare ≤ 1/10 · null unsure+abstain ≥ 8/10 (a tie fails) · plant ANSWERED ≥ 6/10 (its grades printed; not gradable while the plant was never shown) · hedge rate printed, no bar (predicted < 0.10)"}
    if not answer_declared or not isinstance(gp, dict) or not isinstance(gn, dict) or par is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: ANSWER not declared / no graded counts on the asks (a life before the graded answer)")
        return out
    n_null = sum(gn.values()) or 1; n_plant = sum(gp.values()) or 1
    null_sb = int(gn.get("sure_bare", 0)); null_soft = int(gn.get("unsure", 0)) + int(gn.get("abstain_with_resemblance", 0)) + int(gn.get("abstain", 0))
    plant_sure = int(gp.get("sure_bare", 0))
    pc = plant_clause(float(par) >= 0.6, plant_shown, "plant ANSWERED ≥ 6/10")
    ok_null = (null_sb / n_null <= 0.1) and (null_soft / n_null >= 0.8)
    out.update(null_sure_bare=null_sb, null_soft=null_soft, null_n=n_null, plant_sure=plant_sure, plant_n=n_plant, plant_clause=pc,
               graded=True, **{"pass": bool(ok_null and (pc["pass"] if pc["graded"] else True))},
               reason="graded (§19.3)" + ("" if pc["graded"] else "; the plant clause " + pc["reason"]))
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
    within its next canvases printed (the plan's prediction ≥ 0.5 for maker things). Not gradable without the gene or under 2 h.

    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (5), the third hand's review §4: the answered
    share counts each QUESTION once. `answered_rows` counted the maker's answer twice (it stamps `answering` on BOTH its ear and eye
    rows, creature/world_maker.py:68-70) and the lexicon door's answers never (its eye row carries `answers: <word>` and a moment hashed
    from (word, qid), creature/senses/lexicon.py:_moment_id — imported, never re-typed). qid = `q-<n>`, n the question row's own payload
    `seq` (the ask/out index both doors key on). Printed: maker / lexicon / both / unanswered, and the questions about the hands' own
    pictures (args[0] a moment whose eye row is `source: hands`) — no door answers a hands moment."""
    from creature.senses.lexicon import _moment_id as _lex_moment
    qs = [j for j in journal if isinstance(j.get("question"), dict)]
    answered = [r for r in tape if _meta(r).get("answering")]
    forms = collections.Counter(str(j["question"].get("q")) for j in qs)
    qids = [f"q-{j['question'].get('seq')}" for j in qs]
    qset = set(qids)
    maker_qids = {str(_meta(r)["answering"]) for r in answered}
    lex_rows = [r for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "lexicon" and _meta(r).get("answers")]
    lex_moments = {str(_meta(r).get("moment")) for r in lex_rows}
    lex_words = sorted({str(_meta(r)["answers"]) for r in lex_rows})
    lex_qids: set = set(); lex_matched: set = set()
    for q in qids:
        for w in lex_words:
            mid = _lex_moment(w, q)
            if mid in lex_moments:
                lex_qids.add(q); lex_matched.add(mid)
    by_maker = maker_qids & qset; by_lex = lex_qids & qset; ans = by_maker | by_lex
    src_of = {str(_meta(r).get("moment")): _meta(r).get("source") for r in tape if r.get("sense") == "eye"}
    hands_q = {q for q, j in zip(qids, qs) if (j["question"].get("args") or [None])[0] is not None
               and src_of.get(str(j["question"]["args"][0])) == "hands"}
    unanswered = qset - ans
    un_forms = collections.Counter(str(j["question"].get("q")) for q, j in zip(qids, qs) if q in unanswered and q not in hands_q)
    out: Dict[str, object] = {"questions": len(qs), "forms": dict(forms), "answered_rows": len(answered),
                              "answered_by_maker": len(by_maker), "answered_by_lexicon": len(by_lex), "answered_by_both": len(by_maker & by_lex),
                              "answered": len(ans), "unanswered": len(unanswered),
                              "hands_picture_questions": len(hands_q), "unanswered_hands_pictures": len(hands_q & unanswered),
                              "unanswered_other_by_form": dict(un_forms),
                              "answered_share": (round(len(ans) / len(qs), 4) if qs else None),
                              "lexicon_answers_on_tape": len(lex_rows), "lexicon_answers_unattributed": len(lex_moments - lex_matched),
                              "maker_answers_not_a_question": sorted(maker_qids - qset),
                              "status_written": status.get("questions_written", "not recorded"), "status_answered": status.get("questions_answered", "not recorded"),
                              "bar": "questions ≥ (hours − 2)/2 · the answered share printed (prediction ≥ 0.5 for maker things): each question once, by the maker or the lexicon door"}
    if not question_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: QUESTION not declared on this life"); return out
    if hours < 2.0:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {hours} h < 2 h (questions are graded after hour 2)"); return out
    need = max(1, int((hours - 2.0) / 2.0))
    out.update(needed=need, graded=True, **{"pass": len(qs) >= need}, reason=f"graded (§19.7): {len(qs)} questions vs {need} needed")
    return out


def _max_lift(pairs: "collections.Counter") -> Tuple[Optional[float], Optional[str]]:
    n = sum(pairs.values())
    if not n:
        return None, None
    pc: collections.Counter = collections.Counter(); po: collections.Counter = collections.Counter()
    for (c, o), k in pairs.items():
        pc[c] += k; po[o] += k
    best = None; best_pair = None
    for (c, o), k in pairs.items():
        if k < 5: continue
        lift = k / (n * (pc[c] / n) * (po[o] / n))
        if best is None or lift > best: best, best_pair = lift, f"{c} {o}"
    return (round(best, 4) if best is not None else None), best_pair


def world_pair_skew(tape: Iterable[dict]) -> Dict[str, object]:
    """The world's OWN pair skew (PREREG §19.8's ceiling clause): over the game's missions on the tape (the mission's last two tokens =
    colour, object), the max lift count / (n · p(colour) · p(object)) over pairs met ≥ 5 times.

    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (4), the third hand's review §6: ONE mission per
    game EPISODE, never one per frame — every frame of an episode republishes the same mission (creature/senses/game.py:209-225), so a
    64-frame episode was 64 «meetings» and one episode cleared «met ≥ 5» alone (alpha4-1's hour 1: 121 frames, 2 episodes, lift 2.16
    «gradable»): the gate measured episode sparsity, not the world. An episode is a RUN of object rows with one (game, episode) — a run,
    so an episode id a restarted worker re-uses is a new mission; a row without an `episode` (an older game door) is its own mission,
    the old count, and says so. The per-frame count and its lift are printed beside, never graded."""
    per_frame: collections.Counter = collections.Counter(); episodes: List[Tuple[str, str]] = []
    prev_key = object(); no_episode = 0
    for r in tape:
        m = _meta(r)
        if r.get("sense") != "ear" or m.get("source") != "game" or not m.get("mission"):
            continue
        toks = str(m["mission"]).split()
        if len(toks) < 2 or m.get("word") != toks[-1]:
            continue                                  # each FRAME once, on its object row
        pair = (toks[-2], toks[-1])
        per_frame[pair] += 1
        if m.get("episode") is None:
            no_episode += 1; episodes.append(pair); prev_key = object(); continue
        key = (m.get("game"), m.get("episode"))
        if key != prev_key:
            episodes.append(pair); prev_key = key
    pairs: collections.Counter = collections.Counter(episodes)
    n = sum(pairs.values())
    lift_f, pair_f = _max_lift(per_frame)
    base = {"missions_per_frame": sum(per_frame.values()), "max_lift_per_frame": lift_f, "max_pair_per_frame": pair_f,
            "rows_without_episode": no_episode, "missions_unit": "one per game episode (a run of object rows with one (game, episode))"}
    if not n:
        return {"missions": 0, "max_lift": None, "max_pair": None, "pairs": 0, **base}
    best, best_pair = _max_lift(pairs)
    return {"missions": n, "max_lift": best, "max_pair": best_pair, "pairs": len(pairs), **base}


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
    if skew["missions"] < min_missions:   # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (4): missions are EPISODES
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {skew['missions']} missions < {min_missions} (one per game episode; {skew.get('missions_per_frame')} frames)"); return out
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


def _parse_at(s: str):
    import datetime as _dt
    return _dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def sleep_times(tape: Iterable[dict], journal: Iterable[dict]) -> List[Tuple[int, object]]:
    """edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (7): every `sleep` journal row as (seq, time).
    The row carries the TRIGGERING canvas's seq and no clock (creature/mind.py:_maybe_sleep journals it after the sleep, on that seq);
    its time is that tape row's `at` — the stall of the sleep's merge begins at it (plus the mind's lag, rows, never minutes)."""
    at_of = {int(r["seq"]): r["at"] for r in tape if r.get("at") is not None and r.get("seq") is not None}
    out = [(int(j["seq"]), _parse_at(at_of[int(j["seq"])])) for j in journal
           if isinstance(j.get("sleep"), dict) and j.get("seq") is not None and int(j["seq"]) in at_of]
    return sorted(out, key=lambda x: x[1])


def sleep_gap_attribution(tape: Iterable[dict], journal: Iterable[dict], bar: float, window_s: float = 60.0,
                          senses: Tuple[str, ...] = ("eye", "ear")) -> Dict[str, object]:
    """READER-FIX-0923 (7), the third hand's review §2/§6: the two longest eye gaps of alpha4-1's first five hours sat on sleeps 18 and 17
    (the cycle's pure-Python O(n²) merge). Every gap between consecutive rows of one sense is IN a sleep's minute when it overlaps
    [t, t + window_s], t = the sleep row's tape time; printed: the max inside and outside those minutes, and every gap over the bar with
    the sleep it sits on (None = outside). The bar is not touched here — the reader attributes, it never excuses."""
    import bisect
    import datetime as _dt
    tape = list(tape)
    sleeps = sleep_times(tape, journal)
    ts = [t for _s, t in sleeps]
    w = _dt.timedelta(seconds=window_s)
    inside: List[float] = []; outside: List[float] = []; over: List[dict] = []; per_sleep: Dict[int, float] = {}
    for sense in senses:
        rows = [(int(r["seq"]), _parse_at(r["at"])) for r in tape if r.get("sense") == sense and r.get("at") is not None]
        for (_sa, a), (_sb, b) in zip(rows, rows[1:]):
            gap = (b - a).total_seconds()
            i = bisect.bisect_right(ts, a - w)              # the first sleep with t > a − window: it overlaps iff t < b
            sleep_seq = sleeps[i][0] if (i < len(ts) and ts[i] < b) else None
            (inside if sleep_seq is not None else outside).append(gap)
            if sleep_seq is not None:
                per_sleep[sleep_seq] = max(per_sleep.get(sleep_seq, 0.0), gap)
            if gap > bar:
                over.append({"sense": sense, "at": a.isoformat(timespec="milliseconds"), "gap_s": round(gap, 3), "sleep_seq": sleep_seq})
    over.sort(key=lambda d: d["at"])
    return {"sleeps_on_record": len(sleeps), "sleep_window_s": window_s,
            "max_gap_in_sleep_minutes_s": (round(max(inside), 3) if inside else None),
            "max_gap_outside_sleep_minutes_s": (round(max(outside), 3) if outside else None),
            "over_bar_in_sleep_minutes": sum(1 for d in over if d["sleep_seq"] is not None),
            "over_bar_outside_sleep_minutes": sum(1 for d in over if d["sleep_seq"] is None),
            "gaps_over_bar": over, "sleep_minute_max_gaps": [[s, round(g, 3)] for s, g in sorted(per_sleep.items())],
            "attribution_rule": f"a gap between consecutive rows of one sense is IN a sleep's minute when it overlaps [t, t + {window_s:g} s], t = the tape time of the sleep row's triggering canvas (the journal's sleep row carries its seq, no clock)"}


def thread_mark(alive: dict, status: dict, threaded: bool, max_gap_bar: float = 5.1, waits_bar: float = 0.05,
                tape: Optional[Iterable[dict]] = None, journal: Optional[Iterable[dict]] = None) -> Dict[str, object]:
    """PREREG §19.2 (builder E's shapes): ALIVE's max sense gap ≤ 5.1 s (life 3b's, the box otherwise idle) with the think ms series
    printed; think_waits / thinks < 5 %. Not gradable when THINK is not on its own thread, or when no think ran.
    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (7): with the tape and the journal given, the
    gaps are ATTRIBUTED (`sleep_gap_attribution`): those in the minute after a `sleep` row and the max outside those minutes printed beside
    the max; the 5.1 s bar is unchanged. (`gaps_per_hour` is ALIVE's per-SENSE pair [eye, ear] — a misnomer kept for the record.)"""
    gaps = [float(g) for g in (alive or {}).get("max_gap_s_eye_ear") or [] if g is not None]
    thinks = int(status.get("thinks") or 0); waits = int(status.get("think_waits") or 0)
    out: Dict[str, object] = {"max_gap_s": (max(gaps) if gaps else None), "gaps_per_hour": gaps, "thinks": thinks, "think_waits": waits,
                              "waits_share": (round(waits / thinks, 4) if thinks else None), "think_wait_ms": status.get("think_wait_ms", "not recorded"),
                              "think_ms_last": status.get("think_ms_last", "not recorded"), "think_ms_median": status.get("think_ms_median", "not recorded"),
                              "bar": f"max sense gap ≤ {max_gap_bar} s · think_waits / thinks < {waits_bar:.0%} (gaps attributed to sleeps, printed, never excused)"}
    if tape is not None and journal is not None:
        out.update(sleep_gap_attribution(tape, journal, bar=max_gap_bar))
    if not threaded:
        out.update(graded=False, **{"pass": None}, reason="not gradable: THINK is not on its own thread on this life"); return out
    if thinks == 0 or not gaps:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no think ran / no sense gaps on the record"); return out
    out.update(graded=True, **{"pass": max(gaps) <= max_gap_bar and (waits / thinks) < waits_bar}, reason="graded (§19.2)")
    return out


def evolve_mark(tape: Iterable[dict], journal: Iterable[dict], evolve_declared: bool, hours: float,
                 negative_control: Optional[Dict[str, dict]] = None, every_h: Optional[float] = None) -> Dict[str, object]:
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
    it did not produce, independent of whether the change is actually better or worse.

    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (1), the third hand's review §6: a VOID round
    is not a judged round. The designed minute-2 round (tools/evolve.py:355 — no shadow checkpoint yet, epoch 0) publishes a proposal
    row with `reason` «not gradable: …» and NO incumbent/mutant readings; «every proposal paired» failed on it by construction on every
    ALPHA4 life. A void round = no paired readings AND a reason that says «not gradable» (both — an unpaired row with any other reason is
    still a defect and still FAILS); void rounds are printed (`void_rounds`, their reasons) and excluded from the ≥ 3 count, the pairing
    and the adoption bound. `every_h` (the genome's EVOLVE every) prints `rounds_possible` beside `needed` — a schedule fact."""
    proposals = [r for r in tape if r.get("sense") == "proposal"]
    def _is_paired(p) -> bool:
        return isinstance(_meta(p).get("incumbent"), dict) and isinstance(_meta(p).get("mutant"), dict)
    void = [p for p in proposals if not _is_paired(p) and str(_meta(p).get("reason") or "").startswith("not gradable")]
    void_ids = {id(p) for p in void}
    judged = [p for p in proposals if id(p) not in void_ids]
    paired = [p for p in judged if _is_paired(p)]
    epochs = [j for j in journal if isinstance(j.get("epoch"), dict)]
    epoch_events = [{"epoch": j["epoch"].get("epoch"), "genome_sha": j["epoch"].get("genome_sha"),
                      "moment": j["epoch"].get("moment"), "gene": j["epoch"].get("gene"), "value": j["epoch"].get("value")}
                     for j in epochs]
    lags = [int(_meta(p)["shadow_lag_rows"]) for p in proposals if isinstance(_meta(p).get("shadow_lag_rows"), (int, float))]
    out: Dict[str, object] = {
        "proposals": len(proposals), "judged_rounds": len(judged), "void_rounds": len(void),
        "void_round_reasons": [str(_meta(p).get("reason")) for p in void],
        "paired_readings": len(paired), "adoptions": len(epochs),
        "epoch_events": epoch_events, "hours": hours, "negative_control": negative_control,
        "every_h": every_h, "rounds_possible": (int(hours // every_h) if every_h else None),
        "max_shadow_lag_rows": (max(lags) if lags else None),
        "bar": "JUDGED rounds >= 3 scaled to the record's own hours (min 1; a void round — no readings, reason «not gradable» — is printed, "
               "never counted) · every judged round paired (incumbent+mutant readings) · adoptions <= judged rounds · every adoption's genome "
               "sha printed · REPLAY identical across epochs (the existing REPLAY mark, on a tape carrying a proposal row) · the negative "
               "control's planted-bad and null mutants both REFUSED · max_shadow_lag_rows printed, never gated (#236)",
    }
    if not evolve_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: EVOLVE not declared on this life")
        return out
    if hours <= 0:
        out.update(graded=False, **{"pass": None}, reason="not gradable: hours <= 0")
        return out
    needed = max(1, round(3 * hours / 24.0))
    all_paired = len(paired) == len(judged)
    adoptions_ok = len(epochs) <= len(judged)
    nc_ok: Optional[bool] = None
    if negative_control is not None:
        nc_ok = (negative_control.get("planted_bad", {}).get("verdict") == "REFUSED"
                 and negative_control.get("null", {}).get("verdict") == "REFUSED")
    out.update(
        needed=needed, graded=True,
        **{"pass": bool(len(judged) >= needed and all_paired and adoptions_ok and (nc_ok is not False))},
        reason=(f"graded (§5/§6): {len(judged)} judged rounds vs {needed} needed (+{len(void)} void, printed); paired {len(paired)}/{len(judged)}; "
                f"adoptions {len(epochs)} <= judged rounds; negative control "
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
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (10): «the plant birthed ≥ 1 sight cell» is NOT
    # GRADABLE while the plant was never shown (alpha4-1's 2 h smoke: plant shown 0 read SIZING FAIL); the other clauses stay graded.
    pc = plant_clause(plant_births >= 1, plant_shown, "the plant birthed ≥ 1 sight cell")
    out["plant_clause"] = pc
    ok_plant = pc["pass"] if pc["graded"] else True
    plant_txt = f"plant births {plant_births}" if pc["graded"] else "plant clause not gradable (plant shown 0)"
    if grow:
        if not isinstance(born, int) or not isinstance(refused, int):
            out.update(graded=False, **{"pass": None}, reason="not gradable: sight_born / births_refused_nmax not on STATUS (an older body)")
        else:
            out.update(graded=True, **{"pass": bool(refused == 0 and ok_plant)},
                       reason=f"graded (§19.11, GROW): refused {refused}; {plant_txt}; born {born} (no band)")
    elif prediction is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight)")
    elif not isinstance(born, int) or not isinstance(nmax, int):
        out.update(graded=False, **{"pass": None}, reason="not gradable: sight_born / sight_nmax not on STATUS (an older body)")
    else:
        band = 0.5 * prediction <= born <= 1.5 * prediction
        out.update(graded=True, **{"pass": bool(band and int(refused or 0) == 0 and ok_plant)},
                   reason=f"graded (§19.11): band {'ok' if band else 'MISSED'}; refused {refused}; {plant_txt}")
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


def read_sample(heard: Iterable[str], tape: Iterable[dict], n: int = 50, seed: int = 20260923) -> Dict[str, object]:
    """edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (6) × (11): the reading mark's 50 words.
    (6) A fixed-seed draw (`random.Random(seed).sample`) over the WHOLE of read/HEARD.json in first-heard order, never its newest 50 (the
    20/50 NEWEST are the least-exposed words — the third hand's review §3). (11) Drawn only from the words the SHELF owns on the CUT tape:
    a word also heard from another source (7 of 255 in alpha4-1's hour 1 — the lexicon's glosses: of/and/with/or/to/more/a) keeps a
    words-cell in the blind twin (shelf rows dropped), so «the blind twin reads 0 by construction» holds only without them; a word not on
    the cut tape's shelf rows was never heard by the twins (read with --hours under the life's length). Both exclusions printed."""
    import random as _random
    heard = [str(w) for w in heard]
    shelf: set = set(); other: set = set()
    for r in tape:
        if r.get("sense") != "ear":
            continue
        w = _meta(r).get("word")
        if w:
            (shelf if _meta(r).get("source") == "shelf" else other).add(str(w))
    not_on_tape = [w for w in heard if w not in shelf]
    shared = [w for w in heard if w in shelf and w in other]
    eligible = [i for i, w in enumerate(heard) if w in shelf and w not in other]
    out: Dict[str, object] = {"seed": seed, "n": n, "population_heard": len(heard), "excluded_not_on_cut_tape": len(not_on_tape),
                              "excluded_other_source": shared, "eligible": len(eligible),
                              "rule": f"random.Random({seed}).sample over HEARD.json's words the shelf alone heard on the cut tape (first-heard order kept)"}
    if len(eligible) < n:
        out.update(indices=[], words=[], note=f"only {len(eligible)} eligible shelf words (of {len(heard)} heard); the mark asks {n}")
        return out
    idx = sorted(_random.Random(seed).sample(eligible, n))
    out.update(indices=idx, words=[heard[i] for i in idx], note="")
    return out


def read_mark(tape: Iterable[dict], journal: Iterable[dict], read_declared: bool, recog: Optional[dict],
              recog_blind: Optional[dict], min_words_born: int = 500, min_frames: int = 20,
              frame_precision_bar: float = 0.8, reading_bar: float = 0.6, shuffle_seed: int = 20260923,
              sample: Optional[dict] = None, blind_reason: Optional[str] = None) -> Dict[str, object]:
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
    # edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (11): the blind twin's clause. A twin that RAN is
    # graded (share == 0); a twin that CANNOT run (`blind_reason`: no shelf rows on the cut tape, no snapshot, --skip-twins, a worker error)
    # leaves the clause NOT GRADABLE, printed, never FAIL; neither given = the reader never tried — FAIL, as before (a mark cannot vouch for
    # a control nobody attempted). Its price (the twin's replay seconds) is printed in `blind_twin`.
    blind_ran = isinstance(recog_blind, dict) and recog_blind.get("share") is not None
    blind: Dict[str, object] = {"graded": bool(blind_ran) or blind_reason is None,
                                "share": (recog_blind or {}).get("share"), "n": (recog_blind or {}).get("n"),
                                "correct": (recog_blind or {}).get("correct"), "seconds": (recog_blind or {}).get("seconds"),
                                "reason": ("graded" if blind_ran else (blind_reason or "the blind twin was not run — that clause FAILS"))}
    out: Dict[str, object] = {
        "shelf_eye_rows": sum(1 for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "shelf"),
        "words_born_from_shelf": words_born, "frames": frames, "reading": recog, "reading_blind_twin": recog_blind,
        "reading_sample": sample, "blind_twin": blind,
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
    if blind_ran:
        ok_blind: Optional[bool] = float(recog_blind["share"]) == 0.0
    elif blind_reason is not None:
        ok_blind = None
    else:
        ok_blind = False
    out.update(graded=True, clause_words_born=ok_words, clause_frames=ok_frames, clause_reading=ok_reading,
               clause_blind_twin=ok_blind, **{"pass": bool(ok_words and ok_frames and ok_reading and (ok_blind is not False))},
               reason="graded (ALPHA4-PREREG §5, READ/H)" + ("" if blind_ran else "; the blind twin: " + str(blind["reason"])))
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


def stage_mark(journal: Iterable[dict], stage_ready_declared: bool, tape: Optional[Iterable[dict]] = None) -> Dict[str, object]:
    """§5 STAGE: the stage series by moment, each with the READINESS judge's own readings (a..e) at the
    moment it fired; exactly one stage-4 event or none — never more (the mind's own "never undone" law,
    checked directly: a second event would mean the guard in `_maybe_advance_stage` broke).

    edit: Claude (Opus 5.5, reader-fix builder), 2026-09-23 11:34 +0400 — READER-FIX-0923 (8), the third hand's review §3: «≤ 1 stage-4
    event» cannot fail and says nothing about WHY a door stayed shut. Beside the unchanged bar, the READINESS SERIES: per SIT boundary
    (the `sit` journal row's `readiness`, creature/mind.py:_consume_sit), which of (a)–(e) held, `b_read_proxy`, and — joined by seq from
    the tape's `sit` row — the exam's score/composite/read_share that (b)/(c) read; the count of boundaries where all five held and the
    longest run of them (two consecutive open the door). The numbers behind (a) the reward window, (b) frames alive/lift and (d) the
    grade counts are on NO record (the mind journals booleans) — a life-side gap, said here, not invented. The caller passes the mind's
    `stage` event rows beside the journal (gather's `mind_events`: they carry no `at`)."""
    journal = list(journal)
    events = [j for j in journal if j.get("event") == "stage"]
    series = [{"moment": j.get("moment"), "stage": j.get("stage"), "readings": j.get("readings")} for j in events]
    sit_meta = {int(r["seq"]): _meta(r) for r in (tape or []) if r.get("sense") == "sit" and r.get("seq") is not None}
    rs: List[Dict[str, object]] = []
    for j in journal:
        rd = j.get("readiness")
        if not isinstance(rd, dict):
            continue
        m = sit_meta.get(int(j["seq"]), {}) if j.get("seq") is not None else {}
        rs.append({"seq": j.get("seq"), **{k: rd.get(k) for k in "abcde"}, "b_read_proxy": rd.get("b_read_proxy"),
                   "score": m.get("score"), "composite": m.get("composite"), "read_share": m.get("read_share")})
    all5 = [all(x[k] is True for k in "abcde") for x in rs]
    longest = run = 0
    for ok in all5:
        run = run + 1 if ok else 0; longest = max(longest, run)
    out: Dict[str, object] = {"stage_events": len(events), "series": series,
                              "readiness_boundaries": len(rs), "held": {k: sum(1 for x in rs if x[k] is True) for k in "abcde"},
                              "all_five_held": sum(all5), "longest_all_five_streak": longest, "readiness_series": rs,
                              "readiness_note": "booleans from the mind's `sit` rows; the numbers behind (a) the reward window, (b) frames/lift and (d) grade counts are on no record (the mind journals booleans only)",
                              "bar": "the stage series by moment, each with its five readings · at most ONE stage-4 event, ever (the readiness series printed beside, never gating)"}
    if not stage_ready_declared:
        out.update(graded=False, **{"pass": None}, reason='not gradable: STAGE_READY ("by READY") not declared on this life')
        return out
    out.update(graded=True, **{"pass": len(events) <= 1}, reason="graded (§5 STAGE)")
    return out


# ============================================================================ A4L-VOICE: the rung's marks (A4-LADDER-PREREG §2.3)
# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:44 +0400 — docs/briefs/A4L-VOICE.md task 5. PURE functions over the
# shapes this branch LANDED: genome/questions.py:ask_sound's dict (V1/V2/V5/V1b, `gradable`, `voiced`), the exam file's
# `ask_seen_words.Q1.acc`, STATUS's sound keys. Written test-first (tests/creature/test_verdict_voice_marks.py); each reads «not
# gradable» on a record whose life has no sound area (the hour-1 fixture: alpha4-1 — the control, L-1's rule).
def hear_mark(rung: Optional[dict], blind_ear: Optional[dict], shuffled: Optional[dict], min_v1: int = 13, max_null_v1: int = 2,
              min_v2: float = 0.8, max_null_v2: float = 0.15, min_v5: float = 0.8) -> Dict[str, object]:
    """V1 (the thing named by SOUND, the letter ear blinded): on the `--blind ear` twin's final state, chord → sound → the
    strongest MEET edge to sight → the sight cell's birth ledger names the thing ≥ 13/16; the SHUFFLED-sound twin (the maker's
    chords permuted across things on the tape before replay, `shuffle_voice`) ≤ 2/16 by the true mapping. V2 (sight → sound, on
    the rung's own final state): held-out renders → the sound cell NAMED BY THE CHORD IT HOLDS ≥ 0.8; the shuffled twin ≤ 0.15.
    V5 (sound → words, the rung): ≥ 0.8 — «not gradable» when MEET sound words is off. V1b (the ±4 % chords) printed, no bar.
    Not gradable until every asked thing was voiced ≥ 5 times (the rung's own `voiced`), or when a twin is missing."""
    bar = (f"V1 blind-ear ≥ {min_v1}/16 and the shuffled twin ≤ {max_null_v1}/16 · V2 ≥ {min_v2} and the shuffled twin ≤ {max_null_v2} · "
           f"V5 ≥ {min_v5} (not gradable when MEET sound words is off) · not gradable until every thing voiced ≥ 5 times · V1b printed, no bar")
    out: Dict[str, object] = {"bar": bar}
    if not isinstance(rung, dict) or rung.get("V1") is None and rung.get("V2") is None:
        why = (rung or {}).get("reason") if isinstance(rung, dict) else None
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {why or 'no exam by sound on this record (no sound area — the voice was not declared)'}")
        return out
    if not rung.get("gradable"):
        out.update(graded=False, **{"pass": None}, reason=f"{rung.get('reason') or 'not gradable: a thing voiced < 5 times'}")
        return out
    if not isinstance(blind_ear, dict) or not isinstance(shuffled, dict) or blind_ear.get("V1") is None or shuffled.get("V1") is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the --blind ear twin or the shuffled-sound twin is missing")
        return out
    v1 = {"blind_ear_correct": int(blind_ear["V1"]["correct"]), "n": int(blind_ear["V1"]["n"]),
          "shuffled_correct": int(shuffled["V1"]["correct"]), "rung_correct": int((rung.get("V1") or {}).get("correct", 0)),
          "per_thing_blind_ear": (blind_ear["V1"] or {}).get("per_thing")}
    v1["pass"] = v1["blind_ear_correct"] >= min_v1 and v1["shuffled_correct"] <= max_null_v1
    v2r, v2s = rung.get("V2") or {}, shuffled.get("V2") or {}
    v2 = {"acc": v2r.get("acc"), "n": v2r.get("n"), "shuffled_acc": v2s.get("acc"), "ledger_correct": v2r.get("ledger_correct")}
    v2["pass"] = (v2["acc"] is not None and v2["acc"] >= min_v2) and (v2["shuffled_acc"] is not None and v2["shuffled_acc"] <= max_null_v2)
    v5r = rung.get("V5")
    if v5r is None:
        v5 = {"graded": False, "pass": None, "reason": "not gradable: MEET sound words is off (#OFF with its reason on the line)"}
    else:
        v5 = {"graded": True, "acc": v5r.get("acc"), "correct": v5r.get("correct"), "n": v5r.get("n"), "pass": float(v5r.get("acc") or 0.0) >= min_v5}
    out.update(V1=v1, V2=v2, V5=v5, V1b={"blind_ear": blind_ear.get("V1b"), "rung": rung.get("V1b")}, voiced=rung.get("voiced"))
    ok = bool(v1["pass"]) and bool(v2["pass"]) and (v5["pass"] if v5["graded"] else True)
    out.update(graded=True, **{"pass": ok}, reason="graded (A4-LADDER-PREREG §2.3 V1/V2/V5)")
    return out


def voice_harm_mark(rung_exam: Optional[dict], blind_sound_exam: Optional[dict], declared: bool, bar_delta: float = -0.01) -> Dict[str, object]:
    """V3 NO HARM (the regression bar): Q1 on seen words in the rung − the `--blind sound` replay of the SAME tape ≥ −0.01. Not
    gradable when the life did not declare the voice, or either exam is missing (the fixture clause — the hour-1 fixture under the
    rung genome ≡ master+FLOOR INCLUDING hash — is the landing gate's, not this mark's)."""
    out: Dict[str, object] = {"bar": f"Q1(rung) − Q1(--blind sound) ≥ {bar_delta}"}
    def q1(e):
        try:
            return float(((e or {}).get("ask_seen_words") or {}).get("Q1", {}).get("acc"))
        except (TypeError, ValueError):
            return None
    a, b = q1(rung_exam), q1(blind_sound_exam)
    out.update(q1_rung=a, q1_blind_sound=b)
    if not declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the voice (AREA sound) is not declared on this record")
    elif a is None or b is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the rung's exam or its --blind sound twin's exam is missing")
    else:
        d = round(a - b, 6)
        out.update(delta=d, graded=True, **{"pass": d >= bar_delta}, reason="graded (A4-LADDER-PREREG §2.3 V3)")
    return out


def sound_cells_mark(status: dict) -> Dict[str, object]:
    """V4 SOUND CELLS, printed (no bar): sound cells born / alive and refused (the ONE budget's sound refusals), the maker's voice
    rows consumed and bound. ≈ 17 born expected (one per chord); many more means the front does not band the chords — a finding."""
    keys = ("sound_born", "sound_cells", "sound_births_refused", "voice_rows", "voice_bound")
    out: Dict[str, object] = {k: (status or {}).get(k) for k in keys}
    out["bar"] = "printed, no bar — ≈ 17 expected (one per chord); many more is a finding"
    if (status or {}).get("sound_born") is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: STATUS carries no sound keys (a record before the voice)")
    else:
        out.update(graded=True, **{"pass": None}, reason="printed (A4-LADDER-PREREG §2.3 V4)")
    return out


def shuffle_voice(rows: List[dict], seed: int) -> Tuple[List[dict], Dict[str, str]]:
    """The SHUFFLED-SOUND twin's tape (V1/V2's null): copies of the rows with every MAKER ear-sound row's payload replaced by
    ANOTHER thing's chord, by a fixed DERANGEMENT of the voiced things drawn from `seed` (the reader's) — the first payload
    heard for that thing. Every other row (the words, the canvases, a folder wav's rows) is untouched; `meta.word` stays the
    canvas's own (the mind never learns from it). Pure: the input is never touched. Returns (rows', {word: word it now hears})."""
    first_payload: Dict[str, str] = {}
    for r in rows:
        m = _meta(r)
        if r.get("sense") == "ear-sound" and m.get("source") == "maker" and m.get("word") and m["word"] not in first_payload:
            first_payload[m["word"]] = r.get("payload")
    words = sorted(first_payload)
    perm: Dict[str, str] = {}
    if len(words) >= 2:
        rng = np.random.default_rng(int(seed))
        while True:
            p = [words[int(i)] for i in rng.permutation(len(words))]
            if all(a != b for a, b in zip(words, p)):
                perm = dict(zip(words, p)); break
    out = []
    for r in rows:
        m = _meta(r)
        if r.get("sense") == "ear-sound" and m.get("source") == "maker" and m.get("word") in perm:
            r2 = copy.deepcopy(r)
            r2["payload"] = first_payload[perm[m["word"]]]
            out.append(r2)
        else:
            out.append(r)
    return out, perm
