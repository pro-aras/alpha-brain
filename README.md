# Alpha 7 (`v3.2.0`) — Pure-Rust Embodied Cortical-Hippocampal & Unified Thermal-Conductive Brain

**Alpha 7** is a 100% pure-Rust embodied, bio-inspired cognitive architecture centered on a **Unified Self-Mutating Cortical Brain ([`src/unified_core_brain.rs`](src/unified_core_brain.rs))** inside a sparse dendritic neural fabric ([`src/fabric.rs`](src/fabric.rs)), verified by an **Immutable Constitutional Judge (`E0`–`E17`, 18/18 Exams Passed)** and tested live in **The Sovereign Crucible**:

1. **Unified Self-Mutating Cortical Brain & Narrow-Waist Firewall ([`src/unified_core_brain.rs`](src/unified_core_brain.rs)):**
   - **Zero-Organ Narrow-Waist Architecture (`Invariants I1–I6`):** `UnifiedCoreBrain` contains only `{fabric, genome, rng_state, fast_error_ema, slow_error_ema, homeostatic_social_drive}`—zero string lookup tables, zero external rule-caches, and zero readout shortcuts (`12` bytes of non-fabric parameters).
   - **Blind Log/Logit-Space Self-Mutation (`E8`):** 12 unconstrained real parameters $\mathbf{z} \in \mathbb{R}^{12}$ mutated strictly via blind Gaussian perturbation (`mutate_blind`) and selected by held-out empirical survival (`16/16` paired sign-test wins, `50% -> 100%` held-out generalization, `0%` under flagless synapse lesion).
   - **Homeostatic Social & Zeigarnik Uneasiness Speech Drive (`E7`):** Unprompted vocal motor emission (`VOCAL_MOTOR_START..66_256`) emerges endogenously when `homeostatic_social_drive` and cortical assembly uneasiness cross threshold (`0%` at low drive $\to$ `100%` at high drive, `97%` topic bias toward unresolved cortical assemblies).
2. **Commitment-Gated ~15 Hz Rivalry, Context-Rotated Mental Lines & The Sovereign Crucible (`E9`, `E10`, `E11`):**
   - **`E9` · Commitment-Gated ~15 Hz Conscious (`State 1`) vs. Suppressed (`State 2`) Alternation:** Alternates at ~15 Hz between an active conscious working hypothesis (`State 1`, `1.21x` gain, tuning slope `+0.95`, split-half EV `100%`) and a suppressed counterfactual detour hypothesis (`State 2`, `1.00x` gain, opponent slope `-0.78`, split-half EV `100%`), promoting `State 2` to `State 1` in **1 tick** when blocked (`██`).
   - **`E10` & `E11` · Context-Rotated Premotor Subspace Mental Lines & The Sovereign Crucible:** Learns a geometric mental line $\langle \boldsymbol{\zeta} \mid \text{item}\rangle$ from adjacent (`SD = 1`) pairs (`100%` zero-shot transitive inference in both `Context C+` and inverted `Context C-` vs. `0%` literal 1D collapse) and solves **all 4 disjoint solution ways (`4.0 / 4.0`)** in `LiveSovereignCrucibleEngine`.
3. **Pragmatic Role-Filler Intention Binding, Active Hypothesis Probing & ALife Autopoiesis (`E12`, `E13`, `E14`):**
   - **`E12` · Dendritic Role-Filler Pragmatic Intention Binding:** Distinguishes syntactic role-swap anagrams sharing identical words (`"what made you"` vs. `"what you made"`, `100%` vs. `0%` bag-of-words control) and multiplexes multi-clause questions (`100%`).
   - **`E13` · Active Epistemic Hypothesis Probing:** Driven by somatic uneasiness (`0.75 -> 0.04`), executes a 1-trial diagnostic probe to disambiguate 80%-overlapping candidate world laws before acting (`100%` vs. `50%` passive guesser).
   - **`E14` · ALife Autopoietic 50%-Stroke Self-Repair & Edge-of-Chaos Niche Co-Evolution:** Self-heals from a 50% cortical interneuron stroke (`100% -> 0% -> 100%` by sprouting `4.0` replacement interneurons from uncommitted reserve vs. `0%` static control) and masters `4.0 / 4.0` co-evolved stepping-stone niches.
4. **Continuous 4D Thermal-Chemical Field, Multi-Path Conductive Flux & Organic Learning Synergy (`E15`, `E16`, `E17`):**
   - **`E15` · Continuous 4D Thermal-Chemical Reaction Field & Affective Synonym Web:** Computes a continuous 4D vector $\mathbf{\Theta}_i = (\tau_{\text{exc}}, \tau_{\text{fric}}, \tau_{\text{warm}}, \tau_{\text{cold}})$ directly from neuron compartments (`100%` micro-input trajectory uniqueness vs. `12.5%` predefined `if/match` buckets; `100%` affective synonym & path routing accuracy vs. `50%` 1D scalar temperature and `33.3%` unbounded heat runaway).
   - **`E16` · Multi-Path Thermal Conductive Flux & Hybrid Bridge Synthesis:** Propagates continuous thermal potential across multiple paths (`3` simultaneous active paths) with non-linear conductance reinforcement ($\sigma_{uv}^{1.8}$) and friction back-pressure, overflowing `0.76` flux when the primary path heats up and synthesizing a novel **Multi-Path Hybrid Bridge (`0.69` flux vs. `0.001` single-path control)** when every individual path is blocked at a different hop.
   - **`E17` · Organic Learning, Teaching & Growth Synergy Matrix:** Head-to-head benchmark across a 4-stage unseen gauntlet comparing `M1` Passive Rote (`6.25%` unseen / `100%` seen), `M2` Conceptual Coaching (`31.25%`), `M3` Active Probing (`37.50%`), `M4` 4D Thermal Multi-Path Web (`43.75%`, Best Single Method), and `M5` Autopoietic Sleep Consolidation (`31.25%`) against `C1` (`50.0%`), `C2` (`75.0%`), and **`C3` Full Organic Synergy (`100.0%`, `+56.25%` synergy gain over the best single method, `0.0%` under flagless lesion)**.

## Quick Start

```bash
# Run the E0-E17 Unified Cortical Brain & Sovereign Crucible constitutional suite
cargo test --release test_phase18 -- --nocapture

# Run the full 24-test release verification suite
cargo test --release

# Launch the live Alpha 7 daemon
cargo run --release -- --daemon --live-dir /data/dev/alpha7/live
```
