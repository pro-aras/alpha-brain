#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-24 07:34 +0400 — read closed 8 h lives from a PINNED reader tree, N at a time, with per-rung extra flags.
# Born for the A4 ladders' reads (A4-LADDER-2-PREREG §7 + ADDENDUM §7(2); READER-V35-REPORT §7): reread.sh's shape, plus
#   • extra reader args per rung (R0b: --identity-root; R1–R3, R5: --control-root), passed after the genome rel;
#   • --skip-random unless the rung's genome declares EVOLVE (the 20 random twins feed only the EVOLVE mark — #239 (9));
#   • PAR reads at a time (default 3; each read spawns <workers> replay processes) — price it against the box first (#236);
#   • the out dir carries a TAG so a re-read never overwrites a finished record (#234: controls run beside a record, never in it).
# usage: PAR=3 tools/lives/a4_read.sh <pinned-code-dir> <workers> <tag> <name>|<genome-rel>[|<extra reader args>] ...
# A read writes ONLY under <root>/readings/ (verdict-8h-<tag>/ and its .log); the root's tape/journal/state are read, never written.
set -u
CODE="${1:?pinned code dir}"; WORKERS="${2:?workers}"; TAG="${3:?tag}"; shift 3
LIVES=/data/dev/genome-lives; PAR="${PAR:-3}"; export TMPDIR=/data/dev/scratch-reads/tmp; mkdir -p "$TMPDIR"
one() {   # <name> <genome-rel> <extra...>
  local n="$1" g="$2"; shift 2; local root="$LIVES/$n" out="$LIVES/$n/readings/verdict-8h-$TAG" skip="--skip-random"
  grep -qE '^EVOLVE' "$root/code/$g" && skip=""
  echo "[a4_read] $(date '+%H:%M:%S') start $n · code $(git -C "$CODE" rev-parse --short HEAD) · genome $g · workers $WORKERS · ${skip:-randoms ON} · extra: $*" | tee -a "$out.log"
  ( cd "$CODE" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 5 python3 -u tools/verdict_g4.py --root "$root" --genome "$root/code/$g" \
      --out "$out" --hours 8 --slice-hours 2 --regime-step 25 --workers "$WORKERS" --unit "creature-g5@$n.service" $skip "$@" ) >> "$out.log" 2>&1
  echo "[a4_read] $(date '+%H:%M:%S') $n exit=$? · $(grep -aE '^VERDICT ' "$out.log" | tail -1 | cut -c1-200)" | tee -a "$out.log"
}
running=0
for spec in "$@"; do
  IFS='|' read -r n g extra <<< "$spec"; [ -z "${g:-}" ] && g="genome/ALPHA4.genome"
  one "$n" "$g" ${extra:-} &
  running=$((running+1)); if [ "$running" -ge "$PAR" ]; then wait -n; running=$((running-1)); fi
done
wait; echo "[a4_read] $(date '+%H:%M:%S') all done"
