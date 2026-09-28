#!/bin/bash
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:25 +0400 — a PINNED copy of one commit's code for S1a's runs
# (/data/dev/brain-runs/scene/code-<sha>/), so no run reads a file a builder may still edit (#239). Usage:
#   tools/scene/pin_code.sh <commit>   (from the worktree)
set -eu
SHA=$(git rev-parse --short=7 "${1:-HEAD}")
DEST=/data/dev/brain-runs/scene/code-$SHA
[ -e "$DEST" ] && { echo "$DEST exists"; exit 0; }
mkdir -p "$DEST"
git archive "$SHA" brain genome tools/scene | tar -x -C "$DEST"
git rev-parse "$SHA" > "$DEST/CODE_SHA"
echo "$DEST"
