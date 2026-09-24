# READER v3.5 step 5: the IDENTITY mark on two CLOSED root copies, through the reader's OWN functions (tools/verdict_g4.py:side_record +
# ladder2_read's identity branch: identity_mark + wall_reading + wall_band). usage: run_identity.py <root A> <hours A|whole> <root B> [<hours B>]
import json, sys
from datetime import timedelta
from pathlib import Path
sys.path.insert(0, "/data/dev/genome-wt-reader35")
import tools.verdict_g4 as vg
from tools import verdict_life as vl
A_root = Path(sys.argv[1]); hA = None if sys.argv[2] == "whole" else float(sys.argv[2]); B_root = Path(sys.argv[3])
hB = (None if len(sys.argv) < 5 or sys.argv[4] == "whole" else float(sys.argv[4]))
A = vg.side_record(A_root, hA); B = vg.side_record(B_root, hB)
wall_h = hA if hA is not None else 8.0
ta = A["t0"] + timedelta(hours=wall_h); tb = B["t0"] + timedelta(hours=(hB if hB is not None else wall_h))
wa = vl.wall_reading(A["series"], A["status"], vg._canvas_seqs(A["mind"]), ta.timestamp())
wb = vl.wall_reading(B["series"], B["status"], vg._canvas_seqs(B["mind"]), tb.timestamp())
m = vl.identity_mark(A["tape"], A["mind"], B["tape"], B["mind"], wall=vl.wall_band(wa, wb), label_a=A_root.name, label_b=B_root.name)
print(f"A {A_root.name} cut {hA} h (on tape {A['hours_on_tape']} h, closed {A['closed']}, lag cut {A['lag_cut']}) · B {B_root.name} cut {hB} (on tape {B['hours_on_tape']} h, closed {B['closed']})")
print(f"IDENTITY: {'PASS' if m.get('pass') else 'FAIL'} graded {m['graded']} — {m['reason']}")
for s, v in m["streams"].items():
    print(f"  {s:8s} identical {v['identical']:>6,}/{v['compared']:<6,} (a {v['a']:,}, b {v['b']:,}) first divergence {v['first_divergence']}{'' if v['graded'] else '  [printed]'}")
print(f"  meeting points {m['meeting_points']:,} (agree {m['meeting_points_agree']:,}, disagree {m['meeting_points_disagree']}) · canvases {m['canvases_a']:,} / {m['canvases_b']:,} · reach {m['reach']}")
print(f"  last meeting point: {json.dumps(m['last_meeting_point'], default=str)}")
if m.get("id_order_note"): print("  " + m["id_order_note"])
for d in m.get("disagreements") or []: print("  DISAGREE", json.dumps(d, default=str)[:600])
w = m["wall"]
print(f"  WALL: a {json.dumps({k: w['a'].get(k) for k in ('at','source','canvases','cells','sight_born','births','sleeps')})}")
print(f"        b {json.dumps({k: w['b'].get(k) for k in ('at','source','canvases','cells','sight_born','births','sleeps')})} rate/canvas last hour {w['b'].get('rate_per_canvas_last_hour')}")
print(f"        Δcanvases {w['delta_canvases']} · " + "; ".join(f"{k} Δ {v['delta']} (expected from pacing {v.get('expected_from_pacing')}, band ±{v['band']}, inside {v['inside']})" for k, v in w["per_counter"].items()))
print(f"  disagreement max |Δ| {m.get('disagreement_max_abs')} · last agreeing meeting point canvas {m.get('last_agreeing_meeting_point_canvas')} · last meeting point agrees {m.get('last_meeting_point_agrees')}")
for s, v in m["streams"].items():
    if v["first_divergence"]:
        f = v["first_divergence"]; print(f"  {s}: divergence tags a {f.get('tags_a')} b {f.get('tags_b')} realigned {f.get('realigned')}")
