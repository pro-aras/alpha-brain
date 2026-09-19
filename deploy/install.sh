#!/usr/bin/env bash
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:53 +0400 — A5 (docs/G4-PREREG.md §2.10). Copies the
# unit files to ~/.config/systemd/user/ and reloads the user daemon. NEVER enables or starts anything —
# Claude does that, after the gates (PREREG §7). No sudo.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.config/systemd/user"
mkdir -p "${DEST}"

for f in creature.service creature-watch.service creature-watch.timer; do
    cp "${HERE}/${f}" "${DEST}/${f}"
    echo "installed ${DEST}/${f}"
done

systemctl --user daemon-reload
echo "daemon-reload done."
echo
echo "NOT enabled, NOT started (that is Claude's step, after the gates — docs/G4-PREREG.md §2.10, §7)."
echo "Next step, when the gates pass:"
echo "  systemctl --user enable --now creature.service"
echo "  systemctl --user enable --now creature-watch.timer"
