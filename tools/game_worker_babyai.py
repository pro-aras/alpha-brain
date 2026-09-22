# edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:2x +0400 — docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 1.
"""tools/game_worker_babyai.py — the BabyAI world PROCESS.

Runs under /data/dev/game-worlds/venv's own python3 ONLY: gymnasium + minigrid are installed there and
NOWHERE else on this box (the creature itself runs on the system python3, which has neither, and the venv
holds none of this tree -- G5-G's own install road, docs/briefs/G5-G-GAME-WORLDS.md §6). Launched as a
SUBPROCESS by creature/senses/game.py (the system-python door sense that reads what this script writes);
never imported by anything under creature/ or genome/.

Writes one manifest JSON + one PNG per step into --door-dir, EACH atomically (a .tmp file written then
os.replace'd into place -- never a partial file visible to a concurrent reader), the PNG durable BEFORE
its manifest is renamed into place (the tape's own payload-before-row law, creature/tape.py, applied here
one layer earlier). The door sense's cursor (root/game/CURSOR) is written only after it has read a
manifest whose PNG already exists -- SOLUTIONS #230's crash-loop lesson (a persisted cursor advances only
after the thing it names is durable).

DETERMINISTIC: every action is drawn from ONE seeded rng, np.random.default_rng([seed, "game" bytes]),
NEVER the environment's own internal rng for action choice (env.action_space.sample() reads from a
DIFFERENT, gym-managed generator and would not reproduce identically run to run) -- so two runs started
with the same --seed produce a byte-identical stream of frames + missions + rewards + acts. This IS the
frame-identity proof the brief asks for (docs/briefs/G5-L-BABYAI-WORLD-EAR.md item 3): compare two
--door-dir outputs from two separate processes, byte for byte, exactly as G5-G's REPORT-G5-G.md §2 "Stage
3" compares two Atari/MiniGrid processes (its own §7 finding #7: same-PROCESS agreement proves nothing --
two SEPARATE processes are the only real test).

`ACT_NAMES` and the 7-action space match G5-G's own harvest.py comment verbatim ("7: left,right,forward,
pickup,drop,toggle,done") and its null measurement (uniform over ALL 7 acts, not just navigation) -- so
this worker's own null, measured the same way, reproduces REPORT-G5-G.md's 0.29 / 0.1464 numbers (§4.1).

The creature's own act: K's ACT vocabulary (`turn`/`step`) is not wired on this branch (G5-K, a sibling
worktree). Until it lands, THIS SCRIPT chooses the action -- a scheduled, seeded, deterministic choice,
never the mind's -- and creature/senses/game.py records that plainly on every outcome row
(`chosen_by: "schedule"`, `road: "no road"`), the brief's own phrase for "no ACT gene exists yet to
choose this act instead."
"""
# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:36 +0400 — LIFE-D-ACT-SOUND.md item 1 (L-8; the
# plan's §4 L-8, MOTOR-HANDS.md G-MOT-1/G-MOT-4's "replay problem, named"): `--act-file <path>`. When
# given, the worker no longer draws its own act -- it WAITS (poll 50 ms, no timeout: the game pauses
# while the creature decides, and that is the consequence, not a bug to work around) for `<path>` to
# carry a JSON `{"seq": <int>, "act": <int>, "at": ...}` whose "seq" is strictly newer than the one it
# last consumed, steps that act, and tags the manifest `chosen_by: "mind"` + `act_seq: <the seq it
# obeyed>`. The read cursor is persisted at `<door_dir>/ACT_CURSOR` (#230: a persisted cursor advances
# ONLY AFTER the manifest naming the act it read is durable -- write_step's own atomic png-then-json
# order, one layer up). Without --act-file, the old seeded schedule is BYTE-IDENTICAL to before
# (chosen_by "schedule", no act_seq key) -- test_game_act_file.py's own regression clause.
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

GAME_IDS = {"babyai-gotolocal": "BabyAI-GoToLocal-v0"}
ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]   # G5-G REPORT-G5-G.md §1 table, verbatim order
ACT_FILE_POLL_S = 0.05


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _read_act_file(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None   # absent, or a rename race (write-then-replace should prevent a torn read) -- "nothing new yet", never fatal


def _load_act_cursor(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        t = path.read_text().strip()
        return int(t) if t else -1
    except (OSError, ValueError):
        return -1


def _wait_for_act(act_file: Path, last_seq: int, stop_path: Optional[Path]) -> Optional[dict]:
    """Blocks (poll ACT_FILE_POLL_S, NO timeout — the brief's own law) until `act_file` carries a "seq"
    strictly greater than `last_seq`, or `stop_path` appears (a clean shutdown mid-wait) -> None."""
    while True:
        if stop_path is not None and stop_path.exists():
            return None
        data = _read_act_file(act_file)
        if data is not None:
            try:
                seq = int(data["seq"])
            except (KeyError, TypeError, ValueError):
                seq = None
            if seq is not None and seq > last_seq:
                return data
        time.sleep(ACT_FILE_POLL_S)


def _png_bytes(rgb: np.ndarray) -> bytes:
    import io
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def run(game: str, door_dir: Path, seed: int, tile: int = 32, steps: int = 0, period_s: float = 0.0,
        stop_path: Optional[Path] = None, act_file: Optional[Path] = None) -> int:
    """`steps<=0` -> run until `stop_path` exists (creature/senses/game.py writes it on shutdown) or,
    with no stop_path given (a bare CLI run), forever. Returns the total number of manifests written.
    `act_file`: L-8 -- given, the mind chooses every act after the reset frame (`--act-file`'s own
    docstring above); absent, the old seeded `act_rng` schedule, unchanged."""
    import gymnasium as gym
    import minigrid  # noqa: F401  -- registers the BabyAI/MiniGrid env ids

    door_dir = Path(door_dir)
    door_dir.mkdir(parents=True, exist_ok=True)
    env_id = GAME_IDS[game]
    env = gym.make(env_id, render_mode="rgb_array")
    base = env.unwrapped
    act_rng = np.random.default_rng([int(seed), 0x67616D65])   # "game" bytes-ish; its own stream, never env's own rng
    n_actions = int(env.action_space.n)   # published on every manifest -- L-8: "never hardcode 7"

    act_cursor_path = door_dir / "ACT_CURSOR"
    last_act_seq = _load_act_cursor(act_cursor_path) if act_file is not None else -1

    step_total = 0
    episode = 0

    def write_step(mission: str, frame_rgb: np.ndarray, act: Optional[int], reward: float,
                    terminated: bool, truncated: bool, chosen_by: Optional[str] = None,
                    act_seq: Optional[int] = None) -> None:
        nonlocal step_total
        png_name = f"step-{step_total:09d}.png"
        _atomic_write_bytes(door_dir / png_name, _png_bytes(frame_rgb))
        manifest = {
            "step": step_total, "episode": episode, "game": game, "seed": seed,
            "mission": mission, "act": act, "reward": float(reward),
            "terminated": bool(terminated), "truncated": bool(truncated), "frame": png_name,
            "n_actions": n_actions, "act_names": ACT_NAMES,
        }
        if chosen_by is not None:
            manifest["chosen_by"] = chosen_by
        if act_seq is not None:
            manifest["act_seq"] = act_seq
        _atomic_write_text(door_dir / f"step-{step_total:09d}.json", json.dumps(manifest))   # LAST: the manifest names an already-durable PNG
        step_total += 1

    obs, _info = env.reset(seed=int(seed) + episode)
    mission = obs["mission"]
    write_step(mission, base.get_pov_render(tile_size=tile), act=None, reward=0.0, terminated=False, truncated=False,
               chosen_by="schedule")

    try:
        while steps <= 0 or step_total < steps:
            if stop_path is not None and stop_path.exists():
                break
            if act_file is not None:
                chosen = _wait_for_act(Path(act_file), last_act_seq, stop_path)
                if chosen is None:
                    break   # stop requested while waiting -- a clean shutdown, never a timeout (no timeout exists)
                act = int(chosen["act"])
                act_seq = int(chosen["seq"])
                chosen_by = "mind"
            else:
                act = int(act_rng.integers(0, n_actions))
                act_seq = None
                chosen_by = "schedule"
            obs, reward, terminated, truncated, _info = env.step(act)
            write_step(mission, base.get_pov_render(tile_size=tile), act=act, reward=float(reward),
                       terminated=bool(terminated), truncated=bool(truncated), chosen_by=chosen_by, act_seq=act_seq)
            if act_file is not None:
                last_act_seq = act_seq
                _atomic_write_text(act_cursor_path, str(last_act_seq))   # AFTER the manifest above is durable (#230)
            if terminated or truncated:
                episode += 1
                obs, _info = env.reset(seed=int(seed) + episode)
                mission = obs["mission"]
            if period_s > 0:
                time.sleep(period_s)
    finally:
        _atomic_write_text(door_dir / "STOPPED.json", json.dumps({"step_total": step_total, "episodes": episode + 1}))
        env.close()
    return step_total


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, choices=sorted(GAME_IDS))
    ap.add_argument("--door-dir", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--tile", type=int, default=32)
    ap.add_argument("--steps", type=int, default=0, help="0 = run until --stop-file appears (or forever if none given)")
    ap.add_argument("--period-s", type=float, default=0.0)
    ap.add_argument("--stop-file", default=None)
    ap.add_argument("--act-file", default=None, help="L-8: the mind writes the next act here; absent -> the old seeded schedule")
    a = ap.parse_args(argv)
    n = run(a.game, Path(a.door_dir), a.seed, tile=a.tile, steps=a.steps, period_s=a.period_s,
            stop_path=Path(a.stop_file) if a.stop_file else None,
            act_file=Path(a.act_file) if a.act_file else None)
    print(f"game_worker_babyai: wrote {n} steps to {a.door_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
