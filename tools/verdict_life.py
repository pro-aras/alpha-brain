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
