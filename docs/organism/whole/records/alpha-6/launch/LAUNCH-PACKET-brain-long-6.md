# LAUNCH PACKET — brain-long-6 (the registers' first body; PREREG-BRAIN-LONG-6)

*Written by Kimi Code (K3, kimi-code, the seat alone), 2026-10-11 20:2x +0400, on the branch `bl6-1011`. The law:
`docs/organism/whole/PREREG-BRAIN-LONG-6.md` (SIGNED; SEAT-LINE sha256 2c6bb22b…; the verifier loop
`verify/BL6-VERIFIER-READ.md`). The launch is the SEAT's act, only when §5's gates are green on the LAUNCH sha.
brain-long-5 stays alive until the launch reads PASS; its close is HIS word at that wall.*

## 0 · What this life is (the ladder, RULES §3)

`brain-long-6` = brain-long-5's launched genome with EXACTLY the law's §1 diff (`genome/brain/lives/BRAIN-LONG-6.genome`,
the diff printed in the law and re-printed here):

1. `SEED 20261211` and the scene world's seed `20261211` (the two together, the standing rule).
2. `WORLD scene seed 20261211` lawful — `brain/scene/world.py`'s maps gained the seed and its three splits
   (s1b1 20261321 · fresh 20261521 · held 20261621 — all verified NEVER used anywhere before the law; the
   check: `grep -rn '20261321|20261521|20261621' brain/ genome/ creature/ tests/ tools/` → empty, printed in
   the build record).
3. `+ REGISTERS content-web muse precision` (after the FILE line) — the three verdicted registers armed;
   the parser's ONE pinned-window branch (machinery.py) + the Mind's tri-state self-wiring (creature/mind.py);
   absent = byte-identical.
4. `WORLD video shelf /data/dev/genome-lives/brain-long-6/world/video-shelf every 2 s; loop; manifest sha256` —
   the SAME frozen content as brain-long-5's shelf, promoted to this life's own dir (7,136 files, VERIFY OK,
   manifest sha256 8d0960c6… — the staging path `/data/dev/genome-lives/_brain-long-6-shelf/` moves into
   place per §2 below).
5. Everything else byte-identical to brain-long-5's launched genome (MOUTH `incremental`, `hears scene
   maker video`, the calibration list whole, the doors, DRIVE, EVOLVE, the STAGEs, HASH sparse).
6. **trajectory stays OFF** (N2 verdicted FAIL-FORM — named in the law §0/§7; the parser refuses the word).

## 1 · Pre-conditions, each with its evidence

| gate | evidence |
|---|---|
| G-SUITES | the five suites on the launch sha through slot (the creature split's partition-exact runner at 10G; tools/genome/brain/scene at 4G) — logs + exits under `scratch/bl6/suites/` |
| G-IDENTITY | the 500-row bl2 segment + the 200-moment toy tape replayed under pre-window master vs the branch, no REGISTERS line: byte-identical journals — the journals of record a7280723… and 26dc80c6… REPRODUCED (cmp exit 0 ×2; `scratch/bl6/id/`) |
| G-CACHE-IDENTITY | the pinned window's redraw into the fresh run root `/data/dev/brain-runs/scene-organ-bl6`: every cache of the unchanged world seeds (20261101/02/03) array-identical to the pre-window root's (`tools/brain/diag/cache_identity.py`); the 20261211 splits drawn there (the window's own log) |
| G-SCENE-SEED | `plan()` at 20261211 returns moments (no refusal — tests/brain/scene/test_world_seed_bl6.py); the pre-flight's scene rows publish with restarts == 0 |
| G-REGISTERS-LIVE | a replay of a REGISTERS-declaring toy genome runs the registers: web/journal carry the content-web tokens (w:/s:/g:), the muse budget rows, the precision weight stream — presence counts; the OFF twin byte-identical (`scratch/bl6/registers-live/`) |
| G-PREFLIGHT | the two pre-flight lives (§2's note) |
| G-PLANT | the REGISTERS parser refuses garbage by name (tests/genome/test_parse_registers.py); the tampered shelf CAUGHT (the shelf tool's verify); the tampered declared-word list caught (tests/creature/test_mind_registers_wiring.py) |
| the sisu contamination check | DONE 2026-10-12 00:3x: `grep -ri 'sisu' <shelf> <curriculum>` EMPTY, but the LEXICON carries «mipplo»
   (senses, 1 row) — a contamination path through the ask/answer door. **THE DECLARED FALLBACK, per the law's
   verifier V3: the M-CHAT word is «mipplo»** — verified ABSENT in the video shelf, the read curriculum, AND
   the lexicon (the three checks printed in the gate record). Never silently swapped: this note IS the swap's
   record. |

## 2 · The commands (the seat, in this order)

0. **The shelf** is already promoted + verified at the staging path `/data/dev/genome-lives/_brain-long-6-shelf/`
   (7,136 files, VERIFY OK). NOTE the bl5 packet's own rule: `launch_long.sh` (step 1) refuses a root that
   exists — so `/data/dev/genome-lives/brain-long-6/` must NOT exist when step 1 runs; the staging dir moves
   into place (`mv /data/dev/genome-lives/_brain-long-6-shelf /data/dev/genome-lives/brain-long-6/world/video-shelf`
   with the `world/` parent made) AFTER step 1 creates the root and BEFORE step 4's first start — the
   manifest's paths are relative, so the move changes nothing. (The pre-flights rehearse this exact
   sequence with the toy shelf.)
1. **Launch** from the repo whose master carries the integration:
   `cd /data/dev/genome && tools/lives/launch_long.sh brain-long-6 <LAUNCH_SHA> genome/brain/lives/BRAIN-LONG-6.genome "--folder /data/dev/genome/world --plant-after 15000 --eye-front"`
   — brain-long-5's own body args (the front wired, the law §1's carried form).
2. Confirm the fence (`MemoryHigh=16G MemoryMax=20G` on the unit's show line) and the timers
   (`systemctl --user list-timers | grep brain-long-6`: g5-watch, series, health).
3. **The resit timer needs its drop-in BEFORE it is enabled**: install this directory's
   `creature-brain-resit@brain-long-6.service.d-origin.conf` as
   `~/.config/systemd/user/creature-brain-resit@brain-long-6.service.d/origin.conf` with `<LAUNCH_SHA>`
   written (the grader checkout `/data/dev/brain-runs/resit/grader-<LAUNCH_SHA>` prepared first; **items-root
   brain-long-5 per the ladder**), verify with `systemctl --user cat`, then
   `systemctl --user enable --now creature-brain-resit@brain-long-6.timer`. **If the drop-in is not written,
   do not enable the timer** (it would grade against the wrong origin); the life does not need it to live.
4. The first start + the first-20-minutes list (M-LAUNCH): the unit active, the tape flowing, the fence,
   the timers enabled, the origin-fallback copy running; **ramguard's heartbeat read state=OK first**.
5. **M-REGISTERS' exact reads** (the law's V13/V15 forms):
   (a) content web — `python3 -c` over `state/web.json`: count nodes by prefix (w:/s:/g:); the OFF witness
   = brain-long-5's archived `state/web.json` (s:/g: absent there);
   (b) the muse — the journal's muse rows (chain/budget/skip) once 26+ sentences heard;
   (c) precision — **the replay form** (no direct live surface exists; measured before signing): the
   life's first tape segment replayed under the launch sha with the declared genome (ON) vs an OFF twin
   (the same genome minus the line), the modulate scale streams compared and the weight stream printed.
6. **M-CHAT's teaching act**: the declared chat-only word «mipplo» (contamination check §1 green), taught
   through the chat door in the arc's form («sisu is happy», in/016.json); the read at the FIRST sleep
   boundary after the teaching inside the 24-h wall: `w:mipplo` a node with edge count > 0; the s:-node
   share of the web's cap printed.

## 3 · brain-long-5's close (HIS word at the launch wall)

When M-LAUNCH + the marks read PASS: present the readings; brain-long-5's close is HIS word (the standing
rule — `tools/lives/close_long.sh brain-long-5` disables the life and its timers; bl6's resit then grades
items-root brain-long-5 per the ladder).
