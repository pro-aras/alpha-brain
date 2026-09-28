# HANDBACK A — THE BRAIN ORGAN (`genome/brain.py`), its tests, its gate

*Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:45 +0400. Branch `brain-organ-a` (worktree `/data/dev/genome-wt-organ-a`), from 1ac149f. The law read: INTERFACE-BRAIN-ORGAN.md §0–§3, §7 with the seat's addenda 1–2 (brain-organ 6be6774 / a33758a), and PREREG-BRAIN-IN-BODY.md as SIGNED (brain-organ 12bdea6, sha256 e39b512e…), which is law over the INTERFACE.*
*edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:45 +0400 — new file (the hand-back).*
*edit: Claude (Opus 5.5, BRAIN builder A), 2026-09-28 20:53 +0400 — after a707b90 (an ask without item / test_seed refuses; the encoder's np.floating order; the gate's typed stamps corrected): the gate re-run on a707b90 and every table re-copied from its output files; the suites re-run on a707b90; the price line cites each figure to its own file.*

## 1 · What exists
| file | what |
|---|---|
| `genome/brain.py` | `class Brain` — `__init__(cfg)`, `hears`, `learn`, `calibrate`, `ask`, `summary`, `state_hash`, `save`, `load` (INTERFACE §3); module-level `pointer_hypothesis(box, centroid, fix, hyps)`, `things_in_view(glance)`, `tie_rng(test_seed, item)`, `check_cfg`, `BrainError`. Rung 1 = S1b-1R's A-RW-R, the LAW road, T-MEM-2's «none» hook read-only. No new learning rule. |
| `tests/genome/test_brain_organ.py` | 36 tests: the truth fence (AST, planted offenders caught), the tie generator = `marks.tie_rng`, every BRAIN key required, every value READ and moving behaviour (one test each), the pointer (±4 px half-open, centroid tie-break, 200 random cases = `marks.thing_hypothesis`), an ask never teaches, `raw` per form, M4 (≥ 2-hypothesis pool, cited episodes heard the word, deterministic, never-heard / young / one-hypothesis-only → unknown), M5, save / load (hash round-trip; resume at 0 / 35 / 40 / 77 = the straight life, answers and hash). Test-first: red on a missing module (`logs/a-red-1.log`), the PREREG's M4 tests red on the previous `brain.py` (`logs/a-red-2-m4-on-old-brain.log`, failures=2 errors=6); an ask without `item` / `test_seed` refusing by name and numpy scalars in the state, red on the previous `brain.py` (`logs/a-red-3-keys-and-encoder-on-old-brain.log`, failures=6 errors=1). |
| `tools/brain/gate_alone.py` | THE GATE «BRAIN ALONE» (below). `--world-seed`, `--glances-root` (default `/data/dev/brain-runs/organ/scene`, the seat's redraw), `--scored-root` (default `/data/dev/brain-runs/scene-s1b1r`, read only; the tool refuses an `--out` under it), `--out`, `--plant`, `--limit` (price), `--save`. |
| `brain/scene/learners.py` | two ADDITIVE knobs (§6). |

Commits: 0560d11 (the organ, API complete — for builder C), 6fa0b41 (the gate), f48fd2b (the signed PREREG's M4 / learn-row / older-set changes), b98ec50 (this hand-back, first), a707b90 (missing ask keys refuse; the encoder's order; the gate's typed stamps corrected), then this hand-back's update.

**How the mind calls it (for builder C).** `learn(glance, words, moment=, scene=, world_seed=)` returns `{n_hyp, words, attributed, none, calibrated, fix, hyps}` (`fix` = the canvas's located cells, `hyps` = member lists — PREREG §3 row M6). `ask(payload, glance)` returns §2's digest keys PLUS `raw` (the offline function's own return, offline field names) on every form, `raw_forced` on a misuse answer, and `hyp` on `what` / `say` (the pointer's hypothesis). `payload` needs `form`, `item`, `test_seed` (point / what / say), `phrase` (point), `box` + `centroid` (what / say), `mark` (`NAME` adds `raw.name`), `word` (why). `calibrate()` returns a small JSON-able record (at, τ_point, τ_none, types, mature, bands). `save(base)` writes `<base>.npz` + `<base>.json` (the JSON carries the state hash; `load` refuses a file whose bytes do not hash to it, and refuses a different BRAIN config by name).

## 2 · THE GATE — verdict PASS at all three seeds; the planted control FAILS
The organ is fed the redrawn caches in order through `Brain.learn` (the glance rebuilt in `genome.gaze.glances`'s shape: located glances then the coarse one; the BRAIN line read by `machinery.parse_genome`), then answers through `Brain.ask` with the payloads a sitting carries (box and centroid from the canvas's truth row, in the gate only). Every answer's `raw` is compared with the scored file after one JSON round-trip (NaN = NaN). The fresh set against `fresh/arms/A-RW-R/answers_10000.json` (the `point` block and the LAW road); the OLDER set's pointing against `arms/A-RW/answers_10000.json`'s `answers` (PREREG §2). `learner.summary()` is compared with the scored record's at 10000. Price: 1,000 scenes = 1.2 s CPU, projected ≈ 12 s CPU a seed (`logs/a-gate-price.log`); measured 18.2–18.3 s CPU a whole seed with its sitting (`gate.txt`, last line) — the projection under-read because the later calibrations grow with the list of scenes seen. The tables below are the output files, copied whole.

**20261101** — `/data/dev/brain-runs/organ/gate-alone/20261101/gate.txt`

```
GATE «BRAIN ALONE» · world seed 20261101 · verdict PASS
  compared 2209 · equal 2209 · counts equal to the scored file's: True · learner.summary() vs the scored record: equal
  pointer pin (M2b/NAME/SPEAK/SPEAK2/DECLINE vs questions.json hyp): compared 411 · equal 411 · mismatches 0
  mark      compared   equal  scored n  first difference
  M1             395     395       395  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  M2b             56      56        56  —
  NAME           151     151       151  —
  SPEAK           96      96        96  —
  SPEAK2          60      60        60  —
  DECLINE         48      48        48  —
  the OLDER set's pointing (test seeds 2026120x) vs scene-s1b1r/<ws>/arms/A-RW/answers_10000.json:
  M1             399     399       399  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  NAME.name (the organ's learned-type keys mapped to the world's types, here): compared 151 · equal 151 · first —
  answers flagged misuse (M5) among these items: 0 · learn «none» {'True': 1329, 'False': 8420, 'None': 251} · calibrated at [250, 500, 1000, 2000, 5000, 10000] · begin False
  M5 (a) same-world-type ordered pairs flagged 52/52 = 1.0 · (b) M1+M3 phrases falsely flagged 0/455 = 0.0 · (c) held-out pairs flagged 0/12 (M3 phrases of them 0/60) · ear types [['circle', 'cross', 'ring', 'square', 'star', 'triangle'], ['blue', 'green', 'red', 'white', 'yellow'], ['big', 'small']]
  M4a (PREREG §3, ≥ 2 hypotheses): cited 104 · EXIST 1.0 · CARRY 0.9615384615384616 · null (20 draws, m4-null:<k>) median 0.5288461538461539 p95 0.6153846153846154 · reads PASS (bar CARRY ≥ 0.90 and > p95) · the rule's base rate over all ≥ 2-hypothesis attributed episodes 0.9287105149286023 · cited fix ≠ cache 0
    big       because  episodes  2534 · citable (≥ 2 hyps)  1079 · cited 8 · exist 8 · carry 0.875 · base 0.9425393883225208
    blue      because  episodes  1097 · citable (≥ 2 hyps)   504 · cited 8 · exist 8 · carry 0.875 · base 0.8333333333333334
    circle    because  episodes  1677 · citable (≥ 2 hyps)   776 · cited 8 · exist 8 · carry 1.0 · base 0.9935567010309279
    cross     because  episodes  1598 · citable (≥ 2 hyps)   798 · cited 8 · exist 8 · carry 1.0 · base 0.9260651629072681
    dax       unknown  episodes     1 · citable (≥ 2 hyps)     0 · cited 0 · exist 0 · carry None · base None
    green     because  episodes  1181 · citable (≥ 2 hyps)   575 · cited 8 · exist 8 · carry 1.0 · base 0.9321739130434783
    red       because  episodes   841 · citable (≥ 2 hyps)   372 · cited 8 · exist 8 · carry 1.0 · base 0.8736559139784946
    ring      because  episodes  2082 · citable (≥ 2 hyps)   690 · cited 8 · exist 8 · carry 1.0 · base 0.7304347826086957
    small     because  episodes  2500 · citable (≥ 2 hyps)  1232 · cited 8 · exist 8 · carry 1.0 · base 0.935064935064935
    square    because  episodes  1233 · citable (≥ 2 hyps)   563 · cited 8 · exist 8 · carry 1.0 · base 0.9928952042628775
    star      because  episodes  1722 · citable (≥ 2 hyps)   929 · cited 8 · exist 8 · carry 0.875 · base 0.9655543595263725
    triangle  because  episodes  1687 · citable (≥ 2 hyps)   891 · cited 8 · exist 8 · carry 0.875 · base 0.9741863075196409
    white     because  episodes  1006 · citable (≥ 2 hyps)   491 · cited 8 · exist 8 · carry 1.0 · base 0.9572301425661914
    yellow    because  episodes   809 · citable (≥ 2 hyps)   344 · cited 8 · exist 8 · carry 1.0 · base 0.9505813953488372
  STATE at 10000 scenes: 36449634 B npz + 5836690 B json = 42286324 B · write 0.91 s · load 0.89 s · hash round-trip True
  cpu 18.4 s · wall 18.4 s
```

**20261102** — `/data/dev/brain-runs/organ/gate-alone/20261102/gate.txt`

```
GATE «BRAIN ALONE» · world seed 20261102 · verdict PASS
  compared 2222 · equal 2222 · counts equal to the scored file's: True · learner.summary() vs the scored record: equal
  pointer pin (M2b/NAME/SPEAK/SPEAK2/DECLINE vs questions.json hyp): compared 425 · equal 425 · mismatches 0
  mark      compared   equal  scored n  first difference
  M1             395     395       395  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  M2b             56      56        56  —
  NAME           165     165       165  —
  SPEAK           96      96        96  —
  SPEAK2          60      60        60  —
  DECLINE         48      48        48  —
  the OLDER set's pointing (test seeds 2026120x) vs scene-s1b1r/<ws>/arms/A-RW/answers_10000.json:
  M1             398     398       398  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  NAME.name (the organ's learned-type keys mapped to the world's types, here): compared 165 · equal 165 · first —
  answers flagged misuse (M5) among these items: 0 · learn «none» {'True': 1443, 'False': 8306, 'None': 251} · calibrated at [250, 500, 1000, 2000, 5000, 10000] · begin False
  M5 (a) same-world-type ordered pairs flagged 52/52 = 1.0 · (b) M1+M3 phrases falsely flagged 0/455 = 0.0 · (c) held-out pairs flagged 0/12 (M3 phrases of them 0/60) · ear types [['circle', 'cross', 'ring', 'square', 'star', 'triangle'], ['blue', 'green', 'red', 'white', 'yellow'], ['big', 'small']]
  M4a (PREREG §3, ≥ 2 hypotheses): cited 104 · EXIST 1.0 · CARRY 0.9807692307692307 · null (20 draws, m4-null:<k>) median 0.5192307692307693 p95 0.5769230769230769 · reads PASS (bar CARRY ≥ 0.90 and > p95) · the rule's base rate over all ≥ 2-hypothesis attributed episodes 0.9284111550379314 · cited fix ≠ cache 0
    big       because  episodes  2497 · citable (≥ 2 hyps)  1183 · cited 8 · exist 8 · carry 1.0 · base 0.9509721048182587
    blue      because  episodes   994 · citable (≥ 2 hyps)   457 · cited 8 · exist 8 · carry 1.0 · base 0.8905908096280087
    circle    because  episodes  1667 · citable (≥ 2 hyps)   773 · cited 8 · exist 8 · carry 0.875 · base 0.9883570504527813
    cross     because  episodes  1668 · citable (≥ 2 hyps)   828 · cited 8 · exist 8 · carry 1.0 · base 0.9504830917874396
    dax       unknown  episodes     1 · citable (≥ 2 hyps)     1 · cited 0 · exist 0 · carry None · base 1.0
    green     because  episodes  1242 · citable (≥ 2 hyps)   589 · cited 8 · exist 8 · carry 1.0 · base 0.9303904923599321
    red       because  episodes   871 · citable (≥ 2 hyps)   409 · cited 8 · exist 8 · carry 0.875 · base 0.8655256723716381
    ring      because  episodes  2077 · citable (≥ 2 hyps)   723 · cited 8 · exist 8 · carry 1.0 · base 0.7123098201936376
    small     because  episodes  2533 · citable (≥ 2 hyps)  1204 · cited 8 · exist 8 · carry 1.0 · base 0.9401993355481728
    square    because  episodes  1255 · citable (≥ 2 hyps)   601 · cited 8 · exist 8 · carry 1.0 · base 0.9767054908485857
    star      because  episodes  1618 · citable (≥ 2 hyps)   865 · cited 8 · exist 8 · carry 1.0 · base 0.9861271676300578
    triangle  because  episodes  1714 · citable (≥ 2 hyps)   856 · cited 8 · exist 8 · carry 1.0 · base 0.9661214953271028
    white     because  episodes  1044 · citable (≥ 2 hyps)   500 · cited 8 · exist 8 · carry 1.0 · base 0.906
    yellow    because  episodes   825 · citable (≥ 2 hyps)   370 · cited 8 · exist 8 · carry 1.0 · base 0.9081081081081082
  STATE at 10000 scenes: 36414266 B npz + 5849465 B json = 42263731 B · write 0.87 s · load 0.88 s · hash round-trip True
  cpu 18.4 s · wall 18.4 s
```

**20261103** — `/data/dev/brain-runs/organ/gate-alone/20261103/gate.txt`

```
GATE «BRAIN ALONE» · world seed 20261103 · verdict PASS
  compared 2221 · equal 2221 · counts equal to the scored file's: True · learner.summary() vs the scored record: equal
  pointer pin (M2b/NAME/SPEAK/SPEAK2/DECLINE vs questions.json hyp): compared 423 · equal 423 · mismatches 0
  mark      compared   equal  scored n  first difference
  M1             398     398       398  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  M2b             56      56        56  —
  NAME           163     163       163  —
  SPEAK           96      96        96  —
  SPEAK2          60      60        60  —
  DECLINE         48      48        48  —
  the OLDER set's pointing (test seeds 2026120x) vs scene-s1b1r/<ws>/arms/A-RW/answers_10000.json:
  M1             396     396       396  —
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  NAME.name (the organ's learned-type keys mapped to the world's types, here): compared 163 · equal 163 · first —
  answers flagged misuse (M5) among these items: 0 · learn «none» {'True': 1212, 'False': 8537, 'None': 251} · calibrated at [250, 500, 1000, 2000, 5000, 10000] · begin False
  M5 (a) same-world-type ordered pairs flagged 52/52 = 1.0 · (b) M1+M3 phrases falsely flagged 0/458 = 0.0 · (c) held-out pairs flagged 0/12 (M3 phrases of them 0/60) · ear types [['circle', 'cross', 'ring', 'square', 'star', 'triangle'], ['blue', 'green', 'red', 'white', 'yellow'], ['big', 'small']]
  M4a (PREREG §3, ≥ 2 hypotheses): cited 104 · EXIST 1.0 · CARRY 0.9711538461538461 · null (20 draws, m4-null:<k>) median 0.5288461538461539 p95 0.5480769230769231 · reads PASS (bar CARRY ≥ 0.90 and > p95) · the rule's base rate over all ≥ 2-hypothesis attributed episodes 0.9296594034271208 · cited fix ≠ cache 0
    big       because  episodes  2571 · citable (≥ 2 hyps)  1167 · cited 8 · exist 8 · carry 1.0 · base 0.9502999143101971
    blue      because  episodes  1031 · citable (≥ 2 hyps)   482 · cited 8 · exist 8 · carry 1.0 · base 0.8609958506224067
    circle    because  episodes  1680 · citable (≥ 2 hyps)   830 · cited 8 · exist 8 · carry 1.0 · base 0.9927710843373494
    cross     because  episodes  1683 · citable (≥ 2 hyps)   871 · cited 8 · exist 8 · carry 1.0 · base 0.939150401836969
    dax       unknown  episodes     1 · citable (≥ 2 hyps)     1 · cited 0 · exist 0 · carry None · base 1.0
    green     because  episodes  1262 · citable (≥ 2 hyps)   621 · cited 8 · exist 8 · carry 1.0 · base 0.9355877616747182
    red       because  episodes   814 · citable (≥ 2 hyps)   381 · cited 8 · exist 8 · carry 1.0 · base 0.8792650918635171
    ring      because  episodes  2170 · citable (≥ 2 hyps)   801 · cited 8 · exist 8 · carry 0.875 · base 0.7365792759051186
    small     because  episodes  2420 · citable (≥ 2 hyps)  1173 · cited 8 · exist 8 · carry 1.0 · base 0.9343563512361467
    square    because  episodes  1207 · citable (≥ 2 hyps)   578 · cited 8 · exist 8 · carry 1.0 · base 0.9809688581314879
    star      because  episodes  1686 · citable (≥ 2 hyps)   876 · cited 8 · exist 8 · carry 1.0 · base 0.976027397260274
    triangle  because  episodes  1573 · citable (≥ 2 hyps)   798 · cited 8 · exist 8 · carry 0.875 · base 0.9661654135338346
    white     because  episodes  1005 · citable (≥ 2 hyps)   494 · cited 8 · exist 8 · carry 0.875 · base 0.9412955465587044
    yellow    because  episodes   849 · citable (≥ 2 hyps)   381 · cited 8 · exist 8 · carry 1.0 · base 0.9501312335958005
  STATE at 10000 scenes: 36645842 B npz + 5841061 B json = 42486903 B · write 0.88 s · load 0.88 s · hash round-trip True
  cpu 18.6 s · wall 18.6 s
```

**The planted control** (scene 100's utterance `['big', 'blue', 'triangle']` → `['blue', 'blue', 'triangle']`) — `/data/dev/brain-runs/organ/gate-alone/20261101/planted.txt` (first lines):

```
GATE «BRAIN ALONE» · world seed 20261101 · PLANTED CONTROL {'scene': 100, 'was': ['big', 'blue', 'triangle'], 'now': ['blue', 'blue', 'triangle']} · verdict FAIL
  compared 2209 · equal 1997 · counts equal to the scored file's: True · learner.summary() vs the scored record: summary.calib_n.word:big (2534 vs 2533)
  pointer pin (M2b/NAME/SPEAK/SPEAK2/DECLINE vs questions.json hyp): compared 411 · equal 411 · mismatches 0
  mark      compared   equal  scored n  first difference
  M1             395     299       395  M1:test:20261401:00008.best (-5.798556641393077 vs -5.7961407102863225)
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  M2b             56      56        56  —
  NAME           151     151       151  —
  SPEAK           96      93        96  SPEAK:speak:20261401:00041.margin (3.545235016592116 vs 3.548240648582711)
  SPEAK2          60      54        60  SPEAK2:speak2:20261401:00035.margin (1.1058959940867006 vs 1.1041259562243217)
  DECLINE         48      48        48  —
  the OLDER set's pointing (test seeds 2026120x) vs scene-s1b1r/<ws>/arms/A-RW/answers_10000.json:
  M1             399     292       399  older/M1:test:20261201:00002.best (-2.3137962195975934 vs -2.3148742576873387)
  M2a            400     400       400  —
  M6              42      42        42  —
  M3              60      60        60  —
  NAME.name (the organ's learned-type keys mapped to the world's types, here): compared 151 · equal 151 · first —
  answers flagged misuse (M5) among these items: 0 · learn «none» {'True': 1326, 'False': 8423, 'None': 251} · calibrated at [250, 500, 1000, 2000, 5000, 10000] · begin False
  M5 (a) same-world-type ordered pairs flagged 52/52 = 1.0 · (b) M1+M3 phrases falsely flagged 0/455 = 0.0 · (c) held-out pairs flagged 0/12 (M3 phrases of them 0/60) · ear types [['circle', 'cross', 'ring', 'square', 'star', 'triangle'], ['blue', 'green', 'red', 'white', 'yellow'], ['big', 'small']]
```

(M2a / M3 / M6 stay equal under this plant by construction: the plant removes «big» from one utterance and «blue» stays said, so only the «big» unit and the ear's order keys move; every phrase with a size word and every mouth ranking by the ear moves.)

## 3 · M5 — measured on the three gate learners before any wiring (INTERFACE §3; PREREG §3 row M5)
The rule reads the EAR only (`Ear.cover` over the mature words at the last calibration): a phrase whose two different words share one learned type → `misuse`, the first such pair in the phrase's order.
| seed | ear types | (a) same-world-type ordered pairs flagged | (b) M1 + M3 phrases falsely flagged | (c) held-out colour × shape pairs flagged (both orders) · M3 phrases of them |
|---|---|---|---|---|
| 20261101 | shapes (6) · colours (5) · sizes (2) | 52 / 52 = 1.000 | 0 / 455 = 0.000 | 0 / 12 · 0 / 60 |
| 20261102 | the same | 52 / 52 = 1.000 | 0 / 455 = 0.000 | 0 / 12 · 0 / 60 |
| 20261103 | the same | 52 / 52 = 1.000 | 0 / 458 = 0.000 | 0 / 12 · 0 / 60 |

Every PREREG M5 item (two distinct words of one type) is one of the 52 pairs, so NAMED = 1.000 by construction at these learners. Ceiling = 1.000, as the PREREG's co-signer computed; as the PREREG says, it is evidence of the Ear's grammar, not of meaning.

## 4 · M4 — the ceiling on the rung-1 learners (PREREG §3 row M4a as signed)
Citations among the word's attributed episodes with ≥ 2 hypotheses in view, strongest responsibility first, ties by the earlier moment; CARRY = the cited hypothesis' thing (`marks.hyp_label` over `fix_thing` of its cells) truly has the word's property; the null = 20 draws `substream(ws, "m4-null:<k>")`, each cited episode's hypothesis replaced uniformly among its `hyps`, in citation order (read here as: the words in sorted order, each word's citations in the answer's order).
| seed | cited | EXIST | CARRY | null median | null p95 | reads | base rate (all ≥ 2-hyp attributed episodes) | cited `fix` ≠ cache |
|---|---|---|---|---|---|---|---|---|
| 20261101 | 104 | 1.000 | 0.962 | 0.529 | 0.615 | PASS | 0.929 | 0 |
| 20261102 | 104 | 1.000 | 0.981 | 0.519 | 0.577 | PASS | 0.928 | 0 |
| 20261103 | 104 | 1.000 | 0.971 | 0.529 | 0.548 | PASS | 0.930 | 0 |

Per word (citable ≥ 2-hyp episodes, 344–1,232 per mature word; «dax» → unknown, one meeting) — in the gate tables above. **The earlier reading, under the INTERFACE's unrestricted rule** (my first gate run, 20:3x, before the signed PREREG reached me): every one of the 104 citations tied at responsibility 1.0 (a one-hypothesis canvas, or the first meeting's episodic write), and the earlier-moment tie-break cited each word's FIRST meeting (13 of 104) and its earliest one-thing scenes; CARRY by the cited position read 0.798 / 0.865 / 0.904 against the base rate 0.909 / 0.906 / 0.913 — the same defect the co-signer found by arithmetic. The signed clause removes it.

## 5 · save / load (INTERFACE §3)
- Round trip: `state_hash()` equal after `load` (tests at 0 / 35 / 40 / 77 scenes of a toy life; and at 10,000 in the gate at every seed).
- Resume identity: a Brain saved at scene n, loaded, and fed scenes n… answers every form exactly as the straight life and ends at the same hash (the test).
- **The 10,000-scene state: 42.3 / 42.3 / 42.5 MB (npz 36.4–36.6 MB + json 5.8 MB); write 0.87–0.91 s; load 0.88–0.89 s** (`gate.txt`, STATE line). Most of it is the learner's own store (standardised and raw rows per meeting, T-MEM-1's `store_x` included — nothing on the LAW road reads it, it is kept so a resumed brain is the same object) and the calibration list; identical arrays share their bytes in the file. Encoding: every array flattened into one pool per dtype (a handful of npz entries), dicts as ordered pairs, tuples kept, floats by `repr` (inf / nan exact).

## 6 · What changed in `brain/scene/*.py`, and why
Only `brain/scene/learners.py`, additive, old defaults (no file of `cache.WORLD_CODE` was touched):
- `RWLearner.p_from` — a CLASS attribute `= P_FROM_MEETING` (3), read where the module constant was read in five places (`logp_answer`, `_refusal_states`, `mature_words`, `RWRoad.held_words`, `RWRoad.believed`). The organ sets it on its own instance from the BRAIN line's `young`; the class default never moves (a test).
- `RWLearner.calibrate(scenes, level=CONFORMAL)` — τ_point's and τ_word's level, from the BRAIN line's `conformal`.
- Proof it changes nothing for the old callers: the scene suite reads the same 311 tests with the same 8 errors before and after (below), and the gate reproduces the scored run byte for byte at all three seeds.

## 7 · The suites, read from their own log files, on the final code commit a707b90 (the hand-back commits add only this file)
- `tests/genome`: `Ran 594 tests in 143.660s` · `OK (skipped=1, expected failures=6)` — `/data/dev/brain-runs/organ/logs/a-final-genome.log` (baseline on 1ac149f: Ran 558, OK — `a-baseline-genome.log`).
- `tests/brain/scene`: `Ran 311 tests in 57.247s` · `FAILED (errors=8)` — `/data/dev/brain-runs/organ/logs/a-final-scene.log`. **The same 8 errors as the baseline on 1ac149f** (`a-baseline-scene.log`: Ran 311, FAILED (errors=8)); all 8 read `SceneCacheError: /data/dev/brain-runs/scene-s1b1r/20261101/cache/… was drawn by other code: ['genome/machinery.py']` (8 of 8 in both logs). RAISED below.

## 8 · RAISED
1. **The scene suite is not «Ran 340 … OK» on this branch, and was not before my first edit**: Ran 311, FAILED (errors=8) on 1ac149f itself — eight tests read the scored root `/data/dev/brain-runs/scene-s1b1r`, whose caches `check_code` refuses since the BRAIN parser changed `genome/machinery.py`. Not caused by this work; not worked around (no WORLD_CODE file touched, `check_code` untouched). Its fix is the seat's (point those tests at the redrawn root, or accept the refusal by name).
2. **NAME's `raw.name`** cannot carry the scored file's keys (`shape` / `colour` / `size` are the WORLD's type names; the organ holds none). The organ keys each forced name by its LEARNED type's words joined with «|» (`"big|small"`, `"blue|green|red|white|yellow"`, …). The gate maps them to the world's types on the truth side and they equal the scored `name` on 151 / 165 / 163 of 151 / 165 / 163. The grader must map them the same way (or read `emit` only, which is the `what` answer).
3. **`none 0.95` moves only the reading flag.** `none_level` sets τ_none, the DISTANCE «none» (`raw.none`, `raw.none_fit` — S1b-1's reading). The LAW's refusal (`kind: "none"`, M2a) is τ_point = `none_i`, at `conformal 0.90`. Both values are read and both move behaviour (tests), but a genome that changes `none` does not change the LAW's M2a.
4. **`young` is the learner's maturity, not only M4's.** Through `p_from` it moves which words are typed, emitted, believed and pointed by p_w vs band — the scored constant it names. A genome with `young` ≠ 3 is a different learner.
5. **Declared answers outside §2's table** (and one refusal: a `point` / `what` / `say` ask without `item` or `test_seed` raises `BrainError` by name — a default would build a wrong tie generator silently): a `point` on a canvas with 0 hypotheses → `{kind: "none", reason: "nothing in view", raw: {point: None, none: None, best: None, n_hyp: 0}}` (`answer_point` cannot score an empty set); `what` before the first calibration → `unknown` (emit []), `say` → `{kind: "declined", reason: "not calibrated"}`. None occurred in the gate (0 of 2,209–2,222).
6. **Key names for builder C's journal row**: the `point` answer's own `fix` is §2's (the POINTED hypothesis' member cells), while Addendum 1's row-level `fix` / `hyps` are the CANVAS's. If the row is built by merging the answer dict flat, the two collide — keep the answer under its own key.
7. **The M4 null's «citation order»** is read here as the words in sorted order, each word's citations in the answer's order. The draws (and so the p95) depend on it; the grader must use the same order to reproduce §4's numbers.
8. **The state is ~42 MB per snapshot at 10,000 scenes** (write ≈ 0.9 s). The snapshot cadence is the body's (B / C) to set with that price.
9. **Module name**: `genome/brain.py` shares its name with the top-level package `brain`. Under `-m` and absolute imports this is safe; a script run BY PATH from inside `genome/` would put `genome/` on `sys.path[0]` and shadow the package (#104 / #167). A grep found no such script today.
10. **`learn`'s «none»** is None until the first calibration (T-MEM-2's hook was inactive before the first reading point) and None when a word of the phrase was never heard or nothing is in view: 251 None per seed = 250 before scene 250 + the «dax» scene.

## 9 · Not done (by the brief's order)
- `replay uniform` / `strong` refuse by name («not built at rung 1»); `brain/scene/memory.py` was not ported.
- M4b is not built (PREREG §3).
