"""predict.py — PREDICT + FILE: the one modulator, and the falsifiability law (G4 §3 B6; docs/G4-DESIGN.md
row 3b — his research's predictive-coding/active-inference mechanism, docs/THINKING-RUNG1-PREREG.md §1 —
new, minimal; FILE reimplements Alpha 2's organs/prediction_ledger.py's law in tens of lines).

edit: Claude (Sonnet 5, G4 builder B), 2026-09-19 22:07 +0400 — B6 (docs/briefs/G4-BUILDER-B-GENES.md).

edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 10:46 +0400 — W3-2b (docs/G4-WAVE3-CLAUSES.md, W3-2's
NOTE; docs/G4-PREREG.md §16 addendum 1): `error()`'s target moves INSIDE the organism. The reading that
forced this: PREDICT's error was measured against `expect()` = the LAST moment's strongest sight winner
— a state carried from a DIFFERENT thing (the previous canvas), so every canvas boundary read the same
size (steady ~.23) and an ARRIVAL was invisible to it (life 1: 0 of 5 spikes). The law now: the expected
glance is the nearest RESONATING cell's stored vector for THIS glance — `c = org.sight.cos(x_actual)`
over the cells alive BEFORE this moment (this method is called, in `creature/mind.py`, before
`Organism.moment()` runs for the canvas — no newborn from this very glance can be among them); if the
nearest cell RESONATES (`c.max() >= org._theta(org.sight)`, machinery's own threshold, read not called —
`Organism._resonate` BIRTHS, which a mere error reading must never do) the error is `1 - c.max()`; with
nothing resonating (including no sight cell born yet) the error is the maximal 1.0 — a genuine surprise,
not a graded wrongness. `expect()`/`note_winners()` are KEPT for the record (mind.py still calls
`note_winners` after every moment) but nothing grades on them any more; see this module's own toy
(tests/genome/test_predict.py) and tests/genome/test_b13_modulation_arrival.py for the re-read this
forced on both the B6 and B13 toys — reported honestly, not moved.

edit: Claude (Sonnet 5, builder E), 2026-09-21 16:58 +0400 — G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md;
docs/organs/MIND-MEMORY.md §4 G-MIND-3): PREDICT gains an ERROR ARM — the mechanism above (renamed
"novelty" here) stays the untouched default and executes the SAME lines it always has (byte-identical
when the genome's PREDICT line carries no `; error <arm>` clause, or spells `; error novelty` — the
regression pin is `tests/genome/test_predict.py::test_novelty_arm_is_byte_identical_to_pre_g5e`). Three
more arms, each exactly as MIND-MEMORY G-MIND-3 defines it, live here (the mind's own reading layer —
never in genome/machinery.py's Area/Organism, which stay organs with no notion of "arm"):

- **conjunctive** — `err = max(sight_novelty, word_novelty)`. `sight_novelty` is the novelty arm's own
  number (identical formula). `word_novelty` = 1.0 while this WORD has been delivered fewer than 3 times
  BEFORE this canvas, then 0.0 — held for showings 1, 2 AND 3 (not just the 1st), per G-MIND-3's own
  ceiling table row "A, as written above": median{1.0, 1.0, 1.0} over the first 3 showings.
  Tracked in `self._word_seen: Dict[str, int]`, incremented once per canvas that carries a word (a
  sight-only canvas, word=None, touches nothing and reads word_novelty=0.0 — there is no word to be new).
- **episodic** — `err = clip(max(0, cos_to_nearest_SIGHT_CELL - cos_to_nearest_EPISODE), 0, 2)`: how much
  better the resonating prototype explains this glance than any actual remembered episode does. Needs
  the FAST store (`episodes`, read-only: `Episodes.nearest` never mutates); with no sight cell ever born
  `cos_to_nearest_cell := -1.0` (Area.cos's own dead-cell convention); with no episode yet written
  `cos_to_nearest_episode := -1.0` (nothing to explain away, so the two -1's cancel to a 0 gap at the
  very first few canvases of a life — the only place this bootstrap default is reachable, since FAST
  writes one episode every canvas from the first one on). G-MIND-3's own table: this arm's ratio-to-
  last-50 denominator is ~0 at steady state, so `tools/verdict_g4.py`'s `modulation()` ratio is read
  UNCHANGED (never re-derived) and reported beside the ABSOLUTE reading the table specifies instead
  (`first3_med >= last50_med + 0.05`) — see G5-E-REPORT.md for which arm is admissible and how each is
  read.
- **comparator** — `err = 1.0` when the winning sight cell's established answer (`Organism._answer_of`)
  is NOT among this moment's WORD winners; the graded novelty otherwise. This is `Organism._misfire`'s
  own predicate, read-only, never called: `_misfire` MUTATES (`area.misfires`, can birth) and needs S/T
  (this canvas's sight+word winners) which do not exist yet when `error()` runs (it runs before
  `Organism.moment()` for this canvas). So the word winners are recomputed here exactly as
  `Organism._resonate` computes them but WITHOUT the birth side effect: `org.words.cos(xw)`, the same
  per-area threshold (`org._theta(org.words)`), the same top-KWTA-that-resonates rule, stable sort tie-
  break matching `_resonate`'s `np.argsort(-c, kind="stable")`. Two fallbacks mirror `_misfire` exactly:
  no established answer yet (`ans is None`, `_misfire`'s own `continue` case) -> graded novelty, nothing
  to violate; no word on this canvas (sight-only) -> graded novelty, nothing to compare against. Reading
  a WORDS-area cell id against WORDS-area winners — the opposite direction of the think.py:411 bug
  (SOLUTIONS #232's ADDENDUM 2: a SIGHT id compared to a WORDS index) — is the one line worth a second
  look in review, and it reads the right area on both sides (`_answer_of(self.org.sight, cid)` returns a
  WORDS cell id; `winners_w` are WORDS cell ids; compared to each other, never to a sight id).

Not persisted at resume: `_word_seen` (arm A's per-word count). `Mind.resume()` re-derives `_heard` (a
boolean set) from the ledger's `moment_word`, which cannot recover a COUNT; a resumed life under arm A
would restart every word's count at 0. Out of scope for this brief (replay-only, a fresh Mind every
time — creature/replay.py and this module's own worker never call resume()); raised in G5-E-REPORT.md as
a gap a live deployment of arm A would need to close (persist `_word_seen` in ledger.json, gated the
same way `predictor_last_winner` already is).

PREDICT's OLD law (superseded above, kept here so the "why" is not lost): `expect()` named the feature
the NEXT glance was predicted to look like — the current sight winner's own cell vector (the strongest
resonating sight cell of the last moment lived, read from `Organism.moment()`'s new (S, T) return — B2's
edit to machinery.py); before any winner had ever been seen, the mean of the alive sight cells; with none
alive at all, zeros. `error(x_actual)` was 1 minus the cosine to that expectation (clipped into [0, 2],
cosine's own range) — the modulator: it grades the act (the caller reads `.last_error` to know how
surprising this moment was), scales DELTA's learning rate (`modulate`), and ranks what SLEEP replays (B7
reads `surprise=error` off this same number — still true under the new law, same signal, new source).

FILE's law: a prediction is FILED with all four fields named (claim, route, decider, due) or REFUSED BY
NAME — never silently dropped, never accepted half-written. `score` grades a filed (never a refused) row
against `evidence`: a callable `evidence(row) -> bool` is the general form (the "decider" is WHO applies
it; `evidence` supplies the mechanical check no free-text field can); a plain value is graded by its own
truthiness. `append_ledger` writes one JSON line to `predictions.jsonl` per PREREG §3 B6 — plain append
(a ledger is append-only; unlike FAST's full-file save, a torn last line is a known, tolerable read-time
risk, not a save-time one).
"""
from __future__ import annotations

import json
import pathlib as _pl
from typing import Callable, Dict, List, Optional, Union

import numpy as np

from .machinery import Organism

FILE_FIELDS = ("claim", "route", "decider", "due")

# N1 PRECISION (PREREG-N1-PRECISION §1 + AMENDMENTS 1–3, SIGNED 2026-10-09; docs/brain/precision/) — the declared
# machine-form constants of the precision register, fixed before any reading, never fitted. The register lives
# ONLY behind Predictor(precision=True) (default False: not one of these lines runs — the byte-identity pin).
# AMENDMENT 3's form: the registers are EMAs of log(e^2 + δ) — the arithmetic variance ratio carries a Jensen
# bias on bursty stationary streams (measured: w 2.674 at true stationarity); log-domain EMAs of the same
# variable converge to the same expectation, so w -> 1 at stationarity by construction.
PRECISION_ETA_FAST = 0.05     # l_fast EMA rate (τ ≈ 20 moments): the stream's recent reliability
PRECISION_ETA_SLOW = 0.005    # l_slow EMA rate (τ ≈ 200 moments): the long-run anchor the present is weighed against
PRECISION_FLOOR = 1e-6        # δ — inside the log: log(e^2 + δ)
PRECISION_PRIOR = 0.25        # v0 — both registers start at log(v0); the first call's w = exp(0) = 1 exactly
PRECISION_W_LO = 0.25         # the weight clip: the register can discount to a quarter…
PRECISION_W_HI = 4.0          # …or amplify to fourfold, never beyond (modulate's own [lo, hi] clip stands after)


class Predictor:
    """PREDICT — PREREG §3 B6: `expect()`, `error(x_actual)`, `modulate(lr)`. Bound to one Organism;
    call `note_winners(S)` with the sight winners `Organism.moment()` returned, once per moment lived,
    so the NEXT `expect()` reflects what was just seen.

    W3-2b (2026-09-21): `error()` no longer calls `expect()` — it reads `self.org.sight` directly (the
    nearest RESONATING cell to the actual glance, module docstring). `expect()`/`note_winners()` are kept
    for the record (still called every moment) but nothing grades on them any more.

    G5-E (2026-09-21): `arm` names which of the four G-MIND-3 error computations `error()` runs —
    "novelty" (default, today's, byte-identical), "conjunctive", "episodic", "comparator"."""

    def __init__(self, org: Organism, lo: float = 0.5, hi: float = 2.0, arm: str = "novelty", precision: bool = False):
        self.org = org
        self.lo, self.hi = lo, hi
        self._last_winner: Optional[np.ndarray] = None
        self.last_error: Optional[float] = None
        self.arm = arm
        self._word_seen: Dict[str, int] = {}          # G5-E arm "conjunctive": canvases this word has been delivered on, so far
        # N1 (edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:25 +0400 — PREREG-N1-PRECISION
        # + AMENDMENT 1): the precision register, default OFF = byte-identical. Two EMAs of log(e^2 + δ)
        # (AMENDMENT 3's form) at the declared prior; `last_weight` stays None while the flag is off.
        self.precision = precision
        self._l_fast = float(np.log(PRECISION_PRIOR))
        self._l_slow = float(np.log(PRECISION_PRIOR))
        self.last_weight: Optional[float] = None

    def note_winners(self, S: List[int]) -> None:
        """S: the sight winners of the moment just lived (best first, §11 am. 3's resonate order). The
        strongest one becomes what the NEXT expect() names. An empty S (nothing resonated) leaves the
        last winner as it was — a moment with no sight winner teaches expect() nothing new."""
        if S:
            self._last_winner = self.org.sight.cells[S[0]].copy()

    def expect(self) -> np.ndarray:
        """The next glance's expected feature: the last noted winner; before any winner, the mean of
        the alive sight cells; with none alive, zeros (genome.sight_dim()-long)."""
        if self._last_winner is not None:
            return self._last_winner
        alive = self.org.sight.alive_ids()
        if len(alive) == 0:
            return np.zeros(self.org.g.sight_dim())
        return self.org.sight.cells[alive].mean(axis=0)

    def error(self, x_actual: np.ndarray, word: Optional[str] = None, xw: Optional[np.ndarray] = None,
              episodes: Optional[object] = None) -> float:
        """W3-2b (docs/G4-WAVE3-CLAUSES.md, W3-2's NOTE; PREREG §16 addendum 1): the expected glance is
        the nearest RESONATING sight cell's stored vector for THIS glance — `c = org.sight.cos(x_actual)`
        over the cells alive BEFORE this moment (the caller, creature/mind.py, calls this BEFORE
        `Organism.moment()` runs for the canvas, so no newborn from this very glance can be among them —
        a newborn scoring 0 error at its own birth would hide every arrival). If the nearest cell
        RESONATES (`c.max() >= org._theta(org.sight)` — machinery's own comparison, READ not CALLED:
        `Organism._resonate` births, which a mere error reading must never do) the error is
        `1 - c.max()` (clipped into [0, 2], cosine's own range); with nothing resonating — including no
        sight cell born yet (`org.sight.n == 0`) — the error is the maximal 1.0: a genuine surprise,
        not a graded wrongness (there is nothing yet to be wrong ABOUT).

        G5-E: this is the "novelty" arm — the DEFAULT and the only one run when `self.arm == "novelty"`,
        UNCHANGED from the six lines above (the pin). `word`/`xw`/`episodes` are accepted so every caller
        can pass them unconditionally (creature/mind.py does); the novelty arm ignores all three. The
        other three arms are separate methods below, dispatched here."""
        area = self.org.sight
        if area.n == 0:
            e_novelty = 1.0
        else:
            c = area.cos(x_actual)
            cmax = float(c.max())
            theta = self.org._theta(area)
            e_novelty = float(np.clip(1.0 - cmax, 0.0, 2.0)) if cmax >= theta else 1.0

        if self.arm == "novelty":
            e = e_novelty
        elif self.arm == "conjunctive":
            e = self._error_conjunctive(e_novelty, word)
        elif self.arm == "episodic":
            e = self._error_episodic(x_actual, area, episodes)
        elif self.arm == "comparator":
            e = self._error_comparator(x_actual, area, word, xw, e_novelty)
        else:
            raise ValueError(f"Predictor.error: unknown arm {self.arm!r} (novelty|conjunctive|episodic|comparator)")
        if self.precision:
            # N1 (PREREG-N1-PRECISION §1 + AMENDMENTS 1–3): the precision weight is READ from the registers
            # first (causal — the past weighs the present), THEN both registers update with this raw error's
            # log-square. last_error keeps the RAW value (the journal, act grading and sleep ranking read
            # raw); the weight is consumed by modulate() alone.
            w = float(np.clip(np.exp(self._l_slow - self._l_fast), PRECISION_W_LO, PRECISION_W_HI))
            le = float(np.log(e * e + PRECISION_FLOOR))
            self._l_fast = (1.0 - PRECISION_ETA_FAST) * self._l_fast + PRECISION_ETA_FAST * le
            self._l_slow = (1.0 - PRECISION_ETA_SLOW) * self._l_slow + PRECISION_ETA_SLOW * le
            self.last_weight = w
        self.last_error = e
        return e

    # -------------------------------------------------------------------------------- G5-E's three arms
    def _error_conjunctive(self, e_novelty: float, word: Optional[str]) -> float:
        """arm A — MIND-MEMORY §4 G-MIND-3: err = max(sight_novelty, word_novelty); word_novelty = 1.0
        while the ear has delivered this word FEWER THAN 3 TIMES, then 0 — "held for the first 3
        showings" (G-MIND-3's own ceiling table, row "A, as written above": median{1.0, 1.0, 1.0} over
        showings 1-3, "novelty held for the first 3 showings", so it must NOT already read 0 on the 3rd
        showing). Read on the count of PRIOR deliveries (before this one), which is what makes showings
        1, 2 AND 3 all read 1.0, falling to 0.0 only from the 4th showing on: prior=0 -> 1st showing,
        prior=1 -> 2nd, prior=2 -> 3rd, all < 3 -> 1.0; prior=3 -> 4th showing, not < 3 -> 0.0. The
        count is THEN incremented for the next call. A sight-only canvas (word=None) has no word to be
        new: word_novelty = 0.0, err = e_novelty."""
        if word is None:
            return e_novelty
        prior = self._word_seen.get(word, 0)
        self._word_seen[word] = prior + 1
        word_novelty = 1.0 if prior < 3 else 0.0
        return max(e_novelty, word_novelty)

    def _error_episodic(self, x_actual: np.ndarray, area, episodes: Optional[object]) -> float:
        """arm B — MIND-MEMORY §4 G-MIND-3: err = clip(max(0, cos_to_nearest_CELL - cos_to_nearest_
        EPISODE), 0, 2) — how much better the resonating prototype explains this glance than any actual
        remembered episode does. `episodes` is the FAST store (genome/fast.py's Episodes), read via
        `nearest()` only (never mutated). No sight cell ever born -> cos_to_cell = -1.0 (Area.cos's own
        dead-cell convention); no episode yet -> cos_to_episode = -1.0 (reachable only at the very start
        of a life, since FAST writes one episode every canvas)."""
        cos_cell = float(area.cos(x_actual).max()) if area.n > 0 else -1.0
        cos_ep = -1.0
        if episodes is not None and len(episodes) > 0:
            nearest = episodes.nearest(x_actual, 1)
            if nearest:
                cos_ep = nearest[0][1]
        return float(np.clip(max(0.0, cos_cell - cos_ep), 0.0, 2.0))

    def _error_comparator(self, x_actual: np.ndarray, area, word: Optional[str], xw: Optional[np.ndarray], e_novelty: float) -> float:
        """arm C — MIND-MEMORY §4 G-MIND-3: err = 1.0 when the winning sight cell's established answer
        (Organism._answer_of) is not among this moment's WORD winners; the graded novelty otherwise.
        Reimplements Organism._misfire's own predicate, read-only (_misfire mutates and needs S/T, which
        do not exist yet at this point in the canvas). No word on this canvas (sight-only, xw is None),
        or nothing resonates in sight, or the winning cell has no established answer yet -> graded
        novelty (nothing to compare, or nothing to violate — _misfire's own `continue` case)."""
        if area.n == 0:
            return 1.0
        c = area.cos(x_actual)
        cmax = float(c.max())
        theta = self.org._theta(area)
        if cmax < theta:
            return 1.0
        if word is None or xw is None:
            return e_novelty
        nearest_cell = int(np.argmax(c))
        ans = self.org._answer_of(area, nearest_cell)
        if ans is None:
            return e_novelty
        words_area = self.org.words
        cw = words_area.cos(xw)
        theta_w = self.org._theta(words_area)
        order = np.argsort(-cw, kind="stable")
        winners_w = [int(i) for i in order[: self.org.g.kwta] if words_area.alive[i] and cw[i] >= theta_w]
        return e_novelty if ans in winners_w else 1.0

    def modulate(self, lr: float) -> float:
        """lr x clip(0.5 + 3*error, 0.5, 2.0) — PREREG's genome line: `PREDICT … error scales delta
        0.5..2.0`. Reads the last `error()` call's result; with none yet, error=0 (scale floors at 0.5).
        N1: with `precision` on, the SAME formula reads the precision-weighted error (e · w, w from the
        register at the last error() call); the [lo, hi] clip is unchanged either way."""
        e = self.last_error if self.last_error is not None else 0.0
        if self.precision and self.last_weight is not None:
            e = e * self.last_weight
        scale = float(np.clip(0.5 + 3.0 * e, self.lo, self.hi))
        return lr * scale


# ============================================================================================= FILE
def file(claim: str, route: str, decider: str, due: str) -> Dict[str, object]:
    """FILE claim route decider due: all four named (non-empty) or refused BY NAME. Returns
    {"accepted": True, "row": {...}} or {"accepted": False, "refused": [missing field names], "row": {...}}
    — the refusal is itself a row, never a silent drop or a raised exception."""
    row = {"claim": claim, "route": route, "decider": decider, "due": due}
    missing = [f for f in FILE_FIELDS if not row.get(f)]
    if missing:
        return {"accepted": False, "refused": missing, "row": dict(row)}
    return {"accepted": True, "refused": [], "row": dict(row), "outcome": None}


def score(row: Dict[str, object], evidence: Union[Callable[[Dict[str, object]], bool], object]) -> Dict[str, object]:
    """Grades a FILED (never a refused) row's claim against `evidence`. `evidence` callable -> called as
    evidence(row["row"]); otherwise graded by bool(evidence). Returns a NEW dict (the input row is never
    mutated) with "outcome" set True/False. Raises ValueError on a refused row — there is nothing to
    grade (score()ing a refusal is a caller bug, not a data condition FILE should paper over)."""
    if not row.get("accepted"):
        raise ValueError(f"score: a refused claim was never filed — nothing to grade (refused: {row.get('refused')})")
    outcome = bool(evidence(row["row"])) if callable(evidence) else bool(evidence)
    out = dict(row); out["row"] = dict(row["row"]); out["outcome"] = outcome
    return out


def append_ledger(path, row: Dict[str, object]) -> None:
    """Appends one FILE/score row as a JSON line to `path` (predictions.jsonl, PREREG §3 B6)."""
    p = _pl.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(row, default=str) + "\n")
