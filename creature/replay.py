# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 23:12 +0400 — A6: replay (docs/G4-PREREG.md §2.9). The mind's
# decisions are a pure function of (genome, tape rows in seq order) -- I2, PREREG §2.3/B4. This tool proves it.
"""creature/replay.py — python3 -m creature.replay --genome G --tape run/tape/<date>.jsonl
[--against run/journal/<date>.jsonl] [--blind gaze] [--closed] [--timings] [--exam-every N] --out DIR

Rebuilds a fresh Mind from one day's tape file (in seq order) into a temporary work root (PREREG §2.11:
fresh roots for every test/gate), and writes DIR/journal.jsonl -- MIND rows only, which since ALPHA4
(docs/ALPHA4-PREREG.md §4/§6) is a WIDER set than G4-PREREG.md §2.4 originally drew: a row with NO
"event" key (every ordinary domain row: "moment"/"hash"/"sight_only", and now also "grade"/"hold"/"web"/
"readiness"), PLUS a row whose "event" value is a genuine MIND-level semantic event (ALPHA4-PREREG §4's
"stage", §6's "epoch") — a fact the mind itself decided and journaled via `Mind._write_journal`, fully
reproducible by a bare-Mind replay, unlike the five NON-MIND bookkeeping events (`NON_MIND_EVENTS`,
below) — four from creature/body.py's own `_journal_event` (wall-clock/thread-lifecycle facts:
`resumed_from_seq`, `sense_restart`'s own error, `snapshots`, …) plus "exam" from creature/exam.py's OWN,
separate `_journal_event` (the voice thread examines real pictures on disk, off its own wall-clock
cadence, never the tape) — neither writer is the Mind, and a bare Mind (what `run_replay` below drives)
cannot reproduce anything either one wrote. With --against, exit 0 iff every mind row matches field by
field, else exit 1 naming the first differing (seq, field).

edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:5x +0400 — found while proving "a tape carrying a
web/stage row replays identically" (my own brief's own test list) through THIS tool rather than only my
own ad hoc two-Mind comparison: the OLD blanket `"event" not in r` filter silently dropped the "stage"
event from `out_journal` — indistinguishable from "the stage event never fired" to any --against
comparison built from this function's own output (both sides equally blind). Not live-breaking today (no
genome on this tree has ever declared STAGE_READY/EVOLVE before this brief; gate_g4.py's own gate3 runs
G4-skeleton.genome/G4.genome, neither of which produces ANY mind-level event, so its "live" and "replay"
sides were equally empty of them either way) -- but it WOULD have silently defeated replay verification
the moment any life actually reached stage 4 or adopted an EVOLVE epoch, exactly when that proof matters
most. Fixed by naming the NON-mind events explicitly rather than testing for "event" at all -- first as
the four body-only ones (grep of creature/body.py alone), THEN widened to five after
tests/creature/test_exam.py's own `test_exam_event_row_excluded_from_mind_journal_reader` failed on the
full suite: creature/exam.py's voice thread journals its OWN "exam" event directly, a THIRD writer this
file's first pass missed — re-grepped `'"event":'` across creature/*.py and genome/*.py exhaustively
(`NON_MIND_EVENTS`'s own comment names the command) before calling this done a second time. Verified
additive: gate_g4.py's gate2/gate3/gate6 (G4-skeleton.genome), the full tests/creature/test_exam.py suite,
and this tree's own life-3a replay-diff (scratch/replay-life3a-{master,mine}/journal.jsonl, 2,576 rows, 0
divergence) all re-ran byte-identical after this change (no existing tape/genome ever produces a MIND-
level "event" row in the first place, so the excluded set is unchanged for every existing case).
"""
from __future__ import annotations

import json
import shutil
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

from .mind import Mind

# Every event name written by something OTHER than `Mind._write_journal` -- exhaustive by
# `grep -rn '"event":\s*"' creature/*.py genome/*.py` at the time of this edit: four from
# creature/body.py's `_journal_event` (the BODY's own writer) and one, "exam", from creature/exam.py's
# OWN separate `_journal_event` (the voice thread, examining real pictures off its own wall-clock cadence
# -- never the tape). A bare Mind (what `run_replay` below drives) cannot reproduce any of these five --
# there is no sense-thread to restart, no voice thread sitting an exam, no wall-clock
# "resumed_from_seq"/"backlog_replayed" a replay ever computes, and Mind.snapshot()/close() are called
# directly here without Body's own snapshot-count bookkeeping around them. Anything else carrying an
# "event" key is a MIND-level semantic event (`Mind._write_journal`'s own writes -- ALPHA4-PREREG §4's
# "stage", §6's "epoch") and belongs in the comparison.
NON_MIND_EVENTS = frozenset({"start", "sense_restart", "snapshot", "stop", "exam"})


def is_mind_row(r: Dict[str, object]) -> bool:
    return r.get("event") not in NON_MIND_EVENTS


def _read_jsonl(path: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def read_mind_journal(path: Path) -> List[Dict[str, object]]:
    """Mind rows -- every row except the five NON-mind bookkeeping events (`NON_MIND_EVENTS`): the body
    and the voice thread write those, the mind writes everything else, including its own semantic event
    rows since ALPHA4 (the module docstring explains the amendment to G4-PREREG.md §2.4's original,
    narrower law)."""
    return [r for r in _read_jsonl(path) if is_mind_row(r)]


def run_replay(genome_path: Path, tape_path: Path, out_dir: Path, blind: FrozenSet[str] = frozenset(), close: bool = False,
               timings: bool = False, exam_every: int = 0) -> Path:
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
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # edit: Claude (Fable 5.1), 2026-09-23 10:58 +0400 — A4-LADDER-PREREG §4's two instruments, both OUTSIDE the mind's road (the
    # journal is byte-identical with or without them — pinned by tests/creature/test_replay_instruments.py):
    # `timings`: per-row consume wall-ms to DIR/timings.jsonl (the COST rung's C2 bars and DROP's D4 read it);
    # `exam_every`: every N eye rows (N canvases) the replayed organism is SNAPSHOT to its work root and the
    # self-exam sits on that snapshot READ-ONLY (creature/exam.py:run_exam, check_tape 0) — the exam files land
    # under DIR/exam/ (ANSWER's A-controls and DROP's D1 read them). An exam never changes him: the identity
    # control is the same journal with exam_every 0.
    import time as _time
    tf = (out_dir / "timings.jsonl").open("w") if timings else None
    eye_rows = 0
    exam_dir = out_dir / "exam"
    for row in rows:
        t0 = _time.perf_counter() if tf is not None else None
        mind.consume(row)
        if tf is not None:
            tf.write(json.dumps({"seq": row.get("seq"), "sense": row.get("sense"), "source": (row.get("meta") or {}).get("source"),
                                 "ms": round((_time.perf_counter() - t0) * 1000.0, 3)}) + "\n")
        if exam_every > 0 and row.get("sense") == "eye":
            eye_rows += 1
            if eye_rows % exam_every == 0:
                mind.snapshot()
                from creature import exam as _exam_module
                _exam_module.run_exam(work_root, genome_path, held=10, check_tape=0)
    if tf is not None:
        tf.close()
    if close:
        mind.close()
    if exam_every > 0 and (work_root / "exam").exists():
        exam_dir.mkdir(parents=True, exist_ok=True)
        for f_ in sorted((work_root / "exam").glob("*.json")):
            if f_.name != "LAST.json":
                shutil.copy2(f_, exam_dir / f_.name)
    out_journal = out_dir / "journal.jsonl"
    mind_rows: List[Dict[str, object]] = []
    jdir = work_root / "journal"
    if jdir.exists():
        for f in sorted(jdir.glob("*.jsonl")):
            mind_rows.extend(r for r in _read_jsonl(f) if is_mind_row(r))
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

    exam_every = int(argv[argv.index("--exam-every") + 1]) if "--exam-every" in argv else 0
    out_journal = run_replay(genome_path, tape_path, out_dir, blind=blind, close="--closed" in argv,   # --closed: the tape is a closed life's whole record
                             timings="--timings" in argv, exam_every=exam_every)   # A4 ladder instruments (2026-09-23 10:58 +0400)

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
