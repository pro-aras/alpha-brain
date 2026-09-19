#!/usr/bin/env python3
# edit: Claude (Fable 5.1), 2026-09-19 21:29 +0400 — G4's INDEPENDENT gate checker (docs/G4-PREREG.md §4; SOLUTIONS #214: the orchestrator keeps
# its own checker with a positive and a negative control). Runs G4-1 (writer sweep + planted offender), G4-2 (mind parity vs the pin
# read at git 9a36475 + a swapped-canvas control) and G4-3 (replay identity on a Mind-written journal + a planted payload flip).
# Every run uses a FRESH temporary root (#212). Exit 0 iff every gate and every control reads as the PREREG says.
"""usage: python3 tools/gate_g4.py [--genome genome/G4-skeleton.genome] [--tree /data/dev/genome] [--only 1,2,3]"""
from __future__ import annotations

import argparse, ast, io, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

PIN = "d4b5c6b8d57f35e6ad199b49b38d720095ba3b678c380b206665a876698aaa86"   # G4-2, read 2026-09-19 21:3x at 9a36475
SENSE_FILES = ["creature/world_maker.py", "creature/ask.py", "creature/tape.py"]
FORBIDDEN_DIRS = ("state", "journal", "memory")


def _literal_text(node) -> str:
    """Every string piece reachable in a call's first argument (literals, f-strings, joins)."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
    return " ".join(out)


def sweep(paths) -> list:
    offenders = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        tree = ast.parse(p.read_text(), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + ([node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                if any("Organism" == n or n.endswith("machinery") and isinstance(node, ast.ImportFrom) and any(a.name == "Organism" for a in node.names) for n in names):
                    offenders.append((str(p), node.lineno, "imports Organism"))
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
                if name in ("open", "write_text", "write_bytes", "save", "savez", "savez_compressed", "replace", "rename"):
                    target = _literal_text(node.args[0]) if node.args else ""
                    if name == "open" and node.args and len(node.args) > 1:
                        target += " " + _literal_text(node.args[1])
                    if isinstance(fn, ast.Attribute):
                        target += " " + _literal_text(fn.value)
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
    return not off and bool(caught)


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
        b = bytearray(pp.read_bytes()); b[len(b) // 2] ^= 0x01; pp.write_bytes(bytes(b))
        out2 = Path(d) / "replay2"
        r2 = subprocess.run([sys.executable, "-m", "creature.replay", "--genome", str(genome_path), "--tape", str(root2 / "tape" / "ALL.jsonl"),
                             "--against", str(live), "--out", str(out2)], cwd=tree, capture_output=True, text=True)
        caught = r2.returncode != 0
        print(f"G4-3 control (payload byte flipped at seq {eye['seq']}): exit {r2.returncode} → {'CAUGHT' if caught else 'MISSED'}  {(r2.stdout + r2.stderr).strip()[-200:]}")
    return ok and caught


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default="/data/dev/genome")
    ap.add_argument("--genome", default="genome/G4-skeleton.genome")
    ap.add_argument("--only", default="1,2,3")
    a = ap.parse_args()
    tree = Path(a.tree).resolve(); genome_path = (tree / a.genome).resolve()
    os.chdir(tree)
    results = {}
    for k in a.only.split(","):
        results[k] = {"1": gate1, "2": lambda t: gate2(t, genome_path), "3": lambda t: gate3(t, genome_path)}[k](tree)
    print("G4 gates:", {k: ("PASS" if v else "FAIL") for k, v in results.items()})
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
