#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 10:49 +0400 — ORIENTATION PROBE (not a result, not committed): world facts under the
# NULL policy (uniform over the 7 acts, the worker's own rng law) on BabyAI-GoToLocal-v0 — per-act frame-change rate (the premise of an
# «effect» signal), per-act marginal reward rate (why a per-act value law starves), render cost, and the oracle bot's API.
# Runs under /data/dev/game-worlds/venv/bin/python3 only.
import collections
import contextlib
import hashlib
import io
import json
import sys
import time

import numpy as np
import gymnasium as gym
import minigrid  # noqa: F401

ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
WORKER_RNG_TAG = 0x67616D65


def quiet_reset(env, seed):
    with contextlib.redirect_stdout(io.StringIO()):
        return env.reset(seed=int(seed))


def frame_sha(env):
    return hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()


def probe_random(seeds, episodes):
    env = gym.make("BabyAI-GoToLocal-v0", render_mode="rgb_array")
    n = collections.Counter()
    changed = collections.Counter()
    rewarded = collections.Counter()
    succ = 0
    eps = 0
    steps = 0
    t0 = time.perf_counter()
    for s in seeds:
        rng = np.random.default_rng([int(s), WORKER_RNG_TAG])
        for e in range(episodes):
            quiet_reset(env, s + e)
            prev = frame_sha(env)
            while True:
                a = int(rng.integers(0, 7))
                _o, r, te, tr, _i = env.step(a)
                cur = frame_sha(env)
                n[a] += 1
                changed[a] += int(cur != prev)
                rewarded[a] += int(r > 0)
                prev = cur
                steps += 1
                if te or tr:
                    eps += 1
                    succ += int(te and r > 0)
                    break
    wall = time.perf_counter() - t0
    env.close()
    rows = {}
    for a in range(7):
        rows[ACT_NAMES[a]] = {"n": n[a], "effect_rate": round(changed[a] / max(1, n[a]), 4),
                              "reward_rate_per_step": round(rewarded[a] / max(1, n[a]), 5), "rewarded": rewarded[a]}
    return {"episodes": eps, "steps": steps, "success": round(succ / eps, 4), "wall_s": round(wall, 1),
            "steps_per_s": round(steps / wall), "per_act": rows}


def probe_oracle(seed, episodes):
    from minigrid.utils.baby_ai_bot import BabyAIBot
    env = gym.make("BabyAI-GoToLocal-v0")
    succ = 0
    lens = []
    for e in range(episodes):
        quiet_reset(env, seed + e)
        bot = BabyAIBot(env.unwrapped)
        a = bot.replan()
        steps = 0
        while True:
            _o, r, te, tr, _i = env.step(a)
            steps += 1
            if te or tr:
                succ += int(te and r > 0)
                lens.append(steps)
                break
            a = bot.replan(a)
    env.close()
    return {"episodes": episodes, "success": succ / episodes, "mean_steps": float(np.mean(lens)), "max_steps": int(max(lens))}


if __name__ == "__main__":
    out = {}
    seeds = [20260923, 21260923, 22260923]
    out["random7"] = probe_random(seeds, 200)
    print(json.dumps(out["random7"], indent=1), flush=True)
    try:
        out["oracle"] = probe_oracle(20260923, 100)
        print("oracle", json.dumps(out["oracle"]), flush=True)
    except Exception as ex:  # the API may differ: report, do not guess
        print("oracle FAILED:", type(ex).__name__, str(ex)[:300], flush=True)
    json.dump(out, open("scratch/probe_world_facts.json", "w"), indent=1)
