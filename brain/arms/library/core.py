"""core.py — arm D's learner, independent of the tape's row format (report §1, §2.5, §2.6, §2.8).

edit: Claude (Opus 5.5, B1 builder 1), 2026-09-24 16:55 +0400 — the data memory, the examples, the per-cue
programs, the sleep (search → install → compress → log), the answer, the fit floor, why() and rule(). The Arm in
arm.py only translates the frozen protocol's rows and Answers to and from this class.

Identity law: every decision here is a pure function of the rows recorded so far and the config; no clock is
read; nothing iterates an unordered set; every real number is an exact int64.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import dsl
from .dsl import Sig
from .enumerator import Enumerator, Grammar, bridge_ok
from .evaluate import Batch, Data, Evaluator, LVal, Val, correct_mask, pick_index
from . import compress as C

STATE_VERSION = 1


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def quantize_pool(glances: np.ndarray) -> np.ndarray:
    """F_pool (creature/mind.py:_bind_pool — the mean of the glances, unit-normalised by
    genome/machinery.py:_unit) rounded to integer multiples of 2**-26. glances: (rows, 5, 144) float64."""
    out = np.zeros((glances.shape[0], glances.shape[2]), dtype=np.int64)
    for i in range(glances.shape[0]):
        v = np.mean(np.stack(list(glances[i]), axis=0), axis=0)
        n = np.linalg.norm(v)
        u = v / n if n > 0 else v
        out[i] = np.rint(u * float(1 << 26)).astype(np.int64)
    return out


class LibraryCore:
    """config keys (all optional): candidates_per_sleep (int), max_size (int, 20), fit_floor ('majority' |
    'all'), top_k (int, 3)."""

    def __init__(self, Q, config: Optional[Dict[str, Any]] = None):
        """Q: the (rows, 144) int64 quantized percepts, or a zero-argument callable returning them (read on first
        need, so a core that only loads and hashes a snapshot never opens the cache)."""
        cfg = dict(config or {})
        self._Q_src = Q
        self.budget = int(cfg.get("candidates_per_sleep", 2000))
        self.max_size = int(cfg.get("max_size", 20))
        self.fit_floor = str(cfg.get("fit_floor", "majority"))
        self.top_k = int(cfg.get("top_k", C.TOP_K))
        # learned state
        self.names: List[str] = []
        self.name_id: Dict[str, int] = {}
        self.teach: List[Tuple[int, int, int]] = []          # (seq, glance_row, name_id)
        self.pending: Dict[int, Dict[str, Any]] = {}         # ask_seq -> ask record
        self.examples: Dict[str, List[Dict[str, Any]]] = {}  # key -> [example]
        self.key_first: Dict[str, int] = {}                  # key -> seq of its first example's ASK
        self.programs: Dict[str, Dict[str, Any]] = {}        # key -> program record
        self.library: List[Dict[str, Any]] = []              # abstractions in creation order
        self.sleep_index = 0
        self.version = 0
        # derived (never hashed)
        self._data: Optional[Data] = None

    # ------------------------------------------------------------------------------------------ names
    def intern(self, name: str) -> int:
        nid = self.name_id.get(name)
        if nid is None:
            nid = len(self.names)
            self.names.append(name)
            self.name_id[name] = nid
            self._data = None
        return nid

    # ------------------------------------------------------------------------------------------ awake
    def record_teach(self, seq: int, glance_row: int, name: str) -> None:
        self.teach.append((int(seq), int(glance_row), self.intern(name)))
        self._data = None

    def record_ask(self, seq: int, cues: Sequence[str], operands: Sequence[Tuple[str, Any]],
                   cands: Optional[Sequence[int]], answer_kind: str) -> None:
        ops = []
        for kind, value in operands:
            if kind == "G":
                ops.append(["G", int(value)])
            else:
                ops.append(["N", self.intern(str(value))])
        self.pending[int(seq)] = {"cues": list(cues), "ops": ops,
                                  "cands": None if cands is None else [int(c) for c in cands],
                                  "kind": str(answer_kind)}

    def record_feedback(self, seq: int, ask_seq: int, right: Any) -> None:
        ask = self.pending.pop(int(ask_seq), None)
        if ask is None:
            return
        kind = ask["kind"]
        if kind == "NAME":
            r = self.intern(str(right))
        elif kind == "PICK":
            r = int(right)
        else:
            r = 1 if str(right) == "YES" else 0
        key = self.key_of(ask["cues"], ask["ops"], ask["cands"] is not None, kind)
        ex = {"ask": int(ask_seq), "fb": int(seq), "ops": ask["ops"], "cands": ask["cands"], "right": r}
        self.examples.setdefault(key, []).append(ex)
        self.key_first.setdefault(key, int(ask_seq))

    @staticmethod
    def key_of(cues: Sequence[str], ops: Sequence[Sequence[Any]], has_cands: bool, kind: str) -> str:
        return dsl.cue_key("+".join(cues), [o[0] for o in ops], has_cands, kind)

    # ------------------------------------------------------------------------------------------ data
    def data(self) -> Data:
        if self._data is None:
            order = [nid for _s, _r, nid in self.teach]
            taught: Dict[int, List[int]] = {}
            for _s, row, nid in self.teach:
                taught.setdefault(nid, []).append(row)
            Q = self._Q_src() if callable(self._Q_src) else self._Q_src
            self._data = Data(Q, order, taught, len(self.names))
        return self._data

    def batch_for(self, key: str, exs: Sequence[Dict[str, Any]], extra_names: int = 0) -> Tuple[Batch, np.ndarray]:
        n = len(exs)
        _cue, ops_t, has_cands, kind = dsl.parse_cue_key(key)
        inputs: Dict[str, object] = {}
        for i, t in enumerate(ops_t):
            arr = np.array([int(e["ops"][i][1]) for e in exs], dtype=np.int64)
            inputs[f"x{i}"] = Val(False, arr, np.ones(n, dtype=bool))
        if has_cands:
            K = max(len(e["cands"]) for e in exs)
            mat = np.zeros((n, K), dtype=np.int64)
            lens = np.zeros(n, dtype=np.int64)
            for j, e in enumerate(exs):
                mat[j, : len(e["cands"])] = e["cands"]
                lens[j] = len(e["cands"])
            inputs["cands"] = LVal(False, mat=mat, lens=lens, ok=np.ones(n, dtype=bool))
        right = np.array([e["right"] for e in exs], dtype=np.int64)
        if kind == "YESNO":
            right = right.astype(bool)
        return Batch(n, inputs), right

    # ------------------------------------------------------------------------------------------ references
    def _closure(self, tree: tuple, seen_abs=None, seen_keys=None) -> set:
        """Cue keys a tree reaches, through cue ops, cue refs, abstractions and those keys' own programs."""
        seen_abs = set() if seen_abs is None else seen_abs
        seen_keys = set() if seen_keys is None else seen_keys
        abs_by = {a["token"]: a for a in self.library}
        stack = [tree]
        while stack:
            t = stack.pop()
            tok = t[0]
            if dsl.is_cue_op(tok) or dsl.is_cue_ref(tok):
                k = tok[1:]
                if k not in seen_keys:
                    seen_keys.add(k)
                    p = self.programs.get(k)
                    if p is not None:
                        stack.append(p["tree"])
            elif dsl.is_abs(tok) and tok not in seen_abs and tok in abs_by:
                seen_abs.add(tok)
                stack.append(abs_by[tok]["body"])
            stack.extend(t[1:])
        return seen_keys

    def _usable_for(self, key: str, frozen_programs: Dict[str, Dict[str, Any]]):
        abstractions = []
        for a in self.library:
            if key in self._closure(a["body"]):
                continue
            abstractions.append((a["token"], a["sig"]))
        cue_ops = []
        for k in self._ordered_keys(frozen_programs):
            if k == key or "+" in dsl.parse_cue_key(k)[0]:
                continue
            if key in self._closure(frozen_programs[k]["tree"]):
                continue
            cue_ops.append((k, dsl.key_sig(k)))
        return abstractions, cue_ops

    def _ordered_keys(self, keys) -> List[str]:
        return sorted(keys, key=lambda k: (self.key_first.get(k, 1 << 60), k))

    # ------------------------------------------------------------------------------------------ evaluation
    def _abs_table(self) -> Dict[str, Tuple[tuple, int]]:
        return {a["token"]: (a["body"], len(a["sig"].ins)) for a in self.library}

    def _cue_table(self, programs: Dict[str, Dict[str, Any]]):
        return {k: (p["tree"], dsl.key_input_tokens(k), dsl.key_sig(k)) for k, p in programs.items()}

    def score_program(self, key: str, tree: tuple, programs=None) -> int:
        exs = self.examples.get(key, [])
        if not exs:
            return 0
        batch, right = self.batch_for(key, exs)
        ev = Evaluator(self.data(), batch, self._abs_table(), self._cue_table(programs or self.programs), memo=False)
        val = ev.run(tree)
        kind = dsl.parse_cue_key(key)[3]
        return int(correct_mask(val, kind, right, batch).sum())

    # ------------------------------------------------------------------------------------------ sleep
    def sleep(self) -> Dict[str, Any]:
        """One DreamCoder iteration (report §2.5): search every cue that needs it under the library and the cue
        programs FROZEN at the sleep's start, install, compress once, log."""
        self.sleep_index += 1
        frozen = {k: dict(v) for k, v in self.programs.items()}
        log: Dict[str, Any] = {"sleep": self.sleep_index, "budget": self.budget, "cues": [], "added": [],
                               "unspent": 0}
        keys = [k for k in self._ordered_keys(self.examples) if "+" not in dsl.parse_cue_key(k)[0]]
        work = []
        rescored: Dict[str, int] = {}
        for k in keys:
            n = len(self.examples[k])
            p = frozen.get(k)
            if p is not None:
                rescored[k] = self.score_program(k, p["tree"], frozen)
                perfect = rescored[k] == n
                unchanged = (p.get("searched_n") == n and p.get("searched_ver") == self.version)
                if perfect or unchanged:
                    log["cues"].append({"key": k, "n": n, "searched": False,
                                        "why": "perfect" if perfect else "nothing new since its last search",
                                        "score": rescored[k]})
                    continue
            work.append(k)
        searches: Dict[str, Dict[str, Any]] = {}
        for k in work:
            searches[k] = self._start_search(k, frozen)
        spent_total = 0
        if work:
            share = self.budget // len(work)
            for k in work:
                spent_total += self._run_search(searches[k], share)
                searches[k]["ev"].memo.clear()   # pure values: clearing changes no result, only memory
            pool = self.budget - spent_total
            open_keys = [k for k in work if not searches[k]["perfect"] and not searches[k]["exhausted"]]
            if open_keys and pool > 0:
                share2 = pool // len(open_keys)
                for k in open_keys:
                    spent_total += self._run_search(searches[k], share2)
        log["unspent"] = self.budget - spent_total
        # install, in the declared order; a new program that would close a cycle is refused (logged)
        changed = False
        for k in work:
            s = searches[k]
            n = len(self.examples[k])
            old = frozen.get(k)
            cand = s["best"]
            if old is not None:
                # the incumbent stays unless the search beat it: a higher score, or the same score in fewer
                # symbols (token ranks differ between sleeps, so no lexicographic comparison across them)
                inc = {"tree": old["tree"], "score": rescored.get(k, 0), "size": dsl.size(old["tree"]),
                       "found": old.get("found", self.sleep_index)}
                if cand is None or (cand["score"], -cand["size"]) <= (inc["score"], -inc["size"]):
                    cand = inc
            row = {"key": k, "n": n, "searched": True, "spent": s["spent"], "perfect": s["perfect"],
                   "exhausted": s["exhausted"], "max_size_reached": s["size_reached"]}
            if cand is None:
                row["score"] = 0
                log["cues"].append(row)
                continue
            if k in self._closure(cand["tree"]):
                row["refused_cycle"] = dsl.text_key(cand["tree"])
                log["cues"].append(row)
                continue
            prev = self.programs.get(k)
            self.programs[k] = {"tree": cand["tree"], "score": int(cand["score"]), "n": n,
                                "size": int(cand["size"]), "found": int(cand.get("found", self.sleep_index)),
                                "searched_n": n, "searched_ver": self.version}
            if prev is None or prev["tree"] != cand["tree"]:
                changed = True
            row.update({"score": int(cand["score"]), "program": dsl.render(cand["tree"]),
                        "size": int(cand["size"])})
            log["cues"].append(row)
        for k in keys:
            if k in self.programs and k not in work:
                self.programs[k]["score"] = int(rescored.get(k, self.programs[k]["score"]))
                self.programs[k]["n"] = len(self.examples[k])
        # compress once
        added = self._compress()
        if added or changed:
            self.version += 1
        log["added"] = added
        log["library_size"] = len(self.library)
        log["version"] = self.version
        return log

    def _start_search(self, key: str, frozen: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        abstractions, cue_ops = self._usable_for(key, frozen)
        ins = list(zip(dsl.key_input_tokens(key), dsl.key_sig(key).ins))
        g = Grammar(abstractions, cue_ops, ins, dsl.key_sig(key).out)
        en = Enumerator(g, dsl.key_sig(key), self.max_size)
        exs = self.examples[key]
        batch, right = self.batch_for(key, exs)
        abs_table = self._abs_table()
        ev = Evaluator(self.data(), batch, abs_table, self._cue_table(frozen), memo=True)
        return {"key": key, "gen": en.programs(), "ev": ev, "batch": batch, "right": right,
                "kind": dsl.parse_cue_key(key)[3], "n": len(exs), "best": None, "spent": 0,
                "perfect": False, "exhausted": False, "size_reached": 0, "index": 0}

    def _run_search(self, s: Dict[str, Any], share: int) -> int:
        spent = 0
        if s["perfect"] or s["exhausted"]:
            return 0
        while spent < share:
            try:
                tree = next(s["gen"])
            except StopIteration:
                s["exhausted"] = True
                break
            spent += 1
            s["index"] += 1
            sz = dsl.size(tree)
            s["size_reached"] = max(s["size_reached"], sz)
            val = s["ev"].run(tree)
            score = int(correct_mask(val, s["kind"], s["right"], s["batch"]).sum())
            b = s["best"]
            if b is None or score > b["score"]:   # equal score: the earlier (smaller, then lexicographic) stays
                s["best"] = {"tree": tree, "score": score, "size": sz, "found": self.sleep_index}
            if score == s["n"]:
                s["perfect"] = True
                break
        s["spent"] += spent
        return spent

    def _compress(self) -> List[Dict[str, Any]]:
        abs_sigs = {a["token"]: a["sig"] for a in self.library}
        cue_sigs = {k: dsl.key_sig(k) for k in self.programs}
        typer = C.Typer(dict(abs_sigs), cue_sigs)
        corpus = []
        for k in self._ordered_keys(self.programs):
            ins = dict(zip(dsl.key_input_tokens(k), dsl.key_sig(k).ins))
            corpus.append(C.Program(k, self.programs[k]["tree"], ins))
        added, new_corpus = C.compress(corpus, typer, len(self.library), self.top_k)
        out = []
        for token, pat, sig, g in added:
            self.library.append({"token": token, "body": pat, "sig": sig, "sleep": self.sleep_index, "gain": int(g)})
            out.append({"token": token, "body": dsl.render(pat), "sig": repr(sig), "gain": int(g)})
        for p in new_corpus:
            if self.programs[p.key]["tree"] != p.tree:
                self.programs[p.key]["tree"] = p.tree
                self.programs[p.key]["size"] = dsl.size(p.tree)
        return out

    # ------------------------------------------------------------------------------------------ answering
    def answers_ok(self, key: str) -> bool:
        p = self.programs.get(key)
        if p is None:
            return False
        if self.fit_floor == "all":
            return p["score"] == p["n"]
        return 2 * p["score"] > p["n"]

    def fits_all(self, key: str) -> bool:
        p = self.programs.get(key)
        return p is not None and p["n"] > 0 and p["score"] == p["n"]

    def resolve(self, cues: Sequence[str], op_types: Sequence[str], has_cands: bool, kind: str):
        """The program answering an ask: (tree, [keys it was fitted on]) or (None, reason)."""
        if len(cues) == 1:
            key = dsl.cue_key(cues[0], op_types, has_cands, kind)
            if key not in self.programs:
                return None, "no program"
            if not self.answers_ok(key):
                return None, "under the fit floor"
            return self.programs[key]["tree"], [key]
        # a compound: compose of its parts, in order (report §2.3). Part 1 takes the ask's operands; every later
        # part takes ONE operand bridged from the previous part's output; the last part answers the ask's kind.
        parts: List[str] = []
        prev_out = None
        for i, cue in enumerate(cues):
            last = i == len(cues) - 1
            found = None
            for k in self._ordered_keys(self.programs):
                c, ops, hc, kd = dsl.parse_cue_key(k)
                if c != cue or (hc and not has_cands):
                    continue
                if i == 0 and list(ops) != list(op_types):
                    continue
                if i > 0 and (len(ops) != 1 or not bridge_ok(prev_out, ops[0])):
                    continue
                if last and kd != kind:
                    continue
                found = k
                break
            if found is None:
                return None, f"no program for part {cue}"
            if not self.answers_ok(found):
                return None, f"part {cue} under the fit floor"
            parts.append(found)
            prev_out = dsl.key_sig(found).out
        tree = ("&" + parts[-1],)
        for k in reversed(parts[:-1]):
            tree = ("compose", ("&" + k,), tree)
        return tree, parts

    def evaluate_one(self, tree: tuple, ops: Sequence[Sequence[Any]], cands: Optional[Sequence[int]],
                     programs=None):
        inputs: Dict[str, object] = {}
        for i, (t, v) in enumerate(ops):
            inputs[f"x{i}"] = Val(False, np.array([int(v)], dtype=np.int64), np.ones(1, dtype=bool))
        if cands is not None:
            mat = np.array([list(cands)], dtype=np.int64)
            inputs["cands"] = LVal(False, mat=mat, lens=np.array([len(cands)], dtype=np.int64),
                                   ok=np.ones(1, dtype=bool))
        batch = Batch(1, inputs)
        ev = Evaluator(self.data(), batch, self._abs_table(), self._cue_table(programs or self.programs), memo=False)
        return ev.run(tree), batch

    # ------------------------------------------------------------------------------------------ rule text
    def rule_text(self, cues: Sequence[str]) -> str:
        """U4b's readable operation for a cue (every shape D holds a program for), or for a compound (its
        compose), with the definitions it rests on: the library entries and the other cues' programs it calls."""
        lines: List[str] = []
        keys: List[str] = []
        if len(cues) == 1:
            keys = [k for k in self._ordered_keys(self.programs) if dsl.parse_cue_key(k)[0] == cues[0]]
            if not keys:
                return f"{cues[0]}: no program (D has not fitted this cue)"
            for k in keys:
                p = self.programs[k]
                floor = "answers" if self.answers_ok(k) else "under the fit floor: answers NOTHING"
                lines.append(f"{k} := {dsl.render(p['tree'])}    [reproduces {p['score']}/{p['n']} shown examples; {floor}]")
        else:
            lines.append(" then ".join(cues) + " := compose of the parts' programs, in order (a NAME passed on to a"
                         " glyph slot is the name's first TEACH exemplar)")
            for c in cues:
                ks = [k for k in self._ordered_keys(self.programs) if dsl.parse_cue_key(k)[0] == c]
                for k in ks:
                    lines.append(f"  {k} := {dsl.render(self.programs[k]['tree'])}")
                    keys.append(k)
        # the definitions reached
        seen_abs, seen_keys = set(), set()
        for k in keys:
            self._closure(self.programs[k]["tree"], seen_abs, seen_keys)
        abs_by = {a["token"]: a for a in self.library}
        for tok in [a["token"] for a in self.library if a["token"] in seen_abs]:
            a = abs_by[tok]
            holes = ", ".join(f"#{i}:{t}" for i, t in enumerate(a["sig"].ins))
            lines.append(f"  where {tok}({holes}) -> {a['sig'].out} := {dsl.render(a['body'])}")
        for k in self._ordered_keys([k for k in seen_keys if k not in keys and k in self.programs]):
            lines.append(f"  where @{k} := {dsl.render(self.programs[k]['tree'])}")
        return "\n".join(lines)

    # ------------------------------------------------------------------------------------------ state
    def state(self) -> Dict[str, Any]:
        return {
            "v": STATE_VERSION,
            "names": list(self.names),
            "teach": [list(t) for t in self.teach],
            "pending": {str(k): v for k, v in sorted(self.pending.items())},
            "examples": {k: v for k, v in sorted(self.examples.items())},
            "key_first": dict(sorted(self.key_first.items())),
            "programs": {k: {"tree": dsl.to_json(p["tree"]), "score": p["score"], "n": p["n"], "size": p["size"],
                             "found": p["found"], "searched_n": p.get("searched_n"),
                             "searched_ver": p.get("searched_ver")}
                         for k, p in sorted(self.programs.items())},
            "library": [{"token": a["token"], "body": dsl.to_json(a["body"]), "ins": list(a["sig"].ins),
                         "out": a["sig"].out, "sleep": a["sleep"], "gain": a["gain"]} for a in self.library],
            "sleep_index": self.sleep_index,
            "version": self.version,
        }

    def state_sha(self) -> str:
        return hashlib.sha256(canonical(self.state()).encode("utf-8")).hexdigest()

    def load_state(self, st: Dict[str, Any]) -> None:
        assert st["v"] == STATE_VERSION
        self.names = list(st["names"])
        self.name_id = {n: i for i, n in enumerate(self.names)}
        self.teach = [tuple(t) for t in st["teach"]]
        self.pending = {int(k): v for k, v in st["pending"].items()}
        self.examples = {k: list(v) for k, v in st["examples"].items()}
        self.key_first = {k: int(v) for k, v in st["key_first"].items()}
        self.programs = {k: {"tree": dsl.from_json(p["tree"]), "score": p["score"], "n": p["n"],
                             "size": p["size"], "found": p["found"], "searched_n": p.get("searched_n"),
                             "searched_ver": p.get("searched_ver")} for k, p in st["programs"].items()}
        self.library = [{"token": a["token"], "body": dsl.from_json(a["body"]), "sig": Sig(a["ins"], a["out"]),
                         "sleep": a["sleep"], "gain": a["gain"]} for a in st["library"]]
        self.sleep_index = int(st["sleep_index"])
        self.version = int(st["version"])
        self._data = None
