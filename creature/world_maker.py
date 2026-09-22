# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 22:22 +0400 — A4: the world-maker (docs/G4-PREREG.md §2.8).
"""creature/world_maker.py — a pure schedule of (SEED, window) + a sense thread that publishes it.

`schedule`/`make` are pure functions of their integer arguments (no I/O, no clock) so the stream a maker
run produces is fully replayable from its seed. `sense()` is the thread body a `creature.body.SenseThread`
runs: it is the only impure part (it reads wall clock for window timing and writes truth files), and it
NEVER writes memory (G4-1's writer sweep: only `root/truth/*.json`, never state/journal/memory).
"""
from __future__ import annotations

import io
import json
import re
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from genome import world

WINDOW_SECONDS = 6 * 3600          # PREREG §2.8: windows of 6 h
DEFAULT_SEED = 20260920            # never 2 (G1's held-out seed); matches docs/G4-DESIGN.md §9's draft SEED
PLANT_AFTER_CANVASES = 15000       # the plant shows in the hour after this many canvases (PREREG §2.8)
PLANT_WINDOW_S = 3600.0
PLANT_SHOWINGS = 5
_PLANT_MARKER = 10 ** 6            # a seed-tuple offset that never collides with a real window number


def schedule(seed: int, window: int) -> List[str]:
    """Pure: the things shown in `window`. Even windows (0, 2, 4, ...) show world.THINGS_11; odd windows
    show world.THINGS_ARRIVAL2 plus 3 of THINGS_11 chosen by an rng seeded on (seed, window) — a draw
    kept separate from make()'s per-canvas rng (seed, window, i) so the two never collide."""
    if window % 2 == 0:
        return list(world.THINGS_11)
    rng = np.random.default_rng([int(seed), int(window), _PLANT_MARKER])
    chosen = rng.choice(np.array(world.THINGS_11, dtype=object), size=3, replace=False)
    return list(world.THINGS_ARRIVAL2) + [str(c) for c in chosen]


def make(seed: int, window: int, i: int) -> Tuple[str, np.ndarray, Dict[str, object]]:
    """Pure: (thing, rgb, truth) for canvas `i` of `window`. ONE rng, default_rng([seed, window, i]):
    its first draw picks the thing from schedule(seed, window), its remaining draws render it
    (world.render_canvas) — so `make` is a pure function of its three integer arguments."""
    things = schedule(seed, window)
    rng = np.random.default_rng([int(seed), int(window), int(i)])
    thing = things[int(rng.integers(0, len(things)))]
    rgb, truth = world.render_canvas(thing, rng)
    return thing, rgb, truth


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _publish_canvas(publish: Callable, root: Path, moment: str, thing: str, rgb: np.ndarray, truth: Dict[str, object],
                     answering: Optional[str] = None) -> None:
    """ear (word bytes) THEN eye (PNG) — the tape order law (§2.2) — then the truth file, keyed by the
    EYE row's own seq, under root/truth/ (never on the tape, §2.1). `answering`, when given (L-10, the
    QUESTION door), is stamped on BOTH rows' meta -- the plan's own text: "the row's meta carries
    `answering: 'q-<seq>'`" — never touching the shape of an ordinary (unanswering) canvas's meta, which
    is exactly what it always was (a genome/replay reading an ordinary row sees no new key)."""
    ear_meta: Dict[str, object] = {"moment": moment, "source": "maker", "word": thing}
    eye_meta: Dict[str, object] = {"moment": moment, "source": "maker"}
    if answering is not None:
        ear_meta["answering"] = answering
        eye_meta["answering"] = answering
    publish("ear", thing.encode("utf-8"), ear_meta, "txt")
    eye_row = publish("eye", _png_bytes(rgb), eye_meta, "png")
    truth_dir = root / "truth"
    truth_dir.mkdir(parents=True, exist_ok=True)
    (truth_dir / f"{eye_row['seq']:09d}.json").write_text(json.dumps(truth))


# ============================================================================ L-10: QUESTION's door
# edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:1x +0400 — L-10 (docs/briefs/LIFE-C-QUESTION-SENTENCE.md
# task 1; NEXT-LIFE-PLAN-2026-09-22.md §4 L-10): the world-maker's door polls `run/ask/out/` and answers a
# `what-is` whose moment id names a canvas IT DREW (the "w<4>i<6>t<9>" shape `sense()`'s own moment strings
# always take) by showing that thing again, byte-identical (`make()` is pure), with a FRESH `total` so the
# schedule's own `window`/`i` sequence is never consumed or perturbed (the advisor's own reading, taken).
# Never writes to root/ask/in or touches the mind's memory -- only reads root/ask/out/q-*.json and renames
# them (G4-1's writer sweep: `Path.rename` is not in WRITE_METHODS, and this stays a READ of a file the
# mind wrote, matching the folder door's own "a sense may read files" law).
_QUESTION_MOMENT_RE = re.compile(r"w(\d{4})i(\d{6})t(\d{9})")


def _answer_one_question(publish: Callable, root: Path, seed: int, total: int) -> Optional[int]:
    """Answers the FIRST unanswered `what-is` in `root/ask/out/q-*.json` whose `args[0]` names a canvas
    this door drew, by publishing that thing again under a moment carrying the SAME (window, i) but a
    FRESH `total`; renames the question file `<qid>.answered.json`. A question this door cannot answer (no
    "w..." moment — a folder picture, a game frame — or a malformed row) is left exactly as it found it;
    PARK's own `reopen on new-sense` is its consumer, never this function. Returns the NEXT `total` to use
    if it answered one (the caller's own counter, advanced by exactly one canvas), else None."""
    ask_out = root / "ask" / "out"
    if not ask_out.exists():
        return None
    # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:4x +0400 — the glob "q-*.json" ALSO matches an
    # already-renamed "q-<n>.answered.json" (the `*` wildcard swallows ".answered"), which would re-answer
    # (and re-rename to "...answered.answered.json") a question this function already finished with on the
    # very next tick -- caught by this file's own live test, not by inspection. Filtered out explicitly.
    for qpath in sorted(p for p in ask_out.glob("q-*.json") if not p.name.endswith(".answered.json")):
        try:
            req = json.loads(qpath.read_text())
        except (json.JSONDecodeError, OSError):
            continue   # a row read mid-write (rare, atomic-write races aside) -- retried next tick, never fatal
        if req.get("q") != "what-is":
            continue
        args = req.get("args") or []
        if not args:
            continue
        m = _QUESTION_MOMENT_RE.fullmatch(str(args[0]))
        if not m:
            continue
        w_orig, i_orig = int(m.group(1)), int(m.group(2))
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:2x +0400 — a discovered off-by-one in
        # sense()'s own moment-string line, verified against a live tape (world_maker.make(seed, 0, 0) ==
        # "circle" but the FIRST recorded moment reads "w0000i000001..."): `moment = f"...i{i:06d}..."`
        # below is built AFTER the regular branch's `i += 1`, so a recorded moment's `i` field is always
        # ONE MORE than the `i` that was actually passed to `make()`. Never "fixed" here (the recorded
        # tape's own moment strings, already durable, keep their existing meaning; changing the encoding
        # would be a global format change far outside this brief) — this door simply undoes it before
        # recomputing: `i_orig - 1` is the `i` `make()` actually saw. RAISED in the report as a latent
        # defect in the pre-existing (unpinned) moment-string line, found by this task, not caused by it.
        i_used = max(0, i_orig - 1)
        qid = qpath.stem
        thing, rgb, truth = make(seed, w_orig, i_used)
        moment = f"w{w_orig:04d}i{i_orig:06d}t{total:09d}"
        _publish_canvas(publish, root, moment, thing, rgb, truth, answering=qid)
        qpath.rename(qpath.with_name(f"{qid}.answered.json"))
        return total + 1
    return None


def sense(publish: Callable, stop_event, root: Path, period: float = 5.0, seed: int = DEFAULT_SEED,
          plant_after_canvases: int = PLANT_AFTER_CANVASES, plant_window_s: float = PLANT_WINDOW_S,
          plant_showings: int = PLANT_SHOWINGS, window_seconds: float = WINDOW_SECONDS) -> None:
    """The world-maker sense thread body: one canvas every `period` s, forever, until `stop_event`. The
    plant (THING_PLANT) shows `plant_showings` times, evenly spaced, in the `plant_window_s` seconds
    after the `plant_after_canvases`-th canvas; THING_NULL and THING_NEVER are never shown (schedule()
    never names them, and the plant path only ever substitutes THING_PLANT). `window_seconds`: how long a
    window stays open before `window` increments (default WINDOW_SECONDS, 6 h -- C1.3, W3-0b: WORLD's
    declared `arrivals every <h> h` becomes this DEFAULT only; `schedule()`/`make()` themselves take the
    integer `window` they are given either way, so the PIN (test_world_pin.py) is untouched)."""
    window = 0
    i = 0
    total = 0
    window_start = time.monotonic()
    plant_deadline = None
    plant_next_at = None
    plant_interval = plant_window_s / plant_showings if plant_showings else None
    plant_shown = 0

    while not stop_event.is_set():
        now = time.monotonic()
        if now - window_start >= window_seconds:
            window += 1
            window_start = now
            i = 0

        # L-10 (QUESTION): answer at most one pending what-is per tick, BEFORE this tick's own regular
        # canvas -- an EXTRA showing, never a substitute (the schedule's own (window, i) sequence below is
        # completely untouched by this branch: `total` is the only counter it advances).
        answered_total = _answer_one_question(publish, root, seed, total)
        if answered_total is not None:
            total = answered_total

        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught: `_answer_one_
        # question` above can advance `total` by one BEFORE this check runs (an answered question inserts
        # an EXTRA canvas), so a tick that entered with total == plant_after_canvases can reach here with
        # total == plant_after_canvases + 1, and the exact `==` would then never fire -- the whole plant
        # (zog, the life's (vi') mark) silently skipped. `>=` (still guarded by `plant_deadline is None`,
        # so it still arms exactly once) is behaviour-identical to `==` whenever no question answer lands
        # on that exact tick, and safe whenever one does.
        if total >= plant_after_canvases and plant_deadline is None:
            plant_deadline = now + plant_window_s
            plant_next_at = now

        show_plant = (plant_deadline is not None and now < plant_deadline and plant_shown < plant_showings
                      and plant_next_at is not None and now >= plant_next_at)
        if show_plant:
            rng = np.random.default_rng([int(seed), _PLANT_MARKER, int(plant_shown)])
            rgb, truth = world.render_canvas(world.THING_PLANT, rng)
            thing = world.THING_PLANT
            plant_shown += 1
            plant_next_at += plant_interval
        else:
            thing, rgb, truth = make(seed, window, i)
            i += 1

        moment = f"w{window:04d}i{i:06d}t{total:09d}"
        _publish_canvas(publish, root, moment, thing, rgb, truth)
        total += 1
        stop_event.wait(period)
