//! Alpha 7 Event-Driven Sparse Neural Fabric
//!
//! Runs millions of multi-compartment dendritic neurons with O(active_spikes) compute cost.
//! - Zero idle compute: Only neurons receiving events in the current tick are touched.
//! - Micro-column k-Winner-Take-All (kWTA) lateral inhibition maintains ~1-2% sparse activity.
//! - Detects both types of prediction error:
//!   1. Unpredicted reality (SurprisePlateauBurst) -> triggers BTSP 1-shot learning.
//!   2. Failed prediction (Omission Surprise: predicted by apical dendrites, failed to happen)
//!      -> triggers causal analysis & predictive synapse correction.

use crate::neuron::{DendriticNeuron, Modality, SpikeEvent, SpikeKind, Synapse};
use rustc_hash::{FxHashMap, FxHashSet};
use serde::{Deserialize, Serialize};
use smallvec::SmallVec;

/// Record of a prediction failure when something Alpha 7 predicted failed to happen,
/// or when something unpredicted happened.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurpriseAnalysis {
    pub tick: u32,
    /// Neurons that were predicted to fire by apical dendrites but FAILED to happen.
    pub failed_predictions: Vec<u32>,
    /// Neurons that fired unexpectedly without prior apical prediction (Novelty/Surprise bursts).
    pub unpredicted_bursts: Vec<u32>,
    /// Overall surprise / prediction-error magnitude in [0.0, 1.0].
    pub surprise_score: f32,
    /// Number of synapses updated or created via 1-shot BTSP & predictive correction in this tick.
    pub plastic_updates: usize,
}

/// Summary telemetry of a single fabric step.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StepReport {
    pub tick: u32,
    pub total_neurons: usize,
    pub touched_neurons: usize,
    pub active_spikes: Vec<SpikeEvent>,
    pub predicted_matches: Vec<u32>,
    pub surprise: SurpriseAnalysis,
}

/// High-efficiency sparse neural fabric supporting millions of neurons.
#[derive(Serialize, Deserialize)]
pub struct SparseNeuralFabric {
    pub current_tick: u32,
    /// Flat contiguous array of all neurons (32 bytes per neuron: 1M neurons = 32 MB).
    pub neurons: Vec<DendriticNeuron>,
    /// Sparse outgoing synapses per active neuron (0 bytes for unconnected neurons).
    pub synapses: FxHashMap<u32, SmallVec<[Synapse; 4]>>,
    /// Named trait/symbol lookup <-> neuron assembly IDs.
    pub trait_to_neuron: FxHashMap<String, u32>,
    pub neuron_to_trait: FxHashMap<u32, String>,
    /// Queue of pending events to deliver in the next step.
    pub event_queue: Vec<SpikeEvent>,
    /// Neurons whose apical dendrites predicted they would fire on the upcoming step.
    pub pending_predictions: FxHashSet<u32>,
    /// Rolling behavioral-timescale history of recently spiked neurons `(tick, neuron_id)`
    /// for O(active) Behavioral Timescale Synaptic Plasticity (BTSP).
    pub btsp_history: Vec<(u32, u32)>,
    /// Configuration parameters.
    pub kwta_winners_per_column: usize,
    pub btsp_window_ticks: u32,
    pub predictive_window_ticks: u32,
    pub btsp_one_shot_lr: f32,
}

impl SparseNeuralFabric {
    /// Creates a new sparse neural fabric with `num_neurons` pre-allocated in contiguous memory.
    pub fn new(num_neurons: usize, neurons_per_column: usize) -> Self {
        let cols = neurons_per_column.max(1);
        let mut neurons = Vec::with_capacity(num_neurons);
        for i in 0..num_neurons {
            let col_id = (i / cols) as u32;
            let modality = match col_id % 9 {
                0 => Modality::Visual,
                1 => Modality::Auditory,
                2 => Modality::TactileHand,
                3 => Modality::Olfactory,
                4 => Modality::Internal,
                5 => Modality::Association,
                6 => Modality::ConceptHub,
                7 => Modality::Language,
                _ => Modality::MotorGoal,
            };
            neurons.push(DendriticNeuron::new(col_id, modality));
        }

        Self {
            current_tick: 1,
            neurons,
            synapses: FxHashMap::default(),
            trait_to_neuron: FxHashMap::default(),
            neuron_to_trait: FxHashMap::default(),
            event_queue: Vec::with_capacity(256),
            pending_predictions: FxHashSet::default(),
            btsp_history: Vec::with_capacity(512),
            kwta_winners_per_column: 4,
            btsp_window_ticks: 6,
            predictive_window_ticks: 3,
            btsp_one_shot_lr: 0.65,
        }
    }

    /// Registers or retrieves a grounded neuron ID for a specific sensory/motor/lexical trait
    /// (e.g., `"eyes:whiskers"`, `"ears:purr"`, `"hands:soft_fur"`, `"word:cat"`).
    pub fn ensure_trait_neuron(&mut self, trait_key: &str, modality: Modality) -> u32 {
        if let Some(&id) = self.trait_to_neuron.get(trait_key) {
            return id;
        }
        // Allocate either from an unmapped slot or append a new neuron
        let id = self.trait_to_neuron.len() as u32;
        let neuron_id = if (id as usize) < self.neurons.len() {
            let n = &mut self.neurons[id as usize];
            n.modality = modality as u8;
            n.column_id = (modality as u32) * 1000 + (id % 256);
            id
        } else {
            let new_id = self.neurons.len() as u32;
            let col_id = (modality as u32) * 1000 + (new_id % 256);
            self.neurons.push(DendriticNeuron::new(col_id, modality));
            new_id
        };

        self.trait_to_neuron
            .insert(trait_key.to_string(), neuron_id);
        self.neuron_to_trait
            .insert(neuron_id, trait_key.to_string());
        neuron_id
    }

    /// Injects bottom-up sensory or motor events into Basal dendrites for the current step.
    pub fn inject_basal_stimulus(&mut self, neuron_id: u32, amplitude: f32) {
        if (neuron_id as usize) < self.neurons.len() {
            self.event_queue.push(SpikeEvent {
                source_id: neuron_id,
                tick: self.current_tick,
                amplitude,
                kind: SpikeKind::SurprisePlateauBurst,
            });
        }
    }

    /// Injects a top-down expectation/goal signal into the Apical dendrite of `neuron_id`.
    pub fn inject_apical_prediction(&mut self, neuron_id: u32, amplitude: f32) {
        if (neuron_id as usize) < self.neurons.len() {
            let n = &mut self.neurons[neuron_id as usize];
            n.integrate(self.current_tick, amplitude, true);
            if n.apical_v >= 0.45 {
                self.pending_predictions.insert(neuron_id);
            }
        }
    }

    /// Connects or strengthens a directed synapse between `pre_id` and `post_id`.
    pub fn upsert_synapse(
        &mut self,
        pre_id: u32,
        post_id: u32,
        delta_w: f32,
        is_apical: bool,
        max_w: f32,
    ) -> bool {
        if pre_id == post_id
            || (pre_id as usize) >= self.neurons.len()
            || (post_id as usize) >= self.neurons.len()
        {
            return false;
        }
        let list = self.synapses.entry(pre_id).or_default();
        for syn in list.iter_mut() {
            if syn.target_id == post_id && syn.is_apical == is_apical {
                syn.weight = (syn.weight + delta_w).clamp(0.0, max_w);
                if delta_w > 0.0 {
                    syn.consolidation_count = syn.consolidation_count.saturating_add(1);
                }
                return true;
            }
        }
        if delta_w > 0.0 {
            list.push(Synapse {
                target_id: post_id,
                weight: delta_w.min(max_w),
                is_apical,
                consolidation_count: 1,
            });
            return true;
        }
        false
    }

    /// Returns what neurons are currently predicted to happen next based on active apical synapses
    /// from the given set of active neurons.
    pub fn predict_next_from(&self, active_ids: &[u32], min_weight: f32) -> Vec<(u32, f32)> {
        let mut scores: FxHashMap<u32, f32> = FxHashMap::default();
        for &src in active_ids {
            if let Some(syns) = self.synapses.get(&src) {
                for syn in syns.iter() {
                    if syn.is_apical && syn.weight >= min_weight {
                        *scores.entry(syn.target_id).or_insert(0.0) += syn.weight;
                    }
                }
            }
        }
        let mut out: Vec<(u32, f32)> = scores.into_iter().collect();
        out.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        out
    }

    /// Executes a single event-driven tick across the neural fabric.
    /// Complexity is strictly O(active_events) — millions of silent neurons cost 0 CPU.
    pub fn step(&mut self, learn_enabled: bool) -> StepReport {
        let tick = self.current_tick;
        let mut touched_set: FxHashSet<u32> = FxHashSet::default();
        let mut touched_list: Vec<u32> = Vec::new();

        // 1. Deliver queued sensory / internal events to Basal dendrites
        let queued = std::mem::take(&mut self.event_queue);
        for ev in &queued {
            let idx = ev.source_id as usize;
            if idx < self.neurons.len() {
                self.neurons[idx].integrate(tick, ev.amplitude, false);
                if touched_set.insert(ev.source_id) {
                    touched_list.push(ev.source_id);
                }
                // Propagate feedforward basal synapses from direct sensory inputs
                let ff_targets: SmallVec<[(u32, f32); 8]> = self
                    .synapses
                    .get(&ev.source_id)
                    .map(|list| {
                        list.iter()
                            .filter(|s| !s.is_apical && s.weight > 0.05)
                            .map(|s| (s.target_id, s.weight * ev.amplitude))
                            .collect()
                    })
                    .unwrap_or_default();

                for (target_id, current) in ff_targets {
                    if (target_id as usize) < self.neurons.len() {
                        self.neurons[target_id as usize].integrate(tick, current, false);
                        if touched_set.insert(target_id) {
                            touched_list.push(target_id);
                        }
                    }
                }
            }
        }

        // 2. Group touched neurons by micro-column and apply k-Winner-Take-All (kWTA) lateral inhibition
        let mut columns: FxHashMap<u32, SmallVec<[(u32, f32); 8]>> = FxHashMap::default();
        for &nid in &touched_list {
            let n = &mut self.neurons[nid as usize];
            n.lazy_sync(tick);
            columns.entry(n.column_id).or_default().push((nid, n.basal_v));
        }

        let mut winners: Vec<u32> = Vec::new();
        for (_col_id, mut candidates) in columns {
            candidates.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            for (rank, &(nid, _v)) in candidates.iter().enumerate() {
                if rank < self.kwta_winners_per_column {
                    winners.push(nid);
                } else {
                    // Lateral inhibition suppresses non-winners in the same micro-column
                    self.neurons[nid as usize].basal_v *= 0.2;
                }
            }
        }

        // 3. Evaluate somatic firing on winning candidates & classify Predicted vs. Surprise Burst
        let mut active_spikes: Vec<SpikeEvent> = Vec::new();
        let mut predicted_matches: Vec<u32> = Vec::new();
        let mut unpredicted_bursts: Vec<u32> = Vec::new();
        let mut fired_set: FxHashSet<u32> = FxHashSet::default();

        for nid in winners {
            if let Some(kind) =
                self.neurons[nid as usize].evaluate_soma(tick, self.predictive_window_ticks)
            {
                fired_set.insert(nid);
                match kind {
                    SpikeKind::PredictedSingleSpike => predicted_matches.push(nid),
                    SpikeKind::SurprisePlateauBurst => unpredicted_bursts.push(nid),
                    SpikeKind::ApicalPrediction => {}
                }
                active_spikes.push(SpikeEvent {
                    source_id: nid,
                    tick,
                    amplitude: 1.0,
                    kind,
                });
            }
        }

        // 4. Detect Failed Predictions (Omission Surprise):
        // Neurons that were predicted to fire on this tick by apical dendrites, but did NOT fire.
        let prev_predictions = std::mem::take(&mut self.pending_predictions);
        let mut failed_predictions: Vec<u32> = Vec::new();
        for pred_nid in prev_predictions {
            if !fired_set.contains(&pred_nid) {
                failed_predictions.push(pred_nid);
            }
        }

        // 5. Local 3-Factor BTSP & Predictive Error Plasticity
        // Triggered ONLY when surprise occurs (either unpredicted burst or failed prediction).
        let mut plastic_updates = 0usize;
        let window = self.btsp_window_ticks;
        let lr = self.btsp_one_shot_lr;

        // Prune expired BTSP eligibility history
        self.btsp_history
            .retain(|&(past_tick, _)| tick.saturating_sub(past_tick) <= window);

        if learn_enabled && (!unpredicted_bursts.is_empty() || !failed_predictions.is_empty()) {
            // (a) One-shot BTSP causal predictive wiring:
            // Any neuron active in the previous ticks (eligibility > 0) wires an Apical predictive
            // synapse onto the newly bursting neuron so next time Alpha 7 predicts it!
            let eligible_pre: Vec<(u32, f32)> = self
                .btsp_history
                .iter()
                .filter(|&&(past_tick, _)| past_tick < tick)
                .map(|&(past_tick, pre_id)| {
                    let dt = tick.saturating_sub(past_tick);
                    let elig = 1.0 / (1.0 + 0.25 * (dt as f32));
                    (pre_id, elig)
                })
                .collect();

            for &burst_post in &unpredicted_bursts {
                for &(pre_id, elig) in &eligible_pre {
                    if self.upsert_synapse(pre_id, burst_post, lr * elig, true, 1.5) {
                        plastic_updates += 1;
                    }
                }
            }

            // (b) Failed Prediction Analysis & Depression:
            // If `pre_id` was active just before `failed_id` was falsely predicted, weaken that false prediction!
            for &failed_post in &failed_predictions {
                for &(pre_id, elig) in &eligible_pre {
                    if self.upsert_synapse(pre_id, failed_post, -0.35 * elig, true, 1.5) {
                        plastic_updates += 1;
                    }
                }
                // Reset the unfulfilled apical potential after analyzing the failure
                if (failed_post as usize) < self.neurons.len() {
                    self.neurons[failed_post as usize].apical_v = 0.0;
                    self.neurons[failed_post as usize].last_predicted_tick = u32::MAX;
                }
            }
        }

        // 6. Forward Apical Prediction for Tick + 1:
        // Every neuron that fired in `tick` projects through its Apical synapses to prime
        // expected neurons for `tick + 1`.
        for ev in &active_spikes {
            self.btsp_history.push((tick, ev.source_id));
            let apical_targets: SmallVec<[(u32, f32); 8]> = self
                .synapses
                .get(&ev.source_id)
                .map(|list| {
                    list.iter()
                        .filter(|s| s.is_apical && s.weight > 0.20)
                        .map(|s| (s.target_id, s.weight))
                        .collect()
                })
                .unwrap_or_default();

            for (target_id, weight) in apical_targets {
                self.inject_apical_prediction(target_id, weight);
            }
        }

        let total_events =
            predicted_matches.len() + unpredicted_bursts.len() + failed_predictions.len();
        let surprise_score = if total_events == 0 {
            0.0
        } else {
            ((unpredicted_bursts.len() + failed_predictions.len()) as f32) / (total_events as f32)
        };

        self.current_tick = self.current_tick.saturating_add(1);

        StepReport {
            tick,
            total_neurons: self.neurons.len(),
            touched_neurons: touched_list.len(),
            active_spikes,
            predicted_matches,
            surprise: SurpriseAnalysis {
                tick,
                failed_predictions,
                unpredicted_bursts,
                surprise_score,
                plastic_updates,
            },
        }
    }
}
