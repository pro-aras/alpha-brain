#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-22 19:2x +0400 — THE ONE LIFE's marks (PREREG §19; docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §6, L-1): PURE
# functions over the tape rows, the live journal rows and STATUS, imported by tools/verdict_g4.py. Each reads «not gradable» (graded False,
# with the reason) on a record whose life did not declare the line — the six closed 8 h records and life 3b are the control (L-1). Written
# test-first against builder D's landed shapes (creature/senses/game.py:213-220; creature/mind.py:_maybe_choose_act / _consume_ear_sound).
"""The ONE life's verdict marks: ACT (§19.5), SOUND (§19.10), SIZING (§19.11); the shuffled-act plant."""
from __future__ import annotations

import collections
import copy
from typing import Dict, Iterable, List, Optional


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
    the plant «zog» answered SURE ≥ 6 of 10; the hedge rate printed (the plan predicted < 10 %; L1's replay read 0.426 — a finding)."""
    gp = (plant or {}).get("graded"); gn = (null or {}).get("graded")
    hedge = ((seen or {}).get("Q1") or {}).get("hedge_rate")
    out: Dict[str, object] = {"plant_graded": gp, "null_graded": gn, "hedge_rate": hedge,
                              "bar": "null sure-bare ≤ 1/10 · null unsure+abstain ≥ 8/10 (a tie fails) · plant answered sure ≥ 6/10 · hedge rate printed, no bar (predicted < 0.10)"}
    if not answer_declared or not isinstance(gp, dict) or not isinstance(gn, dict):
        out.update(graded=False, **{"pass": None}, reason="not gradable: ANSWER not declared / no graded counts on the asks (a life before the graded answer)")
        return out
    n_null = sum(gn.values()) or 1; n_plant = sum(gp.values()) or 1
    null_sb = int(gn.get("sure_bare", 0)); null_soft = int(gn.get("unsure", 0)) + int(gn.get("abstain_with_resemblance", 0)) + int(gn.get("abstain", 0))
    plant_sure = int(gp.get("sure_bare", 0))
    out.update(null_sure_bare=null_sb, null_soft=null_soft, null_n=n_null, plant_sure=plant_sure, plant_n=n_plant,
               graded=True, **{"pass": (null_sb / n_null <= 0.1) and (null_soft / n_null >= 0.8) and (plant_sure / n_plant >= 0.6)},
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


def surprise_mark(journal: Iterable[dict], status: dict, canvases_per_window: int, surprise_declared: bool) -> Dict[str, object]:
    """PREREG §19.1 (builder B's shapes: `confirmed` on every eye moment row; STATUS glances_confirmed/glances_surprised): the
    confirmed share RISES within each window (second half > first half in ≥ 2/3 of the windows with ≥ 100 canvases) and DROPS at
    every window that brings new words (the first 100 canvases after the boundary under the last 100 before it). Windows are
    `canvases_per_window` canvases of glance-0 rows in tape order (the world's arrival period). Not gradable without the field."""
    canv = [j for j in journal if "moment" in j and j.get("glance") == 0]
    if not surprise_declared or not canv or not any("confirmed" in j for j in canv):
        return {"graded": False, "pass": None, "reason": "not gradable: SURPRISE not declared / no `confirmed` field on the moment rows",
                "bar": "share rises in ≥ 2/3 of windows · drops at every new-thing window"}
    W = max(1, int(canvases_per_window)); n = len(canv)
    windows = [canv[i:i + W] for i in range(0, n, W)]
    seen: set = set(); new_thing_windows: List[int] = []
    shares: List[dict] = []
    for w, rows in enumerate(windows):
        head = rows[:max(1, len(rows) // 20)]
        new = [j["word"] for j in head if j.get("word") and j["word"] not in seen]
        for j in rows:
            if j.get("word"): seen.add(j["word"])
        if w > 0 and new: new_thing_windows.append(w)
        h = len(rows) // 2
        s1 = sum(1 for j in rows[:h] if j.get("confirmed")) / max(1, h); s2 = sum(1 for j in rows[h:] if j.get("confirmed")) / max(1, len(rows) - h)
        shares.append({"window": w, "canvases": len(rows), "first_half": round(s1, 4), "second_half": round(s2, 4), "new_words": new[:5]})
    full = [s for s in shares if s["canvases"] >= 100]
    rising = sum(1 for s in full if s["second_half"] > s["first_half"])
    drops = {}
    for w in new_thing_windows:
        before = windows[w - 1][-100:]; after = windows[w][:100]
        sb = sum(1 for j in before if j.get("confirmed")) / max(1, len(before)); sa = sum(1 for j in after if j.get("confirmed")) / max(1, len(after))
        drops[w] = {"before": round(sb, 4), "after": round(sa, 4), "dropped": sa < sb}
    ok = bool(full) and rising * 3 >= 2 * len(full) and all(d["dropped"] for d in drops.values())
    return {"graded": True, "pass": ok, "windows": shares, "windows_rising": rising, "windows_full": len(full), "new_thing_windows": new_thing_windows,
            "drops_at_new_thing_windows": drops, "overall_share": round(sum(1 for j in canv if j.get("confirmed")) / n, 4),
            "status_confirmed": status.get("glances_confirmed", "not recorded"), "status_surprised": status.get("glances_surprised", "not recorded"),
            "reason": "graded (§19.1)", "bar": "share rises in ≥ 2/3 of windows · drops at every new-thing window"}


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


def sizing_mark(status: dict, journal: Iterable[dict], prediction: Optional[float], plant_word: str = "zog") -> Dict[str, object]:
    """PREREG §19.11: sight born by 24 h within [0.5×, 1.5×] of the pre-flight's prediction; births_refused_nmax 0; the plant birthed ≥ 1
    sight cell. The per-hour sight-births SERIES is on the record (#233's instrument). Not gradable without a prediction or an older body."""
    per_hour: "collections.OrderedDict[str, int]" = collections.OrderedDict(); plant_births = 0; plant_shown = 0
    for j in journal:
        if "moment" in j:
            h = (j.get("when") or "")[:13]
            n = sum(1 for b in (j.get("births") or []) if b and b[0] == "sight")
            per_hour[h] = per_hour.get(h, 0) + n
            if j.get("word") == plant_word:
                plant_shown += 1; plant_births += n
    born = status.get("sight_born"); nmax = status.get("sight_nmax"); refused = status.get("births_refused_nmax")
    out: Dict[str, object] = {"sight_born": born, "sight_nmax": nmax, "births_refused_nmax": refused, "prediction": prediction,
                              "series_sight_births_per_hour": list(per_hour.values()), "plant_shown_moments": plant_shown, "plant_sight_births": plant_births,
                              "bar": "born within [0.5×, 1.5×] of the prediction · refused at NMAX 0 · the plant birthed ≥ 1 sight cell"}
    if prediction is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight)")
    elif not isinstance(born, int) or not isinstance(nmax, int):
        out.update(graded=False, **{"pass": None}, reason="not gradable: sight_born / sight_nmax not on STATUS (an older body)")
    else:
        band = 0.5 * prediction <= born <= 1.5 * prediction
        out.update(graded=True, **{"pass": band and int(refused or 0) == 0 and plant_births >= 1},
                   reason=f"graded (§19.11): band {'ok' if band else 'MISSED'}; refused {refused}; plant births {plant_births}")
    return out
