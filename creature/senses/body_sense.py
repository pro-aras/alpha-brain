# edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: SENSE body, BODY-SENSES.md §4.1
# (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md).
"""creature/senses/body_sense.py — SENSE body: publishes STATUS's own numbers onto the tape.

BODY-SENSES.md §4.1: "it is a SENSE THREAD, so it publishes a row onto the tape ... and the mind reads it
as it reads any row — replay stays exact, because the reading enters through the tape's instants like
everything else. It writes no memory." "What it explicitly does NOT do: it delivers readings. Hunger,
tiredness and a set point are the MIND's, by his rule; this gene must not carry a threshold." This module
carries no threshold: it reads `root/STATUS.json` (the file `creature/body.py`'s own STATUS thread writes,
a DIFFERENT thread — the file is the public interface Body already exposes) and republishes the declared
fields' values verbatim.

A pure SENSE (G4-1's writer sweep): it only reads STATUS.json (no "state"/"journal"/"memory" in that
path) and never imports Organism.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence

# The genome names (BODY-SENSES.md §4.1's own field list) mapped to the STATUS.json key each one reads
# (creature/body.py:Body._build_status's own field names — "refused"/"restarts"/"mind_ms"/"rss" are the
# genome's shorter words for STATUS's "births_refused_budget"/"sense_restarts"/"mind_ms_median_1min"/"rss_mb").
STATUS_FIELD_MAP: Dict[str, str] = {
    "moments": "moments", "births": "births", "arrivals": "arrivals", "budget_left": "budget_left",
    "refused": "births_refused_budget", "restarts": "sense_restarts", "mind_ms": "mind_ms_median_1min", "rss": "rss_mb",
    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:00 +0400 — L-9/SELF (docs/briefs/LIFE-A-ANSWER-SELF.md
    # #3): "backlog" (#236's STATUS.mind_backlog_rows, already landed) and "refused_nmax" (STATUS already
    # carries births_refused_nmax) -- both new genome words this task's SELF gene reads off the body row.
    "backlog": "mind_backlog_rows", "refused_nmax": "births_refused_nmax",
}


def _read_status(status_path: Path) -> Optional[dict]:
    try:
        return json.loads(status_path.read_text())
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None    # STATUS.json not yet written (a fresh root) or torn mid-write (os.replace makes this rare, never fatal)


def sense(publish: Callable, stop_event, root: Path, fields: Sequence[str], period_s: float = 60.0) -> None:
    root = Path(root)
    status_path = root / "STATUS.json"
    while not stop_event.is_set():
        status = _read_status(status_path)
        if status is not None:
            reading = {f: status.get(STATUS_FIELD_MAP.get(f, f)) for f in fields}
            payload = json.dumps(reading).encode("utf-8")
            publish("body", payload, {"moment": f"body{status.get('heartbeat_at', '')}", "source": "body",
                                       "reading": reading}, "json")
        stop_event.wait(period_s)
