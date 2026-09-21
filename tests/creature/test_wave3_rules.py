# edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — D2 (docs/briefs/W3-BUILDER-D.md; W3-2,
# docs/G4-WAVE3-CLAUSES.md): INDUCE / DEDUCE wired — a rule is a PREDICTION, filed through FILE's four
# fields, scored at its due canvas. The toy genome is `G4-wave2-test.genome` (PREDICT/FAST already on
# it) PLUS the FILE/CURIOSITY/PARK/BELIEF/THINK/INDUCE/DEDUCE lines lifted VERBATIM from `genome/G4.genome`
# (never `genome/G4.genome` itself — the brief's own words; that file is Claude's, edited only at a life
# boundary), built as TEXT in a tempdir here (never a new .genome file under tests/creature/ — this
# builder's file-ownership is "tests/genome/ + NEW tests/creature/test_wave3_*.py", so no other new file
# is added to that directory).
"""test_wave3_rules.py — the maker's world for 600 canvases: INDUCE/DEDUCE filing and scoring, the
shuffled-word null, the zog plant's natural dead end, and the FILE/BELIEF gates (W3-0b) each on their
own small fixture."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image

from creature.mind import Mind, _THINK_LAWS_AVAILABLE, _CURIOSITY_AVAILABLE
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import parse_genome

ROOT = Path(__file__).resolve().parents[2]
BASE_GENOME_TEXT = (ROOT / "tests" / "creature" / "G4-wave2-test.genome").read_text()

# lifted verbatim from genome/G4.genome (its own currently-#OFF INDUCE/DEDUCE lines, un-commented, and
# its FILE/CURIOSITY/PARK/BELIEF/THINK lines) — never that file itself.
EXTRA_GENES = """\
FILE     claim route decider due                   # the falsifiability law: four fields or refused by name
CURIOSITY interests 50 operators recombine generalize specialize bridge   # chooses what to THINK about and which door to open, never whether to perceive
PARK     after 3 identical dead-ends reopen on new-sense                  # D39
BELIEF   clash opens never overwrites               # Alpha 2's scope law
THINK    every 10 canvases                        # §11.1 step 3: the pool → CURIOSITY chooses → work → PARK/FILE
INDUCE   rule from 5 episodes no counter      # a rule is a prediction
DEDUCE   one step                             # two beliefs → a prediction
"""


def _full_genome_text() -> str:
    return BASE_GENOME_TEXT.rstrip("\n") + "\n" + EXTRA_GENES


def _png_bytes(rgb: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _publish_canvas(tape: Tape, word: str, rgb: np.ndarray, moment: str, i: int) -> None:
    at = f"2026-09-21T{(i // 3600) % 24:02d}:{(i // 60) % 60:02d}:{i % 60:02d}.000Z"
    tape.publish("ear", word.encode("utf-8"), {"moment": moment, "source": "maker", "word": word}, "txt", at=at)
    tape.publish("eye", _png_bytes(rgb), {"moment": moment, "source": "maker"}, "png", at=at)


def _build_tape(root: Path, seed: int = 20260921) -> None:
    """600 canvases: 300 of THINGS_11 (shuffled), then the plant `zog` 5 times running (world.THING_PLANT
    — world.py's own made-up hourglass thing, PREREG §2.8's plant, never world_maker's schedule — its
    5 showings land at canvas 300-304, well past STAGE 2's meet boundary at moment 200 ≈ canvas 50, so
    the wiring the rule needs is already live), then 295 more of THINGS_11 — zog is never shown again."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    i = 0

    def _feed_things(n: int) -> None:
        nonlocal i
        rows = world.stream_canvas(world.THINGS_11, (n // len(world.THINGS_11)) + 1, rng)[:n]
        for t, rgb, _truth in rows:
            _publish_canvas(tape, t, rgb, f"m{i:05d}", i)
            i += 1

    _feed_things(300)
    assert world.THING_PLANT == "zog"
    for _ in range(5):
        rgb, _truth = world.render_canvas(world.THING_PLANT, rng)
        _publish_canvas(tape, world.THING_PLANT, rgb, f"m{i:05d}", i)
        i += 1
    _feed_things(295)
    assert i == 600, i


def _shuffle_ear_words(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """tools/verdict_g4.py's OWN T-shuffle, replicated exactly (the verdict reader's own twin, per the
    brief): the ear's words permuted across canvases by `default_rng(5)`; the sight stream (eye rows)
    untouched."""
    rows = list(rows)
    ears = [idx for idx, r in enumerate(rows) if r["sense"] == "ear"]
    words = [rows[idx]["meta"]["word"] for idx in ears]
    perm = np.random.default_rng(5).permutation(len(words))
    for idx, j in zip(ears, perm):
        rows[idx] = dict(rows[idx])
        rows[idx]["meta"] = dict(rows[idx]["meta"])
        rows[idx]["meta"]["word"] = words[int(j)]
    return rows


def _read_predictions(root: Path) -> List[Dict[str, object]]:
    path = root / "state" / "predictions.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def _rule_accuracy_by_claim(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    """Every SCORED row (outcome is not None — a plain filed-not-yet-scored row carries outcome: None,
    predict.py's file() law) grouped by its claim text; {"n", "correct", "acc"} per claim."""
    by_claim: Dict[str, List[bool]] = {}
    for r in rows:
        if r.get("outcome") is None:
            continue
        claim = r.get("row", {}).get("claim", "?")
        by_claim.setdefault(claim, []).append(bool(r["outcome"]))
    return {c: {"n": len(v), "correct": sum(v), "acc": sum(v) / len(v)} for c, v in by_claim.items()}


@unittest.skipUnless(_THINK_LAWS_AVAILABLE and _CURIOSITY_AVAILABLE, "genome.think/genome.curiosity not on master")
class TestGenomeParses(unittest.TestCase):
    def test_full_genome_declares_induce_and_deduce(self) -> None:
        g = parse_genome(_full_genome_text())
        for gene in ("FILE", "CURIOSITY", "PARK", "BELIEF", "THINK", "INDUCE", "DEDUCE", "PREDICT", "FAST"):
            self.assertIn(gene, g.declared, gene)


@unittest.skipUnless(_THINK_LAWS_AVAILABLE and _CURIOSITY_AVAILABLE, "genome.think/genome.curiosity not on master")
class TestRulesFiledAndScored(unittest.TestCase):
    """The maker's world, 600 canvases (real arm) and its word-shuffled twin (null arm) — built ONCE in
    setUpClass (a real ~2,400-moment life at ~9s/2,600-moments-class cost, per gate_g4's own timing) and
    shared read-only by every test method below (never mutated after setUpClass)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp())
        cls.real_root = cls.tmp / "real"
        _build_tape(cls.real_root)
        cls.rows = list(read_tape(cls.real_root))
        cls.genome_path = cls.tmp / "wave3-rules-test.genome"
        cls.genome_path.write_text(_full_genome_text())

        cls.real_mind = Mind(cls.genome_path, cls.real_root)
        for r in cls.rows:
            cls.real_mind.consume(r)
        cls.real_predictions = _read_predictions(cls.real_root)
        cls.real_acc = _rule_accuracy_by_claim(cls.real_predictions)

        # the null arm: the SAME tape, ear words shuffled — a FRESH root, FRESH Mind; the payload dir is
        # SHARED (symlinked, the pictures do not change) so no PNG is re-encoded a second time.
        cls.null_root = cls.tmp / "null"
        (cls.null_root / "tape").mkdir(parents=True)
        import os
        os.symlink((cls.real_root / "tape" / "payload").resolve(), cls.null_root / "tape" / "payload")
        cls.null_rows = _shuffle_ear_words(cls.rows)
        cls.null_mind = Mind(cls.genome_path, cls.null_root)
        for r in cls.null_rows:
            cls.null_mind.consume(r)
        cls.null_predictions = _read_predictions(cls.null_root)
        cls.null_acc = _rule_accuracy_by_claim(cls.null_predictions)

    def test_numbers_printed(self) -> None:
        """PREREG/brief: 'print every per-thing number' (B13's own rule, applied here) — unconditional,
        run once, both bars graded separately below."""
        c = self.real_mind.think_counters
        print(f"[wave3-rules] REAL predictions_filed={c['predictions_filed']} predictions_scored={c['predictions_scored']}")
        for claim, d in self.real_acc.items():
            print(f"[wave3-rules] REAL rule accuracy: {claim!r} n={d['n']} correct={d['correct']} acc={d['acc']:.3f}")

    # edit: Claude (Fable 5.1), 2026-09-21 15:38 +0400 — expectedFailure REMOVED: with INDUCE clustering the word's own cells and the kind-fair
    # think chooser (PREREG §18 addendum 2) the toy's literal bar is met (the suite read it as an unexpected success 15:3x).
    def test_at_least_5_filed_real_arm(self) -> None:
        """The toy's literal bar. Measured on this 600-canvas shuffled maker-world stream (seed
        20260921): predictions_filed=3, not >=5 — RAISED, expectedFailure, never forced. The mechanism
        (module docstring's honest finding): the pool's 'rule' items compete against 'word'/'sight'/'due'
        items at CURIOSITY's plain highest-weight-ties-by-rng choice; a rule that scores FAIL is
        HALVED (specialize, this task's own wiring — the FIRST place interests.update() is ever called
        in this codebase, see the report) while 'word'/'sight' items are NEVER updated (a pre-existing
        gap, not this task's to fix) and sit at their birth weight of 1.0 forever — so a rule that fails
        once becomes systematically LESS likely to be re-chosen than a word item that dead-ends just as
        often but is never penalized. A blocked-per-word stream (tried, not shipped — see the report) did
        WORSE (0 filed), so this is not a stream-ordering artifact to chase; it is a real property of the
        wiring as built. This is exactly the class of finding PREREG asks for: 'a FAIL is a result'."""
        c = self.real_mind.think_counters
        self.assertGreaterEqual(c["predictions_filed"], 5, c)

    def test_at_least_3_scored_real_arm(self) -> None:
        """The toy's second literal bar. Measured: predictions_scored=3 -- clears >=3 exactly."""
        c = self.real_mind.think_counters
        self.assertGreaterEqual(c["predictions_scored"], 3, c)

    def test_null_arm_filed_and_scored_reported(self) -> None:
        """The null's OWN filed/scored counts, printed unconditionally (PREREG's own caution, applied
        here: 'induce() may find zero agreeing episodes -- 0 of 0 scored is not at chance')."""
        c = self.null_mind.think_counters
        print(f"[wave3-rules] NULL predictions_filed={c['predictions_filed']} predictions_scored={c['predictions_scored']}")
        for claim, d in self.null_acc.items():
            print(f"[wave3-rules] NULL rule accuracy: {claim!r} n={d['n']} correct={d['correct']} acc={d['acc']:.3f}")
        # printed only -- see test_null_accuracy_at_chance_or_no_rules_found for the graded reading

    def test_null_accuracy_at_chance_or_no_rules_found(self) -> None:
        """PREREG's own words: 'a rule engine that scores well on shuffled words is reading the sight,
        not the meeting.' Graded as: EITHER the null files/scores nothing scorable (the shuffled tape
        breaks the >= 5-agreeing-episode / shared-belief-cell preconditions before a rule can even be
        induced — itself the finding, per the module docstring), OR every scored rule's accuracy sits at
        or below chance + noise (1/11 + 0.15, matching B13/B8's own noise margins on a small toy)."""
        scored_total = sum(d["n"] for d in self.null_acc.values())
        if scored_total == 0:
            print("[wave3-rules] NULL: 0 rules ever scored under the word-shuffle -- the meeting itself "
                  "is what the shuffle destroys (a finding, not a bug); nothing to grade against chance")
            return
        chance_bar = 1.0 / 11.0 + 0.15
        worst = max(d["acc"] for d in self.null_acc.values())
        print(f"[wave3-rules] NULL worst rule accuracy={worst:.3f} vs chance+noise bar={chance_bar:.3f}")
        self.assertLessEqual(worst, chance_bar, self.null_acc)

    def test_zog_stays_pending_never_scored_never_parked_never_crashes(self) -> None:
        """D2: 'the plant zog shown 5 times and never again is the natural unscorable rule -- its item
        stays pending; report what happens to it after 600 canvases (it should sit in
        _filed_predictions unscored, not crash, not PARK -- PARK is for 3 FAILS, not for never-due).'"""
        zog_entries = [e for e in self.real_mind._filed_predictions if e["target_word"] == "zog"]
        print(f"[wave3-rules] zog pending entries at canvas 600: {len(zog_entries)}")
        if not zog_entries:
            print("[wave3-rules] zog: INDUCE never found a k=5-agreeing rule for it on this run "
                  "(reported, not forced -- see the report for the per-seed reading)")
            return
        self.assertGreaterEqual(len(zog_entries), 1)
        zog_scored = [r for r in self.real_predictions
                      if r.get("outcome") is not None and "zog" in str(r.get("row", {}).get("claim", ""))]
        self.assertEqual(zog_scored, [], "zog's rule must never have been scored -- it is never shown again")
        self.assertFalse(self.real_mind.park.is_parked("induce:zog"),
                          "zog must never be parked -- PARK is for 3 FAILS, not for a rule that is never due")


@unittest.skipUnless(_THINK_LAWS_AVAILABLE and _CURIOSITY_AVAILABLE, "genome.think/genome.curiosity not on master")
class TestNeverDueRuleDeterministic(unittest.TestCase):
    """The 600-canvas toy's own randomness may or may not happen to induce a rule for a word that is
    never shown again (TestRulesFiledAndScored's zog test reports whichever it was, honestly). This is
    the SAME mechanism verified deterministically, independent of that: file a rule by hand for a word
    that will never recur, feed more canvases of OTHER words, and confirm it sits in _filed_predictions
    forever -- not scored (there is nothing to score it against), not parked (PARK is for 3 FAILS, never
    for 'not yet due'), no crash."""

    def test_a_never_recurring_target_word_stays_pending_forever(self) -> None:
        root = Path(tempfile.mkdtemp())
        genome_path = root / "g.genome"
        genome_path.write_text(_full_genome_text())
        tape_root = root / "run"
        rng = np.random.default_rng(3)
        tape = Tape(tape_root)
        for i in range(60):
            t = world.THINGS_11[i % len(world.THINGS_11)]
            rgb, _truth = world.render_canvas(t, rng)
            _publish_canvas(tape, t, rgb, f"m{i:05d}", i)
        mind = Mind(genome_path, tape_root)
        for r in read_tape(tape_root):
            mind.consume(r)
        before_filed = mind.think_counters["predictions_filed"]
        # file a rule by hand for a word this tape will NEVER show again ("ghost"), exactly the shape
        # _think_rule/_file_rule build for a real INDUCE row (predict.file()'s own accepted shape).
        from genome.predict import file as predict_file
        ghost_row = predict_file(
            claim='"ghost" resonates cluster [0]', route="recall(sight) on the next episode with word 'ghost'",
            decider="recall(sight) in cluster [0]", due="moment 999999",
        )
        ghost_row["word"] = "ghost"; ghost_row["cluster"] = [0]
        mind._induce_pending.add("ghost")
        mind._file_rule(ghost_row, want="induce:ghost", op="induce")
        self.assertEqual(mind.think_counters["predictions_filed"], before_filed + 1)
        pending = [e for e in mind._filed_predictions if e["target_word"] == "ghost"]
        self.assertEqual(len(pending), 1)

        # 40 more canvases, none of them "ghost"
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — these two publishes used to omit
        # `at=`, so Tape.now_iso() read the wall clock (non-deterministic, non-replayable — the one row in
        # this suite that broke the tape's own reproducibility law, advisor-flagged). Fixed with the SAME
        # deterministic `at` formula _publish_canvas() (above) uses for every other call site in this
        # file, still consuming the two rows tape.publish() returns directly (as the original did) rather
        # than re-reading the whole tape.
        for i in range(60, 100):
            t = world.THINGS_11[i % len(world.THINGS_11)]
            rgb, _truth = world.render_canvas(t, rng)
            at = f"2026-09-21T{(i // 3600) % 24:02d}:{(i // 60) % 60:02d}:{i % 60:02d}.000Z"
            row_ear = tape.publish("ear", t.encode(), {"moment": f"m{i:05d}", "source": "maker", "word": t}, "txt", at=at)
            row_eye = tape.publish("eye", _png_bytes(rgb), {"moment": f"m{i:05d}", "source": "maker"}, "png", at=at)
            mind.consume(row_ear); mind.consume(row_eye)

        still_pending = [e for e in mind._filed_predictions if e["target_word"] == "ghost"]
        self.assertEqual(len(still_pending), 1, "the never-recurring rule must still be pending, unscored")
        ghost_scored = [r for r in _read_predictions(tape_root)
                        if r.get("outcome") is not None and "ghost" in str(r.get("row", {}).get("claim", ""))]
        self.assertEqual(ghost_scored, [], "a rule for a word never shown again must never be scored")
        self.assertFalse(mind.park.is_parked("induce:ghost"), "never-due is not a FAIL -- must never be parked")


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestFileGeneGating(unittest.TestCase):
    """W3-0b (docs/G4-WAVE3-CLAUSES.md): predict.file() is called only when 'FILE' in declared -- a
    genome with INDUCE but WITHOUT FILE must never journal a row (predictions_filed stays 0)."""

    def test_induce_without_file_files_nothing(self) -> None:
        text = (BASE_GENOME_TEXT.rstrip("\n") + "\n" +
                "CURIOSITY interests 50 operators recombine generalize specialize bridge\n"
                "PARK     after 3 identical dead-ends reopen on new-sense\n"
                "THINK    every 10 canvases\n"
                "INDUCE   rule from 5 episodes no counter\n")
        # no FILE line at all
        g = parse_genome(text)
        self.assertIn("INDUCE", g.declared); self.assertNotIn("FILE", g.declared)
        root = Path(tempfile.mkdtemp())
        genome_path = root / "no-file.genome"
        genome_path.write_text(text)
        tape_root = root / "run"
        _build_small_tape(tape_root)
        mind = Mind(genome_path, tape_root)
        for r in read_tape(tape_root):
            mind.consume(r)
        self.assertEqual(mind.think_counters["predictions_filed"], 0, mind.think_counters)
        preds_path = tape_root / "state" / "predictions.jsonl"
        self.assertFalse(preds_path.exists() and preds_path.read_text().strip(),
                          "no FILE declared -- predictions.jsonl must stay empty/absent")


@unittest.skipUnless(_THINK_LAWS_AVAILABLE, "genome.think not on master")
class TestBeliefGeneGating(unittest.TestCase):
    """W3-0b: think_laws.believe() is called only when 'BELIEF' in declared -- a word item without
    BELIEF dead-ends 'no_belief_gene', and beliefs.jsonl is never written."""

    def test_word_item_without_belief_dead_ends_by_name(self) -> None:
        text = (BASE_GENOME_TEXT.rstrip("\n") + "\n" +
                "THINK    every 5 canvases\n")
        # no BELIEF, no CURIOSITY, no PARK -- the plainest possible fixture
        g = parse_genome(text)
        self.assertNotIn("BELIEF", g.declared)
        root = Path(tempfile.mkdtemp())
        genome_path = root / "no-belief.genome"
        genome_path.write_text(text)
        tape_root = root / "run"
        _build_word_forming_tape(tape_root)
        mind = Mind(genome_path, tape_root)
        for r in read_tape(tape_root):
            mind.consume(r)
        pool = mind._think_pool()
        word_items = [it for it in pool if it["kind"] == "word"]
        found_no_belief_gene = False
        for item in word_items:
            result = mind._think_work(item)
            if result["outcome"] == "no_belief_gene":
                found_no_belief_gene = True
            self.assertNotEqual(result["outcome"], "belief", "BELIEF undeclared -- no word item may ever form a belief")
        self.assertTrue(word_items, "fixture must produce at least one word pool item to test the gate on")
        self.assertTrue(found_no_belief_gene, "at least one word item's recall_many must succeed, reaching the BELIEF gate")
        beliefs_path = tape_root / "state" / "beliefs.jsonl"
        self.assertFalse(beliefs_path.exists() and beliefs_path.read_text().strip(),
                          "no BELIEF declared -- beliefs.jsonl must stay empty/absent")


def _build_small_tape(root: Path, seed: int = 1) -> None:
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    rows = world.stream_canvas(world.THINGS_11, 6, rng)  # 66 canvases -- well past STAGE 2, < 5 episodes/word by itself
    for i, (t, rgb, _truth) in enumerate(rows):
        _publish_canvas(tape, t, rgb, f"m{i:05d}", i)


def _build_word_forming_tape(root: Path, seed: int = 2) -> None:
    """Reuses test_wave2_belief_path.py's own proven fixture shape (150 canvases, 3 things) -- the exact
    scale that file already demonstrated reliably reaches recall_many's answered branch."""
    tape = Tape(root)
    rng = np.random.default_rng(seed)
    things = ["circle", "square", "triangle"]
    for i in range(150):
        t = things[i % 3]
        rgb, _truth = world.render_canvas(t, np.random.default_rng([seed, i]))
        at = f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z"
        tape.publish("ear", t.encode(), {"moment": f"m{i}", "source": "maker", "word": t}, "txt", at=at)
        tape.publish("eye", _png_bytes(rgb), {"moment": f"m{i}", "source": "maker"}, "png", at=at)


if __name__ == "__main__":
    unittest.main()
