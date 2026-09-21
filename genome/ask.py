"""ask.py — the small door of G0 §8 / G1 §5 step 7: ask the grown organism, from the shell.

    python3 -m genome.ask what-is <picture>            → the word, or «I do not know» with the reason
    python3 -m genome.ask show <word>                  → the thing its strongest edge leads to (by the ledger)
    python3 -m genome.ask is <picture> <word>          → yes / no (the Q3 rule)
    python3 -m genome.ask which <a> <b> <word>         → a or b (the Q4 rule: the larger summed edge)
    (optional first argument --run <dir>: a run directory; default = the newest runs/g1-his-*, else the newest runs/g1-toy-*)

edit: Claude (Fable 5.1), 2026-09-19 17:28 +0400 — G1. Reads organism.npz/.json + ledger.json + the genome file saved by run_g1;
never changes the organism; appends one line per question to world/ASK.log (his record).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from . import gaze, world
from .machinery import Organism, parse_genome

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "world" / "ASK.log"


def newest_run() -> Path:
    for pat in ("g1-his-*", "g1-toy-*"):
        c = sorted((ROOT / "runs").glob(pat))
        c = [p for p in c if (p / "organism.npz").exists()]
        if c:
            return c[-1]
    raise SystemExit("no run with a saved organism under runs/ (run python3 -m genome.run_g1 --toy or --his first)")


def load(run: Path):
    import json
    gfile = next(p for p in run.iterdir() if p.suffix == ".genome")
    g = parse_genome(gfile.read_text())
    org = Organism.load(run / "organism", g)
    L = json.loads((run / "ledger.json").read_text())
    Ls = {int(k): set(v) for k, v in L["sight"].items()}; Lw = {int(k): set(v) for k, v in L["words"].items()}
    return g, org, Ls, Lw


# edit: Claude (Sonnet 5, G5 builder J), 2026-09-21 22:38 +0400 — added `colour=g.colour` (the orchestrator's
# addendum: this is a LIVE consumer — `python3 -m genome.ask what-is <picture>` against a saved run whose
# genome declares SENSE colour would recall_many() a 112-dim vector against a 144-dim organism and crash
# inside Area.cos with a shape mismatch, same class of bug as glance_held/glance_rows above).
def glance_picture(path: Path, g) -> List[np.ndarray]:
    p = Path(path)
    rgb = gaze.canvas_of_picture(p, int(g.gaze["canvas"]))
    return gaze.glances(rgb, g.retina, g.gaze, "surprise", p.name, colour=g.colour)["feats"]


def word_cells(org, Lw, word: str) -> List[int]:
    return [c for c, s in Lw.items() if s == {word} and org.words.alive[c]]


def main(argv: List[str]) -> int:
    run = Path(argv[argv.index("--run") + 1]) if "--run" in argv else newest_run()
    argv = [a for i, a in enumerate(argv) if a != "--run" and not (i > 0 and argv[i - 1] == "--run")]
    if not argv:
        print(__doc__); return 1
    g, org, Ls, Lw = load(run)
    cmd, args = argv[0], argv[1:]
    if cmd == "what-is":
        r = org.recall_many("sight", glance_picture(args[0], g))
        ans = "/".join(sorted(Lw.get(r["cell"], set()))) if r["cell"] is not None else None
        line = f"what-is {args[0]} → {ans if ans else 'I do not know this'} ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f} cos {r['cos']:.3f})"
    elif cmd == "show":
        r = org.recall_many("words", [world.encode_word(args[0], g.ear_blank_zero)])
        ans = "/".join(sorted(Ls.get(r["cell"], set()))) if r["cell"] is not None else None
        line = f"show {args[0]} → {('a picture of ' + ans) if ans else 'I do not know this word'} ({r['reason']}; best {r['best']:.3f} second {r['second']:.3f})"
    elif cmd == "is":
        r = org.recall_many("sight", glance_picture(args[0], g))
        yes = r["cell"] is not None and Lw.get(r["cell"], set()) == {args[1]}
        line = f"is {args[0]} {args[1]} → {'yes' if yes else 'no'} ({r['reason']}; it reads {'/'.join(sorted(Lw.get(r['cell'], set()))) if r['cell'] is not None else 'nothing'})"
    elif cmd == "which":
        wc = word_cells(org, Lw, args[2])
        ea = max([org.edge_many("sight", glance_picture(args[0], g), c) for c in wc], default=0.0)
        eb = max([org.edge_many("sight", glance_picture(args[1], g), c) for c in wc], default=0.0)
        pick = args[0] if ea > eb else (args[1] if eb > ea else "neither (tie)")
        line = f"which {args[0]} {args[1]} {args[2]} → {pick} (edges {ea:.3f} vs {eb:.3f}; word cells {len(wc)})"
    else:
        print(__doc__); return 1
    stamp = time.strftime("%Y-%m-%d %H:%M:%S %z")
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"{stamp} [{run.name}] {line}\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
