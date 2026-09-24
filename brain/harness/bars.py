"""bars.py — STAGE -1 CLAUSE 4: FROM CEILING TO BAR, the validator (B1-PREREG.md §3.4).

edit: Claude (Sonnet 5, B1 builder 2), 2026-09-24 18:3x +0400 — B1-PREREG.md §9 row 1, step 4/5 (stage −1
clause 4; reused by the results.json validator, step 5).

"After ceilings.json exists, the seat appends a dated line under §12 declaring every bar's number, each
with its ceiling beside it. The validator refuses any bar above its family's ceiling, and any bar below
k_min / n (a bar an arm at chance could clear with P >= 0.001). A family whose ceiling <= (k_min / n) + its
95% binomial half-width is NOT GRADABLE — ORGAN LIMIT, named, never failed. Bars are never moved after any
graded answer exists (#228)."

This module never declares a bar itself (that is the seat's own §12 line, never a builder's, §3.4's own
words) — it only VALIDATES numbers the caller supplies against `ceilings.json`'s own contents. Every family
entry in `ceilings.json` is expected to carry, at minimum, `{"organ_ceiling": {"max": float, ...}, "k_min":
int, "n": int}` — `stage_minus1.py`'s assembly step normalises every family (naming, relation, perceptual)
into this shared shape (§3.3's own output list applies it uniformly across every family kind).
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Dict, Mapping, Optional


class BarsError(Exception):
    pass


def binomial_half_width_95(p: float, n: int) -> float:
    if n <= 0:
        raise BarsError(f"binomial_half_width_95: n must be > 0, got {n}")
    return 1.96 * math.sqrt(max(p, 0.0) * max(1.0 - p, 0.0) / n)


def is_not_gradable(entry: Mapping[str, object]) -> bool:
    """§3.4: "A family whose ceiling <= (k_min / n) + its 95% binomial half-width is NOT GRADABLE — ORGAN LIMIT.\""""
    ceiling = entry["organ_ceiling"]["max"]  # type: ignore[index]
    k_min, n = entry["k_min"], entry["n"]
    if n <= 0:
        raise BarsError("is_not_gradable: n must be > 0")
    p = k_min / n
    return ceiling <= p + binomial_half_width_95(p, n)


def validate_bar(family: str, entry: Mapping[str, object], bar: float) -> None:
    """Raises BarsError (RAISED, never silently clamped) if `bar` is above the family's ceiling or below
    k_min/n, or if the family is NOT GRADABLE at all (no bar may be declared for it, §3.4)."""
    if entry.get("not_gradable") or is_not_gradable(entry):
        raise BarsError(f"{family}: NOT GRADABLE (ORGAN LIMIT) — no bar may be declared")
    ceiling = entry["organ_ceiling"]["max"]  # type: ignore[index]
    k_min, n = entry["k_min"], entry["n"]
    floor = k_min / n
    if bar > ceiling:
        raise BarsError(f"{family}: declared bar {bar} is ABOVE its organ ceiling {ceiling}")
    if bar < floor:
        raise BarsError(f"{family}: declared bar {bar} is BELOW k_min/n={floor} "
                         f"(an arm at chance could clear it with P >= 0.001)")


def validate_bars_line(ceilings: Mapping[str, Mapping[str, object]], bars: Mapping[str, float]) -> Dict[str, object]:
    """Every declared bar is checked against the family's own ceilings.json entry. A bar for a family with
    no computed ceiling, or for a NOT GRADABLE family, is refused outright."""
    results: Dict[str, object] = {}
    for family, bar in bars.items():
        entry = ceilings.get(family)
        if entry is None:
            raise BarsError(f"no ceiling computed for family {family!r} — cannot declare its bar")
        validate_bar(family, entry, bar)
        k_min, n = entry["k_min"], entry["n"]
        results[family] = {"bar": bar, "ceiling": entry["organ_ceiling"]["max"], "k_min_over_n": k_min / n}
    return results


def ceilings_sha256(ceilings_path: Path) -> str:
    """The hash `results.json`'s own `ceilings_sha` field carries (§8) — of the FILE'S BYTES on disk, so a
    byte-for-byte identical re-read always reproduces it and a single-byte edit to ceilings.json is caught."""
    return hashlib.sha256(Path(ceilings_path).read_bytes()).hexdigest()


def assert_bars_not_moved_after_grading(bars_declared_at_iso: str, first_graded_answer_at_iso: Optional[str]) -> None:
    """#228: "Bars are never moved after any graded answer exists." Both timestamps are ISO-8601 UTC
    strings (comparable lexicographically); `first_graded_answer_at_iso=None` means no graded answer exists
    yet — always fine to (re)declare bars then."""
    if first_graded_answer_at_iso is None:
        return
    if bars_declared_at_iso > first_graded_answer_at_iso:
        raise BarsError(f"a bar was (re)declared at {bars_declared_at_iso}, AFTER the first graded answer "
                         f"at {first_graded_answer_at_iso} — #228 forbids moving bars once grading has begun")
