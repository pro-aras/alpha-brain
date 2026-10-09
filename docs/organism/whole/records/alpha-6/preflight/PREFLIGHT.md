# G-PREFLIGHT — the two short lives of brain-long-5 on the DECLARED TOY SHELF (PREREG-ALPHA-6 §2 B5, §3)

*Builder lane: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 — the seat's authority delegated by the law
(§2 B5: «closed by the seat under this law»; the delegation brief: launched/closed by the builder under the
law). The launch machinery is the standard one (launch_long.sh → launch_brain.sh → close_long.sh); the driver
is the committed `tools/lives/preflight_alpha6.sh` (its header names the fence form).*

**The toy shelf (the law's own fixtures, never the real shelf):** `/data/dev/brain-runs/alpha-6/
bl5-preflight-toy/video-shelf` — 22 synthetic frames (a red square that moves; a blue circle's visit) +
a tiny SRT (an 11-word motherese vocabulary), put through the REAL converter (`tools/worlds/video_door.py`,
unchanged — V0's own mapping: 22 eye rows + 28 ear rows = 50 rows) and promoted by the build's own tool
(`tools/worlds/video_shelf.py`). The manifest: `MANIFEST.sha256` sha256
**4f663459a5e7082781adbcd8b7a0caa0d47f0efdcca6b08d0a06d20deed5e641** (55 files, verified OK at each
launch). The fixture's recipe + truths: `make_toy_shelf.py`, `TOY-FIXTURE.json` here. Both pre-flight lives
share it READ-ONLY (frozen by its manifest); each life's root got its own GENOME.genome copy at launch.

**The pre-flight genome:** `genome/brain/lives/BRAIN-LONG-5-PREFLIGHT.genome` = BRAIN-LONG-5.genome with the
ladder's own pre-flight values (train 400; calibrate at 250 and before a sitting; the toy shelf's path) — the
diff pinned by tests/genome/test_brain_long_5.py. The mouth clause declared (`; incremental`); the front wired
by the launch command's `--eye-front`.

## pre-1 — the kill gate: **PREFLIGHT PASS** (the driver's log: pre-1-driver.log)

- Birth healthy: STATUS crash null; the first calibration (learned 250, calibrations 1) at ~18 min
  (the full organism + the video world + the front: ≈28 % worded-heard density at ~0.8 canvases/s — the
  law's M-CADENCE arithmetic's own form at bench scale).
- The video world flows: eye 829 / ear 1057 rows at the 2 s cadence (loop 24 by then — the loop count
  journaled); the first 40 video rows == the shelf's own, metas and payload bytes (provenance untouched).
- The front: the journal's `front` key on 685/685 canvas rows (100 %).
- The mouth: voice rows 60 (the W1 voice live); the say-answer row-level form NAMED honestly — none inside
  the flight's ≤1 h price (the sitting's speak split lands later; the clause's selection is proven at the
  bench and by the voice rows; it reads live on the launch's first day at M-MOUTH's own 6 h wall).
- RSS 447.96 MB against the DECLARED 4G fence (S2 — never crossed).
- THE HARD KILL (`kill -9` the MainPID): the unit's Restart=on-failure brought it back; STATUS
  `restored: true` (the gate's own bar), crash null; the life went on (learned 406; turns
  {406, said 67, asked 64, voiced 67} — said == voiced exactly, W1's own invariant live).
- Closed clean: `STOPPED-AT 2026-10-09 10:13 +0400`; the unit disabled; the three timers removed.

## pre-2 — the power-cut gate: **PREFLIGHT PASS** (the driver's log: pre-2-driver.log)

- The same healthy birth (learned 251, calibrations 1; front 687/687; video eye 834 / ear 1064; voice rows 64;
  RSS 473.81 MB vs the fence).
- THE POWER CUT (preflight_days.sh's own form): `kill -9` and, inside the restart gap, the tape's day file
  torn with 4,096 NULs, the journal's day file torn mid-row, beliefs.jsonl torn, the SEQ emptied.
- The life came back by itself (Restart=on-failure), the repair healed it BEFORE anything appended:
  `repairs/REPAIRS.jsonl` 3 rows; `restored: true`; the tape 3,295 rows with NO seq used twice, max 3,295 >
  3,168 before the cut (new rows — video among them — flowing after the heal).
- Closed clean: `STOPPED-AT 2026-10-09 10:42 +0400`; the unit disabled; the timers removed.

## The false starts, named (never hidden)

- pre-1 attempt 1 (09:1x): the driver's own first wait caps (15 min to the calibration) were mispriced against
  the real pace of the full organism + the video world + the front; stopped at the cap, closed clean
  (STOPPED-AT), the minutes-old root removed. The checkpoints were re-priced into the law's ≤1 h price
  (commit 76e97c7). Log: pre-1-false-start-0.log.
- pre-1 attempt 2 (09:4x): the driver reached the calibration but its video-provenance check over-asserted the
  concat tapes' `video` meta key (a single-video converter tape carries none); the LIFE was healthy — the
  instrument was wrong. Closed clean, the root removed; the check now pins the first 40 video rows against the
  shelf's own rows field-for-field and byte-for-byte (commit 972f6e7). Log: pre-1-false-start-1.log.

Both pre-flight roots stand sealed under `/data/dev/genome-lives/` (pre-1 at 972f6e7, pre-2 at 972f6e7), the
program's own closed-life records.
