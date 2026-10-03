#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:55 +0400 — POLLER-FIX G5 (docs/organism/days/PREREG-POLLER-FIX.md §3): the mutation sweep.
"""mutate_poller.py — every mutant of the law's G5 (m1..m15, plus m12b and m14w, the two-sided mutants split into their sides, plus the author's own m16..m18) is applied to a CLEAN
OVERLAY COPY of the worktree (never the worktree itself), and the ONE test the mapping names for it (MUTANT_TESTS in tests/creature/test_poller_cursor.py,
committed BEFORE this sweep ran) is run ALONE. CAUGHT = that test FAILS or ERRORS by name; SURVIVED = it passes; INVALID = the run failed without the named
test failing (an import error is not a catch).

Instruments (each must read as it should or the sweep exits non-zero):
  - the CLEAN overlay: every distinct named test PASSES on the unmutated copy, and the whole module passes (the positive control);
  - every edit matches EXACTLY ONCE in its file, changes the bytes (sha256 before != after) and leaves valid Python (ast.parse);
  - the overlay is what the subprocess imports (creature.exam / creature.mind / creature.senses.sit __file__ under the overlay);
  - the NEGATIVE PLANT m0: a docstring-only edit (an EQUIVALENT mutant, behaviour identical by construction) must read SURVIVED — the sweep can say «not caught».
Usage (from the worktree root, through slot): python3 -B docs/organism/days/poller/records/mutate_poller.py --out <prefix>   (writes <prefix>.json and <prefix>.txt)
Exit 0 iff every real mutant is CAUGHT, the clean controls pass and m0 SURVIVED; 2 if the worktree is not clean."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DIRS = ("creature", "genome", "tools", "brain", "world", "judge", "runs", "tests")
MIND, EXAM, SIT = "creature/mind.py", "creature/exam.py", "creature/senses/sit.py"
MOD = "tests.creature.test_poller_cursor"
SNAP_OLD = '    if isinstance(ci, int) and not isinstance(ci, bool):\n        return ci, "snapshot"'
LEDGER_ROAD = '    ledger_path = state_dir / "ledger.json"\n    if ledger_path.exists():'
VOICE_CALL = '        canvas_count, _road = canvas_count_now(root / "state", fixations)'
SIT_CALL = '        canvas_count, _road = canvas_count_now(root / "state", fixations) if every_canvases > 0 else (None, "none")'
KEY_LINE = '                                       "canvas_index": ledger["canvas_index"],\n'
PARSE_LEDGER_STATE = '        try:\n            json.loads((state_dir / "ledger.json").read_text())\n        except (OSError, ValueError):\n            pass\n'
PARSE_LEDGER_ROOT = '        try:\n            json.loads((root / "state" / "ledger.json").read_text())\n        except (OSError, ValueError):\n            pass\n'

# (id, what the mutant is, [(file, old text (must match once), new text)])
MUTANTS = [
    ("m1", "the writer omits the key", [(MIND, KEY_LINE, "")]),
    ("m2", "the writer writes self.org.t (moments, not canvases)", [(MIND, '"canvas_index": ledger["canvas_index"],', '"canvas_index": int(self.org.t),')]),
    ("m3", "the writer writes str(canvas_index)", [(MIND, '"canvas_index": ledger["canvas_index"],', '"canvas_index": str(ledger["canvas_index"]),')]),
    ("m4", "the reader ignores the key", [(EXAM, SNAP_OLD, SNAP_OLD.replace("if isinstance(ci, int)", "if False and isinstance(ci, int)"))]),
    ("m5", "the reader takes t // fixations when the key is absent",
     [(EXAM, LEDGER_ROAD, '    if isinstance(manifest, dict) and isinstance(manifest.get("t"), int):\n        return int(manifest["t"]) // max(1, int(fixations)), "snapshot"\n' + LEDGER_ROAD)]),
    ("m6", "the reader accepts a bool", [(EXAM, SNAP_OLD, SNAP_OLD.replace(" and not isinstance(ci, bool)", ""))]),
    ("m7", "an unparsable manifest yields 0 instead of the ledger road",
     [(EXAM, '    except (OSError, ValueError):\n        manifest = None\n', '    except (OSError, ValueError):\n        return 0, "snapshot"\n')]),
    ("m8", "the ledger road only when the manifest is MISSING, not when it lacks the key",
     [(EXAM, LEDGER_ROAD, '    if isinstance(manifest, dict):\n        return None, "none"\n' + LEDGER_ROAD)]),
    ("m9", "the snapshot road still parses the ledger (road says snapshot)", [(EXAM, SNAP_OLD, SNAP_OLD.replace('        return ci, "snapshot"', PARSE_LEDGER_STATE + '        return ci, "snapshot"'))]),
    ("m10", "voice_loop still calls json.loads(ledger)", [(EXAM, VOICE_CALL, PARSE_LEDGER_ROOT + VOICE_CALL)]),
    ("m11", "sense still calls json.loads(ledger)", [(SIT, SIT_CALL, PARSE_LEDGER_ROOT + SIT_CALL)]),
    ("m12", "voice_loop passes root for root/state", [(EXAM, 'canvas_count_now(root / "state", fixations)', "canvas_count_now(root, fixations)")]),
    ("m12b", "sense passes root for root/state", [(SIT, 'canvas_count_now(root / "state", fixations)', "canvas_count_now(root, fixations)")]),
    ("m13", "the manifest read is cached (stale forever)",
     [(EXAM, "def canvas_count_now(state_dir: Path, fixations: int)", "_STALE: dict = {}\n\n\ndef canvas_count_now(state_dir: Path, fixations: int)"),
      (EXAM, 'return ci, "snapshot"', 'return _STALE.setdefault(str(state_dir), ci), "snapshot"')]),
    ("m14", "the reader is off by one", [(EXAM, 'return ci, "snapshot"', 'return ci + 1, "snapshot"')]),
    ("m14w", "the writer is off by one", [(MIND, '"canvas_index": ledger["canvas_index"],', '"canvas_index": ledger["canvas_index"] + 1,')]),
    # edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 21:57 +0400 — m16..m18 are the author's own, beyond the law's m1..m15 (the first sweep read 17 of 17 without them)
    ("m16", "sense's every <= 0 guard dropped (SIT would poll a disabled duty)", [(SIT, ' if every_canvases > 0 else (None, "none")', "")]),
    ("m17", "the ledger road ignores fixations", [(EXAM, 'return canvas_count_of(ledger, fixations), "ledger"', 'return canvas_count_of(ledger, 1), "ledger"')]),
    ("m18", "a zero cursor is read as falsy", [(EXAM, SNAP_OLD, SNAP_OLD.replace("if isinstance(ci, int)", "if ci and isinstance(ci, int)"))]),
    ("m15", "a torn ledger on the ledger road raises instead of {}",
     [(EXAM, '        try:\n            ledger = json.loads(ledger_path.read_text())\n        except (json.JSONDecodeError, OSError):\n            ledger = {}\n        return canvas_count_of(ledger, fixations), "ledger"',
       '        ledger = json.loads(ledger_path.read_text())\n        return canvas_count_of(ledger, fixations), "ledger"')]),
]
# the negative plant: a DOCSTRING-only edit — an equivalent mutant, never counted as caught
M0 = ("m0", "EQUIVALENT (docstring only): «at most one» -> «at most 1»", [(EXAM, "this reader lags by at most one", "this reader lags by at most 1")],
      "TestLoopEquivalence.test_s1_voice_loop_manifest_and_ledger_agree")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def named_tests(test_file: Path) -> dict:
    tree = ast.parse(test_file.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "MUTANT_TESTS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("MUTANT_TESTS not found in the test module")


def run_test(overlay: Path, dotted: str, env: dict, timeout: int = 600):
    cmd = [sys.executable, "-B", "-u", "-m", "unittest", f"{MOD}.{dotted}" if dotted else MOD]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=overlay, env=env, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr, time.time() - t0


def verdict(rc: int, out: str, meth: str) -> str:
    ran1 = re.search(r"^Ran 1 test", out, re.M) is not None
    named = re.search(rf"^(FAIL|ERROR): {re.escape(meth)} ", out, re.M) is not None
    if rc == 0:
        return "SURVIVED"
    return "CAUGHT" if (ran1 and named) else "INVALID"


def first_error(out: str) -> str:
    m = re.search(r"^((?:[A-Za-z_.]*(?:Error|Exception))[^\n]*)", out, re.M)
    return (m.group(1) if m else "")[:170]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wt", default=str(Path(__file__).resolve().parents[5]))
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    wt = Path(a.wt).resolve()
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + [d for d in DIRS if (wt / d).exists()], cwd=wt, capture_output=True, text=True).stdout.strip()
    if dirty:
        print("the worktree is not clean (a sweep runs on the fix's committed bytes):\n" + dirty)
        return 2
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt, capture_output=True, text=True, check=True).stdout.strip()
    mapping = named_tests(wt / "tests/creature/test_poller_cursor.py")
    ids = [m[0] for m in MUTANTS]
    if sorted(ids) != sorted(mapping):
        print(f"the sweep's mutants {sorted(ids)} != the mapping's {sorted(mapping)}")
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="poller-mutants-", dir=os.environ.get("TMPDIR") or None))
    overlay = tmp / "overlay"
    overlay.mkdir()
    for d in DIRS:
        if (wt / d).exists():
            shutil.copytree(wt / d, overlay / d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    clean = {rel: (overlay / rel).read_bytes() for rel in (MIND, EXAM, SIT)}
    for rel, b in clean.items():
        assert sha(b) == sha((wt / rel).read_bytes()), f"the overlay copy of {rel} differs from the worktree's"
    env = dict(os.environ, PYTHONPATH=str(overlay), OPENBLAS_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    where = subprocess.run([sys.executable, "-B", "-c", "import creature.exam as e, creature.mind as m, creature.senses.sit as s; print(e.__file__, m.__file__, s.__file__)"],
                           cwd=overlay, env=env, capture_output=True, text=True).stdout.split()
    assert len(where) == 3 and all(w.startswith(str(overlay)) for w in where), f"the subprocess imports the wrong tree: {where}"
    rows, ok = [], True
    # the positive control: the unmutated overlay passes every named test and the whole module
    ctl = {}
    for dotted in sorted(set(mapping.values()) | {M0[3]}):
        rc, out, dt = run_test(overlay, dotted, env)
        ctl[dotted] = {"exit": rc, "ran": (re.search(r"^Ran (\d+) tests?", out, re.M) or [None, None])[1], "ok": rc == 0 and re.search(r"^OK$", out, re.M) is not None}
        ok &= ctl[dotted]["ok"]
    rc, out, dt = run_test(overlay, "", env)
    whole = {"exit": rc, "ran": (re.search(r"^Ran (\d+) tests?", out, re.M) or [None, None])[1], "ok": rc == 0 and re.search(r"^OK$", out, re.M) is not None}
    ok &= whole["ok"]
    for mid, what, edits in MUTANTS + [M0[:3]]:
        dotted = mapping[mid] if mid != "m0" else M0[3]
        for rel, b in clean.items():                         # restore the clean bytes, then apply this mutant's edits
            (overlay / rel).write_bytes(b)
        applied = []
        for rel, old, new in edits:
            src = (overlay / rel).read_text()
            n = src.count(old)
            assert n == 1, f"{mid}: the anchor matches {n} times in {rel}: {old[:60]!r}"
            mut = src.replace(old, new)
            assert mut != src and sha(mut.encode()) != sha(src.encode()), f"{mid}: the plant did not change the bytes"
            ast.parse(mut)
            (overlay / rel).write_text(mut)
            applied.append({"file": rel, "sha256_clean": sha(src.encode())[:16], "sha256_mutated": sha(mut.encode())[:16], "anchor": old[:70]})
        rc, out, dt = run_test(overlay, dotted, env)
        v = verdict(rc, out, dotted.split(".")[1])
        if mid == "m0":
            good = v == "SURVIVED"                            # the instrument can say «not caught»
        else:
            good = v == "CAUGHT"
        ok &= good
        rows.append({"id": mid, "what": what, "named_test": dotted, "verdict": v, "as_expected": good, "exit": rc, "seconds": round(dt, 1), "first_error": first_error(out), "edits": applied})
    for rel, b in clean.items():
        (overlay / rel).write_bytes(b)
    caught = sum(1 for r in rows if r["id"] != "m0" and r["verdict"] == "CAUGHT")
    summary = {"fix_sha": head, "mutants": len(MUTANTS), "caught": caught, "negative_plant_m0": next(r["verdict"] for r in rows if r["id"] == "m0"),
               "clean_controls": ctl, "clean_whole_module": whole, "overlay_imports": where, "ok": bool(ok and caught == len(MUTANTS))}
    Path(a.out + ".json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True))
    lines = [f"MUTATION SWEEP of {head[:12]} (clean overlay copy; each mutant's named test run ALONE)",
             f"{caught} of {len(MUTANTS)} mutants CAUGHT; negative plant m0 (equivalent, docstring only) reads {summary['negative_plant_m0']}; clean module: Ran {whole['ran']}, exit {whole['exit']}"]
    for r in rows:
        lines.append(f"{r['id']:5s} {r['verdict']:8s} {r['named_test']}  [{r['what']}]  {r['seconds']}s  {r['first_error']}")
    lines.append("RESULT: " + ("OK" if summary["ok"] else "NOT OK"))
    Path(a.out + ".txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
