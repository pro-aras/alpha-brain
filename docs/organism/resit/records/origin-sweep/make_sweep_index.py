# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:34 +0400 (the file's own mtime; the first draft of this header said 21:35 «from `date`», typed ahead of the clock — corrected) — builds docs/organism/resit/records/origin-sweep/INDEX.md's table from the sweeps' own logs and the script's own mutant list, so no verdict is typed by hand.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:55 +0400 (from `date`) — v2: FOUR sweep columns (sweep 1 c887b50, sweep 2 a82ea77, final-1 f31db0f, FINAL 916f741), the first three failing tests of each FINAL mutant as the sweep printed them, and a second table
# that follows every SWEEP-1 SURVIVOR to the test that now kills it and the commit that introduced that test (git log -S on `def test_<name>` in the reader's own history), so «survivor -> killing test -> commit» is computed, not typed.
# usage: python3 -B make_sweep_index.py <mutate_origin.py> <INDEX.md out> <repo checkout with the wip history> <s1 logs> <s2 logs> <final-1 logs> <FINAL logs>   (log lists comma-separated; a later line of a mutant wins)
import re
import subprocess
import sys
from pathlib import Path

SCRIPT, OUT, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
LOGS = {k: [Path(p) for p in v.split(",") if p] for k, v in zip(("s1", "s2", "f1", "fin"), sys.argv[4:8])}
src = open(SCRIPT).read().split("def run_tests")[0]
ns = {}
exec(compile(src, "mutate_origin_head", "exec"), ns)
MUT = ns["MUTATIONS"]
LINE = re.compile(r"^(SURVIVED|CAUGHT-OTHER|CAUGHT)\s+(\w\d\d) (.*?)  \[(.*?)\]  \((\d+) s\)\s*$")


def read(paths):
    got = {}
    for p in paths:
        if not p.exists():
            continue
        for ln in p.read_text(errors="replace").splitlines():
            m = LINE.match(ln)
            if m:
                tests = m.group(4).split("test(s): ")[-1] if "test(s):" in m.group(4) else ""
                got[m.group(2)] = (m.group(1), tests)
    return got


def full_test_names(fragment: str):
    """The sweep prints the first failing names with `test_` stripped and cut to 48 characters: recover EVERY full name that starts with the fragment (a cut name can be ambiguous: a daily-mode test and an origin-mode test may share their first 48 characters)."""
    frag = fragment.strip().rstrip("…").strip()
    if not frag:
        return []
    hits = []
    for f in sorted(Path(REPO, "tests", "tools").glob("test_resit*.py")):
        hits += re.findall(r"def (test_" + re.escape(frag) + r"\w*)\(", f.read_text())
    return sorted(set(hits))


def commit_of(test_name: str):
    r = subprocess.run(["git", "-C", REPO, "log", "--format=%h %s", "-S" + f"def {test_name}(", "--", "tests/tools"], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return lines[-1] if lines else "(not found in this history)"        # the oldest commit that touched the string = the one that introduced it


res = {k: read(v) for k, v in LOGS.items()}
cols = ("s1", "s2", "f1", "fin")
count = {k: sum(1 for m in MUT if res[k].get(m[0], ("",))[0] == "CAUGHT") for k in cols}
ran = {k: sum(1 for m in MUT if m[0] in res[k]) for k in cols}
surv = {k: [m[0] for m in MUT if res[k].get(m[0], ("",))[0] == "SURVIVED"] for k in cols}
other = {k: [m[0] for m in MUT if res[k].get(m[0], ("",))[0] == "CAUGHT-OTHER"] for k in cols}
labels = {"s1": "sweep 1 (c887b50, 59 mutants)", "s2": "sweep 2 (a82ea77, 72 mutants; a later line of a mutant is its rerun)", "f1": "final-1 (f31db0f, 72 mutants in four parts)", "fin": f"FINAL (916f741, {len(MUT)} mutants in four parts)"}
summary = "\n".join(f"- {labels[k]}: run {ran[k]}, CAUGHT {count[k]}, SURVIVED {len(surv[k])}: {', '.join(surv[k]) or 'none'}; CAUGHT-OTHER {len(other[k])}: {', '.join(other[k]) or 'none'}" for k in cols)
head = ["| id | the mutant (one thing the law relies on, broken) | sweep 1 | sweep 2 | final-1 | **FINAL** | named to catch it (substring of a test name) | FINAL: first failing tests as printed |", "|---|---|---|---|---|---|---|---|"]
rows = []
for mid, name, old, new, expected in MUT:
    cells = [(res[k].get(mid) or ("—", ""))[0] for k in cols]
    fin = res["fin"].get(mid) or ("—", "")
    rows.append(f"| {mid} | {name} | {cells[0]} | {cells[1]} | {cells[2]} | **{cells[3]}** | {'; '.join('…' + e + '…' for e in expected)} | {fin[1] or '—'} |")
t2 = ["| sweep-1 survivor | the mutant | FINAL verdict | the test that now kills it | the commit that introduced that test |", "|---|---|---|---|---|"]
for mid in surv["s1"]:
    nm = next(m[1] for m in MUT if m[0] == mid)
    fin = res["fin"].get(mid) or ("—", "")
    first = fin[1].split(", ")[0] if fin[1] else ""
    fulls = full_test_names(first) if first else []
    killers = " <br> ".join(f"`{n}`" for n in fulls) if fulls else (first or "—")
    commits = " <br> ".join(commit_of(n) for n in fulls) if fulls else "—"
    t2.append(f"| {mid} | {nm} | {fin[0]} | {killers}{' (the sweep prints 48 characters: ' + str(len(fulls)) + ' tests share this beginning)' if len(fulls) > 1 else ''} | {commits} |")
Path(OUT).write_text(summary + "\n\n" + "\n".join(head + rows) + "\n\n### Every sweep-1 survivor, followed to the test that kills it\n\n" + "\n".join(t2) + "\n")
print(summary)
