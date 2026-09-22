# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:12 +0400 — ALPHA4-H task 3 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §3): creature/mind.py's own RAISED-clause fix -- a real "what-is <word>" want also writes
# `run/world/questions/q-<n>.json {"q":"what-is","word":...}` for the lexicon door, gated on 'DOOR_LEXICON'
# in declared so an undeclared gene (every OLDER life, life 3a included) changes nothing (the closed-tape
# regression's own requirement). Test-first, at the `_maybe_ask` level directly -- the trigger conditions
# that FORM a real want (PARK/PREDICT/a wordless-sight-seen-twice) are pre-existing, already-tested
# mechanisms; this file targets only the NEW plumbing.
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from creature.mind import Mind

G4_SKELETON = Path(__file__).resolve().parents[2] / "genome" / "G4-skeleton.genome"
QUESTION_LINE = "QUESTION from wants; forms what-is is which; to the world door"
DOOR_LEXICON_LINE = "DOOR     lexicon /data/alpha2-library/lexicon-enwiktionary-20260901.sqlite answers what-is by showing"


def _genome_with(tmp: Path, *extra_lines: str) -> Path:
    text = G4_SKELETON.read_text() + "\n" + "\n".join(extra_lines) + "\n"
    p = tmp / "g.genome"
    p.write_text(text)
    return p


class TestLexiconWantQueue(unittest.TestCase):
    def test_a_what_is_want_with_a_resolved_word_writes_the_lexicon_queue_file(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE, DOOR_LEXICON_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("test:zog", "what-is", ["somemoment123"], why_word="zog")

        ask_out = json.loads((root / "ask" / "out" / "q-0.json").read_text())
        self.assertEqual(ask_out["args"], ["somemoment123"])
        self.assertNotIn("word", ask_out, "the format C landed carries args, not a top-level word (this file's own RAISED finding)")

        lex_path = root / "world" / "questions" / "q-0.json"
        self.assertTrue(lex_path.exists(), "the lexicon door's own queue file must exist")
        lex = json.loads(lex_path.read_text())
        self.assertEqual(lex, {"q": "what-is", "word": "zog"})

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_undeclared_door_lexicon_writes_nothing_new_replay_safety(self) -> None:
        """W3-0's law, and the closed-tape regression's own requirement: life 3a never declares
        DOOR_LEXICON, so replaying its tape under this tree must write NOTHING under world/questions/."""
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE)   # QUESTION only, no DOOR_LEXICON
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("test:zog", "what-is", ["somemoment123"], why_word="zog")

        self.assertTrue((root / "ask" / "out" / "q-0.json").exists(), "the pre-existing behaviour is untouched")
        self.assertFalse((root / "world" / "questions").exists(), "no DOOR_LEXICON -> no new directory, no new file")

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_a_sight_only_want_with_no_why_word_is_never_queued_to_the_lexicon(self) -> None:
        """The OTHER `_maybe_ask` caller (a wordless sight seen twice, mind.py ~line 1078) has no
        why_word -- it is world_maker's/folder's "show me this picture again" domain, never a dictionary
        lookup; the lexicon queue must stay untouched even with DOOR_LEXICON declared."""
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE, DOOR_LEXICON_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("sight:7", "what-is", ["f0123456789ab"])   # why_word defaults to None

        self.assertTrue((root / "ask" / "out" / "q-0.json").exists())
        self.assertFalse((root / "world" / "questions").exists())

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_a_clash_want_form_is_is_never_queued_to_the_lexicon(self) -> None:
        """_maybe_ask_clash's own form is "is", not "what-is" -- a belief-clash question, not a
        definition lookup; must never reach the lexicon queue even though it carries a why_word."""
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE, DOOR_LEXICON_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("clash:zog:x", "is", ["somemoment123", "zog"], why_word="zog")

        self.assertTrue((root / "ask" / "out" / "q-0.json").exists())
        self.assertFalse((root / "world" / "questions").exists())

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_two_distinct_wants_get_two_distinct_correlated_filenames(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE, DOOR_LEXICON_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("test:zog", "what-is", ["m1"], why_word="zog")
        mind._maybe_ask("test:vex", "what-is", ["m2"], why_word="vex")

        self.assertEqual(json.loads((root / "world" / "questions" / "q-0.json").read_text())["word"], "zog")
        self.assertEqual(json.loads((root / "world" / "questions" / "q-1.json").read_text())["word"], "vex")
        # correlated with the SAME n as ask/out's own file (payload["seq"])
        self.assertEqual(json.loads((root / "ask" / "out" / "q-0.json").read_text())["seq"], 0)
        self.assertEqual(json.loads((root / "ask" / "out" / "q-1.json").read_text())["seq"], 1)

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)

    def test_asking_the_same_want_twice_never_double_writes(self) -> None:
        """`_maybe_ask`'s own dedupe (self._asked) fires before either write -- a second call with the
        SAME want string must produce no second file of either kind."""
        tmp = Path(tempfile.mkdtemp())
        genome_path = _genome_with(tmp, QUESTION_LINE, DOOR_LEXICON_LINE)
        root = Path(tempfile.mkdtemp())
        mind = Mind(genome_path, root)
        mind._cur_at = "2026-09-23T01:00:00.000Z"; mind._cur_seq = 1

        mind._maybe_ask("test:zog", "what-is", ["m1"], why_word="zog")
        mind._maybe_ask("test:zog", "what-is", ["m1-again"], why_word="zog")

        self.assertFalse((root / "ask" / "out" / "q-1.json").exists())
        self.assertFalse((root / "world" / "questions" / "q-1.json").exists())

        shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
