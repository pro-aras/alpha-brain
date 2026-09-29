# PREREG SLEEP-AB — which episodes the creature rehearses at sleep, tested on alpha4-1's closed tape

*Drafted by Opus 5.5 (the designer), 2026-09-29 14:32 +0400, for the co-signature of Claude (Fable 5.1, the seat). Law once both names stand on the FINAL text.*

**The order it carries (VERDICT-TMEM1, 2026-09-28, «What this changes» 2):** «Before any new life, the sleep rule gets an A/B on a closed tape: surprise against uniform against protect-the-strong.»

**What this is.** A design and a price. Nothing in it is built. Behind it: one 6,000-row pilot replay (§6), read-only scripts, and one exam plant on copies (§5.4). Every script and output is under `/data/dev/brain-runs/day0929/sleep-ab/` (`scripts/`, `measure/`, `pilot/`, `plant/`). Tags: **[Certain]** = read in a file or measured, with its path. **[Likely]** = inferred. **[Guessing]** = a prediction with little behind it.

## 0 · What was known when this was written
So a reader can tell a prediction from hindsight.

### 0.1 The law, and what it actually replays
- The genome line is `SLEEP    every 2500 moments replay 200 by surprise`. [Certain, `GENOME.genome`]
- At a boundary the mind replays `Episodes.most_surprising(200)` as ordinary moments: the 200 live episodes with the largest stored `surprise`, ties by the SMALLER id. [Certain, `genome/sleep.py:43–65`, `genome/fast.py:182–189`]
- The stored `surprise` is PREDICT's error at the moment of writing. It is never updated. [Certain, `fast.py:133` is its only writer] alpha4-1 runs the COMPARATOR arm: 1.0 when the winning sight cell's answer is not the moment's word or nothing resonates, else 1 − cos ≤ 0.048. So it is bimodal. [Certain, `genome/predict.py:137–230`; the ring at seq 51,303 holds 5,941 rows at exactly 1.0 and a median of 0.018, `measure/ring.json`]
- **So the law replays the SAME 200 episodes at every one of the 43 sleeps inside the 12 h cut.** [Certain, `measure/law_set.json`, read from the pilot's own replayed ring (its last snapshot, seq 5,897, kept at `pilot/state-last-snapshot/`) and the live journal] One episode is written per canvas (the journal's `ep` reaches 20,236 at seq 50,094). Among the first 500 episodes, which is the ring at the first sleep, 242 carry 1.0. The 200 with the smallest ids are ids 0–411: the first ≈ 15 minutes of life. New episodes carry larger ids, so they never displace them. The ring (20,000 rows) holds 19,820 at the cut's last sleep (seq 49,098) and first overwrites id 0 at the 20,000th canvas, after it.
- **That fixed set holds** 129 shelf episodes (the book's header words: «eclectic», «gutenber», «ebook», «revised», «edition» …), 38 maker episodes of the eleven (2–5 each), 25 folder episodes («anchor» 18, «ahmad» 6), 4 game, 2 hands, 2 lexicon. It holds **0 of the five arrivals** (they first appear at seq 17,289; presence: 159 maker episodes among ids 0–411). [Certain, `measure/law_set.json`; the 51 / 224 split of §4 from the same copy, `scripts/read_w0_split.py`]
- After the wrap the set MOVES: it becomes the oldest surprising episodes about to fall off the ring (ids 744–1,220 at seq 51,303; ids 18,422–19,109 at 93,188). [Certain, `measure/ring.json`]
- The lived life slept 83 times, first at seq 1,271, 2,434 and 3,588; 43 sleeps fall inside the 12 h cut. CYCLE ran at 57 of the 80 sleeps of 2026-09-23. [Certain, `measure/verify_record.json`, journal]
- A replayed moment prunes more edges than a live one: 0.51 against 0.37 a moment inside the cut (0.69 against 0.43 over the lived day). [Certain, `measure/replay_vs_live_rates.json`] Live glances include SURPRISE's confirmed (cheap) moments, which never prune; so this is not yet evidence of harm. [Likely]

### 0.2 What the memory round measured (a different learner)
- T-MEM-1 (VERDICT-TMEM1) on the brain's word learner, rooms in sequence: forgetting after R3 was 24–32 % with no rehearsal, 1–4 % uniform, 2–3 % by drift, ≤ 0.4 % protect-the-strong (the GATE), and **49–64 % by surprise, worse than none.** The GATE beat GATE-RANDOM at 1 of 3 seeds only. [Certain, as recorded]
- That learner answers from ONE shared map. The creature answers through cells and edges. Nothing here assumes the result transfers.

### 0.3 The creature's own history on sleep and forgetting
- G4-PREREG §10 (2026-09-19): a two-arrival toy on the creature's tower front lost 0.0 pp without sleep at three seed pairs; «SLEEP's retention role … on this one it is untestable». A toy on drawn worlds. [Certain, as recorded]
- Life 2 (`docs/organs/MIND-MEMORY.md:75`): the no-sleep twin scored Q1 .99375 against the live creature's .956. One reading each. [Certain, as recorded]
- `tests/genome/test_sleep.py` (W3-2b note, 2026-09-21), a crude pool3 front: no sleep lost 70 pp; under the bimodal error the weakest schedule lost 85 pp, «a ranking now mostly a tie at error=1.0 broken by episode-array order, can pick a worse sample than never replaying». [Certain, as recorded]
- alpha4-1's 2 h smoke: the blind-sleep twin read Q1 (all words) 0.650 against the life's 0.669, one sitting each (3 answers of 160). [Certain, `readings/smoke-2h/VERDICT.md`] No reading.

### 0.4 alpha4-1 forgets, under the law, in its own exams
Read from `exam/*.json` (`ask_all_words.Q1.per_thing`: 10 FIXED held-out canvases a thing, seed 2, `tools/self_exam.py:60`) by `scripts/exam_series.py`. [Certain]
- The maker's windows, from the tape's first maker rows: w1 opens at seq 17,289, w2 at 33,828, w3 at 50,095, w4 at 65,106, w5 at 79,195.
- **Window 1** shows the five arrivals (cup, house, key, moon, tree) and three of the eleven (dot, star, triangle). So **eight of the eleven go unshown for 4 h**: arrow, bar, circle, cross, diamond, ring, square, wave. [Certain, the maker's ear words by window] (The maker draws with `world_maker.DEFAULT_SEED` 20260920, not the genome's SEED; `schedule(20260923, 1)` names the wrong three. Every window fact here is read from the tape.)
- **Window 2** shows the eleven again. So **the five arrivals go unshown for 4 h.**
- A window's LEVEL = the mean over its last three sittings (18 live sittings a window).

| window pair | things | level at the end of learning | level at the end of the unshown window | per thing |
|---|---|---|---|---|
| w0 → w1 | the eight | 0.975 | 0.892 (−0.083) | circle −0.13, diamond −0.17, ring −0.17, square −0.20, the other four 0 |
| w1 → w2 | the five | 0.993 | 0.440 (−0.553) | key −1.00, tree −0.97, house −0.80, moon 0, cup 0 |

- The collapses are by THING and abrupt: key read 1.0 at seq 33,060 and 0.0 at 34,849, a thousand rows into w2. Ten answers of a thing move together. **So the unit of forgetting here is the thing, not the answer.**
- **A correlate, not yet a cause** (#243 (2)). An arrival was lost when ANOTHER source kept saying its word while the maker was silent. In w2: key heard 145 times from the game, tree 8 and house 2 from the shelf, moon and cup 0 times. In w4 (outside the cut): key 4 → −0.27, tree 18 → −0.87, house 0 → −0.17, moon and cup 0 → 0. [Certain, `measure/shelf_words.json`; the reading is Likely] The eight's words were heard by nobody in w1; their smaller losses sit with look-alike arrivals (the live Q2 at 05:02 answered house → «diamond»). [Likely]

### 0.5 The record as it stands on disk
- **The lived cut ends at seq 93,188** (the first stop, §3.1). **The ledger no longer says so**: `state/ledger.json` reads 119,958. The 09-24 21:51 reboot resurrected the unit, which resumed «from seq 93188» and lived to 2026-09-26T06:52:52Z. `state/` is that resurrected organism. [Certain]
- **The closed end state survives** at `readings/read-by-age-root/state/` (the copy taken at the 05:00 stop; link count 1 on `organism.*`, `ledger.json`, `episodes.npz`). Loaded, its hash is `7b2749de…`, the live journal's own hash at seq 93,188. [Certain, `plant/plant.json`] Its `beliefs.jsonl` and `predictions.jsonl` are hard links the resurrected life appended to. They are contaminated.
- **EVOLVE is inert in the cut.** 2 `proposal` rows on the tape, both `REFUSED`; 0 `epoch` rows among the 86,948 lived mind rows. [Certain]
- **No run of any rule but the law exists.** Every number marked «predicted» in §4 is a prediction.

## 1 · The question
- **The question.** On alpha4-1's own closed tape, does the choice of WHICH 200 episodes are rehearsed at each sleep change how much the creature forgets what it learned early and was not shown again?
- **The comparison.** Four rules, one difference each: S by surprise (the law), U uniform, P protect-the-strong, N none. Same tape, same code, same boundary rule.
- **Two readings it must give.** (1) A RANKING of the rules on retention. (2) Whether the law HARMS against no rehearsal, as it did on the brain's learner.
- **What it is for.** The SLEEP line of the next life (§7).

## 2 · The arms
Each arm is ONE genome text: `code/genome/ALPHA4.genome` (the file `unit.env` ran; sha-256 `a68870a8…`, byte-equal to the root's `GENOME.genome` [Certain]) with the SLEEP line replaced. Nothing else differs.

| arm | the SLEEP line | parses under 7bbc995? |
|---|---|---|
| **S** by surprise (the law) | `SLEEP    every 2500 moments replay 200 by surprise` | yes (it is the line) |
| **U(d)** uniform, d = 1 … 10 | `SLEEP    every 2500 moments replay 200 uniform seed <d>` | no: the branch's parser |
| **P** protect the strong | `SLEEP    every 2500 moments replay 200 strong` | no: the branch's parser |
| **N** none | `SLEEP    every 2500 moments replay 0 by surprise` | **yes**: `replay (\d+)` takes 0 *(seat, 2026-09-29 14:50 +0400: checked under the life's own code; it parses to `{"every": 2500, "replay": 0}`)* |
| **PR** P's own null *(seat, 2026-09-29 14:50 +0400: ADDED, §5.6)* | `SLEEP    every 2500 moments replay 200 balanced seed 1` | no: the branch's parser |

**What every arm keeps.** The boundary rule is the law's: a sleep fires after the canvas at which `org.t` crosses the next multiple of 2,500. At a boundary the mind runs, in order: the replay, `cycle()`, curiosity's `sleep_boundary()`, EVOLVE's adoption point (`creature/mind.py:1495–1542`). A replayed moment is an ordinary `Organism.moment`: HEBB, DELTA, MISFIRE, PRUNE, MERGE, births. The arms differ in ONE thing: the ordered list of episode ids handed to the replay.

**S — the law, unchanged.** The list is `most_surprising(200)`. (§0.1: in the cut this is one fixed set of 200.)

**U(d) — uniform.** At boundary k, drawn once:
1. k = `self._last_sleep_at // every`, read after the loop's `+= every` (the first sleep is k = 1). It derives from `org.t`, so a resume rebuilds it (`mind.py:2831–2833`). `sleep_count` is never used: it is not persisted.
2. L = the ring's live ids, sorted ascending.
3. `rng = numpy.random.default_rng([20260923, d, k])`: the genome's SEED, the line's d, the boundary k. A fresh generator per boundary. No wall clock.
4. The list = `[L[i] for i in rng.choice(len(L), size=min(200, len(L)), replace=False)]`, in draw order.

Two replays of U(d) are byte-identical. U(1) … U(10) are ten draws of one rule.

**P — protect the strong.** T-MEM-1's rule was a GATE on a delta step (k = 8 anchors a strong word). The creature has no projection to gate. The closest REPLAY rule: rehearse the anchors of the words the organism already holds well. It is computed ONCE at the boundary, before any replayed moment, from the organism and the ring only, read-only:
1. For each live episode e with a word: s0 = the alive sight cell with the largest `cos(x_s)`, if that cosine ≥ THETA_N (0.952); w0 = the alive word cell with the largest `cos(x_w)`, if ≥ THETA_N (the words area has no RESONATE line, so it uses THETA_N; `machinery.py:1096–1098`).
2. e is **self-consistent** iff both exist and `Organism._answer_of(sight, s0) == w0`. This is the organism's OWN test of a correctly answered glance, the one THRESH's band uses (`machinery.py:1148–1153`). No `_resonate`, no `moment`: nothing is born, no band is pushed.
3. A word is **STRONG** iff the ring holds ≥ 20 of its episodes and ≥ 0.80 of them are self-consistent. These are CONCLUSION-MEMORY §2's constants, with the creature's recall as the reader and no truth.
4. A word's **anchors** = its self-consistent episodes, newest (largest id) first.
5. **The fill.** Tier 1 = the strong words, ordered by self-consistent count descending, then the word ascending. Take one anchor from each tier-1 word in turn, round after round, until 200 or tier 1 is empty. If slots remain, tier 2 = every other word with a self-consistent episode, same order, same round-robin. If slots still remain, replay what was found.
6. Under P the sleep row adds `strong_words` and `tier2` beside `replayed`.

Measured on the two law-arm states on disk [Certain, `measure/ring.json`]: at seq 51,303 P finds 61 strong words of 120 with ≥ 20 rows and fills 200 in 4 rounds (3–4 anchors a word). Ten of the eleven, moon, tree, house and cup are strong. **Key is not** (350 of its 710 rows self-consistent: the game says «key» over other sights), **nor «dot»** (585 of 798).

**Rejected: the brief's example** (rank every self-consistent episode by its own edge `W[s0, w0]`, take the top 200). At seq 51,303 its 200 fall on 4 words («is» 114, «arrow» 68, «y» 11, «z» 7); at 93,188 on 3. It protects a few saturated memories. T-MEM-1's gate protected EVERY strong word. **Why tier 2:** at the first sleeps few words can have 20 ring rows; without tier 2, P would replay fewer than 200 and its clock would drift from S's (below).

**A limit of P, measured.** STRONG is read on STORED episodes. At seq 51,303 tree is 385 of 398 self-consistent and house 362 of 400, while the held-out exam read tree 0.0 and house 0.2 at the end of w2. [Certain] So P can keep a thing «strong» that no longer generalises. Whether rehearsing the stored episodes restores held-out naming is what the A/B measures.

**PR — P's own null** *(seat, 2026-09-29 14:50 +0400)*. The same fill as P with the STRONG test removed and nothing read from the organism: tier 1 = every word with ≥ 20 live ring episodes, in an order drawn by `default_rng([20260923, 1, k])`; a word's episodes in an order drawn by the same generator; one episode from each word in turn, round after round, until 200; if slots remain, the words with fewer than 20, the same way. PR is word-balanced rehearsal with no «strong» in it. P against PR is what «the strong» adds. *(designer, 2026-09-29 14:53 +0400: buildable as worded, with two things fixed so a builder cannot read it two ways. (1) **The generator is `default_rng([20260923, d, k, 99])`**, d = the line's seed (1), k the boundary as for U. As worded, PR's generator `[20260923, 1, k]` is U(1)'s own generator at every boundary: the null would share its random stream with one of the ten draws it is read against. The trailing 99 is a stream tag no other rule uses. (2) **The order of draws is fixed:** words = the non-empty `word` values of the live ring (sight-only «» excluded, as in P). First `rng.permutation` of the tier-1 words sorted ascending; then, for each tier-1 word in that drawn order, `rng.permutation` of its live ids sorted ascending; then the same two steps for tier 2 (1–19 live episodes), drawn after all of tier 1's; then the round-robin, tier 1 first, until 200. Measured on the law's state at seq 51,303: tier 1 holds 120 words against P's 61 strong ones (`measure/ring.json`), so PR spreads ≈ 1.7 replays a word a sleep where P gives ≈ 3.3. PR is blind to «strong» and, by that, also to how many words are kept; the reader prints both counts at every sleep.)*

**N — none.** `replay 0` parses (`machinery.py:387`). `most_surprising(0)` returns `[]` (`fast.py:186`). The boundary still runs `cycle()`, curiosity and the EVOLVE point; nothing is replayed. **N runs on the life's own code, unchanged.** **Rejected: the line ABSENT.** `_maybe_sleep` then returns at once (`mind.py:1501`). That also removes CYCLE's consolidation pass (57 of 80 sleeps on 09-23 ran it), curiosity's window close and EVOLVE's adoption point: four mechanisms, not one.

**A consequence every reader must hold.** A replayed moment advances `org.t`. So:
- S, U and P replay 200 at every sleep and share one clock: a sleep every 460 canvases (2,300 live moments + 200 replayed; 5 moments a canvas). [Certain by arithmetic; the journal's sleeps sit every ≈ 1,150 rows]
- N sleeps every 500 canvases. Budget regeneration (1 per 60 moments) and SCALE (every 1,250 moments) also tick on replayed moments. These differences ARE «no replay» under this law. They are printed, never removed.
- P keeps S's clock only while it finds 200. Every sleep row prints `replayed`.

## 3 · The runs and the code they run under

### 3.1 The cut
- **The lived cut is the FIRST stop: seq ≤ 93,188.** `journal/2026-09-24.jsonl` line 2,944 is the stop at 2026-09-24T01:00:44.922Z; the mind rows before it end at seq 93,188; `readings/verdict-24h-v4.log` reads «tape head 93652 · STATUS last_seq 93188 · backlog-at-stop 464 · arithmetic 0». The tape's rows 1–93,188 are contiguous. [Certain, `measure/verify_record.json`]
- **`tools/brain/cut_tape.py` must NOT be used on this life.** It cuts at the ledger's `last_seq` (now 119,958) and copies every journal day file (`cut_tape.py:45–46, 74`). Both are wrong here. [Certain]
- **The live journal** = `journal/2026-09-23.jsonl` whole + `journal/2026-09-24.jsonl` lines 1–2,944, mind rows only (`creature.replay.is_mind_row`): 86,948 rows. It equals PASS 1's `readings/verdict-24h-pass1/live-journal.jsonl` row by row. [Certain]
- **The A/B's cut is shorter: seq ≤ 50,094**, the last row before w3's first maker row. It holds w0, w1 and w2 whole: 20,237 canvases, 47,274 mind rows, 43 sleeps, both unshown windows. [Certain] Why not the whole life: §6.4. It lies entirely in the 2026-09-23 day file, so 7bbc995's one-file `run_replay` suffices. The whole cut would not: it crosses into 2026-09-24. [Certain]
- It is a MID-tape cut: no `--closed`. A think launched before the cut lands after it on both sides, so it is absent from both.

### 3.2 Does the tape replay to itself under its own code?
**Yes, over the 12 h cut and past it. Never over the whole life.** [Certain, `measure/verify_record.json`, `pilot/summary.json`]
- **PASS 1's two law-arm replays**, started 2026-09-24 05:01 and killed by the 21:51 reboot, were never compared. They ran the reader pin f018f2c; `git diff --stat 7bbc995 f018f2c -- creature genome` lists only `creature/replay.py` (the two instruments) and one genome file. Compared today with the life's own `compare()`: every mind row with seq < 51,370 (48,439 rows, 45 sleeps) and < 51,542 (48,598 rows) is **identical to the live journal, every field, `hash` included.** The two are identical to each other. 0 torn lines.
- **The compare sees a sleep:** one sleep row's `replayed` planted at 199 is caught at seq 1,271.
- **The pilot** (§6.1): rows 1–6,000 under the life's own checkout, `REPLAY identical`, 5,668 mind rows, 5 sleeps.
- **The 2 h smoke** (reader commit = life commit = 7bbc995): identical over 8,566 mind rows, twice, a plant caught at seq 513. [Certain, `readings/smoke-2h/results.json`]
- **Never done whole.** Rows 51,543–93,188 (hours ≈ 12.5–24) were never replayed. The A/B does not need them.

### 3.3 The code of the arms
- **N runs on the life's own checkout** (`/data/dev/genome-lives/alpha4-1/code`, 7bbc995). Its line parses there.
- **U and P need new code.** It goes on a NEW branch `sleep-ab` cut from 7bbc995, in a NEW worktree (e.g. `/data/dev/genome-wt-sleepab`), never on master (master's `creature/` is the brain organ's; #234 (4)).
- **What the branch carries, and nothing else:**
  1. a17cb0e's `creature/replay.py`, cherry-picked: `--timings` and `--exam-every N`. **At 7bbc995 both flags are SILENT NO-OPS**: `main()` reads only `--genome/--tape/--out/--blind/--closed/--against`. A builder who runs them on the life's checkout gets no timings and no exams, and no error. Between 7bbc995 and a17cb0e only `creature/replay.py`, one genome file and two tools changed. [Certain, `git diff --stat`]
  2. `genome/machinery.py`, the SLEEP branch (lines 386–389): accept `by surprise` | `uniform seed <d>` | `strong`. **The law's declared dict stays `{"every", "replay"}`**: `tests/genome/test_parse_g4.py:106` pins it, and `creature/genes.py:278–286` (EVOLVE's SLEEP.every / SLEEP.replay patterns) reads the text. A new rule adds `"rule"` (and `"seed"`). A misspelt rule refuses by name.
  3. `genome/fast.py`: `Episodes.live_ids()` (the ring's live ids, ascending). Nothing else.
  4. `genome/sleep.py`: `select(org, episodes, n, rule, seed, k) -> List[int]` (S = `most_surprising(n)` unchanged; U and P as §2), and `sleep()` replaying the GIVEN list.
  5. `creature/mind.py:_maybe_sleep`: compute k, call `select` ONCE, hand the SAME list to the `moment_word` pre-record (today line 1515) and to `sleep()`. Today the law calls `most_surprising` twice and is safe only because it reads the ring alone. P reads the organism. The sleep row gains `rule` only when the rule is not surprise.
  6. **The instrument for READ-W0 (§4):** each `--exam-every` sitting also runs `tools/read_recognised.py:recognised_share` on the 275-word list (`--read-list measure/READ-W0-list.txt`: the 224 of READ-W0-out and the 51 of READ-W0-in) and writes each word's answer into the exam JSON. It never touches the mind's road; `recognised_share` asserts the organism's hash unchanged (`tools/read_recognised.py:48`).
- **No pin list at 7bbc995 names any of these files.** [Certain, every `read_bytes()` + `sha256` site read] The pins are `genome/gaze.py` PINS (alpha2 `organs/retina.py`, `organs/gaze.py`), `_RETINA_FAST_PIN` (`genome/retina_fast.py`), `genome/cochlea.py` PINS (E52 `gammatone.py`, `front.py`), `genome/retina_fast.py` RETINA_PIN, and the eye tower's seal (`genome/eye.py:55`). There is no glance cache (`WORLD_CODE`) at 7bbc995, so #245 (1) cannot fire. Tests that read the law and must stay green: `tests/genome/test_parse_g4.py`, `test_sleep.py`, `test_fast.py`, `test_cycle_redundant.py`.
- **Every command:** `/usr/bin/python3 -B` (the life's `code/` already holds `__pycache__`; never add one under the record), `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, `nice -n 10`, `TMPDIR=/data/dev/brain-runs/day0929/tmp`, `PYTHONPATH` = the tree that runs.

### 3.4 The runs
| run | tree | rows | flags | purpose |
|---|---|---|---|---|
| S | branch | ≤ 50,094 | `--exam-every 500 --read-list --timings --against` the live mind rows ≤ 50,094 | identity + S's marks |
| N | branch (its line also runs on 7bbc995) | ≤ 50,094 | `--exam-every 500 --read-list --timings` | the floor |
| P | branch | ≤ 50,094 | same | protect the strong |
| U(1) … U(10) | branch | ≤ 50,094 | same | ten draws |
| PR | branch | ≤ 50,094 | same | P's own null *(seat, 2026-09-29 14:50 +0400)* |
| S′ planted | branch, `replay 199` | ≤ 2,000 | `--against` | must DIVERGE at seq 1,271 |
| U(1) twice | branch | ≤ 6,000 | — | determinism |

**The sittings.** `--exam-every 500` sits after every 500th eye row, the live life's own cadence (`EXAM every 500 canvases`). In the cut that is 40 sittings: 13 in w0, 14 in w1, 13 in w2. The last sitting of each window is at seq 16,198, 33,505 and 49,524. [Certain, `measure/shelf_words.json`]

## 4 · The marks
**A window's LEVEL** for a thing = the mean of its Q1 over the window's LAST THREE sittings. Never one sitting (#240): the live series swings by up to 0.4 inside a window (circle 0.6–1.0).

| id | the mark | n (counted) | ceiling | bar | reachable? | failable? |
|---|---|---|---|---|---|---|
| **R-B** | the five arrivals: level at the end of w2 (unshown) − level at the end of w1 (learned) | **5 things** (50 answers that move by thing) | 0 (no loss); the floor is −(end-w1 level), −0.993 under S | **none: UNDERPOWERED** (5 < 30). A reading. | yes: S lost 0.553 | yes: 3 of 5 things lost under S |
| **R-A** | the eight: level at the end of w1 − level at the end of w0 | **8 things** | 0; floor −0.975 under S | **none: UNDERPOWERED** (8 < 30) | yes: S lost 0.083 | yes: 4 of 8 fell 0.13–0.20 under S |
| **BWT-t** | per thing (13 rows), the same difference; arm − S paired by thing | **13 things** | 0 each | **none: UNDERPOWERED** (13 < 30). A 13-row table. | yes | yes |
| **SER** | the composite (16 words) as a series: OLS slope per 1,000 tape rows over each unshown window's sittings, ± SE, with lag-1 autocorrelation and n_eff beside it | **13 / 14 sittings a window**; the live w2 read −0.0037 ± 0.0010 (n 18, lag-1 0.02, n_eff 17.2) | — | **none: UNDERPOWERED** (n < 30) | yes | yes |
| **READ-W0-out** | shelf words whose EVERY hearing inside the cut falls at or before the last w0 sitting (seq 16,198), minus the 51 that have an episode in the law's fixed replay set: recognised at the cut's last sitting (seq 49,524), by the life's own READ probe (one render in the held-out font) | **224 words** (`measure/READ-W0-out-list.txt`) | the arm's own end-w0 share; the live «last 20 heard» share in w0 read 0.10–0.65, mean 0.44 (18 sittings, `exam/*.json` `read_share`) | **the ONE bar** (§7), **GRADABLE only if ≥ 30 of the 224 are recognised at the end-w0 sitting under S** | unknown before S runs: no per-word probe exists on the record before 24 h | yes: a word not recognised at the end fails it |
| **READ-W0-in** | the same, on the 51 words the law rehearses at all 43 sleeps by construction | **51 words** (`measure/READ-W0-in-list.txt`) | as above | **none: a reading.** Its winner is set by construction (#228): the law replays them, the others barely | yes | yes |

**Why the bar leaves the 51 out.** The law's fixed set is known now (§0.1). A bar the law wins by its own construction cannot be failed by it. The 224 are words no rule rehearses by design: U draws each word's episodes ≈ 1.8 times over the cut (the median over all 275), P almost never (1 of the 275 reaches 20 episodes; `measure/read_w0_counts.json`), S and N never. So the 224 read two things: whether light uniform rehearsal keeps early material, and whether the law's heavy rehearsal of its 200 HURTS the rest (S below N).

**How READ-W0-out compares two arms.** Paired by word: b = words X recognises at the end and Y does not, c = the reverse. z = (b − c) / √(b + c). Printed beside it: b + c, and the smallest gap the n can pass (2·√(b + c)) (#245 (5)). Each arm's end-w0 share is printed. If two arms' end-w0 shares differ by more than 2 binomial SE, the end-cut difference is read as acquisition plus retention, and each arm's own retention (recognised at the end among those recognised at end-w0) is printed beside it.

**Predicted, before any run.** S's column is the live record (the replay is the life, §3.2). The rest are [Guessing] unless tagged.

| mark | S (the law) | N (none) | U (uniform, 10 draws) | P (protect the strong) |
|---|---|---|---|---|
| R-B, the five | −0.553 (key, tree, house lost) [Certain, live] | ≈ S: the law's fixed set holds 0 arrival episodes, so S rehearses none of them [Likely] | better than S: ≈ 3.5–4.1 episodes of each arrival a sleep (the ring's share at seq 51,303) | better than S on tree and house (strong: 3–4 anchors a sleep); key unprotected (not strong) |
| R-A, the eight | −0.083 [Certain, live] | worse than S [Guessing]: S's fixed set holds 29 episodes of the eight [Certain, `measure/law_set.json`] | ≈ S (≈ 5 of each a sleep) | ≈ S (all eight strong at seq 51,303) |
| READ-W0-out (224) | ≈ N, or below N if its 200 interfere | the floor | slightly above N: a list word's episodes are drawn ≈ 1.8 times over the cut (median; mean 2.8, range 0.5–25) [Certain as expectation, `measure/law_set.json`] | ≈ N |
| READ-W0-in (51) | best: it replays them 43 times | below S | below S | below S |
| SER, w2 | −0.0037 / 1,000 rows [Certain, live] | ≈ S | flatter than S | flatter than S |

## 5 · The controls
Each control is blind to ONE thing, and each says what it must still be able to do (#228's fifth gate).

1. **IDENTITY (the law against the life).** S on the branch, cut at 50,094, `--against` the live mind rows with seq ≤ 50,094 → «REPLAY identical», every field, `hash` included. It proves the branch changed nothing for the law. It runs WITH `--exam-every 500` and `--read-list`, so it also re-proves a17cb0e's pin (an exam never changes him) on this tape.
   - **Its planted twin:** S′ with `replay 199` must DIVERGE, first at seq 1,271 (the first sleep row). The same plant on the record was caught today (§3.2).
   - **If S cannot reproduce the live journal,** the A/B has no identity control. What replaces it: S on the branch against S on 7bbc995 (the same-code baseline, #234 (4)), both over the cut, must be identical; the live exams then are NOT S's readings, and every S figure of §4 is read from the replay only.
2. **DETERMINISM.** U(1) twice on the first 6,000 rows: byte-identical journals.
3. **THE WORLD'S POSITIVE CONTROL: forgetting exists here.** Already on the record under the law: key, tree and house lost in w2 (§0.4). The A/B needs more: **N must forget, or S and N must differ.** If N loses at most one of the 13 things («lost» as §7 defines it) AND N's READ-W0-out end share is within 2 binomial SE of its own end-w0 share, replay has nothing to restore here, and §7 reads «this world cannot tell», unless S forgets MORE than N (the T-MEM-1 direction, a finding).
4. **THE MARK'S POSITIVE CONTROL: a plant on a COPY — RUN TODAY, PASSED.** [Certain, `plant/`] Two scratch copies of the closed end state (seq 93,188). In one, every `W` and `mask` entry from any sight cell into the word cells of «moon» and «cup» (cells 603, 606; 104 edges) was set to 0 and saved. The life's own exam (`tools/self_exam.py --check-tape 0`) sat on both:
   - unplanted: Q1 all 0.9375; per thing equal to the live sitting at seq 92,953 except diamond (0.8 against 0.7, 235 rows later);
   - planted: **moon 0.0 and cup 0.0**; the other 14 things IDENTICAL to the unplanted copy; Q1 all 0.8125; `noedge` abstentions 11 against 2;
   - both: `organism_hash_unchanged_by_exam` true; 34.3 s and 32.5 s a sitting at 9,172 alive sight cells, on a crowded box.
   So the exam sees a lost association in THIS organism at its largest, thing by thing.
5. **U IS A DISTRIBUTION.** Ten draws, d = 1 … 10, printed as a band (min, max, mean). S, P and N are read against the band, never against one draw (#244 (2)).
6. **P's own null, PR.** The same round-robin over RANDOM words with ≥ 20 ring rows, their episodes drawn at random (§2). Without it, a P win cannot be split into «the strong» against «word-balanced rehearsal». (T-MEM-1's GATE beat GATE-RANDOM at 1 of 3 seeds.) *(seat, 2026-09-29 14:50 +0400: the draft left it «not run»; it RUNS. With lever H it costs about 1 CPU-h, and a control blind to exactly one thing is what P's claim needs (#228's fifth gate). It is ONE draw: a P win over PR is read against U's ten-draw band for its size.)*

## 6 · The price

### 6.1 The pilot
[Certain, `pilot/summary.json`, `pilot/pilot.log`, `measure/price.json`]
- **What ran.** The law arm's replay of the cut tape's first 6,000 rows (2,381 canvases, 5 sleeps) under the life's own checkout (7bbc995). One process. `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, `nice -n 10`, `python3 -B`, cwd the pilot folder.
- **How.** `--timings` does not exist at 7bbc995 (§3.3). So the pilot is `scripts/pilot_driver.py`: 7bbc995's own `run_replay` (the same Mind, a fresh temp root, the payload symlinked, sort by seq, the mind-row filter, `compare`) plus a `perf_counter` / `process_time` around each `mind.consume(row)`, which is a17cb0e's instrument. No `mind.close()`.
- **Identity:** `REPLAY identical`, 5,668 mind rows against the live rows ≤ 6,000.
- **Cost:** 377.6 s wall · **332.3 CPU-s** (329.1 user + 3.2 sys) · max RSS 381 MB · 0.140 CPU-s a canvas on average. The eye rows carry 331.8 s; every other sense 0.3 s. The heaviest 2 % of rows (the sleeps and the snapshots, every 100 canvases) carry 104.8 s.
- **The load beside it:** before 14.06 / 5.46 / 3.08 (1 / 5 / 15 min), 25 python3 processes; after 16.56 / 14.45 / 8.21, 22. The word road's gate entered its phase 2 at 14:19:26 (19 processes at nice 10). **The pilot ran on a CROWDED box.**
- **The crowding, measured on the same rows.** The reader's solo probe replayed these first 1,000 rows alone at 21.0 ms a canvas (wall, 2026-09-23, `readings/smoke-2h.log`) and 22.25 ms (2026-09-24). The pilot read 59.8 ms wall and 40.3 ms CPU a canvas there. So crowding inflated wall ×2.7–2.8 and **CPU ×1.8–1.9** (#242).

### 6.2 From 6,000 rows to an arm
- **The model.** A canvas costs c0 + H × (2 × (a·n_s·n_w + b·L)): the state hash, run twice a canvas, over the live W block (n_s × n_w born cells) and the four logs (L entries). a and b come from the ladder designer's M1 on alpha4-1's own state (168 ms a call = 142.6 ms at 6,229 × 687 born + 22.0 ms at 59,893 log entries; `A4-LADDER-PREREG.md` §6). n_s, n_w and L are read row by row from the live journal. c0 and H are fitted on the pilot's canvases (the heaviest 2 % left out): **c0 = 40.3 ms, H = 2.16.** [Certain as computed; the extrapolation is Likely]
- **At the cut** (seq 50,094; born 11,056 × 1,186): the hash is 0.97 s a canvas at M1's scale. Summed over the arm, it is ≈ 80 % of the replay's cost.
- **Three readings of one 12 h arm (replay only):** 5.5 CPU-h at the pilot's crowding (fitted H); 2.8 at M1's absolute scale; ≈ 3.0 as the crowded figure ÷ 1.87. [Likely]
- **The cross-check on this very tape.** PASS 1's two replays reached seq 51,370 and 51,542 in 6.77 h of running each (wall, BLAS at 1 thread, nice 5, a busy box; `readings/verdict-24h-v4.log`, `readings/verdict-waiter-v4.sh:12`). So those rows cost ≤ 6.8 CPU-h. The model says 5.9 crowded / 3.0 at M1's scale for the same rows. Consistent. [Certain bound; Likely model]
- **What the linear model leaves out** [Likely]: CYCLE's merge grows as alive² (≈ 30 s a sleep at 4,100 sight cells, ALPHA4-PREREG §12c (4)); snapshots grow with the state. + ≈ 0.4 CPU-h an arm.
- **Beside the replay** [Likely]: 40 sittings at 2.6–37 s each (the live `seconds` field at 530 → 6,031 alive sight cells; 32–34 s at 9,172 on today's plant) ≈ 0.2 CPU-h; the READ-W0 list (275 renders a sitting) ≈ 0.05; P's selection (20,000 × n_s cosines a sleep, 43 sleeps) ≈ 0.1–0.2.

### 6.3 One arm, and the whole A/B
| design | one arm, solo-equivalent | one arm, crowded like the pilot | arms | the whole A/B, solo-equivalent |
|---|---|---|---|---|
| **the whole lived life** (≤ 93,188) | ≈ 13–14 CPU-h (model 12.5 at M1's scale; 26.0 ÷ 1.87) | ≈ 26 (ALPHA4-PREREG §12c: ≈ 28) | 13 | ≈ 180 CPU-h — **over the 6 CPU-h line** |
| **the 12 h cut (PROPOSED)** (≤ 50,094) | **≈ 3.5 CPU-h** (≈ 3.0 replay + 0.4 CYCLE/snapshots + 0.2 exams + P's selection) | ≈ 6 | 13 (S, N, P, U × 10) | **≈ 45 CPU-h** |
| the 12 h cut, U × 5 | ≈ 3.5 | ≈ 6 | 8 | ≈ 28 CPU-h |
| the 12 h cut, **lever H** (see below) | S ≈ 3.5; N, P, U ≈ 1.0 | — | 13 | ≈ 15 CPU-h |
| + P's own null (§5.6) | ≈ 3.5 | ≈ 6 | +1 | + 3.5 |
| + controls (S′ to 2,000 rows; U(1) twice to 6,000) | — | — | — | + ≈ 0.2 |

- **THE SEAT'S CHOICES** *(Claude (Fable 5.1), 2026-09-29 14:50 +0400)*: (1) **the 12 h cut**, as proposed; (2) **U × 10**; (3) **PR runs**; (4) **lever H is TAKEN for N, P, PR and every U**: S keeps its hash (identity needs it). So 14 arms: S ≈ 3.5 CPU-h and thirteen at ≈ 1.0, ≈ 17 CPU-h solo-equivalent. (5) **The launch shape:** the arms start only after the word road's gate has ended and no suite runs; each arm is its own user unit (`systemd-run --user`, BLAS threads 1, nice 10), so it outlives the session; at most 14 at once on the 16 threads. (6) **The price is re-measured in THAT shape** (#242): each arm's own `timings.jsonl` gives its CPU; the report prints the load beside it. No mark here reads a cost, so crowding moves the wall clock and nothing else. *(designer, 2026-09-29 14:53 +0400: two corrections, no choice changed. (a) a17cb0e's `timings.jsonl` carries WALL ms per row only (`creature/replay.py` at a17cb0e: `"ms"` from `perf_counter`); it gives no CPU. So the branch adds `cpu_ms` (`time.process_time`, the pilot driver's own instrument) to each timings row, an instrument outside the mind's road; the reader sums it per arm. A unit's `CPUUsageNSec` is lost when `--collect` removes the unit, so it is not the source. (b) Memory, beside the threads: the pilot's replay held 381 MB at seq 6,000; the live body's own row read 1,598 MB at seq 51,370 (body and senses included; the replayed twin's copy of it). Fourteen arms at the cut are therefore ≈ 6–22 GB against 27 GB available at 14:52 [Likely]. The launch prints `free -g` beside `/proc/loadavg`, and each unit's `MemoryCurrent` is read at 10 minutes.)*
- **At 4 arms at a time** on this 16-thread box, 45 CPU-h is ≈ 12 h of wall before crowding, ≈ 15–20 h with it (#236, #242). The price is for THAT shape only if it is re-measured in it. [Likely]
- **Lever H (the seat's choice, not in the arms' definition).** The per-row state hash is output only; nothing in the mind reads it. The arms U, P and N do not need it: they are compared by their marks, never by journal identity. A replay-only switch in `creature/mind.py` that writes `"hash": null` on mind rows cuts each of them to ≈ 1.0 CPU-h (the canvas work, CYCLE, the snapshots, the exams and P's selection remain). Its cost: one more file on the branch, outside the SLEEP rule. Its proof: U(1) over the first 6,000 rows with and without the switch, journals identical except `hash`; S always runs with the hash (identity). The snapshot's own digest stays (the exam's load gate).

### 6.4 The shorter design, and what it cannot settle
- **The whole life costs ≈ 13–14 CPU-h an arm solo, ≈ 26 crowded: over the 6 CPU-h line.** So the proposal is the **first 12 h (seq ≤ 50,094)**: windows 0–2, both unshown windows once, all 40 sittings, the law's identity proven on the record already (§3.2).
- **The 8 h cut (≤ 33,827) was rejected.** It would cost ≈ 1.5 CPU-h an arm, but it holds only R-A (the eight; the law lost 0.083 there). It drops R-B, the life's clearest forgetting (the law lost 0.553).
- **What 12 h cannot settle:**
  - windows 3–5: the eleven's second and third absences, the arrivals' second absence (the law lost only 0.26 there, key heard 4 times), and the plant «zog» (hour ≈ 21);
  - **the law after the ring wraps.** From the 20,000th canvas on, the law's set MOVES (§0.1): it rehearses what is about to fall off the ring. The cut tests only the frozen-set regime;
  - cost and growth at 20,000 cells;
  - identity of rows 51,543–93,188.

## 7 · The decision rule
Nothing is read until IDENTITY (§5.1) and its planted twin have passed. If either fails, the A/B is VOID and says which. Then: **the SLEEP line of the next life CHANGES to rule X (P or U)** when READ-W0-out is gradable and X recognises more of the 224 than S at the cut's end by z ≥ 2 (for U: the ten draws' mean does, and ≥ 8 of the 10 draws each beat S), AND X loses no more of the 13 maker things than S does plus one (a thing is «lost» when its level at the end of its unshown window is ≤ 0.2 after ≥ 0.8 at the end of its learning window); if both P and U qualify, P is taken only if it also beats U's mean by z ≥ 2 AND beats PR, its own null, by z ≥ 2 *(seat, 2026-09-29 14:50 +0400: the PR clause added; a P that does not beat PR is word-balanced rehearsal, and U is the simpler rule that has it)*, else U, the simpler rule. **The line CHANGES to `replay 0`** when S recognises fewer of the 224 than N by z ≥ 2 and neither P nor U beats N: the law's rehearsal only harms here. **The line is KEPT** when no rule clears those bars and S is not worse than N by z ≥ 2 nor by more than one lost thing. **«This world cannot tell»** is the reading when N forgets nothing measurable (§5.3) and S does not differ from N; or when READ-W0-out is UNDERPOWERED (fewer than 30 of the 224 recognised by S at the end-w0 sitting) and the maker readings of S, P and N all lie inside U's ten-draw band. The maker marks never change the line alone: they are UNDERPOWERED (13 things). They can only VETO a change (the «plus one» clause). READ-W0-in, SER and each arm's CPU are printed beside the verdict; they decide nothing.

## 8 · What this does not claim
- **It is not a life.** The tape is the law arm's world. The game frames followed the LAW's acts. The `sit` rows return the LAW's exam scores to every arm as a sense (the reflex ring). The door answers answer the LAW's questions. An arm is «what this mind learns from this stream», never «what it would have lived».
- **It is 12 hours of a 24-hour life** (§6.4).
- **It tests the creature's cells, not the brain organ.** A result here does not transfer to T-MEM-1's learner, or back.
- **It tests the SELECTION of 200.** Not the dose (200), not the cadence (2,500), not CYCLE (it runs in every arm), not replay's other roles.
- **The maker marks are underpowered.** 13 things. They are readings.
- **READ-W0-out reads one forgetting road.** Its words were never heard again inside the cut, so it sees sight-side loss only. The arrivals' loss rode on words that kept being heard (§0.4). The two roads can rank the rules differently. That is a finding, not a flaw, and §7 lets the maker readings veto.
- **The law's win on its own 51 words is a property of the frozen set** (§0.1), which ends when the ring wraps. It is printed, never read as the law's merit in a longer life.
- **P is one definition of «protect the strong».** Its STRONG test reads stored episodes (§2). It is not T-MEM-1's gate.
- **Nothing here reads the on-disk `state/`.** It is the resurrected organism.
- *(seat)* **One fact stands whatever the A/B reads:** for its first 12 hours the law rehearsed ONE fixed set of 200 episodes, the first ≈ 15 minutes of the life, at every sleep (§0.1). The seat checked its two causes under the life's own code: the stored surprise is never updated, and ties go to the smaller id. That is reported to him as a finding of its own.

SIGNED:
- Opus 5.5 (the designer) — 2026-09-29 14:53 +0400: RENEWED on the text as of this commit (the seat's marked choices of 14:50 read and checked against my measurements; two designer notes added: PR's generator and draw order, §2; the CPU source and the memory of fourteen arms, §6.3); every [Certain] figure was read from the file named beside it or measured by the scripts under `/data/dev/brain-runs/day0929/sleep-ab/`. Superseded: my 14:40 +0400 signature, on the text before the seat's choices.
- Claude (Fable 5.1, the seat) — *(signs after the designer renews on the text with the seat's notes)*
