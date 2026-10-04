Toy C, REAL gates, run 2 (submitted 2026-10-03 23:53:12 +0400, admitted by slot at 23:56:43 after a 210 s wait, ended 2026-10-04 00:00:32): ALL SIX PASSED.

Code of record: e8ee2f5 (the NULL-2 byte-identical speed-up, tree clean: toys_tree_dirty false in the record's header), the ten copies verified. Command (through slot, SLOT_MEM=2G):
  PYTHONPATH=. OPENBLAS_NUM_THREADS=1 /data/dev/swarm/bin/slot toys gates-real2 -- python3 -B -u -m tools.toys.frames.run gates
GATES.json sha256 f1f9621bccdd7412b1a46d3af8e9bc2c2d5f838a2a799dd5a8ad58cb4bcad9f4 (passed True, failures []; prereg shas a9787ef8... / 158660bb... / 948d7704...).
G5, the price, against run 1 (../gates-run1-2026-10-03/, the FAIL at 724865d):
  pilots at 10 and 20 null draws: 66.0 and 83.7 CPU-s (run 1: 239.2 and 455.5); slope 1.769 CPU-s a draw (run 1: 21.63);
  predicted ALPHA4 at 100 draws 225.2 CPU-s (run 1: 2,185.7); the five conditions priced as five ALPHA4s (a ceiling): 18.77 CPU-min against the ceiling 40.0 (run 1: 182.1);
  peak RSS 190.8 MB against 1,024; the whole gates run 228 CPU-s, the slot's measured cgroup peak 249 MB.
Load (the seat's terms): before 10.32 9.80 8.84 | cpu pressure some avg10 0.28 avg60 0.23; after 7.91 8.87 8.80 | avg10 0.00. The box was loaded and a CPU-second inflates under contention (SOLUTIONS #242), so a quiet-box price can only be lower: the reading passes the ceiling with margin from above, and no LOAD-SUSPECT is needed.
No ceiling, bar, draw count or law text was changed between run 1 and run 2: the only change is the byte-identical NULL-2 pick (../null-pick-speedup-2026-10-03/).
