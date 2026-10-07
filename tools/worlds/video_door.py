# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-07 — PREREG-OPEN-WORLD-1 §2/§3 build (the law signed at f682314)
"""tools/worlds/video_door.py — THE VIDEO DOOR'S CONVERTER (PREREG-OPEN-WORLD-1 §2, docs/organism/whole/).

One real video file + one caption file → the organism's own TAPE format, regenerable byte-identical from the
hashed files (never the network twice). Written under tests/tools/test_video_door.py (tests first, RED then GREEN).

§2.1 the eye rows: ffmpeg's scene-cut detector finds candidate cuts; frames sampled at 1 Hz between cuts
(SAMPLE_HZ, a constant of the law); each frame letterboxed to the eye's own 128×128 RGB PNG; one eye row per
sampled frame, the payload under tape/payload/, the row's `sha` the payload's own. Written by creature/tape.py's
OWN Tape — the format's own writer, so the gates read the format, not a paraphrase.

§2.2 the ear rows: each caption cue's {text, start, duration} → whitespace-split tokens, lowercased, every
character outside a–z stripped, truncated to the ear's own WORD_SLOTS letters (the organism's own word form,
creature/senses/read_common.py:59's rule); a token that cleans to "" (digits/symbols) is DROPPED AND COUNTED
(never silent, §7). One ear row per kept token: sense "ear", meta.word, the cue's timing in meta as
start/duration, source "video-caption", the provenance flag track_kind.

The caption→moment mapping (declared, §1's "the caption mapping" is a constant of the law): a token is HEARD at
the first sampled frame at-or-after its start (the canvas on screen as the word begins); rows sort by time
(ear rows by caption start, eye rows by frame time, an ear row before an eye row on a tie) so the ear row
precedes the eye row of its own moment (PREREG §2.2's order law). A token past the last sampled frame has no
canvas to meet: dropped and COUNTED (dropped_late), never silently heard-and-lost.

§2.3 the tape: the conversion date's day file, rows ordered by time, seq 1..N, plus payload/, plus
record.json (the sources' sha256, the parameters, the counts — NO absolute paths, so two conversions of the
same files are byte-identical) and SHA256SUMS (the payload sha table — the converter's own check, §3 G-PLANT).

§2.4 the TP-dip reader (RESEARCH-OPEN-WORLD.md W1's machine form): running unigram/bigram counters over the
caption token stream; TP(Y|X) = count(XY)/count(X); a boundary where TP dips below the stream's own median TP
by ≥ TP_DIP_K × the median absolute deviation (declared, never tuned). `segment` prints the dip boundaries;
with --video it prints them beside ffmpeg's scene cuts with the overlap BOTH directions — a READING, no bar.

CLI:
  python3 -m tools.worlds.video_door convert --video V --captions C --out DIR [--date YYYY-MM-DD] [--track-kind authored|ASR]
  python3 -m tools.worlds.video_door segment --captions C [--video V]
  python3 -m tools.worlds.video_door verify --tape DIR [--video V] [--captions C]
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from typing import Dict, List, Optional, Sequence, Tuple

from creature.tape import Tape
from genome.world import WORD_SLOTS

SAMPLE_HZ = 1.0            # the law §2.1: one frame a second between cuts
CANVAS = 128               # the eye's own canvas (brain/scene/world.py:539's form)
SCENE_THRESHOLD = 0.4      # ffmpeg's scene score for a candidate cut — declared, never tuned
TP_DIP_K = 2.0             # the law §2.4: median TP − 2×MAD — declared, never tuned
OVERLAP_TOLERANCE_S = 2.0  # M-SEG's own declared window for the dip×cut overlap reading
EYE_SOURCE = "video"
EAR_SOURCE = "video-caption"

_NON_LETTER = re.compile(r"[^a-z]+")          # read_common.py:26's own rule
_TAG = re.compile(r"<[^>]+>")                 # VTT/SRT inline tags (<i>, <v Speaker>, …)
_TS = re.compile(r"^(?:(\d+):)?(\d+):(\d+)[,.](\d{1,3})$")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_path(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _ff(cmd: List[str], binary: bool = False) -> bytes:
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])}… exit {p.returncode}: {p.stderr.decode(errors='replace')[-600:]}")
    return p.stdout


# ----------------------------------------------------------------------------- the video side (§2.1)
def probe_duration(video: Path) -> float:
    out = _ff(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", str(video)])
    return round(float(out.decode().strip()), 3)


def scene_cuts(video: Path) -> List[float]:
    """ffmpeg's scene-cut detector (select gt(scene, SCENE_THRESHOLD)): the candidate cut times, seconds,
    in stream order. Deterministic for the same file and the same ffmpeg build. metadata=print reports on
    stderr, so both streams are searched."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
                        "-vf", f"select='gt(scene,{SCENE_THRESHOLD})',metadata=print", "-f", "null", "-"],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"scene detection failed: {p.stderr.decode(errors='replace')[-600:]}")
    text = p.stdout.decode(errors="replace") + p.stderr.decode(errors="replace")
    return sorted(round(float(m), 3) for m in re.findall(r"pts_time:([0-9.]+)", text))


def sample_times(duration: float, cuts: Sequence[float]) -> List[float]:
    """1 Hz between cuts (the law's constant): within each between-cut segment [a, b), the frame times are
    a, a+1, a+2, … < b — a cut restarts the grid, so a new scene's first frame is always sampled."""
    bounds = [0.0] + [c for c in sorted(cuts) if 0.0 < c < duration] + [duration]
    times: List[float] = []
    for a, b in zip(bounds, bounds[1:]):
        t = a
        while t < b - 1e-9:
            times.append(round(t, 3))
            t += SAMPLE_HZ
    return times


def extract_frame_png(video: Path, t: float) -> bytes:
    """One frame at `t` seconds, letterboxed (scale to fit, black pads) to CANVAS×CANVAS RGB PNG bytes."""
    vf = (f"scale={CANVAS}:{CANVAS}:force_original_aspect_ratio=decrease,"
          f"pad={CANVAS}:{CANVAS}:(ow-iw)/2:(oh-ih)/2,format=rgb24")
    png = _ff(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
               "-frames:v", "1", "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], binary=True)
    if not png:
        raise RuntimeError(f"no frame at t={t} in {video}")
    return png


# ----------------------------------------------------------------------------- the caption side (§2.2)
def _parse_ts(s: str) -> float:
    m = _TS.match(s.strip())
    if not m:
        raise ValueError(f"bad caption timestamp: {s!r}")
    h, mnt, sec, ms = m.groups()
    return round(int(h or 0) * 3600 + int(mnt) * 60 + int(sec) + int(ms.ljust(3, "0")) / 1000.0, 3)


def parse_captions(path: Path) -> List[Dict[str, object]]:
    """SRT and VTT cue forms → [{start, duration, text}] in file order. Pure: the same bytes, the same cues.
    Cue identifiers, WEBVTT headers and NOTE blocks carry no `-->` line and are never cues."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    cues: List[Dict[str, object]] = []
    for block in re.split(r"\n\s*\n", text):
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        tl = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if tl is None:
            continue
        m = re.search(r"(\S+)\s+-->\s+(\S+)", lines[tl])
        start, end = _parse_ts(m.group(1)), _parse_ts(m.group(2))
        payload = _TAG.sub("", " ".join(lines[tl + 1:])).strip()
        if payload:
            cues.append({"start": start, "duration": round(max(0.0, end - start), 3), "text": payload})
    return cues


def caption_tokens(cues: Sequence[Dict[str, object]]) -> Tuple[List[Dict[str, object]], int]:
    """Cues → the tape's word form: whitespace-split, lowercased, a–z only (the organism's own rule,
    read_common.py:59), truncated to WORD_SLOTS; a token that cleans to "" (digits/symbols) is dropped and
    COUNTED. Each kept token carries its cue's {start, duration} (the law §2.2)."""
    toks: List[Dict[str, object]] = []
    dropped = 0
    for cue in cues:
        for raw in str(cue["text"]).split():
            w = _NON_LETTER.sub("", raw.lower())[:WORD_SLOTS]
            if w:
                toks.append({"word": w, "start": float(cue["start"]), "duration": float(cue["duration"])})
            else:
                dropped += 1
    return toks, dropped


# ----------------------------------------------------------------------------- the TP-dip reader (§2.4)
def tp_dips(tokens: Sequence[str]) -> Dict[str, object]:
    """W1's machine form: TP(Y|X) = count(XY)/count(X) over the token stream's running unigram/bigram counts;
    a boundary after token i where TP < the stream's median TP AND median−TP ≥ TP_DIP_K × MAD (declared,
    never tuned). `boundaries` holds the index i of the token BEFORE each cut."""
    n = len(tokens)
    if n < 2:
        return {"n_tokens": n, "median": None, "mad": None, "k": TP_DIP_K, "tps": [], "boundaries": []}
    uni = Counter(tokens)
    bi = Counter(zip(tokens, tokens[1:]))
    tps = [bi[(tokens[i], tokens[i + 1])] / uni[tokens[i]] for i in range(n - 1)]
    med = median(tps)
    mad = median([abs(tp - med) for tp in tps])
    bounds = [i for i, tp in enumerate(tps) if tp < med and (med - tp) >= TP_DIP_K * mad]
    return {"n_tokens": n, "median": med, "mad": mad, "k": TP_DIP_K, "tps": tps, "boundaries": bounds}


# ----------------------------------------------------------------------------- the tape (§2.3)
def _iso(date: str, t: float) -> str:
    base = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return (base + timedelta(seconds=t)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _moment(date: str, t: float) -> str:
    return f"v{date.replace('-', '')}t{int(round(t * 1000)):09d}"


def convert(video_path: Path, captions_path: Path, out_tape_dir: Path, *, date: Optional[str] = None,
            track_kind: str = "authored") -> Dict[str, object]:
    """§2 whole: video + captions → the organism's tape, byte-identical for the same two files and date.
    Returns the stats dict (also written to record.json — every drop counted, never silent)."""
    video, captions, out = Path(video_path), Path(captions_path), Path(out_tape_dir)
    if out.name == "run":
        raise ValueError("the out dir must not be named 'run' (creature/tape.py:_resolve_tape_dir strips it)")
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"out dir is not empty: {out} (a conversion writes a FRESH tape dir — byte-identity)")
    date = date or datetime.now(timezone.utc).date().isoformat()
    datetime.strptime(date, "%Y-%m-%d")   # the day file's name, validated

    duration = probe_duration(video)
    cuts = scene_cuts(video)
    times = sample_times(duration, cuts)
    cues = parse_captions(captions)
    toks, dropped_nonword = caption_tokens(cues)

    # the declared caption→moment mapping: heard at the first sampled frame at-or-after the token's start
    dropped_late = 0
    ear_events: List[Tuple[float, int, Dict[str, object]]] = []
    for tok in toks:
        i = bisect.bisect_left(times, tok["start"] - 1e-9)
        if i == len(times):
            dropped_late += 1
            continue
        ear_events.append((tok["start"], 0, {**tok, "moment": _moment(date, times[i])}))
    eye_events = [(t, 1, {"t": t, "moment": _moment(date, t)}) for t in times]
    events = sorted(ear_events + eye_events, key=lambda e: (e[0], e[1]))  # stable: a cue's tokens keep their order

    tape = Tape(out.parent, out.name)
    for t, kind, ev in events:
        if kind == 1:
            tape.publish("eye", extract_frame_png(video, t),
                         {"moment": ev["moment"], "source": EYE_SOURCE, "t": t}, "png", at=_iso(date, t))
        else:
            tape.publish("ear", ev["word"].encode("utf-8"),
                         {"moment": ev["moment"], "word": ev["word"], "start": ev["start"],
                          "duration": ev["duration"], "track_kind": track_kind, "source": EAR_SOURCE},
                         "txt", at=_iso(date, ev["start"]))

    sums = "".join(f"{_sha256_path(f)}  payload/{f.name}\n" for f in sorted(tape.payload_dir.iterdir()))
    (tape.tape_dir / "SHA256SUMS").write_text(sums)
    stats = {"frames": len(times), "scene_cuts": cuts, "caption_cues": len(cues),
             "caption_tokens": len(toks) + dropped_nonword, "tokens_kept": len(toks),
             "dropped_nonword": dropped_nonword, "dropped_late": dropped_late,
             "ear_rows": len(ear_events), "eye_rows": len(eye_events), "rows": len(ear_events) + len(eye_events)}
    record = {"law": "PREREG-OPEN-WORLD-1 §2", "built": "tools/worlds/video_door.py", "date": date,
              "video": {"name": video.name, "sha256": _sha256_path(video), "bytes": video.stat().st_size},
              "captions": {"name": captions.name, "sha256": _sha256_path(captions), "bytes": captions.stat().st_size},
              "params": {"sample_hz": SAMPLE_HZ, "scene_threshold": SCENE_THRESHOLD, "canvas": CANVAS,
                         "track_kind": track_kind, "max_word_letters": WORD_SLOTS},
              "stats": stats}
    (tape.tape_dir / "record.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return stats


# ----------------------------------------------------------------------------- the converter's own check (§3 G-PLANT)
def verify(tape_dir: Path, video: Optional[Path] = None, captions: Optional[Path] = None) -> int:
    """The payload sha table + the source record: every row's `sha` == its payload's sha256, SHA256SUMS
    exactly the payload dir, and (if given) the source files' sha256 == record.json's. 0 iff all green."""
    tape_dir = Path(tape_dir)
    rows = [json.loads(l) for f in sorted(tape_dir.glob("*.jsonl"))
            for l in f.read_text().splitlines() if l.strip()]
    for r in rows:
        p = tape_dir / str(r["payload"])
        if not p.is_file() or _sha256_path(p) != r["sha"]:
            print(f"VERIFY FAIL: payload {r['payload']} sha mismatch (row seq {r.get('seq')})")
            return 1
    manifest = tape_dir / "SHA256SUMS"
    want = "".join(f"{_sha256_path(f)}  payload/{f.name}\n"
                   for f in sorted((tape_dir / "payload").iterdir()))
    if not manifest.is_file() or manifest.read_text() != want:
        print("VERIFY FAIL: SHA256SUMS does not match the payload dir")
        return 1
    record = json.loads((tape_dir / "record.json").read_text())
    for label, path in (("video", video), ("captions", captions)):
        if path is not None and _sha256_path(Path(path)) != record[label]["sha256"]:
            print(f"VERIFY FAIL: source {label} sha256 mismatch against record.json "
                  f"({Path(path).name} is not the file this tape was converted from)")
            return 1
    print(f"VERIFY OK: {len(rows)} rows, every payload sha matches, sources match the record")
    return 0


# ----------------------------------------------------------------------------- M-SEG's reading
def segment(captions_path: Path, video_path: Optional[Path] = None) -> Dict[str, object]:
    cues = parse_captions(captions_path)
    toks, dropped = caption_tokens(cues)
    tokens = [t["word"] for t in toks]
    d = tp_dips(tokens)
    print(f"tokens {d['n_tokens']} kept ({dropped} non-word dropped and counted)")
    if d["median"] is None:
        print("no pairs — no boundaries")
        return d
    print(f"TP median {d['median']:.4f} mad {d['mad']:.4f} k {d['k']}: "
          f"cut where TP < median and median−TP >= k*mad (declared, never tuned)")
    for i in d["boundaries"]:
        print(f"boundary after token {i}: {tokens[i]} | {tokens[i + 1]} (tp={d['tps'][i]:.4f})")
    if video_path is not None:
        cuts = scene_cuts(Path(video_path))
        bt = [toks[i + 1]["start"] for i in d["boundaries"]]
        c_with = sum(1 for c in cuts if any(abs(b - c) <= OVERLAP_TOLERANCE_S for b in bt))
        b_with = sum(1 for b in bt if any(abs(b - c) <= OVERLAP_TOLERANCE_S for c in cuts))
        print(f"scene cuts (ffmpeg, threshold {SCENE_THRESHOLD}): {cuts}")
        print(f"overlap (a READING, no bar — the two cutters answer different questions; "
              f"tolerance {OVERLAP_TOLERANCE_S}s declared): "
              f"cuts with a dip near: {c_with}/{len(cuts)}; dips with a cut near: {b_with}/{len(bt)}")
    return d


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="tools.worlds.video_door", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert", help="video + captions → the organism's tape")
    c.add_argument("--video", required=True, type=Path)
    c.add_argument("--captions", required=True, type=Path)
    c.add_argument("--out", required=True, type=Path)
    c.add_argument("--date", default=None, help="the tape's day (YYYY-MM-DD); default: today UTC")
    c.add_argument("--track-kind", default="authored", choices=["authored", "ASR"])
    s = sub.add_parser("segment", help="the TP-dip reader over the caption token stream")
    s.add_argument("--captions", required=True, type=Path)
    s.add_argument("--video", default=None, type=Path, help="print the dip×scene-cut overlap reading too")
    v = sub.add_parser("verify", help="the converter's own check: the payload sha table + the source record")
    v.add_argument("--tape", required=True, type=Path)
    v.add_argument("--video", default=None, type=Path)
    v.add_argument("--captions", default=None, type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "convert":
        stats = convert(a.video, a.captions, a.out, date=a.date, track_kind=a.track_kind)
        print(f"converted: {stats['eye_rows']} eye rows, {stats['ear_rows']} ear rows "
              f"({stats['dropped_nonword']} non-word + {stats['dropped_late']} late dropped and counted), "
              f"cuts {stats['scene_cuts']} → {a.out}")
        return 0
    if a.cmd == "segment":
        segment(a.captions, a.video)
        return 0
    return verify(a.tape, a.video, a.captions)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
