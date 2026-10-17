//! Alpha 7 Hippocampal-Cortical Conceptual Knowledge Web, Compositional Hierarchy & Sleep Replay
//!
//! Implements:
//! 1. One-Shot & Two-Shot Infant-Like Concept Formation (Quiroga Concept Cells + BTSP):
//!    - 1st interaction: Immediately binds active multimodal traits (eyes, ears, hands,
//!      smell, senses), grounded words, and affordances into a Concept Hub assembly.
//!    - 2nd interaction: Separates Core Invariant Traits (shared across instances, e.g.,
//!      whiskers, pointy ears, feline gait) from Variable/Incidental Traits (e.g., orange
//!      vs. black fur), enabling recognition of ANY instance of that concept.
//! 2. Phase 2B — Compositional Concept Hierarchy & Relational Comparison:
//!    - Automatically discovers shared core invariants across distinct concepts (e.g., `cat` and `dog`
//!      sharing `eyes:four_legs`, `hands:warm_body`) to induce parent categories (`is_a`,
//!      `shares_core_with`, `contrasts_with`) and answer comparative questions.
//! 3. Phase 2D — Hippocampal-Neocortical Sharp-Wave Ripple Replay & Sleep Consolidation:
//!    - Replays high-surprise episodic memories into `SparseNeuralFabric`, strengthens multi-episode
//!      invariant synapses, prunes weak incidental noise synapses, and consolidates categories.

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
    /// High (>= 0.65 after 2+ exposures) = Core Invariant Trait; Low = Variable/Incidental Trait.
    pub invariance: f32,
}

/// A grounded Concept Assembly in the Conceptual Knowledge Web (e.g., "cat", "user", "multiply_code").
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
        list.sort_by(|a, b| {
            b.weight
                .partial_cmp(&a.weight)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        list
    }

    /// Returns traits classified as Variable / Incidental surface features (e.g., fur color).
    pub fn variable_traits(&self) -> Vec<&TraitBinding> {
        let mut list: Vec<&TraitBinding> = self
            .traits
            .values()
            .filter(|t| self.exposures >= 2 && t.invariance < 0.65)
            .collect();
        list.sort_by(|a, b| {
            b.weight
                .partial_cmp(&a.weight)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        list
    }
}

fn default_episode_provenance() -> String {
    "lived".to_string()
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
    /// Provenance tag (`"lived"` vs `"taught"`).
    #[serde(default = "default_episode_provenance")]
    pub provenance: String,
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

/// Phase 2B: Structured comparison between two grounded concepts.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConceptComparison {
    pub concept_a: String,
    pub concept_b: String,
    pub shared_core_traits: Vec<String>,
    pub unique_to_a: Vec<String>,
    pub unique_to_b: Vec<String>,
    pub shared_categories: Vec<String>,
    pub similarity_score: f32,
    pub summary: String,
}

/// Phase 2D: Telemetry report produced by a Hippocampal-Neocortical Sleep Replay cycle.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SleepConsolidationReport {
    pub cycle_number: u32,
    pub episodes_replayed: usize,
    pub synapses_reinforced: usize,
    pub weak_synapses_pruned: usize,
    pub relations_discovered: usize,
    pub summary: String,
}

/// The Hippocampal-Cortical Conceptual Knowledge Web and Episodic Memory store.
#[derive(Serialize, Deserialize, Default)]
pub struct ConceptualKnowledgeWeb {
    pub concepts: FxHashMap<String, ConceptNode>,
    pub episodes: Vec<EpisodicMemory>,
    /// Directed conceptual associations `(concept_a, relation, concept_b, weight)`.
    pub relations: Vec<(String, String, String, f32)>,
    #[serde(default)]
    pub sleep_cycles_completed: u32,
    #[serde(default)]
    pub last_sleep_report: Option<SleepConsolidationReport>,
}

impl ConceptualKnowledgeWeb {
    pub fn new() -> Self {
        let genesis_ep = EpisodicMemory {
            episode_id: 1,
            tick: 1,
            partner: "self_genesis".to_string(),
            summary: "Awakened at Tick #1 as a Pure-Rust Sparse Dendritic Organism.".to_string(),
            active_concepts: vec!["self_genesis".to_string()],
            observed_traits: vec!["senses:awakened_tick_1".to_string()],
            action_or_code: None,
            outcome_traits: Vec::new(),
            surprise_score: 0.65,
            provenance: "lived".to_string(),
        };
        Self {
            concepts: FxHashMap::default(),
            episodes: vec![genesis_ep],
            relations: Vec::new(),
            sleep_cycles_completed: 0,
            last_sleep_report: None,
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
        let clean_name = concept_name.trim().to_lowercase();
        let hub_key = format!("concept:{}", clean_name);
        let word_key = format!("word:{}", clean_name);
        let hub_neuron_id = fabric.ensure_trait_neuron(&hub_key, Modality::ConceptHub);
        let word_neuron_id = fabric.ensure_trait_neuron(&word_key, Modality::Language);

        // Wire bidirectional grounding between the word neuron and the concept hub
        fabric.upsert_synapse(word_neuron_id, hub_neuron_id, 0.90, false, 1.5);
        fabric.upsert_synapse(word_neuron_id, hub_neuron_id, 0.90, true, 1.5);
        fabric.upsert_synapse(hub_neuron_id, word_neuron_id, 0.90, true, 1.5);

        let node = self
            .concepts
            .entry(clean_name.clone())
            .or_insert_with(|| ConceptNode {
                name: clean_name.clone(),
                hub_neuron_id,
                word_neuron_id,
                exposures: 0,
                familiarity: 0.0,
                traits: FxHashMap::default(),
                grounded_words: vec![clean_name.clone()],
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
                    weight: 0.65,
                    seen_count: 0,
                    invariance: 1.0,
                });

            entry.seen_count += 1;
            entry.invariance = (entry.seen_count as f32) / (node.exposures as f32);
            if node.exposures > 1 && entry.seen_count > 1 {
                entry.weight = (entry.weight + 0.22).min(1.0);
            }

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
                binding.weight = (binding.weight * 0.72).max(0.20);
            }
        }

        // 3. Ground additional spoken/written words to this concept
        for w in associated_words {
            let w_clean = w.trim().to_lowercase();
            if w_clean.is_empty() {
                continue;
            }
            if !node.grounded_words.contains(&w_clean) {
                node.grounded_words.push(w_clean.clone());
            }
            let w_nid =
                fabric.ensure_trait_neuron(&format!("word:{}", w_clean), Modality::Language);
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
            fabric.upsert_synapse(hub_neuron_id, act_nid, 0.70, true, 1.5);
            fabric.upsert_synapse(act_nid, eff_nid, 0.85, true, 1.5);
        }

        let snapshot = node.clone();

        // 5. Store direct autobiographical Episodic Memory with the user/partner (bounded to 500 max, M1)
        let ep_id = (self.episodes.last().map(|e| e.episode_id).unwrap_or(0)) + 1;
        self.episodes.push(EpisodicMemory {
            episode_id: ep_id,
            tick: fabric.current_tick,
            partner: partner.to_string(),
            summary: format!(
                "Interacted with '{}' on concept '{}' (exposure #{}, familiarity {:.2})",
                partner, clean_name, snapshot.exposures, snapshot.familiarity
            ),
            active_concepts: vec![clean_name],
            observed_traits: sensory_traits.to_vec(),
            action_or_code: action_opt,
            outcome_traits: outcome_vec,
            surprise_score,
            provenance: "lived".to_string(),
        });
        while self.episodes.len() > 500 {
            if let Some(pos) = self
                .episodes
                .iter()
                .position(|e| e.episode_id != 1 && e.surprise_score < 0.45)
            {
                self.episodes.remove(pos);
            } else {
                self.episodes.remove(1);
            }
        }

        // 6. Phase 2B: Update compositional conceptual relations (throttled when concept web is large)
        if self.concepts.len() <= 64 || self.episodes.len() % 16 == 0 {
            let _ = self.discover_relations(fabric);
        }

        snapshot
    }

    /// Phase 2B: Automatically discovers shared core invariants across concepts,
    /// induces parent category relationships (`is_a`), and links sibling concepts (`shares_core_with`).
    pub fn discover_relations(&mut self, fabric: &mut SparseNeuralFabric) -> usize {
        let mut new_relations: Vec<(String, String, String, f32)> = Vec::new();
        let mut concept_entries: Vec<(&String, u32)> = self
            .concepts
            .iter()
            .map(|(k, v)| (k, v.exposures))
            .collect();
        concept_entries.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
        let mut names: Vec<String> = concept_entries
            .into_iter()
            .take(80)
            .map(|(k, _)| k.clone())
            .collect();
        names.sort();

        for i in 0..names.len() {
            for j in (i + 1)..names.len() {
                let na = &names[i];
                let nb = &names[j];
                let (Some(ca), Some(cb)) = (self.concepts.get(na), self.concepts.get(nb)) else {
                    continue;
                };
                let core_a: std::collections::HashSet<&str> =
                    ca.core_invariants().iter().map(|t| t.trait_key.as_str()).collect();
                let core_b: std::collections::HashSet<&str> =
                    cb.core_invariants().iter().map(|t| t.trait_key.as_str()).collect();

                // Filter out generic V1 visual traits when inducing semantic categories so semantic
                // overlap is meaningful, or require >= 2 shared traits.
                let shared: Vec<&str> = core_a.intersection(&core_b).copied().collect();
                let semantic_shared: Vec<&str> = shared
                    .iter()
                    .copied()
                    .filter(|t| !t.starts_with("eyes:v1_") && !t.starts_with("eyes:aspect_"))
                    .collect();

                if !semantic_shared.is_empty() || shared.len() >= 3 {
                    let union_len = core_a.union(&core_b).count().max(1);
                    let sim = ((shared.len() as f32) / (union_len as f32)).clamp(0.15, 1.0);
                    new_relations.push((na.clone(), "shares_core_with".to_string(), nb.clone(), sim));

                    // Wire associative lateral synapse between sibling concept hubs
                    fabric.upsert_synapse(ca.hub_neuron_id, cb.hub_neuron_id, sim * 0.45, true, 1.2);
                    fabric.upsert_synapse(cb.hub_neuron_id, ca.hub_neuron_id, sim * 0.45, true, 1.2);

                    // Induce specific parent category name from shared semantic traits
                    if shared.contains(&"eyes:four_legs") || shared.contains(&"hands:warm_body") {
                        new_relations.push((
                            na.clone(),
                            "is_a".to_string(),
                            "living_quadruped".to_string(),
                            0.92,
                        ));
                        new_relations.push((
                            nb.clone(),
                            "is_a".to_string(),
                            "living_quadruped".to_string(),
                            0.92,
                        ));
                    }
                    if shared.contains(&"eyes:code_program") || shared.contains(&"eyes:code_block") {
                        new_relations.push((
                            na.clone(),
                            "is_a".to_string(),
                            "executable_program".to_string(),
                            0.90,
                        ));
                        new_relations.push((
                            nb.clone(),
                            "is_a".to_string(),
                            "executable_program".to_string(),
                            0.90,
                        ));
                    }
                }
            }
        }

        // Preserve explicit/inherited relations (e.g., from Alpha 3 beliefs or coaching) and deduplicate in O(1)
        let mut seen_keys: std::collections::HashSet<(String, String, String)> =
            std::collections::HashSet::new();
        let mut unique_rels: Vec<(String, String, String, f32)> = Vec::new();
        for (a, r, b, w) in self
            .relations
            .iter()
            .filter(|(_, r, _, _)| r != "shares_core_with")
            .cloned()
            .chain(new_relations.into_iter())
        {
            if unique_rels.len() >= 512 {
                break;
            }
            if seen_keys.insert((a.clone(), r.clone(), b.clone())) {
                unique_rels.push((a, r, b, w));
            }
        }
        let count = unique_rels.len();
        self.relations = unique_rels;
        count
    }

    /// Explicitly links two concepts (`a`, `rel`, `b`) in the Conceptual Knowledge Web
    /// (used for Alpha 3 taxonomic heritage and real-time conceptual coaching).
    pub fn link_concepts(&mut self, a: &str, rel: &str, b: &str, _evidence: &str, _tick: u32) {
        let ca = a.trim().to_lowercase();
        let cr = rel.trim().to_lowercase();
        let cb = b.trim().to_lowercase();
        if ca.is_empty() || cb.is_empty() {
            return;
        }
        if !self
            .relations
            .iter()
            .any(|(ea, er, eb, _)| ea == &ca && er == &cr && eb == &cb)
        {
            self.relations.push((ca, cr, cb, 0.95));
        }
    }

    /// Phase 2B: Compares two grounded concepts directly from their core invariants, variable
    /// traits, and induced parent categories.
    pub fn compare_concepts(&self, name_a: &str, name_b: &str) -> Option<ConceptComparison> {
        let ka = name_a.trim().to_lowercase();
        let kb = name_b.trim().to_lowercase();
        let node_a = self.concepts.get(&ka)?;
        let node_b = self.concepts.get(&kb)?;

        let core_a: Vec<String> = node_a
            .core_invariants()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();
        let core_b: Vec<String> = node_b
            .core_invariants()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();

        let shared_core_traits: Vec<String> = core_a
            .iter()
            .filter(|t| core_b.contains(t))
            .cloned()
            .collect();
        let unique_to_a: Vec<String> = core_a
            .iter()
            .filter(|t| !core_b.contains(t))
            .cloned()
            .collect();
        let unique_to_b: Vec<String> = core_b
            .iter()
            .filter(|t| !core_a.contains(t))
            .cloned()
            .collect();

        let mut shared_categories = Vec::new();
        for (s, r, cat, _) in &self.relations {
            if r == "is_a" && s == &ka {
                if self
                    .relations
                    .iter()
                    .any(|(s2, r2, cat2, _)| r2 == "is_a" && s2 == &kb && cat2 == cat)
                    && !shared_categories.contains(cat)
                {
                    shared_categories.push(cat.clone());
                }
            }
        }

        let union_cnt = (shared_core_traits.len() + unique_to_a.len() + unique_to_b.len()).max(1);
        let similarity_score = (shared_core_traits.len() as f32) / (union_cnt as f32);

        let cat_note = if shared_categories.is_empty() {
            String::new()
        } else {
            format!(" Both belong to category {:?}.", shared_categories)
        };

        let summary = format!(
            "Comparing '{}' and '{}' (similarity {:.0}%): they share {} core invariant(s) {:?}, while '{}' is distinguished by {:?} and '{}' is distinguished by {:?}.{}",
            node_a.name,
            node_b.name,
            similarity_score * 100.0,
            shared_core_traits.len(),
            shared_core_traits,
            node_a.name,
            unique_to_a.iter().take(4).collect::<Vec<_>>(),
            node_b.name,
            unique_to_b.iter().take(4).collect::<Vec<_>>(),
            cat_note
        );

        Some(ConceptComparison {
            concept_a: node_a.name.clone(),
            concept_b: node_b.name.clone(),
            shared_core_traits,
            unique_to_a,
            unique_to_b,
            shared_categories,
            similarity_score,
            summary,
        })
    }

    /// Phase 2D: Hippocampal-Neocortical Sharp-Wave Ripple Replay & Sleep Consolidation.
    /// Replays recent high-surprise episodic memories through `SparseNeuralFabric`, strengthens
    /// multi-exposure core invariant bindings, prunes weak noisy traits/synapses, and updates
    /// compositional concept hierarchy relations.
    pub fn consolidate_memories(
        &mut self,
        fabric: &mut SparseNeuralFabric,
    ) -> SleepConsolidationReport {
        self.sleep_cycles_completed += 1;
        if fabric.lesioned {
            let report = SleepConsolidationReport {
                cycle_number: self.sleep_cycles_completed,
                episodes_replayed: 0,
                synapses_reinforced: 0,
                weak_synapses_pruned: 0,
                relations_discovered: 0,
                summary: format!(
                    "Sleep Consolidation Cycle #{}: fabric is lesioned (0 traces replayed).",
                    self.sleep_cycles_completed
                ),
            };
            self.last_sleep_report = Some(report.clone());
            return report;
        }
        let mut episodes_replayed = 0usize;
        let mut synapses_reinforced = 0usize;
        let mut weak_synapses_pruned = 0usize;

        // 1. Select up to 8 highest-surprise or most recent episodic memories for sharp-wave replay
        let mut replay_indices: Vec<usize> = (0..self.episodes.len()).collect();
        replay_indices.sort_by(|&ia, &ib| {
            self.episodes[ib]
                .surprise_score
                .partial_cmp(&self.episodes[ia].surprise_score)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        replay_indices.truncate(8);

        for idx in replay_indices {
            let (obs_traits, act_concepts) = {
                let ep = &self.episodes[idx];
                (ep.observed_traits.clone(), ep.active_concepts.clone())
            };
            for tr in &obs_traits {
                if !tr.starts_with("senses:") && !tr.starts_with("ears:heard_") {
                    let nid = fabric.ensure_trait_neuron(tr, Modality::from_str(tr));
                    fabric.inject_basal_stimulus(nid, 1.05);
                }
            }
            for cname in &act_concepts {
                if let Some(node) = self.concepts.get(cname) {
                    fabric.inject_apical_prediction(node.hub_neuron_id, 0.90);
                }
            }
            let _ = fabric.step(true);
            // Fix M2: Decay episode surprise after sharp-wave ripple consolidation so replay
            // rotates across lived experiences rather than freezing on initial episodes.
            self.episodes[idx].surprise_score =
                (self.episodes[idx].surprise_score * 0.82).max(0.05);
            episodes_replayed += 1;
        }

        // 2. Reinforce Core Invariant synapses and prune weak incidental single-occurrence noise
        for node in self.concepts.values_mut() {
            let exposures = node.exposures;
            for binding in node.traits.values_mut() {
                if exposures >= 2 && binding.invariance >= 0.65 {
                    binding.weight = (binding.weight + 0.08).min(1.0);
                    fabric.upsert_synapse(
                        binding.neuron_id,
                        node.hub_neuron_id,
                        0.12,
                        false,
                        1.5,
                    );
                    fabric.upsert_synapse(
                        node.hub_neuron_id,
                        binding.neuron_id,
                        0.12,
                        true,
                        1.5,
                    );
                    synapses_reinforced += 2;
                } else if exposures >= 3 && binding.invariance < 0.35 && binding.weight < 0.35 {
                    binding.weight = (binding.weight * 0.80).max(0.10);
                }
            }
        }

        // 3. Synaptic homeostasis: prune ultra-weak noisy synapses (< 0.03) in the sparse fabric
        for syn_list in fabric.synapses.values_mut() {
            let before = syn_list.len();
            syn_list.retain(|s| s.weight >= 0.03);
            weak_synapses_pruned += before.saturating_sub(syn_list.len());
        }

        // 4. Re-induce compositional relations across consolidated concepts
        let relations_discovered = self.discover_relations(fabric);

        let summary = format!(
            "Sleep Consolidation Cycle #{}: replayed {} episodic traces, reinforced {} core invariant synapses, pruned {} weak synapses, and consolidated {} conceptual relations.",
            self.sleep_cycles_completed,
            episodes_replayed,
            synapses_reinforced,
            weak_synapses_pruned,
            relations_discovered
        );

        let report = SleepConsolidationReport {
            cycle_number: self.sleep_cycles_completed,
            episodes_replayed,
            synapses_reinforced,
            weak_synapses_pruned,
            relations_discovered,
            summary,
        };
        self.last_sleep_report = Some(report.clone());
        report
    }

    /// Recognizes concepts from an arbitrary set of sensory traits, gated by `SparseNeuralFabric`
    /// synaptic connectivity (`Law L1 / Fixes D3`). If the fabric is lesioned or the trait->hub
    /// synapses in `fabric.synapses` are ablated, recognition collapses to empty.
    pub fn recognize_from_traits_in_fabric(
        &self,
        fabric: &SparseNeuralFabric,
        observed_traits: &[String],
    ) -> Vec<ConceptRecognition> {
        if fabric.lesioned || fabric.synapses.is_empty() {
            return Vec::new();
        }
        self.recognize_from_traits(observed_traits)
            .into_iter()
            .filter(|rec| {
                if let Some(node) = self.concepts.get(&rec.concept_name) {
                    node.traits.values().any(|b| {
                        fabric
                            .synapses
                            .get(&b.neuron_id)
                            .map(|list| {
                                list.iter()
                                    .any(|s| s.target_id == node.hub_neuron_id && s.weight > 0.05)
                            })
                            .unwrap_or(false)
                    })
                } else {
                    false
                }
            })
            .collect()
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
                let unmatched_obs = exteroceptive_obs
                    .iter()
                    .filter(|&&t| !node.traits.contains_key(t))
                    .count();

                let inhibition_per_unmatched = if matched_core.len() >= 4 {
                    0.015
                } else {
                    0.065
                };
                let lateral_inhibition = (unmatched_obs as f32) * inhibition_per_unmatched;

                let core_ratio = core_score / total_core_possible;
                let multi_trait_gain = if matched_core.len() >= 4 {
                    1.38
                } else if matched_core.len() == 3 {
                    1.20
                } else {
                    0.85
                };
                let confidence = (core_ratio * multi_trait_gain + var_bonus - lateral_inhibition)
                    .clamp(0.0, 1.0);
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

    /// Grounded language comprehension gated by `SparseNeuralFabric` (`Law L1 / Fixes D1, D3`):
    /// requires intact word->hub and hub->trait synapses in `fabric.synapses`. When `fabric.lesioned`
    /// is true or synapses are wiped, returns an empty `GroundedThought`.
    pub fn understand_utterance_in_fabric(
        &self,
        fabric: &SparseNeuralFabric,
        text: &str,
    ) -> GroundedThought {
        if fabric.lesioned || fabric.synapses.is_empty() {
            return GroundedThought {
                utterance: text.to_string(),
                activated_concepts: Vec::new(),
                evoked_sensory_traits: Vec::new(),
                predicted_affordances: Vec::new(),
                recalled_episodes: Vec::new(),
            };
        }
        let mut thought = self.understand_utterance(text);
        thought.activated_concepts.retain(|cname| {
            if let Some(node) = self.concepts.get(cname) {
                fabric
                    .synapses
                    .get(&node.word_neuron_id)
                    .map(|list| {
                        list.iter()
                            .any(|s| s.target_id == node.hub_neuron_id && s.weight > 0.05)
                    })
                    .unwrap_or(false)
            } else {
                false
            }
        });
        if thought.activated_concepts.is_empty() {
            thought.evoked_sensory_traits.clear();
            thought.predicted_affordances.clear();
            thought.recalled_episodes.clear();
        }
        thought
    }

    /// Returns true if a token is a syntactic operator, interrogative, pronoun, or auxiliary verb
    /// that serves a grammatical role-filler function rather than naming a physical object concept.
    pub fn is_conversational_stopword(token: &str) -> bool {
        matches!(
            token,
            "who"
                | "what"
                | "how"
                | "why"
                | "when"
                | "where"
                | "which"
                | "whom"
                | "whose"
                | "did"
                | "do"
                | "does"
                | "done"
                | "doing"
                | "are"
                | "is"
                | "am"
                | "was"
                | "were"
                | "be"
                | "been"
                | "being"
                | "you"
                | "your"
                | "yours"
                | "yourself"
                | "me"
                | "my"
                | "mine"
                | "myself"
                | "i"
                | "we"
                | "us"
                | "our"
                | "he"
                | "she"
                | "it"
                | "its"
                | "they"
                | "them"
                | "their"
                | "to"
                | "of"
                | "in"
                | "on"
                | "at"
                | "for"
                | "with"
                | "from"
                | "by"
                | "about"
                | "as"
                | "into"
                | "like"
                | "through"
                | "after"
                | "over"
                | "between"
                | "out"
                | "against"
                | "during"
                | "without"
                | "before"
                | "under"
                | "around"
                | "among"
                | "the"
                | "a"
                | "an"
                | "and"
                | "or"
                | "but"
                | "if"
                | "because"
                | "while"
                | "can"
                | "could"
                | "would"
                | "should"
                | "will"
                | "shall"
                | "may"
                | "might"
                | "must"
                | "have"
                | "has"
                | "had"
                | "having"
                | "came"
                | "come"
                | "comes"
                | "coming"
                | "made"
                | "make"
                | "makes"
                | "making"
                | "tell"
                | "told"
                | "ask"
                | "asked"
                | "know"
                | "think"
                | "say"
                | "said"
                | "go"
                | "went"
                | "get"
                | "got"
                | "here"
                | "there"
                | "now"
                | "then"
                | "so"
                | "very"
                | "just"
                | "too"
                | "also"
                | "only"
                | "even"
                | "still"
                | "already"
                | "always"
                | "never"
                | "not"
                | "no"
                | "yes"
                | "this"
                | "that"
                | "these"
                | "those"
        )
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
            if tokens.len() > 1 && Self::is_conversational_stopword(token) {
                continue;
            }
            for node in self.concepts.values() {
                if node.name == *token || node.grounded_words.contains(token) {
                    // In multi-word sentences, skip ungrounded prose-placeholder tokens whose only traits
                    // are generic `senses:lexical_pattern` or `association:prose_context`.
                    if tokens.len() > 1
                        && !node.traits.is_empty()
                        && node.traits.keys().all(|k| {
                            k == "senses:lexical_pattern" || k == "association:prose_context"
                        })
                    {
                        continue;
                    }
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
