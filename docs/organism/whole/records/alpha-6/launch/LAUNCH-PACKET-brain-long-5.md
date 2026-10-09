# LAUNCH PACKET — brain-long-5 (the organism ALPHA 6's first life; PREREG-ALPHA-6 + AMENDMENT 1)

*Written by Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400, on the branch `alpha-6`. The law:
`docs/organism/whole/PREREG-ALPHA-6.md` (SEAT-LINE sha256 1d00a35f…) + AMENDMENT 1 (26640c8c…). The launch is the
SEAT's act, only when §5's gates are green on the LAUNCH sha AND the amendment's prerequisite chain stands:
(a) the ear's cover law PASS (PREREG-EAR-COVER-CAP — its verdict), (b) the shelf content lawful (V3's bench tapes,
never re-litigated), (c) this law's own gates. NOTHING here is run by the builder beyond the pre-flights (the law
§2 B5's own delegation).*

## 0 · What this life is (the ladder, RULES §3)

`brain-long-5` = brain-long-4's launched genome with EXACTLY the law's §1 diff (every other byte identical —
`genome/brain/lives/BRAIN-LONG-5.genome`, the diff printed in the builder's report):

1. `SEED 20261201` and the scene world's seed 20261201 (the two together, the standing rule).
2. `+ WORLD    video shelf /data/dev/genome-lives/brain-long-5/world/video-shelf every 2 s; loop; manifest sha256` —
   the open world's curriculum tapes (V3's bench set, promoted to the frozen shelf) as the life's own rows.
3. `MOUTH` gains `; incremental` — the brain's say paths select `produce_incremental` (VERDICT-MOUTH-INCREMENTAL's
   mechanism) when and only when the clause declares it.
4. `BRAIN … hears scene maker video` (the hears list gains exactly `video`; HEARS-2's derived index/seed).
5. The front wired at launch: the launch command carries `--eye-front` (creature/body.py's opt-in pass-through;
   absent = byte-identical).

## 1 · Pre-conditions, each with its evidence (the builder's report carries the real outputs)

| gate | evidence |
|---|---|
| G-SUITES | the five suites on the branch sha through slot (the creature split's partition-exact runner at 10G; tools/genome/brain/scene at 4G) — logs + exits under `scratch/a6/suites/` |
| G-IDENTITY | the 500-row bl2 segment (the standard copy, never touched) replayed under pre-window master vs the branch, no clause: byte-identical journals (sha256s printed); the front-absent and mouth-undeclared forms byte-identical (the suites' own pins + the replay) |
| G-SCENE-FRONT | the same segment replayed WIRED (`--eye-front`): births > 0 with presence counts; the learning measures printed beside the unwired replay's (`scratch/a6/gscene-front/`) |
| G-PREFLIGHT | the two pre-flight lives (below) |
| G-PLANT | the mouth parser's garbage refused by name; the tampered shelf CAUGHT; the sense's manifest discipline (tests/creature/test_sense_video.py + tests/tools/test_video_shelf.py + tests/genome/test_parse_mouth_incremental.py) |
| the pinned window | machinery.py's two branches' redraw into the FRESH root `/data/dev/brain-runs/scene-organ-alpha6`: caches compared N · differing 0, the planted bit CAUGHT (the window's own log) |
| the cover law (AMENDMENT 1's (a)) | PREREG-EAR-COVER-CAP's verdict PASS — **the seat names its sha here at integration** |

## 2 · The commands (the seat, in this order)

0. **The shelf** (the law's frozen content, promoted BEFORE the launch; the tool is the build's own):
   `cd /data/dev/genome && python3 -m tools.worlds.video_shelf promote --src docs/organism/whole/records/open-world-4/bench/tape-curriculum --shelf /data/dev/genome-lives/brain-long-5/world/video-shelf`
   — the bench dir is READ in place, never moved; the tool refuses a non-empty target. Then
   `python3 -m tools.worlds.video_shelf verify --shelf /data/dev/genome-lives/brain-long-5/world/video-shelf`
   must print `VERIFY OK`. NOTE: launch_brain.sh (step 1) refuses a root that exists — so the shelf's parent
   `/data/dev/genome-lives/brain-long-5/` must NOT exist when step 1 runs: promote FIRST to a staging path
   (`/data/dev/genome-lives/_brain-long-5-shelf/`), and move it into place (`mv` to
   `/data/dev/genome-lives/brain-long-5/world/video-shelf`) AFTER step 1 creates the root and BEFORE step 4's
   first start — the manifest's paths are relative, so the move changes nothing. (The pre-flights rehearse this
   exact sequence with the toy shelf.)
1. **Launch** from the repo whose master carries the integration (`launch_brain.sh` resolves the source repo from
   the script's own path):
   `cd /data/dev/genome && tools/lives/launch_long.sh brain-long-5 <LAUNCH_SHA> genome/brain/lives/BRAIN-LONG-5.genome "--folder /data/dev/genome/world --plant-after 15000 --eye-front"`
   — brain-long-4's own body args + `--eye-front` (the front wired; the law §1.5).
2. Confirm the fence (`MemoryHigh=16G MemoryMax=20G` on the unit's show line — launch_long.sh prints it) and the
   three timers (`systemctl --user list-timers | grep brain-long-5`: g5-watch, series, health).
3. **The resit timer needs its drop-in BEFORE it is enabled**: install this directory's
   `creature-brain-resit@brain-long-5.service.d-origin.conf` as
   `~/.config/systemd/user/creature-brain-resit@brain-long-5.service.d/origin.conf` with `<LAUNCH_SHA>` written
   (the grader checkout `/data/dev/brain-runs/resit/grader-<LAUNCH_SHA>` prepared first — the resit lane's/seat's
   act, as bl4's), verify with `systemctl --user cat`, then
   `systemctl --user enable --now creature-brain-resit@brain-long-5.timer`. **If the drop-in is not written, do
   not enable the timer** (it would grade against the wrong origin); the life does not need it to live.
4. **The origin-fallback copy job** (HEARS-2 A2.3 (c)): install this directory's `bl5-origin-fallback.service` and
   `bl5-origin-fallback.timer` to `~/.config/systemd/user/`, then `systemctl --user daemon-reload &&
   systemctl --user enable --now bl5-origin-fallback.timer`. It exits quietly until the scene world ends, then
   copies the life's state/prev generation READ-ONLY into
   `/data/dev/brain-runs/alpha-6/brain-long-5-origin-fallback/` and writes DONE.

## 3 · What the first 20 minutes must show (M-LAUNCH's list; read-only reads of the new root)

Root `/data/dev/genome-lives/brain-long-5`.
- `systemctl --user is-active creature-brain@brain-long-5.service` = active; `STATUS.json`: `crash` null;
  `moments`/`last_seq` rising between two reads a minute apart; `hash_form` `sparse`; `brain.learned` rising;
  `brain.restored` None at birth; `mind_backlog_rows` small.
- **THE TAPE FLOWING (M-WORLD):** tape rows with `meta.source == "video"` (eye) and `"video-caption"` (ear)
  present from the first minutes, each eye row's payload the shelf's own PNG; the `video` meta on every such row;
  STATUS's `video` key: `published_canvases` rising, `loop` 0 (the shelf's first pass is ~4 h at 2 s × 7,135
  rows; the wrap is NOT due in the first 20 minutes — a `video_loop` journal row before then is a defect).
- **THE FRONT (M-FRONT):** the journal's canvas rows carry `front` (`t_mass`, `o`) on 100% of them — the video
  eye rows AND the scene/maker rows alike (ONE retina for all the life's light).
- **THE MOUTH (M-MOUTH):** once the brain is calibrated and speaks, the sitting/turn say paths' rows are the
  incremental mechanism's own (the `n_readbacks`/`n_say` keys on the answered say rows' `raw`; never the old
  enumeration's absence of them) — printed with presence counts.
- The scene world's own stream unchanged in shape (its rows carry no `world` key; the maker's learn rows carry
  `world: "maker"`; the video hand's learn rows carry `world: "video"` and the derived index/seed — HEARS-2's
  form).
- The fence and the timers (§2.2) and the fallback copy (§2.4) all armed.
- The window-reset caveat from bl3's packet stands verbatim: every body start sends the maker back to window 0.

## 4 · The memory budget

brain-long-4's own fence (MemoryHigh=16G / MemoryMax=20G, launch_long.sh's own bytes — this directory's
`creature-brain@brain-long-5.service.d-fence.conf` is their record). The box's arithmetic at launch: the ON
replay 12G until ~10-10 + the life growing from ~1 GB + the baseline — deep inside 30 GB (the law §6). The
video sense's own price: the shelf's rows stream at 2 s a canvas, the payloads re-hashed against the manifest as
they go out (~30 MB of PNGs a pass, seconds of hashing — the law's declared discipline).

## 5 · The stop rules (the law §6, verbatim for this life)

S1 a gate fails → VOID, no launch. S2 a pre-flight's RSS > its 4G fence → STOP, named. S3 the life's first-hour
RSS growth past the fence's line → the health watch pages (the standing form). Closing the life is HIS word again.
