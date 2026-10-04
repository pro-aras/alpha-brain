#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:0x +0400 — AMENDMENT 3b's runs, queued THROUGH SLOT while the seat's SEAT-HOLD (the quiet window) lasts: every step is one `slot` call, so it WAITS
# (WAIT-HOLD) and starts at the lift; nothing here runs outside slot. Each step writes its own log and exit file under <out>; the verdict of a step is read from ITS log's «Ran N … OK/FAILED» line.
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:12 +0400 — two RED commits now (A3b's tests, then A′'s tests) and one GREEN (the code of both): RED1 and RED2 are checked out DETACHED and run
# against exactly the tests written before the code they test; GREEN runs the whole evolve-cal group; then the arithmetic and the sweeps.
# usage: a3b_chain.sh <RED1 sha: A3b tests only> <RED2 sha: A′ tests, A3b code present> <GREEN sha: all code> <out dir>
set -u
RED1=${1:?red1 sha}; RED2=${2:?red2 sha}; GREEN=${3:?green sha}; O=${4:?out}
SLOT=/data/dev/swarm/bin/slot
mkdir -p "$O"
echo "$(date '+%F %T %z') chain queued: RED1 $RED1, RED2 $RED2, GREEN $GREEN" >> "$O/chain.clock"
MODS_RED1="tests.tools.test_evolve_cal_analyse tests.tools.test_evolve_cal_twin tests.tools.test_evolve_cal_queue"
MODS_RED2="tests.tools.test_evolve_cal_gate tests.tools.test_evolve_cal_analyse"
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
step a3b-red1 "$RED1" red1 "$MODS_RED1" "$O/red1"
step a3b-red2 "$RED2" red2 "$MODS_RED2" "$O/red2"
step a3b-green-all "$GREEN" green "$MODS8" "$O/green-all"
SLOT_MEM=1G "$SLOT" integrator a3b-arith -- bash -c "cd /data/dev/genome-wt-evolve-cal-green && PYTHONPATH=. /usr/bin/python3 -B docs/organism/evolve/scripts/a3b_arith.py > $O/a3b_arith.out 2>&1; echo \$? > $O/a3b_arith.exit" > /dev/null 2>&1
echo "$(date '+%F %T %z') a3b-arith exit $(cat "$O/a3b_arith.exit" 2>/dev/null || echo MISSING)" >> "$O/chain.clock"
SLOT_MEM=2G "$SLOT" integrator a3b-sweeps -- bash -c "bash /data/dev/genome-wt-evolve-cal-green/docs/organism/evolve/scripts/run_sweeps_a3b.sh /data/dev/genome-wt-evolve-cal-green $O/sweeps > $O/sweeps-driver.out 2>&1" > /dev/null 2>&1
echo "$(date '+%F %T %z') a3b-sweeps done: $(tr '\n' ' ' < "$O/sweeps/SWEEPS.done" 2>/dev/null)" >> "$O/chain.clock"
echo "chain end" >> "$O/chain.clock"
