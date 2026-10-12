# PREREG-HOMEOSTASIS — AMENDMENT 1 (the wiring's own findings, written BEFORE the wiring code)

*edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-12 ~17:0x +0400 — the law SIGNED this morning
(SEAT-LINE-H0.txt sha256 edda32e7…). This amendment carries the four findings the build's architecture
survey surfaced (mind.py/predict.py/gaze.py/body.py read on ce628fa). No bar moves; two mechanisms take
their honest form against the REAL architecture. The sign-off form is the law's own: this file is the
amendment of record; its sha256 lands in SEAT-LINE-H0-A1.txt.*

## A1 · The seek's mechanism (§2.3's «the next world source in the round-robin»)

**The finding:** the body has NO round-robin — each world is its own cadenced sense thread
(`creature/body.py`'s SenseThread.run: each sense publishes on its own period). There is no shared cycle
to nudge, and crossing the thread boundary to steal a canvas would touch every world's pacing.
**The honest form:** the seek is MIND-side. At boredom's ceiling (b ≥ 0.95, refractory one per 500
canvases) the mind journals a `seek` event naming the LEAST-RECENTLY-ATTENDED armed source (the episodes
carry `source`; the attended-source ledger is derivable from them), and for the following 1,000 canvases
the boredom-driven EXTRA asks/says (A2) prefer that source's content. The mark H-SEEK-LEARN is unchanged
(the sought source's asks+says share rises ≥ 2×; clamped boredom → zero seeks, presence printed).
**Non-vacuity, declared:** if the sought source is so neglected it owns no episodes, the preference finds
nothing and the mark fails HONESTLY — the mechanism never invents content.

## A2 · Extras, never gates (§2.3's «the firing probability scales with b» / §2.4)

**The finding:** today's asks fire once-ever per want (`_maybe_ask`, mind.py:3463) and today's says fire
on filed frames (`_maybe_say`, mind.py:4330). A probabilistic GATE on either would cut the baseline rates
(~360 asks / ~770 says per 1,000 canvases at youth, §0(b)) and fail the law's own H-DRIVE-EFFECT
non-degradation bar against the flat twin.
**The honest form:** boredom ADDS, never gates. (i) EXTRA asks: after each think, with deterministic
probability `p = clip(2·max(0, b − θ_babble), 0, 1)` the mind forms ONE curiosity ask through the EXISTING
wordless-sight want road (no new want kind), preferring the seek's target source when one is active.
(ii) EXTRA babble says: the same p-form at the mouth, saying a FILED frame's own words (the most recently
cited frame), journaled with `babble: true`. (iii) At low boredom both extras are exactly zero — the
baseline is untouched by construction. The 2×/1.5× ratio bars (H-BOREDOM-ASK/-MOUTH) are read on the
TOTALS (base + extras); the constants (slope 2·, θ_babble 0.7) are fitted to §0(b)'s measured boredom
distribution and DECLARED here, like §2.2's own.

## A3 · The deterministic draw (every probability in this law)

No shared RNG stream is consumed (the OFF twin's stream must stay untouched). Every gate draws
`u = sha256(f"{seed}|{seq}|{purpose}")[:4 bytes] / 2**32`, a pure function of the life's seed and the
tape row's own seq — replay-identical, OFF-identical. (The replay-determinism form of I2, as amended by
the verifier's V6, is preserved.)

## A4 · The gain path and the eye, as wired

- The arousal/fatigue gains ride `genome/predict.py:266 modulate()` exactly as §2.3 signed
  (`lr × clip(0.5 + 3e, 0.5, 2) × g_a × g_f`, `g_a = clip(1 + 2·(a − 0.3), 0.5, 2)`, `g_f = 1 − 0.5·f`):
  the Predictor gains a `homeostasis=None` construction parameter, threaded at BOTH build sites (the init
  at mind.py:636 and the resume-path rebuild — the REGISTERS/precision precedent's own threading), default
  None = byte-identical.
- The eye's +1 fixation lands at the `_consume_eye` call site (mind.py): `F_eff = F + 1` when arousal is
  declared and a > 0.7 — a pure function of the drive state, which is a pure function of the tape.
- The drive state updates ONCE per canvas at the canvas-row site (mind.py:2955's `journal_row`), from that
  canvas's own `err`; the row gains ONE additive key `drives: {a, b, f}` when declared (the `front` key's
  own precedent — absent otherwise, byte-identical). The sleep boundary's fatigue clause lands in
  `_maybe_sleep` (mind.py:3185): `or (fatigue declared and f ≥ 0.95 and since ≥ every // 2)`, the boundary
  advancing by the count at regular firings and snapping to `t` at forced ones; every boundary (declared
  fatigue) resets `f ← f·(1 − ζ)`.
- The mouth's suppression (§2.4): fatigue declared and f > 0.9 → `_maybe_say` and the babble extras both
  return without saying. The exclaim: one repeat of the last say when a > 0.7 within 5 canvases of a
  surprise ≥ 2·s̄, journaled `exclaim: true`, at most one per canvas.

*Signed by the seat alone under the law's own form, 2026-10-12: the mechanisms fitted to the real
architecture, the marks untouched, the bars unmoved.*
