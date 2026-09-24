# edit: Claude (Fable 5.1), 2026-09-23 03:43 +0400 — RE-PIN at ALPHA 4 integration: G's declared hash-law change (state_hash over the live prefix of alive/misfires) moved every genome's digest once; the new digest read identically from the genome suite, the creature suite and gate 2 on the merged tree 6ff2204 (three witnesses).
#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-21 20:50 +0400 — G4-2 pin moved to the live-block state_hash digest (Builder F, g5-repairs merged into g5-integration); the old digest d4b5c6b8… is the legacy road Organism.load still accepts.
# edit: Claude (Fable 5.1), 2026-09-19 21:29 +0400 — G4's INDEPENDENT gate checker (docs/G4-PREREG.md §4; SOLUTIONS #214: the orchestrator keeps
# its own checker with a positive and a negative control). Runs G4-1 (writer sweep + planted offender), G4-2 (mind parity vs the pin
# read at git 9a36475 + a swapped-canvas control) and G4-3 (replay identity on a Mind-written journal + a planted payload flip).
# Every run uses a FRESH temporary root (#212). Exit 0 iff every gate and every control reads as the PREREG says.
"""usage: python3 tools/gate_g4.py [--genome genome/G4-skeleton.genome] [--tree /data/dev/genome] [--only 1,2,3]"""
from __future__ import annotations

import argparse, ast, io, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from typing import Optional     # FIX 2: `_resolve` was already annotated `-> Optional[str]` with no import (lazy under `from __future__ import annotations`)

import numpy as np

PIN = "44f6fa81f9c21c549036a44f89dfb04276cd07aaec9565ccbd13ef75a11bcc00"   # G4-2, read 2026-09-19 21:3x at 9a36475
# edit: Claude (Sonnet 5, LIFE builder E), 2026-09-22 20:43 +0400 — L-5 (docs/briefs/LIFE-E-THINK-THREAD.md
# item 4): "extend the sweep's walk to the think module if it does not reach it" -- it did not (the walk
# was creature/world_maker.py/ask.py/tape.py + creature/senses/*.py; the think thread's own module,
# creature/think_thread.py, is none of those, so a write planted there would have gone uncaught). Added
# here, not to creature/senses/ (it is not a sense) -- the sweep's SECOND check (any open/write_text/save/
# etc. call whose target names a forbidden dir) applies to every file in this list regardless of the
# "is_sense" gate that guards ONLY the first check (imports Organism); the think module legitimately
# imports Organism (it builds a read-only shadow of one, genome.machinery.Organism/Area, to reuse
# Organism.recall_many/genome.questions.build_ledgers verbatim against a frozen copy -- never the live
# organism), so it deliberately does NOT get the "is_sense" treatment, only the writer check.
# edit: Claude (Opus 5.5, A4 ladder builder COST), 2026-09-23 11:59 +0400 — A4L-COST: genome/witness.py, the sparse per-row witness, writes NO file — the sweep reaches it (its planted offender: tests/genome/test_a4l_cost_writer_sweep.py).
# edit: Claude (Opus 5.5, A4 ladder builder VOICE), 2026-09-23 11:46 +0400 — A4L-VOICE: genome/voice.py (the world's voice) is walked by the writer check too (tests/creature/test_writer_sweep.py plants an offender shaped like it).
SENSE_FILES = ["creature/world_maker.py", "creature/ask.py", "creature/tape.py", "creature/think_thread.py", "genome/witness.py", "genome/voice.py"]
FORBIDDEN_DIRS = ("state", "journal", "memory")


def _literal_text(node) -> str:
    """Every string piece reachable in a call's first argument (literals, f-strings, joins)."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return " ".join(out)


# edit: Claude (Sonnet 5, ALPHA4 builder I), 2026-09-23 01:04 +0400 — a gap found while landing the web
# door's OWN planted-offender test (ALPHA4-PREREG.md's instruction: "a planted offender: a web sense that
# writes memory"): the two-step form every real sense module here actually uses for its cursor writes —
# `seen_path = Path(root) / "folder" / "SEEN.json"` on one line, `seen_path.write_text(...)` later
# (folder.py, game.py, sit.py, this builder's own grade.py/web.py) — was INVISIBLE to this sweep. `target`
# was built from `_literal_text(fn.value)`, a bare walk of the RECEIVER expression; for `seen_path.write_
# text(...)`, `fn.value` is just the `Name` node `seen_path`, which carries no string constant of its own
# — the path text lives in a SEPARATE, earlier assignment this walk never looked at. A same-module plant
# in exactly this shape (`p = Path(root) / 'memory' / 'x.json'; p.write_text('{}')`) sailed through with
# ZERO offenders (verified: the INLINE form, `(Path(root)/'memory'/'x.json').write_text(...)`, was already
# caught — only the two-step, variable-indirected form was blind). tests/creature/test_writer_sweep.py's
# OWN independent sweep (`find_offenders`) already resolves this via `_build_env`/`_flatten`; `_resolve`
# below is the same technique, ported here so gate_g4.py's sweep — the one every builder's landing runs
# under `tools/gate_g5_landing.sh` — has the SAME resolving power, not a narrower one. Additive only: every
# node shape this function did not specially handle before still falls through to the exact same
# `_literal_text` walk, so no previously-caught offender or previously-clean file changes verdict; the six
# real sense modules (folder/game/sit/body_sense/hands/ear — every one already using this two-step
# pattern) were re-swept after this change and stayed clean (tests.creature.test_writer_sweep.
# TestWriterSweepG41.test_the_real_web_and_grade_modules_pass_both_sweeps and a manual re-run of gate1
# below, both green).
def _resolve(node, env: dict) -> Optional[str]:
    """Best-effort static text of a path-like expression: literals/f-strings (falls through to
    `_literal_text`), `a / b` chains, `Path(...)` calls, `.attr` chains, and a same-module bare variable
    name resolved through `env` (built by `_build_env`, below)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left, right = _resolve(node.left, env), _resolve(node.right, env)
        return None if left is None and right is None else f"{left or ''}/{right or ''}"
    if isinstance(node, ast.Call):
        callee = node.func
        name = callee.id if isinstance(callee, ast.Name) else (callee.attr if isinstance(callee, ast.Attribute) else None)
        if name == "Path" and node.args:
            return _resolve(node.args[0], env)
        return _literal_text(node)   # a call shape not specially understood -- the plain walk, unchanged
    if isinstance(node, ast.Attribute):
        return _resolve(node.value, env)
    return _literal_text(node)       # anything else -- the plain walk, unchanged (byte-identical fallback)


# edit: Claude (Fable 5.1), 2026-09-23 17:00 +0400 — SIT-ATOMIC-SWEEP-0923 FIX 2 (docs/briefs/SEAM5-WITNESS-SOUND-REPORT.md item 5): the env is
# built PER FUNCTION SCOPE. Before, ONE flat env was built over the whole module (`ast.walk` over every Assign, last write wins), so a
# same-named local in a DIFFERENT function overwrote a leak's binding: the seam-5 builder's own edit bound an unrelated local `p`, COST's
# planted leak (`p = root/'state'/'witness.json'; p.write_text(...)`) resolved to the wrong text, and BOTH sweeps read [] — a negative control
# that had stopped controlling (#91's class). Now every def/lambda gets its own env, seeded from the enclosing scope's finished env (module-
# level names stay visible inside functions, as at run time) and taking only its OWN simple assignments, in source order; a sibling's locals
# never enter it. Class bodies are left transparent (a widening only: more names visible, never fewer). `_resolve` is unchanged. Mirrors
# tests/creature/test_writer_sweep.py's `_scope_map`/`_build_env` exactly; the planted control (two functions, one binding `p` innocently,
# the other binding `p` to a forbidden path and writing through it, in BOTH orders) is
# tests.creature.test_writer_sweep.TestWriterSweepG41.test_a_leak_shadowed_by_a_same_named_local_in_another_function_is_caught_by_both_sweeps.
_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def _scope_map(tree: ast.AST) -> dict:
    """node -> its nearest enclosing function scope (the Module node for top-level code). A def/lambda node itself belongs
    to the scope it is written in; everything under it belongs to the def (its decorators/defaults included — a
    simplification that can only widen a name's visibility, never narrow it)."""
    scope_of: dict = {tree: tree}

    def visit(node, scope):
        for child in ast.iter_child_nodes(node):
            scope_of[child] = scope
            visit(child, child if isinstance(child, _SCOPE_NODES) else scope)

    visit(tree, tree)
    return scope_of


def _build_env(tree: ast.AST, scope_of: Optional[dict] = None) -> dict:
    """`{scope_node: name -> resolved path text}` — one env for the Module and one for every def/lambda, from simple
    `x = <expr>` assignments (last write wins WITHIN a scope, in source order — still not real dataflow, adequate for this
    codebase's straight-line sense modules). A def's env starts as a copy of its enclosing scope's COMPLETE env, then takes
    the def's own assignments; a sibling function's locals never reach it."""
    scope_of = scope_of if scope_of is not None else _scope_map(tree)
    own: dict = {}
    assigns = (n for n in ast.walk(tree) if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name))
    for node in sorted(assigns, key=lambda n: (n.lineno, n.col_offset)):
        own.setdefault(scope_of[node], []).append(node)
    envs: dict = {}

    def env_of(scope) -> dict:
        if scope in envs:
            return envs[scope]
        env = {} if scope is tree else dict(env_of(scope_of[scope]))     # the enclosing scope's finished env, copied
        envs[scope] = env
        for node in own.get(scope, []):
            text = _resolve(node.value, env)
            if text is not None:
                env[node.targets[0].id] = text
        return env

    env_of(tree)
    for node in ast.walk(tree):
        if isinstance(node, _SCOPE_NODES):
            env_of(node)
    return envs


def sweep(paths) -> list:
    offenders = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        tree = ast.parse(p.read_text(), filename=str(p))
        scope_of = _scope_map(tree)
        envs = _build_env(tree, scope_of)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                is_sense = ("senses" in p.parts) or p.name == "world_maker.py"
                if is_sense and any("Organism" == n or n.endswith("machinery") and isinstance(node, ast.ImportFrom) and any(a.name == "Organism" for a in node.names) for n in names):
                    offenders.append((str(p), node.lineno, "imports Organism (a sense module)"))
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
                if name in ("open", "write_text", "write_bytes", "save", "savez", "savez_compressed", "replace", "rename"):
                    env = envs[scope_of[node]]          # FIX 2: the env of THIS call's own scope, not one flat module-wide map
                    target = (_resolve(node.args[0], env) or "") if node.args else ""
                    if name == "open" and node.args and len(node.args) > 1:
                        target += " " + _literal_text(node.args[1])
                    if isinstance(fn, ast.Attribute):
                        target += " " + (_resolve(fn.value, env) or "")
                    mode = ""
                    for kw in node.keywords:
                        if kw.arg == "mode":
                            mode = _literal_text(kw.value)
                    if name == "open" and len(node.args) > 1:
                        mode += _literal_text(node.args[1])
                    writes = name != "open" or any(c in mode for c in "wax")
                    if writes and any(d in target for d in FORBIDDEN_DIRS):
                        offenders.append((str(p), node.lineno, f"{name}() under a forbidden dir: {target.strip()[:60]}"))
    return offenders


def gate1(tree: Path) -> bool:
    files = [tree / f for f in SENSE_FILES] + sorted((tree / "creature" / "senses").glob("*.py"))
    off = sweep(files)
    print(f"G4-1 writer sweep over {len(files)} files: {len(off)} offenders")
    for o in off:
        print("   ", o)
    with tempfile.TemporaryDirectory() as d:
        plant = Path(d) / "offender.py"
        plant.write_text("from pathlib import Path\n"
                         "def f(root):\n    with open(root / 'state' / 'organism.npz', 'wb') as h:\n        h.write(b'x')\n")
        caught = sweep([plant])
        print(f"G4-1 control: planted offender {'CAUGHT' if caught else 'MISSED'}")
        # edit: Claude (Opus 5.5, A4 ladder builder LANG), 2026-09-23 11:34 +0400 — A4L-LANG (docs/briefs/A4L-LANG.md, gates): the chat
        # sense's planted offender — a chat-shaped sense (creature/senses/chat.py's own signature and its own two-step
        # cursor style) that writes its SEEN cursor under root/state/ instead of root/chat/. The real chat.py is in the
        # walk above (creature/senses/*.py); this plant proves the walk would see it misbehave.
        plant_chat = Path(d) / "senses" / "chat_offender.py"; plant_chat.parent.mkdir(parents=True, exist_ok=True)
        plant_chat.write_text("from pathlib import Path\n"
                              "def sense(publish, stop_event, root, in_dir=None, canvas=128, letters=8, period=1.0):\n"
                              "    seen_path = Path(root) / 'state' / 'SEEN.json'\n"
                              "    seen_path.write_text('[]')\n")
        caught_chat = sweep([plant_chat])
        print(f"G4-1 control: the chat sense's planted offender {'CAUGHT' if caught_chat else 'MISSED'}")
    return not off and bool(caught) and bool(caught_chat)


def _png(rgb) -> bytes:
    from PIL import Image
    b = io.BytesIO(); Image.fromarray(rgb).save(b, format="PNG"); return b.getvalue()


def build_tape(root: Path, genome, canvases, tree: Path):
    sys.path.insert(0, str(tree))
    from creature.tape import Tape
    tape = Tape(root)
    for i, (thing, rgb, _truth) in enumerate(canvases):
        m = f"m{i}"
        tape.publish("ear", thing.encode(), {"moment": m, "source": "maker", "word": thing}, "txt", at=f"2026-09-19T00:00:{i % 60:02d}.{i:03d}Z")
        tape.publish("eye", _png(rgb), {"moment": m, "source": "maker"}, "png", at=f"2026-09-19T00:00:{i % 60:02d}.{i:03d}Z")
    return tape


def consume_all(root: Path, genome_path: Path, tree: Path) -> str:
    from creature.mind import Mind
    from creature.tape import read_tape
    mind = Mind(genome_path, root)
    for row in read_tape(root):
        mind.consume(row)
    h = mind.org.state_hash()
    if hasattr(mind, "close"):
        mind.close()
    return h


def gate2(tree: Path, genome_path: Path) -> bool:
    sys.path.insert(0, str(tree))
    from genome.machinery import parse_genome
    from genome import run_g1
    g = parse_genome(genome_path.read_text())
    things, arr2, dev, held, a2, plant, shuffle_words, _n = run_g1.toy_streams(g, 5)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "run"
        build_tape(root, g, dev, tree)
        h = consume_all(root, genome_path, tree)
    ok = h == PIN
    print(f"G4-2 mind parity: {h[:16]}… vs pin {PIN[:16]}… → {'PASS' if ok else 'FAIL'}")
    swapped = list(dev); swapped[0], swapped[1] = swapped[1], swapped[0]
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "run"
        build_tape(root, g, swapped, tree)
        h2 = consume_all(root, genome_path, tree)
    ctl = h2 != PIN
    print(f"G4-2 control (two canvases swapped): {h2[:16]}… → {'CAUGHT' if ctl else 'MISSED'}")
    return ok and ctl


def gate3(tree: Path, genome_path: Path) -> bool:
    sys.path.insert(0, str(tree))
    from genome.machinery import parse_genome
    from genome import run_g1
    g = parse_genome(genome_path.read_text())
    things, arr2, dev, *_ = run_g1.toy_streams(g, 5)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "run"
        build_tape(root, g, dev[:120], tree)
        consume_all(root, genome_path, tree)
        journals = sorted((root / "journal").glob("*.jsonl"))
        live = Path(d) / "live-journal.jsonl"
        live.write_bytes(b"".join(j.read_bytes() for j in journals))
        tapes = sorted((root / "tape").glob("*.jsonl"))
        tape_file = Path(d) / "tape-all.jsonl"
        tape_file.write_bytes(b"".join(t.read_bytes() for t in tapes))
        # the replay tool resolves payload paths relative to the tape's root: keep the copy beside the payload dir
        tape_in_root = root / "tape" / "ALL.jsonl"; tape_in_root.write_bytes(tape_file.read_bytes())
        out1 = Path(d) / "replay1"
        r = subprocess.run([sys.executable, "-m", "creature.replay", "--genome", str(genome_path), "--tape", str(tape_in_root),
                            "--against", str(live), "--out", str(out1)], cwd=tree, capture_output=True, text=True)
        print(f"G4-3 replay identity: exit {r.returncode} → {'PASS' if r.returncode == 0 else 'FAIL'}  {r.stdout.strip()[-160:]} {r.stderr.strip()[-200:]}")
        ok = r.returncode == 0
        # the plant: flip one byte of one payload in a COPY of the root
        root2 = Path(d) / "run2"; shutil.copytree(root, root2)
        rows = [json.loads(l) for l in (root2 / "tape" / "ALL.jsonl").read_text().splitlines()]
        eye = [x for x in rows if x["sense"] == "eye"][30]
        pp = root2 / "tape" / eye["payload"]
        from PIL import Image
        arr = np.array(Image.open(pp).convert("RGB"))
        cy, cx = dev[30][2]["cell"]                      # the thing's own cell (the truth, held by the checker, never on the tape)
        y0, x0 = int((cy + 0.5) * 8) - 12, int((cx + 0.5) * 8) - 12
        y0, x0 = max(0, min(y0, 104)), max(0, min(x0, 104))
        arr[y0:y0 + 24, x0:x0 + 24] = 255 - arr[y0:y0 + 24, x0:x0 + 24]
        Image.fromarray(arr).save(pp, format="PNG")
        out2 = Path(d) / "replay2"
        r2 = subprocess.run([sys.executable, "-m", "creature.replay", "--genome", str(genome_path), "--tape", str(root2 / "tape" / "ALL.jsonl"),
                             "--against", str(live), "--out", str(out2)], cwd=tree, capture_output=True, text=True)
        caught = r2.returncode != 0
        print(f"G4-3 control (payload byte flipped at seq {eye['seq']}): exit {r2.returncode} → {'CAUGHT' if caught else 'MISSED'}  {(r2.stdout + r2.stderr).strip()[-200:]}")
    return ok and caught


# edit: Claude (Fable 5.1), 2026-09-21 11:42 +0400 — G4-6 (PREREG §4: «G4-3 re-run PASS with two senses on the tape»): runs Builder C's
# self-contained two-sense replay test (tests/creature/test_g46_two_senses.py) as a subprocess in the tree under test and
# requires BOTH its exit 0 AND its own printed evidence line (row counts per source with folder rows > 0 and the seq of the
# caught divergence) — a green exit with no evidence line is a FAIL (a suite can pass by skipping; #229).
def gate6(tree: Path) -> bool:
    r = subprocess.run([sys.executable, "-m", "unittest", "tests.creature.test_g46_two_senses"], capture_output=True, text=True, cwd=tree)
    out = r.stdout + r.stderr
    m = re.search(r"G4-6 row counts by source: (\{.*?\}); caught divergence planted at seq (\d+)", out)
    ok = r.returncode == 0 and m is not None
    folder_rows = 0
    if m:
        try:
            folder_rows = int(re.search(r"'folder': (\d+)", m.group(1)).group(1))
        except Exception:
            folder_rows = 0
    ok = ok and folder_rows > 0
    print(f"G4-6 two senses on one tape: exit {r.returncode}, evidence {'present' if m else 'ABSENT'}, folder rows {folder_rows} → {'PASS' if ok else 'FAIL'}  {(m.group(0) if m else out.strip()[-200:])}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default="/data/dev/genome")
    ap.add_argument("--genome", default="genome/G4-skeleton.genome")
    ap.add_argument("--only", default="1,2,3,6")
    a = ap.parse_args()
    tree = Path(a.tree).resolve(); genome_path = (tree / a.genome).resolve()
    os.chdir(tree)
    results = {}
    for k in a.only.split(","):
        results[k] = {"1": gate1, "2": lambda t: gate2(t, genome_path), "3": lambda t: gate3(t, genome_path), "6": gate6}[k](tree)
    print("G4 gates:", {k: ("PASS" if v else "FAIL") for k, v in results.items()})
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
