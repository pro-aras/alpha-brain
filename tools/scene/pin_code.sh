#!/bin/bash
# edit: Claude (Opus 5.5, S1a builder), 2026-09-28 12:25 +0400 — a PINNED copy of one commit's code for S1a's runs
# (/data/dev/brain-runs/scene/code-<sha>/), so no run reads a file a builder may still edit (#239). Usage:
#   tools/scene/pin_code.sh <commit>   (from the worktree)
set -eu
SHA=$(git rev-parse --short=7 "${1:-HEAD}")
DEST=/data/dev/brain-runs/scene/code-$SHA
[ -e "$DEST" ] && { echo "$DEST exists"; exit 0; }
mkdir -p "$DEST"
# edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:12 +0400 — the scene tests ride with the pin (S1c's FIRST GATE runs the truth
# fence's own test module from the pinned copy; earlier pins are untouched: a pin is written once)
git archive "$SHA" brain genome tools/scene tests/__init__.py tests/brain/__init__.py tests/brain/scene | tar -x -C "$DEST"
git rev-parse "$SHA" > "$DEST/CODE_SHA"
echo "$DEST"
