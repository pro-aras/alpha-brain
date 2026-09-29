# VERDICT BRAIN-DRIVES, stage 1 — the brain takes its turn at every canvas: it expects, it speaks and it asks, by itself

*Claude (Fable 5.1, the seat, alone), 2026-09-29 19:27 +0400. The law: `PREREG-BRAIN-DRIVES.md` in this folder, signed on its final text (sha256 a5fdea1e…). The gate was read once. Every figure below is read from `/data/dev/brain-runs/day0929/drive/read/gate.json`.*

## The verdict
1. **Every mark passes. `DRIVE` becomes a line of the brain templates** (`BRAIN-LEAN`, `BRAIN-FULL`). The brain now acts by itself at every canvas it hears.
2. **What it says, unasked, is true.** On a world never drawn before the law was signed (seed 20261104), 0.972 of its 9,240 says are true of the thing it looked at, and 0.940 pick that thing out among the things in view. The same phrases dealt to other canvases are true 0.206 of the time at most.
3. **It speaks on 0.948 of the canvases** after its first calibration; its lowest window of 1,000 canvases reads 0.903.
4. **Its doubt informs.** Where it holds a word for a thing its forced names are right 0.918; where it holds none, 0.797. It asks on 0.112 of the canvases.
5. **Its surprise is real.** Against the parent's words it reads 0.145; with the utterances dealt to other canvases, 0.683 at least.
6. **Its learning and its exam answers did not move.** Three closed lives replayed with the line: every other row equal. The price: × 1.096 / 1.098 / 1.076 of the mind's CPU per training canvas.

## The marks
| Mark | What was read | The reading | Bar | Verdict |
|---|---|---|---|---|
| I1 | the line absent: each closed lean life replayed against its own journal (20261101 / 02 / 03) | exits 0 / 0 / 0; rows 34481 / 34477 / 34472; the identity plant's exit 1 | every row equal; the plant diverges | **PASS** |
| I2 | the line present: the journal without its turn rows against the journal without the line | turn rows 10000 / 10000 / 10000; other rows 34481 / 34477 / 34472; first difference None / None / None | every row equal | **PASS** |
| JB | each turn row of the body against the bench's turn for the same scene | equal 10000 / 10000 / 10000 of 10000 / 10000 / 10000; differing by key {} / {} / {} | every canvas equal | **PASS** |
| J | the bench with the production turn against stage −1's table | differing figures [] / [] / [] of 13 blocks | equal | **PASS** |
| S | TRUE, world 20261104 | 0.972 (n 9,240; not gradable 0); null's highest of 10 draws 0.206 | ≥ 0.95, above every draw | **PASS** |
| U | UNIQUE-TRUE | 0.940 (n 9,240) | ≥ 0.9 | **PASS** |
| R | the say rate, every window of 1,000 | lowest 0.903 (canvases 0–1,000, n 750); 10 windows | ≥ 0.85 | **PASS** |
| D | DOUBT INFORMS | 0.918 − 0.797 = 0.121 (names 41,367 and 3,396); exact p 1.1e-96 | ≥ 0.05, p < 0.001 | **PASS** |
| E | SURPRISE against the forced names | 0.145 (n 9,750); null's lowest of 10 draws 0.683 | ≤ 0.2, below every draw | **PASS** |
| C | CPU per training canvas, ON over OFF (ms) | 68.59 / 149.02 / 67.50 over 62.59 / 135.71 / 62.71 = × 1.096 / 1.098 / 1.076; canvases 10000 / 10000 / 10000 | ≤ 1.5 | **PASS** |

**The controls.** The planted say (every said word replaced by a false word of its kind): TRUE reads 0.000 over 9,240 says, so the grader can fail a mouth: True. The identity plant (`DELTA lr 0.05` → `0.06`): the replay's exit 1.

## Readings, never graded (world 20261104)
- **Its first true word:** canvas 251, «circle».
- **Its spoken vocabulary as it grows** (distinct words said truly, by canvas): 1,000: 13 · 2,000: 13 · 3,000: 13 · 4,000: 13 · 5,000: 13 · 6,000: 13 · 7,000: 13 · 8,000: 13 · 9,000: 13 · 10,000: 13.
- **The words it has said truly by the end:** big, blue, circle, cross, green, red, ring, small, square, star, triangle, white, yellow.
- **Its surprise falls** by -0.0080 ± 0.0015 a thousand canvases (10 windows).
- **Its surprise by window:** 0.202 · 0.179 · 0.154 · 0.133 · 0.153 · 0.148 · 0.134 · 0.117 · 0.130 · 0.114.
- **Its say rate by window:** 0.903 · 0.942 · 0.947 · 0.948 · 0.954 · 0.951 · 0.956 · 0.950 · 0.947 · 0.968.
- **How long it speaks:** {'1': 9212, '2': 27, '3': 1} (words in a say: count). It says the shortest phrase that picks the thing out.
- **What it speaks about:** the parent's own thing 0.655 of the time.
- Scenes of 1 thing: it speaks on 0.930; true 0.983; unique-true 0.983 (says 3,618).
- Scenes of 2 things: it speaks on 0.956; true 0.968; unique-true 0.935 (says 3,705).
- Scenes of 3 things: it speaks on 0.967; true 0.957; unique-true 0.867 (says 1,917).
- **The turn row:** 607 / 604 / 607 bytes a row; 6.1 / 6.0 / 6.1 MB a life of 10,000 canvases.
- **CPU per canvas, the last 1,000 canvases:** ON 92.97 / 204.26 / 91.70 ms, OFF 86.79 / 191.48 / 87.10 ms.

## The runs
```
2026-09-29 17:06:42 +0400 the gate starts at c68da99; PREREG sha256 a5fdea1e45e36e3f; load 19.22 19.74 18.67
17:56:06 bench-jb-20261103 exit 0; load 30.08 31.50 31.33
17:56:07 bench-jb-20261102 exit 0; load 30.08 31.50 31.33
17:56:07 bench-jb-20261101 exit 0; load 30.08 31.50 31.33
17:56:38 bench-g-20261104 exit 0; load 29.02 31.08 31.20
17:56:38 bench-j-20261101 exit 0; load 29.02 31.08 31.20
17:56:38 bench-j-20261103 exit 0; load 29.02 31.08 31.20
17:56:38 bench-j-20261102 exit 0; load 29.02 31.08 31.20
--- THE BOX STOPPED HARD at 18:59 (no shutdown record) and came back at 19:00. Complete before it: every bench run; the pair of 20261102 (off exit 0, on exit 0).
2026-09-29 19:11:49 +0400 the gate RESUMES at c68da99; load 0.11 0.11 0.06
19:26:48 on-20261103 done; load 3.93 4.71 3.28
19:26:58 on-20261101 done; load 3.55 4.60 3.26
19:26:58 plant-20261102 done; load 3.55 4.60 3.26
19:26:58 off-20261101 done; load 3.55 4.60 3.26
19:26:58 off-20261103 done; load 3.55 4.60 3.26
off-20261101 replay exit 0 · on-20261101 replay exit 0
off-20261102 replay exit 0 · on-20261102 replay exit 0
off-20261103 replay exit 0 · on-20261103 replay exit 0
plant-20261102 replay exit 1 (it must not be 0)
2026-09-29 19:26:58 +0400 the runs are done (an ON replay failed: 0)
19:27:06 the reader exit 0
```

## What this does and does not show
- **Shown:** put in the body's loop, the brain acts by itself at every canvas. What it says is true, its doubt informs, its surprise is real, and nothing it learned or answered moved.
- **Not shown:** that it learns by itself. It still learns only when the parent speaks.
- **Not shown:** that the two minds talk. No other organ reads a say or an ask yet, and the world does not answer the ask. That is stage 2.
- **Not shown:** sentences. It says the one word that picks the thing out, and two when one is not enough.
- The never-used world is drawn by the same generator as the three old ones. It guards the bars against three draws, not against a new kind of world.
- JB's bench side read each life's own BRAIN line (`young 3`); runs G and J read the template's (`young 3 nearest`). The turn says mature words only, so it is the same turn under both.
