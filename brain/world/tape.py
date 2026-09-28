"""tape.py — THE MATERIALISER: schedule → renderings → cache → tape.jsonl + truth.jsonl + mlc.jsonl
(B1-PREREG.md §2.4–§2.7, §5.5 (0f)/(0g), §8; docs/brain/b1/SEAT-DECISIONS.md R2, R3, R19, R20).

edit: Claude (Fable 5.1), 2026-09-24 18:17 +0400 — the seat, alone.

Runs under `/usr/bin/python3` for every graded tape (§3.0 — the one interpreter that renders and glances;
`main()` refuses any other unless told). `brain/world/schedule.py` decides WHAT is on the tape (pure, tested
in seconds); this module only turns that decision into bytes: `build_cache` renders every rendering the
schedule listed (unique ids, self-checked), the rendering ids become cache rows, `make_row` computes every
sha, and the three files are written with their counts printed — the per-kind and per-family counts (§2.7's
own test), the SLEEP positions (R2), the plant's seq and its gap to T_L (§5.3 U6, R3).

Controls run at build time, on the materialised bytes: (0f) DISJOINT — no test-sitting operand's or
candidate's PNG sha appears on any TEACH row (a planted copy is caught — `tests/brain/harness/test_tape.py`);
(0g) the MLC leak check over `mlc.jsonl` read whole, through the cache index, never the truth; and the world's
own identity law — the schedule built twice must be identical before a single canvas is rendered.

Layout (§2.5/§2.6/§8): the cache at `<out_root>/cache/<seed>/`, the tape at `<out_root>/<seed>/tape.jsonl`
beside `tape.sha256`, `truth.jsonl`, `mlc.jsonl`, `counts.json`, `schedule-notes.json`, `fonts.json`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from brain.protocol import canonical_json, make_row, validate_tape_row, verify_row

from . import fonts as fonts_mod
from . import mlc as mlc_mod
from . import schedule as S
from .glyphs import NEVER_TAUGHT_SCRIPTS, GlyphLibrary
from .seeds import substream

OUT_ROOT = Path("/data/dev/brain-runs/b1")
SYSTEM_PYTHON = "/usr/bin/python3"


class TapeError(Exception):
    pass


# ================================================================================================ the world's inputs
def plant_fonts_for(plant: Mapping[str, Any], seed: int, n_test: int = 10) -> List[str]:
    """§3.3: "the plant's TEACH rendering is in one of its fonts, its 10 test renderings in 10 others" — the
    pool's own font (the first by sorted order that has the character) teaches; the 10 test fonts are a seeded
    draw from the rest. Raises if the sign has fewer than 11 fonts (the pool guarantees ≥ 11 — MIN_PLANT_FONTS)."""
    lib = GlyphLibrary(plant["script"])
    available = lib.fonts_available_for(plant["char"])
    teach = plant.get("font") or (available[0] if available else None)
    others = [f for f in available if f != teach]
    if teach is None or len(others) < n_test:
        raise TapeError(f"plant {plant['script']}/{plant['char']!r} has {len(available)} fonts, needs the TEACH font + {n_test}")
    rng = substream(seed, "plant:test-fonts")
    idx = sorted(int(i) for i in rng.choice(len(others), size=n_test, replace=False))
    return [teach] + [others[i] for i in idx]


def world_from_stage1(stage1: Mapping[str, Any], seed: int) -> S.WorldInputs:
    """The graded world: TEACH/TEST fonts from the library's own split (§2.2, `fonts.compute`), the never-
    taught pools and the OTHER_CASE removals from stage −1's `ceilings.json` (§3.3)."""
    pools = stage1.get("never_taught_pools")
    if not pools or not all(k in pools for k in ("u2", "u6_refusal", "u5_after_never_taught", "plant")):
        raise TapeError("stage −1's ceilings.json carries no never_taught_pools lists (run the FULL stage −1 first, §3.3)")
    excluded = [e["letter"] for e in (stage1.get("families", {}).get("OTHER_CASE", {}).get("excluded") or [])]
    f = fonts_mod.compute()
    return S.WorldInputs(teach_fonts=list(f["teach"]), test_fonts={s: list(f["test"][s]) for s in ("latin-upper", "latin-lower", "digits")},
                         pools=dict(pools), plant_fonts=plant_fonts_for(pools["plant"], seed), other_case_excluded=excluded)


def smoke_world(seed: int, n_test_fonts: int = 3) -> S.WorldInputs:
    """A SMALL world for the materialiser's own tests: the first `n_test_fonts` TEST fonts per script and
    never-taught signs taken straight from the library (NO θ filter — this is a plumbing world, never a graded
    one; a graded tape's pools come from stage −1 only). The plant = the first Greek sign with ≥ 11 fonts."""
    f = fonts_mod.compute()
    test = {s: list(f["test"][s][:n_test_fonts]) for s in ("latin-upper", "latin-lower", "digits")}

    def signs(script: str, n: int, skip: int = 0) -> List[Dict[str, Any]]:
        lib = GlyphLibrary(script)
        chars = sorted({c for (c, _f) in lib._by_key})
        out = []
        for c in chars[skip:]:
            fs = lib.fonts_available_for(c)
            if fs:
                out.append({"script": script, "char": c, "font": fs[0], "n_fonts_available": len(fs)})
            if len(out) == n:
                break
        if len(out) < n:
            raise TapeError(f"smoke world: {script} has only {len(out)} signs, need {n}")
        return out

    greek = GlyphLibrary("greek")
    plant = None
    for c in sorted({c for (c, _f) in greek._by_key}):
        fs = greek.fonts_available_for(c)
        if len(fs) >= 11:
            plant = {"script": "greek", "char": c, "font": fs[0], "n_fonts_available": len(fs)}
            break
    if plant is None:
        raise TapeError("smoke world: no Greek sign with >= 11 fonts")
    pools = {"u2": signs("hebrew", 20) + signs("arabic", 20), "u6_refusal": signs("greek", 10, skip=1),
             "u5_after_never_taught": signs("greek", 10, skip=11), "plant": plant}
    return S.WorldInputs(teach_fonts=list(f["teach"]), test_fonts=test, pools=pools, plant_fonts=plant_fonts_for(plant, seed))


# ================================================================================================ resolution
def resolve_rows(rows: Sequence[Mapping[str, Any]], item_to_row: Mapping[str, int]) -> List[Dict[str, Any]]:
    """Abstract rows (rendering ids) → concrete tape rows (cache rows, sha computed by `make_row`). Pure."""
    out = []
    for row in rows:
        p = dict(row["payload"])
        try:
            if row["kind"] == "TEACH":
                p["glance_row"] = int(item_to_row[p["glance_row"]])
            elif row["kind"] == "ASK":
                p["operands"] = [({"kind": "row", "value": int(item_to_row[op["value"]])} if op["kind"] == "row" else dict(op))
                                 for op in p["operands"]]
                p["candidate_rows"] = [int(item_to_row[x]) for x in p["candidate_rows"]] if p["candidate_rows"] else None
        except KeyError as e:
            raise TapeError(f"row {row['seq']} references a rendering the cache does not hold: {e}") from None
        concrete = make_row(row["seq"], row["kind"], row["phase"], row["item"], p)
        validate_tape_row(concrete)
        out.append(concrete)
    return out


def resolve_mlc_rows(mlc_rows: Sequence[Mapping[str, Any]], item_to_row: Mapping[str, int]) -> List[Dict[str, Any]]:
    out = []
    for row in mlc_rows:
        p = dict(row["payload"])
        if row["kind"] == "ASK":
            p["operands"] = [{"kind": "row", "value": int(item_to_row[op["value"]])} for op in p["operands"]]
        else:
            p["ask_seq"] = mlc_mod.MLC_SEQ_BASE + int(p["ask_seq"])
        out.append(mlc_mod.make_mlc_row(row["mlc_seq"], row["after_seq"], row["episode"], row["kind"], row["phase"], row["item"], p))
    return out


# ================================================================================================ controls
def disjoint_check(tape_rows: Sequence[Mapping[str, Any]], sha_of_row: Callable[[int], str]) -> Dict[str, Any]:
    """§5.5 (0f): no TEST rendering's PNG sha appears on any TEACH row (`genome/world.py:assert_disjoint_canvas`'s
    law). A test rendering = any glyph row an ASK inside a TEST_BEGIN…TEST_END window carries (operands and
    candidate sheets alike). Returns {pass, n_teach, n_test, collisions: [...]}."""
    teach: Dict[str, int] = {}
    for r in tape_rows:
        if r["kind"] == "TEACH":
            teach[sha_of_row(int(r["payload"]["glance_row"]))] = r["seq"]
    test_rows: Dict[int, int] = {}
    in_sit = False
    for r in tape_rows:
        if r["kind"] == "TEST_BEGIN":
            in_sit = True
        elif r["kind"] == "TEST_END":
            in_sit = False
        elif r["kind"] == "ASK" and in_sit:
            for op in r["payload"]["operands"]:
                if op["kind"] == "row":
                    test_rows.setdefault(int(op["value"]), r["seq"])
            for c in (r["payload"]["candidate_rows"] or []):
                test_rows.setdefault(int(c), r["seq"])
    collisions = []
    for row, seq in test_rows.items():
        sha = sha_of_row(row)
        if sha in teach:
            collisions.append({"cache_row": row, "png_sha": sha, "teach_seq": teach[sha], "test_seq": seq})
    return {"pass": not collisions, "n_teach": len(teach), "n_test": len(test_rows), "collisions": collisions}


def sha256_bytes(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ================================================================================================ materialise
def materialize(sch: S.Schedule, out_dir: Path, cache_dir: Path, seed: int, recheck_n: int = 10,
                log: Callable[[str], None] = print) -> Dict[str, Any]:
    """Render, cache, resolve, control, write. Imports the renderer here (it pulls the gaze and the tower)
    so the pure half of this module stays importable under any interpreter."""
    from brain.glance_cache import Cache
    from brain.world.build import RenderRequest, build_cache

    out_dir = Path(out_dir)
    cache_dir = Path(cache_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    requests = [RenderRequest(item_id=r.item_id, script=r.script, char=r.char, font=r.font) for r in sch.renderings]
    log(f"[tape] seed {seed}: rendering {len(requests)} canvases through the gaze (cache {cache_dir}) …")
    item_to_row, header, truths = build_cache(requests, cache_dir, seed, recheck_n=recheck_n)
    t_render = time.time() - t0
    cache = Cache(cache_dir)
    log(f"[tape] cache built: {len(cache)} rows in {t_render:.0f}s ({1000 * t_render / max(1, len(cache)):.0f} ms per canvas); npy sha {header['npy_sha256'][:16]}…")

    tape_rows = resolve_rows(sch.rows, item_to_row)
    mlc_rows = resolve_mlc_rows(sch.mlc_rows, item_to_row)

    def sha_of_row(row: int) -> str:
        return cache.meta(row)["canvas_png_sha256"]

    def char_of_row(row: int) -> Tuple[str, str]:
        m = cache.meta(row)
        return m["script"], m["char"]

    disjoint = disjoint_check(tape_rows, sha_of_row)
    if not disjoint["pass"]:
        raise TapeError(f"DISJOINT (0f) FAILED: {disjoint['collisions'][:5]}")
    leak = mlc_mod.leak_check(mlc_rows, char_of_row)
    if not leak["pass"]:
        raise TapeError(f"MLC LEAK (0g) FAILED: {leak['violations'][:5]}")

    # ---- write: tape.jsonl + its sha
    tape_path = out_dir / "tape.jsonl"
    with tape_path.open("w", encoding="utf-8") as f:
        for r in tape_rows:
            assert verify_row(r)
            f.write(canonical_json(r) + "\n")
    tape_sha = sha256_bytes(tape_path)
    (out_dir / "tape.sha256").write_text(tape_sha + "\n")
    # ---- mlc.jsonl
    with (out_dir / "mlc.jsonl").open("w", encoding="utf-8") as f:
        for r in mlc_rows:
            f.write(canonical_json(r) + "\n")
    mlc_sha = sha256_bytes(out_dir / "mlc.jsonl")
    # ---- truth.jsonl (R20): rendering records, then ask records
    with (out_dir / "truth.jsonl").open("w", encoding="utf-8") as f:
        for r in sch.renderings:
            row = item_to_row[r.item_id]
            m = cache.meta(row)
            t = truths[r.item_id]
            rec = {"type": "rendering", "item_id": r.item_id, "cache_row": row, "script": m["script"], "char": m["char"],
                   "font": m["font"], "variant": m["variant"], "seed": m["seed"], "top": int(t["top"]), "left": int(t["left"]),
                   "cell": list(t["cell"]), "canvas_png_sha256": m["canvas_png_sha256"]}
            f.write(canonical_json(rec) + "\n")
        for t in sch.truth_asks:
            rec = dict(t)
            rec["rendering_rows"] = [int(item_to_row[i]) for i in t["rendering"]]
            if t.get("mlc"):
                rec["seq"] = mlc_mod.MLC_SEQ_BASE + int(t["seq"])
            f.write(canonical_json(rec) + "\n")
    truth_sha = sha256_bytes(out_dir / "truth.jsonl")

    kinds = sch.counts["kinds"]
    summary = {
        "seed": seed, "interpreter": sys.executable, "params": sch.notes["params"], "params_are_prereg": sch.notes["params_are_prereg"],
        "rows": len(tape_rows), "kinds": kinds, "renderings": len(cache), "render_seconds": round(t_render, 1),
        "ms_per_canvas": round(1000 * t_render / max(1, len(cache)), 1),
        "tape_sha256": tape_sha, "mlc_sha256": mlc_sha, "truth_sha256": truth_sha, "cache_npy_sha256": header["npy_sha256"],
        "cache_dir": str(cache_dir), "out_dir": str(out_dir),
        "sleep_seqs": list(sch.sleep_seqs), "sleep_steps": sch.notes["sleep_steps"], "n_sleeps": len(sch.sleep_seqs),
        "plant": sch.notes["plant"], "T_L_begin_seq": sch.notes["T_L_begin_seq"], "u6_gap_events": sch.notes["u6_gap_events"],
        "asks_by_sitting_family": sch.counts["asks"], "episodes_by_phase_family": sch.counts["episodes"], "sittings": sch.counts["sittings"],
        "mlc": sch.counts["mlc"], "controls": {"disjoint": disjoint, "mlc_leak": {k: v for k, v in leak.items() if k != "violations"}},
    }
    (out_dir / "counts.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    (out_dir / "schedule-notes.json").write_text(json.dumps(sch.notes, sort_keys=True, indent=2, default=str) + "\n")
    # ---- the printed record (§2.7's test, R2, R3)
    log(f"[tape] rows {len(tape_rows)} · kinds {json.dumps(kinds, sort_keys=True)}")
    log(f"[tape] sleeps ({len(sch.sleep_seqs)}, steps {sch.notes['sleep_steps']}) at seqs {sch.sleep_seqs}")
    log(f"[tape] plant «zog» taught at seq {sch.notes['plant']['teach_seq']} ({sch.notes['plant']['script']}/{sch.notes['plant']['char']!r} in {sch.notes['plant']['teach_font']}); T_L begins at seq {sch.notes['T_L_begin_seq']}: gap {sch.notes['u6_gap_events']} events")
    log(f"[tape] mlc: {json.dumps(sch.counts['mlc'], sort_keys=True)} · leak check {'PASS' if leak['pass'] else 'FAIL'} over {leak['n_pairs']} pairs")
    log(f"[tape] DISJOINT (0f): {'PASS' if disjoint['pass'] else 'FAIL'} — {disjoint['n_teach']} TEACH shas vs {disjoint['n_test']} test rows")
    for key in sorted(sch.counts["asks"]):
        log(f"[tape]   asks {key}: {sch.counts['asks'][key]}")
    log(f"[tape] tape.jsonl sha256 {tape_sha}")
    return summary


def build_tape(seed: int, out_dir: Path, cache_dir: Path, world: S.WorldInputs, params: S.Params = S.PREREG,
               log: Callable[[str], None] = print) -> Dict[str, Any]:
    """The whole road for one seed: the schedule built TWICE and compared (the world's identity law, before any
    canvas is rendered), then `materialize`. `fonts.json` is written beside the tape for the graded world."""
    sch = S.build(seed, world, params)
    sch2 = S.build(seed, world, params)
    if not (sch.rows == sch2.rows and sch.truth_asks == sch2.truth_asks and sch.mlc_rows == sch2.mlc_rows
            and [r.item_id for r in sch.renderings] == [r.item_id for r in sch2.renderings]):
        raise TapeError("the schedule built twice from the same (seed, world) differs — the world is not a pure function of its inputs")
    log(f"[tape] schedule: {len(sch.rows)} rows, {len(sch.renderings)} renderings, {len(sch.mlc_rows)} mlc rows; built twice identical")
    summary = materialize(sch, out_dir, cache_dir, seed, log=log)
    if params == S.PREREG:
        fonts_mod.write(Path(out_dir) / "fonts.json")
    return summary


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="B1 tape builder (B1-PREREG.md §2) — run under /usr/bin/python3")
    p.add_argument("--seed", type=int, default=20261001)
    p.add_argument("--stage1", default=None, help="stage −1's ceilings.json (the FULL run) — required for a graded tape")
    p.add_argument("--out-root", default=str(OUT_ROOT))
    p.add_argument("--smoke", action="store_true", help="the SMOKE params + a small library world; writes under <out-root>/smoke/<seed>")
    p.add_argument("--allow-any-interpreter", action="store_true")
    ns = p.parse_args(argv)
    if not ns.allow_any_interpreter and os.path.realpath(sys.executable) != os.path.realpath(SYSTEM_PYTHON):
        raise TapeError(f"a graded tape renders under {SYSTEM_PYTHON} only (§3.0); this is {sys.executable}")
    root = Path(ns.out_root)
    if ns.smoke:
        world = smoke_world(ns.seed)
        out_dir, cache_dir = root / "smoke" / str(ns.seed), root / "smoke" / str(ns.seed) / "cache"
        build_tape(ns.seed, out_dir, cache_dir, world, S.SMOKE)
        return 0
    if not ns.stage1:
        raise TapeError("--stage1 <ceilings.json> is required for a graded tape")
    stage1 = json.loads(Path(ns.stage1).read_text())
    if stage1.get("smoke"):
        raise TapeError("the given ceilings.json is a --smoke stage −1 record; a graded tape needs the FULL run")
    world = world_from_stage1(stage1, ns.seed)
    out_dir, cache_dir = root / str(ns.seed), root / "cache" / str(ns.seed)
    if (out_dir / "tape.jsonl").exists():
        raise TapeError(f"{out_dir / 'tape.jsonl'} exists — a tape is written ONCE per seed (§2.6); remove it deliberately first")
    build_tape(ns.seed, out_dir, cache_dir, world, S.PREREG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
