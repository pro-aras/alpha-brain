#!/usr/bin/env bash
# edit: Claude (Fable 5.1), 2026-09-22 12:16 +0400 — RE-GRADE closed lives' 8 h reads under a newer READER without replaying: the twins are
# reused (--reuse), the marks recomputed, into a HARD-LINK COPY of the record (readings/verdict-8h-<tag>/) so the original read stays
# whole. Born on reader v3.1 (PREREG §18 addendum 4): the plant's window, every cap refusal, the null by majority.
# usage: tools/lives/regrade.sh <code-dir> <tag> <name>[:<genome-rel>] ...
set -u
CODE="${1:?code dir}"; TAG="${2:?tag}"; shift 2
LIVES=/data/dev/genome-lives
for a in "$@"; do
  n="${a%%:*}"; g="${a#*:}"; [ "$g" = "$a" ] && g="genome/G5.genome"
  root="$LIVES/$n"; src="$root/readings/verdict-8h"; out="$root/readings/verdict-8h-$TAG"
  [ -f "$src/results.json" ] || { echo "[regrade] $n: no completed read at $src"; continue; }
  rm -rf "$out"; cp -al "$src" "$out" && rm -f "$out/VERDICT.md" "$out/results.json"
  ( cd "$CODE" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 5 python3 -u tools/verdict_g4.py --root "$root" --genome "$root/code/$g" \
      --out "$out" --hours 8 --slice-hours 2 --regime-step 25 --workers 4 --unit "creature-g5@$n.service" --reuse > "$out.log" 2>&1 )
  echo "[regrade $TAG] $n at $(git -C "$CODE" rev-parse --short HEAD): $(grep -E '^VERDICT ' "$out.log" | tail -1 | cut -c1-160)"
done
