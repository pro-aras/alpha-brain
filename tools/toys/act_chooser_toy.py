#!/usr/bin/env python3
# edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:33 +0400 — docs/A4-LADDER-PREREG.md §2.5 PHASE 1
# (the brief's THE TOY): the game's act chooser driven against BabyAI GoToLocal at machine speed, the chooser's
# arithmetic copied VERBATIM as pure functions, its parity against the hour-1 fixture pinned; arms (i)–(v).
"""tools/toys/act_chooser_toy.py — THE ACT CHOOSER'S TOY (A4L-EXPLORE, Phase 1; ALPHA4-PREREG §11 finding 2).

WHY A COPY, NOT AN IMPORT: the old chooser's arithmetic lives INSIDE three `creature.mind.Mind` methods
(`_maybe_choose_act`, `_recent_reflex_residuals`, `_record_reflex`); it cannot be imported as a pure function
without changing mind.py's bytes (the ladder's negative control needs master's mind untouched), so it is copied
here verbatim and PINNED by `replay_choices()`: it walks a tape and the journal a replay wrote from it, in seq
order, and recomputes every `act` row — the weights (rounded to 6, as the journal writes them) and the chosen
act_idx — from the outcome history the mind had at that row (tests/creature/test_a4l_explore_toy.py: the hour-1
fixture's 121 act rows; and a REAL Mind driven through a planted-reward history, for the NONZERO weights the first
hour never has).

HALF 1 — PURE (numpy only; the system python3 the creature runs on imports it):
  Ring            the outcome ring as the chooser reads it: per act its outcomes in order, each (eid, got,
                  surprise), the surprise filed exactly as `_record_reflex` files a GAME row (the row carries
                  expected None and residual None, so expected = the act's running mean of its past `got`, None
                  on its first outcome → surprise 0.0; the mean updated AFTER filing); the window = the act's last
                  10 outcomes with eid ≥ n − cap (`_recent_reflex_residuals`; cap 2,000 = OUTCOME_EPISODES_CAP).
                  The toy's ring holds GAME outcomes only; the life's also holds say/sit/hands rows (303 of 1,014
                  in the 09-23 10:55 snapshot) — the cap can only matter to an act with < 10 outcomes among the
                  last 2,000 ring rows; `Ring.cap_cut_reads` counts every such read (printed per run).
  old_weights     per act: sum(last-10 surprise) / len, 0.0 when none — `_maybe_choose_act`, verbatim.
  reward_values   THE CANDIDATE (v): per act: sum(last-10 got) / len; an act with NO outcome in its window
                  («untried in that window» — the per-act window of `_recent_reflex_residuals`) reads the
                  optimism prior (1.0). Declared before any run (docs/briefs/A4L-EXPLORE-TOY.md §1).
  choose          u = rng.random(); u < 0.1 → rng.integers(0, n); else argmax, ties broken by
                  rng.integers(0, len(tied)) — TWO draws of the act rng on EVERY call, either branch.
  act_rng         np.random.default_rng([seed, 0x4143544d]) — creature/mind.py's own `_act_rng`.
  replay_choices  the parity walk (above).

HALF 2 — THE HARNESS (the game-worlds venv's python3 ONLY: gymnasium + minigrid are installed nowhere else):
  the worker's seed law — `env.reset(seed=base + episode)`, episode 0, 1, 2, … (tools/game_worker_babyai.py);
  64 steps an episode (RoomGridLevel recomputes max_steps at EVERY reset: asserted == 64 every time);
  the life's ONE-STEP LAG — creature/senses/game.py publishes ear, eye, outcome for a step, so the mind chooses
  act t+1 on frame t's eye row BEFORE it files outcome t; the act chosen on a terminal frame is applied to the
  NEXT episode's first state (the worker resets silently; the mind never sees that state);
  success = the episode ended `terminated` with reward > 0 (G5-G's rule, `worldfacts.py:null_scores`: tot > 0).
  No render_mode (rendering draws no randomness; calibration (0b) proves the dynamics equal the life's: the old
  chooser at the life's seed reproduces the life's acts and rewards act for act).

Usage (the venv python for everything but `parity`):
  VENV=/data/dev/game-worlds/venv/bin/python3
  python3 tools/toys/act_chooser_toy.py parity --tape <fixture tape> --journal <its replayed journal>
  $VENV tools/toys/act_chooser_toy.py calib --tape <fixture tape> --snapshot <snapshot state dir> --out <json>
  $VENV tools/toys/act_chooser_toy.py arms --episodes 1000 --seeds 20260923,21260923,22260923 --out <json>
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import io
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

TREE = Path(__file__).resolve().parents[2]      # #199: every path derived from this file, never a live-tree literal

ACT_NAMES = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]   # tools/game_worker_babyai.py, verbatim order
OUTCOME_EPISODES_CAP = 2000     # creature/mind.py:106 (pinned against the import by the test)
WINDOW = 10                     # `self._recent_reflex_residuals(name, k=10)` in `_maybe_choose_act`
EXPLORE = 0.1                   # `if u < 0.1:` in `_maybe_choose_act`
ACT_RNG_TAG = 0x4143544d        # creature/mind.py:410 — `np.random.default_rng([seed, 0x4143544d])`
WORKER_RNG_TAG = 0x67616D65     # tools/game_worker_babyai.py — the worker's own seeded schedule (L-8's random worker)
MAX_STEPS = 64                  # GoToLocal: 1 nav × room 8² (RoomGridLevel.reset)
ENV_ID = "BabyAI-GoToLocal-v0"  # tools/game_worker_babyai.py GAME_IDS["babyai-gotolocal"]
LIFE_SEED = 20260923            # genome/ladder/A4L-FLOOR.genome SEED + WORLD game seed (alpha4-1's)

_GOT, _SURPRISE = 1, 2          # Ring record fields (eid, got, surprise)


# ============================================================================================ HALF 1 — PURE
class Ring:
    """The outcome ring as the chooser reads it. See the module docstring."""

    def __init__(self, cap: int = OUTCOME_EPISODES_CAP, k: int = WINDOW):
        self.cap = int(cap)
        self.k = int(k)
        self.n = 0                                        # ring rows ever written (the next write's eid)
        self._win: Dict[str, collections.deque] = {}      # act -> its last k (eid, got, surprise)
        self._expected: Dict[str, float] = {}             # `Mind._act_expected`
        self._count: Dict[str, int] = {}                  # `Mind._act_n`
        self.cap_cut_reads = 0                            # reads the cap cut short (see the module docstring)

    def record(self, act: str, got) -> Dict[str, object]:
        """`Mind._record_reflex` for a game outcome row (expected_in None, residual_in None), verbatim."""
        expected: Optional[float] = self._expected.get(act)
        got_f: Optional[float] = float(got) if got is not None else None
        if expected is not None and got_f is not None:
            residual: Optional[float] = abs(got_f - expected)
        else:
            residual = None
        surprise = float(residual) if residual is not None else 0.0
        eid = self.n
        self.n += 1
        self._win.setdefault(act, collections.deque(maxlen=self.k)).append(
            (eid, got_f if got_f is not None else 0.0, surprise))
        if got_f is not None:                         # update the running expectation AFTER filing this residual
            n = self._count.get(act, 0) + 1
            old = self._expected.get(act, got_f)
            self._expected[act] = old + (got_f - old) / n
            self._count[act] = n
        return {"act": act, "expected": expected, "got": got_f, "residual": residual, "surprise": surprise}

    def recent(self, act: str, field: int) -> List[float]:
        """The act's last ≤ k outcomes with eid ≥ n − cap, NEWEST FIRST — `_recent_reflex_residuals`'s walk
        (it scans eid n−1 … max(0, n−cap) and stops at k matches; an overwritten slot never resolves)."""
        win = self._win.get(act)
        if not win:
            return []
        lo = max(0, self.n - self.cap)
        out = [rec[field] for rec in reversed(win) if rec[0] >= lo]
        if len(out) < len(win):
            self.cap_cut_reads += 1
        return out


def old_weights(ring: Ring, act_names: Sequence[str]) -> List[float]:
    """`_maybe_choose_act`'s weights, verbatim: the mean |residual| (the filed surprise) of each act's last 10."""
    weights = []
    for name in act_names:
        residuals = ring.recent(name, _SURPRISE)
        weights.append(sum(residuals) / len(residuals) if residuals else 0.0)
    return weights


def reward_values(ring: Ring, act_names: Sequence[str], optimism: float = 1.0) -> List[float]:
    """THE CANDIDATE (v): each act's mean REWARD (`got`) over its last 10 outcomes; an act with no outcome in its
    window reads `optimism`."""
    values = []
    for name in act_names:
        gots = ring.recent(name, _GOT)
        values.append(sum(gots) / len(gots) if gots else float(optimism))
    return values


def act_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng([int(seed), ACT_RNG_TAG])


def choose(weights: Sequence[float], rng: np.random.Generator, n_actions: int,
           explore: float = EXPLORE) -> Tuple[int, bool]:
    """`_maybe_choose_act`'s choice, verbatim: TWO rng draws every call. Returns (idx, explored)."""
    u = float(rng.random())
    if u < explore:
        return int(rng.integers(0, n_actions)), True
    best = max(weights)
    tied = [i for i, w in enumerate(weights) if w == best]
    pick = int(rng.integers(0, len(tied)))
    return tied[pick], False


def replay_choices(tape_rows: Iterable[Dict[str, object]], journal_rows: Iterable[Dict[str, object]],
                   seed: int) -> List[Dict[str, object]]:
    """THE PARITY WALK: the game rows of a tape in seq order — on a game `eye` row the old chooser's weights and
    choice are recomputed from the ring as it stands (BEFORE that frame's own outcome row, which follows it on
    the tape) and compared with the journal's `act` row at that seq; on a game `outcome` row the outcome is filed.
    One row per game eye row: {seq, weights, act_idx, act, weights_match, act_match, journal}."""
    journal_acts: Dict[int, Dict[str, object]] = {}
    for r in journal_rows:
        a = r.get("act")
        if isinstance(a, dict) and "weights" in a:
            journal_acts[int(r["seq"])] = a
    ring = Ring()
    rng = act_rng(seed)
    out: List[Dict[str, object]] = []
    for row in sorted(tape_rows, key=lambda r: int(r["seq"])):
        meta = row.get("meta") or {}
        if meta.get("source") != "game":
            continue
        if row.get("sense") == "eye":
            n_actions = meta.get("n_actions")
            if n_actions is None:
                continue
            n_actions = int(n_actions)
            names = list(meta.get("act_names") or [str(i) for i in range(n_actions)])[:n_actions]
            w = old_weights(ring, names)
            idx, _explored = choose(w, rng, n_actions)
            wr = [round(x, 6) for x in w]
            j = journal_acts.get(int(row["seq"]))
            out.append({"seq": int(row["seq"]), "weights": wr, "act_idx": idx, "act": names[idx],
                        "weights_match": j is not None and list(j.get("weights") or []) == wr,
                        "act_match": j is not None and int(j.get("act_idx", -1)) == idx and j.get("act") == names[idx],
                        "journal": j})
        elif row.get("sense") == "outcome":
            ring.record(str(meta.get("act", "")), meta.get("got"))
    return out


def null_bound(n: int, p0: float, alpha: float = 0.05) -> Tuple[int, float]:
    """The one-sided (1 − alpha) upper bound of a Binomial(n, p0) success COUNT: the smallest k with
    P(X ≥ k) ≤ alpha. Returns (k, k / n) — a rate at or above k/n over n episodes clears the null."""
    if n <= 0:
        return 0, float("nan")
    tail = 0.0
    for k in range(n, -1, -1):
        tail += math.comb(n, k) * (p0 ** k) * ((1.0 - p0) ** (n - k))
        if tail > alpha:
            return k + 1, (k + 1) / n
    return 0, 0.0


# ============================================================================================ HALF 2 — THE HARNESS
class OldChooser:
    """(i): the life's chooser — weights = mean surprise of the last 10 outcomes; 90 % argmax, 10 % uniform."""
    label = "old"

    def __init__(self, seed: int):
        self.rng = act_rng(seed)
        self.calls = 0
        self.explored = 0
        self.states: Dict[int, dict] = {}
        self.keep_states: frozenset = frozenset()

    def act(self, ring: Ring) -> int:
        idx, explored = choose(old_weights(ring, ACT_NAMES), self.rng, len(ACT_NAMES))
        self.calls += 1
        self.explored += int(explored)
        if self.calls in self.keep_states:
            self.states[self.calls] = self.rng.bit_generator.state
        return idx


class RewardChooser(OldChooser):
    """(v) THE CANDIDATE: value = mean reward of the last 10 outcomes, optimism for an act with none; the same
    10 % uniform draw and the same two-draw discipline on the same act rng."""
    label = "reward"

    def __init__(self, seed: int, optimism: float = 1.0):
        super().__init__(seed)
        self.optimism = float(optimism)

    def act(self, ring: Ring) -> int:
        idx, explored = choose(reward_values(ring, ACT_NAMES, self.optimism), self.rng, len(ACT_NAMES))
        self.calls += 1
        self.explored += int(explored)
        return idx


class FixedDist:
    """(ii)–(iv): a FIXED distribution over acts, drawn from the WORKER's own seeded schedule rng
    (`default_rng([seed, 0x67616D65])`). Uniform over k acts draws `integers(0, k)` — for k = 7 exactly the
    worker's own `act_rng.integers(0, n_actions)` (L-8's random worker); otherwise one `random()` against the
    cumulative probabilities (left, right, forward order)."""
    label = "fixed"

    def __init__(self, seed: int, probs: Dict[int, float]):
        self.rng = np.random.default_rng([int(seed), WORKER_RNG_TAG])
        self.acts = sorted(i for i, p in probs.items() if p > 0)
        ps = [probs[i] for i in self.acts]
        self.uniform = len(set(round(p, 12) for p in ps)) == 1
        tot = float(sum(ps))
        self.cum = list(np.cumsum([p / tot for p in ps]))
        self.calls = 0
        self.explored = 0

    def act(self, ring: Ring) -> int:
        self.calls += 1
        if self.uniform:
            return self.acts[int(self.rng.integers(0, len(self.acts)))]
        u = float(self.rng.random())
        for a, c in zip(self.acts, self.cum):
            if u < c:
                return a
        return self.acts[-1]


def make_env(env_id: str = ENV_ID):
    import gymnasium as gym
    import minigrid  # noqa: F401  -- registers the BabyAI ids
    return gym.make(env_id)


def quiet_reset(env, seed: int):
    """env.reset(seed=…) with minigrid's rejection-sampling chatter ("Sampling rejected: unreachable object at …",
    printed by RoomGridLevel's generator loop to stdout) swallowed — it draws nothing and changes nothing."""
    with contextlib.redirect_stdout(io.StringIO()):
        return env.reset(seed=int(seed))


def run_game(policy, base_seed: int, episodes: int, env_id: str = ENV_ID, keep_trace: int = 0,
             max_steps_total: Optional[int] = None) -> Dict[str, object]:
    """One life of the game at machine speed under the worker's seed law and the life's one-step lag. Stops after
    `episodes` completed episodes, or (`max_steps_total`, the `lives` diagnostic) after that many env steps."""
    if os.environ.get("BABYAI_DONE_ACTIONS"):
        raise SystemExit("BABYAI_DONE_ACTIONS is set: `done` would change the verifier (minigrid babyai verifier.py:26)")
    env = make_env(env_id)
    un = env.unwrapped
    ring = Ring()
    episode = 0
    quiet_reset(env, int(base_seed) + episode)
    if int(un.max_steps) != MAX_STEPS:
        raise SystemExit(f"max_steps {un.max_steps} != {MAX_STEPS} at episode {episode}")
    a = policy.act(ring)                                  # the reset frame's eye row: the first choice
    per_ep: List[Tuple[int, float, bool, bool]] = []      # (steps, reward, terminated, truncated)
    acts: List[int] = []
    trace: List[Dict[str, object]] = []
    ep_steps, ep_ret, step_total = 0, 0.0, 0
    t0 = time.perf_counter()
    while episode < episodes and (max_steps_total is None or step_total < max_steps_total):
        _obs, r, te, tr, _info = env.step(a)
        step_total += 1
        ep_steps += 1
        ep_ret += float(r)
        acts.append(a)
        nxt = policy.act(ring)                            # frame t's eye row: chosen BEFORE outcome t is filed
        filed = ring.record(ACT_NAMES[a], float(r))       # outcome t
        if len(trace) < keep_trace:
            trace.append({"act": ACT_NAMES[a], "act_idx": a, "got": float(r), "surprise": filed["surprise"],
                          "terminated": bool(te), "truncated": bool(tr), "episode": episode, "step": step_total})
        if te or tr:
            per_ep.append((ep_steps, ep_ret, bool(te), bool(tr)))
            episode += 1
            ep_steps, ep_ret = 0, 0.0
            if episode < episodes:
                quiet_reset(env, int(base_seed) + episode)
                if int(un.max_steps) != MAX_STEPS:
                    raise SystemExit(f"max_steps {un.max_steps} != {MAX_STEPS} at episode {episode}")
        a = nxt
    env.close()
    wall = time.perf_counter() - t0
    if not per_ep:
        per_ep.append((ep_steps, ep_ret, False, False))    # a step budget that ended before any episode did
    succ = [1 if (te and rew > 0) else 0 for (_s, rew, te, _tr) in per_ep]
    last100 = collections.Counter(ACT_NAMES[i] for i in acts[-100:])
    top_act, top_n = last100.most_common(1)[0]
    blocks = [acts[i:i + 100] for i in range(0, len(acts) - 99, 100)]
    locked_blocks = sum(1 for b in blocks if collections.Counter(b).most_common(1)[0][1] >= 80)
    first_success = next((i for i, s in enumerate(succ) if s), None)
    return {
        "episodes": len(per_ep), "successes": int(sum(succ)), "success_rate": sum(succ) / len(per_ep),
        "mean_steps": statistics.fmean(s for (s, _r, _te, _tr) in per_ep),
        "mean_reward": statistics.fmean(rw for (_s, rw, _te, _tr) in per_ep),
        "truncated": sum(1 for (_s, _r, _te, tr) in per_ep if tr),
        "steps": step_total, "last100": dict(last100.most_common()), "last100_top": [top_act, top_n],
        "locked_blocks": [locked_blocks, len(blocks)], "first_success_episode": first_success,
        "explored_share": policy.explored / max(1, policy.calls), "cap_cut_reads": ring.cap_cut_reads,
        "wall_s": round(wall, 2), "trace": trace,
    }


# ------------------------------------------------------------------------------------------ the arms (declared)
def arm_specs() -> List[Tuple[str, str, object]]:
    """(key, label, factory(seed) -> policy). Declared in docs/briefs/A4L-EXPLORE-TOY.md §1 before any run."""
    specs: List[Tuple[str, str, object]] = [
        ("i", "(i) OLD chooser — mean |residual| of the last 10, 90 % argmax, 10 % uniform", lambda s: OldChooser(s)),
        ("ii", "(ii) uniform over the 7 acts (the worker's own schedule)", lambda s: FixedDist(s, {i: 1.0 for i in range(7)})),
        ("iii", "(iii) uniform over {left, right, forward}", lambda s: FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0})),
    ]
    for f in (0.3, 0.5, 0.7, 0.9):
        side = (1.0 - f) / 2.0
        specs.append((f"iv-{f:.1f}", f"(iv) fixed: forward {f:.1f}, left {side:.2f}, right {side:.2f}",
                      (lambda ff, ss: (lambda s: FixedDist(s, {0: ss, 1: ss, 2: ff})))(f, side)))
    specs.append(("v", "(v) CANDIDATE — mean REWARD of the last 10, optimism 1.0 if untried, 90 % argmax, 10 % uniform",
                  lambda s: RewardChooser(s, 1.0)))
    return specs


def _summ(vals: Sequence[float]) -> Tuple[float, float]:
    return statistics.fmean(vals), (statistics.stdev(vals) if len(vals) > 1 else 0.0)


def cmd_arms(a) -> int:
    seeds = [int(s) for s in a.seeds.split(",")]
    out: Dict[str, object] = {"env": ENV_ID, "episodes": a.episodes, "seeds": seeds, "max_steps": MAX_STEPS,
                              "lag": "one step (the life's)", "arms": {}}
    print(f"[arms] {ENV_ID} · {a.episodes} episodes × seeds {seeds} · max_steps {MAX_STEPS} · the life's one-step lag")
    for key, label, factory in arm_specs():
        runs = []
        for s in seeds:
            pol = factory(s)
            r = run_game(pol, s, a.episodes)
            r.pop("trace", None)
            r["seed"] = s
            runs.append(r)
            print(f"  {key:7s} seed {s}: success {r['success_rate']:.3f} ({r['successes']}/{r['episodes']}) "
                  f"steps {r['mean_steps']:.1f} reward/ep {r['mean_reward']:.4f} last100 {r['last100_top']} "
                  f"locked {r['locked_blocks']} cap_cut {r['cap_cut_reads']} ({r['wall_s']} s)", flush=True)
        m, sd = _summ([r["success_rate"] for r in runs])
        pooled_n = sum(r["episodes"] for r in runs)
        pooled_p = sum(r["successes"] for r in runs) / pooled_n
        out["arms"][key] = {
            "label": label, "runs": runs, "success_mean": m, "success_sd": sd,
            "pooled_success": pooled_p, "pooled_se": math.sqrt(pooled_p * (1 - pooled_p) / pooled_n),
            "mean_steps": statistics.fmean(r["mean_steps"] for r in runs),
            "mean_reward": statistics.fmean(r["mean_reward"] for r in runs),
        }
    arms = out["arms"]
    grid = {k: v for k, v in arms.items() if k.startswith("iv-")}
    best_key = max(grid, key=lambda k: grid[k]["success_mean"])
    ii = arms["ii"]["success_mean"]
    out["ceiling"] = {"best_iv": best_key, "iv_minus_ii": grid[best_key]["success_mean"] - ii,
                      "v_minus_ii": arms["v"]["success_mean"] - ii, "iii_minus_ii": arms["iii"]["success_mean"] - ii}
    # X2's resolution (hours 2–8 of an 8 h life: 6 h × 120 steps an hour at the game's 30 s cadence)
    res = {}
    for k in ("ii", "iii", best_key, "v", "i"):
        n_ep = int(720 / arms[k]["mean_steps"])
        kk, rate = null_bound(n_ep, 0.29)
        kk2, rate2 = null_bound(n_ep, arms["ii"]["pooled_success"])
        res[k] = {"episodes_in_6h": n_ep, "bound_k_p029": kk, "bound_rate_p029": rate,
                  "bound_k_toy_null": kk2, "bound_rate_toy_null": rate2,
                  "toy_success": arms[k]["success_mean"]}
    out["x2_resolution"] = res
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"[arms] best (iv) {best_key}: (iv) − (ii) = {out['ceiling']['iv_minus_ii']:+.3f}; "
          f"(v) − (ii) = {out['ceiling']['v_minus_ii']:+.3f}; wrote {a.out}")
    return 0


# ------------------------------------------------------------------------------------------ calibration
def g_null(env_id: str, seeds: Iterable[int] = range(101, 201), rng_seed: int = 20260921) -> Dict[str, object]:
    """/data/dev/game-worlds/code/worldfacts.py:null_scores (G5-G's BabyAI null), reproduced EXACTLY: one
    default_rng(20260921) across the episodes, env.reset(seed=s) for s in 101..200, uniform over the 7 acts,
    up to max_steps, success = the episode's total reward > 0."""
    env = make_env(env_id)
    rng = np.random.default_rng(rng_seed)
    rets, succ, lens = [], 0, []
    seeds = list(seeds)
    for s in seeds:
        quiet_reset(env, s)
        tot, n = 0.0, 0
        for _t in range(int(env.unwrapped.max_steps)):
            _o, r, te, tr, _ = env.step(int(rng.integers(0, 7)))
            tot += r
            n += 1
            if te or tr:
                break
        rets.append(tot)
        lens.append(n)
        succ += int(tot > 0)
    env.close()
    return {"env": env_id, "episodes": len(seeds), "seeds": f"{seeds[0]}..{seeds[-1]}", "rng": rng_seed,
            "success_rate": round(succ / len(seeds), 3), "mean_return": round(float(np.mean(rets)), 4),
            "mean_steps": statistics.fmean(lens)}


def _tape_game_outcomes(tape: Path) -> List[Dict[str, object]]:
    rows = [json.loads(l) for l in tape.read_text().splitlines() if l.strip()]
    rows.sort(key=lambda r: int(r["seq"]))
    out = []
    for r in rows:
        m = r.get("meta") or {}
        if r.get("sense") == "outcome" and m.get("source") == "game":
            out.append({"seq": int(r["seq"]), "act": m["act"], "act_idx": int(m["act_idx"]), "got": float(m["got"]),
                        "terminated": bool(m.get("terminated")), "truncated": bool(m.get("truncated")),
                        "episode": int(m["episode"]), "step": int(m["step"]), "chosen_by": m.get("chosen_by")})
    return out


def _snapshot_game_ring(state_dir: Path) -> Tuple[List[Dict[str, object]], dict, int]:
    sys.path.insert(0, str(TREE))
    from genome.fast import Episodes      # numpy-only: the venv imports it from this tree
    ep = Episodes.load(str(state_dir / "outcome_episodes.npz"))
    game = []
    for eid in range(ep.n_written):
        rec = ep.get(eid)
        if rec is not None and rec["word"] in ACT_NAMES:
            game.append({"eid": eid, "act": str(rec["word"]), "got": float(rec["x_s"][0]), "surprise": float(rec["surprise"])})
    ledger = json.loads((state_dir / "ledger.json").read_text())
    return game, ledger.get("act_rng_state"), int(ledger.get("last_seq", -1))


def cmd_calib(a) -> int:
    out: Dict[str, object] = {}
    print("[calib] (0a) G5-G's null protocol, EXACT (worldfacts.py:null_scores)")
    for env_id in ("BabyAI-GoToRedBall-v0", ENV_ID):
        r = g_null(env_id)
        out[f"0a {env_id}"] = r
        print(f"  {env_id}: success {r['success_rate']} mean_return {r['mean_return']} mean_steps {r['mean_steps']:.1f} "
              f"(seeds {r['seeds']}, rng {r['rng']})")
    print("[calib] (0b) the OLD chooser at the life's seed vs the life's own record")
    fx = _tape_game_outcomes(Path(a.tape))
    snap, snap_rng, snap_seq = _snapshot_game_ring(Path(a.snapshot))
    n_trace = max(len(fx), len(snap)) + 5
    pol = OldChooser(LIFE_SEED)
    pol.keep_states = frozenset({len(snap), len(snap) + 1})
    # enough episodes to cover the snapshot's outcomes: run by episodes until the trace is long enough
    r = run_game(pol, LIFE_SEED, episodes=max(20, n_trace // 8), keep_trace=n_trace)
    tr = r["trace"]
    if len(tr) < n_trace:
        raise SystemExit(f"(0b) trace {len(tr)} < {n_trace}: raise the episode count")
    fields = ("act", "act_idx", "got", "terminated", "truncated", "episode", "step")
    fx_eq = [all(tr[i][f] == fx[i][f] for f in fields) for i in range(len(fx))]
    first_fx_diff = next((i for i, ok in enumerate(fx_eq) if not ok), None)
    sn_eq = [tr[i]["act"] == snap[i]["act"] and tr[i]["got"] == snap[i]["got"] and tr[i]["surprise"] == snap[i]["surprise"]
             for i in range(len(snap))]
    first_sn_diff = next((i for i, ok in enumerate(sn_eq) if not ok), None)
    rng_match = {str(k): (pol.states.get(k) == snap_rng) for k in sorted(pol.keep_states)}
    rewarded = [(i, snap[i]["act"], snap[i]["got"]) for i in range(len(snap)) if snap[i]["got"] != 0.0]
    census = collections.Counter(tr[i]["act"] for i in range(len(snap)))
    last100 = collections.Counter(tr[i]["act"] for i in range(max(0, len(snap) - 100), len(snap)))
    out["0b"] = {"fixture_outcomes": len(fx), "fixture_equal": sum(fx_eq), "fixture_first_diff": first_fx_diff,
                 "fixture_chosen_by_mind": sum(1 for x in fx if x["chosen_by"] == "mind"),
                 "snapshot_game_outcomes": len(snap), "snapshot_equal": sum(sn_eq), "snapshot_first_diff": first_sn_diff,
                 "snapshot_last_seq": snap_seq, "act_rng_state_equal_after_choices": rng_match,
                 "snapshot_rewarded": rewarded, "census_to_snapshot": dict(census.most_common()),
                 "last100_to_snapshot": dict(last100.most_common())}
    print(f"  fixture (hour 1): {sum(fx_eq)}/{len(fx)} outcomes equal on {fields} (first diff {first_fx_diff})")
    print(f"  snapshot (last_seq {snap_seq}): {sum(sn_eq)}/{len(snap)} game outcomes equal on (act, got, surprise) "
          f"(first diff {first_sn_diff}); rewarded {rewarded}")
    print(f"  act rng state equal after choices {rng_match}")
    print(f"  census to the snapshot {dict(census.most_common())}; its last 100 {dict(last100.most_common())}")
    Path(a.out).write_text(json.dumps(out, indent=1))
    ok = (first_fx_diff is None and first_sn_diff is None and any(rng_match.values())
          and out["0a BabyAI-GoToRedBall-v0"]["success_rate"] == 0.29
          and out["0a BabyAI-GoToRedBall-v0"]["mean_return"] == 0.1464)
    print(f"[calib] {'PASS' if ok else 'FAIL'} — wrote {a.out}")
    return 0 if ok else 1


def cmd_lockseries(a) -> int:
    """A DIAGNOSTIC of arm (i), not an arm: the same runs (the same seeds, the same 1,000 episodes — the totals must
    equal arm (i)'s), read as a SERIES — success per 100 episodes, the life-matched window (seed 20260923's first
    10 and 12 episodes ARE alpha4-1's, by (0b)), the locked act per 100-step block and every change of it, and
    which act each success was earned on (the locked act or an explored one)."""
    seeds = [int(s) for s in a.seeds.split(",")]
    out: Dict[str, object] = {}
    for s in seeds:
        pol = OldChooser(s)
        r = run_game(pol, s, a.episodes, keep_trace=10 ** 7)
        tr = r.pop("trace")
        ep_succ: Dict[int, bool] = {}
        ep_last: Dict[int, Dict[str, object]] = {}
        for t in tr:
            if t["terminated"] or t["truncated"]:
                ep_succ[t["episode"]] = bool(t["terminated"] and t["got"] > 0)
                ep_last[t["episode"]] = t
        eps = sorted(ep_succ)
        per100 = [round(sum(ep_succ[e] for e in eps[i:i + 100]) / len(eps[i:i + 100]), 3) for i in range(0, len(eps), 100)]
        blocks = [collections.Counter(t["act"] for t in tr[i:i + 100]).most_common(1)[0] for i in range(0, len(tr) - 99, 100)]
        tops = [b[0] if b[1] >= 80 else None for b in blocks]
        changes = sum(1 for x, y in zip(tops, tops[1:]) if x is not None and y is not None and x != y)
        locked_names = collections.Counter(t for t in tops if t is not None)
        # which act earned each success, and was it the act locked in that 100-step block?
        on_locked = 0
        earned = collections.Counter()
        for i, t in enumerate(tr):
            if t["terminated"] and t["got"] > 0:
                earned[t["act"]] += 1
                blk = i // 100
                if blk < len(tops) and tops[blk] == t["act"]:
                    on_locked += 1
        row = {"success_rate": r["success_rate"], "successes": r["successes"], "per100": per100,
               "first10": sum(ep_succ[e] for e in eps[:10]), "first12": sum(ep_succ[e] for e in eps[:12]),
               "locked_blocks": r["locked_blocks"], "lock_changes": changes, "locked_act_blocks": dict(locked_names.most_common()),
               "successes_by_act": dict(earned.most_common()), "successes_on_the_locked_act": on_locked}
        out[str(s)] = row
        print(f"  seed {s}: success {r['success_rate']:.3f} ({r['successes']}) · first 10 episodes {row['first10']} · first 12 {row['first12']} "
              f"· per 100 {per100} · locked blocks {r['locked_blocks']} on {row['locked_act_blocks']} · lock changes {changes} "
              f"· successes by act {row['successes_by_act']} (on the locked act {on_locked})", flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    return 0


def cmd_lives(a) -> int:
    """A DIAGNOSTIC for the rung's marks (A4-LADDER-PREREG §2.5, written before the life): `n` FRESH lives of `acts`
    game steps each (960 = an 8 h life at the game's 30 s cadence), per arm, each on its own seed
    (base + 1,000 × i: the ≤ 30 episodes a life plays never share a layout with the next life's). Per life:
    X1 — the largest share one act holds in ANY 100-act window (sliding) that starts after the first `hour` acts
    (120 = hour 1); X2 — the episodes that END in acts x2_from+1 … acts (240 → 960 = the life's hours 2–8, «hours
    a–b» read as the ladder reads «hours 0–8»: from a h to b h), their successes, and whether the successes reach
    the one-sided 95 % bound of the null (p0) at that N. Printed: the share of lives X1 would pass (max share < 0.5)
    and X2 would pass, the success distribution — the rung's predictions, and X2's ceiling."""
    keys = a.arms.split(",")
    specs = {k: f for k, _label, f in arm_specs()}
    out: Dict[str, object] = {"acts": a.acts, "hour": a.hour, "x2_from": a.x2_from, "lives": a.n, "base": a.base, "p0": a.p0, "arms": {}}
    for key in keys:
        rows = []
        for i in range(a.n):
            s = a.base + 1000 * i
            pol = specs[key](s)
            r = run_game(pol, s, 10 ** 6, keep_trace=a.acts, max_steps_total=a.acts)
            tr = r.pop("trace")
            acts = [t["act"] for t in tr]
            mx = 0.0
            cnt = collections.Counter(acts[a.hour:a.hour + 100])
            if len(acts) >= a.hour + 100:
                mx = max(cnt.values()) / 100.0
                for j in range(a.hour + 100, len(acts)):
                    cnt[acts[j]] += 1
                    cnt[acts[j - 100]] -= 1
                    mx = max(mx, max(cnt.values()) / 100.0)
            ends = [t for t in tr[a.x2_from:] if t["terminated"] or t["truncated"]]
            n_ep = len(ends)
            k = sum(1 for t in ends if t["terminated"] and t["got"] > 0)
            kb, _rate = null_bound(n_ep, a.p0)
            rows.append({"seed": s, "x1_max_share": mx, "x2_episodes": n_ep, "x2_successes": k, "x2_bound_k": kb,
                         "x2_pass": bool(n_ep > 0 and k >= kb), "x1_pass": bool(mx < 0.5)})
        x1 = sum(r["x1_pass"] for r in rows) / len(rows)
        x2 = sum(r["x2_pass"] for r in rows) / len(rows)
        rates = [r["x2_successes"] / r["x2_episodes"] for r in rows if r["x2_episodes"]]
        eps = [r["x2_episodes"] for r in rows]
        mxs = sorted(r["x1_max_share"] for r in rows)
        out["arms"][key] = {"rows": rows, "x1_pass_share": x1, "x2_pass_share": x2,
                            "x2_success_mean": statistics.fmean(rates), "x2_success_sd": statistics.pstdev(rates),
                            "x2_episodes_median": statistics.median(eps), "x2_episodes_range": [min(eps), max(eps)],
                            "x1_max_share_median": statistics.median(mxs), "x1_max_share_range": [mxs[0], mxs[-1]]}
        print(f"  {key:7s} {a.n} lives × {a.acts} acts: X1 pass {x1:.2f} (max 100-window share median {statistics.median(mxs):.2f}, "
              f"range {mxs[0]:.2f}–{mxs[-1]:.2f}) · X2 acts {a.x2_from + 1}–{a.acts}: episodes median {statistics.median(eps)} ({min(eps)}–{max(eps)}), "
              f"success {statistics.fmean(rates):.3f} ± {statistics.pstdev(rates):.3f} (sd over lives), X2 pass {x2:.2f}", flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    return 0


def cmd_parity(a) -> int:
    tape_rows = [json.loads(l) for l in Path(a.tape).read_text().splitlines() if l.strip()]
    journal_rows = [json.loads(l) for l in Path(a.journal).read_text().splitlines() if l.strip()]
    rows = replay_choices(tape_rows, journal_rows, a.seed)
    n = len(rows)
    wm = sum(1 for r in rows if r["weights_match"])
    am = sum(1 for r in rows if r["act_match"])
    nz = sum(1 for r in rows if any(r["weights"]))
    print(f"[parity] {n} game eye rows; weights equal {wm}/{n}; chosen act equal {am}/{n}; rows with a nonzero weight {nz}")
    ok = n >= 50 and wm == n and am == n
    print(f"[parity] {'PASS' if ok else 'FAIL'} (admission: ≥ 50 rows, every one equal)")
    return 0 if ok else 1


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parity")
    p.add_argument("--tape", required=True)
    p.add_argument("--journal", required=True)
    p.add_argument("--seed", type=int, default=LIFE_SEED)
    c = sub.add_parser("calib")
    c.add_argument("--tape", required=True)
    c.add_argument("--snapshot", required=True)
    c.add_argument("--out", required=True)
    r = sub.add_parser("arms")
    r.add_argument("--episodes", type=int, default=1000)
    r.add_argument("--seeds", default=f"{LIFE_SEED},{LIFE_SEED + 1_000_000},{LIFE_SEED + 2_000_000}")
    r.add_argument("--out", required=True)
    d = sub.add_parser("lockseries")
    d.add_argument("--episodes", type=int, default=1000)
    d.add_argument("--seeds", default=f"{LIFE_SEED},{LIFE_SEED + 1_000_000},{LIFE_SEED + 2_000_000}")
    d.add_argument("--out", required=True)
    v = sub.add_parser("lives")
    v.add_argument("--arms", default="i,ii,iv-0.5,v")
    v.add_argument("--n", type=int, default=50)
    v.add_argument("--acts", type=int, default=960)
    v.add_argument("--hour", type=int, default=120)
    v.add_argument("--x2-from", dest="x2_from", type=int, default=240)
    v.add_argument("--base", type=int, default=30260923)
    v.add_argument("--p0", type=float, default=0.29)
    v.add_argument("--out", required=True)
    a = ap.parse_args(list(argv))
    return {"parity": cmd_parity, "calib": cmd_calib, "arms": cmd_arms, "lockseries": cmd_lockseries, "lives": cmd_lives}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
