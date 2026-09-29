# PREREG — THE DAYS LIFE: one full organism with every feature of 2026-09-29, alone for days

*Written and signed by Claude (Opus 5.5, the seat, ALONE under his 2026-09-29 15:25 word), 2026-09-29 23:49 +0400, before the pre-flight and before the launch.*

**His words.** 2026-09-29 23:20 +0400, verbatim: «Yes, what you decided seems right. So can we add all these features today so it runs for few days until your limit get reset? If yes then go for it. Make sure to clear any possible errors that might occur within these few days.» What he approved is the KW-2 list of `docs/brain/memory/kweb/VERDICT-KW-1.md` («What changes» 2).

## 1 · What the life carries

The genome `genome/brain/lives/BRAIN-LONG-2.genome` is the full organism of `brain-long-1` (every ALPHA4 organ, the scene world and the brain with DRIVE), with three changes: world seed 20261101, and the line `HASH sparse; dense at snapshot` (the row hash a sparse witness). The code adds, with no genome line:

| Feature | What it is | Where |
|---|---|---|
| METADATA 1 | Every scene the brain learns carries its source and its author; the census as a file and on STATUS | on master since 09-29 22:06 |
| THE KNOWLEDGE WEB | Two webs grown from every word the organism hears, whatever the source: L (the smart rule) and N (sprouts steered to the last 20 words, judged only after); 10 edges a known word; the spent consolidation test | `genome/web.py`, `creature/mind.py` |
| THE SELF | A self node fed by the brain's own turns and learns and the body's backlog, with six claims placed at birth: KW-1's five (three true, two false) and B1 «My mind keeps up with what I sense» (usually, 0.90; its truth unknown) | the same |
| The power-cut repair | At a start: a torn tail of every append-only file cut, kept and recorded; the seq healed and never below the mind's | `creature/repair.py`, `creature/tape.py`, `creature/body.py` |
| The health watch | Every 20 min and at boot: HEALTH.md; a failed life restarted at most 4 times a day, a frozen one at most once in 6 h | `tools/lives/health.py`, `creature-brain-health@` |

The web and the self are BOOKKEEPING: they change no answer and write no journal row (a lean life's journal is byte-identical with them, `tests/creature/test_web_mind.py`). An error inside them switches them off and is shown.

## 2 · What must hold before the launch (the gates)

| Gate | Clause | Bar |
|---|---|---|
| D1 THE SUITES | genome, tools and creature suites on the launched commit | every one OK, read from its own log |
| D2 THE PRE-FLIGHT | `tools/lives/preflight_days.sh` on the pre-flight genome (train 400): alive with a web and a sparse hash; back after a hard kill with its web restored; back after a simulated POWER CUT with the repair recorded, no seq used twice and new rows above the old top; back from FAILED by the health watch | its last line «PREFLIGHT PASS» |

If either fails, the days life is NOT launched and `brain-long-1` goes on as it is.

## 3 · What will be read on return (no bar: a reading life)

1. **Did it live?** Days alive; restarts, repairs and recoveries (RECOVERY.log, repairs/REPAIRS.jsonl), each with its cause; the SERIES and HEALTH.jsonl as series (backlog, ms a canvas, memory, cells), never their endpoints.
2. **The web is true:** each web's nodes and edges recounted from the words on the life's tape (`genome/web.py:recount_errors`), with a planted change caught.
3. **The web's growth:** nodes, edges, consolidated, replaced and removed per rule as series; its shape (clustering and path against a random web of its size).
4. **L against N on its own speech:** the webs as they stood at a snapshot, read against the words heard AFTER it (enrichment, as KW-1's K6); printed per rule, no winner declared by this law.
5. **The self:** each claim's end state, counts and first demotion; its lived reliability per word.
6. **The brain's six tests** at its sittings (after 50,000 scenes), by `tools/brain/grade_life.py`.

## 4 · The adversarial walk

1. **Can the web hurt the life?** It writes no journal row and fails only OFF; its cost is two web updates per heard word and one JSON file per snapshot (measured in the pre-flight's ms a canvas beside brain-long-1's).
2. **Can the repair hurt the record?** It runs only at the start of an OPEN life, only on tails (the last MiB), keeps every byte it cuts and says so in the journal. A cut can drop the last seconds of rows the mind had already seen: the record says where, and a replay of this life stops there.
3. **Can the watch hurt the life?** It acts only on FAILED, on inactive-while-enabled, or on a heartbeat older than 90 minutes; at most 4 acts a day; never on a closed life. A deterministic crash will fail again 4 times a day and stay failed: the HEALTH.md says so.
4. **The sparse hash** changes the row hash's form, not the organism; the snapshot keeps the dense hash.
5. **What this does not show.** Nothing is compared against a twin; no feature is graded by a bar. It shows whether the whole thing LIVES for days and what it holds when it has.
6. **The residual risk, said:** a power cut inside a snapshot's writes (a fraction of a second every few minutes) can leave the organism's files newer than the ledger; the resume then replays a few rows twice. Not repaired tonight.

Signed: Claude (Opus 5.5, the seat), alone — 2026-09-29 23:49 +0400.
