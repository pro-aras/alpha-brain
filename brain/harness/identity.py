"""identity.py — STAGE -1 CLAUSE 1: the replay-identity test, orchestrated across REAL SEPARATE PROCESSES
(B1-PREREG.md §3.1).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:5x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

Every arm — torch or not (§3.1: "the same twice-and-planted test for the non-torch arms") — is checked the
same four ways: TWICE (byte-identical answers, identical state_sha at every checkpoint); a PLANTED
DIVERGENCE (a legitimate tape whose first TEACH at/after event 1234 points to a different cache row — must
diverge from exactly that point, never earlier); a RESUME (a snapshot mid-replay, reloaded in a fresh
process, continued — must match the uninterrupted run at the end); and, as a FINDING never a gate, the same
run at 8 threads. `identity_worker.py` does the actual replay, in its own `subprocess.run` — real process
isolation, not merely a fresh function call in the same interpreter, so a source of nondeterminism that
lives in process-global state (an uninitialised buffer, a BLAS thread pool) cannot hide.
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from brain.protocol import canonical_json, row_sha


class IdentityError(Exception):
    pass


def write_tape_jsonl(tape_rows: Sequence[Dict[str, Any]], path: Path) -> None:
    with Path(path).open("w") as f:
        for row in tape_rows:
            f.write(canonical_json(row) + "\n")


def plant_divergence(tape_rows: Sequence[Dict[str, Any]], at_or_after_event: int, new_glance_row: int) -> List[Dict[str, Any]]:
    """§3.1: "a copy of the tape in which the first TEACH row at or after event `at_or_after_event` points
    to a DIFFERENT cache row (its sha recomputed, so the copy is a legitimate tape)". Mutates only that ONE
    row's `glance_row` and recomputes its `sha` — every other row is untouched, so the copy differs from the
    original by exactly one payload field."""
    out = [copy.deepcopy(r) for r in tape_rows]
    for row in out:
        if row["seq"] >= at_or_after_event and row["kind"] == "TEACH":
            row["payload"] = dict(row["payload"])
            row["payload"]["glance_row"] = new_glance_row
            row["sha"] = row_sha(row["payload"])
            return out
    raise IdentityError(f"no TEACH row at seq >= {at_or_after_event} to plant a divergence on")


def run_worker(python: Path, repo_root: Path, arm_module: str, arm_class: str, seed: int, config: Dict[str, Any],
               tape_path: Path, n_events: int, checkpoints: Sequence[int], out_dir: Path, run_name: str, *,
               start_event: int = 0, load_snapshot: Optional[Path] = None, save_snapshot: Optional[Path] = None,
               threads: int = 1, timeout: int = 900) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    args: Dict[str, Any] = {
        "arm_module": arm_module, "arm_class": arm_class, "seed": seed, "config": config,
        "tape_path": str(tape_path), "n_events": n_events, "checkpoints": list(checkpoints),
        "start_event": start_event,
        "out_path": str(out_dir / f"{run_name}.result.json"),
        "answers_path": str(out_dir / f"{run_name}.answers.jsonl"), "threads": threads,
    }
    if load_snapshot is not None:
        args["load_snapshot"] = str(load_snapshot)
    if save_snapshot is not None:
        args["save_snapshot"] = str(save_snapshot)
    args_path = out_dir / f"{run_name}.args.json"
    args_path.write_text(json.dumps(args))

    env = dict(os.environ)
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    cmd = [str(python), "-m", "brain.harness.identity_worker", "--args-json", str(args_path)]
    proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=timeout, env=env)
    log_path = out_dir / f"{run_name}.worker.log"
    log_path.write_text(f"$ {' '.join(cmd)}\n\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n")
    if proc.returncode != 0:
        raise IdentityError(f"worker {run_name!r} exited {proc.returncode} — see {log_path}")
    return json.loads((out_dir / f"{run_name}.result.json").read_text())


def identity_test(python: Path, repo_root: Path, arm_module: str, arm_class: str, seed: int, config: Dict[str, Any],
                   tape_rows: Sequence[Dict[str, Any]], out_dir: Path, *,
                   checkpoints: Sequence[int] = (500, 1000, 1500, 2000), n_events: int = 2000,
                   plant_at_event: int = 1234, planted_row: int = 999999,
                   run_8_threads: bool = True) -> Dict[str, Any]:
    """§3.1's whole clause. Returns a report with a `pass` bool per sub-check and every raw result kept on
    disk under `out_dir` (never only the verdict — #194)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = sorted(checkpoints)
    tape_slice = list(tape_rows[:n_events])
    if len(tape_slice) < n_events:
        raise IdentityError(f"identity_test: tape has only {len(tape_slice)} rows, need >= {n_events}")

    tape_path = out_dir / "tape.jsonl"
    write_tape_jsonl(tape_slice, tape_path)

    r1 = run_worker(python, repo_root, arm_module, arm_class, seed, config, tape_path, n_events, checkpoints, out_dir, "run1")
    r2 = run_worker(python, repo_root, arm_module, arm_class, seed, config, tape_path, n_events, checkpoints, out_dir, "run2")
    twice_answers_match = r1["answers_sha256"] == r2["answers_sha256"]
    twice_state_match = r1["state_sha_at"] == r2["state_sha_at"]

    diverged = plant_divergence(tape_slice, plant_at_event, planted_row)
    diverged_path = out_dir / "tape_diverged.jsonl"
    write_tape_jsonl(diverged, diverged_path)
    r3 = run_worker(python, repo_root, arm_module, arm_class, seed, config, diverged_path, n_events, checkpoints, out_dir, "run_diverged")
    early_cps = [c for c in checkpoints if c < plant_at_event]
    late_cps = [c for c in checkpoints if c >= plant_at_event]
    planted_early_ok = all(r1["state_sha_at"][str(c)] == r3["state_sha_at"][str(c)] for c in early_cps)
    planted_late_ok = bool(late_cps) and all(r1["state_sha_at"][str(c)] != r3["state_sha_at"][str(c)] for c in late_cps)

    # The resume point is the smallest checkpoint strictly before n_events (§3.1: "a snapshot at event
    # 1,000 loaded in a new process and continued"). `replay()`'s own convention (identity_worker.py) is
    # that `events` starts AT `start_event` and a checkpoint is recorded only after a row past it is
    # processed — so the resumed process never re-records `resume_at` itself; that ONE checkpoint is
    # instead verified against the FIRST (pre-resume) run's own snapshot-time state below.
    resume_at = min(c for c in checkpoints if c < n_events) if checkpoints else n_events // 2
    snap_path = out_dir / "resume.snap"
    r_first = run_worker(python, repo_root, arm_module, arm_class, seed, config, tape_path, resume_at,
                          [resume_at], out_dir, "resume_first", save_snapshot=snap_path)
    r_resumed = run_worker(python, repo_root, arm_module, arm_class, seed, config, tape_path, n_events,
                            [c for c in checkpoints if c > resume_at], out_dir, "resume_continued",
                            start_event=resume_at, load_snapshot=snap_path)
    snapshot_point_ok = r_first["state_sha_at"].get(str(resume_at)) == r1["state_sha_at"].get(str(resume_at))
    later_cps = [c for c in checkpoints if c > resume_at]
    later_ok = all(r1["state_sha_at"][str(c)] == r_resumed["state_sha_at"].get(str(c)) for c in later_cps)
    resume_ok = snapshot_point_ok and later_ok

    threads_finding: Dict[str, Any] = {}
    if run_8_threads:
        r8 = run_worker(python, repo_root, arm_module, arm_class, seed, config, tape_path, n_events, checkpoints,
                         out_dir, "run_8threads", threads=8)
        threads_finding = {"identical_to_1_thread": r8["state_sha_at"] == r1["state_sha_at"], "result": r8}

    overall_pass = twice_answers_match and twice_state_match and planted_early_ok and planted_late_ok and bool(resume_ok)
    return {
        "pass": overall_pass,
        "twice": {"answers_match": twice_answers_match, "state_match": twice_state_match},
        "planted_divergence": {"early_unchanged": planted_early_ok, "late_diverged": planted_late_ok,
                                "plant_at_event": plant_at_event, "early_checkpoints": early_cps, "late_checkpoints": late_cps},
        "resume": {"ok": resume_ok},
        "threads_finding": threads_finding,   # a FINDING, never a gate (§3.1)
        "out_dir": str(out_dir),
    }
