"""The mutant table for TOY C's tools/toys/frames/report.py (one single textual replacement each; the NAMED test must be what catches it).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:58 +0400 — new (the report's own sweep; the gates sweep's driver and table sit beside it in records/frames/mutations/).
"""
TESTS = "tests.tools.test_toys_frames_report_figures,tests.tools.test_toys_frames_report"
F = "TestFigures."
I = "TestInstrumentChecks."
P = "TestPredictions."
R = "TestReport."

T_COND = F + "test_the_conditions_table_has_a_row_per_condition_with_its_own_counts"
T_GAIN = F + "test_the_gain_section_prints_each_rules_numbers_from_its_records"
T_PLANT = F + "test_the_plant_section_prints_B_its_decomposition_and_each_rules_gate"
T_SHUF = F + "test_the_shuffle_section_prints_each_rules_quiet_reading"
T_CRIT = F + "test_the_criterion_section_prints_each_rules_null2_reading"
T_EYE = F + "test_the_eye_section_prints_each_rules_counts_and_the_per_frame_table"
T_EYETAB = F + "test_the_eye_table_marks_the_rules_that_keep_a_said_frame"
T_OVL = F + "test_the_overlaps_section_prints_each_conditions_jaccards"
T_SCENE = F + "test_the_scene_section_prints_the_ceiling_the_rows_the_oracle_and_each_rules_gradability"
T_NULLERR = F + "test_a_null_that_could_not_be_dealt_prints_its_error_never_a_blank"
T_GATES = F + "test_the_gates_section_prints_every_gate_figure_of_the_record"
T_HDR = F + "test_the_provenance_header_lines"
T_NORESULTS = F + "test_a_missing_results_file_is_an_error_not_a_blank"
T_NOGATES = F + "test_without_gates_the_provenance_says_so_and_lists_six_records"
T_CTRL = F + "test_the_g4_control_line_prints_each_of_its_six_fields"
T_FALLB = F + "test_fallbacks_are_summed_over_the_seeds_and_the_criterion_section_prints_a_changed_scene_beat"
T_MAIN = F + "test_main_defaults_read_the_runners_directory_and_write_the_committed_report_path"
T_TRACE = F + "test_the_mdl_trace_is_printed_when_the_run_has_one_and_cut_at_fifteen"
T_NL = F + "test_the_text_ends_with_one_newline_and_every_section_is_one_block"
T_PRISTINE = I + "test_the_pristine_fixture_reads_yes_on_every_check"
T_GRADE = I + "test_a_changed_grade_or_overlap_or_eye_block_in_results_reads_NO"
T_GRADE1 = I + "test_a_changed_verdict_in_a_record_reads_NO_on_the_grade_check_only"
T_EYE_NO = I + "test_a_changed_kept_set_reads_NO_on_the_eye_and_overlap_checks"
T_SCENE_NO = I + "test_a_changed_scene_record_reads_NO_on_the_scene_check"
T_SCENE_PL = I + "test_a_scene_row_missing_or_for_another_rule_or_with_another_margin_reads_NO"
T_LAW_G = I + "test_a_gates_record_with_another_law_text_reads_NO_for_gates_only"
T_LAW_C = I + "test_a_condition_record_with_another_law_text_reads_NO_for_that_record_only"
T_NOTAB = I + "test_without_a_per_frame_table_the_eye_check_says_it_was_not_run"
T_PC1 = P + "test_pc1_mdl_greedy_g_is_the_largest"
T_PC2 = P + "test_pc2_web_and_sentence_beat_their_nulls_with_g_below_mdl"
T_PC3 = P + "test_pc3_every_scene_g_is_a_tenth_of_g_max_at_most"
T_PC4 = P + "test_pc4_the_eye_splits_mdls_frames_into_grounded_and_function_word_pairs"
T_PC5 = P + "test_pc5_sentence_keeps_the_three_named_pairs_and_a_game_pair"
T_PC6 = P + "test_pc6_two_guesses_on_null2"

MUTANTS = []


def M(name, old, new, expect, why, count=1):
    MUTANTS.append({"name": name, "old": old, "new": new, "expect": list(expect), "why": why, "count": count})


# ------------------------------------------------------------------------------------------------ load and helpers
M("rp-sha-truncated", "return hashlib.sha256(path.read_bytes()).hexdigest()", "return hashlib.sha256(path.read_bytes()).hexdigest()[:63]", [R + "test_the_provenance_lists_every_record_file_with_its_sha256"], "a record's hash is cut")
M("rp-load-results-silent", 'raise ReportError(f"RESULTS.json is missing from {root.name}")', "pass", [T_NORESULTS], "a missing RESULTS.json is no ReportError")
M("rp-load-cond-silent", 'raise ReportError(f"{p.name}: the condition record is missing from {root.name}")', "continue", [R + "test_a_missing_condition_record_is_an_error_not_a_blank"], "a missing condition record is skipped")
M("rp-num-none", 'return "none" if x is None else f"{x:.{nd}f}"', 'return "-" if x is None else f"{x:.{nd}f}"', [T_GATES], "a missing number reads «-»")
M("rp-signed-plus", 'f"{x:+.{nd}f}"', 'f"{x:.{nd}f}"', [T_PLANT], "G({F*}) loses its sign")
M("rp-spread-mean-max", 'return f"{num(mean(xs), nd)} ({num(min(xs), nd)} to {num(max(xs), nd)})"', 'return f"{num(max(xs), nd)} ({num(min(xs), nd)} to {num(max(xs), nd)})"', [T_GAIN], "the mean is the maximum")
M("rp-spread-minmax-swap", "({num(min(xs), nd)} to {num(max(xs), nd)})", "({num(max(xs), nd)} to {num(min(xs), nd)})", [T_GAIN], "min and max swapped")
M("rp-spread-single-nd", "return num(xs[0], nd)", "return num(xs[0])", [T_GAIN], "a single value ignores its decimals")
M("rp-spread-empty", 'if not xs:\n        return "none"\n    if len(xs) == 1:\n        return num(xs[0], nd)', 'if not xs:\n        return "n/a"\n    if len(xs) == 1:\n        return num(xs[0], nd)', [T_GAIN], "an empty list reads n/a")
M("rp-counts-single-float", "return str(int(xs[0]))", 'return f"{xs[0]:.1f}"', [T_GAIN], "a count prints as a float")
M("rp-counts-mean-decimals", 'return f"{sum(xs) / len(xs):.1f} ({int(min(xs))} to {int(max(xs))})"', 'return f"{sum(xs) / len(xs):.2f} ({int(min(xs))} to {int(max(xs))})"', [T_GAIN], "the count mean has two decimals")
M("rp-counts-minmax-swap", '({int(min(xs))} to {int(max(xs))})', '({int(max(xs))} to {int(min(xs))})', [T_SHUF], "count min and max swapped (the gain block's WEB-S |F| has min == max in the fixture; the shuffle block's does not)")
M("rp-null-of-error", 'return {} if "error" in n else n', "return n", ["TestFigures"], "a null's error is read as a null: the fixture's own SCENE record carries one, so the shared setUpClass crashes (the whole class errors)")
M("rp-null-error-text", 'return str(n["error"]) if "error" in n else None', "return None", [T_NULLERR], "a null's error text is lost")
M("rp-kept-sets-pair", 'frozenset(tuple(f) for f in r["frames"])', 'frozenset(tuple(f)[:1] for f in r["frames"])', [T_EYETAB], "a kept pair is its first word")
# ------------------------------------------------------------------------------------------------ the instrument checks
M("rp-grade-mode", 'VD.grade(conds, res["mode"])', 'VD.grade(conds, "law")', [T_PRISTINE], "the run's grade is recomputed in the wrong mode")
M("rp-grade-law-key", 'again_law == res["grade_law"]', 'again_law == res["grade"]', [T_PRISTINE], "the base text's grade is compared with the run's")
M("rp-grade-true", 'return again == res["grade"], again_law == res["grade_law"]', "return True, True", [T_GRADE1, T_GRADE], "the grade check always passes")
M("rp-eye-true", 'return _roundtrip(VD.eye_reading(rep["conds"]["ALPHA4"], says)) == eye', "return True", [T_EYE_NO], "the eye check always passes")
M("rp-eye-yes-le", '"yes" if i < int(f["yes"]) else "no"', '"yes" if i <= int(f["yes"]) else "no"', [T_PRISTINE], "one confirmation too many")
M("rp-eye-says-plus", 'for i in range(int(f["says"])):', 'for i in range(int(f["says"]) + 1):', [T_PRISTINE], "one say too many")
M("rp-eye-none-off", "if frames is None:\n        return None", "if False:\n        return None", [T_NOTAB], "a missing table is not noticed")
M("rp-overlaps-true", 'return _roundtrip({name: VD.overlaps(rep["conds"][name]) for name in CONDITIONS}) == rep["results"]["overlaps"]', "return True", [T_EYE_NO, T_GRADE], "the overlap check always passes")
M("rp-overlaps-drop-last", 'for name in CONDITIONS}) == rep["results"]["overlaps"]', 'for name in CONDITIONS[:-1]}) == rep["results"]["overlaps"]', [T_PRISTINE], "a condition's overlaps are not recomputed")
M("rp-scene-len", 'if len(sb["rows"]) != len(recs_):\n        return False', "if False:\n        return False", [T_SCENE_PL], "a missing SCENE row is not noticed")
M("rp-scene-id", '(row["rule"], row["seed"]) != (r["rule"], r["seed"]) or ', "False or ", [T_SCENE_PL], "a row of another rule or seed is not noticed")
M("rp-scene-G", 'or row["G"] != r["gain"]["G"] or', "or False or", [T_SCENE_PL], "a row's G is not compared (a changed RECORD is also seen through the margin; the planted row G is what isolates this line)")
M("rp-scene-margin", 'abs(row["margin"] - (sb["G_max"] - r["gain"]["G"])) > 1e-9', 'abs(row["margin"] - (sb["G_max"] - r["gain"]["G"])) > 1e9', [T_SCENE_PL], "a row's margin is not compared")
M("rp-scene-oracle-margin", 'abs(o["margin"] - (sb["G_max"] - o["G"])) <= 1e-9 and', "True and", [T_SCENE_PL], "the oracle's margin is not compared")
M("rp-scene-recall", '_roundtrip(VD.oracle_recall(sc, SC.oracle_frames())) == o["recall"]', "True", [T_SCENE_PL], "the oracle's recall is not recomputed")
M("rp-law-key-dropped", 'for k in ("frames", "frames_amend1", "frames_amend2")]', 'for k in ("frames", "frames_amend1")]', [T_LAW_G], "AMENDMENT-2's text is not compared")
M("rp-law-conds", 'all(rep["conds"][name]["header"].get(k) == h.get(k) for k in keys)', "True", [T_LAW_C], "a condition's law text is not compared")
M("rp-law-gates-off", 'if rep["gates"] is not None:\n        out.append(("GATES.json"', 'if False:\n        out.append(("GATES.json"', [T_PRISTINE], "GATES.json is not flagged")
M("rp-law-gates-true", 'all(rep["gates"]["header"].get(k) == h.get(k) for k in keys)', "True", [T_LAW_G], "GATES.json's law text is not compared")
M("rp-yn-inverted", 'return "yes" if ok else "NO"', 'return "NO" if ok else "yes"', [T_PRISTINE], "yes and NO swapped")
# ------------------------------------------------------------------------------------------------ 0 provenance
M("rp-prov-sha", "code sha (RESULTS.json): {h.get('toys_git_sha')}", "code sha (RESULTS.json): {h.get('toys_tree_dirty')}", [T_HDR], "the code sha is the dirty flag")
M("rp-prov-dirty", "when the unit ran: {h.get('toys_tree_dirty')}", "when the unit ran: {h.get('toys_git_sha')}", [T_HDR], "the dirty flag is the sha")
M("rp-prov-signed-key", "{h.get(f'prereg_{k}_sha256')}\")\n    L.append(\"signed texts", "{h.get('prereg_frames_sha256')}\")\n    L.append(\"signed texts", [T_HDR], "the three signed texts print the first one")
M("rp-prov-code-one", "{'one' if len(code) == 1 else str(len(code)) + ' DIFFERENT'}", "{'one' if len(code) != 1 else str(len(code)) + ' DIFFERENT'}", [T_HDR], "one / DIFFERENT swapped")
M("rp-prov-gates-same", "({'the same' if gates['header'].get('toys_git_sha') == h.get('toys_git_sha') else 'DIFFERENT from the unit'})", "({'the same' if gates['header'].get('toys_git_sha') != h.get('toys_git_sha') else 'DIFFERENT from the unit'})", [T_HDR], "the same / DIFFERENT swapped")
M("rp-prov-gates-absent", 'if gates is None:\n        L.append("GATES.json: not present")', 'if False:\n        L.append("GATES.json: not present")', [T_NOGATES], "an absent GATES.json is not said (the predecessor's test is a substring test that section 1's own words also satisfy)")
# ------------------------------------------------------------------------------------------------ 1 gates
M("rp-g-passed", "GATES.json: passed {g.get('passed')} (failures:", "GATES.json: passed {g.get('failures')} (failures:", [T_GATES], "passed prints the failures")
M("rp-g-cpu", "{num(g.get('cpu_seconds'), 1)} CPU-s; peak RSS", "{num(g.get('cpu_seconds'), 2)} CPU-s; peak RSS", [T_GATES], "CPU seconds to two decimals")
M("rp-g-rss", "peak RSS {num((g.get('peak_rss_kb') or 0) / 1024.0, 0)} MB", "peak RSS {num((g.get('peak_rss_kb') or 0) / 1000.0, 0)} MB", [T_GATES], "kB / 1000")
M("rp-g1-words", "{g1['alpha4']['moments']} moments / {g1['alpha4']['words']} words", "{g1['alpha4']['words']} moments / {g1['alpha4']['moments']} words", [T_GATES], "moments and words swapped")
M("rp-g1-chi", "f\"{k} p {num((c2.get(k) or {}).get('p'), 3)}\" for k in (\"length\"", "f\"{k} p {num((c2.get(k) or {}).get('p'), 2)}\" for k in (\"length\"", [T_GATES], "χ² p to two decimals")
M("rp-g1-ok", "L.append(f\"G1 {'OK' if g1['ok'] else 'FAILED'}:", "L.append(f\"G1 {'FAILED' if g1['ok'] else 'OK'}:", [T_GATES], "G1 OK / FAILED swapped")
M("rp-g2-frames", "frames {g2.get('frames')}\")", "frames {g2.get('n_rows')}\")", [T_GATES], "G2 prints the row count as the frames")
M("rp-g3-fmt", "{g3.get('max_abs_diff'):.3g}", "{g3.get('max_abs_diff'):.4g}", [T_GATES], "G3's difference at four digits")
M("rp-g3-steps", "the greedy's {g3.get('mdl_steps')} steps over {g3.get('mdl_seeds')} seeds", "the greedy's {g3.get('mdl_seeds')} steps over {g3.get('mdl_steps')} seeds", [T_GATES], "G3 steps and seeds swapped")
M("rp-g4-tag", 'tag = "REQUIRED" if rule in required else "PRINTED, not required"', 'tag = "PRINTED, not required" if rule in required else "REQUIRED"', [T_GATES], "REQUIRED / PRINTED swapped (the predecessor's test cannot tell: WEB-H's own line carries the swapped tag too)")
M("rp-g4-pass", "gate {'PASS' if g['pass'] else 'FAIL'} — {tag}", "gate {'FAIL' if g['pass'] else 'PASS'} — {tag}", [T_GATES], "PASS / FAIL swapped")
M("rp-g4-header", "V {s.get('V')}, budget B = 2V = {s.get('budget')}; B = G({{F*}}) {num(s.get('B'))};", "V {s.get('budget')}, budget B = 2V = {s.get('V')}; B = G({{F*}}) {num(s.get('B'))};", [T_GATES, R + "test_the_small_vocabulary_failure_of_g4_stream_a_stays_printed"], "V and the budget swapped")
M("rp-g4-control", "the gate's parse-breaking control: caught {c.get('caught')}, bytes changed {c.get('bytes_changed')};", "the gate's parse-breaking control: caught {c.get('bytes_changed')}, bytes changed {c.get('caught')};", [T_CTRL], "caught and bytes changed swapped (both True in the hand-made record)")
M("rp-g5-slope", "num(g5.get('cpu_slope_per_draw'), 3)", "num(g5.get('cpu_slope_per_draw'), 2)", [T_GATES], "G5's slope to two decimals")
M("rp-g5-unit", "predicted unit {num(g5.get('predicted_unit_cpu_minutes'), 1)} CPU-min", "predicted unit {num(g5.get('predicted_unit_cpu_minutes'), 2)} CPU-min", [T_GATES], "G5's unit price to two decimals")
M("rp-g5-ceiling", "(ceiling {num(g5.get('cpu_ceiling_min'), 1)})", "(ceiling {num(g5.get('rss_ceiling_mb'), 1)})", [T_GATES], "G5's CPU ceiling is the memory one")
M("rp-g6-reps", "{len(g6.get('replicates', []))} replicates", "{len(g6.get('cheat', {}))} replicates", [T_GATES], "G6 counts the cheat's keys as replicates")
M("rp-g6-viol", "if r.get('violation'))}; the planted cheat", "if not r.get('violation'))}; the planted cheat", [T_GATES], "G6 counts the non-violations")
M("rp-g6-entropy", "entropy {num(ex.get('entropy'), 4)}", "entropy {num(ex.get('entropy'), 3)}", [T_GATES], "G6's entropy at three decimals")
# ------------------------------------------------------------------------------------------------ 2 conditions
M("rp-cond-every", "str(c.get('every') or '-')", "str(c.get('every'))", [T_COND], "a plain condition has `every` None")
M("rp-cond-peak", "{num((c.get('peak_rss_kb') or 0) / 1024.0, 0):>9}", "{num((c.get('peak_rss_kb') or 0) / 1000.0, 0):>9}", [T_COND], "kB / 1000")
M("rp-cond-words", "{str(c['n_train_words']) + '/' + str(c['n_held_words']):>20}", "{str(c['n_held_words']) + '/' + str(c['n_train_words']):>20}", [T_COND], "train and held words swapped")
# ------------------------------------------------------------------------------------------------ 3 plant
M("rp-plant-kept", 'kept = sum(1 for r in rs if r["plant"]["kept"])', 'kept = sum(1 for r in rs if not r["plant"]["kept"])', [T_PLANT], "kept counts the non-kept")
M("rp-plant-law", "{'pass' if lg['pass'] else 'fail'} (a reading)", "{'fail' if lg['pass'] else 'pass'} (a reading)", [T_PLANT], "the base text's reading inverted")
# EQUIVALENT, removed: rp-plant-A (`A = [r["plant"]["A"] ...]` -> `[r["gain"]["G"] ...]`): on a PLANT condition the record's gain IS the whole-set G on the plant stream, which is what plant["A"] is (plants.plant_reading and
# evaluate._record both call sc.gain(F).G on the same Scorer): the two lists are equal by construction.
M("rp-plant-C", 'C = [r["plant"]["C"] for r in rs if r["plant"]["C"] is not None]', 'C = [r["plant"]["C"] for r in rs if r["plant"]["C"] is None]', ["TestFigures"], "(C) keeps only the unkept: the shared setUpClass crashes on an empty C for the WEB-S of SCENE+PLANT (the whole class errors)")
M("rp-plant-side", 'pg = res["grade"][side][rule]["plant_gate"]', 'pg = res["grade"]["alpha4"][rule]["plant_gate"]', [T_PLANT], "SCENE+PLANT reads ALPHA4's gate")
M("rp-plant-b2", "mean {num(n2.get('mean'))}, sd {num(n2.get('sd'))}, q95", "mean {num(n2.get('sd'))}, sd {num(n2.get('mean'))}, q95", [T_PLANT], "NULL-2's mean and sd swapped")
M("rp-plant-first-scene", "SCENE {'gradable' if res['grade']['scene'][rule]['gradable'] else 'NOT GRADABLE'}\")", "SCENE {'gradable' if res['grade']['alpha4'][rule]['plant_gate']['pass'] else 'NOT GRADABLE'}\")", [T_PLANT], "SCENE's gradability read from ALPHA4")
# ------------------------------------------------------------------------------------------------ 4 shuffle, 5 gain, 6 criterion
M("rp-shuffle-quiet", "{'QUIET' if sq['quiet'] else 'LOUD'}", "{'LOUD' if sq['quiet'] else 'QUIET'}", [T_SHUF], "QUIET / LOUD swapped")
M("rp-shuffle-q95", "NULL-1 q95 {spread([null_of(r, 'null1').get('q95') for r in rs if null_of(r, 'null1')])}", "NULL-1 q95 {spread([null_of(r, 'null1').get('mean') for r in rs if null_of(r, 'null1')])}", [T_SHUF], "the q95 is the mean")
M("rp-gain-signp", "exact sign p {num(gn['exact_sign_p'], 4)}", "exact sign p {num(gn['exact_sign_p'], 3)}", [T_GAIN], "the sign p to three decimals")
M("rp-gain-perword", "spread([r['gain']['per_word'] for r in rs], 5)", "spread([r['gain']['per_word'] for r in rs], 4)", [T_GAIN], "per held-out word at four decimals")
M("rp-gain-L", "L {spread([r['gain']['L'] for r in rs])}; held adjacency", "L {spread([r['gain']['G'] for r in rs])}; held adjacency", [T_GAIN], "L is G")
M("rp-gain-adj", 'adj = [r["adjacency"]["train_adjacent_share"] for r in rs if r["adjacency"]["train_adjacent_share"] is not None]', 'adj = [r["adjacency"]["train_adjacent_share"] for r in rs if r["adjacency"]["train_adjacent_share"] is None]', [T_GAIN], "the adjacency shares keep only the missing")
M("rp-gain-seed-lines", 'if rule == "WEB-S":\n            for r in rs:\n                n1 = null_of(r, "null1")', 'if False:\n            for r in rs:\n                n1 = null_of(r, "null1")', [T_GAIN], "WEB-S's per-seed lines vanish")
M("rp-gain-seed-beats", "beats q95 {n1.get('beats_q95')}\")", "beats q95 {n1.get('q95')}\")", [T_GAIN], "a seed line prints q95 as beats")
M("rp-gain-anatomy-T", "T = D + C {spread([a['T'] for a in an])}", "T = D + C {spread([a['D'] for a in an])}", [T_GAIN], "T is D")
M("rp-gain-trace-cut", "for t in tr[:15]:", "for t in tr[:14]:", [T_TRACE], "the trace is cut at fourteen")
M("rp-gain-trace-head", "its first {min(15, len(tr))} picks", "its first {len(tr)} picks", [T_TRACE], "the header counts every step as printed")
M("rp-gain-trace-off", 'if mdl and mdl[0].get("info", {}).get("trace"):', "if False:", [T_TRACE], "no trace is ever printed")
M("rp-null-label", 'label = key.upper().replace("NULL", "NULL-")', 'label = key.upper()', [T_GAIN], "NULL1 instead of NULL-1")
M("rp-null-z", "z {spread([n['z'] for n in ns if n.get('z') is not None])}", "z {spread([n['sd'] for n in ns])}", [T_GAIN], "z prints sd")
M("rp-null-fallbacks", "fallbacks {sum(n.get('fallbacks', 0) for n in ns)}\")", "fallbacks {max(n.get('fallbacks', 0) for n in ns)}\")", [T_FALLB], "fallbacks take the maximum (the fixture's seeds all read 0)")
M("rp-crit-verdict", "CRITERION-MATTERS {rule}: {cr['verdict']} — {cr['n_pass']} of {cr['n']} seeds (need {cr['need']})", "CRITERION-MATTERS {rule}: {cr['verdict']} — {cr['n']} of {cr['n_pass']} seeds (need {cr['need']})", [T_CRIT], "n and n_pass swapped")
M("rp-crit-beats", "SCENE+PLANT {beats['SCENE+PLANT']}", "SCENE+PLANT {beats['ALPHA4+PLANT']}", [T_FALLB], "SCENE's plant-beats-null reads ALPHA4's (both True in the fixture)")
# ------------------------------------------------------------------------------------------------ 7 eye, 8 overlaps, 9 scene
M("rp-eye-base", "base rate {num(eye['base_rate'], 4)}", "base rate {num(eye['base_rate'], 3)}", [T_EYE], "the base rate at three decimals")
M("rp-eye-kept-rate", "{spread([r['rate_kept'] for r in er if r['rate_kept'] is not None], 3)} (says kept", "{spread([r['rate_not_kept'] for r in er if r['rate_not_kept'] is not None], 3)} (says kept", [T_EYE], "the kept rate is the not-kept one")
M("rp-eye-never", "frames it keeps that the cells never said {counts([r['kept_never_said'] for r in er])} of |F|", "frames it keeps that the cells never said {counts([r['said_kept'] for r in er])} of |F|", [T_EYE], "never-said prints said-kept")
M("rp-eye-pair-none", "if pair is None:\n                    flags.append", "if pair is not None:\n                    flags.append", [T_EYE], "a pair-less frame is treated as a pair")
M("rp-eye-webs", 'elif rule == "WEB-S":\n                    flags.append(f"{rule} {sum(1 for s in sets[rule] if pair in s)}/{len(sets[rule])}")', 'elif rule == "WEB-S":\n                    flags.append(f"{rule} {sum(1 for s in sets[rule] if pair in s)}/{len(sets[rule]) + 1}")', [T_EYETAB, T_EYE], "WEB-S's seed count is off by one")
# EQUIVALENT, removed: rp-eye-first (`sets[rule][0]` -> `sets[rule][-1]`): every rule but WEB-S has exactly one record per condition, so its first and its last record are the same.
M("rp-ovl-fmt", "f\"{k} {num(v, 3)}\" for k, v in sorted(ov.items())", "f\"{k} {num(v, 2)}\" for k, v in sorted(ov.items())", [T_OVL], "Jaccards to two decimals")
M("rp-scene-chi", "f\"{k} p {num((ch.get(k) or {}).get('p'), 3)} (n {(ch.get(k) or {}).get('n')})\"", "f\"{k} p {num((ch.get(k) or {}).get('p'), 2)} (n {(ch.get(k) or {}).get('n')})\"", [T_SCENE], "the SCENE χ² p to two decimals")
M("rp-scene-ceiling", "THE CEILING: G_max {num(sb['G_max'])} bits (bits(held | empty) {num(sb['bits0'])}", "THE CEILING: G_max {num(sb['bits0'])} bits (bits(held | empty) {num(sb['G_max'])}", [T_SCENE], "G_max and bits0 swapped")
M("rp-scene-viol", "{'VIOLATION' if r['violation'] else 'under G_max + 20'}", "{'under G_max + 20' if r['violation'] else 'VIOLATION'}", [T_SCENE], "VIOLATION inverted")
M("rp-scene-recall-fmt", "f\"{k} {num(v, 3)}\" for k, v in sorted(o[\"recall\"].items())", "f\"{k} {num(v, 2)}\" for k, v in sorted(o[\"recall\"].items())", [T_SCENE], "recall to two decimals")
M("rp-scene-grad", "L.append(f\"SCENE {rule}: {'gradable' if res['grade']['scene'][rule]['gradable'] else 'NOT GRADABLE'}", "L.append(f\"SCENE {rule}: {'NOT GRADABLE' if res['grade']['scene'][rule]['gradable'] else 'gradable'}", [T_SCENE, R + "test_a_not_gradable_verdict_is_printed_as_such"], "gradable inverted")
# ------------------------------------------------------------------------------------------------ 10 predictions and main
M("rp-pc1-ge", "holds = mdl >= max(G[\"WEB-H\"][0], mean_s, G[\"SENTENCE\"][0])", "holds = mdl > max(G[\"WEB-H\"][0], mean_s, G[\"SENTENCE\"][0])", [T_PC1, R + "test_the_predictions_are_read_mechanically"], "P-C1 strict")
M("rp-pc1-mean", 'mean_s = sum(G["WEB-S"]) / len(G["WEB-S"])', 'mean_s = max(G["WEB-S"])', [T_PC1], "WEB-S as its best seed")
M("rp-pc2-need", "need = -(-WEB_S_MIN * len(rs) // 10)", "need = -(-WEB_S_MIN * len(rs) // 5)", [T_PC2], "WEB-S needs 8 of 5")
M("rp-pc2-below", "below = r[\"gain\"][\"G\"] < mdl", "below = r[\"gain\"][\"G\"] <= mdl", [T_PC2], "SENTENCE equal to MDL counts as below")
M("rp-pc2-beat", 'b = bool(n1) and r["gain"]["G"] > n1["q95"]', 'b = bool(n1) and r["gain"]["G"] >= n1["q95"]', [T_PC2], "equal to the null counts as beating it (unreachable: equivalent unless equal)")
M("rp-pc3-frac", "P_C3_FRACTION = 0.10 ", "P_C3_FRACTION = 0.11 ", [T_PC3], "a tenth becomes 0.11")
M("rp-pc3-le", "ok3 = all(v <= P_C3_FRACTION for v in ratios.values())", "ok3 = all(v < P_C3_FRACTION for v in ratios.values())", [T_PC3], "exactly a tenth fails")
M("rp-pc3-gmax", "if gm is None or gm <= 0:", "if gm is None or gm < 0:", [T_PC3], "G_max = 0 is readable")
M("rp-pc4-says", "P_C4_MIN_SAYS = 5 ", "P_C4_MIN_SAYS = 4 ", [T_PC4], "four says are enough")
M("rp-pc4-rate", "P_C4_GROUNDED_RATE = 0.5\n", "P_C4_GROUNDED_RATE = 0.4\n", [T_PC4], "40 % is grounded")
M("rp-pc4-ge", 'f["yes"] / f["says"] >= P_C4_GROUNDED_RATE', 'f["yes"] / f["says"] > P_C4_GROUNDED_RATE', [T_PC4], "exactly half is not grounded")
M("rp-pc4-function", 'f["says"] >= P_C4_MIN_SAYS and f["yes"] == 0', 'f["says"] >= P_C4_MIN_SAYS and f["yes"] <= 1', [T_PC4], "one confirmation is still a function pair")
M("rp-pc4-both", 'out.append(("P-C4", "holds" if (kept_g and kept_f) else "does not hold",', 'out.append(("P-C4", "holds" if (kept_g or kept_f) else "does not hold",', [T_PC4], "either half is enough")
M("rp-pc5-pairs", 'P_C5_PAIRS = (("the", "letters"), ("a", "big"), ("to", "the"))', 'P_C5_PAIRS = (("the", "letters"), ("a", "big"))', [T_PC5], "one named pair dropped")
M("rp-pc5-colours", 'GAME_COLOURS = ("green", "yellow", "grey", "purple", "red", "blue")', 'GAME_COLOURS = ("green", "yellow", "grey", "red", "blue")', [T_PC5], "purple is no game colour")
M("rp-pc5-objects", 'GAME_OBJECTS = ("box", "key", "ball")', 'GAME_OBJECTS = ("box", "ball")', [T_PC5], "key is no game object")
M("rp-pc5-all", "ok5 = all(k for _p, k in named) and len(game_kept) >= 1", "ok5 = any(k for _p, k in named) and len(game_kept) >= 1", [T_PC5], "any named pair is enough")
M("rp-pc5-game", "ok5 = all(k for _p, k in named) and len(game_kept) >= 1", "ok5 = all(k for _p, k in named)", [T_PC5], "no game pair is needed")
M("rp-pc6-inside", 'inside = mdl <= n2["q95"]', 'inside = mdl < n2["q95"]', [T_PC6], "G equal to q95 is above the band")
M("rp-pc6-above", 'above = mdl > n2["q95"]', 'above = mdl >= n2["q95"]', [T_PC6], "G equal to q95 is above it")
M("rp-pc6-nearer", "all(v is not None and v < z[\"MDL-GREEDY\"] for v in others)", "all(v is not None and v <= z[\"MDL-GREEDY\"] for v in others)", [T_PC6], "a tie in z is nearer")
# ------------------------------------------------------------------------------------------------ render and main
M("rp-render-join", 'return "\\n\\n".join("\\n".join(p) for p in parts) + "\\n"', 'return "\\n".join("\\n".join(p) for p in parts) + "\\n"', [T_NL], "sections run together")
M("rp-render-end", 'return "\\n\\n".join("\\n".join(p) for p in parts) + "\\n"', 'return "\\n\\n".join("\\n".join(p) for p in parts) + "\\n\\n"', [T_NL], "two final newlines")
M("rp-render-order", "parts = [sec_provenance(rep), sec_gates(rep), sec_conditions(rep), sec_plant(rep),", "parts = [sec_gates(rep), sec_provenance(rep), sec_conditions(rep), sec_plant(rep),", [R + "test_every_section_is_present_in_order"], "sections 0 and 1 swapped")
M("rp-main-root", 'ap.add_argument("--root", default=str(RN.RUNS))', 'ap.add_argument("--root", default=str(ST.COPIES))', [T_MAIN], "the default root is the copies")
M("rp-main-out", 'ap.add_argument("--out", default=str(DEFAULT_OUT))', 'ap.add_argument("--out", default=str(DEFAULT_OUT.with_suffix(".bak")))', [T_MAIN], "the default output is another file")
M("rp-main-print", 'print(f"wrote {out.name}: {len(text)} bytes, sha256 {hashlib.sha256(text.encode()).hexdigest()}")', 'print(f"wrote {out.name}: {len(text)} bytes, sha256 {hashlib.sha256(text.encode()).hexdigest()[:8]}")', [T_MAIN], "the printed hash is cut")

TABLE = {
    "module": "tools.toys.frames.report",
    "file": "tools/toys/frames/report.py",
    "tests": TESTS,
    "control_broken": {"old": 'return "none" if x is None else f"{x:.{nd}f}"', "new": 'raise RuntimeError("BROKEN CONTROL")'},
    "mutants": MUTANTS,
}
