"""tools/toys/w2/inject.py — PREREG-W2 §3 item 1: the ON-tape injector (the bench's ON arm = the closed tape + the mentor's
own rows, the world's output simulated from the record as the law's §8 item 12 declares).

edit: Kimi K3 (kimi-code, builder lane kimi-w2), 2026-10-05 02:35 +0400 — new file, written after tests/tools/test_w2_bench.py
was red; law docs/organism/whole/PREREG-W2-MENTOR-WORLD.md §3 item 1.

build_on_tape(src, out, mentor_rows_by_moment): every tape day file copied row for row, with each moment's mentor rows
inserted IMMEDIATELY BEFORE its eye row (the moment's own delivery order: the parent's ear rows, then the mentor's, then
the eye — `creature/senses/scene.py:259-267`'s own shape, mentor rows in the canvas's declared order). Every mentor row
gets a real payload file (`payload/mentor-<seq:09d>-<k>.txt`, the word's bytes) and its sha (creature/tape.py:74-86's own
publish form). Seqs are renumbered 1..N in order (the insertion shifts them; diffj.tape_identity compares the two tapes
with seqs normalized). `at` of a mentor row = its moment's eye row's `at`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Sequence


def build_on_tape(src: Path, out: Path, mentor_rows_by_moment: Dict[str, Sequence[Dict[str, object]]]) -> Dict[str, int]:
    src, out = Path(src), Path(out)
    (out / "payload").mkdir(parents=True, exist_ok=True)
    counts = {"rows": 0, "mentor_rows": 0, "files": 0}
    for f in sorted(src.glob("*.jsonl")):
        written: List[str] = []
        seq = 0
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            meta = row.get("meta") or {}
            moment = meta.get("moment")
            if row.get("sense") == "eye" and moment in mentor_rows_by_moment:
                for k, mr in enumerate(mentor_rows_by_moment[moment]):
                    seq += 1
                    payload = bytes(mr["payload"])
                    rel = f"payload/mentor-{seq:09d}-{k}.txt"
                    (out / rel).write_bytes(payload)
                    mmeta = dict(mr["meta"])
                    new = {"seq": seq, "at": row.get("at"), "sense": "ear", "sha": hashlib.sha256(payload).hexdigest(),
                           "payload": rel, "meta": mmeta}
                    written.append(json.dumps(new) + "\n")
                    counts["mentor_rows"] += 1
            seq += 1
            row = dict(row)
            row["seq"] = seq
            written.append(json.dumps(row) + "\n")
            counts["rows"] += 1
        (out / f.name).write_text("".join(written), encoding="utf-8")
        counts["files"] += 1
    return counts
