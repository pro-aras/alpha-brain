pub mod body;
pub mod concept_web;
pub mod curriculum;
pub mod fabric;
pub mod language_road;
pub mod neuron;
pub mod predictor;
pub mod world2d;

use body::{Alpha7Body, SensoryFrame};
use concept_web::{ConceptNode, ConceptRecognition, ConceptualKnowledgeWeb};
use fabric::{SparseNeuralFabric, StepReport};
use language_road::{LanguageRoad, MouthUtterance};
use neuron::{DendriticNeuron, Modality, Synapse};
use predictor::{PredictionEvaluation, PredictiveEngine, ScenarioBranch};
use serde::{Deserialize, Serialize};
use std::fs;
use world2d::World2DCanvas;

/// Complete Pure-Rust Alpha 7 Organism uniting:
/// - Brain:
///   1. Event-Driven Sparse Dendritic Neural Fabric (`1,000,000+` neurons, zero idle compute)
///   2. Hippocampal-Cortical Conceptual Knowledge Web & Direct User Episodic Memory (1-2 shot BTSP)
///   3. Predictive Processing, Failed-Prediction Analyzer & Goal-Directed Scenario Simulator
///   4. Grounded Language & Mouth Road (understands and speaks strictly from grounded concepts)
/// - Body:
///   5. 5-Sense Embodied Interface (Eyes, Ears, Hands, Smell, Internal Senses)
/// - Environment:
///   6. Interactive 2D Spatial World Canvas
#[derive(Serialize, Deserialize)]
pub struct Alpha7Organism {
    pub fabric: SparseNeuralFabric,
    pub knowledge_web: ConceptualKnowledgeWeb,
    pub predictor: PredictiveEngine,
    pub language: LanguageRoad,
    pub body: Alpha7Body,
    pub world: World2DCanvas,
}

impl Alpha7Organism {
    pub fn new(num_neurons: usize, neurons_per_column: usize) -> Self {
        Self {
            fabric: SparseNeuralFabric::new(num_neurons, neurons_per_column),
            knowledge_web: ConceptualKnowledgeWeb::new(),
            predictor: PredictiveEngine::new(),
            language: LanguageRoad::new(),
            body: Alpha7Body::new(),
            world: World2DCanvas::default_sandbox(),
        }
    }

    pub fn neuron_count(&self) -> usize {
        self.fabric.neurons.len()
    }

    pub fn active_synapse_count(&self) -> usize {
        self.fabric.synapses.values().map(|s| s.len()).sum()
    }

    pub fn memory_footprint_mb(&self) -> f64 {
        let neuron_bytes = self.fabric.neurons.len() * std::mem::size_of::<DendriticNeuron>();
        let syn_vec_bytes = self.fabric.synapses.len()
            * (std::mem::size_of::<u32>()
                + std::mem::size_of::<smallvec::SmallVec<[Synapse; 4]>>());
        ((neuron_bytes + syn_vec_bytes) as f64) / (1024.0 * 1024.0)
    }

    /// Injects a 5-sense `SensoryFrame`, steps the sparse neural fabric, and returns step report
    /// and recognized concepts.
    pub fn perceive_and_step(
        &mut self,
        frame: &SensoryFrame,
        learn_enabled: bool,
    ) -> (StepReport, Vec<ConceptRecognition>) {
        let traits = frame.to_neural_traits();
        for trait_str in &traits {
            let prefix = trait_str.split(':').next().unwrap_or("association");
            let modality = Modality::from_str(prefix);
            let nid = self.fabric.ensure_trait_neuron(trait_str, modality);
            self.fabric.inject_basal_stimulus(nid, 1.25);
        }
        let step_report = self.fabric.step(learn_enabled);
        let recognitions = self.knowledge_web.recognize_from_traits(&traits);
        (step_report, recognitions)
    }

    /// Learns or refines a concept in 1-2 interactions (infant-like BTSP binding), separating
    /// core invariant traits from incidental traits and recording a direct user episodic memory.
    pub fn experience_concept(
        &mut self,
        concept_name: &str,
        frame: &SensoryFrame,
        affordance: Option<(String, String)>,
        partner: &str,
    ) -> (ConceptNode, StepReport) {
        let traits = frame.to_neural_traits();
        for trait_str in &traits {
            let prefix = trait_str.split(':').next().unwrap_or("association");
            let modality = Modality::from_str(prefix);
            let nid = self.fabric.ensure_trait_neuron(trait_str, modality);
            self.fabric.inject_basal_stimulus(nid, 1.25);
        }
        let report = self.fabric.step(true);
        let words = if frame.spoken_words.is_empty() {
            vec![concept_name.to_string()]
        } else {
            frame.spoken_words.clone()
        };
        let node = self.knowledge_web.experience_concept(
            &mut self.fabric,
            concept_name,
            &traits,
            &words,
            affordance,
            partner,
            report.surprise.surprise_score,
        );
        (node, report)
    }

    /// Predicts what will happen next, observes what actually happens, and if something predicted
    /// fails to happen, analyzes the cause of the failure and updates both the predictive engine
    /// and the neural fabric's apical synapses in one shot.
    pub fn act_and_analyze(
        &mut self,
        context_frame: &SensoryFrame,
        action: &str,
        actual_outcomes: &[String],
        partner: &str,
    ) -> (PredictionEvaluation, StepReport) {
        let context_traits = context_frame.to_neural_traits();

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
        for out_trait in actual_outcomes {
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
            actual_outcomes,
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
                    outcome_traits: actual_outcomes.to_vec(),
                    surprise_score: step_report.surprise.surprise_score.max(0.75),
                });
        }

        (eval, step_report)
    }

    /// Practices a small code snippet using Eyes (visual syntax inspection) and Hands (execution),
    /// predicting the outcome first and analyzing any surprise or syntax error.
    pub fn practice_coding(
        &mut self,
        code_str: &str,
        concept_label: Option<&str>,
    ) -> PredictionEvaluation {
        let visual_traits = self.body.eyes.inspect_code(code_str);
        let senses = self.body.internal.read_state(0.0);
        let frame = SensoryFrame {
            eyes: visual_traits,
            ears: Vec::new(),
            hands: Vec::new(),
            smell: Vec::new(),
            senses,
            spoken_words: Vec::new(),
        };
        let actual_outcomes = self.body.hands.execute_small_code(code_str);
        let (eval, _step) = self.act_and_analyze(&frame, "run_code", &actual_outcomes, "user");

        if let Some(label) = concept_label {
            if let Some(first_out) = actual_outcomes.first() {
                let _ = self.experience_concept(
                    label,
                    &frame,
                    Some(("run_code".to_string(), first_out.clone())),
                    "user",
                );
            }
        }
        eval
    }

    /// Simulates multi-step possibilities and scenarios directed toward `goal_trait`.
    pub fn simulate_goal_scenarios(
        &self,
        current_frame: &SensoryFrame,
        goal_trait: &str,
        max_depth: usize,
    ) -> Vec<ScenarioBranch> {
        self.predictor
            .simulate_scenarios(&current_frame.to_neural_traits(), goal_trait, max_depth)
    }

    /// Processes a user utterance through the Grounded Language & Mouth Road.
    pub fn converse(&mut self, utterance: &str) -> MouthUtterance {
        let current_frame = self.world.sense_current_frame(&mut self.body, Some(utterance));
        self.language.respond_to_user(
            &mut self.fabric,
            &self.knowledge_web,
            &self.predictor,
            &current_frame,
            utterance,
        )
    }

    /// Saves the entire Alpha 7 organism state to disk using sparse neuron checkpointing
    /// (~40 KB instead of ~300 MB for 1,000,000 neurons).
    pub fn save_state(&self, path: &str) -> Result<(), String> {
        let total_n = self.fabric.neurons.len();
        let active_neurons: Vec<(usize, DendriticNeuron)> = self
            .fabric
            .neurons
            .iter()
            .copied()
            .enumerate()
            .filter(|(_, n)| n.last_update_tick > 0 || n.maturity_count > 0 || (n.threshold - 1.0).abs() > 1e-4)
            .collect();

        let checkpoint = serde_json::json!({
            "total_neurons": total_n,
            "current_tick": self.fabric.current_tick,
            "active_neurons": active_neurons,
            "synapses": self.fabric.synapses,
            "trait_to_neuron": self.fabric.trait_to_neuron,
            "neuron_to_trait": self.fabric.neuron_to_trait,
            "knowledge_web": self.knowledge_web,
            "predictor": self.predictor,
            "body": self.body,
            "world": self.world,
        });
        let json = serde_json::to_string_pretty(&checkpoint).map_err(|e| e.to_string())?;
        fs::write(path, json).map_err(|e| e.to_string())
    }

    /// Loads a persisted Alpha 7 organism state from disk and restores the 1,000,000-neuron arena.
    pub fn load_state(path: &str) -> Result<Self, String> {
        let data = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let val: serde_json::Value = serde_json::from_str(&data).map_err(|e| e.to_string())?;
        let total_n = val
            .get("total_neurons")
            .and_then(|v| v.as_u64())
            .unwrap_or(1_000_000) as usize;
        let mut org = Self::new(total_n, 64);
        if let Some(tick) = val.get("current_tick").and_then(|v| v.as_u64()) {
            org.fabric.current_tick = tick as u32;
        }
        if let Some(act_val) = val.get("active_neurons") {
            if let Ok(list) = serde_json::from_value::<Vec<(usize, DendriticNeuron)>>(act_val.clone()) {
                for (idx, n) in list {
                    if idx < org.fabric.neurons.len() {
                        org.fabric.neurons[idx] = n;
                    }
                }
            }
        }
        if let Some(syn_val) = val.get("synapses") {
            if let Ok(s) = serde_json::from_value(syn_val.clone()) {
                org.fabric.synapses = s;
            }
        }
        if let Some(ttn_val) = val.get("trait_to_neuron") {
            if let Ok(m) = serde_json::from_value(ttn_val.clone()) {
                org.fabric.trait_to_neuron = m;
            }
        }
        if let Some(ntt_val) = val.get("neuron_to_trait") {
            if let Ok(m) = serde_json::from_value(ntt_val.clone()) {
                org.fabric.neuron_to_trait = m;
            }
        }
        if let Some(kw_val) = val.get("knowledge_web") {
            if let Ok(kw) = serde_json::from_value(kw_val.clone()) {
                org.knowledge_web = kw;
            }
        }
        if let Some(pred_val) = val.get("predictor") {
            if let Ok(p) = serde_json::from_value(pred_val.clone()) {
                org.predictor = p;
            }
        }
        if let Some(body_val) = val.get("body") {
            if let Ok(b) = serde_json::from_value(body_val.clone()) {
                org.body = b;
            }
        }
        if let Some(world_val) = val.get("world") {
            if let Ok(w) = serde_json::from_value(world_val.clone()) {
                org.world = w;
            }
        }
        Ok(org)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_million_neurons_zero_idle_bottleneck() {
        let mut org = Alpha7Organism::new(1_000_000, 64);
        assert_eq!(org.neuron_count(), 1_000_000);
        assert!(org.memory_footprint_mb() < 40.0);

        let frame = org.body.build_frame(
            &["pointy_ears", "whiskers"],
            &["purr"],
            &["soft_fur"],
            &["feline_scent"],
            None,
        );
        let start = std::time::Instant::now();
        let (report, _) = org.perceive_and_step(&frame, true);
        let elapsed = start.elapsed();
        assert!(
            elapsed.as_millis() < 20,
            "1M neuron sparse step took too long: {:?}",
            elapsed
        );
        assert!(report.touched_neurons > 0 && report.touched_neurons < 100);
    }

    #[test]
    fn test_world2d_and_two_shot_infant_cat_generalization() {
        let mut org = Alpha7Organism::new(100_000, 64);

        // 1. Move to Orange Cat at (2, 2) on the 2D World Canvas & learn 'cat' (Exposure #1)
        org.world.move_agent_to(&mut org.body, 2, 2);
        let frame1 = org
            .world
            .sense_current_frame(&mut org.body, Some("cat kitty"));
        let (node1, _) = org.experience_concept(
            "cat",
            &frame1,
            Some(("gentle_pet".to_string(), "ears:purr".to_string())),
            "user",
        );
        assert_eq!(node1.exposures, 1);

        // 2. Move to Black Cat at (10, 2) on the 2D World Canvas & refine 'cat' (Exposure #2)
        org.world.move_agent_to(&mut org.body, 10, 2);
        let frame2 = org.world.sense_current_frame(&mut org.body, Some("cat"));
        let (node2, _) = org.experience_concept("cat", &frame2, None, "user");
        assert_eq!(node2.exposures, 2);

        let core: Vec<String> = node2
            .core_invariants()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();
        let var: Vec<String> = node2
            .variable_traits()
            .iter()
            .map(|t| t.trait_key.clone())
            .collect();
        assert!(core.contains(&"eyes:whiskers".to_string()));
        assert!(core.contains(&"eyes:pointy_ears".to_string()));
        assert!(var.contains(&"eyes:orange_fur".to_string()));
        assert!(var.contains(&"eyes:black_fur".to_string()));

        // 3. Move to Unseen White Cat at (10, 9) and ask Alpha 7 "what is this?" via LanguageRoad!
        org.world.move_agent_to(&mut org.body, 10, 9);
        let reply = org.converse("what is this?");
        assert!(reply.spoken_response.contains("I recognize 'cat'"));

        // 4. Move to Unseen Dog at (2, 9) and ask "what is this?" -> should NOT falsely recognize cat!
        org.world.move_agent_to(&mut org.body, 2, 9);
        let dog_reply = org.converse("what is this?");
        assert!(dog_reply.spoken_response.contains("unfamiliar traits"));
    }

    #[test]
    fn test_prediction_failure_coding_and_goal_scenarios() {
        let mut org = Alpha7Organism::new(50_000, 64);

        // 1. Practice valid code
        let eval_ok = org.practice_coding("result = 6 * 7\nprint(result)", Some("multiply_code"));
        assert!(!eval_ok.prediction_failed || eval_ok.analysis_report.contains("ONE-SHOT"));

        // 2. Practice broken code -> prediction failure analyzed!
        let eval_err = org.practice_coding("result = 6 * * * 7", None);
        assert!(eval_err.prediction_failed);
        assert!(eval_err.analysis_report.contains("PREDICTION FAILURE ANALYZED"));
        assert!(eval_err.analysis_report.contains("eyes:syntax_typo"));

        // 3. Causal chain & Goal Scenario Simulation via Mouth
        let f_switch = org
            .body
            .build_frame(&["switch_visible"], &[], &["near_switch"], &[], None);
        org.act_and_analyze(
            &f_switch,
            "press_switch",
            &["eyes:light_on".to_string()],
            "user",
        );
        let f_light = org.body.build_frame(&["light_on"], &[], &[], &[], None);
        org.act_and_analyze(
            &f_light,
            "read_book",
            &["eyes:knowledge_gained".to_string()],
            "user",
        );

        let branches = org.simulate_goal_scenarios(&f_switch, "eyes:knowledge_gained", 3);
        assert!(branches.iter().any(|b| b.reaches_goal
            && b.actions == vec!["press_switch".to_string(), "read_book".to_string()]));
    }
}
