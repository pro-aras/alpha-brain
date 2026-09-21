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


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _png_bytes(rgb: np.ndarray) -> bytes:
    import io
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def run(game: str, door_dir: Path, seed: int, tile: int = 32, steps: int = 0, period_s: float = 0.0,
        stop_path: Optional[Path] = None) -> int:
    """`steps<=0` -> run until `stop_path` exists (creature/senses/game.py writes it on shutdown) or,
    with no stop_path given (a bare CLI run), forever. Returns the total number of manifests written."""
    import gymnasium as gym
    import minigrid  # noqa: F401  -- registers the BabyAI/MiniGrid env ids

    door_dir = Path(door_dir)
    door_dir.mkdir(parents=True, exist_ok=True)
    env_id = GAME_IDS[game]
    env = gym.make(env_id, render_mode="rgb_array")
    base = env.unwrapped
    act_rng = np.random.default_rng([int(seed), 0x67616D65])   # "game" bytes-ish; its own stream, never env's own rng

    step_total = 0
    episode = 0

    def write_step(mission: str, frame_rgb: np.ndarray, act: Optional[int], reward: float,
                    terminated: bool, truncated: bool) -> None:
        nonlocal step_total
        png_name = f"step-{step_total:09d}.png"
        _atomic_write_bytes(door_dir / png_name, _png_bytes(frame_rgb))
        manifest = {
            "step": step_total, "episode": episode, "game": game, "seed": seed,
            "mission": mission, "act": act, "reward": float(reward),
            "terminated": bool(terminated), "truncated": bool(truncated), "frame": png_name,
        }
        _atomic_write_text(door_dir / f"step-{step_total:09d}.json", json.dumps(manifest))   # LAST: the manifest names an already-durable PNG
        step_total += 1

    obs, _info = env.reset(seed=int(seed) + episode)
    mission = obs["mission"]
    write_step(mission, base.get_pov_render(tile_size=tile), act=None, reward=0.0, terminated=False, truncated=False)

    try:
        while steps <= 0 or step_total < steps:
            if stop_path is not None and stop_path.exists():
                break
            act = int(act_rng.integers(0, int(env.action_space.n)))
            obs, reward, terminated, truncated, _info = env.step(act)
            write_step(mission, base.get_pov_render(tile_size=tile), act=act, reward=float(reward),
                       terminated=bool(terminated), truncated=bool(truncated))
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
    a = ap.parse_args(argv)
    n = run(a.game, Path(a.door_dir), a.seed, tile=a.tile, steps=a.steps, period_s=a.period_s,
            stop_path=Path(a.stop_file) if a.stop_file else None)
    print(f"game_worker_babyai: wrote {n} steps to {a.door_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
