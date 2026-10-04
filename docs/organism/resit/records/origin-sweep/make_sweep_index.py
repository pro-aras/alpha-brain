# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:34 +0400 (the file's own mtime; the first draft of this header said 21:35 «from `date`», typed ahead of the clock — corrected) — builds docs/organism/resit/records/origin-sweep/INDEX.md's table from the sweeps' own logs and the script's own mutant list, so no verdict is typed by hand.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 21:55 +0400 (from `date`) — v2: FOUR sweep columns (sweep 1 c887b50, sweep 2 a82ea77, final-1 f31db0f, FINAL 916f741), the first three failing tests of each FINAL mutant as the sweep printed them, and a second table
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:12 +0400 (from `date`) — optional 8th argument: outputs of one_mutant_all_names.py (every failing name of one mutant) for a survivor whose pre-named test is beyond the three names the sweep prints (C08).
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:13 +0400 (from `date`) — the commit column now says where the test was INTRODUCED and where its BODY last changed (O01 and O23 are killed by old tests strengthened in a82ea77, not by new ones: «introduced» alone would have read as the wrong cause).
# that follows every SWEEP-1 SURVIVOR to the test that now kills it and the commit that introduced that test (git log -S on `def test_<name>` in the reader's own history), so «survivor -> killing test -> commit» is computed, not typed.
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:10 +0400 (from `date`) — the survivor table picks, among the printed failing names, the one that carries a substring the mutant NAMED in advance (the advisor's catch: the first printed name is only the alphabetically first of three, so C08 showed an incidental test); falls back to the first printed and says so.
# usage: python3 -B make_sweep_index.py <mutate_origin.py> <INDEX.md out> <repo checkout with the wip history> <s1 logs> <s2 logs> <final-1 logs> <FINAL logs> [<one-mutant all-names outputs>]   (log lists comma-separated; a later line of a mutant wins)
import re
import subprocess
import sys
from pathlib import Path

SCRIPT, OUT, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
LOGS = {k: [Path(p) for p in v.split(",") if p] for k, v in zip(("s1", "s2", "f1", "fin"), sys.argv[4:8])}
ALLNAMES = {}                                           # mutant id -> the NAMED failing tests read from one_mutant_all_names.py outputs (the sweep prints only three names)
for f in (sys.argv[8].split(",") if len(sys.argv) > 8 else []):
    lines = Path(f).read_text().splitlines() if f else []
    if lines:
        ALLNAMES[lines[0].split()[0]] = [l.split("NAMED", 1)[1].strip() for l in lines if "NAMED" in l and not l.startswith("named in advance")]
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


def _body(src: str, name: str):
    m = re.search(r"^    def " + re.escape(name) + r"\(.*?(?=^    def |^class |\Z)", src, re.M | re.S)
    return m.group(0) if m else None


def commit_of(test_name: str):
    """(introduced, body last changed) as «sha subject» each: walk the commits that touched the file that holds the test, oldest first, comparing the test's own source."""
    files = [f for f in sorted(Path(REPO, "tests", "tools").glob("test_resit*.py")) if f"def {test_name}(" in f.read_text()]
    if not files:
        return "(test not found in this checkout)"
    rel = str(files[0].relative_to(REPO))
    shas = subprocess.run(["git", "-C", REPO, "log", "--format=%h", "--reverse", "--", rel], capture_output=True, text=True).stdout.split()
    intro = last = prev = None
    for s in shas:
        b = _body(subprocess.run(["git", "-C", REPO, "show", f"{s}:{rel}"], capture_output=True, text=True).stdout, test_name)
        if b is None:
            continue
        if intro is None:
            intro = last = s
        elif b != prev:
            last = s
        prev = b
    subj = lambda s: subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h %s", s], capture_output=True, text=True).stdout.strip()[:90]
    if intro is None:
        return "(no commit holds the test)"
    return f"introduced {subj(intro)}" + ("" if last == intro else f"; body last changed {subj(last)}")


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
t2 = ["| sweep-1 survivor | the mutant | FINAL verdict | the failing test that carries a substring the mutant NAMED in advance (else the first printed, marked) | the commit that introduced that test; and the one that last changed its body |", "|---|---|---|---|---|"]
for mid in surv["s1"]:
    nm, exp = next((m[1], m[4]) for m in MUT if m[0] == mid)
    fin = res["fin"].get(mid) or ("—", "")
    printed = [x.strip().rstrip("…").strip() for x in fin[1].split(", ") if x.strip()] if fin[1] else []
    cands = sorted({n for frag in printed for n in full_test_names(frag)})
    named = [n for n in cands if any(e in n for e in exp)]
    if not named and mid in ALLNAMES and ALLNAMES[mid]:
        named = ALLNAMES[mid]                              # read from the one-mutant run that printed EVERY failing name
    if named:
        shown, note = named, ""
    else:
        first = full_test_names(printed[0]) if printed else []
        shown, note = first, " (MARKED: no printed failing name carries a substring the mutant named; the sweep prints only the first three, sorted, cut to 48 characters)"
    killers = " <br> ".join(f"`{n}`" for n in shown) if shown else "—"
    commits = " <br> ".join(commit_of(n) for n in shown) if shown else "—"
    t2.append(f"| {mid} | {nm} | {fin[0]} | {killers}{note} | {commits} |")
Path(OUT).write_text(summary + "\n\n" + "\n".join(head + rows) + "\n\n### Every sweep-1 survivor, followed to the failing test that carries a substring its mutant named in advance\n\n" + "\n".join(t2) + "\n")
print(summary)
