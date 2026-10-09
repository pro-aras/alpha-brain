# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §2 B5 (the law SIGNED;
# SEAT-LINE sha256 1d00a35f…): the DECLARED TOY SHELF's maker — ~20 synthetic frames + a tiny SRT, NEVER the
# real shelf. The frames go through ffmpeg and the REAL converter (tools/worlds/video_door.py, UNCHANGED — V0's
# own mapping), then the promotion tool (tools/worlds/video_shelf.py) freezes the shelf with its manifest. The
# fixture's truths are known by construction: 22 frames, the 8-word motherese vocabulary below, the token count.
# usage: make_toy_shelf.py <out shelf dir>   (writes under the out dir; never into a life root)
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from creature.senses import video as V
from tools.worlds import video_door, video_shelf

CANVAS = 128
FPS = 1
N_FRAMES = 22

# the toy world's little song: a red square that moves, then a blue circle that appears and goes — the captions
# name it in a tiny repetitive vocabulary (the motherese form), 8 distinct words, letters-only by construction.
SRT = """\
1
00:00:01,000 --> 00:00:03,500
the red square moves

2
00:00:04,000 --> 00:00:06,500
the red square moves here

3
00:00:08,000 --> 00:00:10,500
the square is red

4
00:00:12,000 --> 00:00:14,500
a blue circle comes

5
00:00:15,000 --> 00:00:17,500
the circle is blue

6
00:00:18,000 --> 00:00:20,500
the red square and the blue circle
"""


def frame(k: int) -> np.ndarray:
    img = np.full((CANVAS, CANVAS, 3), 96, dtype=np.uint8)
    x = 8 + min(k, 11) * 6                                  # the red square moves for the first half
    img[44:76, x:x + 32] = (220, 40, 40)
    if 12 <= k < 20:                                        # the blue circle's visit
        yy, xx = np.mgrid[0:CANVAS, 0:CANVAS]
        img[(yy - 76) ** 2 + (xx - 96) ** 2 <= 15 ** 2] = (40, 60, 230)
    return img


def main() -> int:
    shelf = Path(sys.argv[1])
    if shelf.exists() and any(shelf.iterdir()):
        print(f"refusing: {shelf} is not empty", file=sys.stderr)
        return 2
    work = Path(tempfile.mkdtemp(prefix="toy-shelf-build-"))
    frames = work / "frames"
    frames.mkdir()
    for k in range(N_FRAMES):
        Image.fromarray(frame(k), mode="RGB").save(frames / f"f{k:03d}.png")
    video = work / "toy.mp4"
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", str(frames / "f%03d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(video)], capture_output=True)
    if p.returncode != 0:
        print(p.stderr.decode()[-600:], file=sys.stderr)
        return 1
    srt = work / "toy.srt"
    srt.write_text(SRT)
    tape = work / "tape"
    stats = video_door.convert(video, srt, tape, date="2026-10-08", track_kind="authored")
    vrc = video_door.verify(tape, video=video, captions=srt)
    assert vrc == 0, "the toy tape failed its own converter's verify"
    rec = video_shelf.promote(tape, shelf)
    rec["fixture"] = {"frames": N_FRAMES, "fps": FPS, "srt": SRT.strip(), "converter_stats": stats,
                      "vocabulary": sorted({w for line in SRT.split("\n") if line and not line[0].isdigit() and "-->" not in line
                                            for w in line.split()})}
    (shelf / "TOY-FIXTURE.json").write_text(json.dumps(rec["fixture"], indent=2, sort_keys=True) + "\n")
    # the fixture record rides the shelf; rewrite the manifest to carry it too, then re-verify
    V.write_manifest(shelf)
    V.verify_shelf(shelf)
    rec["manifest_sha256"] = __import__("hashlib").sha256((shelf / "MANIFEST.sha256").read_bytes()).hexdigest()
    print(json.dumps({k: v for k, v in rec.items() if k != "files"}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
