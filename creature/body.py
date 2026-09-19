# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:05 +0400 — A3: the body (docs/G4-PREREG.md §2, §2.5, §2.6, §2.10).
"""creature/body.py — the body: sense threads over a tape, ONE mind thread, a STATUS thread, crash
isolation, SIGTERM -> snapshot + stop.

Wall clock: the body (not the mind) is where wall-clock reads belong -- STATUS timestamps, the
sense-restart backoff, the SIGTERM/stop sequencing. The determinism law (PREREG §2.3) binds
creature/mind.py only.
"""
from __future__ import annotations

import collections
import json
import os
import queue
import resource
import signal
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import ask as ask_module
from .mind import Mind
from .tape import Tape, now_iso, read_tape

STATUS_PERIOD_S = 10.0
RESTART_BACKOFF_S = 1.0
MIND_TIMES_WINDOW_S = 60.0


def _rss_mb() -> float:
    # ru_maxrss is KB on Linux, bytes on macOS; this box is Linux (see the environment banner).
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class SenseThread(threading.Thread):
    """Runs `fn(publish, stop_event)` forever: `fn` is expected to loop internally until `stop_event` is
    set. An exception from `fn` is journaled as `sense_restart` and `fn` is called again after 1 s
    (PREREG §2.6) -- the mind is unaffected. `plant`: "eye:100" raises inside `_publish` the Nth time
    THIS thread publishes that sense (counted across restarts, so the plant fires exactly once)."""

    def __init__(self, name: str, fn: Callable[[Callable, threading.Event], None], journal_fn: Callable[[Dict[str, object]], None],
                 on_publish: Callable[[str, bytes, Dict[str, object], str], Dict[str, object]], plant: Optional[str] = None):
        super().__init__(name=f"sense-{name}", daemon=True)
        self.sense_name = name
        self.fn = fn
        self.journal_fn = journal_fn
        self.on_publish = on_publish
        self._stop = threading.Event()
        self._plant_sense: Optional[str] = None
        self._plant_n: Optional[int] = None
        if plant:
            s, n = plant.split(":")
            self._plant_sense, self._plant_n = s, int(n)
        self._plant_counts: Dict[str, int] = {}

    def stop(self) -> None:
        self._stop.set()

    def _publish(self, sense: str, payload: bytes, meta: Dict[str, object], ext: str) -> Dict[str, object]:
        if self._plant_sense is not None and sense == self._plant_sense:
            self._plant_counts[sense] = self._plant_counts.get(sense, 0) + 1
            if self._plant_counts[sense] == self._plant_n:
                raise RuntimeError(f"CREATURE_PLANT_EXCEPTION fired: {sense}:{self._plant_n}")
        return self.on_publish(sense, payload, meta, ext)

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                self.fn(self._publish, self._stop)
            except Exception as e:
                self.journal_fn({"event": "sense_restart", "sense": self.sense_name, "error": repr(e)})
                self._stop.wait(RESTART_BACKOFF_S)
                continue
            else:
                break     # fn returned cleanly (saw the stop event) -- no restart


class Body:
    """The body: one Tape, one queue, one mind thread, one STATUS thread, N sense threads. `add_sense`
    before `start()`. `stop()` snapshots the mind, writes a final STATUS, and journals a stop event."""

    def __init__(self, root: Path, genome_path: Path, blind: frozenset = frozenset()):
        self.root = Path(root)
        self.genome_path = Path(genome_path)
        self.blind = blind
        self.root.mkdir(parents=True, exist_ok=True)
        self.tape = Tape(self.root)
        self.q: "queue.Queue[Dict[str, object]]" = queue.Queue()
        self._publish_lock = threading.Lock()
        self._status_lock = threading.Lock()
        self.sense_threads: List[SenseThread] = []
        self.stop_event = threading.Event()
        self.started_at = now_iso()
        self.sense_restarts = 0
        self.crash: Optional[Dict[str, object]] = None
        self._mind_times: "collections.deque[tuple[float, float]]" = collections.deque(maxlen=200000)
        self.mind: Optional[Mind] = None
        self._mind_thread: Optional[threading.Thread] = None
        self._status_thread: Optional[threading.Thread] = None
        self._ask_thread: Optional[threading.Thread] = None
        self._exam_thread: Optional[threading.Thread] = None
        self._started = False
        self._stopped = False

    # ------------------------------------------------------------------ wiring
    def add_sense(self, name: str, fn: Callable[[Callable, threading.Event], None], plant: Optional[str] = None) -> SenseThread:
        st = SenseThread(name, fn, self._journal_event, self._publish, plant=plant)
        self.sense_threads.append(st)
        return st

    def _publish(self, sense: str, payload: bytes, meta: Dict[str, object], ext: str) -> Dict[str, object]:
        with self._publish_lock:
            row = self.tape.publish(sense, payload, meta, ext)
            self.q.put(row)
        return row

    def _journal_event(self, event: Dict[str, object]) -> None:
        at = now_iso()
        row = {"seq": None, "at": at, **event}
        date = at[:10]
        path = self.root / "journal" / f"{date}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        if event.get("event") == "sense_restart":
            with self._status_lock:
                self.sense_restarts += 1

    # ------------------------------------------------------------------ startup: resume + replay backlog
    def start(self) -> None:
        state_ok = (self.root / "state" / "organism.npz").exists()
        if state_ok:
            self.mind, last_seq = Mind.resume(self.genome_path, self.root, blind=self.blind)
        else:
            self.mind = Mind(self.genome_path, self.root, blind=self.blind)
            last_seq = 0
        backlog = 0
        for row in read_tape(self.root):
            if row["seq"] > last_seq:
                self._consume(row)
                backlog += 1
        self._journal_event({"event": "start", "resumed_from_seq": last_seq, "backlog_replayed": backlog})

        self._mind_thread = threading.Thread(target=self._mind_loop, name="mind", daemon=True)
        self._mind_thread.start()
        self._status_thread = threading.Thread(target=self._status_loop, name="status", daemon=True)
        self._status_thread.start()
        self._ask_thread = threading.Thread(target=ask_module.inbox_loop, args=(self.root, self.stop_event),
                                             kwargs={"poll_period": 1.0}, name="ask", daemon=True)
        self._ask_thread.start()
        if "EXAM" in self.mind.genome.declared:      # A13 (PREREG §11.4): never true through a real genome file
            from . import exam as exam_module         # today (EXAM's own parser clause is not yet on master) — wired for when it lands.
            every = int(self.mind.genome.declared["EXAM"]["every"])
            self._exam_thread = threading.Thread(target=exam_module.voice_loop, args=(self.root, self.genome_path, self.stop_event),
                                                  kwargs={"every_canvases": every, "poll_period": 5.0}, name="exam", daemon=True)
            self._exam_thread.start()
        for st in self.sense_threads:
            st.start()
        self._started = True

    # ------------------------------------------------------------------ the mind loop
    def _consume(self, row: Dict[str, object]) -> None:
        prev_snap = self.mind.snapshot_count
        t0 = time.perf_counter()
        self.mind.consume(row)
        ms = (time.perf_counter() - t0) * 1000.0
        with self._status_lock:
            self._mind_times.append((time.perf_counter(), ms))
        if self.mind.snapshot_count > prev_snap:
            self._journal_event({"event": "snapshot", "snapshots": self.mind.snapshot_count, "at_moment": self.mind.org.t})

    def _mind_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                row = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self._consume(row)
            except Exception as e:
                self._handle_mind_crash(e, row)
                return

    def _handle_mind_crash(self, e: Exception, row: Dict[str, object]) -> None:
        at = now_iso()
        with self._status_lock:
            self.crash = {"at": at, "error": repr(e), "seq": row.get("seq")}
        status = self._build_status()
        self._write_status(status)
        self._append_page({"at": at, "why": f"mind_crash: {e!r}", "status": status})
        sys.stderr.write(f"creature.body: mind crashed at seq {row.get('seq')}: {e!r}\n")
        os._exit(3)      # PREREG §2.6: the process EXITS non-zero; no loop

    # ------------------------------------------------------------------ STATUS (PREREG §2.5)
    def _status_loop(self) -> None:
        while not self.stop_event.is_set():
            self._write_status(self._build_status())
            self.stop_event.wait(STATUS_PERIOD_S)
        self._write_status(self._build_status())

    def _build_status(self) -> Dict[str, object]:
        now = now_iso()
        with self._status_lock:
            cutoff = time.perf_counter() - MIND_TIMES_WINDOW_S
            recent = [ms for ts, ms in self._mind_times if ts >= cutoff]
            sense_restarts = self.sense_restarts
            crash = self.crash
        org = self.mind.org
        return {
            "heartbeat_at": now, "started_at": self.started_at,
            "moments": org.t, "tape_rows": self.mind.last_seq, "journal_rows": self.mind.journal_rows_written,
            "births": len(org.births), "edges_born": int(org.c["edges_born"]), "edges_pruned": int(org.c["edges_pruned"]),
            "cells": org.total_cells(), "sight_only_skipped": self.mind.sight_only_skipped,
            "sense_restarts": sense_restarts, "snapshots": self.mind.snapshot_count,
            "last_seq": self.mind.last_seq, "mind_ms_median_1min": (statistics.median(recent) if recent else None),
            "rss_mb": round(_rss_mb(), 2), "crash": crash,
            # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — PREREG §11.1 step 3's STATUS fields, written on EVERY status write (#164):
            # the mind computed them (think_counters) and nothing exported them (#163's class: computing and exporting differ).
            **{k: int(v) for k, v in getattr(self.mind, "think_counters", {}).items()},
            "episodes": int(self.mind.episodes.n_written) if getattr(self.mind, "episodes", None) is not None else 0,
            "sleeps": int(getattr(self.mind, "sleep_count", 0)),
        }

    def _write_status(self, status: Dict[str, object]) -> None:
        path = self.root / "STATUS.json"
        tmp = self.root / "STATUS.json.tmp"
        tmp.write_text(json.dumps(status))
        os.replace(str(tmp), str(path))

    def _append_page(self, row: Dict[str, object]) -> None:
        path = self.root / "pages.jsonl"
        with path.open("a") as f:
            f.write(json.dumps(row) + "\n")

    # ------------------------------------------------------------------ shutdown
    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self.stop_event.set()
        for st in self.sense_threads:
            st.stop()
        for st in self.sense_threads:
            st.join(timeout=5.0)
        if self._mind_thread is not None:
            self._mind_thread.join(timeout=5.0)
        if self._ask_thread is not None:
            self._ask_thread.join(timeout=5.0)
        if self._exam_thread is not None:
            self._exam_thread.join(timeout=5.0)
        if self.mind is not None:
            prev_snap = self.mind.snapshot_count
            self.mind.close()
            if self.mind.snapshot_count > prev_snap:
                self._journal_event({"event": "snapshot", "snapshots": self.mind.snapshot_count, "at_moment": self.mind.org.t})
        self._write_status(self._build_status())
        self._journal_event({"event": "stop"})
        if self._status_thread is not None:
            self._status_thread.join(timeout=STATUS_PERIOD_S + 1.0)


# ============================================================================ CLI
def main(argv: List[str]) -> int:
    root = Path(argv[argv.index("--root") + 1])
    genome_path = Path(argv[argv.index("--genome") + 1])
    maker_period = float(argv[argv.index("--maker-period") + 1]) if "--maker-period" in argv else 5.0
    no_maker = "--no-maker" in argv
    # A12 (PREREG §11.3): the folder door is armed only by an explicit --folder PATH, default OFF — it is
    # only meant to be lit after G4-6 (a re-run of G4-3 with two senses on the tape), Claude's own gate.
    folder_dir = Path(argv[argv.index("--folder") + 1]) if "--folder" in argv else None
    folder_period = float(argv[argv.index("--folder-period") + 1]) if "--folder-period" in argv else 30.0

    body = Body(root, genome_path)
    if not no_maker:
        from . import world_maker   # imported lazily: body.py must not hard-depend on world_maker at import time
        plant = os.environ.get("CREATURE_PLANT_EXCEPTION")
        import functools
        fn = functools.partial(world_maker.sense, root=root, period=maker_period)
        body.add_sense("maker", fn, plant=plant)
    if folder_dir is not None:
        from .senses import folder as folder_sense   # lazily, same discipline as world_maker above
        from genome.machinery import parse_genome
        import functools
        canvas = int(parse_genome(genome_path.read_text()).gaze["canvas"])   # body.mind does not exist until start(); read it straight from the genome file
        ffn = functools.partial(folder_sense.sense, world_dir=folder_dir, root=root, canvas=canvas, period=folder_period)
        body.add_sense("folder", ffn)

    body.start()
    stop_requested = threading.Event()

    def _sigterm(signum, frame):
        stop_requested.set()

    signal.signal(signal.SIGTERM, _sigterm)
    signal.signal(signal.SIGINT, _sigterm)
    try:
        while not stop_requested.is_set():
            time.sleep(0.2)
    finally:
        body.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
