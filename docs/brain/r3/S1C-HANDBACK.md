# S1c «THE NOISY ROOM» — the builder's hand-back

*edit: Claude (Opus 5.5, S1c builder), 2026-09-28 15:24 +0400.* This is written to `PREREG-S1C.md` (genome-wt-brain3 9ef2583, sha a552515a…) and its AMENDMENT 1 (1eba85d, sha 825f4ad8…; the seat signed it, Fable's co-signature is pending). Branch `scene-s1c` from `scene-s1b1` 7706371, run root `/data/dev/brain-runs/scene-s1c/`. Both shas were checked before the gate and are checked inside every run command.

## 0 · The verdict: THE FIRST GATE STOPPED at step 2 — K is not flat
- **K (i) MISS:** K's mean own block-drop after block 20 is **6.084** (3 visits in blocks 21–60). The bound is 0.05 × L_K's level = **0.274**. The miss holds under every reading of «level»: the bound is 0.190 for L_K at block 60 and 0.581 for the largest L_K in 21–60.
- **K (ii) passes:** L_K(60) 3.801 ≤ min L_R(60) 4.623.
- **N passes:** |mean drop| 0.137 ≤ 0.404.
- **R1–R3 pass:** 1.257 ≥ 3 × 0.137 = 0.410. The other reading of «3 × that» (≥ 3 × 0.05 × L_N's level = 1.211) passes too.
- **U would be DROPPED:** its last-20 mean 6.588 < 2 × the learnable rooms' 5.882 = 11.765.
- **What did not run:** steps 3–5, none of the 18 lives and no unit. The step is a STOP by the law («each step stops the run on a miss»), so nothing was worked around.

## 1 · What the miss is (a reading, `tools/scene/diag/s1c_gate_k.py`; its output is `/data/dev/brain-runs/scene-s1c/gate/diag_k.out`, copied as `tools/scene/diag/s1c_gate_k.out`)
- **The control:** the script re-ran the step-2 life by the gate's own call and reproduced its claims exactly. Its per-word terms sum to the table's L_K to 2e-16.
- **K is RE-LEARNED, not known** [the numbers Certain as printed; the reading Likely]:
  - Between K's 8 visits, the other rooms' blocks RAISE L_K by +2.67, 0.00, +9.15, +1.88, +7.10, +6.45, +3.16 and +2.20.
  - Each K visit drops it back by 0.25–7.63 (after block 20: 7.61, 6.99, 3.66).
- **The K column of the interference** (the mean ΔL_K per block in each room): R1 +1.31 (11 blocks) · U +0.88 (15) · N +0.46 (16) · R2 −0.36 (4) · R3 −0.66 (6).
- **The rise is spread over the words NOT said of K.** After block 51, L_K is 5.25: blue 0.68 · big 0.67 · cross 0.55 · white 0.52 · yellow 0.50 · ring 0.50 · … Right after K's own block 52, every term is ≤ 0.17 (L_K 1.60).
- **What it would mean for the run** [Likely, not measured]: K's own drops (mean 6.08) are the LARGEST progress readings in this world (R1–R3's mean is 1.26). A picker that follows PROGRESS would therefore be drawn to the «known» room, because interference re-opens K after every other room's block.

## 2 · THE FIRST GATE as printed (`/data/dev/brain-runs/scene-s1c/gate/first_gate.out`; the record is `first_gate.json`)
```
THE FIRST GATE (S1c, seed 20261301) — PREREG-S1C a552515af334… · AMENDMENT 1 825f4ad8086f… · PREREG-S1B1 caace482d890… · code 72c97632deb483cf0ff6d0b4f45c816d19c5e888
1. the room pools read: R1 2000+40 · R2 2000+40 · R3 2000+40 · N 2000+40 · K 2000+1 · U 2000+40 (H = 0 windows: 0) · the fixed test set: NAME 472, M1 1193 (graded 2–3 721) · per-word n 57–238 · no room canvas is a test canvas (1200 checked) · the truth fence's sweep (rooms.py + pickers.py): Ran 3, OK
2. RANDOM over 60 blocks, blocks 21–60 (visits N 11, K 3, R1–R3 16):
   N: |mean drop| 0.1368 ≤ 0.05 × level 8.076 = 0.4038 → PASS
   R1–R3: mean drop 1.2573 ≥ 3 × |N's| = 0.4105 → PASS (the other reading, ≥ 3 × 0.05 × L_N's level = 1.2113: PASS)
   K: (i) mean drop 6.0845 ≤ 0.05 × level 5.483 = 0.2741 → MISS · (ii) L_K(60) 3.801 ≤ min L_R(60) 4.623 → PASS
   U: last-20 mean 6.588 ≥ 2 × R1–R3's 5.882 = 11.765 → U DROPPED (its bars with it)
   the room-by-block table of L_k (every 10th boundary): b0: R1 13.41 R2 12.88 R3 12.50 N 11.91 K 9.01 U 14.17 | b10: R1 14.24 R2 9.60 R3 9.31 N 11.33 K 4.21 U 13.25 | b20: R1 8.59 R2 8.19 R3 8.32 N 9.31 K 9.30 U 9.21 | b30: R1 5.71 R2 8.10 R3 9.36 N 8.17 K 6.84 U 8.08 | b40: R1 5.15 R2 6.53 R3 9.36 N 8.11 K 3.76 U 7.78 | b50: R1 5.66 R2 6.55 R3 5.76 N 7.61 K 4.92 U 6.75 | b60: R1 4.62 R2 6.38 R3 5.47 N 7.51 K 3.80 U 6.22
   STOP at step 2
```

## 3 · Prices (against the declared ≤ 15 CPU-min, which AMENDMENT 1 §1 replaces by the price's own figure)
- **Seed 20261301's pools:** 12,201 canvases in **88.3 CPU-s**, 7.2 ms per canvas. That was the only heavy process on the box.
- **The gate to its stop:** 2 s.
- **Per block, from a probe on seed 20261301** (a reading, not a solo life): training 3.4 ms · the six window losses 3.8 ms · WORDS-LEARNED 1.5 ms · M1 21 ms · a clone 2.3 ms.
- **Projected** [Likely]:
  - a non-ORACLE life ≈ 2 CPU-s; an ORACLE life ≈ 40 CPU-s;
  - the unit ≈ 3 CPU-min for two seeds' pools + ≈ 2.5 for 18 lives + ≈ 2 for 60 band lives = ≈ 7–8 CPU-min.
- **Not priced:** no whole life was priced solo, because the gate stopped before the price.

## 4 · RAISED
1. **Pool exhaustion:** 1,000 visit scenes could run out → ruled by AMENDMENT 1 §1 (2,000 per room). Built.
2. **K's canvases:** re-rendered per visit vs «one scene» → ruled by AMENDMENT 1 §2. Built.
3. **The null's VOID clause** sat above its ceiling → ruled by AMENDMENT 1 §3 (PROGRESS's bars VOID iff the NULL meets them at ≥ 2 seeds; the RANDOM band a reading; the pin). Built, but not run.
4. **Facts, built as written:** K's star-red is one of S1's held-out pairs; R2 has no yellow.
5. **The builder's declared readings:** adopted as AMENDMENT 1 §4.
6. **NEW, at this stop: K's clause (i) meets a property of the world, not a fault of the instrument.** The rooms share one learner, and the other rooms unlearn K between its visits.
   - This is the seat's to rule. The builder only lists the shapes of a ruling:
     - «known» read right after a K visit rather than as flatness;
     - a K the other rooms never unlearn;
     - K dropped like U.
   - U's drop needs no ruling: the law drops it.

## 5 · What was built (branch `scene-s1c`)
- **c9be24a**
  - `brain/scene/rooms.py` (WORLD side): the six rooms and their pools, 2,000 visit scenes per room. A pool never wraps; K is re-rendered per visit. The room caches go through S1a's road, without forced windows (declared: no S1c arm reads them; they would cost +28 %). rooms.py's sha sits under its own header key, and a planted foreign sha is refused.
  - `brain/scene/pickers.py` (LEARNER side):
    - the loss: frozen, over the fixed 13 words, an unheard word at σ(0) = 0.5, the clip on the scene-level P;
    - the ε stream `explore:<block>`;
    - π from `null:seed` with its pin;
    - the six pickers, with the ORACLE by callback.
  - The truth fence covers both files, with planted offenders caught.
- **72c9763**
  - `brain/scene/run_s1c.py`: the life, the record, the marks, the gate's five steps, the price and the report.
    - The fixed test set is S1's three test seeds pooled from S1b-1's caches: NAME 472, M1 1,193.
    - The batched WORDS-LEARNED and M1 readers equal name_forced, answer_point and S1a's grader item by item. They are pinned by tests on real states and again at the end of every life.
    - The ORACLE's chosen clone is asserted equal to the learner after the same block.
  - `tools/scene/run_s1c.sh`: the unit (two waves of 9 + the band). It was **not launched**.
  - `tools/scene/pin_code.sh`: pins now carry the scene tests (the gate runs the fence from the pin).
- **f0b04c3:** the gate's output and the K diagnosis.
- **Test-first:** the 46 new tests are red on the parent 7706371 (`FAILED (errors=5)`: the three modules are missing, and the fence's two tests error on the missing files; log `/data/dev/brain-runs/scene-s1c/logs/redcheck-7706371.log`) and green from 72c9763.

## 6 · The suites on the final code
They were run on **f0b04c3**, the last commit that touches anything but this file. Each line below is read from its log, and each log has 0 `ERROR:` / `FAIL:` blocks.
- **The whole brain suite under the venv:** `Ran 566 tests in 271.965s` / `OK (skipped=3)`; log `/data/dev/brain-runs/scene-s1c/logs/suite-venv-f0b04c3.log`. That is S1b-1's 520 plus S1c's 46.
- **The scene package under /usr/bin/python3:** `Ran 164 tests in 27.498s` / `OK`; log `/data/dev/brain-runs/scene-s1c/logs/suite-scene-sys-f0b04c3.log`.

## 7 · Declared readings (beyond AMENDMENT 1 §4)
- **The draws:**
  - ε's coin comes first, then the room, both from `explore:<block>`;
  - RANDOM draws from `<prefix>pick:<block>`, and the band uses the prefix `random-band:<seed>:<k>:`;
  - π is drawn by rejection of permutations with a fixed point;
  - the episodic generator is `episodic:room:<r>:visit:<i>`.
- **The rooms:**
  - N's utterance is drawn after the things, from the scene's own substream;
  - U's referent is S1's `_parent`'s first draw.
- **DRIFT:** a zero path reads 0.
- **Gate 2:**
  - a room's mean block-drop reads over its own visited blocks 21–60;
  - «level» is the mean over the boundaries after blocks 21–60;
  - both readings of «3 × that» are printed.
- **The verdict's order:** NOT GRADABLE → VOID → PASS / FAIL.
- **A caveat to read later:** with gains in whole words, «within 1 word» ties most blocks, so the ORACLE is mostly an M1-gain picker. This is to be seen in its record.
