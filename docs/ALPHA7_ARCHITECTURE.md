# Alpha 7: The Pure Road Architecture & Scientific Grounding

Alpha 7 is designed from first principles as an embodied, hardware-efficient, bio-inspired organism that unites **three biological scales** into a single engine (`Rust` core + `Python` 5-sense embodiment):

1. **Micro Scale (Event-Driven Spiking & Lazy Membrane Evaluation):** Millions of neurons in contiguous memory with $O(\text{active\_spikes})$ compute cost and zero idle CPU/memory-bus traffic.
2. **Cellular Scale (Multi-Compartment Dendritic Predictive Coding & Plateau Bursts):** Basal dendrites process bottom-up reality; Apical dendrites process top-down predictions and goals; mismatches trigger Dendritic $\text{Ca}^{2+}$ Plateau Bursts that unlock one-shot plasticity.
3. **Macro Scale (Hippocampal-Cortical Concept Cells & Behavioral Timescale Synaptic Plasticity):** 1–2 shot infant-like trait binding, core-invariant separation, grounded language comprehension, and direct autobiographical memories with the user.

---

## 1. Scientific & Organic Literature Grounding (Nature, Science, Cell, bioRxiv, arXiv)

### A. Compartmentalized Pyramidal Neurons & Dendritic Predictive Coding
- **Biological Finding:** Cortical and hippocampal pyramidal neurons physically segregate **bottom-up sensory reality** (targeting **basal dendrites** near the soma) from **top-down predictions, context, and goals** (targeting **apical tuft dendrites** in Layer 1). Rather than requiring a separate network of error neurons or global backpropagation, each pyramidal neuron acts as a local comparator between expectation (apical) and observation (basal).
- **Key References:**
  - Mikulasch, F. A., Rudelt, L., Wibral, M., & Priesemann, V. (2023). *Dendritic predictive coding: A theory of cortical computation with spiking neurons.* **Trends in Neurosciences (Cell Press) / arXiv:2205.05303**.
  - Larkum, M. E. (2013). *A cellular mechanism for cortical associations: an organizing principle for the cerebral cortex.* **Trends in Neurosciences (Cell Press)**, 36(3), 141–151.
- **Implementation in Alpha 7 ([`src/neuron.rs`](../src/neuron.rs)):**
  - `DendriticNeuron` maintains independent `basal_v` (sensory reality) and `apical_v` (top-down prediction/goal) potentials with lazy timestamp-based decay (`lazy_sync`).

### B. Multiplexed Single Spikes vs. Surprise Plateau Bursts
- **Biological Finding:** How does the brain transmit both current sensory state and prediction-error teaching signals over the same axons without scrambling them? Payeur, Naud, Sacramento, Richards et al. showed in **Nature Neuroscience** that neurons multiplex two distinct firing modes:
  1. **Single Spikes (`PredictedSingleSpike`):** Emitted during expected flow when predictions match sensory input.
  2. **High-Frequency Somatic Bursts driven by Apical $\text{Ca}^{2+}$ Plateau Potentials (`SurprisePlateauBurst`):** Emitted when unpredicted novelty occurs or when an apical prediction fails, acting as a local 3-factor switch for synaptic plasticity.
- **Key References:**
  - Payeur, A., Guerguiev, J., Zenke, F., Richards, B. A., & Naud, R. (2021). *Burst-dependent synaptic plasticity can coordinate learning in hierarchical circuits.* **Nature Neuroscience**, 24(7), 1010–1019.
  - Sacramento, J., Ponte Costa, R., Bengio, Y., & Senn, W. (2018). *Dendritic cortical microcircuits approximate the backpropagation algorithm.* **NeurIPS / arXiv:1810.11393**.
- **Implementation in Alpha 7 ([`src/fabric.rs`](../src/fabric.rs)):**
  - `SparseNeuralFabric::step` classifies every somatic firing event into `PredictedSingleSpike` vs. `SurprisePlateauBurst`, and explicitly tracks `failed_predictions` (neurons whose apical dendrites predicted firing, but which failed to happen).

### C. Behavioral Timescale Synaptic Plasticity (BTSP) for 1–2 Shot Learning
- **Biological Finding:** Classic Spike-Timing-Dependent Plasticity (STDP) operates over $\pm 20\text{ ms}$ and requires hundreds of repetitions—failing to explain how infants or animals learn a new concept, place, or rule in **1 or 2 exposures**. Bittner et al. and Magee & Grienberger discovered **Behavioral Timescale Synaptic Plasticity (BTSP)** in **Science**: active synapses leave a seconds-long biochemical **eligibility trace**; if a dendritic plateau burst occurs within that behavioral window, those eligible synapses undergo a massive, **one-shot weight update** in a single trial.
- **Key References:**
  - Bittner, K. C., Milstein, A. D., Grienberger, C., Romani, S., & Magee, J. C. (2017). *Behavioral time scale synaptic plasticity underlies CA1 place fields.* **Science**, 357(6355), 1033–1036.
  - Magee, J. C., & Grienberger, C. (2020). *Synaptic plasticity forms and functions.* **Annual Review of Neuroscience**, 43, 95–117.
  - Recent extensions of BTSP to neocortical sensory representations and one-shot memory networks (**bioRxiv / Nature**, 2023–2025).
- **Implementation in Alpha 7 ([`src/neuron.rs`](../src/neuron.rs), [`src/fabric.rs`](../src/fabric.rs)):**
  - `btsp_eligibility` and `btsp_history` track behavioral-timescale activity so that a single surprise burst or user teaching interaction immediately wires causal and conceptual synapses in one shot.

### D. Hippocampal Concept Cells & Neocortical Trait Invariance
- **Biological Finding:** Single-neuron recordings in the human medial temporal lobe (Quiroga et al., **Nature** / **Cell**) reveal **Concept Cells** that respond invariantly to a concept across modalities (sight, sound, spoken/written word) and across surface variations. Coupled with neocortical micro-column feature assemblies, 1–2 exposures separate **core invariant traits** (e.g., *whiskers*, *pointy ears*, *purr*, *soft fur*) from **incidental surface traits** (e.g., *orange fur* vs. *black fur*).
- **Key References:**
  - Quiroga, R. Q., Reddy, L., Kreiman, G., Koch, C., & Fried, I. (2005). *Invariant visual representation by single neurons in the human brain.* **Nature**, 435(7045), 1102–1107.
  - Quiroga, R. Q. (2012). *Concept cells: the building blocks of declarative memory functions.* **Nature Reviews Neuroscience**, 13(8), 587–597.
- **Implementation in Alpha 7 ([`src/concept_web.rs`](../src/concept_web.rs)):**
  - `ConceptualKnowledgeWeb::experience_concept` binds multimodal traits from all 5 senses + grounded words + motor affordances on exposure #1, and automatically separates `core_invariants()` from `variable_traits()` on exposure #2.

---

## 2. System Architecture Overview

| Module | File | Role |
| :--- | :--- | :--- |
| **Dendritic Neuron** | [`src/neuron.rs`](../src/neuron.rs) | 32-byte compact neuron with Basal (reality), Apical (prediction/goal), Soma comparator, and lazy timestamp decay. |
| **Sparse Neural Fabric** | [`src/fabric.rs`](../src/fabric.rs) | Contiguous arena for $1,000,000+$ neurons, $k$-Winner-Take-All micro-column inhibition, and BTSP/Surprise plasticity. |
| **Conceptual Knowledge Web** | [`src/concept_web.rs`](../src/concept_web.rs) | 1–2 shot concept formation, core vs. variable trait distillation, grounded word comprehension, and direct user episodic memories. |
| **Predictive Engine** | [`src/predictor.rs`](../src/predictor.rs) | Forward next-state prediction, failed-prediction causal diagnosis, and goal-directed multi-step scenario simulation. |
| **5-Sense Body** | [`python/alpha7/body.py`](../python/alpha7/body.py) | `Eyes`, `Ears`, `Hands` (including small code execution), `Smell`, and `InternalSenses`. |
| **Interactive Sandbox** | [`python/alpha7/sandbox.py`](../python/alpha7/sandbox.py) | `Alpha7Organism` and `SandboxWorld` for interactive teaching, coding practice, and scenario rollouts. |
