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
from typing import Dict, Iterable, List, Optional, Sequence, Tuple   # edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:26 +0400 — Sequence for the v3.5 marks

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


# ============================================================================ A4L-ANSWER (A4-LADDER-PREREG §2.2)
# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:11 +0400 — A1/A2, test-first against the
# self_exam.py/questions.py shapes this rung lands (#171/#173): the sitter's own exam dicts (each carrying
# ask_seen_words/ask_all_words/ask_seen_words_old_law/ask_all_words_old_law/lit_counts_seen — task 3) and the
# reader's one-off plant-shaped asks (genome/questions.py:ask_plant_glances) for the null plant "vex" on the
# final snapshot, both laws (task 5).
def _two_clauses(graded: dict) -> Optional[bool]:
    """The shared A1 bar (grade_mark's own null-clause math, generalised to any n): sure-bare <= 1/10 of the
    asked AND unsure+abstain_with_resemblance+abstain >= 8/10 -- both bounds strict, so a tie (neither
    clearly clears nor clearly fails, e.g. a 5/10 split under an older ">50%" phrasing) fails by
    construction. None when there is nothing to grade (n == 0)."""
    n = sum(int(v) for v in (graded or {}).values())
    if not n:
        return None
    sb = int((graded or {}).get("sure_bare", 0))
    soft = n - sb
    return (sb / n <= 0.1) and (soft / n >= 0.8)


def _q5_graded(ask_result: Optional[dict], thing: str) -> Optional[dict]:
    q5 = ((ask_result or {}).get("Q5") or {}).get(thing)
    return (q5 or {}).get("graded") if isinstance(q5, dict) else None


def answer_null_mark(exams: Iterable[dict], vex_new: Optional[dict], vex_old: Optional[dict],
                     answer_majority_declared: bool, spiral_key: str = "spiral") -> Dict[str, object]:
    """A4-LADDER-PREREG §2.2 A1 NULL: the exam files' Q5 spiral at EVERY exam from hour 1 (sure-bare <=
    1/10 AND resembles+unsure+abstain >= 8/10; a tie fails, `_two_clauses`) + the reader's one-off `vex`
    asks (genome/questions.py:ask_plant_glances on THING_NULL) on the rung's final snapshot, the SAME two
    clauses. `exams`: the sitter's own exam dicts, in order (self_exam.py's `out`, task 3 — Q5 is read off
    `ask_all_words` since it is invariant to which `things` list Q1-4 used). `vex_new`/`vex_old`: the
    reader's `ask_plant_glances(..., world.THING_NULL, ..., majority=None/False)` return dicts (or None
    before alpha4-1 closes — A3/A1's vex clause is not gradable that early, printed as such). The old-law
    reading (spiral per-exam, vex) is printed beside each, never graded (A1's own bar is the new law's)."""
    bar = ('spiral: at every exam from hour 1, sure-bare <= 1/10 AND resembles+unsure+abstain >= 8/10 (a tie fails) · '
           'vex (the reader, final snapshot): the same two clauses · the old-law reading printed beside each, ungraded')
    out: Dict[str, object] = {"bar": bar}
    if not answer_majority_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: ANSWER's majority clause not declared on this line")
        return out
    per_exam = []
    for ex in exams:
        g_new = _q5_graded(ex.get("ask_all_words"), spiral_key)
        g_old = _q5_graded(ex.get("ask_all_words_old_law"), spiral_key)
        if g_new is None:
            continue
        n = sum(int(v) for v in g_new.values())
        per_exam.append({"at": ex.get("at"), "n": n, "sure_bare": int(g_new.get("sure_bare", 0)),
                          "pass": _two_clauses(g_new), "old_law_sure_bare": (int(g_old.get("sure_bare", 0)) if g_old else None)})
    if not per_exam:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the exam file carries no Q5"); return out
    spiral_pass = all(e["pass"] for e in per_exam)
    vex_graded_new = (vex_new or {}).get("graded")
    vex_graded_old = (vex_old or {}).get("graded")
    vex_pass = _two_clauses(vex_graded_new) if isinstance(vex_graded_new, dict) else None
    out.update(spiral_per_exam=per_exam, spiral_pass=spiral_pass,
               vex_graded=vex_graded_new, vex_old_law_graded=vex_graded_old, vex_pass=vex_pass)
    if vex_pass is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no vex reading yet (the reader asks it on the rung's final snapshot)")
        return out
    out.update(graded=True, **{"pass": bool(spiral_pass and vex_pass)}, reason="graded (§2.2 A1)")
    return out


def answer_seen_mark(exams: Iterable[dict], answer_majority_declared: bool, glances_needed: int = 3,
                     ceiling_share: float = 0.95, min_delta: float = -0.01, min_q1: float = 0.95) -> Dict[str, object]:
    """A4-LADDER-PREREG §2.2 A2 SEEN (the regression bar, #231 (6)): at every exam WHERE ITS OWN CEILING
    HOLDS (the sitter's `lit_counts_seen` share of seen canvases lighting >= `glances_needed` of the
    glances asked, >= `ceiling_share`) -- Q1 on seen words under the new law minus Q1 under the old law,
    read off the SAME snapshot by the sitter (task 3) >= `min_delta`; Q1 (new) >= `min_q1`. An early
    organism may light fewer glances per canvas (measured, task 0: 74 % at ~1,500 cells vs 100 % at
    ~4,000) — a reason the CEILING gives, never the law — so every exam prints its own share/delta and
    only the ones whose ceiling clears are graded; not gradable when none ever does."""
    bar = (f"at every exam whose own ceiling (share of seen canvases lighting >= {glances_needed} glances) reaches "
           f">= {ceiling_share:.0%}: Q1(new) - Q1(old) >= {min_delta} AND Q1(new) >= {min_q1}; earlier exams print their own share/delta, ungraded")
    out: Dict[str, object] = {"bar": bar}
    if not answer_majority_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: ANSWER's majority clause not declared on this line")
        return out
    per_exam = []
    for ex in exams:
        counts = ex.get("lit_counts_seen") or {}
        total = sum(int(v) for v in counts.values())
        share = (sum(int(v) for k, v in counts.items() if int(k) >= glances_needed) / total) if total else None
        q1_new = ((ex.get("ask_seen_words") or {}).get("Q1") or {}).get("acc")
        q1_old = ((ex.get("ask_seen_words_old_law") or {}).get("Q1") or {}).get("acc")
        delta = (q1_new - q1_old) if (q1_new is not None and q1_old is not None) else None
        per_exam.append({"at": ex.get("at"), "share": share, "q1_new": q1_new, "q1_old": q1_old, "delta": delta,
                          "ceiling_holds": (share is not None and share >= ceiling_share)})
    if not per_exam:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no exams with a lit_counts_seen reading"); return out
    out["per_exam"] = per_exam
    graded_rows = [e for e in per_exam if e["ceiling_holds"]]
    if not graded_rows:
        out.update(graded=False, **{"pass": None},
                   reason=f"not gradable: no exam's own ceiling reaches {ceiling_share:.0%} yet (an early-organism finding, #231 (5) — printed per_exam)")
        return out
    ok = all((e["delta"] is not None and e["delta"] >= min_delta and e["q1_new"] is not None and e["q1_new"] >= min_q1) for e in graded_rows)
    out.update(graded=True, **{"pass": bool(ok)}, reason="graded (§2.2 A2)")
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
        if "moment" in j and "kind" not in j:      # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:40 +0400 — BRAIN-IN-BODY: an `answer`/`brain` row is no canvas row
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


# edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md §2.4
# (docs/briefs/A4L-DROP.md task 5): D1's mark. drop_mark's own 5-parameter signature is the brief's own
# words and stays TAPE-FREE (pure); window membership — needed for D1's "retention pair across window 2"
# clause — is resolved SEPARATELY by annotate_windows(exams, tape) (the caller's own job, mirroring
# tools/verdict_g4.py's window_of()/§15 pairing exactly, tape and all) and handed in as an OPTIONAL
# "window" key already sitting on each exam dict; drop_mark only ever READS that key, never derives it.
def annotate_windows(exams: Iterable[dict], tape: Iterable[dict]) -> List[dict]:
    """Each exam dict gets a "window" key (int, or None when unresolvable) — mirrors tools/verdict_g4.py's
    own window_of() (§15's retention pairing) to the letter: walk BACK from the exam's own
    `snapshot_last_seq` to the nearest MAKER row (a moment id shaped "w<NNNN>i...") and read its window
    number from the id itself. Never mutates an input dict (returns fresh copies, `exams`' own tape-free
    contract preserved for the caller) — a pure function over already-loaded rows, no I/O of its own."""
    seq_at: Dict[object, dict] = {r["seq"]: r for r in tape}
    out: List[dict] = []
    for ex in exams:
        s = ex.get("snapshot_last_seq") or 0
        while s > 0 and (s not in seq_at or not str((seq_at[s].get("meta") or {}).get("moment", "")).startswith("w")):
            s -= 1
        window = int(seq_at[s]["meta"]["moment"][1:5]) if s in seq_at else None
        out.append({**ex, "window": window})
    return out


def drop_mark(twin_floor_exams: List[dict], twin_drop_exams: List[dict], timings_floor: List[dict],
              timings_drop: List[dict], declared: Optional[dict]) -> Dict[str, object]:
    """A4-LADDER-PREREG.md §2.4, D1 WHAT THE EXAM LOSES (the tape twin, exact): alpha4-1's 0-8 h cut
    replayed under DROP and under the FLOOR, the self-exam sat every 500 canvases at the SAME rows —
    `twin_floor_exams`/`twin_drop_exams` are the two ordered exam-JSON lists (tools/self_exam.py's own
    shape, `ask_seen_words.Q1..Q4.acc`, `.Q1.hedge_rate`, `.Q5`), matched by POSITION: both twins replay
    the identical tape at the identical --exam-every N cadence, so exam i lands at the same eye-row
    boundary in both (DROP never skips or adds a tape row, only within-canvas LEARNING) — a
    `snapshot_last_seq` mismatch at the same index is therefore itself a defect, not a reading, and fails
    the mark (`mismatched_snapshot_rows`). `declared` is the DROP genome's own `genome.declared["SURPRISE"]`
    sub-dict. The pre-registered CLAIM ("the drop costs nothing"): |ΔQ1| <= 0.01 AT EVERY EXAM AND
    Δretention >= -1 pp across window 2 — retention read from a PRE-ANNOTATED "window" key
    (annotate_windows(), above); when no window-2 pair exists on this cut (the hour-1 fixture: only
    window 0, arrivals are hours apart) retention reads NOT READABLE and the claim is judged on Q1 alone
    (A2's own "graded only where its ceiling holds" precedent, sizing_mark/hands_mark's own printed-not-
    gated fields) — never silently assumed to pass. D4 (ms saved on the same rows) is printed, no bar.
    «not gradable» when the clause is undeclared or fewer than 2 exams exist on EITHER twin's cut."""
    bar = ("|ΔQ1| ≤ 0.01 at every exam AND Δretention ≥ −1 pp across window 2 (the pre-registered claim, "
           "'the drop costs nothing'); retention graded only where a window-2 pair exists on this cut; "
           "D4 (ms saved) printed, no bar")
    out: Dict[str, object] = {"bar": bar}
    if declared is None or declared.get("drop") != "confirmed":
        out.update(graded=False, **{"pass": None}, reason="not gradable: SURPRISE 'drop confirmed' undeclared")
        return out
    n = min(len(twin_floor_exams), len(twin_drop_exams))
    if n < 2:
        out.update(graded=False, **{"pass": None},
                   reason=f"not gradable: {len(twin_floor_exams)} floor / {len(twin_drop_exams)} drop exams on the cut (need >= 2 each)")
        return out

    def q(ex: dict, key: str) -> Optional[float]:
        return ((ex.get("ask_seen_words") or {}).get(key) or {}).get("acc")

    def hedge(ex: dict) -> Optional[float]:
        return ((ex.get("ask_seen_words") or {}).get("Q1") or {}).get("hedge_rate")

    def q5(ex: dict) -> Dict[str, object]:
        d = (ex.get("ask_seen_words") or {}).get("Q5") or {}
        return {name: v.get("abstain_rate") for name, v in d.items()}

    table: List[Dict[str, object]] = []
    max_abs_dq1 = 0.0
    mismatched_rows: List[Tuple[int, object, object]] = []
    for i in range(n):
        ef, ed = twin_floor_exams[i], twin_drop_exams[i]
        if ef.get("snapshot_last_seq") != ed.get("snapshot_last_seq"):
            mismatched_rows.append((i, ef.get("snapshot_last_seq"), ed.get("snapshot_last_seq")))
        row: Dict[str, object] = {"i": i, "snapshot_last_seq_floor": ef.get("snapshot_last_seq"), "snapshot_last_seq_drop": ed.get("snapshot_last_seq")}
        for key in ("Q1", "Q2", "Q3", "Q4"):
            fv, dv = q(ef, key), q(ed, key)
            row[key] = {"floor": fv, "drop": dv, "delta": (round(dv - fv, 6) if (fv is not None and dv is not None) else None)}
        fh, dh = hedge(ef), hedge(ed)
        row["hedge"] = {"floor": fh, "drop": dh, "delta": (round(dh - fh, 6) if (fh is not None and dh is not None) else None)}
        row["Q5"] = {"floor": q5(ef), "drop": q5(ed)}
        dq1 = row["Q1"]["delta"]
        if dq1 is not None:
            max_abs_dq1 = max(max_abs_dq1, abs(dq1))
        table.append(row)

    def retention_change_pp(exams: List[dict]) -> Optional[float]:
        # §15's own pair: the LAST exam of window 1 (before arrival 2) vs the LAST exam of window 2, read
        # as a CHANGE (last - before) — negative = accuracy fell (retention lost), positive = it rose.
        by_w: Dict[int, List[dict]] = {}
        for ex in exams:
            w = ex.get("window")
            if w is not None:
                by_w.setdefault(int(w), []).append(ex)
        if 1 not in by_w or 2 not in by_w or not by_w[1] or not by_w[2]:
            return None
        b, l = q(by_w[1][-1], "Q1"), q(by_w[2][-1], "Q1")
        return None if (b is None or l is None) else round(100.0 * (l - b), 4)

    floor_retention_change_pp = retention_change_pp(twin_floor_exams)
    drop_retention_change_pp = retention_change_pp(twin_drop_exams)
    retention_readable = floor_retention_change_pp is not None and drop_retention_change_pp is not None
    # Δretention = DROP's own change minus FLOOR's own change — negative means DROP retained WORSE than
    # FLOOR did over the same window (the quantity A4-LADDER-PREREG §2.4's bar reads: "Δretention >= -1 pp").
    delta_retention_pp = round(drop_retention_change_pp - floor_retention_change_pp, 4) if retention_readable else None
    retention_claim = (delta_retention_pp is not None and delta_retention_pp >= -1.0) if retention_readable else None

    def mean_ms_per_canvas(timings: Iterable[dict]) -> Optional[float]:
        # "per-canvas" == per EYE row (a canvas). timings.jsonl (creature/replay.py --timings) carries
        # EVERY tape row's own consume time -- ear/outcome/smell/body/touch/sit rows mixed in beside the
        # eye ones -- so a plain mean over every row silently dilutes the canvas cost by however many
        # cheap non-eye rows the tape also carries (measured on the hour-1 fixture: 23.1 ms mixed vs
        # 58.2 ms eye-only -- a 2.5x understatement, #213's class: the wrong denominator still looks like
        # a real number).
        vals = [float(r["ms"]) for r in timings if isinstance(r, dict) and r.get("sense") == "eye" and "ms" in r]
        return (sum(vals) / len(vals)) if vals else None

    floor_ms, drop_ms = mean_ms_per_canvas(timings_floor), mean_ms_per_canvas(timings_drop)
    ms_saved_pct = (round(100.0 * (floor_ms - drop_ms) / floor_ms, 2) if (floor_ms and drop_ms is not None and floor_ms > 0) else None)

    # the per-exam WINDOWED reading (task 4's own words: "at every exam row print ... the per-canvas ms
    # of both") -- the canvases strictly between the PREVIOUS exam's own snapshot_last_seq and this
    # one's, the SAME seq range on both twins by construction. Far less confounded than the one
    # whole-tape mean above: per-canvas cost is DOMINATED by the organism's own size (state_hash is
    # quadratic in cells x words, M1), which grows across the tape, so an aggregate mean conflates "the
    # drop's own per-glance saving" with "which segment of the growth curve the mean happened to average
    # over" -- measured on the hour-1 fixture, the LAST window (near-identical final cell counts, 1334 vs
    # 1351 sight cells) read floor and drop at the identical 93.67 ms/canvas; the whole-tape means read
    # -5.5% (DROP slower) purely from the growth-curve shape, not from either road's own per-glance cost.
    def eye_rows_sorted(timings: Iterable[dict]) -> List[dict]:
        return sorted((r for r in timings if isinstance(r, dict) and r.get("sense") == "eye" and "ms" in r and "seq" in r),
                       key=lambda r: r["seq"])

    def window_mean(rows: List[dict], lo_excl: object, hi_incl: object) -> Optional[float]:
        if hi_incl is None:
            return None
        vals = [r["ms"] for r in rows if (lo_excl is None or r["seq"] > lo_excl) and r["seq"] <= hi_incl]
        return (sum(vals) / len(vals)) if vals else None

    floor_eye, drop_eye = eye_rows_sorted(timings_floor), eye_rows_sorted(timings_drop)
    prev_seq: Optional[object] = None
    for row in table:
        hi = row.get("snapshot_last_seq_floor")   # == snapshot_last_seq_drop when not mismatched (checked above)
        row["ms_window"] = {"floor": window_mean(floor_eye, prev_seq, hi), "drop": window_mean(drop_eye, prev_seq, hi)}
        if hi is not None:
            prev_seq = hi

    q1_claim = max_abs_dq1 <= 0.01
    # the claim is judged on what IS readable: retention only counts against the verdict once it HAS a
    # window-2 pair to read (never silently assumed true OR false while unreadable — A2's own law).
    overall_pass = bool(q1_claim and (retention_claim if retention_readable else True) and not mismatched_rows)
    out.update(
        table=table, n_exams=n, max_abs_delta_q1=round(max_abs_dq1, 4), claim_q1=q1_claim,
        retention={"readable": retention_readable, "floor_change_pp": floor_retention_change_pp, "drop_change_pp": drop_retention_change_pp,
                   "delta_pp": delta_retention_pp, "pass": retention_claim,
                   "reason": "graded" if retention_readable else "not readable: no window-1-then-window-2 pair on this cut"},
        mismatched_snapshot_rows=mismatched_rows,
        d4_ms_saved_pct=ms_saved_pct, floor_ms_per_canvas=(round(floor_ms, 3) if floor_ms is not None else None),
        drop_ms_per_canvas=(round(drop_ms, 3) if drop_ms is not None else None),
        graded=True, **{"pass": overall_pass},
        reason=("graded (§2.4 D1): the claim holds" if overall_pass else "graded (§2.4 D1): the claim FAILS")
              + ("" if not mismatched_rows else f"; {len(mismatched_rows)} exam(s) landed at different rows between twins — a defect, not a reading"),
    )
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


# ============================================================================ A4-LADDER-PREREG §3.4: the LANG rung's marks
# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:47 +0400 — A4L-LANG task 7 (docs/briefs/A4L-LANG.md): L1-L9
# as PURE functions over the shapes LANDED (#171/#173): creature/mind.py:_consume_chat's chat/out/<id>.json and its journal
# `say` row of kind "chat"; tools/chat_seat.py's chat/truth/<id>.json; creature/senses/chat.py's `chat` / kind-chat `grade`
# rows on the tape. Every mark reads «not gradable» on a record whose life did not declare CHAT (the hour-1 fixture, every
# closed record before tonight — the L-1 control). The READ-ONLY law's replay twin (--blind chat, creature/replay.py) is
# computed OUTSIDE this module (tools/verdict_g4.py's `blind-chat` worker) and handed in as `blind_journal`.
CHAT_NULL_THINGS = ("spiral", "vex")
# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:52 +0400 — L5's pre-registered ceiling, measured BEFORE the life (task 0 (b)) on
# alpha4-1's 10:54 snapshot copy: the share of two-thing canvases where a located glance lands on the asked thing AND its
# single-glance recall is the asked word. tools/chat_ceiling.py on the seat's OWN where-canvases (plan_slot k = 6 + 7i, 50):
# 39/50 = 0.78 (the POINT rule itself also 39/50); the builder's first probe (scratch, one rng(3) stream over the 16): 42/50 =
# 0.84. Both >= 0.5 -> L5 is gradable; the seat-road number is the one the life's canvases are drawn from, so it is the bar's.
CHAT_POINTING_CEILING_PRELIFE = 0.78
CHAT_MARKS = ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9")


def _chat_dt(s: str):
    from datetime import datetime, timezone
    s = str(s).replace("Z", "+00:00")
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _chat_said(o: dict) -> List[str]:
    return [str(w) for w in (o.get("answer") or [])]


def _chat_q1_nearest(exams: Sequence[dict], when) -> Optional[float]:
    best = None
    for e in exams or []:
        q1 = (((e.get("ask_seen_words") or {}).get("Q1") or {}).get("acc"))
        if q1 is None or not e.get("at"):
            continue
        d = abs((_chat_dt(e["at"]) - when).total_seconds())
        if best is None or d < best[0]:
            best = (d, float(q1))
    return None if best is None else best[1]


def _chat_tape_instants(tape: List[dict]) -> List[Tuple[int, List[str]]]:
    """(eye seq, words heard on its moment in publish order) for every eye row — pending_words' own rule, rebuilt from
    the tape alone (never the mind's FAST ring): the independent witness of L7's CITED clause."""
    words: Dict[str, List[str]] = {}
    out: List[Tuple[int, List[str]]] = []
    for r in tape:
        m = _meta(r)
        if r.get("sense") == "ear" and m.get("word"):
            words.setdefault(str(m.get("moment")), []).append(str(m["word"]))
        elif r.get("sense") == "eye":
            out.append((int(r["seq"]), words.pop(str(m.get("moment")), [])))
    return out


def chat_marks(chat_out: Dict[str, dict], chat_truth: Dict[str, dict], tape: Iterable[dict], journal: Iterable[dict],
               exams: Sequence[dict], declared: dict, blind_journal: Optional[List[dict]] = None,
               pointing_ceiling: Optional[float] = None, born: Optional[str] = None, seed: int = 20260923,
               permutations: int = 200, tape_canvases: Optional[Sequence[np.ndarray]] = None,
               chat_pics: Optional[Dict[str, np.ndarray]] = None, min_answered: int = 20, glance: int = 32) -> Dict[str, object]:
    """A4-LADDER-PREREG §3.4 L1-L9, exactly: L1 the read-only law (every say row's hash_before == hash_after AND the blind-chat
    twin equal to the live journal's non-chat rows field for field including `hash`); L2 what-is precision >= max(0.80, Q1 at
    the nearest exam - 0.05) over answered, abstention on seen things <= 0.10, the shuffled-question twin's p95 <= 0.20
    (`permutations` re-judgings, `seed` — the reader's own); L3 yes-no the same precision bar and ECHO <= 0.10 (the echo twin —
    content := the lure — printed: 0.5 by construction); L4 which precision >= 0.85; L5 where POINT >= ceiling - 0.15, graded
    only when the pre-life pointing ceiling >= 0.5; L6 from hour 4 >= 0.5 of the correct what-is + yes-no + which answers
    carry >= 3 words (the per-hour length table and the longest printed); L7 100 % of said contents grounded and 100 % of
    links/pivots cited — re-checked on the TAPE; L8 the seat's grades printed (no bar); L9 the null in words printed. A
    family under `min_answered` answered chats reads «not gradable». The canvases' disjointness from the tape is checked
    when both are handed in (world.assert_disjoint_canvas + its planted control)."""
    from creature.senses.chat import render_answer
    tape = list(tape); journal = list(journal)
    decl = (declared or {}).get("CHAT")
    if decl is None:
        out0: Dict[str, object] = {k: {"graded": False, "pass": None, "reason": "not gradable: CHAT not declared on this life"} for k in CHAT_MARKS}
        out0["disjoint"] = {"checked": 0, "ok": None, "reason": "not checked: CHAT not declared"}
        return out0
    adj_bar, fol_bar = int(decl["links_adjacent"]), int(decl["pivot_distinct"])
    t0 = _chat_dt(born) if born else (_chat_dt(tape[0]["at"]) if tape else None)

    def hours(o: dict) -> Optional[float]:
        return None if (t0 is None or not o.get("at")) else (_chat_dt(o["at"]) - t0).total_seconds() / 3600.0

    pairs = [(chat_out[i], chat_truth[i]) for i in sorted(chat_out) if i in chat_truth]
    fam = lambda f: [(o, t) for o, t in pairs if t.get("family") == f]
    M: Dict[str, object] = {}

    # ---- L1 READ-ONLY
    from creature import replay as _replay
    says = [j for j in journal if _replay.is_chat_journal_row(j) and isinstance(j.get("say"), dict)]
    heq = sum(1 for j in says if j["say"].get("hash_before") == j["say"].get("hash_after"))
    non_chat = [j for j in journal if not _replay.is_chat_journal_row(j)]
    L1: Dict[str, object] = {"say_rows": len(says), "hash_equal": heq, "live_non_chat_rows": len(non_chat),
                             "bar": "hash_before == hash_after on 100 % of say rows · the blind-chat twin reproduces every non-chat row INCLUDING hash"}
    if not says:
        L1.update(graded=False, **{"pass": None}, reason="not gradable: no chat on this record")
    else:
        diff = None if blind_journal is None else _replay.compare(list(blind_journal), non_chat)
        L1["twin_rows"] = None if blind_journal is None else len(list(blind_journal))
        L1["twin_first_difference"] = (list(diff) if diff else None)
        twin_ok = blind_journal is not None and diff is None
        L1.update(graded=True, **{"pass": heq == len(says) and twin_ok},
                  reason=("graded (§3.4 L1)" if blind_journal is not None else "graded (§3.4 L1); the blind-chat twin was not run — that clause FAILS"))
    M["L1"] = L1

    # ---- shared: the precision family bars
    def precision_block(items: List[Tuple[dict, dict]], label: str) -> Dict[str, object]:
        ans = [(o, t) for o, t in items if _chat_said(o)]
        correct = sum(1 for o, t in ans if o.get("content") == t.get("thing"))
        q1s = [q for q in (_chat_q1_nearest(exams, _chat_dt(o["at"])) for o, _t in ans if o.get("at")) if q is not None]
        q1 = (sum(q1s) / len(q1s)) if q1s else None
        return {"items": len(items), "answered": len(ans), "correct": correct,
                "precision": (round(correct / len(ans), 4) if ans else None), "q1_nearest_mean": (round(q1, 4) if q1 is not None else None),
                "bar_precision": round(max(0.80, (q1 - 0.05) if q1 is not None else 0.80), 4), "_ans": ans}

    # ---- L2 WHAT-IS (the null things excluded; printed in L9)
    b = precision_block([(o, t) for o, t in fam("what-is") if t.get("thing") not in CHAT_NULL_THINGS], "what-is")
    ans = b.pop("_ans")
    abst = round((b["items"] - b["answered"]) / b["items"], 4) if b["items"] else None
    p95 = None
    if ans:
        rng = np.random.default_rng(seed); contents = [o.get("content") for o, _t in ans]; truths = [t.get("thing") for _o, t in ans]
        precs = sorted(sum(1 for c, tt in zip(contents, [truths[i] for i in rng.permutation(len(truths))]) if c == tt) / len(ans) for _ in range(permutations))
        p95 = round(precs[max(0, int(0.95 * len(precs)) - 1)], 4)
    L2 = {**b, "abstention_seen": abst, "shuffled_p95": p95, "chance": round(1.0 / 16, 4),
          "bar": "precision >= max(0.80, Q1 at the nearest exam - 0.05) · abstention on seen things <= 0.10 · the shuffled-question twin's p95 <= 0.20"}
    if b["answered"] < min_answered:
        L2.update(graded=False, **{"pass": None}, reason=f"not gradable: {b['answered']} what-is answered < {min_answered}")
    else:
        L2.update(graded=True, **{"pass": bool(b["precision"] >= b["bar_precision"] and abst <= 0.10 and p95 <= 0.20)}, reason="graded (§3.4 L2)")
    M["L2"] = L2

    # ---- L3 YES-NO (the lure)
    b = precision_block(fam("yes-no"), "yes-no")
    ans = b.pop("_ans")
    wrong = [(o, t) for o, t in ans if t.get("lure") != t.get("thing")]
    echo = sum(1 for o, t in wrong if o.get("content") == t.get("lure"))
    twin_prec = (round(sum(1 for _o, t in ans if t.get("lure") == t.get("thing")) / len(ans), 4) if ans else None)
    L3 = {**b, "wrong_lures_answered": len(wrong), "echo": echo, "echo_rate": (round(echo / len(wrong), 4) if wrong else None),
          "echo_twin_precision": twin_prec, "bar": "precision >= max(0.80, Q1 - 0.05) · ECHO <= 0.10 (the echo twin — content := the lure — reads 0.5 by construction)"}
    if b["answered"] < min_answered:
        L3.update(graded=False, **{"pass": None}, reason=f"not gradable: {b['answered']} yes-no answered < {min_answered}")
    else:
        L3.update(graded=True, **{"pass": bool(b["precision"] >= b["bar_precision"] and (L3["echo_rate"] or 0.0) <= 0.10)}, reason="graded (§3.4 L3)")
    M["L3"] = L3

    # ---- L4 WHICH
    b = precision_block(fam("which"), "which"); b.pop("_ans")
    L4 = {**b, "chance": 0.5, "bar": "precision >= 0.85"}
    if b["answered"] < min_answered:
        L4.update(graded=False, **{"pass": None}, reason=f"not gradable: {b['answered']} which answered < {min_answered}")
    else:
        L4.update(graded=True, **{"pass": bool(b["precision"] >= 0.85)}, reason="graded (§3.4 L4)")
    M["L4"] = L4

    # ---- L5 WHERE (the POINT)
    items = fam("where"); hits = 0
    for o, t in items:
        pt = o.get("point"); box = (t.get("bboxes") or {}).get(t.get("thing"))
        if pt and box and pt.get("window"):
            cy, cx = int(pt["window"][0]) + glance / 2.0, int(pt["window"][1]) + glance / 2.0
            hits += int(box[0] <= cy < box[0] + box[2] and box[1] <= cx < box[1] + box[3])
    rate = round(hits / len(items), 4) if items else None
    L5: Dict[str, object] = {"items": len(items), "pointed_inside": hits, "point_rate": rate, "pointing_ceiling": pointing_ceiling,
                             "bar": "graded only if the pre-life pointing ceiling >= 0.5; then POINT >= ceiling - 0.15 (the pointed window's centre inside the asked thing's bbox)"}
    if pointing_ceiling is None:
        L5.update(graded=False, **{"pass": None}, reason="not gradable: no pointing ceiling on the record (task 0 (b) measured it pre-life)")
    elif pointing_ceiling < 0.5:
        L5.update(graded=False, **{"pass": None}, reason=f"not gradable: the pointing ceiling is {pointing_ceiling}")
    elif not items:
        L5.update(graded=False, **{"pass": None}, reason="not gradable: no where-question on this record")
    else:
        L5["bar"] = round(pointing_ceiling - 0.15, 4)
        L5.update(graded=True, **{"pass": bool(rate >= pointing_ceiling - 0.15)}, reason=f"graded (§3.4 L5): the pointing ceiling {pointing_ceiling}")
    M["L5"] = L5

    # ---- L6 LENGTH
    said_all = [(o, t) for o, t in pairs if _chat_said(o)]
    per_hour: Dict[int, Dict[int, int]] = {}
    for o, _t in said_all:
        h = hours(o)
        if h is not None:
            d = per_hour.setdefault(int(h), {}); n = len(_chat_said(o)); d[n] = d.get(n, 0) + 1
    late_correct = [(o, t) for o, t in said_all if t.get("family") in ("what-is", "yes-no", "which") and t.get("thing") not in CHAT_NULL_THINGS
                    and o.get("content") == t.get("thing") and (hours(o) or 0.0) >= 4.0]
    three = sum(1 for o, _t in late_correct if len(_chat_said(o)) >= 3)
    any_cand = any(int(o.get("candidates_n") or 0) > 0 for o, _t in pairs)
    L6: Dict[str, object] = {"correct_from_hour_4": len(late_correct), "with_3_words": three,
                             "share_3plus": (round(three / len(late_correct), 4) if late_correct else None),
                             "longest": max((len(_chat_said(o)) for o, _t in said_all), default=0),
                             "longest_said": max((" ".join(_chat_said(o)) for o, _t in said_all), key=len, default=None),
                             "per_hour": {h: per_hour[h] for h in sorted(per_hour)},
                             "bar": "from hour 4, >= 0.5 of the CORRECT what-is + yes-no + which answers carry >= 3 words (content-only control: 1 word by construction)"}
    if not any_cand:
        L6.update(graded=False, **{"pass": None}, reason="not gradable: the rung's frames never yielded a pivot-ending candidate with a question word")
    elif not late_correct:
        L6.update(graded=False, **{"pass": None}, reason="not gradable: no correct answer from hour 4")
    else:
        L6.update(graded=True, **{"pass": bool(three / len(late_correct) >= 0.5)}, reason="graded (§3.4 L6)")
    M["L6"] = L6

    # ---- L7 GROUNDED + CITED (the record, then the TAPE)
    said = [o for o, _t in said_all]
    ungrounded = [o["id"] for o in said if not ((o.get("grounded") or {}).get("ok") and ((o.get("grounded") or {}).get("edge") or [0, 0, 0])[2] > 0)]
    short_rec = [f"{l[0]} {l[1]} @ {o['id']}: {l[2]}" for o in said for l in (o.get("links") or []) if int(l[2]) < adj_bar]
    piv_short = [o["id"] for o in said if len(_chat_said(o)) > 1 and o.get("form") and int(o.get("pivot_followers") or 0) < fol_bar]
    inst = _chat_tape_instants(tape)
    import bisect
    adj_seqs: Dict[Tuple[str, str], List[int]] = {}; foll_first: Dict[str, Dict[str, int]] = {}
    for s, ws in inst:
        for a_, b_ in set(zip(ws, ws[1:])):
            adj_seqs.setdefault((a_, b_), []).append(s)
        for a_, b_ in zip(ws, ws[1:]):
            foll_first.setdefault(a_, {}).setdefault(b_, s)
    tape_short: List[str] = []; min_adj = None; min_fol = None
    for o in said:
        cs = int(o.get("seq") or 0)
        for l in (o.get("links") or []):
            n = bisect.bisect_left(adj_seqs.get((str(l[0]), str(l[1])), []), cs)
            min_adj = n if min_adj is None else min(min_adj, n)
            if n < adj_bar:
                tape_short.append(f"{l[0]} {l[1]} @ {o['id']}: {n}")
        if o.get("form") and o.get("pivot"):
            nf = sum(1 for s in foll_first.get(str(o["pivot"]), {}).values() if s < cs)
            min_fol = nf if min_fol is None else min(min_fol, nf)
            if nf < fol_bar:
                tape_short.append(f"pivot {o['pivot']} @ {o['id']}: {nf} followers")
    L7 = {"said": len(said), "ungrounded": ungrounded, "record_short_links": short_rec, "record_short_pivots": piv_short,
          "tape_short_links": tape_short, "tape_min_link_adjacency": min_adj, "tape_min_pivot_followers": min_fol,
          "bar": f"100 % of said contents MEET-tied to their own picture's lit cells · every link >= {adj_bar} adjacency instants and every pivot >= {fol_bar} followers — on the record AND re-counted on the tape"}
    if not said:
        L7.update(graded=False, **{"pass": None}, reason="not gradable: nothing was said")
    else:
        L7.update(graded=True, **{"pass": not (ungrounded or short_rec or piv_short or tape_short)}, reason="graded (§3.4 L7)")
    M["L7"] = L7

    # ---- L8 FORM (printed, seat-graded) and L9 THE NULL IN WORDS (printed)
    by_family: Dict[str, Dict[str, int]] = {}
    for j in journal:
        g = j.get("grade")
        if isinstance(g, dict) and g.get("kind") == "chat":
            f = (chat_truth.get(str(g.get("id"))) or {}).get("family", "?")
            d = by_family.setdefault(f, {"right": 0, "wrong": 0}); d["right" if g.get("right") else "wrong"] += 1
    M["L8"] = {"graded": False, "pass": None, "by_family": by_family, "reason": "printed (seat-graded, no bar)",
               "bar": "no bar: the seat grades 30 random family answers and every free chat for well-formedness"}
    null_said: Dict[str, List[dict]] = {}
    for o, t in fam("what-is"):
        if t.get("thing") in CHAT_NULL_THINGS:
            null_said.setdefault(t["thing"], []).append({"id": o["id"], "said": render_answer(o), "grade": o.get("grade"), "resembles": o.get("resembles")})
    M["L9"] = {"graded": False, "pass": None, "said": null_said, "reason": "printed (A4L-ANSWER's clause; ALPHA4's own answer law, heard)", "bar": "no bar"}

    # ---- the pictures' disjointness from the tape (§3.3), with its planted control
    if tape_canvases is not None and chat_pics:
        from genome import world as _world
        dev = [("?", rgb, {}) for rgb in tape_canvases]
        held = {cid: [(rgb, {})] for cid, rgb in chat_pics.items()}
        try:
            k = _world.assert_disjoint_canvas(dev, held); ok = True
        except AssertionError:
            k = sum(len(v) for v in held.values()); ok = False
        first = next(iter(held.values()))[0][0]
        try:
            _world.assert_disjoint_canvas(dev + [("?", first.copy(), {})], held); caught = False
        except AssertionError:
            caught = True
        M["disjoint"] = {"checked": k, "ok": ok, "control_caught": caught}
    else:
        M["disjoint"] = {"checked": 0, "ok": None, "reason": "not checked (no canvases handed in)"}
    return M
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
# ============================================================================ A4L-EXPLORE (docs/A4-LADDER-PREREG.md §2.5)
# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:59 +0400 — the rung's two marks, test-first
# (tests/creature/test_a4l_explore_marks.py) against the landed shapes: the game eye rows (creature/senses/game.py), the
# journal `act` rows (creature/mind.py:_maybe_choose_act), the game `outcome` rows (terminated / truncated / got).
def _at_s(at: str) -> float:
    import datetime as _dt
    return _dt.datetime.fromisoformat(str(at).replace("Z", "+00:00")).timestamp()


def _first_at_s(tape: List[dict]) -> Optional[float]:
    ats = [_at_s(r["at"]) for r in tape if r.get("at")]
    return min(ats) if ats else None


def explore_lock_mark(tape: Iterable[dict], journal: Iterable[dict], value_declared: bool, after_s: float = 3600.0,
                      window: int = 100, bar: float = 0.5) -> Dict[str, object]:
    """X1 THE LOCK ABSENT (§2.5): over the MIND's game choices (journal `act` rows — never STATUS `acts_chosen`, which
    counts the mouth's `say` beside the seven game acts, the review's finding 3) made on eye rows at or after `after_s`
    of the tape's first row, no act holds ≥ `bar` of any sliding window of `window` consecutive choices. Control:
    alpha4-1's 0–8 h record (`left` 96 of 100 at hour 5) must FAIL; the toy's 50 fresh 8 h lives read the old chooser
    0 / 50 and the candidate 50 / 50. A LOCK detector, not a learning detector: the state-blind ceiling itself
    (forward 0.5) holds 0.54–0.66 of a window. Not gradable where the ACT value line is undeclared (L-1) or fewer than
    `window` choices fall after hour 1."""
    tape = list(tape)
    t0 = _first_at_s(tape)
    at_of = {int(r["seq"]): _at_s(r["at"]) for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "game" and r.get("at")}
    choices = sorted(((int(j["seq"]), j["act"]) for j in journal if isinstance(j.get("act"), dict) and j["act"].get("game")),
                     key=lambda x: x[0])
    after = [(s, a) for s, a in choices if t0 is not None and s in at_of and at_of[s] >= t0 + after_s]
    names = [a.get("act") for _s, a in after]
    policies = dict(collections.Counter(a.get("policy") for _s, a in choices))
    out: Dict[str, object] = {"choices": len(choices), "choices_after": len(names), "policies": policies,
                              "census_after": dict(collections.Counter(names).most_common()),
                              "bar": f"no act ≥ {bar:.0%} of any {window}-choice window after hour {after_s / 3600:g} (the mind's journal act rows)"}
    mx, mx_act, mx_seq = None, None, None
    if len(names) >= window:
        cnt = collections.Counter(names[:window])
        a0, c0 = cnt.most_common(1)[0]
        mx, mx_act, mx_seq = c0 / window, a0, after[0][0]
        for i in range(window, len(names)):
            cnt[names[i]] += 1
            cnt[names[i - window]] -= 1
            a1, c1 = cnt.most_common(1)[0]
            if c1 / window > mx:
                mx, mx_act, mx_seq = c1 / window, a1, after[i - window + 1][0]
    out.update(max_share=(round(mx, 4) if mx is not None else None), max_act=mx_act, max_window_first_seq=mx_seq)
    if not value_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the ACT value line is not declared on this life (L-1)")
    elif len(names) < window:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {len(names)} game choices after hour 1 < {window}")
    else:
        out.update(graded=True, **{"pass": bool(mx < bar)}, reason="graded (A4L-EXPLORE X1)")
    return out


def _binom_bound_k(n: int, p0: float, alpha: float) -> int:
    """The smallest k with P(X ≥ k | Binomial(n, p0)) ≤ alpha — the one-sided (1 − alpha) upper bound of the null."""
    from math import comb
    tail = 0.0
    for k in range(n, -1, -1):
        tail += comb(n, k) * (p0 ** k) * ((1.0 - p0) ** (n - k))
        if tail > alpha:
            return k + 1
    return 0


def explore_success_mark(tape: Iterable[dict], value_declared: bool, from_s: float = 7200.0, to_s: float = 28800.0,
                         p0: float = 0.29, alpha: float = 0.05, ceiling: float = 0.488,
                         toy_candidate: Tuple[float, float] = (0.240, 0.106),
                         age_matched: Optional[dict] = None) -> Dict[str, object]:
    """X2 SUCCESS PER EPISODE (§2.5) over hours 2–8 — PRINTED, NO BAR (edit: Claude (Opus 5.5, A4 ladder builder EXPLORE),
    2026-09-23 12:26 +0400, on the orchestrator's 12:2x +04 order; #228 (b)): the game episodes whose terminal outcome row (terminated or
    truncated) falls in [t0 + from_s, t0 + to_s); successes = terminated with reward > 0. Printed beside them: the null's
    one-sided 95 % bound at that N (p0 = L-8's 0.29, reproduced by the toy's (0a) on GoToLocal), the state-blind CEILING
    the toy measured (forward 0.5: 0.488 ± 0.023, docs/briefs/A4L-EXPLORE-TOY.md §3), whether the bound sits above it
    (at an 8 h life's N ≈ 13 it does: 8 / 13 = 0.615 — no state-blind chooser can clear it, so no bar is set), the
    toy's candidate reading over 50 fresh 8 h lives (0.240 ± 0.106 — the prediction) and the age-matched control the
    orchestrator passes (alpha4-1's own episodes over its hours 2–8). Never graded; «not gradable» where the ACT value
    line is undeclared (L-1)."""
    tape = list(tape)
    t0 = _first_at_s(tape)
    ends = [r for r in tape if r.get("sense") == "outcome" and _meta(r).get("source") == "game" and r.get("at")
            and (_meta(r).get("terminated") or _meta(r).get("truncated"))]
    win = [r for r in ends if t0 is not None and t0 + from_s <= _at_s(r["at"]) < t0 + to_s]
    n = len(win)
    k = sum(1 for r in win if _meta(r).get("terminated") and float(_meta(r).get("got") or 0.0) > 0)
    kb = _binom_bound_k(n, p0, alpha) if n else None
    out: Dict[str, object] = {
        "episodes": n, "successes": k, "success_rate": (round(k / n, 4) if n else None), "p0": p0, "alpha": alpha,
        "bound_k": kb, "bound_rate": (round(kb / n, 4) if n else None), "ceiling": ceiling,
        "bound_above_ceiling": (bool(kb / n > ceiling) if n else None), "clears_bound": (bool(k >= kb) if n else None),
        "toy_candidate_mean_sd": list(toy_candidate), "age_matched": age_matched,
        "bar": "none — printed (#228 (b)): at an 8 h life's N the null's 95 % bound sits above the state-blind ceiling",
    }
    if not value_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: the ACT value line is not declared on this life (L-1)")
    elif n == 0:
        out.update(graded=False, **{"pass": None}, reason="printed, no bar: no game episode ended in hours 2–8")
    else:
        out.update(graded=False, **{"pass": None},
                   reason=(f"printed, no bar (#228 (b)): {k} of {n} episodes; the null's 95 % bound {kb}/{n} = {kb / n:.3f}"
                           f" {'above' if kb / n > ceiling else 'at or under'} the state-blind ceiling {ceiling}"))
    return out


# ================================================================================================= READER v3.5 — the ladder-2 marks
# edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 05:26 +0400 — A4-LADDER-2-PREREG §2 (each rung's mark read at 8 h) and its ADDENDUM §7(2)
# (the identity law's operational form). Pure functions over the landed row shapes (#171/#173); the I/O (a second closed root, predictions.jsonl,
# HEARD.json, the exam files) is read by tools/verdict_g4.py:side_record and handed in. Every mark prints its DENOMINATOR and REACH (#234) and reads
# NOT GRADABLE below a declared floor or where its line is undeclared (L-1) — never FAIL for a horizon the world could not reach (#237 (b)).

IDENTITY_SOURCES = ("maker", "game", "shelf", "folder")     # ADDENDUM §7(2) item 1: the world's four eye streams (graded); any other source printed


STREAM_TAGS = ("answering", "control", "program", "episode")    # the eye-row meta keys that name WHY a row is in a stream (printed at a divergence)


def eye_streams(tape: Iterable[dict]) -> Dict[str, List[Tuple[int, str, dict]]]:
    """source -> [(seq, sha, tags)] of the tape's EYE rows, each stream in its own (tape) order; tags = the row's meta keys among STREAM_TAGS
    (edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 06:00 +0400 — the 8 h reads showed the world's streams diverge by INSERTED rows, e.g. the maker's
    `answering` canvas for the mind's own question; the tags say so at the divergence)."""
    s: Dict[str, List[Tuple[int, str, dict]]] = collections.defaultdict(list)
    for r in tape:
        if r.get("sense") == "eye":
            m = _meta(r)
            s[str(m.get("source"))].append((int(r["seq"]), str(r.get("sha")), {k: m[k] for k in STREAM_TAGS if k in m}))
    return dict(s)


def _realign(a: Sequence[tuple], b: Sequence[tuple], fd: int, max_off: int = 10) -> Dict[str, object]:
    """After a stream's first divergence at `fd`: the offset in [-max_off, max_off] under which the REST of the two streams agree best
    (b[k + offset] == a[k] for k ≥ fd — a positive offset = b carries `offset` more rows before the rest), with the matched count. Printed
    only: a stream identical «up to an inserted row» is still a different stream to the mind that consumed it."""
    best = None
    for off in range(-max_off, max_off + 1):
        n = tot = 0
        for k in range(fd, len(a)):
            j = k + off
            if j < 0 or j >= len(b):
                continue
            tot += 1
            n += int(a[k][1] == b[j][1])
        if tot and (best is None or n > best[1] or (n == best[1] and abs(off) < abs(best[0]))):
            best = (off, n, tot)
    if best is None:
        return {"offset": None, "matched": 0, "of": 0}
    return {"offset": best[0], "matched": best[1], "of": best[2], "whole_rest": bool(best[1] == best[2])}


def stream_identity(sa: Dict[str, List[tuple]], sb: Dict[str, List[tuple]],
                    sources: Sequence[str] = IDENTITY_SOURCES) -> Dict[str, dict]:
    """Per source: both lengths, the canvases compared (the last canvas BOTH reached = the shorter stream), how many are identical before the
    first divergence, and the divergence itself (index, both seqs, both sha prefixes). The four world sources are graded; any other source the
    tapes carry (hands — the creature's own drawings; lexicon — the door) is printed beside, `graded` False."""
    out: Dict[str, dict] = {}
    for src in list(sources) + sorted(k for k in set(sa) | set(sb) if k not in sources):
        a, b = sa.get(src, []), sb.get(src, [])
        n = min(len(a), len(b))
        fd = next((i for i in range(n) if a[i][1] != b[i][1]), None)
        out[src] = {"a": len(a), "b": len(b), "compared": n, "identical": (n if fd is None else fd),
                    "first_divergence": (None if fd is None else {"index": fd, "seq_a": a[fd][0], "seq_b": b[fd][0],
                                                                  "sha_a": a[fd][1][:12], "sha_b": b[fd][1][:12],
                                                                  "tags_a": (a[fd][2] if len(a[fd]) > 2 else {}), "tags_b": (b[fd][2] if len(b[fd]) > 2 else {}),
                                                                  "realigned": _realign(a, b, fd)}),
                    "graded": src in sources}
    return out


def meeting_readings(journal: Iterable[dict]) -> Tuple[Dict[tuple, dict], int]:
    """The mind's own counters at every canvas row that carries its OWN reading. Key: the per-source canvas counts so far over EVERY eye source
    the journal names — hands and lexicon included: keyed on the four world sources alone, a hands canvas interleaved on either side of a
    folder canvas makes two different moments look like one meeting point (a4l2-pre-cost seq 1575/1580 vs a4l-pre-cost 1577/1578: cells 725
    vs 724 at «the same» four-source counts). Only a canvas row carrying `cells` is a reading: a hands canvas (and a life's very first folder
    canvas) journals neither `births` nor `cells`, so a reading carried forward over it lags that canvas's own births (the carry-forward's one
    false hit on the pre-flights). Value: {seq, canvas (1-based, over every source), births (journaled: sight/words on canvas rows + a sleep's
    consolidation births — a LOWER bound of STATUS's, which counts the hands canvases' births too), cells (the row's own alive count per area —
    exact), sleeps (sleep rows so far), id_next (the next id per area after the largest id journaled — printed only: two lives that interleave a
    hands canvas differently give the same births different ids)}. Returns (readings, total canvases)."""
    out: Dict[tuple, dict] = {}
    cnt: collections.Counter = collections.Counter(); births: collections.Counter = collections.Counter()
    idn: collections.Counter = collections.Counter(); sleeps = 0; n = 0
    for r in journal:
        if "event" in r:
            continue
        sl = r.get("sleep")
        if isinstance(sl, dict):
            sleeps += 1
            births["sleep"] += int(sl.get("births") or 0)
        if "moment" in r and r.get("glance") == 0 and r.get("source") is not None:
            for b in r.get("births") or []:
                births[str(b[0])] += 1
                try:
                    idn[str(b[0])] = max(idn[str(b[0])], int(b[1]) + 1)
                except (TypeError, ValueError, IndexError):
                    pass
            cnt[str(r["source"])] += 1
            n += 1
            if r.get("cells") is not None:
                out[tuple(sorted(cnt.items()))] = {"seq": int(r["seq"]), "canvas": n, "births": dict(births),
                                                   "cells": list(r["cells"]), "sleeps": sleeps, "id_next": dict(idn)}
    return out, n


def _max_abs_deltas(pairs: Sequence[Tuple[dict, dict]]) -> Dict[str, int]:
    """The largest |a − b| per counter over the disagreeing meeting points (births per kind, cells per area, sleeps) — printed: a ±1 that
    re-converges (an error birth landing on a neighbouring canvas when the senses interleave differently) reads apart from a growing gap.
    (edit: Claude (Opus 5.5, reader v3.5 builder), 2026-09-24 06:00 +0400)"""
    out: Dict[str, int] = {}
    for x, y in pairs:
        for k in set(x.get("births") or {}) | set(y.get("births") or {}):
            out["births." + k] = max(out.get("births." + k, 0), abs(int((x.get("births") or {}).get(k, 0)) - int((y.get("births") or {}).get(k, 0))))
        for i, (u, v) in enumerate(zip(x.get("cells") or [], y.get("cells") or [])):
            out[f"cells[{i}]"] = max(out.get(f"cells[{i}]", 0), abs(int(u) - int(v)))
        out["sleeps"] = max(out.get("sleeps", 0), abs(int(x.get("sleeps") or 0) - int(y.get("sleeps") or 0)))
    return out


def _reading_counts(x: dict) -> tuple:
    return (tuple(sorted((x.get("births") or {}).items())), tuple(x.get("cells") or ()), int(x.get("sleeps") or 0))


def identity_mark(tape_a: Iterable[dict], journal_a: Iterable[dict], tape_b: Iterable[dict], journal_b: Iterable[dict],
                  provided: bool = True, wall: Optional[dict] = None, min_canvases: int = 100, max_listed: int = 10,
                  label_a: str = "this life", label_b: str = "the identity root") -> Dict[str, object]:
    """R0b IDENTITY (A4-LADDER-2-PREREG §2 R0b row; its ADDENDUM §7(2) item 1 — «equality is judged PER SOURCE STREAM at equal canvas counts,
    never per tape or at equal wall-clock»): (1) each world stream (the eye rows of maker/game/shelf/folder, each in its own order, by sha)
    identical to the last canvas BOTH reached — an identical game stream means the two minds chose the same acts; (2) at EVERY meeting point
    (`meeting_readings`: a canvas row carrying its own reading in BOTH journals at equal per-source canvas counts over every eye source) the
    two minds' journaled births (sight/words/sleep), alive cells per area and sleeps are EQUAL. PASS iff (1) and (2). Printed beside, never
    graded: the id order (differs by sense interleaving), the other streams (hands, lexicon), the reach (the last meeting point's canvas of each
    life's total) and the wall-clock numbers of both lives with the band (the reference's own per-canvas rate over its last hour × Δcanvases —
    the pacing differs by minutes between lives). NOT GRADABLE: no second root given; fewer than `min_canvases` canvases on either side; no
    meeting point at or beyond canvas `min_canvases`."""
    bar = ("ADDENDUM §7(2): every world stream (eye rows of maker/game/shelf/folder, each in its own order, by sha) identical to the last canvas "
           "both reached, AND at every meeting point (a canvas row with its own reading in BOTH journals at equal per-source canvas counts over "
           "every eye source) the journaled births (sight/words/sleep), alive cells per area and sleeps equal; the wall-clock numbers beside with the band")
    out: Dict[str, object] = {"bar": bar, "label_a": label_a, "label_b": label_b}
    if not provided:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no --identity-root given (R0b's reading compares this life with a second CLOSED root)")
        return out
    streams = stream_identity(eye_streams(tape_a), eye_streams(tape_b))
    ra, na = meeting_readings(journal_a)
    rb, nb = meeting_readings(journal_b)
    common = sorted((k for k in ra if k in rb), key=lambda k: ra[k]["canvas"])
    dis = [k for k in common if _reading_counts(ra[k]) != _reading_counts(rb[k])]
    ids_only = [k for k in common if _reading_counts(ra[k]) == _reading_counts(rb[k]) and ra[k]["id_next"] != rb[k]["id_next"]]
    last = common[-1] if common else None
    def _pt(k):
        return {"counts": dict(k), "canvas": ra[k]["canvas"], "seq_a": ra[k]["seq"], "seq_b": rb[k]["seq"],
                "a": {kk: ra[k][kk] for kk in ("births", "cells", "sleeps", "id_next")},
                "b": {kk: rb[k][kk] for kk in ("births", "cells", "sleeps", "id_next")}}
    graded_streams = {s: v for s, v in streams.items() if v["graded"]}
    streams_ok = all(v["first_divergence"] is None for v in graded_streams.values())
    out.update(streams=streams, streams_identical=streams_ok,
               streams_not_on_either_tape=[s for s, v in graded_streams.items() if v["compared"] == 0],
               canvases_a=na, canvases_b=nb, readings_a=len(ra), readings_b=len(rb),
               meeting_points=len(common), meeting_points_agree=len(common) - len(dis), meeting_points_disagree=len(dis),
               disagreements=[_pt(k) for k in dis[:max_listed]],
               disagreement_max_abs=_max_abs_deltas([(ra[k], rb[k]) for k in dis]),
               last_agreeing_meeting_point_canvas=next((ra[k]["canvas"] for k in reversed(common) if _reading_counts(ra[k]) == _reading_counts(rb[k])), None),
               last_meeting_point_agrees=(bool(_reading_counts(ra[last]) == _reading_counts(rb[last])) if last is not None else None),
               id_order_differs_at=len(ids_only), id_order_note=("the next-id counter differs at %d meeting points where births, cells and sleeps agree: "
                                                                "the same births took different ids (a hands canvas births without a journal row, and "
                                                                "the two lives interleave it differently) — printed, never graded" % len(ids_only)) if ids_only else None,
               last_meeting_point=(_pt(last) if last is not None else None),
               reach=({"canvas": ra[last]["canvas"], "of_a": na, "of_b": nb, "share_of_shorter": round(ra[last]["canvas"] / max(1, min(na, nb)), 4)}
                      if last is not None else None),
               births_note="journaled births: the canvas rows' `births` + a sleep's consolidation births — a lower bound of STATUS sight_born/births "
                           "(a hands canvas births with no journal row); the SAME instrument on both lives",
               wall=wall)
    if min(na, nb) < min_canvases:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: {na} / {nb} canvases < {min_canvases}")
        return out
    why = []
    if not streams_ok:     # a diverged world stream decides the mark alone — never hidden behind «no meeting point»
        why.append("streams diverge: " + "; ".join(
            f"{s} at {v['first_divergence']['index']}"
            + (f" (a {v['first_divergence']['tags_a']} / b {v['first_divergence']['tags_b']})" if (v['first_divergence'].get('tags_a') or v['first_divergence'].get('tags_b')) else "")
            + (f"; the rest identical at offset {v['first_divergence']['realigned']['offset']:+d} for {v['first_divergence']['realigned']['matched']} of {v['first_divergence']['realigned']['of']}"
               if (v['first_divergence'].get('realigned') or {}).get('offset') is not None else "")
            for s, v in graded_streams.items() if v["first_divergence"]))
    elif last is None or ra[last]["canvas"] < min_canvases:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: the streams are identical but no meeting point lies at or beyond canvas {min_canvases} (the two minds' per-source counts never coincide there)")
        return out
    ok = bool(streams_ok and not dis)
    if dis:
        k0 = dis[0]
        why.append(f"{len(dis)} of {len(common)} meeting points disagree (first at canvas {ra[k0]['canvas']}: {label_a} {_reading_counts(ra[k0])} vs {label_b} {_reading_counts(rb[k0])}; "
                   f"max |Δ| {out['disagreement_max_abs']}; the last meeting point (canvas {ra[last]['canvas']}) {'agrees' if out['last_meeting_point_agrees'] else 'disagrees'})")
    out.update(graded=True, **{"pass": ok}, reason=("graded (ADDENDUM §7(2)): " + ("identical — every world stream to the last canvas both reached, and the counts at all "
                                                                                  f"{len(common)} meeting points" if ok else "; ".join(why))))
    return out


def _series_t(r: dict) -> Optional[float]:
    for k in ("heartbeat_at", "sampled_at"):
        if r.get(k):
            try:
                return _at_s(r[k])
            except (TypeError, ValueError):
                continue
    return None


WALL_KEYS = ("cells", "sight_born", "births", "sleeps")


def wall_reading(series: Sequence[dict], status: dict, canvas_seqs: Sequence[int], t_cut: Optional[float]) -> Dict[str, object]:
    """The life's own exact counters at the wall-clock cut: the last `readings/status-series.jsonl` sample (the sampler's STATUS copies, every 5 min)
    whose STATUS write (`heartbeat_at`) is at or before `t_cut` — or STATUS.json itself when it is (a closed life's last write) or when no series
    exists; `canvases` = the journal's canvas rows with seq ≤ that reading's `last_seq`. Also the per-canvas RATE of each counter over the hour
    before it (the band's rate). `t_cut` None = the latest reading."""
    import bisect
    cands = [(t, r) for r in list(series or []) + ([dict(status, _src="STATUS.json")] if status else []) for t in [_series_t(r)] if t is not None]
    if t_cut is not None:
        cands = [(t, r) for t, r in cands if t <= t_cut + 1e-6]
    if not cands:
        return {"at": None, "source": "no reading at or before the cut"}
    cands.sort(key=lambda x: x[0])
    t, r = cands[-1]
    def _canv(x):
        ls = x.get("last_seq")
        return bisect.bisect_right(list(canvas_seqs), int(ls)) if isinstance(ls, int) and not isinstance(ls, bool) else None
    out: Dict[str, object] = {"at": r.get("heartbeat_at"), "source": r.get("_src", "readings/status-series.jsonl"), "last_seq": r.get("last_seq"),
                              "canvases": _canv(r), **{k: r.get(k) for k in WALL_KEYS}}
    prev = [(tt, rr) for tt, rr in cands if tt <= t - 3600.0]
    rate: Dict[str, Optional[float]] = {}
    if prev:
        tp, rp = prev[-1]
        c1, c0 = _canv(r), _canv(rp)
        for k in WALL_KEYS:
            try:
                rate[k] = round((float(r[k]) - float(rp[k])) / (c1 - c0), 5) if (c1 is not None and c0 is not None and c1 > c0) else None
            except (TypeError, ValueError, KeyError):
                rate[k] = None
        out["rate_window"] = {"from": rp.get("heartbeat_at"), "to": r.get("heartbeat_at"), "canvases": ((c1 - c0) if (c1 is not None and c0 is not None) else None)}
    out["rate_per_canvas_last_hour"] = rate or None
    return out


def wall_band(wa: dict, wb: dict) -> Dict[str, object]:
    """The wall-clock comparison (printed, never graded — ADDENDUM §7(2) item 1): Δ = a − b per counter; the band = ceil(|b's own per-canvas
    rate over its last hour × Δcanvases|) — the difference the pacing alone explains; `inside` per counter."""
    import math
    dc = (wa.get("canvases") - wb.get("canvases")) if (isinstance(wa.get("canvases"), int) and isinstance(wb.get("canvases"), int)) else None
    rates = wb.get("rate_per_canvas_last_hour") or {}
    per: Dict[str, dict] = {}
    for k in WALL_KEYS:
        va, vb = wa.get(k), wb.get(k)
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            per[k] = {"a": va, "b": vb, "delta": None, "band": None, "inside": None}
            continue
        r = rates.get(k)
        band = (int(math.ceil(abs(r * dc))) if (r is not None and dc is not None) else None)
        per[k] = {"a": va, "b": vb, "delta": va - vb, "expected_from_pacing": (round(r * dc, 1) if (r is not None and dc is not None) else None),
                  "band": band, "inside": (abs(va - vb) <= band if band is not None else None)}
    return {"a": wa, "b": wb, "delta_canvases": dc, "per_counter": per,
            "band_rule": "ceil(|the identity root's own per-canvas rate over its last hour × Δcanvases|) — the pacing's share (ADDENDUM §7(2) item 1)",
            "band_note": (None if rates else "no band: the identity root carries no status-series sample an hour before its reading (a pre-flight "
                                             "or an older record) — the Δ printed alone")}


def explore_lock_window(tape: Iterable[dict], journal: Iterable[dict], after_s: float = 3600.0, window: int = 100) -> Dict[str, object]:
    """X1's window, located (the brief: «print the max share and the window it sat in»): the same choices `explore_lock_mark` reads (journal `act`
    rows of the game, on game eye rows at or after hour 1), the window of `window` consecutive choices whose top act's share is largest —
    its first and last choice's seq, their tape time and hour of life, and the act census inside it."""
    tape = list(tape)
    t0 = _first_at_s(tape)
    at_of = {int(r["seq"]): _at_s(r["at"]) for r in tape if r.get("sense") == "eye" and _meta(r).get("source") == "game" and r.get("at")}
    choices = sorted(((int(j["seq"]), j["act"]) for j in journal if isinstance(j.get("act"), dict) and j["act"].get("game")), key=lambda x: x[0])
    after = [(s, a) for s, a in choices if t0 is not None and s in at_of and at_of[s] >= t0 + after_s]
    if len(after) < window:
        return {"choices_after_hour_1": len(after), "window": None}
    names = [a.get("act") for _s, a in after]
    cnt = collections.Counter(names[:window]); best = (cnt.most_common(1)[0][1], 0)
    for i in range(window, len(names)):
        cnt[names[i]] += 1; cnt[names[i - window]] -= 1
        c1 = cnt.most_common(1)[0][1]
        if c1 > best[0]:
            best = (c1, i - window + 1)
    i0 = best[1]; seg = after[i0:i0 + window]
    return {"choices_after_hour_1": len(after),
            "window": {"first_choice": i0 + 1, "last_choice": i0 + window, "first_seq": seg[0][0], "last_seq": seg[-1][0],
                       "first_hour": round((at_of[seg[0][0]] - t0) / 3600.0, 3), "last_hour": round((at_of[seg[-1][0]] - t0) / 3600.0, 3),
                       "census": dict(collections.Counter(a.get("act") for _s, a in seg).most_common()), "top_share": round(best[0] / window, 4)}}


def explore_x2_census(tape: Iterable[dict], journal: Iterable[dict], status: dict) -> Dict[str, object]:
    """X2's denominators (A4-LADDER-2-PREREG ADDENDUM §7(2) items 3–4: a «never paid» count is computed from the field the CONSUMER reads — the
    journal's game `outcome.got` — with that field's PRESENCE count beside the zero; BabyAI pays only on the successful terminal step): the
    journal's game outcome rows, how many carry `got`, how many paid (got > 0, the values listed), and the tape's game outcome rows with the
    terminal flags (terminated / truncated — the episodes), the rewarded terminal rows, success per episode; the chooser's law as STATUS last
    wrote it (act_policy, act_weights, act_explored). Printed, never graded."""
    tape = list(tape); journal = list(journal)
    j_out = [j["outcome"] for j in journal if isinstance(j.get("outcome"), dict) and j["outcome"].get("source") == "game"]
    has_got = [o for o in j_out if "got" in o]
    paid = [o for o in has_got if isinstance(o.get("got"), (int, float)) and not isinstance(o.get("got"), bool) and o["got"] > 0]
    t_out = [r for r in tape if r.get("sense") == "outcome" and _meta(r).get("source") == "game"]
    term = [r for r in t_out if _meta(r).get("terminated")]
    trunc = [r for r in t_out if _meta(r).get("truncated") and not _meta(r).get("terminated")]
    wins = [r for r in term if float(_meta(r).get("got") or 0.0) > 0]
    eps = len(term) + len(trunc)
    return {"journal_game_outcome_rows": len(j_out), "rows_carrying_got": len(has_got), "rewarded_rows": len(paid),
            "rewards": [round(float(o["got"]), 4) for o in paid][:20],
            "tape_game_outcome_rows": len(t_out), "rows_carrying_flags": sum(1 for r in t_out if "terminated" in _meta(r) or "truncated" in _meta(r)),
            "episodes_terminal_rows": eps, "terminated": len(term), "truncated": len(trunc), "successes": len(wins),
            "success_per_episode": (round(len(wins) / eps, 4) if eps else None),
            "act_policy": (status or {}).get("act_policy", "not recorded"), "act_weights": (status or {}).get("act_weights", "not recorded"),
            "act_explored": (status or {}).get("act_explored", "not recorded")}


LINE_CEILING = 0.272          # A42-B2-REPORT §1: the strict ceiling on the 6 h snapshot (0.545 on hour 1) — A4-LADDER-2-PREREG §2 R2 row, cleared
LINE_CEILING_SOURCE = "docs/briefs/A42-B2-REPORT.md §1 (B2's ceiling: 0.272 strict on the 6 h snapshot, 0.545 on hour 1 — measured before the build)"


def _line_group(r: dict) -> str:
    i = r.get("instant")
    if not isinstance(i, dict):
        return "unstamped"
    src = str(i.get("source"))
    if src == "shelf":
        return "shelf_line" if i.get("line") else "shelf_word"
    return src


def line_mark(pred_rows: Iterable[dict], status: dict, line_declared: bool, ceiling: float = LINE_CEILING,
              tape_frames: Optional[dict] = None, control: Optional[dict] = None) -> Dict[str, object]:
    """R2 LINE (A4-LADDER-2-PREREG §2 R2 row, B2's finding): shelf frames scored TRUE > 0 — read from the scorer's OWN ledger
    (`state/predictions.jsonl`: a frame row is written when filed, `outcome` null, and again when scored, `outcome` true/false; under
    `SENTENCE …; judged by the eye on the line; …` the scored row carries `instant: {source, words, line}`) and STATUS `frames_scored`/
    `frames_true` — NEVER from the journal (the scorer is a read-only road; the LINE genome's journal is IDENTICAL to FLOOR's). Printed beside:
    the scored frames by the instant they were scored on (shelf line / game / lexicon / unstamped), the realised shelf true-rate and its ratio
    to B2's ceiling (§7 (4): predicted 0.1×–1×), READ's tape frames vs their shuffled twin (`read_frames` — the tape's co-occurrence, not the
    scorer: the scorer exposes no shuffled twin), the game frames beside the control's (R0) when given. NOT GRADABLE: the `on the line` clause
    undeclared (the scorer writes no stamp); no shelf line instant scored a frame on the record (the horizon, #237 (b))."""
    rows = [r for r in pred_rows if isinstance(r, dict) and (r.get("row") or {}).get("route") == "frame"]
    scored = [r for r in rows if r.get("outcome") is not None]
    by: Dict[str, Dict[str, int]] = {}
    for r in scored:
        g = by.setdefault(_line_group(r), {"scored": 0, "true": 0})
        g["scored"] += 1; g["true"] += int(r.get("outcome") is True)
    sl = by.get("shelf_line", {"scored": 0, "true": 0})
    rate = (sl["true"] / sl["scored"]) if sl["scored"] else None
    st = {k: (status or {}).get(k, "not recorded") for k in ("frames_filed", "frames_scored", "frames_true")}
    out: Dict[str, object] = {
        "bar": "shelf frames scored TRUE > 0 (state/predictions.jsonl rows stamped instant.source shelf, line True; STATUS frames_scored/frames_true beside — never the journal)",
        "status": st, "frame_rows": len(rows), "frame_rows_filed": sum(1 for r in rows if r.get("outcome") is None), "frame_rows_scored": len(scored),
        "scored_reconciles_with_status": (len(scored) == st["frames_scored"]) if isinstance(st["frames_scored"], int) else None,
        "by_instant": by, "shelf_line_scored": sl["scored"], "shelf_line_true": sl["true"],
        "shelf_true_rate": (round(rate, 4) if rate is not None else None), "ceiling": ceiling, "ceiling_source": LINE_CEILING_SOURCE,
        "ratio_to_ceiling": (round(rate / ceiling, 3) if (rate is not None and ceiling) else None),
        "predicted": "shelf true-rate between 0.1× and 1× the ceiling (§7 (4) as amended 17:53: ≈ the ceiling × the world's co-occurrence rate)",
        "game": by.get("game"), "tape_frames_read": tape_frames,
        "shuffled_twin_of_the_scorer": "not exposed by the scorer (its ledger carries no twin); READ's tape frames vs their shuffled twin printed instead",
        "control": control}
    if not line_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: SENTENCE's «judged by the eye on the line» clause is not declared on this life (the scorer writes no instant stamp; L-1)")
    elif sl["scored"] == 0:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: no shelf LINE instant scored a frame on this record ({len(scored)} frame rows scored in all) — the horizon, never FAIL")
    else:
        out.update(graded=True, **{"pass": bool(sl["true"] > 0)},
                   reason=f"graded (R2): {sl['true']} of {sl['scored']} shelf-line frames true ({rate:.3f}; {rate / ceiling:.2f}× the ceiling {ceiling})")
    return out


NURSERY_HEADER_STEMS = ("gutenb", "ebook", "www", "license", "licence")    # the header's tokens (A4-LADDER-2-PREREG §2 R3 row), cut to 8 letters as the reader cuts


def _is_header_token(w: str) -> bool:
    w = str(w).lower()
    return any(w.startswith(s) for s in NURSERY_HEADER_STEMS)


def nursery_mark(heard: Sequence[str], control_heard: Optional[Sequence[str]], shelf_words: Sequence[str], body_only_declared: bool,
                 prereg_shift: int = 129) -> Dict[str, object]:
    """R3 NURSERY (A4-LADDER-2-PREREG §2 R3 row; the brief's measured form): `read/HEARD.json` (the shelf reader's first-heard distinct words)
    carries NONE of the header's tokens — the stems gutenb*/ebook/www*/license*, and «project» where it is the header's «project gutenb…»
    (the bigram on the shelf's ear-word stream; «project» alone may be a body word) — AND the rung's words are an ORDERED SUBSEQUENCE of R0's
    body words: every word R0 first heard at or after the SHIFT (the index in R0's HEARD of this life's first word) appears here in R0's
    order. Printed: the measured shift beside the PREREG's guessed 129 (the reader cuts words to 8 letters and skips non-letters), the words
    R0 heard first in its header and this life heard in the body (a re-heard word, not a failure), the words R0 never heard (this life read
    further into the book), and the stronger reading: this life's words minus R0's header words == R0's body words on their common length.
    NOT GRADABLE: `; gutenberg body only` undeclared; no control HEARD (--control-root); an empty HEARD; this life's first word absent from R0's."""
    heard = [str(w) for w in (heard or [])]
    ctl = [str(w) for w in (control_heard or [])]
    hits = [w for w in heard if _is_header_token(w)]
    sw = [str(w).lower() for w in (shelf_words or [])]
    proj_bigrams = sum(1 for i in range(len(sw) - 1) if sw[i] == "project" and sw[i + 1].startswith("gutenb"))
    out: Dict[str, object] = {
        "bar": "HEARD.json carries 0 header tokens (gutenb*/ebook/www*/license*, and «project» as the header's «project gutenb…» bigram on the ear stream) AND "
               "an ordered subsequence of R0's body words (R0's HEARD from the measured shift on)",
        "heard": len(heard), "header_tokens_in_heard": hits[:20], "header_tokens_n": len(hits), "project_gutenberg_bigrams_heard": proj_bigrams,
        "project_in_heard": ("project" in heard), "shelf_ear_words": len(sw), "prereg_shift_guess": prereg_shift,
        "control_heard": (len(ctl) if control_heard is not None else None)}
    if not body_only_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: SENSE read's «; gutenberg body only» clause is not declared on this life (L-1)")
        return out
    if control_heard is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no control HEARD.json (--control-root: R0's closed root) — the header tokens printed")
        return out
    if not heard:
        out.update(graded=False, **{"pass": None}, reason="not gradable: this life's HEARD.json is empty")
        return out
    idx = {w: i for i, w in enumerate(ctl)}
    shift = idx.get(heard[0])
    out["shift_measured"] = shift
    out["first_word"] = heard[0]
    if shift is None:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: this life's first word {heard[0]!r} is absent from R0's HEARD ({len(ctl)} words)")
        return out
    body = [(w, idx[w]) for w in heard if w in idx and idx[w] >= shift]
    breaks = [(a[0], a[1], b[0], b[1]) for a, b in zip(body, body[1:]) if not a[1] < b[1]]
    header_shared = [w for w in heard if w in idx and idx[w] < shift]
    beyond = [w for w in heard if w not in idx]
    hw = set(ctl[:shift]); mine = [w for w in heard if w not in hw]; theirs = ctl[shift:]
    n = min(len(mine), len(theirs))
    fd = next((i for i in range(n) if mine[i] != theirs[i]), None)
    ordered = not breaks
    out.update(ordered_subsequence=ordered, body_words_matched=len(body), order_breaks=breaks[:10], order_breaks_n=len(breaks),
               header_shared_reheard=len(header_shared), header_shared_sample=header_shared[:12],
               beyond_control=len(beyond), beyond_control_sample=beyond[:12],
               stronger_prefix_equal={"compared": n, "first_mismatch": (None if fd is None else {"index": fd, "this": mine[fd], "control": theirs[fd]})},
               differs_from_word_1=bool(ctl and heard[0] != ctl[0]))
    ok = (len(hits) == 0 and proj_bigrams == 0 and ordered)
    out.update(graded=True, **{"pass": bool(ok)},
               reason=(f"graded (R3): header tokens {len(hits)} (+ «project gutenb…» bigrams {proj_bigrams}); ordered subsequence {ordered} over {len(body)} body words; "
                       f"shift measured {shift} (PREREG guessed {prereg_shift})"))
    return out


def nursery_read_mark(exams: Sequence[dict], control_exams: Optional[Sequence[dict]], body_only_declared: bool, z: float = 2.0) -> Dict[str, object]:
    """R3's third clause (A4-LADDER-2-PREREG §2 R3 row: «READ mark within noise of R0»): the sitter's own reading mark (`read_share` over
    `read_words_n` HEARD words in the held-out font, every exam file) at this life's LAST exam vs R0's last exam in the same window; within
    noise = |Δ| ≤ z × the two-sample binomial standard error (z = 2). The samples are different words by design (each life's fixed-seed draw over
    its OWN HEARD.json) — said. NOT GRADABLE: the clause undeclared; no control exams; either side carries no read_share."""
    import math
    def _last(ex):
        for e in reversed(list(ex or [])):
            if isinstance(e.get("read_share"), (int, float)) and e.get("read_words_n"):
                return {"at": e.get("at"), "share": float(e["read_share"]), "n": int(e["read_words_n"]), "file": e.get("_file")}
        return None
    a, b = _last(exams), (_last(control_exams) if control_exams is not None else None)
    out: Dict[str, object] = {"bar": f"this life's last exam read_share within {z:g} × the two-sample binomial SE of R0's last exam's",
                              "this": a, "control": b, "exams": len(list(exams or [])), "control_exams": (len(list(control_exams)) if control_exams is not None else None),
                              "note": "each life's sample is its own fixed-seed draw over its OWN HEARD.json — different words by design"}
    if not body_only_declared:
        out.update(graded=False, **{"pass": None}, reason="not gradable: «; gutenberg body only» not declared on this life (L-1)")
        return out
    if control_exams is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: no control exams (--control-root: R0's closed root)")
        return out
    if a is None or b is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: an exam with read_share is missing on %s" % ("this life" if a is None else "the control"))
        return out
    se = math.sqrt(a["share"] * (1 - a["share"]) / a["n"] + b["share"] * (1 - b["share"]) / b["n"])
    d = a["share"] - b["share"]
    ok = abs(d) <= z * se + 1e-12
    out.update(delta=round(d, 4), se=round(se, 4), band=round(z * se, 4), graded=True, **{"pass": bool(ok)},
               reason=f"graded (R3 READ): {a['share']:.3f} (n {a['n']}) vs R0 {b['share']:.3f} (n {b['n']}): Δ {d:+.3f}, band ±{z * se:.3f}")
    return out


def drop_equality_mark(status: dict, drop_declared: bool) -> Dict[str, object]:
    """R5's live equality (A4-LADDER-PREREG §2.4 / A4L-DROP task 5; A4-LADDER-2-PREREG ADDENDUM §7(2) item 2): under `; drop confirmed` every
    CONFIRMED glance is a DROPPED one — STATUS glances_dropped == glances_confirmed. NOT GRADABLE where the clause is undeclared (the body writes
    glances_dropped 0 on every write — the ordinary reading there) or where STATUS never wrote the key (an older body)."""
    gc, gd = (status or {}).get("glances_confirmed"), (status or {}).get("glances_dropped")
    out: Dict[str, object] = {"bar": "STATUS glances_dropped == glances_confirmed while `; drop confirmed` is declared",
                              "glances_confirmed": gc, "glances_dropped": gd, "glances_surprised": (status or {}).get("glances_surprised")}
    if gd is None or gc is None:
        out.update(graded=False, **{"pass": None}, reason="not gradable: STATUS carries no glances_dropped/glances_confirmed (an older body)")
    elif not drop_declared:
        out.update(graded=False, **{"pass": None}, reason=f"not gradable: `; drop confirmed` not declared (dropped {gd} — 0 is the ordinary reading)")
    else:
        out.update(graded=True, **{"pass": bool(gd == gc)}, reason=f"graded (R5): dropped {gd} {'==' if gd == gc else '!='} confirmed {gc}")
    return out


CHAT_COUNTER_KEYS = ("chats", "chat_answered", "chat_abstained", "chat_refused_form", "chat_refused_content", "chat_graded",
                     "chat_graded_right", "chat_graded_novel", "chat_words_mean", "chat_longest")


def chat_counters_mark(status: dict, chat_declared: bool) -> Dict[str, object]:
    """R5: the chat door's counters as STATUS last wrote them (A4-LADDER-2-PREREG §2 R5 row) — printed, never graded; «not recorded» for a key an
    older body never wrote (never a fabricated 0)."""
    vals = {k: ((status or {})[k] if k in (status or {}) else "not recorded") for k in CHAT_COUNTER_KEYS}
    return {"bar": "printed, no bar", "declared": bool(chat_declared), **vals, "graded": False, "pass": None,
            "reason": "printed, no bar (the chat door's counters)" + ("" if chat_declared else " — CHAT not declared on this life")}
