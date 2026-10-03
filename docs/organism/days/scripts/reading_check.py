#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 11:39 +0400 — the 3.4-day reading of brain-long-2 (days law §3): the series, memory, the cost per canvas, each with its planted control.
"""READING-DAYS-LIFE-2026-10-03's numbers. READ-ONLY over COPIES (RULES #7): from the worktree root

    mkdir -p scratch/br2days scratch/br2
    cp -p /data/dev/genome-lives/brain-long-2/{HEALTH.jsonl,HEALTH.md,SERIES.tsv,STATUS.json} scratch/br2days/
    cp -p /data/dev/genome-lives/brain-long-2/state/{web.json,SNAPSHOT.json} scratch/br2days/
    cp -p /data/dev/genome-lives/brain-long-2/journal/*.jsonl scratch/br2/
    PYTHONPATH=. OPENBLAS_NUM_THREADS=1 python3 -B docs/organism/claims/../days/scripts/reading_check.py series

`series`: did it live (restarts, repairs, problems, presence of RECOVERY.log and repairs/), memory, and the cost per canvas as a SERIES with every one-minute
window classified by what it CONTAINED (a sleep, a snapshot) before any fit (STATUS `mind_ms_per_canvas_1min` = every row's consume ms in the last minute
divided by the EYE rows in it, creature/body.py:_build_status). Every fit is checked by recovering a PLANTED exponent from the real windows."""
from __future__ import annotations

import argparse
import bisect
import collections
import csv
import datetime as dt
import glob
import json
import math
import os
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DD = ROOT / "scratch" / "br2days"
JD = ROOT / "scratch" / "br2"
LIVE = Path("/data/dev/genome-lives/brain-long-2")
SCENE_END_Z = "2026-09-30T01:30:00Z"        # the scene world ended 05:03 +04 (= 01:03Z): rows after 01:30Z are the clock worlds only


def iso(z):
    return dt.datetime.fromisoformat(z.replace("Z", "+00:00"))


def check(cond, msg):
    if not cond:
        print("ASSERTION FAILED:", msg)
        raise SystemExit(1)
    print("  ok:", msg)


def load_series():
    rows = list(csv.reader(open(DD / "SERIES.tsv"), delimiter="\t"))
    h = rows[0]
    out = []
    for r in rows[1:]:
        d = dict(zip(h, r))
        if len(r) < len(h) or d["mind_ms_per_canvas_1min"] in ("absent", "null"):
            continue
        d["hb"] = iso(d["heartbeat_at"].strip('"'))      # csv has already removed the JSON quotes SERIES writes around it
        d["load"] = float(d["load"])
        for k in ("moments", "tape_rows", "cells", "sleeps", "snapshots", "thinks", "said"):
            d[k] = int(d[k])
        d["ms"] = float(d["mind_ms_per_canvas_1min"])
        d["peak"] = float(d["rss_mb"])      # STATUS `rss_mb` is getrusage(RUSAGE_SELF).ru_maxrss (creature/body.py:91-93): a PEAK that can only rise
        d["mem"] = int(d["unit"].split("MemoryCurrent=")[1]) if "MemoryCurrent=" in d["unit"] else None
        d["restarts"] = int(d["unit"].split("NRestarts=")[1].split()[0])
        out.append(d)
    return out


def load_journal_events():
    seqs, whens, sleeps, snaps = [], [], [], []
    last = None
    for fn in sorted(glob.glob(str(JD / "*.jsonl"))):
        for line in open(fn):
            d = json.loads(line)
            s = d.get("seq")
            if "when" in d and isinstance(s, int):
                seqs.append(s); whens.append(d["when"]); last = d["when"]
            if isinstance(d.get("sleep"), dict) and isinstance(s, int):
                sleeps.append(s)
            if d.get("event") == "snapshot" and d.get("at"):
                snaps.append(iso(d["at"]))
    def when_of(seq):
        i = bisect.bisect_left(seqs, seq)
        return iso(whens[min(i, len(whens) - 1)])
    return [when_of(s) for s in sleeps], snaps, iso(last)


def fit_loglog(cells, ms, load=None, boot=1000, seed=0):
    """OLS of log(ms) on log(cells) (+ load): the exponent b with a bootstrap 95 % interval."""
    y = np.log(np.asarray(ms, float)); x = np.log(np.asarray(cells, float))
    cols = [np.ones_like(x), x] + ([np.asarray(load, float)] if load is not None else [])
    X = np.vstack(cols).T
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    rng = np.random.default_rng(seed)
    bs = []
    n = len(y)
    for _ in range(boot):
        idx = rng.integers(0, n, n)
        bs.append(np.linalg.lstsq(X[idx], y[idx], rcond=None)[0][1])
    return beta, (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def series():
    print("== SERIES  (SERIES.tsv copy, %s; journal copy %s)" % (DD, JD))
    S = load_series()
    sl_t, snap_t, j_last = load_journal_events()
    S = [d for d in S if d["hb"] <= j_last - dt.timedelta(seconds=30)]
    print("SERIES rows (5-minute samples) with a numeric ms: %d, from %s to %s ; journal copy ends %s" % (len(S), S[0]["at"], S[-1]["at"], j_last.isoformat()))
    print("  journal events: %d sleeps, %d snapshot events (wall-clock `at`)" % (len(sl_t), len(snap_t)))
    # --- 1. did it live
    hl = [json.loads(l) for l in open(DD / "HEALTH.jsonl")]
    print("\n-- did it live")
    print("  alive from %s (STARTED-AT) ; SERIES restarts max %d ; sense_restarts max %d ; crash non-null %d/%d rows" % (
        open(LIVE / "STARTED-AT").read().strip(), max(d["restarts"] for d in S), max(int(d["sense_restarts"]) for d in S),
        sum(1 for d in S if d["crash"] not in ("null",)), len(S)))
    print("  HEALTH.jsonl rows %d (every ≈ %.0f min) ; with a non-empty `problems`: %d ; max `repairs` %s ; `last_repair` non-null %d ; `page` non-null %d ; `stuck_s` non-null %d" % (
        len(hl), (iso(hl[-1]["at"]) - iso(hl[0]["at"])).total_seconds() / 60 / max(1, len(hl) - 1) if "at" in hl[0] else float("nan"),
        sum(1 for r in hl if r.get("problems")), max((r.get("repairs") or 0) for r in hl), sum(1 for r in hl if r.get("last_repair")),
        sum(1 for r in hl if r.get("page")), sum(1 for r in hl if r.get("stuck_s") is not None)))
    print("  RECOVERY.log exists: %s ; repairs/ exists: %s ; PAGE.json: %s (an absent file is a presence fact, not silence)" % (
        (LIVE / "RECOVERY.log").exists(), (LIVE / "repairs").exists(), (LIVE / "PAGE.json").read_text().strip()))
    check(max(d["restarts"] for d in S) == 0 and not (LIVE / "RECOVERY.log").exists() and not (LIVE / "repairs").exists() and sum(1 for r in hl if r.get("problems")) == 0,
          "0 unit restarts, 0 repairs, no RECOVERY.log, no repairs/, no HEALTH problem row: the life never needed a repair")
    # --- 2. memory
    print("\n-- memory: the process's PEAK RSS (ru_maxrss: a high-water mark that only rises), the cgroup's MemoryCurrent (the CURRENT figure, page cache included) and swap, by 6 h windows (UTC)")
    def sixh(d):
        h = d["hb"]; return "%s %02d" % (h.strftime("%m-%d"), h.hour // 6 * 6)
    by = collections.OrderedDict()
    for d in S:
        by.setdefault(sixh(d), []).append(d)
    hl_by = collections.defaultdict(list)
    for r_ in hl:
        t_ = iso(r_["at"].replace(" +0400", "+04:00").replace(" ", "T")) if " " in r_["at"] else iso(r_["at"])
        t_ = t_.astimezone(dt.timezone.utc)
        hl_by["%s %02d" % (t_.strftime("%m-%d"), t_.hour // 6 * 6)].append(r_)
    print("  window(UTC)  n   cells(med)  peak_RSS_MB(med)  MemoryCurrent_GB(med)  swap_GB(med/max)  load(med)")
    for k, v in by.items():
        sw = [x["swap_used_gb"] for x in hl_by.get(k, []) if x.get("swap_used_gb") is not None]
        print("  %-11s %3d  %9d  %15.0f  %20.2f  %7.2f / %4.2f  %8.2f" % (k, len(v), statistics.median(d["cells"] for d in v), statistics.median(d["peak"] for d in v),
                                                         statistics.median(d["mem"] for d in v if d["mem"]) / 1e9, statistics.median(sw) if sw else float("nan"), max(sw) if sw else float("nan"), statistics.median(d["load"] for d in v)))
    mem_gb = [d["mem"] / 1e9 for d in S if d["mem"]]
    iM = int(np.argmax(mem_gb))
    print("  MemoryCurrent (current, not peak): max %.2f GB at %s, last %.2f GB; the peak RSS only rose: %.0f -> %.0f MB" % (max(mem_gb), [d for d in S if d["mem"]][iM]["at"][5:16], mem_gb[-1], S[0]["peak"], S[-1]["peak"]))
    rises = [(S[i + 1]["peak"] - S[i]["peak"], i) for i in range(len(S) - 1) if S[i + 1]["peak"] - S[i]["peak"] >= 100]
    check(all(S[i + 1]["peak"] >= S[i]["peak"] for i in range(len(S) - 1)), "the peak RSS never falls in 983 samples: it is a high-water mark, so it says nothing about usage going up or down")
    print("  new peaks of at least 100 MB between consecutive samples after 06:00Z 09-30: %d ; the largest: %s" % (
        len([1 for dr, i in rises if S[i]["hb"] >= iso("2026-09-30T06:00:00Z")]),
        ", ".join("%s +%.0f MB" % (S[i]["at"][5:16], dr) for dr, i in sorted(rises, reverse=True)[:3])))
    # --- 3. cost per canvas
    print("\n-- the cost per canvas: every one-minute window CLASSIFIED by what it contained, then the quiet ones fitted")
    sl_ts = sorted(sl_t); sn_ts = sorted(snap_t)
    def within(ts, a, b):
        i = bisect.bisect_left(ts, a); return i < len(ts) and ts[i] <= b
    for d in S:
        a = d["hb"] - dt.timedelta(seconds=75); b = d["hb"] + dt.timedelta(seconds=15)
        d["sleep"] = within(sl_ts, a, b); d["snap"] = within(sn_ts, a, b)
    clock = [d for d in S if d["hb"] >= iso(SCENE_END_Z)]
    quiet = [d for d in clock if not d["sleep"] and not d["snap"]]
    print("  clock-worlds-only windows (after 05:30 +04 09-30): %d ; containing a sleep: %d ; containing a snapshot: %d ; quiet (neither): %d" % (
        len(clock), sum(1 for d in clock if d["sleep"]), sum(1 for d in clock if d["snap"]), len(quiet)))
    def q(v, p):
        return float(np.percentile([x["ms"] for x in v], p))
    print("  ms per canvas: ALL windows median %.0f p90 %.0f max %.0f | QUIET median %.0f p90 %.0f max %.0f | windows with a sleep median %.0f | with a snapshot median %.0f" % (
        q(clock, 50), q(clock, 90), max(d["ms"] for d in clock), q(quiet, 50), q(quiet, 90), max(d["ms"] for d in quiet),
        q([d for d in clock if d["sleep"]], 50) if any(d["sleep"] for d in clock) else float("nan"), q([d for d in clock if d["snap"]], 50)))
    print("  by 6 h window (UTC): n | cells | ms median ALL | ms median QUIET | quiet p90 | share of windows holding a snapshot/sleep | load median")
    byc = collections.OrderedDict()
    for d in clock:
        byc.setdefault(sixh(d), []).append(d)
    for k, v in byc.items():
        qq = [d for d in v if not d["sleep"] and not d["snap"]]
        print("  %-11s %3d | %6d | %6.0f | %6.0f | %6.0f | %.2f | %5.2f" % (k, len(v), statistics.median(d["cells"] for d in v), q(v, 50),
                                                                     q(qq, 50) if qq else float("nan"), q(qq, 90) if qq else float("nan"),
                                                                     sum(1 for d in v if d["sleep"] or d["snap"]) / len(v), statistics.median(d["load"] for d in v)))
    # the fit on the quiet windows
    cq = [d["cells"] for d in quiet]; mq = [d["ms"] for d in quiet]; lq = [d["load"] for d in quiet]
    beta, ci = fit_loglog(cq, mq)
    beta2, ci2 = fit_loglog(cq, mq, load=lq)
    print("  QUIET windows (n %d): log ms = %.2f + %.2f log cells ; exponent %.2f (bootstrap 95 %% [%.2f, %.2f]) ; with the 1-min load as a covariate: exponent %.2f [%.2f, %.2f], load coefficient %.3f per unit load" % (
        len(quiet), beta[0], beta[1], beta[1], ci[0], ci[1], beta2[1], ci2[0], ci2[1], beta2[2]))
    allc = [d["cells"] for d in clock]; allm = [d["ms"] for d in clock]
    beta_all, ci_all = fit_loglog(allc, allm)
    print("  ALL clock-world windows (n %d), spikes included: exponent %.2f [%.2f, %.2f]" % (len(clock), beta_all[1], ci_all[0], ci_all[1]))
    # the exponent depends on WHICH hours are fitted: three regimes, and the whole-life fit is the first one's
    print("  the exponent by regime (quiet windows):")
    reg = {}
    for name, lo, hi in (("phase 1  09-30 01:30Z .. 10-01 06:00Z", "2026-09-30T01:30:00Z", "2026-10-01T06:00:00Z"),
                         ("phase 2  10-01 06:00Z .. 10-02 00:00Z", "2026-10-01T06:00:00Z", "2026-10-02T00:00:00Z"),
                         ("phase 3  10-02 00:00Z .. 10-03 07:00Z", "2026-10-02T00:00:00Z", "2026-10-03T07:00:00Z")):
        v = [d for d in quiet if iso(lo) <= d["hb"] < iso(hi)]
        b, ci_ = fit_loglog([d["cells"] for d in v], [d["ms"] for d in v], boot=500)
        reg[name] = (b[1], ci_)
        print("    %s: n %3d, median cells %6d, median ms %5.0f, exponent %.2f [%.2f, %.2f]" % (name, len(v), statistics.median(d["cells"] for d in v), q(v, 50), b[1], ci_[0], ci_[1]))
    check(reg[list(reg)[0]][0] > 2.0 and reg[list(reg)[2]][0] < 1.5, "the steep exponent belongs to the first 30 hours; the last 31 hours read near-linear: one power law over all 3.4 days misdescribes the cost")
    # does the evolve worker's twin run (the other big process on this box) slow the mind? windows from the proposal files' own mtime and twin wall times
    ev = []
    for fn in sorted(glob.glob(str(ROOT / "scratch" / "br2evolve" / "PROPOSAL-*.json"))):
        p = json.load(open(fn))
        if p.get("incumbent"):
            end = dt.datetime.fromtimestamp(os.path.getmtime(fn), tz=dt.timezone.utc)
            ev.append((end - dt.timedelta(seconds=p["incumbent"]["wall_s"] + p["mutant"]["wall_s"] + 120), end))
    def busy(d):
        return any(a <= d["hb"] <= b for a, b in ev)
    p3 = [d for d in quiet if d["hb"] >= iso("2026-10-01T06:00:00Z")]
    inn = [d for d in p3 if busy(d)]; out = [d for d in p3 if not busy(d)]
    print("  evolve twin windows (%d rounds; each [proposal mtime - both twins' wall - 2 min, mtime]): quiet windows after 10-01 06:00Z inside them %d (median ms %.0f, cells %d, load %.2f) vs outside %d (median ms %.0f, cells %d, load %.2f)" % (
        len(ev), len(inn), q(inn, 50), statistics.median(d["cells"] for d in inn), statistics.median(d["load"] for d in inn),
        len(out), q(out, 50), statistics.median(d["cells"] for d in out), statistics.median(d["load"] for d in out)))
    # the same test with the label shuffled (a planted null: the difference must shrink to noise)
    rngp = np.random.default_rng(5)
    labs = np.array([busy(d) for d in p3]); diffs = []
    msv = np.array([d["ms"] for d in p3])
    for _ in range(500):
        perm = rngp.permutation(labs)
        diffs.append(float(np.median(msv[perm]) - np.median(msv[~perm])))
    real = float(np.median(msv[labs]) - np.median(msv[~labs]))
    print("  inside minus outside, median ms: %+.0f ; the same difference with the labels shuffled (500 draws): 2.5 %% %.0f, 97.5 %% %.0f" % (real, np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)))
    print("  quiet baseline by 3-hour window (UTC): median ms | median cells | median load")
    hrs = collections.OrderedDict()
    for d in quiet:
        hrs.setdefault(d["hb"].strftime("%m-%d ") + "%02d" % (d["hb"].hour // 3 * 3), []).append(d)
    print("   " + " ; ".join("%s: %.0f/%dk/%.1f" % (k, q(v, 50), round(statistics.median(x["cells"] for x in v) / 1000), statistics.median(x["load"] for x in v)) for k, v in hrs.items()))
    # what the life DID with its days: rates per hour by 6 h window from SERIES counters
    print("  rates per hour by 6 h window (UTC): births | thinks | said | sleeps (per 6 h) | snapshots (per 6 h)")
    byr = collections.OrderedDict()
    for d in S:
        byr.setdefault(sixh(d), []).append(d)
    for k, v in byr.items():
        hrs_ = max(1e-9, (v[-1]["hb"] - v[0]["hb"]).total_seconds() / 3600)
        print("   %-11s births %6.0f | thinks %5.0f | said %5.1f | sleeps %4.1f | snapshots %4.1f" % (k, (int(v[-1]["births"]) - int(v[0]["births"])) / hrs_, (v[-1]["thinks"] - v[0]["thinks"]) / hrs_, (v[-1]["said"] - v[0]["said"]) / hrs_,
                                                                                               (v[-1]["sleeps"] - v[0]["sleeps"]) / hrs_ * 6, (v[-1]["snapshots"] - v[0]["snapshots"]) / hrs_ * 6))
    # can cells and moments be told apart as the driver? (they grow together: moments 70 a minute, births ≈ one per 60 moments)
    mq_ = np.log([d["moments"] for d in quiet]); cq_ = np.log(cq)
    r_cm = float(np.corrcoef(cq_, mq_)[0, 1])
    b_cells = float(np.polyfit(cq_, np.log(mq), 1)[0]); b_mom = float(np.polyfit(mq_, np.log(mq), 1)[0])
    X2 = np.vstack([np.ones_like(cq_), cq_, mq_]).T
    beta_2 = np.linalg.lstsq(X2, np.log(mq), rcond=None)[0]
    vif = 1.0 / (1.0 - r_cm ** 2)
    print("  CELLS vs MOMENTS as the driver (quiet windows): corr(log cells, log moments) = %.4f (variance inflation %.0f) ; exponent vs cells alone %.2f, vs moments alone %.2f ; both together: cells %.2f, moments %.2f — this series cannot separate them" % (r_cm, vif, b_cells, b_mom, beta_2[1], beta_2[2]))
    # the new PEAKS: the two largest rises of the high-water mark between consecutive samples, with what moved beside them
    rss_steps = sorted(((S[i + 1]["peak"] - S[i]["peak"], i) for i in range(len(S) - 1)), reverse=True)[:2]
    for dr, i in rss_steps:
        print("  new PEAK %s -> %s: %+.0f MB (%.0f -> %.0f) with cells %d -> %d, births %s -> %s, sleeps %d -> %d, snapshots %d -> %d" % (
            S[i]["at"][5:16], S[i + 1]["at"][11:16], dr, S[i]["peak"], S[i + 1]["peak"], S[i]["cells"], S[i + 1]["cells"], S[i]["births"], S[i + 1]["births"],
            S[i]["sleeps"], S[i + 1]["sleeps"], S[i]["snapshots"], S[i + 1]["snapshots"]))
    check(sum(dr for dr, _ in rss_steps) > 1800 and abs(S[rss_steps[0][1] + 1]["cells"] - S[rss_steps[0][1]]["cells"]) < 50, "the peak RSS rose by about 2 GB in two consecutive samples while cells did not move: a new high-water mark (a transient allocation), not a function of cells")
    # load bands among the quiet windows
    bands = [(0, 2.5), (2.5, 6), (6, 100)]
    for lo, hi in bands:
        v = [d for d in quiet if lo <= d["load"] < hi]
        if v:
            print("  quiet windows with load in [%.1f, %.1f): n %d, median cells %d, median ms %.0f, p90 %.0f" % (lo, hi, len(v), statistics.median(d["cells"] for d in v), q(v, 50), q(v, 90)))
    first = [d for d in quiet if d["hb"] < iso("2026-09-30T08:00:00Z")]
    last = [d for d in quiet if d["hb"] >= iso("2026-10-03T00:00:00Z")]
    print("  quiet windows, first day (hb < 09-30 12:00 +04): n %d, cells %d, median ms %.0f ; last 8 h: n %d, cells %d, median ms %.0f ; ratio of per-cell cost %.2f" % (
        len(first), statistics.median(d["cells"] for d in first), q(first, 50), len(last), statistics.median(d["cells"] for d in last), q(last, 50),
        (q(last, 50) / statistics.median(d["cells"] for d in last)) / (q(first, 50) / statistics.median(d["cells"] for d in first))))
    # --- the planted control: recover a PLANTED exponent from the real windows' cells and classification
    rng = np.random.default_rng(7)
    for b_true in (0.0, 1.0, 1.5):
        ms_syn = 300.0 * (np.array(cq, float) / 30000.0) ** b_true * np.exp(rng.normal(0, 0.15, len(cq)))
        bb, cc = fit_loglog(cq, ms_syn, boot=300)
        print("  PLANT exponent %.1f on the real quiet windows' cells (lognormal noise sd 0.15): recovered %.2f [%.2f, %.2f]" % (b_true, bb[1], cc[0], cc[1]))
        check(cc[0] - 0.05 <= b_true <= cc[1] + 0.05, "the fit recovers the planted exponent %.1f" % b_true)
    # the planted classification: relabel the snapshot windows as quiet; the quiet median must move (the classification is not decoration)
    mixed = [d for d in clock if not d["sleep"]]
    print("  PLANT (relabel the snapshot windows as quiet): median ms %.0f -> %.0f" % (q(quiet, 50), q(mixed, 50)))
    check(q(mixed, 50) > q(quiet, 50) * 1.05, "relabelling the snapshot windows as quiet moves the baseline: the classification is what separates spikes from cost")
    # --- 4. the snapshot's own cost, and the think's, from HEALTH.jsonl
    th = [(iso(r["at"]), r.get("think_ms_median"), r.get("hash_ms_last"), r.get("cells")) for r in hl if r.get("think_ms_median") is not None]
    if th:
        byh = collections.OrderedDict()
        for t, tm, hm, c in th:
            byh.setdefault("%s %02d" % (t.strftime("%m-%d"), t.hour // 6 * 6), []).append((tm, hm, c))
        print("\n-- the components HEALTH.jsonl carries (by 6 h, local +04 hours): think_ms_median (ms) | hash_ms_last (ms) | cells")
        for k, v in byh.items():
            print("  %-11s %6.1f | %5.1f | %6d" % (k, statistics.median(x[0] for x in v), statistics.median(x[1] for x in v if x[1] is not None), statistics.median(x[2] for x in v)))
    st = json.load(open(DD / "STATUS.json"))
    print("\n-- STATUS now (heartbeat %s): think_freeze_ms %s think_apply_ms %s think_ms_median %s hash_ms_last %s cells %s snapshots %s (the state files: organism.json %.0f MB, brain.npz %.0f MB, ledger.json %.0f MB, web.json %.0f MB)" % (
        st.get("heartbeat_at"), st.get("think_freeze_ms"), st.get("think_apply_ms"), st.get("think_ms_median"), st.get("hash_ms_last"), st.get("cells"), st.get("snapshots"),
        os.path.getsize(LIVE / "state" / "organism.json") / 1e6, os.path.getsize(LIVE / "state" / "brain.npz") / 1e6,
        os.path.getsize(LIVE / "state" / "ledger.json") / 1e6, os.path.getsize(LIVE / "state" / "web.json") / 1e6))


# ======================================================================================== the webs, the self, the brain (days law §3 items 2-6)
WEBDIR = ROOT / "scratch" / "br2web"        # STATUS.json copied FIRST, then the tape rows (as claims_check.py's `web`)


def _avg_clustering(adj):
    tot = 0.0; n = 0
    for u, nb in adj.items():
        k = len(nb)
        if k < 2:
            continue
        links = 0
        nbl = list(nb)
        for i in range(k):
            a = adj[nbl[i]]
            for j in range(i + 1, k):
                if nbl[j] in a:
                    links += 1
        tot += 2.0 * links / (k * (k - 1)); n += 1
    return tot / n if n else float("nan")


def _path_len(adj, sample=150, seed=3):
    """mean shortest path over `sample` BFS sources inside the largest component"""
    nodes = sorted(adj, key=str)                 # sorted: str hashing is randomised per process, so set/dict order must not decide the sample (the verifier's catch)
    seen = set(); comps = []
    for s in nodes:
        if s in seen:
            continue
        comp = [s]; seen.add(s); i = 0
        while i < len(comp):
            for v in adj[comp[i]]:
                if v not in seen:
                    seen.add(v); comp.append(v)
            i += 1
        comps.append(comp)
    big = sorted(max(comps, key=lambda c: (len(c), sorted(c, key=str)[0])), key=str)
    rng = np.random.default_rng(seed)
    srcs = [big[int(i)] for i in rng.choice(len(big), size=min(sample, len(big)), replace=False)]
    tot = 0; cnt = 0
    for s in srcs:
        dist = {s: 0}; q = [s]; i = 0
        while i < len(q):
            u = q[i]; i += 1
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1; q.append(v)
        tot += sum(dist.values()); cnt += len(dist) - 1
    return tot / cnt if cnt else float("nan"), len(big), len(comps)


def _adj_from(edges, nodes):
    adj = {w: set() for w in nodes}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    return adj


def _er(n_nodes, n_edges, seed):
    rng = np.random.default_rng(seed)
    adj = {i: set() for i in range(n_nodes)}
    m = 0
    while m < n_edges:
        a, b = int(rng.integers(n_nodes)), int(rng.integers(n_nodes))
        if a != b and b not in adj[a]:
            adj[a].add(b); adj[b].add(a); m += 1
    return adj


def enrichment(web_edges, heldout, d=3):
    """PREREG-KW-1 K6: sum h_ab / sum E'_ab over the consolidated edges whose two words both occur in the held-out part;
    h_ab = the pair's events there under the web's own `recent` rule; E'_ab = 2 d n'_a n'_b / N'."""
    n = collections.Counter(heldout); N = len(heldout)
    h = collections.Counter(); recent = []
    for w in heldout:
        for u in recent:
            if u != w:
                h[(u, w) if u < w else (w, u)] += 1
        recent = ([w] + [x for x in recent if x != w])[:d]
    sh = se = 0.0; used = 0
    for a, b in web_edges:
        if a in n and b in n:
            sh += h[(a, b)]; se += 2.0 * d * n[a] * n[b] / N; used += 1
    return (sh / se if se else float("nan")), used, len(web_edges)


def webs_and_self():
    print("== WEBS  (replay of Web L and N from the tape's ear rows, validated against STATUS at its own t; %s)" % WEBDIR)
    sys.path.insert(0, str(ROOT))
    from genome import web as W
    st = json.load(open(WEBDIR / "STATUS.json")); sw = st["brain"]["web"]; T = sw["L"]["t"]
    words = []; ats = []; src_of = collections.defaultdict(set)
    for fn in sorted(glob.glob(str(WEBDIR / "*.jsonl"))):
        for line in open(fn):
            d = json.loads(line)
            if d.get("sense") == "ear":
                w = (d.get("meta") or {}).get("word")
                if w:
                    words.append(str(w)); ats.append(d["at"]); src_of[str(w)].add((d.get("meta") or {}).get("source"))
    print("ear words on the tape copy %d ; STATUS web L t %d (heartbeat %s)" % (len(words), T, st.get("heartbeat_at")))
    check(len(words) >= T, "the tape copy holds every word STATUS's web has heard")
    words = words[:T]; ats = ats[:T]
    webs = {r: W.Web(r, beta=10, seed=20261101, spend="harmonic", reach=20, author="brain-long-2") for r in ("L", "N")}
    series, snaps = [], {}
    keep = (100000, 150000)
    for i, w in enumerate(words, 1):
        for wb in webs.values():
            wb.hear(w)
        if i % 10000 == 0 or i == T:
            series.append((i, ats[i - 1], {r: (len(wb.nodes), len(wb.edges), wb.stats["consolidated"], wb.stats["replaced"], wb.stats["removed_missed"]) for r, wb in webs.items()}))
        if i in keep:
            snaps[i] = {r: wb.consolidated() for r, wb in webs.items()}
    fin = {r: {"t": wb.t, "nodes": len(wb.nodes), "edges": len(wb.edges), "cap": wb.cap(), "consolidated": wb.stats["consolidated"], "replaced": wb.stats["replaced"], "removed_missed": wb.stats["removed_missed"]} for r, wb in webs.items()}
    check(all(fin[r][k] == sw[r][k] for r in fin for k in fin[r]), "the replayed webs equal STATUS's at t=%d, every counter of L and N" % T)
    print("\n-- the web's growth, as a series every 10,000 words: words heard | tape time (UTC) | L nodes, edges, consolidated, replaced, removed | N nodes, edges, consolidated, replaced, removed")
    for i, at, v in series:
        print("  %7d  %s  L %5d %6d %5d %6d %6d | N %5d %6d %5d %6d %6d" % ((i, at[5:16]) + v["L"] + v["N"]))
    # item 2: the web is true (recount from the words), with a planted change
    print("\n-- the web is true: recount_errors(web, words)")
    for r, wb in webs.items():
        errs = W.recount_errors(wb, words)
        print("  %s: %d nodes, %d edges recounted from %d words: %d errors" % (r, len(wb.nodes), len(wb.edges), len(words), len(errs)))
        check(len(errs) == 0, "web %s: every node's n/first/last and every live edge's c/occ/last equals the recount from the words" % r)
    planted = W.Web.from_dict(webs["L"].to_dict())
    some_node = next(iter(planted.nodes)); planted.nodes[some_node]["n"] += 1
    some_edge = next(iter(planted.edges)); planted.edges[some_edge]["c"] += 1
    perr = W.recount_errors(planted, words)
    print("  PLANT (node %r n+1, edge %r c+1 in a copy): recount reports %d errors" % (some_node, some_edge, len(perr)))
    check(len(perr) >= 2, "the planted changes are CAUGHT by the recount")
    # item 3: the shape against a random web of its size
    print("\n-- the shape: average clustering and mean shortest path (150 BFS sources, largest component) against 5 random webs of the same nodes and edges")
    for r, wb in webs.items():
        for label, edges in (("all edges", list(wb.edges)), ("consolidated edges", wb.consolidated())):
            nodes_in = sorted({x for e in edges for x in e})
            adj = _adj_from(edges, nodes_in)
            cl = _avg_clustering(adj); pl, big, ncomp = _path_len(adj)
            er_c, er_p = [], []
            for s in range(5):
                a = _er(len(nodes_in), len(edges), s)
                er_c.append(_avg_clustering(a)); er_p.append(_path_len(a, seed=s)[0])
            print("  %s %-19s nodes %5d edges %6d components %3d (largest %d): clustering %.3f vs random %.3f ; mean path %.2f vs random %.2f" % (
                r, label, len(nodes_in), len(edges), ncomp, big, cl, float(np.mean(er_c)), pl, float(np.mean(er_p))))
    # what the web holds: hubs, the strongest consolidated edges, and how many consolidated edges touch a word ever heard from a grounded world
    Lw = webs["L"]
    deg = {w: len(Lw._adj.get(w, ())) for w in Lw.nodes}
    hubs = sorted(deg.items(), key=lambda kv: -kv[1])[:8]
    top = sorted(((int(Lw.edges[k]["c"]), k) for k in Lw.consolidated()), reverse=True)[:8]
    grounded = lambda w: bool(src_of.get(w, set()) & {"scene", "game", "maker"})
    cons = Lw.consolidated()
    both = sum(1 for a, b in cons if grounded(a) and grounded(b)); one = sum(1 for a, b in cons if grounded(a) != grounded(b)); none_ = len(cons) - both - one
    print("\n-- what Web L holds: top hubs by degree %s ; strongest consolidated edges (evidence c) %s" % (hubs, [(k, c) for c, k in top]))
    print("  consolidated edges of L: %d ; both words ever heard from the scene/game/maker worlds: %d ; one: %d ; neither (shelf and lexicon words only): %d ; words in L: %d of which grounded %d" % (
        len(cons), both, one, none_, len(Lw.nodes), sum(1 for w in Lw.nodes if grounded(w))))
    # item 4: L against N on its own speech (K6): the webs as they stood at a snapshot, read against the words heard AFTER it
    print("\n-- L against N on its own speech (PREREG-KW-1 K6 enrichment): consolidated edges at a snapshot, read against the words heard AFTER it; K7: the same on the held-out words SHUFFLED")
    rng = np.random.default_rng(11)
    for t0 in keep:
        held = words[t0:]
        shuf = list(held); rng.shuffle(shuf)
        for r in ("L", "N"):
            e, used, tot = enrichment(snaps[t0][r], held)
            e0, used0, _ = enrichment(snaps[t0][r], shuf)
            print("  snapshot after %6d words (%s UTC), held-out %6d words: web %s: %5d consolidated edges, %5d with both words in the held-out part: enrichment %.2f ; shuffled control %.2f" % (
                t0, ats[t0 - 1][5:16], len(held), r, tot, used, e, e0))
            check(e0 <= 1.5 or used == 0, "K7: the shuffled held-out words read %.2f (≤ 1.5): the instrument finds no association in a shuffle (web %s, snapshot %d)" % (e0, r, t0))
            cls = {"grounded-grounded": [], "grounded-shelf": [], "shelf-shelf": []}
            for a, b in snaps[t0][r]:
                ga, gb = grounded(a), grounded(b)
                cls["grounded-grounded" if (ga and gb) else ("shelf-shelf" if not (ga or gb) else "grounded-shelf")].append((a, b))
            parts = []
            for name, edges in cls.items():
                ee, uu, tt = enrichment(edges, held)
                ee0, _, _ = enrichment(edges, shuf)
                parts.append("%s: %d edges (%d usable) enrichment %s (shuffled %s)" % (name, tt, uu, ("%.2f" % ee) if uu else "n/a", ("%.2f" % ee0) if uu else "n/a"))
            print("      by edge class — " + " | ".join(parts))
    # item 5: the self
    print("\n-- the self (state/web.json copy, snapshot t %s)" % json.load(open(DD / "SNAPSHOT.json")).get("t"))
    wj = json.load(open(DD / "web.json")); sn = W.SelfNode.from_dict(wj["self"])
    for cid, c in sorted(sn.claims.items()):
        print("  %s %-8s %-9s confirmed %6d contradicted %6d share %.3f first_event_at %s first_demoted_at %s — %s" % (
            cid, c.quantifier, c.state, c.confirmed, c.contradicted, c.confirmed / max(1, c.confirmed + c.contradicted),
            c.first_event_at, c.first_demoted_at, c.text))
    lv = sn.lived
    print("  lived: canvases %d ; fixations a canvas %s ; turns expecting %d, expectation confirmed %d (%.3f)" % (lv["canvases"], dict(sorted(lv["fix"].items())), lv["turns_expecting"], lv["expect_confirmed"], lv["expect_confirmed"] / max(1, lv["turns_expecting"])))
    rel = sorted(((sn.reliability(w), w, lv["words"][w][0]) for w in lv["words"] if lv["words"][w][0] >= 100), key=lambda x: x[0])
    print("  lived reliability per word (the word named something it expected that word for; words heard ≥ 100 times, weakest first): %s" % ", ".join("%s %.3f (n %d)" % (w, r, n) for r, w, n in rel))
    # the self's and the brain's history, from HEALTH.jsonl
    hl = [json.loads(l) for l in open(DD / "HEALTH.jsonl")]
    print("\n-- from HEALTH.jsonl (%d rows): the claims' states over time, the brain's counters" % len(hl))
    prev = None
    for r in hl:
        cur = {k: v[0] for k, v in (r.get("self") or {}).items()}
        if cur != prev:
            print("  %s claim states %s" % (r["at"][:16], cur)); prev = cur
    br = [(r["at"], (r.get("brain") or {}).get("learned"), (r.get("brain") or {}).get("asks_answered")) for r in hl]
    first_full = next(a for a, l, _ in br if l == 50000)
    later = [(l, k) for a, l, k in br if a >= first_full]
    print("  brain.learned first reads 50000 at %s ; in the %d HEALTH rows since it read: learned {%s}, asks_answered {%s}" % (
        first_full[:16], len(later), ", ".join(map(str, sorted({l for l, _ in later}))), ", ".join(map(str, sorted({k for _, k in later})))))
    sc = [(r["at"], (r.get("scene") or {})) for r in hl]
    ended = next(a for a, s in sc if s.get("ended"))
    print("  scene.ended first true at %s (HEALTH row time, +04)" % ended[:16])
    check(len({l for l, _ in later}) == 1 and len({k for _, k in later}) == 1, "the brain's learned count and answered-asks count have not moved since the scene world ended: it has been idle since")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("series", "webs", "all"))
    a = ap.parse_args()
    if a.what in ("series", "all"):
        series()
    if a.what in ("webs", "all"):
        webs_and_self()
    print("RESULT OK (%s)" % a.what)


if __name__ == "__main__":
    main()
