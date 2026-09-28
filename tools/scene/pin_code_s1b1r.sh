#!/bin/bash
# edit: Claude (Opus 5.5, S1b-1R builder), 2026-09-28 16:00 +0400 — PREREG-S1B1R AMENDMENT 1 §4 (i): a PINNED copy of one commit's code for
# S1b-1R's runs, under this slice's OWN root (/data/dev/brain-runs/scene-s1b1r/code-<sha>/) — never S1a's or S1b-1's —
# so no run reads a file a builder may still edit (#239). Usage (from the worktree):  tools/scene/pin_code_s1b1r.sh <commit>
set -eu
SHA=$(git rev-parse --short=7 "${1:-HEAD}")
DEST=/data/dev/brain-runs/scene-s1b1r/code-$SHA
[ -e "$DEST" ] && { echo "$DEST exists"; exit 0; }
mkdir -p "$DEST"
git archive "$SHA" brain genome tools/scene | tar -x -C "$DEST"
git rev-parse "$SHA" > "$DEST/CODE_SHA"
echo "$DEST"
