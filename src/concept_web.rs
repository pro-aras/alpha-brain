//! Alpha 7 Hippocampal-Cortical Conceptual Knowledge Web & Episodic Memory
//!
//! Implements:
//! 1. One-Shot & Two-Shot Infant-Like Concept Formation (Quiroga Concept Cells + BTSP):
//!    - 1st interaction: Immediately binds active multimodal traits (eyes, ears, hands,
//!      smell, senses), grounded words, and affordances into a Concept Hub assembly.
//!    - 2nd interaction: Separates Core Invariant Traits (shared across instances, e.g.,
//!      whiskers, pointy ears, feline gait) from Variable/Incidental Traits (e.g., orange
//!      vs. black fur), enabling recognition of ANY instance of that concept.
//! 2. Grounded Language & Code Understanding:
//!    - Words and code primitives are wired directly to sensory-motor traits and causal
//!      input->output transitions, so speaking/thinking a word reactivates its sensory-motor
//!      meaning.
//! 3. Direct User Episodic Memories:
//!    - Stores autobiographical interaction episodes with the user, indexed by concepts,
//!      traits, surprise level, and causal outcomes.

use crate::fabric::SparseNeuralFabric;
use crate::neuron::Modality;
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};

/// A single sensory, motor, or structural trait bound to a Concept Node.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraitBinding {
    pub trait_key: String,
    pub modality: String,
    pub neuron_id: u32,
    /// Synaptic binding strength in [0.0, 1.0].
    pub weight: f32,
    /// Number of exposures of this concept in which this trait was present.
    pub seen_count: u32,
    /// Invariance ratio `seen_count / concept_exposures`.
    /// High (>= 0.75 after 2+ exposures) = Core Invariant Trait; Low = Variable/Incidental Trait.
    pub invariance: f32,
}

/// A grounded Concept Assembly in the Conceptual Knowledge Web (e.g., "cat", "user", "python_loop").
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptNode {
    pub name: String,
    pub hub_neuron_id: u32,
    pub word_neuron_id: u32,
    pub exposures: u32,
    /// Familiarization level in [0.0, 1.0] — reaches high familiarity after 1-2 interactions.
    pub familiarity: f32,
    /// Bound traits keyed by `trait_key` (e.g. `"eyes:whiskers"`).
    pub traits: FxHashMap<String, TraitBinding>,
    /// Grounded words/phrases associated with this concept.
    pub grounded_words: Vec<String>,
    /// Causal affordances / actions or code patterns associated with this concept
    /// `(action_or_code, expected_effect_trait)`.
    pub causal_affordances: Vec<(String, String)>,
}

impl ConceptNode {
    /// Returns traits classified as Core Invariants (essential defining traits of the concept).
    pub fn core_invariants(&self) -> Vec<&TraitBinding> {
        let mut list: Vec<&TraitBinding> = self
            .traits
            .values()
            .filter(|t| {
                if self.exposures <= 1 {
                    t.weight >= 0.5
                } else {
                    t.invariance >= 0.65 && t.weight >= 0.55
                }
            })
            .collect();
        list.sort_by(|a, b| b.weight.partial_cmp(&a.weight).unwrap_or(std::cmp::Ordering::Equal));
        list
    }

    /// Returns traits classified as Variable / Incidental surface features (e.g., fur color).
    pub fn variable_traits(&self) -> Vec<&TraitBinding> {
        let mut list: Vec<&TraitBinding> = self
            .traits
            .values()
            .filter(|t| self.exposures >= 2 && t.invariance < 0.65)
            .collect();
        list.sort_by(|a, b| b.weight.partial_cmp(&a.weight).unwrap_or(std::cmp::Ordering::Equal));
        list
    }
}

/// Direct Autobiographical / Episodic Memory formed with the user or environment.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpisodicMemory {
    pub episode_id: u64,
    pub tick: u32,
    pub partner: String, // e.g. "user" or "sandbox"
    pub summary: String,
    pub active_concepts: Vec<String>,
    pub observed_traits: Vec<String>,
    pub action_or_code: Option<String>,
    pub outcome_traits: Vec<String>,
    pub surprise_score: f32,
}

/// Match result when recognizing concepts from a sparse sensory-motor trait pattern.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptRecognition {
    pub concept_name: String,
    pub confidence: f32,
    pub matched_core_traits: Vec<String>,
    pub matched_variable_traits: Vec<String>,
    pub familiarity: f32,
}

/// The Hippocampal-Cortical Conceptual Knowledge Web and Episodic Memory store.
#[derive(Serialize, Deserialize, Default)]
pub struct ConceptualKnowledgeWeb {
    pub concepts: FxHashMap<String, ConceptNode>,
    pub episodes: Vec<EpisodicMemory>,
    /// Directed conceptual associations `(concept_a, relation, concept_b, weight)`.
    pub relations: Vec<(String, String, String, f32)>,
}

impl ConceptualKnowledgeWeb {
    pub fn new() -> Self {
        Self {
            concepts: FxHashMap::default(),
            episodes: Vec::new(),
            relations: Vec::new(),
        }
    }

    /// Learns or refines a concept from a single interaction (1-2 shot infant-like learning),
    /// wiring the sensory-motor traits and word directly into the `SparseNeuralFabric`.
    pub fn experience_concept(
        &mut self,
        fabric: &mut SparseNeuralFabric,
        concept_name: &str,
        sensory_traits: &[String],
        associated_words: &[String],
        affordance: Option<(String, String)>,
        partner: &str,
        surprise_score: f32,
    ) -> ConceptNode {
        let hub_key = format!("concept:{}", concept_name.to_lowercase());
        let word_key = format!("word:{}", concept_name.to_lowercase());
        let hub_neuron_id = fabric.ensure_trait_neuron(&hub_key, Modality::ConceptHub);
        let word_neuron_id = fabric.ensure_trait_neuron(&word_key, Modality::Language);

        // Wire bidirectional grounding between the word neuron and the concept hub
        fabric.upsert_synapse(word_neuron_id, hub_neuron_id, 0.90, false, 1.5);
        fabric.upsert_synapse(word_neuron_id, hub_neuron_id, 0.90, true, 1.5);
        fabric.upsert_synapse(hub_neuron_id, word_neuron_id, 0.90, true, 1.5);

        let node = self
            .concepts
            .entry(concept_name.to_lowercase())
            .or_insert_with(|| ConceptNode {
                name: concept_name.to_lowercase(),
                hub_neuron_id,
                word_neuron_id,
                exposures: 0,
                familiarity: 0.0,
                traits: FxHashMap::default(),
                grounded_words: vec![concept_name.to_lowercase()],
                causal_affordances: Vec::new(),
            });

        node.exposures += 1;
        // Infant-like familiarity curve: 1 exposure -> ~0.68, 2 exposures -> ~0.90, 3+ -> ~0.97+
        node.familiarity = 1.0 - (1.0 / (1.0 + 1.45 * (node.exposures as f32)).powi(2));

        // Filter external object-defining sensory traits (eyes, ears, hands, smell)
        // from internal self-homeostasis state (`senses:*`) and spoken user labels (`ears:heard_*`),
        // which belong to EpisodicMemory and GroundedWords respectively.
        let object_traits: Vec<String> = sensory_traits
            .iter()
            .filter(|t| !t.starts_with("senses:") && !t.starts_with("ears:heard_"))
            .cloned()
            .collect();

        let active_set: std::collections::HashSet<String> =
            object_traits.iter().cloned().collect();

        // 1. Update or bind newly observed object traits via 1-shot BTSP
        for trait_str in &object_traits {
            let modality_prefix = trait_str.split(':').next().unwrap_or("association");
            let modality = Modality::from_str(modality_prefix);
            let trait_nid = fabric.ensure_trait_neuron(trait_str, modality);

            let entry = node
                .traits
                .entry(trait_str.clone())
                .or_insert_with(|| TraitBinding {
                    trait_key: trait_str.clone(),
                    modality: modality.as_str().to_string(),
                    neuron_id: trait_nid,
                    weight: 0.65, // Strong 1-shot initial BTSP binding
                    seen_count: 0,
                    invariance: 1.0,
                });

            entry.seen_count += 1;
            entry.invariance = (entry.seen_count as f32) / (node.exposures as f32);
            if node.exposures > 1 && entry.seen_count > 1 {
                // Shared invariant across exposures boosts weight strongly
                entry.weight = (entry.weight + 0.22).min(1.0);
            }

            // Wire trait <-> concept hub in the neural fabric:
            // Basal synapse (trait -> concept hub for bottom-up recognition)
            fabric.upsert_synapse(trait_nid, hub_neuron_id, entry.weight * 0.55, false, 1.5);
            // Apical synapse (concept hub -> trait for top-down mental simulation/prediction)
            fabric.upsert_synapse(hub_neuron_id, trait_nid, entry.weight * 0.75, true, 1.5);
        }

        // 2. Recompute invariance for traits NOT present in this instance (separating core vs variable)
        let exposures = node.exposures;
        for (t_key, binding) in node.traits.iter_mut() {
            if !active_set.contains(t_key) {
                binding.invariance = (binding.seen_count as f32) / (exposures as f32);
                // Slightly relax weight of non-invariant surface trait (e.g. orange fur vs black fur)
                binding.weight = (binding.weight * 0.72).max(0.20);
            }
        }

        // 3. Ground additional spoken/written words to this concept
        for w in associated_words {
            let w_clean = w.to_lowercase();
            if !node.grounded_words.contains(&w_clean) {
                node.grounded_words.push(w_clean.clone());
            }
            let w_nid = fabric.ensure_trait_neuron(&format!("word:{}", w_clean), Modality::Language);
            fabric.upsert_synapse(w_nid, hub_neuron_id, 0.85, false, 1.5);
            fabric.upsert_synapse(hub_neuron_id, w_nid, 0.85, true, 1.5);
        }

        // 4. Record causal affordance / code behavior if provided
        let mut outcome_vec = Vec::new();
        let mut action_opt = None;
        if let Some((act, eff)) = affordance {
            action_opt = Some(act.clone());
            outcome_vec.push(eff.clone());
            if !node.causal_affordances.contains(&(act.clone(), eff.clone())) {
                node.causal_affordances.push((act.clone(), eff.clone()));
            }
            let act_nid =
                fabric.ensure_trait_neuron(&format!("hands:{}", act), Modality::TactileHand);
            let eff_nid = fabric.ensure_trait_neuron(&eff, Modality::Visual);
            // Wire causal prediction: Concept + Hand Action -> Apical prediction of Effect
            fabric.upsert_synapse(hub_neuron_id, act_nid, 0.70, true, 1.5);
            fabric.upsert_synapse(act_nid, eff_nid, 0.85, true, 1.5);
        }

        let snapshot = node.clone();

        // 5. Store direct autobiographical Episodic Memory with the user/partner
        let ep_id = (self.episodes.len() + 1) as u64;
        self.episodes.push(EpisodicMemory {
            episode_id: ep_id,
            tick: fabric.current_tick,
            partner: partner.to_string(),
            summary: format!(
                "Interacted with '{}' on concept '{}' (exposure #{}, familiarity {:.2})",
                partner, concept_name, snapshot.exposures, snapshot.familiarity
            ),
            active_concepts: vec![concept_name.to_lowercase()],
            observed_traits: sensory_traits.to_vec(),
            action_or_code: action_opt,
            outcome_traits: outcome_vec,
            surprise_score,
        });

        snapshot
    }

    /// Recognizes concepts from an arbitrary set of sensory traits (even on unseen instances
    /// with different surface traits, like a white cat after seeing an orange and black cat).
    pub fn recognize_from_traits(&self, observed_traits: &[String]) -> Vec<ConceptRecognition> {
        let exteroceptive_obs: Vec<&str> = observed_traits
            .iter()
            .map(|s| s.as_str())
            .filter(|s| !s.starts_with("senses:") && !s.starts_with("ears:heard_"))
            .collect();
        let obs_set: std::collections::HashSet<&str> = exteroceptive_obs.iter().copied().collect();
        let mut results = Vec::new();

        for node in self.concepts.values() {
            let mut matched_core = Vec::new();
            let mut matched_var = Vec::new();
            let mut core_score = 0.0f32;
            let mut total_core_possible = 0.0f32;
            let mut var_bonus = 0.0f32;

            for binding in node.traits.values() {
                let is_core = node.exposures <= 1 || binding.invariance >= 0.65;
                if is_core {
                    total_core_possible += binding.weight;
                    if obs_set.contains(binding.trait_key.as_str()) {
                        core_score += binding.weight;
                        matched_core.push(binding.trait_key.clone());
                    }
                } else if obs_set.contains(binding.trait_key.as_str()) {
                    var_bonus += binding.weight * 0.15;
                    matched_var.push(binding.trait_key.clone());
                }
            }

            if !matched_core.is_empty() && total_core_possible > 0.0 {
                // Count contradictory / novel exteroceptive traits (lateral inhibition against wrong concepts)
                let unmatched_obs = exteroceptive_obs
                    .iter()
                    .filter(|&&t| !node.traits.contains_key(t))
                    .count();

                // When >= 4 core invariants match, dendritic NMDA plateau locks in recognition
                // so incidental environmental traits (e.g. rain scent or novel fur color) do not
                // suppress recognition; when < 3 core invariants match, lateral inhibition is strong.
                let inhibition_per_unmatched = if matched_core.len() >= 4 {
                    0.015
                } else {
                    0.065
                };
                let lateral_inhibition = (unmatched_obs as f32) * inhibition_per_unmatched;

                // Dendritic NMDA-style nonlinear threshold on core invariant overlap:
                let core_ratio = core_score / total_core_possible;
                let nmda_amplification = if matched_core.len() >= 4 {
                    1.38
                } else if matched_core.len() == 3 {
                    1.20
                } else {
                    0.85
                };
                let confidence =
                    (core_ratio * nmda_amplification + var_bonus - lateral_inhibition).clamp(0.0, 1.0);
                if confidence >= 0.35 {
                    results.push(ConceptRecognition {
                        concept_name: node.name.clone(),
                        confidence,
                        matched_core_traits: matched_core,
                        matched_variable_traits: matched_var,
                        familiarity: node.familiarity,
                    });
                }
            }
        }

        results.sort_by(|a, b| {
            b.confidence
                .partial_cmp(&a.confidence)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        results
    }

    /// Grounded language comprehension: given a spoken/written sentence or code instruction,
    /// activates the underlying Concept Nodes, their core sensory-motor traits, and expected
    /// causal outcomes ("understanding the words it speaks and thinks on").
    pub fn understand_utterance(&self, text: &str) -> GroundedThought {
        let tokens: Vec<String> = text
            .split(|c: char| !c.is_alphanumeric() && c != '_')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_lowercase())
            .collect();

        let mut activated_concepts = Vec::new();
        let mut evoked_sensory_traits = Vec::new();
        let mut predicted_affordances = Vec::new();
        let mut recalled_episodes = Vec::new();

        for token in &tokens {
            for node in self.concepts.values() {
                if node.name == *token || node.grounded_words.contains(token) {
                    if !activated_concepts.contains(&node.name) {
                        activated_concepts.push(node.name.clone());
                        for core in node.core_invariants() {
                            if !evoked_sensory_traits.contains(&core.trait_key) {
                                evoked_sensory_traits.push(core.trait_key.clone());
                            }
                        }
                        for (act, eff) in &node.causal_affordances {
                            predicted_affordances.push((node.name.clone(), act.clone(), eff.clone()));
                        }
                    }
                }
            }
        }

        // Recall direct user episodic memories involving these concepts
        for ep in self.episodes.iter().rev() {
            if ep
                .active_concepts
                .iter()
                .any(|c| activated_concepts.contains(c))
            {
                recalled_episodes.push(ep.summary.clone());
                if recalled_episodes.len() >= 3 {
                    break;
                }
            }
        }

        GroundedThought {
            utterance: text.to_string(),
            activated_concepts,
            evoked_sensory_traits,
            predicted_affordances,
            recalled_episodes,
        }
    }
}

/// The internal grounded representation produced when Alpha 7 thinks or hears words.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GroundedThought {
    pub utterance: String,
    pub activated_concepts: Vec<String>,
    /// Sensory-motor traits mentally simulated via apical dendrites when thinking these words.
    pub evoked_sensory_traits: Vec<String>,
    /// Predicted `(concept, action_or_code, expected_effect)` transitions.
    pub predicted_affordances: Vec<(String, String, String)>,
    /// Relevant autobiographical memories with the user.
    pub recalled_episodes: Vec<String>,
}
