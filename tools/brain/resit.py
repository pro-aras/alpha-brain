#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 15:44 +0400 — PREREG-RESIT-READER (branch resit-1003; the law's text b02cf10, sha256 f6390b0d82b410b2d0f6c6d91b712d20b54b3b55f814784f38ec5ac66a45dedd,
# signed by the author 15:27, the architect 15:30 and the seat 15:31): the re-sit reader. This file is Part 1 — the PURE parts (no numpy, no life code); the children and the orchestrator follow below.
"""tools/brain/resit.py — a daily offline re-sit of a life's saved brain on the scene sittings' FIXED items, graded as a SERIES, read against the
brain AT the sittings (the ORIGIN) and never against a daily copy.

RUN BY PATH, never `-m`:  python3 -B -I tools/brain/resit.py run --mode {daily|gate|origin} --root R --code C --items-root I --grader-code G --out OUT --scored S
The orchestrator imports the standard library only. It runs two CHILD processes, each BY PATH with the same flags, so that no module of the LIFE (the
subject: genome, brain, creature) and no module of the GRADER ever meet in one interpreter:
    python3 -B -I tools/brain/resit.py answer --spec <json>     # the ANSWER child: the life's own code first on sys.path; frozen brain; no learning
    python3 -B -I tools/brain/resit.py grade  --spec <json>     # the GRADE child: the pinned grader's code first on sys.path
It never writes under a life's root, never calls Brain.learn, never calls Brain.turn outside R14's test on a copy, never touches a unit."""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import math
import os
import re
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

# ================================================================================================ errors and constants
class ResitError(Exception):
    """A refusal by name. Daily mode turns it into a row and exits 0; origin and gate modes exit 2."""


class Refused(ResitError):
    """The run is refused: something it was told to trust does not hold."""


class Skipped(ResitError):
    """Nothing to do yet (no state/prev, no sitting on the tape): a row, never a crash (#230)."""


class NotGradable(ResitError):
    """A premise of the reading does not hold (P0: the brain moved after the sittings): NOT GRADABLE, never «a reader defect»."""


SHAPE_WORDS = ("circle", "cross", "ring", "square", "star", "triangle")
COLOUR_WORDS = ("blue", "green", "red", "white", "yellow")
SIZE_WORDS = ("big", "small")
CLASSES = ("shape_only", "colour_or_size", "white")
CLASS_MARKS = ("M1", "M2a", "M3")                 # the marks the series splits by phrase class (law §2)
READ_ONLY_ACTS = ("turn", "refused")              # R9 / AM1 (b): every other act of a `kind: "brain"` row moves the brain or may — the set FAILS CLOSED
UNDERPOWERED_N = 30
VERDICT_COPY_LEARNED = 8640                       # HEARS-2 A2.2: one day of maker-only feed
EYE_LINE_PREFIXES = ("RETINA", "GAZE", "SENSE.colour", "BRAIN")
PINNED_FIELDS = ("root", "n_asks", "n_canvases", "ask_digest", "canvas_digest", "world_scene_line_sha", "scored")
MODULE_PREFIXES = ("genome", "brain", "creature", "tools")


# ================================================================================================ small pure helpers
def canon(obj) -> str:
    """The canonical text of a JSON value: sorted keys, no spaces, NaN/Infinity kept as the journal writes them. int and float stay different bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=True)


def rows_equal(a: Mapping, b: Mapping, ignore: Sequence[str] = ("hash",)) -> bool:
    """R1 (a): two journal rows are equal iff their canonical texts are, the chain field `hash` set aside and nothing else."""
    ka = {k: v for k, v in a.items() if k not in ignore}
    kb = {k: v for k, v in b.items() if k not in ignore}
    return canon(ka) == canon(kb)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def check_flags(dont_write_bytecode: int, isolated: int, env: Mapping[str, str], blas_reading: Optional[int] = None) -> Dict[str, object]:
    """§1.0: the orchestrator refuses to run unless python was started with -B (a cold import of the grader would write .pyc files INTO the life's tree)
    and -I (PYTHON* variables could put master's tree first on sys.path and shadow the life's modules), and unless the two BLAS pins are 1 (a brain
    state's float bits depend on the BLAS thread count, #246 (8)). Both are recorded in the row.
    # edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 16:54 +0400 — R2's READING: `blas_reading=N` (N != 1) declares that this ANSWER run is the law's one warm run under another thread count
    # (the pin stays law; the reading is printed). The declared N and the environment's two pins must AGREE, else refused: a reading can never be a mis-set environment."""
    problems: List[str] = []
    reading = int(blas_reading) if blas_reading is not None and int(blas_reading) != 1 else None
    want = "1" if reading is None else str(reading)
    if not dont_write_bytecode:
        problems.append("python was not started with -B (a cold import of tools/brain/grade_life.py would write .pyc files into the life's tree)")
    if not isolated:
        problems.append("python was not started with -I (a PYTHON* variable could put another tree first on sys.path)")
    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
        if env.get(var) != want:
            why = (f"the declared blas_reading is {reading}, so both pins must say so" if reading is not None
                   else "the life's own unit pins it; a brain state's float bits depend on it")
            problems.append(f"{var} is {env.get(var)!r}, not {want!r} ({why})")
    if problems:
        raise ResitError("refused: " + "; ".join(problems))
    out: Dict[str, object] = {"dont_write_bytecode": True, "isolated": True, "OPENBLAS_NUM_THREADS": want, "OMP_NUM_THREADS": want}
    if reading is not None:
        out["blas_reading"] = reading
    return out


def resolve_tape_dir(root, declared_path: Optional[str]) -> Path:
    """creature.tape._resolve_tape_dir, copied (pinned against the life's own function by a parity test)."""
    root = Path(root)
    if not declared_path:
        return root / "tape"
    parts = Path(declared_path).parts
    if parts and parts[0] == "run":
        parts = parts[1:]
    return root / Path(*parts) if parts else root / "tape"


def tape_decl_of(genome_text: str) -> Optional[str]:
    """The genome's `TAPE <path>` line, read as text (the orchestrator has no parser of the life's): None when undeclared."""
    for line in genome_text.splitlines():
        s = line.split("#", 1)[0].strip()
        parts = s.split()
        if len(parts) >= 2 and parts[0] == "TAPE":
            return parts[1]
    return None


# ================================================================================================ phrase classes and the pairing arithmetic (law §2, §4)
def phrase_class(phrase: Sequence[object]) -> str:
    """white > colour_or_size > shape_only. A phrase holding a word of NO type (or no word) is refused by name, never binned (R6)."""
    ws = [str(w) for w in (phrase or [])]
    if not ws:
        raise ResitError("refused: an empty phrase has no class")
    unknown = [w for w in ws if w not in SHAPE_WORDS and w not in COLOUR_WORDS and w not in SIZE_WORDS]
    if unknown:
        raise ResitError(f"refused: the phrase word(s) {unknown} are of no type (shape, colour, size) — a phrase is never binned by guess")
    if "white" in ws:
        return "white"
    if any(w in COLOUR_WORDS or w in SIZE_WORDS for w in ws):
        return "colour_or_size"
    return "shape_only"


def smallest_gap(n: int) -> Optional[float]:
    """The smallest gap a paired test can pass at n items (HEARS-2 A2.2; SOLUTIONS #245 (5)): 10 / n."""
    return (10.0 / n) if n else None


def class_rates(recs: Iterable[Mapping[str, object]]) -> Dict[str, Dict[str, object]]:
    """recs: [{"class", "in_g" (covered and gradable), "correct"}]. Per class: items, n (the graded population), k (correct among them), left_out, rate,
    10 / n, UNDERPOWERED (n < 30) — an empty class reads n/a, never 0."""
    out: Dict[str, Dict[str, object]] = {}
    recs = list(recs)
    for c in CLASSES:
        sel = [r for r in recs if r["class"] == c]
        g = [r for r in sel if r["in_g"]]
        n, k = len(g), sum(1 for r in g if r["correct"])
        out[c] = {"items": len(sel), "n": n, "k": k, "left_out": len(sel) - n, "rate": (k / n) if n else None,
                  "smallest_gap": smallest_gap(n), "underpowered": bool(sel) and n < UNDERPOWERED_N, "na": not sel}
    return out


def exact_sign_p(b: int, c: int) -> float:
    """The exact one-sided sign test p for a FALL: P(X >= b), X ~ Binomial(b + c, 1/2). No discordant pair, or b = 0, reads 1.0."""
    n = b + c
    if n == 0 or b <= 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(b, n + 1)) / float(2 ** n)


def pair_vectors(v_t: Mapping[str, Optional[int]], v_o: Mapping[str, Optional[int]]) -> Dict[str, object]:
    """Day t against the ORIGIN, by item, on the items present (1 or 0) in BOTH: b = right -> wrong, c = wrong -> right, g = (c - b) / n,
    the exact one-sided sign p for a fall (and for a rise), and 10 / n. Items in one vector only, or None in either, are left out."""
    n = b = c = 0
    for key, o in v_o.items():
        t = v_t.get(key)
        if o is None or t is None:
            continue
        n += 1
        if int(o) == 1 and int(t) == 0:
            b += 1
        elif int(o) == 0 and int(t) == 1:
            c += 1
    return {"n_paired": n, "b": b, "c": c, "g": ((c - b) / n) if n else None, "p_fall": exact_sign_p(b, c), "p_rise": exact_sign_p(c, b),
            "smallest_gap": smallest_gap(n), "discordant": b + c}


# ================================================================================================ the genome in force (law §1.2; AM2, AM3)
def read_epoch_rows(journal_dir) -> List[Dict[str, object]]:
    """Every adoption: the journal row `{"seq": s, "epoch": {"epoch": k, "genome_sha": ..., "moment", "gene", "value", "proposal_no"}, "hash": ...}`
    (an `epoch` KEY, not an `event` value; `epoch_refused` rows and stray words are not it). -> [{"seq": s, "epoch": k, "genome_sha": ..., ...}]."""
    rows: List[Dict[str, object]] = []
    for f in sorted(Path(journal_dir).glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if '"epoch"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                e = d.get("epoch") if isinstance(d, dict) else None
                if isinstance(e, dict) and "genome_sha" in e and "epoch" in e:
                    rows.append({"seq": int(d["seq"]), **e})
    return rows


def genome_in_force(root, epochs: Sequence[Mapping[str, object]], *, before_seq: Optional[int] = None, upto_seq: Optional[int] = None) -> Dict[str, object]:
    """The genome in force when the compared state or answers were made. Gate mode and the rebuilt origin: the highest epoch whose row seq is
    STRICTLY BEFORE the sitting set's begin ask (`before_seq`). Daily mode and a fallback copy: the highest epoch whose row seq is AT OR BEFORE the state's
    last_seq (`upto_seq`). Epoch 0 is GENOME.genome; epoch k is GENOME.v<k>.genome and its sha256 must be the epoch row's `genome_sha`. A root with
    GENOME.v<n> files and no readable epoch row is undetermined and REFUSED — never defaulted."""
    if (before_seq is None) == (upto_seq is None):
        raise ValueError("genome_in_force: give exactly one of before_seq, upto_seq")
    root = Path(root)
    versioned = sorted(root.glob("GENOME.v*.genome"))
    if versioned and not epochs:
        raise Refused(f"genome in force undetermined: {root} holds {[p.name for p in versioned]} and the journal holds no readable epoch row")
    sel = [e for e in epochs if (int(e["seq"]) < before_seq if before_seq is not None else int(e["seq"]) <= upto_seq)]
    k = max((int(e["epoch"]) for e in sel), default=0)
    row = None
    if k == 0:
        path, want = root / "GENOME.genome", None
    else:
        path = root / f"GENOME.v{k}.genome"
        row = next(e for e in sel if int(e["epoch"]) == k)
        want = str(row["genome_sha"])
    if not path.exists():
        raise Refused(f"genome in force: epoch {k} names {path.name}, which does not exist under {root}")
    got = sha256_file(path)
    if want is not None and got != want:
        raise Refused(f"genome in force: the sha256 of {path.name} ({got[:12]}…) is not the epoch row's genome_sha ({want[:12]}…)")
    return {"epoch": k, "path": path, "sha256": got, "epoch_row": dict(row) if row else None}


def _norm_line(line: str) -> str:
    return " ".join(line.split("#", 1)[0].split())


def genome_line_hashes(text: str) -> Dict[str, str]:
    """sha256 of the RETINA, GAZE, SENSE colour and BRAIN lines (comment- and whitespace-normalised) and of the whole text. EVOLVE cannot move any of
    the four (creature/genes.py excludes the eye keys and holds no BRAIN key), so a difference between rows is an ANOMALY (AM2)."""
    sel: Dict[str, List[str]] = {"retina": [], "gaze": [], "colour": [], "brain": []}
    for line in text.splitlines():
        s = _norm_line(line)
        if not s:
            continue
        w = s.split()
        if w[0] == "RETINA":
            sel["retina"].append(s)
        elif w[0] == "GAZE":
            sel["gaze"].append(s)
        elif w[0] == "SENSE" and len(w) > 1 and w[1] == "colour":
            sel["colour"].append(s)
        elif w[0] == "BRAIN":
            sel["brain"].append(s)
    out = {k: sha256_bytes("\n".join(v).encode("utf-8")) for k, v in sel.items()}
    out["genome"] = sha256_bytes(text.encode("utf-8"))
    return out


def world_scene_line_sha(genome_text: str) -> str:
    """sha256 of the `WORLD scene …` line (the items' world), comment-stripped."""
    for line in genome_text.splitlines():
        s = _norm_line(line)
        w = s.split()
        if len(w) >= 2 and w[0] == "WORLD" and w[1] == "scene":
            return sha256_bytes(s.encode("utf-8"))
    return sha256_bytes(b"")


# ================================================================================================ state copies (law §1.1 S1)
def verify_prints(dest, prints: Mapping[str, Sequence[int]], names: Sequence[str] = ("brain.json", "brain.npz")) -> None:
    """R4 (b): every copied file's (size, mtime_ns) must equal SNAPSHOT.json's print of it (shutil.copy2 keeps the nanosecond mtime)."""
    dest = Path(dest)
    for n in names:
        if n not in prints:
            raise Refused(f"SNAPSHOT.json carries no print of {n}")
        st = (dest / n).stat()
        size, mt = int(prints[n][0]), int(prints[n][1])
        if st.st_size != size:
            raise Refused(f"{n}: size {st.st_size} is not the manifest's {size}")
        if st.st_mtime_ns != mt:
            raise Refused(f"{n}: mtime_ns {st.st_mtime_ns} is not the manifest's {mt}")


def copy_state_prev(root, dest, *, retries: int = 3, sleep_s: float = 20.0, sleeper: Callable[[float], None] = time.sleep,
                    after_copy: Optional[Callable[[], None]] = None) -> Dict[str, object]:
    """Copy <root>/state/prev/{brain.json, brain.npz} (the last COMPLETE snapshot generation, hard links, replaced at every snapshot) into `dest` and
    CHECK the copies against prev/SNAPSHOT.json's prints. A generation replaced during the copy is retried (`retries` tries, `sleep_s` apart, no sleep
    after the last), then REFUSED by name. No state/prev: Skipped. The live root is only read."""
    prev = Path(root) / "state" / "prev"
    snapf = prev / "SNAPSHOT.json"
    names = ("brain.json", "brain.npz")
    if not snapf.exists() or not all((prev / n).exists() for n in names):
        raise Skipped(f"no usable state/prev under {root} (SNAPSHOT.json and {list(names)} must all exist)")
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    last: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        text1 = snapf.read_text()
        d1 = json.loads(text1)
        for n in names:
            shutil.copy2(prev / n, dest / n)
        if after_copy is not None:
            after_copy()
        try:
            if snapf.read_text() != text1:
                raise Refused("state/prev's generation was replaced during the copy")
            verify_prints(dest, d1["prints"], names)
            return {"last_seq": int(d1["last_seq"]), "t": d1.get("t"), "prints_ok": True, "attempts": attempt, "files": list(names),
                    "prints": {n: list(d1["prints"][n]) for n in names}, "source": str(prev)}
        except Refused as e:
            last = e
            if attempt < retries:
                sleeper(sleep_s)
    raise Refused(f"state/prev could not be copied whole in {retries} tries ({last})")


# ================================================================================================ items: the tape's asks and canvases (law §1.3)
def scan_items(root, tape_decl: Optional[str]) -> Dict[str, object]:
    """Read a life's tape (read-only, plain JSON) for the sittings: every `ask` row (its payload, set, item, mark, phrase and class) and every sitting
    canvas (an eye row of kind `sitting`). The digests carry CONTENT only — payload bytes, moments, canvas shas — never a seq, so the same seed's
    sittings on two lives hash alike."""
    tape = resolve_tape_dir(root, tape_decl)
    asks: List[Dict[str, object]] = []
    canvases: List[Dict[str, object]] = []
    sets: Dict[str, Dict[str, object]] = {}
    cur: Optional[str] = None
    ah, ch = hashlib.sha256(), hashlib.sha256()
    for f in sorted(tape.glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                sense = r.get("sense")
                meta = r.get("meta") or {}
                if sense == "ask":
                    pbytes = (tape / r["payload"]).read_bytes()
                    ph = sha256_bytes(pbytes)
                    if r.get("sha") and r["sha"] != ph:
                        raise Refused(f"tape ask row seq {r['seq']}: its sha {str(r['sha'])[:12]}… is not its payload's {ph[:12]}…")
                    p = json.loads(pbytes)
                    form = p.get("form")
                    if form == "begin":
                        cur = p.get("set")
                    setname = p.get("set") or cur
                    mark, phrase = p.get("mark"), p.get("phrase")
                    rec = {"seq": int(r["seq"]), "moment": meta.get("moment"), "form": form, "item": p.get("item"), "mark": mark, "set": setname,
                           "phrase": phrase, "payload_sha": ph, "at": r.get("at")}
                    if mark in CLASS_MARKS and phrase:
                        rec["class"] = phrase_class(phrase)
                    asks.append(rec)
                    ah.update(str(meta.get("moment")).encode("utf-8") + b"\0" + len(pbytes).to_bytes(8, "little") + pbytes)
                    if setname is not None:
                        s = sets.setdefault(setname, {"begin_seq": None, "end_seq": None, "n_asks": 0})
                        s["n_asks"] += 1
                        if form == "begin":
                            s["begin_seq"] = int(r["seq"])
                        if form == "end":
                            s["end_seq"] = int(r["seq"])
                    if form == "end":
                        cur = None
                elif sense == "eye" and meta.get("kind") == "sitting":
                    canvases.append({"seq": int(r["seq"]), "moment": meta.get("moment"), "sha": r.get("sha")})
                    ch.update(str(meta.get("moment")).encode("utf-8") + b"\0" + str(r.get("sha")).encode("utf-8") + b"\n")
    return {"asks": asks, "canvases": canvases, "sets": sets, "n_asks": len(asks), "n_canvases": len(canvases),
            "ask_digest": ah.hexdigest(), "canvas_digest": ch.hexdigest(), "tape_dir": str(tape)}


def pin_items(out_dir, scan: Mapping[str, object], *, scored: Mapping[str, object], world_line_sha: str, items_root) -> Dict[str, object]:
    """ITEMS.json: written at the first run, re-checked at every later one; the SAME --scored reference every day."""
    pin = {"root": str(items_root), "n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"],
           "canvas_digest": scan["canvas_digest"], "world_scene_line_sha": world_line_sha, "scored": dict(scored)}
    p = Path(out_dir) / "ITEMS.json"
    if not p.exists():
        atomic_write(p, json.dumps(pin, indent=1, sort_keys=True) + "\n")
        return pin
    old = json.loads(p.read_text())
    for field in PINNED_FIELDS:
        if old.get(field) != pin[field]:
            raise Refused(f"items pin: {field} is {pin[field]!r}, ITEMS.json holds {old.get(field)!r} — the series would not be about the pinned sittings")
    return old


# ================================================================================================ the journal (law R1, R9, R4 k)
_RE_KIND = re.compile(r'"kind"\s*:\s*"(answer|brain)"')


def scan_journal(journal_dir) -> Dict[str, object]:
    """Read a life's journal day files (plain JSON, streamed): the answer rows by ASK seq, the `kind: "brain"` rows as (seq, act), the epoch rows and the
    `start` event rows."""
    answers: Dict[int, List[Dict[str, object]]] = collections.defaultdict(list)
    brain_rows: List[Tuple[int, Optional[str]]] = []
    starts: List[Dict[str, object]] = []
    for f in sorted(Path(journal_dir).glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                m = _RE_KIND.search(line)
                if m:
                    d = json.loads(line)
                    k = d.get("kind")
                    if k == "answer":
                        answers[int(d["seq"])].append(d)
                    elif k == "brain":
                        brain_rows.append((int(d["seq"]), d.get("act")))
                elif '"event"' in line and '"start"' in line:
                    d = json.loads(line)
                    if d.get("event") == "start":
                        starts.append(d)
    return {"answers": dict(answers), "brain_rows": brain_rows, "epochs": read_epoch_rows(journal_dir), "starts": starts}


def collapse_duplicates(answers: Mapping[int, Sequence[Mapping[str, object]]]) -> Dict[str, object]:
    """AM1 (d): a restart inside a sitting can leave two answer rows for ONE ask seq (the killed process wrote one, the resumed one wrote it again).
    They must equal each other (the `hash` field set aside) and collapse to the LAST; unequal rows are RESTART-DIVERGENT. The key is the ASK seq —
    a `why` asked in two sittings under one item name is two asks, not a duplicate."""
    rows: Dict[int, Dict[str, object]] = {}
    dup = 0
    divergent: List[int] = []
    for seq, group in answers.items():
        last = dict(group[-1])
        rows[int(seq)] = last
        if len(group) > 1:
            dup += 1
            if not all(rows_equal(g, last) for g in group[:-1]):
                divergent.append(int(seq))
    return {"rows": rows, "restart_duplicates": dup, "divergent": sorted(divergent)}


def require_no_divergent(dup: Mapping[str, object]) -> None:
    if dup["divergent"]:
        raise Refused(f"RESTART-DIVERGENT: {len(dup['divergent'])} ask(s) hold two unequal answer rows (first ask seqs {dup['divergent'][:5]})")


def answering_seq(row: Mapping[str, object]) -> int:
    """The seq at which the answer was GIVEN: a held form is answered at its eye row (`eye_seq`); a canvas-less form (begin, end, why) at its ask row.
    The answer row's own `seq` is the ASK's."""
    return int(row["eye_seq"]) if row.get("eye_seq") is not None else int(row["seq"])


def classify_early_late(js: Mapping[str, object], begin_seq_by_set: Mapping[str, int]) -> Dict[str, object]:
    """R9 (AM1 a–c): an item is EARLY iff NO `kind: "brain"` row whose act is NOT in {turn, refused} has begin_seq < seq < answering_seq; else LATE.
    Fail-closed: any other act (learn, calibrate, a future sleep rehearsal, an unknown one) makes it LATE. n_early is per set; 0 reads UNTESTED."""
    moving = sorted(s for s, a in js["brain_rows"] if a not in READ_ONLY_ACTS)
    sets = sorted(begin_seq_by_set.items(), key=lambda kv: kv[1])
    begins = [b for _, b in sets]
    by_ask: Dict[int, str] = {}
    per_set: Dict[str, Dict[str, object]] = {s: {"n_early": 0, "n_late": 0} for s, _ in sets}
    for seq, group in js["answers"].items():
        i = bisect.bisect_right(begins, int(seq)) - 1
        if i < 0:
            continue
        setname, begin = sets[i]
        row = group[-1]
        lo, hi = bisect.bisect_right(moving, begin), bisect.bisect_left(moving, answering_seq(row))
        early = not (lo < hi)
        by_ask[int(seq)] = "EARLY" if early else "LATE"
        per_set[setname]["n_early" if early else "n_late"] += 1
    for s, d in per_set.items():
        d["note"] = "R9 UNTESTED for this set (n_early = 0): its begin state is verified only by R10c" if d["n_early"] == 0 else ""
    return {"by_ask_seq": by_ask, "by_set": per_set}


def act_census(brain_rows: Sequence[Tuple[int, Optional[str]]], windows: Mapping[str, Tuple[int, int]]) -> Dict[str, Dict[str, int]]:
    """The acts of the `kind: "brain"` rows strictly inside each sitting (begin < seq < end)."""
    out: Dict[str, Dict[str, int]] = {}
    for s, (b, e) in windows.items():
        c: Dict[str, int] = {}
        for seq, act in brain_rows:
            if b < seq < e:
                c[str(act)] = c.get(str(act), 0) + 1
        out[s] = c
    return out


def precondition_p0(brain_rows: Sequence[Tuple[int, Optional[str]]], first_ask_seq: int) -> Dict[str, object]:
    """R1 P0 (A1, AM1 b): no `kind: "brain"` row whose act is NOT in {turn, refused} has a seq above the first sitting ask. If one has, R1 reads NOT
    GRADABLE («the brain moved after the sittings») — never «a reader defect»."""
    above: Dict[str, int] = {}
    allowed: Dict[str, int] = {}
    for seq, act in brain_rows:
        if seq > first_ask_seq:
            if act in READ_ONLY_ACTS:
                allowed[str(act)] = allowed.get(str(act), 0) + 1
            else:
                above[str(act)] = above.get(str(act), 0) + 1
    if above:
        raise NotGradable(f"NOT GRADABLE: the brain moved after the first sitting ask (seq {first_ask_seq}): rows above it {above}")
    return {"ok": True, "above": {}, "allowed_above": allowed, "first_ask_seq": first_ask_seq, "rows_seen": len(brain_rows)}


# ================================================================================================ restarts, the verdict-copy flag, eye-changed (law §4)
def restarts_between(starts: Sequence[Mapping[str, object]], lo_seq: int, hi_seq: int) -> List[Mapping[str, object]]:
    """HEARS-2 A3.4 (3): the journal's `start` rows with resumed_from_seq > 0 and lo_seq < resumed_from_seq <= hi_seq (a cold start is not a restart)."""
    return [s for s in starts if int(s.get("resumed_from_seq") or 0) > 0 and lo_seq < int(s["resumed_from_seq"]) <= hi_seq]


def restarts_info(starts: Sequence[Mapping[str, object]], lo_seq: int, hi_seq: int) -> Dict[str, object]:
    return {"restarts": restarts_between(starts, lo_seq, hi_seq), "start_rows_seen": len(starts), "lo_seq": lo_seq, "hi_seq": hi_seq}


def post_origin_learned(copy_n_learned: int, origin_n_learned: int) -> int:
    return int(copy_n_learned) - int(origin_n_learned)


def flag_verdict_copy(rows: Sequence[Mapping[str, object]]) -> List[Dict[str, object]]:
    """A2.2: the FIRST daily row whose post_origin_learned reaches 8,640 is the verdict copy — unless it is EYE-CHANGED (an anomaly, AM2): then the row
    says «verdict copy NOT taken: EYE-CHANGED», no verdict is read from it, and this law adds no replacement rule (what follows is HEARS-2's to rule)."""
    out = [dict(r) for r in rows]
    for r in out:
        p = r.get("post_origin_learned")
        if p is not None and int(p) >= VERDICT_COPY_LEARNED:
            if r.get("eye_changed"):
                r["verdict_copy_note"] = "verdict copy NOT taken: EYE-CHANGED"
            else:
                r["verdict_copy"] = True
            break
    return out


# ================================================================================================ the series store (law §4, R8)
def load_origin(out_dir) -> Optional[Dict[str, object]]:
    p = Path(out_dir) / "ORIGIN.json"
    return json.loads(p.read_text()) if p.exists() else None


def write_origin(out_dir, row: Mapping[str, object]) -> None:
    """The ORIGIN is written ONCE (R4 g / R8 a): a second one is refused, the first untouched."""
    p = Path(out_dir) / "ORIGIN.json"
    if p.exists():
        raise Refused(f"{p} exists: the origin is written once and never replaced")
    atomic_write(p, json.dumps(dict(row), indent=1, sort_keys=True) + "\n")


def check_origin_kind(kind: str, reason: Optional[str]) -> Dict[str, object]:
    """S3: a fallback copy is the origin only on the seat's say — `--reason "<the seat's words>"`, recorded verbatim (R4 i)."""
    if kind == "fallback_copy":
        if reason is None or not str(reason).strip():
            raise Refused("an origin from a fallback copy needs --reason \"<the seat's words>\" (HEARS-2 A2.3 (6)(c): the seat decides)")
        return {"kind": kind, "reason": str(reason)}
    return {"kind": kind, "reason": None}


def check_origin_source(*, from_state_prev: bool, origin_kind: str) -> None:
    """R4 (h): an origin taken from state/prev is only ever the labelled fallback — a daily copy is never an origin."""
    if from_state_prev and origin_kind != "fallback_copy":
        raise Refused("an origin from state/prev is only the labelled fallback: pass --origin-kind fallback_copy and the seat's --reason")


def pair_with_origin(day: Mapping[str, object], origin: Optional[Mapping[str, object]]) -> Dict[str, object]:
    """Every daily row is paired against the ORIGIN row, by item, per mark and class and pooled; no origin yet -> NO pairing and the line says so (R8 b)."""
    if origin is None:
        return {"vs_origin": None, "note": "NO ORIGIN: a daily copy is never one — no g_c is printed"}
    out: Dict[str, object] = {}
    dv, ov = day.get("vectors") or {}, origin.get("vectors") or {}
    classes = day.get("item_class") or {}
    for mark in sorted(set(dv) | set(ov)):
        t, o = dv.get(mark, {}), ov.get(mark, {})
        per = {"pooled": pair_vectors(t, o)}
        for c in CLASSES:
            keys = {k for k in o if classes.get(k) == c}
            per[c] = pair_vectors({k: t.get(k) for k in keys}, {k: o[k] for k in keys})
        out[mark] = per
    return {"vs_origin": out, "note": ""}


def append_series(out_dir, row: Mapping[str, object]) -> None:
    """One line appended to OUT/RESIT.jsonl; OUT/RESIT.md is rewritten from the whole series."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "RESIT.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(row), sort_keys=True) + "\n")
    rows = [json.loads(l) for l in (out / "RESIT.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    lines = ["# RESIT — the series (read from RESIT.jsonl; rewritten at every run)", "",
             "| stamp | kind | n_learned | post-origin | eye-changed | verdict copy | note |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(
            r.get("stamp"), r.get("kind"), (r.get("state") or {}).get("n_learned", ""), r.get("post_origin_learned", ""), r.get("eye_changed", ""),
            r.get("verdict_copy", r.get("verdict_copy_note", "")), r.get("refused") or r.get("skipped") or ""))
    atomic_write(out / "RESIT.md", "\n".join(lines) + "\n")


# ================================================================================================ Part 2 — the CHILDREN (law §1.0, §1.4, §1.5)
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 15:56 +0400 — the ANSWER child (the SUBJECT) and the GRADE child (the GRADER): two processes, each BY PATH with the same flags.
class ShadowError(Refused):
    """R11: a module of the life's packages came from another tree, or was imported before the import step."""


def jsonable(v):
    """creature.mind._jsonable, copied (pinned against it by a parity test): numpy scalars and arrays -> plain Python; no key or list re-ordered."""
    import numpy as np
    if isinstance(v, dict):
        return {(k if isinstance(k, str) else str(jsonable(k))): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return jsonable(v.tolist())
    if isinstance(v, np.generic):
        return v.item()
    return v


def pre_import_check(prefixes: Sequence[str] = MODULE_PREFIXES) -> None:
    """R11: before the import step NO module of the life's packages may be in sys.modules — a package imported earlier keeps another tree's __path__ and
    silently serves every later submodule from there (what `python -m tools.brain.resit` does by accident)."""
    pre = sorted(m for m in sys.modules if m.split(".")[0] in prefixes)
    if pre:
        raise ShadowError(f"R11: {len(pre)} module(s) of {list(prefixes)} were imported before the import step, e.g. {pre[:6]} — refused")


def modules_report(code: str, prefixes: Sequence[str] = MODULE_PREFIXES) -> Dict[str, object]:
    """R11: every loaded module of the four packages must have its realpath under realpath(<code>); the sha256 of each file goes into the row, and their
    digest is part of the glance cache's key (a cache drawn under other code is never reused)."""
    code_real = os.path.realpath(code)
    bad: List[str] = []
    files: Dict[str, str] = {}
    for name, mod in list(sys.modules.items()):
        if name.split(".")[0] not in prefixes:
            continue
        f = getattr(mod, "__file__", None)
        paths = [f] if f else list(getattr(mod, "__path__", None) or [])
        for pth in paths:
            rp = os.path.realpath(pth)
            if not (rp == code_real or rp.startswith(code_real + os.sep)):
                bad.append(f"{name} ({rp})")
            elif f and os.path.isfile(rp):
                files[os.path.relpath(rp, code_real)] = sha256_file(rp)
    if bad:
        raise ShadowError(f"R11: {len(bad)} module(s) are not under {code_real}: {sorted(bad)[:6]} — refused")
    mods = [{"rel": r, "sha256": s} for r, s in sorted(files.items())]
    digest = sha256_bytes("".join(f"{m['rel']}\0{m['sha256']}\n" for m in mods).encode("utf-8"))
    return {"modules": mods, "digest": digest}


def check_eye_pin(mutable_keys: Sequence[str]) -> Dict[str, int]:
    """R13 (AM2): EVOLVE cannot move the RETINA, GAZE, SENSE colour or BRAIN lines — creature/genes.py's MUTABLE_KEYS must name none of them. If one
    did, a changed eye between rows would no longer be an anomaly, and the series would not hold one thing fixed."""
    bad = [k for k in mutable_keys if str(k).startswith(EYE_LINE_PREFIXES)]
    if bad:
        raise Refused(f"R13: MUTABLE_KEYS names eye/brain key(s) {bad} — EVOLVE could move what this series holds fixed; refused")
    return {"n_mutable": len(mutable_keys), "eye_or_brain": 0}


class GlanceCache:
    """OUT/glances.pkl: {key: glance dict}. The key carries the canvas sha, the in-force RETINA / GAZE / colour line hashes AND the digest of the life's own
    modules (the law's key plus the code: a cache drawn under other code is never reused). Counts hits and misses; an unreadable file is ignored and said."""

    def __init__(self, path: Optional[str]):
        import pickle
        self.path = Path(path) if path else None
        self.entries: Dict[str, object] = {}
        self.hits = self.misses = 0
        self.note = ""
        self.dirty = False
        if self.path is not None and self.path.exists():
            try:
                d = pickle.loads(self.path.read_bytes())
                if not (isinstance(d, dict) and d.get("version") == 1 and isinstance(d.get("entries"), dict)):
                    raise ValueError("not a version-1 cache")
                self.entries = d["entries"]
            except Exception as e:
                self.entries = {}
                self.note = f"cache file unreadable ({type(e).__name__}: {e}); ignored"

    def get(self, key: str):
        g = self.entries.get(key)
        if g is None:
            self.misses += 1
        else:
            self.hits += 1
        return g

    def put(self, key: str, g) -> None:
        import copy
        self.entries[key] = copy.deepcopy(g)
        self.dirty = True

    def save(self) -> None:
        import pickle
        if self.path is not None and self.dirty:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + ".tmp")
            tmp.write_bytes(pickle.dumps({"version": 1, "entries": self.entries}, protocol=4))
            os.replace(tmp, self.path)

    def info(self) -> Dict[str, object]:
        return {"path": str(self.path) if self.path else None, "hits": self.hits, "misses": self.misses, "note": self.note}


def _canon_default(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def cmd_answer(spec_path: str) -> int:
    """The ANSWER child (the SUBJECT): the LIFE's own code first on sys.path; a frozen brain; the tape read in the mind's own order; every ask answered as the
    mind answers it (creature/mind.py: _consume_ask, _brain_canvas, _answer_ask) and written as the mind's own `answer` row. Nothing is ever learned."""
    spec = json.loads(Path(spec_path).read_text())
    flags = check_flags(sys.flags.dont_write_bytecode, sys.flags.isolated, os.environ, blas_reading=spec.get("blas_reading"))
    code = os.path.realpath(spec["code"])
    pre_import_check()
    sys.path.insert(0, code)
    cpu0 = time.process_time()
    import numpy as np
    from PIL import Image
    from genome import gaze as G
    from genome.machinery import parse_genome
    from genome.brain import Brain
    from creature.tape import read_tape, _resolve_tape_dir
    from creature import organs_road as road
    from creature.genes import MUTABLE_KEYS
    rep = modules_report(code)
    eye_pin = check_eye_pin(MUTABLE_KEYS)
    out_dir = Path(spec["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    items_root = Path(spec["items_root"])
    tape_decl = spec.get("tape_decl")
    tape_dir = _resolve_tape_dir(items_root, tape_decl)
    cache = GlanceCache(spec.get("glance_cache"))

    states: Dict[Tuple[str, str], Dict[str, object]] = {}
    nudges: List[Dict[str, object]] = []

    def load_state(entry: Mapping[str, object]) -> Dict[str, object]:
        key = (str(entry["dir"]), str(entry["genome"]))
        if key in states:
            return states[key]
        gtext = Path(entry["genome"]).read_text()
        g = parse_genome(gtext)
        cfg = dict(g.declared["BRAIN"])
        try:
            b = Brain.load(Path(entry["dir"]) / "brain", cfg)
        except Exception as e:
            raise Refused(f"state {entry['dir']}: Brain.load refused it ({type(e).__name__}: {e})")
        h_load = b.state_hash()
        # edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 16:54 +0400 — R3's PLANT: the COPY's word map nudged in memory, V += eps * std(V) * u (u seeded standard normal; scale-free), the state
        # hash ASSERTED to move (a plant that changes nothing is refused, #247 (5)); the files on disk are never touched.
        nudge = spec.get("nudge")
        if nudge:
            V = getattr(getattr(b, "L", None), "V", None)
            if V is None:
                raise Refused("R3: this brain has no word map (L.V) to nudge")
            V = np.asarray(V)
            u = np.random.default_rng(int(nudge["seed"])).standard_normal(V.shape)
            b.L.V = (V + float(nudge["eps"]) * float(V.std()) * u).astype(V.dtype)
            h_after = b.state_hash()
            if h_after == h_load:
                raise Refused(f"R3: the nudge (eps {nudge['eps']}) did not change the state's hash — the plant must change the bytes it re-sits")
            nudges.append({"eps": float(nudge["eps"]), "seed": int(nudge["seed"]), "hash_before": h_load, "hash_after": h_after,
                           "n_words": int(V.shape[0]) if V.ndim else 0, "std_V": float(V.std())})
        st = {"brain": b, "genome": g, "lines": genome_line_hashes(gtext),
              "meta": {"name": entry["name"], "dir": str(entry["dir"]), "genome": str(entry["genome"]), "genome_sha256": sha256_bytes(gtext.encode("utf-8")),
                       "parsed": {"retina": sha256_bytes(_canon_default(g.retina).encode()), "gaze": sha256_bytes(_canon_default(g.gaze).encode()),
                                  "colour": sha256_bytes(_canon_default(g.colour).encode()), "brain": sha256_bytes(_canon_default(cfg).encode())},
                       "lines": genome_line_hashes(gtext), "state_hash": h_load, "n_learned": int(b.n_learned),
                       "calibrated_at_load": b.calibrated_at, "n_calibrations_load": int(b.n_calibrations)}}
        states[key] = st
        return st

    entries = list(spec["states"])

    def pick_state(setname: Optional[str]) -> Dict[str, object]:
        for e in entries:
            if setname is not None and e["name"] == setname:
                return load_state(e)
        for e in entries:
            if e["name"] == "*":
                return load_state(e)
        raise Refused(f"no state for the set {setname!r} and no default state (`*`) — the spec names {[e['name'] for e in entries]}")

    rows_out: List[Dict[str, object]] = []
    pending: Dict[str, List[Dict[str, object]]] = {}
    held_payloads: List[Dict[str, object]] = []
    active: Optional[Dict[str, object]] = None
    asks_seen = 0
    turn_check: Optional[Dict[str, object]] = None
    turn_spec = spec.get("check_turn")

    def glance(row: Mapping[str, object], st: Mapping[str, object]):
        ln = st["lines"]
        key = f"{row['sha']}|{ln['retina']}|{ln['gaze']}|{ln['colour']}|{rep['digest']}"
        g = cache.get(key)
        if g is None:
            rgb = np.asarray(Image.open(tape_dir / row["payload"]).convert("RGB"), dtype=np.uint8)
            g = G.glances(rgb, st["genome"].retina, st["genome"].gaze, "surprise", row["sha"], colour=st["genome"].colour, predicted=None)
            cache.put(key, g)
        return g

    def answer(ask: Mapping[str, object], g, at: str, eye_seq: Optional[int], cv: Dict[str, object]) -> None:
        payload = ask["payload"]
        form = str(payload.get("form"))
        view = None
        if g is not None:
            view = cv.get("view") or road.eye_view(g)
            cv["view"] = view
        try:
            ans = jsonable(active["brain"].ask(payload, g))
        except Exception as e:            # the organ's own refusal of a malformed ask is ANSWERED as refused, by name — as the mind does (#230)
            if type(e).__name__ != "BrainError":
                raise
            ans = {"kind": "refused", "reason": str(e), "raw": {"refused": str(e)}}
        rows_out.append({"kind": "answer", "by": "brain", "item": payload.get("item"), "mark": payload.get("mark"), "form": form, "answer": ans,
                         "moment": ask["moment"], "seq": ask["seq"], "eye_seq": eye_seq, "at": at,
                         "fix": (None if view is None else [[int(y), int(x)] for (y, x) in view[0]]),
                         "hyps": (None if view is None else [[int(i) for i in h.members] for h in view[2]]), "detail": None})

    for row in read_tape(items_root, tape_decl):
        sense = row["sense"]
        meta = row.get("meta") or {}
        moment = meta.get("moment")
        if sense == "ask":
            payload = json.loads((tape_dir / row["payload"]).read_text())
            ask = {"seq": int(row["seq"]), "at": row["at"], "moment": meta.get("moment"), "payload": payload}
            asks_seen += 1
            form = payload.get("form")
            if form == "begin" or active is None:
                active = pick_state(payload.get("set") if form == "begin" else None)
            if form in ("begin", "end", "why"):
                answer(ask, None, str(row["at"]), None, {})
            else:
                pending.setdefault(str(meta.get("moment")), []).append(ask)
        elif sense == "eye":
            asks = pending.pop(str(moment), None) if moment is not None else None
            if asks:
                g = glance(row, active)
                cv: Dict[str, object] = {}
                for ask in asks:
                    answer(ask, g, str(row["at"]), int(row["seq"]), cv)
                    if len(held_payloads) < 8:
                        held_payloads.append(ask["payload"])
                if turn_spec and turn_check is None:
                    turn_check = _turn_check(Brain, parse_genome, active, held_payloads[: int(turn_spec.get("n_asks", 3))], g, int(turn_spec.get("world_seed", 0)),
                                             entries[0], jsonable)
    unanswered = sum(len(v) for v in pending.values())
    cache.save()
    answers_text = "".join(json.dumps(r) + "\n" for r in rows_out)
    (out_dir / "answers.jsonl").write_text(answers_text, encoding="utf-8")
    smeta = []
    for st in states.values():
        b = st["brain"]
        m = dict(st["meta"])
        m.update(state_hash_end=b.state_hash(), calibrated_at_end=b.calibrated_at, n_calibrations_end=int(b.n_calibrations), n_learned_end=int(b.n_learned))
        smeta.append(m)
    meta = {"flags": flags, "code": code, "python": sys.version.split()[0], "modules": rep["modules"], "modules_digest": rep["digest"], "eye_pin": eye_pin,
            "states": smeta, "asks_seen": asks_seen, "answered": len(rows_out), "unanswered": unanswered, "glance_cache": cache.info(),
            "turn_check": turn_check, "cpu_s": round(time.process_time() - cpu0, 3), "answers_sha256": sha256_bytes(answers_text.encode("utf-8"))}
    if nudges:
        meta["nudge"] = nudges[0]
        meta["nudges"] = nudges
    atomic_write(out_dir / "answer-meta.json", json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": True, "answered": len(rows_out), "unanswered": unanswered}))
    return 0


def _turn_check(Brain, parse_genome, active: Mapping[str, object], payloads: Sequence[Mapping[str, object]], g, world_seed: int,
                entry: Mapping[str, object], jsonable_fn) -> Dict[str, object]:
    """R14 (AM1 b): `Brain.turn` is read-only — on a SECOND load of the same state, a turn leaves state_hash() and the answers to a fixed set of asks
    unchanged. R9 and P0 count a `turn` row as moving nothing; this is what makes that true."""
    cfg = dict(parse_genome(Path(active["meta"]["genome"]).read_text()).declared["BRAIN"])
    b2 = Brain.load(Path(active["meta"]["dir"]) / "brain", cfg)
    probe = [p for p in payloads if p.get("form") in ("point", "what", "say")][:5]

    def asks() -> List[str]:
        out = []
        for p in probe:
            try:
                out.append(canon(jsonable_fn(b2.ask(p, g))))
            except Exception as e:
                out.append(f"error:{type(e).__name__}:{e}")
        return out

    h0, pre = b2.state_hash(), asks()
    b2.turn(g, scene=0, world_seed=int(world_seed), says=1, asks=1)
    h1, post = b2.state_hash(), asks()
    res = {"state_hash_equal": h0 == h1, "answers_equal": pre == post, "n_asks": len(probe)}
    if not (res["state_hash_equal"] and res["answers_equal"]):
        raise Refused(f"R14: Brain.turn is not read-only on this code — state hash {'kept' if res['state_hash_equal'] else 'CHANGED'}, "
                      f"answers {'kept' if res['answers_equal'] else 'CHANGED'}; the early/late split and P0 count a turn row as moving nothing")
    return res


def grader_m2a_rows(GL, items_root: str, journal: str, genome: Optional[str]) -> Dict[str, List[Dict[str, object]]]:
    """Per-item M2a refusal, by the PINNED GRADER's own functions (the grade holds the aggregate only): for each sitting set, `M.grade_m2a` called on
    ONE item with the road's own «none» key. Nothing here re-implements a mark."""
    life = GL.Life(Path(items_root), Path(journal), Path(genome) if genome else None)
    out: Dict[str, List[Dict[str, object]]] = {}
    for tset in list(life.cfg.get("sitting") or []):
        sc = GL.SetCtx(life, tset)
        A = GL.offline_answers(life, sc)
        key = A["m2a_keys"]["LAW"]
        rows = []
        for it in sc.items.get("M2a", []):
            r = GL.M.grade_m2a([it], A["point"], key)["all"]
            rows.append({"item_id": str(it["item_id"]), "answered": r["n"] == 1, "refused": (bool(r["refusal"] >= 0.5) if r["n"] == 1 else None)})
        out[tset] = rows
    return out


def cmd_grade(spec_path: str) -> int:
    """The GRADE child (the GRADER): the pinned grader's code first on sys.path; `grade()` is called as a LIBRARY (never `main()`, which writes into the
    life's root); grade.json is written as the grader's own main writes it."""
    spec = json.loads(Path(spec_path).read_text())
    check_flags(sys.flags.dont_write_bytecode, sys.flags.isolated, os.environ)
    gcode = os.path.realpath(spec["grader_code"])
    pre_import_check()
    sys.path.insert(0, gcode)
    cpu0 = time.process_time()
    from tools.brain import grade_life as GL
    rep = modules_report(gcode)
    genome = spec.get("genome")
    g = GL.grade(Path(spec["items_root"]), Path(spec["journal"]), Path(spec["scored"]), spec["label"], Path(genome) if genome else None)
    default = getattr(getattr(GL, "R", None), "_jsonable", str)
    out = Path(spec["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "grade.json").write_text(json.dumps(g, indent=1, sort_keys=True, default=default))
    extra = None
    if spec.get("m2a_rows"):
        extra = grader_m2a_rows(GL, spec["items_root"], spec["journal"], genome)
        atomic_write(out / "items_extra.json", json.dumps({"m2a": extra}, indent=1, sort_keys=True) + "\n")
    meta = {"grader_code": gcode, "grader_sha256": sha256_file(Path(gcode) / "tools" / "brain" / "grade_life.py"), "modules": rep["modules"],
            "modules_digest": rep["digest"], "m2a_rows": bool(extra), "cpu_s": round(time.process_time() - cpu0, 3), "python": sys.version.split()[0]}
    atomic_write(out / "grade-meta.json", json.dumps(meta, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": True}))
    return 0


def _spec_arg(argv: Sequence[str]) -> str:
    if len(argv) != 2 or argv[0] != "--spec":
        raise SystemExit("usage: resit.py {answer|grade} --spec <json>")
    return argv[1]


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("run", "answer", "grade"):
        print("usage: python3 -B -I tools/brain/resit.py {run|answer|grade} …", file=sys.stderr)
        return 64
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "answer":
            return cmd_answer(_spec_arg(rest))
        if cmd == "grade":
            return cmd_grade(_spec_arg(rest))
        return cmd_run(rest)
    except ResitError as e:
        print(json.dumps({"refused": str(e), "class": type(e).__name__}))
        return 2


# ================================================================================================ Part 3 — the ORCHESTRATOR (law §1.0–§1.5, R1, R3, R5, R7, R12)
# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:04 +0400 — the orchestrator, GATE mode first (the law's order: R1 on the closed brain-long-2 before anything else is believed). It imports the
# standard library only and runs the two children BY PATH with the same flags; it never imports the life or the grader. Daily and origin modes follow R1.
RESIT_PY = os.path.abspath(__file__)
CPU_CAP_COLD_S = 30 * 60                  # R7: a cold run (no glance cache yet)
CPU_CAP_WARM_S = 8 * 60                   # R7: a warm run
DEFAULT_SCORED = "/data/dev/brain-runs/scene-s1b1r"
R1_MARKS = ("M1", "M2a", "M3")            # R1 (b): these marks, both sets, and M5 (fresh); M6 is a READING (c)
MARKER_NAME = "START.marker"
_STATUS_FIELDS = ("mind_backlog_rows", "mind_ms_per_canvas_1min")


def _differing_keys(a: Mapping[str, object], b: Mapping[str, object], ignore: Sequence[str] = ("hash",)) -> List[str]:
    out = []
    for k in sorted((set(a) | set(b)) - set(ignore)):
        if (k in a) != (k in b) or (k in a and canon(a[k]) != canon(b[k])):
            out.append(k)
    return out


def compare_answers(resit_rows: Sequence[Mapping[str, object]], life_rows: Mapping[int, Mapping[str, object]]) -> Dict[str, object]:
    """R1 (a): every re-sit answer row (read back from answers.jsonl — the JSON round trip) against the life's LAST row for the same ask seq, equal in EVERY key
    but `hash` (the key sets too: an extra key on one side is a difference). The first difference, by the lowest ask seq, is printed with both rows."""
    n_equal = n_diff = n_missing = 0
    first: Optional[Dict[str, object]] = None
    resat = set()
    for r in resit_rows:
        seq = int(r["seq"])
        resat.add(seq)
        life = life_rows.get(seq)
        if life is None:
            n_missing += 1
            continue
        if rows_equal(r, life):
            n_equal += 1
            continue
        n_diff += 1
        if first is None or seq < first["seq"]:
            first = {"seq": seq, "item": r.get("item"), "form": r.get("form"), "differing_keys": _differing_keys(r, life), "resit": dict(r), "life": dict(life)}
    return {"n_resit": len(resit_rows), "n_equal": n_equal, "n_diff": n_diff, "n_missing_life_row": n_missing,
            "life_rows_not_resat": sum(1 for s in life_rows if int(s) not in resat), "first_diff": first,
            "all_equal": bool(resit_rows) and n_diff == 0 and n_missing == 0 and n_equal == len(resit_rows)}


_ABSENT = "<missing>"


def _leaf_diffs(got, want, path: str, tol: float, diffs: List[Dict[str, object]], count: List[int]) -> None:
    if isinstance(want, dict) or isinstance(got, dict):
        if not (isinstance(want, dict) and isinstance(got, dict)):
            count[0] += 1
            diffs.append({"path": path, "got": got, "want": want})
            return
        for k in sorted(set(want) | set(got), key=str):
            p = f"{path}.{k}"
            if k not in got:
                count[0] += 1
                diffs.append({"path": p, "got": _ABSENT, "want": want[k]})
            elif k not in want:
                count[0] += 1
                diffs.append({"path": p, "got": got[k], "want": _ABSENT})
            else:
                _leaf_diffs(got[k], want[k], p, tol, diffs, count)
        return
    if isinstance(want, list) or isinstance(got, list):
        if not (isinstance(want, list) and isinstance(got, list)) or len(got) != len(want):
            count[0] += 1
            diffs.append({"path": path, "got": got if not isinstance(got, list) else f"list of {len(got)}",
                          "want": want if not isinstance(want, list) else f"list of {len(want)}"})
            return
        for i, (g, w) in enumerate(zip(got, want)):
            _leaf_diffs(g, w, f"{path}.{i}", tol, diffs, count)
        return
    count[0] += 1
    if isinstance(got, bool) or isinstance(want, bool):
        if not (type(got) is type(want) and got == want):
            diffs.append({"path": path, "got": got, "want": want})
        return
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        if isinstance(got, float) and isinstance(want, float) and math.isnan(got) and math.isnan(want):
            return
        if got == want:
            return
        if any(isinstance(x, float) and (math.isnan(x) or math.isinf(x)) for x in (got, want)) or abs(got - want) > tol:
            diffs.append({"path": path, "got": got, "want": want})
        return
    if type(got) is not type(want) or got != want:
        diffs.append({"path": path, "got": got, "want": want})


def _dig(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return _ABSENT
        d = d[k]
    return d


def compare_marks(grade: Mapping[str, object], ref: Mapping[str, object], tol: float = 1e-12) -> Dict[str, object]:
    """R1 (b): the graded marks M1, M2a and M3 (every set of the reference) and M5 equal the reference grade.json's, floats to `tol`, everything else exactly.
    M6, `meeting` and `counts` are READINGS and never compared (the reference was graded on the tape as it stood on 09-30; the tape has grown since)."""
    diffs: List[Dict[str, object]] = []
    count = [0]
    names: List[str] = []
    for s in sorted(ref.get("sets") or {}):
        for mark, keys in (("M1", ("marks", "M1")), ("M3", ("marks", "M3")), ("M2a", ("marks", "roads", "LAW", "M2a"))):
            names.append(f"{s}.{mark}")
            prefix = "sets." + s + "." + ".".join(keys)
            want = _dig(ref["sets"][s], *keys)
            got = _dig(grade.get("sets") or {}, s, *keys)
            if want is _ABSENT or got is _ABSENT:
                count[0] += 1
                diffs.append({"path": prefix, "got": got, "want": want})
            else:
                _leaf_diffs(got, want, prefix, tol, diffs, count)
    if "M5" in ref:
        names.append("M5")
        got = grade.get("M5", _ABSENT)
        if got is _ABSENT:
            count[0] += 1
            diffs.append({"path": "M5", "got": got, "want": "present"})
        else:
            _leaf_diffs(got, ref["M5"], "M5", tol, diffs, count)
    return {"equal": not diffs, "n_leaves": count[0], "diffs": diffs, "marks_compared": names, "tol": tol}


def marks_of_diffs(diffs: Sequence[Mapping[str, object]]) -> List[str]:
    """Which of M1, M2a, M3, M5 a list of compare_marks diffs touches."""
    found = set()
    for d in diffs:
        p = str(d["path"])
        if ".roads.LAW.M2a" in p:
            found.add("M2a")
        elif p.startswith("M5"):
            found.add("M5")
        else:
            for m in ("M1", "M3"):
                if f".marks.{m}" in p:
                    found.add(m)
    return sorted(found)


def newer_than(roots: Sequence, marker_ns: int, limit: int = 20) -> Dict[str, object]:
    """R5 (b): `find <root> -newer <marker>`, in-process — every file and directory under each root (symlinks not followed) whose mtime is strictly newer than the marker's.
    The listing is capped at `limit`; the count is not."""
    listed: List[str] = []
    n_newer = walked = 0
    for root in roots:
        root = str(root)
        entries = [root]
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            entries.extend(os.path.join(dirpath, n) for n in dirnames)
            entries.extend(os.path.join(dirpath, n) for n in filenames)
            for e in entries:
                walked += 1
                try:
                    mt = os.lstat(e).st_mtime_ns
                except OSError:
                    continue
                if mt > marker_ns:
                    n_newer += 1
                    if len(listed) < limit:
                        listed.append(e)
            entries = []
    return {"n_newer": n_newer, "listed": listed, "n_entries_walked": walked, "roots": [str(r) for r in roots]}


def status_reading(path) -> Dict[str, object]:
    """R12: the live life's STATUS.json `mind_backlog_rows` and `mind_ms_per_canvas_1min`, read once. An absent file, a missing field or a torn file is SAID, never a zero."""
    p = Path(path) if path else None
    out: Dict[str, object] = {"path": str(p) if p else None, "present": False, "mind_backlog_rows": None, "mind_ms_per_canvas_1min": None,
                              "fields_present": {k: False for k in _STATUS_FIELDS}, "note": "", "read_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if p is None or not p.exists():
        return out
    out["present"] = True
    try:
        out["file_mtime_ns"] = p.stat().st_mtime_ns
        d = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        out["note"] = f"STATUS.json unreadable ({type(e).__name__}: {e})"
        return out
    if isinstance(d, dict):
        for k in _STATUS_FIELDS:
            out["fields_present"][k] = k in d
            out[k] = d.get(k)
    return out


def world_seed_of(genome_text: str) -> Optional[int]:
    """The seed of the `WORLD scene seed <n>; …` line (the items' world); None when the genome has no scene world."""
    for line in genome_text.splitlines():
        m = re.match(r"\s*WORLD\s+scene\s+seed\s+(\d+)", line.split("#", 1)[0])
        if m:
            return int(m.group(1))
    return None


def git_info(path) -> Dict[str, object]:
    """The commit of a checkout — only when `path` IS a checkout (a `.git` entry in it): a directory merely inside another repository must not report that repository's HEAD."""
    d = Path(path)
    if not (d / ".git").exists():
        return {"commit": None, "dirty": None, "git_note": "not a git checkout"}
    try:
        head = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
        st = subprocess.run(["git", "-C", str(d), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        return {"commit": None, "dirty": None, "git_note": f"git failed ({type(e).__name__})"}
    if head.returncode != 0:
        return {"commit": None, "dirty": None, "git_note": "git rev-parse failed"}
    return {"commit": head.stdout.strip(), "dirty": bool(st.stdout.strip()), "git_note": ""}


def grader_info(path) -> Dict[str, object]:
    d = Path(path)
    gl = d / "tools" / "brain" / "grade_life.py"
    if not gl.exists():
        raise Refused(f"grader code {d}: tools/brain/grade_life.py does not exist")
    return {"grader_code": os.path.realpath(d), **git_info(d), "grade_life_sha256": sha256_file(gl)}


GRADER_PIN_KEYS = ("commit", "grade_life_sha256", "modules_digest")


def check_grader_pin(out_dir, info: Mapping[str, object], *, write: bool = True) -> str:
    """R4 (j): OUT/GRADER.json is written once (the first run's grader: its commit, grade_life.py's sha256, the digest of every module its child loaded); a later run under another
    pin is REFUSED. `write=False` only checks (the pre-check before the children are spent: the modules digest is known only after the grade child ran)."""
    p = Path(out_dir) / "GRADER.json"
    if not p.exists():
        if write:
            atomic_write(p, json.dumps({k: info.get(k) for k in ("grader_code", "commit", "dirty", "grade_life_sha256", "modules_digest")}, indent=1, sort_keys=True) + "\n")
            return "written"
        return "absent"
    old = json.loads(p.read_text())
    # edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:11 +0400 — FAIL CLOSED (the seat's review of the working tree): EVERY pin key is compared; a key the caller did not give reads None and
    # differs from a pinned value. The ONE legitimate skip is `modules_digest` on the pre-check (write=False), where the grade child has not yet run and the digest is not known.
    for k in GRADER_PIN_KEYS:
        new = info.get(k)
        if k == "modules_digest" and new is None and not write:
            continue
        if old.get(k) != new:
            raise Refused(f"grader pin: {k} is {new!r} but GRADER.json holds {old.get(k)!r} — a series is read by ONE grader (R4 j)")
    return "checked"


def run_child(kind: str, spec: Mapping[str, object], workdir, *, cpu_cap_s: Optional[int] = None, blas_reading: Optional[int] = None) -> Dict[str, object]:
    """Run one child BY PATH — `python3 -B -I resit.py <kind> --spec <json>` — with PYTHON* stripped from its environment and both BLAS pins set. stdout and stderr go to files
    in `workdir` (never a pipe: a child that fills one must not deadlock the parent). The CPU cap is `RLIMIT_CPU` (R7: over it the run STOPs); `os.wait4` returns THIS
    child's own rusage — its peak RSS and its CPU time are the numbers the law's price names (RULES 6d)."""
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    specp = workdir / f"{kind}-spec.json"
    specp.write_text(json.dumps(spec, indent=1, sort_keys=True), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    n = str(int(blas_reading)) if blas_reading and int(blas_reading) != 1 else "1"
    env["OPENBLAS_NUM_THREADS"] = n
    env["OMP_NUM_THREADS"] = n
    cmd = [sys.executable, "-B", "-I", RESIT_PY, kind, "--spec", str(specp)]
    outp, errp = workdir / f"{kind}.stdout", workdir / f"{kind}.stderr"
    t0 = time.time()
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe, env=env, cwd=str(workdir))
        if cpu_cap_s:
            try:
                resource.prlimit(p.pid, resource.RLIMIT_CPU, (int(cpu_cap_s), int(cpu_cap_s) + 15))
            except (ProcessLookupError, OSError):
                pass
        _pid, status, ru = os.wait4(p.pid, 0)
    p.returncode = os.waitstatus_to_exitcode(status)
    stdout = outp.read_text(errors="replace")
    result: Dict[str, object] = {}
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                result = json.loads(line)
            except ValueError:
                result = {}
            break
    return {"kind": kind, "rc": p.returncode, "result": result, "wall_s": round(time.time() - t0, 3), "cpu_s": round(ru.ru_utime + ru.ru_stime, 3),
            "maxrss_mb": round(ru.ru_maxrss / 1024.0, 1), "stderr_tail": errp.read_text(errors="replace")[-1500:], "stdout_file": str(outp), "stderr_file": str(errp)}


def require_child_ok(ch: Mapping[str, object], cap_s: Optional[int]) -> None:
    """A child that did not finish becomes a NAMED refusal, never a crash: its own refusal text, the CPU cap (R7), a kill (the slot's memory cap or the RAM guard, RULES 6c), or its stderr."""
    rc, kind = int(ch["rc"]), str(ch["kind"])
    if rc == 0:
        return
    res = ch.get("result") or {}
    if rc == 2 and res.get("refused"):
        raise Refused(str(res["refused"]))
    if rc == -24:
        raise Refused(f"R7: the {kind.upper()} child exceeded the CPU cap of {cap_s} s (SIGXCPU) after {ch['cpu_s']} CPU-s — the run STOPs and reports")
    if rc == -9:
        raise Refused(f"the {kind.upper()} child was killed (SIGKILL) at {ch['maxrss_mb']} MB peak — the slot's memory cap or the RAM guard (read the slot ledger: "
                      f"exit 137 is SLOT OOM-CAP or SLOT RAMGUARD-KILLED, RULES 6c)")
    raise ResitError(f"the {kind.upper()} child failed (rc {rc}): {str(ch['stderr_tail']).strip()[-600:]}")


def parse_run_args(argv: Sequence[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="resit.py run", allow_abbrev=False)
    ap.add_argument("--mode", required=True, choices=("gate", "daily", "origin"))
    ap.add_argument("--root", required=True, help="the life whose state/prev is copied (gate, daily)")
    ap.add_argument("--code", help="the code the SUBJECT runs (default <root>/code)")
    ap.add_argument("--items-root", help="the life whose tape holds the fixed sittings (default --root)")
    ap.add_argument("--grader-code", required=True, help="a checkout of the pinned commit carrying the grader (tools/brain/grade_life.py)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scored", default=DEFAULT_SCORED)
    ap.add_argument("--label", help="names the run's folder (gate: default r1; daily: the stamp)")
    ap.add_argument("--stamp", help="default: UTC now")
    ap.add_argument("--reference-grade", help="R1 (b): the reference grade.json")
    ap.add_argument("--check-turn", action="store_true", help="R14: Brain.turn is read-only on a second load of the state")
    ap.add_argument("--world-seed", type=int, help="the seed Brain.turn's substreams are keyed by (default: the items genome's WORLD scene seed, else 0)")
    ap.add_argument("--status", help="the live life's STATUS.json (R12); default <root>/STATUS.json when it exists")
    ap.add_argument("--cache", help="the glance cache file (default OUT/glances.pkl)")
    ap.add_argument("--blas-reading", type=int, help="R2's one warm run under another BLAS thread count (the pin stays law; the reading is printed)")
    ap.add_argument("--nudge", type=float, help="R3's plant: V += eps * std(V) * u on the COPY in memory")
    ap.add_argument("--nudge-seed", type=int, default=20261003)
    ap.add_argument("--cpu-cap-s", type=int, help="override R7's cap (tests)")
    ap.add_argument("--m2a-rows", action="store_true", help="also take the per-item M2a rows from the pinned grader's own functions")
    ap.add_argument("--copy-retry-sleep-s", type=float, default=20.0)
    return ap.parse_args(list(argv))


def _is_inside(child: Path, parents: Sequence[Path]) -> Optional[Path]:
    c = Path(os.path.realpath(child))
    for p in parents:
        pr = Path(os.path.realpath(p))
        if c == pr or pr in c.parents:
            return pr
    return None


def _outermost(paths: Sequence) -> List[str]:
    """Realpaths with any path that lies inside another dropped (a life's code/ is walked once, with its root)."""
    real = sorted({os.path.realpath(p) for p in paths})
    return [p for p in real if not any(q != p and (p == q or p.startswith(q + os.sep)) for q in real)]


def _utc_stamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def cmd_run(argv: Sequence[str]) -> int:
    a = parse_run_args(argv)
    flags = check_flags(sys.flags.dont_write_bytecode, sys.flags.isolated, os.environ)
    root = Path(a.root)
    items_root = Path(a.items_root) if a.items_root else root
    code = Path(a.code) if a.code else root / "code"
    inside = _is_inside(Path(a.out), [root, items_root, code])
    if inside is not None:
        raise Refused(f"--out {a.out} lies inside {inside}: nothing is ever written under a life (R5); give an OUT elsewhere")
    a.stamp = a.stamp or _utc_stamp()
    if a.mode == "gate":
        return run_gate(a, flags, root, items_root, code)
    raise ResitError(f"refused: --mode {a.mode} is not built yet (the law builds the gate first; daily and origin follow R1)")


def run_gate(a: argparse.Namespace, flags: Mapping[str, object], root: Path, items_root: Path, code: Path) -> int:
    """R1 (a nudge makes it R3's plant). Everything cheap that can refuse runs BEFORE the children are spent: the items scan and pin, the journal and P0, the genome in force,
    the grader's pre-pin, the state copy. The row is written whatever happens, with what was known."""
    cpu0, t0 = time.process_time(), time.time()
    out = Path(a.out)
    label = a.label or "r1"
    run_dir = out / "gate" / label
    run_dir.mkdir(parents=True, exist_ok=True)
    marker = run_dir / MARKER_NAME
    marker.write_text(a.stamp + "\n")
    marker_ns = marker.stat().st_mtime_ns
    status_path = a.status or (str(root / "STATUS.json") if (root / "STATUS.json").exists() else None)
    row: Dict[str, object] = {"kind": "gate", "label": label, "stamp": a.stamp, "status": "RUNNING", "reader_sha256": sha256_file(RESIT_PY), "flags": dict(flags),
                              "root": str(root), "items_root": str(items_root), "code": os.path.realpath(code), "mode_args": {"nudge": a.nudge, "check_turn": a.check_turn}}
    row["live_load"] = {"start": status_reading(status_path)}
    rc = 2
    cap: Optional[int] = None
    try:
        row["code_commit"] = git_info(code)
        genome_text = (items_root / "GENOME.genome").read_text()
        tape_decl = tape_decl_of(genome_text)
        scan = scan_items(items_root, tape_decl)
        if not scan["n_asks"]:
            raise Skipped(f"no sitting ask on the tape of {items_root}")
        sets = {s: v for s, v in scan["sets"].items() if v["begin_seq"] is not None}
        if not sets:
            raise Skipped(f"no `begin` ask on the tape of {items_root}")
        ws = world_seed_of(genome_text)
        marks_json = Path(a.scored) / str(ws) / "fresh" / "marks.json" if ws is not None else None
        scored_pin = {"path": str(marks_json) if marks_json and marks_json.exists() else None,
                      "sha256": sha256_file(marks_json) if marks_json and marks_json.exists() else None}
        pinned_before = (out / "ITEMS.json").exists()
        pin_items(out, scan, scored=scored_pin, world_line_sha=world_scene_line_sha(genome_text), items_root=items_root)
        row["items"] = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"],
                        "sets": scan["sets"], "world_seed": ws, "scored": scored_pin, "pin": "checked" if pinned_before else "written"}
        # the journal: the life's own rows, P0, restarts
        js = scan_journal(items_root / "journal")
        dup = collapse_duplicates(js["answers"])
        row["restart_duplicates"] = dup["restart_duplicates"]
        if dup["divergent"]:
            raise NotGradable(f"NOT GRADABLE: RESTART-DIVERGENT — {len(dup['divergent'])} ask(s) hold two unequal answer rows (first ask seqs {dup['divergent'][:5]})")
        first_begin = min(v["begin_seq"] for v in sets.values())
        row["p0"] = precondition_p0(js["brain_rows"], first_begin)
        # the genome in force at each set's begin ask (AM3), and every epoch's four line hashes as a reading
        per_set: Dict[str, Dict[str, object]] = {}
        for sname, v in sorted(sets.items(), key=lambda kv: kv[1]["begin_seq"]):
            gf = genome_in_force(items_root, js["epochs"], before_seq=int(v["begin_seq"]))
            per_set[sname] = {"epoch": gf["epoch"], "path": str(gf["path"]), "sha256": gf["sha256"], "lines": genome_line_hashes(gf["path"].read_text()),
                              "epoch_row": gf["epoch_row"]}
        eye_keys = ("retina", "gaze", "colour", "brain")
        distinct = {tuple(p["lines"][k] for k in eye_keys) for p in per_set.values()}
        epochs_reading = []
        for k in sorted({0} | {int(e["epoch"]) for e in js["epochs"]}):
            gp = items_root / ("GENOME.genome" if k == 0 else f"GENOME.v{k}.genome")
            if gp.exists():
                epochs_reading.append({"epoch": k, "path": str(gp), "lines": genome_line_hashes(gp.read_text())})
        four_equal = len({tuple(e["lines"][k] for k in eye_keys) for e in epochs_reading}) <= 1
        row["genome"] = {"sets": per_set, "epochs_reading": epochs_reading, "epochs_four_lines_equal": four_equal, "eye_changed": len(distinct) > 1}
        if len(distinct) > 1:
            raise Refused("EYE-CHANGED between the sets' in-force genomes: one brain copy cannot be read under two eyes (an anomaly: EVOLVE cannot move those lines, AM2)")
        genome_path = next(iter(per_set.values()))["path"]
        # the grader: its pin is checked BEFORE any child is spent
        ginfo = grader_info(a.grader_code)
        row["grader"] = {**ginfo, "pin": check_grader_pin(out, ginfo, write=False)}
        # the state: a COPY of state/prev, its prints checked
        copy_dir = run_dir / "copy"
        st = copy_state_prev(root, copy_dir, sleep_s=a.copy_retry_sleep_s)
        row["state"] = {k: st[k] for k in ("source", "last_seq", "t", "prints_ok", "attempts", "files", "prints")}
        row["state"]["copy_dir"] = str(copy_dir)
        # the children
        cache = Path(a.cache) if a.cache else out / "glances.pkl"
        cold = not cache.exists()
        cap = a.cpu_cap_s or (CPU_CAP_COLD_S if cold else CPU_CAP_WARM_S)
        wseed = a.world_seed if a.world_seed is not None else (ws or 0)
        spec = {"code": str(code), "items_root": str(items_root), "tape_decl": tape_decl,
                "states": [{"name": "*", "dir": str(copy_dir), "genome": genome_path}], "out_dir": str(run_dir), "glance_cache": str(cache),
                "check_turn": ({"world_seed": wseed, "n_asks": 3} if a.check_turn else None)}
        if a.nudge is not None:
            spec["nudge"] = {"eps": float(a.nudge), "seed": int(a.nudge_seed)}
        if a.blas_reading:
            spec["blas_reading"] = int(a.blas_reading)
        ach = run_child("answer", spec, run_dir, cpu_cap_s=cap, blas_reading=a.blas_reading)
        require_child_ok(ach, cap)
        ameta = json.loads((run_dir / "answer-meta.json").read_text())
        row["answer_meta"] = ameta
        row["subject"] = {"modules": ameta["modules"], "modules_digest": ameta["modules_digest"], "python": ameta["python"]}
        row["eye_pin"] = ameta["eye_pin"]
        row["turn_check"] = ameta.get("turn_check")
        row["state"].update({k: ameta["states"][0].get(k) for k in ("state_hash", "n_learned", "calibrated_at_load", "calibrated_at_end", "state_hash_end")})
        resit_rows = [json.loads(line) for line in (run_dir / "answers.jsonl").read_text().splitlines() if line.strip()]
        r1a = compare_answers(resit_rows, dup["rows"])
        r1a["n_asks_on_tape"] = scan["n_asks"]
        r1a["unanswered"] = ameta["unanswered"]
        r1a["pass"] = bool(r1a["all_equal"] and r1a["n_resit"] == scan["n_asks"] and not ameta["unanswered"])
        # the grade, by the pinned grader's own function
        gspec = {"grader_code": str(a.grader_code), "items_root": str(items_root), "journal": str(run_dir / "answers.jsonl"), "scored": str(a.scored),
                 "label": label, "genome": str(items_root / "GENOME.genome"), "out_dir": str(run_dir), "m2a_rows": bool(a.m2a_rows)}
        gch = run_child("grade", gspec, run_dir, cpu_cap_s=cap)
        require_child_ok(gch, cap)
        gmeta = json.loads((run_dir / "grade-meta.json").read_text())
        row["grader"]["modules_digest"] = gmeta["modules_digest"]
        row["grader"]["modules"] = gmeta["modules"]
        row["grader"]["pin"] = check_grader_pin(out, {**ginfo, "modules_digest": gmeta["modules_digest"]})
        grade = json.loads((run_dir / "grade.json").read_text())
        row["m6_reading"] = {"M6_pooled": grade.get("M6_pooled"), "read_by": (grade.get("meeting") or {}).get("read_by"),
                             "meeting_seen": (grade.get("meeting") or {}).get("seen")}
        ref = json.loads(Path(a.reference_grade).read_text()) if a.reference_grade else None
        r1b = compare_marks(grade, ref) if ref is not None else {"compared": False, "note": "no --reference-grade given: R1 (b) was NOT RUN"}
        row["cpu"] = {"answer_s": ach["cpu_s"], "grade_s": gch["cpu_s"], "orchestrator_s": round(time.process_time() - cpu0, 3), "cap_s": cap, "cold": cold,
                      "answer_self_s": ameta.get("cpu_s"), "grade_self_s": gmeta.get("cpu_s")}
        row["cpu"]["total_s"] = round(ach["cpu_s"] + gch["cpu_s"] + row["cpu"]["orchestrator_s"], 3)
        row["children"] = {"answer": {k: ach[k] for k in ("rc", "wall_s", "cpu_s", "maxrss_mb")}, "grade": {k: gch[k] for k in ("rc", "wall_s", "cpu_s", "maxrss_mb")}}
        row["memory"] = {"answer_maxrss_mb": ach["maxrss_mb"], "grade_maxrss_mb": gch["maxrss_mb"],
                         "orchestrator_maxrss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)}
        if a.nudge is not None:
            n = ameta["nudge"]
            changed = marks_of_diffs(r1b["diffs"]) if ref is not None and "diffs" in r1b else None
            row["r3"] = {"eps": n["eps"], "seed": n["seed"], "hash_before": n["hash_before"], "hash_after": n["hash_after"], "answers_changed": r1a["n_diff"],
                         "answers_compared": r1a["n_resit"], "marks_changed": changed, "first_diff": r1a["first_diff"]}
            caught = r1a["n_diff"] >= 1 and bool(set(changed or []) & set(R1_MARKS))
            row["status"] = "PLANT CAUGHT" if caught else "FAIL"
            if not caught:
                row["reading"] = ("R3: the plant does not reach the answers or the marks (#228 (a)) — "
                                  f"answers changed {r1a['n_diff']}, marks changed {changed}")
            rc = 0 if caught else 2
        else:
            row["r1a"], row["r1b"] = r1a, r1b
            if not r1a["pass"]:
                row["status"], row["reading"] = "FAIL", "R1 (a) red: a SUBJECT difference — the first differing item is printed with both rows (the first suspect is the glance, not the brain)"
            elif ref is None:
                row["status"], row["reading"] = "PARTIAL", "R1 (a) passed; R1 (b) was NOT RUN (no --reference-grade)"
            elif not r1b["equal"]:
                row["status"], row["reading"] = "FAIL", "R1 (a) green and (b) red: GRADER DRIFT — the pinned grader's marks differ from the reference's"
            else:
                row["status"], row["reading"], rc = "PASS", f"R1: {r1a['n_equal']} of {scan['n_asks']} rows equal, {len(r1b['marks_compared'])} mark groups equal to 1e-12", 0
    except NotGradable as e:
        row["status"], row["reason"] = "NOT GRADABLE", str(e)
    except Skipped as e:
        row["status"], row["reason"] = "SKIPPED", str(e)
    except ResitError as e:
        row["status"], row["reason"] = "REFUSED", str(e)
    except Exception as e:                      # a defect of the reader: still a row, with the traceback, and exit 2 — never a silent half-run
        import traceback
        row["status"], row["reason"] = "ERROR", f"{type(e).__name__}: {e}"
        row["traceback"] = traceback.format_exc()[-3000:]
    finally:
        row["live_load"]["end"] = status_reading(status_path)
        row["nothing_written"] = dict(newer_than(_outermost([root, items_root, code]), marker_ns), checked=True)
        row["wall_s"] = round(time.time() - t0, 3)
        atomic_write(run_dir / "gate.json", json.dumps(row, indent=1, sort_keys=True, default=str) + "\n")
    short = {"status": row["status"], "gate_json": str(run_dir / "gate.json")}
    for k in ("reason", "reading"):
        if row.get(k):
            short[k] = row[k]
    if "r1a" in row:
        short["r1a"] = {k: row["r1a"][k] for k in ("n_resit", "n_equal", "n_diff", "n_missing_life_row")}
        short["r1b"] = {k: row["r1b"].get(k) for k in ("equal", "n_leaves")}
    print(json.dumps(short, default=str))
    return rc


if __name__ == "__main__":
    sys.exit(main())
