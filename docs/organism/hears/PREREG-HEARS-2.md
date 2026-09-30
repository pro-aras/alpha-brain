# PREREG — HEARS-2: the brain hears the maker's world

*Written and signed by Claude (Fable 5.1, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-30 10:1x +0400 (the exact minute is the commit's own), before any code, any replay and any life. It follows the morning-one reading (`docs/organism/days/READING-DAYS-LIFE-2026-09-30.md`) and the map's row B3 (`docs/organism/HUMAN-MECHANISM-MAP-2026-09-29.md`: «The brain hears every world that shows a picture with words»).*

**His words (2026-09-30 09:48 +04, verbatim):** «Upgrade the organism as much as possible and check it's brain functionality and mostly focus there. Do check the memories and knowledge web mechanisms of brain and see if the knowledge and improvement and growth is happening as per human mechanism or no. Do consider the language part as well, not output wise but atleast a self thoughts improving as it grows and the language as well within his own mind.»

**What the reading found:** the brain hears one world (`hears scene`); that world's 14 words were all taken by scene 401; when the world ended at 05:03 the brain went idle for the rest of a life meant to run for days. A brain that stops meeting new words has no language that can grow.

## 1 · What changes, and what does not

**The human mechanism.** A child's words come from every hand that names things: the parent, a picture book, a sibling's drawing. The same word said of a drawn star and of a painted one is one word (Rosch's basic level holds across depictions; the CDC's 18-month «points to show» is at pictures as well as things). The organism has a second hand that names things: the maker (`WORLD drawn every 10 s`), which draws ONE white thing on a noisy ground and names it — 16 names so far in `brain-long-2` (triangle, dot, star, moon, house, cup, tree, key, cross, arrow, wave, diamond, ring, bar, square, …). Three of its canvases were opened by the seat this morning; each holds one drawn thing and a few faint stroke distractors. Its word is the truth of the one thing.

**The change (code; no parser edit, the pinned file untouched):**

| Where | What |
|---|---|
| the genome line | `BRAIN … hears scene maker` — the parser already accepts several sources on `hears`; no genome on this tree names a second one yet |
| `creature/mind.py:_brain_canvas` | an eye row from a world the brain hears that carries no `scene` / `world_seed` (every world but the scene world) gets them DERIVED: `scene` = the count of canvases the brain has learned from that world so far (0-based; kept per world in the ledger and restored at a resume), `world_seed` = a number from the genome's SEED and the world's name (sha256 of `"<seed>:<world>"`, the first 4 bytes). A scene-world row keeps the tape's own `scene` and `world_seed`, and a scene row without them is still refused by name. The brain's turn, learn and calibrate rows for a non-scene world carry `"world": <name>`; scene rows carry no new key, so every closed life's journal is byte-identical |
| `genome/brain.py` | `learn(…, world=)` keeps, per scene learned, its world (`worlds`, index-aligned with `moments`); saved in the state only when a world other than the scene was heard (a scene-only brain's saved bytes are unchanged; the state version stays 2; an older state loads with every scene as `scene`); the hash of what was LEARNED (`state_hash`, the version-1 form) is unchanged by it; `inherit` carries it; `census()` adds `scenes_by_world` and, per word, `meetings_by_world` |
| the self (`creature/mind.py:_self_turn`) | T2, T3, F1 and F2 speak of THE PARENT: they are observed on scene canvases only. T1 (four places) and the lived per-word reliability are observed on every canvas the brain hears. One claim is placed for the new hand, its truth unknown (B1's pattern): **M1 «Usually, what I expect is what the maker names.»** (usually, 0.70), observed on maker canvases only |
| `tools/brain/grade_life.py` | test 4a's EXIST is read over EVERY world's rows (a cited moment exists on the tape with the word among its ear rows, whatever the hand); CARRY and its null are read over the cited episodes that have a truth file (the scene's), and the count cited from each world is printed. Without this the wiring pin EXIST would fail on a citation of a maker memory for an instrument reason |
| `tools/brain/worlds_read.py` (new) | the reader of the brain's turns per world, as series: say rate, surprise, the say TRUE of the world's own word (a one-word world), distinct words said truly, each word's first true say and first meeting; TRANSFER (§2.3) |

**What does not change.** The learner, its rule, its constants; the turn; the scene world; every organ of the body; the web and the self's other claims; the journal of every closed life (all carry `hears scene` alone).

## 2 · The bench, before any life (replays of the closed life `brain-full-20261102`, 39.6 min, tape seq ≤ 38,173, 10,000 training scenes, both sittings, 472 maker canvases of 11 words — six of them scene words: square, ring, cross, star, triangle, circle)

Both arms replay the life's own tape under this tree's code with the life's own genome plus `DRIVE brain turn before hearing; says 1; asks 1` (the life predates DRIVE; without it there are no turn rows and no transfer reading):

- **OFF** = that genome with `hears scene`;
- **ON** = the same with `hears scene maker`.

One token apart. Both graded by `grade_life.py` into scratch, the maker side read by `worlds_read.py`.

| Mark | What is read | Bar |
|---|---|---|
| **I1 · the closed life still replays to itself** | the life's own genome (no DRIVE, `hears scene`) replayed under this tree's code `--against` its journal: exit 0; the identity plant (`DELTA lr 0.05 → 0.06`) exits 1 | exit 0; the plant 1 |
| **I2 · the token absent changes nothing** | OFF's journal without its turn rows against the replay under the life's own genome without DRIVE (`journal_diff.py`): every other row equal | equal |
| **P · the scene words, paired** | ON against OFF, item by item on the scene sittings: M1, M2a, M3 covered rates and the six tests' verdicts; beside every pair the smallest gap its n can pass (10 / n) | a READING, no bar: at n ≈ 200 (M1 covered) the smallest passing gap is 0.05, so a fall under 0.05 cannot be told from noise here. The days life at seed 20261101 is the paired test that can (§4) |
| **T · TRANSFER** (a reading) | on maker canvases, the brain's say against the maker's word, split by whether the word is ALSO a scene word: the true rate on the first 3 maker meetings of each shared word (the word already mature from scenes) beside the same for the maker-only words (bar, diamond, dot, arrow, wave; young there) | a reading; the prediction on the record: shared words are said truly of the maker's drawings from their first maker meeting more often than maker-only words are (a word carried to a new hand) |
| **G · GROWTH** (a reading) | the maker words the brain holds (mature) at the end; its say rate and its true rate on maker canvases by windows of 100; its surprise there | a reading; the prediction: every maker word with ≥ 3 meetings is mature by the last calibration, and the true rate on the last 100 maker canvases is above 0.8 |
| **C · COST** | the mind's CPU per canvas ON over OFF (`--timings`), scene canvases and maker canvases | ≤ 1.5 (the drive law's bar) |
| **X · EXIST holds by any hand** | test 4a on ON: EXIST 1.000 with the count of citations by world printed; the grader's planted control: a citation of a moment that is on no world's tape reads EXIST < 1 | the plant caught |

If I1 or I2 fails, nothing is launched and the code is wrong. If C fails, the cadence of the maker's world is the knob, never a cap on hearing.

## 3 · What must hold (the standing laws)

- A closed life replays to itself (I1 above, and one closed lean life with its plant: `brain-lean-20261101`).
- The suites: genome, tools and creature on the launched commit (the days law's D1), each read from its own log.
- The days pre-flight (`tools/lives/preflight_days.sh`) on a pre-flight genome carrying `hears scene maker`: alive with a web, back after a hard kill with its brain hearing the maker still (`heard_by_world` restored), back after the power cut, back from FAILED (D2).
- The brain's scored answers on the closed lives: unchanged under `hears scene` (I1).

## 4 · The life: `brain-long-3` (§5 of the reading)

Genome `genome/brain/lives/BRAIN-LONG-3.genome` = `BRAIN-LONG-2.genome` with: `hears scene maker`; the calibration list extended by count past 50,000 (…50000 60000 70000 80000 90000 100000 120000 140000 160000 180000 200000 250000 300000) so the maker's words keep maturing for days (a genome change only; a calibration at 20,000 scenes paused learning 0.3 s on brain-long-1, so a calibration at 300,000 is a few seconds); the SLEEP line as it is unless the sleep A/B's verdict lands before the launch (then its winner, said in an amendment). Seed 20261101, as `brain-long-2`: the scene stream and both sittings are drawn from that seed, so `brain-long-2`'s graded sittings (`READING-DAYS-LIFE-2026-09-30.md` §3) are this life's OFF twin ITEM BY ITEM — the strongest measure available of whether hearing the maker costs the scene words, and free.

Launched only after §2 and §3; `brain-long-2` closed at that launch with `close_long.sh` (its brain has been idle since 05:03; its readings are taken).

**What is read on return (no bar; a reading life, as the days law):** the maker series (`worlds_read.py`): its vocabulary by day, first true say of each maker word, the arrivals' new words (every 4 h the maker adds names); the scene sittings paired with `brain-long-2`'s (M1, M2a, M3, 4a, 5 item by item, with 10 / n beside each); the census by world; the self's M1; the cost per canvas as a series.

## 5 · The adversarial walk

1. **Is the maker's word the truth?** One drawn thing per canvas (three opened); the faint strokes can draw a fixation and make a second hypothesis, so a maker canvas is sometimes a two-thing scene where one thing has no name — the learner's `none` road and its bands are built for that (T-MEM-2). The reader prints `n_hyp` per maker canvas.
2. **Can the maker's words hurt the scene's?** Six names are shared and drawn by another hand; the prototype of «star» must now cover both. That is the cost P measures on the bench (underpowered) and §4 measures in the life (paired, n ≈ 200–400 items). If the scene marks fall beyond 10 / n in the life, the finding is the law's own: one word, two depictions, one prototype is too few — and the next design is a word with several prototypes, not a brain that hears less.
3. **The calibration points move.** `calibrate at` counts scenes LEARNED, so with the maker heard the 250th canvas comes earlier in scene terms. Part of ON by design; said here so nobody reads it as a leak.
4. **Memory and time.** `seen` grows by every maker canvas (8,640 a day at 10 s): about 30 MB a day in `brain.npz`, days of it inside the 20 GB fence; a calibration over 100,000 scenes is seconds (measured at 20,000: 0.3 s).
5. **The turn on a maker canvas asks and says.** Nothing answers the ask (stage 2 A is not built); the say goes to the journal as on scene canvases. No organ reads either.
6. **Determinism.** The per-world count and the seed are functions of the tape's order and the genome; a resume restores the count from the ledger, a replay recounts it. `_brain_canvas` for a scene row is byte-for-byte what it was.
7. **The grader.** Only EXIST changes (any world); CARRY's population is named (the scene-cited episodes) with the cited-by-world counts beside it. The planted control (§2 X) proves it can still fail.
8. **What this does not show.** Nothing about the game (its named thing is often out of the 7×7 view; its colour words collide with the scene's) or the shelf (a read word is a glyph, another mechanism): both stay unheard, by name. Nothing about learning by its own ask (stage 2 A). Nothing about thought when the world is silent (the inner turn, designed in the reading, not built).

Signed: Claude (Fable 5.1, the seat), alone — 2026-09-30 (the minute is the commit's).
