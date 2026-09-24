"""harness_arms.py — KEY, SHIFTED-KEY and RING-READ: arms the HARNESS owns, answering from the truth
(B1-PREREG.md §5.5 (0c), §4 "RING-READ"; SEAT-DECISIONS R25, R26).

edit: Claude (Fable 5.1), 2026-09-24 18:31 +0400 — the seat, alone.

These are the only arms allowed to open `truth.jsonl` (§2.6: "Arms never open it" — the AST sweep of
`brain/arms/` and `brain/hybrids/` does not walk `brain/twins/`; this file is the declared exception, and it is
why these three live here and nowhere under `brain/arms/`). All three conform to `brain.protocol.Arm`:
`state_sha()` is a constant (nothing is learned from the tape except, for RING-READ, the TEACH order it
hears, which IS its state), `answer(learn=False)` never moves it.

KEY answers every ask with the truth's answer (REFUSE → UNKNOWN) — it must score 1.0 on every grader, or
the grader is INSTRUMENT-VOID. SHIFTED-KEY answers ask i with ask i+1's truth (the last with the first),
coerced to ask i's own `answer_kind` (a PICK index beyond the sheet → NOTHING) — it must NOT score 1.0.
RING-READ reads the operand's NAME from the truth (a perfect eye by construction) and answers AFTER /
BEFORE / BETWEEN by index arithmetic over the TEACH order it has heard — «reach given the name», printed
beside the REACH families; every other cue NOTHING.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

from brain.protocol import Answer, AnswerKind, canonical_json, is_row_operand
from brain.world.names import DIGIT_NAMES, digit_name, letter_name

REFUSE = "REFUSE"


def load_truth_asks(truth_path: Union[str, Path]) -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    with Path(truth_path).open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "ask":
                out[int(rec["seq"])] = rec
    return out


def load_truth_renderings(truth_path: Union[str, Path]) -> Dict[int, Dict[str, Any]]:
    out: Dict[int, Dict[str, Any]] = {}
    with Path(truth_path).open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "rendering":
                out[int(rec["cache_row"])] = rec
    return out


def answer_from_truth(ask_row: Mapping[str, Any], truth_answer: Any) -> Answer:
    """The truth's answer as an Answer of the ask's own kind (KEY's road, and SHIFTED-KEY's coercion)."""
    kind = ask_row["payload"]["answer_kind"]
    if truth_answer == REFUSE or truth_answer is None:
        return Answer(kind=AnswerKind.UNKNOWN, raw={"truth": truth_answer})
    if kind == "NAME":
        return Answer(kind=AnswerKind.NAME, value=str(truth_answer)) if isinstance(truth_answer, str) else Answer(kind=AnswerKind.NOTHING)
    if kind == "PICK":
        cands = ask_row["payload"].get("candidate_rows") or []
        if isinstance(truth_answer, int) and not isinstance(truth_answer, bool) and 0 <= truth_answer < len(cands):
            return Answer(kind=AnswerKind.PICK, value=int(truth_answer))
        return Answer(kind=AnswerKind.NOTHING, raw={"truth": truth_answer, "why": "not an index into this ask's sheet"})
    if kind == "YESNO":
        if truth_answer in ("YES", "NO"):
            return Answer(kind=AnswerKind.YES if truth_answer == "YES" else AnswerKind.NO)
        return Answer(kind=AnswerKind.NOTHING, raw={"truth": truth_answer})
    return Answer(kind=AnswerKind.NOTHING)


class _ConstantStateArm:
    """The shared plumbing: no learning, a constant state digest, a marker snapshot, cost counters."""
    STATE_LABEL = "constant"

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self._events = 0
        self._ms = 0.0

    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        self._events += 1

    def sleep(self, steps: int) -> None:
        self._events += 1

    def state_sha(self) -> str:
        return hashlib.sha256(f"{self.STATE_LABEL}:{self.seed}".encode()).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(canonical_json({"arm": self.STATE_LABEL, "seed": self.seed}))

    def load(self, path: Union[str, Path]) -> None:
        json.loads(Path(path).read_text())

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}


class KeyArm(_ConstantStateArm):
    """§5.5 (0c) KEY (shift 0) and SHIFTED-KEY (config {"shift": 1}). Needs config["truth_path"]."""
    STATE_LABEL = "key"

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        super().__init__(seed, config)
        self.shift = int(self.config.get("shift", 0))
        self.STATE_LABEL = "key" if self.shift == 0 else f"shifted-key:{self.shift}"
        self.asks = load_truth_asks(self.config["truth_path"])
        self._order = sorted(s for s in self.asks if s < 1_000_000)   # main-tape asks only (MLC seqs are offset)
        self._pos = {s: i for i, s in enumerate(self._order)}

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        self._events += 1
        seq = int(ask_row["seq"])
        if seq not in self.asks:
            return Answer(kind=AnswerKind.SILENT, raw={"why": "no truth record for this seq"})
        if self.shift == 0:
            return answer_from_truth(ask_row, self.asks[seq]["answer"])
        i = self._pos.get(seq)
        if i is None:
            return Answer(kind=AnswerKind.SILENT)
        other = self.asks[self._order[(i + self.shift) % len(self._order)]]
        return answer_from_truth(ask_row, other["answer"])


class RingReadArm(_ConstantStateArm):
    """R25: reach given the name. State = the TEACH order heard (first-seen names, per script family)."""
    STATE_LABEL = "ring-read"

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        super().__init__(seed, config)
        self.renderings = load_truth_renderings(self.config["truth_path"])
        self.order: Dict[str, List[str]] = {"letters": [], "digits": []}

    @staticmethod
    def _family_of_script(script: str) -> Optional[str]:
        if script in ("latin-upper", "latin-lower"):
            return "letters"
        if script == "digits":
            return "digits"
        return None

    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        self._events += 1
        if row["kind"] != "TEACH":
            return
        name = row["payload"]["name"]
        fam = "digits" if name in DIGIT_NAMES else ("letters" if len(name) == 1 else None)
        if fam and name not in self.order[fam]:
            self.order[fam].append(name)

    def state_sha(self) -> str:
        return hashlib.sha256(canonical_json(self.order).encode()).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(canonical_json(self.order))

    def load(self, path: Union[str, Path]) -> None:
        self.order = json.loads(Path(path).read_text())

    def _name_of(self, op: Mapping[str, Any]) -> Optional[tuple]:
        if not is_row_operand(op):
            return None
        rec = self.renderings.get(int(op["value"]))
        if rec is None:
            return None
        fam = self._family_of_script(rec["script"])
        if fam is None:
            return None
        nm = digit_name(rec["char"]) if fam == "digits" else letter_name(rec["char"])
        return fam, nm

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        self._events += 1
        p = ask_row["payload"]
        cues = p["cues"]
        if cues not in (["AFTER"], ["BEFORE"], ["BETWEEN"]) or p["answer_kind"] != "NAME":
            return Answer(kind=AnswerKind.NOTHING)
        names = [self._name_of(op) for op in p["operands"]]
        if any(n is None for n in names):
            return Answer(kind=AnswerKind.NOTHING, raw={"why": "an operand is not a taught-family glyph"})
        fam = names[0][0]
        order = self.order[fam]
        try:
            idx = [order.index(n[1]) for n in names]
        except ValueError:
            return Answer(kind=AnswerKind.NOTHING, raw={"why": "operand not yet heard"})
        if cues == ["AFTER"]:
            j = idx[0] + 1
        elif cues == ["BEFORE"]:
            j = idx[0] - 1
        else:
            if len(idx) != 2 or abs(idx[1] - idx[0]) != 2:
                return Answer(kind=AnswerKind.NOTHING, raw={"why": "no single name between these two"})
            j = (idx[0] + idx[1]) // 2
        if not (0 <= j < len(order)):
            return Answer(kind=AnswerKind.NOTHING, raw={"why": "off the end of the order"})
        return Answer(kind=AnswerKind.NAME, value=order[j])
