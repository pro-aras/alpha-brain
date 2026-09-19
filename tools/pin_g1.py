"""pin_g1.py — G1 §1/§5 pins, run BEFORE the toy (edit: Claude (Fable 5.1), 2026-09-19 17:22 +0400).
(1) G0b's development life replays to its recorded hash with GAZE off (the machinery change moved nothing);
(2) recall_many/edge_many equal recall/edge result for result over G0b's 380 held-out pictures (K=1 reduction);
(3) a canvas written as PPM P6 and read back by the organ's own reader is the same frame dict; the surprise gaze's
    first fixation on a clean canvas lands on the thing (a planted wrong pin must be caught);
(4) save/load round-trips the organism to the same state_hash."""
import json, os, sys, tempfile
from pathlib import Path
import numpy as np
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from genome import world, gaze
from genome.machinery import parse_genome, Organism, retina, GenomeError
from genome.run_g0 import make_streams, PER_THING, HELD_N, ARR2_PER_THING

g = parse_genome(Path("genome/G0b.genome").read_text())
assert g.gaze is None, "G0b must parse with GAZE off"
R = json.load(open("runs/g0b-20260919-165207/results.json"))
things = list(world.THINGS_11); arr2 = list(world.THINGS_ARRIVAL2)
dev, held, a2, plant, shuf, n_checked = make_streams(things, PER_THING, HELD_N, arr2, ARR2_PER_THING, world.THING_PLANT, world.THING_NULL, world.THING_NEVER, side=32, plant_showings=int(R.get("plant_showings", 5)))
org = Organism(g); org.new_arrival()
for t, p in dev:
    org.moment(retina(p, g.retina), world.encode_word(t, g.ear_blank_zero))
h = org.state_hash()
print(f"(1) development hash {h[:16]} vs recorded {R['design']['hash_600'][:16]}:", "SAME" if h == R["design"]["hash_600"] else "DIFFERENT")
assert h == R["design"]["hash_600"]
# (2) K=1 reduction over the 380 held-out pictures, both sides, and the edge road
n = 0; ne = 0
for t, pics in held.items():
    for p in pics:
        x = retina(p, g.retina)
        a, b = org.recall("sight", x), org.recall_many("sight", [x])
        assert a == b, (t, a, b); n += 1
        for wc in range(min(org.words.n, 6)):
            assert org.edge("sight", x, wc) == org.edge_many("sight", [x], wc); ne += 1
for t in things + arr2 + [world.THING_NEVER]:
    xw = world.encode_word(t, g.ear_blank_zero)
    assert org.recall("words", xw) == org.recall_many("words", [xw]); n += 1
print(f"(2) recall == recall_many on {n} questions; edge == edge_many on {ne} pairs: SAME")
# (3) the frame road + the first fixation
rng = np.random.default_rng(7)
rgb, truth = world.render_canvas("cross", rng)
gz, rt = gaze.organs()
with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
    f.write(gaze.ppm_bytes(rgb)); ppm = f.name
fr = rt.read_ppm(ppm); os.unlink(ppm)
assert fr == gaze.frame_of(rgb), "PPM round-trip differs"
fix = gaze.fixations(rgb, 4, "surprise")
cell = truth["cell"]; d0 = max(abs(fix[0][0] - cell[0]), abs(fix[0][1] - cell[1]))
print(f"(3) PPM round-trip SAME; first fixation {fix[0]} vs the thing's cell {cell} (distance {d0}); fixations {fix}")
assert d0 <= 1, "the first fixation did not land on the thing"
# planted wrong pin must be caught
gaze._ORGANS = None; old = gaze.PINS["organs/gaze.py"]; gaze.PINS["organs/gaze.py"] = "0" * 64
try:
    gaze.organs(); raise SystemExit("planted wrong pin NOT caught")
except GenomeError:
    print("(3b) planted wrong sha pin: CAUGHT")
gaze.PINS["organs/gaze.py"] = old; gaze._ORGANS = None
# (4) save / load
with tempfile.TemporaryDirectory() as d:
    org.save(Path(d) / "organism.npz")
    o2 = Organism.load(Path(d) / "organism", g)
print(f"(4) save/load state_hash {o2.state_hash()[:16]}:", "SAME" if o2.state_hash() == h else "DIFFERENT")
assert o2.state_hash() == h
print("PIN_G1_OK")
