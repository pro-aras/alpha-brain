# edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:0x +0400 — a NEGATIVE CONTROL for
# test_identity.py: an arm whose state_sha depends on an UNSEEDED random draw taken at construction, so two
# separate processes (which do not share Python's global random state) MUST disagree — proving
# identity_test's "twice" check actually detects nondeterminism rather than trivially passing everything.
from __future__ import annotations

import random
from typing import Any, Mapping

from brain.harness.dummy_arm import DummyArm
from brain.protocol import canonical_json
import hashlib


class NonDeterministicArm(DummyArm):
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        super().__init__(seed, config)
        self._unseeded_draw = random.random()   # deliberately IGNORES `seed` — the planted defect

    def state_sha(self) -> str:
        payload = {"heard": {name: sorted(rows) for name, rows in self._heard.items()},
                   "unseeded_draw": self._unseeded_draw}
        return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
