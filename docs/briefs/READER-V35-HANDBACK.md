# READER v3.5 — HAND-BACK (kept current while the lane runs; the last stamp is the state)
*Claude (Opus 5.5, reader v3.5 builder). Branch `reader-v35` in `/data/dev/genome-wt-reader35` (from a4-integration b84bad8 + master b650ebe). Stamp: 2026-09-24 06:07 +0400.*

## THE RESULT FIRST
**IDENTITY (R0b's mark, ADDENDUM §7(2)'s operational form) reads FAIL at 8 h on BOTH pairs the brief named** — a4l2-cost vs a4l-cost and a4l2-floor vs a4l2-cost (same code C2). The stream part reproduces the seat's 2 h numbers EXACTLY (pinned in `TheSeatsTwoHourNumbers`); at 8 h the maker stream diverges (a4l2-floor vs a4l2-cost: a4l2-cost's `answering` canvas q-79, the rest identical one row later; a4l2-cost vs a4l-cost: at maker 2872, near the 4 h arrival) and the counts at equal per-source canvas counts part from canvas 2291 on, on every pair, by ±1–5 (an error birth landing on a neighbouring canvas when the senses interleave differently). The same-code pair shows the same class at the same canvas: **between-LIVES, not the machinery's.** Logs: `/data/dev/scratch-reader35/identity-*.log`, `reproduce-2h-*.log`. The bar is untouched; the classification is in the report.

## Done
1. Step 1 — the merge (f90cd08): master's v3.4 [LAG] cut + a4-integration's ladder additions; three hunks of `tools/verdict_g4.py` resolved additively; READER_VERSION v3.5.
2. Step 2 — `tools/lives/check.py` (ddd09a6): the glances line gated on the genome's own `; drop confirmed` clause; `tests/creature/test_lives_check_drop.py`. On the six closed 8 h copies: five «not declared», ALL «OK: dropped == confirmed» (`check-glances-6.log`).
3. Step 3 — the ladder-2 marks (be1d316 + abfd017): IDENTITY, X1_LOCK/X2_SUCCESS, LINE, NURSERY/NURSERY_READ, DROP_EQ, CHAT_COUNTERS, A1_NULL/A2_SEEN; `tests/creature/test_reader_v35_marks.py` (33 tests).
4. Step 4 (first run, be1d316): `Ran 1718 tests in 1075.343s` · `FAILED (failures=2, skipped=7, expected failures=6)` — the two failures were the DROP builder's check.py fixtures (no genome at the root); fixed in abfd017 (the fixtures carry A4L-DROP.genome; the PREREG decides).

## Not done (at this stamp)
- Step 4's run on the final bytes abfd017 (RUNNING at this stamp: `/data/dev/scratch-reader35/suite.log`, `suite.exit`).
- Step 5's heavy dry run on the a4l-cost copy (queued after the suite, with `--identity-root` the a4l2-cost copy).
- The report's last sections.

## The next command
`cat /data/dev/scratch-reader35/suite.exit; grep -n '^Ran \|^OK\|^FAILED' /data/dev/scratch-reader35/suite.log` — then the dry run:
`cd /data/dev/genome-wt-reader35 && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 19 python3 tools/verdict_g4.py --root /data/dev/scratch-reader35/a4l-cost-copy --genome /data/dev/scratch-reader35/a4l-cost-copy/code/genome/ladder/A4L-COST.genome --hours 8 --skip-twins --skip-random --workers 1 --identity-root /data/dev/scratch-reader35/a4l2-cost-copy --identity-hours 8 --out /data/dev/scratch-reader35/a4l-cost-read`
