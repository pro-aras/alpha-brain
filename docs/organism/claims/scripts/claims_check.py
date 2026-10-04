#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 10:57 +0400 — CLAIMS-CHECK-2026-10-03's reproduction: motor / episodes / mouth / evolve, each with its planted control.
"""Reproduction of the three bottleneck verdicts of docs/organism/claims/CLAIMS-CHECK-2026-10-03.md.

READ-ONLY over COPIES of brain-long-2's record (never the live root, RULES #7). From the worktree root:

    mkdir -p scratch/br2 scratch/br2tape scratch/br2evolve
    cp -p /data/dev/genome-lives/brain-long-2/journal/*.jsonl scratch/br2/
    cp -p /data/dev/genome-lives/brain-long-2/tape/*.jsonl    scratch/br2tape/        (the .jsonl rows only, not tape/payload)
    cp -p /data/dev/genome-lives/brain-long-2/evolve/PROPOSAL-*.json scratch/br2evolve/
    cp -p /data/dev/genome-lives/brain-long-2/GENOME.genome /data/dev/genome-lives/brain-long-2/GENOME.v1.genome scratch/br2/
    PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python3 -B docs/organism/claims/scripts/claims_check.py all

Every count prints the PRESENCE of the field it read beside it (#168). Every subcommand ends with a PLANTED control that
must be CAUGHT, and the plant asserts that it changed the data (#247 (5)). A failed assertion exits non-zero."""
from __future__ import annotations

import argparse
import bisect
import collections
import glob
import itertools
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # docs/organism/claims/scripts/claims_check.py -> the worktree root (#199: from __file__)
JDIR = ROOT / "scratch" / "br2"
TDIR = ROOT / "scratch" / "br2tape"
EDIR = ROOT / "scratch" / "br2evolve"
ASKDIR = ROOT / "scratch" / "br2ask"            # cp -rp of root/ask/in and root/ask/out
PDF_STATUS_AT = "2026-10-01T19:04"                   # the PDF's STATUS read, pinned by `said`==1790 and right==2307 (see `mouth`/`motor`)


def jl(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def load_journal(jdir: Path) -> dict:
    """One pass over the journal copy. `act` is a DICT on a game-act choice row and the STRING 'glance' etc. on an eye row."""
    J = {"rows": 0, "choices": [], "outs": [], "says": [], "epochs": [], "seq_when": ([], [])}
    for fn in sorted(glob.glob(str(jdir / "*.jsonl"))):
        for d in jl(fn):
            J["rows"] += 1
            seq = d.get("seq")
            if "when" in d and isinstance(seq, int):
                J["seq_when"][0].append(seq)
                J["seq_when"][1].append(d["when"])
            a = d.get("act")
            if isinstance(a, dict):
                J["choices"].append((seq, a.get("act"), a.get("act_idx"), a.get("policy"), a.get("weights"), a.get("game")))
            o = d.get("outcome")
            if isinstance(o, dict) and o.get("source") == "game":
                J["outs"].append((seq, o))
            s = d.get("say")
            if isinstance(s, dict):
                J["says"].append((seq, s))
            if isinstance(d.get("epoch"), dict):
                J["epochs"].append((seq, d["epoch"]))
    return J


def when_of(J, seq):
    seqs, whens = J["seq_when"]
    i = bisect.bisect_left(seqs, seq)
    return whens[min(i, len(whens) - 1)]


def load_tape(tdir: Path) -> dict:
    T = {"rows": 0, "by_sense": collections.Counter(), "game_outcome": [], "eye_src": collections.Counter(), "ear_src": collections.Counter(),
         "word_src": collections.defaultdict(collections.Counter), "proposal_rows": 0}
    for fn in sorted(glob.glob(str(tdir / "*.jsonl"))):
        for d in jl(fn):
            T["rows"] += 1
            sense = d.get("sense")
            T["by_sense"][sense] += 1
            m = d.get("meta") or {}
            if sense == "outcome" and m.get("source") == "game":
                T["game_outcome"].append((d["seq"], d["at"], m))
            elif sense == "eye":
                T["eye_src"][m.get("source")] += 1
            elif sense == "ear":
                T["ear_src"][m.get("source")] += 1
                if m.get("word") is not None:
                    T["word_src"][m["word"]][m.get("source")] += 1
            elif sense == "proposal":
                T["proposal_rows"] += 1
    return T


def check(cond, msg):
    if not cond:
        print("ASSERTION FAILED:", msg)
        raise SystemExit(1)
    print("  ok:", msg)


# ======================================================================================== (a) MOTOR
def motor(J):
    print("== (a) MOTOR  (journal copy: %d rows)" % J["rows"])
    ch, outs = J["choices"], J["outs"]
    print("game act CHOICE rows (journal rows whose `act` is a dict):", len(ch))
    print("  presence: policy %d  weights %d  act_idx %d" % (sum(1 for c in ch if c[3] is not None), sum(1 for c in ch if c[4] is not None), sum(1 for c in ch if c[2] is not None)))
    print("  by policy:", dict(collections.Counter(c[3] for c in ch)), " by game:", dict(collections.Counter(c[5] for c in ch)))
    byact = collections.Counter(c[1] for c in ch)
    print("  by act:", dict(byact), " right share of ALL game choices: %d/%d = %.4f" % (byact["right"], len(ch), byact["right"] / len(ch)))
    og = outs
    print("game OUTCOME rows:", len(og), " presence: got %d expected %d residual %d" % (sum(1 for _, o in og if "got" in o), sum(1 for _, o in og if "expected" in o), sum(1 for _, o in og if "residual" in o)))
    nz = [(s, o) for s, o in og if o.get("got") not in (None, 0, 0.0)]
    print("  non-zero got:", len(nz), "by act", dict(collections.Counter(o["act"] for _, o in nz)))
    rn = collections.Counter(); ordinal = {}
    for s, o in og:
        rn[o["act"]] += 1
        if o.get("got") not in (None, 0, 0.0):
            ordinal[s] = rn[o["act"]]
    for s, o in nz:
        print("   reward at seq %d  %s  act %s  got %.7g  (the %d-th `%s` outcome)  expected_before %.6g" % (s, when_of(J, s), o["act"], o["got"], ordinal[s], o["act"], o["expected"] or 0.0))
    # replay: weights re-derived from the outcome rows alone (mind.py:2042-2043 + :1053-1057), compared with the chooser's own journalled weights
    idx2name = {c[2]: c[1] for c in ch}
    names = [idx2name[i] for i in range(len(idx2name))]
    print("  act index -> name (from the choice rows):", {i: n for i, n in enumerate(names)})
    stream = sorted([(s, 0, o) for s, o in og] + [(c[0], 1, c) for c in ch], key=lambda x: (x[0], x[1]))   # an outcome with the same seq is filed before a choice
    def replay(nudge_seq=None):
        sur = collections.defaultdict(list); mism = 0; checked = 0; maxd = 0.0
        for seq, kind, p in stream:
            if kind == 0:
                r = p.get("residual")
                if nudge_seq is not None and seq == nudge_seq:
                    r = (r or 0.0) + 0.05
                sur[p["act"]].append(float(r) if r is not None else 0.0)
            else:
                w = []
                for nm in names:
                    last = sur[nm][-10:]
                    w.append(round(sum(last) / len(last), 6) if last else 0.0)
                checked += 1
                lw = p[4]
                d = max(abs(a - b) for a, b in zip(w, lw))
                maxd = max(maxd, d)
                if d > 1e-9:
                    mism += 1
        return checked, mism, maxd
    c0, m0, d0 = replay()
    print("  REPLAY of weights from outcome rows: choices checked %d, mismatches %d, max |diff| %.3g" % (c0, m0, d0))
    check(m0 == 0 and c0 == len(ch), "the weights re-derived from the outcome rows equal the journalled weights on every choice")
    plant_seq = nz[0][0]
    c1, m1, d1 = replay(nudge_seq=plant_seq)
    print("  PLANT (+0.05 on the residual of the outcome at seq %d): mismatches %d, max |diff| %.3g" % (plant_seq, m1, d1))
    check(m1 > 0 and d1 > 0, "the planted residual nudge is CAUGHT (and it changed the data: max |diff| > 0)")
    # lock census
    ridx = names.index("right")
    all_zero = sum(1 for c in ch if all(v == 0.0 for v in c[4]))
    only_r = [c for c in ch if c[4][ridx] > 0 and all(v == 0.0 for i, v in enumerate(c[4]) if i != ridx)]
    other_nz = sum(1 for c in ch if any(v != 0.0 for i, v in enumerate(c[4]) if i != ridx))
    first_pos = next(c[0] for c in ch if c[4][ridx] > 0)
    zero_after = sum(1 for c in ch if c[0] > first_pos and c[4][ridx] == 0.0)
    print("  lock census: all-zero weights %d | only `right` nonzero %d | any OTHER act nonzero %d | first weight[right]>0 at seq %d, choices after it with weight[right]==0: %d" % (all_zero, len(only_r), other_nz, first_pos, zero_after))
    cr = sum(1 for c in only_r if c[1] == "right")
    sd = math.sqrt((0.9 + 0.1 / 7) * (0.1 - 0.1 / 7) / len(only_r))
    print("  locked choices: right %d/%d = %.4f ; pure-lock expectation 0.9+0.1/7 = %.4f (binomial sd %.4f)" % (cr, len(only_r), cr / len(only_r), 0.9 + 0.1 / 7, sd))
    check(other_nz == 0 and zero_after == 0, "no other act ever carries weight; weight[right] is never 0 again after the first reward")
    check(abs(cr / len(only_r) - (0.9 + 0.1 / 7)) < 3 * sd, "the locked share of `right` is the 10 %-uniform-floor lock (within 3 sd)")
    # the explore floor
    st = json.load(open(JDIR / "STATUS.json")) if (JDIR / "STATUS.json").exists() else {}
    if st:
        print("  STATUS snapshot (heartbeat %s): act_explored %s, acts_chosen right %s, act_policy %s, act_weights %s" % (st.get("heartbeat_at"), st.get("act_explored"), (st.get("acts_chosen") or {}).get("right"), st.get("act_policy"), st.get("act_weights")))
        print("  explore draws / game choices = %s / %d = %.4f (uniform floor 0.1; mind.py:2054-2056)" % (st.get("act_explored"), len(ch), (st.get("act_explored") or 0) / len(ch)))
    # the PDF's moment: the 2,307th right
    cum = collections.Counter(); at = None
    for i, c in enumerate(ch):
        cum[c[1]] += 1
        if c[1] == "right" and cum["right"] == 2307:
            at = i
            break
    c_at = ch[at]
    tot = at + 1
    print("  THE PDF's MOMENT: the 2,307th `right` choice = seq %d at %s ; weights then %s" % (c_at[0], when_of(J, c_at[0]), c_at[4]))
    check(c_at[4] == [0.0, 0.000423, 0.0, 0.0, 0.0, 0.0, 0.0], "the PDF's weight vector is in the journal exactly at its 2,307th right")
    print("  at that moment: total game choices %d  by act %s" % (tot, dict(cum)))
    print("  right share of all choices %.4f (the PDF says 92.6 %%)" % (cum["right"] / tot))
    first_reward_idx = next(i for i, c in enumerate(ch) if c[0] > nz[0][0])
    since = collections.Counter(c[1] for c in ch[first_reward_idx:at + 1])
    print("  since the first reward (choices %d..%d): right %d/%d = %.4f" % (first_reward_idx, at, since["right"], sum(since.values()), since["right"] / sum(since.values())))
    mv = cum["right"] + cum["left"] + cum["forward"]
    print("  right/(right+left+forward) = %.4f" % (cum["right"] / mv))
    others = {k: v for k, v in cum.items() if k != "right"}
    lo, hi = 2307 / 0.9265 - 2307, 2307 / 0.9255 - 2307
    subs = [(sum(v for _, v in sub), [k for k, _ in sub]) for r in range(1, len(others) + 1) for sub in itertools.combinations(others.items(), r) if lo <= sum(v for _, v in sub) <= hi]
    wins = []
    seqs_right = [1 if c[1] == "right" else 0 for c in ch[:tot]]
    for W in range(20, tot + 1):
        s = sum(seqs_right[tot - W:]) / W
        if 0.9255 <= s < 0.9265:
            wins.append(W)
    print("  92.6 %%: a denominator 2307+S needs S in [%.1f, %.1f]; subsets of the other six acts with such a sum: %s ; TRAILING windows ending there that read 92.6 %%: %d (W = %s ...)" % (lo, hi, subs, len(wins), wins[:14]))
    check(not subs and len(wins) > 1, "92.6 % is not the all-choices share, not a subset-sum denominator, and not uniquely a window: NOT RECOVERABLE from the PDF's text")


# ======================================================================================== episodes (tape)
def episodes(J, T):
    print("== EPISODES  (tape copy: %d rows)" % T["rows"])
    go = T["game_outcome"]
    print("game outcome rows on the tape:", len(go), " presence: " + " ".join("%s %d" % (k, sum(1 for _, _, m in go if k in m)) for k in ("terminated", "truncated", "episode", "step", "got", "act", "chosen_by")))
    print("  chosen_by:", dict(collections.Counter(m.get("chosen_by") for _, _, m in go)))
    def tally(rows):
        term = [r for r in rows if r[2].get("terminated")]
        trunc = [r for r in rows if r[2].get("truncated")]
        rew = sum(r[2]["got"] for r in rows if r[2].get("got") is not None)
        return term, trunc, rew
    term, trunc, rew = tally(go)
    done = len(term) + len(trunc)
    print("  COMPLETED episodes %d = %d terminated (success) + %d truncated; sum(got) %.6f" % (done, len(term), len(trunc), rew))
    print("  success per completed episode %.4f ; reward per completed episode %.4f ; mean reward per STEP %.6f" % (len(term) / done, rew / done, rew / len(go)))
    for s, at, m in term:
        print("   success: episode %s global step %s act %s got %s at %s (seq %d)" % (m["episode"], m["step"], m["act"], m["got"], at, s))
    eps = set(m["episode"] for _, _, m in go)
    open_eps = sorted(eps - set(m["episode"] for _, _, m in term + trunc))
    print("  episodes seen %d, completed %d, STILL OPEN %s" % (len(eps), len(eps) - len(open_eps), open_eps))
    p = 0.29
    cdf = sum(math.comb(done, i) * p ** i * (1 - p) ** (done - i) for i in range(len(term) + 1))
    print("  random worker 0.29 per episode (docs/ALPHA4-PREREG.md:33): expected successes %.1f of %d ; P(X <= %d | Binomial(%d, 0.29)) = %.3e" % (p * done, done, len(term), done, cdf))
    # the PDF's moment
    ch = J["choices"]
    cum = 0; moment_seq = None
    for c in ch:
        if c[1] == "right":
            cum += 1
            if cum == 2307:
                moment_seq = c[0]
                break
    sub = [r for r in go if r[0] <= moment_seq + 6]    # outcome rows filed up to that choice's own outcome
    t2, r2, rew2 = tally(sub)
    d2 = len(t2) + len(r2)
    print("  AT THE PDF's MOMENT (tape outcome rows up to seq %d): steps %d, completed episodes %d (%d success), success per episode %.4f, reward per episode %.4f" % (moment_seq + 6, len(sub), d2, len(t2), len(t2) / d2, rew2 / d2))
    check(len(term) == 3 and done == 79 and abs(len(term) / done - 0.0380) < 1e-3, "3 successes in 79 completed episodes = 0.038 (the figure alpha4-1 had)")
    # planted control: flip one truncated row to terminated in a copy -> successes must move 3 -> 4
    victim = trunc[0]
    m2 = dict(victim[2]); m2["terminated"] = True
    changed = (m2 != victim[2])
    go2 = [(s, a, (m2 if (s == victim[0]) else m)) for s, a, m in go]
    t3, _, _ = tally(go2)
    print("  PLANT (flip `terminated` on the truncated row at seq %d): successes %d -> %d" % (victim[0], len(term), len(t3)))
    check(changed and len(t3) == len(term) + 1, "the planted terminated-flag flip is CAUGHT (and changed the row)")


# ======================================================================================== (b) MOUTH
def mouth(J, T):
    print("== (b) MOUTH  (journal copy: %d rows)" % J["rows"])
    says = J["says"]
    spoken = [(s, d) for s, d in says if d.get("heard") in ("yes", "no")]
    other = [(s, d) for s, d in says if d.get("heard") not in ("yes", "no")]
    refused = [x for x in other if x[1].get("outcome") == "refused"]
    print("journal rows with a `say` dict:", len(says), "= SPOKEN by the cells' MOUTH (carry `heard`) %d + other %d (of which refused-uncited %d)" % (len(spoken), len(other), len(refused)))
    print("  presence in the SPOKEN rows: frame %d episodes %d heard %d" % (sum(1 for _, d in spoken if "frame" in d), sum(1 for _, d in spoken if "episodes" in d), sum(1 for _, d in spoken if "heard" in d)))
    kk = collections.Counter(k for _, d in other for k in d.keys())
    print("  the other rows are the BRAIN's say (keys %s); count %d" % (dict(kk), len(other)))
    hy = sum(1 for _, d in spoken if d["heard"] == "yes")
    print("  heard yes %d / no %d -> no-share %.4f" % (hy, len(spoken) - hy, (len(spoken) - hy) / len(spoken)))
    c = 0; n_no = 0; at1790 = None
    for s, d in spoken:
        c += 1; n_no += d["heard"] == "no"
        if c == 1790:
            at1790 = (s, when_of(J, s), n_no, n_no / c)
            break
    print("  THE 1,790th SPOKEN FRAME: seq %d at %s : cumulative no %d / 1790 = %.4f   (the PDF: «1,790 queries spoken», «84.4 %%»)" % at1790)
    check(at1790[2] == 1510 and abs(at1790[3] - 0.844) < 0.0005, "1,510 of 1,790 = 84.36 % = the PDF's 84.4 %, EXACTLY, at the 1,790th spoken frame")
    ser = []; c = 0; n_no = 0
    for s, d in spoken:
        c += 1; n_no += d["heard"] == "no"
        if c % 250 == 0:
            ser.append((c, round(n_no / c, 3)))
    print("  cumulative no-share every 250 spoken:", ser)
    wins = []
    for i in range(0, len(spoken), 500):
        w = spoken[i:i + 500]
        wins.append((i, len(w), round(sum(1 for _, d in w if d["heard"] == "no") / len(w), 3)))
    print("  no-share by 500-frame window (start, n, no-share):", wins)
    # grounded vs text frames, by the SOURCES each word was heard from on the tape (ear rows)
    ws = T["word_src"]
    def grounded_word(w):
        return bool(set(ws.get(w, {}).keys()) & {"game", "scene", "maker"})
    print("  tape ear rows: %d, with word %d, by source %s ; distinct words %d" % (T["by_sense"]["ear"], sum(sum(v.values()) for v in ws.values()), dict(T["ear_src"]), len(ws)))
    def comp(rows, label):
        g = [d for _, d in rows if all(grounded_word(w) for w in d["frame"].split(" ", 1))]
        t = [d for _, d in rows if not all(grounded_word(w) for w in d["frame"].split(" ", 1))]
        gy = sum(1 for d in g if d["heard"] == "yes"); ty = sum(1 for d in t if d["heard"] == "yes")
        n = len(rows)
        print("  %-26s n=%4d | GROUNDED frames n=%4d yes=%3d no-share %.4f | TEXT frames n=%4d yes=%3d no-share %.4f | blended no-share %.4f" % (label, n, len(g), gy, 1 - gy / max(1, len(g)), len(t), ty, 1 - ty / max(1, len(t)), 1 - (gy + ty) / n))
        return len(g), gy, len(t), ty
    g1 = comp(spoken[:1790], "first 1,790 (the PDF's)")
    comp(spoken, "all %d (now)" % len(spoken))
    comp(spoken[1790:], "after the PDF")
    fc = collections.Counter(d["frame"] for _, d in spoken); fy = collections.Counter(d["frame"] for _, d in spoken if d["heard"] == "yes")
    print("  distinct spoken frames %d ; frames ever heard yes (%d): %s" % (len(fc), len(fy), [(f, n, fy[f]) for f, n in fc.most_common() if fy[f]]))
    gyes = sum(fy[f] for f in fy if all(grounded_word(w) for w in f.split(" ", 1)))
    print("  heard-yes from GROUNDED frames %d of %d total yes" % (gyes, hy))
    first_text = next(i for i, (_, d) in enumerate(spoken) if not all(grounded_word(w) for w in d["frame"].split(" ", 1)))
    print("  first TEXT frame at spoken index %d (seq %d, %r)" % (first_text, spoken[first_text][0], spoken[first_text][1]["frame"]))
    print("  tape eye rows by source:", dict(T["eye_src"]), " (shelf = the reader's sentence RENDERED on a canvas the eye sees)")
    check(g1[0] + g1[2] == 1790 and g1[2] > 0 and (1 - g1[1] / g1[0]) > 0.5, "at the PDF's cutoff the GROUNDED frames alone already read a no-share above 0.5")
    # planted control: flip ONE `heard` no->yes in a copy; the no-count must drop by exactly 1
    victim_i = next(i for i, (_, d) in enumerate(spoken) if d["heard"] == "no")
    spoken2 = [(s, dict(d)) for s, d in spoken]
    before = sum(1 for _, d in spoken2 if d["heard"] == "no")
    spoken2[victim_i][1]["heard"] = "yes"
    after = sum(1 for _, d in spoken2 if d["heard"] == "no")
    print("  PLANT (flip one `heard` no->yes in a copy): no-count %d -> %d" % (before, after))
    check(spoken2[victim_i][1] != spoken[victim_i][1] and after == before - 1, "the planted heard-flip is CAUGHT (and changed the row)")
    # the world door never answered a mouth question: ask/in is empty, ask/out holds the questions (the mouth's `is`, the mind's own)
    qf = [json.load(open(p)) for p in sorted(glob.glob(str(ASKDIR / "out" / "q-*.json")))]
    in_files = sorted(os.listdir(ASKDIR / "in"))
    byfrom = collections.Counter(q.get("from") for q in qf)
    print("  ask/out question files %d (by `from` %s; `q` %s) ; ask/in (the door's answers) %d files" % (len(qf), dict(byfrom), dict(collections.Counter(q.get("q") for q in qf)), len(in_files)))
    def door_answered_none(listing):
        return len(listing) == 0 and byfrom["mouth"] >= len(spoken) and byfrom["mouth"] > 0
    check(door_answered_none(in_files),
          "the world door has answered NONE of the mouth's `is` questions (ask/in holds 0 files; ask/out holds the mouth's %d): «rejected» is not a door's verdict" % byfrom["mouth"])
    planted_in = in_files + ["q-0.json"]
    check(planted_in != in_files and not door_answered_none(planted_in), "PLANT (one fake answer file added to a copy of the listing) is CAUGHT: the zero-answers test fails on it")
    st = json.load(open(JDIR / "STATUS.json")) if (JDIR / "STATUS.json").exists() else {}
    if st:
        b = (st.get("brain") or {}).get("turns") or {}
        print("  STATUS snapshot (heartbeat %s): said %s heard_yes %s heard_no %s frames_filed %s frames_scored %s frames_true %s ; brain.turns %s" % (st.get("heartbeat_at"), st.get("said"), st.get("heard_yes"), st.get("heard_no"), st.get("frames_filed"), st.get("frames_scored"), st.get("frames_true"), b))
        print("  (the snapshot is later than the journal copy by minutes: counts may differ by the rows written in between)")


# ======================================================================================== (c) EVOLVE
def evolve(J, T):
    print("== (c) EVOLVE  (proposal files: %s)" % EDIR)
    sys.path.insert(0, str(ROOT))
    from tools.evolve import regression_bar, MARGINS, COST_RATIO_BAR
    from creature.genes import draw_mutation
    props = {}
    for fn in sorted(glob.glob(str(EDIR / "PROPOSAL-*.json")), key=lambda p: int(os.path.basename(p)[9:-5])):
        p = json.load(open(fn))
        props[p["no"]] = (p, os.path.getmtime(fn))
    print("proposal files %d ; tape `proposal` rows %d ; presence of `verdict` %d/%d" % (len(props), T["proposal_rows"], sum(1 for p, _ in props.values() if "verdict" in p), len(props)))
    st = json.load(open(JDIR / "STATUS.json")) if (JDIR / "STATUS.json").exists() else {}
    print("  STATUS snapshot: evolve_proposals_seen %s evolve_epoch %s" % (st.get("evolve_proposals_seen"), st.get("evolve_epoch")))
    print("  verdicts:", dict(collections.Counter(p["verdict"] for p, _ in props.values())))
    print("  no  gene                    value    verdict  q1 inc->mut (items/110)   frames inc->mut   written(+04)       reason")
    import datetime as _dt
    for no, (p, mt) in props.items():
        inc, mut = p.get("incumbent") or {}, p.get("mutant") or {}
        q = ("%3d->%3d" % (round(inc["q1_seen"] * 110), round(mut["q1_seen"] * 110))) if inc.get("q1_seen") is not None else "   -"
        ff = ("%2s->%2s" % (inc.get("frames_filed"), mut.get("frames_filed"))) if inc else "  -"
        print("  %2d  %-22s %-8s %-8s %-24s %-16s  %s  %s" % (no, p.get("gene"), p.get("value"), p["verdict"], q, ff, _dt.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"), (p.get("reason") or "")[:70]))
    at_pdf = [no for no, (p, mt) in props.items() if mt <= _dt.datetime(2026, 10, 1, 23, 43).timestamp()]
    print("  proposals written by the PDF's 23:43 +04 stamp (10-01): %s" % at_pdf)
    vs = collections.Counter(props[n][0]["verdict"] for n in at_pdf)
    print("  their verdicts: %s ; the PASS(es): %s" % (dict(vs), [n for n in at_pdf if props[n][0]["verdict"] == "PASS"]))
    check(len(at_pdf) == 8 and vs["PASS"] == 1, "at the PDF's own stamp there were 8 proposals and ONE of them was a PASS: «8 out of 8 rejected» is FALSE then, not only now")
    # the dead dimensions, with presence counts
    judged = [p for no, (p, _) in props.items() if no > 1]
    print("  DEAD DIMENSIONS over the %d judged rounds (incumbent side; the mutant side is identical):" % len(judged))
    for k in ("confirmed_share", "sentence_pass", "reward_mean", "act_pass", "q1_seen", "frames_filed"):
        present = sum(1 for p in judged if p["incumbent"].get(k) is not None)
        nonzero = sum(1 for p in judged if p["incumbent"].get(k) not in (None, 0, 0.0, False))
        print("   %-16s non-None in %2d/%d rounds ; non-zero/True in %2d  %s" % (k, present, len(judged), nonzero, "NOT GRADABLE in every round" if present == 0 else ""))
    # which readings ever DIFFER between the two twins (a mark that cannot differ cannot gate)
    keys = ("q1_seen", "frames_filed", "reward_mean", "act_pass", "confirmed_share", "sentence_pass", "wall_s")
    def census(pp):
        return {k: sum(1 for p in pp if p["incumbent"].get(k) != p["mutant"].get(k)) for k in keys}
    cen = census(judged)
    print("  TWIN-DIFFERENCE census over the %d judged rounds (rounds where incumbent != mutant): %s" % (len(judged), cen))
    print("   sentence_mark missions per round (the bar needs 100): %s" % [p["incumbent"]["detail"]["sentence"].get("missions") for p in judged])
    check(cen["reward_mean"] == 0 and cen["act_pass"] == 0 and cen["confirmed_share"] == 0 and cen["sentence_pass"] == 0 and cen["q1_seen"] > 0 and cen["frames_filed"] > 0,
          "only q1_seen and frames_filed (and the cost) ever differ between the twins; reward_mean/act_pass are the TAPE's (identical by construction), confirmed_share/sentence_pass are None")
    judged2 = [json.loads(json.dumps(p)) for p in judged]
    judged2[0]["mutant"]["reward_mean"] = 123.0
    cen2 = census(judged2)
    print("  PLANT (set one mutant's reward_mean to 123.0 in a copy): reward_mean differs in %d -> %d rounds" % (cen["reward_mean"], cen2["reward_mean"]))
    check(judged2[0]["mutant"]["reward_mean"] != judged[0]["mutant"]["reward_mean"] and cen2["reward_mean"] == 1, "the planted reward_mean difference is CAUGHT by the census")
    # E3: the call at tools/evolve.py:151 passes its arguments shifted by one to surprise_mark
    import inspect, re, itertools as _it
    from tools.verdict_life import surprise_mark
    params = list(inspect.signature(surprise_mark).parameters)[:4]
    src = (ROOT / "tools" / "evolve.py").read_text()
    call = re.search(r"surprise_mark\(([^)]*)\)", src.split("def grade_twin", 1)[1])
    cargs = [a.strip() for a in call.group(1).split(",")]
    g4 = re.search(r"surprise_mark\(([^)]*)\)", (ROOT / "tools" / "verdict_g4.py").read_text().split("M[\"SURPRISE\"] =", 1)[1])
    print("  surprise_mark parameters: %s ; tools/evolve.py grade_twin passes: %s ; tools/verdict_g4.py passes: %s" % (params, cargs, [a.strip() for a in g4.group(1).split(",")]))
    check(params[:3] == ["journal", "status", "surprise_declared"] and cargs[:3] == ["tape_slice", "journal_rows", "status"],
          "evolve.py passes (tape_slice, journal_rows, status, declared) to surprise_mark(journal, status, surprise_declared, source_of, ...): every argument is one place off")
    jr = list(jl(JDIR / "2026-10-03.jsonl"))
    tp = list(_it.islice(jl(TDIR / "2026-10-03.jsonl"), 3000))
    withm = sum(1 for r in jr if "moment" in r); withc = sum(1 for r in jr if "moment" in r and "confirmed" in r)
    print("  real rows: journal rows %d, with `moment` %d, with `moment` AND `confirmed` %d ; tape-slice rows %d, with a top-level `confirmed` %d" % (len(jr), withm, withc, len(tp), sum(1 for r in tp if "confirmed" in r)))
    good = surprise_mark(jr, {}, True)
    bad = surprise_mark(tp, jr, {}, True)
    print("  CORRECT order : graded %s overall_share %s" % (good.get("graded"), good.get("overall_share")))
    print("  EVOLVE's order: graded %s overall_share %s reason %r" % (bad.get("graded"), bad.get("overall_share"), bad.get("reason")))
    check(withm == withc > 0 and good.get("overall_share") is not None and bad.get("overall_share") is None and "SURPRISE" in (JDIR / "GENOME.genome").read_text(),
          "the same data grades with the right call and reads «not gradable: SURPRISE not declared…» through evolve.py's call, though SURPRISE IS declared in the genome and the rows DO carry `confirmed`")
    stripped = [{k: v for k, v in r.items() if k != "confirmed"} for r in jr]
    ctl = surprise_mark(stripped, {}, True)
    print("  PLANT (the same journal rows with `confirmed` stripped, called CORRECTLY): overall_share %s" % ctl.get("overall_share"))
    check(len(stripped) == len(jr) and any("confirmed" in r for r in jr) and ctl.get("overall_share") is None, "stripping `confirmed` makes even the correct call read None: the reader can tell a dead input, so the shift (not the data) is what killed the mark")
    # adoption
    g0 = (JDIR / "GENOME.genome").read_text().splitlines(); g1 = (JDIR / "GENOME.v1.genome").read_text().splitlines()
    diff = [(a, b) for a, b in zip(g0, g1) if a != b]
    print("  GENOME.genome vs GENOME.v1.genome: %d line(s) differ (same line count %s): %s" % (len(diff), len(g0) == len(g1), [(a.split("#")[0].strip(), b.split("#")[0].strip()) for a, b in diff]))
    print("  journal `epoch` rows: %s" % [(s, e) for s, e in J["epochs"]])
    check(len(diff) == 1 and diff[0][0].split("#")[0].split() == ["KWTA", "5"] and diff[0][1].split("#")[0].split() == ["KWTA", "4"] and len(J["epochs"]) == 1 and J["epochs"][0][1].get("proposal_no") == 5,
          "the launch genome says KWTA 5, the ADOPTED genome says KWTA 4 (proposal 5, journal epoch row), so the PDF's «KWTA 5» was stale at its own timestamp")
    # the epoch row's genome_sha IS the sha256 of GENOME.v1.genome: the adopted genome is that very file
    import hashlib
    sha_file = hashlib.sha256((JDIR / "GENOME.v1.genome").read_bytes()).hexdigest()
    sha_row = J["epochs"][0][1]["genome_sha"]
    print("  epoch row genome_sha %s... ; sha256(GENOME.v1.genome) %s..." % (sha_row[:16], sha_file[:16]))
    check(sha_row == sha_file and sha_row != hashlib.sha256((JDIR / "GENOME.genome").read_bytes()).hexdigest(), "the journal's epoch row names GENOME.v1.genome byte for byte (and not the launch file)")
    # the 13 draws are reproducible
    seed = 20261101
    rep = sum(1 for no, (p, _) in props.items() if no > 1 and draw_mutation(seed, p["epoch"] + 1, p["no"]) == (p["gene"], p["value"]))
    print("  the %d recorded (gene, value) re-drawn from (SEED %d, epoch+1, proposal_no): %d reproduce" % (len(props) - 1, seed, rep))
    check(rep == len(props) - 1, "every recorded mutation is reproducible from (SEED, epoch+1, proposal_no)")
    launch = {"BIRTH.misfires": 3, "KWTA.k": 5, "DELTA.lr": 0.05, "SLEEP.every": 2500, "SLEEP.replay": 200, "MERGE.theta_m": 0.9969, "BUDGET.per_arrival": 400}
    nullc = [no for no, (p, _) in props.items() if no > 1 and launch.get(p["gene"]) == p["value"]]
    print("  proposals whose drawn value EQUALS the launch genome's own value (null by construction): %s" % nullc)
    # the bar, by the REAL function: -1, +0, +1, +2 items on the 110-item grid
    print("  THE BAR (tools/evolve.py regression_bar, margins %s, cost bar %s) on the 110-item q1_seen grid, incumbent 100/110:" % (MARGINS, COST_RATIO_BAR))
    base = dict(q1_seen=100 / 110, confirmed_share=None, reward_mean=0.0, frames_filed=30, act_pass=True, sentence_pass=None, wall_s=2000.0)
    got = {}
    for items in (99, 100, 101, 102):
        mut = dict(base); mut["q1_seen"] = items / 110
        v, r = regression_bar(base, mut)
        got[items] = v
        print("     mutant %3d/110 (%+d item, %+.4f) -> %-7s %s" % (items, items - 100, items / 110 - 100 / 110, v, r[:88]))
    mut = dict(base); mut["q1_seen"] = 102 / 110; mut["frames_filed"] = 28
    v12 = regression_bar(base, mut)
    print("     proposal-12's shape (q1 +2 items, frames_filed 30->28): %s" % (v12,))
    check(got == {99: "REFUSED", 100: "REFUSED", 101: "REFUSED", 102: "PASS"} and v12[0] == "REFUSED", "-1 item REFUSED, +1 item REFUSED (null mutant), +2 items PASS; +2 items with -2 frames REFUSED")
    # planted control: corrupt one verdict (a REFUSED -> PASS) in a copy; the PASS count must move 1 -> 2
    before = sum(1 for p, _ in props.values() if p["verdict"] == "PASS")
    p2 = {no: (dict(p), mt) for no, (p, mt) in props.items()}
    victim = next(no for no, (p, _) in p2.items() if p["verdict"] == "REFUSED")
    changed = p2[victim][0]["verdict"] != "PASS"
    p2[victim][0]["verdict"] = "PASS"
    after = sum(1 for p, _ in p2.values() if p["verdict"] == "PASS")
    print("  PLANT (corrupt proposal %d's verdict REFUSED->PASS in a copy): PASS count %d -> %d" % (victim, before, after))
    check(changed and after == before + 1, "the planted verdict corruption is CAUGHT (and changed the record)")


# ======================================================================================== WEB (replay of the knowledge web from the tape)
WEBDIR = ROOT / "scratch" / "br2web"          # a STATUS.json copied FIRST, then the tape rows (so the tape is never shorter than STATUS's `t`)


def web(limit=None):
    """Replay Web L and Web N exactly as the mind feeds them (creature/mind.py:951-961 `consume` -> `_web_hear`: every ear row with a
    truthy word, in tape order; the webs are built at mind.py:905 as Web(r, beta=10, seed=SEED, spend="harmonic", reach=20)), validate the
    replay against STATUS `brain.web` at STATUS's own `t`, then read the web at the PDF's two instants."""
    print("== WEB  (replay of Web L / N from the tape's ear rows; validated against STATUS at its own t)")
    sys.path.insert(0, str(ROOT))
    from genome import web as W
    st = json.load(open(WEBDIR / "STATUS.json"))
    sw = st["brain"]["web"]
    t_status = sw["L"]["t"]
    words = []
    for fn in sorted(glob.glob(str(WEBDIR / "*.jsonl"))):
        for d in jl(fn):
            if d.get("sense") == "ear":
                w = (d.get("meta") or {}).get("word")
                if w:
                    words.append((d["seq"], d["at"], str(w)))
    print("ear rows with a word on the tape copy: %d ; STATUS (heartbeat %s) web L t = %d" % (len(words), st.get("heartbeat_at"), t_status))
    check(len(words) >= t_status, "the tape copy holds at least the %d words STATUS's web has heard" % t_status)
    seed = 20261101
    def build():
        return {r: W.Web(r, beta=10, seed=seed, spend="harmonic", reach=20, author="brain-long-2") for r in ("L", "N")}
    def snap(webs):
        return {r: {"t": w.t, "nodes": len(w.nodes), "edges": len(w.edges), "cap": w.cap(), "consolidated": w.stats["consolidated"],
                    "replaced": w.stats["replaced"], "removed_missed": w.stats["removed_missed"]} for r, w in webs.items()}
    cuts = {"first PDF read (seq<=255068, 23:05 +04)": 255068, "second PDF read (seq<=255622, 23:20 +04)": 255622}
    cut_t = {name: sum(1 for s, _, _ in words if s <= seq) for name, seq in cuts.items()}
    def run(seq_words, upto):
        webs = build(); out = {}
        for i, (s, at, w) in enumerate(seq_words, 1):
            for wb in webs.values():
                wb.hear(w)
            if "rm11951" not in out and webs["L"].stats["removed_missed"] >= 11951:
                out["rm11951"] = (i, at, webs["L"].stats["removed_missed"])      # the PDF's «11,951 pruned» is Web L's `removed_missed`
            if "nodes1946" not in out and len(webs["L"].nodes) >= 1946:
                out["nodes1946"] = (i, at, len(webs["L"].nodes))
            for name, tt in cut_t.items():
                if i == tt:
                    out[name] = snap(webs)
            if i == upto:
                out["status"] = snap(webs)
                break
        return out
    upto = t_status if limit is None else min(limit, t_status)
    res = run(words, upto)
    if limit is None:
        print("  replay at STATUS's t=%d:" % t_status)
        for r in ("L", "N"):
            print("   %s replay %s" % (r, res["status"][r]))
            print("   %s STATUS %s" % (r, sw[r]))
        match = all(res["status"][r][k] == sw[r][k] for r in ("L", "N") for k in res["status"][r])
        check(match, "the replayed web equals STATUS's web exactly at t=%d (every counter of L and N): the replay IS what the mind computed" % t_status)
        print("  Web L first reads removed_missed >= 11,951 (the PDF's «11,951 pruned») at word %d, %s, value %d ; first reads 1,946 nodes at word %d, %s" % (res["rm11951"] + res["nodes1946"][:2]))
        for name in cuts:
            print("  %s: t=%d  L %s" % (name, cut_t[name], res[name]["L"]))
            print("  %-60s     N %s" % ("", res[name]["N"]))
        # a planted control: drop ONE word from the stream; the replay must then differ from STATUS
        words2 = words[:4999] + words[5000:]
        changed = len(words2) == len(words) - 1 and words2[4999] != words[4999]
        res2 = run(words2, t_status - 1)
        diff = [k for r in ("L", "N") for k in res2["status"][r] if res2["status"][r][k] != sw[r][k]]
        print("  PLANT (drop the 5,000th word from the stream): counters that now differ from STATUS: %s" % diff)
        check(changed and len(diff) > 0, "the planted dropped word is CAUGHT (and changed the stream)")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("motor", "episodes", "mouth", "evolve", "web", "all"))
    ap.add_argument("--journal", default=str(JDIR))
    ap.add_argument("--tape", default=str(TDIR))
    a = ap.parse_args()
    if a.what == "web":                              # the web replay needs neither the journal nor the frozen tape copy
        web()
        print("RESULT OK (web)")
        return
    J = load_journal(Path(a.journal))
    T = load_tape(Path(a.tape))
    if a.what in ("motor", "all"):
        motor(J)
    if a.what in ("episodes", "all"):
        episodes(J, T)
    if a.what in ("mouth", "all"):
        mouth(J, T)
    if a.what in ("evolve", "all"):
        evolve(J, T)
    print("RESULT OK (%s)" % a.what)


if __name__ == "__main__":
    main()
