"""read_b11.py — the B1.1 records, read for the brain-organ debate (edit: Fable 5.1 (brain r2), 2026-09-27 18:58 +0400).
Reads /data/dev/brain-runs/b1.1/runs/<seed>/<arm>/answers.jsonl (R27's shape: answer{kind,value,raw}, answer_kind,
cues, phase, sitting, truth, correct) and prints, per arm and seed: the NAME-cue TRAINING asks (phase L4, no sitting)
in thirds of their tape order — right / n, distinct answers, the top answer's share, abstentions — and T_L's NAME asks.
Nothing is written but this output. Run: PYTHONPATH=/data/dev/genome-wt-b1-tape2 python read_b11.py > read_b11.out
"""
import json, os, sys
from collections import Counter

ROOT = "/data/dev/brain-runs/b1.1/runs"
ARMS = ["A0", "A1", "A1-TEACH", "A1-BPTT-AWAKE", "A1-LOCAL", "A1-NO-SLEEP", "A1-FIXED", "A1-ATT", "A1-MA", "A1-MLC",
        "A2", "A3", "A4", "A5", "D", "E′", "F", "RING-READ"]


def rows(seed, arm):
    p = f"{ROOT}/{seed}/{arm}/answers.jsonl"
    if not os.path.exists(p):
        return None
    out = []
    with open(p) as f:
        for l in f:
            l = l.strip()
            if l:
                out.append(json.loads(l))
    return out


def describe(rs):
    n = len(rs)
    if n == 0:
        return "n=0"
    right = sum(1 for r in rs if r.get("correct") is True)
    ans = Counter()
    abst = 0
    for r in rs:
        a = r["answer"]
        if a["kind"] == "NAME":
            ans[a["value"]] += 1
        else:
            abst += 1
            ans[f"<{a['kind']}>"] += 1
    top, topn = ans.most_common(1)[0]
    return f"right {right}/{n} ({100*right/n:.0f} %) · distinct {len(ans)} · top {top!r} {100*topn/n:.0f} % · non-NAME {abst}"


for seed in ("20261001", "20261002"):
    print(f"=== seed {seed} ===")
    for arm in ARMS:
        rs = rows(seed, arm)
        if rs is None:
            print(f"  {arm:14s}: (no record)")
            continue
        train = [r for r in rs if r["cues"] == ["NAME"] and r.get("sitting") is None and not r.get("mlc")]
        train.sort(key=lambda r: r["seq"])
        k = len(train) // 3
        thirds = [train[:k], train[k:2 * k], train[2 * k:]]
        tl = [r for r in rs if r["cues"] == ["NAME"] and r.get("sitting") == "T_L"]
        td = [r for r in rs if r["cues"] == ["NAME"] and r.get("sitting") == "T_D"]
        print(f"  {arm:14s} NAME train asks n={len(train)}: all → {describe(train)}")
        for i, t in enumerate(thirds):
            print(f"  {'':14s}   third {i+1} (seq {t[0]['seq']}–{t[-1]['seq']}) → {describe(t)}")
        print(f"  {'':14s} T_L NAME → {describe(tl)}")
        print(f"  {'':14s} T_D NAME → {describe(td)}")
        confs = [r["answer"]["raw"].get("conf") for r in train if isinstance(r["answer"].get("raw"), dict) and "conf" in r["answer"]["raw"]]
        if confs and k > 0 and len(confs) >= len(train):
            c1, c3 = confs[:k], confs[2 * k:]
            print(f"  {'':14s} conf on NAME train asks: first third mean {sum(c1)/len(c1):.3f} · last third mean {sum(c3)/len(c3):.3f} · n with conf {len(confs)}")
    # the tape's own NAME corrections per letter (the denominator of «6 per letter»)
    tape = [json.loads(l) for l in open(f"/data/dev/brain-runs/b1.1/{seed}/tape.jsonl")]
    asks = {r["seq"]: r for r in tape if r["kind"] == "ASK"}
    per = Counter()
    for r in tape:
        if r["kind"] == "FEEDBACK":
            a = asks.get(r["payload"]["ask_seq"])
            if a and a["payload"]["cues"] == ["NAME"]:
                per[r["payload"]["right"]] += 1
    teach = Counter(r["payload"]["name"] for r in tape if r["kind"] == "TEACH")
    print(f"  tape: NAME corrections per name (min/median/max) {min(per.values())}/{sorted(per.values())[len(per)//2]}/{max(per.values())} over {len(per)} names, total {sum(per.values())}; "
          f"TEACH rows per name min/max {min(teach.values())}/{max(teach.values())}, total {sum(teach.values())}; "
          f"SLEEP rows {sum(1 for r in tape if r['kind']=='SLEEP')}; rows {len(tape)}")
