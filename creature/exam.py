# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 02:25 +0400 — A13: the self-exam duty (docs/G4-PREREG.md §11.4).
"""creature/exam.py — the voice's own exam duty: every EXAM.every canvases, run tools/self_exam.py's own
exam (by import, never copied) over the LATEST snapshot, write a journal EVENT row, and never touch the
live mind's objects (self_exam.py only ever loads a PRIVATE Organism from disk).

Not walked by gate G4-1 (creature/senses/*.py, creature/world_maker.py, creature/ask.py): this module is
neither a sense nor the voice's own core file, so its journal write (an EVENT row, exactly like the body's
own — PREREG §2.4, and explicitly asked for here by §11.4) is not in the sweep's scope.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Optional

from tools import self_exam

from .tape import now_iso


def run_exam(root: Path, genome_path: Path, held: int = 10, check_tape: int = 400) -> Dict[str, object]:
    """Runs tools/self_exam.py's own `main()` (its argument parsing reused via a scoped sys.argv swap,
    restored in a finally -- never copying its logic) and returns {"path": <the file it wrote>, "data":
    {...}}. Read-only on the creature: self_exam.py only ever opens run/state/organism.npz + ledger.json
    into a PRIVATE Organism, and writes only run/exam/<stamp>.json."""
    root = Path(root)
    old_argv = sys.argv
    try:
        sys.argv = ["self_exam.py", "--root", str(root), "--genome", str(genome_path), "--held", str(held), "--check-tape", str(check_tape), "--read-words", "20"]   # ALPHA4 §4(b): the reading share on every sitting (Claude (Fable 5.1), 2026-09-23 03:02 +0400)
        self_exam.main()
    finally:
        sys.argv = old_argv
    # edit: Claude (Fable 5.1), 2026-09-19 23:33 +0400 — the voice's pointer LAST.json sorted AFTER every stamped file ("L" > "2"), so the
    # event row read the pointer and journaled q1 null while the stamped file held Q1 .991 (#168's class: a sorted listing read wrong).
    exam_files = sorted(p for p in (root / "exam").glob("*.json") if p.name[0].isdigit())
    if not exam_files:
        raise RuntimeError("self_exam.main() did not write a run/exam/*.json file")
    latest = exam_files[-1]
    data = json.loads(latest.read_text())
    return {"path": str(latest), "data": data}


def _journal_event(root: Path, obj: Dict[str, object]) -> None:
    at = now_iso()
    row = {"seq": None, "at": at, **obj}
    date = at[:10]
    path = Path(root) / "journal" / f"{date}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, default=str) + "\n")


def run_and_journal(root: Path, genome_path: Path, held: int = 10, check_tape: int = 400) -> Dict[str, object]:
    """run_exam() + PREREG §11.4's journal EVENT row {"event": "exam", "path", "q1", "cells"}."""
    result = run_exam(root, genome_path, held=held, check_tape=check_tape)
    data = result["data"]
    ask_seen = data.get("ask_seen_words") or {}
    q1 = (ask_seen.get("Q1") or {}).get("acc") if isinstance(ask_seen, dict) else None   # the NUMBER (#162: a .get that returns a dict or None is not a reading)
    _journal_event(Path(root), {"event": "exam", "path": result["path"], "q1": q1, "cells": data.get("cells")})
    return result


def genome_for_sitting(root: Path, birth_genome_path: Path) -> Path:
    """edit: Claude (Fable 5.1), 2026-09-23 02:13 +0400 — the J × exam seam (docs/briefs/ALPHA4-J-REPORT.md, "not done" 1): the
    genome a SITTING runs under is the latest ADOPTED one (`GENOME.v<n>.genome` under the root, the highest n read
    numerically — creature/mind.py's own `_latest_evolved_genome`, the same resolver Mind.resume uses), and the birth
    genome when no adoption has happened. Resolved at EVERY sitting, never once at thread start, so an adoption between
    two sittings is honoured by the next one."""
    from creature.mind import _latest_evolved_genome
    n, path = _latest_evolved_genome(Path(root))
    return Path(path) if path is not None else Path(birth_genome_path)


def voice_loop(root: Path, genome_path: Path, stop_event, every_canvases: int, poll_period: float = 5.0) -> None:
    """The voice's own exam cadence: every `every_canvases` canvases, read from the latest snapshot's
    own "moments" (state/ledger.json) divided by the genome's fixations-per-canvas -- never a counter the
    mind hands over live (the voice never touches the mind's objects, PREREG §2.7's own law, unbroken
    here). A cursor (run/exam/LAST.json) survives a restart so a re-armed voice does not immediately
    re-run the exam it already ran just before a crash."""
    root = Path(root)
    last_path = root / "exam" / "LAST.json"
    last_path.parent.mkdir(parents=True, exist_ok=True)
    last_canvas = 0
    if last_path.exists():
        try:
            last_canvas = int(json.loads(last_path.read_text()).get("last_canvas", 0))
        except (json.JSONDecodeError, OSError):
            last_canvas = 0
    from genome.machinery import parse_genome
    genome = parse_genome(Path(genome_path).read_text())
    fixations = int(genome.gaze["fixations"]) if genome.gaze else 1
    while not stop_event.is_set():
        ledger_path = root / "state" / "ledger.json"
        if ledger_path.exists():
            try:
                moments = int(json.loads(ledger_path.read_text()).get("moments", 0))
            except (json.JSONDecodeError, OSError):
                moments = 0
            canvas_count = moments // max(1, fixations)
            if every_canvases > 0 and canvas_count - last_canvas >= every_canvases:
                last_canvas = canvas_count
                last_path.write_text(json.dumps({"last_canvas": last_canvas}))
                run_and_journal(root, genome_for_sitting(root, genome_path))   # the adopted genome, if any (the J × exam seam)
        stop_event.wait(poll_period)
