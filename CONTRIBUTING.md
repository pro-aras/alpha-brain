# Contributing to Alpha 7

Thank you for your interest in **Alpha 7 (`v3.2.0`)**! This repository is designed to be 100% self-contained, reproducible, and extensible on any Linux, macOS, or Windows machine with a standard Rust toolchain (`cargo`).

---

## Core Architectural Principles (The 6 Laws & Narrow-Waist Firewall)

When contributing new cortical mechanisms, sensory transducers, or benchmark tasks, please adhere to the project's foundational verification rules:

1. **Zero Frozen LLM Weights / Zero Backprop:**
   - All learning must occur online via local biological plasticity rules: **3-Compartment Dendritic Predictive Coding**, **Behavioral Timescale Synaptic Plasticity (`BTSP`)**, **Sherman-Morrison Recursive Least Squares (`LDM RLS`)**, **Two-Stage Helmholtz Consolidation (`Omega_fast -> Omega_slow`)**, or **Blind Log-Space Self-Mutation**.
2. **The Narrow-Waist Firewall (`Invariants I1–I6` in `src/unified_core_brain.rs`):**
   - `UnifiedCoreBrain` must never store hidden lookup tables, string caches, or side-channel task answers outside the sparse neural fabric (`BrainFabric`).
3. **Mandatory Flagless Synapse Lesion Control:**
   - Every capability test (`E0` through `E17`) must be paired with a **flagless physical synapse lesion control** (`zero_all_synapse_weights_flagless()`) that zeroes synaptic conductances `w = 0.0` without setting any boolean flag.
   - If a test still passes when synaptic weights are zeroed, the implementation is bypassing the neural fabric and must be refactored.
4. **Live (`L`) vs. Null-Twin (`N`) Falsifiability:**
   - Every exam must compare a trained organism (`L`) against a freshly initialized or phase/reward-scrambled Null Twin (`N`) on held-out items.

---

## Running the Verification Suite Before Submitting a PR

```bash
# 1. Run the E0–E17 Constitutional Judge & Sovereign Crucible suite
cargo test --release test_phase18 -- --nocapture

# 2. Run the entire 24-test verification suite across all 18 phases
cargo test --release

# 3. Verify zero compiler warnings
cargo check --all-targets
```
