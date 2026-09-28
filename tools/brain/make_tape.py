#!/usr/bin/env /usr/bin/python3
# edit: Claude (Sonnet 5, BRAIN builder B), 2026-09-28 20:32 +0400 — BRAIN-IN-BODY §5 (docs/brain/body/INTERFACE-BRAIN-ORGAN.md);
# the seat's amendment (deterministic tape clock, so a made tape is a single day file `creature/replay.py` can read whole).
"""tools/brain/make_tape.py — a whole scene-world life's tape at machine speed, synchronously, for the replay road (the
twins, the nulls): the SAME `creature.senses.scene.plan()` the live sense thread runs, published into a
`creature.tape.Tape` with no threads and no waiting.

The seat's amendment: `creature/replay.py:run_replay` reads ONE tape day file, and the tape's day rolls at 00:00 UTC — a
made tape must land entirely inside one day file to be replayable whole. Every row here is published with an explicit,
DETERMINISTIC `at`: 2026-09-28T00:00:00.000Z plus 1 ms per row (module-order, the SAME order `plan()` gives), so two
`make_tape.py` runs of the same genome/cfg write byte-identical tape day files (test_make_tape.py's own pin).

`--limit-train N`: the DECLARED WORLD_SCENE `train` count overridden downward (never up — a genome's own `train` is the
ceiling), for a cheap smoke tape without editing a genome file.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from creature.senses import scene as S               # noqa: E402
from creature.tape import Tape                        # noqa: E402
from genome.machinery import parse_genome              # noqa: E402

FIXED_START = datetime(2026, 9, 28, 0, 0, 0, tzinfo=timezone.utc)


def deterministic_clock(start: datetime = FIXED_START) -> Callable[[], str]:
    """A zero-arg generator of ISO-8601 ms timestamps, `start` + 1 ms per call — never the wall clock, so a
    tape made twice from the same cfg is byte-identical (the seat's amendment)."""
    n = [0]

    def next_at() -> str:
        t = start + timedelta(milliseconds=n[0])
        n[0] += 1
        return t.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return next_at


def scene_cfg_of(genome_path: Path, limit_train: Optional[int] = None) -> Dict[str, object]:
    declared = parse_genome(genome_path.read_text()).declared
    if "WORLD_SCENE" not in declared:
        raise ValueError(f"make_tape: {genome_path} declares no WORLD_SCENE line")
    cfg = dict(declared["WORLD_SCENE"])
    if limit_train is not None:
        cfg = {**cfg, "train": min(int(cfg["train"]), int(limit_train))}
    return cfg, declared


def make(genome_path: Path, root: Path, limit_train: Optional[int] = None) -> Dict[str, object]:
    """Writes the whole tape + truth files under `root` (the genome's own TAPE path, `creature.tape.Tape`'s
    own resolution — `_resolve_tape_dir`, unchanged). Returns rows-per-sense and the truth-file count, for
    the CLI's own print (never judged by piping stdout — the caller reads this return, or the printed JSON)."""
    root = Path(root)
    cfg, declared = scene_cfg_of(genome_path, limit_train)
    tape = Tape(root, declared_path=declared.get("TAPE", {}).get("path"))
    clock = deterministic_clock()
    moments = S.plan(cfg)
    rows_per_sense: Dict[str, int] = {}
    truth_written = 0
    for m in moments:
        eye_row = None
        for row in m["rows"]:
            payload = row["payload"]()
            r = tape.publish(row["sense"], payload, row["meta"], row["ext"], at=clock())
            rows_per_sense[row["sense"]] = rows_per_sense.get(row["sense"], 0) + 1
            if row["sense"] == "eye":
                eye_row = r
        truth_fn = m["truth"]
        if truth_fn is not None:
            if eye_row is None:
                raise RuntimeError(f"make_tape: moment {m['moment']!r} carries truth but published no eye row")
            truth_obj = truth_fn()
            truth_dir = root / "truth" / "scene"
            truth_dir.mkdir(parents=True, exist_ok=True)
            (truth_dir / f"{int(eye_row['seq']):09d}.json").write_text(json.dumps(truth_obj, sort_keys=True))
            truth_written += 1
    return {"moments": len(moments), "rows_per_sense": rows_per_sense, "truth_files_written": truth_written}


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--genome", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--limit-train", type=int, default=None)
    args = ap.parse_args(argv)
    root = Path(args.root)
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"make_tape: {root} exists and is not empty — a tape root is written once")
    root.mkdir(parents=True, exist_ok=True)
    stats = make(Path(args.genome), root, args.limit_train)
    print(json.dumps(stats, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
