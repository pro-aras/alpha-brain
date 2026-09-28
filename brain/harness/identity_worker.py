#!/usr/bin/env python
"""identity_worker.py — ONE REPLAY, IN ITS OWN PROCESS (B1-PREREG.md §3.1).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:5x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

Invoked as `python -m brain.harness.identity_worker --args-json <path>` (a JSON file, never argv text, so a
tape path or a config dict with spaces/quotes can never be mangled by shell quoting — #182's class). Applies
§3.1's determinism settings when torch is importable (guarded: A0/A3/D's non-torch arms must not need
torch installed to run this worker), constructs the arm via `brain.protocol.make_arm`, optionally loads a
snapshot (resume), replays `tape_rows[:n_events]` through `HarnessContract`'s dispatch, optionally writes a
snapshot at a declared event count, and records `state_sha()` at each declared checkpoint. Writes ONE JSON
result file: `{"answers_sha256": ..., "answers": [...], "state_sha_at": {"500": ..., ...},
"final_state_sha": ..., "threads_torch": int|None}`.

`answers.jsonl` (per §8's own ledger — one line per ASK row, both training and test) is written beside the
result file so a caller can diff RAW per-item answers, not only their combined sha.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # the repo root, so `brain`/`genome` import

from brain.protocol import HarnessContract, canonical_json, make_arm  # noqa: E402


def _maybe_pin_torch(threads: int) -> Optional[int]:
    try:
        import torch
    except ImportError:
        return None
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(threads)
    if threads == 1:
        torch.use_deterministic_algorithms(True)
    return torch.get_num_threads()


def load_tape(path: Path) -> List[Dict[str, Any]]:
    """tape.jsonl's real shape — one JSON row per line (§2.6/§8), never a single JSON array."""
    rows = []
    with Path(path).open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def replay(arm, tape_rows: List[Dict[str, Any]], n_events: int, checkpoints: List[int],
           start_event: int = 0) -> Dict[str, Any]:
    """The HarnessContract dispatch loop (mirrors what `brain/harness/run.py` will do for a whole seed, but
    over a slice of the tape and with state_sha CHECKPOINTS instead of a final verdict). `pending` holds the
    last training ASK's Answer, keyed by its own seq, since FEEDBACK rows arrive later in tape order.

    `start_event` > 0 is the RESUME case (§3.1): the arm has already been `.load()`ed from a snapshot taken
    after `start_event` rows, so replay begins at `tape_rows[start_event]`, never from 0 (replaying from 0
    into an already-taught arm would re-teach everything twice). A FEEDBACK whose matching training ASK fell
    BEFORE `start_event` (so `pending` never saw it in THIS process) is skipped exactly as an unmatched
    FEEDBACK always is — the real B1 schedule keeps an ASK and its FEEDBACK adjacent, so a resume point
    between them is a test-construction choice to avoid, not a case this loop must handle specially.
    `events` counts from `start_event` (matching the tape's own seq numbering), so `checkpoints` are ABSOLUTE
    tape positions in every case, resumed or not."""
    answers: List[Dict[str, Any]] = []
    pending: Dict[int, Any] = {}
    window = tape_rows[start_event:n_events]
    ask_kind_by_seq: Dict[int, str] = {r["seq"]: r["payload"]["answer_kind"] for r in window if r["kind"] == "ASK"}
    in_test = False
    state_sha_at: Dict[int, str] = {}
    events = start_event
    for row in window:
        kind = row["kind"]
        if kind == "TEACH":
            HarnessContract.teach(arm, row)
        elif kind == "ARRIVAL":
            HarnessContract.arrival(arm, row)
        elif kind == "SLEEP":
            HarnessContract.sleep(arm, row)
        elif kind == "TEST_BEGIN":
            in_test = True
        elif kind == "TEST_END":
            in_test = False
        elif kind == "ASK":
            if in_test:
                ans = HarnessContract.test_ask(arm, row)
            else:
                ans = HarnessContract.training_ask(arm, row)
                pending[row["seq"]] = ans
            answers.append({"seq": row["seq"], **ans.to_dict()})
        elif kind == "FEEDBACK":
            ask_seq = row["payload"]["ask_seq"]
            ans = pending.pop(ask_seq, None)
            if ans is not None:
                HarnessContract.feedback(arm, row, ans, ask_kind_by_seq[ask_seq])
        events += 1
        if events in checkpoints:
            state_sha_at[events] = arm.state_sha()
    answers_blob = canonical_json(answers)
    import hashlib
    return {
        "answers": answers,
        "answers_sha256": hashlib.sha256(answers_blob.encode()).hexdigest(),
        "state_sha_at": {str(k): v for k, v in state_sha_at.items()},
        "final_state_sha": arm.state_sha(),
        "events_replayed": events,
    }


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--args-json", required=True)
    ns = p.parse_args(argv)
    args = json.loads(Path(ns.args_json).read_text())

    threads_torch = _maybe_pin_torch(int(args.get("threads", 1)))

    mod = importlib.import_module(args["arm_module"])
    cls = getattr(mod, args["arm_class"])
    config = dict(args["config"])
    arm = make_arm(cls, int(args["seed"]), config)

    if args.get("load_snapshot"):
        arm.load(args["load_snapshot"])

    tape_rows = load_tape(Path(args["tape_path"]))
    result = replay(arm, tape_rows, int(args["n_events"]), list(args.get("checkpoints", [])),
                     start_event=int(args.get("start_event", 0)))
    result["threads_torch"] = threads_torch

    if args.get("save_snapshot"):
        arm.snapshot(args["save_snapshot"])

    out_path = Path(args["out_path"])
    out_path.write_text(json.dumps(result, sort_keys=True, indent=2))
    answers_path = Path(args["answers_path"])
    with answers_path.open("w") as f:
        for a in result["answers"]:
            f.write(canonical_json(a) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
