# PREREG-HEARS-2 — AMENDMENT 4: the grader reads a brain that hears two hands

*Drafted by Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:15 +0400, after the bench's `read` stage crashed on the ON arm. **A file of its own**: the signatures of AMENDMENTS 1–3 stand untouched; the law of HEARS-2 is `PREREG-HEARS-2.md` + its amendment files. It moves no bar and no launch gate; it names a cause in the INSTRUMENT (RULES §2), records the adaptation made, and the control that shows the adaptation changes nothing for a one-world brain. The architect co-signs by the sha256 of this file after its last edit; the seat signs after.*

## A4.1 · The cause
The bench's ON arm (`hears scene maker`, replayed 11:22–12:07 under 55ef469's code) finished with exit 0 and its journal was written. `tools/brain/grade_life.py` then **crashed** on that journal (exit 1): `WorldError: not a word of this world: 'arrow'`, raised by `W.word_type` in `world_type_of_key` while the NAME road mapped the brain's learned types to the world's type names. OFF graded without error.

**The cause is the grader.** It was written for a brain that hears ONE world (the scene), so it assumed every word of a learned type — and of a phrase the brain SAYS — is a word the scene world can type. With the maker heard, a learned type holds the maker's words (`arrow`, `bar`, `diamond`, `dot`, `wave`, … none of them a word of `brain/scene/world.py`), and the brain may say one on a scene canvas. `word_type` raises on a word outside SHAPES, COLOURS, SIZES and the dax word. A second path of the same class was found by reading the scored marks: `in_parent_order` types every word of a SAID phrase of two or more words and would raise on a maker word there; `word_true_of`, by contrast, returns False for such a word and does not raise.

## A4.2 · The adaptation (in `tools/brain/grade_life.py` only; the scored modules `brain/scene/*` are untouched and pinned)
1. **The type vote** (`world_type_of_key`): the vote is over the words the scene world KNOWS; a learned type that holds none (a type of the maker's words alone) has no world type — `None` — and the NAME road SKIPS it and COUNTS it (`NAME:foreign_type_skipped`). Two learned types mapping to one world type is still a `GradeError`.
2. **A said phrase** (`world_words`): a foreign word in a phrase the brain SAID is read as the world's `DAX_WORD`, a shape word that is true of nothing any sitting shows (only the one `dax` canvas of training carries the dax shape): the phrase is then not TRUE, and its ORDER is read with a shape where the foreign word stood (the maker names shapes). The words so read are COUNTED (`<mark>:foreign_word→dax`, in `sets.<set>.forced`).
3. **Nothing else.** The pointing marks (M1, M2a, M3, M6), M5 and test 4a take no word the brain says; the adaptation does not touch their inputs.
The count of foreign words said and foreign types skipped is itself a reading for P: how far the maker's words reach onto scene canvases (A1.5's over-extension).

## A4.3 · The controls
- **A one-world grade is unchanged:** OFF's grade, regraded with the fixed grader, is BYTE-IDENTICAL to its grade before the fix (`grade.json` sha256 `0632997a59eb8667a85a89c9…` both; `report.txt` identical): nothing is foreign in a one-world journal, and the `forced` counters gain no key unless a foreign word is met.
- **Tests** (`tests/tools/test_grade_foreign_words.py`, 9, red first: 7 errors on the unfixed grader): the type vote with the maker's words is still `shape`; a key of scene words only is what it was; a key of foreign words only has no world type and is skipped and counted; two types for one world type is still an error; a foreign word becomes the dax word and is counted; **the scored functions run on the adapted phrase** (`in_parent_order` reads «big arrow» as in order and «arrow big» as out of order, `unique_true` reads both as not TRUE) while they raise on the unadapted one; the dax stand-in is true of no shape.
- **ON now grades** (exit 0): EXIST 1.000 over 104 citations, all 104 of the scene (no maker memory was cited by the 14 `why` answers: the by-any-hand road is therefore NOT exercised on the real data, said in the reader's X line).

## A4.4 · What this does not change
No bar; no launch gate; the ladder; the mind, the organ, the genomes, the scored modules.

*Co-signed: the architect (Opus 5.5) — by the sha256 of this file after the last edit, pending. Signed: the seat — pending.*
*(edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:15 +0400)*
