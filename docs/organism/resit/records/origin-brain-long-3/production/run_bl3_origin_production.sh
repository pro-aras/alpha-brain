#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:59 +0400 (the file's own mtime, 21:59:55; the first draft said 22:00 «from `date`», typed ahead of the clock — corrected) — the seat's 21:34 order for brain-long-3's production FALLBACK ORIGIN, as ONE script so no flag is typed twice:
#   reader  = the final reader checkout (a detached worktree of resit-1003 @ 916f741; resit.py sha256 bacf8fc3…)
#   state   = the seat's read-only copy of state/prev taken 19:30:14 (never touched here)
#   reason  = the seat's text VERBATIM (claims-scratch3/bl3-origin-reason.txt, sha256 8a264d2a…)
#   grader  = the pinned checkout of d2fe75b at the daily unit's own path
#   out     = /data/dev/brain-runs/resit/brain-long-3 (the production folder; this run is the ONLY writer of its first row)
# The run's stdout/stderr/time/exit go to claims-scratch3/bl3-prod-* (NOT into OUT, so OUT holds only what the reader writes). Run it through slot: SLOT_MEM=4G (the rehearsal's cgroup peak was 2,319 MB; 1.3x = 3,015 MB).
set -u
READER=/data/dev/genome-wt-claims-reader-916f741
OUT=/data/dev/brain-runs/resit/brain-long-3
LOGS=/data/dev/swarm/2026-10-03/claims-scratch3
REASON="$(cat $LOGS/bl3-origin-reason.txt)"
cd "$READER" || exit 97
[ -e "$OUT" ] && { echo "REFUSED: $OUT already exists (the production origin is written once)"; exit 96; }
mkdir -p "$OUT" || exit 95
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /usr/bin/time -v -o "$LOGS/bl3-prod-time.txt" \
  python3 -B -I tools/brain/resit.py run --mode origin --origin-kind fallback_copy --reason "$REASON" \
  --state /data/dev/brain-runs/day1003/brain-long-3-origin-fallback/copy-20261003-193014 \
  --root /data/dev/genome-lives/brain-long-3 --code /data/dev/genome-lives/brain-long-3/code \
  --items-root /data/dev/genome-lives/brain-long-2 --grader-code /data/dev/brain-runs/resit/grader-d2fe75b \
  --out "$OUT" --scored /data/dev/brain-runs/scene-s1b1r > "$LOGS/bl3-prod-stdout.txt" 2> "$LOGS/bl3-prod-stderr.txt"
RC=$?
echo "$RC" > "$LOGS/bl3-prod-exit"
exit "$RC"
