# edit: Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:13 +0400 — A4-LADDER-PREREG §2.2 task 6: the
# four seams the brief names. ANSWER's majority-of-glances gate lives in ONE place (genome/machinery.py:
# Organism.recall_many); every seam here is a proof that the gate composes correctly with a REAL consumer,
# not a re-test of the gate itself (tests/genome/test_answer_grade.py already covers that exhaustively).
"""tests/creature/test_a4l_answer_seams.py — ANSWER x the ask door, THINK's word work, QUESTION, SURPRISE/THRESH."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from creature.ask import render_what_is
from creature.mind import Mind
from creature.tape import Tape, read_tape
from genome import world
from genome.machinery import Organism, parse_genome

from tests.genome._toy import mini_genome, onehot

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME = ROOT / "genome" / "G4.genome"


def _majority_genome(unknown_below: float = 0.6):
    text = mini_genome().text + (f"THRESH cell own band history 30\n"
                                  f"ANSWER resembles under own-band; unknown below {unknown_below}; "
                                  "sure only when a majority of the glances light\n")
    return parse_genome(text)


def _minority_result(org: Organism):
    """2 of 5 glances lit (< floor(5/2)+1 == 3): the WOULD-BE answer becomes "minority", same shape every
    seam below drives against a real consumer."""
    lit_glance, dark = onehot(0, 64), onehot(50, 64)
    return org.recall_many("sight", [lit_glance, lit_glance, dark, dark, dark])


class TestAnswerXAskDoor(unittest.TestCase):
    """(1) ANSWER x the ask door: what-is on a "spiral"-shaped canvas (a minority abstention) renders the
    "resembles" sentence, NEVER a bare "-> dot"-style confident answer -- structurally guaranteed since a
    minority result always carries cell=None (render_what_is's bare-answer branch requires cell is not
    None), verified here on the real render_what_is()."""

    def test_minority_renders_resembles_never_a_bare_answer(self) -> None:
        org = Organism(_majority_genome(0.6))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)   # cell0 <-> word0 "dot"
        r = _minority_result(org)
        self.assertEqual(r["reason"], "minority")
        self.assertIsNone(r["cell"])
        s = render_what_is("spiral.png", r, org, {0: {"dot"}})
        self.assertIn("I don't know what it is, but it resembles dot", s)
        self.assertIn("(minority; cos", s)
        self.assertNotEqual(s, f"what-is spiral.png -> dot ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})")

    def test_undeclared_clause_is_unaffected(self) -> None:
        """The negative control: without the majority clause, the SAME 2-of-5 pattern still answers
        confidently ("dot"), never "resembles" -- the seam only exists once the clause is declared."""
        org = Organism(parse_genome(mini_genome().text + "ANSWER resembles under own-band; unknown below 0.6\n"))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        lit_glance, dark = onehot(0, 64), onehot(50, 64)
        r = org.recall_many("sight", [lit_glance, lit_glance, dark, dark, dark])
        self.assertEqual(r["reason"], "answer")
        s = render_what_is("x.png", r, org, {0: {"dot"}})
        self.assertTrue(s.startswith("what-is x.png -> dot ("), s)


class TestAnswerXSurpriseThresh(unittest.TestCase):
    """(4) ANSWER x SURPRISE/THRESH: a minority abstention NEVER pushes a cell's own band -- `_own_band_
    push` is called only from inside `moment()` (never from `recall`/`recall_many`, which `moment()` never
    calls -- confirmed by grep, machinery.py:1152 is the ONLY call site), so this holds by construction;
    proven here by asking `recall_many` repeatedly (including "minority" results) and checking the band
    and the whole organism's own hash never move."""

    def test_repeated_minority_asks_never_touch_the_own_band_or_the_hash(self) -> None:
        org = Organism(_majority_genome(0.6))
        xs0, xw0 = onehot(0, 64), onehot(0, 208)
        org.moment(xs0, xw0); org.moment(xs0, xw0)
        band_before = org.sight.own_band.copy(); n_before = org.sight.own_band_n.copy()
        h_before = org.state_hash()
        for _ in range(20):
            r = _minority_result(org)
            self.assertEqual(r["reason"], "minority")
        np.testing.assert_array_equal(org.sight.own_band, band_before)
        np.testing.assert_array_equal(org.sight.own_band_n, n_before)
        self.assertEqual(org.state_hash(), h_before)

    def test_moment_never_calls_recall_many(self) -> None:
        """The structural guarantee itself, by source inspection (#217's law: verify the artifact, not the
        sentence) -- moment()'s own body never names recall/recall_many, so a minority abstention (only
        ever produced by recall_many) cannot reach the own-band push no matter what a future edit does
        nearby, as long as this stays true."""
        import inspect
        src = inspect.getsource(Organism.moment)
        self.assertNotIn("recall_many(", src)
        self.assertNotIn("self.recall(", src)


class TestAnswerXThinkWordWork(unittest.TestCase):
    """(2) ANSWER x THINK's word work (creature/mind.py:1966 and its threaded twin, creature/think_thread.py
    :206 -- both call the SAME Organism.recall_many): a word whose last five EPISODES (repeated showings,
    `_recent_word_glances`'s own unit -- not GAZE's within-canvas glances) mostly resonate still forms its
    belief once the majority clause is declared, exactly as it does without the clause (test_wave2_belief_
    path.py's own working example, reproduced here with THRESH+the majority clause added -- nothing else
    about that genome touched)."""

    def test_belief_still_forms_when_the_majority_of_recent_showings_light(self) -> None:
        text = G4_GENOME.read_text() + ("THRESH cell own band history 30\n"
                                         "ANSWER resembles under own-band; unknown below 0.911; "
                                         "sure only when a majority of the glances light\n")
        genome_path = Path(tempfile.mkdtemp()) / "g4-plus-answer-majority.genome"
        genome_path.write_text(text)
        root = Path(tempfile.mkdtemp()) / "run"
        tape = Tape(root)
        things = ["circle", "square", "triangle"]

        def _png(rgb):
            import io
            from PIL import Image
            b = io.BytesIO(); Image.fromarray(rgb).save(b, format="PNG"); return b.getvalue()

        for i in range(150):
            t = things[i % 3]
            rgb, _truth = world.render_canvas(t, np.random.default_rng([4242, i]))
            tape.publish("ear", t.encode(), {"moment": f"m{i}", "source": "maker", "word": t}, "txt", at=f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z")
            tape.publish("eye", _png(rgb), {"moment": f"m{i}", "source": "maker"}, "png", at=f"2026-09-19T00:{i // 60:02d}:{i % 60:02d}.000Z")
        mind = Mind(genome_path, root)
        for row in read_tape(root):
            mind.consume(row)
        self.assertGreater(mind.think_counters["thinks"], 0)
        outcomes = [json.loads(l)["think"]["outcome"] for f in (root / "journal").glob("*.jsonl") for l in f.read_text().splitlines() if '"think"' in l]
        self.assertIn("belief", outcomes, f"no belief formed under the majority clause; outcomes: {outcomes}")
        beliefs = (root / "state" / "beliefs.jsonl")
        self.assertTrue(beliefs.exists() and len(beliefs.read_text().splitlines()) >= 1)
        # the majority clause is genuinely ACTIVE on this record, not a no-op: at least one minority
        # abstention actually fired somewhere in the run's think/exam road, or every recall_many call this
        # word-rich a tape drives happened to clear the bar -- either way, print it, never assert a specific
        # count (an early/short run's exact mix is not pre-registered).
        no_cell = sum(1 for o in outcomes if o == "no_cell_answers")
        print(f"[seam] think outcomes: {dict((o, outcomes.count(o)) for o in set(outcomes))}; no_cell_answers={no_cell}")


class TestAnswerXQuestion(unittest.TestCase):
    """(3) ANSWER x QUESTION: "a minority answer on a wordless sight writes the same what-is want a novel
    one would, or says in the report why not". Grepped exhaustively (creature/mind.py, creature/think_
    thread.py): the ONLY two "wordless sight" want-forming roads are (a) the per-canvas trigger at mind.py
    :1363-1387, which calls `Organism.recall` (ONE glance -- `majority` can never gate a single glance, so
    "minority" cannot arise there), and (b) THINK's "sight" pool-kind work (mind.py:2008-2042 / think_
    thread.py's own "sight" branch), which never calls recall/recall_many at all (it routes through
    `episodes.nearest`, a k-NN search, not ANSWER's own-band grading). So today there is NO consumer that
    can ever see reason=="minority" on a wordless sight -- this test proves the negative by construction
    (both call sites reachable only via the non-`recall_many` roads named above) rather than asserting a
    behaviour nothing on this tree can produce."""

    def test_no_wordless_sight_road_calls_recall_many(self) -> None:
        import inspect
        from creature import mind as mind_mod, think_thread as think_thread_mod
        # the eye-time trigger (a real 2nd-sighting-without-a-word check)
        src_mind = inspect.getsource(mind_mod)
        # isolate the two "sight"-kind regions by their own distinctive anchors rather than re-deriving line numbers
        self.assertIn('r = self.org.recall("sight", f0)', src_mind, "the eye-time wordless-sight trigger moved -- re-check this seam")
        self.assertIn("candidates = self.episodes.nearest(rec[\"x_s\"], 10)", src_mind, "THINK's sight-kind route moved -- re-check this seam")
        src_think_thread = inspect.getsource(think_thread_mod)
        self.assertIn("candidates = frozen.episodes.nearest(rec[\"x_s\"], 10)", src_think_thread)
        # A TRIPWIRE, not a law (Claude (Sonnet 5, A4 ladder builder ANSWER), 2026-09-23 12:16 +0400, advisor-
        # caught): counting call sites is brittle by nature -- a FUTURE builder adding a legitimate second
        # recall_many() consumer to either module breaks this assertion whether or not it touches a
        # wordless-sight road. That is the intended failure mode: it forces a human to re-read this seam's
        # own reasoning (§ above) rather than silently going stale, not a promise that the count itself is
        # meaningful in isolation.
        self.assertEqual(src_mind.count("self.org.recall_many("), 1, "a new recall_many call site appeared -- re-audit this seam (task 6)")
        self.assertEqual(src_think_thread.count(".recall_many("), 1, "a new recall_many call site appeared -- re-audit this seam (task 6)")


if __name__ == "__main__":
    unittest.main()
