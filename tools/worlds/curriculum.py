# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 09:28 +0400 — PREREG-OPEN-WORLD-4 §2 build (the law
# signed at d7213d4; its sha256 dd60548061a0…88ad5 carried by docs/organism/whole/records/open-world-4/SEAT-LINE.txt).
"""tools/worlds/curriculum.py — THE CURRICULUM MACHINERY + THE CO-REFERENCE INSTRUMENT (PREREG-OPEN-WORLD-4,
docs/organism/whole/, V3). Written under tests/tools/test_curriculum.py (tests first, RED then GREEN).

NO new organism code (the law §2): this module reads caption files, converted tapes and replay journals; the
converter (video_door.py), the cutter (event_cutter.py), the front (creature/senses/vfront.py) and the bench
genome are sha-pinned instruments of record, imported UNCHANGED, never edited under this law.

THE DECLARED PARAMETERS (the law §1/§2.2 — fixed before any reading, never tuned after one):
- TARGET_WORDED / CAP_VIDEOS / CAP_MEDIA_S: the sizing rule — videos added in SHELF ORDER until the
  curriculum's cumulative WORDED CANVASES (distinct sampled frames carrying ≥ 1 ear token, V0's own declared
  caption→moment mapping, computed from the converted per-video tapes) reach ≥ 500 — twice the brain's first
  calibration cadence (250 learned scenes). Cap: 30 videos / 75 minutes of media. A video that would cross a
  cap is the WALL: the walk stops there (never a skip ahead — the only skip is the law's caption fallback,
  applied BEFORE the walk); below target at the wall is FAIL-SIZE, named, never stretched.
- THE GRADIENT: the sourced set ordered by simpleness = the caption stream's TYPE-TOKEN RATIO (unique kept
  tokens / total kept tokens, ASCENDING — repetition is the simpler speech), ties by WORDS-PER-SECOND (slower
  first; computed from the caption files alone — the stream's own span, never the media's), a double tie by
  the shelf's own index (the mechanical total order, declared). Printed as a table, never hand-ranked.
- THE CONCAT (V1's form, mirrored from records/open-world-2/bench/tape-502's own rows): the per-video tapes
  in gradient order, all converted with the same --date (the curriculum date — one day file); seq reassigned
  1..N in row order; payload files renamed to the new seq (bytes untouched — the row's sha stands); meta gains
  `series` (V1's own concat key) AND `video` (the law §1's ONE additive key), both = the source's short name;
  `source`, `at`, meta.t and meta.moment are UNTOUCHED (per-source clocks — moments restart per video, the
  collisions are V1's form's own, declared). Byte-identical for the same inputs.
- THE CO-REFERENCE INSTRUMENT (§2.2): a motion event = a frame whose wired journal's `front.t_mass` exceeds
  the stream's own median + 3×MAD (the cutter's declared threshold form, imported unchanged — plain exceedance,
  never the integrator); a caption token is SYNCHRONIZED when its onset lands within ±1 s of a motion-event
  frame. The tape's own resolution makes this exact: within one video the 1 Hz sampling grid's spacing never
  exceeds 1 s (a scene cut only restarts the grid), so |Δcanvas| ≤ 1 ⇔ |Δt| ≤ 1 s — the instrument works in
  canvas space, ±1 canvas, SAME VIDEO only (two frames of different videos are never within ±1 s of each
  other in any honest clock; the law's named resolution limit). A token's canvas is the FIRST eye row after
  its ear row in seq order — V0's mapping realized by the tape's own order law (an ear row precedes the eye
  row of its own moment); the mapping is asserted against the rows' moments (a mismatch is a finding, never
  patched) and is collision-free by position, never by the moment string.
- THE SHUFFLED-ONSET CONTROL (§2.2, seed 20261777 — the cutter's own declared constant): every token's onset
  redrawn as a UNIFORM-RANDOM CANVAS of the tape (V1's shuffled-boundary form — the same count at
  uniform-random frames). A PERMUTATION of the real onsets is vacuous for this instrument — it preserves the
  onset multiset, hence the synchronized canvas set, exactly — so the uniform redraw is the honest control;
  synchrony must vanish. Printed beside the real, never one without the other.
- M-LEARN is V1/V2's own form whole: event_cutter.analyze over the wired journal + the curriculum tape (the
  memory effect at the cutter's boundaries, real vs matched controls vs the shuffled-boundary control, every
  boundary count with its chance expectation). M-SEG is video_door.tp_dips over the full caption token stream
  (the W1 instrument at curriculum scale — a READING, no bar).

CLI (the bench drivers live in scratch/ow4/; the machinery here is what the tests pin):
  (library only — the reading's composition is the bench driver's, printed to records/open-world-4/bench/)
"""
from __future__ import annotations

import bisect
import json
import random
import shutil
from pathlib import Path
from statistics import median
from typing import Dict, List, Sequence

from tools.worlds import event_cutter as EC
from tools.worlds import video_door as VD

TARGET_WORDED = 500                # §1: ≥ 500 worded canvases — twice the brain's first calibration at 250
CAP_VIDEOS = 30                    # §1's cap
CAP_MEDIA_S = 75 * 60              # §1's cap, seconds of media
SYNC_TOLERANCE = 1                 # §2.2: ±1 s AT THE TAPE'S OWN 1 Hz SAMPLING — one canvas (named limit)
SHUFFLE_SEED = EC.SHUFFLE_SEED     # 20261777 — the declared fixed seed, the cutter's own constant
MOTION_K = EC.MAD_K                # 3.0 — the cutter's declared median + k×MAD threshold form


# ----------------------------------------------------------------------------- the caption side (§1, the gradient)
def caption_stats(path) -> Dict[str, object]:
    """One caption file → its gradient stats, from the captions ALONE (the law §1): the kept tokens (the
    converter's own word form, imported unchanged), the type-token ratio, and words-per-second over the
    caption stream's OWN span (the last cue's end — the media duration is never read here)."""
    cues = VD.parse_captions(Path(path))
    toks, dropped = VD.caption_tokens(cues)
    words = [str(t["word"]) for t in toks]
    span = max((float(c["start"]) + float(c["duration"]) for c in cues), default=0.0)
    n = len(words)
    return {"tokens": words, "n_tokens": n, "n_unique": len(set(words)),
            "ttr": (len(set(words)) / n) if n else None, "span_s": span,
            "wps": (n / span) if span > 0 else None, "dropped_nonword": dropped}


def gradient_order(entries: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """§1's simpleness gradient, mechanical: type-token ratio ASCENDING (repetition is the simpler speech),
    ties by words-per-second (slower first), a double tie by the shelf's own index. Never hand-ranked."""
    return sorted(entries, key=lambda e: (e["ttr"], e["wps"], e["shelf_index"]))


# ----------------------------------------------------------------------------- the tape side (the sizing walk's input)
def _tape_rows(tape_dir: Path) -> List[Dict[str, object]]:
    tape_dir = Path(tape_dir)
    days = sorted(tape_dir.glob("*.jsonl"))
    if len(days) != 1:
        raise RuntimeError(f"{tape_dir}: expected exactly one day file, got {[d.name for d in days]}")
    return [json.loads(l) for l in days[0].read_text().splitlines() if l.strip()]


def worded_canvases(tape_dir: Path) -> Dict[str, int]:
    """§1's sizing unit on ONE converted per-video tape: distinct sampled frames carrying ≥ 1 ear token under
    V0's declared mapping (the ear rows carry their mapped frame's own moment — the converter's §2.2). On a
    per-video tape the eye moments are unique per frame (asserted — a collision here is a finding)."""
    rows = _tape_rows(tape_dir)
    eye = [r for r in rows if r["sense"] == "eye"]
    ear = [r for r in rows if r["sense"] == "ear"]
    moments = [r["meta"]["moment"] for r in eye]
    if len(set(moments)) != len(moments):
        raise RuntimeError(f"{tape_dir}: eye-row moments not unique per frame ({len(moments) - len(set(moments))} "
                           "collisions) — worded_canvases is declared for per-video tapes; a finding, never patched")
    ear_moments = {r["meta"]["moment"] for r in ear}
    return {"frames": len(eye), "ear_rows": len(ear),
            "worded": sum(1 for r in eye if r["meta"]["moment"] in ear_moments)}


def sizing_walk(candidates: Sequence[Dict[str, object]], target: int = TARGET_WORDED,
                cap_videos: int = CAP_VIDEOS, cap_media_s: float = CAP_MEDIA_S) -> Dict[str, object]:
    """§1's sizing rule, mechanical: candidates in SHELF ORDER (only the caption-rule survivors reach here),
    each {name, worded, media_s, shelf_index}. Take until cumulative worded ≥ target; the caps are WALLS —
    a video that would cross one is never taken and the next is never skipped to. `sized` False below the
    target at any wall = the law's FAIL-SIZE row, named, never stretched."""
    taken: List[Dict[str, object]] = []
    worded, media = 0, 0.0
    stop = "shelf exhausted"
    for c in candidates:
        if len(taken) >= cap_videos:
            stop = "cap-videos"
            break
        if media + float(c["media_s"]) > cap_media_s:
            stop = "cap-media"
            break
        taken.append(dict(c))
        worded += int(c["worded"])
        media += float(c["media_s"])
        if worded >= target:
            stop = "sized"
            break
    return {"taken": taken, "worded": worded, "media_s": media, "stop": stop, "sized": worded >= target,
            "target": target, "cap_videos": cap_videos, "cap_media_s": cap_media_s}


# ----------------------------------------------------------------------------- the concat (V1's form + the law's one key)
def concat_plan(videos: Sequence[Dict[str, object]], date: str) -> Dict[str, object]:
    """The concat plan — a file of record (§2.1: the same files + the same plan = the same tape): the sourced
    tapes in GRADIENT order, each {name, tape}, under the curriculum date. Deterministic for the same inputs."""
    return {"law": "PREREG-OPEN-WORLD-4 §1/§2.1", "date": date,
            "form": "V1's concat (records/open-world-2/bench/tape-502) mirrored exactly + the ONE additive "
                    "meta key `video`; seq renumbered 1..N; payload renamed to the new seq; meta.series (V1's "
                    "own concat key) and meta.video = the source's short name; source/at/meta.t/meta.moment "
                    "untouched (per-source clocks)",
            "videos": [{"name": str(v["name"]), "tape": str(v["tape"])} for v in videos]}


def concat_tapes(plan: Dict[str, object], out_dir: Path) -> Dict[str, int]:
    """V1's concat form, mirrored from tape-502's own rows, + the law §1's ONE additive meta key `video`.
    Byte-identical for the same inputs (the plan, the tapes, the date)."""
    out = Path(out_dir)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"out dir is not empty: {out} (a concat writes a FRESH tape dir — byte-identity)")
    out.mkdir(parents=True, exist_ok=True)
    (out / "payload").mkdir()
    date = str(plan["date"])
    seq, n_eye, n_ear = 0, 0, 0
    lines: List[str] = []
    for v in plan["videos"]:
        tape_dir = Path(v["tape"])
        days = sorted(tape_dir.glob("*.jsonl"))
        if [d.name for d in days] != [f"{date}.jsonl"]:
            raise RuntimeError(f"{tape_dir}: the day file is not the curriculum date's ({date}.jsonl): "
                               f"{[d.name for d in days]} — a mixed-date set is not this curriculum")
        for line in days[0].read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            seq += 1
            ext = str(r["payload"]).rsplit(".", 1)[1]
            payload_rel = f"payload/{seq:09d}.{ext}"
            shutil.copyfile(tape_dir / str(r["payload"]), out / payload_rel)   # the bytes untouched
            meta = dict(r["meta"])
            meta["series"] = str(v["name"])    # V1's own concat key (tape-502's rows carry it)
            meta["video"] = str(v["name"])     # the law §1's ONE additive key — provenance honest
            row = {"seq": seq, "at": r["at"], "sense": r["sense"], "sha": r["sha"],
                   "payload": payload_rel, "meta": meta}
            n_eye += row["sense"] == "eye"
            n_ear += row["sense"] == "ear"
            lines.append(json.dumps(row) + "\n")
    (out / f"{date}.jsonl").write_text("".join(lines))
    return {"rows": seq, "eye": n_eye, "ear": n_ear}


# ----------------------------------------------------------------------------- the co-reference instrument (§2.2)
def token_canvases(tape_dir: Path) -> List[Dict[str, object]]:
    """Every kept ear token → its canvas (0-based, the tape's eye-row order): the FIRST eye row after the ear
    row in seq order — V0's declared caption→moment mapping realized by the tape's own order law (an ear row
    precedes the eye row of its own moment). Asserted against the rows' moments; collision-free by POSITION
    (V1's concat form repeats moment strings across videos — never a key)."""
    rows = _tape_rows(tape_dir)
    eye_pos = [i for i, r in enumerate(rows) if r["sense"] == "eye"]
    out: List[Dict[str, object]] = []
    for i, r in enumerate(rows):
        if r["sense"] != "ear":
            continue
        j = bisect.bisect_right(eye_pos, i)
        if j >= len(eye_pos):
            raise RuntimeError(f"{tape_dir}: ear row seq {r['seq']} ({r['meta'].get('word')!r}) has no following "
                               "eye row — V0's mapping dropped no kept token; a finding, never patched")
        e = rows[eye_pos[j]]
        if e["meta"].get("moment") != r["meta"].get("moment"):
            raise RuntimeError(f"{tape_dir}: ear row seq {r['seq']} moment {r['meta'].get('moment')} meets eye "
                               f"row seq {e['seq']} moment {e['meta'].get('moment')} — a finding, never patched")
        out.append({"word": str(r["meta"]["word"]), "start": float(r["meta"]["start"]), "canvas": j,
                    "video": r["meta"].get("video"), "seq": int(r["seq"])})
    return out


def canvas_videos(tape_dir: Path) -> List[object]:
    """The video (the concat's additive key; None on an un-concatenated tape) of every canvas, eye-row order."""
    return [r["meta"].get("video") for r in _tape_rows(tape_dir) if r["sense"] == "eye"]


def motion_events(tmass: Sequence[float]) -> Dict[str, object]:
    """§2.2's detector: a motion event = a frame whose front.t_mass EXCEEDS the stream's own median + 3×MAD
    (the cutter's declared threshold form, plain exceedance — never the integrator; declared, never tuned)."""
    tmass = [float(x) for x in tmass]
    med = median(tmass)
    mad = median([abs(x - med) for x in tmass])
    thr = med + MOTION_K * mad
    return {"events": [i for i, x in enumerate(tmass) if x > thr],
            "median": med, "mad": mad, "threshold": thr}


def synchronized(tokens: Sequence[Dict[str, object]], events: Sequence[int], cvideos: Sequence[object],
                 tol: int = SYNC_TOLERANCE) -> Dict[str, object]:
    """A token is SYNCHRONIZED when a motion-event frame of the SAME VIDEO lands within ±tol canvases of its
    own canvas — the ±1 s at the tape's own 1 Hz sampling (within one video |Δcanvas| ≤ 1 ⇔ |Δt| ≤ 1 s: the
    grid's spacing never exceeds 1 s; the law's named resolution limit)."""
    by_video: Dict[object, List[int]] = {}
    for e in events:
        by_video.setdefault(cvideos[e], []).append(e)
    tix: List[int] = []
    cset = set()
    for k, t in enumerate(tokens):
        c = int(t["canvas"])
        if any(abs(c - e) <= tol for e in by_video.get(cvideos[c], [])):
            tix.append(k)
            cset.add(c)
    return {"token_ixs": tix, "canvases": sorted(cset)}


def shuffled_onsets(n_tokens: int, n_canvases: int, seed: int = SHUFFLE_SEED) -> List[int]:
    """§2.2's shuffled-onset control: every token's onset redrawn as a UNIFORM-RANDOM CANVAS of the tape
    (V1's shuffled-boundary form — the same count at uniform-random frames; a permutation of the real onsets
    preserves the canvas set exactly and is VACUOUS for this instrument), the declared fixed seed."""
    rng = random.Random(seed)
    return [rng.randrange(n_canvases) for _ in range(n_tokens)]


def _learn_block(learns: Sequence[int], canvases: Sequence[int]) -> Dict[str, object]:
    tot = sum(int(learns[c]) for c in canvases)
    return {"frames": len(canvases), "total": tot, "mean": (tot / len(canvases)) if canvases else None}


def sync_reading(tokens: Sequence[Dict[str, object]], tmass: Sequence[float], learns: Sequence[int],
                 cvideos: Sequence[object], tol: int = SYNC_TOLERANCE,
                 seed: int = SHUFFLE_SEED) -> Dict[str, object]:
    """The law §2.2's whole co-reference computation over the WIRED journal: the motion events on the
    front.t_mass stream; the synchronized share of tokens; the learning (births + brain learn rows — the
    reading's own currency, event_cutter.learn_per_frame's) at synchronized-token canvases vs matched
    non-synchronized controls (the same count, nearest in time, SAME VIDEO — the cutter's own matcher with
    the video as the source key); the shuffled-onset control beside (synchrony must vanish). Every number
    printed in pairs, never one without the other."""
    n = len(tmass)
    if not (n == len(learns) == len(cvideos)):
        raise RuntimeError(f"the wired streams disagree: t_mass {n}, learns {len(learns)}, canvases "
                           f"{len(cvideos)} — a finding, never patched")
    ev = motion_events(tmass)
    real = synchronized(tokens, ev["events"], cvideos, tol)
    rset = set(real["canvases"])
    rctrl = EC.matched_controls(rset, n, list(cvideos))          # the cutter's own matcher, the video as the key
    sh = shuffled_onsets(len(tokens), n, seed)
    shuf = synchronized([dict(t, canvas=c) for t, c in zip(tokens, sh)], ev["events"], cvideos, tol)
    sset = set(shuf["canvases"])
    sctrl = EC.matched_controls(sset, n, list(cvideos))
    # the chance expectation: the share of canvases a uniform-random onset would synchronize (the exact
    # ±1-same-video neighborhoods of the real events)
    near = set()
    for e in ev["events"]:
        for c in range(max(0, e - tol), min(n, e + tol + 1)):
            if cvideos[c] == cvideos[e]:
                near.add(c)
    return {"n_canvases": n, "n_tokens": len(tokens), "seed": seed, "tol": tol, "motion": ev,
            "chance_share": (len(near) / n) if n else None,
            "real": {"token_ixs": real["token_ixs"], "canvases": real["canvases"],
                     "share": (len(real["token_ixs"]) / len(tokens)) if tokens else None,
                     "learning": _learn_block(learns, sorted(rset)),
                     "control": _learn_block(learns, rctrl), "control_canvases": rctrl},
            "shuffled": {"token_ixs": shuf["token_ixs"], "canvases": shuf["canvases"],
                         "share": (len(shuf["token_ixs"]) / len(tokens)) if tokens else None,
                         "learning": _learn_block(learns, sorted(sset)),
                         "control": _learn_block(learns, sctrl), "control_canvases": sctrl}}
