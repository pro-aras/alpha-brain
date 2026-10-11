# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:58 +0400 — A4L-COST (docs/briefs/A4L-COST.md; A4-LADDER-PREREG §2.1): the five hashed journal rows (the canvas row, a
# sight-only canvas, the coarse row, the epoch row, the sleep row) read `self.org.row_hash()` — the ONE per-row witness the genome
# declares (dense = the digest they always carried; sparse under HASH). This file still reads no clock: the organism times its witness.
# edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2 M3 (one hash per canvas): the coarse row now CARRIES its canvas row's digest
# (`_row_digest()` / `_coarse_row(digest=)`) instead of hashing the same state one statement later — four hashed rows are computed, five carried.
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

# edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5: `concurrent.futures` is a
# CONCURRENCY primitive, not a clock/randomness source — it is NOT in the determinism law's forbidden set
# (time, datetime, random, os.urandom; test_mind_has_no_clock's own AST sweep names exactly those four).
# The actual wall-clock read (timing a think's compute, timing a wait) lives in creature/think_thread.py,
# which this law does not bind; this file only ever does ARITHMETIC on the float ms numbers that module
# hands back (see _maybe_think_threaded/_think_apply_pending below).
import collections
import concurrent.futures
import hashlib
import inspect
import json
import os
import re
import shutil
import statistics
from pathlib import Path
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple

import numpy as np
from PIL import Image

from creature import genes as genes_module
from creature import think_thread
from genome import gaze
from genome.fast import Episodes
from genome.machinery import Genome, GenomeError, Organism, parse_genome, _unit
from genome.park import Park
from genome.predict import Predictor, file as predict_file, score as predict_score
from creature.tape import _resolve_tape_dir   # W3-0b seam: the mind reads payloads where the genome says the tape is
from genome.questions import build_ledgers, why as questions_why
from genome.sentence import find_frames
# edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:38 +0400 — A4L-LANG (A4-LADDER-PREREG §3.2): the composer/judge/thing-words (pure readers), called
# through the MODULE (`_chain.compose`, never a bare import) so a planted test double reaches the live branch.
from genome import chain as _chain
from genome.questions import word_cells
from genome.sleep import cycle as run_cycle, sleep as run_sleep
from genome.world import encode_word
from genome import web as _web
import traceback as _traceback

# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:37 +0400 — his 23:20 word («add all these features today so it runs for few days»): THE KNOWLEDGE WEB
# and THE SELF, live, as BOOKKEEPING (KW-1 / KW-2, docs/brain/memory/kweb/). A mind with a brain grows two webs from every heard word
# (L, and N the steered sprouts; WEB_BETA edges a known word; the spent consolidation test) and a self node from the brain's own turns
# and learns, with the claims placed below. Nothing is journaled; both ride in the snapshot (state/web.json). An error inside them
# switches them OFF and is shown (STATUS web_error, web/ERROR.txt); it never reaches the mind.
WEB_BETA = 10
WEB_REACH = 20
SELF_SHAPES = frozenset({"circle", "cross", "ring", "square", "star", "triangle"})


class SnapshotCrash(RuntimeError):
    """Raised only by the test hook `_crash_after_renames`: the process «dies» inside a snapshot's renames."""


# edit: Claude (Opus 5.5, the seat), 2026-09-29 23:54 +0400 — his 23:20 word; the days life's pre-flight died on a snapshot TORN by a kill (organism.* from
# moment 5,700, ledger.json from 5,200: every restart `KeyError: 5204`). A snapshot is now a GENERATION (see Mind.snapshot); a resume
# that finds its files disagreeing heals here BEFORE anything loads, and says so (repairs/REPAIRS.jsonl, and the body journals it).
def _fingerprint(p: Path) -> List[int]:
    s = p.stat()
    return [int(s.st_size), int(s.st_mtime_ns)]


def _generation_t(d: Path) -> Optional[int]:
    """The moment a state directory's generation stands at, or None when it is torn: with SNAPSHOT.json, EVERY file it lists must be
    there with the size and write time it recorded (a file renamed from another generation differs), and the organism, the ledger
    and the marker must name one moment; without it (a life saved before generations), the organism and the ledger must agree."""
    try:
        o = int(json.loads((d / "organism.json").read_text())["t"])
        l = int(json.loads((d / "ledger.json").read_text())["moments"])
        if not (d / "organism.npz").exists():
            return None
        if (d / "SNAPSHOT.json").exists():
            gen = json.loads((d / "SNAPSHOT.json").read_text())
            if int(gen["t"]) != o:
                return None
            for name, fp in (gen.get("prints") or {}).items():
                if not (d / name).exists() or _fingerprint(d / name) != list(fp):
                    return None
    except Exception:
        return None
    return o if o == l else None


def _heal_torn_snapshot(run_root: Path) -> Optional[Dict[str, object]]:
    from creature import repair as _repair
    st = Path(run_root) / "state"
    if not any((st / n).exists() for n in ("organism.npz", "organism.json", "ledger.json", "SNAPSHOT.json")):
        return None                                    # a life with no snapshot yet: nothing to heal
    if _generation_t(st) is not None:
        return None
    stamp = _repair._now().replace(":", "").replace("-", "")
    q = Path(run_root) / _repair.QDIR
    q.mkdir(parents=True, exist_ok=True)
    rec: Dict[str, object] = {"at": _repair._now(), "kind": "torn_snapshot", "file": "state", "offset": None, "bytes": None,
                              "nul_bytes": None, "lines": None, "sha256": None}
    prev = st / "prev"
    kept = q / f"state.torn.{stamp}"
    if prev.exists() and _generation_t(prev) is not None:
        kept.mkdir()
        names = json.loads((prev / "SNAPSHOT.json").read_text())["files"] + ["SNAPSHOT.json"]
        for n in names:
            if (st / n).exists():
                shutil.copy2(str(st / n), str(kept / n))
            if (prev / n).exists():
                os.replace(str(prev / n), str(st / n))
        rec.update({"restored": "prev", "t": _generation_t(st), "quarantine": str(kept.relative_to(run_root))})
    else:
        os.replace(str(st), str(kept))
        rec.update({"restored": "none: rebuilt from the tape", "t": None, "quarantine": str(kept.relative_to(run_root))})
    _repair._record(Path(run_root), rec)
    return rec


def _self_claims():
    """The memories about itself placed at birth (source implanted-knowledge, author the seat): KW-1's five (PREREG-KW-1 §4.3, verbatim)
    and one it had never been asked (B1: its own speed)."""
    a = "the seat"
    return [_web.Claim("T1", "I look at no more than four places on a canvas.", "always", 0.05, author=a),
            _web.Claim("T2", "The parent says at most one word of each kind at a time.", "always", 0.05, author=a),
            _web.Claim("T3", "Usually, what I expect is what the parent says.", "usually", 0.70, author=a),
            _web.Claim("F1", "I see every thing the parent names.", "always", 0.05, author=a),
            _web.Claim("F2", "The parent always says three words.", "always", 0.05, author=a),
            _web.Claim("B1", "My mind keeps up with what I sense.", "usually", 0.90, author=a),
            # PREREG-HEARS-2 §1: the new hand's claim, its truth unknown (B1's pattern); it gets no event in a life that never hears the maker
            _web.Claim("M1", "Usually, what I expect is what the maker names.", "usually", 0.70, author=a)]

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

# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1: the muse's
# pure machinery (the trigger, the content address, the declared constants). Pure functions only; no
# circularity (creature/muse.py imports nothing of the organism).
from creature import muse as _muse_mod
from creature.muse import MUSE_BUDGET, MUSE_INHIBIT, MUSE_STEPS

# edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB (F1) §1
# (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27): the content tokens. Pure
# functions only; no circularity (creature/contentweb.py imports nothing of the organism — the muse
# import's own form, above). genome/web.py is UNTOUCHED: the webs hear strings, as always.
from creature import contentweb as _cweb

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
# edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:48 +0400 — LIFE-D-ACT-SOUND.md item 3 (L-13;
# EAR.md §4's own TRAIT line): band 32 + onset-shape 4 + level 1.
SOUND_TRAIT_DIM = 37
# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md items 3/4
# (BODY-SENSES.md §4.5/§4.6): SENSE touch's own five fields (exit, rate, stalls, retries, bytes) and SENSE
# smell's own four (kind, size, folder, age) -- each gets a DEDICATED Episodes ring sized to its own trait
# dim, the same shape as sound_episodes above (never self.outcome_episodes, whose x_s is sight_dim()-wide
# with only x_s[0] used as a scalar payload -- a multi-number vector needs its own columns, or the toy
# "two programs ... give different touch VECTORS" (BODY-SENSES §4.6) has nothing to compare). Capacity: a
# code constant like OUTCOME_EPISODES_CAP above (no numeric parameter exists in either SENSE shape's fixed
# genome-text grammar) -- reused, not re-invented, since both this ring and the reflex ring carry the same
# order of traffic (one row per act, never one per glance).
TOUCH_TRAIT_DIM = 5
SMELL_TRAIT_DIM = 4
TOUCH_SMELL_EPISODES_CAP = OUTCOME_EPISODES_CAP

# edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:40 +0400 — ALPHA4-PREREG §4 AMENDED (§11 finding 1; branch
# judge-units-0923, HELD for alpha4-2). THE READINESS JUDGE's clause (a) in the units of its own null: success per COMPLETED
# EPISODE. The null is L-8's random worker, measured by G5-G (/data/dev/game-worlds/REPORT-G5-G.md §4.1: uniform over the 7
# acts, 100 episodes, seeds 101-200, max_steps 64 → success 0.29 per episode). A judge's number, sealed like the judge (§2),
# never a gene. The bound is COMPUTED from the three (never typed): 10 of 20.
READY_A_WINDOW = 20        # completed game episodes in (a)'s window — N, fixed and printed on every readiness row
READY_A_NULL = 0.29        # the random worker's success per episode (L-8's own figure)
READY_A_ALPHA = 0.05       # the null's one-sided band


def binomial_tail(n: int, p: float, k: int) -> float:
    """P(Binomial(n, p) >= k), exact (math.comb, fsum). Factored out of binomial_bound (below) so family_wise_bound
    (below) can share it — the same arithmetic, never retyped."""
    from math import comb, fsum
    return fsum(comb(n, j) * p ** j * (1.0 - p) ** (n - j) for j in range(k, n + 1))


def binomial_bound(n: int, p: float, alpha: float) -> int:
    """The smallest k with P(Binomial(n, p) >= k) <= alpha — the least number of successes in n trials that a policy no
    better than the null reaches with probability at most alpha. Exact; n + 1 when even k = n is not rare enough (never,
    for n >= 1 and p < 1). binomial_bound(20, 0.29, 0.05) == 10: P(X >= 10) = 0.0385, P(X >= 9) = 0.0948. This is the
    SINGLE-READING bound — right for a judge read ONCE, wrong for one read at every sitting on an overlapping window
    (see family_wise_bound and READY_A_BLOCK_K below, ALPHA4-2-PREREG §4.3)."""
    for k in range(n + 2):
        if binomial_tail(n, p, k) <= alpha:
            return k
    return n + 1


READY_A_BOUND = binomial_bound(READY_A_WINDOW, READY_A_NULL, READY_A_ALPHA)


# edit: Claude (Sonnet 5, judge builder B4), 2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3 (§0.4 finding 5; recommended
# by the designer, adopted by the orchestrator under Ahmad's 2026-09-05 delegation). THE FLAW: (a) was read at EVERY
# sitting on a SLIDING window of the last READY_A_WINDOW completed episodes (READY_A_BOUND computed above), so the 5%
# bound holds for ONE reading only; over a 24 h life (~30-45 sittings, each an overlapping window) a policy exactly at
# the null clears it somewhere ~23% of the time (six times the stated alpha) — a family-wise-error problem, #162/#215's
# class. THE FIX: (a) now reads DISJOINT blocks of READY_A_WINDOW completed mind-chosen episodes — block j = episodes
# 20j+1 .. 20j+20 in the order they completed (never overlapping) — against a HIGHER k chosen so the FAMILY-WISE rate
# over the blocks a 24 h life can complete at the null's pace stays under alpha.
def family_wise_bound(n: int, p: float, alpha: float, blocks: int) -> int:
    """The smallest k with the FAMILY-WISE rate over `blocks` independent disjoint n-trial blocks —
    1 - (1 - P(Binomial(n, p) >= k))**blocks — <= alpha. At the adopted parameters (20, 0.29, 0.05, 2) this is 11: the
    single-block tail at k=11 is 0.0132 (binomial_bound's own k=10 gives 0.0385), and the family-wise rate over the ~2
    blocks a 24 h life completes at the null's pace is 1-(1-0.0132)**2 = 0.0262 (k=10's family-wise rate, 0.0755, is
    ABOVE alpha — why k moved). A real function of the null (never a typed 11): family_wise_bound(20, 0.5, 0.05, 2) ==
    15, a different k at a different null."""
    for k in range(n + 2):
        family = 1.0 - (1.0 - binomial_tail(n, p, k)) ** blocks
        if family <= alpha:
            return k
    return n + 1


# The blocks a 24 h life completes at the null's pace: the game steps every 30 s (~2,880 steps/24h) and a policy at
# READY_A_NULL averages ~54 steps/episode (A4L-EXPLORE-TOY §3), so ~53 episodes/24h ~= 2 full 20-episode blocks
# (ALPHA4-2-PREREG §4.3's own words: "the blocks a 24 h life can complete (2 at the null's rate)"). Not a general
# claim about every success rate (a policy near the state-blind ceiling finishes episodes faster and completes MORE
# than 2 blocks/24h — §4.3's own table — which is why this constant is scoped to the null's own pace, the rate (a)'s
# false-positive risk is actually judged against).
READY_A_BLOCKS_PER_LIFE = 2
READY_A_BLOCK_K = family_wise_bound(READY_A_WINDOW, READY_A_NULL, READY_A_ALPHA, READY_A_BLOCKS_PER_LIFE)
# The SINGLE-BLOCK tail at k = READY_A_BLOCK_K (0.0132) — what `p_null_at_k` prints on every readiness row. Distinct
# from the FAMILY-WISE rate over READY_A_BLOCKS_PER_LIFE blocks (0.0262, computed above, never stored) that is the
# actual reason k = 11 was chosen over k = 10 — a single-block tail answers "how surprising is THIS block", the
# family-wise rate answers "how surprising is a life containing this block among others" (#162's unit-mismatch class:
# these are two different statistics and neither may stand in for the other unlabelled).
READY_A_BLOCK_P_NULL = binomial_tail(READY_A_WINDOW, READY_A_NULL, READY_A_BLOCK_K)


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


# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2
# (MOTOR-HANDS.md G-MOT-4): HANDS's declared `jail`/`shelf` values are paths RELATIVE TO A ROOT the genome
# text itself never names -- `jail` is a SIBLING of the worktree (/data/dev/alpha3/hands/jail_run), `shelf`
# is a directory INSIDE the worktree (world/programs/, never /data/dev/genome/world -- the brief's own
# words). `creature/mind.py` is directly under the worktree's `creature/` package, exactly like
# `creature/body.py` -- `Path(__file__).resolve().parents[1]` is the SAME "repo root" body.py's own
# `_declared_folder_dir` already resolves `WORLD`'s `folder` against; `.parents[2]` is one level up (the
# alpha3 tree's own parent), the ONLY root `alpha3/hands/jail_run` can resolve against without hardcoding
# `/data/dev` as a literal.
def _mind_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


# edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:28 +0400 — BRAIN-IN-BODY (docs/brain/body/INTERFACE-BRAIN-ORGAN.md §3/§4): the brain
# organ's class, imported LAZILY (only a genome that declares BRAIN, unblinded, ever calls this) so every other genome's Mind imports
# exactly what it always did. One function, so a test double reaches Mind.__init__ and Mind.resume alike.
def _brain_class():
    from genome.brain import Brain
    return Brain


# edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1: the scene hand's name and the derived seed of any other hand are the
# ORGAN's (genome/brain.py: SCENE_WORLD, world_seed_of); read lazily like the organ itself, so a tree without it still imports.
def _brain_scene_world() -> str:
    from genome.brain import SCENE_WORLD
    return SCENE_WORLD


def _brain_world_seed(seed: int, world: str) -> int:
    from genome.brain import world_seed_of
    return world_seed_of(int(seed), str(world))


def _jsonable(v):
    """numpy scalars/arrays → plain Python for the journal (json.dumps is bare there); ±inf/nan kept as floats (json writes
    Infinity, as the scored files hold it); no key or list is re-ordered."""
    if isinstance(v, dict):
        return {(k if isinstance(k, str) else str(_jsonable(k))): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return _jsonable(v.tolist())
    if isinstance(v, np.generic):
        return v.item()
    return v


# edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE): the
# genome a resumed Mind rebuilds from. `Mind._maybe_adopt_evolve_proposal` writes `GENOME.v<n>.genome` under
# `run_root` at every adoption; a process restart must rebuild from the HIGHEST such file, never from the
# caller's own (birth) `genome_path`, or every adopted mutation is silently undone the moment the mind
# process is restarted. `creature/replay.py` never calls `resume()` (it always starts a fresh Mind from
# birth and re-consumes the whole tape, including the 'proposal' rows that drove every adoption), so this
# function is read by `Mind.resume` only.
def _latest_evolved_genome(run_root: Path) -> Tuple[int, Optional[Path]]:
    """(0, None) when no GENOME.v<n>.genome exists under `run_root`; else (the highest n, its path)."""
    best_n, best_path = 0, None
    for p in Path(run_root).glob("GENOME.v*.genome"):
        m = re.fullmatch(r"GENOME\.v(\d+)\.genome", p.name)
        if m and int(m.group(1)) > best_n:
            best_n, best_path = int(m.group(1)), p
    return best_n, best_path


def _hands_paths(declared: Dict[str, dict]) -> Tuple[Optional[Path], Optional[Path]]:
    """(jail_path, shelf_dir) from declared['HANDS'], or (None, None) when HANDS is undeclared or declares
    only the SHORT form (jail, no shelf -- the pre-existing "HANDS jail <path>" grammar, test_parse_g4.py's
    own pin): a HANDS line with no shelf arms nothing here, exactly like a WORLD line with no folder arms
    no folder door (creature/body.py:_declared_folder_dir's own law)."""
    hands = declared.get("HANDS")
    if hands is None or "shelf" not in hands:
        return None, None
    jail_path = resolve_sibling(str(hands["jail"]))
    shelf_dir = _mind_repo_root() / str(hands["shelf"])
    return jail_path, shelf_dir


DEV_ROOT = Path("/data/dev")


def resolve_sibling(rel: str) -> Path:
    """edit: Claude (Fable 5.1), 2026-09-23 04:11 +0400 — a genome path written as a SIBLING of the tree (`alpha3/hands/jail_run`)
    resolves against the tree's parent when that exists, else against DEV_ROOT. Found by the pre-flight life
    alpha4-pre-1: a life's checkout lives at /data/dev/genome-lives/<life>/code, whose parent is genome-lives, not
    /data/dev — the hands read «no road» on all 11 of their thinks, 0 runs, 0 touch rows (a DECLARED-ONLY organ,
    exactly what his 23:08 rule forbids). Both resolvers (this one for the mind's think road, creature/body.py's
    for the sense) use this function so they can never disagree again."""
    first = _mind_repo_root().parent / rel
    if first.exists():
        return first
    second = DEV_ROOT / rel
    return second if second.exists() else first


# edit: Claude (Fable 5.1, the seat), 2026-09-29 12:59 +0400 — PREREG-WORD-ROAD §2: the declared genes HEAR may stand beside at STAGE 1.
HEAR_TWO_WORDS_COS = 0.875          # 7 of 8 letter slots shared: the largest cosine of two distinct words (WALK §C.3, measured)
HEAR_STAGE_1 = frozenset({"HEAR", "BRAIN", "ANSWER", "ARRIVAL", "ASK", "BODY", "CRASH", "DELIVER", "HEART", "TAPE", "THRESH",
                          "WORLD_SCENE"})


class Mind:
    """genome_path: the genome file (read once, text + parsed). run_root: the SAME root the body's Tape
    uses — payload bytes for a tape row live at run_root/tape/<row.payload>. blind: gene names this mind
    is blind to (e.g. {"gaze"} runs the random-gaze twin, PREREG §2.9's --blind gaze)."""

    def __init__(self, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset(), eye_front=None,
                 precision: bool = False, muse: bool = False, content_web: bool = False):
        self.genome_path = Path(genome_path)
        self.run_root = Path(run_root)
        self.genome_text = self.genome_path.read_text()
        self.genome: Genome = parse_genome(self.genome_text)
        self.blind = frozenset(blind)
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400 — PREREG-OPEN-WORLD-3 §1's ONE DECLARED
        # CHANGE: the innate video front (creature/senses/vfront.py) as a CONSTRUCTION PARAMETER — None (the default,
        # every existing caller) is byte-identical everywhere; wired, _consume_eye's ONE branch point (below) sends
        # every eye row's canvas through the front instead of the raw-frame feature path, and each eye row's journal
        # glance row gains §2.7's one additive `front` key. No genome edit, no parser edit, no machinery.py touch.
        self.eye_front = eye_front
        # edit: Kimi Code (K3, kimi-code, the seat alone), 2026-10-09 14:26 +0400 — PREREG-N1-PRECISION §1's wiring:
        # the precision flag as a CONSTRUCTION PARAMETER, threaded to both Predictor builds (the init below and the
        # resume-path rebuild); default False = byte-identical, no genome/parser/machinery.py touch (the OW-3 form).
        self.precision = precision
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1's wiring
        # (docs/brain/muse/PREREG-CONTEMPLATE-1.md, signed 2026-10-09 23:01): THE MUSE as a CONSTRUCTION PARAMETER —
        # default False = byte-identical, not one muse line runs (the N1 form; no genome/parser/machinery.py edit).
        # The state is inert data: the heard-sentence count (the budget), the content-addressed chain store, and the
        # skip counts (a trigger-negative sentence is counted, a budget-suppressed firing is journaled).
        self.muse = muse
        self._muse: Dict[str, object] = {"heard": 0, "chains_started": 0, "chains": {}, "skipped": {}}
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB (F1) §1's
        # wiring (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27): THE CONTENT WEB as a
        # CONSTRUCTION PARAMETER — default False = byte-identical (the webs hear ear rows only, exactly as
        # today; the N1/muse form; no genome/parser/machinery.py edit; nothing persisted beyond the web's own
        # existing state). The census is in-memory instrument data (per-sense token counts — the accounting
        # of the law's G-UNIT(d)/G-PLANT(i)), zeroed at every birth/resume and never snapshotted.
        self.content_web = content_web
        self._cweb_counts: Dict[str, int] = {s: 0 for s in _cweb.TOKEN_SENSES}

        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — W3-0 (docs/G4-WAVE3-CLAUSES.md):
        # THE GENERIC REFUSAL, first — before any object is built from the genome (a refusal message must
        # not be preceded by some other constructor's error). Every declared gene not in creature/genes.py's
        # RUNS registry (a real call site) refuses the organism by name; TRAITS's row is `None` (no
        # interpreter yet, PREREG §12/§14), which is why this single check now replaces that earlier
        # standalone `raise` — one law, not two.
        bad = genes_module.unwired(self.genome.declared)
        if bad:
            raise GenomeError(f"{', '.join(bad)} declared but nothing runs it (W3-0): the organism does not start")

        # L-4/L-7 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): BIND pools every one of
        # a canvas's feature vectors into ONE mean vector before Organism.moment() ever sees them
        # (_bind_pool, below) — SURPRISE's confirm= and the coarse glance's residual are both computed per
        # INDIVIDUAL feature, index-aligned with org_feats (_consume_eye, below), which BIND breaks by
        # construction (a pooled vector has no single glance a residual could be attributed to). Neither
        # combination has a mechanism — W3-0's own law, applied here explicitly rather than silently
        # falling back to confirm=False/no-coarse: BIND is #OFF in every genome that declares SURPRISE or
        # GAZE's coarse clause today (LIFE.genome), so this refuses nothing live, only an unbuilt combination.
        if "BIND" in self.genome.declared:
            if "SURPRISE" in self.genome.declared:
                raise GenomeError("BIND and SURPRISE both declared: SURPRISE's per-glance residual has no "
                                   "mechanism once BIND pools the canvas into one vector — the organism does not start")
            if "coarse" in (self.genome.gaze or {}):
                raise GenomeError("BIND declared with GAZE's coarse clause: BIND pools whatever org_feats "
                                   "holds, including the coarse glance, into one indiscriminate mean — the organism does not start")

        # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:3x +0400): the BARE old form
        # `SURPRISE floor <f>` (no `predicted mind-cell`) still parses — genome/machinery.py:275 sets
        # `declared["SURPRISE"] = {"floor": f}` regardless, on purpose, so every genome that already
        # carries the old line on disk (G5.genome:30, G4.genome:28, G5-nmax8000.genome:35 — all `#OFF`
        # today) keeps parsing byte-identically. G5.genome's own comment gives that bare line a DIFFERENT
        # intended meaning than this brief's mechanism: "a sense publishes when |actual − predicted| > floor
        # (V0.1's rule on every sense)" — a per-sense publish gate that was never built. Once creature/genes.py
        # names "SURPRISE" in RUNS["mind"] (added by this same brief, below), a bare declared SURPRISE would
        # pass genes_module.unwired() and silently run THIS mechanism instead of refusing — the exact trap
        # W3-0 exists to catch. So: SURPRISE is wired ONLY for the `predicted mind-cell` form; the bare form
        # has no consumer here and refuses by name, exactly as it did before this brief touched RUNS.
        if "SURPRISE" in self.genome.declared and self.genome.declared["SURPRISE"].get("predicted") != "mind-cell":
            raise GenomeError("SURPRISE floor declared without 'predicted mind-cell': no consumer names this "
                               "form (W3-0) — the organism does not start")

        # edit: Claude (Fable 5.1, the seat), 2026-09-29 12:59 +0400 — PREREG-WORD-ROAD §2: the gene HEAR, STAGE 1 = the lean body. An ALLOW-list:
        # HEAR starts only beside the genes whose consumers the law covers today (the genes of genome/brain/BRAIN-LEAN-TWIN.genome,
        # and BRAIN); beside any other declared gene, and beside `--blind ear` (the twin's own word bookkeeping is last-word),
        # the organism does not start — by name, so a consumer that was never widened cannot run by oversight.
        self._hear: bool = "HEAR" in self.genome.declared
        self.hear_words_refused: int = 0
        if self._hear:
            not_yet = sorted(k for k in self.genome.declared if k not in HEAR_STAGE_1)
            if not_yet:
                raise GenomeError(f"HEAR declared beside {', '.join(not_yet)}: its consumer does not meet every word yet "
                                   f"(HEAR stage 2, PREREG-WORD-ROAD §2) — the organism does not start")
            if "ear" in self.blind:
                raise GenomeError("--blind ear beside HEAR: the blind twin's ledger and arrival clock read ONE word "
                                   "(HEAR stage 2, PREREG-WORD-ROAD §2) — the organism does not start")
            # edit: Claude (Fable 5.1, the seat), 2026-09-29 13:13 +0400 — the co-signer's note on §2: the law's own facts rest on three PARSED
            # FIELDS outside `declared`, so the fence covers them too, each by name. Two distinct words of 8 letter slots have
            # cosine <= 7/8: a words floor at or under it lets two words light ONE cell (§1.5's «the word that lit it», §1.9's
            # decode); the decode reads the 27-symbol code.
            floor = self.genome.theta_words if self.genome.theta_words is not None else self.genome.theta_n
            if float(floor) <= HEAR_TWO_WORDS_COS:
                raise GenomeError(f"HEAR declared beside a words floor of {floor}: two words can light one cell at or under "
                                   f"{HEAR_TWO_WORDS_COS} (PREREG-WORD-ROAD §2) — the organism does not start")
            if int(self.genome.ear_letters) != 8:
                raise GenomeError(f"HEAR declared beside SENSE ear letters {self.genome.ear_letters}: the law is measured at 8 "
                                   "(PREREG-WORD-ROAD §2) — the organism does not start")
            if self.genome.ear_blank_zero:
                raise GenomeError("HEAR declared beside SENSE ear … blank=zero: no life was ever lived under that code "
                                   "(HEAR stage 2, PREREG-WORD-ROAD §2) — the organism does not start")

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
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:48 +0400 — LIFE-D-ACT-SOUND.md item 3 (L-13):
        # a THIRD, separate Episodes ring for ear-sound events (37-wide: EAR.md §4's TRAIT line, band 32 +
        # onset-shape 4 + level 1) -- never self.episodes (dims differ) and never fed to SLEEP's org.moment
        # replay (K's own hazard for outcome_episodes above applies identically: a zero sight vector would
        # birth a garbage cell). Gated on FAST declaring the "sound" key (genome/machinery.py's parser);
        # cap reuses FAST's own declared episode count (the same gene's cap parameter, a separate ring
        # instance). x_w is a single unused slot (sound has no word dimension).
        self.sound_episodes: Optional[Episodes] = (
            Episodes(int(self.genome.declared["FAST"]["episodes"]), SOUND_TRAIT_DIM, 1)
            if ("FAST" in self.genome.declared and "sound" in (self.genome.declared["FAST"].get("keys") or []))
            else None
        )
        self.sound_events: int = 0
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:32 +0400 — A4L-VOICE: the maker's sound rows held until
        # their canvas's eye row (moment -> {"trait", "seq"}), and two counts on STATUS on every write (#164): maker sound rows
        # consumed (`voice_rows`) and bound at a canvas (`voice_bound`) — a voice that is heard but never bound is the finding.
        self.pending_sound: Dict[str, Dict[str, object]] = {}
        self.voice_rows: int = 0
        self.voice_bound: int = 0
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
        # items 3/4: touch/smell's own dedicated rings (see the module-level comment on TOUCH_TRAIT_DIM
        # above for why they are not self.outcome_episodes). Gated on their own SENSE_TOUCH/SENSE_SMELL
        # declared presence, matching sound_episodes' own gate one line up.
        self.touch_episodes: Optional[Episodes] = (
            Episodes(TOUCH_SMELL_EPISODES_CAP, TOUCH_TRAIT_DIM, 1) if "SENSE_TOUCH" in self.genome.declared else None
        )
        self.smell_episodes: Optional[Episodes] = (
            Episodes(TOUCH_SMELL_EPISODES_CAP, SMELL_TRAIT_DIM, 1) if "SENSE_SMELL" in self.genome.declared else None
        )
        self.touch_events: int = 0
        self.smell_events: int = 0
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
        # item 2 (L-12): HANDS's own choosing state. `_hands_jail_path`/`_hands_shelf_dir`: None unless
        # HANDS declares the full form (jail + shelf) -- see _hands_paths' own docstring. `_hands_rng`: its
        # own stream, distinct from every other rng here (resume-safe, its bit_generator state lives in
        # the snapshot -- see snapshot()/resume() below, mirroring `_act_rng`'s own pattern). `_hands_
        # pending`: the outstanding choice awaiting its own outcome row (None <=> the "hands" pool item may
        # be chosen again; not None <=> a run is in flight, so the pool never offers a SECOND choice before
        # the sense thread has answered the first -- #175's law for a choice that must not be doubled).
        # `_hands_last_program`: the most recently CHOSEN program name (for the 10% re-run draw, L-12's own
        # words: "so the positive control fires"). `runs_chosen`: one count PER PROGRAM (G-MOT-1's census
        # shape, never a total, #165). `hands_no_road`: the jail binary was missing when a 'hands' item was
        # worked -- journaled by name each time (dead_end's own mechanism), counted here for STATUS.
        self._hands_jail_path, self._hands_shelf_dir = _hands_paths(self.genome.declared)
        self._hands_rng = np.random.default_rng([int(self.genome.seed), 0x48414e44])   # "HAND" bytes-ish
        self._hands_pending: Optional[Dict[str, object]] = None
        self._hands_last_program: Optional[str] = None
        self.runs_chosen: Dict[str, int] = {}
        self.hands_no_road: int = 0
        self._act_expected: Dict[str, float] = {}     # act -> running mean of past "got" values (the PREDICTION; #175)
        self._act_n: Dict[str, int] = {}               # act -> count backing the running mean
        # merge (Claude (Fable 5.1), g5-integration): K's ring above + E's arm-aware Predictor below — both kept.
        # G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md): the arm name lives on the genome's PREDICT
        # clause (machinery.py's parser, default "novelty" when the genome's PREDICT line carries no
        # trailing "; error <arm>" — every genome on disk before this edit, G4.genome included).
        self.predictor: Optional[Predictor] = (
            Predictor(self.org, arm=self.genome.declared["PREDICT"].get("arm", "novelty"), precision=self.precision)
            if "PREDICT" in self.genome.declared else None
        )
        self._last_sleep_at: int = 0        # org.t at the last SLEEP boundary crossed
        # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE):
        # the latest not-yet-adopted PASS proposal (a dict: no/epoch/gene/value/mutant_genome_text/…), None
        # when there is none or the last one seen was already adopted (_consume_proposal/_maybe_adopt_
        # evolve_proposal below). `evolve_epoch`: how many adoptions this Mind has lived through (0 = the
        # birth genome, unmutated) — stamped on the epoch journal row and on GENOME.v<n>.genome's own name;
        # `resume()` below restores it from the highest such file already on disk, never from a counter.
        self._evolve_pending_proposal: Optional[Dict[str, object]] = None
        self.evolve_epoch: int = 0
        self.evolve_proposals_seen: int = 0

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
        # edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5 (docs/briefs/LIFE-E-THINK-THREAD.md;
        # PREREG §19.2): THINK on its own thread. `_think_threaded` reads the genome's own flag (absent -> False,
        # byte-identical to today -- genome/machinery.py's own comment on the parser change). The executor is built
        # ONLY when threaded (a genome that never asks for this starts no extra thread, ever) -- one worker, so at
        # most one think is ever in flight, matching the brief's own "launch at N, apply at N+every" pipeline (never
        # more than one boundary's worth of work outstanding at a time, `THINK.every` >= 1 canvas apart). `_think_
        # pending` holds the ONE outstanding launch (its Future, the boundary N it was launched at, and the chosen
        # item) between the boundary that launched it and the boundary that applies it -- never persisted in
        # snapshot()/resume() (a resumed or replayed mind is a FRESH Mind, so there is never a pending think to
        # restore; a crash between launch and apply loses that one think's result, same class of gap as
        # _filed_predictions/Park/Interests not being persisted either, named in the report). `think_waits`/
        # `think_wait_ms` (cumulative) and `_think_ms_history` (capped, for a running median) are exported on
        # STATUS via creature/body.py's existing `getattr(self.mind, ...)` pattern -- this file computes ZERO wall-
        # clock reads itself (creature/think_thread.py's `worker_run`/`wait_for` measure think_ms/wait_ms and hand
        # back plain floats; this file only ever does arithmetic on them, per the determinism law's own comment
        # above the concurrent.futures import).
        self._think_threaded: bool = "THINK" in self.genome.declared and bool(self.genome.declared["THINK"].get("threaded"))
        self._think_executor: Optional[concurrent.futures.ThreadPoolExecutor] = (
            concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="think") if self._think_threaded else None
        )
        self._think_pending: Optional[Dict[str, object]] = None
        self.think_waits: int = 0
        self.think_wait_ms: float = 0.0
        self.think_ms_last: Optional[float] = None
        # edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2 M5: the freeze (before the launch) and the apply (the
        # ONE-WRITER's real writes) land on the MIND thread and `think_ms` (decide() on the frozen copy) never saw them; both are timed
        # by creature/think_thread.py (this file reads no clock — test_mind_has_no_clock), the last value of each exported by
        # creature/body.py:_build_status as think_freeze_ms / think_apply_ms on every STATUS write (#164). None until the road runs.
        self.think_freeze_ms_last: Optional[float] = None
        self.think_apply_ms_last: Optional[float] = None
        self._think_ms_history: List[float] = []
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:52 +0400 — LIFE-D-ACT-SOUND.md item 2
        # (L-8): the game's own act-choosing policy. `_act_policy_on` is the SAME gate creature/body.py's
        # `_game_act_file_path` reads (creature.senses.game.mind_drives_acts), computed once here so a
        # genome that never declares ACT's turn+step verbs touches none of this (byte-identical to before,
        # G4-8's own law). `_act_rng`: its own stream, distinct from `_think_rng`/CURIOSITY's/the
        # organism's — resume-safe (its bit_generator state lives in the snapshot, see snapshot()/resume()
        # below). `_act_choices`: seq (the eye row that triggered the choice) -> {"idx","name"}, popped by
        # the matching outcome row's own act_seq (#175: the mismatch check compares against the CHOICE
        # that produced THIS row, never merely "the last one made" — eye_k chooses for outcome_k, but by
        # the time outcome_k arrives the mind may already have chosen for eye_{k+1}).
        from creature.senses.game import mind_drives_acts as _mind_drives_acts
        self._act_policy_on: bool = _mind_drives_acts(self.genome.declared)
        self._act_rng = np.random.default_rng([int(self.genome.seed), 0x4143544d])   # "ACTM" bytes-ish
        self._act_choices: Dict[int, Dict[str, object]] = {}
        self.acts_chosen: Dict[str, int] = {}
        self.act_mismatches: int = 0
        # edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:59 +0400 — docs/A4-LADDER-PREREG.md §2.5 (A4L-EXPLORE): the
        # declared VALUE law of the game act chooser (`ACT value reward <n>; optimism <f>` → declared["ACT_VALUE"]); None →
        # the outcome-weighted law, byte-identical. `act_policy`/`act_weights`/`act_explored`: the law the last choice used,
        # its weights as journaled, and the choices drawn by the 10 % uniform branch — STATUS on every write (#164), never
        # read by the mind itself (the journal is unchanged by them).
        self._act_value: Optional[Dict[str, object]] = self.genome.declared.get("ACT_VALUE")
        self.act_policy: Optional[str] = None
        self.act_weights: Optional[List[float]] = None
        self.act_explored: int = 0
        self._canvas_index: int = 0
        # edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2 M3 (one hash per canvas): `_row_digest()` records the
        # moment count its digest witnessed; `_coarse_row` reuses the canvas row's digest only while `org.t` still equals it, else
        # REFUSES (recomputes) and counts here — 0 on every live road (tests/creature/test_a42_b1.py's seam scan pins that nothing
        # between the two rows touches the organism); a test's planted moment between them makes it 1. Not on STATUS: a counter that
        # can only read 0 on a live body is not printed (tools/lives/check.py's own rule).
        self._row_digest_t: int = -1
        self.hash_reuse_refused: int = 0
        self._filed_predictions: list = []          # [{"row": FILE's row dict, "due_canvas": int}, ...] awaiting the next showing of their word
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2 (docs/G4-WAVE3-CLAUSES.md):
        # words/pairs with a currently FILED-but-not-yet-SCORED rule, so _think_pool never re-files the
        # SAME rule twice while its first attempt is still pending (removed once scored, whether PASS or
        # FAIL, so a word/pair may be re-attempted later — up to PARK's own n identical fails). Not
        # persisted in snapshot() (pre-existing gap, shared with _filed_predictions/Park/Interests — see
        # the builder report).
        self._induce_pending: set = set()            # words
        self._deduce_pending: set = set()             # "w1|w2" (sorted) pair keys
        # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): SURPRISE's per-glance counters
        # (STATUS's own two, creature/body.py) and "no think-pool item" for a CONFIRMED glance -- an episode
        # id whose glance 0 was confirmed, skipped by _think_pool()'s two FAST-episode loops below. Additive:
        # the episode is still WRITTEN (SLEEP's most_surprising(), the episodic PREDICT arm and "ep" on the
        # journal row are all untouched -- the alternative, skipping the FAST write itself, was raised and
        # not built: its blast radius reaches those three mechanisms, this narrower fix reaches only THINK).
        # NOT persisted at resume -- same class of gap as _induce_pending/_deduce_pending/_filed_predictions
        # immediately above/below (raised, not built; replay is a fresh Mind every time, so the tape road
        # this brief owns is unaffected).
        self.glances_confirmed: int = 0
        self.glances_surprised: int = 0
        # edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md §2.4
        # (docs/briefs/A4L-DROP.md task 5): every glance actually DROPPED (never reached Organism.moment()
        # at all — the "; drop confirmed" clause's own cheap moment, one call to Organism.tick() instead).
        # 0 forever when "drop confirmed" is undeclared (byte-identical to before this task, same class of
        # gap as glances_confirmed/glances_surprised immediately above — NOT persisted at resume, see the
        # comment on those two).
        self.glances_dropped: int = 0
        self._confirmed_episodes: set = set()
        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:05 +0400 — D-G12/W3-1 (docs/G4-WAVE3-CLAUSES.md):
        # revisits/extensions/clashes, coded against Builder B's believe() "kind" interface before it lands
        # (today believe() always returns kind="belief"; the mapping below already handles the other three).
        self.think_counters: Dict[str, int] = {
            "thinks": 0, "parked": 0, "beliefs": 0, "revisits": 0, "extensions": 0, "clashes": 0,
            "predictions_filed": 0, "predictions_scored": 0,
            # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF (docs/briefs/LIFE-A-ANSWER-SELF.md
            # #3): on STATUS from the FIRST write (#164's law: a new counter is on STATUS on every branch that
            # writes STATUS, never only once it first moves) via _build_status's existing `**think_counters` spread.
            "think_skipped_for_backlog": 0,
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11 (docs/briefs/
            # LIFE-C-QUESTION-SENTENCE.md): a new counter goes on STATUS on every branch that writes STATUS
            # (#164) — creature/body.py's STATUS loop already unpacks every key of this dict unconditionally.
            "questions_written": 0, "questions_answered": 0,
            "frames_filed": 0, "frames_scored": 0, "frames_true": 0,
            "said": 0, "heard_yes": 0, "heard_no": 0,
        }
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF: the body sense's last TWO
        # readings (seq, reading dict), oldest first, truncated to 2 -- the pair a "self" think item compares.
        # `_last_body_reading` is the SINGLE most recent one, read by `_maybe_think`'s backlog-skip gate (never
        # the live queue -- G-MIND-6's trap and its twin, in one rule: a replay reads the same recorded number
        # and decides the same). `_self_worked_seq` is the seq of the latest body row a "self" item has already
        # compared, so the SAME pair is never re-added to the pool on every THINK boundary between body rows
        # (#232's "starved by a kind that always wins" class, one level down: an item that never leaves the
        # pool once worked would crowd out every other kind at every future boundary). Neither is in the
        # snapshot (a pre-existing gap this class shares with `_filed_predictions`/Park/Interests -- named in
        # the builder report, not fixed here).
        self._body_pair: List[Tuple[int, dict]] = []
        self._last_body_reading: Optional[Dict[str, object]] = None
        self._self_worked_seq: Optional[int] = None
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — the coordinator's fix
        # (docs/briefs/LIFE-A-REPORT.md §3 clause 6's finding: the backlog-crossing trigger and the backlog
        # skip read the same field/threshold, so the skip always preempts the boundary that would file it):
        # "I am behind" is filed at the FIRST think that RUNS after a run of skips, not at a comparison --
        # so it is tracked here across skips, never inside `_self_trigger`.
        # `_skip_run_seqs`: the seq of the body row each skip in the CURRENT run read (may repeat if two
        # skips share one body row); `_skip_run_skips`/`_skip_run_max_backlog`: K and N for the sentence.
        # Reset to empty/0/None once the run's belief is filed. Read from RECORDED body rows only (never
        # the live queue), same as the skip itself, so a replay decides identically (G-MIND-6's twin).
        self._skip_run_seqs: List[int] = []
        self._skip_run_skips: int = 0
        self._skip_run_max_backlog: Optional[int] = None
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
        # edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:05 +0400 — A42-B2 PART 2 (ALPHA4-2-PREREG §2.5 "B2 birth-source
        # ledger"): the words heard while a PICTURE-source canvas (genome/chain.py:PICTURE_SOURCES) was shown, first-heard order,
        # each once, ONLY GROWING — written in _consume_eye from the eye row's own `meta["source"]` and the instant's (post-blind)
        # words, the same two facts FAST's ring keeps per episode, so before the ring wraps `set(picture_words) ==
        # chain.heard_on_pictures(episodes)` exactly (proven on the hour-1 fixture, A42-B2-REPORT) and after it the ledger still
        # holds what the ring evicted (≈ hour 11.6 of a 24 h life). A LEDGER, like moment_word: persisted in the snapshot's
        # ledger.json (never org.c, never the births log — both hashed), restored by resume(); read by chain.thing_words(rule=
        # "ledger", THING_WORD_RULE since 17:5x) through _chat_content, the ring rule and the twin printed beside it on the say
        # row. A snapshot from before this key resumes EMPTY, never back-filled from the ring.
        self.picture_words: List[str] = []
        self._picture_words_set: set = set()
        # The OTHER half of the same attribution (the PREREG's own name for B2, "the birth-source ledger"): sight cell -> the
        # source of the canvas it was FIRST born on ("sleep" for a birth inside the sleep replay), written at the birth, on the
        # three roads that birth (the worded canvas, the sight-only canvas, the sleep step). chain.birth_sources() derives the same
        # map from the RING (a birth older than the oldest live episode reads "?" — so after the wrap even the LITERAL set forgets
        # the picture-born cells; the toy's control shows it); this ledger is what rule "ledger" reads instead. Agreement with the
        # ring on the hour-1 fixture: every sight cell, A42-B2-REPORT.
        self.birth_source: Dict[int, str] = {}
        self.last_seq: int = 0
        self.sight_only_skipped: int = 0
        self.journal_rows_written: int = 0
        self.snapshot_count: int = 0
        self.sleep_count: int = 0                        # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — STATUS.sleeps (PREREG §11.1 step 4)
        # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — the standalone TRAITS refusal that
        # lived here is now one row of the generic refusal above (creature/genes.py RUNS["mind"]["TRAITS"] = None),
        # checked immediately after parse_genome, before this point is ever reached.
        self._last_snapshot_moments: int = 0

        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §3/§4: THE
        # STAGE and its readiness judge. `self.stage` starts at the highest MOMENTS-based STAGE this
        # genome declares whose lower bound org.t has already reached (`_moments_stage()`, below) -- a
        # fresh Organism starts at t=0, so this reads 1 here; `consume()` recomputes it on every row
        # (org.t only ever increases, so this is a monotonic, idempotent refresh, exactly like
        # `stage2_start` is already recomputed from the genome on demand). A "by READY" stage (STAGE_READY
        # declared) is committed permanently by `_maybe_advance_stage` once §4 (a)-(e) all hold on ONE
        # readiness reading at an EXAM boundary (edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:40 +0400 — §4
        # AMENDED: the streak defined once; each clause spans its own horizon, so the old «two consecutive»
        # counter, `_stage_ready_streak`, is gone) -- "never undone by the mind" (the brief's own words): nothing
        # here ever LOWERS self.stage.
        self.stage: int = self._moments_stage()
        # (d): the seat's grades (`grade` tape rows, creature/senses/grade.py) -- ALL of them (since
        # birth, the PREREG's own words), plus the RIGHT flag of the last 10 flagged `novel` (a picture
        # this mind had never seen; "right" there means "correctly said I don't know", the grade
        # schema's own meaning for a novel item — SENSE_GRADE's own docstring).
        self._grades_total: int = 0
        self._grades_right: int = 0
        self._novel_grades: "collections.deque[bool]" = collections.deque(maxlen=10)
        # (e): the hold flag, from `hold` tape rows (the SAME grade sense, on every change, including the
        # very first observation — creature/senses/grade.py's own docstring).
        self._hold_active: bool = False
        # (a) (edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:40 +0400 — §4 AMENDED: per EPISODE, never per act;
        # edit: Claude (Sonnet 5, judge builder B4), 2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3: DISJOINT blocks, never
        # a sliding deque). Three fields replace the old sliding `_game_episodes` deque:
        #   _game_last_episode_step: the (episode, step) of the last COUNTED terminal row — the dedup guard the deque's
        #     own [-1] used to serve (a sense restart between a publish and its cursor write re-publishes that step,
        #     #230's cursor law; the SAME row twice must count once).
        #   _game_block_n / _game_block_successes: episodes counted toward the block CURRENTLY being filled (0..19) and
        #     its successes so far. Meaningful only before the FIRST block ever completes — once any block has, these
        #     reset to 0 after each completion and are never read for the reported (a) numbers again (the reading pins
        #     to _game_last_block below; #180's law: a value computed is not a value read unless something reads it).
        #   _game_last_block: the latest COMPLETE block, {"block_index": int, "successes": int} — locked in the instant
        #     it completes (in _consume_outcome), never mutated again except to be REPLACED wholesale when the NEXT
        #     block completes ("a block once read is never re-read with a different verdict", §4.3).
        # All persisted in the snapshot ledger (game_last_episode_step/game_block_n/game_block_successes/game_last_block)
        # so a resumed mind reads the same blocks (replay purity) — see snapshot()/resume() below.
        self._game_last_episode_step: "Optional[Tuple[object, object]]" = None
        self._game_block_n: int = 0
        self._game_block_successes: int = 0
        self._game_last_block: "Optional[Dict[str, int]]" = None
        # (c): the last TWO `sit` rows' (score, composite) pairs -- `score` is the existing SIT payload
        # (Q1's own accuracy, `creature/senses/sit.py`'s own `_score_of`); `composite` is a NEW field that
        # module's `sense()` gains in this same brief (`_composite_of`) so this judge can read §4(c)'s
        # OTHER number from tape facts too — an older `sit` row (before that field existed) carries no
        # `composite` key, read as None, which fails (c) honestly rather than fabricating a pass.
        self._sit_readings: "collections.deque[tuple]" = collections.deque(maxlen=2)
        # (b)'s read half was RAISED when this judge landed and RESOLVED at integration (the sitter's `read_share`, a
        # TAPE FACT on the SIT row). edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:40 +0400 — the test-only
        # `_read_proxy_override` that let a test force this door clause True is REMOVED (a production attribute that can
        # force an internet-door clause is #180's class); tests feed SIT rows that carry `read_share` instead.
        # WEB (I): fetch/refusal counters from `web` tape rows (creature/senses/web.py) — on STATUS on
        # every branch (#164), and the hold flag above doubles as STATUS.web_hold (the SAME `_hold_active`
        # (e) reads — one fact, one name, never two counters that could disagree, #180).
        self.web_fetches: int = 0
        self.web_refused_rate: int = 0
        self.web_refused_hold: int = 0
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:38 +0400 — A4L-LANG task 10: the chat counters (STATUS's ten chat keys via
        # creature/body.py:_chat_status, on every write — #164). Present on EVERY Mind (zeros unless CHAT is declared).
        self.chat_counters: Dict[str, int] = {"chats": 0, "answered": 0, "abstained": 0, "refused_form": 0,
                                               "refused_content": 0, "words_total": 0, "longest": 0,
                                               "graded": 0, "graded_right": 0, "graded_novel": 0}

        # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:28 +0400 — BRAIN-IN-BODY (INTERFACE §4): the brain, a NEW consumer beside
        # MEET (it replaces nothing). None without a BRAIN line or under `--blind brain` (the twin: the asks go to the organs' road).
        # `pending_asks`: moment -> the asks held for that moment's eye row, in tape order (saved in the snapshot like ear_pending).
        # `asks_answered`/`asks_by`: counts for STATUS (brain_status). A BRAIN line whose organ is not on this tree refuses BY NAME.
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 20:56 +0400 — PREREG-ALPHA-6 §1.3/§2 B1 (the law SIGNED;
        # SEAT-LINE sha256 1d00a35f…): the MOUTH line's OPTIONAL word «incremental», read here ONCE and handed to the brain at
        # EVERY construction below (the birth, the inheritance, and the resume at Mind.resume) — a construction parameter,
        # never a BRAIN gene value (the W1 «brain» clause's own read at self._voice, below, is the pattern). ABSENT: False,
        # the old mouth, byte-identical everywhere.
        self._mouth_incremental: bool = bool((self.genome.declared.get("MOUTH") or {}).get("incremental"))
        self.brain = None
        self.brain_restored: Optional[bool] = None
        if "BRAIN" in self.genome.declared and "brain" not in self.blind:
            try:
                brain_cls = _brain_class()
            except ImportError as e:
                raise GenomeError(f"BRAIN declared but genome/brain.py cannot be imported ({e}): the organism does not start")
            self.brain = brain_cls(dict(self.genome.declared["BRAIN"]), mouth_incremental=self._mouth_incremental)
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 20:35 +0400 — PREREG-INHERIT §3: a root that holds inherit/brain.json|npz gives the NEWBORN its
        # parent's brain (the learner and the aligned lists; the cited episodes emptied). With no pair this is the old birth,
        # untouched. `brain_inherited` is STATUS's; the one journal row is written before the life's first row is consumed.
        self.brain_inherited: Optional[Dict[str, object]] = None
        self._inherit_row_due = False
        _pair = self.run_root / "inherit" / "brain"
        if self.brain is not None and (Path(str(_pair) + ".json").exists() or Path(str(_pair) + ".npz").exists()):
            try:
                self.brain, self.brain_inherited = brain_cls.inherit(_pair, dict(self.genome.declared["BRAIN"]),
                                                                     mouth_incremental=self._mouth_incremental)
            except Exception as e:
                raise GenomeError(f"{e} (root {self.run_root})")
            self._inherit_row_due = True
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 20:52 +0400 — PREREG-METADATA-1 §2: the scenes this life learns carry its own name as author.
        if self.brain is not None:
            self.brain.author = self.run_root.name
        # the KNOWLEDGE WEB and the SELF (his 23:20 word; bookkeeping, above WEB_BETA): only a mind with a brain grows them
        self.webs: Optional[Dict[str, object]] = None
        self.self_node = None
        self.web_error: Optional[str] = None
        self.web_restored: Optional[bool] = None
        self.snapshot_heal: Optional[Dict[str, object]] = None     # set by resume() when a torn snapshot was healed
        self._crash_after_renames: Optional[int] = None            # a TEST hook: «die» after this many renames of a snapshot
        self._self_kinds: Tuple[int, Optional[List[set]]] = (-1, None)
        if self.brain is not None:
            try:
                self.webs = {r: _web.Web(r, beta=WEB_BETA, seed=int(self.genome.seed), spend="harmonic", reach=WEB_REACH,
                                         author=self.run_root.name) for r in ("L", "N")}
                self.self_node = _web.SelfNode(author=self.run_root.name)
                for c in _self_claims():
                    self.self_node.place(c)
            except Exception as e:           # pragma: no cover — a construction bug must not stop a life
                self._web_fail(e)
        self.pending_asks: Dict[str, List[Dict[str, object]]] = {}
        self.asks_answered: int = 0
        self.asks_by: Dict[str, int] = {"brain": 0, "organs": 0}
        self.brain_learned: int = 0
        self.brain_refused: int = 0
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 16:28 +0400 — PREREG-BRAIN-DRIVES §2.1 / §2.4: the gene DRIVE. The brain takes its TURN at
        # every canvas it hears, before it hears. Refused BY NAME beside no BRAIN line (a turn needs a brain); under `--blind brain`
        # there is no brain and no turn (the twin). The counts are STATUS's and the snapshot's, written only under the gene.
        self._drive: Optional[Dict[str, int]] = self.genome.declared.get("DRIVE")
        if self._drive is not None and "BRAIN" not in self.genome.declared:
            raise GenomeError("DRIVE declared beside no BRAIN line: the turn is the brain's (PREREG-BRAIN-DRIVES §2.1) — "
                               "the organism does not start")
        self.brain_turns: Dict[str, int] = {"turns": 0, "said": 0, "asked": 0}
        # edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 18:35 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §2 (the law SIGNED x3 at
        # toys-1003 1ccc3bf; the VERIFIER's NOTE-1 binds): the MOUTH line's OPTIONAL clause «and the brain's phrase per canvas». The
        # clause declared beside no DRIVE line is refused BY NAME («the phrase is the DRIVE turn's», the form of the DRIVE-beside-no-
        # BRAIN refusal above; DRIVE already refuses beside no BRAIN). "voiced" is INITIALISED at construction, ONLY under the clause
        # (every other ledger is what it was): the snapshot saves dict(self.brain_turns) unconditionally and the resume restores only
        # the keys present here, so a resumed life keeps its voiced count. The voice row itself is written at the DRIVE turn site.
        self._voice: Optional[str] = (self.genome.declared.get("MOUTH") or {}).get("brain")
        if self._voice is not None and "DRIVE" not in self.genome.declared:
            raise GenomeError("MOUTH's brain clause declared beside no DRIVE line: the phrase is the DRIVE turn's "
                              "(PREREG-W1-MOUTH-VOICES-BRAIN §2) — the organism does not start")
        if self._voice is not None:
            self.brain_turns["voiced"] = 0
        # edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 23:4x +0400 — PREREG-EYE-1 §2 (THE CHOSEN LOOK, signed):
        # the loop's return arrow. None = OFF (every organism caller, byte-identical); the bench instrument
        # (tools/brain/look_diff.py) sets it after construction. When set: after the DRIVE turn, a leading hypothesis
        # holding NO word (the turn's own doubt) gets ONE forced glance at its locus, the brain's eye row is re-fed,
        # the turn is re-read on it, and the learn runs on the re-read state. Never a genome line of this law's own
        # (the rung's law carries it); the cells' road is untouched.
        self._look: Optional[Dict[str, object]] = None
        # PREREG-HEARS-2 §1: per hand other than the scene world, the count of canvases the brain learned from it (its derived scene
        # index); rebuilt from the brain's own `worlds` at a resume (_restore_brain_world_count), counted as it goes in a replay.
        self._brain_world_count: Dict[str, int] = {}
        # edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:39 +0400 — PREREG-INNER-1 §2 + AMENDMENT 1 A3 (research-1003 @ 9c589b2; the signed text
        # sha256 857e07b2…faa82): the gene INNER — THE INNER TURN, the brain's thought about a REMEMBERED scene when the body has spare
        # capacity (a SENSE body row with backlog 0). Refused BY NAME beside no BRAIN line (the turn is the brain's) and beside no SENSE body
        # line (its trigger row is consumed only under SENSE_BODY, _consume_body's own gate). Under `--blind brain` there is no brain and
        # every body row is counted «no brain». The chain state (ledger["inner"]) and the counts are written only under the gene.
        self._inner: Optional[Dict[str, object]] = self.genome.declared.get("INNER")
        if self._inner is not None and "BRAIN" not in self.genome.declared:
            raise GenomeError("INNER declared beside no BRAIN line: the inner turn is the brain's (PREREG-INNER-1 §2) — "
                               "the organism does not start")
        if self._inner is not None and "SENSE_BODY" not in self.genome.declared:
            raise GenomeError("INNER declared beside no SENSE body line: its trigger is the body row's own reading (PREREG-INNER-1 "
                               "AMENDMENT 1 A3) — the organism does not start")
        self.inner_state: Dict[str, object] = {"n": 0, "pos": 0, "last": [], "said": []}
        self.inner_counts: Dict[str, object] = {"turns": 0, "said": 0, "skipped": {}}

        (self.run_root / "journal").mkdir(parents=True, exist_ok=True)
        (self.run_root / "state").mkdir(parents=True, exist_ok=True)

    @property
    def hold_active(self) -> bool:
        """Read-only public view of `_hold_active` (§4(e)'s own flag) — creature/body.py's STATUS builder
        reads every OTHER exported fact off a plain public attribute (think_waits, web_fetches, …); this
        property keeps that convention instead of reaching into a leading-underscore field from outside
        the class."""
        return self._hold_active

    def ledgers(self) -> Dict[str, Dict[int, set]]:
        """The runner's ledgers (genome/questions.py:build_ledgers) as THIS mind reads them: under the gene HEAR a word cell is
        named by the word its own vector holds (PREREG-WORD-ROAD §1.9); without it, the ledger it always was."""
        return build_ledgers(self.org, self.moment_word)

    # ------------------------------------------------------------------ consume
    def consume(self, row: Dict[str, object]) -> None:
        if self._inherit_row_due:            # PREREG-INHERIT §3: one row, the life's first
            self._inherit_row_due = False
            self._write_journal(row["at"], {"kind": "inherit", "seq": row["seq"], **self.brain_inherited})
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
                if self.webs is not None:
                    # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB
                    # §1: under the flag the ear's word feeds as w:<word> (the node keys gain the prefix by
                    # construction — the SAME vocabulary the chat/ask doors feed); OFF: the exact old call.
                    if self.content_web:
                        for _tok in _cweb.ear_tokens(str(w)):
                            self._cweb_hear("ear", _tok)
                    else:
                        self._web_hear(str(w))
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
            if self.self_node is not None:
                self._self_body(row)
            if self._inner is not None:          # PREREG-INNER-1 §2: the inner turn's trigger is this row (its reading), nothing else
                self._inner_turn(row)
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:48 +0400 — LIFE-D-ACT-SOUND.md item 3
        # (L-13): the branch the brief's own READ FIRST line named as missing ("no ear-sound branch --
        # :244-257"). Gates itself on FAST's own "sound" key (self.sound_episodes is None otherwise), the
        # same one-row-carries-no-work-until-armed law every other new sense here already follows.
        elif sense == "ear-sound":
            # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:32 +0400 — A4L-VOICE task 3: `--blind sound` (the V3
            # twin) steps every sound row over whole — no FAST episode, no pending sound, no journal row.
            if "sound" not in self.blind:
                self._consume_ear_sound(row)
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
        # items 3/4: the two new tape senses (touch/smell), same one-row-carries-no-work-until-armed law.
        elif sense == "touch":
            self._consume_touch(row)
        elif sense == "smell":
            self._consume_smell(row)
        # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6: the
        # EVOLVE worker's own proposal, republished onto the tape by creature/senses/evolve.py.
        elif sense == "proposal":
            self._consume_proposal(row)
        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §3/§4: three
        # more tape senses, the same one-row-carries-no-work-until-armed law every sense above already
        # follows. `grade`/`hold` feed the READINESS judge's (d)/(e); `web` is counted only (an
        # UNCONSUMED sense otherwise, the brief's own words — see _consume_web's own docstring).
        elif sense == "grade":
            self._consume_grade(row)
        elif sense == "hold":
            self._consume_hold(row)
        elif sense == "web":
            self._consume_web(row)
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:38 +0400 — A4L-LANG task 3 (A4-LADDER-PREREG §3.2 item 2): a `chat` row goes to ONE
        # read-only branch and NEVER into the MEET road (it is never an ear/eye row, so pending/moment_word/org.t/
        # _canvas_index/ARRIVAL/FAST/THINK/SLEEP are never reached from it) — gated inside on CHAT's own presence.
        elif sense == "chat":
            self._consume_chat(row)
        # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:28 +0400 — BRAIN-IN-BODY (INTERFACE §2/§4): the scene world's `ask` rows.
        # Gated on the ROWS, never on the gene: the twin genome (no BRAIN line) answers the same sitting by the organs' road.
        elif sense == "ask":
            self._consume_ask(row)
        # a "door" row (the ask door / other senses not yet armed) carries no organism work here
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1: the muse hears
        # the sentence AFTER its door consumed it (the composer's same-breath answer is already written — the chain
        # never speaks, §1.3). Behind the flag alone; flag OFF: not one of these lines runs.
        if self.muse and sense in ("chat", "ask"):
            self._maybe_muse(row)
        self.last_seq = int(row["seq"])
        # ALPHA4-PREREG.md §3: self.stage only ever RISES here (org.t is monotonic; a committed "by READY"
        # stage is never revisited by _moments_stage, which cannot itself produce a judge-stage index).
        self.stage = max(self.stage, self._moments_stage())
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
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1: the game
        # channel's token (g:<act>:<reward sign>, declared from the row's own keys) — under the flag, where the
        # row is genuinely consumed (above the reflex bookkeeping; OFF: not one of these lines runs).
        if self.content_web and self.webs is not None:
            for _tok in _cweb.outcome_tokens(meta.get("act"), meta.get("got")):
                self._cweb_hear("outcome", _tok)
        result = self._record_reflex(act=str(meta.get("act", "")), got=meta.get("got"), expected_in=meta.get("expected"),
                                       residual_in=meta.get("residual"), source=str(meta.get("source", "")))
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:52 +0400 — LIFE-D-ACT-SOUND.md item 2
        # (L-8): the REPLAY control. Only a game row the mind itself chose (`chosen_by: "mind"`) carries
        # anything to check against -- a "schedule" row (no --act-file, or the ladder's twin road) has no
        # pending choice, and `_check_act_mismatch` would correctly return None for it anyway, but gating
        # here keeps every pre-existing test's outcome dict shape (#175's law for what a check MUST NOT
        # do: touch rows it was never asked about) untouched.
        if meta.get("source") == "game" and meta.get("chosen_by") == "mind":
            result = dict(result)
            result["act_mismatch"] = self._check_act_mismatch(meta)
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §4(a):
            # THE READINESS JUDGE's own window. The SAME gate the mismatch check above already uses
            # (source=="game" and chosen_by=="mind"), so a scheduled/worker-chosen act never counts toward it.
            # edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:40 +0400 — §4 AMENDED (§11 finding 1): per EPISODE.
            # An episode is COMPLETED by the outcome row whose own `terminated` or `truncated` is true (the worker's
            # gymnasium flags, creature/senses/game.py) and succeeded iff THAT row's own reward `got` > 0 — BabyAI pays
            # reward only on a successful terminal step (1 - 0.9·steps/max_steps), so the terminal row's `got` IS the
            # episode's return; never inferred from step counts. A terminal row carrying the same (episode, step) as the
            # last one counted is ONE episode, never two (a sense restart between a publish and its cursor write
            # re-publishes that step — the cursor law, #230). The journal's outcome row is untouched (the negative
            # control: nothing but the readiness rows moves).
            # edit: Claude (Sonnet 5, judge builder B4), 2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3: DISJOINT blocks
            # of READY_A_WINDOW, never a sliding deque. The dedup guard reads `_game_last_episode_step` (the deque's own
            # [-1] read the same fact); a counted episode advances the block-in-progress counters and, on the block's
            # READY_A_WINDOW'th episode, LOCKS `_game_last_block` (never mutated again except wholesale replacement by
            # the NEXT block completing) and resets the in-progress counters for the block after it.
            if meta.get("terminated") or meta.get("truncated"):
                ep, step = meta.get("episode"), meta.get("step")
                last = self._game_last_episode_step
                duplicate = (last is not None and ep is not None and step is not None
                             and last[0] == ep and last[1] == step)
                if not duplicate:
                    self._game_last_episode_step = (ep, step)
                    got = meta.get("got")
                    success = bool(got is not None and float(got) > 0.0)
                    self._game_block_n += 1
                    if success:
                        self._game_block_successes += 1
                    if self._game_block_n == READY_A_WINDOW:
                        block_index = (self._game_last_block["block_index"] + 1) if self._game_last_block else 0
                        self._game_last_block = {"block_index": block_index, "successes": self._game_block_successes}
                        self._game_block_n = 0
                        self._game_block_successes = 0
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item
        # 2 (L-12): the OTHER half of `_maybe_think`'s pending gate — a hands outcome row's own `act_seq`
        # (the eye row that chose it) clears `_hands_pending` iff it matches the CURRENT pending choice
        # (#175: never cleared by a stale/foreign row) so the 'hands' pool item can be offered again. No
        # mismatch check here (unlike the game's ACT policy, HANDS has no separate obeying agent that could
        # diverge from the mind's own choice — the sense thread reads exactly the program run/hands/ACT
        # names and runs exactly that).
        elif meta.get("source") == "hands":
            act_seq = meta.get("act_seq")
            if (self._hands_pending is not None and act_seq is not None
                    and int(act_seq) == int(self._hands_pending["seq"])):
                self._hands_pending = None
        self._write_journal(row["at"], {"seq": row["seq"], "outcome": result})

    def _consume_sit(self, row: Dict[str, object]) -> None:
        """G-MOT-3: SIT must be declared. `--blind sit` means "the score is not published" (MOTOR-HANDS.md's own
        words for this twin) -- blind is a Mind-level concept here (senses never receive it), so the mind treats a
        blind-sit row as if SIT had never fired: journaled as blind, no reflex recorded.

        edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §4: every SIT
        row is also an EXAM BOUNDARY — the point at which THE READINESS JUDGE is evaluated (never on a
        blind row: a blind SIT twin never receives a score at all, so §4(c) can never hold for it either
        way, and evaluating here would be dead code exercised by nothing). `composite` (§4(c)'s OTHER
        number) is read straight off the row's own meta — `creature/senses/sit.py`'s `sense()` gains this
        field in this same brief (`_composite_of`, additive, alongside the existing `score`); an older row
        (recorded before that change) simply carries no `composite` key, read as None here, which fails
        (c) honestly rather than inventing a value."""
        if "SIT" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        if "sit" in self.blind:
            self._write_journal(row["at"], {"seq": row["seq"], "sit": {"blind": True}})
            return
        result = self._record_reflex(act="sit", got=meta.get("score"), expected_in=None, residual_in=None,
                                       source=str(meta.get("source", "sit")))
        composite = meta.get("composite")
        read_share = meta.get("read_share")   # ALPHA4 §4(b): a TAPE FACT the sitter computed (Claude (Fable 5.1), 2026-09-23 03:02 +0400)
        self._sit_readings.append((meta.get("score"), float(composite) if isinstance(composite, (int, float)) else None,
                                   float(read_share) if isinstance(read_share, (int, float)) else None))
        readiness = self._readiness_readings() if "STAGE_READY" in self.genome.declared else None
        journal_row: Dict[str, object] = {"seq": row["seq"], "sit": result}
        if readiness is not None:
            journal_row["readiness"] = readiness       # #164/(b)'s "print it": every EXAM boundary states its own readings, not only the one that commits
        self._write_journal(row["at"], journal_row)
        if readiness is not None:
            self._maybe_advance_stage(row, readiness)

    # ------------------------------------------------------------------ ALPHA4-PREREG.md §4: THE READINESS JUDGE
    def _moments_stage(self) -> int:
        """The highest STAGE index whose grammar is `moments <a>..<b>` and whose lower bound `a` the
        organism has already reached (`org.t >= a`) — a pure function of the genome + org.t, recomputed on
        demand (never persisted separately), exactly like `Genome.stage2_start` already is. A "by READY"
        stage's own `a` is a judge NAME (a str), never an int, so it is simply skipped here — only
        `_maybe_advance_stage` may ever raise `self.stage` to that index."""
        best = 1
        for idx, _name, a, _b in self.genome.stages:
            if isinstance(a, int) and self.org.t >= a:
                best = max(best, idx)
        return best

    def _frames_alive(self) -> "List[Tuple[str, Optional[float]]]":
        """§4(b)'s frame half (edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:41 +0400 — §4 AMENDED, §11 finding 1):
        the frames ALIVE NOW = every pair `genome.sentence.find_frames()` returns over the mind's own FAST ring — the SAME
        call THINK's frame kind makes, "from the mind's own counts" — each with its co-occurrence lift count/expected >= 2.0.
        The ring's horizon IS the definition of alive: a frame whose evidence the ring has evicted is no longer alive, and it
        no longer BLOCKS. The unamended judge asked all() over every frame EVER FILED (`self._frames`, never pruned) against a
        20,000-episode ring that wraps ≈ hour 11.6 of alpha4-1 — (b) False for the rest of the life once any early frame's
        evidence left (#237 (c)'s shape) — and `self._frames` is not in the snapshot, so a resumed mind or an EVOLVE twin
        read that half against an empty set. Not consulted here any more (MOUTH still says from it). find_frames() emits a
        row only when count >= 5 and count > 2.0 * expected, so presence already means lift > 2.0; the >= 2.0 check below
        keeps the LAW's number in the judge, independent of find_frames' default. expected > 0 for every emitted row (both
        marginals >= 1); guarded anyway — a None lift, never float('inf') (json.dumps would write `Infinity`, invalid JSON
        for every other reader). Returns [(key "w1|w2", lift)] in find_frames' own order (by (w1, w2))."""
        if self.episodes is None:
            return []
        alive: List[Tuple[str, Optional[float]]] = []
        for r in find_frames(self.episodes):
            expected = float(r.get("expected") or 0.0)
            lift = (float(r["count"]) / expected) if expected > 0 else None
            if lift is None or lift >= 2.0:
                alive.append((f"{r['w1']}|{r['w2']}", lift))
        return alive

    def _read_proxy(self) -> Optional[bool]:
        """§4(b)'s read half: the sitter's `read_share` (tools/self_exam.py --read-words 50 --read-seed 20260923 — a fixed-
        seed sample of 50 over ALL the words the shelf has read aloud, rendered in the held-out font and answered by the
        snapshot; AMENDED 2026-09-23, it was the 20 NEWEST heard words) read off the last TWO `sit` rows, never computed
        here. Both >= 0.6 -> True; either under -> False; fewer than two rows, or a row without the number (a sitting with
        fewer than 50 heard words) -> None, which fails closed wherever it is read."""
        # edit: Claude (Fable 5.1), 2026-09-23 03:02 +0400 — RESOLVED at integration: the share is a TAPE FACT. The exam sitter (off the
        # mind thread, on the snapshot) reports `read_share`; the SIT row carries it; here it is READ, never computed.
        # edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:41 +0400 — the test-only override is gone (see __init__).
        if len(self._sit_readings) < 2:
            return None
        shares = [r[2] if len(r) > 2 else None for r in self._sit_readings]
        if any(v is None for v in shares):
            return None
        return all(v >= 0.6 for v in shares)

    def _sit_composite_ok(self) -> bool:
        """§4(c): the last TWO `sit` rows' composite >= 0.95 AND Q1 (the row's own `score`) >= 0.98 — both
        numbers, both rows. Fewer than two SIT rows yet, or either number missing/under its bar, fails."""
        if len(self._sit_readings) < 2:
            return False
        return all(r[0] is not None and r[0] >= 0.98 and r[1] is not None and r[1] >= 0.95
                   for r in self._sit_readings)

    def _readiness_readings(self) -> Dict[str, object]:
        """§4 (a)-(e), from TAPE FACTS ONLY — every value below is derived from a counter this mind built by CONSUMING rows
        (outcome/sit/grade/hold) or from its own FAST ring, never by reaching outside the tape or re-asking the organism;
        a pure function of those (reading it twice moves nothing and returns the same dict).

        edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:41 +0400 — §4 AMENDED (§11 finding 1): every clause is a
        BLOCK carrying its NUMBERS beside its verdict `ok` (#164 — the 23 readiness rows of alpha4-1's first hours carried
        booleans only), written on EVERY reading, the first included; every key on every row:
          a: success per COMPLETED episode, now over DISJOINT blocks (edit: Claude (Sonnet 5, judge builder B4),
             2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3, replacing the sliding-window read below). {window, n,
             successes, bound, null, ok, block_index, block_n, k, p_null_at_k, blocks_complete, k_single_reading} — the
             reading is the LATEST COMPLETE disjoint block of `window` (block_n, both READY_A_WINDOW) mind-chosen game
             episodes; `n`/`successes` are that block's own count and tally once any block has completed (frozen — "a
             block once read is never re-read with a different verdict" — until the NEXT block completes), or the
             in-progress count toward the block still being filled when NO block has completed yet (n < window, ok
             always False). `bound` == `k` == READY_A_BLOCK_K (11): the OPERATIVE threshold, the smallest k whose
             FAMILY-WISE rate over the ~2 disjoint blocks a 24 h life completes at the null's pace stays under alpha
             (`family_wise_bound`, computed, never typed — changing the null moves it). `p_null_at_k` is the SINGLE-BLOCK
             tail P(Binomial(window, null) >= k) at that k (0.0132) — NOT the family-wise rate (0.026) that is why k
             moved off `k_single_reading` (READY_A_BOUND, 10: the smallest k whose SINGLE-reading tail is <= alpha — the
             bound the held branch used before this amendment, correct for a judge read once, six-fold too loose read at
             every sitting on an overlapping window). `blocks_complete` counts every block that has ever locked in. The
             old formula (ok iff the window is full (n == 20) and successes >= bound): success over the SLIDING last
             `window` completed episodes, re-tested at every sitting — replaced here, not merely renamed.
          b: {frames_alive, lifts (the top 3 by lift, then by frame), read_share_last2, frames_ok, read_ok, ok} — ok iff
             >= 3 frames alive in the ring now (`_frames_alive`) AND both of the last two sittings' read_share >= 0.6.
          c: {composite_last2, q1_last2, ok} — unchanged: both of the last two sittings' composite >= 0.95 and Q1 >= 0.98.
          d: {answered, right, novel_window_n, novel_right, ok} — unchanged: >= 20 graded since birth, >= 0.8 right, and the
             last 10 novel grades FULL with >= 8 right.
          e: {hold, ok} — unchanged: no HOLD."""
        if self._game_last_block is not None:
            block_index = self._game_last_block["block_index"]
            a_n = READY_A_WINDOW
            a_successes = self._game_last_block["successes"]
        else:
            block_index = None
            a_n = self._game_block_n
            a_successes = self._game_block_successes
        blocks_complete = block_index + 1 if block_index is not None else 0
        a_ok = bool(self._game_last_block is not None and a_successes >= READY_A_BLOCK_K)
        a = {"window": READY_A_WINDOW, "n": a_n, "successes": a_successes, "bound": READY_A_BLOCK_K,
             "null": READY_A_NULL, "ok": a_ok,
             "block_index": block_index, "block_n": READY_A_WINDOW, "k": READY_A_BLOCK_K,
             "p_null_at_k": READY_A_BLOCK_P_NULL, "blocks_complete": blocks_complete,
             "k_single_reading": READY_A_BOUND}

        alive = self._frames_alive()
        top = sorted(alive, key=lambda kv: (-(kv[1] if kv[1] is not None else float("inf")), kv[0]))[:3]
        shares = [(r[2] if len(r) > 2 else None) for r in self._sit_readings]
        frames_ok = len(alive) >= 3
        read_ok = self._read_proxy() is True
        b = {"frames_alive": len(alive),
             "lifts": [{"frame": k, "lift": (round(v, 4) if v is not None else None)} for k, v in top],
             "read_share_last2": shares, "frames_ok": frames_ok, "read_ok": read_ok, "ok": bool(frames_ok and read_ok)}

        c = {"composite_last2": [r[1] for r in self._sit_readings], "q1_last2": [r[0] for r in self._sit_readings],
             "ok": bool(self._sit_composite_ok())}

        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:5x +0400 — advisor-caught: PREREG §4(d)
        # and §8 point 7 both name TEN as the denominator ("8 of the last 10 grades flagged novel"; "ten
        # of them never-seen pictures, so the judge's (d) can ever be true") — `>= 8` on a maxlen=10 deque
        # let as few as 8 novel grades (all right) satisfy (d) before the window ever filled. `== 10`
        # (never `>`, since the deque's own maxlen caps it) requires the FULL last-10 window before (d)
        # can ever hold, matching the bar's own denominator.
        novel_right = sum(1 for r in self._novel_grades if r)
        d_ok = (self._grades_total >= 20 and (self._grades_right / self._grades_total) >= 0.8
                and len(self._novel_grades) == 10 and novel_right >= 8) if self._grades_total else False
        d = {"answered": self._grades_total, "right": self._grades_right, "novel_window_n": len(self._novel_grades),
             "novel_right": novel_right, "ok": bool(d_ok)}

        e = {"hold": bool(self._hold_active), "ok": not self._hold_active}
        return {"a": a, "b": b, "c": c, "d": d, "e": e}

    def _maybe_advance_stage(self, row: Dict[str, object], readings: Dict[str, object]) -> None:
        """§4 (AMENDED 2026-09-23 — the streak defined ONCE): the door opens on ONE readiness reading whose five clauses all
        hold — each clause already spans its own horizon ((a) the latest complete disjoint block of 20 completed episodes,
        ALPHA4-2-PREREG §4.3; (b) the ring now and the last two sittings' read shares; (c) the last two sittings; (d) since
        birth and the last 10 novel grades; (e) now). The
        unamended «on two consecutive exam windows» counted (b)'s read half and (c) three sittings deep. ONE journal event
        carrying the whole reading (the same five blocks the readiness row carries), `self.stage` raised to the declared
        judge's own stage index, NEVER undone by the mind (a no-op forever once `self.stage` has reached it). Each verdict
        is read by its own "ok" key, never by a block's truthiness (a non-empty dict is always truthy — #238's SURPRISE mark)."""
        ready_gene = self.genome.declared.get("STAGE_READY")
        if ready_gene is None:
            return
        target_stage = int(ready_gene["stage"])
        if self.stage >= target_stage:
            return
        if all(readings[k]["ok"] is True for k in ("a", "b", "c", "d", "e")):
            self.stage = target_stage
            self._write_journal(row["at"], {"seq": row["seq"], "event": "stage", "stage": target_stage,
                                              "moment": self.org.t,
                                              "readings": {k: readings[k] for k in ("a", "b", "c", "d", "e")}})

    # ------------------------------------------------------------------ (d)/(e): the seat's grades + the hold flag
    def _consume_grade(self, row: Dict[str, object]) -> None:
        """ALPHA4-PREREG.md §4(d): a `grade` tape row (creature/senses/grade.py) — "mentorship enters
        through the tape, so the judge replays". Gated on SENSE_GRADE's own declared presence (the same
        "an unarmed sense's rows carry no organism work" law every other new tape-sense here follows)."""
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:38 +0400 — A4L-LANG task 3: a kind-"chat" grade (the chat door's republished seat
        # grade) is routed FIRST under CHAT — counted on STATUS (chat_graded/_right/_novel) and journaled as a grade row
        # carrying its kind, and NEVER reaching _grades_total/_grades_right/_novel_grades (the READINESS judge's (d)):
        # a grade on a chat moves nothing in this rung (§3.2 item 2). Such a row exists only where CHAT armed the door;
        # a genome without CHAT keeps master's road below, unchanged (the negative control).
        meta0 = row.get("meta") or {}
        if meta0.get("kind") == "chat" and "CHAT" in self.genome.declared:
            if "chat" in self.blind:
                return
            right_c, novel_c = bool(meta0.get("right")), bool(meta0.get("novel"))
            self.chat_counters["graded"] += 1
            self.chat_counters["graded_right"] += int(right_c)
            self.chat_counters["graded_novel"] += int(novel_c)
            self._write_journal(row["at"], {"seq": row["seq"], "grade": {"id": meta0.get("id"), "right": right_c,
                                                                          "novel": novel_c, "kind": "chat"}})
            return
        if "SENSE_GRADE" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        right = bool(meta.get("right"))
        novel = bool(meta.get("novel"))
        self._grades_total += 1
        if right:
            self._grades_right += 1
        if novel:
            self._novel_grades.append(right)
        self._write_journal(row["at"], {"seq": row["seq"], "grade": {"id": meta.get("id"), "right": right, "novel": novel}})

    def _consume_hold(self, row: Dict[str, object]) -> None:
        """§4(e): a `hold` tape row (the SAME grade sense, on every change — creature/senses/grade.py's own
        docstring). Gated on SENSE_GRADE's own declared presence, matching `_consume_grade` above."""
        if "SENSE_GRADE" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        self._hold_active = bool(meta.get("active"))
        self._write_journal(row["at"], {"seq": row["seq"], "hold": {"active": self._hold_active}})

    # ------------------------------------------------------------------ WEB (I): fetch/refusal counters
    def _consume_web(self, row: Dict[str, object]) -> None:
        """A `web` tape row (creature/senses/web.py) — counted, never otherwise acted on (the mind
        consumes nothing of the web row's own content: "an unconsumed sense", the brief's own words,
        matching the game door's outcome rows before K wired them). Gated on DOOR_WEB's own declared
        presence."""
        if "DOOR_WEB" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        status = meta.get("status")
        if status in ("ok", "failed"):
            self.web_fetches += 1
        elif status == "refused_rate":
            self.web_refused_rate += 1
        elif status == "refused_hold":
            self.web_refused_hold += 1
        self._write_journal(row["at"], {"seq": row["seq"],
                                         "web": {"status": status, "question_id": meta.get("question_id")}})

    # ------------------------------------------------------------------ A4L-LANG: THE CHAT (read-only)
    # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:38 +0400 — A4L-LANG tasks 3/5 (docs/briefs/A4L-LANG.md; A4-LADDER-PREREG §3.2 items 2-6).
    def _glances_per_canvas(self) -> int:
        """How many org moments one canvas occupies (the birth-source attribution's own window): 1 under BIND, else the
        GAZE fixations plus the coarse glance when it is declared and not blinded."""
        if "BIND" in self.genome.declared:
            return 1
        gz = self.genome.gaze or {}
        return int(gz.get("fixations", 1)) + (1 if (gz.get("coarse") and "coarse" not in self.blind) else 0)

    def _chat_guard(self) -> tuple:
        """The mind-level road a chat must never touch (the brief's own list), as one comparable value — asserted equal
        around the branch beside the organism's hash: the clock, the canvas index, the MEET road's pending words, the
        moment->word ledger, the heard set (ARRIVAL), every ring's size, the sleep cursor, SURPRISE's counts and the
        predictor's expectation, the act census, the think counters and pending sets, the READINESS tallies, the
        mouth's current instant."""
        rings = tuple(getattr(self, k).n_written if getattr(self, k) is not None else None
                      for k in ("episodes", "outcome_episodes", "sound_episodes", "touch_episodes", "smell_episodes"))
        lw = self.predictor._last_winner if self.predictor is not None else None
        return (self.org.t, self._canvas_index, tuple(sorted(self.pending.items())),
                tuple(sorted((k, tuple(v)) for k, v in self.pending_words.items())), len(self.moment_word),
                len(self._heard), rings, self._last_sleep_at, self.sleep_count, self.glances_confirmed,
                self.glances_surprised, (None if lw is None else np.asarray(lw).tobytes()),
                tuple(sorted(self.acts_chosen.items())), tuple(sorted(self.think_counters.items())),
                len(self._filed_predictions), len(self._frame_pending), len(self._frames), self._ask_out_n,
                self._grades_total, self._grades_right, tuple(self._novel_grades), self.stage,
                tuple(self._last_words_in_instant), self.org.budget_left, self.org.arrivals,
                len(self.picture_words), len(self.birth_source))     # A42-B2: a chat never writes either ledger

    def _chat_content(self, heard: List[str], xs: List[np.ndarray], Ls: Dict[int, set], Lw: Dict[int, set]) -> Dict[str, object]:
        """§3.2 item 3 — the content, grounded, chosen FIRST, one road for every chat: the canvas's glances asked by the
        genome's own answer law (recall_many + ANSWER's grade, unchanged); when the question names >= 2 THING-words
        (genome/chain.py:thing_words under THING_WORD_RULE — RAISED), the content is chosen AMONG them by the larger
        summed edge from the canvas's lit cells (the Q4 road: edge_many, max over the word's own cells); a tie abstains.
        Reads only."""
        r = self.org.recall_many("sight", xs) if xs else {"cell": None, "reason": "novel", "grade": None, "resembles_cell": None}
        # A42-B2 (edit: Claude (Fable 5.1), 2026-09-23 17:05 +0400; the rule flipped to "ledger" 17:5x on the orchestrator's word): the
        # THING-WORDS under THING_WORD_RULE ("ledger": the two LEDGERS, nothing from the ring). The ring rule «heard» and the
        # literal-from-ledger TWIN are still computed and PRINTED beside it on the say row (`things`, below) — counts and the two
        # differences, never the full sets — so the ring's forgetting after the wrap (≈ hour 11.6) is a visible difference on the
        # record, never a silent one. Every read here is read-only (the chat guard and the hash assert it).
        per_canvas = self._glances_per_canvas()
        things = _chain.thing_words(self.org, Lw, self.episodes, per_canvas=per_canvas, rule=_chain.THING_WORD_RULE,
                                    picture_words=self.picture_words, birth_source=self.birth_source)
        things_heard = _chain.thing_words(self.org, Lw, self.episodes, per_canvas=per_canvas, rule="heard")
        things_twin = _chain.literal_from_ledger(self.org, Lw, self.birth_source)
        named = list(dict.fromkeys(w for w in heard if w in things))
        out: Dict[str, object] = {"recall": r, "named_things": named, "content": None, "abstain_reason": None,
                                   "road": "recall", "edges": None,
                                   "things": {"rule": _chain.THING_WORD_RULE, "n": len(things), "heard_n": len(things_heard),
                                              "twin_n": len(things_twin), "heard_minus_rule": sorted(things_heard - things),
                                              "rule_minus_heard": sorted(things - things_heard)}}
        if len(named) >= 2:
            out["road"] = "choose"
            edges = {w: max([self.org.edge_many("sight", xs, c) for c in word_cells(self.org, Lw, w)], default=0.0) for w in named}
            ranked = sorted(edges.items(), key=lambda kv: (-kv[1], kv[0]))
            out["edges"] = [[w, round(float(v), 6)] for w, v in ranked]
            if ranked[0][1] <= 0.0:
                out["abstain_reason"] = "no_edge"
            elif len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
                out["abstain_reason"] = "tie"
            else:
                out["content"] = ranked[0][0]
            return out
        if r.get("cell") is None:
            out["abstain_reason"] = str(r.get("reason"))
            return out
        ws = Lw.get(int(r["cell"]), set())
        if len(ws) == 1 and next(iter(ws)):
            out["content"] = next(iter(ws))
        else:
            out["abstain_reason"] = "not_one_word"     # the answer cell's ledger is not one word (a merged or a sight-only birth)
        return out

    def _chat_grounded(self, xs: List[np.ndarray], content: str, Lw: Dict[int, set]) -> Dict[str, object]:
        """§3.2 item 5's content half: MEET-tied to THIS canvas — W > 0 from a sight cell one of its glances lights to
        one of the content's own word cells. The citation is the strongest such edge."""
        lit: List[int] = []
        for x in xs:
            for l in self.org._lit(self.org.sight, x)[0]:
                if l not in lit:
                    lit.append(int(l))
        best = None
        for t in word_cells(self.org, Lw, content):
            for l in lit:
                if self.org.mask[l, t] == 1 and float(self.org.W[l, t]) > 0.0:
                    w = float(self.org.W[l, t])
                    if best is None or w > best[2]:
                        best = (l, int(t), w)
        return {"ok": best is not None, "lit": len(lit),
                 "edge": (None if best is None else [best[0], best[1], round(best[2], 6)])}

    def _chat_point(self, g: Dict[str, object], xs: List[np.ndarray], target: Optional[str], Lw: Dict[int, set]) -> Optional[Dict[str, object]]:
        """§3.2 item 6: the window of the FIRST located glance whose own single-glance recall is `target` (the question's
        first thing-word, else the content); None when no located glance answers it."""
        if not target:
            return None
        for i in range(len(g.get("fix") or [])):
            rr = self.org.recall("sight", xs[i])
            ws = Lw.get(int(rr["cell"]), set()) if rr.get("cell") is not None else set()
            if ws == {target}:
                top, left = g["windows"][i]
                return {"glance": i, "window": [int(top), int(left)], "word": target}
        return None

    def _consume_chat(self, row: Dict[str, object]) -> None:
        """THE READ-ONLY LAW — «a question never teaches» (§3.2 item 2). Glance the canvas (the gaze's deterministic mode,
        the eye's own road), then READ — never write — the organism: the content (item 3), the point (item 6), the
        frames/links/pivots from `self.episodes` (the SAME find_frames the think step calls), the composer (item 4), the
        judge (item 5). Then write chat/out/<id>.json and journal ONE row {seq, say: {kind: "chat", …}}. It touches none
        of pending/pending_words/moment_word/_heard/org.t/_canvas_index, the rings, SURPRISE's expectation, the
        predictor, the THINK/SLEEP/SIT/EXAM boundaries, acts_chosen, the reflex ring, think_counters: `_chat_guard` and
        the organism's state hash are compared around it, and a difference RAISES — the crash law pages; a chat that
        changed him is a defect, never a result to log and continue."""
        decl = self.genome.declared.get("CHAT")
        if decl is None or "chat" in self.blind:
            return
        meta = row.get("meta") or {}
        raw_id = str(meta.get("id") or "")
        cid = raw_id if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", raw_id) else f"seq{int(row['seq'])}"
        heard = [str(w) for w in (meta.get("words") or []) if w]
        guard_before = self._chat_guard()
        hash_before = self.org.row_hash()   # edit: Claude (Fable 5.1), 2026-09-23 14:32 +0400 — the witness-aware digest (A4L-COST × A4L-LANG at the merge): row_hash IS state_hash when HASH is undeclared, the sparse witness when declared; the guard compares like with like

        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        mode = "random" if "gaze" in self.blind else "surprise"
        g = gaze.glances(rgb, self.genome.retina, self.genome.gaze, mode, row["sha"], colour=self.genome.colour)
        if "coarse" in (self.genome.gaze or {}) and "coarse" in self.blind:
            g = dict(g); g["feats"] = g["feats"][:-1]
        xs = list(g["feats"])
        ledgers = self.ledgers()
        Ls, Lw = ledgers["sight"], ledgers["words"]

        c = self._chat_content(heard, xs, Ls, Lw)
        content = c["content"]
        r = c["recall"]
        grade = r.get("grade")
        resembles = None
        if content is None and grade in ("sure", "unsure") and r.get("resembles_cell") is not None:
            rs = Ls.get(int(r["resembles_cell"]), set())
            resembles = next(iter(rs)) if len(rs) == 1 else None
        first_thing = c["named_things"][0] if c["named_things"] else None
        point = self._chat_point(g, xs, first_thing or content, Lw)

        rows_ = _chain.instants(self.episodes)
        stats = _chain.store_stats(self.episodes, rows=rows_)
        frames = find_frames(self.episodes)
        links = _chain.links(self.episodes, adj=int(decl["links_adjacent"]), stats=stats, frames=frames)
        pivots = _chain.pivots(self.episodes, distinct=int(decl["pivot_distinct"]), instants=int(decl["pivot_instants"]), stats=stats)
        comp = _chain.compose(heard, content, links, pivots, stats["follow"], stats["adjacency"], max_words=int(decl["max_words"]))
        form = list(comp.get("form") or [])

        refused: Optional[str] = None
        grounded: Optional[Dict[str, object]] = None
        judged = {"ok": True, "reason": None, "links": [], "cited": [], "pivot_followers": None, "pivot_instants": None}
        chain_said: List[str] = []
        if content is not None:
            grounded = self._chat_grounded(xs, content, Lw)
            if not grounded["ok"]:
                refused = "content"
            else:
                judged = _chain.judge_form(form, self.episodes, adj=int(decl["links_adjacent"]), distinct=int(decl["pivot_distinct"]),
                                           instants=int(decl["pivot_instants"]), rows=rows_, frames=frames)
                if judged["ok"]:
                    chain_said = list(comp.get("answer") or [content])
                else:
                    refused = "form"
                    chain_said = [content]
        chain_said = chain_said[: int(decl["max_words"])]

        hash_after = self.org.row_hash()
        if hash_after != hash_before or self._chat_guard() != guard_before:
            raise RuntimeError(f"CHAT: a chat changed the organism (id {cid}, seq {row['seq']}): hash {hash_before[:16]}… -> "
                               f"{hash_after[:16]}…, mind road {'unchanged' if self._chat_guard() == guard_before else 'CHANGED'} — the read-only law (A4-LADDER-PREREG §3.2 item 2)")

        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1.4 (THE FRUIT):
        # when the composer abstained (chain_said empty — the honest floor) and the muse holds a PROMOTED chain seeded
        # by EXACTLY this heard sequence, the answer comes from the organism's OWN consideration: the chain's candidacy
        # rows' words, each traced to its line. Tentative content never reaches here (the quarantine); the composer
        # itself is untouched (the same-breath bar, M-HONEST). Flag OFF: not one of these lines runs.
        muse_fruit = self._muse_fruit(heard) if (self.muse and not chain_said) else None
        if muse_fruit is not None:
            chain_said = list(muse_fruit["answer"])

        say = {"kind": "chat", "id": cid, "heard": heard, "content": content, "grade": grade, "chain": chain_said,
               "form": form, "pivot": comp.get("pivot"),
               "links": judged["links"] if judged["links"] else [[l["w1"], l["w2"], l["adj_count"], l["n_episodes"]]
                                                                   for l in links if [l["w1"], l["w2"]] in
                                                                   [[a, b] for a, b in zip(form, form[1:])]],
               "pivot_followers": judged.get("pivot_followers"), "point": point, "abstain_reason": c["abstain_reason"],
               "resembles": resembles, "refused": refused, "road": c["road"], "named_things": c["named_things"],
               "things": c["things"],      # A42-B2: the rule read + the ring rule and the twin beside it (counts and differences)
               "edges": c["edges"], "grounded": grounded, "form_reason": judged.get("reason"),
               "candidates_n": comp.get("candidates_n"), "truncated": comp.get("truncated"),
               "hash_before": hash_before, "hash_after": hash_after}
        if muse_fruit is not None:
            say["muse"] = muse_fruit      # the one additive key, present only when the fruit spoke (byte-identity OFF)
        out_dir = self.run_root / str(decl["out"])
        out_dir.mkdir(parents=True, exist_ok=True)
        out = {"id": cid, "seq": row["seq"], "at": row["at"], "answer": (chain_said or None), **{k: v for k, v in say.items() if k != "kind"}}
        tmp = out_dir / f"{cid}.json.tmp"
        tmp.write_text(json.dumps(out, default=str))
        os.replace(str(tmp), str(out_dir / f"{cid}.json"))
        self._write_journal(row["at"], {"seq": row["seq"], "say": say})

        self.chat_counters["chats"] += 1
        if chain_said:
            self.chat_counters["answered"] += 1
            self.chat_counters["words_total"] += len(chain_said)
            self.chat_counters["longest"] = max(self.chat_counters["longest"], len(chain_said))
            if refused == "form":
                self.chat_counters["refused_form"] += 1
        elif refused == "content":
            self.chat_counters["refused_content"] += 1
        else:
            self.chat_counters["abstained"] += 1
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1: THE OPENED
        # DOOR — the chat's consumed sentence feeds the webs as w: words (the ear's own vocabulary), under the
        # flag, AFTER the door's own work above (the read-only law's hash guard already passed; the webs are not
        # the organism — _chat_guard never covered them). OFF: not one of these lines runs.
        if self.content_web and self.webs is not None:
            for _tok in _cweb.words_tokens(heard):
                self._cweb_hear("chat", _tok)

    # ------------------------------------------------------------------ THE MUSE (PREREG-CONTEMPLATE-1)
    # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — the law's wiring (docs/brain/muse/
    # PREREG-CONTEMPLATE-1.md, signed 2026-10-09 23:01). Every method here runs ONLY behind Mind(muse=True)
    # (the flag gates the one call site in consume()); the organism, the brain, the web and the self are
    # READ, never written (the chain's writes are the mind's own records: the beliefs file's statused rows,
    # the question door's own files, and the journal's muse rows — the think road's own shape).
    def _muse_heard_words(self, row: Dict[str, object]) -> List[str]:
        """The sentence the chat/ask door consumed: a chat row's meta words (the door's own cut); an ask
        payload's `phrase` (the say form) or its bare `word` (what/why forms). Never the ear's stream."""
        meta = row.get("meta") or {}
        if row["sense"] == "chat":
            return [str(w) for w in (meta.get("words") or []) if w]
        try:
            payload = json.loads((_resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path"))
                                  / row["payload"]).read_text())
        except (OSError, ValueError):
            return []
        phrase = payload.get("phrase")
        if phrase:
            return [str(w) for w in phrase if w]
        word = payload.get("word")
        return [str(word)] if word else []

    def _maybe_muse(self, row: Dict[str, object]) -> None:
        """The trigger + the budget (the law §1.1). A chat row counts only when the chat door actually
        consumed it (CHAT declared and not blind); the chain machinery needs the brain's web and self —
        without them the muse is exactly as inert as the flag being off."""
        if row["sense"] == "chat" and ("CHAT" not in self.genome.declared or "chat" in self.blind):
            return
        if self.brain is None or self.webs is None or self.self_node is None:
            return
        heard = self._muse_heard_words(row)
        if not heard:
            return
        st = self._muse
        st["heard"] = int(st["heard"]) + 1
        heard_n = int(st["heard"])
        mature = {str(w) for w in self.brain.L.mature_words()}
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1's declared
        # composition: with the content web ON, the web's word vocabulary is the w:-prefixed one, so the
        # trigger's web.nodes lookups are handed w:-tokenized words (the heard sentence, the self's words, the
        # mature set alike) — the self/novel classes read EXACTLY as before (G-UNIT(e)'s pin), and the anchors
        # come back to BARE words before the chain machinery, so the composer, the beliefs store and the
        # question doors never see a prefix. Flag OFF: the exact old call.
        if self.content_web:
            trig_t = _muse_mod.trigger([_cweb.word_token(w) for w in heard], self.webs.get("L"),
                                       {_cweb.word_token(w) for w in _muse_mod.self_words(self.self_node)},
                                       {_cweb.word_token(w) for w in mature})
            trig = {"fire": trig_t["fire"], "classes": list(trig_t["classes"]),
                    "anchors": [a[len(_cweb.WORD_PREFIX):] if a.startswith(_cweb.WORD_PREFIX) else a
                                for a in trig_t["anchors"]]}
        else:
            trig = _muse_mod.trigger(heard, self.webs.get("L"), _muse_mod.self_words(self.self_node), mature)
        if not trig["fire"]:
            return                      # a trigger-negative sentence is counted, never journaled
        chain_id = _muse_mod.seed_of(heard)
        chains = st["chains"]
        if chain_id in chains:
            chains[chain_id]["reheard"] = int(chains[chain_id].get("reheard", 0)) + 1
            return                      # one chain per content: a re-hearing is never a new thought
        last_at = int(st.get("last_chain_at", -MUSE_BUDGET))
        if heard_n - last_at < MUSE_BUDGET:
            sk = st["skipped"]
            sk["budget"] = int(sk.get("budget", 0)) + 1
            self._write_journal(row["at"], {"kind": "muse", "act": "budget-skip", "seq": int(row["seq"]),
                                            "heard": list(heard), "anchors": list(trig["anchors"]),
                                            "classes": list(trig["classes"]), "heard_n": heard_n,
                                            "last_chain_at": last_at})
            return                      # a suppressed firing is always on the record
        st["last_chain_at"] = heard_n
        st["chains_started"] = int(st["chains_started"]) + 1
        self._muse_chain(row, heard, trig)

    def _muse_chain(self, row: Dict[str, object], heard: List[str], trig: Dict[str, object]) -> None:
        """ONE chain (the law §1.2), at most MUSE_STEPS steps: the anchors first (the heard claim's own
        substance, in order), then INNER's walk (creature/inner.py's candidates/draw, seeded from the
        heard rows' own bytes via the content address) from the previous topic; the chain RESTS when the
        neighbourhood is exhausted (never INNER's self-restart — this thought is ABOUT the heard claim).
        Each step files ONE tentative belief (the think road's own cells/episodes via questions_why, the
        store's new status) and, when the topic is unknown (no cells, no live episode to cite), forms ONE
        what-is question through the QUESTION door's declared forms. Every step journals its muse row."""
        from brain.world.seeds import substream
        from creature import inner as _inner
        chain_id = _muse_mod.seed_of(heard)
        web = self.webs.get("L")
        mature = sorted(str(w) for w in self.brain.L.mature_words())
        chain: Dict[str, object] = {"heard": list(heard), "anchors": list(trig["anchors"]),
                                    "classes": list(trig["classes"]), "seq": int(row["seq"]), "at": row["at"],
                                    "filed_sleep": int(self.sleep_count), "steps": [], "beliefs": [],
                                    "questions": [], "promoted": [], "reheard": 0}
        self._muse["chains"][chain_id] = chain
        bel_path = self.run_root / "state" / "beliefs.jsonl"
        anchors = list(trig["anchors"])
        said = list(heard)
        last: List[str] = []
        for step in range(MUSE_STEPS):
            cands: List[List[object]] = []
            if step < len(anchors):
                topic, source = anchors[step], "heard"
            else:
                cl, lifted = _inner.candidates(web, said, mature, last, MUSE_INHIBIT)
                cands = [[w, int(c), float(l)] for w, c, l in cl]
                topic = _inner.draw(cl, substream(int(self.genome.seed), f"muse-walk:{chain_id}:{step}"), "lift")
                if topic is None:
                    break               # the neighbourhood is exhausted: the thought rests
                source = "web (inhibition lifted)" if lifted else "web"
            record = questions_why(self.org, self.ledgers(), self.episodes, topic)
            belief_line = None
            if _THINK_LAWS_AVAILABLE and "BELIEF" in self.genome.declared:
                cells = [int(c) for area, c in record["cells"] if area == "sight"]
                brow = think_laws.file_tentative(bel_path, topic, cells, list(record["episodes"]), self.org.t)
                belief_line = int(brow["line"])
                chain["beliefs"].append(belief_line)
            question = None
            if "QUESTION" in self.genome.declared and not record["cells"]:
                # a question is formed only for a topic the organism cannot answer for (no sight cells —
                # the think road's own "its look"): the law's counter-questions are about the UNKNOWN
                question = self._muse_ask(chain_id, step, topic, record, row)
                if question is not None:
                    chain["questions"].append(question)
            chain["steps"].append({"step": step, "topic": topic, "source": source})
            self._write_journal(row["at"], {"kind": "muse", "act": "step", "seq": int(row["seq"]),
                                            "chain": chain_id, "step": step, "topic": topic,
                                            "topic_source": source, "said": list(said), "candidates": cands,
                                            "belief_line": belief_line, "question": question})
            said = [topic]
            last = (last + [topic])[-MUSE_INHIBIT:] if MUSE_INHIBIT > 0 else []

    def _muse_ask(self, chain_id: str, step: int, topic: str, record: Dict[str, object],
                  row: Dict[str, object]) -> Optional[Dict[str, object]]:
        """ONE question through the QUESTION door's declared what-is form (L-10's _maybe_ask itself, with
        its dedupe/persistence/counters): the scene parent's door when the topic has a live episode to
        cite (args [tape_moment] — the world-maker re-shows the canvas), else the bare word (the lexicon
        door's word-keyed twin, written by _maybe_ask only when DOOR_LEXICON is declared — with no episode
        and no lexicon door there is NO declared door, so no question is formed, never an invented one).
        The want carries the chain's address, so a question is asked at most once ever per chain topic."""
        tape_moment = self._latest_tape_moment_for_word(topic)
        door = None
        args: List[object] = []
        if tape_moment is not None:
            door, args = "scene-parent", [tape_moment]
        elif "DOOR_LEXICON" in self.genome.declared:
            door, args = "lexicon", [topic]
        if door is None:
            return None
        want = f"muse:{chain_id}:{step}:{topic}"
        n0 = self._ask_out_n
        saved = (self._cur_at, self._cur_seq)
        self._cur_at, self._cur_seq = row["at"], int(row["seq"])   # the question's at/seq is the HEARD row's
        try:
            self._maybe_ask(want, "what-is", args, why_word=topic)
        finally:
            self._cur_at, self._cur_seq = saved
        if self._ask_out_n == n0:
            return None                       # the want was already standing (the door's own dedupe)
        return {"want": want, "word": topic, "qid": f"q-{n0}", "door": door}

    def _muse_question_answered(self, q: Dict[str, object]) -> bool:
        """Promotion condition (i): the question's own door marked it answered (the doors' own completion
        markers — the world-maker's rename in ask/out, the lexicon sense's rename in world/questions)."""
        if q["door"] == "scene-parent":
            return (self.run_root / "ask" / "out" / f"{q['qid']}.answered.json").exists()
        return (self.run_root / "world" / "questions" / f"{q['qid']}.answered.json").exists()

    def _muse_promote(self, row: Dict[str, object]) -> None:
        """THE PROMOTION RULE (the law §1.4), checked at each consolidation pass (the SLEEP boundary's own
        call site): a chain's tentative rows are promoted to candidacy when BOTH (i) at least one question
        filed from the chain was answered through its declared door AND (ii) this pass ran since the
        filing. Promotion appends one superseding row per tentative (the store never overwrites) and
        journals one muse row; tentatives that never earn both stay quarantined forever."""
        chains = self._muse["chains"]
        if not chains or not _THINK_LAWS_AVAILABLE:
            return
        bel_path = self.run_root / "state" / "beliefs.jsonl"
        for chain_id, chain in chains.items():
            if chain.get("promoted") or not chain["beliefs"]:
                continue
            if int(self.sleep_count) <= int(chain["filed_sleep"]):
                continue                          # no consolidation pass since the filing
            answered = [q for q in chain["questions"] if self._muse_question_answered(q)]
            if not answered:
                continue                          # no question of this chain answered through its door yet
            considered = {int(r["line"]): r for r in think_laws.read_considered(bel_path)}
            pairs = []
            for line in chain["beliefs"]:
                t = considered.get(int(line))
                if t is None or t["current"] != "tentative":
                    continue
                c = think_laws.promote(bel_path, t["word"], int(t["line"]), list(t.get("cells", [])),
                                       list(t.get("episodes", [])), self.org.t)
                pairs.append([int(t["line"]), int(c["line"])])
            chain["promoted"] = pairs
            self._write_journal(row["at"], {"kind": "muse", "act": "promote", "seq": int(row["seq"]),
                                            "chain": chain_id, "pairs": pairs,
                                            "answered": [q["want"] for q in answered],
                                            "sleep_count": int(self.sleep_count)})

    def _muse_fruit(self, heard: List[str]) -> Optional[Dict[str, object]]:
        """THE FRUIT (the law §1.4): the composer's store may meet PROMOTED content only. A chain seeded
        by EXACTLY this heard sequence (the content address — a shuffled bag addresses nothing) whose
        rows reached candidacy answers from the organism's OWN consideration: the candidacy rows' words
        in chain order (the chain's bound is the CHAT line's own max_words), every word traced to its
        tentative and candidacy lines. Anything less (no chain, tentative still) is the honest floor."""
        chain = self._muse["chains"].get(_muse_mod.seed_of(heard))
        if not chain or not chain.get("promoted") or not _THINK_LAWS_AVAILABLE:
            return None
        decl = self.genome.declared.get("CHAT") or {}
        max_words = int(decl.get("max_words", 6))
        considered = {int(r["line"]): r for r in think_laws.read_considered(self.run_root / "state" / "beliefs.jsonl")}
        words: List[str] = []
        trace = []
        for t_line, c_line in chain["promoted"]:
            row_c = considered.get(int(c_line))
            if row_c is None or row_c["current"] != "candidacy":
                continue
            w = str(row_c["word"])
            if w not in words:
                words.append(w)
            trace.append([w, int(t_line), int(c_line)])
        if not words:
            return None
        return {"chain": _muse_mod.seed_of(heard), "answer": words[:max_words], "trace": trace}

    # ------------------------------------------------------------------ BRAIN-IN-BODY: the ask sense and the brain organ
    # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:34 +0400 — docs/brain/body/INTERFACE-BRAIN-ORGAN.md §2/§4 and the seat's two
    # addenda (every answer carries `raw` in the offline graders' names; every answer row carries `fix` + `hyps`; a box ask carries the
    # thing's `centroid`). An answer row's `seq` is the ASK row's seq, `eye_seq` the canvas it was answered on (None: canvas-less),
    # `at` the row the answer was MADE on (the eye row's for a held ask). One `answer` row per `ask` row, brain or organs.
    def _consume_ask(self, row: Dict[str, object]) -> None:
        """An `ask` tape row: its JSON payload read where the genome says the tape is (as `_consume_eye` reads its PNG). A
        canvas-less form (`begin`, `end`, `why`) is answered at once; any other is held for its moment's eye row, in tape order."""
        meta = row.get("meta") or {}
        payload = json.loads((_resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]).read_text())
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1: the ask
        # door's consumed sentence feeds the webs as w: words under the flag — the phrase (a say form) or the
        # bare word (what/why forms), the muse's own reading of what the door consumed (_muse_heard_words's
        # own cut, on the already-parsed payload). A begin/end carries no words: no tokens, never silently
        # skipped (named by the law §1's own list). OFF: not one of these lines runs.
        if self.content_web and self.webs is not None:
            _phrase = payload.get("phrase") or ([payload["word"]] if payload.get("word") else [])
            for _tok in _cweb.words_tokens([str(w) for w in _phrase if w]):
                self._cweb_hear("ask", _tok)
        ask = {"seq": int(row["seq"]), "at": row["at"], "moment": meta.get("moment"), "payload": payload}
        if payload.get("form") in ("begin", "end", "why"):
            self._answer_ask(ask, None, str(row["at"]), None, {})
        else:
            self.pending_asks.setdefault(str(meta.get("moment")), []).append(ask)

    def _chosen_look(self, row: Dict[str, object], g: Dict[str, object], turn: Dict[str, object],
                     scene_ix: int, ws: int, rgb) -> Tuple[Dict[str, object], Dict[str, object], Optional[Dict[str, object]]]:
        """PREREG-EYE-1 §2 (edit: Kimi K3 (kimi-code, acting seat, alone), 2026-10-05 23:23 +0400 — THE CHOSEN LOOK, the loop's
        return arrow): the leading hypothesis holds NO word (the turn's own doubt) → ONE forced glance at its locus, the
        brain's eye row re-fed (the forced feat INSERTED among the located feats, before the coarse one — feats stay
        index-aligned with fix), the turn re-read on it, and (in `_brain_canvas`) the learn runs on the re-read state.
        At most one look a canvas; the cells' road is untouched; a pure function of the tape and the turn's own output
        (no clock, no set order). Returns (g2, turn2, look_rec | (g, turn, None) when no look fires)."""
        if rgb is None or not turn.get("order"):
            return g, turn, None
        lead_ix = turn["order"][0]
        if not turn.get("held") or lead_ix >= len(turn["held"]) or turn["held"][lead_ix]:
            return g, turn, None        # no doubt, or the pre-calibration turn (its order is computed before the check)
        from genome.brain import things_in_view
        from brain.scene import eye as _eye
        hyps, _X = things_in_view(g)
        lead = hyps[lead_ix]
        grid = int((self.genome.gaze or {}).get("grid", 16))
        cy, cx = _eye.cell_centre_px((lead.pos[0], lead.pos[1]), int(rgb.shape[0]), grid)
        forced = _eye.forced_glance(rgb, (cy, cx), self.genome.retina, self.genome.gaze, self.genome.colour)
        n_loc = len(g.get("fix") or [])
        cell = [int(round(lead.pos[0])), int(round(lead.pos[1]))]
        g2 = dict(g)
        g2["feats"] = list(g["feats"][:n_loc]) + [forced] + list(g["feats"][n_loc:])
        g2["fix"] = [list(f) for f in (g.get("fix") or [])] + [cell]
        g2["windows"] = list(g.get("windows") or []) + [None]
        if g.get("residual") is not None:
            g2["residual"] = list(g["residual"][:n_loc]) + [None] + list(g["residual"][n_loc:])
        turn2 = self.brain.turn(g2, scene=scene_ix, world_seed=ws,
                                says=int(self._drive["says"]), asks=int(self._drive["asks"]))
        hyps2, _X2 = things_in_view(g2)
        j = next((i for i, h in enumerate(hyps2) if n_loc in h.members), None)
        rec = {"looked": True, "at": cell, "hyp": int(lead_ix),
               "held_before": [], "held_after": list(turn2["held"][j]) if j is not None else []}
        return g2, turn2, rec

    def _brain_canvas(self, row: Dict[str, object], moment: Optional[str], g: Dict[str, object], words: List[str],
                      rgb=None) -> None:
        """INTERFACE §4, the eye hook: held asks → answered here, and the brain does NOT learn from this canvas («an ask never
        teaches»); else a present brain that hears the eye row's source learns the instant's words (the TAPE's words, in order)."""
        meta = row.get("meta") or {}
        asks = self.pending_asks.pop(str(moment), None) if moment is not None else None
        if asks:
            cache: Dict[str, object] = {}
            for ask in asks:
                self._answer_ask(ask, g, str(row["at"]), int(row["seq"]), cache)
            return
        source = meta.get("source")
        if self.brain is None or not words or not self.brain.hears(source):
            return
        base = {"moment": moment, "seq": row["seq"], "at": row["at"]}
        # edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1: a hand other than the scene world (the maker, …) carries no
        # scene / world_seed on its rows; the brain hears it under a DERIVED index (this hand's own count of canvases the brain
        # learned, 0-based, restored from the brain's own state at a resume) and a DERIVED seed (genome.brain.world_seed_of: the
        # genome's SEED and the hand's name). Its rows carry `world`, `scene` and `world_seed`; a scene row is what it was, and a
        # scene row without its index is still refused by name.
        world = str(source)
        extra: Dict[str, object] = {}
        if world == _brain_scene_world() or (meta.get("scene") is not None and meta.get("world_seed") is not None):
            if meta.get("scene") is None or meta.get("world_seed") is None:
                self.brain_refused += 1      # a malformed scene row is named on the record, never learned from and never a crash loop (#230)
                self._write_journal(row["at"], {"kind": "brain", "act": "refused", **base,
                                                "reason": "an eye row the brain hears carries no scene / world_seed"})
                return
            scene_ix, ws = int(meta["scene"]), int(meta["world_seed"])
        else:
            scene_ix, ws = int(self._brain_world_count.get(world, 0)), _brain_world_seed(self.genome.seed, world)
        learn_kw: Dict[str, object] = {}
        if world != _brain_scene_world():
            extra = {"world": world, "scene": scene_ix, "world_seed": ws}
            learn_kw = {"world": world}
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 16:28 +0400 — PREREG-BRAIN-DRIVES §2.4: under DRIVE the brain takes its turn BEFORE it
        # learns from this canvas (it expects, it says, it asks — read-only, genome/brain.py:Brain.turn), its surprise is read
        # against the instant's words, and ONE row is journaled ahead of the learn row. The learning below is untouched.
        if self._drive is not None:
            turn = self.brain.turn(g, scene=scene_ix, world_seed=ws,
                                   says=int(self._drive["says"]), asks=int(self._drive["asks"]))
            look_rec = None
            if self._look is not None:
                g, turn, look_rec = self._chosen_look(row, g, turn, scene_ix, ws, rgb)
            self.brain_turns["turns"] += 1
            self.brain_turns["said"] += turn["say"] is not None
            self.brain_turns["asked"] += turn["ask"] is not None
            surprise = self.brain.surprise(turn, list(words))
            self._write_journal(row["at"], {"kind": "brain", "act": "turn", **base, **extra, **_jsonable(turn), "heard": list(words),
                                            "surprise": surprise, **({"look": look_rec} if look_rec else {})})
            # edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 18:35 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §2 (the mind):
            # THE MOUTH VOICES THE BRAIN — just after the turn's journal row and BEFORE the learn row, when the MOUTH clause is
            # declared and the turn's say is not None: ONE journal row (kind brain, act voice; the turn's say, every field,
            # copied; the scene hand carries no extra key, another hand carries world/scene/world_seed exactly as the turn row
            # does) and two counters. A canvas whose turn says nothing writes NOTHING. No world-door row, no reflex-ring episode,
            # never an ear row (the law §2's «what does not change»; the seat's six defaults taken by name).
            if self._voice is not None and turn["say"] is not None:
                self._write_journal(row["at"], {"kind": "brain", "act": "voice", **base, **extra,
                                                "say": _jsonable(turn["say"])})
                self.acts_chosen["voice"] = self.acts_chosen.get("voice", 0) + 1
                self.brain_turns["voiced"] += 1
            if self.self_node is not None:
                self._self_turn(turn, list(words), surprise, scene_ix, world)
        out = _jsonable(self.brain.learn(g, list(words), moment=str(moment), scene=scene_ix, world_seed=ws, **learn_kw))
        self.brain_learned += 1
        if learn_kw:
            self._brain_world_count[world] = scene_ix + 1
        # PREREG-BRAIN-IN-BODY (the seat, 20:4x): every learn row carries the canvas's located fixations and the eye's hypotheses (member
        # lists into `fix`) — the grader reads from it whether the one «dax» meeting was seen. The brain's own keys win if it returns them.
        from brain.scene import eye as _eye
        fix = [[int(y), int(x)] for (y, x) in (g.get("fix") or [])]
        view = {"fix": fix, "hyps": [[int(i) for i in m] for m in _eye.groups([tuple(f) for f in fix])]}
        self._write_journal(row["at"], {"kind": "brain", "act": "learn", **base, **extra, **view, **out})
        if self.self_node is not None:
            self._self_canvas(len(fix), scene_ix)
        if out.get("calibrated"):
            self._write_journal(row["at"], {"kind": "brain", "act": "calibrate", **base, **extra, "summary": _jsonable(self.brain.summary())})
            self.write_census()                 # PREREG-METADATA-1 §2: a file, never a journal row

    # -- the KNOWLEDGE WEB and the SELF (his 23:20 word): bookkeeping that can fail only OFF ----------------------------------
    def _web_fail(self, e: BaseException) -> None:
        self.web_error = f"{type(e).__name__}: {e}"
        self.webs = None
        self.self_node = None
        try:
            d = self.run_root / "web"
            d.mkdir(parents=True, exist_ok=True)
            with (d / "ERROR.txt").open("a") as f:
                f.write(f"moment {getattr(self.org, 't', None)} · {self.web_error}\n{''.join(_traceback.format_exception(e))}\n")
        except Exception:
            pass

    def _restore_brain_world_count(self) -> None:
        """PREREG-HEARS-2 §1: the derived scene index of every hand but the scene world = how many of its canvases the brain has
        learned; read from the brain's own index-aligned `worlds` (a brain without the attribute — a stand-in — has heard one hand)."""
        counts: Dict[str, int] = {}
        for w in (getattr(self.brain, "worlds", None) or []):
            if w != _brain_scene_world():
                counts[str(w)] = counts.get(str(w), 0) + 1
        self._brain_world_count = counts

    # edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:39 +0400 — PREREG-INNER-1 §2 + AMENDMENT 1 A1–A4 (research-1003 @ 9c589b2; the signed text
    # sha256 857e07b2…faa82): THE INNER TURN. The brain's first thought that is not about the present: on a SENSE body row whose own
    # reading says backlog 0, it re-sees ONE remembered scene (genome/brain.py:Brain.turn_remembered, read-only), says what it would
    # say, reads its surprise against the words heard then, and lets the said words' web associations choose the next thought. The
    # first consumer of the KNOWLEDGE WEB and the SELF. Every choice is a function of the tape and the genome (substreams keyed by the
    # inner index n), so a closed life with the line replays to itself and a resume reproduces the rows (the chain state in the ledger).
    def _inner_turn(self, row: Dict[str, object]) -> None:
        """ONE inner turn, or nothing (counted by reason): eligible when the brain exists, has calibrated once and learned a scene, and the
        row's `meta.reading.backlog` is 0 — a tape fact, no clock, no queue read. The chain of `restart` thoughts begins at the SELF's
        least reliable mature word (creature/inner.py:first_topic; A2 when none has a reliability); each later thought's topic is drawn,
        ∝ lift, among the previous say's words' consolidated web neighbours that are mature words and not among the last `inhibit`
        topics (inner.candidates / inner.draw, substream(SEED, "inner-walk:<n>"); A1: the union over the said words; a say of
        nothing carries the topic forward); no candidate → the chain restarts at the self. The scene: one drawn uniformly
        (substream(SEED, "inner-scene:<n>")) among the learned scenes whose heard words carried the topic; its world seed as
        _brain_canvas supplies it (the WORLD scene seed for the scene hand, world_seed_of otherwise). ONE journal row, kind brain act
        inner. The brain, the web and the self are READ, never written."""
        reading = (row.get("meta") or {}).get("reading") or {}
        skipped: Dict[str, int] = self.inner_counts["skipped"]      # type: ignore[assignment]

        def skip(why: str) -> None:
            skipped[why] = int(skipped.get(why, 0)) + 1

        if self.brain is None:
            skip("no brain")
            return
        bl = reading.get("backlog")
        if bl is None:
            skip("no backlog reading")
            return
        if int(bl) != 0:
            skip("backlog")
            return
        if int(self.brain.n_calibrations) < 1 or int(self.brain.n_learned) < 1:
            skip("not calibrated")
            return
        from brain.world.seeds import substream
        from creature import inner as _inner
        st = self.inner_state
        n, pos = int(st["n"]), int(st["pos"])
        restart, inhibit, rule = int(self._inner["restart"]), int(self._inner["inhibit"]), str(self._inner["walk"])
        # `walk_from` is a TEST parameter (PREREG-INNER-1 AMENDMENT 2 A2.1, G3's plant; set on the mind by the bench, never by the parser):
        # "said" = the law's walk, from the words the remembered turn SAID; "topic" = §0.2's counted walk, from the topic itself.
        walk_from = str(self._inner.get("walk_from", "said"))
        mature = sorted(str(w) for w in self.brain.L.mature_words())
        if not mature:
            skip("no mature word")
            return
        web = self.webs.get("L") if self.webs is not None else None
        said_from: List[str] = [str(x) for x in (st.get("said") or [])] if pos > 0 else []
        cands: List[List[object]] = []
        if pos == 0 or not said_from:
            topic, source, _table = _inner.first_topic(self.self_node, mature)
            pos = 0
        else:
            cl, lifted = _inner.candidates(web, said_from, mature, [str(x) for x in (st.get("last") or [])], inhibit)
            cands = [[w, int(c), float(l)] for w, c, l in cl]
            topic = _inner.draw(cl, substream(int(self.genome.seed), f"inner-walk:{n}"), rule)
            if topic is None:
                topic, _source, _table = _inner.first_topic(self.self_node, mature)
                source = "self (restart: no candidate)"
                pos = 0
            else:
                source = "web (inhibition lifted)" if lifted else "web"
        if topic is None:
            skip("no mature word")
            return
        scenes = self.brain.scenes_with(topic)
        if not scenes:
            skip("no scene carries the topic")
            return
        o = int(scenes[int(substream(int(self.genome.seed), f"inner-scene:{n}").integers(len(scenes)))])
        world = str(self.brain.world_of(o))
        ws_decl = self.genome.declared.get("WORLD_SCENE")
        if world == _brain_scene_world() and ws_decl is not None:
            ws = int(ws_decl["seed"])
        else:
            ws = _brain_world_seed(self.genome.seed, world)
        turn = self.brain.turn_remembered(o, world_seed=ws, says=1, asks=1)
        surprise = self.brain.surprise(turn, list(turn["heard"]))
        out = {"kind": "brain", "act": "inner", "n": n, "seq": row["seq"], "at": row["at"], "chain": pos + 1, "topic": topic,
               "topic_source": source, "from": said_from if pos > 0 else [], "candidates": cands, **_jsonable(turn),
               "world_seed": ws, "surprise": surprise}
        self._write_journal(row["at"], out)
        self.inner_counts["turns"] = int(self.inner_counts["turns"]) + 1
        self.inner_counts["said"] = int(self.inner_counts["said"]) + int(turn["say"] is not None)
        st["n"] = n + 1
        st["pos"] = (pos + 1) % restart
        st["last"] = ([str(x) for x in (st.get("last") or [])] + [topic])[-inhibit:] if inhibit > 0 else []
        st["said"] = [str(w) for w in turn["say"]["words"]] if (turn["say"] and walk_from != "topic") else [topic]

    def _web_hear(self, word: str) -> None:
        try:
            for w in self.webs.values():
                w.hear(word)
        except Exception as e:
            self._web_fail(e)

    # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB (F1) §1
    # (docs/brain/content-web/PREREG-CONTENT-WEB.md, signed 2026-10-10 13:27): the content feed. Every method
    # here runs ONLY behind Mind(content_web=True) — flag OFF: not one of these lines runs (byte-identity,
    # G-UNIT(a)). _cweb_hear is the ON road's SINGLE funnel (one _web_hear call per token, the ear's own
    # cadence — the web's arithmetic never learns the difference) and the census's only writer (the
    # per-sense token accounting of G-UNIT(d)/G-PLANT(i), in-memory instrument data, never snapshotted).
    def _cweb_hear(self, sense: str, token: str) -> None:
        self._cweb_counts[sense] = int(self._cweb_counts.get(sense, 0)) + 1
        self._web_hear(token)

    def _cweb_eye(self, g: Dict[str, object]) -> None:
        """The SIGHT channel's tokens for one consumed canvas: ONE s: token per hypothesis of the glance,
        in the glance's own order (the law's declared feed order). things_in_view is genome/brain.py:99's
        own path (reused, never re-implemented); a malformed glance would already have raised in the
        brain's own turn above, and the webs exist only beside a brain — so this never runs on a glance
        the brain refused.
        AMENDMENT 1 (edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 18:1x +0400): the token
        keys the organism's OWN RECOGNITION — self.org's alive sight store read HERE, as it stands ON
        ARRIVAL (before this canvas's own learning road below — the law §1's feed order is unchanged:
        the feed site, the guards and the census funnel are exactly as built; the empty store emits
        zero tokens, the declared honest floor)."""
        from genome.brain import things_in_view
        hyps, _X = things_in_view(g)
        for tok in _cweb.eye_tokens(self.org, [h.feat for h in hyps]):
            self._cweb_hear("eye", tok)

    def _self_kinds_now(self) -> Optional[List[set]]:
        n = int(self.brain.n_calibrations) if self.brain is not None else 0
        if n == 0:
            return None
        if self._self_kinds[0] != n:
            self._self_kinds = (n, [set(k) for k in self.brain.types()])
        return self._self_kinds[1]

    def _self_turn(self, turn: Dict[str, object], heard: List[str], surprise: Optional[float], scene: int,
                   world: Optional[str] = None) -> None:
        # edit: Claude (Fable 5.1, the seat), 2026-09-30 10:3x +0400 — PREREG-HEARS-2 §1: T2, T3, F1 and F2 speak of THE PARENT (the scene hand) and are
        # observed on its canvases only; the lived per-word reliability hears every hand; M1 speaks of the maker and hears it alone.
        try:
            node = self.self_node
            expected = [list(h) for h in (turn.get("expected") or [])]
            node.turn(heard, expected, surprise)
            C = node.claims
            hand = _brain_scene_world() if world is None else str(world)
            if hand == "maker":
                if surprise is not None and "M1" in C:
                    C["M1"].observe(surprise == 0, at=scene)
                return
            if hand != _brain_scene_world():
                return
            kinds = self._self_kinds_now()
            if kinds:
                C["T2"].observe(all(sum(1 for w in heard if w in k) <= 1 for k in kinds), at=scene)
            if surprise is not None:
                C["T3"].observe(surprise == 0, at=scene)
                shapes = [w for w in heard if w in SELF_SHAPES]
                if shapes:
                    union = {x for h in expected for x in h}
                    C["F1"].observe(any(w in union for w in shapes), at=scene)
            C["F2"].observe(len(heard) == 3, at=scene)
        except Exception as e:
            self._web_fail(e)

    def _self_canvas(self, n_fix: int, scene: int) -> None:
        try:
            self.self_node.canvas(n_fix)
            self.self_node.claims["T1"].observe(n_fix <= 4, at=scene)
        except Exception as e:
            self._web_fail(e)

    def _self_body(self, row: Dict[str, object]) -> None:
        try:
            reading = ((row.get("meta") or {}).get("reading") or {})
            bl = reading.get("backlog")
            if bl is not None:
                self.self_node.claims["B1"].observe(int(bl) <= 50, at=int(row["seq"]))
        except Exception as e:
            self._web_fail(e)

    def _answer_ask(self, ask: Dict[str, object], g: Optional[Dict[str, object]], at: str, eye_seq: Optional[int],
                    cache: Dict[str, object]) -> None:
        """One ask → one `answer` journal row. By the brain when there is one (its `ask` return journaled WHOLE), else by THE
        ORGANS' ROAD (creature/organs_road.py). Read-only either way: the organism's row hash and the mind's road (`_chat_guard`,
        the chat's own list) are compared around the answer and a difference RAISES — an answer that changed him is a defect."""
        payload = ask["payload"]
        form = str(payload.get("form"))
        view = None
        if g is not None:
            from creature import organs_road as _road
            view = cache.get("view") or _road.eye_view(g)
            cache["view"] = view
        hash_before, guard_before = self.org.row_hash(), self._chat_guard()
        detail = None
        if self.brain is not None:
            by = "brain"
            try:
                answer = _jsonable(self.brain.ask(payload, g))
            except Exception as e:                 # the organ's own refusal of a malformed ask (genome.brain.BrainError) is ANSWERED
                if type(e).__name__ != "BrainError":   # as refused, by name, never a crash: one bad row must not become a crash loop (#230)
                    raise
                answer = {"kind": "refused", "reason": str(e), "raw": {"refused": str(e)}}
        else:
            by = "organs"
            answer, detail = self._organs_answer(form, payload, view, cache)
        if self.org.row_hash() != hash_before or self._chat_guard() != guard_before:
            raise RuntimeError(f"ASK: answering {payload.get('item')!r} (form {form}, seq {ask['seq']}) by the {by} changed the organism "
                               f"or the mind's road — the read-only law (INTERFACE-BRAIN-ORGAN §4)")
        self._write_journal(at, {"kind": "answer", "by": by, "item": payload.get("item"), "mark": payload.get("mark"), "form": form,
                                 "answer": answer, "moment": ask["moment"], "seq": ask["seq"], "eye_seq": eye_seq, "at": at,
                                 "fix": (None if view is None else [[int(y), int(x)] for (y, x) in view[0]]),
                                 "hyps": (None if view is None else [[int(i) for i in h.members] for h in view[2]]),
                                 "detail": _jsonable(detail)})
        self.asks_answered += 1
        self.asks_by[by] = self.asks_by.get(by, 0) + 1

    def _organs_answer(self, form: str, payload: Dict[str, object], view, cache: Dict[str, object]):
        """THE ORGANS' ROAD (INTERFACE §4): -> (answer with `raw`, detail). `begin`/`end` are acknowledgements (the organs have
        nothing to calibrate)."""
        from creature import organs_road as _road
        if form in ("begin", "end"):
            a: Dict[str, object] = {"kind": form, "set": payload.get("set")}
            a["raw"] = dict(a)
            return a, None
        if "ledgers" not in cache:
            cache["ledgers"] = self.ledgers()
        ledgers = cache["ledgers"]
        if form == "why":
            return _road.answer_why(self.org, ledgers, self.episodes, payload)
        fix, located, hyps = view if view is not None else ([], None, [])
        if form == "point":
            return _road.answer_point(self.org, ledgers["words"], payload, fix, located, hyps)
        if form == "what":
            return _road.answer_what(self.org, ledgers["words"], payload, fix, located, hyps)
        if form == "say":
            return _road.answer_say(self.org, ledgers["words"], payload, fix, located, hyps)
        a = {"kind": "refused", "reason": f"no such form: {form!r}"}
        a["raw"] = dict(a)
        return a, None

    def brain_status(self) -> Optional[Dict[str, object]]:
        """STATUS (INTERFACE §4): the brain's `summary()` plus the ask counts; for the twin (BRAIN declared and blinded, or asks
        answered by the organs) the counts alone; None when this mind has neither a brain nor an ask (every other genome)."""
        if self.brain is None and "BRAIN" not in self.genome.declared and not self.asks_answered and not self.pending_asks:
            return None
        base = _jsonable(self.brain.summary()) if self.brain is not None else {"brain": None, "blind": "brain" in self.blind}
        out = {**base, "asks_answered": self.asks_answered, "asks_by": dict(self.asks_by),
               "asks_pending": sum(len(v) for v in self.pending_asks.values()), "learn_rows": self.brain_learned,
               "refused_rows": self.brain_refused, "restored": self.brain_restored}
        if self._drive is not None:            # PREREG-BRAIN-DRIVES: the turn counts, only under the gene
            out["turns"] = dict(self.brain_turns)
        if self._inner is not None:            # PREREG-INNER-1 §2: the inner counts (turns, said, skipped by reason) and the chain's place
            out["inner"] = {"turns": int(self.inner_counts["turns"]), "said": int(self.inner_counts["said"]),
                            "skipped": dict(self.inner_counts["skipped"]), "n": int(self.inner_state["n"]),
                            "chain": int(self.inner_state["pos"])}
        if self.brain_inherited is not None:   # PREREG-INHERIT §3: only a child carries the field
            out["inherited"] = dict(self.brain_inherited)
        # the KNOWLEDGE WEB and the SELF (his 23:20 word): counts and lengths only — this runs on the STATUS thread, which must never
        # walk a dict the mind thread is growing (#245)
        webs, node = self.webs, self.self_node        # one reference each: the mind thread may switch them off between two reads
        try:
            if webs is not None or self.web_error is not None:
                out["web"] = {k: {"t": w.t, "nodes": len(w.nodes), "edges": len(w.edges), "cap": w.cap(),
                                  "consolidated": int(w.stats["consolidated"]), "replaced": int(w.stats["replaced"]),
                                  "removed_missed": int(w.stats["removed_missed"])} for k, w in list((webs or {}).items())}
                out["web_error"] = self.web_error
                out["web_restored"] = self.web_restored
            if node is not None:
                lv = node.lived
                out["self"] = {"claims": {k: [c.state, c.confirmed, c.contradicted] for k, c in list(node.claims.items())},
                               "canvases": int(lv["canvases"]), "turns_expecting": int(lv["turns_expecting"]),
                               "expect_confirmed": int(lv["expect_confirmed"])}
        except Exception as e:                        # a STATUS read never takes the status thread down
            out["web_status_error"] = f"{type(e).__name__}: {e}"
        if self.brain is not None:             # PREREG-METADATA-1 §2: the census's totals (the whole census is the file)
            c = self.brain.census()
            out["census"] = {"scenes": c["scenes"], "scenes_by_source": c["scenes_by_source"], "n_words": c["n_words"],
                             "given_only_words": c["given_only_words"]}
        return out

    def write_census(self) -> None:
        """PREREG-METADATA-1 §2: the census as a FILE, <root>/census/<scenes learned>.json. Never a journal row."""
        if self.brain is None:
            return
        d = self.run_root / "census"
        d.mkdir(parents=True, exist_ok=True)
        c = self.brain.census()
        p = d / f"{int(c['scenes']):08d}.json"
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(c, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(p)

    def _consume_body(self, row: Dict[str, object]) -> None:
        """BODY-SENSES.md §4.1: "the readings; the DRIVE is the mind's" -- this gene carries no threshold, so
        there is nothing here to compute beyond recording the reading itself as a journal row (the refusal test in
        BODY-SENSES §4.1 -- "count the moments in which any journaled decision differs" -- is satisfied structurally
        by this row's own presence/absence).
        edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 -- L-9/SELF (docs/briefs/LIFE-A-ANSWER-SELF.md
        #3): the consumer BODY-SENSES.md asked for and this class's own docstring said did not exist yet --
        gated on SELF's own declared presence (a genome without SELF still just journals the reading, byte-for-
        byte the pre-SELF behaviour). Records the (seq, reading) pair a "self" think item compares
        (`_think_pool`/`_think_work`) and the single latest reading `_maybe_think` reads for the backlog skip --
        both READ from this recorded row, never the live queue, so a replay of the same tape decides the same
        (G-MIND-6's trap and its own twin, in one rule)."""
        if "SENSE_BODY" not in self.genome.declared:
            return
        if "body" in self.blind:
            self._write_journal(row["at"], {"seq": row["seq"], "body": {"blind": True}})
            return
        meta = row.get("meta") or {}
        reading = dict(meta.get("reading") or {})
        self._write_journal(row["at"], {"seq": row["seq"], "body": reading})
        if "SELF" in self.genome.declared:
            self._body_pair.append((int(row["seq"]), reading))
            del self._body_pair[:-2]
            self._last_body_reading = reading

    # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:48 +0400 — LIFE-D-ACT-SOUND.md item 3 (L-13).
    def _consume_ear_sound(self, row: Dict[str, object]) -> None:
        """The sound ear, consumed: a 37-float trait (band 32 + onset-shape 4 + level 1, EAR.md §4's TRAIT
        line) decoded from the row's own payload bytes (float32, `errors="replace"`'s spirit applied to a
        shape mismatch: a bad payload journals an error and returns, never crashes -- #230, the crash-loop
        lesson) and written to the DEDICATED sound_episodes ring (never self.episodes -- dims differ and
        this ring, like K's outcome_episodes, is never replayed through Organism.moment). "sound_episodes
        is None" covers both "FAST undeclared" and "FAST declared without the 'sound' key" -- the twin
        (#228): the row is stepped over, no journal, no episode, byte-for-byte the pre-L-13 behaviour.

        A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:32 +0400 — docs/briefs/A4L-VOICE.md task 2):
        a sound row the MAKER published on a canvas's own moment (`source: maker` — the world's voice) is ALSO held pending
        like a word, when the organism has a sound area (AREA sound declared), and bound at that moment's eye row
        (`_consume_eye`): the sound area resonates/births and meets sight and words there. Its journal row carries
        `"pending": True`. A sound row without a maker moment (a wav dropped in his folder: the ear door's `a<sha>e<i>`
        moments) keeps today's FAST-only road; with no sound area at all (the FLOOR genome — «the voice alone»), every row
        keeps it, byte-for-byte."""
        meta = row.get("meta") or {}
        area_on = (self.org.sound is not None and meta.get("source") == "maker" and meta.get("moment") is not None)
        if self.sound_episodes is None and not area_on:
            return
        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        try:
            raw = payload_path.read_bytes()
            trait = np.frombuffer(raw, dtype="float32")
            if trait.shape != (SOUND_TRAIT_DIM,):
                raise ValueError(f"ear-sound trait: expected {SOUND_TRAIT_DIM} float32s, got {trait.shape[0]}")
        except (OSError, ValueError) as e:
            # a malformed row is NOT an event -- self.sound_events is deliberately left untouched (#175: never a fabricated count)
            self._write_journal(row["at"], {"seq": row["seq"], "sound": {"error": str(e)}})
            return
        x_s = trait.astype(np.float64)
        x_w = np.zeros(1, dtype=np.float64)
        ep_id = None
        if self.sound_episodes is not None:
            ep_id = self.sound_episodes.write(moment=self.org.t, x_s=x_s, x_w=x_w, word="", surprise=0.0)
            self.sound_events += 1
        sound_row: Dict[str, object] = {"moment": meta.get("moment"), "level": meta.get("level"), "when": meta.get("when"),
                                         "file": meta.get("file"), "ep": ep_id}
        if area_on:
            self.pending_sound[str(meta.get("moment"))] = {"trait": x_s, "seq": int(row["seq"])}
            self.voice_rows += 1
            sound_row["pending"] = True
        self._write_journal(row["at"], {"seq": row["seq"], "sound": sound_row})

    # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 3
    # (BODY-SENSES.md §4.6). Mirrors _consume_ear_sound's own shape exactly (dedicated ring, errors=replace's
    # spirit applied to a shape mismatch -- a bad payload journals an error and returns, never crashes,
    # #230): decodes the row's own payload bytes as TOUCH_TRAIT_DIM float32s (exit, rate, stalls, retries,
    # bytes -- SENSE touch's own declared field order) and writes them to the dedicated touch_episodes ring
    # (never self.outcome_episodes, never replayed through Organism.moment -- see the module-level comment
    # on TOUCH_TRAIT_DIM).
    def _consume_touch(self, row: Dict[str, object]) -> None:
        if self.touch_episodes is None:
            return
        meta = row.get("meta") or {}
        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        try:
            raw = payload_path.read_bytes()
            trait = np.frombuffer(raw, dtype="float32")
            if trait.shape != (TOUCH_TRAIT_DIM,):
                raise ValueError(f"touch trait: expected {TOUCH_TRAIT_DIM} float32s, got {trait.shape[0]}")
        except (OSError, ValueError) as e:
            self._write_journal(row["at"], {"seq": row["seq"], "touch": {"error": str(e)}})
            return
        x_s = trait.astype(np.float64)
        x_w = np.zeros(1, dtype=np.float64)
        ep_id = self.touch_episodes.write(moment=self.org.t, x_s=x_s, x_w=x_w, word="", surprise=0.0)
        self.touch_events += 1
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "touch": {"moment": meta.get("moment"), "program": meta.get("program"), "ep": ep_id,
                      "exit": round(float(trait[0]), 6), "rate": round(float(trait[1]), 6),
                      "stalls": round(float(trait[2]), 6), "retries": round(float(trait[3]), 6),
                      "bytes": round(float(trait[4]), 6)},
        })

    # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 4
    # (BODY-SENSES.md §4.5). Same shape as _consume_touch above (kind, size, folder, age -- SENSE smell's
    # own declared field order).
    def _consume_smell(self, row: Dict[str, object]) -> None:
        if self.smell_episodes is None:
            return
        meta = row.get("meta") or {}
        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        try:
            raw = payload_path.read_bytes()
            trait = np.frombuffer(raw, dtype="float32")
            if trait.shape != (SMELL_TRAIT_DIM,):
                raise ValueError(f"smell trait: expected {SMELL_TRAIT_DIM} float32s, got {trait.shape[0]}")
        except (OSError, ValueError) as e:
            self._write_journal(row["at"], {"seq": row["seq"], "smell": {"error": str(e)}})
            return
        x_s = trait.astype(np.float64)
        x_w = np.zeros(1, dtype=np.float64)
        ep_id = self.smell_episodes.write(moment=self.org.t, x_s=x_s, x_w=x_w, word="", surprise=0.0)
        self.smell_events += 1
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "smell": {"moment": meta.get("moment"), "sha_prefix": meta.get("sha_prefix"), "ep": ep_id,
                      "kind": round(float(trait[0]), 6), "size": round(float(trait[1]), 6),
                      "folder": round(float(trait[2]), 6), "age": round(float(trait[3]), 6)},
        })

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

    # ------------------------------------------------------------------ LIFE builder D: L-8, the act loop
    def _recent_reflex_residuals(self, act: str, k: int = 10) -> List[float]:
        """The last (most recent) `k` LIVE outcome_episodes rows whose `word` (the act's own name — see
        `_record_reflex`'s `write(..., word=act, ...)`) equals `act`, newest first, each read back as its
        own `surprise` field (already the |residual| `_record_reflex` computed and stored -- never None,
        it substitutes 0.0 when the residual itself was ungradable). [] for an act never yet observed."""
        ep = self.outcome_episodes
        if ep is None:
            return []
        out: List[float] = []
        n = ep.n_written
        lo = max(0, n - ep.cap)
        for eid in range(n - 1, lo - 1, -1):
            rec = ep.get(eid)
            if rec is not None and rec["word"] == act:
                out.append(float(rec["surprise"]))
                if len(out) >= k:
                    break
        return out

    def _recent_reflex_gots(self, act: str, k: int = 10) -> List[float]:
        """edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:59 +0400 — A4L-EXPLORE: `_recent_reflex_residuals`'
        own walk (the last `k` LIVE outcome_episodes rows whose `word` is `act`, newest first, never past the ring's
        cap) reading each row's `got` — the payload `_record_reflex` files in x_s[0] (0.0 when a row carried none) —
        instead of its surprise. [] for an act with no outcome in that window (the value law's «untried»)."""
        ep = self.outcome_episodes
        if ep is None:
            return []
        out: List[float] = []
        n = ep.n_written
        lo = max(0, n - ep.cap)
        for eid in range(n - 1, lo - 1, -1):
            rec = ep.get(eid)
            if rec is not None and rec["word"] == act:
                out.append(float(rec["x_s"][0]))
                if len(out) >= k:
                    break
        return out

    def _maybe_choose_act(self, row: Dict[str, object]) -> None:
        """L-8 (MOTOR-HANDS.md G-MOT-1/G-MOT-4's "replay problem, named"; the plan's §4 L-8): on a game
        eye row, when this genome's ACT vocabulary drives the game (`self._act_policy_on`), choose the
        NEXT act and write it to `root/game/ACT` for the worker to obey. Policy (rung 1, exactly as the
        brief specifies): for each of the game's own acts (never `declared["ACT"]["verbs"]` -- the game's
        acts are BabyAI's own left/right/forward/pickup/drop/toggle/done, a DIFFERENT vocabulary; an
        outcome row's `act` field lands outside `declared["ACT"]["verbs"]` and is tagged `in_vocab: False`
        by `_record_reflex`, pre-existing and unchanged, raised in the report) the mean |residual| of its
        last 10 outcome episodes (0.0 for an act never yet observed); argmax with probability 0.9, uniform
        with 0.1; ties broken by `_act_rng`. Exactly TWO `_act_rng` draws per choice regardless of branch
        (one for explore-vs-exploit, one for the pick) so the stream's shape never depends on how many
        acts happen to tie -- replay recomputes the identical branch from the identical data either way,
        but a fixed draw count keeps the stream easy to reason about. A pure function of (genome, seed,
        the outcome ring's own live content, this row) -- replay re-derives the identical choice; no
        clock, no other rng stream, no organism state is read.

        edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 11:59 +0400 — docs/A4-LADDER-PREREG.md §2.5 (A4L-EXPLORE, the
        ALPHA4-PREREG §11.2 lock): when `ACT value reward <n>; optimism <f>` is declared, an act's weight is its VALUE —
        the mean REWARD (`got`) over its last <n> outcomes, <f> for an act with none in that window — instead of its
        mean |residual| (a surprise that, once one act was rewarded, never let any other act win: 96 of alpha4-1's last
        100 acts at hour 5). The 10 % uniform draw, the argmax with rng ties, the TWO draws a choice and the rng are
        unchanged; the journal's `policy` names the law. Undeclared: the loop below is the old one, byte for byte in
        its effect (the landing's negative control replays the hour-1 fixture identical, `hash` included)."""
        if not self._act_policy_on:
            return
        meta = row.get("meta") or {}
        if meta.get("source") != "game":
            return
        n_actions = meta.get("n_actions")
        if n_actions is None:
            return   # a game eye row that (for whatever reason) never published its own action-space size -- nothing to choose over
        n_actions = int(n_actions)
        act_names = list(meta.get("act_names") or [str(i) for i in range(n_actions)])[:n_actions]
        weights = []
        if self._act_value is None:
            for name in act_names:
                residuals = self._recent_reflex_residuals(name, k=10)
                weights.append(sum(residuals) / len(residuals) if residuals else 0.0)
            policy = "outcome-weighted"
        else:
            value_window = int(self._act_value["window"])
            optimism = float(self._act_value["optimism"])
            for name in act_names:
                gots = self._recent_reflex_gots(name, k=value_window)
                weights.append(sum(gots) / len(gots) if gots else optimism)
            policy = "reward-valued"

        u = float(self._act_rng.random())
        if u < 0.1:
            idx = int(self._act_rng.integers(0, n_actions))
            self.act_explored += 1
        else:
            best = max(weights)
            tied = [i for i, w in enumerate(weights) if w == best]
            pick = int(self._act_rng.integers(0, len(tied)))
            idx = tied[pick]
        act_name = act_names[idx]
        seq = int(row["seq"])

        act_path = self.run_root / "game" / "ACT"
        act_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = act_path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"seq": seq, "act": idx, "at": row["at"]}))
        os.replace(str(tmp), str(act_path))

        self._act_choices[seq] = {"idx": idx, "name": act_name}
        self.acts_chosen[act_name] = self.acts_chosen.get(act_name, 0) + 1
        self.act_policy = policy
        self.act_weights = [round(w, 6) for w in weights]
        self._write_journal(row["at"], {
            "seq": seq,
            "act": {"game": meta.get("game"), "act": act_name, "act_idx": idx, "seq": seq,
                    "policy": policy, "weights": [round(w, 6) for w in weights]},
        })

    def _check_act_mismatch(self, meta: Dict[str, object]) -> Optional[bool]:
        """L-8's REPLAY control: the outcome row that follows a chosen act carries the act the worker
        ACTUALLY took (`act_idx`), keyed to the choice that produced it by `act_seq` (the eye row's own
        seq -- #175: never "the last choice made", which by the time this row arrives may already be a
        LATER choice; see `_act_choices`'s own docstring above). None when there is nothing to check
        against (no `act_seq`, or no pending choice under it — never fabricated as a match or a
        mismatch, #175)."""
        act_seq = meta.get("act_seq")
        if act_seq is None:
            return None
        chosen = self._act_choices.pop(int(act_seq), None)
        if chosen is None:
            return None
        got_idx = meta.get("act_idx")
        mismatch = (got_idx is None) or (int(got_idx) != int(chosen["idx"]))
        if mismatch:
            self.act_mismatches += 1
        return bool(mismatch)

    def _consume_eye(self, row: Dict[str, object], moment: Optional[str]) -> None:
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11: this canvas's own
        # "at"/"seq", read by nested calls (_grade_rule, _maybe_ask, _maybe_say) that are not themselves
        # handed `row`. Set at the top, read-only for the duration of this one call.
        self._cur_at = row["at"]
        self._cur_seq = row["seq"]
        # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:52 +0400 — LIFE-D-ACT-SOUND.md item 2
        # (L-8): on a GAME eye row, choose the next act before anything else in this method (order among
        # the rest of _consume_eye's work is otherwise irrelevant to replay identity — this is a pure
        # function of genome/seed/tape either way — but the choice is made as early as possible so the
        # worker sees it with the least possible latency in a live life).
        self._maybe_choose_act(row)
        # edit: Claude (Fable 5.1), 2026-09-21 12:01 +0400 — W3-0b seam (Builder C's finding 4): the payload is read under the genome's own TAPE path
        # (creature/tape.py:_resolve_tape_dir — byte-identical for the default `run/tape`), never a second hardcoded "tape".
        payload_path = _resolve_tape_dir(self.run_root, self.genome.declared.get("TAPE", {}).get("path")) / row["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        mode = "random" if "gaze" in self.blind else "surprise"
        # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): word/xw moved ABOVE the
        # gaze.glances() call (were below it) so SURPRISE's expectation — the word's best sight cell — can
        # be computed and passed in as `predicted=`. Safe by PREREG §2.2's own order law (the ear row
        # precedes the eye row of the same moment; `word` is already fully known here, exactly as it
        # always was two lines further down before this edit).
        word = self.pending.pop(moment, None) if moment is not None else None
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: every word this
        # instant's ear rows delivered, in order (popped alongside self.pending above; a moment with one
        # ear row is a one-element list, byte-identical in meaning to `word` alone).
        words_in_instant: List[str] = self.pending_words.pop(moment, []) if moment is not None else []
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:36 +0400 — A4L-VOICE task 3: `--blind ear` (V1's twin).
        # «The words area never lights»: the ORGANISM hears no word — `word`/`words_in_instant` (and so xw, PREDICT, SURPRISE's
        # expectation, the episode) are None/[] below, exactly as on a wordless canvas. The RUNNER's bookkeeping still reads the
        # ear row: `label` is the word the tape carried, used ONLY for the ledger (moment_word — «the sight cell's birth ledger
        # names the thing», V1's own read) and for ARRIVAL's world clock (a never-heard word opens an arrival, the ONE budget
        # refreshes). Blind to exactly ONE thing (#228's addendum): without ARRIVAL the twin would have 0 arrivals in 8 h and
        # its births would be refused by the budget — V1 would then read the budget, not the ear (#228 (a), #238). Not blind:
        # label == word, every line below byte-for-byte what it was.
        label = word
        tape_words: List[str] = list(words_in_instant)    # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:31 +0400 — the brain hears the TAPE's words (its own blind is `--blind brain`, never `--blind ear`)
        if "ear" in self.blind:
            word, words_in_instant = None, []
        # A4L-VOICE task 2: this canvas's SOUND (the maker's chord, held since its ear-sound row) — bound HERE, at the eye row.
        snd = self.pending_sound.pop(str(moment), None) if (moment is not None and self.pending_sound) else None
        x_snd = snd["trait"] if snd is not None else None
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 4 (MOUTH): the CURRENT
        # instant's words and first glance, read by _maybe_think -> _maybe_say below (the mouth judges what
        # it says against THIS canvas's own glance, never a stored/replayed one).
        self._last_words_in_instant: List[str] = words_in_instant
        # G5-E (docs/briefs/G5-E-ERROR-ARMS-BY-REPLAY.md): hoisted above PREDICT's error() call, which
        # arm "comparator" needs (a word's encoding, read-only) BEFORE Organism.moment() runs for this
        # canvas — encode_word is pure, so computing it here changes nothing else (word is None on a
        # sight-only canvas, xw stays None, exactly as arm "comparator"/"conjunctive" expect).
        xw = encode_word(word, self.genome.ear_blank_zero) if word is not None else None
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 12:59 +0400 — PREREG-WORD-ROAD §1.1 (the gene HEAR): W, the words the organism MEETS at this
        # canvas = the instant's ear rows in tape order, each distinct word once (its first place). `word` (the LAST word) stays
        # the thing: the ledger, the journal's `word`, ARRIVAL. A word the ear refuses that is NOT last (over 8 letters, or a
        # letter outside a–z) is left out BY NAME and counted; the last word's own refusal is what it always was.
        hear_words: Optional[List[str]] = None
        hear_xws: Optional[List[np.ndarray]] = None
        hear_refused: List[str] = []
        if self._hear and word is not None:
            hear_words, hear_xws = [], []
            for w in dict.fromkeys(words_in_instant):
                if w == word:
                    hear_words.append(w); hear_xws.append(xw)
                    continue
                try:
                    xv = encode_word(w, self.genome.ear_blank_zero)
                except ValueError:
                    hear_refused.append(w)
                    self.hear_words_refused += 1
                    continue
                hear_words.append(w); hear_xws.append(xv)
            if word not in hear_words:                       # a blank last word («») is no entry of words_in_instant: met as it always was
                hear_words.append(word); hear_xws.append(xw)
        surprise_gene = self.genome.declared.get("SURPRISE")
        # L-4: read-only, never births (Organism.expected_sight's own guarantee) — None when SURPRISE is
        # undeclared, xw is None (sight-only or an unknown word), or the word's own cell has no edge yet.
        predicted = self.org.expected_sight(xw) if surprise_gene is not None else None
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:30 +0400 — G-EYE-3/§3.6: colour=None unless
        # SENSE colour is declared (Genome.colour, machinery.py) — a complete no-op call otherwise, byte-
        # identical to every existing pin.
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400 — PREREG-OPEN-WORLD-3 §1's ONE branch
        # point: with the front wired, the canvas is TRANSduced by creature/senses/vfront.py instead — the raw-frame
        # feature path (luminance → INK rule → retina tower) is REPLACED for this consumption (never raw frames
        # inward); fixation SELECTION stays on the Alpha-2 analyse/gaze_sequence inside the front, and the returned
        # dict is the glances dict's own shape, so every line below reads it unchanged. None (the default): the
        # exact call this method has always made.
        if self.eye_front is not None:
            g = self.eye_front.glances(rgb, mode, row["sha"], predicted=predicted)
        else:
            g = gaze.glances(rgb, self.genome.retina, self.genome.gaze, mode, row["sha"], colour=self.genome.colour, predicted=predicted)
        g_eye = g     # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:31 +0400 — the glance BEFORE the organism's blind-coarse strip (which rebinds `g`, never mutates this dict): the brain's input
        # L-7 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): --blind coarse drops the
        # fifth (coarse) feature from THIS mind's own learning road entirely — genome/gaze.py has no notion
        # of "blind" (a Mind-only concept), so it always appends the coarse feature when the gene is
        # declared; stripping it here, before org_feats/residuals are built, is what makes a blind-coarse
        # replay's journal equal a genome that never declared coarse at all (the reader's own test, below).
        if "coarse" in (self.genome.gaze or {}) and "coarse" in self.blind:
            g = dict(g)
            g["feats"] = g["feats"][:-1]
            if g.get("residual") is not None:
                g["residual"] = g["residual"][:-1]
        # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:31 +0400 — BRAIN-IN-BODY (INTERFACE §4): asks held for this moment are answered
        # (by the brain, else the organs' road — read-only, asserted) and the brain does NOT learn from this canvas; else a present brain
        # that hears this source learns the instant's words. BEFORE the organism's road (an answer reads the organism as it was before
        # this canvas), and above org_feats/_row_digest, so nothing here can move org.t between the canvas row and its coarse row.
        # Neither branch runs without a brain or a held ask: every genome and tape without them is byte-identical.
        if self.brain is not None or self.pending_asks:
            self._brain_canvas(row, moment, g_eye, tape_words, rgb=rgb)
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1: the SIGHT
        # channel's tokens. Under the flag (and only then), ONE s: token per hypothesis of THIS canvas's glance,
        # in the glance's own order, fed where the row is consumed (tape order — the law's feed order). The
        # glance → hypotheses path is genome/brain.py:99's things_in_view (reused, never re-implemented);
        # `g` here is post-coarse-strip, which things_in_view never reads (it reads feats[:len(fix)]). The
        # organism's road below is untouched: the webs are not the organism (OFF: not one of these lines runs).
        if self.content_web and self.webs is not None:
            self._cweb_eye(g)
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:30 +0400 — G-EYE-2/BIND (_bind_pool, above):
        # undeclared (the common case today) this is g["feats"] itself, unchanged — every existing `for x
        # in g["feats"]:` loop below now reads `org_feats` instead, with IDENTICAL contents when BIND is
        # off. Declared: ONE pooled vector, so the loops below run their body once instead of F times —
        # this is the whole of "one canvas = one moment" (org.t advances by 1, not by GAZE.fixations).
        org_feats = _bind_pool(g["feats"]) if "BIND" in self.genome.declared else g["feats"]
        # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): index-aligned with
        # org_feats — safe because BIND and SURPRISE/coarse are refused together at __init__ above, so
        # whenever SURPRISE is declared (the only case confirmed_flags can ever be True) org_feats IS
        # g["feats"] unpooled. `floor` is the blind twin's own law: "--blind surprise" reads residual/
        # confirmed exactly as the live mind does (still computed, still journaled) but never confirms
        # (floor -1 is below every possible residual, which is >= 0 by construction) — a twin to compare
        # the CONFIRM mechanism's effect against, not a twin blind to the computation itself.
        residuals = g.get("residual") or [None] * len(org_feats)
        floor: Optional[float] = None
        if surprise_gene is not None:
            floor = -1.0 if "surprise" in self.blind else float(surprise_gene["floor"])
        confirmed_flags = [(floor is not None and r is not None and r < floor) for r in residuals]
        n_graded = sum(1 for r in residuals if r is not None)
        n_confirmed = sum(1 for f in confirmed_flags if f)
        self.glances_confirmed += n_confirmed
        self.glances_surprised += max(0, n_graded - n_confirmed)
        # edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md §2.4
        # (docs/briefs/A4L-DROP.md task 2): "drop_on" reads the parser's own nested sub-key (genome/machinery.py's
        # SURPRISE branch: "drop" can only be present when "predicted" is), so this is False on every genome
        # that predates this task, and False on a genome that declares SURPRISE (with or without "predicted
        # mind-cell") but not the trailing "; drop confirmed" clause.
        drop_on = surprise_gene is not None and surprise_gene.get("drop") == "confirmed"

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

        # edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:05 +0400 — A42-B2 PART 2: the picture-words LEDGER (see __init__).
        # Written from the SAME two facts the episode written below carries — the eye row's own `meta["source"]` (a picture source:
        # genome/chain.py:PICTURE_SOURCES) and this instant's words AFTER the blind-ear twin cleared them — on BOTH roads below
        # (a worded canvas and a sight-only one alike, the ring is written on both), so `set(picture_words)` is exactly
        # chain.heard_on_pictures(episodes) until the ring wraps. A ledger only: no organism state, no journal field, no hash.
        if words_in_instant and meta.get("source") in _chain.PICTURE_SOURCES:
            for _pw in words_in_instant:
                if _pw and _pw not in self._picture_words_set:
                    self._picture_words_set.add(_pw)
                    self.picture_words.append(_pw)

        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:36 +0400 — A4L-VOICE task 2/3: the worded road ALSO
        # carries a canvas that has a SOUND and no word (`--blind ear`, or a voiced canvas whose word never came) — «a canvas
        # that carries a SOUND and no word must still run the sight↔sound meeting, never the sight-only road» (the brief's own
        # words; #228 (a): else V1's twin can learn nothing by construction). With a word and no sound every line below is
        # byte-for-byte the old road (x_snd None; `word or label` == word; the episode/score/journal lines unchanged).
        if word is not None or x_snd is not None:
            births_before = len(self.org.births)
            edges_before = len(self.org.edges_log)
            prunes_before = len(self.org.prunes_log)
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: a never-heard word is an ARRIVAL — the birth budget is
            # fresh BEFORE the moment that first meets it (life 1 never called new_arrival: arrivals 0, budget spent once,
            # 419 births refused, nothing born after 07:41 +04). Gated on the gene: an undeclared ARRIVAL changes nothing.
            arrival_n: Optional[int] = None
            arr_word = word if word is not None else label       # A4L-VOICE: the blind-ear twin keeps the world's arrival clock
            if arr_word is not None and arr_word not in self._heard:
                self._heard.add(arr_word)
                if "ARRIVAL" in self.genome.declared:
                    self.org.new_arrival()
                    arrival_n = int(self.org.arrivals)
            ledger_word = word if word is not None else (label if label is not None else "")
            sound_winners: List[int] = []
            for i, x in enumerate(org_feats):
                self.moment_word[self.org.t] = ledger_word    # keyed by the organism's OWN moment counter, one per glance (or one per canvas under BIND)
                # L-4: confirmed_flags[i] is False on every existing genome (SURPRISE undeclared -> floor
                # is None -> every flag False) — byte-identical to the old bare `self.org.moment(x, xw,
                # lr_scale=lr_scale)` call.
                # edit: Claude (Sonnet 5, A4 ladder builder DROP), 2026-09-23 11:19 +0400 — A4-LADDER-PREREG.md
                # §2.4 (docs/briefs/A4L-DROP.md task 2): a glance this same "confirmed_flags" already marks
                # CONFIRMED, under "drop confirmed", is not passed to Organism.moment() at all — Organism.tick()
                # runs exactly moment_sight()'s tail (t += 1; SCALE at its own multiples; the budget's regen
                # check), so every moment-denominated cadence keeps its wall-clock meaning (D3). S, T = [], []
                # for this glance: predictor.note_winners([]) is its own documented no-op (genome/predict.py:120,
                # "an empty S leaves the last winner as it was") and glance 0's FAST episode below is written
                # from f0/t_at_f0, captured before this loop, so it is untouched either way. drop_on False
                # (every genome before this task, and every genome that never declares "; drop confirmed"):
                # this branch is never taken — byte-identical to the bare `self.org.moment(...)` call below.
                if drop_on and confirmed_flags[i]:
                    self.org.tick()
                    S, T = [], []
                    self.glances_dropped += 1
                else:
                    S, T = self.org.moment(x, (hear_xws if hear_xws is not None else xw), lr_scale=lr_scale,
                                           confirm=confirmed_flags[i], x_snd=x_snd)
                    if x_snd is not None:   # A4L-VOICE, kept inside the else at the merge (Claude (Fable 5.1)): a DROPPED glance runs no moment, so no sound winners either
                        sound_winners.extend(u for u in self.org.last_sound_winners if u not in sound_winners)
                if predict_on:
                    self.predictor.note_winners(S)
            ep_kwargs = seam0 if moment_on else {}         # G-MIND-1: Episodes stores the seam only once MOMENT declares the columns
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: words_in_instant/
            # tape_moment are stored UNCONDITIONALLY (not gated on MOMENT — the plan's own words: "MOMENT
            # keys ... gains nothing in the genome"), a fresh pair of Episodes columns exactly like x_s2 above.
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0,
                                          x_w=(xw if xw is not None else encode_word("", self.genome.ear_blank_zero)),
                                          word=(word if word is not None else ""), surprise=err,
                                          words_in_instant=words_in_instant, tape_moment=moment,
                                          **ep_kwargs) if fast_on else None
            # L-4: "no think-pool item" — glance 0 is the one FAST's episode is built from (f0 above); if
            # it was CONFIRMED, this episode is excluded from _think_pool()'s pool (below), never from
            # SLEEP/the episodic PREDICT arm, which read the episode ring directly, not the pool.
            if fast_on and ep_id is not None and confirmed_flags and confirmed_flags[0]:
                self._confirmed_episodes.add(ep_id)
            if word is not None:
                # A42-B2 G9 (edit: Claude (Fable 5.1), 2026-09-23 17:05 +0400): the instant's LOCATED glances (g["feats"][:len(fix)];
                # the whole list when no fixation is located — `one` mode, or BIND's pooled vector) and its source travel with the
                # call; the scorer reads them ONLY under `SENTENCE …; judged by the eye on the line` — undeclared, every line of
                # _score_due_predictions is the road it always was (the hour-1 fixture replays identical, A42-B2-REPORT).
                self._score_due_predictions(word, g["feats"][0] if g["feats"] else None, words_in_instant=words_in_instant,
                                            glances=(org_feats[:len(g["fix"])] if g["fix"] else list(org_feats)), source=meta.get("source"))
            if snd is not None:
                self.voice_bound += 1
            self._ledger_births(births_before, meta.get("source"))      # A42-B2: the birth-source ledger (a ledger only; the row below is unchanged)
            births = [[b[1], int(b[2]), b[3]] for b in self.org.births[births_before:]]
            edges_born = len(self.org.edges_log) - edges_before
            edges_pruned = len(self.org.prunes_log) - prunes_before
            journal_row = {
                "seq": row["seq"], "moment": moment, "word": word,
                # PREREG-WORD-ROAD §1.10 (the gene HEAR): the words the organism met at this canvas; absent without the line
                **({"words": list(hear_words), **({"words_refused": list(hear_refused)} if hear_refused else {})}
                   if hear_words is not None else {}),
                "fix": [[int(y), int(x)] for (y, x) in g["fix"]],
                "births": births,
                "cells": [int(self.org.sight.alive.sum()), int(self.org.words.alive.sum())],
                "edges": [edges_born, edges_pruned],
                "err": round(err, 4), "lr": round(lr_scale, 3), "ep": ep_id,
                "hash": self._row_digest(),   # M3: the canvas row's digest — the coarse row below carries it (one hash per canvas)
                **({"arrival": arrival_n} if arrival_n is not None else {}),   # PREREG §15: an event field on the row where an arrival opened
                # G-EYE-1 (edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 20:57 +0400): every glance's window origin, this
                # episode's when/act/source — EXTRA keys, never touching any key above; a genome that never declares DELIVER
                # writes exactly the dict this branch always wrote (the parity test pins it).
                **({"windows": [[int(t), int(l)] for (t, l) in g["windows"]], "when": row["at"], "act": "glance",
                    "source": meta.get("source"), "glance": 0} if deliver_on else {}),
                # L-4 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): residual/confirmed
                # on every eye moment row — the brief's own words — sliced to the four LOCATED glances
                # (len(g["fix"])); the coarse glance's own residual/confirmed live on its own row, below.
                # Undeclared SURPRISE: this key is absent, byte-identical to before this gene existed.
                **({"residual": residuals[:len(g["fix"])], "confirmed": confirmed_flags[:len(g["fix"])]} if surprise_gene is not None else {}),
                # A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:36 +0400): the sound bound at this
                # canvas — its tape row's seq, the sound winners of its glances, the sound area's alive count. Absent (no key at
                # all) on every canvas without a sound: a genome/tape without the voice writes exactly the row it always wrote.
                **({"sound": {"seq": int(snd["seq"]), "winners": [int(u) for u in sound_winners],
                              "cells": int(self.org.sound.alive.sum()) if self.org.sound is not None else 0}} if snd is not None else {}),
                # OW-3 (edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400): PREREG-OPEN-WORLD-3
                # §2.7's ONE additive key — when (and only when) the front is wired, this canvas's instrument values
                # (t_mass = mean|T-ON|+mean|T-OFF|; o = the operating point the front's state now holds). Absent
                # otherwise: the identity gates cover both cases.
                **({"front": {"t_mass": self.eye_front.last_t_mass, "o": self.eye_front.last_o}} if self.eye_front is not None else {}),
            }
            self._write_journal(row["at"], journal_row)
            coarse_row = self._coarse_row(row["seq"], moment, residuals, confirmed_flags, surprise_gene, digest=journal_row["hash"])
            if coarse_row is not None:
                self._write_journal(row["at"], coarse_row)
        elif fast_on:
            # PREREG §11.1 step 2: sight-only, FAST declared -> Organism.moment_sight per glance (B2),
            # never Organism.moment (no word to MEET); an episode is still written, word "". A sight-only
            # glance can still BIRTH a sight cell (moment_sight's own _resonate call), and
            # questions.build_ledgers needs moment_thing[m] for EVERY birth moment, sight-only ones
            # included, or snapshot() KeyErrors the first time such a birth happens (caught by this
            # test, not by inspection) -- word "" here, exactly what the written episode itself carries.
            births_before = len(self.org.births)
            # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:36 +0400 — A4L-VOICE task 3: under `--blind ear` a
            # worded canvas with no sound comes here; the runner still books its label (the ledger) and its arrival (the world's
            # clock). Not blind: `label` is None on this road (no word came), so both lines are no-ops — byte-for-byte the old road.
            if label is not None and label not in self._heard:
                self._heard.add(label)
                if "ARRIVAL" in self.genome.declared:
                    self.org.new_arrival()
            for x in org_feats:
                self.moment_word[self.org.t] = label if label is not None else ""
                self.org.moment_sight(x)
            births_after = len(self.org.births)
            self._ledger_births(births_before, meta.get("source"))      # A42-B2: the birth-source ledger, the sight-only road
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
                    ledgers = self.ledgers()
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
            sight_row = {   # M3: bound to a name so the coarse row below can carry this row's digest (the same dict, the same bytes)
                "seq": row["seq"], "moment": moment, "word": None,
                "err": round(err, 4), "ep": ep_id, "hash": self._row_digest(),
                **({"windows": [[int(t), int(l)] for (t, l) in g["windows"]], "when": row["at"], "act": "glance",
                    "source": meta.get("source"), "glance": 0} if deliver_on else {}),
                # L-4: a sight-only canvas has no word, so `predicted` is always None here and no glance
                # ever confirms — the fields are still journaled (gated the same way) for schema parity.
                **({"residual": residuals[:len(g["fix"])], "confirmed": confirmed_flags[:len(g["fix"])]} if surprise_gene is not None else {}),
                # OW-3 (edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-08 01:08 +0400): §2.7's one additive
                # key on the sight-only glance row too — every eye row's journal glance row carries it when (and
                # only when) the front is wired, so the front's instrument stream lines up 1:1 with the residual
                # stream the cutter reads (tools/worlds/event_cutter.py's err_series).
                **({"front": {"t_mass": self.eye_front.last_t_mass, "o": self.eye_front.last_o}} if self.eye_front is not None else {}),
            }
            self._write_journal(row["at"], sight_row)
            coarse_row = self._coarse_row(row["seq"], moment, residuals, confirmed_flags, surprise_gene, digest=sight_row["hash"])
            if coarse_row is not None:
                self._write_journal(row["at"], coarse_row)
        else:
            # the skeleton's own law, untouched: no FAST declared -> a sight-only canvas is skipped
            # entirely, the organism never sees it (G4-8's byte-identical pin depends on this).
            self.sight_only_skipped += 1
            self._write_journal(row["at"], {"seq": row["seq"], "moment": moment, "sight_only": True})

        self._canvas_index += 1
        self._maybe_sleep(row)
        self._maybe_think(row)

    def _row_digest(self) -> str:
        """M3 (edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400; ALPHA4-2-PREREG.md §2 M3, §2.5): the row's witness digest —
        `Organism.row_hash()` (the sparse witness under HASH, the dense state_hash otherwise) — and, in the SAME statement, the moment
        count it stands for. `_coarse_row` reuses this digest for the coarse row of the same canvas while `org.t` is unchanged; a
        digest obtained any other way meets a stale `_row_digest_t` and is refused (recomputed), so no caller can bypass the guard."""
        digest, self._row_digest_t = self.org.row_hash(), self.org.t
        return digest

    def _coarse_row(self, seq: object, moment: Optional[str], residuals: list, confirmed_flags: list,
                     surprise_gene: Optional[dict], *, digest: str) -> Optional[Dict[str, object]]:
        """L-7 (edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400): the fifth, whole-canvas
        glance's OWN journal row — SLEEP's own "a second mind row sharing the triggering canvas's own seq"
        pattern (creature.replay's compare() already groups mind rows by seq for exactly this reason).
        `act: "coarse"`, `glance: 4` (the coarse feature's own index — always LAST in g["feats"]/residual,
        after the four located glances), `fix: null`, `windows: null` (it has no location) — the brief's
        own field shapes. None (nothing journaled) when GAZE's coarse clause is undeclared, or blind to it
        ("coarse" in self.blind — the coarse feature was already stripped from org_feats above, so there is
        nothing to report)."""
        gaze_decl = self.genome.gaze or {}
        if "coarse" not in gaze_decl or "coarse" in self.blind:
            return None
        # M3 (edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400): `digest` is the canvas row's own (`_row_digest()` in the caller's dict) —
        # the two rows hashed the same state one statement apart on 9,331 of 9,331 alpha4-1 canvases (ALPHA4-2 review §2). The reuse
        # is REFUSED — recomputed, counted — if the organism lived a moment since (PREREG §2.5: "a planted write between the two rows
        # makes the reuse REFUSE, so the reuse can never hide a change"); on the live road nothing between them touches it.
        if self.org.t != self._row_digest_t:
            self.hash_reuse_refused += 1
            digest = self._row_digest()
        idx = len(residuals) - 1
        out: Dict[str, object] = {"seq": seq, "moment": moment, "act": "coarse", "glance": idx,
                                   "fix": None, "windows": None, "hash": digest}
        if surprise_gene is not None:
            out["residual"] = residuals[idx]; out["confirmed"] = confirmed_flags[idx]
        return out

    # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6 (EVOLVE).
    def _consume_proposal(self, row: Dict[str, object]) -> None:
        """A 'proposal' tape row, published by creature/senses/evolve.py (a SENSE in the writer law's
        sense — it never touches state/journal/memory itself; it only reads $ROOT/evolve/PROPOSAL-<n>.json
        files tools/evolve.py's worker wrote and republishes them onto the tape). EVOLVE must be declared,
        else this sense-name row is a fact on the tape with no consumer here (the same "a door row carries
        no organism work" law every other unarmed sense follows, W3-0's own law one level up). Only a PASS
        verdict is remembered for adoption — a REFUSED proposal is still counted (`evolve_proposals_seen`,
        STATUS's own #164 field) but never adopted. A LATER proposal (PASS or not) simply overwrites the
        pending one — the tape's own order decides which mutation reaches the next sleep boundary, exactly
        as a live worker and a replay of the same tape must agree (both consume rows in the same seq order)."""
        if "EVOLVE" not in self.genome.declared:
            return
        meta = row.get("meta") or {}
        self.evolve_proposals_seen += 1
        if meta.get("verdict") == "PASS":
            self._evolve_pending_proposal = dict(meta)

    def _maybe_adopt_evolve_proposal(self, row: Dict[str, object]) -> None:
        """ALPHA4-PREREG.md §6: ADOPTION at the next SLEEP boundary — if a 'proposal' row with verdict PASS
        has arrived since the last sleep and no epoch has adopted it yet, adopt it: write
        GENOME.v<n>.genome (the mutant TEXT, never a dict — brief item 1), re-parse self.genome/self.org.g
        from it (only VALUE genes ever change here: BOUNDS excludes every gene that could change a moment's
        or an array's shape, so this re-parse is always safe by construction), journal the epoch as a MIND
        row — never a top-level "event" key (PREREG §2.4's own discriminator: the BODY writes "event" rows,
        and creature.replay.read_mind_journal() drops any row that carries one; nesting it under "epoch"
        keeps this a first-class, replay-comparable MIND row, which is what "REPLAY identical … including
        the epoch event" (brief item 3) requires in practice — PREREG §6's own JSON sketch names the
        SEMANTIC event, not a literal dict key) — and live-patches the two stateful objects whose OWN gene
        value is cached at construction time rather than read live: genome/park.py's Park.n and
        genome/curiosity.py's Interests.n (checked against their source before writing this; every other
        mutable gene is read LIVE off self.g/self.genome.declared each time it is used, so the re-parse
        alone is enough for those)."""
        proposal = self._evolve_pending_proposal
        if proposal is None:
            return
        self._evolve_pending_proposal = None
        mutant_text = str(proposal.get("mutant_genome_text", ""))
        gene_key = proposal.get("gene")
        value = proposal.get("value")
        try:
            new_genome = parse_genome(mutant_text)
        except GenomeError as e:
            # a proposal whose mutant text does not parse is a worker bug, never a live crash — journaled, not adopted.
            self._write_journal(row["at"], {"seq": row["seq"],
                                             "epoch_refused": {"reason": f"mutant genome text did not parse: {e!r}",
                                                                "gene": gene_key, "value": value, "proposal_no": proposal.get("no")}})
            return
        self.evolve_epoch += 1
        genome_sha = hashlib.sha256(mutant_text.encode("utf-8")).hexdigest()
        (self.run_root / f"GENOME.v{self.evolve_epoch}.genome").write_text(mutant_text)
        self.genome_text = mutant_text
        self.genome = new_genome
        self.org.g = new_genome
        if gene_key == "PARK.after" and self.park is not None:
            self.park.n = int(new_genome.declared["PARK"]["after"])
        elif gene_key == "CURIOSITY.interests" and self.interests is not None:
            self.interests.n = int(new_genome.declared["CURIOSITY"]["interests"])
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "epoch": {"epoch": self.evolve_epoch, "genome_sha": genome_sha, "moment": self.org.t,
                      "gene": gene_key, "value": value, "proposal_no": proposal.get("no")},
            "hash": self.org.row_hash(),
        })

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
            # A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:34 +0400): `--blind ear` replays with no word
            births_before_sleep = len(self.org.births)
            result = run_sleep(self.org, self.episodes, n, **({"words": False} if "ear" in self.blind else {}))
            self.sleep_count += 1
            cycled = run_cycle(self.org)
            self._ledger_births(births_before_sleep, "sleep")     # A42-B2: a birth inside the replay is owned by no canvas — "sleep", chain.birth_sources' own word
            if "TRAITS" in self.genome.declared and _TRAITS_AVAILABLE:
                Traits.learn(self.episodes)      # per the interface name given for wave 2; unexercised until genome/traits.py lands
            self._write_journal(row["at"], {
                "seq": row["seq"], "sleep": {**result, "cycle": cycled}, "hash": self.org.row_hash(),
            })
            # edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 23:05 +0400 — W3-3 (docs/G4-WAVE3-CLAUSES.md;
            # genome/curiosity.py's own contract, B10 note 3): one sleep_boundary() call per boundary crossed
            # (this loop iterates once per boundary), so a recombine chain never pairs an "answered" item from
            # before this boundary with one from after it.
            if self.interests is not None:
                self.interests.sleep_boundary()
            # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6: adoption
            # happens LAST in a boundary's own processing (this SLEEP/CYCLE/CURIOSITY-window-close all run
            # under the genome this boundary was ENTERED with; a pending mutation, if any, then takes over
            # from the next moment on) — a no-op call when EVOLVE is undeclared or no PASS proposal is pending.
            self._maybe_adopt_evolve_proposal(row)
            # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1.4:
            # the muse's promotion check rides THIS consolidation pass (condition (ii): a pass ran since the
            # filing). Behind the flag alone; flag OFF: not one line runs.
            if self.muse:
                self._muse_promote(row)

    # ------------------------------------------------------------------ THINK (A11, PREREG §11.1 step 3)
    def _score_due_predictions(self, word: str, first_glance: Optional[np.ndarray],
                                 words_in_instant: Optional[List[str]] = None,
                                 glances: Optional[List[np.ndarray]] = None, source: Optional[str] = None) -> None:
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
        # edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:05 +0400 — G9 (ALPHA4-2-PREREG §2 row G9): under `SENTENCE …;
        # judged by the eye on the line` a SHELF instant scores a frame only when it is a LINE — the reader's sentence moment,
        # >= 2 distinct words on the canvas (creature/senses/read.py:_publish_chunk publishes every word of a chunk ALONE first,
        # shown large, then the whole line; a frame was due on w1's one-word canvas, where w2 cannot be: alpha4-1 0 of 63 shelf
        # frames true, 4 of 4 false on the hour-1 replay) — and its evidence is ANY of the line's located glances
        # (_frame_evidence_line; the ceiling: 0.272 strict over located glances on the 10:54 copy, 0.089 with glance 0 alone).
        # SHELF-only by the seat's word: every other source (the game's mission with its picture, a lexicon gloss, a test tape)
        # keeps today's trigger and today's decider on the same lines below. Undeclared: `line_on` is False and nothing here moves.
        line_on = self.genome.declared.get("SENTENCE", {}).get("line") is True
        shelf_line = None
        if line_on and source == "shelf":
            shelf_line = len([w for j, w in enumerate(words_in_instant) if w and w not in words_in_instant[:j]]) >= 2
        for entry in self._filed_predictions:
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 3 (SENTENCE): a
            # frame entry's target_word is w1, the COLOUR — never equal to `word` (the moment's own word is
            # the OBJECT, game.py's own publish order). Its trigger is "w1 in this instant's words", not
            # "word == w1"; every other entry keeps the original word==target_word trigger, unchanged.
            frame_w2 = entry.get("frame_w2")
            if frame_w2 is not None:
                due = entry["target_word"] in words_in_instant
                if shelf_line is False:      # G9: a one-word SHELF moment never scores a frame under the clause
                    due = False
            else:
                due = entry["target_word"] == word
            if due and self._canvas_index >= entry["due_canvas"]:
                rule = entry.get("rule")
                if frame_w2 is not None:
                    if shelf_line:
                        evidence = self._frame_evidence_line(str(frame_w2), glances if glances else [first_glance])
                    else:
                        evidence = self._frame_evidence(str(frame_w2), first_glance)
                elif rule is not None:
                    evidence = self._rule_evidence(rule["cluster"], first_glance)
                else:
                    if ledgers is None:
                        ledgers = self.ledgers()
                    r = self.org.recall("sight", first_glance)
                    Lw = ledgers["words"]
                    evidence = r["cell"] is not None and Lw.get(r["cell"], set()) == {word}
                scored = predict_score(entry["row"], evidence)
                if line_on and frame_w2 is not None:
                    # G9: the instant a frame was judged on, stamped on its scored row (the DECLARED replay's own record of shelf
                    # true/false by source and kind; tools read predictions.jsonl, never the journal) — absent undeclared.
                    scored["instant"] = {"source": source, "words": list(words_in_instant), "line": bool(shelf_line)}
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
        ledgers = self.ledgers()
        r = self.org.recall("sight", first_glance)
        Lw = ledgers["words"]
        return r["cell"] is not None and Lw.get(r["cell"], set()) == {w2}

    def _ledger_births(self, births_before: int, source: Optional[str]) -> None:
        """A42-B2 (edit: Claude (Fable 5.1), 2026-09-23 17:05 +0400): every SIGHT cell born since `births_before` is filed under
        `source` in the birth-source ledger, FIRST birth only (an id is never reborn — G4 §3 B7 — so the guard is a formality).
        A ledger write only: no organism state, no journal field, no hash."""
        for _t, area, cid, _reason in self.org.births[births_before:]:
            if area == "sight" and int(cid) not in self.birth_source:
                self.birth_source[int(cid)] = str(source) if source is not None else ""

    def _frame_evidence_line(self, w2: str, glances: List[np.ndarray]) -> bool:
        """edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:05 +0400 — G9's decider on a LINE: `_frame_evidence`'s strict
        decider (the answer cell's ledger is exactly {w2}) asked of EVERY located glance of the line — true if any answers w2.
        The line's MEET binds the canvas's glances to the chunk's LAST word only (`pending` is last-wins), so w2 elsewhere on the
        line can be read only from what the eye learned of w2 on its own one-word showings — the measured ceiling (A42-B2-REPORT):
        0.430 when w2 is the last word, 0.183 when it is not; glance 0 alone reads 0.089, below the bar, which is why this asks
        every glance. A scoring read never changes the organism (Organism.recall's own law)."""
        ledgers = self.ledgers()
        Lw = ledgers["words"]
        for x in glances:
            if x is None:
                continue
            r = self.org.recall("sight", x)
            if r["cell"] is not None and Lw.get(r["cell"], set()) == {w2}:
                return True
        return False

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
    def _write_ask_out(self, payload: Dict[str, object]) -> int:
        """Writes ONE `run/ask/out/q-<n>.json` row -- the SAME JSON shape `run/ask/in/` accepts (creature/
        ask.py's own inbox schema), but this mind is the WRITER here, not the answerer: the world-maker's
        door (creature/world_maker.py:sense) and, for a `what-is` no sense drew, the human ASK door's own
        listener, are its readers. `n` is `self._ask_out_n`, a mind-local FILENAME counter shared by every
        writer of a q-file (never the tape row's own seq -- two wants can form on the same tape row,
        advisor's point 5), so no two writes ever collide on a name. Returns the `n` used (edit: Claude
        (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:1x +0400 — ALPHA4-H task 3: additive, every existing
        caller discards it as a bare statement, exactly like Organism.moment's own S/T return did when it
        was added).
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
        return n

    # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:1x +0400 — ALPHA4-H task 3 (docs/briefs/
    # ALPHA4-H.md; ALPHA4-PREREG.md §3 DOOR lexicon): the RAISED clause. The brief's own words: "watches the
    # QUESTION queue C landed (read its format from the code; if questions are only journaled and not
    # written as files, RAISE it and write the smallest queue...)". Read from the code (this file, L-10):
    # questions ARE written as files (`_write_ask_out`, just above) -- but the file's `args` carries a TAPE
    # MOMENT (`_maybe_ask_word`'s own `[tape_moment]`), never the word text a dictionary lookup needs; the
    # brief's own contingency assumed "files vs. no files", not "files keyed by the wrong thing". The
    # narrower gap the brief authorizes fixing is real, so this write lands: a SEPARATE, additive outbox
    # (`run/world/questions/`, never touching `run/ask/out/` -- world_maker's own door polls THAT directory
    # matching `args[0]` against ITS OWN drawn-moment shape, and must never be handed a word-keyed want to
    # misinterpret) carrying the word `_maybe_ask` already resolved. A PURE, deterministic write of
    # information already computed this call (payload's own `seq`, `why_word`) -- no new randomness, no new
    # wall-clock read -- so replay stays identical; gated on 'DOOR_LEXICON' in self.genome.declared (W3-0's
    # law: an undeclared gene changes nothing -- life 3a's replay, which never declares it, writes nothing
    # new here, the closed-tape regression's own requirement).
    def _write_lexicon_want(self, n: int, word: str) -> None:
        q_dir = self.run_root / "world" / "questions"
        q_dir.mkdir(parents=True, exist_ok=True)
        (q_dir / f"q-{n}.json").write_text(json.dumps({"q": "what-is", "word": word}))

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
            ledgers = self.ledgers()
            record = questions_why(self.org, ledgers, self.episodes, why_word)
            payload["why"] = {
                "cells": [[area, int(c)] for area, c in record["cells"]],
                "episodes": list(record["episodes"]),
                "edges": [[int(s), int(t), float(w)] for s, t, w in record["edges"]],
            }
        n = self._write_ask_out(payload)   # advances self._ask_out_n itself (see that method's own comment)
        # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:1x +0400 — ALPHA4-H task 3: the lexicon
        # door's own queue (see _write_lexicon_want's own comment for the RAISED clause this answers) --
        # only a real "what-is <word>" want (why_word resolved -- never the sight-only "show me this
        # picture again" want at line ~1078, which has no why_word and is world_maker's/folder's domain).
        if form == "what-is" and why_word is not None and "DOOR_LEXICON" in self.genome.declared:
            self._write_lexicon_want(n, why_word)
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
                if eid in self._confirmed_episodes:
                    continue   # L-4: "no think-pool item" for a CONFIRMED glance — this episode's word was already expected and matched
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
                if eid in self._confirmed_episodes:
                    continue   # L-4: same law for a sight-only episode (never actually reachable — a confirmed episode always carries a word — kept for symmetry)
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
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF: a "self" kind item, ONE at
        # a time, present only once a comparable PAIR of body readings exists and that pair has not already
        # been worked (`_self_worked_seq` -- else the same comparison would re-enter the pool at every THINK
        # boundary between body rows, since body arrives far less often than THINK fires). Kind-fair with
        # word/sight/due/rule/outcome via `_think_choose`'s own kind-first draw -- no special-casing needed.
        if "SELF" in self.genome.declared and len(self._body_pair) >= 2 and self._body_pair[-1][0] != self._self_worked_seq:
            pool.append({"kind": "self", "key": "body", "episode": None, "pred": None})
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item
        # 2 (L-12): the 'hands' kind — ONE item, present iff HANDS declares a shelf (_hands_shelf_dir is
        # not None) AND no run is already in flight (_hands_pending is None, #175: never offer a second
        # choice before the sense thread has answered the first). `_think_work` picks the program;
        # `_maybe_think` writes run/hands/ACT once `_think_choose` has picked this item over any other kind
        # present (#175/E's seam note: the think step returns a decision, never writes state itself, so
        # this item carries no filesystem side effect until _maybe_think applies it).
        if self._hands_shelf_dir is not None and self._hands_pending is None:
            pool.append({"kind": "hands", "key": "run", "episode": None, "pred": None})
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
            ledgers = self.ledgers()
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

        if item["kind"] == "self":
            # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF (docs/briefs/LIFE-A-ANSWER-SELF.md
            # #3): the mind reads its own body. Compares the last TWO recorded body readings; on a trigger, files
            # a belief ("word" encodes which trigger -- believe() carries no separate reason field) with cells=[]
            # (a self belief names no sight cell -- it is about the mind, not a picture) and the two body rows'
            # OWN seq numbers as its "episodes" (the citation the toy's own words ask for: "citing the rows").
            # Marks the pair WORKED regardless of outcome, so an unchanging pair (nothing to report) or a repeat
            # of the same trigger (a revisit, believe()'s own dedupe) never re-enters the pool on the next THINK
            # boundary before a NEW body row arrives.
            (seq1, r1), (seq2, r2) = self._body_pair[-2], self._body_pair[-1]
            self._self_worked_seq = seq2
            word = self._self_trigger(r1, r2)
            if word is None:
                return {"outcome": "no_change", "parked": False}
            if not _THINK_LAWS_AVAILABLE:
                return dead_end(word, "think_laws_unavailable")
            if "BELIEF" not in self.genome.declared:
                return dead_end(word, "no_belief_gene")
            extra_kwargs = {}
            if "clash_enabled" in _BELIEVE_KWARGS:
                extra_kwargs["clash_enabled"] = "BELIEF" in self.genome.declared
            row = think_laws.believe(word, [], [seq1, seq2], self.org.t,
                                      self.run_root / "state" / "beliefs.jsonl", **extra_kwargs)
            KIND_TO_COUNTER = {"belief": "beliefs", "revisit": "revisits", "extension": "extensions", "clash": "clashes"}
            kind = row.get("kind", "belief") if isinstance(row, dict) else "belief"
            self.think_counters[KIND_TO_COUNTER.get(kind, "beliefs")] += 1
            return {"outcome": "belief", "parked": False, "belief": row}
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item
        # 2 (L-12; MOTOR-HANDS.md G-MOT-4): the 'hands' branch PICKS a program and RETURNS the decision --
        # it never touches the filesystem itself (E's seam note, docs/organs/NEXT-LIFE-PLAN-2026-09-22.md
        # §4 L-5: "the think thread writes nothing; the mind applies" — _maybe_think is what writes
        # run/hands/ACT, after this method returns, so today's synchronous THINK and tomorrow's threaded
        # one apply the decision through the exact same seam). "A declared `run` with no jail binary
        # journals «no road» once and never crashes" (the brief's own words, verbatim as the dead-end
        # reason): checked EVERY time a 'hands' item is worked (the jail binary can appear or vanish
        # between attempts; never assumed permanent from one reading). Exactly TWO `_hands_rng` draws per
        # choice regardless of branch (`_maybe_choose_act`'s own discipline, one line up in this file) —
        # explore (10% re-run of the last program, "so the positive control fires", the brief's own words)
        # or exploit (uniform over the shelf) — so the stream's shape never depends on which branch fires.
        if item["kind"] == "hands":
            if self._hands_jail_path is None or not self._hands_jail_path.exists():
                self.hands_no_road += 1
                return dead_end("run", "no road")
            names = sorted(p.stem for p in self._hands_shelf_dir.glob("*.py")) if self._hands_shelf_dir is not None else []
            if not names:
                return dead_end("run", "no_shelf")
            u = float(self._hands_rng.random())
            idx = int(self._hands_rng.integers(0, len(names)))
            program = self._hands_last_program if (u < 0.1 and self._hands_last_program in names) else names[idx]
            self._hands_last_program = program
            return {"outcome": "run", "parked": False, "program": program}

        return dead_end(str(item.get("key")), "unknown_kind")

    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF: the two COMPARISON triggers
    # (stall, no_room), in the plan's order. Each reads only the two given readings (never STATUS, never
    # the live queue) so a replay of the same recorded pair always decides the same (G-MIND-6's twin).
    # The THIRD trigger ("I am behind") is NOT a comparison -- see `_file_behind_belief` below and its own
    # comment: a comparison reading the same field/threshold as the skip is always preempted by the skip
    # (the report's §3 clause 6 finding); the coordinator's fix files it on RESUME instead.
    _SELF_STALL_KEYS = ("moments", "births", "arrivals")

    # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 02:40 +0400 — ALPHA4-G.md task 5
    # (docs/ALPHA4-PREREG.md §2/§3): a FOURTH trigger — "self:no_budget", read from `refused` (the body
    # row's own field name for STATUS's births_refused_budget, BODY-SENSES §4.1's SENSE body field list) —
    # beside the existing `refused_nmax` ("self:no_room"). Checked AFTER no_room, so a pair where BOTH
    # rise on the same comparison (a life starved of room and budget at once) still returns exactly one
    # word (believe() carries no second reason field) — DETERMINISTIC, never a set/dict iteration order.
    def _self_trigger(self, r1: Dict[str, object], r2: Dict[str, object]) -> Optional[str]:
        stalled = [k for k in self._SELF_STALL_KEYS if r1.get(k) is not None and r2.get(k) is not None and r1[k] == r2[k]]
        moved = [k for k in self._SELF_STALL_KEYS if r1.get(k) is not None and r2.get(k) is not None and r1[k] != r2[k]]
        if stalled and moved:
            return f"self:{stalled[0]}_stopped"
        n1, n2 = r1.get("refused_nmax"), r2.get("refused_nmax")
        if n1 is not None and n2 is not None and n2 > n1:
            return "self:no_room"
        b1, b2 = r1.get("refused"), r2.get("refused")
        if b1 is not None and b2 is not None and b2 > b1:
            return "self:no_budget"
        return None

    # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — the coordinator's fix (docs/briefs/
    # LIFE-A-REPORT.md §3 clause 6).
    def _file_behind_belief(self) -> Dict[str, object]:
        """L-9/SELF, the coordinator's fix (2026-09-22): "I am behind" fires at the FIRST think that RUNS
        after a run of skips, never at a crossing -- the crossing and the skip read the SAME recorded
        field (`_last_body_reading["backlog"]`) against the SAME threshold, so the crossing boundary is
        always the one the skip claims instead (the unreachable trigger this replaces). Cites the
        DISTINCT body rows the skips actually read (backlog over the threshold) -- never the resuming,
        now-under-threshold row, which is not one of them. `cells=[]` (a self belief names no sight cell)."""
        seqs = sorted(set(self._skip_run_seqs))
        note = (f"I was behind: max backlog {self._skip_run_max_backlog} rows over "
                f"{self._skip_run_skips} skipped thinks, from seq {seqs[0] if seqs else None} to seq {seqs[-1] if seqs else None}")
        if not _THINK_LAWS_AVAILABLE:
            return {"outcome": "think_laws_unavailable", "note": note}
        if "BELIEF" not in self.genome.declared:
            return {"outcome": "no_belief_gene", "note": note}
        extra_kwargs = {}
        if "clash_enabled" in _BELIEVE_KWARGS:
            extra_kwargs["clash_enabled"] = "BELIEF" in self.genome.declared
        row = think_laws.believe("self:behind", [], seqs, self.org.t,
                                  self.run_root / "state" / "beliefs.jsonl", **extra_kwargs)
        KIND_TO_COUNTER = {"belief": "beliefs", "revisit": "revisits", "extension": "extensions", "clash": "clashes"}
        kind = row.get("kind", "belief") if isinstance(row, dict) else "belief"
        self.think_counters[KIND_TO_COUNTER.get(kind, "beliefs")] += 1
        return {"outcome": "belief", "belief": row, "note": note}

    def _file_rule(self, row: Dict[str, object], want: str, op: str, due_canvas: Optional[int] = None) -> None:
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
        in the report, not fixed here: changing it changes what a live rule's existing consumers see.)

        edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5: `due_canvas`, optional,
        defaulting to `self._canvas_index` (byte-identical to every call site before this brief — the sole
        inline caller, `_think_work`'s "rule" branch, never passes it). The THREADED road's own caller
        (`_think_apply_plan`) passes the LAUNCH boundary explicitly: this method is now called from
        `_think_apply_pending`, running at boundary N+every, where `self._canvas_index` would read
        N+every — the wrong content for a rule DECIDED from state at N (item 3's shift-equivalence gate:
        the filed row's own content must match what inline-at-N would have produced, only its journal
        seq/launched_at move)."""
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
                "row": row, "target_word": str(target_word),
                "due_canvas": self._canvas_index if due_canvas is None else int(due_canvas),
                "rule": {"op": op, "want": want, "cluster": cluster},
            })
        self.think_counters["predictions_filed"] += 1

    def _maybe_think(self, row: Dict[str, object]) -> None:
        """PREREG §11.1 step 3: every THINK.every canvases. THINK's own gene clause parses since Builder
        B's B9 (genome/machinery.py) — the INLINE road below is byte-identical to what it has always been;
        L-5 (docs/briefs/LIFE-E-THINK-THREAD.md) adds a SECOND road, `_maybe_think_threaded`, taken only
        when `self._think_threaded` (the genome's own "; on its own thread; lands next boundary" tail)."""
        if "THINK" not in self.genome.declared:
            return
        every = int(self.genome.declared["THINK"]["every"])
        if every <= 0 or self._canvas_index % every != 0:
            return
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — L-9/SELF (docs/briefs/LIFE-A-ANSWER-SELF.md
        # #3): the ONE decision -- skip THINK entirely (never even building the pool) while the LAST RECORDED body
        # reading's backlog stays over SELF's own threshold. Read from `_last_body_reading` (written only by
        # `_consume_body`, never the live queue's own qsize()) so a replay of the same tape makes the same
        # decision at the same boundary (G-MIND-6's trap: a drive that reads its own live state and lowers its
        # own work would stabilise on doing nothing, and would decide DIFFERENTLY on a replay that reads the
        # recording instead of a live queue -- #171's class). A skip is counted, never counted as a think.
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 19:37 +0400 — the coordinator's fix: the run of
        # skips is tracked (`_skip_run_*`, __init__); the FIRST think that RUNS after a run (the branch below,
        # still gated on SELF and still read from the recorded row) files the "I am behind" belief and resets
        # the run -- never a comparison, so it is never preempted by the skip it follows.
        if "SELF" in self.genome.declared and self._last_body_reading is not None:
            backlog = self._last_body_reading.get("backlog")
            threshold = int(self.genome.declared["SELF"]["backlog_threshold"])
            if backlog is not None and backlog > threshold:
                self._skip_run_skips += 1
                seq = self._body_pair[-1][0] if self._body_pair else None
                if seq is not None:
                    self._skip_run_seqs.append(seq)
                self._skip_run_max_backlog = backlog if self._skip_run_max_backlog is None else max(self._skip_run_max_backlog, backlog)
                self.think_counters["think_skipped_for_backlog"] += 1
                self._write_journal(row["at"], {"seq": row["seq"], "think": {"item": None, "kind": None, "outcome": "skipped_backlog", "parked": False}})
                return
            if self._skip_run_skips > 0:
                self.think_counters["thinks"] += 1
                result = self._file_behind_belief()
                self._write_journal(row["at"], {
                    "seq": row["seq"],
                    "think": {"item": "self", "kind": "self", "outcome": result.get("outcome"), "parked": False, "note": result.get("note")},
                })
                self._skip_run_seqs = []; self._skip_run_skips = 0; self._skip_run_max_backlog = None
                return
        # edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5: the threaded road is a
        # SEPARATE method (below), taken here BEFORE the pool is ever built on this thread — everything
        # from this line down is the ORIGINAL inline road, untouched, byte-identical to before this brief
        # (G4-8's own law: absent the genome's threaded tail, nothing here changed).
        if self._think_threaded:
            self._maybe_think_threaded(row)
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
        journal_obj: Dict[str, object] = {
            "seq": row["seq"],
            "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": result.get("outcome"), "parked": bool(result.get("parked"))},
        }
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item
        # 2 (L-12): the ONE place a 'hands' decision touches the filesystem (E's seam note, quoted at
        # _think_work's own 'hands' branch above) — the atomic write-tmp-then-replace pattern
        # `_maybe_choose_act` already uses for run/game/ACT, applied here to run/hands/ACT. `_hands_pending`
        # is set so `_think_pool` offers no second 'hands' item until the matching outcome row (its own
        # `act_seq` == this seq) is consumed — see `_consume_outcome`'s own clearing branch, below.
        # `act_chosen` is journaled BESIDE `think` (the brief's own words: "journaled `act_chosen: {run,
        # program, seq}`") in the SAME row, never a second journal write for one think pass.
        self._land_hands_run(row, item, result, journal_obj)   # F's hands act — ONE helper for both think roads (the E×F seam)
        self._write_journal(row["at"], journal_obj)

    def _land_hands_run(self, row: Dict[str, object], item: Dict[str, object], result: Dict[str, object],
                        journal_obj: Dict[str, object]) -> None:
        """edit: Claude (Fable 5.1), 2026-09-23 04:21 +0400 — the E×F seam, found by the pre-flight life alpha4-pre-3: builder F put the
        hands' ACT write in `_maybe_think` (the inline road) and builder E's threaded entry copied the journal write for
        the non-word/self kinds "byte-identical to the inline road" — WITHOUT this block. Under a threaded genome every
        hands think journaled «run» and no ACT was ever written: 0 runs, 0 touch rows, the organ declared and dead. Both
        roads now call this one helper."""
        if item.get("kind") == "hands" and result.get("outcome") == "run":
            program = str(result["program"])
            seq = int(row["seq"])
            act_path = self.run_root / "hands" / "ACT"
            act_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = act_path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"seq": seq, "program": program, "at": row["at"]}))
            os.replace(str(tmp), str(act_path))
            self._hands_pending = {"seq": seq, "program": program}
            self.runs_chosen[program] = self.runs_chosen.get(program, 0) + 1
            journal_obj["act_chosen"] = {"act": "run", "program": program, "seq": seq}

    # ------------------------------------------------------------------ L-5: THE THINKING THREAD (threaded road)
    def _maybe_think_threaded(self, row: Dict[str, object]) -> None:
        """PREREG §19.2/plan §4 L-5: at boundary N (this call), FIRST apply the PREVIOUS boundary's think
        (if one is pending — waiting, blocking, if it is not back yet), THEN build the pool and choose an
        item HERE, live, on the mind's own thread (`_think_pool`/`_think_choose` are cheap: no organism
        edge-matrix touch, and `_think_choose` mutates `self.interests` — a live write that must stay on
        this thread), and finally hand the CHOSEN item's own work to the think thread as a frozen copy
        (creature/think_thread.py) and continue — `consume()` returns right after `submit()`, it never
        waits for this boundary's own result (that happens at boundary N+every, above this method, in
        `_maybe_think`'s `if self._think_pending is not None:` gate — see `_think_apply_pending`)."""
        if self._think_pending is not None:
            self._think_apply_pending(row)
        pool = self._think_pool()
        item = self._think_choose(pool)
        self.think_counters["thinks"] += 1
        # MOUTH (`_maybe_say`) judges THIS canvas's OWN instant synchronously, every boundary, threaded or
        # not — its own law (docs/briefs/LIFE-C-QUESTION-SENTENCE.md task 4: "the songbird's loop ... no
        # external judge") is defined in terms of `self._last_words_in_instant`/`self._last_glance`, i.e.
        # the CURRENT canvas; deferring it to N+every would judge a DIFFERENT canvas's instant, changing
        # what it means, not merely when it runs. RAISED in the report: item 2's "say rows" among a think's
        # deferred writes is read here as the general class of writes a THINK tick can make, not a
        # directive to move MOUTH off its own synchronous law.
        self._maybe_say(row)
        if item is None:
            self._think_pending = None
            return
        # edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 21:2x +0400 — found empirically, closing a
        # real shift-equivalence break (item 3's gate; the LIFE-E-REPORT.md has the numbers): deferring
        # "sight"/"rule"/"frame"'s in-memory pool-gating bookkeeping (`_filed_predictions.append`,
        # `_induce_pending`/`_deduce_pending`/`_frame_pending` adds) to apply time (N+every) — as item 2's
        # letter asks for every kind — means the SAME candidate stays offered to `_think_choose` on every
        # threaded boundary between N and N+every where the inline road would already have excluded it
        # (or a "due" item can appear/vanish on a different boundary than inline). A different pool
        # COMPOSITION draws a different number of `self._think_rng` picks, desyncing every choice after
        # it from the inline trajectory — not a timing shift, a different life. None of these five kinds
        # (sight, due, rule, frame, outcome) touch the organism's edge matrix (§ the module docstring of
        # creature/think_thread.py) — the ring/pool-item lookups they need are already cheap and bounded,
        # so there is no real latency win in deferring them. SCOPE: only "word" and "self" — the two kinds
        # that DO need `Organism.recall_many`/`build_ledgers`/`questions_why` (an O(alive cells) read that
        # can grow as the organism does) — go through the launch/apply pipeline below; every other kind
        # calls the ORIGINAL, unmodified `_think_work` here, synchronously, and its journal row is written
        # at THIS boundary — byte-identical to the inline road's own handling of these five kinds. RAISED:
        # `creature/think_thread.py:decide()`'s sight/due/rule/frame/outcome branches and this file's
        # `_think_apply_plan`'s matching branches are BUILT and unit-tested for content-equivalence against
        # `_think_work` (see LIFE-E-REPORT.md), but are DEAD CODE on this scoped pipeline — a future
        # session that fixes the pool-gating timing (mark `_filed_predictions`/`_frame_pending` bookkeeping
        # synchronously too, the same pattern this fix already applies to `_self_worked_seq`/rule/frame's
        # pending sets) can re-route them through the thread without rewriting them.
        if item.get("kind") not in ("word", "self"):
            result = self._think_work(item)
            self._think_pending = None
            journal_obj_t: Dict[str, object] = {
                "seq": row["seq"],
                "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": result.get("outcome"), "parked": bool(result.get("parked"))},
            }
            self._land_hands_run(row, item, result, journal_obj_t)   # edit: Claude (Fable 5.1), 2026-09-23 04:21 +0400 — the E×F seam (see the helper)
            self._write_journal(row["at"], journal_obj_t)
            return
        if item.get("kind") == "self":
            # LIFE-A-ANSWER-SELF.md #3's own law: `_self_worked_seq` is marked the MOMENT the pair is
            # chosen (unconditionally, whatever the outcome), so the SAME pair never re-enters the pool at
            # the next boundary — this is live pool-bookkeeping, not part of the item's WORK, so it happens
            # here, synchronously, exactly where `_think_work`'s own "self" branch used to do it.
            item = dict(item)
            item["body_pair"] = list(self._body_pair)
            self._self_worked_seq = self._body_pair[-1][0]
        frozen, self.think_freeze_ms_last = think_thread.freeze_inputs_timed(self, item, self._canvas_index)   # M5: timed in think_thread (the clock lives there)
        future = self._think_executor.submit(think_thread.worker_run, frozen)
        self._think_pending = {"future": future, "boundary": self._canvas_index, "item": item}

    def _think_apply_pending(self, row: Dict[str, object]) -> None:
        """Applies the ONE outstanding think (launched at `self._think_pending["boundary"]`, some earlier
        boundary N): waits for the future if it is not done yet (`think_waits`/`think_wait_ms` — the WAIT
        itself is timed by creature/think_thread.py's `wait_for`, never by this file, per the determinism
        law's own comment on the `concurrent.futures` import above), then performs the REAL writes the
        think decided on (`_think_apply_plan`) and journals the "think" row for the TRIGGERING (launch)
        item, stamped with `launched_at` so a reader can always tell which boundary decided it — the row
        itself is written now, at this (later) boundary's own `row["at"]`/`row["seq"]` (item 2's own words:
        "the files and journal rows are written then")."""
        pending = self._think_pending
        future = pending["future"]
        was_done = future.done()
        outcome = think_thread.wait_for(future)
        if not was_done:
            self.think_waits += 1
            self.think_wait_ms += outcome["wait_ms"]
        result = outcome["result"]
        self.think_ms_last = result.get("think_ms")
        if self.think_ms_last is not None:
            self._think_ms_history.append(float(self.think_ms_last))
            if len(self._think_ms_history) > 500:
                del self._think_ms_history[: len(self._think_ms_history) - 500]
        item = pending["item"]
        launched_at = pending["boundary"]
        if result.get("error") is not None:
            self._write_journal(row["at"], {
                "seq": row["seq"],
                "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": "error",
                          "error": result["error"], "parked": False, "launched_at": launched_at},
            })
            self._think_pending = None
            return
        plan = result.get("plan") or {}
        applied, self.think_apply_ms_last = think_thread.timed_call(self._think_apply_plan, item, plan, launched_at)   # M5: the ONE-WRITER's apply, timed in think_thread
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": applied.get("outcome"),
                      "parked": bool(applied.get("parked")), "launched_at": launched_at},
        })
        self._think_pending = None

    def _think_apply_plan(self, item: Dict[str, object], plan: Dict[str, object], launched_at: int) -> Dict[str, object]:
        """Performs the REAL write(s) `creature/think_thread.py:decide()` decided on (a plan, never a
        write itself — the ONE-WRITER law: this is the ONLY place that plan is ever acted on, and it runs
        on the mind's own thread). Mirrors `_think_work`'s branches field-for-field: same dead-end reason
        vocabulary, same PARK/ASK/believe()/predict_file() call shapes, same STATUS counters — the only
        difference is WHERE the deciding data came from (a frozen copy at `launched_at`, not live state
        now) and, for "rule"/"frame", that `due_canvas` is pinned to `launched_at` rather than read live
        off `self._canvas_index` at call time (`_file_rule`'s own `due_canvas=` parameter, added by this
        brief) — the INLINE road computes it at the boundary it runs on; this road must use the boundary
        the DECISION was made at, or a filed rule's own due_canvas would silently be `every` canvases later
        than the shift-equivalence gate expects (item 3)."""
        def dead_end(want: str, reason: str, ask_spec: Optional[Dict[str, object]]) -> Dict[str, object]:
            parked = False
            if self.park is not None:
                parked = self.park.answer(want, reason) == "parked"
                if parked:
                    self.think_counters["parked"] += 1
                    if ask_spec is not None:
                        if "args_word" in ask_spec:
                            w = str(ask_spec["args_word"])
                            self._maybe_ask_word(f"parked:word:{w}", w)
                        elif "args_tape_moment" in ask_spec:
                            self._maybe_ask(f"parked:sight:{item['key']}", "what-is", [ask_spec["args_tape_moment"]])
            return {"outcome": reason, "parked": parked}

        if "dead_end" in plan:
            d = plan["dead_end"]
            return dead_end(str(d["want"]), str(d["reason"]), d.get("ask"))

        if "not_yet_due" in plan:
            return {"outcome": "not_yet_due", "parked": False}

        if "no_change" in plan:
            return {"outcome": "no_change", "parked": False}

        if "reflected" in plan:
            r = plan["reflected"]
            return {"outcome": "reflected", "parked": False, "act": r["act"], "residual": r["residual"]}

        if "believe" in plan:
            if not _THINK_LAWS_AVAILABLE:
                return {"outcome": "think_laws_unavailable", "parked": False}
            b = plan["believe"]
            # believe()'s "ledgers" kwarg is its OWN drift check (rule 4: has one of this word's cells since
            # been reassigned to another word by a birth/merge that happened AFTER this belief's content was
            # decided?) — built LIVE, here, at apply time (cheap: O(births), no W/mask touch), deliberately
            # NOT from the frozen copy: a frozen ledger could never disagree with cells decided from that
            # SAME frozen state, which would make the drift check a no-op. This is the one place the
            # threaded and inline roads can genuinely diverge in CONTENT (revisit/extension/clash, never
            # whether a row is written at all) when births/merges land between launch and apply — named in
            # the report, not hidden.
            ledgers = self.ledgers() if item.get("kind") == "word" else None
            extra_kwargs: Dict[str, object] = {}
            if "ledgers" in _BELIEVE_KWARGS:
                extra_kwargs["ledgers"] = ledgers
            if "clash_enabled" in _BELIEVE_KWARGS:
                extra_kwargs["clash_enabled"] = "BELIEF" in self.genome.declared
            belief_row = think_laws.believe(str(b["word"]), list(b["cells"]), list(b["episode_ids"]), int(b["moment"]),
                                             self.run_root / "state" / "beliefs.jsonl", **extra_kwargs)
            KIND_TO_COUNTER = {"belief": "beliefs", "revisit": "revisits", "extension": "extensions", "clash": "clashes"}
            kind = belief_row.get("kind", "belief") if isinstance(belief_row, dict) else "belief"
            self.think_counters[KIND_TO_COUNTER.get(kind, "beliefs")] += 1
            if kind == "clash":
                clash_lines = belief_row.get("clashes") if isinstance(belief_row, dict) else None
                self._maybe_ask_clash(f"clash:{b['word']}:{clash_lines}", str(b["word"]))
            return {"outcome": "belief", "parked": False, "belief": belief_row}

        if "file_predict" in plan:
            fp = plan["file_predict"]
            filed = predict_file(claim=str(fp["claim"]), route=str(fp["route"]), decider=str(fp["decider"]), due=str(fp["due"]))
            if not filed["accepted"]:
                return {"outcome": "refused", "parked": False, "refused": filed.get("refused")}
            self._filed_predictions.append({"row": filed, "target_word": fp["target_word"], "due_canvas": int(fp["due_canvas"])})
            self.think_counters["predictions_filed"] += 1
            return {"outcome": "filed", "parked": False, "route_word": fp["target_word"]}

        if "file_rule" in plan:
            fr = plan["file_rule"]
            op, want, row_pred = str(fr["op"]), str(fr["want"]), fr["row"]
            key = want.split(":", 1)[1] if ":" in want else want
            (self._induce_pending if op == "induce" else self._deduce_pending).add(key)
            self._file_rule(row_pred, want=want, op=op, due_canvas=launched_at)
            if not row_pred.get("accepted"):
                return {"outcome": "refused", "parked": False, "refused": row_pred.get("refused")}
            return {"outcome": "filed", "parked": False, "want": want}

        if "file_frame" in plan:
            ff = plan["file_frame"]
            w1, w2, key = str(ff["w1"]), str(ff["w2"]), str(ff["key"])
            filed = predict_file(claim=f'"{w1} {w2}"', route="frame",
                                  decider="the eye answers BOTH words on the next instant that carries w1",
                                  due=f"the next instant with {w1!r}")
            predict_ledger_path = self.run_root / "state" / "predictions.jsonl"
            predict_ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with predict_ledger_path.open("a") as f:
                f.write(json.dumps(filed, default=str) + "\n")
            self.think_counters["predictions_filed"] += 1
            if not filed.get("accepted"):
                return {"outcome": "refused", "parked": False, "refused": filed.get("refused")}
            self._frame_pending.add(key)
            self._frames[key] = {"w1": w1, "w2": w2, "episodes": list(ff["episodes_cited"])}
            self._filed_predictions.append({
                "row": filed, "target_word": w1, "due_canvas": launched_at,
                "frame_w2": w2, "frame_key": key,
            })
            self.think_counters["frames_filed"] += 1
            return {"outcome": "filed", "parked": False, "frame": key}

        return {"outcome": "unknown_plan", "parked": False}

    def think_ms_median(self) -> Optional[float]:
        """PREREG §19.2 L-5's mark: "think_ms ... on STATUS as a series-friendly last value and a running
        median" — `think_ms_last` is the last value; this is the median over the last (at most 500) real
        think computations (`_think_ms_history`, capped in `_think_apply_pending`). `statistics` is not on
        the determinism law's forbidden list (time/datetime/random/os.urandom) — no clock read, arithmetic
        only, over numbers creature/think_thread.py already measured. None (not 0.0 — never a fabricated
        reading, #175) when no threaded think has completed yet, including on every non-threaded genome."""
        return statistics.median(self._think_ms_history) if self._think_ms_history else None

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
            # edit: Claude (Fable 5.1), 2026-09-22 20:08 +0400 — the C×D SEAM (tests/creature/test_life_seams.py; plan L-8/L-11): a SAY is one of the
            # creature's ACTS — counted in D's census (`acts_chosen`) and recorded as an OUTCOME episode in K's reflex ring (the mouth
            # EXPECTS to be heard: expected 1.0, got 1.0/0.0 by its own recall, the residual is the act's surprise). RED on the merged
            # bytes before this (acts_chosen had no "say"; the ring held no say episode).
            self.acts_chosen["say"] = self.acts_chosen.get("say", 0) + 1
            self._record_reflex("say", got=1.0 if heard else 0.0, expected_in=1.0, residual_in=None, source="mouth")
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
        # edit: Claude (Opus 5.5, the seat), 2026-09-29 23:54 +0400 — a snapshot is a GENERATION (his 23:20 word; the pre-flight's torn snapshot): every file
        # is written under a staged name FIRST, the complete generation already on disk is kept as hard links in state/prev/, then the
        # staged files are renamed back to back and SNAPSHOT.json {t, last_seq, files} LAST. A resume heals a torn one (_heal_torn_snapshot).
        staged: List[Tuple[Path, Path]] = []
        tmp_base = state_dir / "organism_tmp"
        self.org.save(tmp_base)
        staged += [(Path(str(tmp_base) + ".npz"), state_dir / "organism.npz"), (Path(str(tmp_base) + ".json"), state_dir / "organism.json")]

        ledgers = self.ledgers()
        predictor_last_winner = None
        if self.predictor is not None and self.predictor._last_winner is not None:
            predictor_last_winner = self.predictor._last_winner.tolist()      # A9: PREDICT's state (its last winner) lives in the mind and is saved in the snapshot (PREREG §11.1 step 1)
        ledger = {
            "last_seq": self.last_seq,
            "moment_word": {str(k): v for k, v in self.moment_word.items()},
            "moments": self.org.t,
            # edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — ALPHA4-2-PREREG.md §2 M4: the mind's OWN canvas count — a LEDGER key, never an
            # organism key (which would move every digest: G's lesson, ALPHA4-PREREG §5 GROW). creature/exam.py:canvas_count_of reads
            # it (the exam and SIT cadences); `moments // fixations` over-counted (5 moments a canvas + 200 a sleep → ≈ 400 real canvases
            # per «500»). Restored by resume() below so a live restart continues the count the sitter's LAST.json cursor was set from.
            "canvas_index": self._canvas_index,
            "ear_pending": dict(self.pending),
            # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-11 task 2: the SAME kind
            # of in-flight state as ear_pending above, same reason (a resume never loses an ear row
            # consumed just before a crash).
            "ear_pending_words": {k: list(v) for k, v in self.pending_words.items()},
            # A42-B2 (edit: Claude (Fable 5.1), 2026-09-23 17:05 +0400): the picture-words LEDGER (see __init__) — a ledger key,
            # never hashed; first-heard order kept.
            "picture_words": list(self.picture_words),
            "birth_source": {str(k): v for k, v in self.birth_source.items()},
            "sight": {str(k): sorted(v) for k, v in ledgers["sight"].items()},
            "words": {str(k): sorted(v) for k, v in ledgers["words"].items()},
            "predictor_last_winner": predictor_last_winner,
            # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:52 +0400 — LIFE-D-ACT-SOUND.md item 2
            # (L-8): "_act_rng, resume-safe: its state in the snapshot". `Generator.bit_generator.state`
            # is a plain JSON-safe dict (PCG64: {"state": {"state": int, "inc": int}, "has_uint32": int,
            # "uinteger": int}) -- persisted whole, restored whole in resume() below.
            "act_rng_state": self._act_rng.bit_generator.state,
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # item 2 (L-12): `_hands_rng`'s state (the same resume-safety `_act_rng` already has, one line
            # up), `_hands_pending` (a run already in flight, its own ACT file already on disk — the pool
            # must stay closed to a second 'hands' item across a resume until the matching outcome row is
            # replayed) and `_hands_last_program` (the 10% re-run draw's own memory).
            "hands_rng_state": self._hands_rng.bit_generator.state,
            "hands_pending": self._hands_pending,
            "hands_last_program": self._hands_last_program,
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §3/§4:
            # THE STAGE and its judge's own running state — "a resume mid-life keeps the stage" (the
            # brief's own test); the grade/episode/sit-reading state is persisted too so a resume
            # does not lose the (d) grade tally or (a)'s window it has already earned.
            # edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:41 +0400 — §4 AMENDED: "stage_ready_streak" is gone
            # (the door opens on ONE reading) and (a)'s per-act "game_rewards" became the per-EPISODE "game_episodes"
            # ([episode, step, success] each, the last READY_A_WINDOW). Neither key is journaled or hashed.
            # edit: Claude (Sonnet 5, judge builder B4), 2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3: the sliding
            # "game_episodes" deque is gone; the disjoint-block state is four small fields instead (see __init__'s own
            # comment on _game_last_block/_game_block_n/_game_block_successes/_game_last_episode_step).
            "stage": self.stage,
            "grades_total": self._grades_total,
            "grades_right": self._grades_right,
            "novel_grades": list(self._novel_grades),
            "hold_active": self._hold_active,
            "game_last_episode_step": list(self._game_last_episode_step) if self._game_last_episode_step else None,
            "game_block_n": self._game_block_n,
            "game_block_successes": self._game_block_successes,
            "game_last_block": self._game_last_block,
            "sit_readings": [list(t) for t in self._sit_readings],
            "web_fetches": self.web_fetches,
            "web_refused_rate": self.web_refused_rate,
            "web_refused_hold": self.web_refused_hold,
        }
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:40 +0400 — A4L-LANG task 10: the chat counters survive a restart
        # (STATUS reads them) — written ONLY under CHAT, so a genome without the gene writes the ledger it always wrote.
        if "CHAT" in self.genome.declared:
            ledger["chat_counters"] = dict(self.chat_counters)
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:34 +0400 — A4L-VOICE: the SOUND ledger (a sound birth is
        # filed as sound, genome/questions.build_ledgers) and the in-flight maker sounds (the same durability `ear_pending` has,
        # #230) — written ONLY when the organism has a sound area, so a genome without it writes exactly the ledger it always did.
        if self.org.sound is not None:
            ledger["sound"] = {str(k): sorted(v) for k, v in ledgers.get("sound", {}).items()}
            ledger["sound_pending"] = {k: {"trait": [float(x) for x in v["trait"]], "seq": int(v["seq"])}
                                       for k, v in self.pending_sound.items()}
            ledger["voice_rows"] = self.voice_rows
            ledger["voice_bound"] = self.voice_bound
        # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:36 +0400 — BRAIN-IN-BODY (INTERFACE §4): the held asks (the same durability
        # ear_pending has) and the ask/brain counts — written ONLY when BRAIN is declared or an ask was ever seen, so every other genome
        # writes exactly the ledger it always did. The brain's own state is written below, beside the organism's.
        if "BRAIN" in self.genome.declared or self.pending_asks or self.asks_answered:
            ledger["asks"] = {"pending": {k: list(v) for k, v in self.pending_asks.items()}, "answered": self.asks_answered,
                              "by": dict(self.asks_by), "learned": self.brain_learned, "refused": self.brain_refused}
            if self._drive is not None:        # PREREG-BRAIN-DRIVES: written only under the gene (every other ledger is what it was)
                ledger["asks"]["turns"] = dict(self.brain_turns)
        if self._inner is not None:            # PREREG-INNER-1 §2 (A5/A7): the chain state rides in the ledger, a generation file; absent the
            ledger["inner"] = {"state": {"n": int(self.inner_state["n"]), "pos": int(self.inner_state["pos"]),       # line, no key
                                         "last": [str(x) for x in self.inner_state["last"]],
                                         "said": [str(x) for x in self.inner_state["said"]]},
                               "counts": {"turns": int(self.inner_counts["turns"]), "said": int(self.inner_counts["said"]),
                                          "skipped": dict(self.inner_counts["skipped"])}}
        if self.brain is not None:
            brain_tmp = state_dir / "brain_tmp"
            self.brain.save(brain_tmp)
            staged += [(Path(str(brain_tmp) + ".npz"), state_dir / "brain.npz"), (Path(str(brain_tmp) + ".json"), state_dir / "brain.json")]
        if self.webs is not None or self.self_node is not None:     # the KNOWLEDGE WEB and the SELF (his 23:20 word)
            try:
                web_state = {"version": 1, "webs": {k: w.to_dict() for k, w in (self.webs or {}).items()},
                             "self": (self.self_node.to_dict() if self.self_node is not None else None)}
                web_tmp = state_dir / "web_tmp.json"
                web_tmp.write_text(json.dumps(web_state, sort_keys=True, separators=(",", ":")))
                staged.append((web_tmp, state_dir / "web.json"))
            except Exception as e:
                self._web_fail(e)
        # A9 / G5-K / L-13 / LIFE-F: the episode rings (Episodes.save is atomic onto the path it is given: here, a STAGED path)
        for ring, name in ((self.episodes, "episodes.npz"), (self.outcome_episodes, "outcome_episodes.npz"),
                           (self.sound_episodes, "sound_episodes.npz"), (self.touch_episodes, "touch_episodes.npz"),
                           (self.smell_episodes, "smell_episodes.npz")):
            if ring is not None:
                sp = state_dir / (name + ".staged")
                ring.save(sp)
                staged.append((sp, state_dir / name))
        ledger_tmp = state_dir / "ledger_tmp.json"
        ledger_tmp.write_text(json.dumps(ledger))
        staged.append((ledger_tmp, state_dir / "ledger.json"))
        gen_tmp = state_dir / "SNAPSHOT_tmp.json"
        gen_tmp.write_text(json.dumps({"t": int(self.org.t), "last_seq": int(self.last_seq or 0),
                                       # edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:53 +0400 — POLLER-FIX (docs/organism/days/PREREG-POLLER-FIX.md §2, option A): the very integer the ledger above carries (the same variable, nothing runs between), in the file renamed LAST and atomically, so the two 5-second pollers (creature/exam.py canvas_count_now) read ~40 bytes instead of parsing the whole ledger
                                       "canvas_index": ledger["canvas_index"],
                                       "files": [f.name for _s, f in staged],
                                       "prints": {f.name: _fingerprint(s) for s, f in staged}}, sort_keys=True))
        self._keep_prev_generation(state_dir)
        for i, (s, f) in enumerate(staged):
            if self._crash_after_renames is not None and i >= self._crash_after_renames:
                raise SnapshotCrash(f"the test hook: stopped after {i} renames")
            os.replace(str(s), str(f))
        os.replace(str(gen_tmp), str(state_dir / "SNAPSHOT.json"))

        self._last_snapshot_moments = self.org.t
        self.snapshot_count += 1

    def _keep_prev_generation(self, state_dir: Path) -> None:
        """Hard-link the COMPLETE generation now on disk into state/prev/ (a torn one is never kept)."""
        gen = state_dir / "SNAPSHOT.json"
        if not gen.exists() or _generation_t(state_dir) is None:
            return
        tmpd, prev = state_dir / "prev_tmp", state_dir / "prev"
        shutil.rmtree(tmpd, ignore_errors=True)
        tmpd.mkdir()
        for n in json.loads(gen.read_text())["files"] + ["SNAPSHOT.json"]:
            if (state_dir / n).exists():
                os.link(str(state_dir / n), str(tmpd / n))
        shutil.rmtree(prev, ignore_errors=True)
        os.replace(str(tmpd), str(prev))

    def close(self) -> None:
        # edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5: a tape can end (or a life
        # can stop) with a think still in flight — its result would otherwise be silently lost (never
        # applied, never journaled). Applied here, against the LAST eye row's own at/seq (self._cur_at/
        # _cur_seq, set by every _consume_eye call) — the brief does not specify a tail rule for this edge;
        # raised in the report as the chosen behaviour, not left undefined. The executor is shut down
        # (wait=True: the one in-flight future, if any, already finished by the apply call above) so a
        # short-lived Mind (a replay, a test) leaves no daemon thread behind it.
        if self._think_pending is not None and self._cur_at is not None:
            self._think_apply_pending({"at": self._cur_at, "seq": self._cur_seq})
        if self._think_executor is not None:
            self._think_executor.shutdown(wait=True)
        self.write_census()                     # PREREG-METADATA-1 §2: the census at close
        self.snapshot()

    @classmethod
    def resume(cls, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset(), eye_front=None,
               muse: bool = False, content_web: bool = False) -> Tuple["Mind", int]:
        """Load the latest snapshot (if any) and return (mind, last_seq). No snapshot -> a fresh mind, 0.

        ALPHA4-PREREG.md §6 (EVOLVE): epoch-aware (`_latest_evolved_genome`, above) — a root that carries one
        or more `GENOME.v<n>.genome` files is rebuilt from the HIGHEST one, never from the caller's own
        (birth) `genome_path`, so a process restart after an adoption does not silently revert to pre-
        adoption gene values; `evolve_epoch` is restored to that same n (never re-derived from a persisted
        counter — the files on disk ARE the count)."""
        heal = _heal_torn_snapshot(Path(run_root))       # his 23:20 word: a snapshot torn by a kill is healed BEFORE anything loads
        evolve_epoch, evolved_path = _latest_evolved_genome(Path(run_root))
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-09 04:36 +0400 — PREREG-ALPHA-6 §1.5/§2 B3: the
        # body's opt-in eye_front pass-through reaches a resume exactly as a birth (V2's declared parameter —
        # creature/replay.py:276-283's form; absent = byte-identical). The front's temporal state is the NEW
        # process's own: built fresh by the caller, one previous frame + the operating point, by construction.
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 07:00 +0400 — PREREG-CONTEMPLATE-1 §1: the muse
        # flag re-threads at resume exactly as at birth (the N1 precision= form; default False = byte-identical).
        # The chain STATE is in-memory and rebuilt fresh (the G5-E `_word_seen` precedent, named in the verdict
        # draft); the stores it reads (the beliefs file's statused rows, the question doors' files) are on disk.
        # edit: Kimi Code (K3, kimi-code, builder lane), 2026-10-10 14:21 +0400 — PREREG-CONTENT-WEB §1: the
        # content_web flag re-threads at resume exactly as at birth (the muse form's own precedent, one line
        # up); the census is in-memory instrument data, zeroed fresh (never snapshotted — nothing is persisted
        # beyond the web's own existing state, which resumes through state/web.json as it always did).
        mind = cls(evolved_path if evolved_path is not None else genome_path, run_root, blind=blind, eye_front=eye_front,
                   muse=muse, content_web=content_web)
        mind.snapshot_heal = heal
        mind.evolve_epoch = evolve_epoch
        state_dir = Path(run_root) / "state"
        npz, meta, ledger_path = state_dir / "organism.npz", state_dir / "organism.json", state_dir / "ledger.json"
        if npz.exists() and meta.exists() and ledger_path.exists():
            mind.org = Organism.load(state_dir / "organism", mind.genome)
            ledger = json.loads(ledger_path.read_text())
            mind.pending = dict(ledger.get("ear_pending", {}))
            mind.pending_words = {k: list(v) for k, v in ledger.get("ear_pending_words", {}).items()}
            # A42-B2 (edit: Claude (Fable 5.1), 2026-09-23 17:05 +0400): the picture-words LEDGER, restored as written; a snapshot
            # from before this key resumes EMPTY — never back-filled from the ring (RAISED in A42-B2-REPORT).
            mind.picture_words = [str(w) for w in ledger.get("picture_words", []) if w]
            mind._picture_words_set = set(mind.picture_words)
            mind.birth_source = {int(k): str(v) for k, v in (ledger.get("birth_source") or {}).items()}
            # A4L-VOICE (edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:34 +0400): in-flight maker sounds + counts
            mind.pending_sound = {k: {"trait": np.asarray(v["trait"], dtype=np.float64), "seq": int(v["seq"])}
                                  for k, v in (ledger.get("sound_pending") or {}).items()}
            mind.voice_rows = int(ledger.get("voice_rows", 0))
            mind.voice_bound = int(ledger.get("voice_bound", 0))
            mind.moment_word = {int(k): v for k, v in ledger.get("moment_word", {}).items()}
            mind._heard = {v for v in mind.moment_word.values() if v}     # PREREG §15: the heard-set, re-derived (never persisted separately)
            mind.last_seq = int(ledger.get("last_seq", 0))
            # edit: Claude (Fable 5.1, A42 builder B1), 2026-09-23 17:12 +0400 — M4: the canvas count continues across a restart (0 on an old ledger, the old
            # behaviour). The advisor's block: without this a restart under an exam/LAST.json cursor in the thousands would sit again
            # only after that many more canvases. Live resume only — a replay starts fresh; note: THINK's `_canvas_index % every`
            # boundary phase now also continues across a restart instead of restarting at 0 (docs/briefs/A42-B1-REPORT.md).
            mind._canvas_index = int(ledger.get("canvas_index", 0) or 0)
            mind._last_snapshot_moments = mind.org.t
            # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — ALPHA4-PREREG.md §3/§4:
            # THE STAGE — "a resume mid-life keeps the stage" (the brief's own test). Absent (a snapshot
            # from before this gene existed) -> recomputed from the JUST-LOADED org.t via `_moments_stage`
            # (never the pre-load org's t=0, which __init__ used to seed `mind.stage` a few lines above
            # this classmethod's own body starts) — the same fallback shape `_last_sleep_at` below uses.
            mind.stage = int(ledger["stage"]) if "stage" in ledger else mind._moments_stage()
            mind._grades_total = int(ledger.get("grades_total", 0))
            mind._grades_right = int(ledger.get("grades_right", 0))
            mind._novel_grades = collections.deque(ledger.get("novel_grades", []), maxlen=10)
            mind._hold_active = bool(ledger.get("hold_active", False))
            # edit: Claude (Opus 5.5, judge builder), 2026-09-23 11:41 +0400 — §4 AMENDED: (a)'s per-EPISODE window (absent
            # from a snapshot taken before the amendment -> empty: the old per-act "game_rewards" is in other units and is
            # never converted; the old "stage_ready_streak" is ignored, the door opens on one reading).
            # edit: Claude (Sonnet 5, judge builder B4), 2026-09-23 14:35 +0400 — ALPHA4-2-PREREG §4.3: the disjoint-block
            # state (absent from a snapshot taken before THIS amendment -> empty: an old "game_episodes" deque holds only
            # the last 20 completed episodes with no record of block boundaries, so it cannot be converted into a
            # disjoint block either — not merely skipped, genuinely impossible to reconstruct; moot for alpha4-2, a fresh
            # life, ALPHA4-2-PREREG §7.1).
            gles = ledger.get("game_last_episode_step")
            mind._game_last_episode_step = tuple(gles) if gles else None
            mind._game_block_n = int(ledger.get("game_block_n", 0))
            mind._game_block_successes = int(ledger.get("game_block_successes", 0))
            mind._game_last_block = ledger.get("game_last_block")
            mind._sit_readings = collections.deque([tuple(x) for x in ledger.get("sit_readings", [])], maxlen=2)
            mind.web_fetches = int(ledger.get("web_fetches", 0))
            mind.web_refused_rate = int(ledger.get("web_refused_rate", 0))
            mind.web_refused_hold = int(ledger.get("web_refused_hold", 0))
            # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:40 +0400 — A4L-LANG task 10: restored when present (CHAT only).
            for k_, v_ in (ledger.get("chat_counters") or {}).items():
                if k_ in mind.chat_counters:
                    mind.chat_counters[k_] = int(v_)
            # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:36 +0400 — BRAIN-IN-BODY: the held asks, the counts, and the brain's
            # state (state/brain.npz|json) beside the organism's. A snapshot without the brain's files (from before the gene) resumes a
            # NEWBORN brain and says so: `brain_restored` False on STATUS, never silent.
            asks_ = ledger.get("asks") or {}
            mind.pending_asks = {str(k): list(v) for k, v in (asks_.get("pending") or {}).items()}
            mind.asks_answered = int(asks_.get("answered", 0))
            mind.asks_by = {"brain": 0, "organs": 0, **{str(k): int(v) for k, v in (asks_.get("by") or {}).items()}}
            mind.brain_learned = int(asks_.get("learned", 0))
            mind.brain_refused = int(asks_.get("refused", 0))
            for k_, v_ in (asks_.get("turns") or {}).items():     # PREREG-BRAIN-DRIVES: restored when present (DRIVE only)
                if k_ in mind.brain_turns:
                    mind.brain_turns[k_] = int(v_)
            inner_ = ledger.get("inner")                            # PREREG-INNER-1 §2 (A7): the chain state, restored when present (INNER only)
            if inner_ and mind._inner is not None:
                s_ = inner_.get("state") or {}
                mind.inner_state = {"n": int(s_.get("n", 0)), "pos": int(s_.get("pos", 0)), "last": [str(x) for x in (s_.get("last") or [])],
                                    "said": [str(x) for x in (s_.get("said") or [])]}
                c_ = inner_.get("counts") or {}
                mind.inner_counts = {"turns": int(c_.get("turns", 0)), "said": int(c_.get("said", 0)),
                                     "skipped": {str(a): int(b) for a, b in (c_.get("skipped") or {}).items()}}
            if mind.brain is not None:
                if (state_dir / "brain.npz").exists() and (state_dir / "brain.json").exists():
                    mind.brain = _brain_class().load(state_dir / "brain", dict(mind.genome.declared["BRAIN"]),
                                                     mouth_incremental=mind._mouth_incremental)   # PREREG-ALPHA-6 §1.3: the clause re-declared at the resume
                    mind.brain_restored = True
                    mind._inherit_row_due = False      # PREREG-INHERIT §3: the inherit row is in the journal of the life that saved
                    mind.brain.author = Path(run_root).name   # PREREG-METADATA-1 §2
                    mind._restore_brain_world_count()  # PREREG-HEARS-2 §1: each other hand's count, from the brain's own worlds
                else:
                    mind.brain_restored = False
            if mind.webs is not None:          # the KNOWLEDGE WEB and the SELF (his 23:20 word): restored when saved; a bad file starts them fresh, said
                wp = state_dir / "web.json"
                if wp.exists():
                    try:
                        wst = json.loads(wp.read_text())
                        mind.webs = {k: _web.Web.from_dict(v) for k, v in wst["webs"].items()}
                        if wst.get("self"):
                            mind.self_node = _web.SelfNode.from_dict(wst["self"])
                        mind.web_restored = True
                    except Exception as e:
                        mind.web_error = f"restore failed, started fresh: {type(e).__name__}: {e}"
                        mind.web_restored = False
                else:
                    mind.web_restored = False
            # edit: Claude (Sonnet 5, LIFE builder D), 2026-09-22 18:52 +0400 — LIFE-D-ACT-SOUND.md item 2
            # (L-8): restore the act rng's stream exactly (absent from a snapshot taken before this gene
            # existed -> the freshly-seeded stream __init__ already built, unchanged).
            act_rng_state = ledger.get("act_rng_state")
            if act_rng_state is not None:
                mind._act_rng.bit_generator.state = act_rng_state
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # item 2 (L-12): the hands rng/pending/last-program state, restored the same way.
            hands_rng_state = ledger.get("hands_rng_state")
            if hands_rng_state is not None:
                mind._hands_rng.bit_generator.state = hands_rng_state
            mind._hands_pending = ledger.get("hands_pending")
            mind._hands_last_program = ledger.get("hands_last_program")

            # A9: `mind.predictor`/`mind.episodes` were built in __init__ against the PRE-load org/genome;
            # the predictor in particular closes over `org` by reference, so it must be rebuilt against
            # the LOADED org (a stale reference here would silently expect() off a dead, pre-resume
            # organism) -- caught by tracing the constructor, not by a test failure.
            if "PREDICT" in mind.genome.declared:
                # G5-E: _word_seen (arm "conjunctive") is NOT persisted (see genome/predict.py's module
                # docstring) — a resumed life restarts every word's count at 0. Out of scope for this
                # brief (replay-only); raised in G5-E-REPORT.md.
                mind.predictor = Predictor(mind.org, arm=mind.genome.declared["PREDICT"].get("arm", "novelty"),
                                           precision=mind.precision)   # N1: the flag re-threads at resume (PREREG-N1 §1)
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
            # LIFE builder D (L-13): the sound ring reloaded the same way; sound_events (a plain count,
            # like snapshots/sleeps elsewhere in this file) is NOT persisted -- a resumed life's count
            # restarts at 0, matching the existing gap this file already documents for think_counters etc.
            sound_path = state_dir / "sound_episodes.npz"
            if mind.sound_episodes is not None and sound_path.exists():
                mind.sound_episodes = Episodes.load(sound_path)
            # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:34 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md
            # items 3/4: the touch/smell rings reloaded the same way; touch_events/smell_events (plain
            # counts, matching sound_events' own gap) are NOT persisted.
            touch_path = state_dir / "touch_episodes.npz"
            if mind.touch_episodes is not None and touch_path.exists():
                mind.touch_episodes = Episodes.load(touch_path)
            smell_path = state_dir / "smell_episodes.npz"
            if mind.smell_episodes is not None and smell_path.exists():
                mind.smell_episodes = Episodes.load(smell_path)
            if "SLEEP" in mind.genome.declared:
                every = int(mind.genome.declared["SLEEP"]["every"])
                mind._last_sleep_at = (mind.org.t // every) * every if every > 0 else 0

            return mind, mind.last_seq
        return mind, 0
