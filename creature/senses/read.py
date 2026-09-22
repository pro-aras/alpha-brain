# edit: Claude (Sonnet 5, ALPHA4 builder H), 2026-09-23 01:1x +0400 — ALPHA4-H task 2 (docs/briefs/ALPHA4-H.md;
# ALPHA4-PREREG.md §3): the shelf reader -- a sentence SHOWN (rendered on a canvas) and HEARD (its words as
# ear rows) on one moment, walking `/data/alpha3-library/SHELF.sqlite`'s nursery prose in curriculum order.
"""creature/senses/read.py — a sense thread that reads Ahmad's shelf aloud: every `period` seconds it takes
the NEXT sentence (a cursor `root/read/CURSOR.json` = {doc_id, sentence_ix, chunk_ix}, written AFTER the
row(s) are durable -- the cursor law, #230), publishes one `ear` row per word (source "shelf") then ONE `eye`
row (the rendered line, source "shelf"), on ONE moment id `readXXXXXXXX` deterministic from
(doc_id, sentence_ix, chunk_ix). A sentence longer than `words` continues on the FOLLOWING moments (a
distinct chunk_ix each) -- creature/senses/folder.py's own "one item per period" model, extended with a
third cursor coordinate because a sentence, unlike a picture, may need more than one moment.

**THE NURSERY SHELF EXCLUDES HELD-OUT EXAM FILES (#224):** only `docs` rows with `format='text'`; every
path containing "holdout" and every ".jsonl" exam-family path (e.g. `K/mathematics/compare.holdout.jsonl`,
`counting.train.jsonl`) is excluded -- the exam bank must never be shown (ALPHA4-H.md's own words). Ordered
by the curriculum's own class bands: CURRICULUM.md was read in full (2026-09-23) and names no per-doc
order (only the six classes' CONTENTS), so `_nursery_docs` falls back to the brief's own stated order --
K, G1-G3, G4-G8, G9-G12, College, University, each band sorted by path -- exactly as instructed. If a
future CURRICULUM.md ever adds a literal "## Reading order" section (a markdown list of exact shelf
paths), `_explicit_order` below picks it up; today it returns None on every real curriculum file on disk.

**shape (task 0's own candidate, kept as a real code path, not a rewrite the toy might force later):**
`one_word_moments=False` (the default, ALPHA4-PREREG §3's literal genome line): ONE moment per chunk, every
word of the chunk as an ear row, then the rendered LINE as the eye row -- MEET (creature/mind.py:_consume_eye)
binds every located glance of that canvas to `self.pending[moment]`, which is last-wins: only the chunk's
LAST word ever gets a words-cell born for it (`self._heard`/ARRIVAL), and only that word is ever answerable
by `creature.ask what-is`. `one_word_moments=True` (task 0's candidate, built so a design pivot is a
parameter, not a rewrite): for each chunk, ALSO publish one extra moment PER WORD -- the word alone, heard
and shown LARGE (the maker's own proven one-word-one-moment road, `creature/world_maker.py`) -- so every
word gets its own MEET binding; the whole-line "sentence moment" is published either way, since
`genome/sentence.py`'s frame-finder reads `pending_words[moment]`, which needs every word of the chunk on
ONE moment regardless of how MEET is fed.

A pure SENSE (G4-1's writer sweep): never touches state/journal/memory, never imports Organism/machinery.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from . import read_common

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists. `--shelf`/`--curriculum` stay explicit overrides for tests regardless of this
# constant (creature/body.py:main's own convention for --folder/--game-door).
READ_DOOR_GATED = True

_CLASS_ORDER = ("K", "G1-G3", "G4-G8", "G9-G12", "College", "University")
_ORDER_HEADING_RE = re.compile(r"^##\s*Reading order\s*$", re.M)
_ORDER_ITEM_RE = re.compile(r"^\s*-\s*(\S+)\s*$", re.M)


def _class_rank(path: str) -> int:
    top = path.split("/", 1)[0]
    try:
        return _CLASS_ORDER.index(top)
    except ValueError:
        return len(_CLASS_ORDER)   # a top dir CURRICULUM.md never named (e.g. "video") -- walked last


def _explicit_order(curriculum_text: str) -> Optional[List[str]]:
    """A literal "## Reading order" section (a markdown list of exact shelf paths), if the curriculum ever
    states one. None (today, always -- CURRICULUM.md's six class sections describe CONTENTS, never a
    per-doc walk order) means the caller falls back to the class-band order above, exactly as ALPHA4-H.md
    itself instructs ("if it names no per-doc order, walk K/ first, then G1-G3, ...")."""
    m = _ORDER_HEADING_RE.search(curriculum_text)
    if not m:
        return None
    tail = curriculum_text[m.end():]
    next_heading = re.search(r"^##\s", tail, re.M)
    body = tail[:next_heading.start()] if next_heading else tail
    return _ORDER_ITEM_RE.findall(body) or None


def _nursery_docs(shelf_db: str, curriculum_md: str) -> List[Tuple[str, str]]:
    """(doc_id, path), in reading order -- the nursery shelf: format='text' prose, held-out exam files
    excluded (#224). Reads `curriculum_md` (the genome line's own second path) to check for an explicit
    order before falling back."""
    con = sqlite3.connect(f"file:{shelf_db}?mode=ro", uri=True)
    try:
        cur = con.cursor()
        cur.execute("SELECT doc_id, path FROM docs WHERE format='text' AND path NOT LIKE '%holdout%' AND path NOT LIKE '%.jsonl'")
        rows = [(str(r[0]), str(r[1])) for r in cur.fetchall()]
    finally:
        con.close()
    try:
        curriculum_text = Path(curriculum_md).read_text(errors="replace")
    except OSError:
        curriculum_text = ""
    explicit = _explicit_order(curriculum_text)
    if explicit:
        rank = {p: i for i, p in enumerate(explicit)}
        rows.sort(key=lambda r: (rank.get(r[1], len(explicit)), r[1]))
    else:
        rows.sort(key=lambda r: (_class_rank(r[1]), r[1]))
    return rows


def _load_cursor(cursor_path: Path) -> dict:
    if not cursor_path.exists():
        return {}
    try:
        return json.loads(cursor_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}   # a torn cursor from a crash mid-write -- treated as "nothing read yet" (folder.py's own SEEN.json law)


def _doc_sentences(base_dir: Path, path: str) -> List[str]:
    try:
        text = (base_dir / path).read_text(errors="replace")
    except OSError:
        return []
    return read_common.split_sentences(text)


def _chunks_of(sentence: str, words: int, letters: int) -> List[List[str]]:
    """Every clean word of `sentence` (read_common.words_of, uncapped), split into groups of at most
    `words` -- "a sentence longer than `words` continues on the following moments" (task 2's own text)."""
    all_words = read_common.words_of(sentence, max_words=10 ** 6, letters=letters)
    if not all_words:
        return []
    return [all_words[i:i + words] for i in range(0, len(all_words), words)]


def _moment_id(doc_id: str, sentence_ix: int, chunk_ix: int, word_ix: Optional[int] = None) -> str:
    key = f"{doc_id}:{sentence_ix}:{chunk_ix}" if word_ix is None else f"{doc_id}:{sentence_ix}:{chunk_ix}:w{word_ix}"
    return "read" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]


def _publish_chunk(publish: Callable, doc_id: str, sentence_ix: int, chunk_ix: int, chunk_words: List[str],
                    canvas: int, font_path: str, one_word_moments: bool) -> None:
    if one_word_moments:
        # task 0's candidate: every word its own moment, shown large -- world_maker.py's own proven road,
        # applied to a single word instead of a drawn shape.
        for wi, w in enumerate(chunk_words):
            wmoment = _moment_id(doc_id, sentence_ix, chunk_ix, wi)
            publish("ear", w.encode("utf-8"), {"moment": wmoment, "source": "shelf", "word": w}, "txt")
            rgb = read_common.render_line(w, canvas, font_path)
            publish("eye", read_common.png_bytes(rgb),
                    {"moment": wmoment, "source": "shelf", "doc_id": doc_id, "sentence_ix": sentence_ix,
                     "chunk_ix": chunk_ix, "word_ix": wi, "text": w}, "png")
    # the sentence moment: every word heard, the whole line shown -- genome/sentence.py's frame-finder
    # reads `pending_words[moment]` on THIS moment either way (L-11's own words_in_instant).
    moment = _moment_id(doc_id, sentence_ix, chunk_ix)
    for w in chunk_words:
        publish("ear", w.encode("utf-8"), {"moment": moment, "source": "shelf", "word": w}, "txt")
    line_text = " ".join(chunk_words)
    rgb = read_common.render_line(line_text, canvas, font_path)
    publish("eye", read_common.png_bytes(rgb),
            {"moment": moment, "source": "shelf", "doc_id": doc_id, "sentence_ix": sentence_ix,
             "chunk_ix": chunk_ix, "text": line_text}, "png")


def sense(publish: Callable, stop_event, shelf_db: str, curriculum_md: str, root: Path, canvas: int = 128,
          period: float = 5.0, words: int = 8, letters: int = 8, font_path: str = read_common.DEFAULT_FONT_PATH,
          one_word_moments: bool = False) -> None:
    root = Path(root)
    base_dir = Path(shelf_db).resolve().parent   # SHELF.sqlite's own directory -- docs' paths are relative to it (READ FIRST note)
    cursor_path = root / "read" / "CURSOR.json"
    cursor_path.parent.mkdir(parents=True, exist_ok=True)

    docs = _nursery_docs(shelf_db, curriculum_md)
    doc_ix, sentence_ix, chunk_ix = 0, 0, 0
    saved = _load_cursor(cursor_path)
    if saved.get("doc_id") is not None:
        ids = [d for d, _p in docs]
        try:
            doc_ix = ids.index(saved["doc_id"])
            sentence_ix = int(saved.get("sentence_ix", 0))
            chunk_ix = int(saved.get("chunk_ix", 0))
        except ValueError:
            pass   # a resumed shelf that no longer carries this doc_id -- start over rather than guess

    cur_doc_ix: Optional[int] = None
    cur_sentences: List[str] = []
    cur_chunks: List[List[str]] = []

    while not stop_event.is_set():
        if doc_ix >= len(docs):
            stop_event.wait(period)   # the shelf is exhausted -- idle, never crash (folder.py's own "no candidate" law)
            continue
        doc_id, path = docs[doc_ix]
        if cur_doc_ix != doc_ix:
            cur_sentences = _doc_sentences(base_dir, path)
            cur_doc_ix = doc_ix
            cur_chunks = []
        if sentence_ix >= len(cur_sentences):
            doc_ix += 1; sentence_ix = 0; chunk_ix = 0; cur_doc_ix = None
            continue
        if chunk_ix == 0 or not cur_chunks:
            cur_chunks = _chunks_of(cur_sentences[sentence_ix], words, letters)
        if not cur_chunks or chunk_ix >= len(cur_chunks):
            sentence_ix += 1; chunk_ix = 0; cur_chunks = []
            continue

        chunk_words = cur_chunks[chunk_ix]
        _publish_chunk(publish, doc_id, sentence_ix, chunk_ix, chunk_words, canvas, font_path, one_word_moments)

        next_chunk_ix = chunk_ix + 1
        if next_chunk_ix >= len(cur_chunks):
            next_sentence_ix, next_chunk_ix, next_doc_id = sentence_ix + 1, 0, doc_id
        else:
            next_sentence_ix, next_doc_id = sentence_ix, doc_id
        cursor_path.write_text(json.dumps({"doc_id": next_doc_id, "sentence_ix": next_sentence_ix, "chunk_ix": next_chunk_ix}))
        chunk_ix = next_chunk_ix
        if next_chunk_ix == 0 and next_sentence_ix != sentence_ix:
            sentence_ix = next_sentence_ix
        stop_event.wait(period)
