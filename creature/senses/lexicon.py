# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:13 +0400 — ALPHA4-H task 3 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §3 DOOR lexicon): the offline dictionary door -- "nobody answers him: no seat road, no
# prompt, only the shelf and the dictionary" (the brief's own words, echoing his 09-16 18:46 rule: the world
# answers by SHOWING).
"""creature/senses/lexicon.py — watches `root/world/questions/q-*.json` (creature/mind.py:_maybe_ask's own
write, gated on 'DOOR_LEXICON' in declared -- see that method's comment for the RAISED clause this answers:
the pre-existing `ask/out/q-<n>.json` carries a TAPE MOMENT, never a word, so this door needed its OWN
word-keyed queue). For `{"q": "what-is", "word": <w>}`: looks up `senses` (word, lang='en') ordered by
(sense_no, id) -- sense_no repeats ACROSS pos (verified against the real lexicon: "cat" carries Verb
sense_no=1, Noun sense_no=1, Adjective sense_no=1 -- id is the only globally monotonic column, so it is the
deterministic tie-break, not an assumption) -- takes the FIRST gloss that yields at least one ear-ready word
(read_common.words_of); a gloss that cleans to nothing (e.g. "the"'s Pronoun sense, gloss ".") is skipped
for the next sense_no, not treated as found. Publishes through the SAME show-and-hear road every other sense
here uses: moment `lexXXXXXXXX` (deterministic from word + the question's own id, so two distinct wants for
the same word -- e.g. "predict:sight:zog" and "rule:zog" both resolving why_word="zog" -- each get their own
fresh moment, world_maker.py's own "a fresh total, never a stale one" discipline for a repeat showing), the
gloss's words as ear rows (source "lexicon"), the rendered gloss as the eye row (source "lexicon", DEFAULT
font -- read_common.DEFAULT_FONT_PATH, the same font a life is ever shown, never the mark's held-out one).

Marks the question `<qid>.answered.json` (a gloss was shown) or `<qid>.unanswered.json` (no dictionary entry,
or every sense's gloss cleaned to nothing) -- **the seam contract for builder I's web door: it watches this
SAME directory for `*.unanswered.json` and may then try the internet door for the same word.** One lookup
per scan (folder.py's own "at most one new picture per scan" pacing law), then `stop_event.wait(period)`.

A pure SENSE (G4-1's writer sweep): never touches state/journal/memory, never imports Organism/machinery.
No cursor file is needed -- the rename IS the completion marker (world_maker.py's own door has none either,
for the same reason: the glob's own filter already skips a `.answered.json`/`.unanswered.json` file).
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from . import read_common

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists. `--lexicon` stays an explicit override for tests regardless of this constant.
LEXICON_DOOR_GATED = True


def _lookup_gloss(sqlite_path: str, word: str, max_words: int, letters: int) -> Tuple[List[str], str]:
    """The first sense (word, lang='en'), ordered by (sense_no, id), whose gloss cleans to at least one
    ear-ready word. `([], "")` when the word has no English sense at all, or every sense's gloss is empty
    or cleans to nothing (read_common.words_of drops pure punctuation/digit tokens whole)."""
    con = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        cur.execute("SELECT gloss FROM senses WHERE word = ? AND lang = 'en' ORDER BY sense_no, id", (word,))
        rows = cur.fetchall()
    finally:
        con.close()
    for (gloss,) in rows:
        if not gloss:
            continue
        words = read_common.words_of(gloss, max_words, letters)
        if words:
            return words, " ".join(words)
    return [], ""


def _moment_id(word: str, qid: str) -> str:
    return "lex" + hashlib.sha256(f"{word}:{qid}".encode("utf-8")).hexdigest()[:8]


def _answer_one(publish: Callable, sqlite_path: str, q_dir: Path, canvas: int, words: int, letters: int,
                 font_path: str) -> bool:
    """Answers the FIRST pending `world/questions/q-*.json` (excluding already-marked ones); returns True
    iff it processed one (the caller's own "did anything happen this scan" pacing flag)."""
    if not q_dir.exists():
        return False
    for qpath in sorted(p for p in q_dir.glob("q-*.json")
                        if not (p.name.endswith(".answered.json") or p.name.endswith(".unanswered.json"))):
        try:
            req = json.loads(qpath.read_text())
        except (json.JSONDecodeError, OSError):
            continue   # a row read mid-write -- retried next scan, never fatal (world_maker.py's own law)
        if req.get("q") != "what-is" or not req.get("word"):
            continue
        word = str(req["word"])
        qid = qpath.stem
        gloss_words, gloss_text = _lookup_gloss(sqlite_path, word, words, letters)
        if gloss_words:
            moment = _moment_id(word, qid)
            for w in gloss_words:
                publish("ear", w.encode("utf-8"), {"moment": moment, "source": "lexicon", "word": w}, "txt")
            rgb = read_common.render_line(gloss_text, canvas, font_path)
            publish("eye", read_common.png_bytes(rgb),
                    {"moment": moment, "source": "lexicon", "answers": word, "gloss": gloss_text}, "png")
            qpath.rename(qpath.with_name(f"{qid}.answered.json"))
        else:
            qpath.rename(qpath.with_name(f"{qid}.unanswered.json"))
        return True
    return False


def sense(publish: Callable, stop_event, sqlite_path: str, root: Path, canvas: int = 128, period: float = 1.0,
          words: int = 8, letters: int = 8, font_path: str = read_common.DEFAULT_FONT_PATH) -> None:
    root = Path(root)
    q_dir = root / "world" / "questions"
    while not stop_event.is_set():
        advanced = _answer_one(publish, sqlite_path, q_dir, canvas, words, letters, font_path)
        if not advanced:
            stop_event.wait(period)
