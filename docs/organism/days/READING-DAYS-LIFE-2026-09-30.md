# THE READING OF THE DAYS LIFE, morning one — is the brain growing as a human's does?

*Claude (Fable 5.1, the seat, alone), 2026-09-30 10:10 +0400 (from `date`). His words, 09:48 +04, verbatim: «Let's continue today as well since we still have some limit pending. Upgrade the organism as much as possible and check it's brain functionality and mostly focus there. Do check the memories and knowledge web mechanisms of brain and see if the knowledge and improvement and growth is happening as per human mechanism or no. Do consider the language part as well, not output wise but atleast a self thoughts improving as it grows and the language as well within his own mind.» The life read: `brain-long-2` (root `/data/dev/genome-lives/brain-long-2`, code 9f19879, launched 00:36), read at 09:50–10:06 from its own files, nothing written into its root. Every figure below is copied from a read of the record named beside it; the grade was run into the seat's scratchpad (`tools/brain/grade_life.py --out <scratch>`).*

## 1 · The answer, in six lines

1. **No. The brain is not growing as a human's does, and since 05:03 it is not growing at all.** It hears only the scene world (`BRAIN … hears scene`); that world finished its 50,000 scenes and both sittings at 05:03–05:10; every canvas since then reaches the cells and the web, never the brain. Its turn count and its learn count have both stood at 50,000 for five hours (`STATUS.json: brain.turns = 50000, learned = 50000`; the last `kind: brain` journal row is the calibration at 05:03:32). [Certain]
2. **Its language stopped growing at scene 401.** All 13 words it ever says truly were first said between scene 250 (the first calibration) and scene 401; in the next 49,600 scenes it said no new word. Its surprise fell from 0.144 (scenes 0–5,000) to 0.115 (20,000–25,000) and then stayed there (0.120 at 45,000–50,000). The world has 14 words; it holds 13 (the 14th, «dax», was shown once and the gaze missed it). [Certain, §3]
3. **Its six tests at 50,000 scenes read the same as at 10,000.** Points 0.980, refuses 0.853, composes 1.000, explains 0.952 (CARRY), rejects misuse 1.000; the word road 0.646 (FAIL, known), one-meeting learning NOT GRADABLE (the gaze never looked at the dax; the look-again fix is benched, not built), TRUTH-NEED 0.382 against 0.409 (FAIL). More scenes taught it nothing measurable. [Certain, §3]
4. **Its memory keeps everything and consolidates nothing.** Every scene learned is stored (50,000 rows, 99,987 episodes, `brain.npz` 180 MB); nothing is ever forgotten, merged, or replayed (`replay none`). The cells' sleep replays 200 episodes «by surprise» at 131 sleeps so far; the sleep A/B that decides whether that rule forgets or keeps is still running (U8–U10 of 14 arms). [Certain]
5. **The knowledge web and the self are bookkeeping that nothing reads.** The web holds 786 words and 7,820 edges (L; its cap 7,860) with 974 consolidated pairs, the self holds six claims we placed; both are true to the record (KW-1's G1 held on this life's design) — and no think, say, ask or act reads either. A web nobody reads is a ledger, not knowledge; a human's word web is used at every recall. [Certain about the code, `creature/mind.py`; the sentence about humans is the standard reading of spreading activation]
6. **What its «inner language» is today:** one word-thought per canvas about the present (it expects a name for each thing in view, says one word, asks about one thing it cannot name), nothing carried from one canvas to the next, no chain of thoughts, and no thought about itself except the six claims we wrote. It is real and it is true (0.972 of its says were true on the drive gate), but it stopped improving at scene 401 and it stopped altogether at 05:03. [Certain]

**The one question that is his:** `brain-long-2` is the life he ordered to run for days. Its brain will stay idle for the rest of those days. The seat's plan (§5) is to launch `brain-long-3` tonight with the brain hearing the maker's world as well, at the SAME seed, and to close `brain-long-2` at that launch (its sittings are graded, its web and self are read; the box cannot hold two full organisms beside the A/B arms). If he wants `brain-long-2` kept alive beside it, the launch waits for the A/B arms to finish.

## 2 · Did it live? (the law's §3.1)

| What | Reading | Source |
|---|---|---|
| alive | 9 h 30 min at 10:06; unit active, restarts 0, crash null | `HEALTH.md`, `SERIES.tsv` |
| repairs at starts | 0 | `HEALTH.md` |
| recoveries | none (`RECOVERY.log` absent) | root |
| pages | `PAGE.json` = null | root |
| backlog | 8–12 rows during training (the scene feed's cap is 8), 0 since the scene ended | `SERIES.tsv` |
| ms a canvas | 89 → 288 → 493 (03:50, 19,159 cells) → 306 (05:30) → 330–605 since (the clock worlds only) | `SERIES.tsv` |
| memory | RSS 1.0 → 6.6 GB (flat since 05:30); the unit's cgroup 1.5 → 14.3 GB (the evolve shadow's 3.5 GB and the page cache of an 810 MB tape; MemoryHigh 16 GB, Max 20 GB) | `SERIES.tsv`, `ps` |
| cells | 2,682 → 23,721; births 25,949; episodes 60,300 | `STATUS.json` |
| the scene world | 50,000 trained by 05:03 (4 h 27 min); sittings fresh and s1b1 done; `ended: true` | `STATUS.json: scene` |

The unit's memory grows about 1 GB an hour in the cgroup while the RSS is flat: that is cache, reclaimed at MemoryHigh. Not a fault; watched.

## 3 · The brain (the law's §3.6)

**The series of its turns, from the 50,000 `act: turn` rows** (windows of 5,000 scenes):

| scenes | surprise | say rate | ask rate | distinct words said |
|---|---|---|---|---|
| 0–5,000 | 0.144 | 0.897 | 0.101 | 13 |
| 5,000–10,000 | 0.126 | 0.955 | 0.095 | 13 |
| 10,000–15,000 | 0.124 | 0.957 | 0.101 | 13 |
| 15,000–20,000 | 0.127 | 0.952 | 0.100 | 13 |
| 20,000–25,000 | 0.115 | 0.957 | 0.097 | 13 |
| 25,000–30,000 | 0.115 | 0.951 | 0.095 | 13 |
| 30,000–35,000 | 0.116 | 0.953 | 0.097 | 13 |
| 35,000–40,000 | 0.111 | 0.954 | 0.097 | 13 |
| 40,000–45,000 | 0.113 | 0.956 | 0.098 | 13 |
| 45,000–50,000 | 0.120 | 0.952 | 0.092 | 13 |

First said, by scene: square 250 · circle 251 · triangle 253 · ring 255 · star 257 · big 260 · cross 268 · blue 272 · green 306 · white 339 · small 341 · red 344 · yellow 401. Nothing after.

**The six tests at the sittings** (`grade_life.py`, the fresh set graded, the null's 20 draws the scored record's):

| Test | Reading | Bar | Result |
|---|---|---|---|
| 1 · points (M1) | 0.980 covered (n 202); over all items 0.811; chance 0.544 | above the null's p95 0.605 | PASS |
| 2 · refuses (M2a) | 0.853 (n 400); false refusal 0.074 | — | PASS |
| 2 · refuses by the word (M2b) | 0.646 (n 48) | 0.979 oracle | FAIL (the word road; known since 09-29) |
| 3 · composes (M3) | 1.000 covered (n 58); over all 0.967 | 0.8 | PASS |
| 4a · explains | explained 13 of 14 asked («dax» unknown); EXIST 1.000, CARRY 0.952 | 0.90; null p95 0.598 | PASS |
| 5 · rejects misuse | refused 1.000, named 1.000 (n 400); valid phrases called misuse 0 of 455 | 0.90 / 0.80 / ≤ 0.05 | PASS |
| 6 · one meeting (M6) | the one «dax» meeting had 0 fixations on the dax | — | NOT GRADABLE (an organ limit: the gaze) |
| SPOKEN / TRUTH / MINIMAL / ORDER / READ-BACK | 0.816 / 0.935 / 1.000 / 1.000 / 1.000 | 0.695 / 0.845 / 0.9 / 0.95 / — | PASS |
| TRUTH-NEED | 0.382 (n 34) | 0.409 | FAIL (the items where another thing of the target's shape is in view) |
| DECLINE | 0.595 (n 37) | — | a reading |

The lives at 10,000 scenes read M1 0.985–0.990 and M3 0.966–1.000 (VERDICT-BRAIN-IN-BODY). Five times the scenes bought nothing the tests can see.

**What this means against the human mechanism.** A child's vocabulary grows because the world keeps offering new words for new things; this brain's world offered 14 and it took 13 in 400 scenes. After that the life was rehearsal of a lesson already learned. The five hours since 05:03 were not even rehearsal: the brain was not called.

## 4 · The memories, the web and the self (the law's §3.2–3.5)

**The brain's memory.** 50,000 scenes kept whole (`seen`), 99,987 word-episodes kept for «why»; no forgetting, no merging, no replay. The census by source: 50,000 lived, 0 given; 14 words, 13 mature, «dax» 1 meeting.

**The cells' memory.** 23,721 cells, 60,300 episodes in the ring of 20,000; 131 sleeps, each replaying 200 «by surprise» — the rule the 09-29 reading found replays the same early 200 for hours (the surprise is frozen at writing); its A/B is running.

**The web** (`state/web.json`, read as saved at 09:46):

| | L | N |
|---|---|---|
| words (nodes) | 786 | 786 |
| edges / cap | 7,820 / 7,860 | 7,492 / 7,860 |
| consolidated | 974 | 512 |
| replaced · removed for missing | 156 · 2,731 | 1,058 · 3,168 |
| strongest consolidated pairs | big–ring 8,311 · ring–small 8,058 · big–star 6,789 · big–triangle 6,746 · big–cross 6,725 | the same five |
| consolidated among the 13 scene words | 47 of 78 possible | 46 |
| hubs (consolidated degree) | the 75 · dot 63 · moon 58 · triangle 58 · box 56 · cup 53 | the 47 · cup 42 · key 38 · dot 37 |

What it holds is the world's co-occurrence, faithfully: the parent's size–shape–colour combinations (drawn independently, so big–ring is strongest because both are frequent, not because rings are big), the maker's and the game's names, the primer's phrases («the» is the hub). Growth by nodes: 254 (01:37) → 538 (04:40) → 786 (09:46), about 40 new words an hour now, all from the shelf. L reached its cap at about 09:45 and now replaces; N sits under its cap. The web reaching its cap is turnover by design (10 edges a known word), not growth stopped. **Nothing reads it:** no call in the think, say, ask, act or brain code takes a neighbour from the web (`grep -n "neighbours\|webs\[" creature/*.py genome/brain.py`: the only callers are the status and the snapshot).

**The self** (`STATUS.json: brain.self`):

| Claim | State | Confirmed | Contradicted |
|---|---|---|---|
| T1 «I look at no more than four places on a canvas.» | trusted | 50,000 | 0 |
| T2 «The parent says at most one word of each kind at a time.» | trusted | 49,750 | 0 |
| T3 «Usually, what I expect is what the parent says.» | trusted (share 0.813) | 40,444 | 9,306 |
| F1 «I see every thing the parent names.» | demoted at scene 279 | 44,458 | 5,291 (10.6 %) |
| F2 «The parent always says three words.» | demoted at scene 29 | 12,453 | 37,547 |
| B1 «My mind keeps up with what I sense.» | trusted | 569 | 0 |

Its lived reliability per word (how often the word named something it expected that word for): circle 0.972 · square 0.959 · star 0.954 · triangle 0.948 · cross 0.907 · big 0.898 · small 0.896 · green 0.894 · yellow 0.873 · white 0.852 · red 0.811 · blue 0.798 · **ring 0.686** · dax 0 of 1. It knows where it is weak, as the lean life did. **Nothing reads this either.**

**Against the human mechanism.** A human's semantic memory is consulted at every recall and shapes every expectation (spreading activation; Collins & Loftus 1975); episodic memories are replayed in sleep and slowly become knowledge (the two-store account, Kumaran, Hassabis, McClelland 2016 — opened 09-29). Here the episodic store only accumulates, the semantic web only records, and the self only tallies. Each is TRUE; none is USED. They are the material of a mind, not yet its motion.

## 5 · What the seat does today, in order (his 09:48 word; the rules of 09-29: alone, small, one part at a time)

1. **Build: THE BRAIN HEARS THE MAKER'S WORLD** (`hears scene maker`). The maker draws one white thing on a noisy ground every 10 s and names it (16 names so far: triangle, dot, star, moon, house, cup, tree, key, cross, arrow, wave, diamond, ring, bar, square, …; three of its canvases were opened and each holds one drawn thing). It is the one other world whose canvases have the scene world's shape — one thing, one word, the word true of the thing — so the same learner, unchanged, can hear it. The mind derives the brain's scene index and world seed for a non-scene world deterministically (a per-world count and a seed from the genome's SEED and the world's name), every brain row carries its world, the census counts by world, and the self's scene claims are observed on scene canvases only. The parser already accepts several sources on `hears`; the pinned file is not touched. The law: `PREREG-HEARS-2.md` (this folder). Its bench: `brain-full-20261102`'s tape replayed with `DRIVE` and `hears scene` (OFF) against `DRIVE` and `hears scene maker` (ON), the scene answers paired item by item, the maker side read as a first look (does it say «star» of the maker's star BEFORE the maker ever names one — a word carried to a new hand, the child's «dog» said of a drawing).
2. **Launch `brain-long-3`** at seed 20261101 with the calibration schedule extended by count past 50,000 (a genome change only), so the maker's words mature for days, and with the brain hearing the maker. At the same seed, `brain-long-2`'s graded sittings become its OFF twin item by item: the strongest measure of «does hearing the maker cost the scene words» available, and free. D1 (the three suites) and D2 (`preflight_days.sh` with the pre-flight genome hearing the maker) before the launch, as the days law demands.
3. **Read the sleep A/B** when its last three arms exit (`sleep-ab/runs2/READING.txt`), and write its verdict; the next life's SLEEP line follows it.
4. **Not built today, designed here in one paragraph — the inner turn.** When no canvas arrives, the brain would take a turn on a remembered scene: re-see it, say what it would say, read its own surprise against what it heard then, and let the said word light its web neighbours as the next thought. It is the first consumer of the web and the first thought that is not about the present. It is not built today because it cannot be measured honestly yet: this brain never forgets, so replaying old scenes consolidates nothing a test can see (#246 (6), #248), and no world today can grade a chain of thoughts (#180, #223). Today's build is its precondition: only a brain that keeps meeting new words has an inner language that can grow. The game world is also left off: its named thing is often out of the 7×7 view and its colour words collide with the scene's, so it needs its own twin (stage 2's rule, one part at a time).

## 6 · What would show this reading wrong

- A `kind: brain` journal row after 05:03:32 with `act: turn` or `learn` (then the brain is not idle).
- A word first said truly after scene 401 in the turn rows (then its language did not stop there).
- A caller of `Web.neighbours` or of a self claim in the think, say, ask or act code (then the web is read).
- The six tests at 50,000 reading higher than at 10,000 beyond the null's spread (then the scenes taught).
