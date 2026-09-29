# edit: Claude (Fable 5.1, the seat), 2026-09-29 12:58 +0400 — PREREG-WORD-ROAD §1 / §2 / §6, test-first (red on day-0929 f855582: no gene HEAR).
"""tests/creature/test_hear_mind.py — the gene HEAR in the MIND: the organism meets every word of an utterance.

One fixture tape of the scene world (60 training scenes + a sitting), lived by four minds: OFF (the lean twin genome as it
stands), ON (the same text plus the HEAR line), ON again (determinism), and ON stopped and resumed at a cut."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

import creature.mind as MM
from brain.scene import world as W
from genome.machinery import GenomeError, parse_genome
from genome.questions import word_cells
from tests.creature import _scene_tape as S

ROOT = Path(__file__).resolve().parents[2]
TWIN = (ROOT / "genome" / "brain" / "BRAIN-LEAN-TWIN.genome").read_text()
HEAR_LINE = "HEAR     every word; thing last; arrival last"
N_TRAIN = 60


def genome_text(hear: bool, extra: str = "") -> str:
    text = re.sub(r"^WORLD    scene .*$", S.scene_line(train=N_TRAIN), TWIN, count=1, flags=re.M)
    assert text != TWIN
    return text + ("\n" + HEAR_LINE + "\n" if hear else "\n") + extra


class _Lives(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="hear-mind-"))
        cls.tape_root = cls.tmp / "tape-root"
        cls.tape_root.mkdir()
        cls.info = S.build(cls.tape_root, n_train=N_TRAIN)
        cls.rows = S.rows(cls.tape_root)
        cls.n = 0
        cls.off, cls.off_root = cls.live(False)
        cls.on, cls.on_root = cls.live(True)
        # the tape's own words per training moment, in order (the truth of what was SAID)
        cls.said: Dict[str, List[str]] = {}
        for r in cls.rows:
            if r["sense"] == "ear":
                cls.said.setdefault(r["meta"]["moment"], []).append(r["meta"]["word"])

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def live(cls, hear: bool, rows=None, blind=frozenset(), extra: str = ""):
        cls.n += 1
        root = S.link_root(cls.tape_root, cls.tmp / f"run{cls.n}" / "r")
        gp = root.parent / "g.genome"
        gp.write_text(genome_text(hear, extra))
        m = MM.Mind(gp, root, blind=blind)
        try:
            for row in (cls.rows if rows is None else rows):
                m.consume(row)
        finally:
            m.close()
        return m, root


class TheLine(unittest.TestCase):
    def test_parses_to_its_three_values(self) -> None:
        d = parse_genome(genome_text(True)).declared
        self.assertEqual(d["HEAR"], {"words": "every", "thing": "last", "arrival": "last"})
        self.assertNotIn("HEAR", parse_genome(genome_text(False)).declared)

    def test_any_other_word_refuses_by_name(self) -> None:
        for bad in ("HEAR     every word; thing first; arrival last", "HEAR     every word; thing last; arrival every",
                    "HEAR     last word; thing last; arrival last", "HEAR     every word"):
            with self.subTest(line=bad):
                with self.assertRaises(GenomeError) as e:
                    parse_genome(genome_text(False) + bad + "\n")
                self.assertIn("HEAR", str(e.exception))

    def test_the_one_difference(self) -> None:
        a, b = parse_genome(genome_text(False)).declared, parse_genome(genome_text(True)).declared
        self.assertEqual({k: v for k, v in b.items() if k != "HEAR"}, a)


class TheOrganismMeetsEveryWord(_Lives):
    def test_the_tape_holds_words_that_are_never_last(self) -> None:
        # the presence count beside every zero below: this tape says size and colour words, and never says one last
        never_last = {w for ws in self.said.values() for w in ws[:-1]} - {ws[-1] for ws in self.said.values()}
        self.assertGreaterEqual(len(never_last), 5, never_last)
        self.assertTrue(never_last <= set(W.SIZE_NAMES) | set(W.COLOUR_NAMES), never_last)

    def test_off_the_cells_never_met_a_word_that_is_not_last(self) -> None:
        Lw = self.off.ledgers()["words"]
        last = {ws[-1] for ws in self.said.values()}
        for w in self.info["said"]:
            with self.subTest(word=w):
                self.assertEqual(bool(word_cells(self.off.org, Lw, w)), w in last)

    def test_on_every_word_said_has_a_cell_named_by_itself(self) -> None:
        Lw = self.on.ledgers()["words"]
        for w in self.info["said"]:
            with self.subTest(word=w):
                self.assertTrue(word_cells(self.on.org, Lw, w), f"no cell is named {w!r}")
        names = [next(iter(s)) for s in Lw.values() if len(s) == 1]
        self.assertEqual(sorted(set(names)), sorted(self.info["said"]), "and no cell carries a name the tape never said")
        self.assertEqual(self.on.org.hear_shared_cell, 0)

    def test_on_a_sight_cell_is_wired_to_a_word_that_was_never_last(self) -> None:
        # MEET wires from STAGE 2 on (the genome's own stage2_start, in moments); a canvas is org.t / N_TRAIN moments
        Lw = self.on.ledgers()["words"]
        per = self.on.org.t // N_TRAIN
        self.assertEqual(per * N_TRAIN, self.on.org.t)
        first = -(-int(self.on.org.g.stage2_start) // per)                       # the first canvas whose moments all wire
        late = [ws for k, (m, ws) in enumerate(self.said.items()) if k >= first]
        self.assertGreater(len(late), 10)
        last = {ws[-1] for ws in self.said.values()}
        said_late = {w for ws in late for w in ws[:-1]} - last
        self.assertGreaterEqual(len(said_late), 3, said_late)
        wired = {w for w in said_late for c in word_cells(self.on.org, Lw, w) if self.on.org.mask[:, c].any()}
        self.assertEqual(wired, said_late)
        off_cols = [c for w in said_late for c in word_cells(self.off.org, self.off.ledgers()["words"], w)]
        self.assertEqual(off_cols, [], "OFF: those words have no cell at all")

    def test_the_clock_is_the_same(self) -> None:
        self.assertEqual(self.on.org.t, self.off.org.t)

    def test_thing_last_and_arrival_last(self) -> None:
        self.assertEqual(self.on.moment_word, self.off.moment_word)
        self.assertEqual(self.on.org.arrivals, self.off.org.arrivals)
        self.assertEqual(self.on._heard, self.off._heard)

    def test_the_journal_carries_the_words_under_the_line_only(self) -> None:
        jon = [r for r in S.journal(self.on_root) if r.get("moment") in self.said and "word" in r]
        joff = [r for r in S.journal(self.off_root) if r.get("moment") in self.said and "word" in r]
        self.assertEqual(len(jon), N_TRAIN)
        self.assertEqual(len(joff), N_TRAIN)
        for r in jon:
            self.assertEqual(r["words"], list(dict.fromkeys(self.said[r["moment"]])))
            self.assertEqual(r["word"], self.said[r["moment"]][-1])
        self.assertEqual(sum(1 for r in joff if "words" in r), 0)
        self.assertEqual([r["word"] for r in jon], [r["word"] for r in joff])

    def test_a_phrase_with_a_colour_or_size_word_can_be_asked(self) -> None:
        def answers(root):
            return [r for r in S.journal(root) if r.get("kind") == "answer" and r.get("form") == "point"]
        a_on, a_off = answers(self.on_root), answers(self.off_root)
        self.assertEqual(len(a_on), len(a_off))
        self.assertGreater(len(a_on), 0)
        said = set(self.info["said"])
        off = [w for r in a_off for w in (r["answer"]["raw"].get("unheard") or [])]
        on = [w for r in a_on for w in (r["answer"]["raw"].get("unheard") or [])]
        self.assertGreater(len([w for w in off if w in said]), 0, "this fixture must hold a phrase the OFF cells cannot be asked")
        self.assertEqual([w for w in on if w in said], [], "ON: no word the tape said is «unheard»")
        self.assertEqual(sorted(set(on)), sorted(set(off) - said), "a word the tape never said stays unheard in both")

    def test_the_same_life_twice_is_the_same_journal(self) -> None:
        _m, root = self.live(True)
        self.assertEqual(S.journal_bytes(root), S.journal_bytes(self.on_root))

    def test_resumed_at_a_cut_after_a_colour_word_was_heard(self) -> None:
        never_last = {w for ws in self.said.values() for w in ws[:-1]} - {ws[-1] for ws in self.said.values()}
        k = next(i for i, r in enumerate(self.rows) if r["sense"] == "ear" and r["meta"]["word"] in never_last)
        cut = next(i for i in range(k, len(self.rows)) if self.rows[i]["sense"] == "eye") + 3     # a few rows past that canvas
        first, rr = self.live(True, rows=self.rows[:cut + 1])
        m2, last = MM.Mind.resume(rr.parent / "g.genome", rr)
        try:
            self.assertEqual(last, self.rows[cut]["seq"])
            for row in self.rows:
                if row["seq"] > last:
                    m2.consume(row)
        finally:
            m2.close()
        self.assertEqual(m2.org.state_hash(), self.on.org.state_hash())
        self.assertEqual({c: sorted(s) for c, s in m2.ledgers()["words"].items()},
                         {c: sorted(s) for c, s in self.on.ledgers()["words"].items()})
        mine = [json.dumps(r, sort_keys=True) for r in S.journal(rr) if "hash" in r]
        whole = [json.dumps(r, sort_keys=True) for r in S.journal(self.on_root) if "hash" in r]
        self.assertEqual(mine, whole)


class Refusals(_Lives):
    def test_refused_beside_a_gene_of_stage_2_by_name(self) -> None:
        with self.assertRaises(GenomeError) as e:
            self.live(True, rows=[], extra="SURPRISE floor 0.05 predicted mind-cell\n")
        self.assertIn("SURPRISE", str(e.exception))
        self.assertIn("HEAR stage 2", str(e.exception))

    def test_the_same_gene_without_the_line_starts(self) -> None:
        m, _root = self.live(False, rows=[], extra="SURPRISE floor 0.05 predicted mind-cell\n")
        self.assertIsNotNone(m)

    def test_blind_ear_is_refused_beside_the_line(self) -> None:
        with self.assertRaises(GenomeError) as e:
            self.live(True, rows=[], blind=frozenset({"ear"}))
        self.assertIn("HEAR stage 2", str(e.exception))

    def test_a_word_the_ear_refuses_that_is_not_last_never_stops_the_mind(self) -> None:
        rows = [json.loads(json.dumps(r)) for r in self.rows]
        k = next(i for i, r in enumerate(rows) if r["sense"] == "ear" and len(self.said[r["meta"]["moment"]]) >= 2
                 and r["meta"]["word"] == self.said[r["meta"]["moment"]][0])
        moment, good = rows[k]["meta"]["moment"], self.said[rows[k]["meta"]["moment"]][1:]
        rows[k]["meta"]["word"] = "toolongaword"
        m, root = self.live(True, rows=rows[:k + 1 + len(good) + 1])
        row = [r for r in S.journal(root) if r.get("moment") == moment and "word" in r]
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0]["words"], list(dict.fromkeys(good)))
        self.assertEqual(row[0]["words_refused"], ["toolongaword"])
        self.assertEqual(m.hear_words_refused, 1)


if __name__ == "__main__":
    unittest.main()
