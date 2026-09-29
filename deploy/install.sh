#!/usr/bin/env bash
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:53 +0400 — A5 (docs/G4-PREREG.md §2.10). Copies the
# unit files to ~/.config/systemd/user/ and reloads the user daemon. NEVER enables or starts anything —
# Claude does that, after the gates (PREREG §7). No sudo.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.config/systemd/user"
mkdir -p "${DEST}"

# edit: Claude (Fable 5.1), 2026-09-21 20:57 +0400 — the templated seam-life units (creature-g5@, creature-g5-watch@) installed beside the 24 h life's.
# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:45 +0400 — BRAIN-IN-BODY §5: creature-brain@.service added to the fixed
# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:14 +0400 — THE LONG LIFE: creature-brain-series@.service/.timer appended to the copy list.
# copy list (this script's own behaviour for every existing unit here is unchanged — one more name appended, nothing removed).
for f in creature.service creature-watch.service creature-watch.timer creature-g5@.service creature-g5-watch@.service creature-g5-watch@.timer creature-brain@.service creature-brain-series@.service creature-brain-series@.timer; do
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
echo "A seam life <name> (root /data/dev/genome-lives/<name>): systemctl --user enable --now creature-g5@<name>.service creature-g5-watch@<name>.timer"
echo "A brain-in-body life <name> (root /data/dev/genome-lives/<name>): systemctl --user enable --now creature-brain@<name>.service"
