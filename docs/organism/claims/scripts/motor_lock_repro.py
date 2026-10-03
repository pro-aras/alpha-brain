#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 11:03 +0400 — the smallest reproduction of brain-long-2's motor lock (CLAIMS-CHECK-2026-10-03 (a)).
"""One reward anywhere locks the old chooser on that act. The law is copied from the code, nothing else is simulated:

  creature/mind.py:1037-1057  _record_reflex : expected = the act's cumulative mean of past `got` (None on its first observation),
                              residual = |got - expected| (None -> stored surprise 0.0); the mean is updated AFTER the residual is filed.
  creature/mind.py:2042-2043  weight[act] = mean of the last 10 stored surprises of that act (0.0 for an act never observed).
  creature/mind.py:2054-2062  with probability 0.1 a uniform draw (act_explored += 1), else argmax with ties broken by the rng.

Run:  python3 -B docs/organism/claims/scripts/motor_lock_repro.py        (stdlib only, ~2 s, exits 1 on a failed control)
The environment is the minimum that lets the law act: every step pays 0.0 except ONE planted reward (0.971875, the value brain-long-2's first
reward had) on the n-th choice of one chosen act. The real life paid 3 times in 4,925 steps (docs/organism/claims/CLAIMS-CHECK-2026-10-03.md)."""
import collections
import random
import sys

ACTS = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]     # BabyAI's own order, as in the journal's act_idx


def run(n_choices, seed, reward_act=None, reward_on_nth=44, reward=0.971875):
    rng = random.Random(seed)
    stored = {a: [] for a in ACTS}          # the outcome ring's stored `surprise` per act, oldest first
    mean = {a: None for a in ACTS}
    cnt = {a: 0 for a in ACTS}
    chosen = collections.Counter()
    after = collections.Counter()           # the choices made AFTER the planted reward was paid (the locked regime)
    reward_step = None
    explored = 0
    seen_of_rewarded = 0
    for step in range(n_choices):
        w = [(sum(stored[a][-10:]) / len(stored[a][-10:]) if stored[a] else 0.0) for a in ACTS]
        if rng.random() < 0.1:                       # the uniform floor (mind.py:2054-2056)
            idx = rng.randrange(7)
            explored += 1
        else:
            best = max(w)
            tied = [i for i, x in enumerate(w) if x == best]
            idx = tied[rng.randrange(len(tied))]
        a = ACTS[idx]
        chosen[a] += 1
        if reward_step is not None:
            after[a] += 1
        got = 0.0
        if a == reward_act:
            seen_of_rewarded += 1
            if seen_of_rewarded == reward_on_nth:
                got = reward
                reward_step = step
        expected = mean[a]
        residual = abs(got - expected) if expected is not None else None
        stored[a].append(residual if residual is not None else 0.0)
        cnt[a] += 1
        mean[a] = got if mean[a] is None else mean[a] + (got - mean[a]) / cnt[a]       # updated AFTER filing the residual
    return chosen, explored, after, reward_step


def main():
    n = 4000
    lock = 0.9 + 0.1 / 7
    # control 1: no reward at all -> every weight is exactly 0.0 forever -> uniform play (the lock needs a reward)
    ch0, ex0, _, _ = run(n, seed=1, reward_act=None)
    share0 = max(ch0.values()) / n
    print("choices per run: %d" % n)
    print("CONTROL, no reward at all: max act share %.3f of %d (uniform = %.3f), counts %s, explore draws %d" % (share0, n, 1 / 7, dict(ch0), ex0))
    assert share0 < 0.20, "control failed: without a reward the chooser must play ~uniformly (max share %.3f)" % share0
    # the planted reward on `right` (brain-long-2's case), on `left` (alpha4-1's case) and on `pickup` (an act that cannot move the agent), 10 seeds each
    mean_after = {}
    for act in ("right", "left", "pickup"):
        whole, aft, steps = [], [], []
        for seed in range(10):
            ch, ex, after, rstep = run(n, seed=100 + seed, reward_act=act)
            assert rstep is not None, "the planted reward was never paid"
            whole.append(ch[act] / n)
            aft.append(after[act] / sum(after.values()))
            steps.append(rstep)
        mean_after[act] = sum(aft) / len(aft)
        print("one reward on %-7s: reward paid at choice %d..%d ; share of `%s` AFTER it (10 seeds) min %.4f mean %.4f max %.4f ; over all %d choices %.3f-%.3f" % (act, min(steps), max(steps), act, min(aft), mean_after[act], max(aft), n, min(whole), max(whole)))
        assert all(abs(x - lock) < 0.02 for x in aft), "the lock did not form on %s: shares after the reward %s" % (act, [round(x, 3) for x in aft])
        assert abs(mean_after[act] - lock) < 0.004, "the locked share is not the floor's arithmetic on %s (mean %.4f vs %.4f)" % (act, mean_after[act], lock)
    # the plant changes the data: before its own reward the rewarded act holds no lock (the first choices are uniform)
    ch_pre, _, _, rstep = run(30, seed=100, reward_act="right")
    assert rstep is None or rstep >= 30 or max(ch_pre.values()) / 30 < 0.6
    assert max(ch_pre.values()) / 30 < 0.6, "plant check failed: the lock cannot exist before the planted reward"
    print("pure-lock expectation 0.9+0.1/7 = %.4f" % lock)
    print("CONTROLS CAUGHT: no reward -> uniform; ONE reward on any act -> that act locks at the floor's arithmetic (%.4f); the lock cannot exist before its reward" % lock)


if __name__ == "__main__":
    main()
    sys.exit(0)
