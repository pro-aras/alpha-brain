# Alpha 7 (`v1.8.0`) — Pure-Rust Embodied Cortical-Hippocampal & Sovereign Quantum AI

**Alpha 7** is a 100% pure-Rust embodied, bio-inspired cognitive architecture that unites dendritic spiking neural fabrics, hippocampal-cortical memory consolidation, laminar depth memory, and synchronized biological co-maturation into a single hardware-efficient engine:

1. **Event-Driven Sparse Dendritic Neurons ([`src/neuron.rs`](src/neuron.rs), [`src/fabric.rs`](src/fabric.rs)):**
   - Supports **1,000,000+ neurons** in ~30.5 MB of contiguous RAM with **zero idle compute** ($O(\text{active\_spikes})$ complexity via lazy timestamp membrane evaluation).
   - Segregates **Basal Dendrites** (bottom-up sensory reality) from **Apical Dendrites** (top-down predictions & goals).
   - Emits quiet `PredictedSingleSpike` events when predictions match reality, and `SurprisePlateauBurst` events when unpredicted events or failed predictions occur.
2. **Hippocampal-Cortical Concept Web & 1–2 Shot Infant Learning ([`src/concept_web.rs`](src/concept_web.rs), [`src/substrate.rs`](src/substrate.rs)):**
   - Uses **Behavioral Timescale Synaptic Plasticity (BTSP)** to bind multi-sensory traits across all 5 senses on the **1st exposure**, and separates **Core Invariant Traits** from **Variable Surface Traits** on the **2nd exposure**.
   - Includes a Cortical-Hippocampal Substrate (`Hot16` AoS + `ColdSoA` pools, VIP/SST/PV interneuron gates, Two-Stage Helmholtz $\Omega$, `KenyonBinder`, and `CORE` timescale hierarchy).
3. **Bio-Stabilized Bidirectional Unwinding LDM & Multilingual HybridLink ([`src/balanced_growth_hybrid_ldm.rs`](src/balanced_growth_hybrid_ldm.rs)):**
   - **Bio-Stabilized Bidirectional Linear Depth Memory (`BioStabilizedBidirectionalLDM`):** Multi-group ($G=4$), windowed ($E=4$) Recursive Least-Squares depth memory with Directional Forgetting and Spectral Stabilization ($L=70$ layers) plus Top-Down Laminar State Unwinding ($M_{\ell-1} = M_\ell - u_\ell \kappa_\ell^\top$) for apical credit assignment.
   - **Grounded Workspace HybridLink (`GroundedWorkspaceHybridLink`):** Language-independent conceptual workspace with Two-Pass Self-Conditioned Training, Global Neuronal Workspace (GNW) attractor ignition, and multilingual readout (English, Arabic, and Symbolic Mathematics).
   - **Synchronized Biological Co-Maturation (`SynchronizedDevelopmentalHomeostasis`):** Coupled Hensch E/I critical-period homeostasis ensuring all 5 life domains (Vision/Physics, Language, Social/Causal, Mathematical Number Sense, and Executive Self-Regulation) mature at the same biological age rate (`Age 2 -> 5 -> 9 -> 14 -> 18`, inter-domain spread $\le 0.75$ years).
   - **Interactive Trilingual Curriculum & Sandboxed Self-Code Upgrade Organ (`Phase14InteractiveEvolutionEngine`):** 5-stage grounded trilingual dialogue curriculum and sandboxed A/B organ upgrade verification runner.
4. **Sovereign Quantum Brain, Academic Progression & Mathematical Discovery ([`src/sovereign_quantum.rs`](src/sovereign_quantum.rs), [`src/academy_computer_phd.rs`](src/academy_computer_phd.rs), [`src/chrono_census_ldm_math.rs`](src/chrono_census_ldm_math.rs)):**
   - Simulated bifurcation (`QuantumBifurcationSettler`), somatic state integrity (`EndogenousGeneticVault`), epistemic verification (`EpistemicSovereigntyEngine`), virtual 64×64 desktop lab (`VirtualComputerDesktop`), Peano symbolic induction, and open mathematical conjecture probing.
5. **Pure-Rust 5-Sense Body, Grounded Mouth & 2D Spatial World Canvas ([`src/body.rs`](src/body.rs), [`src/language_road.rs`](src/language_road.rs), [`src/world2d.rs`](src/world2d.rs), [`src/bin/alpha7.rs`](src/bin/alpha7.rs)):**
   - **Eyes, Ears, Hands, Smell, and Internal Senses** operate natively in Rust on a 2D spatial world canvas with saccades, olfactory plumes, acoustic ranges, tactile manipulation, and sandboxed code execution.

## Quick Start

```bash
# Run the full 18-test release verification suite (Phases 0–14)
cargo test --release

# Run the full showcase
cargo run --release

# Launch the interactive live REPL & 2D World Explorer
cargo run --release -- --repl
```

