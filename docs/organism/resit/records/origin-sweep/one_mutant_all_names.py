# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:11 +0400 (the file's own mtime; the first draft typed 22:12 ahead of the clock — corrected) — applies ONE mutant of mutate_origin.py to the reader in the CURRENT directory (a detached sweep copy), runs the sweep's own TESTS, prints EVERY failing
# test name (the sweep itself prints only the first three, sorted, cut to 48 characters), restores the file and checks its sha256. usage (from the copy): python3 -B one_mutant_all_names.py <mutate_origin.py> <mutant id>
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT, MID = sys.argv[1], sys.argv[2]
ns = {}
exec(compile(open(SCRIPT).read().split("def run_tests")[0], "mutate_origin_head", "exec"), ns)
M = {m[0]: m for m in ns["MUTATIONS"]}
mid, name, old, new, expected = M[MID]
old, new = old.replace("<<NEVER>>", "False"), new.replace("<<NEVER>>", "False")
target = Path("tools/brain/resit.py")
orig = target.read_text()
sha0 = hashlib.sha256(orig.encode()).hexdigest()
assert orig.count(old) == 1
try:
    target.write_text(orig.replace(old, new))
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONPATH": ".", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
    p = subprocess.run([sys.executable, "-B", "-u", "-m", "unittest", *ns["TESTS"]], capture_output=True, text=True, env=env)
    names = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(", p.stderr, re.M)))
finally:
    target.write_text(orig)
print(f"{MID} {name}")
print("named in advance:", expected)
print(f"failing tests ({len(names)}):")
for n in names:
    print("  ", ("NAMED  " if any(e in n for e in expected) else "       ") + n)
print("restored sha256 equal:", hashlib.sha256(target.read_text().encode()).hexdigest() == sha0)
