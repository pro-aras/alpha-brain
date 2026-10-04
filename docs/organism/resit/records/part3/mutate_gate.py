# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:05 +0400 — a MUTATION SWEEP of tools/brain/resit.py against tests/tools/test_resit_gate.py: each mutation breaks ONE thing the law relies on; the module must go red
# on it (a mutation that survives names a test gap). The original is restored in a `finally` and its sha256 verified. Run through slot, from the worktree root.
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

TARGET = Path("tools/brain/resit.py")
ORIG = TARGET.read_text()
SHA0 = hashlib.sha256(ORIG.encode()).hexdigest()

MUTATIONS = [
    ("M01 R1(a): every row is called equal", "        if rows_equal(r, life):\n            n_equal += 1\n            continue", "        if True:\n            n_equal += 1\n            continue"),
    ("M02 P0: the brain may move after the first ask", "    if above:\n        raise NotGradable(", "    if <<NEVER>>:\n        raise NotGradable("),
    ("M03 R5(b): the find sees nothing", "                if mt > marker_ns:\n                    n_newer += 1", "                if <<NEVER>>:\n                    n_newer += 1"),
    ("M04 R1(b): the tolerance is infinite", "or abs(got - want) > tol:\n            diffs.append", "or <<NEVER>>:\n            diffs.append"),
    ("M05 R4(k): a restart-divergent journal is let through", "        if dup[\"divergent\"]:\n            raise NotGradable(", "        if <<NEVER>>:\n            raise NotGradable("),
    ("M06 AM3: the gate reads the genome by the daily rule (the state's last seq)", "gf = genome_in_force(items_root, js[\"epochs\"], before_seq=int(v[\"begin_seq\"]))", "gf = genome_in_force(items_root, js[\"epochs\"], upto_seq=10**12)"),
    ("M07 R4(j): the grader pin is never compared", "        if old.get(k) != new:\n            raise Refused(f\"grader pin", "        if <<NEVER>>:\n            raise Refused(f\"grader pin"),
    ("M15 R4(j): modules_digest is skipped unconditionally (not only on the pre-check)", "        if k == \"modules_digest\" and new is None and not write:\n            continue", "        if k == \"modules_digest\":\n            continue"),
    ("M08 R7: a CPU-capped child is not named", "    if rc == -24:\n        raise Refused(f\"R7:", "    if <<NEVER>>:\n        raise Refused(f\"R7:"),
    ("M09 R5: an OUT inside the life is allowed", "    if inside is not None:\n        raise Refused(f\"--out", "    if <<NEVER>>:\n        raise Refused(f\"--out"),
    ("M10 §1.0: a run without -B is accepted", "    if not dont_write_bytecode:\n        problems.append(", "    if <<NEVER>>:\n        problems.append("),
    ("M11 R1(a): the life's row is not the LAST row for an ask (the first is taken)", "        last = dict(group[-1])\n        rows[int(seq)] = last", "        last = dict(group[0])\n        rows[int(seq)] = last"),
    ("M12 R3: a plant that changes nothing is accepted", "            if h_after == h_load:\n                raise Refused(", "            if <<NEVER>>:\n                raise Refused("),
    ("M13 R1(a) pass: unanswered asks do not count", "        r1a[\"pass\"] = bool(r1a[\"all_equal\"] and r1a[\"n_resit\"] == scan[\"n_asks\"] and not ameta[\"unanswered\"])", "        r1a[\"pass\"] = bool(r1a[\"all_equal\"])"),
    ("M14 R1 status: PASS without the reference grade", "            elif ref is None:\n                row[\"status\"], row[\"reading\"] = \"PARTIAL\"", "            elif <<NEVER>>:\n                row[\"status\"], row[\"reading\"] = \"PARTIAL\""),
]


def run_tests() -> tuple:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONPATH": ".", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
    p = subprocess.run([sys.executable, "-B", "-u", "-m", "unittest", "tests.tools.test_resit_gate"], capture_output=True, text=True, env=env)
    tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
    return p.returncode, tail


def main() -> int:
    survived = []
    try:
        for name, old, new in MUTATIONS:
            assert ORIG.count(old.replace("<<NEVER>>", "False")) == 1, f"{name}: the anchor is not unique ({ORIG.count(old.replace('<<NEVER>>', 'False'))})"
            mutated = ORIG.replace(old.replace("<<NEVER>>", "False"), new.replace("<<NEVER>>", "False"))
            old = old.replace("<<NEVER>>", "False")
            assert mutated != ORIG, f"{name}: the mutation must change the bytes"
            TARGET.write_text(mutated)
            t0 = time.time()
            rc, tail = run_tests()
            verdict = "CAUGHT" if rc != 0 else "SURVIVED"
            if rc == 0:
                survived.append(name)
            print(f"{verdict:9s} {name}  [{tail}]  ({time.time() - t0:.0f} s)", flush=True)
    finally:
        TARGET.write_text(ORIG)
        sha1 = hashlib.sha256(TARGET.read_text().encode()).hexdigest()
        print(f"restored: sha256 {'equal' if sha1 == SHA0 else 'DIFFERENT'} ({SHA0[:16]})", flush=True)
    print(f"survivors: {survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
