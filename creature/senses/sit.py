# edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: SIT, G-MOT-3 (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md,
# docs/organs/MOTOR-HANDS.md §4 G-MOT-3).
"""creature/senses/sit.py — SIT: publishes the voice's own exam score onto the tape as a row.

He already sits the exam (creature/exam.py's voice thread, EXAM's own cadence) and the file is already
written; nothing reads it. This sense thread reads the NEWEST exam file (digit-prefixed, sorted — never
`LAST.json`, the pointer: `exam.py`'s own scar, "the voice's pointer LAST.json sorted AFTER every stamped
file ('L' > '2')", #168's class) and, when it names a file this thread has not yet published, publishes
its score onto the tape as sense="sit" — the mind consumes it like any other row (creature/mind.py's
`_consume_sit`, which reuses the same reflex-episode mechanism `_consume_outcome` does).

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory and never imports Organism —
it only READS run/exam/*.json (a file `creature/exam.py`'s voice thread writes, a DIFFERENT thread; this
sense's own "last published" cursor lives in memory only, never on disk — a restart can re-publish the
CURRENT latest exam file once, which is harmless: `_consume_sit` just writes one more reflex episode with
the same score, and SIT's own period (`every` canvases, read from the genome, the same ledger-based
cadence `creature/exam.py`'s voice_loop uses) keeps re-checks sparse).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional


def _latest_exam_file(exam_dir: Path) -> Optional[Path]:
    """The newest digit-prefixed exam report — never `LAST.json` (`creature/exam.py`'s own scar)."""
    if not exam_dir.exists():
        return None
    files = sorted(p for p in exam_dir.glob("*.json") if p.name[:1].isdigit())
    return files[-1] if files else None


def _score_of(data: dict) -> Optional[float]:
    """The Q1 accuracy — the same field `creature/exam.py`'s own `run_and_journal` extracts
    (`ask_seen_words.Q1.acc`, #162's discipline: a `.get` that could return a dict or None is not a
    reading)."""
    ask = data.get("ask_seen_words") if isinstance(data, dict) else None
    q1 = (ask or {}).get("Q1") if isinstance(ask, dict) else None
    acc = (q1 or {}).get("acc") if isinstance(q1, dict) else None
    return float(acc) if isinstance(acc, (int, float)) else None


# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:13 +0400 — ALPHA4-PREREG.md §4(c) (THE
# READINESS JUDGE): "the last two SIT rows composite >= 0.95". The exam report already carries this
# number (`ask_seen_words.composite`, `genome/questions.py`'s own field — the mean of Q1..Q4's own
# accuracies, `tools/verdict_g4.py`'s and `genome/run_g0.py`/`run_g1.py`'s own established reader of it)
# but `_score_of` above only ever forwarded Q1 to the tape; the READINESS judge (creature/mind.py, "from
# TAPE FACTS ONLY") has no other road to this number. ADDITIVE: `sense()`'s existing "score"/"exam_file"
# payload/meta keys are untouched, byte for byte — this only adds a THIRD key, "composite", so no existing
# reader of a `sit` row (tests.creature.test_g5k_outcome's own dogfooding test, `creature/mind.py`'s
# `_consume_sit`'s `_record_reflex` call, which reads only `meta.get("score")`) sees any different value
# than before.
def _read_share_of(data: dict) -> Optional[float]:
    """edit: Claude (Fable 5.1), 2026-09-23 03:02 +0400 — ALPHA4 §4(b): the exam report's `read_share` (tools/self_exam.py --read-words),
    forwarded to the tape the same additive way `composite` is; None when the report carries no number."""
    v = data.get("read_share") if isinstance(data, dict) else None
    return float(v) if isinstance(v, (int, float)) else None


def _composite_of(data: dict) -> Optional[float]:
    """The mean of Q1..Q4's own accuracies — the SAME field `_score_of` reads Q1 out of
    (`ask_seen_words.composite`), extracted the same defensive way (#162's discipline)."""
    ask = data.get("ask_seen_words") if isinstance(data, dict) else None
    comp = (ask or {}).get("composite") if isinstance(ask, dict) else None
    return float(comp) if isinstance(comp, (int, float)) else None


def sense(publish: Callable, stop_event, root: Path, genome_path: Path, every_canvases: int, poll_period: float = 5.0) -> None:
    """Mirrors `creature/exam.py`'s own `voice_loop` cadence (state/ledger.json's "moments" divided by the
    genome's fixations-per-canvas) so SIT's own `every` value is a real, read parameter — never a fixed
    wall-clock poll pretending to honour it. `every_canvases <= 0` never checks (the same convention
    `_maybe_think` uses for THINK.every)."""
    root = Path(root)
    exam_dir = root / "exam"
    last_canvas = 0
    last_published_name: Optional[str] = None
    from genome.machinery import parse_genome
    genome = parse_genome(Path(genome_path).read_text())
    fixations = int(genome.gaze["fixations"]) if genome.gaze else 1

    while not stop_event.is_set():
        ledger_path = root / "state" / "ledger.json"
        if ledger_path.exists() and every_canvases > 0:
            try:
                moments = int(json.loads(ledger_path.read_text()).get("moments", 0))
            except (json.JSONDecodeError, OSError):
                moments = 0
            canvas_count = moments // max(1, fixations)
            if canvas_count - last_canvas >= every_canvases:
                last_canvas = canvas_count
                latest = _latest_exam_file(exam_dir)
                if latest is not None and latest.name != last_published_name:
                    try:
                        data = json.loads(latest.read_text())
                    except (json.JSONDecodeError, OSError):
                        data = None      # a torn/partial exam file mid-write (#47/#186) -- skip this poll, try again next one
                    if data is not None:
                        score = _score_of(data)
                        if score is not None:
                            composite = _composite_of(data)   # ALPHA4-PREREG §4(c): additive, alongside score (None on an exam report that carries no "composite" field)
                            payload = json.dumps({"score": score, "exam_file": latest.name, "composite": composite, "read_share": _read_share_of(data)}).encode("utf-8")
                            publish("sit", payload, {"moment": f"sit{latest.stem}", "source": "sit",
                                                      "exam_file": latest.name, "score": score, "composite": composite, "read_share": _read_share_of(data)}, "json")
                        last_published_name = latest.name    # advance the cursor AFTER the row is durable (#230), even if score was None (a malformed report is not re-tried forever)
        stop_event.wait(poll_period)
