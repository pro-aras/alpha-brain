# RESEARCH-HUMAN-MOUTH-MECHANISM — how the human brain names a thing when it knows a hundred words for it, and what that machine is at our level

*Research under his word of 2026-10-05 ~15:20 +0400 (memory `feedback_2026-10-05_human_mechanism_never_cheat.md`): «How does that get solved in human brain and it's knowledge and experience memory and full mechanism? Research on that and fix it in a perfect way. … A reverse Engineering of actual real working mechanisms from human at machine level.» — Kimi K3 (kimi-code), 2026-10-05. Origin: the W2 pilot's candidate cliff (the mouth enumerated 1<<len(say) subsets and hung at 321,719 read-backs on one canvas).*

**Sources and how they were read (the house rule: whole, primaries first):**
1. **Dale & Reiter 1995**, *Computational Interpretations of the Gricean Maxims in the Generation of Referring Expressions*, Cognitive Science 19(2) — [arXiv:cmp-lg/9504020](https://arxiv.org/pdf/cmp-lg/9504020). Read whole in the fetch through §3 (the four interpretations, their costs, the psychological evidence); §4–§5 (the IDAS implementation and conclusions) were cut by the fetch limit — their algorithmic content is quoted in §3.1.4 and cross-checked against the survey below and the CMU implementation note. Flagged, never silently relied on.
2. **Hawkins, Graf, Kreiss & Goodman**, *When redundancy is useful: A Bayesian approach to 'overinformative' referring expressions* — [arXiv:1903.08237](https://arxiv.org/html/1903.08237v3). Read through §2.2.2 (all phenomena, the model, simulations 1–2); later experiment sections cut by the fetch limit, same flag.
3. **Yassa & Stark 2011**, *Pattern separation in the hippocampus*, Trends in Neurosciences 34(10) — [PMC3183227](https://pmc.ncbi.nlm.nih.gov/articles/PMC3183227/). Abstract, introduction and mechanism sections read; the review's role here is the memory mechanism only.
4. Levelt 1989 *Speaking* (via Dale & Reiter's summary of it and secondary sources — the book itself is not fetchable whole; flagged), Pechmann 1989 (via Dale & Reiter's account of the eye-tracking experiments), Grice 1975 (quoted inside source 1).
5. Krahmer & van Deemter 2012 survey, *Computational Generation of Referring Expressions* ([MIT Press](https://direct.mit.edu/coli/article/38/1/173/2136/)) — abstract and the quoted Greedy Heuristic definition; paywalled whole, flagged.

---

## 1 · The human mechanism, as the evidence has it

**The human speaker NEVER enumerates.** Naming a thing is not «generate all 2^N descriptions and filter». The production mechanism has five working parts, and each is attested:

1. **Salience-ordered concepts, not a scan.** The thing's properties come to mind in a PREFERENCE ORDER — basic-level type first («dog» before «animal» before «dalmatian», Rosch), then the attributes by their discriminating reliability (colour before size, systematically). The speaker does NOT finish scanning the distractors before starting to speak (Observation 2 of Dale & Reiter §3.2: Pechmann's eye-tracking — speech begins while the scene is still being scanned).
2. **Incremental, indelible assembly.** Words are added ONE AT A TIME; once uttered, a word is not unsaid («incrementally and indelibly», McDonald via D&R). If an early word later proves unnecessary, it stays — which is why humans say *the white bird* where *the bird* would do (Observation 1: unnecessary modifiers are the norm, not the exception).
3. **A sufficiency test after each word — against the LISTENER, not the world.** After each addition the speaker asks «can my hearer pick it out now?» — the distinguishing-description rule (every property true of the referent; every distractor ruled out by ≥ 1 property), made hearer-relative (D&R's C3: the hearer must know or easily perceive it; a *magenta* is wasted on a hearer who can't tell it from maroon). The test is against a MODEL OF THE LISTENER, and it runs after each increment, not once at the end of a full search.
4. **Useful redundancy is rational, not sloppy.** Humans systematically overmodify (colour ≫ size; more in varied scenes; more for atypical features — a *blue* banana gets its colour said, a yellow one doesn't). Hawkins et al. show this falls out of a NOISY semantics: when a word is only an approximate fit for the thing, a second word genuinely raises the hearer's chance of the right referent. The «perfect» human form is NOT the minimal one — it is the incrementally-built, approximately-minimal, robustly redundant one. Full Brevity (the true minimum) is NP-hard and humans demonstrably do not compute it (D&R §3.1.1, §3.2.1).
5. **The bail-out exists.** Speakers say «I can't describe it», point, or start over. A bounded attempt with an honest give-up is part of the real mechanism, not a failure of it.

**The memory loop underneath (his «knowledge and experience memory»):**
- **Semantic memory (knowledge):** the word store the mouth draws from — associative, spread-activated, organised by kind (our web of words). 
- **Episodic memory (experience):** the particular meetings, stored DISTINCTLY — **pattern separation** keeps similar experiences from overwriting each other (Yassa & Stark: the dentate gyrus orthogonalises; without it, catastrophic interference), and **pattern completion** retrieves the whole episode from a partial cue (CA3's auto-association).
- Production uses both: the semantic store supplies the words and their kinds; the episodic/attentional state supplies THIS scene's referent and contrast set; the hearer model is run with the same episodic scene.

## 2 · The machine at our level — the part-by-part map (the reverse engineering)

| the human part (evidence) | our organ (code) | verdict |
|---|---|---|
| salience/preference order of attributes (basic level; colour > size) | the ear's order (`Ear.key`, first-heard) and the type order of the road | **present** — our phrases are already ear-ordered; the order IS our salience order |
| incremental assembly, one word at a time | **ABSENT** — the mouth enumerated every subset of the sayable set (`1 << len(say)`) | **the defect** — this and only this is what hung |
| sufficiency test after each word, against a hearer model | the READ-BACK — the learner's own pointing with «none» (`answer_point`), run per candidate | **present and exactly the right organ** — it IS our listener model; the fix is to ask it after each word instead of after each of 2^N subsets |
| discriminatory-power pre-filter (a property that rules out nothing is never said — D&R's Relevance) | the believed map `B[k][h]` — a word another hypothesis shares believes nothing; computable WITHOUT a read-back | **present, mis-scoped** — the old mouth computed it per subset; the incremental mouth computes it per WORD, free |
| useful redundancy (no backtracking) | the margin tie-break prefers the surer phrase; the incremental form keeps the indelible early word | **compatible** — the incremental form's natural output is approximately-minimal with the same indelibility, and we must NOT «improve» it toward Full Brevity (NP-hard, non-human) |
| the bail-out | the budgeted overflow form (`reason "the mouth's budget"`, PREREG-MOUTH-CAP) | **present, stays** — the honest bound underneath the mechanism, as sleep is under wakefulness |
| pattern separation (distinct episodic stores) | the per-word episodic stores `store_z[j]` / `store_r[j]` behind each band — each meeting kept, none averaged away | **present** |
| pattern completion (whole from a cue) | the band read: a partial state is classified by its nearest prototype (`held`, `phrase_fit`) | **present** |
| semantic store (knowledge web) | the KW webs L/N | **present** |

## 3 · The machine form, exactly (the design the law will pin)

`produce_believed`'s incremental form, mapped line by line from §1:

1. **The candidate list is the ear-ordered type list of the target's sayable believed names** — the preference order, as before.
2. **Walk it once.** For each word: if it rules out no hypothesis (every other hypothesis believes the same name in that word's type — the believed map, no read-back), SKIP it (Relevance: no discriminatory power). Else ADD it to the phrase.
3. **After each addition, ONE read-back** (the hearer model). If the read-back points at the target first and «none» does not fire → **STOP: speak.** (Sufficiency.)
4. **The list exhausted without sufficiency → the bail-out** (the cap's overflow form — nothing, never a different phrase).
5. Cost: ≤ len(say) read-backs ≈ 26 × 4.7 ms ≈ 0.12 s at the mentor tape's scale — against 2^20 ≈ hours. The 2^N enumeration exists nowhere.

**What this deliberately does NOT do:** search for the shortest (humans don't; NP-hard); unsay a redundant early word (indelibility); change the learner, the bands, the ear, the read-back, the turn's journaling.

**What it changes, said now and never hidden:** the SPOKEN PHRASE can differ from the rank's winner — exactly the way *the white bird* differs from *the bird* (an indelible early word kept). On the closed record the difference is measureable and could be nonzero, so the incremental mouth is **a ladder advancement**: it enters a LIFE by its own genome line (the W1 voice's precedent: brain-long-4 = brain-long-3 + exactly one advancement), after its own law, with the mouth-cap's identity gates proving the old mouth unmoved where it stays. The first reading before any life: replay brain-long-2's tape under the incremental mouth and COUNT the differing says (an R-DIFF reading with the anchors printed — the share of canvases where the two mouths differ, and the length distribution) — a measurement, never a bar dressed as one.

## 4 · The mouth-cap law's place (nothing above supersedes it)

PREREG-MOUTH-CAP (build 7843695, G-SUITES green, M-TAPE-FULL passed, M-TAPE-BL2 armed) is the BOUND: it guarantees no mouth ever enumerates past 4,096 read-backs on any code path. The incremental mouth is the MECHANISM that makes the bound nearly unreachable. Both are the human design: a mechanism that almost never bails, and an honest bail-out underneath. Neither is a cheat: the bail-out says NOTHING (never a different phrase), and the incremental form is the documented human mechanism, not a tweak tuned to pass our gate.

## 5 · Open questions carried to the law's walk (each answered before signature)

- The read-back per increment is ONE per added word — but is ONE the human count? The hearer model updates continuously; our discrete per-word check is the machine form of the same loop. Named, not hidden.
- Sufficiency = «points first and «none» does not fire» — the current accepted rule, unchanged. The incremental form inherits it verbatim.
- A skipped (powerless) early word: D&R's algorithm also skips attributes with empty RulesOut; identical.
- A tie in the believed map (two hypotheses believing alike): the categorical uniqueness rule, unchanged.
- The margin's place: under the incremental form there is no within-class competition — the phrase is built, not chosen. The margin stays in the row as a READING (the record's margin field keeps its meaning for graders).
- The ordering of same-key words: the ear's first-heard tie-break, unchanged.

*(edit: Kimi K3 (kimi-code), 2026-10-05 17:39 +0400 — first version, on the sources named in the header with their read-status flags)*
