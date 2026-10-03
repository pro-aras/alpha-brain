"""prereg.py — the TOYS lane's signed-text pins: a run REFUSES if a signed law's text differs from the one that carries the architect's co-signature.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 11:33 +0400 — new module, red-first (tests/tools/test_toys_common.py). The pinned sha of a law is the sha256 of
# its file WITH its signature lines removed (a signature line begins `- Co-signed:`), i.e. the text the co-signer read; a later signature line never moves it.

  cp          docs/research/toys/PREREG-TOY-CP.md          text co-signed 2026-10-03 11:13 +0400 (commit 31f24d9)
  cp_amend1   docs/research/toys/PREREG-TOY-CP-AMEND-1.md  text co-signed 2026-10-03 11:28 +0400 (commit 0cf21c9)
  nullspace   docs/research/toys/PREREG-TOY-NULLSPACE.md   text co-signed 2026-10-03 11:24 +0400 (commit eefa8d2)
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[3]
DOCS = REPO / "docs" / "research" / "toys"
SIGNED: Dict[str, Tuple[str, str]] = {
    "cp": ("PREREG-TOY-CP.md", "726d032918b3a2114ce2d7802865ffd64d3458910106a3af88c21df0c4866900"),
    "cp_amend1": ("PREREG-TOY-CP-AMEND-1.md", "59181d22d873614674728450a8a3f3a2428784656066577eaae8b8bc8d273448"),
    "nullspace": ("PREREG-TOY-NULLSPACE.md", "d15a6353d6b62e7ba74c407e2a220054c127250c7b4ee07f55d4564bc40ac2ca"),
}
SIGNATURE_PREFIX = b"- Co-signed:"


class PreregError(Exception):
    pass


def signed_sha(path: Path) -> str:
    kept = b"\n".join(line for line in Path(path).read_bytes().split(b"\n") if not line.startswith(SIGNATURE_PREFIX))
    return hashlib.sha256(kept).hexdigest()


def check(keys: Sequence[str], root: Optional[Path] = None) -> Dict[str, str]:
    """Each named law's signed sha against its pin; raises PreregError on any difference (a run must not start)."""
    base = Path(root) if root is not None else DOCS
    got: Dict[str, str] = {}
    for k in keys:
        name, want = SIGNED[k]
        have = signed_sha(base / name)
        if have != want:
            raise PreregError(f"{name}: signed text sha256 {have[:12]}… ≠ the co-signed {want[:12]}… — STOP; an edit needs a new co-signature or an amendment")
        got[k] = have
    return got


def header(keys: Sequence[str]) -> Dict[str, str]:
    return {f"prereg_{k}_sha256": SIGNED[k][1] for k in keys}
