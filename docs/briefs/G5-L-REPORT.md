# Builder L (Sonnet 5) — REPORT: the BabyAI world door + the sound ear ON
*edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:32 +0400. Branch `g5-world-ear`, worktree `/data/dev/genome-wt-p`, off master `ec28b4c`.*

## 0 · What was built

1. **Parser (`genome/machinery.py`), additive:**
   - `WORLD` gains a second shape, dispatched on `args[0] == "game"` so the existing `drawn ...` shape (dispatched on `args[0] != "game"`) is untouched byte-for-byte: `WORLD game <id> every <n> s; seed <s>; frames pov <h>x<w> tile <t>; consequence: <text>`, stored under a **new declared key `WORLD_GAME`** (never overwriting `declared["WORLD"]`, the drawn world's own dict — `creature/body.py`'s `_maker_args_from_declared`/`_declared_folder_dir` read that dict unconditionally). Both `WORLD` lines coexist in one genome text regardless of order (tested both orders).
   - `SENSE ear-sound wav <rate> mono` — a new alternative under the existing `SENSE` gene (dispatched on `args[0] == "ear-sound"`), stored as a plain `Genome` field `ear_sound` (like `gaze`), **never** a `declared[...]` key — so it is never subject to `creature/genes.py`'s `unwired()` refusal, matching how `SENSE eye`/`SENSE ear` already work. Stereo is refused, not silently accepted (the declared line is mono-only; ITD/ILD would need two channels — raised in §4).
   - `creature/genes.py`: one new `RUNS["body"]["WORLD_GAME"]` row, pointing at `creature/body.py:main`. `tests/creature/test_refusal.py`'s `SAMPLE_LINE` fixture (a pre-existing test that pins every `RUNS` gene to a real parseable sample line) needed — and got — a new row for `WORLD_GAME`; this was the *only* thing the pre-existing 139-test creature suite's baseline run failed on before I fixed it (two assertions in `test_sample_line_set_is_exactly_the_registry`/`test_every_runs_gene_parses`), confirming the registry-pinning test does its job.

2. **The game door** (`creature/senses/game.py` + `tools/game_worker_babyai.py`):
   - The BabyAI world runs as a **subprocess** under `/data/dev/game-worlds/venv`'s own python3 (gymnasium/minigrid are not installed for the system python the creature itself runs on, and the venv has none of this tree). The worker writes one manifest JSON + one PNG per step into a door directory, each **atomically** (tmp file + `os.replace`, the PNG durable before its manifest names it).
   - The creature's own act: **no `ACT` gene exists on this branch** (Builder K's, a sibling worktree `g5-acts`, unmerged) — so the *worker* chooses each action from a seeded RNG stream (`np.random.default_rng([seed, 0x67616D65])`, never `env.action_space.sample()`'s own generator), and every outcome row records this plainly: `meta["chosen_by"] = "schedule"`, `meta["road"] = "no road"` — the brief's own phrase, item 1.
   - The sense thread (`creature/senses/game.py:sense`) watches the door directory and publishes, per manifest, in the tape's own order law: **ear** (the mission's target word) → **eye** (the 128×128 canvas via `gaze.canvas_of_picture`, the folder door's own road) → **outcome** (for every manifest but the very first — the reset frame has no act). `outcome`'s row carries K's own OUTCOME shape (`act`/`expected`/`got`/`residual`/`source`) as both payload and meta, published under sense name `"outcome"` since `genome.declared["OUTCOME"]` does not exist on this branch — **said here, not worked around**.
   - `creature/mind.py:consume` only branches on `"ear"`/`"eye"`; an `"outcome"` row (like a `"door"` row already did) falls through untouched — verified directly (§2).

3. **The sound ear** (`genome/cochlea.py` + `creature/senses/ear.py`):
   - `genome/cochlea.py` **sha-pins and imports verbatim** E52's own `gammatone.py` (`afb637a9…`) and `front.py` (`91bddd4e…`) from `/data/dev/alpha3/experiments/E52-hearing-the-cochlear-front/code/` — the same discipline `genome/gaze.py` already uses for Alpha 2's organs, applied here to a second tree's code, so the Slaney/Holdsworth IIR coefficients and the measured AGC/modulation machinery are never re-derived by hand. What this file *adds* (E52 never built it — its own report says so) is **EVENT DETECTION**: peak-picking the broadband onset (the per-band onset channels summed) with `find_peaks(prominence=2 dB, distance=60 ms)` — EAR.md §4's own line, verbatim — and the per-event **TRAIT vector** (`band` 32 + `onset_shape` 4 + `level` 1 = 37, unit length).
   - `creature/senses/ear.py` watches **the same folder door** the picture sense watches (the brief's own words: "a sense thread listening at the folder door for audio files") for `.wav` files, publishes one tape row per event under sense name `"ear-sound"`, and publishes **zero rows** while silent (both senses of silent — no file, and a file that IS silence — proven in §3).
   - **Not wired**: `AREA sound`/`MEET sight sound`/`MEET sound words` (a machinery change beyond this brief's item 2), and `OWNVOICE` (needs a top-down prediction the mind does not send on this branch — `meta["ownvoice"]` is honestly `None`, never a guessed `False`). WHERE (ITD/ILD) is not delivered: the declared line is mono, and a directional cue needs two channels.

## 1 · The parser tests

`tests/genome/test_parse_g5_world_game_ear_sound.py`, 13 tests, all passing:
- `G4.genome` (the live creature's own genome, unmodified on this branch) parses to the **exact same four-key `declared["WORLD"]`** dict as before (`drawn_every_s: 5, arrival_every_h: 6, folder: "world/", web_per_hour: 6`), with no `WORLD_GAME` key and `ear_sound is None` — the refusing test the brief names.
- The old `WORLD drawn ...` line, fed alone, still parses to the same four keys; a malformed old line still refuses the same way.
- The new `WORLD game ...` line parses into its own `declared["WORLD_GAME"]` dict; missing a number, or missing the `consequence:` clause, refuses by name (`"WORLD game"` in the message).
- **Both lines together, in both orders**, coexist: `declared["WORLD"]` is byte-identical to the drawn-alone case regardless of the game line's presence or position.
- `SENSE ear-sound wav 16000 mono` sets `genome.ear_sound == {"rate": 16000, "channels": "mono"}`, never touches `declared`; a malformed line, or `stereo` in place of `mono`, refuses by name; `SENSE ear letters 8` (the old line) is untouched when both are present.
- `WORLD_GAME` is confirmed WIRED against `creature/genes.py:unwired()` directly (not only "the organism starts" — the exact mechanism the refusal law checks).

## 2 · The game door — measurements

**Frame-identity (item 3's refusing test, reused from G5-G's own road — REPORT-G5-G.md §2 "Stage 3": same-process agreement proves nothing, two separate processes are the only real test).** Ran the worker twice, same `--seed 20260922`, 8 steps each, in two independent processes:

```
8 8
ALL MANIFESTS + FRAMES BYTE-IDENTICAL ACROSS TWO SEPARATE PROCESSES
```

Every manifest field (`step, episode, game, seed, mission, act, reward, terminated, truncated, frame`) and every frame PNG's sha256 matched exactly. `tests/creature/test_game_door.py::TestFrameIdentityAcrossTwoProcesses` pins this (plus a negative control: a *different* seed diverges on the very first step — the identity claim is not vacuous).

**The `outcome` row falls through `mind.consume` untouched — verified directly**, not inferred: built a real tape (5 manifests → 14 rows: 5 ear, 5 eye, 4 outcome), fed it to `creature.replay.run_replay` on `G4-skeleton.genome` twice from two fresh work roots, and the two mind journals were **byte-identical** (`tests/creature/test_game_door.py::TestReplayNeverReRunsTheGame`, 5 mind-journal rows for 5 eye canvases). The worker subprocess ran exactly once, before either replay; `creature.replay` never touches `creature/senses/game.py` or the venv at all — the game is never re-run at replay, structurally, not by convention.

**Row shapes and ordering** (`tests/creature/test_game_door.py::TestSenseThreadPublishesRows`): a 5-manifest run publishes 14 rows (1 reset × [ear, eye] + 4 stepped × [ear, eye, outcome]); every `ear` row's word is ≤ 8 lowercase letters (the ear's own channel limit); every `outcome` row carries `act ∈ ACT_NAMES`, `expected: None`, `got: float`, `residual: None`, `chosen_by: "schedule"`, `road: "no road"`; ear precedes eye precedes outcome within every moment.

**The mission word — a raised design decision.** BabyAI missions are multi-word sentences (`"go to the purple box"`); the creature's ear delivers exactly one word per moment (`SENSE ear letters 8`; `mind.py`'s `self.pending[moment] = word` keeps only the *last* ear row published before a moment's eye row). **The full mission cannot fit this channel without a machinery change nobody has built** (Builder I's DELIVER/MOMENT seam, a sibling worktree, does not touch this). Chose the mission's **last token — the object noun** (`ball`/`key`/`box`) as the one word published, because it is still the token `MEET sight words` was designed to bind, and because it is the single decision-critical word (which object to find). The full mission survives losslessly in `meta["mission"]` on the same tape row, so nothing is discarded from the *record*, only from what reaches the organism's word channel today. **Raised, not resolved**: a multi-word mission (colour + object, or the full sentence) needs either several ear rows per moment (a `mind.py` change outside this brief) or a wider word channel.

**The null, reproduced** (item 3: "the null (a random policy .29) printed as the mark's floor"). Ran the worker's own action schedule (uniform over `env.action_space.n == 7`, matching REPORT-G5-G.md §4.1's protocol exactly) over 100 episodes, seeds 101–200, under the venv:

```
episodes: 100
success rate: 0.3100
mean return: 0.1870
REPORT-G5-G.md's own numbers: success 0.29, mean return 0.1464
```

Same regime (≈30% success, small positive mean return), not byte-identical to G's own number — expected, since G's exact action-RNG seeding scheme is not specified in the report's prose and this worker's own scheme (`default_rng([seed, "game" bytes])`) is necessarily a different generator stream. Printed as the mark's floor, per the brief.

**The eye's band on the world's things — reproduced through THIS worktree** (item 3: "with J's colour block if merged, without it the number G measured (−0.107) must reproduce"). J's colour work (`g5-bind-colour`, a sibling worktree) is not merged here, so this is the grey-only number. Reused G's own already-harvested BabyAI POV frames (`/data/dev/game-worlds/results/minigrid.npz`, read-only, untouched — G's own harvest, independent of any worktree's code), ran them through **this worktree's own** `genome/gaze.py` + `genome/machinery.py` retina road (not `/data/dev/genome`):

```
[reproduced on genome-wt-p, grey, mode=gaze] THINGS-ONLY margin=-0.10696197572697974
  (within-median 0.8035265018295555, between-p95 0.9104884775565353, classes 5, glances 195)
G5-G's own reported number (REPORT-G5-G.md table): BabyAI POV gaze grey things-only margin = -0.107
```

Matches to 3 decimal places. Pinned as a real test (`tests/creature/test_game_bands_reproduce.py`, `assertAlmostEqual(..., places=2)`), not just a one-off script.

**Cost:** the worker's own `--period-s` is wired from `declared["WORLD_GAME"]["every_s"]`; per-step wall time on this box (8 steps, cold start including env construction) was well under a second per step excluding the one-time `gym.make` cost — consistent with G5-G's own measured 1.94 ms/frame (frame render) + 8.3 ms (eye) figures; not independently re-timed here (G's own numbers are the load-bearing cost claim, reused, not re-derived).

## 3 · The sound ear — measurements

**T7, measured BEFORE anything was wired** (item 2: "T7 FIRST: count the events one hour of a real recording would publish against the tape's rate (0.219 rows/s)... before any event reaches the tape"). Ran `genome/cochlea.analyse` over the first 100 files of LibriSpeech dev-clean (≈10.9 minutes of real speech), under `nice -n 10`, `OMP_NUM_THREADS=2`:

```
files: 100
total audio duration: 652.5 s = 10.88 min
total events: 8169
event rate: 12.5188 events/s
one hour of this audio would publish: 45067.6 events = 12.5188 events/s sustained
the creature's own tape rate today: 0.219 rows/s
ratio hour-rate : 5/s floor = 2.504   ratio hour-rate : 100/s ceiling = 0.1252
in log10 space, the rate 12.519/s is closer to 5/s
wall time for 100 files: 37.7 s
front cost: 0.0578 wall-s per audio-second (2 threads)
21:03:26 up 6 days, 7:19, 1 user, load average: 4.46, 3.45, 2.09
```

**Passes the brief's own gate**: 12.52 events/s is 2.5× the 5/s floor and 12.5% of the 100/s ceiling — closer to 5/s under both a linear and a log-scale reading, by a wide margin. Pinned as `tests/creature/test_ear_sound_door.py::TestT7EventRateGate` (a faster 15-file subset for test speed; the 100-file number above is the load-bearing one). **Honest caveat**: 12.52/s sits above the 3–8 Hz syllable-rate band EAR.md itself names (E44d's own peak-picker found 3.01/s) — this is an *onset* rate (plosive attacks, vowel onsets, formant transitions), not a syllable-nuclei rate; it clears the brief's literal gate but a design that wants syllable-grain events specifically would need a coarser prominence/gap than the one tested here. Named, not smoothed over. An hour of continuous speech would add ≈45,068 rows against the tape's current ≈788 rows/hour — a ≈57× increase if this sense ran on a continuously-speaking world; worth a caution for whoever arms it on a world that actually talks.

**Silence, both halves proven** (`tests/creature/test_ear_sound_door.py::TestSilencePublishesNothing`, `tests/genome/test_cochlea.py::TestSilence`):
- An armed door with **no file at all** publishes 0 rows over 1.5 s / several scans.
- A **digitally-silent** `.wav` (all-zero samples) publishes 0 rows through the sense thread, and `cochlea.analyse(np.zeros(...))` returns `{"events": []}` directly against the organ.
- The file is still marked SEEN either way (never re-scanned forever, never a re-publish storm).

**T1 — the frequency-path plant, the ear's own toy** (item 2, EAR.md §4 T1: "the ONE E52 could not do"). A 4-bit code, each bit choosing between two neighbouring gammatone channels' centre frequencies, **identical amplitude/duration/onset-schedule regardless of bit** (so a broadband envelope reader sees the same shape for bit 0 and bit 1 by construction):

```
pair channel indices: [(18, 19), (22, 23), (25, 26), (29, 30)]
pair centre frequencies (Hz): [(1617.1, 1821.4), (2580.6, 2891.7), (3620.9, 4047.1), (5630.4, 6279.1)]
held-out trials: 50
FRONT (gammatone, band read at each pip's centre): per-bit accuracy 1.0000, exact-code accuracy 1.0000
BLIND CONTROL (one broadband channel THROUGH THE SAME rectify/compress/AGC nonlinearity, EAR §4 T1's own
  definition): per-bit accuracy 0.4750, exact-code accuracy 0.0000 -- within the shuffled twin's noise
  band around 0.5 (0.475 vs 0.5, N=200 bits, sd~=0.035)
SECOND, INDEPENDENTLY-BLIND CONTROL (plain RMS of the raw waveform, no cochlear machinery at all):
  per-bit accuracy 0.5850, exact-code accuracy 0.1000
ceiling of this toy: 1.0 (deterministic synthesis, band read at a fixed known instant, no noise) -- REACHED
```

**Front reaches the ceiling (1.0/1.0)**; the brief's own literal blind control (one broadband channel, rectify→compress→AGC, no filterbank) sits within noise of chance. Pinned in `tests/genome/test_cochlea.py::TestT1FrequencyPathPlant` with a binomial significance check (`|z| < 2.6`) rather than an eyeball "close to 0.5".

**A real finding, from building this toy, corrected before the numbers above were taken:** the *first* channel-pair choice (adjacent indices 4/5 and 11/12, centre frequencies 195–755 Hz) made the brief's own literal blind control **leak**:

```
pair 0: f=(196,243)  broadband_level_lo=0.349355 hi=1.450547  rel_diff=+315.2069%
pair 1: f=(656,754)  broadband_level_lo=0.696572 hi=0.751845  rel_diff=+7.9350%
pair 2: f=(1617,1821) broadband_level_lo=0.668365 hi=0.736764  rel_diff=+10.2337%
pair 3: f=(3621,4047) broadband_level_lo=0.710572 hi=0.710187  rel_diff=-0.0541%
```

**Mechanism**: E52's `rectify_compress` (a pointwise nonlinearity, exponent 0.3) runs *before* the 320 Hz envelope low-pass (`ENV_LPF_HZ`); for carriers near/below that cutoff, the compressed ripple is not fully attenuated by the 2nd-order Butterworth's −12 dB/octave roll-off, so a "broadband channel through the same nonlinear stages" is **not actually blind to frequency** for those carriers. Per the brief's own rule ("if it rises above chance, the plant leaks through the envelope and the design is refused before the front is judged at all"), **that first pair choice would have been refused**. Fixed by moving all four pairs to ≥ 5× the 320 Hz cutoff (1.6 kHz and up), where the leak measures < 1% at the smallest of the four and the control reads chance (above). This is the estate's own #228/#175 discipline in a new instance: a control's blindness must be *measured*, not assumed from its description.

**A second, separate finding, also reported and not hidden**: `analyse()`'s own EVENT rule **over-segments a sharp synthetic tone onset** — a 4-pip stamp (intended: 4 onsets) produced 18–20 events, because a narrowband gammatone channel's own impulse-response ringdown at low-to-mid centre frequencies wobbles for tens of milliseconds as it settles, and those wobbles sum (across 32 channels) into several distinguishable broadband-onset peaks per pip. **This did not appear in T7's measurement on real speech** (12.52 events/s, a plausible onset rate) — natural formant onsets are far less abrupt than a linear/raised-cosine amplitude ramp on a pure tone. Consequence for this toy: band was read at each pip's known **centre** (bypassing the EVENT peak list entirely), not at the first detected peak, and each bit was decoded from its **own independent clip** (a second bug found and fixed: reading 4 pips as one concatenated stamp let the AGC's own "target from the first 200 ms of the clip" calibrate against pip 1's frequency only, then mis-gain pips 2–4 — a test-harness confound, not a fact about the front). Raised for whoever tunes the EVENT rule's parameters against synthetic material: this specific over-segmentation is a property of sharp synthetic onsets, not of T7's real-speech measurement.

## 4 · What was raised, not worked around

1. **The full BabyAI mission cannot fit the creature's one-word-per-moment ear channel.** Publishing only the target-object noun (§2) is the smallest honest choice, not a fix; a colour+object or full-sentence design needs a `mind.py`/machinery change this brief does not make.
2. **`ACT`/`OUTCOME` are not merged on this branch** (Builder K's, sibling worktree `g5-acts`). The game worker chooses acts by a seeded schedule; outcome rows are published under sense name `"outcome"` with K's own field shape, `meta["road"] = "no road"`, ready for K's consumer the day it lands — not built here.
3. **`WHERE` (ITD/ILD) and `OWNVOICE` are not computed.** `SENSE ear-sound` is mono-only (the declared line, and machinery.py's parser refuses `stereo`); a directional cue needs two channels. `OWNVOICE` needs a top-down prediction (ADAPTS, BRIEF.md's bin) the mind does not send on this branch (`SENTENCE`/the mouth are `#OFF` in `G4.genome`) — `meta["ownvoice"]` is always `None`.
4. **`AREA sound from cochlea` / `MEET sight sound` / `MEET sound words` are not wired.** Both new senses only *publish*; `creature/mind.py:consume` falls through `"ear-sound"` and `"outcome"` rows untouched today (verified directly, §2) — a machinery change beyond this brief's item 1/2, ready for whoever wires it.
5. **The EVENT rule's parameters (prominence 2 dB, gap 60 ms) were only measured against real speech (T7) and a synthetic-tone toy (T1), not tuned for either.** T1 exposed real over-segmentation on sharp synthetic onsets (§3) that did not appear in T7's real-speech measurement; if a future design wants syllable-grain events specifically (3–8 Hz, per EAR.md's own citation), the current parameters (12.5 events/s, an onset rate) are not that grain, though they clear the brief's literal T7 refusal gate.
6. **The game's own cost (wall-ms per step, sustained) was not independently re-timed** on this box beyond the frame-identity/null runs (§2); G5-G's own 1.94 ms/frame + 8.3 ms/eye figures are reused, not re-derived, since the worker/sense-thread pipeline built here did not change either number's mechanism.

## 5 · Suites, on the final bytes

```
$ python3 -u -m unittest discover -s tests/genome -t .
----------------------------------------------------------------------
Ran 156 tests in 76.301s

OK (skipped=1, expected failures=6)
```

```
$ python3 -u -m unittest discover -s tests/creature -t .
----------------------------------------------------------------------
Ran 150 tests in 729.068s

OK
```

(729 s reflects heavy CPU contention: three sibling builders — I/J/K — were running their own full `tests/creature` suites concurrently on the same box at the time; `uptime` load average during this window was 4-5 on a shared host. The intermediate 139-test baseline run, taken before any of this branch's code was written, caught the two `test_refusal.py` assertions fixed in commit 1 — see §0 item 1. Every G5-L-specific test file — `test_parse_g5_world_game_ear_sound.py` (13/13), `test_cochlea.py` (7/7), `test_ear_sound_door.py` (6/6), `test_game_door.py` (5/5), `test_game_bands_reproduce.py` (1/1), `test_game_and_ear_sound_arming.py` (5/5), `test_writer_sweep.py` (5/5, both new sense modules pass the writer/no-Organism-import checks) — was run and confirmed green individually before this final full-suite run.)

New/changed test files in this branch: `tests/genome/test_parse_g5_world_game_ear_sound.py` (13), `tests/genome/test_cochlea.py` (7), `tests/creature/test_ear_sound_door.py` (6), `tests/creature/test_game_door.py` (5), `tests/creature/test_game_bands_reproduce.py` (1), `tests/creature/test_game_and_ear_sound_arming.py` (5), `tests/creature/test_refusal.py` (updated fixture, all 12 pass). **60 new/updated assertions across 6 files, all green individually before the final full-suite run.**

## 6 · Commits on `g5-world-ear`

- `2aa02dd` — the BabyAI world door + the sound ear ON (parser + senses + tests)
- `eefb8a8` — the game-door replay proof + portability skip-guards
- `e612509` — `--game-door` overrides only the directory, never substitutes for `WORLD_GAME`
- `233aa8f` — pin the game/ear-sound door arming functions directly

## 7 · Files touched

- `genome/machinery.py` — parser: `WORLD game ...`, `SENSE ear-sound ...`
- `creature/genes.py` — `RUNS["body"]["WORLD_GAME"]`
- `creature/body.py` — `_declared_game_config`, the game/ear-sound wiring in `main()`
- `creature/senses/game.py`, `creature/senses/ear.py`, `genome/cochlea.py`, `tools/game_worker_babyai.py` — new
- `tests/genome/test_parse_g5_world_game_ear_sound.py`, `tests/genome/test_cochlea.py`, `tests/creature/test_ear_sound_door.py`, `tests/creature/test_game_door.py`, `tests/creature/test_game_bands_reproduce.py`, `tests/creature/test_game_and_ear_sound_arming.py` — new
- `tests/creature/test_refusal.py` — `SAMPLE_LINE["WORLD_GAME"]`
- `.gitignore` — `scratch/`
