"""forced.py — the FORCED-ANSWER wrapper (B1-PREREG.md §4 "FORCED-ANSWER — each arm with UNKNOWN / NOTHING
disabled (its argmax always given)"; SEAT-DECISIONS R24): an arm that abstains carries its would-be answer in
`Answer.raw["forced"] = {"kind", "value"}`; this wrapper returns it in place of the abstention. An arm whose
abstentions carry no `forced` reads «no road» for the twin — counted by the wrapper and printed, never hidden.

edit: Claude (Fable 5.1), 2026-09-24 18:31 +0400 — the seat, alone.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Union
from pathlib import Path

from brain.protocol import Answer, AnswerKind

ABSTAIN = (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT)


class ForcedAnswer:
    def __init__(self, inner) -> None:
        self.inner = inner
        self.forced = 0
        self.no_road = 0

    def __getattr__(self, name: str):
        return getattr(self.inner, name)   # why / rule / cost / anything else the inner arm has

    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        self.inner.fit_event(row, valence)

    def sleep(self, steps: int) -> None:
        self.inner.sleep(steps)

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        a = self.inner.answer(ask_row, learn=learn)
        if a.kind not in ABSTAIN:
            return a
        f = (a.raw or {}).get("forced")
        if not isinstance(f, dict) or f.get("kind") not in AnswerKind.ALL or f.get("kind") in ABSTAIN:
            self.no_road += 1
            raw = dict(a.raw or {})
            raw["forced_no_road"] = True
            return Answer(kind=a.kind, value=a.value, raw=raw)
        self.forced += 1
        raw = dict(a.raw or {})
        raw["forced_from"] = a.kind
        try:
            return Answer(kind=f["kind"], value=f.get("value"), raw=raw)
        except Exception:   # a malformed forced value: the abstention stands, named
            self.no_road += 1
            raw["forced_no_road"] = True
            return Answer(kind=a.kind, value=a.value, raw=raw)

    def state_sha(self) -> str:
        return self.inner.state_sha()

    def snapshot(self, path: Union[str, Path]) -> None:
        self.inner.snapshot(path)

    def load(self, path: Union[str, Path]) -> None:
        self.inner.load(path)

    def cost(self) -> Dict[str, float]:
        return self.inner.cost()

    def counters(self) -> Dict[str, int]:
        return {"forced": self.forced, "no_road": self.no_road}
