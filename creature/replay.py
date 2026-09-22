# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:12 +0400 — A6: replay (docs/G4-PREREG.md §2.9). The mind's
# decisions are a pure function of (genome, tape rows in seq order) -- I2, PREREG §2.3/B4. This tool proves it.
"""creature/replay.py — python3 -m creature.replay --genome G --tape run/tape/<date>.jsonl
[--against run/journal/<date>.jsonl] [--blind gaze] [--closed] --out DIR

Rebuilds a fresh Mind from one day's tape file (in seq order) into a temporary work root (PREREG §2.11:
fresh roots for every test/gate), and writes DIR/journal.jsonl -- MIND rows only (rows without an
"event" key; the body's own event rows carry wall-clock facts the mind never produced, PREREG §2.4).
With --against, exit 0 iff every mind row matches field by field, else exit 1 naming the first
differing (seq, field).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

from .mind import Mind


def _read_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def read_mind_journal(path: Path) -> List[Dict[str, object]]:
    """Mind rows only -- a row without an "event" key (PREREG §2.4: the body writes event rows, the
    mind writes rows carrying "moment"/"hash" or "sight_only")."""
    return [r for r in _read_jsonl(path) if "event" not in r]


def run_replay(genome_path: Path, tape_path: Path, out_dir: Path, blind: FrozenSet[str] = frozenset(), close: bool = False) -> Path:
    """Feeds `tape_path`'s rows (one day file, sorted by seq -- defensive, they are already in order) to
    a fresh Mind in a temporary root whose tape/payload is a symlink to the source tape's own payload
    directory (never copied: replay never writes to the source tape). Returns DIR/journal.jsonl's path.

    `close` (edit: Claude (Fable 5.1), 2026-09-22 22:27 +0400 — plan L-1 × L-5, builder E's tail note): a tape that is a CLOSED life's
    whole record ends the replayed mind the way the body ended the live one — `Mind.close()` applies the think still in flight at the
    last eye row's seq (creature/body.py:stop) — or the closed journal carries one think row the replay cannot. A MID-tape cut keeps
    the default False: the live mind lands that think at a later boundary, outside the cut, and a close here would invent a row."""
    tape_path = Path(tape_path)
    tape_root = tape_path.parent
    work_root = Path(tempfile.mkdtemp(prefix="creature-replay-"))
    # edit: Claude (Fable 5.1), 2026-09-21 12:01 +0400 — W3-0b seam (Builder C's finding 5): the work root's tape dir follows the genome's own
    # TAPE path (creature/tape.py:_resolve_tape_dir; byte-identical for the default `run/tape`), so a Mind reading payloads under
    # that path finds the symlinked payload dir.
    from genome.machinery import parse_genome as _parse_genome
    from creature.tape import _resolve_tape_dir as _resolve
    work_tape = _resolve(work_root, _parse_genome(Path(genome_path).read_text()).declared.get("TAPE", {}).get("path"))
    work_tape.mkdir(parents=True, exist_ok=True)
    payload_src = tape_root / "payload"
    if payload_src.exists():
        os.symlink(payload_src.resolve(), work_tape / "payload")

    mind = Mind(genome_path, work_root, blind=blind)
    rows = sorted(_read_jsonl(tape_path), key=lambda r: r["seq"])
    for row in rows:
        mind.consume(row)
    if close:
        mind.close()

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_journal = out_dir / "journal.jsonl"
    mind_rows: List[Dict[str, object]] = []
    jdir = work_root / "journal"
    if jdir.exists():
        for f in sorted(jdir.glob("*.jsonl")):
            mind_rows.extend(r for r in _read_jsonl(f) if "event" not in r)
    with out_journal.open("w") as f:
        for r in mind_rows:
            f.write(json.dumps(r) + "\n")
    return out_journal


def compare(got: Iterable[Dict[str, object]], want: Iterable[Dict[str, object]], ignore: Iterable[str] = ()) -> Optional[Tuple[int, str]]:
    """None iff every row matches field by field (as JSON objects, never as raw text/whitespace); else
    the first (seq, field) that differs, seqs walked in order.

    A9/A10 (PREREG §11.1 step 4): SLEEP journals a SECOND mind row sharing its triggering canvas's own
    seq, so one seq can now carry more than one row — grouped into ORDERED lists (append order, which is
    also seq-then-within-seq order for both a live run and a replay of the same tape) and compared
    pairwise; a row-count mismatch at a seq is itself reported as a divergence at that seq."""
    by_seq_got: Dict[int, List[Dict[str, object]]] = {}
    by_seq_want: Dict[int, List[Dict[str, object]]] = {}
    for r in got:
        by_seq_got.setdefault(int(r["seq"]), []).append(r)
    for r in want:
        by_seq_want.setdefault(int(r["seq"]), []).append(r)
    for seq in sorted(set(by_seq_got) | set(by_seq_want)):
        gs, ws = by_seq_got.get(seq), by_seq_want.get(seq)
        if gs is None:
            return seq, "<missing from replay>"
        if ws is None:
            return seq, "<missing from --against>"
        if len(gs) != len(ws):
            return seq, f"<row count: replay {len(gs)} vs --against {len(ws)}>"
        for g, w in zip(gs, ws):
            # edit: Claude (Fable 5.1), 2026-09-22 18:29 +0400 — `ignore`: fields DECLARED volatile by the caller (the reader masks `hash` only when its commit is not the life's — PREREG §19 / plan L-1); default () = every field, as always.
            skip = set(ignore)
            for key in sorted((set(g) | set(w)) - skip):
                if g.get(key) != w.get(key):
                    return seq, key
    return None


def main(argv: List[str]) -> int:
    genome_path = Path(argv[argv.index("--genome") + 1])
    tape_path = Path(argv[argv.index("--tape") + 1])
    out_dir = Path(argv[argv.index("--out") + 1])
    blind: FrozenSet[str] = frozenset([argv[argv.index("--blind") + 1]]) if "--blind" in argv else frozenset()

    out_journal = run_replay(genome_path, tape_path, out_dir, blind=blind, close="--closed" in argv)   # --closed: the tape is a closed life's whole record

    if "--against" in argv:
        against_path = Path(argv[argv.index("--against") + 1])
        got = read_mind_journal(out_journal)
        want = read_mind_journal(against_path)
        diff = compare(got, want)
        if diff is None:
            print(f"REPLAY identical: {len(got)} mind rows")
            return 0
        seq, field = diff
        print(f"DIVERGED at seq {seq}: {field}")
        return 1

    print(f"replay wrote {out_journal}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
