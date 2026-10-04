#!/bin/bash
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 23:1x +0400 — STAGE A0 of PREREG-EVOLVE-CAL, launched at the lift of the seat's SEAT-HOLD from a clean DETACHED checkout of 74b0fc1 (the commit that carries the three signatures of
# AMENDMENT 3): the incumbent and one twin at 1e-3 and 1e-2 on the FULL S1 (4,665 rows), ONE twin at a time, each through slot at SLOT_MEM=12G (the verifier's limit 3: the first 4,665-row twin runs above the 8G
# of the 1,000-row twins and its END peak is read before any other cap is fixed), plus the 10 s cgroup memory.stat anon sampler for the seat's two-twin rule.
set -u
export XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
SHA=74b0fc18a972193a677a3e863b09ce3788576de5
W=/data/dev/genome-wt-evolve-cal-1003
OUT=/data/dev/swarm/2026-10-03/evolve-cal-records/n1
S=/data/dev/swarm/2026-10-03/evolve-cal-scratch
[ ! -e /data/dev/swarm/slots/SEAT-HOLD ] || { echo "STOP: SEAT-HOLD exists"; exit 3; }
bash "$W/docs/organism/evolve/scripts/launch_queue.sh" "$SHA" docs/organism/evolve/records/lists/N1-A0.tsv "$OUT" a0 "$S/cps/32" "$S/slices/S1" 304002 308667 12G || exit $?
systemd-run --user --unit=swarm-integrator-evcal-a0-sampler --collect -- bash "$W/docs/organism/evolve/scripts/anon_sampler.sh" "$OUT/anon-a0.csv" swarm-integrator-evcal-a0.service
echo "$(date '+%F %T %z') A0 launched from $SHA (unit swarm-integrator-evcal-a0, sampler swarm-integrator-evcal-a0-sampler); results in $OUT"
