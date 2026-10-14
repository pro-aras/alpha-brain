//! Alpha 7 Interactive 2D Spatial World Canvas (Option 3)
//!
//! Provides a continuous/grid 2D spatial arena where Alpha 7's body moves, its eyes saccade
//! and fixate, its nose detects spatial scent gradients, its ears detect acoustic sources,
//! and its hands touch and manipulate objects or code blocks.

use crate::body::{Alpha7Body, SensoryFrame};
use rustc_hash::FxHashMap;
use serde::{Deserialize, Serialize};

/// A multi-sensory entity placed at `(x, y)` on the 2D World Canvas.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorldEntity {
    pub id: String,
    pub concept_label: String,
    pub symbol: char,
    pub x: i32,
    pub y: i32,
    /// Visual traits observed when Alpha 7's eyes fixate on this entity (distance <= 1).
    pub visual_traits: Vec<String>,
    /// Coarse peripheral visual traits observed at distance 2..=4 before foveal fixation.
    pub peripheral_traits: Vec<String>,
    /// Acoustic traits heard within auditory range (distance <= 4).
    pub auditory_traits: Vec<String>,
    /// Tactile traits felt when Alpha 7's hands touch this entity (distance <= 1).
    pub tactile_traits: Vec<String>,
    /// Olfactory scent markers smelled within scent range (distance <= 5).
    pub olfactory_traits: Vec<String>,
    /// Action affordances: `action_name -> resulting sensory traits`.
    pub action_effects: FxHashMap<String, Vec<String>>,
}

/// 2D Spatial World Canvas containing Alpha 7's embodied state and interactive entities.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct World2DCanvas {
    pub width: i32,
    pub height: i32,
    pub agent_x: i32,
    pub agent_y: i32,
    pub gaze_x: i32,
    pub gaze_y: i32,
    pub entities: Vec<WorldEntity>,
    pub step_count: u64,
}

impl World2DCanvas {
    pub fn new(width: i32, height: i32) -> Self {
        let cx = width / 2;
        let cy = height / 2;
        Self {
            width,
            height,
            agent_x: cx,
            agent_y: cy,
            gaze_x: cx,
            gaze_y: cy,
            entities: Vec::new(),
            step_count: 0,
        }
    }

    /// Creates a rich default 2D sandbox populated with multi-sensory entities:
    /// - Cat #1 (Orange Cat at (2, 2))
    /// - Cat #2 (Black Cat at (10, 2))
    /// - Unseen White Cat (at (10, 9))
    /// - Distractor Dog (at (2, 9))
    /// - Light Switch (at (6, 2))
    /// - Code Terminal (at (6, 9))
    pub fn default_sandbox() -> Self {
        let mut world = Self::new(13, 12);
        world.agent_x = 6;
        world.agent_y = 6;
        world.gaze_x = 6;
        world.gaze_y = 6;

        // 1. Orange Cat (top-left)
        let mut cat1_fx = FxHashMap::default();
        cat1_fx.insert(
            "gentle_pet".to_string(),
            vec!["ears:purr".to_string(), "hands:warm_vibration".to_string()],
        );
        world.entities.push(WorldEntity {
            id: "orange_cat".to_string(),
            concept_label: "cat".to_string(),
            symbol: 'c',
            x: 2,
            y: 2,
            visual_traits: vec![
                "pointy_ears".into(),
                "whiskers".into(),
                "slit_pupils".into(),
                "four_legs".into(),
                "long_tail".into(),
                "orange_fur".into(),
            ],
            peripheral_traits: vec!["small_agile_silhouette".into()],
            auditory_traits: vec!["purr".into(), "meow".into()],
            tactile_traits: vec!["soft_fur".into(), "warm_body".into()],
            olfactory_traits: vec!["feline_scent".into()],
            action_effects: cat1_fx,
        });

        // 2. Black Cat (top-right)
        let mut cat2_fx = FxHashMap::default();
        cat2_fx.insert(
            "gentle_pet".to_string(),
            vec!["ears:purr".to_string(), "hands:warm_vibration".to_string()],
        );
        world.entities.push(WorldEntity {
            id: "black_cat".to_string(),
            concept_label: "cat".to_string(),
            symbol: 'C',
            x: 10,
            y: 2,
            visual_traits: vec![
                "pointy_ears".into(),
                "whiskers".into(),
                "slit_pupils".into(),
                "four_legs".into(),
                "long_tail".into(),
                "black_fur".into(),
            ],
            peripheral_traits: vec!["small_agile_silhouette".into()],
            auditory_traits: vec!["purr".into()],
            tactile_traits: vec!["soft_fur".into(), "warm_body".into()],
            olfactory_traits: vec!["feline_scent".into()],
            action_effects: cat2_fx,
        });

        // 3. Unseen White Cat (bottom-right)
        let mut cat3_fx = FxHashMap::default();
        cat3_fx.insert("gentle_pet".to_string(), vec!["ears:purr".to_string()]);
        world.entities.push(WorldEntity {
            id: "white_cat".to_string(),
            concept_label: "cat".to_string(),
            symbol: 'w',
            x: 10,
            y: 9,
            visual_traits: vec![
                "pointy_ears".into(),
                "whiskers".into(),
                "slit_pupils".into(),
                "four_legs".into(),
                "white_fur".into(),
            ],
            peripheral_traits: vec!["small_agile_silhouette".into()],
            auditory_traits: vec![],
            tactile_traits: vec!["soft_fur".into()],
            olfactory_traits: vec!["feline_scent".into(), "rain_ozone".into()],
            action_effects: cat3_fx,
        });

        // 4. Brown Dog (bottom-left)
        let mut dog_fx = FxHashMap::default();
        dog_fx.insert(
            "pat_head".to_string(),
            vec!["eyes:wagging_tail".to_string(), "ears:happy_pant".to_string()],
        );
        world.entities.push(WorldEntity {
            id: "brown_dog".to_string(),
            concept_label: "dog".to_string(),
            symbol: 'd',
            x: 2,
            y: 9,
            visual_traits: vec![
                "floppy_ears".into(),
                "wet_snout".into(),
                "four_legs".into(),
                "wagging_tail".into(),
                "brown_fur".into(),
            ],
            peripheral_traits: vec!["medium_quadruped_silhouette".into()],
            auditory_traits: vec!["bark".into(), "panting".into()],
            tactile_traits: vec!["coarse_fur".into(), "warm_body".into()],
            olfactory_traits: vec!["canine_scent".into()],
            action_effects: dog_fx,
        });

        // 5. Light Switch (top-center)
        let mut sw_fx = FxHashMap::default();
        sw_fx.insert(
            "press_switch".to_string(),
            vec!["eyes:light_on".to_string(), "eyes:room_bright".to_string()],
        );
        world.entities.push(WorldEntity {
            id: "wall_switch".to_string(),
            concept_label: "switch".to_string(),
            symbol: 'S',
            x: 6,
            y: 2,
            visual_traits: vec!["switch_visible".into(), "toggle_lever".into()],
            peripheral_traits: vec!["wall_fixture".into()],
            auditory_traits: vec![],
            tactile_traits: vec!["hard_plastic".into(), "click_detent".into()],
            olfactory_traits: vec![],
            action_effects: sw_fx,
        });

        world
    }

    #[inline]
    pub fn manhattan_dist(x1: i32, y1: i32, x2: i32, y2: i32) -> i32 {
        (x1 - x2).abs() + (y1 - y2).abs()
    }

    /// Moves Alpha 7's eye fixation (saccade) to `(gx, gy)`.
    pub fn saccade_to(&mut self, body: &mut Alpha7Body, gx: i32, gy: i32) {
        self.gaze_x = gx.clamp(0, self.width - 1);
        self.gaze_y = gy.clamp(0, self.height - 1);
        body.eyes.gaze_x = self.gaze_x;
        body.eyes.gaze_y = self.gaze_y;
    }

    /// Moves Alpha 7's body and hands to `(nx, ny)` and aligns eye fixation.
    pub fn move_agent_to(&mut self, body: &mut Alpha7Body, nx: i32, ny: i32) {
        self.agent_x = nx.clamp(0, self.width - 1);
        self.agent_y = ny.clamp(0, self.height - 1);
        self.gaze_x = self.agent_x;
        self.gaze_y = self.agent_y;
        body.hands.hand_x = self.agent_x;
        body.hands.hand_y = self.agent_y;
        body.eyes.gaze_x = self.gaze_x;
        body.eyes.gaze_y = self.gaze_y;
        self.step_count += 1;
    }

    /// Steps Alpha 7 one grid cell toward `(target_x, target_y)`.
    pub fn step_towards(&mut self, body: &mut Alpha7Body, target_x: i32, target_y: i32) {
        let dx = (target_x - self.agent_x).signum();
        let dy = (target_y - self.agent_y).signum();
        let nx = self.agent_x + dx;
        let ny = self.agent_y + dy;
        self.move_agent_to(body, nx, ny);
    }

    /// Samples a complete 5-sense `SensoryFrame` from the 2D Canvas based on Alpha 7's
    /// current body position `(agent_x, agent_y)` and eye gaze `(gaze_x, gaze_y)`.
    pub fn sense_current_frame(
        &self,
        body: &mut Alpha7Body,
        utterance: Option<&str>,
    ) -> SensoryFrame {
        let mut eyes_vec: Vec<&str> = Vec::new();
        let mut ears_vec: Vec<&str> = Vec::new();
        let mut hands_vec: Vec<&str> = Vec::new();
        let mut smell_vec: Vec<&str> = Vec::new();

        for ent in &self.entities {
            let gaze_dist = Self::manhattan_dist(self.gaze_x, self.gaze_y, ent.x, ent.y);
            let body_dist = Self::manhattan_dist(self.agent_x, self.agent_y, ent.x, ent.y);

            // Eyes: Foveal high-detail vision at gaze_dist <= 1; peripheral vision at 2..=4
            if gaze_dist <= 1 {
                for v in &ent.visual_traits {
                    eyes_vec.push(v.as_str());
                }
            } else if gaze_dist <= 4 {
                for pv in &ent.peripheral_traits {
                    eyes_vec.push(pv.as_str());
                }
            }

            // Ears: Heard within distance <= 4 of body
            if body_dist <= 4 {
                for a in &ent.auditory_traits {
                    ears_vec.push(a.as_str());
                }
            }

            // Hands: Felt when adjacent or co-located (body_dist <= 1)
            if body_dist <= 1 {
                for h in &ent.tactile_traits {
                    hands_vec.push(h.as_str());
                }
            }

            // Smell: Olfactory plume detected within distance <= 5 of body
            if body_dist <= 5 {
                for s in &ent.olfactory_traits {
                    smell_vec.push(s.as_str());
                }
            }
        }

        body.build_frame(&eyes_vec, &ears_vec, &hands_vec, &smell_vec, utterance)
    }

    /// Renders an ASCII view of the 2D World Canvas showing Alpha 7 (`@`), eye gaze (`+`),
    /// and all multi-sensory entities.
    pub fn render_ascii(&self) -> String {
        let mut out = String::new();
        out.push_str(&format!(
            "┌{}┐ (Agent '@' at {},{} | Gaze '+' at {},{})\n",
            "─".repeat((self.width * 2) as usize),
            self.agent_x,
            self.agent_y,
            self.gaze_x,
            self.gaze_y
        ));
        for y in 0..self.height {
            out.push('│');
            for x in 0..self.width {
                let ch = if x == self.agent_x && y == self.agent_y {
                    '@'
                } else if x == self.gaze_x && y == self.gaze_y {
                    '+'
                } else if let Some(ent) = self.entities.iter().find(|e| e.x == x && e.y == y) {
                    ent.symbol
                } else {
                    '·'
                };
                out.push(ch);
                out.push(' ');
            }
            out.push_str("│\n");
        }
        out.push_str(&format!("└{}┘", "─".repeat((self.width * 2) as usize)));
        out
    }
}
