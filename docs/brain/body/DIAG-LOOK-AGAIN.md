# DIAG-LOOK-AGAIN — how many missed things one more look would reach (a reading on training scenes, before any design)

*Claude (Fable 5.1, the seat), 2026-09-29 14:59 +0400. A geometry reading: 2,000 TRAINING scenes of each world seed, rendered by the world's own code; the eye's fixations by `genome.gaze.fixations` (the pinned organ); a fixation's thing by `brain.scene.world.fixation_thing`. No test scene, no mind, no brain, nothing learned. The tools: `tools/brain/diag/lookagain_coverage.py`, `lookagain_blob.py`. The files: `/data/dev/brain-runs/day0929/lookagain/`.*

**Why.** DIAG-M2B (today) and VERDICT-BRAIN-IN-BODY put the brain's two open failures on the eye: about 1 meeting in 10 it never saw the named thing. The look-again act is dated 2026-09-30. This says what it can reach, and by which rule.

## 1 · More of the eye's own fixations reach little
The organ keeps its first four fixations when asked for more (checked on every scene: {'5': 2000, '6': 2000, '8': 2000} / {'5': 2000, '6': 2000, '8': 2000} / {'5': 2000, '6': 2000, '8': 2000} of 2,000).

| fixations | the named thing was seen | every thing was seen |
|---|---|---|
| 4 | 0.896 / 0.899 / 0.892 | 0.751 / 0.752 / 0.766 |
| 5 | 0.916 / 0.918 / 0.924 | 0.803 / 0.803 / 0.816 |
| 6 | 0.935 / 0.931 / 0.939 | 0.839 / 0.837 / 0.847 |
| 8 | 0.960 / 0.953 / 0.960 | 0.891 / 0.892 / 0.895 |

Of the scenes whose named thing four fixations missed (208 / 202 / 215), a fifth fixation reaches 0.197 / 0.188 / 0.298, and four more reach 0.611 / 0.530 / 0.623. The organ looks again where it already looked.

By the number of things in the scene, four fixations see the named thing: one thing 1.000 / 1.000 / 1.000 · two 0.862 / 0.871 / 0.857 · three 0.752 / 0.752 / 0.749.

## 2 · One TARGETED look reaches nearly all of them
**The rule read (R-BLOB), built from what the eye itself holds:** an ink cell is a cell of the eye's 16 × 16 grid whose pixels hold ink above a threshold (the eye's own rule, `ink_border`); a blob is a connected set of ink cells; a blob is seen when a fixation lies on it or touches it; **look again = one more fixation at the largest unseen blob**, at its cell nearest its centre. The rule reads no truth.

| ink threshold : smallest blob (cells) | the named thing seen: 4 fixations · + 1 look · + 2 looks | looks taken when every thing was ALREADY seen (a scene) | share of the new fixations on no thing |
|---|---|---|---|
| 0.1 : 1 | 0.896 / 0.899 / 0.892 · 0.990 / 0.988 / 0.992 · 0.999 / 0.999 / 0.999 | 2.123 / 2.144 / 2.164 | 0.876 / 0.879 / 0.887 (of 4487 / 4519 / 4515) |
| 0.1 : 3 | 0.896 / 0.899 / 0.892 · 0.990 / 0.988 / 0.992 · 0.999 / 0.999 / 0.999 | 1.257 / 1.230 / 1.264 | 0.815 / 0.811 / 0.825 (of 2925 / 2858 / 2869) |
| 0.1 : 4 | 0.896 / 0.899 / 0.892 · 0.990 / 0.988 / 0.992 · 0.999 / 0.999 / 0.999 | 0.376 / 0.383 / 0.369 | 0.567 / 0.572 / 0.585 (of 1243 / 1259 / 1211) |
| 0.1 : 6 | 0.896 / 0.899 / 0.892 · 0.979 / 0.979 / 0.984 · 0.986 / 0.986 / 0.988 | 0.062 / 0.050 / 0.054 | 0.202 / 0.180 / 0.182 (of 604 / 572 / 556) |
| 0.25 : 1 | 0.896 / 0.899 / 0.892 · 0.988 / 0.985 / 0.989 · 0.998 / 0.998 / 0.997 | 2.234 / 2.264 / 2.280 | 0.882 / 0.885 / 0.890 (of 4694 / 4739 / 4731) |
| 0.25 : 3 | 0.896 / 0.899 / 0.892 · 0.988 / 0.985 / 0.989 · 0.998 / 0.998 / 0.997 | 1.334 / 1.313 / 1.342 | 0.822 / 0.820 / 0.831 (of 3084 / 3022 / 3021) |
| 0.25 : 4 | 0.896 / 0.899 / 0.892 · 0.988 / 0.985 / 0.989 · 0.998 / 0.997 / 0.996 | 0.395 / 0.419 / 0.390 | 0.583 / 0.595 / 0.601 (of 1289 / 1321 / 1252) |
| 0.25 : 6 | 0.896 / 0.899 / 0.892 · 0.972 / 0.973 / 0.975 · 0.977 / 0.981 / 0.979 | 0.065 / 0.056 / 0.056 | 0.232 / 0.210 / 0.205 (of 560 / 543 / 523) |

1. **One targeted look takes «the named thing was seen» from 0.89–0.90 to 0.99**; two take it to 0.999. One more of the organ's own fixations takes it to 0.92.
2. **The price is wasted looks.** The canvas holds about 3.8 ink blobs for 1.8 things. With no smallest size the rule looks about twice at a scene whose things were all seen. At 4 cells it looks 0.37–0.42 times; at 6 cells 0.05–0.07 times, and the named thing is still seen 0.97–0.98 after one look.
3. **DIAG-M2B's dose table says what the reader needs:** a store about 0.98 right. Four fixations give 0.89–0.90 seen. So the smallest blob of 4 cells (0.99 after one look) reaches it on this reading, and 6 cells (0.97–0.98) sits at its edge.

## 3 · What this does not show
- **It is geometry.** It counts whether a fixation falls on the named thing. It does not show that the brain attributes the word to it, that the reader then refuses a never-taught shape, or that test 2b passes.
- **A new fixation on no thing becomes a hypothesis of nothing** in the brain's view. What that does to its learning is not measured here.
- **The rule changes the eye's road.** `genome/gaze.py` is pinned by the scene caches; a canvas would carry 5 or 6 glances, so the organism's clock, its caches and every gaze-bound ceiling move. The design must say which of them it touches and price each (#235, #245).
- **Training scenes of three world seeds.** The test sets were not read.
