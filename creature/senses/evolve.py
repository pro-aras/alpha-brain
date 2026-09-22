# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE).
"""creature/senses/evolve.py — the EVOLVE door's sense thread.

Mirrors `creature/senses/game.py`'s own split exactly: `tools/evolve.py` (started as a SEPARATE SUBPROCESS
by `creature/body.py:main`, the same way `game.start_worker` launches the BabyAI worker) is where the shadow
organism lives and where mutant genomes are drawn, replayed and graded — it writes
`$ROOT/evolve/PROPOSAL-<n>.json` files, never the tape directly (a subprocess cannot safely share the
Body's own Tape lock/sequence counter). THIS module is the in-process thread a `creature.body.SenseThread`
runs: it watches `$ROOT/evolve/` for proposal files the worker has not yet republished, and publishes each
one as a single "proposal" tape row — payload = the proposal JSON bytes (durable, for a human/tool to
inspect); meta = the SAME dict (Mind._consume_proposal reads `meta`, never re-decodes the payload bytes —
the same convention `_consume_outcome`/`_consume_sit` already use).

The cursor (`$ROOT/evolve/CURSOR_SENSE`) is written to DISK, not kept in memory (unlike
`creature/senses/sit.py`'s own in-memory cursor, whose docstring explains why a re-publish there is
harmless — re-publishing an ALREADY-ADOPTED proposal here is NOT harmless: `Mind._consume_proposal`
unconditionally overwrites the pending proposal on a PASS row, so a duplicate row would let the SAME
mutation be adopted a SECOND time as a new epoch). Written AFTER the row is durable on the tape (#230).

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory, and never imports Organism or
`genome.machinery` — it only reads plain JSON files under `$ROOT/evolve/` (the worker's own output) and
calls `publish()`.
"""
from __future__ import annotations

import json
import re
import signal
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists.
EVOLVE_DOOR_GATED = True

WORKER_SCRIPT = str(Path(__file__).resolve().parents[2] / "tools" / "evolve.py")

_PROPOSAL_RE = re.compile(r"PROPOSAL-(\d+)\.json")


def start_worker(root: Path, genome_path: Path, stop_file: Path, python: str = sys.executable,
                  poll_period: float = 30.0) -> "subprocess.Popen[bytes]":
    """Mirrors `creature/senses/game.py:start_worker` exactly: launches `tools/evolve.py` as a SUBPROCESS
    (the shadow-organism/twin-replay machinery imports Organism/machinery directly, which a SENSE module
    must never do — `tools/evolve.py` is not under `creature/senses/`, so `tools/gate_g4.py`'s writer sweep
    does not apply to it, exactly like `tools/game_worker_babyai.py`). Unlike the game worker, this one
    needs no venv (numpy/PIL are already the running process's own dependencies), so `python` defaults to
    THIS process's own interpreter."""
    argv = [python, WORKER_SCRIPT, "--root", str(root), "--genome", str(genome_path),
            "--stop-file", str(stop_file), "--poll-period", str(poll_period)]
    return subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_worker(proc: "subprocess.Popen[bytes]", stop_file: Optional[Path] = None, timeout: float = 30.0) -> None:
    """Mirrors `creature/senses/game.py:stop_worker` exactly: kill by the PID this module itself holds
    (`proc`) — never `pkill -f` a pattern the caller's own command line might carry (#193/#197). `timeout`
    is longer than the game worker's own default: an in-flight judging round (a full organism replay over
    a 2 h slice) should finish cleanly rather than be cut mid-write."""
    if proc.poll() is not None:
        return
    if stop_file is not None:
        try:
            stop_file.parent.mkdir(parents=True, exist_ok=True)
            stop_file.write_text("stop")
        except OSError:
            pass
    try:
        proc.wait(timeout=timeout)
        return
    except subprocess.TimeoutExpired:
        pass
    proc.send_signal(signal.SIGTERM)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=timeout)


def _load_cursor(cursor_path: Path) -> int:
    if not cursor_path.exists():
        return -1
    try:
        t = cursor_path.read_text().strip()
        return int(t) if t else -1
    except (OSError, ValueError):
        return -1


def _read_proposal(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None    # a proposal read mid-write should not happen (the worker writes atomically -- see
                        # tools/evolve.py's own doc) -- treated as "not yet there", never fatal; the next scan retries


def sense(publish: Callable, stop_event, root: Path, poll_period: float = 5.0) -> None:
    """The sense thread body a `creature.body.SenseThread` runs. Reads `$ROOT/evolve/PROPOSAL-<n>.json`
    files in n order (the worker's own numbering, tools/evolve.py), publishing one "proposal" row per file
    not yet past the cursor, then persisting the cursor -- the cursor law (#230, and see the module
    docstring for why THIS cursor must be durable, unlike sit.py's)."""
    root = Path(root)
    evolve_dir = root / "evolve"
    cursor_path = evolve_dir / "CURSOR_SENSE"
    last_done = _load_cursor(cursor_path)

    while not stop_event.is_set():
        advanced = False
        if evolve_dir.exists():
            # sorted by the EXTRACTED INTEGER, never the raw path string: "PROPOSAL-10.json" sorts
            # lexicographically BEFORE "PROPOSAL-2.json" (bytewise '1' < '2'), which would advance the
            # cursor past 10 and then skip 2..9 forever (the SAME class of bug game.py's own manifest
            # names are zero-padded to avoid, "the filename's own zero-padded index sorts bytewise ==
            # numeric order" -- found here by re-reading this file against that exact precedent).
            numbered = []
            for p in evolve_dir.glob("PROPOSAL-*.json"):
                m = _PROPOSAL_RE.fullmatch(p.name)
                if m:
                    numbered.append((int(m.group(1)), p))
            for n, p in sorted(numbered):
                if n <= last_done:
                    continue
                data = _read_proposal(p)
                if data is None:
                    break   # not durable yet -- stop this scan, retry next period (order preserved)
                payload = json.dumps(data).encode("utf-8")
                publish("proposal", payload, dict(data), "json")
                last_done = n
                cursor_path.parent.mkdir(parents=True, exist_ok=True)
                cursor_path.write_text(str(last_done))   # AFTER the row is durable (#230)
                advanced = True
        if not advanced:
            stop_event.wait(poll_period)
