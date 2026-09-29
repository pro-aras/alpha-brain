#!/bin/bash
# edit: Claude (Fable 5.1, the seat), 2026-09-29 — PREREG-BRAIN-DRIVES §8 (14): the cache pin's price, and the never-used world's first draw.
# The form of /data/dev/brain-runs/day0929/wordroad/redraw.sh. Run ONLY with every life closed.
set -u
CODE=/data/dev/genome-wt-drive; ROOT=/data/dev/brain-runs/scene-organ-drive; OLD=/data/dev/brain-runs/scene-organ-hear
O=/data/dev/brain-runs/day0929/drive; L=$O/logs
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/day0929/tmp PYTHONPATH=$CODE
cd $CODE || exit 2
C=$O/redraw-clock.txt
n=$(systemctl --user list-units 'creature*' --state=active --no-legend --no-pager | grep -c .)
[ "$n" = "0" ] || { echo "STOP: $n creature unit(s) active" | tee -a $C; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "STOP: the drive tree is not clean" | tee -a $C; exit 3; }
date "+%Y-%m-%d %H:%M:%S %z start at $(git rev-parse --short HEAD); load $(cut -d' ' -f1-3 /proc/loadavg)" > $C
step() { name="$1"; shift; "$@" > $L/redraw-$name.log 2>&1; rc=$?; echo "$(date '+%H:%M:%S') $name exit $rc" >> $C; return $rc; }
[ -e $ROOT ] && { echo "STOP: $ROOT exists (a fresh root only)" | tee -a $C; exit 3; }
mkdir -p $ROOT && rsync -a --exclude='cache/' --exclude='code-*/' --exclude='redcheck-*/' $OLD/ $ROOT/; echo "$(date '+%H:%M:%S') rsync exit $?" >> $C
step cache-r nice -n 5 /usr/bin/python3 -B -m brain.scene.run cache-r --root $ROOT || exit 4
step cache-identity /usr/bin/python3 -B tools/brain/diag/cache_identity.py $ROOT $OLD || exit 5
step cache-new-world nice -n 5 /usr/bin/python3 -B -m brain.scene.run cache --split train --world-seed 20261104 --root $ROOT || exit 6
date "+%Y-%m-%d %H:%M:%S %z done; load $(cut -d' ' -f1-3 /proc/loadavg)" >> $C
