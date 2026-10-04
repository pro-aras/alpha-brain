# THE SEAT'S ONE SHARED PINNED REDRAW WINDOW — W1 + SLEEP-IDLE (2026-10-05)

*Integrator: Kimi K3 (kimi-code, builder lane kimi-w1, integrator hat), on the seat's handoff of 2026-10-05 (Ahmad's standing
word: «go for all the next builds without stop»). RULES §9/§10/§14. The window's form: the INNER window's
(/data/dev/swarm/2026-10-03/int/pinned_window.sh, the record's redraw.sh of the DRIVE window).*

## What landed, and its signature coverage (step 0, board-posted)

- **W1, the mouth voices the brain** — PREREG-W1-MOUTH-VOICES-BRAIN (SIGNED ×3 at toys-1003 1ccc3bf), VERIFIED at toys-1003
  9a2c1cc («W1: True», every mark PASS; records `docs/organism/whole/records/w1/`), branch tip b9d5605. Its pinned hunk: the
  MOUTH line's optional clause in genome/machinery.py (@@ -514).
- **SLEEP-IDLE's parser hunk** — PREREG-SLEEP-IDLE §2.1 (SIGNED ×3 at 5b21fa7/8bb2600; AMENDMENT 1 signed by the architect,
  the verifier and the seat; AMENDMENT 2 by the verifier and the seat; the graded run PASS at sleep-1003 d68e90e). Taken as
  its own two commits, made for exactly this taking: f2813f1 (the clause, genome/machinery.py @@ -443) + 75dfd82 (the 15
  parser tests). The rest of the SLEEP-IDLE feature (creature/idle.py, the body/mind idle loop, genome/sleep.py, fixtures,
  tools/idle, its records) is NOT in this window (the task's own bound). The two hunks are DISJOINT (443+34 < 514).

## The landing tree (int-1003)

`a62f339` merge toys-1003 b9d5605 --no-ff (exit 0, the tree byte-identical to b9d5605's) → `804cf1e` cherry-pick f2813f1 →
`4683d26` cherry-pick 75dfd82 → `8062f6c` THE PIN EDIT (cache.py RUNS = /data/dev/brain-runs/scene-organ-swarm-1005 FRESH,
INNER_RUNS names the swarm-1003 root read as plain files only; the pin test green; tools/brain/gate_fm6.py's FORBIDDEN_OUT
gains C.INNER_RUNS). Then this records commit.

## The redraw (slot kimi w1-window, cap 4G, peak 1023 MB, exit 0; 00:30:43 → 00:38:10)

rsync exit 0 → cache-r exit 0 (5 min 55 s) → cache-identity exit 0 → cache-new-world exit 0 → identity-20261104 exit 0.
- **«caches compared 63 · differing 0»** and **«CONTROL (one bit flipped in the redrawn glances.npy, in memory): CAUGHT
  ['glances.npy']»** (w1-window-cache-identity.log); the 20261104 train cache equal with its own plant CAUGHT
  (w1-window-identity-20261104.log).
- Beside the LIVE life (5 creature units; ALLOW_LIVE=1, the seat's word in the window's own BOUNDS): the life's backlog read
  **0 in all 15 samples** (w1-window-backlog.tsv; moments 432,955 → 433,445 undisturbed); its root READ only.
- The toys' ten room pools redrawn on the merged bytes (slot w1s-pools, exit 0, peak 414 MB): the three S1c seeds read
  **«identity with S1c's pools: EQUAL (8 pools)»** again (pools-identity-lines.txt).

## The suites on the merged bytes (each through slot, its log + exit under suites/)

| suite | line | exit |
|---|---|---|
| genome (1G, peak 863 MB) | «Ran 728 tests in 159.217s / OK (skipped=1, expected failures=6)» | 0 |
| scene (2G) | «Ran 368 tests in 116.200s / OK» | 0 |
| tools (2G, peak 1537 MB) | «Ran 1243 tests in 409.319s / OK (skipped=8)» | 0 |
| brain (4G, peak 996 MB) | «Ran 715 tests in 205.346s / FAILED (errors=16, skipped=2)» | 1 (expected) |
| creature, 3 parts (10G, peak 10,240 MB) | 444 / 559 / 445 OK, SUM 1448 = 1448, PARTITION EXACT, split verdict exit 0 | 0 |

The 31 pin-refusals of the W1 review are GONE everywhere (zero «drawn by other code» in every log). The brain suite's 16
errors are EXACTLY the pre-existing torch family — 16 import failures, each «ModuleNotFoundError: No module named 'torch'»,
the same names proven on a detached master 3c9ab08 (the toys-1003 records' suites/master24.log) — named, never fixed; the 8
pin-priced scene errors are gone. The combined parse check before the window: tests.genome.test_parse_sleep_idle +
tests.creature.test_voice_mind + tests.creature.test_refusal «Ran 54 tests … OK».

## The landing

int-1003's tip fast-forwards genome master (master was 3c9ab08; the landing sits on top). The W1 voice and the SLEEP idle
clause land in CODE only: no life is launched or closed by this window; a life carries ONE advancement over its twin under
the ladder (RULES §3), which is the seat's word, later.
