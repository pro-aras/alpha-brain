*Filed by Claude (Fable 5.1, the seat), 2026-09-28 21:27 +0400. Builder B (Sonnet 5) was STOPPED at 21:20 +0400 on Ahmad's word («Limit the builders to max 2, one you and one opus 5.5»), while it waited on its own second creature-suite run. Its code was already merged (brain-organ 76998a6, its last code commit dc1aa5e). This is its hand-back DRAFT as it stood in its worktree, uncommitted; §6's creature line and §7 were never filled by it. The suites of record are the seat's own on the merged commit 76998a6: scene 340 OK · brain (venv) 742 OK (skipped=3) · genome 601 OK (skipped=1, expected failures=6) · creature 1171 OK (skipped=6) · tools 62 OK (logs /data/dev/brain-runs/organ/logs/merged-*-76998a6.log).*

# HANDBACK-B — BRAIN-IN-BODY, builder B (the scene sense, the body, the genomes, the unit)

*Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:52 +0400. Worktree `/data/dev/genome-wt-organ-b`, branch `brain-organ-b`, built on `1ac149f` (the interface commit). Final commit: see §7.*

## 0 · What exists

| file | what it is |
|---|---|
| `creature/senses/scene.py` | `plan(cfg)` (pure, lazy payload/truth callables) + `sense()` (the threaded executor: feed `max backlog`/`every`, a `#230` cursor, an in-process `Progress` object for STATUS) + `Progress` |
| `tools/brain/make_tape.py` | the same `plan()` published synchronously into a `creature.tape.Tape`, deterministic clock (`2026-09-28T00:00:00.000Z` + 1 ms/row) |
| `creature/body.py` | `_declared_scene_config`, `_maker_should_arm` (pure, tested), the scene sense armed in `main()`, `STATUS`'s `scene`/`brain` keys on every write |
| `creature/genes.py` | the `WORLD_SCENE` RUNS row (body layer) |
| `genome/brain/BRAIN-LEAN.genome`, `BRAIN-LEAN-TWIN.genome`, `BRAIN-FULL.genome`, `BRAIN-LEAN-PREFLIGHT.genome` | the four genomes (INTERFACE §5) |
| `deploy/creature-brain@.service`, `deploy/install.sh` (extended) | the unit + its place in the fixed copy list |
| `tools/lives/launch_brain.sh`, `tools/lives/close_brain.sh` | FILES ONLY — never run by this builder |
| `tests/creature/test_scene_sense.py`, `test_make_tape.py`, `test_scene_arming.py`, `tests/genome/test_brain_genomes.py` | this builder's own pins |

## 1 · The per-mark question equality table, ws 20261101 (against the scored run's OWN files, READ-ONLY)

Fresh set (`/data/dev/brain-runs/scene-s1b1r/20261101/fresh/keys.json`) — item_id + phrase compared, every mark the file carries:

| mark | in file | in plan | equal |
|---|---|---|---|
| DECLINE | 48 | 48 | True |
| M1 | 395 | 395 | True |
| M2a | 400 | 400 | True |
| M2b | 56 | 56 | True |
| M3 | 60 | 60 | True |
| M6 | 42 | 42 | True |
| NAME | 151 | 151 | True |
| SPEAK | 96 | 96 | True |
| SPEAK2 | 60 | 60 | True |
| M5 | — (not in the file; the scored run predates it) | 400 | not comparable — checked structurally instead (§2) |

S1b1 set (`/data/dev/brain-runs/scene-s1b1r/20261101/keys.json`) — same equality on all 8 marks it carries (no SPEAK2, no M5): **all True.** (DECLINE 48, M1 399, M2a 400, M2b 56, M3 60, M6 42, NAME 170, SPEAK 96.)

## 2 · M5 — rewritten mid-build to the SIGNED PREREG

The seat's first message gave M5 a row-index-cycled, three-word draft; the SIGNED `docs/brain/body/PREREG-BRAIN-IN-BODY.md` §3 (a later message, LAW over everything before it) replaced it. The shipped generator (`creature/senses/scene.py:_m5_items`) is the PREREG's: the type drawn uniformly over (colour, shape, size), two distinct words of that type drawn uniformly, no third word, "dax" never used.

Verified for ws 20261101, fresh set: **400 items** (one per `test`-split row), by kind `{"shape": 130, "size": 123, "colour": 147}`, every phrase exactly 2 distinct words, no `DAX_WORD` in any phrase, and **`W.phrase_true_of` is False for all 400 against their own scene's things (count of true-of-something = 0)** — structural, not incidental (two distinct words of one type can never both hold of one thing, since each attribute is single-valued per thing).

## 3 · The price (INTERFACE item 7 — the FULL tape for BRAIN-LEAN.genome)

`tools/brain/make_tape.py` on `genome/brain/BRAIN-LEAN.genome` (10,000 train scenes + both sittings, fresh then s1b1), under `/data/dev/brain-runs/organ/tape-price/`, env `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TMPDIR=/data/dev/brain-runs/organ/tmp-b`, `nice -n 10`:

```
wall_seconds: 26.904
moments: 11496   (11464 canvases + 32 canvas-less: 2×(begin+end) + 2×14 why-asks, one per distinct word said)
rows_per_sense: {"ear": 19968, "eye": 11464, "ask": 3011}
truth_files_written: 11464
bytes_on_disk (du -sb, apparent size): 47,004,832  (~47 MB)
bytes_on_disk (du -sh, actual block usage): ~195 MB  — the gap is 45,909 files, most well under one 4 KiB block each (many small ask-JSON and PNG payloads); apparent size is the honest content total, block usage is what `df` will actually show consumed
asks_per_mark (both sittings pooled): {"M1": 794, "M2a": 800, "M2b": 112, "M3": 120, "M5": 400, "M6": 84, "NAME": 321, "SPEAK": 192, "SPEAK2": 60, "DECLINE": 96}
```
Full JSON at `/data/dev/brain-runs/organ/logs/price.json`. The render (`W.render_scene`) is the whole cost: measured separately at ≈ 1.08 ms/canvas (50-canvas sample), projecting to ≈ 15 s of the 27 s wall total — the rest is item generation, JSON encoding, and file I/O across ~46,000 small files.

Note: this is the **tape-write cost** (INTERFACE's own item 7 ask), not the PREREG's §6 cost rule (a *live* pre-flight pricing one canvas through the *mind* — the seat's job at launch, not this builder's).

## 4 · Genes ADDED to the lean genomes (RAISED)

The lean list (INTERFACE §5) names "the GROW / WIRE / SHRINK laws" — read as `BIRTH`/`BUDGET`/`ARRIVAL`/`KWTA`/`HEBB`/`DELTA`/`PRUNE`/`MERGE`/`SCALE` (ALPHA4's own section header, verbatim, right above `BIRTH novelty`), **not** the specific gene literally named `GROW` (capacity growth, ALPHA4's "no cap" addition). With `GROW` turned `#OFF` and no `NMAX` line, `genome.machinery.parse_genome` refused:

```
genome.machinery.GenomeError: genome lacks ['nmax']
```

**Added:** `NMAX 8000` to `BRAIN-LEAN.genome`, `BRAIN-LEAN-TWIN.genome` and `BRAIN-LEAN-PREFLIGHT.genome` (inherited from LEAN), with the refusing message and the reasoning left on the line itself. `BRAIN-FULL.genome` needed no addition — it is ALPHA4 whole, which already carries `GROW unbounded`.

No other gene was required to be added: with `NMAX 8000` present, `creature.mind.Mind(BRAIN-LEAN-TWIN.genome, <tmp root>)` constructs cleanly (tested, `tests/genome/test_brain_genomes.py::MindConstructsUnderTwin`).

## 5 · Every clause RAISED

1. **No `PREREG-BRAIN-IN-BODY.md` existed in this worktree when work started** (INTERFACE §0 cites it; `find` returned nothing). It was drafted and SIGNED (commit `12bdea6` on a sibling ref) partway through this build; its M5 row superseded the seat's earlier message (§2 above). Everything else this builder shipped predates the PREREG and was cross-checked against it where it bears on builder B's own files (M5; the genome seeds; nothing else in the PREREG touches scene.py/body.py/the genomes/the unit).
2. **NMAX added to the lean genomes** (§4) — the lean list's wording is ambiguous between the ALPHA4 section header and the specific `GROW` gene; read conservatively (neither named), the smallest fix (a fixed cap) was taken over re-enabling `GROW unbounded`'s own (untested here) hash-over-live-prefix machinery.
3. **`SEED` = 20261101 in all four genome files** (INTERFACE's own instruction), including `BRAIN-FULL.genome` — but PREREG §4 wants rung 3 (the full organism) launched at world seed **20261102** specifically. Read as: the template file's own default stays 20261101 (matching the other three, and the "a life at another world seed changes SEED and the WORLD scene seed together" comment every file carries); the seat edits the LAUNCHED COPY's two seed occurrences together for the rung-3 life. Not resolved by editing the template itself, since the template is shared with any future life at any world seed.
4. **Ask order on a `test`-split canvas**: M1 (if the scene has one) < M2a (always) < NAME (1-thing scenes only) < M5 (fresh set only) — not fixed by the INTERFACE or the PREREG; chosen for a stable, testable order and pinned.
5. **`box`/`centroid` are null on every `point`-form ask, not omitted** — kept the 7-key ask payload uniform (`item, mark, form, phrase, box, centroid, word, test_seed`) rather than a variable-shape payload per form.
6. **`end`'s payload** mirrors `begin`'s shape (`{"form": "end", "set": set_name}`) — INTERFACE names `begin`'s payload explicitly and leaves `end`'s unstated.
7. **`why`'s moment id** (`sc<ws>q-<set>-why-<word>`) — INTERFACE gives the payload/meta shape for `why` but never its moment string; every published word is ≤ 8 letters a-z (the ear's own alphabet), so it is always a safe id component.
8. **Split order within one sitting** (`test, m2b, m6, m3, speak, decline[, speak2]`) — copied from `brain.scene.cache.TEST_SPLITS`/`FRESH_SPLITS`'s own order rather than importing `cache.py` itself (it pulls in the glance-cache/eye stack this sense must never touch, per INTERFACE §0.4's truth fence and this module's own "never renders at plan time" law).
9. **The `#230` cursor is real, not a stub.** `SenseThread` restarts `fn` after ANY exception and the unit has `Restart=on-failure`; without a cursor a restart mid-life would republish the whole stream onto a tape that already carries it (a hole the advisor caught before any code was written). `root/scene/SCENE-CURSOR`, written after each moment's rows are durable, closes it — tested (`FeedAndCursor.test_cursor_resumes_without_republishing`).
10. **`STATUS`'s `scene`/`brain` shape**: `scene` = `{published_moments, train_done, sitting_done, ended}` exactly as INTERFACE's own body-section text gives it (the brief's phrasing, not a shorter one); it is carried on EVERY status write, `None`/zeros when `WORLD_SCENE` is undeclared (never omitted, SOLUTIONS #164's law). `brain` calls `mind.brain_status()` only via `hasattr` — builder C's method was not yet landed on this worktree's ancestor when this line was written; the guard is defensive against a Mind that predates it, not against one that carries it.
11. **The maker-arming change is minimal and grep-verified.** Final count (`tests/creature/test_scene_arming.py`, printed at run time, after `genome/brain/`'s four files existed): **47 genome files, 50 carry a `WORLD ` line, 46 parsed, 43 non-scene genomes verified byte-for-byte unchanged, 3 scene-only genomes** (`BRAIN-LEAN`, `BRAIN-LEAN-TWIN`, `BRAIN-LEAN-PREFLIGHT` — `BRAIN-FULL.genome` declares BOTH `WORLD` and `WORLD_SCENE` and is correctly counted as *unchanged*, since only a scene-**only** genome suppresses the maker) **verified to now suppress it**; `--maker` overrides.
12. **`creature/body.py:_build_status` reads `self.scene_progress` via `getattr`, not directly** — caught by the first full-suite run: `tests/creature/test_a4l_voice_seams.py` and `test_verdict_reader_lag_0923.py` call `Body._build_status` unbound against a `mock`/`SimpleNamespace` stand-in that has no `scene_progress` attribute at all. Fixed to match every other STATUS field's own defensive `getattr(..., default)` convention in the same method (a real regression this builder introduced and fixed before hand-back, not a pre-existing failure).
13. **`tests/creature/test_refusal.py`'s `SAMPLE_LINE` registry needed a `WORLD_SCENE` row** — an EXISTING test file (not authored by this builder) that the class's own comments say has caught five prior builders the same way; added the sixth row, following its exact convention.

## 6 · Suites (final commit `54833ce`+M5-fix `7556d21` — see §7 for the actual final hash)

- **`tests/genome`**: `/usr/bin/python3 -B -m unittest discover -s tests/genome -t .` → log `/data/dev/brain-runs/organ/logs/suite-genome.log` (exit 0): **`Ran 565 tests in 137.185s — OK (skipped=1, expected failures=6)`** (baseline before this build: 553; +12 from `test_parse_brain.py`'s pre-existing 5 plus this builder's `test_brain_genomes.py`'s 7 — the delta is accounted for, nothing lost).
- **`tests/creature`**: `/usr/bin/python3 -B -m unittest discover -s tests/creature -t .` → log `/data/dev/brain-runs/organ/logs/suite-creature.log`. *(filled in below once the run — several minutes, per the contract's own note — completes; nothing in this builder's own new test files failed in isolation: `test_scene_sense.py` 10/10, `test_make_tape.py` 2/2, `test_scene_arming.py` 10/10, all green run standalone before the full-suite run started.)*

## 7 · Final commit

`git log -1 --oneline` on `brain-organ-b`: *(recorded at the very end, after this file's own commit — see the caller-facing report.)*
