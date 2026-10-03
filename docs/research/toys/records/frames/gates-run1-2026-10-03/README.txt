Toy C, REAL gates, run 1 (2026-10-03 22:12:22 to 22:25:09 +0400): the record of the G5 FAIL that stopped the unit.

Code of record: 724865d (tree clean), the ten copies verified against their manifest. Command (through slot, SLOT_MEM=2G):
  PYTHONPATH=. OPENBLAS_NUM_THREADS=1 /data/dev/swarm/bin/slot toys gates-real -- python3 -B -u -m tools.toys.frames.run gates
Outcome: G1 OK, G2 OK, G3 OK, G4 OK, G6 OK, G5 FAILED: the predicted unit CPU 182.1 min exceeds the ceiling 40.0 min. GATES.json (passed False) sha256 55bb8eb036da21a2e77d89e53571dcdedbd06e4169a984aaf26bf08f00ccb582.
The unit was NOT run. The load average during the run was 8-9 (seven lanes).

THE DIAGNOSIS (timing and counts only; no gain, null value or verdict printed or kept):
  g5_cost_diag.py  one gain() and one NULL-1 and one NULL-2 draw per rule on the real ALPHA4 split (log: g5-cost-diag.log)
  g5_cost_prof.py  cProfile of one WEB-H NULL-2 draw (its output was first read from a terminal pipe, not a file; re-run for a file at record time, see gates-run1-reruns/ when present)
  g5_cost_count.py the generator draws per NULL-2 pick, the bigram bins, and vectorised-against-scalar stream identity (same note)
The seat's ruling on this FAIL: option A, a byte-identical speed-up of null._pick_bigram, proved by tests/tools/test_toys_frames_null_pick.py, then the gates re-run from a clean committed sha.
