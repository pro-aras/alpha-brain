//! Alpha 7 Biological Multi-Compartment Dendritic Neuron Model
//!
//! Grounded in:
//! 1. Dendritic Predictive Coding (Mikulasch et al., PNAS / arXiv; Larkum, TINS):
//!    - Basal compartment: Bottom-up sensory reality (Eyes, Ears, Hands, Smell, Senses).
//!    - Apical/Distal compartment: Top-down predictions & goal-directed expectations.
//! 2. Multiplexed Single-Spike vs. Plateau Bursting (Payeur, Naud, Sacramento, Richards,
//!    Nature Neuroscience 2021):
//!    - Predicted match -> SingleSpike (quiet inference, suppresses downstream surprise).
//!    - Unpredicted reality OR failed prediction -> Dendritic Ca2+ Plateau Burst (Surprise),
//!      which unlocks local 3-factor plasticity.
//! 3. Behavioral Timescale Synaptic Plasticity - BTSP (Bittner et al., Science 2017;
//!    Magee & Grienberger, Science 2020):
//!    - Lazy timestamp-based eligibility traces over behavioral windows (seconds/ticks)
//!      enable 1-2 shot concept & episodic memory formation without global backprop.
//! 4. Lazy Event-Driven State Evaluation:
//!    - Neurons never decay on a global clock loop. Decay is computed lazily only when an
//!      event reaches the neuron, giving O(active_spikes) complexity for millions of neurons.

use serde::{Deserialize, Serialize};

/// Functional region / sensory modality of a neuron or micro-column.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[repr(u8)]
pub enum Modality {
    Visual = 0,      // Eyes: shape, color, motion, spatial parts, code tokens
    Auditory = 1,    // Ears: spoken words, phonemes, acoustic signatures (purr, tone)
    TactileHand = 2, // Hands: touch texture, motor actions, code manipulation
    Olfactory = 3,   // Smell: chemical/environmental markers & state signatures
    Internal = 4,    // Internal Senses: proprioception, surprise/curiosity, energy, familiarity
    Association = 5, // Cortical multi-modal trait integration micro-columns
    ConceptHub = 6,  // Hippocampal-Cortical Concept Cell / Invariant Anchor
    Language = 7,    // Grounded lexical / symbol assemblies
    MotorGoal = 8,   // Action / scenario simulation & goal-directed effectors
}

impl Modality {
    pub fn from_u8(v: u8) -> Self {
        match v {
            0 => Modality::Visual,
            1 => Modality::Auditory,
            2 => Modality::TactileHand,
            3 => Modality::Olfactory,
            4 => Modality::Internal,
            5 => Modality::Association,
            6 => Modality::ConceptHub,
            7 => Modality::Language,
            _ => Modality::MotorGoal,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            Modality::Visual => "eyes",
            Modality::Auditory => "ears",
            Modality::TactileHand => "hands",
            Modality::Olfactory => "smell",
            Modality::Internal => "senses",
            Modality::Association => "association",
            Modality::ConceptHub => "concept_hub",
            Modality::Language => "language",
            Modality::MotorGoal => "motor_goal",
        }
    }

    pub fn from_str(s: &str) -> Self {
        let prefix = s
            .trim()
            .split(':')
            .next()
            .unwrap_or(s)
            .trim()
            .to_ascii_lowercase();
        match prefix.as_str() {
            "eyes" | "visual" | "vision" | "sight" => Modality::Visual,
            "ears" | "auditory" | "audio" | "sound" | "hearing" => Modality::Auditory,
            "hands" | "tactile" | "touch" | "motor" | "hand" => Modality::TactileHand,
            "smell" | "olfactory" | "scent" | "odor" => Modality::Olfactory,
            "senses" | "internal" | "proprioception" | "body" => Modality::Internal,
            "association" | "trait" => Modality::Association,
            "concept" | "concept_hub" | "hippocampus" => Modality::ConceptHub,
            "language" | "word" | "speech" | "code" | "mouth" => Modality::Language,
            _ => Modality::MotorGoal,
        }
    }
}

/// Output event type emitted by a soma (Payeur et al., Nature Neuroscience 2021).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum SpikeKind {
    /// Quiet regular spike: bottom-up input matched apical prediction (expected flow).
    PredictedSingleSpike = 0,
    /// Unpredicted bottom-up sensory/trait activation OR novelty plateau burst:
    /// triggers downstream attention and BTSP 1-shot plasticity.
    SurprisePlateauBurst = 1,
    /// Top-down predictive / scenario rollout signal targeting apical dendrites.
    ApicalPrediction = 2,
}

/// A single sparse event on the SpikeEventQueue.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct SpikeEvent {
    pub source_id: u32,
    pub tick: u32,
    pub amplitude: f32,
    pub kind: SpikeKind,
}

/// Directed synapse connecting a pre-synaptic neuron to either the Basal (feedforward)
/// or Apical (predictive/feedback) compartment of a post-synaptic neuron.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Synapse {
    pub target_id: u32,
    pub weight: f32,
    /// True if this synapse targets the Apical (predictive/contextual) dendrite;
    /// False if it targets the Basal (sensory/feedforward) dendrite.
    pub is_apical: bool,
    /// Count of co-activations across distinct episodes (tracks trait invariance vs incidental noise).
    pub consolidation_count: u16,
}

/// Compact 32-byte biological neuron state designed for contiguous Arena allocation.
/// Supports millions of neurons in RAM with zero idle CPU cost via lazy tick evaluation.
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[repr(C)]
pub struct DendriticNeuron {
    /// Bottom-up sensory/feedforward membrane potential (Basal dendrites).
    pub basal_v: f32,
    /// Top-down predictive/goal membrane potential (Apical dendrites).
    pub apical_v: f32,
    /// Adaptive firing threshold (homeostatic intrinsic excitability).
    pub threshold: f32,
    /// Last simulation tick when basal/apical potentials were lazily decayed/updated.
    pub last_update_tick: u32,
    /// Last tick when this neuron emitted a somatic spike or burst (used for lazy STDP & BTSP eligibility).
    pub last_spike_tick: u32,
    /// Last tick when apical dendrites placed this neuron into a depolarized predictive state.
    pub last_predicted_tick: u32,
    /// Micro-column ID for fast local k-Winner-Take-All lateral inhibition.
    pub column_id: u16,
    /// Persistent Zeigarnik sub-threshold apical-basal dissonance / uneasiness tension (Q8.8 fixed-point, T_i = uneasiness_q8 / 256.0).
    /// Refuses to decay rapidly (tau ~ 10,000 ticks) and primes the neuron until a confirmed resolution discharges it.
    pub uneasiness_q8: u16,
    /// Modality / cortical region tag.
    pub modality: u8,
    /// Last spike kind emitted.
    pub last_spike_kind: u8,
    /// Total lifetime bursts (tracks familiarity / maturation).
    pub maturity_count: u16,
}

impl DendriticNeuron {
    #[inline]
    pub fn new(column_id: u32, modality: Modality) -> Self {
        Self {
            basal_v: 0.0,
            apical_v: 0.0,
            threshold: 1.0,
            last_update_tick: 0,
            last_spike_tick: u32::MAX,
            last_predicted_tick: u32::MAX,
            column_id: (column_id & 0xFFFF) as u16,
            uneasiness_q8: 0,
            modality: modality as u8,
            last_spike_kind: SpikeKind::PredictedSingleSpike as u8,
            maturity_count: 0,
        }
    }

    /// Returns the neuron's current Zeigarnik uneasiness tension $T_i \in [0.0, 255.99]$.
    #[inline]
    pub fn uneasiness(&self) -> f32 {
        (self.uneasiness_q8 as f32) / 256.0
    }

    /// Accumulates persistent sub-threshold dendritic uneasiness $T_i$ when an apical prediction fails,
    /// a GABAergic contradiction occurs, or an ungrounded shortcut is detected.
    #[inline]
    pub fn accumulate_uneasiness(&mut self, delta_t: f32) {
        let cur = self.uneasiness();
        let next = (cur + delta_t.max(0.0)).clamp(0.0, 250.0);
        self.uneasiness_q8 = (next * 256.0).round() as u16;
        // Inject sub-threshold tonic apical bias (< 0.40 so it primes recall without hallucinating a prediction)
        let tonic_bias = (0.18 * next).min(0.35);
        if self.apical_v < tonic_bias {
            self.apical_v = tonic_bias;
        }
    }

    /// Discharges a fraction `rho in [0.0, 1.0]` of the neuron's Zeigarnik uneasiness when resolved.
    #[inline]
    pub fn resolve_uneasiness(&mut self, rho: f32) {
        let keep = (1.0 - rho.clamp(0.0, 1.0)).max(0.0);
        self.uneasiness_q8 = ((self.uneasiness_q8 as f32) * keep).round() as u16;
    }

    /// Resets neuron membrane potentials, thresholds, and spike history for `FABRIC-LESION` ablation.
    #[inline]
    pub fn reset_lesion(&mut self) {
        self.basal_v = 0.0;
        self.apical_v = 0.0;
        self.threshold = 1.0;
        self.last_update_tick = 0;
        self.last_spike_tick = u32::MAX;
        self.last_predicted_tick = u32::MAX;
        self.uneasiness_q8 = 0;
        self.last_spike_kind = SpikeKind::PredictedSingleSpike as u8;
        self.maturity_count = 0;
    }

    /// Lazily decays basal and apical potentials (and relaxes homeostatic threshold toward 1.0)
    /// to `current_tick` using fast rational approximation of exponential decay.
    /// Silent neurons cost 0 CPU until an event arrives.
    #[inline]
    pub fn lazy_sync(&mut self, current_tick: u32) {
        let dt = current_tick.saturating_sub(self.last_update_tick);
        if dt == 0 {
            return;
        }
        if dt >= 32 {
            self.basal_v = 0.0;
            self.apical_v = 0.0;
        } else {
            // Fast biological membrane decay: basal tau ~ 4 ticks, apical plateau tau ~ 8 ticks
            let basal_decay = 1.0 / (1.0 + 0.35 * (dt as f32));
            let apical_decay = 1.0 / (1.0 + 0.15 * (dt as f32));
            self.basal_v *= basal_decay;
            self.apical_v *= apical_decay;
        }
        // Slow Zeigarnik uneasiness decay (tau_leak ~ 10,000 ticks) + tonic sub-threshold apical priming
        if self.uneasiness_q8 > 0 {
            let zeig_decay = 1.0 / (1.0 + 0.0001 * (dt as f32));
            self.uneasiness_q8 = ((self.uneasiness_q8 as f32) * zeig_decay).round() as u16;
            let tonic_bias = (0.18 * self.uneasiness()).min(0.35);
            if self.apical_v < tonic_bias {
                self.apical_v = tonic_bias;
            }
        }
        // Homeostatic intrinsic threshold relaxation toward baseline 1.0 (fixes N3/V-05 ratchet)
        if (self.threshold - 1.0).abs() > 1e-4 {
            let th_decay = 1.0 / (1.0 + 0.04 * (dt as f32));
            self.threshold = 1.0 + (self.threshold - 1.0) * th_decay;
        }
        self.last_update_tick = current_tick;
    }

    /// Integrate incoming synaptic current into either the Basal or Apical compartment.
    #[inline]
    pub fn integrate(&mut self, current_tick: u32, delta_v: f32, is_apical: bool) {
        self.lazy_sync(current_tick);
        if is_apical {
            // Genuine NMDA-like supralinear dendritic amplification when apical tuft crosses 0.40
            let raw_next = self.apical_v + delta_v;
            let nmda_boost = if raw_next > 0.40 && delta_v > 0.0 {
                1.0 + 0.35 * (raw_next - 0.40).clamp(0.0, 1.0)
            } else {
                1.0
            };
            self.apical_v += delta_v * nmda_boost;
            if self.apical_v >= 0.45 {
                self.last_predicted_tick = current_tick;
            }
        } else {
            self.basal_v += delta_v;
        }
    }

    /// Returns true if the neuron was recently predicted by its apical dendrites within the predictive window.
    #[inline]
    pub fn is_predicted(&self, current_tick: u32, window_ticks: u32) -> bool {
        if self.last_predicted_tick == u32::MAX {
            return false;
        }
        current_tick.saturating_sub(self.last_predicted_tick) <= window_ticks
            || self.apical_v >= 0.45
    }

    /// Computes Behavioral Timescale Synaptic Plasticity (BTSP) eligibility trace at `current_tick`.
    /// In biology (Magee & Grienberger, Science 2020), active synapses leave a seconds-long
    /// eligibility trace that converts into one-shot weight updates if a Plateau Burst occurs.
    #[inline]
    pub fn btsp_eligibility(&self, current_tick: u32, btsp_window_ticks: u32) -> f32 {
        if self.last_spike_tick == u32::MAX {
            return 0.0;
        }
        let dt = current_tick.saturating_sub(self.last_spike_tick);
        if dt > btsp_window_ticks {
            return 0.0;
        } else {
            // Smooth eligibility kernel peaking for recent co-activation and decaying over the window
            1.0 / (1.0 + 0.25 * (dt as f32))
        }
    }

    /// Evaluates whether the soma crosses firing threshold, returning `Some(SpikeKind)` if it fires.
    /// - If Basal reality is strong AND Apical prediction was already present -> `PredictedSingleSpike`
    ///   (which also discharges persistent Zeigarnik uneasiness $T_i$!)
    /// - If Basal reality is strong WITHOUT Apical prediction -> `SurprisePlateauBurst`
    #[inline]
    pub fn evaluate_soma(&mut self, current_tick: u32, predictive_window: u32) -> Option<SpikeKind> {
        self.lazy_sync(current_tick);

        // Apical depolarization + Zeigarnik uneasiness tension lowers effective somatic threshold
        let priming_bonus = (self.apical_v * 0.25 + self.uneasiness() * 0.12).min(0.35);
        let effective_threshold = (self.threshold - priming_bonus).max(0.45);

        if self.basal_v >= effective_threshold {
            let predicted = self.is_predicted(current_tick, predictive_window);
            let kind = if predicted {
                // Confirmed prediction discharges persistent Zeigarnik uneasiness!
                if self.uneasiness_q8 > 0 {
                    self.resolve_uneasiness(0.75);
                }
                SpikeKind::PredictedSingleSpike
            } else {
                self.maturity_count = self.maturity_count.saturating_add(1);
                SpikeKind::SurprisePlateauBurst
            };

            // Reset basal membrane after firing and apply slight intrinsic homeostatic adaptation
            self.basal_v = 0.0;
            self.last_spike_tick = current_tick;
            self.last_spike_kind = kind as u8;
            self.threshold = (self.threshold + 0.01).min(1.35);
            Some(kind)
        } else {
            None
        }
    }
}
