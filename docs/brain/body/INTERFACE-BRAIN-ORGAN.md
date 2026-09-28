# THE BRAIN ORGAN — the builders' contract (BRAIN-IN-BODY)

*Written by Claude (Fable 5.1, the seat), 2026-09-28 20:13 +0400. His order (2026-09-28 19:56 +04, verbatim): «The brain full build continues and should get finished today. Check all the research and documentations, and tests and experiments and find the failing parts and fix them and test the whole brain as one and then test it in a single organism body and test the full organism as one.»*

This file fixes the SEAMS so three builders can work at once. The bars and the nulls are law in `PREREG-BRAIN-IN-BODY.md` (same folder). A clause here that cannot be implemented is RAISED to the seat, never worked around.

## 0 · Laws
1. **One organ, beside MEET.** The brain is a NEW consumer of the eye's glances and the ear's words. It replaces nothing. With no `BRAIN` line the mind is byte-identical to today (every pin, every replay).
2. **Rung 1 is the brain AS IT SCORED** (S1b-1R's A-RW-R, the LAW road; T-MEM-2's «none» hook as a read-only health row). No new learning rule tonight: not the mixture likelihood, not `context.py` (refuted), not a growing network.
3. **Replay identity.** Every generator is `brain.world.seeds.substream(seed, tag)` with seed and tag taken from the tape row or the genome. No `default_rng()`, no clock, no `hash()`, no set or dict order in anything journaled.
4. **Truth fence.** The brain and the mind never read `root/truth/`. Only the grader does.
5. **An ask never teaches.** A canvas that carries asks is never learned from by the brain.
6. **Python:** `/usr/bin/python3`, numpy + scipy + PIL only. No torch in the body.
7. **Stamps** come from `date "+%Y-%m-%d %H:%M %z"` every time, never typed or incremented. Every edited file carries `# edit: <name>, <stamp> — <what>`.

## 1 · The genome lines (already parsed on `brain-organ`; pinned by `tests/genome/test_parse_brain.py`)
```
BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene
WORLD    scene seed 20261101; train 10000; sitting fresh s1b1; feed max backlog 8; utterance true
```
- `declared["BRAIN"]` = `{lr, eps, none_level, conformal, young, calibrate_at: [int…], replay: "none"|"uniform"|"strong", hears: [source…]}`. Every value is READ by `genome/brain.py` (no VALUE-UNREAD).
- `declared["WORLD_SCENE"]` = `{seed, train, sitting: [set…] (empty = none), feed: {mode: "max", backlog: k} | {mode: "every", ms: n}, utterance: "true" | {shuffled: k}}`.
- `creature/genes.py` RUNS: builder C adds `"BRAIN"` (mind layer), builder B adds `"WORLD_SCENE"` (body layer), each naming its real call site.

## 2 · The tape rows of the scene world (builder B writes them; builder C reads them)
World code: `brain/scene/world.py` (W), unchanged. `ws` = the world seed. Every row of a moment precedes its eye row (G4 §2.2).

**A training scene** `i` (0-based; `W.train_scene(ws, i)`), moment `sc<ws>t<i:06d>`:
| # | sense | payload | meta |
|---|---|---|---|
| 1…k | `ear` | the word, utf-8, ext `txt` | `{moment, source: "scene", word, scene: i}` — one row per word of the utterance, in the parent's order |
| k+1 | `eye` | the PNG of `W.render_scene(scene)[0]` | `{moment, source: "scene", kind: "train", scene: i, world_seed: ws}` |

Truth file `root/truth/scene/<eye seq, 9 digits>.json`: `{kind: "train", scene: i, world_seed, scene_dict: scene.to_dict(), said: [the words actually published]}`.
Under `utterance shuffled k` the words published with canvas `i` are the utterance of scene `π(i)`, `π = brain.scene.run.null_perm(ws, k, train)`; the canvas and the truth's `scene_dict` stay scene `i`'s.

**A sitting** (after the whole train stream; one per set in `sitting`, in the declared order). Test seed `ts = W.TEST_SETS[set][ws]`.
- `ask` row, canvas-less, form `begin`: payload JSON `{form: "begin", set, test_seed: ts}`; meta `{moment: "sc<ws>q-<set>-begin", source: "scene", form: "begin"}`.
- Then, per split and per scene row `r` that has ≥ 1 question: moment `sc<ws>q-<set>-<split>-<r:04d>`:
  - one `ask` row per question on this canvas: payload JSON `{item, mark, form, phrase: [...], box: [top, left, side] | null, word: str | null, test_seed: ts}`, ext `json`; meta `{moment, source: "scene", item, form}`;
  - the `eye` row: meta `{moment, source: "scene", kind: "sitting", set, split, row: r}`;
  - the truth file: `{kind: "sitting", set, split, row: r, scene_dict, items: [the grader's keys for each item]}`.
- `why` asks are canvas-less: `{form: "why", item, mark: "M4", word}`; one per word the parent ever said in training, published after the splits.
- `ask` row form `end`, canvas-less. After it the sense publishes nothing more and waits for the stop event.

**Forms.** `box` is the parent's POINTING GESTURE at one thing (its picture box in pixels). It is part of the ask, not truth: a parent who asks «what is this?» points.
| form | marks | asks | the answer (journaled) |
|---|---|---|---|
| `point` | M1, M2a, M3, M6, M5 | `phrase` | `{kind: "thing", hyp, pos: [y, x], fix: [[y, x]…]}` · `{kind: "none"}` · `{kind: "misuse", words: [a, b]}` · `{kind: "unheard", words}` |
| `what` | M2b, NAME | `box` | `{kind: "words", words: […]}` · `{kind: "unknown"}` · `{kind: "unseen"}` (no fixation of mine fell in the box) |
| `say` | SPEAK, SPEAK2, DECLINE | `box` | `{kind: "phrase", words: […]}` · `{kind: "declined", reason}` · `{kind: "unseen"}` |
| `why` | M4 | `word` | `{kind: "because", word, episodes: [{moment, scene, pos: [y, x]}…] (≤ 8), rule: {over: [the cited moments], band}}` · `{kind: "unknown"}` |

The questions are the offline generators' own (`brain/scene/marks.py`: `m1_items`, `m2a_items`, `m2b_items`, `m6_items`, `m3_items`, `speak_items`, `speak2_items`, `decline_items`, NAME as `run.build_questions_r` builds it), built from the world's truth by the SENSE, never by the mind. M5 items are new (PREREG §M5).

## 3 · The organ: `genome/brain.py` (builder A)
```python
class Brain:
    def __init__(self, cfg: dict): ...                       # declared["BRAIN"]
    def hears(self, source: str | None) -> bool: ...
    def learn(self, glance: dict, words: list[str], *, moment: str, scene: int, world_seed: int) -> dict
    def calibrate(self) -> dict
    def ask(self, payload: dict, glance: dict | None) -> dict   # never learns
    def summary(self) -> dict                                  # small, for STATUS
    def state_hash(self) -> str
    def save(self, base: pathlib.Path) -> None                 # writes <base>.npz + <base>.json (the caller renames atomically)
    @classmethod
    def load(cls, base: pathlib.Path, cfg: dict) -> "Brain"
```
- `glance` is `genome.gaze.glances(...)`'s own return (`feats`, `fix`, `windows`, `residual`). The located glances are `feats[:len(fix)]`; the coarse one, when GAZE declares it, is `feats[len(fix)]`, kept aside as the cache did. Things in view are `brain.scene.eye.hypotheses(fix, located)`; the learner's input is `learners.feed_rw(hyp feats, hyp pos)`.
- `learn` = the offline life's one step, in its order: `Ear.hear` as `train_scene` does it · the T-MEM-2 hook `health.heard_none` BEFORE `train_scene` (generator `substream(world_seed, "tmem2-none:<scene>")` as `run_tmem2.py` has it — read it, do not guess the tag) · `RWLearner.train_scene(X, words, referent=None, rng=substream(world_seed, f"episodic:{scene}"))` · the row appended to the calibration list · a calibration when the count of scenes learned reaches a `calibrate_at` value. Returns `{n_hyp, words, attributed: {word: hyp | None}, none: bool | None, calibrated: bool}`.
- `ask`: `begin` → calibrate if scenes were learned since the last calibration. `point` → the LAW road (`RWLearner.answer_point`, «none» by S1b-1R's `none_i`), the tie generator `marks.tie_rng(test_seed, item)`; BEFORE it, the misuse check (§M5). `what` / `say` → the pointer's hypothesis (below), then `RWRoad.held_words` / `produce_believed`. `why` → §M4.
- **The pointer.** `box` → the hypothesis with the most of its fixations inside the box ± 4 px (a fixation cell's centre pixel: `cell * 8 + 4`; `W.fixation_thing`'s own arithmetic, for ONE box); a tie → the nearest mean position to the box's centre in cells (`marks.thing_hypothesis`'s rule); none inside → `unseen`. **Pin:** on every M2b / NAME / SPEAK / SPEAK2 / DECLINE question of the scored run's fresh sets it returns the same index as `questions.json`'s `hyp` (mismatches = 0, the count printed).
- **THE GATE «BRAIN ALONE»** (`tools/brain/gate_alone.py`): the Brain, fed the scored run's cached glances in order (`/data/dev/brain-runs/scene-s1b1r/<ws>/cache/train`, fresh test caches), answers the scored run's fresh questions. Its `point` answers and its LAW-road `what` / `say` answers must EQUAL `/data/dev/brain-runs/scene-s1b1r/<ws>/fresh/arms/A-RW-R/answers_10000.json` item by item, at all three world seeds. The gate prints, per seed and per mark, items compared · items equal · the first difference. A difference is a JOIN DEFECT to fix, never a finding. Control: a planted one-word change in one training utterance must make the gate FAIL.
- **M4 · explain.** `why(word)`: `unknown` when the word was never heard or is young (< `young` meetings). Else up to 8 episodes FROM ITS OWN STORE where it heard the word and attributed it (`health.attribution`'s reading: the thing it took the word to be about), strongest responsibility first, ties by the earlier moment: each `{moment, scene, pos}`. `rule.over` = the cited moments, `rule.band` = the word's band. The brain must therefore keep, per stored row, the moment and the attributed hypothesis' position.
- **M5 · misuse.** A phrase holding two words the brain's own EAR puts in ONE type (`Ear.cover` over its mature words: words that never met in one utterance and share a type clique) names nothing that can exist → `{kind: "misuse", words: [a, b]}` (the first such pair in the phrase's order). A pair in DIFFERENT types is never misuse, heard together or not (the held-out pairs of M3 must not be flagged). Measure on the scored run's learners BEFORE wiring: the share of same-type pairs flagged, and the share of M1 + M3 phrases falsely flagged; print both. If the EAR cannot tell them apart, RAISE it.
- `save` / `load` round-trip to an equal `state_hash()`; a Brain loaded at scene n and fed scenes n… answers exactly as one that lived straight through (test).

## 4 · The mind: `creature/mind.py` (builder C)
- `__init__`: `self.brain = Brain(declared["BRAIN"])` when `BRAIN` is declared and `"brain"` is not in `self.blind`; else `None`.
- `consume`: a new branch `sense == "ask"` → `_consume_ask(row)`: a canvas-less form (`begin`, `end`, `why`) is handled at once; any other is held in `self.pending_asks[moment]` (a list, in tape order) until its eye row. A snapshot carries the pending asks as it carries `ear_pending`.
- `_consume_eye`, right after `g = gaze.glances(...)` (and after the blind-coarse strip): 
  - asks pending on this moment → answer each, in order: by the brain when there is one, else by THE ORGANS' ROAD (below). One journal row per ask: `{kind: "answer", by: "brain" | "organs", item, mark, form, answer, moment, seq, at}`. The brain does not learn from this canvas.
  - else, brain present and `brain.hears(meta.source)` and the instant carried words → `brain.learn(...)`; one journal row `{kind: "brain", act: "learn", moment, seq, at, …learn's return}`; a calibration adds `{kind: "brain", act: "calibrate", …}`.
  - the organism's own road below this point is UNTOUCHED on every canvas.
- **THE ORGANS' ROAD** (the twin's answers; #228: a control must still be able to DO the thing): `point` → the eye's own hypotheses (`brain.scene.eye.hypotheses`), each scored by the summed edge between its member glances and each phrase word's cell (`Organism.edge_many` / the words ledger); the best hypothesis, or `none` when no phrase word has a cell or every edge is 0. `what` / `say` → `Organism.recall_many` over the pointer's member glances, the words ledger's names, under the ANSWER / ABSTAIN genes → `words` or `unknown`. `why` → `unknown` unless ASK's own `why` road exists for the word. The pointer rule is §3's (import it from `genome/brain.py`; until A lands, from your own copy with a test that pins the two equal).
- `snapshot` / `resume` / `close`: the brain's state beside the organism's (`state/brain.npz`, `state/brain.json`, write-tmp-then-rename); `resume` restores it; `creature/replay.py` reproduces every `answer` and `brain` row byte for byte (test: a tape replayed twice; a tape replayed whole vs resumed from a mid-life snapshot).
- `--blind brain` = the twin: no brain, the asks answered by the organs' road. **Test:** on one tape, every journal row that is not `kind: "answer"` / `kind: "brain"` is byte-identical between the brain mind and the blind-brain mind (the brain does not disturb the organs).
- `Mind.brain_status()` → `brain.summary()` plus `asks_answered`, or `None`.

## 5 · The body, the sense, the genomes, the unit (builder B)
- `creature/senses/scene.py`: `sense(publish, stop_event, root, cfg, backlog)` — the rows of §2. `feed max backlog k`: publish the next MOMENT only while `backlog() < k` (the body passes `lambda: body.q.qsize()`), else wait 5 ms; the mind is never behind its world by more than k rows plus one moment. `feed every n ms`: a plain period. `SCENE_DOOR_GATED = True` once its tests pass. The sense checks `seed in W.WORLD_SEEDS` and refuses by name otherwise.
- `creature/body.py:main`: arms the scene sense from `declared["WORLD_SCENE"]`. The maker world is armed only when `WORLD` (drawn) is declared or `--maker` is passed; today's behaviour for every existing genome is unchanged (they all declare it — verify by grep, print the count). `_build_status` carries `scene: {published, train_done, sitting_done}` and, when the mind has one, `brain: mind.brain_status()`.
- `tools/brain/make_tape.py --genome G --root R`: the SAME sense function with a synchronous publish into a `creature.tape.Tape` (no threads, no waiting): a whole life's tape at machine speed, for the replay road (the twins, the nulls).
- Genomes (`genome/brain/`): `BRAIN-LEAN.genome` = the lean body: SEED, BODY, TAPE, HEART, CRASH, SENSE eye / ear / colour, RETINA, GAZE, DELIVER, AREA sight / words, MEET, the GROW / WIRE / SHRINK laws, THRESH, ANSWER, ABSTAIN, RECALL, ASK, STAGE 1–2, `WORLD scene`, `BRAIN` — every other ALPHA4 line `#OFF` WITH ITS REASON on the line. `BRAIN-LEAN-TWIN.genome` = the same without the BRAIN line. `BRAIN-FULL.genome` = `ALPHA4.genome` whole + `WORLD scene` + `BRAIN`. **RETINA, GAZE and SENSE colour are byte-equal to ALPHA4's in all three** (test), so the body's eye is the eye the brain scored with. SEED = the world seed.
- The unit: `deploy/creature-brain@.service`, `creature-g5@`'s [Unit] / [Service] laws kept whole (`StartLimitIntervalSec=600`, `StartLimitBurst=5`, `Restart=on-failure`, `RestartPreventExitStatus=3 4`, `TimeoutStopSec=120`, the two thread-count env lines, `PYTHONUNBUFFERED=1`), `ExecStart=/usr/bin/python3 -m creature.body --root /data/dev/genome-lives/%i --genome ${GENOME}` and nothing else. `tools/lives/launch_brain.sh <name> <commit> <genome>` (a detached checkout per life, `enable --now`) and `tools/lives/close_brain.sh <name>` (`disable --now`, `STOPPED-AT` written, then `ls ~/.config/systemd/user/default.target.wants` printed — #240).

## 6 · The grader (phase 2, after the organ's gate): `tools/brain/grade_life.py --root R`
Reads the life's tape, its journal's `answer` rows and `root/truth/scene/`, and writes the six marks with each bar's CEILING beside it (PREREG). It reuses `brain/scene/marks.py`'s graders; it never imports the mind.

## 7 · Hand-back
Each builder stops at `docs/brain/body/HANDBACK-<A|B|C>.md`: what was built, the suites' own `Ran N … OK` lines read from log files written on the final commit, every clause RAISED, every number with its file. A report is read against its own completed run.
