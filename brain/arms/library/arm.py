"""arm.py — ARM D, THE RULE LIBRARY, as a `brain.protocol.Arm` (B1-PREREG.md §4 row D; §9 row «Builder 1»).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — the frozen protocol (ac7d2ff) wrapped around
`core.LibraryCore`: rows in, Answers out; nothing here decides anything the core does not.

Construction: `make_arm(LibraryArm, seed, config)` (the protocol's one construction path). `config` keys read
beside the protocol's reserved ones (`cache_dir`, `run_dir`, `seed`, `interpreter`):
  candidates_per_sleep  int   the SEARCH budget of one sleep, in candidate programs — the seat's number from
                              B1-PREREG §4's formula after §3.5's probe (default 2,000: toys and tests only)
  max_size              int   the largest program the enumerator reaches (default 20 symbols)
  fit_floor             str   "majority" (default; report §4 R1) or "all"
  top_k                 int   abstractions added per sleep at most (default 3)
  library_log           bool  append each sleep's record to run_dir/library_log.jsonl (default True)
  library_snapshots     bool  write run_dir/library/sleep-<k>.json at the end of sleep k (default True)
  library_load_from     str   a directory of such snapshots: sleep k LOADS sleep-<k>.json (its sha checked
                              against that directory's library_log.jsonl when present) instead of searching —
                              the E′/F road (report §4 R9; the router and the path are the seat's to settle)

The learned state is a pure function of the tape: the valence argument is ignored (D reads the SHOWN right
answer on the FEEDBACK row, never its own valence), `answer()` never changes state, no clock enters a decision.
`cost()`'s milliseconds are a measurement kept outside the state.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

import numpy as np

from brain.glance_cache import Cache
from brain.protocol import (Answer, AnswerKind, ProtocolError, VALENCE_NO, VALENCE_REWARD, canonical_json,
                            is_name_operand, is_row_operand, verify_row)

from . import dsl
from .core import LibraryCore, quantize_pool


def _all_quantized(cache: Cache) -> np.ndarray:
    rows = len(cache)
    if rows == 0:
        return np.zeros((0, 144), dtype=np.int64)
    glances = np.stack([cache.glances(i) for i in range(rows)], axis=0)
    return quantize_pool(glances)


class LibraryArm:
    """Arm D. See the module docstring for its config and the report (docs/briefs/B1-BUILDER1-REPORT.md) for
    its DSL, search, compressor and the clauses raised to the seat."""

    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self._events = 0
        self._ms = 0.0
        self._cache: Optional[Cache] = None
        self._Q: Optional[np.ndarray] = None
        self.core = LibraryCore(self._q_lazy, self._core_config())
        self.run_dir = Path(self.config["run_dir"]) if self.config.get("run_dir") else None

    def _core_config(self) -> Dict[str, Any]:
        keys = ("candidates_per_sleep", "max_size", "fit_floor", "top_k")
        return {k: self.config[k] for k in keys if k in self.config}

    # the percepts are read from the cache on first need (a fresh instance that only loads a snapshot and
    # hashes it never opens the cache)
    def _q_lazy(self) -> np.ndarray:
        if self._Q is None:
            self._cache = Cache(self.config["cache_dir"])
            self._Q = _all_quantized(self._cache)
        return self._Q

    # ------------------------------------------------------------------------------------------ ingestion
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        try:
            if valence is not None and valence not in (VALENCE_REWARD, VALENCE_NO):
                raise ProtocolError(f"unknown valence {valence!r}")
            if not verify_row(row):
                raise ProtocolError(f"row seq={row.get('seq')} fails its own sha (arm D refuses a row it cannot verify)")
            kind = row["kind"]
            p = row["payload"]
            seq = int(row["seq"])
            if kind == "TEACH":
                self.core.record_teach(seq, int(p["glance_row"]), str(p["name"]))
            elif kind == "ASK":
                self.core.record_ask(seq, list(p["cues"]), self._operands(p["operands"]),
                                     p.get("candidate_rows"), str(p["answer_kind"]))
            elif kind == "FEEDBACK":
                self.core.record_feedback(seq, int(p["ask_seq"]), p["right"])
            # ARRIVAL and anything else: nothing to record (D's data memory is TEACH rows; its examples are
            # ASK + FEEDBACK pairs)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    @staticmethod
    def _operands(ops: Sequence[Mapping[str, Any]]) -> List[tuple]:
        out = []
        for op in ops:
            if is_row_operand(op):
                out.append(("G", int(op["value"])))
            elif is_name_operand(op):
                out.append(("N", str(op["value"])))
            else:
                raise ProtocolError(f"unknown operand {op!r}")
        return out

    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        try:
            src = self.config.get("library_load_from")
            if src:
                self._load_sleep(Path(src), self.core.sleep_index + 1)
                return
            log = self.core.sleep()
            self._after_sleep(log)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def _after_sleep(self, log: Dict[str, Any]) -> None:
        if self.run_dir is None:
            return
        snap_sha = None
        if self.config.get("library_snapshots", True):
            d = self.run_dir / "library"
            d.mkdir(parents=True, exist_ok=True)
            path = d / f"sleep-{self.core.sleep_index}.json"
            text = canonical_json(self.core.state())
            path.write_text(text)
            snap_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if self.config.get("library_log", True):
            self.run_dir.mkdir(parents=True, exist_ok=True)
            rec = dict(log)
            rec["state_sha"] = self.core.state_sha()
            rec["snapshot_sha"] = snap_sha
            with (self.run_dir / "library_log.jsonl").open("a", encoding="utf-8") as f:
                f.write(canonical_json(rec) + "\n")

    def _load_sleep(self, src: Path, k: int) -> None:
        path = src / "library" / f"sleep-{k}.json"
        if not path.exists():
            path = src / f"sleep-{k}.json"
        text = path.read_text()
        logp = (src / "library_log.jsonl") if (src / "library_log.jsonl").exists() else (src.parent / "library_log.jsonl")
        if logp.exists():
            want = None
            for line in logp.read_text().splitlines():
                rec = json.loads(line)
                if int(rec.get("sleep", -1)) == k:
                    want = rec.get("snapshot_sha")
            got = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if want is not None and want != got:
                raise ProtocolError(f"snapshot sleep-{k}.json sha {got} != the library log's {want}")
        st = json.loads(text)
        # the loaded state replaces the learned state whole; the awake rows since that sleep are the same tape
        self.core.load_state(st)

    # ------------------------------------------------------------------------------------------ answering
    def _resolve(self, p: Mapping[str, Any]):
        ops = self._operands(p["operands"])
        cands = p.get("candidate_rows")
        return (self.core.resolve(list(p["cues"]), [o[0] for o in ops], cands is not None, str(p["answer_kind"])),
                ops, cands)

    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            return self._answer_with(self.core, ask_row)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    @staticmethod
    def _answer_with(core: LibraryCore, ask_row: Mapping[str, Any]) -> Answer:
        p = ask_row["payload"]
        ops = LibraryArm._operands(p["operands"])
        cands = p.get("candidate_rows")
        kind = str(p["answer_kind"])
        tree, keys = core.resolve(list(p["cues"]), [o[0] for o in ops], cands is not None, kind)
        if tree is None:
            return Answer(kind=AnswerKind.NOTHING, raw={"road": "none", "reason": keys})
        # heard names are mapped to ids WITHOUT interning (answering never changes state): an unknown name gets
        # a temporary id past the known ones
        temp: Dict[str, int] = {}
        ids = []
        for t, v in ops:
            if t == "G":
                ids.append(("G", int(v)))
            else:
                nid = core.name_id.get(v)
                if nid is None:
                    nid = temp.setdefault(v, len(core.names) + len(temp))
                ids.append(("N", nid))
        val, _batch = core.evaluate_one(tree, ids, cands)
        ok = bool(np.asarray(val.ok).reshape(-1)[0])
        raw = {"program": dsl.render(tree), "keys": list(keys)}
        if not ok:
            raw["reason"] = "the program raised"
            return Answer(kind=AnswerKind.NOTHING, raw=raw)
        v = np.asarray(val.v).reshape(-1)[0]
        if kind == "NAME":
            v = int(v)
            if v < len(core.names):
                return Answer(kind=AnswerKind.NAME, value=core.names[v], raw=raw)
            back = {i: n for n, i in temp.items()}
            if v in back:
                return Answer(kind=AnswerKind.NAME, value=back[v], raw=raw)
            raw["reason"] = "a name id with no name"
            return Answer(kind=AnswerKind.NOTHING, raw=raw)
        if kind == "PICK":
            v = int(v)
            sheet = [int(c) for c in cands]
            if v not in sheet:
                raw["reason"] = "the program's glyph is not on the sheet"
                return Answer(kind=AnswerKind.NOTHING, raw=raw)
            return Answer(kind=AnswerKind.PICK, value=sheet.index(v), raw=raw)
        if kind == "YESNO":
            return Answer(kind=AnswerKind.YES if bool(v) else AnswerKind.NO, raw=raw)
        raise ProtocolError(f"unknown answer_kind {kind!r}")

    # ------------------------------------------------------------------------------------------ U4a / U4b
    def why(self, ask_row: Mapping[str, Any]) -> List[int]:
        """The tape seqs of the examples the answering program(s) were fitted on — each example cited by its
        FEEDBACK row (the row that carries the shown answer). Report §4 R5: U4a counts TEACH rows only, so D
        alone reads 0 there by construction."""
        t0 = time.perf_counter()
        try:
            p = ask_row["payload"]
            ops = self._operands(p["operands"])
            cands = p.get("candidate_rows")
            tree, keys = self.core.resolve(list(p["cues"]), [o[0] for o in ops], cands is not None,
                                           str(p["answer_kind"]))
            if tree is None:
                return []
            seqs = []
            for k in keys:
                seqs.extend(int(e["fb"]) for e in self.core.examples.get(k, []))
            return sorted(set(seqs))
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def rule(self, cue: Sequence[str]) -> Dict[str, Any]:
        """The readable operation D answers `cue` with, and an executable that runs exactly that — frozen at
        this call (a copy of the state), so later learning never changes what was stated."""
        t0 = time.perf_counter()
        try:
            frozen = LibraryCore(self._q_lazy, self._core_config())
            frozen.load_state(json.loads(canonical_json(self.core.state())))
            text = frozen.rule_text(list(cue))

            def executable(ask_row: Mapping[str, Any], _core=frozen) -> Answer:
                return LibraryArm._answer_with(_core, ask_row)

            return {"text": text, "executable": executable}
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------------------------------ identity
    def state_sha(self) -> str:
        return self.core.state_sha()

    def snapshot(self, path: Union[str, Path]) -> None:
        Path(path).write_text(canonical_json({"arm": "D", "seed": self.seed, "state": self.core.state()}))

    def load(self, path: Union[str, Path]) -> None:
        d = json.loads(Path(path).read_text())
        self.core.load_state(d["state"])

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}

    # ------------------------------------------------------------------------------------------ for F's router
    def fits_all(self, ask_row: Mapping[str, Any]) -> bool:
        """F's router (B1-PREREG §4): «D has a program that fits all of the cue's training examples (a compound:
        all of its parts)». Read-only."""
        p = ask_row["payload"]
        ops = self._operands(p["operands"])
        cands = p.get("candidate_rows")
        tree, keys = self.core.resolve(list(p["cues"]), [o[0] for o in ops], cands is not None, str(p["answer_kind"]))
        if tree is None:
            return False
        return all(self.core.fits_all(k) for k in keys)
