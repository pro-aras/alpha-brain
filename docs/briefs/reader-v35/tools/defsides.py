# for a def touched by both sides: every line each side ADDED is in the merged def; every line each side REMOVED is gone (multiset)
import ast, subprocess, sys, difflib, collections
path, base_ref, ours_ref, theirs_ref = sys.argv[1:5]; names = sys.argv[5:]
def defs(src):
    t = ast.parse(src); return {n.name: ast.get_source_segment(src, n) for n in t.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
show = lambda r: subprocess.run(["git", "show", r], capture_output=True, text=True, check=True).stdout
M = defs(open(path).read()); B = defs(show(base_ref)); O = defs(show(ours_ref)); T = defs(show(theirs_ref))
for k in names:
    m = collections.Counter(M[k].splitlines()); b = B[k].splitlines()
    for side, S in (("ours(a4-int)", O[k]), ("theirs(master)", T[k])):
        s = S.splitlines()
        add = collections.Counter(); rem = collections.Counter()
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, b, s, autojunk=False).get_opcodes():
            if tag in ("replace", "delete"): rem.update(b[i1:i2])
            if tag in ("replace", "insert"): add.update(s[j1:j2])
        missing_add = [l for l, c in add.items() if m[l] < c]
        kept_rem = [l for l, c in rem.items() if m[l] > 0 and add[l] == 0 and collections.Counter(b)[l] - c < m[l]]
        print(f"{k} / {side}: added {sum(add.values())} lines, {len(missing_add)} missing in merge; removed {sum(rem.values())}, {len(kept_rem)} still present")
        for l in missing_add: print("    MISSING ADD:", l.strip()[:170])
        for l in kept_rem: print("    KEPT REMOVED:", l.strip()[:170])
