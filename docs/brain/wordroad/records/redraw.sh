#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — PREREG-WORD-ROAD §5: the cache pin's price. Run ONLY with every life closed.
set -u
CODE=/data/dev/genome-wt-wordroad; ROOT=/data/dev/brain-runs/scene-organ-hear; OLD=/data/dev/brain-runs/scene-organ-fm6
O=/data/dev/brain-runs/day0929/wordroad; L=$O/logs
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
cd $CODE || exit 2
C=$O/redraw-clock.txt
n=$(systemctl --user list-units 'creature*' --state=active --no-legend --no-pager | grep -c .)
[ "$n" = "0" ] || { echo "STOP: $n creature unit(s) active" | tee -a $C; exit 3; }
date "+%Y-%m-%d %H:%M:%S %z start at $(git rev-parse --short HEAD)" > $C
step() { name="$1"; shift; "$@" > $L/redraw-$name.log 2>&1; rc=$?; echo "$(date '+%H:%M:%S') $name exit $rc" >> $C; return $rc; }
[ -e $ROOT ] && { echo "STOP: $ROOT exists (a fresh root only)" | tee -a $C; exit 3; }
mkdir -p $ROOT && rsync -a --exclude='cache/' --exclude='code-*/' --exclude='redcheck-*/' $OLD/ $ROOT/; echo "$(date '+%H:%M:%S') rsync exit $?" >> $C
step cache-r nice -n 10 /usr/bin/python3 -B -m brain.scene.run cache-r --root $ROOT || exit 4
step cache-identity /usr/bin/python3 -B tools/brain/diag/cache_identity.py $ROOT $OLD || exit 5
date "+%Y-%m-%d %H:%M:%S %z done" >> $C
