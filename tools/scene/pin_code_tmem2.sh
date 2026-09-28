#!/bin/bash
# edit: Claude (Opus 5.5, T-MEM-2 builder), 2026-09-28 17:40 +0400 — PREREG-TMEM2 §8: a PINNED copy of one commit's code for T-MEM-2's runs,
# under this slice's OWN root (/data/dev/brain-runs/scene-tmem2/code-<sha>/) — never S1b-1R's (read, never written) — so no
# run reads a file a builder may still edit (#239). Usage (from the worktree):  tools/scene/pin_code_tmem2.sh <commit>
set -eu
SHA=$(git rev-parse --short=7 "${1:-HEAD}")
DEST=/data/dev/brain-runs/scene-tmem2/code-$SHA
[ -e "$DEST" ] && { echo "$DEST exists"; exit 0; }
mkdir -p "$DEST"
git archive "$SHA" brain genome tools/scene | tar -x -C "$DEST"
git rev-parse "$SHA" > "$DEST/CODE_SHA"
echo "$DEST"
