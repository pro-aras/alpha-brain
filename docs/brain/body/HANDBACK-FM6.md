# HANDBACK — F-M6 (AMENDMENT 1 §2): the nearest rule for a young word, the «held» test set, the bench gate

*Claude (Opus 5.5, F-M6 builder), written 2026-09-28 22:31 +0400. Branch `brain-organ-fm6` (cut from `brain-organ` bc45156), worktree `/data/dev/genome-wt-organ-f`. The law: `docs/brain/body/PREREG-BRAIN-IN-BODY-AMEND-1.md` §2 (sha256 45abeca2…, read whole). Only light work was run (single test modules ≤ 60 s, one process, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`, nice 19, TMPDIR on disk). No cache draw, gate, replay or suite was run at full size; nothing was written under a life's root or a scored root.*

## 1 · What exists

| # | file | what |
|---|---|---|
| 1 | `genome/machinery.py` (WORLD_CODE) | BRAIN parser: `young <n> nearest` → `declared["BRAIN"]["young_rule"] = "nearest"`; `young <n>` declares NO `young_rule` key (every existing genome's dict byte-identical); any other word after the count refuses BY NAME (`BRAIN: young takes 'nearest' or nothing after its count, got '…'`). |
| 2 | `brain/scene/learners.py` | `RWLearner.young_rule` (class attribute, default `"band"` = the law) and `RWLearner._young_nearest`; `answer_point` chooses `point` by it ONLY when the rule is `"nearest"`, the phrase is ONE word, the word is heard and young (`meetings < p_from`). Distance = DIAG-M6's: `√((z − μ_w)ᵀ Λ (z − μ_w))`, `μ_w = prototype(j)`, `Λ = reader["ear"]["lam"][one_alone]`; exact tie → `pick(d, rng, "min")` (the item's generator). Four fall-backs to the law: no `reader`, `one_alone` None, that Λ None, `proto_w` 0. When the rule acts: `best = max(s)` (the law's number), the law's `pick(s, rng)` is NOT drawn, and the answer gains `young_d` (the distances) and `point_rule: "nearest"`; every other answer is byte-identical to the law's. `logp_answer`, `phrase_scores`, `calibrate`, `calibrate_r`, `train_scene`, `believed`, `held_words` untouched. An unknown `young_rule` raises `ValueError` naming it. |
| 3 | `genome/brain.py` | `young_rule` an OPTIONAL cfg key (`CFG_OPTIONAL`): absent / `"band"` = the law and leaves no trace (cfg, `vars(L)`, state hash, save file, summary all as before — pinned to a pre-fix fixture); `"nearest"` sets the learner's INSTANCE attribute, enters `cfg` (→ `state_hash`, `save`), and `summary()` carries `young_rule: "nearest"`; `load` refuses across rules BY NAME (`load: the saved brain lived under young_rule 'nearest', not 'band' …`); any other word refuses by name. |
| 4 | `brain/scene/world.py` (WORLD_CODE) | `HELD_TEST_SEEDS` {20261101: 20261501, 20261102: 20261502, 20261103: 20261503}; `TEST_SETS["held"]`; `M6_HELD = 84`; `test_set_of(seed)`; `m6_scene`: on a held seed 84 items, item i ≥ 42 follows the rule on i − 42 (two things below 28, else three) from its OWN stream `scene:m6:<i>`; items 0–41 byte for byte; any other seed keeps 42 (and still refuses 42+). `split_size(split, tset=None)` («m6»: 84 on held, 42 otherwise); `scenes_for(split, seed, limit, tset=None)` (None → the seed's own set). |
| 4 | `brain/scene/cache.py` (WORLD_CODE) | `_SET_SPLITS["held"] = FRESH_SPLITS` (SPEAK2 included) under `<root>/<ws>/held/cache/<split>`; `build` passes the set to `scenes_for`; `build_world_seed(tset="held")` also checks the held canvases against the OLDER sets' canvases of the same root (`checked_vs_old`, `old_canvases` in `disjoint.json`). **`RUNS` moves to the FRESH root `/data/dev/brain-runs/scene-organ-fm6`** (the precedent at every WORLD_CODE change); `SCENE_ORGAN_RUNS` names the old one. |
| 4 | `brain/scene/run.py` | `CACHE_R_TSETS = ("s1b1", "fresh", "held")` — `cache_r` draws held after the two it drew before; `r_seed_root(root, ws, tset=R_TSET)`; `build_questions_r(root, ws, tset=R_TSET)` (fresh or held; writes `<root>/<ws>/held/questions.json` + `keys.json`); CLI `questions-r --tset held`. Defaults unchanged. |
| 4 | `tools/brain/diag/cache_identity.py` | optional `argv[1]` = the redrawn root to compare (default as before). |
| 5 | `tools/brain/gate_fm6.py` | THE BENCH GATE (docstring = its contract). Law (`young 3`) and fix (`young 3 nearest`) organs trained in LOCKSTEP from the same caches (learn rows compared: must differ 0); both answer held (every mark), fresh (every mark) and s1b1 (pointing, `older/<item>`). Prints per seed: IDENTITY per set (compared · equal · first difference, on every ask that is not a one-young-word pointing — the young set decided from the LAW organ's state; beside it the young asks' answers minus `point`, `hyp`/`pos`/`fix`, `young_d`, `point_rule` must equal the law's; «rule acted outside the young set» must be 0), M6 on held for law and fix (covered, n, chance, unheard, bar 0.70 / n ≥ 30), the paired discordants b / c and the per-seed exact sign p, `meeting_seen` (train truth row 2699). `--pool D1 D2` = the pooled one-sided exact sign test + gap (≥ 0.10, p < 0.001; 20261101 and unseen meetings never pooled). `--plant` = the fix also acts on MATURE one-word phrases; exits 0 only when IDENTITY FAILS. Refuses `--out` under scene-s1b1r, scene-s1b1, scene, scene-organ, scene-organ-fm6, the given roots, `/data/dev/genome-lives`. Writes `<out>/<ws>/fm6.json|txt`, `law-gate-answers.json`, **`fix-gate-answers.json` (the fixed life's PARITY reference: fresh `<item>` + `older/<item>`, gate_alone's shape)**, `law-held-answers.json`, `fix-held-answers.json` (and `planted*` twins under `--plant`). |
| 6 | `genome/brain/lives/BRAIN-LEAN-NEAREST-20261102.genome` | `BRAIN-LEAN-20261102.genome` with exactly `young 3;` → `young 3 nearest;` (one line; `diff` shows line 107 only). |

Tests (new): `tests/genome/test_parse_brain.py` (2 added), `tests/brain/scene/test_learners_fm6.py`, `tests/genome/test_brain_fm6.py`, `tests/genome/test_brain_genomes.py` (class `LeanNearest`), `tests/brain/scene/test_world_fm6.py`, `tests/brain/scene/test_gate_fm6.py`; `tests/brain/scene/test_cache_s1b1r.py`'s RUNS pin moved. Fixtures computed by the UNCHANGED code before any edit: `tests/brain/scene/fixtures/m6_scenes_pre_fm6.json` (m6 0–41 at 2026120x / 2026140x), `tests/brain/scene/fixtures/world_pre_fm6.json` (m6 0–41 at 2026150x; a sample of every split of fresh and s1b1), `tests/genome/fixtures_brain_law_pre_fm6.json` (the law organ's state hash, learn rows, answers, summary on the toy life).

Commits: `52d7662` (fixtures) → `e4f175a` (items 1–2) → `dac238c` (items 3, 6) → `1ab55f8` (world fixture) → `f920130` (item 4) → `fcb0181` (item 5) → this hand-back.

## 2 · Test modules, on `fcb0181` (the last code commit; this hand-back adds docs only)

Each run alone: `env -u PYTHONPATH OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TMPDIR=/data/dev/brain-runs/organ/tmp-f nice -n 19 timeout 60 /usr/bin/python3 -m unittest <module>`; logs in `/data/dev/brain-runs/organ/tmp-f/final-fcb0181/<module>.log`.

```
tests.genome.test_parse_brain            Ran 7 tests in 0.012s   OK
tests.genome.test_brain_fm6              Ran 10 tests in 0.841s  OK
tests.genome.test_brain_organ            Ran 36 tests in 3.149s  OK
tests.genome.test_brain_genomes          Ran 8 tests in 0.035s   OK
tests.creature.test_refusal              Ran 15 tests in 0.112s  OK
tests.brain.scene.test_learners_fm6      Ran 11 tests in 0.727s  OK
tests.brain.scene.test_learners          Ran 18 tests in 1.272s  OK
tests.brain.scene.test_learners_s1b1     Ran 14 tests in 1.516s  OK
tests.brain.scene.test_learners_s1b1r    Ran 15 tests in 1.011s  OK
tests.brain.scene.test_learners_tmem2    Ran 1 test in 0.130s    OK
tests.brain.scene.test_world_fm6         Ran 10 tests in 5.050s  OK
tests.brain.scene.test_world             Ran 16 tests in 4.377s  OK
tests.brain.scene.test_world_s1b1        Ran 7 tests in 0.138s   OK
tests.brain.scene.test_world_s1b1r       Ran 9 tests in 1.898s   OK
tests.brain.scene.test_cache             Ran 8 tests in 0.318s   OK (skipped=1)   ← the real-cache test skips: no cache exists yet under the fresh RUNS
tests.brain.scene.test_cache_s1b1r       Ran 4 tests in 0.094s   OK
tests.brain.scene.test_marks             Ran 10 tests in 0.151s  OK
tests.brain.scene.test_truth_fence       Ran 3 tests in 0.095s   OK
tests.brain.scene.test_gate_fm6          Ran 7 tests in 1.946s   OK
tests.creature.test_brain_mind           Ran 32 tests in 50.471s OK   ← 50 s of the 60 s limit
```
RED logs, each saved BEFORE its implementation edit: `/data/dev/brain-runs/organ/tmp-f/red-test_parse_brain.log` (FAILED failures=5 errors=1), `red-test_learners_fm6.log` (FAILED failures=1 errors=3), `red-test_brain_fm6.log` (FAILED failures=1 errors=4), `red-test_world_fm6.log` (FAILED failures=1 errors=8).
**Not run (heavy, the seat's):** the scene suite as a whole (`discover`), `test_run_s1b1r` and the other run modules that build 80-scene caches and run arms, every creature suite beyond the two above.

## 3 · The seat's commands, in AMENDMENT 1 §2's order

All from `/data/dev/genome-wt-organ-f` on the fix's commit, `PYTHONPATH` unset, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`.

**Step 1 — every life closed** (a redraw is a cache draw, §1). Nothing here.

**Step 2 — every cache redrawn in a FRESH run root, then identity.**
```
/usr/bin/python3 -m brain.scene.run cache-r --root /data/dev/brain-runs/scene-organ-fm6
```
[Likely ≈ 6 CPU-min: the last draw's own record, `scene-organ/logs/cache-r.json`, reads 328 s for toy + s1b1 + fresh; held adds ≈ 9 s a seed (its m6 has 84 rows)]. Read `logs/cache-r.json`: a `<ws>/held` row per seed with `overlap 0`, and `<root>/<ws>/held/cache/disjoint.json` → `checked_vs_old` names all 13 older caches, `overlap: 0`.
```
for ws in 20261101 20261102 20261103; do /usr/bin/python3 -m brain.scene.run questions-r --tset held --world-seed $ws --root /data/dev/brain-runs/scene-organ-fm6; done
```
[Guessing: seconds each]. Read the log line: `M6: 84` per seed.
```
/usr/bin/python3 tools/brain/diag/cache_identity.py /data/dev/brain-runs/scene-organ-fm6
```
[Guessing: 1–2 min, it reads every array]. Must print `caches compared 42 · differing 0` (3 seeds × 14: s1b1 train + 6, fresh 7) and `CONTROL (one bit flipped …): CAUGHT`, exit 0. (It compares the s1b1 and fresh caches only; held has no scored twin.)

**Step 3 — rung 1's gate again on the fix's commit, under `young 3`.**
```
for ws in 20261101 20261102 20261103; do /usr/bin/python3 tools/brain/gate_alone.py --world-seed $ws --glances-root /data/dev/brain-runs/scene-organ-fm6 --out /data/dev/brain-runs/organ/gate-alone-fm6; done
/usr/bin/python3 tools/brain/gate_alone.py --world-seed 20261102 --glances-root /data/dev/brain-runs/scene-organ-fm6 --out /data/dev/brain-runs/organ/gate-alone-fm6 --plant
```
[Likely ≈ 20 s CPU a seed: the record's `organ/gate-alone/20261102/gate.json` reads cpu 18.4 s]. `--glances-root` is REQUIRED: gate_alone's default is still `scene-organ`, whose caches this code now refuses (RAISED 4). Read each `gate.txt`: verdict PASS, `compared` = `equal` = 2,209 / 2,222 / 2,221 (the record), summary equal; the plant: FAIL.

**Step 4 — the bench reads the new set.**
```
for ws in 20261101 20261102 20261103; do /usr/bin/python3 tools/brain/gate_fm6.py --world-seed $ws --out /data/dev/brain-runs/organ/gate-fm6; done
/usr/bin/python3 tools/brain/gate_fm6.py --world-seed 20261102 --out /data/dev/brain-runs/organ/gate-fm6 --plant
/usr/bin/python3 tools/brain/gate_fm6.py --pool /data/dev/brain-runs/organ/gate-fm6/20261102 /data/dev/brain-runs/organ/gate-fm6/20261103
```
[Guessing ≈ 1–1.5 CPU-min a seed: two organs' learning ≈ 2 × 13 s plus three sittings twice]. Read `gate-fm6/<ws>/fm6.txt`:
- IDENTITY: every set `compared` = `equal`, young asks equal-but-pointing, «rule acted outside them 0», PASS. Expect ≈ 1,300 asks a set a seed; the young one-word pointings are the 84 held / 42 fresh / 42 s1b1 M6 items (plus any M1 T1 item whose shape word is young — expected none at 10,000 scenes). The exit code is 0 only on IDENTITY PASS.
- M6 on held: fix covered ≥ 0.70 with n ≥ 30 at 20261102 and 20261103; law beside (a reading); meeting_seen True at both, False at 20261101 (NOT GRADABLE there as signed).
- the plant: `planted.txt` IDENTITY FAIL, exit 0.
- `--pool`: gap ≥ 0.10 and p < 0.001 → PASS (exit 0).

**If the gate passes:** the fixed life runs `genome/brain/lives/BRAIN-LEAN-NEAREST-20261102.genome` (its sets: `fresh s1b1`), and its PARITY is read against the FIX's bench answers:
```
/usr/bin/python3 tools/brain/parity.py --journal <life root>/journal --gate-answers /data/dev/brain-runs/organ/gate-fm6/20261102/fix-gate-answers.json
```
Its M6 is a READING, never evidence (§2).

## 4 · RAISED

1. **The tool test (item 5) and the genome pin (item 6) were written AFTER their subjects** — no red log for either. Items 1–4 were test-first (logs above).
2. **`point_rule` never reads `"band"`.** The brief names `"nearest" | "band"` AND «present ONLY when the nearest rule acted»; both cannot hold, so the field is present only when the rule acted and then reads `"nearest"`. A one-young-word pointing that FELL BACK carries no field and equals the law's answer (the byte-identity the brief asks for).
3. **`Brain.summary()` names the rule only when it is `nearest`** (a law life's calibrate rows, which `creature/mind.py` journals, stay byte-identical). A reader that wants «band» must read its absence.
4. **`gate_alone.py`'s default `--glances-root` is still `/data/dev/brain-runs/scene-organ`** (not edited): under this code `check_code` refuses every cache there, so step 3 must pass `--glances-root /data/dev/brain-runs/scene-organ-fm6`. `tools/brain/null_k1_answers.py` and the diag scripts read `C.RUNS`, which now names the fresh root (empty until step 2).
5. **`cache.RUNS` moved** to `/data/dev/brain-runs/scene-organ-fm6` (precedent: every WORLD_CODE change moved it); `tests/brain/scene/test_cache_s1b1r.py`'s pin moved with it. `run.py`'s `--root` default follows.
6. **«ONE word» is read as `len(phrase) == 1`** in the learner and in the gate's young set. No test item holds a repeated word (§2's co-signer note: no mixed phrase exists either).
7. **The rule acts during LEARNING too**: `Brain.learn`'s T-MEM-2 hook (`health.heard_none`) calls `RWRoad.answer_point`; a young one-word utterance there takes the nearest point, but the hook returns only `none` / `best` (the law's), so learn rows are unchanged — pinned (`test_brain_fm6.Organ.test_learning_is_the_laws`) and read at full size by the gate (`learn rows differing`, must be 0).
8. **The tiny gate test holds no young one-word ask** (40 scenes hold no «dax»); the gate's young branch (`is_young_point`, `strip`) is tested on the organ's toy life (`TestYoungBranch`), the rule itself in `test_learners_fm6` and `test_brain_fm6`. The full-size young branch is first read in step 4.
9. **The held set's disjointness from the older sets** is checked twice: specs in `test_world_fm6` (every held split vs every split of both older sets and 3,000 training scenes, per world seed) and canvases in `build_world_seed(tset="held")` against the older caches present in the same root (cache-r draws them first).
10. **The fixed life's genome carries no edit-attribution line**: the brief says «exactly `young 3` → `young 3 nearest`»; attribution is here and in commit `dac238c`.
11. **`WORLD scene`'s parser still refuses `sitting held`** (`known_ = ("fresh", "s1b1")`, untouched): no life can sit the new set, by design tonight.
12. **Seat traps met**: two edit stamps were TYPED ahead of the clock (22:24, 22:22) and corrected to the read clock (22:18, 22:20) before commit (#50).

## 5 · Files of `WORLD_CODE` changed (every glance cache voided until the seat redraws)
- `genome/machinery.py`
- `brain/scene/world.py`
- `brain/scene/cache.py`
