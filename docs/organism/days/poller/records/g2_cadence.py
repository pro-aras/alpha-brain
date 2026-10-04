#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm hears), 2026-10-03 22:00 +0400 — POLLER-FIX G2 (docs/organism/days/PREREG-POLLER-FIX.md §3): cadence identity on ONE real saved state.
"""g2_cadence.py — G2 for ONE saved state, in a process whose cwd is the life's own code with the fix applied (the OVERLAY: PYTHONPATH=. , cwd = the overlay tree).

    cd <overlay> && PYTHONPATH=. python3 -B <this file> --label ck4 --src <state dir to COPY> --genome <genome file> --work <scratch dir> --out <jsonl>

The state is COPIED first (RULES 7; shutil.copy2: size AND mtime_ns preserved, verified file by file against the source, which is never written). Then:
  1. the manifest of the original copy has NO canvas_index (the old-format premise) and the ledger carries one (the PRESENCE count, #168);
  2. the OLD road on the original copy: canvas_count_now returns road "ledger" and the number the independent reference returns
     (canvas_count_of(json.loads(ledger.json), fixations), the old code verbatim; fixations read from the state's own genome);
  3. Mind.resume + Mind.snapshot() on the copy under the OVERLAY writes a NEW-FORMAT manifest; canvas_count_now now returns road "snapshot" and the SAME number
     (the ablated-system guard, #246 (1): with the key stripped the reader falls to the ledger road and reads the same number, so the number alone would pass
     WITHOUT the fix: stripped manifest -> road "ledger" is recorded as the guard's own reading);
  4. the number equals the original ledger's canvas_index (resume restores _canvas_index from it);
  5. PLANT: a manifest copy with canvas_index + 1 is read: the comparison must report DIFFERENT (CAUGHT); the plant asserts its bytes differ (sha256).
The copy is deleted at the end (unless --keep). Exit 0 iff every check holds; one JSON line is appended to --out either way."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path


def vm_kb(key: str) -> int:
    for ln in open("/proc/self/status"):
        if ln.startswith(key + ":"):
            return int(ln.split()[1])
    return -1


def tree_sig(d: Path) -> dict:
    out = {}
    for dp, _dn, fns in os.walk(d):
        for fn in fns:
            p = Path(dp) / fn
            if p.is_symlink():
                continue
            st = p.stat()
            out[str(p.relative_to(d))] = (st.st_size, st.st_mtime_ns)
    return out


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--genome", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    rec: dict = {"label": a.label, "src": a.src, "genome": a.genome, "cwd": os.getcwd(), "ok": False}
    try:
        from creature import exam
        from creature import mind as mind_module
        from creature.mind import Mind
        from creature.tape import _resolve_tape_dir
        from genome.machinery import parse_genome
        assert str(Path(exam.__file__).resolve()).startswith(os.getcwd()) and str(Path(mind_module.__file__).resolve()).startswith(os.getcwd()), "not the overlay's code"
        assert hasattr(exam, "canvas_count_now"), "the overlay does not carry the fix"
        genome_text = Path(a.genome).read_text()
        genome = parse_genome(genome_text)
        fixations = int(genome.gaze["fixations"]) if genome.gaze else 1
        rec["fixations"] = fixations
        src = Path(a.src)
        root = Path(a.work) / f"root-{a.label}"
        if root.exists():
            shutil.rmtree(root)
        t0 = time.perf_counter()
        shutil.copytree(src, root / "state", copy_function=shutil.copy2)
        shutil.copy2(a.genome, root / "GENOME.genome")
        rec["copy_s"] = round(time.perf_counter() - t0, 2)
        state = root / "state"
        sig_src, sig_dst = tree_sig(src), tree_sig(state)
        bad = [k for k in sig_src if sig_dst.get(k) != sig_src[k]]
        rec["copy_files"], rec["copy_mismatches"] = len(sig_src), len(bad) + len(set(sig_dst) - set(sig_src))
        declared = genome.declared.get("TAPE", {}).get("path")
        (_resolve_tape_dir(root, declared) / "payload").mkdir(parents=True, exist_ok=True)

        # (1) the old-format premise and the presence count
        man0 = json.loads((state / "SNAPSHOT.json").read_text())
        rec["manifest_has_key_before"] = "canvas_index" in man0
        rec["t"], rec["last_seq"] = man0.get("t"), man0.get("last_seq")
        ledger = json.loads((state / "ledger.json").read_text())
        rec["ledger_has_canvas_index"] = "canvas_index" in ledger
        rec["moments"] = ledger.get("moments")
        rec["ledger_canvas_index"] = ledger.get("canvas_index")
        ref = exam.canvas_count_of(ledger, fixations)            # the independent reference: the old code verbatim
        rec["reference"] = ref
        del ledger
        gc.collect()

        # (2) the OLD road on the original copy
        n_old, road_old = exam.canvas_count_now(state, fixations)
        rec["n_old"], rec["road_old"] = n_old, road_old

        # (3) resume + snapshot under the overlay: a NEW-FORMAT manifest
        t1 = time.perf_counter()
        mind, last = Mind.resume(Path(root / "GENOME.genome"), root)
        rec["resume_s"] = round(time.perf_counter() - t1, 2)
        rec["resume_canvas_index"] = int(mind._canvas_index)
        rec["resume_last_seq"] = int(last)
        t2 = time.perf_counter()
        mind.snapshot()
        rec["snapshot_s"] = round(time.perf_counter() - t2, 2)
        man1_raw = (state / "SNAPSHOT.json").read_bytes()
        man1 = json.loads(man1_raw)
        rec["manifest_key_after"] = man1.get("canvas_index")
        ledger2 = json.loads((state / "ledger.json").read_text())
        rec["ledger2_canvas_index"] = ledger2.get("canvas_index")
        del ledger2
        gc.collect()
        n_new, road_new = exam.canvas_count_now(state, fixations)
        rec["n_new"], rec["road_new"] = n_new, road_new

        # the ablated-system guard: the key stripped from a copy of the new manifest (the ledger hard-linked, never rewritten) falls to the ledger road
        abl = Path(a.work) / f"ablate-{a.label}"
        if abl.exists():
            shutil.rmtree(abl)
        abl.mkdir()
        os.link(state / "ledger.json", abl / "ledger.json")
        stripped = {k: v for k, v in man1.items() if k != "canvas_index"}
        (abl / "SNAPSHOT.json").write_text(json.dumps(stripped, sort_keys=True))
        n_abl, road_abl = exam.canvas_count_now(abl, fixations)
        rec["ablated"] = [n_abl, road_abl]

        # (5) the plant: canvas_index + 1 in a copy of the new manifest
        plant = Path(a.work) / f"plant-{a.label}"
        if plant.exists():
            shutil.rmtree(plant)
        plant.mkdir()
        os.link(state / "ledger.json", plant / "ledger.json")
        planted = dict(man1)
        planted["canvas_index"] = int(man1["canvas_index"]) + 1
        planted_raw = json.dumps(planted, sort_keys=True).encode()
        (plant / "SNAPSHOT.json").write_bytes(planted_raw)
        assert sha(planted_raw) != sha(man1_raw), "the plant did not change the bytes"
        n_pl, road_pl = exam.canvas_count_now(plant, fixations)
        rec["plant"] = {"read": [n_pl, road_pl], "reported_different": n_pl != ref, "sha256_original": sha(man1_raw)[:16], "sha256_planted": sha(planted_raw)[:16]}
        shutil.rmtree(abl, ignore_errors=True)
        shutil.rmtree(plant, ignore_errors=True)

        checks = {
            "copy_exact": rec["copy_mismatches"] == 0,
            "old_format_premise": rec["manifest_has_key_before"] is False,
            "ledger_presence": rec["ledger_has_canvas_index"] is True,
            "old_road_is_ledger_and_equals_reference": road_old == "ledger" and n_old == ref,
            "resume_restores_the_count": rec["resume_canvas_index"] == ref and rec["resume_last_seq"] == rec["last_seq"],
            "new_manifest_key_is_an_int_equal_to_the_ledger": type(man1.get("canvas_index")) is int and man1["canvas_index"] == rec["ledger2_canvas_index"] == ref,
            "new_road_is_snapshot_and_equals_reference": road_new == "snapshot" and n_new == ref,
            "ablation_falls_to_the_ledger_road_and_reads_the_same_number": road_abl == "ledger" and n_abl == ref,
            "plant_reports_different": rec["plant"]["reported_different"] is True and road_pl == "snapshot",
        }
        rec["checks"] = checks
        rec["compared"] = True
        rec["differs"] = not (n_old == n_new == ref)
        rec["ok"] = all(checks.values())
    except Exception as e:                                         # a failed state is a RESULT, recorded, never averaged away
        rec["error"] = repr(e)
        rec["traceback"] = traceback.format_exc()[-1500:]
    rec["hwm_mb"] = round(vm_kb("VmHWM") / 1024.0, 0)
    with open(a.out, "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    if not a.keep:
        shutil.rmtree(Path(a.work) / f"root-{a.label}", ignore_errors=True)
    print(json.dumps({k: rec.get(k) for k in ("label", "ok", "moments", "reference", "road_old", "road_new", "n_new", "resume_s", "snapshot_s", "hwm_mb", "error")}))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
