# HEARS-2 bench records — the launch-deciding evidence (RULES §14)

*Written by Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:37 +0400 (from `date`), on the seat's RULES §14: the bench's result must not live only in `scratch/`. Law: `PREREG-HEARS-2.md` + AMENDMENTS 1–4 (A3 corrected the D2 checker; A4 names the grader and reader changes made at the read stage). This file lives in the commit that records it (`git log -1 -- docs/organism/hears/records/INDEX.md`); the final sha is announced by message and in the lane's handback. Small files are copied verbatim into this directory; the large ones are copies under `/data/dev/swarm/2026-10-03/hears-records/` with their sha256 below.*

## 0 · The result in one screen (the figures are read from the files named beside them)

**All three barred marks PASS and every control is CAUGHT** — `bench-1/hears.txt`, last line: «BARS: C PASS · X PASS · I2 PASS · controls CAUGHT». The arms were launched in the same second (start skew 0.0 s), both exited 0 (`bench-1/arms.exit`), wall 2,731 s and 2,732 s, overlap 1.000 (floor 0.90).

```
  P · the six tests' verdicts, OFF → ON: 1 PASS→PASS · 2a PASS→PASS · 2b FAIL→FAIL · 3 PASS→PASS · 4a PASS→PASS · 5 PASS→PASS · 6 PASS→PASS
  P · every bar of the grade, OFF → ON (14 read in OFF, 14 in ON; a pass of None is a reading, not a bar), whose pass flag DIFFERS: TRUTH-NEED PASS→FAIL (OFF 0.561 n 41 · ON 0.389 n 36 · smallest passing gap 10 / 36 = 0.278 on the smaller n)
  T · TRANSFER (a reading, A1.3; the maker-only comparison is struck: STRUCK (A1.3): 0 by construction (the turn precedes the learn; young 3)). The SHARED words' first k maker meetings, agreed / ALL turns, against 1000 dealt-targets draws (the maker's words permuted among the same canvases, says fixed; seed 20261003); SHOWN iff agreed > the null's p95:
    k = 3: shared words ['circle', 'cross', 'ring', 'square', 'star', 'triangle'] · agreed 17 of 18 (silent 0, word typed at the turn 18) · null p95 6 (max 11, mean 2.858) · pass line 7 → shown True
    k = 1: shared words ['circle', 'cross', 'ring', 'square', 'star', 'triangle'] · agreed 6 of 6 (silent 0, word typed at the turn 6) · null p95 3 (max 6, mean 1.040) · pass line 4 → shown True
  G · GROWTH (a reading, A1.4): maker turns 472 · the LAST 100 (n 100): agreed 89 of 100 = 0.890 (agreed / ALL; says 92) · ceiling 1.000 (turns whose word was typed: 100) · floor, always the commonest word «ring»: 0.140 · surprise 0.000 · distinct said 13 · prediction «above 0.8»: True
    every maker word typed at the last calibration said truly at least once: True · arrow (meetings 37, first true say at maker turn 69), bar (meetings 50, first true say at maker turn 32), circle (meetings 35, first true say at maker turn 33), cross (meetings 42, first true say at maker turn 7), diamond (meetings 49, first true say at maker turn 105), dot (meetings 42, first true say at maker turn 67), ring (meeting … (line cut here; whole in hears.txt)
  X · EXIST by any hand: ON exist 1.000 over 104 citations (with a truth 104) · cited by world {'scene': 104} · maker citations 0 (the by-any-hand road exercised: False) · carry 0.971 null p95 0.606 · OFF exist 1.000 over 104
    the planted control: exist 0.990 over 104 · caught (< 1): True · exactly one citation spoiled ((n−1)/n): True → X PASS
  C · launch (A1.1): start skew 0.0 s · wall OFF 2731 s ON 2732 s · overlap 1.000 (min 0.9) → ok · loadavg OFF 5.35 5.99 6.20 5/1054 490008 → 9.04 8.98 8.70 9/1117 590184 · ON 5.35 5.99 6.20 5/1053 490008 → 9.04 8.98 8.70 7/1107 590193 · PSI cpu OFF some avg10=0.00 avg60=0.16 avg300=0.07 total=346307634|full avg10=0.00 avg60=0.00 avg300=0.00 total=0| → some avg10=0.42 avg60=0.16 avg300=0.08 total=353446180|full avg10 … (line cut here; whole in hears.txt)
  C · COST, the mind's CPU per canvas ON over OFF (the drive law's canvas = its ear + eye rows; bar ≤ 1.5 on EACH population, A1.2) → PASS:
    maker        canvases 472 · timed off 472 (missing 0) on 472 (missing 0) · cpu_ms mean off 210.612 on 223.998 · median off 146.826 on 155.906 · ratio mean 1.064 median 1.062 → PASS
    scene_train  canvases 10000 · timed off 10000 (missing 0) on 10000 (missing 0) · cpu_ms mean off 122.714 on 125.148 · median off 82.492 on 85.340 · ratio mean 1.020 median 1.035 → PASS
    all_rows     rows off 38173 on 38173 · mean cpu_ms off 70.636 on 71.177 · ratio 1.008 → PASS
      the verdict of every population is THE SAME as the barred reading
  I2 · OFF without its turn rows vs the replay under the life's own genome: OFF rows 51039 (turn rows dropped 10000) → compared 41039 vs I1 41039 · first difference None → PASS
  controls (run on THESE inputs): P {"caught": true, "set": "fresh", "mark": "M1", "item": "M1:test:20261402:00001", "before": [0, 1], "after": [0, 2]} · I2 {"caught": true, "planted_changed_the_rows": true}
  BARS: C PASS · X PASS · I2 PASS · controls CAUGHT
```

**What the reading does NOT carry, said plainly:**
- **X was proven as wiring, not as the by-any-hand road.** All 104 of ON's citations are the scene's (`cited by world {'scene': 104}`): the maker was heard but cited by no `why` answer, so «EXIST over a maker memory» was never asked of real data. The plant (one citation spoiled) read exactly (n − 1) / n, which proves the instrument sees a bad citation, nothing about the maker's.
- **P is within noise on every paired mark** (pooled M1 n 389: OFF 0.985 → ON 0.977, smallest passing gap 0.026; M3 n 115; M6 n 56; the sign tests are one-sided, p(ON worse) 0.227 / 0.250 / 0.969). It is a reading, not a bar: no pooled gap clears its own 10 / n in either direction.
- **I1 was not re-run in full by this lane.** My first background replays (10:40) were killed by the harness at its 30-minute limit because I passed no `timeout` (my error, posted on the board at the time). The I1 evidence is the VERIFIER's independent full and lean replays (paths and sha256 in section 2c; verdict lines in their `.log` files). Its strongest form is checkable in that table: the full identity replay's journal and the closed life's own live journal have the same size and the same sha256 (`2d3c6397…`), i.e. they are the same bytes. Beside it, my 400-row runs (`i1/`), which are labelled for what they say and nothing more. The lean brain-internal plant replay (my own extra) was not run.
- **The creature suite was not run by this lane on the final sha.** The organism's CODE (every `.py` under `creature/`, `brain/`, `genome/`) is unchanged between the commit the arms ran under and now (section 2d, `git diff --stat` lines; the only additions under those directories and their tests are two genome data files and the test of them), so the verifier's creature run on 33f68f9 and the integrator's gate on 1fcef73 stand by the integrator's own rule; this lane ran the genome and tools suites (D1, `tests/`).

## 1 · Two readings the bars do not carry (a reading, not a gate; the seat decides)
The architect's wording stands for both: **a bar flipped on a draw the n cannot separate** — never «ON breaks SPEAK2» — and a direction the law predicted, **[Likely] a small real cost, post-hoc, not proven**; A2's verdict copy settles it on the pre-registered split.

**(1) TRUTH-NEED (SPEAK2) is the one grade bar whose pass flag differs between the arms (14 read in each arm).** The reader printed nothing about it until A4.5 (the six tests' verdicts name seven bars). Rebuilt item by item with the grader's own machinery (`diag/diag_truth_need.py`; its control reproduces both arms' rates exactly):

```
CONTROL off: rebuilt TRUTH-NEED n 41 value 0.5609756097560976 · the grade holds n 41 value 0.5609756097560976 → REPRODUCED
CONTROL on: rebuilt TRUTH-NEED n 36 value 0.3888888888888889 · the grade holds n 36 value 0.3888888888888889 → REPRODUCED
items: off 60 on 60 union 60 same ids True
covered in OFF 46 in ON 46 in both 46
{'spoke_both': 36, 'only_off': 5, 'only_on': 0, 'neither': 5}
spoke in both n 36: both true 13 · both false 16 · ON-right only 1 · OFF-right only 6 · smallest passing gap 10/n = 0.278
sign test (ON worse = OFF-right more) p = 0.0625
off spoken covered 41 true 23 length mix {1: 18, 2: 23, 3: 0}
on spoken covered 36 true 14 length mix {1: 22, 2: 14, 3: 0}
reasons not spoken among covered: {'off': {'no sayable word': 4, 'no believed-unique phrase': 1}, 'on': {'no sayable word': 4, 'the read-back': 3, 'no believed-unique phrase': 3}}
```

Read: ON's paired gap on the 36 items both arms spoke is (1 − 6) / 36 = −0.139, **inside the smallest passing gap 10 / 36 = 0.278**; the one-sided sign p is 0.0625. ON speaks shorter phrases (one word 18 → 22, two words 23 → 14). In the six items OFF got right and ON got wrong, ON dropped a word of OFF's phrase in three (`small white` → `white` twice, `big green` → `big`) and named another single colour in three (`green ring` → `white`, `small red` → `yellow`, `big triangle` → `yellow`); the single word «white» is ON's whole phrase in three of the six. [Speculative] «white» is the word both readings of this section touch; nothing here shows a cause. The 5 items OFF spoke alone were refused by ON at the read-back (3) or for no believed-unique phrase (2). Every item row is in `diag/diag_truth_need.out`.

**(2) The architect's A1.5 class split has «white» alone against ON:** M1 pooled `white n 51 (0/4)` and M3 `white n 19 (0/2)` (ON-right / OFF-right) = **0 ON-right, 6 OFF-right**, against `colour_size n 257 (2/1)` and `shape_only n 81 (0/0)` on M1 and `colour_size n 96 (0/0)` on M3 (all in `bench-1/hears.txt`). That is the direction A1.5's route (ii) predicts (y = 0 on «white» for every maker canvas, a white thing named by its shape) after only 472 maker canvases; 6 of 6 is a post-hoc cell of a declared split and 6 / 70 = 0.086 is inside 10 / 70 = 0.143, so it is not proven.

## 2 · Files

### 2a · Committed here (verbatim copies; sha256 of each)

| file (under `docs/organism/hears/records/`) | bytes | sha256 | what it is |
|---|---|---|---|
| `bench-1/GENOME-life.genome` | 12,133 | `df8abcabdc22bc8ad9db933c3a376b075c1a0894fe7df60b9bdaf736d5415628` | the closed life's own genome (brain-full-20261102) |
| `bench-1/GENOME-off.genome` | 12,184 | `7945be5d454cc7cd72f744a8813edb0a9f5991ae3c36db1b4d881a49498dea12` | OFF: the life's genome + one DRIVE line |
| `bench-1/GENOME-on.genome` | 12,190 | `31361946c6cd829993f403932eb5a668c9c07914f4a5dc9c0f199ca9bf60a414` | ON: OFF with `hears scene maker` (one token) |
| `bench-1/arms.exit` | 24 | `31f6be24c7585b0e2c99048e64e890b887eaa22e61610863e40e296e9939da0e` | both arms' exit codes |
| `bench-1/clock.txt` | 738 | `027e5997a7b92ec70aa668f6968b863427c775947b1e82bb1ceef25751c86214` | the read stage's step exit codes, THREE passes in order: 12:09 (grade-on exit 1: the grader crash, hears_read exit 2), 12:14 (after the grader fix, A4), 12:24 (after the reader's flips line, A4.5) |
| `bench-1/grade-off.report.txt` | 4,393 | `e537d63b060ac06758edb9220041180fb5e0996273e5bc010746360588dfd6eb` | the grader's report for OFF (grade.json, 470 KB, is in the external copy) |
| `bench-1/grade-on.report.txt` | 4,421 | `0c105879c796c21731b66df3f07f3f1d972dd183fe76d74e65453b183ca2401d` | the grader's report for ON (grade.json, 470 KB, is in the external copy) |
| `bench-1/grade-xplant.report.txt` | 4,433 | `4b13ae0c3d29c09b98e60f67281a6151aec8d168c60bb760162a96aa8498a349` | the grader's report for XPLANT (grade.json, 470 KB, is in the external copy) |
| `bench-1/hears-before-flips.txt` | 12,554 | `3930f61e89cb115a696fc6bc35b208a146f1270e17ff6d00a368e1969a51dd6d` | the reading of 12:14, before the reader printed bar flips: differs from hears.txt by exactly ONE added line |
| `bench-1/hears.json` | 29,963 | `4c2cd98c0da8bfa2a3212d40ee3eb57e249ca1ab679efeae361f02f69aae22a0` | the same reading, machine-readable (what a verifier re-derives from) |
| `bench-1/hears.txt` | 12,803 | `022fe67ceb27970c0dd4366595a78f0511f3c00f60763da473da37762f54870d` | the reader's whole reading: P, T, G, C, X, I2, the controls and the BARS line (the rerun of 12:24 after A4.5) |
| `bench-1/i2-journal_diff-planted.txt` | 725 | `46371c3763390912aa1c765080dd6a6861bfb6c10e24dbf965a31904de1f673b` | its planted control: one character of a kept row, must read DIFFERENT |
| `bench-1/i2-journal_diff.txt` | 275 | `b0d5d49e789d5c9eafee3f2afc5d938ccc6218d34587a62838aab87b43a12b16` | I2 as the law names it (journal_diff.py: answer and brain rows dropped): IDENTICAL |
| `bench-1/launch.txt` | 222 | `da30a7adba540380a1631c5a47c331a97ff463f06f67fcf855b4557a3ef41e27` | the same-minute launch record (A1.1) |
| `bench-1/logs/grade-off-after-fix.log` | 4,512 | `88a58c79507a69f741ec738dac2895a1fad9569130c722362f7c548541453bbe` | stage log grade-off-after-fix (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/grade-off.log` | 4,492 | `de04b7088a1de751e147859d465c69dcdf23d4d90b02b9e5aeb2bfb91b79fec1` | stage log grade-off (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/grade-on-try.log` | 4,526 | `86db44e460ff076cf5e26b5aeddb1576beb9d2420ba69f70ec81f4337475a62d` | stage log grade-on-try (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/grade-on.log` | 4,518 | `866a18db256e0efb87e6922cbc5992a037ac14db4a42478de63135ae9bd1fad2` | stage log grade-on (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/grade-xplant.log` | 4,538 | `e55d8366ff3a8e3cbd20ee748d6bff6d0b81653788a010debd030d58a2f5860c` | stage log grade-xplant (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/read.log` | 12,803 | `022fe67ceb27970c0dd4366595a78f0511f3c00f60763da473da37762f54870d` | stage log read (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/worlds-on.log` | 7,019 | `17353bd6098bdd4fe43219f573fafe76541a696bfc77ae5c481282ae5bcdf2b5` | stage log worlds-on (the 12:14 read stage's; read.log is byte-identical to hears.txt of that pass) |
| `bench-1/logs/xplant.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | the plant maker's stderr (empty) |
| `bench-1/off.arm` | 477 | `6c5bdd4dbbca44b83f7c78dbe411d55bb13e9108bbc9f031e95bf06050094970` | OFF arm: start/end epoch seconds, loadavg and CPU pressure at both ends, exit |
| `bench-1/off.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | OFF arm's exit code (the replay's own, written by the arm stage) |
| `bench-1/off.log` | 47 | `f04a00ff8bc2a3c58ea1063351a575290c138efaaf18add43aae553a59f2710c` | OFF arm's replay stdout/stderr |
| `bench-1/on.arm` | 476 | `f0e0e759eb1f59ab6347ba29c8efec3eb3d25d5255b408dc4883d29af2a801c8` | ON arm: start/end epoch seconds, loadavg and CPU pressure at both ends, exit |
| `bench-1/on.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | ON arm's exit code (the replay's own, written by the arm stage) |
| `bench-1/on.log` | 46 | `ff93d9f775316b1e70c34a165ad698f5f79f79afd3ab0a6b73321de21e53bfc5` | ON arm's replay stdout/stderr |
| `bench-1/worlds-on.json` | 26,209 | `97294df0f716dab01f919d7b3e64166d70e1262508517405459c37b8365f0b4f` | worlds_read of ON's journal, machine-readable |
| `bench-1/worlds-on.txt` | 7,019 | `17353bd6098bdd4fe43219f573fafe76541a696bfc77ae5c481282ae5bcdf2b5` | worlds_read of ON's journal |
| `bench-1/xplant.json` | 270 | `c4118d155c2f1c04491a4244c9ecfd93dcdfcc6f96542481e4bfc5a6a486e62a` | what the X plant changed (ONE citation's moment, one line) |
| `calibration/fill_calibration_insitu.out` | 3,239 | `57021ca404216c7687c6f8c929fbe96f246241e93d317c55929d9d0c10495b14` | its output |
| `calibration/fill_calibration_insitu.py` | 6,210 | `c8db4fdfc689266061f235be53a5cb3ef36a4eb28953bb53c25908c2c2ed9d92` | fills the in-situ section of CALIBRATION-COST-2026-10-03.md from the arms' timings (every number computed) |
| `d2/d2-real-reread.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | the read's exit code |
| `d2/d2-real-reread.json` | 1,543 | `5f0ee6f07ca679ee8cbedcfc572bb0af9062e585d81f8f3c0a39ac943864c4ef` | the same read: machine-readable |
| `d2/d2-real-reread.log` | 1,647 | `7cfa909381d34105199a001ba49b658e207a6671e68d2038f2ec77354e3d23ff` | the D2 checker (tools/lives/hears_d2_read.py) re-read of the REAL pre-flight life brain-long-3-pre-1 after A3: PASS |
| `diag/diag_truth_need.out` | 2,372 | `e1b3fcc81906b9dbd5139cc4b31fbe21beb0833e0d6f5b9069ba45e03c2c9cd6` | its output; its built-in control reproduces both arms' TRUTH-NEED n and value exactly |
| `diag/diag_truth_need.py` | 4,773 | `39cb6b81d31a47b34608c66a8fc34a90ea765172c1256288e52af059ce29811b` | the TRUTH-NEED pairing diagnosis (one-off, not a gate): rebuilds SPEAK2 item rows with the grader's own machinery |
| `i1/CODE-IDENTITY.txt` | 152 | `d165bb941fbeaca25473ae2f217e00e81a1d93812a3f6ee1a3014f9aaf6a8917` | git shas at the time of my first replay set-up |
| `i1/identity400.exit` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | its exit code |
| `i1/identity400.log` | 43 | `9eea5eb6ae46fe6635f6bb09ff13cc16e2503ec290cc1249002f747a65f8058c` | MY 400-row identity replay: matched every row it wrote (400 rows, last seq 399), then the live journal's next row (seq 403) is missing from the replay because the replay stops at the cut |
| `i1/plant400.exit` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | its exit code |
| `i1/plant400.log` | 26 | `c6040d27e2d1ebfa5a88179cd5ec712f1a8a4805716dbebfd48afa0d94c08672` | MY 400-row DELTA plant replay: diverges at seq 121, field hash |
| `tests/brain_long_3-final.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/brain_long_3-final.log` | 106 | `35649ccb7621214ac024bd31428022d326fb76b6926043ad7d6527b41cd3c0f8` | tests/genome/test_brain_long_3.py (8 tests) |
| `tests/genome-45b7fb9.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/genome-45b7fb9.log` | 6,415 | `8db6dcf90d1d57dac6cb2add6109e3adcff2508fcf2f3b70e8d504e6c0d797c8` | D1 genome suite on 45b7fb9 (detached clean checkout) |
| `tests/grade_foreign-final2.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/grade_foreign-final2.log` | 111 | `893163108e94e85b2a9190459f7181f91a6ed08f8d362839e2a82a75d0f2d8b1` | A4: grader tests on the code-final tree (12 OK) |
| `tests/grade_foreign-red.log` | 7,638 | `193de7925b7b067a4bd83f429bfbd7723068291b72a8682f20805b74ce8d5d6a` | A4: the grader's foreign-word tests RED on the unfixed grader (7 errors) |
| `tests/hears_d2-final3.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/hears_d2-final3.log` | 120 | `c7bfa9984221d5a7e10529b323ae1a7012ffac8a3d795f31b4e3fbd80cf12b64` | D2 checker suite (21 tests) |
| `tests/hears_d2-red.log` | 939 | `da2a16796fcf5f7b32bc163aa2ef8bd5d3d5e89f8ee90dc43a0cece994a51534` | D2 checker: RED |
| `tests/hears_read-final4.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/hears_read-final4.log` | 74,879 | `f574191bfc5ba8c8b0ea3dda35f4fa0ff02843dbc2fa9dfbf3b28f6526e5a2af` | reader suite on the code-final tree: 76 OK |
| `tests/hears_read-flips-red.log` | 14,896 | `d9b19a4070f578a4d974d92149ac3d4e935305ad7bc340b92eac400bda9400da` | A4.5: the 8 new reader tests RED on the reader as it was |
| `tests/hears_read-red.log` | 28,690 | `4ca64ac797236abe17db8105c31a59a8ffaca928a3f8f380bd940b5a1a9ff939` | reader draft: RED (before the reader was rebuilt) |
| `tests/mutation_sweep-flips.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/mutation_sweep-flips.log` | 6,137 | `96ca0072eba4a19805cecfa1ea02b00faaf73b613afb4eebcaad67e21ed8add8` | reader mutation sweep with A4.5: 35 mutants, 35 CAUGHT, no survivor |
| `tests/mutation_sweep.log` | 4,440 | `593b57e9ad1c8073de9652c2da36877dc93ad5eb1a0ab22af683959329c70b08` | reader mutation sweep, the first 25 mutants (all CAUGHT) |
| `tests/mutation_sweep_d2.log` | 3,766 | `e6d92b89d8f2a771492194aadb5c241bab664b84aa32a6d9f94fd5fcc2cb2566` | D2 checker mutation sweep, 18 mutants (all CAUGHT) |
| `tests/scene_arming-0d9970c.log` | 296 | `581849d8b9ed7ac7334c47f0d9f1e576f50d5705f421cc48d9bb158be0da3572` | tests/creature/test_scene_arming.py on 0d9970c (10 OK, the creature leg's own lane test) |
| `tests/tools-45b7fb9.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/tools-45b7fb9.log` | 91,873 | `5dcebcddbac5fd073dd30393c33506f971a8a6316aedfebb9bb6125c9c4903b6` | D1 tools suite on 45b7fb9 |
| `tests/tools-7f91fdf.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `tests/tools-7f91fdf.log` | 91,873 | `4109f2c94e0d6d8328ba69f187771fb55d95ffd9721f733991ee775498b7864a` | D1 tools suite on 7f91fdf (the code-final commit: grader dax pin) |
| `MANIFEST-bench-1.sha256` | 4,081 | `1040d9be64764354f036d2f33a2fcb035b023684029308c3ae39eebe67360583` | `sha256sum -c` list of every regular file of the external copy except `groot/truth/` (below) |

### 2b · The large files: a full copy of the bench directory at `/data/dev/swarm/2026-10-03/hears-records/bench-1/`

`cp -a` of my `scratch/bench-1` taken 2026-10-03 12:37 +0400; its `groot/tape` symlink is re-pointed at the ORIGINAL read-only cut (`/data/dev/brain-runs/organ/rung3/brain-full-20261102/cut/tape`), because my scratch copy of the cut is verified identical to it (`diff -rq`: IDENTICAL, no output; the live journal copy's sha256 equals the original's). `groot/truth/` (11936 files, a copy of the closed life's truth) is covered by ONE combined hash: sha256 of the sorted `<file sha256>  <path>` lines = `52deed5515580f71d96a63859994d6ae2047ed90ecaed96c49d22ce663284506`. Every other regular file is in `MANIFEST-bench-1.sha256`; the ones the reading rests on:

| file (under `…/hears-records/bench-1/`) | bytes | sha256 |
|---|---|---|
| `off/journal.jsonl` | 22,015,687 | `82486f52abd185031753ed892beb4c009fc49de4e57b1e86cb05b586f55875d9` |
| `off/timings.jsonl` | 3,075,765 | `43d2eda4e4a31773b9799e1f8f55475aca8482bdd1ad39cf30349d0b3380622b` |
| `on/journal.jsonl` | 22,441,970 | `14ff8467c5e7d0d047765de3a6013dd3ed8dd28a00f2889bcd7dfd98004e285c` |
| `on/timings.jsonl` | 3,076,125 | `65474c3747659fdb5c67bb7519f90fc9d8d673855c6e1d7d3af0c8e3915c8016` |
| `xplant/journal.jsonl` | 22,441,972 | `eb0ddffb18c7b1f989b16bee7aa009f9150b3eaab536637f76ddbcf022efa67c` |
| `grade-off/grade.json` | 472,750 | `0632997a59eb8667a85a89c9aa68d6b77b1d10f14f201b33a7e6964d58595b1d` |
| `grade-on/grade.json` | 473,189 | `9e266124b59c57d73a4015a1b65e9b2bfa28bcae6785ccde0c2a15996cb1481f` |
| `grade-xplant/grade.json` | 473,270 | `d52f610835ee1cd34cb9ff6583599346d261ba2ccad70b003fab4e438eee9b07` |
| `grade-off-before-fix/grade.json` | 472,750 | `0632997a59eb8667a85a89c9aa68d6b77b1d10f14f201b33a7e6964d58595b1d` |
| `grade-off-after-fix/grade.json` | 472,750 | `0632997a59eb8667a85a89c9aa68d6b77b1d10f14f201b33a7e6964d58595b1d` |
| `grade-on-try/grade.json` | 473,189 | `9e266124b59c57d73a4015a1b65e9b2bfa28bcae6785ccde0c2a15996cb1481f` |
| `read-before-flips.json` | 29,607 | `f3796f274fab217c52977b73bd9815322db213990fe206afa2aacb7c1fafb934` |

### 2c · Inputs by reference (read-only; not copied)

| path | bytes | sha256 | what it is |
|---|---|---|---|
| `/data/dev/swarm/2026-10-03/verify/i1-55ef469/out/journal.jsonl` | 15,978,333 | `2d3c639702c49aba417bcaf81a63c80b0100c4ddb5d8d26cf885fba07feb052b` | the full-life identity replay's journal (the I1 oracle comparison's other side; I2's `--i1-journal`) |
| `/data/dev/swarm/2026-10-03/verify/i1-55ef469/i1.log` | 34 | `b36eb74a983d745a1667a1f08e67aad01b880979aa118a9f59e8bb66aaf07b42` | I1 full identity: the replay's own verdict line |
| `/data/dev/swarm/2026-10-03/verify/i1-55ef469/i1.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `/data/dev/swarm/2026-10-03/verify/i1-55ef469/i1-plant.log` | 26 | `c6040d27e2d1ebfa5a88179cd5ec712f1a8a4805716dbebfd48afa0d94c08672` | I1 DELTA plant on the full life: the replay's verdict line |
| `/data/dev/swarm/2026-10-03/verify/i1-55ef469/i1-plant.exit` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | its exit code |
| `/data/dev/swarm/2026-10-03/verify/i1lean-55ef469/i1lean.log` | 34 | `81efd26da872882ce07accba878cc85f525bb03569a6293f0f35178a84551129` | I1 on the lean life: verdict line |
| `/data/dev/swarm/2026-10-03/verify/i1lean-55ef469/i1lean.exit` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` | its exit code |
| `/data/dev/swarm/2026-10-03/verify/i1lean-55ef469/i1lean-plant.log` | 26 | `042093b08dd5b3faf247f38aac3f217659aa78706104791217b7ce6c95fb8ea6` | lean DELTA plant verdict line |
| `/data/dev/swarm/2026-10-03/verify/i1lean-55ef469/i1lean-plant.exit` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | its exit code |
| `/data/dev/brain-runs/organ/rung3/brain-full-20261102/cut/live-journal.jsonl` | 15,978,333 | `2d3c639702c49aba417bcaf81a63c80b0100c4ddb5d8d26cf885fba07feb052b` | the closed life's live journal (the oracle of every identity replay) |
| `/data/dev/brain-runs/organ/rung3/brain-full-20261102/cut/tape/2026-09-28.jsonl` | 10,890,383 | `a9be8b1e4102ef83dd3aaccf8cf1af3addf9168be60675ac813edd349354ca0e` | the cut tape's day file (the payload directory beside it: see the diff -rq line) |

My copy of the identity journal (`scratch/i1/identity-verifier-journal.jsonl`, the file `I1_JOURNAL` named in the read stage) is byte-identical to the verifier's `out/journal.jsonl` (`cmp`: identical). The real pre-flight life read by D2 is `/data/dev/genome-lives/brain-long-3-pre-1` (the seat's; read-only). The integrator's long gate logs are under `/data/dev/swarm/2026-10-03/int/logs/hears-pre-*` (the integrator's files: reference only, no hash taken because they were still being written).

### 2d · Which code the arms ran, and that the organism has not moved since
The arms were launched 2026-10-03 11:22:06 +0400 from this branch (`hears-2` at `33f68f9` then; the bench pair was started by the `33f68f9` version of `tools/brain/hears_bench.sh`). The organism's CODE (every `.py` under `creature/`, `brain/`, `genome/`) between `55ef469` (the HEARS-2 code) and `33f68f9`: `git diff --stat` → (empty: no .py file of creature/, brain/ or genome/ differs). Between `33f68f9` and the commit before this one: (empty: no .py file of creature/, brain/ or genome/ differs). The only files under `creature/`, `brain/`, `genome/` and the tests of those that changed after `33f68f9` (`git diff --name-status`): A	genome/brain/lives/BRAIN-LONG-3-PREFLIGHT.genome · A	genome/brain/lives/BRAIN-LONG-3.genome · A	tests/genome/test_brain_long_3.py — the two life genomes this lane added (BRAIN-LONG-3 and its pre-flight twin) and their test; no replay of the bench reads them.

The genomes differ by ONE added line and ONE token, asserted by the launcher before any replay:
```
diff GENOME-life GENOME-off :
106a107
> DRIVE    brain turn before hearing; says 1; asks 1
diff GENOME-off GENOME-on :
106c106
< BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene
---
> BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene maker
```

## 3 · How to re-derive the reading
```
cp -a /data/dev/swarm/2026-10-03/hears-records/bench-1 <new dir>
cd <a checkout of hears-2>        # the verifier's own
TAPE=/data/dev/brain-runs/organ/rung3/brain-full-20261102/cut/tape \
I1_JOURNAL=/data/dev/swarm/2026-10-03/verify/i1-55ef469/out/journal.jsonl \
  bash tools/brain/hears_bench.sh read <new dir>
cat <new dir>/read/hears.txt          # must equal bench-1/hears.txt here (the 12:24 pass)
```
The read stage regrades OFF, ON and the X plant, runs `journal_diff.py` and its plant, and runs `hears_read.py`; it reuses `<new dir>/groot` (a symlink to the original cut tape and a copy of the truth). The arms stage (`hears_bench.sh arms <out>`) is not to be re-run: it is 45 minutes of two slots, and the journals and timings it wrote are the copies above.

## 4 · The history of the read stage (nothing is hidden)
`bench-1/clock.txt` holds three passes. **12:09** — OFF graded, ON did not (`grade-on exit 1`): the grader raised `WorldError: not a word of this world: 'arrow'`; the cause is the grader, not the arms (A4.1). **12:14** — after the grader fix (commits 81e7726, 45b7fb9, 7f91fdf): all steps exit 0. **12:24** — after the reader printed every bar whose pass flag differs (A4.5): the reading differs from the 12:14 one by exactly one added line (`hears-before-flips.txt` vs `hears.txt`). The first pass's crash log was overwritten by the second; the crash is reproduced by `tests/grade_foreign-red.log` (7 errors, the same `WorldError` on the unfixed grader).

*(edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 12:37 +0400; every table row above was computed by `scratch/make_records.py` at that time)*
