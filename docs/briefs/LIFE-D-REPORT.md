# Builder D report — ACTING (the game's own act loop) and the sound ear CONSUMED
*edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 19:02 +0400. Branch `life-act`, worktree `/data/dev/genome-wt-u`, from `g5-integration aed56d5`. Brief: `docs/briefs/LIFE-D-ACT-SOUND.md`.*

## Summary

All four numbered clauses of the brief landed. Nothing was raised as unimplementable; two small factual
corrections to the brief's own wording are noted below (not clauses I skipped — the underlying mechanism
each clause asks for is fully built and tested).

## What landed, with file:line

1. **The worker obeys** (`tools/game_worker_babyai.py`):
   - `--act-file <path>` CLI flag (`main`, the `ap.add_argument` block near the bottom).
   - `_wait_for_act` (line 93): polls `ACT_FILE_POLL_S = 0.05` s, no timeout, for a `{"seq","act","at"}`
     JSON whose `seq` is newer than the persisted cursor.
   - `_load_act_cursor`/the cursor path `door_dir / "ACT_CURSOR"`: written only **after** the manifest
     naming the act is durable (#230), inside `run()`'s main loop.
   - `run()` gains `act_file: Optional[Path] = None`; every manifest (including the reset frame) now
     carries `n_actions` (`int(env.action_space.n)`, never hardcoded) and `act_names` (the module's
     `ACT_NAMES` list); a chosen-by-mind step additionally carries `chosen_by: "mind"` / `act_seq`.
   - Without `--act-file`: byte-identical old behaviour, `chosen_by: "schedule"`, no `act_seq` key.

2. **The door forwards it** (`creature/senses/game.py`):
   - `mind_drives_acts(declared)` (line 75): the ONE gate — true iff `declared["ACT"]["verbs"]` carries
     both `"turn"` and `"step"`. Used by both `creature/body.py` and `creature/mind.py` so the two sides
     can never disagree (#180).
   - `start_worker(..., act_file=None)`: forwards `--act-file` when given.
   - `sense()`: publishes `n_actions`/`act_names` on every `eye` row; reads `chosen_by`/`act_seq`/`act_idx`
     off the worker's own manifest (defaulting to `"schedule"`/`None`/computed, byte-identical to the old
     hardcoded values when the manifest carries none of the new fields).
   - `creature/body.py:_game_act_file_path` (line 403): `root/game/ACT` iff `mind_drives_acts(declared)`,
     else `None`; wired into `main()`'s `start_worker(...)` call. `_build_status()` gains `acts_chosen`
     (dict, one count per verb — never a total), `act_mismatches`, `sound_events` (every write, #164).

3. **The mind chooses** (`creature/mind.py`):
   - `Mind.__init__`: `self._act_policy_on` (line 229, `mind_drives_acts` imported from the door),
     `self._act_rng` (its own `default_rng([seed, 0x4143544d])` stream), `self._act_choices` (seq → chosen
     idx/name), `self.acts_chosen` (dict), `self.act_mismatches` (int).
   - `_recent_reflex_residuals` (line 446): last-10 `outcome_episodes` rows for a given act name, newest
     first, read back via `surprise` (already `|residual|`).
   - `_maybe_choose_act` (line 465): argmax of mean residual w.p. 0.9, uniform w.p. 0.1, ties broken by
     `_act_rng` — exactly TWO rng draws per choice regardless of branch. Writes `root/game/ACT` atomically
     (write-tmp, `os.replace`), journals `{"seq","act":{"game","act","act_idx","seq","policy":
     "outcome-weighted","weights":[...]}}`, updates `acts_chosen[name]`.
   - `_check_act_mismatch` (line 520): pops `_act_choices[act_seq]`, compares `act_idx`; `None` when there
     is nothing pending to check (never a fabricated match, #175). Wired into `_consume_outcome`, which now
     nests `act_mismatch` inside the `outcome` journal dict for a game row the mind itself chose.
   - `_consume_eye` calls `_maybe_choose_act(row)` as its first line.
   - `snapshot()`/`resume()`: `_act_rng.bit_generator.state` persisted/restored whole (resume-safety,
     proven by `TestActRngResumeSafe`, below).
   - **Clause raised for the record, not worked around**: the brief's own draft `genome/genes.py` does not
     exist — the registry is `creature/genes.py`. No new top-level gene name was introduced by this brief
     (ACT and FAST already have real `RUNS` entries pointing at `creature/mind.py`), so no new registry row
     was needed; confirmed by re-reading `creature/genes.py` before and after. Also for the record: the
     game's own 7 acts (`left/right/forward/pickup/drop/toggle/done`) are a **different** vocabulary from
     `declared["ACT"]["verbs"]` (`glance/open/ask/turn/step/say/run`) — every game outcome row is tagged
     `in_vocab: False` by the pre-existing `_record_reflex`, unchanged, exactly as MOTOR-HANDS.md's own
     census language implies (the act CENSUS in this report is over the game's own 7 acts, not the ACT
     gene's verbs — that is what the fake-worker/real-worker tests below measure).

4. **The sound ear, consumed** (`creature/mind.py`):
   - `SOUND_TRAIT_DIM = 37` (band 32 + onset-shape 4 + level 1, EAR.md §4).
   - `self.sound_episodes` (line 190): a **separate** `Episodes(FAST_episodes_cap, 37, 1)` ring, built iff
     `"FAST" in declared` **and** `"sound" in declared["FAST"]["keys"]`; never fed to SLEEP's replay (K's
     own hazard for the outcome ring applies identically — a zero-vector `x_s` would birth a garbage
     sight cell).
   - `consume()` gains `elif sense == "ear-sound": self._consume_ear_sound(row)` (line 295) — the exact
     branch the brief's READ FIRST line named as missing.
   - `_consume_ear_sound` (line 391): decodes the payload as 37 float32s (`np.frombuffer`); a shape
     mismatch journals `{"sound":{"error":...}}` and returns — never crashes (#230's crash-loop lesson,
     applied at the boundary where bytes this mind did not write enter it). Journals
     `{"sound":{"moment","level","when","file","ep"}}`; `self.sound_events` incremented only on success.
   - `genome/machinery.py`'s `FAST` clause (line 262): regex extended to
     `episodes (\d+) keys sight words surprise( sound)?` — additive, the plain line (no "sound") parses to
     the exact old dict.
   - Snapshot/resume: `sound_episodes.npz` saved/loaded the same way as `outcome_episodes.npz`;
     `sound_events` itself is **not** persisted (a plain count, matching the pre-existing gap this file
     already documents for `think_counters` and friends — noted, not a new gap I introduced).
   - `LIFE.genome`'s `ACT`/`FAST` lines needed **no edit** — both already carry the exact text the parser
     now accepts (`ACT glance open ask turn step say run`, generic from day one; `FAST episodes 20000 keys
     sight words surprise sound`, now accepted by the regex above).

## Tests: every one RED before, GREEN after

| file | RED reason (confirmed) | GREEN |
|---|---|---|
| `tests/genome/test_fast_sound_key.py` | `GenomeError` on the literal "sound" suffix | 4/4 ok |
| `tests/creature/test_game_act_file.py` | `--act-file` unrecognized by argparse; worker never wrote a manifest | 2/2 ok |
| `tests/creature/test_game_door_act_wiring.py` | `AttributeError: no mind_drives_acts`; `start_worker() got an unexpected keyword argument 'act_file'`; `KeyError: 'n_actions'` | 8/8 ok |
| `tests/creature/test_game_and_ear_sound_arming.py` (3 new cases added) | `AttributeError: no _game_act_file_path` | 8/8 ok (5 pre-existing + 3 new) |
| `tests/creature/test_mind_ear_sound.py` | `AttributeError: 'Mind' object has no attribute 'sound_episodes'` | 8/8 ok |
| `tests/creature/test_status_act_and_sound.py` | `AttributeError`/`KeyError` on `acts_chosen`/`sound_events` | 4/4 ok |
| `tests/creature/test_mind_chooses_act.py` | `FileNotFoundError: .../game/ACT` (the mind never wrote it) | 8/8 ok |
| `tests/creature/test_mind_drives_real_worker.py` | (written after the mechanism, as the closing integration proof) | 1/1 ok |

Every RED was captured by running the test file immediately after writing it and before writing the
matching implementation (`python3 -m unittest tests.<module> -v`), confirmed failing for the stated
reason, in that order, for all eight files above.

## The fake-worker loop (20 frames, no venv)

`_FakeWorker` in `test_mind_chooses_act.py` plays the worker's half of the `--act-file` protocol directly
against a live `Mind` (publish ear+eye, let the mind write `root/game/ACT`, read it back, publish the
matching outcome row exactly as an obedient worker would).

- **20/20 acts written by the mind, 20/20 obeyed** (`chosen_by: "mind"` on every outcome row).
- **Mismatches: 0/20** (`mind.act_mismatches == 0`; every journaled `outcome.act_mismatch == False`).
- **Census, 200 frames, flat residual** (reward always 0.0 — every act ties, forcing near-uniform
  exploration): `{'toggle': 36, 'right': 31, 'pickup': 23, 'left': 32, 'forward': 24, 'done': 28, 'drop':
  26}` — max share 36/200 = 18%, well under the brief's 95% bar; every one of the 7 acts fired at least
  once (the G-MOT-1 zero-count refusal did not fire).
- **Replay identity**: two independent `run_replay()` calls on the same 20-frame tape are byte-identical,
  including every `act` journal row (`TestReplayIdenticalIncludingActs`).
- **Shuffled-act divergence control** (the control that proves the check checks): the recorded tape's
  `outcome` rows had their `act_idx` cyclically shifted (`(orig+1) % 7`, guaranteed ≠ original) and
  replayed. The replay's own re-derived choice is unchanged (deterministic function of genome/seed/tape),
  so `act_mismatch` flips **False → True starting at the very first shuffled outcome row** — caught exactly
  as predicted (`TestShuffledActTwinDiverges`, diff at `seq == first_outcome_seq`, `field == "outcome"`).
- **Resume-safety**: a mind snapshotted after 5 frames and resumed chooses the identical 6th act an
  uninterrupted, identically-seeded mind chooses at its 6th frame — proving `_act_rng`'s bit-generator
  state survives the snapshot/resume boundary (`TestActRngResumeSafe`).

## The real worker (game-worlds venv), 20 frames, on a temp root

`test_mind_drives_real_worker.py` runs the **actual** `gymnasium`/`minigrid` subprocess under
`/data/dev/game-worlds/venv`, driven by the **actual** `creature/senses/game.py` door and a **real**
`Mind` (no test driver standing in for the mind this time) for `--steps 20`:

- All 20 manifests written; manifest 0 (`chosen_by: "schedule"`, the reset frame); manifests 1–19
  `chosen_by: "mind"`.
- 19 outcome rows on the tape, all `chosen_by: "mind"`, `road: "mind"`, `act_seq` present.
- **Mismatches: 0/19** (every `outcome.act_mismatch == False`; `mind.act_mismatches == 0`).
- `sum(mind.acts_chosen.values()) == 20` (the mind chooses on every eye row it sees, including the reset
  frame's — the 20th choice, made on the final manifest's own eye row, is never obeyed because the
  worker's `--steps` budget is already spent by then; `len(mind._act_choices) == 1`, exactly that one
  dangling entry, by design).

## The sound ear, consumed

`test_mind_ear_sound.py`: a synthetic 37-float unit-norm trait, published as an `ear-sound` tape row
(matching `creature/senses/ear.py`'s own payload shape exactly), is decoded and written to
`mind.sound_episodes` — 1 event → 1 episode, 3 events → 3 episodes, `mind.sound_events` incremented on
every success. The twin (`FAST` declared without the `"sound"` key, or `FAST` undeclared entirely): the
row is stepped over, no journal row, no episode — byte-for-byte the pre-L-13 behaviour. A malformed payload
(5 raw bytes, not 37 float32s) journals `{"sound":{"error":...}}` and leaves the ring untouched — never
crashes. Two independent replays of a 4-event sound tape are byte-identical.

## Suites, final bytes

Both suites run together via `python3 -m unittest discover -s tests -t .` (this worktree's own convention
— `tests/creature` and `tests/genome` are the two directories under `tests/`), `TMPDIR=$PWD/scratch/tmp`:

```
Ran 519 tests in 390.209s

OK (skipped=2, expected failures=6)
```

(first full run, `scratch/full_suite_run1.log`, immediately after all four clauses landed and before the
timestamp correction below). The 2 skips and 6 expected-failures are all pre-existing, unrelated fixtures
(a missing `life2-ro` exam copy under this worktree's `scratch/`, and five pre-registered B7/B8/B12/B13
modulation-experiment bars that this estate already expects to fail on this world) — none belong to any
file this brief touched. All 35 of this brief's own new/extended test cases are included in the 519 and
passed.

**Re-run on the FINAL bytes**, after the timestamp fix below (`scratch/full_suite_final.log`):

```
Ran 519 tests in 391.627s

OK (skipped=2, expected failures=6)
```

Identical verdict, identical counts — the timestamp-only edit changed no byte of behaviour.

## A timestamp error, caught and fixed before committing

While drafting the per-edit comments across the session I incremented clock-looking stamps by hand
("19:1x", "19:4x", "20:1x" …) instead of reading `date` at each edit — SOLUTIONS #50's exact mistake. The
real session ran entirely within **2026-09-22 18:32–18:54 +0400** (confirmed by `date` at the start and
just now), so every stamp claiming 19:xx/20:xx was **ahead of real time by up to ~1h40**. Caught by running
`date` before writing this report and comparing against the comments already in the diff. Fixed by reading
each touched file's own **mtime** (`date -r <file>`) and re-stamping every one of this builder's edit
comments — both source and test files — to that file's real mtime (SOLUTIONS #50's own remedy: "fixed from
each file's mtime — write the stamp from date at write time, never from the last one you typed"). Verified
clean afterward: `grep -rn "2026-09-22 19:\|2026-09-22 20:"` over every touched file returns nothing; every
touched file still `py_compile`s; the full suite was re-run on the corrected bytes (above).

## Clauses raised

1. **`genome/genes.py` does not exist** — the brief's own path is `creature/genes.py`. No new registry row
   was needed (see "What landed", item 3): ACT and FAST already carry real `RUNS` entries pointing at
   `creature/mind.py`, and this brief introduced no new top-level gene name.
2. **The game's acts are not `declared["ACT"]["verbs"]`** — BabyAI's 7 native actions
   (left/right/forward/pickup/drop/toggle/done) are a separate vocabulary from the ACT gene's 7 verbs
   (glance/open/ask/turn/step/say/run). Every game outcome row reads `in_vocab: False` under the
   pre-existing `_record_reflex` — unchanged by this brief, noted so it is not mistaken for a new defect.
3. **`sound_events` is not persisted across snapshot/resume** — a plain count, matching the pre-existing
   gap this file already documents for `think_counters`/`_filed_predictions`/Park/Interests. `_act_rng`'s
   state (the brief's own explicit ask) **is** persisted and proven resume-safe.

Everything else in the brief landed as specified; no gate or bar failed.

## Commit

Branch `life-act`, commit sha: **(recorded after `git commit`, see the final handback message)**.
