# THE ORGAN RESEARCH — the shared brief for every organ document
*edit: Claude (Fable 5.1), 2026-09-21 13:50 +0400. Written on Ahmad's 2026-09-21 13:30 and 13:39 words (verbatim below). One document per organ group under this directory; Claude commits; the writer never commits.*

## His words (verbatim — the whole brief)
13:30: «You mentioned eyes that learns, the trait system, but that trait system is for mind, not the eyes or ears, or any organs, the organs prefilter and get the continuous inputs, the mind is where those traits and geometric time space combined, memories are stored and also the thinking and reasoning and learning happens, not at organ level. So catching traits and prefiltration is separate then learning, so we need a genome, a life that is grown on exactly these features, a complete set of life of the original one but with less upgrades, or let's say we update our instructions at extreme levels after deep research on each organ and other things and run a single life with it's multi testing exam and small scale environment for exploration etc.»
13:39: «The organ research now, make sure you first check the already researched documents in our pc, which contains research on animals, best parts from them, and also the advancements we can add at growth instructions, from either software, machine level, and from living beings, biological life. All the benefits and gaps that get filled by either machine, software or biology. And the G5, it's not what law or anything, i gave you many research, the main thing is, we need something that is purely inspired and reverse Engineered from biological life and advancements added at software level. So biology says how organ works and then software is what we can add as advancements, features and upgrade the instructions.»

## The rule every document obeys
**Organs prefilter and deliver; the mind learns.** Every mechanism you describe is sorted into exactly ONE bin, in its own column:
- **FIXED** — set by the genome at development: a prefilter parameter (a filter bank, a retina's centre–surround, a cochlea's tonotopy, a whisker's resonance). Never changes in a life.
- **ADAPTS** — changes at runtime WITHOUT learning: gain control, adaptation, habituation, efference-copy cancellation, a top-down PREDICTION sent by the mind that the organ subtracts (the organ only computes the residual; the prediction is the mind's).
- **LEARNS** — belongs to the MIND, delivered by the organ as a TRAIT (a channel value with its where and when). If the biology puts learning inside the organ (a task-emergent fovea, cochlear efferent learning, an adaptive retina), say so, then say what the mind-side equivalent is under his rule.

## The shape of every document (sections in this order; his three parts)
0. **On disk already** — the documents read FIRST (paths), what each already settled, and what was measured here (E-series verdicts, G-series gates, the animal register). Never rebuild `alpha1-organism-capabilities-research-2026-08-24.md`'s 17-animal register — EXTEND it per organ.
1. **BIOLOGY — how the organ works.** The mechanism chain from the physical signal to what leaves the organ, in humans and in the species whose version is the best part (name the species and the number: dynamic range, resolution, latency, channel count, band). Each mechanism with its bin (FIXED / ADAPTS / LEARNS).
2. **SOFTWARE / MACHINE — what we add.** Two kinds, kept apart: (a) what MIMICS biology in code (a gammatone bank, a centre–surround kernel, a saccade policy); (b) what biology CANNOT do and software/machine can (channels outside the animal's band, exact replay, parallel senses on 16 cores, an event sensor's µs and 140 dB, a sense that never sleeps, provenance on every trait). Name the cost on this box (a 16-core CPU, no GPU; the creature's mind runs ~26 ms a canvas).
3. **BENEFITS and GAPS.** A table: `gap in the creature today | filled by BIOLOGY (which mechanism) | filled by SOFTWARE/MACHINE (which feature) | still open`. "Today" = the G4 creature as it runs (docs/G4-DESIGN.md §1, docs/G4-PREREG.md §11, the life-2 verdict `runs/g4-verdict-life2-20260921-1215/VERDICT.md`, the gap map `/data/dev/alpha3/docs/proposals/GAP-MAP-2026-09-19.md`).
4. **The growth instructions proposed** — draft gene lines in the genome's own syntax (read `genome/G4.genome` and `docs/G4-DESIGN.md §9` for the syntax: `NAME  value words  # source`), each with its source and the small test that could refuse it. Proposals, not laws.
5. **What this document does not claim** — and the 3 questions Ahmad would have to answer.

## Verification discipline (or the document is prose)
- Every factual claim carries its road in brackets: **[fetched: full text URL]**, **[abstract only: URL]**, **[PMC copy: URL]** (paywalled primaries are read at pmc.ncbi.nlm.nih.gov — SOLUTIONS #196), **[secondary: URL]**, **[from disk: path]**, **[unverified]**. No number quoted from a summary or from memory without a road.
- His pastes outrank every agent synthesis on disk. Where two disk documents contradict (the inventory names R1 vs his 2026-09-15 stream-first paste), resolve it HIS way unless you find PRIMARY evidence otherwise — and say which you did.
- A species' "best part" is a measured property with a number and a source, never an adjective.
- Search wide (Google Scholar-style queries, arXiv, PMC, Nature/Science/Cell/eLife/J Neurosci/Current Biology); prefer 2020–2026 reviews for the state of the art and the classic primary for the mechanism.

## Where you may write, and nothing else
- Your ONE file: `/data/dev/genome/docs/organs/<NAME>.md` (the name given in your task). Nothing else under `/data/dev/genome` (a live creature runs from it: never touch `run/`, `world/`, any `.py`, `genome/*.genome`, `docs/G4-PREREG.md`), no commits, no systemd, no other worktree. Read anything.
- Length: as long as the evidence needs; tables over prose; every section present even if it says "nothing on disk; nothing found".
- The edit stamp on line 2: `*edit: Claude (Opus 5, organ researcher), <output of date "+%Y-%m-%d %H:%M %z" run at write time>*` — never a typed time.
- Keep "law", "PREREG" and "gate" OUT of the framing (his 13:39 word); write "proposed growth line" and "the test that could refuse it".
