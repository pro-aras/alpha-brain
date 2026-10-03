"""said_frames_counts.py — counts only: the train and held-out adjacent occurrences of the cells' eye-confirmed game frames on ALPHA4's plain split (why a frame's marginal credit reads negative on the held-out part).

# edit: Claude (Sonnet 5.5, swarm toys), written at the RESULT, 2026-10-04 00:23 +0400 (post-hoc reading, no mark).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.toys.frames import compress as CO
from tools.toys.frames import plants as PL
from tools.toys.frames import run as RN

a4 = RN.load_streams(Path(sys.argv[1]))["alpha4"]
train, held = PL.condition_parts(a4, "plain")
sc = CO.Scorer([m.words for m in train], [m.words for m in held])
print(f"train moments {len(train)}, held moments {len(held)}")
print(f"{'frame':<14}{'train adjacent':>16}{'held adjacent':>15}")
for f in (("green", "box"), ("grey", "ball"), ("blue", "ball"), ("red", "box"), ("purple", "ball"), ("yellow", "key"), ("blue", "key"), ("red", "key"), ("green", "key"), ("yellow", "ball"), ("yellow", "box"), ("grey", "box")):
    print(f"{' '.join(f):<14}{sc.train_adjacent(f):>16}{sc.held_adjacent(f):>15}")
# where the game moments sit: first and last seq index of two-word moments made of a colour and an object, as fractions of the stream
objs = {"box", "ball", "key"}
idx = [i for i, m in enumerate(a4) if len(m.words) == 2 and m.words[1] in objs]
print(f"two-word colour+object moments: {len(idx)}; first at moment {idx[0]} of {len(a4)}, last at {idx[-1]}; share in the train part (first {len(train)} moments): {sum(1 for i in idx if i < len(train)) / len(idx):.3f}")
