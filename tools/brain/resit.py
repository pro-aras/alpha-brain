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

import bisect
import collections
import hashlib
import json
import math
import os
import re
import shutil
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


def check_flags(dont_write_bytecode: int, isolated: int, env: Mapping[str, str]) -> Dict[str, object]:
    """§1.0: the orchestrator refuses to run unless python was started with -B (a cold import of the grader would write .pyc files INTO the life's tree)
    and -I (PYTHON* variables could put master's tree first on sys.path and shadow the life's modules), and unless the two BLAS pins are 1 (a brain
    state's float bits depend on the BLAS thread count, #246 (8)). Both are recorded in the row."""
    problems: List[str] = []
    if not dont_write_bytecode:
        problems.append("python was not started with -B (a cold import of tools/brain/grade_life.py would write .pyc files into the life's tree)")
    if not isolated:
        problems.append("python was not started with -I (a PYTHON* variable could put another tree first on sys.path)")
    for var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
        if env.get(var) != "1":
            problems.append(f"{var} is {env.get(var)!r}, not '1' (the life's own unit pins it; a brain state's float bits depend on it)")
    if problems:
        raise ResitError("refused: " + "; ".join(problems))
    return {"dont_write_bytecode": True, "isolated": True, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"}


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
