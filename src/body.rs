//! Alpha 7 Pure-Rust 5-Sense Embodied Interface (Eyes, Ears, Hands, Smell, Internal Senses)
//!
//! Translates raw observations from the 2D World Canvas, user interactions, and code snippets
//! directly into grounded modality-prefixed neural traits without any Python overhead.

use serde::{Deserialize, Serialize};

/// A unified multi-modal sensory snapshot captured by Alpha 7's 5 senses on a single tick.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SensoryFrame {
    pub eyes: Vec<String>,
    pub ears: Vec<String>,
    pub hands: Vec<String>,
    pub smell: Vec<String>,
    pub senses: Vec<String>,
    pub spoken_words: Vec<String>,
}

impl SensoryFrame {
    pub fn new() -> Self {
        Self::default()
    }

    /// Flattens all 5 sensory streams into grounded modality-prefixed neural trait keys.
    pub fn to_neural_traits(&self) -> Vec<String> {
        let mut traits = Vec::with_capacity(
            self.eyes.len()
                + self.ears.len()
                + self.hands.len()
                + self.smell.len()
                + self.senses.len(),
        );
        for item in &self.eyes {
            traits.push(if item.starts_with("eyes:") {
                item.clone()
            } else {
                format!("eyes:{}", item)
            });
        }
        for item in &self.ears {
            traits.push(if item.starts_with("ears:") {
                item.clone()
            } else {
                format!("ears:{}", item)
            });
        }
        for item in &self.hands {
            traits.push(if item.starts_with("hands:") {
                item.clone()
            } else {
                format!("hands:{}", item)
            });
        }
        for item in &self.smell {
            traits.push(if item.starts_with("smell:") {
                item.clone()
            } else {
                format!("smell:{}", item)
            });
        }
        for item in &self.senses {
            traits.push(if item.starts_with("senses:") {
                item.clone()
            } else {
                format!("senses:{}", item)
            });
        }
        traits
    }
}

/// Visual processing organ: extracts structural traits from visual scenes, 2D canvas fixations, and code.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EyesSensor {
    pub gaze_x: i32,
    pub gaze_y: i32,
}

impl EyesSensor {
    pub fn observe_entity(&self, features: &[&str]) -> Vec<String> {
        features
            .iter()
            .map(|f| {
                if f.starts_with("eyes:") {
                    (*f).to_string()
                } else {
                    format!("eyes:{}", f)
                }
            })
            .collect()
    }

    /// Extracts structural visual traits when Alpha 7 looks at a snippet of code.
    pub fn inspect_code(&self, code_str: &str) -> Vec<String> {
        let mut traits = vec!["eyes:code_block".to_string()];
        let trimmed = code_str.trim();

        // Check for obvious syntax errors (unbalanced parentheses, triple operators, trailing operators)
        let open_parens = trimmed.chars().filter(|&c| c == '(').count();
        let close_parens = trimmed.chars().filter(|&c| c == ')').count();
        let has_double_op = trimmed.contains("+ *")
            || trimmed.contains("* * *")
            || trimmed.contains("/ / /")
            || trimmed.ends_with('+')
            || trimmed.ends_with('*')
            || trimmed.ends_with('-');

        if open_parens != close_parens || has_double_op || trimmed.is_empty() {
            traits.push("eyes:syntax_typo".to_string());
            return traits;
        }

        traits.push("eyes:valid_syntax".to_string());
        if trimmed.contains("fn ") || trimmed.contains("def ") {
            traits.push("eyes:has_function_def".to_string());
        }
        if trimmed.contains("for ") || trimmed.contains("while ") {
            traits.push("eyes:has_loop".to_string());
        }
        if trimmed.contains("print") || trimmed.contains("println") {
            traits.push("eyes:calls_print".to_string());
        }
        if trimmed.contains('+') {
            traits.push("eyes:has_addition".to_string());
        }
        if trimmed.contains('*') {
            traits.push("eyes:has_multiplication".to_string());
        }
        if trimmed.contains('-') {
            traits.push("eyes:has_subtraction".to_string());
        }
        traits
    }
}

/// Auditory & lexical organ: perceives acoustic signatures and spoken words from the user.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct EarsSensor;

impl EarsSensor {
    pub fn listen(&self, sounds: &[&str], utterance: Option<&str>) -> (Vec<String>, Vec<String>) {
        let mut sound_traits: Vec<String> = sounds
            .iter()
            .map(|s| {
                if s.starts_with("ears:") {
                    (*s).to_string()
                } else {
                    format!("ears:{}", s)
                }
            })
            .collect();

        let mut words = Vec::new();
        if let Some(text) = utterance {
            for token in text.split(|c: char| !c.is_alphanumeric() && c != '_') {
                let clean = token.trim().to_lowercase();
                if !clean.is_empty() {
                    words.push(clean.clone());
                    sound_traits.push(format!("ears:heard_{}", clean));
                }
            }
        }
        (sound_traits, words)
    }
}

/// Tactile & motor organ: touches objects, manipulates the 2D world, and executes small code expressions.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct HandsEffector {
    pub hand_x: i32,
    pub hand_y: i32,
}

impl HandsEffector {
    pub fn touch(&self, tactile: &[&str]) -> Vec<String> {
        tactile
            .iter()
            .map(|t| {
                if t.starts_with("hands:") {
                    (*t).to_string()
                } else {
                    format!("hands:{}", t)
                }
            })
            .collect()
    }

    /// Native Rust evaluator for small code snippets practiced by Alpha 7's hands.
    pub fn execute_small_code(&self, code_str: &str) -> Vec<String> {
        let visual = EyesSensor::default().inspect_code(code_str);
        if visual.iter().any(|t| t == "eyes:syntax_typo") {
            return vec![
                "eyes:syntax_error".to_string(),
                "hands:execution_halted".to_string(),
            ];
        }

        // Evaluate simple assignments and arithmetic (`result = A op B`) natively in Rust
        let mut result_val: Option<i64> = None;
        for line in code_str.lines() {
            let l = line.trim();
            if let Some(rhs) = l.strip_prefix("result =").or_else(|| l.strip_prefix("let result =")) {
                let expr = rhs.trim().trim_end_matches(';');
                if let Some((a, b)) = expr.split_once('+') {
                    if let (Ok(x), Ok(y)) = (a.trim().parse::<i64>(), b.trim().parse::<i64>()) {
                        result_val = Some(x + y);
                    }
                } else if let Some((a, b)) = expr.split_once('*') {
                    if let (Ok(x), Ok(y)) = (a.trim().parse::<i64>(), b.trim().parse::<i64>()) {
                        result_val = Some(x * y);
                    }
                } else if let Some((a, b)) = expr.split_once('-') {
                    if let (Ok(x), Ok(y)) = (a.trim().parse::<i64>(), b.trim().parse::<i64>()) {
                        result_val = Some(x - y);
                    }
                } else if let Ok(v) = expr.parse::<i64>() {
                    result_val = Some(v);
                }
            }
        }

        let mut outcomes = vec!["eyes:code_ran_cleanly".to_string()];
        if let Some(v) = result_val {
            if code_str.contains("print") {
                outcomes.push(format!("eyes:printed_{}", v));
            }
            outcomes.push(format!("eyes:result_{}", v));
        }
        outcomes
    }
}

/// Olfactory & chemical/context marker sensor.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SmellSensor;

impl SmellSensor {
    pub fn sniff(&self, scents: &[&str]) -> Vec<String> {
        scents
            .iter()
            .map(|s| {
                if s.starts_with("smell:") {
                    (*s).to_string()
                } else {
                    format!("smell:{}", s)
                }
            })
            .collect()
    }
}

/// Proprioception, surprise arousal, energy, and user bond sensor.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternalSenses {
    pub user_interactions: u32,
    pub last_surprise: f32,
}

impl Default for InternalSenses {
    fn default() -> Self {
        Self {
            user_interactions: 0,
            last_surprise: 0.0,
        }
    }
}

impl InternalSenses {
    pub fn read_state(&mut self, surprise: f32) -> Vec<String> {
        self.last_surprise = surprise;
        let mut traits = vec!["senses:awake".to_string()];
        if surprise >= 0.5 {
            traits.push("senses:high_surprise_alert".to_string());
        } else {
            traits.push("senses:calm_predictive_flow".to_string());
        }
        if self.user_interactions > 0 {
            traits.push("senses:user_bond_active".to_string());
        }
        traits
    }
}

/// Complete Pure-Rust 5-Sense Body for Alpha 7.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Alpha7Body {
    pub eyes: EyesSensor,
    pub ears: EarsSensor,
    pub hands: HandsEffector,
    pub smell: SmellSensor,
    pub internal: InternalSenses,
}

impl Alpha7Body {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn build_frame(
        &mut self,
        eyes: &[&str],
        ears: &[&str],
        hands: &[&str],
        smell: &[&str],
        utterance: Option<&str>,
    ) -> SensoryFrame {
        let (ear_traits, words) = self.ears.listen(ears, utterance);
        if utterance.is_some() {
            self.internal.user_interactions += 1;
        }
        let senses = self.internal.read_state(self.internal.last_surprise);
        SensoryFrame {
            eyes: self.eyes.observe_entity(eyes),
            ears: ear_traits,
            hands: self.hands.touch(hands),
            smell: self.smell.sniff(smell),
            senses,
            spoken_words: words,
        }
    }
}
