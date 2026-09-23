# READER-LAG-0923 closed-record control: ONE tree's gather() on ONE root copy at ONE cut, dumped whole (default=str) — old and new run in
# SEPARATE processes (the two trees' modules never share one sys.modules), diffed by control_diff.py.
import importlib.util, json, sys
from pathlib import Path
tree, root, hours, out_json, out_dir = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
spec = importlib.util.spec_from_file_location("vg_ctl", tree / "tools" / "verdict_g4.py"); vg = importlib.util.module_from_spec(spec); spec.loader.exec_module(vg)
out_dir.mkdir(parents=True, exist_ok=True)
G = vg.gather(root, out_dir, hours)
out_json.write_text(json.dumps(G, default=str))
print(json.dumps({"tree": str(tree), "root": root.name, "hours": hours, "keys": sorted(G), "last_seq": G["last_seq"], "closed_whole": G["closed_whole"],
                  "tape_rows": len(G["tape"]), "mind_rows": len(G["mind"]), "events": len(G["events"]), "hours_on_tape": round(G["hours_on_tape"], 4),
                  "lag": ({k: G["lag"].get(k) for k in ("cut", "mind_last_seq", "source", "time_cut_seq", "tape_head_seq", "rows_unconsumed", "backlog_reconciles")} if "lag" in G else None)}))
