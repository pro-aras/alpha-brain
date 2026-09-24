# READER v3.5 step 5 (light): every ladder-2 mark that needs no replay, through the reader's OWN ladder2_read, on a CLOSED copy (read-only).
# A1_NULL needs the unblinded replay (twins_dir) — not given here, so it reads «no vex reading» (the full reader asks it).
import json, sys
from pathlib import Path
sys.path.insert(0, "/data/dev/genome-wt-reader35")
import tools.verdict_g4 as vg
from genome.machinery import parse_genome
root = Path(sys.argv[1]); hours = float(sys.argv[2]); ctl = (Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != "-" else None)
A = vg.side_record(root, hours)
decl = parse_genome((root / "GENOME.genome").read_text()).declared
M = vg.ladder2_read(root, {"t0": A["t0"], "exams": A["exams"]}, A["tape"], A["mind"], A["status"], decl, hours, control_root=ctl)
print(f"== {root.name} at {hours} h (tape {len(A['tape'])} rows, mind {len(A['mind'])} rows, exams {len(A['exams'])}; control {ctl.name if ctl else None})")
for k in ("X1_LOCK", "X2_SUCCESS", "LINE", "NURSERY", "NURSERY_READ", "DROP_EQ", "CHAT_COUNTERS", "A2_SEEN"):
    print(f"  {k}: {vg.gv_(M[k])} — {str(M[k].get('reason'))[:400]}")
for l in vg.ladder2_rows(M):
    if l.startswith(("| X1_LOCK", "| X2_SUCCESS", "| LINE", "| NURSERY", "| DROP_EQ", "| CHAT_COUNTERS")):
        print("  ROW " + l[:1600])
