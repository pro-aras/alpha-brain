# edit: Claude (Fable 5.1, A42 builder B2), 2026-09-23 17:0x +0400 — A42-B2 PART 2 (ALPHA4-2-PREREG §2.5 "B2 birth-source ledger (LANG)";
# the orchestrator's P2-1 decision, 2026-09-23 16:4x): the THING-WORD attribution's «heard» half read FAST's ring, which wraps
# ≈ hour 11.6 of a 24 h life (A4L-LANG-REPORT §2 item 5) — after the wrap the oldest picture-born words leave the set although the
# creature still knows them. The fix keeps «heard»'s MEANING (a word heard while a PICTURE-source canvas was shown) and loses the
# ring: `Mind.picture_words`, an only-growing, first-heard-ordered ledger written the moment such a word is heard, persisted in the
# snapshot LEDGER (never an org.c key, never the births log — both hashed), read by `genome/chain.py:thing_words(rule="ledger")`.
# RED first (this file's own first run, before the code): `Mind` has no `picture_words`, `thing_words` refuses rule "ledger".
"""tests/creature/test_b2_picture_words.py — the birth-source ledger for LANG's thing-words, through the REAL consume() road.

The toy: a FAST ring of 200 episodes (the same A4L-LANG genome otherwise), 90 maker canvases of three things FIRST, then 220
shelf lines — so the ring WRAPS and every picture episode is evicted. The control (today's behaviour, unchanged by this build):
«heard» = literal ∩ heard_on_pictures(ring) loses all three things after the wrap. The claim: rule "ledger" = literal ∩ the
snapshot ledger's `picture_words` keeps them, and before the wrap the two read EXACTLY the same set (the ledger IS the ring's
meaning, written live)."""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import List, Sequence

import numpy as np
from PIL import Image

from creature.mind import Mind
from creature.senses import read_common
from creature.tape import Tape, read_tape
from genome import chain
from genome.questions import build_ledgers
from tests.creature import _chat_tape as T

ROOT = Path(__file__).resolve().parents[2]
FAST_CAP = 200
PER_THING = 30
N_LINES = 220
AT = T.AT


def _png(rgb: np.ndarray) -> bytes:
    b = io.BytesIO(); Image.fromarray(rgb, mode="RGB").save(b, format="PNG"); return b.getvalue()


def _small_ring_genome(root: Path) -> Path:
    """A4L-LANG.genome with ONE number changed: FAST episodes 20000 → 200 (the ring must wrap inside a test)."""
    text = T.LANG_GENOME.read_text()
    old = "FAST     episodes 20000 keys sight words surprise sound"
    assert old in text, "the LANG genome's FAST line moved — update this toy"
    text = text.replace(old, f"FAST     episodes {FAST_CAP} keys sight words surprise sound")
    p = root / "g.genome"; p.write_text(text)
    return p


def _publish_things(tape: Tape, things: Sequence[str], per_thing: int, seed: int = 20260923) -> int:
    k = 0
    for _i in range(per_thing):
        for t in things:
            rgb, _truth = T.world.render_canvas(t, np.random.default_rng([seed, k]))
            m = f"w0000i{k:06d}t{k:09d}"
            tape.publish("ear", t.encode(), {"moment": m, "source": "maker", "word": t}, "txt", at=AT)
            tape.publish("eye", _png(rgb), {"moment": m, "source": "maker"}, "png", at=AT)
            k += 1
    return k


def _publish_lines(tape: Tape, lines: List[List[str]]) -> None:
    for j, words in enumerate(lines):
        m = f"read{j:06d}"
        for w in words:
            tape.publish("ear", w.encode(), {"moment": m, "source": "shelf", "word": w}, "txt", at=AT)
        rgb = read_common.render_line(" ".join(words), 128, read_common.DEFAULT_FONT_PATH)
        tape.publish("eye", _png(rgb), {"moment": m, "source": "shelf", "text": " ".join(words)}, "png", at=AT)


def _consume(mind: Mind, root: Path, after_seq: int = 0) -> int:
    last = after_seq
    for row in read_tape(root):
        if row["seq"] > after_seq:
            mind.consume(row); last = row["seq"]
    return last


def _sets(mind: Mind) -> dict:
    Lw = build_ledgers(mind.org, mind.moment_word)["words"]
    kw = dict(per_canvas=mind._glances_per_canvas())
    return {
        "ledger": list(mind.picture_words),
        "ring": set(chain.heard_on_pictures(mind.episodes)),
        "births_ring": chain.birth_sources(mind.org.births, mind.episodes, kw["per_canvas"]),
        "births_ledger": dict(mind.birth_source),
        "literal": chain.thing_words(mind.org, Lw, mind.episodes, rule="literal", **kw),
        "literal_ledger": chain.literal_from_ledger(mind.org, Lw, mind.birth_source),
        "heard": chain.thing_words(mind.org, Lw, mind.episodes, rule="heard", **kw),
        "ledger_rule": chain.thing_words(mind.org, Lw, mind.episodes, rule="ledger", picture_words=mind.picture_words,
                                         birth_source=mind.birth_source, **kw),
        "n_written": int(mind.episodes.n_written), "cap": int(mind.episodes.cap),
    }


class TestPictureWordsLedger(unittest.TestCase):
    """One learned mind, read at two moments: A — after the 90 maker canvases (the ring holds them all); B — after 220 shelf
    lines more (the ring, cap 200, has evicted every picture episode)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp(prefix="b2-picture-words-"))
        cls.genome = _small_ring_genome(cls.root)
        tape = Tape(cls.root)
        _publish_things(tape, T.THINGS, PER_THING)
        cls.mind = Mind(cls.genome, cls.root)
        cls.seq_a = _consume(cls.mind, cls.root)
        cls.A = _sets(cls.mind)
        cls.lines = T.lines_varied(N_LINES)
        _publish_lines(tape, cls.lines)
        _consume(cls.mind, cls.root, after_seq=cls.seq_a)
        cls.B = _sets(cls.mind)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.mind.close()
        finally:
            shutil.rmtree(cls.root, ignore_errors=True)

    def test_the_toy_wraps_the_ring(self) -> None:
        self.assertEqual(self.A["cap"], FAST_CAP)
        self.assertLess(self.A["n_written"], FAST_CAP, "phase A must sit BEFORE the wrap")
        self.assertGreater(self.B["n_written"] - FAST_CAP, PER_THING * len(T.THINGS), "phase B must have evicted every picture episode")

    def test_before_the_wrap_the_ledgers_are_the_ring_exactly(self) -> None:
        """The agreement proof on the toy, both halves: the picture-words ledger written live == the set read from the ring,
        element for element; the birth-source ledger == chain.birth_sources(ring) for EVERY sight cell; so the literal twin
        and the ledger rule read exactly what the ring rules read."""
        self.assertEqual(set(self.A["ledger"]), self.A["ring"], (self.A["ledger"], self.A["ring"]))
        self.assertGreater(len(self.A["births_ledger"]), 0)
        self.assertEqual(self.A["births_ledger"], self.A["births_ring"])
        self.assertEqual(self.A["literal_ledger"], self.A["literal"])
        self.assertEqual(self.A["heard"], self.A["ledger_rule"])
        self.assertEqual(self.A["heard"], set(T.THINGS), "the three drawn things are the thing-words before the wrap")

    def test_after_the_wrap_the_ring_rules_lose_the_picture_words__the_control(self) -> None:
        """Today's behaviour, unchanged by this build: BOTH ring rules forget what the ring can no longer see — «heard»
        because no live episode is a picture any more, and even «literal» because chain.birth_sources reads a birth older
        than the oldest live episode as "?" (A42-B2-REPORT P2-1, the finding this ledger answers)."""
        self.assertEqual(self.B["ring"], set(), "the ring must have evicted every picture episode")
        self.assertEqual(self.B["heard"], set())
        self.assertEqual(self.B["literal"], set())
        self.assertTrue(all(v == "?" for k, v in self.B["births_ring"].items() if self.A["births_ledger"].get(k) == "maker"),
                        "every maker-born cell of phase A reads «?» from the wrapped ring")

    def test_after_the_wrap_the_ledger_rule_keeps_them(self) -> None:
        self.assertEqual(self.B["ledger_rule"], set(T.THINGS), self.B["ledger_rule"])
        self.assertTrue(set(T.THINGS) <= self.B["literal_ledger"], "the twin: the creature still KNOWS them — their word cells are MEET-wired to picture-born cells")
        self.assertEqual({k: v for k, v in self.B["births_ledger"].items() if k in self.A["births_ledger"]}, self.A["births_ledger"],
                         "the birth-source ledger only grows; a source once written never changes")

    def test_rule_ledger_refuses_without_its_ledgers(self) -> None:
        Lw = build_ledgers(self.mind.org, self.mind.moment_word)["words"]
        with self.assertRaises(ValueError):
            chain.thing_words(self.mind.org, Lw, self.mind.episodes, per_canvas=5, rule="ledger")
        with self.assertRaises(ValueError):
            chain.thing_words(self.mind.org, Lw, self.mind.episodes, per_canvas=5, rule="ledger", picture_words=[])

    def test_the_ledger_only_grows_in_first_heard_order_and_no_shelf_word_enters(self) -> None:
        self.assertEqual(self.A["ledger"], self.B["ledger"], "220 shelf lines added nothing: the shelf is not a picture source")
        self.assertEqual(self.B["ledger"], list(T.THINGS), "first-heard order, each word once")
        shelf_words = {w for line in self.lines for w in line}
        self.assertFalse(shelf_words & set(self.B["ledger"]))

    def test_snapshot_persists_it_and_resume_restores_it(self) -> None:
        self.mind.snapshot()
        ledger = json.loads((self.root / "state" / "ledger.json").read_text())
        self.assertEqual(ledger["picture_words"], list(T.THINGS))
        self.assertEqual({int(k): v for k, v in ledger["birth_source"].items()}, self.mind.birth_source)
        h = self.mind.org.state_hash()
        twin, _seq = Mind.resume(self.genome, self.root)
        try:
            self.assertEqual(list(twin.picture_words), list(T.THINGS))
            self.assertEqual(twin.birth_source, self.mind.birth_source)
            self.assertEqual(twin.org.state_hash(), h, "the ledger keys are LEDGER keys: the organism's hash never sees them")
            self.assertEqual(_sets(twin)["ledger_rule"], set(T.THINGS))
        finally:
            twin.close()

    def test_a_snapshot_from_before_this_ledger_resumes_empty_never_back_filled(self) -> None:
        """RAISED in the report: an old snapshot has no key; rule "ledger" then reads literal ∩ {} = {} — the ring is never used to
        back-fill it (that would make the proof circular, A42-B2-REPORT P2-1)."""
        self.mind.snapshot()
        p = self.root / "state" / "ledger.json"
        ledger = json.loads(p.read_text()); ledger.pop("picture_words"); ledger.pop("birth_source"); p.write_text(json.dumps(ledger))
        twin, _seq = Mind.resume(self.genome, self.root)
        try:
            self.assertEqual(list(twin.picture_words), [])
            self.assertEqual(twin.birth_source, {})
            self.assertEqual(_sets(twin)["ledger_rule"], set())
            self.assertEqual(_sets(twin)["literal_ledger"], set())
        finally:
            twin.close()

    def test_the_constant_still_reads_heard_and_the_new_rule_is_named(self) -> None:
        """The one-constant switch to "ledger" is the orchestrator's at the LANG landing (RAISED), not this build's."""
        self.assertEqual(chain.THING_WORD_RULE, "heard")
        self.assertIn("ledger", chain.THING_WORD_RULES)
        with self.assertRaises(ValueError):
            chain.thing_words(self.mind.org, {}, self.mind.episodes, per_canvas=5, rule="no-such-rule")


class TestBlindEarWritesNothing(unittest.TestCase):
    """--blind ear (A4L-VOICE's twin): the organism hears no word, the ring's words_in_instant is empty on every episode — the
    ledger must agree with the ring here too (written from the SAME post-blind words), so it stays empty."""

    def test_blind_ear(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="b2-blind-ear-"))
        try:
            genome = _small_ring_genome(root)
            tape = Tape(root); _publish_things(tape, T.THINGS, 6)
            mind = Mind(genome, root, blind=frozenset({"ear"}))
            _consume(mind, root)
            try:
                self.assertEqual(list(mind.picture_words), [])
                self.assertEqual(chain.heard_on_pictures(mind.episodes), set())
                # the birth-source half still agrees with the ring: the blind twin's canvases are still maker canvases
                self.assertGreater(len(mind.birth_source), 0)
                self.assertEqual(mind.birth_source, chain.birth_sources(mind.org.births, mind.episodes, mind._glances_per_canvas()))
            finally:
                mind.close()
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
