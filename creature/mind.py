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
from genome.machinery import Genome, Organism, parse_genome
from genome.predict import Predictor
from genome.questions import build_ledgers
from genome.sleep import cycle as run_cycle, sleep as run_sleep
from genome.world import encode_word

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

        self.pending: Dict[str, str] = {}                 # ear-consumed, eye not yet arrived: moment -> word
        self.moment_word: Dict[int, str] = {}              # org.t (per GLANCE, before increment) -> word — build_ledgers' input
        self.last_seq: int = 0
        self.sight_only_skipped: int = 0
        self.journal_rows_written: int = 0
        self.snapshot_count: int = 0
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
            for x in g["feats"]:
                self.moment_word[self.org.t] = word          # keyed by the organism's OWN moment counter, one per glance
                S, T = self.org.moment(x, xw, lr_scale=lr_scale)
                if predict_on:
                    self.predictor.note_winners(S)
            ep_id = self.episodes.write(moment=t_at_f0, x_s=f0, x_w=xw, word=word, surprise=err) if fast_on else None
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

        self._maybe_sleep(row)

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
            cycled = run_cycle(self.org)
            if "TRAITS" in self.genome.declared and _TRAITS_AVAILABLE:
                Traits.learn(self.episodes)      # per the interface name given for wave 2; unexercised until genome/traits.py lands
            self._write_journal(row["at"], {
                "seq": row["seq"], "sleep": {**result, "cycle": cycled}, "hash": self.org.state_hash(),
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
