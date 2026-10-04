# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:29 +0400 — reads the gate rows of the real-data runs (R1, R14, R2, R3, R1') and prints the law's comparisons from the FILES: R2's byte identity and row identity,
# the BLAS-4 reading's diff, R3's dose table, R1' against R1. Stdlib only; small files (answers.jsonl is 1.8 MB), far under 1 GB.
# usage: python3 -B compare_runs.py <out-dir holding gate/<label>/>
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
MASK = ("stamp", "cpu", "memory", "wall_s", "answer_meta", "live_load", "label", "nothing_written", "children", "mode_args", "code", "subject", "r3")


def row(label):
    p = OUT / "gate" / label / "gate.json"
    return json.loads(p.read_text()) if p.exists() else None


def ans_bytes(label):
    p = OUT / "gate" / label / "answers.jsonl"
    return p.read_bytes() if p.exists() else None


def norm(r):
    r = json.loads(json.dumps({k: v for k, v in r.items() if k not in MASK}))
    for k in ("items", "grader"):
        if k in r:
            r[k]["pin"] = "-"
    if "state" in r:
        r["state"]["copy_dir"] = "-"
    return r


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16] if b is not None else None


print("== R2 determinism: cold, warm, third (fresh processes) against R1 (also cold)")
labels = ["r1", "r2-cold", "r2-warm", "r2-third"]
rows = {l: row(l) for l in labels}
bytes_ = {l: ans_bytes(l) for l in labels}
for l in labels:
    r = rows[l]
    print(f"  {l:9s} status={r and r['status']!s:6s} answers sha256[:16]={sha(bytes_[l])}  cache hits/misses={r and (r['answer_meta']['glance_cache']['hits'], r['answer_meta']['glance_cache']['misses'])}  cold={r and r['cpu']['cold']}  answer cpu={r and r['cpu']['answer_s']} s")
base = bytes_["r1"]
print("  answers.jsonl byte-identical to R1:", {l: (bytes_[l] == base) for l in labels[1:]})
nr = {l: norm(rows[l]) for l in labels if rows[l]}
print("  gate row identical but stamp/timings/paths (against R1):", {l: (nr[l] == nr["r1"]) for l in labels[1:] if l in nr})
for l in labels[1:]:
    if l in nr and nr[l] != nr["r1"]:
        a, b = nr["r1"], nr[l]
        print("    DIFFERING TOP KEYS in", l, [k for k in set(a) | set(b) if a.get(k) != b.get(k)])

print("== R2 reading: one warm run under OPENBLAS_NUM_THREADS=4 (the pin is law either way)")
rb = row("r2-blas4")
if rb:
    ab = ans_bytes("r2-blas4")
    a1 = [json.loads(x) for x in base.decode().splitlines() if x.strip()]
    a4 = [json.loads(x) for x in ab.decode().splitlines() if x.strip()]
    nd = sum(1 for x, y in zip(a1, a4) if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True))
    print(f"  status={rb['status']} flags={rb['flags']} rows differing from the 1-thread answers: {nd} of {len(a1)} | byte-identical: {ab == base} | R1 (a) {rb['r1a']['n_equal']}/{rb['r1a']['n_asks_on_tape']} equal to the LIFE's rows | R1 (b) equal={rb['r1b']['equal']}")
else:
    print("  (no r2-blas4 row)")

print("== R14: Brain.turn is read-only on a second load of the real state")
r14 = row("r14")
print("  ", r14 and {"status": r14["status"], "turn_check": r14.get("turn_check"), "reason": r14.get("reason")})

print("== R3 sensitivity: the nudge V += eps * std(V) * u on a COPY in memory (the bar is eps 0.5; the rest are readings)")
for e in ("0.001", "0.01", "0.1", "0.5"):
    r = row(f"r3-{e}")
    if not r:
        print(f"  eps {e}: no row")
        continue
    r3 = r.get("r3")
    if r3:
        print(f"  eps {e:6s} status={r['status']:13s} answers changed {r3['answers_changed']:4d} of {r3['answers_compared']}  marks changed {r3['marks_changed']}  hash {r3['hash_before'][:10]} -> {r3['hash_after'][:10]}")
    else:
        print(f"  eps {e:6s} status={r['status']} reason={r.get('reason')}")

print("== R1': brain-long-3's code answering brain-long-2's brain on the same items (R1 (a)/(b) against the life's rows and the reference)")
rp = row("r1p")
if rp:
    print(f"  status={rp['status']} | {rp.get('reading') or rp.get('reason')}")
    print(f"  code={rp['code']} commit={rp['code_commit'].get('commit')} dirty={rp['code_commit'].get('dirty')} modules={len(rp['subject']['modules'])} digest={rp['subject']['modules_digest'][:12]} (R1's {rows['r1']['subject']['modules_digest'][:12]})")
    print(f"  answers byte-identical to R1's: {ans_bytes('r1p') == base}")
    if rp.get("r1a"):
        print("  r1a:", {k: rp["r1a"][k] for k in ("n_resit", "n_equal", "n_diff", "n_missing_life_row", "unanswered")}, "| r1b equal:", rp["r1b"]["equal"])
        if rp["r1a"]["first_diff"]:
            fd = rp["r1a"]["first_diff"]
            print("  FIRST DIFF:", fd["item"], fd["differing_keys"])
else:
    print("  (no r1p row)")
