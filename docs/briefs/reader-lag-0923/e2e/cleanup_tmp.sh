#!/bin/bash
# READER-LAG-0923: the named cleanup of THIS lane's leaked temp roots under scratch/tmp (#216/#236: name the list first — pattern, age, count,
# size — check open handles, remove only what was named; nothing outside scratch/tmp is touched).
set -u
T=/data/dev/genome-wt-reader-lag/scratch/tmp
cd "$T" || exit 2
echo "named at $(date '+%Y-%m-%d %H:%M:%S %z'):"
for pat in 'creature-replay-*' 'reader-lag-*' 'tmp*'; do
  n=$(find . -maxdepth 1 -mindepth 1 -name "$pat" | wc -l); s=$(find . -maxdepth 1 -mindepth 1 -name "$pat" -print0 | du -shc --files0-from=- 2>/dev/null | tail -1 | cut -f1)
  echo "  pattern $pat: $n entries, $s, mtimes $(find . -maxdepth 1 -mindepth 1 -name "$pat" -printf '%TH:%TM\n' | sort | sed -n '1p;$p' | tr '\n' ' ')"
done
other=$(find . -maxdepth 1 -mindepth 1 ! -name 'creature-replay-*' ! -name 'reader-lag-*' ! -name 'tmp*' | wc -l); echo "  entries matching NONE of the patterns (kept): $other"
busy=$(find . -maxdepth 1 -mindepth 1 \( -name 'creature-replay-*' -o -name 'reader-lag-*' -o -name 'tmp*' \) -exec fuser -s {} \; -print 2>/dev/null | wc -l); echo "  entries with an open handle (kept): $busy"
# a process of THIS lane = one whose cwd is under this worktree (other lanes run the same commands in their own trees); $$ and $PPID excluded (#236 e)
mine=0; for p in $(pgrep -f 'verdict_g4\.py|unittest|build_racy_root|build_lag_root|gate_g4\.py'); do [ "$p" = "$$" ] || [ "$p" = "$PPID" ] && continue; case "$(readlink /proc/$p/cwd 2>/dev/null)" in /data/dev/genome-wt-reader-lag*) mine=$((mine+1)); echo "  lane process still running: pid $p $(readlink /proc/$p/cwd)";; esac; done
if [ "$mine" -gt 0 ]; then echo "a process of this lane is still running — NOT removing"; exit 3; fi
find . -maxdepth 1 -mindepth 1 \( -name 'creature-replay-*' -o -name 'reader-lag-*' -o -name 'tmp*' \) ! -exec fuser -s {} \; -print0 | xargs -0 rm -rf --
echo "after: $(find . -maxdepth 1 -mindepth 1 | wc -l) entries, $(du -sh . | cut -f1)"
