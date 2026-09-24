"""organs.py — LOADING THE PINNED ORGANS FOR THE GLANCE CACHE (B1-PREREG.md §2.5).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 17:1x +0400 — B1-PREREG.md §9 row 1, step 3 (the cache).

§2.5: "The call: genome.gaze.glances(rgb, spec, gaze, 'surprise', pic_id=<canvas png sha>,
colour=<Genome.colour>, predicted=None), with spec, gaze, colour parsed by genome.machinery.parse_genome
from genome/ALPHA4.genome." This module is that parse, done ONCE, plus the four organ pins §2.5's header
spec names: organs/retina.py, organs/gaze.py (both from `genome.gaze.PINS`, verified by `genome.gaze.
organs()` itself the first time it runs), genome/retina_fast.py (`genome.gaze._RETINA_FAST_PIN`), and the
sealed eye tower's own tower.bin — independently sha256'd here (never trusted from a docstring) and checked
against the value B1-PREREG.md §2.5 states.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple

from genome import gaze as genome_gaze
from genome.machinery import Genome, parse_genome

from brain.glance_cache import sha256_file

_REPO_ROOT = Path(__file__).resolve().parents[2]
ALPHA4_GENOME_PATH = _REPO_ROOT / "genome" / "ALPHA4.genome"
TOWER_BIN_PATH = Path("/data/dev/alpha3/judge/eye-tower-g2/tower.bin")
# B1-PREREG.md §2.5, checked directly against the file on this box before this module existed.
TOWER_BIN_SHA256 = "6abc6d7553d8b8c7529b4b1802e6f6b5c758c89d4abc0be01a2e6299fbb301f6"


class OrgansError(Exception):
    pass


def load_genome(path: Path = ALPHA4_GENOME_PATH) -> Genome:
    text = path.read_text()
    return parse_genome(text)


def genome_sha(path: Path = ALPHA4_GENOME_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def organ_pins() -> Dict[str, str]:
    """The four organ pins (§2.5's header spec), each independently re-hashed — never copied from a
    comment. Raises OrgansError (RAISED to the seat, §11) if the tower's own bytes ever changed."""
    pins: Dict[str, str] = dict(genome_gaze.PINS)   # organs/retina.py, organs/gaze.py — verified by organs()
    pins["genome/retina_fast.py"] = genome_gaze._RETINA_FAST_PIN
    got = sha256_file(TOWER_BIN_PATH)
    if got != TOWER_BIN_SHA256:
        raise OrgansError(f"{TOWER_BIN_PATH} sha256 changed: expected {TOWER_BIN_SHA256}, got {got} — RAISE to the seat, do not proceed")
    pins["eye-tower-g2/tower.bin"] = got
    return pins


def gaze_config(g: Optional[Genome] = None) -> Tuple[Tuple[str, ...], Dict[str, object], Optional[Dict[str, object]]]:
    """(RETINA spec, GAZE dict, SENSE colour dict-or-None) exactly as ALPHA4.genome declares them —
    imported, never re-typed (§2.5)."""
    g = g or load_genome()
    return g.retina, g.gaze, g.colour


def verify_organs_load() -> None:
    """Forces genome.gaze.organs() to run its own sha check on organs/retina.py and organs/gaze.py NOW
    (it otherwise lazily verifies on first real glance call) — a fast fail before any rendering starts."""
    genome_gaze.organs()
