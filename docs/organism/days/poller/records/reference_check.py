#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:57 +0400 — POLLER-FIX G3 (docs/organism/days/PREREG-POLLER-FIX.md §3): the reference loops' extraction, repeated from git.
"""reference_check.py — the OLD voice_loop and sense that tests/creature/test_poller_cursor.py compares the real loops against are embedded in that module as
OLD_VOICE_LOOP_SRC / OLD_SENSE_SRC and pinned by sha256. This script extracts the same two functions from GIT at the base (default 233a4cb), by
ast.get_source_segment, and requires the embedded strings to equal them BYTE FOR BYTE and the module's pins to equal their sha256. A reference that someone
edits is caught by its own pin (the unit test) and by this extraction (the verifier's independent repeat).
--plant: change ONE character in a copy of the embedded voice_loop and require the comparison to read DIFFERENT (exit 0 = CAUGHT; the plant asserts it changed the bytes).
Exit 0 iff every check holds (default mode) / the plant is caught (--plant)."""
from __future__ import annotations

import argparse
import ast
import hashlib
import subprocess
import sys
from pathlib import Path


def git_segment(wt: Path, base: str, rel: str, name: str) -> str:
    src = subprocess.run(["git", "show", f"{base}:{rel}"], cwd=wt, capture_output=True, text=True, check=True).stdout
    node = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name][0]
    return ast.get_source_segment(src, node)


def embedded(test_file: Path) -> dict:
    out = {}
    for node in ast.parse(test_file.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("OLD_VOICE_LOOP_SRC", "OLD_SENSE_SRC", "OLD_VOICE_LOOP_SHA256", "OLD_SENSE_SHA256"):
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wt", default=str(Path(__file__).resolve().parents[5]))
    ap.add_argument("--base", default="233a4cb")
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    wt = Path(a.wt).resolve()
    emb = embedded(wt / "tests/creature/test_poller_cursor.py")
    ref = {"OLD_VOICE_LOOP_SRC": git_segment(wt, a.base, "creature/exam.py", "voice_loop"), "OLD_SENSE_SRC": git_segment(wt, a.base, "creature/senses/sit.py", "sense")}
    if a.plant:
        mutated = emb["OLD_VOICE_LOOP_SRC"].replace("poll_period", "poll_perlod", 1)
        assert mutated != emb["OLD_VOICE_LOOP_SRC"], "the plant did not change the bytes"
        caught = mutated != ref["OLD_VOICE_LOOP_SRC"]
        print("PLANT: one character changed in the embedded voice_loop ->", "DIFFERENT from git's (CAUGHT)" if caught else "equal (the check is blind)")
        return 0 if caught else 1
    ok = True
    for key, pin in (("OLD_VOICE_LOOP_SRC", "OLD_VOICE_LOOP_SHA256"), ("OLD_SENSE_SRC", "OLD_SENSE_SHA256")):
        same = emb[key] == ref[key]
        h = hashlib.sha256(ref[key].encode("utf-8")).hexdigest()
        pinned = emb[pin] == h
        ok &= same and pinned
        print(f"{key}: {len(ref[key])} chars; embedded == git {a.base} segment: {same}; pin {emb[pin][:16]}... == sha256 of git's: {pinned}")
    print("RESULT:", "OK" if ok else "NOT OK")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
