# PREREG-HEARS-2 — AMENDMENT 3: a learn event is a TAPE ROW; the maker redraws its first pictures after every restart

*Drafted by Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:07 +0400, on the seat's word (12:0x), after the first REAL D2 read FAIL. **A file of its own**: the signatures of AMENDMENT 1 and AMENDMENT 2 stand untouched; the law of HEARS-2 is `PREREG-HEARS-2.md` + `PREREG-HEARS-2-AMENDMENT-2.md` + this file. It moves no bar and no launch gate. It corrects the reading of A1.7 (b) and (c), names the cause (RULES §2: the instrument, not the mechanism), and registers a reading caveat for the days. The architect co-signs by the sha256 of this file after its last edit; the seat signs after.*

## A3.1 · What happened, and the cause (RULES §2)
The seat's real pre-flight of `hears scene maker` (`brain-long-3-pre-1`, 11:55) ended `PREFLIGHT PASS`; `tools/lives/hears_d2_read.py` then read the SAME life **FAIL with 16 violations**: after each of three resumes (`resumed_from_seq` 2060 / 4356 / 5780) the first maker learn row «re-learned» the moment `w0000i000001t000000000` with scene 2, 6, 12 where it had first been learned as 0, and later new moments «did not take the next index».

**The cause is the checker, not the mind.** The checker took the moment NAME as the identity of a learn event. The maker world keeps `window`, `i`, `total` and `window_start` in the sense thread's memory (`creature/world_maker.py`, `sense()`, lines 180–183) and `make(seed, window, i)` is deterministic, so after every restart the maker redraws its first pictures under the SAME names on NEW tape rows: on the real tape `w0000i000001t000000000` sits on seq 5, 2075, 4388 and 5954. The brain heard each of those tape rows once and gave it the next index; the rows re-consumed after the last resume (seq 5925 / 5931 / 5949, journaled before the `start` row because the startup replay writes them first) carried 9 / 10 / 11 again, the indices they had before the kill. Found independently by the integrator (copies of the tape and journal) and by the verifier (**[Certain]**, copies under `verify/d2diag/`); reproduced by this lane on the real root.

## A3.2 · The correction to A1.7 (the identity of a learn event is its tape row, `seq`)
A1.7's wording «any maker moment learned twice … carries the SAME `scene` and `world_seed`» is superseded by:
- **(a)** the maker's count CONTINUES across each resume: the first maker learn row after a `start` event with `resumed_from_seq > 0` carries the index the brain restored — the index the same **seq** carried before if the journal already holds that seq (a row re-consumed after the resume), else one past the number of distinct maker **seqs** learned so far; never 0 again;
- **(b)** any maker TAPE ROW (seq) journaled twice (the days law's residual) carries the SAME `scene` and `world_seed` both times; every NEW seq, whatever its name, takes the next index; every maker row carries `world_seed_of(SEED, maker)`;
- **(c)** every census file equals the journal's own count by world over the first N distinct learned **seqs**.
A name that reappears on a new seq is a NEW canvas, counted (`moment_ids_reused`), never a fault.

## A3.3 · The instrument, changed
`tools/lives/hears_d2_read.py` keys `seen` and (c)'s order by the learn row's `seq`; a FOURTH control joins the three: `redrawn` — an earlier name, an unseen seq and the next index — must read NEW (no violation added; `MISREAD` fails the run), beside `reset` / `seed` / `census`, each CAUGHT. The real pre-flight's rows are a committed fixture (`tests/fixtures/hears_d2/`), RED on the name-keyed checker (verdict FAIL) and GREEN on the seq-keyed one; 21 tests; a sweep of 18 mutants, the original bug among them, none surviving. **The SAME real root re-read: `D2 PASS`** (exit 0; 9,098 journal rows, 3 resumes all bracketed by maker rows, 75 maker learn rows on 72 tape rows, 3 rows journaled twice by seq with equal scene and world_seed, 12 maker tape rows reusing an earlier name, census 250: 1 vs 1, the four controls as expected). The mind's code (55ef469), the genome and the launch commit's behaviour are unchanged by this amendment.

## A3.4 · The READING CAVEAT for the days: the maker restarts at window 0 after any restart
Because the maker's `window`, `i`, `total` and `window_start` live in process memory, after ANY restart or resume of the body (a power cut, a kill, the health watch's restart) the maker restarts at window 0: its 4-hour arrivals (§4: «every 4 h the maker adds names») restart from the FIRST vocabulary, it re-draws its first pictures, and `total` (the plant's canvas counter) restarts. Therefore, for every reading of `brain-long-3` (§4, A1, A2):
1. **every restart is NAMED on the maker series** — the journal's `start` rows with `resumed_from_seq > 0` are printed beside it (`tools/brain/hears_read.py` prints each restart's position in the maker turns and marks the windows that contain one);
2. §4's «new names every 4 h» and «first true say of each maker word» are read **per restart segment**: a name that reappears after a restart is a redraw, not an arrival;
3. A2's **verdict copy** and every g_c(t) print the restarts that lie between the origin and the copy (a restart returns the feed to the maker's first pictures, which are a fraction of the vocabulary the brain had by then).
**Persisting the maker's `window` / `total` is a LATER rung, not the launch commit:** it needs its own law and the maker's pinned `make()` stays untouched; `brain-long-3` launches with the maker as it is.

## A3.5 · What this amendment does not change
No bar of §2 or §3; no launch gate; the ladder (RULES §3); the mind, the organ, the genomes.

*Co-signed: Claude (Opus 5.5, swarm architect), 2026-10-03 12:09 +0400 (from `date`) — on the text of this file as committed at bc57862 (sha256 e58cda4928eca89d9756c73e2ed0e2efe4e9ad285169ccbed047aa4cd7dfc8b9); any later edit other than a signature line voids this co-signature. Signed: the seat — pending.*
*(edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:07 +0400)*
