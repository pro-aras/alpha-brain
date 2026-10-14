//! Alpha 7 Predictive World Model, Surprise Failure Analyzer & Goal-Directed Scenario Simulator
//!
//! Implements:
//! 1. Forward Prediction ("what will happen next") given current sensory state & action.
//! 2. Prediction Failure Analysis ("if something fails to happen they analyze it and learn from it"):
//!    - Compares predicted traits against actual observed traits.
//!    - When an expected outcome fails to occur, isolates contextual differences (blocking or
//!      altering traits), weakens the over-generalized prediction, and forms a conditional rule
//!      explaining the failure.
//! 3. Goal-Directed Scenario Simulation ("calculating possibilities and scenarios directed toward
//!    our needs or goals"):
//!    - Evaluates candidate multi-step action/thought rollouts toward a target goal trait.

use crate::fabric::SparseNeuralFabric;
use crate::neuron::Modality;
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};

/// A learned causal transition rule: `(context_traits, action) -> predicted_outcomes`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CausalRule {
    pub rule_id: u64,
    pub trigger_traits: Vec<String>,
    pub action: String,
    /// Predicted outcome trait -> probability / synaptic strength in [0.0, 1.0].
    pub predicted_outcomes: FxHashMap<String, f32>,
    /// Blocking / exception traits discovered when a prediction failed!
    /// Maps `blocking_trait -> alternative_outcome`.
    pub learned_exceptions: FxHashMap<String, String>,
    pub successes: u32,
    pub failures: u32,
}

/// Detailed diagnostic produced when a prediction matches or fails to happen.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PredictionEvaluation {
    pub action: String,
    pub predicted_traits: Vec<(String, f32)>,
    pub actual_traits: Vec<String>,
    /// Traits that were predicted to happen, but FAILED to happen!
    pub failed_to_happen: Vec<String>,
    /// Traits that happened unexpectedly without being predicted.
    pub unexpected_traits: Vec<String>,
    /// True if any high-confidence prediction failed or unexpected surprise occurred.
    pub prediction_failed: bool,
    /// Human-readable causal analysis of why the prediction failed and what Alpha 7 learned.
    pub analysis_report: String,
}

/// A simulated future branch when calculating possibilities and scenarios toward a goal.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioBranch {
    pub actions: Vec<String>,
    pub predicted_trajectory: Vec<Vec<String>>,
    pub probability: f32,
    pub reaches_goal: bool,
    pub rationale: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct PredictiveEngine {
    pub rules: Vec<CausalRule>,
}

impl PredictiveEngine {
    pub fn new() -> Self {
        Self { rules: Vec::new() }
    }

    /// Predicts what sensory/state traits will happen next if `action` is taken in `current_traits`.
    pub fn predict_next(
        &self,
        current_traits: &[String],
        action: &str,
    ) -> Vec<(String, f32)> {
        let mut outcome_scores: FxHashMap<String, f32> = FxHashMap::default();

        for rule in &self.rules {
            if rule.action != action {
                continue;
            }
            // Check overlap between current_traits and rule.trigger_traits
            let matched_triggers = rule
                .trigger_traits
                .iter()
                .filter(|t| current_traits.contains(t))
                .count();
            if matched_triggers == 0 && !rule.trigger_traits.is_empty() {
                continue;
            }
            let match_ratio = if rule.trigger_traits.is_empty() {
                1.0
            } else {
                (matched_triggers as f32) / (rule.trigger_traits.len() as f32)
            };
            if match_ratio < 0.4 {
                continue;
            }

            // Check if any known exception / blocking trait is present in `current_traits`!
            let mut blocked_by: Option<(&String, &String)> = None;
            for (blocker, alt_outcome) in &rule.learned_exceptions {
                if current_traits.contains(blocker) {
                    blocked_by = Some((blocker, alt_outcome));
                    break;
                }
            }

            if let Some((_blocker, alt_outcome)) = blocked_by {
                // We previously analyzed a failure under this blocker and learned the alternative outcome!
                let entry = outcome_scores.entry(alt_outcome.clone()).or_insert(0.0);
                *entry = (*entry + 0.90 * match_ratio).min(1.0);
            } else {
                for (out_trait, &prob) in &rule.predicted_outcomes {
                    if prob >= 0.25 {
                        let entry = outcome_scores.entry(out_trait.clone()).or_insert(0.0);
                        *entry = (*entry + prob * match_ratio).min(1.0);
                    }
                }
            }
        }

        let mut list: Vec<(String, f32)> = outcome_scores.into_iter().collect();
        list.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        list
    }

    /// Observes a transition `(context_traits, action) -> actual_outcomes`, compares against what
    /// Alpha 7 predicted, and if something failed to happen, analyzes the failure and updates
    /// both the CausalRule and the `SparseNeuralFabric` apical synapses.
    pub fn observe_and_analyze(
        &mut self,
        fabric: &mut SparseNeuralFabric,
        context_traits: &[String],
        action: &str,
        actual_outcomes: &[String],
    ) -> PredictionEvaluation {
        let predicted = self.predict_next(context_traits, action);
        let actual_set: std::collections::HashSet<&str> =
            actual_outcomes.iter().map(|s| s.as_str()).collect();
        let predicted_set: std::collections::HashSet<&str> = predicted
            .iter()
            .filter(|(_, p)| *p >= 0.45)
            .map(|(t, _)| t.as_str())
            .collect();

        let failed_to_happen: Vec<String> = predicted
            .iter()
            .filter(|(t, p)| *p >= 0.45 && !actual_set.contains(t.as_str()))
            .map(|(t, _)| t.clone())
            .collect();

        let unexpected_traits: Vec<String> = actual_outcomes
            .iter()
            .filter(|t| !predicted_set.contains(t.as_str()))
            .cloned()
            .collect();

        let prediction_failed = !failed_to_happen.is_empty() || !unexpected_traits.is_empty();
        let act_nid =
            fabric.ensure_trait_neuron(&format!("hands:{}", action), Modality::TactileHand);

        // Find or create matching rule for this action
        let mut rule_idx = None;
        for (i, r) in self.rules.iter().enumerate() {
            if r.action == action {
                rule_idx = Some(i);
                break;
            }
        }

        let analysis_report = if let Some(idx) = rule_idx {
            let rule = &mut self.rules[idx];
            if !failed_to_happen.is_empty() {
                rule.failures += 1;
                // Analyze WHY the expected outcome failed to happen:
                // Identify novel context traits in `context_traits` that were NOT in `rule.trigger_traits`
                let novel_context: Vec<String> = context_traits
                    .iter()
                    .filter(|t| !rule.trigger_traits.contains(t))
                    .cloned()
                    .collect();

                let alt_outcome = unexpected_traits
                    .first()
                    .cloned()
                    .unwrap_or_else(|| "state:nothing_happened".to_string());

                if let Some(blocker) = novel_context.first() {
                    rule.learned_exceptions
                        .insert(blocker.clone(), alt_outcome.clone());

                    // Wire the blocker + action -> alt_outcome into the neural fabric's apical dendrites
                    let blocker_nid =
                        fabric.ensure_trait_neuron(blocker, Modality::from_str(blocker));
                    let alt_nid =
                        fabric.ensure_trait_neuron(&alt_outcome, Modality::from_str(&alt_outcome));
                    fabric.upsert_synapse(blocker_nid, alt_nid, 0.85, true, 1.5);
                    fabric.upsert_synapse(act_nid, alt_nid, 0.55, true, 1.5);

                    format!(
                        "PREDICTION FAILURE ANALYZED: Expected {:?} after action '{}', but it failed to happen. \
                        Isolated contextual condition '{}' as the cause and learned new exception -> '{}'.",
                        failed_to_happen, action, blocker, alt_outcome
                    )
                } else {
                    // No novel context trait: the rule itself was wrong/changed; depress old outcome and learn new one
                    for failed in &failed_to_happen {
                        if let Some(w) = rule.predicted_outcomes.get_mut(failed) {
                            *w = (*w - 0.50).max(0.0);
                        }
                        let f_nid =
                            fabric.ensure_trait_neuron(failed, Modality::from_str(failed));
                        fabric.upsert_synapse(act_nid, f_nid, -0.50, true, 1.5);
                    }
                    for actual in actual_outcomes {
                        let entry = rule.predicted_outcomes.entry(actual.clone()).or_insert(0.0);
                        *entry = (*entry + 0.80).min(1.0);
                        let a_nid =
                            fabric.ensure_trait_neuron(actual, Modality::from_str(actual));
                        fabric.upsert_synapse(act_nid, a_nid, 0.80, true, 1.5);
                    }
                    format!(
                        "PREDICTION FAILURE ANALYZED: Expected {:?} failed in same context; depressed false prediction and updated outcome to {:?}.",
                        failed_to_happen, actual_outcomes
                    )
                }
            } else {
                rule.successes += 1;
                for actual in actual_outcomes {
                    let entry = rule.predicted_outcomes.entry(actual.clone()).or_insert(0.65);
                    *entry = (*entry + 0.20).min(1.0);
                    let a_nid = fabric.ensure_trait_neuron(actual, Modality::from_str(actual));
                    fabric.upsert_synapse(act_nid, a_nid, 0.25, true, 1.5);
                }
                format!(
                    "PREDICTION CONFIRMED: Action '{}' produced expected outcome {:?} (reliability {}/{}).",
                    action,
                    actual_outcomes,
                    rule.successes,
                    rule.successes + rule.failures
                )
            }
        } else {
            // First time performing this action: 1-shot BTSP causal rule acquisition!
            let mut outcomes_map = FxHashMap::default();
            for out in actual_outcomes {
                outcomes_map.insert(out.clone(), 0.85);
                let out_nid = fabric.ensure_trait_neuron(out, Modality::from_str(out));
                fabric.upsert_synapse(act_nid, out_nid, 0.85, true, 1.5);
                for ctx in context_traits {
                    let ctx_nid = fabric.ensure_trait_neuron(ctx, Modality::from_str(ctx));
                    fabric.upsert_synapse(ctx_nid, out_nid, 0.45, true, 1.5);
                }
            }
            let rule_id = (self.rules.len() + 1) as u64;
            self.rules.push(CausalRule {
                rule_id,
                trigger_traits: context_traits.to_vec(),
                action: action.to_string(),
                predicted_outcomes: outcomes_map,
                learned_exceptions: FxHashMap::default(),
                successes: 1,
                failures: 0,
            });
            format!(
                "ONE-SHOT CAUSAL LEARNING: First observation of action '{}' in context {:?} -> learned outcome {:?}.",
                action, context_traits, actual_outcomes
            )
        };

        PredictionEvaluation {
            action: action.to_string(),
            predicted_traits: predicted,
            actual_traits: actual_outcomes.to_vec(),
            failed_to_happen,
            unexpected_traits,
            prediction_failed,
            analysis_report,
        }
    }

    /// Simulates multi-step possibilities and scenarios directed toward `goal_trait`
    /// starting from `initial_traits` up to `max_depth` steps.
    pub fn simulate_scenarios(
        &self,
        initial_traits: &[String],
        goal_trait: &str,
        max_depth: usize,
    ) -> Vec<ScenarioBranch> {
        let depth_limit = max_depth.clamp(1, 4);
        let mut branches: Vec<ScenarioBranch> = Vec::new();

        // Collect all known candidate actions
        let mut candidate_actions: Vec<String> =
            self.rules.iter().map(|r| r.action.clone()).collect();
        candidate_actions.sort();
        candidate_actions.dedup();

        // Breadth-first scenario rollout over learned causal rules
        let mut frontier: Vec<(Vec<String>, Vec<Vec<String>>, Vec<String>, f32)> = vec![(
            Vec::new(),
            Vec::new(),
            initial_traits.to_vec(),
            1.0,
        )];

        for _step in 0..depth_limit {
            let mut next_frontier = Vec::new();
            for (actions_so_far, traj_so_far, state_traits, prob_so_far) in frontier {
                for act in &candidate_actions {
                    let preds = self.predict_next(&state_traits, act);
                    if preds.is_empty() {
                        continue;
                    }
                    let mut next_state = state_traits.clone();
                    let mut step_outcomes = Vec::new();
                    let mut best_p = 0.0f32;
                    for (t, p) in &preds {
                        if *p >= 0.35 {
                            step_outcomes.push(t.clone());
                            if !next_state.contains(t) {
                                next_state.push(t.clone());
                            }
                            if *p > best_p {
                                best_p = *p;
                            }
                        }
                    }
                    if step_outcomes.is_empty() {
                        continue;
                    }
                    let mut new_actions = actions_so_far.clone();
                    new_actions.push(act.clone());
                    let mut new_traj = traj_so_far.clone();
                    new_traj.push(step_outcomes.clone());
                    let new_prob = prob_so_far * best_p;
                    let reaches_goal = next_state.iter().any(|t| t == goal_trait);

                    let rationale = if reaches_goal {
                        format!(
                            "Goal '{}' reached in {} step(s) via {:?} (confidence {:.2})",
                            goal_trait,
                            new_actions.len(),
                            new_actions,
                            new_prob
                        )
                    } else {
                        format!(
                            "Explored path {:?} -> produces {:?}",
                            new_actions, step_outcomes
                        )
                    };

                    branches.push(ScenarioBranch {
                        actions: new_actions.clone(),
                        predicted_trajectory: new_traj.clone(),
                        probability: new_prob,
                        reaches_goal,
                        rationale,
                    });

                    if !reaches_goal {
                        next_frontier.push((new_actions, new_traj, next_state, new_prob));
                    }
                }
            }
            frontier = next_frontier;
        }

        // Rank scenarios: goal-reaching branches first (shortest & highest probability), then highest probability
        branches.sort_by(|a, b| {
            match (a.reaches_goal, b.reaches_goal) {
                (true, false) => std::cmp::Ordering::Less,
                (false, true) => std::cmp::Ordering::Greater,
                (true, true) => a
                    .actions
                    .len()
                    .cmp(&b.actions.len())
                    .then_with(|| {
                        b.probability
                            .partial_cmp(&a.probability)
                            .unwrap_or(std::cmp::Ordering::Equal)
                    }),
                (false, false) => b
                    .probability
                    .partial_cmp(&a.probability)
                    .unwrap_or(std::cmp::Ordering::Equal),
            }
        });

        branches
    }
}
