# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:2x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1.
"""creature/senses/game.py — the BabyAI door sense.

Launches `tools/game_worker_babyai.py` as a SUBPROCESS under the game-worlds venv's own python3
(gymnasium/minigrid are not installed for the SYSTEM python this creature itself runs on, and the venv
does not hold this tree -- docs/briefs/G5-G-GAME-WORLDS.md §6's own install road), then watches
`--door-dir` for the worker's own manifests (`step-NNNNNNNNN.json` + `.png`, written atomically -- the
worker's own doc). Every manifest publishes rows in the tape's own order law (PREREG §2.2, the SAME order
`creature/senses/folder.py` and `creature/world_maker.py` already use -- ear before eye):

  1. ear  (the mission's target-object word)                        -- always
  2. eye  (the frame, through gaze.canvas_of_picture -- the SAME     -- always
           road the folder door uses for a picture: folder.py:102)
  3. outcome (the act that PRODUCED this frame + its reward)         -- every manifest but the reset frame
     (the very first manifest of an episode carries no act -- nothing produced it, it is what `env.reset`
     handed back -- so no outcome row is published for it)

`outcome` is published under that sense NAME, carrying K's own OUTCOME row shape (docs/briefs/
G5-K-ACTS-OUTCOME-SIT-BODY.md item 2: fields `act` (str), `expected` (float|null), `got` (float),
`residual` (float|null), `source` (str)) as BOTH the JSON payload and `meta` -- because K's OUTCOME gene
is not merged onto this branch (a sibling worktree, g5-acts), so there is no `genome.declared["OUTCOME"]`
for a parser to gate on; this is said here, not worked around. `creature/mind.py:consume` reads only
"ear"/"eye" senses today and falls through everything else untouched ("a door row ... carries no organism
work here" -- its own comment), so an "outcome" row is harmless dead weight on this branch: durable on the
tape, replayable, and ready for K's consumer the day it lands.

The creature's own act: no ACT gene exists on this branch to choose it (K's, unmerged) -- so the WORKER
process chooses it, from a SEEDED schedule (never a live mind decision), and every outcome row says so in
its own meta: `chosen_by: "schedule"`, `road: "no road"` -- the brief's own phrase (item 1: "a scheduled
random act, journaled <<no road>>").

REPLAY: every frame/mission/reward this sense ever published is a RECORDED tape row (payload files under
the tape's own payload/ dir, JSON meta on the row) -- `creature.replay` reads the tape, never re-invokes a
sense, so the game is NEVER re-run at replay (MOTOR Q1's recommendation, adopted here structurally: there
is no code path from replay back into this module at all).

A pure SENSE (G4-1's writer sweep): never touches state/journal/memory, never imports Organism/machinery.
Its cursor (`root/game/CURSOR`) is written only AFTER a manifest's rows are durable on the tape (#230).
"""
from __future__ import annotations

import io
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

from genome import gaze

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists; --game-door stays an explicit override for tests regardless of this constant.
GAME_DOOR_GATED = True

VENV_PYTHON = "/data/dev/game-worlds/venv/bin/python3"
WORKER_SCRIPT = str(Path(__file__).resolve().parents[2] / "tools" / "game_worker_babyai.py")
ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]   # game_worker_babyai.py's own order, verbatim


def _png_bytes(rgb) -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:37 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8): the
# ONE gate creature/body.py:main reads before passing --act-file to the worker, and creature/mind.py reads
# before it ever writes root/game/ACT -- a single source of truth so the two can never disagree (#180: a
# fact computed independently in two places is two features sharing one name, not one). True when this
# genome's ACT vocabulary carries BOTH "turn" and "step" (the plan's own phrase, §4 L-8: "ACT ... turn
# step" declared together with WORLD game).
def mind_drives_acts(declared: Dict[str, dict]) -> bool:
    verbs = set((declared.get("ACT") or {}).get("verbs") or [])
    return {"turn", "step"} <= verbs


def target_word(mission: str) -> str:
    """The mission's single decision-critical word: its LAST token -- the object noun (ball/key/box) in
    every GoToLocal mission ("go to a/the <colour> <object>"). RAISED in the builder report: the full
    multi-word mission cannot fit the creature's ONE-word-per-moment ear channel (SENSE ear letters 8: one
    `word` binds to one `moment`, and mind.py's `self.pending[moment] = word` keeps only the LAST ear row
    published before a moment's eye row) without a machinery change nobody has built (Builder I's DELIVER/
    MOMENT seam, a sibling worktree, does not touch this). This is the smallest honest choice, not a
    work-around: it is still the token `MEET sight words` was designed to bind, and the FULL mission
    survives losslessly in `meta["mission"]` on the same tape row, so nothing is discarded from the
    record -- only from what reaches the organism's word channel today."""
    return mission.strip().split()[-1]


def start_worker(door_dir: Path, seed: int, game: str = "babyai-gotolocal", tile: int = 32,
                  period_s: float = 0.0, steps: int = 0, python: str = VENV_PYTHON,
                  stop_file: Optional[Path] = None, act_file: Optional[Path] = None) -> "subprocess.Popen[bytes]":
    """`act_file` (L-8): forwarded as `--act-file` when given -- creature/body.py:main passes this only
    when `mind_drives_acts(declared)` is true, the same gate above; absent (the common case until a
    genome declares ACT's turn/step verbs), the worker keeps its own seeded schedule, unchanged."""
    door_dir = Path(door_dir)
    door_dir.mkdir(parents=True, exist_ok=True)
    argv = [python, WORKER_SCRIPT, "--game", game, "--door-dir", str(door_dir), "--seed", str(seed),
            "--tile", str(tile), "--period-s", str(period_s), "--steps", str(steps)]
    if stop_file is not None:
        argv += ["--stop-file", str(stop_file)]
    if act_file is not None:
        argv += ["--act-file", str(act_file)]
    return subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_worker(proc: "subprocess.Popen[bytes]", stop_file: Optional[Path] = None, timeout: float = 5.0) -> None:
    """Kill by the PID this module itself holds (`proc`) -- never `pkill -f` a pattern the caller's own
    command line might carry (#193/#197). `stop_file`, if given, is written first so the worker's own
    step loop notices and exits its `while` cleanly (the SIGTERM below is the fallback, not the plan)."""
    if proc.poll() is not None:
        return
    if stop_file is not None:
        try:
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


def _read_manifest(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None   # a manifest read mid-rename should not happen (os.replace is atomic) -- treated as
                       # "not yet there", never fatal; the next scan retries the same step index


def sense(publish: Callable, stop_event, door_dir: Path, root: Path, canvas: int = 128,
          poll_period: float = 0.5) -> None:
    """The sense thread body a `creature.body.SenseThread` runs. `door_dir`: where the worker (started
    separately -- see `start_worker`, called by `creature/body.py:main`, NOT by this function -- a sense
    function's only job is publishing, matching every other sense here) writes its manifests. Reads
    manifests in step order (the filename's own zero-padded index sorts bytewise == numeric order, exactly
    like the folder door's (folder, filename) bytewise order), publishing ear+eye (+outcome) for every
    manifest not yet past the cursor, then persisting the cursor -- the cursor law (#230)."""
    door_dir = Path(door_dir)
    cursor_path = Path(root) / "game" / "CURSOR"
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    last_done = _load_cursor(cursor_path)

    while not stop_event.is_set():
        advanced = False
        for man_path in sorted(door_dir.glob("step-*.json")):
            try:
                step_idx = int(man_path.stem.split("-")[1])
            except (IndexError, ValueError):
                continue
            if step_idx <= last_done:
                continue
            data = _read_manifest(man_path)
            if data is None:
                break   # not durable yet -- stop this scan, retry next period (order preserved)
            png_path = man_path.parent / data["frame"]
            if not png_path.exists():
                break
            try:
                rgb = gaze.canvas_of_picture(png_path, canvas)
            except Exception:
                break   # an unreadable/partial PNG (a rename race the atomic write should prevent, but
                        # never fatal to the sense thread -- SenseThread's own restart law covers a real crash)

            mission = data["mission"]
            word = target_word(mission)
            moment = f"g{str(data['game'])[:4]}{int(data['seed']):08d}s{step_idx:09d}"
            common = {"game": data["game"], "episode": data["episode"], "step": step_idx}
            # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:37 +0400 — LIFE-D-ACT-SOUND.md item 1
            # (L-8): the worker's own manifest, never hardcoded -- absent (a manifest from before this
            # change) falls back to the module's own ACT_NAMES/7, byte-identical to before.
            n_actions = int(data["n_actions"]) if data.get("n_actions") is not None else len(ACT_NAMES)
            act_names = data.get("act_names") or ACT_NAMES

            publish("ear", word.encode("utf-8"),
                    {"moment": moment, "source": "game", "word": word, "mission": mission, **common}, "txt")
            publish("eye", _png_bytes(rgb),
                    {"moment": moment, "source": "game", "n_actions": n_actions, "act_names": act_names, **common}, "png")

            act = data.get("act")
            if act is not None:
                act_i = int(act)
                act_name = act_names[act_i] if 0 <= act_i < len(act_names) else str(act_i)
                got = float(data["reward"])
                # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:37 +0400 — LIFE-D-ACT-SOUND.md item 1
                # (L-8): chosen_by/act_seq read straight off the worker's own manifest -- "schedule"/None
                # when absent (every manifest before this change, and every --act-file-less run since),
                # byte-identical to the old hardcoded values (test_game_door.py's own pin).
                chosen_by = data.get("chosen_by") or "schedule"
                act_seq = data.get("act_seq")
                road = "mind" if chosen_by == "mind" else "no road"
                payload = json.dumps({"act": act_name, "expected": None, "got": got, "residual": None,
                                       "source": "game"}).encode("utf-8")
                publish("outcome",
                        payload,
                        {"moment": moment, "source": "game", "act": act_name, "act_idx": act_i, "expected": None,
                         "got": got, "residual": None, "chosen_by": chosen_by, "road": road, "act_seq": act_seq,
                         "terminated": bool(data.get("terminated")), "truncated": bool(data.get("truncated")),
                         **common}, "json")

            last_done = step_idx
            cursor_path.write_text(str(last_done))   # AFTER the row(s) are durable -- the cursor law (#230)
            advanced = True
        if not advanced:
            stop_event.wait(poll_period)
