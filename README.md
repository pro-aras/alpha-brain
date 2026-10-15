# Alpha 7 (`v2.0.0`) — Pure-Rust Embodied Cortical-Hippocampal & Sovereign Quantum AI

**Alpha 7** is a 100% pure-Rust embodied, bio-inspired cognitive architecture that unites dendritic spiking neural fabrics, hippocampal-cortical memory consolidation, laminar depth memory, dynamic hardware-adaptive vision/audio, a unified thalamo-cortical sensory stream, and multicellular fission–fusion self-play into a single hardware-efficient engine:

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
   - **Synchronized Biological Co-Maturation (`SynchronizedDevelopmentalHomeostasis`):** Coupled Hensch E/I critical-period homeostasis ensuring all 5 life domains (Vision/Physics, Language, Social/Causal, Mathematical Number Sense, and Executive Self-Regulation) mature at the same biological age rate (`Age 2 -> 5 -> 9 -> 14 -> 18 -> 21`, inter-domain spread $\le 0.75$ years).
4. **Human-Clarity Foveated Retina, Synchronized Video/Audio Stream & Unorganized Chaos Root Prover ([`src/foveated_vision_video_chaos_prover.rs`](src/foveated_vision_video_chaos_prover.rs)):**
   - **Human-Clarity Foveated Retina (`HumanFoveatedRetinaOrgan`):** Two-stream primate vision combining a magnocellular peripheral saliency map with $1:1$ native-pixel parvocellular foveal saccades and headless browser visual inspection.
   - **Synchronized Audio-Visual Video Organ (`SynchronizedAudioVisualVideoOrgan`):** Decodes consecutive `.png` video frames with MT/V5 optical motion flow alongside time-aligned mono PCM `audio.wav` cochlear envelopes and spoken language cues.
   - **Unorganized Chaos Self-Organizer & Root Prover (`UnorganizedChaosRootProverOrgan`):** Ingests an unlabeled, scrambled mix of raw items from Kindergarten through PhD, autonomously sorts them by prerequisite root depth (Zone of Proximal Development), extracts each invariant root law, and proves it from first principles.
5. **Dynamic Native-Resolution Body, Unified Thalamic Sensory Stream & Multicellular Fission–Fusion Self-Play ([`src/dynamic_thalamus_fission_games.rs`](src/dynamic_thalamus_fission_games.rs)):**
   - **Dynamic Hardware-Adaptive Sensory Body (`DynamicHardwareAdaptiveBody`):** Eliminates fixed-grid sensory bottlenecks; dynamically adapts to any native visual resolution (`160x120`, `640x480`, `1920x1080` Full HD, up to `8192x8192` as RAM/CPU allows at `1:1` pixel stride) and any audio sample rate (`8 kHz` to `192 kHz`) with aspect-ratio-invariant geometric moments.
   - **Unified Thalamo-Cortical & Claustrum Sensory Bus (`UnifiedThalamicSensoryBus`):** Continuously fuses simultaneous inputs from all 5 peripheral organs (`Eyes`, `Ears`, `Hands`, `Smell`, `Interoception`) via precision-weighted and superadditive cross-modal integration into **one single unified wave packet (`UnifiedCorticalWavePacket`)** before entering the cortical brain.
   - **Multicellular Fission–Fusion Organism & Non-Repeating Strategy Games (`MulticellularFissionFusionOrgan`):** Solves procedurally generated, non-repeating `9x9` Sudoku boards (learning Row/Col/Box tri-constraints from initial conflict failures) and performs **Asymmetric Cognitive Mitosis (Fission)** into genuinely distinct individuals (`Cell α: Vanguard-Tactician` vs. `Cell β: Sentinel-Strategist`, $\cos(\Delta_\alpha, \Delta_\beta) < 0$) that play full legal `8x8` Chess against each other and **recombine (`ZygoticBrainFusionEvent`)** back into one unified organism via Fisher-precision synaptic consolidation.
6. **Sovereign Quantum Brain, Academic Progression & Mathematical Discovery ([`src/sovereign_quantum.rs`](src/sovereign_quantum.rs), [`src/academy_computer_phd.rs`](src/academy_computer_phd.rs), [`src/chrono_census_ldm_math.rs`](src/chrono_census_ldm_math.rs)):**
   - Simulated bifurcation (`QuantumBifurcationSettler`), somatic state integrity (`EndogenousGeneticVault`), epistemic verification (`EpistemicSovereigntyEngine`), virtual desktop lab (`VirtualComputerDesktop`), Peano symbolic induction, and open mathematical conjecture probing.

## Quick Start

```bash
# Run the full 20-test release verification suite (Phases 0–16)
cargo test --release

# Run the full showcase
cargo run --release

# Launch the interactive live REPL & 2D World Explorer
cargo run --release -- --repl
```

