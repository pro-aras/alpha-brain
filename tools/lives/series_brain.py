# edit: Claude (Fable 5.1, the seat), 2026-09-29 20:14 +0400 — THE LONG LIFE: one SERIES line per call, from STATUS.json alone.
"""tools/lives/series_brain.py --root <life root> — appends ONE line to <root>/SERIES.tsv.

Run by creature-brain-series@<name>.timer every 5 min. It never closes, stops or restarts anything and never
reads the tape (a days-long tape is gigabytes; STATUS is the body's own reading). Every field is printed with
its PRESENCE: a key STATUS does not carry reads «absent», never 0 (#162, #168)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

FIELDS = ("moments", "tape_rows", "mind_backlog_rows", "cells", "births", "episodes", "thinks", "sleeps", "snapshots",
          "mind_ms_per_canvas_1min", "rss_mb", "sense_restarts", "crash", "said", "think_skipped_for_backlog", "births_refused_budget",
          "evolve_epoch", "stage")
SCENE = ("published_moments", "train_done", "sitting_done", "ended")
BRAIN = ("learned", "calibrations", "words", "mature", "episodes", "asks_answered", "asks_pending", "refused_rows")


def line(root: Path, unit_name: str) -> str:
    try:
        s = json.loads((root / "STATUS.json").read_text())
    except Exception as e:   # a torn or missing STATUS is a reading too
        s = {"_status_error": repr(e)}
    def get(d, k):
        return json.dumps(d[k], sort_keys=True) if isinstance(d, dict) and k in d else "absent"
    load = Path("/proc/loadavg").read_text().split()[0]
    show = subprocess.run(["systemctl", "--user", "show", unit_name, "-p", "ActiveState", "-p", "NRestarts", "-p", "MemoryCurrent"],
                          capture_output=True, text=True).stdout.strip().replace("\n", " ")
    sc, br = s.get("scene"), s.get("brain")
    cols = [time.strftime("%Y-%m-%d %H:%M:%S %z"), load, show, get(s, "heartbeat_at")]
    cols += [get(s, k) for k in FIELDS] + [get(sc, k) for k in SCENE] + [get(br, k) for k in BRAIN]
    cols.append(s.get("_status_error", ""))
    return "\t".join(str(c) for c in cols)


def header() -> str:
    return "\t".join(("at", "load", "unit", "heartbeat_at") + FIELDS + tuple("scene." + k for k in SCENE)
                     + tuple("brain." + k for k in BRAIN) + ("status_error",))


def main(argv) -> int:
    root = Path(argv[argv.index("--root") + 1])
    out = root / "SERIES.tsv"
    if not out.exists():
        out.write_text(header() + "\n")
    with out.open("a") as fh:
        fh.write(line(root, f"creature-brain@{root.name}.service") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
