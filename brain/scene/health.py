"""health.py — T-MEM-2 «METACOGNITION DECIDES» (PREREG-TMEM2, final 4d03f79, sha b785b54f…; CONCLUSION-MEMORY §4 T-MEM-2):
the per-word HEALTH row, kept WITHOUT the world, and the road whose `sayable` consults it.

edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:30 +0400 — new module.
edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:18 +0400 — PREREG-TMEM2 AMENDMENT 1 (final a7dceea, sha 6da8ff67…): a claim is
graded ONLY IF the said word's own band holds the thing it is attributed to; otherwise UNGRADED «about a thing I did not see»,
counted under the claimed word (the row's `unseen`); the claim record carries the held words it was made from.
edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 18:43 +0400 — PREREG-TMEM2 AMENDMENT 2 (final b1e2b15, sha 76d8ac86…) REPLACES
AMENDMENT 1's rule: «a thing I did not see» is the learner's own M2a «none» (heard_none: the LAW road's pointing for the
parent's phrase over the scene's seen hypotheses, τ_point, before train_scene); when it fires, every claim the phrase would
grade is set aside (grades(..., set_aside=True)). No band rule; the held words stay in the claim record, read by no rule.

THE FENCE: like learners.py this module imports numpy, math, typing and brain.scene.learners only — never the world, the
cache's reader of scene specs or the graders (tests/brain/scene/test_truth_fence.py). What the law grades AGAINST the world —
the row's offline ceiling (the same claims graded at the scene's referent) and the oracle's per-word accuracies — is
computed by run_tmem2.py and reaches this module only as plain arguments (an index, a number per word).

  claims()       §2 A CLAIM, read-only, before the parent's phrase: the LAW road's own step 1 — per learned type the believed
                 name of every hypothesis, and whether it is CONFIDENT (the band holds it).
  attribution()  §2 the learner's OWN attribution of each said word, read-only, after train_scene (h* = the argmax of the
                 responsibilities it just stored; the episodic write's thing for a word's first meeting).
  grades()       ITS GRADE, FILED UNDER THE CLAIMED WORD (the co-signed edit): (b_T(h*), confirmed, the said word) — or, by
                 AMENDMENT 2, when the phrase's «none» fired, (b_T(h*), None, the said word): set aside, «unseen».
  heard_none()   AMENDMENT 2: the learner's own «this phrase fits nothing I see» — the LAW road's M2a pointing, read-only.
  HealthRow      one word's row: n_claims, its graded outcomes in order, cal_20 (the last 20 graded), the consecutive
                 20-claim windows, Δ, median |Δ|, the drift READING in both forms; the said word's MISSED count apart.
  HealthBook     the rows of every word, fed claims and grades.
  row_gate()     the gate (§3): n_graded ≥ 20 AND cal_20 ≥ 0.80 → open; else «no row» / «not held lately».
  book_gate(), accuracy_gate()   a road's gate: from a book (own rows, or deranged rows — the null), or from per-word
                 accuracies (the oracle's).
  HealthRoad     the LAW road (RWRoad) with ONE difference in `sayable`: the band AND the gate; the refused words recorded.
  derange()      the null's derangement over the trained words (no word keeps its own row).
  ece(), auroc() the offline graders of a row's confidence against a correctness the CALLER supplies.
  row_toy()      THE FIRST GATE step 2's toy.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import learners as Lr

WINDOW = 20                 # cal_20 over the last 20 graded claims; Δ over consecutive 20-claim windows
GATE_N = 20                 # the gate: n_graded ≥ 20 …
GATE_CAL = 0.80             # … AND cal_20 ≥ 0.80
DRIFT_K = 2.0               # the drift READING: Δ ≥ −2 × median |Δ| (out of the gate on this stationary world)
DRIFT_FLOOR = 1.0 / WINDOW  # its alternative form: the median floored at 1/20 (printed beside)
REASON_NO_ROW = "no row"
REASON_NOT_HELD = "not held lately"
REASON_UNSEEN = "about a thing I did not see"   # AMENDMENT 1: a claim set aside — the said word does not fit the thing


# ------------------------------------------------------------------------------------------------ a claim and its grade
def claims(road: "Lr.RWRoad", X: np.ndarray) -> Dict[str, object]:
    """§2 A CLAIM, read-only, BEFORE the parent's phrase is heard: the LAW road's own step 1 on the scene's hypotheses — per
    learned type T (the road's types: the ear's cover at the last reading point), the believed name b_T(h) of every
    hypothesis h (`RWRoad.believed`) and whether it is CONFIDENT (`RWRoad.sayable` ≡ the word is among the hypothesis's
    held words; the held words are read once per hypothesis). Nothing is written. AMENDMENT 1: the record carries those held
    words per hypothesis (sorted) — the band's own «what is this?»; AMENDMENT 2 replaced the rule that read them, and the
    record keeps them, read by no rule."""
    X = np.atleast_2d(X)
    types = [tuple(t) for t in road.types()]
    believed = road.believed(X)
    held = [set(road.held_words(X[h])) for h in range(X.shape[0])]
    confident = [[believed[k][h] is not None and believed[k][h] in held[h] for h in range(X.shape[0])]
                 for k in range(len(types))]
    return {"types": types, "believed": believed, "confident": confident, "held": [tuple(sorted(s)) for s in held]}


def heard_none(road: "Lr.RWRoad", X: np.ndarray, phrase: Sequence[str], rng: np.random.Generator) -> Dict[str, object]:
    """AMENDMENT 2 §2 — the learner's own «this phrase fits nothing I see», read-only, after the parent's phrase is heard and
    BEFORE train_scene: the LAW road's pointing for the phrase over the scene's SEEN hypotheses, exactly as M2a asks it
    (`RWRoad.answer_point`: the best Σ log p_w over the things, «none» = S1a's τ_point rule, S1b-1R's none_i, under the current
    state). `none` is True / False; None when a word of the phrase was never heard (no pointing — nothing is set aside)."""
    a = road.answer_point(np.atleast_2d(X), list(phrase), rng)
    none = a.get("none") if a.get("point") is not None else None
    return {"none": None if none is None else bool(none), "best": a.get("best"), "unheard": a.get("unheard")}


def attribution(L: "Lr.RWLearner", raw: np.ndarray, words: Sequence[str], new: Sequence[str]) -> Dict[str, Optional[int]]:
    """§2 the learner's OWN attribution of each said word, read AFTER train_scene: h* = the argmax of the responsibilities the
    delta rule just stored (`store_r[j][-1]`; a tie → the first hypothesis); for a word met for the FIRST time (`new`: the
    episodic write), its thing t_star = the hypothesis whose standardised input equals the row the write stored (the inputs
    re-standardised by the statistics train_scene just observed — the Z it used). None when nothing was stored. Read-only."""
    raw = np.atleast_2d(raw)
    said = list(dict.fromkeys(words))
    if raw.shape[0] == 0:
        return {w: None for w in said}
    Z = L.stats.standardise(raw)
    out: Dict[str, Optional[int]] = {}
    for w in said:
        j = L.index.get(w)
        if j is None or not L.store_r[j]:
            out[w] = None
        elif w in new:
            z0 = L.store_z[j][0][0]
            hits = [h for h in range(Z.shape[0]) if np.array_equal(Z[h], z0)]
            out[w] = hits[0] if hits else None
        else:
            out[w] = int(np.argmax(L.store_r[j][-1]))
    return out


def grades(claim_rec: Dict[str, object], attributed: Dict[str, Optional[int]],
           set_aside: bool = False) -> List[Tuple[str, Optional[bool], str]]:
    """§2 ITS GRADE, as co-signed — FILED UNDER THE CLAIMED WORD: for each said word w of a learned type T with an attributed
    hypothesis h*, the claim about h* in T, IF IT WAS CONFIDENT, is confirmed iff b_T(h*) = w and refuted iff b_T(h*) is
    another word of T; returned as (the claimed word b_T(h*), confirmed, the said word w). A said word of no learned type, an
    unattributed word, or a claim that was not confident: ungraded (nothing returned).
    AMENDMENT 2 — the rule (replacing AMENDMENT 1's band rule): when the phrase's «none» fired (`set_aside`), every claim
    this phrase would grade is set aside, «about a thing I did not see», returned as (b_T(h*), None, w); otherwise graded
    as above. What was never gradable stays ungraded either way."""
    types = claim_rec["types"]
    where = {w: k for k, T in enumerate(types) for w in T}
    out: List[Tuple[str, Optional[bool], str]] = []
    for w, h in attributed.items():
        k = where.get(w)
        if k is None or h is None:
            continue
        conf = claim_rec["confident"][k]
        if h >= len(conf) or not conf[h]:
            continue
        b = claim_rec["believed"][k][h]
        out.append((b, None if set_aside else (b == w), w))
    return out


# ------------------------------------------------------------------------------------------------ the row
class HealthRow:
    """One word's row (§2): its CONFIDENT claims (n_claims), the graded ones in order (1 confirmed, 0 refuted), and the said
    word's MISSED count (the parent said this word about a thing believed to be another — a reading, never in the gate).
    AMENDMENT 1: `unseen` counts its claims set aside «about a thing I did not see» (never graded, never in cal_20)."""

    def __init__(self) -> None:
        self.n_claims = 0
        self.outcomes: List[int] = []
        self.missed = 0
        self.unseen = 0

    @property
    def n_graded(self) -> int:
        return len(self.outcomes)

    def cal20(self) -> Optional[float]:
        """cal_20 = confirmed / graded over the LAST 20 graded claims (all of them while fewer than 20)."""
        last = self.outcomes[-WINDOW:]
        return (sum(last) / len(last)) if last else None

    def windows(self) -> List[float]:
        """The series of cal_20 over consecutive, non-overlapping 20-claim windows from the first graded claim (a partial
        tail is not a window) — declared."""
        n = len(self.outcomes) // WINDOW
        return [sum(self.outcomes[i * WINDOW:(i + 1) * WINDOW]) / WINDOW for i in range(n)]

    def deltas(self) -> List[float]:
        w = self.windows()
        return [w[i] - w[i - 1] for i in range(1, len(w))]

    def delta_last(self) -> Optional[float]:
        d = self.deltas()
        return d[-1] if d else None

    def median_abs_delta(self) -> Optional[float]:
        d = self.deltas()
        return float(np.median(np.abs(d))) if d else None

    def drift_firings(self, floor: float = 0.0) -> int:
        """The drift clause's would-be firings, a READING (§3): at each completed window, Δ < −2 × max(the median |Δ| of the
        windows so far, floor) — the unfloored form (CONCLUSION §4's) and the 1/20-floored one (the edit's alternative)."""
        d = self.deltas()
        fired = 0
        for i in range(len(d)):
            med = float(np.median(np.abs(d[:i + 1])))
            if d[i] < -DRIFT_K * max(med, floor):
                fired += 1
        return fired

    def summary(self) -> Dict[str, object]:
        return {"n_claims": self.n_claims, "n_graded": self.n_graded, "cal20": self.cal20(), "windows": self.windows(),
                "delta_last": self.delta_last(), "median_abs_delta": self.median_abs_delta(),
                "drift_firings": self.drift_firings(), "drift_firings_floor": self.drift_firings(DRIFT_FLOOR),
                "missed": self.missed, "confirmed": int(sum(self.outcomes)), "unseen": self.unseen}


class HealthBook:
    """The rows of every word, for ONE grading road (the learner's own attribution, or the referent's — the offline ceiling)."""

    def __init__(self) -> None:
        self.rows: Dict[str, HealthRow] = {}

    def row(self, w: str) -> HealthRow:
        r = self.rows.get(w)
        if r is None:
            r = self.rows[w] = HealthRow()
        return r

    def add_claims(self, claim_rec: Dict[str, object]) -> None:
        for k, bs in enumerate(claim_rec["believed"]):
            for h, b in enumerate(bs):
                if claim_rec["confident"][k][h]:
                    self.row(b).n_claims += 1

    def add_grades(self, graded: Sequence[Tuple[str, Optional[bool], str]]) -> None:
        for b, ok, w in graded:
            if ok is None:                                   # AMENDMENT 1: set aside — counted under the claimed word only
                self.row(b).unseen += 1
                continue
            self.row(b).outcomes.append(1 if ok else 0)
            if not ok:
                self.row(w).missed += 1

    def summary(self) -> Dict[str, Dict[str, object]]:
        return {w: self.rows[w].summary() for w in sorted(self.rows)}


# ------------------------------------------------------------------------------------------------ the gate and the road
def row_gate(row: Optional[HealthRow]) -> Tuple[bool, Optional[str]]:
    """§3 the gate from a row: n_graded ≥ 20 AND cal_20 ≥ 0.80 → open; under 20 graded → «no row»; else «not held lately»."""
    if row is None or row.n_graded < GATE_N:
        return False, REASON_NO_ROW
    if row.cal20() < GATE_CAL:
        return False, REASON_NOT_HELD
    return True, None


def book_gate(book: HealthBook, perm: Optional[Dict[str, str]] = None) -> Callable[[str], Tuple[bool, Optional[str]]]:
    """A road's gate from a book: the word's OWN row, or (the null) the row of perm[word]."""
    def gate(w: str) -> Tuple[bool, Optional[str]]:
        src = perm.get(w, w) if perm is not None else w
        return row_gate(book.rows.get(src))
    return gate


def accuracy_gate(acc: Dict[str, Optional[float]], bar: float = GATE_CAL) -> Callable[[str], Tuple[bool, Optional[str]]]:
    """HEALTH-ORACLE's gate: a per-word accuracy the CALLER measured (≥ 0.80 → open; none measured → «no row»)."""
    def gate(w: str) -> Tuple[bool, Optional[str]]:
        a = acc.get(w)
        if a is None:
            return False, REASON_NO_ROW
        if a < bar:
            return False, REASON_NOT_HELD
        return True, None
    return gate


class HealthRoad(Lr.RWRoad):
    """The LAW road (RWRoad(L): the ear's types, the READER band, production maturity, «none» = τ_point) with ONE difference
    (§3): a believed name is SAYABLE iff the band holds it (RWRoad.sayable, unchanged) AND the road's gate reads open for
    the word. The mouth's code (`produce_believed`) is untouched; the words the gate refused are RECORDED per item
    (begin_item / end_item) so the reasons table can name the row."""

    def __init__(self, L: "Lr.RWLearner", gate: Callable[[str], Tuple[bool, Optional[str]]]):
        super().__init__(L)
        self.gate = gate
        self._refused: List[Dict[str, str]] = []

    def begin_item(self) -> None:
        self._refused = []

    def end_item(self) -> List[Dict[str, str]]:
        out, self._refused = self._refused, []
        return out

    def sayable(self, x: np.ndarray, w: str) -> bool:
        if not super().sayable(x, w):
            return False
        ok, why = self.gate(w)
        if not ok:
            self._refused.append({"word": w, "why": why})
            return False
        return True


# ------------------------------------------------------------------------------------------------ the null and the graders
def derange(words: Sequence[str], rng: np.random.Generator) -> Dict[str, str]:
    """The null (§3): a derangement of the trained words — sorted first, so the draw is order-free — by
    learners.nshuf_permutation; word → the word whose row it reads (no word keeps its own)."""
    ws = sorted(words)
    p = Lr.nshuf_permutation(rng, len(ws))
    return {ws[i]: ws[int(p[i])] for i in range(len(ws))}


def ece(conf: Sequence[float], correct: Sequence[int], bins: int = 10) -> Dict[str, object]:
    """ECE over `bins` equal-width bins of [0, 1] (1.0 in the last): Σ_b (n_b / N)·|accuracy_b − confidence_b|, with the
    calibration curve (per non-empty bin: n, mean confidence, accuracy)."""
    c = np.asarray(list(conf), dtype=np.float64)
    y = np.asarray(list(correct), dtype=np.float64)
    if c.size == 0:
        return {"ece": None, "n": 0, "n_err": 0, "curve": []}
    idx = np.minimum(np.floor(c * bins + 1e-9).astype(int), bins - 1)
    total, curve = 0.0, []
    for b in range(bins):
        m = idx == b
        if not m.any():
            continue
        n, acc, cf = int(m.sum()), float(y[m].mean()), float(c[m].mean())
        total += n / c.size * abs(acc - cf)
        curve.append({"bin": b, "n": n, "conf": cf, "acc": acc})
    return {"ece": total, "n": int(c.size), "n_err": int(round(float((1.0 - y).sum()))), "curve": curve}


def auroc(conf: Sequence[float], correct: Sequence[int]) -> Optional[float]:
    """Type-2 AUROC: P(the confidence of a correct answer > an incorrect one's) + ½ P(=) — every pair (Mann–Whitney); None
    without both kinds."""
    c = np.asarray(list(conf), dtype=np.float64)
    y = np.asarray(list(correct), dtype=bool)
    pos, neg = c[y], c[~y]
    if pos.size == 0 or neg.size == 0:
        return None
    gt = float((pos[:, None] > neg[None, :]).sum())
    eq = float((pos[:, None] == neg[None, :]).sum())
    return (gt + 0.5 * eq) / float(pos.size * neg.size)


def row_toy(seed: int, n: int = 200) -> Dict[str, object]:
    """THE FIRST GATE step 2 (§7): two words, A's confident claims confirmed with probability 0.95, B's with 0.50, n graded
    each (seed `seed`): the gate must keep A and refuse B; the deranged null (for two words, the swap) must flip them; one
    more ungraded claim must move nothing — and (AMENDMENT 1) one claim set aside «unseen» moves nothing but its count."""
    rng = np.random.default_rng(seed)
    book = HealthBook()
    for _ in range(n):
        for w, p in (("A", 0.95), ("B", 0.50)):
            book.row(w).n_claims += 1
            ok = bool(rng.random() < p)
            book.add_grades([(w, ok, w if ok else "other")])
    keeps = {w: book_gate(book)(w)[0] for w in ("A", "B")}
    perm = derange(["A", "B"], rng)
    null = {w: book_gate(book, perm)(w)[0] for w in ("A", "B")}
    before = {w: (book.rows[w].n_graded, book.rows[w].cal20(), row_gate(book.rows[w])) for w in ("A", "B")}
    for w in ("A", "B"):
        book.row(w).n_claims += 1
    after = {w: (book.rows[w].n_graded, book.rows[w].cal20(), row_gate(book.rows[w])) for w in ("A", "B")}
    missed = book.row("other").missed
    for w in ("A", "B"):
        book.add_grades([(w, None, "other")])
    after_unseen = {w: (book.rows[w].n_graded, book.rows[w].cal20(), row_gate(book.rows[w])) for w in ("A", "B")}
    unseen_ok = (after_unseen == after and all(book.rows[w].unseen == 1 for w in ("A", "B"))
                 and book.row("other").missed == missed)
    return {"seed": seed, "keeps": keeps, "null": null, "perm": perm, "ungraded_moves_nothing": before == after,
            "unseen_moves_nothing": unseen_ok,
            "n_graded": {w: book.rows[w].n_graded for w in ("A", "B")},
            "cal20": {w: book.rows[w].cal20() for w in ("A", "B")}}
