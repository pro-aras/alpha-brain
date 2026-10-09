# G-SUITES on the alpha-6 branch (PREREG-ALPHA-6 §3) — the five suites through slot, one heavy job at a time

Run on the branch's bytes at each suite's start (the creature parts re-run after the FakeBrain stand-in fix —
see the pin note and the part-1 note below; every log + exit beside this file and in the worktree's
`scratch/a6/suites/`). Slot form: `SLOT_MEM=4G bash /data/dev/swarm/bin/slot kimi a6-<suite> -- …`; the creature
split at 10G (`split_suite.sh`, partition-exact).

| suite | the suite's own line | exit | peak |
|---|---|---|---|
| genome | «Ran 757 tests in 163.961s / OK (skipped=1, expected failures=6)» | 0 | 900,206,592 B |
| scene | «Ran 391 tests in 132.188s / FAILED (failures=1)» — **exactly the one named failure, below** | 1 | 244,752,384 B |
| tools | «Ran 1293 tests in 421.308s / OK (skipped=33)» | 0 | 1,721,352,192 B |
| brain | «Ran 793 tests in 383.935s / FAILED (failures=1, skipped=3)» — **the same one named failure** | 1 | 932,335,616 B |
| creature, 3 parts | 444 OK (skipped=5) / 572 OK (skipped=1) / 476 OK — **SUM 1492 = 1492, PARTITION EXACT, every part exit 0** | 0 ×3 | 8.86 / 10.04 / 8.91 GB |

## The one named failure (the pinned window's own line — the seat's one-line edit at integration)

`tests/brain/scene/test_cache_s1b1r.py:30` asserts `C.RUNS == /data/dev/brain-runs/scene-organ-swarm-1005`. The
law §6's window moved RUNS to the FRESH root `scene-organ-alpha6` (the redraw: **«caches compared 63 · differing
0»**, the planted bit CAUGHT — `../window/`). Every cache-dependent test in BOTH suites is green on the redrawn
root; the ONLY red line anywhere is that literal path assertion, whose own edit history moves the line with
every window (DRIVE, HEAR, INNER, W1). The file sits inside `tests/brain/scene/`, which the seat's delegation
puts OFF LIMITS to this lane (the cover-law lane's surface, zero file overlap) — so the line stands red here
and is handed to the seat EXACTLY: s/`scene-organ-swarm-1005`/`scene-organ-alpha6`/ on that one line. The scene
suite's pre-window run (`scratch/a6/suites/scene-pre-redraw.log`) showed the window's own price (the pin-priced
errors + the pin line + the mouth-cap caller pin — the last fixed in-branch by the if/else call form, B1's
fixup commit, without touching the test).

## The creature part notes (which bytes ran where)

- The first full split (05:56–06:23, on c452981's bytes): part 1 FAILED (errors=8 — the FakeBrain stand-in's
  constructor had not followed B1's widened contract); parts 2/3 OK (their tests never call the stand-in
  through the widened site — proven by their green on both sides of the fix).
- The stand-in fix (`tests/creature/_scene_tape.py`, commit c2e85ea) landed; part 1 re-ran GREEN («Ran 444
  tests in 512.960s / OK (skipped=5)») on the working tree carrying the fix (== c2e85ea's tree for every
  tracked file; the log's printed sha names c452981 because the commit landed minutes after the re-run began).
- Parts 2/3 then re-ran on the tip c2e85ea for a one-sha record: «Ran 572 … OK (skipped=1)», «Ran 476 … OK».
  SUM 444+572+476 = 1492 = the discovered total (unittest discovery, same form), PARTITION EXACT.
