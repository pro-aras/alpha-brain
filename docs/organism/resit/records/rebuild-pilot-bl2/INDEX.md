# records/rebuild-pilot-bl2 — the PILOT PRICE of the origin rebuild (R10f), measured on the closed brain-long-2's tape under its own code

*edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 18:28 +0400 — written at the wrap-up from the files named; `tools/brain/rebuild_origin.py pilot` (22 tests green) replays the first K rows of a life's tape through the life's OWN Mind, sampling CPU and RSS every N rows. Both pilots read brain-long-2's tape (closed) because brain-long-3's sittings do not exist yet; brain-long-3's tape also interleaves maker rows (about 0.5 percent).*

| run | rows | result |
|---|---|---|
| p1 (`p1.pilot.json`) | 5,000 | 74.6 CPU-s, RSS 195 to 255 MB, a noisy 3 percent sample (fit r2 0.48); not a price |
| p2 (`p2.pilot.json`) | 35,074 of 165,402 (stopped by the 900 CPU-s cap) | 900.3 CPU-s in 1,102 s wall; CPU per row **0.0069 at the start, 0.030 in the middle, 0.094 at the end** (the cost per row is ACCELERATING: x13.7 across 35k rows); RSS 195 MB to 614 MB, VmHWM 814 MB, /usr/bin/time max RSS 834,024 kB, slot cgroup peak 983 MB |

**Extrapolation to 165,402 rows (the s1b1 begin ask; 162,596 for the fresh begin), all three printed:** LOWER 3.64 CPU-h (the last window's rate held constant — growth ignored), CENTRAL 2.08 CPU-h (a power law fitted to ALL intervals, exponent 0.36, r2 0.77), UPPER 7.45 CPU-h (the law fitted to the last third, exponent 1.42, r2 0.37). **The central figure is BELOW the lower bound and is not credible**: the early intervals pull the all-interval fit down while the cost per row is accelerating. The honest reading: **the rebuild costs between about 3.6 and 7.4 CPU-h, i.e. it STRADDLES or EXCEEDS the law's 4 CPU-h line; above it the builder STOPS and the SEAT DECIDES (law section 5, R10f).**

Memory: linear through the samples, about 0.012 MB per row, gives about **2.2 GB at the begin row**; the last third's slope was about zero, so no tighter or looser bound comes from this pilot; the live life itself reached about 12 GB at 3.4 days (cells grow), so a rebuild's `SLOT_MEM` must be set from a longer measure, not from this line.

Verdict string printed by the tool: STRADDLES. Not covered: a pilot on brain-long-3's own tape, a pilot past 35k rows, a measure of the replay's memory beyond 614 MB.
