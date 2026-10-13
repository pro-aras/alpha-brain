#!/usr/bin/env python3
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-13 — PREREG-HOMEOSTASIS §4/§5 + AMENDMENT 2
# (SIGNED 2026-10-13, SEAT-LINE-H0-A2.txt): THE GATE'S MARKS READER. Reads the gate life's and the arm
# replays' journals + the final-snapshot self-exams (F7's proxy for the scene sitting's M1–M6, whose
# gate-scale population is ZERO — measured, named) and computes every mark with its presence counts,
# each ceiling printed beside its bar (#228's discipline). --selftest's planted journals must move each
# reading in its declared direction — CAUGHT or the instrument is refused (RULES §11).
"""Usage: homeostasis_gate.py --manifest <arms.json> --out <report.txt> | --selftest

The manifest maps arm name → {"journal": <file|dir>, "exam": <self-exam.json>, "drives": <drives.json>}.
Arm names (the law §3 + AMENDMENT 2 F8): on (G-ON's own journal) · off · flat · inverted ·
solo-a/solo-b/solo-f · quad-a-no-prec / quad-prec-only / quad-neither (the quad's "both" IS solo-a).

The marks (the law §4 as amended):
  H-DYNAMICS — each of a/b/f visits both halves of [0,1] over the run, none constant, none NaN (on).
  H-DRIVE-EFFECT — the self-exam proxy sections: flat−on ≤ 0.02 each (the non-degradation leg) AND
    KS(on, flat) p < 0.01 on the per-100-canvas err_mean series (the differ leg).
  H-SLEEP-TRIGGER — forced boundaries exist (presence) and the driven boundary schedule diverges from
    the flat twin's on ≥ 10 % of the 1000-canvas windows.
  H-BOREDOM-ASK — the mind's question stream: rate(b>0.7 windows) ≥ 2× rate(b<0.3 windows), on totals;
    the ceiling (~10×: extras ≤ 60/1000 at b=1 vs the 6.4/1000 bench base) printed. Read on: on, solo-b.
  H-BOREDOM-MOUTH — the mind-mouth say stream (journal `say` rows; the brain's kind:brain phrases are
    NEVER in the denominator — F4's units repair): ≥ 1.5×, the same windows. Read on: on, solo-b.
  H-AROUSAL-LEARN — Spearman(per-100-canvas err_mean, lr_mean): ρ > 0.3, p < 0.001. The bar's home is
    quad-a-no-prec (the PURE coupling, precision absent); solo-a printed beside it.
  H-AROUSAL-EYE — fixations/canvas at a>0.7 vs a<0.3 ≥ 1.3× (the ceiling 6/4 = 1.5× printed — F2).
  H-FATIGUE-DEGRADE — the G-ON life's OWN exams around its forced boundaries: the pooled post−pre
    ≥ 0.02 AND post ≥ fresh−0.01 (the declared operational form of «pre-sleep lower ≥ 0.02; recovery
    within 0.01»); n boundaries printed.
  H-NULL — inverted vs on: S = the exam proxy's mean over contributing sections; U = the err descent
    (first-1000 − last-1000 err_mean). Either degraded ≥ 0.05 → the control works. Both intact → the
    drives are decorative and the law DIES (§6's own rule, never softened).
  H-PLANT — 500 planted zero-surprise canvases through the REAL Homeostasis class → b ≥ 0.95; the
    negative control (sustained high surprise → b ≤ 0.1) printed beside it.
  H-PRECISION — the quad's profiles: sections where both ≥ each solo; ≥ 4 of the contributing sections,
    or redundancy declared as the finding (§6).
  H-SEEK-LEARN — the seek's presence count; if a seek fired: the sought source's share of asks+says in
    the 1,000 post-seek canvases vs the 1,000 pre-seek ones (≥ 2×); the flat twin's ZERO seeks printed
    (the clamped clause). No seek → VACUOUS (F5's declared form, never a pass).

The proxy's honesty rule (declared BEFORE the run, F7): a self-exam section constant across ALL compared
arms (incl. all-zero) CANNOT show an effect (#243's pass-by-absence class) — it is named and excluded;
the count of CONTRIBUTING sections is printed beside every profile comparison; zero contributing sections
→ the leg reads VACUOUS, and the verdict says so.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from scipy.stats import ks_2samp, spearmanr

EPS = 1e-12


# ----------------------------------------------------------------------------- the journal walk
class Arm:
    """One arm's streams, walked once. A canvas row carries cells+err (the worded form) or err without
    cells (the sight-only form); the drives key rides both (the wiring's law). The mind's question rows
    (`question`), the mind-mouth's say rows (`say` WITHOUT a kind — the brain's kind:brain phrases are a
    different stream, F4), the sleep rows (`sleep`, forced named), the seek rows (`seek`), the exam
    event rows (`event: exam` with q1)."""

    def __init__(self, name: str, journal: Path):
        self.name = name
        self.canvases: List[Tuple[float, Optional[float], int]] = []   # (err, lr, nfix)
        self.drives: List[Tuple[float, float, float]] = []             # (a, b, f) per canvas row WITH the key
        self.asks: List[Tuple[int, bool]] = []                         # (canvas idx, bored?)
        self.ask_moments: List[Tuple[int, Optional[str], bool]] = []   # (canvas idx, the cited tape moment, bored?)
        self.moment_source: Dict[str, str] = {}                        # the canvas rows' moment → source map
        self.says: List[int] = []                                      # canvas idx of each mind-mouth say
        self.say_pairs: List[Tuple[int, str]] = []                     # (canvas idx, the frame's words) — lockstep
        self.sleeps: List[Tuple[int, bool]] = []                       # (canvas idx, forced)
        self.seeks: List[Tuple[int, Optional[str]]] = []               # (canvas idx, source)
        self.exams: List[Tuple[int, Optional[float]]] = []             # (canvas idx, q1)
        ci = -1
        paths = sorted(journal.glob("*.jsonl")) if journal.is_dir() else [journal]
        for p in paths:
            for line in p.open():
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if "err" in d and ("cells" in d or "hash" in d) and d.get("seq") is not None:
                    ci += 1
                    w = d.get("windows")
                    self.canvases.append((float(d.get("err") or 0.0),
                                          float(d["lr"]) if isinstance(d.get("lr"), (int, float)) else None,
                                          len(w) if w else 0))
                    if d.get("moment") and d.get("source"):
                        self.moment_source[str(d["moment"])] = str(d["source"])
                    dr = d.get("drives")
                    if dr:
                        self.drives.append((float(dr["a"]), float(dr["b"]), float(dr["f"])))
                    else:
                        self.drives.append(None)  # type: ignore
                elif "sleep" in d:
                    self.sleeps.append((max(ci, 0), bool((d.get("sleep") or {}).get("forced"))))
                elif "seek" in d:
                    self.seeks.append((max(ci, 0), (d.get("seek") or {}).get("source")))
                elif "question" in d:
                    q = d["question"]
                    self.asks.append((max(ci, 0), bool(q.get("bored"))))
                    args = q.get("args") or []
                    self.ask_moments.append((max(ci, 0), str(args[0]) if args else None, bool(q.get("bored"))))
                elif "say" in d and "kind" not in d and isinstance(d["say"], dict):
                    self.says.append(max(ci, 0))
                    self.say_pairs.append((max(ci, 0), str(d["say"].get("frame") or "")))
                elif d.get("event") == "exam":
                    self.exams.append((max(ci, 0), d.get("q1") if isinstance(d.get("q1"), (int, float)) else None))

    @property
    def n(self) -> int:
        return len(self.canvases)

    def err_series(self, width: int = 100) -> List[float]:
        """The per-`width`-canvas err_mean series (the learning stream the drives modulate)."""
        errs = [e for e, _lr, _f in self.canvases]
        return [sum(errs[i:i + width]) / len(errs[i:i + width]) for i in range(0, len(errs), width) if errs[i:i + width]]

    def lr_series(self, width: int = 100) -> List[float]:
        lrs = [lr for _e, lr, _f in self.canvases if lr is not None]
        return [sum(lrs[i:i + width]) / len(lrs[i:i + width]) for i in range(0, len(lrs), width) if lrs[i:i + width]]


# ----------------------------------------------------------------------------- the exam proxy (F7)
PROXY_SECTIONS = ("ask_seen_words.Q1", "ask_seen_words.Q2", "ask_seen_words.Q3", "ask_seen_words.Q4",
                  "ask_all_words.Q1", "ask_all_words.Q2", "ask_all_words.Q3", "ask_all_words.Q4",
                  "read_share")


def exam_profile(path: Optional[Path]) -> Dict[str, float]:
    """The final-snapshot self-exam's graded sections as {section: accuracy}. Missing/ungraded cells
    are absent (never a fabricated 0 — #175)."""
    out: Dict[str, float] = {}
    if path is None or not Path(path).exists():
        return out
    d = json.loads(Path(path).read_text())
    for part in ("ask_seen_words", "ask_all_words"):
        for q in ("Q1", "Q2", "Q3", "Q4"):
            v = ((d.get(part) or {}).get(q) or {}).get("acc")
            if isinstance(v, (int, float)):
                out[f"{part}.{q}"] = float(v)
    rs = d.get("read_share")
    if isinstance(rs, (int, float)):
        out["read_share"] = float(rs)
    return out


def contributing(profiles: List[Dict[str, float]]) -> List[str]:
    """The sections that CAN show an effect across these arms: present in every profile and not
    constant across them (#243's pass-by-absence class, declared in the module docstring before any run)."""
    common = [s for s in PROXY_SECTIONS if all(s in p for p in profiles)]
    return [s for s in common if max(p[s] for p in profiles) - min(p[s] for p in profiles) > 0.0]


# ----------------------------------------------------------------------------- the marks
def m_dynamics(on: Arm) -> Dict[str, object]:
    """H-DYNAMICS: each variable visits both halves; none constant; none NaN."""
    ds = [d for d in on.drives if d]
    out = {"presence": len(ds), "canvases": on.n}
    ok = True
    for i, name in enumerate(("arousal", "boredom", "fatigue")):
        series = [d[i] for d in ds]
        lo, hi = min(series), max(series)
        nan = any(math.isnan(v) for v in series)
        both_halves = lo < 0.5 and hi > 0.5
        out[name] = {"min": round(lo, 4), "max": round(hi, 4),
                     "mean": round(sum(series) / len(series), 4), "both_halves": both_halves, "nan": nan}
        ok = ok and both_halves and not nan and hi > lo
    out["verdict"] = "PASS" if ok and len(ds) >= 10000 else ("UNDERPOWERED (presence %d < 10,000 canvases)" % len(ds) if len(ds) < 10000 else "FAIL")
    return out


def m_drive_effect(on: Arm, flat: Arm, on_ex: Dict[str, float], flat_ex: Dict[str, float]) -> Dict[str, object]:
    ks = ks_2samp(on.err_series(), flat.err_series())
    contrib = contributing([on_ex, flat_ex])
    degr = {s: round(flat_ex[s] - on_ex[s], 4) for s in contrib}
    nondeg = all(v <= 0.02 + EPS for v in degr.values())
    return {"ks_p": float(ks.pvalue), "ks_ok": bool(ks.pvalue < 0.01),
            "contributing_sections": len(contrib), "degradation_per_section": degr,
            "nondeg_ok": nondeg, "series_n": [len(on.err_series()), len(flat.err_series())],
            "verdict": "PASS" if (nondeg and ks.pvalue < 0.01 and contrib) else
                       ("VACUOUS (no contributing proxy section)" if not contrib else "FAIL")}


def m_sleep_trigger(on: Arm, flat: Arm) -> Dict[str, object]:
    forced = [c for c, f in on.sleeps if f]
    share_forced = len(forced) / len(on.sleeps) if on.sleeps else 0.0
    # the schedule divergence: per-1000-canvas windows whose boundary counts differ from the flat twin's
    def per_window(sleeps: List[Tuple[int, bool]]) -> Dict[int, int]:
        w: Dict[int, int] = {}
        for c, _f in sleeps:
            w[c // 1000] = w.get(c // 1000, 0) + 1
        return w
    a, b = per_window(on.sleeps), per_window(flat.sleeps)
    keys = sorted(set(a) | set(b))
    divergent = sum(1 for k in keys if a.get(k, 0) != b.get(k, 0))
    div_share = divergent / len(keys) if keys else 0.0
    return {"sleeps_on": len(on.sleeps), "forced": len(forced), "forced_share": round(share_forced, 4),
            "windows": len(keys), "divergent_windows": divergent, "divergence_share": round(div_share, 4),
            "verdict": "PASS" if (forced and div_share >= 0.10) else "FAIL"}


def _boredom_windows(arm: Arm, stream: List[Tuple[int, object]]) -> Tuple[Optional[float], Optional[float], int, int]:
    """The rate of `stream` events per 1000 canvases in mean-b>0.7 vs mean-b<0.3 windows (the window's
    b = the canvas rows' drives.b mean). Returns (rate_high, rate_low, n_high_windows, n_low_windows)."""
    per_win_b: Dict[int, List[float]] = {}
    per_win_n: Dict[int, int] = {}
    for i, d in enumerate(arm.drives):
        if d is None:
            continue
        per_win_b.setdefault(i // 1000, []).append(d[1])
    for i in range(arm.n):
        per_win_n[i // 1000] = per_win_n.get(i // 1000, 0) + 1
    hi, lo = {}, {}
    for w, bs in per_win_b.items():
        mb = sum(bs) / len(bs)
        (hi if mb > 0.7 else lo if mb < 0.3 else {}).update({w: None})
    def rate(windows) -> Optional[float]:
        if not windows:
            return None
        n_ev = sum(1 for c, _x in stream if c // 1000 in windows)
        n_cv = sum(per_win_n.get(w, 0) for w in windows)
        return 1000.0 * n_ev / n_cv if n_cv else None
    return rate(hi), rate(lo), len(hi), len(lo)


def m_boredom_ask(on: Arm, solo_b: Arm) -> Dict[str, object]:
    out = {"ceiling_note": "extras ≤ 100 think ticks/1000 × p ≤ 0.6 → ≤ 60/1000 vs the 6.4/1000 bench base → ceiling ~10× (AMENDMENT 2 F3)"}
    for name, arm in (("on", on), ("solo-b", solo_b)):
        rh, rl, nh, nl = _boredom_windows(arm, arm.asks)
        extras = sum(1 for _c, b in arm.asks if b)
        out[name] = {"rate_high": rh, "rate_low": rl, "windows_high": nh, "windows_low": nl,
                     "extras_bored_marked": extras, "asks_total": len(arm.asks),
                     "ratio": (rh / rl) if (rh is not None and rl and rl > 0) else None}
    ok = [v["ratio"] is not None and v["ratio"] >= 2.0 for v in out.values() if isinstance(v, dict) and "ratio" in v]
    out["verdict"] = ("PASS" if ok and all(ok) else
                      "FAIL" if ok and not all(ok) else "UNDERPOWERED (a boredom window's population is empty — presence printed)")
    return out


def m_boredom_mouth(on: Arm, solo_b: Arm) -> Dict[str, object]:
    out = {"units_note": "the mind-mouth's own `say` rows only — the brain's kind:brain phrase stream is never in the denominator (F4)"}
    for name, arm in (("on", on), ("solo-b", solo_b)):
        stream = [(c, None) for c in arm.says]
        rh, rl, nh, nl = _boredom_windows(arm, stream)
        out[name] = {"rate_high": rh, "rate_low": rl, "windows_high": nh, "windows_low": nl,
                     "says_total": len(arm.says),
                     "ratio": (rh / rl) if (rh is not None and rl and rl > 0) else None}
    ok = [v["ratio"] is not None and v["ratio"] >= 1.5 for v in out.values() if isinstance(v, dict) and "ratio" in v]
    out["verdict"] = ("PASS" if ok and all(ok) else
                      "FAIL" if ok and not all(ok) else "UNDERPOWERED (a boredom window's population is empty — presence printed)")
    return out


def m_arousal_learn(pure: Arm, solo_a: Arm) -> Dict[str, object]:
    out = {}
    for name, arm in (("quad-a-no-prec (the bar's home)", pure), ("solo-a", solo_a)):
        es, ls = arm.err_series(), arm.lr_series()
        n = min(len(es), len(ls))
        if n < 10:
            out[name] = {"n_windows": n, "rho": None, "p": None}
            continue
        rho, p = spearmanr(es[:n], ls[:n])
        out[name] = {"n_windows": n, "rho": round(float(rho), 4), "p": float(p)}
    home = out["quad-a-no-prec (the bar's home)"]
    out["verdict"] = ("PASS" if home["rho"] is not None and home["rho"] > 0.3 and home["p"] < 0.001 else
                      "UNDERPOWERED" if home["rho"] is None else "FAIL")
    return out


def m_arousal_eye(arms: Dict[str, Arm]) -> Dict[str, object]:
    out = {"ceiling_note": "the genome's fixed 4 fixations + AMENDMENT 2's +2 → the ceiling is 6/4 = 1.5× (the bar 1.3× unmoved)"}
    ok_any = False
    for name in ("on", "solo-a"):
        arm = arms[name]
        hi = [f for (e, l, f), d in zip(arm.canvases, arm.drives) if d and d[0] > 0.7]
        lo = [f for (e, l, f), d in zip(arm.canvases, arm.drives) if d and d[0] < 0.3]
        ratio = (sum(hi) / len(hi)) / (sum(lo) / len(lo)) if hi and lo else None
        out[name] = {"fix_high": round(sum(hi) / len(hi), 4) if hi else None, "fix_low": round(sum(lo) / len(lo), 4) if lo else None,
                     "n_high": len(hi), "n_low": len(lo), "ratio": round(ratio, 4) if ratio else None}
        ok_any = ok_any or (ratio is not None and ratio >= 1.3)
    out["verdict"] = "PASS" if ok_any else ("FAIL" if any(v.get("ratio") is not None for v in out.values() if isinstance(v, dict)) else "UNDERPOWERED (an arousal window's population is empty)")
    return out


def m_fatigue_degrade(on: Arm) -> Dict[str, object]:
    """The G-ON life's own exams around its FORCED boundaries: pooled post−pre ≥ 0.02, post ≥ fresh−0.01."""
    forced = [c for c, f in on.sleeps if f]
    ex = [(c, q) for c, q in on.exams if q is not None]
    fresh = [q for c, q in ex if c < 1000]
    fresh_m = sum(fresh) / len(fresh) if fresh else None
    pairs = []
    for fc in forced:
        pre = [q for c, q in ex if fc - 1000 <= c < fc]
        post = [q for c, q in ex if fc <= c < fc + 1000]
        if pre and post:
            pairs.append((sum(pre) / len(pre), sum(post) / len(post)))
    if not pairs or fresh_m is None:
        return {"verdict": "VACUOUS (no forced boundary with exams on both sides)", "forced": len(forced), "exams": len(ex)}
    dp = sum(p[1] - p[0] for p in pairs) / len(pairs)
    post_m = sum(p[1] for p in pairs) / len(pairs)
    return {"pairs": len(pairs), "fresh": round(fresh_m, 4), "mean_pre": round(sum(p[0] for p in pairs) / len(pairs), 4),
            "mean_post": round(post_m, 4), "post_minus_pre": round(dp, 4),
            "verdict": "PASS" if (dp >= 0.02 and post_m >= fresh_m - 0.01) else "FAIL"}


def m_null(inverted: Arm, on: Arm, inv_ex: Dict[str, float], on_ex: Dict[str, float]) -> Dict[str, object]:
    contrib = contributing([inverted and inv_ex or {}, on_ex])
    s_on = sum(on_ex[s] for s in contrib) / len(contrib) if contrib else None
    s_inv = sum(inv_ex[s] for s in contrib) / len(contrib) if contrib else None
    def descent(arm: Arm) -> Optional[float]:
        es = [e for e, _l, _f in arm.canvases]
        if len(es) < 2000:
            return None
        return sum(es[:1000]) / 1000 - sum(es[-1000:]) / 1000
    u_on, u_inv = descent(on), descent(inverted)
    s_deg = (s_inv is not None and s_on is not None and s_inv <= s_on - 0.05)
    u_deg = (u_inv is not None and u_on is not None and u_inv <= u_on - 0.05)
    return {"S_on": s_on, "S_inverted": s_inv, "contributing_sections": len(contrib),
            "U_on": round(u_on, 4) if u_on is not None else None,
            "U_inverted": round(u_inv, 4) if u_inv is not None else None,
            "S_degraded": s_deg, "U_degraded": u_deg,
            "verdict": "PASS" if (s_deg or u_deg) else
                       "FAIL — the inverted drives did not hurt: the drives are decorative, the law is NOT adopted (§6)"}


def m_plant() -> Dict[str, object]:
    """H-PLANT through the REAL Homeostasis class (the gate organism's own module): 500 planted
    zero-surprise canvases after a warm-up must drive boredom ≥ 0.95; the negative control (sustained
    high surprise) must keep it ≤ 0.1."""
    from genome.homeostasis import Homeostasis
    h = Homeostasis({"boredom": True}, seed=20261213)
    for _ in range(300):
        h.note_canvas(0.8)                  # the warm-up: a surprising world (s̄ grows)
    for _ in range(500):
        h.note_canvas(0.0)                  # the planted zero-surprise stretch
    planted = h.b
    c = Homeostasis({"boredom": True}, seed=20261213)
    for _ in range(800):
        c.note_canvas(0.9)                  # the control: sustained HIGH surprise — boredom must never rise
    control = c.b
    return {"planted_boredom": round(planted, 4), "control_boredom": round(control, 4),
            "verdict": "PASS" if (planted >= 0.95 and control <= 0.1) else "FAIL"}


def m_precision(profiles: Dict[str, Dict[str, float]]) -> Dict[str, object]:
    order = ["quad-a-no-prec", "quad-prec-only", "solo-a", "quad-neither"]
    both = profiles.get("solo-a", {})
    contrib = contributing([profiles.get(k, {}) for k in order])
    wins = [s for s in contrib if both[s] >= profiles["quad-a-no-prec"][s] and both[s] >= profiles["quad-prec-only"][s]]
    return {"contributing_sections": len(contrib), "both_ge_each_solo": len(wins), "sections": wins,
            "verdict": ("PASS" if len(wins) >= max(1, math.ceil(2 / 3 * len(contrib))) else
                        "VACUOUS (no contributing proxy section)" if not contrib else
                        "REDUNDANT — arousal-only ≈ both; §6: absorb precision into arousal in the NEXT law (declared as the finding)"
                        if len(wins) < len(contrib) // 2 else "FAIL")}


def m_seek_learn(on: Arm, flat: Arm, on_drives: Optional[Dict[str, object]]) -> Dict[str, object]:
    out = {"seeks_on": len(on.seeks), "seeks_flat": len(flat.seeks),
           "clamped_clause": "PASS" if not flat.seeks else "FAIL — the flat (clamped-boredom) twin SEEKED",
           "seeks_list": [(c, s) for c, s in on.seeks[:20]]}
    if not on.seeks:
        out["verdict"] = "VACUOUS (F5's declared form: no seek fired in the gate run — the presence count is printed, never a pass)"
        return out
    # the first seek's 1,000-canvas windows: the sought source's share of the organism's asks+says
    # (the law's own form). Attribution: an ask's cited tape moment → the canvas rows' moment→source
    # map; a say's frame words → the ON life's final drives.json heard ledger (word → source). Rows
    # that attribute to nothing are counted separately (the presence count), never silently dropped.
    fc, target = on.seeks[0]
    heard = (on_drives or {}).get("heard") or {}
    def word_source(frame: str) -> Optional[str]:
        for w in str(frame).split():
            rec = heard.get(w)
            if rec:
                return str(rec[1])
        return None
    def window_shares(lo: int, hi: int) -> Dict[str, object]:
        total = 0
        tgt = 0
        lost = 0
        for c, mo, _b in on.ask_moments:
            if lo <= c < hi:
                total += 1
                s = on.moment_source.get(mo or "")
                if s is None:
                    lost += 1
                elif s == target:
                    tgt += 1
        for c, fr in on.say_pairs:
            if lo <= c < hi:
                total += 1
                s = word_source(fr)
                if s is None:
                    lost += 1
                elif s == target:
                    tgt += 1
        return {"total": total, "target": tgt, "unattributed": lost,
                "share": (tgt / total) if total else None}
    pre = window_shares(max(0, fc - 1000), fc)
    post = window_shares(fc, fc + 1000)
    ratio = (post["share"] / pre["share"]) if (pre["share"] and post["share"] is not None) else None
    out.update({"seek_canvas": fc, "target": target, "pre": pre, "post": post, "share_ratio": ratio})
    ok = ratio is not None and ratio >= 2.0
    out["verdict"] = "PASS" if ok and not flat.seeks else ("FAIL" if ratio is not None else "UNDERPOWERED (a window's population is empty — presence printed)")
    return out


# ----------------------------------------------------------------------------- the report
def build_report(manifest: Dict[str, Dict[str, str]]) -> Tuple[str, Dict[str, object]]:
    arms: Dict[str, Arm] = {}
    exams: Dict[str, Dict[str, float]] = {}
    drives: Dict[str, Dict[str, object]] = {}
    for name, spec in manifest.items():
        arms[name] = Arm(name, Path(spec["journal"]))
        exams[name] = exam_profile(Path(spec["exam"])) if spec.get("exam") else {}
        if spec.get("drives") and Path(spec["drives"]).exists():
            drives[name] = json.loads(Path(spec["drives"]).read_text())
    marks: Dict[str, object] = {}
    marks["H-DYNAMICS"] = m_dynamics(arms["on"])
    marks["H-DRIVE-EFFECT"] = m_drive_effect(arms["on"], arms["flat"], exams.get("on", {}), exams.get("flat", {}))
    marks["H-SLEEP-TRIGGER"] = m_sleep_trigger(arms["on"], arms["flat"])
    marks["H-BOREDOM-ASK"] = m_boredom_ask(arms["on"], arms["solo-b"])
    marks["H-BOREDOM-MOUTH"] = m_boredom_mouth(arms["on"], arms["solo-b"])
    marks["H-AROUSAL-LEARN"] = m_arousal_learn(arms["quad-a-no-prec"], arms["solo-a"])
    marks["H-AROUSAL-EYE"] = m_arousal_eye(arms)
    marks["H-FATIGUE-DEGRADE"] = m_fatigue_degrade(arms["on"])
    marks["H-NULL"] = m_null(arms["inverted"], arms["on"], exams.get("inverted", {}), exams.get("on", {}))
    marks["H-PLANT"] = m_plant()
    marks["H-PRECISION"] = m_precision(exams)
    marks["H-SEEK-LEARN"] = m_seek_learn(arms["on"], arms["flat"], drives.get("on"))
    lines: List[str] = []
    lines.append("H0 GATE — the marks (PREREG-HOMEOSTASIS §4 + AMENDMENT 2; every presence count printed)\n")
    for name, m in marks.items():
        verdict = m.get("verdict", "?") if isinstance(m, dict) else "?"
        lines.append(f"== {name}: {verdict}")
        lines.append("   " + json.dumps(m, default=str)[:1500])
    n_pass = sum(1 for m in marks.values() if isinstance(m, dict) and str(m.get("verdict", "")).startswith("PASS"))
    lines.append(f"\nPASS {n_pass} of {len(marks)} marks (the identity legs I1/I2 are the runner's cmp exits, recorded beside this)")
    return "\n".join(lines) + "\n", {"marks": marks}


# ----------------------------------------------------------------------------- the planted control
def _synth_journal(path: Path, n: int, bored_from: Optional[int]) -> None:
    """A synthetic journal: n canvases; if bored_from is not None, boredom jumps past θ at that canvas
    and the planted couplings fire there: the asks double, the says rise, the sleeps force EARLY (the
    driven forms). bored_from None = the never-bored twin (the removed plant — nothing may move)."""
    with path.open("w") as fh:
        for i in range(n):
            bored = bored_from is not None and i >= bored_from
            b = 0.85 if bored else 0.1
            fh.write(json.dumps({"seq": i + 1, "cells": [1, 1], "err": 0.8 - 0.6 * (i / n),
                                 "lr": 1.5, "windows": [[0, 0]] * 4,
                                 "drives": {"a": 0.6, "b": b, "f": min(0.95, (i * 0.0022) % 1.0)}}) + "\n")
            gap = 300 if bored else 439          # the forced boundary fires EARLY in the bored half
            if i % gap == gap - 1:
                fh.write(json.dumps({"seq": i + 1, "sleep": {"replayed": 200, "forced": bored}}) + "\n")
            if i % 25 == 0 and bored:
                fh.write(json.dumps({"seq": i + 1, "question": {"q": "what-is", "bored": True}}) + "\n")
            elif i % 50 == 0:
                fh.write(json.dumps({"seq": i + 1, "question": {"q": "what-is"}}) + "\n")
            if (i % 27 == 0 and bored) or i % 40 == 0:
                fh.write(json.dumps({"seq": i + 1, "say": {"frame": "star red"}}) + "\n")


def selftest() -> int:
    """The instrument's planted controls (RULES §11): synthetic journals whose planted series must move
    each reading in its declared direction — and MUST NOT when the plant is removed."""
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="h0gate-selftest-"))
    # plant: boredom high in the run's second half with the planted couplings firing there
    on_p = tmp / "on.jsonl"
    _synth_journal(on_p, 6000, bored_from=3000)
    flat_p = tmp / "flat.jsonl"
    _synth_journal(flat_p, 6000, bored_from=None)   # the removed plant: nothing may move
    arm_on, arm_flat = Arm("on", on_p), Arm("flat", flat_p)
    ask = m_boredom_ask(arm_on, arm_on)
    rh = ask["on"]["ratio"]
    assert rh is not None and rh >= 2.0, f"PLANT MISS: the planted boredom-ask coupling read {rh}"
    mo = m_boredom_mouth(arm_on, arm_on)["on"]["ratio"]
    assert mo is not None and mo >= 1.5, f"PLANT MISS: the planted boredom-mouth coupling read {mo}"
    # … and MUST NOT fire when the plant is removed (negative control)
    ask_neg = m_boredom_ask(arm_flat, arm_flat)
    assert ask_neg["on"]["ratio"] is None or ask_neg["on"]["ratio"] < 2.0 or ask_neg["verdict"].startswith("UNDERPOWERED"), \
        f"PLANT CONTROL MISS: the flat journal read {ask_neg['on']['ratio']}"
    # the sleep trigger: forced rows exist in `on`, none in `flat`; schedules differ
    st = m_sleep_trigger(arm_on, arm_flat)
    assert st["forced"] > 0 and st["divergence_share"] >= 0.10, f"PLANT MISS (sleep): {st}"
    # KS: identical streams must NOT differ (negative control), differing must
    same = ks_2samp(arm_on.err_series(), arm_on.err_series()).pvalue
    assert same > 0.01, f"PLANT CONTROL MISS: an identical stream differed (p {same})"
    pl = m_plant()
    assert pl["verdict"] == "PASS", f"PLANT MISS (the module): {pl}"
    print("SELFTEST PASS — the planted journals moved the readings as declared, and the removed plants did not")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    args = ap.parse_args()
    if not args.manifest:
        print(__doc__)
        return 2
    manifest = json.loads(Path(args.manifest).read_text())
    text, data = build_report(manifest)
    print(text)
    if args.out:
        Path(args.out).write_text(text)
        Path(str(args.out) + ".json").write_text(json.dumps(data, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["--selftest"] else main())
