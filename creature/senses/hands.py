# edit: Claude (Sonnet 5, LIFE builder F), 2026-09-22 19:39 +0400 — LIFE-F-HANDS-TOUCH-SMELL.md item 2
# (docs/organs/NEXT-LIFE-PLAN-2026-09-22.md §4 L-12; docs/organs/MOTOR-HANDS.md G-MOT-4).
"""creature/senses/hands.py — the hands door: the creature runs a chosen program from the shelf through
Alpha 2's jail (`/data/dev/alpha3/hands/jail_run`) and SEES what its hands made.

Protocol (the SAME act-file pattern `creature/senses/game.py` uses, copied per the brief's own READ FIRST
line and builder D's report): the mind's THINK step (creature/mind.py's 'hands' pool kind) writes
`run/hands/ACT` = `{"seq", "program", "at"}` atomically when it chooses to run; this sense thread polls for
a `seq` newer than the last one it served, runs that program through the jail with a FRESH scratch
directory (#212: a measurement run gets a fresh root) and `ro_root` = the shelf (never the creature's own
tree), decodes stdout with `errors="replace"` (#230: a strict decode of bytes the mind did not write is
exactly how a 400-byte truncation aborted the organism 90 times), renders the decoded text to a 128x128
grey canvas through the SAME `_png_bytes` + tape-publish road `creature/senses/folder.py`/`creature/senses/
game.py` use for every other picture on this tape, and publishes in the tape's own order law (PREREG §2.2):
an `eye` row, then an `outcome` row, then a `touch` row. `run/hands/CURSOR` advances only AFTER all three
rows are durable (#230's second half: a persisted cursor turned a data crash into a crash LOOP).

G-MOT-4's three preconditions, each a line of code (not a judgement):
  1. `errors="replace"` decoding of stdout/stderr — never a strict decode of a jail's arbitrary output.
  2. The cursor advances only after the rows it names are durable — `_load_cursor`/the write at the end
     of `_run_one`, matching `creature/senses/folder.py`'s own SEEN-set convention exactly.
  3. A FRESH scratch per act, `ro_root` = the shelf, never the creature's own tree — `_fresh_scratch`,
     removed after the rows are durable (#236: 13 GB of leaked test roots is the warning this avoids).

The OUTCOME row's `act` field is the PROGRAM's OWN NAME, not the literal string "run" the brief's prose
shows — `creature/mind.py:_record_reflex`'s per-act running-mean expectation is bucketed by this field, and
per-program predictability (the whole point of the positive/negative controls: "a program whose output the
MIND CAN predict" vs "CANNOT predict") needs a per-program bucket, not one shared by every program that
happens to run. This is the EXACT precedent `creature/senses/game.py` already set (the game's outcome rows
carry the BabyAI action name, not one of `declared["ACT"]["verbs"]`) and is tagged `in_vocab: False` the
same way. `got` is `_got_fingerprint(stdout)`, a deterministic float in [0, 1) from the exact stdout bytes
(crc32); `expected`/`residual` are left for `Mind._record_reflex`'s own per-program running mean to derive
(never fabricated here) — the positive control's stdout is byte-identical every run, so its fingerprint
converges and the residual settles to 0 after its second run; the negative control's stdout changes every
run (it reads a value this module itself writes into the fresh scratch, see `_negative_control_input`), so
its fingerprint essentially never repeats and the residual stays > 0.

A pure SENSE (G4-1's writer sweep): it never touches state/journal/memory, never imports Organism/
machinery. Never re-run at replay (`creature.replay` never imports this module or `subprocess` — a grep-
level structural proof, tests/creature/test_mind_chooses_hands.py::TestReplayNeverCallsTheJail): the
mind's DECISION (which program, when) is a pure function of (genome, seed, tape) recorded as tape rows;
the RUN's outcome (a jail's stdout/exit/timing) is not reproducible (pids, clocks, scheduling) and is
never asked to be — only the recorded rows are read back.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import zlib
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

# The arming gate (creature/senses/folder.py's own C2/C3 discipline): a genome line arms nothing until the
# code carrying it exists; explicit CLI overrides stay available for tests regardless of this constant.
HANDS_DOOR_GATED = True

CANVAS = 128
GRID_CHARS = 32          # 32 lines x <=32 chars, each a 4x4 pixel block -> 128x128 (CANVAS)
BLOCK = CANVAS // GRID_CHARS
JAIL_TIMEOUT_SLACK_S = 10.0   # belt-and-suspenders on top of jail_run's OWN wall-clock alarm (it always terminates by `wall` seconds)


def _png_bytes(rgb: np.ndarray) -> bytes:
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.fromarray(rgb, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _render_ascii(text: str, side_chars: int = GRID_CHARS, block: int = BLOCK) -> np.ndarray:
    """Text -> a (side_chars*block, side_chars*block, 3) uint8 grey canvas: each character a `block`x
    `block` pixel square, '#' -> ink (255), anything else -> ground (0) -- BODY-SENSES.md/the plan's own
    words, "each character a 4x4 block; # ink". Lines beyond `side_chars` are dropped, lines/chars short of
    it are padded with space (ground); this makes the function total on ANY decoded text, including a
    control program's one-line output or an empty string."""
    lines = text.split("\n")
    lines = (lines + [""] * side_chars)[:side_chars]
    grid = np.zeros((side_chars, side_chars), dtype=np.uint8)
    for y, line in enumerate(lines):
        line = (line + " " * side_chars)[:side_chars]
        for x, ch in enumerate(line):
            if ch == "#":
                grid[y, x] = 255
    canvas = np.repeat(np.repeat(grid, block, axis=0), block, axis=1)
    return np.repeat(canvas[:, :, None], 3, axis=2)


def _got_fingerprint(stdout: bytes) -> float:
    """A deterministic float in [0, 1) from the EXACT stdout bytes (crc32/2**32) -- the same bytes give the
    same fingerprint always (the positive control's constant output converges to residual 0 after its
    second run, via Mind._record_reflex's own per-act running mean); different bytes give a different
    fingerprint essentially always (the negative control's ever-changing input keeps the residual > 0)."""
    return float(zlib.crc32(stdout) & 0xFFFFFFFF) / float(0x100000000)


def _manifest(program_path: Path) -> Dict[str, Optional[str]]:
    """The program's own first-line comment: `# shape: <thing>` or `# control: <kind>`. Neither present ->
    both None (a malformed shelf entry is not fatal to the thread; it simply carries no manifest tag)."""
    try:
        first_line = program_path.read_text(errors="replace").splitlines()[0]
    except (OSError, IndexError):
        return {"shape": None, "control": None}
    line = first_line.strip()
    if line.startswith("# shape:"):
        return {"shape": line[len("# shape:"):].strip(), "control": None}
    if line.startswith("# control:"):
        return {"shape": None, "control": line[len("# control:"):].strip()}
    return {"shape": None, "control": None}


def _load_cursor(cursor_path: Path) -> int:
    if not cursor_path.exists():
        return -1
    try:
        t = cursor_path.read_text().strip()
        return int(t) if t else -1
    except (OSError, ValueError):
        return -1


def _load_act(act_path: Path) -> Optional[dict]:
    try:
        return json.loads(act_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _tape_row_count(root: Path, tape_dirname: str = "tape") -> int:
    """The negative control's own unpredictable input (BODY-SENSES.md §4.6/MOTOR-HANDS.md G-MOT-4's own
    words: "RAISE if the maker has no WINDOW.txt: then the negative control reads the tape's row count
    instead" — RAISED in the report: `creature/world_maker.py` has no such file). A full recount of every
    day-file's lines; acceptable at rung 1's cadence (one hands act every few seconds to minutes against a
    recount costing low tens of ms even at six figures of rows) — a cost worth watching if the tape grows
    far larger, named in the report, not hidden."""
    n = 0
    tape_dir = Path(root) / tape_dirname
    if not tape_dir.exists():
        return 0
    for f in tape_dir.glob("*.jsonl"):
        try:
            with f.open() as fh:
                for _ in fh:
                    n += 1
        except OSError:
            continue
    return n


def _fresh_scratch(scratch_root: Path) -> Path:
    """#212: a measurement run gets a FRESH root. One tempdir per act, under the creature's own
    `run/hands/scratch/` (never the shelf, never the creature's tree) -- the caller removes it after the
    rows it produced are durable (#236: 13 GB of leaked test roots on this box is the standing warning)."""
    scratch_root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="act-", dir=str(scratch_root)))


def _negative_control_input(root: Path) -> str:
    return str(_tape_row_count(root))


def run_in_jail(jail_path: Path, shelf_dir: Path, program_path: Path, scratch: Path,
                 cpu: int, mem: int, wall: int, input_text: Optional[str] = None) -> Dict[str, object]:
    """One jailed run of `program_path` (must live under `shelf_dir` -- the jail's own `ro_root`). Returns
    `{"stdout": bytes, "stderr": bytes, "exit": int, "dt_ms": float, "timed_out": bool}`. `input_text`, when
    given, is written to `scratch/INPUT.txt` BEFORE the run so a program that reads `./INPUT.txt` (its cwd
    is `scratch`, the jail's own `rw_scratch`) sees it -- the negative control's own road (Landlock grants
    reads only beneath `ro_root`/`/usr`/`/etc` and rw beneath `scratch`; a program cannot reach anything the
    world-maker wrote directly, proven live 2026-09-22 by hand before this function was written)."""
    if input_text is not None:
        (scratch / "INPUT.txt").write_text(input_text)
    argv = [str(jail_path), str(shelf_dir), str(scratch), str(int(cpu)), str(int(mem)), str(int(wall)),
            "--", "python3", "-I", "-B", str(program_path)]
    t0 = time.perf_counter()
    timed_out = False
    try:
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(scratch),
                               timeout=float(wall) + JAIL_TIMEOUT_SLACK_S)
        stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        # jail_run's OWN wall-clock alarm should always terminate the child within `wall` seconds and
        # return 124 -- this branch is the belt-and-suspenders case where jail_run itself somehow hung;
        # subprocess.run() has already killed the process group by the time this exception is raised.
        timed_out = True
        stdout = e.stdout or b""
        stderr = e.stderr or b""
        exit_code = 124
    dt_ms = (time.perf_counter() - t0) * 1000.0
    return {"stdout": stdout, "stderr": stderr, "exit": int(exit_code), "dt_ms": dt_ms, "timed_out": timed_out}


def _shelf_programs(shelf_dir: Path) -> List[Path]:
    """Every `*.py` directly under `shelf_dir`, sorted bytewise by filename -- the same deterministic order
    rule folder.py/ear.py use for their own directories."""
    if not shelf_dir.exists():
        return []
    return sorted(shelf_dir.glob("*.py"))


def _run_one(publish: Callable, root: Path, jail_path: Path, shelf_dir: Path, program: str,
             cpu: int, mem: int, wall: int, seq_hint: int) -> None:
    """Runs ONE chosen program end to end: fresh scratch, jail, decode (errors="replace"), render, publish
    eye -> outcome -> touch (the tape's order law, PREREG §2.2), remove the scratch. Never raises: an
    exception here would restart this WHOLE sense thread (creature/body.py's SenseThread contract) and
    potentially re-serve a stale ACT; every failure mode this function can hit (a missing program file, a
    jail invocation error) is caught and turned into a row instead."""
    program_path = shelf_dir / f"{program}.py"
    scratch_root = Path(root) / "hands" / "scratch"
    scratch = _fresh_scratch(scratch_root)
    try:
        manifest = _manifest(program_path)
        input_text = _negative_control_input(root) if manifest.get("control") == "negative" else None
        result = run_in_jail(jail_path, shelf_dir, program_path, scratch, cpu, mem, wall, input_text=input_text)
        stdout_text = result["stdout"].decode("utf-8", errors="replace")           # G-MOT-4 precondition 1
        stderr_text = result["stderr"].decode("utf-8", errors="replace")
        rgb = _render_ascii(stdout_text)
        sha = hashlib.sha256(result["stdout"]).hexdigest()
        moment = "h" + sha[:12]

        eye_meta = {"moment": moment, "source": "hands", "act": "run", "program": program,
                    "shape": manifest.get("shape"), "control": manifest.get("control"),
                    "exit": result["exit"], "stderr": stderr_text[:2000],
                    # G-MOT-4's own crash-control refusal test names the DECODED text explicitly ("a row
                    # with U+FFFD") -- kept on the row (truncated) so a reader/exam can see it without
                    # re-decoding the rendered canvas's pixels back into characters.
                    "stdout_text": stdout_text[:2000]}
        publish("eye", _png_bytes(rgb), eye_meta, "png")

        got = _got_fingerprint(result["stdout"])
        outcome_payload = json.dumps({"act": program, "got": got}).encode("utf-8")
        outcome_meta = {"moment": moment, "source": "hands", "act": program, "program": program,
                        "expected": None, "got": got, "residual": None, "act_seq": seq_hint,
                        "exit": result["exit"], "timed_out": result["timed_out"]}
        publish("outcome", outcome_payload, outcome_meta, "json")

        rate = (len(result["stdout"]) / result["dt_ms"]) if result["dt_ms"] > 0 else 0.0
        touch = np.array([float(result["exit"]), float(rate), 1.0 if result["timed_out"] else 0.0,
                           0.0, float(len(result["stdout"]))], dtype=np.float32)
        publish("touch", touch.tobytes(), {"moment": moment, "source": "hands", "program": program}, "f32")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def sense(publish: Callable, stop_event, root: Path, jail_path: Path, shelf_dir: Path,
          cpu: int = 10, mem: int = 512, wall: int = 20, poll_period: float = 0.2) -> None:
    """The sense thread body a `creature.body.SenseThread` runs. Waits for `run/hands/ACT` (written by the
    mind's THINK step, creature/mind.py's `_maybe_think`) to carry a `seq` strictly greater than the
    persisted cursor, runs that program, publishes its rows, then persists the cursor -- ONLY after the
    rows are durable (#230)."""
    root = Path(root)
    jail_path = Path(jail_path)
    shelf_dir = Path(shelf_dir)
    act_path = root / "hands" / "ACT"
    cursor_path = root / "hands" / "CURSOR"
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    last_seq = _load_cursor(cursor_path)

    while not stop_event.is_set():
        data = _load_act(act_path)
        if data is not None:
            try:
                seq = int(data["seq"])
                program = str(data["program"])
            except (KeyError, TypeError, ValueError):
                seq = None
                program = None
            if seq is not None and seq > last_seq and program is not None:
                _run_one(publish, root, jail_path, shelf_dir, program, cpu, mem, wall, seq_hint=seq)
                last_seq = seq
                cursor_path.write_text(str(last_seq))   # AFTER the rows are durable -- the cursor law (#230)
        stop_event.wait(poll_period)
