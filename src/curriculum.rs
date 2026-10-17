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

/// A single time-series point for SVG sparklines on the telemetry dashboard.
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
                "mentor",
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

/// Command sent from the user or CLI into Alpha 7's live loop.
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

/// Complete real-time telemetry & internal instrument payload exported by the live daemon.
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
    // Instrument 7: Phases 5–10 Sovereign Quantum, Zeigarnik-Insula Uneasiness, Broca Language, Virtual Computer, BSc Graduation & PhD Discovery Lab
    pub phase10_advanced_status: serde_json::Value,
}

pub fn now_unix() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

/// Runs Alpha 7 as a live, continuous organism daemon bridged to `live_dir`.
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
    let _ = org.save_state(&state_path);

    let _curriculum = discover_grounded_curriculum();

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
        let _ = org.act_and_analyze(
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
        let _ = org.practice_coding("result = 6 * * * 7", None);

        last_action = "game_move_6ply_apical".to_string();
        last_predicted_outcomes = ev_fail.predicted_traits.clone();
        last_actual_outcomes = ev_fail.actual_traits.clone();
        last_prediction_failed = ev_fail.prediction_failed;
        last_analysis_report = ev_fail.analysis_report.clone();
    }

    if org.synthesized_programs.is_empty() {
        let _ = org.synthesize_code_for_goal("42");
        let _ = org.synthesize_code_for_goal("15");
    }

    if org.world.puzzle_solves_count == 0 || !org.world.door_unlocked {
        let _ = org.solve_key_door_puzzle();
    }

    let _initial_exams = org.run_school_exams();
    let _lang_exam = org.run_language_course_exam();
    let _comp_task = org.run_virtual_computer_lab_task();
    let _grad_rep = org.run_academic_graduation();
    if org.phd_lab.completed_theses.is_empty() {
        let _ = org.run_autonomous_phd_research();
    }
    let _ = org.step_deep_library_study(3);
    let _adv_exams = org.run_real_advanced_library_exams();
    let _auto_dir = org.request_autonomous_directive();
    let _phase12_rep = org.run_phase12_chrono_census_ldm_and_unsolved_math();
    let _phase13_rep = org.run_phase13_flaw_discovery_and_balanced_maturation();
    let _phase14_rep = org.run_phase14_curriculum_and_self_evolution();
    let _phase15_rep = org.run_phase15_foveated_vision_video_and_chaos_prover();
    let _phase16_rep = org.run_phase16_dynamic_thalamus_fission_and_games();
    let phase17_rep = org.run_phase17_weekly_games_and_sleep();
    let phase18_rep = org.run_phase18_unified_brain_emergence_suite();
    let _cert6_summary = org.run_six_test_certification();
    let _sealed_loci = org.seal_genome();

    if let Some(p17) = &phase17_rep {
        bridge_log.push(BridgeLogEntry {
            timestamp: now_unix(),
            tick: org.fabric.current_tick,
            role: "alpha7_mouth".into(),
            kind: "phase17_weekly_games_and_sleep".into(),
            message: p17.summary.clone(),
            details: None,
        });
    }
    bridge_log.push(BridgeLogEntry {
        timestamp: now_unix(),
        tick: org.fabric.current_tick,
        role: "alpha7_mouth".into(),
        kind: "phase18_unified_self_mutating_brain".into(),
        message: phase18_rep.summary.clone(),
        details: None,
    });

    let mut live_unified_brain = crate::unified_core_brain::UnifiedCoreBrain::new(
        120_000,
        crate::unified_core_brain::BlindLogSpaceGenome::viable_default(),
        0x2026_1017_A700,
    );
    live_unified_brain.homeostatic_social_drive = 0.65;
    let mut live_crucible =
        crate::unified_core_brain::LiveSovereignCrucibleEngine::new(0x2026_1017_A700);

    let mut step_counter = 0u64;
    loop {
        let t_step_start = Instant::now();
        let mut current_activity = String::new();

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
                            let (_rep, recs) = org.perceive_and_step(&frame, true);
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
                            let (_rep, recs) = org.perceive_and_step(&frame, true);
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
                            let (node, _rep) = org.experience_concept(&cname, &frame, None, actor);
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
                        "sleep" | "bio_sleep" => {
                            let rep = org.consolidate_memories();
                            let bio_ev = org
                                .phase17_weekly_games_sleep
                                .bio_sleep_organ
                                .step_homeostatic_and_circadian_sleep(2, 2, true);
                            let bio_msg = bio_ev
                                .map(|e| {
                                    format!(
                                        "{} | [BIO-SLEEP #{}] {} (Adenosine S: {:.2} -> {:.2}, NREM pruned {} synapses, SWR replayed {} episodes)",
                                        rep.summary,
                                        e.cycle_number,
                                        e.trigger_reason,
                                        e.pre_sleep_adenosine_s,
                                        e.post_sleep_adenosine_s,
                                        e.nrem_weak_synapses_pruned,
                                        e.swr_game_and_language_episodes_replayed
                                    )
                                })
                                .unwrap_or(rep.summary);
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "sleep_replay".into(),
                                kind: "sleep".into(),
                                message: bio_msg.clone(),
                                details: None,
                            });
                            current_activity = bio_msg;
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
                        "coach" => {
                            let raw_text = cmd.text.unwrap_or_default();
                            let domain = cmd.concept.unwrap_or_else(|| "User Live Coaching".into());
                            let parts: Vec<&str> = raw_text.splitn(3, '|').collect();
                            let prompt_s = parts.first().copied().unwrap_or("").trim();
                            let ans_s = parts.get(1).copied().unwrap_or("").trim();
                            let exp_s = parts
                                .get(2)
                                .copied()
                                .unwrap_or("User-guided conceptual rule")
                                .trim();
                            if !prompt_s.is_empty() && !ans_s.is_empty() {
                                let lesson =
                                    org.coach_conceptually(&domain, prompt_s, ans_s, exp_s);
                                let msg = format!(
                                    "[{}] Coached on '{}': Initial prediction '{}' -> Self-Analysis: {} -> Applied concept: '{}' -> Verified: {}",
                                    lesson.lesson_id,
                                    lesson.trigger_question,
                                    lesson.initial_wrong_answer,
                                    lesson.self_analysis_question,
                                    lesson.conceptual_hypothesis,
                                    lesson.after_score
                                );
                                bridge_log.push(BridgeLogEntry {
                                    timestamp: now_unix(),
                                    tick: org.fabric.current_tick,
                                    role: "alpha7_mouth".into(),
                                    kind: "coach".into(),
                                    message: msg.clone(),
                                    details: Some(format!("Domain: {}", lesson.domain)),
                                });
                                current_activity = msg;
                            }
                        }
                        "game" => {
                            let st = live_crucible.step_live_move();
                            let game_msg = format!(
                                "[Sovereign Crucible · {}] {}",
                                st.active_way_name, st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "live_game".into(),
                                message: game_msg.clone(),
                                details: Some(st.last_neural_token_stream),
                            });
                            current_activity = game_msg;
                        }
                        "game_replay" | "crucible_block_way" => {
                            live_crucible.force_block_current_way();
                            let st = &live_crucible.last_status;
                            let msg = format!(
                                "[DETOUR SEALED (██) -> PROMOTED {}] {}",
                                st.active_way_name, st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "crucible_block_way".into(),
                                message: msg.clone(),
                                details: Some(st.last_neural_token_stream.clone()),
                            });
                            current_activity = msg;
                        }
                        "game_restart" | "crucible_new_seed" => {
                            let new_seed = now_unix().wrapping_add(step_counter * 0x9E37_79B9);
                            live_crucible.reset_new_unseen_world(new_seed);
                            let st = &live_crucible.last_status;
                            let msg = format!(
                                "[NEW UNSEEN CRUCIBLE WORLD · Seed {:#x} · Ep#1 Cold Discovery] {}",
                                new_seed & 0xFFFF_FFFF,
                                st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "crucible_new_seed".into(),
                                message: msg.clone(),
                                details: Some(st.last_neural_token_stream.clone()),
                            });
                            current_activity = msg;
                        }
                        "game_next" | "crucible_invert_ctx" => {
                            live_crucible.toggle_context_polarity();
                            let st = &live_crucible.last_status;
                            let msg = format!(
                                "[CONTEXT POLARITY INVERTED -> {}] {}",
                                st.current_context_polarity, st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "crucible_invert_ctx".into(),
                                message: msg.clone(),
                                details: Some(st.last_neural_token_stream.clone()),
                            });
                            current_activity = msg;
                        }
                        "crucible_lesion" => {
                            live_crucible.trigger_flagless_synapse_lesion();
                            let st = &live_crucible.last_status;
                            let msg = format!(
                                "[FLAGLESS SYNAPSE LESION EXECUTED -> 0 Synapses] {}",
                                st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "crucible_lesion".into(),
                                message: msg.clone(),
                                details: Some(st.last_neural_token_stream.clone()),
                            });
                            current_activity = msg;
                        }
                        "game_select" => {
                            let sel_id = cmd.text.or(cmd.concept).unwrap_or_else(|| "0".into());
                            let way_idx = sel_id
                                .trim()
                                .trim_start_matches("way_")
                                .parse::<usize>()
                                .unwrap_or(0)
                                % 4;
                            live_crucible.sealed_ways_on_board[way_idx] = false;
                            live_crucible.active_way_index = way_idx;
                            live_crucible.step_in_way = 0;
                            let st = live_crucible.step_live_move();
                            let msg = format!(
                                "[SELECTED CRUCIBLE WAY -> {}] {}",
                                st.active_way_name, st.last_move_explanation
                            );
                            bridge_log.push(BridgeLogEntry {
                                timestamp: now_unix(),
                                tick: org.fabric.current_tick,
                                role: "alpha7_mouth".into(),
                                kind: "game_select".into(),
                                message: msg.clone(),
                                details: Some(st.last_neural_token_stream),
                            });
                            current_activity = msg;
                        }
                        _ => {}
                    }
                }
            }
            // Keep inbox.jsonl and processed_ids bounded without ever forgetting IDs still in inbox.jsonl (Fixes S1)
            let retained_lines: Vec<&str> = if lines.len() > 200 {
                let tail: Vec<&str> = lines.into_iter().rev().take(80).rev().collect();
                let _ = fs::write(&inbox_path, tail.join("\n") + "\n");
                tail
            } else {
                lines
            };
            if processed_ids.len() > 500 {
                let mut active_inbox_ids = std::collections::HashSet::new();
                for l in &retained_lines {
                    if let Ok(cmd) = serde_json::from_str::<BridgeCommand>(l.trim()) {
                        active_inbox_ids.insert(cmd.id);
                    }
                }
                processed_ids.retain(|id| active_inbox_ids.contains(id));
            }
            if let Ok(p_json) = serde_json::to_string(&processed_ids) {
                let _ = fs::write(&processed_path, p_json);
            }
        }

        // 2. Step The Sovereign Crucible (Single Ultra-Hard Multi-Path Detour, Conjunctive XOR & Context-Rotated Transitive Game)
        let crucible_status = live_crucible.step_live_move();
        let board_just_finished = crucible_status.step_in_way >= crucible_status.total_steps_in_way;

        // Feed the current Sovereign Crucible gate into the 1M-neuron spiking fabric
        let move_tag = format!(
            "crucible_way{}_step{}",
            crucible_status.active_way_index + 1,
            crucible_status.step_in_way
        );
        let game_frame = org.body.build_frame(
            &[
                crucible_status.active_way_name.as_str(),
                move_tag.as_str(),
            ],
            &[crucible_status.last_neural_token_stream.as_str()],
            &[crucible_status.state1_conscious_way.as_str()],
            &[crucible_status.current_context_polarity.as_str()],
            Some("sovereign_crucible"),
        );
        let (rep, _recs) = org.perceive_and_step(&game_frame, true);
        let last_touched = rep.touched_neurons;
        cumulative_predicted_spikes += rep.predicted_matches.len() as u64;
        cumulative_surprise_bursts += rep.surprise.unpredicted_bursts.len() as u64;
        cumulative_failed_predictions += rep.surprise.failed_predictions.len() as u64;
        cumulative_btsp_updates += rep.surprise.plastic_updates as u64;
        let curr_idx = crucible_status.active_way_index;

        if board_just_finished || step_counter % 4 == 0 {
            let _ = org
                .phase17_weekly_games_sleep
                .four_cell_cluster
                .run_four_cell_fission_rollout_and_fusion(step_counter);
        }

        let weekly_game_msg = format!(
            "[Sovereign Crucible · {} · Step {}/{} · Ways {}/4 · Ep1 Cold Mistakes: {} -> Cur: {}] {}",
            crucible_status.active_way_name,
            crucible_status.step_in_way,
            crucible_status.total_steps_in_way,
            crucible_status.distinct_ways_solved_count,
            crucible_status.ep1_cold_mistakes_recorded,
            crucible_status.current_episode_mistakes,
            crucible_status.last_move_explanation
        );
        if current_activity.is_empty() {
            current_activity = weekly_game_msg.clone();
        } else {
            current_activity = format!("{} || {}", current_activity, weekly_game_msg);
        }

        if board_just_finished || step_counter % 8 == 0 {
            bridge_log.push(BridgeLogEntry {
                timestamp: now_unix(),
                tick: org.fabric.current_tick,
                role: "alpha7_mouth".into(),
                kind: "live_game".into(),
                message: crucible_status.last_move_explanation.clone(),
                details: Some(format!(
                    "Token Stream: {} | Seed: {:#x}",
                    crucible_status.last_neural_token_stream,
                    crucible_status.world_seed & 0xFFFF_FFFF
                )),
            });
        }

        // Step Two-Process Borbély Homeostatic (`Process S`) + Circadian (`Process C`) Sleep Organ
        // Only trigger an autonomous learning nap right after finishing a board (never mid-move!)
        let ep_done_tick = if board_just_finished { 1 } else { 0 };
        if let Some(bio_sleep_ev) = org
            .phase17_weekly_games_sleep
            .bio_sleep_organ
            .step_homeostatic_and_circadian_sleep(ep_done_tick, ep_done_tick, false)
        {
            let _ = org.consolidate_memories();
            bridge_log.push(BridgeLogEntry {
                timestamp: now_unix(),
                tick: org.fabric.current_tick,
                role: "sleep_replay".into(),
                kind: "bio_sleep".into(),
                message: format!(
                    "[BIO-SLEEP #{}] {} (Adenosine S: {:.2} -> {:.2}, NREM pruned {} synapses, SWR replayed {} episodes)",
                    bio_sleep_ev.cycle_number,
                    bio_sleep_ev.trigger_reason,
                    bio_sleep_ev.pre_sleep_adenosine_s,
                    bio_sleep_ev.post_sleep_adenosine_s,
                    bio_sleep_ev.nrem_weak_synapses_pruned,
                    bio_sleep_ev.swr_game_and_language_episodes_replayed
                ),
                details: None,
            });
        }

        // Phase 11: Periodic paced deep reading comprehension of `/data/alpha3-library` & executive directive refresh
        if step_counter % 5 == 0 {
            let _ = org.step_deep_library_study(1);
            let _ = org.request_autonomous_directive();
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
        let touched_now = last_touched;

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

        // Build Concept list for Instrument 4 (keep full count, export top 80 most familiar/recent for fast live telemetry)
        let total_concepts_count = org.knowledge_web.concepts.len();
        let mut concepts_vec: Vec<_> = org.knowledge_web.concepts.values().collect();
        concepts_vec.sort_by(|a, b| {
            b.exposures
                .cmp(&a.exposures)
                .then_with(|| a.name.cmp(&b.name))
        });
        let concepts_json: Vec<serde_json::Value> = concepts_vec
            .into_iter()
            .take(80)
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
        // Phase 16B: Continuously fuse all 5 peripheral organs into a single UnifiedCorticalWavePacket before entering the brain
        let _ = org
            .phase16_thalamus_fission_games
            .thalamic_bus
            .fuse_live_sensory_traits_into_single_stream(
                &live_frame.eyes,
                &live_frame.ears,
                &live_frame.hands,
                &live_frame.smell,
                &live_frame.senses,
            );
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

        // Step Phase 10 Zeigarnik-Insula Uneasiness Organ and compute live neuron uneasiness stats
        let top_open_loop = org.substrate.unease_organ.step_uneasiness(1);
        let felt_unease_u = org.substrate.unease_organ.felt_unease_u;
        let unease_focus_topic = top_open_loop.map(|l| l.context_cue);
        let uneasy_neuron_count = org
            .fabric
            .neurons
            .iter()
            .filter(|n| n.uneasiness_q8 > 0)
            .count();

        // Step live UnifiedCoreBrain cortical rhythm (15Hz Conscious State 1 <-> Suppressed State 2 alternation)
        let rivalry_epoch = step_counter;
        let rivalry_is_state1 = (rivalry_epoch % 2) == 0;
        let ch_idx = (rivalry_epoch % 8) as u32;
        let _ = live_unified_brain.tick_channels(
            &[
                (10 + ch_idx, if rivalry_is_state1 { 1.21 } else { 1.0 }),
                (20 + ch_idx, if rivalry_is_state1 { 1.0 } else { 1.21 }),
            ],
            &[800, 801],
            true,
        );
        let live_unified_brain_state = serde_json::json!({
            "step_epoch": rivalry_epoch,
            "rivalry_15hz_active_state": if rivalry_is_state1 {
                format!("State 1 · {} (1.21x Gain -> Motor Output)", crucible_status.state1_conscious_way)
            } else {
                format!("State 2 · {} (1.00x Gain · Detour Standby)", crucible_status.state2_suppressed_backup_way)
            },
            "rivalry_is_conscious_state1": rivalry_is_state1,
            "recruited_conjunctive_interneurons": crucible_status.recruited_interneurons_count,
            "active_synapses_in_core": crucible_status.active_synapses_in_core,
            "homeostatic_social_drive": live_crucible.brain.homeostatic_social_drive,
            "genome_params": live_crucible.brain.genome.raw_genes,
            "context_pos_mental_line": crucible_status.context_pos_mental_line,
            "context_neg_mental_line": crucible_status.context_neg_mental_line,
            "last_neural_token_stream": crucible_status.last_neural_token_stream,
        });

        let crucible_ways_json: Vec<serde_json::Value> = (0..4usize)
            .map(|w| {
                let way_title = crate::unified_core_brain::LiveSovereignCrucibleEngine::way_name(w);
                let is_solved = crucible_status.ways_solved_this_board[w];
                let is_sealed = crucible_status.sealed_ways_on_board[w];
                let is_active = crucible_status.active_way_index == w;
                let mastery_pct = if is_solved || crucible_status.total_crucible_boards_mastered > 0 {
                    100.0
                } else if is_active {
                    ((crucible_status.step_in_way as f32) / 6.0) * 100.0
                } else {
                    0.0
                };
                serde_json::json!({
                    "game_index": w,
                    "game_id": format!("way_{}", w),
                    "title": way_title,
                    "scheduled_day": w + 1,
                    "day_label": if is_sealed {
                        "SEALED (██ Detour Forced)"
                    } else if is_active {
                        "ACTIVE (State 1 · 1.21x)"
                    } else {
                        "STANDBY (State 2 · 1.00x)"
                    },
                    "category": crucible_status.current_context_polarity,
                    "episodes_played": crucible_status.episode_in_world,
                    "episodes_won": crucible_status.total_crucible_boards_mastered + usize::from(is_solved),
                    "mastery_percentage": mastery_pct,
                    "mastered": is_solved || crucible_status.total_crucible_boards_mastered > 0,
                    "current_seed": crucible_status.world_seed,
                    "current_move_step": if is_active { crucible_status.step_in_way } else if is_solved { 6 } else { 0 },
                    "total_moves_in_board": 6,
                    "current_board_progress_pct": if is_active {
                        ((crucible_status.step_in_way as f32) / 6.0) * 100.0
                    } else if is_solved {
                        100.0
                    } else {
                        0.0
                    },
                    "active_cell_turn_label": format!(
                        "State 1: {} | State 2 Standby: {}",
                        crucible_status.state1_conscious_way,
                        crucible_status.state2_suppressed_backup_way
                    ),
                    "current_move_action_summary": crucible_status.last_move_explanation,
                    "live_board_2d": crucible_status.board_8x8,
                    "latest_episode_summary": crucible_status.last_move_explanation,
                    "vocabulary_and_laws_gained": [
                        format!("Ep1 Cold Mistakes: {}", crucible_status.ep1_cold_mistakes_recorded),
                        format!("Current Episode Mistakes: {}", crucible_status.current_episode_mistakes),
                        format!("Neural Stream: {}", crucible_status.last_neural_token_stream),
                    ],
                })
            })
            .collect();

        let crucible_arena_json = serde_json::json!({
            "current_day_of_week": crucible_status.active_way_index + 1,
            "active_game_index": crucible_status.active_way_index,
            "total_games_mastered": crucible_status.distinct_ways_solved_count,
            "total_episodes_across_week": crucible_status.episode_in_world,
            "overall_weekly_mastery_pct": (crucible_status.distinct_ways_solved_count as f32 / 4.0) * 100.0,
            "games": crucible_ways_json,
        });

        let total_held_out_sat = org
            .school
            .last_suite_report
            .as_ref()
            .map(|r| r.total_items_sat)
            .unwrap_or(0)
            + org
                .deep_agency
                .last_advanced_exams_report
                .as_ref()
                .map(|r| r.total_items)
                .unwrap_or(0);
        let total_held_out_correct = org
            .school
            .last_suite_report
            .as_ref()
            .map(|r| r.total_items_correct)
            .unwrap_or(0)
            + org
                .deep_agency
                .last_advanced_exams_report
                .as_ref()
                .map(|r| r.total_correct)
                .unwrap_or(0);

        let phase10_advanced_status = serde_json::json!({
            "version": "v3.0.0",
            "organs_total": 1,
            "felt_uneasiness_u": felt_unease_u,
            "uneasiness_focus_topic": unease_focus_topic,
            "open_loops_count": org.substrate.unease_organ.open_loops.len(),
            "resolved_loops_total": org.substrate.unease_organ.resolved_loops_count,
            "uneasy_neurons_count": uneasy_neuron_count,
            "helmholtz_vocab_size": org.substrate.helmholtz.id_to_symbol.len(),
            "helmholtz_omega_slow_edges": org.substrate.helmholtz.omega_slow.len(),
            "helmholtz_s_minus_inhibitory_edges": org.substrate.helmholtz.s_minus.len(),
            "genetic_vault_sealed_loci": org.sovereign_brain.genetic_vault.sealed_loci.len(),
            "genetic_vault_epoch": org.sovereign_brain.genetic_vault.generation_epoch,
            "epistemic_verified_beliefs": org.sovereign_brain.epistemic_engine.verified_beliefs.len(),
            "language_course_report": org.language_academy.last_exam_report,
            "virtual_computer_cursor": [org.virtual_computer.cursor_x, org.virtual_computer.cursor_y],
            "virtual_computer_focused_app": format!("{:?}", org.virtual_computer.focused_app),
            "virtual_computer_last_stdout": org.virtual_computer.last_terminal_stdout,
            "virtual_computer_files": org.virtual_computer.virtual_fs.keys().cloned().collect::<Vec<String>>(),
            "academic_graduation_report": org.academic_engine.last_graduation_report,
            "phd_theses_completed": org.phd_lab.completed_theses,
            "working_ethics": org.deep_agency.ethics,
            "advanced_library_exams": org.deep_agency.last_advanced_exams_report,
            "autonomous_directive": org.deep_agency.last_autonomous_directive,
            "recent_comprehension_traces": org.deep_agency.recent_comprehension_traces.iter().rev().take(8).cloned().collect::<Vec<_>>(),
            "library_study_cursors": [
                org.deep_agency.g4_g8_prose_cursor,
                org.deep_agency.g9_g12_prose_cursor,
                org.deep_agency.hos_ideas_cursor
            ],
            "total_held_out_items_sat_all_suites": total_held_out_sat,
            "total_held_out_items_correct_all_suites": total_held_out_correct,
            "phase12_ldm_benchmark": org.chrono_census_math.last_ldm_benchmark,
            "phase12_self_census": org.chrono_census_math.last_census,
            "phase12_unsolved_math_probes": org.chrono_census_math.last_math_probes,
            "phase12_missing_brain_mechanisms": org.chrono_census_math.last_missing_mechanisms,
            "phase12_honest_speech_disclosure": org.chrono_census_math.last_honest_speech,
            "phase13_balanced_hybrid_ldm_report": org.phase13_balanced_hybrid_ldm.last_report,
            "phase14_evolution_dialogue_report": org.phase14_evolution_dialogue.last_report,
            "phase15_foveated_video_chaos_report": org.phase15_foveated_video_chaos.last_report,
            "phase16_thalamus_fission_games_report": org.phase16_thalamus_fission_games.last_report,
            "live_fission_games_state": org.phase16_thalamus_fission_games.fission_games,
            "live_thalamus_packet": org.phase16_thalamus_fission_games.thalamic_bus.last_wave_packet,
            "phase17_weekly_games_sleep_report": org.phase17_weekly_games_sleep.last_report,
            "live_weekly_arena": crucible_arena_json,
            "live_sovereign_crucible": crucible_status,
            "live_four_cell_cluster": org.phase17_weekly_games_sleep.four_cell_cluster,
            "live_bio_sleep_organ": org.phase17_weekly_games_sleep.bio_sleep_organ,
            "phase18_unified_brain_report": org.phase18_unified_brain_emergence_report,
            "live_unified_brain_state": live_unified_brain_state,
        });

        let snapshot = LiveTelemetrySnapshot {
            updated_at_unix: now_unix(),
            status: "ONLINE · AWAKE · PURE ROAD v3.0.0 (SOVEREIGN CRUCIBLE MULTI-PATH DETOUR + CONTEXT-ROTATED MENTAL LINE + 15Hz COMMITMENT-GATED RIVALRY)".to_string(),
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
            concepts_count: total_concepts_count,
            concepts: concepts_json,
            concept_relations: org.knowledge_web.relations.iter().take(80).cloned().collect(),
            sleep_cycles_completed: org.phase17_weekly_games_sleep.bio_sleep_organ.bio_sleep_cycles_completed as u32,
            last_sleep_report: org.knowledge_web.last_sleep_report.clone(),
            curriculum_index: curr_idx + 1,
            curriculum_total: 4,
            recent_episodes,
            bridge_log: bridge_log.iter().rev().cloned().collect(),
            school_report: org.school.last_suite_report.clone(),
            phase10_advanced_status,
        };

        if let Ok(json_str) = serde_json::to_string_pretty(&snapshot) {
            if fs::write(&telemetry_tmp, json_str).is_ok() {
                let _ = fs::rename(&telemetry_tmp, &telemetry_path);
            }
        }

        if step_counter > 0 && step_counter % 100 == 0 {
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
