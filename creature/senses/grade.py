# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 00:58 +0400 — ALPHA4-PREREG.md §4 (d)/(e): SENSE
# grade (the seat's grades) and the HOLD file, both published onto the tape so mentorship and a hold enter
# through the tape like everything else on this box — the mind never reaches outside it, and a replay
# decides identically (the brief's own words: "mentorship enters through the tape, so the judge replays").
"""creature/senses/grade.py — SENSE grade: watches `$ROOT/ask/graded/*.json` (written by the SEAT, never
by any part of this creature) and publishes each one as a `grade` tape row `{"id","right","novel"}`;
separately watches a HOLD file's existence (`$ROOT/world/HOLD` by the PREREG's own path) and publishes a
`hold` tape row `{"active": bool}` on every CHANGE — including the very first observation, so a HOLD
already present at birth is not silently missed (a row published only on change needs its very first
reading to count as a change too, or "no row yet" reads as "never held", which is false the moment a HOLD
file predates this sense's first scan).

A pure SENSE (G4-1's writer sweep): it only reads `ask/graded/*.json` and a hold file's existence; it never
touches state/journal/memory and never imports Organism/machinery. Its own cursor (`root/grade/SEEN.json`)
is written AFTER each row is durable on the tape (#230's cursor law, `creature/senses/folder.py`'s own
pattern) — a crash between publish and mark-seen re-publishes the same grade, a safe, idempotent duplicate
the mind just re-lives (harmless: `right`/`novel` are read the same way from either copy).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Optional


def _load_seen(seen_path: Path) -> set:
    if not seen_path.exists():
        return set()
    try:
        return set(json.loads(seen_path.read_text()))
    except (json.JSONDecodeError, OSError):
        return set()      # a torn/partial SEEN.json from a crash mid-write is "nothing seen yet", never fatal


def _candidate_grades(graded_dir: Path, seen: set) -> List[Path]:
    """Every `<id>.json` under `graded_dir` not yet published, sorted BYTEWISE by filename — deterministic,
    never mtime (C2's pacing discipline, `folder.py`'s own convention, applied here too)."""
    if not graded_dir.exists():
        return []
    return [p for p in sorted(graded_dir.glob("*.json")) if p.stem not in seen]


def sense(publish: Callable, stop_event, root: Path, graded_dir: Optional[Path] = None,
          hold_file: Optional[Path] = None, period: float = 2.0) -> None:
    """`graded_dir`: defaults to `root/ask/graded` (the PREREG's own path) when not overridden (tests pass
    a scratch dir directly). `hold_file`: None (the default — a genome that declares SENSE grade without
    DOOR web, or DOOR web's own `hold_file` clause resolved to nothing) means this sense never watches a
    hold at all and never publishes a `hold` row — creature/body.py:main threads DOOR_WEB's own declared
    `hold_file` in when both genes are present. `period`: this gene's own genome line (`SENSE grade from
    ask/graded`) carries no rate — 2.0 s is a code-side default (raised in the builder report, not a
    gene-derived number), matching the general granularity of every other polling sense on this box.
    """
    root = Path(root)
    graded_dir = Path(graded_dir) if graded_dir is not None else (root / "ask" / "graded")
    seen_path = root / "grade" / "SEEN.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    seen = _load_seen(seen_path)
    # None == "not yet observed" -- deliberately distinct from True/False so the FIRST scan always counts
    # as a change (advisor's fix: a HOLD already present at birth must not silently read as "not held" for
    # want of a prior observation to differ from -- None != False and None != True are both True in Python).
    prev_hold: Optional[bool] = None
    hold_seq = 0

    while not stop_event.is_set():
        published_any = False
        for p in _candidate_grades(graded_dir, seen):
            try:
                data = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue    # a torn/partial write mid-crash on the seat's side -- skip this scan, retry next one, never fatal
            gid = str(data.get("id", p.stem))
            right = bool(data.get("right"))
            novel = bool(data.get("novel"))
            payload = json.dumps({"id": gid, "right": right, "novel": novel}).encode("utf-8")
            publish("grade", payload, {"moment": f"grade{p.stem}", "source": "grade",
                                        "id": gid, "right": right, "novel": novel}, "json")
            seen.add(p.stem)
            seen_path.write_text(json.dumps(sorted(seen)))   # AFTER the row is durable -- the cursor law (#230)
            published_any = True

        if hold_file is not None:
            cur_hold = Path(hold_file).exists()
            if cur_hold != prev_hold:
                publish("hold", json.dumps({"active": cur_hold}).encode("utf-8"),
                        {"moment": f"hold{hold_seq:06d}", "source": "grade", "active": cur_hold}, "json")
                hold_seq += 1
                prev_hold = cur_hold
                published_any = True

        if not published_any:
            stop_event.wait(period)
