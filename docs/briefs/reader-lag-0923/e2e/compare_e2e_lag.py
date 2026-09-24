# READER-LAG-0923 e2e compare: old (2357347 export) vs new (this branch) results.json on the SAME record.
# A WHITELIST, never an eyeballed diff: the only leaves allowed to differ are NEW leaves under the lag keys; every other
# differing leaf is a leftover and the script exits 1. Clocks, durations and version/path strings are masked by KEY NAME.
import json, sys
old_p, new_p = sys.argv[1], sys.argv[2]
expect_cut = len(sys.argv) > 3 and sys.argv[3] == "--cut"          # the LAG root: the new read is CUT, so the cut-only keys are allowed too
B = json.load(open(old_p)); A = json.load(open(new_p))
VOLATILE = {"at", "seconds_total", "seconds", "ms_per_canvas", "solo_ms_per_canvas_probe", "reader", "reader_commit", "unblinded_replay_ms_under_workers",
            "solo_ms_per_canvas_replay", "cpu_hours", "genome", "root", "reading_window", "heartbeat_at"}
NEW_KEYS = {"tape_rows_world", "LAG", "lag", "cut_seq"}
CUT_ONLY_KEYS = {"mind_reach_full_hours", "hours_beyond_the_minds_reach", "reach_note", "hours_lived", "lag_note"}
def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in VOLATILE: continue
            if k not in a: out.append((path + [k], "<absent>", "new")); continue
            if k not in b: out.append((path + [k], "old", "<absent>")); continue
            walk(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, path + [i], out)
    elif a != b:
        out.append((path, a, b))
d = []; walk(B, A, [], d)
allowed, leftover, cut_only_seen = [], [], []
for p, x, y in d:
    comps = set(map(str, p))
    if x == "<absent>" and y == "new" and comps & NEW_KEYS:
        allowed.append(p)
    elif x == "<absent>" and y == "new" and comps & CUT_ONLY_KEYS:
        (allowed if expect_cut else leftover).append(p if expect_cut else (p, x, y)); cut_only_seen.append(p)
    else:
        leftover.append((p, x, y))
print("verdict old:", B["verdict"], B["marks_failed"]); print("verdict new:", A["verdict"], A["marks_failed"])
print("not gradable old:", [k for k, _ in B.get("marks_not_gradable") or []]); print("not gradable new:", [k for k, _ in A.get("marks_not_gradable") or []])
print("REPLAY old:", {k: B["REPLAY"].get(k) for k in ("pass", "vs_live", "two_replays", "mind_rows", "hash_masked", "closed_whole", "plant_seq", "plant_caught")})
print("REPLAY new:", {k: A["REPLAY"].get(k) for k in ("pass", "vs_live", "two_replays", "mind_rows", "hash_masked", "closed_whole", "plant_seq", "plant_caught", "cut_seq")})
print("ALIVE old:", {k: B["ALIVE"].get(k) for k in ("pass", "hours_on_tape", "every_counter_moved_every_hour", "max_gap_s_eye_ear")})
print("ALIVE new:", {k: A["ALIVE"].get(k) for k in ("pass", "hours_on_tape", "every_counter_moved_every_hour", "max_gap_s_eye_ear", "mind_reach_full_hours")})
print("LAG new:", {k: (A.get("LAG") or {}).get(k) for k in ("cut", "mind_last_seq", "source", "time_cut_seq", "tape_head_seq", "cut_seq", "rows_unconsumed", "rows_cut_by_lag", "status_backlog_rows", "backlog_reconciles", "hours_lived", "hours_on_tape_world")})
print(f"\n{len(d)} differing leaves: {len(allowed)} allowed new lag leaves under {sorted(set(str(p[0]) + ('.' + str(p[1]) if len(p) > 1 else '') for p in allowed))}")
print(f"cut-only keys seen: {len(cut_only_seen)} (expected {'>0' if expect_cut else '0'})")
print(f"LEFTOVER (must be empty): {len(leftover)}")
for p, x, y in leftover[:60]:
    print("   ", "/".join(map(str, p))[:120], "|", str(x)[:90], "->", str(y)[:90])
sys.exit(1 if leftover else 0)
