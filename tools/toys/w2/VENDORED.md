# VENDORED — the files and functions the W2 bench carries from the T-L4 branch (never merged into master), each
# byte-identical to its source, with its source sha. The verifier can re-check: sha256sum against t-l4-1003's files.

- `tools/toys/w2/grade.py`  == `tools/toys/tl4/grade.py` at t-l4-1003 ffe633b (file sha256
  `4867a1065bc67b973e9c94ce0b851fbfbc7082a7068737f093b6594b00d914a3`) — T-L4 §5-§6's grader, verbatim (auc, q95_of,
  flatness with the AMENDMENT-1/2 ruled `center`, m1_rule, m2_rule, assert_derangement, se0, family_T, naming_correct,
  verdict).
- `tools/toys/w2/tl4_arith.py` — the function BODIES of `tools/toys/tl4/arms.py` at t-l4-1003 ffe633b (file sha256
  `396d556c27a029d2f321aa4e4f64b32b32bfe505dad8694cedb4a614ed22764c`) verbatim: `oracle_fit`, `oracle_scores`,
  `const_scores`, `scene_scores`, `row_probs`, `score_window` (T-L4's arms.py:193-208, 272-319), vendored with this
  header naming the source and its sha; the module docstring and imports are the bench's own.

— Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:44 +0400
