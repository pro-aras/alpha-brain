# edit: Claude (Sonnet 5.5, swarm claims), 2026-10-03 17:49 +0400 — a MUTATION SWEEP of tools/brain/resit.py against tests/tools/test_resit_daily.py (the daily mode and the helpers it uses): each mutation breaks ONE thing the law
# relies on; the module must go red on it. The original is restored in a `finally` and its sha256 verified. `<<NEVER>>` stands for an always-false literal so no committed file holds one.
# Run through slot, from the worktree root, ONLY while nothing else edits resit.py.
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

TARGET = Path("tools/brain/resit.py")
ORIG = TARGET.read_text()
SHA0 = hashlib.sha256(ORIG.encode()).hexdigest()
TESTS = "tests.tools.test_resit_daily"

MUTATIONS = [
    ("D01 S1: the genome in force is read by the gate rule", 'gf = genome_in_force(root, ev["epochs"], upto_seq=int(st["last_seq"]))', 'gf = genome_in_force(root, ev["epochs"], before_seq=1)'),
    ("D02 v4: the grade child is given the LIFE's genome", '"genome": str(items_genome), "out_dir": str(run_dir), "m2a_rows": True}', '"genome": str(gf["path"]), "out_dir": str(run_dir), "m2a_rows": True}'),
    ("D03 AM2: eye_changed is never set", 'row["eye_changed"] = bool(eye["eye_changed"])', 'row["eye_changed"] = False'),
    ("D04 A2.2: the verdict-copy flag is never taken", "flagged = flag_verdict_copy(prior + [dict(row)])[-1]", "flagged = {}"),
    ("D05 A2.2: post_origin_learned is read from the wrong base", 'int(origin["origin_n_learned_fresh_begin"])) if origin else None)', 'int(origin["begin_seq_fresh"])) if origin else None)'),
    ("D06 A3.4: the restarts window starts at 0", 'restarts_info(ev["starts"], int(origin["begin_seq_fresh"]), int(st["last_seq"]))', 'restarts_info(ev["starts"], 0, int(st["last_seq"]))'),
    ("D07 R6: the partition is not required", '        require_partition(row["partition"])\n', "        pass\n"),
    ("D08 R8: the items pin is never written or checked", 'pin_items(out, scan, scored=scored_pin, world_line_sha=world_scene_line_sha(genome_text), items_root=items_root)\n        row["items"] = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"],\n                        "world_seed"',
     'pass\n        row["items"] = {"n_asks": scan["n_asks"], "n_canvases": scan["n_canvases"], "ask_digest": scan["ask_digest"], "canvas_digest": scan["canvas_digest"],\n                        "world_seed"'),
    ("D09 §4: a daily row is never paired", 'row["vs_origin"], row["vs_origin_note"] = pair["vs_origin"], pair["note"]', 'row["vs_origin"], row["vs_origin_note"] = None, ""'),
    ("D10 R4: a refusal in daily mode exits 2", '        row["refused"] = str(e)\n    except Exception as e:                      # a defect of the reader: the row carries it, the unit fails visibly',
     '        row["refused"] = str(e)\n        rc = 2\n    except Exception as e:                      # a defect of the reader: the row carries it, the unit fails visibly'),
    ("D11 R7: the cap is always the warm cap", "cap = a.cpu_cap_s or (CPU_CAP_COLD_S if cold else CPU_CAP_WARM_S)\n        spec = {\"code\": str(code), \"items_root\": str(items_root), \"tape_decl\": tape_decl, \"states\"",
     "cap = a.cpu_cap_s or CPU_CAP_WARM_S\n        spec = {\"code\": str(code), \"items_root\": str(items_root), \"tape_decl\": tape_decl, \"states\""),
    ("D12 §1.2: the life's epoch and start rows are ignored", 'ev = scan_life_events(root / "journal")\n        copy_dir = run_dir / "copy"', 'ev = {"epochs": [], "starts": [], "torn_lines": 0, "lines_read": 0}\n        copy_dir = run_dir / "copy"'),
    ("D13 R6: an item with no class is given one instead of being refused", "        c = item_class.get(item)\n        if c is None:\n            raise ResitError(f\"refused: item {item} ({mark}, set {s}) has no phrase class",
     "        c = item_class.get(item) or \"colour_or_size\"\n        if c is None:\n            raise ResitError(f\"refused: item {item} ({mark}, set {s}) has no phrase class"),
    ("D14 S1: the brain is read from state/prev in place", '"states": [{"name": "*", "dir": str(copy_dir), "genome": str(gf["path"])}],\n                "out_dir": str(run_dir), "glance_cache": str(cache), "check_turn": None}\n        ach = run_child("answer", spec, run_dir, cpu_cap_s=cap)',
     '"states": [{"name": "*", "dir": str(root / "state" / "prev"), "genome": str(gf["path"])}],\n                "out_dir": str(run_dir), "glance_cache": str(cache), "check_turn": None}\n        ach = run_child("answer", spec, run_dir, cpu_cap_s=cap)'),
    ("D15 v4: the life's eye is never compared against the grader's genome", "eye = eye_changed(life_lines, origin=(origin.get(\"genome_lines\") if origin else None), grader=grader_lines)", "eye = eye_changed(life_lines, origin=(origin.get(\"genome_lines\") if origin else None), grader=None)"),
    ("D16 AM1 d: the items journal's restart duplicates are not counted", 'row["restart_duplicates"] = collapse_duplicates(ijs["answers"])["restart_duplicates"]\n        ginfo', 'row["restart_duplicates"] = 0\n        ginfo'),
    ("D17 R4 j: the grader pin is not checked before the children", 'row["grader"] = {**ginfo, "pin": check_grader_pin(out, ginfo, write=False)}\n        # the live life', 'row["grader"] = {**ginfo, "pin": "absent"}\n        # the live life'),
]


def run_tests() -> tuple:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({"PYTHONPATH": ".", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1"})
    p = subprocess.run([sys.executable, "-B", "-u", "-m", "unittest", TESTS], capture_output=True, text=True, env=env)
    tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""
    return p.returncode, tail


def main() -> int:
    survived = []
    only = tuple(sys.argv[1:])
    try:
        for name, old, new in MUTATIONS:
            if only and not name.startswith(only):
                continue
            old, new = old.replace("<<NEVER>>", "False"), new.replace("<<NEVER>>", "False")
            assert ORIG.count(old) == 1, f"{name}: the anchor is not unique ({ORIG.count(old)})"
            mutated = ORIG.replace(old, new)
            assert mutated != ORIG, f"{name}: the mutation must change the bytes"
            TARGET.write_text(mutated)
            t0 = time.time()
            rc, tail = run_tests()
            verdict = "CAUGHT" if rc != 0 else "SURVIVED"
            if rc == 0:
                survived.append(name)
            print(f"{verdict:9s} {name}  [{tail}]  ({time.time() - t0:.0f} s)", flush=True)
    finally:
        TARGET.write_text(ORIG)
        sha1 = hashlib.sha256(TARGET.read_text().encode()).hexdigest()
        print(f"restored: sha256 {'equal' if sha1 == SHA0 else 'DIFFERENT'} ({SHA0[:16]})", flush=True)
    print(f"survivors: {survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
