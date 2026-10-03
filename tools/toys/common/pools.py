"""pools.py — the TOYS lane's room pools: S1c's law world (R1, R2, R3, N) redrawn under THIS tree's code, one seed per call.

# edit: Claude (Sonnet 5.5, swarm toys), 2026-10-03 10:49 +0400 — new module. INFRASTRUCTURE ONLY: a thin wrapper over
# brain.scene.rooms.build_room_cache (no picker, no learner, no mark, no experiment logic). Written before the toys' PREREGs are
# signed because the ceilings in them (the input spectrum of the rooms) are read from these pools; the PREREGs say so.

A cache is read only by its own code (cache.check_code), and this tree's WORLD_CODE differs from the one S1c's caches were drawn
under, so S1c's pools are REFUSED here. Every pool is therefore redrawn into this lane's own root (scratch/toys-pools, gitignored)
and, for S1c's three seeds, compared AS FILES with S1c's own (canvas shas, scene specs, the glances' npy sha) — T-MEM-1's
`pools_identical` rule (brain/scene/run_tmem1.py). A pool that is not identical stops the lane: the toys' identity gates
(S1c's own records reproduced) would be void.

  PYTHONPATH=. python3 -m tools.toys.common.pools --seed 20261301          one seed (4 rooms x visit + window = 8,160 canvases)
  PYTHONPATH=. python3 -m tools.toys.common.pools --seed 20261301 --check   only the identity / presence check (no drawing)

Seeds: S1c's three (20261301-03, identity-checked) and seven new ones (20261304-10, no reference to compare with; their
generator is the same substream function of (seed, room, kind, i), so only the self-check of the builder applies).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Sequence

from brain.scene import cache as C
from brain.scene import rooms as RM
from brain.scene import run_s1c as S

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "scratch" / "toys-pools"
S1C_ROOT = S.ROOT                                  # /data/dev/brain-runs/scene-s1c — read as plain files only
LAW_ROOMS: Sequence[str] = tuple(S.WORLDS["law"])  # R1, R2, R3, N
ALL_SEEDS = tuple(range(20261301, 20261311))       # ten world seeds
HEADER = {"lane": "toys", "purpose": "pools for PREREG-TOY-CP and PREREG-TOY-NULLSPACE", "no_experiment_logic": "true"}


def pool_dirs(root: Path, seed: int):
    return [(room, kind, RM.room_cache_dir(root, seed, room, kind)) for room in LAW_ROOMS for kind in RM.KINDS]


def present(root: Path, seed: int) -> Dict[str, bool]:
    return {f"{room}-{kind}": d.exists() and (d / "scene_header.json").exists() for room, kind, d in pool_dirs(root, seed)}


def identity(root: Path, seed: int) -> Optional[Dict[str, object]]:
    """The seed's redrawn pools against S1c's own, as files. None for a seed S1c never drew."""
    if seed not in RM.S1C_SEEDS:
        return None
    res = {f"{room}-{kind}": C.identity_with(d, RM.room_cache_dir(S1C_ROOT, seed, room, kind)) for room, kind, d in pool_dirs(root, seed)}
    return {"pools": res, "same": all(v["same"] for v in res.values()), "n_pools": len(res)}


def build(root: Path, seed: int, log=print) -> Dict[str, object]:
    """Draw the seed's eight law pools (each written once; an existing cache is kept), then compare with S1c's."""
    t0, cpu0 = time.time(), time.process_time()
    drawn = []
    for room, kind, d in pool_dirs(root, seed):
        if d.exists():
            continue
        t1 = time.time()
        RM.build_room_cache(root, seed, room, kind, prereg=HEADER, log=log)
        drawn.append({"pool": f"{room}-{kind}", "wall_s": round(time.time() - t1, 1)})
    out = {"seed": seed, "root": str(root), "drawn": drawn, "present": present(root, seed), "identity": identity(root, seed),
           "wall_s": round(time.time() - t0, 1), "cpu_s": round(time.process_time() - cpu0, 1)}
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--check", action="store_true", help="no drawing: report presence and identity only")
    a = ap.parse_args(argv)
    if a.seed not in ALL_SEEDS:
        print(f"seed {a.seed} is not one of the ten declared seeds {ALL_SEEDS[0]}-{ALL_SEEDS[-1]}", file=sys.stderr)
        return 2
    if a.check:
        out = {"seed": a.seed, "present": present(a.root, a.seed), "identity": identity(a.root, a.seed) if all(present(a.root, a.seed).values()) else None}
    else:
        out = build(a.root, a.seed, log=lambda s: print(s, flush=True))
    a.root.mkdir(parents=True, exist_ok=True)
    (a.root / f"build-{a.seed}.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("seed", "present", "wall_s", "cpu_s") if k in out}, sort_keys=True))
    ident = out.get("identity")
    if ident is not None:
        print(f"identity with S1c's pools: {'EQUAL' if ident['same'] else 'DIFFERENT'} ({ident['n_pools']} pools)")
        if not ident["same"]:
            return 3
    if not all(out["present"].values()):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
