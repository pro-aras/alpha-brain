# Alpha 7 — The Pure Road

**Alpha 7** is a 100% pure-Rust embodied, bio-inspired organism that unites three biological scales into a single hardware-efficient engine:

1. **Event-Driven Sparse Dendritic Neurons ([`src/neuron.rs`](src/neuron.rs), [`src/fabric.rs`](src/fabric.rs)):**
   - Supports **1,000,000+ neurons** in ~30.5 MB of contiguous RAM with **zero idle compute** ($O(\text{active\_spikes})$ complexity via lazy timestamp membrane evaluation).
   - Segregates **Basal Dendrites** (bottom-up sensory reality) from **Apical Dendrites** (top-down predictions & goals).
   - Emits quiet `PredictedSingleSpike` events when predictions match reality, and `SurprisePlateauBurst` events when unpredicted events or failed predictions occur.
2. **Hippocampal-Cortical Concept Web & 1–2 Shot Infant Learning ([`src/concept_web.rs`](src/concept_web.rs)):**
   - Uses **Behavioral Timescale Synaptic Plasticity (BTSP)** to bind multi-sensory traits across all 5 senses on the **1st exposure**, and separates **Core Invariant Traits** (e.g., *whiskers*, *pointy ears*, *four legs*, *soft fur*) from **Variable Surface Traits** (e.g., *orange fur* vs. *black fur*) on the **2nd exposure**.
   - Stores direct autobiographical **Episodic Memories** with the user.
3. **Predictive Engine, Surprise Failure Analyzer & Goal Scenario Simulator ([`src/predictor.rs`](src/predictor.rs)):**
   - Continuously predicts what will happen next; when an expected outcome **fails to happen**, isolates the contextual blocker/exception and updates its causal rules and apical synapses in one shot.
   - Simulates multi-step possibilities directed toward user goals.
4. **Pure-Rust 5-Sense Body, Grounded Mouth & 2D Spatial World Canvas ([`src/body.rs`](src/body.rs), [`src/language_road.rs`](src/language_road.rs), [`src/world2d.rs`](src/world2d.rs), [`src/bin/alpha7.rs`](src/bin/alpha7.rs)):**
   - **Eyes, Ears, Hands, Smell, and Internal Senses** operate natively in Rust on a 2D spatial world canvas with saccades, olfactory plumes, acoustic ranges, tactile manipulation, and small code execution.
   - **Grounded Language & Mouth Road:** Every word is wired to sensory-motor concepts; Alpha 7 speaks and asks curiosity questions strictly from grounded internal state.

## Quick Start

```bash
# Run the full verification test suite
cargo test --release

# Run the full 6-part showcase (1M neurons, 2D canvas, 1-2 shot cat learning, mouth, prediction failure, code learning)
cargo run --release

# Launch the interactive live REPL & 2D World Explorer
cargo run --release -- --repl
```
