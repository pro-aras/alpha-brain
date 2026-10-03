#!/usr/bin/env python3
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 20:45 +0400 — PREREG-EVOLVE-CAL §2 + A1/A2: the calibration's instrument (part 1:
# genome variants, staging, the twin runner, the twin comparison). Tests first: tests/tools/test_evolve_cal_twin.py.
"""tools/evolve_cal.py — EVOLVE-CAL's instrument (docs/organism/evolve/PREREG-EVOLVE-CAL.md).

The calibration replays the INCUMBENT and merit-neutral TWINS of one genome over the same 2 h slice of a closed life's tape, from
the same shadow checkpoint, using `tools/evolve.py`'s OWN `build_twin` / `tape_slice` / `grade_twin` (never re-implemented), and
reads how far twins drift apart (the noise model the gate's bands are built from).

  python3 -m tools.evolve_cal stage-checkpoint --src <checkpoint dir> --dst <copy> [--verify]
  python3 -m tools.evolve_cal stage-slice --live-root <life root> --from-seq A --to-seq B --out <mini tape> [--verify]
  python3 -m tools.evolve_cal twin --cp <copy> --slice-root <mini tape> --from-seq A --to-seq B --variant <v> --out <dir> [--rows-limit N]
  python3 -m tools.evolve_cal compare --a <twin dir> --b <twin dir> [--out file.json]

A VARIANT is ONE changed number of the checkpoint's own genome text and nothing else: `incumbent`; `eps:<eps>:<k>` (DELTA lr x (1 + k*eps),
the law's A1 (ii) null that REACHES the organism); `seed:<k>` (SEED + k: only the think stream moves, the law's A1 (iii) control);
`gene:<KEY>=<value>` (creature/genes.py's own apply_mutation: the planted bad / degraded genes). Nothing under /data/dev/genome-lives is
ever read in place by a twin: a slice is staged as a MINI TAPE (the slice's rows verbatim + only the payload files they name) and a
checkpoint as a verified copy (RULES 7).
"""
from __future__ import annotations

import argparse
import gzip
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
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from creature.genes import BOUNDS, apply_mutation       # noqa: E402
from creature.tape import _resolve_tape_dir             # noqa: E402
import tools.evolve as ev                               # noqa: E402

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\Z")
_SEED_RE = re.compile(r"^(SEED\s+)(\d+)(.*)$", re.MULTILINE)


# ============================================================================ genome variants (ONE number, nothing else)
_spec = ev.bounds_spec          # one implementation, in the worker (tools/evolve.py): the proposer's redraw reads the same numbers
gene_text = ev.gene_text        # The number text the genome currently carries for `key` (BOUNDS' own pattern; exactly one match, or ValueError)


def set_gene_text(text: str, key: str, val_str: str) -> str:
    """Replace the number of `key` by `val_str`, verbatim (no rounding to the gene's printed decimals: an eps twin needs more digits
    than `apply_mutation` keeps). Everything else in the text is byte-identical."""
    if not isinstance(val_str, str) or not _NUMBER.match(val_str):
        raise ValueError(f"evolve_cal: {val_str!r} is not a plain number")
    gene_text(text, key)                                    # exactly one match, or it raises
    new, n = _spec(key)["pattern"].subn(lambda m: m.group(1) + val_str + m.group(2), text, count=1)
    if n != 1:
        raise ValueError(f"evolve_cal: BOUNDS[{key!r}] replaced {n} times (need exactly 1)")
    return new


def eps_variant(text: str, eps: float, k: int) -> str:
    """DELTA lr x (1 + k * eps): the law's A1 (ii) null — a perturbation that REACHES the organism and is merit-negligible. Refuses a
    perturbation that does not change the float at 12 significant digits (a plant that changes nothing, #247 (5))."""
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"evolve_cal: k must be an integer >= 1, got {k!r}")
    if not (eps > 0.0):
        raise ValueError(f"evolve_cal: eps must be > 0, got {eps!r}")
    lr0 = float(gene_text(text, "DELTA.lr"))
    val = format(lr0 * (1.0 + k * eps), ".12g")
    if "e" in val or "E" in val or float(val) == lr0:
        raise ValueError(f"evolve_cal: eps={eps!r} k={k} gives {val!r}, not a different plain number from {lr0!r}")
    return set_gene_text(text, "DELTA.lr", val)


def read_seed(text: str) -> int:
    ms = _SEED_RE.findall(text)
    if len(ms) != 1:
        raise ValueError(f"evolve_cal: the SEED line matched {len(ms)} times (need exactly 1)")
    return int(ms[0][1])


def seed_variant(text: str, k: int) -> str:
    """SEED + k: the law's A1 (iii) control — the seed reaches only the think stream (`_think_rng` and the boundary generator)."""
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"evolve_cal: k must be an integer >= 1, got {k!r}")
    seed = read_seed(text)
    new, n = _SEED_RE.subn(lambda m: m.group(1) + str(seed + k) + m.group(3), text, count=1)
    if n != 1:
        raise ValueError("evolve_cal: the SEED line did not replace exactly once")
    return new


def variant_text(text: str, variant: str) -> str:
    """The genome text of a named variant of `text` (the checkpoint's own GENOME.genome)."""
    if variant == "incumbent":
        return text
    kind, _, rest = variant.partition(":")
    try:
        if kind == "eps":
            eps, _, k = rest.partition(":")
            return eps_variant(text, float(eps), int(k))
        if kind == "seed":
            return seed_variant(text, int(rest))
        if kind == "gene":
            key, _, val = rest.partition("=")
            spec = _spec(key)
            return apply_mutation(text, key, int(val) if spec["kind"] == "int" else float(val))
    except (ValueError, TypeError) as e:
        raise ValueError(f"evolve_cal: cannot read variant {variant!r}: {e}") from e
    raise ValueError(f"evolve_cal: unknown variant {variant!r} (incumbent | eps:<eps>:<k> | seed:<k> | gene:<KEY>=<value>)")


# ============================================================================ staging (a mini tape; a verified checkpoint copy)
def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _source_lines(tape_dir: Path, from_seq: int, to_seq: int):
    """(day file name, original line text, parsed row) for every row with from_seq < seq <= to_seq, in the tape's own order."""
    for day_file in sorted(Path(tape_dir).glob("*.jsonl")):
        with day_file.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if from_seq < int(row["seq"]) <= to_seq:
                    yield day_file.name, line, row


def stage_slice(live_root: Path, declared_tape_path: Optional[str], from_seq: int, to_seq: int, out_root: Path) -> dict:
    """The slice (from_seq, to_seq] of `live_root`'s tape as a MINI TAPE under `out_root`: the rows' ORIGINAL lines (so a verifier can
    compare them byte for byte) in the same day-file names, and only the payload files those rows name, copied. A missing source
    payload raises — a slice with a hole must not replay as a whole one. `tools.evolve.tape_slice(out_root, …)` and `build_twin(…,
    live_root=out_root)` read it unchanged."""
    live_root, out_root = Path(live_root), Path(out_root)
    if out_root.exists() and any(out_root.iterdir()):
        raise FileExistsError(f"evolve_cal: {out_root} exists and is not empty (a staged record is never overwritten)")
    src_tape = _resolve_tape_dir(live_root, declared_tape_path)
    dst_tape = _resolve_tape_dir(out_root, declared_tape_path)
    (dst_tape / "payload").mkdir(parents=True, exist_ok=True)
    by_day: Dict[str, List[str]] = {}
    h = hashlib.sha256()
    n_payloads = payload_bytes = 0
    first_seq = last_seq = None
    for day, line, row in _source_lines(src_tape, from_seq, to_seq):
        by_day.setdefault(day, []).append(line)
        h.update(line.encode("utf-8")); h.update(b"\n")
        seq = int(row["seq"])
        first_seq = seq if first_seq is None else first_seq
        last_seq = seq
        rel = row.get("payload")
        if rel:
            src = src_tape / rel
            if not src.exists():
                raise FileNotFoundError(f"evolve_cal: row {seq} names payload {rel!r}, which does not exist under {src_tape}")
            dst = dst_tape / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            n_payloads += 1
            payload_bytes += dst.stat().st_size
    for day, lines in by_day.items():
        (dst_tape / day).write_text("\n".join(lines) + "\n")
    manifest = {"source_root": str(live_root), "declared_tape_path": declared_tape_path, "from_seq": int(from_seq), "to_seq": int(to_seq),
                "first_seq": first_seq, "last_seq": last_seq, "n_rows": sum(len(v) for v in by_day.values()),
                "n_payloads": n_payloads, "payload_bytes": payload_bytes, "rows_sha256": h.hexdigest(),
                "days": {d: len(v) for d, v in sorted(by_day.items())}}
    (out_root / "STAGED.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return manifest


def verify_staged_slice(live_root: Path, declared_tape_path: Optional[str], staged_root: Path) -> dict:
    """Re-read the SOURCE and compare it with the staged mini tape: every row line byte for byte, every payload present, its sha256
    equal to the row's own `sha` and its bytes equal to the source's. Reads both sides; writes nothing."""
    live_root, staged_root = Path(live_root), Path(staged_root)
    manifest = json.loads((staged_root / "STAGED.json").read_text())
    src_tape = _resolve_tape_dir(live_root, declared_tape_path)
    dst_tape = _resolve_tape_dir(staged_root, declared_tape_path)
    src_rows = [(day, line, row) for day, line, row in _source_lines(src_tape, manifest["from_seq"], manifest["to_seq"])]
    dst_rows: Dict[str, List[str]] = {}
    for f in sorted(dst_tape.glob("*.jsonl")):
        dst_rows[f.name] = [ln.strip() for ln in f.read_text().splitlines() if ln.strip()]
    mismatches = 0
    missing: List[str] = []
    bad_sha: List[str] = []
    seen: Dict[str, int] = {}
    for day, line, row in src_rows:
        i = seen.get(day, 0)
        seen[day] = i + 1
        have = dst_rows.get(day, [])
        if i >= len(have) or have[i] != line:
            mismatches += 1
        rel = row.get("payload")
        if rel:
            p = dst_tape / rel
            if not p.exists():
                missing.append(rel)
                continue
            if row.get("sha") and _sha_file(p) != row["sha"]:
                bad_sha.append(rel)
            elif (src_tape / rel).read_bytes() != p.read_bytes():
                bad_sha.append(rel)
    extra = sum(len(v) for v in dst_rows.values()) - len(src_rows)
    equal = not mismatches and not missing and not bad_sha and extra == 0
    return {"equal": equal, "rows_checked": len(src_rows), "row_mismatches": mismatches, "missing_payloads": missing,
            "payload_mismatches": bad_sha, "extra_rows": extra}


def _tree_manifest(root: Path) -> Dict[str, str]:
    root = Path(root)
    return {str(p.relative_to(root)): _sha_file(p) for p in sorted(root.rglob("*")) if p.is_file()}


def stage_checkpoint(src_dir: Path, dst_dir: Path) -> dict:
    """A COPY of a shadow checkpoint (state/ + GENOME.genome + META.json) — `build_twin` copies `<dir>/state` per twin, so the
    shared copy is only ever read. Returns the destination's manifest (relative path -> sha256)."""
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    if dst_dir.exists() and any(dst_dir.iterdir()):
        raise FileExistsError(f"evolve_cal: {dst_dir} exists and is not empty (a staged record is never overwritten)")
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
    files = _tree_manifest(dst_dir)
    manifest = {"source": str(src_dir), "files": files, "n_files": len(files),
                "bytes": sum((dst_dir / rel).stat().st_size for rel in files)}
    mpath = dst_dir.parent / (dst_dir.name + ".manifest.json")
    mpath.write_text(json.dumps(manifest, sort_keys=True, indent=1) + "\n")
    return manifest


def verify_staged_checkpoint(src_dir: Path, dst_dir: Path) -> dict:
    """Hash both trees and compare: every source file present and byte-equal in the copy, nothing extra in the copy."""
    a, b = _tree_manifest(Path(src_dir)), _tree_manifest(Path(dst_dir))
    mism = sorted(k for k in a if k in b and a[k] != b[k])
    missing = sorted(k for k in a if k not in b)
    extra = sorted(k for k in b if k not in a)
    return {"equal": not mism and not missing and not extra, "n_files": len(a), "mismatches": mism, "missing": missing, "extra": extra}


# ============================================================================ the twin runner (one twin per process)
def _code_provenance() -> Optional[dict]:
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True, timeout=20).stdout.strip())
        return {"git_head": head, "dirty": dirty} if head else None
    except (OSError, subprocess.SubprocessError):
        return None


def _json_default(o):
    try:
        return o.item()
    except AttributeError:
        return str(o)


def run_twin(cp_dir: Path, genome_text: str, slice_root: Path, from_seq: int, to_seq: int, out_dir: Path,
             variant: str = "incumbent", rows_limit: Optional[int] = None, keep_state: bool = False,
             label: Optional[str] = None) -> dict:
    """ONE twin: resume from the checkpoint copy under `genome_text`, consume the slice's rows, close, grade with
    `tools.evolve.grade_twin`, and write `<out>/reading.json` (last, atomically: its presence means the twin finished),
    `<out>/journal.jsonl.gz` (canonical lines), `<out>/GENOME.genome`. The twin's big state copy is removed unless `keep_state`.
    Read beside the grade: the dense `state_hash` (after close, the snapshot's own digest), the sparse `row_hash`, the journal's
    digest, CPU seconds of THIS process around the twin (not wall), the load and the CPU/memory pressure at start and end, and the
    process's peak RSS — one twin per process makes that the twin's."""
    cp_dir, slice_root, out_dir = Path(cp_dir), Path(slice_root), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    twin_root = out_dir / "root"
    rows = ev.tape_slice(slice_root, from_seq, to_seq)
    if rows_limit is not None:
        rows = rows[:int(rows_limit)]
    (out_dir / "GENOME.genome").write_text(genome_text)
    m0 = ev.machine_snapshot()
    t0, c0 = time.perf_counter(), time.process_time()
    mind = ev.build_twin({"dir": cp_dir}, genome_text, twin_root, slice_root)
    build_s = time.perf_counter() - t0
    for row in rows:
        mind.consume(row)
    mind.close()
    wall, cpu = time.perf_counter() - t0, time.process_time() - c0
    m1 = ev.machine_snapshot()
    reading = ev.grade_twin(mind, twin_root, twin_root / "GENOME.genome", rows, wall)
    journal_rows = ev._read_journal_rows(twin_root)
    canon = [json.dumps(r, sort_keys=True) for r in journal_rows]
    with gzip.open(out_dir / "journal.jsonl.gz", "wt") as f:
        f.write("\n".join(canon) + ("\n" if canon else ""))
    reading.update({
        "variant": variant, "label": label, "genome_sha256": hashlib.sha256(genome_text.encode("utf-8")).hexdigest(),
        "from_seq": int(from_seq), "to_seq": int(to_seq), "rows_consumed": len(rows),
        "state_hash": mind.org.state_hash(), "row_hash": mind.org.row_hash(),
        "journal_sha256": hashlib.sha256("\n".join(canon).encode("utf-8")).hexdigest(), "journal_rows": len(journal_rows),
        "cpu_s": round(cpu, 3), "build_s": round(build_s, 3), "load0": m0["load"], "load1": m1["load"], "psi0": m0["psi"], "psi1": m1["psi"],
        "maxrss_kb": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss), "code": _code_provenance(),
    })
    reading = json.loads(json.dumps(reading, default=_json_default))
    del mind
    if not keep_state:
        shutil.rmtree(twin_root, ignore_errors=True)
    tmp = out_dir / "reading.json.tmp"
    tmp.write_text(json.dumps(reading, sort_keys=True, indent=1))
    tmp.replace(out_dir / "reading.json")
    return reading


def read_twin_journal(out_dir: Path) -> List[dict]:
    with gzip.open(Path(out_dir) / "journal.jsonl.gz", "rt") as f:
        return [json.loads(line) for line in f.read().splitlines() if line]


# ============================================================================ comparing two twins
_CONTINUOUS_KEYS = {"hash"}          # a digest of the whole state: a witness that moves with any bit, never a discrete outcome
_MISSING = object()


def _has_float(x) -> bool:
    if isinstance(x, float):
        return True
    if isinstance(x, (list, tuple)):
        return any(_has_float(y) for y in x)
    if isinstance(x, dict):
        return any(_has_float(y) for y in x.values())
    return False


def compare_twins(rows_a: Sequence[dict], rows_b: Sequence[dict]) -> dict:
    """Row-by-row comparison of two twins' journals. `rows_differing` counts rows that differ in ANY key; `discrete_diff_rows` counts
    rows that differ in a key whose value carries no float on either side (a fix, a birth, a cell count, an act, a word, a think) and is
    not the state digest — the outcomes a continuous perturbation must flip before a reading can move. `by_decile` shows where along
    the slice the differing rows fall (a growing divergence is chaos amplifying a perturbation)."""
    n_a, n_b = len(rows_a), len(rows_b)
    n = min(n_a, n_b)
    first = None
    first_disc = None
    key_counts: Counter = Counter()
    rows_diff = disc_rows = 0
    deciles = [0] * 10
    for i in range(n):
        ra, rb = rows_a[i], rows_b[i]
        if ra == rb:
            continue
        first = i if first is None else first
        rows_diff += 1
        keys = [k for k in sorted(set(ra) | set(rb)) if ra.get(k, _MISSING) != rb.get(k, _MISSING)]
        key_counts.update(keys)
        if any(k not in _CONTINUOUS_KEYS and not (_has_float(ra.get(k)) or _has_float(rb.get(k))) for k in keys):
            disc_rows += 1
            first_disc = i if first_disc is None else first_disc
        deciles[min(9, i * 10 // max(1, n))] += 1
    first_diff = first if first is not None else (n if n_a != n_b else None)
    return {"identical": n_a == n_b and rows_diff == 0, "n_a": n_a, "n_b": n_b, "rows_differing": rows_diff,
            "discrete_diff_rows": disc_rows, "first_discrete_diff": first_disc, "first_diff": first_diff, "equal_prefix": first_diff if first_diff is not None else n,
            "diff_key_counts": dict(key_counts), "by_decile": deciles}


# ============================================================================ the bands (PREREG-EVOLVE-CAL A1 (i), A2.2, A4, A7; scipy)
# edit: Claude (Sonnet 5.5, swarm integrator), 2026-10-03 21:10 +0400 — tests first: tests/tools/test_evolve_cal_bands_build.py.
ALPHA_SIDE = 0.0083      # one-sided per side per dimension: 0.025 family-wise over three dimensions
NORMAL_P = 0.01          # Shapiro–Wilk: a null not normal at p < 0.01 uses its rank band
Q1_GRID = 1.0 / 110      # q1_seen is correct / 110 held-out items


def make_band(dim: str, values: Sequence[float], grid: Optional[float] = None, alpha_side: float = ALPHA_SIDE,
              normal_p: float = NORMAL_P) -> dict:
    """The band of ONE dimension from its merit-neutral null (the incumbent + the twins' readings on one slice).
    A4 (i): σ̂ is the sample SD (n − 1 df). A4 (ii): the production Δ is a difference of two draws, centred at 0 with σ_Δ = √2 σ̂, and the edge is
    t(n − 1, 1 − alpha_side) · σ_Δ. A1 (i): fewer than 3 distinct values or σ̂ = 0 → NO band. A4 (iii): not normal at p < normal_p → the rank band, the
    range of the null's readings (Δ outside ± range is «outside all draws»). A None reading in the null is refused, never dropped."""
    import statistics
    from scipy import stats
    if any(v is None for v in values):
        raise ValueError(f"make_band({dim}): a None reading in the null is refused, not dropped")
    vals = [float(v) for v in values]
    n = len(vals)
    if n < 3:
        raise ValueError(f"make_band({dim}): {n} values (need at least 3)")
    distinct, sigma = len(set(vals)), statistics.stdev(vals)
    t = float(stats.t.ppf(1.0 - alpha_side, n - 1))
    base = {"dim": dim, "n": n, "df": n - 1, "distinct": distinct, "sigma_hat": sigma, "mean": statistics.fmean(vals), "min": min(vals), "max": max(vals),
            "range": max(vals) - min(vals), "grid": grid, "alpha_side": alpha_side, "t": t, "values": vals}
    if distinct < 3 or not (sigma > 0.0):
        return {**base, "kind": "none", "edge": None, "normality": None,
                "reason": f"the null held {distinct} distinct value(s), σ̂ = {sigma:.6g}: fewer than 3 distinct values or σ = 0 gives NO band (A1 (i)); the dimension does not gate"}
    W, p = stats.shapiro(vals)
    norm = {"test": "shapiro", "W": float(W), "p": float(p)}
    if p < normal_p:
        out = {**base, "kind": "rank", "edge": None, "normality": norm,
               "note": "rank band: the null is not normal at p < 0.01, so a Δ outside ± the range of the null's readings is outside all draws; its error at n = 21 is "
                       "1/22 ≈ 4.5 % per side per dimension — the 0.025 family-wise holds only for the normal band (A4 (iii))"}
        half = out["range"]
    else:
        edge = t * (2.0 ** 0.5) * sigma
        out = {**base, "kind": "normal", "edge": edge, "normality": norm,
               "note": f"normal band: edge = t({n - 1}, 1 − {alpha_side}) · √2 · σ̂ = {t:.4f} · {2 ** 0.5:.4f} · {sigma:.6g} (A4 (ii))"}
        half = edge
    if grid:
        out["edge_grid"] = half / grid
        out["min_clear_grid"] = math.floor(round(half / grid, 9)) + 1
    return out


def variance_ratio_test(a: Sequence[float], b: Sequence[float], alpha: float = 0.05, two_sided: bool = True) -> dict:
    """F = var(a) / var(b) with (n_a − 1, n_b − 1) df. Two-sided (A7's transfer test): different iff F > F_(1 − alpha/2)(df_a, df_b) or F < 1 / F_(1 − alpha/2)(df_b, df_a);
    one-sided (A2.2's «larger»): different iff F > F_(1 − alpha)(df_a, df_b). A zero variance against a spread is different (F = 0 or ∞); two zero variances are not."""
    import statistics
    from scipy import stats
    na, nb = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    dfa, dfb = na - 1, nb - 1
    tail = alpha / 2 if two_sided else alpha
    hi = float(stats.f.ppf(1.0 - tail, dfa, dfb))
    lo = (1.0 / float(stats.f.ppf(1.0 - tail, dfb, dfa))) if two_sided else 0.0
    if va == 0 and vb == 0:
        F, different, wider = float("nan"), False, None
    elif vb == 0:
        F, different, wider = float("inf"), True, "a"
    elif va == 0:
        F = 0.0
        different, wider = (True, "b") if two_sided else (False, None)
    else:
        F = va / vb
        different = F > hi or (two_sided and F < lo)
        wider = ("a" if F > hi else ("b" if (two_sided and F < lo) else None)) if different else None
    return {"F": F, "df": (dfa, dfb), "f_crit_hi": hi, "f_crit_lo": lo, "alpha": alpha, "two_sided": two_sided, "different": bool(different),
            "wider": wider, "var_a": va, "var_b": vb}


def frames_band(eps_values: Sequence[float], seed_values: Optional[Sequence[float]]) -> dict:
    """A2.2: one band rule for every dimension, `frames_filed` included: the ε twins' null gives the band; the seed twins' σ̂ is printed beside it and RULES only where it
    is larger by a one-sided F-test at p < 0.05 (the wider band then applies, and the record says why)."""
    eps = make_band("frames_filed", eps_values, grid=1.0)
    if not seed_values:
        return {"rules": "eps", "band": eps, "eps": eps, "seed": None, "f_test": None}
    seed = make_band("frames_filed", seed_values, grid=1.0)
    f = variance_ratio_test(seed_values, eps_values, alpha=0.05, two_sided=False)
    if f["different"] and f["wider"] == "a":
        return {"rules": "seed", "band": seed, "eps": eps, "seed": seed, "f_test": f}
    return {"rules": "eps", "band": eps, "eps": eps, "seed": seed, "f_test": f}


def make_bands(null: Dict[str, Sequence[float]], slice_name: str, scope: str, seed_frames: Optional[Sequence[float]] = None,
               alpha_side: float = ALPHA_SIDE) -> dict:
    """The BANDS file (validated): q1_seen on its 1/110 grid, frames_filed on whole frames, confirmed_share continuous, and the cost on ln(CPU-seconds)."""
    from tools import evolve_bands
    for d in evolve_bands.GATED:
        if d not in null:
            raise ValueError(f"make_bands: the null of {d!r} is missing")
    fr = frames_band(null["frames_filed"], seed_frames)
    dims = {"q1_seen": make_band("q1_seen", null["q1_seen"], grid=Q1_GRID, alpha_side=alpha_side),
            "frames_filed": {**fr["band"], "rule": fr["rules"]},
            "confirmed_share": make_band("confirmed_share", null["confirmed_share"], grid=None, alpha_side=alpha_side)}
    if "ln_cpu" in null:
        dims["ln_cpu"] = make_band("ln_cpu", null["ln_cpu"], grid=None, alpha_side=alpha_side)
    n = len(null["q1_seen"])
    out = {"law": "docs/organism/evolve/PREREG-EVOLVE-CAL.md (A1–A8)", "slice": slice_name, "n": n, "df": n - 1, "alpha_side": alpha_side,
           "cost_policy_cap": evolve_bands.COST_POLICY_CAP, "scope": scope, "dims": dims, "frames_rule": fr["rules"], "frames_f_test": fr["f_test"]}
    evolve_bands.validate_bands(out)
    return out


# ============================================================================ CLI
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage-slice")
    p.add_argument("--live-root", required=True); p.add_argument("--declared-tape", default=None)
    p.add_argument("--from-seq", type=int, required=True); p.add_argument("--to-seq", type=int, required=True)
    p.add_argument("--out", required=True); p.add_argument("--verify", action="store_true")
    p = sub.add_parser("stage-checkpoint")
    p.add_argument("--src", required=True); p.add_argument("--dst", required=True); p.add_argument("--verify", action="store_true")
    p = sub.add_parser("twin")
    p.add_argument("--cp", required=True); p.add_argument("--slice-root", required=True)
    p.add_argument("--from-seq", type=int, required=True); p.add_argument("--to-seq", type=int, required=True)
    p.add_argument("--variant", default="incumbent"); p.add_argument("--out", required=True)
    p.add_argument("--rows-limit", type=int, default=None); p.add_argument("--keep-state", action="store_true"); p.add_argument("--label", default=None)
    p = sub.add_parser("compare")
    p.add_argument("--a", required=True); p.add_argument("--b", required=True); p.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    if a.cmd == "stage-slice":
        m = stage_slice(Path(a.live_root), a.declared_tape, a.from_seq, a.to_seq, Path(a.out))
        print(json.dumps({k: m[k] for k in ("n_rows", "n_payloads", "payload_bytes", "rows_sha256", "first_seq", "last_seq")}, sort_keys=True))
        if a.verify:
            v = verify_staged_slice(Path(a.live_root), a.declared_tape, Path(a.out))
            print("VERIFY", json.dumps(v, sort_keys=True))
            return 0 if v["equal"] else 1
        return 0
    if a.cmd == "stage-checkpoint":
        m = stage_checkpoint(Path(a.src), Path(a.dst))
        print(json.dumps({"n_files": m["n_files"], "bytes": m["bytes"]}, sort_keys=True))
        if a.verify:
            v = verify_staged_checkpoint(Path(a.src), Path(a.dst))
            print("VERIFY", json.dumps({k: v[k] for k in ("equal", "n_files", "mismatches", "missing", "extra")}, sort_keys=True))
            return 0 if v["equal"] else 1
        return 0
    if a.cmd == "twin":
        cp = Path(a.cp)
        text = variant_text((cp / "GENOME.genome").read_text(), a.variant)
        r = run_twin(cp, text, Path(a.slice_root), a.from_seq, a.to_seq, Path(a.out), variant=a.variant, rows_limit=a.rows_limit,
                     keep_state=a.keep_state, label=a.label)
        print(json.dumps({k: r.get(k) for k in ("variant", "q1_seen", "confirmed_share", "frames_filed", "rows_consumed", "journal_rows",
                                                "state_hash", "journal_sha256", "wall_s", "cpu_s", "maxrss_kb")}, sort_keys=True))
        return 0
    if a.cmd == "compare":
        da, db = Path(a.a), Path(a.b)
        ra, rb = json.loads((da / "reading.json").read_text()), json.loads((db / "reading.json").read_text())
        res = {"a": {"variant": ra.get("variant"), "label": ra.get("label")}, "b": {"variant": rb.get("variant"), "label": rb.get("label")},
               "journal": compare_twins(read_twin_journal(da), read_twin_journal(db)),
               "state_hash_equal": ra["state_hash"] == rb["state_hash"], "row_hash_equal": ra["row_hash"] == rb["row_hash"],
               "q1_seen": [ra.get("q1_seen"), rb.get("q1_seen")], "frames_filed": [ra.get("frames_filed"), rb.get("frames_filed")],
               "confirmed_share": [ra.get("confirmed_share"), rb.get("confirmed_share")]}
        print(json.dumps(res, sort_keys=True))
        if a.out:
            Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
