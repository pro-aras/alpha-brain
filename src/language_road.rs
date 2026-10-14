//! Alpha 7 Grounded Language, Grammar Road & "The Mouth" (Option 2)
//!
//! Ensures Alpha 7 understands the words it speaks and thinks on:
//! - Every word is wired directly to sensory-motor trait neurons, Concept Hub assemblies,
//!   and causal action->outcome transitions.
//! - "The Mouth" never emits ungrounded statistical tokens; it constructs utterances and
//!   curiosity questions directly from active Concept Nodes, Predictive Scenarios, and
//!   Surprise / Prediction-Error diagnostics.

use crate::body::SensoryFrame;
use crate::concept_web::{ConceptRecognition, ConceptualKnowledgeWeb, GroundedThought};
use crate::fabric::SparseNeuralFabric;
use crate::predictor::{PredictionEvaluation, PredictiveEngine, ScenarioBranch};
use serde::{Deserialize, Serialize};

/// Structured intent parsed from a user utterance on the Language Road.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum UtteranceIntent {
    /// User asks what Alpha 7 currently perceives ("what is this?", "what do you see?").
    AskCurrentPerception,
    /// User asks about a specific concept ("what is cat?", "describe cat").
    AskConcept { concept: String },
    /// User asks what will happen next if an action is taken ("what happens if press_switch?").
    AskPrediction { action: String },
    /// User directs Alpha 7 toward a goal ("how to reach eyes:knowledge_gained?", "goal eyes:light_on").
    AskGoalScenario { goal_trait: String },
    /// User teaches a concept or statement ("teach cat", or general conversational thought).
    GeneralThought { text: String },
}

/// Output from Alpha 7's grounded Mouth + Thought loop.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MouthUtterance {
    pub intent: UtteranceIntent,
    pub spoken_response: String,
    pub grounded_thought: GroundedThought,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct LanguageRoad;

impl LanguageRoad {
    pub fn new() -> Self {
        Self
    }

    /// Parses the user's utterance into a grounded cognitive intent.
    pub fn parse_intent(&self, utterance: &str) -> UtteranceIntent {
        let lower = utterance.trim().to_lowercase();
        let clean = lower.trim_end_matches('?').trim_end_matches('.').trim();

        if clean == "what is this"
            || clean == "what do you see"
            || clean == "what do you sense"
            || clean == "recognize"
        {
            return UtteranceIntent::AskCurrentPerception;
        }

        if let Some(rest) = clean
            .strip_prefix("what happens if ")
            .or_else(|| clean.strip_prefix("predict "))
        {
            return UtteranceIntent::AskPrediction {
                action: rest.trim().replace(' ', "_"),
            };
        }

        if let Some(rest) = clean
            .strip_prefix("how to reach ")
            .or_else(|| clean.strip_prefix("goal "))
        {
            return UtteranceIntent::AskGoalScenario {
                goal_trait: rest.trim().to_string(),
            };
        }

        if let Some(rest) = clean
            .strip_prefix("what is a ")
            .or_else(|| clean.strip_prefix("what is "))
            .or_else(|| clean.strip_prefix("describe "))
        {
            let target = rest.trim();
            if !target.is_empty() && target != "this" {
                return UtteranceIntent::AskConcept {
                    concept: target.to_string(),
                };
            }
        }

        UtteranceIntent::GeneralThought {
            text: utterance.to_string(),
        }
    }

    /// Generates Alpha 7's grounded spoken response when observing a sensory frame.
    pub fn speak_perception(
        &self,
        frame: &SensoryFrame,
        recognitions: &[ConceptRecognition],
    ) -> String {
        let traits = frame.to_neural_traits();
        let extero: Vec<String> = traits
            .into_iter()
            .filter(|t| !t.starts_with("senses:") && !t.starts_with("ears:heard_"))
            .collect();

        if let Some(best) = recognitions.first() {
            let core_preview: Vec<String> =
                best.matched_core_traits.iter().take(5).cloned().collect();
            format!(
                "I recognize '{}' (confidence {:.0}%, familiarity {:.0}%) grounded in core traits: [{}].",
                best.concept_name,
                best.confidence * 100.0,
                best.familiarity * 100.0,
                core_preview.join(", ")
            )
        } else if extero.is_empty() {
            "My senses are calm and waiting; no external object is in focus.".to_string()
        } else {
            // High-surprise unknown entity -> Alpha 7 asks the user!
            let sample: Vec<String> = extero.into_iter().take(5).collect();
            format!(
                "I sense unfamiliar traits [{}] that do not match my concept web yet. What is this?",
                sample.join(", ")
            )
        }
    }

    /// Generates grounded speech explaining a prediction failure or confirmation.
    pub fn speak_prediction_outcome(&self, eval: &PredictionEvaluation) -> String {
        if eval.prediction_failed {
            format!(
                "Surprise detected on action '{}': {}",
                eval.action, eval.analysis_report
            )
        } else {
            format!(
                "Prediction confirmed on action '{}': observed {:?} as expected.",
                eval.action, eval.actual_traits
            )
        }
    }

    /// Generates grounded speech describing a multi-step goal scenario simulation.
    pub fn speak_goal_scenarios(&self, goal_trait: &str, branches: &[ScenarioBranch]) -> String {
        if let Some(best) = branches.iter().find(|b| b.reaches_goal) {
            format!(
                "To achieve goal '{}', I simulated {} scenario(s). Best path ({:.0}% confidence): execute {:?} -> {}.",
                goal_trait,
                branches.len(),
                best.probability * 100.0,
                best.actions,
                best.rationale
            )
        } else {
            format!(
                "I simulated {} scenario(s) toward '{}', but none of my known causal actions reach it yet. Teach me an action that produces '{}'.",
                branches.len(),
                goal_trait,
                goal_trait
            )
        }
    }

    /// Full grounded dialogue turn: processes the user's words through the Concept Web,
    /// fires the word/concept neurons in the `SparseNeuralFabric`, and speaks from grounded knowledge.
    pub fn respond_to_user(
        &self,
        fabric: &mut SparseNeuralFabric,
        web: &ConceptualKnowledgeWeb,
        predictor: &PredictiveEngine,
        current_frame: &SensoryFrame,
        utterance: &str,
    ) -> MouthUtterance {
        let intent = self.parse_intent(utterance);
        let thought = web.understand_utterance(utterance);

        // Fire the activated concept & word neurons in the neural fabric so thinking is physically grounded
        for concept_name in &thought.activated_concepts {
            if let Some(node) = web.concepts.get(concept_name) {
                fabric.inject_basal_stimulus(node.word_neuron_id, 1.1);
                fabric.inject_apical_prediction(node.hub_neuron_id, 0.9);
            }
        }
        let _ = fabric.step(false);

        let spoken_response = match &intent {
            UtteranceIntent::AskCurrentPerception => {
                let recs = web.recognize_from_traits(&current_frame.to_neural_traits());
                self.speak_perception(current_frame, &recs)
            }
            UtteranceIntent::AskConcept { concept } => {
                if let Some(node) = web.concepts.get(&concept.to_lowercase()) {
                    let core: Vec<String> = node
                        .core_invariants()
                        .iter()
                        .take(6)
                        .map(|t| t.trait_key.clone())
                        .collect();
                    let var: Vec<String> = node
                        .variable_traits()
                        .iter()
                        .take(4)
                        .map(|t| t.trait_key.clone())
                        .collect();
                    let affordances: Vec<String> = node
                        .causal_affordances
                        .iter()
                        .map(|(a, e)| format!("{} -> {}", a, e))
                        .collect();
                    format!(
                        "'{}' (experienced {} time(s), familiarity {:.0}%): core invariants=[{}]; variable traits=[{}]; affordances=[{}].",
                        node.name,
                        node.exposures,
                        node.familiarity * 100.0,
                        core.join(", "),
                        var.join(", "),
                        affordances.join(", ")
                    )
                } else {
                    format!(
                        "I have not experienced '{}' yet. Show me '{}' once or twice so I can bind its traits.",
                        concept, concept
                    )
                }
            }
            UtteranceIntent::AskPrediction { action } => {
                let preds = predictor.predict_next(&current_frame.to_neural_traits(), action);
                if preds.is_empty() {
                    format!(
                        "I have no prediction yet for action '{}' in the current sensory state.",
                        action
                    )
                } else {
                    let formatted: Vec<String> = preds
                        .iter()
                        .take(4)
                        .map(|(t, p)| format!("{} ({:.0}%)", t, p * 100.0))
                        .collect();
                    format!(
                        "If I perform '{}', I predict: [{}].",
                        action,
                        formatted.join(", ")
                    )
                }
            }
            UtteranceIntent::AskGoalScenario { goal_trait } => {
                let branches =
                    predictor.simulate_scenarios(&current_frame.to_neural_traits(), goal_trait, 3);
                self.speak_goal_scenarios(goal_trait, &branches)
            }
            UtteranceIntent::GeneralThought { .. } => {
                if thought.activated_concepts.is_empty() {
                    format!(
                        "I heard '{}', but none of those words are grounded in my concept web yet.",
                        utterance
                    )
                } else {
                    let traits_preview: Vec<String> =
                        thought.evoked_sensory_traits.iter().take(6).cloned().collect();
                    let mem_note = thought
                        .recalled_episodes
                        .first()
                        .cloned()
                        .unwrap_or_else(|| "no prior episodes".to_string());
                    format!(
                        "Thinking on {:?} evokes sensory-motor traits [{}] and memory: ({}).",
                        thought.activated_concepts,
                        traits_preview.join(", "),
                        mem_note
                    )
                }
            }
        };

        MouthUtterance {
            intent,
            spoken_response,
            grounded_thought: thought,
        }
    }
}
