# Alpha 2 sweep — read-only, 2026-09-19 ~15:02 +04 (an Explore agent's report, verbatim; tree /data/dev/alpha2: 67 PRE-REGISTERED-a2-*.md, 26 *-REPORT.md, LAWS.md, ORGAN-CENSUS.md, organ headers)

M | mind.py core loop (salience lottery + starvation floor + token bucket) | picks which of ~20 duty kinds runs each pass | PARTIAL | fixed live 30-min run: pursuit 5/school 5/grounding 3 | shipped version starved school/curiosity 6 min live: bookkeeping per-candidate not per-kind | yes: core/loop/mind_scheduler.hpp
M | parity/oracle port discipline | each C++ organ byte-identical vs a Python-oracle corpus | WORKED | PARITY-SLICE-4: 17/17, 33/33, 161/161 | byte-identical is not cost-identical (one port 4× slower) | yes: 82-file parity corpus
M | core/jail (Landlock+seccomp+rlimits+watchdog) | sandboxes any code the mind runs | WORKED | LAWS.md A2-R6 | absolute-path and in-loop-execution bugs fixed | yes: reused directly (Alpha 3's hands)
M | lexicon.py + lexicon.hpp | binds Wiktionary senses to words | WORKED | L3B: 1,483 bound of 2,064; 1.27M senses | under three-quarters bind | yes: HEADWORDS/PRONUNCIATION reused
M | grounding_bind / grounding_check | binds a word to instances in the mind's OWN graded records | PARTIAL | thousands bound | verifies meaning by "literally appears in his own records" — a closed loop over self | Alpha 3's "ground" layer
M | concept_graph (Hebbian nodes/edges) | memory as structural re-routing | FAILED (retention) | rank-corr weight↔freq 0.798, but retention 3.3 %/0 %/0 % after a domain shift, every rule | catastrophic forgetting | named as P5's gap
M | speech_v2 (frozen judge + repair loop) | composes sentences from own record, never predicts tokens | WORKED | L4-REPORT clears its 4-gate bar | vocabulary thin | Alpha 3 layer 6 / voice
M | curiosity_genome | interest population bred/decayed by content-free operators | WORKED | evolved_net 16,114.6 vs null twin 2,223.3 | a purity-canary bug fixed | "the one organ that beat its twin"
M | retina/gaze + eye.hpp | saliency-driven fixation; letter SHAPE across fonts | WORKED | gaze ratio 6.371 vs 1.5 bar; held-out fonts 47.5→58.9 % | own_perception grounding 1 of 20 words | Alpha 3 P7
M | school_study / library | one shelf article per tick, cited sentences as leads | PARTIAL | shipped, 820 tests | reads 3 of 12 sections per book (2.6–10.5 %) | P1 rebuilds as "read whole documents"
M | corroborate_local (shelf-as-witness) | a second source among sections already read | FAILED | 0.300 % vs 1.0 % bar, twin 0 % | ~30 % of leads are sentence fragments — broken extraction | disarmed
M | w0-5c corroboration re-arm | after the shelf grew 5× | FAILED | 37.5 % of "hits" were retired claim_ids; real 0/625 | same root cause | no
M | w0-10 primary_chase | follows citations to primaries | FAILED | 20/200 leads; ratio 6.09× < 10× bar | deployed at budget 0 | no
M | w0-3 contradiction resolver | resolve contradictory beliefs | FAILED/NULL | the armed law admits 0 pairs to grading | publisher-collapse measured zero on 111 cases | no
M | prediction_ledger / b0-b1 ("pay for being wrong") | falsifiable predictions rechecked later | PARTIAL | 73/100 HIT vs 60 % bar | 874 predictions retired as liveness pings, not verdicts | design lesson
M | belief_ledger + belief-law v2 | class-weighted pooled corroboration | PARTIAL | 1,683/1,683 parity | unwired that slice; memory split into two halves that never overlap | "both halves per row" in the Alpha 3 plan
M | N0/N1 neural harness (LIF + R-STDP) | spiking substrate predicts the next letter | FAILED | 0/5 seeds beat the 18.75 % bigram bar; armed loses to frozen 5/5 | dead readout; prediction-shaped task | no
M | microglia (usage-ranked pruning) | prunes least-used synapses | FAILED to beat twin | 0/32 arms vs random | usage pruning never beat random | the random-twin rule carries; the mechanism does not
M | plasticity (STDP + M3 homeostasis) | Hebbian with runaway containment | PARTIAL | homeostasis 192/192 | 0/63 arms beat the twin | homeostasis primitive carried
M | sleep (idle-window consolidation) | re-derives/demotes beliefs in idle windows | PARTIAL | the night window ran | never once demoted a belief live | scaffold only
M | disposal (residue loop) | archives verbatim before any deletion | WORKED | shipped | — | hygiene discipline
M | self_census | hashes and structures every file and organ | WORKED | 353/353 parity | — | yes
M | clock + interoception | typed NOW / body vector, every field names its consumer | WORKED | 914 tests | — | yes
M | goals | Ahmad's dated goals move salience only, never a reward | PARTIAL | — | own-perception sub-goal 1/20 at its deadline | "goals with dates and a judge"
M | news (pure code, no LLM) | member-critical news | WORKED | C++ 8.78 s vs Python 16.74 s | — | newsd live
M | scripture verbatim | quotes byte-identical, never paraphrased | WORKED | all negative controls refused | — | the one working pattern for exact-text domains
M | exams/ (9 held-out families) | 9 capability families daily vs a twin/27B | WORKED as harness / Alpha 2 FAILED most | F1/F4/F7/F9 pass; F2/F3/F5/F6 fail/blocked | 27B baseline measured once | harness reused
M | w0-1 reader-service + track allocator | machine-speed reading with a biology-derived allocation rule | WORKED | 719 windows / 8,596 claims, 0 fallbacks | reading outpaced digestion 11,000–33,000× | the reader's track allocator
M | w0-1c/1d/2b governors | replace fixed caps with measured governors | PARTIAL | each names its miss | hard caps kept starving the reader | "no hard-coded cap standing in for engineering"
M | w0-2 learned index | incremental index | WORKED | select_ms median 1,746→892 | — | performance pattern
M | w0-8 curiosity_policy | steers interests toward his goals | WORKED after fix | 34/58 wrong → 15/59 refused | gate bugs let non-words through | plausible
M | b2 graph-pairs (Hebbian pair wiring) | concept pairs by co-occurrence | WORKED | selectivity median 1.842 | — | folded into concept_graph
M | d1 cut-oracle | retires a Python fallback once its port is proven | WORKED | 17 CUT, 4 KEPT | — | method reused
M | boot-survival | STATUS/duty history across a restart | WORKED | — | — | boot discipline
M | law/ judges (belief_law, authority, logic, hypothesis, null_tapes, sense_judge, prove, corroboration, speech_judge) | frozen C++ judiciary with negative-control twins | WORKED | 159/159 + 2,120/2,120 | only 11 of Alpha 1's 24 judiciary organs landed | reused directly
M | library-stackexchange | widens the shelf | PARTIAL | PM-1/2 PASS; PM-3 FAIL (a null twin's 99.69 %-wrong answers scored equally) | — | the 82 GB library reused
M | growth g0-g1 (alphabet + pronunciation) | headword/pronunciation corpora under a RAM budget | WORKED | 866,813 en / 19,251 ar; RSS ≤ 242 MB | — | reused

R | docs/ORGAN-CENSUS.md | 2026-08-29 | every Alpha 1 organ PORT/REBUILD/RETIRE | 24 ported as judges, 31 rebuilt; microglia already refuted (0/32)
R | docs/LAWS.md | 2026-08-29 | birth laws + R1–R7 | transcribed verbatim
R | PRE-REGISTERED-a2-n0-n1 | 2026-09-03 | LIF+R-STDP next-letter | ties frozen/shuffled near the bigram floor
R | PRE-REGISTERED-a2-v0-vision-program | 2026-09-05 | surprise gaze vs random; letters as shape | gaze 3–6×; shape generalises across held-out fonts
R | PRE-REGISTERED-a2-l2-curiosity | 2026-09-01 | content-free interest genome vs null | beats its twin on every measurement
R | PRE-REGISTERED-belief-law-v2 | 2026-09-05 | weighted pooled class-graded belief | parity clean; two memory halves never overlap
R | PRE-REGISTERED-a2-w0-5-local-corroboration | 2026-09-06 | the shelf as second witness | self-disarms; broken extraction, not the law
R | PRE-REGISTERED-a2-l3-grounding | 2026-09-01 | bind words to the mind's own records | thousands bound; checks against its own past, not the world
R | PRE-REGISTERED-a2-l3b-lexicon | 2026-09-02 | Wiktionary sense bindings | 1.27M senses; a minority bind
R | PRE-REGISTERED-a2-l4-speech | 2026-09-02 | a frozen judge on composed sentences | clears; the limit is vocabulary
R | PRE-REGISTERED-a2-p12-cpp-body | 2026-09-05 | port the body to C++ under a parity oracle | parity clean; "a week of green gates, a mind still unable to hold a sentence" (Ahmad)
R | PRE-REGISTERED-a2-growth-g0-g1 | 2026-09-01 | alphabet + pronunciation under RAM budget | built within budget
R | PRE-REGISTERED-a2-w0-10-primary-chase | 2026-09-06 | citations to primaries | 20/200; disarmed
R | PRE-REGISTERED-a2-s1-clock-interoception | 2026-09-03 | a typed NOW and body state | 4 named consumers
R | PRE-REGISTERED-a2-s4-sleep… | 2026-09-03 | idle time as consolidation | never demoted a belief live
R | PRE-REGISTERED-a2-d7-goal-organ | 2026-09-05 | goals move salience, never reward | one sub-goal missed its deadline
R | PRE-REGISTERED-a2-b0-b1 | 2026-09-02 | "pay for being wrong" | 73 % HIT; 874 retired as non-evidence
R | GROWTH-REPORT-2026-W37 | 2026-09-11 | hunger/digestion at the end of its life | reads 11,000–33,000× faster than it digests

(1) Alpha 2 = a Python-scheduled, C++-bodied organism whose loop bid ~20 duties against a token budget, judged at every step by a frozen, parity-proven judiciary gating what it may believe or say.
(2) Five worked mechanisms for words-tied-to-pictures: lexicon (sense binding); grounding_bind/check (a word to its own graded experience); retina/gaze + eye (saliency fixation, font-invariant letter shape); curiosity_genome (beat its null twin every time); speech_v2 (compose from its record under a frozen judge, never next-token).
(3) Deepest failures: local corroboration structurally unreachable (one article per claim: 0.300 % vs 1.0 %); the starvation floor keyed per-candidate caused the starvation it was to cure; the closed loop over own records (grounding_check made its own prior output the witness, not the world).
(4) Retired 2026-09-12 on Ahmad's order (RETIRED.md, verbatim as in Alpha 1's).
