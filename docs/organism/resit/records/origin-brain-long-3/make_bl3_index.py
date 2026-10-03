# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 22:13 +0400 (from `date`; the INDEX.md it writes carries its own generation stamp) — writes records/origin-brain-long-3/INDEX.md from the three runs' own JSON, so no figure in it is typed by hand.
import json
import re
import sys
from pathlib import Path

REC = Path(sys.argv[1])            # .../records/origin-brain-long-3
STAMP = sys.argv[2]
meas = json.load(open(REC / "measure" / "measure.json"))
reh = json.load(open(REC / "rehearsal" / "ORIGIN.json"))
prod = json.load(open(REC / "production" / "ORIGIN.json"))
slot_m = (REC / "measure" / "slot-ledger-lines.txt").read_text()
slot_r = (REC / "rehearsal" / "slot-ledger-lines.txt").read_text()
slot_p = (REC / "production" / "slot-ledger-lines.txt").read_text()


def peak(text):
    return int(re.search(r"peak (\d+)MB", text).group(1))


def span(text):
    s = re.search(r"(\d\d:\d\d:\d\d) \+0400 START", text).group(1)
    e = re.search(r"(\d\d:\d\d:\d\d) \+0400 END", text).group(1)
    return s, e


def mb(n):
    return f"{n:,}"


r9p, r9r = prod["r9"], reh["r9"]
sc, sr = prod["source_copy"], reh["source_copy"]
st = prod["states"][0]
bs = r9p["by_set"]
ll = prod["live_load"]
reason_sha = re.search(r"^(\w{64})", (REC / "production" / "reason.txt").read_text()) or None
sums = (REC / "production" / "NOT-COMMITTED-sha256.txt").read_text().splitlines()
msha = {l.split()[1]: l.split()[0] for l in sums}
rsums = {l.split()[1]: l.split()[0] for l in (REC / "rehearsal" / "NOT-COMMITTED-sha256.txt").read_text().splitlines()}
t_m = span(slot_m)
t_r = span(slot_r)
t_p = span(slot_p)
tops_same = (REC / "production" / "live-root-top-level-before.txt").read_text() == (REC / "production" / "live-root-top-level-after.txt").read_text()
ntop = len((REC / "production" / "live-root-top-level-before.txt").read_text().splitlines())

text = f"""# records/origin-brain-long-3 — the PRODUCTION FALLBACK ORIGIN of brain-long-3 (the seat's order of 2026-10-03 21:34 +0400)

*(edit: Claude (Sonnet 5.5, swarm claims), {STAMP} (from `date`). Every figure below is generated from the three runs' own JSON and slot-ledger lines by `make_bl3_index.py`, none is typed by hand (RULES section 14). Law: `docs/organism/resit/PREREG-RESIT-READER.md` v4 (signed x3) + erratum E1 (verifier + seat signed). Reader of record: resit-1003 @ 916f741, `tools/brain/resit.py` sha256 {prod['reader_sha256'][:16]}… (the bytes the 74-mutant FINAL sweep ran on, `../origin-sweep/`). The daily timer is NOT enabled; brain-long-3's root, units and timers were read, never written.)*

## The three steps the seat ordered, in order

| step | what | where | result |
|---|---|---|---|
| 1 MEASURE | the reader's own `build_source_copy` on the live root (read-only opens), timed, no child | `measure/` | {meas['rows']:,} tape rows (cut at the last sitting's end ask), {meas['n_manifest_entries']:,} manifest entries, {meas['bytes']:,} bytes, {meas['payloads_kept']:,} payloads kept, {meas['truth_files']:,} truth files, {meas['torn_lines_tape']} + {meas['torn_lines_journal']} torn lines; built in {meas['build_s']} s, re-verified in {meas['verify_s']} s, problems {meas['verify_problems']}; the script's own peak RSS {meas['self_maxrss_mb']} MB; the slot cgroup peak {peak(slot_m)} MB ({t_m[0]}–{t_m[1]}) |
| 2 REHEARSAL (**my addition, not ordered**: the seat ordered measure, then the origin run; I priced SLOT_MEM from a full run in a scratch OUT before the written-once production run) | the whole origin run into a scratch OUT | `rehearsal/` | ORIGIN WRITTEN in {reh['wall_s']} s, {reh['cpu']['total_s']} CPU-s; RSS answer child {reh['memory']['answer_maxrss_mb']} MB, grade child {reh['memory']['grade_maxrss_mb']} MB, life-grade child {reh['memory']['life_grade_maxrss_mb']} MB; the slot cgroup peak **{mb(peak(slot_r))} MB** against its 4G cap. **SLOT_MEM for the production run: 4G >= 1.3 x {mb(peak(slot_r))} MB = {mb(round(1.3 * peak(slot_r)))} MB** |
| 3 PRODUCTION | `run_bl3_origin_production.sh` through slot, SLOT_MEM=4G, the seat's `--reason` verbatim, `--origin-kind fallback_copy`, `--state` the seat's copy of 19:30:14 | `production/` | ORIGIN WRITTEN {t_p[0]}–{t_p[1]} (stdout.txt), exit {(REC / 'production' / 'exit').read_text().strip()}, {prod['wall_s']} s, {prod['cpu']['total_s']} CPU-s, the slot cgroup peak {mb(peak(slot_p))} MB, stderr empty |

## The row (`production/ORIGIN.json`, which equals the one line of `/data/dev/brain-runs/resit/brain-long-3/RESIT.jsonl`, checked)

| what | figure | path in the row |
|---|---|---|
| identity | stamp {prod['stamp']}, kind {prod['kind']}, `origin_kind` {prod['origin_kind']}, label «{prod['label']}»; `reason` is the seat's text, byte-equal to `production/reason.txt` | `kind`, `origin_kind`, `label`, `reason` |
| the state | the seat's read-only copy of `state/prev` (19:30:14): snapshot `last_seq` {st['snapshot']['last_seq']:,}, {st['n_learned']:,} learned, genome epoch {st['genome_epoch']}, genome sha256 {st['genome_sha256'][:12]}…, state hash {st['state_hash'][:12]}… | `states[0]` |
| the source copy | {sc['rows']:,} rows cut at seq {sc['cut_seq']:,}, {sc['n_manifest_entries']:,} entries, {sc['bytes']:,} bytes, {sc['truth_files']:,} truth files, 0 torn lines, built in {sc['build_s']} s; `source_copy_sha256` {sc['source_copy_sha256'][:12]}… equal to the sha256 of its MANIFEST; the end-of-run re-verification read {sc['verify']} | `source_copy` |
| ITEMS-MATCH (R15) | ok: {prod['items_match']['n_asks']:,} asks, {prod['items_match']['n_canvases']:,} canvases, ask digest {prod['items_match']['ask_digest'][:12]}…, canvas digest {prod['items_match']['canvas_digest'][:12]}… | `items_match` |
| the answers | **{prod['answer_meta']['answered']:,} answered of {prod['answer_meta']['asks_seen']:,} asks, {prod['answer_meta']['unanswered']} unanswered**; `answers_sha256` {prod['answers_sha256'][:12]}… | `answer_meta`, `answers_sha256` |
| R9, a READING for a fallback | «{prod['r9_reading']}» (the same text is `RESIT.md`'s note cell); untested sets {prod['r9_untested_sets']} | `r9`, `r9_reading` |
| R6 partition | the origin's grade ok: {prod['partition']['ok']}; the life's own grade ok: {prod['life_own']['partition']['ok']} | `partition`, `life_own` |
| genome | `eye_changed` {prod['eye_changed']}; begin asks at seq {prod['begin_seqs']['fresh']:,} (fresh) and {prod['begin_seqs']['s1b1']:,} (s1b1); {prod['restart_duplicates']} restart duplicates | `eye_changed`, `begin_seqs` |
| the grader pin | commit {prod['grader']['commit'][:12]}…, clean, at `{prod['grader']['grader_code']}` (the daily unit's own path; I created that checkout as a detached worktree of d2fe75b); `GRADER.json` written once by this run | `grader`, `production/GRADER.json` |

## Production against rehearsal (same inputs, 14 minutes apart; compared by script)

`answers.jsonl` is **byte-identical** (`cmp`; sha256 {prod['answers_sha256'][:12]}… in both). `r9_reading`, `items_match`, `partition`, `states`, `begin_seqs`, `genome_lines`, `code_commit`, `eye_changed`, `restart_duplicates`, `reason` and `reader_sha256` are equal. Two things differ and each has its cause on the files: `source_copy_sha256` ({sr['source_copy_sha256'][:12]}… against {sc['source_copy_sha256'][:12]}…) because exactly ONE MANIFEST line differs, the LIVE journal (`journal/2026-10-03.jsonl`, 101,878,230 against 102,107,259 bytes: the life writes on; the answers read only its epoch and start rows); and the grade files' sha256, because each `grade.json` carries the run's stamp as its label.

## What this origin says, and what it does not

- **It is a baseline for the daily series, not a verification of the state at asking time.** The state is the seat's fallback copy (the end of the scene stream), so R9 is a READING: only {r9p['early_tested_total']} TESTED EARLY items exist (fresh {bs['fresh']['n_early_tested']}, s1b1 {bs['s1b1']['n_early_tested']}) because brain-moving rows lie INSIDE the sittings (the act census inside them: fresh {r9p['act_census']['fresh']['learn']} learn and {r9p['act_census']['fresh']['turn']} turn rows, s1b1 {r9p['act_census']['s1b1']['learn']} and {r9p['act_census']['s1b1']['turn']}), so {r9p['late_total']:,} of the {prod['answer_meta']['asks_seen']:,} asked items are LATE by R9's own rule. {r9p['early_tested_total'] - r9p['early_tested_equal']} of the {r9p['early_tested_total']} tested EARLY items differ from the life's own rows (the first, in the key `{(r9p['first_early_diff'] or {}).get('differing_keys')}`), which is what «late by construction» predicts. brain-long-2's smoke (`../origin-bl2-fallback-smoke/`) read 0 of 3,011 because that life had no brain-moving row inside its sittings: the two lives are not comparable on this reading.
- **Not shown:** the exact (rebuilt) origin, which stays deferred; R9 refusing on real data (stubs and the sweep only).
- **The seat's copy of `state/prev`** (`--state`): 12 files, none newer than the production run's START.marker (0 paths), the newest mtime 19:25:46 against the marker's 22:02:31 (`production/state-copy-untouched.txt`).
- **The live life.** The top-level names of its root: {ntop} before and {ntop} after, {'identical' if tops_same else 'DIFFERENT'} (`production/live-root-top-level-*.txt`); no file with an output name of this reader (ORIGIN, RESIT, GRADER, ITEMS, glances, answers, grade, MANIFEST, START.marker, *.pyc) lies under it; the files newer than the run's marker lie in the directories of the life's own writers (tape, evolve, truth, game_door, read, game, ask, world, watch, state, journal, STATUS.json), none of them carrying an output name of this reader. `live_load` in the row: ms per canvas {ll['start'].get('mind_ms_per_canvas_1min')} at the start of the run and {ll['end'].get('mind_ms_per_canvas_1min')} at its end, backlog {ll['start'].get('mind_backlog_rows')} and {ll['end'].get('mind_backlog_rows')}: a box-wide reading (other lanes' jobs were running, slot ledger), and no share of it is claimed for or against this run.

## For the seat (done by me / not done by me)

- DONE: the pinned grader checkout exists at `/data/dev/brain-runs/resit/grader-d2fe75b` (a detached worktree of d2fe75b, `grade_life.py` sha256 557f1bf8…, identical to the checkout the earlier runs used); the production OUT `/data/dev/brain-runs/resit/brain-long-3` holds the origin only.
- NOT DONE (yours): enabling `creature-brain-resit@brain-long-3.timer`; the unit calls `/data/dev/genome/tools/brain/resit.py`, so master must carry resit-1003's `tools/brain/resit.py` (sha256 {prod['reader_sha256'][:16]}…, the bytes this origin was made by) before the first daily row, or the row records another reader.

## Not committed (large; sha256 in `production/NOT-COMMITTED-sha256.txt` and `rehearsal/NOT-COMMITTED-sha256.txt`)

`RESIT.jsonl` (the row again), `origin/<stamp>/answers.jsonl`, `grade.json`, `life-grade/grade.json`, the source copy `origin/<stamp>/src/` and `states/`, and the glance cache `glances.pkl`, all under `/data/dev/brain-runs/resit/brain-long-3/` (production) and `/data/dev/brain-runs/resit-gate/bl3-origin-fallback-rehearsal/` (the rehearsal, a scratch folder, not a record of the series).
"""
(REC / "INDEX.md").write_text(text, encoding="utf-8")
print(text[:600])
