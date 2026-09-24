# #239 (1): after a merge, every def whose END sits at a hunk boundary — print its last statement; def names unique;
# and every function compared to BOTH parents (equal to one of them, or touched by both -> listed for a hand read)
import ast, subprocess, sys, re, collections
path = sys.argv[1]; merged_ref_paths = sys.argv[2:]   # e.g. HEAD:tools/verdict_g4.py MERGE_HEAD:tools/verdict_g4.py BASE:...
src = open(path).read(); tree = ast.parse(src); lines = src.splitlines()
def funcs(t):
    out = []
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append(n)
    return out
F = funcs(tree)
top = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
names = collections.Counter(n.name for n in top)
dups = {k: v for k, v in names.items() if v > 1}
print("top-level defs:", len(top), "duplicates:", dups or "none")
# hunk boundaries in the merged file vs each parent
bounds = set()
for ref in merged_ref_paths:
    old = subprocess.run(["git", "show", ref], capture_output=True, text=True, check=True).stdout
    d = subprocess.run(["diff", "-U0", "/dev/stdin", path], input=old, capture_output=True, text=True).stdout
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", d, re.M):
        s = int(m.group(1)); c = int(m.group(2) or 1)
        bounds.add(s); bounds.add(s + max(c, 1) - 1); bounds.add(s - 1); bounds.add(s + c)
hit = []
for n in F:
    end = n.end_lineno
    if any(abs(end - b) <= 2 for b in bounds):
        last = n.body[-1]
        hit.append((n.name, n.lineno, end, ast.get_source_segment(src, last).splitlines()[-1][:160] if ast.get_source_segment(src, last) else "?", type(last).__name__))
print(f"defs whose END sits within 2 lines of a hunk boundary ({len(hit)}):")
for h in hit:
    print(f"  {h[0]} [{h[1]}-{h[2]}] last stmt ({h[4]}): {h[3]}")
