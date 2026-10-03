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


EPS = 0.05                      # (v-b)/(v-c)'s floor ε (the orchestrator's 12:2x +04 message)


def sampled_choice(values: Sequence[float], rng: np.random.Generator, n_actions: int,
                   explore: float = EXPLORE) -> Tuple[int, bool]:
    """(v-b)/(v-c) — edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 12:21 +0400: the SAME first draw and the same
    10 % uniform branch as `choose`; otherwise ONE `rng.random()` against the running sum of `values` (probability
    ∝ value, no argmax) — TWO draws of the act rng on every call, either branch. Every value must be > 0 (the ε floor)."""
    u = float(rng.random())
    if u < explore:
        return int(rng.integers(0, n_actions)), True
    r = float(rng.random()) * float(sum(values))
    acc = 0.0
    for i, v in enumerate(values):
        acc += v
        if r < acc:
            return i, False
    return len(values) - 1, False


def replay_choices(tape_rows: Iterable[Dict[str, object]], journal_rows: Iterable[Dict[str, object]],
                   seed: int, law: str = "old", window: int = WINDOW, optimism: float = 1.0) -> List[Dict[str, object]]:
    """THE PARITY WALK: the game rows of a tape in seq order — on a game `eye` row the chooser's weights and choice
    are recomputed from the ring as it stands (BEFORE that frame's own outcome row, which follows it on the tape)
    and compared with the journal's `act` row at that seq; on a game `outcome` row the outcome is filed. `law`:
    "old" (the life's outcome-weighted law) or "reward" (the candidate — the rung's `ACT value reward <window>;
    optimism <optimism>`, Phase 2's parity). One row per game eye row: {seq, weights, act_idx, act,
    weights_match, act_match, journal}."""
    journal_acts: Dict[int, Dict[str, object]] = {}
    for r in journal_rows:
        a = r.get("act")
        if isinstance(a, dict) and "weights" in a:
            journal_acts[int(r["seq"])] = a
    ring = Ring(k=window)
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
            w = old_weights(ring, names) if law == "old" else reward_values(ring, names, optimism)
            idx, explored = choose(w, rng, n_actions)
            wr = [round(x, 6) for x in w]
            j = journal_acts.get(int(row["seq"]))
            out.append({"seq": int(row["seq"]), "weights": wr, "act_idx": idx, "act": names[idx], "explored": explored,
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


class RewardSampler(OldChooser):
    """(v-b) — the orchestrator's first further candidate (12:2x +04), declared in A4L-EXPLORE-TOY.md §5 before its run:
    the act is DRAWN with probability ∝ (its mean reward over its last 10 outcomes + ε 0.05) — an act with no outcome
    in its window reads the optimism prior 1.0 (+ ε), as (v) — no argmax; the 10 % uniform draw kept; two draws."""
    label = "reward-sampled"

    def __init__(self, seed: int, eps: float = EPS, optimism: float = 1.0):
        super().__init__(seed)
        self.eps = float(eps)
        self.optimism = float(optimism)

    def act(self, ring: Ring) -> int:
        vals = [v + self.eps for v in reward_values(ring, ACT_NAMES, self.optimism)]
        idx, explored = sampled_choice(vals, self.rng, len(ACT_NAMES))
        self.calls += 1
        self.explored += int(explored)
        return idx


class EpisodeCredit(OldChooser):
    """(v-c) — the orchestrator's second (12:2x +04; «act to episode», the OUTCOME gene's own words): every act taken
    inside an episode is credited with THAT EPISODE's terminal reward (the success reward on a `terminated` step; 0.0
    on a truncation) when the episode's terminal outcome is filed — so the credit, like every outcome, reaches the
    chooser one step late (the life's lag); an act's value = its mean credited reward over its last 20 credited
    outcomes + ε 0.05, an act with none reads the optimism prior 1.0 (+ ε); drawn ∝ value (`sample=True`) or by the
    argmax with rng ties (`sample=False` — the control that the SAMPLING carries any gain); the 10 % uniform draw
    kept; two draws. «Acts taken inside an episode» = the acts whose outcomes that episode's steps filed (the act
    chosen on a terminal frame belongs to the NEXT episode, where the worker applies it)."""
    label = "episode-credit"

    def __init__(self, seed: int, window: int = 20, eps: float = EPS, optimism: float = 1.0, sample: bool = True):
        super().__init__(seed)
        self.window, self.eps, self.optimism, self.sample = int(window), float(eps), float(optimism), bool(sample)
        self.credited: Dict[str, collections.deque] = {a: collections.deque(maxlen=self.window) for a in ACT_NAMES}
        self.episode_acts: List[str] = []

    def observe(self, act: str, got: float, terminated: bool, truncated: bool) -> None:
        self.episode_acts.append(act)
        if terminated or truncated:
            credit = float(got) if terminated else 0.0
            for a in self.episode_acts:
                self.credited.setdefault(a, collections.deque(maxlen=self.window)).append(credit)
            self.episode_acts = []

    def values(self) -> List[float]:
        out = []
        for a in ACT_NAMES:
            c = self.credited.get(a)
            out.append((sum(c) / len(c) if c else self.optimism) + self.eps)
        return out

    def act(self, ring: Ring) -> int:
        vals = self.values()
        if self.sample:
            idx, explored = sampled_choice(vals, self.rng, len(ACT_NAMES))
        else:
            idx, explored = choose(vals, self.rng, len(ACT_NAMES))
        self.calls += 1
        self.explored += int(explored)
        return idx


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
        if hasattr(policy, "observe"):                    # (v-c): the episode's credit, filed with the outcome that ends it
            policy.observe(ACT_NAMES[a], float(r), bool(te), bool(tr))
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
    # the orchestrator's two further laws (12:2x +04), declared in A4L-EXPLORE-TOY.md §5 before their run
    specs.append(("v-b", "(v-b) SAMPLE ∝ (mean reward of the last 10 + ε 0.05; untried 1.0 + ε), 10 % uniform",
                  lambda s: RewardSampler(s)))
    specs.append(("v-c", "(v-c) EPISODE CREDIT, sampled ∝ (mean credited reward of the last 20 + ε; untried 1.0 + ε), 10 % uniform",
                  lambda s: EpisodeCredit(s, sample=True)))
    specs.append(("v-c-argmax", "(v-c control) EPISODE CREDIT, argmax with rng ties, 10 % uniform",
                  lambda s: EpisodeCredit(s, sample=False)))
    return specs


def _summ(vals: Sequence[float]) -> Tuple[float, float]:
    return statistics.fmean(vals), (statistics.stdev(vals) if len(vals) > 1 else 0.0)


def cmd_arms(a) -> int:
    seeds = [int(s) for s in a.seeds.split(",")]
    out: Dict[str, object] = {"env": ENV_ID, "episodes": a.episodes, "seeds": seeds, "max_steps": MAX_STEPS,
                              "lag": "one step (the life's)", "arms": {}}
    print(f"[arms] {ENV_ID} · {a.episodes} episodes × seeds {seeds} · max_steps {MAX_STEPS} · the life's one-step lag")
    only = set(a.only.split(",")) if getattr(a, "only", None) else None
    for key, label, factory in arm_specs():
        if only is not None and key not in only:
            continue
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
    if only is not None and "ii" in arms:
        # the --only road (§5's further laws): each arm's difference from (ii) on the pooled episodes, nothing else
        pooled_ii = arms["ii"]["pooled_success"]
        out["vs_ii_pooled"] = {k: v["pooled_success"] - pooled_ii for k, v in arms.items() if k != "ii"}
        Path(a.out).write_text(json.dumps(out, indent=1))
        print(f"[arms] pooled differences from (ii): " + ", ".join(f"{k} {d:+.3f}" for k, d in out["vs_ii_pooled"].items()) + f"; wrote {a.out}")
        return 0
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


# ============================================================================================ ACT-EFFECT (docs/organism/act/PREREG-ACT-EFFECT.md)
# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:42 +0400 — PREREG-ACT-EFFECT PHASE 1 (signed at 1d55eab, co-signature line c465a7b): NEW classes and a NEW run path ONLY. `Ring`, `choose`, `run_game`, `FixedDist` and every landed arm
# above are untouched (tests/creature/test_a4l_explore_toy.py, the drift alarm, stays green). Everything here is the toy of the EFFECT law: an act's EFFECT is whether the frame the act
# produced differs from the previous one, known only for a SAME-EPISODE pair (the worker resets SILENTLY, so the first outcome after an episode's end crosses a reset and is UNKNOWN: it is
# the reset's effect, not the act's). The window is the act's last 20 KNOWN effects; fewer than 20 reads the optimism prior 1.0 (LIVE); an act is LIVE iff >= 4 of its last 20 changed
# the frame; the candidate draws uniformly over the live set after the landed 10 % uniform draw, TWO rng draws a choice in either branch (§3).
import dataclasses

EFFECT_N = 20                    # PREREG §3: the window of KNOWN effects
EFFECT_K = 4                     # live iff >= 4 changes of the last 20 (t = 0.2)
EFFECT_OPTIMISM = 1.0
NULL2_TAG = 0x6e756c32           # «nul2»: R-NULL2's independent stream
NOOP_ACTS = (3, 4, 5, 6)         # pickup, drop, toggle, done
RATE_WINDOW = 2000               # the ring's cap: the window a real Mind could read
RATE_EPS = 0.005
LOCK_SIZE, LOCK_FROM = 100, 120  # 100-act windows that start after act 120
LOCK_TOP2 = 0.90                 # AMENDMENT 2: the best TWO acts together hold >= 0.90 ...
LOCK_MAX_SHARE = 0.02            # ... in more than 2 % of a life's windows = a lock (persistent, not transient)
DEAL_SHIFT = 3                   # P-DEAL: live_dealt[a] = live[(a + 3) mod 7]


@dataclasses.dataclass
class Ctx:
    """What a REACTIVE arm may read at CHOICE time. Zero lag: the eye row carries the `sha` of the frame the last act produced, so the mind knows it before the outcome row arrives.
    `last_effect`: 1 the frame changed, 0 it did not, None UNKNOWN (an episode's first outcome, or the reset frame's choice). `last_novel`: 1 the frame's signature was unseen earlier in the episode."""
    last_act: Optional[int] = None
    last_effect: Optional[int] = None
    last_novel: Optional[int] = None


def effect_pairs(rows: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    """THE BOUNDARY RULE (M9) as a pure function over TAPE rows (the live tape reader and the mind's tracker obey the same rule). Keep the last two GAME eye rows' (episode, step, sha); an eye
    row whose (episode, step) equals the previous one's is a re-published step and is ignored. At an OUTCOME row the effect is KNOWN iff a previous eye row exists, the outcome is aligned to
    the last eye row (same episode and step) and that previous row is of the SAME episode; then 1 if the two `sha` differ, else 0. Otherwise None (never 0): the reason is printed."""
    out: List[Dict[str, object]] = []
    prev = cur = None
    for r in sorted(rows, key=lambda r: int(r["seq"])):
        m = r.get("meta") or {}
        if m.get("source") != "game":
            continue
        if r.get("sense") == "eye":
            key = (m.get("episode"), m.get("step"))
            if cur is not None and (cur[0], cur[1]) == key:
                continue                                   # a re-published step: never compare a frame with itself
            prev, cur = cur, (m.get("episode"), m.get("step"), r.get("sha"))
        elif r.get("sense") == "outcome":
            effect, why = None, ""
            if cur is None or prev is None:
                why = "no previous eye row"
            elif (m.get("episode"), m.get("step")) != (cur[0], cur[1]):
                why = "outcome not aligned to the last eye row"
            elif prev[0] != cur[0]:
                why = "episode boundary: the worker resets silently"
            else:
                effect = int(prev[2] != cur[2])
            out.append({"seq": int(r["seq"]), "act": m.get("act"), "effect": effect, "why": why})
    return out


class EffectTracker:
    """Per act: its last `n` KNOWN effects (the mind's `_recent_reflex_effects`) and the presence counts (known, excluded, total) printed beside every live/dead verdict (#168)."""

    def __init__(self, n: int = EFFECT_N, k: int = EFFECT_K, optimism: float = EFFECT_OPTIMISM):
        self.n, self.k, self.optimism = int(n), int(k), float(optimism)
        self._win: Dict[str, collections.deque] = {a: collections.deque(maxlen=self.n) for a in ACT_NAMES}
        self._known: collections.Counter = collections.Counter()
        self._excluded: collections.Counter = collections.Counter()
        self._total: collections.Counter = collections.Counter()

    def record(self, act: str, effect: Optional[int]) -> None:
        self._total[act] += 1
        if effect is None:
            self._excluded[act] += 1                       # EXCLUDED: never counted as 0
            return
        self._known[act] += 1
        self._win[act].append(int(effect))

    def rate(self, act: str) -> float:
        w = self._win[act]
        return self.optimism if len(w) < self.n else sum(w) / self.n

    def live(self, act: str) -> bool:
        w = self._win[act]
        return True if len(w) < self.n else sum(w) >= self.k

    def live_flags(self) -> List[bool]:
        return [self.live(a) for a in ACT_NAMES]

    def counts(self) -> Dict[str, Dict[str, int]]:
        return {a: {"known": self._known[a], "excluded": self._excluded[a], "total": self._total[a]} for a in ACT_NAMES}


class RewardWindow:
    """The last `cap` outcomes' (act, got), with per-act sums kept incrementally: what a real Mind could read from the 2,000-row ring."""

    def __init__(self, cap: int = RATE_WINDOW):
        self.cap = int(cap)
        self.q: collections.deque = collections.deque()
        self.sum = [0.0] * 7
        self.cnt = [0] * 7

    def add(self, act_idx: int, got: float) -> None:
        self.q.append((act_idx, float(got)))
        self.sum[act_idx] += float(got)
        self.cnt[act_idx] += 1
        if len(self.q) > self.cap:
            a, g = self.q.popleft()
            self.sum[a] -= g
            self.cnt[a] -= 1

    def mean(self, a: int) -> float:
        return max(0.0, self.sum[a] / self.cnt[a]) if self.cnt[a] else 0.0

    def total(self) -> int:
        return len(self.q)


def deal_flags(flags: Sequence[bool], shift: int = DEAL_SHIFT) -> List[bool]:
    """P-DEAL's plant: the live flags read through a cyclic shift — the effect DEALT to the wrong acts (#247 (1))."""
    return [bool(flags[(a + shift) % 7]) for a in range(7)]


def r_scr_probs() -> Dict[int, float]:
    """R-SCR: the candidate's own stationary mixture — the landed 10 % uniform draw plus uniform over {left, right, forward}."""
    p, q = (1.0 - EXPLORE) / 3.0 + EXPLORE / 7.0, EXPLORE / 7.0
    return {0: p, 1: p, 2: p, 3: q, 4: q, 5: q, 6: q}


class FixedDistTagged(FixedDist):
    """R-NULL2: the same fixed law as FixedDist on an INDEPENDENT rng stream (the null-vs-null distribution)."""
    label = "fixed-tagged"

    def __init__(self, seed: int, probs: Dict[int, float], tag: int):
        super().__init__(seed, probs)
        self.rng = np.random.default_rng([int(seed), int(tag)])


class _FxBase:
    """The effect arms' common body: the act rng (the mind's `_act_rng`), the effect tracker, the TWO draws a choice."""
    fx = True
    needs_ctx = True
    needs_frames = True
    label = "fx"

    def __init__(self, seed: int):
        self.rng = act_rng(seed)
        self.calls = 0
        self.explored = 0
        self.tracker = EffectTracker()
        self.live_history: List[List[bool]] = []

    def observe(self, act_name: str, got: float, effect: Optional[int], terminated: bool, truncated: bool) -> None:
        self.tracker.record(act_name, effect)

    def _pick(self, weights: Sequence[float]) -> int:
        """TWO draws: u; u < 0.1 -> integers(0, 7) (the landed floor, unchanged); else ONE random() against the running sum of the weights (all zero -> all one)."""
        self.calls += 1
        u = float(self.rng.random())
        if u < EXPLORE:
            self.explored += 1
            return int(self.rng.integers(0, 7))
        w = [float(x) for x in weights]
        if sum(w) <= 0.0:
            w = [1.0] * 7
        r = float(self.rng.random()) * sum(w)
        acc = 0.0
        for i, x in enumerate(w):
            acc += x
            if r < acc:
                return i
        return max(i for i, x in enumerate(w) if x > 0.0)


class ScreenChooser(_FxBase):
    """C-SCR, THE CANDIDATE (§3): uniform over the LIVE set (window 20, live iff >= 4 changes), after the landed 10 % draw."""
    label = "screen"

    def flags(self) -> List[bool]:
        return self.tracker.live_flags()

    def act(self, ring, ctx=None) -> int:
        fl = self.flags()
        self.live_history.append(list(fl))
        return self._pick([1.0 if f else 0.0 for f in fl])


class DealtScreen(ScreenChooser):
    """P-DEAL (§4): C-SCR with its live flags read through a cyclic shift of 3."""
    label = "dealt"

    def flags(self) -> List[bool]:
        return deal_flags(self.tracker.live_flags())


class PropChooser(_FxBase):
    """A-PROP: weight = the act's mean known effect over its last 20 (optimism 1.0 while it has fewer), sampled."""
    label = "effect-proportional"

    def act(self, ring, ctx=None) -> int:
        return self._pick([self.tracker.rate(a) for a in ACT_NAMES])


class EffectArgmax(_FxBase):
    """K-ARGMAX, THE PLANTED CONTROL: value = the mean known effect (as A-PROP), ARGMAX with rng ties (the landed `choose`): left and right both change the frame every time, tie at 1.0, and the
    tie is broken AT RANDOM — so it alternates between the two turns, holds neither above ~0.7 and never moves."""
    label = "effect-argmax"

    def act(self, ring, ctx=None) -> int:
        idx, explored = choose([self.tracker.rate(a) for a in ACT_NAMES], self.rng, 7)
        self.calls += 1
        self.explored += int(explored)
        return idx


class RateSampler(_FxBase):
    """A-RATE: weight = the mean reward over the last 2,000 outcomes + 0.005, sampled — the only state-blind signal that ranks forward first."""
    label = "reward-rate"

    def __init__(self, seed: int):
        super().__init__(seed)
        self.win = RewardWindow()

    def observe(self, act_name, got, effect, terminated, truncated) -> None:
        super().observe(act_name, got, effect, terminated, truncated)
        self.win.add(ACT_NAMES.index(act_name), got)

    def weights(self) -> List[float]:
        return [self.win.mean(a) + RATE_EPS for a in range(7)]

    def act(self, ring, ctx=None) -> int:
        return self._pick(self.weights())


class UCBChooser(_FxBase):
    """A-UCB, the count-based bonus: UCB1 on reward over the 2,000-outcome window (mean + sqrt(2 ln N / n_a), an untried act +inf), argmax with rng ties, the landed floor."""
    label = "ucb1"

    def __init__(self, seed: int):
        super().__init__(seed)
        self.win = RewardWindow()

    def observe(self, act_name, got, effect, terminated, truncated) -> None:
        super().observe(act_name, got, effect, terminated, truncated)
        self.win.add(ACT_NAMES.index(act_name), got)

    def values(self) -> List[float]:
        n_tot = max(1, self.win.total())
        return [float("inf") if self.win.cnt[a] == 0 else self.win.mean(a) + math.sqrt(2.0 * math.log(n_tot) / self.win.cnt[a]) for a in range(7)]

    def act(self, ring, ctx=None) -> int:
        idx, explored = choose(self.values(), self.rng, 7)
        self.calls += 1
        self.explored += int(explored)
        return idx


class BothChooser(RateSampler):
    """A-BOTH: weight = LIVE x (the 2,000-outcome mean reward + 0.005), sampled: the fast screen, then the slow reward ranking among the live acts."""
    label = "screen-x-reward"

    def weights(self) -> List[float]:
        return [(1.0 if f else 0.0) * (self.win.mean(a) + RATE_EPS) for a, f in enumerate(self.tracker.live_flags())]


class WSLS(_FxBase):
    """R-WSLS (class B, a REFERENCE that reads the TRUE live set {left, right, forward}): floor 0.1; else if the previous outcome was NOVEL repeat the previous act, else uniform over the live set.
    The second draw is consumed either way, so the stream's shape never depends on the rule."""
    label = "wsls"

    def act(self, ring, ctx=None) -> int:
        ctx = ctx or Ctx()
        self.calls += 1
        if float(self.rng.random()) < EXPLORE:
            self.explored += 1
            return int(self.rng.integers(0, 7))
        pick = int(self.rng.integers(0, 3))
        if ctx.last_novel == 1 and ctx.last_act in (0, 1, 2):
            return int(ctx.last_act)
        return pick


class WALK(_FxBase):
    """R-WALK (class B, reference, the TRUE live set): floor 0.1; else after a forward that did not change the frame (blocked) -> left or right; otherwise forward (after a moving forward,
    after a turn, at an episode start). The turn's side is the second draw, consumed either way."""
    label = "walk"

    def act(self, ring, ctx=None) -> int:
        ctx = ctx or Ctx()
        self.calls += 1
        if float(self.rng.random()) < EXPLORE:
            self.explored += 1
            return int(self.rng.integers(0, 7))
        side = int(self.rng.integers(0, 2))
        if ctx.last_act == 2 and ctx.last_effect == 0:
            return side
        return 2


def window_shares(acts: Sequence[int], start: int = LOCK_FROM, size: int = LOCK_SIZE) -> Tuple[np.ndarray, np.ndarray]:
    """For every `size`-act window that starts at act >= `start`: the share the best ONE act holds and the share the best TWO hold together (M2's detectors)."""
    a = np.asarray(acts, dtype=np.int64)
    h = len(a)
    if h < start + size:
        return np.zeros(0), np.zeros(0)
    onehot = np.zeros((h + 1, 7), dtype=np.int64)
    onehot[np.arange(1, h + 1), a] = 1
    cs = np.cumsum(onehot, axis=0)
    win = cs[start + size:h + 1] - cs[start:h + 1 - size]
    srt = np.sort(win, axis=1)
    return srt[:, -1] / float(size), (srt[:, -1] + srt[:, -2]) / float(size)


def lock_flagged_share(acts: Sequence[int]) -> float:
    """The share of a life's windows in which two acts together hold >= 0.90."""
    _t1, t2 = window_shares(acts)
    return float((t2 >= LOCK_TOP2 - 1e-9).mean()) if len(t2) else 0.0


def lock_pass(acts: Sequence[int]) -> bool:
    """M2 (AMENDMENT 2): a life PASSES when at most 2 % of its 100-act windows (from act 120) have two acts holding >= 0.90 — a lock is a PERSISTENT state."""
    return lock_flagged_share(acts) <= LOCK_MAX_SHARE + 1e-12


def noop_share(acts: Sequence[int], lo: int = 240, hi: int = 960) -> float:
    """M3: the share of {pickup, drop, toggle, done} over acts lo+1 .. hi."""
    seg = list(acts[lo:hi])
    return sum(1 for a in seg if a in NOOP_ACTS) / float(len(seg)) if seg else float("nan")


def m4_readings(live_history: Sequence[Sequence[bool]], lo: int = 240, hi: int = 960) -> Tuple[float, float]:
    """M4 from the chooser's OWN live flags over acts lo+1 .. hi: (a) the mean fraction of the four no-ops judged DEAD, (b) the fraction of choices with forward judged LIVE."""
    seg = list(live_history[lo:hi])
    if not seg:
        return float("nan"), float("nan")
    a = sum(sum(1 for i in NOOP_ACTS if not f[i]) / 4.0 for f in seg) / len(seg)
    b = sum(1 for f in seg if f[2]) / float(len(seg))
    return a, b


def _signature(obs) -> bytes:
    """A frame's identity: `obs["image"]` bytes (M8 proves that equal bytes <=> equal rendered POV `sha`)."""
    return obs["image"].tobytes()


def _call_act(policy, ring, ctx):
    return policy.act(ring, ctx) if getattr(policy, "needs_ctx", False) else policy.act(ring)


def run_game_fx(policy, base_seed: int, episodes: int, env_id: str = ENV_ID, keep_trace: int = 0,
                max_steps_total: Optional[int] = None, expected_max_steps: Optional[int] = MAX_STEPS) -> Dict[str, object]:
    """`run_game`'s loop (the worker's seed law, the life's one-step lag, success = terminated with reward > 0) PLUS the life's frame bookkeeping: the effect of the act just taken (a SAME-EPISODE pair of
    frame signatures; the first outcome after a silent reset is UNKNOWN), its novelty (unseen earlier in the episode), the reactive context handed to the NEXT choice (zero lag), and the outcome filed
    AFTER that choice (the lag). An arm without `needs_ctx`/`fx` runs exactly as it does under `run_game` (M7)."""
    if os.environ.get("BABYAI_DONE_ACTIONS"):
        raise SystemExit("BABYAI_DONE_ACTIONS is set: `done` would change the verifier (minigrid babyai verifier.py:26)")
    env = make_env(env_id)
    un = env.unwrapped
    ring = Ring()
    episode = 0
    obs, _info = quiet_reset(env, int(base_seed) + episode)
    env_max_steps = int(un.max_steps)
    if expected_max_steps is not None and env_max_steps != expected_max_steps:
        raise SystemExit(f"max_steps {env_max_steps} != {expected_max_steps} at episode {episode}")
    cur_sig = _signature(obs)
    seen = {cur_sig}                                       # episode 0's reset frame IS visible (the worker's first manifest)
    a = _call_act(policy, ring, Ctx())                     # the reset frame's eye row: the first choice
    per_ep: List[Tuple[int, float, bool, bool]] = []
    acts: List[int] = []
    trace: List[Dict[str, object]] = []
    ep_steps, ep_ret, step_total = 0, 0.0, 0
    first_after_reset = False
    t0 = time.perf_counter()
    while episode < episodes and (max_steps_total is None or step_total < max_steps_total):
        obs, r, te, tr, _info = env.step(a)
        step_total += 1
        ep_steps += 1
        ep_ret += float(r)
        acts.append(a)
        new_sig = _signature(obs)
        if first_after_reset:                              # the act landed on a reset state the mind never saw: the pair crosses the reset
            effect, novel = None, None
            seen = {new_sig}
            first_after_reset = False
        else:
            effect, novel = int(new_sig != cur_sig), int(new_sig not in seen)
            seen.add(new_sig)
        cur_sig = new_sig
        nxt = _call_act(policy, ring, Ctx(last_act=a, last_effect=effect, last_novel=novel))    # chosen BEFORE outcome t is filed
        ring.record(ACT_NAMES[a], float(r))
        if getattr(policy, "fx", False):
            policy.observe(ACT_NAMES[a], float(r), effect, bool(te), bool(tr))
        elif hasattr(policy, "observe"):
            policy.observe(ACT_NAMES[a], float(r), bool(te), bool(tr))                         # the landed (v-c) signature
        if len(trace) < keep_trace:
            trace.append({"act": ACT_NAMES[a], "act_idx": a, "got": float(r), "effect": effect, "novel": novel,
                          "terminated": bool(te), "truncated": bool(tr), "episode": episode, "step": step_total})
        if te or tr:
            per_ep.append((ep_steps, ep_ret, bool(te), bool(tr)))
            episode += 1
            ep_steps, ep_ret = 0, 0.0
            if episode < episodes:
                obs, _info = quiet_reset(env, int(base_seed) + episode)
                if expected_max_steps is not None and int(un.max_steps) != expected_max_steps:
                    raise SystemExit(f"max_steps {un.max_steps} != {expected_max_steps} at episode {episode}")
                first_after_reset = True
        a = nxt
    env.close()
    wall = time.perf_counter() - t0
    if not per_ep:
        per_ep.append((ep_steps, ep_ret, False, False))
    succ = [1 if (te and rew > 0) else 0 for (_s, rew, te, _tr) in per_ep]
    last100 = collections.Counter(ACT_NAMES[i] for i in acts[-100:])
    top_act, top_n = last100.most_common(1)[0]
    return {
        "episodes": len(per_ep), "successes": int(sum(succ)), "success_rate": sum(succ) / len(per_ep),
        "mean_steps": statistics.fmean(s for (s, _r, _te, _tr) in per_ep),
        "mean_reward": statistics.fmean(rw for (_s, rw, _te, _tr) in per_ep),
        "truncated": sum(1 for (_s, _r, _te, tr) in per_ep if tr), "steps": step_total,
        "last100": dict(last100.most_common()), "last100_top": [top_act, top_n],
        "explored_share": getattr(policy, "explored", 0) / max(1, getattr(policy, "calls", 1)),
        "wall_s": round(wall, 2), "acts": acts, "trace": trace, "env_max_steps": env_max_steps,
        "episode_ends": [i for i, t in enumerate(trace) if t["terminated"] or t["truncated"]] if keep_trace else [],
    }


def fx_arm_specs() -> Dict[str, Tuple[str, object]]:
    """key -> (label, factory(seed) -> policy): the NEW arms of PREREG-ACT-EFFECT §4, declared before any run."""
    uni7 = {i: 1.0 for i in range(7)}
    return {
        "R-NULL2": ("R-NULL2: uniform over 7 on an independent stream", lambda s: FixedDistTagged(s, uni7, NULL2_TAG)),
        "R-SCR": ("R-SCR: the candidate's own stationary mixture", lambda s: FixedDist(s, r_scr_probs())),
        "R-WSLS": ("R-WSLS (class B reference): stay while the frame is novel", lambda s: WSLS(s)),
        "R-WALK": ("R-WALK (class B reference): the persistent walker", lambda s: WALK(s)),
        "A-UCB": ("A-UCB: UCB1 on reward (the count-based bonus)", lambda s: UCBChooser(s)),
        "A-RATE": ("A-RATE: sampled by the 2,000-outcome reward rate", lambda s: RateSampler(s)),
        "C-SCR": ("C-SCR: the effect screen (THE CANDIDATE)", lambda s: ScreenChooser(s)),
        "A-PROP": ("A-PROP: sampled by the known effect rate", lambda s: PropChooser(s)),
        "A-BOTH": ("A-BOTH: live x reward rate", lambda s: BothChooser(s)),
        "K-ARGMAX": ("K-ARGMAX (planted control): argmax on the effect rate", lambda s: EffectArgmax(s)),
        "P-DEAL": ("P-DEAL (planted null): the live flags dealt to the wrong acts", lambda s: DealtScreen(s)),
    }


def landed_specs_fx() -> Dict[str, Tuple[str, object]]:
    """The landed arms the lives need, by the law's names: R-NULL (ii), R-3 (iii), P-OLD (i), A-VAL (v), A-SMP (v-b)."""
    sp = {k: f for k, _label, f in arm_specs()}
    return {"R-NULL": ("R-NULL: uniform over 7 (landed (ii))", sp["ii"]), "R-3": ("R-3: uniform over left, right, forward (landed (iii))", sp["iii"]),
            "P-OLD": ("P-OLD: the old chooser (landed (i))", sp["i"]), "A-VAL": ("A-VAL: the landed `ACT value reward 10; optimism 1` (v)", sp["v"]),
            "A-SMP": ("A-SMP: sampled by reward (landed (v-b))", sp["v-b"])}


def all_fx_specs() -> Dict[str, Tuple[str, object]]:
    out = dict(landed_specs_fx())
    out.update(fx_arm_specs())
    return out


def run_oracle(base_seed: int, episodes: int, env_id: str = ENV_ID) -> Dict[str, object]:
    """R-ORACLE: minigrid's BabyAIBot (the bracket 1.00): it reads the whole state."""
    from minigrid.utils.baby_ai_bot import BabyAIBot
    env = make_env(env_id)
    succ, lens = 0, []
    for e in range(int(episodes)):
        quiet_reset(env, int(base_seed) + e)
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
    return {"episodes": int(episodes), "successes": succ, "success_rate": succ / int(episodes), "mean_steps": statistics.fmean(lens), "max_steps": max(lens)}


# edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:44 +0400 — PREREG-ACT-EFFECT PHASE 1: the run commands of the effect bench (`bench-fx` §4/§5 M1, `lives-fx` M2–M4, `transfer` T1, `equiv` M8, `oracle` the bracket 1.00).
SEEDS12 = [LIFE_SEED + 1_000_000 * k for k in range(12)]      # §5: the unit is the SEED; layouts (reset seed s + episode) are paired across arms
LIVE_SET = [True, True, True, False, False, False, False]      # the TRUE live set of GoToLocal: left, right, forward


def _strip(r: Dict[str, object]) -> Dict[str, object]:
    for k in ("acts", "trace", "episode_ends"):
        r.pop(k, None)
    return r


def cmd_bench_fx(a) -> int:
    seeds = [int(s) for s in a.seeds.split(",")]
    specs = all_fx_specs()
    keys = a.arms.split(",") if a.arms else list(fx_arm_specs())
    out: Dict[str, object] = {"env": ENV_ID, "episodes": a.episodes, "seeds": seeds, "max_steps": MAX_STEPS, "lag": "one step (the life's)", "arms": {}}
    print(f"[bench-fx] {ENV_ID} · {a.episodes} episodes × {len(seeds)} seeds · arms {keys}", flush=True)
    for key in keys:
        label, factory = specs[key]
        runs = []
        for s in seeds:
            pol = factory(s)
            r = _strip(run_game_fx(pol, s, a.episodes))
            r["seed"] = s
            if hasattr(pol, "tracker"):
                r["effect_counts"] = pol.tracker.counts()
                r["final_rates"] = {n: round(pol.tracker.rate(n), 4) for n in ACT_NAMES}
                if getattr(pol, "live_history", None):
                    r["final_live_flags"] = pol.live_history[-1]
            runs.append(r)
            print(f"  {key:9s} seed {s}: success {r['success_rate']:.3f} ({r['successes']}/{r['episodes']}) steps {r['mean_steps']:.1f} last100 {r['last100_top']} ({r['wall_s']} s)", flush=True)
        rates = [r["success_rate"] for r in runs]
        out["arms"][key] = {"label": label, "runs": runs, "success_mean": statistics.fmean(rates), "success_sd": statistics.stdev(rates) if len(rates) > 1 else 0.0,
                            "per_seed": rates, "mean_steps": statistics.fmean(r["mean_steps"] for r in runs)}
        print(f"[bench-fx] {key}: mean {out['arms'][key]['success_mean']:.4f} ± {out['arms'][key]['success_sd']:.4f}", flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"[bench-fx] wrote {a.out}")
    return 0


def life_row(factory, seed: int, acts_n: int) -> Dict[str, object]:
    """One fresh life of `acts_n` game steps and every per-life reading the law's marks need (M2 at 960 and at acts_n, M3, M4, X2 printed)."""
    pol = factory(seed)
    r = run_game_fx(pol, seed, 10 ** 6, keep_trace=acts_n, max_steps_total=acts_n)
    acts, trace = r["acts"], r["trace"]
    row: Dict[str, object] = {"seed": seed, "steps": len(acts)}
    for h in sorted({960, acts_n}):
        pre = acts[:h]
        t1, t2 = window_shares(pre)
        row[f"h{h}"] = {"lock_flagged_share": lock_flagged_share(pre), "lock_pass": bool(lock_pass(pre)), "top1_max": float(t1.max()) if len(t1) else None,
                        "top2_max": float(t2.max()) if len(t2) else None, "single_act_flag_ge_0.8": bool(len(t1) and t1.max() >= 0.8),
                        "x1_pass_lt_0.5": bool(len(t1) and t1.max() < 0.5)}
    row["noop_share_241_960"] = noop_share(acts)
    ends = [t for t in trace if (t["terminated"] or t["truncated"])]
    in_x2 = [t for t in ends if 241 <= t["step"] <= 960]
    row["x2"] = {"episodes_241_960": len(in_x2), "successes_241_960": sum(1 for t in in_x2 if t["terminated"] and t["got"] > 0)}
    row["episodes_all"], row["successes_all"] = len(ends), sum(1 for t in ends if t["terminated"] and t["got"] > 0)
    hist = getattr(pol, "live_history", None)
    if hist and isinstance(pol, ScreenChooser):
        ma, mb = m4_readings(hist)
        seg = hist[240:960]
        row["m4a"], row["m4b"] = ma, mb
        row["exact_live_set_share_241_960"] = sum(1 for f in seg if f == LIVE_SET) / float(len(seg)) if seg else None
        run_len, first = 0, None
        for i, f in enumerate(hist):
            run_len = run_len + 1 if f == LIVE_SET else 0
            if run_len >= 60:
                first = i - 59
                break
        row["first_act_live_set_holds_60"] = first
        row["effect_counts"] = pol.tracker.counts()
    return row


def cmd_lives_fx(a) -> int:
    specs = all_fx_specs()
    out: Dict[str, object] = {"acts": a.acts, "n": a.n, "base": a.base, "arms": {}}
    for key in a.arms.split(","):
        label, factory = specs[key]
        rows = [life_row(factory, a.base + 1000 * i, a.acts) for i in range(a.n)]
        hs = sorted({960, a.acts})
        summ: Dict[str, object] = {}
        for h in hs:
            rr = [r[f"h{h}"] for r in rows]
            summ[f"h{h}"] = {"lock_pass_share": sum(1 for x in rr if x["lock_pass"]) / len(rr), "single_act_flag_share": sum(1 for x in rr if x["single_act_flag_ge_0.8"]) / len(rr),
                             "x1_pass_share": sum(1 for x in rr if x["x1_pass_lt_0.5"]) / len(rr),
                             "top2_max_median": statistics.median(x["top2_max"] for x in rr), "top1_max_median": statistics.median(x["top1_max"] for x in rr)}
        ns = [r["noop_share_241_960"] for r in rows]
        summ["noop_share"] = {"median": statistics.median(ns), "le_0.25_share": sum(1 for x in ns if x <= 0.25) / len(ns), "ge_0.5_share": sum(1 for x in ns if x >= 0.5) / len(ns)}
        if "m4a" in rows[0]:
            summ["m4a_ge_0.95_share"] = sum(1 for r in rows if r["m4a"] >= 0.95) / len(rows)
            summ["m4b_ge_0.95_share"] = sum(1 for r in rows if r["m4b"] >= 0.95) / len(rows)
            summ["m4a_median"], summ["m4b_median"] = statistics.median(r["m4a"] for r in rows), statistics.median(r["m4b"] for r in rows)
            summ["exact_set_median"] = statistics.median(r["exact_live_set_share_241_960"] for r in rows)
            firsts = [r["first_act_live_set_holds_60"] for r in rows if r["first_act_live_set_holds_60"] is not None]
            summ["latency_first_act_set_holds_60"] = {"lives_with_it": len(firsts), "median": statistics.median(firsts) if firsts else None}
        ep = [r["x2"]["episodes_241_960"] for r in rows]
        sc = [r["x2"]["successes_241_960"] / r["x2"]["episodes_241_960"] for r in rows if r["x2"]["episodes_241_960"]]
        summ["x2_printed"] = {"episodes_median": statistics.median(ep), "success_mean": statistics.fmean(sc) if sc else None}
        out["arms"][key] = {"label": label, "rows": rows, "summary": summ}
        locks = ", ".join(f"{h}: {summ[f'h{h}']['lock_pass_share']:.2f}" for h in hs)
        singles = ", ".join(f"{summ[f'h{h}']['single_act_flag_share']:.2f}" for h in hs)
        m4 = (f"M4a>=.95 {summ['m4a_ge_0.95_share']:.2f} M4b>=.95 {summ['m4b_ge_0.95_share']:.2f} latency {summ['latency_first_act_set_holds_60']}" if "m4a_ge_0.95_share" in summ else "")
        print(f"  {key:9s} lock-pass {locks} · single-act flag {singles} · no-op share median {summ['noop_share']['median']:.3f} (<=0.25: {summ['noop_share']['le_0.25_share']:.2f}) · {m4}", flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"[lives-fx] wrote {a.out}")
    return 0


def cmd_transfer(a) -> int:
    """T1 (printed, NO bar): BabyAI-OpenRedDoor-v0, where `toggle` is the winning act: R-NULL, R-3H (the GoToLocal hand rule «never toggle»), C-SCR, nothing re-tuned."""
    env_id = "BabyAI-OpenRedDoor-v0"
    seeds = [int(s) for s in a.seeds.split(",")]
    arms = {"R-NULL": lambda s: FixedDist(s, {i: 1.0 for i in range(7)}), "R-3H": lambda s: FixedDist(s, {0: 1.0, 1: 1.0, 2: 1.0}), "C-SCR": lambda s: ScreenChooser(s)}
    out: Dict[str, object] = {"env": env_id, "episodes": a.episodes, "seeds": seeds, "arms": {}}
    for key, factory in arms.items():
        runs = []
        for s in seeds:
            pol = factory(s)
            r = _strip(run_game_fx(pol, s, a.episodes, env_id=env_id, expected_max_steps=None))
            r["seed"] = s
            if isinstance(pol, ScreenChooser):
                r["effect_counts"] = pol.tracker.counts()
                r["final_rates"] = {n: round(pol.tracker.rate(n), 4) for n in ACT_NAMES}
                r["final_live_flags"] = pol.tracker.live_flags()
                r["toggle_live_at_end"] = pol.tracker.live("toggle")
            runs.append(r)
        rates = [r["success_rate"] for r in runs]
        out["arms"][key] = {"runs": runs, "per_seed": rates, "success_mean": statistics.fmean(rates), "success_sd": statistics.stdev(rates), "mean_steps": statistics.fmean(r["mean_steps"] for r in runs)}
        extra = f" · toggle LIVE at the end on {sum(1 for r in runs if r.get('toggle_live_at_end'))}/{len(runs)} seeds" if key == "C-SCR" else ""
        print(f"  T1 {key:7s}: success {out['arms'][key]['success_mean']:.4f} ± {out['arms'][key]['success_sd']:.4f} (per seed {[round(x, 3) for x in rates]}){extra}", flush=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    return 0


def cmd_equiv(a) -> int:
    """M8: `obs["image"]` bytes equal <=> the rendered POV's sha equal, between consecutive frames, on >= `a.steps` uniformly random steps (two levels)."""
    import hashlib
    import gymnasium as gym
    import minigrid  # noqa: F401
    rng = np.random.default_rng(20261003)
    steps = mism = changed = 0
    per_level = {}
    levels = ["BabyAI-GoToLocal-v0", "BabyAI-OpenRedDoor-v0"]
    for env_id in levels:
        env = gym.make(env_id, render_mode="rgb_array")
        n0, m0, c0, e = steps, mism, changed, 0
        while steps - n0 < a.steps // len(levels):
            obs, _ = quiet_reset(env, 500 + e)
            e += 1
            po = obs["image"].tobytes()
            pr = hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()
            while True:
                obs, _r, te, tr, _i = env.step(int(rng.integers(0, 7)))
                co = obs["image"].tobytes()
                cr = hashlib.sha256(env.unwrapped.get_pov_render(tile_size=32).tobytes()).hexdigest()
                mism += int((co == po) != (cr == pr))
                changed += int(co != po)
                steps += 1
                po, pr = co, cr
                if te or tr:
                    break
        env.close()
        per_level[env_id] = {"steps": steps - n0, "mismatches": mism - m0, "changed": changed - c0}
    res = {"steps": steps, "mismatches": mism, "changed": changed, "per_level": per_level, "pass": mism == 0 and steps >= a.steps}
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(f"[equiv] {json.dumps(res)}")
    return 0 if res["pass"] else 1


def cmd_oracle(a) -> int:
    seeds = [int(s) for s in a.seeds.split(",")]
    runs = [dict(run_oracle(s, a.episodes), seed=s) for s in seeds]
    rates = [r["success_rate"] for r in runs]
    out = {"env": ENV_ID, "episodes": a.episodes, "seeds": seeds, "runs": runs, "success_mean": statistics.fmean(rates), "mean_steps": statistics.fmean(r["mean_steps"] for r in runs)}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"[oracle] success {out['success_mean']:.4f} mean steps {out['mean_steps']:.2f} over {len(seeds)} seeds × {a.episodes}")
    return 0


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
    r.add_argument("--only", default=None, help="comma-separated arm keys (§5's further laws: ii,v-b,v-c,v-c-argmax)")
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
    # edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:44 +0400 — PREREG-ACT-EFFECT PHASE 1: the effect bench's subcommands (the landed five are untouched).
    seeds12 = ",".join(str(s) for s in SEEDS12)
    b = sub.add_parser("bench-fx")
    b.add_argument("--episodes", type=int, default=1000)
    b.add_argument("--seeds", default=seeds12)
    b.add_argument("--arms", default=None, help="comma-separated keys (default: the eleven NEW arms; the landed ones R-NULL,R-3,P-OLD,A-VAL,A-SMP are also accepted)")
    b.add_argument("--out", required=True)
    lf = sub.add_parser("lives-fx")
    lf.add_argument("--arms", default="R-NULL,R-3,P-OLD,A-VAL,A-RATE,C-SCR,A-BOTH,K-ARGMAX,P-DEAL")
    lf.add_argument("--n", type=int, default=50)
    lf.add_argument("--acts", type=int, default=4920)
    lf.add_argument("--base", type=int, default=30260923)
    lf.add_argument("--out", required=True)
    tr = sub.add_parser("transfer")
    tr.add_argument("--episodes", type=int, default=600)
    tr.add_argument("--seeds", default=seeds12)
    tr.add_argument("--out", required=True)
    eq = sub.add_parser("equiv")
    eq.add_argument("--steps", type=int, default=20000)
    eq.add_argument("--out", required=True)
    orc = sub.add_parser("oracle")
    orc.add_argument("--episodes", type=int, default=1000)
    orc.add_argument("--seeds", default=seeds12)
    orc.add_argument("--out", required=True)
    a = ap.parse_args(list(argv))
    return {"parity": cmd_parity, "calib": cmd_calib, "arms": cmd_arms, "lockseries": cmd_lockseries, "lives": cmd_lives,
            "bench-fx": cmd_bench_fx, "lives-fx": cmd_lives_fx, "transfer": cmd_transfer, "equiv": cmd_equiv, "oracle": cmd_oracle}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
