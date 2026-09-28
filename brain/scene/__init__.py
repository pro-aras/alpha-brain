"""brain.scene — S1a «THE SCENE-TALK WORLD» (docs/brain/r3/PREREG-R3-TONIGHT.md §S1a, signed 2026-09-28 11:42 +0400,
sha256 18250d201b6aecbdc95058267f6cab163ca1450e82f4f1d8f9724a1849215968).

edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:00 +0400 — new package.

  world.py     the things, the scenes, the parent's grammar, the held-outs, the truth (OUTSIDE the learner)
  eye.py       one genome.gaze.glances call per scene; the union-find thing hypotheses; the forced window (ORACLE-TRUTH)
  cache.py     the per-seed glance cache (brain.glance_cache's CacheWriter/Cache + sidecars), written once, read by every arm
  slda.py      a verbatim copy of b1-reader's StreamingLDA (P-ORACLE's reader), pinned to its source
  learners.py  A-RW and the LDA oracle reader; the feeds take a referent index from the caller, never the truth
  marks.py     M1, M2a, M2b, M6 with the grading hygiene (reads the truth — grading only)
  run.py       stage −1, the toy, THE FIRST GATE, the prices, the full run, the grader
"""
PREREG_SHA256 = "18250d201b6aecbdc95058267f6cab163ca1450e82f4f1d8f9724a1849215968"
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 13:05 +0400 — AMENDMENT 2 (docs/brain/r3/PREREG-R3-TONIGHT-AMEND-2.md, genome-wt-brain3
# d54e6c0), the sha of the text this code implements; checked at every run beside the signed PREREG's.
AMEND2_SHA256 = "414b320179a74aade87cfda0896637b43f28af1cf8700b0a8a88ae23fb164ed3"
