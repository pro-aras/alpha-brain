//! Alpha 7 Native Pure-Rust CLI, 2D World Explorer & Interactive REPL (Phase 1 + Phase 2A-2D)

use alpha7::Alpha7Organism;
use std::env;
use std::io::{self, Write};
use std::time::Instant;

fn run_demo() {
    println!("================================================================================");
    println!(" ALPHA 7 v0.8.0 — 100% PURE RUST: SUBSTRATE ORGANS, HELMHOLTZ & 6-TEST CERTIFIED");
    println!("================================================================================");

    let t0 = Instant::now();
    let mut org = Alpha7Organism::new(1_000_000, 64);
    let init_ms = t0.elapsed().as_secs_f64() * 1000.0;

    println!("\n[1] HARDWARE-EFFICIENT SPARSE DENDRITIC FABRIC & HOT16/COLDSOA SUBSTRATE");
    println!("    • Total Dendritic Neurons : {}", org.neuron_count());
    println!(
        "    • Hot16 Neuron Struct     : {} bytes (4 per 64B cache line)",
        std::mem::size_of::<alpha7::substrate::Hot16>()
    );
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
        "    • Phase 3A–3C Exam Suite  : Passed {}/{} held-out exams ({}/{} items, {:.1}% Live L vs {:.1}% Null Twin N, +{:.1}% margin in {:.1} ms; organism={:.1}%, tool={:.1}%)",
        suite.exams_passed,
        suite.total_exams,
        suite.total_items_correct,
        suite.total_items_sat,
        suite.mean_live_score * 100.0,
        suite.mean_null_twin_score * 100.0,
        suite.mean_margin_over_twin * 100.0,
        suite.total_eval_time_ms,
        suite.organism_attributable_score * 100.0,
        suite.prosthetic_tool_score * 100.0
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

    println!("\n[7] PHASE 0–4 SUBSTRATE ORGANS, TWO-STAGE HELMHOLTZ & 6-TEST CERTIFICATION");
    let cert_msg = org.run_six_test_certification();
    println!("    • {}", cert_msg);
    let inc_reply = org.converse("what is");
    println!("    • ACC Omission Probe      : \"{}\"", inc_reply.spoken_response);

    println!("\n[8] PHASE 5 (v0.9.0): QUANTUM BIFURCATION, SOMATIC GENETIC SELF-HEALING & EPISTEMIC SOVEREIGNTY");
    let cands = vec![
        "decoy_mirage".to_string(),
        "true_core".to_string(),
        "clue_alpha".to_string(),
        "clue_beta".to_string(),
    ];
    let h = vec![1.10, 0.75, 0.70, 0.70];
    let j_mat = vec![
        vec![0.0, -1.60, -1.60, -1.60],
        vec![-1.60, 0.0, 1.30, 1.30],
        vec![-1.60, 1.30, 0.0, 1.30],
        vec![-1.60, 1.30, 1.30, 0.0],
    ];
    let q_res = org
        .sovereign_brain
        .quantum_settler
        .settle_frustrated_network(&cands, &h, &j_mat);
    println!(
        "    • dSB + Trotter Tunneling : Quantum Winner='{}' (E={:.2}) vs Greedy Twin='{}' (E={:.2}) | Tunneled={}",
        q_res.winner_concept,
        q_res.quantum_ground_energy,
        q_res.classical_greedy_winner,
        q_res.classical_greedy_energy,
        q_res.tunneled_past_local_minimum
    );
    let sealed_n = org.seal_genome();
    org.knowledge_web
        .concepts
        .get_mut("cat")
        .unwrap()
        .grounded_words
        .push("injected_tamper_tag".to_string());
    let audit = org.audit_and_heal_genome(true);
    println!(
        "    • Somatic Genetic Vault   : Sealed {} loci -> Injected tamper on 'cat' -> {}",
        sealed_n, audit.summary
    );
    let claim_ok = org.converse("claim: 12 * 12 = 144");
    let claim_bad = org.converse("claim: 12 * 12 = 150");
    println!("    • Epistemic Self-Proof(+) : {}", claim_ok.spoken_response);
    println!("    • Epistemic Self-Proof(-) : {}", claim_bad.spoken_response);
    let loop_rep = org.run_six_parallel_brain_loops("10.0, 20.0, 40.0, 80.0");
    println!(
        "    • 6-Loop Parallel Brain   : [L1] {} | [L2] {} | [L3] {}",
        loop_rep.loop1_sensory_normalization,
        loop_rep.loop2_working_memory_binding,
        loop_rep.loop3_quantum_bifurcation_understanding
    );

    println!(
        "\n[9] PHASE 6–9 (v1.0.0 → v1.3.0): LANGUAGE COURSE, VIRTUAL COMPUTER, UNIVERSITY & PhD DISCOVERY"
    );
    let lang_exam = org.run_language_course_exam();
    println!("    • Phase 6 Language Course : {}", lang_exam.summary);
    let comp_task = org.run_virtual_computer_lab_task();
    println!("    • Phase 7 Virtual Computer: {}", comp_task.summary);
    let grad_rep = org.run_academic_graduation();
    println!("    • Phase 8 Graduation      : {}", grad_rep.summary);
    let phd_rep = org.run_autonomous_phd_research();
    println!("    • Phase 9 PhD Discovery   : {}", phd_rep.thesis_abstract);
    println!("================================================================================");
}

fn run_repl() {
    println!("================================================================================");
    println!(" ALPHA 7 v1.3.0 INTERACTIVE LIVE REPL");
    println!(" Commands:");
    println!("   map                     - Render the 2D World Canvas");
    println!("   move <x> <y>            - Move Alpha 7's body & hands to (x, y)");
    println!("   saccade <x> <y>         - Move Alpha 7's eye fixation to (x, y)");
    println!("   teach <concept>         - Bind current 5-sense traits to <concept> (1-2 shot)");
    println!("   code <expr>             - Practice executing small code with Eyes & Hands");
    println!("   synthesize <target>     - Synthesize & verify code for a target result");
    println!("   sleep                   - Run Hippocampal-Neocortical sleep replay consolidation");
    println!("   exams                   - Sit all 8 held-out School Exams (Live L vs Null Twin N)");
    println!("   certify                 - Run the 6-Test Substrate Certification Suite");
    println!("   seal genome / genome    - Seal or audit & self-heal memories via Somatic Genetic Code");
    println!("   claim: <stmt>           - Evaluate a math/causal claim via independent self-proof");
    println!("   decode: <signal>        - Decode & Weber-Fechner normalize any numeric/hex/text stream");
    println!("   language exam           - Sit Phase 6 Language Course & Neural Broca Speech Exam");
    println!("   computer task           - Run Phase 7 Virtual Computer Screen/Mouse/Keyboard Lab Task");
    println!("   graduate                - Sit Phase 8 Middle/High School & University BSc Graduation");
    println!("   phd research            - Run Phase 9 Autonomous PhD Unseen Law Discovery Campaign");
    println!("   puzzle                  - Solve the 4-Step Key-Door-Vault tool puzzle on 2D Canvas");
    println!("   complete <phrase>       - Complete a sentence from Cortical Sequence Memory");
    println!("   memories                - List direct episodic memories formed with you");
    println!("   save [path] / load [p]  - Persist or restore Alpha 7's full brain state");
    println!("   quit / exit             - Exit REPL");
    println!("   Or type any question (e.g. 'compare cat and dog', 'what is', 'phd research')");
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
