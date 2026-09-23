# READER-FIX-0923 control (L-1): the new marks vs the old (master a17cb0e, the pristine export) on the closed records' OWN reader inputs
# (readings/<read>/tape/ALL.jsonl + live-journal.jsonl + the root's STATUS.json + results.json), no replay. Every new line must read
# «not gradable» where the life did not declare it, and every mark's graded/pass must equal the old reading unless the fix names it.
import importlib.util, json, sys
from pathlib import Path
W = Path("/data/dev/genome-wt-reader-fix"); OLD = W / "scratch" / "master-a17cb0e"
sys.path.insert(0, str(W))
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
from tools import verdict_life as new_vl          # the NEW package first: old_g4's top level puts the export's tree on sys.path[0]
from tools import verdict_g4 as new_g4
old_vl = _load("old_vl", OLD / "tools" / "verdict_life.py"); old_g4 = _load("old_g4", OLD / "tools" / "verdict_g4.py")
assert "master-a17cb0e" in old_vl.__file__ and "master-a17cb0e" not in new_vl.__file__, (old_vl.__file__, new_vl.__file__)
from genome.machinery import parse_genome
from genome import world
def gp(m): return (m.get("graded", "—"), m.get("pass"))
rows_out = []; diffs = []
for rec in sorted((W / "scratch" / "records").iterdir()):
    tape = [json.loads(l) for l in open(rec / "tape" / "ALL.jsonl")]
    live = [json.loads(l) for l in open(rec / "live-journal.jsonl")]
    st = json.loads((rec / "STATUS.json").read_text()); R = json.loads((rec / "results.json").read_text()); M = R["marks"]
    g = parse_genome((rec / "GENOME.genome").read_text()); decl = g.declared
    hours = float(R["hours"]); alive = R["ALIVE"]
    out = {}
    out["EVOLVE"] = (gp(old_vl.evolve_mark(tape, live, "EVOLVE" in decl, hours)), gp(new_vl.evolve_mark(tape, live, "EVOLVE" in decl, hours, every_h=(decl.get("EVOLVE") or {}).get("every_h"))))
    solo = R.get("solo_ms_per_canvas_probe"); U = (R.get("twins") or {}).get("unblinded-1") or {}
    out["viii_cost"] = (gp(old_g4.viii_cost(st, solo or U.get("ms_per_canvas"), U.get("ms_per_canvas"), None)),
                        gp(new_g4.viii_cost(st, solo or U.get("ms_per_canvas"), U.get("ms_per_canvas"), None, grow=("GROW" in decl))))
    out["ACT"] = (gp(old_vl.act_mark(tape, live, st)), gp(new_vl.act_mark(tape, live, st)))
    o_s = old_vl.sentence_mark(tape, st, "SENTENCE" in decl); n_s = new_vl.sentence_mark(tape, st, "SENTENCE" in decl)
    out["SENTENCE"] = (gp(o_s), gp(n_s)); sk = new_vl.world_pair_skew(tape)
    out["QUESTION"] = (gp(old_vl.question_mark(live, tape, st, hours, "QUESTION" in decl)), gp(new_vl.question_mark(live, tape, st, hours, "QUESTION" in decl)))
    out["READ"] = (gp(old_vl.read_mark(tape, live, "SENSE_READ" in decl, None, None)), gp(new_vl.read_mark(tape, live, "SENSE_READ" in decl, None, None, blind_reason="not gradable: SENSE_READ not declared")))
    th = bool((decl.get("THINK") or {}).get("threaded"))
    n_th = new_vl.thread_mark(alive, st, th, tape=tape, journal=live)
    out["THREAD"] = (gp(old_vl.thread_mark(alive, st, th)), gp(n_th))
    out["STAGE"] = (gp(old_vl.stage_mark(live, "STAGE_READY" in decl)), gp(new_vl.stage_mark(live, "STAGE_READY" in decl, tape=tape)))
    out["WEB"] = (gp(old_vl.web_mark(tape, live, "DOOR_WEB" in decl)), gp(new_vl.web_mark(tape, live, "DOOR_WEB" in decl)))
    out["SIZING"] = (gp(old_vl.sizing_mark(st, live, None, grow=("GROW" in decl))), gp(new_vl.sizing_mark(st, live, None, grow=("GROW" in decl))))
    own = R.get("own_asks") or {}; seen = ((((R.get("twins") or {}).get("unblinded-1") or {}).get("exam") or {}).get("ask_seen_words")) or {}
    ps = new_vl.plant_showings(live, world.THING_PLANT)
    if own:
        out["GRADE"] = (gp(old_vl.grade_mark(own["plant"], own["null"], seen, "ANSWER" in decl)), gp(new_vl.grade_mark(own["plant"], own["null"], seen, "ANSWER" in decl, plant_shown=ps)))
        vi_old = M["vi_knows_unknown"]
        vi_new = new_g4.vi_mark(own["plant"], own["null"], vi_old["Q5_spiral_abstain"], vi_old["false_abstention"], plant_shown=ps)
        out["vi_knows_unknown"] = ((True, vi_old["pass"]), gp(vi_new))
    mo = old_g4.modulation({"mind": live}, 1.0 - g.theta_n, regime_step=25); mn = new_g4.modulation({"mind": live}, 1.0 - g.theta_n, regime_step=25)
    out["MODULATION(step 25, recomputed)"] = ((True, mo["pass"]), gp(mn))
    out["MODULATION(recorded)"] = ((True, M["MODULATION"]["pass"]), (True, M["MODULATION"]["pass"]))
    vr = M["v_retention"]; out["v_retention"] = ((True, vr["pass"]), gp(new_g4.retention_mark(vr["pairs"])))
    rows_out.append((rec.name, out, {"missions_per_episode": sk["missions"], "missions_per_frame": sk["missions_per_frame"], "plant_shown": ps,
                                     "sleeps": n_th.get("sleeps_on_record"), "gap_in_sleep_min": n_th.get("max_gap_in_sleep_minutes_s"), "gap_outside": n_th.get("max_gap_outside_sleep_minutes_s"),
                                     "old_failed": R.get("marks_failed")}))
    for k, (o, n) in out.items():
        if o != n:
            diffs.append((rec.name, k, o, n))
for name, out, extra in rows_out:
    print(f"== {name}: " + " · ".join(f"{k} {o}->{n}" for k, (o, n) in out.items()))
    print(f"   {extra}")
print("\nDIFFERENCES (old != new):", len(diffs))
for d in diffs: print("  ", d)
