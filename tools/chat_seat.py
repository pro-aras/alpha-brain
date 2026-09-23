#!/usr/bin/env python3
# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:43 +0400 — A4L-LANG task 6 (docs/briefs/A4L-LANG.md;
# docs/A4-LADDER-PREREG.md §3.3): THE SEAT'S SIDE OF THE CHAT DOOR. It never imports the mind: it writes questions (and
# their truth, BEFORE the question) under $ROOT/chat/, and grades. The creature answers through creature/senses/chat.py.
"""tools/chat_seat.py — the answering experiments' question writer (the orchestrator runs it by a waiter).

  --root R --schedule --phrasings FILE   from hour 1 to hour 8, ONE family question every 120 s in the 7-slot cycle
                                         (what-is, yes-no, which, what-is, yes-no, which, where) → 60/60/60/30; the
                                         things from the world's own schedule (creature/world_maker.schedule: window 0's
                                         eleven from hour 1, window 1's five arrivals from hour 5 — the PREREG's
                                         «window 1 / window 2», counted from 1); the pictures held-out renders on seed 3
                                         (default_rng([3, k])), two-thing composites for where; one what-is in ten on a
                                         never-seen thing (spiral, vex alternating). Resumable: a slot already written
                                         is never rewritten. The birth time is $ROOT/STARTED-AT (or --born).
  --root R --burst N --phrasings FILE [--from-min 12 --to-min 16]   the pre-flight's positive control: N what-is
                                         questions on the eleven, evenly between two minutes of the life.
  --root R --say "TEXT"                  a free line (no picture: the canvas is the line itself).
  --root R --grade ID --right|--wrong [--novel]   the seat's grade (chat/graded/<ID>.json — the grade sense's shape).
  --root R --show                        every answer so far, rendered by the DOOR (creature/senses/chat.py).
Deterministic from --seed (the seat's own draws) and --world-seed (the maker's schedule; world_maker.DEFAULT_SEED —
creature/body.py never passes the genome's SEED to the maker). The TEST phrasings file is the orchestrator's; this
script reads whatever --phrasings names and never opens anything else.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from creature import world_maker                     # noqa: E402  (the world's own schedule; imports genome.world only)
from creature.senses import chat as chat_door         # noqa: E402  (the door's own rendering of an answer)
from genome import world                               # noqa: E402

CYCLE = ("what-is", "yes-no", "which", "what-is", "yes-no", "which", "where")
FAMILIES = ("what-is", "yes-no", "which", "where")
NULL_THINGS = ("spiral", "vex")
PICTURE_SEED = 3                  # the exam's held-out renders use 2; the chat's use 3 (§3.3)
WINDOW2_FROM_HOUR = 5.0           # the five arrivals of window 1 (hour 4) are asked from hour 5 (≥ 1 h after their arrival)
BURST_OFFSET = 10000              # the burst's picture streams [3, 10000 + i] never meet the schedule's [3, k]


# ============================================================================ pure: phrasings, things, plans, pictures
def load_phrasings(path) -> Dict[str, List[str]]:
    """{family: [phrasing, …]} from a JSON object (keys starting with '_' ignored); every family must be present with at
    least one phrasing, or the file is refused whole."""
    raw = json.loads(Path(path).read_text())
    out = {k: [str(x) for x in v] for k, v in raw.items() if not str(k).startswith("_")}
    missing = [f for f in FAMILIES if not out.get(f)]
    if missing:
        raise ValueError(f"phrasings {path}: missing or empty families {missing}")
    return {f: out[f] for f in FAMILIES}


def fill(phrasing: str, x: str, y: Optional[str] = None) -> str:
    return phrasing.replace("{X}", x).replace("{Y}", y if y is not None else "")


def things_at(hour: float, world_seed: int = world_maker.DEFAULT_SEED) -> List[str]:
    """The things the question may name at `hour` of the life: window 0's eleven, and from WINDOW2_FROM_HOUR the new
    things of window 1 (its arrivals — world_maker.schedule's own lists, never the creature's)."""
    w0 = list(world_maker.schedule(world_seed, 0))
    if hour < WINDOW2_FROM_HOUR:
        return w0
    return w0 + [t for t in world_maker.schedule(world_seed, 1) if t not in w0]


def render_two(a: str, b: str, rng: np.random.Generator, canvas: int = world.CANVAS, side: int = world.THING_SIDE) -> Tuple[np.ndarray, Dict[str, List[int]]]:
    """Two things on one canvas, each by the maker's own renderer (world.render at side 32), placed without overlap,
    with the maker's three faint strokes and its noise (world.render_canvas's own recipe); returns (rgb, {thing: [top,
    left, h, w]}). The WHERE ceiling of task 0 (b) was measured on this very composite (0.84 on the 10:54 copy)."""
    pics = [world.render(a, rng, side), world.render(b, rng, side)]
    while True:
        ta, la, tb, lb = (int(v) for v in rng.integers(0, canvas - side + 1, size=4))
        if ta + side <= tb or tb + side <= ta or la + side <= lb or lb + side <= la:
            break
    cv = np.zeros((canvas, canvas), dtype=np.float64)
    for pic, (t, l) in zip(pics, ((ta, la), (tb, lb))):
        cv[t:t + side, l:l + side] = np.maximum(cv[t:t + side, l:l + side], pic)
    layer = Image.new("L", (canvas, canvas), 0); d = ImageDraw.Draw(layer)
    for _ in range(world.CLUTTER_STROKES):
        x0, y0 = rng.uniform(0, canvas, size=2); ang = rng.uniform(0, math.pi); ln = rng.uniform(8, 16)
        d.line([(x0, y0), (x0 + ln * math.cos(ang), y0 + ln * math.sin(ang))], fill=255, width=1)
    cv = np.maximum(cv, np.asarray(layer, dtype=np.float64) / 255.0 * world.CLUTTER_INK)
    cv = np.clip(cv + rng.normal(0.0, 0.05, size=cv.shape), 0.0, 1.0)
    u8 = np.clip(np.rint(cv * 255.0), 0, 255).astype(np.uint8)
    return np.repeat(u8[:, :, None], 3, axis=2), {a: [ta, la, side, side], b: [tb, lb, side, side]}


def _whatis_index(k: int) -> int:
    """The what-is questions' own running index at slot k (two per 7-slot cycle, at positions 0 and 3)."""
    return 2 * (k // 7) + (0 if (k % 7) == 0 else 1)


def plan_slot(k: int, seed: int, phrasings: Dict[str, List[str]], hour: float, world_seed: int = world_maker.DEFAULT_SEED) -> Dict[str, object]:
    """Slot k of the schedule: its family (the 7-slot cycle), thing, lure/options/bboxes, phrasing, text and picture —
    a pure function of (k, seed, phrasings, the hour's pool)."""
    family = CYCLE[k % 7]
    rng = np.random.default_rng([int(seed), int(k)])
    pool = things_at(hour, world_seed)
    thing = pool[int(rng.integers(0, len(pool)))]
    others = [t for t in pool if t != thing]
    other = others[int(rng.integers(0, len(others)))]
    phr = phrasings[family][int(rng.integers(0, len(phrasings[family])))]
    prng = np.random.default_rng([PICTURE_SEED, int(k)])
    plan: Dict[str, object] = {"id": f"c{k:04d}", "k": int(k), "family": family, "hour": round(float(hour), 4),
                               "phrasing": phr, "lure": None, "options": [], "bboxes": {}, "other": None}
    if family == "what-is":
        j = _whatis_index(k)
        if j % 10 == 9:
            thing = NULL_THINGS[(j // 10) % 2]
        plan["picture"], truth = world.render_canvas(thing, prng)
        plan["bboxes"] = {thing: [int(truth["top"]), int(truth["left"]), world.THING_SIDE, world.THING_SIDE]}
        plan["text"] = fill(phr, thing)
    elif family == "yes-no":
        lure = thing if float(rng.random()) < 0.5 else other
        plan["picture"], truth = world.render_canvas(thing, prng)
        plan["bboxes"] = {thing: [int(truth["top"]), int(truth["left"]), world.THING_SIDE, world.THING_SIDE]}
        plan.update(lure=lure, options=[lure], text=fill(phr, lure))
    elif family == "which":
        opts = [thing, other] if float(rng.random()) < 0.5 else [other, thing]
        plan["picture"], truth = world.render_canvas(thing, prng)
        plan["bboxes"] = {thing: [int(truth["top"]), int(truth["left"]), world.THING_SIDE, world.THING_SIDE]}
        plan.update(options=opts, other=other, text=fill(phr, opts[0], opts[1]))
    else:   # where
        plan["picture"], plan["bboxes"] = render_two(thing, other, prng)
        plan.update(other=other, options=[thing], text=fill(phr, thing))
    plan["thing"] = thing
    return plan


def n_slots(from_hour: float, to_hour: float, every_s: float) -> int:
    return int(round((to_hour - from_hour) * 3600.0 / every_s))


def slot_due(born: datetime, k: int, from_hour: float, every_s: float) -> datetime:
    return born + timedelta(hours=from_hour) + timedelta(seconds=every_s * k)


def burst_plans(n: int, seed: int, phrasings: Dict[str, List[str]], born: datetime, from_min: float = 12.0,
                to_min: float = 16.0, world_seed: int = world_maker.DEFAULT_SEED) -> List[Dict[str, object]]:
    """The pre-flight's positive control (§3.4): `n` what-is questions (the FIRST what-is phrasing of the file — the DEV
    file's «what is this»), each on one of window 0's eleven, evenly between `from_min` and `to_min` of the life."""
    pool = things_at(0.0, world_seed)
    out: List[Dict[str, object]] = []
    for i in range(n):
        rng = np.random.default_rng([int(seed), BURST_OFFSET + i])
        thing = pool[int(rng.integers(0, len(pool)))]
        rgb, truth = world.render_canvas(thing, np.random.default_rng([PICTURE_SEED, BURST_OFFSET + i]))
        phr = phrasings["what-is"][0]
        due = born + timedelta(minutes=from_min + (to_min - from_min) * (i / (n - 1) if n > 1 else 0.0))
        out.append({"id": f"p{i + 1:04d}", "k": BURST_OFFSET + i, "family": "what-is", "thing": thing, "lure": None,
                    "options": [], "other": None, "phrasing": phr, "text": fill(phr, thing), "picture": rgb,
                    "bboxes": {thing: [int(truth["top"]), int(truth["left"]), world.THING_SIDE, world.THING_SIDE]},
                    "due": due, "hour": round((due - born).total_seconds() / 3600.0, 4)})
    return out


# ============================================================================ the writes (the seat's own files only)
def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(b, format="PNG"); return b.getvalue()


def _atomic_write(path, data: bytes) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(str(tmp), str(path))


def write_chat(root: Path, plan: Dict[str, object]) -> bool:
    """The truth FIRST (chat/truth/<id>.json), then the picture (chat/pics/<id>.png), then the chat (chat/in/<id>.json
    {id, text, picture?}) — the chat never carries its truth. False (nothing written) when the chat already exists."""
    root = Path(root); cid = str(plan["id"])
    chat_path = root / "chat" / "in" / f"{cid}.json"
    if chat_path.exists():
        return False
    truth = {"id": cid, "family": plan["family"], "thing": plan.get("thing"), "lure": plan.get("lure"),
             "options": plan.get("options") or [], "other": plan.get("other"), "bboxes": plan.get("bboxes") or {},
             "phrasing": plan.get("phrasing"), "text": plan.get("text"), "k": plan.get("k"), "hour": plan.get("hour")}
    _atomic_write(root / "chat" / "truth" / f"{cid}.json", json.dumps(truth).encode())
    msg: Dict[str, object] = {"id": cid, "text": plan["text"]}
    if plan.get("picture") is not None:
        _atomic_write(root / "chat" / "pics" / f"{cid}.png", _png(np.asarray(plan["picture"], dtype=np.uint8)))
        msg["picture"] = f"{cid}.png"
    _atomic_write(chat_path, json.dumps(msg).encode())
    return True


def _next_free_id(root: Path, prefix: str) -> str:
    used = {p.stem for d in ("in", "truth") for p in (Path(root) / "chat" / d).glob(f"{prefix}*.json")}
    n = 1
    while f"{prefix}{n:04d}" in used:
        n += 1
    return f"{prefix}{n:04d}"


def say(root: Path, text: str) -> str:
    """A free line: no picture (the canvas is the line itself), its truth the family «free» and the text."""
    cid = _next_free_id(Path(root), "s")
    write_chat(Path(root), {"id": cid, "family": "free", "text": str(text), "phrasing": str(text), "picture": None})
    return cid


def grade(root: Path, cid: str, right: bool, novel: bool) -> Path:
    p = Path(root) / "chat" / "graded" / f"{cid}.json"
    _atomic_write(p, json.dumps({"id": str(cid), "right": bool(right), "novel": bool(novel)}).encode())
    return p


def born_of(root: Path) -> datetime:
    """The life's birth: $ROOT/STARTED-AT (tools/lives/launch.sh writes `date "+%Y-%m-%d %H:%M %z"`), as UTC."""
    s = (Path(root) / "STARTED-AT").read_text().strip()
    return datetime.strptime(s, "%Y-%m-%d %H:%M %z").astimezone(timezone.utc)


def _wait_until(due: datetime, stop_file: Optional[Path]) -> bool:
    while True:
        if stop_file is not None and stop_file.exists():
            return False
        now = datetime.now(timezone.utc)
        if now >= due:
            return True
        time.sleep(min(5.0, (due - now).total_seconds()))


# ============================================================================ CLI
def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--phrasings")
    ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--world-seed", type=int, default=world_maker.DEFAULT_SEED)
    ap.add_argument("--born", help='the life\'s birth, "%%Y-%%m-%%d %%H:%%M %%z" (default: $ROOT/STARTED-AT)')
    ap.add_argument("--schedule", action="store_true")
    ap.add_argument("--every", type=float, default=120.0)
    ap.add_argument("--from-hour", type=float, default=1.0)
    ap.add_argument("--to-hour", type=float, default=8.0)
    ap.add_argument("--burst", type=int)
    ap.add_argument("--from-min", type=float, default=12.0)
    ap.add_argument("--to-min", type=float, default=16.0)
    ap.add_argument("--say")
    ap.add_argument("--grade"); ap.add_argument("--right", action="store_true"); ap.add_argument("--wrong", action="store_true")
    ap.add_argument("--novel", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args(list(argv))
    root = Path(a.root)
    stop_file = root / "chat" / "SEAT-STOP"
    if a.say is not None:
        print(say(root, a.say)); return 0
    if a.grade is not None:
        if a.right == a.wrong:
            ap.error("--grade needs exactly one of --right / --wrong")
        print(grade(root, a.grade, right=a.right, novel=a.novel)); return 0
    if a.show:
        for p in sorted((root / "chat" / "out").glob("*.json")):
            out = json.loads(p.read_text())
            print(f"{out.get('id')}: {' '.join(out.get('heard') or [])} → {chat_door.render_answer(out)}")
        return 0
    born = (datetime.strptime(a.born, "%Y-%m-%d %H:%M %z").astimezone(timezone.utc) if a.born else born_of(root))
    if not a.phrasings:
        ap.error("--schedule/--burst need --phrasings FILE")
    P = load_phrasings(a.phrasings)
    if a.burst:
        for plan in burst_plans(int(a.burst), a.seed, P, born, a.from_min, a.to_min, a.world_seed):
            if not _wait_until(plan["due"], stop_file):
                return 0
            if write_chat(root, plan):
                print(f"[seat] {plan['id']} {plan['family']} «{plan['text']}» at {datetime.now(timezone.utc).isoformat(timespec='seconds')}", flush=True)
        return 0
    if a.schedule:
        for k in range(n_slots(a.from_hour, a.to_hour, a.every)):
            due = slot_due(born, k, a.from_hour, a.every)
            if (root / "chat" / "in" / f"c{k:04d}.json").exists():
                continue                                   # resumable: a slot already written is never rewritten
            if datetime.now(timezone.utc) > due + timedelta(seconds=a.every):
                continue                                   # a slot missed while the seat was down is skipped, never bunched
            if not _wait_until(due, stop_file):
                return 0
            hour = (due - born).total_seconds() / 3600.0
            plan = plan_slot(k, a.seed, P, hour, a.world_seed)
            if write_chat(root, plan):
                print(f"[seat] {plan['id']} h{hour:.2f} {plan['family']} «{plan['text']}»", flush=True)
        return 0
    ap.error("one of --schedule / --burst / --say / --grade / --show")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
