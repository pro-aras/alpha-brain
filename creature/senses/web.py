# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:01 +0400 — ALPHA4-PREREG.md §2 (the door laws),
# §3 (DOOR web): the internet opens only by judgment on his own record, and only for what he asked. Law
# text (user agent, the 2 s floor, the Wikipedia summary URL) read from Alpha 3's own road,
# /data/dev/alpha3/src/world.cpp:483,519,524 — never copied wholesale (this door adds Wiktionary, a
# per-hour cap and a STAGE/HOLD gate world.cpp's own `Open::ask` does not have).
"""creature/senses/web.py — DOOR web: fetches ONLY what the lexicon door (builder H, not yet landed) has
marked `unanswered`, ONLY while `STATUS.json["stage"] >= open_at_stage` and no HOLD file, at a hard floor
of `floor_s` seconds between fetches and at most `per_hour` per rolling hour.

**The queue contract, invented here (RAISED in the builder report — H's lexicon door format did not exist
on this tree at the time this was written):** `$ROOT/world/questions/<id>.json` = `{"id","q","word"}` (the
question itself — mirrors ALPHA4-H.md's own words: "the mind writes `$ROOT/world/questions/<id>.json`");
a sidecar `$ROOT/world/questions/<id>.status.json` = `{"status": "answered"|"unanswered"}` the lexicon door
writes after it looks the word up. This module reads `<id>.status.json`, never `<id>.json` alone (a
question with no sidecar yet has not been looked up — not a candidate, not a refusal, simply not yet
ready). Reconcile against H's real format at integration; the reader is ONE function
(`unanswered_questions`), isolated, so a format change is a one-function patch.

Every "turn" (a real fetch OR a refusal for hold/rate) respects the SAME `floor_s` — a refusal is a
decision too, and journaling one every poll tick under an hours-long HOLD would spam the tape; capping
its own cadence to the fetch floor keeps `web` rows bounded at ~1800/hour worst case, printed as a known
simplification in the report rather than built out further under today's deadline.

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory and never imports
Organism/machinery. `root/web/SEEN.json` is its own cursor (successfully-fetched-for-real question ids,
written AFTER the row is durable — #230's law); a FAILED fetch is tracked separately
(`_failed_at`, in memory only) and is eligible again once `floor_hour` seconds have passed — "never
retried within the hour" (the brief's own words), never a permanent blacklist the way a success is.
"""
from __future__ import annotations

import json
import re
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from . import read_common

USER_AGENT = "alpha4/0.1 (a small creature learning words; contact ahmad)"
WEB_DOOR_GATED = True   # C2/C3's own discipline: a genome line arms nothing until the code carrying it exists; flipped True in the commit that lands this module's own passing tests.

Fetcher = Callable[[str, float, str], "Tuple[Optional[int], Optional[bytes], Optional[str]]"]

_AF_INET_LOCK = threading.Lock()


def _url_escape(word: str) -> str:
    return urllib.parse.quote(word, safe="")


def _af_inet_getaddrinfo(orig):
    def _patched(host, port, family=0, type=0, proto=0, flags=0):
        return orig(host, port, socket.AF_INET, type, proto, flags)
    return _patched


def fetch_af_inet(url: str, timeout: float, user_agent: str) -> Tuple[Optional[int], Optional[bytes], Optional[str]]:
    """The real fetcher — written, never network-exercised by this builder (every test injects its own
    `fetcher`, per the brief's own "no network in any test"). AF_INET only (SOLUTIONS #184: this box's
    IPv6 road is a blackhole, and stdlib `urllib` waits out its own ~20-25 s timeout before falling back
    to IPv4) — a SCOPED monkeypatch of `socket.getaddrinfo`, held only for this one call's duration and
    always restored in `finally` (a lock serialises overlapping calls from this module's own single-
    threaded sense loop; it is not a claim about other threads elsewhere in the process, which this
    creature's other senses do not share a fetcher with)."""
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    with _AF_INET_LOCK:
        orig = socket.getaddrinfo
        socket.getaddrinfo = _af_inet_getaddrinfo(orig)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.getcode(), resp.read(), None
        except urllib.error.HTTPError as e:
            return e.code, e.read() if e.fp else None, str(e)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return None, None, str(e)
        finally:
            socket.getaddrinfo = orig


def _load_seen(seen_path: Path) -> set:
    if not seen_path.exists():
        return set()
    try:
        return set(json.loads(seen_path.read_text()))
    except (json.JSONDecodeError, OSError):
        return set()


def unanswered_questions(questions_dir: Path, exclude: set) -> List[Tuple[str, str]]:
    """This door's own candidates: every `<id>.json` under `questions_dir` whose sidecar
    `<id>.status.json` reads `{"status": "unanswered"}`, `id` not in `exclude`, sorted bytewise by id
    (deterministic — C2's pacing convention). A question with no `word` is skipped (no title to fetch)."""
    out: List[Tuple[str, str]] = []
    if not questions_dir.exists():
        return out
    for p in sorted(questions_dir.glob("*.json")):
        if p.name.endswith(".status.json"):
            continue
        qid = p.stem
        if qid in exclude:
            continue
        status_path = questions_dir / f"{qid}.status.json"
        if not status_path.exists():
            continue
        try:
            status = json.loads(status_path.read_text()).get("status")
        except (json.JSONDecodeError, OSError):
            continue
        if status != "unanswered":
            continue
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        word = data.get("word")
        if not word:
            continue
        out.append((qid, str(word)))
    return out


def _first_wiktionary_definition(data: dict) -> Optional[str]:
    """Best-effort extraction over the REST `page/definition/<word>` shape (a dict keyed by language
    code -> list of part-of-speech blocks, each carrying a `definitions` list of `{"definition": <html>}`)
    -- the first English definition, with the crudest possible tag strip (this text is DATA, shown and
    heard, never executed; a stray `<` left over from an unclosed tag is harmless)."""
    blocks = data.get("en") if isinstance(data, dict) else None
    if not isinstance(blocks, list):
        return None
    for block in blocks:
        defs = (block or {}).get("definitions")
        if isinstance(defs, list) and defs:
            raw = (defs[0] or {}).get("definition")
            if raw:
                return re.sub(r"<[^>]+>", "", str(raw)).strip() or None
    return None


def _read_status(status_path: Path) -> Optional[dict]:
    try:
        return json.loads(status_path.read_text())
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None


def _read_stage(status_path: Path) -> Optional[int]:
    status = _read_status(status_path)
    if status is None:
        return None
    stage = status.get("stage")
    return int(stage) if isinstance(stage, (int, float)) else None


def _record_meta(status: str, qid: str, word: str, url: Optional[str], code: Optional[int]) -> Dict[str, object]:
    return {"status": status, "question_id": qid, "word": word, "url": url, "http_status": code, "source": "web"}


def sense(publish: Callable, stop_event, root: Path, questions_dir: Optional[Path] = None,
          hold_file: Optional[Path] = None, floor_s: float = 2.0, per_hour: int = 60,
          open_at_stage: int = 4, max_words: int = 8, letters: int = 8, canvas: int = 128,
          font_path: Optional[str] = None, poll_period: float = 2.0, fetcher: Optional[Fetcher] = None,
          now: Optional[Callable[[], float]] = None) -> None:
    """`fetcher`/`now`: injectable (SOLUTIONS: 61 fetches at a REAL 2.0 s floor would be a 2-minute test) —
    default to `fetch_af_inet`/`time.monotonic`, exactly the production road; every test here passes its
    own. `questions_dir`/`hold_file`: resolved by `creature/body.py:main` from `declared["DOOR_WEB"]`
    (None when the gene is undeclared — this function is simply never wired then, matching every other
    door's C2/C3 gate)."""
    root = Path(root)
    questions_dir = Path(questions_dir) if questions_dir is not None else (root / "world" / "questions")
    status_path = root / "STATUS.json"
    seen_path = root / "web" / "SEEN.json"
    seen_path.parent.mkdir(parents=True, exist_ok=True)
    seen = _load_seen(seen_path)                 # ids fetched FOR REAL (ok or 404 "no page") -- permanent, never reconsidered
    failed_at: Dict[str, float] = {}              # id -> monotonic time of its last FAILED attempt -- retryable after floor_hour
    now_fn = now or time.monotonic
    fetch_fn = fetcher or fetch_af_inet
    fetch_times: "list[float]" = []               # the rolling-hour rate budget (monotonic timestamps of REAL fetches only)
    last_action_at: Optional[float] = None
    last_refusal: List[Optional[Tuple[str, str]]] = [None]   # (reason, question_id) last JOURNALED refusal -- de-dup, see below
    FLOOR_HOUR = 3600.0

    def _rate_available() -> bool:
        cutoff = now_fn() - FLOOR_HOUR
        while fetch_times and fetch_times[0] < cutoff:
            fetch_times.pop(0)
        return len(fetch_times) < per_hour

    while not stop_event.is_set():
        stage = _read_stage(status_path)
        if stage is None or stage < open_at_stage:
            stop_event.wait(poll_period)
            continue
        exclude = seen | {qid for qid, t in failed_at.items() if now_fn() - t < FLOOR_HOUR}
        candidates = unanswered_questions(questions_dir, exclude)
        if not candidates:
            stop_event.wait(poll_period)
            continue
        if last_action_at is not None:
            elapsed = now_fn() - last_action_at
            if elapsed < floor_s:
                stop_event.wait(min(poll_period, floor_s - elapsed))
                continue

        qid, word = candidates[0]

        if hold_file is not None and Path(hold_file).exists():
            # De-duplicated (a spam guard): the SAME candidate refused for the SAME reason on consecutive
            # turns journals ONCE, not on every floor interval — an hours-long hold would otherwise write
            # ~1800 identical rows/hour for no new information. A DIFFERENT candidate reaching the front
            # (or the same one refused for a DIFFERENT reason) is news, and gets its own row.
            if last_refusal[0] != ("refused_hold", qid):
                publish("web", b"", _record_meta("refused_hold", qid, word, None, None), "bin")
                last_refusal[0] = ("refused_hold", qid)
            last_action_at = now_fn()
            continue

        if not _rate_available():
            if last_refusal[0] != ("refused_rate", qid):
                publish("web", b"", _record_meta("refused_rate", qid, word, None, None), "bin")
                last_refusal[0] = ("refused_rate", qid)
            last_action_at = now_fn()
            continue
        last_refusal[0] = None

        title = (word[:1].upper() + word[1:]) if word else word
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{_url_escape(title)}"
        code, body, err = fetch_fn(url, 10.0, USER_AGENT)
        fetch_times.append(now_fn())
        extract: Optional[str] = None
        if code == 200 and body is not None:
            try:
                data = json.loads(body.decode("utf-8", errors="replace"))
                extract = data.get("extract") or data.get("description") or None
            except (json.JSONDecodeError, UnicodeDecodeError):
                extract = None
        if extract is None:
            # Wikipedia had nothing to show (a 200 with an empty summary, a 404, or the road failed) —
            # the brief's own word is "else": try Wiktionary's definition whenever Wikipedia gave nothing,
            # not only on a hard failure.
            url2 = f"https://en.wiktionary.org/api/rest_v1/page/definition/{_url_escape(word)}"
            code2, body2, err2 = fetch_fn(url2, 10.0, USER_AGENT)
            fetch_times.append(now_fn())
            if code2 == 200 and body2 is not None:
                try:
                    extract = _first_wiktionary_definition(json.loads(body2.decode("utf-8", errors="replace")))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    extract = None
            url, code, body, err = url2, code2, body2, err2

        # A DEFINITIVE answer (a real HTTP response, even an empty or a 404 one) is "ok" and permanent —
        # there is nothing to gain by re-asking the same encyclopaedia the same question again. Only a
        # TRANSIENT failure (no response at all, a 5xx, a 429 — "the door, not the room", world.cpp's own
        # distinction) is "failed" and retried after the hour.
        transient = code is None or code >= 500 or code == 429
        ok = not transient
        # Whether the render road is real, decided BEFORE the record row is published, so the record can
        # honestly self-report it (advisor's fix #8: a stub must not send the sense into a restart loop —
        # every call into read_common is guarded, and a partial landing is handled exactly like a total stub).
        sentences: List[str] = []
        rendered = False
        render_error: Optional[str] = None
        if extract:
            try:
                sentences = read_common.split_sentences(extract)
                rendered = True
            except NotImplementedError as e:
                sentences = []
                rendered = False
                render_error = str(e)

        meta = _record_meta("ok" if ok else "failed", qid, word, url, code)
        meta["rendered"] = rendered
        meta["had_extract"] = bool(extract)
        if render_error is not None:
            meta["render_error"] = render_error
        publish("web", body if body is not None else b"", meta, "bin")

        if ok:
            seen.add(qid)
            seen_path.write_text(json.dumps(sorted(seen)))   # AFTER the record row is durable -- the cursor law (#230)
        else:
            failed_at[qid] = now_fn()

        if rendered:
            base = f"web{qid}"
            for ix, sentence in enumerate(sentences):
                moment = f"{base}s{ix:04d}"
                try:
                    words = read_common.words_of(sentence, max_words, letters)
                except NotImplementedError:
                    words = []
                for w in words:
                    if w:
                        publish("ear", w.encode("utf-8"), {"moment": moment, "source": "web", "word": w}, "txt")
                try:
                    rgb = read_common.render_line(sentence, canvas, font_path)
                    png = read_common.png_bytes(rgb)
                except NotImplementedError:
                    png = None
                if png is not None:
                    publish("eye", png, {"moment": moment, "source": "web", "question_id": qid,
                                          "word": word, "sentence_ix": ix, "text": sentence}, "png")

        last_action_at = now_fn()
