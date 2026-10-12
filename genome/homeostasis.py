# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 — PREREG-HOMEOSTASIS §2.2 + AMENDMENT 1
# (docs/organism/homeostasis/PREREG-HOMEOSTASIS.md, SIGNED 2026-10-12, SEAT-LINE-H0.txt sha256 edda32e7…):
# THE DRIVES — the three internal state variables (arousal, boredom, fatigue), their per-canvas update
# rules with the law's DECLARED constants (fitted to the §0(b) bench tape 2026-10-12), the modulate()
# gains, the deterministic draw, and the journal row form. Pure functions of the tape (the canvas err +
# the boundaries) + the life's seed: replay-identical by construction; NEVER wired when undeclared
# (byte-identical — the parser clause is genome/machinery.py's, the Mind self-wires tri-state).
"""genome/homeostasis.py — the HOMEOSTASIS register (the developmental road's Law 1).

The Mind owns ONE Homeostasis instance when the genome declares `HOMEOSTASIS <1..3 of arousal boredom
fatigue>`. The variables update once per canvas from the canvas's own prediction error; the effectors read
them: the learning gains (modulate), the eye's extra fixation, the boredom-driven EXTRA asks/babble
(never gates — A2), the seek at boredom's ceiling (A1), the fatigue-forced sleep boundary and the mouth's
suppression/exclaim (§2.4). Every probability draws from the tape's own seq (A3), never a shared RNG."""
from __future__ import annotations

import hashlib
from typing import Dict, Optional, Tuple

# §2.2's DECLARED constants (fitted to the §0(b) bench, brain-long-6-h0s0, 9,219 canvases, 2026-10-12):
REST_A, ALPHA_A, BETA_A = 0.3, 0.25, 0.02        # arousal: a ← clip(a + α(s−a) + β(REST_A−a))
KAPPA, GAMMA_B, DELTA_B, SLOW_EMA = 0.8, 0.04, 0.10, 0.01   # boredom: +γ while s < κ·s̄, else ×decay δ
EPS_F, ZETA_F = 0.001, 0.6                       # fatigue: +ε per canvas; ×(1−ζ) at a sleep boundary
# §2.2/A2's thresholds (declared against §0(b)'s measured ranges — verifier V5):
TH_BABBLE, TH_EXCLAIM, TH_SILENT, TH_EYE = 0.7, 0.7, 0.9, 0.7
SEEK_CEILING, SEEK_REFRACTORY, SEEK_WINDOW = 0.95, 500, 1000
EXCLAIM_SURPRISE_MULT, EXCLAIM_WINDOW = 2.0, 5   # a > θ within 5 canvases of s ≥ 2·s̄
FATIGUE_FORCE, FATIGUE_FLOOR_SHARE = 0.95, 2     # f ≥ 0.95 forces sleep, never sooner than every//2


def clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


class Homeostasis:
    """The three drives. `declared` is the parser's dict {word: True} — a variable not declared stays at
    its NEUTRAL value and its effectors are inert (gains 1.0, gates off) — the tri-state's own semantics."""

    def __init__(self, declared: Dict[str, bool], seed: int, flat: bool = False):
        self.declared = dict(declared)
        self.seed = int(seed)
        self.flat = bool(flat)
        self.a: float = 0.5 if self.flat else REST_A   # the flat twin (H-DRIVE-EFFECT's baseline):
        self.b: float = 0.0                            # arousal pinned at 0.5, boredom/fatigue at 0 —
        self.f: float = 0.0                            # the state NEVER moves (note_canvas's early return)
        self.slow: float = 0.0          # the slow running mean surprise s̄
        self.canvases: int = 0
        self.sleeps: int = 0
        self.seeks: int = 0
        self.last_seek_canvas: int = -SEEK_REFRACTORY
        self.seek_source: Optional[str] = None
        self.seek_until_canvas: int = -1
        self.last_surprise_canvas: int = -1
        self.exclaimed_at: int = -1
        self.seen: Dict[str, int] = {}            # A1: source → its last canvas index (the seek's ledger)
        self.wordless: Dict[int, Tuple[str, str, int]] = {}   # cell → (source, tape moment, canvas)

    # ------------------------------------------------------------- state
    def on(self, word: str) -> bool:
        return bool(self.declared.get(word, False))

    def note_canvas(self, err: float, source: Optional[str] = None) -> None:
        """§2.2's update, once per canvas, from the canvas's own prediction error (the same stream the
        precision register reads — declared, the H-PRECISION arm owns the interaction question). The flat
        twin's state never moves (H-DRIVE-EFFECT's baseline); the source ledger feeds the seek (A1)."""
        if source is not None:
            self.seen[source] = self.canvases
        if self.flat:
            self.canvases += 1
            return
        s = float(err)
        if self.on("arousal"):
            self.a = clip(self.a + ALPHA_A * (s - self.a) + BETA_A * (REST_A - self.a))
        if s >= EXCLAIM_SURPRISE_MULT * self.slow and self.canvases > 0:
            self.last_surprise_canvas = self.canvases
        self.slow = self.slow + SLOW_EMA * (s - self.slow)
        if self.on("boredom"):
            self.b = clip(self.b + GAMMA_B) if s < KAPPA * self.slow else clip(self.b - DELTA_B * self.b)
        if self.on("fatigue"):
            self.f = clip(self.f + EPS_F)
        self.canvases += 1

    def note_sleep(self) -> None:
        """Every sleep boundary, when fatigue is declared: f ← f·(1 − ζ) (§2.2)."""
        if self.on("fatigue"):
            self.f = clip(self.f * (1 - ZETA_F))
        self.sleeps += 1

    # ------------------------------------------------------------- effectors (read-only)
    def gains(self) -> Tuple[float, float]:
        """(g_a, g_f) for predict.py's modulate() — 1.0 exactly when the variable is undeclared."""
        g_a = clip(1.0 + 2.0 * (self.a - REST_A), 0.5, 2.0) if self.on("arousal") else 1.0
        g_f = (1.0 - 0.5 * self.f) if self.on("fatigue") else 1.0
        return g_a, g_f

    def extra_fixations(self) -> int:
        return 1 if (self.on("arousal") and self.a > TH_EYE) else 0

    def draw(self, seq: object, purpose: str) -> float:
        """A3's deterministic draw: sha256(seed|seq|purpose) → [0, 1). Pure; replay-identical."""
        h = hashlib.sha256(f"{self.seed}|{seq}|{purpose}".encode()).digest()
        return int.from_bytes(h[:4], "big") / 2**32

    def extra_event(self, seq: object, purpose: str) -> bool:
        """A2's extras: deterministic probability clip(2·max(0, b − θ_babble)) — exactly False at low b."""
        if not self.on("boredom"):
            return False
        p = clip(2.0 * max(0.0, self.b - TH_BABBLE))
        return p > 0.0 and self.draw(seq, purpose) < p

    def suppressed(self) -> bool:
        return self.on("fatigue") and self.f > TH_SILENT

    def exclaim(self) -> bool:
        """§2.4's exclamation: aroused within the surprise window, at most one per canvas (the caller
        checks a say happened this canvas) and never twice for the same surprise."""
        return (self.on("arousal") and self.a > TH_EXCLAIM
                and 0 <= self.canvases - self.last_surprise_canvas <= EXCLAIM_WINDOW
                and self.exclaimed_at < self.last_surprise_canvas)

    def note_exclaim(self) -> None:
        self.exclaimed_at = self.last_surprise_canvas

    def force_sleep(self, since: int, every: int) -> bool:
        """§2.2's fatigue clause (V3's floor): at ceiling, never sooner than half the count."""
        return self.on("fatigue") and self.f >= FATIGUE_FORCE and since >= every // FATIGUE_FLOOR_SHARE

    def seek_due(self) -> bool:
        """A1: boredom's ceiling with the refractory window (one seek per 500 canvases)."""
        return (self.on("boredom") and self.b >= SEEK_CEILING
                and self.canvases - self.last_seek_canvas >= SEEK_REFRACTORY)

    def seek_target(self, current: Optional[str] = None) -> Optional[str]:
        """A1: the least-recently-attended armed source (the episodes' source ledger), preferring a source
        other than the current one; None when nothing has been seen or only the current source exists."""
        if not self.seen:
            return None
        cands = {s: c for s, c in self.seen.items() if s != current} or dict(self.seen)
        return min(cands.items(), key=lambda kv: kv[1])[0]

    def note_seek(self, source: Optional[str]) -> None:
        self.seeks += 1
        self.last_seek_canvas = self.canvases
        self.seek_source = source
        self.seek_until_canvas = self.canvases + SEEK_WINDOW

    def seek_active(self) -> Optional[str]:
        if self.seek_source is not None and self.canvases < self.seek_until_canvas:
            return self.seek_source
        return None

    def note_wordless_cell(self, cell: int, source: str, moment: str) -> None:
        """A1: a wordless sight resonated — remember its source/moment for the boredom extras' asks."""
        self.wordless[int(cell)] = (source, moment, self.canvases)

    def extra_ask_cell(self, seek_only: bool = False) -> Optional[Tuple[int, str]]:
        """A1/A2: a wordless cell for an extra curiosity ask — the seek's target source's cells FIRST
        (the attention turn); with no active seek (or none from it), the most recent wordless cell."""
        if not self.wordless:
            return None
        target = self.seek_active()
        if target is not None:
            own = [(c, m) for c, (s, m, _n) in self.wordless.items() if s == target]
            if own:
                return own[-1]
            if seek_only:
                return None
        cell, (s, m, _n) = next(reversed(list(self.wordless.items())))
        return cell, m

    # ------------------------------------------------------------- the journal row's form
    def row(self) -> Dict[str, float]:
        """The canvas row's ONE additive key (the `front` key's precedent — present only when declared)."""
        return {"a": round(self.a, 4), "b": round(self.b, 4), "f": round(self.f, 4)}

    # ------------------------------------------------------------- persistence (a resume restores the drives exactly)
    def to_json(self) -> Dict[str, object]:
        return {"a": self.a, "b": self.b, "f": self.f, "slow": self.slow, "canvases": self.canvases,
                "sleeps": self.sleeps, "seeks": self.seeks, "last_seek_canvas": self.last_seek_canvas,
                "seek_source": self.seek_source, "seek_until_canvas": self.seek_until_canvas,
                "last_surprise_canvas": self.last_surprise_canvas, "exclaimed_at": self.exclaimed_at,
                "seen": dict(self.seen),
                "wordless": {str(c): [s, m, n] for c, (s, m, n) in self.wordless.items()}}

    def load_json(self, d: Dict[str, object]) -> None:
        if self.flat:
            return                  # the flat twin's state is pinned at rest by construction, resume or not
        for k in ("a", "b", "f", "slow"):
            setattr(self, k, float(d[k]))
        for k in ("canvases", "sleeps", "seeks", "last_seek_canvas", "seek_until_canvas",
                  "last_surprise_canvas", "exclaimed_at"):
            setattr(self, k, int(d[k]))
        self.seek_source = d.get("seek_source")
        self.seen = {str(s): int(c) for s, c in (d.get("seen") or {}).items()}
        self.wordless = {int(c): (str(v[0]), str(v[1]), int(v[2]))
                         for c, v in (d.get("wordless") or {}).items()}
