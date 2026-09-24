"""a0.py — ARM A0, THE CELLS (the FLOOR) — B1-PREREG.md §4's table, first row.

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 19:2x +0400 — B1-PREREG.md §9 row 1, step 8.

`genome.machinery.Organism` under `brain/genomes/B1-CELLS.genome` (= `genome/ALPHA4.genome` with every line
outside the cells/episodes/sleep removed, §4's table) + `genome.fast.Episodes`. TEACH is the creature's own
heard-canvas road reduced to the organism: `creature/mind.py:_consume_eye`, WITHOUT BIND (B1-CELLS.genome
does not declare it, exactly as ALPHA4.genome does not), calls `Organism.moment()` ONCE PER GLANCE — so one
canvas (5 glances: 4 located + 1 coarse, §2.5) becomes FIVE moments, `org.t` advancing by 5 per TEACH row,
all five sharing the same word vector.

NAME/POINT/IS are answered by the creature's own LIVE question rules — `genome/ask.py`'s own commands
(what-is / which / is), which this module calls the SAME way, over `recall_many`/`edge_many` (glances
summed, not a single glance): NAME = `recall_many("sight", glances)` graded by THRESH/ANSWER's own
`own_band`/`unknown below 0.911` reading (`_grade_bucket`, `genome/questions.py`) into NAME / RESEMBLES /
UNKNOWN; IS = the Q3 rule (`ask.py`'s own "is" command); POINT = the Q4 rule generalised from 2 candidates to
however many `candidate_rows` the ask carries (`edge_many`'s own summed-edge rule, unchanged). Every relation
cue reads NOTHING — A0 has no relation machinery (§4's table).

The LEDGER (`genome.questions.build_ledgers`) that turns a recalled cell id back into a WORD is not a
saved-run artefact here (there is no `ledger.json` — A0 is a live, growing organism, not a closed run): this
arm keeps `_moment_thing: Dict[moment_index, name]`, written once per TEACH glance-moment, and rebuilds the
ledger from `org.births`/`org.merges` + `_moment_thing` on every `answer()` call (`build_ledgers` is cheap —
one pass over the birth/merge logs, not a search). `_moment_thing` is included in `state_sha()` (never only
`org.state_hash()`) because it is part of what this arm has LEARNED — which moment taught which name — even
though it lives outside `Organism`'s own array/scalar state.

Simplification declared here, not hidden: episodes are written with `surprise=0.0` for every glance-moment
(A0 has no PREDICT/SURPRISE wiring — that is the mind's own modulation layer, explicitly removed, §4's own
line-removal list) — `SLEEP`'s `most_surprising` ranking is therefore a stable arbitrary order among
episodes, not an informed one. This does not affect correctness (a replay of the same tape re-derives the
same order every time — ties are broken by episode id, `Episodes.most_surprising`'s own rule) but is a real
capability gap the seat should know about if A0's GROWS/COST numbers look surprising.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import numpy as np

from genome import questions as genome_questions
from genome import sleep as genome_sleep
from genome.fast import Episodes
from genome.machinery import GenomeError, Organism, parse_genome
from genome.world import encode_word

from brain.glance_cache import Cache
from brain.protocol import Answer, AnswerKind, RELATION_CUES, is_name_operand, is_row_operand

B1_CELLS_GENOME_PATH = Path(__file__).resolve().parents[2] / "genomes" / "B1-CELLS.genome"


class A0Error(Exception):
    pass


def _load_genome_text(config: Mapping[str, Any]) -> str:
    p = Path(config.get("genome_path", B1_CELLS_GENOME_PATH))
    if not p.exists():
        raise A0Error(f"A0: genome file not found: {p}")
    return p.read_text()


class A0Arm:
    def __init__(self, seed: int, config: Mapping[str, Any]) -> None:
        self.seed = int(seed)
        self.config = dict(config)
        self.g = parse_genome(_load_genome_text(self.config))
        self.org = Organism(self.g)
        fast = self.g.declared.get("FAST")
        if fast is None:
            raise A0Error("A0: the genome must declare FAST (episodes)")
        self.episodes = Episodes(int(fast["episodes"]), self.g.sight_dim(), self.g.words_dim())
        cache_dir = self.config.get("cache_dir")
        self._cache: Optional[Cache] = Cache(cache_dir) if cache_dir else None
        self._moment_thing: Dict[int, str] = {}
        self._events = 0
        self._ms = 0.0

    # ------------------------------------------------------------------ plumbing
    def _cache_glances(self, row: int) -> np.ndarray:
        if self._cache is None:
            raise A0Error("A0: no cache_dir in config — cannot resolve a glance_row")
        return self._cache.glances(row)

    def _ledgers(self):
        return genome_questions.build_ledgers(self.org, self._moment_thing)

    # ------------------------------------------------------------------ ingestion
    def fit_event(self, row: Mapping[str, Any], valence: Optional[str] = None) -> None:
        t0 = time.perf_counter()
        kind = row["kind"]
        if kind == "TEACH":
            p = row["payload"]
            glances = self._cache_glances(int(p["glance_row"]))
            x_w = encode_word(p["name"], self.g.ear_blank_zero)
            for i in range(glances.shape[0]):
                moment_idx = self.org.t
                self._moment_thing[moment_idx] = p["name"]
                self.org.moment(glances[i], x_w)
                self.episodes.write(moment_idx, glances[i], x_w, p["name"], 0.0, glance=i,
                                     tape_moment=str(row["seq"]))   # U4a's why() reads this back as the tape seq
        # ARRIVAL, ASK (world-event ingestion) and FEEDBACK: A0 has no separate ingestion step for these —
        # its only learning signal is TEACH (HEBB/DELTA/BIRTH/PRUNE/MERGE all run inside `Organism.moment`,
        # called only from TEACH above); A0 has no reward/valence mechanism at all (declared: the machinery
        # this arm wraps has none — a relation-answering FEEDBACK loop belongs to A1/A2/A3/D, not the cells).
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    def sleep(self, steps: int) -> None:
        t0 = time.perf_counter()
        genome_sleep.sleep(self.org, self.episodes, steps)
        self._events += 1
        self._ms += (time.perf_counter() - t0) * 1000.0

    # ------------------------------------------------------------------ answering
    def answer(self, ask_row: Mapping[str, Any], learn: bool = False) -> Answer:
        t0 = time.perf_counter()
        try:
            p = ask_row["payload"]
            cues: List[str] = p["cues"]
            if any(c in RELATION_CUES for c in cues):
                return Answer(kind=AnswerKind.NOTHING)   # "no road" — §4's table
            ledgers = self._ledgers()
            Lw = ledgers["words"]
            if cues == ["NAME"]:
                return self._answer_name(p, Lw)
            if cues == ["IS"]:
                return self._answer_is(p, Lw)
            if cues == ["POINT"]:
                return self._answer_point(p, Lw)
            return Answer(kind=AnswerKind.NOTHING)
        finally:
            self._events += 1
            self._ms += (time.perf_counter() - t0) * 1000.0

    def _operand_glances(self, op: Mapping[str, Any]) -> List[np.ndarray]:
        g = self._cache_glances(int(op["value"]))
        return [g[i] for i in range(g.shape[0])]

    def _answer_name(self, p: Mapping[str, Any], Lw) -> Answer:
        glances = self._operand_glances(p["operands"][0])
        r = self.org.recall_many("sight", glances)
        if r["cell"] is None:
            return Answer(kind=AnswerKind.UNKNOWN, raw={"reason": r["reason"]})
        names_ = Lw.get(r["cell"], set())
        if not names_:
            return Answer(kind=AnswerKind.UNKNOWN, raw={"reason": "cell has no ledger entry"})
        nm = sorted(names_)[0]   # a cell born on >1 name (a merge) answers its alphabetically-first name
        # _grade_bucket(r) with r["cell"] is not None returns only "sure_bare" or "unsure" (its other two
        # branches are for an abstention, already handled above) — ANSWER's own "resembles under own-band"
        # reading (§4's table) is what "unsure" names: a real cell, held with less than full confidence.
        grade = genome_questions._grade_bucket(r)
        if grade == "unsure":
            return Answer(kind=AnswerKind.RESEMBLES, value=nm, raw={"grade": grade})
        return Answer(kind=AnswerKind.NAME, value=nm, raw={"grade": grade})

    def _answer_is(self, p: Mapping[str, Any], Lw) -> Answer:
        name_op = next((o for o in p["operands"] if is_name_operand(o)), None)
        row_op = next((o for o in p["operands"] if is_row_operand(o)), None)
        if name_op is None or row_op is None:
            raise A0Error(f"IS needs one name operand and one row operand: {p['operands']!r}")
        glances = self._operand_glances(row_op)
        r = self.org.recall_many("sight", glances)
        yes = r["cell"] is not None and Lw.get(r["cell"], set()) == {name_op["value"]}
        return Answer(kind=AnswerKind.YES if yes else AnswerKind.NO, raw={"reason": r.get("reason")})

    def _answer_point(self, p: Mapping[str, Any], Lw) -> Answer:
        name_op = next((o for o in p["operands"] if is_name_operand(o)), None)
        if name_op is None:
            raise A0Error(f"POINT needs a name operand: {p['operands']!r}")
        wc = genome_questions.word_cells(self.org, Lw, name_op["value"])
        candidates = p.get("candidate_rows") or []
        if not candidates:
            raise A0Error("POINT needs candidate_rows")
        if not wc:
            return Answer(kind=AnswerKind.UNKNOWN)
        best_idx, best_val = None, 0.0
        for idx, cand_row in enumerate(candidates):
            glances = [g for g in self._cache_glances(int(cand_row))]
            e = max((self.org.edge_many("sight", glances, c) for c in wc), default=0.0)
            if best_idx is None or e > best_val:
                best_idx, best_val = idx, e
        if best_val <= 0.0:
            return Answer(kind=AnswerKind.UNKNOWN)
        return Answer(kind=AnswerKind.PICK, value=int(best_idx))

    # ------------------------------------------------------------------ U4a: why
    def why(self, ask_row: Mapping[str, Any]) -> List[int]:
        """genome.questions.why(org, ledgers, episodes, word) — the episodes that ground the LAST answer's
        word. Only meaningful for a NAME ask (U4a asks "why <letter>?" about a NAME the arm just named
        right, §5.3); any other cue returns an empty list (no episode-level "why" exists for it)."""
        p = ask_row["payload"]
        if p.get("cues") != ["NAME"]:
            return []
        ledgers = self._ledgers()
        glances = self._operand_glances(p["operands"][0])
        r = self.org.recall_many("sight", glances)
        if r["cell"] is None:
            return []
        names_ = ledgers["words"].get(r["cell"], set())
        if not names_:
            return []
        word = sorted(names_)[0]
        result = genome_questions.why(self.org, ledgers, self.episodes, word)
        # genome.questions.why() returns FAST episode ids in "episodes" (its own docstring); translate each
        # to the TAPE SEQ this arm stamped it with at write time (`tape_moment`, set in fit_event's TEACH
        # branch) — the Arm protocol's why() contract is tape seqs, a different numbering than episode ids.
        seqs: List[int] = []
        for eid in result.get("episodes", []):
            rec = self.episodes.get(eid)
            if rec is not None and rec.get("tape_moment"):
                seqs.append(int(rec["tape_moment"]))
        return sorted(set(seqs))

    # ------------------------------------------------------------------ identity / persistence
    def state_sha(self) -> str:
        import hashlib
        h = hashlib.sha256()
        h.update(self.org.state_hash().encode())
        # _moment_thing: part of what this arm has learned (which moment taught which name), NOT captured
        # by Organism.state_hash() itself — included so state_sha fully characterises future answers.
        mt_canon = json.dumps({str(k): v for k, v in sorted(self._moment_thing.items())}, sort_keys=True)
        h.update(mt_canon.encode())
        return h.hexdigest()

    def snapshot(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.org.save(path)   # writes path.npz + path.json (Organism.save's own suffix convention)
        self.episodes.save(Path(str(path) + "_episodes.npz"))   # Episodes.save writes to ITS OWN path exactly, no suffix added
        Path(str(path) + "_moment_thing.json").write_text(
            json.dumps({str(k): v for k, v in self._moment_thing.items()}))
        Path(str(path) + "_cost.json").write_text(json.dumps({"events": self._events, "ms": self._ms}))

    def load(self, path: Union[str, Path]) -> None:
        path = Path(path)
        self.org = Organism.load(path, self.g)
        ep_path = Path(str(path) + "_episodes.npz")
        if ep_path.exists():
            self.episodes = Episodes.load(ep_path)   # classmethod: returns a NEW Episodes, reassigned here
        else:
            self.episodes = Episodes(int(self.g.declared["FAST"]["episodes"]), self.g.sight_dim(), self.g.words_dim())
        mt_path = Path(str(path) + "_moment_thing.json")
        if mt_path.exists():
            self._moment_thing = {int(k): v for k, v in json.loads(mt_path.read_text()).items()}
        cost_path = Path(str(path) + "_cost.json")
        if cost_path.exists():
            c = json.loads(cost_path.read_text())
            self._events, self._ms = c.get("events", 0), c.get("ms", 0.0)

    def cost(self) -> Dict[str, float]:
        return {"events": self._events, "ms": self._ms}
