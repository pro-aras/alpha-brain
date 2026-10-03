"""streams.py — TOY C «FRAMES BY COMPRESSION»: the copies of the closed records, the readers, the PLANT and the SHUFFLE.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 16:48 +0400 — new module (RELAUNCH after the 15:50:57 crash: the first draft never reached disk), written
# test-first to tests/tools/test_toys_frames.py (stage 1), to docs/research/toys/PREREG-TOY-FRAMES.md §0, §1, §3 (co-signed 12:21 +0400).

THE GROUPING RULE (the law's §0 counts come from it; TestStreams.test_the_copies_reproduce_section_0 reproduces them): an ear row is one WORD; a MOMENT is the set of
ear rows sharing (source, moment name), its words in seq order, the moments in the order their FIRST row appears. 384 alpha4-1 moments have rows split by another row, so
grouping by consecutive run would count more moments than the law's 84,275.

MEMORY (RULES §6b/§6d): every reader STREAMS its files line by line and keeps only what it returns; the real tapes are 57 MB (alpha4-1) and 11 MB (brain-full) of jsonl —
their 1.3 GB / 0.2 GB payload directories are never opened. A line that does not parse, an ear row without a seq / source / moment / word, and a seq that does not strictly
increase across the ear rows read are a StreamError with the file and line, never a silent skip (a dropped row would move every count of the law).

  PYTHONPATH=. python3 -m tools.toys.frames.streams copy      # copy alpha4-1's and brain-full's tape + journal jsonl into scratch/toys-frames/copies (+ MANIFEST.json)
  PYTHONPATH=. python3 -m tools.toys.frames.streams verify    # re-hash the copies against the manifest
  PYTHONPATH=. python3 -m tools.toys.frames.streams counts    # the law's §0 counts, from the copies
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "scratch" / "toys-frames"
COPIES = ROOT / "copies"
SOURCES: Dict[str, Path] = {
    "alpha4-1": Path("/data/dev/genome-lives/alpha4-1"),
    "brain-full-20261102": Path("/data/dev/genome-lives/brain-full-20261102"),
}
SUBDIRS: Tuple[str, ...] = ("tape", "journal")
PLANT: Tuple[str, str] = ("zzq", "xxv")        # the law's §3 PLANT: two tokens in no vocabulary
SHUFFLE_TAG = 7                                # default_rng([20261103, 7, seed]): the law names seed 1 and no key; this key is mine (printed in the report header)
SEED_ROOT = 20261103


class StreamError(Exception):
    pass


@dataclass(frozen=True)
class Moment:
    source: str
    name: str
    words: Tuple[str, ...]
    seqs: Tuple[float, ...]


# ------------------------------------------------------------------------------------------------------------------ reading
def _rows(path: Path):
    """Yield (line number, row dict) for every line of a jsonl file, streaming; an unparseable line is a StreamError."""
    with open(path, "rb") as fh:
        for ln, raw in enumerate(fh, 1):
            if not raw.strip():
                continue
            try:
                yield ln, json.loads(raw)
            except ValueError as e:
                raise StreamError(f"{path}:{ln}: not JSON ({e})") from None


def load_moments(paths: Sequence[Path]) -> List[Moment]:
    """The moments of the ear rows of the given tape files, read in the order given: grouped by (source, moment name), words in row order, moments in the order
    their first row appears. Rows of any other sense add nothing."""
    words: Dict[Tuple[str, str], List[str]] = {}
    seqs: Dict[Tuple[str, str], List[float]] = {}
    last: Optional[float] = None
    for p in paths:
        p = Path(p)
        for ln, r in _rows(p):
            if r.get("sense") != "ear":
                continue
            meta = r.get("meta")
            if not isinstance(meta, dict):
                raise StreamError(f"{p}:{ln}: an ear row without meta")
            seq, src, mom, w = r.get("seq"), meta.get("source"), meta.get("moment"), meta.get("word")
            if not isinstance(seq, (int, float)) or isinstance(seq, bool):
                raise StreamError(f"{p}:{ln}: an ear row without a numeric seq ({seq!r})")
            if not (isinstance(src, str) and isinstance(mom, str) and isinstance(w, str) and w):
                raise StreamError(f"{p}:{ln}: an ear row without a source / moment / word ({src!r}, {mom!r}, {w!r})")
            if last is not None and not seq > last:
                raise StreamError(f"{p}:{ln}: seq {seq} does not strictly increase (the previous ear row's was {last})")
            last = seq
            key = (src, mom)
            if key not in words:
                words[key], seqs[key] = [], []
            words[key].append(w)
            seqs[key].append(seq)
    return [Moment(k[0], k[1], tuple(words[k]), tuple(seqs[k])) for k in words]      # dicts keep insertion order = first-row order


def load_says(paths: Sequence[Path]) -> List[Tuple[str, str, object]]:
    """The cells' says: journal rows with EXACTLY the keys {say, seq} (the filter the law's §0 count of 526 came from), as (frame, heard, seq) in file order."""
    out: List[Tuple[str, str, object]] = []
    for p in paths:
        for ln, r in _rows(Path(p)):
            if set(r) == {"say", "seq"}:
                s = r["say"]
                if not isinstance(s, dict) or "frame" not in s or "heard" not in s:
                    raise StreamError(f"{p}:{ln}: a say row without frame / heard")
                out.append((str(s["frame"]), str(s["heard"]), r["seq"]))
    return out


def scene_moments(ms: Sequence[Moment]) -> List[Moment]:
    return [m for m in ms if m.source == "scene"]


def flat_words(ms: Sequence[Moment]) -> List[str]:
    """Every word of every moment, one per ear row, in row (seq) order: the stream the cells HEARD (moments interleave when their rows do)."""
    rows = [(s, i, w) for i, m in enumerate(ms) for s, w in zip(m.seqs, m.words)]
    rows.sort(key=lambda r: (r[0], r[1]))
    return [w for _s, _i, w in rows]


# ------------------------------------------------------------------------------------------------------------------ split, plant, shuffle
def split_index(n: int) -> int:
    """The first 60 % of the moments are TRAIN (KW-1's fraction), in integer arithmetic: n * 3 // 5."""
    return (int(n) * 3) // 5


def split(ms: Sequence[Moment]) -> Tuple[List[Moment], List[Moment]]:
    i = split_index(len(ms))
    return list(ms[:i]), list(ms[i:])


def with_plant(ms: Sequence[Moment], every: int) -> List[Moment]:
    """A copy of the stream with a NEW moment (source «plant», words PLANT) inserted after every `every`-th moment; the originals are untouched and in order. The plant's
    two rows sit just after the preceding moment's last row (seq + 1/3, + 2/3), so they stay between that row and the next. The split is taken AFTER planting."""
    if every < 1:
        raise StreamError(f"with_plant: every must be >= 1, got {every}")
    out: List[Moment] = []
    k = 0
    for i, m in enumerate(ms, 1):
        out.append(m)
        if i % every == 0:
            k += 1
            last = float(m.seqs[-1])
            out.append(Moment("plant", f"plant{k:06d}", PLANT, (last + 1.0 / 3.0, last + 2.0 / 3.0)))
    return out


def shuffled(ms: Sequence[Moment], n_train: int, seed: int) -> List[Moment]:
    """The SHUFFLE (the law's §3): the words of the train part permuted among the train part's positions and the words of the held-out part among the held-out
    positions (the moments' sizes and rows kept; nothing crosses the split). Deterministic in `seed`."""
    rng = np.random.default_rng([SEED_ROOT, SHUFFLE_TAG, int(seed)])
    out: List[Moment] = []
    for part in (list(ms[:n_train]), list(ms[n_train:])):
        flat = [w for m in part for w in m.words]
        shuf = [flat[int(i)] for i in rng.permutation(len(flat))]
        pos = 0
        for m in part:
            k = len(m.words)
            out.append(Moment(m.source, m.name, tuple(shuf[pos:pos + k]), m.seqs))
            pos += k
    return out


# ------------------------------------------------------------------------------------------------------------------ the copies (G1)
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_sources(sources: Mapping[str, Path], dest: Path, subdirs: Sequence[str] = SUBDIRS) -> Dict[str, Dict[str, object]]:
    """Copy the *.jsonl files directly inside each source's `tape/` and `journal/` into dest/<name>/<sub>/ (never the payload directory, never SEQ, never anything
    else), reading the source and writing only the copy. Returns the manifest {«name/sub/file»: {source_sha256, copy_sha256, bytes}}; a copy whose hash differs from
    its source's is a StreamError (a source that changed under the copy, or a bad write)."""
    man: Dict[str, Dict[str, object]] = {}
    for name, src in sorted(sources.items()):
        for sub in subdirs:
            d = Path(src) / sub
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.jsonl")):
                if not f.is_file():
                    continue
                rel = f"{name}/{sub}/{f.name}"
                target = Path(dest) / name / sub / f.name
                target.parent.mkdir(parents=True, exist_ok=True)
                before = sha256_file(f)
                with open(f, "rb") as fin, open(target, "wb") as fout:
                    shutil.copyfileobj(fin, fout, 1 << 20)
                after = sha256_file(target)
                if after != before:
                    raise StreamError(f"{rel}: the copy's sha256 {after[:12]}… differs from its source's {before[:12]}…")
                man[rel] = {"source_sha256": before, "copy_sha256": after, "bytes": target.stat().st_size}
    return man


def verify_copies(dest: Path, man: Mapping[str, Mapping[str, object]]) -> List[str]:
    """The manifest keys whose copy under `dest` is missing or no longer hashes to what the manifest recorded (both the source's and the copy's hash)."""
    bad: List[str] = []
    for rel, e in sorted(man.items()):
        p = Path(dest) / rel
        if not p.is_file() or sha256_file(p) != e["copy_sha256"] or e["copy_sha256"] != e["source_sha256"]:
            bad.append(rel)
    return bad


# ------------------------------------------------------------------------------------------------------------------ the law's §0 counts
def section0_counts(ms: Sequence[Moment]) -> Dict[str, object]:
    """Moments, words, and per source: moments, words, distinct words, and the words-a-moment histogram."""
    by: Dict[str, Dict[str, object]] = {}
    for m in ms:
        e = by.setdefault(m.source, {"moments": 0, "words": 0, "vocab": set(), "per_moment": Counter()})
        e["moments"] += 1
        e["words"] += len(m.words)
        e["vocab"].update(m.words)
        e["per_moment"][len(m.words)] += 1
    out = {src: {"moments": e["moments"], "words": e["words"], "distinct": len(e["vocab"]), "per_moment": dict(sorted(e["per_moment"].items()))}
           for src, e in by.items()}
    return {"moments": sum(e["moments"] for e in out.values()), "words": sum(e["words"] for e in out.values()), "by_source": out}


# ------------------------------------------------------------------------------------------------------------------ the command line
def _main(argv: Sequence[str]) -> int:
    cmd = argv[0] if argv else ""
    man_path = COPIES / "MANIFEST.json"
    if cmd == "copy":
        COPIES.mkdir(parents=True, exist_ok=True)
        man = copy_sources(SOURCES, COPIES)
        man_path.write_text(json.dumps(man, indent=1, sort_keys=True))
        print(f"copied {len(man)} files into {COPIES}; manifest {man_path}; bytes {sum(int(e['bytes']) for e in man.values())}")
        for rel, e in sorted(man.items()):
            print(f"  {rel} {e['bytes']} sha256 {e['copy_sha256'][:16]}…")
        return 0
    if cmd == "verify":
        man = json.loads(man_path.read_text())
        bad = verify_copies(COPIES, man)
        print(f"verified {len(man)} copies; mismatches {bad}")
        return 1 if bad else 0
    if cmd == "counts":
        for name in ("alpha4-1", "brain-full-20261102"):
            ms = load_moments(sorted((COPIES / name / "tape").glob("*.jsonl")))
            c = section0_counts(ms)
            print(name, json.dumps(c, sort_keys=True))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
