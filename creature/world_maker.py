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
import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple

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


def _publish_canvas(publish: Callable, root: Path, moment: str, thing: str, rgb: np.ndarray, truth: Dict[str, object]) -> None:
    """ear (word bytes) THEN eye (PNG) — the tape order law (§2.2) — then the truth file, keyed by the
    EYE row's own seq, under root/truth/ (never on the tape, §2.1)."""
    publish("ear", thing.encode("utf-8"), {"moment": moment, "source": "maker", "word": thing}, "txt")
    eye_row = publish("eye", _png_bytes(rgb), {"moment": moment, "source": "maker"}, "png")
    truth_dir = root / "truth"
    truth_dir.mkdir(parents=True, exist_ok=True)
    (truth_dir / f"{eye_row['seq']:09d}.json").write_text(json.dumps(truth))


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

        if total == plant_after_canvases and plant_deadline is None:
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
