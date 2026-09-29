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

## 3 · What one look does to the BRAIN (training rows; the bench, no production code)
*(the seat, 2026-09-29 15:23 +0400. Tool: `tools/brain/diag/probe_lookagain.py`. The brain is the organ under the template's BRAIN line. It learns the first 8,000 training scenes with each arm's glances; the other 2,000 are validation rows. A new glance is the eye's own `forced_glance` at the chosen cell. THE CONTROL: at a cell the eye did fixate, the forced glance equals the cached glance on 200 / 200 / 200 of the same, largest difference 0.0. The readers and the proxy are DIAG-M2B's.)*

| arm | looks a scene | the named thing seen | things in the brain's view | attribution right, every meeting | right where «none» did not fire · and responsibility ≥ 0.9 |
|---|---|---|---|---|---|
| the law (4 fixations) | 0.00 / 0.00 / 0.00 | 0.893 / 0.891 / 0.895 | 1.53 / 1.52 / 1.54 | 0.844 / 0.839 / 0.845 | 0.901 / 0.900 / 0.901 · 0.961 / 0.958 / 0.959 |
| one look, blobs ≥ 4 cells | 0.50 / 0.50 / 0.50 | 0.990 / 0.989 / 0.992 | 2.03 / 2.03 / 2.04 | 0.923 / 0.924 / 0.926 | 0.931 / 0.932 / 0.934 · 0.997 / 0.996 / 0.997 |
| two looks, blobs ≥ 4 cells | 0.61 / 0.61 / 0.59 | 0.999 / 0.999 / 0.999 | 2.13 / 2.13 / 2.14 | 0.927 / 0.929 / 0.929 | 0.931 / 0.934 / 0.935 · 0.999 / 0.999 / 1.000 |
| one look, blobs ≥ 6 cells | 0.27 / 0.27 / 0.26 | 0.982 / 0.982 / 0.984 | 1.79 / 1.79 / 1.80 | 0.917 / 0.917 / 0.923 | 0.931 / 0.931 / 0.936 · 0.996 / 0.994 / 0.995 |

**The reader, rebuilt from each store** (the proxy: a taught shape taken out of the reader; a thing of that shape is CORRECT when no shape word holds it; validation rows, one-thing scenes):

| arm | the reader's store | never-taught shape refused | a taught shape held by its own name | its size word · its colour word held |
|---|---|---|---|---|
| the law (4 fixations) | every meeting, by responsibility (the law's reader) | 0.280 / 0.251 / 0.266 | 0.912 / 0.912 / 0.917 | 0.893 / 0.897 / 0.896 · 0.892 / 0.904 / 0.902 |
| the law (4 fixations) | meetings where «none» did not fire, the attributed thing | 0.337 / 0.335 / 0.359 | 0.908 / 0.909 / 0.916 | 0.889 / 0.892 / 0.885 · 0.888 / 0.887 / 0.889 |
| the law (4 fixations) | the same, responsibility ≥ 0.9 | 0.399 / 0.425 / 0.429 | 0.899 / 0.896 / 0.909 | 0.863 / 0.883 / 0.880 · 0.870 / 0.870 / 0.875 |
| the law (4 fixations) | THE TRUE referent (a reading) | 0.766 / 0.838 / 0.802 | 0.912 / 0.921 / 0.921 | 0.908 / 0.909 / 0.907 · 0.899 / 0.909 / 0.909 |
| one look, blobs ≥ 4 cells | every meeting, by responsibility (the law's reader) | 0.217 / 0.213 / 0.265 | 0.953 / 0.940 / 0.948 | 0.945 / 0.938 / 0.935 · 0.936 / 0.949 / 0.956 |
| one look, blobs ≥ 4 cells | meetings where «none» did not fire, the attributed thing | 0.724 / 0.781 / 0.774 | 0.914 / 0.908 / 0.920 | 0.918 / 0.906 / 0.914 · 0.901 / 0.908 / 0.919 |
| one look, blobs ≥ 4 cells | the same, responsibility ≥ 0.9 | 0.769 / 0.835 / 0.824 | 0.906 / 0.896 / 0.902 | 0.862 / 0.871 / 0.875 · 0.878 / 0.892 / 0.896 |
| one look, blobs ≥ 4 cells | THE TRUE referent (a reading) | 0.732 / 0.784 / 0.767 | 0.931 / 0.919 / 0.932 | 0.930 / 0.926 / 0.927 · 0.914 / 0.932 / 0.931 |
| two looks, blobs ≥ 4 cells | every meeting, by responsibility (the law's reader) | 0.238 / 0.222 / 0.256 | 0.953 / 0.943 / 0.948 | 0.944 / 0.936 / 0.935 · 0.938 / 0.945 / 0.955 |
| two looks, blobs ≥ 4 cells | meetings where «none» did not fire, the attributed thing | 0.726 / 0.782 / 0.769 | 0.914 / 0.909 / 0.920 | 0.914 / 0.905 / 0.916 · 0.901 / 0.914 / 0.926 |
| two looks, blobs ≥ 4 cells | the same, responsibility ≥ 0.9 | 0.770 / 0.829 / 0.816 | 0.905 / 0.896 / 0.909 | 0.861 / 0.869 / 0.874 · 0.882 / 0.888 / 0.894 |
| two looks, blobs ≥ 4 cells | THE TRUE referent (a reading) | 0.727 / 0.765 / 0.764 | 0.931 / 0.921 / 0.932 | 0.928 / 0.929 / 0.931 · 0.918 / 0.931 / 0.931 |
| one look, blobs ≥ 6 cells | every meeting, by responsibility (the law's reader) | 0.273 / 0.266 / 0.335 | 0.945 / 0.934 / 0.939 | 0.928 / 0.921 / 0.925 · 0.923 / 0.931 / 0.935 |
| one look, blobs ≥ 6 cells | meetings where «none» did not fire, the attributed thing | 0.756 / 0.806 / 0.805 | 0.914 / 0.905 / 0.920 | 0.910 / 0.897 / 0.910 · 0.901 / 0.894 / 0.909 |
| one look, blobs ≥ 6 cells | the same, responsibility ≥ 0.9 | 0.797 / 0.870 / 0.838 | 0.910 / 0.897 / 0.905 | 0.862 / 0.869 / 0.887 · 0.876 / 0.879 / 0.891 |
| one look, blobs ≥ 6 cells | THE TRUE referent (a reading) | 0.759 / 0.821 / 0.804 | 0.930 / 0.919 / 0.931 | 0.926 / 0.927 / 0.927 · 0.918 / 0.932 / 0.929 |

**The real test 2b items, on the test sets ALREADY READ** (a diagnostic; both sets were read before; never the gate; the brain learned all 10,000 scenes; n 48 a seed; the bar is 0.80):

| arm | the reader's store | fresh set (2026140x) | older set (2026120x) | house, fresh | tree, fresh |
|---|---|---|---|---|---|
| the law (4 fixations) | every meeting, by responsibility (the law's reader) | 0.646 / 0.708 / 0.729 | 0.688 / 0.583 / 0.625 | 0.00 / 0.12 / 0.00 | 0.00 / 0.12 / 0.38 |
| the law (4 fixations) | meetings where «none» did not fire, the attributed thing | 0.646 / 0.729 / 0.729 | 0.688 / 0.583 / 0.688 | 0.00 / 0.12 / 0.00 | 0.00 / 0.25 / 0.38 |
| the law (4 fixations) | the same, responsibility ≥ 0.9 | 0.667 / 0.750 / 0.729 | 0.688 / 0.625 / 0.688 | 0.00 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| the law (4 fixations) | THE TRUE referent (a reading) | 0.896 / 0.875 / 0.833 | 0.896 / 0.812 / 0.896 | 0.88 / 0.88 / 0.62 | 0.50 / 0.38 / 0.38 |
| one look, blobs ≥ 4 cells | every meeting, by responsibility (the law's reader) | 0.417 / 0.542 / 0.500 | 0.458 / 0.417 / 0.375 | 0.00 / 0.12 / 0.00 | 0.00 / 0.12 / 0.38 |
| one look, blobs ≥ 4 cells | meetings where «none» did not fire, the attributed thing | 0.812 / 0.833 / 0.812 | 0.854 / 0.771 / 0.854 | 0.75 / 0.62 / 0.50 | 0.25 / 0.38 / 0.38 |
| one look, blobs ≥ 4 cells | the same, responsibility ≥ 0.9 | 0.896 / 0.854 / 0.833 | 0.896 / 0.792 / 0.938 | 0.88 / 0.75 / 0.62 | 0.62 / 0.38 / 0.38 |
| one look, blobs ≥ 4 cells | THE TRUE referent (a reading) | 0.792 / 0.833 / 0.792 | 0.833 / 0.750 / 0.812 | 0.75 / 0.62 / 0.50 | 0.12 / 0.38 / 0.38 |
| one look, blobs ≥ 6 cells | every meeting, by responsibility (the law's reader) | 0.604 / 0.729 / 0.688 | 0.646 / 0.542 / 0.583 | 0.00 / 0.25 / 0.00 | 0.00 / 0.25 / 0.38 |
| one look, blobs ≥ 6 cells | meetings where «none» did not fire, the attributed thing | 0.875 / 0.896 / 0.833 | 0.896 / 0.812 / 0.896 | 0.88 / 0.88 / 0.62 | 0.50 / 0.50 / 0.38 |
| one look, blobs ≥ 6 cells | the same, responsibility ≥ 0.9 | 0.958 / 0.917 / 0.854 | 0.917 / 0.812 / 0.938 | 0.88 / 1.00 / 0.75 | 0.88 / 0.50 / 0.38 |
| one look, blobs ≥ 6 cells | THE TRUE referent (a reading) | 0.854 / 0.875 / 0.833 | 0.875 / 0.792 / 0.854 | 0.88 / 0.88 / 0.62 | 0.38 / 0.38 / 0.38 |

1. **One look makes the brain's own store right.** Attribution over every meeting rises from 0.84 to 0.92; where «none» did not fire and the responsibility is ≥ 0.9 it rises from 0.96 to 0.995–0.997. DIAG-M2B's ceiling of 0.96 was the eye's.
2. **The look alone does not repair the reader.** The law's reader, fed the better view, still refuses a never-taught shape 0.21–0.34 of the time on the proxy and reads 0.42–0.73 on the real items. It weighs every thing in view by responsibility, and more things are in view.
3. **The look AND the reader from the meetings where «none» did not fire, together, reach the exact-attribution reader.** On the proxy 0.72–0.81 (the true-referent reader: 0.73–0.82 under the same arms). On the real items of the sets already read, with one look at blobs of ≥ 6 cells: 0.875 / 0.896 / 0.833 and 0.896 / 0.812 / 0.896, against the law's 0.646 / 0.708 / 0.729 and 0.688 / 0.583 / 0.625. Houses are refused where they were named.
4. **So F-M2B was closed too early in one sense and rightly in another:** alone it is not a fix (DIAG-M2B stands); beside the look it is the other half of one.
5. **The arm the training rows choose,** by the rule «the highest worst-seed refusal on the proxy among the arms whose hold, size and colour rates fall by no more than 0.02 at any seed»: **one look at blobs of ≥ 6 cells, the reader from the meetings where «none» did not fire.** It also wastes the fewest looks (0.27 a scene; 0.05–0.07 where every thing was already seen).

**The reader's change has two halves, and both carry** *(the seat, 2026-09-29 15:26 +0400; one look at blobs of ≥ 6 cells; the proxy; `/data/dev/brain-runs/day0929/lookagain/halves/`)*:

| the reader's store | never-taught shape refused | a taught shape held by its own name |
|---|---|---|
| every meeting, every thing in view weighed by responsibility (the law's reader) | 0.273 / 0.266 / 0.335 | 0.945 / 0.934 / 0.939 |
| every meeting, the attributed thing alone | 0.616 / 0.655 / 0.693 | 0.931 / 0.931 / 0.929 |
| the meetings where «none» did not fire, weighed by responsibility | 0.406 / 0.408 / 0.430 | 0.934 / 0.921 / 0.931 |
| **the meetings where «none» did not fire, the attributed thing alone** | **0.756 / 0.806 / 0.805** | 0.914 / 0.905 / 0.920 |
| THE TRUE referent (a reading) | 0.759 / 0.821 / 0.804 | 0.930 / 0.919 / 0.931 |

So a control for the fix's gate is at hand: the same reader with the «none» flags ignored must read lower.

## 4 · What this does not show
- **§1 and §2 are geometry.** §3 is the bench on training rows and on test sets already read. None of it is a gate: the fix is graded on a test set never used, after its law is signed.
- **§3 reads test 2b only.** What the look does to tests 1, 2a, 3 and 6, and to the mouth, is not read here.
- **A new fixation on no thing becomes a hypothesis of nothing** in the brain's view. What that does to its learning is not measured here.
- **The rule changes the eye's road.** `genome/gaze.py` is pinned by the scene caches; a canvas would carry 5 or 6 glances, so the organism's clock, its caches and every gaze-bound ceiling move. The design must say which of them it touches and price each (#235, #245).
- **Training scenes of three world seeds.** The test sets were not read.
