#!/usr/bin/env python3
# edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:48 +0400 — PREREG-INNER-1 §3 (K, K-ablated, K-plant, G1, G2, G3, the readings) + §4 (the bench)
# + AMENDMENT 1 A5–A8 (the law signed by author, builder and seat at research-1003 @ 7c49f62, file sha256 b489209c…; the co-signed
# TEXT 857e07b2…faa82). Test-first: tests/tools/test_inner_bench.py (every grader on synthetic rows with a planted control).
"""tools/brain/inner_bench.py — THE BENCH of the inner turn: offline, on a COPIED generation of a closed life's state, through the
mind's OWN handler (creature/mind.py:_inner_turn), never a copy of it.

  run   --gen <copy of state/prev> --genome <the genome IN FORCE at that generation> --tape <copy of the tape day files> --out <dir>
        [--n 1000] [--rule lift|greedy-count|greedy-lift] [--restart 5] [--inhibit 2]
        Loads the mind from the copy (Mind.resume) under <genome> + the INNER line, feeds N synthetic SENSE body rows with backlog 0
        (+ ONE planted backlog-1 row and ONE row with no reading, G1's plants), writes <out>/inner.jsonl (the inner rows the mind
        journaled) and <out>/RUN.json (the counts, the brain / web / self prints BEFORE and AFTER — read-only, pinned — the CPU per
        row, the genome's sha, the generation's last_seq). `--rule` other than lift is G3's PLANT (a test parameter set on the mind
        after construction, never a genome value; AMENDMENT 1 A4).
  grade --out <dir> --tape <dir> --journal <copy of the journal day files> --truth <copy of truth/> --web <copy of web.json>
        [--draws 200] [--self-draws 1000] [--plant-out <the greedy run's out dir>]
        K (TRUE OF ITS PAST) over ALL inner turns against the DEALT-PHRASE null (scene and target kept, ≥ 200 draws), K-ablated (a
        constant phrase) that must FAIL, K-plant (a phrase copied from another turn's scene) that must read FALSE, the truth-file
        cross-check (a planted mismatch caught), G1 from RUN.json's counts, G2 EXIST against the tape's ear rows (a planted miss
        caught), G3 coverage + the greedy run's lock, and the readings R-RET (paired with the live turn, 10/n beside), R-AGE (deciles
        of the remembered scene's age), R-ASSOC (frequency-matched null), R-SELF (label-permutation null). Writes GRADE.json + GRADE.txt.

The truth of a remembered scene is the scene world's own spec, REGENERATED: brain.scene.world.train_scene(world_seed, scene) (A8).
Nothing here writes a life's root: every input is a copy the caller made (RULES §7)."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from brain.scene import marks as M
from brain.scene import world as W
from brain.world.seeds import substream
from creature import inner as I

INNER_LINE = "INNER    every body row when idle; walk lift; inhibit {inhibit}; restart {restart}"
T0 = datetime(2026, 10, 3, 12, 0, 0, tzinfo=timezone.utc)
SEED = 20261003                      # the bench's own seed (the nulls' substreams); the MIND's draws use the genome's SEED


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def reading(backlog: Optional[int]) -> Dict[str, object]:
    r = {"moments": 0, "births": 0, "arrivals": 0, "budget_left": 400, "refused": 0, "restarts": 0, "mind_ms": None, "rss": 0.0,
         "refused_nmax": 0}
    if backlog is not None:
        r["backlog"] = int(backlog)
    return r


def body_row(seq: int, at: str, backlog: Optional[int], moment: str) -> Dict[str, object]:
    return {"seq": int(seq), "at": at, "sense": "body", "sha": "", "payload": "", "meta": {"moment": moment, "source": "body", "reading": reading(backlog)}}


# ------------------------------------------------------------------------------------------------ run
def run(a) -> int:
    import creature.mind as MM
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    root = out / "root"
    if root.exists():
        print(f"refused: {root} exists (a bench run gets a fresh root)", file=sys.stderr)
        return 2
    root.mkdir(parents=True)
    shutil.copytree(Path(a.gen), root / "state", copy_function=shutil.copy2)          # prints preserved
    (root / "tape").symlink_to(Path(a.tape).resolve(), target_is_directory=True)
    gen_manifest = json.loads((root / "state" / "SNAPSHOT.json").read_text())
    genome_text = Path(a.genome).read_text().rstrip("\n") + "\n" + INNER_LINE.format(inhibit=int(a.inhibit), restart=int(a.restart)) + "\n"
    gp = out / "genome.genome"
    gp.write_text(genome_text)
    t_load = time.process_time()
    mind, last_seq = MM.Mind.resume(gp, root)
    t_load = time.process_time() - t_load
    if mind.brain is None or mind._inner is None:
        print("refused: the resumed mind has no brain or no INNER line", file=sys.stderr)
        return 2
    plant = None
    if a.rule != "lift" or a.walk_from != "said":
        mind._inner["walk"] = str(a.rule)                     # G3's plant: a test parameter, never a genome value
        mind._inner["walk_from"] = str(a.walk_from)           # A2.1: "topic" = §0.2's counted walk, the lock's form; a test parameter too
        plant = f"{a.rule}/{a.walk_from}"
    before = prints(mind)
    n = int(a.n)
    t_rows = time.process_time()
    for i in range(n):
        mind.consume(body_row(last_seq + 1 + i, iso(T0 + timedelta(minutes=i)), 0, f"inner-bench-{i:06d}"))
    t_rows = time.process_time() - t_rows
    # G1's plants: a backlog-1 row and a row with no reading — neither may turn, both are counted by reason
    mind.consume(body_row(last_seq + 1 + n, iso(T0 + timedelta(minutes=n)), 1, "inner-bench-plant-backlog"))
    mind.consume(body_row(last_seq + 2 + n, iso(T0 + timedelta(minutes=n + 1)), None, "inner-bench-plant-noreading"))
    after = prints(mind)
    rows = [r for f in sorted((root / "journal").glob("*.jsonl")) for r in _jsonl(f) if r.get("kind") == "brain" and r.get("act") == "inner"]
    with (out / "inner.jsonl").open("w", encoding="utf-8") as w:
        for r in rows:
            w.write(json.dumps(r) + "\n")
    st = mind.brain_status()["inner"]
    # READ-ONLY (the law §2, AMENDMENT 2 A2.3): the brain's state hash and the web unchanged over the whole run; the self unchanged but for
    # its claim B1 («my mind keeps up with what I sense»), which the SELF's own rule observes on EVERY body row (creature/mind.py:_self_body)
    # before the inner turn runs — masked here, its delta printed (it must equal the body rows fed: n + the 2 plants). The strict pin
    # around _inner_turn alone is tests/creature/test_inner_mind.py's.
    read_only = (before["brain"] == after["brain"] and before["web_L"] == after["web_L"] and before["self_but_B1"] == after["self_but_B1"])
    b1_delta = int(after["B1_observed"]) - int(before["B1_observed"])
    rec = {"n": n, "rule": str(a.rule), "walk_from": str(a.walk_from), "plant": plant, "inhibit": int(a.inhibit), "restart": int(a.restart),
           "genome": str(a.genome), "genome_sha256": sha256_file(Path(a.genome)), "bench_genome_sha256": sha256_file(gp), "gen": str(a.gen),
           "gen_last_seq": gen_manifest.get("last_seq"), "resume_last_seq": int(last_seq), "mature": sorted(str(w) for w in mind.brain.L.mature_words()),
           "seed": int(mind.genome.seed), "counts": st, "inner_rows": len(rows), "prints_before": before, "prints_after": after,
           "read_only": read_only, "B1_observed_delta": b1_delta, "body_rows_fed": n + 2, "cpu_s_load": round(t_load, 3),
           "cpu_s_rows": round(t_rows, 3), "cpu_ms_per_row": round(1000.0 * t_rows / max(n, 1), 3), "at": datetime.now(timezone.utc).isoformat()}
    (out / "RUN.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(f"[inner-bench run] rows {len(rows)} of {n} eligible · counts {st} · read-only {read_only} (B1 observed +{b1_delta} on {n + 2} body rows) · "
          f"{rec['cpu_ms_per_row']} ms/row (load {rec['cpu_s_load']} s) · plant {plant}")
    return 0 if (read_only and b1_delta == n + 2) else 1


def prints(mind) -> Dict[str, object]:
    """The brain's state hash, the web L's dump, the self WITHOUT its claim B1 (masked), and B1's observed count (A2.3)."""
    sd = mind.self_node.to_dict() if mind.self_node is not None else None
    b1 = 0
    if sd is not None:
        claims = dict(sd.get("claims") or {})
        b1c = claims.pop("B1", None)
        if isinstance(b1c, dict):                    # genome/web.py:Claim.to_dict: the observations are confirmed + contradicted
            b1 = int(b1c.get("confirmed", 0) or 0) + int(b1c.get("contradicted", 0) or 0)
        sd = {**sd, "claims": claims}
    return {"brain": mind.brain.state_hash(),
            "web_L": hashlib.sha256(mind.webs["L"].dumps().encode("utf-8")).hexdigest() if mind.webs else "none",
            "self_but_B1": hashlib.sha256(json.dumps(sd, sort_keys=True).encode("utf-8")).hexdigest() if sd is not None else "none",
            "B1_observed": b1}


def _jsonl(path: Path, needle: Optional[str] = None) -> Iterable[Dict[str, object]]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if needle is not None and needle not in line:
                continue
            if line.strip():
                yield json.loads(line)


# ------------------------------------------------------------------------------------------------ the graders (plain data in, plain data out)
def attrs(thing) -> set:
    return {str(thing.shape), str(thing.colour), str(thing.size)}


def thing_under(cells: Sequence[Sequence[int]], things: Sequence) -> Optional[int]:
    """The thing a say's target lies on: marks.hyp_label over the things its member cells land on (world.fixation_thing) — the
    grader's own rule for a cited hypothesis (grade_life._cited_thing); None when none or a tie."""
    if not cells:
        return None
    ft = [W.fixation_thing((int(c[0]), int(c[1])), things) for c in cells]
    return M.hyp_label(M.hyp_counts([list(range(len(cells)))], ft)[0])


def k_true(said: Optional[Sequence[str]], cells: Optional[Sequence[Sequence[int]]], things: Sequence) -> bool:
    """K's rule: a say, on a thing, every said word an attribute of that thing. A silent turn, or a target on no thing: False."""
    if not said or not cells:
        return False
    t = thing_under(cells, things)
    if t is None:
        return False
    return set(str(w) for w in said) <= attrs(things[int(t)])


def scene_things(world_seed: int, scene: int):
    return W.train_scene(int(world_seed), int(scene)).things


def k_grade(turns: Sequence[Dict[str, object]], draws: int = 200, seed: int = SEED) -> Dict[str, object]:
    """K over ALL turns: each turn = {"said": [...] or None, "cells": [[y,x],...] or None, "things": [Thing,...]}. The observed count
    of TRUE against the DEALT-PHRASE null: the said phrases of the saying turns permuted among them (scene and target KEPT), `draws`
    draws from substream(seed, "inner-null:<k>"); PASS iff observed > the null's 95th percentile. K-ablated: every say replaced by
    the most frequent phrase (its target kept) — read against its own null (a constant phrase is invariant under dealing, so it
    reads AT its null and must fail). K-plant: one TRUE turn's phrase replaced by another turn's phrase that is not true of its
    thing — the grader must read it FALSE."""
    n = len(turns)
    truth = [k_true(t["said"], t["cells"], t["things"]) for t in turns]
    observed = int(sum(truth))
    saying = [i for i, t in enumerate(turns) if t["said"] and t["cells"]]
    phrases = [tuple(str(w) for w in turns[i]["said"]) for i in saying]
    null_counts = []
    for k in range(int(draws)):
        rng = substream(seed, f"inner-null:{k}")
        perm = rng.permutation(len(saying)) if saying else np.zeros(0, dtype=int)
        c = 0
        for j, i in enumerate(saying):
            c += k_true(phrases[int(perm[j])], turns[i]["cells"], turns[i]["things"])
        null_counts.append(int(c))
    p95 = float(np.percentile(null_counts, 95)) if null_counts else 0.0
    out = {"n": n, "n_said": len(saying), "n_on_thing": int(sum(1 for i in saying if thing_under(turns[i]["cells"], turns[i]["things"]) is not None)),
           "observed": observed, "rate": (observed / n if n else None), "null_draws": len(null_counts),
           "null_p95": p95, "null_max": (max(null_counts) if null_counts else None), "null_mean": (float(np.mean(null_counts)) if null_counts else None),
           "pass": bool(null_counts) and observed > p95}
    # K-ablated: the most frequent phrase everywhere (its target kept)
    if phrases:
        const = collections.Counter(phrases).most_common(1)[0][0]
        abl = int(sum(k_true(const, turns[i]["cells"], turns[i]["things"]) for i in saying))
        abl_null = []
        for k in range(int(draws)):
            abl_null.append(abl)          # a constant phrase is invariant under dealing: every draw is the observed
        out["ablated"] = {"phrase": list(const), "observed": abl, "null_p95": float(np.percentile(abl_null, 95)),
                          "pass": abl > float(np.percentile(abl_null, 95)), "must_fail": True, "failed_as_it_must": not (abl > float(np.percentile(abl_null, 95)))}
    else:
        out["ablated"] = {"phrase": None, "observed": 0, "pass": False, "must_fail": True, "failed_as_it_must": True, "note": "no say at all"}
    # K-plant: one TRUE turn's phrase replaced by another turn's phrase that is NOT true of its thing
    plant = {"caught": None, "note": "no true turn to plant on"}
    for i in saying:
        if not truth[i]:
            continue
        t_i = thing_under(turns[i]["cells"], turns[i]["things"])
        for j in saying:
            if j == i:
                continue
            ph = tuple(str(w) for w in turns[j]["said"])
            if t_i is not None and not (set(ph) <= attrs(turns[i]["things"][int(t_i)])):
                planted = k_true(ph, turns[i]["cells"], turns[i]["things"])
                plant = {"caught": (planted is False), "turn": int(i), "from": int(j), "phrase": list(ph), "was_true": True, "reads": bool(planted)}
                break
        if plant.get("caught") is not None:
            break
    out["plant"] = plant
    return out


def exist_grade(rows: Sequence[Dict[str, object]], ear_by_moment: Dict[str, List[str]]) -> Dict[str, object]:
    """G2: every inner row's remembered moment exists on the tape with its topic among that moment's ear words (grade_life 4a's
    EXIST, reused in form); the plant: a row citing a moment on no tape must be counted MISSING."""
    n = len(rows)
    ok = 0
    missing: List[str] = []
    for r in rows:
        words = ear_by_moment.get(str(r.get("moment")))
        if words is not None and str(r.get("topic")) in words:
            ok += 1
        elif len(missing) < 10:
            missing.append(f"{r.get('moment')}:{r.get('topic')}")
    planted = exist_share([{"moment": "planted-no-such-moment", "topic": "ring"}], ear_by_moment)
    return {"n": n, "exist": (ok / n if n else None), "ok": ok, "missing_first": missing, "presence_moments": len(ear_by_moment),
            "pass": n > 0 and ok == n, "plant": {"share": planted, "caught": planted < 1.0}}


def exist_share(rows: Sequence[Dict[str, object]], ear_by_moment: Dict[str, List[str]]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if str(r.get("topic")) in (ear_by_moment.get(str(r.get("moment"))) or [])) / len(rows)


def coverage_grade(rows: Sequence[Dict[str, object]], mature: Sequence[str], bar: int = 10) -> Dict[str, object]:
    """G3's coverage: the topics of the bench's turns over the brain's mature words."""
    topics = [str(r.get("topic")) for r in rows]
    c = collections.Counter(topics)
    covered = sorted(set(topics) & set(mature))
    return {"n": len(rows), "mature": len(mature), "covered": len(covered), "bar": bar, "pass": len(covered) >= bar,
            "shares": {w: round(c[w] / len(rows), 4) for w in sorted(c)} if rows else {},
            "largest_share": (round(c.most_common(1)[0][1] / len(rows), 4) if rows else None),
            "sources": dict(collections.Counter(str(r.get("topic_source")) for r in rows)),
            "lock": I.locked(topics)}


def lock_grade(topics: Sequence[str]) -> Dict[str, object]:
    """G3's plant: the greedy walk's topics must LOCK (a cycle of period ≤ 4 visiting ≤ 5 words) and the detector must say so."""
    p = I.locked([str(t) for t in topics])
    k = len(set(topics))
    return {"n": len(topics), "distinct": k, "period": p, "caught": (p is not None and p <= 4 and k <= 5)}


def age_deciles(ages: Sequence[int], truth: Sequence[bool], deciles: int = 10) -> List[Dict[str, object]]:
    """R-AGE: the truth rate by deciles of the remembered scene's learn order (oldest first)."""
    if not ages:
        return []
    order = np.argsort(np.asarray(ages, dtype=float), kind="stable")
    parts = np.array_split(order, deciles)
    out = []
    for d, idx in enumerate(parts):
        if len(idx) == 0:
            continue
        out.append({"decile": d, "n": int(len(idx)), "age_lo": int(ages[int(idx[0])]), "age_hi": int(ages[int(idx[-1])]),
                    "true": int(sum(bool(truth[int(i)]) for i in idx)), "rate": round(float(np.mean([bool(truth[int(i)]) for i in idx])), 4)})
    return out


def paired(inner_true: Sequence[bool], live_true: Sequence[bool]) -> Dict[str, object]:
    """R-RET: inner vs live on the same scenes: both / inner only / live only / neither, the smallest passing gap 10/n, the sign test."""
    from tools.brain.grade_life import sign_test
    n = len(inner_true)
    b = sum(1 for i, l in zip(inner_true, live_true) if i and not l)
    c = sum(1 for i, l in zip(inner_true, live_true) if l and not i)
    both = sum(1 for i, l in zip(inner_true, live_true) if i and l)
    return {"n": n, "both": both, "inner_only": b, "live_only": c, "neither": n - both - b - c,
            "inner_rate": (sum(inner_true) / n if n else None), "live_rate": (sum(live_true) / n if n else None),
            "smallest_passing_gap": (10.0 / n if n else None), "sign_test_p_inner_better": sign_test(b, c), "sign_test_p_live_better": sign_test(c, b)}


def spearman(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    if len(x) < 3:
        return None
    rx = np.argsort(np.argsort(np.asarray(x, dtype=float))).astype(float)
    ry = np.argsort(np.argsort(np.asarray(y, dtype=float))).astype(float)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def self_grade(reliability: Dict[str, float], inner_rate: Dict[str, float], draws: int = 1000, seed: int = SEED) -> Dict[str, object]:
    """R-SELF: Spearman's ρ between the self's lived reliability and the inner turns' per-word truth, with a label-permutation null."""
    words = sorted(w for w in reliability if w in inner_rate)
    if len(words) < 3:
        return {"n_words": len(words), "rho": None, "note": "fewer than 3 words with both readings"}
    x = [float(reliability[w]) for w in words]
    y = [float(inner_rate[w]) for w in words]
    rho = spearman(x, y)
    null = []
    for k in range(int(draws)):
        rng = substream(seed, f"inner-self-null:{k}")
        r = spearman(x, [y[int(i)] for i in rng.permutation(len(y))])
        if r is not None:
            null.append(r)
    p = (sum(1 for r in null if r >= rho) / len(null)) if (null and rho is not None) else None
    return {"n_words": len(words), "rho": rho, "null_draws": len(null), "p_label_permutation": p,
            "null_p95": (float(np.percentile(null, 95)) if null else None), "words": words}


def assoc_grade(hops: Sequence[Dict[str, object]], counts: Dict[str, int], mature: Sequence[str], draws: int = 200, seed: int = SEED) -> Dict[str, object]:
    """R-ASSOC: the share of web hops whose re-seen say contains the topic the web chose, against a FREQUENCY-MATCHED null: the topic
    replaced by the mature word (≠ topic) whose hearing count is nearest, ties broken by the draw's substream."""
    if not hops:
        return {"n": 0, "share": None, "note": "no web hop"}
    said = [set(str(w) for w in (h.get("say") or {}).get("words", [])) for h in hops]
    topics = [str(h.get("topic")) for h in hops]
    share = sum(1 for s, t in zip(said, topics) if t in s) / len(hops)
    null = []
    mats = [str(w) for w in mature]
    for k in range(int(draws)):
        rng = substream(seed, f"inner-assoc-null:{k}")
        c = 0
        for s, t in zip(said, topics):
            others = [w for w in mats if w != t]
            if not others:
                continue
            d = np.array([abs(int(counts.get(w, 0)) - int(counts.get(t, 0))) for w in others], dtype=float)
            best = [w for w, dd in zip(others, d) if dd == d.min()]
            w = best[int(rng.integers(len(best)))]
            c += w in s
        null.append(c / len(hops))
    return {"n": len(hops), "share": share, "null_draws": len(null), "null_p95": float(np.percentile(null, 95)), "null_mean": float(np.mean(null)),
            "above_null_p95": share > float(np.percentile(null, 95))}


def spec_fields(things, words, referent) -> Dict[str, object]:
    """The fields the cross-check compares: every thing's shape / colour / size / top / left, the words, the referent."""
    return {"things": [[str(t.shape), str(t.colour), str(t.size), int(t.top), int(t.left)] for t in things],
            "words": [str(w) for w in words], "referent": (None if referent is None else int(referent))}


def file_fields(tf: Dict[str, object]) -> Dict[str, object]:
    sd = tf.get("scene_dict") or {}
    return {"things": [[str(t["shape"]), str(t["colour"]), str(t["size"]), int(t["top"]), int(t["left"])] for t in (sd.get("things") or [])],
            "words": [str(w) for w in (sd.get("words") or [])], "referent": (None if sd.get("referent") is None else int(sd["referent"]))}


def cross_check(rows: Sequence[Dict[str, object]], graded_idx: Sequence[int], eye_seq: Dict[str, int], truth_dir: Path) -> Dict[str, object]:
    """A2.2: for every graded row, the regenerated spec (brain.scene.world.train_scene(world_seed, scene)) against the life's
    truth/scene/<eye seq>.json, field for field; a row with no eye row on the tape or no file is REPORTED, never graded; the PLANT: the
    first file read with ONE field changed (the first thing's top + 1) must read as a mismatch by the same comparison."""
    scene_dir = truth_dir / "scene" if (truth_dir / "scene").is_dir() else truth_dir
    cross: Dict[str, object] = {"dir": str(scene_dir), "checked": 0, "mismatch": 0, "no_file": 0, "no_eye": 0, "first_mismatch": None, "plant_caught": None}
    for i in graded_idx:
        r = rows[i]
        seq = eye_seq.get(str(r.get("moment")))
        if seq is None:
            cross["no_eye"] += 1
            continue
        p = scene_dir / f"{int(seq):09d}.json"
        if not p.exists():
            cross["no_file"] += 1
            continue
        tf = json.loads(p.read_text())
        sc = W.train_scene(int(r["world_seed"]), int(r["scene"]))
        want, got = spec_fields(sc.things, sc.words, sc.referent), file_fields(tf)
        cross["checked"] += 1
        if want != got:
            cross["mismatch"] += 1
            if cross["first_mismatch"] is None:
                cross["first_mismatch"] = {"row": i, "file": str(p), "spec": want, "file_fields": got}
        if cross["plant_caught"] is None and got["things"]:
            planted = json.loads(json.dumps(tf))
            planted["scene_dict"]["things"][0]["top"] = int(planted["scene_dict"]["things"][0]["top"]) + 1
            assert planted != tf, "the plant changed nothing"
            cross["plant_caught"] = (file_fields(planted) != want)
    cross["pass"] = cross["checked"] > 0 and cross["mismatch"] == 0 and cross["plant_caught"] is True
    return cross


# ------------------------------------------------------------------------------------------------ grade
def tape_index(tape_dir: Path) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
    ear: Dict[str, List[str]] = collections.defaultdict(list)
    eye_seq: Dict[str, int] = {}
    for f in sorted(Path(tape_dir).glob("*.jsonl")):
        for r in _jsonl(f, needle='"sense": "e'):
            s = r.get("sense")
            m = (r.get("meta") or {}).get("moment")
            if s == "ear" and m is not None:
                ear[str(m)].append(str((r.get("meta") or {}).get("word")))
            elif s == "eye" and m is not None:
                eye_seq[str(m)] = int(r["seq"])
    return dict(ear), eye_seq


def live_turns(journal_dir: Path) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    for f in sorted(Path(journal_dir).glob("*.jsonl")):
        for r in _jsonl(f, needle='"act": "turn"'):
            if r.get("kind") == "brain" and r.get("act") == "turn" and r.get("moment") is not None:
                out.setdefault(str(r["moment"]), r)
    return out


def grade(a) -> int:
    out = Path(a.out)
    rows = list(_jsonl(out / "inner.jsonl"))
    run_rec = json.loads((out / "RUN.json").read_text())
    mature = list(run_rec.get("mature") or [])
    report: Dict[str, object] = {"out": str(out), "rows": len(rows), "run": {k: run_rec.get(k) for k in ("n", "rule", "plant", "counts", "read_only", "cpu_ms_per_row", "gen_last_seq", "genome_sha256")}}
    # G1: from the run's own counts (every eligible row turned once; the two plants never, counted by reason)
    counts = run_rec.get("counts") or {}
    report["G1"] = {"turns": counts.get("turns"), "n": run_rec.get("n"), "skipped": counts.get("skipped"),
                    "pass": counts.get("turns") == run_rec.get("n") == len(rows) and counts.get("skipped") == {"backlog": 1, "no backlog reading": 1}}
    # the truth per row (A8): regenerated; a scene of another hand, or a non-training index, is REPORTED, not graded
    turns: List[Dict[str, object]] = []
    graded_idx: List[int] = []
    not_graded: collections.Counter = collections.Counter()
    for i, r in enumerate(rows):
        if r.get("world") != "scene":
            not_graded[f"world {r.get('world')}"] += 1
            continue
        try:
            things = scene_things(int(r["world_seed"]), int(r["scene"]))
        except Exception as e:                                                   # pragma: no cover
            not_graded[f"no spec: {type(e).__name__}"] += 1
            continue
        say = r.get("say")
        turns.append({"said": (say or {}).get("words"), "cells": (say or {}).get("fix"), "things": things})
        graded_idx.append(i)
    report["not_graded"] = dict(not_graded)
    K = k_grade(turns, draws=int(a.draws))
    report["K"] = K
    truth_by_row = {graded_idx[j]: k_true(t["said"], t["cells"], t["things"]) for j, t in enumerate(turns)}
    # the truth-file cross-check (A8, strengthened by AMENDMENT 2 A2.2): the SCENE world's truth/scene/<eye seq>.json holds the WHOLE scene
    # dict; the regenerated spec must equal it field for field, and a planted one-field mismatch must be caught
    ear, eye_seq = tape_index(Path(a.tape))
    cross = cross_check(rows, graded_idx, eye_seq, Path(a.truth))
    report["truth_cross_check"] = cross
    # G2
    report["G2"] = exist_grade(rows, ear)
    # G3
    cov = coverage_grade(rows, mature)
    report["G3"] = cov
    if a.plant_out:                                  # A2.1: §0.2's topic-form greedy walk — it MUST lock and the detector must say so
        prow = list(_jsonl(Path(a.plant_out) / "inner.jsonl"))
        report["G3"]["plant"] = lock_grade([r.get("topic") for r in prow])
        report["G3"]["plant"]["rule"] = json.loads((Path(a.plant_out) / "RUN.json").read_text()).get("plant")
    if a.read_plant_out:                             # A2.1: the said-form greedy walk, a READ plant — its coverage printed beside the law's
        rrow = list(_jsonl(Path(a.read_plant_out) / "inner.jsonl"))
        cov_r = coverage_grade(rrow, mature)
        report["G3"]["read_plant"] = {"rule": json.loads((Path(a.read_plant_out) / "RUN.json").read_text()).get("plant"),
                                      "covered": cov_r["covered"], "mature": cov_r["mature"], "largest_share": cov_r["largest_share"],
                                      "lock": cov_r["lock"], "n": cov_r["n"]}
    # R-RET: paired with the live turn on the same scene
    lt = live_turns(Path(a.journal))
    inner_t, live_t, n_no_live = [], [], 0
    for j, i in enumerate(graded_idx):
        r = rows[i]
        L = lt.get(str(r.get("moment")))
        if L is None:
            n_no_live += 1
            continue
        t = turns[j]
        lsay = L.get("say") or {}
        inner_t.append(truth_by_row[i])
        live_t.append(k_true(lsay.get("words"), lsay.get("fix"), t["things"]))
    rr = paired(inner_t, live_t)
    rr["no_live_turn"] = n_no_live
    rr["presence_live_turns"] = len(lt)
    report["R_RET"] = rr
    # R-AGE
    ages = [int(rows[i]["learned"]) for i in graded_idx]
    report["R_AGE"] = age_deciles(ages, [truth_by_row[i] for i in graded_idx])
    # R-ASSOC
    web = json.loads(Path(a.web).read_text())
    Lst = web["webs"]["L"]
    counts_n = {w: int(v.get("n", 0)) for w, v in Lst["nodes"].items()}
    hops = [r for r in rows if int(r.get("chain", 1)) > 1 and str(r.get("topic_source", "")).startswith("web")]
    report["R_ASSOC"] = assoc_grade(hops, counts_n, mature, draws=int(a.draws))
    # R-SELF
    lived = (web.get("self") or {}).get("lived", {}).get("words", {})
    rel = {w: (v[1] / v[0]) for w, v in lived.items() if v and v[0]}
    by_topic: Dict[str, List[bool]] = collections.defaultdict(list)
    for i in graded_idx:
        by_topic[str(rows[i]["topic"])].append(truth_by_row[i])
    inner_rate = {w: float(np.mean(v)) for w, v in by_topic.items() if v}
    report["R_SELF"] = self_grade(rel, inner_rate, draws=int(a.self_draws))
    report["R_SELF"]["per_word"] = {w: {"reliability": rel.get(w), "inner_rate": inner_rate.get(w), "n": len(by_topic.get(w, []))} for w in sorted(set(rel) | set(inner_rate))}
    # cost
    report["cost"] = {"cpu_ms_per_row": run_rec.get("cpu_ms_per_row"), "cpu_s_load": run_rec.get("cpu_s_load")}
    (out / "GRADE.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    lines = report_lines(report)
    (out / "GRADE.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    gates = [report["G1"]["pass"], report["G2"]["pass"], report["G3"]["pass"], report["K"]["pass"], report["K"]["ablated"].get("failed_as_it_must"),
             report["K"]["plant"].get("caught"), report["truth_cross_check"]["pass"], report["G2"]["plant"]["caught"]]
    return 0 if all(bool(g) for g in gates) else 1


def _f(v, nd=3):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def report_lines(rep: Dict[str, object]) -> List[str]:
    K, G1, G2, G3 = rep["K"], rep["G1"], rep["G2"], rep["G3"]
    out = [f"INNER-1 BENCH · {rep['out']} · inner rows {rep['rows']} · rule {rep['run'].get('rule')} (plant {rep['run'].get('plant')}) · "
           f"read-only {rep['run'].get('read_only')} · {_f(rep['run'].get('cpu_ms_per_row'))} ms/row · generation last_seq {rep['run'].get('gen_last_seq')}",
           f"G1 fires exactly: turns {G1['turns']} of {G1['n']} eligible, skipped {G1['skipped']} → {'PASS' if G1['pass'] else 'FAIL'}",
           f"G2 grounded: EXIST {_f(G2['exist'], 4)} ({G2['ok']}/{G2['n']}; moments on the tape {G2['presence_moments']}) → {'PASS' if G2['pass'] else 'FAIL'} · "
           f"plant {'CAUGHT' if G2['plant']['caught'] else 'MISSED'}",
           f"G3 coverage: {G3['covered']} of {G3['mature']} mature words (bar {G3['bar']}) → {'PASS' if G3['pass'] else 'FAIL'} · largest share "
           f"{_f(G3.get('largest_share'), 3)} · sources {G3.get('sources')} · lock {G3.get('lock')}"]
    if "plant" in G3:
        p = G3["plant"]
        out.append(f"G3 plant ({p.get('rule')}): distinct {p['distinct']} · period {p['period']} → {'CAUGHT (locks)' if p['caught'] else 'MISSED'}")
    if "read_plant" in G3:
        q = G3["read_plant"]
        out.append(f"G3 read plant ({q.get('rule')}): covers {q['covered']} of {q['mature']} · largest share {_f(q.get('largest_share'), 3)} · "
                   f"lock {q.get('lock')} (a reading, no bar)")
    out.append(f"K TRUE OF ITS PAST: {K['observed']} of {K['n']} turns ({_f(K['rate'], 4)}; said {K['n_said']}, on a thing {K['n_on_thing']}) vs the dealt-phrase null "
               f"p95 {_f(K['null_p95'], 1)} (mean {_f(K['null_mean'], 1)}, max {K['null_max']}, {K['null_draws']} draws) → {'PASS' if K['pass'] else 'FAIL'}")
    ab = K["ablated"]
    out.append(f"K-ablated (constant phrase {ab.get('phrase')}): {ab['observed']} vs its null p95 {_f(ab.get('null_p95'), 1)} → "
               f"{'FAILS, as it must' if ab.get('failed_as_it_must') else 'PASSES — THE MARK IS BLIND'}")
    out.append(f"K-plant: {'CAUGHT' if K['plant'].get('caught') else 'MISSED'} ({K['plant']})")
    cc = rep["truth_cross_check"]
    out.append(f"truth files vs the regenerated spec: checked {cc['checked']} · mismatch {cc['mismatch']} · no file {cc['no_file']} · no eye {cc['no_eye']} · "
               f"planted mismatch {'CAUGHT' if cc['plant_caught'] else 'MISSED'} → {'PASS' if cc['pass'] else 'FAIL'}")
    out.append(f"not graded: {rep['not_graded']}")
    r = rep["R_RET"]
    out.append(f"R-RET paired with the live turn: n {r['n']} (no live turn {r['no_live_turn']}; live turns on record {r['presence_live_turns']}) · inner "
               f"{_f(r['inner_rate'], 4)} vs live {_f(r['live_rate'], 4)} · both {r['both']} · inner only {r['inner_only']} · live only {r['live_only']} · "
               f"neither {r['neither']} · smallest passing gap 10/n {_f(r['smallest_passing_gap'], 4)} · sign p(inner better) {_f(r['sign_test_p_inner_better'], 4)}")
    out.append("R-AGE (oldest → newest decile): " + " · ".join(f"d{d['decile']} [{d['age_lo']}-{d['age_hi']}] {d['true']}/{d['n']}={_f(d['rate'], 3)}" for d in rep["R_AGE"]))
    s = rep["R_ASSOC"]
    out.append(f"R-ASSOC: web hops {s.get('n')} · say contains the topic {_f(s.get('share'), 4)} vs frequency-matched null p95 {_f(s.get('null_p95'), 4)} "
               f"(mean {_f(s.get('null_mean'), 4)}) → {'above' if s.get('above_null_p95') else 'not above'} {s.get('note', '')}")
    sf = rep["R_SELF"]
    out.append(f"R-SELF: words {sf.get('n_words')} · Spearman ρ {_f(sf.get('rho'), 3)} · label-permutation p {_f(sf.get('p_label_permutation'), 4)} "
               f"(null p95 {_f(sf.get('null_p95'), 3)}, {sf.get('null_draws')} draws) {sf.get('note', '')}")
    out.append(f"cost: {_f(rep['cost'].get('cpu_ms_per_row'))} ms CPU per body row (load {_f(rep['cost'].get('cpu_s_load'))} s)")
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="inner_bench")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--gen", required=True)
    r.add_argument("--genome", required=True)
    r.add_argument("--tape", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--n", type=int, default=1000)
    r.add_argument("--rule", default="lift", choices=list(I.RULES))
    r.add_argument("--walk-from", dest="walk_from", default="said", choices=("said", "topic"))   # A2.1: "topic" = §0.2's walk, the plant's form
    r.add_argument("--restart", type=int, default=5)
    r.add_argument("--inhibit", type=int, default=2)
    g = sub.add_parser("grade")
    g.add_argument("--out", required=True)
    g.add_argument("--tape", required=True)
    g.add_argument("--journal", required=True)
    g.add_argument("--truth", required=True)
    g.add_argument("--web", required=True)
    g.add_argument("--draws", type=int, default=200)
    g.add_argument("--self-draws", type=int, default=1000)
    g.add_argument("--plant-out", default=None)                      # the topic-form greedy run (must lock)
    g.add_argument("--read-plant-out", dest="read_plant_out", default=None)   # the said-form greedy run (a reading)
    a = ap.parse_args(argv)
    return run(a) if a.cmd == "run" else grade(a)


if __name__ == "__main__":
    sys.exit(main())
