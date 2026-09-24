# every top-level def of the merged file vs the same def in BASE / OURS / THEIRS: which side's bytes it carries
import ast, subprocess, sys
path, base_ref, ours_ref, theirs_ref = sys.argv[1:5]
def defs(src):
    t = ast.parse(src); out = {}
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
    return out
show = lambda r: subprocess.run(["git", "show", r], capture_output=True, text=True, check=True).stdout
M = defs(open(path).read()); B = defs(show(base_ref)); O = defs(show(ours_ref)); T = defs(show(theirs_ref))
both = []
for k, v in M.items():
    b, o, t = B.get(k), O.get(k), T.get(k)
    ch_o = (o != b); ch_t = (t != b)
    if v == o and not ch_t: tag = "ours (theirs unchanged)"
    elif v == t and not ch_o: tag = "theirs (ours unchanged)"
    elif v == o == t: tag = "identical all"
    elif ch_o and ch_t: tag = "TOUCHED BY BOTH -> hand read"; both.append(k)
    else: tag = f"MERGED DIFFERS from both (ch_o={ch_o}, ch_t={ch_t}) -> hand read"; both.append(k)
    if "->" in tag or k in both: print(f"{k}: {tag}")
missing = [k for k in set(O) | set(T) if k not in M]
print("defs in a parent but missing from the merge:", missing or "none")
print("hand-read list:", both)
