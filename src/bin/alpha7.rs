//! Alpha 7 Native Pure-Rust CLI, 2D World Explorer & Interactive REPL (Option 1 + 2 + 3)

use alpha7::Alpha7Organism;
use std::env;
use std::io::{self, Write};
use std::time::Instant;

fn run_demo() {
    println!("================================================================================");
    println!(" ALPHA 7 — 100% PURE RUST: SPARSE DENDRITIC BRAIN, 5-SENSE BODY, MOUTH & 2D WORLD");
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

    println!("\n[2] OPTION 3: INTERACTIVE 2D SPATIAL WORLD CANVAS & 5 SENSES");
    println!("{}", org.world.render_ascii());
    println!("    Legend: '@' = Alpha 7 Body | 'c' = Orange Cat (2,2) | 'C' = Black Cat (10,2)");
    println!("            'w' = White Cat (10,9) | 'd' = Brown Dog (2,9) | 'S' = Switch (6,2)");

    // Step 1: Move to Orange Cat at (2, 2) -> Exposure #1
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

    println!("\n[3] INFANT-LIKE 1-2 SHOT CONCEPT FORMATION ON THE 2D CANVAS");
    println!(
        "    • Exposure #1 at (2,2) Orange Cat : familiarity={:.2}, touched={} / {} neurons ({:.1} µs)",
        node1.familiarity,
        rep1.touched_neurons,
        org.neuron_count(),
        step_us
    );

    // Step 2: Move to Black Cat at (10, 2) -> Exposure #2
    org.world.move_agent_to(&mut org.body, 10, 2);
    let frame2 = org
        .world
        .sense_current_frame(&mut org.body, Some("another cat"));
    let (node2, _) = org.experience_concept("cat", &frame2, None, "user");
    let core_traits: Vec<String> = node2
        .core_invariants()
        .iter()
        .map(|t| t.trait_key.clone())
        .collect();
    let var_traits: Vec<String> = node2
        .variable_traits()
        .iter()
        .map(|t| t.trait_key.clone())
        .collect();
    println!(
        "    • Exposure #2 at (10,2) Black Cat : familiarity={:.2}",
        node2.familiarity
    );
    println!("    • Extracted Core Invariants       : {:?}", core_traits);
    println!("    • Variable Surface Traits         : {:?}", var_traits);

    println!("\n[4] OPTION 2: GROUNDED LANGUAGE & MOUTH ROAD");
    // Move to Unseen White Cat at (10, 9) and ask "what is this?"
    org.world.move_agent_to(&mut org.body, 10, 9);
    let ans_white_cat = org.converse("what is this?");
    println!("    • At Unseen White Cat (10,9) -> User: 'what is this?'");
    println!("      Alpha 7 Mouth: \"{}\"", ans_white_cat.spoken_response);

    // Move to Unseen Dog at (2, 9) and ask "what is this?"
    org.world.move_agent_to(&mut org.body, 2, 9);
    let ans_dog = org.converse("what is this?");
    println!("    • At Unseen Dog (2,9)        -> User: 'what is this?'");
    println!("      Alpha 7 Mouth: \"{}\"", ans_dog.spoken_response);

    println!("\n[5] PREDICTIVE PROCESSING, FAILED-PREDICTION ANALYSIS & GOAL SCENARIOS");
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

    // Goal-directed scenario rollout via conversation
    org.world.move_agent_to(&mut org.body, 6, 2);
    let goal_reply = org.converse("how to reach eyes:knowledge_gained?");
    println!("    • User Goal Query         : 'how to reach eyes:knowledge_gained?'");
    println!("      Alpha 7 Mouth: \"{}\"", goal_reply.spoken_response);

    // Failed prediction when power is unplugged
    let f_unplugged = org.body.build_frame(
        &["switch_visible", "toggle_lever"],
        &[],
        &["hard_plastic"],
        &["power_unplugged"],
        None,
    );
    let (eval_fail, _) = org.act_and_analyze(
        &f_unplugged,
        "press_switch",
        &["eyes:darkness_remains".to_string()],
        "user",
    );
    println!(
        "    • Failed Prediction Test  : {}",
        org.language.speak_prediction_outcome(&eval_fail)
    );

    println!("\n[6] SMALL CODING LEARNING & DIRECT USER EPISODIC MEMORIES");
    let code_ok = org.practice_coding("result = 6 * 7\nprint(result)", Some("multiply_code"));
    println!("    • Code Practice #1 (Valid): {}", code_ok.analysis_report);
    let code_err = org.practice_coding("result = 6 * * * 7", None);
    println!("    • Code Practice #2 (Typo) : {}", code_err.analysis_report);

    let thought_reply = org.converse("kitty cat multiply_code");
    println!("    • Grounded Thought        : \"{}\"", thought_reply.spoken_response);
    println!(
        "    • Total User Episodes     : {} autobiographical memories formed",
        org.knowledge_web.episodes.len()
    );
    println!("================================================================================");
}

fn run_repl() {
    println!("================================================================================");
    println!(" ALPHA 7 INTERACTIVE LIVE REPL (Option 1 + Option 2 Mouth + Option 3 2D World)");
    println!(" Commands:");
    println!("   map                     - Render the 2D World Canvas");
    println!("   move <x> <y>            - Move Alpha 7's body & hands to (x, y)");
    println!("   saccade <x> <y>         - Move Alpha 7's eye fixation to (x, y)");
    println!("   teach <concept>         - Bind current 5-sense traits to <concept> (1-2 shot)");
    println!("   code <expr>             - Practice executing small code with Eyes & Hands");
    println!("   memories                - List direct episodic memories formed with you");
    println!("   save [path] / load [p]  - Persist or restore Alpha 7's full brain state");
    println!("   quit / exit             - Exit REPL");
    println!("   Or type any question/sentence (e.g. 'what is this?', 'what is cat?')");
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
                    println!(
                        "Alpha 7: {}",
                        org.language.speak_perception(&frame, &recs)
                    );
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
    if args.iter().any(|a| a == "--repl" || a == "-i") {
        run_repl();
    } else {
        run_demo();
    }
}
