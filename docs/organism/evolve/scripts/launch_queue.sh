#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:59 +0400 — PREREG-EVOLVE-CAL: launch a twin queue as a transient user unit, on a CLEAN detached checkout of an exact sha.
# usage: bash launch_queue.sh <sha> <list.tsv (path inside the checkout)> <out-root> <unit-suffix> [cp] [slice] [from-seq] [to-seq] [slot-mem]
# A long run spawns many processes over many hours, each importing whatever is in the working tree at ITS start: the runs therefore never use the builder's own
# worktree. This script makes (or reuses) /data/dev/genome-wt-evolve-cal-run, refuses unless it is clean and its HEAD is exactly <sha>, records the sha beside the
# results, and starts `python3 -m tools.evolve_cal_queue run` as the unit swarm-integrator-evcal-<suffix> (one twin at a time, each through slot at SLOT_MEM).
set -u
SHA=${1:?sha}; LIST=${2:?list}; OUT=${3:?out-root}; SUFFIX=${4:?unit suffix}
CP=${5:-/data/dev/swarm/2026-10-03/evolve-cal-scratch/cps/32}
SLICE=${6:-/data/dev/swarm/2026-10-03/evolve-cal-scratch/slices/S1}
FROM=${7:-304002}; TO=${8:-308667}; MEM=${9:-8G}
RUN=/data/dev/genome-wt-evolve-cal-run
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}
if [ ! -d "$RUN" ]; then git -C /data/dev/genome worktree add --detach "$RUN" "$SHA" || exit 2; fi
git -C "$RUN" checkout -q --detach "$SHA" || { echo "STOP: cannot check out $SHA in $RUN"; exit 3; }
[ -z "$(git -C "$RUN" status --porcelain)" ] || { echo "STOP: $RUN is not clean"; exit 3; }
[ "$(git -C "$RUN" rev-parse HEAD)" = "$(git -C /data/dev/genome rev-parse "$SHA")" ] || { echo "STOP: $RUN is not at $SHA"; exit 3; }
[ -f "$RUN/$LIST" ] || { echo "STOP: no list $RUN/$LIST"; exit 3; }
if [ "${DRY:-0}" = 1 ]; then   # prints the planned slot commands; creates nothing, starts nothing
  cd "$RUN" && env PYTHONPATH=. /usr/bin/python3 -B -m tools.evolve_cal_queue run --list "$LIST" --cp "$CP" --slice-root "$SLICE" --from-seq "$FROM" --to-seq "$TO" --out-root "$OUT" --lane integrator --slot-mem "$MEM" --dry-run
  exit $?
fi
mkdir -p "$OUT" && git -C "$RUN" rev-parse HEAD >> "$OUT/CODE-SHA.txt"
systemd-run --user --unit="swarm-integrator-evcal-$SUFFIX" --collect -p WorkingDirectory="$RUN" \
  -- env PYTHONPATH=. /usr/bin/python3 -B -m tools.evolve_cal_queue run --list "$LIST" --cp "$CP" --slice-root "$SLICE" --from-seq "$FROM" --to-seq "$TO" \
     --out-root "$OUT" --lane integrator --slot-mem "$MEM"
echo "launched unit swarm-integrator-evcal-$SUFFIX on $(git -C "$RUN" rev-parse --short HEAD); results in $OUT; each twin's log is $OUT/<label>.log"
