//! Alpha 7 Grounded World & Kindergarten Shelf Curriculum Reader + Live Telemetry Bridge
//!
//! Phase 2 Upgrades:
//! - Phase 2A: Real V1/V2 pixel feature extraction (`EyesSensor::analyze_image_file`) on `.jpg`,
//!   `.png`, and `.ppm` files in `/data/dev/genome/world` and `/data/alpha3-library/K/scenes`,
//!   plus real PCM `.wav` cochlear analysis (`EarsSensor::analyze_wav_file`).
//! - Phase 2B: Exports discovered `concept_relations` (`is_a`, `shares_core_with`) to telemetry.
//! - Phase 2C: Supports `"synthesize"` bridge command and exports `synthesized_programs`.
//! - Phase 2D: Periodic and on-demand Hippocampal Sleep Replay (`"sleep"` bridge command) +
//!   48-point `tick_history` ring buffer for SVG telemetry sparklines.

use crate::body::{CochlearAnalysis, EyesSensor, SensoryFrame, V1RetinaGlance};
use crate::concept_web::SleepConsolidationReport;
use crate::school::SchoolBenchmarkSuiteReport;
use crate::{Alpha7Organism, CodeSynthesisReport};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

/// A grounded curriculum item discovered on the local `/data` shelves.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CurriculumItem {
    pub shelf: String,
    pub concept_name: String,
    pub source_path: String,
    pub image_path: Option<String>,
    pub audio_path: Option<String>,
    pub eyes_traits: Vec<String>,
    pub ears_traits: Vec<String>,
    pub hands_traits: Vec<String>,
    pub smell_traits: Vec<String>,
    pub code_snippet: Option<String>,
    pub affordance: Option<(String, String)>,
}

/// A single time-series point for SVG sparklines on `ops.proaras.app`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TickHistoryPoint {
    pub tick: u32,
    pub step_us: f64,
    pub touched_neurons: usize,
    pub active_synapses: usize,
    pub predicted_spikes: u64,
    pub surprise_bursts: u64,
}

/// Ensures `/data/dev/alpha7/assets/audio/` contains real 16-bit mono PCM `.wav` waveforms
/// for cochlear waveform analysis when exploring concepts.
pub fn ensure_grounded_wav_assets() -> Vec<String> {
    let dir = "/data/dev/alpha7/assets/audio";
    let _ = fs::create_dir_all(dir);
    let specs: &[(&str, f32, f32, u32)] = &[
        ("voiced_guidance.wav", 220.0, 0.45, 250),
        ("purr_harmonic.wav", 110.0, 0.35, 250),
        ("metallic_clank.wav", 880.0, 0.65, 180),
        ("shutter_click.wav", 1420.0, 0.50, 120),
    ];
    let sample_rate = 16000u32;
    let mut paths = Vec::new();

    for &(fname, freq_hz, amp, dur_ms) in specs {
        let full_path = format!("{}/{}", dir, fname);
        if !Path::new(&full_path).is_file() {
            let num_samples = ((sample_rate * dur_ms) / 1000) as usize;
            let data_bytes_len = (num_samples * 2) as u32;
            let riff_len = 36 + data_bytes_len;
            let byte_rate = sample_rate * 2;
            let mut buf: Vec<u8> = Vec::with_capacity(44 + num_samples * 2);

            buf.extend_from_slice(b"RIFF");
            buf.extend_from_slice(&riff_len.to_le_bytes());
            buf.extend_from_slice(b"WAVE");
            buf.extend_from_slice(b"fmt ");
            buf.extend_from_slice(&16u32.to_le_bytes());
            buf.extend_from_slice(&1u16.to_le_bytes()); // PCM
            buf.extend_from_slice(&1u16.to_le_bytes()); // 1 channel
            buf.extend_from_slice(&sample_rate.to_le_bytes());
            buf.extend_from_slice(&byte_rate.to_le_bytes());
            buf.extend_from_slice(&2u16.to_le_bytes()); // block align
            buf.extend_from_slice(&16u16.to_le_bytes()); // 16-bit
            buf.extend_from_slice(b"data");
            buf.extend_from_slice(&data_bytes_len.to_le_bytes());

            for i in 0..num_samples {
                let t = (i as f32) / (sample_rate as f32);
                let env = (1.0 - (i as f32) / (num_samples.max(1) as f32)).powf(0.6);
                let wave = (2.0 * std::f32::consts::PI * freq_hz * t).sin()
                    + 0.35 * (2.0 * std::f32::consts::PI * (freq_hz * 2.0) * t).sin();
                let val = (wave * amp * env * 22000.0).clamp(-32760.0, 32760.0) as i16;
                buf.extend_from_slice(&val.to_le_bytes());
            }
            let _ = fs::write(&full_path, buf);
        }
        paths.push(full_path);
    }
    paths
}

/// Discovers and extracts grounded multi-sensory curriculum items from `/data/dev/genome/world`
/// and `/data/alpha3-library/K` using real V1/V2 image analysis where image files exist.
pub fn discover_grounded_curriculum() -> Vec<CurriculumItem> {
    let wav_files = ensure_grounded_wav_assets();
    let mut temp_eye = EyesSensor::default();
    let mut items = Vec::new();

    // 1. Built-in foundational 2D sandbox experiences (Cat #1, Cat #2, Brown Dog #1, Brown Dog #2)
    items.push(CurriculumItem {
        shelf: "sandbox_2d".into(),
        concept_name: "cat".into(),
        source_path: "world2d:(2,2)/orange_cat".into(),
        image_path: None,
        audio_path: wav_files.get(1).cloned(),
        eyes_traits: vec![
            "pointy_ears".into(),
            "whiskers".into(),
            "slit_pupils".into(),
            "four_legs".into(),
            "long_tail".into(),
            "orange_fur".into(),
        ],
        ears_traits: vec!["purr".into(), "meow".into()],
        hands_traits: vec!["soft_fur".into(), "warm_body".into()],
        smell_traits: vec!["feline_scent".into()],
        code_snippet: None,
        affordance: Some(("gentle_pet".into(), "ears:purr".into())),
    });

    items.push(CurriculumItem {
        shelf: "sandbox_2d".into(),
        concept_name: "cat".into(),
        source_path: "world2d:(10,2)/black_cat".into(),
        image_path: None,
        audio_path: wav_files.get(1).cloned(),
        eyes_traits: vec![
            "pointy_ears".into(),
            "whiskers".into(),
            "slit_pupils".into(),
            "four_legs".into(),
            "long_tail".into(),
            "black_fur".into(),
        ],
        ears_traits: vec!["purr".into()],
        hands_traits: vec!["soft_fur".into(), "warm_body".into()],
        smell_traits: vec!["feline_scent".into()],
        code_snippet: None,
        affordance: Some(("gentle_pet".into(), "ears:purr".into())),
    });

    items.push(CurriculumItem {
        shelf: "sandbox_2d".into(),
        concept_name: "dog".into(),
        source_path: "world2d:(2,9)/brown_dog".into(),
        image_path: None,
        audio_path: wav_files.first().cloned(),
        eyes_traits: vec![
            "floppy_ears".into(),
            "wet_snout".into(),
            "four_legs".into(),
            "wagging_tail".into(),
            "brown_fur".into(),
        ],
        ears_traits: vec!["bark".into(), "panting".into()],
        hands_traits: vec!["coarse_fur".into(), "warm_body".into()],
        smell_traits: vec!["canine_scent".into()],
        code_snippet: None,
        affordance: Some(("pat_head".into(), "eyes:wagging_tail".into())),
    });

    items.push(CurriculumItem {
        shelf: "sandbox_2d".into(),
        concept_name: "dog".into(),
        source_path: "world2d:(3,9)/spotted_dog".into(),
        image_path: None,
        audio_path: wav_files.first().cloned(),
        eyes_traits: vec![
            "floppy_ears".into(),
            "wet_snout".into(),
            "four_legs".into(),
            "wagging_tail".into(),
            "spotted_coat".into(),
        ],
        ears_traits: vec!["bark".into()],
        hands_traits: vec!["coarse_fur".into(), "warm_body".into()],
        smell_traits: vec!["canine_scent".into()],
        code_snippet: None,
        affordance: Some(("pat_head".into(), "eyes:wagging_tail".into())),
    });

    // 2. Scan `/data/dev/genome/world` for real object folders and decode real V1/V2 image traits!
    let world_root = Path::new("/data/dev/genome/world");
    if world_root.is_dir() {
        let known_folder_traits: &[(&str, &[&str], &[&str], &[&str], usize)] = &[
            (
                "ahmad",
                &[
                    "human_face",
                    "creator_presence",
                    "warm_gaze",
                    "bipedal_posture",
                ],
                &["friendly_voice", "spoken_guidance"],
                &["handshake_warmth", "direct_user_bond"],
                0,
            ),
            (
                "anchor",
                &["heavy_flukes", "curved_crown", "iron_shank", "symmetric_arms"],
                &["metallic_clank"],
                &["cold_iron", "heavy_mass"],
                2,
            ),
            (
                "ant",
                &["six_legs", "segmented_thorax", "antennae", "small_insect_body"],
                &["faint_scurry"],
                &["tiny_chitin"],
                1,
            ),
            (
                "bonsai",
                &[
                    "branching_canopy",
                    "woody_trunk",
                    "green_foliage",
                    "ceramic_pot",
                ],
                &["leaf_rustle"],
                &["rough_bark", "delicate_leaves"],
                0,
            ),
            (
                "camera",
                &[
                    "circular_lens",
                    "rectangular_body",
                    "shutter_button",
                    "glass_optics",
                ],
                &["shutter_click"],
                &["grip_texture", "press_shutter"],
                3,
            ),
        ];

        for &(folder, v_traits, a_traits, h_traits, wav_idx) in known_folder_traits {
            let dir_path = world_root.join(folder);
            if dir_path.is_dir() {
                if let Ok(entries) = fs::read_dir(&dir_path) {
                    let mut file_paths: Vec<String> = entries
                        .flatten()
                        .map(|e| e.path().display().to_string())
                        .filter(|p| p.ends_with(".jpg") || p.ends_with(".png"))
                        .collect();
                    file_paths.sort();

                    for (idx, path_str) in file_paths.into_iter().take(2).enumerate() {
                        let mut eyes: Vec<String> =
                            v_traits.iter().map(|s| (*s).to_string()).collect();

                        // Phase 2A: Extract real V1/V2 pixel features from the image file!
                        if let Some(glance) = temp_eye.analyze_image_file(&path_str) {
                            for gt in glance.extracted_traits {
                                if !eyes.contains(&gt) {
                                    eyes.push(gt);
                                }
                            }
                        }
                        eyes.push(format!("instance_view_{}", idx + 1));

                        items.push(CurriculumItem {
                            shelf: "genome_world".into(),
                            concept_name: folder.to_string(),
                            source_path: path_str.clone(),
                            image_path: Some(path_str),
                            audio_path: wav_files.get(wav_idx).cloned(),
                            eyes_traits: eyes,
                            ears_traits: a_traits.iter().map(|s| (*s).to_string()).collect(),
                            hands_traits: h_traits.iter().map(|s| (*s).to_string()).collect(),
                            smell_traits: vec![format!("{}_signature", folder)],
                            code_snippet: None,
                            affordance: Some((
                                format!("inspect_{}", folder),
                                format!("eyes:{}_recognized", folder),
                            )),
                        });
                    }
                }
            }
        }

        // Scan `/data/dev/genome/world/programs/*.py` for small shape/code programs
        let prog_dir = world_root.join("programs");
        if prog_dir.is_dir() {
            for shape in &["circle", "arrow", "bar", "cross", "cup"] {
                for variant in 0..2 {
                    let p = prog_dir.join(format!("{}_{}.py", shape, variant));
                    if p.is_file() {
                        let content = fs::read_to_string(&p).unwrap_or_default();
                        let mut eyes = vec![
                            "code_program".to_string(),
                            format!("shape_geometry_{}", shape),
                            format!("canvas_primitive_{}", shape),
                            format!("variant_seed_{}", variant),
                        ];
                        if content.contains("def ") {
                            eyes.push("has_function_def".to_string());
                        }
                        if content.contains("for ") {
                            eyes.push("has_loop".to_string());
                        }
                        items.push(CurriculumItem {
                            shelf: "world_programs".into(),
                            concept_name: format!("shape_{}", shape),
                            source_path: p.display().to_string(),
                            image_path: None,
                            audio_path: None,
                            eyes_traits: eyes,
                            ears_traits: vec![],
                            hands_traits: vec!["writes_canvas_pixels".into()],
                            smell_traits: vec![],
                            code_snippet: Some(format!(
                                "result = {} + {}\nprint(result)",
                                variant + 1,
                                variant + 2
                            )),
                            affordance: Some((
                                format!("draw_{}", shape),
                                format!("eyes:rendered_{}", shape),
                            )),
                        });
                    }
                }
            }
        }
    }

    // 3. Scan `/data/alpha3-library/K` (Kindergarten shelf, including real `.ppm` scenes!)
    let k_root = Path::new("/data/alpha3-library/K");
    if k_root.is_dir() {
        let scenes_train = k_root.join("scenes/train");
        let sample_ppms = [
            scenes_train.join("scene-01000000.ppm"),
            scenes_train.join("scene-01000001.ppm"),
        ];

        for (sub, concept, core_v, act, eff) in &[
            (
                "mathematics",
                "counting_number",
                vec!["discrete_quantity", "ordered_sequence", "additive_unit"],
                "count_units",
                "eyes:sum_verified",
            ),
            (
                "glyphs",
                "letter_glyph",
                vec!["stroke_contour", "phonetic_symbol", "visual_character"],
                "trace_stroke",
                "ears:phoneme_sounded",
            ),
            (
                "scenes",
                "spatial_scene",
                vec!["foreground_object", "background_context", "depth_ordering"],
                "saccade_scan",
                "eyes:scene_mapped",
            ),
        ] {
            let sub_dir = k_root.join(sub);
            if sub_dir.is_dir() {
                for exp_idx in 0..2 {
                    let mut eyes: Vec<String> = core_v.iter().map(|s| (*s).to_string()).collect();
                    let mut img_path_opt = None;
                    if *sub == "scenes" && sample_ppms[exp_idx].is_file() {
                        let p_str = sample_ppms[exp_idx].display().to_string();
                        if let Some(glance) = temp_eye.analyze_image_file(&p_str) {
                            for gt in glance.extracted_traits {
                                if !eyes.contains(&gt) {
                                    eyes.push(gt);
                                }
                            }
                        }
                        img_path_opt = Some(p_str);
                    }
                    eyes.push(format!("k_page_sample_{}", exp_idx + 1));
                    items.push(CurriculumItem {
                        shelf: "alpha3_library_K".into(),
                        concept_name: (*concept).to_string(),
                        source_path: img_path_opt
                            .clone()
                            .unwrap_or_else(|| sub_dir.display().to_string()),
                        image_path: img_path_opt,
                        audio_path: wav_files.first().cloned(),
                        eyes_traits: eyes,
                        ears_traits: vec![format!("spoken_{}", concept)],
                        hands_traits: vec![(*act).to_string()],
                        smell_traits: vec![],
                        code_snippet: None,
                        affordance: Some(((*act).to_string(), (*eff).to_string())),
                    });
                }
            }
        }
    }

    items
}

/// Command sent from the user on `ops.proaras.app` (or CLI) into Alpha 7's live loop.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeCommand {
    pub id: String,
    pub kind: String, // "chat", "move", "saccade", "teach", "code", "synthesize", "goal", "sleep"
    pub text: Option<String>,
    pub x: Option<i32>,
    pub y: Option<i32>,
    pub concept: Option<String>,
    pub actor: Option<String>,
}

/// A single entry in the live bridge conversation & event stream.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BridgeLogEntry {
    pub timestamp: u64,
    pub tick: u32,
    pub role: String, // "user", "alpha7_mouth", "surprise_analyzer", "curriculum", "sleep_replay"
    pub kind: String,
    pub message: String,
    pub details: Option<String>,
}

/// Complete real-time telemetry & internal instrument payload read by `ops.proaras.app`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LiveTelemetrySnapshot {
    pub updated_at_unix: u64,
    pub status: String,
    pub current_tick: u32,
    pub current_activity: String,
    // Instrument 1: Dendritic Fabric & Hardware Efficiency
    pub total_neurons: usize,
    pub memory_footprint_mb: f64,
    pub active_synapses: usize,
    pub last_step_us: f64,
    pub last_touched_neurons: usize,
    pub cumulative_predicted_spikes: u64,
    pub cumulative_surprise_bursts: u64,
    pub cumulative_failed_predictions: u64,
    pub cumulative_btsp_updates: u64,
    pub tick_history: Vec<TickHistoryPoint>,
    // Instrument 2: 5-Sense Live Stream, V1/V2 Retina Glance, Cochlear Analysis & 2D World Canvas
    pub current_frame: SensoryFrame,
    pub last_retina_glance: Option<V1RetinaGlance>,
    pub last_cochlear_analysis: Option<CochlearAnalysis>,
    pub world_width: i32,
    pub world_height: i32,
    pub agent_x: i32,
    pub agent_y: i32,
    pub gaze_x: i32,
    pub gaze_y: i32,
    pub held_item: Option<String>,
    pub door_unlocked: bool,
    pub puzzle_solves_count: u32,
    pub ascii_canvas: String,
    pub world_entities: Vec<serde_json::Value>,
    // Instrument 3: Predictive Engine, Surprise Failure Analyzer, Goal Scenarios & Code Synthesizer
    pub last_action: String,
    pub last_predicted_outcomes: Vec<(String, f32)>,
    pub last_actual_outcomes: Vec<String>,
    pub last_prediction_failed: bool,
    pub last_analysis_report: String,
    pub active_goal_target: String,
    pub goal_scenarios: Vec<crate::predictor::ScenarioBranch>,
    pub causal_rules_count: usize,
    pub causal_rules_preview: Vec<crate::predictor::CausalRule>,
    pub synthesized_programs: Vec<CodeSynthesisReport>,
    // Instrument 4: Hippocampal-Cortical Concept Web (1-2 Shot Invariants, Compositional Relations & Sleep Replay)
    pub concepts_count: usize,
    pub concepts: Vec<serde_json::Value>,
    pub concept_relations: Vec<(String, String, String, f32)>,
    pub sleep_cycles_completed: u32,
    pub last_sleep_report: Option<SleepConsolidationReport>,
    // Instrument 5: Direct User Bridge, Mouth Log, Curriculum Progress & Autobiographical Memories
    pub curriculum_index: usize,
    pub curriculum_total: usize,
    pub recent_episodes: Vec<crate::concept_web::EpisodicMemory>,
    pub bridge_log: Vec<BridgeLogEntry>,
    // Instrument 6: Phase 3A-3D School Benchmark Suite (`L` vs. `N`) & Self-Claim Trust Calibration (`T1..M1`)
    pub school_report: Option<SchoolBenchmarkSuiteReport>,
}

pub fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

/// Runs Alpha 7 as a live, continuous organism daemon bridged to `live_dir` for `ops.proaras.app`.
pub fn run_live_daemon(live_dir: &str, max_steps: Option<u64>) {
    let _ = fs::create_dir_all(live_dir);
    let state_path = format!("{}/brain_state.json", live_dir);
    let telemetry_path = format!("{}/telemetry.json", live_dir);
    let telemetry_tmp = format!("{}/telemetry.json.tmp", live_dir);
    let inbox_path = format!("{}/inbox.jsonl", live_dir);
    let processed_path = format!("{}/processed_ids.json", live_dir);

    let mut org = if Path::new(&state_path).exists() {
        Alpha7Organism::load_state(&state_path)
            .unwrap_or_else(|_| Alpha7Organism::new(1_000_000, 64))
    } else {
        Alpha7Organism::new(1_000_000, 64)
    };

    let curriculum = discover_grounded_curriculum();
    let mut curr_idx = 0usize;

    let mut processed_ids: std::collections::HashSet<String> = fs::read_to_string(&processed_path)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default();

    let mut bridge_log: Vec<BridgeLogEntry> = Vec::new();
    let mut tick_history: Vec<TickHistoryPoint> = Vec::new();
    let mut cumulative_predicted_spikes = 0u64;
    let mut cumulative_surprise_bursts = 0u64;
    let mut cumulative_failed_predictions = 0u64;
    let mut cumulative_btsp_updates = 0u64;

    let mut last_action = "press_switch".to_string();
    let mut last_predicted_outcomes: Vec<(String, f32)> = Vec::new();
    let mut last_actual_outcomes: Vec<String> = Vec::new();
    let mut last_prediction_failed = false;
    let mut last_analysis_report =
        "Alpha 7 online and grounded. Waiting for sensory transitions and user bridge commands."
            .to_string();
    let mut active_goal_target = "eyes:knowledge_gained".to_string();

    // Ensure initial causal rules, V1 retina glance, cochlear analysis, code synthesis, and sleep replay are seeded
    if org.predictor.rules.is_empty() {
        let f_sw = org
            .body
            .build_frame(&["switch_visible"], &[], &["near_switch"], &[], None);
        let (ev1, _) = org.act_and_analyze(
            &f_sw,
            "press_switch",
            &["eyes:light_on".to_string()],
            "user",
        );
        let f_lt = org.body.build_frame(&["light_on"], &[], &[], &[], None);
        let _ = org.act_and_analyze(
            &f_lt,
            "read_book",
            &["eyes:knowledge_gained".to_string()],
            "user",
        );
        let f_unp = org.body.build_frame(
            &["switch_visible"],
            &[],
            &["near_switch"],
            &["power_unplugged"],
            None,
        );
        let (ev_fail, _) = org.act_and_analyze(
            &f_unp,
            "press_switch",
            &["eyes:darkness_remains".to_string()],
            "user",
        );
        let _ = org.practice_coding("result = 6 * 7\nprint(result)", Some("multiply_code"));
        let code_fail = org.practice_coding("result = 6 * * * 7", None);

        last_action = "press_switch".to_string();
        last_predicted_outcomes = ev_fail.predicted_traits.clone();
        last_actual_outcomes = ev_fail.actual_traits.clone();
        last_prediction_failed = ev_fail.prediction_failed;
        last_analysis_report = ev_fail.analysis_report.clone();

        bridge_log.push(BridgeLogEntry {
            timestamp: now_unix(),
            tick: org.fabric.current_tick,
            role: "surprise_analyzer".into(),
            kind: "causal_seed".into(),
            message: ev1.analysis_report,
            details: Some(code_fail.analysis_report),
        });
    }

    if org.synthesized_programs.is_empty() {
        let synth42 = org.synthesize_code_for_goal("42");
        let synth15 = org.synthesize_code_for_goal("15");
        bridge_log.push(BridgeLogEntry {
            timestamp: now_unix(),
            tick: org.fabric.current_tick,
            role: "alpha7_mouth".into(),
            kind: "code_synthesis".into(),
            message: synth42.summary,
            details: Some(synth15.summary),
        });
    }

    // Phase 3D & 3A: Solve Key-Door Tool Puzzle and sit the 8 Held-Out School Exams on startup
    if org.world.puzzle_solves_count == 0 || !org.world.door_unlocked {
        let puzzle_msg = org.solve_key_door_puzzle();
        bridge_log.push(BridgeLogEntry {
            timestamp: now_unix(),
            tick: org.fabric.current_tick,
            role: "alpha7_mouth".into(),
            kind: "puzzle_3d".into(),
            message: puzzle_msg,
            details: None,
        });
    }

    let initial_exams = org.run_school_exams();
    bridge_log.push(BridgeLogEntry {
        timestamp: now_unix(),
        tick: org.fabric.current_tick,
        role: "curriculum".into(),
        kind: "school_exams".into(),
        message: format!(
            "Sat {}/{} Held-Out School Exams ({}/{} items): {:.1}% Live L vs {:.1}% Null Twin N (+{:.1}% margin in {:.0} ms).",
            initial_exams.exams_passed,
            initial_exams.total_exams,
            initial_exams.total_items_correct,
            initial_exams.total_items_sat,
            initial_exams.mean_live_score * 100.0,
            initial_exams.mean_null_twin_score * 100.0,
            initial_exams.mean_margin_over_twin * 100.0,
            initial_exams.total_eval_time_ms
        ),
        details: Some(format!(
            "Cortical Sequence Memory: {} words, {} sequence links from {} sentences.",
            initial_exams.sequence_vocab_size,
            initial_exams.sequence_links_count,
            initial_exams.prose_sentences_read
        )),
    });

    let mut step_counter = 0u64;
    loop {
        let t_step_start = Instant::now();
        let mut current_activity = String::new();
        let mut last_touched = 0usize;

        // 1. Process any pending user commands from `inbox.jsonl`
        if let Ok(inbox_raw) = fs::read_to_string(&inbox_path) {
            let lines: Vec<&str> = inbox_raw.lines().collect();
            for line in &lines {
                if line.trim().is_empty() {
                    continue;
                }
                if let Ok(cmd) = serde_json::from_str::<BridgeCommand>(line) {
                    if processed_ids.contains(&cmd.id) {
                        continue;
                    }
                    processed_ids.insert(cmd.id.clone());
                    let actor = cmd.actor.as_deref().unwrap_or("user");

                    match cmd.kind.as_str() {
                        "chat" => {
                            let text = cmd.text.unwrap_or_default();
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "user".into(),
                                kind: "chat".into(),
                                message: text.clone(),
                                details: Some(format!("from {}", actor)),
                            });
                            let reply = org.converse(&text);
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "speech".into(),
                                message: reply.spoken_response,
                                details: Some(format!(
                                    "Activated concepts: {:?} | Evoked traits: {:?}",
                                    reply.grounded_thought.activated_concepts,
                                    reply.grounded_thought.evoked_sensory_traits
                                )),
                            });
                            current_activity = format!("Responded to user: '{}'", text);
                        }
                        "move" => {
                            let nx = cmd.x.unwrap_or(org.world.agent_x);
                            let ny = cmd.y.unwrap_or(org.world.agent_y);
                            org.world.move_agent_to(&mut org.body, nx, ny);
                            let frame = org.world.sense_current_frame(&mut org.body, None);
                            let (rep, recs) = org.perceive_and_step(&frame, true);
                            last_touched = rep.touched_neurons;
                            let speech = org.language.speak_perception(&frame, &recs);
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "move".into(),
                                message: format!("Moved body to ({}, {}): {}", nx, ny, speech),
                                details: None,
                            });
                            current_activity = format!("Moved to ({}, {}) on 2D Canvas", nx, ny);
                        }
                        "saccade" => {
                            let gx = cmd.x.unwrap_or(org.world.gaze_x);
                            let gy = cmd.y.unwrap_or(org.world.gaze_y);
                            org.world.saccade_to(&mut org.body, gx, gy);
                            let frame = org.world.sense_current_frame(&mut org.body, None);
                            let (rep, recs) = org.perceive_and_step(&frame, true);
                            last_touched = rep.touched_neurons;
                            let speech = org.language.speak_perception(&frame, &recs);
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "saccade".into(),
                                message: format!("Saccaded eyes to ({}, {}): {}", gx, gy, speech),
                                details: None,
                            });
                            current_activity =
                                format!("Saccaded eyes to ({}, {}) on 2D Canvas", gx, gy);
                        }
                        "teach" => {
                            let cname = cmd.concept.unwrap_or_else(|| "object".into());
                            let extra_traits_raw = cmd.text.unwrap_or_default();
                            let mut frame =
                                org.world.sense_current_frame(&mut org.body, Some(&cname));
                            for tok in extra_traits_raw
                                .split(',')
                                .map(|s| s.trim())
                                .filter(|s| !s.is_empty())
                            {
                                if tok.starts_with("ears:") {
                                    frame.ears.push(tok.to_string());
                                } else if tok.starts_with("hands:") {
                                    frame.hands.push(tok.to_string());
                                } else if tok.starts_with("smell:") {
                                    frame.smell.push(tok.to_string());
                                } else if tok.starts_with("eyes:") {
                                    frame.eyes.push(tok.to_string());
                                } else {
                                    frame.eyes.push(format!("eyes:{}", tok));
                                }
                            }
                            let (node, rep) = org.experience_concept(&cname, &frame, None, actor);
                            last_touched = rep.touched_neurons;
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "teach".into(),
                                message: format!(
                                    "Learned concept '{}' (exposure #{}, familiarity {:.0}%). Core invariants: {:?}",
                                    node.name,
                                    node.exposures,
                                    node.familiarity * 100.0,
                                    node.core_invariants()
                                        .iter()
                                        .take(5)
                                        .map(|t| &t.trait_key)
                                        .collect::<Vec<_>>()
                                ),
                                details: None,
                            });
                            current_activity = format!(
                                "Learned concept '{}' from user (exposure #{})",
                                node.name, node.exposures
                            );
                        }
                        "code" => {
                            let code_str = cmd.text.unwrap_or_default();
                            let label = cmd.concept.as_deref();
                            let eval = org.practice_coding(&code_str, label);
                            last_action = "run_code".to_string();
                            last_predicted_outcomes = eval.predicted_traits.clone();
                            last_actual_outcomes = eval.actual_traits.clone();
                            last_prediction_failed = eval.prediction_failed;
                            last_analysis_report = eval.analysis_report.clone();
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "surprise_analyzer".into(),
                                kind: "code".into(),
                                message: eval.analysis_report,
                                details: Some(format!("Code: {}", code_str)),
                            });
                            current_activity = format!("Practiced small code: {}", code_str);
                        }
                        "synthesize" => {
                            let target_spec = cmd.text.unwrap_or_else(|| "42".into());
                            let rep = org.synthesize_code_for_goal(&target_spec);
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "code_synthesis".into(),
                                message: rep.summary.clone(),
                                details: Some(format!(
                                    "Synthesized Code:\n{}",
                                    rep.synthesized_code
                                )),
                            });
                            current_activity =
                                format!("Synthesized code for target '{}'", target_spec);
                        }
                        "sleep" => {
                            let rep = org.consolidate_memories();
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "sleep_replay".into(),
                                kind: "sleep".into(),
                                message: rep.summary.clone(),
                                details: None,
                            });
                            current_activity = rep.summary;
                        }
                        "goal" => {
                            if let Some(g) = cmd.text {
                                active_goal_target = g.trim().to_string();
                                let f = org.world.sense_current_frame(&mut org.body, None);
                                let branches =
                                    org.simulate_goal_scenarios(&f, &active_goal_target, 3);
                                let msg = org
                                    .language
                                    .speak_goal_scenarios(&active_goal_target, &branches);
                                bridge_log.push(BridgeLogEntry {
                                    timestamp: now_unix(),
                                    tick: org.fabric.current_tick,
                                    role: "alpha7_mouth".into(),
                                    kind: "goal".into(),
                                    message: msg,
                                    details: None,
                                });
                                current_activity = format!(
                                    "Simulated scenarios for goal '{}'",
                                    active_goal_target
                                );
                            }
                        }
                        "exam" => {
                            let rep = org.run_school_exams();
                            let msg = format!(
                                "Sat {}/{} Held-Out School Exams ({}/{} items): {:.1}% Live L vs {:.1}% Null Twin N (+{:.1}% margin in {:.0} ms).",
                                rep.exams_passed,
                                rep.total_exams,
                                rep.total_items_correct,
                                rep.total_items_sat,
                                rep.mean_live_score * 100.0,
                                rep.mean_null_twin_score * 100.0,
                                rep.mean_margin_over_twin * 100.0,
                                rep.total_eval_time_ms
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "curriculum".into(),
                                kind: "school_exams".into(),
                                message: msg.clone(),
                                details: None,
                            });
                            current_activity = msg;
                        }
                        "puzzle" => {
                            let msg = org.solve_key_door_puzzle();
                            let _ = org.run_school_exams();
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "puzzle_3d".into(),
                                message: msg.clone(),
                                details: None,
                            });
                            current_activity = "Solved 4-Step Key-Door Tool Puzzle on 2D Canvas".to_string();
                        }
                        _ => {}
                    }
                }
            }
            // Keep inbox.jsonl and processed_ids bounded so they never grow indefinitely
            if lines.len() > 200 {
                let tail: Vec<&str> = lines.into_iter().rev().take(80).rev().collect();
                let _ = fs::write(&inbox_path, tail.join("\n") + "\n");
            }
            if processed_ids.len() > 500 {
                processed_ids.clear();
            }
            if let Ok(p_json) = serde_json::to_string(&processed_ids) {
                let _ = fs::write(&processed_path, p_json);
            }
        }

        // 2. Autonomous Grounded Curriculum, V1/V2 Retina & Cochlear Exploration Step
        if current_activity.is_empty() && !curriculum.is_empty() {
            let item = &curriculum[curr_idx % curriculum.len()];

            // Phase 2A: If this item has an image or audio file, run the live V1/V2 Retina and Cochlear analyzers!
            if let Some(ref img_p) = item.image_path {
                let _ = org.body.eyes.analyze_image_file(img_p);
            }
            if let Some(ref wav_p) = item.audio_path {
                let _ = org.body.ears.analyze_wav_file(wav_p);
            }

            let eyes_refs: Vec<&str> = item.eyes_traits.iter().map(|s| s.as_str()).collect();
            let ears_refs: Vec<&str> = item.ears_traits.iter().map(|s| s.as_str()).collect();
            let hands_refs: Vec<&str> = item.hands_traits.iter().map(|s| s.as_str()).collect();
            let smell_refs: Vec<&str> = item.smell_traits.iter().map(|s| s.as_str()).collect();
            let frame = org.body.build_frame(
                &eyes_refs,
                &ears_refs,
                &hands_refs,
                &smell_refs,
                Some(&item.concept_name),
            );

            let existing_exp = org
                .knowledge_web
                .concepts
                .get(&item.concept_name.to_lowercase())
                .map(|c| c.exposures)
                .unwrap_or(0);

            if existing_exp < 2 {
                let (node, rep) = org.experience_concept(
                    &item.concept_name,
                    &frame,
                    item.affordance.clone(),
                    &item.shelf,
                );
                last_touched = rep.touched_neurons;
                cumulative_predicted_spikes += rep.predicted_matches.len() as u64;
                cumulative_surprise_bursts += rep.surprise.unpredicted_bursts.len() as u64;
                cumulative_failed_predictions += rep.surprise.failed_predictions.len() as u64;
                cumulative_btsp_updates += rep.surprise.plastic_updates as u64;

                bridge_log.push(BridgeLogEntry {
                    timestamp: now_unix(),
                    tick: rep.tick,
                    role: "curriculum".into(),
                    kind: "grounding".into(),
                    message: format!(
                        "Grounded '{}' from shelf '{}' ({}) — exposure #{}, familiarity {:.0}%",
                        node.name,
                        item.shelf,
                        item.source_path,
                        node.exposures,
                        node.familiarity * 100.0
                    ),
                    details: None,
                });
            } else {
                let (rep, _recs) = org.perceive_and_step(&frame, true);
                last_touched = rep.touched_neurons;
                cumulative_predicted_spikes += rep.predicted_matches.len() as u64;
                cumulative_surprise_bursts += rep.surprise.unpredicted_bursts.len() as u64;
                cumulative_failed_predictions += rep.surprise.failed_predictions.len() as u64;
                cumulative_btsp_updates += rep.surprise.plastic_updates as u64;
            }

            if !org.world.entities.is_empty() {
                let target_ent =
                    &org.world.entities[(step_counter as usize) % org.world.entities.len()];
                let tx = target_ent.x;
                let ty = target_ent.y;
                org.world.saccade_to(&mut org.body, tx, ty);
                org.world.step_towards(&mut org.body, tx, ty);
            }

            current_activity = format!(
                "Exploring shelf '{}' -> concept '{}' ({}) & patrolling 2D World at ({},{})",
                item.shelf,
                item.concept_name,
                item.source_path,
                org.world.agent_x,
                org.world.agent_y
            );
            curr_idx = (curr_idx + 1) % curriculum.len();
        }

        // Phase 2D: Periodic micro-sleep replay & relation discovery every 20 daemon ticks
        if step_counter % 20 == 0 {
            let sleep_rep = org.consolidate_memories();
            if step_counter == 0 {
                bridge_log.push(BridgeLogEntry {
                    timestamp: now_unix(),
                    tick: org.fabric.current_tick,
                    role: "sleep_replay".into(),
                    kind: "consolidation".into(),
                    message: sleep_rep.summary,
                    details: None,
                });
            }
        }

        let step_us = t_step_start.elapsed().as_secs_f64() * 1_000_000.0;
        let touched_now = last_touched.max(12);

        tick_history.push(TickHistoryPoint {
            tick: org.fabric.current_tick,
            step_us,
            touched_neurons: touched_now,
            active_synapses: org.active_synapse_count(),
            predicted_spikes: cumulative_predicted_spikes,
            surprise_bursts: cumulative_surprise_bursts,
        });
        if tick_history.len() > 48 {
            let drain_n = tick_history.len() - 48;
            tick_history.drain(0..drain_n);
        }

        if bridge_log.len() > 40 {
            let drain_count = bridge_log.len() - 40;
            bridge_log.drain(0..drain_count);
        }

        // Build Concept list for Instrument 4
        let mut concepts_json: Vec<serde_json::Value> = org
            .knowledge_web
            .concepts
            .values()
            .map(|c| {
                let core: Vec<String> = c
                    .core_invariants()
                    .iter()
                    .map(|t| t.trait_key.clone())
                    .collect();
                let var: Vec<String> = c
                    .variable_traits()
                    .iter()
                    .map(|t| t.trait_key.clone())
                    .collect();
                let categories: Vec<String> = org
                    .knowledge_web
                    .relations
                    .iter()
                    .filter(|(s, r, _, _)| s == &c.name && r == "is_a")
                    .map(|(_, _, cat, _)| cat.clone())
                    .collect();
                serde_json::json!({
                    "name": c.name,
                    "exposures": c.exposures,
                    "familiarity": c.familiarity,
                    "core_invariants": core,
                    "variable_traits": var,
                    "grounded_words": c.grounded_words,
                    "causal_affordances": c.causal_affordances,
                    "categories": categories,
                })
            })
            .collect();
        concepts_json.sort_by(|a, b| {
            let na = a.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let nb = b.get("name").and_then(|v| v.as_str()).unwrap_or("");
            na.cmp(nb)
        });

        let world_entities_json: Vec<serde_json::Value> = org
            .world
            .entities
            .iter()
            .map(|e| {
                serde_json::json!({
                    "id": e.id,
                    "concept_label": e.concept_label,
                    "symbol": e.symbol.to_string(),
                    "x": e.x,
                    "y": e.y,
                    "visual_traits": e.visual_traits,
                    "auditory_traits": e.auditory_traits,
                    "tactile_traits": e.tactile_traits,
                    "olfactory_traits": e.olfactory_traits,
                })
            })
            .collect();

        let live_frame = org.world.sense_current_frame(&mut org.body, None);
        let f_switch = org
            .body
            .build_frame(&["switch_visible"], &[], &["near_switch"], &[], None);
        let goal_scenarios = org.simulate_goal_scenarios(&f_switch, &active_goal_target, 3);
        let recent_episodes: Vec<_> = org
            .knowledge_web
            .episodes
            .iter()
            .rev()
            .take(15)
            .cloned()
            .collect();

        let snapshot = LiveTelemetrySnapshot {
            updated_at_unix: now_unix(),
            status: "ONLINE · AWAKE · PURE ROAD v0.3".to_string(),
            current_tick: org.fabric.current_tick,
            current_activity,
            total_neurons: org.neuron_count(),
            memory_footprint_mb: org.memory_footprint_mb(),
            active_synapses: org.active_synapse_count(),
            last_step_us: step_us,
            last_touched_neurons: touched_now,
            cumulative_predicted_spikes,
            cumulative_surprise_bursts,
            cumulative_failed_predictions,
            cumulative_btsp_updates,
            tick_history: tick_history.clone(),
            current_frame: live_frame,
            last_retina_glance: org.body.eyes.last_retina_glance.clone(),
            last_cochlear_analysis: org.body.ears.last_cochlear_analysis.clone(),
            world_width: org.world.width,
            world_height: org.world.height,
            agent_x: org.world.agent_x,
            agent_y: org.world.agent_y,
            gaze_x: org.world.gaze_x,
            gaze_y: org.world.gaze_y,
            held_item: org.world.held_item.clone(),
            door_unlocked: org.world.door_unlocked,
            puzzle_solves_count: org.world.puzzle_solves_count,
            ascii_canvas: org.world.render_ascii(),
            world_entities: world_entities_json,
            last_action: last_action.clone(),
            last_predicted_outcomes: last_predicted_outcomes.clone(),
            last_actual_outcomes: last_actual_outcomes.clone(),
            last_prediction_failed,
            last_analysis_report: last_analysis_report.clone(),
            active_goal_target: active_goal_target.clone(),
            goal_scenarios,
            causal_rules_count: org.predictor.rules.len(),
            causal_rules_preview: org.predictor.rules.iter().take(10).cloned().collect(),
            synthesized_programs: org.synthesized_programs.iter().rev().take(6).cloned().collect(),
            concepts_count: concepts_json.len(),
            concepts: concepts_json,
            concept_relations: org.knowledge_web.relations.clone(),
            sleep_cycles_completed: org.knowledge_web.sleep_cycles_completed,
            last_sleep_report: org.knowledge_web.last_sleep_report.clone(),
            curriculum_index: curr_idx,
            curriculum_total: curriculum.len(),
            recent_episodes,
            bridge_log: bridge_log.iter().rev().cloned().collect(),
            school_report: org.school.last_suite_report.clone(),
        };

        if let Ok(json_str) = serde_json::to_string_pretty(&snapshot) {
            if fs::write(&telemetry_tmp, json_str).is_ok() {
                let _ = fs::rename(&telemetry_tmp, &telemetry_path);
            }
        }

        if step_counter % 15 == 0 {
            let _ = org.save_state(&state_path);
        }

        step_counter += 1;
        if let Some(limit) = max_steps {
            if step_counter >= limit {
                let _ = org.save_state(&state_path);
                break;
            }
        }
        std::thread::sleep(std::time::Duration::from_millis(1200));
    }
}
