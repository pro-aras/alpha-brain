#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 22:41 +0400 — PREREG-EVOLVE-CAL AMENDMENT 3 (the verifier's limits (3) and (4), the seat's 22:32 line): the A0 twins' own
# memory.stat «anon» figure, sampled every 10 s from each running slot scope's cgroup, beside MemAvailable and SwapFree, so the seat's two-twin rule rests on a measured number
# and not on RSS (which counts shared file-backed pages) or on memory.peak (which counts page cache).
# usage: anon_sampler.sh <out.csv> <unit that bounds the sampling (the queue's transient unit)> [scope glob, default 'slot-integrator-evcal-*.scope']
# It holds no memory worth the name (a shell loop reading four small files per scope), writes one csv line per scope per tick, and ends when the bounding unit is no longer active
# (after one last tick). Columns: time, scope, anon_kb, file_kb, shmem_kb, current_kb, peak_kb, memavail_kb, swapfree_kb. Nothing here is a verdict: it is a series.
set -u
OUT=${1:?out.csv}; UNIT=${2:?bounding unit}; GLOB=${3:-slot-integrator-evcal-*.scope}
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}
[ -s "$OUT" ] || echo "time,scope,anon_kb,file_kb,shmem_kb,current_kb,peak_kb,memavail_kb,swapfree_kb" > "$OUT"
tick() {
  local now avail swapf u cg d anon file shmem cur peak
  now=$(date '+%F %T')
  avail=$(awk '$1=="MemAvailable:"{print $2}' /proc/meminfo); swapf=$(awk '$1=="SwapFree:"{print $2}' /proc/meminfo)
  for u in $(systemctl --user list-units --no-legend --plain "$GLOB" 2>/dev/null | awk '{print $1}'); do
    cg=$(systemctl --user show -p ControlGroup --value "$u" 2>/dev/null); d="/sys/fs/cgroup$cg"
    [ -n "$cg" ] && [ -r "$d/memory.stat" ] || continue
    anon=$(awk '$1=="anon"{print int($2/1024)}' "$d/memory.stat"); file=$(awk '$1=="file"{print int($2/1024)}' "$d/memory.stat")
    shmem=$(awk '$1=="shmem"{print int($2/1024)}' "$d/memory.stat")
    cur=$(awk '{print int($1/1024)}' "$d/memory.current" 2>/dev/null); peak=$(awk '{print int($1/1024)}' "$d/memory.peak" 2>/dev/null)
    echo "$now,$u,${anon:-},${file:-},${shmem:-},${cur:-},${peak:-},$avail,$swapf" >> "$OUT"
  done
}
while systemctl --user is-active --quiet "$UNIT"; do tick; sleep 10; done
tick
