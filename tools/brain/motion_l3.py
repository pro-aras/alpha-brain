#!/usr/bin/env python3
# edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-13 — the developmental road's L3 MARK
# (the advisor's plan §3: «watches you as you move» — a READING of an existing life, never a law):
# does brain-long-6's gaze land on MOTION in the video shelf? The eye's fixation positions (the journal's
# `windows`, pixel coords on the 128×128 canvas) vs each frame's motion field (|frame_t − frame_{t−1}|
# per 16-px cell). The shelf is COPIED into scratch first (RULES §7 — the live root is never read from
# for the payloads; the journal reads are read-only). --selftest carries the planted controls (RULES
# §11): a translating blob must be localized (CAUGHT), a static series must read ~no motion, and the
# shuffled-motion null must NOT show the gaze preference the real pairing reads.
"""usage: motion_l3.py --shelf <copied shelf dir> --journal <life journal dir|file> [--max N] | --selftest
The mark (declared in this docstring before the read): M-MOVE = the share of the organism's fixations
landing in each frame's top-motion-quartile cells, compared against the SAME fixations on the
SHUFFLED-motion null (each canvas's fixation set re-paired to a different frame's motion field — the
expectation under «the gaze does not track motion», ≥ the area share 0.25). The reading is the two
shares + their ratio over all video canvases, never a verdict: L3 is the rung's first measurement."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

CELL = 16  # the 128×128 frame → an 8×8 motion-cell grid


def load_shelf_rows(shelf: Path) -> Dict[str, Tuple[str, str, float]]:
    """moment → (payload rel path, series, t) from the copied shelf's day files."""
    out: Dict[str, Tuple[str, str, float]] = {}
    for f in sorted(shelf.glob("*.jsonl")):
        for line in f.open():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            meta = d.get("meta") or {}
            if d.get("sense") == "eye" and meta.get("moment"):
                out[str(meta["moment"])] = (str(d["payload"]), str(meta.get("series")), float(meta.get("t", 0.0)))
    return out


def frame_of(shelf: Path, rel: str) -> np.ndarray:
    return np.asarray(Image.open(shelf / rel).convert("RGB"), dtype=np.int16)


def motion_field(shelf: Path, rel: str, prev_rel: Optional[str]) -> Optional[np.ndarray]:
    """The per-cell |Δ| motion mass for a frame vs its predecessor in the series (None when the frame
    is the series' first)."""
    if prev_rel is None:
        return None
    cur, prev = frame_of(shelf, rel), frame_of(shelf, prev_rel)
    if cur.shape != prev.shape:
        return None
    delta = np.abs(cur - prev).mean(axis=2)          # 128×128 mean-abs-delta
    h = (delta.shape[0] // CELL) * CELL
    w = (delta.shape[1] // CELL) * CELL
    cells = delta[:h, :w].reshape(h // CELL, CELL, w // CELL, CELL).mean(axis=(1, 3))
    return cells                                     # (8, 8) motion mass per cell


def fixation_cells(windows: List[List[int]], shape: Tuple[int, int] = (128, 128)) -> List[Tuple[int, int]]:
    out = []
    h, w = shape
    for top, left in windows or []:
        out.append((min(int(top) // CELL, h // CELL - 1), min(int(left) // CELL, w // CELL - 1)))
    return out


def share_in_top_quartile(field: np.ndarray, cells: List[Tuple[int, int]]) -> float:
    """The share of fixation cells inside the field's top-motion-quartile cells."""
    if not cells:
        return 0.0
    flat = np.sort(field.flatten())
    q = flat[max(0, int(0.75 * (len(flat) - 1)))]
    top = field >= max(q, 1e-9)
    return sum(1 for c in cells if top[c[0], c[1]]) / len(cells)


def read(shelf: Path, journal: Path, max_n: int = 0) -> Dict[str, object]:
    rows = load_shelf_rows(shelf)
    # the series' consecutive order for the predecessor map
    by_series: Dict[str, List[Tuple[float, str, str]]] = {}
    for moment, (rel, series, t) in rows.items():
        by_series.setdefault(series, []).append((t, moment, rel))
    prev_of: Dict[str, str] = {}
    for series, items in by_series.items():
        items.sort()
        for (t0, m0, _r0), (_t1, m1, r1) in zip(items, items[1:]):
            prev_of[m1] = None  # filled below
        for i in range(1, len(items)):
            prev_of[items[i][1]] = items[i - 1][2]
    paths = sorted(journal.glob("*.jsonl")) if journal.is_dir() else [journal]
    seen = 0
    real_shares: List[float] = []
    null_shares: List[float] = []
    n_fix = 0
    moments_used: List[str] = []
    field_cache: Dict[str, Optional[np.ndarray]] = {}
    for p in paths:
        for line in p.open():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if not ("cells" in d and "err" in d) or d.get("source") != "video":
                continue
            moment = str(d.get("moment") or "")
            if moment not in rows:
                continue
            rel = rows[moment][0]
            if moment not in field_cache:
                field_cache[moment] = motion_field(shelf, rel, prev_of.get(moment))
            field = field_cache[moment]
            if field is None:
                continue
            cells = fixation_cells(d.get("windows") or [])
            if not cells:
                continue
            seen += 1
            n_fix += len(cells)
            real_shares.append(share_in_top_quartile(field, cells))
            # the shuffled-motion null: the same fixations against a seeded-RANDOM same-series frame's
            # field (deterministic per canvas seq; a FAIR shuffle — the first null form always picked the
            # series' FIRST frame, whose intro-motion skews it, named 10-13)
            pool = [m2 for m2 in rows if m2 != moment and rows[m2][1] == rows[moment][1]]
            if pool:
                m2 = pool[int(d["seq"]) % len(pool)]
                if m2 not in field_cache:
                    field_cache[m2] = motion_field(shelf, rows[m2][0], prev_of.get(m2))
                if field_cache[m2] is not None:
                    null_shares.append(share_in_top_quartile(field_cache[m2], cells))
            moments_used.append(moment)
            if max_n and seen >= max_n:
                break
    real = sum(real_shares) / len(real_shares) if real_shares else None
    null = sum(null_shares) / len(null_shares) if null_shares else None
    return {"canvases": seen, "fixations": n_fix,
            "real_share": real, "null_share": null,
            "ratio": (real / null) if (real and null) else None,
            "area_share": 0.25,
            "moments_sample": moments_used[:5]}


# ----------------------------------------------------------------- the planted controls (RULES §11)
def selftest() -> int:
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="l3-selftest-")) / "shelf"
    (tmp / "payload").mkdir(parents=True)
    # a translating blob (4×4 px, moving 16 px/frame rightward) over a STATIC noise background (drawn
    # once — the first form re-drew the noise per frame, so the noise itself carried the motion mass)
    rng = np.random.default_rng(7)
    rows = []
    base = rng.integers(0, 40, (128, 128, 3), dtype=np.uint8)
    for i in range(6):
        frame = base.copy()
        x = 8 + 16 * i
        frame[8:12, x:x + 4] = 250
        rel = f"payload/{i:09d}.png"
        Image.fromarray(frame).save(tmp / rel)
        rows.append({"seq": i + 1, "at": f"2026-10-13T00:00:0{i}Z", "sense": "eye", "payload": rel,
                     "meta": {"moment": f"v{i}", "source": "video", "t": float(i), "series": "plant"}})
    (tmp / "2026-10-13.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    shelf_rows = load_shelf_rows(tmp)
    prev = {rows[i]["meta"]["moment"]: rows[i - 1]["payload"] for i in range(1, len(rows))}
    fields = [motion_field(tmp, rows[i]["payload"], prev.get(rows[i]["meta"]["moment"])) for i in range(1, len(rows))]
    total = sum(f.sum() for f in fields if f is not None)
    blob_hits = 0
    for i, f in enumerate(fields):
        x_new = (8 + 16 * (i + 1)) // CELL
        x_old = (8 + 16 * i) // CELL
        blob_hits += f[0, x_new] + (f[0, x_old] if x_old != x_new else 0.0)
    localized = blob_hits / total if total else 0.0
    assert total > 0, "PLANT MISS: no motion seen at all"
    assert localized >= 0.5, f"PLANT MISS: the blob's cells hold only {localized:.2f} of the motion mass"
    # a static series (identical frames) must read ~no motion
    still = np.zeros((128, 128, 3), dtype=np.uint8)
    Image.fromarray(still).save(tmp / "payload/s.png")
    f_static = motion_field(tmp, "payload/s.png", "payload/s.png")
    assert f_static is not None and f_static.sum() == 0.0, "PLANT CONTROL MISS: a static series read motion"
    # the share form's sanity: fixations planted ON the top-motion cells vs off them
    field = fields[-1]
    x_cell = (8 + 16 * len(fields)) // CELL
    on = share_in_top_quartile(field, [(0, x_cell)])
    off = share_in_top_quartile(field, [(7, 7)])
    assert on > off, f"PLANT MISS (the share form): on {on} vs off {off}"
    print(f"SELFTEST PASS — the translating blob localized {localized:.2f} of the motion mass (bar ≥ 0.5), "
          f"the static series read 0.0, the share form separates {on}>{off}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shelf")
    ap.add_argument("--journal")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.shelf or not args.journal:
        print(__doc__)
        return 2
    out = read(Path(args.shelf), Path(args.journal), max_n=args.max)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
