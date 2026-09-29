# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:36 +0400 — his 23:20 word («make sure to clear any possible errors that might occur
# within these few days»): THE POWER-CUT REPAIR, run at an OPEN life's start (creature/body.py:Body.__init__), before the tape is opened.
"""creature/repair.py — a power cut leaves the files a life had open with a TORN TAIL: zero-filled bytes (the disk kept the new size, not
the data) or a row cut mid-write. Today the body then refuses to start (read_tape names the torn line) and the unit gives up after five
tries, so one cut ends a days-long life. This cuts a torn TAIL — and only a tail — off every append-only JSON-lines file of the life:

  the tape's day files · the journal's day files · state/*.jsonl (beliefs, predictions) · *.jsonl at the root (pages)

The cut bytes are KEPT, never deleted (<root>/repairs/<file>.<offset>.torn), and every repair is one row of <root>/repairs/REPAIRS.jsonl
{at, file, kind, offset, bytes, nul_bytes, lines, sha256, quarantine}; the body journals each as an event. The TAIL is the last MAX_TAIL
bytes (1 MiB: minutes of writes; a power cut loses the last ~30 s of unflushed pages, and the disk may flush them OUT OF ORDER, leaving a
zero-filled hole with good rows after it): the cut starts at the FIRST torn line inside it and takes everything after, good rows too, all
kept. A torn line older than the tail is not a power cut's damage and is left for read_tape to refuse by name (SOLUTIONS #240). Then the tape's
newest rows are checked against their payloads (the row carries the payload's sha256): at the first row whose payload is missing or does
not hash to it, the tape is cut there, that row and every later one kept in the quarantine with their payload files. A whole last row
that lost only its newline is completed, not cut. A closed life is never repaired (the caller checks STOPPED-AT first)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

QDIR = "repairs"
RECORD = "REPAIRS.jsonl"
MAX_TAIL = 1 << 20
CHECK_PAYLOAD_ROWS = 2000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parses(line: bytes) -> bool:
    s = line.strip()
    if not s:
        return True
    if b"\x00" in s:
        return False
    try:
        json.loads(s.decode("utf-8"))
        return True
    except Exception:
        return False


def _fsync(path: Path) -> None:
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _keep(root: Path, rel: str, offset: int, data: bytes) -> str:
    q = root / QDIR
    q.mkdir(parents=True, exist_ok=True)
    name = f"{rel.replace('/', '__')}.{offset}.torn"
    p = q / name
    p.write_bytes(data)
    _fsync(p)
    return name


def _record(root: Path, rec: Dict[str, object]) -> None:
    q = root / QDIR
    q.mkdir(parents=True, exist_ok=True)
    p = q / RECORD
    with p.open("a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def repair_tail(root: Path, path: Path, max_tail: int = MAX_TAIL) -> Optional[Dict[str, object]]:
    """Cut a torn TAIL off one append-only JSON-lines file (from the first torn line in its last `max_tail` bytes to its end, kept and
    recorded); complete a whole last row that lost only its newline. None when the tail is whole."""
    size = path.stat().st_size
    if size == 0:
        return None
    start = max(0, size - max_tail)
    with path.open("rb") as f:
        f.seek(start)
        tail = f.read()
    base = 0
    if start > 0:
        nl = tail.find(b"\n")
        if nl < 0:
            return None
        base = nl + 1
    parts = tail[base:].split(b"\n")
    frag, lines = parts[-1], parts[:-1]            # frag: after the last newline (b"" when the file ends with one)
    rel = str(path.relative_to(root))
    first = next((i for i, x in enumerate(lines) if not _parses(x)), None)
    if first is None:
        if not frag or not _parses(frag):
            if not frag:
                return None                        # the tail is whole
            first = len(lines)                     # only the fragment is torn
        else:
            with path.open("ab") as f:             # a whole row that lost only its newline
                f.write(b"\n")
                f.flush()
                os.fsync(f.fileno())
            rec = {"at": _now(), "file": rel, "kind": "newline_added", "offset": size, "bytes": 0, "nul_bytes": 0, "lines": 0,
                   "good_rows_cut": 0, "sha256": None, "quarantine": None}
            _record(root, rec)
            return rec
    cut_off = start + base + sum(len(x) + 1 for x in lines[:first])
    with path.open("rb") as f:
        f.seek(cut_off)
        data = f.read()
    good_after = sum(1 for x in lines[first:] if x.strip() and _parses(x)) + (1 if frag.strip() and _parses(frag) else 0)
    q = _keep(root, rel, cut_off, data)
    with path.open("r+b") as f:
        f.truncate(cut_off)
        f.flush()
        os.fsync(f.fileno())
    rec = {"at": _now(), "file": rel, "kind": "tail_cut", "offset": cut_off, "bytes": len(data), "nul_bytes": data.count(b"\x00"),
           "lines": data.count(b"\n") + (0 if data.endswith(b"\n") else 1), "good_rows_cut": good_after,
           "sha256": hashlib.sha256(data).hexdigest(), "quarantine": q}
    _record(root, rec)
    return rec


def _rows_with_offsets(path: Path) -> List[Tuple[int, int, Dict[str, object]]]:
    out, off = [], 0
    with path.open("rb") as f:
        for raw in f:
            n = len(raw)
            s = raw.strip()
            if s:
                try:
                    out.append((off, n, json.loads(s.decode("utf-8"))))
                except Exception:
                    return out                    # a middle torn line: read_tape refuses it by name; nothing more here
            off += n
    return out


def verify_payloads(root: Path, tape_dir: Path, check_rows: int = CHECK_PAYLOAD_ROWS) -> Optional[Dict[str, object]]:
    """The last `check_rows` rows (the newest two day files): cut the tape at the first row whose payload is missing or mis-hashed."""
    if check_rows <= 0:
        return None
    days = sorted(tape_dir.glob("*.jsonl"))[-2:]
    cand: List[Tuple[Path, int, int, Dict[str, object]]] = []
    for d in days:
        cand.extend((d, off, n, r) for off, n, r in _rows_with_offsets(d))
    cand = cand[-check_rows:]
    for i, (day, off, _n, row) in enumerate(cand):
        pp = tape_dir / str(row.get("payload", ""))
        why = None
        if not row.get("payload") or not pp.exists():
            why = "missing"
        else:
            if hashlib.sha256(pp.read_bytes()).hexdigest() != row.get("sha"):
                why = "hash"
        if why is None:
            continue
        bad = cand[i:]
        # cut each affected day file at its first bad row; keep the cut rows and their payload files
        rels, first_bad = [], int(row.get("seq") or 0)
        by_day: Dict[Path, int] = {}
        for d, o, _m, _r in bad:
            by_day.setdefault(d, o)
        for d, o in by_day.items():
            with d.open("rb") as f:
                f.seek(o)
                data = f.read()
            rel = str(d.relative_to(root))
            _keep(root, rel, o, data)
            with d.open("r+b") as f:
                f.truncate(o)
                f.flush()
                os.fsync(f.fileno())
            rels.append(rel)
        qp = root / QDIR / "payload"
        qp.mkdir(parents=True, exist_ok=True)
        moved = 0
        for _d, _o, _m, r in bad:
            src = tape_dir / str(r.get("payload", ""))
            if r.get("payload") and src.exists():
                shutil.move(str(src), str(qp / src.name))
                moved += 1
        rec = {"at": _now(), "file": ",".join(rels), "kind": "payload_cut", "first_bad_seq": first_bad, "why": why, "rows": len(bad),
               "payloads_kept": moved, "offset": None, "bytes": None, "nul_bytes": None, "lines": len(bad), "sha256": None,
               "quarantine": f"{QDIR}/payload"}
        _record(root, rec)
        return rec
    return None


def last_row_seq(tape_dir: Path) -> int:
    """The seq of the last whole row of the newest day file holding one (0 if none)."""
    for d in sorted(tape_dir.glob("*.jsonl"), reverse=True):
        size = d.stat().st_size
        if size == 0:
            continue
        with d.open("rb") as f:
            f.seek(max(0, size - (1 << 20)))
            tail = f.read()
        for line in reversed(tail.split(b"\n")):
            s = line.strip()
            if not s:
                continue
            try:
                return int(json.loads(s.decode("utf-8"))["seq"])
            except Exception:
                continue
    return 0


def repair_life(root: Path, tape_declared_path: Optional[str], check_payload_rows: int = CHECK_PAYLOAD_ROWS) -> List[Dict[str, object]]:
    """Every append-only JSON-lines file of an OPEN life: its torn tail cut (kept, recorded); then the tape's newest payloads checked."""
    from .tape import _resolve_tape_dir
    root = Path(root)
    tape_dir = _resolve_tape_dir(root, tape_declared_path)
    files: List[Path] = []
    if tape_dir.exists():
        files += sorted(tape_dir.glob("*.jsonl"))
    for sub in ("journal", "state"):
        d = root / sub
        if d.exists():
            files += sorted(d.glob("*.jsonl"))
    files += sorted(p for p in root.glob("*.jsonl"))
    out: List[Dict[str, object]] = []
    for p in files:
        rec = repair_tail(root, p)
        if rec is not None:
            out.append(rec)
    if tape_dir.exists():
        rec = verify_payloads(root, tape_dir, check_payload_rows)
        if rec is not None:
            out.append(rec)
    return out
