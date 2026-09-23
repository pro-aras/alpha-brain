# JUDGE-UNITS-0923: the READINESS judge in its own units (builder report)
Written by Claude (Opus 5.5, judge builder), 2026-09-23 11:53 +0400. Branch `judge-units-0923` (worktree `/data/dev/genome-wt-judge`, from master 867e8bc), commits listed in §5. **HELD: not merged.** Law: `docs/ALPHA4-PREREG.md` §4 (amended in place, dated, the old words struck) and §11 finding 1. Evidence: `docs/reviews/ALPHA4-1-FIRST-HOURS-REVIEW.md` §3.
**Status:** every change RED on 867e8bc and GREEN here (the final judge tests: 12 failures + 19 errors on 867e8bc; 48/48 OK here with the integration seams). Negative control PASS: the hour-1 fixture's journal is byte-identical outside `readiness` (4,318 rows raw + 4 masked, of 4,322), both planted controls CAUGHT. Creature suite `Ran 738 … OK (skipped=1)`. Genome suite `Ran 360 … FAILED (failures=1, …)`: that one failure is a stale pin, identical on master 867e8bc and not this branch's (§3). gate_g4 1/2/3/6 PASS. Found beyond the brief: the old (b) read an input no snapshot persists (§1), and the amended read sample likely reads LOWER than the struck one (§0.3). Code at 56b08dc; this report in the commits after it.

## 0 · What is NOT done, and why (read first)
1. **Not merged, not pushed.** By rule: the ladder's landing control (A4-LADDER-PREREG §1.6) needs master unmoved until 22:00. The orchestrator merges after the cutoff; `alpha4-2` carries it. `alpha4-1` lives its 24 h under the struck words; its door cannot open (§11 finding 1).
2. **Nothing was run, replayed or written under `alpha4-1`.** One disclosed read under `/data/dev/genome-lives/`: the creature suite's pre-existing seam test `tests/creature/test_alpha4_seams.py::TheReadingShareIsATapeFact::test_self_exam_reports_read_share_on_a_closed_root` copies `state/`, `tape/` and `exam/` of the CLOSED dry life `/data/dev/genome-lives/dry-life-1` (not alpha4-1) into a temp dir on every run. It ran twice today (`scratch/logs/green-judge-files.log` and the creature suite), read-only; nothing was written there. I did not edit it, because master's suite must stay comparable. That is the ONLY path under genome-lives either required suite touches (a grep of every absolute `/data/` path in `tests/creature` and `tests/genome`). The suites also read closed records under `/data/dev/genome/` (`run-g4-life1/2/3a-…`, `runs/g4-verdict-life2-…`) and the libraries, all pre-existing reads, nothing written.
3. **The 50-word seeded read sample is proven on toys and plumbing, not on a real `HEARD.json`.** No fixture carries `read/HEARD.json`: the hour-1 fixture has no `read/` directory, and the snapshot fixture is `state/` only. The sampler's determinism, its coverage of the oldest words and its fail-closed branch are unit-tested. The whole `self_exam` road with the new sampler ran end to end only on dry-life-1's 5 fabricated heard words (the seam test above, `--read-words 5`, default seed 20260923). **What was measured instead, on a COPY of alpha4-1's hour-6 snapshot** (`scratch/fixtures/alpha4-1-snapshot`, moment 55,200; `scratch/read_cost_probe.py`, log `scratch/logs/read-cost-probe.log`):
   - **Cost:** `recognised_share` over 20 words took 1.06–1.08 s and over 50 words 1.35–1.47 s, the organism load included. That is ≈ 13 ms per extra word, under half a second per sitting (one sitting every ≈ 400 canvases) [Certain for this box].
   - **The reading [Likely; one snapshot, two samples, n = 20/50].** Old shelf words: the 255 distinct words the shelf read aloud in hour 1 (the fixture tape's own shelf ear rows) are answered 0.05 (that hour's last 20; 1 right, 5 abstained) and 0.16 (a seeded 50 of them; 8 right, 16 abstained). Recent words: the newest 20 words of the snapshot's own ledger (every source, mostly the shelf by hour 6) read 0.55. The proxy's own kind of comparator is the review's §3 series: the live sitter's REAL newest-20 shelf words read mean 0.42 (median 0.45, range 0.10–0.65, 23 sittings). So the amended proxy, a sample over ALL heard words, will most likely read LOWER than the struck newest-20 one, not higher. The review's premise (the newest words are the least exposed, hence the hardest) does not hold on this snapshot: old words fade from the reading. The mechanism is not established here (candidates: displacement by the shelf's later error births; the ear's 8-letter cut against the full rendered word; lines against one-word renders).
   - **The consequence:** (b)'s read half is likely to be the clause that keeps alpha4-2's door shut. The bar stays 0.6, never loosened. Before alpha4-2, this is worth reading on alpha4-1's CLOSED record (its real `read/HEARD.json`, after its stop).
   - **Not the proxy:** the same probe's 50-word stand-in over ALL ledger words read 0.10. It mixes maker, folder and game names that were never seen as rendered text, so it is printed in the log and not used.
   - **A small ceiling, not filtered:** a sampled word may have been heard after the snapshot the sitter reads. The review measured 10 of 460 tested words (≈ 2 %) for the old newest-20 proxy, whose words were exactly the newest; a uniform sample over all heard words is less exposed.
4. **(a) stays shut for any policy like alpha4-1's.** This fixes the judge's units, not the creature's policy: §11 finding 2 (the `left` lock) is its own road (a toy first, then the A4L-EXPLORE rung). Under the amended clause, alpha4-1's record reads 1 success in its first 10 episodes (0.1 per episode) against a bound of 10 of 20.
5. **Found on the way, not touched (outside the judge):**
   - MOUTH says frames from `Mind._frames`, which no snapshot persists, so a resumed mind's mouth has nothing to say until THINK files again. It is the same gap the old (b) had (§1, the purity guard's finding).
   - §5 WEB's text still says «the four readings» (§4 now says five).
   - A snapshot written by the OLD code resumes under this code with an empty (a) window: the per-act `game_rewards` is in other units and is never converted. This is moot for alpha4-2, a fresh life.
6. **Registers.** The PENDING row and any SOLUTIONS entry are the orchestrator's. This branch journals the law change only in the PREREG itself (D-A4-J1, under the 2026-09-05 delegation, his to overturn).
7. **«Both suites green» is not met, by one failure that is master's.** The genome suite reads `FAILED (failures=1)`. The failure is `test_read_lexicon_parser`'s stale pin of the reader's cadence (5 s / 8 words against the deployed 20 s / 4), identical on 867e8bc (§3). It is not fixed here: it is another builder's pin, outside the judge, and the ladder watches master. The one-line fix is named in §3. For the orchestrator: `tools/gate_g5_landing.sh` runs both suites, so every landing today trips on this same pin (master has been red on it since 7bbc995, 04:57) unless the two-number fix lands first.

## 1 · The changes, each RED → GREEN
The final test bytes were run twice:
- against the unamended code, in a detached worktree at 867e8bc (`scratch/ctl-867e8bc`, the three test files copied in, then removed): `scratch/logs/red-final-on-867e8bc.log`;
- on the branch: `scratch/logs/green-judge-files.log`.

Row builders are in the LANDED shapes, read off the hour-1 fixture's tape and the code that writes them: `tests/creature/readiness_rows.py`, shared by both test files.

| clause | change (code) | test | RED on 867e8bc (the log's own line) | branch |
|---|---|---|---|---|
| (a) units | success per COMPLETED episode. The terminal outcome row's own `terminated`/`truncated` ends an episode, and its own `got` > 0 makes it a success. Window: the last 20 mind-chosen episodes. `ok` iff n == 20 and successes ≥ `binomial_bound(20, 0.29, 0.05)` = **10** (P = 0.0385; 9 gives 0.0948). A republished terminal row, same (episode, step), counts once. Code: `creature/mind.py` `READY_A_*`, `binomial_bound`, `_consume_outcome` | `test_ten_of_twenty_opens_a_per_episode_where_the_per_act_mean_never_could` | `AssertionError: False is not True : 10 of the last 20 episodes succeeded (the bound is 10); (a) read False` (the same history's per-act mean ≈ 0.009 < 0.35) | ok |
| (a) | the bound computed, never typed | `test_the_bound_is_computed_from_the_null_never_typed` | `AttributeError: module 'creature.mind' has no attribute 'binomial_bound'` | ok |
| (a) | window full / last 20 only / unfinished episode / schedule-chosen / republished row | 5 tests | `TypeError: 'bool' object is not subscriptable` (no numbers on the old row) | ok |
| (a) | 5 of 20 and 9 of 20 read False | 2 GUARDS | pass on both trees | ok |
| (b) frames | alive = `find_frames` over the FAST ring NOW, each lift ≥ 2.0. `self._frames` is no longer read. Code: `_frames_alive` | `test_a_frame_whose_evidence_left_the_ring_no_longer_blocks` | `AssertionError: False is not True : three frames are alive in the ring; (b) read False` | ok |
| (b) frames | only 2 alive blocks | GUARD | passes on both | ok |
| (b) read | a fixed-seed sample of 50 over ALL heard words, first-heard order; fewer than 50 heard gives `[]`, so the share is None and the clause fails closed. Code: `tools/self_exam.py:read_sample`, `--read-seed` | `test_the_read_sample_is_seeded_over_all_heard_words` | `AttributeError: module 'tools.self_exam' has no attribute 'read_sample'` | ok |
| (b) read | the sitter's argv: `--read-words 50 --read-seed 20260923`. Code: `creature/exam.py` `READ_WORDS`/`READ_SEED` | `test_the_sitter_asks_for_fifty_seeded_words_not_the_newest_twenty` | `AssertionError: '20' != '50'` | ok |
| (d) path | §4 names `$ROOT/ask/graded/<id>.json`; the old path is kept only inside `~~…~~` | `test_prereg_section_4_names_the_path_the_sense_reads` | `AssertionError: 'ask/graded/<id>.json' not found in "## 4 · …"` | ok |
| (d) path | the grade sense reads that directory | GUARD | passes on both | ok |
| numbers | every row: a {window, n, successes, bound, null, ok} · b {frames_alive, lifts (top 3), read_share_last2, frames_ok, read_ok, ok} · c {composite_last2, q1_last2, ok} · d {answered, right, novel_window_n, novel_right, ok} · e {hold, ok}. `b_read_proxy` is gone | `test_every_readiness_row_carries_its_numbers` | `AssertionError: Items in the first set but not the second:` (`b_read_proxy`; booleans) | ok |
| streak | the door opens on ONE reading whose five `ok` are all True; the stage event carries the same five blocks; `_stage_ready_streak` is gone. Every clause passes on BOTH trees in this test's history (one-step successes clear even the old per-act bar; the frames are filed AND in the ring), so on the old tree the streak alone keeps the door shut | `test_the_door_opens_on_the_first_reading_where_all_five_hold` | `AssertionError: 1 != 4 : all five clauses hold on this ONE reading — the door opens now` | ok |
| streak | never undone, never a second event | `test_once_open_never_undone_and_never_reopened` | `AssertionError: 1 != 4` | ok |
| purity | a pure function of tape facts and the mind's own counters | `test_reading_twice_changes_nothing` (GUARD) | passes on both | ok |
| purity | two minds, one tape, the same rows | `test_two_minds_given_the_same_rows_write_the_same_readiness_rows` | `AssertionError: 4 != 5` (the count only; the old streak opens one sitting after the history ends) | ok |
| purity | a resume mid-history reads what an unbroken mind reads | `test_a_resume_mid_history_reads_the_rows_an_unbroken_mind_reads` | `Lists differ: … 'b': True … != … 'b': False …` **(a defect the review did not name: the old (b) read the FILED frames, `Mind._frames`, which no snapshot persists — a resumed mind or an EVOLVE twin restored from a checkpoint read (b) against an empty set)** | ok |

**Builder I's `tests/creature/test_readiness_judge.py`** was rewritten under the amended law, on the landed rows. The reason is #238's shape: its per-act outcome rows complete no episode, so under the amended judge every «condition removed alone» test would have blocked on (a) ALONE and passed for the wrong reason. Measured before the rewrite: `Ran 21 … FAILED (failures=4)`, and all ten removal tests read ok. After the rewrite:
- the passing case is the positive control;
- every removal test asserts that its own clause is the ONLY `ok: False` on the last reading;
- the stage event is read by `["ok"]`: builder I's `all(readings.values())` passes vacuously on dicts.

On 867e8bc it reads 15 RED of 21; on the branch 21/21.

**Totals.** RED run on 867e8bc with the final bytes: `Ran 42 tests in 2.599s` / `FAILED (failures=12, errors=19)`. The 11 that pass there are the guards and the unchanged grade/hold/filter tests. On the branch, the three judge files together (units + judge + the integration seams): `Ran 48 tests in 5.912s` / `OK`.

## 2 · The negative control: the hour-1 fixture replayed under 867e8bc and under the branch
**Setup.**
- The replay: `python3 -m creature.replay --genome <fixture>/GENOME.genome --tape <fixture>/tape/2026-09-23.jsonl --out DIR`, run from the tree under test: 867e8bc in a detached worktree (`scratch/ctl-867e8bc`), the branch in its own.
- The fixture was copied under `scratch/fixtures/` (`cp -r` from `/data/dev/a4-ladder/fixtures/alpha4-1-hour1`). Its genome is byte-identical to master's `genome/ALPHA4.genome`, so STAGE_READY is declared and every sitting writes a readiness row.
- The tape: 4,581 rows — 1,818 eye, 146 outcome (120 game, of which one completed episode, truncated at step 64), 4 sit.
- The runs took 104 s and 106 s, one after the other, with `nice -n 19`, thread caps of 1, at load ≈ 6.
- The control worktree was removed after use (`git worktree remove`, 12:1x +0400), so no unbriefed checkout stays registered in `/data/dev/genome/.git`. Both journals and every log stay under `scratch/` (`scratch/replay-ctl-867e8bc/journal.jsonl`, `scratch/replay-judge/journal.jsonl`), and the control is re-creatable with `git worktree add --detach <dir> 867e8bc`.

The differ is `scratch/negctl_diff.py`; its log is `scratch/logs/negctl.log`, verbatim:
```
rows: 867e8bc 4322 · branch 4322
byte comparison: 4318 rows identical byte for byte; 4 readiness rows identical outside the `readiness` field; first difference: None
compare(ignore=('readiness',)): None
control 1 — compare() UNMASKED: (1029, 'readiness') · the first sit row's seq: 1029 → CAUGHT exactly there
control 2 — planted hash flip at row 1 (seq 3): byte comparison first difference (1, 3); compare → (3, 'hash') → CAUGHT
stage events: 867e8bc 0 · branch 0
NEGATIVE CONTROL: PASS
```
**What it proves.** Nothing in the mind moved except the readiness rows. Every other row of the hour is the same bytes under both trees. By kind (the branch's journal): moment 3,636 · think 181 · outcome 146 · act 121 · smell 120 · body 60 · touch 26 · say 13 · question 11 · sit 4 · sleep 3 · hold 1.

**The two controls.**
- Control 1 shows the instrument sees the change it masks, and at the right place: the first sitting.
- Control 2 shows it sees a change it must NOT mask: a one-character flip of a moment row's `hash`.

The same sitting (seq 3840, the fourth), side by side:
- 867e8bc: `{"a": false, "b": false, "c": false, "d": false, "e": true, "b_read_proxy": false}`
- branch: `{"a": {"window": 20, "n": 1, "successes": 0, "bound": 10, "null": 0.29, "ok": false}, "b": {"frames_alive": 3, "lifts": [{"frame": "purple|ball", "lift": 6.75}, {"frame": "red|box", "lift": 3.7385}, {"frame": "in|the", "lift": 2.6286}], "read_share_last2": [0.35, 0.1], "frames_ok": true, "read_ok": false, "ok": false}, "c": {"composite_last2": [0.8909090909090909, 0.9022727272727273], "q1_last2": [0.8909090909090909, 0.8727272727272727], "ok": false}, "d": {"answered": 0, "right": 0, "novel_window_n": 0, "novel_right": 0, "ok": false}, "e": {"hold": false, "ok": true}}`

**Reading it [Certain — the replay's own row].** At the end of alpha4-1's first hour the amended judge says, clause by clause, why the door is shut:
- (a): 1 completed episode of the 20 it needs, 0 successes.
- (b): the frame half HOLDS, with 3 frames alive in the ring: `purple|ball` 6.75, `red|box` 3.74, `in|the` 2.63. The read half fails: the last two sittings read 0.35 and 0.10. Those are the OLD sitter's newest-20 shares, because the tape carries what the live sitter wrote.
- (c): composite 0.89 / 0.90, Q1 0.89 / 0.87.
- (d): 0 graded answers.
- (e): no hold.

**One reading worth the orchestrator's eye [Likely].** A frame is any skewed pair, so the shelf's function words qualify (`in|the`). (b)'s frame half is the easy half, and it will hold for most of a life with a shelf. The binding clauses will be (a) (the policy, §11 finding 2), (b)'s read half, (c) and the seat's (d).

## 3 · The suites and the gate (the final bytes)
- **creature suite.** Command: `nice -n 19 python3 -u -m unittest discover -s tests/creature -t .`, TMPDIR on disk, log `scratch/logs/suite-creature.log`. Result: `Ran 738 tests in 645.934s` / `OK (skipped=1)`. The one skip is `test_g5k_outcome…TestSitPreregistrationOnLife2.test_life2_score_series_is_not_constant` («life-2 exam copy not present at …/scratch/life2-ro/exam»): a per-worktree copy that no fresh worktree carries. Named by a verbose run, `scratch/logs/g5k-outcome-v.log`.
- **genome suite.** Command: `… discover -s tests/genome -t .`, log `scratch/logs/suite-genome.log`. Result: `Ran 360 tests in 76.872s` / `FAILED (failures=1, skipped=1, expected failures=6)`.
  - **The one failure is master's, not this branch's.** `tests/genome/test_read_lexicon_parser.py::TestSenseReadParses::test_the_real_deployed_line_in_alpha4_genome_parses_identically` pins `SENSE read … every 5 s words 8` against the deployed `genome/ALPHA4.genome:95`. That line reads `every 20 s words 4` since 7bbc995 (04:57, the pre-flight's cadence decision; before that, 10 s / 6 words from 3d2e41b at 04:36). The test fails with `AssertionError: 20 != 5`, identically on 867e8bc (`scratch/logs/ctl-read-lexicon-parser.log`).
  - This branch touches nothing under `genome/` or `tests/genome/`. Not fixed here: it is another builder's pin, outside the judge. The fix is one line: the pin's two numbers become 20 and 4.
  - The one skip is `test_b8_sleep`'s designed «NOT GRADABLE on this world» branch (`scratch/logs/genome-b8-v.log`).
- **gate_g4.** Command: `python3 tools/gate_g4.py --tree /data/dev/genome-wt-judge --only 1,2,3,6`, `--tree` passed explicitly because its default is master's tree; log `scratch/logs/gate_g4.log`:
```
G4-1 writer sweep over 17 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: 44f6fa81f9c21c54… vs pin 44f6fa81f9c21c54… → PASS
G4-2 control (two canvases swapped): 5ad2e7286789af72… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4-6 two senses on one tape: exit 0, evidence present, folder rows 13 → PASS
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}
```
- **The final bytes.** The suites ran on 56b08dc. After them, only two docs changed: this report (read by no test), and one precision edit to §4's note at 12:04 («≥ 71 successful episodes» became «MORE than 70»: every success pays under 1). The one test file that reads the PREREG was re-run after that edit: `tests.creature.test_readiness_units` + `test_readiness_judge`, `Ran 42 tests in 3.234s` / `OK` (`scratch/logs/units-final.log`).

## 4 · The law change
`docs/ALPHA4-PREREG.md` §4 is amended in place. The old words stay, struck through (`~~…~~`); the new ones stand beside them, marked [AMENDED]. A dated note says why each changed:
- the units, with the arithmetic of why 0.35 cannot be read at N = 20: the null's successes are Binomial(20, 0.29), mean 5.8, sd 2.03, and 7 of 20 sits inside one sd; a policy truly at 0.35 would clear the band 12 % of the time;
- the window's wall-clock: ≈ 10 h for a locked policy (≈ 2 episodes an hour at 120 steps an hour), ≈ 2 h for a good one;
- the ring's horizon and the read sample;
- the streak defined once;
- the path;
- the numbers.

It is journaled as decision D-A4-J1 under Ahmad's 2026-09-05 delegation, his to overturn.

## 5 · Files and commits
- `creature/mind.py` — `READY_A_WINDOW/NULL/ALPHA/BOUND`, `binomial_bound`; `_consume_outcome` (the episode window); `_frames_alive` (replaces `_frames_lift_ok`); `_read_proxy` (the override gone); `_readiness_readings` (the five blocks); `_maybe_advance_stage` (one reading, read by `["ok"]`); snapshot/resume (`game_episodes` in, `game_rewards` and `stage_ready_streak` out).
- `tools/self_exam.py` — `read_sample`, `--read-seed` (default 20260923), `read_seed`/`read_heard_n` on the exam report.
- `creature/exam.py` — the sitter's argv: `--read-words 50 --read-seed 20260923`.
- `docs/ALPHA4-PREREG.md` — §4 amended.
- `tests/creature/readiness_rows.py` (new), `tests/creature/test_readiness_units.py` (new), `tests/creature/test_readiness_judge.py` (rewritten).
- Commits: `56b08dc` (the code, the tests, §4 amended) · the commits after it (this report, and §4's precision edit of 12:04).

## 6 · ADDENDUM 2026-09-23 15:00 +0400 — Claude (Sonnet 5, judge builder B4): clause (a) moved from a SLIDING window to DISJOINT blocks, k = 11
**Why.** The alpha4-2 designer's draft (`/data/dev/genome-wt-a42/docs/ALPHA4-2-PREREG.md` §4.3, written a day after this branch's 11:44 amendment landed) found a defect IN the amendment: (a)'s 5 % bound (`binomial_bound(20, 0.29, 0.05)` = 10) is computed for ONE window, but the judge reads (a) at EVERY sitting on a SLIDING window of the last 20 completed episodes — every window overlapping the last. A 24 h life completes ≈ 53 episodes at the null's pace (2,880 game steps at 30 s, ≈ 54 steps/episode), ≈ 34 overlapping windows read across the life. The designer's own probe (§11 Q1, 20,000 simulated 24 h lives): a policy playing AT RANDOM (0.29) cleared «the game» in ≈ 23 % of lives under the sliding rule — six times the stated 5 % — and alpha4-2's own reward-valued chooser (§2.1, which plays AT the null: 0.270 ± 0.016/episode in the toy) in ≈ 15 %. Recommended fix, adopted by the orchestrator under Ahmad's 2026-09-05 delegation: disjoint blocks, k = 11.

**The change.** (a) now reads DISJOINT blocks of 20 completed mind-chosen episodes — block j = episodes 20j+1..20j+20 in the order they completed, never overlapping, each episode in exactly one block. The reading at a sitting is the LATEST COMPLETE block's own successes against **k = 11** — the smallest k whose FAMILY-WISE rate over the ~2 disjoint blocks a 24 h life completes at the null's pace stays ≤ 0.05 (`family_wise_bound(20, 0.29, 0.05, 2)` = 11, computed at module load, never typed). A block's verdict, once read, is a fixed fact about those 20 episodes forever — pinned through every later sitting until the NEXT block itself completes. The readiness row's (a) block gains `block_index`, `block_n`, `k`, `p_null_at_k`, `blocks_complete` and `k_single_reading` (the struck single-reading bound, 10, printed beside for comparison); `bound` now equals `k` (11) — the OPERATIVE threshold `successes >= bound` is read against.

**`p_null_at_k` vs the family-wise rate — printed exactly, not typed from memory.** `p_null_at_k` (0.013172098935193789, `READY_A_BLOCK_P_NULL = binomial_tail(20, 0.29, 11)`) is the SINGLE-BLOCK tail — "how surprising is THIS block alone". It is NOT the reason k moved from 10 to 11: that reason is the FAMILY-WISE rate over the ~2 blocks a 24 h life completes, `1-(1-binomial_tail(20,0.29,k))**2` — 0.0755 at k=10 (above alpha, why k=10 was too loose under repeated reading) and 0.0262 at k=11 (under alpha), which the designer's own Monte Carlo simulation reads as 0.073 and 0.025 respectively (§4.3's table — the two closed forms agree to three significant figures; the designer's own words, "the smallest k whose family-wise rate at the null over the blocks a 24 h life can complete (2 at the null's rate) stays under 0.05 (0.025)", is what `family_wise_bound(20, 0.29, 0.05, 2)` computes exactly). The family-wise rate is not itself stored on the row — the row is one block's own reading, and the family-wise rate is a fact about a WHOLE LIFE of readings, a different statistic (the units-mismatch class of SOLUTIONS.md #162). Both numbers are printed here, distinctly, rather than either one silently standing in for the other.

**Tests, RED → GREEN** (`tests/creature/test_readiness_units.py::TestAPerEpisode` unless noted; RED = `bbf7af8`, this branch's own tip before this fix; GREEN = `974a2b5`):

| test | RED on `bbf7af8` | GREEN |
|---|---|---|
| `test_a_sliding_window_would_open_where_no_disjoint_block_does` (new — task (i)) — a 40-episode history (`F*11 S*18 F*11`): block 0 (episodes 1-20) reads 9 successes, block 1 (episodes 21-40) reads 9 successes — both fail k=11 — but the 9 successes at the tail of block 0 and the 9 at the head of block 1 are adjacent, so the OLD sliding window at episode 31 (episodes 12-31) reads 18/20 | `AssertionError: True is not False : at episode 25: no disjoint block ever reaches 11; (a) read {..., 'successes': 14, 'bound': 10, ..., 'ok': True}` (the sliding window read True even earlier than the episode-31 case documented in the docstring) | ok — False at every one of 5 checkpoint sittings (episodes 20, 25, 31, 35, 40) |
| `test_a_complete_block_is_pinned_until_the_next_block_completes` (new — task (ii)) — 11 successes complete block 0 (opens (a)); 19 more failures leave block 1 at 19/20; a 20th failure completes block 1 at 0 successes | `KeyError: 'block_index'` (the field does not exist on `bbf7af8`) | ok — block 0 pinned True (`block_index=0, successes=11, blocks_complete=1`) through the 19-failure sitting, then block 1 takes over (`block_index=1, successes=0, blocks_complete=2`, ok=False) only once IT completes |
| `test_the_disjoint_block_bound_is_computed_from_the_null_never_typed` (new — task (iii)) — `family_wise_bound(20, 0.29, 0.05, 2) == 11`; `family_wise_bound(20, 0.5, 0.05, 2)` moves to a DIFFERENT k (15) | `AttributeError: module 'creature.mind' has no attribute 'family_wise_bound'` | ok — k=11 at the adopted null, k=15 at 0.5; `READY_A_BLOCK_P_NULL` matches an independent `binomial_tail(20,0.29,11)` computed in the test to 12 decimal places |
| `test_ten_of_twenty_no_longer_opens_eleven_does` (renamed from `test_ten_of_twenty_opens_a_per_episode_where_the_per_act_mean_never_could`) — 10 successes in one complete block must now read False; 11 must read True | `AssertionError: True is not False : ten of twenty must no longer open (a) under k=11; (a) read {..., 'successes': 10, 'bound': 10, ..., 'ok': True}` | ok |
| `test_a_complete_block_is_not_diluted_by_later_episodes_outside_it` (renamed from `test_the_window_holds_the_last_twenty_only`, whose own premise — "the window holds the last twenty only" — was the sliding behaviour being removed) — 12 successes complete block 0 (opens (a)); 20 more failures fill block 1 to 12/20, not complete | old assertion (still true on `bbf7af8`, not re-run standalone: the sliding window's last 20 completed episodes are those 20 failures, 0 successes, ok False) | ok — block 0 stays pinned (`successes=12, block_index=0, ok=True`), undiluted by the trailing failures outside it |
| `test_every_readiness_row_carries_its_numbers` (`TestNumbersOnEveryRow`) — `BLOCK_KEYS["a"]` widened to the 12-key shape; the `bound` value moves 10→11 | `AssertionError: Items in the second set but not the first: 'blocks_complete' 'k_single_reading' 'k' 'block_n' 'p_null_at_k' 'block_index' : (a) keys` | ok |
| `test_readiness_judge.py::TestResumeKeepsStage.test_resume_mid_life_keeps_the_stage` — the two direct `_game_episodes` references replaced by `_game_last_block`/`_game_block_n`/`_game_block_successes` | `AttributeError: 'Mind' object has no attribute '_game_episodes'` | ok — `mind._game_last_block == {"block_index": 0, "successes": 12}` after `PASSING_EPISODES` (one complete block), both fresh and resumed minds agree |

Full run: RED on `bbf7af8` (`test_readiness_units.py` + `test_readiness_judge.py`, the updated files copied into a detached control worktree at `bbf7af8`, removed after use): `Ran 45 tests in 3.311s` / `FAILED (failures=3, errors=4)` — exactly the 7 tests above, the other 38 (guards, and (b)/(c)/(d)/(e) tests untouched by this change) pass unchanged on both trees (`scratch/logs/red-final-on-bbf7af8.log`). GREEN on the branch: `test_readiness_units.py` + `test_readiness_judge.py`: `Ran 45 tests in 3.454s` / `OK`; + `test_alpha4_seams.py` (the third file the original report counted as "the integration seams"): `Ran 51 tests in 6.320s` / `OK` (`scratch/logs/green-judge-files-final.log`).

**The negative control, re-run** (the hour-1 fixture replayed under `bbf7af8` — a detached worktree, removed after use — and under this fix; the differ is the SAME `scratch/negctl_diff.py` the original round wrote, unchanged): `scratch/logs/negctl-2.log`, verbatim:
```
rows: 867e8bc 4322 · branch 4322
byte comparison: 4318 rows identical byte for byte; 4 readiness rows identical outside the `readiness` field; first difference: None
compare(ignore=('readiness',)): None
control 1 — compare() UNMASKED: (1029, 'readiness') · the first sit row's seq: 1029 → CAUGHT exactly there
control 2 — planted hash flip at row 1 (seq 3): byte comparison first difference (1, 3); compare → (3, 'hash') → CAUGHT
stage events: 867e8bc 0 · branch 0
NEGATIVE CONTROL: PASS
```
(The script's own variable names say "867e8bc" — read here as "the control worktree," `bbf7af8`, not literally 867e8bc.) The fixture's last readiness row (seq 3840) under this fix: `{"a": {"window": 20, "n": 1, "successes": 0, "bound": 11, "null": 0.29, "ok": false, "block_index": null, "block_n": 20, "k": 11, "p_null_at_k": 0.013172098935193789, "blocks_complete": 0, "k_single_reading": 10}, ...}` — the hour-1 fixture never completes a single 20-episode block (it holds one completed game episode total, per §2's own row-count table), so every (a) reading on it is the "no complete block yet" branch: `n` is the in-progress count (1), `block_index` is `null`, `ok` is `false` — `bound`/`k` (11) and `k_single_reading` (10) both print regardless, since they are module constants, not dependent on any block having completed.

**Suites and gate (the final bytes, `974a2b5`):**
- **creature suite.** `nice -n 19 python3 -u -m unittest discover -s tests/creature -t .`, `TMPDIR` on disk: `Ran 741 tests in 612.074s` / `OK (skipped=1)` (`scratch/logs/suite-creature-2.log`) — 738 + 3 net new test methods (738 was this branch's own prior count before this addendum).
- **genome suite.** `Ran 360 tests in 77.578s` / `FAILED (failures=1, skipped=1, expected failures=6)` (`scratch/logs/suite-genome-2.log`). **The one failure is still master's, not this branch's**, identical to §3's own finding: `test_read_lexicon_parser.py::TestSenseReadParses::test_the_real_deployed_line_in_alpha4_genome_parses_identically` pins `every_s == 5` against the deployed `genome/ALPHA4.genome:95`, which reads `every 20 s words 4` since `7bbc995`. Not fixed here (this branch touches nothing under `genome/` or `tests/genome/`); "both suites green" is not literally met, by the same one pre-existing failure the original report already disclosed.
- **gate_g4.** `python3 tools/gate_g4.py --tree /data/dev/genome-wt-judge --only 1,2,3,6` (`scratch/logs/gate_g4-2.log`):
```
G4-1 writer sweep over 17 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: 44f6fa81f9c21c54… vs pin 44f6fa81f9c21c54… → PASS
G4-2 control (two canvases swapped): 5ad2e7286789af72… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4-6 two senses on one tape: exit 0, evidence present, folder rows 13 → PASS
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS', '6': 'PASS'}
```
The mind-parity and replay-identity hashes are byte-identical to §3's own run — expected: this fix touches only the `readiness` journal field, never the organism's state (the negative control's own finding, restated).

**Files touched.** `creature/mind.py` (`binomial_tail` factored out of `binomial_bound`; new `family_wise_bound`; `READY_A_BLOCKS_PER_LIFE`/`READY_A_BLOCK_K`/`READY_A_BLOCK_P_NULL`; `_game_episodes` deque replaced by `_game_last_episode_step`/`_game_block_n`/`_game_block_successes`/`_game_last_block`; `_consume_outcome`, `_readiness_readings`, `_maybe_advance_stage`'s docstring, `snapshot()`/`resume()`); `tests/creature/test_readiness_units.py` (`BLOCK_KEYS["a"]` widened; 3 new tests, 2 rewritten); `tests/creature/test_readiness_judge.py` (2 lines, 1 comment); `docs/ALPHA4-PREREG.md` (§4 (a) amended in place, dated, the sliding-window words struck). **Commit: `974a2b5`** (on `judge-units-0923`, still HELD — not merged; the orchestrator merges after the ladder's 22:00 cutoff, per this branch's own §0.1).
