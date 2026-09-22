# edit: Claude (Sonnet 5, builder E), 2026-09-21 16:58 +0400 — G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md):
# PREDICT's word encoding (`xw`) hoisted above the error() call and passed through (word=, xw=, episodes=)
# so arms "conjunctive"/"episodic"/"comparator" (genome/predict.py) can read them; the default "novelty"
# arm ignores all three (byte-identical). `self.predictor` now built with `arm=genome.declared["PREDICT"]
# ["arm"]` (init and resume()).
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-19 21:41 +0400 — A2: the mind (docs/G4-PREREG.md §2.3, §2.4, §2.7).
# edit: Claude (Sonnet 5, G4 builder A), 2026-09-20 00:55 +0400 — A9/A10 (wave 2, PREREG §11.1 steps 1/2/4):
# PREDICT+FAST wired per canvas (err/lr/ep on the mind row; sight-only canvases now live through
# Organism.moment_sight, word null, no longer skipped once FAST is declared); SLEEP wired (a second mind row
# sharing the triggering canvas's seq, {"seq","sleep":{...},"hash"}); all steps gated on "GENE" in
# genome.declared, so G4-skeleton.genome (no wave-2 gene declared) stays byte-identical (G4-8).
# Determinism law: this file imports none of time, datetime, random, os.urandom (pinned by
# tests/creature/test_mind_parity.py::test_mind_has_no_clock, an AST sweep). Wall clock enters ONLY through
# a tape row's "at" field, which the mind never generates itself.
"""creature/mind.py — the mind: the only writer of memory (organism state + the journal).

`consume(row)` is the one entry point: an ear row remembers its word until the matching eye row of the
same `meta.moment` arrives (the order law, PREREG §2.2); an eye row decodes its PNG payload, glances it
(`genome.gaze.glances`), and feeds each glance feature to the organism as one `Organism.moment` call —
the SAME feed `genome/run_g1.py`'s `live()` uses, so the organism's law is untouched by the body (this is
what gate G4-2 checks). A moment with no matching ear row is sight-only: with FAST undeclared it is
counted and journaled, never fed to the organism (the skeleton's own law, preserved exactly); with FAST
declared it runs `Organism.moment_sight` per glance instead (PREREG §11.1 step 2) and writes a word=""
episode.

Every wave-2 step is gated on the gene's own presence in `genome.declared` (never on module availability
alone) so a genome that declares nothing new is byte-for-byte the walking skeleton (gate G4-8).
"""
from __future__ import annotations

import inspect
import json
import os
from pathlib import Path
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple

import numpy as np
from PIL import Image

from creature import genes as genes_module
from genome import gaze
from genome.fast import Episodes
from genome.machinery import Genome, GenomeError, Organism, parse_genome, _unit
from genome.park import Park
from genome.predict import Predictor, file as predict_file, score as predict_score
from creature.tape import _resolve_tape_dir   # W3-0b seam: the mind reads payloads where the genome says the tape is
from genome.questions import build_ledgers, why as questions_why
from genome.sentence import find_frames
from genome.sleep import cycle as run_cycle, sleep as run_sleep
from genome.world import encode_word

# A11 (PREREG §11.2): genome.curiosity / genome.think are not yet on master at the time this file was
# written — imported defensively so creature/mind.py never breaks when they land, and never stubbed here
# (Builder A owns creature/, not genome/; docs/briefs/G4-BUILDER-A-BODY.md's own instruction for this case).
try:
    from genome.curiosity import Interests
    _CURIOSITY_AVAILABLE = True
except ImportError:
    Interests = None                    # type: ignore[assignment]
    _CURIOSITY_AVAILABLE = False

try:
    from genome import think as think_laws
    _THINK_LAWS_AVAILABLE = True
except ImportError:
    think_laws = None                   # type: ignore[assignment]
    _THINK_LAWS_AVAILABLE = False

# edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:2x +0400 — D-G12/W3-1: Builder B's believe() gains
# `ledgers=None, clash_enabled=True` on branch g4-wave3-b (genome-wt-e, commit 04a302a) — a different
# worktree this branch must NOT include (creature/ is Builder A's, genome/ is Builder B's). Detected by
# introspecting whatever `believe` this tree's genome/think.py actually defines, so the SAME call site
# works unchanged before and after that branch merges: today (5 positional params only) it passes neither
# kwarg -- byte-identical to the call before this edit; once merged, both are passed automatically.
_BELIEVE_KWARGS: frozenset = frozenset()
if _THINK_LAWS_AVAILABLE:
    try:
        _BELIEVE_KWARGS = frozenset(inspect.signature(think_laws.believe).parameters)
    except (TypeError, ValueError):
        _BELIEVE_KWARGS = frozenset()

try:                                    # TRAITS (PREREG §11.2) is not yet on master at the time of A9/A10;
    from genome.traits import Traits    # gated on BOTH "TRAITS" in declared AND this import having succeeded —
    _TRAITS_AVAILABLE = True            # never a stub of this module written here (Builder A owns creature/, not genome/).
except ImportError:
    Traits = None                       # type: ignore[assignment]
    _TRAITS_AVAILABLE = False

SNAPSHOT_EVERY = 500
# edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: the dedicated "reflex" (outcome/SIT) episodes
# ring's capacity. No numeric parameter exists in either OUTCOME's or SIT's fixed genome-text shape (G-MOT-2/3), so
# this is a code constant, sized like FAST's own smaller genomes (genome/G4.genome declares FAST 20000; this ring
# carries far sparser traffic — one row per act/SIT-publish, not one per glance) — not a gene value.
OUTCOME_EPISODES_CAP = 2000


def _bind_pool(feats: List[np.ndarray]) -> List[np.ndarray]:
    # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:30 +0400 — G-EYE-2 (= G-MIND-2): the glances of
    # one canvas become ONE moment. F's diagnostic (docs/briefs/G5-F-REPORT.md §1) found the mechanism —
    # 77.5% of all sight births happen on glances 1-3, not glance 0, and those cells misfire ~10pp more
    # and wire to >1 thing ~15pp more than glance-0 births — is BINDING (several looks at the SAME,
    # correctly-fixated object each birthing their own cell), not clutter (an off-thing glance): 87.3% of
    # the extra glance-1-3 births are themselves ON the thing. The fix: one shared percept, not four
    # competing ones. The rule (EYE.md §1.3's transsaccadic-integration citation — "one object, several
    # fixations, ONE percept" — names WHAT must happen, not an exact formula; this is the plain reading of
    # it): MEAN the glances' feature vectors, then re-normalise to unit length. Mean (not max or first-
    # glance-only) because every glance is a real, cheap, already-computed look at the same object under
    # F's own finding (glance 0 is not "the good one" and the rest "noise" — 22.3% of ALL sight births,
    # including many that never misfire, are already on glance 0; the diagnostic's signal is glance INDEX,
    # not glance content). Unit-renormalise because Organism.cos() (genome/machinery.py:451) is a RAW dot
    # product against unit-norm stored cells — Area.cells are always unit length (born directly from a
    # RETINA `unit`-terminated vector, or from this pooled one) — a non-unit query would silently rescale
    # every cosine comparison (BIRTH's THETA_N threshold included) and permanently corrupt the newborn
    # cell's OWN stored vector norm forever after (the shape of #231(1): an unnormalised quantity treated
    # as if it already were). Cost: one np.mean + one np.linalg.norm over a (4,112)-shaped or (4,144)-shaped
    # array — microseconds, timed in docs/briefs/G5-J-REPORT.md.
    # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:55 +0400 — fixed a typo in this comment
    # ("(co,4)-shaped" -> "(4,112)-shaped": 4 glances x 112 sight dims, or x144 with colour); no code change.
    # Returns a ONE-element list (or the input unchanged if empty) so every existing `for x in feats:` call
    # site keeps working unchanged, now iterating once instead of F times — this is where "one canvas = one
    # moment" actually happens: Organism.moment()/moment_sight() is called exactly once per canvas below,
    # org.t advances by 1 per canvas instead of by GAZE.fixations (see the cadence table, G5-J-REPORT.md).
    if not feats:
        return feats
    return [_unit(np.mean(np.stack(feats, axis=0), axis=0))]


class Mind:
    """genome_path: the genome file (read once, text + parsed). run_root: the SAME root the body's Tape
    uses — payload bytes for a tape row live at run_root/tape/<row.payload>. blind: gene names this mind
    is blind to (e.g. {"gaze"} runs the random-gaze twin, PREREG §2.9's --blind gaze)."""

    def __init__(self, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset()):
        self.genome_path = Path(genome_path)
        self.run_root = Path(run_root)
        self.genome_text = self.genome_path.read_text()
        self.genome: Genome = parse_genome(self.genome_text)
        self.blind = frozenset(blind)

        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — W3-0 (docs/G4-WAVE3-CLAUSES.md):
        # THE GENERIC REFUSAL, first — before any object is built from the genome (a refusal message must
        # not be preceded by some other constructor's error). Every declared gene not in creature/genes.py's
        # RUNS registry (a real call site) refuses the organism by name; TRAITS's row is `None` (no
        # interpreter yet, PREREG §12/§14), which is why this single check now replaces that earlier
        # standalone `raise` — one law, not two.
        bad = genes_module.unwired(self.genome.declared)
        if bad:
            raise GenomeError(f"{', '.join(bad)} declared but nothing runs it (W3-0): the organism does not start")

        # PREREG §11.1 step 5: "frozen" is a TWIN-ONLY blind — it changes how the Organism itself is
        # built, not a per-step gate. FROZEN's own parser clause is not on master yet (A10); absent, its
        # "after" defaults to 50, exactly as the PREREG says.
        frozen_after: Optional[int] = None
        if "frozen" in self.blind:
            frozen_after = int(self.genome.declared.get("FROZEN", {}).get("after", 50))
        self.org = Organism(self.genome, frozen_after=frozen_after)

        self.episodes: Optional[Episodes] = (
            Episodes(int(self.genome.declared["FAST"]["episodes"]), self.genome.sight_dim(), self.genome.words_dim())
            if "FAST" in self.genome.declared else None
        )
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K (MOTOR-HANDS.md G-MOT-2/3): a SEPARATE
        # Episodes ring for non-visual "reflex" observations (an act's outcome; SIT's exam score) — never self.episodes,
        # and NEVER replayed through Organism.moment() by genome.sleep.sleep(). Why: SLEEP replays the n most-surprising
        # live episodes AS ORDINARY MOMENTS (sleep.py's own law), i.e. `org.moment(rec["x_s"], rec["x_w"])`. An outcome
        # has no sight glance — a zero-vector x_s makes Area.cos(x)==0 everywhere (machinery.py:427, a plain dot product,
        # no norm division), which is < THETA_N, so `_resonate` (machinery.py:550) BIRTHS a garbage sight cell every
        # replay; a REAL glance vector paired with encode_word(act) would instead wire that visual context to a
        # non-"thing" word inside stage 2's HEBB/DELTA (machinery.py:566), corrupting Q1 recall. Neither is safe under
        # the CURRENT SLEEP law, so MOTOR-HANDS.md G-MOT-2's "SLEEP already replays surprising acts into SLOW" is
        # RAISED in the report, not built: this ring gives `most_surprising()`/`nearest()` for free (the EXISTING
        # Episodes class, no new learning machinery) so "ranks replay" is a real, working capability on this ring, but
        # genome.sleep.sleep() is never pointed at it. dim_s/dim_w match self.episodes' so the same class works
        # unmodified; x_s[0] doubles as the reflex's own scalar payload ("got") — never read by cos()/_resonate since
        # this ring is never fed to Organism.moment(). Built when EITHER OUTCOME or SIT is declared (SIT's score reuses
        # this same mechanism, tagged act="sit" — see _record_reflex).
        self.outcome_episodes: Optional[Episodes] = (
            Episodes(OUTCOME_EPISODES_CAP, self.genome.sight_dim(), self.genome.words_dim())
            if ("OUTCOME" in self.genome.declared or "SIT" in self.genome.declared) else None
        )
        self._act_expected: Dict[str, float] = {}     # act -> running mean of past "got" values (the PREDICTION; #175)
        self._act_n: Dict[str, int] = {}               # act -> count backing the running mean
        # merge (Claude (Fable 5.1), g5-integration): K's ring above + E's arm-aware Predictor below — both kept.
        # G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md): the arm name lives on the genome's PREDICT
        # clause (machinery.py's parser, default "novelty" when the genome's PREDICT line carries no
        # trailing "; error <arm>" — every genome on disk before this edit, G4.genome included).
        self.predictor: Optional[Predictor] = (
            Predictor(self.org, arm=self.genome.declared["PREDICT"].get("arm", "novelty"))
            if "PREDICT" in self.genome.declared else None
        )
        self._last_sleep_at: int = 0        # org.t at the last SLEEP boundary crossed

        # A11 (PREREG §11.1 step 3): THINK is gated on "THINK" in genome.declared, which requires a
        # parser clause not yet on master at the time this was written (raised in the builder report,
        # not worked around) -- park/curiosity are constructed whenever THEIR OWN genes are declared
        # (both parse today), independent of whether THINK itself can ever fire in this genome.
        self.park: Optional[Park] = Park(int(self.genome.declared["PARK"]["after"])) if "PARK" in self.genome.declared else None
        self.interests: Optional["Interests"] = (
            Interests(int(self.genome.declared["CURIOSITY"]["interests"]), np.random.default_rng(self.genome.seed))
            if "CURIOSITY" in self.genome.declared and _CURIOSITY_AVAILABLE else None
        )
        self._think_rng = np.random.default_rng([int(self.genome.seed), 0x71494e4b])   # "THINK" bytes-ish, distinct from any other stream in this file
        self._canvas_index: int = 0
        self._filed_predictions: list = []          # [{"row": FILE's row dict, "due_canvas": int}, ...] awaiting the next showing of their word
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        # words/pairs with a currently FILED-but-not-yet-SCORED rule, so _think_pool never re-files the
        # SAME rule twice while its first attempt is still pending (removed once scored, whether PASS or
        # FAIL, so a word/pair may be re-attempted later — up to PARK's own n identical fails). Not
        # persisted in snapshot() (pre-existing gap, shared with _filed_predictions/Park/Interests — see
        # the builder report).
        self._induce_pending: set = set()            # words
        self._deduce_pending: set = set()             # "w1|w2" (sorted) pair keys
        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:05 +0400 — D-G12/W3-1 (docs/G4-WAVE3-CLAUSES.md):
        # revisits/extensions/clashes, coded against Builder B's believe() "kind" interface before it lands
        # (today believe() always returns kind="belief"; the mapping below already handles the other three).
        self.think_counters: Dict[str, int] = {
            "thinks": 0, "parked": 0, "beliefs": 0, "revisits": 0, "extensions": 0, "clashes": 0,
            "predictions_filed": 0, "predictions_scored": 0,
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11 (docs/briefs/
            # LIFE-C-QUESTION-SENTENCE.md): a new counter goes on STATUS on every branch that writes STATUS
            # (#164) — creature/body.py's STATUS loop already unpacks every key of this dict unconditionally.
            "questions_written": 0, "questions_answered": 0,
            "frames_filed": 0, "frames_scored": 0, "frames_true": 0,
            "said": 0, "heard_yes": 0, "heard_no": 0,
        }
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 3 (SENTENCE): "w1|w2" keys
        # currently filed-not-yet-scored (INDUCE/DEDUCE's own _induce_pending/_deduce_pending pattern above).
        self._frame_pending: set = set()
        # every frame the mind has ever filed, keyed "w1|w2" -> {"w1","w2","episodes"} (MOUTH reads this to
        # pick what to say; G-MOT-6's citation gate reads its "episodes").
        self._frames: Dict[str, Dict[str, object]] = {}
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:40 +0400 — advisor-caught: the q-file
        # FILENAME counter, shared by every writer of run/ask/out/q-<n>.json (_maybe_ask's real wants AND
        # MOUTH's _maybe_say "is" rows) so no two writes collide on a name -- kept separate from
        # think_counters["questions_written"], which is now the SEMANTIC "a real want was formed" mark
        # (see _write_ask_out's and _maybe_ask's own comments).
        self._ask_out_n: int = 0
        # L-10 (QUESTION): want -> the form it was asked with, so a want is asked AT MOST ONCE. Loaded from
        # `run/ask/out/ASKED.json` HERE (not only at resume()) -- a plain file beside the questions
        # themselves, independent of the snapshot cadence, so a crash between a snapshot and the next
        # question can never re-ask a want the ledger already remembers (the same durability reason
        # ear_pending exists beside the ledger.json's own moment_word).
        asked_path = self.run_root / "ask" / "out" / "ASKED.json"
        try:
            self._asked = {str(k): str(v) for k, v in json.loads(asked_path.read_text()).items()} if asked_path.exists() else {}
        except (json.JSONDecodeError, OSError):
            self._asked = {}   # a torn/partial ASKED.json from a crash mid-write is "nothing asked yet", never fatal (#230's discipline)
        # a resonating-but-not-newly-born sight cell -> how many wordless (word="") canvases have resonated
        # it in a row without it ever being named (L-10's "seen for the SECOND time without a word").
        self._wordless_seen: Dict[int, int] = {}
        # the tape row currently being consumed -- read by nested calls (_grade_rule, _maybe_ask, _maybe_say)
        # that need "at"/"seq" but are not themselves handed `row` (mirrors the existing thread-the-row
        # discipline everywhere else in this file, without widening every intermediate signature).
        self._cur_at: Optional[str] = None
        self._cur_seq: Optional[int] = None
        # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: the words the ear has ever delivered to a met canvas
        # (sight-only "" never enters). A word not in it OPENS AN ARRIVAL when ARRIVAL is declared (below);
        # rebuilt at resume from the ledger's moment_word so a resumed mind and a replay agree.
        self._heard: set = set()

        self.pending: Dict[str, str] = {}                 # ear-consumed, eye not yet arrived: moment -> word
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: moment -> every word heard
        # (ear rows APPEND, never overwrite -- see consume()'s ear branch above).
        self.pending_words: Dict[str, List[str]] = {}
        self._last_words_in_instant: List[str] = []    # L-11 task 4 (MOUTH): this canvas's own words, read by _maybe_say
        self._last_glance = None                        # L-11 task 4 (MOUTH): this canvas's own first glance
        self.moment_word: Dict[int, str] = {}              # org.t (per GLANCE, before increment) -> word — build_ledgers' input
        self.last_seq: int = 0
        self.sight_only_skipped: int = 0
        self.journal_rows_written: int = 0
        self.snapshot_count: int = 0
        self.sleep_count: int = 0                        # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — STATUS.sleeps (PREREG §11.1 step 4)
        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — the standalone TRAITS refusal that
        # lived here is now one row of the generic refusal above (creature/genes.py RUNS["mind"]["TRAITS"] = None),
        # checked immediately after parse_genome, before this point is ever reached.
        self._last_snapshot_moments: int = 0

        (self.run_root / "journal").mkdir(parents=True, exist_ok=True)
        (self.run_root / "state").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ consume
    def consume(self, row: Dict[str, object]) -> None:
        sense = row["sense"]
        meta = row.get("meta") or {}
        moment = meta.get("moment")
        if sense == "ear":
            self.pending[moment] = meta.get("word")
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2 (docs/briefs/
            # LIFE-C-QUESTION-SENTENCE.md): every word heard since the last eye row on THIS moment,
            # APPENDED (never overwritten, unlike self.pending above) -- SENTENCE's frame-finder reads
            # this from the episode row. Popped in _consume_eye alongside self.pending; a moment with one
            # ear row behaves exactly as before (a one-element list).
            w = meta.get("word")
            if w:
                self.pending_words.setdefault(moment, []).append(w)
        elif sense == "eye":
            self._consume_eye(row, moment)
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: the three new tape senses. Each method
        # gates itself on its own gene's declared presence (W3-0's own law one level up: a sense may publish a row of
        # this sense name even under a genome that never declared the gene -- e.g. a test tape, or another builder's
        # world -- and the mind must not act on it then; matches the existing "a 'door' row ... carries no organism
        # work here" law for an unarmed sense).
        elif sense == "outcome":
            self._consume_outcome(row)
        elif sense == "sit":
            self._consume_sit(row)
        elif sense == "body":
            self._consume_body(row)
        # a "door" row (the ask door / other senses not yet armed) carries no organism work here
        self.last_seq = int(row["seq"])
        if self.org.t - self._last_snapshot_moments >= SNAPSHOT_EVERY:
            self.snapshot()

    # ------------------------------------------------------------------ G5-K: ACT/OUTCOME/SIT/body (reflex episodes)
    def _record_reflex(self, act: str, got: Optional[float], expected_in: Optional[float],
                        residual_in: Optional[float], source: str) -> Dict[str, object]:
        """Shared by an "outcome" tape row (G-MOT-2) and a "sit" tape row (G-MOT-3, tagged act="sit"): computes the
        residual (expected vs got — never from how much changed, #175's own law) and, unless blind, writes it as an
        episode in the DEDICATED self.outcome_episodes ring (never self.episodes -- see __init__'s comment on why).
        `expected`: the row's own value if it supplied one (trusting the publisher -- e.g. a future HANDS/game
        mechanism that computes its own expectation); otherwise the mind's own per-act running mean of past `got`
        values -- a real PREDICTION, not the previous single reading (which would be byte-identical to the E21
        magnitude-only twin and control nothing, MOTOR-HANDS.md G-MOT-2). `residual`: the row's own value if supplied
        (trusting a publisher that already graded it, e.g. Builder L's game reward); else |got - expected| when both
        exist; else None ("not gradable", #228 (a) -- never a fabricated 0)."""
        verbs = (self.genome.declared.get("ACT") or {}).get("verbs")
        in_vocab = verbs is None or act in verbs
        expected: Optional[float] = float(expected_in) if expected_in is not None else self._act_expected.get(act)
        got_f: Optional[float] = float(got) if got is not None else None
        if residual_in is not None:
            residual: Optional[float] = float(residual_in)
        elif expected is not None and got_f is not None:
            residual = abs(got_f - expected)
        else:
            residual = None
        ep_id: Optional[int] = None
        if self.outcome_episodes is not None and "outcome" not in self.blind:
            dim_s = self.genome.sight_dim()
            x_s = np.zeros(dim_s, dtype=np.float64)
            x_w = np.zeros(self.genome.words_dim(), dtype=np.float64)
            if got_f is not None:
                x_s[0] = got_f     # the payload slot -- never read by cos()/_resonate (this ring never reaches Organism.moment)
            ep_id = self.outcome_episodes.write(moment=self.org.t, x_s=x_s, x_w=x_w, word=act,
                                                  surprise=float(residual) if residual is not None else 0.0)
            if got_f is not None:                       # update the running expectation AFTER filing this residual
                n = self._act_n.get(act, 0) + 1          # (the NEXT observation of this act is graded against it, not this one)
                old = self._act_expected.get(act, got_f)
                self._act_expected[act] = old + (got_f - old) / n
                self._act_n[act] = n
        return {"act": act, "expected": expected, "got": got_f, "residual": residual, "source": source,
                "in_vocab": in_vocab, "gradable": residual is not None, "ep": ep_id}

    def _consume_outcome(self, row: Dict[str, object]) -> None:
        """G-MOT-2: OUTCOME must be declared (else this sense-name row is a fact on the tape with no consumer, same
        as an unarmed door). meta carries EXACTLY act/expected/got/residual/source (the shape hard rule 6 fixes, so
        Builder L's game-reward rows are readable here too)."""
        if "OUTCOME" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        result = self._record_reflex(act=str(meta.get("act", "")), got=meta.get("got"), expected_in=meta.get("expected"),
                                       residual_in=meta.get("residual"), source=str(meta.get("source", "")))
        self._write_journal(row["at"], {"seq": row["seq"], "outcome": result})

    def _consume_sit(self, row: Dict[str, object]) -> None:
        """G-MOT-3: SIT must be declared. `--blind sit` means "the score is not published" (MOTOR-HANDS.md's own
        words for this twin) -- blind is a Mind-level concept here (senses never receive it), so the mind treats a
        blind-sit row as if SIT had never fired: journaled as blind, no reflex recorded."""
        if "SIT" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        if "sit" in self.blind:
            self._write_journal(row["at"], {"seq": row["seq"], "sit": {"blind": True}})
            return
        result = self._record_reflex(act="sit", got=meta.get("score"), expected_in=None, residual_in=None,
                                       source=str(meta.get("source", "sit")))
        self._write_journal(row["at"], {"seq": row["seq"], "sit": result})

    def _consume_body(self, row: Dict[str, object]) -> None:
        """BODY-SENSES.md §4.1: "the readings; the DRIVE is the mind's" -- this gene carries no threshold, so
        there is nothing here to compute beyond recording the reading itself as a journal row (the refusal test in
        BODY-SENSES §4.1 -- "count the moments in which any journaled decision differs" -- is satisfied structurally
        by this row's own presence/absence; RAISED in the report: nothing downstream of this row yet changes THINK's
        pool or CURIOSITY, so a stricter reading of that clause is not yet met -- no consumer exists to wire it to)."""
        if "SENSE_BODY" not in self.genome.declared:
            return
        if "body" in self.blind:
            self._write_journal(row["at"], {"seq": row["seq"], "body": {"blind": True}})
            return
        meta = row.get("meta") or {}
        reading = meta.get("reading") or {}
        self._write_journal(row["at"], {"seq": row["seq"], "body": dict(reading)})

    def _rebuild_act_expectation(self) -> None:
        """G5-K, called from resume(): replays self.outcome_episodes' own live entries (in id order == temporal
        order — ids never reused, an overwritten id's slot is simply skipped by .get() returning None) through the
        SAME running-mean update _record_reflex uses, so a resumed mind's next reflex is graded against the same
        expectation a non-resumed one would compute."""
        self._act_expected = {}
        self._act_n = {}
        ep = self.outcome_episodes
        if ep is None:
            return
        for eid in range(ep.n_written):
            rec = ep.get(eid)
            if rec is None or not rec["word"]:
                continue
            act = rec["word"]
            got_f = float(rec["x_s"][0]) if rec["x_s"] is not None and rec["x_s"].size > 0 else None
            if got_f is None:
                continue
            n = self._act_n.get(act, 0) + 1
            old = self._act_expected.get(act, got_f)
            self._act_expected[act] = old + (got_f - old) / n
            self._act_n[act] = n

    def _consume_eye(self, row: Dict[str, object], moment: Optional[str]) -> None:
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11: this canvas's own
        # "at"/"seq", read by nested calls (_grade_rule, _maybe_ask, _maybe_say) that are not themselves
        # handed `row`. Set at the top, read-only for the duration of this one call.
        self._cur_at = row["at"]
        self._cur_seq = row["seq"]
        # edit: Claude (Fable 5.1), 2026-09-21 12:01 +0400 — W3-0b seam (Builder C's finding 4): the payload is read under the genome's own TAPE path
        # (creature/tape.py:_resolve_tape_dir — byte-identical for the default `run/tape`), never a second hardcoded "tape".
        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        mode = "random" if "gaze" in self.blind else "surprise"
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:30 +0400 — G-EYE-3/§3.6: colour=None unless
        # SENSE colour is declared (Genome.colour, machinery.py) — a complete no-op call otherwise, byte-
        # identical to every existing pin.
        g = gaze.glances(rgb, self.genome.retina, self.genome.gaze, mode, row["sha"], colour=self.genome.colour)
        word = self.pending.pop(moment, None) if moment is not None else None
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: every word this
        # instant's ear rows delivered, in order (popped alongside self.pending above; a moment with one
        # ear row is a one-element list, byte-identical in meaning to `word` alone).
        words_in_instant: List[str] = self.pending_words.pop(moment, []) if moment is not None else []
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 4 (MOUTH): the CURRENT
        # instant's words and first glance, read by _maybe_think -> _maybe_say below (the mouth judges what
        # it says against THIS canvas's own glance, never a stored/replayed one).
        self._last_words_in_instant: List[str] = words_in_instant
        # G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md): hoisted above PREDICT's error() call, which
        # arm "comparator" needs (a word's encoding, read-only) BEFORE Organism.moment() runs for this
        # canvas — encode_word is pure, so computing it here changes nothing else (word is None on a
        # sight-only canvas, xw stays None, exactly as arm "comparator"/"conjunctive" expect).
        xw = encode_word(word, self.genome.ear_blank_zero) if word is not None else None
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:30 +0400 — G-EYE-2/BIND (_bind_pool, above):
        # undeclared (the common case today) this is g["feats"] itself, unchanged — every existing `for x
        # in g["feats"]:` loop below now reads `org_feats` instead, with IDENTICAL contents when BIND is
        # off. Declared: ONE pooled vector, so the loops below run their body once instead of F times —
        # this is the whole of "one canvas = one moment" (org.t advances by 1, not by GAZE.fixations).
        org_feats = _bind_pool(g["feats"]) if "BIND" in self.genome.declared else g["feats"]

        # PREREG §11.1 step 1 (PREDICT): measured once, on the FIRST glance, regardless of whether this
        # canvas has a word — a sight-only canvas is just as surprising or expected as a worded one.
        predict_on = self.predictor is not None and "predict" not in self.blind
        fast_on = self.episodes is not None
        err, lr_scale = 0.0, 1.0
        if predict_on and g["feats"]:
            # G5-E: word/xw/episodes passed unconditionally — the default "novelty" arm ignores all
            # three (genome/predict.py's error(), byte-identical branch).
            err = self.predictor.error(g["feats"][0], word=word, xw=xw, episodes=self.episodes)
            lr_scale = self.predictor.modulate(1.0)
        t_at_f0 = self.org.t
        f0 = g["feats"][0] if g["feats"] else None
        self._last_glance = f0    # L-11 task 4 (MOUTH): this canvas's own first glance, for _maybe_say

        # edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400 — G-EYE-1/G-MIND-1 (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md):
        # the seam contract. `where` (glance 0's window origin), `when` (the tape row's own instant — the ONE wall clock this
        # file's determinism law lets in, and it enters only through `row["at"]`, never a fresh read), `act` (today always
        # "glance" — DELIVER's own declared value; MOTOR-HANDS.md's wider verb list is a later gene) and `source` (the eye row's
        # OWN `meta["source"]`, already written by whichever sense published it — creature/world_maker.py / senses/folder.py —
        # copied, never invented) are computed HERE, beside f0/xw, and go nowhere near them: `seam0` is a plain dict handed to
        # Episodes.write and the journal row as EXTRA keyword arguments / EXTRA dict keys, never concatenated into f0 or xw, so
        # the cosine org.moment()/moment_sight() see is byte-for-byte what it always was. Gated on DELIVER alone (what the eye
        # promises to deliver); Episodes only STORES it when MOMENT is also declared (FAST's own schema promise) — see fast_on's
        # kwargs below. tests/genome/test_deliver_moment.py's parity test is what proves this claim, not this comment.
        deliver_on = "DELIVER" in self.genome.declared
        moment_on = "MOMENT" in self.genome.declared
        meta = row.get("meta") or {}
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught (#164's class):
        # STATUS declares `questions_answered` but nothing wrote it. The world-maker's QUESTION door
        # (creature/world_maker.py:_publish_canvas) stamps `answering: "<qid>"` on BOTH the ear and eye rows
        # of the canvas it shows again — this is the eye row, so a non-empty `answering` here is exactly
        # "this canvas answers a want this mind once asked." Counted once per answered canvas (never per
        # ear+eye pair — only the eye row reaches this method).
        if meta.get("answering"):
            self.think_counters["questions_answered"] += 1
        seam0: Dict[str, object] = {}
        if deliver_on and g["windows"]:
            # "where" in self.blind (G-EYE-1/G-MIND-1's own test clause c, `--blind where`): the SAME
            # blind-twin convention as "gaze"/"predict"/"sleep"/"curiosity" above — glance normally,
            # compute the window origin normally, but drop it before it is stored, so a caller can prove
            # a mechanism that reads `where` sits at exactly chance once `where` is taken away.
            seam0 = {"where": ((int(g["windows"][0][0]), int(g["windows"][0][1])) if "where" not in self.blind else None),
                      "when": row["at"], "act": "glance", "source": meta.get("source"), "glance": 0}

        if word is not None:
            births_before = len(self.org.births)
            edges_before = len(self.org.edges_log)
            prunes_before = len(self.org.prunes_log)
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: a never-heard word is an ARRIVAL — the birth budget is
            # fresh BEFORE the moment that first meets it (life 1 never called new_arrival: arrivals 0, budget spent once,
            # 419 births refused, nothing born after 07:41 +04). Gated on the gene: an undeclared ARRIVAL changes nothing.
            arrival_n: Optional[int] = None
            if word not in self._heard:
                self._heard.add(word)
                if "ARRIVAL" in self.genome.declared:
                    self.org.new_arrival()
                    arrival_n = int(self.org.arrivals)
            for x in org_feats:
                self.moment_word[self.org.t] = word          # keyed by the organism's OWN moment counter, one per glance (or one per canvas under BIND)
                S, T = self.org.moment(x, xw, lr_scale=lr_scale)
                if predict_on:
                    self.predictor.note_winners(S)
            ep_kwargs = seam0 if moment_on else {}         # G-MIND-1: Episodes stores the seam only once MOMENT declares the columns
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: words_in_instant/
            # tape_moment are stored UNCONDITIONALLY (not gated on MOMENT — the plan's own words: "MOMENT
            # keys ... gains nothing in the genome"), a fresh pair of Episodes columns exactly like x_s2 above.
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0, x_w=xw, word=word, surprise=err,
                                          words_in_instant=words_in_instant, tape_moment=moment,
                                          **ep_kwargs) if fast_on else None
            self._score_due_predictions(word, g["feats"][0] if g["feats"] else None, words_in_instant=words_in_instant)
            births = [[b[1], int(b[2]), b[3]] for b in self.org.births[births_before:]]
            edges_born = len(self.org.edges_log) - edges_before
            edges_pruned = len(self.org.prunes_log) - prunes_before
            journal_row = {
                "seq": row["seq"], "moment": moment, "word": word,
                "fix": [[int(y), int(x)] for (y, x) in g["fix"]],
                "births": births,
                "cells": [int(self.org.sight.alive.sum()), int(self.org.words.alive.sum())],
                "edges": [edges_born, edges_pruned],
                "err": round(err, 4), "lr": round(lr_scale, 3), "ep": ep_id,
                "hash": self.org.state_hash(),
                **({"arrival": arrival_n} if arrival_n is not None else {}),   # PREREG §15: an event field on the row where an arrival opened
                # G-EYE-1 (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400): every glance's window origin, this
                # episode's when/act/source — EXTRA keys, never touching any key above; a genome that never declares DELIVER
                # writes exactly the dict this branch always wrote (the parity test pins it).
                **({"windows": [[int(t), int(l)] for (t, l) in g["windows"]], "when": row["at"], "act": "glance",
                    "source": meta.get("source"), "glance": 0} if deliver_on else {}),
            }
            self._write_journal(row["at"], journal_row)
        elif fast_on:
            # PREREG §11.1 step 2: sight-only, FAST declared -> Organism.moment_sight per glance (B2),
            # never Organism.moment (no word to MEET); an episode is still written, word "". A sight-only
            # glance can still BIRTH a sight cell (moment_sight's own _resonate call), and
            # questions.build_ledgers needs moment_thing[m] for EVERY birth moment, sight-only ones
            # included, or snapshot() KeyErrors the first time such a birth happens (caught by this
            # test, not by inspection) -- word "" here, exactly what the written episode itself carries.
            births_before = len(self.org.births)
            for x in org_feats:
                self.moment_word[self.org.t] = ""
                self.org.moment_sight(x)
            births_after = len(self.org.births)
            xw_blank = encode_word("", self.genome.ear_blank_zero)
            ep_kwargs = seam0 if moment_on else {}
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0, x_w=xw_blank, word="", surprise=err,
                                          words_in_instant=words_in_instant, tape_moment=moment, **ep_kwargs)
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 task 1 (QUESTION): "a
            # wordless sight seen for the SECOND time without a word". The mechanism-grounded reading: no
            # NEW cell was born this canvas (moment_sight resonated an EXISTING cell) AND that cell was
            # itself born wordless (every birth ever recorded for it carries word="" in the ledger) — the
            # organism already holds this look and still has no name for it. Counted per resonating cell;
            # the want fires on the 2nd such count (never the 1st — "seen ... for the SECOND time").
            if ("QUESTION" in self.genome.declared and births_after == births_before
                    and f0 is not None and moment is not None):
                r = self.org.recall("sight", f0)
                # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — a discovered fix:
                # r["lit"] (the SIGHT cell that actually resonated) is the right field here, not r["cell"]
                # (recall's cross-area ANSWER, which needs a sight->words EDGE to exist — during STAGE 1,
                # before MEET starts, or for any picture with no word yet, recall abstains "noedge" and
                # r["cell"] is None even though a real sight cell resonated; r["lit"] is populated on every
                # non-"novel" abstain, not just a successful answer). Caught by this file's own test
                # (test_question_sentence_mouth.py), not by inspection: the trigger never fired at all
                # under r["cell"] on a real (STAGE-1) tape.
                cell = r.get("lit")
                if cell is not None:
                    ledgers = build_ledgers(self.org, self.moment_word)
                    if ledgers["sight"].get(cell) == {""}:
                        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — the FIRST canvas
                        # that births this cell is sighting #1 (never counted here — births_after !=
                        # births_before skips this whole block for it); THIS resonate-without-birth event
                        # is therefore already sighting #2 the moment it is counted once. Firing at n==1
                        # (not n>=2, which would need a THIRD sighting) — caught by this file's own test:
                        # at n>=2 the trigger never fired on a real 2-canvas tape at all.
                        n = self._wordless_seen.get(cell, 0) + 1
                        self._wordless_seen[cell] = n
                        if n >= 1:
                            self._maybe_ask(f"sight:{cell}", "what-is", [moment])
            self._write_journal(row["at"], {
                "seq": row["seq"], "moment": moment, "word": None,
                "err": round(err, 4), "ep": ep_id, "hash": self.org.state_hash(),
                **({"windows": [[int(t), int(l)] for (t, l) in g["windows"]], "when": row["at"], "act": "glance",
                    "source": meta.get("source"), "glance": 0} if deliver_on else {}),
            })
        else:
            # the skeleton's own law, untouched: no FAST declared -> a sight-only canvas is skipped
            # entirely, the organism never sees it (G4-8's byte-identical pin depends on this).
            self.sight_only_skipped += 1
            self._write_journal(row["at"], {"seq": row["seq"], "moment": moment, "sight_only": True})

        self._canvas_index += 1
        self._maybe_sleep(row)
        self._maybe_think(row)

    def _maybe_sleep(self, row: Dict[str, object]) -> None:
        """PREREG §11.1 step 4: every SLEEP.every MOMENTS (org.t, not canvases), after the canvas that
        crosses the boundary — a while loop so a canvas whose glances cross more than one boundary at
        once (a small SLEEP.every) still gets one sleep() per boundary, never skips one. Journaled as a
        SECOND mind row sharing the triggering canvas's own seq (creature.replay's compare() groups mind
        rows by seq into ordered lists for exactly this reason — A10's own finding, see the report)."""
        if "SLEEP" not in self.genome.declared or "sleep" in self.blind or self.episodes is None:
            return
        every = int(self.genome.declared["SLEEP"]["every"])
        n = int(self.genome.declared["SLEEP"]["replay"])
        while self.org.t - self._last_sleep_at >= every:
            self._last_sleep_at += every
            # genome.sleep.sleep() calls org.moment() once per replayed episode -- org.t advances and can
            # BIRTH cells for moments my own per-glance loops never see (those loops only run inside
            # _consume_eye). questions.build_ledgers needs moment_thing[m] for EVERY birth's moment, so
            # those org.t values must be pre-recorded here, in the SAME order sleep() will replay them
            # (Episodes.most_surprising is read-only/deterministic -- calling it again inside sleep() on
            # the same, unchanged store returns the identical id list). Caught by a longer-tape test, not
            # by inspection: a bare `run_sleep(...)` call here KeyErrors the first time a replay births.
            t0 = self.org.t
            for i, eid in enumerate(self.episodes.most_surprising(n)):
                rec = self.episodes.get(eid)
                if rec is not None:
                    self.moment_word[t0 + i] = rec["word"]
            result = run_sleep(self.org, self.episodes, n)
            self.sleep_count += 1
            cycled = run_cycle(self.org)
            if "TRAITS" in self.genome.declared and _TRAITS_AVAILABLE:
                Traits.learn(self.episodes)      # per the interface name given for wave 2; unexercised until genome/traits.py lands
            self._write_journal(row["at"], {
                "seq": row["seq"], "sleep": {**result, "cycle": cycled}, "hash": self.org.state_hash(),
            })
            # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:05 +0400 — W3-3 (docs/G4-WAVE3-CLAUSES.md;
            # genome/curiosity.py's own contract, B10 note 3): one sleep_boundary() call per boundary crossed
            # (this loop iterates once per boundary), so a recombine chain never pairs an "answered" item from
            # before this boundary with one from after it.
            if self.interests is not None:
                self.interests.sleep_boundary()

    # ------------------------------------------------------------------ THINK (A11, PREREG §11.1 step 3)
    def _score_due_predictions(self, word: str, first_glance: Optional[np.ndarray],
                                 words_in_instant: Optional[List[str]] = None) -> None:
        """A prediction filed by THINK's kind-(b) work becomes scorable the next time ITS OWN word is
        shown again — "the journal's err/recall on the next canvas with that word" (PREREG's own route
        text). Simplification, documented in the report: the decider "recall == word" is evaluated by a
        fresh word-cell lookup (questions.build_ledgers) rather than a persisted per-edge index — correct,
        but O(births) per score, acceptable at this life's scale.

        edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        an entry carrying a "rule" (an INDUCE/DEDUCE FILE row, _think_rule below) is scored by ITS OWN
        decider — "the resonance of C on that canvas >= THETA_N for >= half of C" (the brief's verbatim
        text) — never the sight-road's "recall == word" (a rule's claim is about a CLUSTER of cells, not
        a single word-answer edge). `_grade_rule` then runs CURIOSITY's/PARK's outcome (the brief: "the
        outcome grades the act")."""
        if not self._filed_predictions or first_glance is None:
            return
        still_pending = []
        ledgers = None
        words_in_instant = words_in_instant or []
        for entry in self._filed_predictions:
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 3 (SENTENCE): a
            # frame entry's target_word is w1, the COLOUR — never equal to `word` (the moment's own word is
            # the OBJECT, game.py's own publish order). Its trigger is "w1 in this instant's words", not
            # "word == w1"; every other entry keeps the original word==target_word trigger, unchanged.
            frame_w2 = entry.get("frame_w2")
            if frame_w2 is not None:
                due = entry["target_word"] in words_in_instant
            else:
                due = entry["target_word"] == word
            if due and self._canvas_index >= entry["due_canvas"]:
                rule = entry.get("rule")
                if frame_w2 is not None:
                    evidence = self._frame_evidence(str(frame_w2), first_glance)
                elif rule is not None:
                    evidence = self._rule_evidence(rule["cluster"], first_glance)
                else:
                    if ledgers is None:
                        ledgers = build_ledgers(self.org, self.moment_word)
                    r = self.org.recall("sight", first_glance)
                    Lw = ledgers["words"]
                    evidence = r["cell"] is not None and Lw.get(r["cell"], set()) == {word}
                scored = predict_score(entry["row"], evidence)
                predict_ledger_path = self.run_root / "state" / "predictions.jsonl"
                predict_ledger_path.parent.mkdir(parents=True, exist_ok=True)
                with predict_ledger_path.open("a") as f:
                    f.write(json.dumps(scored, default=str) + "\n")
                self.think_counters["predictions_scored"] += 1
                if frame_w2 is not None:
                    self._frame_pending.discard(entry.get("frame_key"))
                    self.think_counters["frames_scored"] += 1
                    if evidence:
                        self.think_counters["frames_true"] += 1
                elif rule is not None:
                    self._grade_rule(rule, evidence)
                elif not evidence:
                    # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:40 +0400 — advisor-caught
                    # (BLOCKS): this is the codebase's OTHER, pre-existing prediction road (W3 builder D's
                    # plain "sight" kind, _think_work's "sight" branch — "the next showing of this sight
                    # resonates X's cells", filed via predict_file() directly, carrying neither a "rule"
                    # nor a "frame_w2" key). Its FALSE outcomes used to be silently dropped here — no want
                    # ever formed, so QUESTION's trigger (b) ("a rule fails once") only ever covered
                    # INDUCE/DEDUCE's "rule" kind, never this one. Demonstrated live in the 6-min
                    # pre-flight (docs/briefs/LIFE-C-REPORT.md): 2 of 7 scored predictions there were FALSE
                    # "sight"-kind outcomes and neither produced a question. The brief's own trigger-(b)
                    # text names no specific mechanism, so this FALSE outcome asks what-is too — a direct
                    # _maybe_ask_word call, never _grade_rule (whose PARK/CURIOSITY bookkeeping is built
                    # around INDUCE/DEDUCE's op/want shape and does not apply to this claim family).
                    self._maybe_ask_word(f"predict:sight:{entry['target_word']}", str(entry["target_word"]))
            else:
                still_pending.append(entry)
        self._filed_predictions = still_pending

    def _frame_evidence(self, w2: str, first_glance: np.ndarray) -> bool:
        """L-11 task 3's decider, verbatim: "the eye answers BOTH words on the next instant that carries
        w1" — the mind's own recall_many over that instant's glances must return w2's cell (sight →
        words). Simplified to `recall` over the due canvas's first glance (the same simplification
        `_score_due_predictions`'s pre-existing sight-road already makes for "recall == word", documented
        there); a scoring read never changes the organism."""
        ledgers = build_ledgers(self.org, self.moment_word)
        r = self.org.recall("sight", first_glance)
        Lw = ledgers["words"]
        return r["cell"] is not None and Lw.get(r["cell"], set()) == {w2}

    def _rule_evidence(self, cluster: List[int], first_glance: np.ndarray) -> bool:
        """W3-2c (edit: Claude (Fable 5.1), 2026-09-21 12:01 +0400 — PREREG §18): the decider is «the due canvas's first-glance WINNER is in C» —
        the alive sight cell of highest cosine, provided it RESONATES (cos >= THETA_N, machinery's own comparison, READ not
        CALLED: `_resonate` births). The clause's first decider («>= half of C resonating») was measured BEFORE any life on a
        copy of life 2's snapshot: ceiling 0.03 on the creature's OWN known words (16 words x 10 held-out first glances; «any of
        C» .99; «winner in C» .96) — a bar above its ceiling reads on itself (#228 (b)); Builder D's 0/3 stands on the record
        as that decider's reading. A scoring read never changes the organism."""
        if not cluster:
            return False
        area = self.org.sight
        if area.n == 0:
            return False
        c = np.asarray(area.cos(first_glance), dtype=float)[: area.n]
        alive = np.asarray(area.alive, dtype=bool)[: area.n]
        c = np.where(alive, c, -np.inf)
        winner = int(np.argmax(c))
        if not np.isfinite(c[winner]) or c[winner] < self.org._theta(area):
            return False
        return winner in set(int(x) for x in cluster)

    def _grade_rule(self, rule: Dict[str, object], evidence: bool) -> None:
        """W3-2: "the outcome grades the act" — a scored PASS is CURIOSITY's "answered" (generalize +
        recombine, curiosity.py's existing law); a scored FAIL is the NEW "failed" outcome (specialize's
        x0.5, under its own name — curiosity.py, this task) and is also reported to PARK by name
        ("rule_failed_3"); PARK's own n-identical-reasons law (genome/park.py, unchanged) parks the want
        after the n-th FAIL (D39's rule). Either way the rule leaves its pending set — scored, so a NEW
        attempt may be filed later (unless just parked, in which case _think_pool's own is_parked() check
        keeps a fresh one from being filed — reopened only by PARK's existing reopen() road, unwired in
        this wave, same as every other PARK want today)."""
        op, want = str(rule["op"]), str(rule["want"])
        key = want.split(":", 1)[1] if ":" in want else want
        (self._induce_pending if op == "induce" else self._deduce_pending).discard(key)
        if self.interests is not None:
            self.interests.update({"kind": "rule", "key": key}, "answered" if evidence else "failed")
        if not evidence:
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 task 1 (QUESTION): "a
            # rule fails once (the think outcome that today counts toward PARK's 3)" -- fires on THIS one
            # failure, not only the n-th that parks it (PARK's own parking, if it happens, is trigger (d),
            # handled separately below). `key` is the word (induce) or "w1|w2" (deduce) the rule claimed;
            # its latest live episode's own tape_moment (L-11 task 2's new Episodes column) is the "what-is"
            # want's evidence -- the same word/cluster a human would need shown again to judge the claim.
            self._maybe_ask_word(f"rule:{want}", key)
            if self.park is not None:
                if self.park.answer(want, "rule_failed_3") == "parked":
                    self.think_counters["parked"] += 1
                    self._maybe_ask_word(f"parked:{want}", key)

    def _recent_word_glances(self, word: str, n: int, fallback) -> list:
        """The sight features of the word's last n live episodes (by moment), oldest first; the fallback alone if none."""
        ep = self.episodes
        if ep is None:
            return [fallback]
        live = np.flatnonzero((ep.ids >= 0) & (ep.word == word))
        if live.size == 0:
            return [fallback]
        order = live[np.argsort(ep.moment[live], kind="stable")][-n:]
        return [ep.x_s[i].copy() for i in order]

    # ------------------------------------------------------------------ QUESTION (L-10)
    def _write_ask_out(self, payload: Dict[str, object]) -> None:
        """Writes ONE `run/ask/out/q-<n>.json` row -- the SAME JSON shape `run/ask/in/` accepts (creature/
        ask.py's own inbox schema), but this mind is the WRITER here, not the answerer: the world-maker's
        door (creature/world_maker.py:sense) and, for a `what-is` no sense drew, the human ASK door's own
        listener, are its readers. `n` is `self._ask_out_n`, a mind-local FILENAME counter shared by every
        writer of a q-file (never the tape row's own seq -- two wants can form on the same tape row,
        advisor's point 5), so no two writes ever collide on a name.
        edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:40 +0400 — advisor-caught (BLOCKS): an
        earlier fix (2026-09-22 19:12) put this increment on `self.think_counters["questions_written"]`
        directly, which conflates two different things: MOUTH's `is` rows (this method's OTHER caller,
        _maybe_say) now counted toward the QUESTION-specific `questions_written` STATUS mark -- a life
        where MOUTH says 50 things and QUESTION forms 0 wants would have read `questions_written=50`, a
        false positive on the L-10 mark. Split: `self._ask_out_n` (below) owns the FILENAME/seq only;
        `think_counters["questions_written"]` is incremented ONLY by `_maybe_ask` itself (a real want),
        again below. Verified by TestMouth.test_two_says_get_two_distinct_q_files, which now also asserts
        `questions_written == 0` after two SAYs and zero real asks."""
        out_dir = self.run_root / "ask" / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        n = self._ask_out_n
        (out_dir / f"q-{n}.json").write_text(json.dumps(payload, default=str))
        self._ask_out_n += 1

    def _maybe_ask(self, want: str, form: str, args: list, why_word: Optional[str] = None) -> None:
        """L-10: forms ONE question for `want`, at most once ever (self._asked, persisted to
        run/ask/out/ASKED.json so a resumed OR replayed mind never re-asks). `why_word`, when given, is
        resolved through questions.why() (the addresses behind the mind's own knowledge of that word) and
        carried on the row as "why" — the plan's own text: "why: the addresses questions.why() returns
        when a word is involved"."""
        if "QUESTION" not in self.genome.declared:
            return
        if want in self._asked:
            return
        self._asked[want] = form
        asked_path = self.run_root / "ask" / "out" / "ASKED.json"
        asked_path.parent.mkdir(parents=True, exist_ok=True)
        asked_path.write_text(json.dumps(self._asked))
        payload: Dict[str, object] = {
            "q": form, "args": list(args), "from": "mind",
            "seq": self._ask_out_n, "at": self._cur_at,
        }
        if why_word is not None:
            ledgers = build_ledgers(self.org, self.moment_word)
            record = questions_why(self.org, ledgers, self.episodes, why_word)
            payload["why"] = {
                "cells": [[area, int(c)] for area, c in record["cells"]],
                "episodes": list(record["episodes"]),
                "edges": [[int(s), int(t), float(w)] for s, t, w in record["edges"]],
            }
        self._write_ask_out(payload)   # advances self._ask_out_n itself (see that method's own comment)
        self._write_journal(self._cur_at, {"seq": self._cur_seq, "question": payload})
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:40 +0400 — advisor-caught: the SEMANTIC
        # STATUS mark for "a real QUESTION want was formed" lives HERE, on the one caller that actually
        # forms a want -- never on _write_ask_out (shared with MOUTH's unrelated "is" rows, see that
        # method's own comment).
        self.think_counters["questions_written"] += 1

    def _latest_tape_moment_for_word(self, word: str) -> Optional[str]:
        """The tape moment string (L-11 task 2's new Episodes column) of `word`'s LATEST live episode, or
        None if it has none live (fallen off FAST's ring, or never seen). Shared by every QUESTION trigger
        that needs "a moment to show again" for a word it already knows about."""
        if self.episodes is None:
            return None
        ep = self.episodes
        live = np.flatnonzero((ep.ids >= 0) & (ep.word == word))
        if live.size == 0:
            return None
        last_slot = int(live[np.argsort(ep.moment[live], kind="stable")][-1])
        return str(ep.tape_moment[last_slot]) or None

    def _maybe_ask_word(self, want: str, word: str) -> None:
        """Resolves `word` (or, for a DEDUCE pair key "w1|w2", its FIRST word -- deduce's claim is about
        the shared cell, not one word alone) to its LATEST live episode's own tape_moment and asks a
        what-is question citing it, with the word's own why(). No episode to cite yet (a word whose only
        episodes have already fallen off FAST's ring) asks nothing -- there is no moment to name."""
        if "QUESTION" not in self.genome.declared:
            return
        w = word.split("|", 1)[0] if "|" in word else word
        tape_moment = self._latest_tape_moment_for_word(w)
        if tape_moment is None:
            return
        self._maybe_ask(want, "what-is", [tape_moment], why_word=w)

    def _maybe_ask_clash(self, want: str, word: str) -> None:
        """L-10: a belief CLASH forms a want too, form "is" (the brief's own shape: `{"q": "is", "args":
        [<moment>, <word>]}`) -- the same latest-tape-moment resolution as _maybe_ask_word, a different
        rendered form."""
        if "QUESTION" not in self.genome.declared:
            return
        tape_moment = self._latest_tape_moment_for_word(word)
        if tape_moment is None:
            return
        self._maybe_ask(want, "is", [tape_moment, word], why_word=word)

    def _think_pool(self) -> list:
        """PREREG §11.1 step 3's POOL: (a) words of the last 200 episodes whose recall abstains; (b)
        episodes with word ""; (c) filed predictions now due. Each item: {"kind", "key", "episode", "pred"}
        (the shape the coordinator's interface message gives for genome.curiosity.Interests)."""
        pool: list = []
        if self.episodes is not None:
            n_written = self.episodes.n_written
            first_id = max(0, n_written - 200)
            seen_words = set()
            for eid in range(first_id, n_written):
                rec = self.episodes.get(eid)
                if rec is None or not rec["word"] or rec["word"] in seen_words:
                    continue
                r = self.org.recall("sight", rec["x_s"])
                if r["cell"] is None:
                    seen_words.add(rec["word"])
                    if self.park is not None and self.park.is_parked(rec["word"]):
                        continue   # edit: Claude (Fable 5.1), 2026-09-21 15:45 +0400 — §18 add. 2: a PARKED word is not re-worked (the rule items' own filter, mirrored; a re-worked parked want counted "parked" again — life 3a's circle at 619 and 659)
                    pool.append({"kind": "word", "key": rec["word"], "episode": eid, "pred": None})
            for eid in range(0, n_written):
                rec = self.episodes.get(eid)
                if rec is not None and rec["word"] == "":
                    if self.park is not None and self.park.is_parked(f"ep{eid}"):
                        continue   # same law for a parked wordless sight
                    pool.append({"kind": "sight", "key": f"ep{eid}", "episode": eid, "pred": None})
        now = self._canvas_index
        for entry in self._filed_predictions:
            if now >= entry["due_canvas"]:
                pool.append({"kind": "due", "key": entry["target_word"], "episode": None, "pred": entry["row"]})
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        # "rule" items — INDUCE (a word with >= k agreeing episodes, no counter-example) and DEDUCE (two
        # standing beliefs sharing a cell, or the same word split disjoint — unroutable, refused by name).
        # Each candidate is computed by CALLING think_laws.induce()/deduce() here (never re-deriving their
        # pairing/agreement law a second time in this file) and carried on the pool item as `pred` — a
        # word/pair already pending (filed, not yet scored) or already PARKED is skipped so the SAME claim
        # is never filed twice while an attempt is outstanding, or after PARK has said stop. Both genes
        # gate the WHOLE candidate computation (never just the later FILE call) — an undeclared INDUCE/
        # DEDUCE means the mind does not even ask think_laws for a rule, matching W3-0's "the machinery
        # does not run it" law one level up from FILE's own gate in _think_work.
        if "INDUCE" in self.genome.declared and self.episodes is not None and _THINK_LAWS_AVAILABLE:
            k = int(self.genome.declared["INDUCE"]["from_episodes"])
            for rule_row in think_laws.induce(self.episodes, k, self.org):
                word = rule_row.get("word")
                if not word or word in self._induce_pending:
                    continue
                if self.park is not None and self.park.is_parked(f"induce:{word}"):
                    continue
                pool.append({"kind": "rule", "key": word, "episode": None, "pred": rule_row, "op": "induce"})
        if "DEDUCE" in self.genome.declared and _THINK_LAWS_AVAILABLE:
            beliefs = think_laws.read_beliefs(self.run_root / "state" / "beliefs.jsonl", fold=True)
            for claim_row in think_laws.deduce(beliefs):
                words = claim_row.get("words") or [None, None]
                pair_key = "|".join(sorted(str(w) for w in words))
                if pair_key in self._deduce_pending:
                    continue
                if self.park is not None and self.park.is_parked(f"deduce:{pair_key}"):
                    continue
                pool.append({"kind": "rule", "key": pair_key, "episode": None, "pred": claim_row, "op": "deduce"})
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 3 (SENTENCE): a "frame"
        # kind, one item per candidate frame genome.sentence.find_frames() returns (kind-fair with word/
        # sight/rule/outcome above, W3-2's own "kind is chosen first, uniformly" law untouched) -- gated on
        # the ring's own presence (a frame needs words_in_instant, FAST's own column). A pair already
        # pending (filed, not yet scored) or PARKED is skipped, same law as INDUCE/DEDUCE above.
        if "SENTENCE" in self.genome.declared and self.episodes is not None:
            for frame_row in find_frames(self.episodes):
                key = f"{frame_row['w1']}|{frame_row['w2']}"
                if key in self._frame_pending:
                    continue
                if self.park is not None and self.park.is_parked(f"frame:{key}"):
                    continue
                pool.append({"kind": "frame", "key": key, "episode": None, "pred": frame_row, "op": "frame"})
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: an "outcome" kind, one item per
        # distinct act among the last 50 live reflex episodes (word/sight's own "last N, one per key" shape, scaled
        # down to this ring's much sparser traffic). Gated on the ring's own presence, not on OUTCOME/SIT separately
        # -- either gene can have populated it. #232's addendum: a branch no test reaches crashes on its first real
        # walk -- see tests/creature/test_g5k_outcome.py::test_think_can_choose_an_outcome_item for the walk.
        if self.outcome_episodes is not None:
            n_reflex = self.outcome_episodes.n_written
            first_reflex = max(0, n_reflex - 50)
            seen_acts: set = set()
            for eid in range(first_reflex, n_reflex):
                rec = self.outcome_episodes.get(eid)
                if rec is None or not rec["word"] or rec["word"] in seen_acts:
                    continue
                seen_acts.add(rec["word"])
                pool.append({"kind": "outcome", "key": rec["word"], "episode": eid, "pred": None})
        return pool

    def _think_choose(self, pool: list):
        if not pool:
            return None
        # edit: Claude (Fable 5.1), 2026-09-21 15:35 +0400 — PREREG §18 addendum 2, the pool-composition rule: the KIND is chosen
        # first, uniformly over the kinds present (the mind's own think rng, so replay is exact), and CURIOSITY chooses
        # WITHIN the kind. Once INDUCE clusters the word's own cells, every inducible word is a "rule" item on every think
        # (21 on life 3a's words) and the word items — the only road to a belief — were starved: in the fixed replay of
        # life 3a 175 of 181 thinks were rule thinks, and the think-counter fixtures formed no belief at all. Kind fairness
        # is a fixed mind rule; CURIOSITY's law (which item within a kind) is untouched, and the blind twin isolates it.
        curiosity_on = self.interests is not None and "curiosity" not in self.blind
        if not curiosity_on and not ("curiosity" in self.blind and "CURIOSITY" in self.genome.declared):
            return pool[0]                                                # no CURIOSITY declared: the first item (the skeleton's pinned road, unchanged)
        # 2026-09-21 15:51 +0400 — kind fairness is CURIOSITY's road (and its blind twin's), never the no-CURIOSITY skeleton's
        kinds = sorted({str(it.get("kind")) for it in pool})
        kind = kinds[int(self._think_rng.integers(0, len(kinds)))] if len(kinds) > 1 else kinds[0]
        sub = [it for it in pool if str(it.get("kind")) == kind]
        if curiosity_on:
            return self.interests.choose(sub, self._think_rng)
        return sub[int(self._think_rng.integers(0, len(sub)))]            # blind curiosity: the rng's uniform pick within the kind

    def _think_work(self, item: dict) -> Dict[str, object]:
        """Works one pool item; returns {"outcome", "parked", ...}. Every dead end goes to
        park.answer(want, reason) when PARK is declared (PREREG: "every dead end goes to park.answer");
        without PARK declared a dead end simply stays a dead end (nothing to park it with)."""
        def dead_end(want: str, reason: str, ask_on_park: Optional[Callable[[], None]] = None) -> Dict[str, object]:
            parked = False
            if self.park is not None:
                parked = self.park.answer(want, reason) == "parked"
                if parked:
                    self.think_counters["parked"] += 1
                    # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 task 1
                    # (QUESTION): "whenever PARK parks a want" — trigger (d), generic to every kind that
                    # can dead-end through PARK (a caller supplies HOW to ask, since "want" alone does not
                    # say whether there is a word or a bare episode to cite).
                    if ask_on_park is not None:
                        ask_on_park()
            return {"outcome": reason, "parked": parked}

        if item["kind"] == "word":
            word = item["key"]
            word_ask = lambda: self._maybe_ask_word(f"parked:word:{word}", word)   # noqa: E731 — local, read only by dead_end() below
            if not _THINK_LAWS_AVAILABLE:
                return dead_end(word, "think_laws_unavailable", ask_on_park=word_ask)
            ledgers = build_ledgers(self.org, self.moment_word)
            record = questions_why(self.org, ledgers, self.episodes, word)
            rec = self.episodes.get(item["episode"]) if self.episodes is not None else None
            if rec is None:
                return dead_end(word, "episode_gone", ask_on_park=word_ask)
            # edit: Claude (Fable 5.1), 2026-09-19 23:33 +0400 — PREREG §11.1 (a) as read in the first 30-min life: the pool admits a word whose
            # LATEST glance abstains, and re-asking the SAME glance can only abstain again (172/172 dead ends). The work now asks over the
            # word's last five episodes' glances (Organism.recall_many, G1's road) — a word known in general though this glance was not
            # becomes a belief; a word unknown over five glances is a dead end (parkable after three).
            xs = self._recent_word_glances(word, 5, fallback=rec["x_s"])
            r = self.org.recall_many("sight", xs)
            if r.get("cell") is None:
                return dead_end(word, "no_cell_answers", ask_on_park=word_ask)
            # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-0b (docs/G4-WAVE3-CLAUSES.md):
            # think_laws.believe() is a real call to BELIEF's mechanism (genes.py's RUNS entry) — gated on
            # BELIEF's own declared presence now, not called unconditionally. A word item without BELIEF
            # declared is a dead end named "no_belief_gene" (never a crash, never a silent belief written
            # for a gene the genome never declared).
            if "BELIEF" not in self.genome.declared:
                return dead_end(word, "no_belief_gene", ask_on_park=word_ask)
            # edit: Claude (Fable 5.1), 2026-09-19 23:37 +0400 — believe() takes the beliefs FILE; the run ROOT was passed and the first belief
            # ever reached (after the recall_many fix) crashed the mind with IsADirectoryError — the crash law fired as designed.
            # edit: Claude (Fable 5.1), 2026-09-19 23:38 +0400 — why() tags cells as (area, id); believe() takes ints and clash() compares the sets,
            # so a belief carries the word's SIGHT cells (its look); the word-side cells are the word's own by definition.
            sight_cells = [int(c) for area, c in record["cells"] if area == "sight"]
            # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:2x +0400 — D-G12/W3-1 (the coordinator's
            # integration note on Builder B's landed interface, g4-wave3-b @ 04a302a): `ledgers` gives
            # rule 4's ledger half a live caller; `clash_enabled` gates the clash half on BELIEF's OWN
            # declared presence (PREREG §14: the clash half is a gene, not a side effect) -- both passed
            # ONLY when this tree's believe() actually accepts them (_BELIEVE_KWARGS, module-level above),
            # so the call is unchanged (and unbroken) against today's 5-parameter believe().
            extra_kwargs = {}
            if "ledgers" in _BELIEVE_KWARGS:
                extra_kwargs["ledgers"] = ledgers
            if "clash_enabled" in _BELIEVE_KWARGS:
                extra_kwargs["clash_enabled"] = "BELIEF" in self.genome.declared
            row = think_laws.believe(word, sight_cells, record["episodes"], self.org.t,
                                      self.run_root / "state" / "beliefs.jsonl", **extra_kwargs)
            # D-G12/W3-1: believe() returns a "kind" in {"belief","revisit","extension","clash"} once
            # Builder B's dedupe lands; today it is always "belief" (plain append). Coded against the
            # interface now: an absent/unknown kind (a stub, or today's shape) counts as "beliefs" and
            # never crashes.
            KIND_TO_COUNTER = {"belief": "beliefs", "revisit": "revisits", "extension": "extensions", "clash": "clashes"}
            kind = row.get("kind", "belief") if isinstance(row, dict) else "belief"
            self.think_counters[KIND_TO_COUNTER.get(kind, "beliefs")] += 1
            if kind == "clash":
                # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 task 1 (QUESTION):
                # "a belief CLASH is filed" forms a want, form "is" ({"q":"is","args":[<moment>,<word>]}).
                clash_lines = row.get("clashes") if isinstance(row, dict) else None
                self._maybe_ask_clash(f"clash:{word}:{clash_lines}", word)
            return {"outcome": "belief", "parked": False, "belief": row}

        if item["kind"] == "sight":
            rec = self.episodes.get(item["episode"]) if self.episodes is not None else None
            if rec is None:
                return dead_end(item["key"], "episode_gone")
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10 task 1 (QUESTION):
            # this episode's OWN tape_moment (L-11 task 2's column) is exactly the "wordless sight" a
            # what-is question needs to cite, when PARK ends up parking this want.
            tape_moment = rec.get("tape_moment")
            sight_ask = (lambda: self._maybe_ask(f"parked:sight:{item['key']}", "what-is", [tape_moment])) if tape_moment else None
            candidates = self.episodes.nearest(rec["x_s"], 10)
            nearest_word = None
            for eid, _cos in candidates:
                other = self.episodes.get(eid)
                if other is not None and other["word"]:
                    nearest_word = other["word"]
                    break
            if nearest_word is None:
                return dead_end(item["key"], "no_route", ask_on_park=sight_ask)
            # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-0b (docs/G4-WAVE3-CLAUSES.md):
            # predict_file() is a real call to FILE's mechanism (genes.py's RUNS entry) — gated on FILE's
            # own declared presence now. Checked HERE (after the route is found, before filing it) so a
            # genome without FILE still exercises the routing logic above and dead-ends by name at the
            # point FILE itself would have refused everything anyway.
            if "FILE" not in self.genome.declared:
                return dead_end(item["key"], "no_file_gene")
            filed = predict_file(
                claim=f"the next showing of this sight resonates {nearest_word}'s cells",
                route="the journal's err/recall on the next canvas with that word",
                decider="recall == word", due="the next showing",
            )
            if not filed["accepted"]:
                return dead_end(item["key"], "no_route")
            self._filed_predictions.append({"row": filed, "target_word": nearest_word, "due_canvas": self._canvas_index + 1})
            self.think_counters["predictions_filed"] += 1
            return {"outcome": "filed", "parked": False, "route_word": nearest_word}

        if item["kind"] == "due":
            # already scored by _score_due_predictions when its word was next shown; if it is still in
            # the pool here, its word has not recurred yet -- not yet answerable, not a dead end either.
            return {"outcome": "not_yet_due", "parked": False}

        if item["kind"] == "rule":
            # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
            # a rule (INDUCE/DEDUCE) is a PREDICTION, filed through FILE's four fields exactly like the
            # "sight" kind above — induce()/deduce() (genome/think.py) already CALLED predict.file()
            # internally to build item["pred"] (_think_pool), so the row here is already accepted-or-
            # refused BY NAME; gated on FILE's own declared presence (W3-0b) BEFORE that row is ever
            # journaled — an undeclared FILE means the mind never writes a row FILE itself never
            # sanctioned (the candidate computation in _think_pool is gated separately, on INDUCE/DEDUCE's
            # own presence, one level up — W3-0's own law: a declared-but-unwired gene never runs at all).
            op = str(item.get("op"))
            key = str(item.get("key"))
            want = f"{op}:{key}"
            if "FILE" not in self.genome.declared:
                return dead_end(want, "no_file_gene")
            row = item.get("pred")
            if row is None:
                return dead_end(want, "no_route")
            (self._induce_pending if op == "induce" else self._deduce_pending).add(key)
            self._file_rule(row, want=want, op=op)
            if not row.get("accepted"):
                return {"outcome": "refused", "parked": False, "refused": row.get("refused")}
            return {"outcome": "filed", "parked": False, "want": want}

        if item["kind"] == "frame":
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 3 (SENTENCE): a
            # frame is a PREDICTION, filed through FILE's four fields exactly as the plan's own text names
            # them (claim "w1 w2"; route "frame"; decider "the eye answers BOTH words on the next instant
            # that carries w1"; due "the next instant with w1"). Scored later by _score_due_predictions'
            # frame branch (triggers on w1 IN that instant's words_in_instant, never word==w1 -- w1 is the
            # COLOUR, never the moment's own `word`, the OBJECT).
            frame_row = item.get("pred") or {}
            w1, w2 = str(frame_row.get("w1")), str(frame_row.get("w2"))
            key = str(item.get("key"))
            want = f"frame:{key}"
            if "FILE" not in self.genome.declared:
                return dead_end(want, "no_file_gene")
            filed = predict_file(
                claim=f'"{w1} {w2}"', route="frame",
                decider="the eye answers BOTH words on the next instant that carries w1",
                due=f"the next instant with {w1!r}",
            )
            predict_ledger_path = self.run_root / "state" / "predictions.jsonl"
            predict_ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with predict_ledger_path.open("a") as f:
                f.write(json.dumps(filed, default=str) + "\n")
            self.think_counters["predictions_filed"] += 1
            if not filed.get("accepted"):
                return {"outcome": "refused", "parked": False, "refused": filed.get("refused")}
            self._frame_pending.add(key)
            episodes_cited = [int(e) for e in (frame_row.get("episodes") or [])]
            self._frames[key] = {"w1": w1, "w2": w2, "episodes": episodes_cited}
            self._filed_predictions.append({
                "row": filed, "target_word": w1, "due_canvas": self._canvas_index,
                "frame_w2": w2, "frame_key": key,
            })
            self.think_counters["frames_filed"] += 1
            return {"outcome": "filed", "parked": False, "frame": key}

        if item["kind"] == "outcome":
            # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: a read-only reflection on one
            # act's own residual -- no FILE claim (no established consumer for "is this act predictable" as a
            # falsifiable claim yet; a further growth line, not built here, raised in the report). Never crashes on
            # a ring the read/write side share (self.outcome_episodes), never a dead end (a residual, gradable or
            # not, is always a real reading, not a failure to find one).
            rec = self.outcome_episodes.get(item["episode"]) if self.outcome_episodes is not None else None
            if rec is None:
                return dead_end(item["key"], "episode_gone")
            return {"outcome": "reflected", "parked": False, "act": rec["word"], "residual": float(rec["surprise"])}

        return dead_end(str(item.get("key")), "unknown_kind")

    def _file_rule(self, row: Dict[str, object], want: str, op: str) -> None:
        """W3-2: predictions.jsonl gets EVERY FILE outcome for a rule — accepted or refused BY NAME
        (predict.py's file()/FILE's law: 'never silently dropped, never accepted half-written');
        `predictions_filed` counts both ('filed by name or refused by name'), moved AT LAST (after the
        write, and after the accepted branch is queued) per the brief's own words. An accepted row is
        queued for scoring at its due canvas — due_canvas = self._canvas_index (NOT +1): this method
        only ever runs from _think_work, called from _maybe_think, which runs AFTER _consume_eye's own
        canvas_index increment for the triggering canvas (creature/mind.py's own call order) — so
        self._canvas_index here already names the NEXT canvas to be consumed, and "the word's next
        showing" (PREREG's own route text) is exactly that canvas. (The pre-existing 'sight' road above
        uses +1 and is one canvas later than it needs to be — a pre-existing quirk, left as is and named
        in the report, not fixed here: changing it changes what a live rule's existing consumers see.)"""
        target_word: Optional[str] = None
        if row.get("accepted"):
            if op == "induce":
                target_word = row.get("word")
            else:
                words = row.get("words") or [None]
                target_word = words[0]
        predict_ledger_path = self.run_root / "state" / "predictions.jsonl"
        predict_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with predict_ledger_path.open("a") as f:
            f.write(json.dumps(row, default=str) + "\n")
        if row.get("accepted") and target_word:
            cluster = [int(c) for c in (row.get("cluster") or row.get("shared") or [])]
            self._filed_predictions.append({
                "row": row, "target_word": str(target_word), "due_canvas": self._canvas_index,
                "rule": {"op": op, "want": want, "cluster": cluster},
            })
        self.think_counters["predictions_filed"] += 1

    def _maybe_think(self, row: Dict[str, object]) -> None:
        """PREREG §11.1 step 3: every THINK.every canvases. THINK's own gene clause is not on master at
        the time this was written (`"THINK" in self.genome.declared` is therefore never true today for
        any genome this worktree can parse) — RAISED, not worked around; the step is fully wired against
        the given interface names and exercised directly by the test (bypassing the gate) against every
        piece that does not need genome.curiosity/genome.think."""
        if "THINK" not in self.genome.declared:
            return
        every = int(self.genome.declared["THINK"]["every"])
        if every <= 0 or self._canvas_index % every != 0:
            return
        pool = self._think_pool()
        item = self._think_choose(pool)
        self.think_counters["thinks"] += 1
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 19:12 +0400 — advisor-caught: this call used
        # to sit AFTER the `if item is None: return` below, so a think whose pool was EMPTY (exactly the
        # state a settled life reaches once every word is parked and every frame scored) never reached the
        # mouth -- MOUTH would go silent by control flow, not by G-MOT-6's own citation gate. Moved above
        # the early return so a filed, cited frame is said on every THINK tick regardless of what (if
        # anything) the pool held this time; verified by
        # tests.creature.test_question_sentence_mouth.TestMouth.test_says_even_when_the_think_pool_is_empty.
        self._maybe_say(row)
        if item is None:
            self._write_journal(row["at"], {"seq": row["seq"], "think": {"item": None, "kind": None, "outcome": "empty_pool", "parked": False}})
            return
        result = self._think_work(item)
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": result.get("outcome"), "parked": bool(result.get("parked"))},
        })

    # ------------------------------------------------------------------ MOUTH (L-11 task 4)
    def _maybe_say(self, row: Dict[str, object]) -> None:
        """L-11 task 4: "on a think, if a filed frame exists and the CURRENT instant's words include w1,
        the mouth SAYS the frame": a journal `say` row + an `ask/out` "is" row, judged SYNCHRONOUSLY by
        the mind's OWN recall of THIS instant (the songbird's loop -- it hears itself through its own eye;
        no external judge, no teacher, never the async ask/in->ask/out round trip). G-MOT-6's gate: a said
        frame must cite its episodes or is refused BY NAME (never said). One frame per think (the first
        match, dict order == filed order); the abstention rate is counted, never optimised (STATUS `said`/
        `heard_yes`/`heard_no` — a mouth that says nothing passes this test perfectly, and that is reported,
        not hidden)."""
        if "MOUTH" not in self.genome.declared:
            return
        words = self._last_words_in_instant
        for key, frame in self._frames.items():
            w1 = str(frame.get("w1"))
            if w1 not in words:
                continue
            episodes_cited = frame.get("episodes") or []
            if not episodes_cited:
                # G-MOT-6: "a said frame must cite its episodes or is refused by name" — a planted
                # uncited frame (self._frames[...]["episodes"] == []) is refused, never said.
                self._write_journal(row["at"], {"seq": row["seq"],
                                                  "say": {"frame": key, "outcome": "refused", "reason": "uncited"}})
                return
            w2 = str(frame.get("w2"))
            heard = self._last_glance is not None and self._frame_evidence(w2, self._last_glance)
            moment = (row.get("meta") or {}).get("moment")
            self._write_ask_out({"q": "is", "args": [moment, w2], "from": "mouth", "seq": row["seq"], "at": row["at"]})
            self._write_journal(row["at"], {
                "seq": row["seq"],
                "say": {"frame": f"{w1} {w2}", "seq": row["seq"], "heard": "yes" if heard else "no", "episodes": episodes_cited},
            })
            self.think_counters["said"] += 1
            self.think_counters["heard_yes" if heard else "heard_no"] += 1
            return   # one frame per think

    def _write_journal(self, at: str, obj: Dict[str, object]) -> None:
        date = at[:10]
        path = self.run_root / "journal" / f"{date}.jsonl"
        with path.open("a") as f:
            f.write(json.dumps(obj) + "\n")
        self.journal_rows_written += 1

    # ------------------------------------------------------------------ snapshot / resume
    def snapshot(self) -> None:
        """Every SNAPSHOT_EVERY moments (and on close()): write organism.npz + organism.json atomically
        (write to a *_tmp basename, then os.replace — PREREG §2.7's write-tmp-then-rename law; see the
        builder report for why the base name differs from the PREREG's literal "organism.npz.tmp": that
        exact path, fed through Organism.save's np.savez_compressed suffix rule and Path.with_suffix,
        produces mismatched filenames that Organism.load cannot read back). ledger.json carries the
        PREREG's {"last_seq", "moment_word", "moments"} PLUS the derived {"sight", "words"} ledgers in
        the shape genome/ask.py's load() reads, built via genome.questions.build_ledgers(org, moment_word)
        — and "ear_pending" (this mind's own in-flight ear-without-eye moments) so a resume never loses
        an ear row consumed just before a crash."""
        state_dir = self.run_root / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        tmp_base = state_dir / "organism_tmp"
        self.org.save(tmp_base)
        os.replace(str(tmp_base) + ".npz", str(state_dir / "organism.npz"))
        os.replace(str(tmp_base) + ".json", str(state_dir / "organism.json"))

        ledgers = build_ledgers(self.org, self.moment_word)
        predictor_last_winner = None
        if self.predictor is not None and self.predictor._last_winner is not None:
            predictor_last_winner = self.predictor._last_winner.tolist()      # A9: PREDICT's state (its last winner) lives in the mind and is saved in the snapshot (PREREG §11.1 step 1)
        ledger = {
            "last_seq": self.last_seq,
            "moment_word": {str(k): v for k, v in self.moment_word.items()},
            "moments": self.org.t,
            "ear_pending": dict(self.pending),
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: the SAME kind
            # of in-flight state as ear_pending above, same reason (a resume never loses an ear row
            # consumed just before a crash).
            "ear_pending_words": {k: list(v) for k, v in self.pending_words.items()},
            "sight": {str(k): sorted(v) for k, v in ledgers["sight"].items()},
            "words": {str(k): sorted(v) for k, v in ledgers["words"].items()},
            "predictor_last_winner": predictor_last_winner,
        }
        ledger_tmp = state_dir / "ledger_tmp.json"
        ledger_tmp.write_text(json.dumps(ledger))
        os.replace(str(ledger_tmp), str(state_dir / "ledger.json"))

        if self.episodes is not None:      # A9: FAST's episodes are saved with the snapshot (Episodes.save is already atomic: tmp + os.replace internally)
            self.episodes.save(state_dir / "episodes.npz")
        if self.outcome_episodes is not None:   # G5-K: the reflex ring — same class, same atomic save; never hashed (state_hash reads only org.c/cells/W)
            self.outcome_episodes.save(state_dir / "outcome_episodes.npz")

        self._last_snapshot_moments = self.org.t
        self.snapshot_count += 1

    def close(self) -> None:
        self.snapshot()

    @classmethod
    def resume(cls, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset()) -> Tuple["Mind", int]:
        """Load the latest snapshot (if any) and return (mind, last_seq). No snapshot -> a fresh mind, 0."""
        mind = cls(genome_path, run_root, blind=blind)
        state_dir = Path(run_root) / "state"
        npz, meta, ledger_path = state_dir / "organism.npz", state_dir / "organism.json", state_dir / "ledger.json"
        if npz.exists() and meta.exists() and ledger_path.exists():
            mind.org = Organism.load(state_dir / "organism", mind.genome)
            ledger = json.loads(ledger_path.read_text())
            mind.pending = dict(ledger.get("ear_pending", {}))
            mind.pending_words = {k: list(v) for k, v in ledger.get("ear_pending_words", {}).items()}
            mind.moment_word = {int(k): v for k, v in ledger.get("moment_word", {}).items()}
            mind._heard = {v for v in mind.moment_word.values() if v}     # PREREG §15: the heard-set, re-derived (never persisted separately)
            mind.last_seq = int(ledger.get("last_seq", 0))
            mind._last_snapshot_moments = mind.org.t

            # A9: `mind.predictor`/`mind.episodes` were built in __init__ against the PRE-load org/genome;
            # the predictor in particular closes over `org` by reference, so it must be rebuilt against
            # the LOADED org (a stale reference here would silently expect() off a dead, pre-resume
            # organism) -- caught by tracing the constructor, not by a test failure.
            if "PREDICT" in mind.genome.declared:
                # G5-E: _word_seen (arm "conjunctive") is NOT persisted (see genome/predict.py's module
                # docstring) — a resumed life restarts every word's count at 0. Out of scope for this
                # brief (replay-only); raised in G5-E-REPORT.md.
                mind.predictor = Predictor(mind.org, arm=mind.genome.declared["PREDICT"].get("arm", "novelty"))
                last_winner = ledger.get("predictor_last_winner")
                if last_winner is not None:
                    mind.predictor._last_winner = np.array(last_winner, dtype=np.float64)
            episodes_path = state_dir / "episodes.npz"
            if "FAST" in mind.genome.declared and episodes_path.exists():
                mind.episodes = Episodes.load(episodes_path)
            # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:08 +0400 — G5-K: the reflex ring reloaded the same
            # way; the per-act running expectation is NEVER itself persisted (advisor: "derive it from the dedicated
            # ring at resume, no separate persisted field") — rebuilt by replaying the ring's own live entries in id
            # (== temporal) order, x_s[0] read back as each entry's own "got" payload.
            outcome_path = state_dir / "outcome_episodes.npz"
            if ("OUTCOME" in mind.genome.declared or "SIT" in mind.genome.declared) and outcome_path.exists():
                mind.outcome_episodes = Episodes.load(outcome_path)
                mind._rebuild_act_expectation()
            if "SLEEP" in mind.genome.declared:
                every = int(mind.genome.declared["SLEEP"]["every"])
                mind._last_sleep_at = (mind.org.t // every) * every if every > 0 else 0

            return mind, mind.last_seq
        return mind, 0
