---
name: neuromorphic-predictive-brain
description: "Scientific and systems-engineering skill for biologically grounded Neuromorphic Spiking Neural Networks, Multi-Compartment Dendritic Predictive Coding, Behavioral Timescale Synaptic Plasticity (BTSP 1-2 shot learning), Hippocampal Concept Cells, and Hippocampal-Neocortical Sleep Replay in Pure Rust. Use whenever designing, extending, or auditing Alpha 7 or bio-inspired cognitive engines."
---

# Neuromorphic Predictive Brain & Pure-Road Engineering Skill

## 1. Scientific Foundations (Primary Literature)
1. **Multi-Compartment Dendritic Predictive Coding (Mikulasch et al., *Trends in Neurosciences* / *arXiv*; Larkum, *Trends in Neurosciences*; Payeur et al., *Nature Neuroscience* 2021):**
   - Cortical pyramidal neurons segregate **bottom-up sensory reality** onto **Basal Dendrites** ($V_{\text{basal}}$) and **top-down expectations/goals** onto **Apical Tuft Dendrites** ($V_{\text{apical}}$).
   - **Matched Prediction (`PredictedSingleSpike`):** When $V_{\text{basal}} \ge \theta$ and $V_{\text{apical}} \ge 0.35$, the neuron emits a single confirming spike without triggering surprise plasticity.
   - **Unpredicted Reality (`SurprisePlateauBurst`):** When $V_{\text{basal}} \ge \theta$ while $V_{\text{apical}} < 0.35$, an apical $\text{Ca}^{2+}$ plateau burst fires, unlocking 1-shot synaptic plasticity.
   - **Omission Surprise (`FailedPrediction`):** When $V_{\text{apical}} \ge 0.55$ but $V_{\text{basal}} < 0.25$, expected reality failed to happen, triggering counterfactual blocker isolation.

2. **Behavioral Timescale Synaptic Plasticity — BTSP (Bittner, Milstein, Grienberger, Romani, & Magee, *Science* 2017; Magee & Grienberger, *Annual Review of Neuroscience* 2020):**
   - Unlike classical STDP (which requires dozens of tight $\pm 20\text{ ms}$ pairings), BTSP uses a seconds-long synaptic eligibility trace gated by a dendritic plateau potential to form functional place/concept assemblies in **1 to 2 trials**.
   - $$\Delta w_{ij} = \eta_{\text{BTSP}} \cdot E_i(t) \cdot P_j^{\text{plateau}}(t) \cdot (w_{\max} - w_{ij})$$

3. **Human Invariant Concept Cells (Quiroga, Reddy, Kreiman, Koch, & Fried, *Nature* 2005; *Cell* / *Trends in Cognitive Sciences*):**
   - Medial Temporal Lobe (MTL) concept hubs respond selectively to abstract concepts across sensory modalities.
   - By exposure #2, **Core Invariant Traits** ($\text{invariance} \ge 0.65$) are separated from **Variable Surface Traits** ($\text{invariance} < 0.65$), enabling immediate generalization to unseen instances.
   - **Exteroceptive vs. Interoceptive Separation:** Internal homeostasis states (`senses:*`) and spoken user commentary tokens (`ears:heard_*`) must be stored in `EpisodicMemory`, never conflated with external object traits.

4. **Hippocampal-Neocortical Sharp-Wave Ripple Replay & Consolidation (Buzsáki, *Science*; Stickgold, *Nature*):**
   - During micro-sleep / consolidation cycles, high-surprise episodic memories are replayed into the cortical fabric, reinforcing multi-episode invariant synapses, pruning weak single-exposure noise synapses, and inducing compositional parent categories (`is_a`, `shares_core_with`, `contrasts_with`).

## 2. Pure-Rust Hardware Efficiency Guarantees
- **32-Byte Cache-Aligned Neuron Struct:** Keep `DendriticNeuron` at exactly 32 bytes (`2` neurons per 64-byte CPU cache line) so `1,000,000` neurons occupy `30.5 MB` RAM.
- **Zero-Idle Event-Driven Lazy Evaluation:** Never iterate over all `1,000,000` neurons per tick. Only evaluate neurons in `active_queue` and decay potentials lazily via $\exp(-\Delta t / \tau)$.
- **Sparse Checkpointing:** Only serialize active/modified neurons to disk (`< 150 KB` JSON) with atomic `.tmp` + `rename` writes.
- **Zero Crash Points:** Forbid `.unwrap()` / `.expect()` on runtime I/O, user inputs, or arithmetic. Guard against division-by-zero, `NaN`, and unbounded log/queue growth.
