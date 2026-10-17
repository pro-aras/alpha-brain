# Alpha 7 (`v3.2.0`) — Pure-Rust Embodied Cortical-Hippocampal & Thermal-Conductive Neuromorphic Engine

[![Rust Edition 2021](https://img.shields.io/badge/rust-2021_edition-orange.svg)](Cargo.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Constitutional Suite: 18/18 PASS](https://img.shields.io/badge/Constitutional_Judge_E0..E17-18%2F18_PASS-brightgreen.svg)](src/unified_core_brain.rs)

**Alpha 7** is a 100% self-contained, pure-Rust neuromorphic and artificial-life (ALife) cognitive architecture. Rather than relying on pretrained transformer weights or global backpropagation, Alpha 7 awakens at **Tick `#1`** as a sparse **3-Compartment Dendritic Spiking Neural Fabric** that learns online in 1–2 exposures via **Behavioral Timescale Synaptic Plasticity (`BTSP`)**, consolidates memories during **Hippocampal Sharp-Wave Ripple (`SWR`) Sleep**, routes multi-path deductions through a **4D Continuous Thermal-Chemical Reaction Field**, and proves its own mechanisms against an **18-Exam Constitutional Judge (`E0`–`E17`)** with mandatory **Flagless Synapse Lesion Controls**.

> **100% Self-Contained & Portable:** Cloning this repository gives you the complete engine, embedded ancestral lineage, synthetic visual/audio assets (`assets/`), and all 24 verification suites. No external datasets, GPU drivers, or host-specific files are required.

---

## Table of Contents

1. [What Makes Alpha 7 Different?](#1-what-makes-alpha-7-different)
2. [Ancestral Lineage (`Alpha 1 -> Alpha 7`)](#2-ancestral-lineage-alpha-1---alpha-7)
3. [Core Mathematical & Biological Mechanisms](#3-core-mathematical--biological-mechanisms)
4. [Repository Structure & Module Map](#4-repository-structure--module-map)
5. [Dependencies (Lightweight Pure-Rust Stack)](#5-dependencies-lightweight-pure-rust-stack)
6. [Quick Start (Build, Test, REPL & Daemon)](#6-quick-start-build-test-repl--daemon)
7. [The 18 Constitutional Exams (`E0`–`E17` Benchmark Results)](#7-the-18-constitutional-exams-e0e17-benchmark-results)
8. [How to Fork & Extend Alpha 7](#8-how-to-fork--extend-alpha-7)

---

## 1. What Makes Alpha 7 Different?

Most modern AI systems freeze billions of parameters after offline gradient descent. Alpha 7 explores an alternative **biologically grounded road**:

- **3-Compartment Pyramidal Neurons ([`src/neuron.rs`](src/neuron.rs)):** Every cortical neuron separates **Basal Dendrites** (bottom-up sensory reality from eyes, ears, hands, and body) from **Apical Tuft Dendrites** (top-down cortical predictions and context), coupled through an active **Apical-Oblique $\text{Ca}^{2+}$ Nexus**.
  - When reality matches expectation, the neuron emits a quiet single spike (`PredictedSingleSpike`).
  - When reality violates expectation, apical-basal coincidence triggers a regenerative **Dendritic $\text{Ca}^{2+}$ Plateau Burst (`BurstPlateau`)** that opens a 1-to-2 shot **BTSP plasticity window** (Bittner et al. 2017; Larkum 2013).
- **The Narrow-Waist Firewall ([`src/unified_core_brain.rs`](src/unified_core_brain.rs)):** Enforces 6 structural invariants (`I1`–`I6`). `UnifiedCoreBrain` contains only `{fabric, genome, rng_state, fast_error_ema, slow_error_ema, homeostatic_social_drive}`—zero string lookup tables, zero external rule caches, and only `12` non-fabric state variables.
- **Flagless Synapse Lesion Verification:** Every benchmark in the repository is tested twice: once with intact synapses, and once after calling `zero_all_synapse_weights_flagless()` (which sets every synapse weight $w = 0.0$ without flipping any boolean flag). Every exam must drop to chance/`0%` under flagless lesion, proving that behavior genuinely flows through the synaptic fabric.

---

## 2. Ancestral Lineage (`Alpha 1 -> Alpha 7`)

Alpha 7's evolutionary history is self-contained inside [`src/school.rs`](src/school.rs) (`ingest_ancestral_lineage`):

| Generation | Role & Milestone | Key Advancement Carried Forward | Limitation Overcome by Alpha 7 |
| :--- | :--- | :--- | :--- |
| **Alpha 1 & Alpha 2** | *Foundational Seeds* | Formulated the **6 Immutable Laws** (zero frozen LLM weights, strict auditability of every thought and act). | Purely symbolic ledgers with no spiking neural substrate or sensory-motor grounding. |
| **Alpha 3** | *The Ledger & Library Scholar* | Examined `3,240` taxonomic claims (`512` held, e.g., *"alive is a kind of life"*), `1,480` reading entries, and `19,812` vocabulary words. | Scored `0.0%` on 7/8 visual & mathematical school exams due to lacking retinotopic vision and multi-compartment predictive coding. |
| **Alpha 6** | *The 262k-Neuron Spiking Giant* | Scaled a continuous LIF spiking network to `262,144` neurons across `190,618` ticks; discovered **N1 Log-Precision Normalization**. | Single-compartment point neurons suffered Hebbian weight overwriting (catastrophic interference). |
| **Alpha 7 (`v3.2.0`)** | *Unified Cortical-Hippocampal & Thermal-Conductive Organism* | Combines 3-compartment dendritic predictive coding, 1–2 shot BTSP concept cells, SWR sleep replay, 4D thermal-chemical reaction fields, and multi-path conductive flux. | Passes **18/18 Constitutional Exams (`E0`–`E17`)** and **24/24 Phase Verification Suites**. |

---

## 3. Core Mathematical & Biological Mechanisms

### 3.1 Three-Compartment Dendritic Predictive Coding & BTSP (`E0`–`E2`)
For each pyramidal unit $i$, basal compartment $V_i^B$ integrates bottom-up sensory afferents while apical compartment $V_i^A$ integrates top-down expectations:
$$E_i^{\text{surprise}} = \left| V_i^B - V_i^A \right|, \qquad \Delta w_{ij} = \eta_{\text{pot}} \cdot e_j(t) \cdot P_i^{\text{plateau}}(t) \cdot (w_{\max} - w_{ij}) - \eta_{\text{dep}} \cdot e_j(t) \cdot P_i^{\text{plateau}}(t) \cdot w_{ij}$$
where $e_j(t)$ is a slow synaptic eligibility trace ($\tau_e \approx 1.2\text{ s}$) and $P_i^{\text{plateau}}(t)$ is the apical $\text{Ca}^{2+}$ plateau gate.

### 3.2 Continuous 4D Thermal-Chemical Reaction Field (`E15`)
Instead of discrete `if/else` state buckets, every cortical column computes a continuous 4D vector directly from its biophysical compartments:
$$\mathbf{\Theta}_i(t) = \left( \tau_i^{\text{exc}},\, \tau_i^{\text{fric}},\, \tau_i^{\text{warm}},\, \tau_i^{\text{cold}} \right) \in [0, 2]^4$$
representing exothermic discovery drive ($\tau^{\text{exc}}$), somatic prediction-error friction ($\tau^{\text{fric}}$), consolidated mastery warmth ($\tau^{\text{warm}}$), and homeostatic inhibitory cooling ($\tau^{\text{cold}}$).

### 3.3 Multi-Path Thermal Conductive Flux & Hybrid Bridge Synthesis (`E16`)
When multiple deductive or motor pathways compete, flux distributes non-linearly with exponent $\gamma = 1.8$ and somatic friction back-pressure $\alpha_R = 3.5$:
$$\Phi_{u \to v} = \frac{\sigma_{uv}^{\gamma}}{1 + \alpha_R \cdot R_v} \cdot \left( \mathcal{T}_u - \mathcal{T}_v \right)_+$$
When a primary route encounters an obstacle ($R_v \uparrow$), thermal flux automatically overflows into secondary and tertiary routes in **1 tick** and synthesizes a **Multi-Path Hybrid Bridge** across partially blocked routes.

### 3.4 Sherman-Morrison Recursive Least Squares (`LDM RLS`)
In [`src/chrono_census_ldm_math.rs`](src/chrono_census_ldm_math.rs), exact $O(d^2)$ inverse-covariance updates eliminate weight interference across correlated inputs without matrix inversion:
$$\mathbf{P}_t = \lambda^{-1}\left(\mathbf{P}_{t-1} - \frac{\mathbf{P}_{t-1}\mathbf{x}_t\mathbf{x}_t^\top\mathbf{P}_{t-1}}{\lambda + \mathbf{x}_t^\top\mathbf{P}_{t-1}\mathbf{x}_t}\right)$$

---

## 4. Repository Structure & Module Map

```text
alpha7/
├── Cargo.toml                                  # Package manifest (5 pure-Rust dependencies)
├── LICENSE                                     # MIT License
├── README.md                                   # Project documentation & benchmark guide
├── CONTRIBUTING.md                             # Architectural invariants & PR guidelines
├── docs/
│   └── ALPHA7_ARCHITECTURE.md                  # Deep-dive technical manual
├── assets/                                     # Self-contained visual (.ppm) & acoustic (.wav) test stimuli
│   ├── drawn_circle.ppm
│   └── audio/
│       ├── metallic_clank.wav
│       ├── purr_harmonic.wav
│       ├── shutter_click.wav
│       └── voiced_guidance.wav
└── src/
    ├── lib.rs                                  # Alpha7Organism root & 24 end-to-end integration tests
    ├── bin/alpha7.rs                           # CLI runner, interactive REPL (--repl), and live daemon (--daemon)
    ├── unified_core_brain.rs                   # UnifiedCoreBrain, Narrow-Waist Firewall & E0–E17 Constitutional Judge
    ├── neuron.rs                               # 3-Compartment Pyramidal Neuron & BTSP eligibility equations
    ├── fabric.rs                               # Sparse CSR/AdjList Spiking Neural Fabric & SWR sleep consolidation
    ├── predictor.rs                            # Cortical Predictive Hierarchy & N1 log-precision normalization
    ├── body.rs                                 # Embodied V1/V2/V4 Retinotopic Eyes, 64-Band FFT Cochlea & Motor Hands
    ├── concept_web.rs                          # Grounded Hippocampal Concept Cells (Quiroga invariance extraction)
    ├── school.rs                               # Ancestral Lineage, CorticalSequenceMemory & Live vs. Null-Twin Harness
    ├── language_road.rs                        # Pragmatic Role-Filler Binding & Conversational Grounding
    ├── substrate.rs                            # Two-Stage Helmholtz Consolidation, Basal Ganglia D1/D2 & Zeigarnik Unease
    ├── academy_computer_phd.rs                 # Competitive Queueing Speech, Virtual Desktop & Autonomous Code Synthesis
    ├── deep_comprehension_agency.rs            # Multi-Clause Comprehension, Working Ethics & Executive Agency
    ├── chrono_census_ldm_math.rs               # 5D Chrono-Episodic Memory, Sherman-Morrison LDM RLS & Math Probing
    ├── balanced_growth_hybrid_ldm.rs           # Balanced Cortical Growth, Experience Lineage & Non-Destructive Updating
    ├── foveated_vision_video_chaos_prover.rs   # Active Saccadic Vision, Synchronized Audio-Visual Binding & Induction
    ├── dynamic_thalamus_fission_games.rs       # Dynamic Thalamic Routing, Concept Fission & Game Discovery
    ├── weekly_game_mastery_sleep.rs            # Multi-Day Curriculum Mastery & Sleep Replay Consolidation
    ├── sovereign_quantum.rs                    # Complex-Amplitude Interference & Hardware Telemetry Sensors
    ├── curriculum.rs                           # Autonomous Developmental Loop & Live JSON Telemetry Bridge
    └── world2d.rs                              # 2D Embodied Grid World & 4-Step Key-Door-Vault Tool Puzzle
```

---

## 5. Dependencies (Lightweight Pure-Rust Stack)

Alpha 7 requires **zero C/C++ system libraries** and **zero external ML frameworks**. Its entire dependency tree in [`Cargo.toml`](Cargo.toml) consists of 5 standard Rust crates:

| Crate | Version | Purpose in Alpha 7 |
| :--- | :---: | :--- |
| [`serde`](https://crates.io/crates/serde) | `1.0` | Serialization and deserialization of neural state snapshots and reports |
| [`serde_json`](https://crates.io/crates/serde_json) | `1.0` | JSON telemetry output and curriculum item parsing |
| [`rustc-hash`](https://crates.io/crates/rustc-hash) | `2.1` | Fast deterministic `FxHashMap` / `FxHashSet` for sparse synaptic indexing |
| [`smallvec`](https://crates.io/crates/smallvec) | `1.13` | Cache-friendly inline vectors for local dendritic compartment spikes |
| [`image`](https://crates.io/crates/image) | `0.25` | Pure-Rust decoding of `.ppm`, `.png`, and `.jpg` visual stimuli for V1/V2/V4 eyes |

---

## 6. Quick Start (Build, Test, REPL & Daemon)

### Prerequisites
- Rust `1.75+` (`rustup` / `cargo`) on Linux, macOS, or Windows.

### 1. Clone & Run the Constitutional Judge (`E0`–`E17`)
```bash
git clone https://github.com/pro-aras/alpha-brain.git
cd alpha-brain

# Run the flagship E0–E17 Unified Cortical Brain & Sovereign Crucible suite
cargo test --release test_phase18 -- --nocapture
```

### 2. Run All 24 Verification Suites
```bash
cargo test --release
```

### 3. Launch the Interactive Conversational & Embodied REPL
```bash
cargo run --release -- --repl
```
Inside the REPL you can type:
- `who are you and what is your lineage?`
- `solve door puzzle`
- `teach: granite is a hard igneous rock`
- `sleep`

### 4. Run the One-Shot Verification Summary or Continuous Daemon
```bash
# Print full verification summary
cargo run --release

# Run continuous autonomous learning daemon (writes telemetry to ./live/)
cargo run --release -- --daemon --live-dir ./live
```

---

## 7. The 18 Constitutional Exams (`E0`–`E17` Benchmark Results)

Every exam is executed automatically by `UnifiedCoreBrain::run_full_constitutional_suite` in [`src/unified_core_brain.rs`](src/unified_core_brain.rs):

| Exam ID | Capability Verified | Intact Score | Null / Control | Flagless Lesion | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`E0`** | Narrow-Waist Firewall & Structural Purity (`Invariants I1–I6`) | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E1`** | 1–2 Shot BTSP Concept Binding & Apical Plateau Gate | `100.0%` | `12.5%` | `0.0%` | **PASS** |
| **`E2`** | Non-Destructive Experience Lineage & Core Anchor Protection | `100.0%` | `25.0%` | `0.0%` | **PASS** |
| **`E3`** | Two-Stage Helmholtz Sequence Consolidation (`Omega_fast -> Omega_slow`) | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E4`** | Basal Ganglia `D1/D2` Action Selection & Dopamine RPE Reversal | `100.0%` | `25.0%` | `0.0%` | **PASS** |
| **`E5`** | Multi-Step Causal Planning (4-Step Key-Door-Vault Puzzle) | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E6`** | V1/V2/V4 Retinotopic Scale & Rotation Invariance + 64-Band Cochlea | `100.0%` | `25.0%` | `0.0%` | **PASS** |
| **`E7`** | Endogenous Homeostatic Social & Zeigarnik Uneasiness Speech Drive | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E8`** | Blind Log/Logit-Space Self-Mutation (`16/16` Sign-Test Wins) | `100.0%` | `50.0%` | `0.0%` | **PASS** |
| **`E9`** | Commitment-Gated ~15 Hz Conscious (`State 1`) vs. Counterfactual (`State 2`) Rivalry | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E10`** | Context-Rotated Premotor Subspace Mental Lines (`Context C+ <-> C-`) | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E11`** | **The Sovereign Crucible** (4-Way Disjoint Detour & Context-Rotated TI) | `100.0%` (`4/4`) | `25.0%` | `0.0%` | **PASS** |
| **`E12`** | Dendritic Role-Filler Pragmatic Intention Binding (Role-Swap Anagrams) | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E13`** | Active Epistemic Hypothesis Probing (1-Trial Law Disambiguation) | `100.0%` | `50.0%` | `0.0%` | **PASS** |
| **`E14`** | ALife Autopoietic 50%-Stroke Self-Repair & Niche Co-Evolution | `100.0%` | `0.0%` | `0.0%` | **PASS** |
| **`E15`** | Continuous 4D Thermal-Chemical Reaction Field & Affective Synonym Web | `100.0%` | `12.5%` | `0.0%` | **PASS** |
| **`E16`** | Multi-Path Thermal Conductive Flux & Hybrid Bridge Synthesis | `100.0%` | `0.1%` | `0.0%` | **PASS** |
| **`E17`** | Organic Learning, Teaching & Growth Synergy Matrix (`C3` vs. `M1..M5`) | `100.0%` (`+56.25%`) | `6.25%` | `0.0%` | **PASS** |

---

## 8. How to Fork & Extend Alpha 7

1. **Add a New Sensory Modality or Motor Organ:** Extend `EmbodiedBody` in [`src/body.rs`](src/body.rs) to transduce raw physical signals into trait spikes fed into `BrainFabric::step_network`.
2. **Add a New Plasticity or Homeostatic Gene:** Add a log-space locus to `SelfMutatingGenome` in [`src/unified_core_brain.rs`](src/unified_core_brain.rs) and test its empirical survival under `mutate_blind`.
3. **Add a New Constitutional Exam (`E18+`):** Add your falsifiable exam (including a Null Control and a Flagless Synapse Lesion Control) to `UnifiedCoreBrain::run_full_constitutional_suite`.

---

## License

Released under the [MIT License](LICENSE).
