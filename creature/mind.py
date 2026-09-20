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

import json
import os
from pathlib import Path
from typing import Dict, FrozenSet, Optional, Tuple

import numpy as np
from PIL import Image

from genome import gaze
from genome.fast import Episodes
from genome.machinery import Genome, GenomeError, Organism, parse_genome
from genome.park import Park
from genome.predict import Predictor, file as predict_file, score as predict_score
from genome.questions import build_ledgers, why as questions_why
from genome.sleep import cycle as run_cycle, sleep as run_sleep
from genome.world import encode_word

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

try:                                    # TRAITS (PREREG §11.2) is not yet on master at the time of A9/A10;
    from genome.traits import Traits    # gated on BOTH "TRAITS" in declared AND this import having succeeded —
    _TRAITS_AVAILABLE = True            # never a stub of this module written here (Builder A owns creature/, not genome/).
except ImportError:
    Traits = None                       # type: ignore[assignment]
    _TRAITS_AVAILABLE = False

SNAPSHOT_EVERY = 500


class Mind:
    """genome_path: the genome file (read once, text + parsed). run_root: the SAME root the body's Tape
    uses — payload bytes for a tape row live at run_root/tape/<row.payload>. blind: gene names this mind
    is blind to (e.g. {"gaze"} runs the random-gaze twin, PREREG §2.9's --blind gaze)."""

    def __init__(self, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset()):
        self.genome_path = Path(genome_path)
        self.run_root = Path(run_root)
        self.genome_text = self.genome_path.read_text()
        self.genome: Genome = parse_genome(self.genome_text)
        self.blind = frozenset(blind)

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
        self.predictor: Optional[Predictor] = Predictor(self.org) if "PREDICT" in self.genome.declared else None
        self._last_sleep_at: int = 0        # org.t at the last SLEEP boundary crossed

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
        self._canvas_index: int = 0
        self._filed_predictions: list = []          # [{"row": FILE's row dict, "due_canvas": int}, ...] awaiting the next showing of their word
        self.think_counters: Dict[str, int] = {"thinks": 0, "parked": 0, "beliefs": 0, "predictions_filed": 0, "predictions_scored": 0}
        # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: the words the ear has ever delivered to a met canvas
        # (sight-only "" never enters). A word not in it OPENS AN ARRIVAL when ARRIVAL is declared (below);
        # rebuilt at resume from the ledger's moment_word so a resumed mind and a replay agree.
        self._heard: set = set()

        self.pending: Dict[str, str] = {}                 # ear-consumed, eye not yet arrived: moment -> word
        self.moment_word: Dict[int, str] = {}              # org.t (per GLANCE, before increment) -> word — build_ledgers' input
        self.last_seq: int = 0
        self.sight_only_skipped: int = 0
        self.journal_rows_written: int = 0
        self.snapshot_count: int = 0
        self.sleep_count: int = 0                        # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — STATUS.sleeps (PREREG §11.1 step 4)
        if "TRAITS" in self.genome.declared:             # edit: Claude (Fable 5.1), 2026-09-19 23:17 +0400 — a declared gene the machinery does not run must REFUSE at start (PREREG §3/§12): the
            raise GenomeError("TRAITS is declared but the mind has no TRAITS interpreter yet (wave 3: same-cell positives) — the organism does not start")   # sleep step called Traits.learn on the CLASS; it would have crashed the mind at its first sleep
        self._last_snapshot_moments: int = 0

        (self.run_root / "journal").mkdir(parents=True, exist_ok=True)
        (self.run_root / "state").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ consume
    def consume(self, row: Dict[str, object]) -> None:
        sense = row["sense"]
        meta = row.get("meta") or {}
        moment = meta.get("moment")
        if sense == "ear":
            self.pending[moment] = meta.get("word")
        elif sense == "eye":
            self._consume_eye(row, moment)
        # a "door" row (the ask door / other senses not yet armed) carries no organism work here
        self.last_seq = int(row["seq"])
        if self.org.t - self._last_snapshot_moments >= SNAPSHOT_EVERY:
            self.snapshot()

    def _consume_eye(self, row: Dict[str, object], moment: Optional[str]) -> None:
        payload_path = self.run_root / "tape" / row["payload"]
        rgb = np.asarray(Image.open(payload_path).convert("RGB"), dtype=np.uint8)
        mode = "random" if "gaze" in self.blind else "surprise"
        g = gaze.glances(rgb, self.genome.retina, self.genome.gaze, mode, row["sha"])
        word = self.pending.pop(moment, None) if moment is not None else None

        # PREREG §11.1 step 1 (PREDICT): measured once, on the FIRST glance, regardless of whether this
        # canvas has a word — a sight-only canvas is just as surprising or expected as a worded one.
        predict_on = self.predictor is not None and "predict" not in self.blind
        fast_on = self.episodes is not None
        err, lr_scale = 0.0, 1.0
        if predict_on and g["feats"]:
            err = self.predictor.error(g["feats"][0])
            lr_scale = self.predictor.modulate(1.0)
        t_at_f0 = self.org.t
        f0 = g["feats"][0] if g["feats"] else None

        if word is not None:
            births_before = len(self.org.births)
            edges_before = len(self.org.edges_log)
            prunes_before = len(self.org.prunes_log)
            xw = encode_word(word, self.genome.ear_blank_zero)
            # edit: Claude (Fable 5.1), 2026-09-20 11:59 +0400 — PREREG §15: a never-heard word is an ARRIVAL — the birth budget is
            # fresh BEFORE the moment that first meets it (life 1 never called new_arrival: arrivals 0, budget spent once,
            # 419 births refused, nothing born after 07:41 +04). Gated on the gene: an undeclared ARRIVAL changes nothing.
            arrival_n: Optional[int] = None
            if word not in self._heard:
                self._heard.add(word)
                if "ARRIVAL" in self.genome.declared:
                    self.org.new_arrival()
                    arrival_n = int(self.org.arrivals)
            for x in g["feats"]:
                self.moment_word[self.org.t] = word          # keyed by the organism's OWN moment counter, one per glance
                S, T = self.org.moment(x, xw, lr_scale=lr_scale)
                if predict_on:
                    self.predictor.note_winners(S)
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0, x_w=xw, word=word, surprise=err) if fast_on else None
            self._score_due_predictions(word, g["feats"][0] if g["feats"] else None)
            births = [[b[1], int(b[2]), b[3]] for b in self.org.births[births_before:]]
            edges_born = len(self.org.edges_log) - edges_before
            edges_pruned = len(self.org.prunes_log) - prunes_before
            journal_row = {
                "seq": row["seq"], "moment": moment, "word": word,
                "fix": [[int(y), int(x)] for (y, x) in g["fix"]],
                "births": births,
                "cells": [int(self.org.sight.alive.sum()), int(self.org.words.alive.sum())],
                "edges": [edges_born, edges_pruned],
                "err": round(err, 4), "lr": round(lr_scale, 3), "ep": ep_id,
                "hash": self.org.state_hash(),
                **({"arrival": arrival_n} if arrival_n is not None else {}),   # PREREG §15: an event field on the row where an arrival opened
            }
            self._write_journal(row["at"], journal_row)
        elif fast_on:
            # PREREG §11.1 step 2: sight-only, FAST declared -> Organism.moment_sight per glance (B2),
            # never Organism.moment (no word to MEET); an episode is still written, word "". A sight-only
            # glance can still BIRTH a sight cell (moment_sight's own _resonate call), and
            # questions.build_ledgers needs moment_thing[m] for EVERY birth moment, sight-only ones
            # included, or snapshot() KeyErrors the first time such a birth happens (caught by this
            # test, not by inspection) -- word "" here, exactly what the written episode itself carries.
            for x in g["feats"]:
                self.moment_word[self.org.t] = ""
                self.org.moment_sight(x)
            xw_blank = encode_word("", self.genome.ear_blank_zero)
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0, x_w=xw_blank, word="", surprise=err)
            self._write_journal(row["at"], {
                "seq": row["seq"], "moment": moment, "word": None,
                "err": round(err, 4), "ep": ep_id, "hash": self.org.state_hash(),
            })
        else:
            # the skeleton's own law, untouched: no FAST declared -> a sight-only canvas is skipped
            # entirely, the organism never sees it (G4-8's byte-identical pin depends on this).
            self.sight_only_skipped += 1
            self._write_journal(row["at"], {"seq": row["seq"], "moment": moment, "sight_only": True})

        self._canvas_index += 1
        self._maybe_sleep(row)
        self._maybe_think(row)

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
            result = run_sleep(self.org, self.episodes, n)
            self.sleep_count += 1
            cycled = run_cycle(self.org)
            if "TRAITS" in self.genome.declared and _TRAITS_AVAILABLE:
                Traits.learn(self.episodes)      # per the interface name given for wave 2; unexercised until genome/traits.py lands
            self._write_journal(row["at"], {
                "seq": row["seq"], "sleep": {**result, "cycle": cycled}, "hash": self.org.state_hash(),
            })

    # ------------------------------------------------------------------ THINK (A11, PREREG §11.1 step 3)
    def _score_due_predictions(self, word: str, first_glance: Optional[np.ndarray]) -> None:
        """A prediction filed by THINK's kind-(b) work becomes scorable the next time ITS OWN word is
        shown again — "the journal's err/recall on the next canvas with that word" (PREREG's own route
        text). Simplification, documented in the report: the decider "recall == word" is evaluated by a
        fresh word-cell lookup (questions.build_ledgers) rather than a persisted per-edge index — correct,
        but O(births) per score, acceptable at this life's scale."""
        if not self._filed_predictions or first_glance is None:
            return
        still_pending = []
        ledgers = None
        for entry in self._filed_predictions:
            if entry["target_word"] == word and self._canvas_index >= entry["due_canvas"]:
                if ledgers is None:
                    ledgers = build_ledgers(self.org, self.moment_word)
                r = self.org.recall("sight", first_glance)
                Lw = ledgers["words"]
                evidence = r["cell"] is not None and Lw.get(r["cell"], set()) == {word}
                scored = predict_score(entry["row"], evidence)
                predict_ledger_path = self.run_root / "state" / "predictions.jsonl"
                predict_ledger_path.parent.mkdir(parents=True, exist_ok=True)
                with predict_ledger_path.open("a") as f:
                    f.write(json.dumps(scored, default=str) + "\n")
                self.think_counters["predictions_scored"] += 1
            else:
                still_pending.append(entry)
        self._filed_predictions = still_pending

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
                rec = self.episodes.get(eid)
                if rec is None or not rec["word"] or rec["word"] in seen_words:
                    continue
                r = self.org.recall("sight", rec["x_s"])
                if r["cell"] is None:
                    seen_words.add(rec["word"])
                    pool.append({"kind": "word", "key": rec["word"], "episode": eid, "pred": None})
            for eid in range(0, n_written):
                rec = self.episodes.get(eid)
                if rec is not None and rec["word"] == "":
                    pool.append({"kind": "sight", "key": f"ep{eid}", "episode": eid, "pred": None})
        now = self._canvas_index
        for entry in self._filed_predictions:
            if now >= entry["due_canvas"]:
                pool.append({"kind": "due", "key": entry["target_word"], "episode": None, "pred": entry["row"]})
        return pool

    def _think_choose(self, pool: list):
        if not pool:
            return None
        curiosity_on = self.interests is not None and "curiosity" not in self.blind
        if curiosity_on:
            return self.interests.choose(pool, self._think_rng)
        if "curiosity" in self.blind and "CURIOSITY" in self.genome.declared:
            return pool[int(self._think_rng.integers(0, len(pool)))]      # blind curiosity: the rng's uniform pick
        return pool[0]                                                    # no CURIOSITY declared: the first item

    def _think_work(self, item: dict) -> Dict[str, object]:
        """Works one pool item; returns {"outcome", "parked", ...}. Every dead end goes to
        park.answer(want, reason) when PARK is declared (PREREG: "every dead end goes to park.answer");
        without PARK declared a dead end simply stays a dead end (nothing to park it with)."""
        def dead_end(want: str, reason: str) -> Dict[str, object]:
            parked = False
            if self.park is not None:
                parked = self.park.answer(want, reason) == "parked"
                if parked:
                    self.think_counters["parked"] += 1
            return {"outcome": reason, "parked": parked}

        if item["kind"] == "word":
            word = item["key"]
            if not _THINK_LAWS_AVAILABLE:
                return dead_end(word, "think_laws_unavailable")
            ledgers = build_ledgers(self.org, self.moment_word)
            record = questions_why(self.org, ledgers, self.episodes, word)
            rec = self.episodes.get(item["episode"]) if self.episodes is not None else None
            if rec is None:
                return dead_end(word, "episode_gone")
            # edit: Claude (Fable 5.1), 2026-09-19 23:33 +0400 — PREREG §11.1 (a) as read in the first 30-min life: the pool admits a word whose
            # LATEST glance abstains, and re-asking the SAME glance can only abstain again (172/172 dead ends). The work now asks over the
            # word's last five episodes' glances (Organism.recall_many, G1's road) — a word known in general though this glance was not
            # becomes a belief; a word unknown over five glances is a dead end (parkable after three).
            xs = self._recent_word_glances(word, 5, fallback=rec["x_s"])
            r = self.org.recall_many("sight", xs)
            if r.get("cell") is None:
                return dead_end(word, "no_cell_answers")
            # edit: Claude (Fable 5.1), 2026-09-19 23:37 +0400 — believe() takes the beliefs FILE; the run ROOT was passed and the first belief
            # ever reached (after the recall_many fix) crashed the mind with IsADirectoryError — the crash law fired as designed.
            # edit: Claude (Fable 5.1), 2026-09-19 23:38 +0400 — why() tags cells as (area, id); believe() takes ints and clash() compares the sets,
            # so a belief carries the word's SIGHT cells (its look); the word-side cells are the word's own by definition.
            sight_cells = [int(c) for area, c in record["cells"] if area == "sight"]
            row = think_laws.believe(word, sight_cells, record["episodes"], self.org.t, self.run_root / "state" / "beliefs.jsonl")
            self.think_counters["beliefs"] += 1
            return {"outcome": "belief", "parked": False, "belief": row}

        if item["kind"] == "sight":
            rec = self.episodes.get(item["episode"]) if self.episodes is not None else None
            if rec is None:
                return dead_end(item["key"], "episode_gone")
            candidates = self.episodes.nearest(rec["x_s"], 10)
            nearest_word = None
            for eid, _cos in candidates:
                other = self.episodes.get(eid)
                if other is not None and other["word"]:
                    nearest_word = other["word"]
                    break
            if nearest_word is None:
                return dead_end(item["key"], "no_route")
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

        return dead_end(str(item.get("key")), "unknown_kind")

    def _maybe_think(self, row: Dict[str, object]) -> None:
        """PREREG §11.1 step 3: every THINK.every canvases. THINK's own gene clause is not on master at
        the time this was written (`"THINK" in self.genome.declared` is therefore never true today for
        any genome this worktree can parse) — RAISED, not worked around; the step is fully wired against
        the given interface names and exercised directly by the test (bypassing the gate) against every
        piece that does not need genome.curiosity/genome.think."""
        if "THINK" not in self.genome.declared:
            return
        every = int(self.genome.declared["THINK"]["every"])
        if every <= 0 or self._canvas_index % every != 0:
            return
        pool = self._think_pool()
        item = self._think_choose(pool)
        self.think_counters["thinks"] += 1
        if item is None:
            self._write_journal(row["at"], {"seq": row["seq"], "think": {"item": None, "kind": None, "outcome": "empty_pool", "parked": False}})
            return
        result = self._think_work(item)
        self._write_journal(row["at"], {
            "seq": row["seq"],
            "think": {"item": item.get("key"), "kind": item.get("kind"), "outcome": result.get("outcome"), "parked": bool(result.get("parked"))},
        })

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
        tmp_base = state_dir / "organism_tmp"
        self.org.save(tmp_base)
        os.replace(str(tmp_base) + ".npz", str(state_dir / "organism.npz"))
        os.replace(str(tmp_base) + ".json", str(state_dir / "organism.json"))

        ledgers = build_ledgers(self.org, self.moment_word)
        predictor_last_winner = None
        if self.predictor is not None and self.predictor._last_winner is not None:
            predictor_last_winner = self.predictor._last_winner.tolist()      # A9: PREDICT's state (its last winner) lives in the mind and is saved in the snapshot (PREREG §11.1 step 1)
        ledger = {
            "last_seq": self.last_seq,
            "moment_word": {str(k): v for k, v in self.moment_word.items()},
            "moments": self.org.t,
            "ear_pending": dict(self.pending),
            "sight": {str(k): sorted(v) for k, v in ledgers["sight"].items()},
            "words": {str(k): sorted(v) for k, v in ledgers["words"].items()},
            "predictor_last_winner": predictor_last_winner,
        }
        ledger_tmp = state_dir / "ledger_tmp.json"
        ledger_tmp.write_text(json.dumps(ledger))
        os.replace(str(ledger_tmp), str(state_dir / "ledger.json"))

        if self.episodes is not None:      # A9: FAST's episodes are saved with the snapshot (Episodes.save is already atomic: tmp + os.replace internally)
            self.episodes.save(state_dir / "episodes.npz")

        self._last_snapshot_moments = self.org.t
        self.snapshot_count += 1

    def close(self) -> None:
        self.snapshot()

    @classmethod
    def resume(cls, genome_path: Path, run_root: Path, blind: FrozenSet[str] = frozenset()) -> Tuple["Mind", int]:
        """Load the latest snapshot (if any) and return (mind, last_seq). No snapshot -> a fresh mind, 0."""
        mind = cls(genome_path, run_root, blind=blind)
        state_dir = Path(run_root) / "state"
        npz, meta, ledger_path = state_dir / "organism.npz", state_dir / "organism.json", state_dir / "ledger.json"
        if npz.exists() and meta.exists() and ledger_path.exists():
            mind.org = Organism.load(state_dir / "organism", mind.genome)
            ledger = json.loads(ledger_path.read_text())
            mind.pending = dict(ledger.get("ear_pending", {}))
            mind.moment_word = {int(k): v for k, v in ledger.get("moment_word", {}).items()}
            mind._heard = {v for v in mind.moment_word.values() if v}     # PREREG §15: the heard-set, re-derived (never persisted separately)
            mind.last_seq = int(ledger.get("last_seq", 0))
            mind._last_snapshot_moments = mind.org.t

            # A9: `mind.predictor`/`mind.episodes` were built in __init__ against the PRE-load org/genome;
            # the predictor in particular closes over `org` by reference, so it must be rebuilt against
            # the LOADED org (a stale reference here would silently expect() off a dead, pre-resume
            # organism) -- caught by tracing the constructor, not by a test failure.
            if "PREDICT" in mind.genome.declared:
                mind.predictor = Predictor(mind.org)
                last_winner = ledger.get("predictor_last_winner")
                if last_winner is not None:
                    mind.predictor._last_winner = np.array(last_winner, dtype=np.float64)
            episodes_path = state_dir / "episodes.npz"
            if "FAST" in mind.genome.declared and episodes_path.exists():
                mind.episodes = Episodes.load(episodes_path)
            if "SLEEP" in mind.genome.declared:
                every = int(mind.genome.declared["SLEEP"]["every"])
                mind._last_sleep_at = (mind.org.t // every) * every if every > 0 else 0

            return mind, mind.last_seq
        return mind, 0
