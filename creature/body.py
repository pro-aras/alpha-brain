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

from genome.machinery import GenomeError, parse_genome

from . import ask as ask_module
from .mind import Mind
from .tape import Tape, now_iso, read_tape

STATUS_PERIOD_S = 10.0
RESTART_BACKOFF_S = 1.0
MIND_TIMES_WINDOW_S = 60.0

# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.6 (docs/G4-WAVE3-CLAUSES.md W3-0b):
# BODY's declared thread roster, the five names the body knows about (eye+ear are one "maker" thread in
# this implementation, door covers the ask/folder/web senses, voice is the exam thread -- the check is a
# pure VALIDATION of the declared list against this known set, independent of how many real threads a run
# actually starts).
KNOWN_BODY_THREADS = frozenset({"eye", "ear", "door", "mind", "voice"})


def _check_body_threads(declared: Dict[str, dict]) -> None:
    """BODY undeclared -> nothing to check (the thread wiring the body actually runs is fixed by code
    either way, creature/genes.py's own finding). BODY declared -> every named thread must be one of
    KNOWN_BODY_THREADS, and "mind" must be named -- else the body refuses to start (GenomeError naming
    the bad thread), before any thread object is created."""
    body = declared.get("BODY")
    if body is None:
        return
    threads = body.get("threads", [])
    for name in threads:
        if name not in KNOWN_BODY_THREADS:
            raise GenomeError(f"BODY declares an unknown thread {name!r} (known: {sorted(KNOWN_BODY_THREADS)}): the body does not start")
    if "mind" not in threads:
        raise GenomeError(f"BODY declares threads {threads!r} without 'mind': the body does not start")


# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.5 (docs/G4-WAVE3-CLAUSES.md W3-0b):
# CRASH's declared policy. CRASH undeclared keeps today's unconditional default (PREREG §2.6's crash law
# stands regardless of the gene, genes.py's own finding); CRASH declared reads its own two sub-facts off
# the parsed dict. genome/machinery.py's CRASH grammar is a single fixed-string match today ("sense
# restart journal; mind page") so every genome this parser accepts sets BOTH sub-facts True -- the False
# branches below are real code, reachable the day that grammar loosens (raised in the builder report, not
# worked around: not this builder's file).
def _crash_policy(declared: Dict[str, dict]) -> "tuple[bool, bool]":
    crash = declared.get("CRASH")
    if crash is None:
        return True, True
    return crash.get("sense") == "restart journal", crash.get("mind") == "page"


def _rss_mb() -> float:
    # ru_maxrss is KB on Linux, bytes on macOS; this box is Linux (see the environment banner).
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class SenseThread(threading.Thread):
    """Runs `fn(publish, stop_event)` forever: `fn` is expected to loop internally until `stop_event` is
    set. An exception from `fn` is journaled as `sense_restart` and, when `restart` is True (the default,
    and CRASH's "sense restart journal" -- C1.5), `fn` is called again after 1 s (PREREG §2.6) -- the mind
    is unaffected. When `restart` is False (CRASH declared WITHOUT "sense restart", a state the parser
    cannot produce today -- C1.5's own raised gap) the event is still journaled once and the thread ends,
    never retrying. `plant`: "eye:100" raises inside `_publish` the Nth time THIS thread publishes that
    sense (counted across restarts, so the plant fires exactly once)."""

    def __init__(self, name: str, fn: Callable[[Callable, threading.Event], None], journal_fn: Callable[[Dict[str, object]], None],
                 on_publish: Callable[[str, bytes, Dict[str, object], str], Dict[str, object]], plant: Optional[str] = None,
                 restart: bool = True):
        super().__init__(name=f"sense-{name}", daemon=True)
        self.sense_name = name
        self.fn = fn
        self.journal_fn = journal_fn
        self.on_publish = on_publish
        self.restart = restart
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
                if not self.restart:
                    return    # C1.5: CRASH without "sense restart" -- journaled once, thread ends, no retry
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
        # edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1 (docs/G4-WAVE3-CLAUSES.md
        # W3-0b): the genome is read once, here, before Mind exists (Mind is built only in start()) --
        # Tape's own directory (C1.2) and the BODY thread-roster refusal (C1.6) both need the declared
        # values at construction time, and HEART's/CRASH's (C1.1/C1.5) are cheapest read once too.
        self._declared: Dict[str, dict] = parse_genome(self.genome_path.read_text()).declared
        _check_body_threads(self._declared)
        self._status_period_s: float = float(self._declared.get("HEART", {}).get("every_s", STATUS_PERIOD_S))
        self._crash_restart_on, self._crash_page_on = _crash_policy(self._declared)
        self._tape_declared_path: Optional[str] = self._declared.get("TAPE", {}).get("path")
        self.root.mkdir(parents=True, exist_ok=True)
        self.tape = Tape(self.root, declared_path=self._tape_declared_path)
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
        st = SenseThread(name, fn, self._journal_event, self._publish, plant=plant, restart=self._crash_restart_on)
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
        for row in read_tape(self.root, declared_path=self._tape_declared_path):
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
        if self._crash_page_on:    # C1.5: CRASH without "mind page" -- STATUS.crash + exit 3 stand (#230 is not a gene), no PAGE.json
            self._append_page({"at": at, "why": f"mind_crash: {e!r}", "status": status})
        sys.stderr.write(f"creature.body: mind crashed at seq {row.get('seq')}: {e!r}\n")
        os._exit(3)      # PREREG §2.6: the process EXITS non-zero; no loop

    # ------------------------------------------------------------------ STATUS (PREREG §2.5)
    def _status_loop(self) -> None:
        while not self.stop_event.is_set():
            self._write_status(self._build_status())
            self.stop_event.wait(self._status_period_s)   # C1.1: HEART's declared every_s, default STATUS_PERIOD_S
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
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: the three numbers that would have shown life 1's spent budget at 07:41 +04, on EVERY write (#164)
            "arrivals": int(org.arrivals), "budget_left": int(org.budget_left), "births_refused_budget": int(org.c["births_refused_budget"]),
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


# edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:08 +0400 — C1.3/C2 (docs/G4-WAVE3-CLAUSES.md
# W3-0b, W3-6 step 4): the two WORLD-driven derivations `main()` needs, factored out so they are testable
# without invoking the CLI (which blocks in a signal-driven loop). WORLD's own `arrival_every_h` regex in
# genome/machinery.py is `(\d+)` (whole hours only) -- a genome cannot express the PREREG toy's own
# "arrivals every 0.01 h" example; RAISED in the builder report, not worked around (not this builder's
# file). `_maker_args_from_declared` is exercised directly against hand-built declared dicts for that
# reason (tests/creature/test_world_maker.py), same as C1.4/C1.5's pure-function toys.
def _maker_args_from_declared(declared: Dict[str, dict], default_period: float, default_window_s: float) -> "tuple[float, float]":
    """WORLD undeclared -> the given defaults, unchanged (today's 5.0 s / world_maker.WINDOW_SECONDS).
    WORLD declared -> its own `drawn every <n> s` / `arrivals every <h> h`."""
    world_declared = declared.get("WORLD")
    if world_declared is None:
        return default_period, default_window_s
    return float(world_declared["drawn_every_s"]), float(world_declared["arrival_every_h"]) * 3600.0


def _declared_folder_dir(declared: Dict[str, dict]) -> Optional[Path]:
    """C2: the folder door's directory from declared['WORLD']'s `folder <dir>`, relative to the REPO root
    (this file's own parents[1] -- never the run root), gated on creature.senses.folder.FOLDER_DOOR_GATED
    so a genome line arms nothing until the code carrying G4-6 exists (Claude flips the constant)."""
    from .senses import folder as folder_sense   # lazily, same discipline as world_maker's own import below
    if not folder_sense.FOLDER_DOOR_GATED:
        return None
    world_declared = declared.get("WORLD")
    if not world_declared or not world_declared.get("folder"):
        return None
    return Path(__file__).resolve().parents[1] / world_declared["folder"]


# edit: Claude (Fable 5.1), 2026-09-21 20:57 +0400 — the 8 h SEAM LIVES (docs/G5-SEAM-LIFE-PLAN.md §1): world_maker.sense() has always
# taken `plant_after_canvases`, but main() never passed it, so every life ran the module default (15,000 canvases ≈ hour 21)
# and an 8 h life could NEVER show the plant (SOLUTIONS #228 (a): a plant placed where the mechanism cannot fire). `--plant-after N`
# on the CLI now reaches the maker partial; the default is unchanged (the 24 h lives keep hour ~21). Both derivations are
# factored out of main() so tests can pin the LAST link — the partial's keywords (#180) — without the signal-driven loop.
def _plant_after_from_argv(argv: List[str], default: int) -> int:
    """`--plant-after N` -> N (an int; a malformed value raises); absent -> `default` unchanged."""
    if "--plant-after" not in argv:
        return int(default)
    return int(argv[argv.index("--plant-after") + 1])


def _maker_sense_fn(argv: List[str], declared: Dict[str, dict], root: Path):
    """The maker sense's partial exactly as main() runs it: WORLD's `drawn every`/`arrivals every` (or the
    --maker-period / --window-seconds overrides) and --plant-after (default world_maker.PLANT_AFTER_CANVASES)."""
    from . import world_maker   # imported lazily: body.py must not hard-depend on world_maker at import time
    import functools
    default_period, default_window_s = _maker_args_from_declared(declared, 5.0, world_maker.WINDOW_SECONDS)
    maker_period = float(argv[argv.index("--maker-period") + 1]) if "--maker-period" in argv else default_period
    window_seconds = float(argv[argv.index("--window-seconds") + 1]) if "--window-seconds" in argv else default_window_s
    plant_after = _plant_after_from_argv(argv, world_maker.PLANT_AFTER_CANVASES)
    return functools.partial(world_maker.sense, root=root, period=maker_period, window_seconds=window_seconds,
                             plant_after_canvases=plant_after)


# ============================================================================ CLI
def main(argv: List[str]) -> int:
    root = Path(argv[argv.index("--root") + 1])
    genome_path = Path(argv[argv.index("--genome") + 1])
    # C1.3/C2: read once, here -- Body.__init__ parses the same text again for its own (TAPE/HEART/
    # CRASH/BODY) purposes; this is the CLI's own copy, used for WORLD's maker period/window and the
    # folder door's directory below.
    genome_for_cli = parse_genome(genome_path.read_text())
    declared = genome_for_cli.declared
    no_maker = "--no-maker" in argv

    body = Body(root, genome_path)
    if not no_maker:
        plant = os.environ.get("CREATURE_PLANT_EXCEPTION")
        fn = _maker_sense_fn(argv, declared, root)   # WORLD's period/window (+ CLI overrides) + --plant-after
        body.add_sense("maker", fn, plant=plant)

    # C2: --folder PATH stays an explicit override for tests, regardless of the gate (A12's own road,
    # unchanged); otherwise the door arms only from the genome's own WORLD line, behind FOLDER_DOOR_GATED.
    folder_dir = Path(argv[argv.index("--folder") + 1]) if "--folder" in argv else _declared_folder_dir(declared)
    folder_period = float(argv[argv.index("--folder-period") + 1]) if "--folder-period" in argv else 30.0
    if folder_dir is not None:
        from .senses import folder as folder_sense   # lazily, same discipline as world_maker above
        import functools
        canvas = int(genome_for_cli.gaze["canvas"])
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
