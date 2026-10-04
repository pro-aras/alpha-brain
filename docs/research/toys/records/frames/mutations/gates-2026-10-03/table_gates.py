"""The mutant table for TOY C's tools/toys/frames/gates.py (one single textual replacement each; the NAMED test must be what catches it).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 20:31 +0400 — new (the relaunched lane). The predecessor's five survivors were not recorded as mutations (only their test logs), so they are re-derived here from its
# 18:29 NOTE (the manifest-check line, G4's control line, PLANT-BEATS-NULL-2, G6's cheat condition, G3's tolerance) and swept as a SUPERSET: every decision line, tolerance and law-pinned default of gates.py.
"""
TESTS = "tests.tools.test_toys_frames_gates"

G1_MAN = "TestG1.test_a_copy_changed_where_only_the_manifest_can_see_it_is_named"
G1_NOMAN = "TestG1.test_a_copies_directory_without_a_manifest_is_named"
G1_EACH = "TestG1.test_every_count_the_law_names_is_checked_one_at_a_time"
G1_OK = "TestG1.test_it_passes_when_every_count_is_the_expected_one_and_the_copies_hash_to_their_manifest"
G1_UNREAD = "TestG1.test_an_unreadable_copy_is_named_and_g1_says_not_ok"
G1_NOSRC = "TestG1.test_an_expected_source_missing_from_the_copies_is_named"
G1_SCENE_TOK = "TestG1.test_a_plant_token_found_in_the_real_scene_stream_is_named"
G1_ALPHA_TOK = "TestG1.test_a_plant_token_found_in_a_real_stream_is_named"
G2_DIS = "TestG2G3.test_g2_fails_when_the_real_store_disagrees_with_a_correct_stand_in"
G2_SIDIS = "TestG2G3.test_g2_fails_when_the_stand_in_disagrees_with_a_correct_real_store"
G2_WRONG = "TestG2G3.test_g2_fails_when_both_stores_agree_on_a_wrong_frame_set"
G3_TOL = "TestG2G3.test_g3_pins_its_tolerance_from_both_sides_for_every_compared_key"
G3_CNT = "TestG2G3.test_g3_fails_when_the_token_counts_disagree"
G3_TRACE = "TestG2G3.test_g3_fails_when_the_greedys_trace_has_a_problem"
G4_RULE = "TestG4.test_a_required_rule_failing_its_plant_gate_stops_g4_naming_the_stream_and_the_rule"
G4_B2 = "TestG4.test_a_plant_that_does_not_beat_null2_stops_g4_and_prints_both_numbers"
G4_CTRL = "TestG4.test_each_conjunct_of_the_parse_breaking_control_stops_g4"
G4_DEF = "TestG4.test_the_defaults_are_the_signed_streams"
G4_SEEDS = "TestG4.test_g4_draws_stream_a_from_replicate_seed_1_and_stream_b_from_alpha_seed_1"
G4_REAL = "TestG4.test_both_streams_every_required_rule_keeps_the_plant_and_both_controls_are_caught"
G5_STUB = "TestG5.test_g5_arithmetic_and_the_ceiling_boundaries_on_stubbed_clocks"
G5_DEF = "TestG5.test_g5_defaults_are_the_laws_ceilings"
G6_EACH = "TestG6.test_g6_each_failure_is_named_and_the_tolerances_are_pinned_from_both_sides"
G6_ARGS = "TestG6.test_g6_runs_the_laws_twenty_replicates_of_ten_thousand_moments"
RG_LAW = "TestRunGates.test_a_changed_law_text_stops_the_gates_before_anything_is_written"
RG_AGG = "TestRunGates.test_a_gate_that_fails_without_a_failure_list_is_named_by_its_label_and_the_record_says_not_passed"
RG_LOG = "TestRunGates.test_the_log_names_each_gate_in_order_and_every_failure"
RG_HDR = "TestRunGates.test_the_gates_record_carries_all_three_signed_shas_and_the_gate_mode"

MUTANTS = []


def M(name, old, new, expect, why, count=1):
    MUTANTS.append({"name": name, "old": old, "new": new, "expect": list(expect), "why": why, "count": count})


# ------------------------------------------------------------------------------------------------ G1
M("g1-manifest-verify-off", "bad = ST.verify_copies(copies, man)", "bad = []", [G1_MAN], "the manifest is read but never verified: a changed copy goes unseen")
M("g1-manifest-report-off", 'failures += [f"copy {rel}: no longer hashes to its manifest" for rel in bad]', "failures += []", [G1_MAN], "a mismatch is computed and dropped")
M("g1-manifest-missing-silent", 'failures.append("no MANIFEST.json in the copies directory")', "pass", [G1_NOMAN], "a copies directory without a manifest passes g1")
M("g1-copies-verified-ignores-bad", 'out["copies_verified"] = len(man) - len(bad)', 'out["copies_verified"] = len(man)', [G1_MAN], "the verified count ignores the bad copies")
M("g1-cmp-inverted", "    if got != want:", "    if got == want:", [G1_OK], "every count comparison inverted")
M("g1-alpha-moments-skip", '_cmp(failures, "alpha4.moments", c["moments"], ea["moments"])', "pass", [G1_EACH], "the total moment count is not compared")
M("g1-alpha-words-skip", '_cmp(failures, "alpha4.words", c["words"], ea["words"])', "pass", [G1_EACH], "the total word count is not compared")
M("g1-per-source-skip", '_cmp(failures, f"alpha4.{src}.{k}", got[k], v)', "pass", [G1_EACH], "the per-source counts are not compared")
M("g1-source-absent-silent", 'failures.append(f"alpha4.{src}: the source is absent")', "pass", [G1_NOSRC], "an expected source missing from the copies passes")
M("g1-scene-moments-skip", '_cmp(failures, "scene.moments", len(sc), es["moments"])', "pass", [G1_EACH], "the scene moment count is not compared")
M("g1-scene-per-moment-skip", '_cmp(failures, "scene.per_moment", dict(sorted(Counter(len(m.words) for m in sc).items())), es["per_moment"])', "pass", [G1_EACH], "the scene words-a-moment histogram is not compared")
M("g1-dax-skip", "if got != (SC.DAX_WORD,):", "if False:", [G1_EACH], "the «dax» scene is not checked at its index")
M("g1-says-skip", '_cmp(failures, "says (rows, yes, distinct frames)", got_says, tuple(expected["says"]))', "pass", [G1_EACH], "the says count is not compared")
M("g1-plant-check-off", "if any(t.values()):", "if False:", [G1_ALPHA_TOK], "a plant token found in a real stream is not a failure")
M("g1-plant-alpha-skip", '"ALPHA4": PL.plant_token_occurrences(a4),', '"ALPHA4": {},', [G1_ALPHA_TOK], "ALPHA4's plant tokens are not counted")
M("g1-plant-scene-skip", '"SCENE": PL.plant_token_occurrences(sc)}', '"SCENE": {}}', [G1_SCENE_TOK], "SCENE's plant tokens are not counted")
M("g1-streamerror-not-named", 'failures.append(f"a copy cannot be read: {e}")', "pass", [G1_UNREAD], "an unreadable copy is not named")
M("g1-streamerror-ok-true", 'return {"ok": False, "failures": failures, **out}', 'return {"ok": True, "failures": failures, **out}', [G1_UNREAD], "an unreadable copy reads ok")
M("g1-chi2-dropped", '"plant_tokens": tokens, "chi2": chi}', '"plant_tokens": tokens}', [G1_OK], "the chi-square fit is not carried")
M("g1-ok-const", 'return {"ok": not failures, "failures": failures, **out}', 'return {"ok": True, "failures": failures, **out}', [G1_EACH], "g1 always ok")
# ------------------------------------------------------------------------------------------------ G2
M("g2-drop-equality", 'ok = a == b and frames == [["blue", "ball"], ["green", "key"], ["red", "box"]]', 'ok = frames == [["blue", "ball"], ["green", "key"], ["red", "box"]]', [G2_DIS], "the stand-in is no longer compared with the real store")
M("g2-drop-frames-clause", 'ok = a == b and frames == [["blue", "ball"], ["green", "key"], ["red", "box"]]', "ok = a == b", [G2_WRONG], "the known store's frames are no longer checked")
M("g2-ok-const", 'ok = a == b and frames == [["blue", "ball"], ["green", "key"], ["red", "box"]]', "ok = True", [G2_DIS, G2_SIDIS, G2_WRONG], "g2 always ok")
M("g2-stand-in-reads-real", "b = find_frames(RL.StandIn(ms))", "b = find_frames(real)", [G2_SIDIS], "the stand-in store is never exercised")
M("g2-real-store-unwritten", 'real.write(0, np.zeros(2), np.zeros(2), "", 0.0, words_in_instant=list(m))', "pass", ["TestG2G3.test_g2_the_stand_in_store_equals_the_real_episodes_store"], "the real store stays empty")
# ------------------------------------------------------------------------------------------------ G3
M("g3-tol-1e-8", "worst < 1e-9 and not problems", "worst < 1e-8 and not problems", [G3_TOL], "the tolerance loosened ten-fold")
M("g3-tol-1e-3", "worst < 1e-9 and not problems", "worst < 1e-3 and not problems", [G3_TOL], "the tolerance loosened a million-fold")
M("g3-tol-1e-10", "worst < 1e-9 and not problems", "worst < 1e-10 and not problems", [G3_TOL], "the tolerance tightened ten-fold")
M("g3-problems-ignored", "worst < 1e-9 and not problems", "worst < 1e-9", [G3_TRACE], "the greedy's incremental-gain problems are ignored")
M("g3-key-G-dropped", 'for key in ("G", "bits0", "bitsF", "L"):', 'for key in ("bits0", "bitsF", "L"):', [G3_TOL], "G is not compared with its recount")
M("g3-key-bits0-dropped", 'for key in ("G", "bits0", "bitsF", "L"):', 'for key in ("G", "bitsF", "L"):', [G3_TOL], "bits0 is not compared")
M("g3-key-bitsF-dropped", 'for key in ("G", "bits0", "bitsF", "L"):', 'for key in ("G", "bits0", "L"):', [G3_TOL], "bitsF is not compared")
M("g3-key-L-dropped", 'for key in ("G", "bits0", "bitsF", "L"):', 'for key in ("G", "bits0", "bitsF"):', [G3_TOL], "L is not compared")
M("g3-abs-dropped", "worst = max(worst, abs(getattr(fast, key) - slow[key]))", "worst = max(worst, getattr(fast, key) - slow[key])", [G3_TOL], "a recount larger than the fast value goes unseen")
M("g3-counts-compare-off", 'if (fast.N, fast.K, fast.V, fast.n_held_words) != (slow["N"], slow["K"], slow["V"], slow["n_held_words"]):', "if False:", [G3_CNT], "the token counts are not compared")
M("g3-counts-no-penalty", "worst = max(worst, 1.0)", "worst = max(worst, 0.0)", [G3_CNT], "a count mismatch carries no penalty")
M("g3-cases-not-counted", "cases += 1", "cases += 0", ["TestG2G3.test_g3_the_fast_compressor_and_the_greedys_incremental_gain_equal_their_recounts"], "the compared cases are not counted")
M("g3-mdl-steps-dropped", 'steps += r.info["steps"]', "steps += 0", ["TestG2G3.test_g3_the_fast_compressor_and_the_greedys_incremental_gain_equal_their_recounts"], "the greedy's steps are not counted")
# ------------------------------------------------------------------------------------------------ G4
M("g4-rule-check-off", 'if not s["gates"][rule]["pass"]:', "if False:", [G4_RULE], "a required rule may fail its plant gate")
M("g4-beats2-off", 'if not s["plant_beats_null2"]:', "if False:", [G4_B2], "PLANT-BEATS-NULL-2 is not enforced")
M("g4-beats2-silent", 'failures.append(f"G4 stream {key}: PLANT-BEATS-NULL-2 fails (B {s[\'B\']:.2f}, q95 {s[\'null2_q95\']:.2f})")', "pass", [G4_B2], "the failure is dropped")
M("g4-ctrl-caught-dropped", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', 'if not (c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', [G4_CTRL], "`caught` is not required")
M("g4-ctrl-bytes-dropped", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', 'if not (c["caught"] and c["gate_honest"] and not c["gate_broken"]):', [G4_CTRL], "the plant's changed-bytes assertion is not required")
M("g4-ctrl-honest-dropped", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', 'if not (c["caught"] and c["bytes_changed"] and not c["gate_broken"]):', [G4_CTRL], "the honest gate need not pass")
M("g4-ctrl-broken-dropped", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"]):', [G4_CTRL], "the broken gate may pass")
M("g4-ctrl-or", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', 'if not (c["caught"] or c["bytes_changed"] or c["gate_honest"] or not c["gate_broken"]):', [G4_CTRL], "the four conditions are alternatives")
M("g4-ctrl-off", 'if not (c["caught"] and c["bytes_changed"] and c["gate_honest"] and not c["gate_broken"]):', "if False:", [G4_CTRL], "the control is not enforced")
M("g4-ctrl-silent", 'failures.append(f"G4 stream {key}: the gate\'s parse-breaking control is not caught ({c})")', "pass", [G4_CTRL], "the failure is dropped")
M("g4-ok-const", 'return {"ok": not failures, "failures": failures, "streams": streams, "draws": draws}', 'return {"ok": True, "failures": failures, "streams": streams, "draws": draws}', [G4_RULE], "g4 always ok")
M("g4-required-A-adds-web-s", '"A": ("WEB-H", "SENTENCE", "MDL-GREEDY")', '"A": ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")', ["TestG4.test_stream_a_as_signed_prints_web_s_failure_and_does_not_fail_the_gate"], "WEB-S required on the small-vocabulary stream")
M("g4-required-B-drops-web-s", '"B": ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")', '"B": ("WEB-H", "SENTENCE", "MDL-GREEDY")', [G4_REAL], "WEB-S not required on the ALPHA4-regime stream")
M("g4-mode-law", 'gates = VD.plant_gates(cond, "amend1")', 'gates = VD.plant_gates(cond, "law")', [G4_REAL], "the gate runs in the base text's mode")
M("g4-control-unplanted", '"control": PL.plant_gate_control(planted)}', '"control": PL.plant_gate_control(list(moments))}', [G4_REAL], "the control is built on the stream without its plants")
M("g4-default-scene-moments", "scene_moments: int = 3000", "scene_moments: int = 2999", [G4_DEF], "stream A is not the signed 3,000 moments")
M("g4-default-alpha-moments", "alpha_moments: int = 20_000", "alpha_moments: int = 19_999", [G4_DEF], "stream B is not the signed 20,000 moments")
M("g4-default-scene-every", 'scene_every: int = PL.PLANT_EVERY["SCENE"]', 'scene_every: int = PL.PLANT_EVERY["ALPHA4"]', [G4_DEF], "stream A's plant cadence is not SCENE's")
M("g4-default-alpha-every", 'alpha_every: int = PL.PLANT_EVERY["ALPHA4"]', 'alpha_every: int = PL.PLANT_EVERY["SCENE"]', [G4_DEF], "stream B's plant cadence is not ALPHA4's")
M("g4-replicate-seed", "np.random.default_rng([SC.SEED_ROOT, SC.G6_TAG, 1])", "np.random.default_rng([SC.SEED_ROOT, SC.G6_TAG, 2])", [G4_SEEDS], "stream A is not the signed replicate seed 1")
M("g4-default-draws", "def g4(draws: int = 100,", "def g4(draws: int = 99,", [G4_DEF], "the null draws are not the law's 100")
# ------------------------------------------------------------------------------------------------ G5
M("g5-cpu-gt-ge", "if pred_unit_min > cpu_ceiling_min:", "if pred_unit_min >= cpu_ceiling_min:", [G5_STUB], "a price exactly at the ceiling stops")
M("g5-rss-gt-ge", "if pred_rss_mb > rss_ceiling_mb:", "if pred_rss_mb >= rss_ceiling_mb:", [G5_STUB], "a memory exactly at the ceiling stops")
M("g5-rss-slope-dropped", 'pred_rss_mb = (b["peak_rss_kb"] + rss_slope * max(0, 100 - b["draws"])) / 1024.0', 'pred_rss_mb = b["peak_rss_kb"] / 1024.0', [G5_STUB], "memory is not extrapolated to 100 draws")
M("g5-peak-min", 'max(p["peak_rss_kb"] for p in pilots) / 1024.0', 'min(p["peak_rss_kb"] for p in pilots) / 1024.0', [G5_STUB], "the reported peak is the smaller pilot's")
M("g5-unit-factor", "pred_unit_min = 5 * pred_alpha / 60.0", "pred_unit_min = 4 * pred_alpha / 60.0", ["TestG5.test_the_pilot_extrapolates_cpu_linearly_in_the_draws_and_reports_peak_memory"], "the unit is priced as four ALPHA4 conditions, not five")
M("g5-default-cpu-ceiling", "cpu_ceiling_min: float = 40.0", "cpu_ceiling_min: float = 400.0", [G5_DEF], "the CPU ceiling is not the law's 40 min")
M("g5-default-rss-ceiling", "rss_ceiling_mb: float = 1024.0", "rss_ceiling_mb: float = 10240.0", [G5_DEF], "the memory ceiling is not 1 GB")
# ------------------------------------------------------------------------------------------------ G6
M("g6-violation-off", 'if r["violation"]:', "if False:", [G6_EACH], "a replicate above G_max + 20 is not a failure")
M("g6-cheat-caught-dropped", 'if not (cheat["caught"] and cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', 'if not (cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', [G6_EACH], "an uncaught cheat passes")
M("g6-cheat-bytes-dropped", 'if not (cheat["caught"] and cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', 'if not cheat["caught"]:', [G6_EACH], "a cheat that changed no bytes passes")
M("g6-cheat-or", 'if not (cheat["caught"] and cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', 'if not (cheat["caught"] or cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', [G6_EACH], "the cheat's two conditions are alternatives")
M("g6-cheat-off", 'if not (cheat["caught"] and cheat["bitsF_cheat"] != cheat["bitsF_honest"]):', "if False:", [G6_EACH], "the cheat is not enforced")
M("g6-sum-tol-loose", 'if abs(ex["sum_p"] - 1.0) >= 1e-12:', 'if abs(ex["sum_p"] - 1.0) >= 1e-6:', [G6_EACH], "the support-sum tolerance loosened")
M("g6-sum-tol-tight", 'if abs(ex["sum_p"] - 1.0) >= 1e-12:', 'if abs(ex["sum_p"] - 1.0) >= 1e-13:', [G6_EACH], "the support-sum tolerance tightened")
M("g6-entropy-tol-loose", 'abs(ex["entropy"] - 6.0774) >= 5e-5', 'abs(ex["entropy"] - 6.0774) >= 5e-3', [G6_EACH], "the entropy tolerance loosened")
M("g6-entropy-dropped", 'abs(ex["entropy"] - 6.0774) >= 5e-5 or ', "", [G6_EACH], "the entropy is not checked")
M("g6-hgl-tol-loose", 'abs(ex["h_given_length"] - 4.5774) >= 5e-5', 'abs(ex["h_given_length"] - 4.5774) >= 5e-3', [G6_EACH], "H(utterance | length) tolerance loosened")
M("g6-hgl-dropped", 'or abs(ex["h_given_length"] - 4.5774) >= 5e-5 ', "", [G6_EACH], "H(utterance | length) is not checked")
M("g6-hl-tol-loose", 'abs(ex["h_length"] - 1.5) >= 1e-12', 'abs(ex["h_length"] - 1.5) >= 1e-6', [G6_EACH], "H(length) tolerance loosened")
M("g6-hl-dropped", 'or abs(ex["h_length"] - 1.5) >= 1e-12 ', "", [G6_EACH], "H(length) is not checked")
M("g6-support-dropped", 'or ex["support_size"] != 90', "", [G6_EACH], "the support size is not checked")
M("g6-min-margin-max", '"min_margin": min(r["margin"] for r in reps)', '"min_margin": max(r["margin"] for r in reps)', [G6_EACH], "the printed margin is the largest, not the smallest")
M("g6-replicates-from-zero", "for k in range(1, replicates + 1)]", "for k in range(0, replicates)]", [G6_ARGS], "the replicates are 0-19, not the law's 1-20")
M("g6-default-replicates", "def g6(replicates: int = 20,", "def g6(replicates: int = 19,", [G6_ARGS], "not the law's twenty replicates")
M("g6-default-moments", "n_moments: int = 10_000) -> Dict[str, object]:\n    reps", "n_moments: int = 9_999) -> Dict[str, object]:\n    reps", [G6_ARGS], "not the law's 10,000 moments")
# ------------------------------------------------------------------------------------------------ run_gates
M("rg-law-check-off", "PR.check(RN.LAW_KEYS, root=prereg_root)", "pass", [RG_LAW], "the gates run against a changed law text")
M("rg-failure-label-off", '([] if r["ok"] else [f"{name} failed"])', "[]", [RG_AGG], "a gate that fails without a failure list leaves the record PASSED")
M("rg-passed-const", 'res.update({"passed": not failures,', 'res.update({"passed": True,', ["TestRunGates.test_a_failing_gate_writes_passed_false_and_exits_nonzero"], "the record always says passed")
M("rg-exit-const", "return 0 if not failures else 1", "return 0", ["TestRunGates.test_a_failing_gate_writes_passed_false_and_exits_nonzero"], "the exit code is always 0")
M("rg-log-status", "log(f\"[gates] {name}: {'OK' if r['ok'] else 'FAILED'}\")", 'log(f"[gates] {name}: OK")', [RG_LOG], "the log reads OK for a failed gate")
M("rg-log-failures-off", "    for f in failures:\n        log(f\"[gates] FAILURE: {f}\")", "    for f in failures:\n        pass", [RG_LOG], "the failures are not printed")
M("rg-header-prereg-dropped", '"header": {**PR.header(RN.LAW_KEYS), **RN.code_header(), "gate_mode": RN.GATE_MODE}', '"header": {**RN.code_header(), "gate_mode": RN.GATE_MODE}', [RG_HDR], "the record carries no signed sha")
M("rg-header-mode-dropped", '"header": {**PR.header(RN.LAW_KEYS), **RN.code_header(), "gate_mode": RN.GATE_MODE}', '"header": {**PR.header(RN.LAW_KEYS), **RN.code_header()}', [RG_HDR], "the record carries no gate mode")
M("rg-gate-order", '("g1", lambda: g1(copies, expected)), ("g2", g2),', '("g2", g2), ("g1", lambda: g1(copies, expected)),', [RG_LOG], "g2 runs before g1")

TABLE = {
    "module": "tools.toys.frames.gates",
    "file": "tools/toys/frames/gates.py",
    "tests": TESTS,
    "control_broken": {"old": 'failures.append(f"{label}: {got!r} != {want!r}")', "new": 'raise RuntimeError("BROKEN CONTROL")'},
    "mutants": MUTANTS,
}
