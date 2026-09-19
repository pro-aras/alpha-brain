# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 21:36 +0400 — A1: the tape (docs/G4-PREREG.md §2.1). One row per sense
# delivery; the payload is written BEFORE the row is appended; seq strictly increasing, persisted in tape/SEQ, written
# AFTER the row. Thread-safe under one lock. This is the ONLY place in the creature that reads the wall clock.
"""creature/tape.py — the tape: `run/tape/<YYYY-MM-DD>.jsonl` (PREREG §2.1).

Nothing that grades the organism is on the tape (the world-maker writes truth elsewhere, PREREG §2.1).
`Tape.publish` is called by sense threads through the body; `read_tape` is used by the mind's startup
replay and by `creature.replay`.
"""
from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, Optional


def now_iso() -> str:
    """UTC ISO-8601 with millisecond precision, e.g. 2026-09-19T21:36:03.123Z."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Tape:
    """One tape rooted at `root` (creates `root/tape/` and `root/tape/payload/`). Thread-safe: one lock
    guards payload write + row append + SEQ persistence together, so seq is strictly increasing and the
    queue a caller feeds from `publish`'s return value is in the same order as the tape itself."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.tape_dir = self.root / "tape"
        self.payload_dir = self.tape_dir / "payload"
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        self.seq_path = self.tape_dir / "SEQ"
        self._lock = threading.Lock()
        self._seq = self._read_seq()

    def _read_seq(self) -> int:
        if self.seq_path.exists():
            t = self.seq_path.read_text().strip()
            return int(t) if t else 0
        return 0

    def publish(self, sense: str, payload: bytes, meta: Dict[str, object], ext: str, at: Optional[str] = None) -> Dict[str, object]:
        """Append one tape row. `at`: a UTC ISO string (ms) or None → now (the ONLY wall-clock read in the
        creature). Returns the row dict (also what was appended, byte for byte via json.dumps)."""
        if at is None:
            at = now_iso()
        date = at[:10]
        with self._lock:
            seq = self._seq + 1
            payload_rel = f"payload/{seq:09d}.{ext}"
            payload_path = self.tape_dir / payload_rel
            payload_path.write_bytes(payload)          # payload durable BEFORE the row is appended (§2.1)
            sha = hashlib.sha256(payload).hexdigest()
            row = {"seq": seq, "at": at, "sense": sense, "sha": sha, "payload": payload_rel, "meta": meta}
            day_path = self.tape_dir / f"{date}.jsonl"
            with day_path.open("a") as f:
                f.write(json.dumps(row) + "\n")
            self.seq_path.write_text(str(seq))          # SEQ persisted AFTER the row is appended (§2.1)
            self._seq = seq
        return row


def read_tape(root: Path) -> Iterator[Dict[str, object]]:
    """Yield every row of every day file under `root/tape/`, in seq order (day files sort lexically by
    date, and within a file rows are appended strictly in seq order by `Tape.publish`'s lock)."""
    tape_dir = Path(root) / "tape"
    if not tape_dir.exists():
        return
    for day_file in sorted(tape_dir.glob("*.jsonl")):
        with day_file.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
