# PREREG-REVISE-1 — the belief-revision assay: does counterevidence MOVE a belief, in the evidence's own direction, and nowhere else?

edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 23:39 +0400 — authored under Ahmad's 10-09
words (the contemplation passage, quoted in PREREG-CONTEMPLATE-1) and the queue named at its signing
(«REVISE-1 — the belief-revision assay, the literature's minimal signature, promised tonight»); the
muse law's §6 names this law's three marks: planted counterevidence, locality, PE-gating; the fourth —
the DIRECTION proof — was promised with it. The night's own reading (Tanno et al., bioRxiv
2026.10.02.755501, /data/research/brain-mechanisms/2026-10-09_…credit-routing….md) supplies the
opponent form: revision is a signal ROUTED back along the responsible parties, its SIGN set by the
evidence's sign — the assay measures exactly that in the organism's own stores.

## §0 · What is under assay, named against the code — and what is NOT

Two revision mechanisms EXIST today, both verdicted, neither yet measured under controlled
counterevidence:

1. **The word-belief store** (genome/think.py, W3-1): `believe()` at THINK word items
   (creature/mind.py:3385 — the real chain: `questions_why` → `believe`, cells from the word's SIGHT
   cells). Revision = rule 4: standing cells REMOVED, or the ledger reassigned → a `clash` row naming
   both lines (append-only; the fresh belief becomes standing). In the WILD (brain-long-5, read-only
   read at ~181k moments, 2026-10-09 23:35): 615 rows = 195 beliefs / 266 revisits / 152 extensions /
   **2 clashes** («do» at moment 139,950; «music» at 187,850). The path fires, rarely — and its
   correctness (did the belief move TOWARD the evidence? did nothing else move?) has never been graded.
2. **The SELF claims** (genome/web.py, PREREG-KW-1 §4.3): `Claim.observe(ok, at)` — quantified
   self-beliefs demoted when contradictions pass the claim's tolerance after `min_events` (bl5 today:
   573 demotions). Demotion is revision at the claim level; its direction and gating are exact by
   construction and ungraded as an assay.

NOT under assay (scope, said plainly): the muse's TENTATIVE rows (CONTEMPLATE-1's own promotion rule;
its revision is the NEXT law's), the brain's continuous weight learning (that is adaptation, not
belief revision), and any NEW mechanism — **this law installs nothing; it is an instrument law: tools/
and tests/ only, zero organism edits.** Its verdict grades the organism's EXISTING revision mechanics.

## §1 · The assay (three benches; every constant declared before any reading)

**TIER 1 — the store's law, scripted streams through the real `believe()`.** A scratch beliefs.jsonl;
scripted (word, cells, episodes, moment) calls into `think.believe` with a planted two-word world
(W the target, X the bystander, believed once and never touched again). FIVE planted stream shapes for
W: (a) REMOVAL-FLIP — standing {c1,c2}, then calls carrying {c3,c4} (disjoint); (b) PARTIAL REMOVAL —
{c1,c2} → {c2,c3}; (c) GROWTH — {c1,c2} → {c1,c2,c3}; (d) SAMENESS — {c1,c2} throughout; (e) LEDGER-
REASSIGN — the cells UNCHANGED, but the planted ledger (`ledgers["sight"]`) now maps a standing cell
to ANOTHER word (decision 4's own case — and the wild's own clash shape: both of bl5's wild clashes
are drifted-label reassignments). The production call passes `ledgers`; so does every tier-1 stream
(a minimal planted ledger), never None. Plus the
ORDER null: the derangement family of (a)'s call sequence — the store's own arithmetic makes a clash
fire exactly at each standing→disjoint transition, so the ordered flip reads exactly 1 clash (one
boundary) and every non-monotone derangement reads ≥ 2 (≥ 2 boundaries; the reversed monotone order is
excluded from the draw). 10 seeded derangements.
*The mechanism's own OFF-switch as the control:* the same streams with `clash_enabled=False` (the
gene's declared gate) must read `clash_refused` and never a clash row — a grader that cannot see this
is blind.

**TIER 2 — the organism's revision, the lived toy world with a planted naming flip.** The N1/muse
bench's toy form (the N1 bench's own genome, 8 things) lived twice from one seed to a declared
checkpoint: the FLIP twin, in which one thing's taught name is swapped at the flip moment (the parent
names thing A's visual with thing B's word from then on); the NO-FLIP twins, 10 seeds, the world
unchanged. The bench drives the production call chain itself — `questions_why(org, ledgers, episodes,
word)` → `think_laws.believe(...)` exactly as mind.py:3350–3386 calls it — at declared checkpoints
(pre-flip, post-flip at the declared lag), never a re-implementation. **The population count, written
before the marks bind (the pilot, #228):** whether the flipped word's answering SIGHT-cell set MOVES
within the bench horizon (disjoint or partial), printed as cells-before/cells-after; if it never moves,
the bench REFUSES to grade (NOT-GRADABLE — no revision can fire where the representation never moved;
that is a bench finding, never a mechanism verdict).

**BENCH B — the claims' demotion, exact.** Planted Claims on scripted observation streams:
`always` at level L fed confirmations to `min_events` then contradictions; the symmetric `usually`
under confirmations; a below-floor all-contradicted run; and the SIGN null — the same event count with
contradictions swapped for confirmations.

## §2 · Gates

- **G-UNIT** — tests for: the four tier-1 streams' exact expected rows (kind sequence + standing sets);
  the derangement arithmetic (clash count == standing-boundary count, pinned on all 10 draws); the
  locality reader (byte-identity of X's chain, with the presence count printed — #168); the graders'
  own planted controls (a doctored store with the clash branch neutered — run via the gene's own
  `clash_enabled=False` — must FAIL M-T1-REVISE; a doctored locality reader that rewrites X must be
  caught); bench B's exact crossing arithmetic; determinism ×2 to the last digit of every bench output.
- **G-CHAIN** — a test pinning that the tier-2 bench's belief calls go through the SAME two functions
  mind.py:3350/3385 calls (imported, never copied) — the seam tested at the seam.
- **G-PLANT** — the doctored no-flip-landed tier-2 bench (the driver claims the flip; the world never
  changes) must be CAUGHT: the pilot's cell-movement reading reads «no move» and the bench refuses
  NOT-GRADABLE. A bench that grades anyway is the failure.
- **G-DET** — every bench twice, byte-identical rows/reports.

## §3 · The marks (bars written first; ceilings from the mechanism's own arithmetic)

- **M-T1-FORM** (the revision form matches the evidence shape): (a) REMOVAL-FLIP → ≥ 1 clash row, the
  post-flip standing EXACTLY the planted {c3,c4}; (b) PARTIAL REMOVAL → ≥ 1 clash (rule 4 is
  unconditional — the pinned behavior); (c) GROWTH → an extension, ZERO clashes; (d) SAMENESS →
  revisits only, ZERO clashes; (e) LEDGER-REASSIGN → ≥ 1 clash with the cells UNCHANGED (the
  ledger half of rule 4, the wild's own shape — a stream that never exercises it assays half the
  mechanism). Ceiling note: exact — the store's rules decide each shape's row kinds
  deterministically.
- **M-T1-ORDER** (revision is a function of evidence ORDER — temporal credit, not a bag of cells):
  the ordered flip's clash count == 1, strictly below all 10 derangements' (each ≥ 2 by the boundary
  arithmetic; printed). 
- **M-T1-LOCAL** (locality): the bystander X's chain byte-identical at every checkpoint of every
  stream; presence count printed (n rows of X).
- **M-T1-DIR** (direction, exact at this tier): the post-flip standing's cells == the planted
  post-flip set (set equality), and the PRE-flip standing never reappears as standing after the flip.
- **M-T2-MOVE** (the organism revises): in the flip twin, the flipped word's standing set MOVES after
  the flip (a cell removed, or a clash row) with onset at the first post-flip checkpoint; the 10
  no-flip twins' move count over the same window printed; bar: the flip move where the null MAX is 0,
  else above it (the N1 null form).
- **M-T2-DIR** (the direction proof at the organism's scale): on the organism's OWN post-flip episodes,
  graded by induce's own nearest-in-cluster test (`_nearest_in`, the real geometry): the post-flip
  standing's agree share ≥ the pre-flip standing's post-flip share + the margin from the pilot (the
  smallest passing gap 10/n printed beside it — #245(5)); AND the pre-flip standing's post-flip share
  < its own pre-flip share (the world moved under it). Margin bar: measured in the pilot, printed,
  never tuned after the graded run.
- **M-T2-LOCAL**: every other believed word's rows byte-identical across the flip window; presence
  counts printed.
- **M-B-DIR**: the planted `always` claim demotes EXACTLY at the crossing observation (the index
  printed, `first_demoted_at` correct); the `usually` twin under confirmations stays trusted.
- **M-B-FLOOR** (PE-gating's floor): below `min_events`, an all-contradicted claim stays trusted — the
  evidence's amount never fires before the declared floor.
- **M-B-SIGN** (the opponent null): the same event count with the signs swapped never demotes — the
  SIGN of the evidence, not its amount, drives the revision.
- **M-COST**: the whole assay ≤ 30 CPU-min, peak ≤ 1 GB (SLOT_MEM=1G), measured-first (RULES §6d).

## §4 · Verdict forms

**PASS** — all gates + every mark, the plants caught. **FAIL-MECHANISM** — the tier-2 cells move under
the flip but the belief never follows (the organism's stored beliefs do not track counterevidence at
bench scale): a RESULT; the road re-reads the store's law. **FAIL-FORM** — the flip never moves the
answering cells in the bench horizon (the instrument cannot fire): named, an amendment re-prices the
bench. **VOID** — a gate fails (the instruments cannot be trusted). A bar is never loosened on retry;
a cause that is the instrument gets an amendment, a cause that is the mechanism is a result (RULES §2).

## §5 · Price

Tier 1 + bench B: seconds. Tier 2: the toy world lived × (the pilot + the flip twin + 10 no-flip
twins), the N1-bench class (measured there: peak 52 MB, ~10 s a run) → ≤ 30 CPU-min total,
SLOT_MEM=1G. The assay is a bench law: no replay of any life, no live root, nothing under
/data/dev/genome-lives touched.

## §6 · Adversarial walk

- The tier-2 flip can pass vacuously if the word's cells never move — the pilot's population count is
  printed BEFORE the marks bind, and the G-PLANT no-flip-landed bench must refuse (not grade).
- «Locality» is proven on the store's BYTES (the bystander's rows), never inferred from the mechanism's
  prose; presence counts printed everywhere a «0 of N» appears (#168).
- The order null is deterministic by construction (a clash per standing boundary): the draw excludes
  both monotone orders; all 10 counts printed beside the ordered 1.
- The margin in M-T2-DIR is measured in the pilot and printed; if the pilot's separation is smaller
  than the smallest gap the n can pass (10/n), the mark reads UNDERPOWERED, never silently passed
  (#245 (5)).
- A natural drift move in the no-flip twins is NOT a failure of the null — it is the null's reading;
  the bar sits above the null MAX (declared both forms at §3 M-T2-MOVE).
- The bench drives the production call chain (G-CHAIN), so a green bench is about the organism's own
  mechanism — but the THINK scheduler (WHEN the mind thinks) is not under assay; a life-level revision
  rate is a reading for the audit, not a mark.
- What this law does NOT claim: that revision is optimal, Bayesian, or human-shaped; that the muse's
  tentative rows revise (next law); that two wild clashes prove health. It claims the minimal
  signature, measured: counterevidence moves the belief, in the evidence's direction, locally, and not
  without evidence.

## §7 · Signatures

Author: Kimi Code (K3) — 2026-10-09 23:39 +0400. Verifier loop: the adversarial read recorded in
`verify/REVISE-1-VERIFIER-READ.md` beside this law before the seat signs. The seat: SIGNED under
Ahmad's 10-09 words; the SEAT-LINE in `SEAT-LINE-REVISE-1.txt`.
