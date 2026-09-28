"""router.py — THE ROUTERS A5 · A6 · E′ · F (B1-PREREG.md §4's last four rows; SEAT-DECISIONS R9).

edit: Claude (Fable 5.1), 2026-09-24 18:42 +0400 — the seat, alone.

One class, `Router`, driven by `config["parts"]` and `config["route"]`; four named constructors build the
PREREG's four hybrids from the SAME parts the single arms use (the identical classes and configs — a hybrid is
never a re-implementation of its parts). The router is itself an `Arm`:

  fit_event / sleep   → every part, in the declared order (both parts learn from every row — §4 A5).
  answer              → the route: NAME / POINT / IS → the CELLS (A0) unless A0 abstains (UNKNOWN / NOTHING /
                        SILENT), then the network (A5 / F) — or, for E′, A0 alone; every RELATION cue → the
                        network (A5), the partner (A6), the LIBRARY (E′), or — F — the library when D holds a
                        program that fits ALL of the cue's training examples (`LibraryArm.fits_all`, a compound:
                        all of its parts), else the network.
  why                 → A0's `why()` (U4a — the cells' episodes are the experience).
  rule                → D's `rule()` for E′ and F when D ANSWERED the family («no road» otherwise); A5 / A6: absent.
  state_sha           → sha256 over the parts' own digests in order (a hybrid's state is its parts' states).
  snapshot / load     → one sub-path per part under the given path.
  cost                → the sum of the parts' events and ms (each part's own beside it in `raw`).

D INSIDE E′ AND F DOES NOT SEARCH AGAIN (§4, R9): its part is a `LibraryArm` with `library_load_from` pointing
at D's OWN run directory (the runner's `<out>/D/arm`), so at every SLEEP it LOADS D's `sleep-<k>.json` by sha
instead of enumerating; a run of E′/F therefore needs D's run on the same seed first (the runner's
`config_from` machinery names the dependency). The seam test (R9): a run of F whose D snapshot is swapped for a
planted different one must change F's answers after that sleep — `tests/brain/harness/test_router.py`.

`Answer.raw` on every routed answer carries `{"routed_to": <part>, "fallback": bool}` so the record says WHICH
part answered (a hybrid's mark is read per part in the verdict — #170: a blend hides which half failed).
"""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from brain.protocol import Answer, AnswerKind, RELATION_CUES, has_rule, has_why, make_arm

ABSTAIN = (AnswerKind.UNKNOWN, AnswerKind.NOTHING, AnswerKind.SILENT)
NAMING = ("NAME", "POINT", "IS")

PART_CLASSES = {
    "A0": ("brain.arms.cells.a0", "A0Arm"),
    "A1": ("brain.arms.soft.arm", "ArmA1"),
    "A2": ("brain.arms.logic.arm", "ArmA2"),
    "A3": ("brain.arms.clauses.arm", "ArmA3"),
    "D": ("brain.arms.library.arm", "LibraryArm"),
}


class RouterError(Exception):
    pass


class Router:
    """config: {"parts": {"cells": "A0", "net": "A1", "lib": "D", "partner": "A2"|"A3"}, "route": "A5"|"A6"|"E'"|"F",
    "part_config": {<part role>: {...extra config for that part...}}} plus the reserved keys every arm gets."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self.route = str(self.config.get("route", "A5"))
        parts_decl: Dict[str, str] = dict(self.config.get("parts") or {})
        if "cells" not in parts_decl:
            raise RouterError("a router always has the cells (A0) — config['parts']['cells'] missing")
        self.parts: Dict[str, Any] = {}
        self.part_names: Dict[str, str] = {}
        base = {k: self.config[k] for k in ("cache_dir", "seed", "interpreter") if k in self.config}
        run_dir = Path(self.config["run_dir"]) if self.config.get("run_dir") else None
        part_cfg = dict(self.config.get("part_config") or {})
        for role, arm_name in parts_decl.items():
            if arm_name not in PART_CLASSES:
                raise RouterError(f"unknown part {arm_name!r} for role {role!r}")
            mod, cls = PART_CLASSES[arm_name]
            c = dict(base)
            if run_dir is not None:
                d = run_dir / role
                d.mkdir(parents=True, exist_ok=True)
                c["run_dir"] = str(d)
            c.update(part_cfg.get(role, {}))
            self.parts[role] = make_arm(getattr(importlib.import_module(mod), cls), self.seed, c)
            self.part_names[role] = arm_name
        self.order = list(parts_decl)   # fit/sleep order = declaration order (cells first)
        self._routed = {"cells": 0, "net": 0, "lib": 0, "partner": 0, "fallback": 0, "no_road": 0}

    # ------------------------------------------------------------------ the four hybrids
    @classmethod
    def A5(cls, seed: int, config: Mapping[str, Any]):
        c = dict(config); c.update({"route": "A5", "parts": {"cells": "A0", "net": "A1"}})
        c.setdefault("part_config", {}).setdefault("net", {}).setdefault("variant", "A1")
        return cls(seed, c)

    @classmethod
    def A6(cls, seed: int, config: Mapping[str, Any]):
        partner = str(config.get("partner", "A3"))
        if partner not in ("A2", "A3"):
            raise RouterError("A6's partner is A2 or A3 (chosen once on the pilot seed, §4)")
        c = dict(config); c.update({"route": "A6", "parts": {"cells": "A0", "partner": partner}})
        return cls(seed, c)

    @classmethod
    def E_prime(cls, seed: int, config: Mapping[str, Any]):
        c = dict(config); c.update({"route": "E'", "parts": {"cells": "A0", "lib": "D"}})
        return cls(seed, c)

    @classmethod
    def F(cls, seed: int, config: Mapping[str, Any]):
        c = dict(config); c.update({"route": "F", "parts": {"cells": "A0", "net": "A1", "lib": "D"}})
        c.setdefault("part_config", {}).setdefault("net", {}).setdefault("variant", "A1")
        return cls(seed, c)

    # ------------------------------------------------------------------ Arm protocol
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        for role in self.order:
            self.parts[role].fit_event(row, valence)

    def sleep(self, steps: int) -> None:
        for role in self.order:
            self.parts[role].sleep(steps)

    def _tag(self, ans: Answer, role: str, fallback: bool = False) -> Answer:
        raw = dict(ans.raw or {})
        raw["routed_to"] = role
        raw["fallback"] = fallback
        self._routed[role] += 1
        if fallback:
            self._routed["fallback"] += 1
        return Answer(kind=ans.kind, value=ans.value, raw=raw)

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        cues = list(ask_row["payload"]["cues"])
        naming = all(c in NAMING for c in cues)
        if naming:
            a = self.parts["cells"].answer(ask_row, learn=learn)
            second = "net" if "net" in self.parts else None
            if a.kind in ABSTAIN and second is not None and self.route in ("A5", "F"):
                b = self.parts[second].answer(ask_row, learn=learn)
                return self._tag(b, second, fallback=True)
            if second is not None and learn:
                self.parts[second].answer(ask_row, learn=True)   # the network still SEES the training ask (learn=True bookkeeping) — never its answer
            return self._tag(a, "cells")
        # a relation cue
        if self.route == "A5":
            return self._tag(self.parts["net"].answer(ask_row, learn=learn), "net")
        if self.route == "A6":
            return self._tag(self.parts["partner"].answer(ask_row, learn=learn), "partner")
        if self.route == "E'":
            return self._tag(self.parts["lib"].answer(ask_row, learn=learn), "lib")
        if self.route == "F":
            lib = self.parts["lib"]
            fits = False
            try:
                fits = bool(lib.fits_all(ask_row))
            except Exception:
                fits = False
            if fits:
                a = lib.answer(ask_row, learn=learn)
                if learn:
                    self.parts["net"].answer(ask_row, learn=True)
                return self._tag(a, "lib")
            if learn:
                lib.answer(ask_row, learn=True)
            return self._tag(self.parts["net"].answer(ask_row, learn=learn), "net")
        raise RouterError(f"unknown route {self.route!r}")

    def why(self, ask_row: Mapping[str, Any]) -> List[int]:
        cells = self.parts["cells"]
        return list(cells.why(ask_row)) if has_why(cells) else []

    def rule(self, cue: Sequence[str]) -> Dict[str, Any]:
        if self.route in ("E'", "F") and "lib" in self.parts and has_rule(self.parts["lib"]):
            return self.parts["lib"].rule(cue)
        return {"text": None, "executable": None, "no_road": True}

    def state_sha(self) -> str:
        h = hashlib.sha256()
        for role in self.order:
            h.update(f"{role}:{self.parts[role].state_sha()};".encode())
        return h.hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for role in self.order:
            self.parts[role].snapshot(path / role / "state")
        (path / "router.json").write_text(json.dumps({"route": self.route, "parts": self.part_names, "order": self.order, "routed": self._routed}, sort_keys=True))

    def load(self, path: Union[str, Path]) -> None:
        path = Path(path)
        for role in self.order:
            self.parts[role].load(path / role / "state")

    def cost(self) -> Dict[str, float]:
        ev, ms = 0, 0.0
        for role in self.order:
            c = self.parts[role].cost()
            ev += int(c["events"]); ms += float(c["ms"])
        return {"events": ev, "ms": ms}

    def size(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"routed": dict(self._routed)}
        for role in self.order:
            p = self.parts[role]
            if hasattr(p, "size") and callable(getattr(p, "size")):
                try:
                    out[role] = p.size()
                except Exception as e:  # pragma: no cover
                    out[role] = {"error": repr(e)}
        return out

    # the constructors the runner's registry names (a class per hybrid, so make_arm(cls, seed, config) is uniform)


class ArmA5(Router):
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        c = dict(config); c.update({"route": "A5", "parts": {"cells": "A0", "net": "A1"}})
        c.setdefault("part_config", {}).setdefault("net", {}).setdefault("variant", "A1")
        super().__init__(seed, c)


class ArmA6(Router):
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        partner = str(config.get("partner", "A3"))
        if partner not in ("A2", "A3"):
            raise RouterError("A6's partner is A2 or A3 (chosen once on the pilot seed, §4)")
        c = dict(config); c.update({"route": "A6", "parts": {"cells": "A0", "partner": partner}})
        super().__init__(seed, c)


class ArmEPrime(Router):
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        c = dict(config); c.update({"route": "E'", "parts": {"cells": "A0", "lib": "D"}})
        super().__init__(seed, c)


class ArmF(Router):
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        c = dict(config); c.update({"route": "F", "parts": {"cells": "A0", "net": "A1", "lib": "D"}})
        c.setdefault("part_config", {}).setdefault("net", {}).setdefault("variant", "A1")
        super().__init__(seed, c)
