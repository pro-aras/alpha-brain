# PREREG-CONTEMPLATE-1 — the muse: thinking ABOUT what was heard (the contemplation chain)

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 23:01 +0400 — authored under Ahmad's 10-09 words,
verbatim in the session: «be ready to consume knowledge and then think on it or reason on it… creating novel
thoughts emerging from within as a chain of thoughts… Not like just giving null answer as i don't know.»
His example of record, the law's benchmark sentence: «you are alpha» → not denial, not null — but: what is
alpha? is that me? do I have a name? why this name? — a bounded inner chain ending in tentative beliefs and
counter-questions, and a grounded answer LATER, after consolidation.

## §0 · The gap this law closes, named against the code

Today a heard sentence reaches exactly one path: the chat/ear composer's `chain.compose` — answer if a chain
exists in the episodic store, else abstain (creature/mind.py:1550, the composer returning null, the door
rendering the canned string — measured tonight, 8/8 abstains on novel content). NOTHING thinks ABOUT the
heard claim. The organs needed all exist and are verdicted: the INNER walk (creature/inner.py — PREREG-INNER-1,
a seeded walk over the web by lift, the first thought not about the present), the QUESTION door
(genome/questions.py — what-is/why forms), the append-only BELIEF store (genome/think.py — believe, revisit,
extension, clash; never overwrites), the SELF node (genome/web.py — quantified self-beliefs, demoted on
contradiction — 573 demotions measured today in bl5). This law WIRES them into one loop behind a flag.

## §1 · The mechanism (machine form; constants declared before any reading)

New, behind `Mind(..., muse: bool = False)` (default OFF = byte-identical; the N1 wiring form; no genome,
parser, or machinery.py edit):

1. **The trigger** (declared, bounded): a heard sentence (any ear-source row sequence the chat/ask doors
   consume) whose words include (a) a word within one web edge of the SELF node, or (b) a word heard ≥ 2
   times (this life) that the web has never consolidated (a named novelty — heard but not known). At most
   ONE chain per 25 heard sentences (the budget; declared).
2. **The chain**: INNER's walk machinery, seeded from the heard words, at most 8 steps. Each step may file
   ONE belief row with the NEW status `tentative` (think.py's append-only store gains exactly the status
   field; tentative beliefs are EXCLUDED from every trusted read by construction — they are hypotheses, not
   knowledge) and/or form ONE question through the QUESTION door's declared forms. Every step journals a
   `muse` row (the full trace, replay-deterministic).
3. **The same-breath bar**: the chat composer's answer is UNCHANGED by the chain — an ungrounded sentence
   still abstains. The chain never speaks.
4. **The fruit** (the promotion rule, declared): a tentative belief is promoted to candidacy when BOTH hold —
   (i) at least one question filed from its chain received an answer through a declared door (the scene
   parent, the chat's teacher, the lexicon), and (ii) a consolidation pass (SLEEP) has run since the filing.
   Promotion flips the row's status (a new append-only row naming the line it supersedes — the store never
   overwrites). Only promoted content may meet the composer's store — so a re-asked sentence is answered
   from the organism's OWN consideration, never from memorized surface. Tentatives that never earn both
   stay quarantined forever (they are remembered hypotheses, marked).

## §2 · Gates

- **G-UNIT** (tests/genome or tests/creature, per home): (a) flag OFF byte-identical consume of a scripted
  chat stream; (b) the trigger fires ONLY on the declared classes (a self-touching sentence fires; an
  all-known self-free sentence does not; a once-heard word does not); (c) the 25-sentence budget holds;
  (d) tentative rows are invisible to trusted reads; (e) determinism ×2 to the last digit.
- **G-IDENTITY** — flag OFF: the toy tape replay byte-identical master vs new, and the bl2 500-row segment
  byte-identical (the N1 gate's own form and files).
- **G-PLANT** — a doctored trigger (fires on EVERY sentence) must be CAUGHT by the control-sentence check.

## §3 · The bench toy and the marks (bars written first)

The toy: a small organism state built by living a toy world (the N1 bench's own genome and 8 things), with a
SELF node carrying «alpha» hearsay (the organism's name, heard) and the web holding the toy's words. The
planted sentence: «you are alpha». Control: «the circle is big» (all-known, self-free) and shuffled-word
nulls.

- **M-CHAIN**: the planted sentence spawns exactly one muse chain; the chain carries ≥ 1 tentative belief
  AND ≥ 1 counter-question (printed, presence counts). The control spawns NONE.
- **M-HONEST**: the immediate answer to the planted sentence stays an abstention (same breath, no ground).
- **M-TENTATIVE**: no trusted read (the SELF's trusted claims, the composer's believed sets) contains a
  tentative row's content; presence counts printed.
- **M-FRUIT**: after the chain's questions are answered by the bench's parent AND one consolidation pass,
  re-asking the planted sentence yields a non-null answer whose words trace to the chain's tentative rows
  (the trace printed). NULL: 10 shuffled-word twins of the planted sentence (the same bag of words, order
  destroyed) spawn no self-chains and no fruit (the chain is content-addressed, not bag-addressed).
- **M-COST**: per-heard-sentence overhead ≤ 5 %, measured as N1's.

## §4 · Verdict forms

PASS (all gates + M-CHAIN + M-HONEST + M-TENTATIVE + M-FRUIT + M-COST, the plant caught) / FAIL-FORM
(the toy cannot support the arc — instrument fault, named, amendment) / FAIL-MECHANISM (the arc runs but
the fruit never grounds — a result; the road re-thinks) / VOID (an instrument gate fails).

## §5 · Price

Ceilings: the toy build + arms + nulls ≤ 30 CPU-min, peak ≤ 1 GB (SLOT_MEM=1G), measured-first per RULES
§6d/§6f; the identity replays ≤ 10 CPU-min. Total < 1 CPU-h.

## §6 · Adversarial walk

- The chain is bounded (8 steps, 1-in-25 sentences): no thought-storm path; the mind's own budget sees the
  muse rows like any think row.
- Tentative is quarantined: excluded from trusted reads AND from the mouth's believed-name filter (a
  hypothesis can never be spoken as knowledge — the mouth's law stands).
- The composer is untouched (M-HONEST proves it): tonight's canned «(I do not know)» stays the honest
  floor until the fruit is real.
- Replay determinism: the walk is seeded from the heard rows' own bytes (the INNER precedent); two replays
  byte-identical, proven at G-UNIT(e) and G-IDENTITY.
- What this law does NOT claim: consciousness, understanding, or a self-model upgrade. It claims one
  measurable arc: heard claim → bounded inner chain → tentative beliefs + counter-questions → consolidated
  grounded answer. The revision-side measurement (planted counterevidence, locality, PE-gating) is the NEXT
  law (PREREG-REVISE-1, queued).

## §7 · Signatures

Author: Kimi Code (K3) — 2026-10-09 23:01 +0400. Verifier loop: the seat's adversarial read recorded in
`verify/CONTEMPLATE-1-VERIFIER-READ.md` beside this law. The seat: SIGNED under Ahmad's 10-09 words; the
SEAT-LINE in `SEAT-LINE-CONTEMPLATE-1.txt`.
