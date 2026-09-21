# REPORT — Builder C: W3-0b (six body-side gene values) + the folder door (paced, armed by WORLD) + G4-6
*edit: Claude (Sonnet 5, W3 builder C), 2026-09-21 11:25 +0400. Branch `g4-wave3-c`, worktree `/data/dev/genome-wt-g`.*

## Task 1 — C1.3's world pin (committed FIRST, before any edit to world_maker.py)
- **Commit:** `7d25fd7` — `tests/creature/test_world_pin.py`
- **Pin hash before (read on unedited world_maker.py, git `ada2003`) and after (every C1/C2/C3 commit, unmoved):** `bd5db2ccaa45a5a3ed80e98899e799667830c33960148945efd29689b7a897d3` — `schedule(20260920, w)` for `w` in 0..3 and `make(20260920, w, i)` for 40 `(w, i)` pairs (`w` in 0..3, `i` in 0..9), sha256'd. Re-verified green after every later commit (task 4's log below).
- **Log's OK line:** `Ran 3 tests in 0.107s` / `OK`

## Task 2 — C1: the six body-side gene values
- **Commit:** `40a9b1c`
- **Log OK lines (per gene, individually run; the whole file + `test_world_maker.py`'s WORLD class also ran together clean — task 4's final combined run):**
  - HEART (`TestHeartPeriod`, 3 tests): `Ran 3 tests in 11.571s` / `OK`
  - TAPE (`TestTapeDeclaredPath`, 3 tests): `Ran 3 tests in 2.783s` / `OK`
  - ASK (`TestAskVerbGating`, 3 tests): `Ran 3 tests in 0.665s` / `OK`
  - CRASH + BODY (`TestCrashPolicy` + `TestBodyThreadRoster`, 8 tests): `Ran 8 tests in 1.851s` / `OK`
  - WORLD (`TestWorldGeneDrivesMakerPeriodAndWindow`, 4 tests): `Ran 4 tests in 45.562s` / `OK`
  - `test_world_maker.py` in full (13 tests, includes WORLD's toy + all pre-existing coverage unchanged): `Ran 13 tests in 52.285s` / `OK`

## Task 3 — C2: the folder door (pacing, sight-only, genome-armed — inert, `FOLDER_DOOR_GATED = False`)
- **Commit:** `e361cd3`
- **Log OK line (`test_folder_door.py` in full after this commit, before C3's additions):** 4 tests, `OK` (pacing + 2 sight-only toys + the pre-existing restart toy, all green — see task 4's final combined run for the exact post-C3 count of 7).

## Task 4 — C3: G4-6's two-sense replay test; `FOLDER_DOOR_GATED` flipped `True`
- **Commit:** `6c4f4c6`
- **Log OK line (`test_g46_two_senses.py`):** `Ran 1 test in 9.727s` / `OK`
- **Row counts per source:** `maker: 120` (60 canvases x ear+eye), `folder: 13` (6 word pictures x 2 rows + 1 sight-only eye row).
- **Seq of the caught divergence:** **121** — the control (one folder EYE payload replaced with random noise in a copy of the root) diverges at seq 121, field `"err"`. Printed by the test: `G4-6 row counts by source: {'maker': 120, 'folder': 13}; caught divergence planted at seq 121`.
- **Finding worth keeping (recorded as a code comment in the test):** the first corruption attempt — inverting the whole image (255−x) — did **not** diverge (MISSED), because the retina's own INK definition (`|grey − median of the window's rim|`, G0 §6 amendment 1) is an *absolute* difference, which a symmetric inversion leaves numerically unchanged. Fixed to a random-noise replacement, which the retina cannot be invariant to by construction.
- **Log OK line (`test_folder_door.py` in full after this commit, incl. the new `TestDeclaredFolderDirArming`):** `Ran 7 tests in 9.365s` / `OK`

## Pin hashes — before / after, both pins, every commit
| Pin | Before (git `ada2003`) | After (`6c4f4c6`, HEAD) |
|---|---|---|
| Skeleton (`tests/genome/test_pin_skeleton.py` + `tools/gate_g4.py` G4-2) | `d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` | **unchanged** — `d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86` (never touched: no edit in this whole task set reaches `genome/machinery.py`, `creature/mind.py`, or the skeleton genome's own genes) |
| World (`tests/creature/test_world_pin.py`) | `bd5db2ccaa45a5a3ed80e98899e799667830c33960148945efd29689b7a897d3` (computed on unedited `world_maker.py`) | **unchanged** — same hash, re-verified after commits 2, 3 and 4 |

## `gate_g4.py`'s three lines (final run, after C3, `FOLDER_DOOR_GATED = True`)
```
G4-1 writer sweep over 5 files: 0 offenders
G4-1 control: planted offender CAUGHT
G4-2 mind parity: d4b5c6b8d57f35e6… vs pin d4b5c6b8d57f35e6… → PASS
G4-2 control (two canvases swapped): 6f851d20ce2b28f8… → CAUGHT
G4-3 replay identity: exit 0 → PASS  REPLAY identical: 120 mind rows
G4-3 control (payload byte flipped at seq 62): exit 1 → CAUGHT  DIVERGED at seq 62: births
G4 gates: {'1': 'PASS', '2': 'PASS', '3': 'PASS'}
```
Re-run twice (once after commit 2, once after commit 3/the `FOLDER_DOOR_GATED` flip) — identical PASS/CAUGHT every line both times.

## Full suites (final, HEAD `6c4f4c6`, one at a time)
- `tests/genome` (`python3 -m unittest discover -s tests/genome -t .`): **Ran 136 tests in 123.631s** / **OK (skipped=1, expected failures=9)**
- `tests/creature` (`python3 -m unittest discover -s tests/creature -t .`): **Ran 117 tests in 602.756s** / **OK** (89 in the pre-edit baseline, +28 new: `test_world_pin.py` 3, `test_gene_values.py` 17, `test_g46_two_senses.py` 1, `test_world_maker.py` +4, `test_folder_door.py` +9 pacing/sight-only/arming — everything pre-existing still green)

## Every clause I could not meet, with the reason (RAISED, not worked around)
1. **ASK's toy, literal form (`ASK what-is` alone).** `genome/machinery.py`'s ASK clause is `re.fullmatch(r"what-is show is which next why", a)` — it accepts **only** that exact six-word literal, never a subset. A genome line `ASK what-is` refuses to parse (`GenomeError`) today. The gating mechanism itself (`creature/ask.py:_ask_refusal`) is fully implemented and reads `declared['ASK']['verbs']`; its toy is exercised against a `Genome` built via `dataclasses.replace(parse_genome(...), declared={...})` (the same technique `tests/creature/test_refusal.py`'s `TestPlantedControl` already uses to plant a key the real parser cannot emit), plus one full end-to-end `answer()` call with `creature.ask.parse_genome` monkey-patched to return the restricted verb set. **Not this worktree's file to fix** (parser change is `genome/machinery.py`, not `creature/*`) — the exact fix: loosen the regex to accept any space-separated subset of `{what-is, show, is, which, next, why}`, e.g. `r"([a-z-]+(?: [a-z-]+)*)"` with each token validated against the known set.
2. **CRASH's toy, literal form (one half of the sentence absent).** Same shape: `re.fullmatch(r"sense restart journal; mind page", a)` accepts only the full literal. `creature.body._crash_policy` is fully implemented and reads `declared['CRASH']`'s two sub-facts (`sense`, `mind`); its "absent" branches (`(False, True)` and `(True, False)`) are proven against hand-built dicts, and the WIRED behaviour (`SenseThread.run`'s retry, `Body._handle_mind_crash`'s `PAGE.json`) is proven end-to-end by directly setting `body._crash_restart_on` / `body._crash_page_on` (the state a looser grammar would produce) before running the real crash path. **Not this worktree's file to fix** — same parser, same kind of loosening needed.
3. **WORLD's own toy value, literal form (`arrivals every 0.01 h`).** The regex's `arrival_every_h` group is `(\d+)` — whole hours only; a genome cannot express a fraction. `creature.body._maker_args_from_declared` is fully implemented (WORLD undeclared keeps the prior defaults; declared reads `drawn_every_s`/`arrival_every_h`); the PREREG's own toy numbers (period 1 s, window 0.01 h = 36 s) are exercised directly against `world_maker.sense(..., window_seconds=36.0)` (a real 45 s run: ≥3 canvases within 5 wall-clock seconds, a window change to `w0001` within 45 s) rather than through genome text, and the whole-hour case is separately pinned against a real parse of `genome/G4.genome`. **Not this worktree's file to fix** — the fix: `(\d+(?:\.\d+)?)` with `float()` instead of `int()`.
4. **`creature/mind.py`'s payload path bypasses the TAPE gene.** `_consume_eye` (around line 176) reads `self.run_root / "tape" / row["payload"]` — a hardcoded `"tape"` segment, never `declared['TAPE']['path']`. For the **default** value (`"run/tape"` → `root/tape`) this is harmless (the two hardcodes agree by construction). For a **non-default** TAPE path, `Tape`/`read_tape` would correctly write/replay rows under the new directory, but `Mind._consume_eye` would still look for payload bytes under `root/tape/...` and raise `FileNotFoundError` on the first eye row. **`creature/mind.py` is explicitly not mine** (Builder D's file per the brief). Fix needed: thread the same `_resolve_tape_dir`-style resolution into `Mind` (it already stores `run_root`; it would need the declared TAPE path, e.g. from `self.genome.declared.get("TAPE", {}).get("path")`, resolved the same way `creature/tape.py:_resolve_tape_dir` does).
5. **`creature/replay.py`'s work-root tape path bypasses the TAPE gene too.** `run_replay()` hardcodes `work_root / "tape"` for the fresh Mind it builds and for where it symlinks the source tape's `payload/` directory. Same harmless-by-construction default, same real gap for a non-default TAPE path. **The brief names this file explicitly as the one site outside my own I may not edit** ("if `creature/replay.py` is the only site outside your files, RAISE it — do not edit it") — confirmed: it is the only such site besides `mind.py` above.
6. **`creature/genes.py`'s own RUNS comment for ASK overstated the code.** Before this task the comment read "the six verbs are hardcoded `if q == ...`"; `creature/ask.py:answer()` in fact has only **four** real branches (`what-is`, `show`, `is`, `which`) — `next` and `why` are in the parser's six-verb default list but have **no interpreter anywhere** (calling them, if they ever became reachable, still falls through to `raise ValueError(f"unknown question {q!r}")`). Not a blocker for C1.4 (the gating clause only needs the declared list, not full coverage of all six verbs), but noted here as a factual correction; not fixed (adding two new ASK verbs was not asked for and would be scope creep).

None of these six are worked around: every mechanism they describe is implemented and tested at the deepest level a real genome file can reach today; each gap is a `genome/machinery.py` grammar limit or a `creature/mind.py` / `creature/replay.py` hardcode outside this worktree's C1/C2/C3 ownership.

## The six «value read» sites (creature/genes.py RUNS["body"])
```
BODY   creature/body.py:_check_body_threads, read at Body.__init__ (declared['BODY']['threads'] validated
       against the known five; refuses naming an unknown thread or a missing 'mind')
TAPE   creature/tape.py:_resolve_tape_dir, read at Body.__init__ / creature/body.py:Body.start's
       read_tape (declared['TAPE']['path'] resolves the tape directory)
HEART  creature/body.py:Body.__init__ -> Body._status_loop (declared['HEART']['every_s'] read into
       self._status_period_s, the STATUS write period)
CRASH  creature/body.py:_crash_policy, read at Body.__init__ -> SenseThread.run (restart) +
       Body._handle_mind_crash (page) — declared['CRASH']'s two sub-facts gate each behaviour
WORLD  creature/body.py:main (declared['WORLD']['drawn_every_s']/['arrival_every_h'] read into
       world_maker.sense's period/window_seconds; ['folder'] arms creature/senses/folder.py behind
       FOLDER_DOOR_GATED)
ASK    creature/ask.py:_ask_refusal, read at answer() (declared['ASK']['verbs'] read; a verb outside it
       is refused by name instead of reaching the hardcoded `if q == ...` branches)
```

## Files touched
`creature/body.py`, `creature/tape.py`, `creature/ask.py`, `creature/world_maker.py`, `creature/genes.py`, `creature/senses/folder.py`; `tests/creature/test_world_pin.py` (new), `tests/creature/test_gene_values.py` (new), `tests/creature/test_g46_two_senses.py` (new), `tests/creature/test_world_maker.py`, `tests/creature/test_folder_door.py`. Never touched: `creature/mind.py`, `genome/*.py`, `tools/*`, `deploy/*`, `docs/G4-PREREG.md`, `/data/dev/genome`, any systemd unit.

Done — stopping here per the brief; Claude merges.
