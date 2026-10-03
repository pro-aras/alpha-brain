# PREREG-ACT-EFFECT — can the hands learn which acts DO anything? (the act chooser's next law)

*Written by Claude (Sonnet 5.5, swarm act) 2026-10-03 11:14 +0400. Branch `act-1003` off master `15445a3`, worktree `/data/dev/genome-wt-act-1003`. Renamed from the brief's «PREREG-ACT-FLOOR» on the seat's word (board 10:47 «ACT now tests an `ACT value effect …` chooser toy-first, built only if its bench admits it»; 10:5x «law renamed as you see fit»). Co-signature: the architect (Opus 5.5), added as a signature line only, after the last edit (#244 (6)). Lessons applied: #162 #168 #228 #244 #245 #246 #247 #250.*

## 0 · What is NOT claimed, and what has and has not run (read first)
1. **Not claimed: beating random-3.** random-3 (uniform over left, right, forward; 0.4339 on 12 seeds) is the FREE ABLATION of this law (#246 (1)): a fixed rule that drops the four acts that never change the frame. A chooser that learns only «which acts do something» can at best reach it. This law's claim is that the chooser REACHES that level BY LEARNING, from the visible consequence of its own acts, with no reward, no knowledge of the act names, and no lock. A claim above random-3's seed-wise p95 (0.459) belongs to a reactive or state-conditioned law (§1.6); this bench measures such arms only as references and alternatives and never admits them.
2. **Not claimed: success at the life's own N.** Hours 2–8 of an 8 h life hold ≈ 13 episodes; brain-long-2's 3.4 days hold 79. X2 is printed, no bar (A4L-EXPLORE REPORT §0.3).
3. **Not claimed: anything about brain-long-3.** The ladder: nothing built here enters it. Adopting the already-landed line `ACT value reward 10; optimism 1` at a later rung needs no code and is the seat's call; this law does not depend on it.
4. **What ran BEFORE this law was signed (disclosed, #244):** (a) the status-quo reproduction of the landed reference arms on the 12 seeds (i, ii, iii, iv ×4, v, v-b, v-c, v-c-argmax; 10:49–11:08; `data/statusquo-arms-12seeds.{json,log}`), the brief's item 2; its determinism check against the 09-23 record held (seed 20260923: 0.197, seed 21260923: 0.196, equal to the old rows to the digit); the drift alarm `tests/creature/test_a4l_explore_toy.py` read `Ran 12 … OK` (`data/toy-drift-15445a3.log`); (b) two orientation probes of WORLD FACTS under the NULL policy (uniform random) and one read of brain-long-2's tape (`orient/`); no candidate was evaluated in any of them. **The candidate, its alternatives, the plants and the new references have NOT run, and no harness code for them exists.** The +0.10 bar is A4L-EXPLORE §5's (09-23), not fitted to these rows.

## 1 · The record this law starts from
### 1.1 The collapse is real, and verified twice
- brain-long-2's genome (at `9f19879`) has one ACT line, `ACT glance open ask turn step say run`, and no `ACT value`: the OLD law. The verifier's second path (the world's own step files, not the journal; board 10:48:39): 4,929 applied acts, `right` 86.35 % overall and 0.90–0.94 in every 200-step window from step ≈ 600 (the locked expectation is 0.9 + 0.1/7 = 0.914); 3 rewards, all on `right` (episodes 5, 45, 54); **3 of 79 episodes = 0.038 against the random worker's 0.29 per episode, P(X ≤ 3 | Bin(79, 0.29)) = 1.05e-8**; `act_explored` 509 / 4,930 = 10.3 %. The CLAIMS lane (board 10:43:57) re-derived all 4,921 journalled weights from the outcome rows alone (max |diff| 0; a planted +0.05 caught) and found the PDF's vector `[0, 0.000423, 0, …]` at the 2,307th `right`.
- The mechanism (`creature/mind.py` `_record_reflex` + `_maybe_choose_act`): an act's weight is the mean surprise |got − its running mean| over its last 10 outcomes; 90 % argmax, 10 % uniform. After ONE reward on an act its running mean is r/k > 0 for ever, so every later unrewarded outcome of THAT act has surprise r/k while every never-rewarded act has exactly 0.0: the rewarded act wins the argmax for ever.
- **«Requires an ε floor» is false:** the floor exists (`if u < 0.1:` → uniform, `mind.py`; 10.3 % of choices). The defect is surprise used as value.
- On the toy, 12 seeds (`data/statusquo-arms-12seeds.json`): old chooser **0.1844 ± 0.0172** against random-7 **0.2720 ± 0.0150**; below the null on 12 of 12 seeds; 5,551 of 6,788 100-act blocks locked at ≥ 80.

### 1.2 What the 09-23 ladder already built and measured (reused, not rebuilt)
`ACT value reward <n>; optimism <f>` is in master, and ran for 8 h in vivo (ladder 2's `a4l2-act`: X1 PASS, max share 0.35 on `forward`; 6 of 17 episodes). It removes the lock and nothing more. On 12 seeds: (v) the landed line **0.2702 ± 0.0113** (−0.0018 against random-7; above it on 7 of 12 seeds); (v-b) sampled ∝ reward 0.2854 (+0.0134; 10 of 12); (v-c) episode credit 0.2726; (v-c-argmax) 0.1633 (it locks). None clears +0.10 (A4L-EXPLORE §6). The toy `tools/toys/act_chooser_toy.py` is a parity-pinned copy of the chooser: it reproduces alpha4-1's 711 outcomes act for act.

### 1.3 Why every value law sat at the null (the seat's question), from the world's own counts
Orientation probe 1 (`orient/probe_world_facts.json`: 32,565 uniform steps, 600 episodes, success 0.2717), reward per step: **forward 96/4,641 = 0.0207, right 37/4,734 = 0.0078, left 30/4,648 = 0.0065, pickup 0/4,746, drop 0/4,573, toggle 0/4,591, done 0/4,632** (`orient/prereg_numbers.txt`).
1. **A window of 10 sees a reward once per 48–155 uses.** It holds a reward 6.3 % (left), 7.5 % (right), 18.9 % (forward) of the time, so every value reads 0.0 in most choices; the tie-break is uniform; the landed law IS random-7 between rewards (A4L-EXPLORE §4.1), and a burst on one act after each reward.
2. **An ε of 0.05 (v-b) is 2–8× the signal it floors** (0.0065–0.0207 per step).
3. **A life is starved.** Uniform play pays 0.0050 rewards per step: 4.8 in a 960-act life, 24.6 in 4,920. Ranking forward over a turn at z = 3 needs 1,206 (left) – 1,549 (right) steps of EACH act, ≈ 3,600–4,600 acts: beyond an 8 h life, borderline in 3.4 days.
4. **Reward belongs to act SEQUENCES in a state** (turn until the target is ahead, then forward), not to an act; per-act marginals do not compose. The best STATIONARY mixture needs forward 0.5 though forward is only ≈ 2.9× more rewarded per step than a turn.
5. **An argmax cannot express a mixture** (§1.2), and the sampled laws gain nothing for the reasons 1–3.

### 1.4 The signal in hand: what each act DOES to the frame
Orientation probe 2 (`orient/probe_world_facts2.json`; same-episode pairs only; uniform play) and the live tape (`orient/tape_effect_rates.txt`; brain-long-2's closed days, 4,450 same-episode outcomes):

| act | P(frame changed), uniform play | P(frame NOVEL: sha unseen earlier in the episode) | changed, brain-long-2's own play |
|---|---|---|---|
| left | 1.000 | 0.487 | 98 / 98 |
| right | 1.000 | 0.490 | 3,836 / 3,836 |
| forward | 0.637 | 0.577 | 61 / 103 = 0.592 |
| pickup | 0.090 | 0.060 | 6 / 115 = 0.052 |
| drop | 0.071 | 0.044 | 2 / 110 = 0.018 |
| toggle | 0.027 | 0.027 | 1 / 103 = 0.010 |
| done | 0.000 | 0.000 | 0 / 85 |

- **Presence (#168):** the tape row's `sha` is on 4,524 of 4,524 game eye rows; 0 duplicate (episode, step) eye rows; 4,523 game outcome rows, each with a previous eye row.
- **The episode boundary.** The worker resets SILENTLY: the act chosen on a terminal frame is applied to the NEW episode's reset state, a state the mind never saw, and the frame that results differs from the terminal one whatever the act. That outcome's effect is UNKNOWN (never 0, never 1). 73 of 4,523 live outcomes (1.6 %) and 597 of 32,565 uniform steps (1.8 %) are such. My first live reader did not exclude them and read `done` 1/86 changed, an artefact; with the rule `done` reads 0/85.
- **The separation:** the lowest live-act rate (0.637 / 0.592 live) over the highest dead-act rate (0.090 / 0.052): a factor of 7.1 and 11.4, no overlap in either record.
- **The order is the WRONG one for a ranking.** Raw change ranks turn (1.00) above forward (0.64) — the opposite of the reward ranking — so an ARGMAX on raw change locks on a turn: the spin again by a better-sounding signal. This law therefore never ranks by change: it only splits acts into LIVE and DEAD (§3); K-ARGMAX (§4) is the planted proof. Novelty ranks forward first (0.577 vs 0.49) but only 1.18×: too flat for a stationary sampler to reach forward 0.5. Count-based novelty (Strehl & Littman 2008; Bellemare et al. 2016) and Schmidhuber's compression progress (the TOYS lane's bench) are the lineage of the reactive references R-WSLS / R-WALK below; no mechanism is borrowed silently.

### 1.5 The brackets
Stationary state-blind ceiling **0.4878 ± 0.0189** (iv-0.5: forward 0.5, left = right = 0.25; 12 seeds; **class A only**). random-3 **0.4339 ± 0.0150**. random-7 **0.2720 ± 0.0150**. The oracle (`minigrid.utils.baby_ai_bot.BabyAIBot`, 100 episodes, seed 20260923; probe 1): **success 1.00, mean 5.71 steps (max 19)** against 54.3 steps for random play: the headroom above 0.4878 is the whole of state.

### 1.6 What a state-conditioned chooser would need, and why it is not this rung (one paragraph)
The oracle needs 5.7 steps where random play needs 54 because success is facing the target and the target's bearing is in the frame; no chooser that does not read the frame can pass 0.4878. A chooser conditioned on what the eye sees would need (a) the target's identity — the mission's colour and object words, which the ear already delivers as two rows; (b) the bearing of what those words name in the CURRENT frame, read from the organism's own glances and the cell the word is bound to — an interface that exists inside `Mind._consume_eye` (the word's best sight cell) but that the chooser, which reads only the outcome ring, has never used; (c) a map from bearing to act, innate (a drive) or learned from reward at ≈ 0.005 rewards per step, i.e. ≥ 10³ acts per state class; and (d) an instrument that can judge it, which a replay cannot (the tape fixes the world's answers), so only the standalone game can. It is not this rung because it is a cross-organ seam (eye ↔ word ↔ hands) with its own gene and its own null (the bearing must come from the organism's cells, not from the game's symbols), and its prerequisite is unmeasured: whether the organism's cells localise a named game object at all — a read-only study on stored frames that should come first. This law touches no eye, reads only the tape's `sha`, and stays in class A.

## 2 · The question, and the two phases
**Question.** Starting from the old law (0.184) and the landed line (0.270), both at or below the null (0.272): can a chooser that reads only the visible consequence of its own acts reach the free ablation's level (random-3, 0.434) by learning — and never lock?
- **Phase 1 — the bench** (standalone game, ≥ 10 seeds): NEW classes and a NEW run path only in `tools/toys/act_chooser_toy.py` (`Ring`, `choose`, `run_game` and every landed arm untouched; the drift alarm stays green). Admission rule: §7.
- **Phase 2 — the build** (only if admitted): the genome form, a parser hunk, the registry rows, the mind's chooser (§10).

## 3 · The candidate, exactly (C-SCR: «effect screen»)
**Effect (defined at the OUTCOME row of a game act).** The mind keeps the last two GAME eye rows' `(episode, step, sha)`; an eye row whose `(episode, step)` equals the previous one's is a re-published step and is ignored. At an outcome row, `effect` is **known** iff the previous eye row exists and belongs to the SAME episode as the outcome's own eye row; then `effect = 1` if the two `sha` differ, else `0`. Otherwise it is **unknown** (the first outcome after an episode boundary, after a snapshot that did not carry the pair, at a life's start): excluded from every window, never counted as 0. It reaches the chooser one outcome late, like reward (the life's lag).
**Live set.** For each act, its window = its last **n = 10** outcomes WITH A KNOWN EFFECT. An act with fewer than n such outcomes reads the optimism prior **1.0** (it is LIVE: no act is judged on fewer than ten outcomes). Otherwise it is LIVE iff mean(window) ≥ **t = 0.3**, DEAD else.
**Choice.** Exactly TWO act-rng draws every choice: `u = rng.random()`; if `u < 0.1` → `rng.integers(0, 7)` (the landed 10 % uniform branch, unchanged — it keeps every dead act reachable, so the live set can revive); else weights `w_a = 1.0` if LIVE else `0.0` (all dead → all 1.0: uniform), `r = rng.random() × Σw`, the first act whose running sum exceeds `r`.
**Parameters, declared and never swept:** n = 10, optimism = 1.0, t = 0.3, floor 0.1 (landed). **Genome form (Phase 2):** `ACT value effect <n>; optimism <f>; live <t>` (refused by name when `optimism < live`, a window below 1, or any mis-spelling). The journal's `act` row says `policy: "effect-screened"` and its `weights` are the 0/1 weights used.
**Reads only:** the outcome ring and the previous game eye row's `(episode, step, sha)`. **Class A** (a stationary state-blind mixture whose support moves slowly with learned per-act statistics): its own stationary mixture is R-SCR (§4), and the class ceiling 0.4878 applies.
**Scope (stated assumption).** The law is for worlds whose reward does not require an act without a visible consequence. With `BABYAI_DONE_ACTIONS` set, `done` is required for success and the screen would kill it; the toy refuses that flag (as the landed toy does) and a genome declares the line per world.

## 4 · The bench: arms, classes, ceilings
Class A = stationary state-blind (the class ceiling 0.4878 applies, never to B or C). **Class B = reactive** (the choice depends on the last outcome inside the episode): **0.4878 does NOT apply, no ceiling is known, the references measure one**. Class C = reads frame content (only the oracle).

| key | arm | class | role · ceiling that applies |
|---|---|---|---|
| R-NULL | (ii) uniform over 7 | A | THE NULL: 12 per-seed values (landed) |
| R-NULL2 | the same law, an independent rng stream (tag 0x6e756c32) | A | the null-vs-null distribution (what «no difference» looks like) |
| R-3 | (iii) uniform over left, right, forward | A | the candidate's FREE ABLATION (#246 (1)); printed beside every arm |
| R-CEIL | (iv-0.5) forward 0.5, left = right = 0.25 | A | the stationary state-blind ceiling 0.4878 |
| R-SCR | NEW fixed: left = right = forward = 0.3143, each no-op 0.0143 | A | the candidate's OWN stationary mixture (§3's floor included): its tight ceiling |
| R-ORACLE | `BabyAIBot` | C | the bracket 1.00 |
| R-WSLS | NEW hand-coded, reads the TRUE live set {left, right, forward}: floor 0.1; else if the previous outcome was NOVEL (sha unseen earlier in the episode) repeat the previous act, else uniform over {left, right, forward} | B | prices reactivity on novelty given a perfect screen; reference only |
| R-WALK | NEW hand-coded, same live set: floor 0.1; else after a forward that changed the frame → forward; after a forward that did not (blocked) → left or right (uniform); after a turn → forward; episode start → forward | B | the persistent walker; reference only |
| P-OLD | (i) the old chooser | A | PLANTED CONTROL: must lock (§5 M2) |
| A-VAL | (v) `ACT value reward 10; optimism 1`, the landed line | A | alternative: optimistic initial values; costs no code |
| A-SMP | (v-b) sampled ∝ reward (ε 0.05) | A | alternative: the softmax-floor family (landed in the toy) |
| A-UCB | NEW: UCB1 on reward over the ring's 2,000-outcome window: mean + √(2 ln N / n_a), an untried act +∞, argmax with rng ties; floor 0.1 | A | alternative: the count-based bonus |
| A-RATE | NEW: weight = mean reward over the 2,000-outcome window + 0.005, sampled ∝ weight; floor 0.1 | A | alternative: the only state-blind signal that ranks forward FIRST; power at 1,000 episodes is itself a result |
| **C-SCR** | **§3** | A | **THE CANDIDATE** |
| A-PROP | NEW: weight = mean known effect over the last 10 (10 outcomes else 1.0), sampled ∝ weight | A | alternative: the smooth form (forward-poor by arithmetic: 0.64 against 1.0) |
| A-BOTH | NEW: weight = LIVE × (mean reward over the 2,000-outcome window + 0.005), sampled | A | alternative: fast screen + slow reward ranking; the natural NEXT rung, not built here |
| K-ARGMAX | NEW control: value = mean known effect (as A-PROP), argmax with rng ties | A | PLANTED: must LOCK on a turn (the lock detector must catch it) |
| P-DEAL | NEW plant: C-SCR with the live flags read through a cyclic shift of 3 (`live_dealt[a] = live[(a+3) mod 7]`) | A | PLANTED null (#247 (1)): the effect dealt to the wrong acts; must not beat the null |

**Common to every effect arm:** the harness mirrors the life exactly: the one-step lag; the silent reset; the effect known only for same-episode pairs; `max_steps` asserted 64; `BABYAI_DONE_ACTIONS` refused. The signal is computed from `obs["image"]` bytes if M8 proves it equivalent to the rendered POV's `sha`, else from the render (×4.5 cost).

## 5 · Marks, bars, nulls, plants
**The unit is the SEED** (#244 (2); episodes inside a seed share one learning chooser and are not independent). 12 seeds: `s_k = 20260923 + 1,000,000 k`, k = 0..11; per seed, per arm, success per episode over 1,000 episodes; layouts are paired across arms (reset seed `s + episode`). Tests are over the 12 seed-level values.
**The null, as a distribution (printed before the run, from the landed rows):** R-NULL per seed `[0.274, 0.293, 0.267, 0.251, 0.264, 0.265, 0.279, 0.264, 0.256, 0.304, 0.279, 0.268]`: mean 0.2720, SD 0.0150, max 0.304, normal p95 0.297. R-3: mean 0.4339, SD 0.0150, max 0.458, normal p95 0.459. SD of the paired seed-wise differences against R-NULL: R-3 0.0156, R-CEIL 0.0211, A-VAL 0.0197, A-SMP 0.0154. **Smallest detectable seed-level gap** (paired t, 12 seeds, p < 0.001 one-sided, t = 4.437): **0.020–0.027** (`orient/prereg_numbers.txt`); the +0.10 bar is 3.7× the largest. R-NULL2 − R-NULL (12 paired differences) is printed; the bar must exceed 5 SD of it.

| mark | what it reads | bar | ceiling / null beside it |
|---|---|---|---|
| **M1** SUCCESS (graded; C-SCR) | mean over 12 seeds of success per episode | (a) ≥ R-NULL mean **+ 0.10**; (b) ≥ 11 of 12 seeds above R-NULL (sign test P(≥ 11 of 12) = 0.0032; 12 of 12 = 0.00024); (c) paired t over seeds, p < 0.001; (d) ≥ R-SCR **− 0.03** (it reaches its own stationary ceiling by learning) | R-SCR (its ceiling), R-3 (the free ablation), R-CEIL 0.4878, R-ORACLE 1.00 printed; C-SCR − R-3 printed with its position against R-3's seed-wise p95 (0.459) — NOT graded (§0.1) |
| **M2** LOCK (graded) | 50 fresh lives of 4,920 acts (seeds `30260923 + 1,000 i`), at the 960-act prefix and the full 4,920: the largest share one act holds in any 100-act window after act 120 | C-SCR: < 0.80 in ≥ 95 % of lives, at both horizons. **P-OLD and K-ARGMAX: ≤ 5 % of lives pass** (the detector CATCHES them). X1's 0.5 is printed, not graded: random-3's own lives pass it only 43 of 50 (09-23) because a 3-act mixture sits at its edge (#228 (b)) | P-OLD's 09-23 lives read 0.94–0.99 |
| **M3** NO-OPS (graded, only jointly with M2 and M1) | share of {pickup, drop, toggle, done} over acts 241–960 | C-SCR ≤ 0.25 in ≥ 95 % of lives | null 0.571; the floor's own minimum 0.1 × 4/7 = **0.057**. **The OLD law passes M3 alone (it spins `right`: 0.057), so M3 proves nothing without M2 and M1: an ablated system — the lock — passes the mark without the thing it tests (#246 (1))** |
| **M4** LEARNED SET (graded; C-SCR) | the chooser's own live flags from act 241 to 960: (a) the mean fraction of the four no-op acts judged DEAD; (b) the fraction of choices with `forward` judged LIVE | (a) ≥ 0.90 and (b) ≥ 0.95, each in ≥ 90 % of lives | ceilings from §1.4's rates and n = 10: (a) 0.979, (b) 0.994 (`prereg_numbers.txt`) |
| **M5** PLANTS (graded) | P-DEAL; K-ARGMAX; P-OLD | P-DEAL: mean ≤ R-NULL + 0.02 AND no-op share ≥ 0.5 in ≥ 50 % of lives (it must read as a FAIL of M3); K-ARGMAX and P-OLD: M2 pass share ≤ 5 %. A plant not caught = the instrument is wrong: fix and AMEND, never ignore | the plants assert they changed the bytes (the dealt flags differ from the true flags on ≥ 4 of 7 acts) |
| **M6** ABLATION (unit test) | C-SCR with every effect constant (all 1; all 0) | the draw is uniform over the 7 acts: each act's count over 70,000 choices within 4 SE of 1/7. «No signal» = R-NULL by construction | — |
| **M7** DETERMINISM (graded) | R-NULL re-run through the new frame-aware path; C-SCR twice | per-seed totals EXACTLY equal the landed harness' (rendering/obs never moves a draw); C-SCR twice identical | — |
| **M8** EQUIVALENCE (graded) | `obs["image"]` bytes equal ⟺ rendered POV `sha` equal, on ≥ 20,000 random steps | 0 exceptions; any counterexample → the bench renders | — |
Printed, no bar: X2 per life with its null bound (acts 241–960 hold ≈ 13 episodes, 09-23 record); success per episode on the lives; every arm's last-100 census; the live-set time series; the first act from which the live set holds for 60 consecutive choices (median over lives). Every «0 of N» prints its presence count; every reader carries a planted control that asserts it changed the bytes.

## 6 · Predictions (written before any candidate ran)
| arm | prediction | tag |
|---|---|---|
| R-SCR | 0.41–0.43: random-3's 0.434 less the 5.7 % of steps spent on no-ops (≈ −0.01 to −0.02) | [Likely] |
| **C-SCR** | 0.40–0.42, within 0.01 of R-SCR: a ≈ 100-act startup (every act needs 10 outcomes: mean 102, p5–p95 83–131 under uniform choice) of 55,000 acts per seed; wrongly dead `forward` 0.6 % of evaluations, wrongly live `pickup` 5.4 % and `drop` 2.9 % (`prereg_numbers.txt`). **M1: +0.13 to +0.15 against the bar +0.10 → PASS** | [Likely] |
| C-SCR − R-3 | −0.02 ± 0.01: it will NOT clear R-3's p95, and is not asked to | [Likely] |
| A-PROP | 0.37–0.40 (forward 0.22, turns 0.33 each, no-ops 0.12): below C-SCR, may miss +0.10 | [Likely] |
| A-VAL / A-SMP | 0.270 / 0.285 (the rows above) | [Certain] |
| A-UCB | at the null, 0.27 ± 0.02 (a bonus on a sparse reward is a round-robin) | [Likely] |
| A-RATE | 0.30–0.45 at 1,000 episodes (it concentrates on forward once ≈ 10 rewards per act are seen, ≈ 3,000–10,000 acts) but ≈ the null at the 960-act horizon and 0.28–0.33 at 4,920 acts: a reward-rate law is starved at life scale | [Guessing] bench scale; [Likely] life scale |
| A-BOTH | ≥ C-SCR at bench scale (0.43–0.47); ≈ C-SCR at life scale | [Guessing] |
| K-ARGMAX | locks on a turn: M2 pass ≤ 5 %, success 0.05–0.20 | [Likely] |
| P-DEAL | ≤ 0.15 (it mostly plays drop, toggle, done) | [Likely] |
| R-WSLS, R-WALK | unknown, 0.40–0.65: their purpose is to put a number on class-B headroom | [Guessing] |
| R-ORACLE | 1.00 | [Certain] |
| M2 / M3 / M4 | C-SCR passes all three: the largest 100-window share of a 3-act mixture ≈ 0.40–0.45 (SD 0.046 a window); no-op share ≈ 0.06–0.08 | [Likely] |

## 7 · Admission, and what each outcome does
- **ADMIT → Phase 2** iff M1(a–d) ∧ M2 ∧ M3 ∧ M4 ∧ M5 ∧ M6 ∧ M7 ∧ M8 hold for C-SCR.
- **Otherwise REFUSED BY THE BENCH:** no build; the numbers are the deliverable. The cause is read before anything else (RULES §2): an instrument or code cause → a written AMENDMENT naming it, and a re-run; a mechanism cause → a result, and the next try is a NEW law.
- **An alternative never substitutes for a refused candidate.** If an alternative clears bars the candidate fails, that is a finding that needs its own law. If A-BOTH or a class-B reference clears R-3's seed-wise p95 it is reported as the next law's case, not built.
- M1 passing with M4 failing is NOT admitted (success without the learned pairing). Plants not caught → the bench is void until fixed by amendment.
- Admission launches nothing: the seat decides the rung (the ladder law).

## 8 · Adversarial walk (counted against the record)
1. **Where can it fire?** Every game outcome row with a same-episode previous frame: brain-long-2's tape holds 4,523 outcomes, `sha` on 4,524/4,524 game eye rows, 0 duplicates, 0 outcomes without a previous eye row, 73 boundary outcomes excluded → 4,450 carry a known effect. It fires on every one.
2. **The boundary rule is load-bearing:** without it `done` reads 1/86 on the live tape (§1.4); with it 0/85 (W2 of the bench's unit test plants a terminal-then-reset pair that must read UNKNOWN and fails if the exclusion is removed).
3. **Ablated systems.** M1's: R-3 (free; printed, never beaten by claim) and constant effect (= R-NULL by construction, M6). M3's: the lock (the old law passes M3 alone: stated, M3 conjunctive). M4's: P-DEAL (the learned set is wrong by construction).
4. **Raw change is maximised by turning:** C-SCR never ranks, it splits and draws uniformly among live acts; K-ARGMAX proves what ranking would do.
5. **The lag and the window.** The effect of act t is filed at outcome t, after the choice of act t+1; no act is judged on fewer than 10 known outcomes; the first choice that can drop an act comes after ≈ 100 acts (§6).
6. **Wrongly dead / wrongly live** (`prereg_numbers.txt`, window 10, t = 0.3): `forward` is judged dead at 0.6 % of evaluations (the 10 % draw revives it: 1.43 % per act per choice); `pickup` live at 5.4 %, `drop` 2.9 %, `toggle` 0.2 %, `done` 0 %. M4's ceilings (0.979, 0.994) are computed from these, so its bars are not above them.
7. **State that must survive a resume (#250).** The previous game eye row `(episode, step, sha)` is part of the chooser's state; if it is not persisted, the first outcome after a resume becomes UNKNOWN in the live run and KNOWN in a full replay, and the journals part. Phase 2 persists it and tests a resumed life against an uninterrupted one.
8. **Replay.** A replay of a closed tape under the line follows the tape's recorded acts: a changed choice parts at the first act (the tape twin reads the first differing choice and `act_mismatch`, as for the landed law). Phase 2's identity clause is for the line ABSENT.
9. **A world where the winning act has no visible effect** (`BABYAI_DONE_ACTIONS`): the screen would kill it — §3's scope, refused by the toy.
10. **A frozen frame** (every effect 0): all dead → uniform = R-NULL; the law's worst case is the null (outside item 9).
11. **Seeds are the unit;** layouts are paired; the sign test, the t test and every SD are over 12 seed-level values.
12. **Counting every «first / every / by N».** «every outcome» (item 1); «the first 10 outcomes» (≈ 102 acts); «acts 241–960» (720 choices, after the startup's p95 of 131); «≥ 95 % of 50 lives» = 48 lives (a bar that tolerates 2); «12 seeds» = 12 values; the 4,920-act horizon = brain-long-2's own game length.

## 9 · Price
Phase 1: the 12 NEW seed-runs ≈ 10–15 s each (≈ 14 arms × 12 seeds ≈ 35–40 CPU-min), the 50 lives × 9 arms × 4,920 acts ≈ 7 CPU-min, the oracle ≈ 1 min: **≈ 45 CPU-min** (×≈ 2 for the effect arms if M8 forces rendering). One slot, nice 10, through `slot`; at most 3 in parallel. Phase 2: genome suite ≈ 80 s, tools suite, targeted tests ≈ 1 min, the creature suite ≈ 25–30 min twice: **≈ 70 CPU-min**. The pinned-file protocol (§10) costs the integrator one cache redraw and identity check for ACT and SLEEP together.

## 10 · Phase 2 (only if admitted): test-first
1. **Grammar** (`genome/machinery.py`, ONE parser hunk beside the landed `ACT value reward` branch, in its own hunk): `ACT value effect <n>; optimism <f>; live <t>` → `declared["ACT_VALUE"] = {"law": "effect", "window", "optimism", "live"}`; the `reward` form stays byte-identical; refusals NAME «ACT value» (a mis-spelling, a window < 1, `optimism < live`). **`genome/machinery.py` is in `brain/scene/cache.py:WORLD_CODE`: every scene cache is refused after this edit.** I run only the targeted tests meanwhile and NAME every suite test that refuses a cache because of the pin (expected, not failures); the ONE redraw + `tools/brain/diag/cache_identity.py` is the integrator's, with SLEEP's.
2. **Registry** (`creature/genes.py`): the `ACT_VALUE` RUNS text names the effect law; BOUNDS exclusion `ACT_VALUE.live` with its reason; `tests/creature/test_refusal.py`'s sample clause.
3. **Mind** (`creature/mind.py`): the game-eye tracker (the pair, dedup, same-episode rule); the effect filed in the outcome ring row (x_s slots, a «known» flag beside the bit, so unknown is never 0); `_recent_reflex_effects`; the chooser branch (`law == "effect"`); the pair persisted in the snapshot ledger only when the line is declared; STATUS `act_policy: "effect-screened"`.
4. **Tests, RED first, each with a planted control:** grammar + refusals; the toy's `EffectTracker` equal to the real Mind's flags on a planted row sequence (nonzero: all four no-ops dead after 10 outcomes each; a terminal-then-reset pair UNKNOWN; a duplicate eye row ignored); **identity: the line ABSENT → the hour-1 fixture replay and a closed-life tape replay byte-identical to master's, `hash` included**; replay determinism twice; **resume identity (a snapshot mid-life, resumed, equals the uninterrupted journal)**; stand-ins: every `class Fake`/mock/twin of the Mind grepped before the edit (#235, #248 (3)).
5. **Suites:** `genome`, `tools`, `creature`, from the worktree root, logs and exit files under `scratch/`, the `Ran N … OK` line read from the file (#191).
6. Commit on `act-1003` only, gated on every captured exit code; READY-FOR-VERIFY with the sha, the commands and the logs; the final sha to the integrator after the verifier's VERIFIED.

## 11 · Signatures
- Author: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:14 +0400.
- Architect (Opus 5.5): — pending (a signature line, added after the last edit).
- The seat's go for the direction: board 10:47 and 10:5x; the seat's signature line is the seat's to add.

*(edit: Claude (Sonnet 5.5, swarm act), 2026-10-03 11:14 +0400 — the law written; every figure above is read from `orient/prereg_numbers.txt`, `orient/*.json`, `data/statusquo-arms-12seeds.json` or the board post it names.)*
