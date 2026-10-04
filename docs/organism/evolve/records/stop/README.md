# The STOP stage of PREREG-EVOLVE-CAL — records

*Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:5x +0400. Law: `docs/organism/evolve/PREREG-EVOLVE-CAL.md` A1 (iii), A2.1; the seat's approved epsilon ladder (21:1x); AMENDMENT 3 reads these files. Nothing here is a full run.*

## What was run

Seven twins, each ONE process through `slot` (`SLOT_MEM=8G`, `/usr/bin/time -v`), the first 1,000 rows of S1 (seq 304,003 … 305,002) from brain-long-2's shadow checkpoint 32 (a verified copy), command:

    SLOT_MEM=8G SLOT_SWAP=1G slot integrator evcal-stop-<twin> -- /usr/bin/time -v env PYTHONPATH=. OPENBLAS_NUM_THREADS=1 \
      python3 -B -m tools.evolve_cal twin --cp <cps/32> --slice-root <slices/S1> --from-seq 304002 --to-seq 308667 \
      --variant <v> --rows-limit 1000 --label stop-<twin> --out <dir>

| twin | variant | started | what it is |
|---|---|---|---|
| T0 | incumbent | 20:51:41 | the reference; replication control against the production worker's recorded round-13 incumbent journal |
| T0b | incumbent | 21:02:31 | the same genome again: the determinism control |
| Ts | seed:1 | 21:07:10 | A1 (iii)'s SEED pair |
| Te | eps:1e-05:1 | (waited for a slot; started 20:55:56) | A1 (iii)'s epsilon pair |
| P1e-4, P1e-3, P1e-2 | eps:0.0001:1, eps:0.001:1, eps:0.01:1 | 21:17:42, 21:27:33, 21:38:32 | the seat's ladder, strictly one twin at a time |

Code of record: T0 and Te launched on `008208f` (clean; `CODE-SHA.txt`); T0b and Ts on this branch's tree of 21:02 and 21:07 (the content committed as `ef5f38f` at 21:04:13); the probes on the tree each imported at its own start (`CODE-SHA-probes.txt` = `21070be`, the head when the chain was launched at 21:13): P1e-4 at 21:17:42 on the content of `070379a` (21:16:53), P1e-3 at 21:27:33 and P1e-2 at 21:38:32 on `73d059e` / `9b6fe5c` (the keyed comparison added to `tools/evolve_cal.py`, a new function nothing in the twin path calls). **The twin path is unchanged across them**: `git diff 008208f 2fce569 -- tools/evolve.py tools/evolve_cal.py` touches no line of `build_twin` or `tape_slice`; `grade_twin` gained optional parameters; `run_twin` reads the load through `ev.machine_snapshot()` instead of its own copy of the same reader. A twin's own `reading.json` carries a `code` field read at the END of its run (it names the tree's head then, not the code it imported): the table above and `CODE-SHA*.txt` are the authority.

## Files

- `twins/<twin>/{reading.json, journal.jsonl.gz, GENOME.genome}`: the twin's readings (q1_seen, confirmed_share, frames_filed, CPU / wall / build seconds, the dense `state_hash` and sparse `row_hash`, the journal's digest, load and CPU / memory pressure at the start and end, peak RSS), its journal (canonical lines) and the genome text it ran. `SHA256SUMS` lists them (`sha256sum -c SHA256SUMS` from this folder).
- `logs/<twin>.{log,exit,started}`: each twin's own stdout/stderr with `/usr/bin/time -v`, its exit code, its start.
- `reports/report-final.json` (`docs/organism/evolve/scripts/stop_report.py`: the replication control against the recorded journal with its plant, the determinism pair, the SEED pair, the epsilon ladder, positional AND keyed) and `reports/stop-table.md` (`stop_table.py`, the table of AMENDMENT 3's A3.1).
- `recorded/round-13-incumbent-journal.jsonl.gz`: the journal the production worker recorded for this incumbent on this slice (brain-long-2, `evolve/round-13/incumbent/journal`, 4,395 rows; original sha256 in `round-13-incumbent-journal.sha256`).
- `READING-RULE-LADDER.md`: the ladder's reading rule, committed at 513f382 BEFORE the first probe finished.

## Re-deriving the table (about 30 s)

    PYTHONPATH=. python3 -B docs/organism/evolve/scripts/stop_table.py --dir docs/organism/evolve/records/stop/twins

The staged inputs (not in git: 2.3 GB of checkpoints and 119 MB of mini tapes) are under `/data/dev/swarm/2026-10-03/evolve-cal-scratch/`; each copy was verified against the closed life's files (`stage-checkpoint --verify`, `stage-slice --verify`), their manifests' sha256: cps/32 `0f62caccdaf5…`, cps/34 `a0a2d59c0c8a…`, cps/8 `96cc58eea40e…`, cps/10 `e494fcbbda16…`; slices S1 `a5a3a32f333b…`, S1next `b992d3a459f4…`, S2 `2a9e4608c8ff…`, S2next `5ee1fd784bf7…`. `python3 -m tools.evolve_cal stage-slice --live-root /data/dev/genome-lives/brain-long-2 --declared-tape run/tape --from-seq 304002 --to-seq 308667 --out <new dir> --verify` rebuilds S1 from the life's own tape.
