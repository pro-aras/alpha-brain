# G4 VERDICT — FAIL

root `/data/dev/genome-wt-reader-fix/scratch/dry-life-1` · genome `/data/dev/genome-wt-reader-fix/scratch/dry-life-1/GENOME.genome` (sha d384b6077f6d0732) · read 2026-09-23T07:28:46+00:00 by `tools/verdict_g4.py v3.2 (2026-09-22: v3.1's rules + the version string on the record + `hash` volatile across commits, declared)` (PREREG §5 as amended; the reader's rules §16) · 0.3 h

| mark | bar | reading | verdict |
|---|---|---|---|
| ALIVE | 0.3 h under the unit, NRestarts 0, every counter moved every hour, no sense dead > 60 s | 0.299 h on tape · moved every hour False · max gap eye/ear [5.0, 5.0] s · sense restarts 0 · crashes 0 · NRestarts None | FAIL |
| REPLAY / (vii) | byte-identical mind rows; the plant caught | vs live DIVERGED at (26, 'act_chosen') · two replays identical · 883 rows · plant at seq 427 caught True · masked hash (reader a17cb0e ≠ life 74c661d) | FAIL |
| (i) | Q1,Q2 ≥ .80 · Q3 ≥ .85 · Q4 ≥ .90 | Q1 0.818 Q2 0.818 Q3 0.900 Q4 0.982 (chance 0.067; all words Q1 0.562) | PASS |
| (ii) | ≤ .20 (all 16 words) | T-shuffle Q1 0.1625 · T-nowire Q1 0.0 | PASS |
| (iii) | ≥ 30 pp under on all 16 words (the twin FROZEN after 10 cells, G0b's; the 50-cell twin printed — §16 addenda) | T-frozen-10 Q1 0.05625 (cells [8, 2]) vs Q1 0.562; the 50-cell twin 0.34375 | PASS |
| (iv) | ≥ 50 born · 0 refused at ANY cap (budget · nmax · frozen; §18 add. 4) · ≥ 5 % pruned · 0 by disuse | born 358 · refused at caps 0 (budget 0 · nmax 0 · frozen 0; redundant 199, not a refusal) (arrivals 15, budget left 364) · pruned 206/529 = 38.9 % (cross-thing born 207 / pruned 67) · disuse 0 | PASS |
| (v) | ≤ 5 pp on the last-of-window pair (§15) | no odd window with exams on both sides → not readable | FAIL |
| (vi) | plant majority answered · null majority abstains · Q5 ≥ .80 · false ≤ .20 | plant zog answered 0.00 (as {'cross': 3}, abstain {'novel': 0, 'noedge': 0, 'ratio': 7, 'close': 0}) · null vex abstains 0.10 (answered as {'dot': 6, 'ring': 3}) · Q5 0.00 · false 0.018 | FAIL |
| (viii) COST | G4-7: live ms per CANVAS (STATUS.mind_ms_per_canvas_1min) ≤ 2× the solo probe's · RSS < 2 GB (the 24 h CPU bill printed) | live 195.7031 ms a canvas (per-row median 0.12871104991063476 ms) vs solo 38.0 ms a canvas · RSS 1115.05 MB · CPU None h | FAIL |
| (x) | ≥ .90 in the first 2 fixations · ≥ 1.5× random | gaze 1.000 vs random 0.082 (×12.22) | PASS |
| (xi) | ≥ .10 over G1's one-glance twin (gaze mode 'one': the whole canvas at glance×glance); the first-fixation-only twin printed — §16 addendum | Q1 gaze 0.562 − one-glance 0.13125 (first-fixation-only 0.5375; random-gaze 0.25) | PASS |
| MODULATION | §18 addendum 3: at every window bringing NEW things, a majority spike (≥ 3× the last-50 median AND ≥ the life's own regime null-band) and settle (≤ the life's own regime settle-bar) by the 10th showing; the fake-boundary null clears the same band. The §16 record (3× spike / 1.25× settle / 1.5× null, calibrated pre-W3-2b) is printed as 'pass_fixed_bars_record'. | windows(regime) [] · windows(fixed) [] · null(regime) True · null(fixed) True · regime band 17.24 (n=13, share 0.9231) · regime settle bar 1.0 · not gradable (§18 add. 4: no new thing reached 10 showings) [] · no-predict twin max err {'max_err': 0.0, 'n': 326} · fixed-bar record FAIL · no window change on this tape yet (e.g. a smoke shorter than the maker's window) — not gradable; the regime band is still derived and printed under 'regime' | FAIL |
| TWINS random-gaze | loses (xi) | margin 0.312 | PASS |
| W3-2 rules | filed > 0 · scored > 0 · accuracy ≥ .80 (W3-2c's decider) · the shuffled-words twin at chance · every rule's cluster ≥ .5 the word's OWN cells · rules reach ≥ 5 of ≥ 5 eligible words (§18 add. 2) | filed 3 (induce 6, deduce 0, refused 0) · scored 3 · accuracy 1.0 · words ['bar'] · T-shuffle scored 0 acc None · parked rules 0 · clusters: rules reached 2 of 16 eligible words (of 16), wrong-cell rules 0  VOID by the wiring: rules reached 2 of 16 eligible words (floor 5) | FAIL |
| DOOR | ≥ 300 pictures on the tape · ≥ 11 folder words heard (§18); sight-only rows and recognition REPORTED (§8) | pictures 36 (rows 71) · words 2 · sight-only 1 (first seq 4) · recognition {'ahmad': {'asked': 3, 'own_word': 0}, 'anchor': {'asked': 3, 'own_word': 0}}  | FAIL |
| W3-1 beliefs | every raw `belief` row beyond a word's first is the named second side of a `clash` row of that word (the clash law writes it; life 2's 1,473 unnamed rows fail) · revisits > 0 · clashes reported | rows 11 · kinds {'belief': 6, 'extension': 1, 'revisit': 4} · standing words 6 of 17 heard · max belief rows per word 1 · extra belief rows 0 vs clash rows 0 · unaccounted [] | PASS |
| PARK | ≥ 1 parked · share ≤ 5 % | parked 0 of 32 thinks (rules 0) — graded in this life (§18): a dead end can arrive from a rule failed 3× or a wordless sight; sight-only rows on this tape: 1 | FAIL |
| ACT | mind-chosen = 100 % of ≥ 100 game outcomes · mismatches 0 · census: no act ≥ 95 %, no reachable act at 0 · the shuffled-act plant diverges · reward printed, no bar | mind-chosen 72 of 72 (share 1.0) · mismatches journal 0 status 0 · census {'done': 11, 'toggle': 8, 'right': 16, 'drop': 12, 'pickup': 21, 'forward': 11, 'left': 12, 'say': 1} max 0.2283 zero [] · shuffled twin diverged not run (not gradable) · reward mean 0.0 success/episode 0.0 (random null 0.29) — not gradable: 72 game outcomes < 100 | not graded |
| SOUND | every ear-sound row consumed into the sound ring, 0 errors; not gradable while the world is silent | ear-sound rows 0 · consumed 0 · errors 0 · STATUS sound_events 0 — not gradable: heard 0 s — no ear-sound row on the tape (the world is silent; the plan's §10 names the rung that brings a voice) | not graded |
| SIZING | born within [0.5×, 1.5×] of the prediction · refused at NMAX 0 · the plant birthed ≥ 1 sight cell | born 413 of 6000 · prediction None · refused at NMAX 0 · series/h [338, 0] · plant shown 0 birthed 0 — not gradable: no sizing prediction on the record (PREREG §19.11 is written at the pre-flight) | not graded |
| GRADE | null sure-bare ≤ 1/10 · null unsure+abstain ≥ 8/10 (a tie fails) · plant ANSWERED ≥ 6/10 (its grades printed) · hedge rate printed, no bar (predicted < 0.10) | null graded {'sure_bare': 9, 'unsure': 0, 'abstain_with_resemblance': 1, 'abstain': 0} · plant answered 0.0 graded {'sure_bare': 3, 'unsure': 0, 'abstain_with_resemblance': 7, 'abstain': 0} · hedge rate on seen words 0.2 — graded (§19.3) | FAIL |
| SELF | ≥ 1 belief about itself citing two real body rows; skips printed; not gradable under 24 body rows | self beliefs 3 (citing two body rows 1; words ['self:arrivals_stopped']) · self thinks 5 · body rows 18 · skipped for backlog 0 — not gradable: 18 body rows < 24 | not graded |
| SURPRISE | maker things with ≥ 30 showings: first-3 share < last-20 for ≥ 80 % and > the shuffled null's p95 · last-500 − first-500 share ≥ 0.10 · the blind-surprise twin confirms 0 glances | overall confirmed share 0.3581 over 326 canvases · maker things rising 0 of 0 (null mean None p95 None) · first 500 0.3581 → last 500 0.3581 (rise None) · by source {'folder': {'things': 2, 'confirmed': 0, 'glances': 144, 'share': 0.0}, 'maker': {'things': 11, 'confirmed': 373, 'glances': 868, 'share': 0.4297}, 'game': {'things': 2, 'confirmed': 94, 'glances': 292, 'share': 0.3219}} · printed not graded 15 things · blind-surprise twin confirmed 0 · STATUS confirmed 646 surprised 1114 — not gradable: 0 maker things with ≥ 30 showings / 326 canvases (needs ≥ 1000) | not graded |
| COARSE | Q1 all words ≥ 0.975 beside the blind-coarse twin; house ≥ 0.8 vs twin < 0.6 (a prediction) | Q1 all words 0.5625 vs blind-coarse 0.6375 · house 0.0 vs 0.0 (prediction held False) · cup 0.0 vs 0.0 — graded (§19.4) | FAIL |
| QUESTION | questions ≥ (hours − 2)/2 · the answered share printed (prediction ≥ 0.5 for maker things) | questions 1 (forms {'what-is': 1}; needed None) · answered by the world 2 (share 2.0) · STATUS written 2 answered 2 — not gradable: 0.3 h < 2 h (questions are graded after hour 2) | not graded |
| SENTENCE | ≥ 3 frames · precision ≥ 0.8 · not gradable under 100 missions or when the world's max pair lift < 2 (the ceiling clause) | missions 73 · the world's max pair lift 9.125 on «purple ball» · frames filed 3 scored 3 true 3 (precision 1.0) · said 1 heard yes 1 no 0 — not gradable: 73 missions < 100 | not graded |
| HANDS | ≥ 0.6 recognised (the exam answers the run's canvas with the program's own shape) vs the shuffled-shelf twin; not gradable under 20 runs | runs 0 (by program {}; no road 7) · asked None recognised None vs shuffled shelf None · touch 0 smell 45 — not gradable: 0 runs < 20 | not graded |
| THREAD | max sense gap ≤ 5.1 s · think_waits / thinks < 5% | max sense gap 5.0 s (per hour [5.0, 5.0]) · thinks 40 waits 0 (share 0.0, 0.0 ms) · think ms last 0.016 median 0.914 — graded (§19.2) | PASS |
| TWINS no-sleep / no-curiosity / no-park | (v) / door / PARK | {'graded': False, 'reason': "SLEEP's retention is not gradable on drawn worlds (§10)", 'no_sleep_Q1': 0.5625} · the door is ON but CURIOSITY does not choose doors yet (the web door, W3-6) — not graded · reported: no-park twin parked 0 vs live 0 | not graded |

## Twins (each a replay of the same tape blind to one gene; Q1 on all 16 words, the seen-words Q1 beside it)

| twin | Q1 (all) | Q1 (seen) | composite (all) | cells |
|---|---|---|---|---|
| gaze | 0.25 | 0.36363636363636365 | 0.409375 | [746, 15] |
| sleep | 0.5625 | 0.8181818181818182 | 0.640625 | [319, 15] |
| predict | 0.6375 | 0.9272727272727272 | 0.6703125 | [314, 15] |
| curiosity | 0.5625 | 0.8181818181818182 | 0.640625 | [319, 15] |
| park | 0.5625 | 0.8181818181818182 | 0.640625 | [319, 15] |
| frozen | 0.34375 | 0.7857142857142857 | 0.44062500000000004 | [41, 9] |
| coarse | 0.6375 | 0.9272727272727272 | 0.6984375 | [191, 15] |
| surprise | 0.64375 | 0.9363636363636364 | 0.6875 | [323, 15] |

## Plants

{
 "vi": false,
 "predict_file_pair": {
  "sight_road_rows": 6,
  "rule_rows_filed": 3,
  "rule_rows_scored": 3,
  "status_predictions_filed": 13
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

{"0": {"canvases": 652, "thinks": 32, "sleeps": 0, "snapshots": 3, "exams": 0}}

failed: ['v_retention', 'vi_knows_unknown', 'vii_replay', 'MODULATION', 'viii_cost', 'W3_2_rules', 'DOOR', 'PARK', 'GRADE', 'COARSE', 'ALIVE'] · 166.6 s
