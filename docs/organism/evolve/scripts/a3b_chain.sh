#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:0x +0400 — AMENDMENT 3b's runs, queued THROUGH SLOT while the seat's SEAT-HOLD (the quiet window) lasts: every step is one `slot` call, so it WAITS
# (WAIT-HOLD) and starts at the lift; nothing here runs outside slot. Each step writes its own log and exit file under <out>; the verdict of a step is read from ITS log's «Ran N … OK/FAILED» line.
# usage: a3b_chain.sh <RED sha (tests only)> <GREEN sha (code)> <out dir>
set -u
RED=${1:?red sha}; GREEN=${2:?green sha}; O=${3:?out}
SLOT=/data/dev/swarm/bin/slot
mkdir -p "$O"
echo "$(date '+%F %T %z') chain queued: RED $RED, GREEN $GREEN" >> "$O/chain.clock"
MODS3="tests.tools.test_evolve_cal_analyse tests.tools.test_evolve_cal_twin tests.tools.test_evolve_cal_queue"
MODS8="tests.tools.test_evolve_cal_analyse tests.tools.test_evolve_cal_bands_build tests.tools.test_evolve_cal_d3 tests.tools.test_evolve_cal_gate tests.tools.test_evolve_cal_queue tests.tools.test_evolve_cal_round tests.tools.test_evolve_cal_twin tests.tools.test_evolve_worker"
step() {   # label sha worktree-suffix modules logbase
  local label=$1 sha=$2 wt=/data/dev/genome-wt-evolve-cal-$3 mods=$4 base=$5
  SLOT_MEM=2G "$SLOT" integrator "$label" -- bash -c "
    set -u
    [ -d $wt ] || git -C /data/dev/genome worktree add --detach $wt $sha || exit 90
    git -C $wt checkout -q --detach $sha || exit 91
    [ -z \"\$(git -C $wt status --porcelain)\" ] || exit 92
    cd $wt && mkdir -p scratch/tmp
    echo \"# $label on \$(git rev-parse HEAD), started \$(date '+%F %T %z')\" > $base.log
    TMPDIR=$wt/scratch/tmp PYTHONPATH=. OPENBLAS_NUM_THREADS=1 /usr/bin/python3 -B -u -m unittest $mods >> $base.log 2>&1
    rc=\$?; echo \$rc > $base.exit; exit \$rc" > /dev/null 2>&1
  echo "$(date '+%F %T %z') $label exit $(cat "$base.exit" 2>/dev/null || echo MISSING): $(grep -a -E '^(Ran [0-9]+ tests|OK|FAILED)' "$base.log" 2>/dev/null | tr '\n' ' ')" >> "$O/chain.clock"
}
step a3b-red "$RED" red "$MODS3" "$O/red-3modules"
step a3b-green3 "$GREEN" green "$MODS3" "$O/green-3modules"
step a3b-green-all "$GREEN" green "$MODS8" "$O/green-all"
SLOT_MEM=1G "$SLOT" integrator a3b-arith -- bash -c "cd /data/dev/genome-wt-evolve-cal-green && PYTHONPATH=. /usr/bin/python3 -B docs/organism/evolve/scripts/a3b_arith.py > $O/a3b_arith.out 2>&1; echo \$? > $O/a3b_arith.exit" > /dev/null 2>&1
echo "$(date '+%F %T %z') a3b-arith exit $(cat "$O/a3b_arith.exit" 2>/dev/null || echo MISSING)" >> "$O/chain.clock"
SLOT_MEM=2G "$SLOT" integrator a3b-sweeps -- bash -c "bash /data/dev/genome-wt-evolve-cal-green/docs/organism/evolve/scripts/run_sweeps_a3b.sh /data/dev/genome-wt-evolve-cal-green $O/sweeps > $O/sweeps-driver.out 2>&1" > /dev/null 2>&1
echo "$(date '+%F %T %z') a3b-sweeps done: $(tr '\n' ' ' < "$O/sweeps/SWEEPS.done" 2>/dev/null)" >> "$O/chain.clock"
echo "chain end" >> "$O/chain.clock"
