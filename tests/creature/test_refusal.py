# edit: Claude (Sonnet 5, W3 builder A), 2026-09-20 22:45 +0400 — W3-0 (docs/G4-WAVE3-CLAUSES.md; docs/G4-PREREG.md
# §14): THE GENERIC REFUSAL. Four toys: (a) the life's own genome starts; (b) a genome declaring a gene
# with no interpreter (INDUCE) refuses naming it; (c) a planted, made-up key refuses naming it (the
# instrument's negative control — SOLUTIONS #91); (d) every gene creature/genes.py's RUNS registry names
# is a gene the parser itself recognises (pins the registry to the parser, never the other way round).
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from creature import genes as genes_module
from creature.mind import Mind
from genome.machinery import GenomeError, parse_genome

ROOT = Path(__file__).resolve().parents[2]
G4_GENOME = ROOT / "genome" / "G4.genome"
G4_SKELETON = ROOT / "genome" / "G4-skeleton.genome"
G1_GENOME = ROOT / "genome" / "G1.genome"


def _tmp() -> Path:
    return Path(tempfile.mkdtemp())


class TestPositiveControls(unittest.TestCase):
    """(a): the life's own genome must start under the new refusal law — every gene G4.genome actively
    declares (18 of them: ARRIVAL, ASK, BELIEF, BODY, CRASH, CURIOSITY, CYCLE, EXAM, FAST, FILE, FROZEN,
    HEART, PARK, PREDICT, SLEEP, TAPE, THINK, WORLD) must have a RUNS entry, or the 24 h life this genome
    is running from master could never restart."""

    def test_g4_genome_starts(self) -> None:
        mind = Mind(G4_GENOME, _tmp())
        self.assertGreater(len(mind.genome.declared), 0, "G4.genome must actually declare new genes for this to be a real test")

    def test_g4_genome_declares_exactly_the_expected_set(self) -> None:
        """Not load-bearing for the refusal itself, but pins the fixture: if G4.genome's active gene set
        ever changes, this test names the diff instead of a silent pass/fail elsewhere."""
        genome = parse_genome(G4_GENOME.read_text())
        expected = {"ARRIVAL", "ASK", "BELIEF", "BODY", "CRASH", "CURIOSITY", "CYCLE", "DEDUCE", "EXAM", "FAST",
                    "FILE", "FROZEN", "HEART", "INDUCE", "PARK", "PREDICT", "SLEEP", "TAPE", "THINK", "WORLD"}   # edit: Claude (Fable 5.1), 2026-09-21 15:38 +0400 — INDUCE/DEDUCE ON since life 3 (PREREG §18)
        self.assertEqual(set(genome.declared), expected)

    def test_skeleton_and_g1_genomes_start(self) -> None:
        """The walking skeleton and G1 declare NO new (G4 §3) genes at all -- unwired([]) is always [],
        so these two must be completely untouched by this clause (the G4-8 pin's own precondition)."""
        for path in (G4_SKELETON, G1_GENOME):
            with self.subTest(genome=path.name):
                mind = Mind(path, _tmp())
                self.assertEqual(mind.genome.declared, {})


class TestInduceNowWired(unittest.TestCase):
    """(b), FLIPPED (W3-2, docs/G4-WAVE3-CLAUSES.md, edit: Claude (Sonnet 5, W3 builder D), 2026-09-21
    11:40 +0400): INDUCE now has a real interpreter -- creature/mind.py's `_think_pool`/`_think_work`
    call `think_laws.induce()` for words with enough episodes and file the result (genes.py's RUNS entry,
    this task) -- a genome declaring it must START, not refuse. DEDUCE is wired the same way, tested for
    symmetry below. The refusal's own negative-control role for 'a gene with no interpreter' moves to
    SENTENCE (still OFF, still uninterpreted, docs/G4-WAVE3-CLAUSES.md's own order)."""

    def test_induce_line_starts(self) -> None:
        root = _tmp()
        text = G4_GENOME.read_text() + "INDUCE   rule from 5 episodes no counter\n"
        genome_path = root / "G4-plus-induce.genome"
        genome_path.write_text(text)
        mind = Mind(genome_path, root / "run")   # must not raise
        self.assertIn("INDUCE", mind.genome.declared)

    def test_deduce_line_starts(self) -> None:
        root = _tmp()
        text = G4_GENOME.read_text() + "DEDUCE   one step\n"
        genome_path = root / "G4-plus-deduce.genome"
        genome_path.write_text(text)
        mind = Mind(genome_path, root / "run")   # must not raise
        self.assertIn("DEDUCE", mind.genome.declared)

    def test_induce_hash_off_line_alone_does_not_refuse(self) -> None:
        """The SAME clause, commented (#OFF), as G4.genome already carries it today -- confirms the toy's
        premise (INDUCE really is off in the life's own genome) rather than assuming it."""
        genome = parse_genome(G4_GENOME.read_text())
        self.assertIn("INDUCE", genome.declared, "G4.genome's INDUCE line is ON since life 3 (PREREG §18) -- must parse")   # edit: Claude (Fable 5.1), 2026-09-21 15:38 +0400 — the premise flipped at 13:14 when INDUCE went ON; the pin had not moved


class TestSentenceNowWired(unittest.TestCase):
    """(b), FLIPPED a second time (L-11, docs/briefs/LIFE-C-QUESTION-SENTENCE.md task 3; mirrors
    TestInduceNowWired above exactly): SENTENCE now has a real interpreter -- creature/mind.py's
    `_think_pool`/`_think_work` call `genome.sentence.find_frames()` for episodes carrying >= 2
    words_in_instant and file the result -- a genome declaring the NEW line must START, not refuse. The
    refusal's own negative-control role for 'a gene with no interpreter' moves to TRAITS (still
    uninterpreted, PREREG §12/§14's own finding, genes.py:TRAITS = None)."""

    def test_sentence_line_starts(self) -> None:
        root = _tmp()
        text = G4_GENOME.read_text() + "SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token\n"
        genome_path = root / "G4-plus-sentence.genome"
        genome_path.write_text(text)
        mind = Mind(genome_path, root / "run")   # must not raise
        self.assertIn("SENTENCE", mind.genome.declared)

    def test_sentence_old_line_no_longer_parses(self) -> None:
        """The old literal was REPLACED, not extended (L-11): it must now refuse as an unrecognised value,
        not silently keep parsing to the old declared shape."""
        with self.assertRaises(GenomeError):
            parse_genome("SEED 1\nSENTENCE two-word frames is near under-judge\n")

    def test_sentence_hash_off_line_alone_does_not_refuse(self) -> None:
        genome = parse_genome(G4_GENOME.read_text())
        self.assertNotIn("SENTENCE", genome.declared, "G4.genome's own SENTENCE line is #OFF -- must not parse")


class TestTraitsRefusal(unittest.TestCase):
    """(b)'s new example (SENTENCE's old role, above, is now a positive control): TRAITS parses
    (machinery.py's clause exists) but has NO interpreter anywhere (genes.py: RUNS["mind"]["TRAITS"] =
    None) -- refuses, naming TRAITS and nothing else (mirrors the old INDUCE/SENTENCE toy exactly)."""

    def test_traits_line_refuses_naming_traits(self) -> None:
        root = _tmp()
        text = G4_GENOME.read_text() + "TRAITS   contrast head 32 lr 0.01 at sleep\n"
        genome_path = root / "G4-plus-traits.genome"
        genome_path.write_text(text)
        with self.assertRaises(GenomeError) as ctx:
            Mind(genome_path, root / "run")
        msg = str(ctx.exception)
        self.assertIn("TRAITS", msg)
        # every gene G4.genome ALREADY declares must still be considered wired -- only the new one is named
        for other in ("BODY", "TAPE", "HEART", "CRASH", "FAST", "SLEEP", "PREDICT", "FILE", "CURIOSITY",
                      "PARK", "BELIEF", "THINK", "EXAM", "FROZEN", "ARRIVAL", "CYCLE", "WORLD", "ASK"):
            self.assertNotIn(other, msg, f"{other} was already wired on G4.genome; it must not appear in this refusal")

    def test_traits_hash_off_line_alone_does_not_refuse(self) -> None:
        genome = parse_genome(G4_GENOME.read_text())
        self.assertNotIn("TRAITS", genome.declared, "G4.genome's own TRAITS line is #OFF -- must not parse")


class TestPlantedControl(unittest.TestCase):
    """(c): the instrument's own negative control (SOLUTIONS #91) -- a gene the PARSER never produces
    (a typo, a future gene not yet in RUNS) must still refuse. Exercised through the real Mind.__init__
    refusal path (not just the bare unwired() function) by wrapping parse_genome so the returned Genome's
    `declared` carries one extra, made-up key -- the same technique test_wave2_think.py uses to exercise a
    gated step whose own parser clause is not yet on master."""

    def test_planted_key_refuses_naming_it(self) -> None:
        import creature.mind as mind_module
        real_parse_genome = mind_module.parse_genome

        def _parse_with_plant(text: str):
            g = real_parse_genome(text)
            g.declared["PLANTED"] = {"nothing": "runs-this"}
            return g

        root = _tmp()
        with mock.patch.object(mind_module, "parse_genome", side_effect=_parse_with_plant):
            with self.assertRaises(GenomeError) as ctx:
                Mind(G4_SKELETON, root)
        self.assertIn("PLANTED", str(ctx.exception))

    def test_bare_unwired_function_agrees(self) -> None:
        """The same control, one layer down: unwired() alone (no Mind, no genome file) must name a
        completely unknown key and leave a real wired gene out."""
        self.assertEqual(genes_module.unwired({"PLANTED": {}, "FAST": {"episodes": 1}}), ["PLANTED"])


class TestRegistryPinnedToParser(unittest.TestCase):
    """(d): every gene named in creature/genes.py's RUNS registry (wired or explicitly refused, like
    TRAITS) is a gene the parser itself recognises -- a one-line clause for each, fed alone (so the ONLY
    possible GenomeError besides "unknown gene" is the unrelated "genome lacks [...] required" error that
    firing at the end of parse_genome proves the gene's own line was read just fine)."""

    SAMPLE_LINE = {
        "CYCLE": "CYCLE    grow to 0.9 nmax then consolidate",
        # edit: Claude (Sonnet 5, ALPHA4 builder G), 2026-09-23 03:05 +0400 — ALPHA4-G.md task 1: one row,
        # matching the genes.py RUNS entry added by this task (docs/ALPHA4-PREREG.md §2/§3).
        "GROW": "GROW     unbounded",
        # edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 12:13 +0400 — A4L-COST: one row, matching the genes.py RUNS entry added by
        # docs/briefs/A4L-COST.md (the per-row witness made sparse, A4-LADDER-PREREG §2.1).
        "HASH": "HASH     sparse; dense at snapshot",
        "EXAM": "EXAM     every 2000 canvases",
        "BODY": "BODY     service creature threads eye ear door mind voice",
        "TAPE": "TAPE     run/tape",
        "HEART": "HEART    every 10 s",
        "CRASH": "CRASH    sense restart journal; mind page",
        "WORLD": "WORLD    drawn every 5 s arrivals every 6 h; folder world/; web 6 per hour by curiosity",
        # edit: Claude (Sonnet 5, G5 builder L), 2026-09-21 21:5x +0400 — G5-L brief: WORLD's second shape,
        # matching the new genes.py RUNS entry for WORLD_GAME.
        "WORLD_GAME": ("WORLD    game babyai-gotolocal every 5 s; seed 20260922; "
                        "frames pov 7x7 tile 32; consequence: his act chooses the next frame"),
        "ASK": "ASK      what-is show is which next why",
        "FAST": "FAST     episodes 100 keys sight words surprise",
        "PREDICT": "PREDICT  next glance; error scales delta 0.5..2.0; ranks replay; grades act",
        "PARK": "PARK     after 3 identical dead-ends reopen on new-sense",
        "CURIOSITY": "CURIOSITY interests 50 operators recombine generalize specialize bridge",
        "ARRIVAL": "ARRIVAL  never-heard word",
        "SLEEP": "SLEEP    every 40 moments replay 5 by surprise",
        "THINK": "THINK    every 10 canvases",
        "FROZEN": "FROZEN   after 50 cells",
        "FILE": "FILE     claim route decider due",
        "BELIEF": "BELIEF   clash opens never overwrites",
        "TRAITS": "TRAITS   contrast head 32 lr 0.01 at sleep",
        # edit: Claude (Sonnet 5, W3 builder D), 2026-09-21 11:40 +0400 — W3-2: two rows, matching the two
        # genes.py RUNS entries added by this task.
        "INDUCE": "INDUCE   rule from 5 episodes no counter",
        "DEDUCE": "DEDUCE   one step",
        # edit: Claude (Sonnet 5, G5 builder K), 2026-09-21 21:27 +0400 — G5-K (docs/briefs/G5-K-ACTS-OUTCOME-SIT-BODY.md):
        # four rows, matching the four genes.py RUNS entries added by this task. Caught by this test's own
        # gate (test_sample_line_set_is_exactly_the_registry) at first full-suite run — RUNS was updated
        # without this fixture, exactly the omission this class exists to catch.
        "ACT": "ACT      glance open ask",
        "OUTCOME": "OUTCOME  act to episode; error grades it; ranks replay",
        "SIT": "SIT      exam every 2000 canvases; the score returns as a sense",
        "SENSE_BODY": "SENSE    body every 60 s fields moments births arrivals budget_left refused restarts mind_ms rss",
        # edit: Claude (Sonnet 5, G5 builder I), 2026-09-21 21:19 +0400 — G-EYE-1/G-MIND-1: two rows, matching the two
        # genes.py RUNS entries added by this task (docs/briefs/G5-I-SEAM-DELIVER-MOMENT.md).
        "DELIVER": "DELIVER  where fixation when instant act glance",
        "MOMENT": "MOMENT   keys sight words surprise where when act source",
        # edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 21:35 +0400 — G-EYE-2/BIND: one row, matching
        # the genes.py RUNS entry added by this task (docs/briefs/G5-J-BIND-COLOUR-RETINA.md).
        "BIND": "BIND     glances per canvas",
        # edit: Claude (Sonnet 5, LIFE builder B), 2026-09-22 19:0x +0400 — L-4: one row, matching the
        # genes.py RUNS entry added by this task (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-4).
        "SURPRISE": "SURPRISE floor 0.05 predicted mind-cell",
        # edit: Claude (Sonnet 5, LIFE builder A), 2026-09-22 18:43 +0400 — L-6/L-9 (docs/briefs/LIFE-A-ANSWER-SELF.md):
        # three rows, matching the three genes.py RUNS entries added by this task.
        "THRESH": "THRESH   cell own band history 30",
        "ANSWER": "ANSWER   resembles under own-band; unknown below 0.911",
        "SELF": "SELF     from body; beliefs about itself; skip thinks when backlog > 200",
        # edit: Claude (Sonnet 5, LIFE builder C), 2026-09-22 18:3x +0400 — L-10/L-11: three rows, matching
        # the three genes.py RUNS entries added by this task (docs/briefs/LIFE-C-QUESTION-SENTENCE.md).
        "SENTENCE": "SENTENCE two-word frames from co-occurring words; judged by the eye; never next-token",
        "QUESTION": "QUESTION from wants; forms what-is is which; to the world door",
        # edit: Kimi K3 (kimi-code, builder lane kimi-w1), 2026-10-04 18:32 +0400 — PREREG-W1-MOUTH-VOICES-BRAIN §2 (the registry and the
        # fixtures): the MOUTH row gains the new spelling (the optional clause «and the brain's phrase per canvas»); the old spelling
        # stays pinned by tests/creature/test_question_sentence_mouth.py + test_voice_mind.py (every misspelling refused by name there).
        "MOUTH": "MOUTH    say one frame per think and the brain's phrase per canvas; journaled",
        # edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:42 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md:
        # three rows, matching the three genes.py RUNS entries added by this task.
        "HANDS": "HANDS    jail alpha3/hands/jail_run shelf world/programs cpu 10 mem 512 wall 20",
        "SENSE_TOUCH": "SENSE    touch from hands: exit rate stalls retries bytes",
        "SENSE_SMELL": "SENSE    smell kind size folder age",
        # edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:3x +0400 — ALPHA4-H (docs/briefs/ALPHA4-H.md
        # tasks 2/3): two rows, matching the two genes.py RUNS entries added by this task. Caught by this
        # test's own gate (test_sample_line_set_is_exactly_the_registry) on the full suite, exactly the
        # omission this class exists to catch (G5-K's own comment above, again).
        "SENSE_READ": "SENSE    read shelf /data/alpha3-library/SHELF.sqlite curriculum /data/alpha3-library/CURRICULUM.md every 5 s words 8 canvas 128",
        "DOOR_LEXICON": "DOOR     lexicon /data/alpha2-library/lexicon-enwiktionary-20260901.sqlite answers what-is by showing",
        # edit: Claude (Sonnet 5, ALPHA4 builder J), 2026-09-23 00:52 +0400 — ALPHA4-PREREG.md §6: one row,
        # matching the genes.py RUNS entry added by this task (EVOLVE).
        "EVOLVE": "EVOLVE   every 6 h; mutate 1 gene within bounds; judge on the last 2 h; adopt at sleep under the regression bar",
        # edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:34 +0400 — ALPHA4-PREREG.md §3/§4: three
        # rows, matching the three genes.py RUNS entries added by this task (DOOR_WEB, SENSE_GRADE,
        # STAGE_READY). Caught by this test's own gate on the first full-suite run after landing — exactly
        # the omission this class exists to catch (its own comment above, now proven on a fourth builder).
        "DOOR_WEB": "DOOR     web wikipedia-summary wiktionary; floor 2 s; 60 per hour; opens at STAGE 4; hold-file world/HOLD",
        "SENSE_GRADE": "SENSE    grade from ask/graded",
        "STAGE_READY": "STAGE    4 world by READY",
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 12:15 +0400 — A4L-LANG: one row, matching the genes.py RUNS entry
        # (CHAT). Caught by this test's own gate on the landing's first full-suite run — the omission this class exists to catch.
        "CHAT": "CHAT     door chat/in chat/out; chain of frames + one pivot slot; links adjacent 5; pivot 10 distinct 20 instants; at most 6 words; a question never teaches",
        # edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 12:14 +0400 — A4L-VOICE (docs/briefs/A4L-VOICE.md): three rows, matching the three
        # genes.py RUNS entries added by this task. Caught by this test's own gate on the landing's full suite (the fifth builder it caught).
        "AREA_SOUND": "AREA     sound  from cochlea cos>=0.975",
        "MEET_SIGHT_SOUND": "MEET     sight  sound",
        "MEET_SOUND_WORDS": "MEET     sound  words",
        # edit: Claude (Opus 5.5, A4 ladder builder EXPLORE), 2026-09-23 12:20 +0400 — docs/A4-LADDER-PREREG.md §2.5: one row, matching the
        # genes.py RUNS entry the rung adds (ACT_VALUE — the second ACT line). Caught by this class on the first landing run.
        "ACT_VALUE": "ACT      value reward 10; optimism 1",
        # edit: Claude (Opus 5.5, BRAIN builder C), 2026-09-28 20:26 +0400 — BRAIN-IN-BODY: one row, matching the genes.py RUNS entry (BRAIN, the mind layer).
        "BRAIN": ("BRAIN    word-map lr 0.01; reader eps 0.3; none 0.95; conformal 0.90; young 3; "
                  "calibrate at 250 500 1000 2000 5000 10000 and before a sitting; replay none; hears scene"),
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 13:23 +0400 — PREREG-WORD-ROAD §1: one row, matching the genes.py RUNS entry (HEAR, the
        # mind layer). Caught by this class's own gate on the first full creature suite after the gene landed (2dbc1d8: 2 failures).
        "HEAR": "HEAR     every word; thing last; arrival last",
        # edit: Claude (Fable 5.1, the seat), 2026-09-29 16:28 +0400 — PREREG-BRAIN-DRIVES §2.1: one row, matching the genes.py RUNS entry (DRIVE).
        "DRIVE": "DRIVE    brain turn before hearing; says 1; asks 1",
        # edit: Claude (Fable 5.1, swarm integrator), 2026-10-03 11:26 +0400 — PREREG-INNER-1 §2: one row, matching the genes.py RUNS entry (INNER, the
        # mind layer). Caught by this class's own gate on the first targeted run after the registry row (#246 (8), the trap it named).
        "INNER": "INNER    every body row when idle; walk lift; inhibit 2; restart 5",
        # edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:56 +0400 — BRAIN-IN-BODY §5 (docs/brain/body/
        # INTERFACE-BRAIN-ORGAN.md): one row, matching the genes.py RUNS entry added by this task (WORLD_SCENE).
        # Caught by this class's own gate on the first full-suite run after landing — the omission this class
        # exists to catch (its own comment above, now proven on a sixth builder).
        "WORLD_SCENE": ("WORLD    scene seed 20261101; train 10000; sitting fresh s1b1; feed max backlog 8; "
                        "utterance true"),
    }

    def test_every_runs_gene_parses(self) -> None:
        all_genes = sorted({gene for layer in genes_module.RUNS.values() for gene in layer})
        for gene in all_genes:
            with self.subTest(gene=gene):
                self.assertIn(gene, self.SAMPLE_LINE, f"add a sample clause for {gene!r} to this test")
                try:
                    parse_genome(self.SAMPLE_LINE[gene] + "\n")
                except GenomeError as e:
                    self.assertNotIn(f"unknown gene {gene!r}", str(e), f"{gene} not recognised by the parser: {e}")

    def test_sample_line_set_is_exactly_the_registry(self) -> None:
        """No stray fixture left behind if a gene is ever removed from RUNS."""
        all_genes = {gene for layer in genes_module.RUNS.values() for gene in layer}
        self.assertEqual(set(self.SAMPLE_LINE), all_genes)


if __name__ == "__main__":
    unittest.main()
