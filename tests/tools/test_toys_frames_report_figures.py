"""Tests for TOY C's report, second file: EVERY printed figure against the record it came from, the instrument checks that catch a changed record, and the predictions read one condition at a time.
Written FIRST, STAGE 6b (red against the first draft of report.py: counts printed as floats, no eye / overlaps / SCENE checks, no per-source signed-text flags, a null's error hidden).

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 21:48 +0400 — STAGE 6b. The first file (test_toys_frames_report.py, the predecessor's) pins the report's skeleton and a handful of strings; the RESULT quotes every figure from this
# report, so each section is checked here against the JSON records with the test's OWN statement of the formatting (a swapped field, a wrong mean, a dropped seed, a count read from the wrong record all fail). The instrument checks
# (RESULTS.json's grade, eye reading, overlaps and SCENE rows equal what the five condition records give) are planted: each plant changes a record's bytes (asserted) and must make exactly its check read NO.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.toys.common import prereg as PR
from tools.toys.frames import report as RP
from tools.toys.frames import run as RN
from tools.toys.frames import streams as ST

from tests.tools.test_toys_frames_report import gates_json
from tests.tools.test_toys_frames_run import make_copies

RULES = ("WEB-H", "WEB-S", "SENTENCE", "MDL-GREEDY")
COND_FILES = ("ALPHA4", "ALPHA4+PLANT", "ALPHA4+SHUFFLE", "SCENE", "SCENE+PLANT")
D: Path


def setUpModule():
    global D
    D = Path(tempfile.mkdtemp())
    make_copies(D / "copies")
    RN.run_unit(D / "copies", D / "runs", draws=5, seeds=(1, 2), require_gates=False)
    g = gates_json()
    g["header"] = {**g["header"], **PR.header(RN.LAW_KEYS)}                                          # a real GATES.json carries the three signed shas (the hand-made one of the first file does not)
    g["g3"]["max_abs_diff"] = 3.14159265e-13                                                         # prints as 3.14e-13 under «.3g» (the first file's 3.0e-13 cannot tell .3g from .4g)
    (D / "runs" / "GATES.json").write_text(json.dumps(g))


def tearDownModule():
    shutil.rmtree(D)


def rj(name, root=None):
    return json.loads(((root or D / "runs") / f"{name}.json").read_text())


def sections(text):
    out = {}
    for block in text.split("\n\n"):
        m = re.match(r"== (\d+) · ", block)
        if m:
            out[int(m.group(1))] = block
    return out


def fmt(x, nd=2):
    return f"{x:.{nd}f}"


def spread(xs, nd=2):
    """the test's OWN statement of «mean (min to max)»: one value alone, none when there is none."""
    xs = list(xs)
    if not xs:
        return "none"
    if len(xs) == 1:
        return fmt(xs[0], nd)
    return f"{fmt(sum(xs) / len(xs), nd)} ({fmt(min(xs), nd)} to {fmt(max(xs), nd)})"


def counts(xs):
    """a count a record carries: an integer when there is one record, «mean (min to max)» over seeds."""
    xs = list(xs)
    if len(xs) == 1:
        return str(int(xs[0]))
    return f"{sum(xs) / len(xs):.1f} ({int(min(xs))} to {int(max(xs))})"


def by_rule(cond, rule):
    return [r for r in cond["records"] if r["rule"] == rule]


def block(sec, start, stop_prefix):
    """the lines of `sec` from the first line starting `start` up to (not including) the next line starting `stop_prefix`, or the end."""
    lines = sec.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith(stop_prefix)), len(lines))
    return lines[i:j]


def null_fragment(rs, key, label):
    ns = [r[key] for r in rs if r.get(key) and "error" not in r[key]]
    errs = [r[key]["error"] for r in rs if r.get(key) and "error" in r[key]]
    if not ns:
        return f"{label} error: {errs[0]}" if errs else f"{label} none"
    zs = [n["z"] for n in ns if n.get("z") is not None]
    out = (f"{label} mean {spread(n['mean'] for n in ns)} sd {spread(n['sd'] for n in ns)} q95 {spread(n['q95'] for n in ns)} z {spread(zs)} fallbacks {sum(n.get('fallbacks', 0) for n in ns)}")
    if errs:
        out += f" ({len(errs)} of {len(rs)} without a null: {errs[0]})"
    return out


class TestFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = RP.load(D / "runs")
        cls.text = RP.render(cls.rep)
        cls.sec = sections(cls.text)
        cls.res = rj("RESULTS")

    def test_eleven_sections_and_each_found_by_its_number(self):
        self.assertEqual(sorted(self.sec), list(range(11)))

    def test_the_conditions_table_has_a_row_per_condition_with_its_own_counts(self):
        lines = self.sec[2].splitlines()
        self.assertEqual(len(lines), 2 + len(COND_FILES))
        for name in COND_FILES:
            c = rj(name)
            row = next(l for l in lines[2:] if l.startswith(name + " "))
            self.assertEqual(row.split(), [name, c["kind"], str(c["every"]) if c.get("every") else "-", f"{c['n_train_moments']}/{c['n_held_moments']}", f"{c['n_train_words']}/{c['n_held_words']}",
                                           str(c["V"]), str(c["N0"]), str(c["draws"]), fmt(c["cpu_seconds"], 1), f"{c['peak_rss_kb'] / 1024.0:.0f}"], name)

    def test_the_gain_section_prints_each_rules_numbers_from_its_records(self):
        a4 = rj("ALPHA4")
        sec = self.sec[5]
        for rule in RULES:
            rs = by_rule(a4, rule)
            gv = self.res["grade"]["alpha4"][rule]
            gn = gv["gain"]
            blk = block(sec, f"GAIN {rule}:", "GAIN ")
            head = blk[0]
            self.assertTrue(head.startswith(f"GAIN {rule}: {gv['gain_verdict']} — gate first {'ok' if gv['gate_first_ok'] else 'NOT ok'}"), head)
            self.assertIn(f"{gn['n_pass']} of {gn['n']} seeds pass (need {gn['need']}; exact sign p {gn['exact_sign_p']:.4f}); {gn['no_null']} without a null", head)
            adj = [r["adjacency"]["train_adjacent_share"] for r in rs if r["adjacency"]["train_adjacent_share"] is not None]
            line2 = blk[1].strip()
            self.assertIn(f"|F| {counts(r['n_frames'] for r in rs)}; share with a within-moment adjacent train occurrence {spread(adj, 3)}; G {spread(r['gain']['G'] for r in rs)} bits "
                          f"= {spread((r['gain']['per_word'] for r in rs), 5)} a held-out word; L {spread(r['gain']['L'] for r in rs)}", line2)
            self.assertIn(f"held adjacency: zero-firing frames {counts(r['adjacency']['held_adjacent_zero'] for r in rs)}, firings {counts(r['adjacency']['held_firings'] for r in rs)}", line2)
            self.assertEqual(blk[2].strip(), null_fragment(rs, "null1", "NULL-1"))
            an = [r["anatomy"] for r in rs]
            self.assertEqual(blk[3].strip(), f"anatomy G = M + D + C − L: M {spread(a['M'] for a in an)}, D {spread(a['D'] for a in an)}, C {spread(a['C'] for a in an)}, L {spread(a['L'] for a in an)}; "
                                              f"T = D + C {spread(a['T'] for a in an)}")
            if rule == "WEB-S":
                for r in rs:
                    n1 = r["null1"]
                    self.assertIn(f"      WEB-S seed {r['seed']}: |F| {r['n_frames']}, G {fmt(r['gain']['G'])}, NULL-1 q95 {fmt(n1['q95'])}, beats q95 {n1['beats_q95']}", blk)

    def test_the_plant_section_prints_B_its_decomposition_and_each_rules_gate(self):
        sec = self.sec[3]
        for name, side in (("ALPHA4+PLANT", "alpha4"), ("SCENE+PLANT", "scene")):
            c = rj(name)
            ps, d, n2 = c["plant_stream"], c["plant_stream"]["decomposition"], c["plant_stream"]["null2_of_plant"]
            self.assertIn(f"{name}: plants {ps['plants_train']} train / {ps['plants_held']} held; V {ps['V']}; N0 {ps['N0']}", sec)
            self.assertIn(f"(B) G({{F*}}) = {ps['B']:+.2f} bits; the architect's first-order expected value {ps['expected_first_order']:.2f}; decomposition M {fmt(d['M'])} + D {fmt(d['D'])} + C {fmt(d['C'])} − L {fmt(d['L'])} "
                          f"= {fmt(d['G'])} (T = D + C = {fmt(d['T'])}; denominator effect {d['delta']:.5f} bits a token; {d['firings']} held firings)", sec)
            self.assertIn(f"PLANT-BEATS-NULL-2 {name}: {ps['plant_beats_null2']} (B {fmt(ps['B'])} against NULL-2 of {{F*}}: mean {fmt(n2['mean'])}, sd {fmt(n2['sd'])}, q95 {fmt(n2['q95'])}, "
                          f"fallbacks {n2['fallbacks']}, {n2['draws']} draws)", sec)
            for rule in RULES:
                rs = by_rule(c, rule)
                pg = self.res["grade"][side][rule]["plant_gate"]
                lg = self.res["grade_law"][side][rule]["plant_gate"]
                kept = sum(1 for r in rs if r["plant"]["kept"])
                Cs = [r["plant"]["C"] for r in rs if r["plant"]["C"] is not None]
                line = next(l for l in sec.splitlines() if l.startswith(f"  plant gate {name} {rule}:"))
                self.assertEqual(line, f"  plant gate {name} {rule}: {'PASS' if pg['pass'] else 'FAIL'} — {pg['n_counted']} of {pg['n_seeds']} seeds count (need {pg['need']}); keeps F* at {kept} of {len(rs)}; "
                                       f"(A) whole-set G {spread(r['plant']['A'] for r in rs)}; (C) F*'s marginal credit {spread(Cs)}; the base text's clause (keeps AND (A) > 0): {'pass' if lg['pass'] else 'fail'} (a reading)")
        for rule in RULES:
            a = self.res["grade"]["alpha4"][rule]["plant_gate"]["pass"]
            s = self.res["grade"]["scene"][rule]["gradable"]
            self.assertIn(f"  {rule}: ALPHA4 {'gradable' if a else 'NOT GRADABLE'} on the plant; SCENE {'gradable' if s else 'NOT GRADABLE'}", sec)

    def test_the_shuffle_section_prints_each_rules_quiet_reading(self):
        sh = rj("ALPHA4+SHUFFLE")
        for rule in RULES:
            rs = by_rule(sh, rule)
            sq = self.res["grade"]["alpha4"][rule]["shuffle_quiet"]
            line = next(l for l in self.sec[4].splitlines() if l.startswith(f"SHUFFLE-QUIET {rule}:"))
            self.assertEqual(line, f"SHUFFLE-QUIET {rule}: {'QUIET' if sq['quiet'] else 'LOUD'} — {sq['n_quiet']} of {sq['n']} (need {sq['need']}); empty sets {sq['empty']}; |F| {counts(r['n_frames'] for r in rs)}; "
                                   f"G {spread(r['gain']['G'] for r in rs)}; NULL-1 q95 {spread(r['null1']['q95'] for r in rs)}")

    def test_the_criterion_section_prints_each_rules_null2_reading(self):
        a4 = rj("ALPHA4")
        beats = self.res["grade"]["plant_beats_null2"]
        self.assertIn(f"PLANT-BEATS-NULL-2: ALPHA4+PLANT {beats['ALPHA4+PLANT']}, SCENE+PLANT {beats['SCENE+PLANT']}", self.sec[6])
        for rule in RULES:
            rs = by_rule(a4, rule)
            cr = self.res["grade"]["alpha4"][rule]["criterion"]
            blk = block(self.sec[6], f"CRITERION-MATTERS {rule}:", "CRITERION-MATTERS ")
            self.assertEqual(blk[0], f"CRITERION-MATTERS {rule}: {cr['verdict']} — {cr['n_pass']} of {cr['n']} seeds (need {cr['need']})")
            self.assertEqual(blk[1].strip(), f"G {spread(r['gain']['G'] for r in rs)}; {null_fragment(rs, 'null2', 'NULL-2')}")

    def test_the_eye_section_prints_each_rules_counts_and_the_per_frame_table(self):
        eye = self.res["eye"]
        a4 = rj("ALPHA4")
        sec = self.sec[7]
        self.assertIn(f"the cells said {eye['distinct_said']} distinct frames, {eye['says']} says, {eye['yes']} confirmed by the eye: base rate {eye['base_rate']:.4f}", sec)
        for rule in RULES:
            er = [r for r in eye["records"] if r["rule"] == rule]
            line = next(l for l in sec.splitlines() if l.startswith(f"  {rule}: keeps"))
            self.assertEqual(line, f"  {rule}: keeps {counts(r['said_kept'] for r in er)} of the {eye['distinct_said']} said frames; pooled yes-rate of the says of the frames it KEEPS "
                                   f"{spread((r['rate_kept'] for r in er if r['rate_kept'] is not None), 3)} (says kept {counts(r['says_kept'] for r in er)}) against those it does not keep "
                                   f"{spread((r['rate_not_kept'] for r in er if r['rate_not_kept'] is not None), 3)} (says not kept {counts(r['says_not_kept'] for r in er)}); "
                                   f"frames it keeps that the cells never said {counts(r['kept_never_said'] for r in er)} of |F| {counts(r['n_frames'] for r in er)}")
        for f in eye["frames"]:
            flags = []
            for rule in RULES:
                kept = [{tuple(x) for x in r["frames"]} for r in by_rule(a4, rule)]
                if f["pair"] is None:
                    flags.append(f"{rule} -")
                elif rule == "WEB-S":
                    flags.append(f"{rule} {sum(1 for k in kept if tuple(f['pair']) in k)}/{len(kept)}")
                else:
                    flags.append(f"{rule} {'kept' if tuple(f['pair']) in kept[0] else 'no'}")
            self.assertIn(f"      «{f['frame']}»  says {f['says']}  yes {f['yes']}  " + "  ".join(flags), sec.splitlines())

    def test_the_eye_table_marks_the_rules_that_keep_a_said_frame(self):
        """a planted copy: MDL-GREEDY and WEB-S seed 1 keep «red box»: the table must say so (the fixture's own sets keep none of the said frames)."""
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            p = d / "runs" / "ALPHA4.json"
            before = p.read_bytes()
            c = json.loads(before)
            for r in c["records"]:
                if r["rule"] == "MDL-GREEDY" or (r["rule"] == "WEB-S" and r["seed"] == 1):
                    r["frames"] = r["frames"] + [["red", "box"]]
            p.write_bytes(json.dumps(c, sort_keys=True).encode())
            self.assertNotEqual(p.read_bytes(), before)                                                  # the plant changed the bytes
            text = RP.render(RP.load(d / "runs"))
            self.assertIn("      «red box»  says 2  yes 1  WEB-H no  WEB-S 1/2  SENTENCE no  MDL-GREEDY kept", text.splitlines())
            self.assertIn("      «to the»  says 1  yes 0  WEB-H no  WEB-S 0/2  SENTENCE no  MDL-GREEDY no", text.splitlines())
        finally:
            shutil.rmtree(d)

    def test_without_gates_the_provenance_says_so_and_lists_six_records(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            (d / "runs" / "GATES.json").unlink()
            secs = sections(RP.render(RP.load(d / "runs")))
            lines = secs[0].splitlines()
            self.assertEqual(lines[-1], "GATES.json: not present")                                        # the provenance's own line (section 1 repeats the words, so a substring test cannot tell them apart)
            self.assertEqual(sum(1 for l in lines if re.fullmatch(r"[0-9a-f]{64}  \S+\.json", l)), 6)
            self.assertNotIn("GATES.json yes", secs[0])
            self.assertEqual(secs[1].splitlines(), ["== 1 · GATES (G1-G6 on the real copies, before the unit)", "GATES.json: not present — the gates are not recorded here"])
        finally:
            shutil.rmtree(d)

    def test_the_g4_control_line_prints_each_of_its_six_fields(self):
        g = json.loads((D / "runs" / "GATES.json").read_text())
        g["g4"]["streams"]["A"]["control"] = {"caught": True, "bytes_changed": False, "gate_honest": True, "gate_broken": False, "B_honest": 1.0, "C_honest": 2.0, "B_broken": 3.0, "C_broken": 4.0}
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            (d / "runs" / "GATES.json").write_text(json.dumps(g))
            lines = sections(RP.render(RP.load(d / "runs")))[1].splitlines()
            self.assertIn("    the gate's parse-breaking control: caught True, bytes changed False; honest gate (B 1.00, C 2.00) True, broken gate (B 3.00, C 4.00) False", lines)
        finally:
            shutil.rmtree(d)

    def test_fallbacks_are_summed_over_the_seeds_and_the_criterion_section_prints_a_changed_scene_beat(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            p = d / "runs" / "ALPHA4.json"
            c = json.loads(p.read_text())
            for seed, k in ((1, 3), (2, 4)):
                next(r for r in c["records"] if r["rule"] == "WEB-S" and r["seed"] == seed)["null1"]["fallbacks"] = k
            p.write_text(json.dumps(c, sort_keys=True))
            q = d / "runs" / "RESULTS.json"
            r = json.loads(q.read_text())
            r["grade"]["plant_beats_null2"]["SCENE+PLANT"] = False
            q.write_text(json.dumps(r, sort_keys=True))
            secs = sections(RP.render(RP.load(d / "runs")))
            webs = block(secs[5], "GAIN WEB-S:", "GAIN ")
            self.assertTrue(webs[2].strip().endswith("fallbacks 7"), webs[2])                                # 3 + 4, not the larger of them
            self.assertIn("PLANT-BEATS-NULL-2: ALPHA4+PLANT True, SCENE+PLANT False", secs[6])
        finally:
            shutil.rmtree(d)

    def test_the_mdl_trace_is_printed_when_the_run_has_one_and_cut_at_fifteen(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            p = d / "runs" / "ALPHA4.json"
            before = p.read_bytes()
            c = json.loads(before)
            mdl = next(r for r in c["records"] if r["rule"] == "MDL-GREEDY")
            mdl["info"]["trace"] = [{"frame": [f"a{i}", f"b{i}"], "delta": 10.0 - i, "bits_after": 0.0, "fires": i, "n_tokens": 100} for i in range(17)]
            p.write_bytes(json.dumps(c, sort_keys=True).encode())
            self.assertNotEqual(p.read_bytes(), before)
            lines = sections(RP.render(RP.load(d / "runs")))[5].splitlines()
            i = lines.index("MDL-GREEDY took 17 steps; its first 15 picks (frame, train Δ bits, train firings):")
            self.assertEqual(lines[i + 1:], [f"      a{k} b{k}  Δ {10.0 - k:.2f}  fires {k}" for k in range(15)])                  # the 15 first, in order, and no sixteenth
            short = json.loads(p.read_text())
            next(r for r in short["records"] if r["rule"] == "MDL-GREEDY")["info"]["trace"] = short["records"][-1]["info"]["trace"][:3]
            p.write_text(json.dumps(short, sort_keys=True))
            self.assertIn("MDL-GREEDY took 3 steps; its first 3 picks (frame, train Δ bits, train firings):", sections(RP.render(RP.load(d / "runs")))[5].splitlines())
        finally:
            shutil.rmtree(d)

    def test_the_text_ends_with_one_newline_and_every_section_is_one_block(self):
        self.assertTrue(self.text.endswith("\n") and not self.text.endswith("\n\n"))
        self.assertEqual(len(self.text.split("\n\n")), 11)                                                 # eleven blocks, one blank line between each pair, none inside a block

    def test_the_overlaps_section_prints_each_conditions_jaccards(self):
        for name in COND_FILES:
            ov = self.res["overlaps"][name]
            want = f"{name}: " + "; ".join(f"{k} {'none' if v is None else fmt(v, 3)}" for k, v in sorted(ov.items()))
            self.assertIn(want, self.sec[8].splitlines())

    def test_the_scene_section_prints_the_ceiling_the_rows_the_oracle_and_each_rules_gradability(self):
        sb = self.res["scene"]
        sc = rj("SCENE")
        sec = self.sec[9]
        ch = sb["chi2"]
        self.assertIn("generator fit (G1 χ²): " + ", ".join(f"{k} p {ch[k]['p']:.3f} (n {ch[k]['n']})" for k in ("length", "shape", "colour", "size", "pairs"))
                      + f"; held-out pairs seen {ch['heldout_pairs_seen']}; G_max gated: {sb['gmax_gated']}", sec)
        self.assertIn(f"THE CEILING: G_max {fmt(sb['G_max'])} bits (bits(held | empty) {fmt(sb['bits0'])} minus the generator's own code length); the expected form bits(empty) − 6.0774 · N_utt {fmt(sb['expected_form'])}; "
                      f"entropy {sb['entropy']:.4f}; H(utterance | length) {sb['h_given_length']:.4f}", sec)
        self.assertIn(f"STOP {sb['stop']}", sec)
        for row in sb["rows"]:
            self.assertIn(f"  {row['rule']:<11}seed {row['seed']:>2}  G {fmt(row['G'])}  margin to G_max {fmt(row['margin'])}  {'VIOLATION' if row['violation'] else 'under G_max + 20'}", sec.splitlines())
        o = sb["oracle"]
        self.assertIn(f"G(F_oracle) {fmt(o['G'])} ({o['n_frames']} frames; margin to G_max {fmt(o['margin'])}; violation {o['violation']}); each rule's recall of F_oracle: "
                      + ", ".join(f"{k} {o['recall'][k]:.3f}" for k in sorted(o["recall"])), sec)
        for rule in RULES:
            rs = by_rule(sc, rule)
            g = self.res["grade"]["scene"][rule]
            pg = g["plant_gate"]
            blk = block(sec, f"SCENE {rule}:", "SCENE ")
            self.assertEqual(blk[0], f"SCENE {rule}: {'gradable' if g['gradable'] else 'NOT GRADABLE'} (SCENE+PLANT plant gate: {pg['n_counted']} of {pg['n_seeds']} seeds count, need {pg['need']})")
            self.assertEqual(blk[1].strip(), f"|F| {counts(r['n_frames'] for r in rs)}; G {spread(r['gain']['G'] for r in rs)}; {null_fragment(rs, 'null1', 'NULL-1')}; {null_fragment(rs, 'null2', 'NULL-2')}")

    def test_a_null_that_could_not_be_dealt_prints_its_error_never_a_blank(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            p = d / "runs" / "ALPHA4.json"
            c = json.loads(p.read_text())
            mdl = next(r for r in c["records"] if r["rule"] == "MDL-GREEDY")
            mdl["null2"] = {"error": "a bin without enough candidates (planted)"}
            before = p.read_bytes()
            p.write_text(json.dumps(c, sort_keys=True))
            self.assertNotEqual(p.read_bytes(), before)
            text = RP.render(RP.load(d / "runs"))
            self.assertIn("NULL-2 error: a bin without enough candidates (planted)", text)
        finally:
            shutil.rmtree(d)

    def test_the_provenance_header_lines(self):
        h = self.res["header"]
        lines = self.sec[0].splitlines()
        self.assertEqual(lines[1], f"gate mode: {self.res['mode']}; code sha (RESULTS.json): {h['toys_git_sha']}; the toy's tree differed from it when the unit ran: {h['toys_tree_dirty']}")
        self.assertEqual(lines[2:5], [f"signed text frames: sha256 {h['prereg_frames_sha256']}", f"signed text frames_amend1: sha256 {h['prereg_frames_amend1_sha256']}",
                                      f"signed text frames_amend2: sha256 {h['prereg_frames_amend2_sha256']}"])
        self.assertEqual(len({h["prereg_frames_sha256"], h["prereg_frames_amend1_sha256"], h["prereg_frames_amend2_sha256"]}), 3)    # three DIFFERENT texts: a line printing the wrong one is seen
        self.assertIn(f"code sha across the five conditions and RESULTS.json: one ({h['toys_git_sha']})", lines)
        self.assertIn("code sha of GATES.json: abc (DIFFERENT from the unit)", lines)
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            g = json.loads((d / "runs" / "GATES.json").read_text())
            g["header"]["toys_git_sha"] = h["toys_git_sha"]
            (d / "runs" / "GATES.json").write_text(json.dumps(g))
            c = json.loads((d / "runs" / "SCENE.json").read_text())
            c["header"]["toys_git_sha"] = "another"
            (d / "runs" / "SCENE.json").write_text(json.dumps(c, sort_keys=True))
            lines2 = sections(RP.render(RP.load(d / "runs")))[0].splitlines()
            self.assertIn(f"code sha of GATES.json: {h['toys_git_sha']} (the same)", lines2)
            self.assertTrue(any(l.startswith("code sha across the five conditions and RESULTS.json: 2 DIFFERENT (") for l in lines2), lines2)
        finally:
            shutil.rmtree(d)

    def test_a_missing_results_file_is_an_error_not_a_blank(self):
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            (d / "runs" / "RESULTS.json").unlink()
            with self.assertRaises(RP.ReportError):
                RP.load(d / "runs")
        finally:
            shutil.rmtree(d)

    def test_main_defaults_read_the_runners_directory_and_write_the_committed_report_path(self):
        d = Path(tempfile.mkdtemp())
        try:
            seen = []
            target = d / "sub" / "REPORT.txt"
            with mock.patch.object(RP, "load", lambda root: seen.append(root) or "REP"), mock.patch.object(RP, "render", lambda rep: f"text of {rep}\n"), mock.patch.object(RP, "DEFAULT_OUT", target):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = RP.main([])
            self.assertEqual(code, 0)
            self.assertEqual(seen, [RN.RUNS])
            self.assertEqual(target.read_text(), "text of REP\n")
            import hashlib
            self.assertEqual(buf.getvalue().strip(), f"wrote REPORT.txt: {len('text of REP' + chr(10))} bytes, sha256 {hashlib.sha256(target.read_bytes()).hexdigest()}")
        finally:
            shutil.rmtree(d)
        self.assertEqual(RP.DEFAULT_OUT, ST.REPO / "docs" / "research" / "toys" / "RESULT-TOY-FRAMES-REPORT.txt")      # the real default, once the patch is gone

    def test_the_gates_section_prints_every_gate_figure_of_the_record(self):
        g = json.loads((D / "runs" / "GATES.json").read_text())
        lines = self.sec[1].splitlines()
        self.assertIn(f"GATES.json: passed {g['passed']} (failures: none); gate mode {g['header']['gate_mode']}; 12.5 CPU-s; peak RSS 102 MB", lines)
        self.assertIn("G1 OK: 10 copies verified; ALPHA4 84275 moments / 112489 words; SCENE 10000 moments; says (526, 86, 40) (rows, yes, distinct frames); plant tokens in real rows: "
                      "ALPHA4 {'zzq': 0, 'qxk': 0}, SCENE {'zzq': 0, 'qxk': 0}", lines)
        self.assertIn("   χ² fit of SCENE to the generator (each p > 0.001 gates G_max): length p 0.410, shape p 0.520, colour p 0.330, size p 0.770, pairs p 0.290; held-out pairs seen 0; «dax» excluded 1; G_max gated: True", lines)
        self.assertIn("G2 OK: find_frames on the stand-in store equals the call on the real Episodes store: 3 rows, frames [['blue', 'ball'], ['green', 'key'], ['red', 'box']]", lines)
        self.assertIn("G3 OK: 160 compressor cases, max |fast − slow| 3.14e-13 (bar 1e-9); the greedy's 28 steps over 8 seeds, problems none", lines)
        self.assertIn("G4 OK: two planted synthetic streams (AMENDMENT-2 §2); failures none", lines)
        self.assertIn("  stream A: SCENE-regime (as signed): 3000 moments, a plant after every 10th (180 train / 120 held plants); V 15, budget B = 2V = 30; B = G({F*}) 700.00; PLANT-BEATS-NULL-2 True (NULL-2 q95 none)", lines)
        self.assertIn("    WEB-S 6 of 10 seeds count (need 9): gate FAIL — PRINTED, not required", lines)
        self.assertIn("    WEB-S 10 of 10 seeds count (need 9): gate PASS — REQUIRED", lines)
        self.assertIn("    MDL-GREEDY 1 of 1 seeds count (need 1): gate PASS — REQUIRED", lines)
        self.assertEqual(sum(1 for l in lines if l.startswith("    the gate's parse-breaking control: caught True, bytes changed True; honest gate (B 700.00, C 699.00)")), 2)
        self.assertIn("G5 OK: pilots 10 draws 50.0 CPU-s, peak 98 MB; 20 draws 66.0 CPU-s, peak 99 MB; slope 1.600 CPU-s a draw; predicted unit 16.2 CPU-min (ceiling 40.0); predicted peak 105 MB (ceiling 1024); "
                      "measured peak 99 MB", lines)
        self.assertIn("G6 OK: 1 replicates, smallest margin G_max − G(F_oracle) 4990.00, violations 0; the planted cheat: caught True (G 9000.00 against G_max 5000.00 + 20); exact checks: support sums to 1.0, "
                      "entropy 6.0774, H(length) 1.5000, H(utterance | length) 4.5774, support 90", lines)
        bad = json.loads(json.dumps(g))
        bad["passed"], bad["failures"], bad["g2"]["ok"] = False, ["G2: planted failure"], False
        d = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(D / "runs", d / "runs")
            (d / "runs" / "GATES.json").write_text(json.dumps(bad))
            lines2 = sections(RP.render(RP.load(d / "runs")))[1].splitlines()
            self.assertIn("GATES.json: passed False (failures: ['G2: planted failure']); gate mode amend1; 12.5 CPU-s; peak RSS 102 MB", lines2)
            self.assertTrue(any(l.startswith("G2 FAILED:") for l in lines2))
        finally:
            shutil.rmtree(d)


class TestInstrumentChecks(unittest.TestCase):
    """RESULTS.json's grade, eye reading, overlaps and SCENE rows are printed from RESULTS.json; the report recomputes each from the condition records (the source of truth) and prints yes / NO."""

    def prov(self, root=None):
        return sections(RP.render(RP.load(root or D / "runs")))[0]

    def plant(self, edit):
        d = Path(tempfile.mkdtemp())
        shutil.copytree(D / "runs", d / "runs")
        files = {p.name: p.read_bytes() for p in (d / "runs").glob("*.json")}
        edit(d / "runs")
        after = {p.name: p.read_bytes() for p in (d / "runs").glob("*.json")}
        self.assertNotEqual(files, after)                                                              # the plant changed the bytes of a record
        return d

    def test_the_pristine_fixture_reads_yes_on_every_check(self):
        prov = self.prov()
        self.assertIn("signed texts: every record carries RESULTS.json's three: ALPHA4 yes; ALPHA4+PLANT yes; ALPHA4+SHUFFLE yes; SCENE yes; SCENE+PLANT yes; GATES.json yes", prov)
        self.assertIn("CHECK grade: RESULTS.json's grade equals the grade recomputed from the five condition records: yes (mode amend1); the base text's mode: yes", prov)
        self.assertIn("CHECK eye: RESULTS.json's eye reading equals the reading recomputed from ALPHA4.json and its own per-frame table: yes", prov)
        self.assertIn("CHECK overlaps: RESULTS.json's overlaps equal the overlaps recomputed from the five records: yes", prov)
        self.assertIn("CHECK scene: RESULTS.json's SCENE rows, margins and recalls equal those recomputed from SCENE.json: yes", prov)

    def test_a_changed_verdict_in_a_record_reads_NO_on_the_grade_check_only(self):
        def edit(root):
            p = root / "ALPHA4.json"
            c = json.loads(p.read_text())
            r = next(x for x in c["records"] if x["rule"] == "WEB-H")
            r["gain"]["G"], r["null1"]["q95"] = 1.0e6, 0.0                                                # WEB-H now passes GAIN; RESULTS.json still says FAIL
            p.write_text(json.dumps(c, sort_keys=True))
        d = self.plant(edit)
        try:
            prov = self.prov(d / "runs")
            self.assertIn("CHECK grade: RESULTS.json's grade equals the grade recomputed from the five condition records: NO (mode amend1); the base text's mode: NO", prov)
            self.assertIn("RESULTS.json's SCENE rows, margins and recalls equal those recomputed from SCENE.json: yes", prov)
        finally:
            shutil.rmtree(d)

    def test_a_changed_kept_set_reads_NO_on_the_eye_and_overlap_checks(self):
        def edit(root):
            p = root / "ALPHA4.json"
            c = json.loads(p.read_text())
            next(x for x in c["records"] if x["rule"] == "WEB-H")["frames"].append(["red", "box"])
            p.write_text(json.dumps(c, sort_keys=True))
        d = self.plant(edit)
        try:
            prov = self.prov(d / "runs")
            self.assertIn("CHECK eye: RESULTS.json's eye reading equals the reading recomputed from ALPHA4.json and its own per-frame table: NO", prov)
            self.assertIn("CHECK overlaps: RESULTS.json's overlaps equal the overlaps recomputed from the five records: NO", prov)
        finally:
            shutil.rmtree(d)

    def test_a_changed_scene_record_reads_NO_on_the_scene_check(self):
        def edit(root):
            p = root / "SCENE.json"
            c = json.loads(p.read_text())
            c["records"][-1]["gain"]["G"] += 5.0
            p.write_text(json.dumps(c, sort_keys=True))
        d = self.plant(edit)
        try:
            self.assertIn("CHECK scene: RESULTS.json's SCENE rows, margins and recalls equal those recomputed from SCENE.json: NO", self.prov(d / "runs"))
        finally:
            shutil.rmtree(d)

    def test_a_scene_row_missing_or_for_another_rule_or_with_another_margin_reads_NO(self):
        def results_edit(fn):
            def edit(root):
                p = root / "RESULTS.json"
                r = json.loads(p.read_text())
                fn(r["scene"])
                p.write_text(json.dumps(r, sort_keys=True))
            return edit
        def drop_row(sb): sb["rows"].pop()
        def other_rule(sb): sb["rows"][0]["rule"] = "SENTENCE"
        def other_seed(sb): sb["rows"][1]["seed"] = 99
        def other_g(sb): sb["rows"][0]["G"] += 1.0
        def other_margin(sb): sb["rows"][0]["margin"] += 1.0
        def other_oracle_margin(sb): sb["oracle"]["margin"] += 1.0
        def other_recall(sb): sb["oracle"]["recall"]["MDL-GREEDY"] = 0.0
        for fn in (drop_row, other_rule, other_seed, other_g, other_margin, other_oracle_margin, other_recall):
            with self.subTest(plant=fn.__name__):
                d = self.plant(results_edit(fn))
                try:
                    self.assertIn("CHECK scene: RESULTS.json's SCENE rows, margins and recalls equal those recomputed from SCENE.json: NO", self.prov(d / "runs"))
                finally:
                    shutil.rmtree(d)

    def test_a_changed_grade_or_overlap_or_eye_block_in_results_reads_NO(self):
        def results_edit(fn):
            def edit(root):
                p = root / "RESULTS.json"
                r = json.loads(p.read_text())
                fn(r)
                p.write_text(json.dumps(r, sort_keys=True))
            return edit
        def grade(r): r["grade"]["alpha4"]["WEB-H"]["gain_verdict"] = "PASS"
        def grade_law(r): r["grade_law"]["alpha4"]["WEB-S"]["gain_verdict"] = "PASS"
        def overlap(r): r["overlaps"]["ALPHA4"]["WEB-H|SENTENCE"] = 0.99
        def eye(r): r["eye"]["frames"][0]["yes"] += 1
        want = {"grade": "CHECK grade: RESULTS.json's grade equals the grade recomputed from the five condition records: NO (mode amend1); the base text's mode: yes",
                "grade_law": "CHECK grade: RESULTS.json's grade equals the grade recomputed from the five condition records: yes (mode amend1); the base text's mode: NO",
                "overlap": "CHECK overlaps: RESULTS.json's overlaps equal the overlaps recomputed from the five records: NO",
                "eye": "CHECK eye: RESULTS.json's eye reading equals the reading recomputed from ALPHA4.json and its own per-frame table: NO"}
        for fn in (grade, grade_law, overlap, eye):
            with self.subTest(plant=fn.__name__):
                d = self.plant(results_edit(fn))
                try:
                    self.assertIn(want[fn.__name__], self.prov(d / "runs"))
                finally:
                    shutil.rmtree(d)

    def test_a_gates_record_with_another_law_text_reads_NO_for_gates_only(self):
        def edit(root):
            p = root / "GATES.json"
            g = json.loads(p.read_text())
            g["header"]["prereg_frames_amend2_sha256"] = "0" * 64
            p.write_text(json.dumps(g))
        d = self.plant(edit)
        try:
            self.assertIn("signed texts: every record carries RESULTS.json's three: ALPHA4 yes; ALPHA4+PLANT yes; ALPHA4+SHUFFLE yes; SCENE yes; SCENE+PLANT yes; GATES.json NO", self.prov(d / "runs"))
        finally:
            shutil.rmtree(d)

    def test_a_condition_record_with_another_law_text_reads_NO_for_that_record_only(self):
        def edit(root):
            p = root / "SCENE.json"
            c = json.loads(p.read_text())
            c["header"]["prereg_frames_amend1_sha256"] = "f" * 64
            p.write_text(json.dumps(c, sort_keys=True))
        d = self.plant(edit)
        try:
            self.assertIn("ALPHA4+SHUFFLE yes; SCENE NO; SCENE+PLANT yes; GATES.json yes", self.prov(d / "runs"))
        finally:
            shutil.rmtree(d)

    def test_without_a_per_frame_table_the_eye_check_says_it_was_not_run(self):
        def edit(root):
            p = root / "RESULTS.json"
            r = json.loads(p.read_text())
            del r["eye"]["frames"]
            p.write_text(json.dumps(r, sort_keys=True))
        d = self.plant(edit)
        try:
            self.assertIn("CHECK eye: not checked: RESULTS.json has no per-frame table", self.prov(d / "runs"))
            self.assertIn("the per-frame table is not in RESULTS.json (eye.frames absent)", sections(RP.render(RP.load(d / "runs")))[7].splitlines())
        finally:
            shutil.rmtree(d)


# ------------------------------------------------------------------------------------------------------------------ the predictions, one condition at a time
def pc_rep(*, mdl=100.0, webh=50.0, webs=(40.0,) * 10, sent=60.0, q1=10.0, q2=20.0, z2=None, mdl_frames=(), sent_frames=(), webh_frames=(), scene=None, gmax=1000.0, oracle_g=300.0,
           eye_frames=(), mdl_eye=(0.4, 20, 0.1, 100)):
    z2 = z2 or {"WEB-H": 1.0, "WEB-S": 1.0, "SENTENCE": 1.0, "MDL-GREEDY": 5.0}

    def r(rule, seed, G, frames):
        return {"rule": rule, "seed": seed, "n_frames": len(frames), "frames": [list(f) for f in frames], "gain": {"G": G},
                "null1": {"q95": q1, "mean": 0.0, "sd": 1.0, "z": 1.0}, "null2": {"q95": q2, "mean": 0.0, "sd": 1.0, "z": z2[rule]}}

    alpha = [r("WEB-H", 0, webh, webh_frames)] + [r("WEB-S", i + 1, g, ()) for i, g in enumerate(webs)] + [r("SENTENCE", 0, sent, sent_frames), r("MDL-GREEDY", 0, mdl, mdl_frames)]
    scene = scene or {"WEB-H": 0.0, "WEB-S": 0.0, "SENTENCE": 0.0, "MDL-GREEDY": 50.0}
    sc = [r("WEB-H", 0, scene["WEB-H"], ())] + [r("WEB-S", 1, scene["WEB-S"], ()), r("WEB-S", 2, scene["WEB-S"], ())] + [r("SENTENCE", 0, scene["SENTENCE"], ()), r("MDL-GREEDY", 0, scene["MDL-GREEDY"], ())]
    frames = [{"frame": " ".join(p), "pair": list(p), "says": s, "yes": y} for p, s, y in eye_frames]
    rk, sk, rn, sn = mdl_eye
    return {"conds": {"ALPHA4": {"records": alpha}, "SCENE": {"records": sc}},
            "results": {"scene": {"G_max": gmax, "oracle": {"G": oracle_g}},
                        "eye": {"frames": frames, "base_rate": 0.163, "records": [{"rule": "MDL-GREEDY", "rate_kept": rk, "says_kept": sk, "rate_not_kept": rn, "says_not_kept": sn}]}}}


def verdict(rep, name):
    return next(v for n, v, _d in RP.predictions(rep) if n == name)


class TestPredictions(unittest.TestCase):
    def test_all_six_are_read_and_named(self):
        self.assertEqual([n for n, _v, _d in RP.predictions(pc_rep())], ["P-C1", "P-C2", "P-C3", "P-C4", "P-C5", "P-C6"])

    def test_pc1_mdl_greedy_g_is_the_largest(self):
        self.assertEqual(verdict(pc_rep(), "P-C1"), "holds")
        self.assertEqual(verdict(pc_rep(mdl=60.0), "P-C1"), "holds")                                   # equal to the largest: holds (>=)
        self.assertEqual(verdict(pc_rep(mdl=59.99), "P-C1"), "does not hold")                           # below SENTENCE
        self.assertEqual(verdict(pc_rep(mdl=49.99, sent=10.0), "P-C1"), "does not hold")                # below WEB-H
        self.assertEqual(verdict(pc_rep(mdl=39.99, webh=10.0, sent=10.0), "P-C1"), "does not hold")     # below WEB-S's seed mean
        self.assertEqual(verdict(pc_rep(mdl=40.0, webh=10.0, sent=10.0), "P-C1"), "holds")
        self.assertEqual(verdict(pc_rep(mdl=30.0, webh=10.0, sent=10.0, webs=(10.0,) * 9 + (100.0,)), "P-C1"), "holds")                 # the seed MEAN (19), not the best seed (100)
        self.assertEqual(verdict(pc_rep(mdl=18.0, webh=10.0, sent=10.0, webs=(10.0,) * 9 + (100.0,)), "P-C1"), "does not hold")

    def test_pc2_web_and_sentence_beat_their_nulls_with_g_below_mdl(self):
        self.assertEqual(verdict(pc_rep(), "P-C2"), "holds")
        self.assertEqual(verdict(pc_rep(webh=9.0), "P-C2"), "does not hold")                            # WEB-H inside its null (q95 10)
        self.assertEqual(verdict(pc_rep(webh=10.0), "P-C2"), "does not hold")                           # equal to q95 is not above it
        self.assertEqual(verdict(pc_rep(sent=10.0), "P-C2"), "does not hold")
        self.assertEqual(verdict(pc_rep(webs=(10.0,) * 10), "P-C2"), "does not hold")                   # WEB-S: equal to q95 at every seed beats at none
        self.assertEqual(verdict(pc_rep(sent=9.0), "P-C2"), "does not hold")
        self.assertEqual(verdict(pc_rep(sent=100.0), "P-C2"), "does not hold")                          # SENTENCE not below MDL's
        self.assertEqual(verdict(pc_rep(webh=100.0), "P-C2"), "does not hold")
        self.assertEqual(verdict(pc_rep(webs=(40.0,) * 8 + (5.0, 5.0)), "P-C2"), "holds")               # 8 of 10 seeds beat q95: enough
        self.assertEqual(verdict(pc_rep(webs=(40.0,) * 7 + (5.0,) * 3), "P-C2"), "does not hold")       # 7 of 10: not
        self.assertEqual(verdict(pc_rep(webs=(200.0,) * 10), "P-C2"), "does not hold")                  # the WEB-S seed mean not below MDL's

    def test_pc3_every_scene_g_is_a_tenth_of_g_max_at_most(self):
        self.assertEqual(verdict(pc_rep(), "P-C3"), "holds")                                           # MDL 50 / 1000 = 0.05
        self.assertEqual(verdict(pc_rep(scene={"WEB-H": 0.0, "WEB-S": 0.0, "SENTENCE": 0.0, "MDL-GREEDY": 100.0}), "P-C3"), "holds")          # exactly 0.10: holds (<=)
        self.assertEqual(verdict(pc_rep(scene={"WEB-H": 0.0, "WEB-S": 0.0, "SENTENCE": 0.0, "MDL-GREEDY": 100.01}), "P-C3"), "does not hold")
        self.assertEqual(verdict(pc_rep(scene={"WEB-H": 0.0, "WEB-S": 101.0, "SENTENCE": 0.0, "MDL-GREEDY": 0.0}), "P-C3"), "does not hold")      # WEB-S as its seed mean
        self.assertEqual(verdict(pc_rep(gmax=0.0), "P-C3"), "not readable")
        self.assertEqual(verdict(pc_rep(gmax=-5.0), "P-C3"), "not readable")

    def test_pc4_the_eye_splits_mdls_frames_into_grounded_and_function_word_pairs(self):
        grounded, function = (("green", "box"), 20, 15), (("to", "the"), 30, 0)
        keep_both = pc_rep(eye_frames=[grounded, function], mdl_frames=[("green", "box"), ("to", "the")])
        self.assertEqual(verdict(keep_both, "P-C4"), "holds")
        self.assertEqual(verdict(pc_rep(eye_frames=[grounded, function], mdl_frames=[("green", "box")]), "P-C4"), "does not hold")
        self.assertEqual(verdict(pc_rep(eye_frames=[grounded, function], mdl_frames=[("to", "the")]), "P-C4"), "does not hold")
        self.assertEqual(verdict(pc_rep(eye_frames=[grounded, function], mdl_frames=[("x", "y")]), "P-C4"), "does not hold")
        self.assertEqual(verdict(pc_rep(eye_frames=[function], mdl_frames=[("to", "the")]), "P-C4"), "not readable")      # no grounded frame in the said set
        self.assertEqual(verdict(pc_rep(eye_frames=[grounded], mdl_frames=[("green", "box")]), "P-C4"), "not readable")   # no function-word pair
        # the thresholds: a frame with 4 says is neither; 5 says and 2 confirmed (0.4) is not grounded; 5 and 3 (0.6) is; 5 says and 1 confirmed is not a function pair
        cases = [((("a", "b"), 4, 4), (("to", "the"), 30, 0), "not readable"),                         # 4 says: not grounded, so no grounded frame at all
                 ((("a", "b"), 5, 2), (("to", "the"), 30, 0), "not readable"),                         # 0.4 < 0.5
                 ((("a", "b"), 5, 3), (("to", "the"), 30, 0), "holds"),                                # 0.6: grounded
                 ((("a", "b"), 6, 3), (("to", "the"), 30, 0), "holds"),                                # exactly 0.5: grounded (>=)
                 ((("a", "b"), 5, 5), (("to", "the"), 30, 1), "not readable"),                         # one confirmation: not a function pair
                 ((("a", "b"), 5, 5), (("to", "the"), 4, 0), "not readable")]                          # 4 says: not a function pair
        for g, f, want in cases:
            rep = pc_rep(eye_frames=[g, f], mdl_frames=[g[0], f[0]])
            self.assertEqual(verdict(rep, "P-C4"), want, (g, f))

    def test_pc5_sentence_keeps_the_three_named_pairs_and_a_game_pair(self):
        named = [("the", "letters"), ("a", "big"), ("to", "the")]
        for colour in ("green", "yellow", "grey", "purple", "red", "blue"):
            for obj in ("box", "key", "ball"):
                self.assertEqual(verdict(pc_rep(sent_frames=named + [(colour, obj)]), "P-C5"), "holds", (colour, obj))
        self.assertEqual(verdict(pc_rep(sent_frames=named), "P-C5"), "does not hold")                    # no game pair
        self.assertEqual(verdict(pc_rep(sent_frames=named[:2] + [("red", "box")]), "P-C5"), "does not hold")     # one named pair missing
        self.assertEqual(verdict(pc_rep(sent_frames=named + [("the", "box")]), "P-C5"), "does not hold")  # «the» is no game colour
        self.assertEqual(verdict(pc_rep(sent_frames=named + [("red", "the")]), "P-C5"), "does not hold")  # «the» is no game object
        detail = next(d for n, _v, d in RP.predictions(pc_rep(sent_frames=[("the", "letters"), ("red", "box")])) if n == "P-C5")
        self.assertIn("kept «the letters»: yes, kept «a big»: no, kept «to the»: no; game pairs kept ['red box']", detail)

    def test_pc6_two_guesses_on_null2(self):
        self.assertEqual(verdict(pc_rep(mdl=100.0, q2=20.0), "P-C6"), "architect's guess does not hold; mine holds")      # MDL above q95, z 5 above the others' 1
        self.assertEqual(verdict(pc_rep(mdl=20.0, q2=20.0), "P-C6"), "architect's guess holds; mine does not hold")          # G == q95: inside the band
        self.assertEqual(verdict(pc_rep(mdl=100.0, q2=20.0, z2={"WEB-H": 9.0, "WEB-S": 1.0, "SENTENCE": 1.0, "MDL-GREEDY": 5.0}), "P-C6"), "architect's guess does not hold; mine does not hold")   # WEB-H sits FARTHER from NULL-2's band than MDL
        self.assertEqual(verdict(pc_rep(mdl=100.0, q2=20.0, z2={"WEB-H": 1.0, "WEB-S": 1.0, "SENTENCE": 5.0, "MDL-GREEDY": 5.0}), "P-C6"), "architect's guess does not hold; mine does not hold")  # a tie is not «nearer»


if __name__ == "__main__":
    unittest.main()
