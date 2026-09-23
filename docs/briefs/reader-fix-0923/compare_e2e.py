# READER-FIX-0923: the dry-life-1 end-to-end reads before (master a17cb0e export) and after (this branch) — every field compared,
# masked only where a clock or a version string lives; the marks the fixes name are listed apart.
import json, sys
B = json.load(open("/data/dev/genome-wt-reader-fix/scratch/e2e-before/results.json"))
A = json.load(open("/data/dev/genome-wt-reader-fix/scratch/e2e-after/results.json"))
VOLATILE = {"at", "seconds_total", "seconds", "ms_per_canvas", "solo_ms_per_canvas_probe", "reader", "reader_commit", "unblinded_replay_ms_under_workers",
            "solo_ms_per_canvas_replay", "cpu_hours", "genome", "root"}
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
print("verdict before:", B["verdict"], B["marks_failed"]); print("verdict after: ", A["verdict"], A["marks_failed"]); print("not gradable after:", A.get("marks_not_gradable")); print("missing graded:", A.get("marks_missing_graded"))
by_top = {}
for p, x, y in d:
    top = p[0] if p else "<root>"; top = f"{p[0]}.{p[1]}" if p and p[0] in ("marks", "twins") and len(p) > 1 else top
    by_top.setdefault(top, []).append((p, x, y))
print(f"\n{len(d)} differing leaves in {len(by_top)} places:")
for top, items in sorted(by_top.items()):
    print(f"  {top}: {len(items)}")
    for p, x, y in items[:6]:
        print("     ", "/".join(map(str, p))[:110], "|", str(x)[:80], "->", str(y)[:80])
