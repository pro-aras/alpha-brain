# CALIBRATION COST — what one `Brain.calibrate()` costs at 20,000 … 100,000 scenes, MEASURED

*Written by Claude (Sonnet 5.5, swarm hears), 2026-10-03 11:25 +0400, on the seat's word («price one calibration at 100k scenes from a measurement, not from the 20k figure», PREREG-HEARS-2 AMENDMENT 1 §A1.8 (2)). A separate file, so that the co-signed law's sha256 stays the one the architect signed. Tool: `tools/brain/calibration_cost.py`; raw numbers: `docs/organism/hears/calibration-cost-2026-10-03.json`.*

## The figure the law carries is not reproduced
`PREREG-DAYS-LIFE.md` line 113 and `PREREG-HEARS-2.md` §5.4 say «a calibration at 20,000 scenes paused learning 0.3 s» (on `brain-long-1`) and price 300,000 at «a few seconds». **Measured here: 6.2 s of CPU at 20,000 scenes** (scene-shaped scenes; 4.1 s with the maker's structure). That is 14–20× the figure. What `0.3 s` measured I could not recover (it names a pause, not the call); the direct measurement of the call is below.

## Method
The brain is a real one: the scene hand's 10,000 learned scenes, 14 words, 6 calibrations, the snapshot a full-life replay wrote at the end of the scene world (`state/brain.{json,npz}`, version 2). It is loaded with the life's own BRAIN line (`young 3`; `eps 0.3`; `conformal 0.90`), `Brain.calibrate()` is timed at its own size, then the brain is GROWN by cycling its own real scenes through the learner's own `train_scene` (the per-word stores grow as in a life; `seen` references the same arrays, so memory below is an under-count) and `calibrate()` is timed again, twice at each size (the second reading is the one used). Two structures bracket the days life: **all_scene** (every real scene: two or three things, two or three words — an upper bound for a brain fed by the maker) and **maker_like** (only the real one-thing scenes, each with ONE shape word — the maker's structure). CPU seconds (`time.process_time`) on a box under load ≈ 6; wall equals CPU to 0.1 s at every row.

## Result (CPU seconds of ONE calibration; `calibration-cost-2026-10-03.json`)
| scenes learned | all_scene | maker_like | peak RSS of the measuring process |
|---|---|---|---|
| 10,000 | 3.06 | 3.10 | 281 MB |
| 20,000 | 6.23 | 4.07 | 334 MB |
| 50,000 | 15.31 | 7.43 | 618 MB |
| **100,000** | **30.12** | **12.19** | 1,096 MB |

Linear in the scenes learned. Through the 50k and 100k points: **all_scene c(N) = 0.49 s + 0.296 ms × N**; **maker_like c(N) = 2.68 s + 0.095 ms × N**. The days life's brain past 50,000 holds 50,000 scene-shaped scenes and the maker's, so one calibration costs between the two columns: **12–30 s at 100,000; 22–60 s at 200,000; 31–89 s at 300,000** (the models extrapolated, the 100,000 row measured). The growth itself costs 0.12–0.15 ms of CPU per scene, so learning is not the cost; the calibration is.

## What it means for the seat's list (every 1,000 learned 51000–200000, then every 5,000 to 300000: 170 points)
- The 170 calibrations cost **0.76 h (maker_like) to 1.99 h (all_scene) of CPU in total**, spread over **28.9 days** of the maker's feed past 50,000 (8,640 canvases a day): 0.1–0.3 % of the time.
- Each one PAUSES the mind (it runs inside `Brain.learn`): at the 1,000-learned spacing, every 2.8 h, a stall of 12–60 s from 100,000 to 200,000, then every 13.9 h a stall of 60–90 s to 300,000. The maker publishes every 10 s, so a 60 s stall queues about six canvases; nothing is dropped (the tape is the senses' own record), and the health watch's stuck-mind rule is an hour. Nothing here is a defect; the law's «a few seconds» was wrong by a factor 10–30, and the seat chose the spacing on it.
- The arithmetic of the alternative, for the seat only: spacing 2,000 past 100,000 would halve the total from there; the choice (1,000) stands as the seat made it.

## What this measurement is not
- An isolated calibration, not the days life's: memory in the life is larger than in the measuring process (`seen` here shares arrays), and the life's calibrations run beside other threads.
- Two structures bracket the life's brain; the exact mix (50,000 scene-shaped scenes + the maker's) was not built. The `all_scene` column is the safe reading.
- The in-situ confirmation (the spike a calibration leaves in a replay's own `timings.jsonl`, e.g. 3 s at the 10,000th scene) is read from the HEARS-2 bench arms when they land, and recorded below.

## In-situ check (to be filled from the bench arms' timings)
*(pending)*
