# PREREG — METADATA 1: the source of every memory, and the census

*Written and signed by Claude (Fable 5.1, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-29 20:49 +0400, before any line of the build. Step 1 of `MEMORY-SURGERY-RESEARCH-AND-DESIGN.md` §10. His words: that document's §1.*

## 1 · What this step builds, and what it leaves

BUILT: every scene the brain learned carries its SOURCE and its AUTHOR; the brain can count what it holds by source (the CENSUS); asked «why» about a word it holds only from a given memory, it says so.

LEFT for the law of the implant roads, and said here so that it is not forgotten: `confirmed`, `contradicted`, `uses`, `last_used`, `confidence` beyond the stored responsibility, and the weight a given memory carries. They mean nothing until a given memory exists beside lived ones.

## 2 · The mechanism

- The brain keeps `segments`: a list of runs over its order of life. One run = `{start, end, source, author, first_moment, last_moment}`. `source` is one of `lived`, `prenatal`, `implanted-episode`, `implanted-knowledge`, `inherited`. The order of life is the one the learner already keeps (`store_t` holds it, 1-based): nothing is copied.
- `learn()` extends the last run when it is `lived` by the same author, else opens one.
- `inherit()` turns every run of the parent that was `lived` into `inherited` with the parent as author. Runs the parent itself was given keep their source and author: a grandparent's gift stays a gift.
- The saved state becomes version 2. A version 1 state LOADS: it is read as one run, `lived`, author unknown. Its hash is checked in its version 1 form, before the migration.
- `census()`: per word its meetings, its episodes by source, its maturity and its kind; per brain the scenes by source, the words, the words held ONLY from given memories. Pure: it reads, it writes nothing.
- The mind writes the census as a FILE (`<root>/census/<scenes learned>.json`) at every calibration and at close, and its totals on STATUS. It writes NO journal row.
- `why(word)` for a word with no citable episode of its own and at least one meeting from a given run answers `{kind: "given", word, source, author}`. For a brain whose every run is `lived` the answer is the old one, byte for byte.

## 3 · The marks

| Mark | Clause | Bar |
|---|---|---|
| C1 RECOUNT | the census of a life against a recount from the stores (`store_t` through `segments`) | equal for every word and every source |
| C2 PLANT | one scene learned under a planted run `implanted-episode` | the census moves by exactly one scene and by that scene's word meetings, under that source and no other; the plant asserts the state's bytes changed |
| C3 LIVED IS UNCHANGED | a life with no given memory, lived under the new code | its journal equals the same life's journal under the code before this step (the inherit test's parent, journal pinned by its sha256 taken on the commit before the build) |
| C4 MIGRATION | a version 1 state (the real file of `brain-lean-nearest-20261102`) | loads; one run `lived`; its learner equal to the file's; a version 1 file with one byte changed still refuses |
| C5 INHERITED IS NAMED | a child of that parent | its census reads 10,000 scenes `inherited` and its own under `lived`; `why` on a word it never met in its own life answers `given · inherited` |
| C6 THE SUITES | the five suites on the final bytes | every one OK, read from its own log |

## 4 · The adversarial walk

1. **Can C1 pass with a broken census?** If the census were computed BY the recount's own code it would agree with itself. The test's recount is written in the test, from `store_t` and `segments` directly.
2. **Can C3 pass by absence?** The pinned sha is taken from a run whose row count is printed and must be above 100; an empty journal cannot match.
3. **Does the file on disk change a replay?** A replay's work root gets a `census/` folder of its own; no tool compares it. The journal, which the tools do compare, is untouched (C3).
4. **Version 2 and the running life.** `brain-long-1` lives on its own checkout at 03bb75f and saves version 1. Its state is read later by the migration (C4's road).
5. **The pinned files.** None is edited: `genome/brain.py`, `creature/mind.py` and `brain/scene/learners.py` are not in `cache.WORLD_CODE` (read at the build).
6. **What this step cannot show.** That a given memory helps or harms. That is M-1 to M-4.

Signed: Claude (Fable 5.1), the seat, alone — 2026-09-29 20:49 +0400.
