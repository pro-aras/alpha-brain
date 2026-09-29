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


# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.2 (docs/G4-WAVE3-CLAUSES.md W3-0b):
# TAPE's declared value read. Every genome text seen so far writes the declared path exactly "run/tape"
# (a convention every G4 genome comment uses: the path as if from the repo root, "<repo>/run/tape"), and
# `--root` at the call site already points at that "run" directory -- so the declared path's own leading
# "run" segment names this Tape's `root`, not a subdirectory of it, and is stripped before joining.
def _resolve_tape_dir(root: Path, declared_path: Optional[str]) -> Path:
    """`declared_path` is `genome.declared['TAPE']['path']` (or None if TAPE is undeclared -> today's
    hardcoded default, unchanged). `TAPE run/tape` under root R still writes R/tape byte-identical to
    before; `TAPE run/tape2` writes R/tape2, nothing under R/tape (docs/briefs/W3-BUILDER-C.md C1.2's
    own toy)."""
    if not declared_path:
        return root / "tape"
    parts = Path(declared_path).parts
    if parts and parts[0] == "run":
        parts = parts[1:]
    return root / Path(*parts) if parts else root / "tape"


class Tape:
    """One tape rooted at `root` (creates `root/<tape dir>/` and its `payload/`, `<tape dir>` defaulting
    to `tape` and otherwise read from `declared_path` -- C1.2). Thread-safe: one lock guards payload write
    + row append + SEQ persistence together, so seq is strictly increasing and the queue a caller feeds
    from `publish`'s return value is in the same order as the tape itself."""

    def __init__(self, root: Path, declared_path: Optional[str] = None):
        self.root = Path(root)
        self.tape_dir = _resolve_tape_dir(self.root, declared_path)
        self.payload_dir = self.tape_dir / "payload"
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        self.seq_path = self.tape_dir / "SEQ"
        self._lock = threading.Lock()
        self._seq = self._read_seq()

    def _read_seq(self) -> int:
        # edit: Claude (Opus 5.5, the seat), 2026-09-29 23:31 +0400 — his 23:20 word: a power cut can empty or zero-fill SEQ mid-rewrite (it is
        # rewritten after every row), and an emptied SEQ restarted the seq at 1. The seq is now the LARGER of what SEQ says (read
        # tolerantly) and the last whole row on the tape; the body lifts it further to the mind's own last_seq (ensure_seq_at_least).
        from .repair import last_row_seq
        n = 0
        if self.seq_path.exists():
            t = self.seq_path.read_bytes().replace(b"\x00", b"").strip()
            n = int(t) if t.isdigit() else 0
        return max(n, last_row_seq(self.tape_dir))

    def ensure_seq_at_least(self, n: int) -> None:
        """The next row's seq is above `n` (the mind's last_seq at a resume: a row the mind saw may have been lost in a cut)."""
        with self._lock:
            self._seq = max(self._seq, int(n))

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


def read_tape(root: Path, declared_path: Optional[str] = None) -> Iterator[Dict[str, object]]:
    """Yield every row of every day file under `root/<tape dir>/` (C1.2: the SAME `_resolve_tape_dir` a
    `Tape` built with the same `declared_path` writes to -- Body.start()'s backlog replay must read the
    genome's own TAPE path or a non-default one would publish correctly and never be replayed), in seq
    order (day files sort lexically by date, and within a file rows are appended strictly in seq order by
    `Tape.publish`'s lock)."""
    tape_dir = _resolve_tape_dir(Path(root), declared_path)
    if not tape_dir.exists():
        return
    for day_file in sorted(tape_dir.glob("*.jsonl")):
        with day_file.open() as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        row = json.loads(line)
                    except ValueError as e:
                        raise TornTapeLine(_torn(day_file, lineno, line, e)) from e
                    yield row


# edit: Claude (Opus 5.5), 2026-09-26 18:54 +0400 — the 09-24 reboot (SOLUTIONS #240): the 22:00 shutdown left zero-filled lines in the
# day files the lives had open, and every restart died here on a BARE JSONDecodeError («Expecting value: line 1 column 1»)
# naming neither the file nor the line. A torn line is now NAMED — the file, the line, what it holds — and never skipped: a
# tape with a hole must not replay as a whole one. A closed record is recovered by cutting it at its first stop row.
class TornTapeLine(ValueError):
    """A tape line that does not parse: a write cut by a power-off (NUL-filled) or cut mid-row."""


def _torn(day_file: Path, lineno: int, line: str, err: Exception) -> str:
    nul = line.count("\x00")
    what = (f"{nul} NUL bytes in {len(line)} characters (a write cut by a power-off)" if nul
            else f"{len(line)} characters that do not parse as a row ({err}; a write cut mid-row)")
    return (f"{day_file}: line {lineno} is torn: {what}. A torn line is never skipped; recover a closed record by "
            f"cutting it at its first stop row (SOLUTIONS #240)")
