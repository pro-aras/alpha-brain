# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §2 B2 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…): the video sense's test fixture — a DECLARED TOY SHELF (~a handful of synthetic
# frames + a tiny caption stream, never the real shelf), in the organism's own tape form (V0's mapping, V3's
# concat metas), shared by tests/creature/test_sense_video.py and tests/tools/test_video_shelf.py.
"""tests/creature/_video_shelf.py — a toy video shelf for the tests of PREREG-ALPHA-6 §2 B2.

`build_toy_tape(dir)` writes a 6-canvas tape (V0's mapping mirrored: one eye row per frame, each canvas's
caption tokens as ear rows just before it, metas carried whole: source video/video-caption, series, video,
t/start/duration/track_kind, moment). `CANVASES` lists the expected groups so a test can assert order and
content exactly. The payloads are deterministic 128x128 PNGs (a square moving across a grey field)."""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image

CANVAS = 128
DAY = "2026-10-08"

# the declared toy stream: (the canvas's caption tokens [(word, start, duration)], ) — six frames, a tiny
# repetitive vocabulary (the motherese form), every truth known by construction.
TOKS = [
    [("red", 0.10, 0.40)],
    [],
    [("red", 2.10, 0.30), ("square", 2.45, 0.50)],
    [("square", 3.10, 0.40)],
    [],
    [("red", 5.10, 0.30)],
]


def _png_bytes(k: int) -> bytes:
    img = np.full((CANVAS, CANVAS, 3), 96, dtype=np.uint8)
    x = 8 + k * 16
    img[48:80, x:x + 32] = (220, 40, 40)       # the moving square
    buf = io.BytesIO()
    Image.fromarray(img, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _moment(t_ms: int) -> str:
    return f"v{DAY.replace('-', '')}t{t_ms:09d}"


def _iso(t: float) -> str:
    base = datetime.strptime(DAY, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return (base + timedelta(seconds=t)).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def rows_expected() -> List[Dict[str, object]]:
    """The toy tape's rows (minus seq/at/sha): [(sense, meta)] in tape order — V0's order law: a canvas's
    ear rows, then its eye row."""
    out: List[Dict[str, object]] = []
    for k, toks in enumerate(TOKS):
        for w, s, d in toks:
            out.append(("ear", {"moment": _moment(k * 1000), "word": w, "start": s, "duration": d,
                                "track_kind": "authored", "source": "video-caption",
                                "series": "toy-song", "video": "toy-song"}))
        out.append(("eye", {"moment": _moment(k * 1000), "source": "video", "t": float(k),
                            "series": "toy-song", "video": "toy-song"}))
    return out


def build_toy_tape(tape_dir: Path) -> Dict[str, object]:
    """The toy tape dir: <day>.jsonl + payload/ (+ payloads' bytes returned for the tests' own assertions)."""
    tape_dir = Path(tape_dir)
    payload = tape_dir / "payload"
    payload.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, object]] = []
    payloads: Dict[str, bytes] = {}
    seq = 0
    for sense, meta in rows_expected():
        seq += 1
        if sense == "eye":
            k = int(meta["t"])
            data = _png_bytes(k)
            rel, ext = f"payload/{seq:09d}.png", "png"
        else:
            data = str(meta["word"]).encode("utf-8")
            rel, ext = f"payload/{seq:09d}.txt", "txt"
        (payload / f"{seq:09d}.{ext}").write_bytes(data)
        rows.append({"seq": seq, "at": _iso(float(meta.get("t", meta.get("start", 0.0)))),
                     "sense": sense, "sha": hashlib.sha256(data).hexdigest(), "payload": rel, "meta": meta})
        payloads[rel] = data
    (tape_dir / f"{DAY}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return {"rows": rows, "payloads": payloads}
