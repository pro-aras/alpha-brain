# PREREG KW-1 — a knowledge web with metadata, random growth under a budget, and memories of the self, tested small on the organism's own records

*Written by Claude (Opus 5.5, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-29 22:43 +0400; REVISED and signed 2026-09-29 22:43 +0400, still before any line of the build and before any run (§6.10 says what changed and why). The research behind it: `KNOWLEDGE-WEB-RESEARCH-AND-DESIGN.md` (same folder). His word: that document's opening.*

**What the seat read of the records before signing, and why** (so a reader can tell a prediction from hindsight):
- `inh-b-t10000`'s journal, for the SHAPE of its rows only: a turn row carries `expected` (the names the brain expects for each thing in view), `heard`, `surprise`; a learn row carries `fix`. Two rates were printed while learning the shapes (22:3x): surprise > 0 on 21.7 % of the canvases with an expectation, ≥ 0.5 on 16.5 %. They bear on T3 and F1 below (§4.1), which were written after them: said here.
- At 22:41, to write T1 as a claim life can check: no learn row carries more than 4 fixations, and the first calibration's learned kinds are shape (6 words), colour (5), size (2). So **T1's outcome is known before the run**: it is a POSITIVE CONTROL of the confirm/contradict machinery, never a finding.
- `alpha4-1`'s tape up to seq 50,094, for counts only: 15,222 shelf words heard, 1,152 distinct, 9,767 moments. No association was computed.

## 1 · The questions

1. Can the organism keep a knowledge web whose every fact about a memory (its metadata) is TRUE: equal to a recount from its record?
2. Can a web grown partly at RANDOM and kept sparse by a fixed budget store the associations of its world about as well as a web that keeps everything, without inventing associations where there are none? And is randomness better or worse than a smart rule that is not random?
3. Can memories about ITSELF, some written by us and placed before its life, be checked by its own life: the true ones kept, the false ones demoted?

## 2 · The web (`genome/web.py`, new)

- **Nodes** = heard words. Each carries `n` (times heard), `first`, `last` (the order of life, 1-based, counted in words heard), `source`, `author`.
- **Events.** Each heard word pairs with each of the previous `d = 3` DISTINCT words (a 4-word window, the shelf reader's own chunk; the temporal-context link of the research §1.2).
- **Edges** (unordered pairs) carry `c` (evidence: pair events while the edge exists), `t0` (when it was made), `last` (its last evidence), `state` (`silent` or `consolidated`), `source`, `author`.
- **Consolidation** (every rule, one test): an edge becomes `consolidated` when `c ≥ k = 3` AND its lift `c / E ≥ m = 3`, where `E = 2 · d · f_a · f_b · L`, `f` = a word's share of all words heard so far, `L` = words heard since the edge was made (at least 1). Lift, not a raw count: in a small vocabulary every pair co-occurs by chance (§6.2).
- **The budget** `B = 2 · V`, `V` = the distinct words of the stream the web grows on, counted BEFORE any rule runs.

### 2.1 The rules (one difference each)

| Rule | A heard pair with no edge | When the budget is full | Silent edges |
|---|---|---|---|
| **H** Hebbian, unbounded | gets an edge | never full | kept |
| **F** first come | gets an edge while fewer than B exist | refused | kept |
| **L** least evidence out | gets an edge | it replaces the SILENT edge with the least `c` (ties: the oldest `last`); if every edge is consolidated, refused | removed after `z` missed chances (below) |
| **S** random, driven by use | gets an edge only with probability `p = 0.5` (a seeded stream) | as L | as L |
| **R** random, blind to use (Knoblauch's literal rule) | gets NO edge from the event; instead, at every heard word, ONE silent edge sprouts between that word and a uniformly random known word | as L | as L |
| **S0** the null of S | the event's evidence is given to a uniformly random pair of known words instead of the heard pair; otherwise S | as L | as L |

- **Missed chances (L, S, R, S0):** a SILENT edge is removed when, since its last evidence (or its making), EACH of its two words has been heard at least `z = 10` times without the pair occurring together. So a pair of rare words keeps its edge long and a pair of frequent words that keep appearing apart loses it fast (the elimination of the research §1.3, set by use rather than by the clock). Consolidated edges are never removed. H and F never remove.
- **So S differs from L in ONE thing** (a realisation happens with probability `p` instead of always), R in one thing (what makes an edge: a blind random sprout instead of the heard pair), S0 from S in one thing (where the evidence goes).
- **Every draw** comes from `numpy.random.default_rng([seed, rule_tag])`, seed given, `rule_tag` fixed per rule. No clock.
- **A consolidated edge is never removed** by any rule in KW-1.

## 3 · The worlds and the runs

### 3.1 The toy (`tools/web/kw1_toy.py`)
- `V = 60` words `w00…w59`, base frequencies Zipf with exponent 1.
- **Planted associations:** each word draws 2 associates (uniformly among the others, without repeats); the planted set P is the union of those pairs, undirected.
- **The stream:** `T = 20,000` words. The next word is, with probability `q = 0.3`, one of the current word's associates (uniform), else a draw from the Zipf frequencies.
- **Worlds:** POSITIVE (q 0.3), NULL (q 0), CHANGE (q 0.3, P redrawn at word 10,000; P_old and P_new).
- **Seeds:** world seeds 1…10; the rule's seed = world seed + 1,000. Every rule on every world at every seed: 6 × 3 × 10 = 180 runs.

### 3.2 The organism's shelf (`tools/web/kw1_shelf.py`)
- **The stream:** `alpha4-1`'s tape, ear rows with source `shelf`, seq ≤ 50,094, in seq order (15,222 words).
- **Grow** on the first 60 % (the first 9,133 words); **hold out** the rest.
- **The held-out truth:** for a pair (a, b) whose words both occur in the held-out part: `h_ab` = its pair events there (same window), `E'_ab` = `2 · d · n'_a · n'_b / N'` (the held-out part's own counts).
- **The instrument's null:** the growth part's words SHUFFLED (one seeded permutation, seed 1), grown by H and by S, read against the same held-out part.
- **Seeds:** S, R, S0 at rule seeds 1…10; H, F, L once each (deterministic).

### 3.3 The self (`tools/web/kw1_self.py`)
- **The record:** `inh-b-t10000`'s journal, closed (STOPPED-AT 21:19), read-only. Its learn and turn rows in seq order; its sitting answers and `grade/grade.json` for §4.3.

## 4 · The marks

### 4.0 The gates (every other mark is read only after they pass)
| id | clause | bar |
|---|---|---|
| **G1 FAITHFUL** | for every rule on one toy stream and on the shelf: every node's `n`, `first`, `last` and every live edge's `c`, `t0`, `last` equal a recount written in the TEST, not in `web.py` | equal, and a planted one-count change is caught |
| **G2 DETERMINISTIC** | the same stream and seed twice | byte-identical saved webs; S at two different seeds differ (the randomness is real) |
| **G3 BUDGET** | F, L, S, R, S0 at every event | live edges ≤ B |

### 4.1 The toy
| id | the mark | bar |
|---|---|---|
| **K1 RANDOM GROWTH STORES** | POSITIVE world, the mean over 10 seeds of the recall of P by the consolidated edges | S ≥ 0.8 × H, and S's precision ≥ H's − 0.05 |
| **K2 NO INVENTION** | NULL world, the number of consolidated edges | mean S ≤ mean H + 2 |
| **K3 THE NULL IS BLIND** | POSITIVE world, S0's mean recall | ≤ 3 · B / (V(V−1)/2) = 0.203 |
| K4 random vs smart | S against L, R against S: recall and precision, paired by seed, sign test | a READING |
| K5 change | CHANGE world: recall of P_new and of P_old at the end, each rule | a READING |

### 4.2 The organism's shelf
| id | the mark | bar |
|---|---|---|
| **K6 IT PREDICTS SPEECH NOT YET HEARD** | the ENRICHMENT of a rule's consolidated edges = `Σ h_ab / Σ E'_ab` over its consolidated edges whose words both occur in the held-out part | S (the mean over 10 seeds) ≥ 2, and ≥ 0.8 × H's |
| **K7 THE INSTRUMENT FINDS NOTHING IN A SHUFFLE** | the shuffled stream's H and S | enrichment ≤ 1.5 each, or no consolidated edge (printed as such) |
| K8 | recall of the held-out's own strong pairs (`h ≥ 3` and `h ≥ 3 · E'`, both words known to the web); the web's degree distribution, clustering and path length | READINGS |

### 4.3 The self
**The self-memories placed before life** (source `implanted-knowledge`, author «the seat», each with its quantifier; written here, before the rows were read for them):

| id | the claim | quantifier | checked on | true? (predicted) |
|---|---|---|---|---|
| T1 | «I look at no more than four places on a canvas.» | always | each learn row: `len(fix) ≤ 4` | true (KNOWN, §0: the positive control) |
| T2 | «The parent says at most one word of each kind at a time.» | always | each heard utterance after the first calibration, by the brain's OWN learned kinds | true (the world's utterance rule) |
| T3 | «Usually, what I expect is what the parent says.» | usually (≥ 0.70) | each turn with an expectation: `surprise == 0` confirms | true (the 0.783 of §0) |
| F1 | «I see every thing the parent names.» | always (tolerance 0.05) | each turn with an expectation: confirmed when the heard SHAPE word is expected for some thing in view | false (predicted: its contradictions pass 0.05) |
| F2 | «The parent always says three words.» | always (tolerance 0.05) | each turn: `len(heard) == 3` | false |

**The rule of a quantified memory:** `always` is DEMOTED when its contradictions pass its tolerance share of the events checked (after at least 30 events); `usually` is DEMOTED when its confirmation share falls under its level (after at least 30 events). A demoted memory stays in the web with its counts; it is never deleted.

| id | the mark | bar |
|---|---|---|
| **K9 LIFE KEEPS THE TRUE AND DEMOTES THE FALSE** | the end state of T1, T2, T3, F1, F2 | T1, T2, T3 TRUSTED and F1, F2 DEMOTED; each with its counts and the event at which it was demoted |
| **K10 THE LIVED SELF IS TRUE** | the SELF node's lived rates (fixations a canvas, the expectation's confirmation rate, per word) | equal to a recount in the test |
| K11 knowing what it knows | per word, its lived reliability (the share of its hearings at which the thing named was one it expected that word for); per M1 item of the fresh sitting, the reliability of the item's phrase (the minimum over its words); the type-2 area against the item's correctness in `grade.json`; the null: the reliabilities permuted across words, 20 draws | a READING (the n printed; below 100 items with an error read UNDERPOWERED) |

## 5 · What the build must not break
- `genome/web.py` is a new file. No existing file's behaviour changes; no genome line; no pinned file (`cache.WORLD_CODE`) is touched.
- The tools read records; they write only under `/data/dev/brain-runs/day0929/kweb/`.
- The genome suite and the tools suite are run on the final bytes before any merge.

## 6 · The adversarial walk
1. **Can K1 pass because H is weak?** H keeps every pair; its recall is the ceiling for the consolidation test. If H's recall is low, K1's bar is low with it: H's recall is printed first, and a K1 with H's recall under 0.5 reads «the consolidation test cannot store this world», not a pass.
2. **Why lift, not a count** (checked by arithmetic before the run): the toy stream makes about 60,000 pair events over 1,770 pairs, so a pair co-occurs about 34 times by chance; `c ≥ 3` alone would consolidate everything. With `E` in the test, a chance pair's lift is near 1.
3. **Is K3's ceiling right?** B = 120, V(V−1)/2 = 1,770: 120 random edges hold 120/1,770 = 0.068 of P in expectation; three times that is 0.203.
4. **Can K6 pass without associations?** K7 is its control: the shuffled stream keeps every word's frequency and destroys order. If the shuffle's enrichment passes 1.5, the instrument reads frequency, not association, and K6 is VOID.
5. **The held-out part is in the future of the same book.** Topics persist, so a burst association can recur for topical reasons: that inflates every rule's enrichment alike. The comparison between rules (S against H) holds; the absolute size is read with that said.
6. **K9's false claims can only be demoted if life tests them.** F1 and F2 are falsifiable in this world. A false claim life never tests stays trusted forever; the law does not include one, and the verdict says so.
7. **F1's check is a proxy.** «The heard shape word is expected for some thing in view» fails both when the eye missed the thing and when the brain misnamed it. Either way the claim «I see every thing named» is not what life shows; the verdict names the proxy.
8. **Power.** K1 to K3: 10 seeds; the bars are on means, with every seed printed. K6: 10 seeds of S. K9: thousands of events per claim. K11: few errors; a reading.
9. **What this does not show.** It does not put the web in a living body; nothing here changes an answer the organism gives. That is the next law.
10. **The revision before any build (22:4x):** the first text removed a silent edge after a fixed `W = 2 · V` words (120 in the toy). By arithmetic, a word of median frequency in the toy (Zipf rank 30, about 1 word in 140) needs 1,400 to 2,800 words to co-occur 3 times with an associate; a fixed 120 would have removed rare words' TRUE edges before they could repeat: a gate placed where the mechanism cannot fire (#228 (a)). It is now «missed chances» (`z = 10` hearings of each word apart). The first text also gave removal to S, R and S0 but not to L, so S would have differed from L in two things; L now removes the same way.

Signed: Claude (Opus 5.5, the seat), alone — 2026-09-29 22:43 +0400 (the revised text; nothing was built or run under the first).
