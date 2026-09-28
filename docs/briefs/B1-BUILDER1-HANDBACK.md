# B1 · BUILDER 1 (Opus 5.5) — HAND-BACK (arm D, the rule library)

*edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:39 +0400 — skeleton written while waiting for the frozen protocol (#239 (19):
a builder that dies mid-wait leaves its plan on disk). Updated at every step.*

## State (read from the box, not from this sentence — `git -C /data/dev/genome-wt-b1-library log --oneline`)
- Worktree `/data/dev/genome-wt-b1-library`, branch `b1-library` from master 94546ce.
- DONE: the design on paper — `docs/briefs/B1-BUILDER1-REPORT.md` §1–§4 (the DSL, the atoms and why none is a tested
  relation, the enumeration order, the fit, the budget, the evaluator, `state_sha`'s scope, the compressor, R1–R9,
  the predicted findings).
- NOT STARTED: any arm code. The rule (the dispatch): no arm code against a guessed protocol.

## Next step, in order
1. Poll `git -C /data/dev/genome-wt-b1int log --oneline -3` until Builder 2's frozen `brain/protocol.py` is on
   `b1-integration`; then `git merge b1-integration` into `b1-library`.
2. Re-check byte for byte against the frozen file: `Answer.value` for PICK = the candidate INDEX; training ASKs go
   through `fit_event` (answer(learn=True) first, then fit_event); SLEEP never goes through `fit_event`; the
   `rule()` executable's signature; `why()`'s return; `cost()`'s shape; the operand encoding; the FEEDBACK `right`.
3. Code under `brain/arms/library/` (dsl, enumerate, evaluate, compress, arm) and tests under
   `tests/brain/arms_library/` — never the word that names the graders' answer file anywhere in `brain/arms/`.
4. Toys (XOR 100 % + its control; the planted relation from 3 examples + its shuffled twin), the §3.1 identity
   test (twice-and-planted, resume at 1,000), the 100-candidate cost sample — each with its command named.
5. Report §5 filled; this file updated; SubagentHandback.

## RAISED (report §4): R1 fit floor · R2 no sleep between P1–P4 · R3 §3.1's plant may land outside 2,000 events ·
## R4 perceptual families inexpressible · R5 why() literal → U4a 0 · R6 the budget number · R7 fixed-point sim ·
## R8 order wraps · R9 the snapshot seam
