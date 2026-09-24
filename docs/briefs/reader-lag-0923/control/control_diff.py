# old G vs new G: the new must equal the old MINUS the new keys (tape_world, lag, hours_on_tape_world); prints the key diff and any leaf that differs.
import json, sys
B = json.load(open(sys.argv[1])); A = json.load(open(sys.argv[2]))
NEW = {"tape_world", "lag", "hours_on_tape_world"}
only_new = sorted(set(A) - set(B)); only_old = sorted(set(B) - set(A))
diffs = []
def walk(a, b, path):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b: diffs.append((path + [k], "<absent>" if k not in b else b[k], "<absent>" if k not in a else a[k])); continue
            walk(a[k], b[k], path + [k])
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): diffs.append((path + ["<len>"], len(b), len(a))); return
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, path + [i])
    elif a != b: diffs.append((path, b, a))
for k in sorted(set(A) & set(B)):
    walk(A[k], B[k], [k])
ok = (set(only_new) == NEW) and not only_old and not diffs
print(json.dumps({"keys_only_in_new": only_new, "keys_only_in_old": only_old, "expected_new_keys": sorted(NEW), "shared_keys_differing_leaves": len(diffs),
                  "first_diffs": [("/".join(map(str, p)), str(x)[:80], str(y)[:80]) for p, x, y in diffs[:8]],
                  "new_lag": {k: A["lag"].get(k) for k in ("cut", "mind_last_seq", "source", "time_cut_seq", "tape_head_seq", "rows_unconsumed", "backlog_reconciles")} if "lag" in A else None,
                  "tape_world_rows_new": len(A.get("tape_world") or []), "tape_rows": len(A["tape"]), "CONTROL": "PASS" if ok else "FAIL"}))
sys.exit(0 if ok else 1)
