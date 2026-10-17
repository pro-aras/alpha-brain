//! Alpha 7 Grounded Language, Grammar Road & "The Mouth" (Option 2 + Phase 2B/2C/2D)
//!
//! Ensures Alpha 7 understands the words it speaks and thinks on:
//! - Every word is wired directly to sensory-motor trait neurons, Concept Hub assemblies,
//!   and causal action->outcome transitions.
//! - Phase 2B: Answers comparative questions (`compare A and B`, `how is A different from B?`)
//!   and causal failure/why questions (`why did press_switch fail?`, `why eyes:darkness_remains?`)
//!   directly from its grounded Concept Web and Predictive Engine rules.

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
    /// Phase 2B: User asks to compare two concepts ("compare cat and dog", "difference between cat and dog").
    AskComparison {
        concept_a: String,
        concept_b: String,
    },
    /// Phase 2B: User asks why an action failed or why a trait occurred ("why did press_switch fail?", "why darkness_remains?").
    AskWhy { subject: String },
    /// User asks what will happen next if an action is taken ("what happens if press_switch?").
    AskPrediction { action: String },
    /// User directs Alpha 7 toward a goal ("how to reach eyes:knowledge_gained?", "goal eyes:light_on").
    AskGoalScenario { goal_trait: String },
    /// Phase 2C: User asks Alpha 7 to synthesize & verify code for a target ("synthesize code for 42").
    AskCodeSynthesis { target_spec: String },
    /// Phase 2D: User asks Alpha 7 to run a hippocampal sleep replay cycle ("sleep consolidate", "consolidate memories").
    AskSleepConsolidation,
    /// Phase 3A: User asks Alpha 7 to sit the 8 held-out School Exams vs. Null Twin ("run exams", "sit school exams").
    AskSchoolExams,
    /// Phase 3B: User asks Alpha 7 to complete a sentence using CorticalSequenceMemory ("complete: the little red").
    AskSentenceCompletion { prefix: String },
    /// Phase 3D: User asks Alpha 7 to solve the multi-step Key-Door-Vault tool puzzle ("solve door puzzle", "unlock vault door").
    AskSolveKeyDoorPuzzle,
    /// Phase 4A: User asks Alpha 7 about its birth, identity, memories, or life timeline ("who are you?", "what are you?", "tell me about yourself").
    AskAutobiography,
    /// Phase 18 (`E12` Role-Filler Binding): User asks how Alpha 7 came to life, who made/created/built it, or what made it (`AGENT -> CREATE -> SELF`).
    AskGenesisAndCreator,
    /// Phase 18 (`E12` Role-Filler Reversal): User asks what Alpha 7 itself made, built, discovered, or created (`SELF -> CREATE -> ARTIFACT`).
    AskSelfCreations,
    /// Phase 18 (`E11`/`E13`): User asks what Alpha 7 is doing right now, how its brain/Crucible is working, or its current status.
    AskLiveBrainAndCrucibleState,
    /// Phase 18 (`E14` ALife): User asks about Artificial Life (ALife), autopoiesis, morphogenetic self-repair, or open-ended niche co-evolution.
    AskAlifeAutopoiesis,
    /// Phase 18 (`E12` 15Hz Cortical Multiplexer): User asks a multi-clause compound question ("Who made you? What are you?", "Who are you? What made you?").
    MultiClauseCompound {
        clauses: Vec<String>,
        intents: Vec<UtteranceIntent>,
    },
    /// Phase 4A: User asks about Alpha 7's lineage, Alpha 3's life & work, Alpha 6, or the 6 Laws ("what did you learn from alpha 3?", "lineage", "ancestors").
    AskLineage { target: String },
    /// Phase 4B: User asks about Alpha 7's conceptual mistakes, self-analysis hypotheses, and improvements ("mistakes", "self analysis", "how did you improve?").
    AskSelfAnalysis,
    /// Phase 4B: User coaches Alpha 7 in real time ("coach: <question> | <answer> | <conceptual explanation>").
    ApplyCoaching {
        prompt: String,
        answer: String,
        explanation: String,
    },
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

    /// Splits a multi-clause user utterance into ordered pragmatic clauses (`E12` 15Hz Cortical Multiplexer).
    pub fn split_pragmatic_clauses(utterance: &str) -> Vec<String> {
        let trimmed = utterance.trim();
        let lower = trimmed.to_lowercase();
        if lower.starts_with("coach:")
            || lower.starts_with("complete:")
            || lower.starts_with("claim:")
            || lower.starts_with("decode:")
            || lower.starts_with("read:")
            || lower.starts_with("synthesize code")
            || lower.starts_with("write code")
        {
            return vec![trimmed.to_string()];
        }

        let mut raw_segments = Vec::new();
        let mut current = String::new();
        for ch in trimmed.chars() {
            if ch == '?' || ch == '!' || ch == ';' {
                let seg = current.trim();
                if !seg.is_empty() {
                    raw_segments.push(seg.to_string());
                }
                current.clear();
            } else {
                current.push(ch);
            }
        }
        let tail = current.trim().trim_end_matches('.').trim();
        if !tail.is_empty() {
            raw_segments.push(tail.to_string());
        }

        // Also split compound clauses joined by coordinating conjunctions before an interrogative
        // e.g. "Who are you and how did you come to life"
        let mut final_clauses = Vec::new();
        let interrogative_conjunctions = [
            " and who ",
            " and what ",
            " and how ",
            " and why ",
            " and where ",
            " and when ",
        ];
        for seg in raw_segments {
            let seg_low = seg.to_lowercase();
            let mut split_found = None;
            for pat in &interrogative_conjunctions {
                if let Some(idx) = seg_low.find(pat) {
                    split_found = Some((idx, pat.len()));
                    break;
                }
            }
            if let Some((idx, _pat_len)) = split_found {
                let first = seg[..idx].trim();
                // Keep the interrogative word ("who ...", "what ...", "how ...") in the second clause
                let second = seg[idx + 5..].trim();
                if !first.is_empty() {
                    final_clauses.push(first.to_string());
                }
                if !second.is_empty() {
                    final_clauses.push(second.to_string());
                }
            } else {
                final_clauses.push(seg);
            }
        }
        final_clauses
    }

    /// Parses the user's utterance into a grounded cognitive intent (or a multiplexed multi-clause compound intent).
    pub fn parse_intent(&self, utterance: &str) -> UtteranceIntent {
        let clauses = Self::split_pragmatic_clauses(utterance);
        if clauses.len() >= 2 {
            let intents: Vec<UtteranceIntent> = clauses
                .iter()
                .map(|c| self.parse_single_clause_intent(c))
                .collect();
            return UtteranceIntent::MultiClauseCompound { clauses, intents };
        }
        self.parse_single_clause_intent(utterance)
    }

    /// Parses a single clause using role-order-sensitive pragmatic binding (`E12`).
    pub fn parse_single_clause_intent(&self, utterance: &str) -> UtteranceIntent {
        let trimmed_orig = utterance.trim();
        let lower = trimmed_orig.to_lowercase();
        let clean = lower
            .trim_end_matches('?')
            .trim_end_matches('!')
            .trim_end_matches('.')
            .trim();

        // Phase 4B: Real-time interactive conceptual coaching:
        // `"coach: <prompt> | <answer> | <explanation>"`
        // Phase 0 Security Gate (Fixes P3 / S2 / X7): require non-empty multi-word prompt & answer.
        if let Some(rest_orig) = trimmed_orig
            .strip_prefix("coach:")
            .or_else(|| trimmed_orig.strip_prefix("Coach:"))
            .or_else(|| trimmed_orig.strip_prefix("COACH:"))
        {
            let parts: Vec<&str> = rest_orig.splitn(3, '|').collect();
            if parts.len() >= 2 {
                let p = parts[0].trim().to_string();
                let a = parts[1].trim().to_string();
                if p.split_whitespace().count() >= 2 && !a.is_empty() {
                    let exp = if parts.len() >= 3 {
                        parts[2].trim().to_string()
                    } else {
                        "User-guided conceptual demonstration".to_string()
                    };
                    return UtteranceIntent::ApplyCoaching {
                        prompt: p,
                        answer: a,
                        explanation: exp,
                    };
                }
            }
        }

        // Tokenize clause for syntactic role-filler position analysis (`E12`)
        let tokens: Vec<String> = clean
            .split(|c: char| !c.is_alphanumeric() && c != '_')
            .filter(|s| !s.is_empty())
            .map(|s| s.to_lowercase())
            .collect();

        // Phase 18 (`E14` ALife): Artificial Life, Autopoiesis, Morphogenetic Self-Repair, Open-Ended Evolution
        if clean.contains("alife")
            || clean.contains("artificial life")
            || clean.contains("autopoies")
            || clean.contains("morphogen")
            || clean.contains("self-repair")
            || clean.contains("self repair")
            || clean.contains("niche coevolution")
            || clean.contains("open-ended evolution")
            || clean.contains("basal cognition")
        {
            return UtteranceIntent::AskAlifeAutopoiesis;
        }

        // Phase 18 (`E12` Role-Filler Disambiguation):
        // Distinguish `AGENT -> CREATE/MAKE/BUILD/TEACH -> SELF` ("who made you", "what made you", "how were you made")
        // from `SELF -> CREATE/MAKE/BUILD/TEACH -> OBJECT` ("what you made", "what did you make", "what have you built").
        let create_verb_pos = tokens.iter().position(|w| {
            matches!(
                w.as_str(),
                "made"
                    | "make"
                    | "makes"
                    | "making"
                    | "built"
                    | "build"
                    | "builds"
                    | "created"
                    | "create"
                    | "creates"
                    | "formed"
                    | "form"
                    | "designed"
                    | "design"
                    | "birthed"
                    | "constructed"
                    | "taught"
                    | "teach"
                    | "discovered"
                    | "discover"
            )
        });
        let self_pronoun_pos = tokens
            .iter()
            .position(|w| matches!(w.as_str(), "you" | "your" | "yourself"));
        let has_passive_aux_before_you = if let Some(y_idx) = self_pronoun_pos {
            tokens[..y_idx]
                .iter()
                .any(|w| matches!(w.as_str(), "were" | "was" | "are" | "been" | "be" | "get" | "got"))
        } else {
            false
        };

        if let (Some(v_idx), Some(y_idx)) = (create_verb_pos, self_pronoun_pos) {
            if v_idx < y_idx || has_passive_aux_before_you {
                // Verb precedes "you" ("what made you", "who made you", "who built you")
                // OR passive construction ("how were you made", "when were you created") -> Genesis & Creator!
                return UtteranceIntent::AskGenesisAndCreator;
            } else {
                // "you" precedes active creation verb ("what you made", "what did you make", "what have you built") -> Self Creations!
                return UtteranceIntent::AskSelfCreations;
            }
        }

        // Natural paraphrases asking how Alpha 7 came to life / was born / originated (`E12`)
        if clean.contains("came to life")
            || clean.contains("come to life")
            || clean.contains("came alive")
            || clean.contains("come alive")
            || clean.contains("how were you born")
            || clean.contains("when were you born")
            || clean.contains("where did you come from")
            || clean.contains("how did you start")
            || clean.contains("how did you begin")
            || clean.contains("your origin")
            || clean.contains("your genesis")
            || clean.contains("your creator")
        {
            return UtteranceIntent::AskGenesisAndCreator;
        }

        // Phase 18 (`E11`/`E13`): Live Brain, Sovereign Crucible & Current Situation
        if clean == "what are you doing"
            || clean == "what are you doing right now"
            || clean == "what are you working on"
            || clean == "how are you"
            || clean == "how are you doing"
            || clean.contains("how is your brain")
            || clean.contains("current situation")
            || clean.contains("your current state")
            || clean.contains("sovereign crucible")
            || clean == "crucible"
            || clean == "status"
            || clean == "brain status"
        {
            return UtteranceIntent::AskLiveBrainAndCrucibleState;
        }

        // Phase 4A: Ancestral Lineage, Alpha 3's life & work, Alpha 6, or the 6 Laws
        if clean.contains("alpha 3")
            || clean.contains("alpha3")
            || clean.contains("alpha 6")
            || clean.contains("alpha6")
            || clean.contains("brain-long-6")
            || clean.contains("lineage")
            || clean.contains("ancestor")
            || clean.contains("past sel")
            || clean.contains("immutable law")
            || clean == "laws"
            || clean == "what are your laws"
        {
            let target = if clean.contains("alpha 6")
                || clean.contains("alpha6")
                || clean.contains("brain-long-6")
            {
                "alpha6".to_string()
            } else if clean.contains("law") {
                "laws".to_string()
            } else if clean.contains("alpha 3") || clean.contains("alpha3") {
                "alpha3".to_string()
            } else {
                "all".to_string()
            };
            return UtteranceIntent::AskLineage { target };
        }

        // Phase 4A + Phase 18 (`E12`): Autobiography, identity, and episodic life memories
        if clean == "who are you"
            || clean == "what are you"
            || clean == "who is alpha 7"
            || clean == "what is alpha 7"
            || clean == "who are you really"
            || clean == "tell me who you are"
            || clean == "introduce yourself"
            || clean == "describe yourself"
            || clean.contains("what happened to you")
            || clean.contains("your life")
            || clean.contains("your memories")
            || clean.contains("do you remember")
            || clean == "autobiography"
            || clean == "tell me about yourself"
        {
            return UtteranceIntent::AskAutobiography;
        }

        // Phase 4B: Self-Analysis, mistakes, and conceptual improvements
        if clean.contains("mistake")
            || clean.contains("self analysis")
            || clean.contains("self-analysis")
            || clean.contains("how did you improve")
            || clean.contains("what did you fix")
            || clean == "coach lessons"
            || clean == "improvements"
        {
            return UtteranceIntent::AskSelfAnalysis;
        }

        if clean == "what is this"
            || clean == "what do you see"
            || clean == "what do you sense"
            || clean == "recognize"
        {
            return UtteranceIntent::AskCurrentPerception;
        }

        if clean == "sleep"
            || clean == "sleep consolidate"
            || clean == "consolidate"
            || clean == "consolidate memories"
            || clean == "replay memories"
        {
            return UtteranceIntent::AskSleepConsolidation;
        }

        if clean == "run exams"
            || clean == "sit exams"
            || clean == "sit school exams"
            || clean == "school exams"
            || clean == "school benchmark"
        {
            return UtteranceIntent::AskSchoolExams;
        }

        if clean == "solve puzzle"
            || clean == "solve door puzzle"
            || clean == "solve key door puzzle"
            || clean == "unlock door"
            || clean == "open vault door"
        {
            return UtteranceIntent::AskSolveKeyDoorPuzzle;
        }

        if let Some(rest) = clean
            .strip_prefix("complete: ")
            .or_else(|| clean.strip_prefix("complete sentence "))
            .or_else(|| clean.strip_prefix("complete "))
        {
            let p = rest.trim();
            if !p.is_empty() {
                return UtteranceIntent::AskSentenceCompletion {
                    prefix: p.to_string(),
                };
            }
        }

        if let Some(rest) = clean
            .strip_prefix("synthesize code for ")
            .or_else(|| clean.strip_prefix("synthesize code "))
            .or_else(|| clean.strip_prefix("write code for "))
            .or_else(|| clean.strip_prefix("code goal "))
        {
            return UtteranceIntent::AskCodeSynthesis {
                target_spec: rest.trim().to_string(),
            };
        }

        // Phase 2B: Comparative queries ("compare A and B", "how is A different from B", "difference between A and B")
        if let Some(rest) = clean
            .strip_prefix("compare ")
            .or_else(|| clean.strip_prefix("difference between "))
        {
            if let Some((a, b)) = rest.split_once(" and ").or_else(|| rest.split_once(" vs ")) {
                let ca = a.trim().to_string();
                let cb = b.trim().to_string();
                if !ca.is_empty() && !cb.is_empty() {
                    return UtteranceIntent::AskComparison {
                        concept_a: ca,
                        concept_b: cb,
                    };
                }
            }
        }
        if let Some(rest) = clean.strip_prefix("how is ") {
            if let Some((a, b)) = rest.split_once(" different from ") {
                let ca = a.trim().to_string();
                let cb = b.trim().to_string();
                if !ca.is_empty() && !cb.is_empty() {
                    return UtteranceIntent::AskComparison {
                        concept_a: ca,
                        concept_b: cb,
                    };
                }
            }
        }

        // Phase 2B: Causal Why queries ("why did X fail", "why X")
        if let Some(rest) = clean
            .strip_prefix("why did ")
            .or_else(|| clean.strip_prefix("why "))
        {
            let subj = rest.trim().trim_end_matches(" fail").trim();
            if !subj.is_empty() {
                return UtteranceIntent::AskWhy {
                    subject: subj.replace(' ', "_"),
                };
            }
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
            .or_else(|| clean.strip_prefix("what is an "))
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

    /// Phase 2B: Explains why an action failed or why a specific outcome occurred by inspecting
    /// learned causal rules and counterfactual blocker exceptions.
    pub fn explain_causal_why(&self, predictor: &PredictiveEngine, subject: &str) -> String {
        let subj_lower = subject.trim().to_lowercase();
        for rule in &predictor.rules {
            if rule.action.to_lowercase() == subj_lower
                || rule.action.to_lowercase().contains(&subj_lower)
                || rule
                    .learned_exceptions
                    .iter()
                    .any(|(b, alt)| b.contains(&subj_lower) || alt.contains(&subj_lower))
            {
                if !rule.learned_exceptions.is_empty() {
                    let ex_list: Vec<String> = rule
                        .learned_exceptions
                        .iter()
                        .map(|(blocker, alt)| {
                            format!(
                                "blocking condition '{}' diverted expected outcome {:?} to '{}'",
                                blocker,
                                rule.predicted_outcomes.keys().collect::<Vec<_>>(),
                                alt
                            )
                        })
                        .collect();
                    return format!(
                        "Causal failure analysis for '{}': {}",
                        rule.action,
                        ex_list.join("; ")
                    );
                } else {
                    let outs: Vec<String> = rule.predicted_outcomes.keys().cloned().collect();
                    return format!(
                        "Action '{}' normally requires {:?} and produces {:?} (reliability {}/{}).",
                        rule.action,
                        rule.trigger_traits,
                        outs,
                        rule.successes,
                        rule.successes + rule.failures
                    );
                }
            }
        }
        format!(
            "I do not have a recorded causal failure or rule matching '{}' yet.",
            subject
        )
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
        let thought = web.understand_utterance_in_fabric(fabric, utterance);

        if fabric.lesioned {
            return MouthUtterance {
                intent,
                spoken_response: format!(
                    "[TOOL:ABSTAIN] Neural fabric is lesioned; cannot ground or recall '{}'.",
                    utterance.trim()
                ),
                grounded_thought: thought,
            };
        }

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
                let recs =
                    web.recognize_from_traits_in_fabric(fabric, &current_frame.to_neural_traits());
                self.speak_perception(current_frame, &recs)
            }
            UtteranceIntent::AskConcept { concept } => {
                let c_low = concept.trim().to_lowercase();
                if let Some(node) = web.concepts.get(&c_low) {
                    let has_live_hub_synapse = fabric
                        .synapses
                        .get(&node.word_neuron_id)
                        .map(|list| list.iter().any(|s| s.weight > 0.01))
                        .unwrap_or(false)
                        || fabric
                            .synapses
                            .get(&node.hub_neuron_id)
                            .map(|list| list.iter().any(|s| s.weight > 0.01))
                            .unwrap_or(false);
                    if !has_live_hub_synapse {
                        format!(
                            "[TOOL:ABSTAIN] Concept '{}' has no intact neural synapses in the fabric.",
                            concept
                        )
                    } else {
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
                        let categories: Vec<String> = web
                            .relations
                            .iter()
                            .filter(|(s, r, _, _)| s == &node.name && r == "is_a")
                            .map(|(_, _, cat, _)| cat.clone())
                            .collect();
                        let cat_str = if categories.is_empty() {
                            String::new()
                        } else {
                            format!("; categories=[{}]", categories.join(", "))
                        };
                        format!(
                            "'{}' (experienced {} time(s), familiarity {:.0}%): core invariants=[{}]; variable traits=[{}]; affordances=[{}]{}.",
                            node.name,
                            node.exposures,
                            node.familiarity * 100.0,
                            core.join(", "),
                            var.join(", "),
                            affordances.join(", "),
                            cat_str
                        )
                    }
                } else {
                    let rel_parents: Vec<String> = web
                        .relations
                        .iter()
                        .filter(|(s, r, _, _)| s == &c_low && (r == "is_a" || r == "coached_answer"))
                        .map(|(_, r, cat, _)| format!("{} {}", r, cat))
                        .collect();
                    if !rel_parents.is_empty() && !fabric.synapses.is_empty() {
                        format!(
                            "From my Concept Web & Alpha 3 heritage, '{}': [{}].",
                            c_low,
                            rel_parents.join(", ")
                        )
                    } else {
                        format!(
                            "[TOOL:ABSTAIN] I have not experienced '{}' yet. Show me '{}' once or twice so I can bind its traits.",
                            concept, concept
                        )
                    }
                }
            }
            UtteranceIntent::AskComparison {
                concept_a,
                concept_b,
            } => {
                if let Some(comp) = web.compare_concepts(concept_a, concept_b) {
                    comp.summary
                } else {
                    format!(
                        "[TOOL:ABSTAIN] To compare '{}' and '{}', both must be grounded in my Concept Web first.",
                        concept_a, concept_b
                    )
                }
            }
            UtteranceIntent::AskWhy { subject } => self.explain_causal_why(predictor, subject),
            UtteranceIntent::AskPrediction { action } => {
                let preds = predictor.predict_next(&current_frame.to_neural_traits(), action);
                if preds.is_empty() {
                    format!(
                        "[TOOL:ABSTAIN] I have no prediction yet for action '{}' in the current sensory state.",
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
            UtteranceIntent::AskCodeSynthesis { target_spec } => {
                format!(
                    "Initiating goal-directed code synthesis for target '{}'.",
                    target_spec
                )
            }
            UtteranceIntent::AskSleepConsolidation => {
                "Initiating Hippocampal-Neocortical sharp-wave ripple sleep consolidation cycle."
                    .to_string()
            }
            UtteranceIntent::AskSchoolExams => {
                "Sitting the 8 held-out School Exams (1,050 items across Kindergarten, G1-G3, and College) vs. Null Twin."
                    .to_string()
            }
            UtteranceIntent::AskSentenceCompletion { prefix } => {
                format!(
                    "Completing sequence prefix '{}' from Cortical Sequence Memory.",
                    prefix
                )
            }
            UtteranceIntent::AskSolveKeyDoorPuzzle => {
                "Executing multi-step Key-Door-Vault tool puzzle on the 2D World Canvas."
                    .to_string()
            }
            UtteranceIntent::AskAutobiography => {
                "Recalling my birth, autobiographical life stages, and episodic memory timeline."
                    .to_string()
            }
            UtteranceIntent::AskGenesisAndCreator => {
                "Recalling my genesis, human creator, and Pure Road dendritic awakening."
                    .to_string()
            }
            UtteranceIntent::AskSelfCreations => {
                "Recalling the concepts, causal laws, code syntheses, and Crucible routes I have created and discovered."
                    .to_string()
            }
            UtteranceIntent::AskLiveBrainAndCrucibleState => {
                "Reading my live UnifiedCoreBrain and Sovereign Crucible telemetry."
                    .to_string()
            }
            UtteranceIntent::AskAlifeAutopoiesis => {
                "Recalling my ALife Autopoietic Morphogenesis, Precarious Metabolic Viability, and Open-Ended Niche Co-Evolution."
                    .to_string()
            }
            UtteranceIntent::MultiClauseCompound { clauses, .. } => {
                format!(
                    "Multiplexing {} pragmatic clauses via 15Hz cortical buffer.",
                    clauses.len()
                )
            }
            UtteranceIntent::AskLineage { target } => {
                format!(
                    "Recalling ancestral lineage and heritage for '{}'.",
                    target
                )
            }
            UtteranceIntent::AskSelfAnalysis => {
                "Recalling my conceptual self-analysis hypotheses and verified coaching lessons."
                    .to_string()
            }
            UtteranceIntent::ApplyCoaching { prompt, answer, .. } => {
                format!(
                    "Applying real-time conceptual coaching for '{}' -> '{}'.",
                    prompt, answer
                )
            }
            UtteranceIntent::GeneralThought { .. } => {
                if thought.activated_concepts.is_empty() {
                    format!(
                        "[TOOL:ABSTAIN] I heard '{}', but none of those words are grounded in my concept web yet.",
                        utterance.trim()
                    )
                } else {
                    let traits_preview: Vec<String> = thought
                        .evoked_sensory_traits
                        .iter()
                        .take(6)
                        .cloned()
                        .collect();
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
