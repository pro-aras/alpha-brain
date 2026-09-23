# READER-FIX-0923: each defect as the OLD reader (master a17cb0e, the pristine export) reads it, on the new tests' own landed-shape rows.
import importlib.util, json, sys, tempfile
from pathlib import Path
W = Path("/data/dev/genome-wt-reader-fix"); OLD = W / "scratch" / "master-a17cb0e"
sys.path.insert(0, str(W))
import tests.creature.test_verdict_reader_fix_0923 as T          # the fixtures (helpers only; no tools import at module level)
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
ovl = _load("old_vl", OLD / "tools" / "verdict_life.py"); og4 = _load("old_g4", OLD / "tools" / "verdict_g4.py")
p = lambda *a: print(*a, flush=True)
m = ovl.evolve_mark([T._void_proposal(29), T._judged_proposal(10000, 2), T._judged_proposal(20000, 3), T._judged_proposal(30000, 4)], [], True, 24.0)
p("1 EVOLVE  old: 3 judged + the void round at 24 h ->", m["pass"], "|", m["reason"])
for ms in (600.0, 756.0):
    m = og4.viii_cost({"rss_mb": 965.0, "mind_ms_per_canvas_1min": ms, "cells": 4900}, 21.0, 85.0, None)
    p(f"2 COST    old: GROW life {ms} ms/canvas at 4,900 cells ->", m["pass"], "(bar:", m["bar"][:60], "…) — §8b's bar is 661.5 ms")
acts = [a for a in T.GAME_ACTS for _ in range(3)] + ["left"] * 100
st = {"acts_chosen": {**{a: acts.count(a) for a in T.GAME_ACTS}, "say": 300}, "act_mismatches": 0}
m = ovl.act_mark(T._act_tape(acts), [], st)
p("3 ACT     old: the last 100 game acts all `left`, STATUS with say 300 ->", m["pass"], "max_share", m["max_share"], "census", m["census"])
tape = T._episodes_tape([("red", "ball"), ("blue", "key"), ("green", "box")], 64)
m = ovl.sentence_mark(tape, {"frames_filed": 4, "frames_scored": 4, "frames_true": 4}, True)
p("4 SENTENCE old: 3 episodes × 64 frames ->", "graded" if m["graded"] else "not graded", m["pass"], "missions", m["missions"], "max lift", m["max_lift"])
qt = T.QuestionAnsweredOncePerQuestion(); j, t = qt._record()
m = ovl.question_mark(j, t, {}, 24.0, True)
p("5 QUESTION old: 5 questions, 3 answered (maker 2, lexicon 2, both 1) -> answered_rows", m["answered_rows"], "share", m["answered_share"], "(truth 0.6)")
heard = [json.loads(l) for l in open(W / "scratch" / "control-hour1-read-sample.json")] if False else None
s = json.loads((W / "scratch" / "control-hour1-read-sample.json").read_text())
p("6 READ    old rule on alpha4-1's hour 1: the NEWEST 50 of 255 heard; the new sample shares", "7 of 50 with them (scratch/control-hour1-marks.log)")
tape, journal = T._thread_record()
m = ovl.thread_mark({"max_gap_s_eye_ear": [7.0, 7.0]}, {"thinks": 300, "think_waits": 0}, True)
p("7 THREAD  old: a 7.0 s gap on a sleep and a 5.5 s gap off it ->", m["pass"], "attribution keys:", [k for k in m if "sleep" in k] or "none")
jr = [T._sit_boundary(100, False, False, True, False, True), T._sit_boundary(300, True, True, True, True, True, True), T._sit_boundary(400, True, True, True, True, True, True),
      {"seq": 400, "event": "stage", "stage": 4, "moment": 9000, "readings": {k: True for k in "abcde"}}]
m = ovl.stage_mark(jr, True)
p("8 STAGE   old: 3 boundaries with readiness ->", m["pass"], "readiness keys:", [k for k in m if "readiness" in k] or "none")
with tempfile.TemporaryDirectory() as d:
    import datetime as _dt
    root = Path(d) / "root"
    for sub in ("tape/payload", "journal", "state", "exam"): (root / sub).mkdir(parents=True)
    for f in ("organism.npz", "organism.json", "ledger.json"): (root / "state" / f).write_bytes(b"x")
    (root / "tape" / "2026-09-23.jsonl").write_text("".join(json.dumps({"seq": i, "at": T._at(i), "sense": "eye", "meta": {}}) + "\n" for i in range(1, 11)))
    rows = [{"seq": None, "at": T._at(0), "event": "start"}, {"seq": 6, "event": "stage", "stage": 4, "moment": 60, "readings": {}}, {"seq": None, "at": T._at(11), "event": "stop"}]
    (root / "journal" / "2026-09-23.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    try:
        og4.gather(root, Path(d) / "out", 1.0); p("8 STAGE   old gather on a stage event: no error")
    except Exception as e:
        p("8 STAGE   old gather on the mind's stage event row (no `at`) ->", type(e).__name__, e)
R = json.loads((W / "scratch" / "smoke-2h-copy" / "results.json").read_text())
p("9 PARTITION old (alpha4-1's 2 h smoke): MODULATION in marks_failed:", "MODULATION" in R["marks_failed"], "| its reason:", R["marks"]["MODULATION"]["reason"][:70], "| READ graded FAIL, in failed:", "READ" in R["marks_failed"])
p("10 PLANT  old on the smoke: plant shown", R["marks"]["SIZING"]["plant_shown_moments"], "-> SIZING", R["marks"]["SIZING"]["pass"], "GRADE", R["marks"]["GRADE"]["pass"], "(plant answered", R["marks"]["GRADE"]["plant_answered_rate"], ")")
m = ovl.read_mark(*T.ReadBlindTwin()._tape_and_journal(), True, {"n": 50, "correct": 40, "share": 0.8}, None, min_words_born=500, min_frames=1)
p("11 READ blind old: the twin not run ->", m["pass"], "|", m["reason"])
