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
    /// Law L1 (`FABRIC-LESION`): when true, the neural substrate is ablated to test whether
    /// an observed capability genuinely depends on the neural fabric or is a prosthetic tool.
    #[serde(default)]
    pub lesioned: bool,
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
            lesioned: false,
        }
    }

    /// Law L1 (`FABRIC-LESION`): Wipes all synapses, resets all active neuron potentials and thresholds,
    /// clears pending queues, and marks the fabric as lesioned. Any capability that survives `zero_lesion()`
    /// is a non-neural prosthetic (`TOOL`), not brain understanding.
    pub fn zero_lesion(&mut self) {
        self.synapses.clear();
        self.event_queue.clear();
        self.pending_predictions.clear();
        self.btsp_history.clear();
        for n in &mut self.neurons {
            if n.last_update_tick > 0 || n.maturity_count > 0 || (n.threshold - 1.0).abs() > 1e-4 {
                n.reset_lesion();
            }
        }
        self.lesioned = true;
    }

    /// Lesions all neurons and synapses belonging to a specific `Modality` pool.
    pub fn lesion_modality(&mut self, target_modality: Modality) {
        let mod_u8 = target_modality as u8;
        let mut lesioned_ids: FxHashSet<u32> = FxHashSet::default();
        for (idx, n) in self.neurons.iter_mut().enumerate() {
            if n.modality == mod_u8
                && (n.last_update_tick > 0 || self.neuron_to_trait.contains_key(&(idx as u32)))
            {
                n.reset_lesion();
                lesioned_ids.insert(idx as u32);
            }
        }
        for id in &lesioned_ids {
            self.synapses.remove(id);
            self.pending_predictions.remove(id);
        }
        for list in self.synapses.values_mut() {
            list.retain(|s| !lesioned_ids.contains(&s.target_id));
        }
        self.event_queue
            .retain(|ev| !lesioned_ids.contains(&ev.source_id));
        self.btsp_history
            .retain(|&(_, nid)| !lesioned_ids.contains(&nid));
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
            n.column_id = ((modality as u32) * 1000 + (id % 256)) as u16;
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
        if self.lesioned
            || pre_id == post_id
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
        if self.lesioned {
            return Vec::new();
        }
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

    /// Causal fabric readout (`Fixes D2/V-02`): maps `active_traits` to their neuron IDs,
    /// queries `predict_next_from` over the spiking fabric's apical synapses, and returns
    /// predicted `(trait_key, synaptic_drive)` pairs. Returns empty when `self.lesioned` is true.
    pub fn predict_next_traits(
        &self,
        active_traits: &[String],
        min_weight: f32,
    ) -> Vec<(String, f32)> {
        if self.lesioned {
            return Vec::new();
        }
        let active_ids: Vec<u32> = active_traits
            .iter()
            .filter_map(|t| self.trait_to_neuron.get(t).copied())
            .collect();
        self.predict_next_from(&active_ids, min_weight)
            .into_iter()
            .filter_map(|(nid, score)| self.neuron_to_trait.get(&nid).map(|t| (t.clone(), score)))
            .collect()
    }

    /// Executes a single event-driven tick across the neural fabric.
    /// Complexity is strictly O(active_events) — millions of silent neurons cost 0 CPU.
    pub fn step(&mut self, learn_enabled: bool) -> StepReport {
        let tick = self.current_tick;
        if self.lesioned {
            self.event_queue.clear();
            self.pending_predictions.clear();
            self.current_tick = self.current_tick.saturating_add(1);
            return StepReport {
                tick,
                total_neurons: self.neurons.len(),
                touched_neurons: 0,
                active_spikes: Vec::new(),
                predicted_matches: Vec::new(),
                surprise: SurpriseAnalysis {
                    tick,
                    failed_predictions: Vec::new(),
                    unpredicted_bursts: Vec::new(),
                    surprise_score: 0.0,
                    plastic_updates: 0,
                },
            };
        }

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
            columns
                .entry(n.column_id as u32)
                .or_default()
                .push((nid, n.basal_v));
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

        // 5. Local 3-Factor BTSP & Predictive Error Plasticity (fixes N8 deduplication/budget & N9 confirmation consolidation)
        let mut plastic_updates = 0usize;
        let window = self.btsp_window_ticks;
        let lr = self.btsp_one_shot_lr;

        // Prune expired BTSP eligibility history
        self.btsp_history
            .retain(|&(past_tick, _)| tick.saturating_sub(past_tick) <= window);

        if learn_enabled
            && (!unpredicted_bursts.is_empty()
                || !failed_predictions.is_empty()
                || !predicted_matches.is_empty())
        {
            // Deduplicate eligible predecessors (keep highest eligibility per pre_id, budgeted to top 8)
            let mut elig_map: FxHashMap<u32, f32> = FxHashMap::default();
            for &(past_tick, pre_id) in &self.btsp_history {
                if past_tick < tick {
                    let dt = tick.saturating_sub(past_tick);
                    let elig = 1.0 / (1.0 + 0.25 * (dt as f32));
                    let entry = elig_map.entry(pre_id).or_insert(0.0);
                    if elig > *entry {
                        *entry = elig;
                    }
                }
            }
            let mut eligible_pre: Vec<(u32, f32)> = elig_map.into_iter().collect();
            eligible_pre.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            eligible_pre.truncate(8);

            // (a) One-shot BTSP causal predictive wiring (budgeted to top-8 eligible predecessors):
            for &burst_post in &unpredicted_bursts {
                for &(pre_id, elig) in &eligible_pre {
                    if self.upsert_synapse(pre_id, burst_post, lr * elig, true, 1.5) {
                        plastic_updates += 1;
                    }
                }
            }

            // (b) Confirmed Prediction Consolidation (fixes N9):
            for &matched_post in &predicted_matches {
                for &(pre_id, elig) in &eligible_pre {
                    if self.upsert_synapse(pre_id, matched_post, 0.08 * elig, true, 1.5) {
                        plastic_updates += 1;
                    }
                }
            }

            // (c) Failed Prediction Analysis, Depression & Zeigarnik Uneasiness Accumulation:
            for &failed_post in &failed_predictions {
                for &(pre_id, elig) in &eligible_pre {
                    if self.upsert_synapse(pre_id, failed_post, -0.35 * elig, true, 1.5) {
                        plastic_updates += 1;
                    }
                }
                if (failed_post as usize) < self.neurons.len() {
                    // Instead of erasing the error in 1 tick, accumulate persistent Zeigarnik uneasiness tension!
                    self.neurons[failed_post as usize].last_predicted_tick = u32::MAX;
                    self.neurons[failed_post as usize].accumulate_uneasiness(0.45);
                }
            }
        }

        // 6. Forward Apical Prediction AND Multi-Hop Basal Recurrence for Tick + 1 (fixes N1/V-07):
        let next_tick = tick.saturating_add(1);
        for ev in &active_spikes {
            if !self
                .btsp_history
                .iter()
                .any(|&(t, id)| t == tick && id == ev.source_id)
            {
                self.btsp_history.push((tick, ev.source_id));
            }
            let (apical_targets, basal_targets): (
                SmallVec<[(u32, f32); 8]>,
                SmallVec<[(u32, f32); 8]>,
            ) = self
                .synapses
                .get(&ev.source_id)
                .map(|list| {
                    let ap = list
                        .iter()
                        .filter(|s| s.is_apical && s.weight > 0.20)
                        .map(|s| (s.target_id, s.weight))
                        .collect();
                    let mut bs: SmallVec<[(u32, f32); 8]> = list
                        .iter()
                        .filter(|s| !s.is_apical && s.weight > 0.05)
                        .map(|s| (s.target_id, s.weight * ev.amplitude))
                        .collect();
                    bs.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
                    bs.truncate(8);
                    (ap, bs)
                })
                .unwrap_or_default();

            for (target_id, weight) in apical_targets {
                self.inject_apical_prediction(target_id, weight);
            }
            // Enqueue recurrent basal targets for `tick + 1` if not already fired this tick
            for (target_id, drive) in basal_targets {
                if !fired_set.contains(&target_id) && self.event_queue.len() < 512 {
                    self.event_queue.push(SpikeEvent {
                        source_id: target_id,
                        tick: next_tick,
                        amplitude: drive,
                        kind: SpikeKind::PredictedSingleSpike,
                    });
                }
            }
        }

        let total_events =
            predicted_matches.len() + unpredicted_bursts.len() + failed_predictions.len();
        let surprise_score = if total_events == 0 {
            0.0
        } else {
            ((unpredicted_bursts.len() + failed_predictions.len()) as f32) / (total_events as f32)
        };

        self.current_tick = next_tick;

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
