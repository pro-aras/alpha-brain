"""env.py — STAGE -1 CLAUSE 0: the environment, pinned (B1-PREREG.md §3.0).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:3x +0400 — B1-PREREG.md §9 row 1, step 4 (stage −1).

Records both interpreters' versions (and each numpy's BLAS), asserts no sklearn on either, and runs the
genome pin suite (`tests/genome`) UNDER THE VENV — its PASS/FAIL decides whether the cells (A0) may run
in-process with the torch arms, or must be pushed to a `/usr/bin/python3` subprocess (§3.0's own branch;
the seat decides which, never silently).

`run_suite`'s result is read from the LOG'S OWN "Ran N tests in Xs" / "OK"|"FAILED" line, never from the
subprocess's exit code alone (#191, #239 (8): a pipeline's exit and a traceback that happens to quote the
word you would have grepped for both lie in ways a log's own final line does not).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

VENV_PYTHON = Path("/data/dev/venvs/brain/bin/python")
SYSTEM_PYTHON = Path("/usr/bin/python3")
TMPDIR = Path("/data/dev/brain-runs/tmp")

_PROBE = r"""
import sys, json, importlib.util
info = {"executable": sys.executable, "python": sys.version.split()[0]}
for mod in ("numpy", "scipy", "PIL"):
    try:
        m = __import__(mod)
        info[mod] = getattr(m, "__version__", "?")
    except ImportError:
        info[mod] = None
try:
    import torch
    info["torch"] = torch.__version__
except ImportError:
    info["torch"] = None
try:
    import numpy as np
    cfg = np.show_config(mode="dicts")
    info["numpy_blas"] = cfg.get("Build Dependencies", {}).get("blas", {})
except Exception as e:
    info["numpy_blas"] = {"error": repr(e)}
info["sklearn_present"] = importlib.util.find_spec("sklearn") is not None
print(json.dumps(info))
"""


class EnvError(Exception):
    pass


def _probe_interpreter(python_path: Path, timeout: int = 60) -> Dict[str, object]:
    if not python_path.exists():
        raise EnvError(f"interpreter not found: {python_path}")
    out = subprocess.run([str(python_path), "-c", _PROBE], capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        raise EnvError(f"probing {python_path} exited {out.returncode}: {out.stderr[-2000:]}")
    line = out.stdout.strip().splitlines()[-1]
    return json.loads(line)


def record_environment() -> Dict[str, object]:
    """§3.0: "Record: /usr/bin/python3 (...) and /data/dev/venvs/brain/bin/python (...), each library's
    version and the BLAS each numpy links; no sklearn on either." Raises EnvError (RAISED, §11) if sklearn
    is present on either interpreter — the PREREG states its absence as a checked fact, not a hope."""
    system = _probe_interpreter(SYSTEM_PYTHON)
    venv = _probe_interpreter(VENV_PYTHON)
    for name, info in (("system", system), ("venv", venv)):
        if info.get("sklearn_present"):
            raise EnvError(f"{name} interpreter ({info['executable']}) has sklearn installed — §3.0 declares neither does")
    differ_in = sorted(k for k in ("numpy", "scipy", "PIL") if system.get(k) != venv.get(k))
    return {"system_python": system, "venv_python": venv, "differ_in": differ_in}


_RAN_RE = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s", re.MULTILINE)
_RESULT_RE = re.compile(r"^(OK|FAILED)(\s*\(.*\))?\s*$", re.MULTILINE)


def parse_unittest_log(text: str) -> Dict[str, object]:
    """The log's OWN verdict line — never the caller's exit code. Raises EnvError if the log carries
    neither a "Ran N tests" line nor an OK/FAILED line (a truncated or corrupted log is not a pass)."""
    ran_m = _RAN_RE.search(text)
    result_m = _RESULT_RE.search(text)
    if ran_m is None or result_m is None:
        raise EnvError("log carries no recognisable \"Ran N tests ... OK|FAILED\" line — refusing to guess a verdict")
    return {"ran": int(ran_m.group(1)), "seconds": float(ran_m.group(2)),
            "ok": result_m.group(1) == "OK", "result_line": result_m.group(0).strip()}


def run_suite(python: Path, start_dir: str, top_level: Path, log_path: Path,
              extra_env: Optional[Dict[str, str]] = None, timeout: int = 1800) -> Dict[str, object]:
    """Runs `python -m unittest discover -s start_dir -t top_level`, writes combined stdout+stderr to
    `log_path`, and returns the parsed verdict (`parse_unittest_log`) plus the raw `returncode` (recorded,
    never trusted alone)."""
    env = dict(os.environ)
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "TMPDIR": str(TMPDIR)})
    if extra_env:
        env.update(extra_env)
    TMPDIR.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["nice", "-n", "19", str(python), "-m", "unittest", "discover", "-s", start_dir, "-t", str(top_level)]
    with log_path.open("w") as logf:
        proc = subprocess.run(cmd, cwd=str(top_level), env=env, stdout=logf, stderr=subprocess.STDOUT, timeout=timeout)
    text = log_path.read_text()
    verdict = parse_unittest_log(text)
    verdict["returncode"] = proc.returncode
    verdict["log_path"] = str(log_path)
    verdict["command"] = " ".join(cmd)
    return verdict


def run_genome_pin_suite_under_venv(repo_root: Path, log_path: Path) -> Dict[str, object]:
    """§3.0's own branch-deciding run: PASS -> hybrids may run cells+torch in one process; FAIL -> the cells
    run under /usr/bin/python3 in a subprocess (a decision for the seat, never made silently here)."""
    return run_suite(VENV_PYTHON, "tests/genome", repo_root, log_path)
