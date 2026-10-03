# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 20:35 +0400 (from `date`; the first draft of this line typed 20:41, six minutes AHEAD of the clock, and was corrected at once) — a MUTATION SWEEP of tools/brain/resit.py's ORIGIN-mode code (Part 5: the source copy, ITEMS-MATCH, dax_index_of; Part 6: run_origin, states_by_set,
# the R9 cross-check, check_rebuilt_dir) against tests/tools/test_resit_origin.py + test_resit_origin_copy.py. Each mutant breaks ONE thing the law relies on and NAMES the test(s) that must catch it
# (substring of the test name). A mutant is CAUGHT only when a NAMED test fails; CAUGHT-OTHER (a failure, but not the named one) and SURVIVED both exit 1 and name a gap.
# Run on a DETACHED COPY of the tree (never the watched tree), from that copy's root, through slot:  python3 -B <this file> [id-prefix ...]
# `<<NEVER>>` stands for an always-false literal, so no committed file holds one. The original is restored in a `finally` and its sha256 verified.
import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TARGET = Path("tools/brain/resit.py")
ORIG = TARGET.read_text()
SHA0 = hashlib.sha256(ORIG.encode()).hexdigest()
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:17 +0400 (from `date`) — TestEarlyLate (the pure classify_early_late tests, E1) lives in test_resit.py: the first runs of sweep 2 did not execute it, so N02 and N03 SURVIVED for the
# wrong reason (their named catching tests were never run); rerun with it included.
TESTS = ["tests.tools.test_resit_origin", "tests.tools.test_resit_origin_copy", "tests.tools.test_resit.TestEarlyLate"]

# (id, description, old, new, [named catching tests as substrings])
MUTATIONS = [
    # ---------------------------------------------------------------- Part 5: the source copy (R16), ITEMS-MATCH (R15), dax_index_of
    ("C01", "R16: the tape is cut after the FIRST set's end", "                    if n_end == len(sets):", "                    if n_end == 1:",
     ["the_copy_holds_the_tape_cut_after_the_last_end"]),
    ("C02", "R16: a torn tape line is kept", '                if not s.endswith("}"):\n                    torn_tape += 1\n                    continue', "                if <<NEVER>>:\n                    torn_tape += 1\n                    continue",
     ["a_torn_tape_tail"]),
    ("C03", "R16: a torn journal line is kept", '                if not s.endswith("}"):\n                    torn_journal += 1\n                    continue', "                if <<NEVER>>:\n                    torn_journal += 1\n                    continue",
     ["a_torn_last_line_of_the_journal"]),
    ("C04", "R16: the ask payloads are not copied", 'if r.get("sense") == "ask" or (r.get("sense") == "eye" and (meta.get("kind") == "sitting" or', 'if (r.get("sense") == "eye" and (meta.get("kind") == "sitting" or',
     ["the_copy_holds_the_tape_cut_after_the_last_end"]),
    ("C05", "R16: the sitting canvases' payloads are not copied", '(meta.get("kind") == "sitting" or (meta.get("kind") == "train" and meta.get("scene") == dax_index))', '((meta.get("kind") == "train" and meta.get("scene") == dax_index))',
     ["the_copy_holds_the_tape_cut_after_the_last_end", "the_non_sitting_eye_payloads"]),
    ("C06", "R16: the dax training canvas is not copied", '(meta.get("kind") == "train" and meta.get("scene") == dax_index)', '(meta.get("kind") == "train" and <<NEVER>>)',
     ["the_dax_training_canvas_is_copied"]),
    ("C07", "R16: EVERY training canvas is copied, not the dax one", '(meta.get("kind") == "train" and meta.get("scene") == dax_index)', '(meta.get("kind") == "train" and meta.get("scene") is not None)',
     ["the_dax_training_canvas_is_copied"]),
    ("C08", "R16: a payload is SYMLINKED into the life, never copied", "        shutil.copyfile(src, out)\n    truth_src", "        os.symlink(src, out)\n    truth_src",
     ["symlink"]),
    ("C09", "R16: truth/scene is not copied", '        shutil.copytree(truth_src, dest / "truth" / "scene")', "        pass",
     ["the_copy_holds_the_tape_cut_after_the_last_end"]),
    ("C10", "R16: only GENOME.genome is copied, not the GENOME.v<n> files the epoch rows name", 'for g in [root / "GENOME.genome"] + sorted(root.glob("GENOME.v*.genome")):', 'for g in [root / "GENOME.genome"]:',
     ["genome_v", "epoch_genomes", "genomes_the_epoch"]),
    ("C11", "R16: the row's source_copy_sha256 is the hash of nothing", '"source_copy_sha256": sha256_bytes(manifest.encode("utf-8")),', '"source_copy_sha256": sha256_bytes(b""),',
     ["the_manifest_hash_equals"]),
    ("C12", "R16: the re-verification compares sizes only, not bytes", "        elif f.stat().st_size != size or sha256_file(f) != h:", "        elif f.stat().st_size != size:",
     ["one_byte_flipped_in_the_copy"]),
    ("C13", "R16: the re-verification ignores a file the MANIFEST does not list", '    for rel in sorted(present - set(listed)):\n        problems.append(f"{rel}: a file the MANIFEST does not list")', '    for rel in []:\n        problems.append(f"{rel}: a file the MANIFEST does not list")',
     ["an_added_or_removed_file"]),
    ("C14", "R16: the re-verification does not compare the MANIFEST's text with the row's sha256", '    if sha256_bytes(text.encode("utf-8")) != expected_sha256:\n        problems.append(', "    if <<NEVER>>:\n        problems.append(",
     ["manifest_text", "a_rewritten_manifest", "manifest_rewritten"]),
    ("C15", "R16: a destination that is not empty is accepted", "    if dest.exists() and any(dest.iterdir()):\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["a_destination_that_is_not_empty"]),
    ("C16", "R4 c: an incomplete sitting is not skipped", "    if cut_seq is None:\n        raise Skipped(", "    if <<NEVER>>:\n        raise Skipped(",
     ["sittings_are_not_complete"]),
    ("C17", "R15: ITEMS-MATCH does not compare the ask digest", 'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     ["plant_a"]),
    ("C18", "R15: ITEMS-MATCH does not compare the canvas digest", 'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "world_scene_line_sha": world_line_sha}',
     ["plant_f", "canvas_replaced"]),
    ("C19", "R15: ITEMS-MATCH does not compare the WORLD scene line", 'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"]}',
     ["plant_d"]),
    ("C20", "R15: ITEMS-MATCH does not count the asks", 'got = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     'got = {"n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha}',
     ["plant_e"]),
    ("C21", "R15: the canvas bytes are not checked against the row's sha on the copy scan", "            cscan = scan_items(src, copy_decl, verify_canvas_bytes=True)", "            cscan = scan_items(src, copy_decl, verify_canvas_bytes=False)",
     ["plant_c"]),
    ("C22", "v4 1.6: the dax index is the file's constant, not constant minus one", "    return int(m.group(1)) - 1", "    return int(m.group(1))",
     ["DAX_SCENE_minus_one", "plant_a_different_constant"]),
    ("C23", "v4 1.6: a missing world.py is a raw file error, not a refusal", "    try:\n        text = path.read_text()\n    except OSError as e:\n        raise Refused(", "    try:\n        text = path.read_text()\n    except FileNotFoundError as e:\n        raise RuntimeError(",
     ["without_world_py"]),
    # ---------------------------------------------------------------- Part 6: ORIGIN mode
    ("O01", "R4 g: the written-once rule is checked only at the END (the children run for nothing)", "        if (out / \"ORIGIN.json\").exists():\n            raise Refused(f\"{out / 'ORIGIN.json'} exists", "        if <<NEVER>>:\n            raise Refused(f\"{out / 'ORIGIN.json'} exists",
     ["r4g_a_second_origin"]),
    ("O02", "R15: ITEMS-MATCH is never called", "            items_match(cscan, pin, world_scene_line_sha(copy_text))", "            pass",
     ["plant_a", "plant_d"]),
    ("O03", "R4 k: a restart-divergent journal is let through", "        require_no_divergent(dup)\n        sets = {s: v for s, v in cscan", "        sets = {s: v for s, v in cscan",
     ["r4k"]),
    ("O04", "R9: an EARLY difference does not refuse", '        if r9["refusing"] and r9["early_diff_count"]:', "        if <<NEVER>>:",
     ["r9_a_planted_state_difference_refuses"]),
    ("O05", "R9: a fallback origin REFUSES on a difference", "refusing=(a.origin_kind == \"rebuilt\"))", "refusing=True)",
     ["r9_is_a_reading_for_a_fallback"]),
    ("O06", "R9: the comparison masks the coordinates (seq, eye_seq, at, moment) as well as the hash", "        same = rows_equal(r, life)\n        s = set_of.get(seq)", '        same = rows_equal(r, life, ignore=("hash", "seq", "eye_seq", "at", "moment"))\n        s = set_of.get(seq)',
     ["any_key_but_hash"]),
    ("O07", "R9: the comparison masks the answer's own detail, fix and hyps", "        same = rows_equal(r, life)\n        s = set_of.get(seq)", '        same = rows_equal(r, life, ignore=("hash", "fix", "hyps", "detail"))\n        s = set_of.get(seq)',
     ["any_key_but_hash"]),
    ("O08", "R16: the copy's re-verification at the end of the run is never acted on", '        row["source_copy"]["verify"] = ver\n        if ver:', '        row["source_copy"]["verify"] = ver\n        if <<NEVER>>:',
     ["source_copy_changed_during_the_run"]),
    ("O09", "v4 1.2: the origin's GRADE child is given the life's genome, not the pinned one", '"items_root": str(src), "journal": str(run_dir / "answers.jsonl"), "scored": str(a.scored), "label": a.stamp,\n                 "genome": str(items_genome),',
     '"items_root": str(src), "journal": str(run_dir / "answers.jsonl"), "scored": str(a.scored), "label": a.stamp,\n                 "genome": str(src / "GENOME.genome"),',
     ["grader_is_the_pinned_configuration"]),
    ("O10", "v4 1.6: the ANSWER child reads the live root, not the copy", 'spec = {"code": str(code), "items_root": str(src), "tape_decl": copy_decl, "states": entries,', 'spec = {"code": str(code), "items_root": str(root), "tape_decl": copy_decl, "states": entries,',
     ["children_read_the_source_copy"]),
    ("O11", "v4 1.6: the GRADE child reads the live root, not the copy", 'gspec = {"grader_code": str(a.grader_code), "items_root": str(src),', 'gspec = {"grader_code": str(a.grader_code), "items_root": str(root),',
     ["children_read_the_source_copy"]),
    ("O12", "v4 1.6: the life's own grade reads the live journal, not the copy's", 'lspec = {**gspec, "journal": str(src / "journal"),', 'lspec = {**gspec, "journal": str(root / "journal"),',
     ["children_read_the_source_copy"]),
    ("O13", "R4 d: the rebuilt state's sidecar is never checked (read as given)", 'side = check_rebuilt_dir(by_set[s], s, begins[s], src / "tape")',
     'side = json.loads((by_set[s] / "ORIGIN.json").read_text()) if (by_set[s] / "ORIGIN.json").is_file() else {"state_hash": None}',
     ["r4d", "genome_whose_sha", "rebuild_of_another_tape", "bare_state_pair"]),
    ("O14", "§1.2: EYE-CHANGED against the grader is never evaluated for the origin", "eyes = {nm: eye_changed(ln, origin=first_lines, grader=grader_lines) for nm, ln in set_lines.items()}", "eyes = {nm: eye_changed(ln, origin=first_lines, grader=None) for nm, ln in set_lines.items()}",
     ["eye_changed_against_the_grader"]),
    ("O15", "§1.2: EYE-CHANGED between the origin's own sets is never evaluated", "eyes = {nm: eye_changed(ln, origin=first_lines, grader=grader_lines) for nm, ln in set_lines.items()}", "eyes = {nm: eye_changed(ln, origin=None, grader=grader_lines) for nm, ln in set_lines.items()}",
     ["eye_changed_between_the_sets"]),
    ("O16", "R8: the origin is not a series line", "        write_origin(out, row)\n        append_series(out, row)", "        write_origin(out, row)",
     ["origin_is_the_first_series_line"]),
    ("O17", "R8: ORIGIN.json is never written", "        write_origin(out, row)\n        append_series(out, row)", "        append_series(out, row)",
     ["a_rebuilt_origin_is_written_once"]),
    ("O18", "R9: the act census is not computed", '        r9["act_census"] = act_census(js["brain_rows"], windows)', '        r9["act_census"] = {}',
     ["the_acts_inside_each_sitting_are_censused"]),
    ("O19", "S3: the fallback label is dropped", '            row["label"] = FALLBACK_LABEL', '            row["label"] = ""',
     ["is_labelled"]),
    ("O20", "R4 i: a fallback without the seat's reason is accepted", '        if reason is None or not str(reason).strip():\n            raise Refused("an origin from a fallback copy needs', '        if <<NEVER>>:\n            raise Refused("an origin from a fallback copy needs',
     ["r4i"]),
    ("O21", "R4 h: an origin from state/prev is accepted without the fallback kind", '    if from_state_prev and origin_kind != "fallback_copy":', "    if <<NEVER>>:",
     ["r4h"]),
    ("O22", "R9: every item is EARLY (the fail-closed classification is off)", "        early = not (lo < hi)", "        early = True",
     ["a_late_item_that_differs", "no_tested_early_item"]),
    ("O23", "R9: LATE items are all counted in the first third", "    return [list(items[i * n // 3:(i + 1) * n // 3]) for i in range(3)]", "    return [list(items), [], []]",
     ["by_thirds"]),
    # edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:30 +0400 (from `date`) — O24/O25's named tests are the two planted-aggregate tests (their names carry «aggregate_disagrees», not «partition»): sweep 2 read them CAUGHT-OTHER on the
    # wrong substring; the names are corrected here and the two mutants rerun.
    ("O24", "R6: the origin's partition is not required", '        require_partition(row["partition"])\n        lrecords', "        lrecords",
     ["a_grade_whose_aggregate_disagrees"]),
    ("O25", "R6: the life's own partition is not required", "        require_partition(lpart)", "        pass",
     ["a_life_own_grade_whose_aggregate_disagrees"]),
    ("O26", "R4 k: restart duplicates are not counted in the row", '        row["restart_duplicates"] = dup["restart_duplicates"]\n        require_no_divergent(dup)', '        row["restart_duplicates"] = 0\n        require_no_divergent(dup)',
     ["equal_duplicate", "restart_duplicates"]),
    ("O27", "§5: the origin row's begin seq is the LAST set's, not the fresh one's", '        row["begin_seq_fresh"] = begins[ordered[0]]', '        row["begin_seq_fresh"] = begins[ordered[-1]]',
     ["a_rebuilt_origin_is_written_once"]),
    ("O28", "§4.6: the origin's learned count is read from the LAST set's state, not the fresh-begin one", '        row["origin_n_learned_fresh_begin"] = int(smeta[fresh_name]["n_learned"])', '        row["origin_n_learned_fresh_begin"] = int(smeta[ordered[-1] if a.origin_kind == "rebuilt" else "*"]["n_learned"])',
     ["n_learned_of_the_fresh_begin", "a_rebuilt_origin_is_written_once"]),
    ("O29", "R4 j: the grader pin is not checked before the source copy", '        row["grader"] = {**ginfo, "pin": check_grader_pin(out, ginfo, write=False)}\n        # the SOURCE COPY', '        row["grader"] = {**ginfo, "pin": "absent"}\n        # the SOURCE COPY',
     ["grader_pin"]),
    ("O30", "S2: a bare dir is not given to every set (only the first)", "        return {s: bare[0] for s in ordered}", "        return {ordered[0]: bare[0]}",
     ["a_bare_dir_serves_every_set"]),
    ("O31", "S2: a set named twice is let through", "    if twice:\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["every_other_assignment_is_refused_by_name"]),
    ("O32", "R4 d: the sidecar's begin seq is not compared with the life's", "    if int(side.get(\"begin_seq\", -1)) != int(begin_seq):\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["rebuild_of_another_tape"]),
    ("O33", "R4 d: the sidecar's tape digest is not compared with the life's rows", "    if side.get(\"tape_digest\") != dig:\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["rebuild_of_another_tape"]),
    ("O34", "R4 d: the sidecar's genome sha is not compared", "    if sha256_file(d / \"GENOME.in-force.genome\") != side.get(\"genome_in_force_sha\"):\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["genome_whose_sha"]),
    ("O35", "R4 d: the sidecar's SET is not compared", "    if side.get(\"set\") != setname:\n        raise Refused(", "    if <<NEVER>>:\n        raise Refused(",
     ["bare_dir_with_a_sidecar", "set_name"]),
    ("O36", "§1.1 S3: a fallback state is taken whole (the life's epoch rule is the gate rule)", '            gf = genome_in_force(src, js["epochs"], upto_seq=int(st["last_seq"]))', '            gf = genome_in_force(src, js["epochs"], before_seq=1)',
     ["an_epoch_adopted_before_the_states_last_seq", "an_epoch_adopted_after_the_states_last_seq"]),
    # ---------------------------------------------------------------- the verifier's finding on c887b50 (erratum E1), the omission checks, the symlink check — second sweep, on the final bytes
    ("N01", "E1: end is not a structural form (only begin is)", 'STRUCTURAL_FORMS = ("begin", "end")', 'STRUCTURAL_FORMS = ("begin",)',
     ["begin_and_end_alone_test_nothing", "r9_every_early_item_equals"]),
    ("N02", "E1: begin and end count as tested EARLY items in classify_early_late", 'if early and row.get("form") not in STRUCTURAL_FORMS:', "if early:",
     ["n_early_and_n_early_tested_are_both_printed", "a_set_whose_only_early_item_is_begin"]),
    ("N03", "E1: the UNTESTED note is never set in classify_early_late", 'd["note"] = UNTESTED_NOTE if d["untested"] else ""', 'd["note"] = ""',
     ["a_set_whose_only_early_item_is_begin", "begin_and_end_alone_test_nothing"]),
    ("N04", "E1: r9_reading leaves out NOT A PASS", " — NOT A PASS for them: their begin state", " — for them: their begin state",
     ["one_untested_set_leads_the_line", "no_tested_early_item_reads_untested_never_a_pass"]),
    ("N05", "E1: r9_reading never lists an untested set", '    untested = [s for s, v in by_set.items() if v["untested"]]\n', "    untested = []\n",
     ["one_untested_set_leads_the_line", "every_untested_set_is_named"]),
    ("N06", "E1: the origin row carries no r9_reading", '        row["r9_reading"], row["r9_untested_sets"] = r9_reading(r9)', '        row["r9_reading"], row["r9_untested_sets"] = "", []',
     ["no_tested_early_item_reads_untested_never_a_pass", "r9_every_early_item_equals"]),
    ("N07", "E1: RESIT.md's note never carries the reading", ' or r.get("r9_reading") or ""', ' or ""',
     ["no_tested_early_item_reads_untested_never_a_pass"]),
    ("N08", "R16: the symlink check is removed from the re-verification", "        if q.is_symlink():\n            problems.append(", "        if <<NEVER>>:\n            problems.append(",
     ["no_kept_file_is_a_symlink"]),
    ("N09", "omissions: require_all_answered is never called", '        require_all_answered(ameta, cscan["n_asks"])', "        pass",
     ["answered_fewer_asks"]),
    ("N10", "omissions: require_all_answered ignores a count mismatch", "    if unanswered or answered != int(n_asks):", "    if unanswered:",
     ["answered_fewer_asks"]),
    ("N11", "omissions: the R9 refusal on life rows with no origin row is removed", '        if r9["refusing"] and r9["life_rows_not_resat"]:', "        if <<NEVER>>:",
     ["answered_one_ask_twice"]),
    ("N12", "omissions: a life row of a sitting ask with no origin row is not counted", "not_resat = sorted(seq for seq, s in set_of.items() if s is not None and seq in life_rows and seq not in origin_seqs)", "not_resat = []",
     ["an_origin_row_missing_for_a_life_row"]),
    ("N13", "omissions: the reading line hides the unmatched counts", '    late = late + "".join(f"; {g}" for g in gaps)', "    late = late",
     ["reading_line_says_it_whenever"]),
    # edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:40 +0400 (from `date`) — the verifier's ruling on the reading line: TESTED and STRUCTURAL rows counted apart (two new mutants for the code that does it).
    ("N14", "E1 counts: a structural begin/end row is counted among the TESTED rows in r9_cross_check", "            if form_of.get(seq) in STRUCTURAL_FORMS:\n                struct_total += 1", "            if <<NEVER>>:\n                struct_total += 1",
     ["tested_and_structural_early_rows_are_counted_apart", "every_set_tested_and_exact_reads_exact_with_the_tested"]),
    ("N15", "E1 counts: the line's TESTED denominator is the merged EARLY total", '    tt, te = int(r9["early_tested_total"]), int(r9["early_tested_equal"])', '    tt, te = int(r9["early_total"]), int(r9["early_equal"])',
     ["every_set_tested_and_exact_reads_exact_with_the_tested", "the_two_counts_move_apart"]),
]


def run_tests() -> tuple:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONPATH": ".", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
    p = subprocess.run([sys.executable, "-B", "-u", "-m", "unittest", *TESTS], capture_output=True, text=True, env=env)
    names = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", p.stderr, re.M)))
    tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
    return p.returncode, names, tail


def main() -> int:
    survived, other = [], []
    only = tuple(sys.argv[1:])
    n = 0
    try:
        for mid, name, old, new, expected in MUTATIONS:
            if only and not mid.startswith(only):
                continue
            old, new = old.replace("<<NEVER>>", "False"), new.replace("<<NEVER>>", "False")
            assert ORIG.count(old) == 1, f"{mid}: the anchor is not unique ({ORIG.count(old)})"
            mutated = ORIG.replace(old, new)
            assert mutated != ORIG, f"{mid}: the mutation must change the bytes"
            TARGET.write_text(mutated)
            t0 = time.time()
            rc, names, tail = run_tests()
            n += 1
            if rc == 0:
                verdict = "SURVIVED"
                survived.append(f"{mid} {name}")
            elif any(e in nm for nm in names for e in expected):
                verdict = "CAUGHT"
            else:
                verdict = "CAUGHT-OTHER"
                other.append(f"{mid} {name} (failed: {names[:4]}; named: {expected})")
            shown = ", ".join(nm.replace("test_", "", 1)[:48] for nm in names[:3]) + (" …" if len(names) > 3 else "")
            print(f"{verdict:12s} {mid} {name}  [{tail}; {len(names)} test(s): {shown}]  ({time.time() - t0:.0f} s)", flush=True)
    finally:
        TARGET.write_text(ORIG)
        sha1 = hashlib.sha256(TARGET.read_text().encode()).hexdigest()
        print(f"restored: sha256 {'equal' if sha1 == SHA0 else 'DIFFERENT'} ({SHA0[:16]})", flush=True)
    print(f"mutants run: {n}; survivors: {survived}")
    print(f"caught by a test other than the named one: {other}")
    return 1 if (survived or other) else 0


if __name__ == "__main__":
    sys.exit(main())
