//! Alpha 7 Native Pure-Rust CLI, 2D World Explorer & Interactive REPL (Phase 1 + Phase 2A-2D)

use alpha7::Alpha7Organism;
use std::env;
use std::io::{self, Write};
use std::time::Instant;

fn run_demo() {
    println!("================================================================================");
    println!(" ALPHA 7 v0.3 — 100% PURE RUST: SPARSE DENDRITIC BRAIN, V1/V2 RETINA, MOUTH & LAB");
    println!("================================================================================");

    let t0 = Instant::now();
    let mut org = Alpha7Organism::new(1_000_000, 64);
    let init_ms = t0.elapsed().as_secs_f64() * 1000.0;

    println!("\n[1] HARDWARE-EFFICIENT SPARSE DENDRITIC FABRIC");
    println!("    • Total Dendritic Neurons : {}", org.neuron_count());
    println!(
        "    • Memory Footprint        : {:.1} MB",
        org.memory_footprint_mb()
    );
    println!("    • Initialization Time     : {:.1} ms", init_ms);

    println!("\n[2] PHASE 2A: REAL RAW-PIXEL V1/V2 VISUAL CORTEX & COCHLEAR WAVEFORM ENCODER");
    let wavs = alpha7::curriculum::ensure_grounded_wav_assets();
    if let Some(glance) = org
        .body
        .eyes
        .analyze_image_file("/data/dev/genome/world/anchor/image_0001.jpg")
    {
        println!(
            "    • V1/V2 Retina Glance     : {} ({}x{} px, symmetry={:.2}, contrast={:.2})",
            glance.source_path,
            glance.width,
            glance.height,
            glance.bilateral_symmetry,
            glance.contrast_std
        );
        println!("    • Extracted Pixel Traits  : {:?}", glance.extracted_traits);
    }
    if let Some(first_wav) = wavs.first() {
        if let Some(cochlea) = org.body.ears.analyze_wav_file(first_wav) {
            println!(
                "    • Cochlear PCM Analysis   : {} ({} Hz, {} ms, ZCR={:.3}, RMS={:.3})",
                cochlea.source_path,
                cochlea.sample_rate,
                cochlea.duration_ms,
                cochlea.zero_crossing_rate,
                cochlea.rms_energy
            );
            println!("    • Extracted Audio Traits  : {:?}", cochlea.extracted_traits);
        }
    }

    println!("\n[3] INFANT-LIKE 1-2 SHOT CONCEPT FORMATION & PHASE 2B COMPOSITIONAL HIERARCHY");
    org.world.move_agent_to(&mut org.body, 2, 2);
    let frame1 = org
        .world
        .sense_current_frame(&mut org.body, Some("look at this cat kitty"));
    let t_step = Instant::now();
    let (node1, rep1) = org.experience_concept(
        "cat",
        &frame1,
        Some(("gentle_pet".to_string(), "ears:purr".to_string())),
        "user",
    );
    let step_us = t_step.elapsed().as_secs_f64() * 1_000_000.0;
    println!(
        "    • Exposure #1 at (2,2) Orange Cat : familiarity={:.2}, touched={} / {} neurons ({:.1} µs)",
        node1.familiarity,
        rep1.touched_neurons,
        org.neuron_count(),
        step_us
    );

    org.world.move_agent_to(&mut org.body, 10, 2);
    let frame2 = org
        .world
        .sense_current_frame(&mut org.body, Some("another cat"));
    let (node2, _) = org.experience_concept("cat", &frame2, None, "user");
    println!(
        "    • Exposure #2 at (10,2) Black Cat : familiarity={:.2}, core invariants={:?}",
        node2.familiarity,
        node2
            .core_invariants()
            .iter()
            .map(|t| &t.trait_key)
            .collect::<Vec<_>>()
    );

    // Experience dog at (2, 9) so Phase 2B induces shared category `living_quadruped`
    org.world.move_agent_to(&mut org.body, 2, 9);
    let frame_dog = org.world.sense_current_frame(&mut org.body, Some("dog"));
    org.experience_concept("dog", &frame_dog, None, "user");

    let cmp_reply = org.converse("compare cat and dog");
    println!("    • Phase 2B Comparison     : \"{}\"", cmp_reply.spoken_response);

    println!("\n[4] PREDICTIVE PROCESSING, FAILED-PREDICTION ANALYSIS & CAUSAL 'WHY'");
    org.world.move_agent_to(&mut org.body, 6, 2);
    let f_switch = org.world.sense_current_frame(&mut org.body, None);
    let (eval1, _) = org.act_and_analyze(
        &f_switch,
        "press_switch",
        &["eyes:light_on".to_string()],
        "user",
    );
    println!("    • Initial Causal Learning : {}", eval1.analysis_report);

    let f_light = org.body.build_frame(&["light_on"], &[], &[], &[], None);
    org.act_and_analyze(
        &f_light,
        "read_book",
        &["eyes:knowledge_gained".to_string()],
        "user",
    );

    let f_unplugged = org.body.build_frame(
        &["switch_visible", "toggle_lever"],
        &[],
        &["hard_plastic"],
        &["power_unplugged"],
        None,
    );
    let _ = org.act_and_analyze(
        &f_unplugged,
        "press_switch",
        &["eyes:darkness_remains".to_string()],
        "user",
    );
    let why_reply = org.converse("why did press_switch fail?");
    println!("    • Phase 2B Causal 'Why'   : \"{}\"", why_reply.spoken_response);

    println!("\n[5] PHASE 2C & 2D: GOAL-DIRECTED CODE SYNTHESIS & HIPPOCAMPAL SLEEP REPLAY");
    let synth_reply = org.converse("synthesize code for 42");
    println!("    • Phase 2C Code Synthesis : \"{}\"", synth_reply.spoken_response);

    let sleep_reply = org.converse("sleep consolidate");
    println!("    • Phase 2D Sleep Replay   : \"{}\"", sleep_reply.spoken_response);

    println!("\n[6] PHASE 3A–3D: GRADED SCHOOL EXAMS (LIVE L vs. NULL TWIN N) & KEY–DOOR TOOL PUZZLE");
    let puzzle_msg = org.solve_key_door_puzzle();
    println!("    • Phase 3D Key-Door Puzzle: {}", puzzle_msg);

    let suite = org.run_school_exams();
    println!(
        "    • Phase 3A–3C Exam Suite  : Passed {}/{} held-out exams ({}/{} items, {:.1}% Live L vs {:.1}% Null Twin N, +{:.1}% margin in {:.1} ms)",
        suite.exams_passed,
        suite.total_exams,
        suite.total_items_correct,
        suite.total_items_sat,
        suite.mean_live_score * 100.0,
        suite.mean_null_twin_score * 100.0,
        suite.mean_margin_over_twin * 100.0,
        suite.total_eval_time_ms
    );
    for v in &suite.exam_verdicts {
        println!(
            "      - {:26} | Live L: {:5.1}% ({:3}/{:3}) | Twin N ({:14}): {:5.1}% | Bar: {:5.1}% | PASS={}",
            v.family,
            v.live_score * 100.0,
            v.correct_items,
            v.n_items,
            v.strongest_twin_name,
            v.strongest_twin_score * 100.0,
            v.pass_mark * 100.0,
            v.passed
        );
    }
    let comp_reply = org.converse("complete: the little red");
    println!("    • Phase 3B Sequence Memory: {}", comp_reply.spoken_response);
    println!("================================================================================");
}

fn run_repl() {
    println!("================================================================================");
    println!(" ALPHA 7 v0.3 INTERACTIVE LIVE REPL");
    println!(" Commands:");
    println!("   map                     - Render the 2D World Canvas");
    println!("   move <x> <y>            - Move Alpha 7's body & hands to (x, y)");
    println!("   saccade <x> <y>         - Move Alpha 7's eye fixation to (x, y)");
    println!("   teach <concept>         - Bind current 5-sense traits to <concept> (1-2 shot)");
    println!("   code <expr>             - Practice executing small code with Eyes & Hands");
    println!("   synthesize <target>     - Synthesize & verify code for a target result");
    println!("   sleep                   - Run Hippocampal-Neocortical sleep replay consolidation");
    println!("   exams                   - Sit all 8 held-out School Exams (Live L vs Null Twin N)");
    println!("   puzzle                  - Solve the 4-Step Key-Door-Vault tool puzzle on 2D Canvas");
    println!("   complete <phrase>       - Complete a sentence from Cortical Sequence Memory");
    println!("   memories                - List direct episodic memories formed with you");
    println!("   save [path] / load [p]  - Persist or restore Alpha 7's full brain state");
    println!("   quit / exit             - Exit REPL");
    println!("   Or type any question (e.g. 'compare cat and dog', 'why did press_switch fail?')");
    println!("================================================================================");

    let mut org = Alpha7Organism::new(1_000_000, 64);
    let stdin = io::stdin();

    loop {
        print!("\nalpha7 ({},{})> ", org.world.agent_x, org.world.agent_y);
        let _ = io::stdout().flush();

        let mut line = String::new();
        if stdin.read_line(&mut line).unwrap_or(0) == 0 {
            break;
        }
        let cmd = line.trim();
        if cmd.is_empty() {
            continue;
        }
        if cmd == "quit" || cmd == "exit" {
            break;
        } else if cmd == "map" {
            println!("{}", org.world.render_ascii());
        } else if let Some(rest) = cmd.strip_prefix("move ") {
            let parts: Vec<&str> = rest.split_whitespace().collect();
            if parts.len() == 2 {
                if let (Ok(x), Ok(y)) = (parts[0].parse::<i32>(), parts[1].parse::<i32>()) {
                    org.world.move_agent_to(&mut org.body, x, y);
                    let frame = org.world.sense_current_frame(&mut org.body, None);
                    let (_, recs) = org.perceive_and_step(&frame, true);
                    println!("{}", org.world.render_ascii());
                    println!("Alpha 7: {}", org.language.speak_perception(&frame, &recs));
                    continue;
                }
            }
            println!("Usage: move <x> <y>");
        } else if let Some(rest) = cmd.strip_prefix("saccade ") {
            let parts: Vec<&str> = rest.split_whitespace().collect();
            if parts.len() == 2 {
                if let (Ok(x), Ok(y)) = (parts[0].parse::<i32>(), parts[1].parse::<i32>()) {
                    org.world.saccade_to(&mut org.body, x, y);
                    let frame = org.world.sense_current_frame(&mut org.body, None);
                    let (_, recs) = org.perceive_and_step(&frame, true);
                    println!(
                        "Alpha 7 (gaze {},{}): {}",
                        x,
                        y,
                        org.language.speak_perception(&frame, &recs)
                    );
                    continue;
                }
            }
            println!("Usage: saccade <x> <y>");
        } else if let Some(concept) = cmd.strip_prefix("teach ") {
            let cname = concept.trim();
            let frame = org.world.sense_current_frame(&mut org.body, Some(cname));
            let (node, _) = org.experience_concept(cname, &frame, None, "user");
            println!(
                "Alpha 7: Learned '{}' (exposure #{}, familiarity {:.0}%).",
                node.name,
                node.exposures,
                node.familiarity * 100.0
            );
        } else if let Some(code_str) = cmd.strip_prefix("code ") {
            let eval = org.practice_coding(code_str, None);
            println!("Alpha 7: {}", eval.analysis_report);
        } else if let Some(target_str) = cmd.strip_prefix("synthesize ") {
            let rep = org.synthesize_code_for_goal(target_str);
            println!("Alpha 7: {}", rep.summary);
        } else if cmd == "sleep" {
            let rep = org.consolidate_memories();
            println!("Alpha 7: {}", rep.summary);
        } else if cmd == "exams" {
            let rep = org.run_school_exams();
            println!(
                "Alpha 7: Passed {}/{} exams ({}/{} items, {:.1}% Live L vs {:.1}% Null Twin N).",
                rep.exams_passed,
                rep.total_exams,
                rep.total_items_correct,
                rep.total_items_sat,
                rep.mean_live_score * 100.0,
                rep.mean_null_twin_score * 100.0
            );
        } else if cmd == "puzzle" {
            println!("Alpha 7: {}", org.solve_key_door_puzzle());
        } else if cmd == "memories" {
            for ep in org.knowledge_web.episodes.iter().rev().take(10) {
                println!("  • [tick {}] {}", ep.tick, ep.summary);
            }
        } else if let Some(rest) = cmd.strip_prefix("save") {
            let path = rest.trim();
            let target = if path.is_empty() {
                "brain_state.json"
            } else {
                path
            };
            match org.save_state(target) {
                Ok(_) => println!("Saved Alpha 7 brain state to {}", target),
                Err(e) => println!("Save error: {}", e),
            }
        } else if let Some(rest) = cmd.strip_prefix("load") {
            let path = rest.trim();
            let target = if path.is_empty() {
                "brain_state.json"
            } else {
                path
            };
            match Alpha7Organism::load_state(target) {
                Ok(loaded) => {
                    org = loaded;
                    println!("Loaded Alpha 7 brain state from {}", target);
                }
                Err(e) => println!("Load error: {}", e),
            }
        } else {
            let reply = org.converse(cmd);
            println!("Alpha 7: {}", reply.spoken_response);
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.iter().any(|a| a == "--daemon") {
        let mut live_dir = "/data/dev/alpha7/live".to_string();
        let mut max_steps: Option<u64> = None;
        for i in 0..args.len() {
            if args[i] == "--live-dir" && i + 1 < args.len() {
                live_dir = args[i + 1].clone();
            } else if args[i] == "--steps" && i + 1 < args.len() {
                max_steps = args[i + 1].parse::<u64>().ok();
            }
        }
        alpha7::curriculum::run_live_daemon(&live_dir, max_steps);
    } else if args.iter().any(|a| a == "--repl" || a == "-i") {
        run_repl();
    } else {
        run_demo();
    }
}
