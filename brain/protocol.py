"""protocol.py — THE `Arm` PROTOCOL (B1-PREREG.md §4's table, frozen by Builder 2 before Builders 1 and 3
start — "the seam first, by the third hand", #235).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:2x +0400 — B1-PREREG.md §9's row 1: written, tested
against a dummy arm, and committed FIRST. FROZEN the moment this commit lands: a clause found wrong after
that is RAISED to the seat (docs/brain/B1-PREREG.md's own law, §0), never changed here unilaterally.

WHY A FROZEN FILE MATTERS (#235's lesson, applied before the fact rather than diagnosed after): the PREREG's
§4 table names seven required methods and two optional ones in one line each, but the SHAPES of their
arguments and return values are not in that line. Left to prose, three builders reading the same sentence
would each guess a shape, and the guesses would only be found to disagree at the merge — after real compute
has been spent building arms against them. Every shape below is therefore pinned HERE, once, in code a
`from brain.protocol import ...` line can import rather than re-derive:

  1. The tape row schema, per kind (§ "The tape row schema" below), with one worked EXAMPLE_ROWS entry per
     kind whose own `sha` is computed by this module's own `row_sha` — so a test can assert the shape
     parses, not merely that prose describes it (#171: a shape is learned from an untransformed read).
  2. The glance cache's reading interface lives in `brain/glance_cache.py` (shipped in the same commit as
     this file) — an ask/teach row carries a glance-cache ROW NUMBER (an int), never an array, so nothing
     but JSON needs to cross a §3.0 subprocess pipe if the cells ever have to run under a different
     interpreter than the venv.
  3. `valence`'s two literal values (`VALENCE_REWARD`, `VALENCE_NO`) — never a bare `+1`/`-1` or `True`/
     `False`, which would silently collide with a Python truthiness check somewhere downstream.
  4. `Answer.value`'s shape per `AnswerKind` (see the class docstring).
  5. `rule(cue)`'s `executable` signature — the SAME shape as `answer(ask_row, learn=False)`: a callable
     over an ask row, returning an `Answer`, so U4b can diff the rule's answer stream against the arm's own
     directly, item for item.
  6. The `learn=True` / `fit_event` division of labour across TEACH, training ASK, FEEDBACK, TEST ASK,
     ARRIVAL and SLEEP rows (see `HarnessContract` below) — spelled out once so no arm invents its own.
  7. `cost()`'s shape: cumulative `{"events": int, "ms": float}`.
  8. Everything above is a plain dict / dataclass with `to_dict`/`from_dict` — nothing that cannot cross a
     JSON pipe (or a `multiprocessing` boundary) if §3.0's fallback fires.

A conformance checker (`check_arm`) ships beside the protocol, with its own planted control (a dummy arm
that mutates state under `learn=False`, which `check_arm` must catch — #228's law: a test ships with a
control that must fail, not only one that must pass). `brain/harness/dummy_arm.py` (same commit) is the
honest reference implementation every builder can diff their own arm's plumbing against.

Seat traps read before this file was written (docs/brain/B1-PREREG.md §10; ~/.ai-context/SOLUTIONS.md):
#171 (learn a shape from an untransformed read — EXAMPLE_ROWS's sha is COMPUTED, never typed), #194 (a
claim is not the artefact — this docstring names the commit that must exist, not an adjective), #234 (a
mechanism mark prints its denominator — `check_arm` returns every violation, never a bare bool).
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

try:
    from typing import Protocol, runtime_checkable
except ImportError:  # pragma: no cover — 3.14.4 on both interpreters has typing.Protocol; kept defensive.
    from typing_extensions import Protocol, runtime_checkable  # type: ignore


class ProtocolError(Exception):
    """Raised by this module's own validators — never by an arm. An arm that cannot express a required
    answer kind returns Answer(kind=NOTHING) or Answer(kind=SILENT); it never raises to signal that."""


# ============================================================================================ THE CUE VOCABULARY (§2.6)
# The 14 cue marks, verbatim from B1-PREREG.md §2.6. A COMPOUND cue (today, only CHAIN) is represented as
# the LIST of its primitive marks in order — ["AFTER", "OTHER_CASE"] — never as a fifteenth string; nothing
# in this vocabulary changes to express a compound.
CUE_MARKS: tuple = (
    "NAME", "POINT", "IS",                                   # naming / pointing — never relation cues
    "SAME", "CONST", "CANARY",                                # positive controls (§5.5)
    "AFTER", "BEFORE", "BETWEEN", "TWO_AFTER",                # order relations
    "OTHER_CASE",                                             # the name bridges two shapes
    "MIRROR", "LOOP", "VOWEL",                                # perceptual categories
)
_NAMING_CUES = frozenset({"NAME", "POINT", "IS"})
# "Relation cues" (§2.6's own word, used by the routers of §4): every mark except NAME, POINT and IS.
RELATION_CUES: frozenset = frozenset(CUE_MARKS) - _NAMING_CUES

TAPE_KINDS: tuple = ("TEACH", "ASK", "FEEDBACK", "ARRIVAL", "SLEEP", "TEST_BEGIN", "TEST_END")
ANSWER_KIND_FAMILIES: tuple = ("NAME", "PICK", "YESNO")  # an ASK row's own `answer_kind` field

VALENCE_REWARD = "reward"
VALENCE_NO = "no"
VALENCES = (VALENCE_REWARD, VALENCE_NO)

# Config keys the harness always provides in `config` (arms may carry any other key beside these).
RESERVED_CONFIG_KEYS = ("cache_dir", "run_dir", "seed", "interpreter")


# ============================================================================================ CANONICAL JSON / TAPE HASHING (§2.6)
def canonical_json(obj: Any) -> str:
    """Sorted keys, no whitespace, ASCII-safe — the ONE serialisation every sha in this file is computed
    over, so two callers building "the same" payload always agree on its bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_sha(payload: Mapping[str, Any]) -> str:
    """sha256 of the payload's canonical JSON (§2.6: "sha = sha256 of the payload's canonical JSON")."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def make_row(seq: int, kind: str, phase: str, item: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Build one tape row `{seq, kind, phase, item, payload, sha}` with `sha` computed, never typed."""
    if kind not in TAPE_KINDS:
        raise ProtocolError(f"unknown tape kind {kind!r} (must be one of {TAPE_KINDS})")
    payload = dict(payload)
    return {"seq": int(seq), "kind": kind, "phase": str(phase), "item": str(item),
            "payload": payload, "sha": row_sha(payload)}


def verify_row(row: Mapping[str, Any]) -> bool:
    """True iff `row["sha"]` matches a fresh `row_sha` of `row["payload"]` — the planted-corruption test
    every reader of tape.jsonl runs before trusting a row (#191's class: a row that LOOKS parsed is not one
    that was verified)."""
    try:
        return row_sha(row["payload"]) == row["sha"]
    except (KeyError, TypeError):
        return False


# -------------------------------------------------------------------------------------------- operands (§2.6)
# "operands = glyph rows or, for POINT and IS only, a heard name" — encoded uniformly so every consumer
# (arms, the world, the graders) dispatches on `op["kind"]` rather than on the operand's Python type.
def op_row(cache_row: int) -> Dict[str, Any]:
    """An operand that is a glyph: `cache_row` indexes `brain.glance_cache.Cache` (a rendering)."""
    return {"kind": "row", "value": int(cache_row)}


def op_name(name: str) -> Dict[str, Any]:
    """An operand that is a HEARD NAME (POINT's "which of these is X", IS's "is this X" — §2.6: never any
    other cue's operand)."""
    return {"kind": "name", "value": str(name)}


def is_row_operand(op: Mapping[str, Any]) -> bool:
    return op.get("kind") == "row"


def is_name_operand(op: Mapping[str, Any]) -> bool:
    return op.get("kind") == "name"


# ============================================================================================ TAPE ROW SHAPES, PER KIND (§2.6)
# Each dict below is the PAYLOAD shape for one kind (the row's other four fields — seq, kind, phase, item —
# are the same across every kind, per `make_row` above). Nothing here is enforced beyond what
# `validate_tape_row` checks; the world builder (B1-PREREG.md §2) is free to add item-specific keys the
# graders read, but MAY NOT rename or drop the keys fixed here (every arm and every grader is written
# against exactly these names).
#
#   TEACH       {"glance_row": int, "name": str}
#               `glance_row` indexes the glance cache (brain/glance_cache.py); `name` is the ear-word
#               (§2.3: a lower-case letter a-z, a digit word "zero".."nine", or the plant's name "zog").
#
#   ASK         {"cues": [str, ...], "operands": [operand, ...], "candidate_rows": Optional[List[int]],
#                "answer_kind": "NAME" | "PICK" | "YESNO"}
#               `cues` is one mark, or CHAIN's two marks in order (§2.6); `operands` is a list of `op_row`/
#               `op_name` dicts (§2.6: POINT and IS carry a heard name, every other cue carries glyph rows —
#               one operand for a unary cue, two for AFTER/BEFORE/OTHER_CASE, three for BETWEEN);
#               `candidate_rows` is the PICK sheet (glance-cache rows), present iff `answer_kind == "PICK"`.
#
#   FEEDBACK    {"ask_seq": int, "right": Any}
#               `ask_seq` names the ASK row this follows; `right`'s shape mirrors that ASK's `answer_kind`
#               (NAME -> str; PICK -> int, an INDEX into that ask's own `candidate_rows`, never a cache row
#               id — the same convention as `Answer.value`, so a valence computation never has to
#               cross-reference two numbering schemes; YESNO -> "YES" | "NO"). FEEDBACK follows an ASK only
#               in TRAINING episodes, never after a TEST ask (§2.6).
#
#   ARRIVAL     {"what": str}                         e.g. "digits" (§2.7 Phase D).
#   SLEEP       {"steps": int}                        the harness calls `arm.sleep(steps)` for this row,
#                                                      never `fit_event` (see HarnessContract below).
#   TEST_BEGIN  {"sitting": str}                       e.g. "T_L", "T_D".
#   TEST_END    {"sitting": str}
def validate_tape_row(row: Mapping[str, Any]) -> None:
    """Raise ProtocolError on any shape violation; return None on a valid row. Does not check `sha` (use
    `verify_row` for that — the two checks are independent: a row can be well-shaped and still corrupted,
    or malformed and still hash-consistent with itself)."""
    for f in ("seq", "kind", "phase", "item", "payload", "sha"):
        if f not in row:
            raise ProtocolError(f"tape row missing field {f!r}: {row!r}")
    kind = row["kind"]
    if kind not in TAPE_KINDS:
        raise ProtocolError(f"unknown tape kind {kind!r}")
    p = row["payload"]
    if kind == "TEACH":
        _require_keys(p, {"glance_row", "name"}, kind)
        if not isinstance(p["glance_row"], int):
            raise ProtocolError(f"TEACH.glance_row must be int, got {type(p['glance_row'])!r}")
        if not isinstance(p["name"], str) or not p["name"]:
            raise ProtocolError("TEACH.name must be a non-empty str")
    elif kind == "ASK":
        _require_keys(p, {"cues", "operands", "candidate_rows", "answer_kind"}, kind)
        cues = p["cues"]
        if not isinstance(cues, list) or not cues or any(c not in CUE_MARKS for c in cues):
            raise ProtocolError(f"ASK.cues must be a non-empty list drawn from CUE_MARKS: {cues!r}")
        for op in p["operands"]:
            if not (is_row_operand(op) or is_name_operand(op)):
                raise ProtocolError(f"ASK operand has unknown kind: {op!r}")
        if p["answer_kind"] not in ANSWER_KIND_FAMILIES:
            raise ProtocolError(f"ASK.answer_kind must be one of {ANSWER_KIND_FAMILIES}: {p['answer_kind']!r}")
        if p["answer_kind"] == "PICK" and not p.get("candidate_rows"):
            raise ProtocolError("ASK.answer_kind == PICK requires a non-empty candidate_rows")
        # §2.6: "operands = glyph rows or, for POINT and IS only, a heard name" — every cue OTHER than
        # POINT/IS takes glyph-row operands only; POINT/IS must carry at least one heard-name operand.
        non_naming = set(cues) - {"POINT", "IS"}
        if non_naming:
            if any(is_name_operand(op) for op in p["operands"]):
                raise ProtocolError(f"cues {cues} take glyph-row operands only (§2.6); a heard-name operand is only for POINT/IS")
        else:
            if not any(is_name_operand(op) for op in p["operands"]):
                raise ProtocolError(f"cues {cues} (POINT/IS) require a heard-name operand (§2.6)")
    elif kind == "FEEDBACK":
        _require_keys(p, {"ask_seq", "right"}, kind)
        if not isinstance(p["ask_seq"], int):
            raise ProtocolError("FEEDBACK.ask_seq must be int")
    elif kind == "ARRIVAL":
        _require_keys(p, {"what"}, kind)
    elif kind == "SLEEP":
        _require_keys(p, {"steps"}, kind)
        if not isinstance(p["steps"], int) or p["steps"] < 0:
            raise ProtocolError("SLEEP.steps must be a non-negative int")
    elif kind in ("TEST_BEGIN", "TEST_END"):
        _require_keys(p, {"sitting"}, kind)


def _require_keys(payload: Mapping[str, Any], keys, kind: str) -> None:
    missing = keys - set(payload)
    if missing:
        raise ProtocolError(f"{kind} payload missing {sorted(missing)}: {payload!r}")


# -------------------------------------------------------------------------------------------- EXAMPLE_ROWS — one per kind, sha COMPUTED (#171)
def _example_rows() -> Dict[str, Dict[str, Any]]:
    rows = {
        "TEACH": make_row(1, "TEACH", "L1", "a", {"glance_row": 0, "name": "a"}),
        "ASK": make_row(2, "ASK", "L4", "a-after", {
            "cues": ["AFTER"], "operands": [op_row(0)], "candidate_rows": None, "answer_kind": "NAME"}),
        "FEEDBACK": make_row(3, "FEEDBACK", "L4", "a-after", {"ask_seq": 2, "right": "b"}),
        "ARRIVAL": make_row(4, "ARRIVAL", "D", "digits", {"what": "digits"}),
        "SLEEP": make_row(5, "SLEEP", "L1", "-", {"steps": 200}),
        "TEST_BEGIN": make_row(6, "TEST_BEGIN", "T_L", "-", {"sitting": "T_L"}),
        "TEST_END": make_row(7, "TEST_END", "T_L", "-", {"sitting": "T_L"}),
    }
    for kind, row in rows.items():
        validate_tape_row(row)
        assert verify_row(row), f"EXAMPLE_ROWS[{kind!r}] built with a stale sha — row_sha/make_row disagree"
    return rows


EXAMPLE_ROWS: Dict[str, Dict[str, Any]] = _example_rows()


# ============================================================================================ Answer (§4's table)
class AnswerKind:
    """The eight answer kinds (§4's table, §5.1's list), as plain string constants rather than an Enum —
    so `Answer.to_dict()` round-trips through JSON with no custom decoder anywhere downstream (the graders,
    the runner and every arm all compare `answer.kind == AnswerKind.NAME`, a plain string equality).

    `Answer.value`'s shape, per kind (pinned here so no two arms invent different conventions):
      NAME       -> str: the lower-case letter a-z, a digit word "zero".."nine", or an invented sign's name.
      PICK       -> int: the INDEX into the ask row's OWN `candidate_rows` list (0-based) — never a glance-
                    cache row id, so a grader never has to resolve which sitting's candidate sheet a raw
                    row number belonged to.
      YES        -> None (the kind alone carries the answer).
      NO         -> None.
      UNKNOWN    -> None ("I don't know").
      RESEMBLES  -> str: the name it resembles ("I don't know what it is, but it resembles X").
      NOTHING    -> None (a capability the arm does not have — "no road", §4's table).
      SILENT     -> None (the arm returned nothing at all — §5.1: "SILENT is never read as UNKNOWN").
    `raw` is the arm's own free-form dict (confidences, margins, whatever it wants to log) — never read by
    a grader for a pass/fail decision, only ever for a report's colour.
    """
    NAME = "NAME"
    PICK = "PICK"
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"
    RESEMBLES = "RESEMBLES"
    NOTHING = "NOTHING"
    SILENT = "SILENT"

    ALL = (NAME, PICK, YES, NO, UNKNOWN, RESEMBLES, NOTHING, SILENT)


@dataclass
class Answer:
    kind: str
    value: Optional[Union[str, int]] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in AnswerKind.ALL:
            raise ProtocolError(f"Answer.kind must be one of {AnswerKind.ALL}, got {self.kind!r}")
        if self.kind == AnswerKind.PICK and not isinstance(self.value, int):
            raise ProtocolError(f"Answer(kind=PICK).value must be int, got {type(self.value)!r}")
        if self.kind == AnswerKind.NAME and not isinstance(self.value, str):
            raise ProtocolError(f"Answer(kind=NAME).value must be str, got {type(self.value)!r}")
        if self.kind == AnswerKind.RESEMBLES and not isinstance(self.value, str):
            raise ProtocolError(f"Answer(kind=RESEMBLES).value must be str, got {type(self.value)!r}")

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "value": self.value, "raw": self.raw}

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "Answer":
        return cls(kind=d["kind"], value=d.get("value"), raw=dict(d.get("raw", {})))


def right_matches(answer_kind_family: str, given: Answer, right: Any) -> bool:
    """Did `given` (the arm's own answer to a training ASK) match the FEEDBACK's `right`? Used by the
    HarnessContract to compute `valence` — never by an arm itself (an arm never sees `right` directly; it
    only ever sees the `valence` this function's caller derives from it, per §2.6: "the valence ... is
    computed by the harness from that arm's answer"). UNKNOWN/NOTHING/SILENT never match (an abstention is
    never "right")."""
    if given.kind in (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT):
        return False
    if answer_kind_family == "NAME":
        return given.kind == AnswerKind.NAME and given.value == right
    if answer_kind_family == "PICK":
        return given.kind == AnswerKind.PICK and given.value == right
    if answer_kind_family == "YESNO":
        return given.kind in (AnswerKind.YES, AnswerKind.NO) and given.kind == right
    raise ProtocolError(f"unknown answer_kind family {answer_kind_family!r}")


# ============================================================================================ THE Arm PROTOCOL
@runtime_checkable
class Arm(Protocol):
    """The structural protocol every arm (and every twin, and every router's parts) implements. Construction
    is `ArmClass(seed, config)` — i.e. `init(seed, config)` in B1-PREREG.md §4's table names the
    CONSTRUCTOR's signature, not a separate method called after a no-arg `__init__` (pinned here so three
    builders build one convention, not three) — always go through `make_arm` below rather than calling a
    class directly, so there is exactly one construction path in the whole estate (#235's "a widened vector
    is a chain", read backwards: a single construction site is a chain nothing can silently diverge from).

    `config` always carries the RESERVED_CONFIG_KEYS (cache_dir, run_dir, seed, interpreter); an arm may
    read any other key it declares in its own docs. `run_dir` is the arm's own private scratch/log directory
    under the harness's run root — an arm never writes outside it.
    """

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None: ...

    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        """Ingest one non-test tape row IN ORDER (see HarnessContract for exactly which rows and when).
        `valence` is one of VALENCE_REWARD/VALENCE_NO, present only when `row["kind"] == "FEEDBACK"`."""
        ...

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        """Answer one ASK row. `learn=False` (every TEST-sitting ask, §5.1) MUST leave `state_sha()`
        unchanged — the harness asserts this after every such call; a violation makes the sitting
        INSTRUMENT-VOID (§5.1), not merely wrong. `learn=True` (a training ask, §2.7 L4-L6) MAY change
        state (see HarnessContract: the primary learning update still happens through the FEEDBACK's
        `fit_event`, so what `learn=True` is allowed to change here is bookkeeping/context state, not a
        finished weight update the FEEDBACK hasn't arrived to justify)."""
        ...

    def sleep(self, steps: int) -> None:
        """A SLEEP tape row — never routed through `fit_event` (see HarnessContract)."""
        ...

    def state_sha(self) -> str:
        """A hex digest over every array/scalar that constitutes this arm's LEARNED STATE — never its
        cumulative cost counters, never a cache of already-computed answers. Two arms with identical
        learned state return the identical digest; `answer(..., learn=False)` must not move it (§5.1's
        FROZEN control, 0e)."""
        ...

    def snapshot(self, path: Union[str, Path]) -> None:
        """Write this arm's full learned state to `path` (the arm chooses its own file shape under that
        path — a single file or a directory, its call)."""
        ...

    def load(self, path: Union[str, Path]) -> None:
        """Load a snapshot written by `snapshot` INTO this (already-constructed) instance, in place. A
        fresh instance loaded from a path a live instance wrote at some `state_sha()` must itself report
        that same `state_sha()` (the harness's own round-trip check, in `check_arm`)."""
        ...

    def cost(self) -> Dict[str, float]:
        """Cumulative `{"events": int, "ms": float}` since construction — the arm's own count of
        fit_event/answer/sleep calls and the wall-milliseconds it spent inside its own code computing them
        (a `time.perf_counter()` wrapper around the arm's own body is enough; the harness independently
        times each call from outside as a cross-check in run-facts.json, never hashed, never graded —
        #171's law: never trust one instrument alone)."""
        ...

    # ---- optional (§4's table: "absent -> 'no road'" / "absent -> U4a/U4b read 'no road'") ----
    # def why(self, ask_row: Mapping[str, Any]) -> List[int]: ...
    #     Tape SEQ numbers this arm's answer to `ask_row` was grounded in (U4a). Detected by `has_why`.
    # def rule(self, cue: Sequence[str]) -> Dict[str, Any]: ...
    #     {"text": str, "executable": Callable[[Mapping[str, Any]], Answer]} for the relation family named
    #     by `cue` (the SAME list shape an ASK row's own "cues" field carries, so a compound like CHAIN's
    #     ["AFTER", "OTHER_CASE"] is one call, not two). `executable` is called by the harness EXACTLY as
    #     `answer(ask_row, learn=False)` is — same input, same Answer return — so U4b can diff the rule's
    #     answers against the arm's own on the identical held-out items (U4b's own bar). Detected by
    #     `has_rule`.


def make_arm(cls, seed: int, config: Mapping[str, Any]):
    """THE single construction path for every arm, twin and router part (see Arm's docstring). Every
    caller — the runner, every test, every router — builds an arm through this function, never through
    `cls(seed, config)` directly, so a future change to construction (e.g. a §3.0 subprocess wrapper) has
    exactly one call site to change."""
    return cls(seed, dict(config))


def has_why(arm: object) -> bool:
    return hasattr(arm, "why") and callable(getattr(arm, "why"))


def has_rule(arm: object) -> bool:
    return hasattr(arm, "rule") and callable(getattr(arm, "rule"))


# ============================================================================================ HarnessContract
# The learn=True / fit_event division of labour (item 6 in this file's own docstring), pinned as CODE (a
# reference dispatcher) rather than left as a paragraph three builders would each re-derive slightly
# differently. `brain/harness/run.py` (B1-PREREG.md §8's runner) calls exactly this dispatcher, per row, in
# tape order, for every arm; nothing about it is arm-specific.
class HarnessContract:
    """Stateless: every method is a `@staticmethod` over (arm, row, ...). Holds no per-run state itself —
    the caller (the runner) tracks `pending_ask` (the last training ASK's own Answer, awaiting its
    FEEDBACK) and whether the tape position is inside a TEST_BEGIN/TEST_END window."""

    @staticmethod
    def teach(arm: Arm, row: Mapping[str, Any]) -> None:
        assert row["kind"] == "TEACH"
        arm.fit_event(row, valence=None)

    @staticmethod
    def arrival(arm: Arm, row: Mapping[str, Any]) -> None:
        assert row["kind"] == "ARRIVAL"
        arm.fit_event(row, valence=None)

    @staticmethod
    def sleep(arm: Arm, row: Mapping[str, Any]) -> None:
        assert row["kind"] == "SLEEP"
        arm.sleep(int(row["payload"]["steps"]))

    @staticmethod
    def training_ask(arm: Arm, row: Mapping[str, Any]) -> Answer:
        """A training ASK (outside any TEST_BEGIN/TEST_END window): answered with learn=True (never
        graded, §5.1), then ingested as a world-event via fit_event. Returns the Answer so the caller can
        hold it until the matching FEEDBACK row arrives."""
        assert row["kind"] == "ASK"
        ans = arm.answer(row, learn=True)
        arm.fit_event(row, valence=None)
        return ans

    @staticmethod
    def feedback(arm: Arm, row: Mapping[str, Any], pending_answer: Answer, answer_kind_family: str) -> str:
        """The FEEDBACK that follows a training ASK: compute this arm's OWN valence from its OWN prior
        answer (§2.6 — the tape stores only the shown `right`; every arm's valence is derived fresh, so the
        tape stays the same object for every arm) and hand it to fit_event. Returns the valence used (for
        the runner's own log)."""
        assert row["kind"] == "FEEDBACK"
        valence = VALENCE_REWARD if right_matches(answer_kind_family, pending_answer, row["payload"]["right"]) else VALENCE_NO
        arm.fit_event(row, valence=valence)
        return valence

    @staticmethod
    def test_ask(arm: Arm, row: Mapping[str, Any]) -> Answer:
        """A TEST-sitting ASK: answered with learn=False and FROZEN (§5.1) — never followed by fit_event
        (no FEEDBACK exists for a test ask). Raises ProtocolError if state_sha moved (0e's own control)."""
        assert row["kind"] == "ASK"
        before = arm.state_sha()
        ans = arm.answer(row, learn=False)
        after = arm.state_sha()
        if before != after:
            raise ProtocolError(
                f"INSTRUMENT-VOID (§5.1, control 0e): state_sha moved under learn=False "
                f"({before} -> {after}) answering ask seq={row.get('seq')}")
        return ans


# ============================================================================================ check_arm — the conformance checker (#228: ships with a control that must FAIL)
def check_arm(arm: Arm, sample_teach_row: Mapping[str, Any], sample_ask_row: Mapping[str, Any],
              tmp_dir: Union[str, Path], fresh_arm_factory: Optional[Callable[[], Arm]] = None) -> List[str]:
    """Run the protocol's conformance battery against an already-constructed, already-taught-a-little `arm`.
    Returns a list of violation strings — EMPTY means the arm conforms. Never raises for an ordinary
    conformance failure (a caller that wants a hard failure asserts `not violations`); it DOES let a genuine
    bug in the arm's own code (an uncaught exception) propagate, since that is not this checker's to
    interpret.

    `fresh_arm_factory`, if given, must return a NEW, freshly-constructed (untaught) instance of the SAME
    class/seed/config as `arm` — used for the snapshot/load round-trip. Omit it to skip that one check
    (useful for a quick smoke of an arm still under construction)."""
    violations: List[str] = []

    # (1) every returned Answer has a valid kind (Answer.__post_init__ already enforces the per-kind value
    # shape at construction time, so a bad kind or a bad value both surface here as an exception the
    # caller sees — this list only ever grows from checks THIS function evaluates itself).
    try:
        before = arm.state_sha()
    except Exception as e:  # pragma: no cover - defensive; a real arm must implement state_sha
        violations.append(f"state_sha() raised: {e!r}")
        return violations

    ans1 = arm.answer(sample_ask_row, learn=False)
    if not isinstance(ans1, Answer):
        violations.append(f"answer(...) returned {type(ans1)!r}, not an Answer")
    after1 = arm.state_sha()
    if after1 != before:
        violations.append(f"answer(learn=False) moved state_sha: {before} -> {after1} (§5.1 control 0e)")

    # (2) determinism under no learning: asking the SAME frozen item twice gives the SAME answer.
    ans2 = arm.answer(sample_ask_row, learn=False)
    after2 = arm.state_sha()
    if after2 != after1:
        violations.append(f"a SECOND answer(learn=False) moved state_sha: {after1} -> {after2}")
    if isinstance(ans1, Answer) and isinstance(ans2, Answer) and ans1.to_dict() != ans2.to_dict():
        violations.append(f"two answer(learn=False) calls on the same frozen item disagreed: {ans1} vs {ans2}")

    # (3) fit_event on a TEACH row does not raise (state MAY change; not asserted either way — an arm is
    # free to ignore a TEACH if its own design says so, though every real arm in B1 does not).
    try:
        arm.fit_event(sample_teach_row, valence=None)
    except Exception as e:
        violations.append(f"fit_event(TEACH) raised: {e!r}")

    # (4) cost() has the declared shape.
    try:
        c = arm.cost()
        if not isinstance(c, dict) or "events" not in c or "ms" not in c:
            violations.append(f"cost() must return {{'events':..., 'ms':...}}, got {c!r}")
        elif c["events"] < 0 or c["ms"] < 0:
            violations.append(f"cost() returned a negative counter: {c!r}")
    except Exception as e:
        violations.append(f"cost() raised: {e!r}")

    # (5) snapshot -> load round-trips to the SAME state_sha (skipped without a factory).
    if fresh_arm_factory is not None:
        tmp_dir = Path(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        snap_path = tmp_dir / "check_arm_snapshot"
        try:
            want = arm.state_sha()
            arm.snapshot(snap_path)
            fresh = fresh_arm_factory()
            fresh.load(snap_path)
            got = fresh.state_sha()
            if got != want:
                violations.append(f"snapshot->load round-trip changed state_sha: {want} -> {got}")
        except Exception as e:
            violations.append(f"snapshot/load round-trip raised: {e!r}")

    return violations
