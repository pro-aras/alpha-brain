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
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md):
        # SIT and SENSE_BODY, wired the same C1.7 shape EXAM uses above (gated on the gene's own declared presence;
        # started here, after self.mind exists, via add_sense so both get the SAME crash-isolation/restart/journal
        # machinery every other sense has — unlike the exam thread above, which predates SenseThread and journals
        # its own EVENT rows directly (creature/exam.py), SIT and body publish TAPE rows, exactly the shape a
        # `SenseThread` is for. `add_sense` may be called any time before the `for st in self.sense_threads: st.start()`
        # loop just below — it only appends to the list; nothing here requires it to run before start().
        import functools
        if "SIT" in self.mind.genome.declared:
            from .senses import sit as sit_sense
            sit_every = int(self.mind.genome.declared["SIT"]["every"])
            sit_fn = functools.partial(sit_sense.sense, root=self.root, genome_path=self.genome_path,
                                        every_canvases=sit_every, poll_period=5.0)
            self.add_sense("sit", sit_fn)
        if "SENSE_BODY" in self.mind.genome.declared:
            from .senses import body_sense as body_sense_module
            body_period = float(self.mind.genome.declared["SENSE_BODY"]["period_s"])
            body_fields = list(self.mind.genome.declared["SENSE_BODY"]["fields"])
            body_fn = functools.partial(body_sense_module.sense, root=self.root, fields=body_fields, period_s=body_period)
            self.add_sense("body", body_fn)
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
        # item 2 (MOTOR-HANDS.md G-MOT-4): the hands door, the SAME C1.7 shape SIT/SENSE_BODY use above
        # (gated on the gene's own declared presence; started via add_sense so it gets the same crash-
        # isolation/restart/journal machinery every other sense here has).
        hands_cfg = _declared_hands_config(self.mind.genome.declared)
        if hands_cfg is not None:
            from .senses import hands as hands_sense
            hands_fn = functools.partial(hands_sense.sense, root=self.root, jail_path=hands_cfg["jail_path"],
                                          shelf_dir=hands_cfg["shelf_dir"], cpu=hands_cfg["cpu"],
                                          mem=hands_cfg["mem"], wall=hands_cfg["wall"], poll_period=0.2)
            self.add_sense("hands", hands_fn)
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
            # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — the row's sense rides with the timing so STATUS can state the cost per CANVAS (#162)
            self._mind_times.append((time.perf_counter(), ms, row.get("sense")))
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
            recent_rows = [(ms, sense) for ts, ms, sense in self._mind_times if ts >= cutoff]
            recent = [ms for ms, _s in recent_rows]
            sense_restarts = self.sense_restarts
            crash = self.crash
        # edit: Claude (Fable 5.1), 2026-09-22 10:3x +0400 — the mind's cost in the verdict probe's unit: every row's consume time in the
        # window ÷ eye rows (one canvas each) in the window; None when no eye row fell in it — the key is on EVERY write (#164, #162)
        eye_rows = sum(1 for _ms, s in recent_rows if s == "eye")
        ms_per_canvas = (sum(recent) / eye_rows) if eye_rows else None
        org = self.mind.org
        return {
            "heartbeat_at": now, "started_at": self.started_at,
            "moments": org.t, "tape_rows": self.mind.last_seq, "journal_rows": self.mind.journal_rows_written,
            "births": len(org.births), "edges_born": int(org.c["edges_born"]), "edges_pruned": int(org.c["edges_pruned"]),
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: the three numbers that would have shown life 1's spent budget at 07:41 +04, on EVERY write (#164)
            "arrivals": int(org.arrivals), "budget_left": int(org.budget_left), "births_refused_budget": int(org.c["births_refused_budget"]),
            # edit: Claude (Fable 5.1), 2026-09-22 12:0x +0400 — the birth LEDGER on every write (#164): NMAX is a lifetime budget of ids (G4 §3 B7 never
            # reuses one); g5-seam-1 spent its 2,000 sight ids by hour ~6 and refused 1,988 births while this surface showed budget refusals 0
            "sight_born": int(org.sight.n), "words_born": int(org.words.n), "sight_nmax": int(org.sight.nmax), "words_nmax": int(org.words.nmax),
            "births_refused_nmax": int(org.c["births_refused_nmax"]), "births_refused_frozen": int(org.c["births_refused_frozen"]),
            "births_refused_redundant": int(org.c["births_refused_redundant"]),
            "births_refused_caps": int(org.c["births_refused_budget"]) + int(org.c["births_refused_nmax"]) + int(org.c["births_refused_frozen"]),
            "cells": org.total_cells(), "sight_only_skipped": self.mind.sight_only_skipped,
            "sense_restarts": sense_restarts, "snapshots": self.mind.snapshot_count,
            "last_seq": self.mind.last_seq, "mind_ms_median_1min": (statistics.median(recent) if recent else None),
            "mind_ms_per_canvas_1min": (round(ms_per_canvas, 4) if ms_per_canvas is not None else None),
            # edit: Claude (Fable 5.1), 2026-09-22 10:49 +0400 — rows delivered by the senses and not yet consumed: a mind behind its world
            # (g5-seam-1 sat 6,917 rows behind under the readers' load, 2026-09-22 10:34 +04, and no surface said so — #164, #180)
            "mind_backlog_rows": self.q.qsize(),
            "rss_mb": round(_rss_mb(), 2), "crash": crash,
            # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — PREREG §11.1 step 3's STATUS fields, written on EVERY status write (#164):
            # the mind computed them (think_counters) and nothing exported them (#163's class: computing and exporting differ).
            **{k: int(v) for k, v in getattr(self.mind, "think_counters", {}).items()},
            "episodes": int(self.mind.episodes.n_written) if getattr(self.mind, "episodes", None) is not None else 0,
            "sleeps": int(getattr(self.mind, "sleep_count", 0)),
            # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: the reflex ring's own count, exported
            # on every write (#164's law: a computed value and an exported one are different features, #163's class).
            "outcome_episodes": int(self.mind.outcome_episodes.n_written) if getattr(self.mind, "outcome_episodes", None) is not None else 0,
            # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:41 +0400 — LIFE-D-ACT-SOUND.md items 2/3
            # (L-8/L-13): `acts_chosen` is a dict, one count PER VERB (G-MOT-1's census, never a total,
            # #165), never omitted (#164, every write). `getattr` defaults cover every genome that never
            # declares ACT's turn/step verbs or FAST's sound key -- those never build the counters at all.
            "acts_chosen": dict(getattr(self.mind, "acts_chosen", {}) or {}),
            "act_mismatches": int(getattr(self.mind, "act_mismatches", 0)),
            "sound_events": int(getattr(self.mind, "sound_events", 0)),
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # item 2 (G-MOT-1's census shape, never a total, #165): `runs_by_program` is a dict, one count
            # PER PROGRAM; `runs` is its sum, for a reader that wants the total without summing itself.
            # `getattr` defaults cover every genome that never declares HANDS/SENSE_TOUCH/SENSE_SMELL.
            "runs_by_program": dict(getattr(self.mind, "runs_chosen", {}) or {}),
            "runs": sum((getattr(self.mind, "runs_chosen", {}) or {}).values()),
            "hands_no_road": int(getattr(self.mind, "hands_no_road", 0)),
            "touch_events": int(getattr(self.mind, "touch_events", 0)),
            "smell_events": int(getattr(self.mind, "smell_events", 0)),
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


# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:3x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1:
# the game door's own arming, mirroring _declared_folder_dir's own shape and gate discipline exactly
# (C2/C3's convention, reused rather than re-invented).
def _declared_game_config(declared: Dict[str, dict]) -> Optional[Dict[str, object]]:
    """WORLD_GAME undeclared -> None (arms nothing). WORLD_GAME declared -> its own parsed dict, gated on
    creature.senses.game.GAME_DOOR_GATED so a genome line arms nothing until the code carrying it exists
    (the same "flip the constant, not the live creature" discipline C2/C3 used for the folder door --
    Claude decides separately when to deploy this branch and restart creature.service)."""
    from .senses import game as game_sense   # lazily, same discipline as folder's own import below
    if not game_sense.GAME_DOOR_GATED:
        return None
    return declared.get("WORLD_GAME")


# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:41 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8): the
# body's own half of the ONE gate (creature/senses/game.py:mind_drives_acts) that decides whether
# --act-file ever reaches the worker -- the SAME predicate creature/mind.py reads before it ever writes
# root/game/ACT, so the two sides can never disagree (#180).
def _game_act_file_path(root: Path, declared: Dict[str, dict]) -> Optional[Path]:
    """None (the worker keeps its own seeded schedule) unless this genome's ACT vocabulary carries BOTH
    "turn" and "step" -- then `root/game/ACT`, the path the mind writes and the worker's --act-file
    reads."""
    from .senses import game as game_sense
    if not game_sense.mind_drives_acts(declared):
        return None
    return root / "game" / "ACT"


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


# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2
# (MOTOR-HANDS.md G-MOT-4): the hands door's own arming, mirroring _declared_folder_dir/_declared_game_
# config's own shape and gate discipline exactly (C2/C3's convention, reused rather than re-invented).
def _declared_hands_config(declared: Dict[str, dict]) -> Optional[Dict[str, object]]:
    """HANDS undeclared, or declared in its SHORT form (no shelf -- the pre-existing "HANDS jail <path>"
    grammar, test_parse_g4.py's own pin) -> None (arms nothing, exactly like a WORLD line with no folder).
    HANDS declared in its FULL form -> `{"jail_path", "shelf_dir", "cpu", "mem", "wall"}`, gated on
    creature.senses.hands.HANDS_DOOR_GATED so a genome line arms nothing until the code carrying it exists.
    `jail_path` resolves against this file's own parents[2] (the worktree's PARENT -- alpha3/ is a SIBLING
    tree, never inside this repo); `shelf_dir` resolves against parents[1] (the repo root, the SAME root
    `_declared_folder_dir` above already uses for WORLD's own `folder`) -- `creature/mind.py`'s own
    `_hands_paths` resolves the identical two roots for the SAME reason (LIFE-F-HANDS-TOUCH-SMELL.md's own
    module-level comment there)."""
    from .senses import hands as hands_sense
    if not hands_sense.HANDS_DOOR_GATED:
        return None
    hands = declared.get("HANDS")
    if hands is None or "shelf" not in hands:
        return None
    return {
        "jail_path": Path(__file__).resolve().parents[2] / str(hands["jail"]),
        "shelf_dir": Path(__file__).resolve().parents[1] / str(hands["shelf"]),
        "cpu": int(hands["cpu"]), "mem": int(hands["mem"]), "wall": int(hands["wall"]),
    }


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
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:24 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item
        # 4: `smell` gated on the genome's own SENSE_SMELL declared presence (C1.7's own shape) -- False
        # (folder.sense's own default) when undeclared, byte-identical to before this brief.
        smell_on = "SENSE_SMELL" in declared
        ffn = functools.partial(folder_sense.sense, world_dir=folder_dir, root=root, canvas=canvas,
                                 period=folder_period, smell=smell_on)
        body.add_sense("folder", ffn)

    # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 22:1x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md
    # item 2: the sound ear, listening AT THE SAME FOLDER DOOR the picture sense watches (the brief's own
    # words: "a sense thread listening at the folder door for audio files") -- `--ear-sound-dir PATH`
    # overrides it for tests, regardless of the gate; otherwise it arms only when BOTH a folder door
    # directory AND `SENSE ear-sound ...` are present (genome_for_cli.ear_sound, a plain Genome field,
    # never `declared[...]` -- see genome/machinery.py's own comment on that field).
    ear_sound_dir = (Path(argv[argv.index("--ear-sound-dir") + 1]) if "--ear-sound-dir" in argv else folder_dir)
    from .senses import ear as ear_sense   # lazily, same discipline as folder/game above
    ear_sound_cfg = genome_for_cli.ear_sound if ear_sense.EAR_SOUND_DOOR_GATED else None
    if ear_sound_dir is not None and ear_sound_cfg is not None:
        import functools
        efn = functools.partial(ear_sense.sense, audio_dir=ear_sound_dir, root=root,
                                 rate=int(ear_sound_cfg["rate"]), period=folder_period)
        body.add_sense("ear_sound", efn)

    # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:3x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md
    # item 1: the game door, arming from declared['WORLD_GAME'] behind GAME_DOOR_GATED (C2/C3's own
    # convention) -- the worker needs its seed/game-id/tile from WORLD_GAME regardless of any override, so
    # (unlike --folder, which needs no per-line config) --game-door only overrides the DIRECTORY, never
    # substitutes for a missing WORLD_GAME line.
    game_cfg = _declared_game_config(declared)
    game_door_dir = (Path(argv[argv.index("--game-door") + 1]) if "--game-door" in argv
                      else (root / "game_door" if game_cfg is not None else None))
    game_proc = None
    game_stop_file = None
    if game_cfg is not None:
        from .senses import game as game_sense   # lazily, same discipline as folder above
        import functools
        canvas = int(genome_for_cli.gaze["canvas"])
        game_stop_file = root / "game" / "STOP"
        game_stop_file.parent.mkdir(parents=True, exist_ok=True)
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:41 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8):
        # --act-file only when this genome's ACT vocabulary drives the game (_game_act_file_path's own gate).
        act_file = _game_act_file_path(root, declared)
        game_proc = game_sense.start_worker(
            game_door_dir, seed=int(game_cfg["seed"]), game=str(game_cfg["game"]), tile=int(game_cfg["tile"]),
            period_s=float(game_cfg["every_s"]), stop_file=game_stop_file, act_file=act_file)
        gfn = functools.partial(game_sense.sense, door_dir=game_door_dir, root=root, canvas=canvas, poll_period=0.5)
        body.add_sense("game", gfn)

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
        if game_proc is not None:
            from .senses import game as game_sense
            game_sense.stop_worker(game_proc, stop_file=game_stop_file)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
