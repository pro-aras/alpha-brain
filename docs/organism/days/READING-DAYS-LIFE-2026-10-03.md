# READING OF `brain-long-2` — the days life at 3 days 11 hours (2026-10-03)

*Claude (Sonnet 5.5, swarm claims), 2026-10-03 11:59 +0400 (from `date`) — a reading, no bar set (the days law §3, `PREREG-DAYS-LIFE.md`). Read-only: every figure is computed on COPIES (journal 150 MB, tape rows, SERIES.tsv 983 samples, HEALTH.jsonl 246 rows, STATUS.json, `state/web.json`) by `docs/organism/days/scripts/reading_check.py` at `bc69fdc`; logs `scratch/reading-all-bc69fdc.{log,exit}` (exit 0, 18 assertions, planted controls in each section). *Revised after the verifier's REFUSED of a8baae4: the memory field is the peak (§2), the box's swap is named as the box's, the web path lengths are deterministic and quoted from this log.* The earlier reading is the seat's of 09-30 (`READING-DAYS-LIFE-2026-09-30.md`, branch `hears`); this one says what moved since. Tags: [Certain] = logged and re-derived; [Likely] = fits every measurement, not isolated; [Guessing] = a candidate with its discriminator named.*

## The answer

1. **It lived.** 3 d 11 h since 09-30 00:36 +04: unit restarts 0 (983 SERIES samples), sense restarts 0, `crash` null in 983 of 983, HEALTH.jsonl 246 rows with 0 `problems`, 0 `repairs`, 0 `last_repair`, 0 `page`, 0 `stuck_s`; `RECOVERY.log` and `repairs/` do not exist (an absent file is a presence fact, not silence); `PAGE.json` reads `null`. The only change of the running genome was the evolve adoption of 10-01 01:59 (KWTA 5 → 4), by design.
2. **The brain is as idle as on 09-30.** `brain.learned` 50,000 and `asks_answered` 3,011 read the same in all 232 HEALTH rows since the scene world ended (first read 05:21 +04 on 09-30). Its six tests, graded on 09-30 at 50,000 scenes, therefore describe it today (§6). Everything that moved in these days moved in the cells' mind, the webs and the self.
3. **The cost per canvas did rise, but not as one law.** The quiet baseline went from ≈ 420–520 ms (09-30) to ≈ 1,000–1,060 ms, and the quoted «900–3,600 ms» mixes that baseline with windows that hold a snapshot (median 1,669 ms) and spikes (max 5,239). **All of the rise happened in the first ≈ 30 hours** (exponent against cells 3.53 [2.91, 4.09]); since 10-01 06:00Z it reads flat to near-linear (0.30 and 0.83, both intervals spanning 1), so the whole-life exponent 2.43 is the first phase's. Load, the evolve twins, swap and the sleeps do **not** explain it; cells and moments are 99.6 % collinear, so the series cannot say which one drives it. The cause is **not** identified; the test that would is named in §3.
4. **Memory: the current figure FELL while the peak rose in a step.** The cgroup's `MemoryCurrent` (current, page cache included) rose to 15.5 GB (09-30 18Z) and has fallen since to 12.4 GB (10-03 00Z; 11.9 in the last window); the BOX's swap went 0 → 3.8 GB over the same days (HEALTH reads `/proc/meminfo`: not the life's own; ≈ 3.1 GB of it was released when the life closed at 11:46, so [Likely] mostly the life's cold pages). The process's **peak RSS** (`rss_mb` is `ru_maxrss`, `creature/body.py:91–93`: a high-water mark that can only rise, 1.0 → 10.2 GB) took one new peak of +2.0 GB in two consecutive samples (10-02 12:45–12:55 +04, 8,001 → 10,008 MB) with cells still; mechanism [Guessing] a transient copy of the state.
5. **The webs are true, full and clustered — and the part of them that joins the body's words to the text predicts nothing.** Recount from the words: 0 errors in L and in N, planted changes caught. The cap binds (L: 28,410 edges = 10.0 × 2,841 nodes). Two thirds of the consolidated edges at 150,000 words link a grounded word to a shelf-only word; those read **0.65×** chance in the speech that followed (below it), while shelf–shelf edges read 2.58× and grounded–grounded 1.47×.
6. **The self is frozen with the brain** except one claim: F1 and F2 were demoted in the first hour and nothing has changed state since; B1 («my mind keeps up with what I sense») is the one claim still being observed (4,976 confirmed, 1 contradicted).

## 1 · Did it live — the series

| window (UTC) | births / h | thinks / h | said / h | sleeps / 6 h | snapshots / 6 h | load (median) |
|---|---|---|---|---|---|---|
| 09-30 06 | 370 | 84 | 16.1 | 11.2 | 54.8 | 1.41 |
| 09-30 12 | 337 | 84 | 21.8 | 11.2 | 54.8 | 0.82 |
| 10-01 00 | 326 | 85 | 23.0 | 11.2 | 54.7 | 0.95 |
| 10-01 12 | 356 | 83 | 24.7 | 10.1 | 53.8 | 1.01 |
| **10-01 18** | **170** | 85 | 31.4 | 11.2 | 55.8 | 1.13 |
| **10-02 00** | **160** | 83 | 29.2 | 10.1 | 53.8 | 1.10 |
| 10-02 06 | 332 | 83 | 25.2 | 11.2 | 53.8 | 1.13 |
| 10-02 18 | 317 | 83 | 26.2 | 11.2 | 54.8 | 1.22 |
| 10-03 06 | 280 | 82 | 36.1 | 10.3 | 51.5 | 1.45 |

[Certain] The life runs at a steady cadence: a think every 43 s (10 canvases, ≈ 8.3 canvases a minute), a sleep every ≈ 32 min, a snapshot every ≈ 6.7 min, ≈ 330 births an hour — except two windows (10-01 18Z to 10-02 06Z) where births fell to 160–170 an hour and cells stood nearly still (29,752 → 29,834). [Likely] the dip is the shelf's: births follow the arrival of never-heard words (`ARRIVAL never-heard word`, `BUDGET 400 per arrival`), and the web's node count (= distinct words heard) grew ≈ 40 an hour until 10-01 12Z, then 13 an hour (10-01 08Z–17Z) and 5 an hour (10-01 17Z–10-02 02Z), and ≈ 30 an hour from 10-02 04Z (§4). The first 12 hours carried the seat's heavy jobs (load 6.8–8.2); from 09-30 12Z the box has been quiet (0.8–1.3) until today's swarm (1.45 at the last window).

## 2 · Memory — the peak, the current figure and swap

*Corrected 2026-10-03 after the verifier's REFUSED: STATUS `rss_mb` is `getrusage(RUSAGE_SELF).ru_maxrss` (`creature/body.py:91–93`), a PEAK that can only rise, so the first version of this section (an «RSS» that «climbs in steps» and a line fitted to it) described a high-water mark and is withdrawn. The current figure is the cgroup's `MemoryCurrent` (page cache included); swap is HEALTH's — and that is the BOX's, not the life's: `tools/lives/health.py:202–204` reads `/proc/meminfo` (`SwapTotal − SwapFree`, `MemAvailable`), shared with the seat's jobs and the swarm.*

| window (UTC) | cells | peak RSS MB (ru_maxrss) | MemoryCurrent GB (current) | BOX swap GB (median / max) |
|---|---|---|---|---|
| 09-30 00 | 22,960 | 6,538 | 13.03 | 0.00 / 0.00 |
| 09-30 12 | 25,359 | 7,054 | 15.36 | 0.05 / 0.10 |
| 09-30 18 | 26,345 | 7,305 | **15.49** | 0.00 / 0.00 |
| 10-01 12 | 29,137 | 7,997 | 14.84 | 0.00 / 0.40 |
| 10-02 00 | 29,834 | 8,001 | 14.90 | 0.40 / 0.40 |
| 10-02 06 | 30,727 | **10,008** | 14.33 | 0.75 / 1.30 |
| 10-02 12 | 31,606 | 10,187 | 13.19 | 2.00 / 3.00 |
| 10-02 18 | 32,427 | 10,187 | 12.67 | 3.40 / 3.60 |
| 10-03 00 | 33,257 | 10,187 | 12.39 | 3.80 / 3.90 |
| 10-03 06 | 33,685 | 10,222 | 11.90 | 3.80 / 3.80 |

- **Current usage rose to a high in the first 18 hours and has FALLEN since:** `MemoryCurrent` 13.0 GB (09-30 00Z) → **15.5 GB (09-30 18Z)** → 14.9 (10-02 00Z) → 12.4 (10-03 00Z) → 11.9 (last window; the last sample 12.54 GB; one sample at 07:30Z on 10-03 reads 17.18 GB, page cache beside the swarm's first hour [Guessing]). [Certain]
- **The box's swap rose from nothing to 3.8 GB** while the cgroup fell: 0 until 10-01 12Z, 0.4 GB (10-01 18Z–10-02 00Z), 0.75 (median; max 1.3) at 10-02 06Z, 2.0–3.0 at 10-02 12Z, 3.4 at 10-02 18Z, 3.8 from 10-03 00Z; from 09-30 06:00 +04 on the box's `MemAvailable` never fell below 12.3 GB (it read 6.3 GB in the first hours, with the seat's heavy jobs), so this is swappiness, not pressure. HEALTH cannot say whose pages: its figure is box-wide. [Likely, indirect] most of it was the life's cold pages: `free -m` at 12:15 +04, 29 minutes after the life closed (`STOPPED-AT` 11:46), reads 685 MB of swap used against 3.8 GB in HEALTH's last row, so the closure released ≈ 3.1 GB. A per-process read (`VmSwap` of the pid, or the cgroup's `memory.swap.current`) would settle it; neither was recorded and the life is closed. [Guessing] which pages: the idle brain's arrays.
- **The peak** (a high-water mark: asserted never to fall in the 983 samples) went 1.0 → 10.2 GB with **a new peak of +2.0 GB in two consecutive samples, 10-02 12:45–12:55 +04 (8,001 → 8,925 → 10,008 MB)** while cells stood still (30,707 → 30,724 → 30,722) and births moved by +49 and +13 [Certain]. It is a new peak, i.e. one moment that held 2 GB more than any before; mechanism [Guessing]: a transient copy of the state (the think's freeze copies it on the mind thread: STATUS `think_freeze_ms` reads 247 ms and 1,460 ms in two reads an hour apart; a snapshot writes several state files). Discriminator: `tracemalloc` on a replayed copy, not run. Six new peaks of at least 100 MB after 09-30 06Z; the largest are that pair and 09-30 00:40 (+324 MB).
- **For any life of this genome:** `sight_capacity` 65,536 against `sight_born` 45,456 (STATUS 06:56Z): the allocated arrays double at 65,536 sight births, ≈ 63 h after the copies at ≈ 300 sight births an hour (≈ 10-06/07). What a doubling does to the peak is unmeasured [Guessing]. `brain-long-2` itself was closed at 11:46 +04 (`STOPPED-AT`), after every copy this reading used.

## 3 · The cost per canvas — a series read by window class, not an endpoint

**What the number is.** `mind_ms_per_canvas_1min` = every row's consume time in the last minute **divided by the EYE rows in that minute** (`creature/body.py:_build_status`). A minute that holds a snapshot or a sleep carries its cost; the denominator changed when the scene world stopped feeding (≈ 185 canvases a minute while training, ≈ 8.3 since 05:03 +04 on 09-30), so only clock-worlds-only windows are compared (after 05:30 +04: 925 of the 983).

**Every window classified before any fit** (the journal's own events: 1,311 snapshot events with wall-clock `at`, 262 sleeps through seq → time, a window padded −75 s / +15 s around the STATUS heartbeat): 42 hold a sleep, 221 a snapshot, **688 are quiet**.

| statistic (ms per canvas) | value |
|---|---|
| all clock-world windows | median 895 · p90 1,937 · max 5,239 |
| quiet windows | median 831 · p90 1,303 · max 2,186 |
| windows holding a sleep | median **818** (a sleep adds nothing visible: its 200 replays are cheap) |
| windows holding a snapshot | median **1,669** (a snapshot adds ≈ 840 ms to its minute) |

| window (UTC) | cells | ms all | ms **quiet** | quiet p90 | share holding a snapshot/sleep | load |
|---|---|---|---|---|---|---|
| 09-30 00 | 23,156 | 476 | 456 | 680 | 0.24 | 6.77 |
| 09-30 12 | 25,359 | 616 | 609 | 814 | 0.25 | 0.82 |
| 10-01 00 | 27,414 | 834 | 794 | 1,188 | 0.32 | 0.95 |
| 10-01 06 | 28,346 | 1,013 | 904 | 1,304 | 0.31 | 1.04 |
| 10-01 18 | 29,752 | 1,015 | 980 | 1,416 | 0.26 | 1.13 |
| 10-02 06 | 30,727 | 980 | 936 | 1,252 | 0.26 | 1.13 |
| 10-02 18 | 32,427 | 1,138 | 1,039 | 1,470 | 0.25 | 1.22 |
| 10-03 06 | 33,685 | 1,102 | 1,057 | 1,125 | 0.25 | 1.45 |

So the **«900–3,600 now»** of the brief is the quiet baseline (≈ 1,000–1,060) **plus** snapshot windows and spikes; the baseline is not 3,600. HEALTH.md at 11:24 read 331.9 ms a canvas with a 29-row backlog and STATUS at 10:37 read 1,649.8: the same life within an hour — a one-minute statistic, which is why only the series is read.

**The fits (quiet windows; a planted exponent is recovered first).** Planted on the real windows' cells with noise sd 0.15: exponent 0.0 recovered 0.05 [−0.06, 0.14], 1.0 → 1.00 [0.90, 1.11], 1.5 → 1.48 [1.37, 1.59]: the instrument is sound.
- Whole life: log ms = −18.28 + 2.43 log cells, **exponent 2.43 [2.23, 2.62]**; with the 1-minute load as a covariate 2.40 [2.17, 2.63], load coefficient −0.005 per unit (nothing). With spikes included 2.11 [1.78, 2.43].
- **By regime** — phase 1 (09-30 01:30Z → 10-01 06:00Z; cells 22.7k → 28.2k): **3.53 [2.91, 4.09]**, median 585 ms; phase 2 (→ 10-02 00:00Z; cells 29.2k → 29.8k, nearly still): 0.30 [−1.85, 2.47], median 938 ms; phase 3 (→ 10-03 07:00Z; cells 29.8k → 33.7k): **0.83 [−0.23, 1.85]**, median 1,001 ms. One power law over 3.4 days misdescribes it. Per-cell cost: first day 472 ms / 23.5k = 0.0201 ms; last 8 h 1,033 / 33.3k = 0.0310 (×1.54 over the life) — but over the last 31 h it is **flat to falling** (0.0338 at 10-02 00Z → 0.0314).

**What it is NOT, each tested** [Certain]:
| candidate | test | result |
|---|---|---|
| contention from other jobs | the load covariate; quiet windows by load band | coefficient −0.005; the high-load windows (all early, 23k cells) were *faster* (461–492 ms); load and cells are collinear early, so this excludes a large load effect, not a small one |
| the evolve worker's twins | the 13 rounds' windows [proposal mtime − both twins' wall − 2 min, mtime], quiet windows after 10-01 06Z: inside 87 (median 1,002 ms, load 1.53) vs outside 347 (975 ms, load 1.03) | +27 ms; the same difference with the labels shuffled (500 draws): [−98, +87] — not distinguishable from nothing |
| swap (the BOX's, HEALTH) | 0.0–0.1 GB until 10-01 12:00; 3.8 GB at the end | the rise (phase 1) predates it; phase 3 is flat while it grew |
| the sleeps | median ms of windows holding a sleep | 818 vs 831 quiet |
| the sparse hash (A4L-COST's gene) | `hash_ms_last` from HEALTH: 2.6 → 10.9 ms (∝ cells^1.67) | ≈ 2–3 calls a canvas → 20–35 ms of ≈ 1,000 (2–4 %) |
| the think thread | `think_ms_median` | 39–56 ms in every 6 h window (one window reads 0.0: null readings), flat |

**What it might be** [Guessing; none isolated]: the freeze/apply of the think on the mind thread (`think_freeze_ms` 247 and 1,460 ms in two reads: 25–146 ms a canvas amortized); the recall over all alive cells for each of 5 glances (O(cells × 144)); `ledgers()` rebuilt at 11 call sites of `mind.py` (`build_ledgers` walks all `org.births` and `org.merges`: O(births) each, several per canvas); the edge structure (64,155 alive edges at 06:56Z; edges per cell rising); the garbage collector's full passes over a 10 GB heap of dicts and sets. **Cells and moments cannot be told apart by this series**: corr(log cells, log moments) = 0.9959 (variance inflation 122); the exponent against moments alone is 1.18. **The discriminating measurement** (not run; it needs its own PREREG): replay the same 20–30 canvases from three evolve checkpoints (cells ≈ 24k, 29k, 33k) on COPIES under `cProfile` and `gc.callbacks`, and read ms per canvas by function against cells — ≈ 10 CPU-min on a slot.

**Horizon.** The mind must keep up with ≈ 8.3 canvases a minute (≈ 7.2 s each): the baseline uses ≈ 15 % of that, backlog median 0 (HEALTH max 57 rows at one 10-03 window). At the whole-life exponent the baseline would reach 7.2 s at ≈ 70k cells (≈ 4 months at 330 births an hour); at the phase-3 slope, never in weeks. For a rung fed by the scene world (≈ 185 canvases a minute, a 0.32 s budget) the cost matters at once.

## 4 · The webs (days law §3, items 2–4)

**Replayed exactly.** Web L and N rebuilt from the tape's 192,795 ear words with the mind's own feeding (`mind.py:951–961`, built at `:905`: beta 10, reach 20, seed 20261101): every counter of both webs equals STATUS's at its own `t` (192,795).
**True (item 2).** `recount_errors` from the words: **L 2,841 nodes / 28,410 edges: 0 errors; N 2,841 / 27,495: 0 errors**; planted (a node's `n` +1, an edge's `c` +1 in a copy): 2 errors reported.
**Growth (item 3), every 20,000 words** — words | tape time (UTC) | L nodes, edges, consolidated, replaced, removed | N nodes, edges, consolidated, replaced, removed:

| words | time | L nodes | L edges | L cons. | L repl. | L rem. | N edges | N cons. | N repl. | N rem. |
|---|---|---|---|---|---|---|---|---|---|---|
| 20,000 | 09-29 20:56 | 134 | 875 | 23 | 0 | 212 | 1,317 | 20 | 259 | 199 |
| 60,000 | 09-29 22:17 | 332 | 2,402 | 190 | 0 | 799 | 3,320 | 125 | 726 | 853 |
| 100,000 | 09-30 00:38 | 535 | 4,505 | 371 | 0 | 1,563 | 5,264 | 217 | 1,058 | 1,797 |
| 120,000 | 09-30 14:11 | 1,082 | 10,762 | 1,640 | 1,687 | 4,930 | 10,331 | 821 | 1,058 | 5,309 |
| 140,000 | 10-01 07:45 | 1,782 | 17,820 | 2,987 | 3,850 | 8,947 | 16,375 | 1,381 | 1,058 | 9,783 |
| 160,000 | 10-02 01:43 | 1,947 | 19,470 | 4,082 | 7,489 | 13,210 | 19,469 | 1,908 | 1,530 | 15,144 |
| 180,000 | 10-02 19:46 | 2,528 | 25,168 | 4,954 | 10,655 | 17,177 | 24,151 | 2,241 | 2,124 | 20,041 |
| 192,795 | 10-03 07:17 | 2,841 | 28,410 | 5,451 | 12,739 | 20,127 | 27,495 | 2,423 | 2,124 | 23,272 |

[Certain] **L's edge count is the cap and nothing else:** within 1 % of 10 × nodes at every cut after ≈ 110,000 words and exactly at it at the end (28,410 = 10.0 × 2,841; beta 10 edges a word); what carries information is the churn (12,739 edges evicted, 20,127 dropped by missed chances) and the 5,451 that were consolidated (19 %). N's edges sit just under its cap (27,495 of 28,410). Nodes grow with the shelf's new words: ≈ 40 an hour to 140,000 words (10-01 07:45Z), 13 an hour to 150,000, 5 an hour to 160,000 (10-02 01:43Z), then ≈ 30 an hour (170,000: 2,236; 190,000: 2,781).
**What L holds.** Top hubs by degree: «the» 944, «dot» 937, «key» 937, «circle» 798, «ring» 750, «house» 716, «tree» 711, «cup» 710 (the maker's things dominate the hubs: it says one word every 10 s); strongest consolidated edges: big–ring 8,322, ring–small 8,059, big–star 6,789, big–triangle 6,750, big–cross 6,725 — the scene parent's own size–shape pairs, strongest because both words are frequent. Of L's 2,841 words **29** were ever heard from the scene, game or maker worlds; of its 5,451 consolidated edges **301** join two such words, **3,493** one such word and one shelf-only word, **1,657** two shelf-only words.
**Shape (item 3).** Against 5 random webs of the same nodes and edges (150 BFS sources sampled from the sorted largest component: identical under `PYTHONHASHSEED` 1 and 2, the first version's figures varied and are withdrawn): L all edges clustering **0.645** vs 0.007, mean path 2.45 vs 2.91; L consolidated 0.796 vs 0.011, path 2.64 vs 3.15; N all 0.476 vs 0.007, path 2.38 vs 2.95; N consolidated 0.729 vs 0.014, path 2.68 vs 3.23 — hub-dominated and tightly clustered, as a Zipf text graph is.
**L against N on its own speech (item 4; PREREG-KW-1 K6 enrichment: Σ pair events / Σ chance expectation, over consolidated edges whose two words occur in the held-out words; K7: the same on the held-out words shuffled).**

| snapshot | held-out | web | all | **grounded–grounded** | **grounded–shelf** | **shelf–shelf** | shuffled |
|---|---|---|---|---|---|---|---|
| after 100,000 words (09-30 00:38Z) | 92,795 | L | 1.76 | 1.82 (107 edges) | **0.71** (154; 38 usable) | 1.86 (110) | 0.99 |
| | | N | 1.86 | 1.90 (86) | 0.75 (112; 7 usable) | 1.82 (19) | 0.99 |
| after 150,000 words (10-01 16:58Z) | 42,795 | L | 1.15 | 1.47 (300) | **0.65** (2,362; 2,034 usable) | 2.58 (941) | 1.00 |
| | | N | 1.19 | 1.48 (286) | **0.65** (1,014; 859 usable) | 2.49 (335) | 1.00 |

[Certain] L and N are indistinguishable on speech they have not heard (1.76 vs 1.86; 1.15 vs 1.19); both beat the shuffle (0.99–1.00). The split is the finding: **an edge between a grounded word and a shelf word is anti-predictive (0.65–0.75×, below chance)**; it was consolidated from clock adjacency (the worlds' rows interleave in one tape) and does not recur, and at 150,000 words it is two thirds of the consolidated edges (2,362 of 3,603). The within-world edges predict (shelf–shelf 2.5×; grounded–grounded 1.5×). [Likely] This is the web-level form of Antigravity's «zero connection»: in Web L the text and the body's words are statistically unassociated. It is a statement about the web, which nothing reads (0 callers of `Web.neighbours` in `creature/`), and not about the eye, which sees the rendered sentences (CLAIMS-CHECK §1(b), b5).

## 5 · The self (item 5)

| claim | quantifier | state | confirmed | contradicted | share | first event at scene | first demoted at scene |
|---|---|---|---|---|---|---|---|
| T1 I look at no more than four places on a canvas | always | trusted | 50,000 | 0 | 1.000 | 0 | — |
| T2 the parent says at most one word of each kind | always | trusted | 49,750 | 0 | 1.000 | 250 | — |
| T3 usually what I expect is what the parent says | usually (0.70) | trusted | 40,444 | 9,306 | 0.813 | 250 | **294** (recovered) |
| F1 I see every thing the parent names | always | **demoted** | 44,458 | 5,291 | 0.894 | 250 | **279** |
| F2 the parent always says three words | always | **demoted** | 12,453 | 37,547 | 0.249 | 0 | **29** |
| B1 my mind keeps up with what I sense | usually (0.90) | trusted | 4,976 | 1 | 1.000 | 1 | — |

[Certain] Six claims, not the five Antigravity counts (T1–F2 are KW-1's five; B1 is the days life's sixth, `mind.py:_self_claims`). HEALTH.jsonl shows the claim states changing **once**: all trusted at 00:36 +04 on 09-30, F1 and F2 demoted by 00:57; nothing since. Counts of T1–F2 stand at the brain's 50,000 turns; only B1 moves (the body row every 60 s). Lived: 50,000 canvases, **4 fixations on every one**, 49,750 turns with an expectation, 40,444 confirmed (0.813). **Lived reliability per word** (the word named something it expected for that word; weakest first): ring 0.686 (n 10,247), blue 0.798, red 0.811, white 0.852, yellow 0.873, green 0.894, small 0.896, big 0.898, cross 0.907, triangle 0.948, star 0.954, square 0.959, circle 0.972 — the same ordering as on 09-30 (ring weakest at 0.686), because nothing has been added.

## 6 · The brain, and the sittings' grade (already taken, not re-run)

The brain heard only the scene world; the scene world ended on 09-30 (first HEALTH row showing it, 05:21 +04). `brain.learned` 50,000 and `asks_answered` 3,011 are unchanged in all 232 HEALTH rows since; STATUS now: turns 50,000, said 47,425, asked 4,859. **The sittings were graded on 09-30** (`/data/dev/brain-runs/day0929/days/grade-brain-long-2-2026-09-30/grade-bl2-new/report.txt`; a copy of that folder was the reading's input, nothing re-run here):

| test | reading | bar | verdict |
|---|---|---|---|
| 1 · points (M1) | 0.980 covered (n 202) · 0.811 over all items · coverage 0.828 · chance 0.544 | null p95 0.605 | PASS |
| 2 · refuses (M2a) | 0.853 (n 400) · false refusal 0.074 | — | PASS |
| 2 · refuses by the word (M2b) | 0.646 (n 48) · oracle 0.979 | — | FAIL (the word road) |
| 3 · composes (M3) | 1.000 covered (n 58) · 0.967 over all | 0.80 | PASS |
| 4a · explains | EXIST 1.000 · CARRY 0.952 (13 of 14 words explained; «dax» unknown) | 0.90 · null p95 0.598 | PASS |
| 4b · rule | NOT BUILT | — | — |
| 5 · rejects misuse | refused 1.000 · named 1.000 (n 400) · valid called misuse 0 of 455 | 0.90 / 0.80 / ≤ 0.05 | PASS |
| 6 · one meeting (M6) | 0 fixations on the «dax» at its one showing | 0.70 | NOT GRADABLE (the gaze) |
| SPOKEN · TRUTH · MINIMAL · ORDER · READ-BACK | 0.816 (n 76) · 0.935 (n 62) · 1.000 · 1.000 (n 13, underpowered) · 1.000 (n 96) | 0.695 · 0.845 · 0.90 · 0.95 · — | PASS |
| TRUTH-NEED | 0.382 (n 34) | 0.409 | FAIL |

## 7 · What would show this reading wrong, and what is not done

- A `brain.learned` or `asks_answered` that moves, or a brain row after 05:03 +04 on 09-30 with `act: turn` / `learn` (the seat's own refuter of 09-30): the brain is not idle.
- A profile (§3) in which one function's ms per canvas grows with cells at the phase-1 rate would name the cause; if the cost per canvas is flat across the three checkpoints at equal load, the phase-1 rise was the box (early heavy jobs) and not the life.
- Not done, by design: the profile and the memory high-water test (each needs its own PREREG); the births dip of 10-01 18Z–10-02 06Z is explained only by the arrival rate of new shelf words (§1, [Likely]), not by reading the shelf's text; the 09-30 reading's «its language stopped at scene 401» is the seat's, not re-derived here.
- The numbers are as of the copies (SERIES to 10:35 +04, HEALTH and web.json copied 11:3x, the tape at 11:17, STATUS 07:17Z). The life was closed at 11:46 +04 (`STOPPED-AT`), after every copy: this reading is of a closed record.
