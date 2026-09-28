# edit: Claude (Fable 5.1, the seat), 2026-09-28 — the redrawn glance caches against the scored run's, array by array.
import hashlib, json, sys
from pathlib import Path
import numpy as np
A = Path("/data/dev/brain-runs/scene-s1b1r"); B = Path("/data/dev/brain-runs/organ/scene")
SEEDS = (20261101, 20261102, 20261103)
S1 = ("train", "test", "m2b", "m6", "m3", "speak", "decline"); FR = ("test", "m2b", "m6", "m3", "speak", "decline", "speak2")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arrays(p):
    z = np.load(p)
    return {k: z[k] for k in z.files}
def compare(da, db, plant=False):
    diffs = []
    for name in ("glances.npy", "hear.jsonl", "truth.jsonl", "index.jsonl"):
        a = (da / name).read_bytes(); b = (db / name).read_bytes()
        if plant and name == "glances.npy":
            b = bytearray(b); b[len(b) // 2] ^= 1; b = bytes(b)
        if hashlib.sha256(a).hexdigest() != hashlib.sha256(b).hexdigest():
            diffs.append(name)
    for name in ("percept.npz", "forced.npz"):
        xa, xb = arrays(da / name), arrays(db / name)
        if set(xa) != set(xb):
            diffs.append(name + ":keys"); continue
        for k in xa:
            if xa[k].shape != xb[k].shape or xa[k].dtype != xb[k].dtype or xa[k].tobytes() != xb[k].tobytes():
                diffs.append(f"{name}:{k}")
    return diffs
n = bad = 0
for ws in SEEDS:
    for rel, splits in (("cache", S1), ("fresh/cache", FR)):
        for s in splits:
            da, db = A / str(ws) / rel / s, B / str(ws) / rel / s
            d = compare(da, db); n += 1
            rows = len(np.load(db / "glances.npy", mmap_mode="r"))
            if d:
                bad += 1; print(f"DIFF {ws}/{rel}/{s}: {d}")
            else:
                print(f"equal {ws}/{rel}/{s}  rows {rows}")
print(f"caches compared {n} · differing {bad}")
d = compare(A / "20261102/cache/train", B / "20261102/cache/train", plant=True)
print("CONTROL (one bit flipped in the redrawn glances.npy, in memory):", "CAUGHT " + str(d) if d else "MISSED")
sys.exit(1 if bad or not d else 0)
