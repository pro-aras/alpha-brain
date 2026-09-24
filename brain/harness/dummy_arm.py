"""dummy_arm.py — THE HONEST REFERENCE ARM (B1-PREREG.md §9 row 1: "write it, test it with a dummy arm").

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 16:2x +0400 — a minimal, genuinely-conforming
implementation of `brain.protocol.Arm`. It carries no visual capability at all (it never opens the glance
cache) — every NAME ask it can answer at all comes from having HEARD the name on a TEACH row, and even
then it only ever returns UNKNOWN or the memorised name back for the exact glance_row it was taught on
(never generalising to an unseen rendering). It exists for two reasons:
  1. `check_arm`'s own self-test needs SOMETHING that conforms, to prove the checker accepts a conforming
     arm (a checker only ever exercised against arms that fail it is unfalsifiable the other way — #91's
     "a 0-finding audit needs a negative control", read for a checker's OWN positive control).
  2. Builders 1 and 3 can diff their own arm's plumbing (construction, fit_event/answer/sleep wiring,
     state_sha/snapshot/load) against a working example without reading the whole protocol docstring again.

Deliberately NOT built: any of A0-A6/D's actual learning machinery. `genome.machinery.Organism` (A0) and
the PyTorch arms (A1-A4) each get their own module under `brain/arms/`.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from brain.protocol import Answer, AnswerKind, VALENCE_NO, VALENCE_REWARD, canonical_json


class DummyArm:
    """Conforms to `brain.protocol.Arm`. State = the set of names it has heard, plus a {name: [glance_row,
    ...]} memory of exactly which rows it was taught that name on (so a POINT/IS ask about a MEMORISED row
    can be answered correctly — proving the plumbing round-trips a real answer — while anything else reads
    UNKNOWN/NOTHING, never a guess)."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self._heard: Dict[str, list] = {}   # name -> [glance_row, ...] taught
        self._events = 0
        self._ms = 0.0

    # ------------------------------------------------------------------ ingestion
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        if valence is not None and valence not in (VALENCE_REWARD, VALENCE_NO):
            raise ValueError(f"unknown valence {valence!r}")
        if row["kind"] == "TEACH":
            p = row["payload"]
            self._heard.setdefault(p["name"], [])
            if p["glance_row"] not in self._heard[p["name"]]:
                self._heard[p["name"]].append(p["glance_row"])
        # ARRIVAL, ASK (world-event ingestion) and FEEDBACK: the dummy has nothing further to learn from
        # them — it only ever remembers TEACH rows. This is a legitimate, if useless, implementation of the
        # protocol (an arm is never REQUIRED to learn from every row, only permitted to).
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        self._events += int(steps)
        self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------ answering
    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        p = ask_row["payload"]
        cues = p["cues"]
        try:
            if cues == ["NAME"]:
                row = p["operands"][0]["value"]
                for name, rows in self._heard.items():
                    if row in rows:
                        return Answer(kind=AnswerKind.NAME, value=name)
                return Answer(kind=AnswerKind.UNKNOWN)
            if cues == ["IS"] or cues == ["POINT"]:
                # naming cues the dummy has no candidate-scoring machinery for: abstain honestly.
                return Answer(kind=AnswerKind.UNKNOWN)
            # every relation cue (§2.6's RELATION_CUES): "no road" — the dummy has no relation machinery,
            # exactly like A0's own documented behaviour for a cue outside its road (§4's table).
            return Answer(kind=AnswerKind.NOTHING)
        finally:
            if learn:
                pass  # bookkeeping only; the dummy's real learning happens in fit_event (HarnessContract).
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------ identity / persistence
    def state_sha(self) -> str:
        payload = {"heard": {name: sorted(rows) for name, rows in self._heard.items()}}
        return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps({"seed": self.seed, "heard": self._heard}, sort_keys=True))

    def load(self, path: Union[str, Path]) -> None:
        d = json.loads(Path(path).read_text())
        self._heard = {k: list(v) for k, v in d["heard"].items()}

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}
