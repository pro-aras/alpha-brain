#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:00 +0400 — ORIENTATION PROBE 2 (scratch, not committed, no candidate evaluated): world facts under the
# NULL policy (uniform over the 7 acts) on BabyAI-GoToLocal-v0, mirroring the life's episode boundary (the worker resets SILENTLY: the act chosen on a
# terminal frame lands on the next episode's reset state, so the first outcome of an episode has NO same-episode previous frame).
#   (1) per act: P(frame changed) and P(frame NOVEL = its sha unseen earlier in this episode), both over SAME-EPISODE pairs only;
#   (2) the same two, conditioned on whether the PREVIOUS act's frame changed (the 7 x 2 table a reactive chooser could learn);
#   (3) per act: P(reward) conditioned on previous-changed (is blocked-then-turn different from moved-then-turn?).
import collections
import contextlib
import hashlib
import io
import json

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


def run(seeds, episodes):
    env = gym.make("BabyAI-GoToLocal-v0", render_mode="rgb_array")
    n = collections.Counter(); chg = collections.Counter(); nov = collections.Counter()
    n2 = collections.Counter(); chg2 = collections.Counter(); nov2 = collections.Counter(); rew2 = collections.Counter()
    unknown = 0
    total = 0
    for s in seeds:
        rng = np.random.default_rng([int(s), WORKER_RNG_TAG])
        quiet_reset(env, s)
        episode = 0
        prev_sha = frame_sha(env)          # episode 0's reset frame IS visible (the worker's first manifest)
        seen = {prev_sha}
        prev_changed = None                # no previous outcome yet
        visible_prev = True
        done_eps = 0
        first_in_episode = False
        while done_eps < episodes:
            a = int(rng.integers(0, 7))
            _o, r, te, tr, _i = env.step(a)
            cur = frame_sha(env)
            total += 1
            if first_in_episode:
                # the act lands on a reset state the mind never saw: the pair crosses the boundary -> UNKNOWN
                unknown += 1
                seen = {cur}
                prev_changed = None
            else:
                changed = cur != prev_sha
                novel = cur not in seen
                n[a] += 1; chg[a] += int(changed); nov[a] += int(novel)
                if prev_changed is not None:
                    key = (a, int(prev_changed))
                    n2[key] += 1; chg2[key] += int(changed); nov2[key] += int(novel); rew2[key] += int(r > 0)
                seen.add(cur)
                prev_changed = changed
            prev_sha = cur
            first_in_episode = False
            if te or tr:
                done_eps += 1
                episode += 1
                quiet_reset(env, s + episode)
                prev_sha = None
                first_in_episode = True    # the next act lands on the (never shown) reset state
                prev_changed = None
    env.close()
    out = {"steps": total, "unknown_boundary_outcomes": unknown, "per_act": {}, "ctx": {}}
    for a in range(7):
        out["per_act"][ACT_NAMES[a]] = {"n": n[a], "p_changed": round(chg[a] / max(1, n[a]), 3), "p_novel": round(nov[a] / max(1, n[a]), 3)}
    for a in range(7):
        for pc in (0, 1):
            k = (a, pc)
            out["ctx"][f"{ACT_NAMES[a]}|prev_changed={pc}"] = {
                "n": n2[k], "p_changed": round(chg2[k] / max(1, n2[k]), 3), "p_novel": round(nov2[k] / max(1, n2[k]), 3),
                "reward_per_step": round(rew2[k] / max(1, n2[k]), 4)}
    return out


if __name__ == "__main__":
    res = run([20260923, 21260923, 22260923], 200)
    print(json.dumps(res, indent=1))
    json.dump(res, open("scratch/probe_world_facts2.json", "w"), indent=1)
