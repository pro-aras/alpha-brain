#!/bin/bash
# the instrument's mutation sweeps, one after another in ONE capped scope (called through scratch/capped.sh)
set -u
cd /data/dev/genome-wt-evolve-cal-1003 || exit 2
SW=docs/organism/evolve/scripts
O=/data/dev/swarm/2026-10-03/evolve-cal-records/sweeps
mkdir -p $O
rc=0
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_bands.py --tests tests.tools.test_evolve_cal_gate --mutants $SW/mutants_cal_bands.json --out $O/bands > $O/bands.out 2>&1; echo "bands exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal.py --tests tests.tools.test_evolve_cal_bands_build --mutants $SW/mutants_cal_bandsbuild.json --out $O/bandsbuild > $O/bandsbuild.out 2>&1; echo "bandsbuild exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve.py --tests tests.tools.test_evolve_cal_gate tests.tools.test_evolve_cal_d3 tests.tools.test_evolve_cal_round.TestConfirmationRound tests.tools.test_evolve_cal_round.TestGradeTwinCost --mutants $SW/mutants_cal_evolve_pure.json --out $O/evolve-pure > $O/evolve-pure.out 2>&1; echo "evolve-pure exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve_cal.py --tests tests.tools.test_evolve_cal_twin --mutants $SW/mutants_cal_twin.json --out $O/twin > $O/twin.out 2>&1; echo "twin exit $?" >> $O/SWEEPS.done
python3 -B $SW/mutsweep.py --tree . --module tools/evolve.py --tests tests.tools.test_evolve_cal_round.TestRound --mutants $SW/mutants_cal_evolve_round.json --out $O/evolve-round > $O/evolve-round.out 2>&1; echo "evolve-round exit $?" >> $O/SWEEPS.done
echo "ALL SWEEPS RAN" >> $O/SWEEPS.done
