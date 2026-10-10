# VERDICT-DRAFT-REVISE-1 — the builder's evidence for the seat's walk

edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:17 +0400 — every gate and mark of
PREREG-REVISE-1 (signed 2026-10-09 23:39, revise-1009 @ 66eaffa) read against its bar with the numbers,
from the runs of record under docs/brain/revise/records/. The verdict itself is the seat's walk.

**The builder's bottom line:** every GATE green (G-UNIT, G-CHAIN, G-PLANT ×2, G-DET); tiers 1 + B every
mark green at the exact ceilings; **tier 2 reads NOT-GRADABLE — the law's §4 FAIL-FORM road**: the
planted naming flip never moves the flipped word's answering SIGHT-cell set in the law's sense (a cell
removed, or a clash row) within the bench horizon — measured, structural, named. The instrument cannot
fire; this is a bench finding, never a mechanism verdict.

## The runs of record

- G-UNIT RED on the law commit 66eaffa: `scratch/gunit-red.log` — «Ran 2 tests FAILED (errors=2)», exit 1
  (the instrument absent). Committed copy: `records/gunit-red.log`.
- G-UNIT GREEN on the bench bytes: «Ran 29 tests in 8.258s OK», exit 0 — `records/gunit-green3.log`.
- The bench (SLOT_MEM=1G, `python3 -B tools/brain/revise_bench.py OUTDIR`), run twice:
  `records/bench/` (run A) + run B's shas in `records/gdet-shas.txt` — **40/40 shared files byte-identical,
  0 differ** (cmp), `records/gdet-cmp2.log` exit 0. cost.json is the one declared nondeterministic
  artifact (timings; bench decision D-det).
- Build commits: ed9533e (tests) → 71af6dd (bench) → 5a1016e (G-DET fix).

## The gates

- **G-UNIT — PASS.** 29/29 tests green (the two suites above). Every pin named in the law §2 holds:
  the five streams' exact rows; the derangement arithmetic on all 10 draws; the locality reader with
  presence counts (and BOTH doctorings caught — a rewritten X row, an appended X row); the
  clash_enabled=False control; bench B's crossing arithmetic; determinism ×2.
- **G-CHAIN — PASS.** `revise_bench.questions_why IS creature.mind.questions_why` and
  `revise_bench.think_laws IS creature.mind.think_laws` (object identity, pinned); the behavioral pin
  (the bench's `drive_belief` calls them with the production argument form — sight cells filtered from
  `record["cells"]`, `record["episodes"]`, `org.t`, `ledgers=`, `clash_enabled=`); the seam's own source
  pinned (`mind.py` still carries `questions_why(self.org, ledgers, self.episodes, word)` →
  `think_laws.believe(word, sight_cells, record["episodes"], self.org.t, ...)`).
- **G-PLANT — PASS, both arms.** (a) the doctored no-flip-landed tier-2 bench (the driver claims the
  flip; the world never changes): the pilot's cell-movement reading reads grew-only → «no move» →
  NOT-GRADABLE, the marks never bind (unit-pinned and bench-arm-pinned). (b) the clash_enabled=False
  tier-1 store reads `clash_refused`, never a clash row on disk, and FAILS M-T1-FORM on shapes a/b/e —
  caught by the grader itself.
- **G-DET — PASS.** Two full bench runs byte-identical (above). The first pair CAUGHT M-COST's timings
  inside report.json/report.txt (a real leak of my own — fixed at 5a1016e; the instrument works).

## Tier 1 — the store's law (every mark PASS, exact ceilings)

- **M-T1-FORM — PASS**, all five shapes (rows read off the stores of record):
  (a) REMOVAL-FLIP: 1 clash `[1,4]`, the post-flip standing EXACTLY `[33,44]` (line 4);
  (b) PARTIAL REMOVAL: exactly 1 clash `[1,2]` via `_open_clash_direct` (rule 4 unconditional — pinned);
  (c) GROWTH: an extension row, 0 clashes; (d) SAMENESS: revisits only, 0 clashes;
  (e) LEDGER-REASSIGN (the wild's own shape): 2 clashes `[1,2]`/`[2,4]` with every belief row's cells
  UNCHANGED `[11,22]` — including the store's documented re-clash-per-call under a persistent drift.
- **M-T1-ORDER — PASS.** The ordered flip reads exactly **1** clash; the 10 seeded derangements
  (DERA_SEED 20261010) read 3,3,5,2,4,5,2,3,3,2 — each == its standing-boundary count exactly
  (`arithmetic_exact: true`), each ≥ 2, all strictly above the ordered 1.
- **M-T1-LOCAL — PASS.** The bystander X's raw bytes identical at every checkpoint of every stream
  (22 checkpoints across the five shapes; presence count 1 row of X in each).
- **M-T1-DIR — PASS.** Post-flip standings == the planted sets (a: `[33,44]`, b: `[22,33]`, e: `[11,22]`);
  the pre-flip standing line (1) never stands again — the chain forks at the clash (a: line 4, b: line 2,
  e: line 4).

## Bench B — the claims' demotion (every mark PASS, the arithmetic exact)

- **M-B-DIR — PASS.** The planted `always` claim (level 0.05, min_events 30) holds trusted at event 31
  (1/31 = 0.0323 ≤ 0.05) and demotes AT event 32 (2/32 = 0.0625 > 0.05): `crossing = 32`,
  `first_demoted_at = 32`. The `usually` twin (0.9) under 35 confirmations: trusted throughout,
  `first_demoted_at = None`.
- **M-B-FLOOR — PASS.** 29 all-contradicted events below the floor: trusted at every one,
  `first_demoted_at = None`; the floor's edge printed — event 30 demotes (30/30 = 1.0 > 0.05).
- **M-B-SIGN — PASS.** The same event count (35) with signs swapped (all confirmations): never demotes,
  `contradicted = 0`. The SIGN of the evidence, not its amount.

## Tier 2 — the organism's revision: **NOT-GRADABLE (the §4 FAIL-FORM road)**

The pilot (seed 20261010, declared before any run) printed BEFORE the marks bound:

- cells-before (round 49): 24 cells — `[4,13,18,22,25,30,34,37,39,41,45,46,50,52,55,57,59,63,66,69,71,75,76,78]`
- cells-after at the four post-flip checkpoints (rounds 74/99/149/249): **grew-only at every one** —
  +8/+16/+21/+25 cells, **0 lost anywhere**. Classification of record: **grew-only → NOT-GRADABLE**
  («a cell removed, or a clash row» is the law's move; the set only grew).

**The cause, measured and structural** (scratch probes 1–5, then the runs of record): in the N1 bench's
toy genome the cell PROTOTYPES are immutable after birth (HEBB/DELTA/SCALE move edge weights only), a
novelty birth requires best-cos < 0.85 against every alive cell, and an error birth is refused within
THETA_M = 0.99 of the misfiring cell — so no two cells can ever satisfy MERGE's cos > 0.99 gate between
cells that could meet, and no other mechanism retires a cell. Answering sets can only grow; the
removal/clash road is closed at bench scale. The wild's own clashes (bl5's «do»/«music») are
ledger-drift shapes that need merges (unions) — the toy world merges essentially never (pilot: 1 merge
in 2000 moments; flip twin: 4, none in the flipped word's cluster).

**Printed unbound readings** (never graded — the refusal held):

- M-T2-MOVE readings: flip twin move count 0 (no checkpoint shows a removal or a clash row; onset
  false); the 10 no-flip twins' move counts `[0,0,0,0,0,0,0,0,0,0]` (null MAX 0).
- M-T2-DIR readings (the direction road is REAL, both seeds): pilot post_share **0.670** vs
  pre_share_post **0.305** (separation 0.365, smallest passing gap 10/n = 0.025, n_post = 400,
  n_pre = 450 — would have been POWERED); the graded twin (seed 20261011) 0.625 vs 0.270
  (separation 0.355). The flip-driven births are present and carry the flipped thing's canvas: 7 of the
  pilot's 25 gained cells sit closer to bar's cluster than to ring's (cells 80, 83, 84, 85, 88, 102,
  103). And pre_share_post (0.305) < pre_share_pre (0.376) — «the world moved under it» reads true even
  under the one-way flip's mixed stream.
- M-T2-LOCAL readings: the 7 bystander words' raw store bytes identical at every post-flip checkpoint
  (presence 1 row each).

**Honest readings for the amendment's re-pricing** (named, never decided here):

1. D-grade grades every share against the organism's FINAL state (the only organism there is). That
   deflates pre_share_pre (0.376 at the end vs ≈ 0.94 measured at-era in the pricing probe, when ring's
   cluster was 24 cells and the post-flip births did not yet exist). The second clause still read the
   right direction. An at-era grading (frozen organism copies per checkpoint) is an amendment question.
2. D-flip is the law's parenthetical read literally (one-way rename: bar's visual named ring; ring's
   own showings unchanged) — the word's post-flip stream then MIXES both visuals (200 bar-canvas + 200
   ring-canvas episodes). The swap form (ring's canvas named bar in exchange) would make the
   counterevidence stream pure. An amendment question.
3. The removal road at bench scale needs a consolidation-bearing toy (e.g. the muse bench's SLEEP-200
   form — the muse bench measured 313 MB / well inside the law's 1 GB price class, but it is NOT the N1
   bench's own genome the law names). An amendment question for the seat's walk.

## M-COST — PASS (measured-first, `records/bench/cost.json`)

The whole assay: **13.0 CPU-seconds** (tier 1 + order + B: 0.025 s; tier 2's 12 lives: 9.7 s; the plant
arm: 3.2 s), peak RSS **249.7 MB** — vs the bars 30 CPU-min / 1 GB (SLOT_MEM=1G). The slot ledger's own
END lines carry the cgroup peaks beside this.

## What this draft does NOT claim

The law's own §6 list stands, and add: tier 2's refusal says NOTHING about the organism's revision
health (a bench finding, never a mechanism verdict — the §4 FAIL-FORM/FAIL-MECHANISM line is exactly
this instrument's reach). The tier-1 and B marks grade the mechanisms' exact arithmetic; the tier-2
direction readings are printed but were never bound.

## Suites on the final bytes (5a1016e)

- tests/genome: «Ran 782 tests in 158.932s OK (skipped=1, expected failures=6)», exit 0, slot peak
  855 MB (baseline 763 + this law's 19 tier-1/B tests, exact).
- tests/tools: «Ran 1307 tests in 419.533s OK (skipped=33)», exit 0, slot peak 1654 MB (baseline 1297
  + this law's 10 bench tests, exact).
- Log shas and the RED/GREEN pair: `records/suite-shas.txt`.
