# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:48 +0400 — A5: the STATUS watcher (docs/G4-PREREG.md §2.5, §2.10).
"""tools/creature_watch.py — liveness is motion (#179, #230): reads root/STATUS.json (written by the
body), compares against the last DIFFERENT reading it kept in root/watch/last.json, and pages
(root/pages.jsonl + root/PAGE.json) when moments/tape_rows have not moved in >= 60 min.

`check()` is a pure function of two STATUS-shaped dicts so the "frozen vs moving" test never has to
sleep a real hour — it compares the readings' OWN heartbeat_at stamps, not wall clock read at watch time
(a watcher that used its own poll time would be blind to a body that is itself behind).

STATUS.json is the body's ONLY writer (PREREG §2.5); this tool never touches it. The watcher's verdict
lives in its own root/PAGE.json (a would-be "STATUS.page" mirror, one writer per file).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

STALE_SECONDS = 60 * 60


def _parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def check(status: Dict[str, object], last: Optional[Dict[str, object]], stale_seconds: float = STALE_SECONDS) -> Tuple[bool, Dict[str, object], Optional[str]]:
    """(should_page, new_last, why). `last` is the previously-kept reading ({"heartbeat_at", "moments",
    "tape_rows"}) or None on the first run. Moved (moments or tape_rows differ) -> new_last = current
    reading, never pages. Unmoved -> pages iff status.heartbeat_at - last.heartbeat_at >= stale_seconds,
    and `last` is kept AS IS (so it keeps naming the last moment real motion was seen)."""
    current = {"heartbeat_at": status["heartbeat_at"], "moments": status["moments"], "tape_rows": status["tape_rows"]}
    if last is None:
        return False, current, None
    moved = (current["moments"] != last["moments"]) or (current["tape_rows"] != last["tape_rows"])
    if moved:
        return False, current, None
    elapsed = (_parse_iso(current["heartbeat_at"]) - _parse_iso(last["heartbeat_at"])).total_seconds()
    if elapsed >= stale_seconds:
        why = (f"frozen: moments={current['moments']} tape_rows={current['tape_rows']} unchanged since "
               f"{last['heartbeat_at']} ({elapsed / 60.0:.1f} min >= {stale_seconds / 60.0:.0f} min)")
        return True, last, why
    return False, last, None


def run_once(root: Path, stale_seconds: float = STALE_SECONDS) -> bool:
    """Reads STATUS.json, updates watch/last.json, and writes PAGE.json + appends to pages.jsonl when
    stale. Returns True iff it paged. Missing STATUS.json (the body has not started yet) is a no-op."""
    status_path = root / "STATUS.json"
    if not status_path.exists():
        return False
    status = json.loads(status_path.read_text())
    watch_dir = root / "watch"
    watch_dir.mkdir(parents=True, exist_ok=True)
    last_path = watch_dir / "last.json"
    last = json.loads(last_path.read_text()) if last_path.exists() else None

    paged, new_last, why = check(status, last, stale_seconds=stale_seconds)
    last_path.write_text(json.dumps(new_last))

    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    page_path = root / "PAGE.json"
    if paged:
        page_path.write_text(json.dumps({"at": now, "why": why}))
        with (root / "pages.jsonl").open("a") as f:
            f.write(json.dumps({"at": now, "why": why, "status": status}) + "\n")
    else:
        page_path.write_text(json.dumps(None))
    return paged


def main(argv) -> int:
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path(".")
    paged = run_once(root)
    print(f"creature_watch: {'PAGED' if paged else 'ok'} ({root})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
