#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:22 +0400 — ORIENTATION PROBE 3 (no candidate evaluated): world facts under the NULL policy (uniform over the 7 acts)
# on BabyAI-OpenRedDoor-v0, the TRANSFER world of PREREG-ACT-EFFECT §5 T1 (a level where `toggle` is the winning act): random-play success, and per-act change
# rate over same-episode pairs only, the first outcome of each episode EXCLUDED (the life's silent-reset rule), plus the OTHER door levels for context. Runs under /data/dev/game-worlds/venv/bin/python3.
import collections
import contextlib
import hashlib
import io
import json
import sys

import numpy as np
import gymnasium as gym
import minigrid  # noqa: F401

ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]
WORKER_RNG_TAG = 0x67616D65


def sha(env):
    return hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()


def probe(env_id, seeds, episodes):
    env = gym.make(env_id, render_mode="rgb_array")
    n = collections.Counter(); chg = collections.Counter()
    succ = eps = steps = excluded = 0
    max_steps = None
    for s in seeds:
        rng = np.random.default_rng([int(s), WORKER_RNG_TAG])
        for e in range(episodes):
            with contextlib.redirect_stdout(io.StringIO()):
                env.reset(seed=int(s) + e)
            max_steps = env.unwrapped.max_steps
            prev = sha(env)
            first = True               # the life never SEES the reset frame: the first act's effect crosses a silent reset -> UNKNOWN, excluded
            while True:
                a = int(rng.integers(0, 7))
                _o, r, te, tr, _i = env.step(a)
                cur = sha(env)
                if first:
                    first = False
                    excluded += 1
                else:
                    n[a] += 1; chg[a] += int(cur != prev)
                prev = cur; steps += 1
                if te or tr:
                    eps += 1; succ += int(te and r > 0)
                    break
    env.close()
    return {"env": env_id, "max_steps": max_steps, "episodes": eps, "success": round(succ / eps, 4), "mean_steps": round(steps / eps, 1),
            "excluded_first_outcomes": excluded, "per_act": {ACT_NAMES[a]: {"n": n[a], "p_changed": round(chg[a] / max(1, n[a]), 3)} for a in range(7)}}


if __name__ == "__main__":
    out = {}
    out["BabyAI-OpenRedDoor-v0"] = probe("BabyAI-OpenRedDoor-v0", [20260923, 21260923, 22260923], 100)
    print(json.dumps(out["BabyAI-OpenRedDoor-v0"], indent=1), flush=True)
    for eid in ("BabyAI-OpenDoor-v0", "BabyAI-GoToDoor-v0"):
        out[eid] = probe(eid, [20260923], 30)
        print(eid, "success", out[eid]["success"], {k: v["p_changed"] for k, v in out[eid]["per_act"].items()}, flush=True)
    json.dump(out, open("docs/organism/act/orient/probe_doors.json", "w"), indent=1)
