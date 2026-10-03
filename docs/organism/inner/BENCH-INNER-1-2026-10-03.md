# BENCH INNER-1 — the inner turn on brain-long-2's copied generation (PREREG-INNER-1 §3–§4, AMENDMENT 1 A5–A8, AMENDMENT 2)

*Written by Claude (Fable 5.1, swarm integrator, the builder), 2026-10-03 12:2x +0400 (the minute is the commit's). The law: `PREREG-INNER-1.md`
signed by author, builder and seat at research-1003 @ 7c49f62 (file sha256 b489209c…), AMENDMENT 2 at babc0da (sha256 242f64ca…) co-signed by the
builder 12:09; the code: inner-1003 @ 9a037ec (afe3909 the parser + registry; f123190 `Brain.turn_remembered` + `scenes_with`; 9c70783 the mind's
`_inner_turn`, `creature/inner.py`, the bench; 9a037ec the bench's B1 expectation). Every figure below is checked against the record's own files
by `docs/organism/inner/records/check_bench_doc.py` (the commit's log line says so); the record files are copies of the bench's outputs under
`docs/organism/inner/records/bench-inner-1/` (RULES §14).*

## 1 · What was run (§4 of the law, as amended)
- **The generation:** `brain-long-2`'s `state/prev` (a complete generation under the days law's snapshot rule), copied 11:18:16 +0400 with `cp -a` while
  the life was alive; every file's print equal to `SNAPSHOT.json`'s manifest and every sha256 equal to the original at the copy
  (`int/bl2-gen/COPY.clock`): **last_seq 330,367**. The life's tape (5 day files), journal (5), `truth/` and `web.json` copied after its close
  (11:46; `int/bl2-inputs/COPY.clock`, sha-equal).
- **The genome in force at that generation (A5):** `GENOME.v1.genome` (KWTA 4, adopted 2026-10-01 01:59:55; sha256 fd15f9e3…) + the line
  `INNER    every body row when idle; walk lift; inhibit 2; restart 5`. The mind is loaded by `Mind.resume` from the copy and fed **1,000 synthetic
  SENSE body rows with backlog 0** through `mind.consume` (the production handler), then ONE planted backlog-1 row and ONE row with no reading
  (G1's plants). Two plant runs through the same handler under TEST parameters never parsed from a genome (A4, A2.1): `greedy-count` from the
  SAID words (the read plant) and `greedy-count` from the TOPIC with no restart and no inhibition (§0.2's counted walk, the lock plant).
- **The record's run:** `records/bench-inner-1/` = the bench's fourth pass (`int/bench-inner-4`, code 9a037ec); the third pass (code 9c70783) and
  the second (uncommitted bytes) read EQUAL section by section (the bench is deterministic: every draw is a substream of the genome's SEED or the
  bench's own; `check_bench_doc.py --equal` prints the comparison).

## 2 · The gates and the mark (§3), from `GRADE.txt`
| # | What | Read | Verdict |
|---|---|---|---|
| G1 | fires where it must and nowhere else | turns **1,000 of 1,000** eligible rows; skipped `{backlog: 1, no backlog reading: 1}` — the two plants, by reason | **PASS** |
| G2 | grounded | EXIST **1.000** (1,000 / 1,000: every remembered moment on the tape with its topic among that moment's ear words; 118,567 moments indexed); the planted citation of a moment on no tape **CAUGHT** | **PASS** |
| G3 | the walk does not ruminate | the law's walk covers **13 of 13** mature words (bar 10); largest share **0.212** (ring, the self's weakest word, as §5.6 predicts); sources self 200 / web 800; no lock. The LOCK PLANT (greedy-count from the topic, A2.1): distinct **2**, period **2** (big ↔ ring — §0.2's own count) → **CAUGHT**. The READ plant (greedy-count from the said words): covers 9 of 13, largest share 0.316, no cycle — a reading | **PASS** |
| **K** | **TRUE OF ITS PAST (the bar)** | **929 of 1,000** turns say something TRUE of the thing under the target (0.929; said 940, every say on a thing) against the DEALT-PHRASE null (scene and target kept; 200 draws): p95 **206**, mean 185, max 218 | **PASS** |
| K-ablated | the null can see a scene-blind mouth | the constant phrase «ring» (the most frequent inner say) reads **191**, exactly its own null's p95 (a constant phrase is invariant under dealing) | **FAILS, as it must** |
| K-plant | | one TRUE turn's phrase replaced by another turn's phrase that is not true of its thing: reads FALSE | **CAUGHT** |
| A2.2 | the truth files against the regenerated spec | **1,000 checked, 0 mismatch**, 0 without a file, 0 without an eye row (`truth/scene/<seq>.json` vs `brain.scene.world.train_scene(world_seed, scene)`, every thing's shape / colour / size / top / left, the words, the referent); the planted one-field mismatch **CAUGHT** | **PASS** |
| read-only | §2 / A2.3 | the brain's state hash and the web L unchanged over the whole run; the self unchanged but for B1, which the self's own rule observes on every body row that carries a reading: **+1,001 on 1,001** such rows (the no-reading plant reaches no observation) | holds |

## 3 · The readings (§3; no bar)
- **R-RET · retention, paired with the live turn** (the DRIVE turn the life took on the same scene when it was learned; 50,000 live turns on record):
  n **1,000**, inner **0.929** vs live **0.917**; both 905, inner-only 24, live-only 12, neither 59; the smallest passing gap 10/n = **0.010**;
  one-sided sign test p(inner better) **0.0326**. The inner turn re-sees TRAINING scenes after the brain has learned all 50,000: at least as true as
  the live turn, as the law predicted for a stationary world.
- **R-AGE · the organism's own forgetting curve**, K's truth rate by deciles of the remembered scene's learn order (oldest first):
  0.950 · 0.900 · 0.950 · 0.950 · 0.930 · 0.910 · 0.920 · 0.980 · 0.910 · 0.890 — FLAT (the prediction on this copy: one stationary world, a brain that
  never forgets); its slope in a later life is what INNER-2 needs (§6).
- **R-ASSOC · does the association hold in memory:** of the **800** web hops, the re-seen say contains the topic the web chose in **0.135**, against
  the frequency-matched null's p95 **0.0512** (mean 0.0513): ABOVE — the association survives in the brain's own re-seeing beyond frequency.
- **R-SELF · does the self know its weak words:** over the 13 mature words, Spearman ρ **0.451** between the self's lived reliability and the inner
  turns' per-word truth; label-permutation null (1,000 draws) p **0.059**, null p95 0.462 — agreement at the edge of its null (expected: the two
  are measured on related data; disagreement would have been the finding).
- **Cost:** **6.7 ms CPU** per body row on the record's run (the load 16.7 s CPU; the third pass read 6.4 / 17.7 beside other lanes' jobs — the
  CPU-second is load-dependent on this box, #242, so the cost is a reading of the run it cites) — far under the law's «≤ 1 per 60 s of body clock».

## 4 · What this does NOT show (§5.7, §6)
Improvement: none claimed (a read-only turn changes nothing). INNER-2 (learning on the remembered scene) is written only after the forgetting
prediction is measured on `brain-long-3` (HEARS-2 AMENDMENT 2's verdict copy). The closed-tape replays with the line ON are identity checks
(§0.4: the full cut's one eligible body row precedes its first calibration; the lean tape has no body row) and run at the landing (G0 / G0b),
with the suites; G4 (a resume mid-chain) is pinned by `tests/creature/test_inner_mind.py::Resume` and read in the pre-flight the seat launches.

## 5 · The instrument's own faults on the way (recorded, each pinned)
A hand-written test Web without `stats["events"]` made `Web.hear` raise on the mind's first ear row and `_web_fail` switched the web AND the self
off for the life (every chain at position 1) — pinned by `test_inner_walk.HearRuns`; a parity read one learn apart (the DRIVE turn precedes the
learn) — pinned at one state; a plant that moved a fixation the turn never reports — moved to the saying thing; a read-only pin around `consume()`
that caught the self's own B1 observation — around `_inner_turn` alone; the bench's first truth cross-check looked in `truth/` (the maker's boxes)
instead of `truth/scene/` (no file 1,000) — A2.2; the bench's first B1 expectation counted the no-reading plant — n + 1.
