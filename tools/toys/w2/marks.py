"""tools/toys/w2/marks.py — PREREG-W2 §5: the TRUTH/DELIVERY family's readers (M-TRUE, M-ATTRIB, M-JOINT, M-SELFVOICE,
M-CONTINGENT (i)) and M-PURE — each figure with its n and presence counts.

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 03:19 +0400 — new file; law
docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §5. Truth is re-derived from the RECORD (the truth specs, the fixation
record, the states), never from the generator's own claim — the LYING MENTOR is caught by that, by construction.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

from brain.world.seeds import substream
from creature.senses import mentor as M
from tools.toys.w2 import key as K
from tools.toys.w2 import sweep as SW
from tools.toys.w2.record import SceneCanvas
from tools.toys.w2.stream import BenchStream, words_of

STATE_TPL_FLAG = {"M-M1": "doubt", "M-M2": "young", "M-M3": "ask_prev"}
ANSWER_TPLS = ("M-A1", "M-A2", "M-A3")


def _np_match(things: Sequence[M.Thing], npw: Sequence[str]) -> List[int]:
    return [i for i, t in enumerate(things) if all(M.word_true_of(w, t) for w in npw)]


def m_true(canvases: Sequence[SceneCanvas], stream: BenchStream, lo: int = 250) -> Dict[str, object]:
    """Every mentor production TRUE against the record: carriers vs the truth specs with the polarity rule; mirror
    tokens vs the states; answers per their rule. first_false names the first lying row (the LYING MENTOR's catch)."""
    n_rows = 0
    per_tpl: Dict[str, int] = {}
    first_false = None
    n_checked = 0
    for pos, c in enumerate(canvases):
        rows = stream.mentor_rows[pos] if pos < len(stream.mentor_rows) else []
        if not rows:
            continue
        prods = M.productions(rows)
        tpls = [r["meta"]["tpl"] for r in rows]
        # one tpl per production (the rows of one production share it)
        k = 0
        for p in prods:
            tpl = tpls[k]
            k += len(p)
            n_rows += len(p)
            per_tpl[tpl] = per_tpl.get(tpl, 0) + 1
            parsed = K.parse(p, tpl)
            n_checked += 1
            if parsed is None:
                if first_false is None:
                    first_false = {"moment": c.moment, "tpl": tpl, "reason": "UNPARSEABLE", "production": p}
                continue
            s = stream.states[pos]
            if parsed["verb"] == "mirror":
                flag = STATE_TPL_FLAG[tpl]
                ok = bool(s[{"doubt": 0, "young": 1, "ask_prev": 2}[flag]])
                if not ok and first_false is None:
                    first_false = {"moment": c.moment, "tpl": tpl, "reason": f"the mirror token is false ({flag} {s})", "production": p}
            elif parsed["polarity"] == "+":
                npw = parsed["np"]
                if tpl == "M-A3":
                    at = stream.utterances[pos].get("ask_target")
                    ok = at is not None and all(M.word_true_of(w, c.things[at]) for w in npw)
                    reason = "the answer does not name the asked thing"
                else:
                    hits = [M.fixation_hits(t, c.fix) for t in c.things]
                    best = max(hits, default=0)
                    tied = [i for i, n in enumerate(hits) if n == best and n > 0]
                    ok = bool(tied) and any(all(M.word_true_of(w, c.things[i]) for w in npw) for i in tied)
                    reason = "the named thing is not the fixated referent"
                if not ok and first_false is None:
                    first_false = {"moment": c.moment, "tpl": tpl, "reason": reason, "production": p}
            else:
                in_spec = bool(_np_match(c.things, parsed["np"]))
                seen = any(all(M.word_true_of(w, t) for w in parsed["np"]) and M.fixation_hits(t, c.fix) >= 1
                           for t in c.things)
                ok = in_spec and not seen
                if not ok and first_false is None:
                    first_false = {"moment": c.moment, "tpl": tpl, "reason": "the «does not see» claim is false", "production": p}
    return {"mark": "M-TRUE", "pass": first_false is None, "n_rows": n_rows, "n_productions": n_checked,
            "per_tpl": per_tpl, "first_false": first_false}


def m_attrib(canvases: Sequence[SceneCanvas], stream: BenchStream, lo: int = 250) -> Dict[str, object]:
    """Every mentor row carries source + a v1 tpl; the key parses every production; the coverage pair."""
    n_rows = n_bad_source = n_bad_tpl = n_unparseable = 0
    sayable = {"referent": 0, "unseen": 0, "state": 0, "say_or_ask": 0}
    spoke = 0
    sayable_n = 0
    for pos, c in enumerate(canvases):
        rows = stream.mentor_rows[pos] if pos < len(stream.mentor_rows) else []
        for r in rows:
            n_rows += 1
            n_bad_source += int(r["meta"].get("source") != "mentor")
            n_bad_tpl += int(r["meta"].get("tpl") not in M.TEMPLATES_V1)
        tpls = [r["meta"]["tpl"] for r in rows]
        k = 0
        for p in M.productions(rows):
            tpl = tpls[k] if k < len(tpls) else None
            k += len(p)
            if K.parse(p, tpl) is None:
                n_unparseable += 1
        has_ref = any(M.fixation_hits(t, c.fix) >= 1 for t in c.things)
        has_unseen = any(M.fixation_hits(t, c.fix) == 0 for t in c.things)
        s = stream.states[pos]
        has_state = bool(s[0] or s[1] or s[2])
        has_sa = bool(c.turn.get("say") is not None or c.turn.get("ask") is not None)
        sayable["referent"] += has_ref
        sayable["unseen"] += has_unseen
        sayable["state"] += has_state
        sayable["say_or_ask"] += has_sa
        if has_ref or has_unseen or has_state or has_sa:
            sayable_n += 1
            spoke += bool(rows)
    cover = (spoke / sayable_n) if sayable_n else float("nan")
    return {"mark": "M-ATTRIB", "pass": n_bad_source == 0 and n_bad_tpl == 0 and n_unparseable == 0 and cover >= 0.90,
            "n_rows": n_rows, "n_bad_source": n_bad_source, "n_bad_tpl": n_bad_tpl, "n_unparseable": n_unparseable,
            "coverage": {"sayable": sayable_n, "spoke": spoke, "share": cover, "classes": sayable}}


def m_joint(canvases: Sequence[SceneCanvas], stream: BenchStream, seed: int, k: int = 100) -> Dict[str, object]:
    """M-JOINT: the attended share of C1/C3 referents vs the dealt-uniform null (anchors 0.896 / 0.655 printed).
    The null's 100 draws are SLICE-WIDE: each re-picks every C1/C3 canvas's referent uniformly among its things and the
    attended share over the slice is recomputed (the law's dealt-uniform form)."""
    n_rows = attended = 0
    cells_of: List[tuple] = []                                        # (canvas position, things, fix)
    for pos, c in enumerate(canvases):
        rows = stream.mentor_rows[pos] if pos < len(stream.mentor_rows) else []
        prods = [p for p in M.productions(rows) if len(p) >= 3 and p[0] == "alpha" and p[1] == "sees"]
        if not prods:
            continue
        for p in prods:
            cand = _np_match(c.things, p[2:])
            if len(cand) != 1:
                continue
            n_rows += 1
            attended += int(M.fixation_hits(c.things[cand[0]], c.fix) >= 1)
            cells_of.append((pos, c.things, c.fix))
    null_shares = []
    for kk in range(1, k + 1):
        rng = substream(seed, f"w2:joint-null:{kk}")
        hits = 0
        for pos, things, fix in cells_of:
            i = int(rng.integers(len(things)))
            hits += int(M.fixation_hits(things[i], fix) >= 1)
        null_shares.append(hits / len(cells_of) if cells_of else float("nan"))
    share = (attended / n_rows) if n_rows else float("nan")
    q95 = float(np.quantile(np.asarray(null_shares), 0.95)) if null_shares else float("nan")
    mean_null = float(np.mean(null_shares)) if null_shares else float("nan")
    return {"mark": "M-JOINT", "pass": bool(share == share and share >= 0.99 and (not null_shares or share > q95)),
            "n_rows": n_rows, "attended": attended, "share": share,
            "null": {"k": k, "mean": mean_null, "q95": q95, "anchors": {"named_thing_seen": 0.896, "say_about_parent": 0.655}}}


def m_selfvoice(tape_rows: Sequence[dict], canvases: Sequence[SceneCanvas], stream: BenchStream) -> Dict[str, object]:
    """No ear row's source is a self-source; every answer is built from its referent (never the say's words)."""
    n_rows = 0
    n_self = 0
    sources: Dict[str, int] = {}
    for r in tape_rows:
        if r.get("sense") != "ear":
            continue
        n_rows += 1
        src = (r.get("meta") or {}).get("source")
        sources[src] = sources.get(src, 0) + 1
        if src in ("voice", "say", "brain"):
            n_self += 1
    n_answers = n_bad = 0
    for pos, c in enumerate(canvases):
        rows = stream.mentor_rows[pos] if pos < len(stream.mentor_rows) else []
        tpls = [r["meta"]["tpl"] for r in rows]
        k = 0
        for p in M.productions(rows):
            tpl = tpls[k] if k < len(tpls) else None
            k += len(p)
            if tpl not in ANSWER_TPLS:
                continue
            n_answers += 1
            if tpl == "M-A3":
                at = stream.utterances[pos].get("ask_target")
                thing = c.things[at] if at is not None else None
            else:
                ref = stream.referents[pos]
                thing = c.things[ref] if ref is not None else None
            if thing is None:
                continue
            allowed = {thing.shape, thing.colour, thing.size, "alpha", "sees"}
            if not all(w in allowed for w in p):
                n_bad += 1
    return {"mark": "M-SELFVOICE", "pass": n_self == 0 and n_bad == 0, "n_ear_rows": n_rows,
            "n_self_source": n_self, "sources": sources, "n_answers": n_answers, "n_answer_rows_off_referent": n_bad}


def m_contingent_i(canvases: Sequence[SceneCanvas], stream: BenchStream) -> Dict[str, object]:
    """Every mirror token lands on its state's OWN canvas (unsure iff doubt, fresh iff young, asked iff ask_prev)."""
    n_tok = n_ok = 0
    for pos, u in enumerate(stream.utterances):
        s = stream.states[pos]
        for w in u["mirror"]:
            n_tok += 1
            ok = (w == "unsure" and s[0]) or (w == "fresh" and s[1]) or (w == "asked" and s[2])
            n_ok += int(bool(ok))
    return {"mark": "M-CONTINGENT (i)", "pass": n_tok == n_ok, "n_tokens": n_tok, "n_aligned": n_ok}


def m_pure() -> Dict[str, object]:
    from pathlib import Path
    found = SW.sweep(Path("creature/senses/mentor.py")) + SW.sweep(Path("tools/toys/w2"))
    return {"mark": "M-PURE", "pass": not found, "findings": found}
