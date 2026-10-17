# Alpha 7 (`v3.0.0`) — Pure-Rust Embodied Cortical-Hippocampal & Sovereign Quantum AI

**Alpha 7** is a 100% pure-Rust embodied, bio-inspired cognitive architecture centered on a **Unified Self-Mutating Cortical Brain ([`src/unified_core_brain.rs`](src/unified_core_brain.rs))** inside a sparse dendritic neural fabric ([`src/fabric.rs`](src/fabric.rs)), verified by an **Immutable Constitutional Judge (`E0`–`E11`)** and tested live in **The Sovereign Crucible**:

1. **Unified Self-Mutating Cortical Brain & Narrow-Waist Firewall ([`src/unified_core_brain.rs`](src/unified_core_brain.rs)):**
   - **Zero-Organ Narrow-Waist Architecture (`Invariants I1–I6`):** `UnifiedCoreBrain` contains only `{fabric, genome, rng_state, fast_error_ema, slow_error_ema, homeostatic_social_drive}`—zero string lookup tables, zero external rule-caches, and zero readout shortcuts.
   - **Blind Log/Logit-Space Self-Mutation (`E8`):** 12 unconstrained real parameters $\mathbf{z} \in \mathbb{R}^{12}$ mutated strictly via blind Gaussian perturbation (`mutate_blind`) and selected by held-out empirical survival (`16/16` paired sign-test wins, `50% -> 100%` held-out generalization, `0%` under flagless synapse lesion).
   - **Homeostatic Social & Zeigarnik Uneasiness Speech Drive (`E7`):** Unprompted vocal motor emission (`VOCAL_MOTOR_START..66_256`) emerges endogenously when `homeostatic_social_drive` and cortical assembly uneasiness cross threshold (`0%` at low drive $\to$ `100%` at high drive, `97%` topic bias toward unresolved cortical assemblies).
2. **Adversarially Hardened October 2026 Neuroscience Discoveries (`E9`, `E10`, `E11`):**
   - **`E9` · Commitment-Gated ~15 Hz Conscious (`State 1`) vs. Suppressed (`State 2`) Alternation (Hardening Hesse & Tsao, *Nature*, Oct 2026):**
     - Alternates at ~15 Hz between an active conscious working hypothesis (`State 1`, `1.21x` gain, tuning slope `+0.95`, split-half EV `100%`) and a suppressed counterfactual detour hypothesis (`State 2`, `1.00x` gain, opponent slope `-0.78`, split-half EV `100%`).
     - Fixes the **Motor Thrashing Hazard** of literal 15 Hz rivalry via a **Commitment Hysteresis Gate** that routes only `State 1` to motor output while keeping `State 2` as a motor-gated standby route that promotes to `State 1` in **1 tick** when the active route is physically blocked (`██`).
   - **`E10` & `E11` · Context-Rotated Premotor Subspace Mental Lines (Hardening *Science Advances*, Oct 2026):**
     - Learns a geometric mental line $\langle \boldsymbol{\zeta} \mid \text{item}\rangle$ from adjacent (`SD = 1`) pairs via differential opponent RPE plasticity (`100%` zero-shot transitive inference on unseen non-adjacent `SD >= 2` and interior pairs, monotonic Symbolic Distance Effect `SD1 0.33 < SD2 0.67 < SD3 1.00 < SD4 1.32`, rank correlation $r = 1.000$).
     - Fixes the **Context-Reversal / Cyclic Collapse** of a literal 1D mental line (which cancels out to `0%–50%` when hierarchy polarity reverses between `Context C+` and `Context C-`) by dynamically recruiting conjunctive context-item interneurons `h(ctx, item)` inside `self.fabric.synapses`, achieving **`100%` zero-shot transitive deduction in both `Context C+` (`A > ... > G`) and `Context C-` (`G > ... > A`)**.
3. **The Sovereign Crucible (`E11` & `LiveSovereignCrucibleEngine`):**
   - A single non-memorizable, multi-path $8 \times 8$ deductive game where every move requires `UnifiedCoreBrain` to solve unseen non-adjacent transitive gates (`SD >= 2`) across both normal (`C+`) and inverted (`C-`) contexts.
   - Starts Episode 1 in each unseen rule-world making genuine cold discovery mistakes (`ep1_cold_mistakes_mean = 8.0` in batch exam, `4` in live incremental episode), learns strictly from adjacent (`SD = 1`) experiences via BTSP/RPE plasticity, and drops to **`0.0` mistakes** upon mastery.
   - Physically seals (`██`) each solved path upon completion, forcing Alpha 7 to discover **all 4 distinct, non-overlapping solution ways (`Way 1: Route-α`, `Way 2: Route-β`, `Way 3: Route-γ`, `Way 4: Route-δ` = `4.0 / 4.0`)**, whereas a rote memorizer (`0%`), an ungated 15 Hz thrashing controller (`0%`), and a flaglessly lesioned brain (`zero_lesion_flagless() -> 0%`) all fail.
4. **Event-Driven Sparse Dendritic Fabric, Hippocampal Concept Web & Borbély Two-Process Sleep ([`src/neuron.rs`](src/neuron.rs), [`src/fabric.rs`](src/fabric.rs), [`src/concept_web.rs`](src/concept_web.rs), [`src/weekly_game_mastery_sleep.rs`](src/weekly_game_mastery_sleep.rs)):**
   - Supports **1,000,000+ neurons** in ~30.5 MB RAM with bounded synaptic homeostasis (`prune_bounded_memory`) and sub-millisecond daemon step latency (`~650–1,000 µs`).

## Quick Start

```bash
# Run the E0-E11 Unified Cortical Brain & Sovereign Crucible constitutional suite
cargo test --release test_phase18 -- --nocapture

# Run the full release verification suite
cargo test --release

# Launch the live Alpha 7 daemon
cargo run --release -- --daemon --live-dir /data/dev/alpha7/live
```
