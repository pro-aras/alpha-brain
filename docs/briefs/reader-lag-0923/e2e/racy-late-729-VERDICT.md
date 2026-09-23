# G4 VERDICT — FAIL

root `/data/dev/genome-wt-reader-lag/scratch/e2e/racy-late-729` · genome `/data/dev/genome-wt-reader-lag/scratch/e2e/racy-late-729/GENOME.genome` (sha d384b6077f6d0732) · read 2026-09-23T13:39:57+00:00 by `tools/verdict_g4.py v3.4 (2026-09-23: v3.3 + READER-LAG-0923 — the read is CUT at the mind's last consumed seq when the mind is behind its world (ledger/STATUS last_seq, the journal's last mind row on a closed record): every twin replays the cut tape, closed_whole is judged against the cut, every mark reads the cut; ALIVE reads the world's hours and gaps, the mind's counters over the hours it lived; the unconsumed tail printed under ALIVE, COST and REPLAY; v3.3: EVOLVE's void round apart; COST as §8b's function of cells; ACT's census over the game's acts, ≥ 95 % on the last 100; SENTENCE's missions per episode; QUESTION once per question, the lexicon counted; READ's fixed-seed sample of shelf-only words + its blind twin; THREAD's gaps attributed to sleeps; STAGE's readiness series + the mind's stage events carried; not gradable never failed; the plant clauses not gradable before the plant)` (PREREG §5 as amended; the reader's rules §16) · 1.0 h

**The read is CUT at the mind's last consumed seq 729** — it lived 0.2546 of the window's world hours; LAG: the mind's last consumed seq 729 (journal) of the tape's 850: 121 rows / 0.0445 world h unconsumed; the read is CUT at it (121 rows / 0.0445 world h of the 850-row window the mind never lived; it lived 0.2546 h); backlog (body rows, n 18): max 0 at 2026-09-22T20:39:55.612Z, last 0, first > 100 never; STATUS backlog 121 (reconciles with the tape: False)

| mark | bar | reading | verdict |
|---|---|---|---|
| ALIVE | 1.0 h under the unit, NRestarts 0, every counter moved every hour, no sense dead > 60 s | 0.299 h on tape · moved every hour True · the mind's counters graded over the 0 world h it fully lived; beyond its reach (hours [0]) the wall-clock snapshots only · max gap eye/ear [5.0, 5.0] s · sense restarts 0 · crashes 0 · NRestarts None · LAG: the mind's last consumed seq 729 (journal) of the tape's 850: 121 rows / 0.0445 world h unconsumed; the read is CUT at it (121 rows / 0.0445 world h of the 850-row window the mind never lived; it lived 0.2546 h); backlog (body rows, n 18): max 0 at 2026-09-22T20:39:55.612Z, last 0, first > 100 never; STATUS backlog 121 (reconciles with the tape: False) | FAIL |
| REPLAY / (vii) | byte-identical mind rows; the plant caught | vs live DIVERGED at (729, 'act') · two replays identical · 757 rows · plant at seq 368 caught True · masked hash (reader 289d2a4 ≠ life 74c661d) · closed whole True at the cut seq 729 (the mind's last consumed seq) · LAG: the mind's last consumed seq 729 (journal) of the tape's 850: 121 rows / 0.0445 world h unconsumed; the read is CUT at it (121 rows / 0.0445 world h of the 850-row window the mind never lived; it lived 0.2546 h); backlog (body rows, n 18): max 0 at 2026-09-22T20:39:55.612Z, last 0, first > 100 never; STATUS backlog 121 (reconciles with the tape: False) | FAIL |
| (i) | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.882 Q2 0.818 Q3 0.927 Q4 0.991 (chance 0.071; all words Q1 0.606) | PASS |
| (ii) | ≤ .20 (all 16 words) | T-shuffle Q1 0.00625 · T-nowire Q1 0.0 | PASS |
| (iii) | ≥ 30 pp under on all 16 words (the twin FROZEN after 10 cells, G0b's; the 50-cell twin printed — §16 addenda) | T-frozen-10 Q1 0.05625 (cells [8, 2]) vs Q1 0.606; the 50-cell twin 0.35 | PASS |
| (iv) | ≥ 50 born · 0 refused at ANY cap (budget · nmax · frozen; §18 add. 4) · ≥ 5 % pruned · 0 by disuse | born 311 · refused at caps 0 (budget 0 · nmax 0 · frozen 0; redundant 169, not a refusal) (arrivals 14, budget left 197) · pruned 164/464 = 35.3 % (cross-thing born 188 / pruned 54) · disuse 0 | PASS |
| (v) | ≤ 5 pp on the last-of-window pair (§15) | no odd window with exams on both sides → not readable — not gradable: no odd window with exams on both sides (the maker's second window has not closed on this record) | not graded |
| (vi) | plant majority answered (not gradable while the plant was never shown) · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant zog answered 0.00 (as {'cross': 5, 'dot': 4}, abstain {'novel': 0, 'noedge': 0, 'ratio': 1, 'close': 0}; plant shown 0 — plant clause NOT GRADABLE) · null vex abstains 0.00 (answered as {'dot': 7, 'ring': 3}) · Q5 0.00 · false 0.073 | FAIL |
| (viii) COST | G4-7: live ms per CANVAS (STATUS.mind_ms_per_canvas_1min) ≤ 2× the solo probe's · RSS < 2 GB (the 24 h CPU bill printed) | live None ms a canvas (per-row median None ms) vs solo 39.57 ms a canvas · RSS 603.79 MB · CPU None h · STATUS carries only the per-row median (mind_ms_median_1min), which is not the probe's unit (ms per canvas, #162): not graded — every (viii) PASS before 2026-09-22 was a reading of this instrument · LAG: the mind's last consumed seq 729 (journal) of the tape's 850: 121 rows / 0.0445 world h unconsumed; the read is CUT at it (121 rows / 0.0445 world h of the 850-row window the mind never lived; it lived 0.2546 h); backlog (body rows, n 18): max 0 at 2026-09-22T20:39:55.612Z, last 0, first > 100 never; STATUS backlog 121 (reconciles with the tape: False) | not graded |
| (x) | ≥ .90 in the first 2 fixations · ≥ 1.5× random | gaze 1.000 vs random 0.082 (×12.22) | PASS |
| (xi) | ≥ .10 over G1's one-glance twin (gaze mode 'one': the whole canvas at glance×glance); the first-fixation-only twin printed — §16 addendum | Q1 gaze 0.606 − one-glance 0.175 (first-fixation-only 0.525; random-gaze 0.24375) | PASS |
| MODULATION | §18 addendum 3: at every window bringing NEW things, a majority spike (≥ 3× the last-50 median AND ≥ the life's own regime null-band) and settle (≤ the life's own regime settle-bar) by the 10th showing; the fake-boundary null clears the same band. The §16 record (3× spike / 1.25× settle / 1.5× null, calibrated pre-W3-2b) is printed as 'pass_fixed_bars_record'. | windows(regime) [] · windows(fixed) [] · null(regime) None · null(fixed) None · regime band 1.4344 (n=11, share 0.9091) · regime settle bar 1.0 · not gradable (§18 add. 4: no new thing reached 10 showings) [] · no-predict twin max err {'max_err': 0.0, 'n': 279} · fixed-bar record FAIL · no window change on this tape yet (e.g. a smoke shorter than the maker's window) — not gradable; the regime band is still derived and printed under 'regime' | not graded |
| TWINS random-gaze | loses (xi) | margin 0.362 | PASS |
| W3-2 rules | filed > 0 · scored > 0 · accuracy ≥ .80 (W3-2c's decider) · the shuffled-words twin at chance · every rule's cluster ≥ .5 the word's OWN cells · rules reach ≥ 5 of ≥ 5 eligible words (§18 add. 2) | filed 3 (induce 6, deduce 0, refused 0) · scored 3 · accuracy 1.0 · words ['bar'] · T-shuffle scored 0 acc None · parked rules 0 · clusters: rules reached 1 of 14 eligible words (of 14), wrong-cell rules 0  VOID by the wiring: rules reached 1 of 14 eligible words (floor 5) | FAIL |
| DOOR | ≥ 300 pictures on the tape · ≥ 11 folder words heard (§18); sight-only rows and recognition REPORTED (§8) | pictures 31 (rows 61) · words 2 · sight-only 1 (first seq 4) · recognition {'ahmad': {'asked': 3, 'own_word': 0}, 'anchor': {'asked': 3, 'own_word': 0}}  | FAIL |
| W3-1 beliefs | every raw `belief` row beyond a word's first is the named second side of a `clash` row of that word (the clash law writes it; life 2's 1,473 unnamed rows fail) · revisits > 0 · clashes reported | rows 11 · kinds {'belief': 6, 'extension': 1, 'revisit': 4} · standing words 6 of 15 heard · max belief rows per word 1 · extra belief rows 0 vs clash rows 0 · unaccounted [] | PASS |
| PARK | ≥ 1 parked · share ≤ 5 % | parked 0 of 27 thinks (rules 0) — graded in this life (§18): a dead end can arrive from a rule failed 3× or a wordless sight; sight-only rows on this tape: 1 | FAIL |
| ACT | mind-chosen = 100 % of ≥ 100 game outcomes · mismatches 0 · census over the GAME's acts: no act ≥ 95 % of the last 100 game acts, no reachable act at 0 over the life · the shuffled-act plant diverges · reward printed, no bar | mind-chosen 62 of 62 (share 1.0) · mismatches journal 0 status 0 · the GAME's census {'left': 8, 'right': 12, 'forward': 4, 'pickup': 18, 'drop': 7, 'toggle': 5, 'done': 8} max 0.2903 zero [] · the last 62 game acts {'left': 8, 'right': 12, 'forward': 4, 'pickup': 18, 'drop': 7, 'toggle': 5, 'done': 8} max 0.2903 (the ≥ 95 % clause) · STATUS acts_chosen (with the mouth's say, printed only) {'done': 8, 'toggle': 5, 'right': 13, 'drop': 7, 'pickup': 18, 'forward': 4, 'left': 8} · shuffled twin diverged not run (not gradable) · reward mean 0.0 success/episode None (random null 0.29) — not gradable: 62 game outcomes < 100 | not graded |
| SOUND | every ear-sound row consumed into the sound ring, 0 errors; not gradable while the world is silent | ear-sound rows 0 · consumed 0 · errors 0 · STATUS sound_events 0 — not gradable: heard 0 s — no ear-sound row on the tape (the world is silent; the plan's §10 names the rung that brings a voice) | not graded |
| SIZING | born within [0.5×, 1.5×] of the prediction · refused at NMAX 0 · the plant birthed ≥ 1 sight cell | born 296 of 6000 · prediction None · refused at NMAX 0 · series/h [292, 0] · plant shown 0 birthed 0 (plant clause NOT GRADABLE) — not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight) | not graded |
| GRADE | null sure-bare ≤ 1/10 · null unsure+abstain ≥ 8/10 (a tie fails) · plant ANSWERED ≥ 6/10 (its grades printed; not gradable while the plant was never shown) · hedge rate printed, no bar (predicted < 0.10) | null graded {'sure_bare': 10, 'unsure': 0, 'abstain_with_resemblance': 0, 'abstain': 0} · plant answered 0.0 graded {'sure_bare': 9, 'unsure': 0, 'abstain_with_resemblance': 1, 'abstain': 0} (plant shown 0; plant clause NOT GRADABLE) · hedge rate on seen words 0.15463917525773196 — graded (§19.3); the plant clause not gradable: plant shown 0 (the plant lands at the maker's PLANT_AFTER canvas; graded from its first showing) | FAIL |
| SELF | ≥ 1 belief about itself citing two real body rows; skips printed; not gradable under 24 body rows | self beliefs 3 (citing two body rows 1; words ['self:arrivals_stopped']) · self thinks 5 · body rows 16 · skipped for backlog 0 — not gradable: 16 body rows < 24 | not graded |
| SURPRISE | maker things with ≥ 30 showings: first-3 share < last-20 for ≥ 80 % and > the shuffled null's p95 · last-500 − first-500 share ≥ 0.10 · the blind-surprise twin confirms 0 glances | overall confirmed share 0.3387 over 279 canvases · maker things rising 0 of 0 (null mean None p95 None) · first 500 0.3387 → last 500 0.3387 (rise None) · by source {'folder': {'things': 2, 'confirmed': 0, 'glances': 124, 'share': 0.0}, 'maker': {'things': 11, 'confirmed': 294, 'glances': 740, 'share': 0.3973}, 'game': {'things': 1, 'confirmed': 84, 'glances': 252, 'share': 0.3333}} · printed not graded 14 things · blind-surprise twin confirmed 0 · STATUS confirmed 387 surprised 733 — not gradable: 0 maker things with ≥ 30 showings / 279 canvases (needs ≥ 1000) | not graded |
| COARSE | Q1 all words ≥ 0.975 beside the blind-coarse twin; house ≥ 0.8 vs twin < 0.6 (a prediction) | Q1 all words 0.60625 vs blind-coarse 0.6125 · house 0.0 vs 0.0 (prediction held False) · cup 0.0 vs 0.0 — graded (§19.4) | FAIL |
| QUESTION | questions ≥ (hours − 2)/2 · the answered share printed (prediction ≥ 0.5 for maker things): each question once, by the maker or the lexicon door | questions 0 (forms {}; needed None) · ANSWERED 0 (share None): by the maker 0, by the lexicon 0, both 0 · unanswered 0 (about the hands' own pictures, no door answers: 0; others by form {}) · rows stamped `answering` 2 (ear+eye) · STATUS written 0 answered 1 — not gradable: 1.0 h < 2 h (questions are graded after hour 2) | not graded |
| SENTENCE | ≥ 3 frames · precision ≥ 0.8 · not gradable under 100 missions or when the world's max pair lift < 2 (the ceiling clause) | missions 1 (one per game episode; 63 per frame, lift 1.0) · the world's max pair lift None on «None» · frames filed 0 scored 0 true 0 (precision None) · said 0 heard yes 0 no 0 — not gradable: 1 missions < 100 (one per game episode; 63 frames) | not graded |
| HANDS | ≥ 0.6 recognised (the exam answers the run's canvas with the program's own shape) vs the shuffled-shelf twin; not gradable under 20 runs | runs 1 (by program {'dot_0': 1}; no road 0) · asked None recognised None vs shuffled shelf None · touch 0 smell 31 — not gradable: 1 runs < 20 | not graded |
| THREAD | max sense gap ≤ 5.1 s · think_waits / thinks < 5% (gaps attributed to sleeps, printed, never excused) | max sense gap 5.0 s (eye/ear [5.0, 5.0]) · in the minute after a sleep: max None s, 0 over the bar · outside those minutes: max 5.015 s, 0 over the bar (0 sleeps) · thinks 27 waits 0 (share 0.0, 0.0 ms) · think ms last 2.136 median 0.856 — graded (§19.2) | PASS |
| READ | words born from shelf >= 500 · frames from shelf >= 20 with precision >= 0.8 vs the shuffled twin · the reading mark >= 0.6 (50 shelf words the life DID hear, rendered in the held-out font) · the blind twin reads 0 by construction | words born from shelf 0 · frames 0 (precision vs shuffled None) · reading None on None words — the sample: seed None, 0 of None eligible (heard None; excluded: heard elsewhere too 0, not on the cut tape None) · blind twin not gradable: SENSE_READ not declared — not gradable: SENSE_READ not declared on this life | not graded |
| EVOLVE | JUDGED rounds >= 3 scaled to the record's own hours (min 1; a void round — no readings, reason «not gradable» — is printed, never counted) · every judged round paired (incumbent+mutant readings) · adoptions <= judged rounds · every adoption's genome sha printed · REPLAY identical across epochs (the existing REPLAY mark, on a tape carrying a proposal row) · the negative control's planted-bad and null mutants both REFUSED · max_shadow_lag_rows printed, never gated (#236) | judged rounds 0 (needed None; every None h → None possible) · void rounds 0 [] · paired 0 · adoptions 0 [] · max shadow lag None rows — not gradable: EVOLVE not declared on this life | not graded |
| WEB | made/refused_rate/refused_hold printed · every web row's question_id present (this mark's own traceability proxy, RAISED) · under STAGE 3 (no stage-4 event) made == 0 | web rows 0 · made 0 · refused rate 0 hold 0 · untraceable 0 · stage 4 reached False — not gradable: DOOR_WEB not declared on this life | not graded |
| STAGE | the stage series by moment, each with its five readings · at most ONE stage-4 event, ever (the readiness series printed beside, never gating) | stage-4 events 0 [] · READINESS at 0 SIT boundaries: held a 0 · b 0 · c 0 · d 0 · e 0; all five 0 (longest run 0, 2 open the door) · per boundary [] · booleans from the mind's `sit` rows; the numbers behind (a) the reward window, (b) frames/lift and (d) grade counts are on no record (the mind journals booleans only) — not gradable: STAGE_READY ("by READY") not declared on this life | not graded |
| TWINS no-sleep / no-curiosity / no-park | (v) / door / PARK | {'graded': False, 'reason': "SLEEP's retention is not gradable on drawn worlds (§10)", 'no_sleep_Q1': 0.60625} · the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded · reported: no-park twin parked 0 vs live 0 | not graded |

**failed (8):** vi_knows_unknown, vii_replay, W3_2_rules, DOOR, PARK, GRADE, COARSE, ALIVE

**not gradable (18) — never in the failed list (READER-FIX-0923 (9)):** v_retention (not gradable: no odd window with exams on both sides (the maker's second window has not closed on this record)); MODULATION (no window change on this tape yet (e.g. a smoke shorter than the maker's window) — not gradable; the regime band is still derived and printed under 'regime'); viii_cost (STATUS carries only the per-row median (mind_ms_median_1min), which is not the probe's unit (ms per canvas, #162): not graded — every (viii) PASS before 2026-09-22 was a reading of this instrument); ACT (not gradable: 62 game outcomes < 100); SOUND (not gradable: heard 0 s — no ear-sound row on the tape (the world is silent; the plan's §10 names the rung that brings a voice)); SIZING (not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight)); SELF (not gradable: 16 body rows < 24); SURPRISE (not gradable: 0 maker things with ≥ 30 showings / 279 canvases (needs ≥ 1000)); QUESTION (not gradable: 1.0 h < 2 h (questions are graded after hour 2)); SENTENCE (not gradable: 1 missions < 100 (one per game episode; 63 frames)); HANDS (not gradable: 1 runs < 20); EVOLVE (not gradable: EVOLVE not declared on this life); READ (not gradable: SENSE_READ not declared on this life); WEB (not gradable: DOOR_WEB not declared on this life); STAGE (not gradable: STAGE_READY ("by READY") not declared on this life); TWINS.no_curiosity (the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded); TWINS.no_park (reported: no-park twin parked 0 vs live 0); TWINS.no_sleep_v (SLEEP's retention is not gradable on drawn worlds (§10))

## Twins (each a replay of the same tape blind to one gene; Q1 on all 16 words, the seen-words Q1 beside it)

| twin | Q1 (all) | Q1 (seen) | composite (all) | cells |
|---|---|---|---|---|
| gaze | 0.24375 | 0.35454545454545455 | 0.4296875 | [629, 14] |
| sleep | 0.60625 | 0.8818181818181818 | 0.6578125 | [276, 14] |
| predict | 0.59375 | 0.8636363636363636 | 0.65625 | [272, 14] |
| curiosity | 0.60625 | 0.8818181818181818 | 0.6578125 | [276, 14] |
| park | 0.60625 | 0.8818181818181818 | 0.6578125 | [276, 14] |
| frozen | 0.35 | 0.8 | 0.44375 | [41, 9] |
| coarse | 0.6125 | 0.8909090909090909 | 0.6765625 | [165, 14] |
| surprise | 0.6125 | 0.8909090909090909 | 0.678125 | [282, 14] |

## Plants

{
 "vi": false,
 "predict_file_pair": {
  "sight_road_rows": 3,
  "rule_rows_filed": 3,
  "rule_rows_scored": 3,
  "status_predictions_filed": 6
 },
 "park_unanswerable_want": {
  "sight_only_rows": 1,
  "first_seq": 4,
  "parked_total": 0
 },
 "sleep_replay": {
  "sleeps": 0,
  "no_sleep_twin_sleeps": 0
 },
 "belief_contradiction": {
  "clash_rows": 0,
  "extension_rows": 1
 }
}

## BANDS (reported, never gating)

{
 "drawn_gate_Ga_line": null,
 "eye_photo_g1_gate": {
  "eye-photo-g1 (trained)": {
   "within_median": 0.49888455080798466,
   "within_p5": 0.37052335904616485,
   "between_median": 0.4804114741939055,
   "between_p95": 0.6097629365143347,
   "floor": 0.6097629365143347,
   "margin": -0.11087838570635,
   "met": false,
   "closest_pair": {
    "pair": "ahmad/buddha",
    "p95": 0.6745258893781366
   },
   "ahmad_within_median": 0.5675470247259926,
   "ahmad_between_p95": 0.6178079359674555,
   "ahmad_separates": false,
   "n_feat": 768
  },
  "untrained twin": {
   "within_median": 0.9327385776846988,
   "within_p5": 0.8071716644973077,
   "between_median": 0.9268360150402636,
   "between_p95": 0.9743295520248235,
   "floor": 0.9743295520248235,
   "margin": -0.04159097434012471,
   "met": false,
   "closest_pair": {
    "pair": "bass/cannon",
    "p95": 0.9803717861408382
   },
   "ahmad_within_median": 0.9363206099459785,
   "ahmad_between_p95": 0.9727987988156809,
   "ahmad_separates": false,
   "n_feat": 768
  },
  "glyph eye (G1-his)": {
   "within_median": 0.8337071521045215,
   "within_p5": 0.6662882775303571,
   "between_median": 0.8315493277448813,
   "between_p95": 0.9200069967451245,
   "floor": 0.9200069967451245,
   "margin": -0.08629984464060303,
   "met": false,
   "closest_pair": {
    "pair": "beaver/camera",
    "p95": 0.9465695825046994
   },
   "ahmad_within_median": 0.8363687052060623,
   "ahmad_between_p95": 0.9145881819313775,
   "ahmad_separates": false,
   "n_feat": 112
  },
  "G4": {
   "pass": false,
   "trained_margin": -0.11087838570635,
   "untrained_margin": -0.04159097434012471,
   "delta_vs_untrained": -0.0692874113662253,
   "bar": "p95 rule met \u00b7 ahmad separates \u00b7 margin \u2212 untrained \u2265 0.05"
  }
 }
}

## ALIVE per hour

{"0": {"canvases": 558, "thinks": 27, "sleeps": 0, "snapshots": 3, "exams": 1}}

failed: ['vi_knows_unknown', 'vii_replay', 'W3_2_rules', 'DOOR', 'PARK', 'GRADE', 'COARSE', 'ALIVE'] · not gradable: ['v_retention', 'MODULATION', 'viii_cost', 'ACT', 'SOUND', 'SIZING', 'SELF', 'SURPRISE', 'QUESTION', 'SENTENCE', 'HANDS', 'EVOLVE', 'READ', 'WEB', 'STAGE', 'TWINS.no_curiosity', 'TWINS.no_park', 'TWINS.no_sleep_v'] · 162.2 s
