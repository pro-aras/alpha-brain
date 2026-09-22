#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-22 11:02 +0400 — re-read closed lives' 8 h verdicts from a PINNED reader checkout, within the cores.
# The 2026-09-22 morning: six readers × 8 workers on 16 cores starved the lives (seam-1 / L5 fell 6,917 / 5,941 rows behind their
# tapes) and crawled on INDUCE's per-episode copies; the first reads were abandoned (readings/verdict-8h-abandoned-<commit>).
# usage: tools/lives/reread.sh <pinned-code-dir> <workers> <name>[:<genome-rel>] ...   — runs the names in PAIRS, each pair in parallel.
set -u
CODE="${1:?pinned code dir}"; WORKERS="${2:?workers}"; shift 2
LIVES=/data/dev/genome-lives
one() {   # <name> <genome-rel>
  local n="$1" g="$2" root="$LIVES/$1"
  cd "$CODE" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 5 python3 -u tools/verdict_g4.py --root "$root" --genome "$root/code/$g" \
    --out "$root/readings/verdict-8h" --hours 8 --slice-hours 2 --regime-step 25 --workers "$WORKERS" --unit "creature-g5@$n.service" \
    > "$root/readings/verdict-8h.log" 2>&1; echo "[$n] exit=$? $(date '+%H:%M')" >> "$root/readings/verdict-8h.log"
}
while [ $# -gt 0 ]; do
  a="$1"; b="${2:-}"; shift; [ -n "$b" ] && shift
  na="${a%%:*}"; ga="${a#*:}"; [ "$ga" = "$a" ] && ga="genome/G5.genome"
  echo "[reread] $(date '+%H:%M') start $na$( [ -n "$b" ] && echo " + ${b%%:*}") from $CODE at $(git -C "$CODE" rev-parse --short HEAD), $WORKERS workers each"
  one "$na" "$ga" &
  if [ -n "$b" ]; then nb="${b%%:*}"; gb="${b#*:}"; [ "$gb" = "$b" ] && gb="genome/G5.genome"; one "$nb" "$gb" & fi
  wait
  for x in "$na" ${b:+${b%%:*}}; do echo "[reread] $(date '+%H:%M') $x: $(grep -E '^VERDICT ' "$LIVES/$x/readings/verdict-8h.log" | tail -1 | cut -c1-200)"; done
done
