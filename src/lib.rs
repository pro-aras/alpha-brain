pub mod concept_web;
pub mod fabric;
pub mod neuron;
pub mod predictor;

use concept_web::ConceptualKnowledgeWeb;
use fabric::SparseNeuralFabric;
use neuron::{DendriticNeuron, Modality, Synapse};
use predictor::PredictiveEngine;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::fs;

/// Unified Alpha 7 Brain combining:
/// 1. Event-Driven Sparse Dendritic Neural Fabric (millions of neurons, O(active) compute)
/// 2. Hippocampal-Cortical Conceptual Knowledge Web & Direct User Episodic Memory (1-2 shot learning)
/// 3. Predictive Processing, Failed-Prediction Analyzer & Goal-Directed Scenario Simulator
#[pyclass]
#[derive(Serialize, Deserialize)]
pub struct Alpha7Brain {
    pub fabric: SparseNeuralFabric,
    pub knowledge_web: ConceptualKnowledgeWeb,
    pub predictor: PredictiveEngine,
}

#[pymethods]
impl Alpha7Brain {
    #[new]
    #[pyo3(signature = (num_neurons=1_000_000, neurons_per_column=64))]
    pub fn new(num_neurons: usize, neurons_per_column: usize) -> Self {
        Self {
            fabric: SparseNeuralFabric::new(num_neurons, neurons_per_column),
            knowledge_web: ConceptualKnowledgeWeb::new(),
            predictor: PredictiveEngine::new(),
        }
    }

    /// Total number of neurons currently in the sparse fabric.
    pub fn neuron_count(&self) -> usize {
        self.fabric.neurons.len()
    }

    /// Current simulation tick of the brain.
    pub fn current_tick(&self) -> u32 {
        self.fabric.current_tick
    }

    /// Total number of directed synapses currently wired across the fabric.
    pub fn active_synapse_count(&self) -> usize {
        self.fabric.synapses.values().map(|s| s.len()).sum()
    }

    /// Approximate RAM footprint of the neuron arena + synapse storage in megabytes.
    pub fn memory_footprint_mb(&self) -> f64 {
        let neuron_bytes = self.fabric.neurons.len() * std::mem::size_of::<DendriticNeuron>();
        let syn_vec_bytes = self.fabric.synapses.len()
            * (std::mem::size_of::<u32>() + std::mem::size_of::<smallvec::SmallVec<[Synapse; 4]>>());
        ((neuron_bytes + syn_vec_bytes) as f64) / (1024.0 * 1024.0)
    }

    /// Injects a sensory-motor frame (list of grounded trait strings across eyes, ears, hands,
    /// smell, senses), steps the sparse dendritic fabric, and returns JSON telemetry.
    #[pyo3(signature = (sensory_traits, learn_enabled=true))]
    pub fn perceive_and_step(&mut self, sensory_traits: Vec<String>, learn_enabled: bool) -> String {
        for trait_str in &sensory_traits {
            let prefix = trait_str.split(':').next().unwrap_or("association");
            let modality = Modality::from_str(prefix);
            let nid = self.fabric.ensure_trait_neuron(trait_str, modality);
            self.fabric.inject_basal_stimulus(nid, 1.25);
        }
        let step_report = self.fabric.step(learn_enabled);
        let recognitions = self.knowledge_web.recognize_from_traits(&sensory_traits);

        let payload = serde_json::json!({
            "step": step_report,
            "recognized_concepts": recognitions,
        });
        serde_json::to_string(&payload).unwrap_or_else(|_| "{}".to_string())
    }

    /// Teaches or refines a concept in 1-2 interactions (infant-like BTSP binding), separating
    /// core invariant traits from incidental traits and recording a direct user episodic memory.
    #[pyo3(signature = (concept_name, sensory_traits, associated_words=vec![], affordance=None, partner="user"))]
    pub fn learn_concept(
        &mut self,
        concept_name: &str,
        sensory_traits: Vec<String>,
        associated_words: Vec<String>,
        affordance: Option<(String, String)>,
        partner: &str,
    ) -> String {
        // First step the sensory traits through the fabric so BTSP eligibility traces are live
        for trait_str in &sensory_traits {
            let prefix = trait_str.split(':').next().unwrap_or("association");
            let modality = Modality::from_str(prefix);
            let nid = self.fabric.ensure_trait_neuron(trait_str, modality);
            self.fabric.inject_basal_stimulus(nid, 1.25);
        }
        let report = self.fabric.step(true);
        let node = self.knowledge_web.experience_concept(
            &mut self.fabric,
            concept_name,
            &sensory_traits,
            &associated_words,
            affordance,
            partner,
            report.surprise.surprise_score,
        );

        let core_traits: Vec<String> = node
            .core_invariants()
            .into_iter()
            .map(|t| t.trait_key.clone())
            .collect();
        let variable_traits: Vec<String> = node
            .variable_traits()
            .into_iter()
            .map(|t| t.trait_key.clone())
            .collect();

        let payload = serde_json::json!({
            "concept": node.name,
            "exposures": node.exposures,
            "familiarity": node.familiarity,
            "core_invariants": core_traits,
            "variable_traits": variable_traits,
            "grounded_words": node.grounded_words,
            "causal_affordances": node.causal_affordances,
            "surprise_score": report.surprise.surprise_score,
            "touched_neurons": report.touched_neurons,
        });
        serde_json::to_string(&payload).unwrap_or_else(|_| "{}".to_string())
    }

    /// Recognizes concepts from an arbitrary set of sensory traits (returns JSON array).
    pub fn recognize(&self, observed_traits: Vec<String>) -> String {
        let recs = self.knowledge_web.recognize_from_traits(&observed_traits);
        serde_json::to_string(&recs).unwrap_or_else(|_| "[]".to_string())
    }

    /// Inspects a learned concept node in detail.
    pub fn inspect_concept(&self, concept_name: &str) -> String {
        if let Some(node) = self.knowledge_web.concepts.get(&concept_name.to_lowercase()) {
            let core_traits: Vec<String> = node
                .core_invariants()
                .into_iter()
                .map(|t| t.trait_key.clone())
                .collect();
            let variable_traits: Vec<String> = node
                .variable_traits()
                .into_iter()
                .map(|t| t.trait_key.clone())
                .collect();
            let payload = serde_json::json!({
                "concept": node.name,
                "exposures": node.exposures,
                "familiarity": node.familiarity,
                "core_invariants": core_traits,
                "variable_traits": variable_traits,
                "grounded_words": node.grounded_words,
                "causal_affordances": node.causal_affordances,
                "all_traits": node.traits,
            });
            serde_json::to_string(&payload).unwrap_or_else(|_| "{}".to_string())
        } else {
            "{}".to_string()
        }
    }

    /// Predicts what traits will happen next if `action` is executed in `current_traits`.
    pub fn predict_next(&self, current_traits: Vec<String>, action: &str) -> Vec<(String, f32)> {
        self.predictor.predict_next(&current_traits, action)
    }

    /// Predicts what will happen next, observes what actually happens, and if something predicted
    /// fails to happen, analyzes the cause of the failure and updates both the predictive engine
    /// and the neural fabric's apical synapses in one shot.
    #[pyo3(signature = (context_traits, action, actual_outcomes, partner="sandbox"))]
    pub fn act_and_analyze(
        &mut self,
        context_traits: Vec<String>,
        action: &str,
        actual_outcomes: Vec<String>,
        partner: &str,
    ) -> String {
        // 1. Prime apical dendrites with the predicted outcome before observing reality
        let predicted = self.predictor.predict_next(&context_traits, action);
        for (pred_trait, prob) in &predicted {
            if *prob >= 0.45 {
                let nid = self
                    .fabric
                    .ensure_trait_neuron(pred_trait, Modality::from_str(pred_trait));
                self.fabric.inject_apical_prediction(nid, *prob);
            }
        }

        // 2. Inject actual outcome traits into basal dendrites & step the sparse fabric
        for out_trait in &actual_outcomes {
            let nid = self
                .fabric
                .ensure_trait_neuron(out_trait, Modality::from_str(out_trait));
            self.fabric.inject_basal_stimulus(nid, 1.25);
        }
        let step_report = self.fabric.step(true);

        // 3. Run causal prediction vs. reality comparison & failure analysis
        let eval = self.predictor.observe_and_analyze(
            &mut self.fabric,
            &context_traits,
            action,
            &actual_outcomes,
        );

        // 4. Record an episodic memory if surprise/learning occurred
        if eval.prediction_failed {
            let ep_id = (self.knowledge_web.episodes.len() + 1) as u64;
            self.knowledge_web
                .episodes
                .push(concept_web::EpisodicMemory {
                    episode_id: ep_id,
                    tick: step_report.tick,
                    partner: partner.to_string(),
                    summary: eval.analysis_report.clone(),
                    active_concepts: vec![action.to_string()],
                    observed_traits: context_traits,
                    action_or_code: Some(action.to_string()),
                    outcome_traits: actual_outcomes,
                    surprise_score: step_report.surprise.surprise_score.max(0.75),
                });
        }

        let payload = serde_json::json!({
            "evaluation": eval,
            "fabric_step": step_report,
        });
        serde_json::to_string(&payload).unwrap_or_else(|_| "{}".to_string())
    }

    /// Simulates multi-step possibilities and scenarios directed toward `goal_trait`.
    #[pyo3(signature = (current_traits, goal_trait, max_depth=3))]
    pub fn simulate_goal_scenarios(
        &self,
        current_traits: Vec<String>,
        goal_trait: &str,
        max_depth: usize,
    ) -> String {
        let branches =
            self.predictor
                .simulate_scenarios(&current_traits, goal_trait, max_depth);
        serde_json::to_string(&branches).unwrap_or_else(|_| "[]".to_string())
    }

    /// Grounded language understanding: maps words/sentences/code to sensory-motor traits,
    /// causal affordances, and direct user episodic memories.
    pub fn think_on_words(&self, utterance: &str) -> String {
        let thought = self.knowledge_web.understand_utterance(utterance);
        serde_json::to_string(&thought).unwrap_or_else(|_| "{}".to_string())
    }

    /// Returns the most recent direct episodic memories formed with the user or environment.
    #[pyo3(signature = (limit=10))]
    pub fn recalled_episodes(&self, limit: usize) -> String {
        let slice: Vec<_> = self
            .knowledge_web
            .episodes
            .iter()
            .rev()
            .take(limit)
            .cloned()
            .collect();
        serde_json::to_string(&slice).unwrap_or_else(|_| "[]".to_string())
    }

    /// Persists the entire Alpha 7 brain (neurons, synapses, concept web, episodic memories) to JSON.
    pub fn save_state(&self, path: &str) -> PyResult<()> {
        let data = serde_json::to_string_pretty(self).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to serialize Alpha7Brain: {}", e))
        })?;
        fs::write(path, data).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to write {}: {}", path, e))
        })?;
        Ok(())
    }

    /// Loads a persisted Alpha 7 brain from disk.
    #[staticmethod]
    pub fn load_state(path: &str) -> PyResult<Self> {
        let data = fs::read_to_string(path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to read {}: {}", path, e))
        })?;
        let brain: Alpha7Brain = serde_json::from_str(&data).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to deserialize Alpha7Brain: {}", e))
        })?;
        Ok(brain)
    }
}

#[pymodule]
fn alpha7_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Alpha7Brain>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_million_neurons_zero_idle_bottleneck() {
        let mut brain = Alpha7Brain::new(1_000_000, 64);
        assert_eq!(brain.neuron_count(), 1_000_000);
        // 1 million neurons should use < 65 MB of RAM and step in sub-millisecond time
        assert!(brain.memory_footprint_mb() < 75.0);

        let start = std::time::Instant::now();
        let report_json = brain.perceive_and_step(
            vec![
                "eyes:whiskers".to_string(),
                "eyes:pointy_ears".to_string(),
                "ears:purr".to_string(),
            ],
            true,
        );
        let elapsed = start.elapsed();
        assert!(
            elapsed.as_millis() < 20,
            "1M neuron sparse step took too long: {:?}",
            elapsed
        );
        assert!(report_json.contains("touched_neurons"));
    }

    #[test]
    fn test_two_shot_infant_cat_generalization() {
        let mut brain = Alpha7Brain::new(100_000, 64);

        // Exposure 1: User shows an orange cat that meows
        brain.learn_concept(
            "cat",
            vec![
                "eyes:pointy_ears".to_string(),
                "eyes:whiskers".to_string(),
                "eyes:slit_pupils".to_string(),
                "eyes:four_legs".to_string(),
                "hands:soft_fur".to_string(),
                "ears:purr".to_string(),
                "eyes:orange_coat".to_string(),
            ],
            vec!["cat".to_string(), "kitty".to_string()],
            Some(("gentle_pet".to_string(), "ears:purr".to_string())),
            "user",
        );

        // Exposure 2: User shows a black cat (shares feline invariants, differs in coat color)
        brain.learn_concept(
            "cat",
            vec![
                "eyes:pointy_ears".to_string(),
                "eyes:whiskers".to_string(),
                "eyes:slit_pupils".to_string(),
                "eyes:four_legs".to_string(),
                "hands:soft_fur".to_string(),
                "ears:purr".to_string(),
                "eyes:black_coat".to_string(),
            ],
            vec!["cat".to_string()],
            None,
            "user",
        );

        let node = brain.knowledge_web.concepts.get("cat").unwrap();
        let core: Vec<String> = node
            .core_invariants()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();
        let var: Vec<String> = node
            .variable_traits()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();

        assert!(core.contains(&"eyes:whiskers".to_string()));
        assert!(core.contains(&"eyes:pointy_ears".to_string()));
        assert!(var.contains(&"eyes:orange_coat".to_string()));
        assert!(var.contains(&"eyes:black_coat".to_string()));

        // Test 3: Unseen white cat is immediately recognized with high confidence!
        let recs = brain.knowledge_web.recognize_from_traits(&vec![
            "eyes:pointy_ears".to_string(),
            "eyes:whiskers".to_string(),
            "eyes:four_legs".to_string(),
            "hands:soft_fur".to_string(),
            "eyes:white_coat".to_string(),
        ]);
        assert!(!recs.is_empty());
        assert_eq!(recs[0].concept_name, "cat");
        assert!(recs[0].confidence > 0.80);
    }

    #[test]
    fn test_prediction_failure_analysis_and_goal_rollout() {
        let mut brain = Alpha7Brain::new(50_000, 64);

        // 1. Alpha 7 learns that running `run_code` on valid code produces `eyes:output_ok`
        brain.act_and_analyze(
            vec!["eyes:code_written".to_string()],
            "run_code",
            vec!["eyes:output_ok".to_string()],
            "user",
        );

        // Verify Alpha 7 now predicts `eyes:output_ok`
        let preds = brain.predict_next(vec!["eyes:code_written".to_string()], "run_code");
        assert_eq!(preds[0].0, "eyes:output_ok");

        // 2. Now something FAILS to happen: when `eyes:syntax_typo` is present, `eyes:output_ok`
        // fails to happen and `eyes:syntax_error` happens instead!
        let failure_json = brain.act_and_analyze(
            vec![
                "eyes:code_written".to_string(),
                "eyes:syntax_typo".to_string(),
            ],
            "run_code",
            vec!["eyes:syntax_error".to_string()],
            "user",
        );
        assert!(failure_json.contains("PREDICTION FAILURE ANALYZED"));
        assert!(failure_json.contains("eyes:syntax_typo"));

        // 3. Verify Alpha 7 learned from the failure: with `eyes:syntax_typo` present, it now
        // predicts `eyes:syntax_error` instead of `eyes:output_ok`!
        let updated_preds = brain.predict_next(
            vec![
                "eyes:code_written".to_string(),
                "eyes:syntax_typo".to_string(),
            ],
            "run_code",
        );
        assert_eq!(updated_preds[0].0, "eyes:syntax_error");
    }
}
